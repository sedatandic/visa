import logging
import os
import re
import secrets
import string
import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile

from content import (
    AGENCY_INFO,
    ARTICLES,
    BANK_TRANSFER,
    COMPANY,
    FAMILY_DISCOUNT_TEXT,
    FAMILY_DISCOUNT_TIERS,
    FAQ,
    IMPORTANT_NOTICE,
    MAX_TRAVELERS,
    PARTNERS,
    PHOTO_RULES,
    PROCESS_STEPS,
    PROMO,
    REFUND_TERMS,
    REQUIRED_DOCUMENTS,
    REVIEW_SUMMARY,
    SERVICE_TERMS,
    SERVICES,
    STATUS_LABELS,
    TESTIMONIALS,
    TOURS,
    VISA_CATEGORIES,
    VISA_TYPES,
    WHY_US,
    compute_pricing,
)
from db import (
    applications_col,
    articles_col,
    contact_col,
    serialize_doc,
    settings_col,
    testimonials_col,
    uploads_col,
    visa_types_col,
    drafts_col,
)
from emailer import (
    admin_notify_html,
    applicant_received_html,
    contact_admin_html,
    documents_completed_admin_html,
    send_email,
)
from models import ApplicationCreate, ContactCreate, DocumentSubmission, QuoteRequest
from doc_reminders import missing_documents
from fx import addon_prices_try, addons_with_fx, apply_fx_to_list, apply_fx_to_visa, get_fx
from passport_ai import check_photo, read_passport
from storage import APP_NAME, MIME_TYPES, get_object, put_object
from visa_guides import build_guide, guide_index

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_FILE_BYTES = 10 * 1024 * 1024
ALLOWED_EXT = {"jpg", "jpeg", "png", "webp", "pdf"}


def generate_reference_code() -> str:
    alphabet = "ABCDEFGHJKLMNPRSTUVYZ"
    letters = "".join(secrets.choice(alphabet) for _ in range(2))
    digits = "".join(secrets.choice(string.digits) for _ in range(6))
    return f"DV-{letters}{digits}"


STEP_DEFS = [
    ("received", "Başvurunuz alındı", "Bilgileriniz ve belgeleriniz sistemimize kaydedildi."),
    ("payment", "Ödeme onaylandı", "Ödemeniz alındıktan sonra işleme başlıyoruz."),
    ("documents", "Belgeler tamamlandı", "Pasaport, fotoğraf, uçak bileti ve otel rezervasyonu kontrol edildi."),
    ("processing", "Göçmenlik idaresine iletildi", "Başvurunuz GDRFA/acente portalı üzerinden işleme alındı."),
    ("result", "Vize sonucu", "Sonuç açıklandığında vizeniz e-postanıza gönderilir."),
]


def _iso_or_none(value):
    """Datetime/date degerini ISO string'e cevirir; digerlerini oldugu gibi dondurur."""
    return value.isoformat() if hasattr(value, "isoformat") else value


def _first_status_dates(doc: dict) -> dict:
    """status_history icindeki her durum icin ilk gerceklesme zamanini dondurur."""
    history: dict = {}
    for entry in doc.get("status_history") or []:
        status = entry.get("status")
        if status and status not in history:
            history[status] = entry.get("at")
    return history


def _timeline_progress_index(doc: dict, missing: list | None) -> int:
    """Tamamlanan son adimin indeksi (0=alindi, 1=odeme, 2=belgeler, 3=islemde, 4=sonuc)."""
    status = doc.get("status") or "submitted"
    payment = doc.get("payment") or {}
    paid = payment.get("status") == "paid"
    docs_ok = not (missing or [])
    in_process = status in {"reviewing", "approved", "rejected"} or bool(doc.get("zami_transferred_at"))
    final = status in {"approved", "rejected", "cancelled"}

    done_upto = 0
    if paid:
        done_upto = 1
    if paid and docs_ok:
        done_upto = 2
    if in_process:
        done_upto = max(done_upto, 3)
    if final:
        done_upto = 4
    return done_upto


def _timeline_step_dates(doc: dict) -> dict:
    """Her adim icin gosterilecek tarihleri toplar."""
    history = _first_status_dates(doc)
    payment = doc.get("payment") or {}
    return {
        "received": doc.get("created_at"),
        "payment": payment.get("paid_at"),
        "documents": None,
        "processing": history.get("reviewing"),
        "result": history.get("approved") or history.get("rejected") or history.get("cancelled"),
    }


def _timeline_step_state(idx: int, done_upto: int) -> str:
    if idx <= done_upto:
        return "done"
    if idx == done_upto + 1:
        return "current"
    return "pending"


def build_customer_timeline(doc: dict, missing: list | None = None) -> dict:
    """Musteriye gosterilecek adim adim durum akisini uretir."""
    status = doc.get("status") or "submitted"
    final = status in {"approved", "rejected", "cancelled"}
    done_upto = _timeline_progress_index(doc, missing)
    step_dates = _timeline_step_dates(doc)

    steps = [
        {
            "key": key,
            "title": title,
            "description": description,
            "state": _timeline_step_state(idx, done_upto),
            "at": _iso_or_none(step_dates.get(key)),
            "result": status if key == "result" and final else None,
        }
        for idx, (key, title, description) in enumerate(STEP_DEFS)
    ]

    return {
        "steps": steps,
        "current_status": status,
        "is_final": final,
        "last_portal_check": _iso_or_none(doc.get("zami_status_checked_at")),
        "portal_tracked": bool(doc.get("zami_transferred_at") or doc.get("zami_reference")),
    }


def public_application_view(doc: dict) -> dict:
    d = serialize_doc(doc)
    if not d:
        return d
    d.pop("admin_notes", None)
    # portal ic bilgileri musteriye gosterilmez
    for key in ("zami_status_raw", "zami_reference", "linked_order_id"):
        d.pop(key, None)
    return d


async def get_visa_type(visa_type_id: str):
    visa = await visa_types_col.find_one({"id": visa_type_id})
    if not visa:
        visa = next((v for v in VISA_TYPES if v["id"] == visa_type_id), None)
    if not visa:
        return None
    return await apply_fx_to_visa(serialize_doc(visa))


# ---------------------------------------------------------------- content
@router.get("/visa-types")
async def get_visa_types():
    docs = await visa_types_col.find({"active": True}).sort("order", 1).to_list(100)
    items = serialize_doc(docs) if docs else VISA_TYPES
    return await apply_fx_to_list(items)


@router.get("/visa-guides")
async def list_visa_guides() -> dict:
    """Vize rehberi (SEO) sayfalarinin listesi. Fiyatlar DB'den guncellenir."""
    docs = await visa_types_col.find({"active": True}).to_list(100)
    by_slug = {d.get("slug"): d for d in docs}
    fx = await get_fx()
    items = []
    for item in guide_index():
        doc = by_slug.get(item["slug"])
        if docs and not doc:
            continue  # admin tarafindan pasife alinmis
        if doc:
            item = {
                **item,
                "name": doc.get("name", item["name"]),
                "price": doc.get("price", item["price"]),
                "price_usd": doc.get("price_usd", item.get("price_usd")),
                "currency": doc.get("currency", item["currency"]),
                "processing_days": doc.get("processing_days", item["processing_days"]),
                "summary": doc.get("description", item["summary"]),
            }
        items.append(await apply_fx_to_visa(item, fx["effective_rate"]))
    return {"items": items, "fx": fx}


@router.get("/visa-guides/{slug}")
async def get_visa_guide(slug: str):
    doc = await visa_types_col.find_one({"slug": slug})
    if doc is not None:
        active_flag = doc.get("active", True)
        # Yalnizca acik sekilde pasife alinmis (falsy ama None olmayan) kayitlari gizle.
        if active_flag is not None and not active_flag:
            raise HTTPException(404, "Vize rehberi bulunamadi.")
    visa_override = serialize_doc(doc) if doc else None
    guide_override = (visa_override or {}).pop("guide", None) if visa_override else None
    guide = build_guide(slug, visa_override=visa_override, guide_override=guide_override)
    if not guide:
        raise HTTPException(404, "Vize rehberi bulunamadi.")
    fx = await get_fx()
    guide["visa"] = await apply_fx_to_visa(guide["visa"], fx["effective_rate"])
    guide["related"] = [await apply_fx_to_visa(r, fx["effective_rate"]) for r in guide["related"]]
    guide["fx"] = fx
    return guide


@router.get("/fx")
async def public_fx() -> dict:
    """Musteriye gosterilen guncel USD/TRY kuru (seffaflik icin)."""
    fx = await get_fx()
    return {
        "effective_rate": fx["effective_rate"],
        "currency_pair": fx["currency_pair"],
        "fetched_at": fx["fetched_at"],
        "source": fx["source"] if fx["mode"] == "live" else "sabit kur",
    }


@router.get("/content/site")
async def get_site_content() -> dict:
    testimonials = await testimonials_col.find({"published": True}).sort("order", 1).to_list(50)
    summary_doc = await settings_col.find_one({"key": "review_summary"})
    article_docs = (
        await articles_col.find({"published": True}).sort("date", -1).limit(20).to_list(20)
    )
    company_doc = await settings_col.find_one({"key": "company_info"})
    company = {**COMPANY, **((company_doc or {}).get("value") or {})}
    agency_info = {
        **AGENCY_INFO,
        "items": [
            {"label": "Ticaret Unvanı", "value": company.get("legal_name", "")},
            {"label": "TÜRSAB Belge No", "value": company.get("tursab_no", "")},
            {"label": "Acente Türü", "value": company.get("tursab_type", "")},
            {
                "label": "Vergi Dairesi / No",
                "value": f"{company.get('tax_office', '')} / {company.get('tax_no', '')}".strip(" /"),
            },
            {"label": "MERSİS No", "value": company.get("mersis_no", "")},
            {"label": "Ticaret Sicil No", "value": company.get("trade_registry_no", "")},
            {"label": "Adres", "value": company.get("address", "")},
            {"label": "Kuruluş", "value": company.get("founded_year", "")},
        ],
    }
    agency_info["items"] = [i for i in agency_info["items"] if i["value"]]
    return {
        "company": company,
        "visa_categories": VISA_CATEGORIES,
        "addons": await addons_with_fx(),
        "fx": await get_fx(),
        "family_discount_tiers": [{"min": m, "rate": r} for m, r in FAMILY_DISCOUNT_TIERS],
        "family_discount_text": FAMILY_DISCOUNT_TEXT,
        "max_travelers": MAX_TRAVELERS,
        "process_steps": PROCESS_STEPS,
        "why_us": WHY_US,
        "services": SERVICES,
        "tours": TOURS,
        "partners": PARTNERS,
        "faq": FAQ,
        "required_documents": REQUIRED_DOCUMENTS,
        "photo_rules": PHOTO_RULES,
        "testimonials": serialize_doc(testimonials) or TESTIMONIALS,
        "review_summary": (summary_doc or {}).get("value") or REVIEW_SUMMARY,
        "articles": serialize_doc(article_docs) or ARTICLES,
        "important_notice": IMPORTANT_NOTICE,
        "status_labels": STATUS_LABELS,
        "promo": PROMO,
        "agency_info": agency_info,
        "bank_transfer": ((await settings_col.find_one({"key": "bank_transfer"})) or {}).get("value")
        or BANK_TRANSFER,
    }


@router.get("/content/legal")
async def get_legal_content() -> dict:
    return {"refund_terms": REFUND_TERMS, "service_terms": SERVICE_TERMS}


@router.get("/articles")
async def list_articles(limit: int = 50):
    docs = await articles_col.find({"published": True}).sort("date", -1).limit(limit).to_list(limit)
    if not docs:
        return ARTICLES
    return serialize_doc(docs)


@router.get("/articles/{slug}")
async def get_article(slug: str) -> dict:
    doc = await articles_col.find_one({"slug": slug, "published": True})
    if not doc:
        fallback = next((a for a in ARTICLES if a["slug"] == slug), None)
        if not fallback:
            raise HTTPException(404, "Yazi bulunamadi.")
        doc = fallback
    article = serialize_doc(doc)
    related = (
        await articles_col.find({"published": True, "slug": {"$ne": slug}})
        .sort("date", -1)
        .limit(3)
        .to_list(3)
    )
    return {"article": article, "related": serialize_doc(related)}


def _parse_iso_date(value: str | None):
    try:
        return date.fromisoformat((value or "").strip()[:10])
    except Exception:
        return None


def trip_day_count(arrival: str | None, departure: str | None) -> int | None:
    """Seyahat suresi (gun). Giris ve donus gunleri dahil."""
    start = _parse_iso_date(arrival)
    end = _parse_iso_date(departure)
    if not start or not end or end < start:
        return None
    return (end - start).days + 1


def _store_line_validity(start: date | None, validity_days: int, trip_days: int | None) -> dict:
    """Ek urunun gecerlilik penceresini ve seyahati kapsayip kapsamadigini hesaplar."""
    starts_on = start.isoformat() if start else None
    ends_on = None
    if start and validity_days > 0:
        ends_on = (start + timedelta(days=validity_days - 1)).isoformat()
    covers_trip = None
    if trip_days and validity_days:
        covers_trip = trip_days <= validity_days
    return {
        "validity_days": validity_days,
        "starts_on": starts_on,
        "ends_on": ends_on,
        "trip_days": trip_days,
        "covers_trip": covers_trip,
    }


def _store_line(product: dict, quantity: int, validity: dict) -> dict:
    unit_price = float(product["price"])
    return {
        "product_id": product["id"],
        "kind": product.get("kind", ""),
        "kind_label": product.get("kind_label", ""),
        "name": product["name"],
        "quantity": quantity,
        "unit_price": unit_price,
        "unit_price_usd": float(product.get("price_usd") or 0),
        "total": round(unit_price * quantity, 2),
        **validity,
    }


async def resolve_store_lines(items, arrival_date: str | None = None, departure_date: str | None = None) -> list:
    """Basvuru icinde secilen eSIM / sigorta urunlerini magaza katalogundan fiyatlar.

    Urunlerin gecerlilik tarihleri seyahatin giris tarihinden baslatilir.
    """
    if not items:
        return []
    from routes_store import MAX_QTY, product_list

    catalog = {p["id"]: p for p in await product_list()}
    start = _parse_iso_date(arrival_date)
    trip_days = trip_day_count(arrival_date, departure_date)

    lines = []
    for item in items:
        product = catalog.get(item.product_id)
        if not product:
            raise HTTPException(400, "Secilen ek urun bulunamadi veya satista degil.")
        quantity = max(1, min(int(item.quantity), MAX_QTY))
        validity = _store_line_validity(start, int(product.get("validity_days") or 0), trip_days)
        lines.append(_store_line(product, quantity, validity))
    return lines


@router.post("/pricing/quote")
async def pricing_quote(payload: QuoteRequest):
    prices = []
    for vid in payload.visa_type_ids:
        visa = await get_visa_type(vid)
        if not visa:
            raise HTTPException(400, f"Gecersiz vize tipi: {vid}")
        prices.append(float(visa["price"]))
    quote = compute_pricing(
        prices,
        payload.addons.model_dump(),
        addon_prices=await addon_prices_try(),
        store_lines=await resolve_store_lines(
            payload.store_items, payload.arrival_date, payload.departure_date
        ),
    )
    quote["trip_days"] = trip_day_count(payload.arrival_date, payload.departure_date)
    quote["fx"] = await get_fx()
    return quote


# ---------------------------------------------------------------- uploads
def _validate_upload(filename: str, data: bytes) -> str:
    """Uzanti ve boyut dogrulamasi yapar; gecerli uzantiyi dondurur."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, "Sadece JPG, PNG, WEBP veya PDF dosyalari yuklenebilir.")
    if len(data) == 0:
        raise HTTPException(400, "Dosya bos gorunuyor. Lutfen tekrar deneyin.")
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(400, "Dosya boyutu en fazla 10 MB olabilir.")
    return ext


def _store_upload(path: str, data: bytes, content_type: str) -> dict:
    """Dosyayi object storage'a yazar; hatalari kullanici dostu mesaja cevirir."""
    result: dict = {}
    try:
        result = put_object(path, data, content_type) or {}
    except Exception as exc:
        logger.error("upload failed: %s", exc)
        raise HTTPException(
            502, "Dosya yuklenemedi. Lutfen birkac saniye sonra tekrar deneyin."
        ) from exc
    if not (result or {}).get("path"):
        raise HTTPException(502, "Dosya yuklenemedi. Lutfen tekrar deneyin.")
    return result

@router.post("/uploads")
async def upload_document(file: UploadFile = File(...), doc_type: str = Form("passport")) -> dict:
    filename = file.filename or "dosya"
    data = await file.read()
    ext = _validate_upload(filename, data)

    file_id = str(uuid.uuid4())
    content_type = MIME_TYPES.get(ext, file.content_type or "application/octet-stream")
    safe_type = "".join(c for c in doc_type if c.isalnum() or c in "-_") or "other"
    path = f"{APP_NAME}/uploads/{safe_type}/{file_id}.{ext}"
    result = _store_upload(path, data, content_type)

    record = {
        "id": file_id,
        "doc_type": safe_type,
        "storage_path": result["path"],
        "original_filename": filename,
        "content_type": content_type,
        "size": result.get("size", len(data)),
        "is_deleted": False,
        "created_at": datetime.now(timezone.utc),
    }
    await uploads_col.insert_one(dict(record))
    return {
        "file_id": file_id,
        "doc_type": safe_type,
        "original_filename": filename,
        "content_type": content_type,
        "size": record["size"],
        "url": f"/api/files/{file_id}",
    }


@router.post("/photo/check")
async def check_photo_document(file_id: str = Form(...)) -> dict:
    """Yuklenen vesikalik fotografi yapay zeka ile denetler (uyari amacli, engellemez)."""
    record = await uploads_col.find_one({"id": file_id, "is_deleted": False})
    if not record:
        raise HTTPException(404, "Dosya bulunamadi.")
    content_type = record.get("content_type") or ""
    if content_type == "application/pdf":
        return {
            "ok": False,
            "checked": False,
            "reason": "pdf",
            "message": "Vesikalik fotografi PDF yerine JPG veya PNG olarak yukleyin.",
        }
    try:
        data, ct = get_object(record["storage_path"])
    except Exception as exc:
        logger.error("photo fetch failed: %s", exc)
        raise HTTPException(502, "Dosya okunamadi.") from exc

    result: dict = {}
    message: str = ""
    try:
        result = await check_photo(data, content_type or ct)
    except Exception as exc:
        logger.error("photo ai failed: %s", exc)
        return {
            "ok": True,
            "checked": False,
            "reason": "ai_error",
            "message": "Fotograf otomatik kontrol edilemedi; basvurunuza devam edebilirsiniz.",
        }

    await uploads_col.update_one(
        {"id": file_id},
        {
            "$set": {
                "photo_check": {
                    "at": datetime.now(timezone.utc),
                    "ok": result.get("ok"),
                    "score": result.get("score"),
                    "failed": result.get("failed"),
                }
            }
        },
    )
    if not result.get("is_photo"):
        message = "Bu goruntu vesikalik fotograf gibi gorunmuyor. Lutfen yuzunuzun net gorundugu bir portre yukleyin."
    elif result.get("ok"):
        message = "Fotograf vize standartlarina uygun gorunuyor."
    else:
        message = "Fotografta duzeltilmesi onerilen noktalar var."
    return {"checked": True, "message": message, **result}


@router.post("/passport/read")
async def read_passport_document(file_id: str = Form(...)) -> dict:
    """Yuklenen pasaport goruntusunu yapay zeka ile okuyup form alanlarini doldurur."""
    record = await uploads_col.find_one({"id": file_id, "is_deleted": False})
    if not record:
        raise HTTPException(404, "Dosya bulunamadi.")
    content_type = record.get("content_type") or ""
    if content_type == "application/pdf":
        return {
            "ok": False,
            "reason": "pdf",
            "message": "PDF dosyalari otomatik okunamiyor. Lutfen bilgileri elle girin.",
        }
    data: bytes = b""
    ct = ""
    try:
        data, ct = get_object(record["storage_path"])
    except Exception as exc:
        logger.error("passport fetch failed: %s", exc)
        raise HTTPException(502, "Dosya okunamadi.") from exc

    result: dict = {}
    try:
        result = await read_passport(data, content_type or ct)
    except Exception as exc:
        logger.error("passport ai failed: %s", exc)
        return {
            "ok": False,
            "reason": "ai_error",
            "message": "Pasaport otomatik okunamadi. Bilgileri elle girebilirsiniz.",
        }

    if not result.get("is_passport") or not (result.get("passport_no") or result.get("last_name")):
        return {
            "ok": False,
            "reason": "not_readable",
            "message": "Goruntuden bilgiler okunamadi. Daha net bir fotograf yukleyin veya elle girin.",
            "data": result,
        }

    await uploads_col.update_one(
        {"id": file_id},
        {"$set": {"ocr": {"at": datetime.now(timezone.utc), "confidence": result.get("confidence")}}},
    )
    return {"ok": True, "data": result}


@router.get("/files/{file_id}")
async def get_file(file_id: str, download: int = 0):
    record = await uploads_col.find_one({"id": file_id, "is_deleted": False})
    if not record:
        raise HTTPException(404, "Dosya bulunamadi.")
    data: bytes = b""
    content_type = ""
    try:
        data, content_type = get_object(record["storage_path"])
    except Exception as exc:
        logger.error("file fetch failed: %s", exc)
        raise HTTPException(502, "Dosya okunamadi.") from exc
    headers = {"Cache-Control": "private, max-age=300"}
    if download:
        name = record.get("original_filename") or f"{file_id}"
        headers["Content-Disposition"] = f'attachment; filename="{name}"'
    return Response(
        content=data,
        media_type=record.get("content_type") or content_type,
        headers=headers,
    )


# ----------------------------------------------------------- applications
async def _ensure_uploads_exist(*file_ids: str | None) -> None:
    """Verilen upload id'lerinin gercekten var oldugunu dogrular."""
    for fid in file_ids:
        if not fid:
            continue
        exists = await uploads_col.find_one({"id": fid, "is_deleted": False})
        if not exists:
            raise HTTPException(400, "Yuklenen belgeler bulunamadi. Lutfen belgeleri tekrar yukleyin.")


async def _validate_extra_documents(extra) -> None:
    """Basvuru geneli belgeleri dogrular.

    Ucak bileti ve otel rezervasyonu OPSIYONELDIR (musteri henuz rezervasyon
    yapmamis olabilir); gonderildiyse gecerli bir upload olmalidir.
    """
    await _ensure_uploads_exist(extra.ticket_file_id, extra.hotel_file_id)


async def _build_travelers(traveler_inputs) -> tuple[list, list]:
    """Yolcu girdilerini vize bilgileri ile zenginlestirir; (travelers, prices) dondurur."""
    travelers: list = []
    prices: list = []
    for t in traveler_inputs:
        visa = await get_visa_type(t.visa_type_id)
        if not visa:
            raise HTTPException(400, "Gecersiz vize tipi secildi.")
        await _ensure_uploads_exist(t.passport_file_id, t.photo_file_id)
        data = t.model_dump()
        data.update(
            {
                "id": str(uuid.uuid4()),
                "visa_type_name": visa["name"],
                "visa_short_name": visa.get("short_name", visa["name"]),
                "processing_days": visa.get("processing_days", ""),
                "price": float(visa["price"]),
                "currency": visa.get("currency", "TRY"),
                "documents": {
                    "passport_file_id": t.passport_file_id,
                    "photo_file_id": t.photo_file_id,
                },
            }
        )
        travelers.append(data)
        prices.append(float(visa["price"]))
    return travelers, prices


async def _unique_reference_code() -> str:
    reference_code = generate_reference_code()
    while await applications_col.find_one({"reference_code": reference_code}):
        reference_code = generate_reference_code()
    return reference_code


def _visa_summary_name(travelers: list) -> str:
    if len(travelers) == 1:
        return travelers[0]["visa_type_name"]
    return f"{travelers[0]['visa_short_name']} + {len(travelers) - 1} yolcu"


def _build_application_doc(
    payload: ApplicationCreate,
    travelers: list,
    store_lines: list,
    pricing: dict,
    reference_code: str,
    now: datetime,
) -> dict:
    """Kaydedilecek basvuru dokumanini olusturur."""
    return {
        "id": str(uuid.uuid4()),
        "reference_code": reference_code,
        "status": "submitted",
        "contact": payload.contact.model_dump(),
        "whatsapp_optin": bool(payload.contact.whatsapp_optin),
        "travelers": travelers,
        "travel": payload.travel.model_dump(),
        "addons": payload.addons.model_dump(),
        "store_items": store_lines,
        "store_total": pricing.get("store_total", 0.0),
        "linked_order_id": None,
        "linked_order_reference": None,
        "extra_documents": payload.extra_documents.model_dump(),
        "pricing": pricing,
        "price": pricing["total"],
        "currency": pricing["currency"],
        "processing_days": "24 saat" if payload.addons.express else travelers[0].get("processing_days", ""),
        "visa_type_name": _visa_summary_name(travelers),
        "payment": {
            "status": "pending",
            "session_id": None,
            "amount": pricing["total"],
            "currency": pricing["currency"],
            "paid_at": None,
        },
        "visa_result": None,
        "kvkk_accepted": bool(payload.kvkk_accepted),
        "admin_notes": "",
        "status_history": [{"status": "submitted", "at": now, "note": "Basvuru olusturuldu"}],
        "created_at": now,
        "updated_at": now,
    }


async def _link_store_order(doc: dict, store_lines: list) -> None:
    """Basvuru icinde alinan eSIM/sigorta urunleri icin teslimat siparisi olusturur."""
    if not store_lines:
        return
    try:
        from routes_store import create_application_order

        linked = await create_application_order(doc, store_lines)
        doc["linked_order_id"] = linked["id"]
        doc["linked_order_reference"] = linked["reference_code"]
        await applications_col.update_one(
            {"id": doc["id"]},
            {
                "$set": {
                    "linked_order_id": linked["id"],
                    "linked_order_reference": linked["reference_code"],
                }
            },
        )
    except Exception as exc:  # pragma: no cover
        logger.error("linked store order creation failed: %s", exc)


async def _after_application_created(doc: dict, travelers: list) -> None:
    """Aile profili guncelleme ve taslak temizligi gibi yan islemler."""
    try:
        from routes_account import upsert_saved_travelers

        await upsert_saved_travelers(doc["contact"]["email"], travelers)
    except Exception as exc:  # pragma: no cover
        logger.warning("saved travelers upsert failed: %s", exc)

    try:
        await drafts_col.delete_many(
            {"email": {"$regex": f"^{re.escape(doc['contact']['email'])}$", "$options": "i"}}
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("draft cleanup failed: %s", exc)


async def _send_application_emails(doc: dict, traveler_count: int) -> dict:
    """Basvuru sahibine ve admine bilgilendirme e-postalari gonderir."""
    reference_code = doc["reference_code"]
    view = serialize_doc(doc)
    email_result = await send_email(
        doc["contact"]["email"],
        f"Dubai vize basvurunuz alindi - {reference_code}",
        applicant_received_html(view),
        kind="application_received",
        meta={"reference_code": reference_code},
    )
    admin_email = os.environ.get("ADMIN_EMAIL") or ""
    if admin_email:
        await send_email(
            admin_email,
            f"Yeni basvuru: {reference_code} ({traveler_count} yolcu)",
            admin_notify_html(view),
            kind="admin_new_application",
            meta={"reference_code": reference_code},
        )
    return email_result


@router.post("/applications")
async def create_application(payload: ApplicationCreate):
    await _validate_extra_documents(payload.extra_documents)
    travelers, prices = await _build_travelers(payload.travelers)

    store_lines = await resolve_store_lines(
        payload.store_items,
        payload.travel.arrival_date,
        payload.travel.departure_date,
    )
    pricing = compute_pricing(
        prices,
        payload.addons.model_dump(),
        addon_prices=await addon_prices_try(),
        store_lines=store_lines,
    )

    reference_code = await _unique_reference_code()
    doc = _build_application_doc(
        payload, travelers, store_lines, pricing, reference_code, datetime.now(timezone.utc)
    )
    await applications_col.insert_one(dict(doc))

    await _link_store_order(doc, store_lines)
    await _after_application_created(doc, travelers)
    email_result = await _send_application_emails(doc, len(travelers))

    result = public_application_view(doc)
    result["email_notification"] = email_result.get("status")
    return result


def _tracking_last_names(doc: dict) -> set[str]:
    """Takip dogrulamasinda kabul edilebilir soyadlarin kucuk harfli kumesi."""
    candidates: set[str] = set()
    for traveler in doc.get("travelers") or []:
        value = (traveler.get("last_name") or "").strip().lower()
        if value:
            candidates.add(value)
    applicant_last = ((doc.get("applicant") or {}).get("last_name") or "").strip().lower()
    if applicant_last:
        candidates.add(applicant_last)
    contact_name = ((doc.get("contact") or {}).get("full_name") or "").strip()
    if contact_name:
        candidates.add(contact_name.split()[-1].lower())
    return candidates


async def _find_application_for_tracking(code: str, last_name: str) -> dict:
    """Takip kodu + soyad dogrulamasi yapar; basarisizsa 400/404 firlatir."""
    code = (code or "").strip().upper()
    last_name = (last_name or "").strip()
    if not code or not last_name:
        raise HTTPException(400, "Takip kodu ve soyad zorunludur.")
    doc = await applications_col.find_one({"reference_code": code})
    if not doc:
        raise HTTPException(404, "Bu takip koduyla bir basvuru bulunamadi.")
    if last_name.lower() not in _tracking_last_names(doc):
        raise HTTPException(404, "Takip kodu ve soyad bilgisi eslesmiyor.")
    return doc


@router.get("/applications/track")
async def track_application(code: str, last_name: str):
    doc = await _find_application_for_tracking(code, last_name)
    view = public_application_view(doc)
    view["missing_documents"] = missing_documents(doc)
    view["timeline"] = build_customer_timeline(doc, view["missing_documents"])
    return view


async def _ensure_upload_exists(file_id: str) -> None:
    """Musterinin gonderdigi file_id'nin gercekten yuklenmis olmasini dogrular."""
    exists = await uploads_col.find_one({"id": file_id, "is_deleted": False})
    if not exists:
        raise HTTPException(400, "Yuklenen belge bulunamadi. Lutfen tekrar yukleyin.")


async def _collect_extra_documents(
    doc: dict, payload: DocumentSubmission, uploaded_keys: list[str]
) -> dict | None:
    """Bilet/otel gibi basvuru geneli belgeleri toplar; degisiklik yoksa None."""
    extra = dict(doc.get("extra_documents") or {})
    changed = False
    for key in ("ticket", "hotel"):
        file_id = getattr(payload, f"{key}_file_id", None)
        if not file_id:
            continue
        await _ensure_upload_exists(file_id)
        extra[f"{key}_file_id"] = file_id
        uploaded_keys.append(key)
        changed = True
    return extra if changed else None


async def _apply_traveler_documents(
    doc: dict, payload: DocumentSubmission, uploaded_keys: list[str]
) -> list[dict] | None:
    """Yolcu bazli pasaport/vesikalik belgelerini yolcu kayitlarina isler."""
    travelers = [dict(t) for t in (doc.get("travelers") or [])]
    for item in payload.traveler_documents or []:
        target = next((t for t in travelers if t.get("id") == item.traveler_id), None)
        if not target:
            raise HTTPException(400, "Yolcu bulunamadi.")
        docs = dict(target.get("documents") or {})
        for key in ("passport", "photo"):
            file_id = getattr(item, f"{key}_file_id", None)
            if not file_id:
                continue
            await _ensure_upload_exists(file_id)
            docs[f"{key}_file_id"] = file_id
            target[f"{key}_file_id"] = file_id
            uploaded_keys.append(f"{key}:{item.traveler_id}")
        target["documents"] = docs
    if any(t.get("documents") for t in travelers):
        return travelers
    return None


async def _notify_documents_uploaded(fresh: dict, uploaded_keys: list[str]) -> None:
    """Belge yuklemesi sonrasi admin bilgilendirmesi (anahtar yoksa sessiz gecer)."""
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email:
        return
    await send_email(
        admin_email,
        f"Musteri belge yukledi - {fresh.get('reference_code', '')}",
        documents_completed_admin_html(fresh, uploaded_keys),
        kind="documents_uploaded",
        meta={"application_id": fresh.get("id")},
    )


@router.post("/applications/{code}/documents")
async def submit_missing_documents(code: str, payload: DocumentSubmission) -> dict:
    """Musterinin takip sayfasindan eksik belgelerini yuklemesi."""
    doc = await _find_application_for_tracking(code, payload.last_name)
    uploaded_keys: list[str] = []
    updates: dict = {}

    extra = await _collect_extra_documents(doc, payload, uploaded_keys)
    if extra is not None:
        updates["extra_documents"] = extra

    travelers = await _apply_traveler_documents(doc, payload, uploaded_keys)
    if travelers is not None:
        updates["travelers"] = travelers

    if not uploaded_keys:
        raise HTTPException(400, "Yuklenecek belge belirtilmedi.")

    updates["updated_at"] = datetime.now(timezone.utc)
    await applications_col.update_one({"id": doc["id"]}, {"$set": updates})
    fresh = await applications_col.find_one({"id": doc["id"]})
    remaining = missing_documents(fresh)

    if not remaining and fresh.get("status") in {"submitted", "documents_pending"}:
        await applications_col.update_one({"id": doc["id"]}, {"$set": {"status": "reviewing"}})
        fresh = await applications_col.find_one({"id": doc["id"]})

    await _notify_documents_uploaded(fresh, uploaded_keys)

    view = public_application_view(fresh)
    view["missing_documents"] = remaining
    view["timeline"] = build_customer_timeline(fresh, remaining)
    return {"application": view, "missing_documents": remaining, "uploaded": uploaded_keys}


# ---------------------------------------------------------------- contact
@router.post("/contact")
async def create_contact(payload: ContactCreate) -> dict:
    msg = payload.model_dump()
    msg.update(
        {
            "id": str(uuid.uuid4()),
            "is_read": False,
            "created_at": datetime.now(timezone.utc),
        }
    )
    await contact_col.insert_one(dict(msg))
    admin_email = os.environ.get("ADMIN_EMAIL") or ""
    if admin_email:
        await send_email(
            admin_email,
            f"Yeni iletisim mesaji: {msg.get('subject') or msg['name']}",
            contact_admin_html(msg),
            kind="contact_message",
        )
    return {"ok": True, "message": "Mesajiniz alindi. En kisa surede size donus yapacagiz."}

