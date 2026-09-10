"""Vize basvurusunun tek sayfalik PDF formu (e-posta eki + panelden indirme)."""

import io
import logging
import os
from datetime import datetime
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from content import brand_footer_lines
from emailer import BRAND
from emailer import money as _money_html
from phone_format import format_phone


def money(amount: float, currency: str = "TRY") -> str:
    """PDF yazi tipinde ₺ glifi yok; TL yazimina cevirir."""
    return _money_html(amount, currency).replace("₺", "TL")

logger = logging.getLogger(__name__)

INK = colors.HexColor("#3E2A14")
GOLD = colors.HexColor("#B06A29")
MUTED = colors.HexColor("#8A7355")
LINE = colors.HexColor("#EADFCB")
PANEL = colors.HexColor("#FBF6EC")
TITLE_LEADING = 19  # baslik satir yuksekligi (logo bu bloga gore olceklenir)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
# Saydam zeminli logo (email-logo.png krem zemine gomulu oldugu icin formda kullanilmaz)
LOGO_FILE = os.path.join(ASSETS_DIR, "pdf-logo.png")
if not os.path.exists(LOGO_FILE):
    LOGO_FILE = os.path.join(ASSETS_DIR, "email-logo.png")
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
NATIONALITY_LABELS = {
    "TR": "Türkiye",
    "TUR": "Türkiye",
    "TURKEY": "Türkiye",
    "TÜRKIYE": "Türkiye",
    "TURKIYE": "Türkiye",
    "TÜRKİYE": "Türkiye",
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


def _safe(value) -> str:
    """Kullanici metnini ReportLab markup'ina karsi kacisir (etiket enjeksiyonu/dis kaynak yok)."""
    text = str(value).strip() if value not in (None, "") else "-"
    return xml_escape(text)


def _nationality(value) -> str:
    """Pasaport/uyruk kodunu okunur ulke adina cevirir (TR -> Türkiye)."""
    raw = str(value or "").strip()
    return NATIONALITY_LABELS.get(raw.upper(), raw)


def _date(value) -> str:
    raw = str(value or "")[:10]
    try:
        return datetime.strptime(raw, "%Y-%m-%d").strftime("%d.%m.%Y")
    except ValueError:
        return raw


def _styles() -> dict:
    reg, bold = _fonts()
    return {
        "title": ParagraphStyle("t", fontName=bold, fontSize=15, leading=TITLE_LEADING, textColor=INK),
        "title_head": ParagraphStyle(
            "th",
            fontName=bold,
            fontSize=15,
            leading=TITLE_LEADING,
            textColor=INK,
            alignment=TA_CENTER,
        ),
        "sub": ParagraphStyle("s", fontName=reg, fontSize=8, leading=11, textColor=MUTED),
        "section": ParagraphStyle(
            "sec", fontName=bold, fontSize=8, leading=11, textColor=GOLD, spaceAfter=3
        ),
        "label": ParagraphStyle("l", fontName=reg, fontSize=7, leading=9, textColor=MUTED),
        "value": ParagraphStyle("v", fontName=bold, fontSize=8.5, leading=11, textColor=INK),
        "value_right": ParagraphStyle(
            "vr", fontName=bold, fontSize=8.5, leading=11, textColor=INK, alignment=TA_RIGHT
        ),
        "label_right": ParagraphStyle(
            "lr", fontName=reg, fontSize=7, leading=9, textColor=MUTED, alignment=TA_RIGHT
        ),
        "value_center": ParagraphStyle(
            "vc", fontName=bold, fontSize=8.5, leading=11, textColor=INK, alignment=TA_CENTER
        ),
        "body": ParagraphStyle("b", fontName=reg, fontSize=8, leading=11, textColor=INK),
        "body_center": ParagraphStyle(
            "bc", fontName=reg, fontSize=8, leading=12, textColor=INK, alignment=TA_CENTER
        ),
        "section_center": ParagraphStyle(
            "secc",
            fontName=bold,
            fontSize=8,
            leading=11,
            textColor=GOLD,
            spaceAfter=3,
            alignment=TA_CENTER,
        ),
        "foot": ParagraphStyle(
            "f", fontName=reg, fontSize=6.5, leading=9, textColor=MUTED, alignment=TA_CENTER
        ),
        "code": ParagraphStyle("c", fontName=bold, fontSize=16, leading=19, textColor=INK),
    }


def _header(app_doc: dict, st: dict, title_text: str = "Dubai Vizesi<br/>Başvuru Detayları") -> Table:
    """Solda logo (baslik blogu kadar yuksek), ortada iki satirlik baslik."""
    title = Paragraph(title_text, st["title_head"])
    if os.path.exists(LOGO_FILE):
        # Logo, sagdaki iki satirlik basligin ust-alt hizasini tam kaplasin
        height = 2 * TITLE_LEADING
        img_w, img_h = ImageReader(LOGO_FILE).getSize()
        logo = Image(LOGO_FILE, width=height * img_w / img_h, height=height)
    else:
        logo = Paragraph(BRAND, st["title"])
    table = Table([[logo, title, ""]], colWidths=_cols(56, 68, 56))
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
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
            [Paragraph("TAKİP KODU", st["label"]), Paragraph(_safe(app_doc.get("reference_code")), st["code"])],
            [
                Paragraph("BAŞVURU TARİHİ", st["label"]),
                Paragraph(_date(str(app_doc.get("created_at") or "")[:10]), st["value"]),
            ],
            [
                Paragraph("ÖDEME DURUMU", st["label"]),
                Paragraph("Ödendi" if payment == "paid" else "Bekliyor", st["value"]),
            ],
            [
                Paragraph("TAHMİNİ SONUÇLANMA", st["label"]),
                Paragraph(_safe(app_doc.get("processing_days")), st["value"]),
            ],
        ]
    ]
    table = Table(rows, colWidths=_cols(56, 38, 38, 48))
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
            row += [Paragraph(label, st["label"]), Paragraph(_safe(value), st["value"])]
        if len(chunk) == 1:
            row += ["", ""]
        rows.append(row)
    table = Table(rows, colWidths=_cols(26, 64, 26, 64))
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
        ("Adı Soyadı", contact.get("full_name")),
        ("E-posta", contact.get("email")),
        ("Telefon (WhatsApp)", format_phone(contact.get("phone"))),
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
    optional = [
        ("Konaklama", travel.get("accommodation")),
        ("Uçuş bilgisi", travel.get("flight_no")),
        ("Notlar", travel.get("notes")),
    ]
    return (
        dates
        + [("Yolcu sayısı", str(len(app_doc.get("travelers") or [])))]
        # bos alanlar formda hic gosterilmez (musteri bilgi vermediyse satir cikmaz)
        + [(label, value) for label, value in optional if str(value or "").strip()]
    )


def _travelers_table(app_doc: dict, st: dict) -> Table:
    head = [
        "#",
        "Adı Soyadı",
        "Doğum Tarihi",
        "Pasaport No",
        "Geçerlilik Tarihi",
        "Vize Türü",
        "Tutar",
    ]
    rows = [
        [
            Paragraph(f"<b>{h}</b>", st["label_right"] if h == "Tutar" else st["label"])
            for h in head
        ]
    ]
    for i, t in enumerate(app_doc.get("travelers") or [], start=1):
        name = f"{t.get('first_name', '')} {t.get('last_name', '')}".strip()
        if t.get("applicant_type") == "child":
            name += " (çocuk)"
        rows.append(
            [
                Paragraph(str(i), st["body"]),
                Paragraph(_safe(name), st["value"]),
                Paragraph(_date(t.get("birth_date")), st["body"]),
                Paragraph(_safe(t.get("passport_no")), st["body"]),
                Paragraph(_date(t.get("passport_expiry")), st["body"]),
                Paragraph(_safe(t.get("visa_short_name") or t.get("visa_type_name")), st["body"]),
                Paragraph(money(t.get("price", 0), t.get("currency", "TRY")), st["value_right"]),
            ]
        )
    table = Table(
        rows,
        colWidths=_cols(6, 40, 22, 26, 24, 36, 26),
        repeatRows=1,
    )
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
        ("Uyruğu", _nationality(t.get("nationality"))),
        ("Doğum yeri", t.get("birth_place")),
    ]


def _discount_row(label: str, amount: float, rate: float | None, currency: str) -> tuple:
    pct = int(round((rate or 0) * 100))
    return (f"{label} (%{pct})", "- " + money(amount, currency))


def _extras_rows(pricing: dict, currency: str) -> list:
    """Ek hizmet ve magaza kalemlerini satirlara cevirir."""
    rows = [
        (f"{addon['name']} x{addon['quantity']}", money(addon["total"], currency))
        for addon in pricing.get("addons") or []
    ]
    for item in pricing.get("store_items") or []:
        label = f"{item['name']} x{item['quantity']}"
        if item.get("scheduled_date"):
            slot = f" {item['scheduled_time']}" if item.get("scheduled_time") else ""
            label += f" ({_date(item['scheduled_date'])}{slot})"
        rows.append((label, money(item["total"], currency)))
    return rows


def _pricing_rows(app_doc: dict) -> list:
    pricing = app_doc.get("pricing") or {}
    currency = pricing.get("currency") or app_doc.get("currency") or "TRY"
    rows = []
    if pricing:
        rows.append(("Vize bedelleri", money(pricing.get("subtotal", 0), currency)))
        if pricing.get("family_discount"):
            rows.append(
                _discount_row(
                    "Aile indirimi",
                    pricing["family_discount"],
                    pricing.get("family_discount_rate"),
                    currency,
                )
            )
        rows += _extras_rows(pricing, currency)
        if pricing.get("visa_insurance_discount"):
            rows.append(
                _discount_row(
                    pricing.get("visa_insurance_discount_title") or "Sigorta dahil vize indirimi",
                    pricing["visa_insurance_discount"],
                    pricing.get("visa_insurance_discount_rate"),
                    currency,
                )
            )
        if pricing.get("bundle_discount"):
            rows.append(
                _discount_row(
                    pricing.get("bundle_discount_title") or "Paket indirimi",
                    pricing["bundle_discount"],
                    pricing.get("bundle_discount_rate"),
                    currency,
                )
            )
    rows.append(("TOPLAM", money(pricing.get("total", app_doc.get("price", 0)) or 0, currency)))
    return rows


def _amount_table(rows: list, st: dict) -> Table:
    """Etiket + tutar satirlari; tutar kolonu yolcu tablosundaki "Tutar" ile ayni yerde."""
    body = [
        [Paragraph(_safe(label), st["body"]), Paragraph(value, st["value_right"])]
        for label, value in rows
    ]
    table = Table(body, colWidths=_cols(154, 26))
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -2), 0.4, LINE),
                ("LINEABOVE", (0, -1), (-1, -1), 0.8, GOLD),
                ("TOPPADDING", (0, -1), (-1, -1), 5),
            ]
        )
    )
    return table


def _price_table(app_doc: dict, st: dict) -> Table:
    return _amount_table(_pricing_rows(app_doc), st)


def _documents_paragraph(documents: list, st: dict) -> Paragraph:
    if not documents:
        return Paragraph("Bu başvuruda yüklenmiş belge kaydı bulunmuyor.", st["body"])
    lines = []
    for item in documents:
        note = "" if item.get("attached", True) else " (e-postada bağlantı olarak)"
        lines.append(f"• {_safe(item.get('label'))}{note}")
    return Paragraph("<br/>".join(lines), st["body"])


FRAME_INSET = 8 * mm

# Tasarim 180 mm genisliginde kurulu; cerceve ici kullanilabilir alana oranlanir
# (SimpleDocTemplate frame'i 6 pt sag/sol padding uygular).
DESIGN_W = 180 * mm
CONTENT_W = A4[0] - 2 * (15 * mm) - 12


def _cols(*widths_mm: float) -> list:
    """Kolon genisliklerini kullanilabilir alana oranlar (sol kenarlar hizali kalir)."""
    scale = CONTENT_W / DESIGN_W
    return [w * mm * scale for w in widths_mm]


def _draw_frame(canvas, doc) -> None:
    """Sayfayi ince altin cerceve icine alir (form gorunumu)."""
    width, height = A4
    canvas.saveState()
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1.1)
    canvas.roundRect(
        FRAME_INSET, FRAME_INSET, width - 2 * FRAME_INSET, height - 2 * FRAME_INSET, 3 * mm
    )
    inner = FRAME_INSET + 1.6 * mm
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.roundRect(inner, inner, width - 2 * inner, height - 2 * inner, 2.2 * mm)

    # Kunye cercevenin alt kenarina sabitlenir (ortali)
    footer = _footer_paragraph(_styles(), getattr(doc, "footer_note", FORM_NOTE))
    pad = FRAME_INSET + 6 * mm
    _, _footer_h = footer.wrap(width - 2 * pad, 40 * mm)
    footer.drawOn(canvas, pad, FRAME_INSET + 4 * mm)
    canvas.restoreState()


TRACK_BASE = (
    os.environ.get("PUBLIC_SITE_URL") or "https://www.dubaivizehatti.com"
).strip().strip('"').rstrip("/")

FORM_NOTE = (
    "Bu form başvuru kaydınızın sistem tarafından üretilmiş özetidir; "
    "resmî vize belgesi değildir."
)


def _track_url(app_doc: dict) -> str:
    ref = str(app_doc.get("reference_code") or "").strip()
    return f"{TRACK_BASE}/takip?kod={quote(ref)}" if ref else f"{TRACK_BASE}/takip"


def _qr_drawing(url: str, side: float) -> Drawing:
    """Takip sayfasina goturen kare QR (reportlab dahili, ek bagimlilik yok)."""
    widget = QrCodeWidget(url, barLevel="M", barBorder=0)
    x1, y1, x2, y2 = widget.getBounds()
    drawing = Drawing(
        side, side, transform=[side / (x2 - x1), 0, 0, side / (y2 - y1), 0, 0]
    )
    drawing.add(widget)
    return drawing


def _track_band(app_doc: dict, st: dict) -> Table:
    """Musteri telefonuyla okutup basvuru durumunu goreceklerini anlatan QR bandi (ortalanmis)."""
    url = _track_url(app_doc)
    rows = [
        [_qr_drawing(url, 19 * mm)],
        [Paragraph("TELEFONUNUZDAN BAŞVURU TAKİBİ", st["section_center"])],
        [
            Paragraph(
                "Kodunu kamerayla okutun; başvurunuzun güncel durumu anında açılsın.<br/>"
                "Dilerseniz takip kodunuzla www.dubaivizehatti.com/takip adresinden de "
                "sorgulayabilirsiniz.",
                st["body_center"],
            )
        ],
        [Paragraph(f"Takip kodu: {_safe(app_doc.get('reference_code'))}", st["value_center"])],
    ]
    table = Table(rows, colWidths=_cols(180))
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PANEL),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (0, 0), 10),
                ("BOTTOMPADDING", (0, 0), (0, 0), 6),
                ("TOPPADDING", (0, 1), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 1), (-1, -2), 3),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
            ]
        )
    )
    return table


def _footer_paragraph(st: dict, note: str = FORM_NOTE) -> Paragraph:
    # Kunye tek kaynaktan gelir (content.brand_footer_lines); her satir alt alta yazilir
    text = "<br/>".join(brand_footer_lines() + [note])
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
        topMargin=15 * mm,
        bottomMargin=27 * mm,
        title=f"Dubai Vizesi Başvuru Detayları {app_doc.get('reference_code', '')}",
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
        Spacer(1, 9),
        _track_band(app_doc, st),
    ]
    pdf.build(story, onFirstPage=_draw_frame, onLaterPages=_draw_frame)
    return buffer.getvalue()
