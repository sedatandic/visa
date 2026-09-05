# ROADMAP (2026-06-10 itibarıyla)

## P0 — Kullanıcıdan bekleyen içerik- [ ] **Gerçek IBAN'lar**: `/vize-tipleri` ve ödeme adımındaki 3 banka kartında IBAN'lar hâlâ
      yer tutucu (`TR00 0000 …`). Admin → Banka sekmesinden gerçek TL/USD IBAN'lar girilecek.
      Banka listesi de değiştirilebilir (İş Bankası / Garanti BBVA / Ziraat varsayılan).
- [ ] **Şirket unvanı**: iştirak cümlesindeki "XXXX Travel Solutions Turizm Ltd. Şti." ve
      "XXXX Travel Solutions FZE" kullanıcı isteğiyle yer tutucu. Gerçek unvan verildiğinde
      Admin → Acente Bilgileri'ndeki yeni alanlardan (bağlı şirket / Dubai şirketi) güncellenecek.
- [ ] **TÜRSAB belge numarası** hâlâ boş/placeholder (`tursab_no`), Instagram ve Google yorum
      linkleri kontrol edilmeli.
- [ ] Sigorta poliçesini düzenleyen sigorta şirketi adı sayfada belirtilmiyor (istenirse eklenir).

## P1
- [ ] Fiyat/politika tutarlılığı: rakip içerikte olup bizde olmayan başlıklar — resmî harç ile
      hizmet bedeli ayrımı, TL ödemede kur açıklaması, vize alındıktan sonra 60 gün içinde giriş
      şartı, yeşil/gri/diplomatik pasaportta 90 gün vizesiz giriş, uzatmanın en fazla 2 kez
      yapılabilmesi, vize iptal ücreti kalemi, "kendiniz mi acenteyle mi başvurmalısınız"
      karşılaştırması. Ekspres ücreti (50$) ve standart süre (2 iş günü) teyit edilmeli.
- [ ] `/api/files/{file_id}` kimlik doğrulaması yok (SEC-003) → imzalı/süreli token.
- [ ] `email_outbox` eski kayıtlarında HTML gövdesi yok → yalnız 2026-06-08 sonrası önizlenebilir.
- [ ] Tarihi belli olmayan başvurular için "tarihim belli oldu" hatırlatma e-postası.
- [ ] Grup/aile başvurusunda yolcu bazlı evrak eksikliği özeti.
- [ ] Ziyaretçi analitiği: günlük grafik, tarih aralığı seçimi ve CSV dışa aktarma eklenebilir.

## P2
- [ ] Eski test dosyalarındaki katalog beklentileri güncellenmeli: `test_visa_categories.py`,
      `test_tour_safari.py`, `test_iteration_48.py::TestVisaPrices`, `test_zami_otp_fix.py`.
- [ ] `backend_test.py` içindeki çok uzun test fonksiyonlarının bölünmesi.
- [ ] `is` / `==` karşılaştırma anti-pattern temizliği (`zami_status.py`, `whatsapp.py`,
      `routes_public.py`).
- [ ] Hız sınırları bellek içi; çoklu replikada Redis'e taşınmalı.
- [ ] Fotoğraf arka plan eşikleri admin panelinden ayarlanabilir olabilir.
