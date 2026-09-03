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
    "constants": {},
    "traveler_fields": {},
    # --- durum takibi ---
    "status_url": "",
    "status_search_selector": "",
    "status_result_selector": "",
    "status_keywords": {
        "approved": ["approved", "issued", "granted", "onay"],
        "rejected": ["rejected", "declined", "refused", "red"],
        "reviewing": ["processing", "in progress", "under process", "pending", "submitted"],
        "cancelled": ["cancelled", "canceled"],
    },
    "auto_check_enabled": False,
    "auto_check_hours": 6,
    "auto_notify": True,
    "updated_at": None,
}


def _fmt(value: str | None, style: str) -> str:
    """ISO tarihi istenen formata cevirir; cevrilemezse orijinali dondurur."""
    raw = (value or "").strip()[:10]
    parsed: datetime | None = None
    try:
        parsed = datetime.strptime(raw, "%Y-%m-%d")
    except Exception:
        return raw
    if parsed is None:  # pragma: no cover - defensive
        return raw
    d = parsed
    if style == "dmy":
        return d.strftime("%d/%m/%Y")
    if style == "dmy_dash":
        return d.strftime("%d-%m-%Y")
    if style == "mdy":
        return d.strftime("%m/%d/%Y")
    return d.strftime("%Y-%m-%d")


# Zami "Dubai Application" formundaki Visa Type secenekleri ile bizim vize
# tiplerimizin eslesmesi (select option etiketleri birebir kullanilir).
ZAMI_VISA_TYPE_LABELS = {
    "visa_30_single": "30 Days",
    "visa_30_multi": "30 Days Multi",
    "visa_60_single": "60 Days",
    "visa_60_multi": "60 Days Multi",
    "visa_30_child": "30 Days",
    "visa_60_child": "60 Days",
}

# Ulke kodlarindan portalda beklenen ingilizce ulke adlari
COUNTRY_LABELS = {
    "TR": "TURKEY",
    "TC": "TURKEY",
    "TUR": "TURKEY",
}


def country_label(code: str | None) -> str:
    raw = (code or "").strip()
    return COUNTRY_LABELS.get(raw.upper(), raw.upper())


def zami_visa_label(visa_type_id: str | None, fallback: str = "") -> str:
    return ZAMI_VISA_TYPE_LABELS.get((visa_type_id or "").strip(), fallback)


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
        "travel.arrival_date_dmy_dash": _fmt(travel.get("arrival_date"), "dmy_dash"),
        "travel.arrival_date_mdy": _fmt(travel.get("arrival_date"), "mdy"),
        "travel.departure_date": _fmt(travel.get("departure_date"), "iso"),
        "travel.departure_date_dmy": _fmt(travel.get("departure_date"), "dmy"),
        "travel.departure_date_dmy_dash": _fmt(travel.get("departure_date"), "dmy_dash"),
        "travel.departure_date_mdy": _fmt(travel.get("departure_date"), "mdy"),
        "travel.purpose": travel.get("purpose", ""),
        "travel.accommodation": travel.get("accommodation", ""),
        "travel.flight_no": travel.get("flight_no", ""),
        "travel.notes": travel.get("notes", ""),
        "visa_type_name": app_doc.get("visa_type_name", ""),
        "zami_visa_type": zami_visa_label(
            (travelers[0] or {}).get("visa_type_id") if travelers else "",
            app_doc.get("visa_type_name", ""),
        ),
        "birth_country_label": country_label(travel.get("birth_country") or "TR"),
        # Zami "Group Membership": tek yolcu ise 'None / Alone', aile ise ana kisi
        "zami_group_membership": "None / Alone" if len(travelers) <= 1 else "Family Main Person",
        "zami_total_members": str(len(travelers)) if len(travelers) > 1 else "",
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
                "birth_date_dmy_dash": _fmt(t.get("birth_date"), "dmy_dash"),
                "birth_date_mdy": _fmt(t.get("birth_date"), "mdy"),
                "gender": t.get("gender", ""),
                "gender_label": GENDER_LABELS.get(t.get("gender", ""), ""),
                "gender_en": "Male" if t.get("gender") == "male" else "Female",
                "nationality": t.get("nationality", "TR"),
                "nationality_label": country_label(t.get("nationality") or "TR"),
                "passport_country_label": country_label(t.get("nationality") or "TR"),
                "national_id": t.get("national_id", ""),
                "passport_no": t.get("passport_no", ""),
                "passport_expiry": _fmt(t.get("passport_expiry"), "iso"),
                "passport_expiry_dmy": _fmt(t.get("passport_expiry"), "dmy"),
                "passport_expiry_dmy_dash": _fmt(t.get("passport_expiry"), "dmy_dash"),
                "passport_expiry_mdy": _fmt(t.get("passport_expiry"), "mdy"),
                "passport_issue_date": _fmt(t.get("passport_issue_date"), "iso"),
                "passport_issue_date_dmy": _fmt(t.get("passport_issue_date"), "dmy"),
                "passport_issue_date_dmy_dash": _fmt(t.get("passport_issue_date"), "dmy_dash"),
                "birth_place": (t.get("birth_place") or "").strip(),
                "passport_issue_place": (t.get("passport_issue_place") or "").strip(),
                "applicant_type": t.get("applicant_type", "adult"),
                "applicant_type_label": APPLICANT_LABELS.get(t.get("applicant_type", "adult"), ""),
                "visa_type_name": t.get("visa_type_name", ""),
                "zami_visa_type": zami_visa_label(t.get("visa_type_id"), t.get("visa_type_name", "")),
                "phone": contact.get("phone", ""),
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
# Zami formunda zorunlu olup bizim basvuru formumuzda toplanmayan alanlar.
# Aktarim sonrasi operatore hatirlatilir (robot bu alanlari bos birakir).
MANUAL_FIELDS = [
    {"selector": '[name="fa"]', "label": "Baba Adı"},
    {"selector": '[name="mo"]', "label": "Anne Adı"},
    {"selector": '[name="pf_tt"]', "label": "Meslek"},
    {"selector": '[name="eu"]', "label": "Eğitim"},
    {"selector": '[name="tr_a_d"]', "label": "Geliş uçuş tarihi"},
    {"selector": '[name="tr_a_fn"]', "label": "Geliş uçuş no"},
    {"selector": '[name="tr_d_d"]', "label": "Dönüş uçuş tarihi"},
    {"selector": '[name="tr_d_fn"]', "label": "Dönüş uçuş no"},
]


async def get_mapping() -> dict:
    doc = await settings_col.find_one({"key": MAPPING_KEY})
    mapping = dict(DEFAULT_MAPPING)
    if doc and isinstance(doc.get("value"), dict):
        mapping.update(doc["value"])
    return mapping


async def save_mapping(value: dict) -> dict:
    mapping = dict(DEFAULT_MAPPING)
    keywords = value.get("status_keywords")
    if not isinstance(keywords, dict) or not keywords:
        keywords = DEFAULT_MAPPING["status_keywords"]
    mapping.update(
        {
            "form_url": (value.get("form_url") or "").strip(),
            "submit_selector": (value.get("submit_selector") or "").strip(),
            "dry_run": bool(value.get("dry_run", True)),
            "fields": {k: v for k, v in (value.get("fields") or {}).items() if v},
            "constants": {k: v for k, v in (value.get("constants") or {}).items() if v},
            "traveler_fields": {k: v for k, v in (value.get("traveler_fields") or {}).items() if v},
            "status_url": (value.get("status_url") or "").strip(),
            "status_search_selector": (value.get("status_search_selector") or "").strip(),
            "status_result_selector": (value.get("status_result_selector") or "").strip(),
            "status_keywords": {
                k: [str(w).strip().lower() for w in (v or []) if str(w).strip()]
                for k, v in keywords.items()
            },
            "auto_check_enabled": bool(value.get("auto_check_enabled", False)),
            "auto_check_hours": max(1, min(int(value.get("auto_check_hours") or 6), 48)),
            "auto_notify": bool(value.get("auto_notify", True)),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    await settings_col.update_one(
        {"key": MAPPING_KEY}, {"$set": {"key": MAPPING_KEY, "value": mapping}}, upsert=True
    )
    return mapping


def match_status(raw_text: str, keywords: dict) -> str | None:
    """Portaldan okunan metni bizim durum koduna cevirir."""
    text = (raw_text or "").lower()
    if not text.strip():
        return None
    # ret/onay gibi kesin ifadeler once denenir
    for status in ("approved", "rejected", "cancelled", "reviewing"):
        for word in keywords.get(status) or []:
            if word and word in text:
                return status
    return None


def normalize_portal_url(value: str) -> str:
    """Portal adresini taban adrese indirir (sonundaki /login vb. temizlenir)."""
    url = (value or "").strip().rstrip("/")
    for suffix in ("/login", "/signin", "/sign-in"):
        if url.lower().endswith(suffix):
            url = url[: -len(suffix)].rstrip("/")
    return url or DEFAULT_PORTAL_URL


async def get_settings() -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    value = (doc or {}).get("value") or {}
    return {
        "portal_url": normalize_portal_url(
            value.get("portal_url") or os.environ.get("ZAMI_PORTAL_URL") or DEFAULT_PORTAL_URL
        ),
        "username": value.get("username") or os.environ.get("ZAMI_USERNAME") or "",
        "has_password": bool(value.get("password") or os.environ.get("ZAMI_PASSWORD")),
    }


async def save_settings(value: dict) -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    current = (doc or {}).get("value") or {}
    new_value = {
        "portal_url": normalize_portal_url(
            value.get("portal_url") or current.get("portal_url") or DEFAULT_PORTAL_URL
        ),
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
        "portal_url": normalize_portal_url(
            value.get("portal_url") or os.environ.get("ZAMI_PORTAL_URL") or DEFAULT_PORTAL_URL
        ),
        "username": value.get("username") or os.environ.get("ZAMI_USERNAME") or "",
        "password": value.get("password") or os.environ.get("ZAMI_PASSWORD") or "",
    }


# ------------------------------------------------- form HTML alan cikarimi
CAPTURE_KEY = "zami_capture"

# Otomatik eslesme icin anahtar kelimeler (alan adi/etiketinde aranir)
GLOBAL_HINTS = [
    ("contact.email", ["email", "e-mail", "eposta"]),
    ("contact.phone", ["phone", "mobile", "tel", "contact_no", "whatsapp"]),
    ("contact.full_name", ["client name", "client_name", "customer", "agent name", "contact name", "full name"]),
    ("travel.arrival_date_dmy", ["arrival", "entry date", "travel date", "date of arrival", "from date"]),
    ("travel.departure_date_dmy", ["departure", "exit date", "return", "to date"]),
    ("travel.flight_no", ["flight"]),
    ("travel.accommodation", ["hotel", "accommodation", "address in uae", "stay"]),
    ("travel.purpose", ["purpose", "reason"]),
    ("travel.notes", ["remark", "note", "comment"]),
    ("visa_type_name", ["visa type", "visa_type", "service", "package"]),
    ("reference_code", ["reference", "ref no", "booking"]),
]

TRAVELER_HINTS = [
    ("first_name", ["first name", "firstname", "given name", "fname", "name_first"]),
    ("last_name", ["last name", "lastname", "surname", "family name", "lname"]),
    ("full_name", ["full name", "passenger name", "traveller name", "traveler name", "name"]),
    ("passport_no", ["passport no", "passport number", "passportno", "passport_no", "passport"]),
    ("passport_expiry_dmy", ["passport expiry", "expiry", "valid till", "valid until", "expiration"]),
    ("birth_date_dmy", ["birth", "dob", "date of birth"]),
    ("gender_label", ["gender", "sex"]),
    ("nationality", ["nationality", "country"]),
    ("national_id", ["national id", "id number", "tc", "identity"]),
    ("applicant_type_label", ["applicant type", "pax type", "adult", "child", "type"]),
]

TRAVELER_MARKERS = ["pax", "passenger", "traveller", "traveler", "applicant", "person", "guest"]


def _haystack(field: dict) -> str:
    return " ".join(
        str(field.get(k) or "").lower().replace("_", " ").replace("-", " ")
        for k in ("label", "name", "id", "placeholder")
    )


def _traveler_template(selector: str) -> str | None:
    """`pax[0][first_name]` gibi indeksli seciciyi `{i}` sablonuna cevirir."""
    for pattern, repl in (
        (re.compile(r"\[(0|1)\]"), "[{i}]"),
        (re.compile(r"(_|-)(0|1)(?=\]|_|-|\"|$)"), r"\1{i}"),
    ):
        if pattern.search(selector):
            return pattern.sub(repl, selector, count=1)
    return None


def suggest_mapping(captured: dict) -> dict:
    """Yakalanan form alanlarindan otomatik eslesme onerisi uretir."""
    form = (captured or {}).get("form") or {}
    fields = form.get("fields") or []
    suggestions = {"fields": {}, "traveler_fields": {}, "notes": []}
    used = set()

    for field in fields:
        selector = field.get("selector")
        if not selector or selector in used:
            continue
        hay = _haystack(field)
        template = _traveler_template(selector)
        is_traveler = bool(template) or any(m in hay for m in TRAVELER_MARKERS)

        if is_traveler:
            for key, words in TRAVELER_HINTS:
                if key in suggestions["traveler_fields"]:
                    continue
                if any(w in hay for w in words):
                    suggestions["traveler_fields"][key] = template or selector
                    used.add(selector)
                    break
            continue

        for key, words in GLOBAL_HINTS:
            if key in suggestions["fields"]:
                continue
            if any(w in hay for w in words):
                suggestions["fields"][key] = selector
                used.add(selector)
                break

    if form.get("submit_selector"):
        suggestions["submit_selector"] = form["submit_selector"]
    if form.get("url"):
        suggestions["form_url"] = form["url"]

    status = (captured or {}).get("status") or {}
    if status.get("url"):
        suggestions["status_url"] = status["url"]
    if status.get("search_selector"):
        suggestions["status_search_selector"] = status["search_selector"]
    if status.get("row_selector"):
        suggestions["status_result_selector"] = status["row_selector"]

    if not suggestions["fields"] and not suggestions["traveler_fields"]:
        suggestions["notes"].append("Otomatik eşleşme bulunamadı; alanları elle seçmeniz gerekebilir.")
    return suggestions


async def get_capture() -> dict:
    doc = await settings_col.find_one({"key": CAPTURE_KEY})
    return (doc or {}).get("value") or {}


async def save_capture(page_type: str, data: dict) -> dict:
    current = await get_capture()
    key = "status" if page_type == "status" else "form"
    current[key] = data
    current[f"{key}_captured_at"] = datetime.now(timezone.utc).isoformat()
    await settings_col.update_one(
        {"key": CAPTURE_KEY}, {"$set": {"key": CAPTURE_KEY, "value": current}}, upsert=True
    )
    return current


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
async def create_capture_token(created_by: str, base_url: str) -> dict:
    """Zami sayfasindan alan yakalamak icin tek kullanimlik kod."""
    token = secrets.token_urlsafe(18)
    now = datetime.now(timezone.utc)
    await zami_handoffs_col.insert_one(
        {
            "id": str(uuid.uuid4()),
            "token": token,
            "kind": "capture",
            "application_id": None,
            "reference_code": None,
            "created_by": created_by,
            "created_at": now,
            "expires_at": now + timedelta(minutes=HANDOFF_TTL_MINUTES),
            "used_count": 0,
            "base_url": (base_url or "").rstrip("/"),
        }
    )
    return {
        "token": token,
        "expires_in_minutes": HANDOFF_TTL_MINUTES,
        "capture_script_url": f"{base_url}/api/zami/capture.js",
    }


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
