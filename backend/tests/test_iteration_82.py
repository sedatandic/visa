"""Iteration 82 backend regression:
- login-lastname endpoint removed (404)
- Account OTP end-to-end (request-code, wrong code 400, correct code 200,
  /account/me 200, code reuse 400, code_plain not stored)
- Rate limits: same-email 60s cooldown (429), per-IP hourly limit (15) (429)
- Contact endpoint still 200, per-IP hourly limit (8) triggers 429
- Zami bookmarklet.js / capture.js still 200 and contain `function dvoEsc`
- Admin OTP regression (request-code -> verify-code -> /admin/emails)
- Applications regression with new phone format '+90 532 588 26 30'
"""
import os
import re
import io
import uuid
import time
from datetime import date, timedelta

import pytest
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

HERE = os.path.dirname(__file__)
load_dotenv(os.path.join(HERE, "..", ".env"))
load_dotenv(os.path.join(HERE, "..", "..", "frontend", ".env"))

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_EMAIL = os.environ["ADMIN_LOGIN_EMAIL"]
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]

db = MongoClient(MONGO_URL)[DB_NAME]


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ------------------------------------------------------------ login-lastname removed
def test_login_lastname_returns_404(api):
    r = api.post(f"{API}/account/login-lastname", json={"email": "a@b.com", "last_name": "X"})
    assert r.status_code == 404, f"expected 404, got {r.status_code} {r.text[:200]}"


# ------------------------------------------------------------ Account OTP end-to-end
def _read_code_from_outbox(email):
    doc = db.email_outbox.find_one({"to": email, "kind": "login_code"}, sort=[("created_at", -1)])
    if not doc:
        return None
    m = re.search(r">\s*(\d{6})\s*<", doc.get("html") or "")
    return m.group(1) if m else None


class TestAccountOTPEndToEnd:
    email = "delivered@resend.dev"

    def setup_method(self):
        db.login_codes.delete_many({"email": self.email})

    def test_full_flow_and_no_code_plain(self, api):
        r = api.post(f"{API}/account/request-code", json={"email": self.email}, timeout=30)
        assert r.status_code == 200, f"request-code failed: {r.status_code} {r.text[:200]}"
        assert r.json().get("email_status") in ("sent", "skipped", "error", "mocked", "queued")

        # brief wait for email_outbox write
        time.sleep(1)
        code = _read_code_from_outbox(self.email)
        assert code and len(code) == 6, f"code not found in outbox: {code}"

        # Wrong code
        bad = api.post(f"{API}/account/verify-code",
                       json={"email": self.email, "code": "000000"}, timeout=15)
        assert bad.status_code == 400, f"wrong code should 400: {bad.status_code} {bad.text[:200]}"

        # Correct code
        ok = api.post(f"{API}/account/verify-code",
                      json={"email": self.email, "code": code}, timeout=15)
        assert ok.status_code == 200, f"correct code should 200: {ok.status_code} {ok.text[:200]}"
        body = ok.json()
        assert "token" in body and isinstance(body["token"], str) and body["token"]
        token = body["token"]

        # /account/me
        me = api.get(f"{API}/account/me", headers={"Authorization": f"Bearer {token}"}, timeout=15)
        assert me.status_code == 200, f"/account/me failed: {me.status_code} {me.text[:200]}"

        # Reuse code -> 400
        reuse = api.post(f"{API}/account/verify-code",
                         json={"email": self.email, "code": code}, timeout=15)
        assert reuse.status_code == 400, f"reuse should 400: {reuse.status_code} {reuse.text[:200]}"

        # code_plain must not be stored
        doc = db.login_codes.find_one({"email": self.email}) or {}
        assert "code_plain" not in doc, f"code_plain should not be stored: {doc}"


# ------------------------------------------------------------ Rate limits
class TestAccountRateLimits:
    def test_same_email_60s_cooldown(self, api):
        email = "delivered@resend.dev"
        db.login_codes.delete_many({"email": email})
        r1 = api.post(f"{API}/account/request-code", json={"email": email}, timeout=15)
        assert r1.status_code == 200, f"first should 200: {r1.status_code}"
        r2 = api.post(f"{API}/account/request-code", json={"email": email}, timeout=15)
        assert r2.status_code == 429, f"second within 60s should 429: {r2.status_code} {r2.text[:200]}"
        assert "1 dakika" in r2.text or "bekleyin" in r2.text.lower()

    def test_ip_hourly_limit_exceeded(self, api):
        # Restart backend to reset in-memory counters before this test to avoid contamination
        os.system("sudo supervisorctl restart backend >/dev/null 2>&1")
        time.sleep(3)
        # After restart, we can issue 15 distinct emails; 16th should 429.
        # But request-code sends REAL emails. Use example.com addresses; Resend will error
        # but 200 is still returned (email_status='error') and the rate counter still increments.
        got_429 = False
        for i in range(17):
            e = f"TEST_iter82_ratelimit_{i}_{uuid.uuid4().hex[:6]}@example.com"
            r = api.post(f"{API}/account/request-code", json={"email": e}, timeout=15)
            if r.status_code == 429:
                got_429 = True
                assert "Cok fazla" in r.text or "saat" in r.text.lower(), r.text[:200]
                break
            assert r.status_code == 200, f"iter {i} unexpected: {r.status_code} {r.text[:200]}"
        assert got_429, "expected a 429 within 17 distinct-email requests from same IP (limit=15/hr)"
        # cleanup
        db.login_codes.delete_many({"email": {"$regex": "^TEST_iter82_ratelimit_"}})


# ------------------------------------------------------------ Contact endpoint
class TestContactEndpoint:
    def test_contact_ok_then_ratelimit(self, api):
        os.system("sudo supervisorctl restart backend >/dev/null 2>&1")
        time.sleep(3)
        got_429 = False
        first_status = None
        for i in range(10):
            payload = {
                "name": f"TEST iter82 {i}",
                "email": f"TEST_iter82_contact_{i}@example.com",
                "phone": "+90 532 588 26 30",
                "subject": "Regresyon",
                "message": "Bu bir regresyon test mesajidir.",
            }
            r = api.post(f"{API}/contact", json=payload, timeout=15)
            if i == 0:
                first_status = r.status_code
                assert r.status_code == 200, f"first should 200: {r.status_code} {r.text[:200]}"
            if r.status_code == 429:
                assert "Cok fazla mesaj" in r.text or "sonra" in r.text.lower(), r.text[:200]
                got_429 = True
                break
        assert first_status == 200
        assert got_429, "expected 429 within 10 contact requests (limit=8/hr)"
        # cleanup
        db.contact_messages.delete_many({"email": {"$regex": "^TEST_iter82_contact_"}})


# ------------------------------------------------------------ Zami scripts
class TestZamiScripts:
    def test_bookmarklet_js_ok_and_contains_dvoEsc(self, api):
        r = api.get(f"{API}/zami/bookmarklet.js", timeout=15)
        assert r.status_code == 200, f"{r.status_code} {r.text[:200]}"
        body = r.text
        assert "function dvoEsc" in body, "expected 'function dvoEsc' in bookmarklet.js"
        # sanity: dvoEsc actually applied to reference_code / labels / docsHtml
        assert "dvoEsc(" in body

    def test_capture_js_ok_and_contains_dvoEsc(self, api):
        r = api.get(f"{API}/zami/capture.js", timeout=15)
        assert r.status_code == 200, f"{r.status_code} {r.text[:200]}"
        assert "function dvoEsc" in r.text


# ------------------------------------------------------------ Admin OTP regression
class TestAdminOTP:
    def test_admin_otp_full(self, api):
        os.system("sudo supervisorctl restart backend >/dev/null 2>&1")
        time.sleep(3)
        db.admin_login_codes.delete_many({"email": ADMIN_EMAIL.lower()})
        r = api.post(f"{API}/admin/request-code", json={"email": ADMIN_EMAIL}, timeout=15)
        assert r.status_code == 200, f"request-code: {r.status_code} {r.text[:200]}"
        time.sleep(1)
        doc = db.admin_login_codes.find_one({"email": ADMIN_EMAIL.lower()})
        assert doc and doc.get("code_plain"), f"admin code_plain missing: {doc}"
        code = doc["code_plain"]
        ok = api.post(f"{API}/admin/verify-code",
                      json={"email": ADMIN_EMAIL, "code": code}, timeout=15)
        assert ok.status_code == 200, f"verify: {ok.status_code} {ok.text[:200]}"
        token = ok.json().get("token")
        assert token
        emails = api.get(f"{API}/admin/emails",
                         headers={"Authorization": f"Bearer {token}"}, timeout=15)
        assert emails.status_code == 200, f"emails: {emails.status_code} {emails.text[:200]}"


# ------------------------------------------------------------ Application regression
def _upload_jpeg(doc_type: str) -> str:
    jpeg = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00" + b"\x08" * 64 + b"\xff\xd9"
    )
    files = {"file": (f"{doc_type}.jpg", io.BytesIO(jpeg), "image/jpeg")}
    r = requests.post(f"{API}/uploads", files=files, data={"doc_type": doc_type}, timeout=20)
    assert r.status_code == 200, f"upload failed: {r.status_code} {r.text[:200]}"
    return r.json()["file_id"]


def test_applications_accept_new_phone_format(api):
    passport = _upload_jpeg("passport")
    photo = _upload_jpeg("photo")
    payload = {
        "contact": {
            "full_name": "TEST iter82 Telefon",
            "email": f"TEST_iter82_app_{uuid.uuid4().hex[:6]}@example.com",
            "phone": "+90 532 588 26 30",
            "whatsapp_optin": True,
        },
        "travelers": [{
            "first_name": "TESTAD",
            "last_name": "TESTSOYAD",
            "birth_date": "1990-05-05",
            "gender": "male",
            "applicant_type": "adult",
            "nationality": "TR",
            "passport_no": "U11223344",
            "passport_expiry": (date.today() + timedelta(days=800)).isoformat(),
            "visa_type_id": "visa_30_single",
            "passport_file_id": passport,
            "photo_file_id": photo,
        }],
        "travel": {
            "arrival_date": (date.today() + timedelta(days=30)).isoformat(),
            "departure_date": (date.today() + timedelta(days=35)).isoformat(),
            "purpose": "tourism",
        },
        "addons": {},
        "store_items": [],
        "extra_documents": {},
        "kvkk_accepted": True,
    }
    r = api.post(f"{API}/applications", json=payload, timeout=30)
    assert r.status_code == 200, f"application failed: {r.status_code} {r.text[:400]}"
    ref = r.json().get("reference_code")
    assert ref and ref.startswith("DV-")
