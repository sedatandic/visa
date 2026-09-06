"""Iteration 102 - Dinamik Aile Paketi (yolcu sayisi steppers + col safarisi 'tam tatil').

Covers:
- New GET /api/bundles/quote endpoint (family live pricing incl. tour)
- Regression: /api/bundles unchanged for the other 5 bundles
- Regression: ?visa_days=60 filter
- Order pricing parity: POST /api/orders with the same lines yields the same bundle_discount as the quote
"""
import os
import pytest
import requests

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or "").rstrip("/") or "https://whatsapp-ai-test.preview.emergentagent.com"
API = f"{BASE_URL}/api"


def _quote(**params):
    r = requests.get(f"{API}/bundles/quote", params=params, timeout=30)
    return r


# --- /api/bundles/quote --------------------------------------------------------
class TestQuoteFamily:
    def test_default_2a_1c_no_tour(self):
        r = _quote(bundle_id="pack_family", adults=2, children=1, tour="false")
        assert r.status_code == 200, r.text
        it = r.json()["item"]
        assert it["quantities"] == {"insurance": 3, "esim": 2, "tour": 0}
        assert it["list_total"] == 3160.0
        assert it["discount"] == 316.0
        assert it["price"] == 2844.0
        f = it["family"]
        assert f["visa_subtotal"] == 12850.0
        assert f["visa_discount"] == 1285.0
        assert f["visa_discount_rate"] == 0.1
        assert f["traveler_count"] == 3
        assert it["total_with_visa"] == 14409.0
        # tour object exposed but not selected
        assert it["tour"] is not None
        assert it["tour"]["selected"] is False
        assert it["tour"]["total"] == 0.0

    def test_2a_1c_with_tour(self):
        r = _quote(bundle_id="pack_family", adults=2, children=1, tour="true")
        assert r.status_code == 200
        it = r.json()["item"]
        assert it["quantities"] == {"insurance": 3, "esim": 2, "tour": 3}
        # extras 3160 + tour 3*2220=6660 = 9820 ; discount 982 ; price 8838
        assert it["list_total"] == 9820.0
        assert it["discount"] == 982.0
        assert it["price"] == 8838.0
        assert it["tour"]["selected"] is True
        assert it["tour"]["total"] == 6660.0
        # visa untouched
        assert it["family"]["visa_subtotal"] == 12850.0
        assert it["family"]["visa_discount"] == 1285.0
        assert it["total_with_visa"] == 20403.0

    def test_3a_2c_with_tour_family_tier_15pct(self):
        r = _quote(bundle_id="pack_family", adults=3, children=2, tour="true")
        assert r.status_code == 200
        it = r.json()["item"]
        assert it["quantities"] == {"insurance": 5, "esim": 3, "tour": 5}
        # extras: 5*560 + 3*740 = 2800+2220=5020 ; tour: 5*2220=11100 ; list 16120 ; disc 1612 ; price 14508
        assert it["price"] == 14508.0
        f = it["family"]
        assert f["visa_discount_rate"] == 0.15
        # visa subtotal 3*5190 + 2*2470 = 15570+4940 = 20510 ; 15% = 3076.5
        assert f["visa_subtotal"] == 20510.0
        assert f["visa_discount"] == 3076.5
        assert it["total_with_visa"] == 31941.5

    def test_4a_2c_15pct_tier(self):
        r = _quote(bundle_id="pack_family", adults=4, children=2, tour="false")
        assert r.status_code == 200
        it = r.json()["item"]
        assert it["family"]["visa_discount_rate"] == 0.15

    def test_clamping_high_and_low(self):
        # adults 99 -> 6, children 99 -> 4
        r = _quote(bundle_id="pack_family", adults=99, children=99, tour="false")
        assert r.status_code == 200
        f = r.json()["item"]["family"]
        assert f["adults"] == 6
        assert f["children"] == 4
        assert f["traveler_count"] == 10
        # adults 0 -> 1
        r2 = _quote(bundle_id="pack_family", adults=0, children=0, tour="false")
        assert r2.status_code == 200
        assert r2.json()["item"]["family"]["adults"] == 1
        assert r2.json()["item"]["family"]["children"] == 0

    def test_unknown_bundle_id_404(self):
        r = _quote(bundle_id="pack_unknown", adults=1, children=0, tour="false")
        assert r.status_code == 404


# --- /api/bundles regression ---------------------------------------------------
EXPECTED = {
    "pack_short": (837.9, 6027.9),
    "pack_standard": (1170.0, 6360.0),
    "pack_comfort": (3765.6, 8955.6),
    "pack_family": (2844.0, 14409.0),  # default 2+1 no tour
    "pack_long": (1948.5, 11828.5),
    "pack_long_plus": (5768.1, 15648.1),
}


class TestBundlesList:
    def test_all_bundles(self):
        r = requests.get(f"{API}/bundles", timeout=30)
        assert r.status_code == 200
        items = {b["id"]: b for b in r.json()["items"]}
        assert set(items.keys()) == set(EXPECTED.keys())
        for bid, (price, tot) in EXPECTED.items():
            assert items[bid]["price"] == price, bid
            assert items[bid]["total_with_visa"] == tot, bid
        # family default tour qty must be 0
        assert items["pack_family"]["quantities"]["tour"] == 0

    def test_visa_days_60_filter(self):
        r = requests.get(f"{API}/bundles", params={"visa_days": 60}, timeout=30)
        assert r.status_code == 200
        ids = {b["id"] for b in r.json()["items"]}
        assert ids == {"pack_long", "pack_long_plus"}


# --- Order-pricing parity (quote vs POST /api/orders) --------------------------
class TestOrderParity:
    def test_order_bundle_discount_matches_quote_tour(self):
        # Same basket as 2a+1c with tour: ins x3, esim x2, tour x3
        payload = {
            "items": [
                {"product_id": "ins_15d", "quantity": 3},
                {"product_id": "esim_3gb", "quantity": 2},
                {"product_id": "tour_desert_safari", "quantity": 3, "scheduled_date": "2026-10-12", "scheduled_time": "14:00"},
            ],
            "contact": {
                "full_name": "TEST Iter102",
                "email": "delivered@resend.dev",
                "phone": "05325882630",
            },
            "payment_method": "transfer",
            "note": "TEST_iteration_102",
        }
        r = requests.post(f"{API}/orders", json=payload, timeout=45)
        assert r.status_code == 200, r.text
        order = r.json()["order"]
        # Match quote: list 9820 ; discount 982 ; price 8838
        assert order["items_total"] == 9820.0
        assert order["bundle_discount"] == 982.0
        assert order["price"] == 8838.0
