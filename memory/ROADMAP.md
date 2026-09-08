# ROADMAP (2026-09-08 itibarıyla · SEO denetim düzeltmeleri sonrası)

## P0 — Kullanıcı eylemi (SEO + güvenlik düzeltmelerinin canlıya yansıması için)
- [ ] **Yeniden deploy**: statik ön-render (`scripts/prerender.js`) ve güvenlik düzeltmeleri
      (hız sınırları, güvenlik başlıkları, /docs kapatma, PDF kaçışı) yalnız yeni deploy
      sonrası canlıda geçerli olur.
- [ ] **301 yönlendirme**: `dubaivizehatti.com` → `www.dubaivizehatti.com` (şu an iki host da
      200 dönüyor; 89 taranan sayfanın yarısı bu yüzden kopya). Alan adı/hosting panelinden.
- [ ] **Search Console**: `https://www.dubaivizehatti.com/sitemap.xml` yeniden gönderilmeli
      (sitemap artık build sırasında üretiliyor, 30 URL, 404 veren transit rehberi çıkarıldı).

## P0 — Acil
- [ ] **Tamamliyo 220 ürün kodu** (2026-09-08: panelde "Ürün kodu satışa açık mı?" butonu
      eklendi — Admin → Sigorta Poliçeleri → kod gir → "Kodu sorgula". 220 hâlâ kapalı:
      "Fiyat bulunamadı … 758". Açıldığında `.env` → `TAMAMLIYO_URUN_ID=220` + restart.)
- [ ] **Eski madde**: sağlayıcı "her sigorta alımında 220 kullanın" dedi ama
      `fiyat-al` 220 için "Fiyat bulunamadı ... 758" dönüyor (141/185/189 çalışıyor, 220
      `urun-kodlari` listesinde de yok). Kullanıcı Tamamliyo'dan ürünün partner hesabına
      tanımlanmasını isteyecek. Açıldığında: `backend/.env` → `TAMAMLIYO_URUN_ID=220` +
      backend restart + fiyat senkronu (kod hazır, 2026-09-08).
- [ ] **İlk gerçek test poliçesi**: kart hazır (**** 1028), otomatik kesim açık; kullanıcı
      isteğiyle **220 açılana kadar ertelendi**. Kesim sırasında gereken: sigortalının gerçek
      TCKN + doğum tarihi + ad soyad (MERNIS doğrulaması).
- [x] ~~Tamamliyo cari bakiyesi / elle ilk kesim~~ → 2026-09-08: ödeme kurumsal karta
      taşındı (odemeTipi=2), kart tanımlı (**** 1028), otomatik poliçe kesimi AÇIK,
      kâr koruması devrede. Kalan tek engel 220 ürün kodunun açılması.
- [ ] **WhatsApp numarası teyidi**: telefon +90 533 743 82 24 olarak güncellendi ve WhatsApp
      linki de bu numaraya alındı; numaranın WhatsApp'ta açık olduğu kullanıcıdan teyit edilmeli.
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
- [x] ~~Başvuru formu PDF'i + evrak ekleri~~ → 2026-09-07: başvuru alındığında müşteriye ve
      sisteme tek sayfalık form PDF'i + yüklenen tüm evraklar ek olarak gidiyor;
      `/takip` ve yönetici detayında "Başvuru formu (PDF)" indirme butonu var.
- [ ] Ödeme alındığında (kart/havale onayı) güncel form PDF'inin ikinci kez eklenmesi (P2 tercih
      edilebilir; şu an yalnız başvuru anında gönderiliyor).
- [x] ~~Sepette misafir "siparişimi takip et" kısayolu + sipariş e-postasına takip linki~~
      → 2026-06-12 tamamlandı (`cart-last-order-shortcut`, `/siparis/{kod}?email=`,
      e-postalarda "Siparişimi takip et" butonu).
- [x] ~~WhatsApp bekleyen belge/temsilci sayacı~~ → 2026-06-12: admin menüsünde rozet
      (Mesajlar + WhatsApp) ve Başvurular sayfasında uyarı bandı.
- [x] ~~Kur kaynağı~~ → 2026-09-07: kullanıcı isteğiyle **TCMB günlük bülteni (USD döviz
      satış)** birincil kaynak oldu (`fx.py`, bülten tarihine göre günlük tazeleme).
      Barchart/Cloudflare denemesi gerekmedi.
- [ ] Fiyat/politika tutarlılığı: resmî harç ile hizmet bedeli ayrımı, TL ödemede kur
      açıklaması, vizeden sonra 60 gün içinde giriş şartı, yeşil/gri pasaportta 90 gün
      vizesiz giriş, uzatmanın en fazla 2 kez yapılabilmesi, vize iptal ücreti.
- [ ] `email_outbox` eski kayıtlarında HTML gövdesi yok → yalnız 2026-06-08 sonrası önizlenebilir.
- [ ] Tarihi belli olmayan başvurular için "tarihim belli oldu" hatırlatma e-postası.
- [ ] Grup/aile başvurusunda yolcu bazlı evrak eksikliği özeti.
- [ ] Ziyaretçi analitiği: günlük grafik, tarih aralığı seçimi ve CSV dışa aktarma.

- [x] ~~Zami RPA form doldurma sadeleştirmesi~~ → 2026-06-13: `fill_application` içindeki
      `set_value` closure'ı `_FieldSetter` sınıfına, akış `_fill_precondition_error` /
      `traveler_selector` / `_fill_mapped_fields` / `_run_helper_clicks` adımlarına bölündü.
      143 → 90 satır, C901 düştü, 32 birim testi (`test_iteration_117_zami_fill_steps.py`).

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
