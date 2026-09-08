"""Iteration 121: vize dosya numarasi otomatik okuma + hazir dogrulama sayfasi.

Kullanici istegi: musteri GDRFA formunu doldurmak zorunda kalmasin. GDRFA sayfasi
ASP.NET ViewState kullandigi ve query string kabul etmedigi icin hazir dolu bir
devlet baglantisi uretilemiyor; bunun yerine dosya numarasi PDF'ten otomatik
okunup musteriye tek dokunusla kopyalanabilen kendi sayfamiz gonderiliyor.
"""

import asyncio
import io
import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import emailer  # noqa: E402
import file_access  # noqa: E402
import visa_file_number  # noqa: E402
import whatsapp  # noqa: E402


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def sample_visa_pdf(file_no: str = "201/2026/1234567", extra: str = "") -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica", 12)
    c.drawString(60, 750, "ENTRY PERMIT / TOURIST VISA")
    c.drawString(60, 720, "Full Name : SEDAT ANDIC")
    c.drawString(60, 700, "Date of Birth : 01-08-1981")
    c.drawString(60, 680, f"File No. : {file_no}")
    c.drawString(60, 660, "Issue Date : 08/09/2026    Expiry Date : 08/10/2026")
    if extra:
        c.drawString(60, 640, extra)
    c.showPage()
    c.save()
    return buf.getvalue()


class TestNumberParsing:
    def test_labelled_same_line(self):
        assert visa_file_number.extract_from_text("File No. : 201/2026/1234567") == "201/2026/1234567"

    def test_label_on_previous_line(self):
        text = "ENTRY PERMIT\nFile Number\n201/2026/98765"
        assert visa_file_number.extract_from_text(text) == "201/2026/98765"

    def test_arabic_label(self):
        assert visa_file_number.extract_from_text("رقم الملف 201/2026/4567890") == "201/2026/4567890"

    def test_spaces_around_slashes(self):
        assert visa_file_number.extract_from_text("File No 201 / 2026 / 1234567") == "201/2026/1234567"

    def test_dates_are_not_mistaken_for_file_numbers(self):
        assert visa_file_number.extract_from_text("Issue Date 01/2026/12") == ""
        assert visa_file_number.extract_from_text("Ref 12/2026/1") == ""

    def test_plain_strips_separators(self):
        assert visa_file_number.plain("201/2026/1234567") == "20120261234567"
        assert visa_file_number.plain("") == ""

    def test_all_numbers_in_document_order_without_duplicates(self):
        text = "File No 201/2026/111111\nFile No 201/2026/222222\nagain 201/2026/111111"
        assert visa_file_number.extract_all_from_text(text) == [
            "201/2026/111111",
            "201/2026/222222",
        ]

    def test_normalize_rejects_garbage(self):
        assert visa_file_number.normalize("merhaba") == ""
        assert visa_file_number.normalize("") == ""


class TestPdfExtraction:
    @pytest.fixture
    def storage(self, monkeypatch):
        state = {"record": None, "data": b"", "raise": False}

        class FakeUploads:
            async def find_one(self, _query):
                return state["record"]

        def fake_get_object(_path):
            if state["raise"]:
                raise RuntimeError("storage down")
            return state["data"], "application/pdf"

        monkeypatch.setattr(visa_file_number, "uploads_col", FakeUploads())
        monkeypatch.setattr(visa_file_number, "get_object", fake_get_object)
        return state

    def _pdf_record(self, state, data):
        state["record"] = {
            "id": "f1",
            "storage_path": "x/y.pdf",
            "content_type": "application/pdf",
        }
        state["data"] = data

    def test_reads_number_from_real_pdf(self, storage):
        self._pdf_record(storage, sample_visa_pdf())
        assert run(visa_file_number.extract_from_upload("f1")) == ["201/2026/1234567"]

    def test_labelled_number_comes_first(self, storage):
        self._pdf_record(
            storage, sample_visa_pdf("201/2026/999999", extra="Sponsor Ref 201/2026/111111")
        )
        numbers = run(visa_file_number.extract_from_upload("f1"))
        assert numbers[0] == "201/2026/999999"
        assert "201/2026/111111" in numbers

    def test_pdf_without_number_returns_empty(self, storage):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        c.drawString(60, 700, "Bu belgede dosya numarasi yok")
        c.showPage()
        c.save()
        self._pdf_record(storage, buf.getvalue())
        assert run(visa_file_number.extract_from_upload("f1")) == []

    def test_missing_file_id_returns_empty(self, storage):
        assert run(visa_file_number.extract_from_upload("")) == []

    def test_image_document_is_skipped(self, storage):
        storage["record"] = {"id": "f1", "storage_path": "x/y.jpg", "content_type": "image/jpeg"}
        assert run(visa_file_number.extract_from_upload("f1")) == []

    def test_storage_error_returns_empty(self, storage):
        self._pdf_record(storage, sample_visa_pdf())
        storage["raise"] = True
        assert run(visa_file_number.extract_from_upload("f1")) == []

    def test_corrupt_pdf_returns_empty(self, storage):
        self._pdf_record(storage, b"not really a pdf")
        assert run(visa_file_number.extract_from_upload("f1")) == []


class TestAnnotate:
    @pytest.fixture
    def apps(self, monkeypatch):
        state = {"numbers": ["201/2026/1234567"], "written": None}

        async def fake_extract(_file_id):
            return state["numbers"]

        class FakeApps:
            async def update_one(self, _query, update):
                state["written"] = update["$set"]

        monkeypatch.setattr(visa_file_number, "extract_from_upload", fake_extract)
        monkeypatch.setattr(visa_file_number, "applications_col", FakeApps())
        return state

    def test_writes_numbers_to_application(self, apps):
        result = run(visa_file_number.annotate("app1", {"file_id": "f1"}))
        assert result["file_number"] == "201/2026/1234567"
        assert result["file_numbers"] == ["201/2026/1234567"]
        assert apps["written"]["visa_result.file_number"] == "201/2026/1234567"

    def test_nothing_written_when_no_number_found(self, apps):
        apps["numbers"] = []
        result = run(visa_file_number.annotate("app1", {"file_id": "f1"}))
        assert "file_number" not in result
        assert apps["written"] is None


class TestVerifyLink:
    def test_signed_link_is_valid(self, monkeypatch):
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        url = visa_file_number.verify_url("https://site.example", "app-123")
        assert url.startswith("https://site.example/vize-dogrula/app-123?t=")
        token = url.split("t=", 1)[1]
        assert file_access.token_valid("app-123", token) is True

    def test_token_does_not_work_for_another_application(self, monkeypatch):
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        token = visa_file_number.verify_url("https://site.example", "app-123").split("t=", 1)[1]
        assert file_access.token_valid("app-999", token) is False

    def test_no_link_without_origin_or_id(self, monkeypatch):
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        assert visa_file_number.verify_url("", "app-1") == ""
        assert visa_file_number.verify_url("https://site.example", "") == ""


class TestMessagesCarryTheLink:
    APP = {
        "id": "app-1",
        "reference_code": "DV-TEST1234",
        "contact": {"full_name": "Sedat Andiç"},
        "travelers": [{"first_name": "SEDAT", "last_name": "ANDIC", "visa_short_name": "30 Gün"}],
        "visa_result": {"file_id": "f1", "file_number": "201/2026/1234567"},
    }

    def test_email_shows_number_and_button(self):
        html = emailer.visa_ready_html(
            self.APP, "https://x/indir", "", True, "https://site.example/vize-dogrula/app-1?t=abc"
        )
        assert "201/2026/1234567" in html
        assert "Doğrulama bilgilerimi aç" in html
        assert "https://site.example/vize-dogrula/app-1?t=abc" in html

    def test_email_without_link_keeps_manual_steps_only(self):
        html = emailer.visa_ready_html(self.APP, "https://x/indir")
        assert "Doğrulama bilgilerimi aç" not in html
        assert "File Number" in html

    def test_whatsapp_short_version_when_link_exists(self):
        text = whatsapp.visa_ready_wa_text(
            self.APP, verify_link="https://site.example/vize-dogrula/app-1?t=abc"
        )
        assert "201/2026/1234567" in text
        assert "https://site.example/vize-dogrula/app-1?t=abc" in text
        # Adimlar sayfada oldugu icin mesaja tekrar yazilmaz
        assert "1. Bağlantıyı açın" not in text
        assert len(text) <= 1024

    def test_whatsapp_falls_back_to_steps_without_link(self):
        text = whatsapp.visa_ready_wa_text(self.APP)
        assert whatsapp.GDRFA_STATUS_URL in text
        assert "1. Bağlantıyı açın" in text

    def test_caption_stays_within_limit_with_long_reference(self):
        app = {**self.APP, "reference_code": "DV-" + "X" * 40}
        text = whatsapp.visa_ready_wa_text(
            app, verify_link="https://site.example/vize-dogrula/" + "a" * 60 + "?t=" + "b" * 60
        )
        assert len(text) <= 1024
