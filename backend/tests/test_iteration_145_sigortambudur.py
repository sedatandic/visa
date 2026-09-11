"""Iteration 145: Yeni sigorta saglayicisi Sigortambudur (Panacea) B2B API'si baglandi.

Kullanici istegi (2026-06): Tamamliyo iptal edildi, "bu apiyi bagla" (Sigortambudur B2B
Partner API). Kararlar: en ucuz sirket otomatik secilsin, odeme `agency_credit` (acente
cari/nakit), kapsam Tum Dunya (scope 2), Covid/Kayak teminati kapali.

Kapsam:
- Jeton onbellegi, 401'de yenileme, hata bicimi ({"result":"error","errors": str | list}).
- Teklif akisi: musteri kaydi -> teklif -> en ucuz SUCCESS yanit.
- Policelestirme istegi `agency_credit` gonderir ve zaman asiminda TEKRARLANMAZ.
- PDF: base64 / ham PDF / print servisi.
"""

import asyncio
import os
import sys

import httpx
import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import insurance_provider  # noqa: E402
import sigortambudur  # noqa: E402

PDF_BYTES = b"%PDF-1.4 test policy"


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture(autouse=True)
def creds(monkeypatch):
    monkeypatch.setenv("SIGORTAMBUDUR_BASE_URL", "https://api.test.local")
    monkeypatch.setenv("SIGORTAMBUDUR_CLIENT_ID", "cid")
    monkeypatch.setenv("SIGORTAMBUDUR_CLIENT_SECRET", "secret")
    monkeypatch.setenv("SIGORTAMBUDUR_COUNTRY_ID", "82")
    monkeypatch.delenv("SIGORTAMBUDUR_SCOPE", raising=False)
    monkeypatch.delenv("SIGORTAMBUDUR_PAYMENT_METHOD", raising=False)
    monkeypatch.delenv("SIGORTAMBUDUR_COVID", raising=False)
    monkeypatch.delenv("SIGORTAMBUDUR_SKI", raising=False)
    sigortambudur.reset_token()


class FakeAPI:
    """httpx.AsyncClient yerine gecen kayit tutan sahte istemci."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []
        self.token_calls = 0

    def install(self, monkeypatch):
        api = self

        class FakeClient:
            def __init__(self, *_a, **_k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_a):
                return False

            async def post(self, url, json=None, headers=None):
                return await self.request("POST", url, json=json, headers=headers)

            async def request(self, method, url, json=None, headers=None):
                path = url.replace("https://api.test.local", "")
                api.calls.append({"method": method, "path": path, "body": json, "headers": headers or {}})
                if path == "/auth/token":
                    api.token_calls += 1
                handler = api.routes.get(f"{method} {path}") or api.routes.get(path)
                if handler is None:
                    raise AssertionError(f"beklenmeyen istek: {method} {path}")
                status, payload = handler(api) if callable(handler) else handler
                return httpx.Response(status, json=payload, request=httpx.Request(method, url))

        monkeypatch.setattr(sigortambudur.httpx, "AsyncClient", FakeClient)
        return api


TOKEN_OK = (200, {"accessToken": "tok-1", "tokenType": "Bearer", "expiresIn": 3600})


class TestToken:
    def test_token_is_cached_and_sent_as_bearer(self, monkeypatch):
        api = FakeAPI({
            "POST /auth/token": TOKEN_OK,
            "GET /countries?region=2": (200, [{"id": 82, "name": "BİRLEŞİK ARAP EMİRLİKLERİ"}]),
        }).install(monkeypatch)
        run(sigortambudur.countries(2))
        run(sigortambudur.countries(2))
        assert api.token_calls == 1
        assert api.calls[-1]["headers"]["Authorization"] == "Bearer tok-1"
        assert api.calls[-1]["headers"]["Accept-Language"] == "tr"

    def test_expired_token_is_refreshed_on_401(self, monkeypatch):
        state = {"first": True}

        def customer(_api):
            if state["first"]:
                state["first"] = False
                return 401, {"result": "error", "errors": "Unauthorized"}
            return 200, {"id": "cust-1", "nameSurname": "A** B**"}

        api = FakeAPI({"POST /auth/token": TOKEN_OK, "POST /customer-detail": customer}).install(monkeypatch)
        assert run(sigortambudur.customer_id("11111111111", "1990-01-01")) == "cust-1"
        assert api.token_calls == 2

    def test_missing_secret_raises(self, monkeypatch):
        monkeypatch.setenv("SIGORTAMBUDUR_CLIENT_SECRET", "")
        sigortambudur.reset_token()
        assert sigortambudur.configured() is False
        with pytest.raises(sigortambudur.SigortambudurError) as exc:
            run(sigortambudur.token())
        assert "SIGORTAMBUDUR_CLIENT_SECRET" in str(exc.value)


class TestErrors:
    def test_string_error_is_surfaced(self, monkeypatch):
        FakeAPI({
            "POST /auth/token": TOKEN_OK,
            "POST /customer-detail": (400, {"result": "error", "errors": "Girmiş olduğunuz TC/YKN geçersizdir."}),
        }).install(monkeypatch)
        with pytest.raises(sigortambudur.SigortambudurError) as exc:
            run(sigortambudur.customer_id("123", "1990-01-01"))
        assert "TC/YKN geçersizdir" in str(exc.value)

    def test_field_errors_are_joined_without_duplicates(self, monkeypatch):
        FakeAPI({
            "POST /auth/token": TOKEN_OK,
            "POST /customer-detail": (
                400,
                {
                    "result": "error",
                    "errors": [
                        {"field": "identityNumber", "message": "Geçersiz"},
                        {"field": "identityNumber", "message": "Geçersiz"},
                        {"field": "birthday", "message": "Boş olamaz"},
                    ],
                },
            ),
        }).install(monkeypatch)
        with pytest.raises(sigortambudur.SigortambudurError) as exc:
            run(sigortambudur.customer_id("123", ""))
        message = str(exc.value)
        assert message.count("identityNumber") == 1
        assert "birthday: Boş olamaz" in message


class TestOfferFlow:
    def test_offer_body_has_agency_scope_and_country(self, monkeypatch):
        api = FakeAPI({
            "POST /auth/token": TOKEN_OK,
            "POST /travel-abroad": (201, {"id": "offer-1"}),
        }).install(monkeypatch)
        assert run(sigortambudur.create_offer(["c1", "c2"], "2026-07-01", "2026-07-08")) == "offer-1"
        body = api.calls[-1]["body"]
        assert body["offerType"] == "group"
        assert body["insurerType"] == "agency"
        assert body["insureds"] == [{"id": "c1"}, {"id": "c2"}]
        assert body["scope"] == 2  # Tum Dunya
        assert body["country"] == 82
        assert body["covidInsurance"] is False and body["skiInsurance"] is False

    def test_cheapest_success_response_is_selected(self):
        detail = {
            "status": "CALCULATED",
            "responses": [
                {"id": "r1", "status": "SUCCESS", "totalPremium": 240.5, "providerName": "A"},
                {"id": "r2", "status": "SUCCESS", "totalPremium": 180.0, "providerName": "B"},
                {"id": "r3", "status": "ERROR", "totalPremium": 10.0, "providerName": "C"},
            ],
        }
        assert sigortambudur.cheapest_response(detail)["id"] == "r2"

    def test_no_success_response_raises_with_message(self):
        detail = {"status": "CALCULATED", "responses": [{"id": "r1", "status": "ERROR", "message": "Yaş sınırı"}]}
        with pytest.raises(sigortambudur.SigortambudurError) as exc:
            sigortambudur.cheapest_response(detail)
        assert "Yaş sınırı" in str(exc.value)

    def test_wait_for_offer_polls_until_calculated(self, monkeypatch):
        calls = {"n": 0}

        def detail(_api):
            calls["n"] += 1
            if calls["n"] < 2:
                return 200, {"status": "PENDING", "responses": []}
            return 200, {"status": "CALCULATED", "responses": [{"id": "r9", "status": "SUCCESS", "totalPremium": 99}]}

        FakeAPI({"POST /auth/token": TOKEN_OK, "GET /travel-abroad/offer-1": detail}).install(monkeypatch)

        async def no_sleep(*_a):
            return None

        monkeypatch.setattr(sigortambudur.asyncio, "sleep", no_sleep)
        best = run(sigortambudur.wait_for_offer("offer-1", timeout_seconds=5))
        assert best["id"] == "r9" and calls["n"] == 2


class TestPolicy:
    def test_policy_request_uses_agency_credit_and_no_retry(self, monkeypatch):
        api = FakeAPI({
            "POST /auth/token": TOKEN_OK,
            "POST /travel-abroad/r1/policy": (201, {"id": "pol-1", "policyNumber": "100001"}),
        }).install(monkeypatch)
        result = run(sigortambudur.issue_policy("r1"))
        assert result["id"] == "pol-1"
        assert api.calls[-1]["body"] == {"paymentMethod": "agency_credit"}

    def test_policy_timeout_is_not_retried(self, monkeypatch):
        attempts = {"n": 0}

        class TimeoutClient:
            def __init__(self, *_a, **_k):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *_a):
                return False

            async def post(self, url, json=None, headers=None):
                return httpx.Response(200, json=dict(TOKEN_OK[1]), request=httpx.Request("POST", url))

            async def request(self, method, url, json=None, headers=None):
                attempts["n"] += 1
                raise httpx.ReadTimeout("timeout", request=httpx.Request(method, url))

        monkeypatch.setattr(sigortambudur.httpx, "AsyncClient", TimeoutClient)
        with pytest.raises(sigortambudur.SigortambudurError) as exc:
            run(sigortambudur.issue_policy("r1"))
        assert attempts["n"] == 1
        assert "gerçekleşmiş olabilir" in str(exc.value)

    def test_pdf_from_policy_detail_base64(self, monkeypatch):
        import base64

        FakeAPI({
            "POST /auth/token": TOKEN_OK,
            "GET /policies/pol-1": (200, {"policyDocument": base64.b64encode(PDF_BYTES + b"x" * 200).decode()}),
        }).install(monkeypatch)
        data = run(sigortambudur.policy_pdf_bytes("pol-1"))
        assert data.startswith(b"%PDF")

    def test_pdf_falls_back_to_print_service(self, monkeypatch):
        import base64

        FakeAPI({
            "POST /auth/token": TOKEN_OK,
            "GET /policies/pol-2": (200, {"policyNumber": "1", "printStatus": "PENDING"}),
            "GET /print/pol-2/document/policy?type=base64": (
                200,
                {"document": base64.b64encode(PDF_BYTES + b"y" * 200).decode()},
            ),
        }).install(monkeypatch)
        assert run(sigortambudur.policy_pdf_bytes("pol-2")).startswith(b"%PDF")

    def test_pdf_missing_asks_for_manual_upload(self, monkeypatch):
        FakeAPI({
            "POST /auth/token": TOKEN_OK,
            "GET /policies/pol-3": (200, {"policyNumber": "1"}),
            "GET /print/pol-3/document/policy?type=base64": (404, {"result": "error", "errors": "Bulunamadı"}),
            "GET /print/pol-3/document/policy": (404, {"result": "error", "errors": "Bulunamadı"}),
        }).install(monkeypatch)
        with pytest.raises(sigortambudur.SigortambudurError) as exc:
            run(sigortambudur.policy_pdf_bytes("pol-3"))
        assert "elle yükleyin" in str(exc.value)


class TestProviderWiring:
    @pytest.fixture(autouse=True)
    def settings(self, monkeypatch):
        async def empty():
            return {}

        monkeypatch.setattr(insurance_provider, "_settings_value", empty)
        monkeypatch.setenv("INSURANCE_PROVIDER", "sigortambudur")

    def test_pdf_failure_after_policy_warns_that_money_was_charged(self, monkeypatch):
        """Police kesildikten sonra PDF alinamazsa operator tekrar kesmemeli."""

        async def fake_quote(_task, _insured):
            return "offer-1", "resp-1"

        async def fake_policy(_task, _response_id):
            return "pol-77"

        async def fake_find(_query):
            return {"id": "t1"}

        async def boom(_policy_id):
            raise sigortambudur.SigortambudurError("Poliçe PDF'i alınamadı; elle yükleyin.")

        monkeypatch.setattr(insurance_provider, "_sigortambudur_quote", fake_quote)
        monkeypatch.setattr(insurance_provider, "_sigortambudur_policy", fake_policy)
        monkeypatch.setattr(insurance_provider.insurance_tasks_col, "find_one", fake_find)
        monkeypatch.setattr(insurance_provider.sigortambudur, "policy_pdf_bytes", boom)

        with pytest.raises(sigortambudur.SigortambudurError) as exc:
            run(insurance_provider._issue_with_sigortambudur({"id": "t1"}, []))
        message = str(exc.value)
        assert "ücret çekildi" in message and "pol-77" in message

    def test_sigortambudur_is_active_and_api_enabled(self):
        assert run(insurance_provider.active_provider()) == "sigortambudur"
        assert run(insurance_provider.api_enabled()) is True

    def test_missing_secret_falls_back_to_manual_issue(self, monkeypatch):
        monkeypatch.setenv("SIGORTAMBUDUR_CLIENT_SECRET", "")

        async def fake_find(_query):
            return {"id": "t1", "status": "pending"}

        monkeypatch.setattr(insurance_provider.insurance_tasks_col, "find_one", fake_find)
        result = run(insurance_provider.issue_via_provider("t1", "https://x.test"))
        assert result["manual"] is True
