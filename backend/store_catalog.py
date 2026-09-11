"""Magaza urun katalogu (eSIM / sigorta / tur) ve fiyat listesi.

`routes_store` ile `insurance_tasks` her ikisi de urun listesine ihtiyac duyuyordu ve
birbirini import ediyordu (dairesel bagimlilik). Katalog burada tek yerde durur; iki
modul de buradan import eder.
"""

from datetime import date, timedelta
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

# Seyahat sagligi policeleri: maliyet saglayici tarifesinden (Sigortambudur,
# en ucuz sirket teklifi) gelir; satis fiyati %100 marj ile TL olarak belirlenir
# (`insurance_margin`). Buradaki degerler katalog/yedek tarifedir, panelden guncellenir.
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
        "provider": "sigortambudur",
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

DESERT_GALLERY = [
    {
        "url": "https://images.unsplash.com/photo-1506645728556-ac574e628eca?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
        "caption": "4×4 Land Cruiser ile kumul safarisi",
    },
    {
        "url": "https://images.unsplash.com/photo-1624062999803-976e1adc8ea2?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
        "caption": "ATV (quad) safari",
    },
    {
        "url": "https://images.unsplash.com/photo-1760529697940-45dfa4f1cd84?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
        "caption": "Gün batımında deve turu",
    },
    {
        "url": "https://images.unsplash.com/photo-1553522988-49daec855a59?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
        "caption": "Bedevi kampı ve akşam programı",
    },
]

# Dubai aktiviteleri: teslimat/rezervasyon acente eliyle yapilir
DESERT_ITINERARY = [
    "15:00 · Otelinizden alınış, çöl bölgesine yaklaşık 40 dakika yolculuk",
    "30 dakika 4×4 kumul safarisi (dune bashing)",
    "Kum sörfü (sandboarding) ve çölün en iyi fotoğraf noktalarında mola",
    "Gün batımının ardından yerel Bedevi kampına geçiş",
    "Kamp girişinde kısa deve turu ve fotoğraf çekimi",
    "Açık büfe akşam yemeği, ateş ve dans gösterileri; kadın misafirlere kına",
    "21:00 – 22:00 · Otelinize dönüş",
]

TOUR_PRODUCTS = [
    {
        "id": "tour_desert_safari",
        "kind": "tour",
        "name": "Dubai Çöl Safarisi · Akşam Turu",
        "summary": "7 kişilik 4×4 Land Cruiser ile kumul safarisi, kum sörfü, deve turu ve Bedevi kampında açık büfe akşam yemeği.",
        "price_usd": 45.0,
        "image_url": "https://images.unsplash.com/photo-1763535539149-53eddcfa20dd?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
        "needs_schedule": True,
        "time_slots": ["15:00"],
        "features": [
            "Otelinizden alış ve dönüş dahil · 7 kişilik 4×4 Land Cruiser",
            "30 dakika kumul safarisi ve kum sörfü",
            "Bedevi kampında deve turu, kına ve açık büfe akşam yemeği",
            "Ateş ve dans gösterileriyle akşam programı",
            "Ortalama 6–7 saat · otelden alınış 15:00, dönüş 21:00 – 22:00",
        ],
        "gallery": DESERT_GALLERY,
        "itinerary": DESERT_ITINERARY[:2]
        + ["İsteğe bağlı 30 dakika ATV safari (+40 USD); istemeyen misafirler dinlenme ve alışveriş alanında vakit geçirir"]
        + DESERT_ITINERARY[2:],
        "order": 1,
        "popular": True,
    },
    {
        "id": "tour_desert_safari_vip",
        "kind": "tour",
        "name": "Dubai Çöl Safarisi · VIP Akşam Turu",
        "summary": "Özel 4×4 Land Cruiser ile kumul safarisi, ATV (quad) sürüşü, VIP kamp masası ve ateş başında canlı gösteriler.",
        "price_usd": 55.0,
        "image_url": "https://images.unsplash.com/photo-1631730690491-d2efef90fc21?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
        "needs_schedule": True,
        "time_slots": ["15:00"],
        "features": [
            "Otelinizden özel 4×4 Land Cruiser ile alış ve dönüş",
            "30 dakika ATV (quad) safari ve kum sörfü dahil",
            "VIP kamp masası, sınırsız içecek ikramı",
            "Ateş gösterisi, tanura ve canlı müzik",
            "Ortalama 6–7 saat · otelden alınış 15:00, dönüş 21:00 – 22:00",
        ],
        "gallery": DESERT_GALLERY,
        "itinerary": DESERT_ITINERARY[:2]
        + ["30 dakika ATV (quad) safari · VIP pakete dahil, ek ücret yok"]
        + DESERT_ITINERARY[2:],
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


# Musteriye/rakibe gosterilmemesi gereken tedarik alanlari (maliyet ve saglayici kodlari)
PRIVATE_PRODUCT_FIELDS = ("cost_try", "cost_updated_at", "cost_source", "provider_urun_id", "provider")


def public_products(items: list) -> list:
    """Herkese acik yanitlar icin urun listesinden maliyet/saglayici alanlarini temizler."""
    public = []
    for item in items:
        row = dict(item)
        for field in PRIVATE_PRODUCT_FIELDS:
            row.pop(field, None)
        public.append(row)
    return public


def customer_order_view(order: dict) -> dict:
    """Siparis kaydini musteriye gosterilecek hale getirir (satir maliyetleri gizlenir)."""
    view = dict(order or {})
    view["items"] = [
        {k: v for k, v in dict(line).items() if k not in {"unit_cost", "unit_price_usd"}}
        for line in (view.get("items") or [])
    ]
    return view

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


# ------------------------------------------------------- tarih / satir yardimcilari
# NOT: Bu yardimcilar `routes_public` icindeydi; `offer_links` de ayni fiyatlama
# kurallarina ihtiyac duydugu icin (dairesel import olusmasin diye) katalog modulune
# tasindi. Tek kural noktasi: hem basvuru, hem siparis, hem teklif buradan gecer.
def parse_iso_date(value: str | None):
    try:
        return date.fromisoformat((value or "").strip()[:10])
    except Exception:
        return None


def trip_day_count(arrival: str | None, departure: str | None) -> Optional[int]:
    """Seyahat suresi (gun). Giris ve donus gunleri dahil."""
    start = parse_iso_date(arrival)
    end = parse_iso_date(departure)
    if not start or not end or end < start:
        return None
    return (end - start).days + 1


def _store_line_validity(start, validity_days: int, trip_days: Optional[int]) -> dict:
    """Ek urunun gecerlilik penceresini ve seyahati kapsayip kapsamadigini hesaplar."""
    starts_on = start.isoformat() if start else None
    ends_on = None
    if start and validity_days > 0:
        ends_on = (start + timedelta(days=validity_days - 1)).isoformat()
    covers_trip = None
    if trip_days and validity_days:
        covers_trip = trip_days <= validity_days
    return {
        "validity_days": validity_days,
        "starts_on": starts_on,
        "ends_on": ends_on,
        "trip_days": trip_days,
        "covers_trip": covers_trip,
    }


def _store_line(product: dict, quantity: int, validity: dict) -> dict:
    unit_price = float(product["price"])
    return {
        "product_id": product["id"],
        "kind": product.get("kind", ""),
        "kind_label": product.get("kind_label", ""),
        "name": product["name"],
        "quantity": quantity,
        "unit_price": unit_price,
        "unit_price_usd": float(product.get("price_usd") or 0),
        "total": round(unit_price * quantity, 2),
        **validity,
    }


async def resolve_store_lines(
    items, arrival_date: Optional[str] = None, departure_date: Optional[str] = None
) -> list:
    """Secilen eSIM / sigorta / tur urunlerini katalogdan fiyatlar.

    Urunlerin gecerlilik tarihleri seyahatin giris tarihinden baslatilir.
    """
    if not items:
        return []

    catalog = {p["id"]: p for p in await product_list()}
    start = parse_iso_date(arrival_date)
    end = parse_iso_date(departure_date)
    trip_days = trip_day_count(arrival_date, departure_date)

    lines = []
    for item in items:
        product = catalog.get(item.product_id)
        if not product:
            raise HTTPException(400, "Secilen ek urun bulunamadi veya satista degil.")
        quantity = max(1, min(int(item.quantity), MAX_QTY))
        validity = _store_line_validity(start, int(product.get("validity_days") or 0), trip_days)
        line = _store_line(product, quantity, validity)
        line.update(
            tour_schedule(
                product,
                getattr(item, "scheduled_date", None),
                getattr(item, "scheduled_time", None),
                start=start,
                end=end,
            )
        )
        lines.append(line)
    return lines


async def get_visa_type(visa_type_id: str):
    """Vize tipini DB'den (yoksa statik katalogdan) okur, guncel kurla fiyatlar."""
    from content import VISA_TYPES
    from db import visa_types_col
    from fx import apply_fx_to_visa

    visa = await visa_types_col.find_one({"id": visa_type_id})
    if not visa:
        visa = next((v for v in VISA_TYPES if v["id"] == visa_type_id), None)
    if not visa:
        return None
    return await apply_fx_to_visa(serialize_doc(visa))
