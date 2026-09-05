"""content.py icindeki vize kategorilerini DB'ye senkronlar (uzatma/transit -> single)."""
import asyncio
import os
import sys

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv("/app/backend/.env")
import content  # noqa: E402


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    for visa in content.VISA_TYPES:
        res = await db.visa_types.update_one(
            {"id": visa["id"]},
            {"$set": {"category": visa["category"], "auto_suggest": visa.get("auto_suggest", True)}},
        )
        print(visa["id"], visa["category"], "modified", res.modified_count)


asyncio.run(main())
