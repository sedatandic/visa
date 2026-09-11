"""Sigortambudur B2B Partner API istemcisi (Panacea) — yurtdisi seyahat / vize sigortasi.

Kimlik dogrulama: `POST /auth/token` (clientId + clientSecret) -> Bearer accessToken (1 saat).
Akis: musteri kaydi (TC + dogum tarihi) -> teklif olustur (travel-abroad) -> yanitlari
      bekle (en ucuz SUCCESS secilir) -> policelestir (agency_credit) -> police PDF.
Dokuman: https://documenter.getpostman.com/view/2746369/2sBXwyFmTt
IP yetkilendirmesi zorunludur; whitelist'te olmayan sunucu 401 alir.
"""

import asyncio
import base64
import json
import logging
import os
import secrets
import time

import httpx

logger = logging.getLogger(__name__)

_jitter = secrets.SystemRandom()

DEFAULT_BASE_URL = "https://api.panaceasigorta.com"
PRODUCT = "travel_abroad"
PAYMENT_AGENCY_CREDIT = "agency_credit"
PAYMENT_CARD = "credit_card"
SCOPE_EUROPE = 1
SCOPE_WORLDWIDE = 2
# /countries?region=2 listesinde bulunmayan ulke icin dokumanda 254 ("tum dunya") deniyor
COUNTRY_FALLBACK = 254
COUNTRY_HINTS = ("BIRLESIK ARAP", "BİRLEŞİK ARAP", "UNITED ARAB", "EMIRATES", "EMİRLİK")
RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}
MAX_ATTEMPTS = 3
TOKEN_EARLY_REFRESH = 300  # jeton suresi bitmeden 5 dk once yenilenir
OFFER_TIMEOUT_SECONDS = 120
OFFER_DONE = {"CALCULATED", "COMPLETED"}
OFFER_FAILED = {"ERROR", "FAILED", "CANCELLED", "EXPIRED"}

_token_cache: dict = {"value": "", "until": 0.0}
_token_lock = asyncio.Lock()
_country_cache: dict = {"id": 0, "name": ""}


class SigortambudurError(Exception):
    """Saglayici hatasi; `retryable` gecici hatalari isaretler."""

    def __init__(self, message: str, status: int | None = None, payload=None, retryable: bool = False):
        super().__init__(message)
        self.status = status
        self.payload = payload
        self.retryable = retryable


def base_url() -> str:
    return (os.environ.get("SIGORTAMBUDUR_BASE_URL") or DEFAULT_BASE_URL).strip().rstrip("/")


def client_id() -> str:
    return (os.environ.get("SIGORTAMBUDUR_CLIENT_ID") or "").strip()


def client_secret() -> str:
    return (os.environ.get("SIGORTAMBUDUR_CLIENT_SECRET") or "").strip()


def configured() -> bool:
    return bool(base_url() and client_id() and client_secret())


def payment_method() -> str:
    """Odeme yontemi: agency_credit (acente cari/nakit, varsayilan) veya credit_card."""
    raw = (os.environ.get("SIGORTAMBUDUR_PAYMENT_METHOD") or "").strip().lower()
    return PAYMENT_CARD if raw == PAYMENT_CARD else PAYMENT_AGENCY_CREDIT


def scope() -> int:
    raw = (os.environ.get("SIGORTAMBUDUR_SCOPE") or "").strip()
    return SCOPE_EUROPE if raw == "1" else SCOPE_WORLDWIDE


def _flag(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes"}


def covid_cover() -> bool:
    return _flag("SIGORTAMBUDUR_COVID")


def ski_cover() -> bool:
    return _flag("SIGORTAMBUDUR_SKI")


def _error_message(payload) -> str:
    """{"result":"error","errors": str | [{field,message}]} bicimini tek metne cevirir."""
    if not isinstance(payload, dict):
        return "Sigortambudur servisi beklenmeyen yanıt döndürdü."
    errors = payload.get("errors")
    if isinstance(errors, str) and errors.strip():
        return errors.strip()
    if isinstance(errors, list) and errors:
        parts = [
            f"{item.get('field', '')}: {item.get('message', '')}".strip(": ")
            if isinstance(item, dict)
            else str(item)
            for item in errors
        ]
        # Ayni kural birden fazla kez donebiliyor; tekrarlari ayikla
        unique = list(dict.fromkeys(p for p in parts if p))
        return " · ".join(unique)
    for key in ("message", "error", "detail"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return json.dumps(payload, ensure_ascii=False)[:300]


def _backoff_seconds(attempt: int) -> float:
    return 0.5 * (2**attempt) + _jitter.random() * 0.25


def _payload_of(res) -> dict | list | str:
    try:
        return res.json()
    except ValueError:
        return res.text[:500]


def _accepted(res, data) -> bool:
    return res.status_code < 400 and not (isinstance(data, dict) and data.get("result") == "error")


def _timeout() -> httpx.Timeout:
    return httpx.Timeout(connect=5.0, read=45.0, write=15.0, pool=5.0)


def _headers(token: str | None = None) -> dict:
    headers = {"Accept": "application/json", "Accept-Language": "tr"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def reset_token() -> None:
    _token_cache.update({"value": "", "until": 0.0})


async def token(force: bool = False) -> str:
    """Jetonu alir ve suresi bitmeden yeniler (es zamanli istekler tek jeton paylasir)."""
    async with _token_lock:
        if not force and _token_cache["value"] and time.monotonic() < _token_cache["until"]:
            return _token_cache["value"]
        if not (base_url() and client_id() and client_secret()):
            raise SigortambudurError(
                "Sigortambudur API bilgileri tanımlı değil "
                "(SIGORTAMBUDUR_CLIENT_ID / SIGORTAMBUDUR_CLIENT_SECRET)."
            )
        body = {"clientId": client_id(), "clientSecret": client_secret()}
        async with httpx.AsyncClient(timeout=_timeout()) as client:
            res = await client.post(f"{base_url()}/auth/token", json=body, headers=_headers())
        data = _payload_of(res)
        if not _accepted(res, data) or not isinstance(data, dict) or not data.get("accessToken"):
            raise SigortambudurError(_error_message(data), res.status_code, data)
        expires = int(data.get("expiresIn") or 3600)
        _token_cache.update(
            {"value": data["accessToken"], "until": time.monotonic() + max(30, expires - TOKEN_EARLY_REFRESH)}
        )
        return _token_cache["value"]


async def _request(method: str, path: str, payload: dict | None = None, retry: bool = True) -> dict | list:
    """Jeton yonetimi + 401 yenileme + gecici hatalarda ustel bekleme.

    `retry=False` policelestirme gibi tekrarlanmamasi gereken istekler icindir.
    """
    access = await token()
    url = f"{base_url()}{path}"
    attempts = MAX_ATTEMPTS if retry else 1
    refreshed = False
    async with httpx.AsyncClient(timeout=_timeout()) as client:
        for attempt in range(attempts):
            last_attempt = attempt == attempts - 1
            try:
                res = await client.request(method, url, json=payload, headers=_headers(access))
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if not retry:
                    raise SigortambudurError(
                        f"Sigortambudur yanıtı alınamadı, işlem gerçekleşmiş olabilir ({exc})."
                    ) from exc
                if last_attempt:
                    raise SigortambudurError(
                        f"Sigortambudur servisine ulaşılamadı: {exc}", retryable=True
                    ) from exc
                await asyncio.sleep(_backoff_seconds(attempt))
                continue
            data = _payload_of(res)
            if _accepted(res, data):
                return data
            if res.status_code == 401 and not refreshed:
                refreshed = True
                access = await token(force=True)
                continue
            retryable = retry and res.status_code in RETRYABLE_STATUS
            if not retryable or last_attempt:
                raise SigortambudurError(_error_message(data), res.status_code, data, retryable)
            await asyncio.sleep(_backoff_seconds(attempt))
    raise SigortambudurError("Sigortambudur isteği tamamlanamadı.", retryable=True)


# ------------------------------------------------------------------ tanimlar
async def authorized_providers(product: str = PRODUCT) -> list:
    """Acentenin yetkili oldugu sigorta sirketleri (slug listesi)."""
    data = await _request("GET", f"/authorized-providers?product={product}")
    return data if isinstance(data, list) else []


async def countries(region: int = 2) -> list:
    data = await _request("GET", f"/countries?region={region}")
    if isinstance(data, dict):
        data = data.get("data") or []
    return data if isinstance(data, list) else []


def _matches_uae(name: str) -> bool:
    upper = (name or "").upper()
    return any(hint in upper for hint in COUNTRY_HINTS)


async def country_id() -> int:
    """BAE ulke kodu: .env'de varsa o, yoksa ulke listesinden bulunur (cache'lenir)."""
    fixed = (os.environ.get("SIGORTAMBUDUR_COUNTRY_ID") or "").strip()
    if fixed.isdigit():
        return int(fixed)
    if _country_cache["id"]:
        return _country_cache["id"]
    for row in await countries(2):
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or row.get("countryName") or "")
        if _matches_uae(name):
            found = row.get("id") or row.get("code")
            if str(found).isdigit():
                _country_cache.update({"id": int(found), "name": name})
                return int(found)
    logger.warning("sigortambudur: BAE ulke kodu bulunamadi, %s kullanilacak", COUNTRY_FALLBACK)
    return COUNTRY_FALLBACK


# --------------------------------------------------------------- musteri
async def customer_id(identity_number: str, birthday: str) -> str:
    """TC/YKN + dogum tarihi ile musteri kaydini bulur/olusturur ve id dondurur."""
    data = await _request(
        "POST",
        "/customer-detail",
        {"identityNumber": str(identity_number).strip(), "birthday": str(birthday).strip()},
    )
    found = data.get("id") if isinstance(data, dict) else None
    if not found:
        raise SigortambudurError("Sigortalı kaydı oluşturulamadı (müşteri id yok).", payload=data)
    return str(found)


# ----------------------------------------------------------------- teklif
async def create_offer(insured_ids: list, start: str, end: str) -> str:
    """Grup teklif olusturur ve teklif (offer) id dondurur."""
    body = {
        "offerType": "group",
        "insurerType": "agency",
        "insurerIdNumber": None,
        "reservationNumber": None,
        "insureds": [{"id": str(i)} for i in insured_ids],
        "startDate": start,
        "endDate": end,
        "scope": scope(),
        "country": await country_id(),
        "covidInsurance": covid_cover(),
        "skiInsurance": ski_cover(),
    }
    data = await _request("POST", "/travel-abroad", body)
    offer_id = data.get("id") if isinstance(data, dict) else None
    if not offer_id:
        raise SigortambudurError("Teklif numarası alınamadı.", payload=data)
    return str(offer_id)


async def offer_detail(offer_id: str) -> dict:
    data = await _request("GET", f"/travel-abroad/{offer_id}")
    return data if isinstance(data, dict) else {}


def _premium(row: dict) -> float:
    try:
        return float(row.get("totalPremium"))
    except (TypeError, ValueError):
        return 0.0


def cheapest_response(detail: dict) -> dict:
    """SUCCESS donen sirket yanitlari arasindan en dusuk primi secer."""
    rows = [
        row
        for row in (detail.get("responses") or [])
        if isinstance(row, dict) and row.get("status") == "SUCCESS" and _premium(row) > 0
    ]
    if not rows:
        messages = " · ".join(
            str(r.get("message")) for r in (detail.get("responses") or []) if isinstance(r, dict) and r.get("message")
        )
        raise SigortambudurError(
            f"Sigorta şirketlerinden fiyat dönmedi.{(' ' + messages) if messages else ''}",
            payload=detail,
        )
    return min(rows, key=_premium)


async def wait_for_offer(offer_id: str, timeout_seconds: int = OFFER_TIMEOUT_SECONDS) -> dict:
    """Teklif hesaplanana kadar bekler (artan araliklarla sorgular) ve en ucuz yaniti dondurur."""
    deadline = time.monotonic() + timeout_seconds
    delay = 1.0
    while True:
        detail = await offer_detail(offer_id)
        status = str(detail.get("status") or "").upper()
        if status in OFFER_DONE:
            return cheapest_response(detail)
        if status in OFFER_FAILED:
            raise SigortambudurError(f"Teklif başarısız döndü ({status}).", payload=detail)
        if time.monotonic() >= deadline:
            raise SigortambudurError("Teklif yanıtı zamanında hesaplanmadı.", payload=detail)
        await asyncio.sleep(delay)
        delay = min(8.0, delay * 1.5)


# --------------------------------------------------------------- police
async def issue_policy(response_id: str) -> dict:
    """Secilen sirket yanitini policeye cevirir. Zaman asiminda TEKRARLANMAZ."""
    body = {"paymentMethod": payment_method()}
    logger.info("sigortambudur policelestirme: yanit %s, odeme %s", response_id, payment_method())
    data = await _request("POST", f"/travel-abroad/{response_id}/policy", body, retry=False)
    return data if isinstance(data, dict) else {}


async def policy_detail(policy_id: str) -> dict:
    data = await _request("GET", f"/policies/{policy_id}")
    return data if isinstance(data, dict) else {}


def _pdf_from_value(value) -> bytes | None:
    if not isinstance(value, str) or len(value) < 100:
        return None
    text = value.split(",", 1)[1] if value.startswith("data:application/pdf;base64,") else value
    if text.startswith("%PDF"):
        return text.encode("latin-1", "ignore")
    try:
        raw = base64.b64decode(text, validate=True)
    except (ValueError, base64.binascii.Error):
        return None
    return raw if raw.startswith(b"%PDF") else None


def _find_pdf(node) -> bytes | None:
    if isinstance(node, str):
        return _pdf_from_value(node)
    children = node.values() if isinstance(node, dict) else node if isinstance(node, list) else ()
    for value in children:
        found = _find_pdf(value)
        if found:
            return found
    return None


def _print_paths(policy_id: str) -> list:
    """Police basim yolu: .env'de tanimliysa o, yoksa dokumandaki kaliba gore denenir."""
    custom = (os.environ.get("SIGORTAMBUDUR_PRINT_PATH") or "").strip()
    if custom:
        return [custom.replace("{id}", str(policy_id))]
    doc_type = (os.environ.get("SIGORTAMBUDUR_PRINT_DOC_TYPE") or "policy").strip()
    return [
        f"/print/{policy_id}/document/{doc_type}?type=base64",
        f"/print/{policy_id}/document/{doc_type}",
    ]


async def policy_pdf_bytes(policy_id: str) -> bytes:
    """Police PDF'i: once police detayindaki dokuman, sonra basim (print) servisi denenir."""
    detail = await policy_detail(policy_id)
    found = _find_pdf(detail)
    if found:
        return found

    errors = []
    for path in _print_paths(policy_id):
        try:
            data = await _request("GET", path)
        except SigortambudurError as exc:
            errors.append(f"{path}: {exc}")
            continue
        found = _find_pdf(data)
        if found:
            return found
        errors.append(f"{path}: PDF alanı bulunamadı")
    raise SigortambudurError(
        "Poliçe PDF'i alınamadı; sağlayıcı panelinden indirip elle yükleyin. " + " | ".join(errors[:2])
    )


async def connection_check() -> dict:
    """Panel icin baglanti testi: jeton + yetkili sirketler + BAE ulke kodu."""
    await token(force=True)
    providers = await authorized_providers()
    country = await country_id()
    return {
        "ok": True,
        "base_url": base_url(),
        "payment_method": payment_method(),
        "scope": scope(),
        "country_id": country,
        "country_name": _country_cache.get("name") or "",
        "providers": [
            {"name": row.get("name"), "slug": row.get("slug")}
            for row in providers
            if isinstance(row, dict)
        ],
    }
