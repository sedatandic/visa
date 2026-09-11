"""Musteri hesabi: e-posta ile giris, onceki basvurular ve taslak yonetimi.

Giris yollari:
1) E-postaya gonderilen 6 haneli tek kullanimlik kod (tek gecerli giris yolu)
2) Taslak devam kodu (kaydedilen yarim basvuruya donmek icin)

Guvenlik notu: e-posta + soyad ile giris kaldirildi (soyad tahmin edilebilir
oldugu icin hesap devralmaya aciktir). Kod yalnizca hash'lenmis saklanir.
"""

import hashlib
import logging
import os
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from db import (
    applications_col,
    drafts_col,
    login_codes_col,
    saved_travelers_col,
    serialize_doc,
)
from doc_reminders import missing_documents
from emailer import draft_saved_html, login_code_html, send_email, subject_with_ref
from rate_limit import allow as rate_allow
from rate_limit import check as rate_check
from rate_limit import client_ip, code_request_window
from store_catalog import customer_order_view

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGO = "HS256"
CODE_TTL_MINUTES = 15
MAX_CODE_ATTEMPTS = 5
CODE_COOLDOWN_SECONDS = 60
CODE_MAX_PER_HOUR = 5
CODE_MAX_PER_IP_HOUR = 15
VERIFY_MAX_PER_IP_HOUR = 30
SESSION_DAYS = 30
RESUME_CODE_LENGTH = 8


# ------------------------------------------------------------------ yardimcilar
def _norm_email(email: str) -> str:
    return (email or "").strip().lower()


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _create_session_token(email: str) -> str:
    payload = {
        "sub": email,
        "role": "customer",
        "exp": datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


async def require_customer(creds: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    if not creds:
        raise HTTPException(401, "Oturum bulunamadi. Lutfen tekrar giris yapin.")
    payload: dict = {}
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.PyJWTError as exc:
        raise HTTPException(401, "Oturum suresi doldu. Lutfen tekrar giris yapin.") from exc
    if payload.get("role") != "customer":
        raise HTTPException(403, "Bu islem icin yetkiniz yok.")
    return payload.get("sub", "")


def _application_summary(doc: dict) -> dict:
    d = serialize_doc(doc) or {}
    travelers = d.get("travelers") or []
    return {
        "id": d.get("id"),
        "reference_code": d.get("reference_code"),
        "status": d.get("status"),
        "payment": d.get("payment") or {},
        "price": d.get("price"),
        "currency": d.get("currency", "TRY"),
        "created_at": d.get("created_at"),
        "updated_at": d.get("updated_at"),
        "traveler_count": len(travelers),
        "traveler_names": [
            f"{t.get('first_name', '')} {t.get('last_name', '')}".strip() for t in travelers
        ],
        "visa_names": sorted({t.get("visa_type_name", "") for t in travelers if t.get("visa_type_name")}),
        "last_name": (travelers[0].get("last_name") if travelers else ""),
        "approved_visa_file_id": d.get("approved_visa_file_id"),
        "missing_documents": missing_documents(doc),
    }


async def _applications_for_email(email: str) -> list:
    cursor = applications_col.find(
        {"contact.email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}}
    ).sort("created_at", -1)
    return [_application_summary(doc) async for doc in cursor]


def _draft_summary(doc: dict, include_data: bool = False) -> dict:
    d = serialize_doc(doc) or {}
    out = {
        "id": d.get("id"),
        "email": d.get("email"),
        "title": d.get("title") or "Kaydedilen basvuru",
        "step": d.get("step", 0),
        "traveler_count": d.get("traveler_count", 0),
        "resume_code": d.get("resume_code"),
        "created_at": d.get("created_at"),
        "updated_at": d.get("updated_at"),
    }
    if include_data:
        out["data"] = d.get("data") or {}
    return out


# ------------------------------------------------------------------- modeller
class EmailIn(BaseModel):
    email: EmailStr


class CodeVerifyIn(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=8)


class DraftIn(BaseModel):
    email: EmailStr
    data: dict
    title: Optional[str] = None
    step: int = 0
    traveler_count: int = 1
    draft_id: Optional[str] = None
    resume_code: Optional[str] = None
    # True yalnizca kullanicinin acik "kaydet" istegi icin; otomatik kayitlarda posta yok.
    notify: bool = False


# ---------------------------------------------------------------------- giris
@router.post("/account/request-code")
async def request_login_code(payload: EmailIn, request: Request) -> dict:
    """E-postaya 6 haneli giris kodu gonderir."""
    email = _norm_email(payload.email)
    ip = client_ip(request)
    rate_check(
        f"account-code-ip:{ip}",
        CODE_MAX_PER_IP_HOUR,
        3600,
        "Cok fazla kod talebi. Lutfen bir saat sonra tekrar deneyin.",
    )
    now = datetime.now(timezone.utc)
    existing = await login_codes_col.find_one({"email": email})
    window_start, count = code_request_window(
        existing, now, CODE_COOLDOWN_SECONDS, CODE_MAX_PER_HOUR
    )
    code = f"{secrets.randbelow(900000) + 100000}"
    await login_codes_col.update_one(
        {"email": email},
        {
            "$set": {
                "email": email,
                # Kod yalnizca hash olarak saklanir (duz metin saklanmaz).
                "code_hash": _hash(code),
                "expires_at": now + timedelta(minutes=CODE_TTL_MINUTES),
                "attempts": 0,
                "created_at": now,
                "window_start": window_start,
                "request_count": count + 1,
                "ip": ip,
            },
            "$unset": {"code_plain": ""},
        },
        upsert=True,
    )
    origin = (request.headers.get("origin") or os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")
    result = await send_email(
        email,
        "Dubai Vize Hattı giris kodunuz",
        login_code_html(code, CODE_TTL_MINUTES, f"{origin}/hesabim" if origin else ""),
        kind="login_code",
        meta={"email": email},
    )
    return {
        "sent": result.get("status") == "sent",
        "email_status": result.get("status"),
        "expires_in_minutes": CODE_TTL_MINUTES,
        "cooldown_seconds": CODE_COOLDOWN_SECONDS,
    }


@router.post("/account/verify-code")
async def verify_login_code(payload: CodeVerifyIn, request: Request) -> dict:
    email = _norm_email(payload.email)
    rate_check(
        f"account-verify-ip:{client_ip(request)}",
        VERIFY_MAX_PER_IP_HOUR,
        3600,
        "Cok fazla deneme. Lutfen bir saat sonra tekrar deneyin.",
    )
    doc = await login_codes_col.find_one({"email": email})
    if not doc:
        raise HTTPException(400, "Once giris kodu talep etmelisiniz.")
    expires = doc.get("expires_at")
    if isinstance(expires, datetime):
        expires_at = expires if expires.tzinfo else expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise HTTPException(400, "Kodun suresi dolmus. Yeni kod talep edin.")
    if int(doc.get("attempts") or 0) >= MAX_CODE_ATTEMPTS:
        raise HTTPException(429, "Cok fazla hatali deneme. Yeni kod talep edin.")
    if _hash(payload.code.strip()) != doc.get("code_hash"):
        await login_codes_col.update_one({"email": email}, {"$inc": {"attempts": 1}})
        raise HTTPException(400, "Kod hatali. Lutfen tekrar deneyin.")

    await login_codes_col.delete_one({"email": email})
    return {"token": _create_session_token(email), "email": email}


# ------------------------------------------------------------- hesap ozetleri
@router.get("/account/me")
async def account_overview(email: str = Depends(require_customer)) -> dict:
    applications = await _applications_for_email(email)
    drafts = [
        _draft_summary(d)
        async for d in drafts_col.find({"email": email}).sort("updated_at", -1)
    ]
    return {"email": email, "applications": applications, "drafts": drafts}


@router.get("/account/applications/{application_id}")
async def account_application_detail(application_id: str, email: str = Depends(require_customer)):
    doc = await applications_col.find_one({"id": application_id})
    if not doc or _norm_email((doc.get("contact") or {}).get("email", "")) != email:
        raise HTTPException(404, "Basvuru bulunamadi.")
    view = serialize_doc(doc)
    view.pop("admin_notes", None)
    view["missing_documents"] = missing_documents(doc)
    return view


@router.get("/account/orders")
async def account_orders(email: str = Depends(require_customer)) -> dict:
    """eSIM / sigorta siparisleri."""
    from db import orders_col

    cursor = orders_col.find(
        {"contact.email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}}
    ).sort("created_at", -1)
    items = [customer_order_view(serialize_doc(doc)) async for doc in cursor]
    return {"items": items}


async def _visa_documents(email_pattern: dict) -> list:
    """Onaylanan vize PDF'leri."""
    import file_access

    items = []
    async for doc in applications_col.find({"contact.email": email_pattern}).sort("created_at", -1):
        visa = doc.get("visa_result") or {}
        if not visa.get("file_id"):
            continue
        travelers = doc.get("travelers") or []
        items.append(
            {
                "kind": "visa",
                "id": f"visa-{doc.get('id')}",
                "title": "Onaylanan vize belgesi",
                "reference": doc.get("reference_code", ""),
                "people": [
                    f"{t.get('first_name', '')} {t.get('last_name', '')}".strip() for t in travelers
                ],
                "detail": visa.get("filename") or "vize.pdf",
                "issued_at": visa.get("sent_at") or visa.get("uploaded_at"),
                "download_url": file_access.file_path(
                    visa["file_id"], file_access.TTL_EMAIL, download=True
                ),
            }
        )
    return items


async def _policy_documents(email_pattern: dict) -> list:
    """Kesilen sigorta policeleri."""
    import file_access
    from db import insurance_tasks_col

    items = []
    cursor = insurance_tasks_col.find({"status": "issued", "customer.email": email_pattern}).sort(
        "issued_at", -1
    )
    async for doc in cursor:
        items.append(
            {
                "kind": "policy",
                "id": f"policy-{doc.get('id')}",
                "title": doc.get("plan_name") or "Seyahat Sağlık Sigortası",
                "reference": doc.get("order_reference", ""),
                "people": [p.get("full_name", "") for p in doc.get("insured") or []],
                "detail": f"{doc.get('starts_on') or '-'} → {doc.get('ends_on') or '-'}",
                "issued_at": doc.get("issued_at"),
                "download_url": file_access.file_path(
                    doc.get("policy_file_id") or "", file_access.TTL_EMAIL, download=True
                ),
            }
        )
    return items


@router.get("/account/documents")
async def account_documents(email: str = Depends(require_customer)) -> dict:
    """Musteriye ait belgeler: onaylanan vize PDF'leri + kesilen sigorta policeleri."""
    pattern = {"$regex": f"^{re.escape(email)}$", "$options": "i"}
    return {"items": await _visa_documents(pattern) + await _policy_documents(pattern)}


@router.post("/account/documents/{document_id}/resend")
async def account_document_resend(
    document_id: str, request: Request, email: str = Depends(require_customer)
) -> dict:
    """Vize belgesini veya police PDF'ini musterinin kendi e-postasina tekrar gonderir."""
    import file_access
    import visa_file_number
    from application_docs import visa_pdf_attachment
    from db import insurance_tasks_col
    from emailer import send_email, subject_with_ref, visa_ready_html
    from insurance_delivery import policy_html

    rate_check(
        f"doc-resend:{email.lower()}",
        6,
        3600,
        "Saatte en fazla 6 belge gönderimi yapılabilir. Lütfen daha sonra deneyin.",
    )
    pattern = {"$regex": f"^{re.escape(email)}$", "$options": "i"}
    kind, _, raw_id = document_id.partition("-")
    origin = str(request.base_url).rstrip("/")

    if kind == "visa":
        app_doc = await applications_col.find_one({"id": raw_id, "contact.email": pattern})
        visa = (app_doc or {}).get("visa_result") or {}
        if not app_doc or not visa.get("file_id"):
            raise HTTPException(404, "Belge bulunamadi.")
        link = file_access.file_url(origin, visa["file_id"], file_access.TTL_EMAIL, download=True)
        verify_link = (
            visa_file_number.verify_url(origin, app_doc["id"]) if visa.get("file_number") else ""
        )
        attachments = await visa_pdf_attachment(visa["file_id"], app_doc.get("reference_code", ""))
        result = await send_email(
            email,
            subject_with_ref(app_doc.get("reference_code", ""), "vize belgeniz"),
            visa_ready_html(serialize_doc(app_doc), link, "", bool(attachments), verify_link),
            kind="visa_delivered",
            meta={"reference_code": app_doc.get("reference_code", ""), "resend": True},
            attachments=attachments,
        )
    elif kind == "policy":
        task = await insurance_tasks_col.find_one(
            {"id": raw_id, "status": "issued", "customer.email": pattern}
        )
        if not task or not task.get("policy_file_id"):
            raise HTTPException(404, "Belge bulunamadi.")
        link = file_access.file_url(origin, task["policy_file_id"], file_access.TTL_EMAIL)
        result = await send_email(
            email,
            f"Sigorta poliçeniz - {task.get('order_reference', '')}",
            policy_html(task, link),
            kind="insurance_policy_sent",
            meta={"task_id": task["id"], "resend": True},
        )
    else:
        raise HTTPException(404, "Belge bulunamadi.")

    return {"ok": result.get("status") == "sent", "email": email, "status": result.get("status")}


@router.get("/account/drafts/{draft_id}")
async def account_draft_detail(draft_id: str, email: str = Depends(require_customer)):
    doc = await drafts_col.find_one({"id": draft_id, "email": email})
    if not doc:
        raise HTTPException(404, "Taslak bulunamadi.")
    return _draft_summary(doc, include_data=True)


@router.delete("/account/drafts/{draft_id}")
async def account_delete_draft(draft_id: str, email: str = Depends(require_customer)) -> dict:
    res = await drafts_col.delete_one({"id": draft_id, "email": email})
    if res.deleted_count == 0:
        raise HTTPException(404, "Taslak bulunamadi.")
    return {"deleted": True}


# ------------------------------------------------------------------- taslaklar
@router.post("/drafts")
async def save_draft(payload: DraftIn, request: Request) -> dict:
    """Yarim kalan basvuruyu kaydeder; devam kodu ile geri donulebilir."""
    email = _norm_email(payload.email)
    rate_check(
        f"draft-save:{client_ip(request)}",
        120,
        3600,
        "Cok fazla taslak kaydi denemesi. Lutfen birkac dakika sonra tekrar deneyin.",
    )
    now = datetime.now(timezone.utc)

    existing = None
    if payload.draft_id:
        existing = await drafts_col.find_one({"id": payload.draft_id, "email": email})
        if existing and payload.resume_code and existing.get("resume_code") != payload.resume_code.strip().upper():
            raise HTTPException(403, "Devam kodu hatali.")

    doc = existing or {
        "id": str(uuid.uuid4()),
        "email": email,
        "resume_code": secrets.token_hex(RESUME_CODE_LENGTH // 2).upper(),
        "created_at": now,
    }
    doc.update(
        {
            "data": payload.data,
            "title": payload.title or "Kaydedilen basvuru",
            "step": payload.step,
            "traveler_count": payload.traveler_count,
            "updated_at": now,
        }
    )
    doc.pop("_id", None)
    await drafts_col.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)

    origin = (request.headers.get("origin") or os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")
    resume_url = (
        f"{origin}/basvuru?taslak={doc['id']}&kod={doc['resume_code']}" if origin else ""
    )
    # E-posta YALNIZCA kullanici "Kaydet, sonra devam et" dedigi zaman gider.
    # Otomatik/sessiz kayitlar (5 sn'de bir) hicbir posta tetiklemez.
    email_result: dict = {"status": "skipped"}
    if payload.notify and rate_allow(f"draft-mail:{email}", 3, 3600):
        email_result = await send_email(
            email,
            subject_with_ref(doc.get("resume_code", ""), "kaydedildi - kaldığınız yerden devam edin"),
            draft_saved_html(doc, resume_url),
            kind="draft_saved",
            meta={"draft_id": doc["id"]},
        )
    return {
        "draft_id": doc["id"],
        "resume_code": doc["resume_code"],
        "resume_url": resume_url,
        "email_status": email_result.get("status"),
    }


@router.get("/drafts/{draft_id}")
async def get_draft(draft_id: str, code: str):
    """Devam kodu ile taslaga erisim (giris yapmaya gerek yok)."""
    doc = await drafts_col.find_one({"id": draft_id})
    if not doc or doc.get("resume_code") != (code or "").strip().upper():
        raise HTTPException(404, "Taslak bulunamadi veya devam kodu hatali.")
    return _draft_summary(doc, include_data=True)


# ------------------------------------------------- aile profili (kayitli yolcular)
TRAVELER_FIELDS = (
    "first_name",
    "last_name",
    "birth_date",
    "gender",
    "national_id",
    "passport_no",
    "passport_expiry",
    "applicant_type",
)


class SavedTravelerIn(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=60)
    last_name: str = Field(..., min_length=2, max_length=60)
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    national_id: Optional[str] = None
    passport_no: Optional[str] = None
    passport_expiry: Optional[str] = None
    applicant_type: str = "adult"
    id: Optional[str] = None


def _traveler_key(data: dict) -> str:
    """Ayni yolcuyu tekrar kaydetmemek icin benzersiz anahtar."""
    passport = (data.get("passport_no") or "").strip().upper()
    if passport:
        return f"p:{passport}"
    return (
        "n:"
        + (data.get("first_name") or "").strip().lower()
        + "|"
        + (data.get("last_name") or "").strip().lower()
        + "|"
        + (data.get("birth_date") or "")
    )


def _saved_traveler_view(doc: dict) -> dict:
    d = serialize_doc(doc) or {}
    return {
        "id": d.get("id"),
        **{f: d.get(f) for f in TRAVELER_FIELDS},
        "created_at": d.get("created_at"),
        "updated_at": d.get("updated_at"),
    }


async def upsert_saved_travelers(email: str, travelers: list) -> int:
    """Basvuru olusturuldugunda yolcularin profilini kaydeder/gunceller."""
    email = _norm_email(email)
    if not email:
        return 0
    saved = 0
    now = datetime.now(timezone.utc)
    for traveler in travelers or []:
        data = {f: traveler.get(f) for f in TRAVELER_FIELDS}
        if not data.get("first_name") or not data.get("last_name"):
            continue
        key = _traveler_key(data)
        await saved_travelers_col.update_one(
            {"email": email, "match_key": key},
            {
                "$set": {**data, "email": email, "match_key": key, "updated_at": now},
                "$setOnInsert": {"id": str(uuid.uuid4()), "created_at": now},
            },
            upsert=True,
        )
        saved += 1
    return saved


@router.get("/account/travelers")
async def list_saved_travelers(email: str = Depends(require_customer)) -> dict:
    docs = await saved_travelers_col.find({"email": email}).sort("updated_at", -1).to_list(50)
    return {"items": [_saved_traveler_view(d) for d in docs]}


@router.post("/account/travelers")
async def save_traveler(payload: SavedTravelerIn, email: str = Depends(require_customer)):
    data = {f: getattr(payload, f, None) for f in TRAVELER_FIELDS}
    now = datetime.now(timezone.utc)
    if payload.id:
        res = await saved_travelers_col.update_one(
            {"id": payload.id, "email": email},
            {"$set": {**data, "match_key": _traveler_key(data), "updated_at": now}},
        )
        if res.matched_count == 0:
            raise HTTPException(404, "Kayitli yolcu bulunamadi.")
        doc = await saved_travelers_col.find_one({"id": payload.id, "email": email})
        return _saved_traveler_view(doc)

    key = _traveler_key(data)
    await saved_travelers_col.update_one(
        {"email": email, "match_key": key},
        {
            "$set": {**data, "email": email, "match_key": key, "updated_at": now},
            "$setOnInsert": {"id": str(uuid.uuid4()), "created_at": now},
        },
        upsert=True,
    )
    doc = await saved_travelers_col.find_one({"email": email, "match_key": key})
    return _saved_traveler_view(doc)


@router.delete("/account/travelers/{traveler_id}")
async def delete_saved_traveler(traveler_id: str, email: str = Depends(require_customer)) -> dict:
    res = await saved_travelers_col.delete_one({"id": traveler_id, "email": email})
    if res.deleted_count == 0:
        raise HTTPException(404, "Kayitli yolcu bulunamadi.")
    return {"deleted": True}
