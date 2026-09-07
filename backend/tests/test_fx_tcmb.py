"""TCMB gunluk kur bulteni (USD doviz satis) birincil kaynak testleri."""
import os
from datetime import datetime, timedelta, timezone

import pytest
import requests

import fx

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Tarih_Date Tarih="07.09.2026" Date="09/07/2026"  Bulten_No="2026/167" >
\t<Currency CrossOrder="0" Kod="USD" CurrencyCode="USD">
\t\t\t<Unit>1</Unit>
\t\t\t<Isim>ABD DOLARI</Isim>
\t\t\t<ForexBuying>48.3465</ForexBuying>
\t\t\t<ForexSelling>48.4336</ForexSelling>
\t\t\t<BanknoteBuying>48.3127</BanknoteBuying>
\t\t\t<BanknoteSelling>48.5063</BanknoteSelling>
\t</Currency>
\t<Currency CrossOrder="9" Kod="EUR" CurrencyCode="EUR">
\t\t\t<ForexSelling>56.7412</ForexSelling>
\t</Currency>
</Tarih_Date>
"""


class TestTcmbParsing:
    def test_forex_selling_is_used(self) -> None:
        assert fx.parse_tcmb_xml(SAMPLE_XML) == 48.4336

    def test_bulletin_date(self) -> None:
        assert fx.parse_tcmb_date(SAMPLE_XML) == "2026-09-07"

    def test_broken_payload(self) -> None:
        assert fx.parse_tcmb_xml("<html>bakim</html>") is None
        assert fx.parse_tcmb_date("<html>bakim</html>") is None

    def test_tcmb_is_primary_source(self) -> None:
        assert fx.SOURCES[0] == (fx.TCMB_LABEL, fx.TCMB_URL)


class TestBulletinSchedule:
    def test_before_publish_uses_previous_business_day(self) -> None:
        monday_morning = datetime(2026, 9, 7, 9, 0, tzinfo=fx.IST)
        assert fx.expected_bulletin_date(monday_morning).isoformat() == "2026-09-04"

    def test_after_publish_uses_today(self) -> None:
        monday_evening = datetime(2026, 9, 7, 17, 0, tzinfo=fx.IST)
        assert fx.expected_bulletin_date(monday_evening).isoformat() == "2026-09-07"

    def test_weekend_falls_back_to_friday(self) -> None:
        sunday = datetime(2026, 9, 6, 20, 0, tzinfo=fx.IST)
        assert fx.expected_bulletin_date(sunday).isoformat() == "2026-09-04"


class TestStaleness:
    def test_fresh_bulletin_is_not_stale(self) -> None:
        state = {
            "fetched_at": datetime.now(timezone.utc),
            "bulletin_date": fx.expected_bulletin_date().isoformat(),
        }
        assert fx._is_stale(state) is False

    def test_old_bulletin_refreshes_after_an_hour(self) -> None:
        state = {
            "fetched_at": datetime.now(timezone.utc) - timedelta(hours=2),
            "bulletin_date": "2020-01-02",
        }
        assert fx._is_stale(state) is True

    def test_missing_timestamp_is_stale(self) -> None:
        assert fx._is_stale({}) is True


@pytest.mark.skipif(not BASE_URL, reason="REACT_APP_BACKEND_URL yok")
class TestPublicFxEndpoint:
    def test_fx_endpoint_reports_tcmb(self) -> None:
        res = requests.get(f"{API}/fx", timeout=30)
        assert res.status_code == 200
        data = res.json()
        assert data["currency_pair"] == "USD/TRY"
        assert data["effective_rate"] > 5
        assert "TCMB" in data["source"]
        assert len(data["bulletin_date"]) == 10
