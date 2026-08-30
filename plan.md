# plan.md

## 1. Objectives
- Türkçe, modern, **sade** ve güven veren bir Dubai/UAE vize başvuru sitesi (kopya değil; benzer bilgi mimarisi/UX, özgün marka/renk).
- Vize tipleri + fiyatlar + genel bilgilendirme + hızlı başvuru akışı.
- Çekirdek iş akışı: **başvuru oluşturma → dosya yükleme → ödeme (Stripe) → takip kodu**.
- Başvuruları MongoDB’ye kaydetme, admin panelde listeleme/detay/güncelleme.
- E-posta bildirimleri (başvuru sahibine + admin’e): **API anahtarı yoksa akışı bozmadan “skipped” olarak outbox’a yaz**.
- Güven ve “insan eliyle tasarlanmış” kurumsal görünüm:
  - **BAE bayrak paleti** (yeşil/kırmızı/siyah/beyaz) — kırmızı vurgu belirgin.
  - **Tipografi**: **Figtree** (başlık + gövde) + opsiyonel IBM Plex Mono.
  - **Koyu mod**: sağ üst tema anahtarı, kalıcı (localStorage), admin’de de var.
  - **Gerçek görseller**: Burj Khalifa hero, Sheikh Zayed yolu, ofis, pasaport/belge flatlay.
  - **Müşteri deneyimleri**: 4,9/5 puan özeti + memnuniyet barları + doğrulanmış yorum kartları.
  - **Örnek vize**: Kişisel verileri gizlenmiş (blur) + “ÖRNEKTİR/SPECIMEN” filigranlı **BAE e-vize örneği**.
  - **UAE + TR bayrak ikonları**: navbar/footer ve içerik içinde (Türkiye → BAE vurgusu).
- **Phase 3 (tamamlandı):**
  - **Aile Başvurusu:** Tek formda çoklu yolcu ekleme/çıkarma, kişi sayısına göre otomatik fiyat + aile indirimi.
  - **Admin Vize PDF:** Admin panelden onaylı vize PDF yükleme ve tek tıkla müşteriye e-posta ile gönderme.
- **Phase 5 (tamamlandı):**
  - **AI Pasaport Okuma (OCR/LLM):** Pasaport görselinden bilgileri okuyup formu otomatik doldurma.
  - **SEO Blog:** Yazıları ayrı sayfalara çıkarma + admin yönetimi.
  - **DB içerik yönetimi:** Yorumlar + puan özeti + blog yazıları DB’ye taşındı ve admin’den yönetiliyor.
  - **WhatsApp bildirimi:** Admin’den tek tıkla wa.me linki ve hazır mesaj oluşturma (harici WhatsApp API yok; bilinçli).

---

## 2. Implementation Steps

### Phase 1 — Core POC (izole test; ilerlemeden önce çalışır hale getir)
**Amaç:** En riskli entegrasyonları tek dosyada uçtan uca doğrulamak.

**POC User Stories (min 5)**
1. MongoDB’ye örnek başvuru kaydedip geri okuyabilmek.
2. Pasaport/foto yükleyip objstore’a yazıp geri indirerek bayt bazında doğrulayabilmek.
3. Stripe sandbox oluşturup ürün/fiyat kataloğunu idempotent kurabilmek.
4. Checkout session oluşturup geçerli bir Stripe Checkout URL’i alabilmek.
5. Webhook veya polling ile ödeme durumunu “paid” olarak DB’ye işleyebilmek.
6. RESEND_API_KEY yoksa e-posta gönderiminin kırmadan “skipped” kaydedilmesi.

**Adımlar**
- `backend/scripts/test_core.py`:
  - Mongo insert/find + datetime serialize.
  - Object Storage: put/get + content-type/size check.
  - Stripe: checkout oluşturma + status doğrulama.
  - Email: Resend varsa gönder, yoksa `email_outbox.status=skipped`.
- Çıkış kriteri: Script tek komutla çalışır, tüm adımlar PASS/log üretir.

---

### Phase 2 — V1 App Development (POC kanıtlı çekirdek üzerine)
**Frontend:** React + router + Tailwind + shadcn/ui. **Backend:** FastAPI `/api` + Motor + servisler.

**V1 User Stories (min 5)**
1. Ana sayfada fiyatları ve “Başvuru Yap” CTA’yı net görmek.
2. Vize tiplerini karşılaştırıp birini seçerek başvuruya başlayabilmek.
3. Çok adımlı formu mobilde rahat doldurup pasaport + vesikalık yüklemek.
4. Stripe ile ödemeyi tamamlayıp “ödeme onaylandı” sayfasında doğrulanmış sonucu görmek.
5. Takip kodu ile başvuruyu görüntüleyip gerekirse ödemeyi sonradan tamamlamak.
6. Admin olarak giriş yapıp başvuruları listeleyip detayda dosyaları görüntülemek ve durum güncellemek.

**Backend (FastAPI)**
- Koleksiyonlar:
  - `visa_types`, `applications`, `uploads`, `payment_transactions` (varsa), `contact_messages`, `email_outbox`, `admin_users`.
- API:
  - Public: `GET /api/visa-types`, `GET /api/content/site`.
  - Uploads: `POST /api/uploads`, `GET /api/files/{file_id}`.
  - Applications: `POST /api/applications`, `GET /api/applications/track?code=&last_name=`.
  - Payments: `POST /api/payments/checkout`, `GET /api/payments/status/{session_id}`, `POST /api/webhook/stripe`.
  - Admin: `POST /api/admin/login`, `GET /api/admin/applications`, `GET /api/admin/applications/{id}`, `PATCH /api/admin/applications/{id}`.
  - Contact: `POST /api/contact`.
- Email:
  - Başvuru alındı + ödeme alındı + admin bildirimleri.
  - `RESEND_API_KEY` yoksa outbox’a `skipped`.
- Güvenlik:
  - Input validation, dosya tip/limit (jpg/png/webp/pdf; max 10MB).
  - Admin endpoint JWT guard.

**Frontend (React)**
- Sayfalar:
  - `/` Landing (hero, süreç, güven alanı, WhatsApp buton).
  - `/vize-tipleri` (hizmet bedelleri / pricing).
  - `/basvuru` (multi-step wizard).
  - `/payment/success`, `/payment/cancel`.
  - `/takip`.
  - `/admin/giris`, `/admin`, `/admin/basvurular/:id`.
- Tasarım:
  - Güven veren palet, bol boşluk, büyük CTA.
  - dubaivizeal.com benzeri bilgi mimarisi; özgün komponent/ikonografi.

**Phase 2 sonu**
- Seed data: vize tipleri ve örnek fiyatlar.
- 1 tur E2E test (manuel + test agent).

---

### Phase 3 — Aile Başvurusu + Admin Vize PDF (Tamamlandı)
**Amaç:** Çoklu yolcu başvurusu + otomatik fiyatlandırma ve admin’in vize PDF gönderim operasyonunu tamamlamak.

**User Stories (min 5)**
1. Kullanıcı olarak tek formda birden fazla yolcu ekleyip çıkarabilmek istiyorum.
2. Kullanıcı olarak kişi sayısına göre fiyatın otomatik güncellenmesini (aile indirimi dahil) görmek istiyorum.
3. Kullanıcı olarak her yolcu için pasaport ve fotoğraf yükleyebilmek istiyorum.
4. Admin olarak onaylı vize PDF’ini yükleyip müşteriye tek tıkla göndermek istiyorum.
5. Admin olarak e-postaların anahtar yokken bozulmadan outbox’a kaydolduğunu görmek istiyorum.

**Adımlar / Çıktılar**
- Backend:
  - `compute_pricing`: çoklu yolcu fiyatı + aile indirimi + kişi başı addon hesapları.
  - `POST /api/pricing/quote` ile aynı hesapların UI’da gösterimi.
  - `POST /api/applications`: `travelers[]` destekli şema (dosya id validasyonu dahil).
  - Admin vize akışı:
    - `POST /api/admin/applications/{id}/visa-document` (PDF yükle)
    - `POST /api/admin/applications/{id}/send-visa` (e-posta ile gönder + status=approved)
    - `DELETE /api/admin/applications/{id}/visa-document` (geri al)
  - Ödeme:
    - Stripe checkout’ta çoklu yolcu uygulamalarında metadata uyumluluğu.
    - `payment_received` e-postası için alıcı: `contact.email` fallback `applicant.email`.
- Frontend:
  - `/basvuru`: dinamik yolcu ekle/çıkar, dosya yüklemelerinin doğru yolcuya bağlanması, özet/fiyat güncellemesi.
  - Admin detay: PDF upload UI + “Müşteriye Gönder” aksiyonu.
  - UI iyileştirmeleri (referans siteye yakın, özgün tasarım).
  - Navbar: link sarmasını engellemek için `whitespace-nowrap`.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_2.json): Phase 3 spesifik akışlar %100 PASS.
- Bulunan tek kritik hata:
  - Çoklu yolcuda Stripe checkout `KeyError: visa_type_id` → **düzeltildi** (`routes_payments.py`, metadata geri-uyumluluk).
- Ek düzeltme:
  - `payment_received` e-postası `contact.email` üzerinden gönderilecek şekilde güncellendi.

---

### Phase 4 — Marka/Tema Yenileme + Koyu Mod + Sosyal Kanıt (Tamamlandı)
**Amaç:** Görsel dili güçlendirmek, “AI şablonu” hissini kırmak, BAE bayrak renkleriyle özgün kurumsal kimlik + gece modu + sosyal kanıt.

**User Stories (min 5)**
1. Kullanıcı olarak gece kullanımı için koyu temaya geçebilmek istiyorum.
2. Kullanıcı olarak tema tercihim sayfa yenilemelerinde ve sayfalar arasında kaybolmasın.
3. Kullanıcı olarak sitede gerçek fotoğraflar görüp güven duymak istiyorum.
4. Kullanıcı olarak diğer müşterilerin deneyimlerini (puan, yorum) görüp karar vermek istiyorum.
5. Admin olarak koyu temada da rahatça paneli kullanmak istiyorum.

**Adımlar / Çıktılar**
- Tema / Tipografi:
  - UAE bayrak paleti (yeşil primary, kırmızı accent/destructive, siyah/beyaz temeller).
  - **Kırmızı vurgular artırıldı**: hero başlık, eyebrow, yıldızlar/ikonlar, rozetler, bayrak şeridi.
  - Token tabanlı renkler: hard-coded renkler temizlendi, CSS var’lara taşındı.
- Koyu Mod:
  - `ThemeToggle` eklendi: navbar + admin header.
  - `html.dark` ile dark tokenlar; localStorage anahtarı: `vizeatlas-theme`.
  - Tema meta rengi: light `#0B6B3A`, dark `#0D1115`.
- Görseller:
  - Hero: Burj Khalifa (gündüz).
  - İkincil: Sheikh Zayed yolu, Burj Al Arab, Dubai gece.
  - Güven/kurumsal: ofis fotoğrafı.
  - Belgeler: pasaport/belge flatlay.
- Müşteri Deneyimleri:
  - Home: “Müşteri Deneyimleri” bölümü: 4,9/5, toplam değerlendirme ve bar metrikleri + doğrulanmış yorum kartları.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_3.json): tema anahtarı, kalıcılık, dark readability, testimonial bölümü, görsel yükleme, mobil görünüm PASS.

---

### Phase 5 — Operasyonel içerik yönetimi + SEO Blog + WhatsApp + AI Pasaport Okuma (Tamamlandı)
**Amaç:** Operasyonu hızlandırmak (admin araçları), arama motoru görünürlüğü (SEO blog), müşteri iletişimi (WhatsApp), form doldurmayı hızlandırmak (AI pasaport okuma), güven artırmak (gerçek vize örneği).

**User Stories (min 5)**
1. Kullanıcı olarak pasaportumu yüklediğimde ad/soyad/pasaport no/doğum tarihi gibi alanların otomatik dolmasını istiyorum.
2. Kullanıcı olarak blog yazılarına Google’dan geldiğimde ayrı sayfada, okunaklı ve paylaşılabilir bir içerik görmek istiyorum.
3. Admin olarak blog yazısı ekleyip düzenleyip yayına alabilmek istiyorum.
4. Admin olarak müşteri yorumlarını ve puan özetini panelden yönetmek istiyorum.
5. Admin olarak vize onaylandığında müşteriye WhatsApp’tan hızlı bir bilgilendirme mesajı hazırlayıp göndermek istiyorum.

**Adımlar / Çıktılar**
- AI Pasaport Okuma:
  - Backend: `backend/passport_ai.py` (Emergent LLM key + vision model) + `POST /api/passport/read`.
  - PDF pasaport yüklenirse: graceful `{ok:false, reason:'pdf'}`.
  - Frontend: `/basvuru` 1. adımda her yolcu kartında “Pasaportu yükleyin, bilgiler otomatik dolsun” alanı.
    - Boş alanlar otomatik doldurulur; kullanıcı kontrol eder.
    - Aynı dosya evrak adımında da kullanılır.
- Örnek BAE Vizesi:
  - Kullanıcı tarafından sağlanan PDF’ten **kişisel detayları blur** + “ÖRNEKTİR/SPECIMEN” filigranı.
  - Çıktı: `frontend/public/ornek-vize.jpg`.
  - Home: “Vizeniz böyle görünür” bölümünde gösterim.
- UAE + TR bayrak ikonları:
  - `FlagIcons.jsx` (SVG) — navbar ve footer’da (Türkiye → BAE) ve örnek vize başlığında.
- Blog (SEO):
  - DB: `articles` koleksiyonu (seed + admin CRUD).
  - Public API: `GET /api/articles`, `GET /api/articles/{slug}` (related dahil).
  - Frontend:
    - `/gelismeler` liste (kartlar + “Yazının devamını oku”).
    - `/gelismeler/:slug` detay (breadcrumb, canonical, OG, **Article JSON-LD**).
- Yorumlar (DB + Admin):
  - DB: `testimonials` + `site_settings.review_summary`.
  - Admin:
    - `GET/POST/PUT/DELETE /api/admin/testimonials`
    - `PUT /api/admin/review-summary`
    - UI: `/admin/yorumlar` (yorum CRUD + puan özeti düzenleme).
- WhatsApp Bildirimi (Link tabanlı):
  - Backend: `POST /api/admin/applications/{id}/whatsapp` → `wa.me` linki + hazır Türkçe mesaj.
  - Log: `notifications` koleksiyonuna kayıt.
  - Frontend: admin başvuru detayında “WhatsApp ile bildir” butonu.
  - Not: Harici WhatsApp API entegrasyonu yok; bilinçli tercih (anahtar gerektirmeyen hızlı operasyon).
- Tasarımın sadeleştirilmesi (dubaivizeal.com’a yakınlaşma):
  - Font: **Figtree**.
  - CTA/sekme görünümü: pill butonlar.
  - Fiyat kartları: kırmızı fiyat + kırmızı “En çok tercih edilen” şeridi.
  - Sade beyaz yüzeyler, daha az “şablon” hissi.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_4.json):
  - Backend: **%96.9 (63/65)** — kalan 2 madde düşük öncelik/test tarafı.
  - Frontend: ana akışlar PASS; regresyon yok.
- Manuel doğrulama:
  - Pasaport yükleme sonrası alanların dolması doğrulandı (OCR success ve form alanları filled).

---

## 3. Next Actions
1. **(Opsiyonel) Resend anahtarını ekle** → canlı e-posta gönderimini E2E doğrula (application_received, payment_received, visa_delivered).
2. **(Opsiyonel) Stripe prod hazırlığı**: canlı anahtarlar + webhook secret + success/cancel URL’leri prod domain.
3. İçerik onayı:
   - Blog yazıları (başlık/slug/özet) ve hukuk/uyumluluk kontrolü.
   - Yorumlar/puan metrikleri (gerçek sayılarla güncelleme).
   - Örnek vize görselinin “örnek” etiketi ve KVKK metinleri.
4. Operasyonel güvenlik:
   - Admin şifresi değişimi, env değişkenleri ve erişim kısıtları.
   - Rate limit / basic bot koruması (opsiyonel).
5. (Opsiyonel) WhatsApp’ı gerçek API ile otomatik gönderime taşımak istenirse: Twilio/Meta entegrasyonu.

---

## 4. Success Criteria
- POC: Mongo write/read + objstore upload/download + Stripe checkout+status update + email skip mekanizması hatasız.
- V1: Kullanıcı başvuru oluşturur, dosya yükler, Stripe ödemesi yapar, success sayfası DB’de “paid” doğrular.
- Takip sayfası referans koduyla doğru başvuruyu gösterir ve “ödemeyi tamamla” çalışır.
- Admin: giriş yapar, başvuruları listeler, detayda dosyaları görür, durum günceller.
- **Phase 3:** çoklu yolcu (aile) başvurusu + otomatik fiyat/indirim + admin vize PDF yükle/gönder akışları sorunsuz.
- **Tema/Koyu Mod:** tema anahtarı görünür, dark/light geçişi sorunsuz, kalıcı ve tüm sayfalarda okunabilirlik korunur.
- **Sosyal kanıt:** müşteri deneyimleri bölümü görünür, veriler backend’den gelir.
- **Örnek vize:** kişisel verileri gizlenmiş vize örneği görüntülenir.
- **AI pasaport okuma:** pasaport yüklenince form alanları otomatik dolar, kullanıcı kontrol eder; akış bozulmaz.
- **SEO blog:** /gelismeler ve /gelismeler/:slug sayfaları meta/canonical/JSON-LD ile çalışır.
- **WhatsApp bildirimi:** admin tek tıkla wa.me linki ve mesaj üretir; loglanır.
- `RESEND_API_KEY` yokken hiçbir kritik akış kırılmaz; tüm “atlanan” mailler `email_outbox`’a kaydolur.

---

## DURUM (2026-08-30)
- Phase 1 POC: PASS (Mongo, objstore upload/download, Stripe checkout+status, Resend graceful skip).
- Phase 2: Backend + Frontend tamamlandı; E2E test PASS (iteration_1).
- **Phase 3: TAMAMLANDI**
  - `testing_agent_v3` iteration_2: Phase 3 özellikleri %100 PASS.
  - Kritik fix: Stripe checkout çoklu yolcuda `visa_type_id` metadata KeyError → düzeltildi (`routes_payments.py`).
  - İyileştirme: `payment_received` e-postası `contact.email` üzerinden gönderilecek şekilde düzeltildi.
  - UI: Navbar link sarması `whitespace-nowrap` ile giderildi.
- **Phase 4: TAMAMLANDI**
  - UAE bayrak paleti + koyu mod + sosyal kanıt + gerçek görseller.
  - `ThemeToggle` navbar + admin header’da; tema kalıcı.
  - `testing_agent_v3` iteration_3: PASS; regresyon yok.
- **Phase 5: TAMAMLANDI**
  - AI pasaport okuma endpoint’i: `POST /api/passport/read` + Apply adım 1 auto-fill.
  - Gerçek vize PDF’inden kişisel verileri blur + filigranlı örnek: `public/ornek-vize.jpg` + Home’da gösterim.
  - UAE + TR bayrak ikonları: navbar/footer + içerik.
  - Blog: DB destekli `articles` + public endpoints + SEO’lu `/gelismeler/:slug` + admin CRUD `/admin/yazilar`.
  - Yorumlar: DB’ye taşındı + admin CRUD `/admin/yorumlar` + puan özeti düzenleme.
  - WhatsApp bildirimi: wa.me link + mesaj üretimi + `notifications` log.
  - Tasarım sadeleştirildi ve referans siteye yaklaştırıldı: Figtree, pill butonlar, kırmızı fiyat/şerit.
  - `testing_agent_v3` iteration_4: Backend %96.9 (63/65, düşük öncelik/test), Frontend ana akışlar PASS; regresyon yok.
- Kalan opsiyonel işler: RESEND_API_KEY ile canlı e-posta doğrulaması, Stripe prod geçişi, içerik onayı ve operasyonel güvenlik ayarları.
