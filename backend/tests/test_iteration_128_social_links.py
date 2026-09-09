"""Admin -> Sosyal Medya: platform katalogu, normalizasyon ve sitede gosterim."""
import os
import sys

import pytest
import requests

sys.path.insert(0, "/app/backend")

import social_links  # noqa: E402
from admin_test_token import admin_token  # noqa: E402

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def headers():
    return {"Authorization": f"Bearer {admin_token()}"}


# ------------------------------------------------------------------ saf fonksiyonlar
def test_kullanici_adi_tam_adrese_cevrilir():
    assert social_links.clean_url("instagram", "dubaivizehatti") == (
        "https://www.instagram.com/dubaivizehatti"
    )
    assert social_links.clean_url("instagram", "@dubaivizehatti") == (
        "https://www.instagram.com/dubaivizehatti"
    )
    assert social_links.clean_url("tiktok", "dubaivize") == "https://www.tiktok.com/@dubaivize"


def test_tam_adres_oldugu_gibi_kalir():
    url = "https://g.page/r/CabcDEF/review"
    assert social_links.clean_url("google_review", url) == url


def test_www_ile_baslayan_adrese_https_eklenir():
    assert social_links.clean_url("facebook", "www.facebook.com/dvh") == (
        "https://www.facebook.com/dvh"
    )


def test_javascript_adresi_kabul_edilmez():
    # google_review'da base olmadigi icin serbest metin adres uretmez
    assert social_links.clean_url("google_review", "javascript:alert(1)") == ""


def test_bos_adres_yayindan_dusurulur():
    items = social_links.normalize_items(
        [{"platform": "instagram", "url": "", "enabled": True}]
    )
    assert items[0]["enabled"] is False


def test_bilinmeyen_platform_ve_mukerrer_kayit_atlanir():
    items = social_links.normalize_items(
        [
            {"platform": "myspace", "url": "https://x.com/a"},
            {"platform": "x", "url": "https://x.com/a"},
            {"platform": "x", "url": "https://x.com/b"},
        ]
    )
    assert [i["platform"] for i in items] == ["x"]
    assert items[0]["url"] == "https://x.com/a"


def test_sira_degerine_gore_dizilir():
    items = social_links.normalize_items(
        [
            {"platform": "instagram", "url": "https://www.instagram.com/a", "order": 5},
            {"platform": "youtube", "url": "https://www.youtube.com/@b", "order": 1},
        ]
    )
    assert [i["platform"] for i in items] == ["youtube", "instagram"]


def test_panel_listesi_her_platform_icin_satir_dondurur():
    rows = social_links.resolve_items({"instagram": "https://www.instagram.com/eski"}, None)
    assert len(rows) == len(social_links.PLATFORMS)
    instagram = next(r for r in rows if r["platform"] == "instagram")
    assert instagram["url"] == "https://www.instagram.com/eski"
    assert instagram["enabled"] is True


def test_public_links_sadece_yayinda_olanlari_verir():
    stored = [
        {"platform": "instagram", "url": "https://www.instagram.com/a", "enabled": True},
        {"platform": "youtube", "url": "https://www.youtube.com/@b", "enabled": False},
    ]
    links = social_links.public_links({}, stored)
    assert [l["platform"] for l in links] == ["instagram"]
    assert links[0]["label"] == "Instagram"
    assert links[0]["in_dock"] is True


# ------------------------------------------------------------------ uc noktalar
def test_admin_social_get_platform_katalogu_dondurur(headers):
    r = requests.get(f"{API}/admin/social", headers=headers, timeout=30)
    assert r.status_code == 200, r.text
    body = r.json()
    assert [p["id"] for p in body["platforms"]] == [p["id"] for p in social_links.PLATFORMS]
    assert len(body["items"]) == len(social_links.PLATFORMS)


def test_admin_social_jetonsuz_erisim_engellenir():
    assert requests.get(f"{API}/admin/social", timeout=30).status_code in (401, 403)


def test_admin_social_kaydeder_ve_sitede_gorunur(headers):
    """Gonderilmeyen platformlar korunur, adres girilmeyen platform yayina alinmaz."""
    before = {
        i["platform"]: i
        for i in requests.get(f"{API}/admin/social", headers=headers, timeout=30).json()["items"]
    }
    payload = {
        "items": [
            {
                "platform": "instagram",
                "url": "dubaivizehatti",
                "enabled": True,
                "in_dock": True,
                "in_footer": True,
                "in_contact": True,
                "order": 0,
            },
            {
                "platform": "tiktok",
                "url": "",
                "enabled": True,
                "in_dock": False,
                "in_footer": True,
                "in_contact": True,
                "order": 3,
            },
        ]
    }
    r = requests.put(f"{API}/admin/social", json=payload, headers=headers, timeout=30)
    assert r.status_code == 200, r.text
    saved = {i["platform"]: i for i in r.json()["items"]}
    assert saved["instagram"]["url"] == "https://www.instagram.com/dubaivizehatti"
    assert saved["tiktok"]["enabled"] is False  # adres yok -> yayinda olamaz
    # Gonderilmeyen platform (google_review) oldugu gibi korunur
    assert saved["google_review"]["url"] == before["google_review"]["url"]
    assert saved["google_review"]["enabled"] == before["google_review"]["enabled"]

    site = requests.get(f"{API}/content/site", timeout=30).json()
    links = {l["platform"]: l for l in site["social_links"]}
    assert links["instagram"]["url"] == "https://www.instagram.com/dubaivizehatti"
    assert "tiktok" not in links
    # Eski alanlarla uyum korunur
    assert site["company"]["instagram"] == "https://www.instagram.com/dubaivizehatti"


def test_kayittan_sonra_instagram_hesabi_dubaivizehatti(headers):
    """Kullanici istegi: Instagram hesabi dubaivizehatti olmali."""
    site = requests.get(f"{API}/content/site", timeout=30).json()
    instagram = next(l for l in site["social_links"] if l["platform"] == "instagram")
    assert "dubaivizehatti" in instagram["url"]
