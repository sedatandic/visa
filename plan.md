# plan.md

## 1. Objectives
- Türkçe, modern, **sade** ve güven veren bir Dubai/UAE vize başvuru sitesi.
- Vize tipleri + fiyatlar + genel bilgilendirme + **rehber içerikler** + hızlı başvuru akışı.
- Çekirdek iş akışı: **başvuru oluşturma → dosya yükleme → ödeme (kart / havale) → takip kodu**.
- Başvuruları MongoDB’ye kaydetme, admin panelde listeleme/detay/güncelleme.

- Bildirimler:
  - **E-posta (Resend)**
    - Resend entegrasyonu canlı; outbox kayıtları admin panelde görünür.
    - Hedef: Resend’de domain doğrulaması + `SENDER_EMAIL=noreply@dubaivizeonline.com` ile üretime çıkmak.
  - **WhatsApp**
    - Manuel mod (wa.me link üretimi) tamam.
    - Admin’e operasyonel uyarılar için serbest metin WhatsApp desteği var (Twilio varsa direkt, yoksa wa.me link).
    - Otomatik sağlayıcı (Twilio/Meta) opsiyonel.

- Güven ve “insan eliyle tasarlanmış” kurumsal görünüm:
  - **Ana tema (kullanıcı referansı): “Sky Panels”**
    - Açık gökyüzü mavisi zemin + kırık beyaz “yüzen panel” katmanları
    - Antrasit “pill” butonlar + yuvarlak ikon butonlar
    - Sıcak krem vurgu (etiket/indirim/öne çıkan)
    - Tipografi: Google Sans hissine yakın geometrik sans → **Figtree** (ital axis dahil)
    - Büyük radius (20–32px) + yumuşak, difüz gölgeler
  - Kırmızı yalnızca destructive/hata semantiğinde kullanılır.
  - Not: `onyuz-rehberi.pdf` bir iş akışı/tasarım rehberi; spesifik “şunu uygula” listesi olmadan geniş değişiklik yapılmaz.

- Başvuru evrak standardı (güncel):
  - **Her yolcu:** Pasaport + vesikalık fotoğraf.
  - **Tüm başvuru:** Uçak bileti/rezervasyon + otel/konaklama rezervasyonu (opsiyonel yükleme; formda soru olarak sorulmaz).

- SEO (tamamlandı): vize rehber sayfaları + sitemap/robots + JSON-LD.
- Operasyonel verim (tamamlandı): eksik belge hatırlatma, taslak hatırlatma, hesap/draft, aile profili.
- Fiyatlandırma (tamamlandı): USD baz + canlı kurla TL tahsilat + kur şeffaflığı.

- Ek ürün satışları (tamamlandı):
  - eSIM + seyahat sigortası mağazası + vize formu içinde upsell
  - seyahat tarihine bağlı geçerlilik
  - akıllı paket önerisi + %10 bundle indirimi

- AI destekli otomasyon (tamamlandı): pasaport OCR + fotoğraf kontrol.

- **OCR Performans Ölçümü (Form Hız Testi) (tamamlandı):**
  - Her pasaport okuması **süre + alan kapsamı** ile ölçülür ve raporlanır.
  - Admin dashboard’da KPI + “en çok okunamayan alanlar” görünür.
  - Hedef: “tek pasaport fotoğrafıyla form kaç saniyede doluyor, hangi alanlar okunamıyor?” sorusuna günlük/aylık KPI.

- Zami Tours otomasyonu (üretim hazır, OTP onboarding devam ediyor):
  - Playwright RPA + capture + mapping + toplu aktarım + status polling + müşteri timeline.
  - Zami zorunlu alanlar UI+RPA: medeni hal, meslek, anne adı, baba adı.
  - Mapping veri kaybı bug fix tamam.
  - **OTP ayda bir yaklaşımı:** trusted-device cookie’leri saklanır; oturum düştüğünde OTP’siz auto-relogin denenir; OTP gerekirse admin uyarılır.
  - **OTP hatırlatıcı:** yaklaşan OTP veya OTP required durumunda admin’e e-posta + WhatsApp (24h dedupe).

- Hosting/Deploy:
  - Paylaşımlı cPanel/PHP hosting yok; FastAPI + Playwright + MongoDB gerektirir.
  - Kullanıcı domain alır; uygulama Emergent üzerinde; DNS ile bağlanır.
  - **Canlı yayın hazırlığı (tamamlandı):** deploy taraması PASS, domain bağımlılıkları düzeltildi.
  - **Güvenlik (tamamlandı):** admin kimlik bilgileri koddan kaldırıldı (env üzerinden), JWT_SECRET sertleştirildi.

---

## 2. Implementation Steps

### Phase 1 — Core POC (Tamamlandı)

---

### Phase 2 — V1 App Development (Tamamlandı)

---

### Phase 3 — Aile Başvurusu + Admin Vize PDF (Tamamlandı)

---

### Phase 4 — Marka/Tema Yenileme + Sosyal Kanıt (Tamamlandı)

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

---

### Phase 11 — Zorunlu Seyahat Belgeleri + Kart Tıklama Davranışı (Tamamlandı)

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

---

### Phase 17 — Vize Başvurusu İçinde eSIM + Sigorta Upsell (Tamamlandı)

---

### Phase 18 — Ek Ürün Geçerlilik Tarihlerinin Seyahat Tarihine Bağlanması (Tamamlandı)

---

### Phase 19 — Akıllı Paket Önerisi + %10 Seyahat Paketi İndirimi (Tamamlandı)

---

### Phase 20 — Zami Tours Portalına Başvuru Aktarımı (Tamamlandı / canlı doğrulandı)

---

### Phase 21 — Toplu Aktarım + Otomatik Durum Takibi (Tamamlandı)

---

### Phase 22 — Alan Eşlemesi Otomasyonu (yakalama + otomatik öneri) (Tamamlandı)

---

### Phase 23 — Müşteri Durum Ekranı + Aktarım Hazırlık Kontrolü (Tamamlandı)

---

### Phase 24 — WhatsApp Bildirimleri (Manuel Mod) + Admin Ayarları (Tamamlandı)

---

### Phase 25 — Ücretsiz Ön Değerlendirme Sihirbazı (Kaldırıldı)

---

### Phase 26 — Kod Kalitesi Refactoring (Tamamlandı)

---

### Phase 34 — Zami Zorunlu Alanlar (Tamamlandı)

---

### Phase 35 — Resend Aktivasyonu (Tamamlandı; prod domain doğrulaması beklemede)

---

### Phase 36 — Zami Mapping Veri Kaybı Bug Fix (Tamamlandı)

---

### Phase 40 — Zami RPA “OTP Ayda Bir” (Tamamlandı)

---

### Phase 41 — Zami OTP Hatırlatıcı (E-posta + WhatsApp) (Tamamlandı)

---

### Phase 42 — Tasarım Sistemi Tam Yenileme (Sky Panels) (Tamamlandı)

---

### Phase 43 — Vize Kartları Vitrini (Tek dokunuşla seçim) (Tamamlandı)
- Home’da 6 kart → `/basvuru?vize=<id>`
- Apply query param ile seçimi preselect eder
- iteration_38 frontend %100

---

### Phase 44 — Kart Üstü Fiyat (Tamamlandı)
- VisaShowcase kartlarında:
  - Güncel **TL fiyat** (₺)
  - “kişi başı” etiketi
  - USD karşılığı + “güncel kurla” notu
- Fiyatlar `/vize-tipleri` ve başvuru özetiyle birebir doğrulandı
- iteration_39 frontend %100

---

### Phase 45 — Zami OTP Canlı Giriş Sağlamlaştırma (Tamamlandı; onboarding beklemede)
**Amaç:** İlk OTP’li girişin başarı oranını artırıp “OTP ayda bir” mekanizmasını gerçekten devreye almak.

**Bulgular ve düzeltmeler**
1) **Trusted Device seçimi (KÖK NEDEN 1):**
   - Portal login sayfasında cihaz tipi radyoları (`si`) var; varsayılan “No Change” cihazı paylaşım sayıp OTP’yi sıklaştırıyor.
   - Çözüm: `_login_credentials_step` içinde de “Trusted Device” işaretleniyor.
   - `_mark_trusted_device` sağlamlaştırıldı: normal check → force check → JS fallback.
   - Canlı doğrulama: `si=2` checked.

2) **Eşzamanlı giriş yarışı (KÖK NEDEN 2):**
   - Keepalive/auto_relogin interaktif login sırasında portala bağlanıp oturumu düşürüyordu (“IP Address changed”).
   - Çözüm: `_login_lock` + `interactive_login_active()`.
   - `auto_relogin` ve `keepalive_session` interaktif login varken atlıyor.
   - `auto_relogin` gövdesi kilit altına alındı (`_auto_relogin_locked`).

3) **OTP süresi çok kısa (KÖK NEDEN 3):**
   - Portal OTP kodu birkaç dakika geçerli (“Time’s up!”) ve yeni kod için 15 dk bekletiyor.
   - Çözüm: Admin’in captcha adımıyla zaman kaybetmemesi için yeni akış:
     - Backend: `start_session_to_otp()` + endpoint `POST /api/admin/zami/session/start-otp`
     - Admin UI: “Oturum başlat” artık `start-otp` çağırıyor; OTP input autoFocus, sadece rakam, Enter ile gönderim, “süre kısa” uyarıları.
   - Ek: Login hata mesajları portal metnine göre Türkçeleştirildi (OTP cooldown/captcha), SESSION_IDLE_LIMIT 900→1800.

**Durum**
- Onboarding hâlâ beklemede: `trusted_device=false`, `otp_required=true`, `expired=true`.
- Bu noktadan sonra OTP’nin panelden hızlı girilmesi gerekir.

---

### Phase 46 — Başvuru Formu Alan Revizyonu (Kullanıcı İsteği) (Tamamlandı)
**Amaç:** Kullanıcı sorusu “neden soruyorsun?” netliğinde; pasaportta olmayan bilgiler açıklansın, form gereksiz alan sormasın.

**Yapılanlar**
1) **Etiket standardı (Title Case):**
   - “Doğum Tarihi”, “Pasaport No”, “Geçerlilik Tarihi”
   - Tutarlılık için ayrıca: “Medeni Hal”, “Anne Adı”, “Baba Adı”, “Vize Türü”, “T.C. Kimlik No”, “Doğum Ülkesi”, “Gidiş Tarihi”, “Dönüş Tarihi”.

2) **Cinsiyet alanı kaldırıldı (frontend):**
   - “Cinsiyet” alanı ve doğrulaması formdan tamamen çıkarıldı.
   - Cinsiyet artık yalnızca **pasaport AI OCR (MRZ)** üzerinden gelir.

3) **Model doğrulama güncellendi (backend):**
   - `models.TravelerIn.gender` artık opsiyonel: `^(male|female|)$`.
   - Böylece cinsiyet boşken başvuru oluşturma 422’ye düşmez.

4) **Zami aktarım güvenliği:**
   - Cinsiyet boşsa Zami aktarımı **net Türkçe hata** ile bloke edilir (`_missing_gender_names`).

5) **Admin üzerinden düzeltme:**
   - Yeni endpoint: `PATCH /api/admin/applications/{id}/traveler` (`index`, `gender`).
   - Admin başvuru detayında “Cinsiyet okunamadı — Zami aktarımı için seçin” uyarısı + select eklendi.

6) **Bilgi kutusu metni netleştirildi:**
   - “BAE başvuru formu için gereken 4 ek bilgi” + “Neden soruyoruz?” açıklaması.

**Test**
- iteration_40: backend 36/36, frontend %100, admin %100, e2e %100

---

### Phase 47 — OCR Performans Ölçümü (Form Hız Testi) (Tamamlandı)
- Yeni modül: `/app/backend/ocr_metrics.py`
  - `ocr_metrics` koleksiyonuna: süre (ms), okuma başarısı, doldurulan/eksik alanlar, core_complete, confidence
  - TRACKED_FIELDS: 11 alan
  - CORE_FIELDS: 5 zorunlu alan
  - `summarize()` saf fonksiyon: success/core rates, avg/p50/p90, alan dolulukları, top missing
- `/api/passport/read` artık şunları döndürür:
  - `duration_ms`, `filled_count`, `missing_fields` (+ mevcut `data`)
- Yeni endpoint: `GET /api/admin/ocr-report?days=30`
- Admin dashboard: `OcrReportCard`
  - Ortalama süre, medyan, başarı oranı, zorunlu alan tamlığı
  - Alan doluluk barları + en sık okunamayan alanlar + son ölçümler
- Pasaport AI prompt iyileştirmesi:
  - T.C. Kimlik No MRZ personal-number alanından da çekilir (canlı doğrulandı)
- **Canlı ölçüm örneği:** ortalama ~3.3 sn, medyan 3.4 sn, başarı %100, 11 alandan 10’u dolu; okunamayan: “Veriliş Yeri” (%0)
- iteration_41: OCR testleri %100

---

### Phase 48 — Canlı Yayın Hazırlığı (Tamamlandı)
- Deploy taraması PASS:
  - `.gitignore` artık `.env` dosyalarını dışlamıyor → deploy blocker giderildi
- Domain bağımlılıkları düzeltildi:
  - `frontend/public/robots.txt` ve `sitemap.xml` artık `https://dubaivizeonline.com`
  - `PUBLIC_BASE_URL` fallback’leri `vizeatlas.com` → `dubaivizeonline.com`
- Stripe incelemesi:
  - success/cancel URL’leri istemci `origin_url` üzerinden üretildiği için domain değişiminde kırılmıyor
  - webhook URL `request.base_url` üzerinden üretildiği için canlı domain’de otomatik doğru
  - **Canlıya geçiş için tek kritik değişiklik:** `backend/.env STRIPE_API_KEY = sk_live_...`
- Sahte veri temizliği:
  - DB’deki test firma verileri temizlendi
  - TÜRSAB rozeti artık belge numarası yoksa render olmuyor
- İletişim bilgileri artık tek kaynaktan:
  - Yeni `useContact` hook (`/content/site` cache)
  - Navbar/Footer/Contact/Services/Home/Apply/WhatsAppButton dinamik
  - Telefon/WhatsApp/adres girilmemişse **placeholder gösterilmez** (alan gizlenir)
  - Admin panelden girilince otomatik görünür
- Kritik bug fix:
  - `admin_update_company` boş string’leri filtreliyordu → artık boş string’ler DB’ye yazılabiliyor (placeholder temizliği mümkün)
- iteration_41: contact wiring + OCR %100

---

### Phase 49 — Deployment Health Check + Güvenlik Sertleştirme (Tamamlandı)
**Amaç:** Canlıya çıkmadan önce “hardcoded secret/şifre” ve zayıf JWT anahtarını engellemek; deploy check’i sıfır blocker ile geçirmek.

**Yapılanlar**
- **BLOCKER fix:** `routes_admin.py` içindeki sabit `ADMIN_USERS` (admin@vizeatlas.com / Dubai2026!) kaldırıldı.
- Admin girişi artık tamamen env üzerinden:
  - `ADMIN_LOGIN_EMAIL`
  - `ADMIN_LOGIN_PASSWORD`
  - `ADMIN_LOGIN_NAME`
  - Şifre tanımlı değilse: net 500 mesajı.
- **JWT sertleştirme:** `JWT_SECRET` 26 → 64 karakter (InsecureKeyLengthWarning giderildi).
- Temizlik: testing agent’ın bıraktığı `backend/test_ocr_metrics.py` silindi (lint bare-except hataları kalktı).

**Doğrulama**
- Canlı doğrulama:
  - Doğru şifre → 200
  - Yanlış şifre → 401
  - Yanlış e-posta → 401
  - Token ile `/api/admin/me` → 200
- deployment_agent taraması tekrar çalıştırıldı → **PASS, findings: []**
- Sağlık: tüm servisler RUNNING; `/api/health` ok; public endpointler 200; frontend build temiz.

---

## 3. Next Actions

### P0 — Gerçek Firma Bilgileri (USER ACTION REQUIRED)
Admin → **Acente Bilgileri** ekranından doldurulacak:
- Telefon
- WhatsApp numarası
- Adres
- TÜRSAB belge no / şirket yasal bilgileri (varsa)
- Çalışma saatleri (opsiyonel)

Not: Bu alanlar girilene kadar sitede telefon/WhatsApp/adres görünmez (yanlış/placeholder gösterilmez).

---

### P0.1 — Zami “OTP Ayda Bir” Aktifleştirme: İlk OTP’li Giriş (USER ACTION REQUIRED)
**Yeni önerilen akış (süre kritik):**
1) Admin → Zami Aktarım → Robot Oturumu
2) **Oturum Başlat** (captcha otomatik geçilip OTP ekranına getirir)
3) E-postaya gelen OTP kodunu **hemen** girin (Enter ile gönder)

Beklenen: `device_state` + `last_otp_at` kaydolur → 1 ay OTP’siz yenileme.

---

### P0.2 — Stripe Canlı Anahtar (USER ACTION REQUIRED)
- `backend/.env` içinde `STRIPE_API_KEY = sk_live_...`
- (Opsiyonel) Stripe webhook endpoint’ini canlı ortamda doğrulayın: `/api/webhook/stripe`

---

### P0.3 — Custom Domain Deploy (USER ACTION REQUIRED)
- `www.dubaivizeonline.com` DNS yönlendirmesi (CNAME)
- Kök alan adı `dubaivizeonline.com` için A/ALIAS veya www’ye yönlendirme
- Emergent Deploy → **Link domain** → Entri akışı
- (Varsa) Resend domain doğrulaması / SPF-DKIM

---

### P0.4 — OTP Hatırlatıcı Kanalları (USER ACTION REQUIRED)
- `company_info.whatsapp` gerçek numara (veya env `ADMIN_WHATSAPP`)
- env `ADMIN_EMAIL` doğru (şu an `info@dubaivizeonline.com`)

---

### P0.5 — `onyuz-rehberi.pdf` Kapsam Kararı (USER DECISION REQUIRED)
A) Ana sayfa satış metni/hiyerarşi
B) Tracking görsel akış
C) Belirli bölüm
D) Atla

---

### P1 — Resend Production Gönderici (USER ACTION REQUIRED)
- Domain doğrulaması + `SENDER_EMAIL=noreply@dubaivizeonline.com`

---

### P2 — WhatsApp Otomatik Sağlayıcı (Twilio/Meta) (opsiyonel)

---

### Ops — Zami’de Kalan Manuel Alanlar (Backlog)
Eğitim + uçuş bilgileri.

---

### Tech Debt — Canlı RPA karmaşıklık azaltma (Backlog, riskli)
`fill_application`, `check_status`, `_upload_documents`.

---

## 4. Success Criteria
- Tema/marka: Sky Panels tutarlılığı, AA kontrast, mobil overflow yok, 44px hedefler.

- Vize Kartları Vitrini + fiyat:
  1) Home’da 6 kart render olur ve görseller bozuk değildir.
  2) Kart tıklaması `/basvuru?vize=<id>` ile sihirbazı açar.
  3) Kart üzerinde **TL kişi başı fiyat** görünür; `/vize-tipleri` ve başvuru özetiyle birebir aynıdır.

- Başvuru formu alan kriterleri (Phase 46):
  1) Kullanıcı formunda “Cinsiyet” sorulmaz.
  2) Etiketler Title Case ve tutarlıdır: “Doğum Tarihi”, “Pasaport No”, “Geçerlilik Tarihi” vb.
  3) “Neden soruyoruz?” açıklaması yalnızca 4 ek bilgiyi (Medeni Hal/Meslek/Anne Adı/Baba Adı) gerekçelendirir.
  4) Cinsiyet boş olsa bile başvuru uçtan uca oluşturulabilir (havale dahil).
  5) Zami aktarımı için cinsiyet gerekiyorsa admin panelden tamamlanabilir.

- OCR Performans (Phase 47):
  1) `/api/passport/read` her denemede `duration_ms` ve `missing_fields` döndürür.
  2) Admin `/admin/ocr-report` raporu: başarı oranı, core_complete_rate, avg/p50/p90 ve alan doluluklarını gösterir.
  3) Admin dashboard’da OCR performans kartı görünür ve yenilenebilir.

- Zami OTP ayda bir:
  1) İlk OTP’li giriş sonrası `device_state` kayıtlıdır (`trusted_device=true`, `last_otp_at` set).
  2) Oturum düşüşlerinde çoğu durumda OTP’siz auto-relogin başarılı.
  3) OTP gerçekten gerektiğinde admin e-posta + WhatsApp uyarısı; 24h dedupe.
  4) Admin UI “Oturum Başlat” ile OTP ekranına hızlı ilerler (start-otp).

- Deploy:
  - `https://www.dubaivizeonline.com` SSL aktif; cron job’lar (doc reminders, Zami status/keepalive, OTP reminders) çalışır.
  - robots/sitemap domain’i doğru (`dubaivizeonline.com`).
  - Stripe live key ile kart ödemesi uçtan uca çalışır.
  - Admin kimlik bilgileri ve JWT sırları kodda değil env’dedir.

---

## DURUM (2026-09-04 → güncellendi)
- Phase 1–43: **TAMAMLANDI**.
- Phase 44 (Kart üstü fiyat): **TAMAMLANDI** — iteration_39 frontend %100.
- Phase 45 (Zami OTP giriş sağlamlaştırma): **TAMAMLANDI** (kod + UI), ancak **ilk OTP’li giriş hâlâ kullanıcı aksiyonu**.
- Phase 46 (Başvuru formu alan revizyonu): **TAMAMLANDI** — iteration_40 backend+frontend+admin+e2e %100.
- Phase 47 (OCR Performans Ölçümü): **TAMAMLANDI** — iteration_41 %100.
- Phase 48 (Canlı Yayın Hazırlığı): **TAMAMLANDI** — deployment taraması PASS, domain bağımlılıkları düzeltildi, iletişim bilgileri panelden yönetilebilir.
- Phase 49 (Deploy health check + security hardening): **TAMAMLANDI** — hardcoded admin credential kaldırıldı, JWT_SECRET güçlendirildi; ikinci deploy taraması PASS.

Test raporları (seçme):
- iteration_35 — OTP ayda bir altyapısı backend PASS
- iteration_36 — OTP hatırlatıcı PASS
- iteration_37 — Sky Panels UI regresyon PASS
- iteration_38 — Vize vitrin seçimi frontend %100
- iteration_39 — Vitrin kart üstü fiyat frontend %100
- iteration_40 — Cinsiyet alanı kaldırma + etiket revizyonu PASS (e2e)
- iteration_41 — OCR ölçümü + iletişim wiring + canlı yayın hazırlığı PASS

Blokajlar / Bekleyen (tamamı kullanıcı aksiyonu):
- Gerçek firma iletişim bilgileri (Admin → Acente Bilgileri)
- Stripe canlı anahtar (`STRIPE_API_KEY=sk_live_...`)
- `www.dubaivizeonline.com` DNS + Emergent domain bağlama
- **Zami ilk OTP (start-otp ile panelden hızlı giriş)**
- Resend production domain doğrulama (SPF/DKIM) (opsiyonel ama canlı e-posta teslimi için önerilir)
