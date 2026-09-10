"""Odeme ozeti PDF'i (basvuru + magaza siparisi) — basvuru formuyla ayni tasarim.

Musteri odemesi alindiginda e-postaya eklenir; takip/siparis sayfasindan da indirilebilir.
Resmi e-Arsiv fatura ayri gonderilir; bu belge bilgilendirme amacli ozettir.
"""

import io
from datetime import datetime, timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from application_pdf import (
    AMOUNT_PAD,
    LINE,
    PANEL,
    _amount_table,
    _cols,
    _draw_frame,
    _header,
    _pairs_table,
    _safe,
    _styles,
)
from content import COMPANY
from emailer import BRAND
from pdf_pricing import (
    currency_of,
    discount_rows,
    fmt_date,
    gross_subtotal,
    money,
    paid_items,
    store_rows,
)

RECEIPT_NOTE = (
    "Bu belge bilgilendirme amaçlı ödeme özetidir; resmî e-Arşiv faturanız kayıtlı "
    "e-posta adresinize ayrıca gönderilir."
)

PAYMENT_METHODS = {
    "card": "Kredi / Banka Kartı",
    "bank_transfer": "Havale / EFT",
}

PAYMENT_STATUS = {
    "paid": "Ödendi",
    "awaiting_transfer": "Havale bekleniyor",
    "pending": "Bekliyor",
    "refunded": "İade edildi",
}


def _payment(doc: dict) -> dict:
    return doc.get("payment") or {}


def _contact_name(doc: dict) -> str:
    contact = doc.get("contact") or {}
    full = (contact.get("full_name") or "").strip()
    if full:
        return full
    return f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()


def _paid_date(doc: dict) -> str:
    raw = _payment(doc).get("paid_at") or doc.get("updated_at") or doc.get("created_at")
    if isinstance(raw, datetime):
        return raw.astimezone(timezone.utc).strftime("%d.%m.%Y")
    return fmt_date(str(raw or "")[:10])


def _info_band(doc: dict, st: dict, code_label: str) -> Table:
    payment = _payment(doc)
    cells = [
        (code_label, _safe(doc.get("reference_code"))),
        ("ÖDEME TARİHİ", _paid_date(doc)),
        ("ÖDEME DURUMU", PAYMENT_STATUS.get(payment.get("status"), "Bekliyor")),
        ("ÖDEME YÖNTEMİ", PAYMENT_METHODS.get(payment.get("method"), "-")),
    ]
    row = [
        [Paragraph(label, st["label"]), Paragraph(value, st["value"])]
        for label, value in cells
    ]
    table = Table([row], colWidths=_cols(52, 38, 38, 52))
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _customer_pairs(doc: dict, order: bool) -> list:
    contact = doc.get("contact") or {}
    return [
        ("Adı Soyadı", _contact_name(doc)),
        ("E-posta", contact.get("email")),
        ("Telefon", contact.get("phone")),
        ("Sipariş tarihi" if order else "Başvuru tarihi", fmt_date(str(doc.get("created_at") or "")[:10])),
    ]


def _seller_pairs() -> list:
    pairs = [
        ("Satıcı", COMPANY["legal_name"]),
        ("Acente türü", COMPANY["tursab_type"]),
        ("TÜRSAB No", COMPANY.get("tursab_no")),
        ("Vergi Dairesi", COMPANY.get("tax_office")),
        ("Vergi No", COMPANY.get("tax_no")),
        ("Adres", COMPANY["address"]),
    ]
    return [(label, value) for label, value in pairs if str(value or "").strip()]


def _application_items(doc: dict) -> list:
    """(aciklama, adet, tutar) — vize bedelleri + ek hizmetler + magaza kalemleri."""
    return paid_items(doc)


def _order_items(doc: dict) -> list:
    return store_rows(doc.get("items"), currency_of(doc))


def _application_summary_rows(doc: dict) -> list:
    """Kalem tablosunu tekrarlamayan sade dokum: ara toplam, indirimler, toplam."""
    currency = currency_of(doc)
    pricing = doc.get("pricing") or {}
    gross = gross_subtotal(pricing)
    rows = [("Ara toplam", money(gross, currency))]
    rows += discount_rows(pricing, currency)
    total = pricing.get("total", doc.get("price", gross)) or gross
    rows.append(("TOPLAM", money(total, currency)))
    return rows


def _order_summary_rows(doc: dict) -> list:
    currency = currency_of(doc)
    subtotal = sum(float(item.get("total", 0) or 0) for item in doc.get("items") or [])
    rows = [("Ara toplam", money(subtotal, currency))]
    if doc.get("bundle_discount"):
        rows.append(("Seyahat paketi indirimi", "- " + money(doc["bundle_discount"], currency)))
    rows.append(("TOPLAM", money(doc.get("price", subtotal), currency)))
    return rows


def _items_table(rows: list, st: dict) -> Table:
    head = ["#", "Açıklama", "Adet", "Tutar"]
    body = [[Paragraph(f"<b>{h}</b>", st["label"]) for h in head]]
    for index, (label, qty, amount) in enumerate(rows, start=1):
        body.append(
            [
                Paragraph(str(index), st["body"]),
                Paragraph(_safe(label), st["value"]),
                Paragraph(_safe(qty), st["body"]),
                Paragraph(amount, st["value_right"]),
            ]
        )
    table = Table(body, colWidths=_cols(6, 128, 20, 26), repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (-1, 0), (-1, -1), AMOUNT_PAD),
            ]
        )
    )
    return table


def receipt_filename(doc: dict) -> str:
    return f"Odeme-Ozeti-{doc.get('reference_code', 'DV')}.pdf"


def build_receipt_pdf(doc: dict, kind: str = "application") -> bytes:
    """Odeme ozetini tek sayfalik PDF olarak dondurur (kind: application | order)."""
    st = _styles()
    order = kind == "order"
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=27 * mm,
        title=f"Ödeme Özeti {doc.get('reference_code', '')}",
        author=BRAND,
    )
    pdf.footer_note = RECEIPT_NOTE

    items = _order_items(doc) if order else _application_items(doc)
    summary = _order_summary_rows(doc) if order else _application_summary_rows(doc)

    story = [
        _header(doc, st, "Ödeme Özeti<br/>Dubai Vize Hattı"),
        Spacer(1, 7),
        _info_band(doc, st, "SİPARİŞ KODU" if order else "TAKİP KODU"),
        Spacer(1, 9),
        Paragraph("MÜŞTERİ BİLGİLERİ", st["section"]),
        _pairs_table(_customer_pairs(doc, order), st),
        Spacer(1, 8),
        Paragraph("ÖDEME KALEMLERİ", st["section"]),
        _items_table(items, st),
        Spacer(1, 8),
        Paragraph("ÖDEME DÖKÜMÜ", st["section"]),
        _amount_table(summary, st),
        Spacer(1, 8),
        Paragraph("SATICI BİLGİLERİ", st["section"]),
        _pairs_table(_seller_pairs(), st),
        Spacer(1, 8),
        Paragraph(RECEIPT_NOTE, st["label"]),
    ]
    pdf.build(story, onFirstPage=_draw_frame, onLaterPages=_draw_frame)
    return buffer.getvalue()


def receipt_attachment(doc: dict, kind: str = "application") -> list:
    """send_email(attachments=...) icin hazir ek listesi; hata halinde bos doner."""
    return [
        {
            "filename": receipt_filename(doc),
            "content": build_receipt_pdf(doc, kind),
            "content_type": "application/pdf",
        }
    ]
