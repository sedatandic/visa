"""USD -> TRY canli kur yonetimi.

- Kur kaynagi: open.er-api.com (anahtarsiz, ucretsiz). Basarisiz olursa
  exchangerate.host denenir; ikisi de basarisiz olursa son bilinen kur kullanilir.
- Admin panelinden manuel kur ve kur payi (marj %) girilebilir.
- Kur 24 saatte bir tazelenir (lazy refresh: ilk istekte suresi gecmisse guncellenir).
"""

import logging
from datetime import datetime, timedelta, timezone

import httpx

from db import settings_col

logger = logging.getLogger(__name__)

FX_KEY = "fx_usd_try"
REFRESH_AFTER_HOURS = 24
FALLBACK_RATE = 41.0  # son cikis noktasi; ilk canli cagri ile guncellenir
DEFAULT_MARGIN_PCT = 2.0

SOURCES = [
    ("open.er-api.com", "https://open.er-api.com/v6/latest/USD"),
    ("exchangerate.host", "https://api.exchangerate.host/latest?base=USD&symbols=TRY"),
]


def _extract_rate(source: str, payload: dict) -> float | None:
    try:
        if source == "open.er-api.com":
            return float(payload["rates"]["TRY"])
        return float(payload["rates"]["TRY"])
    except Exception:
        return None


async def fetch_live_rate() -> dict | None:
    """Canli kuru cekmeye calisir; basarisizsa None doner."""
    async with httpx.AsyncClient(timeout=8.0) as client:
        for source, url in SOURCES:
            try:
                res = await client.get(url)
                res.raise_for_status()
                rate = _extract_rate(source, res.json())
                if rate and rate > 0:
                    return {"rate": rate, "source": source}
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
        "fetched_at": value.get("fetched_at"),
        "updated_at": value.get("updated_at"),
    }


async def _save_state(state: dict) -> None:
    state = {**state, "updated_at": datetime.now(timezone.utc)}
    await settings_col.update_one(
        {"key": FX_KEY}, {"$set": {"key": FX_KEY, "value": state}}, upsert=True
    )


def _is_stale(fetched_at) -> bool:
    if not isinstance(fetched_at, datetime):
        return True
    ts = fetched_at if fetched_at.tzinfo else fetched_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - ts > timedelta(hours=REFRESH_AFTER_HOURS)


async def get_fx(force_refresh: bool = False) -> dict:
    """Etkin kur bilgisini dondurur (gerekirse canli kuru tazeler)."""
    state = await _load_state()
    if force_refresh or state["base_rate"] is None or _is_stale(state["fetched_at"]):
        live = await fetch_live_rate()
        if live:
            state["base_rate"] = live["rate"]
            state["source"] = live["source"]
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
