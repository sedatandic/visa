"""Iteration 118: Tamamliyo teklif/odeme payload duzeltmelerinin regresyon testleri.

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

    async def fake_request(method, path, payload=None):
        calls.append({"method": method, "path": path, "body": payload})
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
    def test_confirm_payment_body(self, captured):
        params = {"pnrNo": "SV-TEST"}
        run(tamamliyo.confirm_payment(2135825, params))
        body = captured[0]["body"]
        assert body["status_code"] == 100
        assert body["payment_status"] == "Payment Successfully Completed"
        assert body["teklifId"] == 2135825
        assert body["parameters"] == params
        assert captured[0]["path"].endswith("/odeme-onay")

    def test_payment_parameters_has_every_required_field(self):
        task = {"order_reference": "SV-XFG87WZW", "starts_on": "2026-10-07"}
        params = insurance_provider._payment_parameters(task)
        required = {
            "pnrNo",
            "flightNumber",
            "ticketNumber",
            "company",
            "ticketType",
            "departureLocation",
            "arrivalLocation",
            "departureDateTime",
        }
        assert required <= set(params)
        assert all(str(params[key]).strip() for key in required)

    def test_payment_parameters_uses_order_reference_and_start_date(self):
        params = insurance_provider._payment_parameters(
            {"order_reference": "SV-XFG87WZW", "starts_on": "2026-10-07"}
        )
        assert params["pnrNo"] == "SV-XFG87WZW"
        assert params["ticketNumber"] == "SV-XFG87WZW"
        assert params["departureDateTime"].startswith("2026-10-07")
        assert params["arrivalLocation"] == "Dubai"

    def test_payment_parameters_tolerates_missing_task_fields(self):
        params = insurance_provider._payment_parameters({})
        assert params["pnrNo"] == "-"
        assert params["departureDateTime"] == "00:00:00"

    def test_ensure_policy_forwards_parameters(self, monkeypatch):
        seen = {}

        async def fake_confirm(quote_id, parameters):
            seen["quote_id"] = quote_id
            seen["parameters"] = parameters
            return {"success": True}

        async def fake_policy(quote_id):
            return {"data": {"policeNo": "P-1"}}

        async def fake_mark(task_id, step, detail=None):
            seen.setdefault("steps", []).append(step)

        monkeypatch.setattr(tamamliyo, "confirm_payment", fake_confirm)
        monkeypatch.setattr(tamamliyo, "create_policy", fake_policy)
        monkeypatch.setattr(insurance_provider, "_mark_step", fake_mark)

        task = {"id": "t1", "order_reference": "SV-XFG87WZW", "starts_on": "2026-10-07"}
        run(insurance_provider._ensure_policy(task, "2135825", {}))

        assert seen["quote_id"] == "2135825"
        assert seen["parameters"]["pnrNo"] == "SV-XFG87WZW"
        assert seen["steps"] == ["payment_confirm", "policy"]


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
