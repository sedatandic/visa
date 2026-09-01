# plan.md

## 1. Objectives
- Türkçe, modern, **sade** ve güven veren bir Dubai/UAE vize başvuru sitesi (kopya değil; benzer bilgi mimarisi/UX, özgün marka/renk).
- Vize tipleri + fiyatlar + genel bilgilendirme + **rehber içerikler** + hızlı başvuru akışı.
- Çekirdek iş akışı: **başvuru oluşturma → dosya yükleme → ödeme (kart / havale) → takip kodu**.
- Başvuruları MongoDB’ye kaydetme, admin panelde listeleme/detay/güncelleme.
- E-posta bildirimleri (başvuru sahibine + admin’e):
  - **RESEND_API_KEY yoksa akışı bozmadan “skipped” olarak outbox’a yaz**.
  - **Canlı Resend anahtarı ile gerçek e-posta gönderimini E2E doğrulama** (beklemede: anahtar gerekli).
- Güven ve “insan eliyle tasarlanmış” kurumsal görünüm:
  - **BAE bayrak paleti** (yeşil/kırmızı/siyah/beyaz) — kırmızı vurgu belirgin.
  - **Tipografi**: **Montserrat (başlık)** + **Figtree (gövde)**.
  - **Koyu mod yok**.
  - Gerçek görseller / kurumsal bloklar / sosyal kanıt / örnek vize görselleri.
  - **TÜRSAB + acente şeffaflığı** ve **GDRFA rozeti**.
- **Başvuru evrak standardı (güncel)**:
  - **Her yolcu:** Pasaport + vesikalık fotoğraf.
  - **Tüm başvuru:** **Uçak bileti/rezervasyon** + **otel/konaklama rezervasyonu**.
- **SEO büyüme hedefi (tamamlandı):** Vize rehber (SEO landing) sayfaları, sitemap/robots, JSON-LD.
- **Operasyonel verim + dönüşüm (tamamlandı):** Eksik belge hatırlatma, taslak hatırlatma, hesap/draft, aile profili.
- **Fiyatlandırma (tamamlandı):** USD baz fiyat + canlı kurla TL tahsilat + kur şeffaflığı.
- **Ek ürün satışları (tamamlandı & geliştirildi):**
  - Mağaza sayfaları üzerinden **eSIM** ve **seyahat sigortası** satışı.
  - Vize başvurusu içinde eSIM + sigorta upsell (tek formda).
  - Ek ürünler seyahat tarihine bağlandı (başlangıç/bitiş).
  - **Akıllı paket önerisi** + **%10 seyahat paketi indirimi** (sigorta+eSIM birlikte) hem başvuruda hem mağazada.
- **Yeni hedef (P0): Zami Tours (visa.zamitours.ae) portalına başvuru aktarımı**
  - Kullanıcı kararı: **A + B**
    - **A) Bookmarklet/Browser Helper ile tek tık form doldurma (kullanıcı captcha+OTP’yi kendisi geçer)**
    - **B) Sunucuda Playwright ile yarı-otomatik oturum/RPA (captcha+OTP insan onayı ile, cookie saklanır)**
  - Teknik engeller: girişte **CAPTCHA** + **OTP** olduğu için tam otomatik login mümkün değil.
  - Gereksinim: Zami form alanları bilinmediği için **admin “alan eşleme (mapping)”** ekranı ile konfigüre edilebilir entegrasyon.
  - Güvenlik: Kullanıcı şifresi sohbet içinde paylaşıldı; **saklanmadı** ve **değiştirilmesi önerildi**. Kimlik bilgileri (varsa) admin panelinden şifreli/korumalı şekilde saklanacak.

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

### Phase 4 — Marka/Tema Yenileme + Sosyal Kanıt (Tamamlandı; koyu mod kaldırıldı)

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
- Uçak bileti + otel zorunlu (frontend+backend)
- Kart gövde tıklaması başvuruya yönlendirmez (sadece buton/link)

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
- Frontend: `Apply.jsx` adım 2'de sigorta planı (yolcu başına, tek seçim) + tüm eSIM paketleri (adet stepper, varsayılan adet yolcu sayısı); özet satırları + canlı FX toplam.
- Admin: AdminOrders’da “Vize başvurusu ile alındı” etiketi; AdminApplicationDetail’de store satırları + bağlı sipariş kodu.
- Test: iteration_15.json backend 51/52 (kritik yok) + E2E başvuru→bağlı sipariş→havale→admin mark-paid senkronu PASS.

---

### Phase 18 — Ek Ürün Geçerlilik Tarihlerinin Seyahat Tarihine Bağlanması — **COMPLETED (2026-08-31)**
- Backend: `resolve_store_lines(items, arrival_date, departure_date)` → satırlarda `validity_days`, `starts_on`, `ends_on`, `trip_days`, `covers_trip`.
- Frontend: giriş tarihi yoksa seçim kapalı; kartlarda geçerlilik penceresi ve “paket seyahat süresinden kısa” uyarısı; özet satırlarında tarih aralığı.
- Admin + email + order status: tarih aralığı görünür.
- Test: canlı UI doğrulaması + E2E date script PASS.

---

### Phase 19 — Akıllı Paket Önerisi + %10 Seyahat Paketi İndirimi — **COMPLETED (2026-08-31)**
Kullanıcı kararları: indirim **%10** (ek ürün toplamı), hem başvuru hem mağaza, öneri otomatik seçmez; etiket + “Önerilenleri ekle”.
- Backend:
  - `content.BUNDLE_DISCOUNT` + `bundle_discount_amount()`
  - `compute_pricing` → `bundle_discount`, `bundle_discount_rate`, `bundle_discount_title`
  - `/api/products` → `bundle`
  - Mağaza siparişi (`/api/orders`) + bağlı sipariş: `items_total`, `bundle_discount`, indirimli `price`
  - E-postalar: indirim satırı
- Frontend:
  - `Apply.jsx`: promosyon kutusu + önerilen etiketler + buton + indirim satırları
  - `StoreCheckout.jsx`: çapraz satış bölümü (diğer kategori) + indirim satırı
  - `OrderStatus`, `AdminOrders`, `AdminApplicationDetail`: indirim/tarih gösterimi
- Test: E2E bundle script PASS + canlı UI screenshot PASS.

---

### Phase 20 — Zami Tours Portalına Başvuru Aktarımı (visa.zamitours.ae) — **PLANNED / NOT STARTED**
**Amaç:** Bizde toplanan başvuru verilerini Zami Tours “meter system” (portal) içine hızlı ve hatasız şekilde aktarmak.

#### 20A) Entegrasyon Yaklaşımı (A + B)
1) **A — Bookmarklet / Browser Helper (Client-side Autofill)**
- Kullanıcı Zami portalına kendi tarayıcısından giriş yapar (CAPTCHA + OTP’yi kendisi geçer).
- Zami’de başvuru formu sayfasında “VizeAtlas → Formu Doldur” butonu / bookmarklet çalıştırılır.
- Bizim sistemimizden alınan başvuru `reference_code` veya `application_id` ile veriler çekilir.
- JavaScript, DOM alanlarına mapping’e göre değer yazar; dosya upload alanlarına mümkün olan en iyi şekilde yardım eder:
  - Tarayıcı güvenliği nedeniyle dosya inputlarına doğrudan set her zaman mümkün değildir → kullanıcıya “tıkla-yükle” yönlendirmesi + otomatik scroll.

2) **B — Playwright RPA (Server-side, Human-in-the-loop Login)**
- Admin panelinden bir “RPA Oturumu” başlatılır.
- Sistem login ekranını açar; CAPTCHA görseli + OTP alanı admin arayüzünde gösterilir.
- İnsan captcha/OTP’yi girer; sistem session cookie’yi güvenli şekilde saklar (Zami’nin device setting’lerine bağlı olarak 1 ay).
- Sonrasında başvuru formu otomatik doldurulur ve submit edilir.
- Oturum süresi dolunca tekrar insan onayı gerekir.

#### 20B) Admin “Alan Eşleme (Mapping)” Altyapısı (kritik)
- Zami form alan adları bilinmediği için konfigüre edilebilir mapping şart.
- Admin ekranı:
  - Zami başvuru formu HTML’i yapıştırma (veya “field list” JSON yükleme)
  - Sistem `input/select/textarea` alanlarını parse eder (name/id/type/label).
  - Bizim şema alanlarımızla eşleme yapılır (contact/travel/travelers/store_items/addons vs.).
  - Mapping versiyonlanır ve “test et” butonu ile doğrulanır.
- Hem bookmarklet hem Playwright RPA aynı mapping kaydını kullanır.

#### 20C) Kimlik Bilgileri ve Güvenlik
- Kullanıcı şifresi sohbetten alınmayacak; mevcut paylaşılan şifre **saklanmadı**.
- Admin panelinde “Zami Portal Ayarları”:
  - username (email)
  - password (şifreli saklama; en azından env/secret veya DB’de şifreli alan)
  - portal base URL
  - “cookie storage” politikası (TTL, manuel sıfırlama)
- Audit log:
  - Hangi başvuru ne zaman aktarılmış, kim başlatmış, sonuç ne.

#### 20D) Yeni API’ler / Ekranlar
- Backend:
  - `GET /api/admin/zami/mapping` + `PUT /api/admin/zami/mapping`
  - `POST /api/admin/zami/session/start` (RPA)
  - `POST /api/admin/zami/session/solve` (captcha/otp input)
  - `POST /api/admin/zami/apply/{application_id}` (RPA ile doldur+gönder)
  - `GET /api/admin/zami/logs`
- Frontend (Admin):
  - `/admin/zami` sekmesi: Mapping editor + session yönetimi + job kuyruğu/loglar
  - Application detay sayfasında: “Zami’ye gönder” butonu + durum.
- Frontend (Client):
  - `/hesabim` veya tracking sayfasında: “Zami için doldur” bookmarklet linki + yönergeler.

#### 20E) Test / Doğrulama
- CAPTCHA/OTP nedeniyle tam otomasyon testi sınırlı:
  - Mapping parse unit testleri
  - Bookmarklet: sahte bir HTML form üzerinde e2e DOM fill testi
  - Playwright: staging’de login ekranına kadar otomasyon + insan adımı sonrası form doldurma smoke test
  - Üretimde: “dry-run” modu (sadece doldur, submit etme) + ekran görüntüsü kaydı.

---

## 3. Next Actions

### P0 — Phase 20: Zami Portal Aktarımı
1) Admin mapping ekranı (HTML parse + field mapping + versiyon)
2) Bookmarklet üretimi (mapping + application fetch)
3) Playwright RPA servisinin eklenmesi (human-in-loop login + cookie store)
4) Admin job/log ekranı + uygulama detayında “Zami’ye gönder”
5) Dry-run + canlı pilot test (1-2 başvuru)

### P0 — Canlı E-posta Testi (Resend) — BEKLEMEDE
- Gerekli env:
  - `RESEND_API_KEY`
  - `SENDER_EMAIL` (domain doğrulanmış)

### P1 — Stripe prod geçişi (opsiyonel)
- Canlı anahtarlar + webhook secret + success/cancel URL’leri.

### P1 — İçerik onayı ve gerçek veriler
- Banka bilgileri (`/admin/banka`)
- TÜRSAB/acente ticari bilgiler (`/admin/acente`)

### P2 — Operasyonel güvenlik (opsiyonel)
- Admin şifresi değişimi, rate limit/bot koruması.

---

## 4. Success Criteria
- POC/V1/SEO/Account/Drafts/FX/Reminders/Storefront akışları: mevcut kriterler **korunur**.
- Phase 17–19 ek ürün akışları:
  - Ek ürün tarihleri doğru, öneri + indirim doğru, hem başvuru hem mağaza akışı sorunsuz.
- **Phase 20 başarı kriterleri (Zami aktarımı):**
  1) Admin mapping ile Zami form alanları eşlenebilir ve değişime dayanıklı olur.
  2) Bookmarklet ile kullanıcı Zami formunu tek tıkla doldurabilir (captcha/OTP kendisi).
  3) Playwright RPA ile admin, insan onayıyla login olup başvuruyu otomatik doldurup gönderebilir.
  4) Aktarım kayıtları (log) ve hata ayıklama çıktıları admin panelinde görünür.
  5) Kimlik bilgileri güvenli saklanır; şifre sohbetten/istemciden loglanmaz.

---

## DURUM (2026-09-01)
- Phase 1–16: **TAMAMLANDI**.
- Phase 17: **TAMAMLANDI**.
- Phase 18: **TAMAMLANDI**.
- Phase 19: **TAMAMLANDI**.
- Phase 20: **PLANLANDI / NOT STARTED** (CAPTCHA + OTP nedeniyle human-in-loop yaklaşımı onaylandı: A + B).

Test:
- `testing_agent_v3` iteration_13.json — backend **46/46 PASS**, frontend **%100 PASS**.
- `testing_agent_v3` iteration_14.json — backend **38/40 (kritik yok)**, frontend **%100**.
- `testing_agent_v3` iteration_15.json — backend **51/52 PASS**, frontend kısmi; kritik yok.
- Ek E2E scriptler: tarih + paket indirimi + ödeme senkronu **PASS**.


### Phase 20 — Zami Tours Portalına Başvuru Aktarımı (A + B) — **COMPLETED (2026-09-01)**
Engel: visa.zamitours.ae girişinde resimli CAPTCHA + OTP var → tam otomatik login mümkün değil. Bu yüzden iki yol birlikte kuruldu.
- **A) Tarayıcı yardımcısı (bookmarklet)**: `GET /api/zami/bookmarklet.js` (BASE'i currentScript.src'den alır → https güvenli). Admin başvuru detayında "Aktarım kodu oluştur" → 45 dk geçerli tek kullanımlık token; Zami formunda bookmarklet çalıştırılıp kod yapıştırılınca alanlar dolar, belgeler indirme linkleriyle listelenir (dosya inputları tarayıcı güvenliği nedeniyle otomatik dolmaz).
- **B) Robot oturumu (Playwright)**: `/api/admin/zami/session/start` login sayfasını açıp CAPTCHA görselini admin paneline gönderir; captcha (+ gerekiyorsa OTP) girilince oturum `storage_state` olarak saklanır. `/api/admin/zami/transfer/{id}` kayıtlı oturumla formu doldurur; "Güvenli mod" açıkken göndermez, ekran görüntüsü döner.
- **Alan eşleme ekranı** (`/admin/zami`): Zami form HTML'i yapıştırılır → `parse_form_fields` (BeautifulSoup) input/select/textarea alanlarını çıkarır; bizim alanlar (17 genel + 17 yolcu alanı, çoklu tarih formatları) Zami seçicileriyle eşlenir. Yolcu alanlarında `{i}` / `{n}` desteği. Eşleme hem bookmarklet hem robot tarafından kullanılır.
- Yeni dosyalar: `backend/zami.py`, `backend/zami_rpa.py`, `backend/routes_zami.py`, `frontend/src/pages/AdminZami.jsx`; koleksiyonlar: `zami_logs`, `zami_handoffs`. Bağımlılık: `playwright==1.62.0`, `beautifulsoup4`.
- Güvenlik: sohbette paylaşılan portal şifresi hiçbir yere kaydedilmedi; kullanıcıya şifre değiştirme önerildi. Portal bilgileri yalnızca admin panelinden `site_settings`e yazılır.
- Test: API uçları (parse/mapping/handoff/logs/hata yolları) + gerçek portalda Playwright captcha yakalama + sahte Zami formunda bookmarklet doldurma (5/5 alan) **PASS**; admin UI ekran görüntüleriyle doğrulandı.
- Kullanıcıdan beklenen: (1) Zami yeni başvuru formunun HTML'i → alan eşlemesi, (2) robot modu için portal kullanıcı/şifresinin admin panelinden girilmesi.


### Phase 21 — Toplu Aktarım + Otomatik Durum Takibi — **COMPLETED (2026-09-01)**
- **Toplu aktarım**: `GET /api/admin/zami/candidates` (aktarıma uygun başvurular), `POST /api/admin/zami/bulk-transfer` (max 20, sıralı, dry_run destekli, oturum yoksa erken durur). Admin'de "Toplu Aktarım" sekmesi: çoklu seçim tablosu + doldur/gönder + sonuç dökümü. Aktarılanlara `zami_transferred_at`, `zami_submitted` yazılır.
- **Otomatik durum takibi**: `zami_rpa.check_status()` portal liste/durum sayfasında referansı arar (zami_reference → takip kodu → pasaport no), sonuç satırını okur; `zami.match_status()` anahtar kelimelerle bizim durum koduna çevirir. `zami_status.apply_status()` başvuru durumunu günceller, `status_history`'ye not düşer ve müşteriye `status_change` e-postası atar. `sweep_statuses()` toplu tarama, `status_loop()` arka planda (ayarlanan saat aralığında, admin'den aç/kapa) çalışır — `server.py` lifespan'e eklendi.
- Yeni endpointler: `PUT /api/admin/zami/reference/{id}`, `POST /api/admin/zami/check-status/{id}`, `POST /api/admin/zami/check-status-all`.
- Admin UI: "Durum Takibi" sekmesi (durum sayfası URL'i, arama/sonuç seçicileri, onay/ret/inceleme/iptal anahtar kelimeleri, otomatik kontrol + periyot + e-posta anahtarı, "Şimdi kontrol et"); başvuru detayında Zami başvuru no alanı + "Durumu kontrol et" + son kontrol bilgisi.
- Playwright tarayıcı yolu otomatik bulunuyor (`PLAYWRIGHT_BROWSERS_PATH` yoksa /pw-browsers vb.); tarayıcı yoksa kullanıcıya anlaşılır hata dönüyor (bookmarklet yolu önerilir).
- Test: sahte portal (localhost) ile uçtan uca — toplu aktarım 2/2 başvuru × 5 alan, tek başvuru durum kontrolü `Approved` → başvuru `approved` + müşteri e-postası, sweep `Processing` → `reviewing`, e-posta kayıtları oluştu. **PASS**
- Kalan: Zami gerçek form/liste sayfalarının HTML'i alınmadan alan eşlemesi tamamlanamıyor (kullanıcıdan bekleniyor).


### Phase 22 — Alan Eşlemesi Otomasyonu (yakalama + otomatik öneri) — **COMPLETED (2026-09-01)**
Zami form HTML'i elde olmadığı için eşlemeyi kullanıcıya bırakmak yerine otomatikleştirildi:
- **Yakalama yardımcısı**: `GET /api/zami/capture.js` bookmarklet'i Zami sayfasındaki tüm input/select/textarea alanlarını (name, id, label, placeholder, tip, submit/search seçicileri) okuyup token korumalı `POST /api/zami/capture/{token}`'a gönderir. Admin'de "Yakalama kodu oluştur" (45 dk) + yer imi bağlantısı; hem başvuru formu hem durum/liste sayfası ayrı ayrı yakalanır.
- **Otomatik eşleme önerisi**: `zami.suggest_mapping()` etiket/isim anahtar kelimeleriyle bizim alanlara eşler; `pax[0][...]` gibi indeksli seçicileri `{i}` şablonuna çevirir; durum sayfasından `status_url`, arama alanı ve satır seçicisini önerir. `POST /api/admin/zami/apply-suggestions` önerileri eşlemeye işler. Mapping ekranındaki açılır listeler yakalanan alanlarla otomatik dolar (HTML yapıştırma artık opsiyonel).
- **Tarayıcı motoru dayanıklılığı**: paketle gelen Chromium yoksa sistem Chromium'una (`/usr/local/bin/browser-use-chromium`, google-chrome) otomatik geçiş; hiçbiri yoksa anlaşılır hata + bookmarklet önerisi.
- Test: gerçekçi sahte Zami formu (15 alan, tablo etiketli + pax[0] yolcu alanları) → yakalama 15 alan, otomatik eşleme **8 genel + 7 yolcu** alanı, `{i}` şablonu doğru; öneriler uygulanıp gerçek başvuruyla dry-run aktarımda **12 alan** doldu (yalnızca select seçenek eşleşmeyen 1 alan atlandı). Durum sayfası yakalamada `status_url` + arama seçicisi otomatik önerildi. **PASS**
- Test verileri temizlendi (mapping/capture/session sıfırlandı), kullanıcı sıfırdan yapılandırabilir.


### Phase 23 — Müşteri Durum Ekranı + Aktarım Hazırlık Kontrolü — **COMPLETED (2026-09-01)**
- **Müşteri durum ekranı**: `build_customer_timeline()` (routes_public) 5 adımlı müşteri dostu akış üretir (Başvuru alındı → Ödeme → Belgeler → Göçmenlik idaresine iletildi → Vize sonucu); ödeme/belge/portal aktarımı/portal durumu verilerinden tek "şu an burada" adımı hesaplanır. `/api/applications/track` ve belge yükleme yanıtına `timeline` eklendi; portal iç bilgileri (`zami_status_raw`, `zami_reference`) müşteri yanıtından temizlendi.
- **Track.jsx**: "Başvurunuz nerede?" kartı — ilerleme çubuğu (x/5 adım), dikey adım listesi, tamam/şu an/bekliyor durumları, onay/ret için özel ikon ve başlık, adım tarihleri ve "portalda en son ... kontrol edildi" notu.
- **Aktarım hazırlık kontrolü**: `GET /api/admin/zami/readiness` — yakalama, form URL, genel/yolcu eşleme (ad-pasaport-doğum tarihi kritik), gönder seçicisi, sunucu tarayıcısı, portal oturumu ve durum sayfası kontrolleri + `ready_bookmarklet` / `ready_robot`. Admin ekranında "Hazırlık kontrolü" butonu ve maddeli kontrol listesi.
- Test: 3 farklı başvuru durumu (submitted / paid+reviewing / approved) API ve UI'da doğru adım akışını gösterdi (1/5, 4/5, 5/5); readiness endpoint eksikleri doğru raporladı. **PASS**
- Kalan (kullanıcı aksiyonu): Zami'de gerçek formda yakalama yardımcısını çalıştırmak, önerilen eşlemeyi uygulamak ve ilk gerçek aktarımı yapmak — captcha/OTP nedeniyle bizim tarafımızdan yapılamıyor.
