"""Magaza urun katalogu (eSIM / sigorta / tur) ve fiyat listesi.

`routes_store` ile `insurance_tasks` her ikisi de urun listesine ihtiyac duyuyordu ve
birbirini import ediyordu (dairesel bagimlilik). Katalog burada tek yerde durur; iki
modul de buradan import eder.
"""

from datetime import date
from typing import Optional

from fastapi import HTTPException

from db import products_col, serialize_doc
from fx import get_fx, try_price

# Bir siparis satirinda izin verilen en yuksek adet.
MAX_QTY = 10


ESIM_PRODUCTS = [
    {
        "id": "esim_1gb",
        "kind": "esim",
        "name": "Dubai eSIM · 1 GB / 7 gün",
        "summary": "Kısa mola ve aktarmalarda harita, çağrı uygulamaları ve sosyal medya için yeterli veri.",
        "price_usd": 9.0,
        "data_amount": "1 GB",
        "validity_days": 7,
        "features": [
            "BAE genelinde 4G/5G kapsama",
            "QR kod ile 2 dakikada kurulum",
            "Numaranız açık kalır, WhatsApp çalışır",
            "Fiziksel SIM değiştirmeye gerek yok",
        ],
        "order": 1,
        "popular": False,
    },
    {
        "id": "esim_3gb",
        "kind": "esim",
        "name": "Dubai eSIM · 3 GB / 15 gün",
        "summary": "Bir haftalık tatilde navigasyon, sosyal medya ve video görüşme için en çok tercih edilen paket.",
        "price_usd": 15.0,
        "data_amount": "3 GB",
        "validity_days": 15,
        "features": [
            "BAE genelinde 4G/5G kapsama",
            "QR kod ile anında kurulum",
            "Hotspot (internet paylaşımı) açık",
            "Uygulama içi veri takibi",
        ],
        "order": 2,
        "popular": True,
    },
    {
        "id": "esim_10gb",
        "kind": "esim",
        "name": "Dubai eSIM · 10 GB / 30 gün",
        "summary": "Uzun kalışlar ve iş seyahatleri için bol veri; toplantı ve video görüşmelerinde rahat kullanım.",
        "price_usd": 29.0,
        "data_amount": "10 GB",
        "validity_days": 30,
        "features": [
            "30 gün geçerli bol veri",
            "Hotspot açık, dizüstü bilgisayara bağlanır",
            "Video görüşme ve bulut yedekleme için uygun",
            "Kurulum desteği dahil",
        ],
        "order": 3,
        "popular": False,
    },
    {
        "id": "esim_unlimited",
        "kind": "esim",
        "name": "Dubai eSIM · Sınırsız / 30 gün",
        "summary": "Veri limiti düşünmeden kullanmak isteyenler için adil kullanım kotalı sınırsız paket.",
        "price_usd": 49.0,
        "data_amount": "Sınırsız",
        "validity_days": 30,
        "features": [
            "Adil kullanım sonrası hız düşer, kesilmez",
            "Yayın (streaming) ve harita kullanımı serbest",
            "Hotspot açık",
            "Öncelikli destek",
        ],
        "order": 4,
        "popular": False,
    },
]

# Seyahat sagligi policeleri: maliyet Tamamliyo Travel API'sinden (urun_id 141,
# "Yurt Disi Saglik Destek Paketi") gunluk cekilir; satis fiyati %100 marj ile TL olarak
# hesaplanir (`insurance_provider.sync_prices`). Buradaki degerler ilk kurulum/yedek tarifedir.
INSURANCE_MARKUP = 2.0

_BASIC_FEATURES = [
    "30.000 € acil sağlık teminatı",
    "Vize başvurusu için geçerli, BAE dahil tüm dünya",
    "Tıbbi tedavi, tıbbi nakil ve cenaze nakli teminatı",
    "Sınırsız tıbbi bilgi ve danışma hattı",
    "Poliçe PDF olarak e-postanıza gelir",
]


def _insurance(pid, days, base_try, popular=False, order=1):
    return {
        "id": pid,
        "kind": "insurance",
        "name": f"Seyahat Sağlık Sigortası · {days} Gün",
        "summary": (
            f"{days} güne kadar BAE seyahatlerinde acil sağlık masraflarını karşılayan, "
            "vize başvurusuna uygun poliçe."
        ),
        "price_try": round(base_try * INSURANCE_MARKUP / 10) * 10,
        "cost_try": round(base_try, 2),
        "coverage": "30.000 € teminat",
        "validity_days": days,
        "features": _BASIC_FEATURES,
        "provider": "tamamliyo",
        "provider_urun_id": 141,
        "needs_tckn": True,
        "order": order,
        "popular": popular,
    }


INSURANCE_PRODUCTS = [
    _insurance("ins_7d", 7, 196.44, order=1),
    _insurance("ins_15d", 15, 224.02, popular=True, order=2),
    _insurance("ins_30d", 30, 257.23, order=3),
    _insurance("ins_60d", 60, 367.55, order=4),
]

# Dubai aktiviteleri: teslimat/rezervasyon acente eliyle yapilir
TOUR_PRODUCTS = [
    {
        "id": "tour_desert_safari",
        "kind": "tour",
        "name": "Çöl Safarisi · Akşam Turu",
        "summary": "4x4 araçlarla kumul turu, deve gezisi, kum sörfü ve geleneksel Arap kampında açık büfe akşam yemeği.",
        "price_usd": 45.0,
        "image_url": "https://images.unsplash.com/photo-1763535539149-53eddcfa20dd?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
        "needs_schedule": True,
        "time_slots": ["14:00", "14:30", "15:00", "15:30", "16:00"],
        "features": [
            "Otelinizden alış ve dönüş dahil",
            "Kum sörfü, deve gezisi ve gün batımı molası",
            "Geleneksel kampta açık büfe akşam yemeği",
            "Türkçe konuşan rehber eşliğinde",
            "Yaklaşık 7 saat sürer, öğleden sonra başlar",
        ],
        "order": 1,
        "popular": True,
    },
    {
        "id": "tour_desert_safari_vip",
        "kind": "tour",
        "name": "Çöl Safarisi · VIP Akşam Turu",
        "summary": "Özel araçta kumul turu, quad bike denemesi, VIP kamp masası ve ateş başında canlı gösteriler.",
        "price_usd": 55.0,
        "image_url": "https://images.unsplash.com/photo-1631730690491-d2efef90fc21?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
        "needs_schedule": True,
        "time_slots": ["14:00", "14:30", "15:00", "15:30", "16:00"],
        "features": [
            "Otelinizden özel araçla alış ve dönüş",
            "Quad bike denemesi ve kum sörfü dahil",
            "VIP kamp masası, sınırsız içecek ikramı",
            "Ateş gösterisi, tanura ve canlı müzik",
            "Türkçe konuşan rehber · yaklaşık 7 saat",
        ],
        "order": 2,
        "popular": False,
    },
]

DEFAULT_PRODUCTS = ESIM_PRODUCTS + INSURANCE_PRODUCTS + TOUR_PRODUCTS

KIND_LABELS = {"esim": "eSIM", "insurance": "Seyahat sigortası", "tour": "Dubai turu"}


async def product_list(kind: Optional[str] = None, include_inactive: bool = False) -> list:
    query = {}
    if kind:
        query["kind"] = kind
    if not include_inactive:
        query["active"] = True
    docs = await products_col.find(query).sort("order", 1).to_list(100)
    if not docs:
        docs = [
            p for p in DEFAULT_PRODUCTS if (not kind or p["kind"] == kind)
        ]
    rate = (await get_fx())["effective_rate"]
    items = []
    for doc in serialize_doc(docs):
        item = dict(doc)
        item.pop("_id", None)
        if item.get("price_try"):
            item["price"] = round(float(item["price_try"]), 2)
        elif item.get("price_usd"):
            item["price"] = try_price(item["price_usd"], rate)
        item["currency"] = "TRY"
        item["fx_rate"] = rate
        item["kind_label"] = KIND_LABELS.get(item.get("kind"), "")
        items.append(item)
    return items

def tour_schedule(product: dict, scheduled_date, scheduled_time, start=None, end=None) -> dict:
    """Tur urunleri icin secilen tarih/saati dogrular ve satira eklenecek alanlari dondurur.

    Hem `/api/applications` hem `/api/orders` akisi buradan gecer; kural tek yerde durur.
    """
    if not product.get("needs_schedule"):
        return {}
    picked = None
    try:
        picked = date.fromisoformat((scheduled_date or "").strip()[:10])
    except ValueError:
        picked = None
    if not picked:
        raise HTTPException(400, f"{product['name']} için tur tarihi seçmelisiniz.")
    if start and picked < start:
        raise HTTPException(400, "Tur tarihi Dubai'ye giriş tarihinizden önce olamaz.")
    if end and picked > end:
        raise HTTPException(400, "Tur tarihi dönüş tarihinizden sonra olamaz.")
    slots = product.get("time_slots") or []
    time_value = (scheduled_time or "").strip()
    if slots and time_value not in slots:
        raise HTTPException(400, f"{product['name']} için geçerli bir saat seçmelisiniz.")
    return {"scheduled_date": picked.isoformat(), "scheduled_time": time_value or None}
