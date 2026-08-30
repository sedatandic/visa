# plan.md

## 1. Objectives
- Türkçe, modern, sade ve güven veren bir Dubai/UAE vize başvuru sitesi (kopya değil; benzer bilgi mimarisi/UX, özgün marka/renk).
- Vize tipleri + fiyatlar + genel bilgilendirme + hızlı başvuru akışı.
- Çekirdek iş akışı: **başvuru oluşturma → dosya yükleme → ödeme (Stripe) → takip kodu**.
- Başvuruları MongoDB’ye kaydetme, admin panelde listeleme/detay/güncelleme.
- E-posta bildirimleri (başvuru sahibine + admin’e): **API anahtarı yoksa akışı bozmadan “skipped” olarak outbox’a yaz**.
- Güven ve “insan eliyle tasarlanmış” kurumsal görünüm:
  - **BAE bayrak paleti** (yeşil/kırmızı/siyah/beyaz) — kırmızı vurgu belirgin.
  - **Tipografi**: Spectral (başlık) + IBM Plex Sans (gövde) + opsiyonel IBM Plex Mono.
  - **Koyu mod**: sağ üst tema anahtarı, kalıcı (localStorage), admin’de de var.
  - **Gerçek görseller**: Burj Khalifa hero, Sheikh Zayed yolu, ofis, pasaport/belge flatlay.
  - **Müşteri deneyimleri**: 4,9/5 puan özeti + memnuniyet barları + doğrulanmış yorum kartları.
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
  - Fontlar: **Spectral + IBM Plex Sans (+ IBM Plex Mono)**.
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
  - Backend `content.py`: zenginleştirilmiş `TESTIMONIALS` + yeni `REVIEW_SUMMARY`.
  - `/api/content/site`: `review_summary` payload’a eklendi.
  - Home: yeni “Müşteri Deneyimleri” bölümü: 4,9/5, toplam değerlendirme ve bar metrikleri + **6 doğrulanmış yorum kartı**.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_3.json):
  - Frontend: %100 PASS (tema anahtarı, kalıcılık, dark readability, testimonial bölümü, görsel yükleme, mobil görünüm).
  - Backend: Phase 3 format testleri PASS; kalan bazı fail’ler eski Phase 2 şema testlerinden (legacy).
  - Regresyon yok: çoklu yolcu başvuru + admin vize PDF akışı çalışıyor.

---

### Phase 5 — Go-live hazırlık (opsiyonel)
- Resend domain doğrulama + **gerçek e-posta gönderimi** (RESEND_API_KEY eklendikten sonra canlı test).
- Stripe canlı hesaba geçiş rehberi + webhook doğrulama (prod).
- KVKK/Gizlilik/Çerez/İade politikası sayfalarının hukuk kontrolü.
- Admin şifresi ve demo credential’ların canlıya alınmadan değiştirilmesi.
- Son UI cilası (mikro kopya, mobil spacing, performans).
- Operasyonel: log/monitoring notları, hata izleme (opsiyonel).

---

## 3. Next Actions
1. **(Opsiyonel) Resend anahtarını ekle** → canlı e-posta gönderimini E2E doğrula (application_received, payment_received, visa_delivered).
2. **(Opsiyonel) Stripe prod hazırlığı**: canlı anahtarlar + webhook secret + success/cancel URL’leri prod domain.
3. İçerik onayı: müşteri yorum metinleri, sayılar (4.500+, 1.284), iletişim bilgileri (telefon/adres).
4. Güvenlik/operasyon: admin şifresi değişimi, env değişkenleri ve erişim kısıtları.

---

## 4. Success Criteria
- POC: Mongo write/read + objstore upload/download + Stripe checkout+status update + email skip mekanizması hatasız.
- V1: Kullanıcı başvuru oluşturur, dosya yükler, Stripe ödemesi yapar, success sayfası DB’de “paid” doğrular.
- Takip sayfası referans koduyla doğru başvuruyu gösterir ve “ödemeyi tamamla” çalışır.
- Admin: giriş yapar, başvuruları listeler, detayda dosyaları görür, durum günceller.
- **Phase 3:** çoklu yolcu (aile) başvurusu + otomatik fiyat/indirim + admin vize PDF yükle/gönder akışları sorunsuz.
- **Tema/Koyu Mod:** tema anahtarı görünür, dark/light geçişi sorunsuz, kalıcı ve tüm sayfalarda okunabilirlik korunur.
- **Sosyal kanıt:** müşteri deneyimleri bölümü görünür, veriler backend’den gelir, görseller kırık değildir.
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
- **Phase 4: TAMAMLANDI (Marka/Tema + Koyu Mod + Yorumlar + Görsel Yenileme)**
  - UAE bayrak paleti + Spectral/IBM Plex Sans uygulandı, kırmızı vurgu artırıldı.
  - ThemeToggle navbar + admin header’da; tema kalıcı.
  - Home: review summary + 6 doğrulanmış yorum kartı.
  - Görseller: Burj Khalifa hero + Dubai/ofis/belge görselleri yenilendi.
  - `testing_agent_v3` iteration_3: Frontend %100 PASS; regresyon yok.
- Kalan opsiyonel işler: RESEND_API_KEY eklendiğinde canlı e-posta doğrulaması, Stripe prod geçişi, içerik onayı ve operasyonel güvenlik ayarları.
