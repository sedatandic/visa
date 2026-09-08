"""Tedarikci belgelerini WhatsApp'tan alip dogru basvuruya ileten otomasyon.

Akis:
1. Tedarikci, vize/sigorta belgesini WhatsApp grubuna (veya is numarasina) atar.
2. Webhook belgeyi indirir, yapay zeka belgenin icindeki bilgileri okur
   (pasaport no, ad-soyad, basvuru kodu, vize/police numarasi).
3. Bilgiler basvurularla eslestirilir. Guven yuksekse belge musteriye WhatsApp +
   e-posta ile otomatik gonderilir; degilse admin panelinde onay kuyruguna dusar.
"""

import base64
import io
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

import file_access
import wa_cloud
from db import applications_col, serialize_doc, uploads_col, wa_documents_col
from emailer import send_email, visa_ready_html
from application_docs import visa_pdf_attachment
from storage import APP_NAME, put_object

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-5.4"
AUTO_MIN_CONFIDENCE = 0.6

SYSTEM_PROMPT = (
    "Sen seyahat belgelerini okuyan bir belge analiz asistanisin. Sana verilen goruntu bir "
    "Dubai (BAE) e-vizesi, vize onay belgesi veya seyahat sagligi sigortasi policesi olabilir. "
    "Belgedeki yazili alanlari oku ve SADECE gecerli JSON dondur."
)

USER_PROMPT = """Bu belgeden asagidaki alanlari cikar ve tam olarak su JSON semasinda dondur:

{
  "document_kind": "visa | insurance | other",
  "first_name": "belgedeki ad (buyuk harf, Turkce karakter kullanma), okunamazsa bos",
  "last_name": "belgedeki soyad (buyuk harf, Turkce karakter kullanma), okunamazsa bos",
  "passport_no": "pasaport numarasi, okunamazsa bos",
  "reference_code": "belgede DV- ile baslayan basvuru kodu varsa, yoksa bos",
  "document_no": "vize numarasi veya police numarasi, okunamazsa bos",
  "valid_from": "gecerlilik baslangici YYYY-MM-DD, okunamazsa bos",
  "valid_to": "gecerlilik bitisi YYYY-MM-DD, okunamazsa bos",
  "birth_date": "dogum tarihi YYYY-MM-DD, okunamazsa bos",
  "confidence": 0.0 ile 1.0 arasinda okuma guveni
}

Kurallar:
- Tarihleri YYYY-MM-DD formatina cevir.
- Emin olmadigin alanlari bos string birak, kesinlikle uydurma.
- Sadece JSON dondur."""


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


def _pdf_first_pages_png(data: bytes, max_pages: int = 2) -> list[bytes]:
    import pymupdf

    images = []
    with pymupdf.open(stream=data, filetype="pdf") as doc:
        for index, page in enumerate(doc):
            if index >= max_pages:
                break
            pix = page.get_pixmap(dpi=170)
            images.append(pix.tobytes("png"))
    return images


def _as_images(data: bytes, mime: str) -> list[bytes]:
    """Belgeyi yapay zekaya verilecek goruntulere cevirir."""
    if (mime or "").lower() == "application/pdf" or data[:4] == b"%PDF":
        return _pdf_first_pages_png(data)
    from PIL import Image

    with Image.open(io.BytesIO(data)) as img:
        rgb = img.convert("RGB")
        buffer = io.BytesIO()
        rgb.save(buffer, format="PNG")
    return [buffer.getvalue()]


async def read_document(data: bytes, mime: str) -> dict:
    """Belgeyi yapay zeka ile okur; alanlari ve guven skorunu dondurur."""
    api_key = (os.environ.get("EMERGENT_LLM_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("EMERGENT_LLM_KEY tanimli degil.")

    from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage

    images = _as_images(data, mime)
    chat = LlmChat(
        api_key=api_key,
        session_id=f"wa-doc-{uuid.uuid4()}",
        system_message=SYSTEM_PROMPT,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)
    response = await chat.send_message(
        UserMessage(
            text=USER_PROMPT,
            file_contents=[
                ImageContent(image_base64=base64.b64encode(img).decode("ascii")) for img in images
            ],
        )
    )
    parsed = _extract_json(response if isinstance(response, str) else str(response))
    if not parsed:
        raise ValueError("Belge okunamadi.")
    return parsed


def _norm(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (value or "").upper())


def _traveler_names(app_doc: dict) -> list[tuple[str, str, str]]:
    out = []
    for t in app_doc.get("travelers") or []:
        out.append(
            (
                _norm(t.get("first_name", "")),
                _norm(t.get("last_name", "")),
                _norm(t.get("passport_no", "")),
            )
        )
    return out


async def match_application(fields: dict) -> dict:
    """Belge alanlarini basvurularla eslestirir."""
    reference = _norm(fields.get("reference_code"))
    passport = _norm(fields.get("passport_no"))
    first = _norm(fields.get("first_name"))
    last = _norm(fields.get("last_name"))

    if reference:
        code = reference if reference.startswith("DV") else f"DV{reference}"
        doc = await applications_col.find_one(
            {"reference_code": {"$regex": f"^{re.escape(code[:2])}-?{re.escape(code[2:])}$", "$options": "i"}}
        )
        if doc:
            return {"application": doc, "confidence": 0.97, "reason": "reference_code"}

    if passport:
        doc = await applications_col.find_one({"travelers.passport_no": {"$regex": f"^{passport}$", "$options": "i"}})
        if doc:
            return {"application": doc, "confidence": 0.9, "reason": "passport_no"}

    if first and last:
        candidates = await applications_col.find(
            {"status": {"$nin": ["cancelled", "rejected"]}}
        ).sort("created_at", -1).to_list(400)
        matches = [
            doc
            for doc in candidates
            if any(f == first and l == last for f, l, _p in _traveler_names(doc))
        ]
        if len(matches) == 1:
            return {"application": matches[0], "confidence": 0.72, "reason": "full_name"}
        if len(matches) > 1:
            return {"application": None, "confidence": 0.3, "reason": "multiple_name_matches"}

    return {"application": None, "confidence": 0.0, "reason": "no_match"}


async def _store_document(application_id: str, data: bytes, filename: str, mime: str) -> dict:
    file_id = str(uuid.uuid4())
    suffix = "pdf" if (mime or "").endswith("pdf") or data[:4] == b"%PDF" else "jpg"
    path = f"{APP_NAME}/visas/{application_id or 'unmatched'}/{file_id}.{suffix}"
    result = put_object(path, data, mime or "application/octet-stream") or {}
    now = datetime.now(timezone.utc)
    await uploads_col.insert_one(
        {
            "id": file_id,
            "doc_type": "visa_result",
            "storage_path": result.get("path", path),
            "original_filename": filename,
            "content_type": mime or "application/pdf",
            "size": result.get("size", len(data)),
            "is_deleted": False,
            "created_at": now,
            "source": "whatsapp_supplier",
        }
    )
    return {
        "file_id": file_id,
        "filename": filename,
        "content_type": mime or "application/pdf",
        "size": result.get("size", len(data)),
        "uploaded_at": now,
        "sent_at": None,
        "send_status": None,
        "sent_to": None,
        "source": "whatsapp_supplier",
    }


def _origin() -> str:
    return (os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")


async def deliver_to_customer(app_doc: dict, record: dict) -> dict:
    """Belgeyi musteriye e-posta + WhatsApp ile iletir."""
    contact = app_doc.get("contact") or {}
    email = (contact.get("email") or "").strip()
    origin = _origin()
    visa_result = record.get("visa_result") or {}
    download_url = (
        file_access.file_url(origin, visa_result["file_id"], file_access.TTL_EMAIL, download=True)
        if visa_result.get("file_id")
        else ""
    )
    now = datetime.now(timezone.utc)
    delivery: dict = {"email_status": "skipped", "whatsapp_status": "skipped"}

    if email:
        attachments = await visa_pdf_attachment(
            visa_result.get("file_id", ""), app_doc.get("reference_code", "")
        )
        res = await send_email(
            email,
            f"Vizeniz hazır - {app_doc.get('reference_code', '')}",
            visa_ready_html(serialize_doc(app_doc), download_url, "", bool(attachments)),
            kind="visa_delivered",
            meta={"reference_code": app_doc.get("reference_code"), "source": "whatsapp_supplier"},
            attachments=attachments,
        )
        delivery["email_status"] = res.get("status", "unknown")

    from whatsapp import normalize_phone

    phone = (normalize_phone(contact.get("phone")) or "").lstrip("+")
    if phone:
        cfg = await wa_cloud.config(masked=False)
        caption = (
            f"{app_doc.get('reference_code', '')} numaralı başvurunuzun vize belgesi ekte. "
            "İyi yolculuklar dileriz."
        )
        sent = await wa_cloud.send_document(
            phone,
            media_id=record.get("outbound_media_id", ""),
            link=download_url if not record.get("outbound_media_id") else "",
            filename=visa_result.get("filename") or "vize.pdf",
            caption=caption,
            cfg=cfg,
        )
        delivery["whatsapp_status"] = sent.get("status", "unknown")

    visa_result.update(
        {"sent_at": now, "send_status": delivery["email_status"], "sent_to": email}
    )
    await applications_col.update_one(
        {"id": app_doc["id"]},
        {
            "$set": {"visa_result": visa_result, "status": "approved", "updated_at": now},
            "$push": {
                "status_history": {
                    "status": "approved",
                    "at": now,
                    "note": "Vize belgesi WhatsApp'tan alindi ve musteriye iletildi",
                }
            },
        },
    )
    return delivery


async def process_incoming_document(
    *,
    data: bytes,
    mime: str,
    filename: str,
    source: str,
    from_wa_id: str = "",
    group_id: str = "",
    media_id: str = "",
) -> dict:
    """Gelen belgeyi okur, eslestirir ve gerekiyorsa musteriye iletir."""
    now = datetime.now(timezone.utc)
    record: dict = {
        "id": str(uuid.uuid4()),
        "source": source,
        "from_wa_id": from_wa_id,
        "group_id": group_id,
        "media_id": media_id,
        "filename": filename,
        "mime": mime,
        "size": len(data),
        "status": "processing",
        "created_at": now,
        "updated_at": now,
    }
    await wa_documents_col.insert_one(dict(record))

    try:
        fields = await read_document(data, mime)
    except Exception as exc:
        logger.error("wa document read failed: %s", exc)
        await wa_documents_col.update_one(
            {"id": record["id"]},
            {"$set": {"status": "failed", "error": str(exc)[:300], "updated_at": now}},
        )
        return {"ok": False, "reason": "read_failed", "document_id": record["id"]}

    matched = await match_application(fields)
    app_doc = matched.get("application")
    ai_confidence = float(fields.get("confidence") or 0)
    confidence = round(min(float(matched.get("confidence", 0)), max(ai_confidence, 0.5)), 2)

    stored = await _store_document(
        (app_doc or {}).get("id", ""), data, filename or "belge.pdf", mime
    )
    update: dict = {
        "extracted": fields,
        "visa_result": stored,
        "match": {
            "application_id": (app_doc or {}).get("id", ""),
            "reference_code": (app_doc or {}).get("reference_code", ""),
            "confidence": confidence,
            "reason": matched.get("reason", ""),
        },
        "updated_at": datetime.now(timezone.utc),
    }

    cfg = await wa_cloud.config(masked=False)
    auto = bool(app_doc) and confidence >= AUTO_MIN_CONFIDENCE and cfg.get("auto_deliver", True)
    if not auto:
        update["status"] = "pending_review"
        await wa_documents_col.update_one({"id": record["id"]}, {"$set": update})
        await _notify_admin_pending(record["id"], fields, matched)
        return {
            "ok": True,
            "document_id": record["id"],
            "status": "pending_review",
            "match": update["match"],
        }

    delivery = await deliver_to_customer(app_doc, {**record, **update})
    update["status"] = "delivered"
    update["delivery"] = delivery
    await wa_documents_col.update_one({"id": record["id"]}, {"$set": update})
    return {
        "ok": True,
        "document_id": record["id"],
        "status": "delivered",
        "match": update["match"],
        "delivery": delivery,
    }


async def deliver_pending(document_id: str, application_id: str) -> dict:
    """Admin onayindan gecen belgeyi secilen basvuruya baglayip gonderir."""
    record = await wa_documents_col.find_one({"id": document_id})
    if not record:
        return {"ok": False, "reason": "not_found"}
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        return {"ok": False, "reason": "application_not_found"}

    delivery = await deliver_to_customer(app_doc, record)
    await wa_documents_col.update_one(
        {"id": document_id},
        {
            "$set": {
                "status": "delivered",
                "delivery": delivery,
                "match": {
                    "application_id": app_doc["id"],
                    "reference_code": app_doc.get("reference_code", ""),
                    "confidence": 1.0,
                    "reason": "admin_assigned",
                },
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    return {"ok": True, "delivery": delivery, "reference_code": app_doc.get("reference_code", "")}


async def _notify_admin_pending(document_id: str, fields: dict, matched: dict) -> None:
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email:
        return
    reasons = {
        "no_match": "Belgedeki bilgiler hicbir basvuruyla eslesmedi.",
        "multiple_name_matches": "Ayni ada sahip birden fazla basvuru var.",
        "full_name": "Yalnizca ad-soyad eslesti, pasaport numarasi dogrulanamadi.",
    }
    html = (
        '<div style="font-family:Arial,sans-serif;font-size:14px;color:#222">'
        "<p>WhatsApp'tan gelen bir belge otomatik gönderilemedi ve onay kuyruğuna alındı.</p>"
        f"<p><b>Sebep:</b> {reasons.get(matched.get('reason', ''), matched.get('reason', ''))}</p>"
        f"<p><b>Okunan bilgiler:</b> {fields.get('first_name', '')} {fields.get('last_name', '')} · "
        f"pasaport: {fields.get('passport_no', '-')} · tür: {fields.get('document_kind', '-')}</p>"
        "<p>Admin → WhatsApp AI → Belge kuyruğundan başvuruyu seçip gönderebilirsiniz.</p>"
        "</div>"
    )
    try:
        await send_email(
            admin_email,
            "WhatsApp belgesi onay bekliyor",
            html,
            kind="wa_document_pending",
            meta={"document_id": document_id},
        )
    except Exception as exc:  # pragma: no cover
        logger.warning("wa pending notify failed: %s", exc)
