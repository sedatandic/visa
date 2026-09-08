"""Iteration 119: Tamamliyo cari bakiye takibi + bakiye bekleyen police kuyrugu.

Tamamliyo bakiye sorgu API'si sunmuyor; bakiye yalnizca odeme aninda
`HATA_15 "Yetersiz puan bakiyesi"` ile anlasiliyor. Bu yuzden:
- bakiye panelden girilir, kesilen policelerin maliyeti dusulur,
- kritik seviyede admine e-posta + WhatsApp uyarisi gider,
- bakiye yetmeyen gorev `waiting_balance` kuyruguna alinir ve bakiye gelince
  kendiliginden kesilir.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import insurance_balance  # noqa: E402
import insurance_provider  # noqa: E402


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class FakeSettings:
    """settings_col yerine gecen basit sozluk deposu ($set/$inc/$push destekler)."""

    def __init__(self, value=None):
        self.value = dict(value or {})

    async def find_one(self, _query):
        return {"key": insurance_balance.SETTINGS_KEY, "value": dict(self.value)}

    async def update_one(self, _query, update, upsert=False):
        for path, new in (update.get("$set") or {}).items():
            if path.startswith("value."):
                self.value[path[6:]] = new
        for path, delta in (update.get("$inc") or {}).items():
            key = path[6:]
            self.value[key] = float(self.value.get(key) or 0) + delta
        for path, spec in (update.get("$push") or {}).items():
            key = path[6:]
            items = list(self.value.get(key) or [])
            items.extend(spec["$each"])
            self.value[key] = items[spec["$slice"] :] if spec.get("$slice") else items


class FakeProducts:
    def __init__(self, costs):
        self.costs = costs

    def find(self, _query, _projection=None):
        async def gen():
            for cost in self.costs:
                yield {"cost_try": cost}

        return gen()


@pytest.fixture
def store(monkeypatch):
    settings = FakeSettings()
    monkeypatch.setattr(insurance_balance, "settings_col", settings)
    monkeypatch.setattr(insurance_balance, "products_col", FakeProducts([244.85, 296.63, 279.74]))
    return settings


class TestParseTry:
    def test_turkish_format(self):
        assert insurance_balance.parse_try("244,85") == 244.85
        assert insurance_balance.parse_try("1.244,85") == 1244.85

    def test_numbers_pass_through(self):
        assert insurance_balance.parse_try(244.85) == 244.85
        assert insurance_balance.parse_try(1000) == 1000.0

    def test_plain_dot_decimal(self):
        assert insurance_balance.parse_try("244.85") == 244.85

    def test_garbage_is_zero(self):
        assert insurance_balance.parse_try("") == 0.0
        assert insurance_balance.parse_try(None) == 0.0
        assert insurance_balance.parse_try("abc") == 0.0


class TestBalanceError:
    def test_detects_provider_balance_message(self):
        assert insurance_balance.is_balance_error("Yetersiz puan bakiyesi.")
        assert insurance_balance.is_balance_error("YETERSIZ BAKIYE")

    def test_other_errors_are_not_balance(self):
        assert not insurance_balance.is_balance_error("T.C. Kimlik Numarası hatalı")
        assert not insurance_balance.is_balance_error("")


class TestBalanceStatus:
    def test_empty_when_nothing_loaded(self, store):
        state = run(insurance_balance.status())
        assert state["remaining_try"] == 0
        assert state["policies_left"] == 0
        assert state["tracked"] is False
        assert state["empty"] is True

    def test_topup_sets_remaining_and_policy_count(self, store):
        state = run(insurance_balance.add_topup(1000, "admin@x.com"))
        assert state["loaded_try"] == 1000
        assert state["remaining_try"] == 1000
        # en pahali police 296,63 TL -> 1000 / 296,63 = 3 police
        assert state["unit_cost_try"] == 296.63
        assert state["policies_left"] == 3
        assert state["tracked"] is True
        assert state["empty"] is False

    def test_spend_reduces_remaining(self, store):
        run(insurance_balance.add_topup(1000))
        run(insurance_balance.record_spend("244,85"))
        state = run(insurance_balance.status())
        assert state["spent_try"] == 244.85
        assert state["remaining_try"] == 755.15
        assert state["policies_left"] == 2

    def test_spend_never_makes_remaining_negative(self, store):
        run(insurance_balance.add_topup(100))
        run(insurance_balance.record_spend(500))
        assert run(insurance_balance.status())["remaining_try"] == 0

    def test_zero_spend_is_ignored(self, store):
        run(insurance_balance.add_topup(1000))
        run(insurance_balance.record_spend(0))
        run(insurance_balance.record_spend("abc"))
        assert run(insurance_balance.status())["spent_try"] == 0

    def test_mark_empty_zeroes_remaining(self, store):
        run(insurance_balance.add_topup(1000))
        run(insurance_balance.mark_empty())
        state = run(insurance_balance.status())
        assert state["remaining_try"] == 0
        assert state["empty"] is True

    def test_low_flag_at_threshold(self, store):
        run(insurance_balance.add_topup(900))  # 3 police -> esik 3
        assert run(insurance_balance.status())["low"] is True
        run(insurance_balance.add_topup(600))  # 5 police
        assert run(insurance_balance.status())["low"] is False

    def test_topup_history_is_recorded_newest_first(self, store):
        run(insurance_balance.add_topup(500, "a@x.com"))
        run(insurance_balance.add_topup(300, "b@x.com"))
        topups = run(insurance_balance.status())["topups"]
        assert [t["amount_try"] for t in topups] == [300, 500]
        assert topups[0]["by"] == "b@x.com"


class TestBalanceAlert:
    @pytest.fixture
    def alerts(self, monkeypatch):
        sent = {"email": [], "whatsapp": []}

        async def fake_email(to, subject, html, **kwargs):
            sent["email"].append({"to": to, "subject": subject, "html": html})
            return {"status": "sent"}

        async def fake_wa(text, reason=""):
            sent["whatsapp"].append(text)
            return {"status": "sent"}

        monkeypatch.setattr(insurance_balance, "send_email", fake_email)
        monkeypatch.setattr(insurance_balance.whatsapp, "send_admin_text", fake_wa)
        monkeypatch.setenv("ADMIN_EMAIL", "info@dubaivizehatti.com")
        return sent

    def test_no_alert_when_balance_is_healthy(self, store, alerts):
        run(insurance_balance.add_topup(5000))
        result = run(insurance_balance.maybe_alert())
        assert result == {"sent": False, "reason": "ok"}
        assert alerts["email"] == [] and alerts["whatsapp"] == []

    def test_empty_balance_alerts_email_and_whatsapp(self, store, alerts):
        run(insurance_balance.add_topup(1000))
        run(insurance_balance.mark_empty())
        result = run(insurance_balance.maybe_alert(waiting=2))
        assert result["sent"] is True and result["kind"] == "empty"
        assert "bitti" in alerts["email"][0]["subject"].lower()
        assert "2 poliçe" in alerts["email"][0]["html"]
        assert len(alerts["whatsapp"]) == 1
        assert "ACİL" in alerts["whatsapp"][0]

    def test_low_balance_alerts_with_policy_count(self, store, alerts):
        run(insurance_balance.add_topup(600))  # 2 police -> low
        result = run(insurance_balance.maybe_alert())
        assert result["kind"] == "low"
        assert "azaldı" in alerts["email"][0]["subject"]
        assert "2 poliçe" in alerts["whatsapp"][0]

    def test_same_alert_is_not_repeated_within_cooldown(self, store, alerts):
        run(insurance_balance.add_topup(600))
        run(insurance_balance.maybe_alert())
        second = run(insurance_balance.maybe_alert())
        assert second["reason"] == "cooldown"
        assert len(alerts["email"]) == 1

    def test_cooldown_expires(self, store, alerts):
        run(insurance_balance.add_topup(600))
        run(insurance_balance.maybe_alert())
        store.value["last_alert_at"] = datetime.now(timezone.utc) - timedelta(hours=13)
        assert run(insurance_balance.maybe_alert())["sent"] is True
        assert len(alerts["email"]) == 2

    def test_low_alert_escalates_to_empty_immediately(self, store, alerts):
        run(insurance_balance.add_topup(600))
        run(insurance_balance.maybe_alert())
        run(insurance_balance.mark_empty())
        assert run(insurance_balance.maybe_alert(waiting=1))["kind"] == "empty"
        assert len(alerts["email"]) == 2

    def test_topup_clears_alert_lock(self, store, alerts):
        run(insurance_balance.add_topup(600))
        run(insurance_balance.maybe_alert())
        run(insurance_balance.add_topup(50))  # hala low, ama uyari kilidi sifirlandi
        assert run(insurance_balance.maybe_alert())["sent"] is True

    def test_naive_timestamp_from_mongo_does_not_crash(self, store, alerts):
        run(insurance_balance.add_topup(600))
        store.value["last_alert_at"] = datetime.utcnow() - timedelta(hours=1)
        store.value["last_alert_kind"] = "low"
        assert run(insurance_balance.maybe_alert())["reason"] == "cooldown"


class TestPolicyCost:
    def test_prefers_provider_quote_price(self):
        task = {"provider_quote_price": "244,85", "unit_cost": 100, "quantity": 3}
        assert insurance_provider._policy_cost(task) == 244.85

    def test_falls_back_to_catalog_cost_times_quantity(self):
        task = {"provider_quote_price": None, "unit_cost": 244.85, "quantity": 2}
        assert insurance_provider._policy_cost(task) == pytest.approx(489.70)

    def test_missing_everything_is_zero(self):
        assert insurance_provider._policy_cost({}) == 0.0


class TestWaitingQueue:
    @pytest.fixture
    def queue(self, monkeypatch):
        state = {"tasks": [], "issued": [], "alerted": []}

        class FakeTasks:
            def find(self, query):
                matched = [t for t in state["tasks"] if t.get("status") == query.get("status")]

                class Cursor:
                    def sort(self, *_a):
                        return self

                    async def to_list(self, _limit):
                        return matched

                return Cursor()

            async def count_documents(self, query):
                return len([t for t in state["tasks"] if t.get("status") == query.get("status")])

            async def update_one(self, query, update):
                for task in state["tasks"]:
                    if task["id"] == query["id"]:
                        task.update(update.get("$set") or {})

        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeTasks())
        monkeypatch.setattr(insurance_provider.tamamliyo, "configured", lambda: True)
        return state

    def test_no_waiting_tasks_is_noop(self, queue, monkeypatch):
        result = run(insurance_provider.retry_waiting_tasks())
        assert result == {"issued": 0, "waiting": 0}

    def test_waiting_tasks_are_skipped_without_balance(self, queue, monkeypatch):
        queue["tasks"] = [{"id": "t1", "status": "waiting_balance"}]

        async def fake_status():
            return {"remaining_try": 0}

        monkeypatch.setattr(insurance_provider.insurance_balance, "status", fake_status)
        result = run(insurance_provider.retry_waiting_tasks())
        assert result == {"issued": 0, "waiting": 1, "reason": "no_balance"}

    def test_balance_arrival_issues_every_waiting_policy(self, queue, monkeypatch):
        queue["tasks"] = [
            {"id": "t1", "status": "waiting_balance"},
            {"id": "t2", "status": "waiting_balance"},
        ]

        async def fake_status():
            return {"remaining_try": 1000}

        async def fake_issue(task_id, origin, actor=""):
            queue["issued"].append((task_id, actor))
            return {"ok": True}

        monkeypatch.setattr(insurance_provider.insurance_balance, "status", fake_status)
        monkeypatch.setattr(insurance_provider, "issue_via_provider", fake_issue)
        result = run(insurance_provider.retry_waiting_tasks())
        assert result == {"issued": 2, "waiting": 0}
        assert [t[0] for t in queue["issued"]] == ["t1", "t2"]
        assert queue["issued"][0][1] == "auto-retry"

    def test_queue_stops_on_first_failure(self, queue, monkeypatch):
        queue["tasks"] = [
            {"id": "t1", "status": "waiting_balance"},
            {"id": "t2", "status": "waiting_balance"},
        ]

        async def fake_status():
            return {"remaining_try": 1000}

        async def fake_issue(task_id, origin, actor=""):
            queue["issued"].append(task_id)
            return {"ok": task_id == "t1", "error": "Yetersiz puan bakiyesi."}

        monkeypatch.setattr(insurance_provider.insurance_balance, "status", fake_status)
        monkeypatch.setattr(insurance_provider, "issue_via_provider", fake_issue)
        result = run(insurance_provider.retry_waiting_tasks())
        assert result == {"issued": 1, "waiting": 1}
        assert queue["issued"] == ["t1", "t2"]

    def test_park_marks_task_and_alerts(self, queue, monkeypatch):
        queue["tasks"] = [{"id": "t1", "status": "pending"}]
        marked = {}

        async def fake_mark_empty():
            marked["empty"] = True

        async def fake_alert(waiting=0):
            marked["waiting"] = waiting
            return {"sent": True}

        monkeypatch.setattr(insurance_provider.insurance_balance, "mark_empty", fake_mark_empty)
        monkeypatch.setattr(insurance_provider.insurance_balance, "maybe_alert", fake_alert)

        run(insurance_provider._park_for_balance("t1"))
        assert queue["tasks"][0]["status"] == "waiting_balance"
        assert queue["tasks"][0]["waiting_since"]
        assert marked["empty"] is True
        assert marked["waiting"] == 1
