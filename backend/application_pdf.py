"""Vize basvurusunun tek sayfalik PDF formu (e-posta eki + panelden indirme)."""

import io
import logging
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from content import COMPANY
from emailer import BRAND, money as _money_html


def money(amount: float, currency: str = "TRY") -> str:
    """PDF yazi tipinde ₺ glifi yok; TL yazimina cevirir."""
    return _money_html(amount, currency).replace("₺", "TL")

logger = logging.getLogger(__name__)

INK = colors.HexColor("#3E2A14")
GOLD = colors.HexColor("#B06A29")
MUTED = colors.HexColor("#8A7355")
LINE = colors.HexColor("#EADFCB")
PANEL = colors.HexColor("#FBF6EC")

LOGO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "email-logo.png")
FONT_CANDIDATES = (
    (
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ),
)
_FONTS: tuple[str, str] | None = None

MARITAL_LABELS = {
    "single": "Bekar",
    "married": "Evli",
    "divorced": "Boşanmış",
    "widowed": "Eşi vefat etmiş",
}
TRAVEL_WINDOWS = {
    "this_month": "Bu ay içinde",
    "1_3_months": "1-3 ay içinde",
    "3_plus_months": "3 aydan sonra",
    "undecided": "Henüz karar verilmedi",
}


def _fonts() -> tuple[str, str]:
    """Turkce karakter destekli TTF kaydeder (Helvetica ı/ğ/ş basmiyor)."""
    global _FONTS
    if _FONTS:
        return _FONTS
    for regular, bold in FONT_CANDIDATES:
        if os.path.exists(regular) and os.path.exists(bold):
            pdfmetrics.registerFont(TTFont("DVH", regular))
            pdfmetrics.registerFont(TTFont("DVH-Bold", bold))
            _FONTS = ("DVH", "DVH-Bold")
            return _FONTS
    logger.warning("Turkce destekli TTF bulunamadi; Helvetica kullaniliyor.")
    _FONTS = ("Helvetica", "Helvetica-Bold")
    return _FONTS


def _date(value) -> str:
    raw = str(value or "")[:10]
    try:
        return datetime.strptime(raw, "%Y-%m-%d").strftime("%d.%m.%Y")
    except ValueError:
        return raw


def _styles() -> dict:
    reg, bold = _fonts()
    return {
        "title": ParagraphStyle("t", fontName=bold, fontSize=15, leading=19, textColor=INK),
        "sub": ParagraphStyle("s", fontName=reg, fontSize=8, leading=11, textColor=MUTED),
        "section": ParagraphStyle(
            "sec", fontName=bold, fontSize=8, leading=11, textColor=GOLD, spaceAfter=3
        ),
        "label": ParagraphStyle("l", fontName=reg, fontSize=7, leading=9, textColor=MUTED),
        "value": ParagraphStyle("v", fontName=bold, fontSize=8.5, leading=11, textColor=INK),
        "body": ParagraphStyle("b", fontName=reg, fontSize=8, leading=11, textColor=INK),
        "foot": ParagraphStyle("f", fontName=reg, fontSize=6.5, leading=9, textColor=MUTED),
        "code": ParagraphStyle("c", fontName=bold, fontSize=16, leading=19, textColor=INK),
    }


def _header(app_doc: dict, st: dict) -> Table:
    created = str(app_doc.get("created_at") or "")[:10]
    right = [
        Paragraph("VİZE BAŞVURU FORMU", st["title"]),
        Paragraph(
            f"Başvuru tarihi: {_date(created)} · Dubai / Birleşik Arap Emirlikleri", st["sub"]
        ),
    ]
    cells = []
    if os.path.exists(LOGO_FILE):
        cells.append(Image(LOGO_FILE, width=52 * mm, height=52 * mm * 0.23, kind="proportional"))
    else:
        cells.append(Paragraph(BRAND, st["title"]))
    cells.append(right)
    table = Table([cells], colWidths=[56 * mm, 124 * mm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("LINEBELOW", (0, 0), (-1, -1), 1.4, GOLD),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _reference_band(app_doc: dict, st: dict) -> Table:
    payment = (app_doc.get("payment") or {}).get("status")
    rows = [
        [
            [Paragraph("TAKİP KODU", st["label"]), Paragraph(app_doc.get("reference_code", "-"), st["code"])],
            [
                Paragraph("ÖDEME DURUMU", st["label"]),
                Paragraph("Ödendi" if payment == "paid" else "Bekliyor", st["value"]),
            ],
            [
                Paragraph("TAHMİNİ SONUÇLANMA", st["label"]),
                Paragraph(app_doc.get("processing_days") or "-", st["value"]),
            ],
        ]
    ]
    table = Table(rows, colWidths=[66 * mm, 52 * mm, 62 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def _pairs_table(pairs: list, st: dict) -> Table:
    """Etiket/deger ciftlerini iki kolonlu kompakt izgaraya dizer."""
    rows = []
    for i in range(0, len(pairs), 2):
        chunk = pairs[i : i + 2]
        row = []
        for label, value in chunk:
            row += [Paragraph(label, st["label"]), Paragraph(str(value or "-"), st["value"])]
        if len(chunk) == 1:
            row += ["", ""]
        rows.append(row)
    table = Table(rows, colWidths=[26 * mm, 64 * mm, 26 * mm, 64 * mm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
            ]
        )
    )
    return table


def _contact_pairs(app_doc: dict) -> list:
    contact = app_doc.get("contact") or {}
    return [
        ("Ad Soyad", contact.get("full_name")),
        ("E-posta", contact.get("email")),
        ("Telefon (WhatsApp)", contact.get("phone")),
        ("Şehir", contact.get("address_city")),
    ]


def _travel_pairs(app_doc: dict) -> list:
    travel = app_doc.get("travel") or {}
    if travel.get("dates_unknown"):
        window = TRAVEL_WINDOWS.get(travel.get("travel_window") or "", "")
        dates = [("Seyahat tarihi", "Henüz belli değil" + (f" · {window}" if window else ""))]
    else:
        dates = [
            ("Gidiş tarihi", _date(travel.get("arrival_date"))),
            ("Dönüş tarihi", _date(travel.get("departure_date"))),
        ]
    return dates + [
        ("Yolcu sayısı", str(len(app_doc.get("travelers") or []))),
        ("Konaklama", travel.get("accommodation")),
        ("Uçuş bilgisi", travel.get("flight_no")),
        ("Notlar", travel.get("notes")),
    ]


def _travelers_table(app_doc: dict, st: dict) -> Table:
    head = ["#", "Ad Soyad", "Doğum t.", "Pasaport no", "Geçerlilik", "Vize", "Tutar"]
    rows = [[Paragraph(f"<b>{h}</b>", st["label"]) for h in head]]
    for i, t in enumerate(app_doc.get("travelers") or [], start=1):
        name = f"{t.get('first_name', '')} {t.get('last_name', '')}".strip()
        if t.get("applicant_type") == "child":
            name += " (çocuk)"
        rows.append(
            [
                Paragraph(str(i), st["body"]),
                Paragraph(name, st["value"]),
                Paragraph(_date(t.get("birth_date")), st["body"]),
                Paragraph(t.get("passport_no") or "-", st["body"]),
                Paragraph(_date(t.get("passport_expiry")), st["body"]),
                Paragraph(t.get("visa_short_name") or t.get("visa_type_name") or "-", st["body"]),
                Paragraph(money(t.get("price", 0), t.get("currency", "TRY")), st["value"]),
            ]
        )
    table = Table(
        rows,
        colWidths=[6 * mm, 44 * mm, 20 * mm, 26 * mm, 20 * mm, 38 * mm, 26 * mm],
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.5, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _traveler_extra_pairs(app_doc: dict) -> list:
    """Zami/portal icin tasinan ek yolcu alanlari (tek yolcuda gosterilir)."""
    travelers = app_doc.get("travelers") or []
    if len(travelers) != 1:
        return []
    t = travelers[0]
    return [
        ("Uyruk", t.get("nationality")),
        ("Doğum yeri", t.get("birth_place")),
        ("Medeni hal", MARITAL_LABELS.get(t.get("marital_status") or "", t.get("marital_status"))),
        ("Meslek", t.get("profession")),
    ]


def _pricing_rows(app_doc: dict) -> list:
    p = app_doc.get("pricing") or {}
    currency = p.get("currency") or app_doc.get("currency") or "TRY"
    rows = []
    if p:
        rows.append(("Vize bedelleri", money(p.get("subtotal", 0), currency)))
        if p.get("family_discount"):
            pct = int(round((p.get("family_discount_rate") or 0) * 100))
            rows.append((f"Aile indirimi (%{pct})", "- " + money(p["family_discount"], currency)))
        for addon in p.get("addons") or []:
            rows.append(
                (f"{addon['name']} x{addon['quantity']}", money(addon["total"], currency))
            )
        for item in p.get("store_items") or []:
            label = f"{item['name']} x{item['quantity']}"
            if item.get("scheduled_date"):
                slot = f" {item['scheduled_time']}" if item.get("scheduled_time") else ""
                label += f" ({_date(item['scheduled_date'])}{slot})"
            rows.append((label, money(item["total"], currency)))
        if p.get("bundle_discount"):
            pct = int(round((p.get("bundle_discount_rate") or 0) * 100))
            title = p.get("bundle_discount_title") or "Paket indirimi"
            rows.append((f"{title} (%{pct})", "- " + money(p["bundle_discount"], currency)))
    rows.append(
        ("TOPLAM", money(p.get("total", app_doc.get("price", 0)) or 0, currency))
    )
    return rows


def _price_table(app_doc: dict, st: dict) -> Table:
    rows = [
        [Paragraph(label, st["body"]), Paragraph(value, st["value"])]
        for label, value in _pricing_rows(app_doc)
    ]
    table = Table(rows, colWidths=[140 * mm, 40 * mm])
    table.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
                ("LINEABOVE", (0, -1), (-1, -1), 0.8, GOLD),
                ("TOPPADDING", (0, -1), (-1, -1), 5),
            ]
        )
    )
    return table


def _documents_paragraph(documents: list, st: dict) -> Paragraph:
    if not documents:
        return Paragraph("Bu başvuruda yüklenmiş belge kaydı bulunmuyor.", st["body"])
    lines = []
    for item in documents:
        note = "" if item.get("attached", True) else " (e-postada bağlantı olarak)"
        lines.append(f"• {item.get('label', '')}{note}")
    return Paragraph("<br/>".join(lines), st["body"])


def _footer_paragraph(st: dict) -> Paragraph:
    text = (
        f"{COMPANY['legal_name']} · TÜRSAB Üyesi {COMPANY['tursab_type']} · "
        f"{COMPANY['phone']} · {COMPANY['email']} · www.dubaivizehatti.com<br/>"
        f"{COMPANY['address']}<br/>"
        "Bu form başvuru kaydınızın sistem tarafından üretilmiş özetidir; "
        "resmî vize belgesi değildir."
    )
    return Paragraph(text, st["foot"])


def build_application_pdf(app_doc: dict, documents: list | None = None) -> bytes:
    """Basvuru ozetini tek sayfalik PDF olarak dondurur."""
    st = _styles()
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=13 * mm,
        bottomMargin=12 * mm,
        title=f"Başvuru Formu {app_doc.get('reference_code', '')}",
        author=BRAND,
    )
    extra_pairs = _traveler_extra_pairs(app_doc)
    story = [
        _header(app_doc, st),
        Spacer(1, 7),
        _reference_band(app_doc, st),
        Spacer(1, 9),
        Paragraph("BAŞVURU SAHİBİ / İLETİŞİM", st["section"]),
        _pairs_table(_contact_pairs(app_doc), st),
        Spacer(1, 8),
        Paragraph("SEYAHAT BİLGİLERİ", st["section"]),
        _pairs_table(_travel_pairs(app_doc), st),
        Spacer(1, 8),
        Paragraph("YOLCULAR VE VİZE SEÇİMİ", st["section"]),
        _travelers_table(app_doc, st),
    ]
    if extra_pairs:
        story += [Spacer(1, 6), _pairs_table(extra_pairs, st)]
    story += [
        Spacer(1, 8),
        Paragraph("HİZMET BEDELİ DÖKÜMÜ", st["section"]),
        _price_table(app_doc, st),
        Spacer(1, 8),
        Paragraph("YÜKLENEN BELGELER", st["section"]),
        _documents_paragraph(documents or [], st),
        Spacer(1, 10),
        _footer_paragraph(st),
    ]
    pdf.build(story)
    return buffer.getvalue()
