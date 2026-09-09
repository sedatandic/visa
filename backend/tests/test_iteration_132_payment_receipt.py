"""Iteration 132: odeme ozeti (fatura goruntusu) PDF'i.

Kullanici istegi: "Aynı düzenle müşteriye e-posta ile giden ödeme özeti/fatura PDF'i".

Kapsam:
- PDF uretimi (basvuru + magaza siparisi) ve icerik kontrolleri,
- tutarlarin form ile ayni hizada (sola dayali, ayni kolon) olmasi,
- odeme e-postalarina ek olarak baglanmasi,
- indirme uclarinin yetki kontrolu (takip kodu + soyad / siparis kodu + e-posta / admin).
"""

import io
import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import application_pdf  # noqa: E402
import payment_receipt_pdf as receipt  # noqa: E402

APPLICATION = {
    "reference_code": "DV-TEST132",
    "created_at": "2026-06-14T10:00:00+00:00",
    "currency": "TRY",
    "contact": {"full_name": "Sedat Andiç", "email": "musteri@ornek.com", "phone": "+90 538 483 82 24"},
    "payment": {"status": "paid", "method": "card", "paid_at": "2026-06-15T09:12:00+00:00"},
    "travelers": [
        {"first_name": "Sedat", "last_name": "Andiç", "visa_short_name": "30 Gün Tek Giriş", "price": 5190},
        {"first_name": "Elif", "last_name": "Andiç", "visa_short_name": "30 Gün Tek Giriş", "price": 5190},
    ],
    "pricing": {
        "currency": "TRY",
        "subtotal": 10380,
        "family_discount": 1038,
        "family_discount_rate": 0.10,
        "addons": [{"name": "Ekspres hizmet", "quantity": 1, "total": 1500}],
        "store_items": [
            {"name": "Seyahat sağlık sigortası", "quantity": 2, "total": 600, "scheduled_date": "2026-09-24"}
        ],
        "total": 11442,
    },
}

ORDER = {
    "reference_code": "SV-TEST132",
    "created_at": "2026-06-14T10:00:00+00:00",
    "currency": "TRY",
    "contact": {"full_name": "Ayşe Yılmaz", "email": "ayse@ornek.com", "phone": "+90 532 000 00 00"},
    "payment": {"status": "paid", "method": "bank_transfer", "paid_at": "2026-06-15T11:30:00+00:00"},
    "items": [
        {"name": "Dubai eSIM 10 GB", "quantity": 1, "total": 690},
        {"name": "Seyahat sağlık sigortası", "quantity": 2, "total": 600, "scheduled_date": "2026-10-01"},
    ],
    "bundle_discount": 129,
    "price": 1161,
}


def pdf_text(data: bytes) -> str:
    """PDF metnini pdfminer olmadan okumak icin: uretilen akista arama yapilir."""
    from pypdf import PdfReader

    return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages)


class TestApplicationReceipt:
    @pytest.fixture(scope="class")
    def data(self):
        return receipt.build_receipt_pdf(APPLICATION)

    def test_is_single_page_pdf(self, data):
        from pypdf import PdfReader

        assert data.startswith(b"%PDF")
        assert len(PdfReader(io.BytesIO(data)).pages) == 1

    def test_shows_payment_band(self, data):
        text = pdf_text(data)
        assert "Ödeme Özeti" in text
        assert "DV-TEST132" in text
        assert "Ödendi" in text
        assert "Kredi / Banka Kartı" in text
        assert "15.06.2026" in text  # odeme tarihi

    def test_lists_every_paid_line(self, data):
        text = pdf_text(data)
        assert "Sedat Andiç · 30 Gün Tek Giriş" in text
        assert "Ekspres hizmet" in text
        assert "Seyahat sağlık sigortası" in text

    def test_summary_has_subtotal_discount_total(self, data):
        text = pdf_text(data)
        assert "Ara toplam" in text
        assert "Aile indirimi (%10)" in text
        assert "TOPLAM" in text
        assert "11.445,00 TL" in text or "11.442,00 TL" in text

    def test_seller_and_invoice_note(self, data):
        text = pdf_text(data)
        assert "Moruya Travel Solutions Turizm Ltd. Şti." in text
        assert "e-Arşiv" in text  # resmi fatura ayri gonderilir uyarisi
        assert "A Grubu Seyahat Acentesi" in text

    def test_filename_uses_reference(self):
        assert receipt.receipt_filename(APPLICATION) == "Odeme-Ozeti-DV-TEST132.pdf"


class TestOrderReceipt:
    @pytest.fixture(scope="class")
    def data(self):
        return receipt.build_receipt_pdf(ORDER, "order")

    def test_order_band_and_items(self, data):
        text = pdf_text(data)
        assert "SV-TEST132" in text
        assert "Havale / EFT" in text
        assert "Dubai eSIM 10 GB" in text

    def test_order_summary(self, data):
        text = pdf_text(data)
        assert "Ara toplam" in text
        assert "1.290,00 TL" in text  # kalemler toplami
        assert "1.161,00 TL" in text  # indirim sonrasi toplam

    def test_pending_payment_is_labelled(self):
        doc = {**ORDER, "payment": {"status": "pending", "method": "bank_transfer"}}
        assert "Bekliyor" in pdf_text(receipt.build_receipt_pdf(doc, "order"))


class TestSharedLayout:
    def test_amount_column_matches_traveler_table(self):
        """Tutar kolonu ayni yerden baslamali: ozet tablosu 154+26 mm."""
        st = application_pdf._styles()
        summary = application_pdf._amount_table([("Ara toplam", "1.000,00 TL")], st)
        travelers = application_pdf._travelers_table(APPLICATION, st)
        assert round(sum(summary._argW), 2) == round(sum(travelers._argW), 2)
        assert round(summary._argW[0], 2) == round(sum(travelers._argW[:-1]), 2)
        assert round(summary._argW[-1], 2) == round(travelers._argW[-1], 2)

    def test_receipt_footer_note_differs_from_form(self):
        assert receipt.RECEIPT_NOTE != application_pdf.FORM_NOTE
        assert "e-Arşiv" in receipt.RECEIPT_NOTE
        assert "resmî vize belgesi değildir" in application_pdf.FORM_NOTE

    def test_form_still_uses_form_note(self):
        text = pdf_text(application_pdf.build_application_pdf(APPLICATION))
        assert "resmî vize belgesi değildir" in text
        assert "e-Arşiv" not in text


class TestEmailWiring:
    def test_receipt_attachment_shape(self):
        attachments = receipt.receipt_attachment(APPLICATION)
        assert len(attachments) == 1
        item = attachments[0]
        assert item["filename"] == "Odeme-Ozeti-DV-TEST132.pdf"
        assert item["content_type"] == "application/pdf"
        assert item["content"].startswith(b"%PDF")

    @pytest.mark.parametrize(
        "path,func",
        [
            ("routes_payments.py", "_notify_application_payment"),
            ("routes_payments.py", "_mark_order_paid"),
        ],
    )
    def test_payment_emails_attach_receipt(self, path, func):
        source = open(os.path.join(BACKEND_DIR, path)).read()
        block = source.split(f"async def {func}(")[1].split("\nasync def ")[0]
        assert "receipt_attachment(" in block, f"{func} odeme ozetini eklemeli"

    def test_admin_payment_email_attaches_receipt(self):
        source = open(os.path.join(BACKEND_DIR, "routes_admin.py")).read()
        block = source.split("async def admin_mark_paid")[1].split("\n@router")[0]
        assert 'kind="payment_received"' in block
        assert "receipt_attachment(serialize_doc(fresh))" in block


class TestDownloadEndpoints:
    def test_public_and_admin_routes_exist(self):
        public = open(os.path.join(BACKEND_DIR, "routes_public.py")).read()
        admin = open(os.path.join(BACKEND_DIR, "routes_admin.py")).read()
        store = open(os.path.join(BACKEND_DIR, "routes_store.py")).read()
        assert '@router.get("/applications/receipt.pdf")' in public
        assert '@router.get("/admin/applications/{application_id}/receipt.pdf")' in admin
        assert '@router.get("/orders/{reference}/receipt.pdf")' in store

    def test_order_receipt_checks_email(self):
        store = open(os.path.join(BACKEND_DIR, "routes_store.py")).read()
        block = store.split("async def order_receipt_pdf(")[1].split("\n@router")[0]
        assert "_find_order_for_customer(" in block, "siparis kodu + e-posta dogrulanmali"

    def test_admin_receipt_requires_admin(self):
        admin = open(os.path.join(BACKEND_DIR, "routes_admin.py")).read()
        block = admin.split("/admin/applications/{application_id}/receipt.pdf")[1][:400]
        assert "Depends(require_admin)" in block
