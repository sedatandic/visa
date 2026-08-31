"""Musteri hesabi: e-posta ile giris, onceki basvurular ve taslak yonetimi.

Giris yollari:
1) E-postaya gonderilen 6 haneli kod (Resend yapilandirildiginda calisir)
2) E-posta + soyad dogrulamasi (mevcut basvurusu olanlar icin, her zaman calisir)
3) Taslak devam kodu (kaydedilen yarim basvuruya donmek icin)
"""

import hashlib
import logging
import os
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
from emailer import draft_saved_html, login_code_html, send_email

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer(auto_error=False)

JWT_SECRET = os.environ.get("JWT_SECRET", "dv-dev-secret")
JWT_ALGO = "HS256"
CODE_TTL_MINUTES = 15
MAX_CODE_ATTEMPTS = 5
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
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.PyJWTError:
        raise HTTPException(401, "Oturum suresi doldu. Lutfen tekrar giris yapin.")
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
        {"contact.email": {"$regex": f"^{email}$", "$options": "i"}}
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


class LastNameLoginIn(BaseModel):
    email: EmailStr
    last_name: str = Field(..., min_length=2, max_length=80)


class DraftIn(BaseModel):
    email: EmailStr
    data: dict
    title: Optional[str] = None
    step: int = 0
    traveler_count: int = 1
    draft_id: Optional[str] = None
    resume_code: Optional[str] = None


# ---------------------------------------------------------------------- giris
@router.post("/account/request-code")
async def request_login_code(payload: EmailIn, request: Request):
    """E-postaya 6 haneli giris kodu gonderir."""
    email = _norm_email(payload.email)
    code = f"{secrets.randbelow(900000) + 100000}"
    now = datetime.now(timezone.utc)
    await login_codes_col.update_one(
        {"email": email},
        {
            "$set": {
                "email": email,
                "code_hash": _hash(code),
                # Resend yapilandirilmadan once destek ekibinin kodu iletebilmesi
                # icin admin panelinde gorunur (yalnizca admin erisebilir).
                "code_plain": code,
                "expires_at": now + timedelta(minutes=CODE_TTL_MINUTES),
                "attempts": 0,
                "created_at": now,
            }
        },
        upsert=True,
    )
    origin = (request.headers.get("origin") or os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")
    result = await send_email(
        email,
        "VizeAtlas Dubai giris kodunuz",
        login_code_html(code, CODE_TTL_MINUTES, f"{origin}/hesabim" if origin else ""),
        kind="login_code",
        meta={"email": email},
    )
    return {
        "sent": result.get("status") == "sent",
        "email_status": result.get("status"),
        "expires_in_minutes": CODE_TTL_MINUTES,
    }


@router.post("/account/verify-code")
async def verify_login_code(payload: CodeVerifyIn):
    email = _norm_email(payload.email)
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


@router.post("/account/login-lastname")
async def login_with_last_name(payload: LastNameLoginIn):
    """Mevcut basvurusu olan musteriler icin e-posta + soyad dogrulamasi."""
    email = _norm_email(payload.email)
    last_name = payload.last_name.strip().lower()
    cursor = applications_col.find({"contact.email": {"$regex": f"^{email}$", "$options": "i"}})
    async for doc in cursor:
        names = {(t.get("last_name") or "").strip().lower() for t in doc.get("travelers") or []}
        contact_name = (doc.get("contact") or {}).get("full_name") or ""
        if contact_name.strip():
            names.add(contact_name.strip().split()[-1].lower())
        if last_name in names:
            return {"token": _create_session_token(email), "email": email}
    raise HTTPException(404, "Bu e-posta ve soyad ile kayitli bir basvuru bulunamadi.")


# ------------------------------------------------------------- hesap ozetleri
@router.get("/account/me")
async def account_overview(email: str = Depends(require_customer)):
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
async def account_orders(email: str = Depends(require_customer)):
    """eSIM / sigorta siparisleri."""
    from db import orders_col

    cursor = orders_col.find({"contact.email": {"$regex": f"^{email}$", "$options": "i"}}).sort(
        "created_at", -1
    )
    items = [serialize_doc(doc) async for doc in cursor]
    return {"items": items}


@router.get("/account/drafts/{draft_id}")
async def account_draft_detail(draft_id: str, email: str = Depends(require_customer)):
    doc = await drafts_col.find_one({"id": draft_id, "email": email})
    if not doc:
        raise HTTPException(404, "Taslak bulunamadi.")
    return _draft_summary(doc, include_data=True)


@router.delete("/account/drafts/{draft_id}")
async def account_delete_draft(draft_id: str, email: str = Depends(require_customer)):
    res = await drafts_col.delete_one({"id": draft_id, "email": email})
    if res.deleted_count == 0:
        raise HTTPException(404, "Taslak bulunamadi.")
    return {"deleted": True}


# ------------------------------------------------------------------- taslaklar
@router.post("/drafts")
async def save_draft(payload: DraftIn, request: Request):
    """Yarim kalan basvuruyu kaydeder; devam kodu ile geri donulebilir."""
    email = _norm_email(payload.email)
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
    email_result = await send_email(
        email,
        "Basvurunuz kaydedildi - kaldiginiz yerden devam edin",
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
async def list_saved_travelers(email: str = Depends(require_customer)):
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
async def delete_saved_traveler(traveler_id: str, email: str = Depends(require_customer)):
    res = await saved_travelers_col.delete_one({"id": traveler_id, "email": email})
    if res.deleted_count == 0:
        raise HTTPException(404, "Kayitli yolcu bulunamadi.")
    return {"deleted": True}
