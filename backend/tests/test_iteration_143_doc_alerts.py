"""Iteration 143: pasaport okunamadi alarmi + ayni belge iki yolcuda uyarisi.

Kullanici istekleri:
- "Pasaport okunamayan basvurularda ekibine aninda bildirim dussun, musteriyi hemen arayin"
  -> panel karti + ekip WhatsApp'i + e-posta (kullanici onayi: hepsi).
- "Ayni pasaport ve resim yanlislikla 2. ya da sonraki yolcularda eklenirse uyari verelim"
  -> formda anlik uyari (Apply.jsx), basvuru olusturmada ise kesin ret.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import doc_alerts
import routes_admin
import routes_public


def traveler(passport_no="U1", passport_file_id="f1", photo_file_id="p1"):
    return SimpleNamespace(
        passport_no=passport_no, passport_file_id=passport_file_id, photo_file_id=photo_file_id
    )


class TestAyniBelgeReddi:
    def test_ayni_pasaport_numarasi_reddedilir(self):
        with pytest.raises(HTTPException) as exc:
            routes_public._reject_duplicate_documents(
                [traveler(), traveler(passport_file_id="f2", photo_file_id="p2")]
            )
        assert exc.value.status_code == 400
        assert "1. ve 2. yolcuda ayni pasaport numarasi" in exc.value.detail

    def test_ayni_pasaport_dosyasi_reddedilir(self):
        with pytest.raises(HTTPException) as exc:
            routes_public._reject_duplicate_documents(
                [traveler(), traveler(passport_no="U2", photo_file_id="p2")]
            )
        assert "pasaport fotografi" in exc.value.detail

    def test_ayni_vesikalik_reddedilir(self):
        with pytest.raises(HTTPException) as exc:
            routes_public._reject_duplicate_documents(
                [traveler(), traveler(passport_no="U2", passport_file_id="f2")]
            )
        assert "vesikalik fotografi" in exc.value.detail

    def test_buyuk_kucuk_harf_farki_ayni_sayilir(self):
        with pytest.raises(HTTPException):
            routes_public._reject_duplicate_documents(
                [
                    traveler(passport_no="u12345678"),
                    traveler(passport_no="U12345678", passport_file_id="f2", photo_file_id="p2"),
                ]
            )

    def test_farkli_belgeler_gecerli(self):
        routes_public._reject_duplicate_documents(
            [traveler(), traveler(passport_no="U2", passport_file_id="f2", photo_file_id="p2")]
        )

    def test_bos_alanlar_cakisma_saymaz(self):
        routes_public._reject_duplicate_documents(
            [traveler(passport_no=""), traveler(passport_no="", passport_file_id="f2", photo_file_id="p2")]
        )


class FakeNotifications:
    def __init__(self, existing=None):
        self.docs = list(existing or [])
        self.updates = []

    async def find_one(self, query):
        for doc in self.docs:
            if all(self._match(doc, key, val) for key, val in query.items()):
                return doc
        return None

    @staticmethod
    def _match(doc, key, expected):
        value = doc.get(key)
        if isinstance(expected, dict) and "$gt" in expected:
            return value is not None and value > expected["$gt"]
        return value == expected

    async def insert_one(self, doc):
        self.docs.append(doc)

    async def update_one(self, query, update):
        self.updates.append((query, update))


CONTACT = {"name": "AYŞE YILMAZ", "phone": "+905551112233", "email": "ayse@ornek.com"}


def install(monkeypatch, col, admin_email="ops@dubaivizehatti.com"):
    sent = {}

    async def fake_wa(text, reason="admin_alert"):
        sent["wa"] = {"text": text, "reason": reason}
        return {"status": "manual", "link": "https://wa.me/905551112233?text=..."}

    async def fake_mail(to, subject, html, kind="generic", meta=None, attachments=None):
        sent["mail"] = {"to": to, "subject": subject, "kind": kind, "html": html}
        return {"status": "sent"}

    monkeypatch.setattr(doc_alerts, "notifications_col", col)
    monkeypatch.setattr(doc_alerts.whatsapp, "send_admin_text", fake_wa)
    monkeypatch.setattr(doc_alerts, "send_email", fake_mail)
    monkeypatch.setenv("ADMIN_EMAIL", admin_email)
    return sent


class TestPasaportAlarmi:
    def test_alarm_olusur_ve_kanallar_tetiklenir(self, monkeypatch):
        col = FakeNotifications()
        sent = install(monkeypatch, col)
        out = asyncio.run(doc_alerts.notify_unreadable_passport("file-1", "not_readable", CONTACT))

        assert out["status"] == "created"
        alert = col.docs[0]
        assert alert["kind"] == "passport_unreadable"
        assert alert["read"] is False
        assert alert["file_id"] == "file-1"
        assert alert["reason_label"] == "Goruntuden bilgiler okunamadi"
        assert alert["contact"]["phone"] == "+905551112233"
        assert alert["contact_key"] == "+905551112233"
        assert "AYŞE YILMAZ" in sent["wa"]["text"]
        assert "hemen arayin" in sent["wa"]["text"]
        assert sent["mail"]["to"] == "ops@dubaivizehatti.com"
        assert "Pasaport okunamadı" in sent["mail"]["subject"]
        # kanal sonuclari kayda islenir
        assert col.updates and "whatsapp" in col.updates[0][1]["$set"]

    def test_ayni_dosya_icin_tek_alarm(self, monkeypatch):
        col = FakeNotifications([{"kind": "passport_unreadable", "file_id": "file-1"}])
        install(monkeypatch, col)
        out = asyncio.run(doc_alerts.notify_unreadable_passport("file-1", "ai_error", CONTACT))
        assert out["status"] == "skipped"
        assert len(col.docs) == 1

    def test_ayni_musteri_10_dakika_icinde_tekrar_alarm_almaz(self, monkeypatch):
        col = FakeNotifications(
            [
                {
                    "kind": "passport_unreadable",
                    "file_id": "eski",
                    "contact_key": "+905551112233",
                    "created_at": datetime.now(timezone.utc) - timedelta(minutes=2),
                }
            ]
        )
        install(monkeypatch, col)
        out = asyncio.run(doc_alerts.notify_unreadable_passport("file-2", "ai_error", CONTACT))
        assert out["status"] == "throttled" or out["status"] == "skipped"
        assert len(col.docs) == 1

    def test_eski_alarm_yeni_alarmi_engellemez(self, monkeypatch):
        col = FakeNotifications(
            [
                {
                    "kind": "passport_unreadable",
                    "file_id": "eski",
                    "contact_key": "+905551112233",
                    "created_at": datetime.now(timezone.utc) - timedelta(minutes=45),
                }
            ]
        )
        install(monkeypatch, col)
        out = asyncio.run(doc_alerts.notify_unreadable_passport("file-2", "ai_error", CONTACT))
        assert out["status"] == "created"

    def test_admin_email_yoksa_posta_atlanir(self, monkeypatch):
        col = FakeNotifications()
        install(monkeypatch, col, admin_email="")
        monkeypatch.delenv("ADMIN_EMAIL", raising=False)
        out = asyncio.run(doc_alerts.notify_unreadable_passport("file-3", "ai_error", CONTACT))
        assert out["status"] == "created"
        assert out["email"]["status"] == "skipped"

    def test_iletisim_bilgisi_yoksa_da_alarm_gider(self, monkeypatch):
        col = FakeNotifications()
        sent = install(monkeypatch, col)
        asyncio.run(doc_alerts.notify_unreadable_passport("file-4", "ai_error", {}))
        assert col.docs[0]["contact_key"] == ""
        assert "Isim girilmemis" in sent["wa"]["text"]


class TestAdminUclari:
    def test_alarm_uclari_kayitli_ve_korumali(self):
        paths = {route.path for route in routes_admin.router.routes}
        assert "/admin/alerts" in paths
        assert "/admin/alerts/{alert_id}/read" in paths
        source = open(os.path.join(BACKEND_DIR, "routes_admin.py"), encoding="utf-8").read()
        block = source[source.index('@router.get("/admin/alerts")') :][:1200]
        assert "Depends(require_admin)" in block
