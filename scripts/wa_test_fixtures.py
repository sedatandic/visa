"""WhatsApp AI akisi icin gecici test verisi + belge uretici (elle kullanim)."""

import asyncio
import sys
import uuid
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "/app/backend")

import pymupdf  # noqa: E402

from db import applications_col  # noqa: E402

REFERENCE = "DV-TEST01"
EMAIL = "delivered@resend.dev"


async def seed_application() -> None:
    now = datetime.now(timezone.utc)
    await applications_col.delete_many({"reference_code": REFERENCE})
    await applications_col.insert_one(
        {
            "id": str(uuid.uuid4()),
            "reference_code": REFERENCE,
            "status": "submitted",
            "visa_type_id": "single_30",
            "travelers": [
                {
                    "first_name": "AYSE",
                    "last_name": "YILMAZ",
                    "passport_no": "U12345678",
                    "birth_date": "1994-05-12",
                    "gender": "F",
                    "nationality": "TUR",
                }
            ],
            "contact": {
                "full_name": "AYSE YILMAZ",
                "email": EMAIL,
                "phone": "+90 555 000 11 22",
            },
            "travel_start": (now + timedelta(days=20)).date().isoformat(),
            "travel_end": (now + timedelta(days=30)).date().isoformat(),
            "created_at": now,
            "updated_at": now,
            "status_history": [{"status": "submitted", "at": now}],
            "is_test_fixture": True,
        }
    )
    print(f"test basvurusu olusturuldu: {REFERENCE}")


def build_visa_pdf(path: str, *, reference: str = REFERENCE, name: str = "AYSE YILMAZ") -> None:
    doc = pymupdf.open()
    page = doc.new_page()
    lines = [
        ("UNITED ARAB EMIRATES", 24),
        ("Federal Authority for Identity and Citizenship", 12),
        ("ENTRY PERMIT / eVISA", 16),
        ("", 10),
        (f"Application No: {reference}", 12),
        ("Visa Number: 784202612345678", 12),
        (f"Full Name: {name}", 13),
        ("Nationality: TURKEY", 12),
        ("Passport No: U12345678", 13),
        ("Date of Birth: 12/05/1994", 12),
        ("Visa Type: Tourist - 30 Days Single Entry", 12),
        ("Date of Issue: 06/09/2026", 12),
        ("Date of Expiry: 06/12/2026", 12),
        ("Duration of Stay: 30 Days", 12),
    ]
    y = 70
    for text, size in lines:
        if text:
            page.insert_text((60, y), text, fontsize=size, fontname="helv")
        y += size + 12
    doc.save(path)
    doc.close()
    print(f"test vize pdf uretildi: {path}")


async def cleanup() -> None:
    from db import conversations_col, uploads_col, wa_documents_col

    apps = await applications_col.delete_many({"is_test_fixture": True})
    docs = await wa_documents_col.delete_many({})
    convs = await conversations_col.delete_many({"wa_id": {"$regex": "^9055"}})
    ups = await uploads_col.delete_many({"source": "whatsapp_supplier"})
    print(
        f"temizlendi -> basvuru: {apps.deleted_count}, belge: {docs.deleted_count}, "
        f"konusma: {convs.deleted_count}, dosya: {ups.deleted_count}"
    )


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "seed"
    if command == "seed":
        asyncio.run(seed_application())
        build_visa_pdf("/tmp/test_visa.pdf")
        build_visa_pdf("/tmp/test_visa_unknown.pdf", reference="", name="MEHMET DEMIRCI")
    elif command == "cleanup":
        asyncio.run(cleanup())
