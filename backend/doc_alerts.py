"""Pasaport okunamadiginda ekibe aninda alarm: panel karti + ekip WhatsApp'i + e-posta.

Amac: musteri formda takilip vazgecmeden once ekip telefonla devreye girsin.
"""

import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

import whatsapp
from db import notifications_col
from emailer import BRAND, send_email
from phone_format import format_phone

logger = logging.getLogger(__name__)

ALERT_KIND = "passport_unreadable"
THROTTLE_MINUTES = 10
REASON_LABELS = {
    "ai_error": "Yapay zeka okuma hatasi",
    "not_readable": "Goruntuden bilgiler okunamadi",
}


def _contact_key(contact: dict) -> str:
    return (contact.get("phone") or contact.get("email") or "").strip().lower()


async def _recently_alerted(file_id: str, key: str) -> bool:
    if await notifications_col.find_one({"kind": ALERT_KIND, "file_id": file_id}):
        return True
    if not key:
        return False
    since = datetime.now(timezone.utc) - timedelta(minutes=THROTTLE_MINUTES)
    return bool(
        await notifications_col.find_one(
            {"kind": ALERT_KIND, "contact_key": key, "created_at": {"$gt": since}}
        )
    )


def _alert_text(contact: dict, reason: str) -> str:
    name = contact.get("name") or "Isim girilmemis"
    phone = format_phone(contact.get("phone") or "") or "-"
    email = contact.get("email") or "-"
    return (
        f"{BRAND} · Pasaport okunamadi\n"
        f"Musteri: {name}\nTelefon: {phone}\nE-posta: {email}\n"
        f"Neden: {REASON_LABELS.get(reason, reason)}\n"
        "Musteri formda takilmis olabilir, hemen arayin."
    )


def _alert_html(contact: dict, reason: str) -> str:
    name = contact.get("name") or "Isim girilmemiş"
    phone = format_phone(contact.get("phone") or "") or "-"
    email = contact.get("email") or "-"
    return f"""
    <div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;color:#1b1b1b">
      <h2 style="margin:0 0 12px;font-size:18px">Pasaport okunamadı · müşteriyi arayın</h2>
      <p style="margin:0 0 12px">Bir müşteri pasaportunu yükledi ama otomatik okuma başarısız oldu.
      Form doldurmayı bırakmadan önce telefonla yardım edilmesi öneriliyor.</p>
      <table style="border-collapse:collapse">
        <tr><td style="padding:4px 12px 4px 0;color:#666">Müşteri</td><td style="padding:4px 0"><b>{name}</b></td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#666">Telefon</td><td style="padding:4px 0"><b>{phone}</b></td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#666">E-posta</td><td style="padding:4px 0">{email}</td></tr>
        <tr><td style="padding:4px 12px 4px 0;color:#666">Neden</td><td style="padding:4px 0">{REASON_LABELS.get(reason, reason)}</td></tr>
      </table>
      <p style="margin:14px 0 0;color:#666">Yönetim panelindeki "Pasaport okunamadı" kartından da takip edebilirsiniz.</p>
    </div>
    """


async def notify_unreadable_passport(file_id: str, reason: str, contact: dict) -> dict:
    """Alarm kaydini olusturur, ekip WhatsApp'i ve e-postasini tetikler."""
    key = _contact_key(contact)
    if await _recently_alerted(file_id, key):
        return {"status": "skipped"}

    alert = {
        "id": str(uuid.uuid4()),
        "kind": ALERT_KIND,
        "title": f"Pasaport okunamadı · {contact.get('name') or 'isim girilmemiş'}",
        "file_id": file_id,
        "reason": reason,
        "reason_label": REASON_LABELS.get(reason, reason),
        "contact": {
            "name": contact.get("name") or "",
            "phone": contact.get("phone") or "",
            "email": contact.get("email") or "",
        },
        "contact_key": key,
        "read": False,
        "created_at": datetime.now(timezone.utc),
    }
    await notifications_col.insert_one(dict(alert))

    text = _alert_text(contact, reason)
    try:
        wa = await whatsapp.send_admin_text(text, reason=ALERT_KIND)
    except Exception as exc:  # pragma: no cover - bildirim akisi basvuruyu bozmasin
        logger.warning("passport alert whatsapp failed: %s", exc)
        wa = {"status": "failed", "detail": str(exc)[:200]}

    admin_email = os.environ.get("ADMIN_EMAIL") or ""
    mail = {"status": "skipped", "reason": "ADMIN_EMAIL tanimli degil"}
    if admin_email:
        mail = await send_email(
            admin_email,
            f"{BRAND} · Pasaport okunamadı, müşteriyi arayın",
            _alert_html(contact, reason),
            kind=ALERT_KIND,
            meta={"file_id": file_id, "reason": reason},
        )

    await notifications_col.update_one(
        {"id": alert["id"]},
        {"$set": {"whatsapp": wa, "email": {"status": mail.get("status"), "to": admin_email}}},
    )
    logger.info("passport unreadable alert created: %s (wa=%s)", alert["id"], wa.get("status"))
    return {"status": "created", "id": alert["id"], "whatsapp": wa, "email": mail}
