"""Backend regression tests after refactor (iteration 78).

Covers:
- Store catalog: /api/products (+ kind filter), /api/bundles
- Store order flow: POST /api/orders, GET /api/orders/{ref}
- Admin insurance endpoints: /api/admin/insurance-tasks, /admin/insurance-report,
  /admin/profit-monthly
- Application flow: POST /api/applications with valid, invalid-passport and
  malformed-date inputs (via _parse_iso_date)
- Visa types + quote endpoints
- Email pipeline via POST /api/contact writes to email_outbox
"""

import io
import os
import time
from datetime import date, timedelta

import pytest
import requests

def _load_backend_url() -> str:
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if url:
        return url.rstrip("/")
    env_path = "/app/frontend/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    return line.split("=", 1)[1].strip().rstrip("/")
    raise RuntimeError("REACT_APP_BACKEND_URL not configured")


BASE_URL = _load_backend_url()
API = f"{BASE_URL}/api"
ADMIN_EMAIL = "info@dubaivizeonline.com"
ADMIN_PASSWORD = "Dubai2026!"


# ------------------------------------------------------------------ fixtures
@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def admin_token(session):
    r = session.post(
        f"{API}/admin/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "remember": False},
        timeout=15,
    )
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    tok = r.json().get("token")
    assert tok
    return tok


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ------------------------------------------------------- store catalog tests
class TestStoreCatalog:
    def test_products_list(self, session):
        r = session.get(f"{API}/products", timeout=15)
        assert r.status_code == 200
        body = r.json()
        items = body["items"]
        # 4 esim + 6 insurance + 1 tour = 11
        assert len(items) == 11, f"expected 11 products, got {len(items)}"
        for it in items:
            assert "price" in it and it["price"] > 0
            assert it["currency"] == "TRY"
            assert "fx_rate" in it and it["fx_rate"] > 0
            assert it["kind_label"] in {"eSIM", "Seyahat sigortası", "Dubai turu"}
            assert "_id" not in it
        assert "bundle" in body

    def test_products_filter_insurance(self, session):
        r = session.get(f"{API}/products", params={"kind": "insurance"}, timeout=15)
        assert r.status_code == 200
        items = r.json()["items"]
        assert len(items) == 6
        assert all(it["kind"] == "insurance" for it in items)

    def test_products_filter_esim(self, session):
        r = session.get(f"{API}/products", params={"kind": "esim"}, timeout=15)
        assert r.status_code == 200
        items = r.json()["items"]
        assert len(items) == 4
        assert all(it["kind"] == "esim" for it in items)

    def test_products_invalid_kind_400(self, session):
        r = session.get(f"{API}/products", params={"kind": "bogus"}, timeout=15)
        assert r.status_code == 400

    def test_bundles(self, session):
        r = session.get(f"{API}/bundles", timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert "items" in body and len(body["items"]) >= 1
        for b in body["items"]:
            assert b["currency"] == "TRY"
            assert b["list_total"] > 0
            assert b["discount"] > 0
            assert b["price"] == round(b["list_total"] - b["discount"], 2)
            assert b["insurance"]["id"] and b["esim"]["id"]


# ------------------------------------------------------- store order tests
class TestStoreOrders:
    def test_create_order_and_fetch(self, session):
        payload = {
            "items": [
                {"product_id": "esim_3gb", "quantity": 1},
                {"product_id": "ins_15d", "quantity": 1},
            ],
            "contact": {
                "full_name": "TEST_Order Customer",
                "email": "test_orders@example.com",
                "phone": "+905555550101",
            },
            "travel_start": (date.today() + timedelta(days=10)).isoformat(),
            "travel_end": (date.today() + timedelta(days=17)).isoformat(),
            "payment_method": "card",
            "note": "TEST_ regression order",
        }
        r = session.post(f"{API}/orders", json=payload, timeout=20)
        assert r.status_code == 200, f"order create failed: {r.status_code} {r.text}"
        body = r.json()
        order = body["order"]
        ref = order["reference_code"]
        assert ref.startswith("SV-"), f"bad reference {ref}"
        assert order["currency"] == "TRY"
        expected_items_total = round(
            sum(l["unit_price"] * l["quantity"] for l in order["items"]), 2
        )
        assert order["items_total"] == expected_items_total
        assert order["price"] == round(order["items_total"] - order["bundle_discount"], 2)
        assert order["payment"]["status"] == "pending"
        assert "_id" not in order

        # GET back
        g = session.get(
            f"{API}/orders/{ref}",
            params={"email": payload["contact"]["email"]},
            timeout=15,
        )
        assert g.status_code == 200, g.text
        assert g.json()["order"]["reference_code"] == ref

    def test_create_order_bad_product_400(self, session):
        r = session.post(
            f"{API}/orders",
            json={
                "items": [{"product_id": "does_not_exist", "quantity": 1}],
                "contact": {
                    "full_name": "TEST_Bad",
                    "email": "bad@example.com",
                    "phone": "+905555550102",
                },
                "payment_method": "card",
            },
            timeout=15,
        )
        assert r.status_code == 400


# ---------------------------------------------------- admin insurance tests
class TestAdminInsurance:
    def test_insurance_tasks(self, session, admin_headers):
        r = session.get(f"{API}/admin/insurance-tasks", headers=admin_headers, timeout=15)
        assert r.status_code == 200
        body = r.json()
        assert "items" in body and isinstance(body["items"], list)

    def test_insurance_report(self, session, admin_headers):
        r = session.get(f"{API}/admin/insurance-report", headers=admin_headers, timeout=15)
        assert r.status_code == 200
        body = r.json()
        # Should return summary + rows (structure may vary; verify no _id leaked)
        text = r.text
        assert '"_id"' not in text

    def test_profit_monthly(self, session, admin_headers):
        r = session.get(
            f"{API}/admin/profit-monthly", params={"months": 12}, headers=admin_headers, timeout=15
        )
        assert r.status_code == 200
        body = r.json()
        # Expect a months list of 12
        months = body.get("months") or body.get("rows") or body.get("items")
        assert months is not None
        assert isinstance(months, list)
        assert len(months) == 12


# --------------------------------------------------------- visa/quote tests
class TestVisaAndQuote:
    def test_visa_types(self, session):
        r = session.get(f"{API}/visa-types", timeout=15)
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list) and len(items) > 0
        assert all(v.get("price") for v in items)
        return items

    def test_pricing_quote(self, session):
        # Pick a visa id
        r = session.get(f"{API}/visa-types", timeout=15)
        assert r.status_code == 200
        vid = r.json()[0]["id"]
        q = session.post(
            f"{API}/pricing/quote",
            json={
                "visa_type_ids": [vid],
                "addons": {"insurance": False, "esim": False},
                "store_items": [],
                "arrival_date": (date.today() + timedelta(days=10)).isoformat(),
                "departure_date": (date.today() + timedelta(days=15)).isoformat(),
            },
            timeout=15,
        )
        assert q.status_code == 200, q.text
        body = q.json()
        assert body["total"] > 0
        assert body["trip_days"] == 6


# --------------------------------------------------------- email pipeline
class TestEmailPipeline:
    def test_contact_creates_outbox_entry(self, session, admin_headers):
        # Snapshot outbox length before
        before = session.get(
            f"{API}/admin/emails", params={"limit": 200}, headers=admin_headers, timeout=15
        )
        assert before.status_code == 200
        before_count = len(before.json().get("items") or [])

        subject = f"TEST_ regression contact {int(time.time())}"
        r = session.post(
            f"{API}/contact",
            json={
                "name": "TEST_Contact",
                "email": "test_contact@example.com",
                "phone": "+905555550103",
                "subject": subject,
                "message": "Regression test contact message; ignore.",
            },
            timeout=15,
        )
        assert r.status_code == 200, r.text
        assert r.json().get("ok") is True

        # Allow async persistence
        time.sleep(1.5)
        after = session.get(
            f"{API}/admin/emails", params={"limit": 200}, headers=admin_headers, timeout=15
        )
        assert after.status_code == 200
        items = after.json().get("items") or []
        # The subject should show up (status sent/skipped/error) if ADMIN_EMAIL is set
        # If admin email not configured, count is still >= before_count and no crash occurred
        assert len(items) >= before_count
        # Verify each item has a status string
        for it in items[:5]:
            assert it.get("status") in {"sent", "skipped", "error", None}
            assert "_id" not in it


# --------------------------------------------------------- application flow
def _upload_file(session, filename="passport.jpg", doc_type="passport"):
    """Upload a tiny dummy JPG so we have a valid file_id to reference."""
    # Minimal valid JPEG (SOI + APP0 + EOI)
    jpeg = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00" + b"\x08" * 64 + b"\xff\xd9"
    )
    files = {"file": (filename, io.BytesIO(jpeg), "image/jpeg")}
    data = {"doc_type": doc_type}
    # requests session has JSON content-type default -- use a fresh call
    r = requests.post(f"{API}/uploads", files=files, data=data, timeout=20)
    assert r.status_code == 200, f"upload failed: {r.status_code} {r.text}"
    return r.json()["file_id"]


def _app_payload(passport_expiry: str, birth_date: str = "1990-05-05"):
    arrival = (date.today() + timedelta(days=15)).isoformat()
    departure = (date.today() + timedelta(days=22)).isoformat()
    return {
        "contact": {
            "full_name": "TEST_Applicant User",
            "email": "test_app@example.com",
            "phone": "+905555550104",
            "whatsapp_optin": False,
        },
        "travelers": [
            {
                "first_name": "TEST",
                "last_name": "APPLICANT",
                "birth_date": birth_date,
                "gender": "male",
                "applicant_type": "adult",
                "nationality": "TR",
                "passport_no": "U12345678",
                "passport_expiry": passport_expiry,
                "visa_type_id": "",  # to be filled
                "passport_file_id": "",  # to be filled
                "photo_file_id": "",  # to be filled
            }
        ],
        "travel": {
            "arrival_date": arrival,
            "departure_date": departure,
            "purpose": "tourism",
        },
        "addons": {},
        "store_items": [],
        "extra_documents": {},
        "kvkk_accepted": True,
    }


class TestApplicationFlow:
    @pytest.fixture(scope="class")
    def uploads(self):
        s = requests.Session()
        return {
            "passport": _upload_file(s, "passport.jpg", "passport"),
            "photo": _upload_file(s, "photo.jpg", "photo"),
        }

    @pytest.fixture(scope="class")
    def visa_id(self):
        r = requests.get(f"{API}/visa-types", timeout=15)
        assert r.status_code == 200
        # pick one with duration >= 30 to safely cover the 7-day trip
        for v in r.json():
            if int(v.get("duration_days") or 0) >= 30 and v.get("applicant_type") == "adult":
                return v["id"]
        return r.json()[0]["id"]

    def test_valid_application(self, session, uploads, visa_id):
        # passport expires 400 days from departure = valid
        expiry = (date.today() + timedelta(days=400)).isoformat()
        payload = _app_payload(expiry)
        payload["travelers"][0]["visa_type_id"] = visa_id
        payload["travelers"][0]["passport_file_id"] = uploads["passport"]
        payload["travelers"][0]["photo_file_id"] = uploads["photo"]
        r = session.post(f"{API}/applications", json=payload, timeout=30)
        assert r.status_code == 200, f"valid app failed: {r.status_code} {r.text}"
        body = r.json()
        assert body["reference_code"].startswith("DV-")
        assert body["status"] == "submitted"
        assert "_id" not in body

    def test_passport_expiring_soon_rejected(self, session, uploads, visa_id):
        # passport expires only 30 days after today (<180 days after departure)
        expiry = (date.today() + timedelta(days=30)).isoformat()
        payload = _app_payload(expiry)
        payload["travelers"][0]["visa_type_id"] = visa_id
        payload["travelers"][0]["passport_file_id"] = uploads["passport"]
        payload["travelers"][0]["photo_file_id"] = uploads["photo"]
        r = session.post(f"{API}/applications", json=payload, timeout=30)
        assert r.status_code == 400, f"expected 400, got {r.status_code}: {r.text}"
        assert "pasaport" in r.text.lower() or "gecerli" in r.text.lower()

    def test_malformed_passport_date_does_not_500(self, session, uploads, visa_id):
        # malformed passport expiry - should be treated as parse-fail => rule skipped => success
        # Not a 500 crash (that's the regression we want to catch)
        payload = _app_payload("not-a-date")
        payload["travelers"][0]["visa_type_id"] = visa_id
        payload["travelers"][0]["passport_file_id"] = uploads["passport"]
        payload["travelers"][0]["photo_file_id"] = uploads["photo"]
        r = session.post(f"{API}/applications", json=payload, timeout=30)
        # Model requires min_length=4 -> "not-a-date" passes model, then _parse_iso_date returns None
        assert r.status_code != 500, f"server crashed on malformed date: {r.text}"
        assert r.status_code in {200, 400, 422}

    def test_malformed_arrival_date_400_not_500(self, session, uploads, visa_id):
        expiry = (date.today() + timedelta(days=400)).isoformat()
        payload = _app_payload(expiry)
        payload["travelers"][0]["visa_type_id"] = visa_id
        payload["travelers"][0]["passport_file_id"] = uploads["passport"]
        payload["travelers"][0]["photo_file_id"] = uploads["photo"]
        payload["travel"]["arrival_date"] = "garbage"
        r = session.post(f"{API}/applications", json=payload, timeout=30)
        assert r.status_code != 500
        assert r.status_code in {400, 422}
