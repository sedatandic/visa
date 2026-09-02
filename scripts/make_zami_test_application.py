"""Zami canli aktarim testi icin hazir bir ornek basvuru olusturur.

Kullanim:  python /app/scripts/make_zami_test_application.py
Cikti:     olusturulan basvurunun referans kodu ve id'si
"""

import asyncio
import io
import os
import sys

import httpx

BASE = os.environ.get("APP_BASE_URL") or ""
if not BASE:
    with open("/app/frontend/.env", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("REACT_APP_BACKEND_URL"):
                BASE = line.split("=", 1)[1].strip().strip('"')

PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d"
    "4944415478da63f8ffff3f0005fe02fea735b1c40000000049454e44ae426082"
)


async def upload(client: httpx.AsyncClient, doc_type: str, name: str) -> str:
    files = {"file": (name, io.BytesIO(PNG), "image/png")}
    r = await client.post(f"{BASE}/api/uploads", files=files, data={"doc_type": doc_type})
    r.raise_for_status()
    return r.json()["file_id"]


async def main() -> None:
    async with httpx.AsyncClient(timeout=60) as client:
        passport = await upload(client, "passport", "pasaport.png")
        photo = await upload(client, "photo", "vesikalik.png")
        ticket = await upload(client, "ticket", "bilet.png")
        hotel = await upload(client, "hotel", "otel.png")

        payload = {
            "contact": {
                "full_name": "ZAMI TEST KULLANICI",
                "email": "zami.test@vizeatlas.com",
                "phone": "05551234567",
                "city": "Istanbul",
                "whatsapp_optin": False,
            },
            "travelers": [
                {
                    "visa_type_id": "visa_30_single",
                    "traveler_type": "adult",
                    "first_name": "ZAMI",
                    "last_name": "TEST",
                    "birth_date": "1990-08-15",
                    "gender": "male",
                    "passport_no": "U12345678",
                    "passport_expiry": "2032-01-20",
                    "national_id": "11111111111",
                    "birth_country": "TR",
                    "nationality": "TR",
                    "passport_file_id": passport,
                    "photo_file_id": photo,
                }
            ],
            "travel": {
                "arrival_date": "2026-11-10",
                "departure_date": "2026-11-20",
                "purpose": "tourism",
                "flight_no": "TK760",
                "accommodation": "Rove Downtown Dubai",
                "notes": "Zami canli aktarim testi icin olusturulmus ornek kayittir.",
            },
            "addons": {"express": False},
            "store_items": [],
            "extra_documents": {"ticket_file_id": ticket, "hotel_file_id": hotel},
            "kvkk_accepted": True,
        }

        r = await client.post(f"{BASE}/api/applications", json=payload)
        if r.status_code >= 400:
            print("HATA:", r.status_code, r.text[:600])
            sys.exit(1)
        data = r.json()
        print("reference_code:", data.get("reference_code"))
        print("id:", data.get("id"))
        print("total:", data.get("price"), data.get("currency"))


if __name__ == "__main__":
    asyncio.run(main())
