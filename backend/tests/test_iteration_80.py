"""Iteration 80 regression:
- Flexible/unknown travel dates: TravelIn allows empty arrival/departure when
  dates_unknown=true; travel_window required; pricing quote works with null dates
- POST /api/orders with tour product enforces scheduled_date/scheduled_time
  (regression fix for iter_79 _tour_schedule bug)
- Order emails use proper Turkish text with UTF-8 characters and payment method
  label "Kredi / Banka Kartı" (not raw "card")
"""
import io
import os
import uuid
from datetime import date, timedelta

import pytest

from insured_data import insured_people
import requests
from dotenv import load_dotenv

HERE = os.path.dirname(__file__)
load_dotenv(os.path.join(HERE, "..", ".env"))
load_dotenv(os.path.join(HERE, "..", "..", "frontend", ".env"))

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_EMAIL = os.environ["ADMIN_LOGIN_EMAIL"]


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _upload_jpeg(doc_type: str) -> str:
    jpeg = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00" + b"\x08" * 64 + b"\xff\xd9"
    )
    files = {"file": (f"{doc_type}.jpg", io.BytesIO(jpeg), "image/jpeg")}
    r = requests.post(f"{API}/uploads", files=files, data={"doc_type": doc_type}, timeout=20)
    assert r.status_code == 200, f"upload failed: {r.status_code} {r.text[:200]}"
    return r.json()["file_id"]


def _app_payload(passport_fid, photo_fid, travel):
    return {
        "contact": {
            "full_name": "TEST Kullanici Deneme",
            "email": f"TEST_iter80_{uuid.uuid4().hex[:6]}@example.com",
            "phone": "+905551112233",
            "whatsapp_optin": False,
        },
        "travelers": [{
            "first_name": "TESTAD",
            "last_name": "TESTSOYAD",
            "birth_date": "1990-05-05",
            "gender": "male",
            "applicant_type": "adult",
            "nationality": "TR",
            "passport_no": "U99887766",
            "passport_expiry": (date.today() + timedelta(days=800)).isoformat(),
            "visa_type_id": "visa_30_single",
            "passport_file_id": passport_fid,
            "photo_file_id": photo_fid,
        }],
        "travel": travel,
        "addons": {},
        "store_items": [],
        "extra_documents": {},
        "kvkk_accepted": True,
    }


# ---------------------------------------------------------------------------
# Pricing quote with flexible dates
# ---------------------------------------------------------------------------
class TestPricingQuoteFlexible:
    def test_quote_null_dates_ok(self, api):
        r = api.post(f"{API}/pricing/quote", json={
            "visa_type_ids": ["visa_30_single"],
            "addons": {},
            "store_items": [
                {"product_id": "ins_15d", "quantity": 1},
                {"product_id": "esim_3gb", "quantity": 1},
            ],
            "arrival_date": None,
            "departure_date": None,
        }, timeout=15)
        assert r.status_code == 200, f"quote failed: {r.status_code} {r.text[:300]}"
        data = r.json()
        store = data.get("store_items") or []
        assert len(store) == 2, f"expected 2 store lines, got {store}"
        for line in store:
            assert line.get("starts_on") in (None, ""), f"starts_on should be null: {line}"
            assert float(line["total"]) > 0

    def test_quote_omitted_dates_ok(self, api):
        r = api.post(f"{API}/pricing/quote", json={
            "visa_type_ids": ["visa_30_single"],
            "store_items": [{"product_id": "ins_15d", "quantity": 1}],
        }, timeout=15)
        assert r.status_code == 200, r.text[:300]


# ---------------------------------------------------------------------------
# Applications with unknown travel dates
# ---------------------------------------------------------------------------
class TestApplicationFlexibleDates:
    @pytest.fixture(scope="class")
    def files(self):
        return _upload_jpeg("passport"), _upload_jpeg("photo")

    def test_dates_unknown_true_accepted(self, api, files):
        p, ph = files
        payload = _app_payload(p, ph, {
            "arrival_date": "",
            "departure_date": "",
            "dates_unknown": True,
            "travel_window": "1_3_months",
            "purpose": "tourism",
        })
        r = api.post(f"{API}/applications", json=payload, timeout=30)
        assert r.status_code == 200, f"unknown-dates app should succeed: {r.status_code} {r.text[:400]}"
        d = r.json()
        assert d.get("reference_code")
        assert d["travel"]["dates_unknown"] is True
        assert d["travel"]["travel_window"] == "1_3_months"

    def test_missing_dates_without_unknown_rejected(self, api, files):
        p, ph = files
        payload = _app_payload(p, ph, {
            "arrival_date": "",
            "departure_date": "",
            "dates_unknown": False,
            "purpose": "tourism",
        })
        r = api.post(f"{API}/applications", json=payload, timeout=30)
        assert r.status_code == 400, f"missing dates should 400: {r.status_code} {r.text[:300]}"

    def test_classic_dates_still_ok(self, api, files):
        p, ph = files
        payload = _app_payload(p, ph, {
            "arrival_date": (date.today() + timedelta(days=20)).isoformat(),
            "departure_date": (date.today() + timedelta(days=25)).isoformat(),
            "dates_unknown": False,
            "purpose": "tourism",
        })
        r = api.post(f"{API}/applications", json=payload, timeout=30)
        assert r.status_code == 200, f"classic flow: {r.status_code} {r.text[:300]}"


# ---------------------------------------------------------------------------
# /api/orders regression (iter_79 tour scheduling bug fix)
# ---------------------------------------------------------------------------
class TestOrderTourSchedule:
    def _contact(self):
        return {
            "full_name": "TEST Sipa Ris",
            "email": f"TEST_iter80_order_{uuid.uuid4().hex[:6]}@example.com",
            "phone": "+905559991122",
        }

    def test_esim_order_ok(self, api):
        r = api.post(f"{API}/orders", json={
            "items": [{"product_id": "esim_3gb", "quantity": 1}],
            "contact": self._contact(),
            "payment_method": "card",
        }, timeout=20)
        assert r.status_code == 200, f"esim order: {r.status_code} {r.text[:300]}"
        assert r.json()["order"]["reference_code"].startswith("SV-")

    def test_insurance_order_ok(self, api):
        r = api.post(f"{API}/orders", json={
            "items": [{"product_id": "ins_15d", "quantity": 1}],
            "contact": self._contact(),
            "insured": insured_people(1),
            "travel_start": (date.today() + timedelta(days=20)).isoformat(),
            "payment_method": "card",
        }, timeout=20)
        assert r.status_code == 200, f"insurance order: {r.status_code} {r.text[:300]}"

    def test_tour_order_without_schedule_rejected(self, api):
        r = api.post(f"{API}/orders", json={
            "items": [{"product_id": "tour_desert_safari", "quantity": 1}],
            "contact": self._contact(),
            "payment_method": "card",
        }, timeout=20)
        assert r.status_code == 400, (
            f"tour without schedule must 400 (was iter_79 bug): {r.status_code} {r.text[:300]}"
        )

    def test_tour_order_with_schedule_ok(self, api):
        future = (date.today() + timedelta(days=30)).isoformat()
        r = api.post(f"{API}/orders", json={
            "items": [{
                "product_id": "tour_desert_safari",
                "quantity": 1,
                "scheduled_date": future,
                "scheduled_time": "15:00",
            }],
            "contact": self._contact(),
            "payment_method": "card",
        }, timeout=20)
        assert r.status_code == 200, f"tour with schedule: {r.status_code} {r.text[:300]}"
        order = r.json()["order"]
        line = order["items"][0]
        assert line.get("scheduled_date") == future
        assert line.get("scheduled_time") == "15:00"


# ---------------------------------------------------------------------------
# Email HTML Turkish content
# ---------------------------------------------------------------------------
class TestOrderEmails:
    def test_order_email_turkish(self, api):
        # email_outbox does not persist html body — test emailer functions directly
        import sys
        sys.path.insert(0, os.path.join(HERE, ".."))
        from emailer import order_received_html, order_admin_html, money

        order = {
            "reference_code": "SV-TEST0001",
            "contact": {"full_name": "TEST Türkçe", "email": "t@e.com", "phone": "+9055"},
            "items": [{"name": "Standart eSIM 3GB", "quantity": 1, "total": 288.0,
                       "starts_on": "2026-03-15", "ends_on": "2026-04-13"}],
            "payment": {"method": "card"},
            "currency": "TRY",
            "price": 288.0,
            "bundle_discount": 0,
        }
        html = order_received_html(order)
        admin_html = order_admin_html(order)

        # Turkish characters
        assert "Siparişiniz alındı" in html
        assert "Sipariş kodu" in html
        assert "Ödeme yöntemi" in html
        # Payment label
        assert "Kredi / Banka Kartı" in html, "expected 'Kredi / Banka Kartı' payment label"
        assert "Kredi / Banka Kartı" in admin_html
        # No ASCII-mangled variants
        for bad in ["Siparis kodu", "Musteri", "Odeme y", "Ödeme yontemi", ">card<"]:
            assert bad not in html, f"broken text '{bad}' found in HTML"
            assert bad not in admin_html, f"broken text '{bad}' found in admin HTML"
        # Money format Turkish (₺ suffix, . as thousands sep, , as decimal)
        assert "₺" in html
        assert money(1288.5) == "1.288,50 ₺"
        # Flexible date note text
        assert "tarihinde başlar" in html
        assert "tarihine kadar geçerli" in html
        # Admin html has Müşteri (with dotted i)
        assert "Müşteri" in admin_html
