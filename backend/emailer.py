"""Resend transactional email with graceful degradation.

If RESEND_API_KEY is not configured the send is recorded as "skipped" and the
application flow is never interrupted.
"""
import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone

from db import email_outbox_col

logger = logging.getLogger(__name__)

BRAND = "VizeAtlas Dubai"


def _wrap(title: str, body_html: str) -> str:
    return f"""
<div style="margin:0;padding:24px;background-color:#FBF7F0;font-family:Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;margin:0 auto;background-color:#ffffff;border:1px solid #D9E2EC;border-radius:12px;">
    <tr><td style="padding:20px 24px;border-bottom:1px solid #D9E2EC;background-color:#0B1F33;border-radius:12px 12px 0 0;">
      <span style="color:#ffffff;font-size:18px;font-weight:bold;letter-spacing:-0.4px;">{BRAND}</span>
    </td></tr>
    <tr><td style="padding:28px 24px;color:#0B1F33;">
      <h1 style="margin:0 0 16px;font-size:20px;color:#0B1F33;">{title}</h1>
      {body_html}
    </td></tr>
    <tr><td style="padding:16px 24px;border-top:1px solid #D9E2EC;color:#52606D;font-size:12px;background-color:#F6F8FB;border-radius:0 0 12px 12px;">
      Bu e-posta {BRAND} tarafından gönderilmiştir. Sorularınız için bu e-postayı yanıtlayabilirsiniz.
    </td></tr>
  </table>
</div>
"""


def _row(label: str, value: str) -> str:
    return (
        f'<tr><td style="padding:6px 0;color:#52606D;font-size:13px;width:42%;">{label}</td>'
        f'<td style="padding:6px 0;color:#0B1F33;font-size:13px;font-weight:600;">{value}</td></tr>'
    )


async def send_email(to: str, subject: str, html: str, kind: str = "generic", meta: dict | None = None) -> dict:
    """Never raises. Always records the attempt in email_outbox."""
    api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
    sender_email = os.environ.get("SENDER_EMAIL") or "onboarding@resend.dev"
    sender = f"{BRAND} <{sender_email}>"
    result = {"status": "skipped", "reason": "RESEND_API_KEY tanimli degil"}
    if api_key and not api_key.startswith("re_placeholder"):
        try:
            import resend

            resend.api_key = api_key
            res = await asyncio.to_thread(
                resend.Emails.send,
                {"from": sender, "to": [to], "subject": subject, "html": html},
            )
            result = {"status": "sent", "provider_id": (res or {}).get("id")}
        except Exception as exc:  # pragma: no cover
            logger.error("Resend send failed: %s", exc)
            result = {"status": "error", "reason": str(exc)[:400]}
    try:
        await email_outbox_col.insert_one(
            {
                "id": str(uuid.uuid4()),
                "to": to,
                "subject": subject,
                "kind": kind,
                "meta": meta or {},
                "created_at": datetime.now(timezone.utc),
                **result,
            }
        )
    except Exception as exc:  # pragma: no cover
        logger.error("email_outbox insert failed: %s", exc)
    return result


def money(amount: float, currency: str = "TRY") -> str:
    symbol = "₺" if currency.upper() == "TRY" else currency.upper()
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" {symbol}"


def applicant_received_html(app_doc: dict) -> str:
    a = app_doc.get("applicant", {})
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {a.get('first_name','')} {a.get('last_name','')},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Dubai (BAE) vize başvurunuz sistemimize başarıyla kaydedildi. Belgeleriniz danışmanlarımız tarafından kontrol edilecek ve süreç boyunca sizi bilgilendireceğiz.</p>
    <div style="background-color:#F4EBDD;border:1px solid #E4D6BF;border-radius:10px;padding:16px;margin:0 0 20px;">
      <div style="font-size:12px;color:#52606D;margin-bottom:4px;">Takip Kodunuz</div>
      <div style="font-size:24px;font-weight:bold;letter-spacing:2px;color:#0B1F33;">{app_doc.get('reference_code','')}</div>
    </div>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Vize Tipi', app_doc.get('visa_type_name',''))}
      {_row('Hizmet Bedeli', money(app_doc.get('price',0), app_doc.get('currency','TRY')))}
      {_row('Ödeme Durumu', 'Ödendi' if app_doc.get('payment',{}).get('status')=='paid' else 'Bekliyor')}
      {_row('Tahmini Sonuçlanma', app_doc.get('processing_days',''))}
    </table>
    <p style="margin:20px 0 0;font-size:13px;line-height:21px;color:#52606D;">Takip kodunuz ve soyadınızla başvurunuzu sitemizin "Başvuru Takip" sayfasından her an görüntüleyebilirsiniz.</p>
    """
    return _wrap("Başvurunuz alındı", body)


def admin_notify_html(app_doc: dict) -> str:
    a = app_doc.get("applicant", {})
    t = app_doc.get("travel", {})
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;">Yeni bir vize başvurusu alındı.</p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Takip Kodu', app_doc.get('reference_code',''))}
      {_row('Ad Soyad', f"{a.get('first_name','')} {a.get('last_name','')}")}
      {_row('E-posta', a.get('email',''))}
      {_row('Telefon', a.get('phone',''))}
      {_row('Pasaport No', a.get('passport_no',''))}
      {_row('Vize Tipi', app_doc.get('visa_type_name',''))}
      {_row('Tutar', money(app_doc.get('price',0), app_doc.get('currency','TRY')))}
      {_row('Gidiş', t.get('arrival_date','-'))}
      {_row('Dönüş', t.get('departure_date','-'))}
    </table>
    """
    return _wrap("Yeni başvuru", body)


def payment_received_html(app_doc: dict) -> str:
    a = app_doc.get("applicant", {})
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {a.get('first_name','')} {a.get('last_name','')},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">{money(app_doc.get('price',0), app_doc.get('currency','TRY'))} tutarındaki ödemeniz başarıyla alındı. Başvurunuz işleme alınmıştır.</p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Takip Kodu', app_doc.get('reference_code',''))}
      {_row('Vize Tipi', app_doc.get('visa_type_name',''))}
    </table>
    """
    return _wrap("Ödemeniz alındı", body)


def status_change_html(app_doc: dict, status_label: str, note: str = "") -> str:
    a = app_doc.get("applicant", {})
    note_html = (
        f'<p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#52606D;">Danışman notu: {note}</p>'
        if note
        else ""
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {a.get('first_name','')} {a.get('last_name','')},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">{app_doc.get('reference_code','')} kodlu başvurunuzun durumu güncellendi.</p>
    <div style="background-color:#F6F8FB;border:1px solid #D9E2EC;border-radius:10px;padding:16px;">
      <div style="font-size:12px;color:#52606D;margin-bottom:4px;">Yeni Durum</div>
      <div style="font-size:18px;font-weight:bold;color:#0B1F33;">{status_label}</div>
    </div>
    {note_html}
    """
    return _wrap("Başvuru durumu güncellendi", body)


def contact_admin_html(msg: dict) -> str:
    body = f"""
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Ad Soyad', msg.get('name',''))}
      {_row('E-posta', msg.get('email',''))}
      {_row('Telefon', msg.get('phone','-'))}
      {_row('Konu', msg.get('subject','-'))}
    </table>
    <p style="margin:16px 0 0;font-size:14px;line-height:22px;white-space:pre-wrap;">{msg.get('message','')}</p>
    """
    return _wrap("Yeni iletişim mesajı", body)
