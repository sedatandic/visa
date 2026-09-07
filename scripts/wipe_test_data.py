"""Test verisi temizligi (tam): panelde yalnizca gercek kayit zinciri ve ayarlar kalir.

Korunanlar:
- KEEP_REFS icindeki basvurular + bagli siparis, dosya, e-posta, odeme ve sigorta kayitlari
- Ayar/icerik koleksiyonlari: site_settings, visa_types, store_products, articles, testimonials

Silinenler: diger tum basvuru/siparis/dosya kayitlari, e-posta arsivi, bildirimler,
iletisim mesajlari, taslaklar, kayitli yolcular, giriş kodlari, OCR olcumleri,
Zami loglari, WhatsApp sohbet/olay kayitlari, ziyaretci kayitlari, sepet anlik goruntuleri.

Kullanim:
  python /app/scripts/wipe_test_data.py            # rapor (dry-run)
  python /app/scripts/wipe_test_data.py --apply    # siler
"""
import argparse
import asyncio
import sys

sys.path.insert(0, "/app/backend")

from db import db as database  # noqa: E402

KEEP_REFS = ["DV-BJ930600"]  # gercek musteri kaydi (Sedat Andic)

WIPE_ALL = [
    "notifications",
    "contact_messages",
    "application_drafts",
    "login_codes",
    "admin_login_codes",
    "ocr_metrics",
    "zami_logs",
    "zami_handoffs",
    "wa_conversations",
    "wa_messages",
    "wa_events",
    "wa_documents",
    "whatsapp_logs",
    "visits",
    "ip_geo",
    "cart_snapshots",
    "pre_evaluations",
    "applications",
    "poc_visa_applications",
    "poc_email_outbox",
    "poc_payment_transactions",
]


def file_ids(doc: dict) -> set:
    """Dokumandaki tum dosya kimliklerini toplar."""
    out: set = set()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "other_file_ids" and isinstance(value, list):
                    out.update(v for v in value if isinstance(v, str))
                elif (key.endswith("_file_id") or key == "file_id") and isinstance(value, str):
                    out.add(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(doc)
    return {v for v in out if v}


async def keepers() -> dict:
    apps = [d async for d in database["visa_applications"].find({"reference_code": {"$in": KEEP_REFS}})]
    app_ids = [a["id"] for a in apps]
    emails = [(a.get("contact") or {}).get("email") for a in apps]
    order_ids = [a.get("linked_order_id") for a in apps if a.get("linked_order_id")]
    orders = [d async for d in database["store_orders"].find({"id": {"$in": order_ids}})]
    files: set = set()
    for doc in apps + orders:
        files |= file_ids(doc)
    return {
        "app_ids": app_ids,
        "order_ids": [o["id"] for o in orders],
        "order_refs": [o.get("reference_code") for o in orders if o.get("reference_code")],
        "emails": [e for e in emails if e],
        "files": sorted(files),
    }


async def main(apply: bool) -> None:
    keep = await keepers()
    print("korunan basvuru:", KEEP_REFS, "| siparis:", keep["order_refs"])
    print("korunan dosya  :", len(keep["files"]), "| e-posta adresi:", keep["emails"])

    plan = [
        ("visa_applications", {"reference_code": {"$nin": KEEP_REFS}}),
        ("store_orders", {"id": {"$nin": keep["order_ids"]}}),
        ("uploads", {"id": {"$nin": keep["files"]}}),
        (
            "email_outbox",
            {
                "to": {"$nin": keep["emails"]},
                "meta.reference_code": {"$nin": KEEP_REFS + keep["order_refs"]},
            },
        ),
        (
            "payment_transactions",
            {
                "application_id": {"$nin": keep["app_ids"]},
                "order_id": {"$nin": keep["order_ids"]},
            },
        ),
        ("insurance_tasks", {"order_id": {"$nin": keep["order_ids"]}}),
        ("saved_travelers", {"email": {"$nin": keep["emails"]}}),
    ] + [(name, {}) for name in WIPE_ALL]

    for name, query in plan:
        col = database[name]
        count = await col.count_documents(query)
        if not count:
            continue
        if apply:
            await col.delete_many(query)
        print(f"{'silindi' if apply else 'silinecek'}: {name} -> {count}")

    if not apply:
        print("\n(dry-run) silmek icin: --apply")
        return

    print("\nkalan kayitlar:")
    for name in (
        "visa_applications",
        "store_orders",
        "uploads",
        "email_outbox",
        "notifications",
        "contact_messages",
        "visits",
        "site_settings",
        "visa_types",
        "store_products",
        "articles",
        "testimonials",
    ):
        print(f"  {name:20} {await database[name].count_documents({})}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    asyncio.run(main(parser.parse_args().apply))
