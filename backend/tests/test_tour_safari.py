"""Backend tests for the new tour (Çöl Safarisi) product feature."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://insurance-checkout-3.preview.emergentagent.com").rstrip("/")


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ------------------ Products ------------------
def test_products_kind_tour(api):
    r = api.get(f"{BASE_URL}/api/products?kind=tour", timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    items = data.get("items", data) if isinstance(data, dict) else data
    assert isinstance(items, list) and len(items) == 1
    p = items[0]
    assert p["id"] == "tour_desert_safari"
    assert p["kind"] == "tour"
    assert p["kind_label"] == "Dubai turu"
    assert p["price_usd"] == 45.0
    assert p.get("active", True) is True
    assert len(p["features"]) == 5
    # TRY price ~2220 at FX ~49.41
    assert 2000 <= p["price"] <= 2400, f"Unexpected TRY price: {p['price']}"


def test_products_no_filter_includes_tour(api):
    r = api.get(f"{BASE_URL}/api/products", timeout=30)
    assert r.status_code == 200
    data = r.json()
    items = data.get("items", data) if isinstance(data, dict) else data
    ids = {i["id"] for i in items}
    kinds = {i["kind"] for i in items}
    assert "tour_desert_safari" in ids
    assert {"esim", "insurance", "tour"}.issubset(kinds)


# ------------------ Pricing quote ------------------
def test_pricing_quote_tour_qty2(api):
    payload = {
        "visa_type_ids": ["visa_30_single"],
        "store_items": [{"product_id": "tour_desert_safari", "quantity": 2}],
    }
    r = api.post(f"{BASE_URL}/api/pricing/quote", json=payload, timeout=30)
    assert r.status_code == 200, r.text
    data = r.json()
    store_items = data.get("store_items") or []
    tour_line = next((l for l in store_items if l.get("kind") == "tour"), None)
    assert tour_line, f"tour line missing: {data}"
    unit = float(tour_line["unit_price"])
    total = float(tour_line["total"])
    assert 2000 <= unit <= 2400
    assert abs(total - unit * 2) < 1.0
    # Bundle discount must NOT trigger (needs insurance + esim)
    bundle_discount = data.get("bundle_discount") or 0
    assert not bundle_discount or float(bundle_discount) == 0, f"bundle discount should be 0, got {bundle_discount}"
    grand = float(data.get("grand_total") or data.get("total") or 0)
    # visa_30_single ~5190 + tour ~4440 ≈ 9630
    assert 9000 <= grand <= 10200, f"unexpected grand total: {grand}"


def test_pricing_quote_tour_only_no_bundle_discount(api):
    # Even with tour + something else, bundle discount requires insurance + esim
    payload = {
        "visa_type_ids": ["visa_30_single"],
        "store_items": [
            {"product_id": "tour_desert_safari", "quantity": 1},
            {"product_id": "ins_8d", "quantity": 1},
        ],
    }
    r = api.post(f"{BASE_URL}/api/pricing/quote", json=payload, timeout=30)
    assert r.status_code == 200
    data = r.json()
    bundle_discount = data.get("bundle_discount") or 0
    assert not bundle_discount or float(bundle_discount) == 0
