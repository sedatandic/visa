import logging
import os
from datetime import datetime, timezone

from emergentintegrations.payments.stripe.checkout import (
    CheckoutSessionRequest,
    StripeCheckout,
)
from fastapi import APIRouter, HTTPException, Request

from content import BANK_TRANSFER
from db import applications_col, payments_col, serialize_doc
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


async def _mark_paid(session_id: str):
    """Idempotent: flips the transaction + application to paid and emails once."""
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
        return
    tx = await payments_col.find_one({"session_id": session_id})
    if not tx:
        return
    app_doc = await applications_col.find_one({"id": tx.get("application_id")})
    if not app_doc:
        return
    now = datetime.now(timezone.utc)
    await applications_col.update_one(
        {"id": app_doc["id"]},
        {
            "$set": {
                "payment.status": "paid",
                "payment.session_id": session_id,
                "payment.paid_at": now,
                "status": "reviewing" if app_doc.get("status") in ("submitted", "payment_pending") else app_doc.get("status"),
                "updated_at": now,
            },
            "$push": {
                "status_history": {"status": "reviewing", "at": now, "note": "Odeme alindi, basvuru incelemeye alindi"}
            },
        },
    )
    fresh = await applications_col.find_one({"id": app_doc["id"]})
    to_email = (fresh.get("contact") or {}).get("email") or (fresh.get("applicant") or {}).get("email")
    if to_email:
        await send_email(
            to_email,
            f"Odemeniz alindi - {fresh['reference_code']}",
            payment_received_html(serialize_doc(fresh)),
            kind="payment_received",
            meta={"reference_code": fresh["reference_code"]},
        )


@router.post("/payments/checkout")
async def create_checkout(payload: CheckoutRequest, request: Request):
    app_doc = await applications_col.find_one({"id": payload.application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    if app_doc.get("payment", {}).get("status") == "paid":
        raise HTTPException(400, "Bu basvurunun odemesi zaten alinmis.")

    origin = (payload.origin_url or "").rstrip("/")
    if not origin.startswith("http"):
        raise HTTPException(400, "Gecersiz origin_url.")

    amount = float(app_doc["price"])  # server-side amount only
    currency = (app_doc.get("currency") or "TRY").lower()
    sc = _client(request)
    
    # Build metadata - handle both single and multi-traveler applications
    metadata = {
        "application_id": str(app_doc["id"]),
        "reference_code": str(app_doc["reference_code"]),
    }
    # For backward compatibility with Phase 2 single-traveler apps
    if "visa_type_id" in app_doc:
        metadata["visa_type_id"] = str(app_doc["visa_type_id"])
    
    req = CheckoutSessionRequest(
        amount=amount,
        currency=currency,
        success_url=f"{origin}/odeme/basarili?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{origin}/odeme/iptal?ref={app_doc['reference_code']}",
        metadata=metadata,
    )
    try:
        session = await sc.create_checkout_session(req)
    except Exception as exc:
        logger.error("checkout create failed: %s", exc)
        raise HTTPException(502, "Odeme sayfasi olusturulamadi. Lutfen tekrar deneyin.")

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
    to_email = (fresh.get("contact") or {}).get("email")
    if to_email:
        await send_email(
            to_email,
            f"Havale/EFT odeme bilgileri - {fresh['reference_code']}",
            bank_transfer_html(serialize_doc(fresh), BANK_TRANSFER),
            kind="bank_transfer_instructions",
            meta={"reference_code": fresh["reference_code"]},
        )
    return {
        "ok": True,
        "reference_code": fresh["reference_code"],
        "amount": fresh.get("price"),
        "currency": fresh.get("currency", "TRY"),
        "bank": BANK_TRANSFER,
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
