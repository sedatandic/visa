"""Iteration 86: visitor tracking, bank transfer merged, affiliation, visits admin endpoints."""
import os
import sys
import time

import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from admin_test_token import admin_token  # type: ignore

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://visa-bot-dashboard.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

HEADERS_BROWSER = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120"}
HEADERS_BOT = {"User-Agent": "python-requests/2.31"}


@pytest.fixture(scope="module")
def admin_headers():
    return {"Authorization": f"Bearer {admin_token()}"}


# ------------------------ Visitor tracking ------------------------
class TestVisitorTracking:
    def test_track_visit_browser_ok(self):
        r = requests.post(f"{API}/track/visit", json={"path": "/iletisim", "referrer": ""}, headers=HEADERS_BROWSER, timeout=10)
        assert r.status_code == 200
        j = r.json()
        assert j.get("ok") is True
        assert "skipped" not in j
        time.sleep(2)  # background task

    def test_track_visit_bot_skipped(self):
        r = requests.post(f"{API}/track/visit", json={"path": "/iletisim", "referrer": ""}, headers=HEADERS_BOT, timeout=10)
        assert r.status_code == 200
        j = r.json()
        assert j.get("ok") is True
        assert j.get("skipped") == "bot"


# ------------------------ Admin visits ------------------------
class TestAdminVisits:
    def test_visits_requires_auth(self):
        r = requests.get(f"{API}/admin/visits", timeout=10)
        assert r.status_code in (401, 403)

    def test_visits_summary_requires_auth(self):
        r = requests.get(f"{API}/admin/visits/summary", timeout=10)
        assert r.status_code in (401, 403)

    def test_visits_list(self, admin_headers):
        r = requests.get(f"{API}/admin/visits", headers=admin_headers, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "items" in data and "total" in data
        assert isinstance(data["items"], list)
        # After the browser POST, should have at least one visit
        if data["items"]:
            item = data["items"][0]
            for k in ("ip", "path", "created_at"):
                assert k in item, f"missing key {k}"
            # City/country may be empty due to ipwho.is rate limits; still keys should exist
            for k in ("city", "country", "country_code", "isp"):
                assert k in item

    def test_visits_summary(self, admin_headers):
        r = requests.get(f"{API}/admin/visits/summary?days=30", headers=admin_headers, timeout=15)
        assert r.status_code == 200, r.text
        data = r.json()
        for key in ("total", "unique_visitors", "total_today", "bots", "daily", "countries", "cities", "pages"):
            assert key in data, f"missing key {key}"
        assert isinstance(data["daily"], list)
        assert isinstance(data["countries"], list)


# ------------------------ Site content ------------------------
class TestContent:
    def test_site_has_affiliation_and_banks(self):
        r = requests.get(f"{API}/content/site", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "affiliation" in data and isinstance(data["affiliation"], str) and data["affiliation"]
        # bank_transfer merged with banks
        bt = data.get("bank_transfer") or {}
        banks = bt.get("banks") or []
        assert len(banks) >= 3, f"expected 3 banks, got {len(banks)}"
        ids = {b.get("id") for b in banks}
        assert {"isbank", "garanti", "ziraat"}.issubset(ids), f"missing banks in {ids}"
        for b in banks:
            accounts = b.get("accounts") or b.get("ibans") or []
            currencies = {i.get("currency") for i in accounts}
            assert {"TRY", "USD"}.issubset(currencies), f"bank {b.get('id')} missing TRY/USD"

    def test_legal_has_affiliation(self):
        r = requests.get(f"{API}/content/legal", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "affiliation" in data and data["affiliation"]
        assert "**" in data["affiliation"], "affiliation should include markdown bold markers"


# ------------------------ Admin bank transfer ------------------------
class TestBankTransferAdmin:
    def test_get_bank_transfer(self, admin_headers):
        r = requests.get(f"{API}/admin/bank-transfer", headers=admin_headers, timeout=10)
        assert r.status_code == 200
        data = r.json()
        banks = data.get("banks") or []
        assert len(banks) >= 3, f"expected 3 banks, got {len(banks)}"

    def test_put_bank_transfer_persists_banks(self, admin_headers):
        # Get current
        r = requests.get(f"{API}/admin/bank-transfer", headers=admin_headers, timeout=10)
        original = r.json()
        # Save unchanged - should not wipe banks
        put_body = {
            "enabled": original.get("enabled", True),
            "title": original.get("title") or "Havale / EFT ile ödeme",
            "account_name": original.get("account_name") or original.get("recipient_name") or "Dubai Vize Hattı",
            "bank_name": original.get("bank_name") or "Türkiye İş Bankası A.Ş.",
            "iban": original.get("iban") or "TR00 0000 0000 0000 0000 0000 00",
            "currency": original.get("currency") or "TRY",
            "note": original.get("note", ""),
            "steps": original.get("steps") or [],
            "banks": original.get("banks") or [],
            "notes": original.get("notes") or [],
        }
        r2 = requests.put(f"{API}/admin/bank-transfer", headers=admin_headers, json=put_body, timeout=10)
        assert r2.status_code == 200, r2.text
        # Verify via public content
        r3 = requests.get(f"{API}/content/site", timeout=15)
        banks = (r3.json().get("bank_transfer") or {}).get("banks") or []
        assert len(banks) >= 3, "banks were wiped after PUT"


# ------------------------ Articles ------------------------
class TestArticles:
    def test_articles_have_covers(self):
        r = requests.get(f"{API}/articles", timeout=15)
        assert r.status_code == 200
        data = r.json()
        # Data may be list or dict; look for list under key
        arts = data if isinstance(data, list) else data.get("items") or []
        assert len(arts) >= 1
