import logging
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import quote

import jwt
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from content import STATUS_LABELS
from db import (
    applications_col,
    articles_col,
    contact_col,
    email_outbox_col,
    notifications_col,
    payments_col,
    serialize_doc,
    settings_col,
    testimonials_col,
    uploads_col,
    visa_types_col,
)
from content import BANK_TRANSFER, COMPANY
from emailer import payment_received_html, send_email, status_change_html, visa_ready_html
from models import (
    AdminLogin,
    ArticleIn,
    BankTransferIn,
    CompanyInfoIn,
    ReviewSummaryIn,
    SendVisaRequest,
    StatusUpdate,
    TestimonialIn,
    WhatsAppRequest,
)
from storage import APP_NAME, MIME_TYPES, put_object

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)

JWT_SECRET = os.environ.get("JWT_SECRET", "dv-dev-secret")
JWT_ALGO = "HS256"

# Demo admin account (documented in /app/memory/test_credentials.md)
ADMIN_USERS = {
    "admin@vizeatlas.com": {"password": "Dubai2026!", "name": "Yonetici"},
}


def create_token(email: str) -> str:
    payload = {
        "sub": email,
        "role": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


async def require_admin(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not creds or not creds.credentials:
        raise HTTPException(401, "Yetkisiz erisim. Lutfen giris yapin.")
    try:
        data = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Oturum suresi doldu. Lutfen tekrar giris yapin.")
    except Exception:
        raise HTTPException(401, "Gecersiz oturum.")
    if data.get("role") != "admin":
        raise HTTPException(403, "Bu islem icin yetkiniz yok.")
    return data


@router.post("/admin/login")
async def admin_login(payload: AdminLogin):
    email = (payload.email or "").strip().lower()
    user = ADMIN_USERS.get(email)
    if not user or user["password"] != payload.password:
        raise HTTPException(401, "E-posta veya sifre hatali.")
    return {"token": create_token(email), "user": {"email": email, "name": user["name"]}}


@router.get("/admin/me")
async def admin_me(admin=Depends(require_admin)):
    return {"email": admin["sub"], "role": admin["role"]}


@router.get("/admin/stats")
async def admin_stats(admin=Depends(require_admin)):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    total = await applications_col.count_documents({})
    today_count = await applications_col.count_documents({"created_at": {"$gte": today}})
    payment_pending = await applications_col.count_documents({"payment.status": {"$ne": "paid"}})
    reviewing = await applications_col.count_documents({"status": "reviewing"})
    approved = await applications_col.count_documents({"status": "approved"})
    rejected = await applications_col.count_documents({"status": "rejected"})
    paid_cursor = applications_col.find({"payment.status": "paid"}, {"price": 1})
    revenue = 0.0
    async for d in paid_cursor:
        revenue += float(d.get("price") or 0)
    unread_messages = await contact_col.count_documents({"is_read": False})
    return {
        "total": total,
        "today": today_count,
        "payment_pending": payment_pending,
        "reviewing": reviewing,
        "approved": approved,
        "rejected": rejected,
        "revenue": revenue,
        "unread_messages": unread_messages,
    }


@router.get("/admin/applications")
async def admin_applications(
    admin=Depends(require_admin),
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    query: dict = {}
    if status and status != "all":
        query["status"] = status
    if payment_status and payment_status != "all":
        query["payment.status"] = payment_status
    if q:
        term = q.strip()
        query["$or"] = [
            {"reference_code": {"$regex": term, "$options": "i"}},
            {"contact.full_name": {"$regex": term, "$options": "i"}},
            {"contact.email": {"$regex": term, "$options": "i"}},
            {"contact.phone": {"$regex": term, "$options": "i"}},
            {"travelers.first_name": {"$regex": term, "$options": "i"}},
            {"travelers.last_name": {"$regex": term, "$options": "i"}},
            {"travelers.passport_no": {"$regex": term, "$options": "i"}},
        ]
    total = await applications_col.count_documents(query)
    docs = (
        await applications_col.find(query)
        .sort("created_at", -1)
        .skip((page - 1) * limit)
        .limit(limit)
        .to_list(limit)
    )
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": max(1, (total + limit - 1) // limit),
        "items": serialize_doc(docs),
    }


@router.get("/admin/applications/{application_id}")
async def admin_application_detail(application_id: str, admin=Depends(require_admin)):
    doc = await applications_col.find_one({"id": application_id})
    if not doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    txs = await payments_col.find({"application_id": application_id}).sort("created_at", -1).to_list(20)
    return {"application": serialize_doc(doc), "transactions": serialize_doc(txs)}


@router.patch("/admin/applications/{application_id}")
async def admin_update_application(application_id: str, payload: StatusUpdate, admin=Depends(require_admin)):
    if payload.status not in STATUS_LABELS:
        raise HTTPException(400, "Gecersiz durum.")
    doc = await applications_col.find_one({"id": application_id})
    if not doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    now = datetime.now(timezone.utc)
    update = {"status": payload.status, "updated_at": now}
    if payload.note is not None:
        update["admin_notes"] = payload.note
    await applications_col.update_one(
        {"id": application_id},
        {
            "$set": update,
            "$push": {"status_history": {"status": payload.status, "at": now, "note": payload.note or ""}},
        },
    )
    fresh = await applications_col.find_one({"id": application_id})
    email_status = None
    to_email = (fresh.get("contact") or {}).get("email") or (fresh.get("applicant") or {}).get("email")
    if payload.notify and payload.status != doc.get("status") and to_email:
        res = await send_email(
            to_email,
            f"Basvuru durumu guncellendi - {fresh['reference_code']}",
            status_change_html(serialize_doc(fresh), STATUS_LABELS[payload.status], payload.note or ""),
            kind="status_change",
            meta={"reference_code": fresh["reference_code"], "status": payload.status},
        )
        email_status = res.get("status")
    return {"application": serialize_doc(fresh), "email_notification": email_status}


# ------------------------------------------------- approved visa document
@router.post("/admin/applications/{application_id}/visa-document")
async def admin_upload_visa_document(
    application_id: str,
    file: UploadFile = File(...),
    admin=Depends(require_admin),
):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")

    filename = file.filename or "vize.pdf"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in {"pdf", "jpg", "jpeg", "png"}:
        raise HTTPException(400, "Vize belgesi PDF, JPG veya PNG olmalidir.")
    data = await file.read()
    if not data:
        raise HTTPException(400, "Dosya bos gorunuyor.")
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(400, "Dosya boyutu en fazla 15 MB olabilir.")

    file_id = str(uuid.uuid4())
    content_type = MIME_TYPES.get(ext, file.content_type or "application/octet-stream")
    path = f"{APP_NAME}/visas/{application_id}/{file_id}.{ext}"
    try:
        result = put_object(path, data, content_type)
    except Exception as exc:
        logger.error("visa upload failed: %s", exc)
        raise HTTPException(502, "Dosya yuklenemedi. Lutfen tekrar deneyin.")

    now = datetime.now(timezone.utc)
    await uploads_col.insert_one(
        {
            "id": file_id,
            "doc_type": "visa_result",
            "storage_path": result["path"],
            "original_filename": filename,
            "content_type": content_type,
            "size": result.get("size", len(data)),
            "is_deleted": False,
            "created_at": now,
        }
    )
    visa_result = {
        "file_id": file_id,
        "filename": filename,
        "content_type": content_type,
        "size": result.get("size", len(data)),
        "uploaded_at": now,
        "sent_at": None,
        "send_status": None,
        "sent_to": None,
    }
    await applications_col.update_one(
        {"id": application_id},
        {"$set": {"visa_result": visa_result, "updated_at": now}},
    )
    fresh = await applications_col.find_one({"id": application_id})
    return {"application": serialize_doc(fresh)}


@router.delete("/admin/applications/{application_id}/visa-document")
async def admin_delete_visa_document(application_id: str, admin=Depends(require_admin)):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    vr = app_doc.get("visa_result") or {}
    if vr.get("file_id"):
        await uploads_col.update_one({"id": vr["file_id"]}, {"$set": {"is_deleted": True}})
    await applications_col.update_one(
        {"id": application_id},
        {"$set": {"visa_result": None, "updated_at": datetime.now(timezone.utc)}},
    )
    fresh = await applications_col.find_one({"id": application_id})
    return {"application": serialize_doc(fresh)}


@router.post("/admin/applications/{application_id}/send-visa")
async def admin_send_visa(
    application_id: str,
    payload: SendVisaRequest,
    request: Request,
    admin=Depends(require_admin),
):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    vr = app_doc.get("visa_result") or {}
    if not vr.get("file_id"):
        raise HTTPException(400, "Once onaylanan vize belgesini yukleyin.")
    to_email = (app_doc.get("contact") or {}).get("email") or (app_doc.get("applicant") or {}).get("email")
    if not to_email:
        raise HTTPException(400, "Basvuruda e-posta adresi bulunamadi.")

    origin = (payload.origin_url or "").rstrip("/")
    if not origin.startswith("http"):
        origin = str(request.base_url).rstrip("/")
    download_url = f"{origin}/api/files/{vr['file_id']}?download=1"

    now = datetime.now(timezone.utc)
    update = {
        "visa_result.sent_at": now,
        "visa_result.sent_to": to_email,
        "updated_at": now,
    }
    if payload.set_approved and app_doc.get("status") != "approved":
        update["status"] = "approved"

    res = await send_email(
        to_email,
        f"Vizeniz hazir - {app_doc['reference_code']}",
        visa_ready_html(serialize_doc(app_doc), download_url, payload.message or ""),
        kind="visa_delivered",
        meta={"reference_code": app_doc["reference_code"]},
    )
    update["visa_result.send_status"] = res.get("status")

    push = {}
    if update.get("status") == "approved":
        push = {
            "status_history": {
                "status": "approved",
                "at": now,
                "note": payload.message or "Vize belgesi basvuru sahibine iletildi",
            }
        }
    mongo_update = {"$set": update}
    if push:
        mongo_update["$push"] = push
    await applications_col.update_one({"id": application_id}, mongo_update)

    fresh = await applications_col.find_one({"id": application_id})
    return {
        "application": serialize_doc(fresh),
        "email_notification": res.get("status"),
        "download_url": download_url,
    }


@router.get("/admin/contact-messages")
async def admin_contact_messages(admin=Depends(require_admin), page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=100)):
    total = await contact_col.count_documents({})
    docs = (
        await contact_col.find({}).sort("created_at", -1).skip((page - 1) * limit).limit(limit).to_list(limit)
    )
    return {"total": total, "items": serialize_doc(docs)}


@router.patch("/admin/contact-messages/{message_id}/read")
async def admin_mark_read(message_id: str, admin=Depends(require_admin)):
    res = await contact_col.update_one({"id": message_id}, {"$set": {"is_read": True}})
    if res.matched_count == 0:
        raise HTTPException(404, "Mesaj bulunamadi.")
    return {"ok": True}


@router.get("/admin/emails")
async def admin_emails(admin=Depends(require_admin), limit: int = Query(50, ge=1, le=200)):
    docs = await email_outbox_col.find({}).sort("created_at", -1).limit(limit).to_list(limit)
    configured = bool((os.environ.get("RESEND_API_KEY") or "").strip())
    return {"email_configured": configured, "items": serialize_doc(docs)}


@router.post("/admin/applications/{application_id}/mark-paid")
async def admin_mark_paid(application_id: str, admin=Depends(require_admin)):
    """Havale/EFT ile odemesi hesaba gecen basvuruyu odendi olarak isaretler."""
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    if (app_doc.get("payment") or {}).get("status") == "paid":
        return {"ok": True, "already_paid": True}

    now = datetime.now(timezone.utc)
    new_status = "reviewing" if app_doc.get("status") in ("submitted", "payment_pending") else app_doc.get("status")
    await applications_col.update_one(
        {"id": application_id},
        {
            "$set": {
                "payment.status": "paid",
                "payment.method": (app_doc.get("payment") or {}).get("method") or "bank_transfer",
                "payment.paid_at": now,
                "payment.marked_by": admin.get("sub"),
                "status": new_status,
                "updated_at": now,
            },
            "$push": {
                "status_history": {
                    "status": new_status,
                    "at": now,
                    "note": "Havale/EFT odemesi admin tarafindan onaylandi",
                }
            },
        },
    )
    fresh = await applications_col.find_one({"id": application_id})
    to_email = (fresh.get("contact") or {}).get("email")
    notification = "skipped"
    if to_email:
        result = await send_email(
            to_email,
            f"Odemeniz alindi - {fresh['reference_code']}",
            payment_received_html(serialize_doc(fresh)),
            kind="payment_received",
            meta={"reference_code": fresh["reference_code"]},
        )
        notification = result.get("status", "skipped")
    return {
        "ok": True,
        "application": serialize_doc(fresh),
        "email_notification": notification,
    }


# ------------------------------------------------------- Acente bilgileri
@router.get("/admin/company")
async def admin_get_company(admin=Depends(require_admin)):
    doc = await settings_col.find_one({"key": "company_info"})
    return {**COMPANY, **((doc or {}).get("value") or {})}


@router.put("/admin/company")
async def admin_update_company(payload: CompanyInfoIn, admin=Depends(require_admin)):
    value = {k: v for k, v in payload.model_dump().items() if v not in (None, "")}
    await settings_col.update_one(
        {"key": "company_info"},
        {"$set": {"value": value, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return {**COMPANY, **value}


# ------------------------------------------------------- Banka bilgileri
@router.get("/admin/bank-transfer")
async def admin_get_bank_transfer(admin=Depends(require_admin)):
    doc = await settings_col.find_one({"key": "bank_transfer"})
    return (doc or {}).get("value") or BANK_TRANSFER


@router.put("/admin/bank-transfer")
async def admin_update_bank_transfer(payload: BankTransferIn, admin=Depends(require_admin)):
    value = payload.model_dump()
    value["steps"] = [s for s in (value.get("steps") or []) if s.strip()] or BANK_TRANSFER["steps"]
    await settings_col.update_one(
        {"key": "bank_transfer"},
        {"$set": {"value": value, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return value


# ------------------------------------------------------- WhatsApp bildirimi
def _wa_number(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return ""
    if digits.startswith("00"):
        digits = digits[2:]
    if digits.startswith("0"):
        digits = "90" + digits[1:]
    if len(digits) == 10:
        digits = "90" + digits
    return digits


@router.post("/admin/applications/{application_id}/whatsapp")
async def admin_whatsapp_link(
    application_id: str,
    payload: WhatsAppRequest,
    request: Request,
    admin=Depends(require_admin),
):
    """Musteriye WhatsApp'tan gonderilecek hazir mesaji ve wa.me linkini uretir."""
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    phone = (app_doc.get("contact") or {}).get("phone") or ""
    number = _wa_number(phone)
    if not number:
        raise HTTPException(400, "Basvuruda gecerli bir telefon numarasi bulunamadi.")

    origin = (payload.origin_url or "").rstrip("/")
    if not origin.startswith("http"):
        origin = str(request.base_url).rstrip("/")
    ref = app_doc.get("reference_code", "")
    name = (app_doc.get("contact") or {}).get("full_name", "")
    track_url = f"{origin}/takip?kod={ref}"
    vr = app_doc.get("visa_result") or {}

    if payload.message:
        message = payload.message
    elif payload.template == "visa_ready" and vr.get("file_id"):
        message = (
            f"Merhaba {name}, VizeAtlas Dubai'den yaziyoruz. "
            f"{ref} numarali basvurunuz ONAYLANDI. Vize belgenizi e-postanizdan veya "
            f"su adresten indirebilirsiniz: {origin}/api/files/{vr['file_id']}?download=1 "
            f"Iyi yolculuklar dileriz."
        )
    elif payload.template == "documents_pending":
        message = (
            f"Merhaba {name}, {ref} numarali Dubai vize basvurunuzda eksik belge bulunuyor. "
            f"Detaylar icin takip sayfaniz: {track_url}"
        )
    elif payload.template == "payment_pending":
        message = (
            f"Merhaba {name}, {ref} numarali basvurunuzun odemesi henuz tamamlanmadi. "
            f"Odemenizi su adresten tamamlayabilirsiniz: {track_url}"
        )
    else:
        message = (
            f"Merhaba {name}, {ref} numarali Dubai vize basvurunuz hakkinda bilgi vermek istiyoruz. "
            f"Takip sayfaniz: {track_url}"
        )

    url = f"https://wa.me/{number}?text={quote(message)}"
    now = datetime.now(timezone.utc)
    await notifications_col.insert_one(
        {
            "id": str(uuid.uuid4()),
            "channel": "whatsapp",
            "application_id": application_id,
            "reference_code": ref,
            "to": number,
            "template": payload.template,
            "message": message,
            "created_at": now,
            "created_by": admin.get("sub"),
        }
    )
    return {"url": url, "message": message, "phone": number}


# --------------------------------------------------------- musteri yorumlari
@router.get("/admin/testimonials")
async def admin_list_testimonials(admin=Depends(require_admin)):
    docs = await testimonials_col.find({}).sort("order", 1).to_list(200)
    summary = await settings_col.find_one({"key": "review_summary"})
    return {
        "items": serialize_doc(docs),
        "review_summary": (summary or {}).get("value") or {},
    }


@router.post("/admin/testimonials")
async def admin_create_testimonial(payload: TestimonialIn, admin=Depends(require_admin)):
    now = datetime.now(timezone.utc)
    doc = payload.model_dump()
    if not doc.get("initials"):
        parts = [p for p in doc["name"].split() if p]
        doc["initials"] = "".join(p[0] for p in parts[:2]).upper()
    doc.update({"id": str(uuid.uuid4()), "created_at": now, "updated_at": now})
    await testimonials_col.insert_one(dict(doc))
    return serialize_doc(doc)


@router.put("/admin/testimonials/{testimonial_id}")
async def admin_update_testimonial(
    testimonial_id: str, payload: TestimonialIn, admin=Depends(require_admin)
):
    update = payload.model_dump()
    update["updated_at"] = datetime.now(timezone.utc)
    res = await testimonials_col.update_one({"id": testimonial_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(404, "Yorum bulunamadi.")
    doc = await testimonials_col.find_one({"id": testimonial_id})
    return serialize_doc(doc)


@router.delete("/admin/testimonials/{testimonial_id}")
async def admin_delete_testimonial(testimonial_id: str, admin=Depends(require_admin)):
    res = await testimonials_col.delete_one({"id": testimonial_id})
    if res.deleted_count == 0:
        raise HTTPException(404, "Yorum bulunamadi.")
    return {"ok": True}


@router.put("/admin/review-summary")
async def admin_update_review_summary(payload: ReviewSummaryIn, admin=Depends(require_admin)):
    value = payload.model_dump()
    await settings_col.update_one(
        {"key": "review_summary"},
        {"$set": {"value": value, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return value


# ------------------------------------------------------------- blog yazilari
def _slugify(text: str) -> str:
    tr = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu")
    slug = text.translate(tr).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug[:120] or str(uuid.uuid4())[:8]


@router.get("/admin/articles")
async def admin_list_articles(admin=Depends(require_admin)):
    docs = await articles_col.find({}).sort("date", -1).to_list(200)
    return {"items": serialize_doc(docs)}


@router.post("/admin/articles")
async def admin_create_article(payload: ArticleIn, admin=Depends(require_admin)):
    now = datetime.now(timezone.utc)
    doc = payload.model_dump()
    doc["slug"] = _slugify(doc.get("slug") or doc["title"])
    if await articles_col.find_one({"slug": doc["slug"]}):
        doc["slug"] = f"{doc['slug']}-{str(uuid.uuid4())[:4]}"
    doc["date"] = doc.get("date") or now.strftime("%Y-%m-%d")
    doc["body"] = [b for b in (doc.get("body") or []) if b.strip()]
    doc.update({"id": str(uuid.uuid4()), "created_at": now, "updated_at": now})
    await articles_col.insert_one(dict(doc))
    return serialize_doc(doc)


@router.put("/admin/articles/{article_id}")
async def admin_update_article(article_id: str, payload: ArticleIn, admin=Depends(require_admin)):
    existing = await articles_col.find_one({"id": article_id})
    if not existing:
        raise HTTPException(404, "Yazi bulunamadi.")
    update = payload.model_dump()
    update["slug"] = _slugify(update.get("slug") or update["title"])
    clash = await articles_col.find_one({"slug": update["slug"], "id": {"$ne": article_id}})
    if clash:
        update["slug"] = f"{update['slug']}-{str(uuid.uuid4())[:4]}"
    update["body"] = [b for b in (update.get("body") or []) if b.strip()]
    update["date"] = update.get("date") or existing.get("date")
    update["updated_at"] = datetime.now(timezone.utc)
    await articles_col.update_one({"id": article_id}, {"$set": update})
    doc = await articles_col.find_one({"id": article_id})
    return serialize_doc(doc)


@router.delete("/admin/articles/{article_id}")
async def admin_delete_article(article_id: str, admin=Depends(require_admin)):
    res = await articles_col.delete_one({"id": article_id})
    if res.deleted_count == 0:
        raise HTTPException(404, "Yazi bulunamadi.")
    return {"ok": True}


@router.get("/admin/visa-types")
async def admin_visa_types(admin=Depends(require_admin)):
    docs = await visa_types_col.find({}).sort("order", 1).to_list(100)
    return serialize_doc(docs)


@router.patch("/admin/visa-types/{visa_type_id}")
async def admin_update_visa_type(visa_type_id: str, payload: dict, admin=Depends(require_admin)):
    allowed = {"price", "processing_days", "active", "popular", "description", "name"}
    update = {k: v for k, v in payload.items() if k in allowed}
    if not update:
        raise HTTPException(400, "Guncellenecek gecerli alan yok.")
    if "price" in update:
        update["price"] = float(update["price"])
    res = await visa_types_col.update_one({"id": visa_type_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(404, "Vize tipi bulunamadi.")
    doc = await visa_types_col.find_one({"id": visa_type_id})
    return serialize_doc(doc)
