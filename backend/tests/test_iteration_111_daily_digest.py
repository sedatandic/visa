"""Iteration 111: Gunluk yonetici ozeti (daily_digest).

Kapsam:
- day_bounds / day_label yerel gun sinirlari (Europe/Istanbul)
- collect_digest: dun gelen basvurular, tahsilat kirilimi, ekstra satislar, ay basi toplami
- send_daily_digest: ayni gun icin ikinci gonderimi engeller (force haric)
- daily_digest_html: bolum basliklari ve tutarlar render edilir
"""

import os
import uuid
from datetime import date, timedelta, timezone

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import daily_digest  # noqa: E402
from emailer import daily_digest_html  # noqa: E402

TAG = f"digest_{uuid.uuid4().hex[:8]}"


def _db():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    return client, client[os.environ["DB_NAME"]]


def _run(coro):
    import asyncio

    return asyncio.run(coro)


def test_day_bounds_covers_local_day() -> None:
    start, end = daily_digest.day_bounds(date(2026, 6, 8))
    assert (end - start) == timedelta(days=1)
    # Istanbul UTC+3 -> yerel gun UTC 21:00'de baslar
    assert start.astimezone(timezone.utc).hour == 21
    assert daily_digest.day_label(date(2026, 6, 8)) == "8 Haziran 2026, Pazartesi"


def test_collect_digest_counts_seeded_day() -> None:
    day = date.today() - timedelta(days=3)
    start, _ = daily_digest.day_bounds(day)
    created = start + timedelta(hours=10)

    async def go():
        client, db = _db()
        app_doc = {
            "id": f"{TAG}-app",
            "reference_code": f"DV-{TAG[:8].upper()}",
            "status": "submitted",
            "created_at": created,
            "contact": {"full_name": "Digest Tester", "email": "delivered@resend.dev"},
            "visa_type_name": "30 Günlük Tek Girişli Dubai Vizesi",
            "travelers": [
                {"visa_short_name": "30 gün tek girişli", "applicant_type": "adult"},
                {"visa_short_name": "30 gün çocuk", "applicant_type": "child"},
            ],
            "pricing": {"total": 7660.0, "store_items": []},
            "payment": {"status": "paid", "method": "card", "paid_at": created, "amount": 7660.0},
        }
        order_doc = {
            "id": f"{TAG}-order",
            "reference_code": f"SV-{TAG[:8].upper()}",
            "source": "store",
            "created_at": created,
            "items": [
                {"product_id": "esim_3gb", "kind": "esim", "quantity": 2, "total": 1480.0},
                {"product_id": "ins_15d", "kind": "insurance", "quantity": 1, "total": 560.0},
            ],
            "price": 2040.0,
            "currency": "TRY",
            "payment": {"status": "paid", "method": "bank_transfer", "paid_at": created},
        }
        await db.visa_applications.insert_one(dict(app_doc))
        await db.store_orders.insert_one(dict(order_doc))
        try:
            return await daily_digest.collect_digest(day)
        finally:
            await db.visa_applications.delete_many({"id": f"{TAG}-app"})
            await db.store_orders.delete_many({"id": f"{TAG}-order"})
            client.close()

    data = _run(go())
    assert data["day"] == day.isoformat()
    assert data["has_activity"] is True
    assert data["applications"]["count"] >= 1
    assert data["applications"]["travelers"] >= 2
    refs = [r["reference"] for r in data["applications"]["rows"]]
    assert f"DV-{TAG[:8].upper()}" in refs
    # tahsilat: 7660 (kart) + 2040 (havale)
    assert data["revenue"]["total"] >= 9700.0
    methods = {m["label"] for m in data["revenue"]["by_method"]}
    assert {"Kart", "Havale/EFT"}.issubset(methods)
    extras = {e["kind"]: e for e in data["extras"]}
    assert extras["esim"]["quantity"] >= 2
    assert extras["insurance"]["amount"] >= 560.0
    assert data["month"]["revenue"] >= 9700.0
    assert data["attention"]["missing_documents"]["count"] >= 0


def test_send_daily_digest_is_once_per_day() -> None:
    day = date.today() - timedelta(days=2)

    async def go():
        client, db = _db()
        settings = await db.site_settings.find_one({"key": daily_digest.SETTINGS_KEY})
        original = (settings or {}).get("value") or {}
        sent_mails = []

        async def fake_send(to, subject, html, kind="generic", meta=None):
            sent_mails.append({"to": to, "subject": subject, "kind": kind, "html": html})
            return {"status": "sent"}

        real_send = daily_digest.send_email
        daily_digest.send_email = fake_send
        # Gercek gonderim kaydiyla cakismasin (gun secimi rastgele tutuyor): isaretci sifirlanir.
        await db.site_settings.update_one(
            {"key": daily_digest.SETTINGS_KEY}, {"$set": {"value": {}}}, upsert=True
        )
        try:
            first = await daily_digest.send_daily_digest(day)
            second = await daily_digest.send_daily_digest(day)
            forced = await daily_digest.send_daily_digest(day, force=True)
            return first, second, forced, sent_mails
        finally:
            daily_digest.send_email = real_send
            await db.site_settings.update_one(
                {"key": daily_digest.SETTINGS_KEY}, {"$set": {"value": original}}, upsert=True
            )
            client.close()

    first, second, forced, mails = _run(go())
    assert first["sent"] is True
    assert second["sent"] is False and second["reason"] == "already_sent"
    assert forced["sent"] is True
    assert len(mails) == 2
    assert mails[0]["kind"] == "daily_digest"
    assert mails[0]["to"] == os.environ["ADMIN_EMAIL"]
    assert "Günlük özet" in mails[0]["subject"]


def test_digest_html_has_all_sections() -> None:
    data = {
        "day": "2026-06-08",
        "day_label": "8 Haziran 2026, Pazartesi",
        "applications": {
            "count": 2,
            "travelers": 3,
            "amount": 12000.0,
            "by_visa": [{"label": "30 gün tek girişli", "count": 3}],
            "rows": [
                {
                    "reference": "DV-TEST0001",
                    "name": "Ali Veli",
                    "visa": "30 Günlük Tek Girişli",
                    "travelers": 2,
                    "total": 10380.0,
                    "payment_status": "paid",
                }
            ],
        },
        "orders": {"count": 1, "amount": 2040.0},
        "revenue": {"total": 12420.0, "count": 2, "by_method": [{"label": "Kart", "count": 2, "amount": 12420.0}]},
        "extras": [{"kind": "esim", "label": "Dubai eSIM", "quantity": 2, "amount": 1480.0}],
        "attention": {
            "missing_documents": {"count": 4, "references": ["DV-1"]},
            "awaiting_transfer": {"count": 2, "amount": 5000.0},
            "abandoned_carts": {"count": 1, "amount": 740.0},
        },
        "month": {"label": "Haziran 2026", "applications": 12, "revenue": 84000.0},
        "has_activity": True,
        "admin_url": "https://example.com/admin",
    }
    html = daily_digest_html(data)
    for needle in (
        "Günlük özet",
        "Dün gelen başvurular",
        "Tahsilat",
        "Ekstra satışlar",
        "Dikkat gerektirenler",
        "Ay başından bugüne",
        "DV-TEST0001",
        "Yönetim paneline git",
    ):
        assert needle in html, needle
    assert "12.420,00 ₺" in html


def test_digest_html_no_activity_variant() -> None:
    html = daily_digest_html(
        {
            "day_label": "8 Haziran 2026, Pazartesi",
            "applications": {"count": 0, "travelers": 0, "amount": 0, "by_visa": [], "rows": []},
            "revenue": {"total": 0, "count": 0, "by_method": []},
            "extras": [],
            "attention": {},
            "month": {"label": "Haziran 2026", "applications": 0, "revenue": 0},
            "has_activity": False,
        }
    )
    assert "Dün hareket yok" in html
    assert "Kayıt yok." in html


def test_digest_loop_settings_key_and_hour() -> None:
    assert daily_digest.SEND_HOUR == 8
    assert daily_digest.SETTINGS_KEY == "daily_digest"
    assert str(daily_digest.TZ) == "Europe/Istanbul"
