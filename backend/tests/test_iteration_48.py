"""Backend regression tests for iteration 48.

Covers:
- Public visa-types prices (USD + TRY consistency w/ FX rate)
- /content/site addons (express 50 USD)
- /pricing/quote for 2 adults with express
- Admin login (new creds work, old creds rejected)
- Admin company GET/PUT for instagram + google_review + whatsapp persistence
"""
import os
import pytest
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", ".env"))

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
ADMIN_EMAIL = os.environ["ADMIN_LOGIN_EMAIL"]
ADMIN_PASSWORD = os.environ["ADMIN_LOGIN_PASSWORD"]
OLD_ADMIN_EMAIL = "admin@vizeatlas.com"

EXPECTED_USD = {
    "visa_30_single": 105,
    "visa_30_child": 50,
    "visa_30_multi": 200,
    "visa_60_single": 200,
    "visa_60_multi": 300,
    "visa_extension_30": 300,
    "visa_60_child": 105,
    "visa_transit_48": 70,
}


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def fx_rate(api):
    r = api.get(f"{BASE_URL}/api/fx", timeout=15)
    assert r.status_code == 200
    return float(r.json()["effective_rate"])


@pytest.fixture(scope="module")
def admin_session(api):
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    r = s.post(
        f"{BASE_URL}/api/admin/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    token = r.json().get("token")
    assert token, "No token in login response"
    s.headers.update({"Authorization": f"Bearer {token}"})
    return s


# --------------- Visa prices ---------------
class TestVisaPrices:
    def test_visa_types_usd_and_try(self, api, fx_rate):
        r = api.get(f"{BASE_URL}/api/visa-types", timeout=15)
        assert r.status_code == 200
        data = r.json()
        by_id = {v["id"]: v for v in data}
        for vid, usd in EXPECTED_USD.items():
            assert vid in by_id, f"Missing {vid}"
            row = by_id[vid]
            assert float(row["price_usd"]) == float(usd), f"{vid} USD mismatch: {row['price_usd']}"
            expected_try = round(usd * fx_rate / 10.0) * 10.0
            # The backend rounds to nearest 10 TRY
            assert abs(float(row["price"]) - expected_try) <= 10.0, (
                f"{vid} TRY {row['price']} not close to USD*FX {expected_try}"
            )


# --------------- Content / addons ---------------
class TestContent:
    def test_express_addon(self, api):
        r = api.get(f"{BASE_URL}/api/content/site", timeout=15)
        assert r.status_code == 200
        d = r.json()
        addons = d.get("addons", [])
        express = next((a for a in addons if a["id"] == "express"), None)
        assert express is not None
        assert float(express["price_usd"]) == 50.0
        assert "8 mesai" in express.get("description", "") or "8 mesai" in " ".join(
            express.get("features", [])
        )

    def test_company_has_social_links(self, api):
        r = api.get(f"{BASE_URL}/api/content/site", timeout=15)
        assert r.status_code == 200
        company = r.json().get("company", {})
        assert "instagram" in company
        assert "google_review" in company
        assert company.get("instagram", "").startswith("http")
        assert company.get("google_review", "").startswith("http")


# --------------- Pricing quote ---------------
class TestQuote:
    def test_two_adults_30day_single_express(self, api):
        r = api.post(
            f"{BASE_URL}/api/pricing/quote",
            json={
                "visa_type_ids": ["visa_30_single", "visa_30_single"],
                "addons": {"express": True},
            },
            timeout=15,
        )
        assert r.status_code == 200
        q = r.json()
        # visa subtotal
        assert q["traveler_count"] == 2
        assert q["subtotal"] > 0
        # family discount 10%
        assert q["family_discount_rate"] == 0.1
        # express 2 travelers
        express = next((a for a in q["addons"] if a["id"] == "express"), None)
        assert express and express["quantity"] == 2
        # total = subtotal - discount + addons
        expected = round(q["subtotal"] - q["family_discount"] + q["addons_total"], 2)
        assert abs(q["total"] - expected) < 0.5


# --------------- Admin auth ---------------
class TestAdminAuth:
    def test_login_success(self, api):
        r = api.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=15,
        )
        assert r.status_code == 200

    def test_old_admin_email_rejected(self, api):
        r = api.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": OLD_ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=15,
        )
        assert r.status_code == 401

    def test_wrong_password_rejected(self, api):
        r = api.post(
            f"{BASE_URL}/api/admin/login",
            json={"email": ADMIN_EMAIL, "password": "wrong"},
            timeout=15,
        )
        assert r.status_code == 401


# --------------- Admin company (social links persistence) ---------------
class TestAdminCompany:
    def test_get_company(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/company", timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert "instagram" in d
        assert "google_review" in d

    def test_put_company_persists_socials_and_whatsapp(self, admin_session):
        # GET current
        r = admin_session.get(f"{BASE_URL}/api/admin/company", timeout=15)
        assert r.status_code == 200
        current = r.json()
        payload = {
            **{k: current.get(k, "") for k in [
                "brand", "legal_name", "phone", "whatsapp", "email",
                "instagram", "google_review", "address", "working_hours",
                "tursab_no", "tursab_type", "tax_office", "tax_no",
                "mersis_no", "trade_registry_no", "founded_year",
            ]}
        }
        if not payload.get("legal_name"):
            payload["legal_name"] = "Dubai Vize Online Ltd."
        payload["instagram"] = "https://www.instagram.com/dubaivizeonline/"
        payload["google_review"] = "https://www.google.com/search?q=Dubai+Vize+Online+yorumlar"
        payload["whatsapp"] = "905331234567"

        rp = admin_session.put(f"{BASE_URL}/api/admin/company", json=payload, timeout=15)
        assert rp.status_code == 200, rp.text

        # verify via admin GET
        r2 = admin_session.get(f"{BASE_URL}/api/admin/company", timeout=15)
        d2 = r2.json()
        assert d2["instagram"] == payload["instagram"]
        assert d2["google_review"] == payload["google_review"]
        assert d2["whatsapp"] == "905331234567"

        # verify via public content
        pub = requests.get(f"{BASE_URL}/api/content/site", timeout=15).json()
        assert pub["company"]["whatsapp"] == "905331234567"
        assert pub["company"]["instagram"] == payload["instagram"]
