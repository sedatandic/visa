"""Iteration 144 (guncellendi 2026-06-18): API bilgisi yokken elle kesim modu.

Kullanici istegi: "cancel the tamamliyo api" -> "tamamliyo tamamen kaldir".
Saglayici secimi artik `sigortambudur` (API) veya `manual` (elle kesim). API bilgisi
eksikse sistem hicbir servise baglanmaz; satis devam eder, police gorevi elle kesilir.
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


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture(autouse=True)
def no_settings(monkeypatch):
    """Panel ayari bos: mod ortam degiskeninden okunur."""

    async def empty():
        return {}

    monkeypatch.setattr(insurance_provider, "_settings_value", empty)
    monkeypatch.delenv("INSURANCE_PROVIDER", raising=False)
    monkeypatch.setenv("SIGORTAMBUDUR_CLIENT_ID", "cid")
    monkeypatch.setenv("SIGORTAMBUDUR_CLIENT_SECRET", "")


class TestActiveProvider:
    def test_default_is_manual(self):
        assert run(insurance_provider.active_provider()) == "manual"
        assert run(insurance_provider.api_enabled()) is False

    def test_api_needs_credentials(self, monkeypatch):
        monkeypatch.setenv("INSURANCE_PROVIDER", "sigortambudur")
        assert run(insurance_provider.api_enabled()) is False
        monkeypatch.setenv("SIGORTAMBUDUR_CLIENT_SECRET", "secret")
        assert run(insurance_provider.api_enabled()) is True

    def test_unknown_provider_falls_back_to_manual(self, monkeypatch):
        monkeypatch.setenv("INSURANCE_PROVIDER", "tamamliyo")
        assert run(insurance_provider.active_provider()) == "manual"

    def test_set_provider_rejects_unknown(self):
        with pytest.raises(ValueError):
            run(insurance_provider.set_provider("tamamliyo"))


class TestManualMode:
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

    def test_manual_link_points_to_provider_portal(self):
        assert "panaceasigorta.com" in insurance_tasks.PROVIDER_PANEL
