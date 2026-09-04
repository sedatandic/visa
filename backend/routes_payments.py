import logging
import os
from datetime import datetime, timezone

from emergentintegrations.payments.stripe.checkout import (
    CheckoutSessionRequest,
    StripeCheckout,
)
from fastapi import APIRouter, HTTPException, Request

from content import BANK_TRANSFER
from db import applications_col, payments_col, serialize_doc, settings_col
from emailer import bank_transfer_html, payment_received_html, send_email
from models import CheckoutRequest

logger = logging.getLogger(__name__)
router = APIRouter()


def _client(request: Request) -> StripeCheckout:
    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        raise HTTPException(500, "Odeme altyapisi yapilandirilmamis.")
    return StripeCheckout(api_key=api_key, webhook_url=webhook_url)


async def _mark_order_paid(session_id: str, tx: dict):
    """Magaza siparisi odemesini isaretler ve musteriyi bilgilendirir."""
    from db import orders_col
    from emailer import order_received_html

    order = await orders_col.find_one({"id": tx.get("order_id")})
    if not order:
        return
    now = datetime.now(timezone.utc)
    await orders_col.update_one(
        {"id": order["id"]},
        {
            "$set": {
                "payment.status": "paid",
                "payment.session_id": session_id,
                "payment.paid_at": now,
                "status": "processing",
                "updated_at": now,
            }
        },
    )
    fresh = await orders_col.find_one({"id": order["id"]})
    to_email = (fresh.get("contact") or {}).get("email")
    if to_email:
        await send_email(
            to_email,
            f"Odemeniz alindi - {fresh['reference_code']}",
            order_received_html(serialize_doc(fresh)),
            kind="order_payment_received",
            meta={"reference_code": fresh["reference_code"]},
        )
    from insurance_tasks import queue_policy_tasks

    await queue_policy_tasks(fresh)


async def _claim_transaction(session_id: str) -> dict | None:
    """Islemi tek seferlik 'paid' olarak isaretler; daha once alinmissa None doner."""
    res = await payments_col.update_one(
        {"session_id": session_id, "payment_status": {"$ne": "paid"}},
        {
            "$set": {
                "status": "completed",
                "payment_status": "paid",
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    if res.modified_count == 0:
        return None
    return await payments_col.find_one({"session_id": session_id})


async def _apply_application_payment(app_doc: dict, session_id: str) -> None:
    """Basvuruyu odendi olarak isaretler ve incelemeye alir."""
    now = datetime.now(timezone.utc)
    next_status = (
        "reviewing"
        if app_doc.get("status") in ("submitted", "payment_pending")
        else app_doc.get("status")
    )
    await applications_col.update_one(
        {"id": app_doc["id"]},
        {
            "$set": {
                "payment.status": "paid",
                "payment.session_id": session_id,
                "payment.paid_at": now,
                "status": next_status,
                "updated_at": now,
            },
            "$push": {
                "status_history": {
                    "status": "reviewing",
                    "at": now,
                    "note": "Odeme alindi, basvuru incelemeye alindi",
                }
            },
        },
    )
    from routes_store import sync_application_order_payment

    await sync_application_order_payment(app_doc["id"], "paid", method="card")


async def _notify_application_payment(application_id: str) -> None:
    """Odeme alindi bilgilendirme e-postasini gonderir."""
    fresh = await applications_col.find_one({"id": application_id})
    if not fresh:
        return
    to_email = (fresh.get("contact") or {}).get("email") or (fresh.get("applicant") or {}).get("email")
    if not to_email:
        return
    await send_email(
        to_email,
        f"Odemeniz alindi - {fresh['reference_code']}",
        payment_received_html(serialize_doc(fresh)),
        kind="payment_received",
        meta={"reference_code": fresh["reference_code"]},
    )


async def _mark_paid(session_id: str) -> None:
    """Idempotent: flips the transaction + application to paid and emails once."""
    tx = await _claim_transaction(session_id)
    if not tx:
        return
    if tx.get("order_id"):
        await _mark_order_paid(session_id, tx)
        return
    app_doc = await applications_col.find_one({"id": tx.get("application_id")})
    if not app_doc:
        return
    await _apply_application_payment(app_doc, session_id)
    await _notify_application_payment(app_doc["id"])


def _checkout_origin(origin_url: str | None) -> str:
    """Istemciden gelen origin degerini dogrular."""
    origin = (origin_url or "").rstrip("/")
    if not origin.startswith("http"):
        raise HTTPException(400, "Gecersiz origin_url.")
    return origin


def _application_metadata(app_doc: dict) -> dict:
    """Stripe metadata alanlarini hazirlar (tek/coklu yolcu uyumlu)."""
    metadata = {
        "application_id": str(app_doc["id"]),
        "reference_code": str(app_doc["reference_code"]),
    }
    # Phase 2 tek yolcu basvurulari ile geriye donuk uyumluluk
    if "visa_type_id" in app_doc:
        metadata["visa_type_id"] = str(app_doc["visa_type_id"])
    return metadata


async def _open_checkout_session(sc, req: CheckoutSessionRequest):
    """Stripe oturumu acar; hatalari kullanici dostu mesaja cevirir."""
    session = None
    try:
        session = await sc.create_checkout_session(req)
    except Exception as exc:
        logger.error("checkout create failed: %s", exc)
        raise HTTPException(
            502, "Odeme sayfasi olusturulamadi. Lutfen tekrar deneyin."
        ) from exc
    if not session or not getattr(session, "session_id", None) or not getattr(session, "url", None):
        raise HTTPException(502, "Odeme sayfasi olusturulamadi. Lutfen tekrar deneyin.")
    return session


@router.post("/payments/checkout")
async def create_checkout(payload: CheckoutRequest, request: Request):
    app_doc = await applications_col.find_one({"id": payload.application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    if app_doc.get("payment", {}).get("status") == "paid":
        raise HTTPException(400, "Bu basvurunun odemesi zaten alinmis.")

    origin = _checkout_origin(payload.origin_url)
    amount = float(app_doc["price"])  # server-side amount only
    currency = (app_doc.get("currency") or "TRY").lower()
    sc = _client(request)

    req = CheckoutSessionRequest(
        amount=amount,
        currency=currency,
        success_url=f"{origin}/odeme/basarili?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{origin}/odeme/iptal?ref={app_doc['reference_code']}",
        metadata=_application_metadata(app_doc),
    )
    session = await _open_checkout_session(sc, req)

    now = datetime.now(timezone.utc)
    await payments_col.insert_one(
        {
            "session_id": session.session_id,
            "application_id": app_doc["id"],
            "reference_code": app_doc["reference_code"],
            "amount": amount,
            "currency": currency,
            "status": "initiated",
            "payment_status": "pending",
            "created_at": now,
            "updated_at": now,
        }
    )
    await applications_col.update_one(
        {"id": app_doc["id"]},
        {"$set": {"payment.session_id": session.session_id, "updated_at": now}},
    )
    return {"checkout_url": session.url, "session_id": session.session_id}


@router.post("/payments/bank-transfer")
async def choose_bank_transfer(payload: CheckoutRequest):
    """Havale/EFT ile odeme secildiginde basvuruyu 'transfer bekleniyor' durumuna alir."""
    app_doc = await applications_col.find_one({"id": payload.application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    if (app_doc.get("payment") or {}).get("status") == "paid":
        raise HTTPException(400, "Bu basvurunun odemesi zaten alinmis.")

    now = datetime.now(timezone.utc)
    await applications_col.update_one(
        {"id": app_doc["id"]},
        {
            "$set": {
                "payment.method": "bank_transfer",
                "payment.status": "awaiting_transfer",
                "payment.selected_at": now,
                "updated_at": now,
            },
            "$push": {
                "status_history": {
                    "status": app_doc.get("status", "payment_pending"),
                    "at": now,
                    "note": "Musteri havale/EFT ile odemeyi secti",
                }
            },
        },
    )
    fresh = await applications_col.find_one({"id": app_doc["id"]})
    from routes_store import sync_application_order_payment

    await sync_application_order_payment(app_doc["id"], "awaiting_transfer", method="bank_transfer")
    settings_doc = await settings_col.find_one({"key": "bank_transfer"})
    bank = (settings_doc or {}).get("value") or BANK_TRANSFER
    to_email = (fresh.get("contact") or {}).get("email")
    if to_email:
        await send_email(
            to_email,
            f"Havale/EFT odeme bilgileri - {fresh['reference_code']}",
            bank_transfer_html(serialize_doc(fresh), bank),
            kind="bank_transfer_instructions",
            meta={"reference_code": fresh["reference_code"]},
        )
    return {
        "ok": True,
        "reference_code": fresh["reference_code"],
        "amount": fresh.get("price"),
        "currency": fresh.get("currency", "TRY"),
        "bank": bank,
    }


@router.get("/payments/status/{session_id}")
async def payment_status(session_id: str, request: Request):
    record = await payments_col.find_one({"session_id": session_id})
    if not record:
        raise HTTPException(404, "Odeme kaydi bulunamadi.")
    if record.get("payment_status") != "paid":
        try:
            sc = _client(request)
            st = await sc.get_checkout_status(session_id)
            if st.payment_status == "paid" or st.status == "complete":
                await _mark_paid(session_id)
                record = await payments_col.find_one({"session_id": session_id})
            elif st.status == "expired":
                await payments_col.update_one(
                    {"session_id": session_id},
                    {"$set": {"status": "expired", "payment_status": "expired"}},
                )
                record = await payments_col.find_one({"session_id": session_id})
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning("status poll failed: %s", exc)
    return {
        "session_id": record["session_id"],
        "status": record["status"],
        "payment_status": record["payment_status"],
        "reference_code": record.get("reference_code"),
        "amount": record.get("amount"),
        "currency": record.get("currency"),
    }


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    try:
        sc = _client(request)
        result = await sc.handle_webhook(body, signature)
    except Exception as exc:
        logger.error("webhook error: %s", exc)
        raise HTTPException(400, "Invalid webhook")
    if result.payment_status == "paid":
        await _mark_paid(result.session_id)
    return {"status": "ok"}


# ------------------------------------------------- magaza (eSIM / sigorta) odeme
@router.post("/orders/{order_id}/checkout")
async def create_order_checkout(order_id: str, payload: dict, request: Request):
    """eSIM / sigorta siparisi icin Stripe odeme sayfasi olusturur."""
    from db import orders_col

    order = await orders_col.find_one({"id": order_id})
    if not order:
        raise HTTPException(404, "Siparis bulunamadi.")
    if (order.get("payment") or {}).get("status") == "paid":
        raise HTTPException(400, "Bu siparisin odemesi zaten alinmis.")

    origin = (payload.get("origin_url") or "").rstrip("/")
    if not origin.startswith("http"):
        raise HTTPException(400, "Gecersiz origin_url.")

    amount = float(order["price"])
    currency = (order.get("currency") or "TRY").lower()
    sc = _client(request)
    req = CheckoutSessionRequest(
        amount=amount,
        currency=currency,
        success_url=f"{origin}/siparis/{order['reference_code']}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{origin}/siparis/{order['reference_code']}?iptal=1",
        metadata={"order_id": str(order["id"]), "reference_code": str(order["reference_code"])},
    )
    session = await _open_checkout_session(sc, req)

    now = datetime.now(timezone.utc)
    await payments_col.insert_one(
        {
            "session_id": session.session_id,
            "order_id": order["id"],
            "reference_code": order["reference_code"],
            "amount": amount,
            "currency": currency,
            "status": "initiated",
            "payment_status": "pending",
            "created_at": now,
            "updated_at": now,
        }
    )
    await orders_col.update_one(
        {"id": order["id"]},
        {"$set": {"payment.session_id": session.session_id, "payment.method": "card", "updated_at": now}},
    )
    return {"checkout_url": session.url, "session_id": session.session_id}
