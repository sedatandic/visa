"""Tamamliyo police odemesi durum takibi + operator uyarisi.

Police bedeli `odeme-yap` ucundan varsayilan olarak partner cari bakiyesinden
dusulur (`odemeTipi=3`); `TAMAMLIYO_PAYMENT_TYPE=2` ile kurumsal karta gecilebilir.
Iki basarisizlik durumu var:

- **Odeme reddi / bakiye-limit sorunu**: gorev `waiting_payment` kuyruguna alinir,
  15 dakikada bir yeniden denenir, operatore e-posta + WhatsApp uyarisi gider.
- **Yanit alinamadi (zaman asimi)**: cekim yapilmis olabilir; gorev `payment_review`
  durumuna alinir ve mukerrer cekim riski nedeniyle OTOMATIK TEKRAR DENENMEZ.
"""

import logging
import os
import re
from datetime import datetime, timedelta, timezone

import tamamliyo
import whatsapp
from db import settings_col
from emailer import send_email

logger = logging.getLogger(__name__)

SETTINGS_KEY = "insurance_payment"
ALERT_COOLDOWN_HOURS = 12
# Odeme engeli olarak degerlendirilen saglayici hatalari (kart/limit/bakiye/tanimsiz kart)
BLOCKED_KEYWORDS = ("kart", "bakiye", "limit", "yetersiz", "tanımlı değil", "tanimli degil")


def parse_try(value) -> float:
    """'1.234,56 TL' / '244,85' / 244.85 -> float (Tamamliyo fiyat alanlari)."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "").strip()
    if not text:
        return 0.0
    text = re.sub(r"[^\d,.]", "", text).replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def is_payment_unknown(message: str) -> bool:
    """Odeme istegine yanit alinamadi mi (cekim yapilmis olabilir)?"""
    return tamamliyo.PAYMENT_UNKNOWN_MARKER in (message or "")


def is_payment_blocked(message: str) -> bool:
    """Saglayici hatasi odeme kaynakli mi (kart reddi, limit, kart tanimsiz)?"""
    text = (message or "").lower()
    if not text or is_payment_unknown(message):
        return False
    return any(word in text for word in BLOCKED_KEYWORDS)


def _as_utc(value):
    """Mongo'dan gelen tarihler tz-naive olabiliyor; karsilastirma icin UTC yapar."""
    if isinstance(value, datetime) and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


async def _state() -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    return ((doc or {}).get("value") or {})


async def status() -> dict:
    """Panelde gosterilen odeme durumu."""
    state = await _state()
    return {
        "method": "balance" if tamamliyo.balance_mode() else "card",
        "card_configured": tamamliyo.card_configured(),
        "card_hint": tamamliyo.card_hint(),
        "provider_configured": tamamliyo.configured(),
        "last_alert_at": _as_utc(state.get("last_alert_at")),
        "last_alert_kind": state.get("last_alert_kind"),
    }


def _panel_link() -> str:
    site = (os.environ.get("PUBLIC_SITE_URL") or "").strip().rstrip("/")
    return f"{site}/admin/sigorta" if site else ""


def _alert_texts(kind: str, waiting: int, card_configured: bool) -> tuple:
    """(konu, html, whatsapp metni) — odeme engeli ya da dogrulama bekleyen cekim."""
    link = _panel_link()
    button = (
        f'<p><a href="{link}" style="color:#B06A29;font-weight:bold">Sigorta panelini aç</a></p>'
        if link
        else ""
    )
    queue = (
        f"Şu anda <b>{waiting} poliçe</b> kesilmeyi bekliyor."
        if waiting
        else "Şu anda bekleyen poliçe yok."
    )
    if kind == "review":
        subject = "ACİL · Tamamliyo ödemesi doğrulanmalı"
        html = (
            '<div style="font-family:Arial,sans-serif;font-size:14px;color:#222">'
            "<p><b>Tamamliyo ödeme isteğine yanıt alınamadı; çekim yapılmış olabilir.</b></p>"
            "<p>Mükerrer çekim riski nedeniyle bu poliçe için otomatik tekrar denenmiyor. "
            "Tamamliyo panelinden ilgili teklifin ödeme durumunu kontrol edip poliçeyi "
            "panelden elle kesin.</p>"
            f"<p>{queue}</p>{button}</div>"
        )
        wa = (
            "ACİL: Tamamliyo ödeme yanıtı alınamadı, çekim yapılmış olabilir. "
            "Panelden ödeme durumunu kontrol edin (otomatik tekrar denenmiyor)."
        )
        return subject, html, wa

    if tamamliyo.balance_mode():
        reason = "Tamamliyo cari bakiyesinden ödeme yapılamadı (bakiye yetersiz olabilir)."
    elif not card_configured:
        reason = "Kart bilgileri tanımlı olmadığı için ödeme yapılamadı."
    else:
        reason = "Kurumsal kartla ödeme başarısız oldu (limit/ret olabilir)."
    subject = "ACİL · Tamamliyo poliçe ödemesi başarısız"
    html = (
        '<div style="font-family:Arial,sans-serif;font-size:14px;color:#222">'
        f"<p><b>{reason}</b></p>"
        f"<p>{queue} Ödeme sorunu çözülünce kuyruk kendiliğinden kesilip müşterilere "
        "gönderilecek.</p>"
        "<p>Kartın limitini ve geçerliliğini kontrol edin; gerekiyorsa sunucudaki kart "
        "bilgilerini güncelleyin.</p>"
        f"{button}</div>"
    )
    wa = (
        f"ACİL: Tamamliyo poliçe ödemesi başarısız. {waiting} poliçe bekliyor. "
        "Kart limitini/geçerliliğini kontrol edin."
    )
    return subject, html, wa


async def _cooldown_passed(kind: str) -> bool:
    state = await _state()
    last_at = _as_utc(state.get("last_alert_at"))
    if state.get("last_alert_kind") != kind or not isinstance(last_at, datetime):
        return True
    return datetime.now(timezone.utc) - last_at >= timedelta(hours=ALERT_COOLDOWN_HOURS)


async def maybe_alert(kind: str = "blocked", waiting: int = 0) -> dict:
    """Odeme engeli ya da dogrulama gereken cekim icin admine uyari gonderir."""
    if not await _cooldown_passed(kind):
        return {"sent": False, "reason": "cooldown", "kind": kind}

    subject, html, wa_text = _alert_texts(kind, waiting, tamamliyo.card_configured())
    admin_email = (os.environ.get("ADMIN_EMAIL") or "").strip()
    email_result = {"status": "skipped"}
    if admin_email:
        email_result = await send_email(
            admin_email, subject, html, kind="insurance_payment_alert", meta={"kind": kind}
        )
    wa_result = await whatsapp.send_admin_text(wa_text, reason="insurance_payment_alert")

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
    logger.warning("tamamliyo odeme uyarisi gonderildi (%s, bekleyen: %s)", kind, waiting)
    return {"sent": True, "kind": kind, "email": email_result, "whatsapp": wa_result}
