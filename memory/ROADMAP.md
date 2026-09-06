# ROADMAP (2026-06-11 itibarıyla · WhatsApp AI paneli sonrası)

## P0 — Acil
- [x] ~~E-posta gönderimi kapalı~~ → 2026-06-11: kullanıcı tam yetkili Resend anahtarı verdi,
      `dubaivizehatti.com` doğrulanmış; gerçek gönderim testi `status=sent` (iteration_98).
- [ ] **WhatsApp canlı moda geçiş**: Meta Developer App açılıp `phone_number_id`,
      `access_token`, `app_secret`, `verify_token` Admin → WhatsApp → Bot Ayarları'ndan
      girilmeli; webhook adresi `{BACKEND_URL}/api/whatsapp/webhook`. Şu an simülasyon modu.

## P0 — Kullanıcıdan bekleyen içerik
- [ ] **Gerçek IBAN'lar**: `/vize-tipleri` ve ödeme adımındaki 3 banka kartında IBAN'lar hâlâ
      yer tutucu (`TR00 0000 …`). Admin → Banka sekmesinden gerçek TL/USD IBAN'lar girilecek.
- [ ] **Şirket unvanı**: iştirak cümlesindeki "XXXX Travel Solutions Turizm Ltd. Şti." ve
      "XXXX Travel Solutions FZE" yer tutucu; Admin → Acente Bilgileri'nden güncellenecek.
- [ ] **TÜRSAB belge numarası** hâlâ boş/placeholder (`tursab_no`), Instagram ve Google yorum
      linkleri kontrol edilmeli.
- [ ] Sigorta poliçesini düzenleyen sigorta şirketi adı sayfada belirtilmiyor (istenirse eklenir).

## P1
- [ ] Sepette misafir kullanıcı için "siparişimi takip et" kısayolu + sipariş e-postasına
      sepet linki (turlar ve hazır paket sepete ekleme 2026-06-10'da tamamlandı).
- [ ] WhatsApp panelinde bekleyen belge/temsilci sayısı için admin ana sayfasında bildirim
      sayacı (şu an yalnız WhatsApp sekmesinde görülüyor).
- [ ] Barchart kuru gerçekten istenirse: headless Chromium ile günlük tek çekim denenebilir;
      Cloudflare engeli sürerse ücretli Barchart OnDemand API şart.
- [ ] Fiyat/politika tutarlılığı: resmî harç ile hizmet bedeli ayrımı, TL ödemede kur
      açıklaması, vizeden sonra 60 gün içinde giriş şartı, yeşil/gri pasaportta 90 gün
      vizesiz giriş, uzatmanın en fazla 2 kez yapılabilmesi, vize iptal ücreti.
- [ ] `email_outbox` eski kayıtlarında HTML gövdesi yok → yalnız 2026-06-08 sonrası önizlenebilir.
- [ ] Tarihi belli olmayan başvurular için "tarihim belli oldu" hatırlatma e-postası.
- [ ] Grup/aile başvurusunda yolcu bazlı evrak eksikliği özeti.
- [ ] Ziyaretçi analitiği: günlük grafik, tarih aralığı seçimi ve CSV dışa aktarma.

## P2
- [ ] Eski test dosyalarındaki katalog beklentileri güncellenmeli: `test_visa_categories.py`,
      `test_tour_safari.py`, `test_iteration_48.py::TestVisaPrices`, `test_zami_otp_fix.py`.
- [ ] `backend_test.py` içindeki çok uzun test fonksiyonlarının bölünmesi.
- [ ] `is` / `==` karşılaştırma anti-pattern temizliği (`zami_status.py`, `whatsapp.py`,
      `routes_public.py`).
- [ ] Hız sınırları bellek içi; çoklu replikada Redis'e taşınmalı.
- [ ] Fotoğraf arka plan eşikleri admin panelinden ayarlanabilir olabilir.

## Beklemede — Global İngilizce sürüm (kullanıcı kararı bekliyor, 2026-06-09)
Kullanıcı: "later we will decide like global english only version targeting all passport
holders in all countries" → ŞİMDİ YAPILMAYACAK. Karar verildiğinde kapsam:
- Tek dil **İngilizce** (TR/EN switcher değil): tüm müşteri sayfaları, sihirbaz, e-postalar,
  dinamik DB içeriği (vize tipleri, rehberler, blog, yorumlar, banka etiketleri).
- Hedef kitle **tüm ülke pasaportları** → mevcut kısıtlar kaldırılmalı: yalnız Türkiye doğumlu
  kabul eden kural (`routes_public._validate_travel_rules` + `Apply.jsx` birth_country),
  `+90 5XX` telefon maskesi, fiyatlarda birincil para birimi USD (₺ ikincil).
- Ana sayfadaki anlatım: İngilizce seslendirme + altyazı; illüstrasyonlardaki Türkçe yazılar
  ("TÜRKİYE CUMHURİYETİ", "GEREK YOK") yenilenmeli.
- Yönetici paneli Türkçe kalabilir. KVKK/yasal metinlerin İngilizce karşılıkları hukuki
  kontrol gerektirir.
