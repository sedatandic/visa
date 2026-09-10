"""Iteration 141: Dubai ofis bilgileri sitede kaybolmasin.

Kullanici: "dubai adres bilgilerini goster sitede". Kok neden: `CompanyInfoIn` alanlarinin
varsayilani `""` oldugu icin KISMI bir `PUT /admin/company` cagrisi gonderilmeyen tum
alanlari bos string olarak yaziyordu (dubai_address / dubai_phone silinip footer ve
iletisim sayfasindaki Dubai ofis karti gizleniyordu). Artik:
- gonderilmeyen alanlar `None` kalir ve kayitta korunur,
- okuma yolunda bos kalan ofis alanlari statik varsayilanla doldurulur.
"""

import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from content import ALWAYS_FILLED, COMPANY, company_with_defaults
from models import CompanyInfoIn


class TestKismiKayit:
    def test_gonderilmeyen_alanlar_none_kalir(self):
        payload = CompanyInfoIn(legal_name="Moruya Travel Solutions Turizm Ltd. Şti.")
        data = payload.model_dump()
        assert data["dubai_address"] is None
        assert data["dubai_phone"] is None
        # route filtresi None alanlari yazmaz -> mevcut deger korunur
        assert {k: v for k, v in data.items() if v is not None} == {
            "legal_name": "Moruya Travel Solutions Turizm Ltd. Şti."
        }

    def test_bos_string_bilincli_silmedir(self):
        data = CompanyInfoIn(legal_name="Moruya Travel", dubai_phone="").model_dump()
        assert data["dubai_phone"] == ""


class TestOfisAlanlariniDoldurma:
    def test_bos_dubai_alanlari_varsayilanla_dolar(self):
        company = company_with_defaults({"dubai_address": "", "dubai_phone": "   "})
        for field in ALWAYS_FILLED:
            assert company[field] == COMPANY[field]

    def test_panelde_girilen_deger_korunur(self):
        company = company_with_defaults({"dubai_address": "Business Bay Tower, Dubai"})
        assert company["dubai_address"] == "Business Bay Tower, Dubai"
        assert company["dubai_phone"] == COMPANY["dubai_phone"]

    def test_kayit_yoksa_sabitler_donuyor(self):
        assert company_with_defaults(None)["dubai_address"] == COMPANY["dubai_address"]

    def test_diger_alanlar_bos_birakilabilir(self):
        """Yasal kunye alanlari bilincli olarak bos kalabilir (sitede gizleniyor)."""
        company = company_with_defaults({"tursab_no": "", "tax_no": ""})
        assert company["tursab_no"] == ""
        assert company["tax_no"] == ""
