"""Yonetici tarafindan hazirlanan, paylasilabilir teklif linkleri.

Akis: Admin -> Teklif Linkleri ekraninda yolcu/vize/ek urun secimi yapilir ve
tek tikla `/teklif/<token>` linki uretilir (WhatsApp paylasim metni hazir gelir).
Musteri linki acinca teklifi ve toplam tutari gorur; "Basvuruyu tamamla" dedigi
anda ayni secimler basvuru formuna dolar (`/basvuru?teklif=<token>`).

Fiyat her goruntulemede yeniden hesaplanir (kur/fiyat degisirse teklif guncel
kalir); hesaplama basarisiz olursa olusturma anindaki tutar gosterilir.
"""

import logging
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from fastapi import HTTPException

from content import compute_pricing
from db import offer_links_col, serialize_doc
from fx import addon_prices_try, get_fx
from models import StoreItemIn
from store_catalog import get_visa_type, resolve_store_lines, trip_day_count

logger = logging.getLogger(__name__)

DEFAULT_VALID_DAYS = 14
MAX_VALID_DAYS = 90


def new_token() -> str:
    """Tahmin edilemez, kisa paylasim jetonu (~72 bit)."""
    return secrets.token_urlsafe(9)


def site_url() -> str:
    return (os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")


def offer_url(token: str, base: str = "") -> str:
    return f"{(base or site_url()).rstrip('/')}/teklif/{token}"


def apply_url(token: str, base: str = "") -> str:
    return f"{(base or site_url()).rstrip('/')}/basvuru?teklif={token}"


def as_utc(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return None


def is_expired(doc: dict, now: datetime | None = None) -> bool:
    expires = as_utc(doc.get("expires_at"))
    return bool(expires and expires < (now or datetime.now(timezone.utc)))


def status_of(doc: dict, now: datetime | None = None) -> str:
    """disabled > used > expired > active."""
    if not doc.get("active", True):
        return "disabled"
    if doc.get("application_id"):
        return "used"
    if is_expired(doc, now):
        return "expired"
    return "active"


def is_open(doc: dict, now: datetime | None = None) -> bool:
    """Musteri linki hala acabilir mi? (kullanilmis teklif de acilabilir)"""
    return bool(doc.get("active", True)) and not is_expired(doc, now)


def money(amount, currency: str = "TRY") -> str:
    try:
        value = f"{round(float(amount)):,}".replace(",", ".")
    except (TypeError, ValueError):
        return ""
    return f"{value} ₺" if currency == "TRY" else f"{value} {currency}"


def wa_number(raw) -> str:
    """TR numarasini wa.me bicimine cevirir; taninmazsa bos doner."""
    digits = "".join(ch for ch in str(raw or "") if ch.isdigit())
    if digits.startswith("00"):
        digits = digits[2:]
    if len(digits) == 10 and digits.startswith("5"):
        digits = f"90{digits}"
    elif len(digits) == 11 and digits.startswith("05"):
        digits = f"90{digits[1:]}"
    return digits if len(digits) >= 11 else ""


def share_text(doc: dict, url: str) -> str:
    name = (doc.get("customer_name") or "").strip()
    lines = [
        f"Merhaba {name}," if name else "Merhaba,",
        f"{doc.get('title') or 'Dubai vize teklifiniz'} hazır: {money(doc.get('total'), doc.get('currency', 'TRY'))}",
        "Teklifi görüntüleyip başvurunuzu tamamlayabilirsiniz:",
        url,
        "Dubai Vize Hattı · TÜRSAB üyesi A Grubu seyahat acentesi",
    ]
    return "\n".join(lines)


def whatsapp_url(doc: dict, url: str) -> str:
    return f"https://wa.me/{wa_number(doc.get('customer_phone'))}?text={quote(share_text(doc, url))}"


def auto_title(travelers: list) -> str:
    first = (travelers or [{}])[0]
    visa = first.get("visa_short_name") or first.get("visa_name") or "Dubai vizesi"
    count = len(travelers or [])
    return f"{count} kişi · {visa}" if count > 1 else visa


def _visa_row(visa: dict, applicant_type: str) -> dict:
    return {
        "applicant_type": "child" if applicant_type == "child" else "adult",
        "visa_type_id": visa["id"],
        "visa_name": visa["name"],
        "visa_short_name": visa.get("short_name") or visa["name"],
        "price": float(visa["price"]),
    }


async def _visa_rows(travelers: list) -> list:
    rows = []
    for item in travelers or []:
        visa = await get_visa_type(item.get("visa_type_id") or "")
        if not visa:
            raise HTTPException(400, f"Geçersiz vize tipi: {item.get('visa_type_id')}")
        rows.append(_visa_row(visa, item.get("applicant_type") or "adult"))
    if not rows:
        raise HTTPException(400, "Teklife en az bir yolcu eklemelisiniz.")
    return rows


async def price_offer(
    travelers: list,
    addons: dict,
    store_items: list,
    arrival_date: str = "",
    departure_date: str = "",
) -> dict:
    """Teklifin guncel fiyatini basvuru akisiyla ayni kurallarla hesaplar."""
    rows = await _visa_rows(travelers)
    lines = await resolve_store_lines(
        [StoreItemIn(**item) for item in (store_items or [])], arrival_date, departure_date
    )
    quote = compute_pricing(
        [row["price"] for row in rows],
        dict(addons or {}),
        addon_prices=await addon_prices_try(),
        store_lines=lines,
    )
    quote["trip_days"] = trip_day_count(arrival_date, departure_date)
    quote["fx"] = await get_fx()
    return {"travelers": rows, "quote": quote}


def _customer_fields(payload) -> dict:
    return {
        "customer_name": (payload.customer_name or "").strip(),
        "customer_phone": (payload.customer_phone or "").strip(),
        "customer_email": (payload.customer_email or "").strip().lower(),
    }


def _tracking_fields(created_by: str) -> dict:
    return {
        "active": True,
        "views": 0,
        "conversions": 0,
        "application_id": None,
        "reference_code": None,
        "used_at": None,
        "created_by": created_by,
    }


async def create_offer(payload, created_by: str = "") -> dict:
    """Teklifi fiyatlandirip kaydeder ve dokumani dondurur."""
    store_items = [i.model_dump() for i in payload.store_items]
    addons = payload.addons.model_dump()
    priced = await price_offer(
        [t.model_dump() for t in payload.travelers],
        addons,
        store_items,
        payload.arrival_date,
        payload.departure_date,
    )
    now = datetime.now(timezone.utc)
    valid_days = min(max(int(payload.valid_days or DEFAULT_VALID_DAYS), 1), MAX_VALID_DAYS)
    doc = {
        "id": str(uuid.uuid4()),
        "token": new_token(),
        "title": (payload.title or "").strip() or auto_title(priced["travelers"]),
        **_customer_fields(payload),
        "travelers": priced["travelers"],
        "addons": addons,
        "store_items": store_items,
        "arrival_date": payload.arrival_date or "",
        "departure_date": payload.departure_date or "",
        "note": (payload.note or "").strip(),
        "quote": priced["quote"],
        "total": priced["quote"]["total"],
        "currency": priced["quote"].get("currency", "TRY"),
        **_tracking_fields(created_by),
        "created_at": now,
        "expires_at": now + timedelta(days=valid_days),
    }
    await offer_links_col.insert_one(dict(doc))
    doc.pop("_id", None)
    return doc


def admin_view(doc: dict, base: str = "") -> dict:
    """Yonetici listesi icin: durum + paylasim baglantilari."""
    out = serialize_doc(doc)
    token = doc.get("token") or ""
    url = offer_url(token, base)
    out.update(
        {
            "status": status_of(doc),
            "url": url,
            "apply_url": apply_url(token, base),
            "whatsapp_url": whatsapp_url(doc, url),
            "share_text": share_text(doc, url),
        }
    )
    return out


async def _repriced(doc: dict) -> dict:
    """Guncel fiyati hesaplar; urun/vize pasife alinmissa kayitli tutara duser."""
    try:
        return await price_offer(
            doc.get("travelers") or [],
            doc.get("addons") or {},
            doc.get("store_items") or [],
            doc.get("arrival_date") or "",
            doc.get("departure_date") or "",
        )
    except Exception as exc:
        logger.info("offer %s repricing failed: %s", doc.get("token"), exc)
        return {"travelers": doc.get("travelers") or [], "quote": doc.get("quote") or {}}


async def public_view(doc: dict) -> dict:
    """Musteriye gosterilecek teklif: guncel fiyat, kisisel veri en aza indirilmis."""
    priced = await _repriced(doc)
    quote = priced["quote"]
    return {
        "token": doc.get("token"),
        "title": doc.get("title") or "",
        "note": doc.get("note") or "",
        "customer_name": doc.get("customer_name") or "",
        "travelers": priced["travelers"],
        "addons": doc.get("addons") or {},
        "store_items": quote.get("store_items") or [],
        "arrival_date": doc.get("arrival_date") or "",
        "departure_date": doc.get("departure_date") or "",
        "quote": quote,
        "total": quote.get("total"),
        "currency": quote.get("currency", "TRY"),
        "status": status_of(doc),
        "created_at": serialize_doc(doc.get("created_at")),
        "expires_at": serialize_doc(doc.get("expires_at")),
        "apply_path": f"/basvuru?teklif={doc.get('token')}",
    }


async def mark_used(token: str, application: dict) -> None:
    """Teklif linkinden gelen basvuruyu teklife isler (donusum takibi)."""
    if not (token or "").strip():
        return
    await offer_links_col.update_one(
        {"token": token.strip()},
        {
            "$set": {
                "application_id": application.get("id"),
                "reference_code": application.get("reference_code"),
                "used_at": datetime.now(timezone.utc),
            },
            "$inc": {"conversions": 1},
        },
    )
