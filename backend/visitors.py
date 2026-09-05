"""Ziyaretci takibi: IP -> sehir/ulke cozumleme (ipwho.is) + Mongo onbellek.

- Gercek istemci IP'si ingress arkasindan `X-Forwarded-For` ile alinir.
- Ozel/loopback IP'ler saglayiciya gonderilmez.
- Cozumleme istek akisini bloklamaz (FastAPI BackgroundTasks).
"""

import ipaddress
import logging
import uuid
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import Request

from db import ip_geo_col, visits_col

logger = logging.getLogger(__name__)

GEO_TTL_DAYS = 30
GEO_URL = "https://ipwho.is/{ip}"
GEO_FIELDS = "success,message,ip,country,country_code,region,city,latitude,longitude,connection"
BOT_MARKERS = (
    "bot", "crawl", "spider", "slurp", "curl", "wget", "python-requests",
    "httpx", "headlesschrome", "lighthouse", "pingdom", "uptime", "monitor",
)


def _first_public(candidates: list[str]) -> str | None:
    for raw in candidates:
        try:
            ip = ipaddress.ip_address(raw.strip())
        except ValueError:
            continue
        if not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast):
            return str(ip)
    return None


def client_ip(request: Request) -> str | None:
    """Ingress zincirindeki ilk halka (istemci) IP'sini dondurur."""
    chain = [p for p in (request.headers.get("x-forwarded-for") or "").split(",") if p.strip()]
    if request.headers.get("cf-connecting-ip"):
        chain.insert(0, request.headers["cf-connecting-ip"])
    if request.client:
        chain.append(request.client.host)
    return _first_public(chain) or (chain[0].strip() if chain else None)


def is_bot(user_agent: str) -> bool:
    ua = (user_agent or "").lower()
    return not ua or any(marker in ua for marker in BOT_MARKERS)


async def lookup_geo(ip: str) -> dict:
    """Onbellekten veya ipwho.is'ten sehir/ulke bilgisi dondurur."""
    cached = await ip_geo_col.find_one({"ip": ip}, {"_id": 0})
    if cached:
        return {k: cached.get(k) for k in ("city", "region", "country", "country_code", "isp")}

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(4.0, connect=2.0)) as http:
            res = await http.get(GEO_URL.format(ip=ip), params={"fields": GEO_FIELDS})
        if res.status_code != 200:
            return {}
        data = res.json()
        if data.get("success") is False:
            return {}
        geo = {
            "city": data.get("city") or "",
            "region": data.get("region") or "",
            "country": data.get("country") or "",
            "country_code": data.get("country_code") or "",
            "isp": ((data.get("connection") or {}).get("isp") or ""),
        }
    except (httpx.HTTPError, ValueError) as exc:
        logger.info("ip geo lookup failed for %s: %s", ip, exc)
        return {}

    now = datetime.now(timezone.utc)
    await ip_geo_col.update_one(
        {"ip": ip},
        {"$set": {**geo, "ip": ip, "updated_at": now, "expires_at": now + timedelta(days=GEO_TTL_DAYS)}},
        upsert=True,
    )
    return geo


async def record_visit(ip: str | None, path: str, referrer: str, user_agent: str) -> None:
    """Ziyareti kaydeder; cografi bilgi bulunursa birlikte yazilir."""
    geo = await lookup_geo(ip) if ip else {}
    await visits_col.insert_one(
        {
            "id": str(uuid.uuid4()),
            "ip": ip or "",
            "path": path[:300],
            "referrer": (referrer or "")[:300],
            "user_agent": (user_agent or "")[:300],
            "bot": is_bot(user_agent),
            "city": geo.get("city", ""),
            "region": geo.get("region", ""),
            "country": geo.get("country", ""),
            "country_code": geo.get("country_code", ""),
            "isp": geo.get("isp", ""),
            "created_at": datetime.now(timezone.utc),
        }
    )


async def visit_summary(days: int = 30) -> dict:
    """Yonetici paneli icin ozet: gunluk sayim, ulke/sehir/sayfa kirilimi."""
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    base = {"bot": False, "created_at": {"$gte": since}}

    async def top(field: str, limit: int = 8) -> list[dict]:
        pipeline = [
            {"$match": {**base, field: {"$nin": ["", None]}}},
            {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        rows = await visits_col.aggregate(pipeline).to_list(limit)
        return [{"label": r["_id"], "count": r["count"]} for r in rows]

    daily_rows = await visits_col.aggregate(
        [
            {"$match": base},
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1},
                    "ips": {"$addToSet": "$ip"},
                }
            },
            {"$sort": {"_id": 1}},
        ]
    ).to_list(400)

    today = now.strftime("%Y-%m-%d")
    return {
        "days": days,
        "total": await visits_col.count_documents(base),
        "total_today": next((r["count"] for r in daily_rows if r["_id"] == today), 0),
        "unique_visitors": len(
            await visits_col.distinct("ip", {**base, "ip": {"$nin": ["", None]}})
        ),
        "unique_today": len(
            [ip for r in daily_rows if r["_id"] == today for ip in r["ips"] if ip]
        ),
        "bots": await visits_col.count_documents({"bot": True, "created_at": {"$gte": since}}),
        "daily": [{"date": r["_id"], "count": r["count"], "unique": len([i for i in r["ips"] if i])} for r in daily_rows],
        "countries": await top("country"),
        "cities": await top("city"),
        "pages": await top("path", 10),
        "referrers": await top("referrer", 6),
    }
