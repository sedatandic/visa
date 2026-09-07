"""Tamamliyo Partner Travel API v3 istemcisi (yurtdisi seyahat saglik sigortasi).

Kimlik dogrulama: partner token, `token` HTTP header'inda gonderilir.
Akis: fiyat-al -> teklif-olustur -> odeme-onay (cari tahsilat) -> police-olustur -> police-pdf
Dokumantasyon kopyasi: /app/memory/tamamliyo/travel_api.txt
"""

import asyncio
import base64
import logging
import os
import re
import secrets

import httpx

logger = logging.getLogger(__name__)

# Deneme araligindaki jitter icin kriptografik guvenli kaynak
_jitter = secrets.SystemRandom()

PATH = "/partner/v3/seyahat-saglik-sigortasi"
PRODUCT = "yurtdisi-seyahat"
URUN_ID = 141  # "Yurt Disi Saglik Destek Paketi" - 30.000 EUR + vize teminati
RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}
MAX_ATTEMPTS = 3
PDF_MAGIC = "JVBERi"


class TamamliyoError(Exception):
    """Saglayici hatasi; `retryable` gecici hatalari isaretler."""

    def __init__(self, message: str, status: int | None = None, payload=None, retryable: bool = False):
        super().__init__(message)
        self.status = status
        self.payload = payload
        self.retryable = retryable


def base_url() -> str:
    return (os.environ.get("TAMAMLIYO_BASE_URL") or "").strip().rstrip("/")


def token() -> str:
    return (os.environ.get("TAMAMLIYO_TOKEN") or "").strip()


def configured() -> bool:
    return bool(base_url() and token())


def auto_issue_enabled() -> bool:
    return (os.environ.get("TAMAMLIYO_AUTO_ISSUE") or "").strip().lower() in {"1", "true", "yes"}


def _error_message(payload) -> str:
    if isinstance(payload, dict):
        for key in ("message", "mesaj", "hata", "error", "authentication", "errors"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, list) and value:
                return str(value[0])
    return "Tamamliyo servisi beklenmeyen yanit dondurdu."


async def _request(method: str, path: str, payload: dict | None = None) -> dict:
    if not configured():
        raise TamamliyoError("Tamamliyo API bilgileri tanimli degil (TAMAMLIYO_BASE_URL/TOKEN).")
    url = f"{base_url()}{path}"
    headers = {"token": token(), "Accept": "application/json"}
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=30.0, write=15.0, pool=5.0)) as client:
        for attempt in range(MAX_ATTEMPTS):
            try:
                res = await client.request(method, url, json=payload, headers=headers)
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt == MAX_ATTEMPTS - 1:
                    raise TamamliyoError(f"Tamamliyo servisine ulasilamadi: {exc}", retryable=True) from exc
                await asyncio.sleep(0.5 * (2**attempt) + _jitter.random() * 0.25)
                continue
            try:
                data = res.json()
            except ValueError:
                data = {"raw": res.text[:500]}
            if res.status_code < 400 and (not isinstance(data, dict) or data.get("success") is not False):
                if isinstance(data, dict) and data.get("authentication"):
                    raise TamamliyoError(str(data["authentication"]), res.status_code, data)
                return data
            retryable = res.status_code in RETRYABLE_STATUS
            if not retryable or attempt == MAX_ATTEMPTS - 1:
                raise TamamliyoError(_error_message(data), res.status_code, data, retryable)
            await asyncio.sleep(0.5 * (2**attempt) + _jitter.random() * 0.25)
    raise TamamliyoError("Tamamliyo istegi tamamlanamadi.", retryable=True)


async def product_codes() -> dict:
    return await _request("GET", f"{PATH}/urun-kodlari")


async def price(insured_count: int, start: str, end: str, urun_id: int = URUN_ID) -> dict:
    """Kisisel veri gondermeden fiyat sorgular."""
    body = {
        "sigortaliSayisi": int(insured_count),
        "baslangicTarihi": start,
        "bitisTarihi": end,
        "urun": PRODUCT,
        "urun_id": urun_id,
    }
    return await _request("POST", f"{PATH}/fiyat-al", body)


async def create_quote(
    insured: list, start: str, end: str, email: str, phone: str, urun_id: int = URUN_ID
) -> dict:
    """Sigortali listesiyle teklif olusturur; yanittaki teklifId saklanmalidir."""
    people = [{"tcKimlikNo": p["tc_kimlik_no"], "dogumTarihi": p["birth_date"]} for p in insured]
    body = {
        "sigortaEttiren": people[0],
        "sigortali": people,
        "baslangicTarihi": start,
        "bitisTarihi": end,
        "email": email,
        "gsmNo": phone,
        "urun": PRODUCT,
        "urun_id": urun_id,
    }
    return await _request("POST", f"{PATH}/teklif-olustur", body)


async def confirm_payment(quote_id, parameters: dict | None = None) -> dict:
    """Cari/acik tahsilat onayi: parayi biz tahsil ettik bilgisini gecer."""
    body = {
        "status_code": 100,
        "payment_status": "Payment Successfully Completed",
        "teklifId": quote_id,
        "parameters": parameters or {},
    }
    return await _request("POST", f"{PATH}/odeme-onay", body)


async def create_policy(quote_id) -> dict:
    return await _request("POST", f"{PATH}/police-olustur", {"teklifId": quote_id})


async def policy_pdf(quote_id) -> dict:
    return await _request("POST", f"{PATH}/police-pdf", {"teklifId": quote_id})


async def quote_info(quote_id) -> dict:
    return await _request("POST", f"{PATH}/teklif-bilgileri", {"teklifId": quote_id})


def _find_pdf_value(node) -> str | None:
    """Yanit icinde base64 PDF ya da PDF baglantisi arar (alan adi surumle degisebiliyor)."""
    if isinstance(node, str):
        text = node.strip()
        if text.startswith(PDF_MAGIC) or text.startswith("%PDF"):
            return text
        if re.match(r"^https?://\S+", text) and (".pdf" in text.lower() or "police" in text.lower()):
            return text
        return None
    if isinstance(node, dict):
        for value in node.values():
            found = _find_pdf_value(value)
            if found:
                return found
    if isinstance(node, list):
        for value in node:
            found = _find_pdf_value(value)
            if found:
                return found
    return None


async def fetch_policy_bytes(payload: dict) -> bytes:
    """police-pdf yanitini PDF baytlarina cevirir (base64 ya da indirme baglantisi)."""
    value = _find_pdf_value(payload)
    if not value:
        raise TamamliyoError("Poliçe PDF'i yanıtta bulunamadı.", payload=payload)
    if value.startswith("%PDF"):
        return value.encode("latin-1", "ignore")
    if value.startswith("http"):
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            res = await client.get(value)
            res.raise_for_status()
            return res.content
    return base64.b64decode(value)
