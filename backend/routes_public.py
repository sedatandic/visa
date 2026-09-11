import logging
import time
import os
import re
import secrets
import string
import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from application_docs import application_email_bundle, application_form_bytes, form_filename
from payment_receipt_pdf import build_receipt_pdf, receipt_filename
from content import (
    MARKETING_CONSENT,
    PRIVACY_POLICY,
    AGENCY_INFO,
    ARTICLES,
    BANK_TRANSFER,
    company_with_defaults,
    FAMILY_DISCOUNT_TEXT,
    FAMILY_DISCOUNT_TIERS,
    FAQ,
    GDRFA_STATUS_URL,
    GDRFA_STEPS,
    IMPORTANT_NOTICE,
    MAX_TRAVELERS,
    PARTNERS,
    PHOTO_RULES,
    PROCESS_STEPS,
    PROMO,
    REFUND_TERMS,
    REQUIRED_DOCUMENTS,
    REVIEW_SUMMARY,
    SERVICE_TERMS,    SERVICES,
    STATUS_LABELS,
    TESTIMONIALS,
    TOURS,
    VISA_CATEGORIES,
    VISA_TYPES,
    WHY_US,
    WITH_VISA_INSURANCE_DISCOUNT,
    affiliation_note,
    compute_pricing,
)
from db import (
    applications_col,
    articles_col,
    contact_col,
    offer_links_col,
    serialize_doc,
    settings_col,
    testimonials_col,
    uploads_col,
    visa_types_col,
    drafts_col,
)
from emailer import (
    admin_notify_html,
    admin_subject,
    applicant_received_html,
    contact_admin_html,
    documents_completed_admin_html,
    send_email,
    subject_with_ref,
)
from models import ApplicationCreate, ContactCreate, DocumentSubmission, QuoteRequest, VisitIn
from doc_reminders import missing_documents
from visitors import client_ip as visitor_client_ip, is_bot, record_visit
from store_catalog import (
    get_visa_type,
    parse_iso_date,
    resolve_store_lines,
    trip_day_count,
)
from fx import addon_prices_try, addons_with_fx, apply_fx_to_list, apply_fx_to_visa, get_fx
import doc_alerts
import ocr_metrics
import offer_links
import social_links
from passport_ai import (
    apply_background_report,
    background_report,
    check_photo,
    compare_passport_photo,
    read_passport,
)
from rate_limit import allow as rate_allow, check as rate_check, client_ip
from usage_quota import consume_daily
import file_access
from storage import APP_NAME, MIME_TYPES, get_object, put_object
from tckn import clean_tckn, valid_tckn
from visa_guides import build_guide, guide_index
import visa_file_number

logger = logging.getLogger(__name__)
router = APIRouter()
file_bearer = HTTPBearer(auto_error=False)

MAX_FILE_BYTES = 10 * 1024 * 1024
ALLOWED_EXT = {"jpg", "jpeg", "png", "webp", "pdf"}
# Kotuye kullanim korumasi: AI cagrilari (OCR/fotograf) ve iletisim formu IP basina sinirli.
AI_MAX_PER_IP_HOUR = 40
CONTACT_MAX_PER_IP_HOUR = 8


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
        "bulletin_date": fx.get("bulletin_date", "") if fx["mode"] == "live" else "",
    }


async def _company_info() -> dict:
    """Sabit sirket bilgileri uzerine admin panelinden girilen alanlar yazilir."""
    company_doc = await settings_col.find_one({"key": "company_info"})
    return company_with_defaults((company_doc or {}).get("value"))


def _agency_info(company: dict) -> dict:
    """Acente seffaflik blogu; degeri bos olan satirlar gizlenir."""
    rows = (
        ("Ticaret Unvanı", company.get("legal_name", "")),
        ("TÜRSAB Belge No", company.get("tursab_no", "")),
        ("Acente Türü", company.get("tursab_type", "")),
        (
            "Vergi Dairesi / No",
            f"{company.get('tax_office', '')} / {company.get('tax_no', '')}"
            if company.get("tax_office") and company.get("tax_no")
            else "",
        ),
        ("MERSİS No", company.get("mersis_no", "")),
        ("Ticaret Sicil No", company.get("trade_registry_no", "")),
        ("Adres", company.get("address", "")),
        ("Kuruluş", company.get("founded_year", "")),
    )
    return {
        **AGENCY_INFO,
        "items": [{"label": label, "value": value} for label, value in rows if value],
    }


async def _bank_transfer_info() -> dict:
    """Havale/EFT bilgileri: admin ayari yoksa varsayilan blok kullanilir."""
    doc = await settings_col.find_one({"key": "bank_transfer"})
    return {**BANK_TRANSFER, **((doc or {}).get("value") or {})}


@router.get("/content/site")
async def get_site_content() -> dict:
    testimonials = await testimonials_col.find({"published": True}).sort("order", 1).to_list(50)
    summary_doc = await settings_col.find_one({"key": "review_summary"})
    article_docs = (
        await articles_col.find({"published": True}).sort("date", -1).limit(20).to_list(20)
    )
    company = await _company_info()
    social_doc = await settings_col.find_one({"key": "social_links"})
    return {
        "company": company,
        "social_links": social_links.public_links(company, (social_doc or {}).get("value")),
        "visa_categories": VISA_CATEGORIES,
        "addons": await addons_with_fx(),
        "fx": await get_fx(),
        "family_discount_tiers": [{"min": m, "rate": r} for m, r in FAMILY_DISCOUNT_TIERS],
        "visa_insurance": WITH_VISA_INSURANCE_DISCOUNT,
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
        "agency_info": _agency_info(company),
        "affiliation": affiliation_note(company),
        "bank_transfer": await _bank_transfer_info(),
    }


@router.get("/content/legal")
async def get_legal_content() -> dict:
    return {
        "refund_terms": REFUND_TERMS,
        "service_terms": SERVICE_TERMS,
        "privacy_policy": PRIVACY_POLICY,
        "marketing_consent": MARKETING_CONSENT,
        "affiliation": affiliation_note(await _company_info()),
    }


@router.get("/articles")
async def list_articles(limit: int = 50):
    docs = await articles_col.find({"published": True}).sort("date", -1).limit(limit).to_list(limit)
    if not docs:
        return ARTICLES
    return serialize_doc(docs)


@router.post("/track/visit")
async def track_visit(payload: VisitIn, request: Request, background: BackgroundTasks) -> dict:
    """Ziyaret kaydi: IP + sehir/ulke cozumlemesi arka planda yapilir."""
    user_agent = request.headers.get("user-agent", "")
    if is_bot(user_agent):
        return {"ok": True, "skipped": "bot"}
    background.add_task(record_visit, visitor_client_ip(request), payload.path, payload.referrer, user_agent)
    return {"ok": True}


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


@router.get("/offers/{token}")
async def get_offer_link(token: str, request: Request) -> dict:
    """Yoneticinin hazirladigi teklif linki: musteriye gosterilecek ozet + guncel fiyat."""
    rate_check(
        f"offer-view-ip:{client_ip(request)}",
        120,
        3600,
        "Cok fazla istek. Lutfen birkac dakika sonra tekrar deneyin.",
    )
    doc = await offer_links_col.find_one({"token": (token or "").strip()})
    if not doc or not doc.get("active", True):
        raise HTTPException(404, "Teklif bulunamadı. Lütfen danışmanınızdan yeni bir bağlantı isteyin.")
    if offer_links.is_expired(doc):
        raise HTTPException(
            404, "Bu teklifin geçerlilik süresi doldu. Güncel fiyat için bize yazabilirsiniz."
        )
    await offer_links_col.update_one(
        {"token": doc["token"]},
        {
            "$inc": {"views": 1},
            "$set": {"last_viewed_at": datetime.now(timezone.utc)},
            "$min": {"first_viewed_at": datetime.now(timezone.utc)},
        },
    )
    return await offer_links.public_view(doc)


# ---------------------------------------------------------------- uploads
def _validate_upload(filename: str, data: bytes) -> str:
    """Uzanti, boyut ve dosya imzasi (magic byte) dogrulamasi yapar."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, "Sadece JPG, PNG, WEBP veya PDF dosyalari yuklenebilir.")
    if len(data) == 0:
        raise HTTPException(400, "Dosya bos gorunuyor. Lutfen tekrar deneyin.")
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(400, "Dosya boyutu en fazla 10 MB olabilir.")
    if not _signature_matches(data):
        raise HTTPException(
            400, "Dosya icerigi taninamadi. Lutfen gercek bir JPG, PNG, WEBP veya PDF yukleyin."
        )
    return ext


def _signature_matches(data: bytes) -> bool:
    """Icerigin gercekten izin verilen bir tur oldugunu imzadan dogrular."""
    head = data[:16]
    if head.startswith(b"\xff\xd8\xff"):  # JPEG
        return True
    if head.startswith(b"\x89PNG\r\n\x1a\n"):  # PNG
        return True
    if head.startswith(b"%PDF-"):  # PDF
        return True
    return head[:4] == b"RIFF" and data[8:12] == b"WEBP"  # WEBP


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
async def upload_document(
    request: Request, file: UploadFile = File(...), doc_type: str = Form("passport")
) -> dict:
    # Kimlik dogrulamasiz uc: ayni IP'den depolama sismesini onler
    # (bir aile basvurusu tipik olarak 12-14 dosya yukler)
    rate_check(
        f"upload:{client_ip(request)}",
        150,
        60,
        "Cok fazla dosya yuklediniz. Lutfen birkac dakika sonra tekrar deneyin.",
    )
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
        "url": file_access.file_path(file_id, file_access.TTL_UPLOAD),
    }


def _photo_check_message(result: dict) -> str:
    """AI sonucuna gore kullaniciya gosterilecek ozet mesaji secer."""
    if not result.get("is_photo"):
        return "Bu goruntu vesikalik fotograf gibi gorunmuyor. Lutfen yuzunuzun net gorundugu bir portre yukleyin."
    if "background_ok" in (result.get("failed") or []):
        return "Arka plan beyaz degil. Vize icin duz beyaz zeminde cekilmis vesikalik gerekir."
    if result.get("ok"):
        return "Fotograf vize standartlarina uygun gorunuyor."
    return "Fotografta duzeltilmesi onerilen noktalar var."


async def _store_photo_check(file_id: str, result: dict) -> None:
    """Denetim sonucunu dosya kaydina isler."""
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


async def _photo_background_fallback(file_id: str, background: dict) -> dict:
    """AI cevap vermezse en az beyaz zemin sartini raporlar."""
    fallback = apply_background_report(
        {
            "ok": True,
            "is_photo": True,
            "checks": {},
            "failed": [],
            "issues": [],
            "advice": "",
            "score": 0.5,
        },
        background,
    )
    await _store_photo_check(file_id, fallback)
    return {
        "checked": True,
        "reason": "background_only",
        "message": _photo_check_message(fallback),
        **fallback,
    }


@router.post("/photo/check")
async def check_photo_document(request: Request, file_id: str = Form(...)) -> dict:
    """Yuklenen vesikalik fotografi yapay zeka ile denetler (uyari amacli, engellemez)."""
    rate_check(
        f"photo-check-ip:{client_ip(request)}",
        AI_MAX_PER_IP_HOUR,
        3600,
        "Cok fazla fotograf kontrolu. Lutfen bir sure sonra tekrar deneyin.",
    )
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

    background = background_report(data)
    await consume_daily(
        "photo_check",
        "Fotograf kontrolu gunluk siniri doldu. Lutfen yarin tekrar deneyin.",
    )
    try:
        result = await check_photo(data, content_type or ct)
    except Exception as exc:
        logger.error("photo ai failed: %s", exc)
        if background.get("checked") and not background.get("ok"):
            return await _photo_background_fallback(file_id, background)
        return {
            "ok": True,
            "checked": False,
            "reason": "ai_error",
            "message": "Fotograf otomatik kontrol edilemedi; basvurunuza devam edebilirsiniz.",
        }

    result = apply_background_report(result, background)
    await _store_photo_check(file_id, result)
    return {"checked": True, "message": _photo_check_message(result), **result}


MATCH_MISMATCH_MESSAGE = (
    "Pasaporttaki fotoğraf ile yüklediğiniz vesikalık aynı kişiye ait görünmüyor. "
    "Lütfen doğru kişinin vesikalık fotoğrafını yükleyin."
)


@router.post("/photo/match")
async def match_photo_with_passport(
    request: Request,
    passport_file_id: str = Form(...),
    photo_file_id: str = Form(...),
) -> dict:
    """Pasaport sayfasindaki fotograf ile vesikaligi karsilastirir (uyari amacli)."""
    rate_check(
        f"photo-match-ip:{client_ip(request)}",
        AI_MAX_PER_IP_HOUR,
        3600,
        "Cok fazla fotograf karsilastirmasi. Lutfen bir sure sonra tekrar deneyin.",
    )
    passport_record = await _get_upload_record(passport_file_id)
    photo_record = await _get_upload_record(photo_file_id)
    photo_type = photo_record.get("content_type") or ""
    if photo_type == "application/pdf":
        return {"checked": False, "reason": "pdf", "message": ""}

    passport_data, passport_ct = _read_upload_bytes(passport_record)
    photo_data, photo_ct = _read_upload_bytes(photo_record)

    await consume_daily(
        "photo_match",
        "Fotograf karsilastirma gunluk siniri doldu. Lutfen yarin tekrar deneyin.",
    )
    try:
        result = await compare_passport_photo(
            passport_data,
            passport_record.get("content_type") or passport_ct,
            photo_data,
            photo_type or photo_ct,
        )
    except Exception as exc:
        logger.error("photo match failed: %s", exc)
        return {"checked": False, "reason": "ai_error", "message": ""}

    message = ""
    if result.get("same_person") is False:
        message = MATCH_MISMATCH_MESSAGE
    return {"checked": True, "message": message, **result}


async def _ocr_failure(
    file_id: str,
    duration_ms: int,
    reason: str,
    message: str,
    data: dict | None = None,
    contact: dict | None = None,
) -> dict:
    """Basarisiz OCR denemesini olcume yazar ve istemciye ayni bicimde yanit dondurur."""
    await ocr_metrics.record_attempt(
        file_id=file_id, duration_ms=duration_ms, ok=False, reason=reason, data=data or {}
    )
    # Ekip aninda haberdar olsun (panel + WhatsApp + e-posta); bildirim hatasi akisi bozmaz
    try:
        await doc_alerts.notify_unreadable_passport(file_id, reason, contact or {})
    except Exception as exc:  # pragma: no cover
        logger.warning("passport alert failed: %s", exc)
    payload = {"ok": False, "reason": reason, "message": message}
    if data is not None:
        payload["data"] = data
    return payload


async def _ocr_success(file_id: str, result: dict, duration_ms: int) -> dict:
    """Okunan pasaport verisini olcume ve dosya kaydina isler."""
    coverage = await ocr_metrics.record_attempt(
        file_id=file_id, duration_ms=duration_ms, ok=True, data=result
    )
    # Okunan alanlar dosya kaydinda saklanir: basvuru olusurken musteriye sorulmayan
    # alanlar (dogum yeri, verilis yeri/tarihi) buradan tamamlanir.
    await uploads_col.update_one(
        {"id": file_id},
        {
            "$set": {
                "ocr": {
                    "at": datetime.now(timezone.utc),
                    "confidence": result.get("confidence"),
                    "fields": {
                        field: str(result.get(field) or "")
                        for field in ocr_metrics.TRACKED_FIELDS
                    },
                }
            }
        },
    )
    return {
        "ok": True,
        "data": result,
        "duration_ms": duration_ms,
        "filled_count": len(coverage["filled"]),
        "missing_fields": [ocr_metrics.FIELD_LABELS.get(m, m) for m in coverage["missing"]],
    }


async def _get_upload_record(file_id: str) -> dict:
    """Silinmemis upload kaydini dondurur, yoksa 404 atar."""
    record = await uploads_col.find_one({"id": file_id, "is_deleted": False})
    if not record:
        raise HTTPException(404, "Dosya bulunamadi.")
    return record


def _read_upload_bytes(record: dict) -> tuple[bytes, str]:
    """Upload kaydinin icerigini object storage'dan okur."""
    try:
        return get_object(record["storage_path"])
    except Exception as exc:
        logger.error("file fetch failed: %s", exc)
        raise HTTPException(502, "Dosya okunamadi.") from exc


@router.post("/passport/read")
async def read_passport_document(
    request: Request,
    file_id: str = Form(...),
    contact_name: str = Form(""),
    contact_phone: str = Form(""),
    contact_email: str = Form(""),
) -> dict:
    """Yuklenen pasaport goruntusunu yapay zeka ile okuyup form alanlarini doldurur.

    Her deneme sure + alan kapsamiyla olculur (`ocr_metrics`), boylece "form ne
    kadar hizli doluyor, hangi alanlar okunamiyor" raporlanabilir.
    """
    rate_check(
        f"passport-read-ip:{client_ip(request)}",
        AI_MAX_PER_IP_HOUR,
        3600,
        "Cok fazla pasaport okuma denemesi. Lutfen bir sure sonra tekrar deneyin.",
    )
    record = await _get_upload_record(file_id)
    content_type = record.get("content_type") or ""
    started = time.perf_counter()

    def elapsed_ms() -> int:
        return int((time.perf_counter() - started) * 1000)

    data, ct = _read_upload_bytes(record)
    contact = {"name": contact_name, "phone": contact_phone, "email": contact_email}

    await consume_daily(
        "passport_ocr",
        "Pasaport okuma gunluk siniri doldu. Bilgileri elle girebilir ya da yarin tekrar deneyebilirsiniz.",
    )
    try:
        result = await read_passport(data, content_type or ct)
    except Exception as exc:
        logger.error("passport ai failed: %s", exc)
        return await _ocr_failure(
            file_id,
            elapsed_ms(),
            "ai_error",
            "Pasaport otomatik okunamadi. Bilgileri elle girebilirsiniz.",
            contact=contact,
        )

    if not result.get("is_passport") or not (result.get("passport_no") or result.get("last_name")):
        return await _ocr_failure(
            file_id,
            elapsed_ms(),
            "not_readable",
            "Goruntuden bilgiler okunamadi. Daha net bir fotograf yukleyin veya elle girin.",
            data=result,
            contact=contact,
        )

    return await _ocr_success(file_id, result, elapsed_ms())


@router.get("/files/{file_id}")
async def get_file(
    file_id: str,
    download: int = 0,
    t: str = "",
    creds: HTTPAuthorizationCredentials | None = Depends(file_bearer),
):
    """Dosyalar yalnizca imzali baglanti (?t=) veya yonetici jetonu ile acilir."""
    token = creds.credentials if creds else ""
    if not file_access.token_valid(file_id, t) and not file_access.admin_token_valid(token):
        raise HTTPException(
            403, "Bu belgeye erisim izniniz yok veya baglantinin suresi doldu."
        )
    record = await _get_upload_record(file_id)
    data, content_type = _read_upload_bytes(record)
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


def _fill_uae_defaults(data: dict) -> None:
    """BAE formunda zorunlu olan ama musteriye sorulmayan alanlari doldurur.
    Admin, basvuru detayindan bu degerleri Zami aktarimindan once duzeltebilir."""
    if not data.get("marital_status"):
        data["marital_status"] = "single"
    if not data.get("profession"):
        data["profession"] = "Student" if data.get("applicant_type") == "child" else "Employee"
    surname = (data.get("last_name") or "").strip()
    if not (data.get("mother_name") or "").strip():
        data["mother_name"] = surname
    if not (data.get("father_name") or "").strip():
        data["father_name"] = surname


# Musteriye sorulmayan, yalnizca pasaporttan okunan alanlar
PASSPORT_ONLY_FIELDS = ("birth_place", "passport_issue_place", "passport_issue_date", "nationality")


async def _fill_from_passport_ocr(data: dict) -> None:
    """Bos kalan pasaport alanlarini (dogum yeri vb.) yuklenen pasaportun okumasindan tamamlar."""
    missing = [field for field in PASSPORT_ONLY_FIELDS if not str(data.get(field) or "").strip()]
    file_id = str(data.get("passport_file_id") or "")
    if not missing or not file_id:
        return
    record = await uploads_col.find_one({"id": file_id}, {"ocr": 1})
    fields = ((record or {}).get("ocr") or {}).get("fields") or {}
    for field in missing:
        value = str(fields.get(field) or "").strip()
        if value:
            data[field] = value


async def _build_travelers(traveler_inputs, travel=None) -> tuple[list, list]:
    """Yolcu girdilerini vize bilgileri ile zenginlestirir; (travelers, prices) dondurur."""
    travelers: list = []
    prices: list = []
    for t in traveler_inputs:
        visa = await get_visa_type(t.visa_type_id)
        if not visa:
            raise HTTPException(400, "Gecersiz vize tipi secildi.")
        data = t.model_dump()
        _fill_uae_defaults(data)
        await _fill_from_passport_ocr(data)
        data.update(
            {
                "id": str(uuid.uuid4()),
                "visa_type_name": visa["name"],
                "visa_short_name": visa.get("short_name", visa["name"]),
                "visa_duration_days": int(visa.get("duration_days") or 0),
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

    # Once kabul kurallari (yas, kalis suresi, pasaport gecerliligi), sonra dosya kontrolu
    _reject_duplicate_documents(traveler_inputs)
    if travel is not None:
        _validate_travel_rules(travel, travelers)
    for t in traveler_inputs:
        await _ensure_uploads_exist(t.passport_file_id, t.photo_file_id)
    return travelers, prices


def _reject_duplicate_documents(traveler_inputs) -> None:
    """Ayni pasaport numarasi/dosyasi iki yolcuda olamaz (yanlislikla ayni belge yuklenmesi)."""
    checks = (
        ("passport_no", lambda t: (t.passport_no or "").strip().upper(), "pasaport numarasi"),
        ("passport_file_id", lambda t: t.passport_file_id, "pasaport fotografi"),
        ("photo_file_id", lambda t: t.photo_file_id, "vesikalik fotografi"),
    )
    for _field, pick, label in checks:
        seen: dict[str, int] = {}
        for index, traveler in enumerate(traveler_inputs, start=1):
            key = pick(traveler)
            if not key:
                continue
            if key in seen:
                raise HTTPException(
                    400,
                    f"{seen[key]}. ve {index}. yolcuda ayni {label} kullanilmis. "
                    "Her yolcu icin kendi belgesini yukleyin.",
                )
            seen[key] = index


# Basvuru kabul kurallari (BAE gocmenlik idaresi sartlari)
PASSPORT_MIN_VALID_DAYS = 180


def _age_on(birth_date, reference) -> float | None:
    if not birth_date or not reference:
        return None
    return (reference - birth_date).days / 365.25


def _travel_window(travel) -> tuple:
    """Gidis/donus tarihlerini dogrular; tarih belli degilse kalis suresi None doner."""
    arrival = parse_iso_date(travel.arrival_date)
    departure = parse_iso_date(travel.departure_date)
    if bool(getattr(travel, "dates_unknown", False)):
        return arrival, departure, None
    if not arrival or not departure:
        raise HTTPException(400, "Gidis ve donus tarihlerini gecerli bir formatta gonderin.")
    if departure < arrival:
        raise HTTPException(400, "Donus tarihi gidis tarihinden once olamaz.")
    if arrival < date.today():
        raise HTTPException(400, "Gidis tarihi bugunden once olamaz.")
    return arrival, departure, (departure - arrival).days + 1


def _validate_child_traveler(name: str, age: float | None, has_adult: bool) -> None:
    """Cocuk vizesi yas siniri ve refakatci yetiskin sarti."""
    if age is not None and age >= 18:
        raise HTTPException(400, f"{name}: cocuk vizesi yalnizca 18 yasindan kucuk yolcular icindir.")
    if not has_adult:
        raise HTTPException(
            400,
            "18 yas alti yolcular, ayni basvuruda en az bir yetiskin yolcu ile birlikte basvurmalidir.",
        )


def _validate_stay_within_visa(name: str, traveler: dict, stay_days: int | None) -> None:
    """Planlanan kalis, secilen vizenin verdigi kalis hakkini asamaz."""
    duration = int(traveler.get("visa_duration_days") or 0)
    if duration and stay_days and stay_days > duration:
        raise HTTPException(
            400,
            f"{name}: secilen vize {duration} gun kalis hakki veriyor; planlanan kalis {stay_days} gun. "
            "Daha uzun sureli bir vize secin veya tarihlerinizi guncelleyin.",
        )


def _validate_passport_validity(name: str, traveler: dict, reference, has_departure: bool) -> None:
    """Pasaport, donus (ya da tarih yoksa bugun) itibariyla en az 6 ay gecerli olmalidir."""
    expiry = parse_iso_date(traveler.get("passport_expiry"))
    if expiry and (expiry - reference).days < PASSPORT_MIN_VALID_DAYS:
        basis = "donus tarihinden" if has_departure else "bugunden"
        raise HTTPException(400, f"{name}: pasaportunuz {basis} itibaren en az 6 ay gecerli olmalidir.")


def _validate_travel_rules(travel, travelers: list) -> None:
    """Vize suresi, yas ve pasaport gecerliligi kurallarini sunucu tarafinda dogrular."""
    arrival, departure, stay_days = _travel_window(travel)

    # Tarih belli degilse yas ve pasaport kontrolleri bugunun tarihine gore yapilir
    age_reference = arrival or date.today()
    expiry_reference = departure or date.today()
    has_adult = any(t.get("applicant_type") != "child" for t in travelers)

    for traveler in travelers:
        name = f"{traveler.get('first_name', '')} {traveler.get('last_name', '')}".strip()
        if traveler.get("applicant_type") == "child":
            age = _age_on(parse_iso_date(traveler.get("birth_date")), age_reference)
            _validate_child_traveler(name, age, has_adult)
        _validate_stay_within_visa(name, traveler, stay_days)
        _validate_passport_validity(name, traveler, expiry_reference, bool(departure))




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
        "processing_days": (
            "12 saat içinde"
            if payload.addons.express
            else travelers[0].get("processing_days", "")
        ),
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
        "consents": {
            **payload.consents.model_dump(),
            "accepted_at": now,
        },
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
    """Basvuru sahibine ve admine bilgilendirme e-postalari gonderir (form PDF + evraklar ekli)."""
    reference_code = doc["reference_code"]
    view = serialize_doc(doc)
    try:
        bundle = await application_email_bundle(doc)
    except Exception as exc:  # pragma: no cover - ekler hazirlanamazsa posta yine gider
        logger.error("basvuru ekleri hazirlanamadi: %s", exc)
        bundle = {"attachments": [], "documents": [], "form_filename": ""}
    # Ayni alici saatte 40'tan fazla basvuru postasi almaz (bombardiman engeli);
    # basvuru her durumda olusur, yalnizca musteri bildirimi atlanir.
    if rate_allow(f"app-mail:{doc['contact']['email'].strip().lower()}", 40, 3600):
        email_result = await send_email(
            doc["contact"]["email"],
            subject_with_ref(reference_code, "alındı"),
            applicant_received_html(view, bundle["documents"], bundle["form_filename"]),
            kind="application_received",
            meta={"reference_code": reference_code},
            attachments=bundle["attachments"],
        )
    else:
        email_result = {"status": "skipped", "reason": "recipient hourly mail limit"}
    admin_email = os.environ.get("ADMIN_EMAIL") or ""
    if admin_email:
        await send_email(
            admin_email,
            admin_subject(view),
            admin_notify_html(view, bundle["documents"], bundle["form_filename"]),
            kind="admin_new_application",
            meta={"reference_code": reference_code},
            attachments=bundle["attachments"],
        )
    return email_result


def pdf_response(pdf: bytes, filename: str) -> Response:
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/applications/form.pdf")
async def application_form_pdf(code: str, last_name: str):
    """Takip kodu + soyad ile tek sayfalik basvuru formunu indirir."""
    doc = await _find_application_for_tracking(code, last_name)
    return pdf_response(await application_form_bytes(doc), form_filename(doc))


@router.get("/applications/receipt.pdf")
async def application_receipt_pdf(code: str, last_name: str):
    """Takip kodu + soyad ile odeme ozetini (PDF) indirir."""
    doc = await _find_application_for_tracking(code, last_name)
    return pdf_response(build_receipt_pdf(serialize_doc(doc)), receipt_filename(doc))


def _validate_insurance_identity(travelers: list, store_lines: list) -> None:
    """Sigorta secildiyse her yolcu icin gecerli TC kimlik no zorunludur (police sarti)."""
    if not any((line.get("kind") or "") == "insurance" for line in store_lines):
        return
    for traveler in travelers:
        digits = clean_tckn(traveler.get("tc_kimlik_no") or traveler.get("national_id") or "")
        if not valid_tckn(digits):
            name = f"{traveler.get('first_name', '')} {traveler.get('last_name', '')}".strip()
            raise HTTPException(
                400,
                f"{name or 'Yolcu'}: seyahat sağlık sigortası için geçerli TC kimlik numarası gerekiyor.",
            )
        traveler["tc_kimlik_no"] = digits


@router.post("/applications")
async def create_application(payload: ApplicationCreate, request: Request):
    rate_check(
        f"app-create-ip:{client_ip(request)}",
        300,
        3600,
        "Cok fazla basvuru olusturma denemesi. Lutfen daha sonra tekrar deneyin.",
    )
    await _validate_extra_documents(payload.extra_documents)
    travelers, prices = await _build_travelers(payload.travelers, payload.travel)

    store_lines = await resolve_store_lines(
        payload.store_items,
        payload.travel.arrival_date,
        payload.travel.departure_date,
    )
    _validate_insurance_identity(travelers, store_lines)
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
    await offer_links.mark_used(payload.offer_token or "", doc)
    email_result = await _send_application_emails(doc, len(travelers))

    result = public_application_view(doc)
    result["email_notification"] = email_result.get("status")
    return result


def _tracking_name_sources(doc: dict):
    """Takip dogrulamasinda kullanilabilecek ham soyad adaylarini uretir."""
    for traveler in doc.get("travelers") or []:
        yield traveler.get("last_name")
    yield (doc.get("applicant") or {}).get("last_name")
    contact_name = ((doc.get("contact") or {}).get("full_name") or "").strip()
    yield contact_name.split()[-1] if contact_name else ""


def _tracking_last_names(doc: dict) -> set[str]:
    """Takip dogrulamasinda kabul edilebilir soyadlarin kucuk harfli kumesi."""
    names = ((raw or "").strip().lower() for raw in _tracking_name_sources(doc))
    return {name for name in names if name}


GUARANTEE_HOURS = 36


def _as_datetime(value) -> datetime | None:
    """Datetime ya da ISO string degerini UTC datetime'a cevirir."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str) and value.strip():
        try:
            parsed = datetime.fromisoformat(value.strip())
        except ValueError:
            return None
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None


def build_guarantee_status(doc: dict) -> dict:
    """36 saat garantisinin durumu: sure ne zaman basladi, ne kadar kaldi.

    Sure, belgeler onaylanip basvuru resmi mercilere iletildiginde baslar
    (portala aktarim ya da "inceleniyor" durumu).
    """
    history = _first_status_dates(doc)
    start = _as_datetime(doc.get("zami_transferred_at")) or _as_datetime(history.get("reviewing"))
    finished = _as_datetime(history.get("approved")) or _as_datetime(history.get("rejected"))
    status = doc.get("status") or "submitted"

    info = {
        "hours": GUARANTEE_HOURS,
        "start_at": _iso_or_none(start),
        "deadline_at": None,
        "finished_at": _iso_or_none(finished),
        "remaining_seconds": None,
        "state": "pending",
    }
    if status == "cancelled":
        info["state"] = "closed"
        return info
    if not start:
        # Sonuc cikmis ama sure baslangici kaydedilmemisse taahhut kapanmis sayilir
        if finished or status in {"approved", "rejected"}:
            info["state"] = "met"
        return info

    deadline = start + timedelta(hours=GUARANTEE_HOURS)
    info["deadline_at"] = _iso_or_none(deadline)
    if finished:
        info["state"] = "met" if finished <= deadline else "missed"
        return info

    remaining = (deadline - datetime.now(timezone.utc)).total_seconds()
    info["remaining_seconds"] = int(remaining)
    info["state"] = "running" if remaining > 0 else "overdue"
    return info


async def _find_application_for_tracking(code: str, last_name: str) -> dict:
    """Takip kodu + soyad dogrulamasi yapar; basarisizsa 400/404 firlatir."""
    code = (code or "").strip().upper()
    last_name = (last_name or "").strip()
    if not code or not last_name:
        raise HTTPException(400, "Takip kodu ve soyad zorunludur.")
    doc = await applications_col.find_one({"reference_code": code})
    # Kod bulunamadi ve soyad eslesmedi durumlari ayni yaniti dondurur (kod tarama engeli).
    if not doc or last_name.lower() not in _tracking_last_names(doc):
        raise HTTPException(404, "Takip kodu ve soyad bilgisi eslesmiyor.")
    return doc


@router.get("/applications/track")
async def track_application(code: str, last_name: str, request: Request):
    # Takip kodu tahmin denemelerini yavaslatir (kod + soyad zaten gerekli)
    rate_check(
        f"track:{client_ip(request)}",
        60,
        300,
        "Cok fazla sorgu yaptiniz. Lutfen birkac dakika sonra tekrar deneyin.",
    )
    doc = await _find_application_for_tracking(code, last_name)
    view = public_application_view(doc)
    view["missing_documents"] = missing_documents(doc)
    view["timeline"] = build_customer_timeline(doc, view["missing_documents"])
    view["guarantee"] = build_guarantee_status(doc)
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


async def _attach_traveler_files(target: dict, item, uploaded_keys: list[str]) -> None:
    """Tek yolcunun pasaport/vesikalik dosyalarini kaydina isler."""
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


async def _apply_traveler_documents(
    doc: dict, payload: DocumentSubmission, uploaded_keys: list[str]
) -> list[dict] | None:
    """Yolcu bazli pasaport/vesikalik belgelerini yolcu kayitlarina isler."""
    travelers = [dict(t) for t in (doc.get("travelers") or [])]
    for item in payload.traveler_documents or []:
        target = next((t for t in travelers if t.get("id") == item.traveler_id), None)
        if not target:
            raise HTTPException(400, "Yolcu bulunamadi.")
        await _attach_traveler_files(target, item, uploaded_keys)
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
        f"Müşteri belge yükledi - {fresh.get('reference_code', '')}",
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
async def create_contact(payload: ContactCreate, request: Request) -> dict:
    rate_check(
        f"contact-ip:{client_ip(request)}",
        CONTACT_MAX_PER_IP_HOUR,
        3600,
        "Cok fazla mesaj gonderdiniz. Lutfen bir sure sonra tekrar deneyin.",
    )
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
            f"Yeni iletişim mesajı: {msg.get('subject') or msg['name']}",
            contact_admin_html(msg),
            kind="contact_message",
        )
    return {"ok": True, "message": "Mesajınız alındı. En kısa sürede size dönüş yapacağız."}



# --------------------------------------------------------- GDRFA dogrulama sayfasi
@router.get("/visa-verify/{application_id}")
async def visa_verify(application_id: str, t: str = "") -> dict:
    """Musteriye ozel dogrulama bilgileri: dosya numarasi, ad ve dogum tarihi.

    GDRFA sayfasi ASP.NET ViewState kullandigi icin hazir dolu bir baglantiyla
    acilamiyor. Bunun yerine musteriye bu sayfayi gonderiyoruz: bilgiler tek
    dokunusla kopyalanir, belgenin icinde numara aranmaz.
    """
    if not file_access.token_valid(application_id, t):
        raise HTTPException(403, "Bağlantının süresi dolmuş. Yeni bağlantı için bize yazın.")
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc or not (app_doc.get("visa_result") or {}).get("file_id"):
        raise HTTPException(404, "Vize belgesi bulunamadı.")

    visa = app_doc.get("visa_result") or {}
    numbers = visa.get("file_numbers") or ([visa["file_number"]] if visa.get("file_number") else [])
    travelers = app_doc.get("travelers") or []
    paired = len(numbers) == len(travelers)
    return {
        "reference_code": app_doc.get("reference_code", ""),
        "gdrfa_url": GDRFA_STATUS_URL,
        "steps": list(GDRFA_STEPS),
        "file_numbers": [
            {"formatted": number, "plain": visa_file_number.plain(number)} for number in numbers
        ],
        "travelers": [
            {
                "first_name": (traveler.get("first_name") or "").strip(),
                "last_name": (traveler.get("last_name") or "").strip(),
                "birth_date": traveler.get("birth_date") or "",
                "nationality": traveler.get("nationality") or "TR",
                "file_number": numbers[index] if paired else "",
                "file_number_plain": visa_file_number.plain(numbers[index]) if paired else "",
            }
            for index, traveler in enumerate(travelers)
        ],
    }
