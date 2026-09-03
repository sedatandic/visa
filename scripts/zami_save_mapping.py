"""Zami 'New Visa Request (Dubai)' formu icin gercek alan eslemesini kaydeder.

Alan adlari 03.09.2026'da canli portaldan yakalanmistir (84 alan).
Bu dosya alan eslemesinin KAYNAGIDIR: mapping bozulursa yeniden calistirilir.
Portalda zorunlu olup bizde bulunmayan alanlar (Egitim, ucus bilgileri)
operator tarafindan doldurulur.
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
        "contact.phone_intl": '[name="mp"]',
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
        # Basvuru formunda kullaniciya sorulan zorunlu Zami alanlari
        "marital_status_label": '[name="ms"]',
        "profession": '[name="pf_tt"]',
        "mother_name": '[name="mo"]',
        "father_name": '[name="fa"]',
    },
    "status_url": "https://visa.zamitours.ae/?_=203&s=vs.search",
    "status_search_selector": '[name="pn"]',
    "status_search_field": "passport",
    "status_submit_selector": 'button:has-text("SEARCH")',
    # Formu gondermeden once Zami'nin kendi dogrulamasini tetikler
    "validate_selector": 'button:has-text("CHECK")',
    "helper_selectors": ['button:has-text("TRANSLATE TO ARABIC")'],
    "upload_targets": [
        {"doc": "passport", "selector": 'div.img-editor:has-text("Main Passport Page")'},
        {"doc": "photo", "selector": 'div.img-editor:has-text("Personal Photo")'},
    ],
    "status_result_selector": "",
    # 6 saatte bir otomatik durum kontrolu ve musteriye bildirim
    "auto_check_enabled": True,
    "auto_check_hours": 6,
    "auto_notify": True,
}


async def main() -> None:
    saved = await zami.save_mapping(MAPPING)
    print("Kaydedilen mapping:")
    print(json.dumps(saved, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    asyncio.run(main())
