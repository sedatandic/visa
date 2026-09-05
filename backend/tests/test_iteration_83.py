"""Iteration 83 backend tests.

Focuses:
- /api/photo/check background analysis (dark vs. white passport photos)
- Regression: /api/contact, /api/uploads, /api/applications with new +90 phone
- Regression: admin OTP + customer OTP flows still work
"""
import os
import re
import time

import pytest
import requests

def _read_env(name: str) -> str:
    val = os.environ.get(name)
    if val:
        return val
    for path in ("/app/frontend/.env", "/app/backend/.env"):
        try:
            with open(path) as fh:
                for line in fh:
                    if line.startswith(name + "="):
                        val = line.split("=", 1)[1].strip()
                        if val.startswith('"') and val.endswith('"'):
                            val = val[1:-1]
                        return val
        except FileNotFoundError:
            pass
    raise RuntimeError(f"{name} not set")


BASE_URL = _read_env("REACT_APP_BACKEND_URL").rstrip("/")

# Fixtures --------------------------------------------------------------------
DARK_PHOTO_URL = "https://customer-assets-rejwkqb3.emergentagent.net/job_1d50e59a-d91d-4df8-96b0-06dee815c3de/artifacts/1nnotrcm_52492013966_e452741b30_o.jpg"
WHITE_PHOTO_URL = "https://customer-assets-rejwkqb3.emergentagent.net/job_visa-application-ae/artifacts/qcg2gulz_IMG_0655.webp"


@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    return sess


def _fetch(url: str) -> bytes:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.content


def _upload_photo(sess, data: bytes, filename: str, mime: str, doc_type: str = "photo") -> str:
    resp = sess.post(
        f"{BASE_URL}/api/uploads",
        files={"file": (filename, data, mime)},
        data={"doc_type": doc_type},
        timeout=60,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("file_id")
    return body["file_id"]


# ---------------------------------------------------------------- photo/check
class TestPhotoBackground:
    """Deterministic background analyser exposed via /api/photo/check."""

    def test_dark_background_photo_is_rejected(self, s):
        file_id = _upload_photo(s, _fetch(DARK_PHOTO_URL), "dark.jpg", "image/jpeg")
        r = s.post(f"{BASE_URL}/api/photo/check", data={"file_id": file_id}, timeout=60)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("checked") is True
        assert body.get("ok") is False, f"expected ok=false, got {body}"
        failed = body.get("failed") or []
        assert "background_ok" in failed, f"'background_ok' missing from failed: {failed}"
        assert "beyaz" in (body.get("message") or "").lower(), body.get("message")
        assert body.get("background", {}).get("ok") is False

    def test_white_background_photo_is_accepted(self, s):
        file_id = _upload_photo(s, _fetch(WHITE_PHOTO_URL), "white.webp", "image/webp")
        r = s.post(f"{BASE_URL}/api/photo/check", data={"file_id": file_id}, timeout=60)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("checked") is True
        bg = body.get("background") or {}
        assert bg.get("checked") is True
        assert bg.get("ok") is True, f"expected background.ok=true, got {bg}"
        assert "background_ok" not in (body.get("failed") or [])


# ---------------------------------------------------------------- regression: contact + uploads
class TestContactAndUploadRegression:
    def test_contact_ok(self, s):
        payload = {
            "name": "TEST_iter83 Kullanici",
            "email": "delivered@resend.dev",
            "phone": "+90 532 588 26 30",
            "subject": "iter83 regresyon",
            "message": "Bu bir otomatik test mesajidir (iter83).",
        }
        r = s.post(f"{BASE_URL}/api/contact", json=payload, timeout=30)
        assert r.status_code == 200, r.text
        assert r.json().get("ok") is True

    def test_uploads_ok(self, s):
        # 1x1 PNG
        png = bytes.fromhex(
            "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000D49"
            "44415478DA6300010000000500010D0A2DB40000000049454E44AE426082"
        )
        r = s.post(
            f"{BASE_URL}/api/uploads",
            files={"file": ("t.png", png, "image/png")},
            data={"doc_type": "other"},
            timeout=30,
        )
        assert r.status_code == 200, r.text
        assert r.json().get("file_id")


# ---------------------------------------------------------------- regression: applications e2e
class TestApplicationCreate:
    def _upload_dummy(self, s, name):
        png = bytes.fromhex(
            "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000D49"
            "44415478DA6300010000000500010D0A2DB40000000049454E44AE426082"
        )
        r = s.post(
            f"{BASE_URL}/api/uploads",
            files={"file": (name, png, "image/png")},
            data={"doc_type": "passport"},
        )
        r.raise_for_status()
        return r.json()["file_id"]

    def test_create_application_with_plus90_phone(self, s):
        # Pick a visa type id
        vt = s.get(f"{BASE_URL}/api/visa-types", timeout=15).json()
        assert isinstance(vt, list) and vt, "no visa types available"
        visa_id = vt[0]["id"]

        passport_fid = self._upload_dummy(s, "passport.png")
        photo_fid = self._upload_dummy(s, "photo.png")

        payload = {
            "contact": {
                "full_name": "TEST_iter83 Yolcu",
                "email": "delivered@resend.dev",
                "phone": "+90 532 588 26 30",
                "address_city": "Istanbul",
                "whatsapp_optin": True,
            },
            "travelers": [
                {
                    "first_name": "AHMET",
                    "last_name": "YILMAZ",
                    "birth_date": "1990-05-15",
                    "gender": "male",
                    "applicant_type": "adult",
                    "nationality": "TR",
                    "passport_no": "U12345678",
                    "passport_expiry": "2032-12-31",
                    "visa_type_id": visa_id,
                    "passport_file_id": passport_fid,
                    "photo_file_id": photo_fid,
                }
            ],
            "travel": {
                "arrival_date": "",
                "departure_date": "",
                "dates_unknown": True,
                "travel_window": "1-3ay",
                "purpose": "tourism",
                "birth_country": "TR",
            },
            "addons": {},
            "extra_documents": {},
            "kvkk_accepted": True,
        }
        r = s.post(f"{BASE_URL}/api/applications", json=payload, timeout=60)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("reference_code", "").startswith("DV-"), body.get("reference_code")
        assert body.get("contact", {}).get("phone") == "+90 532 588 26 30"


# ---------------------------------------------------------------- regression: OTP flows
class TestOTPRegression:
    def test_admin_otp_still_works(self, s):
        # Clear any 60s cooldown by cleaning admin_login_codes for our email
        from pymongo import MongoClient
        from motor.motor_asyncio import AsyncIOMotorClient  # noqa: F401

        mongo_url = _read_env("MONGO_URL")
        db_name = _read_env("DB_NAME")
        MongoClient(mongo_url)[db_name]["admin_login_codes"].delete_many(
            {"email": "info@dubaivizeonline.com"}
        )

        r = s.post(
            f"{BASE_URL}/api/admin/request-code",
            json={"email": "info@dubaivizeonline.com"},
            timeout=30,
        )
        assert r.status_code == 200, r.text

        doc = MongoClient(mongo_url)[db_name]["admin_login_codes"].find_one(
            {"email": "info@dubaivizeonline.com"}, sort=[("created_at", -1)]
        )
        assert doc and doc.get("code_plain"), doc
        r2 = s.post(
            f"{BASE_URL}/api/admin/verify-code",
            json={"email": "info@dubaivizeonline.com", "code": doc["code_plain"]},
            timeout=30,
        )
        assert r2.status_code == 200, r2.text
        assert r2.json().get("token")

    def test_customer_otp_request(self, s):
        from pymongo import MongoClient

        email = "delivered@resend.dev"
        mongo_url = _read_env("MONGO_URL")
        db_name = _read_env("DB_NAME")
        client = MongoClient(mongo_url)[db_name]
        # Clean 60s cooldown
        client["login_codes"].delete_many({"email": email})

        r = s.post(
            f"{BASE_URL}/api/account/request-code",
            json={"email": email},
            timeout=30,
        )
        assert r.status_code == 200, r.text
        # verify email was queued
        outbox = client["email_outbox"].find_one(
            {"to": email, "kind": "login_code"}, sort=[("created_at", -1)]
        )
        assert outbox, "no login_code email in outbox"
        html = outbox.get("html") or ""
        m = re.search(r">\s*(\d{6})\s*<", html)
        assert m, "cannot parse 6-digit code from email"
        code = m.group(1)
        r2 = s.post(
            f"{BASE_URL}/api/account/verify-code",
            json={"email": email, "code": code},
            timeout=30,
        )
        assert r2.status_code == 200, r2.text
        assert r2.json().get("token")
