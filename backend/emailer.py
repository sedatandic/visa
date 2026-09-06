"""Resend transactional email with graceful degradation.

If RESEND_API_KEY is not configured the send is recorded as "skipped" and the
application flow is never interrupted.
"""
import asyncio
import html as html_lib
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Optional

from content import COMPANY, VISA_TYPES
from db import email_outbox_col

logger = logging.getLogger(__name__)

BRAND = "Dubai Vize Hattı"

GOLD = "#B06A29"
INK = "#3E2A14"
MUTED = "#8A7355"
FAINT = "#A08A6B"
LINE = "#EADFCB"

# Pazarlama nitelikli postalar: tek tik abonelik iptali basliklari eklenir
MARKETING_KINDS = {"draft_reminder"}


def _html_to_text(html: str) -> str:
    """HTML govdeden duz metin alternatifi uretir (Gmail HTML-only postalari cezalandirir)."""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>|</p>|</div>|</tr>|</h1>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_lib.unescape(text).replace("\xa0", " ")
    text = re.sub(r"[ \t]{2,}", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


SITE_URL = (os.environ.get("PUBLIC_SITE_URL") or "").strip().strip('"').rstrip("/")
LOGO_URL = f"{SITE_URL}/brand/logo-horizontal-gold-palm.png"


def _contact_footer() -> str:
    """Marka kunyesi: sirket unvanlari + telefon, WhatsApp, e-posta, adresler."""
    site = SITE_URL or "https://www.dubaivizehatti.com"
    site_label = "www.dubaivizehatti.com"
    link = f"color:{GOLD};text-decoration:none;font-weight:600;"
    return f"""
    <tr><td style="padding:22px 26px 6px;background-color:#FBF6EC;border-top:1px solid {LINE};">
      <div style="font-size:13px;font-weight:bold;color:{INK};letter-spacing:.3px;">{BRAND}</div>
      <div style="margin-top:5px;font-size:12px;line-height:19px;color:{MUTED};">
        {COMPANY['legal_name']}<br />
        BAE iştiraki: {COMPANY['dubai_company']}<br />
        TÜRSAB üyesi {COMPANY['tursab_type']}
      </div>
      <div style="margin-top:13px;font-size:12px;line-height:21px;">
        <a href="tel:{COMPANY['phone'].replace(' ', '')}" style="{link}">{COMPANY['phone']}</a>
        <span style="color:{LINE};">&nbsp;|&nbsp;</span>
        <a href="https://wa.me/{COMPANY['whatsapp']}" style="{link}">WhatsApp</a>
        <span style="color:{LINE};">&nbsp;|&nbsp;</span>
        <a href="mailto:{COMPANY['email']}" style="{link}">{COMPANY['email']}</a>
        <span style="color:{LINE};">&nbsp;|&nbsp;</span>
        <a href="{site}" style="{link}">{site_label}</a>
      </div>
      <div style="margin-top:11px;font-size:11px;line-height:18px;color:{FAINT};">
        İstanbul: {COMPANY['address']}<br />
        Dubai: {COMPANY['dubai_address']} · {COMPANY['dubai_phone']}<br />
        Çalışma saatleri: {COMPANY['working_hours']}
      </div>
    </td></tr>
    <tr><td style="padding:14px 26px 22px;background-color:#FBF6EC;font-size:11px;line-height:18px;color:{FAINT};">
      Bu e-posta {BRAND} tarafından gönderilmiştir; sorularınız için doğrudan yanıtlayabilirsiniz.
    </td></tr>
    """


def _wrap(title: str, body_html: str) -> str:
    return f"""
<div style="margin:0;padding:28px 16px;background-color:#F4EBDD;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;background-color:#ffffff;border:1px solid {LINE};border-radius:16px;">
    <tr><td align="center" style="padding:26px 24px 16px;background-color:#FDF8F0;border-radius:16px 16px 0 0;">
      <img src="{LOGO_URL}" width="230" alt="{BRAND}" style="display:block;width:230px;max-width:78%;height:auto;border:0;outline:none;text-decoration:none;" />
      <div style="margin-top:12px;font-size:10px;letter-spacing:2.2px;text-transform:uppercase;color:{FAINT};">
        TÜRSAB Üyesi {COMPANY['tursab_type']}
      </div>
    </td></tr>
    <tr><td style="height:3px;background-color:{GOLD};line-height:3px;font-size:0;">&nbsp;</td></tr>
    <tr><td style="padding:30px 26px 26px;color:{INK};">
      <h1 style="margin:0 0 18px;font-size:21px;line-height:28px;color:{INK};letter-spacing:-.2px;">{title}</h1>
      {body_html}
    </td></tr>
    {_contact_footer()}
  </table>
  <div style="max-width:600px;margin:14px auto 0;text-align:center;font-size:11px;line-height:17px;color:{FAINT};">
    © {datetime.now(timezone.utc).year} {COMPANY['legal_name']} · Tüm hakları saklıdır.
  </div>
</div>
"""


def _row(label: str, value: str) -> str:
    """Bilgi tablosu satiri: ince altin cizgi, kucuk buyuk harf etiket."""
    shown = value if (value or value == 0) and str(value).strip() else "-"
    return (
        f'<tr><td style="padding:11px 2px 11px 0;border-bottom:1px solid {LINE};color:{MUTED};'
        f'font-size:10px;letter-spacing:1.1px;text-transform:uppercase;width:42%;vertical-align:top;">{label}</td>'
        f'<td style="padding:11px 0;border-bottom:1px solid {LINE};color:{INK};font-size:14px;'
        f'font-weight:600;text-align:right;">{shown}</td></tr>'
    )


def _resend_params(to: str, subject: str, html: str, kind: str, sender: str, reply_to: str) -> dict:
    params = {
        "from": sender,
        "to": [to],
        "subject": subject,
        "html": html,
        "text": _html_to_text(html),
    }
    if reply_to:
        params["reply_to"] = reply_to
        if kind in MARKETING_KINDS:
            params["headers"] = {
                "List-Unsubscribe": f"<mailto:{reply_to}?subject=Listeden%20cikar>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            }
    return params


async def _send_via_resend(api_key: str, params: dict) -> dict:
    try:
        import resend

        resend.api_key = api_key
        res = await asyncio.to_thread(resend.Emails.send, params)
        return {"status": "sent", "provider_id": (res or {}).get("id")}
    except Exception as exc:  # pragma: no cover
        logger.error("Resend send failed: %s", exc)
        return {"status": "error", "reason": str(exc)[:400]}


async def _record_attempt(
    to: str, subject: str, kind: str, meta: Optional[dict], result: dict, html: str = ""
) -> None:
    try:
        await email_outbox_col.insert_one(
            {
                "id": str(uuid.uuid4()),
                "to": to,
                "subject": subject,
                "kind": kind,
                "meta": meta or {},
                # Yonetici panelinde tam onizleme icin gövde saklanir
                "html": html[:120000],
                "created_at": datetime.now(timezone.utc),
                **result,
            }
        )
    except Exception as exc:  # pragma: no cover
        logger.error("email_outbox insert failed: %s", exc)


async def send_email(to: str, subject: str, html: str, kind: str = "generic", meta: Optional[dict] = None) -> dict:
    """Never raises. Always records the attempt in email_outbox."""
    api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
    sender_email = (os.environ.get("SENDER_EMAIL") or "onboarding@resend.dev").strip()
    reply_to = (os.environ.get("REPLY_TO_EMAIL") or os.environ.get("ADMIN_EMAIL") or "").strip()
    if sender_email.endswith("@resend.dev"):
        # Paylasimli test alan adi: SPF/DKIM markayla hizalanmadigi icin postalar spam'e duser.
        logger.warning(
            "SENDER_EMAIL paylasimli resend.dev alan adinda; dogrulanmis alan adi kullanin."
        )
    if api_key and not api_key.startswith("re_placeholder"):
        params = _resend_params(to, subject, html, kind, f"{BRAND} <{sender_email}>", reply_to)
        result = await _send_via_resend(api_key, params)
    else:
        result = {"status": "skipped", "reason": "RESEND_API_KEY tanimli degil"}
    await _record_attempt(to, subject, kind, meta, result, html)
    return result


def admin_code_html(code: str, ttl_minutes: int, ip: str = "") -> str:
    """Yonetici paneli girisi icin tek kullanimlik kod."""
    ip_note = (
        f'<p style="margin:12px 0 0;font-size:12px;color:#8A7355;">Talep IP adresi: {ip}</p>'
        if ip
        else ""
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      Yönetim paneline giriş için tek kullanımlık kodunuz:
    </p>
    <div style="background-color:#FBF6EC;border:1px solid #EADFCB;border-radius:10px;padding:18px;text-align:center;">
      <div style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#3E2A14;">{code}</div>
      <div style="margin-top:8px;font-size:12px;color:#8A7355;">Kod {ttl_minutes} dakika geçerlidir.</div>
    </div>
    <p style="margin:18px 0 0;font-size:13px;line-height:21px;">
      Kodu doğruladıktan sonra bu bilgisayarda <strong>30 gün</strong> boyunca tekrar giriş
      yapmanız istenmez.
    </p>
    {ip_note}
    <p style="margin:14px 0 0;font-size:12px;line-height:20px;color:#8A7355;">
      Bu girişi siz talep etmediyseniz kodu kimseyle paylaşmayın ve bize haber verin.
    </p>
    """
    return _wrap("Yönetici giriş kodu", body)


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
        '<tr style="background-color:#FBF6EC;">'
        '<td style="padding:8px 10px;font-size:11px;text-transform:uppercase;color:#8A7355;">Yolcu</td>'
        '<td style="padding:8px 10px;font-size:11px;text-transform:uppercase;color:#8A7355;">Vize</td>'
        '<td style="padding:8px 10px;font-size:11px;text-transform:uppercase;color:#8A7355;text-align:right;">Tutar</td>'
        f"</tr>{rows}</table>"
    )


def _discount_row(title: str, amount: float, rate: float, currency: str) -> str:
    """Indirim satiri (yuzde etiketi + negatif tutar)."""
    pct = int(round((rate or 0) * 100))
    return _row(f"{title} (%{pct})", "- " + money(amount, currency))


def _store_item_label(item: dict) -> str:
    """Ek urun satirinin etiketi; gecerlilik tarihleri varsa ekler."""
    label = f"{item['name']} x{item['quantity']}"
    if item.get("scheduled_date"):
        label += f" ({_tr_date(item['scheduled_date'])}"
        label += f" {item['scheduled_time']})" if item.get("scheduled_time") else ")"
        return label
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
      <div style="font-size:12px;color:#8A7355;margin-bottom:4px;">Takip Kodunuz</div>
      <div style="font-size:24px;font-weight:bold;letter-spacing:2px;color:#3E2A14;">{app_doc.get('reference_code','')}</div>
    </div>
    {_travelers_table(app_doc)}
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_pricing_block(app_doc)}
      {_row('Ödeme Durumu', 'Ödendi' if (app_doc.get('payment') or {}).get('status') == 'paid' else 'Bekliyor')}
      {_row('Tahmini Sonuçlanma', app_doc.get('processing_days', ''))}
    </table>
    <p style="margin:20px 0 0;font-size:13px;line-height:21px;color:#8A7355;">Takip kodunuz ve soyadınızla başvurunuzu sitemizin "Başvuru Takip" sayfasından her an görüntüleyebilirsiniz.</p>
    """
    return _wrap("Başvurunuz alındı", body)


TRAVEL_WINDOW_LABELS = {
    "this_month": "Bu ay içinde",
    "1_3_months": "1-3 ay içinde",
    "3_plus_months": "3 aydan sonra",
    "undecided": "Henüz karar vermedi",
}


def _travel_date_rows(travel: dict) -> str:
    """Seyahat tarihleri; tarih belli degilse secilen zaman araligini gosterir."""
    if travel.get("dates_unknown"):
        window = TRAVEL_WINDOW_LABELS.get(travel.get("travel_window") or "", "")
        value = "Henüz belli değil" + (f" · {window}" if window else "")
        return _row("Seyahat tarihi", value)
    return _row("Gidiş", _tr_date(travel.get("arrival_date")) or "-") + _row(
        "Dönüş", _tr_date(travel.get("departure_date")) or "-"
    )


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
      {_travel_date_rows(t)}
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
    <ul style="margin:16px 0 0;padding-left:18px;color:#8A7355;">{steps}</ul>
    <p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#8A7355;">{bank.get('note','')}</p>
    """
    return _wrap("Havale / EFT ödeme bilgileri", body)


def status_change_html(app_doc: dict, status_label: str, note: str = "") -> str:
    note_html = (
        f'<p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#8A7355;">Danışman notu: {note}</p>'
        if note
        else ""
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {_contact_name(app_doc)},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">{app_doc.get('reference_code','')} kodlu başvurunuzun durumu güncellendi.</p>
    <div style="background-color:#FBF6EC;border:1px solid #EADFCB;border-radius:10px;padding:16px;">
      <div style="font-size:12px;color:#8A7355;margin-bottom:4px;">Yeni Durum</div>
      <div style="font-size:18px;font-weight:bold;color:#3E2A14;">{status_label}</div>
    </div>
    {note_html}
    """
    return _wrap("Başvuru durumu güncellendi", body)


def visa_ready_html(app_doc: dict, download_url: str, message: str = "") -> str:
    message_html = (
        f'<p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#8A7355;">{message}</p>'
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
    <p style="margin:12px 0 0;font-size:12px;line-height:20px;color:#8A7355;">Buton çalışmıyorsa bu adresi tarayıcınıza kopyalayabilirsiniz:<br/>{download_url}</p>
    <p style="margin:16px 0 0;font-size:13px;line-height:21px;">Vizeniz elektroniktir ve pasaportunuza işlenmez. Sınır kapısında bu belgeyi (baskısını veya telefonunuzdaki kopyasını) göstermeniz yeterlidir.</p>
    {message_html}
    <p style="margin:20px 0 0;font-size:13px;line-height:21px;color:#8A7355;">İyi yolculuklar dileriz.</p>
    """
    return _wrap("Vizeniz hazır", body)


def document_reminder_html(app_doc: dict, missing: list, upload_url: str = "") -> str:
    """Eksik belge hatirlatmasi: eksik listesi + yukleme baglantisi."""
    items = []
    for m in missing:
        who = f" — {m['traveler_name']}" if m.get("traveler_name") else ""
        items.append(
            '<li style="margin:0 0 8px;font-size:14px;line-height:22px;color:#3E2A14;">'
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
    <p style="margin:12px 0 0;font-size:12px;line-height:20px;color:#8A7355;">Buton çalışmıyorsa bu adresi tarayıcınıza kopyalayabilirsiniz:<br/>{upload_url}</p>
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
    <p style="margin:18px 0 0;font-size:13px;line-height:21px;color:#8A7355;">
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
        f'<p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#8A7355;">'
        f'Giriş sayfası: <a href="{account_url}" style="color:#B3123A;">{account_url}</a></p>'
        if account_url
        else ""
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      Başvurularınızı görüntülemek ve yarım kalan başvurunuza devam etmek için giriş kodunuz:
    </p>
    <div style="background-color:#F1F5F9;border:1px solid #E2E8F0;border-radius:10px;padding:18px;text-align:center;">
      <div style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#3E2A14;">{code}</div>
      <div style="margin-top:8px;font-size:12px;color:#8A7355;">Kod {ttl_minutes} dakika geçerlidir.</div>
    </div>
    {link}
    <p style="margin:18px 0 0;font-size:12px;line-height:20px;color:#8A7355;">
      Bu kodu siz talep etmediyseniz bu e-postayı dikkate almayabilirsiniz.
    </p>
    """
    return _wrap("Giriş kodunuz", body)


def _visa_label(visa_type_id: str | None) -> str:
    """Vize tipi kimliginden kisa ad (katalog sabit listesinden)."""
    visa = next((v for v in VISA_TYPES if v["id"] == (visa_type_id or "")), None)
    return (visa.get("short_name") or visa.get("name")) if visa else ""


def _draft_name(draft: dict) -> str:
    contact = ((draft.get("data") or {}).get("contact")) or {}
    if contact.get("full_name"):
        return contact["full_name"].strip()
    first = ((draft.get("data") or {}).get("travelers") or [{}])[0]
    return f"{first.get('first_name','')} {first.get('last_name','')}".strip()


def _draft_info_rows(draft: dict) -> str:
    """Basvuran adi, vize tipi, devam kodu ve yolcu sayisi."""
    travelers = ((draft.get("data") or {}).get("travelers")) or []
    labels = [_visa_label(t.get("visa_type_id")) for t in travelers]
    picked = sorted({label for label in labels if label})
    name = _draft_name(draft)
    rows = _row("Başvuran", name) if name else ""
    rows += _row("Vize tipi", " · ".join(picked) if picked else "Seçim aşamasında")
    if len(travelers) > 1:
        names = ", ".join(
            f"{t.get('first_name','')} {t.get('last_name','')}".strip()
            + (" (çocuk)" if t.get("applicant_type") == "child" else "")
            for t in travelers
        )
        rows += _row("Yolcular", names)
    rows += _row("Devam kodu", draft.get("resume_code", ""))
    rows += _row("Yolcu sayısı", draft.get("traveler_count", 1))
    return rows


def draft_saved_html(draft: dict, resume_url: str = "") -> str:
    """Taslak kaydedildi bilgilendirmesi."""
    button = ""
    if resume_url:
        button = f"""
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 4px;">
      <tr><td style="background-color:#B3123A;border-radius:8px;">
        <a href="{resume_url}" style="display:inline-block;padding:14px 26px;color:#ffffff;font-size:15px;font-weight:bold;text-decoration:none;">Başvuruya devam et</a>
      </td></tr>
    </table>
    <p style="margin:12px 0 0;font-size:12px;line-height:20px;color:#8A7355;">Buton çalışmıyorsa: {resume_url}</p>
    """
    name = _draft_name(draft)
    greeting = f"Sayın {name}," if name else "Merhaba,"
    body = f"""
    <p style="margin:0 0 14px;font-size:14px;line-height:22px;">{greeting}</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      Dubai vize başvurunuz kaydedildi. Dilediğiniz zaman kaldığınız yerden devam edebilirsiniz.
    </p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_draft_info_rows(draft)}
    </table>
    {button}
    <p style="margin:18px 0 0;font-size:12px;line-height:20px;color:#8A7355;">
      Kaydedilen bilgiler 60 gün saklanır. Belgeleriniz yalnızca başvurunuz için kullanılır.
    </p>
    """
    return _wrap("Başvurunuz kaydedildi", body)


def draft_reminder_html(draft: dict, resume_url: str = "") -> str:
    """Yarim kalan basvuru hatirlatmasi (sepeti kurtarma)."""
    button = ""
    if resume_url:
        button = f"""
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:18px 0 4px;">
      <tr><td style="background-color:#B3123A;border-radius:8px;">
        <a href="{resume_url}" style="display:inline-block;padding:14px 26px;color:#ffffff;font-size:15px;font-weight:bold;text-decoration:none;">Başvuruma devam et</a>
      </td></tr>
    </table>
    <p style="margin:12px 0 0;font-size:12px;line-height:20px;color:#8A7355;">Buton çalışmıyorsa: {resume_url}</p>
    """
    name = _draft_name(draft)
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">{f'Sayın {name},' if name else 'Merhaba,'}</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      Dubai vize başvurunuz yarım kalmış görünüyor. Bilgileriniz kayıtlı; kaldığınız yerden
      devam edip başvurunuzu birkaç dakikada tamamlayabilirsiniz.
    </p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_draft_info_rows(draft)}
    </table>
    {button}
    <p style="margin:18px 0 0;font-size:13px;line-height:21px;color:#8A7355;">
      Seyahat tarihiniz yaklaştıysa ekspres hizmetimizle başvurunuzu önceliklendirebiliriz.
      Sorularınız için bu e-postayı yanıtlayabilirsiniz.
    </p>
    """
    return _wrap("Başvurunuz yarım kaldı", body)


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
    text = f"{_tr_date(starts)} tarihinde başlar"
    if ends:
        text += f" · {_tr_date(ends)} tarihine kadar geçerli"
    return f'<div style="font-size:12px;color:#8A7355;margin-top:2px;">{text}</div>'


def _order_items_rows(order: dict) -> str:
    currency = order.get("currency", "TRY")
    rows = []
    for item in order.get("items") or []:
        rows.append(
            f'<tr><td style="padding:8px 0;font-size:13px;color:#3E2A14;">{item.get("name","")}'
            f' <span style="color:#8A7355;">x{item.get("quantity",1)}</span>'
            f'{_date_range_note(item)}</td>'
            f'<td style="padding:8px 0;font-size:13px;text-align:right;color:#3E2A14;">'
            f'{money(item.get("total", 0), currency)}</td></tr>'
        )
    return "".join(rows)


def _payment_method_label(order: dict) -> str:
    method = (order.get("payment") or {}).get("method", "")
    return {
        "bank_transfer": "Havale / EFT",
        "card": "Kredi / Banka Kartı",
    }.get(method, method or "-")


def order_received_html(order: dict, bank: dict | None = None) -> str:
    """eSIM / seyahat sigortasi siparis onayi."""
    currency = order.get("currency", "TRY")
    bank_html = ""
    if bank:
        bank_html = f"""
    <div style="margin-top:18px;background-color:#F1F5F9;border:1px solid #E2E8F0;border-radius:10px;padding:16px;">
      <div style="font-size:12px;font-weight:bold;color:#3E2A14;margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px;">Havale / EFT Bilgileri</div>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        {_row('Banka', bank.get('bank_name',''))}
        {_row('Hesap sahibi', bank.get('account_name',''))}
        {_row('IBAN', bank.get('iban',''))}
        {_row('Açıklama', order.get('reference_code',''))}
      </table>
      <p style="margin:12px 0 0;font-size:12px;line-height:20px;color:#8A7355;">
        Açıklama alanına sipariş kodunuzu yazmayı unutmayın. Ödemeniz onaylandığında teslimat yapılır.
      </p>
    </div>
    """
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {order.get('contact',{}).get('full_name','')},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      Siparişiniz alındı. Ödemeniz onaylandıktan sonra eSIM QR kodunuz ve/veya sigorta poliçeniz
      e-posta ile size iletilecek.
    </p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Sipariş kodu', order.get('reference_code',''))}
      {_row('Ödeme yöntemi', _payment_method_label(order))}
    </table>
    <div style="margin-top:16px;border-top:1px solid #E2E8F0;padding-top:8px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        {_order_items_rows(order)}
        {_row('Seyahat paketi indirimi (%10)', '- ' + money(order.get('bundle_discount', 0), currency)) if order.get('bundle_discount') else ''}
        <tr><td style="padding:10px 0 0;font-size:14px;font-weight:bold;border-top:1px solid #E2E8F0;">Toplam</td>
        <td style="padding:10px 0 0;font-size:14px;font-weight:bold;text-align:right;border-top:1px solid #E2E8F0;">{money(order.get('price', 0), currency)}</td></tr>
      </table>
    </div>
    {bank_html}
    """
    return _wrap("Siparişiniz alındı", body)


def order_admin_html(order: dict) -> str:
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Yeni eSIM / sigorta siparişi oluşturuldu.</p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      {_row('Sipariş kodu', order.get('reference_code',''))}
      {_row('Müşteri', order.get('contact',{}).get('full_name',''))}
      {_row('E-posta', order.get('contact',{}).get('email',''))}
      {_row('Telefon', order.get('contact',{}).get('phone',''))}
      {_row('Tutar', money(order.get('price', 0), order.get('currency', 'TRY')))}
      {_row('Ödeme', _payment_method_label(order))}
    </table>
    <div style="margin-top:12px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{_order_items_rows(order)}</table>
    </div>
    """
    return _wrap("Yeni sipariş", body)


def order_delivered_html(order: dict, links: list, message: str = "") -> str:
    """eSIM QR / police teslimati."""
    link_html = "".join(
        f'<tr><td style="padding:8px 0;"><a href="{l["url"]}" style="color:#B3123A;font-size:14px;font-weight:bold;">{l["label"]}</a></td></tr>'
        for l in links
    )
    note = (
        f'<p style="margin:16px 0 0;font-size:13px;line-height:21px;color:#3E2A14;">{message}</p>'
        if message
        else ""
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">Sayın {order.get('contact',{}).get('full_name','')},</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">
      {order.get('reference_code','')} kodlu siparişiniz hazır. Belgelerinizi aşağıdaki bağlantılardan
      indirebilirsiniz.
    </p>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">{link_html}</table>
    {note}
    <p style="margin:18px 0 0;font-size:12px;line-height:20px;color:#8A7355;">
      eSIM kurulumu: Ayarlar &gt; Mobil Veri &gt; eSIM ekle &gt; QR kodu tarat. Kurulum sırasında
      internet bağlantısı gereklidir.
    </p>
    """
    return _wrap("Siparişiniz hazır", body)


def _snapshot_items_rows(snapshot: dict) -> str:
    currency = snapshot.get("currency", "TRY")
    rows = []
    for item in snapshot.get("items") or []:
        rows.append(
            f'<tr><td style="padding:8px 0;font-size:13px;color:#3E2A14;">{item.get("name","")}'
            f' <span style="color:#8A7355;">x{item.get("quantity",1)}</span></td>'
            f'<td style="padding:8px 0;font-size:13px;text-align:right;color:#3E2A14;">'
            f'{money(item.get("total", 0), currency)}</td></tr>'
        )
    return "".join(rows)


def cart_reminder_html(snapshot: dict, cart_url: str, stage: int = 1) -> str:
    """Terk edilmis sepet hatirlatmasi (2. ve 24. saat)."""
    currency = snapshot.get("currency", "TRY")
    name = (snapshot.get("full_name") or "").strip()
    greeting = f"Sayın {name}," if name else "Merhaba,"
    intro = (
        "Sepetinizdeki Dubai hizmetleri hâlâ sizi bekliyor. Ödemenizi tamamladığınızda eSIM QR kodunuz, "
        "poliçeniz ve tur kuponunuz e-postanıza gelir."
        if stage == 1
        else "Sepetinizi kaydettik ve hâlâ hazır. Fiyatlar güncel kurla hesaplanır; kur değişmeden "
        "tamamlamak isterseniz aşağıdan devam edebilirsiniz."
    )
    discount_row = (
        _row("Seyahat paketi indirimi (%10)", "- " + money(snapshot.get("bundle_discount", 0), currency))
        if snapshot.get("bundle_discount")
        else ""
    )
    body = f"""
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">{greeting}</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:22px;">{intro}</p>
    <div style="margin-top:8px;border-top:1px solid #E2E8F0;padding-top:8px;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
        {_snapshot_items_rows(snapshot)}
        {discount_row}
        <tr><td style="padding:10px 0 0;font-size:14px;font-weight:bold;border-top:1px solid #E2E8F0;">Toplam</td>
        <td style="padding:10px 0 0;font-size:14px;font-weight:bold;text-align:right;border-top:1px solid #E2E8F0;">{money(snapshot.get('price', 0), currency)}</td></tr>
      </table>
    </div>
    <p style="margin:22px 0 0;">
      <a href="{cart_url}" style="display:inline-block;background-color:#B06A29;color:#ffffff;text-decoration:none;
      font-size:14px;font-weight:bold;padding:13px 26px;border-radius:999px;">Sepetime dön</a>
    </p>
    <p style="margin:18px 0 0;font-size:12px;line-height:20px;color:#8A7355;">
      Sigorta ve eSIM'i birlikte aldığınızda %10 paket indirimi otomatik uygulanır. Bu e-postayı
      yanıtlayarak bize soru da sorabilirsiniz.
    </p>
    """
    return _wrap("Sepetiniz sizi bekliyor", body)
