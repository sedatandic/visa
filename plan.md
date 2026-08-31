# plan.md

## 1. Objectives
- Türkçe, modern, **sade** ve güven veren bir Dubai/UAE vize başvuru sitesi (kopya değil; benzer bilgi mimarisi/UX, özgün marka/renk).
- Vize tipleri + fiyatlar + genel bilgilendirme + hızlı başvuru akışı.
- Çekirdek iş akışı: **başvuru oluşturma → dosya yükleme → ödeme (kart / havale) → takip kodu**.
- Başvuruları MongoDB’ye kaydetme, admin panelde listeleme/detay/güncelleme.
- E-posta bildirimleri (başvuru sahibine + admin’e): **API anahtarı yoksa akışı bozmadan “skipped” olarak outbox’a yaz**.
- Güven ve “insan eliyle tasarlanmış” kurumsal görünüm:
  - **BAE bayrak paleti** (yeşil/kırmızı/siyah/beyaz) — kırmızı vurgu belirgin.
  - **Tipografi**: **Montserrat (başlık)** + **Figtree (gövde)** + opsiyonel IBM Plex Mono.
  - **Koyu mod yok** (tamamen kaldırıldı).
  - **Gerçek görseller**: Burj Khalifa hero, Sheikh Zayed yolu, ofis, pasaport/belge flatlay.
  - **Müşteri deneyimleri**: 4,9/5 puan özeti + memnuniyet barları + doğrulanmış yorum kartları (DB tabanlı).
  - **Örnek vize**: Kişisel verileri gizlenmiş (blur) + “ÖRNEKTİR/SPECIMEN” filigranlı **BAE e-vize örneği**.
  - **UAE + TR bayrak ikonları**: navbar/footer ve içerik içinde (Türkiye → BAE vurgusu).
  - **TÜRSAB + acente şeffaflığı**: footer + hakkımızda’da TÜRSAB rozeti ve acente detayları (admin’den yönetilebilir).
- **Sadece vize hizmeti**: otel/tur/transfer içerikleri kaldırıldı (6 vize hizmeti kaldı).
- **Phase 3 (tamamlandı):**
  - **Aile Başvurusu:** Tek formda çoklu yolcu ekleme/çıkarma, kişi sayısına göre otomatik fiyat + aile indirimi.
  - **Admin Vize PDF:** Admin panelden onaylı vize PDF yükleme ve tek tıkla müşteriye e-posta ile gönderme.

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

**Test / Doğrulama**
- `testing_agent_v3` (iteration_2.json): Phase 3 spesifik akışlar %100 PASS.

---

### Phase 4 — Marka/Tema Yenileme + Sosyal Kanıt (Tamamlandı; koyu mod kaldırıldı)
**Amaç:** Görsel dili güçlendirmek, “AI şablonu” hissini kırmak, BAE bayrak renkleriyle özgün kurumsal kimlik + sosyal kanıt.

**Adımlar / Çıktılar**
- Tema / Tipografi:
  - UAE bayrak paleti (yeşil primary, kırmızı accent/destructive, siyah/beyaz temeller).
  - Token tabanlı renkler: hard-coded renkler temizlendi, CSS var’lara taşındı.
- Görseller:
  - Hero: Burj Khalifa (gündüz) + ikincil görseller.
  - Güven/kurumsal: ofis fotoğrafı.
  - Belgeler: pasaport/belge flatlay.
- Müşteri Deneyimleri:
  - Home: “Müşteri Deneyimleri” bölümü: 4,9/5, toplam değerlendirme ve bar metrikleri + doğrulanmış yorum kartları.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_3.json): okunabilirlik, testimonial bölümü, görsel yükleme, mobil görünüm PASS.

---

### Phase 5 — Operasyonel içerik yönetimi + SEO Blog + WhatsApp + AI Pasaport Okuma (Tamamlandı)
**Amaç:** Operasyonu hızlandırmak (admin araçları), arama motoru görünürlüğü (SEO blog), müşteri iletişimi (WhatsApp), form doldurmayı hızlandırmak (AI pasaport okuma), güven artırmak (gerçek vize örneği).

**Adımlar / Çıktılar**
- AI Pasaport Okuma:
  - Backend: `backend/passport_ai.py` + `POST /api/passport/read`.
  - Frontend: `/basvuru` 1. adımda “Pasaportu yükleyin, bilgiler otomatik dolsun”.
- Örnek BAE Vizesi:
  - Kullanıcı PDF’inden kişisel detayları blur + filigran.
  - Çıktı: `frontend/public/ornek-vize.jpg` + Home’da gösterim.
- UAE + TR bayrak ikonları:
  - `FlagIcons.jsx` (SVG) — navbar ve footer’da.
- Blog (SEO):
  - DB: `articles` koleksiyonu (seed + admin CRUD).
  - Public API: `GET /api/articles`, `GET /api/articles/{slug}`.
  - Frontend: `/gelismeler` liste, `/gelismeler/:slug` detay (canonical, OG, Article JSON-LD).
- Yorumlar (DB + Admin):
  - DB: `testimonials` + `site_settings.review_summary`.
  - Admin UI: `/admin/yorumlar`.
- WhatsApp Bildirimi (Link tabanlı):
  - Backend: `POST /api/admin/applications/{id}/whatsapp`.
  - Frontend: Admin detay “WhatsApp ile bildir”.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_4.json): Backend %96.9, Frontend ana akışlar PASS.

---

### Phase 6 — Rakip boşluk kapatma + Havale/EFT + Yasal sayfalar + Dribbble Hero (Tamamlandı)
**Amaç:** Rakip sitedeki eksik operasyonel parçaları tamamlamak, ödeme yöntemini genişletmek, yasal şeffaflık eklemek ve hero’yu modern danışmanlık tasarımına yaklaştırmak.

**User Stories (min 5)**
1. Kullanıcı olarak kredi kartı dışında **Havale/EFT** ile de ödeme yapabilmek istiyorum.
2. Kullanıcı olarak iade/iptal koşullarını ve hizmet sözleşmesini net görmek istiyorum.
3. Kullanıcı olarak transit vize / freelancer vizesi gibi özel paketleri de görebilmek istiyorum.
4. Kullanıcı olarak form doldurmak istemezsem WhatsApp/E-posta ile başvuru alternatifini görmek istiyorum.
5. Admin olarak havale ödemesini panelden onaylayıp başvuruyu incelemeye alabilmek istiyorum.

**Adımlar / Çıktılar**
- Yeni vize tipleri:
  - `visa_transit_48` (48 Saat Transit) ve `visa_freelancer_2y` (2 Yıl Freelancer).
- SSS genişletme:
  - 18 yaş kuralı, Formül A, havale, süre aşımı/Escape Report, RED/iade, WhatsApp ile başvuru vb. (toplam 17 SSS).
- Yasal sayfalar:
  - Backend: `GET /api/content/legal` → `refund_terms`, `service_terms`.
  - Frontend: `/iade-kosullari`, `/hizmet-sozlesmesi` + footer linkleri.
- Havale/EFT ödeme akışı:
  - Backend:
    - `POST /api/payments/bank-transfer` → `payment.method=bank_transfer`, `payment.status=awaiting_transfer`, bank bilgileri + `bank_transfer_instructions` e-postası.
    - Admin: `POST /api/admin/applications/{id}/mark-paid` → `payment.status=paid`, `status=reviewing`, `payment_received` e-postası.
  - Frontend:
    - `/basvuru` ödeme adımında “Havale/EFT” seçimi + banka bilgileri blok gösterimi.
    - Admin başvuru detayında “Havale ödemesini onayla” butonu.
- Dribbble referans hero:
  - Üst üste binen görsel kolajı, 7+ yıl deneyim rozeti, puan rozet kartı.
  - Yumuşak degrade zemin.
  - Kayan hizmet şeridi (marquee).

**Test / Doğrulama**
- `testing_agent_v3` (iteration_5.json): Backend %91.8 (zaman aşımı/kurulum kaynaklı), Frontend %100 PASS.

---

### Phase 7 — Ürün sadeleştirme + Tıklanabilir kart fixleri + Admin banka/acente yönetimi + UX düzeltmeleri (Tamamlandı)
**Amaç:** Sadece vize hizmetine odaklanmak, kritik tıklanabilirlik/validasyon sorunlarını gidermek, gerçek banka ve acente bilgilerini yönetilebilir yapmak.

**Adımlar / Çıktılar**
- **60 günlük kart tıklanmıyor** bug fix:
  - `VisaTypeCard` kartlarının tamamı tıklanabilir hale getirildi (mobil dahil).
  - Mobilde “tap” sorununu gidermek için kart üstüne **stretched Link overlay** eklendi.
  - Klavye erişimi (Enter/Space) korundu.
- **Sadece vize hizmeti**:
  - Otel/tur/transfer içerikleri kaldırıldı.
  - `SERVICES` vize odaklı 6 maddeye indirildi; `TOURS = []`.
  - Ana sayfa tours bölümü kaldırıldı; Hizmetler sayfası sadeleştirildi.
  - Promosyon bandı “aile indirimi” olarak güncellendi.
- **Banka bilgileri admin’den yönetilebilir**:
  - Admin UI: `/admin/banka`.
  - Backend: `site_settings.bank_transfer` ile override; public içerik ve havale e-postası/ekranı bu değeri kullanır.
- **Başvuru adım-1 validasyon iyileştirmesi**:
  - Eksik alanlar artık isimleriyle toast’ta listelenir.
  - İlk hatalı alana otomatik kaydırma + odak.
- **Küçük UI istekleri**:
  - “+ Yetişkin ekle” ve “+ Çocuk ekle” butonlarına plus + kullanıcı/bebek ikonları.
  - “Pasaport kimlik sayfası” yanındaki “JPG veya PNG” metni kaldırıldı.
- **Koyu mod tamamen kaldırıldı**:
  - ThemeToggle ve theme altyapısı kaldırıldı; `.dark` token blokları silindi.
- **TÜRSAB + acente detayları**:
  - Footer + Hakkımızda’da TÜRSAB rozeti (temsili SVG) ve acente bilgileri gösterimi.
  - Admin UI: `/admin/acente` ile düzenlenebilir.
- **Font güncellemesi**:
  - Başlık fontu: **Montserrat**, gövde: **Figtree**.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_7.json): 4 kullanıcı hatası düzeltmesi %100 PASS.
- `testing_agent_v3` (iteration_8.json): Koyu mod kaldırma + TÜRSAB/acente + regresyonlar overall %98 PASS.

---

### Phase 8 — Kod Kalitesi + Güvenlik Sertleştirme (Tamamlandı)
**Amaç:** Code review bulgularını uygulamak; runtime crash riskini azaltmak, güvenli token üretimi sağlamak ve refactor sonrası regresyon olmadığını kanıtlamak.

**Adımlar / Çıktılar**
- Tanımsız kalabilen değişkenler:
  - `routes_public.upload_document()` ve dosya okuma akışlarında `result/data/content_type` ön-ilklendirildi.
  - `routes_payments` checkout akışında `session` ön-ilklendirildi ve doğrulama eklendi.
  - `routes_admin` JWT decode akışında `data` ön-ilklendirildi.
  - WhatsApp akışında `message` üretimi helper ile garanti altına alındı.
- Güvenli rastgele üretim:
  - Referans kod üretimi `random` → `secrets` (kriptografik güvenli).
- Daha iyi hata zinciri:
  - Kritik dış servis hatalarında `raise ... from exc` ile kök hata korundu.
- Karmaşıklık azaltma:
  - `admin_whatsapp_link`, `admin_send_visa`, `admin_update_application` fonksiyonlarında helper’lar eklendi:
    - `_build_whatsapp_message`, `_notify_status_change`, `_resolve_origin`, `_visa_send_update`.
- Yanlış karşılaştırma düzeltmeleri:
  - `is` kullanımı: None kontrolleri için doğru olduğu doğrulandı; literal karşılaştırmaları bulunmadı (değişiklik gerekmedi).

**Test / Doğrulama**
- `testing_agent_v3` (iteration_9.json):
  - Refactor doğrulama: 11/11 (%100)
  - Backend: %96.2
  - Frontend smoke: %100
  - Regresyon yok.

---

## 3. Next Actions
1. **İçerik onayı ve gerçek veriler**:
   - Banka bilgileri (IBAN/ünvan/banka adı) gerçek bilgilerle girilsin (`/admin/banka`).
   - TÜRSAB belge numarası ve ticari bilgiler gerçek değerlerle girilsin (`/admin/acente`).
2. **(Opsiyonel) Resend anahtarını ekle** → canlı e-posta gönderimini E2E doğrula (application_received, bank_transfer_instructions, payment_received, visa_delivered).
3. **(Opsiyonel) Stripe prod hazırlığı**: canlı anahtarlar + webhook secret + success/cancel URL’leri prod domain.
4. Operasyonel güvenlik:
   - Admin şifresi değişimi, env değişkenleri ve erişim kısıtları.
   - Rate limit / basic bot koruması (opsiyonel).
5. (Opsiyonel) WhatsApp’ı otomatik gönderime taşımak istenirse: Twilio/Meta entegrasyonu.

---

## 4. Success Criteria
- POC: Mongo write/read + objstore upload/download + Stripe checkout+status update + email skip mekanizması hatasız.
- V1: Kullanıcı başvuru oluşturur, dosya yükler, Stripe ödemesi yapar, success sayfası DB’de “paid” doğrular.
- Takip sayfası referans koduyla doğru başvuruyu gösterir ve “ödemeyi tamamla” çalışır.
- Admin: giriş yapar, başvuruları listeler, detayda dosyaları görür, durum günceller.
- **Phase 3:** çoklu yolcu (aile) başvurusu + otomatik fiyat/indirim + admin vize PDF yükle/gönder akışları sorunsuz.
- **Sosyal kanıt:** müşteri deneyimleri bölümü görünür, veriler backend’den gelir.
- **Örnek vize:** kişisel verileri gizlenmiş vize örneği görüntülenir.
- **AI pasaport okuma:** pasaport yüklenince form alanları otomatik dolar, kullanıcı kontrol eder; akış bozulmaz.
- **SEO blog:** /gelismeler ve /gelismeler/:slug sayfaları meta/canonical/JSON-LD ile çalışır.
- **WhatsApp bildirimi:** admin tek tıkla wa.me linki ve mesaj üretir; loglanır.
- **Havale/EFT:** kullanıcı bank transfer seçer, sistem bank bilgilerini ve referansı gösterir; admin “mark-paid” ile ödemeyi onaylar ve başvuru incelemeye geçer.
- **Banka ve acente yönetimi:** `/admin/banka` ve `/admin/acente` üzerinden girilen bilgiler sitede ve e-posta şablonlarında doğru görünür.
- `RESEND_API_KEY` yokken hiçbir kritik akış kırılmaz; tüm “atlanan” mailler `email_outbox`’a kaydolur.
- **Kod kalitesi:** referans kod üretimi güvenli (`secrets`), error-path’lerde 500 yerine doğru 4xx, refactor sonrası regresyon yok.

---

## DURUM (2026-08-31)
- Phase 1 POC: PASS (Mongo, objstore upload/download, Stripe checkout+status, Resend graceful skip).
- Phase 2: Backend + Frontend tamamlandı; E2E test PASS (iteration_1).
- **Phase 3: TAMAMLANDI**
  - `testing_agent_v3` iteration_2: Phase 3 özellikleri %100 PASS.
- **Phase 4: TAMAMLANDI**
  - UAE bayrak paleti + sosyal kanıt + gerçek görseller.
- **Phase 5: TAMAMLANDI**
  - AI pasaport okuma, örnek vize görseli, blog/yorum CMS, WhatsApp link tabanlı bildirim.
- **Phase 6: TAMAMLANDI**
  - Transit/Freelancer vize tipleri, genişletilmiş SSS, yasal sayfalar.
  - Havale/EFT ödeme akışı + admin onayı.
  - Dribbble benzeri hero (kolaj + rozet + marquee).
- **Phase 7: TAMAMLANDI**
  - 60 günlük kart tıklama bug fix (mobil dahil).
  - Otel/tur kaldırıldı; yalnızca vize hizmetleri.
  - Banka bilgileri + acente bilgileri admin’den yönetiliyor.
  - Form validasyon UX düzeltmeleri.
  - Koyu mod kaldırıldı.
  - Başlık fontu Montserrat, gövde Figtree.
- **Phase 8: TAMAMLANDI**
  - `random` → `secrets` (güvenli referans kodları).
  - Undefined variable riskleri giderildi (result/data/content_type/session/message/jwt data).
  - Admin fonksiyonları helper’lara ayrıldı; hata zinciri `raise ... from exc`.
  - `testing_agent_v3` iteration_9: refactor doğrulama %100, backend %96.2, frontend %100.

Kalan opsiyonel işler: RESEND_API_KEY ile canlı e-posta doğrulaması, Stripe prod geçişi, içerik/hukuk onayı, gerçek banka/acente bilgileri, operasyonel güvenlik ayarları.
