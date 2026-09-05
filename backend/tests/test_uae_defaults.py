"""Test _fill_uae_defaults: 4 extra fields (marital_status, profession,
mother_name, father_name) auto-fill when omitted, are preserved when sent."""
import io
import os
from datetime import date, timedelta

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    return s


@pytest.fixture(scope="module")
def uploaded_files(api):
    """Upload passport + photo files for use in traveler payloads."""
    # tiny JPEG (10x10 red)
    jpg = bytes.fromhex(
        "ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707"
        "07090908" + "0a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c"
        "2837292c30313434341f27393d38323c2e333432ffc0000b0800" + "0a000a0101"
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
        assert r.status_code == 200, f"upload {key} failed: {r.text}"
        ids[key] = r.json()["file_id"]
    return ids


def _base_payload(uploaded, traveler_overrides=None):
    traveler = {
        "first_name": "AHMET",
        "last_name": "YILMAZ",
        "birth_date": "1990-05-10",
        "applicant_type": "adult",
        "nationality": "TR",
        "passport_no": "U12345678",
        "passport_expiry": "2030-01-01",
        "visa_type_id": "visa_30_single",
        "passport_file_id": uploaded["passport"],
        "photo_file_id": uploaded["photo"],
    }
    if traveler_overrides:
        traveler.update(traveler_overrides)
    return {
        "contact": {
            "full_name": "AHMET YILMAZ",
            "email": "TEST_uae@example.com",
            "phone": "+905551112233",
            "whatsapp_optin": False,
        },
        "travelers": [traveler],
        "travel": {
            "arrival_date": (date.today() + timedelta(days=30)).isoformat(),
            "departure_date": (date.today() + timedelta(days=36)).isoformat(),
        },
        "addons": {"express": False, "insurance": False, "esim": False},
        "extra_documents": {
            "ticket_file_id": uploaded["ticket"],
            "hotel_file_id": uploaded["hotel"],
        },
        "kvkk_accepted": True,
    }


def test_create_application_without_uae_fields_autofills(api, uploaded_files):
    """4 alan hiç gönderilmeden başvuru oluşturulmalı ve default'lar dolmalı."""
    payload = _base_payload(uploaded_files)
    r = api.post(f"{BASE_URL}/api/applications", json=payload)
    assert r.status_code == 200, f"create failed: {r.status_code} {r.text}"
    data = r.json()
    ref = data["reference_code"]
    t = data["travelers"][0]
    assert t["marital_status"] == "single"
    assert t["profession"] == "Employee"
    assert t["mother_name"] == "YILMAZ"
    assert t["father_name"] == "YILMAZ"

    # verify persisted via public tracking endpoint
    tr = api.get(f"{BASE_URL}/api/applications/track", params={"code": ref, "last_name": "YILMAZ"})
    assert tr.status_code == 200
    td = tr.json()["travelers"][0]
    assert td["marital_status"] == "single"
    assert td["profession"] == "Employee"
    assert td["mother_name"] == "YILMAZ"
    assert td["father_name"] == "YILMAZ"


def test_create_application_with_empty_string_uae_fields_autofills(api, uploaded_files):
    """Boş string olarak gönderilince yine default'lara dönmeli."""
    payload = _base_payload(
        uploaded_files,
        traveler_overrides={
            "last_name": "KAYA",
            "marital_status": "single",  # boş gönderilemez (pattern), ama default zaten single
            "profession": "",
            "mother_name": "",
            "father_name": "",
        },
    )
    r = api.post(f"{BASE_URL}/api/applications", json=payload)
    assert r.status_code == 200, r.text
    t = r.json()["travelers"][0]
    assert t["profession"] == "Employee"
    assert t["mother_name"] == "KAYA"
    assert t["father_name"] == "KAYA"


def test_create_application_child_defaults_student(api, uploaded_files):
    payload = _base_payload(
        uploaded_files,
        traveler_overrides={
            "first_name": "MERT",
            "last_name": "DEMIR",
            "applicant_type": "child",
            "birth_date": "2018-01-01",
            "visa_type_id": "visa_30_child",
        },
    )
    # 18 yas alti yolcu en az bir yetiskinle birlikte basvurabilir
    payload["travelers"].append(
        {
            "first_name": "AYSE",
            "last_name": "DEMIR",
            "birth_date": "1988-04-02",
            "applicant_type": "adult",
            "nationality": "TR",
            "passport_no": "U87654321",
            "passport_expiry": "2030-01-01",
            "visa_type_id": "visa_30_single",
            "passport_file_id": uploaded_files["passport"],
            "photo_file_id": uploaded_files["photo"],
        }
    )
    r = api.post(f"{BASE_URL}/api/applications", json=payload)
    assert r.status_code == 200, r.text
    t = r.json()["travelers"][0]
    assert t["profession"] == "Student"
    assert t["applicant_type"] == "child"
    assert t["mother_name"] == "DEMIR"


def test_explicit_uae_fields_preserved(api, uploaded_files):
    """Kullanıcı açıkça gönderirse değer korunmalı, ezilmemeli."""
    payload = _base_payload(
        uploaded_files,
        traveler_overrides={
            "last_name": "OZTURK",
            "marital_status": "married",
            "profession": "Engineer",
            "mother_name": "FATMA",
            "father_name": "MEHMET",
        },
    )
    r = api.post(f"{BASE_URL}/api/applications", json=payload)
    assert r.status_code == 200, r.text
    t = r.json()["travelers"][0]
    assert t["marital_status"] == "married"
    assert t["profession"] == "Engineer"
    assert t["mother_name"] == "FATMA"
    assert t["father_name"] == "MEHMET"
