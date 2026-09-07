"""Iteration 105 backend regression tests.

Verifies helper refactors in routes_admin.py, routes_public.py and zami_status.py
did not regress behaviour, and confirms customer-facing URLs use PUBLIC_BASE_URL
(no stale dubaivizeonline.com fallback).
"""
import io
import os
import sys
import time
from datetime import date, timedelta

import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_backend_url() -> str:
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if url:
        return url.rstrip("/")
    env_path = "/app/frontend/.env"
    with open(env_path) as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip().strip('"').rstrip("/")
    raise RuntimeError("REACT_APP_BACKEND_URL not configured")


BASE_URL = _load_backend_url()
API = f"{BASE_URL}/api"


def _public_base_url() -> str:
    # Read from backend .env directly to compare
    with open("/app/backend/.env") as f:
        for line in f:
            if line.startswith("PUBLIC_BASE_URL="):
                return line.split("=", 1)[1].strip().strip('"').rstrip("/")
    return ""


PUBLIC_BASE = _public_base_url()


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    return s


@pytest.fixture(scope="session")
def admin_token():
    from admin_test_token import admin_token as make_token
    return make_token()


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ---------------------------------------------------------------- helpers
def _upload_jpeg(name="passport.jpg", doc_type="passport"):
    jpeg = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00" + b"\x08" * 64 + b"\xff\xd9"
    )
    r = requests.post(
        f"{API}/uploads",
        files={"file": (name, io.BytesIO(jpeg), "image/jpeg")},
        data={"doc_type": doc_type},
        timeout=20,
    )
    assert r.status_code == 200, f"upload failed: {r.status_code} {r.text}"
    return r.json()["file_id"]


def _upload_pdf():
    pdf = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
    r = requests.post(
        f"{API}/uploads",
        files={"file": ("policy.pdf", io.BytesIO(pdf), "application/pdf")},
        data={"doc_type": "policy"},
        timeout=20,
    )
    assert r.status_code == 200, r.text
    return r.json()["file_id"]


# ---------------------------------------------------- general regression
class TestGeneralRegression:
    def test_visa_types(self, session):
        r = session.get(f"{API}/visa-types", timeout=15)
        assert r.status_code == 200
        assert isinstance(r.json(), list) and len(r.json()) > 0

    def test_content_site(self, session):
        r = session.get(f"{API}/content/site", timeout=15)
        assert r.status_code == 200

    def test_bundles_visa_days_30_includes_pack_family(self, session):
        r = session.get(f"{API}/bundles", params={"visa_days": 30}, timeout=15)
        assert r.status_code == 200
        body = r.json()
        ids = [b.get("id") for b in body.get("items", [])]
        assert "pack_family" in ids, f"pack_family missing from bundles: {ids}"

    def test_contact_endpoint(self, session):
        r = session.post(
            f"{API}/contact",
            json={
                "name": "TEST_ContactIter105",
                "email": "test_contact105@example.com",
                "phone": "+905555550777",
                "subject": "TEST_regression 105",
                "message": "regression test - ignore",
            },
            timeout=15,
        )
        assert r.status_code == 200, r.text
        assert r.json().get("ok") is True

    def test_admin_applications_list(self, session, admin_headers):
        r = session.get(f"{API}/admin/applications", headers=admin_headers, timeout=15)
        assert r.status_code == 200

    def test_admin_orders_list(self, session, admin_headers):
        r = session.get(f"{API}/admin/orders", headers=admin_headers, timeout=15)
        assert r.status_code == 200


# ------------------------------------------------- application create + track
@pytest.fixture(scope="module")
def created_application():
    """Create a test application to be reused."""
    passport = _upload_jpeg("passport105.jpg", "passport")
    photo = _upload_jpeg("photo105.jpg", "photo")

    r = requests.get(f"{API}/visa-types", timeout=15)
    visa_id = None
    for v in r.json():
        if int(v.get("duration_days") or 0) >= 30 and v.get("applicant_type") == "adult":
            visa_id = v["id"]
            break
    assert visa_id, "no suitable visa type found"

    arrival = (date.today() + timedelta(days=15)).isoformat()
    departure = (date.today() + timedelta(days=22)).isoformat()
    expiry = (date.today() + timedelta(days=400)).isoformat()

    payload = {
        "contact": {
            "full_name": "TEST_Iter105 Applicant",
            "email": "delivered@resend.dev",
            "phone": "+905555550778",
            "whatsapp_optin": False,
        },
        "travelers": [
            {
                "first_name": "TEST",
                "last_name": "ITER105",
                "birth_date": "1990-05-05",
                "gender": "male",
                "applicant_type": "adult",
                "nationality": "TR",
                "passport_no": "U10500001",
                "passport_expiry": expiry,
                "visa_type_id": visa_id,
                "passport_file_id": passport,
                "photo_file_id": photo,
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
    r = requests.post(f"{API}/applications", json=payload, timeout=30)
    assert r.status_code == 200, r.text
    body = r.json()
    return {
        "id": body["id"],
        "reference_code": body["reference_code"],
        "last_name": "ITER105",
    }


class TestApplicationLifecycle:
    def test_application_created_ok(self, created_application):
        assert created_application["reference_code"].startswith("DV-")

    def test_application_track(self, session, created_application):
        r = session.get(
            f"{API}/applications/track",
            params={"code": created_application["reference_code"], "last_name": "ITER105"},
            timeout=15,
        )
        assert r.status_code == 200, r.text

    def test_admin_patch_status_reviewing(self, session, admin_headers, created_application):
        r = session.patch(
            f"{API}/admin/applications/{created_application['id']}",
            headers=admin_headers,
            json={"status": "reviewing", "note": "TEST_note reviewing", "notify": True},
            timeout=20,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        app = body.get("application") or body
        assert app.get("status") == "reviewing"
        hist = app.get("status_history") or []
        assert len(hist) >= 1
        # notification field present (email is 'sent' or 'skipped', never raised)
        # Response shape: check email_notification or similar
        notif_keys = [k for k in body.keys() if "email" in k.lower() or "notif" in k.lower()]
        assert notif_keys or "email_notification" in body, f"no notification key: {list(body.keys())}"

    def test_admin_patch_status_approved_whatsapp_swallowed(self, session, admin_headers, created_application):
        r = session.patch(
            f"{API}/admin/applications/{created_application['id']}",
            headers=admin_headers,
            json={"status": "approved", "note": "TEST_approved", "notify": True},
            timeout=25,
        )
        assert r.status_code == 200, f"approved patch failed: {r.status_code} {r.text}"
        body = r.json()
        app = body.get("application") or body
        assert app.get("status") == "approved"


# ---------------------------------------------------- order delivery flow
@pytest.fixture(scope="module")
def created_order():
    payload = {
        "items": [{"product_id": "esim_3gb", "quantity": 1}],
        "contact": {
            "full_name": "TEST_Iter105 Order",
            "email": "delivered@resend.dev",
            "phone": "+905555550779",
        },
        "travel_start": (date.today() + timedelta(days=10)).isoformat(),
        "travel_end": (date.today() + timedelta(days=17)).isoformat(),
        "payment_method": "card",
        "note": "TEST_ iter105 order",
    }
    r = requests.post(f"{API}/orders", json=payload, timeout=20)
    assert r.status_code == 200, r.text
    return r.json()["order"]


class TestOrderDelivery:
    def test_deliver_requires_at_least_one_file(self, session, admin_headers, created_order):
        r = session.post(
            f"{API}/admin/orders/{created_order['id']}/deliver",
            headers=admin_headers,
            json={"message": "TEST"},
            timeout=15,
        )
        assert r.status_code == 400
        assert "belge" in r.text.lower() or "esim" in r.text.lower() or "police" in r.text.lower()

    def test_deliver_single_file(self, session, admin_headers, created_order):
        esim = _upload_jpeg("esim_qr.jpg", "esim")
        r = session.post(
            f"{API}/admin/orders/{created_order['id']}/deliver",
            headers=admin_headers,
            json={"esim_file_id": esim, "message": "TEST_delivery"},
            timeout=25,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        order = body["order"]
        assert order["status"] == "fulfilled"
        assert order["delivery"]["esim_file_id"] == esim
        assert order["delivery"].get("sent_at") is not None
        assert "email" in body

    def test_deliver_both_files_two_links(self, session, admin_headers, created_order, admin_token):
        # Create another order to test both-files delivery
        payload = {
            "items": [{"product_id": "esim_3gb", "quantity": 1}],
            "contact": {
                "full_name": "TEST_Iter105 Order2",
                "email": "delivered@resend.dev",
                "phone": "+905555550780",
            },
            "travel_start": (date.today() + timedelta(days=10)).isoformat(),
            "travel_end": (date.today() + timedelta(days=17)).isoformat(),
            "payment_method": "card",
        }
        r = requests.post(f"{API}/orders", json=payload, timeout=20)
        assert r.status_code == 200
        order2 = r.json()["order"]

        esim = _upload_jpeg("esim_qr2.jpg", "esim")
        policy = _upload_pdf()
        r = session.post(
            f"{API}/admin/orders/{order2['id']}/deliver",
            headers=admin_headers,
            json={"esim_file_id": esim, "policy_file_id": policy, "message": "TEST_both"},
            timeout=25,
        )
        assert r.status_code == 200, r.text

        # Wait for async email persistence and check outbox HTML for 2 signed links
        time.sleep(2)
        emails = session.get(
            f"{API}/admin/emails",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"limit": 50},
            timeout=15,
        )
        assert emails.status_code == 200
        items = emails.json().get("items") or []
        # Find latest order_delivered email for our reference
        target_id = None
        for it in items:
            if it.get("kind") != "order_delivered":
                continue
            if order2["reference_code"] in (it.get("subject") or ""):
                target_id = it.get("id")
                break
        assert target_id, f"order_delivered email not found for {order2['reference_code']}"
        detail = session.get(
            f"{API}/admin/emails/{target_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=15,
        )
        assert detail.status_code == 200
        html = detail.json().get("html") or ""
        # Two signed /api/files/ links with t= token query
        file_link_count = html.count("/api/files/")
        assert file_link_count >= 2, f"expected >=2 file links, got {file_link_count}. HTML snippet: {html[:500]}"
        assert "t=" in html or "token=" in html
        # Stale domain check
        assert "dubaivizeonline.com" not in html
        # Uses PUBLIC_BASE_URL
        if PUBLIC_BASE:
            assert PUBLIC_BASE in html, f"PUBLIC_BASE {PUBLIC_BASE} not in delivery email"


# ---------------------------------------------------- photo check endpoint
class TestPhotoCheck:
    def test_photo_check_happy_path(self):
        photo = _upload_jpeg("photo_check.jpg", "photo")
        r = requests.post(
            f"{API}/photo/check",
            data={"file_id": photo},
            timeout=30,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert "checked" in body
        assert "message" in body or "reason" in body

    def test_photo_check_pdf_returns_early(self):
        pdf = _upload_pdf()
        r = requests.post(
            f"{API}/photo/check",
            data={"file_id": pdf},
            timeout=15,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("checked") is False
        assert body.get("reason") == "pdf"
        assert body.get("ok") is False

    def test_photo_check_nonexistent_404(self):
        r = requests.post(
            f"{API}/photo/check",
            data={"file_id": "nonexistent_file_id_xyz"},
            timeout=15,
        )
        assert r.status_code == 404


# ---------------------------------------------------- stale domain check
class TestNoStaleDomain:
    def test_no_stale_domain_in_prod_modules(self):
        import subprocess
        # Only production backend modules (not tests, not admin_test_token.py)
        result = subprocess.run(
            ["grep", "-rn", "dubaivizeonline.com", "/app/backend", "--include=*.py"],
            capture_output=True, text=True,
        )
        offenders = []
        for line in result.stdout.splitlines():
            if "/tests/" in line or "__pycache__" in line:
                continue
            if "admin_test_token.py" in line:
                continue
            # routes_admin.py line 87 is ADMIN_LOGIN_EMAIL fallback -- allowed
            if "ADMIN_LOGIN_EMAIL" in line:
                continue
            offenders.append(line)
        assert not offenders, f"stale domain fallbacks remain: {offenders}"

    def test_public_base_url_configured(self):
        assert PUBLIC_BASE, "PUBLIC_BASE_URL not set in backend .env"
        assert "dubaivizeonline.com" not in PUBLIC_BASE
