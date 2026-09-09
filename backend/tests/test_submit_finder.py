"""Zami gonder butonu tespiti: farkli portal buton varyantlari icin tarayici testi."""

import asyncio

from playwright.async_api import async_playwright

from routes_zami import SUBMIT_FINDER_JS

CHROME = "/usr/local/bin/browser-use-chromium"

CASES = [
    ("<form><input name=a><button type=submit id=btnGo>Insert</button></form>", "#btnGo"),
    ("<form><input name=a><input type=button name=save value='SAVE APPLICATION'></form>", 'input[name="save"]'),
    ("<form><input name=a><a class=btn href='#' onclick='x()'>Gönder</a></form>", 'a:has-text("Gönder")'),
    (
        "<form><input name=a><button onclick='x()'>Cancel</button><button id=ok onclick='y()'>Kaydet</button></form>",
        "#ok",
    ),
    ("<form><input name=a><div role=button id=dv>Submit</div></form>", "#dv"),
    ("<form><input name=a></form>", None),
]


async def main() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        page = await browser.new_page()
        for html, expected in CASES:
            await page.set_content(f"<body>{html}</body>")
            found = await page.evaluate(
                "() => { "
                + SUBMIT_FINDER_JS
                + "; var f = dvoFindSubmit(); return f ? f.selector : null; }"
            )
            assert found == expected, f"{html} -> {found} (beklenen {expected})"
            print("ok:", expected)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
