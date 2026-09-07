"""Gunluk yonetici ozeti e-postasi.

Her sabah 08:00 (Europe/Istanbul) bir onceki gunun basvurulari, tahsilati,
ekstra satislari ve dikkat gerektiren kayitlari tek e-postada ozetlenir.
Hareket olmayan gunlerde de kisa bir ozet gider (otomasyonun calistigi gorulsun).
"""

import asyncio
import logging
import os
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from db import applications_col, cart_snapshots_col, insurance_tasks_col, orders_col, settings_col
from doc_reminders import missing_documents
from emailer import daily_digest_html, money, send_email

logger = logging.getLogger(__name__)

TZ = ZoneInfo("Europe/Istanbul")
SEND_HOUR = 8  # yerel saat
CHECK_INTERVAL_SECONDS = 10 * 60
SETTINGS_KEY = "daily_digest"

OPEN_STATUSES = ["submitted", "documents_pending", "payment_pending", "reviewing"]
KIND_LABELS = {
    "insurance": "Seyahat sigortası",
    "esim": "Dubai eSIM",
    "tour": "Dubai turu",
    "visa": "Vize",
}
METHOD_LABELS = {"card": "Kart", "bank_transfer": "Havale/EFT"}
MONTHS_TR = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
]
DAYS_TR = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]


def local_now() -> datetime:
    return datetime.now(TZ)


def day_bounds(day: date) -> tuple[datetime, datetime]:
    """Yerel gunun UTC baslangic ve bitis sinirlari."""
    start_local = datetime.combine(day, time.min, tzinfo=TZ)
    return start_local.astimezone(timezone.utc), (start_local + timedelta(days=1)).astimezone(timezone.utc)


def day_label(day: date) -> str:
    return f"{day.day} {MONTHS_TR[day.month - 1]} {day.year}, {DAYS_TR[day.weekday()]}"


def _amount(doc: dict) -> float:
    """Basvuru veya siparis tutari."""
    pricing = doc.get("pricing") or {}
    return float(pricing.get("total") or doc.get("price") or (doc.get("payment") or {}).get("amount") or 0)


def _method(doc: dict) -> str:
    return (doc.get("payment") or {}).get("method") or "bank_transfer"


def _application_rows(apps: list) -> list:
    rows = []
    for app in apps:
        rows.append(
            {
                "reference": app.get("reference_code") or "",
                "name": (app.get("contact") or {}).get("full_name") or "",
                "visa": app.get("visa_type_name") or "",
                "travelers": len(app.get("travelers") or []),
                "total": _amount(app),
                "payment_status": (app.get("payment") or {}).get("status") or "pending",
            }
        )
    return rows


def _visa_breakdown(apps: list) -> list:
    counts: dict[str, int] = {}
    for app in apps:
        for traveler in app.get("travelers") or []:
            label = traveler.get("visa_short_name") or traveler.get("visa_type_name") or "Bilinmiyor"
            counts[label] = counts.get(label, 0) + 1
    return sorted(
        ({"label": label, "count": count} for label, count in counts.items()),
        key=lambda row: -row["count"],
    )


def _revenue(paid_docs: list) -> dict:
    by_method: dict[str, dict] = {}
    total = 0.0
    for doc in paid_docs:
        amount = _amount(doc)
        total += amount
        method = _method(doc)
        bucket = by_method.setdefault(
            method, {"label": METHOD_LABELS.get(method, method), "count": 0, "amount": 0.0}
        )
        bucket["count"] += 1
        bucket["amount"] = round(bucket["amount"] + amount, 2)
    return {
        "total": round(total, 2),
        "count": len(paid_docs),
        "by_method": sorted(by_method.values(), key=lambda row: -row["amount"]),
    }


def _extras_sources(orders: list, apps: list):
    """Ekstra satislarin geldigi tum kalemler (siparisler + basvuru sepetleri)."""
    for order in orders:
        yield from order.get("items") or []
    for app in apps:
        yield from (app.get("pricing") or {}).get("store_items") or []


def _extras_breakdown(orders: list, apps: list) -> list:
    """Ekstra satislari urun turune gore toplar (adet + tutar)."""
    buckets: dict[str, dict] = {}
    for item in _extras_sources(orders, apps):
        kind = item.get("kind") or "diger"
        bucket = buckets.setdefault(
            kind, {"kind": kind, "label": KIND_LABELS.get(kind, kind), "quantity": 0, "amount": 0.0}
        )
        bucket["quantity"] += max(int(item.get("quantity") or 0), 0)
        bucket["amount"] = round(bucket["amount"] + float(item.get("total") or 0), 2)
    return sorted(buckets.values(), key=lambda row: -row["amount"])


async def _attention() -> dict:
    """Gune bagli olmayan, su an bekleyen isler."""
    open_apps = await applications_col.find({"status": {"$in": OPEN_STATUSES}}).to_list(500)
    missing_docs = [app for app in open_apps if missing_documents(app)]
    awaiting_apps = await applications_col.find({"payment.status": "awaiting_transfer"}).to_list(500)
    awaiting_orders = await orders_col.find({"payment.status": "awaiting_transfer"}).to_list(500)
    carts = await cart_snapshots_col.find({"active": True}).to_list(500)
    open_carts = [c for c in carts if c.get("items")]
    return {
        "missing_documents": {
            "count": len(missing_docs),
            "references": [a.get("reference_code") or "" for a in missing_docs[:10]],
        },
        "awaiting_transfer": {
            "count": len(awaiting_apps) + len(awaiting_orders),
            "amount": round(sum(_amount(d) for d in awaiting_apps + awaiting_orders), 2),
        },
        "abandoned_carts": {
            "count": len(open_carts),
            "amount": round(sum(float(c.get("price") or 0) for c in open_carts), 2),
        },
    }


async def collect_digest(day: date | None = None) -> dict:
    """Verilen yerel gun icin ozet verisini toplar (varsayilan: dun)."""
    target = day or (local_now().date() - timedelta(days=1))
    start, end = day_bounds(target)
    month_start, _ = day_bounds(target.replace(day=1))
    month_end = end

    apps = await applications_col.find({"created_at": {"$gte": start, "$lt": end}}).to_list(1000)
    orders = await orders_col.find({"created_at": {"$gte": start, "$lt": end}, "source": "store"}).to_list(1000)
    paid_apps = await applications_col.find(
        {"payment.status": "paid", "payment.paid_at": {"$gte": start, "$lt": end}}
    ).to_list(1000)
    paid_orders = await orders_col.find(
        {"payment.status": "paid", "payment.paid_at": {"$gte": start, "$lt": end}}
    ).to_list(1000)

    month_apps = await applications_col.count_documents({"created_at": {"$gte": month_start, "$lt": month_end}})
    month_paid_apps = await applications_col.find(
        {"payment.status": "paid", "payment.paid_at": {"$gte": month_start, "$lt": month_end}}
    ).to_list(3000)
    month_paid_orders = await orders_col.find(
        {"payment.status": "paid", "payment.paid_at": {"$gte": month_start, "$lt": month_end}}
    ).to_list(3000)

    revenue = _revenue(paid_apps + paid_orders)
    extras = _extras_breakdown(orders, apps)
    return {
        "day": target.isoformat(),
        "day_label": day_label(target),
        "applications": {
            "count": len(apps),
            "travelers": sum(len(a.get("travelers") or []) for a in apps),
            "amount": round(sum(_amount(a) for a in apps), 2),
            "by_visa": _visa_breakdown(apps),
            "rows": _application_rows(apps),
        },
        "orders": {"count": len(orders), "amount": round(sum(_amount(o) for o in orders), 2)},
        "revenue": revenue,
        "extras": extras,
        "attention": await _attention(),
        "month": {
            "label": f"{MONTHS_TR[target.month - 1]} {target.year}",
            "applications": month_apps,
            "revenue": round(sum(_amount(d) for d in month_paid_apps + month_paid_orders), 2),
        },
        "has_activity": bool(apps or orders or revenue["count"]),
        "admin_url": f"{(os.environ.get('PUBLIC_SITE_URL') or '').rstrip('/')}/admin",
    }


def _greeting(hour: int) -> str:
    if hour < 11:
        return "Günaydın"
    return "İyi günler" if hour < 18 else "İyi akşamlar"


async def _upcoming_departures(today: date, days: int = 7) -> dict:
    """Onumuzdeki 7 gun icinde gidisi olan ve hala acik olan basvurular."""
    docs = await applications_col.find(
        {
            "status": {"$in": OPEN_STATUSES},
            "travel.arrival_date": {
                "$gte": today.isoformat(),
                "$lte": (today + timedelta(days=days)).isoformat(),
            },
        }
    ).to_list(200)
    return {
        "count": len(docs),
        "references": [d.get("reference_code") or "" for d in docs[:10]],
    }


async def today_overview() -> dict:
    """Panel karsilama karti: bugunun ozeti + su an bekleyen isler."""
    now = local_now()
    today = now.date()
    start, end = day_bounds(today)
    window = {"$gte": start, "$lt": end}

    apps = await applications_col.find({"created_at": window}).to_list(500)
    orders = await orders_col.find({"created_at": window, "source": "store"}).to_list(500)
    paid_apps = await applications_col.find(
        {"payment.status": "paid", "payment.paid_at": window}
    ).to_list(500)
    paid_orders = await orders_col.find(
        {"payment.status": "paid", "payment.paid_at": window}
    ).to_list(500)

    attention = await _attention()
    attention["policy_tasks"] = {"count": await insurance_tasks_col.count_documents({"status": "pending"})}
    upcoming = await _upcoming_departures(today)
    revenue = _revenue(paid_apps + paid_orders)
    pending_total = (
        attention["missing_documents"]["count"]
        + attention["awaiting_transfer"]["count"]
        + attention["abandoned_carts"]["count"]
        + attention["policy_tasks"]["count"]
    )
    return {
        "day": today.isoformat(),
        "day_label": day_label(today),
        "greeting": _greeting(now.hour),
        "applications_today": len(apps),
        "travelers_today": sum(len(a.get("travelers") or []) for a in apps),
        "orders_today": len(orders),
        "revenue_today": revenue,
        "attention": attention,
        "upcoming_departures": upcoming,
        "pending_total": pending_total,
        "has_activity": bool(apps or orders or revenue["count"]),
    }


async def _last_sent_day() -> str:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    return ((doc or {}).get("value") or {}).get("last_sent_day") or ""


async def _mark_sent(day: date) -> None:
    await settings_col.update_one(
        {"key": SETTINGS_KEY},
        {
            "$set": {
                "value.last_sent_day": day.isoformat(),
                "value.last_sent_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        upsert=True,
    )


async def send_daily_digest(day: date | None = None, force: bool = False) -> dict:
    """Ozeti admin adresine gonderir; ayni gun icin tekrar gondermez (force haric)."""
    admin_email = (os.environ.get("ADMIN_EMAIL") or "").strip()
    if not admin_email:
        return {"sent": False, "reason": "ADMIN_EMAIL tanimli degil"}
    target = day or (local_now().date() - timedelta(days=1))
    if not force and await _last_sent_day() == target.isoformat():
        return {"sent": False, "reason": "already_sent", "day": target.isoformat()}

    data = await collect_digest(target)
    apps = data["applications"]["count"]
    subject = (
        f"Günlük özet · {data['day_label']} · {apps} başvuru · "
        f"{money(data['revenue']['total'])} tahsilat"
    )
    result = await send_email(
        admin_email,
        subject,
        daily_digest_html(data),
        kind="daily_digest",
        meta={"day": target.isoformat(), "applications": apps, "revenue": data["revenue"]["total"]},
    )
    await _mark_sent(target)
    return {"sent": True, "day": target.isoformat(), "email_status": result.get("status"), "data": data}


async def digest_loop() -> None:
    """Yerel saat 08:00'i geciyorsa dun icin ozeti gonderir; gunde bir kez."""
    await asyncio.sleep(120)
    while True:
        try:
            now = local_now()
            target = now.date() - timedelta(days=1)
            if now.hour >= SEND_HOUR and await _last_sent_day() != target.isoformat():
                summary = await send_daily_digest(target)
                logger.info("daily digest sent for %s: %s", summary.get("day"), summary.get("email_status"))
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover
            logger.error("daily digest failed: %s", exc)
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
