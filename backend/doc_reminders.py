"""Eksik belge hatirlatma otomasyonu.

- `missing_documents`: bir basvurudaki eksik belgeleri hesaplar
- `send_document_reminder`: musteriye hatirlatma e-postasi gonderir (Resend yoksa outbox'a skipped)
- `run_reminder_sweep`: periyodik tarama; 24 saatten eski, 48 saatten sik olmayan, en fazla 3 hatirlatma
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from db import applications_col, drafts_col
from emailer import document_reminder_html, send_email

logger = logging.getLogger(__name__)

# Hatirlatma kurallari
FIRST_REMINDER_AFTER_HOURS = 24
REMINDER_INTERVAL_HOURS = 48
MAX_REMINDERS = 3
SWEEP_INTERVAL_SECONDS = 60 * 60  # 1 saat (taslak kurtarma hizli olsun)

REMINDABLE_STATUSES = {"submitted", "documents_pending", "payment_pending", "reviewing"}

DOC_LABELS = {
    "passport": "Pasaport kimlik sayfasi",
    "photo": "Vesikalik fotograf",
    "ticket": "Donus ucak bileti / rezervasyonu",
    "hotel": "Otel / konaklama rezervasyonu",
}

DOC_LABELS_TR = {
    "passport": "Pasaport kimlik sayfası",
    "photo": "Vesikalık fotoğraf",
    "ticket": "Dönüş uçak bileti / rezervasyonu",
    "hotel": "Otel / konaklama rezervasyonu",
}


def _traveler_name(traveler: dict, index: int) -> str:
    name = f"{traveler.get('first_name', '')} {traveler.get('last_name', '')}".strip()
    return name or f"{index + 1}. Yolcu"


def missing_documents(app_doc: dict) -> list:
    """Eksik belgeleri normalize liste olarak dondurur.

    Ogeler: {scope: 'application'|'traveler', key, label, traveler_id?, traveler_name?}
    """
    missing = []
    extra = app_doc.get("extra_documents") or {}
    for key in ("ticket", "hotel"):
        if not extra.get(f"{key}_file_id"):
            missing.append(
                {
                    "scope": "application",
                    "key": key,
                    "label": DOC_LABELS_TR[key],
                }
            )

    for index, traveler in enumerate(app_doc.get("travelers") or []):
        docs = traveler.get("documents") or {}
        for key in ("passport", "photo"):
            file_id = docs.get(f"{key}_file_id") or traveler.get(f"{key}_file_id")
            if not file_id:
                missing.append(
                    {
                        "scope": "traveler",
                        "key": key,
                        "label": DOC_LABELS_TR[key],
                        "traveler_id": traveler.get("id"),
                        "traveler_name": _traveler_name(traveler, index),
                    }
                )
    return missing


def _contact_email(app_doc: dict) -> str:
    contact = app_doc.get("contact") or {}
    if contact.get("email"):
        return contact["email"]
    return (app_doc.get("applicant") or {}).get("email", "")


def _track_url(origin: str, app_doc: dict) -> str:
    base = (origin or "").rstrip("/")
    return f"{base}/takip?kod={app_doc.get('reference_code', '')}"


def _reminder_state(app_doc: dict) -> dict:
    state = app_doc.get("document_reminder") or {}
    return {
        "count": int(state.get("count") or 0),
        "last_sent_at": state.get("last_sent_at"),
    }


async def _record_reminder_sent(app_doc: dict, missing: list, state: dict, result: dict) -> None:
    """Hatirlatma sayacini, gecmisi ve gerekiyorsa basvuru durumunu guncelller."""
    missing_keys = [m["key"] for m in missing]
    now = datetime.now(timezone.utc)
    await applications_col.update_one(
        {"id": app_doc.get("id")},
        {
            "$set": {
                "document_reminder": {
                    "count": state["count"] + 1,
                    "last_sent_at": now,
                    "last_missing_keys": missing_keys,
                },
                "updated_at": now,
            },
            "$push": {
                "reminders": {
                    "kind": "document_reminder",
                    "sent_at": now,
                    "missing_keys": missing_keys,
                    "email_status": result.get("status"),
                }
            },
        },
    )
    # eksik belge varsa durumu belge bekleniyor olarak isaretle
    if app_doc.get("status") in {"submitted", "reviewing"}:
        await applications_col.update_one(
            {"id": app_doc.get("id")}, {"$set": {"status": "documents_pending"}}
        )


async def send_document_reminder(app_doc: dict, origin: str, missing: list | None = None) -> dict:
    """Musteriye eksik belge hatirlatmasi gonderir. Asla exception atmaz."""
    missing = missing if missing is not None else missing_documents(app_doc)
    to_email = _contact_email(app_doc)
    if not missing:
        return {"status": "skipped", "reason": "eksik belge yok"}
    if not to_email:
        return {"status": "skipped", "reason": "e-posta adresi yok"}

    state = _reminder_state(app_doc)
    upload_url = _track_url(origin, app_doc)
    result = await send_email(
        to_email,
        f"Eksik belge hatirlatmasi - {app_doc.get('reference_code', '')}",
        document_reminder_html(app_doc, missing, upload_url),
        kind="document_reminder",
        meta={
            "application_id": app_doc.get("id"),
            "reference_code": app_doc.get("reference_code"),
            "missing_keys": [m["key"] for m in missing],
            "reminder_no": state["count"] + 1,
        },
    )
    await _record_reminder_sent(app_doc, missing, state, result)
    return {"status": result.get("status"), "missing": missing, "email": result}


def _due_for_reminder(app_doc: dict, now: datetime) -> bool:
    state = _reminder_state(app_doc)
    if state["count"] >= MAX_REMINDERS:
        return False
    created = app_doc.get("created_at")
    if isinstance(created, datetime):
        created_at = created if created.tzinfo else created.replace(tzinfo=timezone.utc)
        if now - created_at < timedelta(hours=FIRST_REMINDER_AFTER_HOURS):
            return False
    last = state["last_sent_at"]
    if isinstance(last, datetime):
        last_at = last if last.tzinfo else last.replace(tzinfo=timezone.utc)
        if now - last_at < timedelta(hours=REMINDER_INTERVAL_HOURS):
            return False
    return True


async def pending_applications() -> list:
    """Eksik belgesi olan basvurular (hatirlatma zamani gelmis olanlar isaretlenir)."""
    now = datetime.now(timezone.utc)
    items = []
    cursor = applications_col.find({"status": {"$in": list(REMINDABLE_STATUSES)}}).sort("created_at", -1)
    async for doc in cursor:
        missing = missing_documents(doc)
        if not missing:
            continue
        state = _reminder_state(doc)
        items.append(
            {
                "id": doc.get("id"),
                "reference_code": doc.get("reference_code"),
                "contact_name": (doc.get("contact") or {}).get("full_name", ""),
                "email": _contact_email(doc),
                "status": doc.get("status"),
                "created_at": doc.get("created_at").isoformat()
                if isinstance(doc.get("created_at"), datetime)
                else doc.get("created_at"),
                "missing": missing,
                "reminder_count": state["count"],
                "last_sent_at": state["last_sent_at"].isoformat()
                if isinstance(state["last_sent_at"], datetime)
                else state["last_sent_at"],
                "due": _due_for_reminder(doc, now),
            }
        )
    return items


async def run_reminder_sweep(origin: str, force: bool = False) -> dict:
    """Tum uygun basvurulara hatirlatma gonderir. Sonuc ozetini dondurur."""
    now = datetime.now(timezone.utc)
    sent, skipped = 0, 0
    details = []
    cursor = applications_col.find({"status": {"$in": list(REMINDABLE_STATUSES)}})
    async for doc in cursor:
        missing = missing_documents(doc)
        if not missing:
            continue
        if not force and not _due_for_reminder(doc, now):
            skipped += 1
            continue
        try:
            res = await send_document_reminder(doc, origin, missing)
            sent += 1
            details.append(
                {
                    "reference_code": doc.get("reference_code"),
                    "email_status": res.get("status"),
                    "missing_keys": [m["key"] for m in missing],
                }
            )
        except Exception as exc:  # pragma: no cover - guvenlik agi
            logger.error("document reminder failed for %s: %s", doc.get("id"), exc)
            skipped += 1
    return {"sent": sent, "skipped": skipped, "details": details, "ran_at": now.isoformat()}


async def reminder_loop(origin: str) -> None:
    """Arka planda periyodik hatirlatma dongusu."""
    await asyncio.sleep(60)  # servis acilisinda hemen calismasin
    while True:
        try:
            summary = await run_reminder_sweep(origin)
            if summary["sent"]:
                logger.info("document reminder sweep: %s gonderildi", summary["sent"])
            draft_summary = await run_draft_reminder_sweep(origin)
            if draft_summary["sent"]:
                logger.info("draft reminder sweep: %s gonderildi", draft_summary["sent"])
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover
            logger.error("reminder sweep failed: %s", exc)
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)


def default_origin() -> str:
    return (os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")


# ------------------------------------------------------- taslak (sepeti kurtarma)
DRAFT_FIRST_REMINDER_AFTER_HOURS = 1  # yarim kalan basvuruya 1 saat sonra hatirlat
DRAFT_REMINDER_INTERVAL_HOURS = 72
MAX_DRAFT_REMINDERS = 2


def _draft_resume_url(origin: str, draft: dict) -> str:
    base = (origin or "").rstrip("/")
    if not base:
        return ""
    return f"{base}/basvuru?taslak={draft.get('id')}&kod={draft.get('resume_code', '')}"


def _draft_due(draft: dict, now: datetime) -> bool:
    state = draft.get("reminder") or {}
    if int(state.get("count") or 0) >= MAX_DRAFT_REMINDERS:
        return False
    updated = draft.get("updated_at")
    if isinstance(updated, datetime):
        ts = updated if updated.tzinfo else updated.replace(tzinfo=timezone.utc)
        if now - ts < timedelta(hours=DRAFT_FIRST_REMINDER_AFTER_HOURS):
            return False
    last = state.get("last_sent_at")
    if isinstance(last, datetime):
        ts = last if last.tzinfo else last.replace(tzinfo=timezone.utc)
        if now - ts < timedelta(hours=DRAFT_REMINDER_INTERVAL_HOURS):
            return False
    return True


async def _draft_converted(draft: dict) -> bool:
    """Taslak sonrasinda ayni e-posta ile basvuru olusturulmus mu?"""
    updated = draft.get("updated_at")
    query = {"contact.email": {"$regex": f"^{draft.get('email', '')}$", "$options": "i"}}
    if isinstance(updated, datetime):
        query["created_at"] = {"$gte": updated}
    return await applications_col.count_documents(query) > 0


async def send_draft_reminder(draft: dict, origin: str) -> dict:
    """Yarim kalan basvuru icin hatirlatma e-postasi gonderir."""
    from emailer import draft_reminder_html

    email = draft.get("email")
    if not email:
        return {"status": "skipped", "reason": "e-posta yok"}
    state = draft.get("reminder") or {}
    result = await send_email(
        email,
        "Dubai vize basvurunuz yarim kaldi",
        draft_reminder_html(draft, _draft_resume_url(origin, draft)),
        kind="draft_reminder",
        meta={"draft_id": draft.get("id"), "reminder_no": int(state.get("count") or 0) + 1},
    )
    await drafts_col.update_one(
        {"id": draft.get("id")},
        {
            "$set": {
                "reminder": {
                    "count": int(state.get("count") or 0) + 1,
                    "last_sent_at": datetime.now(timezone.utc),
                }
            }
        },
    )
    return {"status": result.get("status"), "email": result}


async def pending_drafts() -> list:
    """Hatirlatma adayi taslaklar."""
    now = datetime.now(timezone.utc)
    items = []
    async for draft in drafts_col.find({}).sort("updated_at", -1):
        if await _draft_converted(draft):
            continue
        state = draft.get("reminder") or {}
        items.append(
            {
                "id": draft.get("id"),
                "email": draft.get("email"),
                "title": draft.get("title"),
                "traveler_count": draft.get("traveler_count", 1),
                "step": draft.get("step", 0),
                "updated_at": draft.get("updated_at").isoformat()
                if isinstance(draft.get("updated_at"), datetime)
                else draft.get("updated_at"),
                "reminder_count": int(state.get("count") or 0),
                "due": _draft_due(draft, now),
            }
        )
    return items


async def run_draft_reminder_sweep(origin: str, force: bool = False) -> dict:
    """Yarim kalan basvurulara hatirlatma gonderir (sepeti kurtarma)."""
    now = datetime.now(timezone.utc)
    sent, skipped = 0, 0
    async for draft in drafts_col.find({}):
        if await _draft_converted(draft):
            skipped += 1
            continue
        if not force and not _draft_due(draft, now):
            skipped += 1
            continue
        try:
            await send_draft_reminder(draft, origin)
            sent += 1
        except Exception as exc:  # pragma: no cover
            logger.error("draft reminder failed for %s: %s", draft.get("id"), exc)
            skipped += 1
    return {"sent": sent, "skipped": skipped, "ran_at": now.isoformat()}
