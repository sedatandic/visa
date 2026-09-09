"""Sosyal medya hesaplari: platform katalogu, normalizasyon ve sitede gosterim.

Kaynak: settings koleksiyonunda `social_links` anahtari. Panelde girilmemisse
`company_info` icindeki eski `instagram` / `google_review` alanlarindan uretilir.
"""

PLATFORMS = [
    {
        "id": "instagram",
        "label": "Instagram",
        "base": "https://www.instagram.com/",
        "placeholder": "kullaniciadi veya tam bağlantı",
    },
    {
        "id": "google_review",
        "label": "Google Yorumları",
        "base": "",
        "placeholder": "https://g.page/r/... (Google İşletme Profili yorum bağlantısı)",
    },
    {
        "id": "facebook",
        "label": "Facebook",
        "base": "https://www.facebook.com/",
        "placeholder": "sayfaadi veya tam bağlantı",
    },
    {
        "id": "tiktok",
        "label": "TikTok",
        "base": "https://www.tiktok.com/@",
        "placeholder": "kullaniciadi veya tam bağlantı",
    },
    {
        "id": "youtube",
        "label": "YouTube",
        "base": "https://www.youtube.com/@",
        "placeholder": "kanaladi veya tam bağlantı",
    },
    {
        "id": "x",
        "label": "X (Twitter)",
        "base": "https://x.com/",
        "placeholder": "kullaniciadi veya tam bağlantı",
    },
    {
        "id": "linkedin",
        "label": "LinkedIn",
        "base": "https://www.linkedin.com/company/",
        "placeholder": "sirketadi veya tam bağlantı",
    },
    {
        "id": "threads",
        "label": "Threads",
        "base": "https://www.threads.net/@",
        "placeholder": "kullaniciadi veya tam bağlantı",
    },
]

PLATFORM_BY_ID = {p["id"]: p for p in PLATFORMS}
CATALOG_ORDER = {p["id"]: index for index, p in enumerate(PLATFORMS)}
PLACEMENTS = ("in_dock", "in_footer", "in_contact")


def clean_url(platform_id: str, raw) -> str:
    """Kullanici adini tam adrese cevirir; yalnizca http(s) adreslerini kabul eder."""
    value = str(raw or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        return value[:400]
    if value.startswith("www."):
        return f"https://{value}"[:400]
    base = (PLATFORM_BY_ID.get(platform_id) or {}).get("base") or ""
    if not base:
        return ""
    handle = value.lstrip("@/").strip()
    return f"{base}{handle}"[:400] if handle else ""


def normalize_items(items) -> list:
    """Panelden gelen listeyi tek kayit/platform olacak sekilde temizler."""
    seen: dict = {}
    for raw in items or []:
        platform = str((raw or {}).get("platform") or "").strip()
        if platform not in PLATFORM_BY_ID or platform in seen:
            continue
        url = clean_url(platform, (raw or {}).get("url"))
        seen[platform] = {
            "platform": platform,
            "url": url,
            "enabled": bool(raw.get("enabled", True)) and bool(url),
            "in_dock": bool(raw.get("in_dock", True)),
            "in_footer": bool(raw.get("in_footer", True)),
            "in_contact": bool(raw.get("in_contact", True)),
            "order": int(raw.get("order") or CATALOG_ORDER.get(platform, 0)),
        }
    return sorted(seen.values(), key=lambda item: (item["order"], CATALOG_ORDER[item["platform"]]))


def _blank(platform_id: str, url: str = "") -> dict:
    return {
        "platform": platform_id,
        "url": url,
        "enabled": bool(url),
        "in_dock": True,
        "in_footer": True,
        "in_contact": True,
        "order": CATALOG_ORDER[platform_id],
    }


def resolve_items(company: dict, stored) -> list:
    """Panelde gosterilecek tam liste: her platform icin bir satir."""
    saved = {item["platform"]: item for item in normalize_items(stored)}
    legacy = {
        "instagram": str((company or {}).get("instagram") or "").strip(),
        "google_review": str((company or {}).get("google_review") or "").strip(),
    }
    rows = []
    for platform in PLATFORMS:
        pid = platform["id"]
        if pid in saved:
            rows.append(saved[pid])
        else:
            rows.append(_blank(pid, legacy.get(pid, "")))
    return rows


def public_links(company: dict, stored) -> list:
    """Sitede gosterilecek (yayinda ve adresi girilmis) hesaplar."""
    return [
        {
            "platform": item["platform"],
            "label": PLATFORM_BY_ID[item["platform"]]["label"],
            "url": item["url"],
            **{key: item[key] for key in PLACEMENTS},
        }
        for item in resolve_items(company, stored)
        if item["enabled"] and item["url"]
    ]
