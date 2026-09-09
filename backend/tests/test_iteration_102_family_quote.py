"""Iteration 102 - Dinamik Aile Paketi (yolcu sayisi steppers + col safarisi 'tam tatil').

Covers:
- New GET /api/bundles/quote endpoint (family live pricing incl. tour)
- Regression: /api/bundles unchanged for the other 5 bundles
- Regression: ?visa_days=60 filter
- Order pricing parity: POST /api/orders with the same lines yields the same bundle_discount as the quote
"""
import os
import requests

from insured_data import insured_people

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or "").rstrip("/") or "https://whatsapp-bot-test-2.preview.emergentagent.com"
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
        # Tur fiyati USD'ye bagli oldugu icin beklenen tutar guncel birim fiyattan turetilir
        tour_unit = it["tour"]["price"]
        extras = 3 * it["insurance"]["price"] + 2 * it["esim"]["price"]
        tour_total = round(3 * tour_unit, 2)
        list_total = round(extras + tour_total, 2)
        assert it["tour"]["total"] == tour_total
        assert it["list_total"] == list_total
        assert it["discount"] == round(list_total * 0.1, 2)
        assert it["price"] == round(list_total * 0.9, 2)
        assert it["tour"]["selected"] is True
        # visa untouched
        assert it["family"]["visa_subtotal"] == 12850.0
        assert it["family"]["visa_discount"] == 1285.0
        assert it["total_with_visa"] == round(12850.0 - 1285.0 + list_total * 0.9, 2)

    def test_3a_2c_with_tour_family_tier_15pct(self):
        r = _quote(bundle_id="pack_family", adults=3, children=2, tour="true")
        assert r.status_code == 200
        it = r.json()["item"]
        assert it["quantities"] == {"insurance": 5, "esim": 3, "tour": 5}
        list_total = round(
            5 * it["insurance"]["price"] + 3 * it["esim"]["price"] + 5 * it["tour"]["price"], 2
        )
        assert it["list_total"] == list_total
        assert it["price"] == round(list_total * 0.9, 2)
        f = it["family"]
        assert f["visa_discount_rate"] == 0.15
        # visa subtotal 3*5190 + 2*2470 = 15570+4940 = 20510 ; 15% = 3076.5
        assert f["visa_subtotal"] == 20510.0
        assert f["visa_discount"] == 3076.5
        assert it["total_with_visa"] == round(20510.0 - 3076.5 + list_total * 0.9, 2)

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
EXPECTED_BUNDLE_IDS = {
    "pack_short",
    "pack_standard",
    "pack_comfort",
    "pack_family",
    "pack_long",
    "pack_long_plus",
}


class TestBundlesList:
    def test_all_bundles(self):
        """Fiyatlar canli tarifeden geldigi icin tutarlilik dogrulanir, sabit tutar degil."""
        r = requests.get(f"{API}/bundles", timeout=30)
        assert r.status_code == 200
        items = {b["id"]: b for b in r.json()["items"]}
        assert set(items.keys()) == EXPECTED_BUNDLE_IDS
        for bid, item in items.items():
            assert item["price"] == round(item["list_total"] - item["discount"], 2), bid
            assert item["total_with_visa"] > item["price"], bid
            assert item["insurance"]["price"] > 0 and item["esim"]["price"] > 0, bid
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
            "insured": insured_people(3),
            "travel_start": "2026-10-10",
            "note": "TEST_iteration_102",
        }
        r = requests.post(f"{API}/orders", json=payload, timeout=45)
        assert r.status_code == 200, r.text
        order = r.json()["order"]
        expected_total = round(sum(float(line["unit_price"]) * line["quantity"] for line in order["items"]), 2)
        assert order["items_total"] == expected_total
        assert order["bundle_discount"] == round(expected_total * 0.1, 2)
        assert order["price"] == round(expected_total - order["bundle_discount"], 2)
