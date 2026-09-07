"""Panel karsilama karti verisi: GET /api/admin/today (iteration 113)."""
import os
import sys
from datetime import date, datetime, timedelta

import pytest
import requests

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from admin_test_token import admin_token  # noqa: E402
from daily_digest import TZ, _greeting, day_bounds, day_label  # noqa: E402

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"


class TestHelpers:
    def test_greeting_windows(self) -> None:
        assert _greeting(8) == "Günaydın"
        assert _greeting(13) == "İyi günler"
        assert _greeting(21) == "İyi akşamlar"

    def test_day_label_is_turkish(self) -> None:
        assert day_label(date(2026, 9, 7)) == "7 Eylül 2026, Pazartesi"

    def test_day_bounds_cover_local_day(self) -> None:
        start, end = day_bounds(date(2026, 9, 7))
        assert (end - start) == timedelta(days=1)
        assert start.astimezone(TZ).hour == 0


@pytest.mark.skipif(not BASE_URL, reason="REACT_APP_BACKEND_URL yok")
class TestTodayEndpoint:
    def test_requires_admin_token(self) -> None:
        assert requests.get(f"{API}/admin/today", timeout=30).status_code == 401

    def test_returns_day_summary_and_pending_work(self) -> None:
        res = requests.get(
            f"{API}/admin/today",
            headers={"Authorization": f"Bearer {admin_token()}"},
            timeout=30,
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["day"] == datetime.now(TZ).date().isoformat()
        assert data["day_label"] == day_label(datetime.now(TZ).date())
        assert data["greeting"] in {"Günaydın", "İyi günler", "İyi akşamlar"}
        for key in ("applications_today", "travelers_today", "orders_today", "pending_total"):
            assert isinstance(data[key], int) and data[key] >= 0
        assert set(data["revenue_today"]) >= {"total", "count", "by_method"}
        attention = data["attention"]
        for key in ("missing_documents", "awaiting_transfer", "abandoned_carts", "policy_tasks"):
            assert isinstance(attention[key]["count"], int)
        assert isinstance(data["upcoming_departures"]["count"], int)
        assert data["pending_total"] == (
            attention["missing_documents"]["count"]
            + attention["awaiting_transfer"]["count"]
            + attention["abandoned_carts"]["count"]
            + attention["policy_tasks"]["count"]
        )
