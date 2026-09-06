"""Iteration 85 - legal content + consents backend regression tests."""
import io
import os

import pytest
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv("/app/backend/.env")
BASE = open("/app/frontend/.env").read().split("REACT_APP_BACKEND_URL=")[1].split("\n")[0].strip().rstrip("/")

PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000a49444154789c6300010000050001"
    "0d0a2db40000000049454e44ae426082"
)


@pytest.fixture(scope="module")
def legal():
    r = requests.get(f"{BASE}/api/content/legal", timeout=15)
    assert r.status_code == 200
    return r.json()


# --- /api/content/legal shape ---
def test_legal_has_all_four_docs(legal):
    assert {"refund_terms", "service_terms", "privacy_policy", "marketing_consent"} <= set(legal.keys())


def test_legal_updated_at_all_2026_06_09(legal):
    for k, doc in legal.items():
        if not isinstance(doc, dict):  # affiliation gibi duz metin alanlar
            continue
        assert doc.get("updated_at") == "2026-06-09", f"{k} updated_at != 2026-06-09"


def test_refund_terms_has_required_sections(legal):
    titles = [s["title"] for s in legal["refund_terms"]["sections"]]
    joined = " | ".join(titles).lower()
    # tur/aktivite
    assert any("tur" in t.lower() and ("aktivite" in t.lower() or "transfer" in t.lower()) for t in titles), titles
    # no-show mentioned in items of tur section
    all_items_text = " ".join(
        item for s in legal["refund_terms"]["sections"] for item in s["items"]
    ).lower()
    assert "no-show" in all_items_text
    # chargeback
    assert "chargeback" in joined or "chargeback" in all_items_text


def test_service_terms_has_required_sections(legal):
    titles = " | ".join(s["title"] for s in legal["service_terms"]["sections"]).lower()
    all_items_text = " ".join(
        item for s in legal["service_terms"]["sections"] for item in s["items"]
    ).lower()
    for kw in ["aracı", "riskli", "cayma", "sorumluluk", "uyuşmazlık"]:
        assert kw in titles or kw in all_items_text, f"missing keyword: {kw}"


def test_privacy_policy_has_10_sections(legal):
    assert len(legal["privacy_policy"]["sections"]) == 10


def test_marketing_consent_has_5_sections(legal):
    assert len(legal["marketing_consent"]["sections"]) == 5


# --- POST /api/applications consents persistence ---
def _upload():
    r = requests.post(
        f"{BASE}/api/uploads",
        files={"file": ("t.png", io.BytesIO(PNG), "image/png")},
        data={"doc_type": "passport"},
        timeout=60,
    )
    assert r.status_code == 200, r.text
    return r.json()["file_id"]


def _make_payload(consents):
    visa = next(v for v in requests.get(f"{BASE}/api/visa-types", timeout=15).json() if v["id"] == "visa_30_single")
    return {
        "contact": {
            "full_name": "TEST_iter85 Consent",
            "email": "delivered@resend.dev",
            "phone": "+90 532 588 26 30",
            "address_city": "Istanbul",
            "whatsapp_optin": True,
        },
        "travelers": [
            {
                "first_name": "AHMET",
                "last_name": "TEST85",
                "birth_date": "1990-05-15",
                "gender": "male",
                "applicant_type": "adult",
                "nationality": "TR",
                "passport_no": "U55443322",
                "passport_expiry": "2032-12-31",
                "visa_type_id": visa["id"],
                "passport_file_id": _upload(),
                "photo_file_id": _upload(),
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
        "consents": consents,
    }


@pytest.fixture(scope="module")
def db():
    return MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]


def test_consents_persist_with_optional_false(db):
    consents = {
        "refund_privacy_accepted": True,
        "service_terms_accepted": True,
        "marketing_email_optin": False,
        "ad_personalization_optin": False,
    }
    r = requests.post(f"{BASE}/api/applications", json=_make_payload(consents), timeout=60)
    assert r.status_code == 200, r.text
    ref = r.json()["reference_code"]
    doc = db.visa_applications.find_one({"reference_code": ref})
    assert doc is not None
    c = doc["consents"]
    assert c["refund_privacy_accepted"] is True
    assert c["service_terms_accepted"] is True
    assert c["marketing_email_optin"] is False
    assert c["ad_personalization_optin"] is False
    assert c.get("accepted_at") is not None


def test_consents_persist_with_optional_true(db):
    consents = {
        "refund_privacy_accepted": True,
        "service_terms_accepted": True,
        "marketing_email_optin": True,
        "ad_personalization_optin": True,
    }
    r = requests.post(f"{BASE}/api/applications", json=_make_payload(consents), timeout=60)
    assert r.status_code == 200, r.text
    ref = r.json()["reference_code"]
    doc = db.visa_applications.find_one({"reference_code": ref})
    c = doc["consents"]
    assert c["marketing_email_optin"] is True
    assert c["ad_personalization_optin"] is True
