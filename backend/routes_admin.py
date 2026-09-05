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
from pydantic import BaseModel, Field

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
    login_codes_col,
    orders_col,
    products_col,
)
from content import BANK_TRANSFER, COMPANY
from doc_reminders import (
    missing_documents,
    pending_drafts,
    run_draft_reminder_sweep,
    pending_applications,
    run_reminder_sweep,
    send_document_reminder,
)
from store_catalog import product_list
from fx import apply_fx_to_list, apply_fx_to_visa, get_fx, update_fx_settings
from visa_guides import build_guide, guide_index
from emailer import (
    order_delivered_html,
    payment_received_html,
    send_email,
    status_change_html,
    visa_ready_html,
)
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

# Admin girisi ortam degiskenlerinden okunur (kodda sabit sifre tutulmaz).
# ADMIN_LOGIN_EMAIL / ADMIN_LOGIN_PASSWORD tanimli degilse gelistirme
# kimlik bilgileri kullanilir (bkz. /app/memory/test_credentials.md).
ADMIN_LOGIN_EMAIL = (os.environ.get("ADMIN_LOGIN_EMAIL") or "info@dubaivizeonline.com").strip().lower()
ADMIN_LOGIN_PASSWORD = os.environ.get("ADMIN_LOGIN_PASSWORD") or ""
ADMIN_LOGIN_NAME = os.environ.get("ADMIN_LOGIN_NAME") or "Yonetici"


def create_token(email: str, remember: bool = False) -> str:
    payload = {
        "sub": email,
        "role": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(days=30 if remember else 0, hours=0 if remember else 12),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


async def require_admin(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    if not creds or not creds.credentials:
        raise HTTPException(401, "Yetkisiz erisim. Lutfen giris yapin.")
    data: dict = {}
    try:
        data = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(401, "Oturum suresi doldu. Lutfen tekrar giris yapin.") from exc
    except Exception as exc:
        raise HTTPException(401, "Gecersiz oturum.") from exc
    if data.get("role") != "admin":
        raise HTTPException(403, "Bu islem icin yetkiniz yok.")
    return data


@router.post("/admin/login")
async def admin_login(payload: AdminLogin) -> dict:
    email = (payload.email or "").strip().lower()
    if not ADMIN_LOGIN_PASSWORD:
        raise HTTPException(500, "Yonetici sifresi tanimli degil. ADMIN_LOGIN_PASSWORD ayarlanmali.")
    if email != ADMIN_LOGIN_EMAIL or payload.password != ADMIN_LOGIN_PASSWORD:
        raise HTTPException(401, "E-posta veya sifre hatali.")
    return {
        "token": create_token(email, payload.remember),
        "user": {"email": email, "name": ADMIN_LOGIN_NAME},
    }


@router.get("/admin/me")
async def admin_me(admin: dict = Depends(require_admin)) -> dict:
    return {"email": admin["sub"], "role": admin["role"]}


@router.get("/admin/stats")
async def admin_stats(admin: dict = Depends(require_admin)) -> dict:
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
    admin: dict = Depends(require_admin),
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
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
async def admin_application_detail(application_id: str, admin: dict = Depends(require_admin)) -> dict:
    doc = await applications_col.find_one({"id": application_id})
    if not doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    txs = await payments_col.find({"application_id": application_id}).sort("created_at", -1).to_list(20)
    return {"application": serialize_doc(doc), "transactions": serialize_doc(txs)}


async def _notify_status_change(fresh: dict, previous_status: str, payload: StatusUpdate):
    """Durum degistiyse musteriye bilgilendirme e-postasi (ve sonucta WhatsApp) gonderir."""
    to_email = (fresh.get("contact") or {}).get("email") or (fresh.get("applicant") or {}).get("email")
    if not (payload.notify and payload.status != previous_status and to_email):
        return None
    res = await send_email(
        to_email,
        f"Basvuru durumu guncellendi - {fresh['reference_code']}",
        status_change_html(serialize_doc(fresh), STATUS_LABELS[payload.status], payload.note or ""),
        kind="status_change",
        meta={"reference_code": fresh["reference_code"], "status": payload.status},
    )
    if payload.status in {"approved", "rejected"}:
        try:
            import whatsapp

            await whatsapp.notify_result(
                fresh, payload.status, os.environ.get("PUBLIC_BASE_URL") or "https://dubaivizeonline.com"
            )
        except Exception as exc:  # pragma: no cover
            logger.error("whatsapp notify failed: %s", exc)
    return res.get("status")


@router.patch("/admin/applications/{application_id}")
async def admin_update_application(application_id: str, payload: StatusUpdate, admin: dict = Depends(require_admin)) -> dict:
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
    email_status = await _notify_status_change(fresh, doc.get("status", ""), payload)
    return {"application": serialize_doc(fresh), "email_notification": email_status}


class TravelerFieldUpdate(BaseModel):
    """Aktarim oncesi eksik kalan yolcu alanini admin tamamlar."""

    index: int = Field(..., ge=0, le=20)
    gender: str = Field(..., pattern="^(male|female)$")


@router.patch("/admin/applications/{application_id}/traveler")
async def admin_update_traveler_field(
    application_id: str, payload: TravelerFieldUpdate, admin: dict = Depends(require_admin)
) -> dict:
    """Yolcunun cinsiyetini gunceller (pasaport OCR okuyamadiysa kullanilir)."""
    doc = await applications_col.find_one({"id": application_id})
    if not doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    travelers = doc.get("travelers") or []
    if payload.index >= len(travelers):
        raise HTTPException(400, "Yolcu bulunamadi.")
    await applications_col.update_one(
        {"id": application_id},
        {
            "$set": {
                f"travelers.{payload.index}.gender": payload.gender,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    fresh = await applications_col.find_one({"id": application_id})
    return {"application": serialize_doc(fresh)}


@router.get("/admin/ocr-report")
async def admin_ocr_report(days: int = 30, admin: dict = Depends(require_admin)) -> dict:
    """Pasaport OCR performans raporu: hiz + alan doluluk oranlari."""
    import ocr_metrics

    return await ocr_metrics.report(days=days)


# ------------------------------------------------- approved visa document
VISA_DOC_EXT = {"pdf", "jpg", "jpeg", "png"}
VISA_DOC_MAX_BYTES = 15 * 1024 * 1024


def _validate_visa_document(filename: str, data: bytes) -> str:
    """Vize belgesi uzanti/boyut dogrulamasi; gecerli uzantiyi dondurur."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in VISA_DOC_EXT:
        raise HTTPException(400, "Vize belgesi PDF, JPG veya PNG olmalidir.")
    if not data:
        raise HTTPException(400, "Dosya bos gorunuyor.")
    if len(data) > VISA_DOC_MAX_BYTES:
        raise HTTPException(400, "Dosya boyutu en fazla 15 MB olabilir.")
    return ext


def _put_visa_document(path: str, data: bytes, content_type: str) -> dict:
    result: dict = {}
    try:
        result = put_object(path, data, content_type) or {}
    except Exception as exc:
        logger.error("visa upload failed: %s", exc)
        raise HTTPException(502, "Dosya yuklenemedi. Lutfen tekrar deneyin.") from exc
    if not (result or {}).get("path"):
        raise HTTPException(502, "Dosya yuklenemedi. Lutfen tekrar deneyin.")
    return result


@router.post("/admin/applications/{application_id}/visa-document")
async def admin_upload_visa_document(
    application_id: str,
    file: UploadFile = File(...),
    admin: dict = Depends(require_admin),
) -> dict:
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")

    filename = file.filename or "vize.pdf"
    data = await file.read()
    ext = _validate_visa_document(filename, data)

    file_id = str(uuid.uuid4())
    content_type = MIME_TYPES.get(ext, file.content_type or "application/octet-stream")
    path = f"{APP_NAME}/visas/{application_id}/{file_id}.{ext}"
    result = _put_visa_document(path, data, content_type)
    size = result.get("size", len(data))

    now = datetime.now(timezone.utc)
    await uploads_col.insert_one(
        {
            "id": file_id,
            "doc_type": "visa_result",
            "storage_path": result["path"],
            "original_filename": filename,
            "content_type": content_type,
            "size": size,
            "is_deleted": False,
            "created_at": now,
        }
    )
    visa_result = {
        "file_id": file_id,
        "filename": filename,
        "content_type": content_type,
        "size": size,
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
async def admin_delete_visa_document(application_id: str, admin: dict = Depends(require_admin)) -> dict:
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


def _resolve_origin(origin_url: Optional[str], request: Optional[Request]) -> str:
    """Istemciden gelen origin degerini dogrular, gecersizse sunucu adresini kullanir."""
    origin = (origin_url or "").rstrip("/")
    if not origin.startswith("http"):
        if request is not None:
            origin = str(request.base_url).rstrip("/")
        else:
            origin = (os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")
    return origin


def _visa_send_update(app_doc: dict, to_email: str, now: datetime, payload: SendVisaRequest) -> dict:
    """Vize gonderimi sonrasi yazilacak alanlari hazirlar."""
    update = {
        "visa_result.sent_at": now,
        "visa_result.sent_to": to_email,
        "updated_at": now,
    }
    if payload.set_approved and app_doc.get("status") != "approved":
        update["status"] = "approved"
    return update


async def _load_sendable_visa(application_id: str) -> tuple[dict, dict, str]:
    """Vize belgesinin gonderilebilirligini dogrular; (basvuru, belge, e-posta) doner."""
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    visa_result = app_doc.get("visa_result") or {}
    if not visa_result.get("file_id"):
        raise HTTPException(400, "Once onaylanan vize belgesini yukleyin.")
    to_email = (app_doc.get("contact") or {}).get("email") or (
        app_doc.get("applicant") or {}
    ).get("email")
    if not to_email:
        raise HTTPException(400, "Basvuruda e-posta adresi bulunamadi.")
    return app_doc, visa_result, to_email


def _visa_send_mongo_update(update: dict, now: datetime, message: str) -> dict:
    """Set/push islemlerini birlestirir; onaya gecişde durum gecmisi eklenir."""
    mongo_update: dict = {"$set": update}
    if update.get("status") == "approved":
        mongo_update["$push"] = {
            "status_history": {
                "status": "approved",
                "at": now,
                "note": message or "Vize belgesi basvuru sahibine iletildi",
            }
        }
    return mongo_update


@router.post("/admin/applications/{application_id}/send-visa")
async def admin_send_visa(
    application_id: str,
    payload: SendVisaRequest,
    request: Request,
    admin: dict = Depends(require_admin),
) -> dict:
    app_doc, visa_result, to_email = await _load_sendable_visa(application_id)

    origin = _resolve_origin(payload.origin_url, request)
    download_url = f"{origin}/api/files/{visa_result['file_id']}?download=1"

    now = datetime.now(timezone.utc)
    update = _visa_send_update(app_doc, to_email, now, payload)

    res = await send_email(
        to_email,
        f"Vizeniz hazir - {app_doc['reference_code']}",
        visa_ready_html(serialize_doc(app_doc), download_url, payload.message or ""),
        kind="visa_delivered",
        meta={"reference_code": app_doc["reference_code"]},
    )
    update["visa_result.send_status"] = res.get("status")

    await applications_col.update_one(
        {"id": application_id}, _visa_send_mongo_update(update, now, payload.message or "")
    )

    fresh = await applications_col.find_one({"id": application_id})
    return {
        "application": serialize_doc(fresh),
        "email_notification": res.get("status"),
        "download_url": download_url,
    }


@router.get("/admin/contact-messages")
async def admin_contact_messages(admin: dict = Depends(require_admin), page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=100)) -> dict:
    total = await contact_col.count_documents({})
    docs = (
        await contact_col.find({}).sort("created_at", -1).skip((page - 1) * limit).limit(limit).to_list(limit)
    )
    return {"total": total, "items": serialize_doc(docs)}


@router.patch("/admin/contact-messages/{message_id}/read")
async def admin_mark_read(message_id: str, admin: dict = Depends(require_admin)) -> dict:
    res = await contact_col.update_one({"id": message_id}, {"$set": {"is_read": True}})
    if res.matched_count == 0:
        raise HTTPException(404, "Mesaj bulunamadi.")
    return {"ok": True}


@router.get("/admin/emails")
async def admin_emails(admin: dict = Depends(require_admin), limit: int = Query(50, ge=1, le=200)) -> dict:
    docs = await email_outbox_col.find({}).sort("created_at", -1).limit(limit).to_list(limit)
    configured = bool((os.environ.get("RESEND_API_KEY") or "").strip())
    sender = (os.environ.get("SENDER_EMAIL") or "onboarding@resend.dev").strip()
    # Resend'in test gondericisi yalnizca hesap sahibine mail atabilir. Gercek
    # musterilere gonderim icin kendi alan adi Resend'de dogrulanmalidir.
    sandbox = sender.endswith("@resend.dev")
    return {
        "email_configured": configured,
        "sender_email": sender,
        "sandbox_sender": sandbox,
        "items": serialize_doc(docs),
    }


@router.post("/admin/applications/{application_id}/mark-paid")
async def admin_mark_paid(application_id: str, admin: dict = Depends(require_admin)) -> dict:
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
    from routes_store import sync_application_order_payment

    await sync_application_order_payment(application_id, "paid")
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
async def admin_get_company(admin: dict = Depends(require_admin)) -> dict:
    doc = await settings_col.find_one({"key": "company_info"})
    return {**COMPANY, **((doc or {}).get("value") or {})}


@router.put("/admin/company")
async def admin_update_company(payload: CompanyInfoIn, admin: dict = Depends(require_admin)) -> dict:
    # Store all values including empty strings to allow overriding COMPANY placeholders
    value = {k: v for k, v in payload.model_dump().items() if v is not None}
    await settings_col.update_one(
        {"key": "company_info"},
        {"$set": {"value": value, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return {**COMPANY, **value}


# ------------------------------------------------------- Banka bilgileri
@router.get("/admin/bank-transfer")
async def admin_get_bank_transfer(admin: dict = Depends(require_admin)):
    doc = await settings_col.find_one({"key": "bank_transfer"})
    return (doc or {}).get("value") or BANK_TRANSFER


@router.put("/admin/bank-transfer")
async def admin_update_bank_transfer(payload: BankTransferIn, admin: dict = Depends(require_admin)):
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


def _build_whatsapp_message(app_doc: dict, template: str, origin: str, custom: str = "") -> str:
    """Basvuru durumuna gore musteriye gidecek hazir WhatsApp metnini uretir."""
    if custom:
        return custom

    ref = app_doc.get("reference_code", "")
    name = (app_doc.get("contact") or {}).get("full_name", "")
    track_url = f"{origin}/takip?kod={ref}"
    visa_file_id = (app_doc.get("visa_result") or {}).get("file_id")

    if template == "visa_ready" and visa_file_id:
        return (
            f"Merhaba {name}, Dubai Vize Online'den yaziyoruz. "
            f"{ref} numarali basvurunuz ONAYLANDI. Vize belgenizi e-postanizdan veya "
            f"su adresten indirebilirsiniz: {origin}/api/files/{visa_file_id}?download=1 "
            f"Iyi yolculuklar dileriz."
        )
    if template == "documents_pending":
        return (
            f"Merhaba {name}, {ref} numarali Dubai vize basvurunuzda eksik belge bulunuyor. "
            f"Detaylar icin takip sayfaniz: {track_url}"
        )
    if template == "payment_pending":
        return (
            f"Merhaba {name}, {ref} numarali basvurunuzun odemesi henuz tamamlanmadi. "
            f"Odemenizi su adresten tamamlayabilirsiniz: {track_url}"
        )
    return (
        f"Merhaba {name}, {ref} numarali Dubai vize basvurunuz hakkinda bilgi vermek istiyoruz. "
        f"Takip sayfaniz: {track_url}"
    )


@router.post("/admin/applications/{application_id}/whatsapp")
async def admin_whatsapp_link(
    application_id: str,
    payload: WhatsAppRequest,
    request: Request,
    admin: dict = Depends(require_admin),
) -> dict:
    """Musteriye WhatsApp'tan gonderilecek hazir mesaji ve wa.me linkini uretir."""
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    phone = (app_doc.get("contact") or {}).get("phone") or ""
    number = _wa_number(phone)
    if not number:
        raise HTTPException(400, "Basvuruda gecerli bir telefon numarasi bulunamadi.")

    origin = _resolve_origin(payload.origin_url, request)
    ref = app_doc.get("reference_code", "")
    message = _build_whatsapp_message(
        app_doc, payload.template or "", origin, (payload.message or "").strip()
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
async def admin_list_testimonials(admin: dict = Depends(require_admin)) -> dict:
    docs = await testimonials_col.find({}).sort("order", 1).to_list(200)
    summary = await settings_col.find_one({"key": "review_summary"})
    return {
        "items": serialize_doc(docs),
        "review_summary": (summary or {}).get("value") or {},
    }


@router.post("/admin/testimonials")
async def admin_create_testimonial(payload: TestimonialIn, admin: dict = Depends(require_admin)):
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
    testimonial_id: str, payload: TestimonialIn, admin: dict = Depends(require_admin)
):
    update = payload.model_dump()
    update["updated_at"] = datetime.now(timezone.utc)
    res = await testimonials_col.update_one({"id": testimonial_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(404, "Yorum bulunamadi.")
    doc = await testimonials_col.find_one({"id": testimonial_id})
    return serialize_doc(doc)


@router.delete("/admin/testimonials/demo")
async def admin_delete_demo_testimonials(admin: dict = Depends(require_admin)) -> dict:
    """Kurulumla gelen ornek yorumlari tek seferde temizler."""
    res = await testimonials_col.delete_many({"demo": True})
    return {"ok": True, "deleted": res.deleted_count}


@router.delete("/admin/testimonials/{testimonial_id}")
async def admin_delete_testimonial(testimonial_id: str, admin: dict = Depends(require_admin)) -> dict:
    res = await testimonials_col.delete_one({"id": testimonial_id})
    if res.deleted_count == 0:
        raise HTTPException(404, "Yorum bulunamadi.")
    return {"ok": True}


@router.put("/admin/review-summary")
async def admin_update_review_summary(payload: ReviewSummaryIn, admin: dict = Depends(require_admin)):
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
async def admin_list_articles(admin: dict = Depends(require_admin)) -> dict:
    docs = await articles_col.find({}).sort("date", -1).to_list(200)
    return {"items": serialize_doc(docs)}


@router.post("/admin/articles")
async def admin_create_article(payload: ArticleIn, admin: dict = Depends(require_admin)):
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
async def admin_update_article(article_id: str, payload: ArticleIn, admin: dict = Depends(require_admin)):
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
async def admin_delete_article(article_id: str, admin: dict = Depends(require_admin)) -> dict:
    res = await articles_col.delete_one({"id": article_id})
    if res.deleted_count == 0:
        raise HTTPException(404, "Yazi bulunamadi.")
    return {"ok": True}


@router.get("/admin/visa-types")
async def admin_visa_types(admin: dict = Depends(require_admin)):
    docs = await visa_types_col.find({}).sort("order", 1).to_list(100)
    items = await apply_fx_to_list(serialize_doc(docs))
    return items


@router.patch("/admin/visa-types/{visa_type_id}")
async def admin_update_visa_type(visa_type_id: str, payload: dict, admin: dict = Depends(require_admin)):
    allowed = {
        "price",
        "price_usd",
        "processing_days",
        "active",
        "popular",
        "description",
        "name",
        "guide",
    }
    update = {k: v for k, v in payload.items() if k in allowed}
    if not update:
        raise HTTPException(400, "Guncellenecek gecerli alan yok.")
    for key in ("price", "price_usd"):
        if key in update:
            update[key] = float(update[key])
    res = await visa_types_col.update_one({"id": visa_type_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(404, "Vize tipi bulunamadi.")
    doc = await visa_types_col.find_one({"id": visa_type_id})
    return await apply_fx_to_visa(serialize_doc(doc))


# ------------------------------------------------- eksik belge hatirlatmalari
@router.get("/admin/applications/{application_id}/missing-documents")
async def admin_missing_documents(application_id: str, admin: dict = Depends(require_admin)) -> dict:
    doc = await applications_col.find_one({"id": application_id})
    if not doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    state = doc.get("document_reminder") or {}
    return {
        "missing": missing_documents(doc),
        "reminder_count": int(state.get("count") or 0),
        "last_sent_at": serialize_doc(state.get("last_sent_at")),
    }


@router.post("/admin/applications/{application_id}/send-document-reminder")
async def admin_send_document_reminder(
    application_id: str, request: Request, payload: Optional[dict] = None, admin: dict = Depends(require_admin)
) -> dict:
    doc = await applications_col.find_one({"id": application_id})
    if not doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    missing = missing_documents(doc)
    if not missing:
        raise HTTPException(400, "Bu basvuruda eksik belge yok.")
    origin = _resolve_origin((payload or {}).get("origin_url"), request)
    result = await send_document_reminder(doc, origin, missing)
    fresh = await applications_col.find_one({"id": application_id})
    return {"result": serialize_doc(result), "application": serialize_doc(fresh)}


@router.get("/admin/document-reminders/pending")
async def admin_pending_reminders(admin: dict = Depends(require_admin)) -> dict:
    items = await pending_applications()
    return {"items": items, "total": len(items), "due": sum(1 for i in items if i["due"])}


@router.post("/admin/document-reminders/run")
async def admin_run_reminders(
    request: Request, payload: Optional[dict] = None, admin: dict = Depends(require_admin)
):
    body = payload or {}
    origin = _resolve_origin(body.get("origin_url"), request)
    summary = await run_reminder_sweep(origin, force=bool(body.get("force")))
    return summary


# --------------------------------------------------------- vize rehberi yonetimi
GUIDE_TEXT_FIELDS = ("h1", "seo_title", "seo_description")
GUIDE_LIST_FIELDS = ("intro", "who_for", "highlights", "tips", "keywords")


def _clean_guide_text_fields(payload: dict) -> dict:
    """Metin alanlarini kirpar; bos olanlari atar."""
    out = {}
    for field in GUIDE_TEXT_FIELDS:
        value = payload.get(field)
        if isinstance(value, str) and value.strip():
            out[field] = value.strip()
    return out


def _clean_guide_list_fields(payload: dict) -> dict:
    """Liste alanlarindaki bos elemanlari temizler."""
    out = {}
    for field in GUIDE_LIST_FIELDS:
        value = payload.get(field)
        if not isinstance(value, list):
            continue
        items = [str(v).strip() for v in value if str(v).strip()]
        if items:
            out[field] = items
    return out


def _clean_guide_faqs(payload: dict) -> dict:
    """Soru-cevap listesini normalize eder; eksik kayitlari atar."""
    faqs = payload.get("faqs")
    if not isinstance(faqs, list):
        return {}
    cleaned = []
    for faq in faqs:
        if not isinstance(faq, dict):
            continue
        question = str(faq.get("q", "")).strip()
        answer = str(faq.get("a", "")).strip()
        if question and answer:
            cleaned.append({"q": question, "a": answer})
    return {"faqs": cleaned} if cleaned else {}


def _clean_guide_payload(payload: dict) -> dict:
    """Admin panelinden gelen rehber override verisini normalize eder."""
    data = {
        **_clean_guide_text_fields(payload),
        **_clean_guide_list_fields(payload),
        **_clean_guide_faqs(payload),
    }
    if not data:
        raise HTTPException(400, "Kaydedilecek gecerli rehber alani yok.")
    return data


@router.get("/admin/visa-guides")
async def admin_list_visa_guides(admin: dict = Depends(require_admin)) -> dict:
    docs = await visa_types_col.find({}).to_list(100)
    overrides = {d.get("slug"): bool(d.get("guide")) for d in docs}
    items = []
    for item in guide_index():
        items.append({**item, "has_override": overrides.get(item["slug"], False)})
    return {"items": items}


@router.get("/admin/visa-guides/{slug}")
async def admin_get_visa_guide(slug: str, admin: dict = Depends(require_admin)) -> dict:
    doc = await visa_types_col.find_one({"slug": slug})
    visa_override = serialize_doc(doc) if doc else None
    guide_override = (visa_override or {}).pop("guide", None) if visa_override else None
    effective = build_guide(slug, visa_override=visa_override, guide_override=guide_override)
    if not effective:
        raise HTTPException(404, "Vize rehberi bulunamadi.")
    defaults = build_guide(slug)
    return {
        "slug": slug,
        "effective": effective,
        "defaults": defaults,
        "override": guide_override or {},
        "has_override": bool(guide_override),
    }


@router.put("/admin/visa-guides/{slug}")
async def admin_update_visa_guide(slug: str, payload: dict, admin: dict = Depends(require_admin)):
    if not build_guide(slug):
        raise HTTPException(404, "Vize rehberi bulunamadi.")
    data = _clean_guide_payload(payload)
    res = await visa_types_col.update_one(
        {"slug": slug},
        {"$set": {"guide": data, "guide_updated_at": datetime.now(timezone.utc)}},
    )
    if res.matched_count == 0:
        raise HTTPException(404, "Vize tipi bulunamadi.")
    return await admin_get_visa_guide(slug, admin=admin)


@router.delete("/admin/visa-guides/{slug}")
async def admin_reset_visa_guide(slug: str, admin: dict = Depends(require_admin)):
    if not build_guide(slug):
        raise HTTPException(404, "Vize rehberi bulunamadi.")
    await visa_types_col.update_one(
        {"slug": slug}, {"$unset": {"guide": "", "guide_updated_at": ""}}
    )
    return await admin_get_visa_guide(slug, admin=admin)


# ----------------------------------------------------------------- kur (USD/TRY)
@router.get("/admin/fx")
async def admin_get_fx(refresh: bool = False, admin: dict = Depends(require_admin)):
    return await get_fx(force_refresh=refresh)


@router.put("/admin/fx")
async def admin_update_fx(payload: dict, admin: dict = Depends(require_admin)):
    manual = payload.get("manual_rate")
    margin = payload.get("margin_pct")
    try:
        return await update_fx_settings(manual_rate=manual, margin_pct=margin)
    except (TypeError, ValueError):
        raise HTTPException(400, "Gecersiz kur veya marj degeri.")


@router.get("/admin/login-codes")
async def admin_login_codes(email: Optional[str] = None, admin: dict = Depends(require_admin)) -> dict:
    """E-posta gonderimi yapilandirilmadan once destek amacli giris kodu goruntuleme."""
    query = {"email": email.strip().lower()} if email else {}
    docs = await login_codes_col.find(query).sort("created_at", -1).limit(20).to_list(20)
    return {
        "items": [
            {
                "email": d.get("email"),
                "code": d.get("code_plain"),
                "expires_at": serialize_doc(d.get("expires_at")),
                "attempts": d.get("attempts", 0),
            }
            for d in docs
        ]
    }


# --------------------------------------------------- taslak (sepeti kurtarma)
@router.get("/admin/draft-reminders/pending")
async def admin_pending_draft_reminders(admin: dict = Depends(require_admin)) -> dict:
    items = await pending_drafts()
    return {"items": items, "total": len(items), "due": sum(1 for i in items if i["due"])}


@router.post("/admin/draft-reminders/run")
async def admin_run_draft_reminders(
    request: Request, payload: Optional[dict] = None, admin: dict = Depends(require_admin)
):
    body = payload or {}
    origin = _resolve_origin(body.get("origin_url"), request)
    return await run_draft_reminder_sweep(origin, force=bool(body.get("force")))


# ------------------------------------------------ magaza: urunler ve siparisler
@router.get("/admin/products")
async def admin_products(admin: dict = Depends(require_admin)) -> dict:
    items = await product_list(include_inactive=True)
    return {"items": items}


@router.patch("/admin/products/{product_id}")
async def admin_update_product(product_id: str, payload: dict, admin: dict = Depends(require_admin)):
    allowed = {"price_usd", "price_try", "cost_try", "name", "summary", "active", "popular", "data_amount", "coverage", "validity_days"}
    update = {k: v for k, v in payload.items() if k in allowed}
    if not update:
        raise HTTPException(400, "Guncellenecek gecerli alan yok.")
    if "price_usd" in update:
        update["price_usd"] = float(update["price_usd"])
    if "price_try" in update:
        update["price_try"] = float(update["price_try"])
    if "cost_try" in update:
        update["cost_try"] = float(update["cost_try"])
    if "validity_days" in update:
        update["validity_days"] = int(update["validity_days"])
    res = await products_col.update_one({"id": product_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(404, "Urun bulunamadi.")
    items = await product_list(include_inactive=True)
    return next((i for i in items if i["id"] == product_id), None)


@router.get("/admin/orders")
async def admin_orders(status: Optional[str] = None, admin: dict = Depends(require_admin)) -> dict:
    query = {"status": status} if status else {}
    docs = await orders_col.find(query).sort("created_at", -1).to_list(200)
    return {"items": serialize_doc(docs), "total": len(docs)}


@router.get("/admin/orders/{order_id}")
async def admin_order_detail(order_id: str, admin: dict = Depends(require_admin)):
    doc = await orders_col.find_one({"id": order_id})
    if not doc:
        raise HTTPException(404, "Siparis bulunamadi.")
    return serialize_doc(doc)


@router.patch("/admin/orders/{order_id}")
async def admin_update_order(order_id: str, payload: dict, admin: dict = Depends(require_admin)):
    doc = await orders_col.find_one({"id": order_id})
    if not doc:
        raise HTTPException(404, "Siparis bulunamadi.")
    update = {"updated_at": datetime.now(timezone.utc)}
    if payload.get("status") in {"pending", "processing", "fulfilled", "cancelled"}:
        update["status"] = payload["status"]
    if payload.get("payment_status") in {"pending", "awaiting_transfer", "paid", "refunded"}:
        update["payment.status"] = payload["payment_status"]
        if payload["payment_status"] == "paid":
            update["payment.paid_at"] = datetime.now(timezone.utc)
            update.setdefault("status", "processing")
    if payload.get("admin_note") is not None:
        update["admin_note"] = str(payload["admin_note"])[:1000]
    if len(update) == 1:
        raise HTTPException(400, "Guncellenecek gecerli alan yok.")
    await orders_col.update_one({"id": order_id}, {"$set": update})
    fresh = await orders_col.find_one({"id": order_id})
    if update.get("payment.status") == "paid":
        from insurance_tasks import queue_policy_tasks

        await queue_policy_tasks(fresh)
    return serialize_doc(fresh)


@router.get("/admin/insurance-tasks")
async def admin_insurance_tasks(status: str = "", admin: dict = Depends(require_admin)) -> dict:
    from db import insurance_tasks_col

    query = {"status": status} if status in {"pending", "issued"} else {}
    docs = await insurance_tasks_col.find(query).sort("created_at", -1).limit(200).to_list(200)
    return {"items": serialize_doc(docs)}


@router.post("/admin/insurance-tasks/{task_id}/issue")
async def admin_issue_policy(task_id: str, payload: dict, admin: dict = Depends(require_admin)) -> dict:
    from insurance_tasks import issue_policy

    policy_file_id = str(payload.get("policy_file_id") or "").strip()
    if not policy_file_id:
        raise HTTPException(400, "Police PDF dosyasi yuklemelisiniz.")
    origin = _resolve_origin(payload.get("origin_url"), None)
    result = await issue_policy(
        task_id, policy_file_id, origin, str(payload.get("message") or "")[:1000]
    )
    if not result.get("ok"):
        raise HTTPException(404, "Police gorevi bulunamadi.")
    return result


@router.get("/admin/profit-monthly")
async def admin_profit_monthly(months: int = 12, admin: dict = Depends(require_admin)) -> dict:
    from insurance_tasks import monthly_profit

    return await monthly_profit(months)


@router.get("/admin/insurance-report")
async def admin_insurance_report(admin: dict = Depends(require_admin)) -> dict:
    from insurance_tasks import profit_report

    return await profit_report()


@router.post("/admin/orders/{order_id}/deliver")
async def admin_deliver_order(order_id: str, payload: dict, admin: dict = Depends(require_admin)) -> dict:
    """eSIM QR kodu / police PDF'ini musteriye e-posta ile gonderir."""
    doc = await orders_col.find_one({"id": order_id})
    if not doc:
        raise HTTPException(404, "Siparis bulunamadi.")

    esim_file_id = payload.get("esim_file_id")
    policy_file_id = payload.get("policy_file_id")
    message = str(payload.get("message") or "")[:1000]
    if not esim_file_id and not policy_file_id:
        raise HTTPException(400, "En az bir belge (eSIM QR veya police) yuklemelisiniz.")

    origin = _resolve_origin(payload.get("origin_url"), None)
    links = []
    if esim_file_id:
        links.append({"label": "eSIM QR kodunuz", "url": f"{origin}/api/files/{esim_file_id}"})
    if policy_file_id:
        links.append({"label": "Sigorta policeniz (PDF)", "url": f"{origin}/api/files/{policy_file_id}"})

    now = datetime.now(timezone.utc)
    await orders_col.update_one(
        {"id": order_id},
        {
            "$set": {
                "delivery": {
                    "esim_file_id": esim_file_id,
                    "policy_file_id": policy_file_id,
                    "message": message,
                    "sent_at": now,
                },
                "status": "fulfilled",
                "updated_at": now,
            }
        },
    )
    fresh = await orders_col.find_one({"id": order_id})
    to_email = (fresh.get("contact") or {}).get("email")
    result = {"status": "skipped"}
    if to_email:
        result = await send_email(
            to_email,
            f"Siparisiniz hazir - {fresh['reference_code']}",
            order_delivered_html(serialize_doc(fresh), links, message),
            kind="order_delivered",
            meta={"order_id": order_id, "reference_code": fresh["reference_code"]},
        )
    return {"order": serialize_doc(fresh), "email": result}

