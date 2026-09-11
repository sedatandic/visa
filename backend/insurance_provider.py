"""Sigorta saglayici entegrasyonu: police kesimi ve odeme kuyrugu.

Aktif saglayici `active_provider()` ile secilir:
- `sigortambudur`: Sigortambudur (Panacea) B2B API — sigortali kaydi -> teklif ->
  en ucuz sirket -> police -> PDF adimlari adim adim (idempotent) yurutulur, PDF object
  storage'a yuklenir ve musteriye e-posta ile gonderilir.
- `manual`: API yok; police saglayici panelinden elle kesilir, PDF panelden yuklenir.

Not: Tamamliyo entegrasyonu 2026-06'da anlasma iptal edildigi icin tamamen kaldirildi.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone

import insurance_margin
import insurance_payment
import sigortambudur
from db import insurance_tasks_col, products_col, settings_col, uploads_col
from insurance_delivery import issue_policy
from storage import APP_NAME, put_object
from store_catalog import INSURANCE_MARKUP

logger = logging.getLogger(__name__)

SETTINGS_KEY = "insurance_provider"
RETRY_INTERVAL_MINUTES = 15
WAITING_STATUS = "waiting_payment"
REVIEW_STATUS = "payment_review"
STEPS = ("quote", "payment_confirm", "policy", "policy_pdf")

PROVIDER_SIGORTAMBUDUR = "sigortambudur"
PROVIDER_MANUAL = "manual"
PROVIDER_LABELS = {
    PROVIDER_SIGORTAMBUDUR: "Sigortambudur API",
    PROVIDER_MANUAL: "Elle kesim (API yok)",
}
API_OFF_MESSAGE = (
    "Sigorta sağlayıcı API'si kapalı. Poliçeyi sağlayıcı panelinden kesip PDF'i buraya yükleyin."
)


def provider_configured(name: str) -> bool:
    return name == PROVIDER_SIGORTAMBUDUR and sigortambudur.configured()


async def _settings_value() -> dict:
    doc = await settings_col.find_one({"key": SETTINGS_KEY})
    return ((doc or {}).get("value") or {})


async def active_provider() -> str:
    """Panel ayari varsa o, yoksa ortam degiskeni, o da yoksa elle kesim."""
    value = await _settings_value()
    name = (value.get("provider") or os.environ.get("INSURANCE_PROVIDER") or "").strip().lower()
    return name if name in PROVIDER_LABELS else PROVIDER_MANUAL


async def api_enabled() -> bool:
    """Saglayici API'si uzerinden police kesilebilir mi?"""
    return provider_configured(await active_provider())


async def set_provider(name: str) -> dict:
    provider = (name or "").strip().lower()
    if provider not in PROVIDER_LABELS:
        raise ValueError("Geçersiz sağlayıcı.")
    await settings_col.update_one(
        {"key": SETTINGS_KEY},
        {"$set": {"key": SETTINGS_KEY, "value.provider": provider}},
        upsert=True,
    )
    return {"provider": provider, "api_enabled": await api_enabled()}


def auto_issue_default() -> bool:
    return (os.environ.get("INSURANCE_AUTO_ISSUE") or "").strip().lower() in {"1", "true", "yes"}


async def auto_issue_on() -> bool:
    """Otomatik police kesimi: panel ayari varsa o, yoksa ortam degiskeni."""
    value = await _settings_value()
    setting = value.get("auto_issue")
    return auto_issue_default() if setting is None else bool(setting)


async def set_auto_issue(enabled: bool) -> dict:
    await settings_col.update_one(
        {"key": SETTINGS_KEY},
        {"$set": {"key": SETTINGS_KEY, "value.auto_issue": bool(enabled)}},
        upsert=True,
    )
    return {"auto_issue": bool(enabled)}


async def provider_status() -> dict:
    products = await products_col.find(
        {"kind": "insurance", "active": True},
        {"_id": 0, "id": 1, "name": 1, "cost_try": 1, "price_try": 1, "active": 1},
    ).sort("order", 1).to_list(20)
    provider = await active_provider()
    return {
        "provider": provider,
        "provider_label": PROVIDER_LABELS[provider],
        "providers": [
            {"id": key, "label": label, "configured": provider_configured(key) or key == PROVIDER_MANUAL}
            for key, label in PROVIDER_LABELS.items()
        ],
        "api_enabled": await api_enabled(),
        "configured": provider_configured(provider),
        "payment_method": sigortambudur.payment_method(),
        "base_url": sigortambudur.base_url(),
        "auto_issue": await auto_issue_on(),
        "markup": INSURANCE_MARKUP,
        "products": products,
    }


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


async def _record_charge(task_id: str) -> None:
    """Saglayicidan cekilen tutari goreve yazar (gider raporu) ve kar kontrolunu tetikler."""
    doc = await insurance_tasks_col.find_one({"id": task_id}) or {}
    charged = insurance_payment.parse_try(doc.get("provider_quote_price"))
    await insurance_tasks_col.update_one(
        {"id": task_id},
        {"$set": {"charged_try": charged, "charged_at": datetime.now(timezone.utc)}},
    )
    try:
        await insurance_margin.check_charge({**doc, "charged_try": charged})
    except Exception as exc:  # uyari gonderilemese de police kesimi durmamali
        logger.error("kar uyarisi gonderilemedi (%s): %s", task_id, exc)


async def _save_provider_error(task_id: str, message: str) -> None:
    if insurance_payment.is_payment_unknown(message):
        message += (
            " Mükerrer çekim riski var: sağlayıcı panelinden ödeme durumunu kontrol edin, "
            "poliçeyi elle kesin."
        )
    elif insurance_payment.is_payment_blocked(message):
        message += " Sağlayıcı cari bakiyenizi/kart limitinizi kontrol edin, poliçe kuyrukta bekliyor."
    await insurance_tasks_col.update_one(
        {"id": task_id},
        {
            "$set": {
                "provider_error": message[:500],
                "provider_updated_at": datetime.now(timezone.utc),
            }
        },
    )


async def _park_for_payment(task_id: str, kind: str) -> None:
    """Odeme yapilamadi: gorev kuyruga/incelemeye alinir, operatore uyari gider."""
    status_value = REVIEW_STATUS if kind == "review" else WAITING_STATUS
    await insurance_tasks_col.update_one(
        {"id": task_id},
        {"$set": {"status": status_value, "waiting_since": datetime.now(timezone.utc)}},
    )
    waiting = await insurance_tasks_col.count_documents(
        {"status": {"$in": [WAITING_STATUS, REVIEW_STATUS]}}
    )
    await insurance_payment.maybe_alert(kind, waiting)


async def _sigortambudur_quote(task: dict, insured: list) -> tuple[str, str]:
    """Sigortalilari kaydeder, grup teklifi acar ve en ucuz SUCCESS yaniti secer (idempotent)."""
    task_id = task["id"]
    if task.get("provider_response_id"):
        return task.get("provider_quote_id"), task["provider_response_id"]

    insured_ids = [
        await sigortambudur.customer_id(person["tc_kimlik_no"], person["birth_date"])
        for person in insured
    ]
    offer_id = await sigortambudur.create_offer(insured_ids, task["starts_on"], task["ends_on"])
    best = await sigortambudur.wait_for_offer(offer_id)
    await insurance_tasks_col.update_one(
        {"id": task_id},
        {
            "$set": {
                "provider_quote_id": offer_id,
                "provider_response_id": str(best.get("id")),
                "provider_quote_price": best.get("totalPremium"),
                "provider_steps.quote": "done",
                "provider_detail.quote": {
                    "offer_id": offer_id,
                    "provider_name": best.get("providerName"),
                    "provider_slug": best.get("providerSlug"),
                    "premium": best.get("totalPremium"),
                },
                "provider_error": None,
            }
        },
    )
    return offer_id, str(best.get("id"))


async def _sigortambudur_policy(task: dict, response_id: str) -> str:
    """Secilen teklifi policeye cevirir (acente cari hesabindan odeme) ve police id dondurur."""
    task_id = task["id"]
    detail = (task.get("provider_detail") or {}).get("policy") or {}
    policy_id = detail.get("policy_id")
    if policy_id:
        return str(policy_id)

    result = await sigortambudur.issue_policy(response_id)
    policy_id = str(result.get("id") or result.get("policyId") or "")
    if not policy_id:
        raise sigortambudur.SigortambudurError("Poliçe numarası alınamadı.", payload=result)
    await _mark_step(task_id, "payment_confirm", {"method": sigortambudur.payment_method()})
    await _mark_step(task_id, "policy", {"policy_id": policy_id, "policy_no": result.get("policyNumber")})
    await _record_charge(task_id)
    return policy_id


async def _issue_with_sigortambudur(task: dict, insured: list) -> str:
    """Teklif -> police -> PDF adimlarini yurutur ve PDF dosya kimligini dondurur."""
    _, response_id = await _sigortambudur_quote(task, insured)
    fresh = await insurance_tasks_col.find_one({"id": task["id"]}) or task
    policy_id = await _sigortambudur_policy(fresh, response_id)
    pdf = await sigortambudur.policy_pdf_bytes(policy_id)
    file_id = await _store_policy_pdf(task, pdf)
    await _mark_step(task["id"], "policy_pdf", {"file_id": file_id, "size": len(pdf)})
    return file_id


def _delivery_message(task: dict) -> str:
    """Musteriye giden police e-postasindaki kisa not (police hangi sirkette kesildi)."""
    insurer = ((task.get("provider_detail") or {}).get("quote") or {}).get("provider_name")
    return f"Poliçeniz {insurer} tarafından düzenlendi." if insurer else "Poliçeniz düzenlendi."


async def issue_via_provider(task_id: str, origin: str, actor: str = "") -> dict:
    """Aktif saglayici API'si ile policeyi keser; her adim tek sefer calisir (idempotent)."""
    task = await insurance_tasks_col.find_one({"id": task_id})
    if not task:
        return {"ok": False, "error": "Görev bulunamadı."}
    if task.get("status") == "issued":
        return {"ok": True, "already": True, "task_id": task_id}
    provider = await active_provider()
    if not provider_configured(provider):
        return {"ok": False, "error": API_OFF_MESSAGE, "manual": True}

    try:
        insured = _validate_task(task)
    except ValueError as exc:
        await insurance_tasks_col.update_one(
            {"id": task_id}, {"$set": {"provider_error": str(exc)}}
        )
        return {"ok": False, "error": str(exc)}

    # Mukerrer kesim korumasi: ayni gorev icin tek seferde tek istek gider
    claim = await insurance_tasks_col.find_one_and_update(
        {"id": task_id, "provider_issuing": {"$ne": True}},
        {"$set": {"provider_issuing": True, "provider_updated_at": datetime.now(timezone.utc)}},
    )
    if not claim:
        return {"ok": False, "error": "Bu poliçenin kesimi şu anda sürüyor, lütfen bekleyin."}

    try:
        file_id = await _issue_with_sigortambudur(task, insured)
    except Exception as exc:
        message = str(exc)
        await insurance_tasks_col.update_one({"id": task_id}, {"$set": {"provider_issuing": False}})
        await _save_provider_error(task_id, message)
        if insurance_payment.is_payment_unknown(message):
            await _park_for_payment(task_id, "review")
        elif insurance_payment.is_payment_blocked(message):
            await _park_for_payment(task_id, "blocked")
        logger.error("police kesimi basarisiz (%s / %s): %s", provider, task_id, message)
        return {"ok": False, "error": message, "quote_id": task.get("provider_quote_id")}

    await insurance_tasks_col.update_one({"id": task_id}, {"$set": {"provider_issuing": False}})
    fresh = await insurance_tasks_col.find_one({"id": task_id}) or task
    sent = await issue_policy(task_id, file_id, origin, message=_delivery_message(fresh))
    await insurance_tasks_col.update_one(
        {"id": task_id},
        {"$set": {"provider_error": None, "provider_issued_by": actor or "system"}},
    )
    fresh = await insurance_tasks_col.find_one({"id": task_id})
    return {
        "ok": True,
        "quote_id": (fresh or {}).get("provider_quote_id"),
        "policy_file_id": file_id,
        "delivery": sent,
        "task_status": (fresh or {}).get("status"),
    }


async def retry_waiting_tasks() -> dict:
    """Odeme bekleyen policeleri (cari bakiye yuklenince) kendiliginden keser.

    `payment_review` durumundakiler mukerrer cekim riski nedeniyle otomatik denenmez.
    """
    waiting = (
        await insurance_tasks_col.find({"status": WAITING_STATUS})
        .sort("created_at", 1)
        .to_list(50)
    )
    if not waiting or not await api_enabled():
        return {"issued": 0, "waiting": len(waiting)}

    origin = (os.environ.get("PUBLIC_SITE_URL") or "").strip().rstrip("/")
    issued = 0
    for task in waiting:
        result = await issue_via_provider(task["id"], origin, actor="auto-retry")
        if not result.get("ok"):
            break  # odeme yine basarisiz olabilir, kuyrugu zorlamayalim
        issued += 1
    return {"issued": issued, "waiting": len(waiting) - issued}


async def payment_retry_loop() -> None:
    """Odeme bekleyen policeleri periyodik olarak tekrar dener."""
    while True:
        await asyncio.sleep(RETRY_INTERVAL_MINUTES * 60)
        try:
            result = await retry_waiting_tasks()
            if result["issued"]:
                logger.info("odeme duzeldi: %s bekleyen police kesildi", result["issued"])
        except Exception as exc:
            logger.error("odeme kuyrugu denemesi hatasi: %s", exc)
