"""USD -> TRY canli kur yonetimi.

- Birincil kaynak: TCMB gunluk kur bulteni (`kurlar/today.xml`) USD **ForexSelling**
  (doviz satis) degeri. TCMB bulteni is gunleri 15:30'da yayinlanir; hafta sonu ve
  resmi tatillerde son bulten gecerli kalir.
  Yedekler: Yahoo Finance USDTRY=X, doviz.com serbest piyasa satisi, open.er-api.com,
  exchangerate.host; hicbiri olmazsa son bilinen kur.
- Admin panelinden manuel kur ve kur payi (marj %) girilebilir.
- Kur 24 saatte bir tazelenir (lazy refresh: ilk istekte suresi gecmisse guncellenir).
"""

import logging
import re
from datetime import date, datetime, timedelta, timezone

import httpx

from db import settings_col

logger = logging.getLogger(__name__)

FX_KEY = "fx_usd_try"
REFRESH_AFTER_HOURS = 24
FALLBACK_RATE = 41.0  # son cikis noktasi; ilk canli cagri ile guncellenir
DEFAULT_MARGIN_PCT = 2.0

TCMB_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
TCMB_LABEL = "TCMB döviz satış"
IST = timezone(timedelta(hours=3))  # TCMB bulten saati (TRT)
DOVIZ_URL = "https://kur.doviz.com/serbest-piyasa/amerikan-dolari"
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/USDTRY=X?interval=1d&range=1d"
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

SOURCES = [
    (TCMB_LABEL, TCMB_URL),
    ("forex (USD/TRY)", YAHOO_URL),
    ("doviz.com", DOVIZ_URL),
    ("open.er-api.com", "https://open.er-api.com/v6/latest/USD"),
    ("exchangerate.host", "https://api.exchangerate.host/latest?base=USD&symbols=TRY"),
]


def parse_tcmb_xml(xml: str) -> float | None:
    """TCMB gunluk bulteninden USD doviz satis (ForexSelling) kurunu okur."""
    block = re.search(r'<Currency[^>]*Kod="USD".*?</Currency>', xml, re.S)
    if not block:
        return None
    for tag in ("ForexSelling", "BanknoteSelling"):
        found = re.search(rf"<{tag}>\s*([\d.]+)\s*</{tag}>", block.group(0))
        if not found:
            continue
        try:
            value = float(found.group(1))
        except ValueError:
            continue
        if 5 < value < 500:
            return value
    return None


def parse_tcmb_date(xml: str) -> str | None:
    """Bultenin tarihini ISO (YYYY-MM-DD) olarak dondurur."""
    found = re.search(r'Tarih="(\d{2})\.(\d{2})\.(\d{4})"', xml)
    if not found:
        return None
    day, month, year = found.groups()
    return f"{year}-{month}-{day}"


def parse_yahoo_json(payload: dict) -> float | None:
    """Yahoo Finance chart yanitindan anlik USD/TRY kotasyonunu okur."""
    try:
        meta = payload["chart"]["result"][0]["meta"]
    except (KeyError, IndexError, TypeError):
        return None
    for key in ("regularMarketPrice", "previousClose", "chartPreviousClose"):
        value = meta.get(key)
        if value and 5 < float(value) < 500:
            return float(value)
    return None


def parse_doviz_html(html: str) -> float | None:
    """doviz.com sayfasindan USD satis (ask), yoksa son islem (s) kurunu okur."""
    for attr in ("ask", "s"):
        pattern = (
            r'data-socket-key="USD"[^>]*data-socket-attr="' + attr + r'"[^>]*>\s*([\d.,]+)'
        )
        for raw in re.findall(pattern, html):
            try:
                value = float(raw.replace(".", "").replace(",", "."))
            except ValueError:
                continue
            if 5 < value < 500:
                return value
    return None


def _extract_rate(source: str, payload: dict) -> float | None:
    try:
        return float(payload["rates"]["TRY"])
    except Exception:
        return None


def expected_bulletin_date(now: datetime | None = None) -> date:
    """O an gecerli olmasi gereken TCMB bulten tarihi (is gunu 15:30'da yayinlanir)."""
    now = now or datetime.now(IST)
    day = now.date()
    if now.hour < 16:
        day -= timedelta(days=1)
    while day.weekday() >= 5:  # cumartesi/pazar bulten yok
        day -= timedelta(days=1)
    return day


async def fetch_live_rate() -> dict | None:
    """Canli kuru cekmeye calisir; basarisizsa None doner."""
    async with httpx.AsyncClient(
        timeout=10.0, follow_redirects=True, headers={"User-Agent": BROWSER_UA}
    ) as client:
        for source, url in SOURCES:
            try:
                res = await client.get(url)
                res.raise_for_status()
                if url == TCMB_URL:
                    rate = parse_tcmb_xml(res.text)
                elif source == "doviz.com":
                    rate = parse_doviz_html(res.text)
                elif url == YAHOO_URL:
                    rate = parse_yahoo_json(res.json())
                else:
                    rate = _extract_rate(source, res.json())
                if rate and rate > 0:
                    bulletin = parse_tcmb_date(res.text) if url == TCMB_URL else None
                    return {"rate": rate, "source": source, "bulletin_date": bulletin or ""}
            except Exception as exc:
                logger.warning("fx fetch failed (%s): %s", source, exc)
    return None


async def _load_state() -> dict:
    doc = await settings_col.find_one({"key": FX_KEY})
    value = (doc or {}).get("value") or {}
    return {
        "base_rate": float(value.get("base_rate") or 0) or None,
        "manual_rate": value.get("manual_rate"),
        "margin_pct": float(value.get("margin_pct", DEFAULT_MARGIN_PCT)),
        "source": value.get("source", ""),
        "bulletin_date": value.get("bulletin_date", ""),
        "fetched_at": value.get("fetched_at"),
        "updated_at": value.get("updated_at"),
    }


async def _save_state(state: dict) -> None:
    state = {**state, "updated_at": datetime.now(timezone.utc)}
    await settings_col.update_one(
        {"key": FX_KEY}, {"$set": {"key": FX_KEY, "value": state}}, upsert=True
    )


def _is_stale(state: dict) -> bool:
    """Gunluk TCMB bulteni degistiyse (ya da 24 saat gectiyse) kur tazelenir."""
    fetched_at = state.get("fetched_at")
    if not isinstance(fetched_at, datetime):
        return True
    ts = fetched_at if fetched_at.tzinfo else fetched_at.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - ts
    if age > timedelta(hours=REFRESH_AFTER_HOURS):
        return True
    # yedek kaynaktan gelmisse ya da yeni bulten yayinlanmissa saatte bir yeniden dene
    return age > timedelta(hours=1) and str(
        state.get("bulletin_date") or ""
    ) < expected_bulletin_date().isoformat()


async def get_fx(force_refresh: bool = False) -> dict:
    """Etkin kur bilgisini dondurur (gerekirse canli kuru tazeler)."""
    state = await _load_state()
    if force_refresh or state["base_rate"] is None or _is_stale(state):
        live = await fetch_live_rate()
        if live:
            state["base_rate"] = live["rate"]
            state["source"] = live["source"]
            state["bulletin_date"] = live.get("bulletin_date", "")
            state["fetched_at"] = datetime.now(timezone.utc)
            await _save_state(state)
        elif state["base_rate"] is None:
            state["base_rate"] = FALLBACK_RATE
            state["source"] = "fallback"

    manual = state.get("manual_rate")
    if manual:
        effective = float(manual)
        mode = "manual"
    else:
        effective = float(state["base_rate"]) * (1 + state["margin_pct"] / 100.0)
        mode = "live"

    return {
        "base_rate": round(float(state["base_rate"]), 4),
        "manual_rate": float(manual) if manual else None,
        "margin_pct": state["margin_pct"],
        "effective_rate": round(effective, 4),
        "mode": mode,
        "source": state["source"],
        "bulletin_date": state.get("bulletin_date", ""),
        "fetched_at": state["fetched_at"].isoformat()
        if isinstance(state["fetched_at"], datetime)
        else state["fetched_at"],
        "currency_pair": "USD/TRY",
    }


async def update_fx_settings(manual_rate=None, margin_pct=None) -> dict:
    state = await _load_state()
    if margin_pct is not None:
        state["margin_pct"] = max(0.0, min(float(margin_pct), 25.0))
    # manual_rate: 0 / None gonderilirse canli kura donulur
    state["manual_rate"] = float(manual_rate) if manual_rate else None
    await _save_state(state)
    return await get_fx()


def try_price(usd_price: float, rate: float) -> float:
    """USD fiyati TL'ye cevirir, 10 TL'nin katina yuvarlar."""
    raw = float(usd_price) * float(rate)
    return float(int(round(raw / 10.0)) * 10)


async def price_in_try(usd_price: float) -> float:
    fx = await get_fx()
    return try_price(usd_price, fx["effective_rate"])


async def addon_prices_try() -> dict:
    """Ek hizmetlerin (ekspres, sigorta) guncel TL fiyatlari."""
    from content import ADDONS

    fx = await get_fx()
    prices = {}
    for key, meta in ADDONS.items():
        usd = meta.get("price_usd")
        prices[key] = try_price(usd, fx["effective_rate"]) if usd else meta["price"]
    return prices


async def addons_with_fx() -> list:
    """Ek hizmet listesi guncel TL fiyatlariyla."""
    from content import ADDONS

    prices = await addon_prices_try()
    return [{**meta, "price": prices.get(key, meta["price"])} for key, meta in ADDONS.items()]


async def apply_fx_to_visa(visa: dict, rate: float | None = None) -> dict:
    """Vize tipine USD bazli TL fiyati uygular."""
    if rate is None:
        rate = (await get_fx())["effective_rate"]
    out = dict(visa)
    usd = out.get("price_usd")
    if usd:
        out["price"] = try_price(usd, rate)
        out["currency"] = "TRY"
        out["fx_rate"] = rate
    return out


async def apply_fx_to_list(items: list) -> list:
    rate = (await get_fx())["effective_rate"]
    return [await apply_fx_to_visa(i, rate) for i in items]
