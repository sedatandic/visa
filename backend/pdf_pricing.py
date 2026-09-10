"""PDF fiyat dokumu yardimcilari.

Basvuru formu (`application_pdf`) ve odeme ozeti/fatura (`payment_receipt_pdf`) ayni
kalem ve indirim mantigini paylasir; tek kaynak burasi. Ciktilar altin kopya
testleriyle korunur (`tests/test_iteration_139_pdf_golden.py`).
"""

from datetime import datetime

from emailer import money as _money_html

# indirim anahtari -> (tutar alani, oran alani, baslik alani, varsayilan baslik)
DISCOUNTS = {
    "family": ("family_discount", "family_discount_rate", None, "Aile indirimi"),
    "visa_insurance": (
        "visa_insurance_discount",
        "visa_insurance_discount_rate",
        "visa_insurance_discount_title",
        "Sigorta dahil vize indirimi",
    ),
    "bundle": (
        "bundle_discount",
        "bundle_discount_rate",
        "bundle_discount_title",
        "Paket indirimi",
    ),
}
ALL_DISCOUNTS = ("family", "visa_insurance", "bundle")


def money(amount: float, currency: str = "TRY") -> str:
    """PDF yazi tipinde ₺ glifi yok; TL yazimina cevirir."""
    return _money_html(amount, currency).replace("₺", "TL")


def fmt_date(value) -> str:
    raw = str(value or "")[:10]
    try:
        return datetime.strptime(raw, "%Y-%m-%d").strftime("%d.%m.%Y")  # noqa: DTZ007
    except ValueError:
        return raw


def currency_of(doc: dict) -> str:
    return (doc.get("pricing") or {}).get("currency") or doc.get("currency") or "TRY"


def discount_rows(pricing: dict, currency: str, keys=ALL_DISCOUNTS) -> list:
    """(etiket, "- tutar") satirlari; oran verilmisse etikete yuzde eklenir."""
    rows = []
    for key in keys:
        amount_field, rate_field, title_field, default_title = DISCOUNTS[key]
        amount = pricing.get(amount_field)
        if not amount:
            continue
        label = (title_field and pricing.get(title_field)) or default_title
        pct = round(float(pricing.get(rate_field) or 0) * 100)
        rows.append((f"{label} (%{pct})" if pct else label, "- " + money(amount, currency)))
    return rows


def schedule_suffix(item: dict, with_time: bool = False) -> str:
    """Tur/randevu kalemlerinde etikete eklenen " (21.09.2026 15:00)" parcasi."""
    if not item.get("scheduled_date"):
        return ""
    slot = f" {item['scheduled_time']}" if with_time and item.get("scheduled_time") else ""
    return f" ({fmt_date(item['scheduled_date'])}{slot})"


def extras_rows(pricing: dict, currency: str) -> list:
    """Form dokumu: ek hizmet + magaza kalemleri (etiket adet iceride, tutar)."""
    rows = [
        (f"{addon['name']} x{addon['quantity']}", money(addon["total"], currency))
        for addon in pricing.get("addons") or []
    ]
    rows += [
        (
            f"{item['name']} x{item['quantity']}{schedule_suffix(item, with_time=True)}",
            money(item["total"], currency),
        )
        for item in pricing.get("store_items") or []
    ]
    return rows


def store_rows(items, currency: str) -> list:
    """Fatura kalemleri: (aciklama, adet, tutar)."""
    return [
        (
            f"{item.get('name', '')}{schedule_suffix(item)}",
            str(item.get("quantity", 1)),
            money(item.get("total", 0), currency),
        )
        for item in items or []
    ]


def paid_items(doc: dict) -> list:
    """Basvuru faturasi kalemleri: vize bedelleri + ek hizmetler + magaza kalemleri."""
    currency = currency_of(doc)
    pricing = doc.get("pricing") or {}
    rows = []
    for traveler in doc.get("travelers") or []:
        name = f"{traveler.get('first_name', '')} {traveler.get('last_name', '')}".strip()
        visa = traveler.get("visa_short_name") or traveler.get("visa_type_name") or "Vize"
        rows.append((f"{name} · {visa}", "1", money(traveler.get("price", 0), currency)))
    rows += store_rows(pricing.get("addons"), currency)
    rows += store_rows(pricing.get("store_items"), currency)
    return rows


def gross_subtotal(pricing: dict) -> float:
    """Indirimsiz ara toplam: vize bedelleri + ek hizmetler + magaza kalemleri."""
    extras = (pricing.get("addons") or []) + (pricing.get("store_items") or [])
    return float(pricing.get("subtotal", 0) or 0) + sum(
        float(item.get("total", 0) or 0) for item in extras
    )
