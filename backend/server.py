import logging
import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from content import VISA_TYPES
from db import client, ensure_indexes, visa_types_col
from storage import init_storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("dubaivize")


async def seed_visa_types():
    for vt in VISA_TYPES:
        existing = await visa_types_col.find_one({"id": vt["id"]})
        if existing:
            continue
        doc = dict(vt)
        doc["active"] = True
        await visa_types_col.insert_one(doc)
    logger.info("visa types seeded")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await ensure_indexes()
        await seed_visa_types()
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
