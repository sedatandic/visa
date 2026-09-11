"""Iteration 144: Tamamliyo API'si iptal edildi, sigorta saglayicisi ayara baglandi.

Kullanici istegi (2026-06): "cancel the tamamliyo api" + "baska bir api tanimlayacagim".

- Varsayilan mod `manual`: hicbir Tamamliyo cagrisi yapilmaz, police elle kesilip yuklenir.
- `sync_prices` / `probe_product` / `issue_via_provider` / `retry_waiting_tasks` erken doner.
- Panelden `tamamliyo` secilse bile API bilgileri yoksa `api_enabled` False kalir.
- Yeni police gorevleri aktif saglayici adiyla acilir (artik sabit "tamamliyo" degil).
"""

import asyncio
import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import insurance_provider  # noqa: E402
import insurance_tasks  # noqa: E402
import tamamliyo  # noqa: E402


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture(autouse=True)
def no_settings(monkeypatch):
    """Panel ayari bos: mod ortam degiskeninden okunur."""

    async def empty():
        return {}

    monkeypatch.setattr(insurance_provider, "_settings_value", empty)
    monkeypatch.delenv("INSURANCE_PROVIDER", raising=False)


class TestActiveProvider:
    def test_default_is_manual(self):
        assert run(insurance_provider.active_provider()) == "manual"
        assert run(insurance_provider.api_enabled()) is False

    def test_env_can_select_tamamliyo_but_needs_credentials(self, monkeypatch):
        monkeypatch.setenv("INSURANCE_PROVIDER", "tamamliyo")
        monkeypatch.setattr(tamamliyo, "configured", lambda: False)
        assert run(insurance_provider.active_provider()) == "tamamliyo"
        assert run(insurance_provider.api_enabled()) is False

        monkeypatch.setattr(tamamliyo, "configured", lambda: True)
        assert run(insurance_provider.api_enabled()) is True

    def test_unknown_provider_falls_back_to_manual(self, monkeypatch):
        monkeypatch.setenv("INSURANCE_PROVIDER", "sigortam-net")
        assert run(insurance_provider.active_provider()) == "manual"


class TestApiCallsBlocked:
    def test_sync_prices_skipped(self, monkeypatch):
        async def boom(*_args, **_kwargs):
            raise AssertionError("Tamamliyo cagrilmamali")

        monkeypatch.setattr(tamamliyo, "price", boom)
        assert run(insurance_provider.sync_prices())["reason"] == "provider_disabled"

    def test_probe_product_reports_api_off(self, monkeypatch):
        async def boom(*_args, **_kwargs):
            raise AssertionError("Tamamliyo cagrilmamali")

        monkeypatch.setattr(tamamliyo, "price", boom)
        result = run(insurance_provider.probe_product(220))
        assert result["available"] is False
        assert "kapalı" in result["error"]

    def test_issue_via_provider_asks_for_manual_upload(self, monkeypatch):
        async def fake_find(_query):
            return {"id": "t1", "status": "pending"}

        monkeypatch.setattr(insurance_provider.insurance_tasks_col, "find_one", fake_find)
        result = run(insurance_provider.issue_via_provider("t1", "https://x.test"))
        assert result == {
            "ok": False,
            "error": insurance_provider.API_OFF_MESSAGE,
            "manual": True,
        }

    def test_retry_queue_does_not_call_provider(self, monkeypatch):
        class FakeCursor:
            def sort(self, *_a):
                return self

            async def to_list(self, _n):
                return [{"id": "t1"}]

        monkeypatch.setattr(
            insurance_provider.insurance_tasks_col, "find", lambda *_a, **_k: FakeCursor()
        )

        async def boom(*_args, **_kwargs):
            raise AssertionError("police kesimi denenmemeli")

        monkeypatch.setattr(insurance_provider, "issue_via_provider", boom)
        assert run(insurance_provider.retry_waiting_tasks()) == {"issued": 0, "waiting": 1}


class TestTaskProviderName:
    def test_new_task_uses_active_provider(self):
        task = insurance_tasks._build_policy_task(
            {"id": "o1", "reference_code": "DV1", "travel": {}},
            {"product_id": "ins_7d", "name": "7 gün", "validity_days": 7, "quantity": 1},
            {"full_name": "Ad Soyad"},
            insurance_tasks.datetime.now(insurance_tasks.timezone.utc),
            "manual",
        )
        assert task["provider"] == "manual"
        assert task["status"] == "pending"
