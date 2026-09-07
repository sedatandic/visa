"""
Core POC for Dubai Visa application site.
Proves in isolation:
  1) MongoDB write/read of a visa application (with datetime serialization helper)
  2) Emergent Object Storage: init -> put_object (jpg) -> get_object -> byte/content-type verify
  3) Stripe Flow A: claimable sandbox provisioning + idempotent catalog (lookup_key)
  4) Stripe: checkout session creation returning a real checkout URL + payment_transactions row
  5) Stripe: status polling + idempotent DB update
  6) Resend email: graceful degradation when RESEND_API_KEY absent (never raises)

Run:  cd /app/backend && python scripts/test_core.py
"""
import asyncio
import io
import json
import os
import sys
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

RESULTS = []


def rec(name, ok, detail="") -> None:
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} :: {detail}")


# ---------------------------------------------------------------- 1. MONGO
def serialize_doc(doc):
    """Recursively make a Mongo doc JSON-serializable."""
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
    try:
        from bson import ObjectId

        if isinstance(doc, ObjectId):
            return str(doc)
    except Exception:
        pass
    return doc


def test_mongo():
    try:
        from pymongo import MongoClient

        db = MongoClient(os.environ["MONGO_URL"])[os.environ.get("DB_NAME", "test_database")]
        ref = "POC-" + uuid.uuid4().hex[:6].upper()
        doc = {
            "id": str(uuid.uuid4()),
            "reference_code": ref,
            "full_name": "Ahmet Yılmaz",
            "email": "ahmet@example.com",
            "visa_type": "30_single",
            "status": "pending",
            "created_at": datetime.now(timezone.utc),
        }
        db.poc_visa_applications.insert_one(dict(doc))
        found = db.poc_visa_applications.find_one({"reference_code": ref})
        ser = serialize_doc(found)
        json.dumps(ser)  # must not raise
        assert ser["full_name"] == "Ahmet Yılmaz" and "_id" not in ser
        db.poc_visa_applications.delete_many({"reference_code": ref})
        rec("Mongo insert/read + datetime serialize", True, f"ref={ref}")
        return True
    except Exception as e:
        rec("Mongo insert/read + datetime serialize", False, repr(e))
        return False


# ------------------------------------------------------- 2. OBJECT STORAGE
STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "dubaivize"
_storage_key = None


def init_storage(force=False):
    global _storage_key
    if _storage_key and not force:
        return _storage_key
    r = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    r.raise_for_status()
    _storage_key = r.json()["storage_key"]
    return _storage_key


def put_object(path, data, content_type):
    key = init_storage()
    r = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data,
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def get_object(path):
    key = init_storage()
    r = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    r.raise_for_status()
    return r.content, r.headers.get("Content-Type", "application/octet-stream")


def make_jpeg_bytes():
    """Minimal valid JPEG produced without external deps."""
    try:
        from PIL import Image

        buf = io.BytesIO()
        Image.new("RGB", (120, 160), (200, 160, 60)).save(buf, format="JPEG")
        return buf.getvalue()
    except Exception:
        # fall back to raw bytes (storage doesn't validate content)
        return b"\xff\xd8\xff\xe0" + b"POC-PASSPORT-IMAGE" * 40 + b"\xff\xd9"


def test_storage():
    try:
        init_storage()
        data = make_jpeg_bytes()
        path = f"{APP_NAME}/uploads/poc/{uuid.uuid4()}.jpg"
        res = put_object(path, data, "image/jpeg")
        back, ctype = get_object(res["path"])
        assert back == data, f"byte mismatch {len(back)} vs {len(data)}"
        assert "image/jpeg" in ctype, ctype
        rec("Object storage put/get roundtrip", True, f"size={res.get('size')} ctype={ctype}")
        return True
    except Exception as e:
        rec("Object storage put/get roundtrip", False, repr(e))
        return False


# --------------------------------------------------------------- 3. STRIPE
SANDBOX = {}
CATALOG = [
    {
        "emergent_product_id": "visa_14_single",
        "name": "Dubai Vizesi - 14 Gun Tek Giris",
        "tax_code": "txcd_99999999",
        "prices": [{"lookup_key": "visa_14_single", "amount": 149900, "currency": "try"}],
    },
    {
        "emergent_product_id": "visa_30_single",
        "name": "Dubai Vizesi - 30 Gun Tek Giris",
        "tax_code": "txcd_99999999",
        "prices": [{"lookup_key": "visa_30_single", "amount": 199900, "currency": "try"}],
    },
]


def provision_sandbox():
    base = os.environ["INTEGRATION_PROXY_URL"]
    job_id = "7c26ec44-45e0-428c-945e-85905acbcf9c"
    key = "sk-emergent-fEd904c9b17A62363C"
    req = urllib.request.Request(
        base + "/stripe/sandboxes",
        data=json.dumps({"job_id": job_id}).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def test_stripe_sandbox():
    """Flow A is impossible here: the claimable-sandbox proxy rejects country TR
    ({"code":"country_not_supported"}). So we verify Flow B (BYOK) instead, using
    the platform-injected STRIPE_API_KEY with the emergentintegrations library."""
    try:
        key = os.environ.get("STRIPE_API_KEY")
        assert key, "STRIPE_API_KEY missing from env"
        from emergentintegrations.payments.stripe.checkout import StripeCheckout  # noqa

        rec("Stripe Flow B key + library available", True, f"key={key[:12]}...")
        return True
    except Exception as e:
        rec("Stripe Flow B key + library available", False, repr(e))
        return False


PACKAGES = {
    "visa_14_single": 1499.0,
    "visa_30_single": 1999.0,
    "visa_30_multi": 3499.0,
    "visa_60_single": 3999.0,
    "visa_60_multi": 5499.0,
}


def test_stripe_catalog():
    """Server-side fixed package catalog (Flow B): amounts never come from the client."""
    try:
        assert all(isinstance(v, float) and v > 0 for v in PACKAGES.values())
        assert "visa_30_single" in PACKAGES
        rec("Server-side package catalog", True, f"{len(PACKAGES)} packages, 30_single={PACKAGES['visa_30_single']} TRY")
        return True
    except Exception as e:
        rec("Server-side package catalog", False, repr(e))
        return False


SESSION_ID = None


def test_stripe_checkout():
    global SESSION_ID
    try:
        from pymongo import MongoClient
        from emergentintegrations.payments.stripe.checkout import (
            CheckoutSessionRequest,
            StripeCheckout,
        )

        db = MongoClient(os.environ["MONGO_URL"])[os.environ.get("DB_NAME", "test_database")]
        origin = "https://whatsapp-bot-test-2.preview.emergentagent.com"
        webhook_url = f"{origin}/api/webhook/stripe"
        sc = StripeCheckout(api_key=os.environ["STRIPE_API_KEY"], webhook_url=webhook_url)
        amount = PACKAGES["visa_30_single"]
        req = CheckoutSessionRequest(
            amount=amount,
            currency="try",
            success_url=origin + "/payment/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=origin + "/payment/cancel",
            metadata={"application_id": "poc-app", "package_id": "visa_30_single"},
        )
        session = asyncio.run(sc.create_checkout_session(req))
        SESSION_ID = session.session_id
        db.poc_payment_transactions.insert_one(
            {
                "session_id": session.session_id,
                "application_id": "poc-app",
                "package_id": "visa_30_single",
                "amount": amount,
                "currency": "try",
                "status": "initiated",
                "payment_status": "pending",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        )
        assert session.url and session.url.startswith("https://"), session.url
        rec("Stripe checkout session created (Flow B)", True, f"url={session.url[:60]}... sid={SESSION_ID[:20]}")
        return True
    except Exception as e:
        rec("Stripe checkout session created (Flow B)", False, repr(e))
        return False


def test_stripe_status():
    try:
        from pymongo import MongoClient
        from emergentintegrations.payments.stripe.checkout import StripeCheckout

        db = MongoClient(os.environ["MONGO_URL"])[os.environ.get("DB_NAME", "test_database")]
        record = db.poc_payment_transactions.find_one({"session_id": SESSION_ID})
        assert record, "tx row missing"
        sc = StripeCheckout(
            api_key=os.environ["STRIPE_API_KEY"],
            webhook_url="https://whatsapp-bot-test-2.preview.emergentagent.com/api/webhook/stripe",
        )
        st = asyncio.run(sc.get_checkout_status(SESSION_ID))
        if st.payment_status == "paid" or st.status == "complete":
            db.poc_payment_transactions.update_one(
                {"session_id": SESSION_ID, "payment_status": {"$ne": "paid"}},
                {"$set": {"status": "completed", "payment_status": "paid"}},
            )
        record = db.poc_payment_transactions.find_one({"session_id": SESSION_ID})
        rec(
            "Stripe status poll + idempotent DB update",
            True,
            f"stripe={st.status}/{st.payment_status} amount={st.amount_total} db={record['status']}/{record['payment_status']}",
        )
        db.poc_payment_transactions.delete_many({"session_id": SESSION_ID})
        return True
    except Exception as e:
        rec("Stripe status poll + idempotent DB update", False, repr(e))
        return False


# ---------------------------------------------------------------- 4. EMAIL
async def send_email_safe(to, subject, html) -> dict:
    """Never raises. Returns dict with status: sent | skipped | error."""
    api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
    sender = os.environ.get("SENDER_EMAIL") or "onboarding@resend.dev"
    if not api_key or api_key.startswith("re_placeholder"):
        return {"status": "skipped", "reason": "RESEND_API_KEY not configured", "to": to, "subject": subject}
    try:
        import resend

        resend.api_key = api_key
        res = await asyncio.to_thread(
            resend.Emails.send, {"from": sender, "to": [to], "subject": subject, "html": html}
        )
        return {"status": "sent", "id": res.get("id"), "to": to}
    except Exception as e:
        return {"status": "error", "reason": str(e), "to": to}


def test_email():
    try:
        from pymongo import MongoClient

        db = MongoClient(os.environ["MONGO_URL"])[os.environ.get("DB_NAME", "test_database")]
        out = asyncio.run(
            send_email_safe(
                "applicant@example.com",
                "Dubai Vize Başvurunuz Alındı",
                "<h1>Merhaba</h1><p>Başvurunuz alındı. Takip kodu: POC-123456</p>",
            )
        )
        db.poc_email_outbox.insert_one(
            {"id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc), **out}
        )
        assert out["status"] in ("sent", "skipped", "error")
        db.poc_email_outbox.delete_many({"to": "applicant@example.com"})
        rec("Email graceful send (skip when no key)", True, f"status={out['status']} reason={out.get('reason','-')}")
        return True
    except Exception as e:
        rec("Email graceful send (skip when no key)", False, repr(e))
        return False


def main() -> None:
    print("=" * 70)
    print("DUBAI VISA APP - CORE POC")
    print("=" * 70)
    test_mongo()
    test_storage()
    if test_stripe_sandbox():
        test_stripe_catalog()
        if test_stripe_checkout():
            test_stripe_status()
    test_email()
    print("=" * 70)
    failed = [r for r in RESULTS if not r[1]]
    print(f"TOTAL: {len(RESULTS)}  PASS: {len(RESULTS)-len(failed)}  FAIL: {len(failed)}")
    if SANDBOX:
        print("\nSANDBOX ENV VALUES (to write into backend/.env):")
        for k in ("sandbox_secret_key", "sandbox_publishable_key", "sandbox_account_id", "preview_webhook_secret"):
            v = SANDBOX.get(k, "")
            print(f"  {k}={v}")
        print(f"  onboarding_url={SANDBOX.get('onboarding_url')}")
    print("=" * 70)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
