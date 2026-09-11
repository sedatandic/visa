"""Iteration 147: teklif linki donusum raporu.

Admin -> Teklif Linkleri ekrani artik "kac teklif gonderildi, kaci acildi, kaci basvuruya
dondu" ozetini gosteriyor (`offer_links.report_summary`) ve liste durum/acilma filtresiyle
daraltilabiliyor (`routes_admin_offers._matches`).
"""

import os
import sys
from datetime import datetime, timedelta, timezone

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import offer_links  # noqa: E402
from routes_admin_offers import _matches  # noqa: E402

NOW = datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc)


def offer(**kwargs) -> dict:
    doc = {
        "token": kwargs.pop("token", "tok"),
        "total": 5000.0,
        "currency": "TRY",
        "active": True,
        "views": 0,
        "application_id": None,
        "created_at": NOW - timedelta(days=1),
        "expires_at": NOW + timedelta(days=5),
    }
    doc.update(kwargs)
    return doc


class TestReportSummary:
    def test_empty_report_is_zeroed(self):
        report = offer_links.report_summary([], now=NOW)
        assert report["total"] == 0
        assert report["open_rate"] == 0
        assert report["conversion_rate"] == 0
        assert report["currency"] == "TRY"
        assert report["avg_open_hours"] is None

    def test_open_and_conversion_rates(self):
        docs = [
            offer(token="a"),  # hic acilmadi
            offer(token="b", views=3, first_viewed_at=NOW - timedelta(hours=22)),
            offer(
                token="c",
                views=2,
                first_viewed_at=NOW - timedelta(hours=20),
                application_id="app-1",
                reference_code="DV-1",
            ),
            offer(token="d", views=1, first_viewed_at=NOW - timedelta(hours=18), application_id="app-2"),
        ]
        report = offer_links.report_summary(docs, now=NOW)
        assert report["total"] == 4
        assert report["opened"] == 3
        assert report["not_opened"] == 1
        assert report["converted"] == 2
        assert report["views"] == 6
        assert report["open_rate"] == 75
        assert report["conversion_rate"] == 50
        assert report["converted_of_opened"] == 67
        assert report["offered_value"] == 20000
        assert report["converted_value"] == 10000
        assert report["avg_open_hours"] == 4.0

    def test_status_breakdown(self):
        docs = [
            offer(token="a"),
            offer(token="b", expires_at=NOW - timedelta(days=1)),
            offer(token="c", active=False),
            offer(token="d", views=1, application_id="app-9"),
        ]
        report = offer_links.report_summary(docs, now=NOW)
        assert report["statuses"] == {"active": 1, "used": 1, "expired": 1, "disabled": 1}

    def test_missing_view_field_counts_as_not_opened(self):
        docs = [offer(token="a", views=None), offer(token="b", total=None)]
        report = offer_links.report_summary(docs, now=NOW)
        assert report["opened"] == 0
        assert report["offered_value"] == 5000


class TestListFilter:
    """`_matches` gercek zamani kullanir; kayitlar bugune gore uretilir."""

    @staticmethod
    def live(**kwargs) -> dict:
        now = datetime.now(timezone.utc)
        return offer(created_at=now - timedelta(hours=2), expires_at=now + timedelta(days=5), **kwargs)

    def test_empty_filter_matches_everything(self):
        assert _matches(self.live(), "") is True

    def test_opened_and_not_opened(self):
        assert _matches(self.live(views=2), "opened") is True
        assert _matches(self.live(views=0), "opened") is False
        assert _matches(self.live(views=0), "not_opened") is True
        assert _matches(self.live(views=1), "not_opened") is False

    def test_status_filters(self):
        assert _matches(self.live(views=1, application_id="app-1"), "used") is True
        assert _matches(self.live(), "used") is False
        assert _matches(self.live(), "active") is True
        assert _matches(self.live(active=False), "disabled") is True
        assert _matches(
            offer(expires_at=datetime.now(timezone.utc) - timedelta(days=1)), "expired"
        ) is True


class TestAdminView:
    def test_opened_flag_is_exposed(self):
        assert offer_links.admin_view(offer(views=0))["opened"] is False
        assert offer_links.admin_view(offer(views=4))["opened"] is True
