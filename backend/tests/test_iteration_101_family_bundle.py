"""Iteration 101 - Aile Paketi (family bundle) + multi-visa cart backend regression tests."""
import os
import pytest
import requests

from insured_data import insured_people

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
        """Tutarlar canli fiyattan turetilir (fiyatlar panelden yonetiliyor)."""
        assert len(bundles) == 6, f"expected 6 bundles, got {len(bundles)}"
        fam = get_bundle(bundles, "pack_family")
        assert fam is not None
        assert fam["name"] == "Aile Paketi"
        assert fam["quantities"] == {"insurance": 3, "esim": 2, "tour": 0}
        list_total = round(3 * fam["insurance"]["price"] + 2 * fam["esim"]["price"], 2)
        assert fam["list_total"] == list_total
        assert fam["discount"] == round(list_total * 0.1, 2)
        assert fam["price"] == round(list_total - fam["discount"], 2)
        f = fam["family"]
        assert fam["total_with_visa"] == round(
            f["visa_subtotal"] - f["visa_discount"] + fam["price"], 2
        )

    def test_family_details(self, bundles):
        fam = get_bundle(bundles, "pack_family")
        f = fam["family"]
        assert f["adults"] == 2
        assert f["children"] == 1
        assert f["traveler_count"] == 3
        assert f["visa_discount_rate"] == 0.1
        assert f["visa_discount"] == round(f["visa_subtotal"] * 0.1, 2)
        assert f["child_visa"]["id"] == "visa_30_child"
        assert f["child_visa"]["price"] > 0
        # 2 yetiskin + 1 cocuk vizesi toplami (yetiskin vizesi paketin "visa" alaninda)
        assert f["visa_subtotal"] == round(
            2 * fam["visa"]["price"] + f["child_visa"]["price"], 2
        )

    def test_pack_standard_unchanged(self, bundles):
        std = get_bundle(bundles, "pack_standard")
        list_total = round(
            std["quantities"]["insurance"] * std["insurance"]["price"]
            + std["quantities"]["esim"] * std["esim"]["price"],
            2,
        )
        assert std["list_total"] == list_total
        assert std["price"] == round(list_total - std["discount"], 2)
        assert std["total_with_visa"] > std["price"]
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
            "insured": insured_people(3),
            "travel_start": "2026-10-10",
            "note": "TEST_iteration_101",
        }
        r = requests.post(f"{BASE_URL}/api/orders", json=payload, timeout=45)
        assert r.status_code == 200, r.text
        data = r.json()
        order = data["order"]
        catalog = {p["id"]: p for p in requests.get(f"{BASE_URL}/api/products", timeout=30).json()["items"]}
        expected_total = round(
            3 * float(catalog["ins_15d"]["price"]) + 2 * float(catalog["esim_3gb"]["price"]), 2
        )
        assert order["items_total"] == expected_total
        assert order["bundle_discount"] == round(expected_total * 0.1, 2)
        assert order["bundle_discount_rate"] == 0.1
        assert order["price"] == round(expected_total - order["bundle_discount"], 2)
        assert data.get("bank") is not None
