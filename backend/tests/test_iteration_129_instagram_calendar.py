"""Admin -> Instagram Takvimi: 12 hazir gonderi, tarih/metin/durum kaydi."""
import os
import sys

import pytest
import requests

sys.path.insert(0, "/app/backend")

import instagram_posts  # noqa: E402
from admin_test_token import admin_token  # noqa: E402

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"
PUBLIC_DIR = "/app/frontend/public"


@pytest.fixture(scope="module")
def headers():
    return {"Authorization": f"Bearer {admin_token()}"}


def test_plan_12_gonderi_icerir():
    assert len(instagram_posts.POSTS) == 12
    assert len({p["id"] for p in instagram_posts.POSTS}) == 12


def test_her_gonderinin_gorseli_diskte_var():
    for post in instagram_posts.POSTS:
        path = PUBLIC_DIR + post["image"].split("?")[0]
        assert os.path.exists(path), f"eksik gorsel: {path}"
        assert os.path.getsize(path) > 20_000


def test_tarihler_farkli_ve_artan():
    from datetime import datetime, timezone

    rows = instagram_posts.default_schedule(datetime(2026, 7, 1, tzinfo=timezone.utc))
    dates = [row["scheduled_at"][:10] for row in rows]
    assert len(set(dates)) == 12, "tum gonderiler farkli tarihte olmali"
    assert dates == sorted(dates)


def test_metinler_ve_hashtagler_dolu():
    for post in instagram_posts.POSTS:
        assert len(post["caption"]) > 80
        assert post["hashtags"].startswith("#")
        assert "dubaivizehatti" in post["hashtags"]


def test_profil_bilgisi_dubaivizehatti():
    assert instagram_posts.PROFILE["username"] == "dubaivizehatti"
    assert len(instagram_posts.PROFILE["steps"]) >= 4


def test_admin_instagram_get(headers):
    r = requests.get(f"{API}/admin/instagram", headers=headers, timeout=30)
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["posts"]) == 12
    assert body["profile"]["username"] == "dubaivizehatti"
    first = body["posts"][0]
    assert {"id", "title", "image", "caption", "hashtags", "scheduled_at", "status"} <= set(first)


def test_admin_instagram_jetonsuz_engellenir():
    assert requests.get(f"{API}/admin/instagram", timeout=30).status_code in (401, 403)


def test_admin_instagram_tarih_metin_durum_kaydeder(headers):
    posts = requests.get(f"{API}/admin/instagram", headers=headers, timeout=30).json()["posts"]
    target = posts[-1]
    payload = {
        "items": [
            {
                "id": target["id"],
                "scheduled_at": "2026-12-24T18:30:00+00:00",
                "caption": "TEST metni - takvim kaydi",
                "status": "posted",
            }
        ]
    }
    r = requests.put(f"{API}/admin/instagram", json=payload, headers=headers, timeout=30)
    assert r.status_code == 200, r.text
    saved = {p["id"]: p for p in r.json()["posts"]}[target["id"]]
    assert saved["scheduled_at"].startswith("2026-12-24")
    assert saved["caption"] == "TEST metni - takvim kaydi"
    assert saved["status"] == "posted"

    # Gorsel/baslik/hashtag plandan gelmeye devam eder
    assert saved["image"] == target["image"]
    assert saved["hashtags"] == target["hashtags"]

    # Geri al
    restore = {
        "items": [
            {
                "id": target["id"],
                "scheduled_at": target["scheduled_at"],
                "caption": target["caption"],
                "status": "planned",
            }
        ]
    }
    r2 = requests.put(f"{API}/admin/instagram", json=restore, headers=headers, timeout=30)
    assert r2.status_code == 200
    back = {p["id"]: p for p in r2.json()["posts"]}[target["id"]]
    assert back["status"] == "planned"


def test_bilinmeyen_id_gonderilirse_yoksayilir(headers):
    before = requests.get(f"{API}/admin/instagram", headers=headers, timeout=30).json()["posts"]
    r = requests.put(
        f"{API}/admin/instagram",
        json={"items": [{"id": "ig-99", "caption": "olmayan", "status": "posted"}]},
        headers=headers,
        timeout=30,
    )
    assert r.status_code == 200
    assert len(r.json()["posts"]) == len(before)
