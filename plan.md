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
3. Çok adımlı formu mobilde rahat doldurup evrakları yüklemek.
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

---

### Phase 3 — Aile Başvurusu + Admin Vize PDF (Tamamlandı)
**Amaç:** Çoklu yolcu başvurusu + otomatik fiyatlandırma ve admin’in vize PDF gönderim operasyonunu tamamlamak.

**Çıktılar**
- `compute_pricing` + `POST /api/pricing/quote`.
- Başvuru şeması `travelers[]`.
- Admin vize akışı: PDF upload + müşteriye gönderim.

**Test**
- `testing_agent_v3` (iteration_2.json): %100 PASS.

---

### Phase 4 — Marka/Tema Yenileme + Sosyal Kanıt (Tamamlandı; koyu mod kaldırıldı)
**Amaç:** Görsel dili güçlendirmek, “AI şablonu” hissini kırmak, BAE bayrak renkleriyle özgün kurumsal kimlik + sosyal kanıt.

---

### Phase 5 — Operasyonel içerik yönetimi + SEO Blog + WhatsApp + AI Pasaport Okuma (Tamamlandı)
**Amaç:** Operasyonu hızlandırmak (admin araçları), arama motoru görünürlüğü (SEO blog), müşteri iletişimi (WhatsApp), form doldurmayı hızlandırmak (AI pasaport okuma).

---

### Phase 6 — Rakip boşluk kapatma + Havale/EFT + Yasal sayfalar + Dribbble Hero (Tamamlandı)
**Amaç:** Ödeme yöntemini genişletmek, yasal şeffaflık eklemek, özel vize tiplerini tamamlamak ve hero’yu modernleştirmek.

---

### Phase 7 — Ürün sadeleştirme + Admin banka/acente yönetimi + UX düzeltmeleri (Tamamlandı)
**Amaç:** Sadece vize hizmetine odaklanmak, kritik UI/validasyon sorunlarını gidermek, banka ve acente bilgilerini yönetilebilir yapmak.

---

### Phase 8 — Kod Kalitesi + Güvenlik Sertleştirme (Tamamlandı)
**Amaç:** Code review bulgularını uygulamak; runtime crash riskini azaltmak, güvenli token üretimi sağlamak ve refactor sonrası regresyon olmadığını kanıtlamak.

---

### Phase 9 — Güven Şeridi + GDRFA Referansı (Tamamlandı)
**Amaç:** Otorite/güven algısını artırmak.

**Adımlar / Çıktılar**
- Frontend:
  - `GdrfaBadge.jsx`: GDRFA Dubai temsili rozet.
  - `AuthorityStrip.jsx`: Ana sayfada “Yetkili Merciler” şeridi (GDRFA + ICP + TÜRSAB).
  - Footer: TÜRSAB rozetinin yanına GDRFA rozeti eklendi.
- Not: Telif riski nedeniyle **resmî logo yerine temsili SVG** kullanıldı; resmî dosya sağlanırsa değiştirilebilir.

**Test / Doğrulama**
- Screenshot tool: şerit ve footer rozeti görsel olarak doğrulandı.

---

### Phase 10 — Vize Rehberi SEO Sayfaları (Tamamlandı)
**Amaç:** Her vize tipi için arama motorlarında sıralanacak, dönüşüm odaklı rehber sayfaları üretmek.

**Kapsam (Hedef URL’ler)**
- `/dubai-vizesi/:slug` (örn. `/dubai-vizesi/30-gun-tek-giris`) — toplam 9 vize tipi.

**Çıktılar**
- Backend:
  - `GET /api/visa-guides` (liste)
  - `GET /api/visa-guides/{slug}` (detay)
  - Admin override: `PATCH /api/admin/visa-types/{id}` içinde `guide` alanı desteklenir.
- Frontend:
  - `VisaGuide.jsx` rehber sayfası
  - Route: `/dubai-vizesi/:slug`
  - İç linkler: Home + /vize-tipleri + Footer + vize kartlarından “Detaylı rehberi oku”
- SEO:
  - `setMeta` + `setJsonLd` ile JSON-LD: `Service`, `FAQPage`, `BreadcrumbList`
  - `public/sitemap.xml` + `public/robots.txt`

**Test / Doğrulama**
- `testing_agent_v3` (iteration_10.json): Rehber sayfaları + endpointler + SEO + linkleme %100 PASS.

---

### Phase 11 — Zorunlu Seyahat Belgeleri + Kart Tıklama Davranışı (Tamamlandı)
**Amaç:** Evrak standardını netleştirmek ve kullanıcı deneyiminde yanlış yönlendirmeyi önlemek.

**Kapsam / Değişiklikler**
1) **Uçak bileti + otel rezervasyonu artık zorunlu**
- Backend:
  - `content.py` içinde `REQUIRED_DOCUMENTS`: `ticket` ve `hotel` `required=True`.
  - `POST /api/applications`: `extra_documents.ticket_file_id` ve `extra_documents.hotel_file_id` yoksa **400**.
  - Dosya ID doğrulaması: ticket/hotel file_id DB’de yoksa **400**.
- Frontend:
  - `Apply.jsx` (Evraklar adımı) validasyon: ticket/hotel yoksa hata gösterir ve adım ilerlemez.
  - UI metinleri “zorunlu” olarak güncellendi.

2) **Vize kartları: gövde tıklaması başvuruya götürmez**
- `VisaTypeCard`:
  - Bilgilendirme sayfalarında (Home, /vize-tipleri) kart gövdesi tıklanınca yönlendirme yok.
  - Sadece **“Başvuruya başla”** butonu ve **“Detaylı rehberi oku”** linki yönlendirir.
  - Başvuru formundaki seçim modunda (`onSelect` varken) kart tıklaması vize seçmeye devam eder.

**Test / Doğrulama**
- `testing_agent_v3` (iteration_11.json): backend 6/6 + frontend 8/8 PASS.

---

## 3. Next Actions
1. **Canlı E-posta Testi (Resend) — BEKLEMEDE**
   - Gerekli env:
     - `RESEND_API_KEY` (kullanıcı sağlayacak)
     - `SENDER_EMAIL` (domain doğrulanmış adres önerilir)
   - E2E doğrulanacak mailler:
     - `application_received`
     - `bank_transfer_instructions`
     - `payment_received`
     - `visa_delivered`
   - Anahtar gelene kadar sistem “skipped” outbox davranışını sürdürür.
2. **(Opsiyonel) Stripe prod geçişi**
   - Canlı anahtarlar + webhook secret + success/cancel URL’leri.
3. **İçerik onayı ve gerçek veriler**
   - Banka bilgileri (`/admin/banka`) gerçek değerlerle.
   - TÜRSAB/acente ticari bilgiler (`/admin/acente`) gerçek değerlerle.
4. **Operasyonel güvenlik (opsiyonel)**
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
- `RESEND_API_KEY` yokken hiçbir kritik akış kırılmaz; tüm “atlanan” mailler `email_outbox`’a kaydolur.
- Canlı Resend anahtarı verildiğinde e-postalar gerçek adrese gider ve outbox “sent” olarak kaydolur.

---

## DURUM (2026-08-31)
- Phase 1 POC: PASS.
- Phase 2: Backend + Frontend tamamlandı; E2E test PASS.
- Phase 3: TAMAMLANDI.
- Phase 4: TAMAMLANDI.
- Phase 5: TAMAMLANDI.
- Phase 6: TAMAMLANDI.
- Phase 7: TAMAMLANDI.
- Phase 8: TAMAMLANDI.
- Phase 9: TAMAMLANDI (GDRFA/Yetkili Merciler şeridi + footer rozeti).
- Phase 10: **TAMAMLANDI** (Vize Rehberi SEO Sayfaları) — iteration_10.json PASS.
- Phase 11: **TAMAMLANDI** (Zorunlu Seyahat Belgeleri + Kart Tıklama Davranışı) — iteration_11.json PASS.

Kalan opsiyonel işler: **RESEND_API_KEY ile canlı e-posta doğrulaması**, Stripe prod geçişi, içerik/hukuk onayı, gerçek banka/acente bilgileri, operasyonel güvenlik ayarları.
