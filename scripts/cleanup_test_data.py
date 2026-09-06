"""Test verisi temizligi: yonetici panelini gercek kayitlarla bas basa birakir.

Test kaydi olcutu: iletisim e-postasi example.com / resend.dev / @test. uzantili
ya da ad-soyad "TEST" ile baslayan basvurular ve siparisler. Bagli kayitlar
(yuklenen dosyalar, odeme kayitlari, bildirimler, sigorta isleri, e-posta
arsivi, taslaklar, kayitli yolcular, Zami/OCR kayitlari) da temizlenir.
Otomasyon trafigi (HeadlessChrome, requests, curl) ziyaretci istatistiginden
dusulur.

Kullanim:
  python /app/scripts/cleanup_test_data.py            # sadece rapor (dry-run)
  python /app/scripts/cleanup_test_data.py --apply    # siler
"""
import argparse
import asyncio
import sys

sys.path.insert(0, "/app/backend")

from db import (  # noqa: E402
    applications_col,
    contact_col,
    db,
    drafts_col,
    email_outbox_col,
    insurance_tasks_col,
    login_codes_col,
    notifications_col,
    orders_col,
    payments_col,
    saved_travelers_col,
    uploads_col,
    visits_col,
    zami_logs_col,
)

TEST_MAIL = {"$regex": "example\\.com|resend\\.dev|@test\\.", "$options": "i"}
TEST_NAME = {"$regex": "^\\s*TEST", "$options": "i"}
BOT_UA = {"$regex": "HeadlessChrome|python-requests|curl/|Playwright|axios/", "$options": "i"}

APP_QUERY = {
    "$or": [
        {"contact.email": TEST_MAIL},
        {"contact.full_name": TEST_NAME},
        {"travelers.first_name": TEST_NAME},
        {"travelers.last_name": TEST_NAME},
    ]
}
ORDER_QUERY = {
    "$or": [
        {"customer.email": TEST_MAIL},
        {"contact.email": TEST_MAIL},
        {"customer.full_name": TEST_NAME},
    ]
}


def file_ids(app: dict) -> set:
    """Basvurudaki tum dosya kimliklerini toplar."""
    out = set()

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

    walk(app)
    return {v for v in out if v}


async def collect() -> dict:
    apps = [d async for d in applications_col.find(APP_QUERY)]
    orders = [d async for d in orders_col.find(ORDER_QUERY)]
    files, refs, emails = set(), set(), set()
    for app in apps:
        files |= file_ids(app)
        refs.add(app.get("reference_code"))
        emails.add((app.get("contact") or {}).get("email"))
    for order in orders:
        files |= file_ids(order)
        refs.add(order.get("reference"))
        emails.add((order.get("customer") or {}).get("email"))
    return {
        "app_ids": [d["id"] for d in apps if d.get("id")],
        "order_ids": [d["id"] for d in orders if d.get("id")],
        "refs": [r for r in refs if r],
        "emails": [e for e in emails if e],
        "files": sorted(files),
        "apps": len(apps),
        "orders": len(orders),
    }


async def orphan_upload_ids() -> list:
    """Hicbir basvuru / siparis / taslak tarafindan kullanilmayan dosyalar."""
    keep = set()
    for col in (applications_col, orders_col, drafts_col):
        async for doc in col.find({}):
            keep |= file_ids(doc)
    return [d["id"] async for d in uploads_col.find({"id": {"$nin": list(keep)}}, {"id": 1})]


async def main(apply: bool) -> None:
    data = await collect()
    total_apps = await applications_col.count_documents({})
    total_orders = await orders_col.count_documents({})
    print(f"basvurular : {data['apps']} test / {total_apps} toplam")
    print(f"siparisler : {data['orders']} test / {total_orders} toplam")
    print(f"dosyalar   : {len(data['files'])}")
    print(f"e-postalar : {len(data['emails'])}")

    plan = [
        (applications_col, APP_QUERY),
        (orders_col, ORDER_QUERY),
        (uploads_col, {"id": {"$in": data["files"]}}),
        (payments_col, {"$or": [
            {"application_id": {"$in": data["app_ids"]}},
            {"order_id": {"$in": data["order_ids"]}},
            {"reference_code": {"$in": data["refs"]}},
            {"metadata.reference": {"$in": data["refs"]}},
        ]}),
        (notifications_col, {"$or": [
            {"application_id": {"$in": data["app_ids"]}},
            {"order_id": {"$in": data["order_ids"]}},
            {"email": TEST_MAIL},
        ]}),
        (insurance_tasks_col, {"$or": [
            {"order_id": {"$in": data["order_ids"]}},
            {"customer.email": TEST_MAIL},
        ]}),
        (email_outbox_col, {"to": TEST_MAIL}),
        (contact_col, {"email": TEST_MAIL}),
        (drafts_col, {"$or": [{"email": TEST_MAIL}, {"contact.email": TEST_MAIL}]}),
        (saved_travelers_col, {"email": TEST_MAIL}),
        (login_codes_col, {"email": TEST_MAIL}),
        (zami_logs_col, {"application_id": {"$in": data["app_ids"]}}),
        (db["ocr_metrics"], {"file_id": {"$in": data["files"]}}),
        (db["whatsapp_logs"], {"$or": [{"application_id": {"$in": data["app_ids"]}}, {"to": TEST_MAIL}]}),
        (visits_col, {"$or": [{"user_agent": BOT_UA}, {"bot": True}]}),
    ]

    for col, query in plan:
        n = await col.count_documents(query)
        if not n:
            continue
        if apply:
            await col.delete_many(query)
        print(f"{'silindi' if apply else 'silinecek'}: {col.name} -> {n}")

    orphans = await orphan_upload_ids()
    if orphans:
        if apply:
            await uploads_col.delete_many({"id": {"$in": orphans}})
            await db["ocr_metrics"].delete_many({"file_id": {"$in": orphans}})
        print(f"{'silindi' if apply else 'silinecek'}: sahipsiz dosya -> {len(orphans)}")

    if apply:
        print("\nkalan kayitlar:")
        print("  basvurular:", await applications_col.count_documents({}))
        print("  siparisler:", await orders_col.count_documents({}))
        print("  dosyalar  :", await uploads_col.count_documents({}))
        print("  ziyaretler:", await visits_col.count_documents({}))
    else:
        print("\n(dry-run) silmek icin: --apply")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    asyncio.run(main(ap.parse_args().apply))
