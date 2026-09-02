"""WhatsApp bildirim servisi (vize sonucu).

Uc mod desteklenir:
- `manual`  : Kredi/anahtar gerekmez. Admin icin hazir metinli `wa.me` baglantisi uretir.
- `meta`    : Meta WhatsApp Cloud API (onayli sablon ile).
- `twilio`  : Twilio WhatsApp (Content Template SID ile).

Mesaj yalnizca vize sonucu (onay/ret) icin gonderilir.
"""

import logging
import os
import re
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

import httpx

from db import db, settings_col

logger = logging.getLogger(__name__)

SETTINGS_KEY = "whatsapp"
logs_col = db["whatsapp_logs"]

DEFAULT_TEMPLATE = (
    "Sayın {name}, Dubai vize başvurunuzun sonucu: {status}. "
    "Başvuru numaranız: {reference}. Detay: {link}"
)

STATUS_TEXT = {
    "approved": "Onaylandı",
    "rejected": "Reddedildi",
    "cancelled": "İptal edildi",
}

RESULT_STATUSES = {"approved", "rejected"}


def normalize_phone(raw: str | None) -> str | None:
    """Turk numaralarini E.164 formatina cevirir (+905XXXXXXXXX)."""
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return None
    if digits.startswith("0090"):
        digits = digits[2:]
    if digits.startswith("0"):
        digits = "90" + digits[1:]
    elif not digits.startswith("90"):
        digits = "90" + digits
    if not re.fullmatch(r"90[1-9]\d{9}", digits):
        return None
    return "+" + digits


async def get_settings(masked: bool = True) -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    value = (doc or {}).get("value") or {}
    data = {
        "enabled": bool(value.get("enabled", True)),
        "provider": value.get("provider") or "manual",
        "template_text": value.get("template_text") or DEFAULT_TEMPLATE,
        "only_optin": bool(value.get("only_optin", True)),
        "meta_phone_number_id": value.get("meta_phone_number_id") or os.environ.get("META_PHONE_NUMBER_ID", ""),
        "meta_template_name": value.get("meta_template_name") or "visa_status_update",
        "meta_template_language": value.get("meta_template_language") or "tr",
        "meta_api_version": value.get("meta_api_version") or "v23.0",
        "twilio_whatsapp_from": value.get("twilio_whatsapp_from") or os.environ.get("TWILIO_WHATSAPP_FROM", ""),
        "twilio_content_sid": value.get("twilio_content_sid") or os.environ.get("TWILIO_CONTENT_SID", ""),
        "twilio_account_sid": value.get("twilio_account_sid") or os.environ.get("TWILIO_ACCOUNT_SID", ""),
    }
    secrets_present = {
        "has_meta_token": bool(value.get("meta_access_token") or os.environ.get("META_ACCESS_TOKEN")),
        "has_twilio_token": bool(value.get("twilio_auth_token") or os.environ.get("TWILIO_AUTH_TOKEN")),
    }
    data.update(secrets_present)
    if not masked:
        data["meta_access_token"] = value.get("meta_access_token") or os.environ.get("META_ACCESS_TOKEN", "")
        data["twilio_auth_token"] = value.get("twilio_auth_token") or os.environ.get("TWILIO_AUTH_TOKEN", "")
    return data


async def save_settings(payload: dict) -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    current = (doc or {}).get("value") or {}
    value = dict(current)
    for key in (
        "enabled",
        "provider",
        "template_text",
        "only_optin",
        "meta_phone_number_id",
        "meta_template_name",
        "meta_template_language",
        "meta_api_version",
        "twilio_whatsapp_from",
        "twilio_content_sid",
        "twilio_account_sid",
    ):
        if payload.get(key) is not None:
            value[key] = payload[key]
    # sirlar yalnizca yeni deger geldiyse guncellenir
    for secret in ("meta_access_token", "twilio_auth_token"):
        if payload.get(secret):
            value[secret] = payload[secret]
    await settings_col.update_one(
        {"key": SETTINGS_KEY}, {"$set": {"key": SETTINGS_KEY, "value": value}}, upsert=True
    )
    return await get_settings()


def render_message(template: str, app_doc: dict, status: str, base_url: str) -> str:
    contact = app_doc.get("contact") or {}
    return (template or DEFAULT_TEMPLATE).format(
        name=contact.get("full_name", ""),
        status=STATUS_TEXT.get(status, status),
        reference=app_doc.get("reference_code", ""),
        link=f"{(base_url or '').rstrip('/')}/takip",
    )


def wa_link(phone: str, text: str) -> str:
    return f"https://wa.me/{phone.lstrip('+')}?text={quote(text)}"


async def _log(app_doc: dict, status: str, provider: str, result: str, detail: str = "", link: str = "") -> None:
    try:
        await logs_col.insert_one(
            {
                "id": str(uuid.uuid4()),
                "application_id": app_doc.get("id"),
                "reference_code": app_doc.get("reference_code"),
                "status": status,
                "provider": provider,
                "result": result,
                "detail": detail[:400],
                "link": link,
                "created_at": datetime.now(timezone.utc),
            }
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("whatsapp log failed: %s", exc)


async def _send_meta(cfg: dict, phone: str, app_doc: dict, status: str) -> dict:
    url = f"https://graph.facebook.com/{cfg['meta_api_version']}/{cfg['meta_phone_number_id']}/messages"
    contact = app_doc.get("contact") or {}
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "template",
        "template": {
            "name": cfg["meta_template_name"],
            "language": {"code": cfg["meta_template_language"]},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": contact.get("full_name", "")},
                        {"type": "text", "text": STATUS_TEXT.get(status, status)},
                        {"type": "text", "text": app_doc.get("reference_code", "")},
                    ],
                }
            ],
        },
    }
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {cfg['meta_access_token']}", "Content-Type": "application/json"},
        )
    if res.is_error:
        return {"status": "failed", "detail": f"Meta hatası: {res.status_code} {res.text[:200]}"}
    return {"status": "sent", "detail": (res.json().get("messages") or [{}])[0].get("id", "")}


async def _send_twilio(cfg: dict, phone: str, app_doc: dict, status: str) -> dict:
    import json as _json

    contact = app_doc.get("contact") or {}
    url = f"https://api.twilio.com/2010-04-01/Accounts/{cfg['twilio_account_sid']}/Messages.json"
    data = {
        "From": cfg["twilio_whatsapp_from"],
        "To": f"whatsapp:{phone}",
        "ContentSid": cfg["twilio_content_sid"],
        "ContentVariables": _json.dumps(
            {
                "1": contact.get("full_name", ""),
                "2": STATUS_TEXT.get(status, status),
                "3": app_doc.get("reference_code", ""),
            },
            ensure_ascii=False,
        ),
    }
    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(
            url, data=data, auth=(cfg["twilio_account_sid"], cfg["twilio_auth_token"])
        )
    if res.is_error:
        return {"status": "failed", "detail": f"Twilio hatası: {res.status_code} {res.text[:200]}"}
    return {"status": "sent", "detail": res.json().get("sid", "")}


async def notify_result(app_doc: dict, status: str, base_url: str = "", force: bool = False) -> dict:
    """Vize sonucu icin WhatsApp bildirimi (moda gore API veya hazir baglanti)."""
    cfg = await get_settings(masked=False)
    contact = app_doc.get("contact") or {}
    phone = normalize_phone(contact.get("phone"))
    text = render_message(cfg["template_text"], app_doc, status, base_url)

    if status not in RESULT_STATUSES and not force:
        return {"status": "skipped", "reason": "Sadece vize sonucu bildirimleri gönderilir."}
    if not cfg["enabled"] and not force:
        return {"status": "skipped", "reason": "WhatsApp bildirimi kapalı."}
    if not phone:
        await _log(app_doc, status, cfg["provider"], "invalid_phone", contact.get("phone", ""))
        return {"status": "failed", "reason": "Geçerli bir Türk cep telefonu numarası bulunamadı."}
    if cfg["only_optin"] and not app_doc.get("whatsapp_optin") and not force:
        link = wa_link(phone, text)
        await _log(app_doc, status, "manual", "optin_missing", "", link)
        return {
            "status": "manual",
            "reason": "Müşteri WhatsApp bilgilendirme onayı vermedi; hazır bağlantı ile elle gönderebilirsiniz.",
            "link": link,
            "message": text,
            "phone": phone,
        }

    provider = cfg["provider"]
    try:
        if provider == "meta" and cfg.get("meta_access_token") and cfg.get("meta_phone_number_id"):
            out = await _send_meta(cfg, phone, app_doc, status)
        elif provider == "twilio" and cfg.get("twilio_auth_token") and cfg.get("twilio_account_sid"):
            out = await _send_twilio(cfg, phone, app_doc, status)
        else:
            link = wa_link(phone, text)
            await _log(app_doc, status, "manual", "manual_link", "", link)
            return {
                "status": "manual",
                "reason": "Manuel mod: hazır WhatsApp bağlantısı oluşturuldu.",
                "link": link,
                "message": text,
                "phone": phone,
            }
    except Exception as exc:
        logger.error("whatsapp send failed: %s", exc)
        out = {"status": "failed", "detail": str(exc)[:200]}

    await _log(app_doc, status, provider, out["status"], out.get("detail", ""))
    return {
        "status": out["status"],
        "provider": provider,
        "detail": out.get("detail", ""),
        "message": text,
        "phone": phone,
        "link": wa_link(phone, text),
    }
