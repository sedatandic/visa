"""Iteration 133: yonetici teklif linkleri (paylasilabilir teklif).

Kapsam:
- Admin teklif olusturma (fiyat = /pricing/quote ile ayni), link + WhatsApp metni,
- musteriye acilan public uc (/api/offers/{token}) ve goruntulenme sayaci,
- kapatilan / suresi dolmus / bilinmeyen jeton -> 404,
- jetonsuz erisim engeli,
- yardimci fonksiyonlar (durum, wa numarasi, paylasim metni).
"""

import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
import requests

sys.path.insert(0, "/app/backend")

import offer_links  # noqa: E402
from admin_test_token import admin_token  # noqa: E402

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def headers():
    return {"Authorization": f"Bearer {admin_token()}"}


@pytest.fixture(scope="module")
def visa_id():
    r = requests.get(f"{API}/visa-types", timeout=30)
    assert r.status_code == 200, r.text
    items = [v for v in r.json() if v.get("applicant_type") != "child"]
    assert items
    return items[0]["id"]


@pytest.fixture(scope="module")
def created(headers, visa_id):
    payload = {
        "customer_name": "Teklif Test",
        "customer_phone": "0538 483 82 24",
        "travelers": [
            {"applicant_type": "adult", "visa_type_id": visa_id},
            {"applicant_type": "adult", "visa_type_id": visa_id},
        ],
        "addons": {"express": True},
        "note": "Iteration 133 testi",
        "valid_days": 7,
    }
    r = requests.post(f"{API}/admin/offer-links", json=payload, headers=headers, timeout=60)
    assert r.status_code == 200, r.text
    doc = r.json()
    yield doc
    requests.delete(f"{API}/admin/offer-links/{doc['id']}", headers=headers, timeout=30)


# ---------------------------------------------------------------- yardimcilar
def test_modul_seviyesinde_dairesel_import_yok():
    """Kod incelemesi tekrar 'circular import' bildirmesin: graf dongusuz olmali.

    Fiyatlama yardimcilari (`resolve_store_lines`, `trip_day_count`, `get_visa_type`)
    `store_catalog` icinde durur; `offer_links` route modullerini import etmez.
    """
    import ast
    import collections
    import pathlib

    root = pathlib.Path("/app/backend")
    modules = {p.stem for p in root.glob("*.py")}
    edges = collections.defaultdict(set)
    for name in modules:
        tree = ast.parse((root / f"{name}.py").read_text())
        for node in tree.body:  # yalniz modul seviyesi importlar
            if isinstance(node, ast.Import):
                edges[name] |= {a.name for a in node.names if a.name in modules}
            elif isinstance(node, ast.ImportFrom) and node.module in modules:
                edges[name].add(node.module)

    cycles = []

    def walk(start, node, path, seen):
        for nxt in edges[node]:
            if nxt == start:
                cycles.append(" -> ".join(path + [nxt]))
            elif nxt not in seen:
                walk(start, nxt, path + [nxt], seen | {nxt})

    for name in sorted(modules):
        walk(name, name, [name], {name})
    assert not cycles, f"dairesel import: {cycles[:5]}"

    assert "routes_public" not in edges["offer_links"]
    assert "store_catalog" in edges["offer_links"]


def test_status_durumlari():
    now = datetime.now(timezone.utc)
    assert offer_links.status_of({"active": True}, now) == "active"
    assert offer_links.status_of({"active": False}, now) == "disabled"
    assert offer_links.status_of({"active": True, "application_id": "x"}, now) == "used"
    assert offer_links.status_of({"active": True, "expires_at": now - timedelta(days=1)}, now) == "expired"


def test_wa_numarasi_normalizasyonu():
    assert offer_links.wa_number("0538 483 82 24") == "905384838224"
    assert offer_links.wa_number("+90 538 483 82 24") == "905384838224"
    assert offer_links.wa_number("538 483 82 24") == "905384838224"
    assert offer_links.wa_number("123") == ""


def test_token_tahmin_edilemez():
    tokens = {offer_links.new_token() for _ in range(50)}
    assert len(tokens) == 50
    assert all(len(t) >= 10 for t in tokens)


def test_paylasim_metni_link_ve_tutar_icerir():
    doc = {"customer_name": "Ayşe", "title": "2 kişi · 30 Gün", "total": 10380, "currency": "TRY"}
    text = offer_links.share_text(doc, "https://x/teklif/abc")
    assert "Ayşe" in text and "https://x/teklif/abc" in text and "10.380 ₺" in text


# ---------------------------------------------------------------- admin ucu
def test_admin_teklif_olusturur(created):
    assert created["token"] and created["status"] == "active"
    assert created["url"].endswith(f"/teklif/{created['token']}")
    assert created["apply_url"].endswith(f"/basvuru?teklif={created['token']}")
    assert "wa.me/905384838224" in created["whatsapp_url"]
    assert created["total"] > 0
    # baslik bos gonderildi -> otomatik uretildi
    assert "2 kişi" in created["title"]


def test_teklif_tutari_quote_ile_ayni(created, visa_id):
    r = requests.post(
        f"{API}/pricing/quote",
        json={"visa_type_ids": [visa_id, visa_id], "addons": {"express": True}, "store_items": []},
        timeout=30,
    )
    assert r.status_code == 200, r.text
    assert round(r.json()["total"], 2) == round(created["total"], 2)


def test_admin_listesinde_gorunur(headers, created):
    r = requests.get(f"{API}/admin/offer-links", headers=headers, timeout=30)
    assert r.status_code == 200, r.text
    body = r.json()
    assert any(item["token"] == created["token"] for item in body["items"])
    assert body["active"] >= 1


def test_jetonsuz_admin_erisimi_engellenir():
    r = requests.get(f"{API}/admin/offer-links", timeout=30)
    assert r.status_code in (401, 403)
    r = requests.post(f"{API}/admin/offer-links", json={"travelers": []}, timeout=30)
    assert r.status_code in (401, 403, 422)


def test_gecersiz_vize_tipi_reddedilir(headers):
    r = requests.post(
        f"{API}/admin/offer-links",
        json={"travelers": [{"applicant_type": "adult", "visa_type_id": "yok_boyle_vize"}]},
        headers=headers,
        timeout=30,
    )
    assert r.status_code == 400, r.text
    assert "vize tipi" in r.json()["detail"].lower()


# ---------------------------------------------------------------- musteri ucu
def test_musteri_teklifi_gorebilir(created):
    r = requests.get(f"{API}/offers/{created['token']}", timeout=30)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["token"] == created["token"]
    assert len(body["travelers"]) == 2
    assert body["quote"]["total"] == created["total"]
    assert body["apply_path"] == f"/basvuru?teklif={created['token']}"
    assert body["note"] == "Iteration 133 testi"
    assert body["customer_name"] == "Teklif Test"
    # kisisel veri en aza indirilmis: telefon/e-posta public yanitta yok
    assert "customer_phone" not in body and "customer_email" not in body


def test_goruntulenme_sayaci_artar(headers, created):
    requests.get(f"{API}/offers/{created['token']}", timeout=30)
    r = requests.get(f"{API}/admin/offer-links", headers=headers, timeout=30)
    row = next(i for i in r.json()["items"] if i["token"] == created["token"])
    assert row["views"] >= 1


def test_bilinmeyen_jeton_404():
    r = requests.get(f"{API}/offers/olmayanjeton123", timeout=30)
    assert r.status_code == 404


def test_kapatilan_teklif_acilmaz(headers, visa_id):
    payload = {
        "travelers": [{"applicant_type": "adult", "visa_type_id": visa_id}],
        "valid_days": 3,
    }
    doc = requests.post(f"{API}/admin/offer-links", json=payload, headers=headers, timeout=60).json()
    assert requests.get(f"{API}/offers/{doc['token']}", timeout=30).status_code == 200

    r = requests.delete(f"{API}/admin/offer-links/{doc['id']}", headers=headers, timeout=30)
    assert r.status_code == 200, r.text
    assert requests.get(f"{API}/offers/{doc['token']}", timeout=30).status_code == 404


def test_teklif_basvuruya_baglanir(headers, visa_id):
    """mark_used: teklif linkinden gelen basvuru teklife islenir (donusum takibi)."""
    import asyncio

    from db import offer_links_col

    doc = requests.post(
        f"{API}/admin/offer-links",
        json={"travelers": [{"applicant_type": "adult", "visa_type_id": visa_id}]},
        headers=headers,
        timeout=60,
    ).json()

    async def convert():
        await offer_links.mark_used(doc["token"], {"id": "app-133", "reference_code": "DV-133TEST"})
        return await offer_links_col.find_one({"token": doc["token"]})

    fresh = asyncio.run(convert())
    assert fresh["application_id"] == "app-133"
    assert fresh["reference_code"] == "DV-133TEST"
    assert fresh["conversions"] == 1
    assert offer_links.status_of(fresh) == "used"
    # kullanilan teklif hala acilabilir (musteri linki tekrar acabilir)
    assert requests.get(f"{API}/offers/{doc['token']}", timeout=30).status_code == 200
    requests.delete(f"{API}/admin/offer-links/{doc['id']}", headers=headers, timeout=30)


def test_suresi_dolmus_teklif_acilmaz(headers, visa_id):
    """expires_at gecmise cekilince musteri ucu 404 doner."""
    import asyncio

    from db import offer_links_col

    doc = requests.post(
        f"{API}/admin/offer-links",
        json={"travelers": [{"applicant_type": "adult", "visa_type_id": visa_id}]},
        headers=headers,
        timeout=60,
    ).json()

    async def expire():
        await offer_links_col.update_one(
            {"token": doc["token"]},
            {"$set": {"expires_at": datetime.now(timezone.utc) - timedelta(days=1)}},
        )

    asyncio.run(expire())
    r = requests.get(f"{API}/offers/{doc['token']}", timeout=30)
    assert r.status_code == 404
    assert "süre" in r.json()["detail"].lower()
    requests.delete(f"{API}/admin/offer-links/{doc['id']}", headers=headers, timeout=30)
