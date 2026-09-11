"""Iteration 123: sigorta gider raporu (saglayiciya odenen tutarlar) + cekim kaydi.

Poliçe bedeli saglayicinin acente cari hesabindan cekildiginde gorev uzerine
`charged_try` + `charged_at` yazilir; panel bu veriden aylik gider tablosunu uretir.
Elle/test kesimlerinde cekim olmadigi icin gider raporuna girmez.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import insurance_payment  # noqa: E402
import insurance_provider  # noqa: E402
import insurance_tasks  # noqa: E402


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestParseTry:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("244,85", 244.85),
            ("1.234,56 TL", 1234.56),
            ("₺296,63", 296.63),
            (367.55, 367.55),
            (None, 0.0),
            ("", 0.0),
            ("abc", 0.0),
        ],
    )
    def test_parses_provider_price_formats(self, value, expected):
        assert insurance_payment.parse_try(value) == expected


class TestRecordCharge:
    """Odeme basarili oldugunda cekilen tutar goreve yazilir."""

    def test_charge_is_written_from_quote_price(self, monkeypatch):
        saved = {}

        class FakeCol:
            async def find_one(self, _query):
                return {"id": "t1", "provider_quote_price": "244,85"}

            async def update_one(self, _query, update):
                saved.update(update["$set"])

        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeCol())
        run(insurance_provider._record_charge("t1"))
        assert saved["charged_try"] == 244.85
        assert isinstance(saved["charged_at"], datetime)

    def test_policy_step_records_charge(self, monkeypatch):
        calls = []

        async def fake_issue(response_id):
            calls.append(("policy", response_id))
            return {"id": "pol-1", "policyNumber": "P-9"}

        async def fake_mark(task_id, step, detail=None):
            return None

        async def fake_record(task_id):
            calls.append(("charge", task_id))

        monkeypatch.setattr(insurance_provider.sigortambudur, "issue_policy", fake_issue)
        monkeypatch.setattr(insurance_provider, "_mark_step", fake_mark)
        monkeypatch.setattr(insurance_provider, "_record_charge", fake_record)

        policy_id = run(insurance_provider._sigortambudur_policy({"id": "t1"}, "resp-1"))
        assert policy_id == "pol-1"
        assert calls == [("policy", "resp-1"), ("charge", "t1")]

    def test_charge_is_not_recorded_when_policy_already_issued(self, monkeypatch):
        calls = []

        async def fake_record(task_id):
            calls.append(task_id)

        async def fake_issue(_response_id):
            raise AssertionError("police zaten kesilmis, tekrar istek gitmemeli")

        monkeypatch.setattr(insurance_provider, "_record_charge", fake_record)
        monkeypatch.setattr(insurance_provider.sigortambudur, "issue_policy", fake_issue)
        task = {"id": "t1", "provider_detail": {"policy": {"policy_id": "pol-9"}}}
        assert run(insurance_provider._sigortambudur_policy(task, "resp-1")) == "pol-9"
        assert calls == []


class TestExpenseReport:
    @pytest.fixture
    def charged_tasks(self, monkeypatch):
        now = datetime.now(timezone.utc)
        docs = [
            {
                "id": "t1",
                "order_reference": "SV-AAA",
                "plan_name": "Seyahat Sağlık Sigortası · 7 Gün",
                "validity_days": 7,
                "quantity": 1,
                "unit_price": 490.0,
                "customer": {"full_name": "TEST Müşteri"},
                "provider_quote_id": "2135835",
                "provider_steps": {"policy_no": "P-1"},
                "charged_try": 244.85,
                "charged_at": now,
            },
            {
                "id": "t2",
                "order_reference": "SV-BBB",
                "plan_name": "Seyahat Sağlık Sigortası · 30 Gün",
                "validity_days": 30,
                "quantity": 2,
                "unit_price": 590.0,
                "charged_try": 296.63,
                "charged_at": now,
            },
            {"id": "t3", "charged_try": 100.0, "charged_at": "gecersiz-tarih"},
        ]

        class FakeCursor:
            def sort(self, *_args):
                return self

            async def to_list(self, _limit):
                return docs

        class FakeCol:
            def find(self, query):
                assert query == {"charged_at": {"$ne": None}}  # sadece cekim yapilanlar
                return FakeCursor()

        monkeypatch.setattr(insurance_tasks, "insurance_tasks_col", FakeCol())
        return docs

    def test_monthly_totals_and_current_month(self, charged_tasks):
        report = run(insurance_tasks.expense_report(months=6))
        month_key = datetime.now(timezone.utc).strftime("%Y-%m")
        current = next(row for row in report["items"] if row["month"] == month_key)
        assert current["count"] == 2
        assert current["charged_try"] == pytest.approx(541.48)
        assert report["totals"]["this_month_try"] == pytest.approx(541.48)
        assert report["totals"]["this_month_count"] == 2
        assert report["currency"] == "TRY"
        assert len(report["items"]) == 6

    def test_recent_rows_carry_panel_fields(self, charged_tasks):
        report = run(insurance_tasks.expense_report(months=3))
        row = report["recent"][0]
        assert row["order_reference"] == "SV-AAA"
        assert row["policy_no"] == "P-1"
        assert row["charged_try"] == 244.85
        assert row["revenue_try"] == 490.0
        assert row["customer_name"] == "TEST Müşteri"

    def test_multi_passenger_revenue_uses_quantity(self, charged_tasks):
        report = run(insurance_tasks.expense_report(months=3))
        row = next(r for r in report["recent"] if r["task_id"] == "t2")
        assert row["revenue_try"] == 1180.0  # 590 x 2

    def test_invalid_charge_date_is_ignored_in_totals(self, charged_tasks):
        report = run(insurance_tasks.expense_report(months=3))
        assert report["totals"]["count"] == 2  # t3 (gecersiz tarih) toplama girmez
