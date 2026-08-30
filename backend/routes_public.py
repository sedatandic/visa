import logging
import os
import random
import string
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile

from content import (
    COMPANY,
    FAQ,
    PHOTO_RULES,
    PROCESS_STEPS,
    REQUIRED_DOCUMENTS,
    STATUS_LABELS,
    TESTIMONIALS,
    VISA_TYPES,
    WHY_US,
)
from db import applications_col, contact_col, serialize_doc, uploads_col, visa_types_col
from emailer import (
    admin_notify_html,
    applicant_received_html,
    contact_admin_html,
    send_email,
)
from models import ApplicationCreate, ContactCreate
from storage import APP_NAME, MIME_TYPES, get_object, put_object

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_FILE_BYTES = 10 * 1024 * 1024
ALLOWED_EXT = {"jpg", "jpeg", "png", "webp", "pdf"}


def generate_reference_code() -> str:
    letters = "".join(random.choices(string.ascii_uppercase.replace("O", "").replace("I", ""), k=2))
    digits = "".join(random.choices(string.digits, k=6))
    return f"DV-{letters}{digits}"


def public_application_view(doc: dict) -> dict:
    d = serialize_doc(doc)
    if not d:
        return d
    d.pop("admin_notes", None)
    return d


# ---------------------------------------------------------------- content
@router.get("/visa-types")
async def get_visa_types():
    docs = await visa_types_col.find({"active": True}).sort("order", 1).to_list(100)
    if not docs:
        return VISA_TYPES
    return serialize_doc(docs)


@router.get("/content/site")
async def get_site_content():
    return {
        "company": COMPANY,
        "process_steps": PROCESS_STEPS,
        "why_us": WHY_US,
        "faq": FAQ,
        "required_documents": REQUIRED_DOCUMENTS,
        "photo_rules": PHOTO_RULES,
        "testimonials": TESTIMONIALS,
        "status_labels": STATUS_LABELS,
    }


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
    path = f"{APP_NAME}/uploads/{doc_type}/{file_id}.{ext}"
    try:
        result = put_object(path, data, content_type)
    except Exception as exc:
        logger.error("upload failed: %s", exc)
        raise HTTPException(502, "Dosya yuklenemedi. Lutfen birkac saniye sonra tekrar deneyin.")

    record = {
        "id": file_id,
        "doc_type": doc_type,
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
        "doc_type": doc_type,
        "original_filename": filename,
        "content_type": content_type,
        "size": record["size"],
        "url": f"/api/files/{file_id}",
    }


@router.get("/files/{file_id}")
async def get_file(file_id: str):
    record = await uploads_col.find_one({"id": file_id, "is_deleted": False})
    if not record:
        raise HTTPException(404, "Dosya bulunamadi.")
    try:
        data, content_type = get_object(record["storage_path"])
    except Exception as exc:
        logger.error("file fetch failed: %s", exc)
        raise HTTPException(502, "Dosya okunamadi.")
    return Response(
        content=data,
        media_type=record.get("content_type") or content_type,
        headers={"Cache-Control": "private, max-age=300"},
    )


# ----------------------------------------------------------- applications
@router.post("/applications")
async def create_application(payload: ApplicationCreate):
    visa = await visa_types_col.find_one({"id": payload.visa_type_id})
    if not visa:
        visa = next((v for v in VISA_TYPES if v["id"] == payload.visa_type_id), None)
    if not visa:
        raise HTTPException(400, "Gecersiz vize tipi.")

    for fid in (payload.documents.passport_file_id, payload.documents.photo_file_id):
        exists = await uploads_col.find_one({"id": fid, "is_deleted": False})
        if not exists:
            raise HTTPException(400, "Yuklenen belgeler bulunamadi. Lutfen belgeleri tekrar yukleyin.")

    # unique reference code
    reference_code = generate_reference_code()
    while await applications_col.find_one({"reference_code": reference_code}):
        reference_code = generate_reference_code()

    now = datetime.now(timezone.utc)
    doc = {
        "id": str(uuid.uuid4()),
        "reference_code": reference_code,
        "status": "submitted",
        "visa_type_id": visa["id"],
        "visa_type_name": visa["name"],
        "processing_days": visa.get("processing_days", ""),
        "price": float(visa["price"]),
        "currency": visa.get("currency", "TRY"),
        "applicant": payload.applicant.model_dump(),
        "travel": payload.travel.model_dump(),
        "documents": payload.documents.model_dump(),
        "payment": {
            "status": "pending",
            "session_id": None,
            "amount": float(visa["price"]),
            "currency": visa.get("currency", "TRY"),
            "paid_at": None,
        },
        "kvkk_accepted": bool(payload.kvkk_accepted),
        "admin_notes": "",
        "status_history": [{"status": "submitted", "at": now, "note": "Basvuru olusturuldu"}],
        "created_at": now,
        "updated_at": now,
    }
    await applications_col.insert_one(dict(doc))

    # emails (never break the flow)
    applicant_email = doc["applicant"]["email"]
    email_result = await send_email(
        applicant_email,
        f"Dubai vize basvurunuz alindi - {reference_code}",
        applicant_received_html(serialize_doc(doc)),
        kind="application_received",
        meta={"reference_code": reference_code},
    )
    admin_email = os.environ.get("ADMIN_EMAIL") or ""
    if admin_email:
        await send_email(
            admin_email,
            f"Yeni basvuru: {reference_code}",
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
    if (doc.get("applicant", {}).get("last_name", "") or "").strip().lower() != last_name.lower():
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
