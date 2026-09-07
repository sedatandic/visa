"""Unit tests for emailer.send_email deliverability fixes (no real emails sent)."""
import os
import sys
import asyncio
import logging
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

# Ensure a fake API key so the resend branch is taken
os.environ["RESEND_API_KEY"] = "re_test_fake_key_for_monkeypatch"
os.environ.setdefault("REPLY_TO_EMAIL", "")
os.environ.setdefault("ADMIN_EMAIL", "info@dubaivizeonline.com")
os.environ.setdefault("SENDER_EMAIL", "onboarding@resend.dev")

import emailer  # noqa: E402


class _FakeOutbox:
    def __init__(self):
        self.docs = []

    async def insert_one(self, doc):
        self.docs.append(doc)
        return doc


@pytest.fixture(autouse=True)
def _stub_outbox(monkeypatch):
    fake = _FakeOutbox()
    monkeypatch.setattr(emailer, "email_outbox_col", fake)
    return fake


@pytest.fixture
def captured_params(monkeypatch):
    holder = {}

    def fake_send(params):
        holder["params"] = params
        return {"id": "fake_resend_id"}

    class FakeEmails:
        send = staticmethod(fake_send)

    class FakeResend:
        api_key = None
        Emails = FakeEmails

    monkeypatch.setitem(sys.modules, "resend", FakeResend)
    return holder


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if False else asyncio.run(coro)


# --- send_email params: text, reply_to, headers ---
def test_send_email_marketing_kind_has_all_deliverability_fields(captured_params, monkeypatch) -> None:
    monkeypatch.setenv("REPLY_TO_EMAIL", "info@dubaivizeonline.com")
    html = "<p>Merhaba <strong>Ali</strong>&nbsp;bey</p><div>Yarim basvurunuz</div>"
    result = asyncio.run(
        emailer.send_email("user@example.com", "Konu", html, kind="draft_reminder")
    )
    assert result["status"] == "sent"
    params = captured_params["params"]
    # plain-text alternative
    assert "text" in params
    assert params["text"].strip() != ""
    assert "<" not in params["text"]
    assert "Merhaba" in params["text"]
    # reply_to
    assert params["reply_to"] == "info@dubaivizeonline.com"
    # List-Unsubscribe (marketing)
    assert "headers" in params
    assert "List-Unsubscribe" in params["headers"]
    assert "List-Unsubscribe-Post" in params["headers"]
    assert params["headers"]["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"


def test_send_email_transactional_kind_has_no_list_unsubscribe(captured_params, monkeypatch) -> None:
    monkeypatch.setenv("REPLY_TO_EMAIL", "info@dubaivizeonline.com")
    html = "<p>Basvurunuz alindi</p>"
    result = asyncio.run(
        emailer.send_email("user@example.com", "Konu", html, kind="application_received")
    )
    assert result["status"] == "sent"
    params = captured_params["params"]
    assert params.get("reply_to") == "info@dubaivizeonline.com"
    assert "headers" not in params or "List-Unsubscribe" not in (params.get("headers") or {})
    assert "text" in params and params["text"]


# --- _html_to_text helper ---
def test_html_to_text_strips_tags_and_entities() -> None:
    html = "<p>Merhaba&nbsp;Ali</p><br/><div>Fiyat &amp; koşullar</div><script>bad()</script>"
    txt = emailer._html_to_text(html)
    assert "<" not in txt
    assert "script" not in txt.lower() or "bad()" not in txt
    assert "Merhaba Ali" in txt
    assert "Fiyat & koşullar" in txt


def test_html_to_text_real_template_turkish() -> None:
    app_doc = {
        "reference_code": "DV-2026-1234",
        "contact": {"full_name": "Ayşe Yılmaz", "email": "a@example.com"},
        "applicant": {"first_name": "Ayşe", "last_name": "Yılmaz"},
        "travelers": [
            {"first_name": "Ayşe", "last_name": "Yılmaz", "visa_short_name": "30 gün tek giriş", "price": 3500, "currency": "TRY"}
        ],
        "price": 3500,
        "currency": "TRY",
        "payment": {"status": "paid"},
        "processing_days": "2 iş günü",
    }
    html = emailer.applicant_received_html(app_doc)
    txt = emailer._html_to_text(html)
    assert "<" not in txt
    assert "Ayşe Yılmaz" in txt
    assert "DV-2026-1234" in txt
    assert "Başvurunuz alındı" in txt


# --- warning log when SENDER_EMAIL is @resend.dev ---
def test_warning_logged_for_resend_dev_sender(captured_params, caplog, _stub_outbox, monkeypatch) -> None:
    monkeypatch.setenv("SENDER_EMAIL", "onboarding@resend.dev")
    caplog.set_level(logging.WARNING, logger=emailer.logger.name)
    result = asyncio.run(
        emailer.send_email("u@example.com", "s", "<p>hi</p>", kind="application_received")
    )
    # No exception, still recorded
    assert result["status"] == "sent"
    assert len(_stub_outbox.docs) == 1
    # warning present
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any("resend.dev" in r.getMessage().lower() for r in warnings)


# --- regression: never raises; outbox always written ---
def test_send_email_skipped_when_placeholder_key(_stub_outbox, monkeypatch) -> None:
    monkeypatch.setenv("RESEND_API_KEY", "re_placeholder_xxx")
    result = asyncio.run(
        emailer.send_email("u@example.com", "s", "<p>hi</p>", kind="application_received")
    )
    assert result["status"] == "skipped"
    assert len(_stub_outbox.docs) == 1
    assert _stub_outbox.docs[0]["status"] == "skipped"


def test_send_email_error_status_when_resend_raises(_stub_outbox, monkeypatch) -> None:
    monkeypatch.setenv("RESEND_API_KEY", "re_valid_looking")

    class FakeEmails:
        @staticmethod
        def send(params):
            raise RuntimeError("boom")

    class FakeResend:
        api_key = None
        Emails = FakeEmails

    monkeypatch.setitem(sys.modules, "resend", FakeResend)
    result = asyncio.run(
        emailer.send_email("u@example.com", "s", "<p>hi</p>", kind="application_received")
    )
    assert result["status"] == "error"
    assert "boom" in result["reason"]
    assert len(_stub_outbox.docs) == 1
    assert _stub_outbox.docs[0]["status"] == "error"
