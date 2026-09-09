"""WhatsApp Cloud API webhook'u ve admin yonetim uclari.

- `GET  /api/whatsapp/webhook`  : Meta dogrulama (hub.challenge)
- `POST /api/whatsapp/webhook`  : gelen mesajlar (musteri sohbeti + tedarikci belgeleri)
- `/api/admin/whatsapp/ai/*`    : ayarlar, konusmalar, belge kuyrugu, grup kurulumu, simulator
"""

import logging
import re
import time
from datetime import datetime, timezone
from hmac import compare_digest
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

import wa_bot
import wa_cloud
import wa_docs
from admin_auth import require_admin
from db import applications_col, conversations_col, serialize_doc, wa_documents_col

logger = logging.getLogger(__name__)
router = APIRouter()

DOCUMENT_TYPES = ("document", "image")

# Webhook hiz siniri: imza gecerli olsa da dakikada en fazla bu kadar olay islenir
# (LLM ve mesaj maliyetini sinirlar).
WEBHOOK_WINDOW_SECONDS = 60
WEBHOOK_MAX_EVENTS = 120
_webhook_hits: list[float] = []


def _webhook_rate_ok() -> bool:
    now = time.monotonic()
    cutoff = now - WEBHOOK_WINDOW_SECONDS
    while _webhook_hits and _webhook_hits[0] < cutoff:
        _webhook_hits.pop(0)
    if len(_webhook_hits) >= WEBHOOK_MAX_EVENTS:
        return False
    _webhook_hits.append(now)
    return True


# ---------------------------------------------------------------- webhook
@router.get("/whatsapp/webhook", response_class=PlainTextResponse)
async def verify_webhook(request: Request) -> PlainTextResponse:
    params = request.query_params
    cfg = await wa_cloud.config(masked=False)
    token_ok = compare_digest(params.get("hub.verify_token") or "", cfg["verify_token"] or "")
    if params.get("hub.mode") == "subscribe" and token_ok:
        return PlainTextResponse(params.get("hub.challenge", ""))
    raise HTTPException(403, "Dogrulama basarisiz.")


@router.post("/whatsapp/webhook")
async def receive_webhook(request: Request, background: BackgroundTasks) -> dict:
    raw = await request.body()
    cfg = await wa_cloud.config(masked=False)
    if not wa_cloud.verify_signature(raw, request.headers.get("X-Hub-Signature-256"), cfg["app_secret"]):
        await wa_cloud.log_event("webhook_rejected", {"reason": "invalid_signature", "size": len(raw)})
        raise HTTPException(403, "Imza dogrulanamadi.")
    if not _webhook_rate_ok():
        await wa_cloud.log_event("webhook_rejected", {"reason": "rate_limited"})
        raise HTTPException(429, "Cok fazla webhook istegi.")
    try:
        payload = await request.json()
    except ValueError:
        payload = {}
    await wa_cloud.log_event("webhook", payload)
    background.add_task(handle_webhook_payload, payload)
    return {"received": True}


def _iter_messages(payload: dict):
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            value = change.get("value") or {}
            contacts = {c.get("wa_id"): c for c in value.get("contacts") or []}
            for message in value.get("messages") or []:
                yield message, contacts.get(message.get("from"), {}), value


def _group_id(message: dict, value: dict) -> str:
    for source in (message, value, message.get("context") or {}):
        for key in ("group_id", "group_jid", "group"):
            found = source.get(key)
            if isinstance(found, str) and found:
                return found
            if isinstance(found, dict) and found.get("id"):
                return found["id"]
    return ""


def _message_text(message: dict) -> str:
    kind = message.get("type")
    if kind == "text":
        return (message.get("text") or {}).get("body", "")
    if kind == "button":
        return (message.get("button") or {}).get("text", "")
    if kind == "interactive":
        interactive = message.get("interactive") or {}
        for key in ("button_reply", "list_reply"):
            if interactive.get(key):
                return interactive[key].get("title", "")
    return ""


async def handle_webhook_payload(payload: dict) -> None:
    cfg = await wa_cloud.config(masked=False)
    for message, contact, value in _iter_messages(payload):
        try:
            await _handle_message(message, contact, value, cfg)
        except Exception as exc:  # pragma: no cover
            logger.error("wa message handling failed: %s", exc)
            await wa_cloud.log_event("handle_error", {"error": str(exc)[:400], "message": message})


async def _handle_message(message: dict, contact: dict, value: dict, cfg: dict) -> None:
    wa_id = (message.get("from") or "").lstrip("+")
    group_id = _group_id(message, value)
    kind = message.get("type", "")
    profile_name = ((contact.get("profile") or {}).get("name")) or ""

    is_supplier_group = bool(group_id) and (
        not cfg.get("supplier_group_id") or group_id == cfg["supplier_group_id"]
    )
    is_supplier_direct = wa_id in wa_cloud.supplier_numbers(cfg)

    if kind in DOCUMENT_TYPES and (is_supplier_group or is_supplier_direct):
        await _handle_supplier_document(message, wa_id, group_id, kind, cfg)
        return

    if group_id:
        return  # grup icindeki metin mesajlarina bot yanit vermez

    await _handle_customer_message(message, wa_id, profile_name, kind, cfg)


async def _handle_supplier_document(message: dict, wa_id: str, group_id: str, kind: str, cfg: dict) -> None:
    media = message.get(kind) or {}
    media_id = media.get("id", "")
    filename = media.get("filename") or f"belge-{media_id[:8]}.pdf"
    downloaded = await wa_cloud.download_media(media_id, cfg=cfg)
    if not downloaded.get("ok"):
        await wa_cloud.log_event("media_download_failed", {"media_id": media_id, "detail": downloaded})
        return

    result = await wa_docs.process_incoming_document(
        data=downloaded["data"],
        mime=downloaded.get("mime") or media.get("mime_type", ""),
        filename=filename,
        source="group" if group_id else "supplier_direct",
        from_wa_id=wa_id,
        group_id=group_id,
        media_id=media_id,
    )

    target, is_group = (group_id, True) if group_id else (wa_id, False)
    match = result.get("match") or {}
    if result.get("status") == "delivered":
        note = (
            f"Belge alındı ve {match.get('reference_code', '')} numaralı başvuru sahibine "
            "WhatsApp + e-posta ile iletildi. Teşekkürler."
        )
    elif result.get("status") == "pending_review":
        note = "Belge alındı ancak hangi başvuruya ait olduğunu netleştirmemiz gerekiyor; ekibimiz kontrol ediyor."
    else:
        note = "Belge alındı ancak okunamadı. Lütfen daha net bir kopya paylaşabilir misiniz?"
    await wa_cloud.send_text(target, note, is_group=is_group, cfg=cfg)


async def _handle_customer_message(message: dict, wa_id: str, profile_name: str, kind: str, cfg: dict) -> None:
    conversation = await wa_bot.get_conversation(wa_id, profile_name)
    text = _message_text(message)
    if not text:
        text = f"[{kind} mesajı]"
    await wa_bot.append_message(wa_id, "user", text, {"type": kind})

    if not cfg.get("bot_enabled", True) or not conversation.get("bot_enabled", True):
        return
    if conversation.get("needs_human"):
        return

    conversation = await conversations_col.find_one({"wa_id": wa_id}) or conversation
    reply = await wa_bot.build_reply(conversation, text)
    sent = await wa_cloud.send_text(wa_id, reply["text"], cfg=cfg)
    await wa_bot.append_message(
        wa_id, "assistant", reply["text"], {"source": reply["source"], "status": sent.get("status")}
    )
    if reply["needs_human"]:
        await conversations_col.update_one(
            {"wa_id": wa_id},
            {"$set": {"needs_human": True, "handoff_at": datetime.now(timezone.utc)}},
        )


# ---------------------------------------------------------------- admin: ayarlar
class CloudConfigIn(BaseModel):
    phone_number_id: Optional[str] = None
    waba_id: Optional[str] = None
    access_token: Optional[str] = None
    app_secret: Optional[str] = None
    verify_token: Optional[str] = None
    supplier_group_id: Optional[str] = None
    supplier_numbers: Optional[str] = None
    graph_version: Optional[str] = None
    visa_template_name: Optional[str] = None
    visa_template_language: Optional[str] = None
    bot_enabled: Optional[bool] = None
    auto_deliver: Optional[bool] = None


@router.get("/admin/whatsapp/ai/config")
async def get_cloud_config(admin: dict = Depends(require_admin)) -> dict:
    cfg = await wa_cloud.config()
    cfg["webhook_url"] = "/api/whatsapp/webhook"
    return cfg


@router.put("/admin/whatsapp/ai/config")
async def update_cloud_config(payload: CloudConfigIn, admin: dict = Depends(require_admin)) -> dict:
    return await wa_cloud.save_config(payload.model_dump(exclude_none=True))


@router.post("/admin/whatsapp/ai/group")
async def create_supplier_group(
    subject: str = Form("Dubai Vize Hatti - Tedarikci Belgeleri"),
    admin: dict = Depends(require_admin),
) -> dict:
    result = await wa_cloud.create_group(subject)
    if not result.get("ok"):
        raise HTTPException(
            400,
            "Grup olusturulamadi. Resmi Isletme Hesabi (mavi tik) ve gecerli erisim anahtari gerekir. "
            f"Detay: {result.get('detail') or result.get('reason')}",
        )
    return result


@router.get("/admin/whatsapp/ai/group/invite")
async def get_group_invite(admin: dict = Depends(require_admin)) -> dict:
    cfg = await wa_cloud.config(masked=False)
    if not cfg.get("supplier_group_id"):
        raise HTTPException(400, "Once grup olusturun.")
    result = await wa_cloud.group_invite_link(cfg["supplier_group_id"])
    if not result.get("ok"):
        raise HTTPException(400, result.get("detail") or "Davet baglantisi alinamadi.")
    return result


# ---------------------------------------------------------------- admin: konusmalar
@router.get("/admin/whatsapp/ai/conversations")
async def list_conversations(admin: dict = Depends(require_admin)) -> dict:
    docs = await conversations_col.find({}).sort("updated_at", -1).to_list(200)
    items = []
    for doc in serialize_doc(docs):
        messages = doc.get("messages") or []
        items.append(
            {
                "id": doc.get("id"),
                "wa_id": doc.get("wa_id"),
                "profile_name": doc.get("profile_name", ""),
                "bot_enabled": doc.get("bot_enabled", True),
                "needs_human": doc.get("needs_human", False),
                "message_count": doc.get("message_count", len(messages)),
                "last_message": (messages[-1].get("text", "") if messages else "")[:160],
                "last_inbound_at": doc.get("last_inbound_at"),
                "updated_at": doc.get("updated_at"),
            }
        )
    return {"items": items, "waiting": sum(1 for i in items if i["needs_human"])}


@router.get("/admin/whatsapp/ai/conversations/{wa_id}")
async def get_conversation_detail(wa_id: str, admin: dict = Depends(require_admin)) -> dict:
    doc = await conversations_col.find_one({"wa_id": wa_id})
    if not doc:
        raise HTTPException(404, "Konusma bulunamadi.")
    return serialize_doc(doc)


class ReplyIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=900)


@router.post("/admin/whatsapp/ai/conversations/{wa_id}/reply")
async def reply_to_conversation(
    wa_id: str, payload: ReplyIn, admin: dict = Depends(require_admin)
) -> dict:
    doc = await conversations_col.find_one({"wa_id": wa_id})
    if not doc:
        raise HTTPException(404, "Konusma bulunamadi.")
    if not wa_bot.within_service_window(doc):
        raise HTTPException(
            400,
            "24 saatlik servis penceresi kapali. Musteri tekrar yazana kadar onayli sablon gerekir.",
        )
    sent = await wa_cloud.send_text(wa_id, payload.text)
    await wa_bot.append_message(wa_id, "agent", payload.text, {"status": sent.get("status")})
    await conversations_col.update_one({"wa_id": wa_id}, {"$set": {"needs_human": False}})
    return {"sent": sent}


class BotToggleIn(BaseModel):
    bot_enabled: bool


@router.post("/admin/whatsapp/ai/conversations/{wa_id}/bot")
async def toggle_conversation_bot(
    wa_id: str, payload: BotToggleIn, admin: dict = Depends(require_admin)
) -> dict:
    result = await conversations_col.update_one(
        {"wa_id": wa_id},
        {"$set": {"bot_enabled": payload.bot_enabled, "needs_human": not payload.bot_enabled}},
    )
    if not result.matched_count:
        raise HTTPException(404, "Konusma bulunamadi.")
    return {"bot_enabled": payload.bot_enabled}


# ---------------------------------------------------------------- admin: belge kuyrugu
@router.get("/admin/whatsapp/ai/documents")
async def list_wa_documents(status: Optional[str] = None, admin: dict = Depends(require_admin)) -> dict:
    query = {"status": status} if status else {}
    docs = await wa_documents_col.find(query).sort("created_at", -1).to_list(200)
    return {"items": serialize_doc(docs)}


class AssignIn(BaseModel):
    application_id: str


@router.post("/admin/whatsapp/ai/documents/{document_id}/assign")
async def assign_wa_document(
    document_id: str, payload: AssignIn, admin: dict = Depends(require_admin)
) -> dict:
    result = await wa_docs.deliver_pending(document_id, payload.application_id)
    if not result.get("ok"):
        raise HTTPException(400, f"Gonderilemedi: {result.get('reason')}")
    return result


@router.post("/admin/whatsapp/ai/documents/{document_id}/reject")
async def reject_wa_document(document_id: str, admin: dict = Depends(require_admin)) -> dict:
    result = await wa_documents_col.update_one(
        {"id": document_id},
        {"$set": {"status": "rejected", "updated_at": datetime.now(timezone.utc)}},
    )
    if not result.matched_count:
        raise HTTPException(404, "Belge bulunamadi.")
    return {"status": "rejected"}


# ---------------------------------------------------------------- admin: simulator
class SimulateTextIn(BaseModel):
    wa_id: str = Field(..., min_length=8, max_length=20)
    text: str = Field(..., min_length=1, max_length=900)
    profile_name: Optional[str] = ""


@router.post("/admin/whatsapp/ai/simulate/message")
async def simulate_message(payload: SimulateTextIn, admin: dict = Depends(require_admin)) -> dict:
    """Meta onayi beklenirken musteri mesaji simule eder (gercek gonderim yapilmaz)."""
    cfg = await wa_cloud.config(masked=False)
    await _handle_customer_message(
        {"type": "text", "from": payload.wa_id, "text": {"body": payload.text}},
        payload.wa_id.lstrip("+"),
        payload.profile_name or "",
        "text",
        cfg,
    )
    doc = await conversations_col.find_one({"wa_id": payload.wa_id.lstrip("+")})
    messages = (doc or {}).get("messages") or []
    return {"reply": messages[-1] if messages else None, "conversation": serialize_doc(doc or {})}


@router.post("/admin/whatsapp/ai/simulate/document")
async def simulate_document(
    file: UploadFile = File(...),
    from_wa_id: str = Form("905000000000"),
    admin: dict = Depends(require_admin),
) -> dict:
    """Tedarikci belgesini elle yukleyip eslestirme akisini test eder."""
    data = await file.read()
    if not data:
        raise HTTPException(400, "Dosya bos.")
    return await wa_docs.process_incoming_document(
        data=data,
        mime=file.content_type or "application/pdf",
        filename=file.filename or "belge.pdf",
        source="admin_upload",
        from_wa_id=from_wa_id,
    )


@router.get("/admin/whatsapp/ai/applications")
async def search_applications(q: str = "", admin: dict = Depends(require_admin)) -> dict:
    """Belge atamasi icin basvuru arama (kod, ad, soyad, pasaport)."""
    query: dict = {}
    if q:
        term = re.escape(q.strip())[:80]
        query = {
            "$or": [
                {"reference_code": {"$regex": term, "$options": "i"}},
                {"travelers.first_name": {"$regex": term, "$options": "i"}},
                {"travelers.last_name": {"$regex": term, "$options": "i"}},
                {"travelers.passport_no": {"$regex": term, "$options": "i"}},
                {"contact.email": {"$regex": term, "$options": "i"}},
            ]
        }
    docs = await applications_col.find(query).sort("created_at", -1).to_list(30)
    items = []
    for doc in serialize_doc(docs):
        traveler = (doc.get("travelers") or [{}])[0]
        items.append(
            {
                "id": doc.get("id"),
                "reference_code": doc.get("reference_code"),
                "status": doc.get("status"),
                "name": f"{traveler.get('first_name', '')} {traveler.get('last_name', '')}".strip(),
                "passport_no": traveler.get("passport_no", ""),
                "email": (doc.get("contact") or {}).get("email", ""),
                "created_at": doc.get("created_at"),
            }
        )
    return {"items": items}
