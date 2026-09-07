"""Ek dogrulamalar (iteration 112): 400/404 semantigi, poppler ile PDF dogrulamasi,
ve cok yolcu senaryosunda ek dosya adlari.
"""
import io
import os
import subprocess
import sys
import tempfile
from datetime import date, timedelta

import pytest
import requests
from PIL import Image
from pymongo import MongoClient

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from admin_test_token import admin_token  # noqa: E402

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"
TEST_EMAIL = "delivered@resend.dev"


def _jpeg() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (240, 320), (240, 240, 240)).save(buf, format="JPEG")
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
def multi_app(db):
    """2 yetiskin + 1 cocuk, insurance/eSIM ekli."""
    session = requests.Session()
    uploads = {}
    for label in [
        "p1_pass", "p1_photo",
        "p2_pass", "p2_photo",
        "p3_pass", "p3_photo",
        "ticket", "hotel",
    ]:
        doc_type = "passport" if "pass" in label else ("photo" if "photo" in label else ("ticket" if label == "ticket" else "hotel"))
        uploads[label] = _upload(session, doc_type)
    arrival = date.today() + timedelta(days=40)
    departure = arrival + timedelta(days=14)
    payload = {
        "contact": {
            "full_name": "TEST Multi Family",
            "email": TEST_EMAIL,
            "phone": "+905551110099",
            "address_city": "Ankara",
            "whatsapp_optin": False,
        },
        "travelers": [
            {
                "first_name": "Ayşe", "last_name": "Yılmaz",
                "birth_date": "1985-03-14", "gender": "female",
                "applicant_type": "adult", "nationality": "TR",
                "passport_no": "U11112222", "passport_expiry": "2032-12-31",
                "marital_status": "married", "profession": "Engineer",
                "visa_type_id": "visa_30_single",
                "passport_file_id": uploads["p1_pass"], "photo_file_id": uploads["p1_photo"],
            },
            {
                "first_name": "Mehmet", "last_name": "Yılmaz",
                "birth_date": "1983-07-22", "gender": "male",
                "applicant_type": "adult", "nationality": "TR",
                "passport_no": "U22223333", "passport_expiry": "2032-12-31",
                "marital_status": "married", "profession": "Manager",
                "visa_type_id": "visa_30_single",
                "passport_file_id": uploads["p2_pass"], "photo_file_id": uploads["p2_photo"],
            },
            {
                "first_name": "Zeynep", "last_name": "Yılmaz",
                "birth_date": "2016-01-10", "gender": "female",
                "applicant_type": "child", "nationality": "TR",
                "passport_no": "U33334444", "passport_expiry": "2032-12-31",
                "marital_status": "single", "profession": "Student",
                "visa_type_id": "visa_30_single",
                "passport_file_id": uploads["p3_pass"], "photo_file_id": uploads["p3_photo"],
            },
        ],
        "travel": {
            "arrival_date": arrival.isoformat(),
            "departure_date": departure.isoformat(),
            "purpose": "tourism",
            "birth_country": "TR",
            "accommodation": "Test Hotel",
            "flight_no": "TK456",
        },
        "addons": {"express": False, "insurance": True, "insurance_plus": False, "esim": True},
        "store_items": [],
        "extra_documents": {
            "ticket_file_id": uploads["ticket"],
            "hotel_file_id": uploads["hotel"],
            "other_file_ids": [],
        },
        "kvkk_accepted": True,
    }
    res = session.post(f"{API}/applications", json=payload, timeout=120)
    assert res.status_code == 200, res.text
    created = res.json()
    yield {"data": created, "reference": created["reference_code"], "uploads": uploads}

    db.visa_applications.delete_many({"reference_code": created["reference_code"]})
    db.orders.delete_many({"reference_code": created["reference_code"]})
    db.email_outbox.delete_many({"meta.reference_code": created["reference_code"]})
    db.uploads.delete_many({"id": {"$in": list(uploads.values())}})


@pytest.mark.skipif(not BASE_URL, reason="REACT_APP_BACKEND_URL yok")
class TestPublicPdfEndpointSemantics:
    def test_missing_params_return_400_or_422(self):
        res = requests.get(f"{API}/applications/form.pdf", timeout=30)
        assert res.status_code in (400, 422), res.status_code

    def test_unknown_code_returns_404(self):
        res = requests.get(
            f"{API}/applications/form.pdf",
            params={"code": "DV-DOESNOTEXIST", "last_name": "Test"},
            timeout=30,
        )
        assert res.status_code == 404


@pytest.mark.skipif(not BASE_URL, reason="REACT_APP_BACKEND_URL yok")
class TestMultiTravelerPdfAndAttachments:
    def test_pdf_valid_via_poppler_and_contains_key_data(self, multi_app):
        res = requests.get(
            f"{API}/applications/form.pdf",
            params={"code": multi_app["reference"], "last_name": "Yılmaz"},
            timeout=60,
        )
        assert res.status_code == 200
        assert res.content.startswith(b"%PDF")
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
            fh.write(res.content)
            path = fh.name
        try:
            info = subprocess.run(["pdfinfo", path], capture_output=True, text=True, check=True)
            assert "Pages:" in info.stdout
            # Cok yolcu -> bir veya iki sayfa olabilir; 1'i cok kati bir sart olarak dayatmiyoruz
            txt = subprocess.run(["pdftotext", path, "-"], capture_output=True, text=True, check=True).stdout
            assert multi_app["reference"] in txt
            assert "Yılmaz" in txt
            assert "TOPLAM" in txt
            assert "TL" in txt
        finally:
            os.unlink(path)

    def test_admin_pdf_endpoint_multi(self, multi_app, db):
        doc = db.visa_applications.find_one({"reference_code": multi_app["reference"]})
        url = f"{API}/admin/applications/{doc['id']}/form.pdf"
        assert requests.get(url, timeout=30).status_code == 401
        res = requests.get(url, headers={"Authorization": f"Bearer {admin_token()}"}, timeout=60)
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/pdf"

    def test_customer_email_lists_every_passport_and_photo(self, multi_app, db):
        rec = db.email_outbox.find_one(
            {"meta.reference_code": multi_app["reference"], "kind": "application_received"}
        )
        assert rec, "musteri e-postasi yok"
        names = rec.get("meta", {}).get("attachments") or []
        # form + 3 pasaport + 3 fotograf + bilet + otel = 9
        assert any("Basvuru-Formu" in n for n in names)
        pass_count = sum(1 for n in names if "pasaport" in n)
        photo_count = sum(1 for n in names if "vesikalik-fotograf" in n)
        assert pass_count >= 3, f"pasaport eki eksik: {names}"
        assert photo_count >= 3, f"fotograf eki eksik: {names}"
        assert any("ucak-bileti" in n for n in names)
        assert any("otel" in n for n in names)

    def test_admin_email_has_same_attachments(self, multi_app, db):
        rec = db.email_outbox.find_one(
            {"meta.reference_code": multi_app["reference"], "kind": "admin_new_application"}
        )
        assert rec
        names = rec.get("meta", {}).get("attachments") or []
        assert len(names) >= 9
