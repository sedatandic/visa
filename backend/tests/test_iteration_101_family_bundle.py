"""Iteration 101 - Aile Paketi (family bundle) + multi-visa cart backend regression tests."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/") or "https://whatsapp-bot-test-2.preview.emergentagent.com"


@pytest.fixture(scope="module")
def bundles():
    r = requests.get(f"{BASE_URL}/api/bundles", timeout=30)
    assert r.status_code == 200
    return r.json()["items"]


def get_bundle(bundles, bid):
    for b in bundles:
        if b["id"] == bid:
            return b
    return None


# --- 1) Family bundle values ---------------------------------------------------
class TestFamilyBundle:
    def test_bundle_count_and_family(self, bundles):
        assert len(bundles) == 6, f"expected 6 bundles, got {len(bundles)}"
        fam = get_bundle(bundles, "pack_family")
        assert fam is not None
        assert fam["name"] == "Aile Paketi"
        assert fam["quantities"] == {"insurance": 3, "esim": 2, "tour": 0}
        assert fam["price"] == 2844.0
        assert fam["total_with_visa"] == 14409.0

    def test_family_details(self, bundles):
        fam = get_bundle(bundles, "pack_family")
        f = fam["family"]
        assert f["adults"] == 2
        assert f["children"] == 1
        assert f["traveler_count"] == 3
        assert f["visa_subtotal"] == 12850.0
        assert f["visa_discount"] == 1285.0
        assert f["visa_discount_rate"] == 0.1
        assert f["child_visa"]["id"] == "visa_30_child"
        assert f["child_visa"]["price"] == 2470.0

    def test_pack_standard_unchanged(self, bundles):
        std = get_bundle(bundles, "pack_standard")
        assert std["price"] == 1170.0
        assert std["total_with_visa"] == 6360.0
        assert std.get("family") is None


# --- 2) visa_days filter regression --------------------------------------------
class TestBundleFilter:
    def test_visa_days_60(self):
        r = requests.get(f"{BASE_URL}/api/bundles?visa_days=60", timeout=30)
        assert r.status_code == 200
        ids = [b["id"] for b in r.json()["items"]]
        assert "pack_long" in ids
        assert "pack_family" not in ids
        assert "pack_standard" not in ids


# --- 3) Products + Orders regression with qty>1 --------------------------------
class TestOrderMultiQty:
    def test_products_available(self):
        r = requests.get(f"{BASE_URL}/api/products", timeout=30)
        assert r.status_code == 200
        ids = {p["id"] for p in r.json()["items"]}
        assert {"ins_15d", "esim_3gb"}.issubset(ids)

    def test_bank_transfer_family_extras_order(self):
        payload = {
            "items": [
                {"product_id": "ins_15d", "quantity": 3},
                {"product_id": "esim_3gb", "quantity": 2},
            ],
            "contact": {
                "full_name": "TEST Aile",
                "email": "delivered@resend.dev",
                "phone": "05325882630",
            },
            "payment_method": "transfer",
            "note": "TEST_iteration_101",
        }
        r = requests.post(f"{BASE_URL}/api/orders", json=payload, timeout=45)
        assert r.status_code == 200, r.text
        data = r.json()
        order = data["order"]
        # items_total = 3*560 + 2*740 = 3160 ; bundle discount 10% = 316 ; price 2844
        assert order["items_total"] == 3160.0
        assert order["bundle_discount"] == 316.0
        assert order["bundle_discount_rate"] == 0.1
        assert order["price"] == 2844.0
        assert data.get("bank") is not None
