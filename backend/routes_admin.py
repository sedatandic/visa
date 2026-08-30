import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from content import STATUS_LABELS
from db import (
    applications_col,
    contact_col,
    email_outbox_col,
    payments_col,
    serialize_doc,
    visa_types_col,
)
from emailer import send_email, status_change_html
from models import AdminLogin, StatusUpdate

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
            {"applicant.first_name": {"$regex": term, "$options": "i"}},
            {"applicant.last_name": {"$regex": term, "$options": "i"}},
            {"applicant.email": {"$regex": term, "$options": "i"}},
            {"applicant.passport_no": {"$regex": term, "$options": "i"}},
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
    if payload.notify and payload.status != doc.get("status"):
        res = await send_email(
            fresh["applicant"]["email"],
            f"Basvuru durumu guncellendi - {fresh['reference_code']}",
            status_change_html(serialize_doc(fresh), STATUS_LABELS[payload.status], payload.note or ""),
            kind="status_change",
            meta={"reference_code": fresh["reference_code"], "status": payload.status},
        )
        email_status = res.get("status")
    return {"application": serialize_doc(fresh), "email_notification": email_status}


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
