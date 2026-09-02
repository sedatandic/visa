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
from db import orders_col, products_col, serialize_doc, settings_col
from emailer import order_admin_html, order_received_html, send_email
from fx import get_fx, try_price

logger = logging.getLogger(__name__)
router = APIRouter()

ORDER_PREFIX = "SV-"
MAX_QTY = 10

ESIM_PRODUCTS = [
    {
        "id": "esim_1gb",
        "kind": "esim",
        "name": "Dubai eSIM · 1 GB / 7 gün",
        "summary": "Kısa mola ve aktarmalarda harita, çağrı uygulamaları ve sosyal medya için yeterli veri.",
        "price_usd": 9.0,
        "data_amount": "1 GB",
        "validity_days": 7,
        "features": [
            "BAE genelinde 4G/5G kapsama",
            "QR kod ile 2 dakikada kurulum",
            "Numaranız açık kalır, WhatsApp çalışır",
            "Fiziksel SIM değiştirmeye gerek yok",
        ],
        "order": 1,
        "popular": False,
    },
    {
        "id": "esim_3gb",
        "kind": "esim",
        "name": "Dubai eSIM · 3 GB / 15 gün",
        "summary": "Bir haftalık tatilde navigasyon, sosyal medya ve video görüşme için en çok tercih edilen paket.",
        "price_usd": 15.0,
        "data_amount": "3 GB",
        "validity_days": 15,
        "features": [
            "BAE genelinde 4G/5G kapsama",
            "QR kod ile anında kurulum",
            "Hotspot (internet paylaşımı) açık",
            "Uygulama içi veri takibi",
        ],
        "order": 2,
        "popular": True,
    },
    {
        "id": "esim_10gb",
        "kind": "esim",
        "name": "Dubai eSIM · 10 GB / 30 gün",
        "summary": "Uzun kalışlar ve iş seyahatleri için bol veri; toplantı ve video görüşmelerinde rahat kullanım.",
        "price_usd": 29.0,
        "data_amount": "10 GB",
        "validity_days": 30,
        "features": [
            "30 gün geçerli bol veri",
            "Hotspot açık, dizüstü bilgisayara bağlanır",
            "Video görüşme ve bulut yedekleme için uygun",
            "Kurulum desteği dahil",
        ],
        "order": 3,
        "popular": False,
    },
    {
        "id": "esim_unlimited",
        "kind": "esim",
        "name": "Dubai eSIM · Sınırsız / 30 gün",
        "summary": "Veri limiti düşünmeden kullanmak isteyenler için adil kullanım kotalı sınırsız paket.",
        "price_usd": 49.0,
        "data_amount": "Sınırsız",
        "validity_days": 30,
        "features": [
            "Adil kullanım sonrası hız düşer, kesilmez",
            "Yayın (streaming) ve harita kullanımı serbest",
            "Hotspot açık",
            "Öncelikli destek",
        ],
        "order": 4,
        "popular": False,
    },
]

INSURANCE_PRODUCTS = [
    {
        "id": "ins_basic",
        "kind": "insurance",
        "name": "Seyahat Sigortası · Temel",
        "summary": "30 güne kadar seyahatlerde acil sağlık masraflarını karşılayan, vize başvurusu için uygun temel poliçe.",
        "price_usd": 20.0,
        "coverage": "30.000 € teminat",
        "validity_days": 30,
        "features": [
            "30.000 € acil sağlık teminatı",
            "30 güne kadar seyahat süresi",
            "Vize başvurusuna uygun poliçe",
            "Poliçe PDF olarak e-postanıza gelir",
        ],
        "order": 1,
        "popular": True,
    },
    {
        "id": "ins_plus",
        "kind": "insurance",
        "name": "Seyahat Sigortası · Geniş Kapsam",
        "summary": "Uzun kalışlar için yüksek teminat; bagaj kaybı ve seyahat iptali gibi ek riskleri de kapsar.",
        "price_usd": 39.0,
        "coverage": "100.000 € teminat + bagaj / iptal",
        "validity_days": 60,
        "features": [
            "100.000 € acil sağlık teminatı",
            "60 güne kadar seyahat süresi",
            "Bagaj kaybı ve gecikmesi teminatı",
            "Seyahat iptal / değişiklik desteği",
        ],
        "order": 2,
        "popular": False,
    },
]

DEFAULT_PRODUCTS = ESIM_PRODUCTS + INSURANCE_PRODUCTS

KIND_LABELS = {"esim": "eSIM", "insurance": "Seyahat sigortası"}


def new_order_reference() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ORDER_PREFIX + "".join(secrets.choice(alphabet) for _ in range(8))


async def product_list(kind: Optional[str] = None, include_inactive: bool = False) -> list:
    query = {}
    if kind:
        query["kind"] = kind
    if not include_inactive:
        query["active"] = True
    docs = await products_col.find(query).sort("order", 1).to_list(100)
    if not docs:
        docs = [
            p for p in DEFAULT_PRODUCTS if (not kind or p["kind"] == kind)
        ]
    rate = (await get_fx())["effective_rate"]
    items = []
    for doc in serialize_doc(docs):
        item = dict(doc)
        item.pop("_id", None)
        if item.get("price_usd"):
            item["price"] = try_price(item["price_usd"], rate)
        item["currency"] = "TRY"
        item["fx_rate"] = rate
        item["kind_label"] = KIND_LABELS.get(item.get("kind"), "")
        items.append(item)
    return items


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
        }
        for line in lines
    ]


def _application_order_note(app_doc: dict, travel: dict) -> str:
    return (
        f"Vize basvurusu ile birlikte alindi ({app_doc.get('reference_code')}). "
        f"Seyahat: {travel.get('arrival_date') or '-'} / {travel.get('departure_date') or '-'}. "
        "Urunler giris tarihinde baslatilacak."
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
