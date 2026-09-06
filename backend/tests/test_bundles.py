"""Tests for /api/bundles + bundle discount applied to orders."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/") or "https://whatsapp-ai-test.preview.emergentagent.com"
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _get(session, url, **params):
    r = session.get(url, params=params, timeout=30)
    assert r.status_code == 200, f"{url} -> {r.status_code} {r.text[:200]}"
    return r.json()


class TestBundles:
    def test_all_bundles(self, session):
        data = _get(session, f"{API}/bundles")
        items = data["items"]
        assert len(items) == 6
        ids = {b["id"] for b in items}
        assert ids == {
            "pack_short",
            "pack_standard",
            "pack_comfort",
            "pack_family",
            "pack_long",
            "pack_long_plus",
        }
        # sub-objects must have price/name
        for b in items:
            assert b["insurance"]["price"] > 0
            assert b["esim"]["price"] > 0
            assert b["insurance"]["name"]
            assert b["esim"]["name"]

    def test_visa_30_bundles(self, session):
        data = _get(session, f"{API}/bundles", visa_days=30)
        items = {b["id"]: b for b in data["items"]}
        assert set(items.keys()) == {"pack_short", "pack_standard", "pack_comfort", "pack_family"}
        # pack_standard is popular
        assert items["pack_standard"]["popular"] is True
        # Check pairing
        assert items["pack_short"]["insurance"]["id"] == "ins_8d"
        assert items["pack_short"]["esim"]["id"] == "esim_1gb"
        assert items["pack_standard"]["insurance"]["id"] == "ins_15d"
        assert items["pack_standard"]["esim"]["id"] == "esim_3gb"
        assert items["pack_comfort"]["insurance"]["id"] == "ins_30d_plus"
        assert items["pack_comfort"]["esim"]["id"] == "esim_10gb"
        # Verify math: list_total = ins.price + esim.price; discount = 10%; price = list - discount
        # (pack_family adet bazli hesaplanir, bu dogrulamadan haric tutulur)
        for bundle_id, b in items.items():
            if bundle_id == "pack_family":
                continue
            expected_list = round(b["insurance"]["price"] + b["esim"]["price"], 2)
            assert abs(b["list_total"] - expected_list) < 0.02, f"list_total mismatch {b}"
            expected_disc = round(expected_list * 0.10, 2)
            assert abs(b["discount"] - expected_disc) < 0.05, f"discount mismatch {b}"
            expected_price = round(expected_list - expected_disc, 2)
            assert abs(b["price"] - expected_price) < 0.05, f"price mismatch {b}"

    def test_visa_60_bundles(self, session):
        data = _get(session, f"{API}/bundles", visa_days=60)
        items = {b["id"]: b for b in data["items"]}
        assert set(items.keys()) == {"pack_long", "pack_long_plus"}
        assert items["pack_long"]["insurance"]["id"] == "ins_60d"
        assert items["pack_long"]["esim"]["id"] == "esim_10gb"
        assert items["pack_long_plus"]["insurance"]["id"] == "ins_60d_plus"
        assert items["pack_long_plus"]["esim"]["id"] == "esim_unlimited"


class TestOrderBundleDiscount:
    """Create a store order matching a bundle and verify 10% discount applies and equals bundle price."""

    def test_pack_standard_order_price_matches_bundle(self, session):
        bundles = _get(session, f"{API}/bundles", visa_days=30)["items"]
        pack = next(b for b in bundles if b["id"] == "pack_standard")

        payload = {
            "items": [
                {"product_id": "ins_15d", "quantity": 1},
                {"product_id": "esim_3gb", "quantity": 1},
            ],
            "contact": {
                "full_name": "TEST Bundle Buyer",
                "email": "test_bundle@example.com",
                "phone": "+905551112233",
            },
            "payment_method": "card",
        }
        r = session.post(f"{API}/orders", json=payload, timeout=30)
        assert r.status_code == 200, r.text[:300]
        order = r.json()["order"]
        assert order["items_total"] == pack["list_total"], (order["items_total"], pack["list_total"])
        assert abs(order["bundle_discount"] - pack["discount"]) < 0.05
        assert abs(order["price"] - pack["price"]) < 0.05
        assert order["bundle_discount_rate"] == 0.10
        # store reference for cleanup context
        print(f"TEST_ORDER reference={order['reference_code']} price={order['price']}")
