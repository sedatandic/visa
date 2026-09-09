"""Tamamliyo Partner Travel API v3 istemcisi (yurtdisi seyahat saglik sigortasi).

Kimlik dogrulama: partner token, `token` HTTP header'inda gonderilir.
Akis: fiyat-al -> teklif-olustur -> odeme-yap (cari bakiye odemeTipi=3, kart odemeTipi=2)
      -> police-olustur -> police-pdf
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
def _configured_urun_id() -> int:
    """Urun kodu .env'den okunur (saglayici partner hesabina gore degisebilir)."""
    raw = (os.environ.get("TAMAMLIYO_URUN_ID") or "").strip()
    return int(raw) if raw.isdigit() else 141


# 141 "Yurt Disi Saglik Destek Paketi" (30.000 EUR + vize teminati) — varsayilan
URUN_ID = _configured_urun_id()
# Gidilecek ulke kodu (Tamamliyo /partner/v1/countries): 784 = Birlesik Arap Emirlikleri.
# teklif-olustur bu alani zorunlu tutuyor (HATA_2: "ulkeKodu gonderilmesi zorunludur").
ULKE_KODU_BAE = 784
PAYMENT_TYPE_CARD = "2"  # odeme-yap: 2 = kurumsal kartla dogrudan cekim
PAYMENT_TYPE_BALANCE = "3"  # odeme-yap: 3 = partner cari bakiyesinden dusum (varsayilan)
# Kart alanlari <-> .env anahtarlari (kart bilgisi yalnizca ortam degiskeninde tutulur)
CARD_ENV = {
    "krediKartiNo": "TAMAMLIYO_CARD_NUMBER",
    "krediKartiBitisTarihi": "TAMAMLIYO_CARD_EXPIRY",
    "krediKartiCvv": "TAMAMLIYO_CARD_CVV",
    "krediKartiAd": "TAMAMLIYO_CARD_NAME",
    "krediKartiSoyad": "TAMAMLIYO_CARD_SURNAME",
}
# Odeme isteginde zaman asimi olursa cekim yapilmis olabilir: istek tekrarlanmaz,
# gorev bu isaretle operator incelemesine dusurulur.
PAYMENT_UNKNOWN_MARKER = "ODEME_DURUMU_BILINMIYOR"
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
        # Tamamliyo hatalari `data.errorMessage` altinda dondurur (errorCode: HATA_*)
        inner = payload.get("data")
        if isinstance(inner, dict):
            detail = inner.get("errorMessage") or inner.get("errorCode")
            if isinstance(detail, str) and detail.strip():
                return detail.strip()
        for key in ("errorMessage", "errorCode", "message", "mesaj", "hata", "error", "authentication", "errors"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, list) and value:
                return str(value[0])
    return "Tamamliyo servisi beklenmeyen yanit dondurdu."


async def _request(method: str, path: str, payload: dict | None = None, retry: bool = True) -> dict:
    if not configured():
        raise TamamliyoError("Tamamliyo API bilgileri tanimli degil (TAMAMLIYO_BASE_URL/TOKEN).")
    url = f"{base_url()}{path}"
    headers = {"token": token(), "Accept": "application/json"}
    attempts = MAX_ATTEMPTS if retry else 1
    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=5.0, read=30.0, write=15.0, pool=5.0)) as client:
        for attempt in range(attempts):
            try:
                res = await client.request(method, url, json=payload, headers=headers)
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt == attempts - 1:
                    if not retry:
                        raise TamamliyoError(
                            f"{PAYMENT_UNKNOWN_MARKER}: Tamamliyo yaniti alinamadi, cekim yapilmis olabilir ({exc})."
                        ) from exc
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
            retryable = retry and res.status_code in RETRYABLE_STATUS
            if not retryable or attempt == attempts - 1:
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
        "ulkeKodu": ULKE_KODU_BAE,
    }
    return await _request("POST", f"{PATH}/teklif-olustur", body)


def payment_type() -> str:
    """Odeme tipi .env'den okunur: 3 = cari bakiye (varsayilan), 2 = kurumsal kart."""
    raw = (os.environ.get("TAMAMLIYO_PAYMENT_TYPE") or "").strip()
    return PAYMENT_TYPE_CARD if raw == PAYMENT_TYPE_CARD else PAYMENT_TYPE_BALANCE


def balance_mode() -> bool:
    """Odeme cari bakiyeden mi dusuluyor (kart bilgisi gerekmez)?"""
    return payment_type() == PAYMENT_TYPE_BALANCE


def card_configured() -> bool:
    """Odeme yapilabilir durumda mi? Cari bakiye modunda kart bilgisi gerekmez."""
    if balance_mode():
        return True
    return all((os.environ.get(env) or "").strip() for env in CARD_ENV.values())


def card_hint() -> str:
    """Panelde gosterilecek maskeli kart bilgisi (son 4 hane)."""
    if balance_mode():
        return ""
    number = re.sub(r"\D", "", os.environ.get(CARD_ENV["krediKartiNo"]) or "")
    return f"**** {number[-4:]}" if len(number) >= 4 else ""


def _card_fields() -> dict:
    missing = [env for env in CARD_ENV.values() if not (os.environ.get(env) or "").strip()]
    if missing:
        raise TamamliyoError(
            "Tamamliyo ödeme kartı tanımlı değil (" + ", ".join(missing) + ")."
        )
    fields = {field: (os.environ.get(env) or "").strip() for field, env in CARD_ENV.items()}
    fields["krediKartiNo"] = re.sub(r"\s", "", fields["krediKartiNo"])
    return fields


async def pay_for_quote(quote_id) -> dict:
    """Teklifin odemesini yapar (`odeme-yap`): cari bakiye (3) ya da kurumsal kart (2).

    Kart modunda kart bilgileri yalnizca .env'den okunur; log'lanmaz, veritabanina
    yazilmaz. Zaman asiminda cekim gerceklesmis olabileceginden istek TEKRARLANMAZ.
    """
    body = {"odemeTipi": payment_type(), "teklifId": quote_id}
    if not balance_mode():
        body |= _card_fields()
    logger.info(
        "tamamliyo odeme istegi: teklif %s, tip %s %s", quote_id, payment_type(), card_hint()
    )
    return await _request("POST", f"{PATH}/odeme-yap", body, retry=False)


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
