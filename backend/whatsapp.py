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


# Metin ayarlari: (anahtar, varsayilan, ortam degiskeni)
# Oncelik sirasi: DB ayari -> ortam degiskeni -> varsayilan.
_SETTING_FIELDS: tuple[tuple[str, str, str | None], ...] = (
    ("provider", "manual", None),
    ("template_text", DEFAULT_TEMPLATE, None),
    ("meta_phone_number_id", "", "META_PHONE_NUMBER_ID"),
    ("meta_template_name", "visa_status_update", None),
    ("meta_template_language", "tr", None),
    ("meta_api_version", "v23.0", None),
    ("twilio_whatsapp_from", "", "TWILIO_WHATSAPP_FROM"),
    ("twilio_content_sid", "", "TWILIO_CONTENT_SID"),
    ("twilio_account_sid", "", "TWILIO_ACCOUNT_SID"),
)

# Gizli ayarlar: (anahtar, ortam degiskeni, "var mi" bayragi)
_SECRET_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("meta_access_token", "META_ACCESS_TOKEN", "has_meta_token"),
    ("twilio_auth_token", "TWILIO_AUTH_TOKEN", "has_twilio_token"),
)

# Admin panelinden guncellenebilen (gizli olmayan) ayar anahtarlari
_EDITABLE_KEYS: tuple[str, ...] = ("enabled", "only_optin") + tuple(
    key for key, _default, _env in _SETTING_FIELDS
)


def _setting_value(stored: dict, key: str, default: str, env_key: str | None) -> str:
    """Tek bir metin ayarini oncelik sirasina gore cozer."""
    if stored.get(key):
        return stored[key]
    if env_key and os.environ.get(env_key):
        return os.environ[env_key]
    return default


def _secret_value(stored: dict, key: str, env_key: str) -> str:
    """Gizli ayari DB'den, yoksa ortam degiskeninden okur."""
    return stored.get(key) or os.environ.get(env_key, "")


async def get_settings(masked: bool = True) -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    value = (doc or {}).get("value") or {}
    data: dict = {
        "enabled": bool(value.get("enabled", True)),
        "only_optin": bool(value.get("only_optin", True)),
    }
    for key, default, env_key in _SETTING_FIELDS:
        data[key] = _setting_value(value, key, default, env_key)
    for key, env_key, flag in _SECRET_FIELDS:
        secret = _secret_value(value, key, env_key)
        data[flag] = bool(secret)
        if not masked:
            data[key] = secret
    return data


async def save_settings(payload: dict) -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    current = (doc or {}).get("value") or {}
    value = dict(current)
    for key in _EDITABLE_KEYS:
        if payload.get(key) is not None:
            value[key] = payload[key]
    # sirlar yalnizca yeni deger geldiyse guncellenir
    for secret, _env_key, _flag in _SECRET_FIELDS:
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


def _manual_response(phone: str, text: str, reason: str) -> dict:
    """Manuel mod yaniti: admin'in tek tikla gonderebilecegi wa.me baglantisi."""
    return {
        "status": "manual",
        "reason": reason,
        "link": wa_link(phone, text),
        "message": text,
        "phone": phone,
    }


async def _delivery_block(
    app_doc: dict, cfg: dict, status: str, phone: str | None, text: str, force: bool
) -> dict | None:
    """Gonderim oncesi kontroller. Engel varsa hazir yanit, yoksa None doner."""
    if status not in RESULT_STATUSES and not force:
        return {"status": "skipped", "reason": "Sadece vize sonucu bildirimleri gönderilir."}
    if not cfg["enabled"] and not force:
        return {"status": "skipped", "reason": "WhatsApp bildirimi kapalı."}
    if not phone:
        contact = app_doc.get("contact") or {}
        await _log(app_doc, status, cfg["provider"], "invalid_phone", contact.get("phone", ""))
        return {"status": "failed", "reason": "Geçerli bir Türk cep telefonu numarası bulunamadı."}
    if cfg["only_optin"] and not app_doc.get("whatsapp_optin") and not force:
        response = _manual_response(
            phone,
            text,
            "Müşteri WhatsApp bilgilendirme onayı vermedi; hazır bağlantı ile elle gönderebilirsiniz.",
        )
        await _log(app_doc, status, "manual", "optin_missing", "", response["link"])
        return response
    return None


# Saglayici -> (gonderici fonksiyon, zorunlu ayar anahtarlari)
_PROVIDERS = {
    "meta": (_send_meta, ("meta_access_token", "meta_phone_number_id")),
    "twilio": (_send_twilio, ("twilio_auth_token", "twilio_account_sid")),
}


def _provider_sender(cfg: dict):
    """Secili saglayici hazirsa gonderici fonksiyonunu, degilse None dondurur."""
    sender, required = _PROVIDERS.get(cfg.get("provider"), (None, ()))
    if sender and all(cfg.get(key) for key in required):
        return sender
    return None


async def notify_result(app_doc: dict, status: str, base_url: str = "", force: bool = False) -> dict:
    """Vize sonucu icin WhatsApp bildirimi (moda gore API veya hazir baglanti)."""
    cfg = await get_settings(masked=False)
    contact = app_doc.get("contact") or {}
    phone = normalize_phone(contact.get("phone"))
    text = render_message(cfg["template_text"], app_doc, status, base_url)

    blocked = await _delivery_block(app_doc, cfg, status, phone, text, force)
    if blocked is not None:
        return blocked

    provider = cfg["provider"]
    sender = _provider_sender(cfg)
    if sender is None:
        response = _manual_response(phone, text, "Manuel mod: hazır WhatsApp bağlantısı oluşturuldu.")
        await _log(app_doc, status, "manual", "manual_link", "", response["link"])
        return response

    try:
        out = await sender(cfg, phone, app_doc, status)
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
