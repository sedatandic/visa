"""Zami oturum uyarilarinin tekrar gonderim (cooldown) davranisi.

Pytest suite uses plain asyncio.run helpers (no pytest-asyncio) to match the
repo-wide style in /app/backend/tests/test_insurance_automation.py.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock

# Make backend importable when running from /app
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import zami_rpa  # noqa: E402
import zami_status  # noqa: E402
from db import settings_col  # noqa: E402


def _iso(delta_hours: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=delta_hours)).isoformat()


# Motor binds its executor to the first running loop it sees, so we keep a
# single loop for all tests instead of using asyncio.run() (which closes the
# loop and orphans the Motor executor -> "Event loop is closed").
_LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(_LOOP)


def _run(coro):
    return _LOOP.run_until_complete(coro)


# -----------------------------------------------------------------------------
# Fix (A): OTP flow reasons must NOT trigger a second e-mail (otp_reminders owns them)
# -----------------------------------------------------------------------------
def test_otp_flow_reasons_dont_send_second_email(monkeypatch):
    sent = []

    async def fake_send(*a, **k):  # pragma: no cover - trivial spy
        sent.append((a, k))
        return {"status": "sent"}

    monkeypatch.setattr(zami_status, "send_email", fake_send)
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")

    async def _go():
        for reason in ("otp_required", "otp_required_pending", "no_trusted_device"):
            await zami_status._warn_admin_session_expired(reason=reason)

    _run(_go())
    assert sent == [], f"OTP-flow reasons should be silent but got {len(sent)} sends"


# -----------------------------------------------------------------------------
# Fix (A): persistent 12h cooldown must survive process restart (backed by settings_col)
# -----------------------------------------------------------------------------
def test_cooldown_blocks_repeat_warning():
    async def _go():
        doc = await settings_col.find_one({"key": "zami_session"})
        original = (doc or {}).get("value") or {}
        try:
            # 1h ago -> still in cooldown
            await settings_col.update_one(
                {"key": "zami_session"},
                {"$set": {"value.expired_notified_at": _iso(1),
                          "value.otp_reminder_sent_at": None}},
                upsert=True,
            )
            assert await zami_status._warn_cooldown_passed() is False, \
                "cooldown should block within 12h window"

            # 13h ago -> passed
            await settings_col.update_one(
                {"key": "zami_session"},
                {"$set": {"value.expired_notified_at": _iso(13),
                          "value.otp_reminder_sent_at": None}},
            )
            assert await zami_status._warn_cooldown_passed() is True, \
                "cooldown should pass after 12h"

            # otp_reminder within 12h should also block
            await settings_col.update_one(
                {"key": "zami_session"},
                {"$set": {"value.expired_notified_at": None,
                          "value.otp_reminder_sent_at": _iso(2)}},
            )
            assert await zami_status._warn_cooldown_passed() is False, \
                "otp_reminder within 12h must also block"
        finally:
            await settings_col.update_one(
                {"key": "zami_session"}, {"$set": {"value": original}}, upsert=True
            )

    _run(_go())


# -----------------------------------------------------------------------------
# Fix (A): first send writes expired_notified_at (persistent, restart-safe)
# -----------------------------------------------------------------------------
def test_warn_writes_persistent_timestamp(monkeypatch):
    monkeypatch.setenv("ADMIN_EMAIL", "admin@example.com")

    calls = []

    async def fake_send(*a, **k):
        calls.append((a, k))
        return {"status": "sent"}

    monkeypatch.setattr(zami_status, "send_email", fake_send)

    async def _go():
        doc = await settings_col.find_one({"key": "zami_session"})
        original = (doc or {}).get("value") or {}
        try:
            # Clear both cooldown fields so send fires
            await settings_col.update_one(
                {"key": "zami_session"},
                {"$set": {"value.expired_notified_at": None,
                          "value.otp_reminder_sent_at": None}},
                upsert=True,
            )
            await zami_status._warn_admin_session_expired(reason="browser")
            assert len(calls) == 1, f"expected 1 send, got {len(calls)}"

            # Persisted timestamp?
            doc2 = await settings_col.find_one({"key": "zami_session"})
            v = (doc2 or {}).get("value") or {}
            assert v.get("expired_notified_at"), "expired_notified_at must be persisted"

            # Second call should be suppressed by cooldown even across simulated restart
            await zami_status._warn_admin_session_expired(reason="browser")
            assert len(calls) == 1, "cooldown should block second send"
        finally:
            await settings_col.update_one(
                {"key": "zami_session"}, {"$set": {"value": original}}, upsert=True
            )

    _run(_go())


# -----------------------------------------------------------------------------
# Fix (A): trusted-device helper strips stale session cookies (expires<=0)
# -----------------------------------------------------------------------------
def test_trust_only_state_drops_session_cookies():
    state = {
        "cookies": [
            {"name": "9D", "expires": 1790000000.0},
            {"name": "9W", "expires": -1},
        ],
        "origins": [],
    }
    out = zami_rpa._trust_only_state(state)
    assert [c["name"] for c in out["cookies"]] == ["9D"]


def test_trust_only_state_handles_empty_state():
    # Must not raise on empty / missing keys
    assert zami_rpa._trust_only_state({}) == {"cookies": [], "origins": []}
    assert zami_rpa._trust_only_state({"cookies": None, "origins": None}) == {
        "cookies": [], "origins": []
    }
