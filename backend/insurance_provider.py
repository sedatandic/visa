"""Sigorta saglayici entegrasyonu (Tamamliyo): canli fiyat senkronu + police kesimi.

- `sync_prices()`: 4 sure icin (7/15/30/60 gun) canli maliyeti ceker, %100 marj ile
  satis fiyatini gunceller. Gunde bir kez otomatik, panelden elle de tetiklenir.
- `issue_via_provider()`: odemesi alinmis police gorevi icin teklif -> cari odeme onayi
  -> police -> PDF adimlarini adim adim (idempotent) yurutur, PDF'i object storage'a
  yukler ve musteriye e-posta ile gonderir.
"""

import asyncio
import logging
import uuid
from datetime import date, datetime, timedelta, timezone

import tamamliyo
from db import insurance_tasks_col, products_col, settings_col, uploads_col
from storage import APP_NAME, put_object
from store_catalog import INSURANCE_MARKUP, INSURANCE_PRODUCTS

logger = logging.getLogger(__name__)

SETTINGS_KEY = "insurance_provider"
SYNC_INTERVAL_HOURS = 24
STEPS = ("quote", "payment_confirm", "policy", "policy_pdf")


def _sale_price(cost: float) -> float:
    """Maliyet + %100 marj, 10 TL'ye yuvarlanir."""
    return float(round(cost * INSURANCE_MARKUP / 10.0) * 10)


async def fetch_cost(days: int) -> dict:
    """Verilen sure icin tek kisilik canli maliyeti dondurur."""
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=days)
    payload = await tamamliyo.price(1, start.isoformat(), end.isoformat(), tamamliyo.URUN_ID)
    info = ((payload.get("data") or {}).get("urunBilgileri")) or {}
    cost = float(info.get("fiyatFloat") or 0)
    if cost <= 0:
        raise tamamliyo.TamamliyoError("Tamamliyo fiyat yanıtı boş döndü.", payload=payload)
    return {
        "days": days,
        "cost": round(cost, 2),
        "price": _sale_price(cost),
        "product_name": info.get("urunAdi") or "",
        "quote_start": start.isoformat(),
        "quote_end": end.isoformat(),
    }


async def sync_prices() -> dict:
    """4 sigorta urununun maliyet ve satis fiyatini canli tarifeden gunceller."""
    now = datetime.now(timezone.utc)
    rows, errors = [], []
    for product in INSURANCE_PRODUCTS:
        try:
            quote = await fetch_cost(int(product["validity_days"]))
        except Exception as exc:
            errors.append({"product_id": product["id"], "error": str(exc)})
            logger.warning("sigorta fiyat senkronu basarisiz (%s): %s", product["id"], exc)
            continue
        await products_col.update_one(
            {"id": product["id"]},
            {
                "$set": {
                    "cost_try": quote["cost"],
                    "price_try": quote["price"],
                    "provider": "tamamliyo",
                    "provider_urun_id": tamamliyo.URUN_ID,
                    "provider_product_name": quote["product_name"],
                    "cost_synced_at": now,
                    "active": True,
                }
            },
            upsert=False,
        )
        rows.append({"product_id": product["id"], **quote})

    # Katalogdan cikarilan eski sigorta urunlerini vitrinden kaldir
    keep = [p["id"] for p in INSURANCE_PRODUCTS]
    retired = await products_col.update_many(
        {"kind": "insurance", "id": {"$nin": keep}}, {"$set": {"active": False}}
    )
    await settings_col.update_one(
        {"key": SETTINGS_KEY},
        {
            "$set": {
                "key": SETTINGS_KEY,
                "value.last_sync_at": now,
                "value.rows": rows,
                "value.errors": errors,
            }
        },
        upsert=True,
    )
    return {
        "synced_at": now.isoformat(),
        "rows": rows,
        "errors": errors,
        "retired": retired.modified_count,
    }


async def auto_issue_on() -> bool:
    """Otomatik police kesimi: panel ayari varsa o, yoksa ortam degiskeni."""
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    value = ((doc or {}).get("value") or {}).get("auto_issue")
    return tamamliyo.auto_issue_enabled() if value is None else bool(value)


async def set_auto_issue(enabled: bool) -> dict:
    await settings_col.update_one(
        {"key": SETTINGS_KEY},
        {"$set": {"key": SETTINGS_KEY, "value.auto_issue": bool(enabled)}},
        upsert=True,
    )
    return {"auto_issue": bool(enabled)}


async def provider_status() -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    value = (doc or {}).get("value") or {}
    last_sync = value.get("last_sync_at")
    products = await products_col.find(
        {"kind": "insurance"}, {"_id": 0, "id": 1, "name": 1, "cost_try": 1, "price_try": 1, "active": 1}
    ).sort("order", 1).to_list(20)
    return {
        "configured": tamamliyo.configured(),
        "base_url": tamamliyo.base_url(),
        "urun_id": tamamliyo.URUN_ID,
        "auto_issue": await auto_issue_on(),
        "markup": INSURANCE_MARKUP,
        "last_sync_at": last_sync.isoformat() if isinstance(last_sync, datetime) else last_sync,
        "last_errors": value.get("errors") or [],
        "products": products,
    }


def _steps(task: dict) -> dict:
    return {step: (task.get("provider_steps") or {}).get(step) for step in STEPS}


async def _mark_step(task_id: str, step: str, detail: dict | None = None) -> None:
    await insurance_tasks_col.update_one(
        {"id": task_id},
        {
            "$set": {
                f"provider_steps.{step}": "done",
                f"provider_detail.{step}": detail or {},
                "provider_updated_at": datetime.now(timezone.utc),
            }
        },
    )


async def _store_policy_pdf(task: dict, data: bytes) -> str:
    """Police PDF'ini object storage'a yukler ve uploads kaydini olusturur."""
    file_id = str(uuid.uuid4())
    path = f"{APP_NAME}/uploads/insurance_policy/{file_id}.pdf"
    result = put_object(path, data, "application/pdf")
    await uploads_col.insert_one(
        {
            "id": file_id,
            "doc_type": "insurance_policy",
            "storage_path": result["path"],
            "original_filename": f"Police-{task.get('order_reference', '')}.pdf",
            "content_type": "application/pdf",
            "size": result.get("size", len(data)),
            "is_deleted": False,
            "created_at": datetime.now(timezone.utc),
        }
    )
    return file_id


def _validate_task(task: dict) -> list:
    insured = task.get("insured") or []
    if not insured:
        raise ValueError("Sigortalı kimlik bilgileri eksik (TC kimlik no / doğum tarihi).")
    for person in insured:
        if not person.get("tc_kimlik_no") or not person.get("birth_date"):
            raise ValueError("Her sigortalı için TC kimlik no ve doğum tarihi zorunlu.")
    if not task.get("starts_on") or not task.get("ends_on"):
        raise ValueError("Poliçe başlangıç/bitiş tarihi bulunamadı.")
    return insured


async def issue_via_provider(task_id: str, origin: str, actor: str = "") -> dict:
    """Tamamliyo uzerinden policeyi keser; her adim tek sefer calisir (idempotent)."""
    from insurance_tasks import issue_policy

    task = await insurance_tasks_col.find_one({"id": task_id})
    if not task:
        return {"ok": False, "error": "Görev bulunamadı."}
    if task.get("status") == "issued":
        return {"ok": True, "already": True, "task_id": task_id}

    try:
        insured = _validate_task(task)
    except ValueError as exc:
        await insurance_tasks_col.update_one(
            {"id": task_id}, {"$set": {"provider_error": str(exc)}}
        )
        return {"ok": False, "error": str(exc)}

    customer = task.get("customer") or {}
    steps = _steps(task)
    quote_id = task.get("provider_quote_id")

    try:
        if not quote_id:
            payload = await tamamliyo.create_quote(
                insured,
                task["starts_on"],
                task["ends_on"],
                customer.get("email", ""),
                customer.get("phone", ""),
            )
            info = ((payload.get("data") or {}).get("teklifBilgileri")) or {}
            quote_id = info.get("teklifId")
            if not quote_id:
                raise tamamliyo.TamamliyoError("Teklif numarası alınamadı.", payload=payload)
            await insurance_tasks_col.update_one(
                {"id": task_id, "provider_quote_id": None},
                {
                    "$set": {
                        "provider_quote_id": quote_id,
                        "provider_quote_price": info.get("fiyat"),
                        "provider_steps.quote": "done",
                        "provider_error": None,
                    }
                },
            )
            fresh = await insurance_tasks_col.find_one({"id": task_id})
            quote_id = (fresh or {}).get("provider_quote_id") or quote_id

        if steps.get("payment_confirm") != "done":
            result = await tamamliyo.confirm_payment(
                quote_id, {"partnerReference": task.get("order_reference", "")}
            )
            await _mark_step(task_id, "payment_confirm", {"success": bool(result.get("success", True))})

        if steps.get("policy") != "done":
            result = await tamamliyo.create_policy(quote_id)
            await _mark_step(task_id, "policy", {"police_no": str((result.get("data") or {}).get("policeNo", ""))})

        pdf_payload = await tamamliyo.policy_pdf(quote_id)
        pdf_bytes = await tamamliyo.fetch_policy_bytes(pdf_payload)
        file_id = await _store_policy_pdf(task, pdf_bytes)
        await _mark_step(task_id, "policy_pdf", {"file_id": file_id, "size": len(pdf_bytes)})
    except Exception as exc:
        message = str(exc)
        await insurance_tasks_col.update_one(
            {"id": task_id},
            {"$set": {"provider_error": message[:500], "provider_updated_at": datetime.now(timezone.utc)}},
        )
        logger.error("tamamliyo police kesimi basarisiz (%s): %s", task_id, message)
        return {"ok": False, "error": message, "quote_id": quote_id}

    sent = await issue_policy(task_id, file_id, origin, message="Poliçeniz Tamamliyo üzerinden düzenlendi.")
    await insurance_tasks_col.update_one(
        {"id": task_id},
        {"$set": {"provider_error": None, "provider_issued_by": actor or "system"}},
    )
    return {"ok": True, "quote_id": quote_id, "policy_file_id": file_id, "delivery": sent}


async def price_sync_loop() -> None:
    """Gunluk fiyat senkronu (servis acilisinda bir kez, sonra 24 saatte bir)."""
    while True:
        try:
            if tamamliyo.configured():
                result = await sync_prices()
                logger.info(
                    "sigorta fiyatlari guncellendi: %s urun, %s hata",
                    len(result["rows"]),
                    len(result["errors"]),
                )
        except Exception as exc:
            logger.error("sigorta fiyat senkronu hatasi: %s", exc)
        await asyncio.sleep(SYNC_INTERVAL_HOURS * 3600)
