"""Iteration 124: kar korumasi (maliyet > satis -> fiyati otomatik yukselt + uyari).

- `guard_products()`: zarar eden urunun satis fiyatini maliyet x marj yapar, ince marjda
  (%20 alti) yalnizca uyarir.
- `check_charge()`: police kesiminde karttan cekilen tutar musteriden alinan tutari
  asarsa fiyati duzeltir ve uyari gonderir (soguma yok, her zarar bildirilir).
- `probe_product()`: bir Tamamliyo urun kodu (orn. 220) satista mi?
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import insurance_margin  # noqa: E402
import insurance_provider  # noqa: E402
import tamamliyo  # noqa: E402


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class FakeCursor:
    def __init__(self, docs):
        self.docs = docs

    def sort(self, *_args):
        return self

    async def to_list(self, _limit):
        return list(self.docs)


class FakeProducts:
    def __init__(self, docs):
        self.docs = docs
        self.updates = []

    def find(self, _query, _fields=None):
        return FakeCursor(self.docs)

    async def find_one(self, query, _fields=None):
        return next((d for d in self.docs if d["id"] == query.get("id")), None)

    async def update_one(self, query, update):
        self.updates.append((query, update["$set"]))
        for doc in self.docs:
            if doc["id"] == query.get("id"):
                doc.update(update["$set"])


class FakeSettings:
    def __init__(self, value=None):
        self.value = dict(value or {})

    async def find_one(self, _query):
        return {"key": insurance_margin.SETTINGS_KEY, "value": self.value}

    async def update_one(self, _query, update, upsert=False):
        for key, val in update["$set"].items():
            if key.startswith("value."):
                self.value[key[6:]] = val


class FakeNotifications:
    def __init__(self):
        self.docs = []

    async def insert_one(self, doc):
        self.docs.append(doc)


@pytest.fixture
def margin_env(monkeypatch):
    """products/settings/notifications sahte, e-posta ve WhatsApp yakalanir."""
    sent = {"email": [], "whatsapp": []}

    async def fake_email(to, subject, html, kind="", meta=None):
        sent["email"].append({"to": to, "subject": subject, "html": html, "kind": kind})
        return {"status": "sent"}

    async def fake_wa(text, reason=""):
        sent["whatsapp"].append({"text": text, "reason": reason})
        return {"status": "sent"}

    notifications = FakeNotifications()
    settings = FakeSettings()
    monkeypatch.setattr(insurance_margin, "send_email", fake_email)
    monkeypatch.setattr(insurance_margin.whatsapp, "send_admin_text", fake_wa)
    monkeypatch.setattr(insurance_margin, "notifications_col", notifications)
    monkeypatch.setattr(insurance_margin, "settings_col", settings)
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")
    return {"sent": sent, "settings": settings, "notifications": notifications}


class TestSalePriceAndRows:
    @pytest.mark.parametrize(
        ("cost", "expected"),
        [(244.85, 490.0), (196.44, 390.0), (367.55, 740.0), (0, 0.0)],
    )
    def test_sale_price_applies_markup_and_rounding(self, cost, expected):
        assert insurance_margin.sale_price(cost) == expected

    def test_row_states(self):
        assert insurance_margin._row({"cost_try": 200, "price_try": 400})["state"] == "ok"
        assert insurance_margin._row({"cost_try": 200, "price_try": 220})["state"] == "low"
        assert insurance_margin._row({"cost_try": 400, "price_try": 400})["state"] == "loss"
        assert insurance_margin._row({"cost_try": 500, "price_try": 400})["state"] == "loss"
        assert insurance_margin._row({"cost_try": 0, "price_try": 400})["state"] == "unknown"

    def test_row_reports_margin_and_suggestion(self):
        row = insurance_margin._row({"id": "ins_7d", "cost_try": 244.85, "price_try": 240})
        assert row["margin_pct"] == pytest.approx(-2.0, abs=0.2)
        assert row["profit_try"] == -4.85
        assert row["suggested_price_try"] == 490.0


class TestGuardProducts:
    def test_losing_product_price_is_raised_and_alerted(self, monkeypatch, margin_env):
        products = FakeProducts(
            [{"id": "ins_7d", "name": "7 Gün", "cost_try": 500.0, "price_try": 490.0}]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)

        result = run(insurance_margin.guard_products("sync"))

        assert [row["new_price_try"] for row in result["fixed"]] == [1000.0]
        assert products.updates[0][1]["price_try"] == 1000.0
        assert products.updates[0][1]["price_guard_reason"] == "sync"
        assert result["alert"]["sent"] is True
        assert "otomatik" in margin_env["sent"]["email"][0]["subject"].lower()
        assert margin_env["sent"]["whatsapp"][0]["text"].startswith("Kâr uyarısı")
        assert margin_env["notifications"].docs[0]["kind"] == "insurance_margin_alert"
        assert margin_env["settings"].value["events"][0]["kind"] == "price_fixed"

    def test_low_margin_only_warns_without_price_change(self, monkeypatch, margin_env):
        products = FakeProducts(
            [{"id": "ins_15d", "name": "15 Gün", "cost_try": 400.0, "price_try": 440.0}]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)

        result = run(insurance_margin.guard_products("manual"))

        assert result["fixed"] == []
        assert [row["id"] for row in result["low_margin"]] == ["ins_15d"]
        assert products.updates == []
        assert margin_env["settings"].value["events"][0]["kind"] == "low_margin"
        assert result["alert"]["sent"] is True

    def test_profitable_products_do_not_alert(self, monkeypatch, margin_env):
        products = FakeProducts(
            [{"id": "ins_30d", "name": "30 Gün", "cost_try": 250.0, "price_try": 500.0}]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)

        result = run(insurance_margin.guard_products())

        assert result["fixed"] == [] and result["low_margin"] == []
        assert result["alert"]["sent"] is False
        assert margin_env["sent"]["email"] == []
        assert margin_env["settings"].value["last_check_at"]

    def test_alert_respects_cooldown_for_products(self, monkeypatch, margin_env):
        products = FakeProducts(
            [{"id": "ins_7d", "name": "7 Gün", "cost_try": 500.0, "price_try": 490.0}]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)
        margin_env["settings"].value.update(
            {"last_alert_kind": "product", "last_alert_at": datetime.now(timezone.utc)}
        )

        result = run(insurance_margin.guard_products())

        assert result["alert"] == {"sent": False, "reason": "cooldown", "kind": "product"}
        assert margin_env["sent"]["email"] == []
        # fiyat duzeltmesi soguma olsa da yapilir
        assert products.updates[0][1]["price_try"] == 1000.0

    def test_alert_sent_again_after_cooldown(self, monkeypatch, margin_env):
        products = FakeProducts(
            [{"id": "ins_7d", "name": "7 Gün", "cost_try": 500.0, "price_try": 490.0}]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)
        margin_env["settings"].value.update(
            {
                "last_alert_kind": "product",
                "last_alert_at": datetime.now(timezone.utc) - timedelta(hours=7),
            }
        )

        assert run(insurance_margin.guard_products())["alert"]["sent"] is True


class TestChargeLoss:
    def _task(self, **over):
        task = {
            "id": "t1",
            "product_id": "ins_7d",
            "plan_name": "Seyahat Sağlık · 7 Gün",
            "order_reference": "DV-1001",
            "quantity": 1,
            "unit_price": 490.0,
            "charged_try": 520.0,
        }
        task.update(over)
        return task

    def test_charge_above_revenue_raises_price_and_alerts(self, monkeypatch, margin_env):
        products = FakeProducts(
            [{"id": "ins_7d", "name": "7 Gün", "cost_try": 244.85, "price_try": 490.0}]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)

        result = run(insurance_margin.check_charge(self._task()))

        assert result["loss"] is True
        assert result["loss_try"] == 30.0
        assert result["cost_try"] == 520.0
        assert result["new_price_try"] == 1040.0
        assert products.updates[0][1]["price_try"] == 1040.0
        assert result["alert"]["sent"] is True
        assert "ZARAR" in margin_env["sent"]["email"][0]["subject"]
        assert margin_env["settings"].value["events"][0]["kind"] == "charge_loss"

    def test_charge_loss_alert_ignores_cooldown(self, monkeypatch, margin_env):
        products = FakeProducts(
            [{"id": "ins_7d", "name": "7 Gün", "cost_try": 244.85, "price_try": 490.0}]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)
        margin_env["settings"].value.update(
            {"last_alert_kind": "charge", "last_alert_at": datetime.now(timezone.utc)}
        )

        assert run(insurance_margin.check_charge(self._task()))["alert"]["sent"] is True

    def test_multi_person_charge_uses_unit_cost(self, monkeypatch, margin_env):
        products = FakeProducts(
            [{"id": "ins_7d", "name": "7 Gün", "cost_try": 244.85, "price_try": 490.0}]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)

        result = run(
            insurance_margin.check_charge(self._task(quantity=2, charged_try=1000.0))
        )

        assert result["loss"] is True  # 1000 > 2 x 490
        assert result["cost_try"] == 500.0  # kisi basi maliyet
        assert result["new_price_try"] == 1000.0

    def test_profitable_charge_does_not_alert(self, monkeypatch, margin_env):
        products = FakeProducts(
            [{"id": "ins_7d", "name": "7 Gün", "cost_try": 244.85, "price_try": 490.0}]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)

        result = run(insurance_margin.check_charge(self._task(charged_try=244.85)))

        assert result == {"loss": False, "charged_try": 244.85, "revenue_try": 490.0}
        assert products.updates == []
        assert margin_env["sent"]["email"] == []

    def test_missing_charge_or_revenue_is_ignored(self, monkeypatch, margin_env):
        monkeypatch.setattr(insurance_margin, "products_col", FakeProducts([]))
        assert run(insurance_margin.check_charge(self._task(charged_try=0)))["loss"] is False
        assert run(insurance_margin.check_charge(self._task(unit_price=0)))["loss"] is False
        assert margin_env["sent"]["email"] == []

    def test_price_not_lowered_when_already_above_new_cost(self, monkeypatch, margin_env):
        products = FakeProducts(
            [{"id": "ins_7d", "name": "7 Gün", "cost_try": 244.85, "price_try": 2000.0}]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)

        result = run(insurance_margin.check_charge(self._task(unit_price=490.0, charged_try=520.0)))

        assert result["new_price_try"] == 2000.0
        assert products.updates == []


class TestRecordChargeIntegration:
    def test_record_charge_triggers_margin_check(self, monkeypatch):
        checked = {}

        class FakeTasks:
            async def find_one(self, _query):
                return {"id": "t1", "provider_quote_price": "520,00", "unit_price": 490.0}

            async def update_one(self, _query, _update):
                return None

        async def fake_check(task):
            checked.update(task)
            return {"loss": True}

        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeTasks())
        monkeypatch.setattr(insurance_provider.insurance_margin, "check_charge", fake_check)
        run(insurance_provider._record_charge("t1"))
        assert checked["charged_try"] == 520.0

    def test_margin_alert_failure_does_not_break_issue(self, monkeypatch):
        class FakeTasks:
            async def find_one(self, _query):
                return {"id": "t1", "provider_quote_price": "520,00"}

            async def update_one(self, _query, _update):
                return None

        async def boom(_task):
            raise RuntimeError("smtp down")

        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeTasks())
        monkeypatch.setattr(insurance_provider.insurance_margin, "check_charge", boom)
        run(insurance_provider._record_charge("t1"))  # hata yutulur


class TestStatus:
    def test_status_lists_products_and_risk_count(self, monkeypatch, margin_env):
        products = FakeProducts(
            [
                {"id": "ins_7d", "name": "7 Gün", "cost_try": 244.85, "price_try": 490.0},
                {"id": "ins_15d", "name": "15 Gün", "cost_try": 400.0, "price_try": 400.0},
            ]
        )
        monkeypatch.setattr(insurance_margin, "products_col", products)

        state = run(insurance_margin.status())

        assert state["risk_count"] == 1
        assert state["low_margin_pct"] == insurance_margin.LOW_MARGIN_PCT
        assert [row["state"] for row in state["items"]] == ["ok", "loss"]


class TestProbeProduct:
    @pytest.fixture(autouse=True)
    def api_on(self, monkeypatch):
        """Fiyat senkronu kapaliyken probe erken doner; test icin acik varsayilir."""

        async def _on():
            return True

        monkeypatch.setattr(insurance_provider, "api_enabled", _on)
        monkeypatch.setattr(insurance_provider, "price_sync_enabled", _on)

    def test_available_product_returns_cost_and_price(self, monkeypatch):
        async def fake_price(_count, _start, _end, urun_id):
            assert urun_id == 220
            return {"data": {"urunBilgileri": {"fiyatFloat": 244.85, "urunAdi": "Seyahat"}}}

        monkeypatch.setattr(tamamliyo, "price", fake_price)
        result = run(insurance_provider.probe_product(220))
        assert result["available"] is True
        assert result["cost_try"] == 244.85
        assert result["price_try"] == 490.0

    def test_provider_error_is_reported(self, monkeypatch):
        async def fake_price(*_args, **_kwargs):
            raise tamamliyo.TamamliyoError("Fiyat bulunamadı. 758")

        monkeypatch.setattr(tamamliyo, "price", fake_price)
        result = run(insurance_provider.probe_product(220))
        assert result["available"] is False
        assert "758" in result["error"]
        assert result["active_urun_id"] == tamamliyo.URUN_ID

    def test_empty_price_marks_unavailable(self, monkeypatch):
        async def fake_price(*_args, **_kwargs):
            return {"data": {"urunBilgileri": {}}}

        monkeypatch.setattr(tamamliyo, "price", fake_price)
        result = run(insurance_provider.probe_product(220))
        assert result["available"] is False
        assert result["price_try"] is None
