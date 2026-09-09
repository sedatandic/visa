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

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field

from content import (
    BANK_TRANSFER,
    BUNDLE_DISCOUNT,
    WITH_VISA_INSURANCE_DISCOUNT,
    bundle_discount_amount,
    family_discount_rate,
)
from db import cart_snapshots_col, orders_col, serialize_doc, settings_col
from emailer import order_admin_html, order_received_html, send_email
from fx import apply_fx_to_list, get_fx
from models import InsuredIn
from payment_receipt_pdf import build_receipt_pdf, receipt_filename
from rate_limit import allow as rate_allow
from rate_limit import check as rate_check
from rate_limit import client_ip

logger = logging.getLogger(__name__)
router = APIRouter()

ORDER_PREFIX = "SV-"

from store_catalog import (  # noqa: F401 - tests/other modules re-import from here
    DEFAULT_PRODUCTS,
    KIND_LABELS,
    MAX_QTY,
    product_list,
    tour_schedule,
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
        "insurance_id": "ins_7d",
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
        "tagline": "30 güne kadar sağlık teminatı + 10 GB bol veri.",
        "insurance_id": "ins_30d",
        "esim_id": "esim_10gb",
    },
    {
        "id": "pack_family",
        "visa_days": 30,
        "name": "Aile Paketi",
        "tagline": "Yolcu sayısını seçin; vizeler, sigorta ve eSIM tek pakette. İsterseniz çöl safarisini de ekleyin.",
        "insurance_id": "ins_15d",
        "esim_id": "esim_3gb",
        # 3 yolcu: vize bedellerine aile indirimi, ek hizmetlere paket indirimi uygulanir
        "family": {"adults": 2, "children": 1},
        # "Tam tatil" secenegi: yolcu sayisi kadar col safarisi
        "tour_id": "tour_desert_safari",
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
        "tagline": "60 gün sağlık teminatı + sınırsız internet; iş ve uzun tatil için.",
        "insurance_id": "ins_60d",
        "esim_id": "esim_unlimited",
    },
]


def _bundle_counts(tpl: dict, adults: Optional[int], children: Optional[int]) -> dict:
    """Sablon ve istekteki yolcu sayilarini tek sozlukte cozer."""
    family = tpl.get("family") or None
    adult_count = max(1, int(adults if adults is not None else (family or {}).get("adults", 1)))
    child_count = max(0, int(children if children is not None else (family or {}).get("children", 0)))
    return {
        "family": family,
        "adults": adult_count,
        "children": child_count,
        "travelers": adult_count + child_count,
    }


def _pick_bundle_visas(tpl: dict, visas: list, child_count: int) -> tuple:
    """Paket suresine uyan en uygun yetiskin ve (gerekiyorsa) cocuk vizesini secer."""

    def cheapest(items: list) -> Optional[dict]:
        return min(items, key=lambda v: float(v["price"])) if items else None

    same_days = [v for v in visas if int(v.get("duration_days") or 0) == tpl["visa_days"]]
    visa = cheapest(
        [v for v in same_days if v.get("applicant_type") == "adult" and v.get("category") == "single"]
    )
    child_visa = cheapest([v for v in same_days if v.get("category") == "child"]) if child_count else None
    return visa, child_visa


def _bundle_totals(prices: dict, quantities: dict, counts: dict) -> dict:
    """Ek hizmet ve vize tutarlarini paket + aile indirimleriyle hesaplar."""
    extras_list = round(
        prices["insurance"] * quantities["insurance"] + prices["esim"] * quantities["esim"], 2
    )
    tour_total = round(prices["tour"] * quantities["tour"], 2) if quantities["tour"] else 0.0
    # Paket indirimi siparis fiyatlamasiyla ayni: sigorta+eSIM varsa tum ek hizmetlere %10
    discount = round((extras_list + tour_total) * float(BUNDLE_DISCOUNT["rate"]), 2)
    visa_subtotal = round(
        prices["visa"] * counts["adults"] + prices["child_visa"] * counts["children"], 2
    )
    family_rate = family_discount_rate(counts["travelers"]) if counts["family"] else 0.0
    return {
        "extras_list": extras_list,
        "tour_total": tour_total,
        "discount": discount,
        "price": round(extras_list + tour_total - discount, 2),
        "visa_subtotal": visa_subtotal,
        "family_rate": family_rate,
        "visa_discount": round(visa_subtotal * family_rate, 2),
    }


def _bundle_family_block(counts: dict, child_visa: Optional[dict], totals: dict) -> Optional[dict]:
    """Aile paketleri icin yolcu/indirim kirilimini dondurur."""
    if not counts["family"]:
        return None
    return {
        "adults": counts["adults"],
        "children": counts["children"],
        "child_visa": (
            {
                "id": child_visa["id"],
                "name": child_visa["name"],
                "price": float(child_visa["price"]),
            }
            if child_visa
            else None
        ),
        "visa_subtotal": totals["visa_subtotal"],
        "visa_discount": totals["visa_discount"],
        "visa_discount_rate": totals["family_rate"],
        "traveler_count": counts["travelers"],
        "max_adults": 6,
        "max_children": 4,
    }


def _bundle_item(
    tpl: dict,
    products: dict,
    visas: list,
    adults: Optional[int] = None,
    children: Optional[int] = None,
    with_tour: bool = False,
) -> Optional[dict]:
    """Paketi verilen yolcu sayisina gore fiyatlandirir (varsayilan: sablon degerleri)."""
    insurance = products.get(tpl["insurance_id"])
    esim = products.get(tpl["esim_id"])
    if not insurance or not esim:
        return None
    counts = _bundle_counts(tpl, adults, children)
    visa, child_visa = _pick_bundle_visas(tpl, visas, counts["children"])
    tour = products.get(tpl.get("tour_id") or "") if counts["family"] else None
    quantities = {
        "insurance": counts["travelers"] if counts["family"] else 1,
        "esim": counts["adults"] if counts["family"] else 1,
        "tour": counts["travelers"] if (with_tour and tour) else 0,
    }
    totals = _bundle_totals(
        {
            "insurance": float(insurance["price"]),
            "esim": float(esim["price"]),
            "tour": float(tour["price"]) if tour else 0.0,
            "visa": float(visa["price"]) if visa else 0.0,
            "child_visa": float(child_visa["price"]) if child_visa else 0.0,
        },
        quantities,
        counts,
    )

    return {
        "id": tpl["id"],
        "name": tpl["name"],
        "tagline": tpl["tagline"],
        "visa_days": tpl["visa_days"],
        "popular": tpl.get("popular", False),
        "visa": (
            {"id": visa["id"], "name": visa["name"], "price": float(visa["price"])} if visa else None
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
        "tour": (
            {
                "id": tour["id"],
                "name": tour["name"],
                "price": tour["price"],
                "duration": tour.get("summary"),
                "selected": bool(quantities["tour"]),
                "total": totals["tour_total"],
            }
            if tour
            else None
        ),
        "list_total": round(totals["extras_list"] + totals["tour_total"], 2),
        "discount": totals["discount"],
        "price": totals["price"],
        "quantities": quantities,
        "family": _bundle_family_block(counts, child_visa, totals),
        "total_with_visa": (
            round(totals["price"] + totals["visa_subtotal"] - totals["visa_discount"], 2)
            if visa
            else None
        ),
        "currency": "TRY",
    }


async def bundle_list(visa_days: Optional[int] = None) -> dict:
    """Vize suresine uygun hazir paketleri fiyatlariyla dondurur."""
    from db import visa_types_col

    products = {p["id"]: p for p in await product_list()}
    visa_docs = await visa_types_col.find({"active": True}).to_list(100)
    visas = await apply_fx_to_list(serialize_doc(visa_docs)) if visa_docs else []
    items = []
    for tpl in BUNDLE_TEMPLATES:
        if visa_days and tpl["visa_days"] != int(visa_days):
            continue
        item = _bundle_item(tpl, products, visas)
        if item:
            items.append(item)
    return {"items": items, "bundle": BUNDLE_DISCOUNT}


@router.get("/bundles/quote")
async def get_bundle_quote(
    bundle_id: str,
    adults: int = 1,
    children: int = 0,
    tour: bool = False,
) -> dict:
    """Yolcu sayisi ve tur secimine gore paket fiyatini yeniden hesaplar."""
    from db import visa_types_col

    tpl = next((t for t in BUNDLE_TEMPLATES if t["id"] == bundle_id), None)
    if not tpl:
        raise HTTPException(status_code=404, detail="Paket bulunamadı.")
    products = {p["id"]: p for p in await product_list()}
    visa_docs = await visa_types_col.find({"active": True}).to_list(100)
    visas = await apply_fx_to_list(serialize_doc(visa_docs)) if visa_docs else []
    item = _bundle_item(
        tpl,
        products,
        visas,
        adults=max(1, min(int(adults), 6)),
        children=max(0, min(int(children), 4)),
        with_tour=bool(tour),
    )
    if not item:
        raise HTTPException(status_code=404, detail="Paket fiyatlandırılamadı.")
    return {"item": item, "bundle": BUNDLE_DISCOUNT}


# ------------------------------------------------------------------- modeller
class OrderItemIn(BaseModel):
    product_id: str
    quantity: int = Field(1, ge=1, le=MAX_QTY)
    scheduled_date: Optional[str] = None  # tur urunleri icin (YYYY-MM-DD)
    scheduled_time: Optional[str] = None


class OrderContactIn(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=90)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=25)


class OrderCreateIn(BaseModel):
    items: List[OrderItemIn] = Field(..., min_length=1, max_length=6)
    contact: OrderContactIn
    # Sigorta satiri varsa police kesimi icin sigortali kimlik bilgileri zorunlu
    insured: List[InsuredIn] = Field(default_factory=list, max_length=10)
    travel_start: Optional[str] = None
    travel_end: Optional[str] = None
    note: Optional[str] = Field(None, max_length=500)
    application_reference: Optional[str] = Field(None, max_length=24)
    payment_method: str = Field("card", pattern="^(card|transfer)$")


# ------------------------------------------------------------------ endpointler
@router.get("/products")
async def get_products(kind: Optional[str] = None) -> dict:
    if kind and kind not in KIND_LABELS:
        raise HTTPException(400, "Gecersiz urun tipi.")
    items = await product_list(kind)
    return {
        "items": items,
        "fx": await get_fx(),
        "bundle": BUNDLE_DISCOUNT,
        "visa_insurance": WITH_VISA_INSURANCE_DISCOUNT,
    }


@router.get("/bundles")
async def get_bundles(visa_days: Optional[int] = None) -> dict:
    return await bundle_list(visa_days)


def _parse_trip_start(value: Optional[str]) -> Optional[date]:
    """ISO tarih metnini gune cevirir; gecersizse None dondurur."""
    try:
        return date.fromisoformat((value or "").strip()[:10])
    except ValueError:
        return None


def _build_order_line(product: dict, item: "OrderItemIn", trip_start: Optional[date]) -> dict:
    """Tek bir siparis satirini (fiyat + gecerlilik penceresi + tur tarihi) olusturur."""
    quantity = item.quantity
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
        **tour_schedule(product, item.scheduled_date, item.scheduled_time, start=trip_start),
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
        lines.append(_build_order_line(product, item, trip_start))
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
    # Ayni alici saatte 40'tan fazla siparis postasi almaz (bombardiman engeli);
    # siparis her durumda olusur, yalnizca bildirim atlanir.
    if rate_allow(f"order-mail:{doc['contact']['email'].strip().lower()}", 40, 3600):
        await send_email(
            doc["contact"]["email"],
            f"Siparişiniz alındı - {doc['reference_code']}",
            order_received_html(view, bank),
            kind="order_received",
            meta={"order_id": doc["id"], "reference_code": doc["reference_code"]},
        )
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email:
        return
    await send_email(
        admin_email,
        f"Yeni eSIM/sigorta siparişi - {doc['reference_code']}",
        order_admin_html(view),
        kind="order_admin_notify",
        meta={"order_id": doc["id"]},
    )


async def _linked_application(reference: Optional[str], email: str) -> dict:
    """Musteri sepette vize basvuru kodu verdiyse siparisi o basvuruya baglar."""
    code = (reference or "").strip().upper()
    if not code:
        return {}
    from db import applications_col

    app_doc = await applications_col.find_one({"reference_code": code})
    if not app_doc:
        raise HTTPException(400, "Bu vize basvuru kodu bulunamadi. Kodu bos birakip devam edebilirsiniz.")
    app_email = ((app_doc.get("contact") or {}).get("email") or "").lower()
    if app_email and app_email != (email or "").strip().lower():
        raise HTTPException(
            400, "Basvuru kodu ile e-posta adresi eslesmiyor. Basvurudaki e-postayi kullanin."
        )
    return {"application_id": app_doc.get("id"), "application_reference": app_doc.get("reference_code")}


def _validate_insured(lines: list[dict], insured: list, travel_start: Optional[str]) -> list[dict]:
    """Sigorta satiri varsa sigortali sayisi, kimlik bilgileri ve police baslangicini dogrular."""
    needed = sum(int(line["quantity"]) for line in lines if line["kind"] == "insurance")
    if not needed:
        return []
    if len(insured) < needed:
        raise HTTPException(
            400,
            f"Poliçe kesilebilmesi için {needed} sigortalının ad-soyad, TC kimlik no ve "
            "doğum tarihi bilgisi gerekiyor.",
        )
    if not _parse_trip_start(travel_start):
        raise HTTPException(400, "Poliçe gidiş tarihinizde başlar; lütfen gidiş tarihini seçin.")
    return [person.model_dump() for person in insured[:needed]]


@router.post("/orders")
async def create_order(payload: OrderCreateIn, request: Request) -> dict:
    rate_check(
        f"order-create-ip:{client_ip(request)}",
        300,
        3600,
        "Cok fazla siparis denemesi. Lutfen daha sonra tekrar deneyin.",
    )
    lines = await _build_order_lines(payload)
    insured = _validate_insured(lines, payload.insured, payload.travel_start)
    linked = await _linked_application(payload.application_reference, payload.contact.email)
    now = datetime.now(timezone.utc)
    doc = {
        "id": str(uuid.uuid4()),
        "reference_code": new_order_reference(),
        "items": lines,
        "contact": payload.contact.model_dump(),
        "insured": insured,
        "travel_start": payload.travel_start,
        "travel_end": payload.travel_end,
        "note": payload.note,
        "source": "store",
        **linked,
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
    await cart_snapshots_col.update_one(
        {"email": payload.contact.email.lower()},
        {"$set": {"active": False, "closed_reason": "ordered", "updated_at": now}},
    )

    bank = await _bank_transfer_details(payload.payment_method)
    view = serialize_doc(doc)
    await _notify_new_order(doc, view, bank)
    return {"order": view, "bank": bank}


class CartSnapshotIn(BaseModel):
    """Terk edilmis sepet hatirlatmasi icin sepet kaydi."""

    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=80)
    items: List[OrderItemIn] = Field(default_factory=list, max_length=6)
    bundle_id: Optional[str] = Field(None, max_length=32)


@router.post("/cart/snapshot")
async def save_cart_snapshot(payload: CartSnapshotIn) -> dict:
    """Sepeti kaydeder; siparis verilmezse 3 ve 24 saat sonra hatirlatma gonderilir."""
    email = payload.email.lower()
    now = datetime.now(timezone.utc)
    if not payload.items:
        await cart_snapshots_col.update_one(
            {"email": email}, {"$set": {"active": False, "closed_reason": "emptied", "updated_at": now}}
        )
        return {"saved": False, "active": False}

    products = {p["id"]: p for p in await product_list()}
    lines = []
    for item in payload.items:
        product = products.get(item.product_id)
        if not product:
            continue
        unit_price = float(product["price"])
        lines.append(
            {
                "product_id": product["id"],
                "kind": product["kind"],
                "name": product["name"],
                "quantity": item.quantity,
                "unit_price": unit_price,
                "total": round(unit_price * item.quantity, 2),
            }
        )
    if not lines:
        raise HTTPException(400, "Sepette gecerli urun bulunamadi.")

    pricing = _pricing_block(lines)
    await cart_snapshots_col.update_one(
        {"email": email},
        {
            "$set": {
                "email": email,
                "full_name": payload.full_name,
                "items": lines,
                "bundle_id": payload.bundle_id,
                "currency": "TRY",
                **pricing,
                "active": True,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now, "reminders_sent": 0},
            "$unset": {"closed_reason": ""},
        },
        upsert=True,
    )
    return {"saved": True, "price": pricing["price"]}


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


async def _find_order_for_customer(reference: str, email: str) -> dict:
    """Siparis kodu + e-posta eslesmesi; misafir musteri erisimi icin tek kapi."""
    doc = await orders_col.find_one({"reference_code": (reference or "").strip().upper()})
    if not doc:
        raise HTTPException(404, "Siparis bulunamadi.")
    if (doc.get("contact") or {}).get("email", "").lower() != (email or "").strip().lower():
        raise HTTPException(404, "Siparis kodu ve e-posta eslesmiyor.")
    return doc


@router.get("/orders/{reference}")
async def get_order(reference: str, email: str) -> dict:
    doc = await _find_order_for_customer(reference, email)
    settings_doc = await settings_col.find_one({"key": "bank_transfer"})
    bank = (settings_doc or {}).get("value") or BANK_TRANSFER
    return {
        "order": serialize_doc(doc),
        "bank": bank if (doc.get("payment") or {}).get("method") == "bank_transfer" else None,
    }


@router.get("/orders/{reference}/receipt.pdf")
async def order_receipt_pdf(reference: str, email: str):
    """Siparis kodu + e-posta ile odeme ozetini (PDF) indirir."""
    doc = await _find_order_for_customer(reference, email)
    return Response(
        content=build_receipt_pdf(serialize_doc(doc), "order"),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{receipt_filename(doc)}"'},
    )
