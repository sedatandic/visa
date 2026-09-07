"""Zami portalindan okunan durumu basvuruya isleyen ve musteriyi bilgilendiren servis.

- `apply_status`: tek basvuru icin durumu isler, degistiyse e-posta gonderir.
- `sweep_statuses`: takip edilen tum basvurulari sirayla kontrol eder.
- `status_loop`: arka planda periyodik tarama (ayardan aktif edilir).
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from content import STATUS_LABELS
from db import applications_col, serialize_doc, settings_col
from emailer import send_email, status_change_html, subject_with_ref
from zami import SESSION_KEY, get_mapping, log_event

logger = logging.getLogger(__name__)

TRACKABLE_STATUSES = ["submitted", "payment_pending", "documents_pending", "reviewing"]
# Portal oturumu ~15-20 dk hareketsizlikte dusuyor; 10 dakikada bir yokluyoruz
SESSION_KEEPALIVE_SECONDS = 10 * 60
FINAL_STATUSES = {"approved", "rejected", "cancelled"}
# Ayni "oturum dustu" uyarisini en fazla 12 saatte bir gonder (surec restart'larinda
# bellek icindeki bayrak sifirlaniyordu ve her yeniden baslatmada e-posta gidiyordu).
SESSION_WARN_COOLDOWN_HOURS = 12
# Bu nedenler OTP akisina ait: otp_reminders modulu gunde bir net hatirlatma gonderiyor,
# ayni durum icin ikinci bir e-posta atmiyoruz.
OTP_FLOW_REASONS = {"otp_required", "otp_required_pending", "no_trusted_device"}


async def _notify_status_email(app_id: str, matched: str) -> str:
    """Durum degisimini musteriye e-posta ile bildirir."""
    fresh = await applications_col.find_one({"id": app_id})
    to_email = (fresh.get("contact") or {}).get("email")
    if not to_email:
        return "skipped"
    res = await send_email(
        to_email,
        subject_with_ref(fresh["reference_code"], "durumu güncellendi"),
        status_change_html(serialize_doc(fresh), STATUS_LABELS[matched], ""),
        kind="status_change",
        meta={"reference_code": fresh["reference_code"], "status": matched, "source": "zami"},
    )
    return res.get("status", "skipped")


def _public_base_url() -> str:
    """Musteriye gonderilen baglantilarin kok adresi (ortam degiskeninden)."""
    return (os.environ.get("PUBLIC_BASE_URL") or os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")


async def _notify_status_whatsapp(app_id: str, matched: str) -> str:
    """Sonuc bildirimini WhatsApp uzerinden gonderir (hata akisi kesmez)."""
    try:
        import whatsapp

        fresh = await applications_col.find_one({"id": app_id})
        out = await whatsapp.notify_result(fresh, matched, _public_base_url())
        return out.get("status", "skipped")
    except Exception as exc:  # pragma: no cover
        logger.error("whatsapp notify failed: %s", exc)
        return "skipped"


async def _auto_deliver_visa(app_id: str) -> str:
    """Onaylanan vize belgesini portaldan indirip musteriye iletir."""
    try:
        from visa_delivery import deliver_visa_document

        fresh = await applications_col.find_one({"id": app_id})
        out = await deliver_visa_document(fresh, _public_base_url())
        return "sent" if out.get("ok") else (out.get("reason") or "failed")
    except Exception as exc:  # pragma: no cover
        logger.error("visa auto delivery failed: %s", exc)
        return "error"


async def _write_status_update(app_id: str, update: dict, matched: str, raw: str, changed: bool) -> None:
    """Durum alanlarini yazar; degisim varsa durum gecmisine kayit ekler."""
    if not changed:
        await applications_col.update_one({"id": app_id}, {"$set": update})
        return
    push = {
        "status_history": {
            "status": matched,
            "at": update["zami_status_checked_at"],
            "note": f"Zami portalından otomatik güncellendi: {raw[:120]}",
        }
    }
    await applications_col.update_one({"id": app_id}, {"$set": update, "$push": push})


async def _run_status_notifications(app_id: str, matched: str, notify: bool) -> dict:
    """Durum degisiminde e-posta / WhatsApp / vize teslimi akislarini yurutur."""
    out = {"email": "skipped", "whatsapp": "skipped", "visa_delivery": "skipped"}
    if notify:
        out["email"] = await _notify_status_email(app_id, matched)
    if matched in {"approved", "rejected"}:
        out["whatsapp"] = await _notify_status_whatsapp(app_id, matched)
    if matched == "approved":
        out["visa_delivery"] = await _auto_deliver_visa(app_id)
    return out


def _status_log_note(matched: str | None, previous: str | None, changed: bool) -> str:
    """Islem gunlugu icin insan okunur not uretir."""
    note = f"Portal durumu: {matched or 'eşleşmedi'}"
    if changed:
        note += f" · başvuru {previous} → {matched} olarak güncellendi"
    return note


async def apply_status(app_doc: dict, result: dict, notify: bool = True, actor: str = "") -> dict:
    """Portal sonucunu basvuruya yazar; durum degistiyse musteriye e-posta atar."""
    now = datetime.now(timezone.utc)
    matched = result.get("matched_status")
    raw = (result.get("raw_text") or "")[:400]
    app_id = app_doc["id"]
    previous = app_doc.get("status")

    update = {
        "zami_status": matched or "",
        "zami_status_raw": raw,
        "zami_status_checked_at": now,
        "updated_at": now,
    }
    changed = bool(matched and matched in STATUS_LABELS and matched != previous)
    if changed:
        update["status"] = matched

    await _write_status_update(app_id, update, matched, raw, changed)

    sent = (
        await _run_status_notifications(app_id, matched, notify)
        if changed
        else {"email": "skipped", "whatsapp": "skipped", "visa_delivery": "skipped"}
    )

    await log_event(
        app_doc.get("id"),
        app_doc.get("reference_code"),
        "status_checked",
        _status_log_note(matched, previous, changed),
        actor=actor,
        extra={"raw": raw, **sent},
    )
    return {
        "status_changed": changed,
        "new_status": matched if changed else previous,
        "previous_status": previous,
        "email_notification": sent["email"],
        "whatsapp_notification": sent["whatsapp"],
        "visa_delivery": sent["visa_delivery"],
    }


async def _check_one(doc: dict, mapping: dict, actor: str) -> dict:
    """Tek basvurunun portal durumunu kontrol edip sonucunu ozetler."""
    import zami_rpa

    res = await zami_rpa.check_status(doc)
    if not res.get("ok"):
        return {
            "reference_code": doc.get("reference_code"),
            "ok": False,
            "error": res.get("error"),
        }
    applied = await apply_status(
        doc, res, notify=bool(mapping.get("auto_notify", True)), actor=actor
    )
    return {
        "reference_code": doc.get("reference_code"),
        "ok": True,
        "matched_status": res.get("matched_status"),
        "raw_text": res.get("raw_text"),
        "status_changed": applied["status_changed"],
    }


def _sweep_blocker(mapping: dict, force: bool) -> dict | None:
    """Tarama on kosullari; engel varsa hazir yanit dondurur."""
    if not mapping.get("status_url"):
        return {"ok": False, "error": "Durum sayfası adresi tanımlı değil.", "checked": 0}
    if not force and not mapping.get("auto_check_enabled"):
        return {"ok": False, "error": "Otomatik durum takibi kapalı.", "checked": 0}
    return None


# Takip edilecek basvuru sorgusu: Zami'ye aktarilmis ve sonuclanmamis olanlar
_SWEEP_QUERY = {
    "status": {"$in": TRACKABLE_STATUSES},
    "$or": [
        {"zami_reference": {"$nin": [None, ""]}},
        {"zami_transferred_at": {"$ne": None}},
    ],
}


async def sweep_statuses(actor: str = "", force: bool = False) -> dict:
    """Takip edilen basvurulari sirayla kontrol eder."""
    mapping = await get_mapping()
    blocked = _sweep_blocker(mapping, force)
    if blocked is not None:
        return blocked

    who = actor or "auto"
    docs = await applications_col.find(_SWEEP_QUERY).sort("created_at", -1).limit(30).to_list(30)
    results = []
    for doc in docs:
        row = await _check_one(doc, mapping, who)
        results.append(row)
        # oturum dustuyse kalan basvurular icin denemeye devam etmenin anlami yok
        if not row["ok"] and "oturum" in (row.get("error") or "").lower():
            break
        await asyncio.sleep(1.5)

    changed = sum(1 for r in results if r.get("status_changed"))
    await log_event(
        None,
        None,
        "status_sweep",
        f"{len(results)} başvuru kontrol edildi, {changed} durum güncellendi",
        actor=who,
    )
    return {"ok": True, "checked": len(results), "changed": changed, "results": results}


async def keepalive_loop():
    """Portal oturumunu 10 dakikada bir yoklayarak canli tutar.

    Oturum dustugunde once OTP'siz otomatik giris denenir (trusted-device
    cerezi + AI captcha). Yalnizca portal gercekten OTP isterse (ayda bir
    civari) admin e-posta ile uyarilir.
    """
    import zami_rpa

    await asyncio.sleep(90)
    warned = False
    while True:
        try:
            warned = await _keepalive_tick(zami_rpa, warned)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("zami keepalive loop error: %s", exc)
        await asyncio.sleep(SESSION_KEEPALIVE_SECONDS)


async def _keepalive_tick(zami_rpa, warned: bool = False) -> bool:
    """Tek yoklama adimi. Uyari tekrari kalici cooldown ile yonetilir (settings)."""
    state = await zami_rpa.session_status()
    if not state.get("has_session"):
        return warned
    out = await zami_rpa.keepalive_session()
    if out.get("ok"):
        return False
    if out.get("reason") != "expired":
        return warned

    relogin = await zami_rpa.auto_relogin()
    if relogin.get("ok"):
        logger.info("zami session auto-renewed without OTP")
        return False
    reason = relogin.get("reason") or ""
    if await _warn_admin_session_expired(reason=reason):
        logger.warning("zami session expired (%s) - admin bilgilendirildi", reason)
        return True
    logger.info("zami session expired (%s) - uyari gonderilmedi", reason)
    return warned


async def _warn_admin_session_expired(reason: str = "") -> bool:
    """Uyari e-postasi gonderildiyse True doner (cagiran taraf ona gore loglar)."""
    admin_email = os.environ.get("ADMIN_EMAIL")
    if not admin_email or reason in OTP_FLOW_REASONS:
        return False
    if not await _warn_cooldown_passed():
        logger.info("zami session warning suppressed (cooldown)")
        return False
    detail = {
        "captcha_failed": "Otomatik giriş captcha'yı okuyamadı, elle giriş gerekiyor.",
        "no_credentials": "Portal kullanıcı adı/şifresi kayıtlı değil.",
        "browser": "Sunucuda tarayıcı motoru başlatılamadı.",
    }.get(reason, "Otomatik yenileme başarısız oldu.")
    panel = (os.environ.get("PUBLIC_SITE_URL") or "").strip().rstrip("/")
    link = (
        f'<p><a href="{panel}/admin/zami" style="color:#B06A29;font-weight:bold">'
        "Robot oturumunu aç</a></p>"
        if panel
        else ""
    )
    html = (
        '<div style="font-family:Arial,sans-serif;font-size:14px;color:#222">'
        "<p><b>Zami portal oturumu düştü ve otomatik yenilenemedi.</b></p>"
        f"<p>{detail}</p>"
        "<p>Panelden bir kez giriş yapmanız yeterli:</p>"
        "<p>Admin → Zami Aktarım → <b>Robot Oturumu</b> → Oturum Başlat "
        "(captcha otomatik okunur, yalnızca e-postanıza gelen OTP kodunu girin).</p>"
        f"{link}"
        "<p style=\"color:#555\">Girişte cihaz güveni kaydedildiği için sonraki "
        "düşüşlerde robot OTP'siz kendi kendine giriş yapacak; OTP'yi yaklaşık "
        "ayda bir girmeniz beklenir. Bu uyarı en fazla 12 saatte bir gönderilir.</p>"
        "</div>"
    )
    try:
        await send_email(
            admin_email,
            "Zami portal oturumu düştü - yeniden giriş gerekiyor",
            html,
            kind="zami_session_expired",
        )
        await settings_col.update_one(
            {"key": SESSION_KEY},
            {"$set": {"value.expired_notified_at": datetime.now(timezone.utc).isoformat()}},
        )
    except Exception as exc:
        logger.warning("zami session warning email failed: %s", exc)


async def _warn_cooldown_passed() -> bool:
    """Son 12 saatte oturum uyarisi ya da OTP hatirlatmasi gittiyse tekrar gonderme."""
    doc = await settings_col.find_one({"key": SESSION_KEY})
    value = (doc or {}).get("value") or {}
    now = datetime.now(timezone.utc)
    for field in ("expired_notified_at", "otp_reminder_sent_at"):
        raw = value.get(field)
        if not raw:
            continue
        try:
            sent = datetime.fromisoformat(raw)
        except (TypeError, ValueError):
            continue
        if not sent.tzinfo:
            sent = sent.replace(tzinfo=timezone.utc)
        if now - sent < timedelta(hours=SESSION_WARN_COOLDOWN_HOURS):
            return False
    return True


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
