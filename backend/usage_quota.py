"""Gunluk global kullanim kotasi: pahali AI cagrilarinda maliyet ust siniri.

IP tabanli hiz siniri kimlik sahteciligine veya dagitik trafige karsi tek basina
yeterli degildir; bu sayac veritabaninda tutuldugu icin tum replikalar icin gecerli
tek bir gunluk tavan saglar.
"""

import os
from datetime import datetime, timezone

from fastapi import HTTPException
from pymongo import ReturnDocument

from db import db

DEFAULT_LIMITS = {
    "passport_ocr": 400,
    "photo_check": 800,
}


def daily_limit(name: str) -> int:
    raw = os.environ.get(f"{name.upper()}_DAILY_LIMIT")
    try:
        return int(raw) if raw is not None else DEFAULT_LIMITS.get(name, 0)
    except ValueError:
        return DEFAULT_LIMITS.get(name, 0)


async def consume_daily(name: str, message: str) -> None:
    """Gunluk sayaci atomik olarak arttirir; tavan asilirsa 429 doner."""
    limit = daily_limit(name)
    if limit <= 0:
        return
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    doc = await db.usage_counters.find_one_and_update(
        {"_id": f"{name}:{day}"},
        {"$inc": {"count": 1}, "$setOnInsert": {"name": name, "day": day}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    if int((doc or {}).get("count") or 0) > limit:
        raise HTTPException(429, message)
