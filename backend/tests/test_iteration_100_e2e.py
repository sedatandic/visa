"""Iteration 100 - end-to-end: create a real application and confirm
- subject in email_outbox starts with '{ref} başvuru nolu Dubai vize başvurunuz alındı'
- outbox html contains public logo URL (not cid)
- Resend accepted the send (status 'sent') implying attachment did not 4xx
"""
import io
import os
from datetime import date

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL missing"

# Admin token helper for outbox inspection
import sys
sys.path.insert(0, "/app/backend")
from admin_test_token import admin_token  # noqa: E402


@pytest.fixture(scope="module")
def api():
    return requests.Session()


@pytest.fixture(scope="module")
def uploaded(api):
    jpg = bytes.fromhex(
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
    ids = {}
    for key in ("passport", "photo", "ticket", "hotel"):
        r = api.post(
            f"{BASE_URL}/api/uploads",
            files={"file": ("t.jpg", io.BytesIO(jpg), "image/jpeg")},
            data={"doc_type": key},
        )
        assert r.status_code == 200, r.text
        ids[key] = r.json()["file_id"]
    return ids


def test_application_creation_subject_and_outbox_logo(api, uploaded):
    payload = {
        "contact": {
            "full_name": "TEST DELIVERED",
            "email": "delivered@resend.dev",
            "phone": "+905551112233",
        },
        "travelers": [{
            "first_name": "TEST",
            "last_name": "DELIVERED",
            "birth_date": "1990-05-10",
            "nationality": "TR",
            "passport_no": "U88880001",
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
    r = api.post(f"{BASE_URL}/api/applications", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    ref = body["reference_code"]
    assert body.get("email_notification") in ("sent", "skipped"), body
    # Should have been "sent" since RESEND_API_KEY is real
    assert body["email_notification"] == "sent", (
        f"Resend did not accept the send (attachment issue?): {body}"
    )

    # Fetch outbox via admin
    tok = admin_token()
    headers = {"Authorization": f"Bearer {tok}"}
    ao = requests.get(f"{BASE_URL}/api/admin/emails", headers=headers, params={"limit": 100})
    assert ao.status_code == 200, ao.text
    items = ao.json().get("items", [])
    applicant = next(
        (row for row in items
         if row.get("kind") == "application_received" and row.get("subject", "").startswith(ref)),
        None,
    )
    assert applicant, f"no application_received row for {ref}"

    expected = f"{ref} başvuru nolu Dubai vize başvurunuz alındı"
    assert applicant["subject"] == expected, applicant["subject"]
    # fetch detail for HTML
    detail_r = requests.get(f"{BASE_URL}/api/admin/emails/{applicant['id']}", headers=headers)
    assert detail_r.status_code == 200, detail_r.text
    html = detail_r.json().get("html") or ""
    assert "cid:dvh-logo" not in html, "outbox html still contains cid reference"
    assert "/brand/logo-horizontal-gold-palm.png" in html, "public logo URL missing"
    assert applicant.get("status") == "sent", (
        f"Resend rejected: {applicant.get('status')} {applicant.get('reason')}"
    )

    # cleanup
    try:
        from pymongo import MongoClient
        mc = MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
        db = mc[os.environ.get("DB_NAME", "test_database")]
        db.applications.delete_many({"reference_code": ref})
        db.email_outbox.delete_many({"meta.reference_code": ref})
    except Exception:
        pass
