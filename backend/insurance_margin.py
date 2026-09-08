"""Kar korumasi: maliyeti satis fiyatini asan sigorta urunlerini otomatik fiyatlar + uyarir.

Uc kontrol noktasi:
- `guard_products()`: gunluk/elle fiyat senkronundan sonra ve panelden fiyat elle
  degistirildiginde calisir. Zarar eden urunun satis fiyatini `maliyet x marj` ile
  yukseltir; marj esigin (%20) altina dustuyse fiyata dokunmaz, yalnizca uyarir.
- `check_charge()`: police kesiminde karttan cekilen gercek tutar musteriden alinan
  tutari asarsa (satis zaten yapilmis) urun fiyatini duzeltir ve uyari gonderir.

Uyari kanallari: yonetici e-postasi + WhatsApp + panel bildirimi. Son 20 olay
`site_settings.insurance_margin.events` altinda saklanir ve panelde listelenir.
"""

import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

import whatsapp
from db import notifications_col, products_col, settings_col
from emailer import send_email
from store_catalog import INSURANCE_MARKUP

logger = logging.getLogger(__name__)

SETTINGS_KEY = "insurance_margin"
LOW_MARGIN_PCT = 20.0
ALERT_COOLDOWN_HOURS = 6
HISTORY_LIMIT = 20
PRODUCT_FIELDS = {
    "_id": 0,
    "id": 1,
    "name": 1,
    "validity_days": 1,
    "cost_try": 1,
    "price_try": 1,
    "order": 1,
}


def sale_price(cost: float) -> float:
    """Maliyet + marj (varsayilan %100), 10 TL'ye yuvarlanir."""
    return float(round(float(cost or 0) * INSURANCE_MARKUP / 10.0) * 10)


def margin_pct(price: float, cost: float):
    return round((price - cost) / cost * 100, 1) if cost > 0 else None


def _row(product: dict) -> dict:
    """Urunun maliyet/satis/marj durumu: ok | low | loss | unknown."""
    cost = float(product.get("cost_try") or 0)
    price = float(product.get("price_try") or 0)
    pct = margin_pct(price, cost)
    if cost <= 0 or price <= 0:
        state = "unknown"
    elif price <= cost:
        state = "loss"
    elif pct < LOW_MARGIN_PCT:
        state = "low"
    else:
        state = "ok"
    return {
        "id": product.get("id"),
        "name": product.get("name"),
        "validity_days": product.get("validity_days"),
        "cost_try": round(cost, 2),
        "price_try": round(price, 2),
        "profit_try": round(price - cost, 2),
        "margin_pct": pct,
        "state": state,
        "suggested_price_try": sale_price(cost) if cost > 0 else None,
    }


async def _state() -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    return (doc or {}).get("value") or {}


async def _save(values: dict) -> None:
    await settings_col.update_one(
        {"key": SETTINGS_KEY},
        {"$set": {"key": SETTINGS_KEY, **{f"value.{k}": v for k, v in values.items()}}},
        upsert=True,
    )


async def _push_events(events: list) -> None:
    if not events:
        return
    state = await _state()
    await _save({"events": (events + (state.get("events") or []))[:HISTORY_LIMIT]})


def _panel_link() -> str:
    site = (os.environ.get("PUBLIC_SITE_URL") or "").strip().rstrip("/")
    return (
        f'<p><a href="{site}/admin/sigorta" style="color:#B06A29;font-weight:bold">'
        "Sigorta panelini aç</a></p>"
        if site
        else ""
    )


def _money(value) -> str:
    return f"{float(value or 0):,.2f} ₺".replace(",", ".")


def _product_alert_texts(fixed: list, low: list) -> tuple:
    """Zarar eden / ince marjli urunler icin (konu, html, whatsapp) metinleri."""
    fixed_rows = "".join(
        f"<li><b>{row['name']}</b>: maliyet {_money(row['cost_try'])}, satış "
        f"{_money(row['price_try'])} → <b>{_money(row['new_price_try'])}</b></li>"
        for row in fixed
    )
    low_rows = "".join(
        f"<li><b>{row['name']}</b>: maliyet {_money(row['cost_try'])}, satış "
        f"{_money(row['price_try'])} (marj %{row['margin_pct']})</li>"
        for row in low
    )
    subject = (
        "Sigorta fiyatı otomatik güncellendi (kâr uyarısı)"
        if fixed
        else "Sigorta kâr marjı düştü (uyarı)"
    )
    html = (
        '<div style="font-family:Arial,sans-serif;font-size:14px;color:#3E2A14">'
        + (
            "<p><b>Maliyet satış fiyatına ulaştığı için satış fiyatları otomatik "
            f"yükseltildi:</b></p><ul>{fixed_rows}</ul>"
            if fixed
            else ""
        )
        + (
            f"<p><b>Kâr marjı %{LOW_MARGIN_PCT:.0f} altına düşen poliçeler</b> "
            f"(fiyata dokunulmadı):</p><ul>{low_rows}</ul>"
            if low
            else ""
        )
        + "<p>Yeni fiyatlar mağazada ve başvuru formunda anında geçerlidir.</p>"
        + _panel_link()
        + "</div>"
    )
    wa = (
        f"Kâr uyarısı: {len(fixed)} poliçenin satış fiyatı maliyet arttığı için otomatik "
        "yükseltildi."
        if fixed
        else f"Kâr uyarısı: {len(low)} poliçede marj %{LOW_MARGIN_PCT:.0f} altına düştü."
    )
    return subject, html, wa


def _charge_alert_texts(event: dict) -> tuple:
    """Kesilen policede zarar olustuysa (cekim > satis) uyari metinleri."""
    price_line = (
        f"<p>Satış fiyatı <b>{_money(event.get('old_price_try'))}</b> → "
        f"<b>{_money(event.get('new_price_try'))}</b> olarak güncellendi.</p>"
        if event.get("new_price_try") and event.get("new_price_try") != event.get("old_price_try")
        else "<p>Ürün satış fiyatı zaten yeni maliyetin üzerinde; fiyat değiştirilmedi.</p>"
    )
    subject = "ZARAR · Poliçe maliyeti satış fiyatını aştı"
    html = (
        '<div style="font-family:Arial,sans-serif;font-size:14px;color:#3E2A14">'
        f"<p><b>{event.get('name') or 'Poliçe'}</b> kesiminde karttan çekilen tutar, "
        "müşteriden alınan tutarı aştı.</p>"
        f"<ul><li>Sipariş: {event.get('order_reference') or '-'}</li>"
        f"<li>Karttan çekilen: <b>{_money(event.get('charged_try'))}</b></li>"
        f"<li>Müşteriden alınan: {_money(event.get('revenue_try'))}</li>"
        f"<li>Zarar: <b>{_money(event.get('loss_try'))}</b></li></ul>"
        + price_line
        + _panel_link()
        + "</div>"
    )
    wa = (
        f"ZARAR: {event.get('name') or 'poliçe'} kesiminde {_money(event.get('charged_try'))} "
        f"çekildi, müşteriden {_money(event.get('revenue_try'))} alındı. Satış fiyatı "
        "güncellendi."
    )
    return subject, html, wa


async def _cooldown_passed(kind: str) -> bool:
    state = await _state()
    last_at = state.get("last_alert_at")
    if state.get("last_alert_kind") != kind or not isinstance(last_at, datetime):
        return True
    if last_at.tzinfo is None:
        last_at = last_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - last_at >= timedelta(hours=ALERT_COOLDOWN_HOURS)


async def _alert(kind: str, subject: str, html: str, wa_text: str, cooldown: bool = True) -> dict:
    """Yoneticiye e-posta + WhatsApp + panel bildirimi gonderir."""
    if cooldown and not await _cooldown_passed(kind):
        return {"sent": False, "reason": "cooldown", "kind": kind}

    now = datetime.now(timezone.utc)
    admin_email = (os.environ.get("ADMIN_EMAIL") or "").strip()
    email_result = {"status": "skipped"}
    if admin_email:
        email_result = await send_email(
            admin_email, subject, html, kind="insurance_margin_alert", meta={"kind": kind}
        )
    wa_result = await whatsapp.send_admin_text(wa_text, reason="insurance_margin_alert")
    await notifications_col.insert_one(
        {
            "id": str(uuid.uuid4()),
            "kind": "insurance_margin_alert",
            "title": subject,
            "body": wa_text,
            "read": False,
            "created_at": now,
        }
    )
    await _save({"last_alert_at": now, "last_alert_kind": kind})
    logger.warning("sigorta kar uyarisi gonderildi (%s)", kind)
    return {"sent": True, "kind": kind, "email": email_result, "whatsapp": wa_result}


async def _products() -> list:
    return (
        await products_col.find({"kind": "insurance", "active": True}, PRODUCT_FIELDS)
        .sort("order", 1)
        .to_list(20)
    )


async def guard_products(reason: str = "sync") -> dict:
    """Zarar eden urunun fiyatini yukseltir, ince marjli urunler icin uyarir."""
    now = datetime.now(timezone.utc)
    fixed, low = [], []
    for product in await _products():
        row = _row(product)
        if row["state"] == "loss":
            await products_col.update_one(
                {"id": row["id"]},
                {
                    "$set": {
                        "price_try": row["suggested_price_try"],
                        "price_guard_at": now,
                        "price_guard_reason": reason,
                    }
                },
            )
            fixed.append({**row, "new_price_try": row["suggested_price_try"]})
        elif row["state"] == "low":
            low.append(row)

    events = [
        {
            "kind": "price_fixed",
            "at": now,
            "reason": reason,
            "product_id": row["id"],
            "name": row["name"],
            "cost_try": row["cost_try"],
            "old_price_try": row["price_try"],
            "new_price_try": row["new_price_try"],
        }
        for row in fixed
    ] + [
        {
            "kind": "low_margin",
            "at": now,
            "reason": reason,
            "product_id": row["id"],
            "name": row["name"],
            "cost_try": row["cost_try"],
            "price_try": row["price_try"],
            "margin_pct": row["margin_pct"],
        }
        for row in low
    ]
    await _push_events(events)
    await _save({"last_check_at": now})

    alert = {"sent": False, "reason": "no_risk"}
    if fixed or low:
        alert = await _alert("product", *_product_alert_texts(fixed, low))
    if fixed:
        logger.warning("kar korumasi: %s urun fiyati otomatik yukseltildi", len(fixed))
    return {"checked_at": now, "fixed": fixed, "low_margin": low, "alert": alert}


async def _raise_price(product_id: str, unit_cost: float) -> dict:
    """Gercek maliyet urunun kayitli maliyetini asiyorsa maliyet + satis fiyatini yukseltir."""
    product = await products_col.find_one({"id": product_id}, PRODUCT_FIELDS) if product_id else None
    if not product:
        return {}
    cost = round(max(float(product.get("cost_try") or 0), unit_cost), 2)
    price = round(float(product.get("price_try") or 0), 2)
    new_price = sale_price(cost)
    if new_price <= price:
        return {"cost_try": cost, "old_price_try": price, "new_price_try": price}
    await products_col.update_one(
        {"id": product_id},
        {
            "$set": {
                "cost_try": cost,
                "price_try": new_price,
                "price_guard_at": datetime.now(timezone.utc),
                "price_guard_reason": "charge",
            }
        },
    )
    return {"cost_try": cost, "old_price_try": price, "new_price_try": new_price}


async def check_charge(task: dict) -> dict:
    """Karttan cekilen tutar satis tutarini asarsa fiyati duzeltir ve uyari gonderir."""
    charged = round(float(task.get("charged_try") or 0), 2)
    quantity = max(1, int(task.get("quantity") or 1))
    revenue = round(float(task.get("unit_price") or 0) * quantity, 2)
    if charged <= 0 or revenue <= 0 or charged < revenue:
        return {"loss": False, "charged_try": charged, "revenue_try": revenue}

    fix = await _raise_price(task.get("product_id"), round(charged / quantity, 2))
    event = {
        "kind": "charge_loss",
        "at": datetime.now(timezone.utc),
        "reason": "charge",
        "product_id": task.get("product_id"),
        "name": task.get("plan_name"),
        "order_reference": task.get("order_reference"),
        "charged_try": charged,
        "revenue_try": revenue,
        "loss_try": round(charged - revenue, 2),
        **fix,
    }
    await _push_events([event])
    alert = await _alert("charge", *_charge_alert_texts(event), cooldown=False)
    logger.warning(
        "kar uyarisi: %s icin cekilen %.2f > satis %.2f", event["name"], charged, revenue
    )
    return {"loss": True, **event, "alert": alert}


async def status() -> dict:
    """Panelde gosterilen kar koruma durumu."""
    rows = [_row(product) for product in await _products()]
    state = await _state()
    return {
        "markup": INSURANCE_MARKUP,
        "low_margin_pct": LOW_MARGIN_PCT,
        "items": rows,
        "risk_count": sum(1 for row in rows if row["state"] in {"loss", "low"}),
        "events": (state.get("events") or [])[:HISTORY_LIMIT],
        "last_check_at": state.get("last_check_at"),
        "last_alert_at": state.get("last_alert_at"),
        "last_alert_kind": state.get("last_alert_kind"),
    }
