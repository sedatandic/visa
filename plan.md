# plan.md

## 1. Objectives
- Türkçe, modern, **sade** ve güven veren bir Dubai/UAE vize başvuru sitesi (özgün marka/renk; kopya UX değil).
- Vize tipleri + fiyatlar + genel bilgilendirme + **rehber içerikler** + hızlı başvuru akışı.
- Çekirdek iş akışı: **başvuru oluşturma → dosya yükleme → ödeme (kart / havale) → takip kodu**.
- Başvuruları MongoDB’ye kaydetme, admin panelde listeleme/detay/güncelleme.
- E-posta bildirimleri (başvuru sahibine + admin’e):
  - **RESEND_API_KEY yoksa akışı bozmadan “skipped” olarak outbox’a yaz**.
  - Canlı Resend anahtarı ile gerçek e-posta gönderimini E2E doğrulama (**beklemede: anahtar gerekli**).
- Güven ve “insan eliyle tasarlanmış” kurumsal görünüm:
  - **BAE bayrak paleti** (yeşil/kırmızı/siyah/beyaz) — kırmızı vurgu belirgin.
  - Tipografi ve UI dili tasarım kılavuzuna uygun.
  - Gerçek görseller / kurumsal bloklar / sosyal kanıt / örnek vize görselleri.
  - **TÜRSAB + acente şeffaflığı** ve **GDRFA rozeti**.
- **Başvuru evrak standardı (güncel)**:
  - **Her yolcu:** Pasaport + vesikalık fotoğraf.
  - **Tüm başvuru:** Uçak bileti/rezervasyon + otel/konaklama rezervasyonu (**opsiyonel yükleme**; formda soru olarak sorulmaz).
- SEO büyüme hedefi (tamamlandı): vize rehber sayfaları, sitemap/robots, JSON-LD.
- Operasyonel verim + dönüşüm (tamamlandı): eksik belge hatırlatma, taslak hatırlatma, hesap/draft, aile profili.
- Fiyatlandırma (tamamlandı): USD baz fiyat + canlı kurla TL tahsilat + kur şeffaflığı.
- Ek ürün satışları (tamamlandı & geliştirildi):
  - Mağaza sayfaları üzerinden **eSIM** ve **seyahat sigortası** satışı.
  - Vize başvurusu içinde eSIM + sigorta upsell (tek formda).
  - Ek ürünler seyahat tarihine bağlandı (başlangıç/bitiş).
  - **Akıllı paket önerisi** + **%10 seyahat paketi indirimi** (sigorta+eSIM birlikte) hem başvuruda hem mağazada.
- AI destekli otomasyon (tamamlandı):
  - **Pasaport OCR** (Adım 1’de “Pasaportla Tek Adım”).
  - **Fotoğraf Kontrolü**: vesikalık fotoğraf yüklenirken AI ile uygunluk kontrolü (arka plan/çerçeve/yüz/netlik) ve kullanıcıya uyarı.
    - **Kritik karar:** Uyarı bazlıdır, **başvuruyu engellemez**.
- Zami Tours otomasyonu (tamamlandı, **canlı doğrulama bekliyor**):
  - Playwright RPA + yakalama (capture) + alan eşleme + toplu aktarım + durum polling + kullanıcı takip zaman çizelgesi.
  - **P0: “İlk Gerçek Aktarım”** canlı Zami portalında doğrulama (**BLOCKED: kullanıcı Zami şifresi yok**).
- WhatsApp bildirimleri: **manuel mod** (wa.me link üretimi) tamam; otomatik sağlayıcı (Twilio/Meta) **beklemede**.

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
- Kart gövde tıklaması başvuruya yönlendirmez (sadece buton/link)
- Not: Seyahat belgeleri artık form sorusu değil, opsiyonel belge yükleme (Phase 31 ile uyumlu).

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
- Frontend: `Apply.jsx` adım 2'de sigorta planı (yolcu başına, tek seçim) + eSIM paketleri (adet stepper, varsayılan adet yolcu sayısı); özet + canlı FX toplam.
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

### Phase 20 — Zami Tours Portalına Başvuru Aktarımı (visa.zamitours.ae) — **COMPLETED (2026-09-01) / LIVE VERIFICATION PENDING**
Engel: visa.zamitours.ae girişinde resimli CAPTCHA + OTP var → tam otomatik login sınırlı. Bu yüzden iki yol birlikte kuruldu.
- **A) Tarayıcı yardımcısı (bookmarklet)**
  - `GET /api/zami/bookmarklet.js` (BASE’i `currentScript.src`’den alır).
  - Admin başvuru detayında “Aktarım kodu oluştur” → 45 dk tek kullanımlık token.
  - Zami formunda bookmarklet çalıştır → token gir → alanlar mapping’e göre dolar; dosyalar için indirme linkleri listelenir (file input set sınırlı → kullanıcı yönlendirilir).
- **B) Robot oturumu (Playwright RPA)**
  - Oturum `storage_state` ile saklanır; transfer “güvenli mod/dry-run” ile screenshot döndürebilir.
  - Kritik: Playwright chromium yolu **`/usr/local/bin/browser-use-chromium`** korunur.
- **Admin alan eşleme ekranı (`/admin/zami`)**
  - HTML yapıştırma opsiyonu + yakalama (capture) ile field listesi.
  - Genel + yolcu alanlarında `{i}` şablonu (multi-passenger).
  - Mapping hem bookmarklet hem RPA tarafından ortak kullanılır.

**Kalan (P0): İlk Gerçek Aktarım (LIVE)**
- Canlı portal DOM/selectors farklı olabilir → gerçek yakalama ve gerçek transfer koşusu gerekli.
- **BLOCKED:** kullanıcı Zami portal şifresi yok/verilmedi; bu olmadan canlı aktarım yapılamaz.

---

### Phase 21 — Toplu Aktarım + Otomatik Durum Takibi — **COMPLETED (2026-09-01)**
- Toplu aktarım API + admin UI.
- Otomatik status polling (`zami_status.py`) → bizim status’e çevirme + status_history + e-posta tetikleme.
- Not: gerçek portal doğrulaması Phase 20 P0 ile birlikte yapılacak.

---

### Phase 22 — Alan Eşlemesi Otomasyonu (yakalama + otomatik öneri) — **COMPLETED (2026-09-01)**
- `GET /api/zami/capture.js` bookmarklet’i alanları okuyup token korumalı capture endpoint’e gönderir.
- `zami.suggest_mapping()` etiket/isim anahtar kelimeleriyle öneri çıkarır; `{i}` şablonlaştırır.
- Dayanıklılık: sistem chromium fallback; yoksa anlaşılır hata + bookmarklet önerisi.

---

### Phase 23 — Müşteri Durum Ekranı + Aktarım Hazırlık Kontrolü — **COMPLETED (2026-09-01)**
- `build_customer_timeline()` 5 adımlı görsel takip akışı.
- `GET /api/admin/zami/readiness` ile mapping/oturum/tarayıcı/durum sayfası kontrolleri.

---

### Phase 24 — WhatsApp Bildirimleri (Manuel Mod) + Admin Ayarları — **COMPLETED (2026-09-01)**
- Admin WhatsApp ayarları paneli.
- Durum değişimlerinde admin’e/operasyona **wa.me** linki üreten manuel bildirim akışı.
- Otomatik sağlayıcı (Twilio/Meta) entegrasyonu **beklemede: API anahtarları yok**.

---

### Phase 25 — Ücretsiz Ön Değerlendirme Sihirbazı (3 Soru) — **KALDIRILDI (2026-09-02)**
- Kullanıcı isteği ile tamamen kaldırıldı.
- Route `/on-degerlendirme` 404.
- Admin sayfası ve backend endpoint’leri kaldırıldı.
- Not: DB koleksiyonu silinmedi (geri getirmek istenirse mümkün).

---

### Phase 26 — Kod Kalitesi Raporu Uygulamasi (Refactor) — **COMPLETED (2026-09-02)**
(Detaylar önceki sürümle aynı; davranış korunarak refactor tamamlandı.)

---

### Phase 27 — Tum Site Arayuz Yenilemesi (Stitch tarzi) — **COMPLETED (2026-09-02)**
(Detaylar önceki sürümle aynı; Stitch tarzı tasarım uygulandı, UI geri alınmayacak.)

---

### Phase 28 — Turkce Tarih Secici + Ana Sayfa Vitrini — **COMPLETED (2026-09-02)**
(Detaylar önceki sürümle aynı.)

---

### Phase 29 — Sehir Alani ve On Degerlendirme Kaldirildi — **COMPLETED (2026-09-02)**
- “Şehir” alanı kaldırıldı.
- Ön değerlendirme tamamen kaldırıldı.

---

### Phase 30 — Formu Kisaltma + Yorum Vitrini — **COMPLETED (2026-09-02)**

---

### Phase 31 — dubaivizeal Tarzi Kisa Soru Seti — **COMPLETED (2026-09-02)**
- Konaklama ve uçuş alanları **soru olarak sorulmaz**.
- Uçak bileti + otel yükleme **opsiyonel**.

---

### Phase 32 — Pasaportla Tek Adim (Sifira Yakin Soru) — **COMPLETED (2026-09-02)**
- Pasaport OCR adım 1’e taşındı; eksiksiz okunduğunda alanlar özet karta dönüşür.

---

### Phase 33 — Fotoğraf Kontrolü (AI Vesikalık Fotoğraf Doğrulama) — **COMPLETED (2026-09-02)**
**Amaç:** Kullanıcı vesikalık fotoğraf yüklediğinde, arka plan/çerçeve/yüz/netlik gibi kriterleri AI ile kontrol edip **hemen uyarı vermek**; admin manuel inceleme yükünü azaltmak.

**Backend**
- `backend/passport_ai.py`
  - `check_photo()` + `normalize_photo_result()` eklendi.
  - Emergent LLM Vision prompt ile kriterler: açık/düz arka plan, tek kişi, yüz net ve kadraj doğru, engel/filtre yok, bulanıklık yok, çözünürlük yeterli.
- `backend/routes_public.py`
  - `POST /api/photo/check` eklendi.
  - Edge-case’ler:
    - Geçersiz `file_id` → **404**
    - PDF → `checked=false`, `reason="pdf"` (kullanıcıyı JPG/PNG’ye yönlendirir)
    - AI hata/verimsiz yanıt → **graceful fallback**: `ok=true`, `checked=false`, `reason="ai_error"` (akış bozulmaz)
  - Kontrol özeti `uploads` kaydına `photo_check` alanı ile yazılır.

**Frontend**
- `frontend/src/pages/Apply.jsx`
  - `checkPhotoWithAI()` eklendi; fotoğraf yükleme sonrası otomatik çağrılır.
  - UI durumları (testid):
    - `traveler-N-photo-check-loading`
    - `traveler-N-photo-check-ok`
    - `traveler-N-photo-check-warning`
  - **Uyarı bazlı:** Uygun değilse bilgilendirir ama **başvuruyu engellemez** (“Yine de devam edebilirsiniz.”).

**Test**
- `testing_agent_v3` iteration_24.json
  - Backend 12/12 **%100 PASS**
  - Fotoğraf kontrolü akışı ve edge-case’ler doğrulandı.

---

## 3. Next Actions

### P0 — “İlk Gerçek Aktarım” (Zami Live Verification) — **BLOCKED**
**Gerekenler:**
1) Kullanıcıdan Zami portal e-posta/şifre (veya kullanıcı tarafında ekran paylaşımı ile doğrulama)
2) Gerçek form sayfasında `capture.js` çalıştırma
3) Admin `/admin/zami` önerilen mapping’i uygulama
4) 1 test başvuru ile `dry-run` (submit yok) → screenshot + log
5) Onay sonrası 1 gerçek submit

### P1 — “Kaldığın Yerden Devam” (Abandon / Draft Link E-postası)
- Amaç: formu yarıda bırakan kullanıcıya e-posta ile tek tıkla dönüş linki.
- Beklenen: dönüşüm artışı, daha az kayıp taslak.

### P1 — “Belge Hatırlatıcı” (Eksik/opsiyonel belge takibi)
- Amaç: bilet/otel gibi opsiyonel belgeler yüklenmediyse nazik otomatik hatırlatma.
- Not: operasyonel altyapı var; mesajlar ve tetik koşulları netleştirilecek.

### P2 — WhatsApp Otomatik Sağlayıcı (Twilio/Meta) — BEKLEMEDE
- Sağlayıcı seçimi + API anahtarları.

### P2 — Canlı E-posta Testi (Resend) — BEKLEMEDE
- Env:
  - `RESEND_API_KEY`
  - `SENDER_EMAIL` (domain doğrulanmış)

### P2 — Stripe prod geçişi (opsiyonel) — BEKLEMEDE
- Canlı anahtarlar + webhook secret + success/cancel URL’leri.

---

## 4. Success Criteria
- POC/V1/SEO/Account/Drafts/FX/Reminders/Storefront akışları: mevcut kriterler **korunur**.
- Phase 17–19 ek ürün akışları:
  - Ek ürün tarihleri doğru, öneri + indirim doğru, hem başvuru hem mağaza akışı sorunsuz.
- Fotoğraf Kontrolü (Phase 33) başarı kriterleri:
  1) Fotoğraf yükleme sonrası kontrol tetiklenir, kullanıcıya 2 durumda net geri bildirim verir (OK / Uyarı).
  2) Uyarı çıktığında **başvuruyu engellemez**.
  3) Edge-case’lerde akış bozulmaz (PDF, AI error, invalid file_id).
- Zami entegrasyonu (Phase 20–23) başarı kriterleri:
  1) Admin mapping ile Zami form alanları eşlenebilir ve değişime dayanıklı olur.
  2) Bookmarklet ile kullanıcı Zami formunu doldurabilir (captcha/OTP kendisi).
  3) Playwright RPA ile admin, insan onayıyla login olup başvuruyu doldurabilir (dry-run + submit).
  4) Aktarım kayıtları/loglar ve hata ayıklama çıktıları admin panelinde görünür.
  5) Canlı portalda en az **1 dry-run + 1 gerçek submit** ile doğrulama yapılır (**P0**).
- WhatsApp (Phase 24):
  - Manuel modda wa.me linkleri doğru mesaj şablonlarıyla üretilir ve operasyon akışına uygun olur.

---

## DURUM (2026-09-02)
- Phase 1–19: **TAMAMLANDI**.
- Phase 20–23 (Zami RPA + yakalama + mapping + status + tracking): **TAMAMLANDI**, ancak **İlk Gerçek Aktarım canlı doğrulaması P0 ve BLOCKED** (Zami şifresi yok).
- Phase 24 (WhatsApp manuel): **TAMAMLANDI** (otomatik sağlayıcı beklemede).
- Phase 25 (Ön değerlendirme): **KALDIRILDI** (kullanıcı isteği).
- Phase 26 (Kod kalitesi refactor): **TAMAMLANDI**.
- Phase 27 (Stitch tarzı UI): **TAMAMLANDI**.
- Phase 28 (Türkçe tarih seçici + ana sayfa vitrini): **TAMAMLANDI**.
- Phase 29 (Şehir + ön değerlendirme kaldırma): **TAMAMLANDI**.
- Phase 30 (Form kısaltma + yorum vitrini): **TAMAMLANDI**.
- Phase 31 (Kısa soru seti; uçuş/otel soru değil): **TAMAMLANDI**.
- Phase 32 (Pasaportla tek adım): **TAMAMLANDI**.
- Phase 33 (Fotoğraf Kontrolü): **TAMAMLANDI** — `testing_agent_v3` iteration_24.json backend 12/12 PASS.

Test:
- iteration_23.json — Pasaportla Tek Adım: backend 5/5, frontend 6/6, **%100**.
- iteration_24.json — Fotoğraf Kontrolü: backend 12/12, **%100**.

---

### Phase 34 — Kod İncelemesi Düzeltmeleri (Refactor) — **COMPLETED (2026-09-02)**
**Kritik (düzeltildi)**
- `routes_public._store_upload`, `routes_public.check_photo_document`, `routes_admin._put_visa_document`:
  `result` / `message` değişkenleri fonksiyon başında tip belirtilerek initialize edildi (linter "used before assignment" uyarısı kapatıldı).

**Karmaşıklık düşürüldü (hepsi artık < 12)**
- `routes_public.submit_missing_documents` → `_ensure_upload_exists`, `_collect_extra_documents`, `_apply_traveler_documents`, `_notify_documents_uploaded`
- `routes_public._find_application_for_tracking` → `_tracking_last_names`
- `routes_zami.zami_readiness` → `_capture_check`, `_mapping_checks`, `_traveler_check`, `_browser_check`, `_session_check`
- `routes_store.create_order` → `_build_order_lines`, `_build_order_line`, `_parse_trip_start`, `_pricing_block`, `_payment_block`, `_bank_transfer_details`, `_notify_new_order`
- `routes_store.create_application_order` → `_application_order_items`, `_application_order_note`, `_pricing_block`

**Temizlik**
- Kullanılmayan importlar kaldırıldı (`content.ADDONS`, `fastapi.Request`). `flake8 --select=F,E9` temiz.

**`is` vs `==` bulgusu → FALSE POSITIVE**
- Kod tabanındaki tüm kullanımlar `is None` / `is not None` biçiminde; literal karşılaştırması yok. Değişiklik gerekmedi (`==`'e çevirmek Python'da yanlış olurdu).

**Test**
- `testing_agent_v3` iteration_25.json → backend **30/30 %100 PASS**, davranış regresyonu yok.
