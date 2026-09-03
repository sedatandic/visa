"""Zami portalindan okunan durumu basvuruya isleyen ve musteriyi bilgilendiren servis.

- `apply_status`: tek basvuru icin durumu isler, degistiyse e-posta gonderir.
- `sweep_statuses`: takip edilen tum basvurulari sirayla kontrol eder.
- `status_loop`: arka planda periyodik tarama (ayardan aktif edilir).
"""

import asyncio
import logging
import os
from datetime import datetime, timezone

from content import STATUS_LABELS
from db import applications_col, serialize_doc
from emailer import send_email, status_change_html
from zami import get_mapping, log_event

logger = logging.getLogger(__name__)

TRACKABLE_STATUSES = ["submitted", "payment_pending", "documents_pending", "reviewing"]
# Portal oturumu ~15-20 dk hareketsizlikte dusuyor; 10 dakikada bir yokluyoruz
SESSION_KEEPALIVE_SECONDS = 10 * 60
FINAL_STATUSES = {"approved", "rejected", "cancelled"}


async def apply_status(app_doc: dict, result: dict, notify: bool = True, actor: str = "") -> dict:
    """Portal sonucunu basvuruya yazar; durum degistiyse musteriye e-posta atar."""
    now = datetime.now(timezone.utc)
    matched = result.get("matched_status")
    raw = (result.get("raw_text") or "")[:400]

    update = {
        "zami_status": matched or "",
        "zami_status_raw": raw,
        "zami_status_checked_at": now,
        "updated_at": now,
    }
    changed = False
    email_status = "skipped"
    previous = app_doc.get("status")

    if matched and matched in STATUS_LABELS and matched != previous:
        update["status"] = matched
        changed = True

    push = None
    if changed:
        push = {
            "status_history": {
                "status": matched,
                "at": now,
                "note": f"Zami portalından otomatik güncellendi: {raw[:120]}",
            }
        }
        await applications_col.update_one({"id": app_doc["id"]}, {"$set": update, "$push": push})
    else:
        await applications_col.update_one({"id": app_doc["id"]}, {"$set": update})

    if changed and notify:
        fresh = await applications_col.find_one({"id": app_doc["id"]})
        to_email = (fresh.get("contact") or {}).get("email")
        if to_email:
            res = await send_email(
                to_email,
                f"Başvuru durumu güncellendi - {fresh['reference_code']}",
                status_change_html(serialize_doc(fresh), STATUS_LABELS[matched], ""),
                kind="status_change",
                meta={"reference_code": fresh["reference_code"], "status": matched, "source": "zami"},
            )
            email_status = res.get("status", "skipped")

    whatsapp_status = "skipped"
    visa_delivery_status = "skipped"
    if changed and matched in {"approved", "rejected"}:
        try:
            import os

            import whatsapp

            fresh = await applications_col.find_one({"id": app_doc["id"]})
            out = await whatsapp.notify_result(
                fresh, matched, os.environ.get("PUBLIC_BASE_URL", "https://vizeatlas.com")
            )
            whatsapp_status = out.get("status", "skipped")
        except Exception as exc:  # pragma: no cover
            logger.error("whatsapp notify failed: %s", exc)

    # Vize onaylandiysa belgeyi portaldan indirip musteriye otomatik ilet
    if changed and matched == "approved":
        try:
            from visa_delivery import deliver_visa_document

            fresh = await applications_col.find_one({"id": app_doc["id"]})
            origin = os.environ.get("PUBLIC_BASE_URL", "https://vizeatlas.com")
            out = await deliver_visa_document(fresh, origin)
            visa_delivery_status = "sent" if out.get("ok") else (out.get("reason") or "failed")
        except Exception as exc:  # pragma: no cover
            logger.error("visa auto delivery failed: %s", exc)
            visa_delivery_status = "error"

    await log_event(
        app_doc.get("id"),
        app_doc.get("reference_code"),
        "status_checked",
        (
            f"Portal durumu: {matched or 'eşleşmedi'}"
            + (f" · başvuru {previous} → {matched} olarak güncellendi" if changed else "")
        ),
        actor=actor,
        extra={
            "raw": raw,
            "email": email_status,
            "whatsapp": whatsapp_status,
            "visa_delivery": visa_delivery_status,
        },
    )
    return {
        "status_changed": changed,
        "new_status": matched if changed else previous,
        "previous_status": previous,
        "email_notification": email_status,
        "whatsapp_notification": whatsapp_status,
        "visa_delivery": visa_delivery_status,
    }


async def sweep_statuses(actor: str = "", force: bool = False) -> dict:
    """Takip edilen basvurulari sirayla kontrol eder."""
    import zami_rpa

    mapping = await get_mapping()
    if not mapping.get("status_url"):
        return {"ok": False, "error": "Durum sayfası adresi tanımlı değil.", "checked": 0}
    if not force and not mapping.get("auto_check_enabled"):
        return {"ok": False, "error": "Otomatik durum takibi kapalı.", "checked": 0}

    query = {
        "status": {"$in": TRACKABLE_STATUSES},
        "$or": [
            {"zami_reference": {"$nin": [None, ""]}},
            {"zami_transferred_at": {"$ne": None}},
        ],
    }
    docs = await applications_col.find(query).sort("created_at", -1).limit(30).to_list(30)
    results = []
    for doc in docs:
        res = await zami_rpa.check_status(doc)
        if res.get("ok"):
            applied = await apply_status(doc, res, notify=bool(mapping.get("auto_notify", True)), actor=actor or "auto")
            results.append(
                {
                    "reference_code": doc.get("reference_code"),
                    "ok": True,
                    "matched_status": res.get("matched_status"),
                    "raw_text": res.get("raw_text"),
                    "status_changed": applied["status_changed"],
                }
            )
        else:
            results.append({"reference_code": doc.get("reference_code"), "ok": False, "error": res.get("error")})
            if "oturum" in (res.get("error") or "").lower():
                break
        await asyncio.sleep(1.5)

    changed = sum(1 for r in results if r.get("status_changed"))
    await log_event(
        None,
        None,
        "status_sweep",
        f"{len(results)} başvuru kontrol edildi, {changed} durum güncellendi",
        actor=actor or "auto",
    )
    return {"ok": True, "checked": len(results), "changed": changed, "results": results}


async def keepalive_loop():
    """Portal oturumunu 10 dakikada bir yoklayarak canli tutar.

    Zami oturumu kisa surede dustugu icin otomatik durum takibinin calismasi
    buna bagli. Oturum dustugunde admin bir kez e-posta ile uyarilir.
    """
    import zami_rpa

    await asyncio.sleep(90)
    warned = False
    while True:
        try:
            state = await zami_rpa.session_status()
            if state.get("has_session"):
                out = await zami_rpa.keepalive_session()
                if out.get("ok"):
                    warned = False
                elif out.get("reason") == "expired" and not warned:
                    warned = True
                    await _warn_admin_session_expired()
                    logger.warning("zami session expired - admin bilgilendirildi")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("zami keepalive loop error: %s", exc)
        await asyncio.sleep(SESSION_KEEPALIVE_SECONDS)


async def _warn_admin_session_expired() -> None:
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email:
        return
    html = (
        '<div style="font-family:Arial,sans-serif;font-size:14px;color:#222">'
        "<p><b>Zami portal oturumu düştü.</b></p>"
        "<p>Otomatik durum takibi ve aktarım için panelden yeniden giriş yapmanız gerekiyor:</p>"
        "<p>Admin → Zami Aktarım → <b>Robot Oturumu</b> → Oturum Başlat "
        "(captcha otomatik okunur, yalnızca e-postanıza gelen OTP kodunu girin).</p>"
        "</div>"
    )
    try:
        await send_email(
            admin_email,
            "Zami portal oturumu düştü - yeniden giriş gerekiyor",
            html,
            kind="zami_session_expired",
        )
    except Exception as exc:
        logger.warning("zami session warning email failed: %s", exc)


async def status_loop():
    """Arka plan dongusu: ayarlanan periyotta durum taramasi yapar."""
    await asyncio.sleep(120)
    while True:
        hours = 6
        try:
            mapping = await get_mapping()
            hours = int(mapping.get("auto_check_hours") or 6)
            if mapping.get("auto_check_enabled") and mapping.get("status_url"):
                out = await sweep_statuses(actor="auto")
                logger.info("zami status sweep: %s", {k: out.get(k) for k in ("checked", "changed", "error")})
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("zami status loop error: %s", exc)
        await asyncio.sleep(max(1, hours) * 3600)
