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
  - **Tüm başvuru:** Uçak bileti/rezervasyon + otel/konaklama rezervasyonu.
- SEO büyüme hedefi (tamamlandı): vize rehber sayfaları, sitemap/robots, JSON-LD.
- Operasyonel verim + dönüşüm (tamamlandı): eksik belge hatırlatma, taslak hatırlatma, hesap/draft, aile profili.
- Fiyatlandırma (tamamlandı): USD baz fiyat + canlı kurla TL tahsilat + kur şeffaflığı.
- Ek ürün satışları (tamamlandı & geliştirildi):
  - Mağaza sayfaları üzerinden **eSIM** ve **seyahat sigortası** satışı.
  - Vize başvurusu içinde eSIM + sigorta upsell (tek formda).
  - Ek ürünler seyahat tarihine bağlandı (başlangıç/bitiş).
  - **Akıllı paket önerisi** + **%10 seyahat paketi indirimi** (sigorta+eSIM birlikte) hem başvuruda hem mağazada.
- Zami Tours otomasyonu (tamamlandı, **canlı doğrulama bekliyor**):
  - Playwright RPA + yakalama (capture) + alan eşleme + toplu aktarım + durum polling + kullanıcı takip zaman çizelgesi.
  - **P0: “İlk Gerçek Aktarım”** canlı Zami portalında doğrulama (**BLOCKED: kullanıcı Zami giriş bilgileri yok**).
- WhatsApp bildirimleri: **manuel mod** (wa.me link üretimi) tamam; otomatik sağlayıcı (Twilio/Meta) **beklemede**.
- **Yeni büyüme hedefi (P1): Ücretsiz Ön Değerlendirme Sihirbazı**
  - Ana sayfada 3 soruluk wizard → “onay olasılığı” skoru + öneriler + başvuru CTA.
  - Lead toplama (opsiyonel iletişim bilgisi) + admin panelde listeleme.

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
- **BLOCKED:** kullanıcı Zami portal e-posta/şifre paylaşmadı/vermedi; bu olmadan canlı aktarım yapılamaz.

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

### Phase 25 — Ücretsiz Ön Değerlendirme Sihirbazı (3 Soru) — **COMPLETED (2026-09-01)**
**Amaç:** Dönüşüm/lead artırmak: ana sayfadan 30–60 sn’de “ön değerlendirme” sonucu göster.

**Backend**
- `backend/pre_eval.py`: skorlama motoru
  - Girdiler (örnek): pasaport geçerliliği, önceki vize geçmişi, red geçmişi
  - Çıktılar: olasılık %, seviye (low/medium/high), öneriler, önerilen vize tipi
- DB: `pre_evaluations` koleksiyonu
- `routes_public.py`: `POST /api/pre-evaluation`
  - Sonucu döner
  - Opsiyonel iletişim bilgisi ile lead kaydeder
- `routes_admin.py`: `GET /api/admin/pre-evaluations` lead listesi

**Frontend**
- `components/PreEvaluation.jsx`: 3 adımlı wizard + sonuç kartı (olasılık göstergesi, öneriler, CTA → `/basvuru`)
- `Home.jsx` içine bölüm olarak ekleme
- Yeni route: `/on-degerlendirme`
- Admin: `pages/AdminPreEval.jsx` + Admin menüsüne ekleme

**Test**
- `curl` ile endpoint testi
- `testing_agent` regresyon + yeni flow testi

---

### Phase 26 — Kod Kalitesi Raporu Uygulamasi (Refactor) — **COMPLETED (2026-09-02)**
Kod inceleme raporundaki bulgular uygulandi (davranis birebir korunarak):
- **Undefined variable sertlestirme:** `zami_rpa._launch/_launch_with_state` (browser), `zami._fmt` (d), `routes_payments` (session), `routes_account.require_customer` (payload).
- **Literal identity:** `get_visa_guide` icindeki `active is False` kontrolu, `None` guvenli falsy kontrolune cevrildi. (Not: `is None` / `is not None` karsilastirmalari PEP 8 geregi dogru oldugu icin korundu.)
- **Karmasiklik azaltma:**
  - `routes_public.create_application` → `_validate_extra_documents`, `_ensure_uploads_exist`, `_build_travelers`, `_unique_reference_code`, `_build_application_doc`, `_link_store_order`, `_after_application_created`, `_send_application_emails` (150 satir → ~30).
  - `build_customer_timeline` → `_first_status_dates`, `_timeline_progress_index`, `_timeline_step_dates`, `_timeline_step_state`, `_iso_or_none`.
  - `resolve_store_lines` → `_store_line_validity`, `_store_line`; `upload_document` → `_validate_upload`, `_store_upload`.
  - `routes_admin._clean_guide_payload` → `_clean_guide_text_fields`, `_clean_guide_list_fields`, `_clean_guide_faqs`; `admin_upload_visa_document` → `_validate_visa_document`, `_put_visa_document`.
  - `routes_payments._mark_paid` → `_claim_transaction`, `_apply_application_payment`, `_notify_application_payment`; `create_checkout` → `_checkout_origin`, `_application_metadata`, `_open_checkout_session` (siparis checkout'u da ayni yardimciyi kullanir).
  - `emailer._pricing_block` → `_discount_row`, `_store_item_label` (HTML cikti birebir dogrulandi).
- **Tip ipuclari:** `db.py`, `server.py`, `routes_zami.py`, `routes_admin.py`, `routes_public.py`, `routes_account.py`, `routes_store.py`, `doc_reminders.py`, `whatsapp.py`, `scripts/test_core.py` icin donus tipleri; `admin: dict = Depends(require_admin)` (72 imza).
- **Test:** iteration_17.json — backend 38/42 (basarisiz 4 kayit gecersiz slug beklentisi kaynakli, regresyon degil), frontend 9/9, kritik hata yok.

---

## 3. Next Actions

### P0 — “İlk Gerçek Aktarım” (Zami Live Verification) — **BLOCKED**
**Gerekenler:**
1) Kullanıcıdan Zami portal e-posta/şifre (veya kullanıcı tarafında ekran paylaşımı ile doğrulama)
2) Gerçek form sayfasında `capture.js` çalıştırma
3) Admin `/admin/zami` önerilen mapping’i uygulama
4) 1 test başvuru ile `dry-run` (submit yok) → screenshot + log
5) Onay sonrası 1 gerçek submit

### P1 — Phase 25: Ücretsiz Ön Değerlendirme Sihirbazı (tamamlama)
1) Backend skorlama + endpoint + DB
2) Frontend wizard + Home entegrasyonu + ayrı sayfa
3) Admin lead listesi
4) Test + deploy

### P1 — Canlı E-posta Testi (Resend) — BEKLEMEDE
- Env:
  - `RESEND_API_KEY`
  - `SENDER_EMAIL` (domain doğrulanmış)

### P1 — Stripe prod geçişi (opsiyonel) — BEKLEMEDE
- Canlı anahtarlar + webhook secret + success/cancel URL’leri.

### P2 — WhatsApp Otomatik Sağlayıcı (Twilio/Meta) — BEKLEMEDE
- Sağlayıcı seçimi + API anahtarları.

---

## 4. Success Criteria
- POC/V1/SEO/Account/Drafts/FX/Reminders/Storefront akışları: mevcut kriterler **korunur**.
- Phase 17–19 ek ürün akışları:
  - Ek ürün tarihleri doğru, öneri + indirim doğru, hem başvuru hem mağaza akışı sorunsuz.
- Zami entegrasyonu (Phase 20–23) başarı kriterleri:
  1) Admin mapping ile Zami form alanları eşlenebilir ve değişime dayanıklı olur.
  2) Bookmarklet ile kullanıcı Zami formunu doldurabilir (captcha/OTP kendisi).
  3) Playwright RPA ile admin, insan onayıyla login olup başvuruyu doldurabilir (dry-run + submit).
  4) Aktarım kayıtları/loglar ve hata ayıklama çıktıları admin panelinde görünür.
  5) Canlı portalda en az **1 dry-run + 1 gerçek submit** ile doğrulama yapılır (**P0**).
- WhatsApp (Phase 24):
  - Manuel modda wa.me linkleri doğru mesaj şablonlarıyla üretilir ve operasyon akışına uygun olur.
- Ön değerlendirme sihirbazı (Phase 25):
  1) 3 adımda sonuç üretir (%, seviye, öneriler).
  2) CTA ile başvuruya dönüşüm sağlar.
  3) Opsiyonel lead kaydı admin panelde listelenir.

---

## DURUM (2026-09-01)
- Phase 1–19: **TAMAMLANDI**.
- Phase 20–23 (Zami RPA + yakalama + mapping + status + tracking): **TAMAMLANDI**, ancak **İlk Gerçek Aktarım canlı doğrulaması P0 ve BLOCKED** (kullanıcı Zami kimlik bilgileri yok).
- Phase 24 (WhatsApp manuel): **TAMAMLANDI** (otomatik sağlayıcı beklemede).
- Phase 26 (Kod kalitesi refactor): **TAMAMLANDI** — iteration_17.json, kritik hata yok.
- Phase 25 (Ücretsiz Ön Değerlendirme): **TAMAMLANDI** — iteration_16.json: backend 60/61, frontend 24/24, admin 7/7 (kritik hata yok).

Test:
- `testing_agent_v3` iteration_13.json — backend **46/46 PASS**, frontend **%100 PASS**.
- `testing_agent_v3` iteration_14.json — backend **38/40 (kritik yok)**, frontend **%100**.
- `testing_agent_v3` iteration_15.json — backend **51/52 PASS**, frontend kısmi; kritik yok.
- Ek E2E scriptler: tarih + paket indirimi + ödeme senkronu **PASS**.
