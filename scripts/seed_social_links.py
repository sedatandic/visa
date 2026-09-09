"""Sosyal medya ayarlarini DB'ye yazar (Instagram: dubaivizehatti).

Panel: Admin -> Sosyal Medya. Bu betik yalnizca ilk kurulum/duzeltme icin.
"""
import asyncio
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv("/app/backend/.env")
sys.path.insert(0, "/app/backend")

import social_links  # noqa: E402
from content import COMPANY  # noqa: E402

TARGET = {
    "instagram": "https://www.instagram.com/dubaivizehatti/",
    "google_review": COMPANY["google_review"],
}


async def main() -> None:
    db = AsyncIOMotorClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
    now = datetime.now(timezone.utc)

    company_doc = await db["site_settings"].find_one({"key": "company_info"})
    company = {**COMPANY, **((company_doc or {}).get("value") or {})}
    company.update(TARGET)

    social_doc = await db["site_settings"].find_one({"key": "social_links"})
    rows = social_links.resolve_items(company, (social_doc or {}).get("value"))
    for row in rows:
        if row["platform"] in TARGET:
            row["url"] = TARGET[row["platform"]]
            row["enabled"] = True
    items = social_links.normalize_items(rows)

    for key, value in (("company_info", company), ("social_links", items)):
        await db["site_settings"].update_one(
            {"key": key}, {"$set": {"value": value, "updated_at": now}}, upsert=True
        )
    print("\n".join(f"{i['platform']} | {i['enabled']} | {i['url']}" for i in items))


asyncio.run(main())
