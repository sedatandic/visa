"""Iteration 139: fatura (odeme ozeti) ve police PDF'leri icin altin kopya testleri.

Kullanici istegi: "Fatura ve police PDF'leri icin altin-kopya testi yaz, sonra karmasik
fonksiyonlari guvenle bol."

Altin kopya yaklasimi: sabit (deterministik) fixture'lardan PDF uretilir, metni ve
tablo kolon genislikleri `tests/golden/*.txt` altindaki kayitli kopyayla karsilastirilir.
Kasitli tasarim degisikliginde kopyalar `UPDATE_GOLDEN=1 pytest ...` ile yenilenir.

Police PDF'i saglayicidan indirilir; police tarafinda altin kopya dosya kaydini ve
musteriye giden e-posta / WhatsApp metnini korur.
"""

import asyncio
import io
import os
import sys
from pathlib import Path

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import application_pdf
import insurance_delivery
import insurance_provider
import payment_receipt_pdf as receipt

GOLDEN_DIR = Path(__file__).parent / "golden"
UPDATE = os.environ.get("UPDATE_GOLDEN") == "1"


def _text(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        body = "\n".join(
            line.strip() for line in (page.extract_text() or "").splitlines() if line.strip()
        )
        pages.append(f"--- sayfa {index} ---\n{body}")
    return "\n".join(pages)


def golden(name: str, content: str) -> None:
    """Uretilen ciktiyi kayitli altin kopyayla karsilastirir."""
    path = GOLDEN_DIR / f"{name}.txt"
    body = content.strip() + "\n"
    if UPDATE:
        GOLDEN_DIR.mkdir(exist_ok=True)
        path.write_text(body, encoding="utf-8")
    assert path.exists(), f"altin kopya yok: {path.name} (UPDATE_GOLDEN=1 ile uretin)"
    assert path.read_text(encoding="utf-8") == body, (
        f"{path.name} altin kopyasindan sapma var; degisiklik kasitliysa "
        "UPDATE_GOLDEN=1 ile yenileyin"
    )


APPLICATION_FAMILY = {
    "reference_code": "DV-GOLD-001",
    "created_at": "2026-06-14T10:00:00+00:00",
    "currency": "TRY",
    "processing_days": "2 iş günü",
    "contact": {
        "full_name": "Sedat Andıç",
        "email": "sedat@ornek.com",
        "phone": "+905384838224",
    },
    "payment": {"status": "paid", "method": "card", "paid_at": "2026-06-15T09:12:00+00:00"},
    "travel": {
        "arrival_date": "2026-09-20",
        "departure_date": "2026-10-02",
        "accommodation": "Rove Downtown",
        "flight_no": "TK 764",
    },
    "travelers": [
        {
            "first_name": "Sedat",
            "last_name": "Andıç",
            "birth_date": "1985-04-11",
            "passport_no": "U12345678",
            "passport_expiry": "2032-03-15",
            "visa_short_name": "30 Gün Tek Giriş",
            "price": 5190,
            "currency": "TRY",
            "nationality": "TR",
            "birth_place": "İstanbul",
        },
        {
            "first_name": "Elif",
            "last_name": "Andıç",
            "birth_date": "2018-07-02",
            "passport_no": "U87654321",
            "passport_expiry": "2030-01-20",
            "visa_short_name": "30 Gün Tek Giriş (çocuk)",
            "applicant_type": "child",
            "price": 2470,
            "currency": "TRY",
        },
    ],
    "pricing": {
        "currency": "TRY",
        "subtotal": 7660,
        "family_discount": 766,
        "family_discount_rate": 0.10,
        "addons": [{"name": "Ekspres hizmet", "quantity": 2, "total": 4940}],
        "store_items": [
            {"name": "Seyahat sağlık sigortası (30 gün)", "quantity": 2, "total": 1288},
            {
                "name": "Dubai Çöl Safarisi",
                "quantity": 2,
                "total": 4440,
                "scheduled_date": "2026-09-21",
                "scheduled_time": "15:00",
            },
        ],
        "visa_insurance_discount": 519,
        "visa_insurance_discount_rate": 0.10,
        "visa_insurance_discount_title": "Sigorta dahil vize indirimi",
        "bundle_discount": 1200,
        "bundle_discount_rate": 0.10,
        "bundle_discount_title": "Seyahat paketi indirimi",
        "total": 15843,
    },
}

APPLICATION_SINGLE = {
    "reference_code": "DV-GOLD-002",
    "created_at": "2026-06-16T08:30:00+00:00",
    "currency": "TRY",
    "processing_days": "yaklaşık 8 mesai saati",
    "contact": {
        "full_name": "Ayşe Yılmaz",
        "email": "ayse@ornek.com",
        "phone": "+905320000000",
    },
    "payment": {"status": "awaiting_transfer", "method": "bank_transfer"},
    "travel": {"dates_unknown": True, "travel_window": "1_3_months"},
    "travelers": [
        {
            "first_name": "Ayşe",
            "last_name": "Yılmaz",
            "birth_date": "1990-01-01",
            "passport_no": "U11223344",
            "passport_expiry": "2031-05-09",
            "visa_short_name": "60 Gün Tek Giriş",
            "price": 9880,
            "currency": "TRY",
            "nationality": "TR",
            "birth_place": "Ankara",
        }
    ],
    "pricing": {"currency": "TRY", "subtotal": 9880, "total": 9880},
}

ORDER = {
    "reference_code": "SV-GOLD-003",
    "created_at": "2026-06-14T12:45:00+00:00",
    "currency": "TRY",
    "contact": {
        "first_name": "Murat",
        "last_name": "Demir",
        "email": "murat@ornek.com",
        "phone": "+905331112233",
    },
    "payment": {"status": "awaiting_transfer", "method": "bank_transfer"},
    "items": [
        {"name": "Dubai eSIM 10 GB", "quantity": 1, "total": 690},
        {
            "name": "Seyahat sağlık sigortası (15 gün)",
            "quantity": 2,
            "total": 1120,
            "scheduled_date": "2026-10-01",
        },
    ],
    "bundle_discount": 181,
    "price": 1629,
}

DOCUMENTS = [
    {"label": "Pasaport kimlik sayfası · Sedat Andıç", "attached": True},
    {"label": "Vesikalık fotoğraf · Sedat Andıç", "attached": True},
    {"label": "Pasaport kimlik sayfası · Elif Andıç", "attached": False},
]

POLICY_TASK = {
    "id": "task-gold-139",
    "order_id": "order-gold-139",
    "order_reference": "SV-GOLD-003",
    "customer": {
        "full_name": "Murat Demir",
        "email": "murat@ornek.com",
        "phone": "+905331112233",
    },
}

POLICY_LINK = "https://www.dubaivizehatti.com/api/files/pol-123?t=imzali-jeton"


class TestFaturaAltinKopya:
    def test_basvuru_faturasi(self):
        golden("fatura_basvuru_aile", _text(receipt.build_receipt_pdf(APPLICATION_FAMILY)))

    def test_basvuru_faturasi_havale_bekliyor(self):
        golden("fatura_basvuru_tek_havale", _text(receipt.build_receipt_pdf(APPLICATION_SINGLE)))

    def test_siparis_faturasi(self):
        golden("fatura_siparis_havale", _text(receipt.build_receipt_pdf(ORDER, "order")))

    def test_tek_sayfa_ve_a4(self):
        from pypdf import PdfReader

        for doc, kind in ((APPLICATION_FAMILY, "application"), (ORDER, "order")):
            data = receipt.build_receipt_pdf(doc, kind)
            reader = PdfReader(io.BytesIO(data))
            assert len(reader.pages) == 1
            box = reader.pages[0].mediabox
            assert (round(float(box.width)), round(float(box.height))) == (595, 842)


class TestFormAltinKopya:
    def test_basvuru_formu(self):
        data = application_pdf.build_application_pdf(APPLICATION_FAMILY, DOCUMENTS)
        golden("form_basvuru_aile", _text(data))

    def test_basvuru_formu_tarih_belirsiz(self):
        data = application_pdf.build_application_pdf(APPLICATION_SINGLE)
        golden("form_basvuru_tarih_belirsiz", _text(data))


class TestYerlesimAltinKopya:
    def test_kolon_genislikleri(self):
        st = application_pdf._styles()
        tables = {
            "baslik": application_pdf._header(APPLICATION_FAMILY, st),
            "takip_bandi": application_pdf._reference_band(APPLICATION_FAMILY, st),
            "ikili_alanlar": application_pdf._pairs_table(
                application_pdf._contact_pairs(APPLICATION_FAMILY), st
            ),
            "yolcu_tablosu": application_pdf._travelers_table(APPLICATION_FAMILY, st),
            "tutar_tablosu": application_pdf._price_table(APPLICATION_FAMILY, st),
            "qr_bandi": application_pdf._track_band(APPLICATION_FAMILY, st),
            "fatura_bandi": receipt._info_band(APPLICATION_FAMILY, st, "TAKİP KODU"),
            "fatura_kalemleri": receipt._items_table(
                receipt._application_items(APPLICATION_FAMILY), st
            ),
        }
        lines = [
            f"{label}: " + " | ".join(f"{w:.1f}" for w in table._argW)
            for label, table in tables.items()
        ]
        golden("yerlesim_kolonlari", "\n".join(lines))

    def test_tl_sutunu_ayni_hizada(self):
        """Kullanici istegi: dokum satirlarindaki TL, yolcu tablosundakiyle ayni hizada."""
        import pymupdf

        for name, data in (
            ("form", application_pdf.build_application_pdf(APPLICATION_FAMILY, DOCUMENTS)),
            ("fatura", receipt.build_receipt_pdf(APPLICATION_FAMILY)),
        ):
            page = pymupdf.open(stream=data, filetype="pdf")[0]
            positions = {round(word[0], 1) for word in page.get_text("words") if word[4] == "TL"}
            assert len(positions) == 1, f"{name}: TL kolonu farkli hizalarda {positions}"


class TestFiyatDokumu:
    """Fiyat/kalem satirlari (bolunecek karmasik fonksiyonlarin ciktisi)."""

    def test_form_fiyat_satirlari(self):
        rows = application_pdf._pricing_rows(APPLICATION_FAMILY)
        golden("dokum_form_fiyat", "\n".join(f"{label} = {value}" for label, value in rows))

    def test_fatura_kalem_ve_ozet_satirlari(self):
        items = receipt._application_items(APPLICATION_FAMILY)
        summary = receipt._application_summary_rows(APPLICATION_FAMILY)
        report = ["[kalemler]"]
        report += [f"{label} x{qty} = {amount}" for label, qty, amount in items]
        report.append("[ozet]")
        report += [f"{label} = {value}" for label, value in summary]
        report.append("[siparis kalemleri]")
        report += [f"{label} x{qty} = {amount}" for label, qty, amount in receipt._order_items(ORDER)]
        report.append("[siparis ozeti]")
        report += [f"{label} = {value}" for label, value in receipt._order_summary_rows(ORDER)]
        golden("dokum_fatura_kalemleri", "\n".join(report))

    def test_indirim_yuzdesi_yoksa_parantez_yazilmaz(self):
        """Oran alani bos gelen indirimde "(%0)" yazilmamali (form ve fatura ayni davranir)."""
        doc = {
            **APPLICATION_SINGLE,
            "pricing": {**APPLICATION_SINGLE["pricing"], "family_discount": 500},
        }
        form = dict(application_pdf._pricing_rows(doc))
        fatura = dict(receipt._application_summary_rows(doc))
        assert "Aile indirimi" in form and "Aile indirimi" in fatura
        assert not any("(%0)" in label for label in list(form) + list(fatura))


class TestPoliceTeslimi:
    def test_musteri_metinleri(self):
        report = [
            "[e-posta]",
            insurance_delivery.policy_html(
                POLICY_TASK, POLICY_LINK, "Poliçeniz düzenlendi."
            ),
            "[whatsapp]",
            insurance_delivery.policy_wa_text(POLICY_TASK, POLICY_LINK),
        ]
        golden("police_teslim_metinleri", "\n".join(report))

    def test_dosya_kaydi(self, monkeypatch):
        """Police PDF'i object storage'a yazilir ve uploads kaydi olusur."""
        saved = {}

        def fake_put(path, data, content_type):
            saved["path"] = path
            saved["content_type"] = content_type
            return {"path": f"s3://{path}", "size": len(data)}

        class FakeUploads:
            async def insert_one(self, doc):
                saved["doc"] = doc

        monkeypatch.setattr(insurance_provider, "put_object", fake_put)
        monkeypatch.setattr(insurance_provider, "uploads_col", FakeUploads())
        file_id = asyncio.run(
            insurance_provider._store_policy_pdf(POLICY_TASK, b"%PDF-1.4 police")
        )

        doc = dict(saved["doc"])
        assert doc.pop("id") == file_id
        assert doc.pop("created_at")
        report = [f"yol: {saved['path'].replace(file_id, '<id>')}"]
        report += [f"{key}: {str(doc[key]).replace(file_id, '<id>')}" for key in sorted(doc)]
        golden("police_dosya_kaydi", "\n".join(report))
