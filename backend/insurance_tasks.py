"""Sigorta policesi kesim kuyrugu.

Odeme onaylandigi anda police kesim gorevi olusturulur; musteriye "policeniz
hazirlaniyor" bilgisi, admine anlik bildirim gider. Admin panelden police PDF'i
yuklendiginde musteriye otomatik e-posta ile iletilir.

Saglayici (seyahatpolicesi.com) acik bir API sunmadigi icin kesim adimi
`provider_link` uzerinden tek tikla yapilir; geri kalan tum akis otomatiktir.
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlencode

from db import insurance_tasks_col, notifications_col, orders_col, serialize_doc
import file_access
from store_catalog import product_list
from emailer import send_email

logger = logging.getLogger(__name__)

PROVIDER_NAME = "tamamliyo"
PROVIDER_PANEL = "https://dashboard.tamamliyo.com/anasayfa"
LEGACY_PROVIDER_BASE = "https://seyahatpolicesi.com/dubai-seyahat-saglik-sigortasi"


def provider_link(line: dict, order: dict) -> str:
    """API dısı manuel kesim gerekirse kullanilan on doldurmali yedek baglanti."""
    travel = order.get("travel") or {}
    params = {
        "bolge": "tum-dunya",
        "ulke": "birlesik-arap-emirlikleri",
        "gun": line.get("validity_days") or "",
        "kisi": line.get("quantity") or 1,
        "baslangic": line.get("starts_on") or travel.get("start") or "",
    }
    return f"{LEGACY_PROVIDER_BASE}?{urlencode({k: v for k, v in params.items() if v})}"


def _policy_html(order: dict, link: str, message: str) -> str:
    contact = order.get("contact") or {}
    extra = f"<p>{message}</p>" if message else ""
    return (
        f"<p>Merhaba {contact.get('full_name') or ''},</p>"
        f"<p>Seyahat sağlık sigortası poliçeniz hazır. Aşağıdaki bağlantıdan "
        f"PDF olarak indirebilirsiniz.</p>"
        f'<p><a href="{link}">Poliçenizi indir (PDF)</a></p>'
        f"{extra}"
        f"<p>Sipariş kodu: <b>{order.get('reference_code','')}</b></p>"
        f"<p>İyi yolculuklar dileriz.<br>Dubai Vize Hattı</p>"
    )


def _pending_html(order: dict, lines: list) -> str:
    contact = order.get("contact") or {}
    items = "".join(
        f"<li>{line.get('name')} · {line.get('quantity')} kişi</li>" for line in lines
    )
    return (
        f"<p>Merhaba {contact.get('full_name') or ''},</p>"
        f"<p>Ödemeniz alındı. Seyahat sağlık sigortası poliçeniz hazırlanıyor ve "
        f"kısa süre içinde PDF olarak bu adrese gönderilecek.</p>"
        f"<ul>{items}</ul>"
        f"<p>Sipariş kodu: <b>{order.get('reference_code','')}</b></p>"
        f"<p>Dubai Vize Hattı</p>"
    )


def _insurance_lines(order: dict) -> list:
    return [line for line in (order.get("items") or []) if line.get("kind") == "insurance"]


def _build_policy_task(order: dict, line: dict, contact: dict, now: datetime) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "order_id": order.get("id"),
        "order_reference": order.get("reference_code", ""),
        "application_id": order.get("application_id"),
        "product_id": line.get("product_id"),
        "plan_name": line.get("name"),
        "validity_days": line.get("validity_days"),
        "quantity": int(line.get("quantity") or 1),
        "unit_price": float(line.get("unit_price") or 0),
        "unit_cost": float(line.get("unit_cost") or 0),
        "starts_on": line.get("starts_on"),
        "ends_on": line.get("ends_on"),
        "customer": {
            "full_name": contact.get("full_name", ""),
            "email": contact.get("email", ""),
            "phone": contact.get("phone", ""),
        },
        "insured": order.get("insured") or [],
        "note": order.get("note", ""),
        "provider": PROVIDER_NAME,
        "provider_link": provider_link(line, order),
        "provider_quote_id": None,
        "provider_steps": {},
        "provider_error": None,
        "status": "pending",
        "policy_file_id": None,
        "issued_at": None,
        "created_at": now,
    }


async def _notify_policy_pending(order: dict, lines: list, contact: dict, now: datetime) -> None:
    await notifications_col.insert_one(
        {
            "id": str(uuid.uuid4()),
            "kind": "insurance_policy_pending",
            "title": f"Poliçe kesimi bekliyor · {order.get('reference_code','')}",
            "body": ", ".join(line.get("name", "") for line in lines),
            "order_id": order.get("id"),
            "read": False,
            "created_at": now,
        }
    )
    if contact.get("email"):
        await send_email(
            contact["email"],
            f"Sigorta policeniz hazirlaniyor - {order.get('reference_code','')}",
            _pending_html(order, lines),
            kind="insurance_pending",
            meta={"order_id": order.get("id")},
        )


async def queue_policy_tasks(order: dict) -> list:
    """Odemesi alinan siparis icin police kesim gorevlerini olusturur (idempotent)."""
    lines = _insurance_lines(order)
    if not lines:
        return []
    if await insurance_tasks_col.find_one({"order_id": order.get("id")}):
        return []

    now = datetime.now(timezone.utc)
    contact = order.get("contact") or {}
    created = []
    for line in lines:
        task = _build_policy_task(order, line, contact, now)
        await insurance_tasks_col.insert_one(dict(task))
        created.append(task)

    await _notify_policy_pending(order, lines, contact, now)
    logger.info("insurance tasks queued: %s (%s)", order.get("reference_code"), len(created))
    await _maybe_auto_issue(created)
    return created


async def _maybe_auto_issue(tasks: list) -> None:
    """TAMAMLIYO_AUTO_ISSUE acikken policeyi hemen keser (varsayilan kapali)."""
    import tamamliyo

    from insurance_provider import auto_issue_on, issue_via_provider

    if not (tasks and tamamliyo.configured() and await auto_issue_on()):
        return

    origin = (os.environ.get("PUBLIC_SITE_URL") or "").strip().rstrip("/")
    for task in tasks:
        try:
            await issue_via_provider(task["id"], origin, actor="auto")
        except Exception as exc:  # pragma: no cover - saglayici hatasi gorevde saklanir
            logger.error("otomatik police kesimi basarisiz (%s): %s", task["id"], exc)


def _application_insurance_order(app_doc: dict) -> dict:
    """Basvurudaki sigorta kalemlerini `queue_policy_tasks` sozlesmesine cevirir."""
    travel = app_doc.get("travel") or {}
    lines = []
    for item in app_doc.get("store_items") or []:
        if (item.get("kind") or "") != "insurance":
            continue
        line = dict(item)
        line.setdefault("starts_on", travel.get("arrival_date"))
        line.setdefault("ends_on", travel.get("departure_date"))
        lines.append(line)
    insured = [
        {
            "full_name": f"{t.get('first_name', '')} {t.get('last_name', '')}".strip(),
            "tc_kimlik_no": t.get("tc_kimlik_no") or "",
            "birth_date": t.get("birth_date") or "",
        }
        for t in app_doc.get("travelers") or []
    ]
    return {
        "id": app_doc.get("id"),
        "reference_code": app_doc.get("reference_code", ""),
        "application_id": app_doc.get("id"),
        "items": lines,
        "contact": app_doc.get("contact") or {},
        "insured": insured,
        "travel": {"start": travel.get("arrival_date")},
        "note": travel.get("notes", ""),
    }


async def queue_application_policy_tasks(app_doc: dict) -> list:
    """Vize basvurusuna eklenen sigorta icin police kesim gorevi olusturur."""
    return await queue_policy_tasks(_application_insurance_order(app_doc))


async def issue_policy(task_id: str, policy_file_id: str, origin: str, message: str = "") -> dict:
    """Yuklenen police PDF'ini musteriye gonderir ve gorevi kapatir."""
    task = await insurance_tasks_col.find_one({"id": task_id})
    if not task:
        return {"ok": False, "reason": "not_found"}

    order = await orders_col.find_one({"id": task.get("order_id")}) or {}
    link = file_access.file_url(origin, policy_file_id, file_access.TTL_EMAIL)
    now = datetime.now(timezone.utc)
    email_result = {"status": "skipped"}
    to_email = (task.get("customer") or {}).get("email")
    if to_email:
        email_result = await send_email(
            to_email,
            f"Sigorta poliçeniz hazır - {task.get('order_reference','')}",
            _policy_html(order or task, link, message),
            kind="insurance_policy_sent",
            meta={"task_id": task_id, "order_id": task.get("order_id")},
        )

    await insurance_tasks_col.update_one(
        {"id": task_id},
        {
            "$set": {
                "status": "issued",
                "policy_file_id": policy_file_id,
                "message": message[:1000],
                "issued_at": now,
            }
        },
    )
    if order:
        await orders_col.update_one(
            {"id": order["id"]},
            {"$set": {"delivery.policy_file_id": policy_file_id, "delivery.sent_at": now}},
        )
    fresh = await insurance_tasks_col.find_one({"id": task_id})
    return {"ok": True, "task": serialize_doc(fresh), "email": email_result}


def _empty_bucket(key: str) -> dict:
    return {
        "month": key,
        "insurance_revenue": 0.0,
        "insurance_cost": 0.0,
        "esim_revenue": 0.0,
        "esim_cost": 0.0,
        "orders": set(),
    }


def _month_keys(months: int) -> list:
    """Bugunden geriye dogru N aylik anahtar listesi (eski -> yeni)."""
    now = datetime.now(timezone.utc)
    keys = []
    year, month = now.year, now.month
    for _ in range(max(1, min(months, 24))):
        keys.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    keys.reverse()
    return keys


def _add_order_to_bucket(bucket: dict, order: dict, products: dict) -> None:
    bucket["orders"].add(order.get("id"))
    for line in order.get("items") or []:
        kind = line.get("kind")
        if kind not in {"insurance", "esim"}:
            continue
        quantity = int(line.get("quantity") or 1)
        product = products.get(line.get("product_id")) or {}
        unit_cost = float(line.get("unit_cost") or product.get("cost_try") or 0)
        bucket[f"{kind}_revenue"] += float(line.get("total") or 0)
        bucket[f"{kind}_cost"] += unit_cost * quantity


def _month_row(key: str, bucket: Optional[dict]) -> dict:
    b = bucket or _empty_bucket(key)
    ins_profit = round(b["insurance_revenue"] - b["insurance_cost"], 2)
    esim_profit = round(b["esim_revenue"] - b["esim_cost"], 2)
    return {
        "month": key,
        "label": f"{key[5:]}.{key[2:4]}",
        "insurance_profit": ins_profit,
        "esim_profit": esim_profit,
        "insurance_revenue": round(b["insurance_revenue"], 2),
        "esim_revenue": round(b["esim_revenue"], 2),
        "total_profit": round(ins_profit + esim_profit, 2),
        "orders": len(b["orders"]),
    }


async def monthly_profit(months: int = 12) -> dict:
    """Son N ay icin sigorta + eSIM ciro/maliyet/kar dagilimi."""
    products = {p["id"]: p for p in await product_list(include_inactive=True)}
    buckets: dict = {}
    async for order in orders_col.find({"payment.status": "paid"}):
        paid_at = (order.get("payment") or {}).get("paid_at") or order.get("created_at")
        if not isinstance(paid_at, datetime):
            continue
        key = paid_at.strftime("%Y-%m")
        _add_order_to_bucket(buckets.setdefault(key, _empty_bucket(key)), order, products)

    rows = [_month_row(key, buckets.get(key)) for key in _month_keys(months)]
    return {
        "items": rows,
        "totals": {
            "insurance_profit": round(sum(r["insurance_profit"] for r in rows), 2),
            "esim_profit": round(sum(r["esim_profit"] for r in rows), 2),
            "total_profit": round(sum(r["total_profit"] for r in rows), 2),
            "revenue": round(sum(r["insurance_revenue"] + r["esim_revenue"] for r in rows), 2),
        },
    }


async def _sold_insurance_totals() -> dict:
    """Odenmis siparislerden urun bazli satilan adet ve ciroyu toplar."""
    sold: dict = {}
    async for order in orders_col.find({"payment.status": "paid"}):
        for line in _insurance_lines(order):
            entry = sold.setdefault(line.get("product_id"), {"quantity": 0, "revenue": 0.0})
            entry["quantity"] += int(line.get("quantity") or 1)
            entry["revenue"] += float(line.get("total") or 0)
    return sold


def _profit_row(product: dict, stats: dict) -> dict:
    price = float(product.get("price") or 0)
    cost = float(product.get("cost_try") or 0)
    return {
        "id": product["id"],
        "name": product["name"],
        "validity_days": product.get("validity_days"),
        "active": product.get("active", True),
        "cost_try": cost,
        "price_try": price,
        "profit_try": round(price - cost, 2),
        "margin_pct": round((price - cost) / cost * 100) if cost else None,
        "sold_quantity": stats["quantity"],
        "revenue_try": round(stats["revenue"], 2),
        "cost_total_try": round(cost * stats["quantity"], 2),
        "profit_total_try": round(stats["revenue"] - cost * stats["quantity"], 2),
    }


async def profit_report() -> dict:
    """Poliçe basina maliyet / satis / kar tablosu."""
    products = [p for p in await product_list(include_inactive=True) if p.get("kind") == "insurance"]
    sold = await _sold_insurance_totals()
    rows = [
        _profit_row(product, sold.get(product["id"], {"quantity": 0, "revenue": 0.0}))
        for product in sorted(products, key=lambda p: p.get("order", 0))
    ]

    return {
        "provider": PROVIDER_NAME,
        "items": rows,
        "totals": {
            "sold_quantity": sum(r["sold_quantity"] for r in rows),
            "revenue_try": round(sum(r["revenue_try"] for r in rows), 2),
            "cost_total_try": round(sum(r["cost_total_try"] for r in rows), 2),
            "profit_total_try": round(sum(r["profit_total_try"] for r in rows), 2),
        },
    }
