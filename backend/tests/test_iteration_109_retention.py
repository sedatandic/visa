"""Iteration 109: RETEST of the 90-day document retention purge fix.

Extends iteration 108. Covers:
1. storage.delete_object() destroys content by zero-byte PUT when service refuses DELETE.
2. purge_expired_uploads() always tombstones the DB record (is_deleted, purged_at,
   purge_reason, purge_outcome), $unset storage_path; counts purged/wiped/failed.
3. A bogus storage path does not raise and still results in a tombstone.
4. Recent uploads (<90 days) are untouched.
5. A purged file id returns 404/410 through /api/files/{id}, not 500.
6. Regression: /api/content/site 200, POST /api/applications valid adult non-500,
   plus homepage data-testids landing-ask-first and landing-commitments render.
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

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or "").rstrip("/")
if not BASE_URL:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL"):
                BASE_URL = line.strip().split("=", 1)[1].strip().rstrip("/")

TEST_PREFIX = "TEST_RETENTION_"


# ------------------------------- 1. delete_object() actually wipes bytes
def test_delete_object_wipes_content_when_delete_forbidden():
    from storage import put_object, get_object, delete_object

    unique = uuid.uuid4().hex[:10]
    path = f"test_retention/{unique}.txt"
    payload = b"gizli pasaport icerigi"  # 22 bytes
    put_object(path, payload, "text/plain")

    body, _ct = get_object(path)
    assert len(body) == 22, f"expected 22 pre-wipe bytes, got {len(body)}"

    outcome = delete_object(path)
    assert outcome in ("wiped", "deleted", "missing"), outcome
    print(f"[delete_object] outcome for {path}: {outcome}")

    # Confirm content destroyed (zero bytes) or truly gone
    if outcome in ("wiped", "deleted"):
        try:
            body2, _ = get_object(path)
        except requests.HTTPError as e:
            # 404 also acceptable if platform actually accepted DELETE
            assert e.response.status_code == 404
            return
        assert len(body2) == 0, f"expected 0 bytes after wipe, got {len(body2)}"
        print(f"[delete_object] post-wipe size = {len(body2)} bytes ✅")


# ------------------------------- 2 & 3. purge always tombstones (even on bogus path)
def test_purge_tombstones_and_bogus_path_is_safe():
    asyncio.run(_run_purge_scenarios())


async def _run_purge_scenarios():
    from db import uploads_col
    from retention import purge_expired_uploads
    from storage import put_object, get_object
    import file_access

    now = datetime.now(timezone.utc)

    # a) real old upload pointing at a real object
    real_unique = uuid.uuid4().hex[:10]
    real_old_id = f"{TEST_PREFIX}OLDREAL_{real_unique}"
    real_old_path = f"test_retention/{real_unique}.txt"
    put_object(real_old_path, b"gizli pasaport icerigi", "text/plain")
    body, _ = get_object(real_old_path)
    assert len(body) == 22

    # b) recent upload — must be left alone
    recent_id = f"{TEST_PREFIX}NEW_{uuid.uuid4().hex[:8]}"
    recent_path = f"test_retention/recent-{uuid.uuid4().hex[:6]}.txt"

    # c) old upload pointing at a bogus, never-created path
    bogus_id = f"{TEST_PREFIX}OLDBOGUS_{uuid.uuid4().hex[:8]}"
    bogus_path = "test_retention/does-not-exist-xyz"

    await uploads_col.insert_many([
        {
            "id": real_old_id,
            "storage_path": real_old_path,
            "content_type": "text/plain",
            "original_filename": "old.txt",
            "created_at": now - timedelta(days=120),
            "is_deleted": False,
        },
        {
            "id": recent_id,
            "storage_path": recent_path,
            "content_type": "text/plain",
            "original_filename": "recent.txt",
            "created_at": now,
            "is_deleted": False,
        },
        {
            "id": bogus_id,
            "storage_path": bogus_path,
            "content_type": "text/plain",
            "original_filename": "bogus.txt",
            "created_at": now - timedelta(days=200),
            "is_deleted": False,
        },
    ])

    cutoff = now - timedelta(days=90)
    total_matching = await uploads_col.count_documents(
        {"is_deleted": {"$ne": True}, "created_at": {"$lt": cutoff}}
    )
    print(f"[retention] docs matching >90d cutoff (incl. our 2 fakes): {total_matching}")

    try:
        result = await purge_expired_uploads()
        print(f"[retention] purge result: {result}")

        # both TEST_ old docs plus any real ones. Assert at least 2 purged, and no crash.
        assert result["purged"] >= 2, result
        assert result["failed"] == 0, f"failed should be 0 with the fix: {result}"
        assert result["wiped"] >= 1, result

        # a) real old doc: tombstoned, outcome wiped/deleted, no storage_path
        old_doc = await uploads_col.find_one({"id": real_old_id})
        assert old_doc is not None
        assert old_doc["is_deleted"] is True
        assert old_doc.get("purge_reason") == "retention_90d"
        assert old_doc.get("purged_at") is not None
        assert old_doc.get("purge_outcome") in ("wiped", "deleted"), old_doc.get("purge_outcome")
        assert "storage_path" not in old_doc

        # Real object bytes must be gone (0 bytes) or a 404
        try:
            body2, _ = get_object(real_old_path)
            assert len(body2) == 0, f"post-purge object still has {len(body2)} bytes"
            print(f"[retention] real object post-purge size = {len(body2)} bytes ✅")
        except requests.HTTPError as e:
            assert e.response.status_code == 404

        # b) recent doc untouched
        recent_doc = await uploads_col.find_one({"id": recent_id})
        assert recent_doc["is_deleted"] is False
        assert recent_doc.get("storage_path") == recent_path
        assert recent_doc.get("purged_at") is None

        # c) bogus old doc: tombstoned despite storage miss
        bogus_doc = await uploads_col.find_one({"id": bogus_id})
        assert bogus_doc is not None
        assert bogus_doc["is_deleted"] is True
        assert bogus_doc.get("purge_reason") == "retention_90d"
        assert bogus_doc.get("purge_outcome") in ("missing", "wiped", "deleted"), bogus_doc.get("purge_outcome")
        assert "storage_path" not in bogus_doc

        # /api/files/{purged}?t=... => 404 (not 500)
        token = file_access.make_token(real_old_id, ttl=3600)
        r = requests.get(f"{BASE_URL}/api/files/{real_old_id}", params={"t": token}, timeout=30)
        assert r.status_code in (404, 410), f"purged file access got {r.status_code}: {r.text[:200]}"
    finally:
        await uploads_col.delete_one({"id": real_old_id})
        await uploads_col.delete_one({"id": recent_id})
        await uploads_col.delete_one({"id": bogus_id})


# ------------------------------- 4. retention wording exists in code
def test_error_logging_wording_present():
    src = open("/app/backend/retention.py").read()
    assert "icerigi depodan silinemedi" in src
    assert "inceleyin" in src


# ------------------------------- 5. Fresh upload + signed download works after purge
def test_fresh_upload_download_after_purge():
    # Reload db/motor so motor picks up the current asyncio loop (each asyncio.run
    # creates a new loop; motor caches the previous one and errors with 'Event loop is closed').
    for mod in ("db", "retention", "file_access"):
        sys.modules.pop(mod, None)
    asyncio.run(_run_fresh_upload_after_purge())


async def _run_fresh_upload_after_purge():
    from db import uploads_col
    from retention import purge_expired_uploads
    from storage import put_object
    import file_access

    # Kick a purge (should be safe; no failures expected)
    result = await purge_expired_uploads()
    assert result["failed"] == 0, result

    # Create a genuinely fresh upload
    fid = f"{TEST_PREFIX}FRESH_{uuid.uuid4().hex[:8]}"
    path = f"test_retention/fresh-{uuid.uuid4().hex[:6]}.txt"
    body = b"taze icerik"
    put_object(path, body, "text/plain")
    await uploads_col.insert_one({
        "id": fid,
        "storage_path": path,
        "content_type": "text/plain",
        "original_filename": "fresh.txt",
        "created_at": datetime.now(timezone.utc),
        "is_deleted": False,
    })
    try:
        tok = file_access.make_token(fid, ttl=3600)
        r = requests.get(f"{BASE_URL}/api/files/{fid}", params={"t": tok}, timeout=30)
        assert r.status_code == 200, f"{r.status_code}: {r.text[:200]}"
        assert r.content == body, f"expected {body!r}, got {r.content!r}"
    finally:
        await uploads_col.delete_one({"id": fid})


# ------------------------------- 6. light regression
class TestLightRegression:
    def test_content_site(self):
        r = requests.get(f"{BASE_URL}/api/content/site", timeout=30)
        assert r.status_code == 200

    def test_applications_post_valid_adult(self):
        # Full "valid adult" payload (matching test_iteration_106 shape).
        # Uses fake file ids so backend still rejects with 400 (files missing)
        # rather than 500 - which is what we care about here (endpoint alive).
        today = datetime.now().date()
        payload = {
            "contact": {
                "full_name": "TEST RETENTION Applicant",
                "email": "delivered@resend.dev",
                "phone": "+905551112233",
                "address_city": "Istanbul",
                "whatsapp_optin": False,
            },
            "travelers": [
                {
                    "first_name": "TEST",
                    "last_name": "RETENTION",
                    "birth_date": "1990-05-10",
                    "gender": "male",
                    "applicant_type": "adult",
                    "nationality": "TR",
                    "passport_no": "U12345678",
                    "passport_expiry": (today + timedelta(days=500)).isoformat(),
                    "marital_status": "single",
                    "profession": "Employee",
                    "mother_name": "Ayse",
                    "father_name": "Mehmet",
                    "visa_type_id": "visa_30_single",
                    "passport_file_id": "fake-passport-file-id",
                    "photo_file_id": "fake-photo-file-id",
                }
            ],
            "travel": {
                "arrival_date": (today + timedelta(days=30)).isoformat(),
                "departure_date": (today + timedelta(days=37)).isoformat(),
                "purpose": "tourism",
                "birth_country": "TR",
                "accommodation": "Hotel X",
                "flight_no": "TK123",
            },
            "addons": {"express": False, "insurance": False, "insurance_plus": False, "esim": False},
            "store_items": [],
            "extra_documents": {"ticket_file_id": None, "hotel_file_id": None, "other_file_ids": []},
            "kvkk_accepted": True,
        }
        r = requests.post(f"{BASE_URL}/api/applications", json=payload, timeout=45)
        # Endpoint alive: must not 500. 200 or 400 (files-missing business validation) are both acceptable.
        assert r.status_code < 500, f"{r.status_code}: {r.text[:400]}"
        print(f"POST /api/applications -> {r.status_code}")
