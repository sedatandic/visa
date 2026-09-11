"""Police teslimi: musteriye e-posta + WhatsApp gonderimi ve gorevin kapatilmasi.

Bu modul `insurance_tasks` (kuyruk) ile `insurance_provider` (saglayici API) arasindaki
dairesel bagimliligi kirmak icin ayrildi: her iki modul de buradan besleniyor, bu modul
hicbirini import etmiyor.
"""

import logging
from datetime import datetime, timezone

import file_access
import whatsapp
from db import insurance_tasks_col, orders_col, serialize_doc
from emailer import send_email

logger = logging.getLogger(__name__)


def policy_html(task: dict, link: str, message: str = "") -> str:
    """Police hazir e-postasi."""
    customer = task.get("customer") or task.get("contact") or {}
    extra = f"<p>{message}</p>" if message else ""
    return (
        f"<p>Merhaba {customer.get('full_name') or ''},</p>"
        f"<p>Seyahat sağlık sigortası poliçeniz hazır. Aşağıdaki bağlantıdan "
        f"PDF olarak indirebilirsiniz.</p>"
        f'<p><a href="{link}">Poliçenizi indir (PDF)</a></p>'
        f"{extra}"
        f"<p>Sipariş kodu: <b>{task.get('order_reference') or task.get('reference_code', '')}</b></p>"
        f"<p>İyi yolculuklar dileriz.<br>Dubai Vize Hattı</p>"
    )


def policy_wa_text(task: dict, link: str) -> str:
    """Police hazir mesaji (WhatsApp, PDF baglantili)."""
    full_name = (task.get("customer") or {}).get("full_name") or ""
    first_name = full_name.split(" ")[0] if full_name else ""
    greeting = f"Merhaba {first_name}," if first_name else "Merhaba,"
    return (
        f"{greeting} seyahat sağlık sigortası poliçeniz hazır. "
        f"PDF olarak buradan indirebilirsiniz: {link}\n"
        f"Sipariş kodu: {task.get('order_reference', '')}\n"
        "İyi yolculuklar dileriz · Dubai Vize Hattı"
    )


async def _notify_customer(task: dict, link: str, message: str) -> tuple[dict, dict]:
    """Police PDF'ini e-posta ve WhatsApp ile iletir."""
    customer = task.get("customer") or {}
    email_result = {"status": "skipped"}
    if customer.get("email"):
        email_result = await send_email(
            customer["email"],
            f"Sigorta poliçeniz hazır - {task.get('order_reference', '')}",
            policy_html(task, link, message),
            kind="insurance_policy_sent",
            meta={"task_id": task.get("id"), "order_id": task.get("order_id")},
        )
    wa_result = await whatsapp.send_customer_text(
        customer.get("phone"),
        policy_wa_text(task, link),
        reason="Poliçe hazır mesajı: WhatsApp API canlı değil, bağlantıya dokunup gönderin.",
    )
    return email_result, wa_result


async def _close_task(task: dict, policy_file_id: str, message: str, wa_result: dict) -> None:
    """Gorevi 'issued' yapar ve siparise teslim bilgisini yazar."""
    now = datetime.now(timezone.utc)
    await insurance_tasks_col.update_one(
        {"id": task["id"]},
        {
            "$set": {
                "status": "issued",
                "policy_file_id": policy_file_id,
                "message": message[:1000],
                "issued_at": now,
                "whatsapp": {
                    "status": wa_result.get("status"),
                    "link": wa_result.get("link", ""),
                    "phone": wa_result.get("phone", ""),
                    "detail": wa_result.get("detail") or wa_result.get("reason") or "",
                    "at": now,
                },
            }
        },
    )
    if task.get("order_id"):
        await orders_col.update_one(
            {"id": task["order_id"]},
            {"$set": {"delivery.policy_file_id": policy_file_id, "delivery.sent_at": now}},
        )


async def issue_policy(task_id: str, policy_file_id: str, origin: str, message: str = "") -> dict:
    """Police PDF'ini musteriye gonderir ve gorevi kapatir."""
    task = await insurance_tasks_col.find_one({"id": task_id})
    if not task:
        return {"ok": False, "reason": "not_found"}

    link = file_access.file_url(origin, policy_file_id, file_access.TTL_EMAIL)
    email_result, wa_result = await _notify_customer(task, link, message)
    await _close_task(task, policy_file_id, message, wa_result)

    fresh = await insurance_tasks_col.find_one({"id": task_id})
    return {"ok": True, "task": serialize_doc(fresh), "email": email_result, "whatsapp": wa_result}
