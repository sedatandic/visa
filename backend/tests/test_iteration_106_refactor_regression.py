"""Iteration 106 backend regression tests.

Confirms that the behaviour-preserving refactors on
  * _validate_travel_rules -> _travel_window / _validate_child_traveler /
    _validate_stay_within_visa / _validate_passport_validity
  * read_passport_document -> _ocr_failure / _ocr_success
in /app/backend/routes_public.py did not change any observable behaviour.

Also runs light regression on neighbouring public endpoints in the same
module (visa-types, content/site, bundles, products, photo/check,
applications/track, contact) and asserts every OCR attempt writes to
the ocr_metrics collection.
"""
from __future__ import annotations

import asyncio
import io
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ----------------------------------------------------------------- config
def _load_backend_url() -> str:
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if url:
        return url.rstrip("/")
    for line in Path("/app/frontend/.env").read_text().splitlines():
        if line.startswith("REACT_APP_BACKEND_URL="):
            return line.split("=", 1)[1].strip().strip('"').rstrip("/")
    raise RuntimeError("REACT_APP_BACKEND_URL not configured")


BASE_URL = _load_backend_url()
API = f"{BASE_URL}/api"


# ------------------------------------------------------------- helpers
JPEG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00" + b"\x08" * 64 + b"\xff\xd9"
)
PDF = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"


def _upload(name: str, blob: bytes, mime: str, doc_type: str) -> str:
    r = requests.post(
        f"{API}/uploads",
        files={"file": (name, io.BytesIO(blob), mime)},
        data={"doc_type": doc_type},
        timeout=20,
    )
    assert r.status_code == 200, f"upload failed: {r.status_code} {r.text}"
    return r.json()["file_id"]


def _upload_jpeg(name: str = "passport106.jpg", doc_type: str = "passport") -> str:
    return _upload(name, JPEG, "image/jpeg", doc_type)


def _upload_pdf(name: str = "passport106.pdf") -> str:
    return _upload(name, PDF, "application/pdf", "passport")


def _contact(email: str = "delivered@resend.dev") -> dict:
    return {
        "full_name": "TEST_Iter106 Applicant",
        "email": email,
        "phone": "+905555550781",
        "address_city": "Istanbul",
        "whatsapp_optin": False,
    }


def _traveler(**overrides) -> dict:
    base = {
        "first_name": "TEST",
        "last_name": "ITER106",
        "birth_date": "1990-05-05",
        "gender": "male",
        "applicant_type": "adult",
        "nationality": "TR",
        "passport_no": "U10600001",
        "passport_expiry": (date.today() + timedelta(days=500)).isoformat(),
        "marital_status": "single",
        "profession": "Employee",
        "mother_name": "Ayse",
        "father_name": "Mehmet",
        "visa_type_id": "visa_30_single",
        "passport_file_id": "fake-passport-file-id",
        "photo_file_id": "fake-photo-file-id",
    }
    base.update(overrides)
    return base


def _travel(arrival: str | None = None, departure: str | None = None, **extra) -> dict:
    if arrival is None:
        arrival = (date.today() + timedelta(days=20)).isoformat()
    if departure is None:
        departure = (date.today() + timedelta(days=27)).isoformat()
    body = {
        "arrival_date": arrival,
        "departure_date": departure,
        "purpose": "tourism",
        "birth_country": "TR",
        "accommodation": "Hotel X",
        "flight_no": "TK123",
    }
    body.update(extra)
    return body


def _payload(travelers: list, travel: dict) -> dict:
    return {
        "contact": _contact(),
        "travelers": travelers,
        "travel": travel,
        "addons": {"express": False, "insurance": False, "insurance_plus": False, "esim": False},
        "store_items": [],
        "extra_documents": {"ticket_file_id": None, "hotel_file_id": None, "other_file_ids": []},
        "kvkk_accepted": True,
    }


def _post_app(payload: dict) -> requests.Response:
    return requests.post(f"{API}/applications", json=payload, timeout=20)


# ================================================================ TRAVEL RULE VALIDATION
class TestTravelRuleValidation:
    """Iteration 106 refactor: each split helper still raises the exact prior message."""

    def test_a_missing_arrival_date(self):
        r = _post_app(_payload([_traveler()], _travel(arrival="", departure="")))
        assert r.status_code == 400, r.text
        assert "Gidis ve donus tarihlerini gecerli bir formatta gonderin" in r.text

    def test_a_invalid_arrival_date(self):
        r = _post_app(_payload([_traveler()], _travel(arrival="not-a-date", departure="also-not")))
        assert r.status_code == 400, r.text
        assert "Gidis ve donus tarihlerini gecerli bir formatta gonderin" in r.text

    def test_b_departure_before_arrival(self):
        arr = (date.today() + timedelta(days=30)).isoformat()
        dep = (date.today() + timedelta(days=25)).isoformat()
        r = _post_app(_payload([_traveler()], _travel(arrival=arr, departure=dep)))
        assert r.status_code == 400, r.text
        assert "Donus tarihi gidis tarihinden once olamaz" in r.text

    def test_c_arrival_in_past(self):
        r = _post_app(_payload([_traveler()], _travel("2020-01-01", "2020-01-05")))
        assert r.status_code == 400, r.text
        assert "Gidis tarihi bugunden once olamaz" in r.text

    def test_d_child_visa_adult_age(self):
        t = _traveler(
            applicant_type="child",
            visa_type_id="visa_30_child",
            birth_date="1990-05-05",
        )
        r = _post_app(_payload([t], _travel()))
        assert r.status_code == 400, r.text
        assert "cocuk vizesi yalnizca 18 yasindan kucuk" in r.text

    def test_e_child_only_application_no_adult(self):
        t = _traveler(
            first_name="Kucuk",
            applicant_type="child",
            visa_type_id="visa_30_child",
            birth_date="2018-05-10",
            passport_no="C10600001",
        )
        r = _post_app(_payload([t], _travel()))
        assert r.status_code == 400, r.text
        assert "en az bir yetiskin yolcu ile birlikte basvurmalidir" in r.text

    def test_f_stay_longer_than_visa_duration(self):
        arr = (date.today() + timedelta(days=10)).isoformat()
        dep = (date.today() + timedelta(days=50)).isoformat()  # 41 days on 30-day visa
        r = _post_app(_payload([_traveler()], _travel(arrival=arr, departure=dep)))
        assert r.status_code == 400, r.text
        assert "gun kalis hakki veriyor" in r.text

    def test_g_passport_less_than_180d_after_return(self):
        # departure ~ today+27; expiry only 50d beyond = well below 180
        exp = (date.today() + timedelta(days=60)).isoformat()
        t = _traveler(passport_expiry=exp)
        r = _post_app(_payload([t], _travel()))
        assert r.status_code == 400, r.text
        assert "pasaportunuz donus tarihinden itibaren en az 6 ay gecerli olmalidir" in r.text

    def test_h_dates_unknown_skips_date_checks_uses_today_for_passport(self):
        """dates_unknown=true skips date checks but passport 6-mo rule uses TODAY."""
        exp = (date.today() + timedelta(days=90)).isoformat()  # < 180 from today
        t = _traveler(passport_expiry=exp)
        travel = {
            "arrival_date": "",
            "departure_date": "",
            "dates_unknown": True,
            "purpose": "tourism",
            "birth_country": "TR",
            "accommodation": "Hotel X",
            "flight_no": "TK123",
        }
        r = _post_app(_payload([t], travel))
        assert r.status_code == 400, r.text
        assert "pasaportunuz bugunden itibaren en az 6 ay gecerli olmalidir" in r.text


# ================================================================ HAPPY PATH
class TestHappyPath:
    def test_single_adult_ok(self):
        passport = _upload_jpeg("passport_hp.jpg", "passport")
        photo = _upload_jpeg("photo_hp.jpg", "photo")
        arr = (date.today() + timedelta(days=15)).isoformat()
        dep = (date.today() + timedelta(days=22)).isoformat()
        exp = (date.today() + timedelta(days=500)).isoformat()
        t = _traveler(
            passport_expiry=exp,
            passport_file_id=passport,
            photo_file_id=photo,
        )
        r = _post_app(_payload([t], _travel(arr, dep)))
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("reference_code", "").startswith("DV-")
        assert "pricing" in body
        assert "travel" in body
        assert body["travel"]["arrival_date"] == arr
        assert body["travel"]["departure_date"] == dep

    def test_family_two_adults_one_child_with_discount(self):
        arr = (date.today() + timedelta(days=15)).isoformat()
        dep = (date.today() + timedelta(days=22)).isoformat()
        exp = (date.today() + timedelta(days=500)).isoformat()
        adults = []
        for i in range(2):
            adults.append(_traveler(
                first_name=f"Adult{i}",
                last_name="TEST106FAM",
                passport_no=f"U1060010{i}",
                passport_expiry=exp,
                passport_file_id=_upload_jpeg(f"padult{i}.jpg", "passport"),
                photo_file_id=_upload_jpeg(f"phadult{i}.jpg", "photo"),
            ))
        child = _traveler(
            first_name="Child",
            last_name="TEST106FAM",
            birth_date="2018-05-10",
            applicant_type="child",
            visa_type_id="visa_30_child",
            passport_no="C10600102",
            passport_expiry=exp,
            passport_file_id=_upload_jpeg("pchild.jpg", "passport"),
            photo_file_id=_upload_jpeg("phchild.jpg", "photo"),
        )
        r = _post_app(_payload(adults + [child], _travel(arr, dep)))
        assert r.status_code == 200, r.text
        body = r.json()
        pricing = body.get("pricing", {})
        # family discount should have been applied
        discount = pricing.get("family_discount") or pricing.get("discount") or 0
        assert float(discount) > 0, f"family discount missing in pricing: {pricing}"


# ================================================================ PASSPORT OCR ENDPOINT
def _count_metrics_sync() -> int:
    from pymongo import MongoClient
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        # Fallback: read from backend/.env
        for line in Path("/app/backend/.env").read_text().splitlines():
            if line.startswith("MONGO_URL=") and not mongo_url:
                mongo_url = line.split("=", 1)[1].strip().strip('"')
            if line.startswith("DB_NAME=") and not db_name:
                db_name = line.split("=", 1)[1].strip().strip('"')
    client = MongoClient(mongo_url)
    try:
        return client[db_name]["ocr_metrics"].count_documents({})
    finally:
        client.close()


class TestPassportOCR:
    def test_pdf_returns_reason_pdf_no_data_key(self):
        before = _count_metrics_sync()
        fid = _upload_pdf()
        r = requests.post(f"{API}/passport/read", data={"file_id": fid}, timeout=30)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("ok") is False
        assert body.get("reason") == "pdf"
        assert "PDF dosyalari otomatik okunamiyor" in (body.get("message") or "")
        assert "data" not in body, f"PDF failure must NOT include 'data': {body}"
        after = _count_metrics_sync()
        assert after == before + 1, f"metrics not written (before={before} after={after})"

    def test_nonexistent_file_id_404(self):
        r = requests.post(
            f"{API}/passport/read",
            data={"file_id": "nonexistent_iter106_xyz"},
            timeout=15,
        )
        assert r.status_code == 404, r.text

    def test_non_passport_image_reason_shape(self):
        """Plain JPG: either not_readable (with data) or ai_error (without data)."""
        before = _count_metrics_sync()
        fid = _upload_jpeg("plain106.jpg", "passport")
        r = requests.post(f"{API}/passport/read", data={"file_id": fid}, timeout=60)
        # Rate-limited responses are acceptable but flag as skip
        if r.status_code == 429:
            pytest.skip("hit AI rate limit for /api/passport/read")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("ok") is False
        reason = body.get("reason")
        assert reason in ("not_readable", "ai_error"), f"unexpected reason: {reason}"
        if reason == "not_readable":
            assert "data" in body, "not_readable must include 'data' key"
        else:  # ai_error
            assert "data" not in body, "ai_error must NOT include 'data' key"
        after = _count_metrics_sync()
        assert after == before + 1, f"metrics not written (before={before} after={after})"


# ================================================================ NEIGHBOURING ENDPOINTS
class TestNeighbouringRegression:
    def test_visa_types(self):
        r = requests.get(f"{API}/visa-types", timeout=15)
        assert r.status_code == 200
        assert isinstance(r.json(), list) and len(r.json()) > 0

    def test_content_site(self):
        r = requests.get(f"{API}/content/site", timeout=15)
        assert r.status_code == 200

    def test_bundles_pack_family(self):
        r = requests.get(f"{API}/bundles", params={"visa_days": 30}, timeout=15)
        assert r.status_code == 200
        body = r.json()
        ids = [b.get("id") for b in body.get("items", [])]
        assert "pack_family" in ids

    def test_products(self):
        r = requests.get(f"{API}/products", timeout=15)
        assert r.status_code == 200
        # response can be list or dict; both accepted
        assert r.json() not in (None, "")

    def test_photo_check_valid_image(self):
        fid = _upload_jpeg("photo_iter106.jpg", "photo")
        r = requests.post(f"{API}/photo/check", data={"file_id": fid}, timeout=45)
        if r.status_code == 429:
            pytest.skip("photo/check rate limited")
        assert r.status_code == 200, r.text
        body = r.json()
        assert "checked" in body

    def test_photo_check_pdf(self):
        fid = _upload_pdf("photo_iter106.pdf")
        r = requests.post(f"{API}/photo/check", data={"file_id": fid}, timeout=15)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("checked") is False
        assert body.get("reason") == "pdf"

    def test_photo_check_nonexistent(self):
        r = requests.post(f"{API}/photo/check", data={"file_id": "nope_iter106"}, timeout=15)
        assert r.status_code == 404

    def test_track_correct_code_and_surname(self):
        # Create app first
        passport = _upload_jpeg("track_p.jpg", "passport")
        photo = _upload_jpeg("track_ph.jpg", "photo")
        arr = (date.today() + timedelta(days=15)).isoformat()
        dep = (date.today() + timedelta(days=22)).isoformat()
        exp = (date.today() + timedelta(days=500)).isoformat()
        t = _traveler(
            last_name="TRACK106",
            passport_expiry=exp,
            passport_file_id=passport,
            photo_file_id=photo,
        )
        pl = _payload([t], _travel(arr, dep))
        pl["contact"]["full_name"] = "TEST_track106 User"
        r = _post_app(pl)
        assert r.status_code == 200, r.text
        ref = r.json()["reference_code"]

        # correct
        r2 = requests.get(
            f"{API}/applications/track",
            params={"code": ref, "last_name": "TRACK106"},
            timeout=15,
        )
        assert r2.status_code == 200, r2.text

        # wrong surname -> 404 generic
        r3 = requests.get(
            f"{API}/applications/track",
            params={"code": ref, "last_name": "WRONG_SURNAME_X"},
            timeout=15,
        )
        assert r3.status_code == 404

    def test_contact_endpoint(self):
        r = requests.post(
            f"{API}/contact",
            json={
                "name": "TEST_iter106",
                "email": "test_contact106@example.com",
                "phone": "+905555550777",
                "subject": "TEST_iter106",
                "message": "regression - ignore",
            },
            timeout=15,
        )
        assert r.status_code == 200, r.text
        assert r.json().get("ok") is True
