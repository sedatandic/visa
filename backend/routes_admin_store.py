"""Admin: magaza urunleri, siparisler, sigorta policeleri ve kar raporlari.

`routes_admin.py` cok fazla sorumluluk tasidigi icin bu grup ayri dosyaya alindi.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request

import file_access
from admin_auth import require_admin
from db import insurance_tasks_col, orders_col, products_col, serialize_doc
from emailer import order_delivered_html, send_email
from origins import resolve_origin
from store_catalog import product_list

router = APIRouter()

PRODUCT_FIELDS = {
    "price_usd",
    "price_try",
    "cost_try",
    "name",
    "summary",
    "active",
    "popular",
    "data_amount",
    "coverage",
    "validity_days",
}
NUMERIC_FIELDS = {"price_usd": float, "price_try": float, "cost_try": float, "validity_days": int}
ORDER_STATUSES = {"pending", "processing", "fulfilled", "cancelled"}
PAYMENT_STATUSES = {"pending", "awaiting_transfer", "paid", "refunded"}


# ------------------------------------------------------------------ urunler
@router.get("/admin/products")
async def admin_products(admin: dict = Depends(require_admin)) -> dict:
    items = await product_list(include_inactive=True)
    return {"items": items}


@router.patch("/admin/products/{product_id}")
async def admin_update_product(product_id: str, payload: dict, admin: dict = Depends(require_admin)):
    update = {k: v for k, v in payload.items() if k in PRODUCT_FIELDS}
    if not update:
        raise HTTPException(400, "Guncellenecek gecerli alan yok.")
    for field, caster in NUMERIC_FIELDS.items():
        if field in update:
            update[field] = caster(update[field])
    res = await products_col.update_one({"id": product_id}, {"$set": update})
    if res.matched_count == 0:
        raise HTTPException(404, "Urun bulunamadi.")
    items = await product_list(include_inactive=True)
    return next((i for i in items if i["id"] == product_id), None)


# ---------------------------------------------------------------- siparisler
@router.get("/admin/orders")
async def admin_orders(status: Optional[str] = None, admin: dict = Depends(require_admin)) -> dict:
    query = {"status": status} if status else {}
    docs = await orders_col.find(query).sort("created_at", -1).to_list(200)
    return {"items": serialize_doc(docs), "total": len(docs)}


@router.get("/admin/orders/{order_id}")
async def admin_order_detail(order_id: str, admin: dict = Depends(require_admin)):
    doc = await orders_col.find_one({"id": order_id})
    if not doc:
        raise HTTPException(404, "Siparis bulunamadi.")
    return serialize_doc(doc)


def _order_update_fields(payload: dict) -> dict:
    """PATCH gövdesinden yazilacak alanlari hazirlar."""
    update: dict = {"updated_at": datetime.now(timezone.utc)}
    if payload.get("status") in ORDER_STATUSES:
        update["status"] = payload["status"]
    if payload.get("payment_status") in PAYMENT_STATUSES:
        update["payment.status"] = payload["payment_status"]
        if payload["payment_status"] == "paid":
            update["payment.paid_at"] = datetime.now(timezone.utc)
            update.setdefault("status", "processing")
    if payload.get("admin_note") is not None:
        update["admin_note"] = str(payload["admin_note"])[:1000]
    return update


@router.patch("/admin/orders/{order_id}")
async def admin_update_order(order_id: str, payload: dict, admin: dict = Depends(require_admin)):
    doc = await orders_col.find_one({"id": order_id})
    if not doc:
        raise HTTPException(404, "Siparis bulunamadi.")
    update = _order_update_fields(payload)
    if len(update) == 1:
        raise HTTPException(400, "Guncellenecek gecerli alan yok.")
    await orders_col.update_one({"id": order_id}, {"$set": update})
    fresh = await orders_col.find_one({"id": order_id})
    if update.get("payment.status") == "paid":
        from insurance_tasks import queue_policy_tasks

        await queue_policy_tasks(fresh)
    return serialize_doc(fresh)


# --------------------------------------------------- sigorta: saglayici paneli
@router.get("/admin/insurance/provider")
async def admin_insurance_provider(admin: dict = Depends(require_admin)) -> dict:
    """Tamamliyo baglanti durumu + guncel maliyet/satis fiyatlari."""
    from insurance_provider import provider_status

    return await provider_status()


@router.post("/admin/insurance/sync-prices")
async def admin_insurance_sync_prices(admin: dict = Depends(require_admin)) -> dict:
    """Canli tarifeden maliyetleri ceker, satis fiyatlarini %100 marj ile guncelller."""
    from insurance_provider import sync_prices

    return await sync_prices()


@router.post("/admin/insurance/auto-issue")
async def admin_insurance_auto_issue(payload: dict, admin: dict = Depends(require_admin)) -> dict:
    """Otomatik police kesimini panelden acar/kapatir (varsayilan kapali)."""
    from insurance_provider import set_auto_issue

    return await set_auto_issue(bool(payload.get("enabled")))


# ----------------------------------------------------- sigorta: cari bakiye
@router.get("/admin/insurance/balance")
async def admin_insurance_balance(admin: dict = Depends(require_admin)) -> dict:
    """Tamamliyo cari bakiye takibi (saglayici bakiye sorgu API'si sunmuyor)."""
    from insurance_balance import status
    from insurance_provider import WAITING_STATUS

    state = await status()
    state["waiting_tasks"] = await insurance_tasks_col.count_documents({"status": WAITING_STATUS})
    return state


@router.post("/admin/insurance/balance/topup")
async def admin_insurance_balance_topup(
    payload: dict, admin: dict = Depends(require_admin)
) -> dict:
    """Tamamliyo paneline yuklenen bakiyeyi kaydeder, bekleyen policeleri hemen keser."""
    from insurance_balance import add_topup
    from insurance_provider import retry_waiting_tasks

    amount = float(payload.get("amount") or 0)
    if amount <= 0:
        raise HTTPException(400, "Yüklediğiniz bakiye tutarını girin.")
    state = await add_topup(amount, admin.get("email", ""))
    return {**state, "retry": await retry_waiting_tasks()}


# ------------------------------------------------------ sigorta: police kesimi
@router.post("/admin/insurance-tasks/{task_id}/issue-provider")
async def admin_issue_policy_via_provider(
    task_id: str, request: Request, admin: dict = Depends(require_admin)
) -> dict:
    """Policeyi Tamamliyo API'si uzerinden keser ve musteriye gonderir."""
    from insurance_provider import issue_via_provider

    result = await issue_via_provider(
        task_id, resolve_origin(None, request), actor=admin.get("email", "")
    )
    if not result.get("ok"):
        raise HTTPException(502, result.get("error") or "Poliçe kesilemedi.")
    task = await insurance_tasks_col.find_one({"id": task_id})
    return {**result, "task": serialize_doc(task)}


@router.get("/admin/insurance-tasks")
async def admin_insurance_tasks(status: str = "", admin: dict = Depends(require_admin)) -> dict:
    query = {"status": status} if status in {"pending", "issued", "waiting_balance"} else {}
    docs = await insurance_tasks_col.find(query).sort("created_at", -1).limit(200).to_list(200)
    return {"items": serialize_doc(docs)}


@router.post("/admin/insurance-tasks/{task_id}/issue")
async def admin_issue_policy(task_id: str, payload: dict, admin: dict = Depends(require_admin)) -> dict:
    from insurance_delivery import issue_policy

    policy_file_id = str(payload.get("policy_file_id") or "").strip()
    if not policy_file_id:
        raise HTTPException(400, "Police PDF dosyasi yuklemelisiniz.")
    origin = resolve_origin(payload.get("origin_url"), None)
    result = await issue_policy(
        task_id, policy_file_id, origin, str(payload.get("message") or "")[:1000]
    )
    if not result.get("ok"):
        raise HTTPException(404, "Police gorevi bulunamadi.")
    return result


# --------------------------------------------------------------- kar raporlari
@router.get("/admin/profit-monthly")
async def admin_profit_monthly(months: int = 12, admin: dict = Depends(require_admin)) -> dict:
    from insurance_tasks import monthly_profit

    return await monthly_profit(months)


@router.get("/admin/insurance-report")
async def admin_insurance_report(admin: dict = Depends(require_admin)) -> dict:
    from insurance_tasks import profit_report

    return await profit_report()


# ------------------------------------------------------------- siparis teslimi
def _delivery_links(origin: str, esim_file_id: Optional[str], policy_file_id: Optional[str]) -> list[dict]:
    """Teslim e-postasina konacak imzali indirme baglantilari."""
    labels = (("eSIM QR kodunuz", esim_file_id), ("Sigorta policeniz (PDF)", policy_file_id))
    return [
        {"label": label, "url": file_access.file_url(origin, file_id, file_access.TTL_EMAIL)}
        for label, file_id in labels
        if file_id
    ]


@router.post("/admin/orders/{order_id}/deliver")
async def admin_deliver_order(order_id: str, payload: dict, admin: dict = Depends(require_admin)) -> dict:
    """eSIM QR kodu / police PDF'ini musteriye e-posta ile gonderir."""
    doc = await orders_col.find_one({"id": order_id})
    if not doc:
        raise HTTPException(404, "Siparis bulunamadi.")

    esim_file_id = payload.get("esim_file_id")
    policy_file_id = payload.get("policy_file_id")
    message = str(payload.get("message") or "")[:1000]
    if not esim_file_id and not policy_file_id:
        raise HTTPException(400, "En az bir belge (eSIM QR veya police) yuklemelisiniz.")

    origin = resolve_origin(payload.get("origin_url"), None)
    links = _delivery_links(origin, esim_file_id, policy_file_id)

    now = datetime.now(timezone.utc)
    await orders_col.update_one(
        {"id": order_id},
        {
            "$set": {
                "delivery": {
                    "esim_file_id": esim_file_id,
                    "policy_file_id": policy_file_id,
                    "message": message,
                    "sent_at": now,
                },
                "status": "fulfilled",
                "updated_at": now,
            }
        },
    )
    fresh = await orders_col.find_one({"id": order_id})
    to_email = (fresh.get("contact") or {}).get("email")
    result = {"status": "skipped"}
    if to_email:
        result = await send_email(
            to_email,
            f"Siparişiniz hazır - {fresh['reference_code']}",
            order_delivered_html(serialize_doc(fresh), links, message),
            kind="order_delivered",
            meta={"order_id": order_id, "reference_code": fresh["reference_code"]},
        )
    return {"order": serialize_doc(fresh), "email": result}
