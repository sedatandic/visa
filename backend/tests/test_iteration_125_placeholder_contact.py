"""Iteration 125: eski demo telefon/WhatsApp numaralarini acilista temizleme.

Onizleme ve canli ortamlarin veritabanlari ayri; canlida `company_info.whatsapp`
alaninda 905331234567 gibi demo degerler kalabiliyordu ve sag alttaki WhatsApp
dugmesi yanlis numarayi aciyordu. `fix_placeholder_contact` bu degerleri guncel
numarayla degistirir, elle girilmis gercek numaralara dokunmaz.
"""

import asyncio
import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import server  # noqa: E402
from content import COMPANY  # noqa: E402


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class FakeSettings:
    def __init__(self, value=None):
        self.value = None if value is None else dict(value)
        self.updates = []

    async def find_one(self, _query):
        return None if self.value is None else {"key": "company_info", "value": self.value}

    async def update_one(self, _query, update):
        self.updates.append(update["$set"])
        for key, val in update["$set"].items():
            self.value[key[6:]] = val


@pytest.fixture
def settings(monkeypatch):
    def install(value):
        col = FakeSettings(value)
        monkeypatch.setattr(server, "settings_col", col)
        return col

    return install


class TestFixPlaceholderContact:
    @pytest.mark.parametrize(
        "placeholder",
        ["905331234567", "905337438224", "908500000000"],
    )
    def test_placeholder_whatsapp_is_replaced(self, settings, placeholder):
        col = settings({"whatsapp": placeholder, "legal_name": "Test A.Ş."})
        run(server.fix_placeholder_contact())
        assert col.value["whatsapp"] == COMPANY["whatsapp"] == "905384838224"
        assert col.value["legal_name"] == "Test A.Ş."

    @pytest.mark.parametrize(
        "placeholder",
        ["+90 533 123 45 67", "+90 533 743 82 24", "+90 850 000 00 00"],
    )
    def test_placeholder_phone_is_replaced(self, settings, placeholder):
        col = settings({"phone": placeholder})
        run(server.fix_placeholder_contact())
        assert col.value["phone"] == COMPANY["phone"] == "+90 538 483 82 24"

    def test_real_numbers_are_untouched(self, settings):
        col = settings({"phone": "+90 212 555 44 33", "whatsapp": "905551112233"})
        run(server.fix_placeholder_contact())
        assert col.updates == []
        assert col.value["whatsapp"] == "905551112233"

    def test_current_numbers_are_untouched(self, settings):
        col = settings({"phone": COMPANY["phone"], "whatsapp": COMPANY["whatsapp"]})
        run(server.fix_placeholder_contact())
        assert col.updates == []

    def test_missing_settings_document_is_safe(self, settings):
        col = settings(None)
        run(server.fix_placeholder_contact())
        assert col.updates == []

    def test_both_fields_fixed_in_single_update(self, settings):
        col = settings({"phone": "+90 850 000 00 00", "whatsapp": "905331234567"})
        run(server.fix_placeholder_contact())
        assert col.updates == [
            {"value.phone": COMPANY["phone"], "value.whatsapp": COMPANY["whatsapp"]}
        ]

    def test_migration_runs_on_startup(self):
        source = open(os.path.join(BACKEND_DIR, "server.py")).read()
        init_block = source.split("async def _init_startup_state()")[1]
        assert "await fix_placeholder_contact()" in init_block.split("except Exception")[0]
