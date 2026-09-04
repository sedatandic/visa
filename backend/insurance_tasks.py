"""Sigorta policesi kesim kuyrugu.

Odeme onaylandigi anda police kesim gorevi olusturulur; musteriye "policeniz
hazirlaniyor" bilgisi, admine anlik bildirim gider. Admin panelden police PDF'i
yuklendiginde musteriye otomatik e-posta ile iletilir.

Saglayici (seyahatpolicesi.com) acik bir API sunmadigi icin kesim adimi
`provider_link` uzerinden tek tikla yapilir; geri kalan tum akis otomatiktir.
"""

import logging
import uuid
from datetime import datetime, timezone
from urllib.parse import urlencode

from db import insurance_tasks_col, notifications_col, orders_col, serialize_doc
from emailer import send_email

logger = logging.getLogger(__name__)

PROVIDER_NAME = "seyahatpolicesi.com"
PROVIDER_BASE = "https://seyahatpolicesi.com/dubai-seyahat-saglik-sigortasi"


def provider_link(line: dict, order: dict) -> str:
    """Saglayici teklif sayfasi icin on doldurmali baglanti."""
    travel = order.get("travel") or {}
    params = {
        "bolge": "tum-dunya",
        "ulke": "birlesik-arap-emirlikleri",
        "gun": line.get("validity_days") or "",
        "kisi": line.get("quantity") or 1,
        "baslangic": line.get("starts_on") or travel.get("start") or "",
    }
    return f"{PROVIDER_BASE}?{urlencode({k: v for k, v in params.items() if v})}"


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
        f"<p>İyi yolculuklar dileriz.<br>Dubai Vize Online</p>"
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
        f"<p>Dubai Vize Online</p>"
    )


def _insurance_lines(order: dict) -> list:
    return [line for line in (order.get("items") or []) if line.get("kind") == "insurance"]


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
        task = {
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
            "note": order.get("note", ""),
            "provider": PROVIDER_NAME,
            "provider_link": provider_link(line, order),
            "status": "pending",
            "policy_file_id": None,
            "issued_at": None,
            "created_at": now,
        }
        await insurance_tasks_col.insert_one(dict(task))
        created.append(task)

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
    logger.info("insurance tasks queued: %s (%s)", order.get("reference_code"), len(created))
    return created


async def issue_policy(task_id: str, policy_file_id: str, origin: str, message: str = "") -> dict:
    """Yuklenen police PDF'ini musteriye gonderir ve gorevi kapatir."""
    task = await insurance_tasks_col.find_one({"id": task_id})
    if not task:
        return {"ok": False, "reason": "not_found"}

    order = await orders_col.find_one({"id": task.get("order_id")}) or {}
    link = f"{origin}/api/files/{policy_file_id}"
    now = datetime.now(timezone.utc)
    email_result = {"status": "skipped"}
    to_email = (task.get("customer") or {}).get("email")
    if to_email:
        email_result = await send_email(
            to_email,
            f"Sigorta policeniz hazir - {task.get('order_reference','')}",
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


async def profit_report() -> dict:
    """Poliçe basina maliyet / satis / kar tablosu."""
    from routes_store import product_list

    products = [p for p in await product_list(include_inactive=True) if p.get("kind") == "insurance"]
    sold: dict = {}
    async for order in orders_col.find({"payment.status": "paid"}):
        for line in _insurance_lines(order):
            pid = line.get("product_id")
            entry = sold.setdefault(pid, {"quantity": 0, "revenue": 0.0})
            entry["quantity"] += int(line.get("quantity") or 1)
            entry["revenue"] += float(line.get("total") or 0)

    rows = []
    for product in sorted(products, key=lambda p: p.get("order", 0)):
        price = float(product.get("price") or 0)
        cost = float(product.get("cost_try") or 0)
        stats = sold.get(product["id"], {"quantity": 0, "revenue": 0.0})
        rows.append(
            {
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
        )

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
