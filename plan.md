# plan.md

## 1. Objectives
- Türkçe, modern, **sade** ve güven veren bir Dubai/UAE vize başvuru sitesi (özgün marka/renk; kopya UX değil).
- Vize tipleri + fiyatlar + genel bilgilendirme + **rehber içerikler** + hızlı başvuru akışı.
- Çekirdek iş akışı: **başvuru oluşturma → dosya yükleme → ödeme (kart / havale) → takip kodu**.
- Başvuruları MongoDB’ye kaydetme, admin panelde listeleme/detay/güncelleme.

- Bildirimler:
  - **E-posta bildirimleri (Resend)**:
    - Resend entegrasyonu canlı (API anahtarı bağlı) ve outbox kayıtları admin panelde görünür.
    - **Kritik kısıt:** Gönderici `onboarding@resend.dev` (sandbox) ise Resend sadece hesap sahibine mail atar; müşteri mailleri “error” olur ama akış bozulmaz (graceful degradation).
    - Hedef: Resend’de **domain doğrulaması** + `SENDER_EMAIL=noreply@dubaivizeonline.com` ile gerçek müşteri e-postalarını üretime almak.
  - WhatsApp bildirimleri:
    - **Manuel mod** (wa.me link üretimi) tamam.
    - Otomatik sağlayıcı (Twilio/Meta) **beklemede** (API anahtarları yok).

- Güven ve “insan eliyle tasarlanmış” kurumsal görünüm:
  - **Tema logo bazlı:** petrol teal + bakır/bronz + royal mavi + kum beyazı.
  - Kırmızı yalnızca **destructive/hata** semantiğinde (silme, reddedildi) kullanılır.
  - **Tipografi güncellendi:** başlık/marka fontu **Tinos** (Times ailesi; logoyla metrik uyumlu), gövde **Figtree**, mono **Roboto Mono**.
  - “AI hissi” azaltma:
    - Public UI’da **parıltı/Sparkles ikonları kaldırıldı** (anlamsız süs yerine anlamlı ikonlar).
    - Premium tasarım sistemi dokunuşları: radius ölçeği, tipografik ince ayarlar (balance/pretty + lining-nums), mikro-etkileşimler, grain doku.
  - Gerçek görseller / kurumsal bloklar / sosyal kanıt / örnek vize görselleri.
  - **TÜRSAB + acente şeffaflığı** ve **GDRFA rozeti**.
  - Not: Kullanıcının paylaştığı `onyuz-rehberi.pdf` bir **Stitch/Dribbble iş akışı rehberi**; bu ortamda Stitch/MCP erişimi yok. “AI hissini kıran” tasarım için **kullanıcıdan Dribbble/Stitch referansı** bekleniyor.

- **Başvuru evrak standardı (güncel)**:
  - **Her yolcu:** Pasaport + vesikalık fotoğraf.
  - **Tüm başvuru:** Uçak bileti/rezervasyon + otel/konaklama rezervasyonu (**opsiyonel yükleme**; formda soru olarak sorulmaz).

- SEO büyüme hedefi (tamamlandı): vize rehber sayfaları, sitemap/robots, JSON-LD.
- Operasyonel verim + dönüşüm (tamamlandı): eksik belge hatırlatma, taslak hatırlatma, hesap/draft, aile profili.
- Fiyatlandırma (tamamlandı): USD baz fiyat + canlı kurla TL tahsilat + kur şeffaflığı.

- Ek ürün satışları (tamamlandı):
  - Mağaza sayfaları üzerinden **eSIM** ve **seyahat sigortası** satışı.
  - Vize başvurusu içinde eSIM + sigorta upsell (tek formda).
  - Ek ürünler seyahat tarihine bağlandı (başlangıç/bitiş).
  - **Akıllı paket önerisi** + **%10 seyahat paketi indirimi** (sigorta+eSIM birlikte) hem başvuruda hem mağazada.

- AI destekli otomasyon (tamamlandı):
  - **Pasaport OCR** (Adım 1’de “Pasaportla Tek Adım”).
  - **Fotoğraf Kontrolü** (AI vesikalık doğrulama) uyarı bazlı, başvuruyu engellemez.

- Zami Tours otomasyonu (tamamlandı, üretim hazır):
  - Playwright RPA + yakalama (capture) + alan eşleme + toplu aktarım + durum polling + kullanıcı takip zaman çizelgesi.
  - **Zami zorunlu alanlar tamamlandı:** Medeni hal, meslek, anne adı, baba adı başvuruda toplanıyor ve RPA ile dolduruluyor.
  - **Kritik sağlamlık:** Zami mapping’in admin panelden kaydedilince veri kaybetmesi bug’ı düzeltildi; mapping artık kayıpsız korunur.
  - Operasyon notu: Zami RPA oturumu OTP’ye bağlı olduğu için zaman zaman düşebilir; admin panelden yeniden oturum açma + OTP gerekebilir.

- Hosting/Deploy hedefi:
  - **Paylaşımlı cPanel/PHP hosting alınmayacak.** (Uygulama Python/FastAPI + Playwright + MongoDB gerektirir.)
  - Kullanıcı yalnızca **Domain (Alan Adı)** satın alır; uygulama Emergent altyapısında barınır; domain sonrası DNS yönlendirme yapılır.

---

## 2. Implementation Steps

### Phase 1 — Core POC (Tamamlandı)
**Amaç:** En riskli entegrasyonları tek dosyada uçtan uca doğrulamak.

---

### Phase 2 — V1 App Development (Tamamlandı)
**Frontend:** React + router + Tailwind + shadcn/ui. **Backend:** FastAPI `/api` + Motor + servisler.

---

### Phase 3 — Aile Başvurusu + Admin Vize PDF (Tamamlandı)

---

### Phase 4 — Marka/Tema Yenileme + Sosyal Kanıt (Tamamlandı)

---

### Phase 5 — Operasyonel içerik yönetimi + SEO Blog + WhatsApp + AI Pasaport Okuma (Tamamlandı)

---

### Phase 6 — Rakip boşluk kapatma + Havale/EFT + Yasal sayfalar + Dribbble Hero (Tamamlandı)

---

### Phase 7 — Ürün sadeleştirme + Admin banka/acente yönetimi + UX düzeltmeleri (Tamamlandı)

---

### Phase 8 — Kod Kalitesi + Güvenlik Sertleştirme (Tamamlandı)

---

### Phase 9 — Güven Şeridi + GDRFA Referansı (Tamamlandı)

---

### Phase 10 — Vize Rehberi SEO Sayfaları (Tamamlandı)
- Backend: `/api/visa-guides`, `/api/visa-guides/{slug}`
- Frontend: `VisaGuide.jsx`, route `/dubai-vizesi/:slug`
- SEO: JSON-LD + sitemap + robots

---

### Phase 11 — Zorunlu Seyahat Belgeleri + Kart Tıklama Davranışı (Tamamlandı)
- Kart gövde tıklaması başvuruya yönlendirmez (sadece buton/link)
- Not: Seyahat belgeleri artık form sorusu değil, opsiyonel belge yükleme.

---

### Phase 12 — Eksik Belge Hatırlatma Otomasyonu + Rehber İçerik Yönetimi (Tamamlandı)

---

### Phase 13 — Müşteri Hesabı + Taslak (Tamamlandı)

---

### Phase 14 — USD Bazlı Fiyat + Canlı Kur (Tamamlandı)

---

### Phase 15 — Kur Şeffaflığı + Sepeti Kurtarma + Aile Profili (Tamamlandı)

---

### Phase 16 — eSIM + Seyahat Sigortası Mağazası (Tamamlandı)
**Durum:** Standalone mağaza akışı üretimde.
- `/esim`, `/seyahat-sigortasi`, `/siparis/:reference`
- Admin sipariş yönetimi + teslim (eSIM QR / poliçe PDF)

---

### Phase 17 — Vize Başvurusu İçinde eSIM + Sigorta Upsell — **COMPLETED (2026-08-31)**
- Backend: `StoreItemIn` + `store_items` (quote & application), `compute_pricing(store_lines=...)`, `resolve_store_lines()`, `create_application_order()` (source=visa_application), `sync_application_order_payment()` (kart/havale/admin mark-paid).
- Frontend: `Apply.jsx` adım 2'de sigorta planı + eSIM paketleri; özet + canlı FX toplam.
- Admin: AdminOrders’da “Vize başvurusu ile alındı” etiketi; AdminApplicationDetail’de store satırları + bağlı sipariş kodu.

---

### Phase 18 — Ek Ürün Geçerlilik Tarihlerinin Seyahat Tarihine Bağlanması — **COMPLETED (2026-08-31)**
- Backend: `resolve_store_lines(items, arrival_date, departure_date)` → satırlarda `validity_days`, `starts_on`, `ends_on`, `trip_days`, `covers_trip`.
- Frontend: giriş tarihi yoksa seçim kapalı; kartlarda geçerlilik penceresi ve uyarılar; özet satırlarında tarih aralığı.

---

### Phase 19 — Akıllı Paket Önerisi + %10 Seyahat Paketi İndirimi — **COMPLETED (2026-08-31)**
- Backend: `bundle_discount_amount()`, `compute_pricing` indirim satırları, store order & bağlı order indirimli fiyat, e-posta satırları.
- Frontend: `Apply.jsx` promosyon kutusu + önerilen etiketler; `StoreCheckout.jsx` çapraz satış; OrderStatus/Admin ekranlarında indirim/tarih gösterimi.

---

### Phase 20 — Zami Tours Portalına Başvuru Aktarımı (visa.zamitours.ae) — **COMPLETED (2026-09-01) / LIVE VERIFIED (2026-09-03)**
Engel: girişte resimli CAPTCHA + OTP var → tam otomatik login sınırlı.
- **A) Tarayıcı yardımcısı (bookmarklet)**
  - `GET /api/zami/bookmarklet.js` (BASE’i `currentScript.src`’den alır).
  - Admin başvuru detayında “Aktarım kodu oluştur” → 45 dk tek kullanımlık token.
  - Zami formunda bookmarklet çalıştır → token gir → alanlar mapping’e göre dolar; dosyalar için indirme linkleri listelenir.
- **B) Robot oturumu (Playwright RPA)**
  - Oturum `storage_state` ile saklanır; transfer “dry-run” ile screenshot döndürebilir.
  - Kritik: Playwright chromium yolu `/usr/local/bin/browser-use-chromium` korunur.
- **Admin alan eşleme ekranı (`/admin/zami`)**
  - HTML yapıştırma + yakalama (capture) ile field listesi.
  - Genel + yolcu alanlarında `{i}` şablonu (multi-passenger).
  - Mapping hem bookmarklet hem RPA tarafından ortak kullanılır.

---

### Phase 21 — Toplu Aktarım + Otomatik Durum Takibi — **COMPLETED (2026-09-01)**
- Toplu aktarım API + admin UI.
- Otomatik status polling (`zami_status.py`) → bizim status’e çevirme + status_history + e-posta tetikleme.

---

### Phase 22 — Alan Eşlemesi Otomasyonu (yakalama + otomatik öneri) — **COMPLETED (2026-09-01)**
- `GET /api/zami/capture.js` capture endpoint’e gönderir.
- `zami.suggest_mapping()` öneri çıkarır; `{i}` şablonlaştırır.

---

### Phase 23 — Müşteri Durum Ekranı + Aktarım Hazırlık Kontrolü — **COMPLETED (2026-09-01)**
- `build_customer_timeline()` 5 adımlı görsel takip akışı.
- `GET /api/admin/zami/readiness` ile mapping/oturum/tarayıcı/durum sayfası kontrolleri.

---

### Phase 24 — WhatsApp Bildirimleri (Manuel Mod) + Admin Ayarları — **COMPLETED (2026-09-01)**
- Admin WhatsApp ayarları paneli.
- Durum değişimlerinde wa.me linki üreten manuel bildirim akışı.

---

### Phase 25 — Ücretsiz Ön Değerlendirme Sihirbazı — **KALDIRILDI (2026-09-02)**

---

### Phase 26 — Kod Kalitesi Refactoring (Rapor Maddeleri + Saf Fonksiyon İyileştirmeleri) — **COMPLETED (2026-09-03)**
**Amaç:** Karmaşıklığı düşürmek, test edilebilirliği artırmak, davranışı bozmadan refactor.

**Kapsam (tamamı kapatıldı)**
- `whatsapp.get_settings` (17 → 5)
- `whatsapp.notify_result` (17 → 8)
- `visa_delivery.fetch_visa_document` (15 → 5)
- `passport_ai.normalize_photo_result` (14 → 4) ve `normalize_result`
- `routes_zami`: `_base_url`, `zami_config`, `zami_candidates`
- `routes_public`: `get_site_content`, `_tracking_last_names`, `_apply_traveler_documents`
- `routes_admin.admin_send_visa`
- `content.compute_pricing` (11 → 6)
- `db.serialize_doc` tip-dispatch
- Testler: `backend_test.py` pythonic True/False
- Ek (raporda yoktu ama risksiz): `zami.save_mapping` ve `zami.build_payload` saf yardımcı fonksiyonlara bölündü; JSON çıktısı birebir aynı doğrulandı.

**Kalite/Tarama**
- Ruff: F632/E712/E711/F821/F401/F811: **All checks passed**
- Ortalama karmaşıklık: **A (≈4.2)**

**Bilinçli ertelenen borç (riskli / canlı OTP gerektirir)**
- `zami_rpa.fill_application` (44)
- `zami_rpa.check_status` (30)
- `zami_rpa._upload_documents` (13)

---

### Phase 39 — Kod Kalitesi Refactoring (3. Tur: Zami saf fonksiyonlar + login + reminders + status) — **COMPLETED (2026-09-03)**
Bu faz, yeni gelen “Code Quality Report” maddelerini doğrulayıp yalnızca **gerçek** sorunları kapattı.

**Raporun 2 “kritik” maddesi yanlış pozitif çıktı (DEĞİŞTİRİLMEDİ)**
1) `passport_ai.py:147` “number atanmadan kullanılabilir” → yanlış (except erken return). Ruff F821/F823 temiz.
2) “24 adet `is` literal karşılaştırma” → yanlış; hepsi `is None`/`is not None` (doğru idiom). Ruff F632 temiz.

**Gerçek karmaşıklık maddeleri kapatıldı**
- `zami.suggest_mapping` **28 → 9**
- `zami.parse_form_fields` **22 → 9**
- `zami_rpa.submit_login` **64 satır → 47 satır** (cc 6)
- `zami_rpa._click_first` iç içe **5 → 3** (cc 4)
- `doc_reminders.send_document_reminder` **51 → 25** (cc 5)
- `routes_public.check_photo_document` **51 → 33** (cc 7)
- Ek güvenli refactor: `zami_status.apply_status` **22 → 8**, `zami_status.sweep_statuses` **12 → 9**

**Davranış korunumu kanıtları**
- `/app/scripts/zami_pure_snapshot.py`: `parse_form_fields` + `suggest_mapping` refactor öncesi/sonrası JSON çıktısı **birebir aynı**.
- `POST /api/admin/zami/check-status-all`: `sweep_statuses` + `apply_status` zinciri canlı doğrulandı (oturum düşmüş olsa bile biçim ve erken çıkış mantığı korunuyor).

**Yakalanan ciddi hata ve önlem**
- Refactor sırasında `@router.post('/photo/check')` dekoratörünün private fonksiyona bağlanması hatası oluştu → tespit edilip düzeltildi.
- Tüm route dosyalarında dekoratör-fonksiyon eşleşmesi otomatik tarandı → başka sorun yok.

**Test**
- iteration_34: backend %97.4, 0 kritik bug, 0 UI bug.
- Bayat test düzeltmesi: `backend_test.py` bookmarklet içeriğinde eski marka adı arıyordu → `Dubai Vize Online` ile güncellendi.

---

### Phase 27 — Stitch Tarzı UI Yenilemesi — **COMPLETED (2026-09-02)**

---

### Phase 28 — Türkçe Tarih Seçici + Ana Sayfa Vitrini — **COMPLETED (2026-09-02)**

---

### Phase 29 — Şehir Alanı + Ön Değerlendirme Kaldırıldı — **COMPLETED (2026-09-02)**

---

### Phase 30 — Formu Kısaltma + Yorum Vitrini — **COMPLETED (2026-09-02)**

---

### Phase 31 — Kısa Soru Seti (uçuş/otel soru değil) — **COMPLETED (2026-09-02)**

---

### Phase 32 — Pasaportla Tek Adım (OCR) — **COMPLETED (2026-09-02)**

---

### Phase 33 — AI Fotoğraf Kontrolü (Vesikalık) — **COMPLETED (2026-09-02)**

---

### Phase 34 — Zami Zorunlu Alanlar (Medeni Hal / Meslek / Anne / Baba) — **COMPLETED (2026-09-03)**

---

### Phase 35 — Canlı E-posta (Resend) Aktivasyonu — **COMPLETED (2026-09-03)**
- `RESEND_API_KEY` bağlı.
- Sandbox uyarıları admin panelde.
- **USER ACTION:** Resend domain doğrulaması sonrası `SENDER_EMAIL=noreply@dubaivizeonline.com`.

---

### Phase 36 — Kritik Bug Fix: Zami Mapping Veri Kaybı — **COMPLETED (2026-09-03)**
**Keşif:** `routes_zami.MappingIn` içinde bazı alanlar yoktu; admin panelden mapping kaydedilince `constants`, `validate_selector`, `helper_selectors`, `upload_targets`, `status_search_field`, `status_submit_selector` siliniyordu.

**Düzeltme**
- `MappingIn` modeline eksik alanlar `Optional=None` olarak eklendi.
- `zami.normalize_mapping(value, current)` artık istek payload’ında **gönderilmeyen** alanları mevcut değerden **korur**.
- AdminZami UI bu alanları round-trip eder.
- Mapping’in tek kaynağı: `/app/scripts/zami_save_mapping.py` (validate_selector/helper_selectors/upload_targets dahil tam set).

**Test:** iteration_32 → kritik bug yok.

---

### Phase 37 — Logo Bazlı Yeni Tema + Marka Adı Güncellemesi — **COMPLETED (2026-09-03)**
**Amaç:** Logoya uyumlu premium görünüm + marka tutarlılığı.

**Yapılanlar**
- Yeni palet (logodan): petrol teal (#0E5A66/#003040), bakır/bronz (#A06030/#B0733C), royal mavi (#2B4B9B), kum beyazı (#F7F4EF).
- `index.css` token seti tamamen yenilendi (light+dark).
- Dekoratif kırmızı kaldırıldı; kırmızı yalnızca destructive/hata.
- `.flag-strip` teal→royal→bakır dalga.
- Logo işleme: kağıt zemin kaldırılıp kırpıldı; `/public/brand/` altında favicon + icon + wordmark üretildi; büyük dosyalar temizlendi.
- Navbar/Footer `BrandMark` ile güncellendi.
- Marka adı: **VizeAtlas Dubai → Dubai Vize Online** (frontend + backend metinleri, FastAPI title, bookmarklet etiketleri).

**Test:** iteration_32 → 0 kritik hata.

---

### Phase 38 — Tipografi + Premium Tasarım Sistemi (AI hissini azaltma) — **COMPLETED (2026-09-03)**
**Kullanıcı geri bildirimi:** “yapay zekayla yapıldığı çok belli oluyor” + “bu fontu kullan” + Instagram reel: “implement these skills”.

**Uygulananlar**
- **Font:** Headings/marka fontu → **Tinos** (Times ailesi; logoyla metrik uyumlu).
- Fake bold engelleme: headings weight 700’e sabitlendi; extrabold/black override edildi.
- Public UI’da Sparkles kaldırıldı → anlamlı ikonlar.
- Premium dokunuşlar: radius ölçeği, `text-wrap: balance/pretty`, `.tabular`, mikro-etkileşimler, grain doku.

**Test:** iteration_33 → 0 kritik bug, 0 UI bug.

---

## 3. Next Actions

### P0 — “AI Hissi”ni Kıran En Kritik İş: Gerçek Firma Bilgileri — **USER ACTION REQUIRED**
**Neden P0?** Sahte/placeholder veriler (telefon, adres, unvan, TÜRSAB, vergi) ve uydurma istatistikler “AI işi” izlenimini en çok artıran unsur.

**Gerekli veriler**
1) Gerçek telefon / WhatsApp
2) Gerçek destek e-postası
3) Açık adres (en az il/ilçe + mahalle)
4) Ticaret unvanı, TÜRSAB belge no, vergi dairesi/no, MERSİS, ticaret sicil no
5) Gerçek sosyal kanıt: tamamlanan başvuru sayısı, ortalama sonuç süresi, yıllık deneyim (varsa)
6) Varsa ekip/ofis fotoğrafları (stok foto yerine)

**Uygulama**
- `company_info` ve `review_summary` admin ayarlarından bu gerçek veriler girilecek.
- Ana sayfadaki vitrin istatistikleri gerçek sayılarla güncellenecek veya kaldırılacak.

---

### P0.1 — Rehberdeki (Stitch/Dribbble) Tasarım Referansı — **USER ACTION REQUIRED**
**Durum:** `onyuz-rehberi.pdf` bir iş akışı rehberi; bu ortamda Stitch/MCP erişimi yok.

**İstenen**
- Kullanıcı 1–2 adet Dribbble referansı (link veya ekran görüntüsü) ya da Stitch çıktı ekran görüntüsü paylaşır.
- Biz bu referansa göre hero/layout görsel hiyerarşisini revize ederiz.

---

### P0.2 — Resend Production Gönderici (Domain Doğrulaması + SENDER_EMAIL) — **USER ACTION REQUIRED**
1) Resend panelinde `resend.com/domains` → `dubaivizeonline.com` doğrula.
2) Deploy ortamında/`.env`:
   - `SENDER_EMAIL=noreply@dubaivizeonline.com` (veya `info@dubaivizeonline.com`)
3) Doğrulama testi:
   - Gerçek müşteri adresine e-posta `sent`.

---

### P1 — Custom Domain Deploy — **IN PROGRESS / USER ACTION REQUIRED**
**Durum / bulgular**
- `dubaivizeonline.com`: DNS’te A kaydı yok (ideal).
- Paylaşımlı hosting alınmayacak.
- Deployment readiness: PASS.

**Deploy runbook**
1) Emergent’te Deploy → Deploy Now.
2) Deploy sonrası Link domain → `dubaivizeonline.com`.
3) DNS kayıtları: kök domain (`@`) ve `www` (Emergent yönlendirmesine göre A/CNAME).
4) SSL otomatik.
5) Env:
   - `MONGO_URL`, `DB_NAME`, `JWT_SECRET`, `EMERGENT_LLM_KEY`, `RESEND_API_KEY`, `SENDER_EMAIL`, `STRIPE_API_KEY`, `PUBLIC_SITE_URL`, `PUBLIC_BASE_URL`.
6) Deploy sonrası:
   - `PUBLIC_SITE_URL` ve `PUBLIC_BASE_URL` yeni domain’e çekilecek (e-posta linkleri, dosya linkleri).

---

### P1.1 — Zami RPA Oturumu Yenileme (OTP) — **USER ACTION REQUIRED**
- Admin panelden `Zami Session Start` → CAPTCHA çözümü + OTP girilir.
- Oturum “ready” olunca transfer ve status sweep tekrar otomatik çalışır.

---

### P2 — Stripe Prod Geçişi (opsiyonel) — **BEKLEMEDE**
- Canlı anahtarlar + webhook secret + success/cancel URL’leri.

---

### P3 — WhatsApp Otomatik Sağlayıcı (Twilio/Meta) — **BEKLEMEDE**
- Sağlayıcı seçimi + API anahtarları.

---

### Ops — Zami’de Kalan Manuel Alanlar (İyileştirme) — **BACKLOG**
- Eğitim (`eu`)
- Uçuş bilgileri (`tr_a_d`, `tr_a_fn`, `tr_d_d`, `tr_d_fn`)

Not: Phase 31 kararı gereği formda soru olarak yok. İstenirse opsiyonel alan yapılabilir.

---

### Tech Debt — Canlı RPA Kodunda Karmaşıklık Azaltma — **BACKLOG (RISKLI)**
OTP/CAPTCHA bağımlı olduğu için deploy öncesi risk alınmadı:
- `zami_rpa.fill_application` (44)
- `zami_rpa.check_status` (30)
- `zami_rpa._upload_documents` (13)

---

## 4. Success Criteria
- POC/V1/SEO/Account/Drafts/FX/Reminders/Storefront akışları: mevcut kriterler korunur.

- Tema/marka başarı kriterleri:
  1) Petrol teal + bakır/bronz tema tüm public/admin sayfalarda tutarlı.
  2) Favicon/ikon/wordmark doğru servis edilir (`/brand/*` 200).
  3) “VizeAtlas” metinleri public alanlarda kalmaz.
  4) Tipografi: başlıklarda Tinos (Times ailesi) kullanılır; fake bold oluşmaz.
  5) Public UI’da anlamsız “AI parıltı” ikonları yoktur.

- Zami entegrasyonu başarı kriterleri:
  1) Mapping kaydı admin panelden kaydedilince **constants/upload_targets/validate_selector** kaybolmaz.
  2) Bookmarklet + RPA aktarım akışı bozulmaz.
  3) Status sweep (cron) çalışır ve admin panelde loglanır.

- E-posta (Resend) başarı kriterleri:
  1) `RESEND_API_KEY` bağlıyken outbox “sent/error” olur.
  2) Domain doğrulaması sonrası müşteri e-postaları **sent** olur.

- Deploy/Domain başarı kriterleri:
  1) `https://dubaivizeonline.com` açılır, SSL aktif.
  2) Admin panel ve ödeme akışları çalışır.
  3) Cron job’lar (taslak hatırlatma, Zami status sweep) deploy ortamında çalışır.

---

## DURUM (2026-09-03)
- Phase 1–19: **TAMAMLANDI**.
- Phase 20–23 (Zami RPA + capture + mapping + status + tracking): **TAMAMLANDI** ve canlı doğrulandı.
- Phase 24 (WhatsApp manuel): **TAMAMLANDI** (otomatik sağlayıcı beklemede).
- Phase 25: **KALDIRILDI**.
- Phase 26 (Kod kalitesi refactor): **TAMAMLANDI**.
- Phase 34 (Zami zorunlu alanlar): **TAMAMLANDI**.
- Phase 35 (Resend aktivasyonu): **TAMAMLANDI** (sandbox kısıtı var; domain doğrulaması bekliyor).
- Phase 36 (Zami mapping veri kaybı bug fix): **TAMAMLANDI**.
- Phase 37 (Logo bazlı yeni tema + marka adı): **TAMAMLANDI**.
- Phase 38 (Tipografi + premium tasarım sistemi): **TAMAMLANDI**.
- Phase 39 (Kod kalitesi refactor 3. tur): **TAMAMLANDI**.

Test raporları (seçme):
- iteration_28.json — Zami zorunlu alanlar: backend 12/12, frontend %100.
- iteration_29.json — Resend aktivasyonu + sandbox uyarıları.
- iteration_30.json — Refactor regresyon: %100.
- iteration_31.json — Refactor + Zami mapping/build_payload regresyon: 39/39 backend.
- iteration_32.json — Tema/Logo/Marka + Zami mapping bug fix regresyon: kritik hata 0.
- iteration_33.json — Tinos font + ikon değişimi + premium tasarım sistemi: kritik hata 0.
- iteration_34.json — Kod kalitesi raporu 3. tur: kritik hata 0; bayat test güncellendi.

Blokajlar / Bekleyen:
- **Gerçek firma bilgileri** (telefon/adres/TÜRSAB/vergisel bilgiler) → “AI hissi”ni kırmak için **USER ACTION REQUIRED**.
- **Stitch/Dribbble referansı** → UI’nin “insan eli” hissi için **USER ACTION REQUIRED**.
- **Resend production (domain doğrulaması + SENDER_EMAIL)** → müşteri e-postaları için **USER ACTION REQUIRED**.
- **Custom domain deploy/DNS yönlendirme** → **USER ACTION REQUIRED** (`dubaivizeonline.com`).
- **Zami RPA oturumu**: transfer/durum takibi için admin panelden yeni oturum + OTP gerekiyor.
- Stripe prod anahtarları yok (opsiyonel).
