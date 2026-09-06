"""Zami portal OTP hatirlaticisi.

Zami oturumu, ilk OTP'li giristen sonra "trusted device" cerezi sayesinde
kendini otomatik yeniler. Bu guven suresi ~30 gun oldugu icin OTP'yi ayda bir
girmek gerekir. Bu modul, tarih yaklastiginda (veya portal OTP istediginde)
yoneticiyi e-posta ve WhatsApp ile onceden uyarir.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

import whatsapp
from db import settings_col
from emailer import send_email
from zami import SESSION_KEY

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 6 * 3600  # 6 saatte bir kontrol
UPCOMING_WINDOW_DAYS = 3  # OTP tarihine 3 gun kalinca uyar
RESEND_AFTER_HOURS = 24  # ayni uyariyi en fazla gunde bir yinele

ADMIN_PANEL_HINT = "Admin → Zami Aktarım → Robot Oturumu → Oturum Başlat"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def decide_reminder(session: dict, state: dict, now: datetime | None = None) -> str | None:
    """Hangi hatirlatmanin gonderilecegini belirler (saf fonksiyon).

    Donen deger: "due_now" | "upcoming" | None
    - due_now: portal OTP istiyor, oturum otomatik yenilenemiyor.
    - upcoming: cihaz guveni sonu 3 gunden az kaldi.
    """
    now = now or _now()
    kind = None
    if session.get("otp_required"):
        kind = "due_now"
    else:
        due = _parse(session.get("next_otp_due"))
        if due and due - now <= timedelta(days=UPCOMING_WINDOW_DAYS):
            kind = "upcoming"
    if kind is None:
        return None

    last_kind = state.get("otp_reminder_kind")
    last_sent = _parse(state.get("otp_reminder_sent_at"))
    if last_kind == kind and last_sent and now - last_sent < timedelta(hours=RESEND_AFTER_HOURS):
        return None
    return kind


def _texts(kind: str, session: dict) -> tuple[str, str, str]:
    """(konu, e-posta html, whatsapp metni)"""
    due = _parse(session.get("next_otp_due"))
    due_text = due.strftime("%d.%m.%Y") if due else "-"
    if kind == "due_now":
        subject = "Zami portalı OTP kodu gerekiyor"
        headline = "Zami portalı şu anda OTP kodu istiyor."
        detail = (
            "Robot oturumu otomatik yenileyemedi. Aktarım ve otomatik durum takibinin "
            "kesintisiz sürmesi için bir kez giriş yapmanız gerekiyor."
        )
        wa_text = (
            "Dubai Vize Hattı: Zami portalı OTP kodu istiyor. "
            f"Robot oturumunu yenilemek için panelden giriş yapın ({ADMIN_PANEL_HINT})."
        )
    else:
        subject = "Zami portalı OTP yenileme tarihi yaklaşıyor"
        headline = f"Zami cihaz güveni {due_text} tarihinde sona eriyor."
        detail = (
            "Oturumun kesintisiz devam etmesi için bu tarihe kadar bir kez OTP ile "
            "giriş yapmanız yeterli. Girişten sonra robot yeniden 1 ay boyunca "
            "OTP'siz çalışır."
        )
        wa_text = (
            f"Dubai Vize Hattı: Zami OTP yenileme tarihi yaklaşıyor ({due_text}). "
            f"Panelden bir kez giriş yapmanız yeterli ({ADMIN_PANEL_HINT})."
        )
    html = (
        '<div style="font-family:Arial,sans-serif;font-size:14px;color:#222">'
        f"<p><b>{headline}</b></p><p>{detail}</p>"
        f"<p>{ADMIN_PANEL_HINT}</p>"
        '<p style="color:#555">Captcha otomatik okunur; yalnızca e-postanıza gelen '
        "OTP kodunu girmeniz gerekir.</p></div>"
    )
    return subject, html, wa_text


async def _mark_sent(kind: str, wa_result: dict) -> None:
    await settings_col.update_one(
        {"key": SESSION_KEY},
        {
            "$set": {
                "value.otp_reminder_kind": kind,
                "value.otp_reminder_sent_at": _now().isoformat(),
                "value.otp_reminder_wa_link": wa_result.get("link", ""),
                "value.otp_reminder_wa_status": wa_result.get("status", ""),
            }
        },
        upsert=True,
    )


async def send_reminder(kind: str, session: dict) -> dict:
    """OTP hatirlatmasini e-posta + WhatsApp ile gonderir."""
    subject, html, wa_text = _texts(kind, session)
    email_status = "skipped"
    admin_email = os.environ.get("ADMIN_EMAIL")
    if admin_email:
        try:
            await send_email(admin_email, subject, html, kind="zami_otp_reminder")
            email_status = "sent"
        except Exception as exc:
            logger.warning("otp reminder email failed: %s", exc)
            email_status = "error"

    try:
        wa_result = await whatsapp.send_admin_text(wa_text, reason="zami_otp_reminder")
    except Exception as exc:
        logger.warning("otp reminder whatsapp failed: %s", exc)
        wa_result = {"status": "failed", "reason": str(exc)[:200]}

    await _mark_sent(kind, wa_result)
    return {
        "ok": True,
        "kind": kind,
        "email": email_status,
        "whatsapp": wa_result.get("status"),
        "whatsapp_link": wa_result.get("link", ""),
    }


async def check_and_notify(force_kind: str = "") -> dict:
    """Tek kontrol adimi; gerekiyorsa hatirlatma gonderir."""
    import zami_rpa

    session = await zami_rpa.session_status()
    doc = await settings_col.find_one({"key": SESSION_KEY})
    state = (doc or {}).get("value") or {}
    kind = force_kind or decide_reminder(session, state)
    if not kind:
        return {"ok": True, "kind": None, "reason": "reminder_not_due"}
    return await send_reminder(kind, session)


async def reminder_loop():
    """Arka plan dongusu: 6 saatte bir OTP hatirlatma kontrolu."""
    await asyncio.sleep(150)
    while True:
        try:
            out = await check_and_notify()
            if out.get("kind"):
                logger.info("zami otp reminder sent: %s", out)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("otp reminder loop error: %s", exc)
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
