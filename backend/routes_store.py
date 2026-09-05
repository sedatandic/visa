"""eSIM ve seyahat sigortasi satisi (magaza).

- Urunler `store_products` koleksiyonunda tutulur, fiyatlar USD bazlidir ve
  guncel kurla TL'ye cevrilir.
- Siparisler `store_orders` koleksiyonunda tutulur.
- Teslimat acente eliyle yapilir: admin panelden eSIM QR kodu / police PDF
  yuklenip musteriye e-posta ile gonderilir.
"""

import logging
import os
import secrets
import string
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from content import BANK_TRANSFER, BUNDLE_DISCOUNT, bundle_discount_amount
from db import orders_col, serialize_doc, settings_col
from emailer import order_admin_html, order_received_html, send_email
from fx import get_fx

logger = logging.getLogger(__name__)
router = APIRouter()

ORDER_PREFIX = "SV-"

from store_catalog import (  # noqa: F401
    DEFAULT_PRODUCTS,
    MAX_QTY,
    ESIM_PRODUCTS,
    INSURANCE_PRODUCTS,
    KIND_LABELS,
    TOUR_PRODUCTS,
    product_list,
)


def new_order_reference() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ORDER_PREFIX + "".join(secrets.choice(alphabet) for _ in range(8))



# --------------------------------------------------------------------- paketler
# Vize suresine gore hazir seyahat paketleri (sigorta + eSIM birlikte, %10 indirimli)
BUNDLE_TEMPLATES = [
    {
        "id": "pack_short",
        "visa_days": 30,
        "name": "Kısa Kaçamak Paketi",
        "tagline": "3-5 günlük şehir molası için yeterli koruma ve internet.",
        "insurance_id": "ins_8d",
        "esim_id": "esim_1gb",
    },
    {
        "id": "pack_standard",
        "visa_days": 30,
        "name": "Standart Tatil Paketi",
        "tagline": "Bir haftalık Dubai tatilinin standardı; en çok tercih edilen paket.",
        "insurance_id": "ins_15d",
        "esim_id": "esim_3gb",
        "popular": True,
    },
    {
        "id": "pack_comfort",
        "visa_days": 30,
        "name": "Konforlu 30 Gün Paketi",
        "tagline": "Bagaj ve seyahat kesintisi teminatı + bol veri, 30 güne kadar.",
        "insurance_id": "ins_30d_plus",
        "esim_id": "esim_10gb",
    },
    {
        "id": "pack_long",
        "visa_days": 60,
        "name": "Uzun Konaklama Paketi",
        "tagline": "60 güne kadar sağlık teminatı ve 30 günlük 10 GB internet.",
        "insurance_id": "ins_60d",
        "esim_id": "esim_10gb",
        "popular": True,
    },
    {
        "id": "pack_long_plus",
        "visa_days": 60,
        "name": "Uzun Konaklama Plus",
        "tagline": "Geniş kapsam teminat + sınırsız internet; iş ve uzun tatil için.",
        "insurance_id": "ins_60d_plus",
        "esim_id": "esim_unlimited",
    },
]


async def bundle_list(visa_days: Optional[int] = None) -> dict:
    """Vize suresine uygun hazir paketleri fiyatlariyla dondurur."""
    from db import visa_types_col
    from routes_public import apply_fx_to_list

    products = {p["id"]: p for p in await product_list()}
    visa_docs = await visa_types_col.find({"active": True}).to_list(100)
    visas = await apply_fx_to_list(serialize_doc(visa_docs)) if visa_docs else []
    rate = float(BUNDLE_DISCOUNT["rate"])
    items = []
    for tpl in BUNDLE_TEMPLATES:
        if visa_days and tpl["visa_days"] != int(visa_days):
            continue
        insurance = products.get(tpl["insurance_id"])
        esim = products.get(tpl["esim_id"])
        if not insurance or not esim:
            continue
        candidates = [
            v
            for v in visas
            if int(v.get("duration_days") or 0) == tpl["visa_days"]
            and v.get("applicant_type") == "adult"
            and v.get("category") == "single"
        ]
        visa = min(candidates, key=lambda v: float(v["price"])) if candidates else None
        list_total = round(float(insurance["price"]) + float(esim["price"]), 2)
        discount = round(list_total * rate, 2)
        price = round(list_total - discount, 2)
        items.append(
            {
                "id": tpl["id"],
                "name": tpl["name"],
                "tagline": tpl["tagline"],
                "visa_days": tpl["visa_days"],
                "popular": tpl.get("popular", False),
                "visa": (
                    {"id": visa["id"], "name": visa["name"], "price": float(visa["price"])}
                    if visa
                    else None
                ),
                "insurance": {
                    "id": insurance["id"],
                    "name": insurance["name"],
                    "price": insurance["price"],
                    "validity_days": insurance.get("validity_days"),
                    "coverage": insurance.get("coverage"),
                },
                "esim": {
                    "id": esim["id"],
                    "name": esim["name"],
                    "price": esim["price"],
                    "data_amount": esim.get("data_amount"),
                    "validity_days": esim.get("validity_days"),
                },
                "list_total": list_total,
                "discount": discount,
                "price": price,
                "total_with_visa": round(price + float(visa["price"]), 2) if visa else None,
                "currency": "TRY",
            }
        )
    return {"items": items, "bundle": BUNDLE_DISCOUNT}


# ------------------------------------------------------------------- modeller
class OrderItemIn(BaseModel):
    product_id: str
    quantity: int = Field(1, ge=1, le=MAX_QTY)


class OrderContactIn(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=90)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=25)


class OrderCreateIn(BaseModel):
    items: List[OrderItemIn] = Field(..., min_length=1, max_length=6)
    contact: OrderContactIn
    travel_start: Optional[str] = None
    travel_end: Optional[str] = None
    note: Optional[str] = Field(None, max_length=500)
    payment_method: str = Field("card", pattern="^(card|transfer)$")


# ------------------------------------------------------------------ endpointler
@router.get("/products")
async def get_products(kind: Optional[str] = None) -> dict:
    if kind and kind not in KIND_LABELS:
        raise HTTPException(400, "Gecersiz urun tipi.")
    items = await product_list(kind)
    return {"items": items, "fx": await get_fx(), "bundle": BUNDLE_DISCOUNT}


@router.get("/bundles")
async def get_bundles(visa_days: Optional[int] = None) -> dict:
    return await bundle_list(visa_days)


def _parse_trip_start(value: Optional[str]) -> Optional[date]:
    """ISO tarih metnini gune cevirir; gecersizse None dondurur."""
    try:
        return date.fromisoformat((value or "").strip()[:10])
    except ValueError:
        return None


def _build_order_line(product: dict, quantity: int, trip_start: Optional[date]) -> dict:
    """Tek bir siparis satirini (fiyat + gecerlilik penceresi) olusturur."""
    validity_days = int(product.get("validity_days") or 0)
    ends_on = None
    if trip_start and validity_days > 0:
        ends_on = (trip_start + timedelta(days=validity_days - 1)).isoformat()
    return {
        "product_id": product["id"],
        "kind": product["kind"],
        "name": product["name"],
        "quantity": quantity,
        "unit_price": float(product["price"]),
        "unit_price_usd": float(product.get("price_usd") or 0),
        "unit_cost": float(product.get("cost_try") or 0),
        "total": round(float(product["price"]) * quantity, 2),
        "validity_days": validity_days,
        "starts_on": trip_start.isoformat() if trip_start else None,
        "ends_on": ends_on,
    }


async def _build_order_lines(payload: OrderCreateIn) -> list[dict]:
    """Katalogdan dogrulanmis siparis satirlarini uretir."""
    catalog = {p["id"]: p for p in await product_list()}
    trip_start = _parse_trip_start(payload.travel_start)
    lines: list[dict] = []
    for item in payload.items:
        product = catalog.get(item.product_id)
        if not product:
            raise HTTPException(400, "Secilen urun bulunamadi veya satista degil.")
        lines.append(_build_order_line(product, item.quantity, trip_start))
    return lines


def _payment_block(payment_method: str) -> dict:
    is_transfer = payment_method == "transfer"
    return {
        "method": "bank_transfer" if is_transfer else "card",
        "status": "awaiting_transfer" if is_transfer else "pending",
    }


def _pricing_block(lines: list[dict]) -> dict:
    """Ara toplam + paket indirimi + odenecek tutari hesaplar."""
    items_total = round(sum(float(line["total"]) for line in lines), 2)
    bundle_discount = bundle_discount_amount(lines)
    return {
        "items_total": items_total,
        "bundle_discount": bundle_discount,
        "bundle_discount_rate": float(BUNDLE_DISCOUNT["rate"]) if bundle_discount else 0.0,
        "price": round(items_total - bundle_discount, 2),
    }


async def _bank_transfer_details(payment_method: str) -> Optional[dict]:
    if payment_method != "transfer":
        return None
    settings_doc = await settings_col.find_one({"key": "bank_transfer"})
    return (settings_doc or {}).get("value") or BANK_TRANSFER


async def _notify_new_order(doc: dict, view: dict, bank: Optional[dict]) -> None:
    """Musteriye ve (tanimliysa) admine siparis bildirimi gonderir."""
    await send_email(
        doc["contact"]["email"],
        f"Siparisiniz alindi - {doc['reference_code']}",
        order_received_html(view, bank),
        kind="order_received",
        meta={"order_id": doc["id"], "reference_code": doc["reference_code"]},
    )
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email:
        return
    await send_email(
        admin_email,
        f"Yeni eSIM/sigorta siparisi - {doc['reference_code']}",
        order_admin_html(view),
        kind="order_admin_notify",
        meta={"order_id": doc["id"]},
    )


@router.post("/orders")
async def create_order(payload: OrderCreateIn) -> dict:
    lines = await _build_order_lines(payload)
    now = datetime.now(timezone.utc)
    doc = {
        "id": str(uuid.uuid4()),
        "reference_code": new_order_reference(),
        "items": lines,
        "contact": payload.contact.model_dump(),
        "travel_start": payload.travel_start,
        "travel_end": payload.travel_end,
        "note": payload.note,
        **_pricing_block(lines),
        "currency": "TRY",
        "fx_rate": (await get_fx())["effective_rate"],
        "status": "pending",
        "payment": _payment_block(payload.payment_method),
        "delivery": {},
        "created_at": now,
        "updated_at": now,
    }
    await orders_col.insert_one(dict(doc))

    bank = await _bank_transfer_details(payload.payment_method)
    view = serialize_doc(doc)
    await _notify_new_order(doc, view, bank)
    return {"order": view, "bank": bank}


def _application_order_items(lines: list) -> list[dict]:
    """Vize basvurusundaki store satirlarini siparis kalemlerine cevirir."""
    return [
        {
            "product_id": line["product_id"],
            "kind": line.get("kind", ""),
            "name": line["name"],
            "quantity": int(line.get("quantity") or 1),
            "unit_price": float(line.get("unit_price") or 0),
            "unit_price_usd": float(line.get("unit_price_usd") or 0),
            "total": float(line.get("total") or 0),
            "validity_days": line.get("validity_days"),
            "starts_on": line.get("starts_on"),
            "ends_on": line.get("ends_on"),
            "scheduled_date": line.get("scheduled_date"),
            "scheduled_time": line.get("scheduled_time"),
        }
        for line in lines
    ]


def _application_order_note(app_doc: dict, travel: dict) -> str:
    tours = [
        f"{line['name']}: {line.get('scheduled_date')} {line.get('scheduled_time') or ''}".strip()
        for line in ((app_doc.get("pricing") or {}).get("store_items") or [])
        if line.get("scheduled_date")
    ]
    return (
        f"Vize basvurusu ile birlikte alindi ({app_doc.get('reference_code')}). "
        f"Seyahat: {travel.get('arrival_date') or '-'} / {travel.get('departure_date') or '-'}. "
        "Urunler giris tarihinde baslatilacak."
        + (f" Tur rezervasyonu: {'; '.join(tours)}." if tours else "")
    )


async def create_application_order(app_doc: dict, lines: list) -> dict:
    """Vize basvurusu icinde alinan eSIM / sigorta urunleri icin teslimat siparisi olusturur.

    Odeme vize basvurusu uzerinden tahsil edilir; bu kayit yalnizca admin
    teslimat akisi (eSIM QR / police PDF) icin kullanilir.
    """
    now = datetime.now(timezone.utc)
    contact = app_doc.get("contact") or {}
    travel = app_doc.get("travel") or {}
    payment = app_doc.get("payment") or {}
    items = _application_order_items(lines)
    doc = {
        "id": str(uuid.uuid4()),
        "reference_code": new_order_reference(),
        "items": items,
        "contact": {
            "full_name": contact.get("full_name", ""),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
        },
        "travel_start": travel.get("arrival_date"),
        "travel_end": travel.get("departure_date"),
        "note": _application_order_note(app_doc, travel),
        "source": "visa_application",
        "application_id": app_doc.get("id"),
        "application_reference": app_doc.get("reference_code"),
        **_pricing_block(items),
        "currency": "TRY",
        "fx_rate": (await get_fx())["effective_rate"],
        "status": "pending",
        "payment": {
            "method": payment.get("method") or "card",
            "status": payment.get("status") or "pending",
            "via": "visa_application",
        },
        "delivery": {},
        "created_at": now,
        "updated_at": now,
    }
    await orders_col.insert_one(dict(doc))
    return doc


async def sync_application_order_payment(application_id: str, status: str, method: str | None = None) -> None:
    """Vize basvurusunun odeme durumu degistiginde bagli siparisi de guncelle."""
    if not application_id:
        return
    now = datetime.now(timezone.utc)
    update = {"payment.status": status, "updated_at": now}
    if method:
        update["payment.method"] = method
    if status == "paid":
        update["payment.paid_at"] = now
        update["status"] = "processing"
    try:
        await orders_col.update_many(
            {"application_id": application_id, "source": "visa_application"},
            {"$set": update},
        )
        if status == "paid":
            from insurance_tasks import queue_policy_tasks

            async for order in orders_col.find(
                {"application_id": application_id, "source": "visa_application"}
            ):
                await queue_policy_tasks(order)
    except Exception as exc:  # pragma: no cover
        logger.warning("linked order payment sync failed: %s", exc)


@router.get("/orders/{reference}")
async def get_order(reference: str, email: str) -> dict:
    doc = await orders_col.find_one({"reference_code": (reference or "").strip().upper()})
    if not doc:
        raise HTTPException(404, "Siparis bulunamadi.")
    if (doc.get("contact") or {}).get("email", "").lower() != (email or "").strip().lower():
        raise HTTPException(404, "Siparis kodu ve e-posta eslesmiyor.")
    settings_doc = await settings_col.find_one({"key": "bank_transfer"})
    bank = (settings_doc or {}).get("value") or BANK_TRANSFER
    return {
        "order": serialize_doc(doc),
        "bank": bank if (doc.get("payment") or {}).get("method") == "bank_transfer" else None,
    }
