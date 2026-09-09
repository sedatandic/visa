"""Iteration 130: Tamamliyo odemesi cari bakiyeye alindi, kart/CVV .env'den kaldirildi.

Kullanici istegi (2026-06): "Tamamliyo odemesini cari bakiyeye cevirip .env'deki kart ve
CVV bilgisini tamamen kaldiralim."

- Varsayilan odeme tipi 3 (cari bakiye); istekte kart alani gonderilmez.
- `TAMAMLIYO_PAYMENT_TYPE=2` ile kurumsal karta donulebilir (kart .env'e yazilirsa).
- Cari bakiye modunda `card_configured()` True doner; bekleyen police kuyrugu kart
  tanimsizligi yuzunden durmaz.
- Sunucuda kart/CVV degeri kalmadi.
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import insurance_payment  # noqa: E402
import tamamliyo  # noqa: E402

CARD_ENVS = list(tamamliyo.CARD_ENV.values())


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture
def captured(monkeypatch):
    calls = []

    async def fake_request(method, path, payload=None, retry=True):
        calls.append({"method": method, "path": path, "body": payload, "retry": retry})
        return {"success": True, "data": {}}

    monkeypatch.setattr(tamamliyo, "_request", fake_request)
    return calls


@pytest.fixture(autouse=True)
def balance_default(monkeypatch):
    monkeypatch.delenv("TAMAMLIYO_PAYMENT_TYPE", raising=False)
    for env in CARD_ENVS:
        monkeypatch.delenv(env, raising=False)


class TestBalancePayment:
    def test_default_payment_type_is_current_account(self):
        assert tamamliyo.payment_type() == "3"
        assert tamamliyo.balance_mode() is True

    def test_pay_body_has_no_card_fields(self, captured):
        run(tamamliyo.pay_for_quote(2135835))
        body = captured[0]["body"]
        assert body == {"odemeTipi": "3", "teklifId": 2135835}
        assert captured[0]["path"].endswith("/odeme-yap")
        assert captured[0]["retry"] is False

    def test_balance_mode_does_not_need_card(self):
        assert tamamliyo.card_configured() is True
        assert tamamliyo.card_hint() == ""

    def test_card_mode_still_available_via_env(self, monkeypatch, captured):
        monkeypatch.setenv("TAMAMLIYO_PAYMENT_TYPE", "2")
        monkeypatch.setenv("TAMAMLIYO_CARD_NUMBER", "4111 1111 1111 1111")
        monkeypatch.setenv("TAMAMLIYO_CARD_EXPIRY", "2030-12-01")
        monkeypatch.setenv("TAMAMLIYO_CARD_CVV", "123")
        monkeypatch.setenv("TAMAMLIYO_CARD_NAME", "MORUYA")
        monkeypatch.setenv("TAMAMLIYO_CARD_SURNAME", "TRAVEL")
        run(tamamliyo.pay_for_quote("2135835"))
        body = captured[0]["body"]
        assert body["odemeTipi"] == "2"
        assert body["krediKartiNo"] == "4111111111111111"

    def test_card_mode_without_card_raises(self, monkeypatch, captured):
        monkeypatch.setenv("TAMAMLIYO_PAYMENT_TYPE", "2")
        assert tamamliyo.card_configured() is False
        with pytest.raises(tamamliyo.TamamliyoError):
            run(tamamliyo.pay_for_quote("2135835"))
        assert captured == []

    def test_unknown_payment_type_falls_back_to_balance(self, monkeypatch):
        monkeypatch.setenv("TAMAMLIYO_PAYMENT_TYPE", "9")
        assert tamamliyo.payment_type() == "3"


class TestPaymentStatusPanel:
    def test_status_reports_balance_method(self, monkeypatch):
        async def fake_state():
            return {}

        monkeypatch.setattr(insurance_payment, "_state", fake_state)
        state = run(insurance_payment.status())
        assert state["method"] == "balance"
        assert state["card_configured"] is True
        assert state["card_hint"] == ""

    def test_alert_text_mentions_balance(self):
        subject, html, wa = insurance_payment._alert_texts("blocked", 2, True)
        assert "cari bakiye" in html.lower()
        assert "ACİL" in subject
        assert wa

    def test_provider_error_hint_points_to_balance(self, monkeypatch):
        import insurance_provider

        saved = {}

        class FakeCol:
            async def update_one(self, _query, update):
                saved["message"] = update["$set"]["provider_error"]

        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeCol())
        run(insurance_provider._save_provider_error("t1", "Yetersiz bakiye."))
        assert "cari bakiye" in saved["message"].lower()
        assert "kart" not in saved["message"].lower()


class TestNoCardSecretsOnServer:
    def test_env_file_has_no_card_or_cvv_values(self):
        lines = Path(BACKEND_DIR, ".env").read_text(encoding="utf-8").splitlines()
        card_lines = [line for line in lines if line.startswith("TAMAMLIYO_CARD_")]
        assert card_lines, "kart anahtarlari .env'de tanimli kalmali (bos deger ile)"
        for line in card_lines:
            assert line.split("=", 1)[1].strip() == "", f"kart verisi hala .env icinde: {line}"

    def test_payment_type_env_is_balance(self):
        lines = Path(BACKEND_DIR, ".env").read_text(encoding="utf-8").splitlines()
        assert "TAMAMLIYO_PAYMENT_TYPE=3" in [line.strip() for line in lines]
