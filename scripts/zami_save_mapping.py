"""Zami 'New Visa Request (Dubai)' formu icin gercek alan eslemesini kaydeder.

Alan adlari 03.09.2026'da canli portaldan yakalanmistir (84 alan).
Sadece bizim topladigimiz veriler eslenir; portalda zorunlu olup bizde
bulunmayan alanlar (Baba/Anne adi, Meslek, Ucus bilgileri vb.) operator
tarafindan doldurulur.
"""
import asyncio
import json
import sys

sys.path.insert(0, "/app/backend")

from dotenv import load_dotenv  # noqa: E402

load_dotenv("/app/backend/.env")

import zami  # noqa: E402

FORM_URL = "https://visa.zamitours.ae/?_=203&s=smrtch.edit"

MAPPING = {
    "form_url": FORM_URL,
    # Gonderim: 'Send' radio'su secilip Save'e basilir. Ilk canli testte
    # bilerek bos birakiliyor (robot formu doldurur, GONDERMEZ).
    "submit_selector": "",
    "dry_run": True,
    # Basvuru geneli alanlar
    "fields": {
        "travel.arrival_date_dmy_dash": '[name="ad"]',
        "reference_code": '[name="dr_rf"]',
        "travel.notes": '[name="vs_cm"]',
        "zami_visa_type": '[name="dr_tp"]',
        "birth_country_label": '[name="bc_tt"]',
        "contact.phone": '[name="mp"]',
        "zami_group_membership": '[name="gp"]',
        "zami_total_members": '[name="gp_f"]',
    },
    # Her aktarimda ayni girilen sabit degerler
    "constants": {
        '[name="ss"]': "dubai",
        '[name="dr_op"]': "Normal",
        '[name="e_vr"]': "Tourism",
        '[name="cc_tt"]': "TURKEY",
        '[name="e_cy_tt"]': "TURKEY",
        '[name="ls"]': "Turkish",
        # Bilmedigimiz bilgiler icin portalin sundugu durust secenek
        '[name="ms"]': "Unknown",
        '[name="rg"]': "Unknown",
    },
    # Yolcu bazli alanlar (Zami formu tek yolcu esasli calisir; ilk yolcu)
    "traveler_fields": {
        "first_name": '[name="fn"]',
        "last_name": '[name="ln"]',
        "passport_no": '[name="pn"]',
        "birth_date_dmy_dash": '[name="bd"]',
        "passport_expiry_dmy_dash": '[name="pe"]',
        "passport_issue_date_dmy_dash": '[name="pd"]',
        "birth_place": '[name="bp"]',
        "passport_issue_place": '[name="pp"]',
        "gender_en": '[name="gn"]',
        "nationality_label": '[name="nt_tt"]',
        "passport_country_label": '[name="pc_tt"]',
        "zami_visa_type": '[name="dr_tp"]',
    },
    "status_url": "https://visa.zamitours.ae/?_=203&s=vs.search&_p_st=1",
    "status_search_selector": "",
    "status_result_selector": "",
    "auto_check_enabled": False,
    "auto_check_hours": 6,
    "auto_notify": True,
}


async def main() -> None:
    saved = await zami.save_mapping(MAPPING)
    print("Kaydedilen mapping:")
    print(json.dumps(saved, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    asyncio.run(main())
