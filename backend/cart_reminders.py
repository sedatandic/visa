"""Terk edilmis sepet hatirlatmasi.

Musteri /sepet sayfasinda e-postasini girdiginde sepet sunucuya kaydedilir
(`cart_snapshots`). Siparis vermezse 3 saat ve 24 saat sonra birer hatirlatma
e-postasi gonderilir; siparis olusursa kayit pasife alinir.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from db import cart_snapshots_col, orders_col
from emailer import cart_reminder_html, send_email

logger = logging.getLogger(__name__)

REMINDER_STAGES_HOURS = [3, 24]  # 1. hatirlatma 3 saat, 2. hatirlatma 24 saat sonra
SWEEP_INTERVAL_SECONDS = 15 * 60


def default_origin() -> str:
    return (os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")


def cart_url(origin: str) -> str:
    base = (origin or "").rstrip("/")
    return f"{base}/sepet" if base else "/sepet"


def _as_utc(value) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return None


def due_stage(snapshot: dict, now: datetime) -> int | None:
    """Gonderilecek hatirlatma sirasini dondurur (1 veya 2), yoksa None."""
    if not snapshot.get("active", True) or not snapshot.get("items"):
        return None
    sent = int(snapshot.get("reminders_sent") or 0)
    if sent >= len(REMINDER_STAGES_HOURS):
        return None
    updated = _as_utc(snapshot.get("updated_at"))
    if not updated:
        return None
    if now - updated < timedelta(hours=REMINDER_STAGES_HOURS[sent]):
        return None
    return sent + 1


async def _ordered_since(snapshot: dict) -> bool:
    """Sepet kaydedildikten sonra ayni e-posta ile siparis verilmis mi?"""
    updated = _as_utc(snapshot.get("updated_at"))
    query = {"contact.email": snapshot.get("email")}
    if updated:
        query["created_at"] = {"$gte": updated - timedelta(minutes=5)}
    return bool(await orders_col.find_one(query))


async def send_cart_reminder(snapshot: dict, origin: str, stage: int) -> dict:
    subject = (
        "Sepetinizi tamamlamak ister misiniz?"
        if stage == 1
        else "Sepetiniz hâlâ hazır · Dubai eSIM, sigorta ve turlar"
    )
    result = await send_email(
        snapshot["email"],
        subject,
        cart_reminder_html(snapshot, cart_url(origin), stage),
        kind="cart_reminder",
        meta={"email": snapshot["email"], "stage": stage},
    )
    await cart_snapshots_col.update_one(
        {"email": snapshot["email"]},
        {
            "$set": {"last_reminder_at": datetime.now(timezone.utc)},
            "$inc": {"reminders_sent": 1},
        },
    )
    return result


async def run_cart_reminder_sweep(origin: str, force: bool = False) -> dict:
    now = datetime.now(timezone.utc)
    sent, skipped = 0, 0
    async for snapshot in cart_snapshots_col.find({"active": True}):
        stage = due_stage(snapshot, now) or (1 if force and snapshot.get("items") else None)
        if not stage:
            skipped += 1
            continue
        if await _ordered_since(snapshot):
            await cart_snapshots_col.update_one(
                {"email": snapshot["email"]}, {"$set": {"active": False, "closed_reason": "ordered"}}
            )
            skipped += 1
            continue
        try:
            await send_cart_reminder(snapshot, origin, stage)
            sent += 1
        except Exception as exc:  # pragma: no cover
            logger.error("cart reminder failed for %s: %s", snapshot.get("email"), exc)
            skipped += 1
    return {"sent": sent, "skipped": skipped, "ran_at": now.isoformat()}


async def cart_reminder_loop(origin: str) -> None:
    await asyncio.sleep(90)
    while True:
        try:
            summary = await run_cart_reminder_sweep(origin)
            if summary["sent"]:
                logger.info("cart reminder sweep: %s gonderildi", summary["sent"])
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover
            logger.error("cart reminder sweep failed: %s", exc)
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)
