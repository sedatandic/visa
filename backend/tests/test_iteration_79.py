"""Iteration 79 regression:
- (B) '48 saatlik Transit Vize' removed from catalog + guides + application validation
- (C) new 'Çöl Safarisi · VIP Akşam Turu' (tour_desert_safari_vip, 55 USD, 5 slots)
- General regression sanity: /api/products, /api/bundles, admin login.

Uses the request/response envelope discovered in iter_78: products endpoint returns
{"items":[...], "fx":..., "bundle":...} and orders endpoint returns {"order":{...}}.
"""
import io
import os
import sys
import uuid
from datetime import date, timedelta

import pytest
import requests
from dotenv import load_dotenv

HERE = os.path.dirname(__file__)
load_dotenv(os.path.join(HERE, "..", ".env"))
load_dotenv(os.path.join(HERE, "..", "..", "frontend", ".env"))

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_EMAIL = os.environ["ADMIN_LOGIN_EMAIL"]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _upload_jpeg(name: str, doc_type: str) -> str:
    jpeg = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00" + b"\x08" * 64 + b"\xff\xd9"
    )
    files = {"file": (name, io.BytesIO(jpeg), "image/jpeg")}
    r = requests.post(f"{API}/uploads", files=files, data={"doc_type": doc_type}, timeout=20)
    assert r.status_code == 200, f"upload {doc_type} failed: {r.status_code} {r.text[:200]}"
    return r.json()["file_id"]


def _base_app_payload(visa_type_id: str, passport_fid: str, photo_fid: str):
    return {
        "contact": {
            "full_name": "TEST_Applicant Transit",
            "email": f"TEST_transit_{uuid.uuid4().hex[:6]}@example.com",
            "phone": "+905551112233",
            "whatsapp_optin": False,
        },
        "travelers": [{
            "first_name": "TEST",
            "last_name": "TRANSIT",
            "birth_date": "1990-05-05",
            "gender": "male",
            "applicant_type": "adult",
            "nationality": "TR",
            "passport_no": "U12345678",
            "passport_expiry": (date.today() + timedelta(days=400)).isoformat(),
            "visa_type_id": visa_type_id,
            "passport_file_id": passport_fid,
            "photo_file_id": photo_fid,
        }],
        "travel": {
            "arrival_date": (date.today() + timedelta(days=15)).isoformat(),
            "departure_date": (date.today() + timedelta(days=17)).isoformat(),
            "purpose": "tourism",
        },
        "addons": {},
        "store_items": [],
        "extra_documents": {},
        "kvkk_accepted": True,
    }


# ---------------------------------------------------------------------------
# (B) Transit visa removal
# ---------------------------------------------------------------------------
class TestTransitRemoved:
    def test_visa_types_no_transit(self, api):
        r = api.get(f"{API}/visa-types")
        assert r.status_code == 200
        types = r.json()
        assert isinstance(types, list)
        active = [t for t in types if t.get("active", True)]
        assert len(active) == 7, f"expected 7 active visa types, got {len(active)}: {[t.get('id') for t in active]}"
        ids = {t.get("id") for t in types}
        slugs = {t.get("slug") for t in types}
        assert "visa_transit_48" not in ids, f"visa_transit_48 still in list: {ids}"
        assert "transit-vize" not in slugs, "transit-vize slug still present"

    def test_visa_guides_no_transit(self, api):
        r = api.get(f"{API}/visa-guides")
        assert r.status_code == 200
        body = r.json()
        items = body if isinstance(body, list) else (body.get("items") or body.get("guides") or [])
        assert len(items) == 7, f"expected 7 guides, got {len(items)}"
        slugs = {g.get("slug") for g in items}
        assert "transit-vize" not in slugs, "transit-vize guide still present"

    def test_visa_guide_transit_returns_404(self, api):
        r = api.get(f"{API}/visa-guides/transit-vize")
        assert r.status_code == 404, f"expected 404, got {r.status_code}: {r.text[:200]}"

    def test_application_with_transit_visa_rejected(self, api):
        passport = _upload_jpeg("passport.jpg", "passport")
        photo = _upload_jpeg("photo.jpg", "photo")
        payload = _base_app_payload("visa_transit_48", passport, photo)
        r = api.post(f"{API}/applications", json=payload, timeout=30)
        assert r.status_code != 200, (
            f"application with visa_transit_48 should be rejected, "
            f"got {r.status_code}: {r.text[:400]}"
        )
        assert r.status_code in (400, 404, 422), f"unexpected status {r.status_code}"


# ---------------------------------------------------------------------------
# (C) new VIP safari
# ---------------------------------------------------------------------------
class TestVipSafari:
    def test_both_safaris_listed(self, api):
        r = api.get(f"{API}/products?kind=tour")
        assert r.status_code == 200
        body = r.json()
        items = body["items"] if isinstance(body, dict) else body
        assert isinstance(items, list)
        by_id = {p["id"]: p for p in items}
        assert "tour_desert_safari" in by_id
        assert "tour_desert_safari_vip" in by_id, f"VIP safari missing: {list(by_id)}"

        std, vip = by_id["tour_desert_safari"], by_id["tour_desert_safari_vip"]
        assert float(std.get("price_usd") or 0) == 45.0
        assert float(vip.get("price_usd") or 0) == 55.0
        for p in (std, vip):
            assert (p.get("currency") or "TRY") == "TRY"
            price = float(p.get("price") or p.get("price_try") or 0)
            assert price > 0, f"missing TRY price on {p['id']}"
            fx = float(p.get("fx_rate") or (body.get("fx") or {}).get("effective_rate") or 0)
            assert fx > 0, "missing fx on response"
            assert p.get("needs_schedule") is True, f"{p['id']} needs_schedule should be True"
            slots = p.get("time_slots") or []
            assert len(slots) == 5, f"{p['id']} expected 5 time_slots, got {len(slots)}"

    def test_vip_order_with_schedule_succeeds(self, api):
        """POST /api/orders with scheduled_date + scheduled_time succeeds and stores schedule."""
        picked_date = (date.today() + timedelta(days=14)).isoformat()
        payload = {
            "items": [{
                "product_id": "tour_desert_safari_vip",
                "quantity": 1,
                "scheduled_date": picked_date,
                "scheduled_time": "15:00",
            }],
            "contact": {
                "full_name": "TEST VIP Sched",
                "email": f"TEST_vip_ok_{uuid.uuid4().hex[:6]}@example.com",
                "phone": "+905551112255",
            },
            "payment_method": "card",
        }
        r = api.post(f"{API}/orders", json=payload, timeout=20)
        assert r.status_code == 200, f"scheduled VIP order failed: {r.status_code} {r.text[:300]}"
        body = r.json()
        order = body.get("order") or body
        ref = order.get("reference_code") or order.get("reference")
        assert ref and ref.startswith("SV-"), f"bad reference: {order}"

        # Retrieve and confirm schedule persisted
        email = payload["contact"]["email"]
        r2 = requests.get(f"{API}/orders/{ref}?email={email}", timeout=15)
        assert r2.status_code == 200, f"GET order failed: {r2.status_code} {r2.text[:200]}"
        got = r2.json()
        order2 = got.get("order") or got
        item = (order2.get("items") or [{}])[0]
        assert item.get("scheduled_date") == picked_date, (
            f"BUG: scheduled_date not persisted (got {item.get('scheduled_date')}). "
            f"POST /api/orders ignores schedule fields entirely — OrderItemIn has no scheduled_* fields "
            f"and _build_order_line does not call _tour_schedule."
        )
        assert item.get("scheduled_time") == "15:00", (
            f"BUG: scheduled_time not persisted (got {item.get('scheduled_time')})"
        )

    def test_vip_order_without_schedule_is_rejected(self, api):
        """POST /api/orders for a needs_schedule tour WITHOUT date/time must be rejected."""
        payload = {
            "items": [{"product_id": "tour_desert_safari_vip", "quantity": 1}],
            "contact": {
                "full_name": "TEST VIP NoSched",
                "email": f"TEST_vip_{uuid.uuid4().hex[:6]}@example.com",
                "phone": "+905551112244",
            },
            "payment_method": "card",
        }
        r = api.post(f"{API}/orders", json=payload, timeout=20)
        assert r.status_code >= 400, (
            f"BUG: order without schedule was accepted (status {r.status_code}). "
            f"Both tour_desert_safari and tour_desert_safari_vip carry needs_schedule=True "
            f"but /api/orders does not enforce it. Only application flow "
            f"(routes_public._tour_schedule) validates schedule. Fix: extend OrderItemIn "
            f"with scheduled_date/scheduled_time and call _tour_schedule from routes_store._build_order_line."
        )


# ---------------------------------------------------------------------------
# General regression sanity
# ---------------------------------------------------------------------------
class TestRegression:
    def test_products_all(self, api):
        r = api.get(f"{API}/products")
        assert r.status_code == 200
        body = r.json()
        items = body["items"] if isinstance(body, dict) else body
        # 4 esim + 6 insurance + 2 tour = 12 (iter_78 had 11 with only 1 tour)
        assert len(items) == 12, f"expected 12 products, got {len(items)}"
        kinds = {p.get("kind") for p in items}
        assert kinds == {"esim", "insurance", "tour"}

    def test_bundles(self, api):
        r = api.get(f"{API}/bundles")
        assert r.status_code == 200
        body = r.json()
        items = body["items"] if isinstance(body, dict) else body
        assert isinstance(items, list) and items

    def test_admin_login(self, api):
        # Sifreli giris kaldirildi: endpoint 404, jeton OTP ile alinir.
        r = api.post(f"{API}/admin/login", json={"email": ADMIN_EMAIL, "password": "x"})
        assert r.status_code == 404
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from admin_test_token import admin_token as make_token

        me = api.get(f"{API}/admin/emails", headers={"Authorization": f"Bearer {make_token()}"})
        assert me.status_code == 200
