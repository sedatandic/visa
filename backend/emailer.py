"""Resend transactional email with graceful degradation.

If RESEND_API_KEY is not configured the send is recorded as "skipped" and the
application flow is never interrupted.
"""
import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from db import email_outbox_col

logger = logging.getLogger(__name__)

BRAND = "VizeAtlas Dubai"


def _wrap(title: str, body_html: str) -> str:
    return f"""
<div style="margin:0;padding:24px;background-color:#FBF7F0;font-family:Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;background-color:#ffffff;border:1px solid #D9E2EC;border-radius:12px;">
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


async def send_email(to: str, subject: str, html: str, kind: str = "generic", meta: Optional[dict] = None) -> dict:
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
    symbol = "₺" if (currency or "TRY").upper() == "TRY" else (currency or "").upper()
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" {symbol}"


def _contact_name(app_doc: dict) -> str:
    contact = app_doc.get("contact") or {}
    if contact.get("full_name"):
        return contact["full_name"]
    applicant = app_doc.get("applicant") or {}
    return f"{applicant.get('first_name','')} {applicant.get('last_name','')}".strip()


def _contact_email(app_doc: dict) -> str:
    contact = app_doc.get("contact") or {}
    return contact.get("email") or (app_doc.get("applicant") or {}).get("email") or ""


def _travelers_table(app_doc: dict) -> str:
    travelers = app_doc.get("travelers") or []
    if not travelers:
        return ""
    rows = "".join(
        f'<tr><td style="padding:8px 10px;border-top:1px solid #E3E8EF;font-size:13px;">{i + 1}. {t.get("first_name","")} {t.get("last_name","")}'
        f'{" (Çocuk)" if t.get("applicant_type") == "child" else ""}</td>'
        f'<td style="padding:8px 10px;border-top:1px solid #E3E8EF;font-size:13px;">{t.get("visa_short_name") or t.get("visa_type_name","")}</td>'
        f'<td style="padding:8px 10px;border-top:1px solid #E3E8EF;font-size:13px;font-weight:600;text-align:right;">{money(t.get("price", 0), t.get("currency", "TRY"))}</td></tr>'
        for i, t in enumerate(travelers)
    )
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
        'style="margin:16px 0;border:1px solid #E3E8EF;border-radius:8px;border-collapse:collapse;">'
        '<tr style="background-color:#F6F8FB;">'
        '<td style="padding:8px 10px;font-size:11px;text-transform:uppercase;color:#52606D;">Yolcu</td>'
        '<td style="padding:8px 10px;font-size:11px;text-transform:uppercase;color:#52606D;">Vize</td>'
        '<td style="padding:8px 10px;font-size:11px;text-transform:uppercase;color:#52606D;text-align:right;">Tutar</td>'
        f"</tr>{rows}</table>"
    )


def _discount_row(title: str, amount: float, rate: float, currency: str) -> str:
    """Indirim satiri (yuzde etiketi + negatif tutar)."""
    pct = int(round((rate or 0) * 100))
    return _row(f"{title} (%{pct})", "- " + money(amount, currency))


def _store_item_label(item: dict) -> str:
    """Ek urun satirinin etiketi; gecerlilik tarihleri varsa ekler."""
    label = f"{item['name']} x{item['quantity']}"
    if not item.get("starts_on"):
        return label
    label += f" ({_tr_date(item['starts_on'])}"
    label += f" - {_tr_date(item['ends_on'])})" if item.get("ends_on") else " itibaren)"
    return label


def _pricing_block(app_doc: dict) -> str:
    p = app_doc.get("pricing") or {}
    if not p:
        return _row("Tutar", money(app_doc.get("price", 0), app_doc.get("currency", "TRY")))
    currency = p.get("currency", "TRY")

    lines = [_row("Vize bedelleri", money(p.get("subtotal", 0), currency))]
    if p.get("family_discount"):
        lines.append(
            _discount_row("Aile indirimi", p["family_discount"], p.get("family_discount_rate", 0), currency)
        )
    lines += [
        _row(f"{a['name']} x{a['quantity']}", money(a["total"], currency))
        for a in p.get("addons") or []
    ]
    lines += [
        _row(_store_item_label(s), money(s["total"], currency))
        for s in p.get("store_items") or []
    ]
    if p.get("bundle_discount"):
        lines.append(
            _discount_row(
                p.get("bundle_discount_title") or "Seyahat paketi indirimi",
                p["bundle_discount"],
                p.get("bundle_discount_rate", 0),
                currency,
            )
        )
    lines.append(
        _row("<strong>Toplam</strong>", "<strong>" + money(p.get("total", 0), currency) + "</strong>")
    )
    return "".join(lines)


def applicant_received_html(app_doc: dict) -> str:
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {_contact_name(app_doc)},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Dubai (BAE) vize başvurunuz sistemimize başarıyla kaydedildi. Belgeleriniz danışmanlarımız tarafından kontrol edilecek ve süreç boyunca sizi bilgilendireceğiz.</p>
    <div style="background-color:#F4EBDD;border:1px solid #E4D6BF;border-radius:10px;padding:16px;margin:0 0 8px;">
      <div style="font-size:12px;color:#52606D;margin-bottom:4px;">Takip Kodunuz</div>
      <div style="font-size:24px;font-weight:bold;letter-spacing:2px;color:#0B1F33;">{app_doc.get('reference_code','')}</div>
    </div>
    {_travelers_table(app_doc)}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_pricing_block(app_doc)}
      {_row('Ödeme Durumu', 'Ödendi' if (app_doc.get('payment') or {}).get('status') == 'paid' else 'Bekliyor')}
      {_row('Tahmini Sonuçlanma', app_doc.get('processing_days', ''))}
    </table>
    <p style="margin:20px 0 0;font-size:13px;line-height:21px;color:#52606D;">Takip kodunuz ve soyadınızla başvurunuzu sitemizin "Başvuru Takip" sayfasından her an görüntüleyebilirsiniz.</p>
    """
    return _wrap("Başvurunuz alındı", body)


def admin_notify_html(app_doc: dict) -> str:
    t = app_doc.get("travel") or {}
    contact = app_doc.get("contact") or {}
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;">Yeni bir vize başvurusu alındı.</p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Takip Kodu', app_doc.get('reference_code',''))}
      {_row('İletişim', _contact_name(app_doc))}
      {_row('E-posta', contact.get('email',''))}
      {_row('Telefon', contact.get('phone',''))}
      {_row('Yolcu sayısı', str(len(app_doc.get('travelers') or [])))}
      {_row('Gidiş', t.get('arrival_date','-'))}
      {_row('Dönüş', t.get('departure_date','-'))}
    </table>
    {_travelers_table(app_doc)}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_pricing_block(app_doc)}
    </table>
    """
    return _wrap("Yeni başvuru", body)


def payment_received_html(app_doc: dict) -> str:
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {_contact_name(app_doc)},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">{money(app_doc.get('price', 0), app_doc.get('currency', 'TRY'))} tutarındaki ödemeniz başarıyla alındı. Başvurunuz işleme alınmıştır.</p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Takip Kodu', app_doc.get('reference_code',''))}
      {_row('Yolcu sayısı', str(len(app_doc.get('travelers') or []) or 1))}
    </table>
    {_travelers_table(app_doc)}
    """
    return _wrap("Ödemeniz alındı", body)


def bank_transfer_html(app_doc: dict, bank: dict) -> str:
    steps = "".join(
        f'<li style="margin:0 0 6px;font-size:13px;line-height:21px;">{s}</li>'
        for s in (bank.get("steps") or [])
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {_contact_name(app_doc)},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Başvurunuz oluşturuldu. Ödemenizi aşağıdaki hesaba havale/EFT ile gönderdiğinizde başvurunuz işleme alınacaktır.</p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Takip Kodu', app_doc.get('reference_code',''))}
      {_row('Tutar', money(app_doc.get('price', 0), app_doc.get('currency', 'TRY')))}
      {_row('Hesap Sahibi', bank.get('account_name',''))}
      {_row('Banka', bank.get('bank_name',''))}
      {_row('IBAN', bank.get('iban',''))}
    </table>
    <ul style="margin:16px 0 0;padding-left:18px;color:#52606D;">{steps}</ul>
    <p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#52606D;">{bank.get('note','')}</p>
    """
    return _wrap("Havale / EFT ödeme bilgileri", body)


def status_change_html(app_doc: dict, status_label: str, note: str = "") -> str:
    note_html = (
        f'<p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#52606D;">Danışman notu: {note}</p>'
        if note
        else ""
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {_contact_name(app_doc)},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">{app_doc.get('reference_code','')} kodlu başvurunuzun durumu güncellendi.</p>
    <div style="background-color:#F6F8FB;border:1px solid #D9E2EC;border-radius:10px;padding:16px;">
      <div style="font-size:12px;color:#52606D;margin-bottom:4px;">Yeni Durum</div>
      <div style="font-size:18px;font-weight:bold;color:#0B1F33;">{status_label}</div>
    </div>
    {note_html}
    """
    return _wrap("Başvuru durumu güncellendi", body)


def visa_ready_html(app_doc: dict, download_url: str, message: str = "") -> str:
    message_html = (
        f'<p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#52606D;">{message}</p>'
        if message
        else ""
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {_contact_name(app_doc)},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Müjde! {app_doc.get('reference_code','')} kodlu başvurunuz <strong>onaylandı</strong>. Vize belgenizi aşağıdaki butondan indirebilirsiniz.</p>
    {_travelers_table(app_doc)}
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:8px 0 4px;">
      <tr><td style="background-color:#0EA5A4;border-radius:8px;">
        <a href="{download_url}" style="display:inline-block;padding:14px 26px;color:#ffffff;font-size:15px;font-weight:bold;text-decoration:none;">Vize belgenizi indir</a>
      </td></tr>
    </table>
    <p style="margin:12px 0 0;font-size:12px;line-height:20px;color:#52606D;">Buton çalışmıyorsa bu adresi tarayıcınıza kopyalayabilirsiniz:<br/>{download_url}</p>
    <p style="margin:16px 0 0;font-size:13px;line-height:21px;">Vizeniz elektroniktir ve pasaportunuza işlenmez. Sınır kapısında bu belgeyi (baskısını veya telefonunuzdaki kopyasını) göstermeniz yeterlidir.</p>
    {message_html}
    <p style="margin:20px 0 0;font-size:13px;line-height:21px;color:#52606D;">İyi yolculuklar dileriz.</p>
    """
    return _wrap("Vizeniz hazır", body)


def document_reminder_html(app_doc: dict, missing: list, upload_url: str = "") -> str:
    """Eksik belge hatirlatmasi: eksik listesi + yukleme baglantisi."""
    items = []
    for m in missing:
        who = f" — {m['traveler_name']}" if m.get("traveler_name") else ""
        items.append(
            '<li style="margin:0 0 8px;font-size:14px;line-height:22px;color:#0B1F33;">'
            f"<strong>{m['label']}</strong>{who}</li>"
        )
    button_html = ""
    if upload_url:
        button_html = f"""
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 4px;">
      <tr><td style="background-color:#B3123A;border-radius:8px;">
        <a href="{upload_url}" style="display:inline-block;padding:14px 26px;color:#ffffff;font-size:15px;font-weight:bold;text-decoration:none;">Eksik belgeleri yükle</a>
      </td></tr>
    </table>
    <p style="margin:12px 0 0;font-size:12px;line-height:20px;color:#52606D;">Buton çalışmıyorsa bu adresi tarayıcınıza kopyalayabilirsiniz:<br/>{upload_url}</p>
    """
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {_contact_name(app_doc)},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      {app_doc.get('reference_code','')} kodlu Dubai vize başvurunuzu yetkili mercilere iletebilmemiz için
      aşağıdaki belgelere ihtiyacımız var. Belgeleriniz tamamlandığı anda başvurunuz işleme alınır.
    </p>
    <div style="background-color:#FFF7ED;border:1px solid #FED7AA;border-radius:10px;padding:16px;">
      <div style="font-size:12px;font-weight:bold;color:#B45309;margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px;">Eksik Belgeler</div>
      <ul style="margin:0;padding-left:18px;">{''.join(items)}</ul>
    </div>
    {button_html}
    <p style="margin:18px 0 0;font-size:13px;line-height:21px;color:#52606D;">
      Belgelerinizi telefonunuzla fotoğraflayıp yükleyebilirsiniz. Yükleme sırasında takip kodunuz ve
      soyadınız sorulur. Sorunuz olursa bu e-postayı yanıtlayabilir veya WhatsApp üzerinden bize yazabilirsiniz.
    </p>
    """
    return _wrap("Eksik belge hatırlatması", body)


def documents_completed_admin_html(app_doc: dict, uploaded_keys: list) -> str:
    """Musteri eksik belgeleri yukledi - admin bildirimi."""
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      {app_doc.get('reference_code','')} kodlu başvuru için müşteri yeni belge yükledi.
    </p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Takip Kodu', app_doc.get('reference_code',''))}
      {_row('İletişim', _contact_name(app_doc))}
      {_row('Yüklenen belgeler', ', '.join(uploaded_keys) or '-')}
    </table>
    """
    return _wrap("Müşteri belge yükledi", body)


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


def login_code_html(code: str, ttl_minutes: int, account_url: str = "") -> str:
    """Musteri girisi icin tek kullanimlik kod."""
    link = (
        f'<p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#52606D;">'
        f'Giris sayfasi: <a href="{account_url}" style="color:#B3123A;">{account_url}</a></p>'
        if account_url
        else ""
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      Basvurularinizi goruntulemek ve yarim kalan basvurunuza devam etmek icin giris kodunuz:
    </p>
    <div style="background-color:#F1F5F9;border:1px solid #E2E8F0;border-radius:10px;padding:18px;text-align:center;">
      <div style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#0B1F33;">{code}</div>
      <div style="margin-top:8px;font-size:12px;color:#52606D;">Kod {ttl_minutes} dakika gecerlidir.</div>
    </div>
    {link}
    <p style="margin:18px 0 0;font-size:12px;line-height:20px;color:#52606D;">
      Bu kodu siz talep etmediyseniz bu e-postayi dikkate almayabilirsiniz.
    </p>
    """
    return _wrap("Giris kodunuz", body)


def draft_saved_html(draft: dict, resume_url: str = "") -> str:
    """Taslak kaydedildi bilgilendirmesi."""
    button = ""
    if resume_url:
        button = f"""
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 4px;">
      <tr><td style="background-color:#B3123A;border-radius:8px;">
        <a href="{resume_url}" style="display:inline-block;padding:14px 26px;color:#ffffff;font-size:15px;font-weight:bold;text-decoration:none;">Basvuruya devam et</a>
      </td></tr>
    </table>
    <p style="margin:12px 0 0;font-size:12px;line-height:20px;color:#52606D;">Buton calismiyorsa: {resume_url}</p>
    """
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      Basvurunuz kaydedildi. Diledigini zaman kaldiginiz yerden devam edebilirsiniz.
    </p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Devam kodu', draft.get('resume_code', ''))}
      {_row('Yolcu sayisi', draft.get('traveler_count', 1))}
    </table>
    {button}
    <p style="margin:18px 0 0;font-size:12px;line-height:20px;color:#52606D;">
      Kaydedilen bilgiler 60 gun saklanir. Belgeleriniz yalnizca basvurunuz icin kullanilir.
    </p>
    """
    return _wrap("Basvurunuz kaydedildi", body)


def draft_reminder_html(draft: dict, resume_url: str = "") -> str:
    """Yarim kalan basvuru hatirlatmasi (sepeti kurtarma)."""
    button = ""
    if resume_url:
        button = f"""
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 4px;">
      <tr><td style="background-color:#B3123A;border-radius:8px;">
        <a href="{resume_url}" style="display:inline-block;padding:14px 26px;color:#ffffff;font-size:15px;font-weight:bold;text-decoration:none;">Basvuruma devam et</a>
      </td></tr>
    </table>
    <p style="margin:12px 0 0;font-size:12px;line-height:20px;color:#52606D;">Buton calismiyorsa: {resume_url}</p>
    """
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Merhaba,</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      Dubai vize basvurunuz yarim kalmis gorunuyor. Bilgileriniz kayitli; kaldiginiz yerden
      devam edip basvurunuzu birkac dakikada tamamlayabilirsiniz.
    </p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Devam kodu', draft.get('resume_code', ''))}
      {_row('Yolcu sayisi', draft.get('traveler_count', 1))}
    </table>
    {button}
    <p style="margin:18px 0 0;font-size:13px;line-height:21px;color:#52606D;">
      Seyahat tarihiniz yaklastiysa ekspres hizmetimizle basvurunuzu onceliklendirebiliriz.
      Sorulariniz icin bu e-postayi yanitlayabilirsiniz.
    </p>
    """
    return _wrap("Basvurunuz yarim kaldi", body)


def _tr_date(value: str | None) -> str:
    """ISO tarihi gg.aa.yyyy formatina cevirir."""
    raw = (value or "").strip()[:10]
    try:
        d = datetime.strptime(raw, "%Y-%m-%d")
        return d.strftime("%d.%m.%Y")
    except Exception:
        return raw


def _date_range_note(item: dict) -> str:
    """Urunun gecerlilik tarih araligi (seyahat tarihine gore)."""
    starts = item.get("starts_on")
    ends = item.get("ends_on")
    if not starts:
        return ""
    text = f"{_tr_date(starts)} tarihinde baslar"
    if ends:
        text += f" · {_tr_date(ends)} tarihine kadar gecerli"
    return f'<div style="font-size:12px;color:#52606D;margin-top:2px;">{text}</div>'


def _order_items_rows(order: dict) -> str:
    rows = []
    for item in order.get("items") or []:
        rows.append(
            f'<tr><td style="padding:8px 0;font-size:13px;color:#0B1F33;">{item.get("name","")}'
            f' <span style="color:#52606D;">x{item.get("quantity",1)}</span>'
            f'{_date_range_note(item)}</td>'
            f'<td style="padding:8px 0;font-size:13px;text-align:right;color:#0B1F33;">'
            f'{item.get("total",0):,.0f} TL</td></tr>'
        )
    return "".join(rows)


def order_received_html(order: dict, bank: dict | None = None) -> str:
    """eSIM / seyahat sigortasi siparis onayi."""
    bank_html = ""
    if bank:
        bank_html = f"""
    <div style="margin-top:18px;background-color:#F1F5F9;border:1px solid #E2E8F0;border-radius:10px;padding:16px;">
      <div style="font-size:12px;font-weight:bold;color:#0B1F33;margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px;">Havale / EFT Bilgileri</div>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        {_row('Banka', bank.get('bank_name',''))}
        {_row('Hesap sahibi', bank.get('account_name',''))}
        {_row('IBAN', bank.get('iban',''))}
        {_row('Aciklama', order.get('reference_code',''))}
      </table>
      <p style="margin:12px 0 0;font-size:12px;line-height:20px;color:#52606D;">
        Aciklama alanina siparis kodunuzu yazmayi unutmayin. Odemeniz onaylandiginda teslimat yapilir.
      </p>
    </div>
    """
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayin {order.get('contact',{}).get('full_name','')},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      Siparisiniz alindi. Odemeniz onaylandiktan sonra eSIM QR kodunuz ve/veya sigorta policeniz
      e-posta ile size iletilecek.
    </p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Siparis kodu', order.get('reference_code',''))}
      {_row('Odeme yontemi', 'Havale/EFT' if (order.get('payment') or {}).get('method') == 'bank_transfer' else 'Kredi/banka karti')}
    </table>
    <div style="margin-top:16px;border-top:1px solid #E2E8F0;padding-top:8px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        {_order_items_rows(order)}
        {_row('Seyahat paketi indirimi (%10)', '- ' + f"{order.get('bundle_discount',0):,.0f} TL") if order.get('bundle_discount') else ''}
        <tr><td style="padding:10px 0 0;font-size:14px;font-weight:bold;border-top:1px solid #E2E8F0;">Toplam</td>
        <td style="padding:10px 0 0;font-size:14px;font-weight:bold;text-align:right;border-top:1px solid #E2E8F0;">{order.get('price',0):,.0f} TL</td></tr>
      </table>
    </div>
    {bank_html}
    """
    return _wrap("Siparisiniz alindi", body)


def order_admin_html(order: dict) -> str:
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Yeni eSIM / sigorta siparisi olusturuldu.</p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Siparis kodu', order.get('reference_code',''))}
      {_row('Musteri', order.get('contact',{}).get('full_name',''))}
      {_row('E-posta', order.get('contact',{}).get('email',''))}
      {_row('Telefon', order.get('contact',{}).get('phone',''))}
      {_row('Tutar', f"{order.get('price',0):,.0f} TL")}
      {_row('Odeme', (order.get('payment') or {}).get('method',''))}
    </table>
    <div style="margin-top:12px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{_order_items_rows(order)}</table>
    </div>
    """
    return _wrap("Yeni siparis", body)


def order_delivered_html(order: dict, links: list, message: str = "") -> str:
    """eSIM QR / police teslimati."""
    link_html = "".join(
        f'<tr><td style="padding:8px 0;"><a href="{l["url"]}" style="color:#B3123A;font-size:14px;font-weight:bold;">{l["label"]}</a></td></tr>'
        for l in links
    )
    note = (
        f'<p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#0B1F33;">{message}</p>'
        if message
        else ""
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayin {order.get('contact',{}).get('full_name','')},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      {order.get('reference_code','')} kodlu siparisiniz hazir. Belgelerinizi asagidaki baglantilardan
      indirebilirsiniz.
    </p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{link_html}</table>
    {note}
    <p style="margin:18px 0 0;font-size:12px;line-height:20px;color:#52606D;">
      eSIM kurulumu: Ayarlar > Mobil Veri > eSIM ekle > QR kodu tarat. Kurulum sirasinda internet
      baglantisi gereklidir.
    </p>
    """
    return _wrap("Siparisiniz hazir", body)
