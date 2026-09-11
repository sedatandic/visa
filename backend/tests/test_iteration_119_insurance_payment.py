"""Iteration 119 (yenilendi 2026-06): Tamamliyo odeme kuyrugu + uyarilari.

Police bedeli varsayilan olarak partner cari bakiyesinden dusuluyor (odemeTipi=3);
bu dosyadaki testler `TAMAMLIYO_PAYMENT_TYPE=2` ile kurumsal kart modunu dogrular
(bkz. test_iteration_130_tamamliyo_balance.py cari bakiye testleri). Kapsam:
- odeme engeli (kart tanimsiz/limit/ret) tespitini,
- yanit alinamayan cekimin (zaman asimi) ayri "inceleme" durumuna dusmesini,
- operator uyarilarini (e-posta + WhatsApp, 12 saat sogutma) dogrular.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import insurance_payment  # noqa: E402
import insurance_provider  # noqa: E402
import tamamliyo  # noqa: E402


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class FakeSettings:
    """settings_col yerine gecen basit sozluk deposu."""

    def __init__(self, value=None):
        self.value = dict(value or {})

    async def find_one(self, _query):
        return {"key": insurance_payment.SETTINGS_KEY, "value": dict(self.value)}

    async def update_one(self, _query, update, upsert=False):
        for path, new in (update.get("$set") or {}).items():
            if path.startswith("value."):
                self.value[path[6:]] = new


@pytest.fixture
def store(monkeypatch):
    settings = FakeSettings()
    monkeypatch.setattr(insurance_payment, "settings_col", settings)
    return settings


@pytest.fixture
def card(monkeypatch):
    monkeypatch.setenv("TAMAMLIYO_PAYMENT_TYPE", "2")
    monkeypatch.setenv("TAMAMLIYO_CARD_NUMBER", "4111111111111111")
    monkeypatch.setenv("TAMAMLIYO_CARD_EXPIRY", "2030-12-01")
    monkeypatch.setenv("TAMAMLIYO_CARD_CVV", "123")
    monkeypatch.setenv("TAMAMLIYO_CARD_NAME", "MORUYA")
    monkeypatch.setenv("TAMAMLIYO_CARD_SURNAME", "TRAVEL")


class TestPaymentErrorDetection:
    def test_card_and_limit_errors_are_payment_blocked(self):
        assert insurance_payment.is_payment_blocked("Kredi kartı reddedildi")
        assert insurance_payment.is_payment_blocked("Kart limiti yetersiz")
        assert insurance_payment.is_payment_blocked("Yetersiz puan bakiyesi.")
        assert insurance_payment.is_payment_blocked(
            "Tamamliyo ödeme kartı tanımlı değil (TAMAMLIYO_CARD_CVV)."
        )

    def test_business_errors_are_not_payment_blocked(self):
        assert not insurance_payment.is_payment_blocked("T.C. Kimlik Numarası hatalı")
        assert not insurance_payment.is_payment_blocked("ulkeKodu zorunludur")
        assert not insurance_payment.is_payment_blocked("")

    def test_unknown_payment_is_detected_separately(self):
        message = f"{tamamliyo.PAYMENT_UNKNOWN_MARKER}: yanit alinamadi"
        assert insurance_payment.is_payment_unknown(message)
        # Belirsiz cekim "engel" sayilmaz: otomatik tekrar denenmemeli
        assert not insurance_payment.is_payment_blocked(message)


class TestStatus:
    def test_reports_card_state(self, store, card):
        state = run(insurance_payment.status())
        assert state["method"] == "card"
        assert state["card_configured"] is True
        assert state["card_hint"] == "**** 1111"

    def test_missing_card_is_reported(self, store, monkeypatch):
        monkeypatch.setenv("TAMAMLIYO_PAYMENT_TYPE", "2")
        monkeypatch.delenv("TAMAMLIYO_CARD_NUMBER", raising=False)
        assert run(insurance_payment.status())["card_configured"] is False


class TestAlerts:
    @pytest.fixture
    def alerts(self, monkeypatch):
        sent = {"email": [], "whatsapp": []}

        async def fake_email(to, subject, html, **kwargs):
            sent["email"].append({"to": to, "subject": subject, "html": html})
            return {"status": "sent"}

        async def fake_wa(text, reason=""):
            sent["whatsapp"].append(text)
            return {"status": "sent"}

        monkeypatch.setattr(insurance_payment, "send_email", fake_email)
        monkeypatch.setattr(insurance_payment.whatsapp, "send_admin_text", fake_wa)
        monkeypatch.setenv("ADMIN_EMAIL", "info@dubaivizehatti.com")
        return sent

    def test_blocked_payment_alerts_email_and_whatsapp(self, store, alerts, card):
        result = run(insurance_payment.maybe_alert("blocked", waiting=2))
        assert result["sent"] is True and result["kind"] == "blocked"
        assert "ödemesi başarısız" in alerts["email"][0]["subject"]
        assert "2 poliçe" in alerts["email"][0]["html"]
        assert "ACİL" in alerts["whatsapp"][0]

    def test_missing_card_reason_is_explicit(self, store, alerts, monkeypatch):
        monkeypatch.setenv("TAMAMLIYO_PAYMENT_TYPE", "2")
        monkeypatch.delenv("TAMAMLIYO_CARD_NUMBER", raising=False)
        run(insurance_payment.maybe_alert("blocked", waiting=1))
        assert "Kart bilgileri tanımlı olmadığı" in alerts["email"][0]["html"]

    def test_review_alert_warns_about_double_charge(self, store, alerts, card):
        result = run(insurance_payment.maybe_alert("review", waiting=1))
        assert result["kind"] == "review"
        assert "doğrulanmalı" in alerts["email"][0]["subject"]
        assert "Mükerrer çekim riski" in alerts["email"][0]["html"]
        assert "otomatik tekrar denenmiyor" in alerts["whatsapp"][0]

    def test_same_alert_is_not_repeated_within_cooldown(self, store, alerts, card):
        run(insurance_payment.maybe_alert("blocked", waiting=1))
        second = run(insurance_payment.maybe_alert("blocked", waiting=1))
        assert second["reason"] == "cooldown"
        assert len(alerts["email"]) == 1

    def test_different_kind_alerts_immediately(self, store, alerts, card):
        run(insurance_payment.maybe_alert("blocked", waiting=1))
        assert run(insurance_payment.maybe_alert("review", waiting=1))["sent"] is True
        assert len(alerts["email"]) == 2

    def test_cooldown_expires(self, store, alerts, card):
        run(insurance_payment.maybe_alert("blocked", waiting=1))
        store.value["last_alert_at"] = datetime.now(timezone.utc) - timedelta(hours=13)
        assert run(insurance_payment.maybe_alert("blocked", waiting=1))["sent"] is True
        assert len(alerts["email"]) == 2


class TestQueue:
    """Odeme sorunu olan gorev kuyruga alinir; belirsiz cekim otomatik denenmez."""

    @pytest.fixture(autouse=True)
    def api_on(self, monkeypatch):
        """Kuyruk denemesi saglayici API'si acikken calisir (varsayilan artik kapali)."""

        async def _on():
            return True

        monkeypatch.setattr(insurance_provider, "api_enabled", _on)

    @pytest.fixture
    def tasks(self, monkeypatch):
        state = {"updates": [], "counts": 3, "alerts": []}

        class FakeCol:
            async def update_one(self, query, update):
                state["updates"].append(update["$set"])

            async def count_documents(self, _query):
                return state["counts"]

        async def fake_alert(kind="blocked", waiting=0):
            state["alerts"].append({"kind": kind, "waiting": waiting})
            return {"sent": True}

        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeCol())
        monkeypatch.setattr(insurance_payment, "maybe_alert", fake_alert)
        return state

    def test_blocked_task_goes_to_waiting_payment(self, tasks):
        run(insurance_provider._park_for_payment("t1", "blocked"))
        assert tasks["updates"][0]["status"] == insurance_provider.WAITING_STATUS
        assert tasks["alerts"] == [{"kind": "blocked", "waiting": 3}]

    def test_unknown_payment_goes_to_review(self, tasks):
        run(insurance_provider._park_for_payment("t1", "review"))
        assert tasks["updates"][0]["status"] == insurance_provider.REVIEW_STATUS
        assert tasks["alerts"][0]["kind"] == "review"

    def test_status_values_are_distinct(self):
        assert insurance_provider.WAITING_STATUS == "waiting_payment"
        assert insurance_provider.REVIEW_STATUS == "payment_review"

    def test_retry_skips_when_card_missing(self, monkeypatch):
        class FakeCursor:
            def sort(self, *_args):
                return self

            async def to_list(self, _limit):
                return [{"id": "t1"}]

        class FakeCol:
            def find(self, _query):
                return FakeCursor()

        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeCol())
        monkeypatch.setattr(tamamliyo, "configured", lambda: True)
        monkeypatch.setattr(tamamliyo, "card_configured", lambda: False)
        result = run(insurance_provider.retry_waiting_tasks())
        assert result == {"issued": 0, "waiting": 1, "reason": "card_not_configured"}

    def test_retry_issues_waiting_tasks(self, monkeypatch):
        issued = []

        class FakeCursor:
            def sort(self, *_args):
                return self

            async def to_list(self, _limit):
                return [{"id": "t1"}, {"id": "t2"}]

        class FakeCol:
            def find(self, _query):
                return FakeCursor()

        async def fake_issue(task_id, origin, actor=""):
            issued.append(task_id)
            return {"ok": True}

        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeCol())
        monkeypatch.setattr(tamamliyo, "configured", lambda: True)
        monkeypatch.setattr(tamamliyo, "card_configured", lambda: True)
        monkeypatch.setattr(insurance_provider, "issue_via_provider", fake_issue)
        result = run(insurance_provider.retry_waiting_tasks())
        assert issued == ["t1", "t2"]
        assert result == {"issued": 2, "waiting": 0}
