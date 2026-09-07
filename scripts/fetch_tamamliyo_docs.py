"""Tamamliyo partner panel dokumantasyonunu indirir (tek seferlik yardimci).

Kullanim: python /app/scripts/fetch_tamamliyo_docs.py
Cikti: /app/memory/tamamliyo/*.txt
"""
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

BASE = "https://dashboard.tamamliyo.com"
EMAIL = os.environ.get("TAMAMLIYO_PANEL_EMAIL", "")
PASSWORD = os.environ.get("TAMAMLIYO_PANEL_PASSWORD", "")
OUT_DIR = "/app/memory/tamamliyo"
PAGES = {
    "travel_api": "/profile/seyahat-saglik",
    "iptal_servis": "/profile/iptal-servis",
}


def login() -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0"
    page = session.get(BASE, timeout=30)
    token = BeautifulSoup(page.text, "html.parser").find("input", {"name": "_token"})
    payload = {"email": EMAIL, "password": PASSWORD, "_token": token["value"] if token else ""}
    res = session.post(f"{BASE}/giris-yap", data=payload, timeout=30, allow_redirects=True)
    if "anasayfa" not in res.url and "Hoş Geldin" not in res.text:
        raise SystemExit(f"giris basarisiz: {res.status_code} {res.url}")
    return session


def dump(session: requests.Session, name: str, path: str) -> None:
    html = session.get(f"{BASE}{path}", timeout=60).text
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav"]):
        tag.decompose()
    text = re.sub(r"\n{3,}", "\n\n", soup.get_text("\n", strip=True))
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/{name}.txt", "w", encoding="utf-8") as handle:
        handle.write(text)
    print(f"{name}: {len(text)} karakter -> {OUT_DIR}/{name}.txt")


if __name__ == "__main__":
    if not (EMAIL and PASSWORD):
        sys.exit("TAMAMLIYO_PANEL_EMAIL / TAMAMLIYO_PANEL_PASSWORD gerekli")
    s = login()
    for key, url in PAGES.items():
        dump(s, key, url)
