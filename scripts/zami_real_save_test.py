"""Zami'de GERCEK kayit testi.

Robot formu doldurur, portalda zorunlu olan (bizde olmayan) alanlari test
degerleriyle tamamlar, durum secenegini **Waiting** (bekleme listesi) yapar ve
SAVE'e basar. 'Send' secilmedigi icin basvuru goc idaresine gonderilmez ve
ucretlendirilmez; yalnizca Zami hesabinizin bekleme listesine dusen gercek bir
kayit olusur.

Kullanim: python scripts/zami_real_save_test.py
"""
import asyncio
import base64
import sys

sys.path.insert(0, "/app/backend")

from dotenv import load_dotenv  # noqa: E402

load_dotenv("/app/backend/.env")

import zami  # noqa: E402
import zami_rpa  # noqa: E402
from db import applications_col  # noqa: E402

REFERENCE = "DV-CV681445"
OUT = "/app/scripts/out"

# Portalda zorunlu olup bizim formda toplanmayan alanlar icin TEST degerleri
TEST_MANUAL_VALUES = {
    '[name="fa"]': "TEST FATHER",
    '[name="mo"]': "TEST MOTHER",
    '[name="pf_tt"]': "EMPLOYEE",
    '[name="eu"]': "Bachelor",
    # Bekleme listesine dussun: 'Send' DEGIL
    '[name="st"]': "Waiting",
}
SAVE_SELECTOR = 'button:has-text("SUBMIT")'


async def main() -> None:
    original = await zami.get_mapping()
    doc = await applications_col.find_one({"reference_code": REFERENCE})
    if not doc:
        print(f"{REFERENCE} bulunamadi.")
        return

    test_mapping = dict(original)
    test_mapping["constants"] = {**(original.get("constants") or {}), **TEST_MANUAL_VALUES}
    test_mapping["submit_selector"] = SAVE_SELECTOR
    await zami.save_mapping(test_mapping)
    print("Test mapping uygulandi (Waiting + Save).")

    try:
        payload = zami.build_payload(doc, "https://visa-bot-dashboard.preview.emergentagent.com")
        result = await zami_rpa.fill_application(doc, payload, dry_run=False, actor="real-save-test")
        print("\nok:", result.get("ok"), "| gonderildi(save):", result.get("submitted"))
        print("dolu alan:", result.get("filled_count"))
        print("bulunamayan:", result.get("missing"))
        print("portal yonetiyor:", result.get("skipped_disabled"))
        print("url:", result.get("current_url"))
        print("hata:", result.get("error"))
        shot = result.get("screenshot")
        if shot:
            path = f"{OUT}/real_save_result.png"
            with open(path, "wb") as fh:
                fh.write(base64.b64decode(shot.split(",", 1)[-1]))
            print("ekran:", path)
    finally:
        await zami.save_mapping(original)
        print("\nOrijinal mapping geri yuklendi (submit_selector bos, dry_run guvenli).")


if __name__ == "__main__":
    asyncio.run(main())
