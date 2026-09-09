"""Iteration 126: terk edilmis sepet hatirlatmasi 1. asama 3 saate cekildi.

Kullanici istegi: "Sepeti yarida birakana 3 saat sonra nazik bir hatirlatma
e-postasi gonder." Akis zaten vardi (2 + 24 saat); 1. asama 3 saat oldu ve
1. asama metni daha nazik bir dille yeniden yazildi.
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import cart_reminders  # noqa: E402
from emailer import cart_reminder_html  # noqa: E402

NOW = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)


def snapshot(hours_ago: float, sent: int = 0, **over) -> dict:
    doc = {
        "email": "musteri@example.com",
        "full_name": "Ayşe K.",
        "active": True,
        "reminders_sent": sent,
        "updated_at": NOW - timedelta(hours=hours_ago),
        "items": [{"product_id": "esim_3gb", "name": "Dubai eSIM", "quantity": 1, "total": 390.0}],
        "price": 390.0,
        "currency": "TRY",
    }
    doc.update(over)
    return doc


class TestSchedule:
    def test_stages_are_three_and_twentyfour_hours(self):
        assert cart_reminders.REMINDER_STAGES_HOURS == [3, 24]

    @pytest.mark.parametrize("hours", [0, 1, 2, 2.9])
    def test_no_reminder_before_three_hours(self, hours):
        assert cart_reminders.due_stage(snapshot(hours), NOW) is None

    @pytest.mark.parametrize("hours", [3, 3.5, 10])
    def test_first_reminder_at_three_hours(self, hours):
        assert cart_reminders.due_stage(snapshot(hours), NOW) == 1

    def test_second_reminder_still_at_twentyfour_hours(self):
        assert cart_reminders.due_stage(snapshot(23, sent=1), NOW) is None
        assert cart_reminders.due_stage(snapshot(24, sent=1), NOW) == 2

    def test_no_third_reminder(self):
        assert cart_reminders.due_stage(snapshot(500, sent=2), NOW) is None

    def test_empty_or_closed_cart_is_skipped(self):
        assert cart_reminders.due_stage(snapshot(5, items=[]), NOW) is None
        assert cart_reminders.due_stage(snapshot(5, active=False), NOW) is None


class TestFirstReminderCopy:
    def test_first_stage_is_gentle_and_has_cart_link(self):
        html = cart_reminder_html(snapshot(3), "https://www.dubaivizehatti.com/sepet", 1)
        assert "Sayın Ayşe K." in html
        assert "acele etmeniz gerekmiyor" in html
        assert "https://www.dubaivizehatti.com/sepet" in html
        assert "Sepetime dön" in html

    def test_second_stage_copy_differs(self):
        first = cart_reminder_html(snapshot(3), "/sepet", 1)
        second = cart_reminder_html(snapshot(24), "/sepet", 2)
        assert first != second
        assert "güncel kurla" in second
