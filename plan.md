# plan.md

## 1. Objectives
- Türkçe, modern ve sade bir Dubai/UAE vize başvuru sitesi (kopya değil; benzer yapı/UX, farklı marka/renk).
- Vize tipleri + fiyatlar + genel bilgilendirme + kolay başvuru akışı.
- Çekirdek iş akışı: **başvuru oluşturma → dosya yükleme → ödeme (Stripe) → takip kodu**.
- Başvuruları MongoDB’ye kaydetme, admin panelde listeleme/detay/güncelleme.
- E-posta bildirimleri (başvuru sahibine + admin’e) **anahtar yoksa akışı bozmadan “skip”**.

## 2. Implementation Steps

### Phase 1 — Core POC (izole test; ilerlemeden önce çalışır hale getir)
**Amaç:** En riskli entegrasyonları tek dosyada uçtan uca doğrulamak.

**POC User Stories (min 5)**
1. Bir geliştirici olarak, MongoDB’ye örnek başvuru kaydedip geri okuyabilmek istiyorum.
2. Bir geliştirici olarak, pasaport/foto yükleyip objstore’a yazıp geri indirerek bayt bazında doğrulamak istiyorum.
3. Bir geliştirici olarak, Stripe sandbox oluşturup ürün/fiyat kataloğunu idempotent kurmak istiyorum.
4. Bir geliştirici olarak, checkout session oluşturup geçerli bir Stripe Checkout URL’i almak istiyorum.
5. Bir geliştirici olarak, webhook veya polling ile ödeme durumunu “paid” olarak DB’ye işleyebilmek istiyorum.
6. Bir geliştirici olarak, RESEND_API_KEY yoksa e-posta gönderiminin kırmadan “skipped” kaydedilmesini istiyorum.

**Adımlar**
- `backend/scripts/test_core.py` oluştur:
  - Mongo: `visa_applications` insert/find + datetime serialize helper.
  - Object Storage: init → put_object (dummy jpg/png) → get_object → content-type/size check.
  - Stripe Flow A: sandbox provision (job_id/key ile) → `setup_stripe.py` katalog (lookup_key).
  - Stripe: `/api/payments/checkout` benzeri fonksiyon çağrısı ile session create (origin_url dummy) + Mongo `payment_transactions` kaydı.
  - Status: Stripe session retrieve (poll) + DB update idempotent.
  - Email: Resend gönder (varsa), yoksa `email_outbox` koleksiyonuna `status=skipped`.
- Websearch: “Stripe Checkout best practices success/cancel, webhook idempotency, polling fallback” kısa kontrol.
- Çıkış kriteri: Script tek komutla çalışır, tüm adımlar PASS/log üretir.

### Phase 2 — V1 App Development (POC kanıtlı çekirdek üzerine)
**Frontend:** React + router + Tailwind + shadcn/ui. **Backend:** FastAPI `/api` + Motor + entegre servisler.

**V1 User Stories (min 5)**
1. Ziyaretçi olarak ana sayfada fiyatları ve “Başvuru Yap” CTA’yı net görmek istiyorum.
2. Ziyaretçi olarak vize tiplerini karşılaştırıp birini seçerek başvuruya başlayabilmek istiyorum.
3. Başvuru sahibi olarak çok adımlı formu mobilde rahat doldurup pasaport + vesikalık yüklemek istiyorum.
4. Başvuru sahibi olarak Stripe ile ödemeyi tamamlayıp “ödeme onaylandı” sayfasında doğrulanmış sonucu görmek istiyorum.
5. Başvuru sahibi olarak takip kodumla başvurumu görüntüleyip gerekirse ödemeyi sonradan tamamlamak istiyorum.
6. Admin olarak giriş yapıp başvuruları listeleyip detayda dosyaları görüntülemek ve durum güncellemek istiyorum.

**Backend (FastAPI)**
- Modeller/koleksiyonlar:
  - `visa_types` (seed), `visa_applications`, `uploads`, `payment_transactions`, `contact_messages`, `email_outbox`, `admin_users`.
- API:
  - Public: `GET /api/visa-types`, `GET /api/content/*` (info/faq).
  - Application: `POST /api/applications` (draft create), `POST /api/uploads` (passport/photo), `POST /api/applications/{id}/submit` (ref code), `GET /api/track?code=&surname_or_email=`.
  - Payments: `POST /api/payments/checkout`, `GET /api/payments/status/{session_id}`, `POST /api/stripe/webhook`.
  - Files: `GET /api/files/{file_id}` (blob fetch) ve/veya query-param auth.
  - Admin auth: `POST /api/admin/login` (demo JWT), `GET /api/admin/applications`, `GET /api/admin/applications/{id}`, `PATCH /api/admin/applications/{id}`.
  - Contact: `POST /api/contact`.
- Email servisi:
  - Başvuru submit + ödeme “paid” eventinde tetik; `RESEND_API_KEY` yoksa `email_outbox.status=skipped`.
- Güvenlik:
  - Input validation, dosya tip/limit (örn. jpg/png/pdf; max 10MB).
  - Admin endpoint’ler JWT guard.
- Ödeme/vergiler:
  - Stripe Flow A claimable sandbox.
  - Varsayılan vergi modu: **Stripe sadece vergi hesaplar (siz beyan edersiniz)** yaklaşımı (uygun değilse sandbox ülkesine göre otomatik uyarlanır).

**Frontend (React)**
- Sayfalar:
  - `/` Landing (hero, süreç adımları, güven alanı, WhatsApp buton).
  - `/fiyatlar` (kartlı pricing tablosu: 14 gün tek giriş, 30 gün tek giriş, 30 gün çok giriş, 60 gün tek giriş/çok giriş örnekleri).
  - `/bilgi` `/evraklar` `/sss`.
  - `/basvuru` (multi-step: kişisel bilgiler → seyahat → dosya yükleme → özet → ödeme).
  - `/payment/success` (poll status), `/payment/cancel`.
  - `/takip` (kod + soyad/e-posta ile sorgu, ödeme tamamla butonu).
  - `/admin/login`, `/admin` (liste/filtre), `/admin/applications/:id` (detay+dosyalar).
- Tasarım:
  - Güven veren palet (lacivert + altın vurgu veya turkuaz + koyu gri), bol boşluk, büyük CTA.
  - dubaivizeal.com benzeri bilgi mimarisi; özgün komponent/ikonografi.
- Admin demo şifreleri: `/app/memory/test_credentials.md`.

**Phase 2 sonu**
- Seed data: visa tipleri ve örnek fiyatlar.
- 1 tur E2E test (manuel + test agent): başvuru→upload→checkout→success poll→admin görüntü.

### Phase 3 — Stabilizasyon + UX/SEO + Operasyonel iyileştirmeler
**User Stories (min 5)**
1. Kullanıcı olarak form hatalarında net Türkçe uyarılar görmek istiyorum.
2. Kullanıcı olarak dosya yükleme ilerlemesini ve önizlemeyi görmek istiyorum.
3. Admin olarak arama/filtre (durum, ödeme, tarih) yapmak istiyorum.
4. Admin olarak başvuru durumunu güncellediğimde başvuru sahibine e-posta gitmesini istiyorum (anahtar varsa).
5. Kullanıcı olarak sayfaların hızlı açılmasını ve mobilde sorunsuz kullanılmasını istiyorum.

**Adımlar**
- Admin tablo: pagination, search, status/payment filter.
- Upload görüntüleme: güvenli blob fetch + cache busting.
- E-posta şablonlarını (TR) iyileştir, `email_outbox` retry (opsiyonel).
- SEO-lite: meta title/description, sitemap/robots (MVP), yapılandırılmış FAQ.
- Hata gözlemi: backend log’ları, edge-case mesajları.
- 1 tur E2E test ve bugfix.

### Phase 4 — Go-live hazırlık (opsiyonel)
- Resend domain doğrulama + gerçek gönderimler.
- Stripe sandbox “claim” link ile canlıya geçiş rehberi.
- Basit KVKK/Gizlilik, Çerez, İade politikası sayfaları.

## 3. Next Actions
1. Phase 1 için `test_core.py` ve `setup_stripe.py` hazırlanıp çalıştırılacak.
2. Stripe sandbox provision edilip katalog kurulacak; checkout URL üretimi doğrulanacak.
3. Object storage upload/download doğrulanacak.
4. Email entegrasyonu anahtarsız “skip” modunda devreye alınacak.
5. POC PASS olduktan sonra Phase 2 V1 uygulama tek seferde inşa edilip E2E test edilecek.

## 4. Success Criteria
- POC: Mongo write/read + objstore upload/download + Stripe sandbox+catalog+checkout+status update + email skip mekanizması hatasız çalışır.
- V1: Kullanıcı başvuru oluşturur, dosya yükler, Stripe ödemesi yapar, success sayfası DB’de “paid” doğrular.
- Takip sayfası referans koduyla doğru başvuruyu gösterir ve “ödemeyi tamamla” akışı çalışır.
- Admin: giriş yapar, başvuru listeler, detayda dosyaları görür, durum günceller.
- `RESEND_API_KEY` yokken hiçbir kritik akış kırılmaz; tüm “atlanan” mailler outbox’a kaydolur.


---
## DURUM (Phase 2 tamamlandi - 2026-08-30)
- Phase 1 POC: 7/7 PASS (Mongo, objstore upload/download, Stripe Flow B checkout+status, Resend graceful skip). Not: Stripe claimable sandbox (Flow A) TR ulkesi desteklenmedigi icin kullanilamadi; Flow B (STRIPE_API_KEY=sk_test_emergent, webhook /api/webhook/stripe) kullanildi.
- Phase 2: Backend (server.py + routes_public/payments/admin, content.py, storage.py, emailer.py) ve Frontend (16 sayfa/komponent) tamamlandi.
- E2E test (iteration_1): backend 30/30, frontend 14/14 user story PASS.
- RESEND_API_KEY bos: e-postalar email_outbox koleksiyonuna status="skipped" olarak kaydediliyor, hicbir akis kirilmiyor. Admin > E-postalar sekmesinde gorulebilir.
- Sonraki adimlar: Resend anahtari eklenmesi, gercek Stripe hesabi, KVKK metinlerinin hukukcu kontrolu, admin sifresinin degistirilmesi.
