"""Iteration 100: verify inline-logo attachment + subject_with_ref refactor.

Covers:
- _logo_payload reads the PNG.
- subject_with_ref formatting (with + without ref).
- _wrap embeds <img src="cid:dvh-logo"> when logo present.
- _resend_params includes an attachments array with the correct fields
  when html contains cid:dvh-logo.
- _record_attempt stores the public URL instead of cid in email_outbox.html.
- application_received: real subject through send_email uses new prefix.
"""
import os
import sys
import asyncio
import re
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

os.environ["RESEND_API_KEY"] = "re_test_fake_key_for_monkeypatch"
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
        return {"id": "fake_id"}

    class FakeEmails:
        send = staticmethod(fake_send)

    class FakeResend:
        api_key = None
        Emails = FakeEmails

    monkeypatch.setitem(sys.modules, "resend", FakeResend)
    return holder


# --- subject_with_ref ---
def test_subject_with_ref_with_reference():
    assert emailer.subject_with_ref("DV-X", "alındı") == "DV-X başvuru nolu Dubai vize başvurunuz alındı"


def test_subject_with_ref_empty_fallback():
    assert emailer.subject_with_ref("", "alındı") == "Dubai vize başvurunuz alındı"
    assert emailer.subject_with_ref(None, "alındı") == "Dubai vize başvurunuz alındı"


# --- logo payload ---
def test_logo_payload_reads_file():
    # reset the module-level cache to force a fresh read
    emailer._logo_bytes = None
    data = emailer._logo_payload()
    assert data is not None
    assert len(data) > 1000  # not empty
    # PNG magic
    assert data[:8] == b"\x89PNG\r\n\x1a\n"


# --- _wrap uses cid src ---
def test_wrap_uses_cid_when_logo_present():
    emailer._logo_bytes = None
    html = emailer._wrap("Title", "<p>x</p>")
    assert 'src="cid:dvh-logo"' in html
    assert "https://" not in html.split('<img')[1].split('/>')[0]  # img tag itself uses cid


# --- _resend_params attaches logo ---
def test_resend_params_includes_attachment_when_cid_in_html():
    emailer._logo_bytes = None
    html = emailer._wrap("Title", "<p>hi</p>")
    params = emailer._resend_params(
        "delivered@resend.dev",
        "Konu",
        html,
        kind="application_received",
        sender="Dubai Vize Hattı <onboarding@resend.dev>",
        reply_to="",
    )
    assert "attachments" in params, "attachments key missing when cid used"
    atts = params["attachments"]
    assert len(atts) == 1
    a = atts[0]
    assert a["filename"] == "dubai-vize-hatti.png"
    assert a["content_id"] == "dvh-logo"
    assert a["content_type"] == "image/png"
    assert isinstance(a["content"], list) and len(a["content"]) > 1000


def test_resend_params_no_attachment_without_cid():
    params = emailer._resend_params(
        "delivered@resend.dev",
        "Konu",
        "<p>plain html no logo</p>",
        kind="application_received",
        sender="Dubai Vize Hattı <onboarding@resend.dev>",
        reply_to="",
    )
    assert "attachments" not in params


# --- outbox stores public URL not cid ---
def test_outbox_html_replaces_cid_with_public_url(captured_params, _stub_outbox):
    emailer._logo_bytes = None
    html = emailer._wrap("Baslik", "<p>merhaba</p>")
    assert 'cid:dvh-logo' in html
    asyncio.run(
        emailer.send_email("delivered@resend.dev", "Konu", html, kind="application_received")
    )
    assert len(_stub_outbox.docs) == 1
    stored_html = _stub_outbox.docs[0]["html"]
    assert "cid:dvh-logo" not in stored_html, "outbox still contains cid: reference"
    # Public logo URL should be present (may be empty PUBLIC_SITE_URL -> /brand/...)
    assert "/brand/logo-horizontal-gold-palm.png" in stored_html


# --- integration: application_received subject uses ref prefix ---
def test_application_received_subject_format(captured_params, _stub_outbox):
    from emailer import applicant_received_html, subject_with_ref
    ref = "DV-2026-ABC123"
    app_doc = {
        "reference_code": ref,
        "contact": {"full_name": "Test User", "email": "delivered@resend.dev"},
        "applicant": {"first_name": "Test", "last_name": "User"},
        "travelers": [{"first_name": "T", "last_name": "U", "visa_short_name": "30 gün", "price": 1000, "currency": "TRY"}],
        "price": 1000, "currency": "TRY",
        "payment": {"status": "paid"}, "processing_days": "2 iş günü",
    }
    subj = subject_with_ref(ref, "alındı")
    asyncio.run(emailer.send_email("delivered@resend.dev", subj, applicant_received_html(app_doc), kind="application_received"))
    params = captured_params["params"]
    assert params["subject"] == f"{ref} başvuru nolu Dubai vize başvurunuz alındı"
    # attachment travelled through
    assert "attachments" in params
    assert params["attachments"][0]["content_id"] == "dvh-logo"
