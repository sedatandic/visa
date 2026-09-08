"""Tamamliyo cari bakiye takibi + kritik seviye uyarisi.

Tamamliyo bakiye sorgulama API'si sunmuyor; bakiyenin bittigini ancak odeme
aninda donen `HATA_15 "Yetersiz puan bakiyesi"` ile ogreniyoruz. Bu yuzden
bakiyeyi biz takip ediyoruz:

- Admin, Tamamliyo panelinden yukledigi tutari bir kez panele girer.
- Kesilen her policenin maliyeti bakiyeden dusulur.
- Kalan bakiye esigin altina inince admine e-posta + WhatsApp uyarisi gider.
- Tamamliyo "yetersiz bakiye" derse takip sifirlanir (gercek her zaman onda).
"""

import logging
import os
from datetime import datetime, timedelta, timezone

import whatsapp
from db import products_col, settings_col
from emailer import send_email

logger = logging.getLogger(__name__)

SETTINGS_KEY = "insurance_balance"
DEFAULT_THRESHOLD_POLICIES = 3
ALERT_COOLDOWN_HOURS = 12
TOPUP_HISTORY = 20


def is_balance_error(message: str) -> bool:
    """Saglayici hatasi bakiye yetersizligi mi?"""
    return "bakiye" in (message or "").lower()


def parse_try(value) -> float:
    """Tamamliyo tutarlarini ("1.244,85") float'a cevirir."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "").strip()
    if "," in text:  # Turkce format: binlik nokta, ondalik virgul
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _as_utc(value):
    """Mongo'dan gelen tarihler tz-naive olabiliyor; karsilastirma icin UTC yapar."""
    if isinstance(value, datetime) and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


async def _state() -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    return ((doc or {}).get("value") or {})


async def _unit_cost() -> float:
    """En pahali aktif policenin maliyeti: kac police kesilebilecegi temkinli hesaplanir."""
    costs = [
        float(p.get("cost_try") or 0)
        async for p in products_col.find({"kind": "insurance", "active": True}, {"cost_try": 1})
    ]
    return max([c for c in costs if c > 0], default=0.0)


async def status() -> dict:
    """Panelde gosterilen bakiye durumu."""
    state = await _state()
    loaded = round(float(state.get("loaded_try") or 0), 2)
    spent = round(float(state.get("spent_try") or 0), 2)
    remaining = round(max(loaded - spent, 0.0), 2)
    unit_cost = await _unit_cost()
    policies_left = int(remaining // unit_cost) if unit_cost else 0
    threshold = int(state.get("threshold_policies") or DEFAULT_THRESHOLD_POLICIES)
    return {
        "loaded_try": loaded,
        "spent_try": spent,
        "remaining_try": remaining,
        "unit_cost_try": round(unit_cost, 2),
        "policies_left": policies_left,
        "threshold_policies": threshold,
        "tracked": loaded > 0,
        "empty": remaining <= 0,
        "low": bool(unit_cost) and policies_left <= threshold,
        "last_topup_at": _as_utc(state.get("last_topup_at")),
        "last_alert_at": _as_utc(state.get("last_alert_at")),
        "topups": (state.get("topups") or [])[-5:][::-1],
    }


async def add_topup(amount: float, actor: str = "") -> dict:
    """Tamamliyo paneline yuklenen tutari kaydeder ve uyari kilidini sifirlar."""
    now = datetime.now(timezone.utc)
    entry = {"amount_try": round(float(amount), 2), "at": now, "by": actor}
    await settings_col.update_one(
        {"key": SETTINGS_KEY},
        {
            "$set": {
                "key": SETTINGS_KEY,
                "value.last_topup_at": now,
                "value.last_alert_at": None,
                "value.last_alert_kind": None,
            },
            "$inc": {"value.loaded_try": entry["amount_try"]},
            "$push": {"value.topups": {"$each": [entry], "$slice": -TOPUP_HISTORY}},
        },
        upsert=True,
    )
    return await status()


async def record_spend(amount: float) -> None:
    """Kesilen policenin maliyetini bakiyeden duser."""
    value = round(parse_try(amount), 2)
    if value <= 0:
        return
    await settings_col.update_one(
        {"key": SETTINGS_KEY},
        {"$set": {"key": SETTINGS_KEY}, "$inc": {"value.spent_try": value}},
        upsert=True,
    )


async def mark_empty() -> None:
    """Tamamliyo 'yetersiz bakiye' dedi: takibimiz ne derse desin kalan sifirlanir."""
    state = await _state()
    await settings_col.update_one(
        {"key": SETTINGS_KEY},
        {"$set": {"key": SETTINGS_KEY, "value.spent_try": round(float(state.get("loaded_try") or 0), 2)}},
        upsert=True,
    )


def _panel_link() -> str:
    site = (os.environ.get("PUBLIC_SITE_URL") or "").strip().rstrip("/")
    return f"{site}/admin/sigorta" if site else ""


def _alert_texts(state: dict, waiting: int) -> tuple:
    """(konu, html, whatsapp metni) — bakiye bittiyse acil, azaldiysa hatirlatma."""
    left = f"{state['remaining_try']:.2f} ₺".replace(".", ",")
    queue = (
        f"Şu anda <b>{waiting} poliçe</b> kesilmeyi bekliyor; bakiye yükleyince "
        "kendiliğinden kesilip müşterilere gönderilecek."
        if waiting
        else "Şu anda bekleyen poliçe yok."
    )
    link = _panel_link()
    button = (
        f'<p><a href="{link}" style="color:#B06A29;font-weight:bold">Sigorta panelini aç</a></p>'
        if link
        else ""
    )
    if state["empty"]:
        subject = "ACİL · Tamamliyo bakiyesi bitti, poliçe kesilemiyor"
        html = (
            '<div style="font-family:Arial,sans-serif;font-size:14px;color:#222">'
            "<p><b>Tamamliyo cari bakiyesi bitti; poliçe kesimi durdu.</b></p>"
            f"<p>{queue}</p>"
            "<p>Tamamliyo panelinden bakiye yükleyin, ardından Sigorta Poliçeleri "
            "ekranındaki <b>Bakiye yükledim</b> alanına tutarı girin.</p>"
            f"{button}</div>"
        )
        wa = (
            "ACİL: Tamamliyo bakiyesi bitti, poliçe kesilemiyor. "
            f"{waiting} poliçe bekliyor. Bakiye yükleyin."
        )
        return subject, html, wa

    subject = f"Tamamliyo bakiyesi azaldı · yaklaşık {state['policies_left']} poliçe kaldı"
    html = (
        '<div style="font-family:Arial,sans-serif;font-size:14px;color:#222">'
        f"<p><b>Tamamliyo bakiyesi azaldı: kalan {left} (yaklaşık "
        f"{state['policies_left']} poliçe).</b></p>"
        "<p>Satışın durmaması için bakiye yüklemenizi öneririz.</p>"
        f"{button}</div>"
    )
    wa = (
        f"Tamamliyo bakiyesi azaldı: kalan {left}, yaklaşık {state['policies_left']} poliçe. "
        "Satış durmasın diye bakiye yükleyin."
    )
    return subject, html, wa


async def _cooldown_passed(kind: str) -> bool:
    state = await _state()
    last_at = _as_utc(state.get("last_alert_at"))
    if state.get("last_alert_kind") != kind or not isinstance(last_at, datetime):
        return True
    return datetime.now(timezone.utc) - last_at >= timedelta(hours=ALERT_COOLDOWN_HOURS)


async def maybe_alert(waiting: int = 0) -> dict:
    """Bakiye kritik/bitmis ise admine e-posta + WhatsApp uyarisi gonderir."""
    state = await status()
    if not state["tracked"] and not waiting:
        return {"sent": False, "reason": "not_tracked"}
    if not (state["empty"] or state["low"]):
        return {"sent": False, "reason": "ok"}

    kind = "empty" if state["empty"] else "low"
    if not await _cooldown_passed(kind):
        return {"sent": False, "reason": "cooldown", "kind": kind}

    subject, html, wa_text = _alert_texts(state, waiting)
    admin_email = (os.environ.get("ADMIN_EMAIL") or "").strip()
    email_result = {"status": "skipped"}
    if admin_email:
        email_result = await send_email(
            admin_email, subject, html, kind="insurance_balance_alert", meta={"kind": kind}
        )
    wa_result = await whatsapp.send_admin_text(wa_text, reason="insurance_balance_alert")

    await settings_col.update_one(
        {"key": SETTINGS_KEY},
        {
            "$set": {
                "key": SETTINGS_KEY,
                "value.last_alert_at": datetime.now(timezone.utc),
                "value.last_alert_kind": kind,
            }
        },
        upsert=True,
    )
    logger.warning("tamamliyo bakiye uyarisi gonderildi (%s, bekleyen: %s)", kind, waiting)
    return {"sent": True, "kind": kind, "email": email_result, "whatsapp": wa_result}
