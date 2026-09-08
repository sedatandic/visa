"""Iteration 118: Tamamliyo teklif/odeme payload testleri.

2026-09-08 guncellemesi: saglayici partner hesabimizda cari bakiye (odemeTipi=3)
bulunmadigini bildirdi; odeme `odeme-yap` ucundan `odemeTipi=2` (kurumsal kart) ile
yapiliyor. Kart bilgileri yalnizca .env'den okunur.

Canli testte ortaya cikan uc hata:
1. `teklif-olustur` -> HATA_2 "ulkeKodu gonderilmesi zorunludur" (eksik alan).
2. `odeme-onay` -> HATA_3 "parameters icinde pnrNo/flightNumber/ticketNumber ...
   zorunludur" (bilet alanlari gonderilmiyordu).
3. Hata mesaji `data.errorMessage` altinda geldigi icin panele "beklenmeyen yanit"
   yaziliyordu; gercek saglayici mesaji gorunmuyordu.

Bu testler canli API'ye cikmaz; `_request` mock'lanir.
"""

import asyncio
import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import insurance_provider  # noqa: E402
import tamamliyo  # noqa: E402


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture
def captured(monkeypatch):
    """`_request` cagrilarini yakalar, sabit basarili yanit doner."""
    calls = []

    async def fake_request(method, path, payload=None, retry=True):
        calls.append({"method": method, "path": path, "body": payload, "retry": retry})
        return {"success": True, "data": {}}

    monkeypatch.setattr(tamamliyo, "_request", fake_request)
    return calls


class TestQuotePayload:
    def test_quote_sends_uae_country_code(self, captured):
        run(
            tamamliyo.create_quote(
                [{"tc_kimlik_no": "45181872398", "birth_date": "1981-08-01"}],
                "2026-10-07",
                "2026-10-14",
                "a@b.com",
                "+905325882630",
            )
        )
        body = captured[0]["body"]
        assert body["ulkeKodu"] == 784
        assert tamamliyo.ULKE_KODU_BAE == 784
        assert captured[0]["path"].endswith("/teklif-olustur")

    def test_quote_maps_insured_to_provider_fields(self, captured):
        run(
            tamamliyo.create_quote(
                [
                    {"tc_kimlik_no": "45181872398", "birth_date": "1981-08-01"},
                    {"tc_kimlik_no": "10000000146", "birth_date": "1990-01-15"},
                ],
                "2026-10-07",
                "2026-10-14",
                "a@b.com",
                "+905325882630",
            )
        )
        body = captured[0]["body"]
        assert body["sigortaEttiren"] == {"tcKimlikNo": "45181872398", "dogumTarihi": "1981-08-01"}
        assert len(body["sigortali"]) == 2
        assert body["urun"] == "yurtdisi-seyahat"
        assert body["urun_id"] == 141

    def test_price_does_not_need_country_code(self, captured):
        # Canli dogrulama: fiyat ulkeKodu ile de olmadan da 244,85 TL donuyor.
        run(tamamliyo.price(1, "2026-10-07", "2026-10-14"))
        assert "ulkeKodu" not in captured[0]["body"]


class TestPaymentPayload:
    """Odeme kurumsal kartla yapilir (`odeme-yap`, odemeTipi=2 — cari bakiye yontemi yok)."""

    @pytest.fixture(autouse=True)
    def card(self, monkeypatch):
        monkeypatch.setenv("TAMAMLIYO_CARD_NUMBER", "4111 1111 1111 1111")
        monkeypatch.setenv("TAMAMLIYO_CARD_EXPIRY", "2030-12-01")
        monkeypatch.setenv("TAMAMLIYO_CARD_CVV", "123")
        monkeypatch.setenv("TAMAMLIYO_CARD_NAME", "MORUYA")
        monkeypatch.setenv("TAMAMLIYO_CARD_SURNAME", "TRAVEL")

    def test_pay_body_uses_card_payment_type(self, captured):
        run(tamamliyo.pay_for_quote(2135835))
        body = captured[0]["body"]
        assert body["odemeTipi"] == "2"
        assert body["teklifId"] == 2135835
        assert captured[0]["path"].endswith("/odeme-yap")

    def test_card_fields_come_from_env_and_are_normalised(self, captured):
        run(tamamliyo.pay_for_quote("2135835"))
        body = captured[0]["body"]
        assert body["krediKartiNo"] == "4111111111111111"  # bosluklar temizlenir
        assert body["krediKartiCvv"] == "123"
        assert body["krediKartiBitisTarihi"] == "2030-12-01"
        assert body["krediKartiAd"] == "MORUYA"
        assert body["krediKartiSoyad"] == "TRAVEL"

    def test_payment_request_is_never_retried(self, captured):
        # Zaman asiminda cekim yapilmis olabilir: tekrar denemek mukerrer cekim riskidir.
        run(tamamliyo.pay_for_quote("2135835"))
        assert captured[0]["retry"] is False

    def test_card_hint_masks_number(self):
        assert tamamliyo.card_hint() == "**** 1111"
        assert tamamliyo.card_configured() is True

    def test_missing_card_raises_actionable_error(self, monkeypatch, captured):
        monkeypatch.delenv("TAMAMLIYO_CARD_CVV", raising=False)
        assert tamamliyo.card_configured() is False
        with pytest.raises(tamamliyo.TamamliyoError) as err:
            run(tamamliyo.pay_for_quote("2135835"))
        assert "TAMAMLIYO_CARD_CVV" in str(err.value)
        assert captured == []  # istek hic gonderilmez

    def test_timeout_marks_payment_unknown(self, monkeypatch):
        import httpx

        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return False

            async def request(self, *_args, **_kwargs):
                raise httpx.ReadTimeout("timeout")

        monkeypatch.setenv("TAMAMLIYO_BASE_URL", "https://api-test.example.com")
        monkeypatch.setenv("TAMAMLIYO_TOKEN", "test-token")
        monkeypatch.setattr(httpx, "AsyncClient", lambda **_kwargs: FakeClient())
        with pytest.raises(tamamliyo.TamamliyoError) as err:
            run(tamamliyo.pay_for_quote("2135835"))
        assert tamamliyo.PAYMENT_UNKNOWN_MARKER in str(err.value)

    def test_ensure_policy_pays_with_card(self, monkeypatch):
        seen = {}

        async def fake_pay(quote_id):
            seen["quote_id"] = quote_id
            return {"success": True}

        async def fake_policy(quote_id):
            return {"data": {"policeNo": "P-1"}}

        async def fake_mark(task_id, step, detail=None):
            seen.setdefault("steps", []).append(step)

        monkeypatch.setattr(tamamliyo, "pay_for_quote", fake_pay)
        monkeypatch.setattr(tamamliyo, "create_policy", fake_policy)
        monkeypatch.setattr(insurance_provider, "_mark_step", fake_mark)

        task = {"id": "t1", "order_reference": "SV-XFG87WZW", "starts_on": "2026-10-07"}
        run(insurance_provider._ensure_policy(task, "2135835", {}))

        assert seen["quote_id"] == "2135835"
        assert seen["steps"] == ["payment_confirm", "policy"]

    def test_completed_steps_are_not_repeated(self, monkeypatch):
        called = []

        async def fake_pay(quote_id):
            called.append("pay")
            return {"success": True}

        async def fake_policy(quote_id):
            called.append("policy")
            return {"data": {}}

        async def fake_mark(task_id, step, detail=None):
            return None

        monkeypatch.setattr(tamamliyo, "pay_for_quote", fake_pay)
        monkeypatch.setattr(tamamliyo, "create_policy", fake_policy)
        monkeypatch.setattr(insurance_provider, "_mark_step", fake_mark)

        steps = {"payment_confirm": "done", "policy": "done"}
        run(insurance_provider._ensure_policy({"id": "t1"}, "2135835", steps))
        assert called == []


class TestErrorMessage:
    def test_reads_nested_error_message(self):
        payload = {
            "success": False,
            "data": {
                "errorCode": "HATA_3",
                "errorMessage": "Bu teklif için acik tahsilat işlemi yapılamaz.",
            },
        }
        assert tamamliyo._error_message(payload) == "Bu teklif için acik tahsilat işlemi yapılamaz."

    def test_falls_back_to_error_code(self):
        assert tamamliyo._error_message({"data": {"errorCode": "HATA_7"}}) == "HATA_7"

    def test_top_level_message_still_works(self):
        payload = {"success": False, "message": "SFS unsur kaydı yapılamadı", "data": {}}
        assert tamamliyo._error_message(payload) == "SFS unsur kaydı yapılamadı"

    def test_nested_message_wins_over_generic_default(self):
        payload = {"success": False, "data": {"errorMessage": "ulkeKodu zorunludur"}}
        assert "beklenmeyen" not in tamamliyo._error_message(payload)

    def test_unknown_shape_gives_default(self):
        assert "beklenmeyen" in tamamliyo._error_message({"weird": 1})
        assert "beklenmeyen" in tamamliyo._error_message("plain text")


class TestProviderContact:
    """Musteri, Tamamliyo'nun haber/promosyon listesine eklenmemeli (2026-09-08)."""

    def test_uses_agency_contact_not_customer(self):
        from content import COMPANY

        email, phone = insurance_provider._provider_contact()
        assert "dubaivizehatti.com" in email
        assert phone == COMPANY["phone"].replace(" ", "")
        assert " " not in phone  # servis bosluklu gsmNo kabul etmiyor

    def test_ensure_quote_never_sends_customer_email(self, monkeypatch):
        seen = {}

        async def fake_quote(insured, starts_on, ends_on, email, phone):
            seen.update(email=email, phone=phone, insured=insured)
            return {"data": {"teklifBilgileri": {"teklifId": "999", "fiyat": "244,85"}}}

        class FakeCol:
            async def update_one(self, *_args, **_kwargs):
                return None

            async def find_one(self, *_args, **_kwargs):
                return {"id": "t1", "provider_quote_id": "999"}

        monkeypatch.setattr(tamamliyo, "create_quote", fake_quote)
        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", FakeCol())

        task = {
            "id": "t1",
            "starts_on": "2026-10-07",
            "ends_on": "2026-10-13",
            "customer": {"email": "musteri@ornek.com", "phone": "05325882630"},
        }
        quote_id = run(insurance_provider._ensure_quote(task, [{"tcKimlikNo": "45181872398"}]))

        assert quote_id == "999"
        assert seen["email"] != "musteri@ornek.com"
        assert seen["phone"] != "05325882630"
        assert "dubaivizehatti.com" in seen["email"]


class TestProviderErrorHint:
    """Odeme hatasi panelde ne yapilacagini soylemeli."""

    class FakeCol:
        def __init__(self, saved):
            self.saved = saved

        async def update_one(self, query, update):
            self.saved["message"] = update["$set"]["provider_error"]

    def test_card_error_gets_actionable_hint(self, monkeypatch):
        saved = {}
        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", self.FakeCol(saved))
        run(insurance_provider._save_provider_error("t1", "Kredi kartı limiti yetersiz."))
        assert "Kredi kartı limiti yetersiz." in saved["message"]
        assert "kartın limitini" in saved["message"].lower()

    def test_unknown_payment_warns_about_double_charge(self, monkeypatch):
        saved = {}
        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", self.FakeCol(saved))
        run(
            insurance_provider._save_provider_error(
                "t1", f"{tamamliyo.PAYMENT_UNKNOWN_MARKER}: yanit alinamadi"
            )
        )
        assert "Mükerrer çekim riski" in saved["message"]
        assert "elle kesin" in saved["message"]

    def test_other_errors_are_left_untouched(self, monkeypatch):
        saved = {}
        monkeypatch.setattr(insurance_provider, "insurance_tasks_col", self.FakeCol(saved))
        run(insurance_provider._save_provider_error("t1", "T.C. Kimlik Numarası hatalı"))
        assert saved["message"] == "T.C. Kimlik Numarası hatalı"
