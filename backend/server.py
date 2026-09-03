import logging
import os
import uuid
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from content import ARTICLES, REVIEW_SUMMARY, TESTIMONIALS, VISA_TYPES, compute_pricing
from db import (
    applications_col,
    articles_col,
    client,
    ensure_indexes,
    settings_col,
    products_col,
    testimonials_col,
    visa_types_col,
)
from storage import init_storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("dubaivize")


async def seed_visa_types() -> None:
    """Upsert catalogue: content fields are always refreshed, while price/active/\n    popular are preserved once an admin has edited them."""
    known_ids = []
    for vt in VISA_TYPES:
        known_ids.append(vt["id"])
        doc = dict(vt)
        price = doc.pop("price")
        price_usd = doc.pop("price_usd", None)
        popular = doc.pop("popular")
        await visa_types_col.update_one(
            {"id": vt["id"]},
            {
                "$set": doc,
                "$setOnInsert": {
                    "price": price,
                    "price_usd": price_usd,
                    "popular": popular,
                    "active": True,
                },
            },
            upsert=True,
        )
        # USD baz fiyat sonradan eklendi: eksik olan kayitlara bir kez yazilir
        if price_usd:
            await visa_types_col.update_one(
                {"id": vt["id"], "price_usd": {"$in": [None, 0]}},
                {"$set": {"price_usd": price_usd}},
            )
            await visa_types_col.update_one(
                {"id": vt["id"], "price_usd": {"$exists": False}},
                {"$set": {"price_usd": price_usd}},
            )
    # retire catalogue entries that no longer exist in code
    await visa_types_col.update_many({"id": {"$nin": known_ids}}, {"$set": {"active": False}})
    logger.info("visa types upserted (%d active)", len(known_ids))


async def seed_products() -> None:
    """eSIM ve sigorta urunlerini bir kez olusturur; fiyatlar admin tarafindan yonetilir."""
    from routes_store import DEFAULT_PRODUCTS

    for product in DEFAULT_PRODUCTS:
        doc = dict(product)
        price_usd = doc.pop("price_usd")
        popular = doc.pop("popular", False)
        await products_col.update_one(
            {"id": doc["id"]},
            {
                "$set": doc,
                "$setOnInsert": {"price_usd": price_usd, "popular": popular, "active": True},
            },
            upsert=True,
        )
    logger.info("store products seeded (%d)", len(DEFAULT_PRODUCTS))


async def backfill_saved_travelers() -> None:
    """Mevcut basvurulardaki yolculari bir kez aile profiline aktarir."""
    flag = await settings_col.find_one({"key": "saved_travelers_backfilled"})
    if flag:
        return
    from routes_account import upsert_saved_travelers

    total = 0
    cursor = applications_col.find({"contact.email": {"$exists": True}})
    async for doc in cursor:
        email = (doc.get("contact") or {}).get("email")
        if not email:
            continue
        total += await upsert_saved_travelers(email, doc.get("travelers") or [])
    await settings_col.update_one(
        {"key": "saved_travelers_backfilled"},
        {"$set": {"key": "saved_travelers_backfilled", "value": {"count": total}}},
        upsert=True,
    )
    logger.info("saved travelers backfilled (%d)", total)


async def migrate_legacy_applications() -> None:
    """Convert single-applicant applications (v1 schema) to the multi-traveller schema."""
    cursor = applications_col.find({"travelers": {"$exists": False}, "applicant": {"$exists": True}})
    migrated = 0
    async for doc in cursor:
        a = doc.get("applicant") or {}
        docs = doc.get("documents") or {}
        traveler = {
            "id": str(uuid.uuid4()),
            "first_name": a.get("first_name", ""),
            "last_name": a.get("last_name", ""),
            "birth_date": a.get("birth_date", ""),
            "gender": a.get("gender", "male"),
            "applicant_type": "adult",
            "nationality": a.get("nationality", "TR"),
            "national_id": a.get("national_id", ""),
            "passport_no": a.get("passport_no", ""),
            "passport_expiry": a.get("passport_expiry", ""),
            "visa_type_id": doc.get("visa_type_id", ""),
            "visa_type_name": doc.get("visa_type_name", ""),
            "visa_short_name": doc.get("visa_type_name", ""),
            "processing_days": doc.get("processing_days", ""),
            "price": float(doc.get("price") or 0),
            "currency": doc.get("currency", "TRY"),
            "passport_file_id": docs.get("passport_file_id"),
            "photo_file_id": docs.get("photo_file_id"),
            "documents": docs,
        }
        pricing = compute_pricing([traveler["price"]], {})
        await applications_col.update_one(
            {"id": doc["id"]},
            {
                "$set": {
                    "contact": {
                        "full_name": f"{a.get('first_name','')} {a.get('last_name','')}".strip(),
                        "email": a.get("email", ""),
                        "phone": a.get("phone", ""),
                        "address_city": a.get("address_city", ""),
                    },
                    "travelers": [traveler],
                    "addons": {"express": False, "insurance": False},
                    "extra_documents": {"ticket_file_id": None, "hotel_file_id": None, "other_file_ids": []},
                    "pricing": pricing,
                    "visa_result": doc.get("visa_result"),
                }
            },
        )
        migrated += 1
    if migrated:
        logger.info("migrated %d legacy applications to multi-traveller schema", migrated)


async def seed_content_collections() -> None:
    """Blog yazilari, musteri yorumlari ve puan ozetini ilk kurulumda tohumlar."""
    if await articles_col.count_documents({}) == 0:
        now = datetime.now(timezone.utc)
        for order, a in enumerate(ARTICLES):
            await articles_col.insert_one(
                {
                    "id": str(uuid.uuid4()),
                    "slug": a["slug"],
                    "title": a["title"],
                    "date": a["date"],
                    "excerpt": a["excerpt"],
                    "body": list(a.get("body") or []),
                    "cover_image": a.get("cover_image", ""),
                    "published": True,
                    "order": order,
                    "created_at": now,
                    "updated_at": now,
                }
            )
        logger.info("seeded %d articles", len(ARTICLES))

    if await testimonials_col.count_documents({}) == 0:
        now = datetime.now(timezone.utc)
        for order, t in enumerate(TESTIMONIALS):
            doc = dict(t)
            doc.update(
                {
                    "id": str(uuid.uuid4()),
                    "published": True,
                    "order": order,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            await testimonials_col.insert_one(doc)
        logger.info("seeded %d testimonials", len(TESTIMONIALS))

    if not await settings_col.find_one({"key": "review_summary"}):
        await settings_col.insert_one(
            {
                "key": "review_summary",
                "value": dict(REVIEW_SUMMARY),
                "updated_at": datetime.now(timezone.utc),
            }
        )
        logger.info("seeded review summary")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await ensure_indexes()
        await seed_visa_types()
        await seed_content_collections()
        await migrate_legacy_applications()
        await seed_products()
        await backfill_saved_travelers()
    except Exception as exc:
        logger.error("startup db init failed: %s", exc)
    try:
        init_storage()
        logger.info("object storage initialized")
    except Exception as exc:
        logger.error("storage init failed: %s", exc)

    reminder_task = None
    zami_task = None
    keepalive_task = None
    try:
        from doc_reminders import default_origin, reminder_loop

        reminder_task = asyncio.create_task(reminder_loop(default_origin()))
        logger.info("document reminder scheduler started")
    except Exception as exc:
        logger.error("reminder scheduler failed to start: %s", exc)

    try:
        from zami_status import keepalive_loop, status_loop

        zami_task = asyncio.create_task(status_loop())
        keepalive_task = asyncio.create_task(keepalive_loop())
        logger.info("zami status + session keepalive schedulers started")
    except Exception as exc:
        logger.error("zami status scheduler failed to start: %s", exc)

    yield

    for task in (reminder_task, zami_task, keepalive_task):
        if task:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass
    client.close()


app = FastAPI(title="Dubai Vize Online API", lifespan=lifespan)

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root() -> dict:
    return {"service": "Dubai Vize Online API", "status": "ok"}


@api_router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "email_configured": bool((os.environ.get("RESEND_API_KEY") or "").strip()),
        "payments_configured": bool(os.environ.get("STRIPE_API_KEY")),
    }


import routes_account
import routes_admin  # noqa: E402
import routes_store  # noqa: E402
import routes_payments  # noqa: E402
import routes_public  # noqa: E402
import routes_zami  # noqa: E402

api_router.include_router(routes_public.router, tags=["public"])
api_router.include_router(routes_payments.router, tags=["payments"])
api_router.include_router(routes_account.router, tags=["account"])
api_router.include_router(routes_store.router, tags=["store"])
api_router.include_router(routes_admin.router, tags=["admin"])
api_router.include_router(routes_zami.router, tags=["zami"])

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origin_regex=".*",
    allow_methods=["*"],
    allow_headers=["*"],
)
