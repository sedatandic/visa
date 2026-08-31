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
- **Ek ürün satışları (kısmen tamamlandı):**
  - Mağaza sayfaları üzerinden **eSIM** ve **seyahat sigortası** satışı: **DONE**.
  - Yeni hedef (P0): **Vize başvurusu içinde** (Apply.jsx) eSIM + sigortayı **gerçek ürün kataloğundan** seçtirerek upsell.
  - Kullanıcı kararı:
    - Sigorta **yolcu başına** (fiyat × yolcu sayısı), tek plan seçilir (Temel vs Geniş).
    - eSIM: **adet seçilebilir**; varsayılan adet **yolcu sayısı**.
    - Form içinde **tüm eSIM paketleri** listelenir.

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

### Phase 17 — Vize Başvurusu İçinde eSIM + Sigorta Upsell — **COMPLETED**
**Amaç:** Vize başvurusu (Apply.jsx) içinde eSIM ve sigorta satın aldırmak; fiyatlama/ödeme/teslimatın admin sipariş akışıyla uyumlu olması.

#### A) Backend Model & Şema Genişletme — **TODO**
1) `backend/models.py`
- `StoreItemIn`:
  - `product_id: str`
  - `quantity: int` (1..MAX_QTY)
- `ApplicationCreate` içine:
  - `store_items: List[StoreItemIn] = []` (vize başvurusu içinde alınan ürünler)
- `QuoteRequest` içine:
  - `store_items: List[StoreItemIn] = []`

2) DB kaydı
- `applications` dokümanına:
  - `store_items` (ürün satırları: id, kind, name, qty, unit_price_try, unit_price_usd, total_try, fx_rate)
  - `linked_order_id` veya `linked_order_reference` (opsiyonel)

#### B) Otoritatif Fiyatlama — **TODO**
1) `backend/content.py` / `compute_pricing`
- Mevcut: `visa_prices + addons`
- Yeni: `store_lines` desteği:
  - Ürün satırları store kataloğundan fiyatlanır (USD→TRY live FX).
  - Çıktıya eklenir:
    - `store_items` (line list)
    - `store_total`
    - `total = visa_subtotal - discount + addons_total + store_total`

2) Ürün fiyat kaynağı
- `routes_store.product_list()` katalog kaynağı olarak kullanılacak.
- Tekilleştirme: Form içindeki ürünler **store_products** ile aynı ID’leri kullanmalı.

#### C) Public API’lerde store_items desteği — **TODO**
1) `POST /api/pricing/quote`
- Payload: `visa_type_ids`, `addons`, `store_items`
- Response: mevcut quote + `store_items/store_total` satırları.

2) `POST /api/applications`
- Payload: `contact, travelers, travel, addons, extra_documents, store_items, kvkk_accepted`
- Server doğrulama:
  - Product_id katalogda var mı?
  - Qty limitleri
- Başvuru dokümanına fiyat satırlarını kaydet.

#### D) “Başvuruya Bağlı Sipariş” Oluşturma — **TODO**
**Hedef:** Admin’in zaten kullandığı `/admin/orders` teslimat paneli ile uyumlu olsun.
- `POST /api/applications` sırasında eğer `store_items` doluysa:
  - `orders_col` (store_orders) içinde bir sipariş oluştur:
    - `reference_code: SV-...`
    - `items: ...`
    - `contact` (başvurudaki)
    - `source: "visa_application"`
    - `application_id: ...`
    - `payment` başlangıçta `pending`
  - `applications` dokümanına `linked_order_id` yaz.

#### E) Ödeme Senkronizasyonu — **TODO**
1) Kart ödemesi (Stripe)
- `routes_payments.py` içinde uygulama ödeme webhook’unda:
  - Application `paid` olduğunda bağlı order varsa onu da `paid/processing` yap.

2) Havale
- Admin “mark paid” akışı (mevcut) uygulama ve order için uyumlu hale getirilecek:
  - Uygulama havale onayında bağlı order da `paid` olsun.

#### F) Frontend (Apply.jsx) — Ek Hizmetler Adımı UI/UX — **TODO**
**Mevcut durum:** Ek hizmetler (addons) toggle listesi var ama sadece metadata üzerinden; eSIM/sigorta ürün kataloğu & adet seçimi yok.

1) Veri çekimi
- `GET /api/products?kind=esim` ile tüm eSIM paketlerini çek.
- Sigorta planları için iki seçenek:
  - ya store katalogdan `kind=insurance` çek,
  - ya legacy addon kartlarını koruyup store’a bağlayacak mapping (önerilmez).
  - Bu fazda: **store katalogdan çekmek** tercih.

2) UI kuralları
- Sigorta:
  - Radyo seçim: `Temel` vs `Geniş`.
  - Fiyat gösterimi: `+ ₺... / kişi`.
  - Quantity otomatik: `traveler_count`.
- eSIM:
  - Paket kart listesi (tüm paketler).
  - Seçilen paket için quantity stepper:
    - Default: `traveler_count`
    - Kullanıcı artır/azalt (1..MAX_QTY)

3) Özet (Summary)
- Quote response içindeki `store_items` satırlarını da göster:
  - `eSIM 10GB x3` gibi
  - Sigorta planı `x{traveler_count}`
- Toplam: `quote.total`

4) Submit payload
- `addons` (express vb.) + `store_items` birlikte gönderilecek.

#### G) Test / Doğrulama — **TODO**
- Backend:
  - Quote: 2 yolcu + insurance_plus + esim_unlimited qty=2 → totals doğru.
  - Application create: store order oluşuyor mu? application.linked_order_id set mi?
  - Payment paid: order paid oluyor mu?
- Frontend:
  - Apply.jsx ek hizmetler adımı görsel doğrulama (kartlar/stepper/radio).
  - Toplam güncelleme (traveler sayısı değişince sigorta qty otomatik güncellenir).
  - Başvuru gönderimi: backend’e store_items gidiyor mu?

---

## 3. Next Actions

### P0 — Phase 17’yi Tamamla: Vize İçinde Upsell (eSIM + Sigorta)
1) Backend model ve API genişletme (models, quote, applications)
2) Fiyat motoru: compute_pricing store_lines
3) Başvuruya bağlı order oluşturma + ödeme senkronizasyonu
4) Frontend Apply.jsx: ürün listeleri + adet seçimi + özet
5) Backend+Frontend testleri (testing agent + screenshot)

### P0 — Canlı E-posta Testi (Resend) — BEKLEMEDE
- Gerekli env:
  - `RESEND_API_KEY`
  - `SENDER_EMAIL` (domain doğrulanmış)
- E2E doğrulanacak mailler: application/order lifecycle + reminder + login/draft.

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
- **Phase 17 (yeni) başarı kriterleri:**
  1) Apply.jsx içinde:
     - Sigorta planı seçilebilir (Temel/Geniş), otomatik `qty = yolcu sayısı`.
     - eSIM paketleri listelenir, paket seçimi + adet stepper çalışır (default yolcu sayısı).
     - Özet satırları ve toplam fiyat canlı güncellenir.
  2) Backend:
     - `POST /api/pricing/quote` store_items ile doğru fiyat satırlarını döner.
     - `POST /api/applications` store_items ile uygulama oluşturur ve fiyatları authoritative hesaplar.
     - Store ürünleri için `orders_col` kaydı otomatik oluşur (admin teslimat panelinde görünür).
  3) Ödeme:
     - Kart ödemesi: application paid → linked order paid/processing.
     - Havale: admin onayı → linked order paid.
  4) Teslimat:
     - Admin sipariş ekranından eSIM QR / poliçe PDF yükleyebilir.
     - Müşteri e-postası + hesap/sipariş sayfası üzerinden dosyaları indirebilir.

---

## DURUM (2026-08-31)
- Phase 1–16: **TAMAMLANDI**.
- Phase 17: **TAMAMLANDI** (2026-08-31).
  - Backend: `StoreItemIn` + `store_items` (quote & application), `compute_pricing(store_lines=...)`, `resolve_store_lines()`, `create_application_order()` (source=visa_application), `sync_application_order_payment()` (kart/havale/admin mark-paid).
  - Frontend: `Apply.jsx` adım 2'de sigorta planı (yolcu başına, tek seçim) + tüm eSIM paketleri (adet stepper, varsayılan yolcu sayısı); özet satırları + canlı FX toplam. AdminOrders'da 'Vize başvurusu ile alındı' etiketi; AdminApplicationDetail fiyat dökümünde store satırları + bağlı sipariş kodu.
  - Test: iteration_15.json backend 51/52 (kritik yok) + kendi E2E scriptim: başvuru + bağlı sipariş + havale + admin mark-paid senkronu **PASS**.

### Phase 18 — Ek Ürün Geçerlilik Tarihlerinin Seyahat Tarihine Bağlanması — **COMPLETED (2026-08-31)**
- Backend: `resolve_store_lines(items, arrival_date, departure_date)` → her satırda `validity_days`, `starts_on`, `ends_on`, `trip_days`, `covers_trip`. `QuoteRequest`e `arrival_date/departure_date` eklendi; `/applications` seyahat tarihlerini kullanıyor. Bağlı sipariş ve standalone mağaza siparişi item'larına da `starts_on/ends_on` yazılıyor. E-postalarda tarih aralığı görünüyor.
- Frontend: `Apply.jsx` — giriş tarihi girilmeden eSIM/sigorta seçimi kapalı (bilgilendirme notu), her kartta "10 Ekim 2026 tarihinde başlar · 24 Ekim 2026 tarihine kadar geçerli" bilgisi, seyahat süresi paketten uzunsa uyarı; özet satırlarında tarih aralığı. AdminOrders ve AdminApplicationDetail'de tarih aralığı gösterimi.
- Test: canlı UI doğrulaması (screenshot) + E2E script: başvuru/sipariş/mağaza satırlarında tarihler **PASS**.

Test:
- `testing_agent_v3` iteration_13.json — backend **46/46 PASS**, frontend **%100 PASS**.
- `testing_agent_v3` iteration_14.json — backend **38/40 (kritik yok)**, frontend **%100**; kalan 2 senaryo manuel doğrulandı.


### Phase 19 — Akıllı Paket Önerisi + Seyahat Paketi İndirimi (%10) — **COMPLETED (2026-08-31)**
Kullanıcı kararları: indirim %10 (ek ürün toplamı), hem başvuru içinde hem mağaza sepetinde geçerli, öneri "Sizin için önerilen" etiketi + "Önerilenleri ekle" butonu (otomatik seçim yok).
- Backend: `content.BUNDLE_DISCOUNT` + `bundle_discount_amount()`; `compute_pricing` çıktısına `bundle_discount / bundle_discount_rate / bundle_discount_title`; `/api/products` yanıtına `bundle`; mağaza siparişlerinde (`/api/orders`) ve başvuruya bağlı siparişte `items_total`, `bundle_discount`, indirimli `price`; e-postalarda indirim satırı. Stripe tahsilatı indirimli tutarı kullanıyor.
- Frontend: `Apply.jsx` paket promosyon kutusu (`bundle-promo-box`), seyahat süresine göre en uygun paket için `Sizin için önerilen` etiketi, `Önerilenleri ekle` butonu, indirim satırları (iki özet alanında). `StoreCheckout.jsx` çapraz satış bölümü (diğer kategori ürünleri) + indirim satırı; `OrderStatus`, `AdminOrders`, `AdminApplicationDetail` indirim/tarih gösterimi.
- Öneri algoritması: seyahat süresini karşılayan en ekonomik paket; hiçbiri karşılamıyorsa en uzun süreli paket.
- Test: E2E script (mağaza siparişi 1720→1548 ₺, tek kategori indirimsiz, başvuru toplamı 6958 ₺, bağlı sipariş 1548 ₺) **PASS** + canlı UI doğrulaması (screenshot).
