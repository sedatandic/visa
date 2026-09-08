"""Guvenlik denetimi (2026-09-08) duzeltmelerinin regresyon testleri.

Kapsam:
- SEC-001: kimliksiz e-posta bombardimani (POST /api/drafts) — otomatik kayitlar posta
  tetiklemez, alici basina saatte en fazla 3 posta; basvuru/siparis uclarinda e-posta
  basina saatlik ust sinir.
- SEC-002: musteri metninin ReportLab markup'ina enjekte edilmesi (PDF).
- Sertlestirme: guvenlik basliklari, /docs kapali, yuklemede dosya imzasi (magic byte).
"""

import io
import os
import sys
import uuid

import pytest
import requests
from dotenv import load_dotenv

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
load_dotenv(os.path.join(HERE, "..", ".env"))
load_dotenv(os.path.join(HERE, "..", "..", "frontend", ".env"))

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
API = f"{BASE_URL}/api"

REAL_JPEG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00" + b"\x08" * 64 + b"\xff\xd9"
)


def _test_email() -> str:
    return f"TEST_sec_{uuid.uuid4().hex[:8]}@example.com"


class TestDraftMailAbuse:
    """SEC-001: taslak kaydi kimliksiz ve sinirsiz posta gonderemez."""

    def test_auto_save_does_not_send_mail_and_recipient_cap_applies(self):
        email = _test_email()
        first = requests.post(
            f"{API}/drafts", json={"email": email, "data": {"step": 1}, "step": 1}, timeout=30
        )
        assert first.status_code == 200, first.text
        created = first.json()
        # Ilk kayit posta dener (test adresinde saglayici hata dondurebilir, "skipped" olmaz)
        assert created["email_status"] != "skipped"

        body = {
            "email": email,
            "data": {"step": 2},
            "step": 2,
            "draft_id": created["draft_id"],
            "resume_code": created["resume_code"],
        }
        auto = requests.post(f"{API}/drafts", json=body, timeout=30)
        assert auto.status_code == 200, auto.text
        # Otomatik kayit (notify yok) posta gondermez
        assert auto.json()["email_status"] == "skipped"

        # Elle kaydet (notify=true): alici basina saatte 3 posta siniri
        statuses = [
            requests.post(f"{API}/drafts", json={**body, "notify": True}, timeout=30)
            .json()["email_status"]
            for _ in range(4)
        ]
        assert statuses[-1] == "skipped", statuses
        assert statuses.count("skipped") >= 2, statuses


class TestUploadSignature:
    """Yuklemede uzanti degil dosya icerigi belirleyici."""

    def test_fake_jpeg_rejected(self):
        files = {"file": ("passport.jpg", io.BytesIO(b"bu bir jpeg degil"), "image/jpeg")}
        r = requests.post(
            f"{API}/uploads", files=files, data={"doc_type": "passport"}, timeout=30
        )
        assert r.status_code == 400, r.text
        assert "icerigi taninamadi" in r.json()["detail"]

    def test_real_jpeg_accepted(self):
        files = {"file": ("passport.jpg", io.BytesIO(REAL_JPEG), "image/jpeg")}
        r = requests.post(
            f"{API}/uploads", files=files, data={"doc_type": "passport"}, timeout=30
        )
        assert r.status_code == 200, r.text
        assert r.json()["file_id"]


class TestHardening:
    def test_security_headers_present(self):
        r = requests.get(f"{API}/health", timeout=30)
        assert r.status_code == 200
        headers = {k.lower(): v for k, v in r.headers.items()}
        assert headers.get("x-content-type-options") == "nosniff"
        assert headers.get("x-frame-options") == "SAMEORIGIN"
        assert "strict-origin" in headers.get("referrer-policy", "")
        assert "max-age" in headers.get("strict-transport-security", "")

    @pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
    def test_api_schema_not_public(self, path):
        # Ingress /api disini frontend'e yonlendirdigi icin uygulama koku uzerinden bakilir
        r = requests.get(f"{API}{path}", timeout=30)
        assert r.status_code == 404, f"{path} -> {r.status_code}"


class TestPdfMarkupInjection:
    """SEC-002: musteri metni PDF markup'i olarak yorumlanmaz."""

    def test_user_markup_is_escaped(self):
        from application_pdf import _safe, build_application_pdf

        evil = '<img src="http://127.0.0.1:8001/api/health"/><b>x</b>'
        assert "<img" not in _safe(evil)
        assert "&lt;img" in _safe(evil)

        doc = {
            "reference_code": "DVH-TEST-SEC",
            "created_at": "2026-09-08T10:00:00+00:00",
            "processing_days": "ortalama 2 iş günü",
            "payment": {"status": "paid"},
            "contact": {"full_name": evil, "email": "a@b.com", "phone": "+905337438224"},
            "travel": {"arrival_date": "2026-10-12", "departure_date": "2026-10-20", "notes": evil},
            "travelers": [
                {
                    "first_name": evil,
                    "last_name": "SOYAD",
                    "passport_no": evil,
                    "birth_date": "1988-04-11",
                    "visa_type_name": evil,
                    "applicant_type": "adult",
                    "price": 5190,
                    "currency": "TRY",
                }
            ],
            "pricing": {"currency": "TRY", "total": 5190, "visa_total": 5190},
        }
        pdf = build_application_pdf(doc, [{"label": evil, "attached": True}])
        assert pdf.startswith(b"%PDF"), "PDF uretilemedi"
        assert len(pdf) > 10_000
