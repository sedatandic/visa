"""Meta WhatsApp Cloud API istemcisi.

- Webhook dogrulama (hub.challenge + X-Hub-Signature-256)
- Serbest metin (24 saat servis penceresi), onayli sablon, belge gonderimi
- Gelen medyayi indirme, giden medyayi yukleme
- Resmi Groups API (Resmi Isletme Hesabi sarti, en fazla 8 katilimci)

Kimlik bilgileri yoksa `simulate` modunda calisir: gonderimler `wa_messages`
koleksiyonuna yazilir, boylece Meta onayi beklenirken akis uctan uca test edilir.
"""

import hashlib
import hmac
import logging
import os
import uuid
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

from db import db, settings_col

load_dotenv()

logger = logging.getLogger(__name__)

CLOUD_KEY = "whatsapp_cloud"
events_col = db["wa_events"]
messages_col = db["wa_messages"]

# (ayar anahtari, ortam degiskeni, varsayilan)
_TEXT_FIELDS: tuple[tuple[str, str | None, str], ...] = (
    ("phone_number_id", "META_PHONE_NUMBER_ID", ""),
    ("waba_id", "META_WABA_ID", ""),
    ("access_token", "META_ACCESS_TOKEN", ""),
    ("app_secret", "META_APP_SECRET", ""),
    ("verify_token", "META_VERIFY_TOKEN", "dubai-vize-hatti"),
    ("supplier_group_id", "META_SUPPLIER_GROUP_ID", ""),
    ("supplier_numbers", "META_SUPPLIER_NUMBERS", ""),
    ("graph_version", "META_GRAPH_VERSION", "v25.0"),
    ("visa_template_name", None, "vize_hazir"),
    ("visa_template_language", None, "tr"),
)

_BOOL_FIELDS: tuple[tuple[str, bool], ...] = (
    ("bot_enabled", True),
    ("auto_deliver", True),
)

_SECRET_KEYS = ("access_token", "app_secret")
EDITABLE_KEYS = tuple(key for key, _env, _default in _TEXT_FIELDS) + tuple(
    key for key, _default in _BOOL_FIELDS
)


async def config(masked: bool = True) -> dict:
    doc = await settings_col.find_one({"key": CLOUD_KEY})
    stored = (doc or {}).get("value") or {}
    cfg: dict = {}
    for key, env_key, default in _TEXT_FIELDS:
        value = stored.get(key) or (os.environ.get(env_key) if env_key else "") or default
        cfg[key] = value
    for key, default in _BOOL_FIELDS:
        cfg[key] = bool(stored.get(key, default))
    cfg["ready"] = bool(cfg["access_token"] and cfg["phone_number_id"])
    cfg["mode"] = "live" if cfg["ready"] else "simulate"
    # Imza dogrulamasi zorunlu: app_secret yoksa gelen webhook reddedilir.
    cfg["signature_ready"] = bool(cfg["app_secret"])
    if masked:
        for key in _SECRET_KEYS:
            cfg[f"has_{key}"] = bool(cfg[key])
            cfg[key] = ""
    return cfg


async def save_config(payload: dict) -> dict:
    doc = await settings_col.find_one({"key": CLOUD_KEY})
    value = dict((doc or {}).get("value") or {})
    for key in EDITABLE_KEYS:
        if key in _SECRET_KEYS:
            if payload.get(key):
                value[key] = payload[key].strip()
        elif payload.get(key) is not None:
            value[key] = payload[key]
    await settings_col.update_one(
        {"key": CLOUD_KEY}, {"$set": {"key": CLOUD_KEY, "value": value}}, upsert=True
    )
    return await config()


def supplier_numbers(cfg: dict) -> list[str]:
    raw = cfg.get("supplier_numbers") or ""
    return [n.strip().lstrip("+") for n in raw.replace(";", ",").split(",") if n.strip()]


def verify_signature(raw_body: bytes, header: str | None, app_secret: str) -> bool:
    """Meta imzasini dogrular. App secret tanimli degilse istek reddedilir (fail-closed)."""
    if not app_secret:
        logger.error("META_APP_SECRET tanimli degil; imzasiz webhook istegi reddedildi.")
        return False
    if not header or not header.startswith("sha256="):
        return False
    digest = hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, header.split("=", 1)[1])


async def log_event(kind: str, payload: dict) -> None:
    try:
        await events_col.insert_one(
            {
                "id": str(uuid.uuid4()),
                "kind": kind,
                "payload": payload,
                "created_at": datetime.now(timezone.utc),
            }
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("wa event log failed: %s", exc)


async def record_message(doc: dict) -> dict:
    entry = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc),
        **doc,
    }
    await messages_col.insert_one(dict(entry))
    return entry


async def _graph(cfg: dict, method: str, path: str, **kwargs) -> dict:
    url = f"https://graph.facebook.com/{cfg['graph_version']}/{path.lstrip('/')}"
    headers = {"Authorization": f"Bearer {cfg['access_token']}"}
    headers.update(kwargs.pop("headers", {}))
    async with httpx.AsyncClient(timeout=45) as client:
        res = await client.request(method, url, headers=headers, **kwargs)
    if res.is_error:
        await log_event("graph_error", {"path": path, "status": res.status_code, "body": res.text[:600]})
        return {"ok": False, "status": res.status_code, "error": res.text[:400]}
    try:
        return {"ok": True, **res.json()}
    except ValueError:
        return {"ok": True, "raw": res.content}


async def _send(cfg: dict, payload: dict, target: str, kind: str, preview: str) -> dict:
    if not cfg["ready"]:
        entry = await record_message(
            {
                "direction": "out",
                "target": target,
                "kind": kind,
                "text": preview,
                "status": "simulated",
                "payload": payload,
            }
        )
        return {"status": "simulated", "message_id": entry["id"]}

    result = await _graph(cfg, "POST", f"{cfg['phone_number_id']}/messages", json=payload)
    status = "sent" if result.get("ok") else "failed"
    message_id = ((result.get("messages") or [{}])[0]).get("id", "") if result.get("ok") else ""
    await record_message(
        {
            "direction": "out",
            "target": target,
            "kind": kind,
            "text": preview,
            "status": status,
            "wa_message_id": message_id,
            "error": result.get("error", ""),
        }
    )
    return {"status": status, "message_id": message_id, "error": result.get("error", "")}


def _recipient(target: str, is_group: bool) -> dict:
    if is_group:
        return {"recipient_type": "group", "to": target}
    return {"recipient_type": "individual", "to": target}


async def send_text(target: str, body: str, is_group: bool = False, cfg: dict | None = None) -> dict:
    cfg = cfg or await config(masked=False)
    payload = {
        "messaging_product": "whatsapp",
        **_recipient(target, is_group),
        "type": "text",
        "text": {"preview_url": True, "body": body[:4000]},
    }
    return await _send(cfg, payload, target, "text", body[:300])


async def send_document(
    target: str,
    *,
    media_id: str = "",
    link: str = "",
    filename: str = "belge.pdf",
    caption: str = "",
    is_group: bool = False,
    cfg: dict | None = None,
) -> dict:
    cfg = cfg or await config(masked=False)
    document: dict = {"filename": filename}
    if caption:
        document["caption"] = caption[:900]
    if media_id:
        document["id"] = media_id
    elif link:
        document["link"] = link
    payload = {
        "messaging_product": "whatsapp",
        **_recipient(target, is_group),
        "type": "document",
        "document": document,
    }
    return await _send(cfg, payload, target, "document", caption[:300] or filename)


async def send_template(
    target: str,
    name: str,
    language: str,
    components: list,
    cfg: dict | None = None,
) -> dict:
    cfg = cfg or await config(masked=False)
    payload = {
        "messaging_product": "whatsapp",
        **_recipient(target, False),
        "type": "template",
        "template": {"name": name, "language": {"code": language}, "components": components},
    }
    return await _send(cfg, payload, target, f"template:{name}", name)


async def upload_media(data: bytes, filename: str, mime: str, cfg: dict | None = None) -> str:
    cfg = cfg or await config(masked=False)
    if not cfg["ready"]:
        return ""
    result = await _graph(
        cfg,
        "POST",
        f"{cfg['phone_number_id']}/media",
        data={"messaging_product": "whatsapp"},
        files={"file": (filename, data, mime)},
    )
    return result.get("id", "") if result.get("ok") else ""


async def download_media(media_id: str, cfg: dict | None = None) -> dict:
    """Medya kimliginden dosya icerigini indirir."""
    cfg = cfg or await config(masked=False)
    if not cfg["ready"]:
        return {"ok": False, "reason": "not_configured"}
    meta = await _graph(cfg, "GET", media_id)
    if not meta.get("ok") or not meta.get("url"):
        return {"ok": False, "reason": "meta_failed", "detail": meta.get("error", "")}
    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        res = await client.get(meta["url"], headers={"Authorization": f"Bearer {cfg['access_token']}"})
    if res.is_error:
        return {"ok": False, "reason": "download_failed", "detail": res.text[:200]}
    return {
        "ok": True,
        "data": res.content,
        "mime": meta.get("mime_type") or res.headers.get("Content-Type", "application/octet-stream"),
        "size": len(res.content),
        "sha256": meta.get("sha256", ""),
    }


async def create_group(subject: str, cfg: dict | None = None) -> dict:
    """Resmi Groups API ile grup olusturur (Resmi Isletme Hesabi gerekir)."""
    cfg = cfg or await config(masked=False)
    if not cfg["ready"]:
        return {"ok": False, "reason": "not_configured"}
    result = await _graph(
        cfg, "POST", f"{cfg['phone_number_id']}/groups", json={"subject": subject[:100]}
    )
    if not result.get("ok"):
        return {"ok": False, "reason": "graph_error", "detail": result.get("error", "")}
    group_id = result.get("id") or result.get("group_id") or ""
    if group_id:
        await save_config({"supplier_group_id": group_id})
    return {"ok": True, "group_id": group_id, "invite_link": result.get("invite_link", "")}


async def group_invite_link(group_id: str, cfg: dict | None = None) -> dict:
    cfg = cfg or await config(masked=False)
    if not cfg["ready"]:
        return {"ok": False, "reason": "not_configured"}
    result = await _graph(cfg, "GET", f"{cfg['phone_number_id']}/groups/{group_id}/invite")
    if not result.get("ok"):
        return {"ok": False, "reason": "graph_error", "detail": result.get("error", "")}
    return {"ok": True, "invite_link": result.get("invite_link") or result.get("link", "")}
