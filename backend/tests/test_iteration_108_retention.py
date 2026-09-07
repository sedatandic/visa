"""Iteration 108: 90-day document retention purge + homepage-backing endpoints.

Tests:
1. purge_expired_uploads() marks old docs is_deleted=true, sets purged_at + purge_reason,
   unsets storage_path, does NOT touch recent uploads, returns purged>=1.
2. GET /api/files/{purged_id}?t=... returns 404 (not 500).
3. Backend regression: /api/content/site, /api/visa-types, /api/bundles, /api/products, POST /api/applications.
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
sys.path.insert(0, "/app/backend")

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/") if os.environ.get("REACT_APP_BACKEND_URL") else None
if not BASE_URL:
    # frontend .env
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL"):
                BASE_URL = line.strip().split("=", 1)[1].strip().rstrip("/")

TEST_PREFIX = "TEST_RETENTION_"


# ------------------------------- retention direct call
def test_purge_expired_uploads_marks_old_ignores_recent():
    asyncio.run(_run_purge())


async def _run_purge():
    from db import uploads_col
    from retention import purge_expired_uploads
    import file_access

    old_id = f"{TEST_PREFIX}OLD_{uuid.uuid4().hex[:8]}"
    recent_id = f"{TEST_PREFIX}NEW_{uuid.uuid4().hex[:8]}"
    old_path = f"dubaivize/{TEST_PREFIX}fake/old.pdf"
    recent_path = f"dubaivize/{TEST_PREFIX}fake/recent.pdf"

    now = datetime.now(timezone.utc)
    await uploads_col.insert_one({
        "id": old_id,
        "storage_path": old_path,
        "content_type": "application/pdf",
        "original_filename": "old.pdf",
        "created_at": now - timedelta(days=100),
        "is_deleted": False,
    })
    await uploads_col.insert_one({
        "id": recent_id,
        "storage_path": recent_path,
        "content_type": "application/pdf",
        "original_filename": "recent.pdf",
        "created_at": now,
        "is_deleted": False,
    })

    # Count matching docs (for safety reporting)
    cutoff = now - timedelta(days=90)
    total_matching = await uploads_col.count_documents(
        {"is_deleted": {"$ne": True}, "created_at": {"$lt": cutoff}}
    )
    print(f"[retention] total docs currently matching purge criteria: {total_matching}")

    try:
        result = await purge_expired_uploads()
        assert result["purged"] >= 1, result
        assert result["failed"] == 0 or result["failed"] < result["purged"] + 5

        # old doc must be marked deleted, storage_path removed
        old_doc = await uploads_col.find_one({"id": old_id})
        assert old_doc is not None
        assert old_doc["is_deleted"] is True
        assert old_doc.get("purge_reason") == "retention_90d"
        assert old_doc.get("purged_at") is not None
        assert "storage_path" not in old_doc

        # recent doc untouched
        recent_doc = await uploads_col.find_one({"id": recent_id})
        assert recent_doc["is_deleted"] is False
        assert recent_doc.get("storage_path") == recent_path

        # /api/files/{purged}?t=... => 404 (not 500)
        token = file_access.make_token(old_id, ttl=3600)
        r = requests.get(f"{BASE_URL}/api/files/{old_id}", params={"t": token}, timeout=30)
        assert r.status_code in (404, 410), f"purged file access got {r.status_code}: {r.text[:200]}"
    finally:
        await uploads_col.delete_one({"id": old_id})
        await uploads_col.delete_one({"id": recent_id})


# ------------------------------- backend regression
class TestBackendRegression:
    def test_content_site(self):
        r = requests.get(f"{BASE_URL}/api/content/site", timeout=30)
        assert r.status_code == 200
        d = r.json()
        # used by frontend Home & CommitmentsStrip
        assert "company" in d or "whatsapp" in d or "working_hours" in d or "phone" in d
        print("content/site keys:", list(d.keys())[:20])

    def test_visa_types(self):
        r = requests.get(f"{BASE_URL}/api/visa-types", timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert isinstance(d, list) and len(d) > 0

    def test_bundles(self):
        r = requests.get(f"{BASE_URL}/api/bundles", params={"visa_days": 30}, timeout=30)
        assert r.status_code == 200

    def test_products(self):
        r = requests.get(f"{BASE_URL}/api/products", timeout=30)
        assert r.status_code == 200

    def test_create_application_still_works(self):
        payload = {
            "contact": {
                "name": "TEST RETENTION",
                "email": "test-retention@example.com",
                "phone": "+905551112233",
            },
            "travelers": [
                {
                    "applicant_type": "adult",
                    "first_name": "TEST",
                    "last_name": "RETENTION",
                    "birth_date": "1990-05-10",
                    "passport_no": "U12345678",
                    "passport_expiry": "2030-01-01",
                    "visa_type_slug": "30-gunluk-tek-girisli",
                }
            ],
            "travel": {
                "start_date": (datetime.now() + timedelta(days=30)).date().isoformat(),
                "end_date": (datetime.now() + timedelta(days=37)).date().isoformat(),
            },
        }
        r = requests.post(f"{BASE_URL}/api/applications", json=payload, timeout=45)
        # accept various success/business-validation codes; must not be 500
        assert r.status_code < 500, f"{r.status_code}: {r.text[:400]}"
        print("POST /api/applications ->", r.status_code)
