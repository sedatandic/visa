"""Zami'de onaylanan vize belgesini indirip musteriye ileten otomasyon.

Akis:
1. Durum takibi bir basvuruyu "approved" olarak isaretler.
2. Robot, basvurunun Zami kaydini acar ve vize PDF'ini indirir.
3. PDF object storage'a yazilir, basvuruya `visa_result` olarak islenir.
4. Musteriye indirme linkiyle "Vizeniz hazir" e-postasi gonderilir.

Not: PDF butonunun yeri portalda kayda gore degisebildigi icin genis bir
secici listesi ve indirme (download) yakalayici birlikte kullanilir.
"""
import logging
import os
import re
import uuid
from datetime import datetime, timezone

from db import applications_col, serialize_doc, uploads_col
from emailer import send_email, visa_ready_html
from storage import APP_NAME, put_object

logger = logging.getLogger(__name__)

# Portalda vize belgesine goturen olasi butonlar/linkler
VISA_DOC_SELECTORS = [
    'a[href$=".pdf"]',
    'a[href*=".pdf"]',
    'a[title*="Visa" i]',
    'a[title*="Print" i]',
    'a[title*="Download" i]',
    'button[title*="Visa" i]',
    'button:has-text("PRINT VISA")',
    'button:has-text("DOWNLOAD")',
    'a:has-text("Visa Copy")',
    'a:has-text("E-Visa")',
]


def zami_record_url(app_doc: dict, portal_url: str) -> str:
    """VS-66059 -> https://portal/?_=203&s=smrtch.edit&id=66059"""
    reference = str(app_doc.get("zami_reference") or "")
    match = re.search(r"(\d{3,})", reference)
    if not match:
        return ""
    return f"{portal_url.rstrip('/')}/?_=203&s=smrtch.edit&id={match.group(1)}"


async def _store_pdf(application_id: str, data: bytes, filename: str) -> dict:
    """Indirilen PDF'i object storage'a yazip uploads kaydini olusturur."""
    file_id = str(uuid.uuid4())
    path = f"{APP_NAME}/visas/{application_id}/{file_id}.pdf"
    result = put_object(path, data, "application/pdf") or {}
    now = datetime.now(timezone.utc)
    await uploads_col.insert_one(
        {
            "id": file_id,
            "doc_type": "visa_result",
            "storage_path": result.get("path", path),
            "original_filename": filename,
            "content_type": "application/pdf",
            "size": result.get("size", len(data)),
            "is_deleted": False,
            "created_at": now,
            "source": "zami_auto",
        }
    )
    return {
        "file_id": file_id,
        "filename": filename,
        "content_type": "application/pdf",
        "size": result.get("size", len(data)),
        "uploaded_at": now,
        "sent_at": None,
        "send_status": None,
        "sent_to": None,
        "source": "zami_auto",
    }


async def _fetch_context(app_doc: dict) -> dict:
    """Zami kayit adresi + saklanan oturumu hazirlar.

    Hazirsa `{"ok": True, "url": ..., "state": ...}`, degilse hata sebebi doner.
    """
    import zami
    import zami_rpa
    from db import settings_col

    creds = await zami.raw_credentials()
    url = zami_record_url(app_doc, creds["portal_url"])
    if not url:
        return {"ok": False, "reason": "no_zami_reference"}

    session = await zami_rpa.session_status()
    if not session.get("has_session") or session.get("expired"):
        return {"ok": False, "reason": "session"}

    doc = await settings_col.find_one({"key": zami_rpa.SESSION_KEY})
    state = ((doc or {}).get("value") or {}).get("storage_state")
    return {"ok": True, "url": url, "state": state}


async def _download_pdf(page, selector: str) -> tuple[bytes, str] | None:
    """Tek bir secici uzerinden PDF indirmeyi dener; PDF degilse None doner."""
    target = page.locator(selector).first
    if await target.count() == 0 or not await target.is_visible():
        return None
    async with page.expect_download(timeout=20000) as info:
        await target.click(timeout=8000)
    download = await info.value
    local = await download.path()
    if not local:
        return None
    with open(local, "rb") as fh:
        data = fh.read()
    if not data.startswith(b"%PDF"):
        return None
    return data, download.suggested_filename


async def _grab_visa_pdf(page, app_doc: dict) -> dict:
    """Olasi tum secicileri sirayla deneyip PDF'i indirir ve saklar."""
    for selector in VISA_DOC_SELECTORS:
        try:
            found = await _download_pdf(page, selector)
            if not found:
                continue
            data, suggested = found
            filename = suggested or f"vize-{app_doc.get('reference_code')}.pdf"
            visa_result = await _store_pdf(app_doc["id"], data, filename)
            return {"ok": True, "visa_result": visa_result, "selector": selector}
        except Exception:
            continue
    return {"ok": False, "reason": "not_found"}


async def fetch_visa_document(app_doc: dict) -> dict:
    """Zami kaydindan vize PDF'ini indirir; bulamazsa sebebini dondurur."""
    import zami_rpa

    prepared = await _fetch_context(app_doc)
    if not prepared.get("ok"):
        return prepared

    url = prepared["url"]
    pw, browser, context, page = await zami_rpa._launch_with_state(prepared["state"])
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        result = await _grab_visa_pdf(page, app_doc)
        if not result.get("ok"):
            result["url"] = url
        return result
    except Exception as exc:
        logger.warning("zami visa fetch failed: %s", exc)
        return {"ok": False, "reason": "error", "error": str(exc)}
    finally:
        await zami_rpa._close({"pw": pw, "browser": browser, "context": context})


async def deliver_visa_document(app_doc: dict, origin: str) -> dict:
    """Vize PDF'ini indirir ve musteriye e-postayla iletir."""
    existing = app_doc.get("visa_result") or {}
    if existing.get("file_id") and existing.get("sent_at"):
        return {"ok": True, "skipped": "already_sent"}

    visa_result = existing if existing.get("file_id") else None
    if not visa_result:
        fetched = await fetch_visa_document(app_doc)
        if not fetched.get("ok"):
            await _warn_admin(app_doc, fetched.get("reason", "error"))
            return {"ok": False, **fetched}
        visa_result = fetched["visa_result"]

    to_email = (app_doc.get("contact") or {}).get("email") or ""
    if not to_email:
        return {"ok": False, "reason": "no_email"}

    download_url = f"{origin.rstrip('/')}/api/files/{visa_result['file_id']}?download=1"
    now = datetime.now(timezone.utc)
    res = await send_email(
        to_email,
        f"Vizeniz hazır - {app_doc.get('reference_code', '')}",
        visa_ready_html(serialize_doc(app_doc), download_url, ""),
        kind="visa_delivered",
        meta={"reference_code": app_doc.get("reference_code"), "auto": True},
    )
    visa_result.update({"sent_at": now, "send_status": res.get("status"), "sent_to": to_email})
    await applications_col.update_one(
        {"id": app_doc["id"]},
        {
            "$set": {
                "visa_result": visa_result,
                "status": "approved",
                "updated_at": now,
            },
            "$push": {
                "status_history": {
                    "status": "approved",
                    "at": now,
                    "note": "Vize belgesi Zami'den otomatik indirildi ve musteriye iletildi",
                }
            },
        },
    )
    return {"ok": True, "email_status": res.get("status"), "download_url": download_url}


async def _warn_admin(app_doc: dict, reason: str) -> None:
    """PDF otomatik alinamadiysa admini bilgilendirir (elle yuklemesi icin)."""
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email:
        return
    reasons = {
        "session": "Portal oturumu düştü; panelden yeniden giriş yapın.",
        "not_found": "Kayıtta vize PDF bağlantısı bulunamadı; belgeyi elle indirip yükleyin.",
        "no_zami_reference": "Başvurunun Zami numarası (VS-xxxxx) kayıtlı değil.",
    }
    html = (
        '<div style="font-family:Arial,sans-serif;font-size:14px;color:#222">'
        f"<p><b>{app_doc.get('reference_code', '')}</b> başvurusu Zami'de onaylandı "
        "ancak vize belgesi otomatik indirilemedi.</p>"
        f"<p>Sebep: {reasons.get(reason, reason)}</p>"
        "<p>Admin → Başvuru detayı → Vize belgesi bölümünden elle yükleyip gönderebilirsiniz.</p>"
        "</div>"
    )
    try:
        await send_email(
            admin_email,
            f"Vize belgesi otomatik alinamadi - {app_doc.get('reference_code', '')}",
            html,
            kind="visa_autofetch_failed",
            meta={"application_id": app_doc.get("id")},
        )
    except Exception as exc:
        logger.warning("visa autofetch warning email failed: %s", exc)
