"""Iteration 120: vize hazir e-postasi - GDRFA dogrulama adimlari + PDF eki.

Kullanici istegi: vize cikinca musteriye WhatsApp mesajina benzer bir e-posta gitsin;
resmi GDRFA sorgulama linki ve adimlari bulunsun, vize belgesi de ekte olsun.
Cumleler orijinal WhatsApp metniyle birebir ayni olmamali.
"""

import asyncio
import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import application_docs  # noqa: E402
import emailer  # noqa: E402


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


APP_DOC = {
    "reference_code": "DV-TEST1234",
    "contact": {"full_name": "Sedat Andiç", "email": "musteri@ornek.com"},
    "travelers": [
        {
            "first_name": "SEDAT",
            "last_name": "ANDIC",
            "visa_short_name": "30 Gün Tek Giriş",
            "price": 4990,
            "currency": "TRY",
        }
    ],
}


@pytest.fixture
def html_attached():
    return emailer.visa_ready_html(APP_DOC, "https://x/indir", "", True)


@pytest.fixture
def html_link_only():
    return emailer.visa_ready_html(APP_DOC, "https://x/indir", "", False)


class TestGdrfaBlock:
    def test_official_inquiry_link_is_present(self, html_attached):
        assert emailer.GDRFA_STATUS_URL in html_attached
        assert "smart.gdrfad.gov.ae" in html_attached

    def test_every_step_is_listed(self, html_attached):
        for keyword in ("English", "File", "First Name", "File Number", "bölü işareti"):
            assert keyword in html_attached

    def test_steps_are_ordered_list(self, html_attached):
        assert "<ol" in html_attached
        assert html_attached.count("<li") >= len(emailer.GDRFA_STEPS)

    def test_marked_as_optional(self, html_attached):
        assert "zorunlu değildir" in html_attached

    def test_wording_is_not_copied_from_whatsapp_message(self, html_attached):
        # Orijinal WhatsApp metninden birebir cumleler gecmemeli
        for original in (
            "Vizeniz tarafınıza gönderildi",
            "Dilerseniz aşağıdaki resmi linkten",
            "Linke tıklayın",
            "Nasıl kontrol edilir?",
            "Şimdiden güzel bir seyahat diliyoruz",
            "kendi isminizi İngilizce karakterlerle yazın",
        ):
            assert original not in html_attached


class TestDeliveryWording:
    def test_attachment_wording_when_attached(self, html_attached):
        assert "ekinde" in html_attached

    def test_link_wording_when_not_attached(self, html_link_only):
        assert "ekinde" not in html_link_only
        assert "butondan indirebilirsiniz" in html_link_only

    def test_download_button_always_present(self, html_attached, html_link_only):
        for html in (html_attached, html_link_only):
            assert "https://x/indir" in html
            assert "Vize belgenizi indir" in html

    def test_approval_and_traveler_table(self, html_attached):
        assert "DV-TEST1234" in html_attached
        assert "onaylandı" in html_attached
        assert "hayırlı olsun" in html_attached
        assert "SEDAT" in html_attached

    def test_advisor_note_is_rendered(self):
        html = emailer.visa_ready_html(APP_DOC, "https://x/indir", "Pasaportunuzu yanınıza alın")
        assert "Pasaportunuzu yanınıza alın" in html

    def test_note_is_escaped(self):
        html = emailer.visa_ready_html(APP_DOC, "https://x/indir", "<script>x</script>")
        assert "<script>" not in html


class TestVisaAttachment:
    @pytest.fixture
    def storage(self, monkeypatch):
        state = {"record": None, "data": b"%PDF-1.4 vize", "raise": False}

        class FakeUploads:
            async def find_one(self, _query):
                return state["record"]

        def fake_get_object(_path):
            if state["raise"]:
                raise RuntimeError("storage down")
            return state["data"], "application/pdf"

        monkeypatch.setattr(application_docs, "uploads_col", FakeUploads())
        monkeypatch.setattr(application_docs, "get_object", fake_get_object)
        return state

    def test_returns_attachment_for_stored_pdf(self, storage):
        storage["record"] = {
            "id": "f1",
            "storage_path": "x/y.pdf",
            "original_filename": "visa.pdf",
            "content_type": "application/pdf",
        }
        result = run(application_docs.visa_pdf_attachment("f1", "DV-TEST1234"))
        assert len(result) == 1
        assert result[0]["filename"] == "vize-dv-test1234.pdf"
        assert result[0]["content"] == b"%PDF-1.4 vize"
        assert result[0]["content_type"] == "application/pdf"

    def test_filename_without_reference(self, storage):
        storage["record"] = {"id": "f1", "storage_path": "x/y.pdf", "content_type": "application/pdf"}
        assert run(application_docs.visa_pdf_attachment("f1"))[0]["filename"] == "vize.pdf"

    def test_missing_upload_returns_empty(self, storage):
        storage["record"] = None
        assert run(application_docs.visa_pdf_attachment("yok")) == []

    def test_storage_error_returns_empty(self, storage):
        storage["record"] = {"id": "f1", "storage_path": "x/y.pdf", "content_type": "application/pdf"}
        storage["raise"] = True
        assert run(application_docs.visa_pdf_attachment("f1")) == []

    def test_oversized_file_falls_back_to_link(self, storage):
        storage["record"] = {"id": "f1", "storage_path": "x/y.pdf", "content_type": "application/pdf"}
        storage["data"] = b"x" * (application_docs.MAX_TOTAL_BYTES + 1)
        assert run(application_docs.visa_pdf_attachment("f1")) == []

    def test_image_visa_keeps_its_extension(self, storage):
        storage["record"] = {
            "id": "f1",
            "storage_path": "x/y.jpg",
            "original_filename": "visa.JPG",
            "content_type": "image/jpeg",
        }
        assert run(application_docs.visa_pdf_attachment("f1"))[0]["filename"] == "vize.jpg"


class TestVisaWhatsAppText:
    """Ayni GDRFA yonlendirmesi WhatsApp mesajinda da olmali (2026-09-08)."""

    def test_document_caption_has_link_and_steps(self):
        import whatsapp

        text = whatsapp.visa_ready_wa_text({"reference_code": "DV-TEST1234"})
        assert "DV-TEST1234" in text
        assert whatsapp.GDRFA_STATUS_URL in text
        for keyword in ("English", "File Number", "First Name", "bölü işareti"):
            assert keyword in text

    def test_steps_are_numbered_lines(self):
        import whatsapp

        text = whatsapp.gdrfa_check_text()
        for index in range(1, len(whatsapp.GDRFA_STEPS) + 1):
            assert f"\n{index}. " in text or text.startswith(f"{index}. ")

    def test_caption_fits_whatsapp_limit(self):
        import whatsapp

        assert len(whatsapp.visa_ready_wa_text({"reference_code": "DV-TEST1234"})) <= 1024

    def test_no_html_markup_in_whatsapp_text(self):
        import whatsapp

        text = whatsapp.visa_ready_wa_text({"reference_code": "DV-TEST1234"})
        assert "<strong>" not in text and "<li" not in text and "<div" not in text

    def test_email_and_whatsapp_share_the_same_source(self):
        import content
        import whatsapp

        assert whatsapp.GDRFA_STEPS is content.GDRFA_STEPS
        assert emailer.GDRFA_STEPS is content.GDRFA_STEPS
        assert whatsapp.GDRFA_STATUS_URL == emailer.GDRFA_STATUS_URL

    def test_custom_closing_line(self):
        import whatsapp

        text = whatsapp.visa_ready_wa_text({"reference_code": "DV-1"}, "Pasaportunuzu unutmayın.")
        assert text.endswith("Pasaportunuzu unutmayın.")


class TestNotifyResultAppend:
    """Vize sonucu bildiriminde onay mesajina GDRFA yonlendirmesi eklenir."""

    @pytest.fixture
    def wa(self, monkeypatch):
        import whatsapp

        async def fake_settings(masked=True):
            return {
                "enabled": True,
                "only_optin": False,
                "provider": "manual",
                "template_text": whatsapp.DEFAULT_TEMPLATE,
            }

        async def fake_log(*_a, **_k):
            return None

        monkeypatch.setattr(whatsapp, "get_settings", fake_settings)
        monkeypatch.setattr(whatsapp, "_log", fake_log)
        return whatsapp

    def test_approved_message_gets_gdrfa_steps(self, wa):
        app_doc = {
            "reference_code": "DV-TEST1234",
            "contact": {"full_name": "Sedat Andiç", "phone": "05325882630"},
        }
        out = run(wa.notify_result(app_doc, "approved"))
        assert wa.GDRFA_STATUS_URL in out["message"]
        assert "File Number" in out["message"]
        assert "Onaylandı" in out["message"]

    def test_rejected_message_stays_clean(self, wa):
        app_doc = {
            "reference_code": "DV-TEST1234",
            "contact": {"full_name": "Sedat Andiç", "phone": "05325882630"},
        }
        out = run(wa.notify_result(app_doc, "rejected"))
        assert wa.GDRFA_STATUS_URL not in out["message"]
        assert "Reddedildi" in out["message"]
