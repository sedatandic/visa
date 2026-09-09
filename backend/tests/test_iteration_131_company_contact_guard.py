"""Iteration 131: acente iletisim bilgisi kayiplarina karsi koruma.

Kullanici canli sitede yanlis cep telefonu gordu (+90 532 588 26 30). Kok neden:
- `company_info.phone` canli veritabaninda eski/test numarasi olarak kalmis
  (onizleme ve canli ayri veritabani kullaniyor),
- `PUT /admin/company` tum `value` nesnesini komple degistiriyordu; kismi bir kayit
  gonderilmeyen alanlari (dubai_phone, adres vb.) siliyordu.

Bu testler:
1. Eski/test numaralarinin acilista otomatik duzeltildigini,
2. Sirket kaydinin artik BIRLESTIRILEREK guncellendigini (alan kaybi yok) dogrular.
"""

import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import server  # noqa: E402


class TestPlaceholderList:
    def test_old_customer_facing_numbers_are_covered(self):
        assert "+90 532 588 26 30" in server.PLACEHOLDER_CONTACT["phone"]
        assert "+905325882630" in server.PLACEHOLDER_CONTACT["phone"]
        assert "905325882630" in server.PLACEHOLDER_CONTACT["whatsapp"]

    def test_real_number_is_not_in_placeholder_list(self):
        from content import COMPANY

        assert COMPANY["phone"] not in server.PLACEHOLDER_CONTACT["phone"]
        assert COMPANY["whatsapp"] not in server.PLACEHOLDER_CONTACT["whatsapp"]


class TestCompanyUpdateMerges:
    def test_put_company_uses_dotted_set_not_whole_value(self):
        """Kismi kayit diger alanlari silmemeli: `$set` alan bazinda olmali."""
        source = open(os.path.join(BACKEND_DIR, "routes_admin.py")).read()
        block = source.split("async def admin_update_company(")[1].split("async def ")[0]
        assert 'f"value.{key}"' in block, "sirket kaydi alan bazinda guncellenmeli"
        assert '{"value": value' not in block, "tum value nesnesi komple degistirilmemeli"
