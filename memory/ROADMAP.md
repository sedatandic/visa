# ROADMAP (2026-06-09 itibarıyla)

## P0 — Kullanıcıdan bekleyen içerik
- [ ] Gerçek havale/IBAN bilgileri (şu an örnek: "VizeAtlas Turizm" / "Örnek Bank" / TR00...)
      → Admin → Banka sekmesinden girilecek.
- [ ] Gerçek WhatsApp numarası + Instagram / Google yorum linkleri (şu an test: 905331234567).

## P1
- [ ] `/api/files/{file_id}` kimlik doğrulaması yok (SEC-003). Dosya kimlikleri uuid4 olduğu için
      tahmin edilemez ("capability URL"), ancak e-posta linklerini bozmadan imzalı/süreli token'a
      geçirmek daha güvenli olur.
- [ ] `email_outbox` eski kayıtlarında HTML gövdesi yok → yalnız 2026-06-08 sonrası önizlenebilir.
- [ ] Tarihi belli olmayan başvurular için "tarihim belli oldu" hatırlatma e-postası.
- [ ] Grup/aile başvurusunda yolcu bazlı evrak eksikliği özeti (kim hangi belgeyi yüklemedi).
- [ ] Fotoğraf rehberi Gerekli Belgeler sayfasına da eklenebilir (şu an yalnız başvuru Adım 3).

## P2
- [ ] Eski test dosyalarındaki katalog beklentileri güncellenmeli: `test_visa_categories.py`,
      `test_tour_safari.py`, `test_iteration_48.py::TestVisaPrices`,
      `test_zami_otp_fix.py::test_visa_types` (kaldırılan transit vize, ikinci tur ürünü).
- [ ] `backend_test.py` içindeki çok uzun test fonksiyonlarının bölünmesi.
- [ ] `is` / `==` karşılaştırma anti-pattern temizliği (`zami_status.py`, `whatsapp.py`,
      `routes_public.py`).
- [ ] Hız sınırları bellek içi; birden fazla replikaya çıkılırsa Redis'e taşınmalı.
- [ ] Fotoğraf arka plan eşikleri (beyaz oranı/parlaklık/std) admin panelinden ayarlanabilir olabilir.
