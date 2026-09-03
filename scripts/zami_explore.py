"""Zami portalinda (kayitli oturumla) gezinip basvuru formunu bulur ve alanlari yakalar.

Kullanim:
    python scripts/zami_explore.py            # menu/linkleri listeler
    python scripts/zami_explore.py <URL>      # verilen sayfanin alanlarini yakalar

Yakalanan alanlar site_settings icine kaydedilir (zami_capture) ve otomatik
mapping onerisi uretilir. Ekran goruntuleri /app/scripts/out altina yazilir.
"""
import asyncio
import json
import sys

sys.path.insert(0, "/app/backend")

from dotenv import load_dotenv  # noqa: E402

load_dotenv("/app/backend/.env")

import zami  # noqa: E402
import zami_rpa  # noqa: E402
from db import settings_col  # noqa: E402

OUT = "/app/scripts/out"


async def _state() -> dict:
    doc = await settings_col.find_one({"key": zami_rpa.SESSION_KEY})
    state = ((doc or {}).get("value") or {}).get("storage_state")
    if not state:
        raise SystemExit("Kayitli portal oturumu yok. Once giris yapilmali.")
    return state


async def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else None
    state = await _state()
    pw, browser, context, page = await zami_rpa._launch_with_state(state)
    try:
        creds = await zami.raw_credentials()
        url = target or creds["portal_url"]
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(2)
        print("URL:", page.url)
        print("Baslik:", await page.title())
        await page.screenshot(path=f"{OUT}/portal_page.png", full_page=True)
        print(f"ekran: {OUT}/portal_page.png")

        links = await page.evaluate(
            """() => Array.from(document.querySelectorAll('a')).map(a => ({
                text: (a.innerText || '').trim().slice(0, 60), href: a.getAttribute('href') || ''
            })).filter(l => l.text || l.href)"""
        )
        seen, uniq = set(), []
        for link in links:
            key = (link["text"], link["href"])
            if key in seen:
                continue
            seen.add(key)
            uniq.append(link)
        print(f"\n{len(uniq)} link bulundu:")
        for link in uniq[:60]:
            print(f"  - {link['text']!r} -> {link['href']}")

        html = await page.content()
        fields = zami.parse_form_fields(html)
        print(f"\nForm alani sayisi: {len(fields)}")
        for field in fields[:40]:
            print(f"  * {field}")

        if target and fields:
            await zami.save_capture("form", {"url": page.url, "fields": fields})
            suggestion = zami.suggest_mapping({"form": {"url": page.url, "fields": fields}})
            print("\nMapping onerisi:")
            print(json.dumps(suggestion, ensure_ascii=False, indent=2)[:3000])
    finally:
        await zami_rpa._close({"pw": pw, "browser": browser, "context": context})


if __name__ == "__main__":
    asyncio.run(main())
