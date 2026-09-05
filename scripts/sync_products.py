"""routes_store.DEFAULT_PRODUCTS icindeki urunleri store_products koleksiyonuna ekler.

Var olan kayitlar korunur; yalnizca eksik urunler eklenir.
"""
import asyncio
import os
import sys

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv("/app/backend/.env")
from routes_store import DEFAULT_PRODUCTS  # noqa: E402


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    total = await db.store_products.count_documents({})
    if not total:
        print("store_products bos: varsayilan katalog kullaniliyor, ekleme yapilmadi.")
        return
    for product in DEFAULT_PRODUCTS:
        existing = await db.store_products.find_one({"id": product["id"]})
        if existing:
            print(product["id"], "zaten var")
            continue
        await db.store_products.insert_one({**product, "active": True})
        print(product["id"], "eklendi")


asyncio.run(main())
