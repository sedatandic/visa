"""Iteration 98: Resend key sanity + email_outbox check for login_code."""
import os
import time
import pytest
import requests
from pymongo import MongoClient

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # fallback: read frontend/.env
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL"):
                BASE_URL = line.split("=", 1)[1].strip().strip('"').rstrip("/")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")


@pytest.fixture(scope="module")
def db():
    client = MongoClient(MONGO_URL)
    return client[DB_NAME]


def test_request_login_code_sends_email(db):
    """Trigger login-code flow for delivered@resend.dev and verify email_outbox record."""
    email = "delivered@resend.dev"
    r = requests.post(f"{BASE_URL}/api/account/request-code", json={"email": email}, timeout=30)
    # can be 200 or 429 (rate-limited). We accept either but still check outbox
    assert r.status_code in (200, 429), f"unexpected status {r.status_code}: {r.text}"

    # wait briefly for async insert
    time.sleep(3)

    doc = db.email_outbox.find_one(
        {"to": email, "kind": "login_code"}, sort=[("created_at", -1)]
    )
    assert doc is not None, "No login_code record in email_outbox"
    print("Outbox doc:", {k: v for k, v in doc.items() if k not in ("html", "_id")})

    status = doc.get("status")
    reason = (doc.get("reason") or "").lower()
    assert status == "sent", f"expected status=sent, got {status}; reason={reason}"
    assert doc.get("provider_id"), f"provider_id missing: {doc}"
    assert "domain is not verified" not in reason
    assert "not verified" not in reason
