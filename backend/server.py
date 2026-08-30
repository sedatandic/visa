import logging
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from content import VISA_TYPES, compute_pricing
from db import applications_col, client, ensure_indexes, visa_types_col
from storage import init_storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("dubaivize")


async def seed_visa_types():
    """Upsert catalogue: content fields are always refreshed, while price/active/\n    popular are preserved once an admin has edited them."""
    known_ids = []
    for vt in VISA_TYPES:
        known_ids.append(vt["id"])
        doc = dict(vt)
        price = doc.pop("price")
        popular = doc.pop("popular")
        await visa_types_col.update_one(
            {"id": vt["id"]},
            {
                "$set": doc,
                "$setOnInsert": {"price": price, "popular": popular, "active": True},
            },
            upsert=True,
        )
    # retire catalogue entries that no longer exist in code
    await visa_types_col.update_many({"id": {"$nin": known_ids}}, {"$set": {"active": False}})
    logger.info("visa types upserted (%d active)", len(known_ids))


async def migrate_legacy_applications():
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await ensure_indexes()
        await seed_visa_types()
        await migrate_legacy_applications()
    except Exception as exc:
        logger.error("startup db init failed: %s", exc)
    try:
        init_storage()
        logger.info("object storage initialized")
    except Exception as exc:
        logger.error("storage init failed: %s", exc)
    yield
    client.close()


app = FastAPI(title="VizeAtlas Dubai API", lifespan=lifespan)

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"service": "VizeAtlas Dubai API", "status": "ok"}


@api_router.get("/health")
async def health():
    return {
        "status": "ok",
        "email_configured": bool((os.environ.get("RESEND_API_KEY") or "").strip()),
        "payments_configured": bool(os.environ.get("STRIPE_API_KEY")),
    }


import routes_admin  # noqa: E402
import routes_payments  # noqa: E402
import routes_public  # noqa: E402

api_router.include_router(routes_public.router, tags=["public"])
api_router.include_router(routes_payments.router, tags=["payments"])
api_router.include_router(routes_admin.router, tags=["admin"])

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origin_regex=".*",
    allow_methods=["*"],
    allow_headers=["*"],
)
