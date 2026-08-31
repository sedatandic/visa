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
  - **Koyu mod yok** (tamamen kaldırıldı).
  - **Gerçek görseller**: Burj Khalifa hero, Sheikh Zayed yolu, ofis, pasaport/belge flatlay.
  - **Müşteri deneyimleri**: 4,9/5 puan özeti + memnuniyet barları + doğrulanmış yorum kartları (DB tabanlı).
  - **Örnek vize**: Kişisel verileri gizlenmiş (blur) + “ÖRNEKTİR/SPECIMEN” filigranlı BAE e-vize örneği.
  - **UAE + TR bayrak ikonları**: navbar/footer ve içerik içinde (Türkiye → BAE vurgusu).
  - **TÜRSAB + acente şeffaflığı**: footer + hakkımızda’da TÜRSAB rozeti ve acente detayları (admin’den yönetilebilir).
  - **GDRFA referansı**: Ana sayfada “Yetkili Merciler” güven şeridi + footer’da GDRFA rozeti (temsili SVG).
- **Sadece vize hizmeti**: otel/tur/transfer içerikleri kaldırıldı.
- **Başvuru evrak standardı (güncel)**:
  - **Her yolcu için zorunlu:** Pasaport + vesikalık fotoğraf.
  - **Tüm başvuru için zorunlu:** **Uçak bileti/rezervasyon** + **otel/konaklama rezervasyonu**.
- **SEO büyüme hedefi (tamamlandı):**
  - Her vize tipi için Google’dan müşteri çekecek **Vize Rehberi (SEO landing)** sayfaları.
  - Sayfa bazlı meta/canonical/OG + JSON-LD + sitemap/robots.
- **Operasyonel verim + dönüşüm (tamamlandı):**
  - **Eksik belge hatırlatma otomasyonu** (otomatik + admin’den manuel tetikleme) ile belge toplama süresini kısaltmak.
  - **Rehber içerik yönetimi**: Vize rehber metinleri ve SSS’leri admin panelinden düzenlenebilir hale getirmek.
- **Müşteri yaşam döngüsü (tamamlandı):**
  - **Müşteri Hesabı + Taslak**: müşterinin e-posta ile giriş yapıp başvurularını görmesi, yarım kalan başvuruya devam etmesi ve eski başvurudan kopyalayarak yeni başvuru başlatması.
  - **Sepeti kurtarma (taslak hatırlatma)**: yarım kalan taslaklara otomatik hatırlatma e-postası.
  - **Aile profili**: kayıtlı yolcuları hesapta saklayıp başvuruda tek tıkla ekleme.
- **Fiyatlandırma (tamamlandı):**
  - **TL tahsilat + USD baz fiyat + canlı kur**: 30 gün **110$** baz alınarak tüm fiyatların canlı kurla TL’ye çevrilmesi (admin kur payı ve manuel kur kontrolü ile).
  - **Kur şeffaflığı**: müşteriye kurun “bugün güncellendi” bilgisi ve güncel kur gösterimi.

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
**Amaç:** Eksik evrak nedeniyle bekleyen başvuruları hızla tamamlatmak ve SEO rehberlerini admin panelinden yönetilebilir hale getirmek.

#### A) Belge Hatırlatma (otomatik + manuel) — **DONE**
- Backend:
  - `backend/doc_reminders.py`: `missing_documents`, `send_document_reminder`, `pending_applications`, `run_reminder_sweep`, 6 saatlik scheduler loop.
  - `routes_public.py`:
    - `GET /api/applications/track` cevabına `missing_documents` eklendi.
    - `POST /api/applications/{code}/documents` ile müşteri eksik belgeleri takip sayfasından yükleyebiliyor (soyad doğrulamalı). Eksikler bitince status `reviewing`.
  - `routes_admin.py`:
    - `GET /api/admin/applications/{id}/missing-documents`
    - `POST /api/admin/applications/{id}/send-document-reminder`
    - `GET /api/admin/document-reminders/pending`
    - `POST /api/admin/document-reminders/run`
  - `emailer.py`: `document_reminder_html` + müşteri belge yükledi admin bildirimi (`documents_completed_admin_html`).
- Frontend:
  - `Track.jsx`: eksik belge paneli + upload + gönder.
  - `AdminApplicationDetail.jsx`: eksik belgeler paneli + hatırlatma butonu.

#### B) Rehber Yönetimi — **DONE**
- Backend:
  - `GET/PUT/DELETE /api/admin/visa-guides/{slug}` override kaydet/sıfırla.
- Frontend:
  - Yeni admin sayfası: `/admin/vize-rehberleri` (`AdminVisaGuides.jsx`).
  - Menü linki eklendi.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_12.json): PASS.

---

### Phase 13 — Müşteri Hesabı + Taslak (Tamamlandı)
**Amaç:** Müşterinin aynı e-posta ile başvurularını görmesi, yarım kalan başvuruya devam etmesi ve tekrar başvuru yapabilmesi.

**Backend (routes_account.py)**
- Müşteri giriş:
  - `POST /api/account/request-code` (6 haneli kod)
  - `POST /api/account/verify-code` (token üretir)
  - `POST /api/account/login-lastname` (e-posta + soyad ile giriş)
- Hesap:
  - `GET /api/account/me` (başvurular + taslaklar)
  - `GET /api/account/applications/{id}` (kendi başvurusu)
  - `GET/DELETE /api/account/drafts/{id}`
- Taslak:
  - `POST /api/drafts` (taslak kaydet/güncelle; resume_code üretir)
  - `GET /api/drafts/{draft_id}?code=...` (devam)
- E-posta şablonları:
  - `emailer.py`: `login_code_html`, `draft_saved_html`
- Resend gelene kadar admin destek:
  - `GET /api/admin/login-codes?email=` (admin-only; kodu görüp kullanıcıya iletmek için)

**Frontend**
- Yeni sayfa: `/hesabim` (`MyAccount.jsx`)
  - İki giriş yöntemi (e-posta+soyad / e-posta kodu)
  - Başvuru listesi, eksik belge uyarısı, “Bu bilgilerle yeni başvuru”
  - Taslak listesi, “kaldığım yerden devam et”, taslak sil
- Başvuru formu (`Apply.jsx`):
  - “Kaydet, sonra devam et” butonu
  - `?taslak={id}&kod={resume_code}` ile taslaktan devam
  - `?kopya={application_id}` ile önceki başvurudan kopyalama (belgeler hariç)
- Navbar: “Başvurularım” linki eklendi.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_12.json): PASS.

---

### Phase 14 — USD Bazlı Fiyat + Canlı Kur (Tamamlandı)
**Amaç:** TL tahsilat devam ederken fiyatları USD bazlı yönetmek; 30 gün için 110$ baz alınarak tüm fiyatları canlı kurla TL’ye çevirmek.

**Backend**
- `content.py`:
  - `price_usd` alanları eklendi (30 gün tek giriş = **110$**; diğerleri oransal).
  - `compute_pricing(..., addon_prices=...)` desteği.
- `fx.py`:
  - Canlı kur (open.er-api.com; fallback exchangerate.host)
  - 24 saatlik lazy refresh
  - Varsayılan kur payı %2
  - Manuel sabit kur
  - TL 10’luk yuvarlama
- Fiyatın geçtiği tüm yerler USD→TL bağlı:
  - `GET /api/visa-types`, `GET /api/visa-guides`, `GET /api/visa-guides/{slug}`, `POST /api/pricing/quote`, `GET /api/content/site` addons.

**Admin**
- `GET/PUT /api/admin/fx`
- `AdminVisaTypes.jsx`: kur kartı + USD fiyat düzenleme (`price_usd`) + TL ön izleme.

**UI**
- Kartlarda ve rehber sayfasında TL fiyatın altında: **“≈ 110 $ · güncel kurla TL tahsil edilir”** notu.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_12.json): PASS.

---

### Phase 15 — Kur Şeffaflığı + Sepeti Kurtarma + Aile Profili (Tamamlandı)
**Amaç:** Kur bilgisini şeffaflaştırmak, yarım kalan başvurulardan dönüşümü artırmak ve aile yolcu profilini tekrar kullanılabilir yapmak.

#### A) Kur Şeffaflığı — **DONE**
- Backend:
  - Public endpoint: `GET /api/fx` → sadece **effective_rate, currency_pair, fetched_at, source** (hassas alanlar dönmez).
- Frontend:
  - Yeni bileşen: `FxNote.jsx`.
  - Yerleşim:
    - Ana sayfa fiyat bölümünde (badge)
    - `/vize-tipleri` fiyat üstünde (badge)
    - Rehber sayfası fiyat kutusunda (inline)
    - Başvuru özetinde (inline)
  - Metin: **“1 $ = X ₺ · kur bugün güncellendi”**.

#### B) Sepeti Kurtarma (Taslak Hatırlatma) — **DONE**
- Backend:
  - `doc_reminders.py` içine taslak sweep eklendi:
    - 24 saat sonra ilk hatırlatma
    - 72 saat aralık
    - Max 2 hatırlatma
    - Başvuruya dönüşmüş taslaklar atlanır
  - `emailer.py`: `draft_reminder_html`
  - Scheduler loop: 6 saatlik döngüye taslak sweep dahil.
- Admin:
  - `GET /api/admin/draft-reminders/pending`
  - `POST /api/admin/draft-reminders/run`

#### C) Aile Profili (Kayıtlı Yolcular) — **DONE**
- Backend:
  - Koleksiyon: `saved_travelers`
  - Account API:
    - `GET /api/account/travelers`
    - `POST /api/account/travelers` (upsert; aynı pasaportla tekrar eklenmez)
    - `DELETE /api/account/travelers/{id}`
  - Otomasyon:
    - Başvuru oluşturulunca yolcular otomatik `upsert` edilir.
    - Mevcut başvurular için tek seferlik backfill: **61 kayıt**.
    - Başvuru sonrası aynı e-postanın taslakları otomatik silinir.
- Frontend:
  - `/hesabim` içinde “Kayıtlı yolcularım” bölümü (liste + sil).
  - `Apply.jsx`: giriş yapmış kullanıcıya “Kayıtlı yolcularım” paneli ve **tek tıkla yolcu ekleme**.
  - Giriş yapılmamışsa panel görünmez.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_13.json): **backend 46/46 PASS**, frontend **%100 PASS**.

---

## 3. Next Actions
1. **Canlı E-posta Testi (Resend) — BEKLEMEDE (P0)**
   - Gerekli env:
     - `RESEND_API_KEY` (kullanıcı sağlayacak)
     - `SENDER_EMAIL` (domain doğrulanmış adres önerilir)
   - E2E doğrulanacak mailler:
     - `application_received`
     - `bank_transfer_instructions`
     - `payment_received`
     - `visa_delivered`
     - `document_reminder`
     - `login_code`
     - `draft_saved`
     - `draft_reminder`
2. **Stripe prod geçişi (opsiyonel) — P1**
   - Canlı anahtarlar + webhook secret + success/cancel URL’leri.
3. **İçerik onayı ve gerçek veriler — P1**
   - Banka bilgileri (`/admin/banka`) gerçek değerlerle.
   - TÜRSAB/acente ticari bilgiler (`/admin/acente`) gerçek değerlerle.
4. **Operasyonel güvenlik (opsiyonel) — P2**
   - Admin şifresi değişimi, rate limit/bot koruması.

---

## 4. Success Criteria
- POC: Mongo write/read + objstore upload/download + Stripe checkout+status update + email skip mekanizması hatasız.
- V1: Kullanıcı başvuru oluşturur, evrak yükler, Stripe ödemesi yapar, success sayfası DB’de “paid” doğrular.
- Takip sayfası referans koduyla doğru başvuruyu gösterir ve “ödemeyi tamamla” çalışır.
- Admin: giriş yapar, başvuruları listeler, detayda dosyaları görür, durum günceller.
- Çoklu yolcu (aile) başvurusu + otomatik fiyat/indirim + admin vize PDF yükle/gönder akışları sorunsuz.
- AI pasaport okuma: pasaport yüklenince form alanları otomatik dolar.
- Havale/EFT: kullanıcı bank transfer seçer; admin “mark-paid” ile onaylar.
- Banka ve acente yönetimi: admin panel verileri site ve e-postalarda doğru görünür.
- **Zorunlu evraklar**:
  - Her yolcu: pasaport + vesikalık zorunlu.
  - Başvuru geneli: **uçak bileti + otel rezervasyonu zorunlu** ve backend+frontend doğrulaması mevcut.
- **Vize Rehberi SEO**:
  - 9 rehber sayfası çalışır; meta/canonical/OG + JSON-LD (Service+FAQ+Breadcrumb) doğru üretilir.
  - `sitemap.xml` ve `robots.txt` ile indekslenebilir.
  - Rehberden `/basvuru?vize=...` ile doğru vize ön-seçimi yapılır.
- **Kart tıklama UX**:
  - Home ve /vize-tipleri sayfalarında kart gövdesi tıklaması yanlışlıkla başvuruya yönlendirmez.
- **Eksik belge hatırlatma**:
  - Admin manuel hatırlatma gönderir; arka plan scheduler sweep çalışır.
  - Müşteri takip sayfasından eksikleri yükler; tamamlanınca status `reviewing` olur ve admin bilgilendirilir.
- **Rehber yönetimi**:
  - Admin rehber içeriklerini düzenler/sıfırlar; frontend rehber sayfasında override içerik görünür.
- **Müşteri hesabı + taslak**:
  - `/hesabim` üzerinden giriş (kod veya soyad) çalışır; başvurular ve taslaklar listelenir.
  - Başvurudan kopyalayarak yeni başvuru başlatma çalışır.
  - Taslak kaydetme ve devam etme çalışır.
- **Sepeti kurtarma (taslak hatırlatma)**:
  - 24 saat sonra otomatik hatırlatma çalışır; başvuruya dönüşen taslaklara mail gitmez.
  - Admin pending/run endpointleri ile manuel tetikleme yapılabilir.
- **Aile profili**:
  - Yolcular otomatik kaydolur; `/hesabim` sayfasında görünür; başvuruda tek tıkla eklenebilir.
- **USD baz fiyat + canlı kur + şeffaflık**:
  - 30 gün tek giriş = 110 USD baz; TL fiyatlar canlı kurla hesaplanır.
  - Admin kur payı / manuel kur ile fiyat kontrolü yapabilir.
  - Müşteri arayüzünde “kur bugün güncellendi” bilgisi ve kur değeri görünür.
- `RESEND_API_KEY` yokken hiçbir kritik akış kırılmaz; tüm “atlanan” mailler `email_outbox`’a kaydolur.
- Canlı Resend anahtarı verildiğinde e-postalar gerçek adrese gider ve outbox “sent” olarak kaydolur.

---

## DURUM (2026-08-31)
- Phase 1–14: **TAMAMLANDI**.
- Phase 15: **TAMAMLANDI** — kur şeffaflığı + sepeti kurtarma + aile profili.

Test:
- `testing_agent_v3` iteration_13.json — **backend 46/46 PASS**, frontend **%100 PASS**.

Kalan opsiyonel işler: **RESEND_API_KEY ile canlı e-posta doğrulaması**, Stripe prod geçişi, içerik/hukuk onayı, gerçek banka/acente bilgileri, operasyonel güvenlik ayarları.
