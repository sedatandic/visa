"""Security audit fix verification (iteration 103).

Covers:
- SEC-001 WhatsApp webhook fail-closed + verify hub.challenge
- SEC-002 admin OTP is hashed, no code_plain, subject without code
- SEC-003 transactional emails escape HTML in user input
- HARDENING tracking code enumeration returns generic 404
- HARDENING wa_bot status requires phone match OR surname (via admin simulator)
- REGRESSION core flows still work (applications, orders, bundles, products, content)
"""
import io
import os
import re
import sys
import time
from datetime import date

import pytest
import requests
from pymongo import MongoClient

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL missing"

sys.path.insert(0, "/app/backend")
from admin_test_token import admin_token  # noqa: E402

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
ADMIN_EMAIL = (os.environ.get("ADMIN_LOGIN_EMAIL") or "info@dubaivizeonline.com").strip().lower()


@pytest.fixture(scope="module")
def mongo():
    client = MongoClient(MONGO_URL)
    yield client[DB_NAME]
    client.close()


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_headers():
    return {"Authorization": f"Bearer {admin_token()}"}


# ---------------------------------------------------------------- SEC-001 webhook
class TestWebhookSignature:
    def test_verify_get_ok_with_correct_token(self, api):
        r = api.get(
            f"{BASE_URL}/api/whatsapp/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "dubai-vize-hatti",
                "hub.challenge": "12345",
            },
        )
        assert r.status_code == 200, r.text
        assert r.text == "12345"

    def test_verify_get_wrong_token_403(self, api):
        r = api.get(
            f"{BASE_URL}/api/whatsapp/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong-token",
                "hub.challenge": "abc",
            },
        )
        assert r.status_code == 403

    def test_post_without_signature_returns_403_and_no_side_effects(self, api, mongo):
        wa_conv_before = mongo.wa_conversations.count_documents({}) if "wa_conversations" in mongo.list_collection_names() else 0
        wa_msg_before = mongo.wa_messages.count_documents({}) if "wa_messages" in mongo.list_collection_names() else 0
        conv_before = mongo.conversations.count_documents({}) if "conversations" in mongo.list_collection_names() else 0

        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "905000000001",
                            "type": "text",
                            "text": {"body": "unsigned test"},
                        }],
                        "contacts": [{"wa_id": "905000000001", "profile": {"name": "T"}}],
                    }
                }]
            }]
        }
        r = requests.post(f"{BASE_URL}/api/whatsapp/webhook", json=payload)
        assert r.status_code == 403, r.text
        assert "Imza" in r.text or "imza" in r.text.lower() or "dogru" in r.text.lower()
        # Give background task a moment (there should be none)
        time.sleep(1)
        assert (mongo.wa_conversations.count_documents({}) if "wa_conversations" in mongo.list_collection_names() else 0) == wa_conv_before
        assert (mongo.wa_messages.count_documents({}) if "wa_messages" in mongo.list_collection_names() else 0) == wa_msg_before
        assert (mongo.conversations.count_documents({}) if "conversations" in mongo.list_collection_names() else 0) == conv_before

    def test_post_with_bogus_signature_returns_403(self, api):
        r = requests.post(
            f"{BASE_URL}/api/whatsapp/webhook",
            json={"entry": []},
            headers={"X-Hub-Signature-256": "sha256=deadbeef"},
        )
        assert r.status_code == 403


# ---------------------------------------------------------------- SEC-002 admin OTP
class TestAdminOtpNoPlaintext:
    def test_request_code_stores_only_hash_and_subject_hides_code(self, mongo):
        # Clean previous state so we bypass the 60s cooldown and can read a fresh outbox row.
        mongo.admin_login_codes.delete_many({"email": ADMIN_EMAIL})
        before_ids = set(
            d["id"]
            for d in mongo.email_outbox.find(
                {"to": ADMIN_EMAIL, "kind": "admin_login_code"}, {"id": 1}
            )
        )

        r = requests.post(
            f"{BASE_URL}/api/admin/request-code", json={"email": ADMIN_EMAIL}
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("sent") is True

        stored = mongo.admin_login_codes.find_one({"email": ADMIN_EMAIL})
        assert stored is not None
        assert "code_plain" not in stored, f"code_plain must not be stored: {stored.keys()}"
        assert stored.get("code_hash"), "code_hash missing"

        # Newest outbox row for this send
        outbox = mongo.email_outbox.find_one(
            {"to": ADMIN_EMAIL, "kind": "admin_login_code", "id": {"$nin": list(before_ids)}},
            sort=[("created_at", -1)],
        )
        assert outbox is not None, "admin_login_code outbox row missing"
        assert outbox["subject"] == "Yönetici giriş kodunuz", outbox["subject"]
        assert not re.search(r"\b\d{6}\b", outbox["subject"]), "subject leaks 6-digit code"
        assert outbox.get("status") in ("sent", "skipped"), outbox.get("status")

        # Code visible only in HTML body
        m = re.search(r"\b(\d{6})\b", outbox.get("html", ""))
        assert m, "6-digit code missing from email HTML"
        code = m.group(1)

        # Verify code works
        vr = requests.post(
            f"{BASE_URL}/api/admin/verify-code",
            json={"email": ADMIN_EMAIL, "code": code},
        )
        assert vr.status_code == 200, vr.text
        token = vr.json().get("token")
        assert token

        # Token authenticates admin API
        me = requests.get(
            f"{BASE_URL}/api/admin/emails",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me.status_code == 200


# ---------------------------------------------------------------- helpers for app creation
_JPG = bytes.fromhex(
    "ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707"
    "070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c"
    "2837292c30313434341f27393d38323c2e333432ffc0000b08000a000a0101"
    "1100ffc4001f0000010501010101010100000000000000000102030405060708090a"
    "0bffc400b5100002010303020403050504040000017d01020300041105122131410613"
    "516107227114328191a1082342b1c11552d1f02433627282090a161718191a2526"
    "2728292a3435363738393a434445464748494a535455565758595a636465666768"
    "696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7"
    "a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3"
    "e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffda0008010100003f00fbd0ffd9"
)


def _upload(api):
    ids = {}
    for key in ("passport", "photo", "ticket", "hotel"):
        r = api.post(
            f"{BASE_URL}/api/uploads",
            files={"file": ("t.jpg", io.BytesIO(_JPG), "image/jpeg")},
            data={"doc_type": key},
        )
        assert r.status_code == 200, r.text
        ids[key] = r.json()["file_id"]
    return ids


def _app_payload(uploaded, name_last):
    return {
        "contact": {
            "full_name": f"TEST {name_last}",
            "email": "delivered@resend.dev",
            "phone": "+905551110001",
        },
        "travelers": [{
            "first_name": "TEST",
            "last_name": name_last,
            "birth_date": "1990-05-10",
            "nationality": "TR",
            "passport_no": f"U777{int(time.time()) % 100000}",
            "passport_expiry": "2030-01-01",
            "visa_type_id": "visa_30_single",
            "passport_file_id": uploaded["passport"],
            "photo_file_id": uploaded["photo"],
        }],
        "travel": {
            "arrival_date": (date(2026, 10, 10)).isoformat(),
            "departure_date": (date(2026, 10, 20)).isoformat(),
        },
        "addons": {"express": False, "insurance": False, "esim": False},
        "extra_documents": {
            "ticket_file_id": uploaded["ticket"],
            "hotel_file_id": uploaded["hotel"],
        },
        "kvkk_accepted": True,
    }


# ---------------------------------------------------------------- SEC-003 HTML escaping
class TestEmailHtmlEscaping:
    def test_application_email_escapes_user_input(self, mongo, admin_headers):
        # Use a session without json header for file upload
        s = requests.Session()
        uploaded = _upload(s)

        payload = _app_payload(uploaded, "DELIVERED")
        # Inject markup into full_name and traveler first_name
        payload["contact"]["full_name"] = 'TEST <img src=x onerror=alert(1)> DEL'
        payload["travelers"][0]["first_name"] = 'TEST<a href="http://evil.example">tikla</a>'

        r = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert r.status_code == 200, r.text
        body = r.json()
        ref = body["reference_code"]
        assert body.get("email_notification") in ("sent", "skipped"), body

        # Find outbox row for this application
        row = None
        for _ in range(5):
            row = mongo.email_outbox.find_one(
                {"meta.reference_code": ref, "kind": "application_received"},
                sort=[("created_at", -1)],
            )
            if row:
                break
            time.sleep(0.5)
        assert row, f"no outbox row for {ref}"
        html = row["html"]
        assert row.get("status") in ("sent", "skipped"), row.get("status")
        assert "<img src=x" not in html.lower(), "raw <img> present in outbox html"
        assert '<a href="http://evil' not in html.lower(), "raw <a href> present in outbox html"
        assert "&lt;img" in html.lower() or "&lt;a" in html.lower(), "no escaped markup found"

        # cleanup
        mongo.applications.delete_many({"reference_code": ref})
        mongo.email_outbox.delete_many({"meta.reference_code": ref})

    def test_contact_email_escapes_user_input(self, mongo):
        payload = {
            "name": 'TEST <img src=x onerror=alert(1)>',
            "email": "delivered@resend.dev",
            "phone": "+905550000000",
            "subject": "hi",
            "message": 'evil <a href="http://evil.example">tikla</a> content',
        }
        r = requests.post(f"{BASE_URL}/api/contact", json=payload)
        assert r.status_code == 200, r.text
        time.sleep(0.5)
        row = mongo.email_outbox.find_one(
            {"kind": "contact_message"}, sort=[("created_at", -1)]
        )
        assert row, "no contact_message outbox row"
        html = row["html"]
        assert row.get("status") in ("sent", "skipped"), row.get("status")
        assert "<img src=x" not in html.lower()
        assert '<a href="http://evil' not in html.lower()
        assert "&lt;img" in html.lower() or "&lt;a" in html.lower()

        mongo.contact_messages.delete_many({"email": "delivered@resend.dev"})


# ---------------------------------------------------------------- Tracking enumeration
class TestTrackingEnumeration:
    def test_unknown_and_wrong_surname_same_message(self, mongo):
        s = requests.Session()
        uploaded = _upload(s)
        payload = _app_payload(uploaded, "HARDENING")
        r = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert r.status_code == 200, r.text
        ref = r.json()["reference_code"]

        try:
            unknown = requests.get(
                f"{BASE_URL}/api/applications/track",
                params={"code": "ZZZZ9999", "last_name": "Test"},
            )
            wrong = requests.get(
                f"{BASE_URL}/api/applications/track",
                params={"code": ref, "last_name": "WRONGSURNAME"},
            )
            ok = requests.get(
                f"{BASE_URL}/api/applications/track",
                params={"code": ref, "last_name": "HARDENING"},
            )
            assert unknown.status_code == 404, unknown.text
            assert wrong.status_code == 404, wrong.text
            expected = "Takip kodu ve soyad bilgisi eslesmiyor."
            assert unknown.json().get("detail") == expected
            assert wrong.json().get("detail") == expected
            assert ok.status_code == 200, ok.text
        finally:
            mongo.applications.delete_many({"reference_code": ref})
            mongo.email_outbox.delete_many({"meta.reference_code": ref})


# ---------------------------------------------------------------- WA bot surname check
class TestWaBotSurnameVerification:
    def test_status_requires_surname_when_phone_mismatch(self, mongo, admin_headers):
        s = requests.Session()
        uploaded = _upload(s)
        payload = _app_payload(uploaded, "SURNAMEZ")
        r = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert r.status_code == 200, r.text
        ref = r.json()["reference_code"]
        random_phone = "905990000001"

        try:
            # No surname in message
            r1 = requests.post(
                f"{BASE_URL}/api/admin/whatsapp/ai/simulate/message",
                json={"wa_id": random_phone, "text": f"Merhaba {ref} durumu nedir?", "profile_name": ""},
                headers=admin_headers,
            )
            assert r1.status_code == 200, r1.text
            reply1 = (r1.json().get("reply") or {}).get("text", "").lower()
            assert "doğrulama" in reply1 or "soyad" in reply1, reply1

            # With surname
            r2 = requests.post(
                f"{BASE_URL}/api/admin/whatsapp/ai/simulate/message",
                json={"wa_id": random_phone, "text": f"{ref} soyad SURNAMEZ", "profile_name": ""},
                headers=admin_headers,
            )
            assert r2.status_code == 200, r2.text
            reply2 = (r2.json().get("reply") or {}).get("text", "").lower()
            assert "durumu" in reply2 or "onayland" in reply2 or "belge" in reply2 or "inceleme" in reply2, reply2
        finally:
            mongo.applications.delete_many({"reference_code": ref})
            mongo.email_outbox.delete_many({"meta.reference_code": ref})
            mongo.conversations.delete_many({"wa_id": random_phone})


# ---------------------------------------------------------------- REGRESSION
class TestRegressionCore:
    def test_bundles_products_content(self, api):
        for path in ("/api/bundles", "/api/bundles?visa_days=30", "/api/products", "/api/content/site"):
            r = api.get(f"{BASE_URL}{path}")
            assert r.status_code == 200, f"{path} -> {r.status_code} {r.text[:200]}"
        # Bundle by visa_days must expose pack_family
        r = api.get(f"{BASE_URL}/api/bundles?visa_days=30")
        data = r.json()
        items = data.get("items") if isinstance(data, dict) else data
        assert items, f"no bundle items: {data}"
        # pack_family is a bundle id; it should be present for visa_days=30
        ids = [i.get("id") for i in items]
        assert "pack_family" in ids, f"pack_family bundle missing: {ids}"

    def test_normal_application_ok(self, mongo):
        s = requests.Session()
        uploaded = _upload(s)
        payload = _app_payload(uploaded, "REGRESSION")
        r = requests.post(f"{BASE_URL}/api/applications", json=payload)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("reference_code")
        assert body.get("email_notification") in ("sent", "skipped"), body
        ref = body["reference_code"]
        mongo.applications.delete_many({"reference_code": ref})
        mongo.email_outbox.delete_many({"meta.reference_code": ref})

    def test_order_esim(self, mongo):
        payload = {
            "items": [{"product_id": "esim_1gb", "quantity": 1}],
            "contact": {
                "full_name": "TEST REGRESSION",
                "email": "delivered@resend.dev",
                "phone": "+905551110002",
            },
            "payment_method": "card",
        }
        r = requests.post(f"{BASE_URL}/api/orders", json=payload)
        assert r.status_code == 200, r.text
        order = r.json().get("order") or {}
        assert order.get("reference_code"), order
        mongo.orders.delete_many({"id": order.get("id")})
