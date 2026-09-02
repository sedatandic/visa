import os
from datetime import datetime, date
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ.get("DB_NAME", "test_database")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
visa_types_col = db["visa_types"]
applications_col = db["visa_applications"]
uploads_col = db["uploads"]
payments_col = db["payment_transactions"]
contact_col = db["contact_messages"]
email_outbox_col = db["email_outbox"]
articles_col = db["articles"]
testimonials_col = db["testimonials"]
settings_col = db["site_settings"]
notifications_col = db["notifications"]
login_codes_col = db["login_codes"]
drafts_col = db["application_drafts"]
saved_travelers_col = db["saved_travelers"]
products_col = db["store_products"]
orders_col = db["store_orders"]
zami_logs_col = db["zami_logs"]
zami_handoffs_col = db["zami_handoffs"]


def serialize_doc(doc: Any) -> Any:
    """Recursively convert a Mongo document into a JSON-serializable structure."""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]
    if isinstance(doc, dict):
        out = {}
        for k, v in doc.items():
            if k == "_id":
                continue
            out[k] = serialize_doc(v)
        return out
    if isinstance(doc, datetime):
        return doc.isoformat()
    if isinstance(doc, date):
        return doc.isoformat()
    try:
        from bson import ObjectId

        if isinstance(doc, ObjectId):
            return str(doc)
    except Exception:
        pass
    return doc


async def ensure_indexes() -> None:
    await applications_col.create_index("id", unique=True)
    await applications_col.create_index("reference_code", unique=True)
    await applications_col.create_index("created_at")
    await uploads_col.create_index("id", unique=True)
    await payments_col.create_index("session_id")
    await visa_types_col.create_index("id", unique=True)
    await articles_col.create_index("slug", unique=True)
    await articles_col.create_index("id", unique=True)
    await testimonials_col.create_index("id", unique=True)
    await settings_col.create_index("key", unique=True)
