"""Iteration 119 (yenilendi 2026-06-18): police odeme kuyrugu + operator uyarilari.

Tamamliyo entegrasyonu kaldirildi; odeme artik saglayicinin acente cari hesabindan
(Sigortambudur `agency_credit`) dusuluyor. Kapsam:
- odeme engeli (bakiye/limit/ret) tespiti,
- yanit alinamayan cekimin (zaman asimi) ayri "inceleme" durumuna dusmesi,
- operator uyarilari (e-posta + WhatsApp, 12 saat sogutma),
- kuyrugun tekrar denenmesi.
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
import sigortambudur  # noqa: E402


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


class TestPaymentErrorDetection:
    def test_balance_and_limit_errors_are_payment_blocked(self):
        assert insurance_payment.is_payment_blocked("Cari bakiye yetersiz")
        assert insurance_payment.is_payment_blocked("Kart limiti yetersiz")
        assert insurance_payment.is_payment_blocked("Acente bakiyesi tanımlı değil.")

    def test_business_errors_are_not_payment_blocked(self):
        assert not insurance_payment.is_payment_blocked("T.C. Kimlik Numarası hatalı")
        assert not insurance_payment.is_payment_blocked("Yaş sınırı aşıldı")
        assert not insurance_payment.is_payment_blocked("")

    def test_unknown_payment_is_detected_separately(self):
        # Saglayici istemcisi zaman asiminda bu ifadeyi kullaniyor
        message = "Sigortambudur yanıtı alınamadı, işlem gerçekleşmiş olabilir (timeout)."
        assert insurance_payment.is_payment_unknown(message)
        # Belirsiz cekim "engel" sayilmaz: otomatik tekrar denenmemeli
        assert not insurance_payment.is_payment_blocked(message)


class TestStatus:
    def test_reports_payment_method(self, store, monkeypatch):
        monkeypatch.setenv("SIGORTAMBUDUR_CLIENT_ID", "cid")
        monkeypatch.setenv("SIGORTAMBUDUR_CLIENT_SECRET", "secret")
        state = run(insurance_payment.status())
        assert state["method"] == "agency_credit"
        assert state["provider_configured"] is True

    def test_missing_credentials_are_reported(self, store, monkeypatch):
        monkeypatch.setenv("SIGORTAMBUDUR_CLIENT_SECRET", "")
        assert run(insurance_payment.status())["provider_configured"] is False


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

    def test_blocked_payment_alerts_email_and_whatsapp(self, store, alerts):
        result = run(insurance_payment.maybe_alert("blocked", waiting=2))
        assert result["sent"] is True and result["kind"] == "blocked"
        assert "ödemesi başarısız" in alerts["email"][0]["subject"]
        assert "2 poliçe" in alerts["email"][0]["html"]
        assert "cari bakiye" in alerts["email"][0]["html"].lower()
        assert "ACİL" in alerts["whatsapp"][0]

    def test_review_alert_warns_about_double_charge(self, store, alerts):
        result = run(insurance_payment.maybe_alert("review", waiting=1))
        assert result["kind"] == "review"
        assert "doğrulanmalı" in alerts["email"][0]["subject"]
        assert "Mükerrer çekim riski" in alerts["email"][0]["html"]
        assert "otomatik tekrar denenmiyor" in alerts["whatsapp"][0]

    def test_same_alert_is_not_repeated_within_cooldown(self, store, alerts):
        run(insurance_payment.maybe_alert("blocked", waiting=1))
        second = run(insurance_payment.maybe_alert("blocked", waiting=1))
        assert second["reason"] == "cooldown"
        assert len(alerts["email"]) == 1

    def test_different_kind_alerts_immediately(self, store, alerts):
        run(insurance_payment.maybe_alert("blocked", waiting=1))
        assert run(insurance_payment.maybe_alert("review", waiting=1))["sent"] is True
        assert len(alerts["email"]) == 2

    def test_cooldown_expires(self, store, alerts):
        run(insurance_payment.maybe_alert("blocked", waiting=1))
        store.value["last_alert_at"] = datetime.now(timezone.utc) - timedelta(hours=13)
        assert run(insurance_payment.maybe_alert("blocked", waiting=1))["sent"] is True
        assert len(alerts["email"]) == 2


class TestQueue:
    """Odeme sorunu olan gorev kuyruga alinir; belirsiz cekim otomatik denenmez."""

    @pytest.fixture(autouse=True)
    def api_on(self, monkeypatch):
        """Kuyruk denemesi saglayici API'si acikken calisir."""

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
        monkeypatch.setattr(insurance_provider, "issue_via_provider", fake_issue)
        result = run(insurance_provider.retry_waiting_tasks())
        assert issued == ["t1", "t2"]
        assert result == {"issued": 2, "waiting": 0}

    def test_retry_stops_when_payment_still_fails(self, monkeypatch):
        class FakeCursor:
            def sort(self, *_args):
                return self

            async def to_list(self, _limit):
                return [{"id": "t1"}, {"id": "t2"}]

        class FakeCol:
            def find(self, _query):
                return FakeCursor()

        async def fake_issue(task_id, origin, actor=""):
            return {"ok": False, "error": "Cari bakiye yetersiz"}

        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeCol())
        monkeypatch.setattr(insurance_provider, "issue_via_provider", fake_issue)
        assert run(insurance_provider.retry_waiting_tasks()) == {"issued": 0, "waiting": 2}

    def test_retry_skipped_when_api_off(self, monkeypatch):
        class FakeCursor:
            def sort(self, *_args):
                return self

            async def to_list(self, _limit):
                return [{"id": "t1"}]

        class FakeCol:
            def find(self, _query):
                return FakeCursor()

        async def _off():
            return False

        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeCol())
        monkeypatch.setattr(insurance_provider, "api_enabled", _off)
        assert run(insurance_provider.retry_waiting_tasks()) == {"issued": 0, "waiting": 1}


class TestNoTamamliyoLeftovers:
    """Tamamliyo entegrasyonu tamamen kaldirildi (2026-06-18 kullanici istegi)."""

    def test_module_is_gone(self):
        with pytest.raises(ModuleNotFoundError):
            __import__("tamamliyo")

    def test_provider_options_only_sigortambudur_and_manual(self):
        assert set(insurance_provider.PROVIDER_LABELS) == {"sigortambudur", "manual"}

    def test_provider_module_has_no_price_sync(self):
        for name in ("sync_prices", "probe_product", "price_sync_loop", "fetch_cost"):
            assert not hasattr(insurance_provider, name), name

    def test_payment_marker_matches_provider_timeout_message(self):
        message = str(
            sigortambudur.SigortambudurError(
                "Sigortambudur yanıtı alınamadı, işlem gerçekleşmiş olabilir (x)."
            )
        )
        assert insurance_payment.is_payment_unknown(message)
