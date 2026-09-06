# ROADMAP (2026-06-10 itibarıyla · sepet turu sonrası)

## P0 — Acil
- [ ] **E-posta gönderimi kapalı**: Resend'de `dubaivizehatti.com` domaini doğrulanmalı ve
      `SENDER_EMAIL` bu domaine geçmeli (şu an tüm e-postalar "domain is not verified"
      hatası alıyor: giriş kodu, sipariş bildirimi, sepet hatırlatma).

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
- [ ] Sepette misafir kullanıcı için "siparişimi takip et" kısayolu + sipariş e-postasına
      sepet linki (turlar ve hazır paket sepete ekleme 2026-06-10'da tamamlandı).
- [ ] Barchart kuru gerçekten istenirse: headless Chromium (playwright install chromium) ile
      günlük tek çekim denenebilir; Cloudflare engeli sürerse ücretli Barchart OnDemand API şart.
- [ ] Fiyat/politika tutarlılığı: rakip içerikte olup bizde olmayan başlıklar — resmî harç ile
      hizmet bedeli ayrımı, TL ödemede kur açıklaması, vize alındıktan sonra 60 gün içinde giriş
      şartı, yeşil/gri/diplomatik pasaportta 90 gün vizesiz giriş, uzatmanın en fazla 2 kez
      yapılabilmesi, vize iptal ücreti kalemi, "kendiniz mi acenteyle mi başvurmalısınız"
      karşılaştırması. Ekspres ücreti (50$) ve standart süre (2 iş günü) teyit edilmeli.
- [x] ~~`/api/files/{file_id}` kimlik doğrulaması yok (SEC-003)~~ → 2026-06-09'da imzalı/süreli
      jeton (`file_access.py`) ile kapatıldı; jetonsuz erişim 403.
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

## Beklemede — Global İngilizce sürüm (kullanıcı kararı bekliyor, 2026-06-09)
Kullanıcı: "later we will decide like global english only version targeting all passport
holders in all countries" → ŞİMDİ YAPILMAYACAK. Karar verildiğinde kapsam:
- Tek dil **İngilizce** (TR/EN switcher değil): tüm müşteri sayfaları, sihirbaz, e-postalar,
  dinamik DB içeriği (vize tipleri, 7 rehber, blog, yorumlar, banka etiketleri).
- Hedef kitle **tüm ülke pasaportları** → mevcut kısıtlar kaldırılmalı: yalnız Türkiye doğumlu
  kabul eden kural (`routes_public._validate_travel_rules` + `Apply.jsx` birth_country),
  `+90 5XX` telefon maskesi (uluslararası ülke kodu seçimi), fiyatlarda birincil para birimi
  USD (₺ ikincil), ülkeye göre vize uygunluğu/ücret farkları araştırılmalı.
- Ana sayfadaki 75 sn'lik anlatım: İngilizce seslendirme (ElevenLabs İngilizce ses) +
  İngilizce altyazı; illüstrasyonlarda Türkçe yazılar ("TÜRKİYE CUMHURİYETİ", "GEREK YOK")
  yenilenmeli. Türk pasaportu görselleri jenerik pasaportla değiştirilmeli.
- Yönetici paneli Türkçe kalabilir (kararlaştırılacak). KVKK/yasal metinlerin İngilizce
  karşılıkları hukuki kontrol gerektirir.
