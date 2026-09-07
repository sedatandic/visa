"""Basvuru formu PDF'i + e-posta ekleri (iteration 112).

- POST /api/applications -> musteriye giden e-postaya form PDF'i ve evraklar eklenir
- GET /api/applications/form.pdf (takip kodu + soyad) tek sayfalik formu indirir
- GET /api/admin/applications/{id}/form.pdf yonetici indirmesi (jeton zorunlu)
"""
import io
import os
import sys
from datetime import date, timedelta

import pytest
import requests
from PIL import Image
from pymongo import MongoClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from admin_test_token import admin_token  # noqa: E402
from application_docs import _slug, document_listing  # noqa: E402
from application_pdf import build_application_pdf, money  # noqa: E402

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"
TEST_EMAIL = "delivered@resend.dev"


def _jpeg() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (240, 320), (250, 250, 250)).save(buf, format="JPEG")
    return buf.getvalue()


def _upload(session, doc_type: str) -> str:
    res = session.post(
        f"{API}/uploads",
        files={"file": (f"{doc_type}.jpg", _jpeg(), "image/jpeg")},
        data={"doc_type": doc_type},
        timeout=60,
    )
    assert res.status_code == 200, res.text
    return res.json()["file_id"]


@pytest.fixture(scope="module")
def db():
    client = MongoClient(os.environ["MONGO_URL"])
    yield client[os.environ["DB_NAME"]]
    client.close()


@pytest.fixture(scope="module")
def application(db):
    """Gercek bir basvuru olusturur; test sonunda tum izlerini siler."""
    session = requests.Session()
    passport_id = _upload(session, "passport")
    photo_id = _upload(session, "photo")
    ticket_id = _upload(session, "ticket")
    arrival = date.today() + timedelta(days=30)
    departure = arrival + timedelta(days=9)
    payload = {
        "contact": {
            "full_name": "TEST Form Kullanici",
            "email": TEST_EMAIL,
            "phone": "+905551110022",
            "address_city": "İstanbul",
            "whatsapp_optin": False,
        },
        "travelers": [
            {
                "first_name": "Şükrü",
                "last_name": "Çağlayan",
                "birth_date": "1990-05-10",
                "gender": "male",
                "applicant_type": "adult",
                "nationality": "TR",
                "passport_no": "U12345678",
                "passport_expiry": "2032-12-31",
                "marital_status": "single",
                "profession": "Employee",
                "visa_type_id": "visa_30_single",
                "passport_file_id": passport_id,
                "photo_file_id": photo_id,
            }
        ],
        "travel": {
            "arrival_date": arrival.isoformat(),
            "departure_date": departure.isoformat(),
            "purpose": "tourism",
            "birth_country": "TR",
            "accommodation": "Test Hotel",
            "flight_no": "TK123",
        },
        "addons": {"express": False, "insurance": False, "insurance_plus": False, "esim": False},
        "store_items": [],
        "extra_documents": {"ticket_file_id": ticket_id, "hotel_file_id": None, "other_file_ids": []},
        "kvkk_accepted": True,
    }
    res = session.post(f"{API}/applications", json=payload, timeout=90)
    assert res.status_code == 200, res.text
    created = res.json()
    yield {"session": session, "data": created, "reference": created["reference_code"]}

    db.visa_applications.delete_many({"reference_code": created["reference_code"]})
    db.email_outbox.delete_many({"meta.reference_code": created["reference_code"]})
    db.uploads.delete_many({"id": {"$in": [passport_id, photo_id, ticket_id]}})


class TestFormHelpers:
    def test_slug_transliterates_turkish(self) -> None:
        assert _slug("Şükrü Çağlayan - vesikalık fotoğraf") == "sukru-caglayan-vesikalik-fotograf"

    def test_money_avoids_missing_lira_glyph(self) -> None:
        assert money(5190, "TRY") == "5.190,00 TL"

    def test_document_listing_drops_bytes(self) -> None:
        items = [
            {"label": "A", "filename": "a.jpg", "url": "u", "data": b"x"},
            {"label": "B", "filename": "b.jpg", "url": "v", "data": None},
        ]
        listing = document_listing(items)
        assert [d["attached"] for d in listing] == [True, False]
        assert all("data" not in d for d in listing)

    def test_pdf_is_single_page_and_titled(self) -> None:
        doc = {
            "reference_code": "DV-TEST01",
            "contact": {"full_name": "Şükrü Çağlayan", "email": "a@b.c", "phone": "+905550001122"},
            "travelers": [
                {
                    "first_name": "Şükrü",
                    "last_name": "Çağlayan",
                    "birth_date": "1990-05-10",
                    "passport_no": "U12345678",
                    "passport_expiry": "2032-12-31",
                    "visa_short_name": "30 Gün Tek Giriş",
                    "price": 5190,
                    "currency": "TRY",
                }
            ],
            "travel": {"arrival_date": "2026-12-01", "departure_date": "2026-12-10"},
            "pricing": {"subtotal": 5190, "total": 5190, "currency": "TRY"},
            "payment": {"status": "pending"},
            "processing_days": "ortalama 2 iş günü",
        }
        pdf = build_application_pdf(doc, [{"label": "Pasaport", "attached": True}])
        assert pdf.startswith(b"%PDF")
        assert len(pdf) > 5000
        assert pdf.count(b"/Type /Page\n") <= 1


@pytest.mark.skipif(not BASE_URL, reason="REACT_APP_BACKEND_URL yok")
class TestApplicationFormEndpoints:
    def test_customer_download_with_code_and_lastname(self, application) -> None:
        res = requests.get(
            f"{API}/applications/form.pdf",
            params={"code": application["reference"], "last_name": "Çağlayan"},
            timeout=60,
        )
        assert res.status_code == 200, res.text
        assert res.headers["content-type"] == "application/pdf"
        assert res.content.startswith(b"%PDF")
        assert application["reference"] in res.headers.get("content-disposition", "")

    def test_wrong_lastname_rejected(self, application) -> None:
        res = requests.get(
            f"{API}/applications/form.pdf",
            params={"code": application["reference"], "last_name": "YANLIS"},
            timeout=30,
        )
        assert res.status_code == 404

    def test_admin_download_requires_token(self, application, db) -> None:
        doc = db.visa_applications.find_one({"reference_code": application["reference"]})
        url = f"{API}/admin/applications/{doc['id']}/form.pdf"
        assert requests.get(url, timeout=30).status_code == 401
        res = requests.get(url, headers={"Authorization": f"Bearer {admin_token()}"}, timeout=60)
        assert res.status_code == 200
        assert res.content.startswith(b"%PDF")

    def test_emails_carry_form_and_documents(self, application, db) -> None:
        record = db.email_outbox.find_one(
            {"meta.reference_code": application["reference"], "kind": "application_received"}
        )
        assert record, "musteriye basvuru alindi e-postasi kaydedilmedi"
        names = record.get("meta", {}).get("attachments") or []
        assert f"Basvuru-Formu-{application['reference']}.pdf" in names
        assert any("pasaport" in n for n in names)
        assert any("vesikalik-fotograf" in n for n in names)
        assert any("ucak-bileti" in n for n in names)
        assert "Ekteki belgeler" in record.get("html", "")

    def test_admin_copy_also_has_attachments(self, application, db) -> None:
        record = db.email_outbox.find_one(
            {"meta.reference_code": application["reference"], "kind": "admin_new_application"}
        )
        assert record, "yonetici bildirimi kaydedilmedi"
        assert len(record.get("meta", {}).get("attachments") or []) >= 4
