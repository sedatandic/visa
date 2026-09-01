"""Zami Tours portali (visa.zamitours.ae) icin basvuru aktarim servisi.

Portalda giriste CAPTCHA + OTP oldugu icin tam otomatik login mumkun degil.
Bu yuzden iki yaklasim birlikte desteklenir:

A) Bookmarklet (tarayici tarafinda otomatik doldurma)
   - Acente Zami'ye kendi tarayicisindan girer (captcha/OTP kendisi),
   - Basvuru formunda bookmarklet'i calistirir,
   - Bookmarklet, tek kullanimlik "handoff" token ile bizim API'den veriyi ceker
     ve alan eslemesine (mapping) gore formu doldurur.

B) Playwright RPA (sunucu tarafinda, insan onayli login)
   - Admin panelinden oturum baslatilir, captcha gorseli + OTP admin'e gosterilir,
   - Login sonrasi cerezler saklanir ve basvuru formu otomatik doldurulur.

Zami form alan adlari bilinmedigi icin tum eslemeler admin panelinden
konfigure edilir (`zami_mapping` ayari).
"""

import logging
import os
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from db import settings_col, zami_handoffs_col, zami_logs_col

logger = logging.getLogger(__name__)

MAPPING_KEY = "zami_mapping"
SETTINGS_KEY = "zami_settings"
SESSION_KEY = "zami_session"

DEFAULT_PORTAL_URL = "https://visa.zamitours.ae"
HANDOFF_TTL_MINUTES = 45

GENDER_LABELS = {"male": "Male", "female": "Female"}
APPLICANT_LABELS = {"adult": "Adult", "child": "Child"}

# Bizim semadaki aktarilabilir alanlar. Admin bunlari Zami form alanlariyla esler.
GLOBAL_FIELDS = [
    ("reference_code", "Başvuru referans kodu"),
    ("contact.full_name", "İletişim - ad soyad"),
    ("contact.email", "İletişim - e-posta"),
    ("contact.phone", "İletişim - telefon"),
    ("contact.address_city", "İletişim - şehir"),
    ("travel.arrival_date", "Seyahat - giriş tarihi (YYYY-AA-GG)"),
    ("travel.arrival_date_dmy", "Seyahat - giriş tarihi (GG/AA/YYYY)"),
    ("travel.arrival_date_mdy", "Seyahat - giriş tarihi (AA/GG/YYYY)"),
    ("travel.departure_date", "Seyahat - dönüş tarihi (YYYY-AA-GG)"),
    ("travel.departure_date_dmy", "Seyahat - dönüş tarihi (GG/AA/YYYY)"),
    ("travel.departure_date_mdy", "Seyahat - dönüş tarihi (AA/GG/YYYY)"),
    ("travel.purpose", "Seyahat amacı"),
    ("travel.accommodation", "Otel / konaklama"),
    ("travel.flight_no", "Uçuş numarası"),
    ("travel.notes", "Not"),
    ("visa_type_name", "Vize tipi (ad)"),
    ("traveler_count", "Yolcu sayısı"),
]

TRAVELER_FIELDS = [
    ("first_name", "Ad"),
    ("last_name", "Soyad"),
    ("full_name", "Ad soyad"),
    ("birth_date", "Doğum tarihi (YYYY-AA-GG)"),
    ("birth_date_dmy", "Doğum tarihi (GG/AA/YYYY)"),
    ("birth_date_mdy", "Doğum tarihi (AA/GG/YYYY)"),
    ("gender", "Cinsiyet (male/female)"),
    ("gender_label", "Cinsiyet (Male/Female)"),
    ("nationality", "Uyruk"),
    ("national_id", "TC kimlik no"),
    ("passport_no", "Pasaport no"),
    ("passport_expiry", "Pasaport geçerlilik (YYYY-AA-GG)"),
    ("passport_expiry_dmy", "Pasaport geçerlilik (GG/AA/YYYY)"),
    ("passport_expiry_mdy", "Pasaport geçerlilik (AA/GG/YYYY)"),
    ("applicant_type", "Başvuran tipi (adult/child)"),
    ("applicant_type_label", "Başvuran tipi (Adult/Child)"),
    ("visa_type_name", "Vize tipi (ad)"),
]

DEFAULT_MAPPING = {
    "form_url": "",
    "submit_selector": "",
    "dry_run": True,
    "fields": {},
    "traveler_fields": {},
    "updated_at": None,
}


def _fmt(value: str | None, style: str) -> str:
    """ISO tarihi istenen formata cevirir; cevrilemezse orijinali dondurur."""
    raw = (value or "").strip()[:10]
    try:
        d = datetime.strptime(raw, "%Y-%m-%d")
    except Exception:
        return raw
    if style == "dmy":
        return d.strftime("%d/%m/%Y")
    if style == "mdy":
        return d.strftime("%m/%d/%Y")
    return d.strftime("%Y-%m-%d")


def build_payload(app_doc: dict, file_base_url: str = "") -> dict:
    """Basvuru dokumanini Zami aktarimi icin duz alan/deger sozluklerine cevirir."""
    contact = app_doc.get("contact") or {}
    travel = app_doc.get("travel") or {}
    travelers = app_doc.get("travelers") or []
    extra = app_doc.get("extra_documents") or {}

    globals_map = {
        "reference_code": app_doc.get("reference_code", ""),
        "contact.full_name": contact.get("full_name", ""),
        "contact.email": contact.get("email", ""),
        "contact.phone": contact.get("phone", ""),
        "contact.address_city": contact.get("address_city", ""),
        "travel.arrival_date": _fmt(travel.get("arrival_date"), "iso"),
        "travel.arrival_date_dmy": _fmt(travel.get("arrival_date"), "dmy"),
        "travel.arrival_date_mdy": _fmt(travel.get("arrival_date"), "mdy"),
        "travel.departure_date": _fmt(travel.get("departure_date"), "iso"),
        "travel.departure_date_dmy": _fmt(travel.get("departure_date"), "dmy"),
        "travel.departure_date_mdy": _fmt(travel.get("departure_date"), "mdy"),
        "travel.purpose": travel.get("purpose", ""),
        "travel.accommodation": travel.get("accommodation", ""),
        "travel.flight_no": travel.get("flight_no", ""),
        "travel.notes": travel.get("notes", ""),
        "visa_type_name": app_doc.get("visa_type_name", ""),
        "traveler_count": str(len(travelers)),
    }

    traveler_rows = []
    for t in travelers:
        traveler_rows.append(
            {
                "first_name": t.get("first_name", ""),
                "last_name": t.get("last_name", ""),
                "full_name": f"{t.get('first_name','')} {t.get('last_name','')}".strip(),
                "birth_date": _fmt(t.get("birth_date"), "iso"),
                "birth_date_dmy": _fmt(t.get("birth_date"), "dmy"),
                "birth_date_mdy": _fmt(t.get("birth_date"), "mdy"),
                "gender": t.get("gender", ""),
                "gender_label": GENDER_LABELS.get(t.get("gender", ""), ""),
                "nationality": t.get("nationality", "TR"),
                "national_id": t.get("national_id", ""),
                "passport_no": t.get("passport_no", ""),
                "passport_expiry": _fmt(t.get("passport_expiry"), "iso"),
                "passport_expiry_dmy": _fmt(t.get("passport_expiry"), "dmy"),
                "passport_expiry_mdy": _fmt(t.get("passport_expiry"), "mdy"),
                "applicant_type": t.get("applicant_type", "adult"),
                "applicant_type_label": APPLICANT_LABELS.get(t.get("applicant_type", "adult"), ""),
                "visa_type_name": t.get("visa_type_name", ""),
            }
        )

    def file_url(file_id):
        if not file_id:
            return None
        return f"{file_base_url}/api/files/{file_id}?download=1"

    documents = []
    for idx, t in enumerate(travelers):
        docs = t.get("documents") or {}
        name = f"{t.get('first_name','')} {t.get('last_name','')}".strip() or f"Yolcu {idx + 1}"
        if docs.get("passport_file_id"):
            documents.append({"label": f"{name} · Pasaport", "url": file_url(docs["passport_file_id"]), "traveler_index": idx})
        if docs.get("photo_file_id"):
            documents.append({"label": f"{name} · Vesikalık", "url": file_url(docs["photo_file_id"]), "traveler_index": idx})
    if extra.get("ticket_file_id"):
        documents.append({"label": "Uçak bileti / rezervasyon", "url": file_url(extra["ticket_file_id"]), "traveler_index": None})
    if extra.get("hotel_file_id"):
        documents.append({"label": "Otel rezervasyonu", "url": file_url(extra["hotel_file_id"]), "traveler_index": None})
    for fid in extra.get("other_file_ids") or []:
        documents.append({"label": "Ek belge", "url": file_url(fid), "traveler_index": None})

    return {
        "application_id": app_doc.get("id"),
        "reference_code": app_doc.get("reference_code"),
        "globals": globals_map,
        "travelers": traveler_rows,
        "documents": documents,
    }


# ------------------------------------------------------------------ mapping
async def get_mapping() -> dict:
    doc = await settings_col.find_one({"key": MAPPING_KEY})
    mapping = dict(DEFAULT_MAPPING)
    if doc and isinstance(doc.get("value"), dict):
        mapping.update(doc["value"])
    return mapping


async def save_mapping(value: dict) -> dict:
    mapping = dict(DEFAULT_MAPPING)
    mapping.update(
        {
            "form_url": (value.get("form_url") or "").strip(),
            "submit_selector": (value.get("submit_selector") or "").strip(),
            "dry_run": bool(value.get("dry_run", True)),
            "fields": {k: v for k, v in (value.get("fields") or {}).items() if v},
            "traveler_fields": {k: v for k, v in (value.get("traveler_fields") or {}).items() if v},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    await settings_col.update_one(
        {"key": MAPPING_KEY}, {"$set": {"key": MAPPING_KEY, "value": mapping}}, upsert=True
    )
    return mapping


async def get_settings() -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    value = (doc or {}).get("value") or {}
    return {
        "portal_url": value.get("portal_url") or os.environ.get("ZAMI_PORTAL_URL") or DEFAULT_PORTAL_URL,
        "username": value.get("username") or os.environ.get("ZAMI_USERNAME") or "",
        "has_password": bool(value.get("password") or os.environ.get("ZAMI_PASSWORD")),
    }


async def save_settings(value: dict) -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    current = (doc or {}).get("value") or {}
    new_value = {
        "portal_url": (value.get("portal_url") or current.get("portal_url") or DEFAULT_PORTAL_URL).strip(),
        "username": (value.get("username") or current.get("username") or "").strip(),
        "password": value.get("password") or current.get("password") or "",
    }
    await settings_col.update_one(
        {"key": SETTINGS_KEY}, {"$set": {"key": SETTINGS_KEY, "value": new_value}}, upsert=True
    )
    return await get_settings()


async def raw_credentials() -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    value = (doc or {}).get("value") or {}
    return {
        "portal_url": value.get("portal_url") or os.environ.get("ZAMI_PORTAL_URL") or DEFAULT_PORTAL_URL,
        "username": value.get("username") or os.environ.get("ZAMI_USERNAME") or "",
        "password": value.get("password") or os.environ.get("ZAMI_PASSWORD") or "",
    }


# ------------------------------------------------- form HTML alan cikarimi
def parse_form_fields(html: str) -> list:
    """Zami form HTML'inden doldurulabilir alanlari cikarir."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html or "", "html.parser")
    fields = []
    for el in soup.find_all(["input", "select", "textarea"]):
        el_type = (el.get("type") or ("select" if el.name == "select" else "text")).lower()
        if el_type in {"hidden", "submit", "button", "reset", "image"}:
            continue
        name = el.get("name") or ""
        el_id = el.get("id") or ""
        if not name and not el_id:
            continue
        selector = f'[name="{name}"]' if name else f"#{el_id}"
        label = ""
        if el_id:
            lab = soup.find("label", attrs={"for": el_id})
            if lab:
                label = lab.get_text(" ", strip=True)
        if not label:
            parent_label = el.find_parent("label")
            if parent_label:
                label = parent_label.get_text(" ", strip=True)
        if not label:
            label = el.get("placeholder") or el.get("aria-label") or name or el_id
        options = []
        if el.name == "select":
            for opt in el.find_all("option"):
                options.append({"value": opt.get("value") or opt.get_text(strip=True), "label": opt.get_text(strip=True)})
        fields.append(
            {
                "tag": el.name,
                "type": el_type,
                "name": name,
                "id": el_id,
                "selector": selector,
                "label": re.sub(r"\s+", " ", label)[:120],
                "options": options[:40],
            }
        )
    return fields


# ------------------------------------------------------ handoff (bookmarklet)
async def create_handoff(app_doc: dict, created_by: str, file_base_url: str) -> dict:
    token = secrets.token_urlsafe(24)
    now = datetime.now(timezone.utc)
    doc = {
        "id": str(uuid.uuid4()),
        "token": token,
        "application_id": app_doc.get("id"),
        "reference_code": app_doc.get("reference_code"),
        "created_by": created_by,
        "created_at": now,
        "expires_at": now + timedelta(minutes=HANDOFF_TTL_MINUTES),
        "used_count": 0,
        "base_url": (file_base_url or "").rstrip("/"),
    }
    await zami_handoffs_col.insert_one(dict(doc))
    await log_event(
        app_doc.get("id"),
        app_doc.get("reference_code"),
        "handoff_created",
        "Bookmarklet aktarim kodu olusturuldu",
        actor=created_by,
    )
    return {
        "token": token,
        "expires_at": doc["expires_at"].isoformat(),
        "expires_in_minutes": HANDOFF_TTL_MINUTES,
        "reference_code": doc["reference_code"],
        "payload_url": f"{file_base_url}/api/zami/handoff/{token}",
    }


async def consume_handoff(token: str) -> dict | None:
    doc = await zami_handoffs_col.find_one({"token": (token or "").strip()})
    if not doc:
        return None
    expires = doc.get("expires_at")
    if isinstance(expires, datetime):
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            return None
    await zami_handoffs_col.update_one({"token": token}, {"$inc": {"used_count": 1}})
    return doc


# ------------------------------------------------------------------- loglar
async def log_event(application_id, reference_code, event: str, message: str, actor: str = "", extra: dict | None = None):
    doc = {
        "id": str(uuid.uuid4()),
        "application_id": application_id,
        "reference_code": reference_code,
        "event": event,
        "message": message,
        "actor": actor,
        "extra": extra or {},
        "created_at": datetime.now(timezone.utc),
    }
    try:
        await zami_logs_col.insert_one(dict(doc))
    except Exception as exc:  # pragma: no cover
        logger.warning("zami log failed: %s", exc)
    return doc
