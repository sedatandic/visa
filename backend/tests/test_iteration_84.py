"""Iteration 84 backend tests.

Scope:
- Kademeli aile indirimi via POST /api/pricing/quote (1..5 travelers, visa_30_single)
- GET /api/content/site: family_discount_tiers ve family_discount_text
- /photo-guide/*.jpg statik dosyalarinin 200 donmesi
- Regresyon: /api/applications 4 yolcuyla toplam indirim %15
- Regresyon: /api/order endpointi hala mevcut (satinalma admin akisi)
"""
import os
import requests
import pytest


def _env(name: str) -> str:
    v = os.environ.get(name)
    if v:
        return v
    for p in ("/app/frontend/.env", "/app/backend/.env"):
        try:
            for line in open(p):
                if line.startswith(name + "="):
                    return line.split("=", 1)[1].strip().strip('"')
        except FileNotFoundError:
            pass
    raise RuntimeError(name)


BASE = _env("REACT_APP_BACKEND_URL").rstrip("/")


@pytest.fixture(scope="module")
def s():
    return requests.Session()


# ---------------------------------------------------------------- pricing tiers
class TestFamilyDiscountTiers:
    EXPECTED = {1: 0.0, 2: 0.10, 3: 0.10, 4: 0.15, 5: 0.15}

    @pytest.mark.parametrize("count", [1, 2, 3, 4, 5])
    def test_quote_family_discount_rate(self, s, count):
        payload = {
            "visa_type_ids": ["visa_30_single"] * count,
            "addons": {},
        }
        r = s.post(f"{BASE}/api/pricing/quote", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("traveler_count") == count
        expected = self.EXPECTED[count]
        assert abs(body.get("family_discount_rate", -1) - expected) < 1e-6, body
        subtotal = body["subtotal"]
        expected_discount = round(subtotal * expected, 2)
        assert abs(body["family_discount"] - expected_discount) < 0.01, body


# ---------------------------------------------------------------- content/site
class TestContentSite:
    def test_family_discount_tiers_and_text(self, s):
        r = s.get(f"{BASE}/api/content/site", timeout=15)
        assert r.status_code == 200
        body = r.json()
        tiers = body.get("family_discount_tiers")
        assert tiers == [{"min": 2, "rate": 0.10}, {"min": 4, "rate": 0.15}], tiers
        txt = body.get("family_discount_text") or ""
        assert "%10" in txt and "%15" in txt, txt


# ---------------------------------------------------------------- photo-guide statics
class TestPhotoGuideAssets:
    ASSETS = [
        "/photo-guide/ok.jpg",
        "/photo-guide/bad-background.jpg",
        "/photo-guide/bad-sunglasses.jpg",
        "/photo-guide/bad-selfie.jpg",
    ]

    @pytest.mark.parametrize("path", ASSETS)
    def test_photo_guide_asset(self, s, path):
        r = s.get(f"{BASE}{path}", timeout=15)
        assert r.status_code == 200, f"{path} -> {r.status_code}"
        assert len(r.content) > 100, f"{path} too small"


# ---------------------------------------------------------------- 4-traveler application regression
class TestApplicationFourTravelers:
    def _upload_png(self, s):
        png = bytes.fromhex(
            "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C4890000000D49"
            "44415478DA6300010000000500010D0A2DB40000000049454E44AE426082"
        )
        r = s.post(
            f"{BASE}/api/uploads",
            files={"file": ("t.png", png, "image/png")},
            data={"doc_type": "passport"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["file_id"]

    def test_four_travelers_15_percent(self, s):
        vt = s.get(f"{BASE}/api/visa-types", timeout=15).json()
        # pick visa_30_single
        v = next(x for x in vt if x["id"] == "visa_30_single")
        visa_id = v["id"]
        unit = float(v["price"])

        fids = [self._upload_png(s) for _ in range(2)]

        def traveler_tpl(i):
            return {
                "first_name": f"AHMET{i}",
                "last_name": "TEST",
                "birth_date": "1990-05-15",
                "gender": "male",
                "applicant_type": "adult",
                "nationality": "TR",
                "passport_no": f"U1234567{i}",
                "passport_expiry": "2032-12-31",
                "visa_type_id": visa_id,
                "passport_file_id": fids[0],
                "photo_file_id": fids[1],
            }
        payload = {
            "contact": {
                "full_name": "TEST_iter84 Aile",
                "email": "delivered@resend.dev",
                "phone": "+90 532 588 26 30",
                "address_city": "Istanbul",
                "whatsapp_optin": True,
            },
            "travelers": [traveler_tpl(i) for i in range(4)],
            "travel": {
                "arrival_date": "",
                "departure_date": "",
                "dates_unknown": True,
                "travel_window": "1-3ay",
                "purpose": "tourism",
                "birth_country": "TR",
            },
            "addons": {},
            "extra_documents": {},
            "kvkk_accepted": True,
        }
        r = s.post(f"{BASE}/api/applications", json=payload, timeout=60)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("reference_code", "").startswith("DV-")
        pricing = body.get("pricing") or {}
        assert pricing.get("traveler_count") == 4
        assert abs(pricing.get("family_discount_rate", 0) - 0.15) < 1e-6, pricing
        subtotal = pricing.get("subtotal")
        assert abs(subtotal - unit * 4) < 0.01
        expected_discount = round(subtotal * 0.15, 2)
        assert abs(pricing.get("family_discount") - expected_discount) < 0.01, pricing


# ---------------------------------------------------------------- /api/order still exists
class TestOrderEndpointExists:
    def test_orders_endpoint_not_removed(self, s):
        # /api/orders is the store checkout endpoint (customer orders)
        r = s.post(f"{BASE}/api/orders", json={}, timeout=15)
        assert r.status_code != 404, "POST /api/orders 404 - endpoint kaldirilmis!"
