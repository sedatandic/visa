"""Iteration 140: dogum yeri (ve diger pasaport alanlari) pasaporttan yazilir.

Kullanici istegi: "dogum yeri pasaportun icindekini yaz" — basvuru formu PDF'inde
"Dogum yeri: -" gorunuyordu. Pasaport okumasi (`/passport/read`) artik okunan alanlari
dosya kaydina yaziyor, basvuru olusurken bos kalan pasaport alanlari buradan tamamlaniyor.
"""

import asyncio
import io
import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import application_pdf
import ocr_metrics
import routes_public

OCR_FIELDS = {
    "birth_place": "ISTANBUL",
    "passport_issue_place": "ISTANBUL VALILIGI",
    "passport_issue_date": "2022-03-15",
    "nationality": "TR",
}


class FakeUploads:
    def __init__(self, doc=None):
        self.doc = doc
        self.updates = []

    async def find_one(self, _query, _projection=None):
        return self.doc

    async def update_one(self, _query, update):
        self.updates.append(update["$set"])


def _install(monkeypatch, doc) -> FakeUploads:
    col = FakeUploads(doc)
    monkeypatch.setattr(routes_public, "uploads_col", col)
    return col


class TestPasaportAlanlarininTamamlanmasi:
    def test_bos_dogum_yeri_pasaporttan_dolar(self, monkeypatch):
        _install(monkeypatch, {"id": "f1", "ocr": {"fields": OCR_FIELDS}})
        data = {"passport_file_id": "f1", "birth_place": "", "passport_issue_place": ""}
        asyncio.run(routes_public._fill_from_passport_ocr(data))
        assert data["birth_place"] == "ISTANBUL"
        assert data["passport_issue_place"] == "ISTANBUL VALILIGI"

    def test_musteri_girdisi_ezilmez(self, monkeypatch):
        _install(monkeypatch, {"id": "f1", "ocr": {"fields": OCR_FIELDS}})
        data = {"passport_file_id": "f1", "birth_place": "ANKARA"}
        asyncio.run(routes_public._fill_from_passport_ocr(data))
        assert data["birth_place"] == "ANKARA"

    def test_okuma_yoksa_alan_bos_kalir(self, monkeypatch):
        _install(monkeypatch, {"id": "f1"})
        data = {"passport_file_id": "f1", "birth_place": ""}
        asyncio.run(routes_public._fill_from_passport_ocr(data))
        assert data["birth_place"] == ""

    def test_pasaport_dosyasi_yoksa_sorgu_yapilmaz(self, monkeypatch):
        col = _install(monkeypatch, {"id": "f1", "ocr": {"fields": OCR_FIELDS}})
        col.doc = None
        data = {"birth_place": ""}
        asyncio.run(routes_public._fill_from_passport_ocr(data))
        assert data["birth_place"] == ""


class TestOkumaKaydi:
    def test_okunan_alanlar_dosya_kaydina_yazilir(self, monkeypatch):
        col = _install(monkeypatch, None)

        async def fake_record(**_kwargs):
            return {"filled": ["birth_place"], "missing": []}

        monkeypatch.setattr(ocr_metrics, "record_attempt", fake_record)
        result = {"birth_place": "ISTANBUL", "passport_no": "U12345678", "confidence": 0.9}
        asyncio.run(routes_public._ocr_success("f1", result, 1200))

        saved = col.updates[0]["ocr"]
        assert saved["fields"]["birth_place"] == "ISTANBUL"
        assert saved["fields"]["passport_no"] == "U12345678"
        assert set(saved["fields"]) == set(ocr_metrics.TRACKED_FIELDS)


class TestFormPdf:
    def test_dogum_yeri_ilk_harf_buyuk(self):
        assert application_pdf._place("ISTANBUL") == "Istanbul"
        assert application_pdf._place("KAHRAMANMARAS") == "Kahramanmaras"
        assert application_pdf._place("") == ""

    def test_pdf_dogum_yerini_gosterir(self):
        app_doc = {
            "reference_code": "DV-140",
            "created_at": "2026-06-18T09:00:00+00:00",
            "contact": {"full_name": "Test Kullanıcı", "email": "t@ornek.com", "phone": "+905384838224"},
            "travel": {"arrival_date": "2026-10-10", "departure_date": "2026-10-20"},
            "travelers": [
                {
                    "first_name": "Testad",
                    "last_name": "Testsoyad",
                    "birth_date": "1990-05-05",
                    "passport_no": "U11223344",
                    "passport_expiry": "2028-11-18",
                    "visa_short_name": "30 Gün Tek Giriş",
                    "price": 5190,
                    "nationality": "TR",
                    "birth_place": "ISTANBUL",
                }
            ],
            "pricing": {"currency": "TRY", "subtotal": 5190, "total": 5190},
        }
        from pypdf import PdfReader

        data = application_pdf.build_application_pdf(app_doc)
        text = PdfReader(io.BytesIO(data)).pages[0].extract_text()
        # 2026-06-18: dogum yeri artik yolcu tablosunda her yolcu icin kolon olarak yazilir
        assert "Doğum Yeri" in text
        assert "Istanbul" in text
        assert "ISTANBUL" not in text
