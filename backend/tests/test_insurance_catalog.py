"""Backend tests: sigorta katalogu, fiyat sabitligi, siparis ve admin PATCH.

Iterasyon 57 - Dubai Vize Online sigorta akisi.
"""

import os
import sys
from pathlib import Path
import pytest
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", ".env"))

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_EMAIL = os.environ["ADMIN_LOGIN_EMAIL"]

EXPECTED_PRICES = {
    "ins_8d": (491, 8),
    "ins_15d": (560, 15),
    "ins_30d": (644, 30),
    "ins_60d": (735, 60),
    "ins_30d_plus": (2754, 30),
    "ins_60d_plus": (3989, 60),
}


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_token(session):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from admin_test_token import admin_token as make_token

    return make_token()


@pytest.fixture(scope="module")
def visa_type_id(session):
    r = session.get(f"{API}/visa-types")
    assert r.status_code == 200, r.text
    data = r.json()
    items = data if isinstance(data, list) else (data.get("items") or [])
    assert items, "Vize tipi listesi boş"
    return items[0]["id"]


# ------------------------------------------------------------------ katalog
class TestInsuranceCatalog:
    def test_returns_six_insurance_products(self, session):
        r = session.get(f"{API}/products", params={"kind": "insurance"})
        assert r.status_code == 200
        data = r.json()
        items = data["items"]
        ids = [p["id"] for p in items]
        assert len(items) == 6, f"Expected 6 insurance products, got {len(items)}: {ids}"
        for pid in EXPECTED_PRICES:
            assert pid in ids, f"Missing product {pid}"

    def test_prices_and_currency(self, session):
        r = session.get(f"{API}/products", params={"kind": "insurance"})
        items = {p["id"]: p for p in r.json()["items"]}
        for pid, (expected_price, expected_days) in EXPECTED_PRICES.items():
            p = items[pid]
            assert p["currency"] == "TRY", f"{pid} currency should be TRY"
            assert int(p["price"]) == expected_price, f"{pid} price={p['price']} expected {expected_price}"
            assert int(p["price_try"]) == expected_price
            assert int(p["validity_days"]) == expected_days
            # sigorta USD dönüşümü uygulanmıyor: price_usd olmamalı veya 0 olmalı
            assert not p.get("price_usd"), f"{pid} should NOT have price_usd (got {p.get('price_usd')})"

    def test_price_equals_price_try_independent_of_fx(self, session):
        """price == price_try, kur alanı bilgi amaçlı olsa da fiyata etki etmez."""
        r = session.get(f"{API}/products", params={"kind": "insurance"})
        for p in r.json()["items"]:
            assert float(p["price"]) == float(p["price_try"])

    def test_esim_still_uses_usd_to_try(self, session):
        r = session.get(f"{API}/products", params={"kind": "esim"})
        assert r.status_code == 200
        items = r.json()["items"]
        assert items, "eSIM ürünleri listelenmiyor"
        for p in items:
            assert p.get("price_usd"), f"eSIM {p['id']} price_usd tanımlı olmalı"
            assert p["currency"] == "TRY"
            # TL fiyat = USD * fx_rate (yuvarlama toleransı)
            expected = float(p["price_usd"]) * float(p["fx_rate"])
            # try_price 10 TL'nin katina yuvarlar -> tolerans 10
            assert abs(float(p["price"]) - expected) < 10.0, (
                f"eSIM {p['id']} price={p['price']} beklenen≈{expected}"
            )


# ---------------------------------------------------------------- siparisler
class TestInsuranceOrder:
    def test_create_order_ins_30d_qty2(self, session):
        payload = {
            "items": [{"product_id": "ins_30d", "quantity": 2}],
            "contact": {
                "full_name": "TEST Sigorta Alici",
                "email": "TEST_ins@example.com",
                "phone": "+905550000101",
            },
            "travel_start": "2026-03-01",
            "travel_end": "2026-03-15",
            "payment_method": "card",
        }
        r = session.post(f"{API}/orders", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        order = data["order"]
        assert order["reference_code"].startswith("SV-")
        assert len(order["items"]) == 1
        line = order["items"][0]
        assert line["product_id"] == "ins_30d"
        assert line["quantity"] == 2
        assert float(line["unit_price"]) == 644.0
        assert float(line["total"]) == 1288.0
        assert order["currency"] == "TRY"
        # validity 30 gün
        assert line["starts_on"] == "2026-03-01"
        assert line["ends_on"] == "2026-03-30"


# ------------------------------------------------ vize basvurusu store_items
class TestApplicationStoreItems:
    def _base_application(self, store_items):
        return {
            "contact": {
                "full_name": "TEST Bundle Alici",
                "email": "TEST_bundle@example.com",
                "phone": "+905550000102",
            },
            "travelers": [
                {
                    "first_name": "TEST",
                    "last_name": "USER",
                    "birth_date": "1990-01-01",
                    "passport_number": "U12345678",
                    "passport_expiry": "2030-01-01",
                    "nationality": "TR",
                    "gender": "male",
                    "marital_status": "single",
                    "profession": "Employee",
                    "mother_name": "USER",
                    "father_name": "USER",
                    "visa_type_id": "tourist_30",
                }
            ],
            "arrival_date": "2026-03-01",
            "departure_date": "2026-03-15",
            "addons": {"express": False, "insurance": False},
            "extra_docs": [],
            "store_items": store_items,
            "payment_method": "card",
        }

    def test_pricing_quote_insurance_only(self, session, visa_type_id):
        r = session.post(f"{API}/pricing/quote", json={
            "visa_type_ids": [visa_type_id],
            "addons": {"express": False, "insurance": False},
            "arrival_date": "2026-03-01",
            "departure_date": "2026-03-15",
            "store_items": [{"product_id": "ins_30d", "quantity": 1}],
        })
        assert r.status_code == 200, r.text
        q = r.json()
        # sadece sigorta -> bundle indirimi uygulanmamalı
        assert q["bundle_discount"] == 0.0
        store_total = sum(float(l["total"]) for l in q["store_items"])
        assert store_total == 644.0

    def test_pricing_quote_bundle_insurance_plus_esim(self, session, visa_type_id):
        r = session.post(f"{API}/pricing/quote", json={
            "visa_type_ids": [visa_type_id],
            "addons": {"express": False, "insurance": False},
            "arrival_date": "2026-03-01",
            "departure_date": "2026-03-15",
            "store_items": [
                {"product_id": "ins_30d", "quantity": 1},
                {"product_id": "esim_3gb", "quantity": 1},
            ],
        })
        assert r.status_code == 200, r.text
        q = r.json()
        # sigorta + esim = %10 indirim
        store_total = sum(float(l["total"]) for l in q["store_items"])
        assert q["bundle_discount"] > 0, "Bundle indirimi uygulanmadı"
        assert abs(q["bundle_discount"] - round(store_total * 0.10, 2)) < 0.01


# ---------------------------------------------------------------- admin PATCH
class TestAdminProductPatch:
    def test_patch_price_try_updates_public_endpoint(self, session, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Yeni fiyat
        new_price = 699.0
        r = session.patch(
            f"{API}/admin/products/ins_30d",
            json={"price_try": new_price},
            headers=headers,
        )
        assert r.status_code == 200, r.text
        updated = r.json()
        assert float(updated["price_try"]) == new_price
        assert float(updated["price"]) == new_price

        # Public endpointte yansıyor
        pub = session.get(f"{API}/products", params={"kind": "insurance"}).json()
        item = next(p for p in pub["items"] if p["id"] == "ins_30d")
        assert float(item["price_try"]) == new_price
        assert float(item["price"]) == new_price

        # Eski fiyata geri döndür
        restore = session.patch(
            f"{API}/admin/products/ins_30d",
            json={"price_try": 644.0},
            headers=headers,
        )
        assert restore.status_code == 200
        pub2 = session.get(f"{API}/products", params={"kind": "insurance"}).json()
        item2 = next(p for p in pub2["items"] if p["id"] == "ins_30d")
        assert float(item2["price_try"]) == 644.0
