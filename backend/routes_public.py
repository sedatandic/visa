import logging
import os
import random
import string
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile

from content import (
    ADDONS,
    ARTICLES,
    COMPANY,
    FAMILY_DISCOUNT_TEXT,
    FAMILY_DISCOUNT_TIERS,
    FAQ,
    IMPORTANT_NOTICE,
    MAX_TRAVELERS,
    PARTNERS,
    PHOTO_RULES,
    PROCESS_STEPS,
    REQUIRED_DOCUMENTS,
    REVIEW_SUMMARY,
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
)
from emailer import (
    admin_notify_html,
    applicant_received_html,
    contact_admin_html,
    send_email,
)
from models import ApplicationCreate, ContactCreate, QuoteRequest
from passport_ai import read_passport
from storage import APP_NAME, MIME_TYPES, get_object, put_object

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_FILE_BYTES = 10 * 1024 * 1024
ALLOWED_EXT = {"jpg", "jpeg", "png", "webp", "pdf"}


def generate_reference_code() -> str:
    alphabet = "ABCDEFGHJKLMNPRSTUVYZ"
    letters = "".join(random.choices(alphabet, k=2))
    digits = "".join(random.choices(string.digits, k=6))
    return f"DV-{letters}{digits}"


def public_application_view(doc: dict) -> dict:
    d = serialize_doc(doc)
    if not d:
        return d
    d.pop("admin_notes", None)
    return d


async def get_visa_type(visa_type_id: str):
    visa = await visa_types_col.find_one({"id": visa_type_id})
    if not visa:
        visa = next((v for v in VISA_TYPES if v["id"] == visa_type_id), None)
    return visa


# ---------------------------------------------------------------- content
@router.get("/visa-types")
async def get_visa_types():
    docs = await visa_types_col.find({"active": True}).sort("order", 1).to_list(100)
    if not docs:
        return VISA_TYPES
    return serialize_doc(docs)


@router.get("/content/site")
async def get_site_content():
    testimonials = await testimonials_col.find({"published": True}).sort("order", 1).to_list(50)
    summary_doc = await settings_col.find_one({"key": "review_summary"})
    article_docs = (
        await articles_col.find({"published": True}).sort("date", -1).limit(20).to_list(20)
    )
    return {
        "company": COMPANY,
        "visa_categories": VISA_CATEGORIES,
        "addons": list(ADDONS.values()),
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
    }


@router.get("/articles")
async def list_articles(limit: int = 50):
    docs = await articles_col.find({"published": True}).sort("date", -1).limit(limit).to_list(limit)
    if not docs:
        return ARTICLES
    return serialize_doc(docs)


@router.get("/articles/{slug}")
async def get_article(slug: str):
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
    return compute_pricing(prices, payload.addons.model_dump())


# ---------------------------------------------------------------- uploads
@router.post("/uploads")
async def upload_document(file: UploadFile = File(...), doc_type: str = Form("passport")):
    filename = file.filename or "dosya"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXT:
        raise HTTPException(400, "Sadece JPG, PNG, WEBP veya PDF dosyalari yuklenebilir.")
    data = await file.read()
    if len(data) == 0:
        raise HTTPException(400, "Dosya bos gorunuyor. Lutfen tekrar deneyin.")
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(400, "Dosya boyutu en fazla 10 MB olabilir.")

    file_id = str(uuid.uuid4())
    content_type = MIME_TYPES.get(ext, file.content_type or "application/octet-stream")
    safe_type = "".join(c for c in doc_type if c.isalnum() or c in "-_") or "other"
    path = f"{APP_NAME}/uploads/{safe_type}/{file_id}.{ext}"
    try:
        result = put_object(path, data, content_type)
    except Exception as exc:
        logger.error("upload failed: %s", exc)
        raise HTTPException(502, "Dosya yuklenemedi. Lutfen birkac saniye sonra tekrar deneyin.")

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


@router.post("/passport/read")
async def read_passport_document(file_id: str = Form(...)):
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
    try:
        data, ct = get_object(record["storage_path"])
    except Exception as exc:
        logger.error("passport fetch failed: %s", exc)
        raise HTTPException(502, "Dosya okunamadi.")

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
    try:
        data, content_type = get_object(record["storage_path"])
    except Exception as exc:
        logger.error("file fetch failed: %s", exc)
        raise HTTPException(502, "Dosya okunamadi.")
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
@router.post("/applications")
async def create_application(payload: ApplicationCreate):
    travelers = []
    prices = []
    for t in payload.travelers:
        visa = await get_visa_type(t.visa_type_id)
        if not visa:
            raise HTTPException(400, "Gecersiz vize tipi secildi.")
        for fid in (t.passport_file_id, t.photo_file_id):
            exists = await uploads_col.find_one({"id": fid, "is_deleted": False})
            if not exists:
                raise HTTPException(400, "Yuklenen belgeler bulunamadi. Lutfen belgeleri tekrar yukleyin.")
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

    pricing = compute_pricing(prices, payload.addons.model_dump())

    reference_code = generate_reference_code()
    while await applications_col.find_one({"reference_code": reference_code}):
        reference_code = generate_reference_code()

    now = datetime.now(timezone.utc)
    doc = {
        "id": str(uuid.uuid4()),
        "reference_code": reference_code,
        "status": "submitted",
        "contact": payload.contact.model_dump(),
        "travelers": travelers,
        "travel": payload.travel.model_dump(),
        "addons": payload.addons.model_dump(),
        "extra_documents": payload.extra_documents.model_dump(),
        "pricing": pricing,
        "price": pricing["total"],
        "currency": pricing["currency"],
        "processing_days": "24 saat" if payload.addons.express else travelers[0].get("processing_days", ""),
        "visa_type_name": (
            travelers[0]["visa_type_name"]
            if len(travelers) == 1
            else f"{travelers[0]['visa_short_name']} + {len(travelers) - 1} yolcu"
        ),
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
    await applications_col.insert_one(dict(doc))

    email_result = await send_email(
        doc["contact"]["email"],
        f"Dubai vize basvurunuz alindi - {reference_code}",
        applicant_received_html(serialize_doc(doc)),
        kind="application_received",
        meta={"reference_code": reference_code},
    )
    admin_email = os.environ.get("ADMIN_EMAIL") or ""
    if admin_email:
        await send_email(
            admin_email,
            f"Yeni basvuru: {reference_code} ({len(travelers)} yolcu)",
            admin_notify_html(serialize_doc(doc)),
            kind="admin_new_application",
            meta={"reference_code": reference_code},
        )

    result = public_application_view(doc)
    result["email_notification"] = email_result.get("status")
    return result


@router.get("/applications/track")
async def track_application(code: str, last_name: str):
    code = (code or "").strip().upper()
    last_name = (last_name or "").strip()
    if not code or not last_name:
        raise HTTPException(400, "Takip kodu ve soyad zorunludur.")
    doc = await applications_col.find_one({"reference_code": code})
    if not doc:
        raise HTTPException(404, "Bu takip koduyla bir basvuru bulunamadi.")

    candidates = set()
    for t in doc.get("travelers") or []:
        candidates.add((t.get("last_name") or "").strip().lower())
    applicant = doc.get("applicant") or {}
    if applicant.get("last_name"):
        candidates.add(applicant["last_name"].strip().lower())
    contact_name = (doc.get("contact") or {}).get("full_name") or ""
    if contact_name.strip():
        candidates.add(contact_name.strip().split()[-1].lower())

    if last_name.lower() not in candidates:
        raise HTTPException(404, "Takip kodu ve soyad bilgisi eslesmiyor.")
    return public_application_view(doc)


# ---------------------------------------------------------------- contact
@router.post("/contact")
async def create_contact(payload: ContactCreate):
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
