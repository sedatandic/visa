# Dubai Vize Online (VizeAtlas Dubai) — PRD

## Orijinal problem tanımı
Dubai/BAE vize başvuru sitesi: bilgi + fiyatlar + basit ve güzel başvuru formu.
Başvuruların DB'ye kaydı, admin paneli, e-posta bildirimleri, pasaport/fotoğraf yükleme,
Stripe & banka transferi ile ödeme, çok yolculu (aile) başvuru, admin vize PDF yükleme,
AI pasaport OCR ile otomatik doldurma, dinamik içerik/varlık yönetimi.
Ek: eSIM ve seyahat sigortası çapraz satışı (paket indirimi), Zami Tours RPA entegrasyonu
(Playwright otomatik doldurma, alan eşleme, durum sorgulama), görsel adım adım müşteri
takibi, WhatsApp bildirimleri.

Kullanıcı dili: **Türkçe** (tüm yanıtlar Türkçe olmalı).

## Mimari
- `backend/`: FastAPI (`server.py`), cron: `doc_reminders.py`, `zami_status.py`, `otp_reminders.py`
  AI: `passport_ai.py`, `captcha_ai.py`, `ocr_metrics.py` · RPA: `zami_rpa.py`, `zami.py`
  Admin route'ları: `routes_admin.py`, `routes_zami.py`
- `frontend/`: React (CRA) + Tailwind + Shadcn. `lib/site.js`, `lib/contact.js` dinamik içerik.
- MongoDB: `applications`, `site_settings`, `uploads`, `drafts`, `orders`, `email_outbox`

## Tamamlananlar (özet)
- Uçtan uca vize başvurusu, Stripe + banka transferi, aile/çok yolculu başvuru
- AI pasaport OCR + form hız testi raporu, fotoğraf doğrulama
- Admin paneli: başvurular, içerik, vize tipleri/rehberler, yorumlar, e-postalar, WhatsApp, banka
- eSIM & seyahat sigortası çapraz satış, paket indirimi
- Zami Tours RPA: alan eşleme, bookmarklet, robot oturumu, toplu aktarım, durum takibi
- Aylık OTP mekanizması (trusted-device cookie + AI captcha) + OTP hatırlatma cron
- "Flightin Sky Panels" tasarım sistemi (gökyüzü zemin, yüzen paneller, Figtree)

### 2026-06 (bu oturum)
- Playwright Chromium fork sonrası eksikti → kuruldu; `zami_rpa.py` içine tek seferlik
  otomatik `playwright install chromium` yedeği eklendi (yeni sunucu/deploy güvenliği)
- Zami robot oturumu doğrulandı: portal erişimi + AI captcha çözümü çalışıyor
  (OTP adımını kullanıcı Admin → Zami → "Robot Oturumu (B)" sekmesinden yapacak)
- **Marka logosu güncellendi**: yüklenen logo işlenip `public/brand/logo-horizontal.png`
  (yatay kilit: amblem + DUBAI Vize Online), `emblem-512.png` ve `logo-lockup.png` olarak
  hazırlandı; `BrandMark` artık tam yatay logoyu kullanıyor (header, footer, admin)
- **Partner logoları + bayrak çifti (2026-06)**: 6 havayolu logosu Wikimedia Commons'tan
  500px PNG olarak `public/brand/partners/` altına indirildi (emirates, flydubai,
  turkish-airlines, pegasus, ajet, sunexpress); `PARTNERS` artık {name, logo} sözlüğü ve
  Home partner kutuları logoyu gösteriyor (dosya yoksa marka adına düşer).
  Logonun yanına TR → BAE bayrak çifti eklendi (`brand-flag-pair`).
  NOT: Havayolu logoları tescilli markadır; resmî iş ortaklığı yoksa başlığı
  "Çalıştığımız havayolları" gibi bir ifadeye çevirmek daha güvenli.
- **Sayfa boşlukları ve genişlikler (2026-06)**: tüm Bilgi & Hizmetler sayfalarında başlık
  paneli ile içerik arası boşluk ~24-32px'e indirildi; SSS, blog listesi ve eSIM/sigorta SSS
  blokları başlık paneliyle aynı genişliğe alındı. Ekspres metni her yerde
  "yaklaşık 8 mesai saati" oldu. Vitrin kartlarındaki zemin fotoğrafları kaldırıldı.
- **Menü ve hizalama düzeltmeleri (2026-06)**: "Başvurularım" üst menüden çıkarılıp
  "Başvuru Takip" açılır menüsüne alındı (Takip Kodu ile Sorgula + Başvurularım);
  /hesabim girişinde e-posta ve soyad aynı satıra alındı; /takip kartları eşit genişlik;
  /vize-tipleri açıklaması tek satır + fiyat kutuları kartlar arasında hizalı
- **2026 fiyat listesi + sosyal butonlar (2026-06)**: müşterinin resmi fiyat tablosu uygulandı
  (30g tek 105$, 30g çocuk 50$, 30g çok 200$, 60g tek 200$, 60g çok 300$, uzatma 300$;
  60g çocuk 105$ ve transit 70$ değişmedi), ekspres hizmet kişi başı sabit 50$ ve
  "yaklaşık 8 mesai saatinde sonuç". Sağ altta `SocialDock` (WhatsApp + Instagram +
  Google yorum) ve footer sosyal satırı eklendi; linkler Admin → Acente Bilgileri'nden yönetilir.
- **Yönetici e-postası** `info@dubaivizeonline.com` olarak değişti (şifre `Dubai2026!`)
- **Üst menü büyütüldü (2026-06)**: navbar 92px, logo `h-14 sm:h-16`, menü yazıları `text-base`,
  "Başvuru Yap" `h-12`; masaüstü menü `lg`→`xl` breakpoint'e taşındı (1024px yatay kayma düzeltildi),
  ana sayfa hero üst boşluğu `pt-3 sm:pt-4` olarak azaltıldı
- **Kur kaynağı doviz.com (2026-06)**: `fx.py` birincil kaynak olarak
  `kur.doviz.com/serbest-piyasa/amerikan-dolari` satış (ask) kurunu HTML'den okur
  (`parse_doviz_html`); open.er-api ve exchangerate.host yedek olarak kalır.
  Kur notu artık kaynağı da gösteriyor.
- **Freelancer vizesi kaldırıldı (2026-06)**: `visa_freelancer_2y` VISA_TYPES ve GUIDES'tan
  silindi (DB'de `active:false`), ana sayfa şerit etiketi ve statik `sitemap.xml` temizlendi
- **GDRFA amblemi**: temsili SVG yerine resmi şahin amblemi (`public/brand/gdrfa.png`,
  ayrıca yazılı tam sürüm `gdrfa-full.png`) kullanılıyor — yetkili merciler şeridi ve footer rozeti: gökyüzü mavisi gradyan, grain dokusu ve ağır gölgeler kaldırıldı;
  zemin düz beyaz (`--background: 0 0% 100%`), nötr gri kenarlıklar, hafif gölgeler.
  Vitrin kartları koyu cam panel yerine sade beyaz kart (üstte görsel, altta metin+fiyat+buton).: ICP kartı kaldırıldı; sıra TÜRSAB (gerçek logo
  `public/brand/tursab.png`) → GDRFA olarak güncellendi, 2 kolonlu ızgara
- **Gold palet**: siyah/antrasit zeminler logodaki bakır-gold tonuna çevrildi
  (`--primary: 30 62% 42%`, `--navy: 34 60% 27%`, `--charcoal`, `--gradient-wave`)
- **Ana sayfa görsel kaydırıcısı**: `components/HeroSlider.jsx` — 5 Dubai görseli,
  4.5 sn'de otomatik geçiş, ok + nokta kontrolleri, hover'da durur (dubaivizeal.com referansı)

## Bekleyen / bloke
- **Zami OTP döngüsü (2026-06 çözüldü)**: keepalive her 10 dk'da şifre gönderip portalın
  OTP e-postası atmasına yol açıyordu. `auto_relogin` artık cihaz güveni yoksa veya
  `otp_required` işaretliyse portala hiç dokunmuyor; sadece admin `?force=true` ile zorlayabilir.
  Admin panelden bir kez OTP'li giriş yapılınca işaret temizlenir ve 30 gün otomatik çalışır.
- **P1 WhatsApp numarası**: DB'de geçici test numarası (905331234567) duruyor —
  gerçek numara Admin → Acente Bilgileri'nden girilmeli. Instagram/Google yorum
  linkleri de aynı ekranda düzenlenebilir (varsayılanlar geçici).
- **P0 Deployment**: Emergent tarafında manuel güven & güvenlik incelemesi nedeniyle bloke.
  Kodda blocker yok (health check PASS). Kullanıcı support@emergent.sh ile iletişimde.
- **P0 Zami OTP ilk giriş**: Kullanıcı Admin → Zami → Robot Oturumu (B) → "Oturum başlat"
  ile OTP kodunu girip cihaz güvenini kaydetmeli (30 gün OTP'siz çalışır).
- **P1** Şirket bilgileri (telefon, WhatsApp, adres, TURSAB) admin panelden güncellenmeli
- **P1** Stripe canlı anahtarları (domain açıldığında)
- **P2** Gerçek müşteri yorumları admin panelden eklenmeli
- **P2** `onyuz-rehberi.pdf` kapsamı netleşmedi (kullanıcı yanıtı bekleniyor)

## 2026-06-04 · UI + kod kalitesi turu
- Hero üst boşluğu kaldırıldı (`Home.jsx` pt-0 + panel pt-6/8)
- `components/HeroHeadline.jsx`: 3 slogan, 4.2 sn'de flip animasyonu, altın/bronz renk
- Logo altın varyanta geçti: `public/brand/logo-horizontal-gold.png`
  (yazı altın, amblem orijinal turkuaz/mavi korunuyor — kahverengi yığılmasını önlemek için)
- Footer + koyu bloklar açıldı: `--navy: 33 52% 34%`, footer `bg-[hsl(33_52%_34%)]`
- Navbar: "Başvuru Takip" alt menü kaldırıldı, doğrudan `/takip`
- `/takip` iki sütun: Takip kodu sorgulama + Başvurularıma giriş
  (`components/AccountLoginCard.jsx` MyAccount ile paylaşılıyor)
- Kod incelemesi: test dosyalarındaki sabit admin şifreleri kaldırıldı
  (`backend_test.py`, `regression_critical_tests.py`, `tests/test_zami_otp_fix.py` artık
  `ADMIN_LOGIN_EMAIL/PASSWORD` + `REACT_APP_BACKEND_URL` env'den okuyor).
  `exec()` ve `is` vs `==` bulguları doğrulandı: kodda yok (yalnız `create_subprocess_exec`).

## 2026-06-04 · Demo/test verisi temizliği
Silinen koleksiyonlar (tümü 0'a indi): visa_applications(95), application_drafts(25),
saved_travelers(99), store_orders(22), payment_transactions(28), contact_messages(19),
pre_evaluations(8), email_outbox(720), zami_logs(253), notifications(16), whatsapp_logs(5),
ocr_metrics(4), uploads(373), zami_handoffs(9), login_codes(4), testimonials(6).
Korunanlar: site_settings (acente bilgileri, Zami eşleme + oturum), visa_types(10),
store_products(6), articles(5).
Not: `testimonials` boş olduğunda `/api/content/site` statik demo yorumlara düşüyor
(routes_public.py:315) — gerçek yorumlar Admin → Yorumlar'dan eklendiğinde otomatik değişir.
Object storage'daki eski dosyalar fiziksel olarak silinmedi, yalnız DB kayıtları temizlendi.

## 2026-06-04 · Seyahat sigortası gün bazlı katalog
Kaynak: seyahatpolicesi.com (BAE = Schengen dışı "Diğer Ülkeler" tarifesi, 30.000 € teminat).
Satış fiyatı = kaynak TL fiyatı × 2 (INSURANCE_MARKUP=2.0), `price_try` alanında TL olarak sabit
(FX dönüşümü uygulanmaz; eSIM ürünleri USD→TRY dönüşümüyle devam ediyor).
Poliçeler: ins_8d 491₺, ins_15d 560₺, ins_31d 644₺ (popüler), ins_63d 735₺,
ins_30d_plus 2754₺, ins_60d_plus 3989₺ (geniş kapsam: bagaj + seyahat kesintisi).
Başvuru formunda seçenekler `requiredInsuranceDays = max(seyahat günü, vize duration_days)`
ile filtrelenir; kapsamı yetmeyen seçim otomatik düşer. Admin panelden `price_try` düzenlenebilir
(PATCH /api/admin/products/{id}). Test: /app/backend/tests/test_insurance_catalog.py (8/8 PASS),
iteration_57 backend+frontend %100.
Ayrıca: BAE 4 ek alan (medeni hal, meslek, anne/baba adı) müşteri formundan kaldırıldı,
backend `_fill_uae_defaults()` ile otomatik dolduruluyor (single / Employee|Student / soyad).
"Yapay zeka" ifadeleri müşteri arayüzünden temizlendi. Menü: "Gelişmeler"→"Dubai'den Haberler",
"Yanınızdaki Ekstralar"→"Ekstra Hizmetler".

## 2026-06-04 · Otomatik poliçe kesim kuyruğu + kâr paneli
Poliçe seçenekleri yeniden düzenlendi (kullanıcı isteği: vize süresini AŞMAYAN poliçeler):
ins_8d 8g/491₺, ins_15d 15g/560₺, ins_30d 30g/644₺, ins_30d_plus 30g/2754₺,
ins_60d 60g/735₺, ins_60d_plus 60g/3989₺ — her birinde `cost_try` (kaynak maliyet).
Filtre: `validity_days <= max(vize duration_days)` (Apply.jsx visaCoverDays memo).
Yeni: `backend/insurance_tasks.py`
- `queue_policy_tasks(order)`: ödeme paid olduğu anda (kart, havale onayı, vize başvurusu
  ödemesi) poliçe kesim görevi oluşturur (idempotent), müşteriye "hazırlanıyor" e-postası +
  admin bildirimi gönderir, sağlayıcı için ön doldurmalı `provider_link` üretir.
- `issue_policy(task, file_id)`: yüklenen poliçe PDF'ini müşteriye e-postalar, görevi kapatır.
- `profit_report()`: poliçe başına maliyet/satış/kâr/marj + satılan adet, ciro, toplam kâr.
Endpointler: GET /api/admin/insurance-tasks, POST /api/admin/insurance-tasks/{id}/issue,
GET /api/admin/insurance-report. Admin UI: `/admin/sigorta` (AdminInsurance.jsx).
Ürün kartlarında TL satış + maliyet düzenlenebilir (price_try/cost_try).
Test: iteration_58 backend 8/8 + frontend %100 (tests/test_insurance_automation.py).
SINIR: seyahatpolicesi.com açık API sunmuyor; kesim adımı tek tık + PDF yükleme (yarı otomatik).
Tam otomasyon için sağlayıcı API/portal hesabı gerekir.

## 2026-06-04 · Aylık kâr grafiği
GET /api/admin/profit-monthly?months=12 → ay bazlı sigorta/eSIM ciro, maliyet ve kâr
(`insurance_tasks.monthly_profit`). Admin → Sigorta Poliçeleri sayfasının üstünde
recharts yığılmış çubuk grafik (`components/MonthlyProfitChart.jsx`).
Ürün kartlarında artık eSIM dahil tüm ürünler için ₺ maliyet girilebiliyor (cost_try),
böylece eSIM kârı da gerçek marjla hesaplanır (maliyet girilmezse kâr = ciro).

## 2026-06-04 · Paketler + adım göstergesi + ekstraların Adım 4'e taşınması
- `GET /api/bundles?visa_days=30|60` → vize süresine uygun hazır paketler
  (routes_store.BUNDLE_TEMPLATES + bundle_list): pack_short/pack_standard/pack_comfort (30 gün),
  pack_long/pack_long_plus (60 gün). Fiyat = sigorta + eSIM, %10 paket indirimi düşülmüş.
- `components/BundlePicker.jsx`: paket kartları; tıklayınca sigorta seçimi + eSIM adedi otomatik.
- Sihirbaz adım göstergesi: tek parça progress bar kaldırıldı, her adımın altında kendi
  hizasında dolum çizgisi (`wizard-step-bar-{key}`, adım anahtarları: people/visa/docs/summary).
- Sigorta + eSIM + paket blokları Adım 2'den **Adım 4 (Özet ve ödeme)** başına taşındı.
  Başvuru yalnız ödeme anında oluşturulduğu için Adım 4 seçimleri fiyata dahil.
- Testler: iteration_59 (backend /bundles 4/4), iteration_60 (frontend uçtan uca 8/8 kriter).
  Test verileri temizlendi.

## 2026-06-04 · Kombinasyonlar + havale bilgileri + ana sayfa satış blokları
- `components/ComboSelector.jsx`: Adım 4'te "Ne almak istiyorsunuz?" — Sadece vize / Vize+eSIM /
  Vize+sigorta / Vize+eSIM+sigorta (%10 indirim). `applyCombo()` ekstraları set/temizler.
- `components/BankTransferInfo.jsx`: Havale/EFT seçildiği an (başvuru oluşmadan) alıcı, banka,
  IBAN, tutar + `agency_info.items` şirket bilgileri gösterilir.
- `components/ExtrasQuickAdd.jsx`: sağ panelde her adımda sigorta/eSIM hızlı ekleme; özet
  kırılımı ve toplam canlı güncellenir. `changeEsimQty` artık 0'a düşürüp kalemi siler.
- Ana sayfa: `HomeBundleStrip.jsx` (vize dahil toplamlı 3 paket) + `SeparatePriceCards.jsx`
  (Vize / Sigorta / eSIM sekmeli ayrı fiyat kartları).
- Testler: iteration_61 (9/9), iteration_62 (10/10) frontend %100. Test verileri temizlendi.
- YAPILACAK: `site_settings.bank_transfer` hâlâ örnek veri
  ("VizeAtlas Turizm ve Danışmanlık A.Ş." / "Örnek Bank A.Ş." / TR00...) — Admin → Havale
  ekranından gerçek unvan, banka ve IBAN girilmeli.

## 2026-06-04 · Kod incelemesi turu 2
Uygulanan: tests/test_insurance_catalog.py ve test_insurance_automation.py artık admin
kimlik bilgilerini ve BASE_URL'i .env'den okuyor (sabit şifre/fallback kaldırıldı);
eski ins_31d/ins_63d id'leri ins_30d/ins_60d olarak güncellendi.
`insurance_tasks.monthly_profit` 71 satırdan ~20 satıra indirildi
(`_empty_bucket`, `_month_keys`, `_add_order_to_bucket`, `_month_row` yardımcıları).
Doğrulanan yanlış pozitifler: `exec()` yok (asyncio.create_subprocess_exec);
`is` vs `==` için üretim kodunda tek örnek yok (yalnız testlerde doğru olan `is True/False`);
insurance_tasks ↔ routes_store döngüsel import zaten fonksiyon içi (lazy) import ile çözülü.
pytest: 39/39 PASS.

## 2026-06-05 · Ana sayfa yeniden kurgusu (sade + dönüşüm odaklı)
Kullanıcı DubaiVizeOnline tarzı, tekrarsız ve sade bir yapı istedi. Ana sayfa 14 bölümden
10 bölüme indirildi (`pages/Home.jsx` tamamen yeniden yazıldı):
Hero (kısa metin + 2 CTA + slider + promo + 3'lü güven şeridi) → AuthorityStrip →
**Neden Bizi Tercih Etmelisiniz** (5 avantaj + "Kimler Başvurabilir?" kartı) →
**Başvuru Süreci** (4 adım, statik metin) → **Dubai Vize Türleri** (VisaShowcase, fiyatlı) →
FX/fiyat notu → Seyahat Paketleri (HomeBundleStrip) → Gerekli Belgeler →
**Başvuru Takibi** (ana sayfada takip kodu kutusu → /takip?kod=) → Müşteri Yorumları
(ReviewSpotlight) → SSS → CTA bandı (Başvuru Yap + WhatsApp).
Kaldırılanlar: hero istatistik şeridi, kayan yazı şeridi (marquee), Hizmetlerimiz,
Neden Biz, SeparatePriceCards, uzun SEO metni, SampleVisa, havayolu logoları,
haberler bloğu, yorum ızgarası, ayrı WhatsApp bölümü (CTA bandına taşındı),
PricingTabs (yalnız /vize-tipleri sayfasında kaldı).
Kullanıcı kararları: 14 günlük vize EKLENMEDİ (resmi fiyat listesinde yok);
vize kartlarında fiyat gösterilir; yorumlar kalır, logolar ve haberler kalkar.
VisaShowcase başlığı "Dubai vize türleri ve fiyatları" oldu. Meta başlık/açıklama güncellendi.
Test: iteration_63 frontend %100 (11 bölüm + 8 kaldırılan bölüm + takip formu + regresyon).
Not: `components/SeparatePriceCards.jsx`, `SampleVisa.jsx`, `Testimonials.jsx` (grid),
`IconCards` ana sayfada kullanılmıyor ama dosyalar korundu (diğer sayfalar/ileride kullanım).

## Kod incelemesi doğrulaması (2026-06-05)
Devralınan "kritik" iki bulgu YANLIŞ POZİTİF: `zami_rpa.py`'de `exec()` yok
(sadece `asyncio.create_subprocess_exec`, satır 90); `insurance_tasks` ↔ `routes_store`
importu fonksiyon içi lazy import (insurance_tasks.py:232,257 · routes_store.py:544).

## Sıradaki açık işler
- **Kur kaynağı (2026-09-07 güncel)**: birincil kaynak **TCMB günlük bülteni**
  (`kurlar/today.xml`, USD `ForexSelling` = döviz satış). Bülten iş günü 15:30'da
  yayınlanır; `fx.expected_bulletin_date()` buna göre günlük tazeleme yapar.
  Yedekler: Yahoo `USDTRY=X`, doviz.com, open.er-api, exchangerate.host.
- **P0 Zami Bookmarklet "Gönder/Submit" butonu yakalama** (2 oturumdur bekliyor, kullanıcı
  detay/ekran görüntüsü paylaşmadı)
- **P1 Gerçek havale bilgileri** (`site_settings.bank_transfer` hâlâ örnek: VizeAtlas Turizm /
  Örnek Bank / TR00...) → Admin → Havale
- **P1 Gerçek WhatsApp/Instagram/Google yorum linkleri** (DB'de test numarası 905331234567)

## 2026-06-05 · İçerik tekrarı temizliği + çelişki düzeltmeleri (kullanıcı denetimi)
Kullanıcı siteyi gezip tekrar ve çelişki raporu verdi. Uygulananlar:
- **Vize kartı metinleri tek şablona alındı** (kullanıcı: "diğer hizmetler de 30 günlük vize
  gibi yaz"): 8 aktif vize tipinin tamamı artık aynı desende — açıklama "... bu vize uygundur."
  kalıbı + tam 5 özellik, son ikisi her kartta "Uzman danışman desteği" ve
  "Dijital vize teslimi". `content.py` VISA_TYPES güncellendi ve
  `scripts/sync_visa_copy.py` ile `visa_types` koleksiyonuna senkronlandı
  (DB, statik içeriği ezdiği için ikisi de gerekliydi).
- **Rehber sayfaları tekilleştirildi** (~%70 ortak metin → yalnız vizeye özel içerik):
  `visa_guides.py` COMMON_FAQ kaldırıldı (genel 4 soru artık sadece /sss'te),
  `build_guide` artık `photo_rules` ve `process_steps` döndürmüyor.
  `VisaGuide.jsx`: belge kartları kompakt satıra indi + /gerekli-belgeler linki,
  fotoğraf kuralları bloğu ve 4 adımlı süreç ızgarası kaldırıldı,
  "Danışman notları" kendi bölümü oldu (ana sayfa süreç linkiyle), SSS altına /sss linki.
- **Çelişkiler giderildi**: çalışma saati tek kaynak (company.working_hours) —
  `Faq.jsx` sabit "09:00-19:00" kaldırıldı; sosyal kanıt tek kaynak —
  `About.jsx` sabit "4.500+" yerine review_summary (5.678+ / %96),
  `content.py` REVIEW_SUMMARY.total_applications 4500→5678; ekspres süresi her yerde
  "yaklaşık 8 mesai saati" (yorumdaki "20 saat" düzeltildi);
  `Services.jsx` başlığı "Tek işimiz vize" → "Odağımız vize" (eSIM/sigorta satışıyla çelişiyordu).
- **Yanlış alarm**: kullanıcının gördüğü test verileri (Test Turizm A.Ş., test@vizeatlas.com,
  0850 123 45 67) ne kodda ne DB'de var (DB unvan: "Dubai Vize Online Ltd."); farklı fiyatlar
  (9.870/10.860/2.710) da eski kurla hesaplanmış önbellek. Kullanıcı deploy edilmiş/eski
  sürümü geziyordu — canlıya yeniden deploy gerekiyor.
- Test: iteration_64 backend %100 + frontend %100 (8 düzeltmenin tamamı + ana sayfa regresyonu).

## 2026-06-05 · Mantık hatası denetimi (kullanıcı: "siteyi incele mantıksal hata bul")
Bulunan ve düzeltilen 6 mantık hatası:
1. **Pasaport 6 ay kuralı hiç doğrulanmıyordu** — site "tek teknik şart" diye duyuruyor, form
   yalnızca "tarih geçmiş mi" kontrol ediyordu. Artık dönüş tarihinden itibaren 180 günden az
   geçerliliği olan pasaportlar hem formda hem API'de engelleniyor.
2. **18 yaş altı yolcu tek başına başvurabiliyordu** (SSS aksini söylüyor) — artık aynı
   başvuruda en az bir yetişkin zorunlu.
3. **Yetişkin, indirimli çocuk vizesiyle API'den geçebiliyordu** (frontend kontrol ediyordu,
   backend etmiyordu) — gelir kaybı/ret riski; artık sunucu tarafında yaş kontrolü var.
4. **Kalış süresi vize süresini aşabiliyordu** (30 günlük vizeyle 46 gün, 48 saatlik transitle
   5 gün) — artık yolcu bazında engelleniyor.
5. **Geçmiş tarihli gidiş** API'den kabul ediliyordu — engellendi.
6. Ana sayfa paket şeridinde **iki "En çok seçilen"** etiketi görünüyordu (pack_standard +
   pack_long) → tek etiket; "Kimler başvurabilir?" metni formla çelişiyordu (form yalnız
   Türkiye doğumlu kabul ediyor) → bordo/yeşil pasaport ayrımı ve Türkiye şartı yazıldı.
Kod: `routes_public._validate_travel_rules` (+ PASSPORT_MIN_VALID_DAYS=180) tek kural noktası;
`_build_travelers(inputs, travel)` kuralları dosya kontrolünden ÖNCE çalıştırır.
`Apply.jsx validateStep` aynı kuralları adım 1-2'de gösterir (e.travelers_adult, e.stay_length,
e.passport_validity blocking toast olarak sunulur).
Test: iteration_65 backend 9/9 pytest (`backend/tests/test_travel_rules.py`) + frontend %100
(üç sihirbaz engeli, tek popüler etiket, yeni uygunluk metni).

## 2026-06-05 · Uygunluk ön kontrolü + vize süresi önerisi
- **`components/EligibilityPreCheck.jsx` (yeni)**: /basvuru Adım 1'in en üstünde gidiş, dönüş
  ve pasaport geçerlilik tarihi sorar. Sonuç 3 durumdan biri:
  `ok` (yeşil: kalış gün sayısı + önerilen vize adı/fiyatı + "Bu bilgilerle devam et"),
  `error` (pasaport dönüşten itibaren 6 aydan az geçerli → gereken asgari tarih yazılır),
  `warning` (60 günden uzun kalış → 60 gün + yurt içi uzatma açıklaması, devam butonu yok).
  "Devam et" tarihleri `travel`e, pasaport tarihini boş olan yolculara, önerilen vizeyi
  seçili olmayan yolculara yazar (`applyPreCheck`), panel kapanır.
- **Vize süresi önerisi (upsell)**: Adım 2'de kalış seçilen vizeyi aşarsa
  `visa-upgrade-suggestion` bandı çıkar: "Planlanan kalış X gün, Y günlük vize gerekiyor
  (fiyat)" + "Y günlük vizeye geç" butonu (`applyVisaUpgrade`, yolcu bazında
  `pickVisaFor` ile giriş tipini ve yetişkin/çocuk ayrımını korur). 60 günü aşan kalışta
  buton yerine uzatma bilgisi gösterilir. Böylece iteration_65'teki engel satış fırsatına
  dönüştü (müşteri hata alıp çıkmıyor, tek tıkla üst vizeye geçiyor).
- Test: iteration_66 frontend %100 (6 senaryo: ok/error/warning, forma aktarma, upsell
  butonu + toplam 9.880₺ güncellemesi, 60 gün üstü uyarı).
- Bilinen sınır: upgrade bandındaki önerilen vize adı ilk uygun olmayan yolcudan alınır;
  uygulama adımı yine yolcu bazında doğru vizeyi seçer.

## 2026-06-05 · Ekspres önerisi (ön kontrolde)
Ön kontrolde gidiş tarihine 72 saatten az kalmışsa `precheck-express-suggestion` bloğu çıkar:
kalan saat + "standart ortalama 2 iş günü, ekspres yaklaşık 8 mesai saati" + kişi başı ekspres
ücreti (addonMeta'dan, 2.470₺). Switch varsayılan AÇIK; "Bu bilgilerle devam et" tıklanınca
`applyPreCheck` ekspres ek hizmetini otomatik seçer (setAddons express:true) ve özet toplamına
yansır (5.190 + 2.470 = 7.660₺). Switch kapatılırsa ekspres seçilmez.
Test: iteration_67 frontend %100 (acil/acil değil, ekspres açık/kapalı taşıma, error/warning
regresyonu). Not: ön kontrol artık uygun vizeyi otomatik seçtiği için upgrade bandı yalnız
kullanıcı elle kısa süreli vize seçtiğinde görünür (iteration_66'da %100 doğrulanmıştı).

## 2026-06-05 · E-postaların spam'e düşmesi (kullanıcı bildirdi) + bölüme özel metinler
**Kök neden**: `SENDER_EMAIL=onboarding@resend.dev` — Resend'in paylaşımlı sandbox alan adı.
Gmail, "Dubai Vize Online" adıyla gelen ama resend.dev'den gönderilen postada SPF/DKIM
hizalanmadığı için hepsini spam'e atıyor. **Çözüm kullanıcı eylemi gerektirir**:
resend.com/domains → dubaivizeonline.com ekle → DKIM/SPF/DMARC TXT kayıtlarını DNS'e gir →
`SENDER_EMAIL`i doğrulanmış adrese çevir (kullanıcıya soruldu, yanıt bekliyor).
Kod tarafında yapılan teslim edilebilirlik düzeltmeleri (`emailer.py`):
- Her postaya **düz metin alternatifi** eklendi (`_html_to_text`, html.unescape + \xa0 temizliği);
  Gmail HTML-only postaları cezalandırıyordu.
- **`reply_to`** eklendi (REPLY_TO_EMAIL → ADMIN_EMAIL); footer "yanıtlayabilirsiniz" diyor ama
  yanıtlar resend.dev'e gidiyordu (spam sinyali).
- `draft_reminder` gibi pazarlama postalarına **List-Unsubscribe + One-Click** başlıkları
  (MARKETING_KINDS); işlemsel postalara eklenmiyor.
- Gönderici resend.dev ise başlangıçta uyarı logu.
**Bölüme özel metinler**: kullanıcı "bu yazıları her başlık için özelleştirelim" dedi; ana
sayfadaki genel hero paragrafı ve tüm bölüm alt metinleri bölüme özgü, somut cümlelerle
değiştirildi (hero, avantajlar, süreç, vize türleri, belgeler, takip, SSS, CTA — hiçbiri
tekrar etmiyor).
Test: iteration_68 backend 7/7 (`tests/test_emailer.py`, monkeypatch ile gerçek posta
gönderilmedi) + frontend %100 (8 metin doğrulandı). Ayrıca `tests/test_uae_defaults.py`
sabit geçmiş tarihleri (2026-03-01) yeni kural nedeniyle 400 alıyordu → dinamik
`date.today() + 30/36 gün` yapıldı. pytest: 55/55 PASS.

### 2026-06-05 · Gönderici adresi ayarlandı
Kullanıcı Resend'de dubaivizeonline.com'u ekledi; `backend/.env` → `SENDER_EMAIL`
`onboarding@resend.dev` → **`info@dubaivizeonline.com`**. Backend yeniden başlatıldı ve
gerçek bir test postası gönderildi: `status=sent`, provider_id alındı (Resend doğrulanmamış
alan adından gönderime izin vermediği için alan adı doğrulanmış demektir).
UYARI: kullanıcı DKIM/SPF/DMARC DNS kayıtlarını eklediğini teyit etmedi ("skipped" dedi).
Kayıtlar eksikse gönderim çalışsa bile Gmail yine spam'e atabilir; kullanıcının test
postasının Gelen Kutusu'na düştüğünü doğrulaması gerekiyor.

## 2026-06-05 · Çöl safarisi ürünü + paket kartı tıklanabilirliği + fiyat sekmeleri
**Rakip analizi (vizemdubai.com)**: eksiklerimiz kullanıcıya sunuldu; kullanıcı yalnızca
"çöl safarisini ekle" dedi (kurumsal hizmetler, acente paneli, güven paketi = gerek yok).
- **Çöl Safarisi** (`tour_desert_safari`, kind `tour`, 45$ ≈ 2.220₺/kişi): `routes_store.py`
  TOUR_PRODUCTS + KIND_LABELS["tour"]="Dubai turu"; `scripts/sync_products.py` ile DB'ye eklendi.
  Sihirbazda "Dubai'de yapacaklarınız" bölümü (`apply-tour-section`): switch + kişi sayısı
  arttır/azalt, tarih seçimi gerektirmez, fiyat özetine ve siparişe yansır.
  eSIM/sigorta mağaza sayfalarında çapraz satış olarak GÖSTERİLMEZ (StoreCheckout crossProducts).
- **Paket kartları tamamen tıklanabilir** (kullanıcı: "cant click on each summary cards"):
  kart artık `/basvuru?paket=<id>` linki; iç buton span oldu (iç içe <a> yok). Apply'da
  `?paket=` okunup vize + sigorta + eSIM hazır seçiliyor (bundleApplied useRef ile tek sefer).
- **Fiyat sekmeleri**: "Tek Girişli" → **Tek Girişli Vize**, "Çok Girişli" → **Çok Girişli Vize**,
  **"Diğer Hizmetler" sekmesi kaldırıldı**; vize uzatma ve transit vize artık tek girişli
  vizelerle aynı satırda (4 kart, xl:grid-cols-4).
  ÖNEMLİ: uzatma/transit `category=single` olduğu için otomatik önerilere karışmasın diye
  `auto_suggest: False` alanı eklendi (content.py + DB, `scripts/sync_visa_categories.py`);
  ön kontrol ve upgrade bandı bu alanı filtreliyor — 2 günlük kalışta bile 30 günlük vize
  öneriliyor, transit/uzatma asla önerilmiyor.
Test: iteration_70 (safari) backend %100 / frontend 83% → çapraz satış hatası düzeltildi;
iteration_71 backend %100 + frontend %100 (sekmeler, 4 kart, auto_suggest koruması,
çapraz satış düzeltmesi, paket ön seçimi regresyonu).
Bilinen teknik borç: `Apply.jsx` 2453 satır — adım bileşenlerine bölünmesi öneriliyor.

## 2026-06-06 · Çöl safarisi tarih/saat seçimi + kapak fotoğrafı
Kullanıcı isteği: safari için tarih/saat seçimi (WhatsApp'tan manuel koordinasyon kalksın)
ve kartta kapak fotoğrafı. Ajan kararları: hazır saat dilimleri, tarih ZORUNLU.
- **Ürün**: `TOUR_PRODUCTS.tour_desert_safari` → `image_url` (Unsplash çöl kumulu),
  `needs_schedule: True`, `time_slots: ["14:00","14:30","15:00","15:30","16:00"]`.
  DB kaydı (`store_products`) upsert ile güncellendi.
- **Backend**: `StoreItemIn` + `scheduled_date` / `scheduled_time`;
  `routes_public._tour_schedule()` → tarih zorunlu (400 "tur tarihi secmelisiniz"),
  gidiş tarihinden önce / dönüşten sonra reddedilir, listede olmayan saat ilk slota düşer.
  Satır `pricing.store_items` içinde saklanır; `_application_order_items` ve sipariş notu
  tur rezervasyon bilgisini taşır; `emailer._store_item_label` e-postada tarih+saat yazar;
  admin başvuru detayında satır etiketinde görünür.
- **Frontend** (`Apply.jsx`): `tourSchedule` state (draft'a kaydedilir/geri yüklenir),
  switch açılınca tarih gidiş tarihiyle ön dolu + ilk saat seçili; kart üstünde kapak
  fotoğrafı; DateField min=gidiş, max=dönüş; saat pill butonları; tarih boşsa
  `tour-date-error-*` ve `missingTourDate` gönderimi engelliyor; özet satırında
  "10 Aralık 2026 · 15:00" gösterimi. Tur bölümündeki "WhatsApp'tan belirliyoruz" metni kaldırıldı.
- Test: `backend/tests/test_tour_safari.py` 7/7 PASS (pytest 72/72), iteration_72 frontend %100 (8/8).

## 2026-06-06 · "Sadece pasaport ve fotoğraf" kolaylık mesajları
Kullanıcı isteği: "Sadece pasaport ve fotoğrafınızla vizenizi alıyoruz" ve "vizeniz çıkmadan
otel/uçak bileti almanıza gerek yok" gibi kolaylık ibareleri eklenmesi.
- `content.py REQUIRED_DOCUMENTS`: uçak bileti ve otel rezervasyonu `required: True` → **False**
  (sihirbazda zaten opsiyoneldi, sayfada "Zorunlu" yazması çelişkiydi); açıklamalar
  "vizeniz onaylanmadan almanıza gerek yok" diye yeniden yazıldı.
- `content.py FAQ`: yeni soru "Vize almadan uçak bileti ve otel rezervasyonu yapmam gerekiyor mu?".
  `visa_guides.py` içindeki aynı konudaki cevap da güncellendi.
- Ana sayfa hero: CTA'ların üstünde 3 yeşil kolaylık pili (`hero-simplicity-strip`).
  `ADVANTAGES` ilk iki kart değişti: "Sadece pasaport ve fotoğraf" + "Bilet ve otel şartı yok".
  Belgeler bölümü paragrafı güncellendi.
- `/gerekli-belgeler`: başlık açıklaması + "İki belgeyle vizeniz hazır" yeşil kutusu
  (`documents-simplicity-note`).
- `/basvuru` Adım 3: "Seyahat belgeleri (opsiyonel)" başlığı ve "vizeniz çıkmadan bilet/otel
  gerekmez" açıklaması. `/vize-tipleri` hariç tutulanlar listesine "(vize için zorunlu değildir)".
- Doğrulama: `/api/content/site` → ticket/hotel `required: false`, yeni SSS sorusu dönüyor;
  ana sayfa ve belgeler sayfası ekran görüntüleriyle kontrol edildi.

## 2026-06-06 · "Neden bizde kolay?" karşılaştırma bölümü
`components/EasyCompare.jsx` (yeni) ana sayfada Avantajlar ile Başvuru Süreci arasında
(`landing-easy-compare`). 8 satırlı 3 kolonlu tablo: Süreç · Dubai Vize Online (yeşil, tikli) ·
Klasik acente yöntemi (gri, çarpı). Satırlar: istenen belgeler, uçak bileti/otel şartı,
pasaportun nerede kaldığı, randevu/ofis, sonuç süresi, fiyat, başvuru takibi, seyahat ekstraları
(`compare-row-{key}`). Altta "Pasaportunuzla başlayın" CTA + hukuki güvenlik notu
("her acentenin süreci farklılık gösterebilir" — rakip ismi verilmiyor).
md altında satırlar kolon başlığı etiketleriyle dikey yığılır. Ekran görüntüsüyle doğrulandı (8/8 satır).

## 2026-06-06 · Hero'da "2 belgeyle vize" animasyonlu anlatımı
`components/VisaExplainer.jsx` (yeni) — gerçek video değil, Framer Motion ile çizilen 4 sahneli
(~5 sn/sahne, 20 sn döngü) anlatım paneli: 1) pasaport kimlik sayfası, 2) vesikalık fotoğraf,
3) yükleme + ödeme (bilet/otel şartı yok), 4) onaylı vize PDF'i e-postaya teslim.
Sol tarafta sahne başlığı/notu (`explainer-scene-title`), 4 segmentli ilerleme çizgisi
(`explainer-dot-{key}`, tıklanabilir) ve duraklat/oynat butonu (`explainer-toggle-button`);
sağ tarafta sahneye özel animasyonlu kart (tik pop, yükleme çubuğu, uçan PDF).
Hero'daki `HeroSlider` bu panelle değiştirildi; Dubai fotoğrafları sayfada kaybolmasın diye
slider "Seyahat Paketleri" öncesine ayrı bölüm olarak taşındı (`landing-gallery`).
Doğrulama: sahne 1→2 otomatik geçiş, segment tıklaması (sahne 3), duraklatınca sahnenin
sabit kalması ekran görüntüleriyle test edildi.

## 2026-06-06 · Anlatıma Türkçe seslendirme + "Kimler başvurabilir?" kartı kaldırıldı
- **Seslendirme**: `scripts/generate_narration.py` (tek seferlik) OpenAI TTS `tts-1-hd`,
  voice `coral` ile 4 Türkçe anlatım klibi üretip `frontend/public/audio/explainer/*.mp3`
  altına yazıyor (EMERGENT_LLM_KEY, emergentintegrations `OpenAITextToSpeech`).
  Klipler ~7.5-9 sn. `VisaExplainer` içine `<audio>` + "Sesli anlat / Ses açık" butonu
  (`explainer-sound-button`) eklendi: varsayılan KAPALI (tarayıcı autoplay politikası),
  ses açıkken sahne klip bittiğinde geçer (`onEnded`), sessizken 5 sn'de geçer;
  duraklat butonu sesi de durduruyor. Segment ilerleme süresi ses açıkken 8.5 sn.
  SINIR: OpenAI TTS sesleri İngilizce optimize; Türkçe okuyuş hafif aksanlı.
  Daha doğal Türkçe için ElevenLabs `eleven_multilingual_v2` + Türkçe yerel ses gerekir
  (kullanıcının ElevenLabs API anahtarı şart).
- Ana sayfa avantajlar ızgarasındaki **"Kimler başvurabilir?" kartı kullanıcı isteğiyle
  kaldırıldı** (bilgi /sss ve /vize-tipleri sayfalarında duruyor); ızgara 6 kart 3x2 oldu.
- Doğrulama: ses butonu → `currentSrc` passport.mp3, `paused:false`, süre 8.9 sn;
  duraklat → `paused:true`; tekrar kapatma çalışıyor (ekran görüntüsü + JS kontrolü).

## 2026-06-06 · Anlatım "görüntülü" hâle getirildi (Türk pasaportu)
Kullanıcı: "animasyon yapalım görüntülü" + "türk pasaportu olsun".
- `VisaExplainer` tamamen yeniden yazıldı: soyut kartlar yerine **gerçek görsellerle video
  hissi** — her sahne tam ekran fotoğraf + Ken Burns yakınlaşması (scale 1.02→1.12, sahne
  süresi kadar), çapraz geçiş, üstte koyu gradyan, üzerinde beyaz metinler ve cam (blur)
  kontroller. Oran: mobil 16/10, sm 16/9, lg 21/9 (hero'yu uzatmasın).
- Görseller Gemini 3.1 Flash Image ile üretildi ve `frontend/public/explainer/*.jpg`
  altına indirildi: passport (bordo **Türk pasaportu** telefonla çekiliyor),
  photo (vesikalık + Türk pasaportu), upload (dizüstünde yükleme), delivered
  (Burj Khalifa fonunda onaylı vize gösteren gezgin).
- Sahne süresi ses açıkken 8.5 sn (klip uzunluğu), sessizken 5 sn; ilerleme segmentleri
  ve Ken Burns süresi bu değere bağlı.
- Doğrulama: sahne 1 görseli 1264x848 yükleniyor, segment tıklaması sahne 4'e atlıyor,
  ses açılınca delivered.mp3 çalıyor (ekran görüntüsü + JS kontrolü).

## 2026-06-06 · Animasyonlu altyazı (CC) + ElevenLabs beklemede
- `VisaExplainer`: her sahneye `subtitle` metni eklendi; `Subtitle` bileşeni kelimeleri
  sahne süresine yayarak tek tek belirginleştiriyor (opacity 0.28→1, kelime başına
  sahne süresi / kelime sayısı gecikme). Koyu yarı saydam pill üzerinde beyaz metin.
  Varsayılan AÇIK; `explainer-captions-button` (CC) ile kapatılabilir.
  Doğrulama: altyazı metni okunuyor, CC kapatınca DOM'dan kalkıyor (ekran görüntüsü).
- **ElevenLabs bekliyor**: kullanıcı ses tercihini seçti (kadın, sıcak/samimi) ama API
  anahtarını bulamadı. Anahtar alındığında: `backend/.env` → `ELEVENLABS_API_KEY`,
  `pip install elevenlabs`, `scripts/generate_narration.py` benzeri bir script ile
  `client.text_to_speech.convert(text=..., voice_id=..., model_id="eleven_multilingual_v2")`
  ve Türkçe yerel bir ses (voice listesi `client.voices.get_all()` ile alınır) kullanılarak
  4 klip yeniden üretilecek. Mevcut OpenAI tts-1-hd/coral klipleri çalışmaya devam ediyor
  (hafif İngilizce aksanlı).

## 2026-06-06 · Ses düzeltmeleri (kullanıcı geri bildirimi)
Kullanıcı: "sesli anlatım bir defa olsun, durmadan tekrar ediyor; kadın çok hızlı konuşuyor
ve Türkçe aksanı çok kötü".
1. **Tek seferlik oynatma**: `onEnded` son sahnede `setSoundOn(false)` yapıyor; ses bir tur
   çalıp kapanıyor, görsel döngü sessiz devam ediyor (döngüsel tekrar bitti).
2. **Hız**: TTS `speed=1.0` → **0.85**.
3. **Aksan/telaffuz kök nedeni**: ilk üretimde anlatım metinleri ASCII yazılmıştı
   ("basvurunuzu", "gozluksuz") — model bunları yanlış okuyordu. Metinler **tam Türkçe
   karakterlerle** yeniden yazıldı (ç, ğ, ı, İ, ö, ş, ü) ve cümleler kısaltıldı; klipler
   yeniden üretildi (7.3-7.8 sn). VOICE_MS 8000.
   Kalan aksan OpenAI TTS'in yapısal sınırı — tam doğal Türkçe için ElevenLabs gerekiyor.
Doğrulama: delivered.mp3 7.3 sn çalıp bitiyor, buton "Sesli anlat"a dönüyor, 6 sn sonra
tekrar başlamıyor (JS kontrolü).

### İngilizce yazı temizliği + daha sıcak ses (2026-06-06)
Kullanıcı ekran görüntüsünde 3. sahnedeki dizüstü ekranında İngilizce "UPLOADING..." yazısı
ve 4. sahnede telefonda "DIGITAL VISA APPROVED" yazısı vardı.
- `upload.jpg` ve `delivered.jpg` yeniden üretildi (Gemini): ekranlarda **hiç yazı yok** —
  yükleme sahnesinde altın ilerleme halkası + belge ikonları, teslim sahnesinde telefonda
  yalnız yeşil onay tiki (Burj Khalifa fonunda Türk gezgin).
- Seslendirme `coral` → **`shimmer`**, hız 0.85 → **0.92** (kullanıcı: "daha sıcak ses tonu").

### ElevenLabs Türkçe seslendirme devrede (2026-06-06)
Kullanıcı ElevenLabs anahtarını paylaştı → `backend/.env` → `ELEVENLABS_API_KEY`.
- Anahtar ilk başta izinsiz oluşturulmuştu (`missing permission text_to_speech`);
  kullanıcı "Has access to all" yaptı. `voices_read` hâlâ kapalı, ses listesi API'den
  alınamıyor — voice ID'ler sabit kullanılıyor.
- Ücretsiz plan **library (topluluk) seslerini API'den kullanamıyor** (402
  `paid_plan_required`): Aria, Rachel, Charlotte çalışmıyor. Çalışan varsayılan kadın
  sesleri: Sarah, Laura, Alice, Lily, Jessica, **Matilda**.
- `scripts/generate_narration_eleven.py` (yeni): Matilda (`XrExE9yKIg1WjnnlVkGX`,
  sıcak/samimi), `eleven_multilingual_v2`, stability 0.5 / similarity 0.85 / style 0.2 /
  speed 0.95, mp3_44100_128. 4 klip `frontend/public/audio/explainer/*.mp3` üzerine yazıldı
  (~6.5 sn). `VOICE_MS` 6800 yapıldı. OpenAI TTS scripti (`generate_narration.py`) yedek
  olarak duruyor.
- Doğrulama: ses butonu → passport.mp3 6.5 sn çalıyor (JS kontrolü + ekran görüntüsü).

## 2026-06-06 · Anlatım çizgi film tarzına dönüştürüldü (yeni metin)
Kullanıcı: "resimler çok koyu, açık renk olsun zemin", "yazılar okunmuyor",
"aslında animasyon yapmak istiyorum çizgi film gibi" + yeni 9 cümlelik seslendirme metni.
- **6 sahne** (`intro, passport, photo, upload, track, cta`) — kullanıcının verdiği metin
  6 parçaya bölündü; sahne süreleri klip uzunluğuna göre ayrı ayrı tanımlı
  (`silentMs` / `voiceMs`, 4.4-12.1 sn). Toplam ~40 sn, badge "Çizgi anlatım · 40 saniye".
- **Görseller**: fotoğraf yerine Gemini ile üretilmiş **düz vektör çizgi film illüstrasyonları**
  (krem zemin, bakır/altın vurgu) — `frontend/public/explainer/{intro,passport,photo,upload,track,cta}.jpg`.
- **Yerleşim açık temaya çevrildi**: illüstrasyon sağda (sm+ %68 genişlik), soldan krem
  gradyan; tüm metinler koyu (foreground), altyazı beyaz yarı saydam pill üzerinde koyu metin
  → okunabilirlik sorunu çözüldü. Panel `bg-[hsl(var(--panel-2))]`, resim `object-right`,
  giriş animasyonu: hafif kayma (x) + Ken Burns.
- **Son sahnede CTA**: "Başvuruya başla" butonu (`explainer-cta-button`).
- **Ses**: yeni metin OpenAI TTS `tts-1-hd` / `shimmer` / speed 0.9 ile 6 klip olarak üretildi
  (`scripts/generate_narration.py` güncellendi). ElevenLabs Türk seslendirmecileri ücretsiz
  planda API'ye kapalı (sesi hesaba eklemek de işe yaramadı, 402); Starter planı alınırsa
  `scripts/generate_narration_eleven.py` ile Pelin Yıldız sesine geçilecek.
- Doğrulama: 3 sahne ekran görüntüsüyle kontrol edildi (metinler okunuyor), CTA butonu
  render ediliyor, ses açılınca cta.mp3 çalıyor.

### Ek istekler (2026-06-06)
- "Animasyonda Hintli kıyafet olmasın, UAE bayrağı ve uçak olsun": intro/track/cta çizimleri
  modern batı tarzı kıyafet (kot + bluz/blazer) + **BAE bayrağı + uçak** ile yeniden üretildi.
- "Seyahat sigortası ve eSIM'den de bahsedelim": **7. sahne `extras`** eklendi
  (`Wifi` ikonu, yeni çizim, 11.4 sn klip): "Dilerseniz seyahat sigortanızı ve Dubai
  eSIM'inizi de aynı başvuruya ekleyin...".
- "TÜRSAB onaylı acente" cümlesi: son sahne başlığı **"TÜRSAB onaylı acente güvencesiyle
  başvurun"**, altyazı/ses "Başvurunuzu TÜRSAB üyesi, A grubu seyahat acentesi güvencesiyle
  yapın..." (site zaten TÜRSAB üyeliğini beyan ediyor, `content.py COMPANY`).
  Badge "Çizgi anlatım · 55 saniye".
- "Sola doğru kayan yazılar (dubaivizeal.com gibi)": `HeroHeadline` geçişi 3D flip'ten
  **slider kaydırmasına** çevrildi — başlık x:120→0, çıkışta x:-120; alt metin x:90→0
  (80 ms gecikmeli), kaplar `overflow-hidden`. Doğrulama: 4.4 sn'de slogan 1→2 geçişi.
- "Ana promoya bilet ve otel şartı yok ekleyelim": `HeroHeadline` SLOGANS'a **ilk sırada**
  yeni promo eklendi — "Bilet ve otel şartı yok / sadece pasaport ve fotoğraf", alt yazısı
  "Vizeniz çıkmadan uçak bileti ve otel rezervasyonu yapmanıza gerek yok...".
  3. slogan alt metni de aynı mesajla güncellendi (4 slogan döngüde).
- Anlatım paneli etiketi: "Dubai vizenizi 55 saniyede nasıl alacağınızı anlatalım".

## 2026-06-06 · Hero banner slider + duyuru şeridi + flip geri döndü
- Kullanıcı "flipping'e geri dönelim" dedi → `HeroHeadline` geçişi tekrar 3D flip
  (rotateX -75→0, çıkış 70) + alt metin y kaymalı fade (80 ms gecikme).
- **`components/HeroBannerSlider.jsx` (yeni)**: navbar altında tam genişlikte, 5 slaytlı
  otomatik banner slider (translateX ile yatay kayma, 5 sn, hover'da durur, ok butonları
  `hero-banner-prev/next`, noktalar `hero-banner-dot-{i}`). Her slaytta koyu gradyan üzerine
  beyaz başlık + alt metin (vize süresi, 2 belge, ekspres, aile indirimi, eSIM/sigorta).
  Sayfa ortasındaki `landing-gallery` bölümü (eski `HeroSlider`) kaldırıldı; `HeroSlider.jsx`
  dosyası duruyor ama artık kullanılmıyor.
- **`components/AnnouncementTicker.jsx` (yeni)**: `SiteLayout` içinde navbar'ın ÜSTÜNDE,
  sola akan sonsuz duyuru şeridi (`ticker-track` CSS animasyonu, 34 sn linear infinite,
  hover'da durur, prefers-reduced-motion desteği). 6 madde: TÜRSAB üyesi A grubu acente,
  ekspres ~8 mesai saati, sadece pasaport+fotoğraf, bilet/otel şartı yok, eSIM+sigorta,
  pasaport sizde kalır. NOT: `site_settings.company.tursab_no` boş olduğu için şeritte
  belge numarası YAZILMIYOR (uydurma numara riski) — numara girildiğinde eklenebilir.
- **ElevenLabs Türk seslendirmeci hâlâ yapılamadı**: hesap ücretsiz planda,
  `paid_plan_required` (402) devam ediyor. Starter alınınca
  `python scripts/generate_narration_eleven.py` (VOICE_ID Pelin Yıldız) yeterli.
- Doğrulama: şerit ve slider görünür, slider 5.5 sn'de bir sonraki slayta kayıyor
  (x: 0 → -1920), 4. noktaya tıklama çalışıyor.
- **GERİ ALINDI**: kullanıcı "resim koyma, eskisi gibi sadece flipping yazılar olsun" dedi →
  `HeroBannerSlider` ana sayfadan kaldırıldı (dosya duruyor, istenirse tek satırla geri gelir).
  Hero yine sadece flip'li başlıklardan oluşuyor. Duyuru şeridi kalmaya devam ediyor.

## 2026-06-06 · Anında Ekspres Vize kademesi + navbar/şerit rötuşları
- **Yeni ek hizmet `instant_express`**: "Anında Ekspres Vize", **150 USD/kişi (7.420 ₺)**,
  "aynı gün içinde sonuç" (kullanıcı onayı). `content.py ADDONS` + EXTRA_SERVICES listesi,
  `models.py AddonsIn.instant_express`, `routes_public.processing_days` →
  "aynı gün içinde". `content._addon_lines()` içinde **iki ekspres kademesi birlikte
  ücretlendirilmiyor** (instant seçiliyse express düşürülür).
  `Apply.jsx` ek hizmet kartlarında karşılıklı kapanma + "En hızlı" etiketi + vurgulu çerçeve.
  Sihirbaz 2. adımda, /vize-tipleri ve /hizmetler sayfalarında otomatik listeleniyor.
- Seslendirme son sahnesi: "**Vizenizi Dubai Vize Online güvencesiyle alın.** TÜRSAB üyesi
  A grubu seyahat acentesiyiz..." (kullanıcı isteği: site adı geçsin) — klip yenilendi (11.5 sn).
- Navbar: **mavi flag-strip kaldırıldı** (yerine 1px border), logonun negatif margin'i geri
  alındı → logo sol kenarı kart/kapsayıcı hizasında; bayrak çifti `ml-7` ile logodan uzaklaştırıldı.
- Duyuru şeridi zemini koyu kahveden **açık kreme** (`--panel-2`) çevrildi, metin `--charcoal`.
- Test: iteration_73 frontend %100 (ek hizmet karşılıklı kapanma, özet tutarları 5.190→12.610,
  7 sahne, şerit, flip başlıklar, /vize-tipleri + /hizmetler regresyonu).

### Hero metni kullanıcı kopyasıyla güncellendi (2026-06-06)
- İlk flip slogan: "2 belgeyle / Dubai vizeniz hazır" (kullanıcı "Pasaportunuzu ve
  Fotoğrafınızı Yükleyin" satırının kaldırılmasını istedi), alt metin: "Başvurunuz için
  yalnızca pasaportunuzun kimlik sayfası ve vesikalık fotoğrafınız yeterlidir...".
- Hero yeşil pil şeridi → **Evrak kontrolü · Resmî başvuru işlemleri · Süreç takibi ve
  bilgilendirme**; altına kapanış cümlesi (`hero-closing-line`): "Siz sadece belgelerinizi
  yükleyin, vize sürecinizi biz yöneteceğiz."
- 4. slogan alt metni de bu mesajla güncellendi.

## 2026-06-06 · ElevenLabs Türk seslendirmeci DEVREDE
Kullanıcı Starter planına geçti → kütüphane sesleri API'den kullanılabiliyor (402 bitti).
- `scripts/generate_narration_eleven.py`: LINES 7 sahneye güncellendi (intro, passport, photo,
  upload, track, extras, cta — cta'da "Dubai Vize Online güvencesiyle" + TÜRSAB cümlesi),
  ses **Pelin Yıldız (`FvxJI7vwUDkTkEOO7nd7`, Türk, sıcak-samimi)**,
  `eleven_multilingual_v2`, stability 0.5 / similarity 0.85 / style 0.2 / **speed 0.92**.
- 7 klip `frontend/public/audio/explainer/*.mp3` üzerine yazıldı: intro 6.3 / passport 5.3 /
  photo 10.7 / upload 13.1 / track 14.3 / extras 14.0 / cta 13.2 sn.
  `VisaExplainer` içindeki `voiceMs` değerleri bu sürelere göre güncellendi.
- Not: anahtarda `user_read` izni yok (abonelik bilgisi API'den okunamıyor) ama TTS çalışıyor.
- Doğrulama: ses açıldığında intro.mp3 (6.3 sn) çalıyor, altyazı sesle senkron ilerliyor (3/12 kelime @1.9 sn).

## 2026-06-06 · Ses akıcılığı + tam senkron (BUG FIX, iteration_74 %100)
Kullanıcı: "ses tonlaması çok kötü, akıcı değil, duraksamalar var" + "konuşma, yazılar ve
animasyon ekranı aynı sırada ilerlemeli".
- **Kök neden (ses)**: ElevenLabs `VoiceSettings.speed` (0.85-0.92) konuşmayı yapay şekilde
  uzatıp kelime aralarında duraksama üretiyordu. → `speed=1.0`, `stability=0.65`,
  `similarity_boost=0.78`, `style=0.0` ile yeniden üretildi.
- Ses **Pelin Yıldız → İlknur Önal** (`xFsOR54lR471QiCvQ5re`) olarak değişti
  (kullanıcı Pelin'e "hayır" dedi). Karşılaştırma örnekleri
  `frontend/public/audio/samples/{pelin,ilknur,filiz}.mp3` altında duruyor.
- **Senkron**: `VisaExplainer` artık sahne süresini gerçek klip süresinden alıyor
  (`onLoadedMetadata` → `audioMs`; `sceneMs = soundOn ? audioMs || voiceMs : silentMs`).
  İlerleme segmenti motion key'ine `sceneMs` eklendi. Böylece konuşma + altyazı kelimeleri +
  ilerleme çubuğu + Ken Burns aynı anda bitiyor. Klipler: intro 5.3 / passport 4.3 /
  photo 9.2 / upload 11.5 / track 10.0 / extras 12.8 / cta 11.0 sn.
- **Test (testing_agent iteration_74, frontend %100)**: altyazı ilerlemesi %26→3/12,
  %51→5/12, %77→9/12 (±2 tolerans); sahne geçişleri klip bitimiyle örtüşüyor; tek seferlik
  oynatma (döngü yok); duraklat/CC/CTA çalışıyor.
- Ayrıca: `.section` dikey boşluğu `py-14 sm:py-20` → **`py-10 sm:py-14`** (kullanıcı
  "boşlukları azalt"), kapanış cümlesi "...vize sürecinizi biz **yönetelim**." olarak
  düzeltildi (hero alt metni + ana sayfa).

### Ek rötuşlar (2026-06-06)
- "TÜRSAB üyesi A grubu seyahat acentesi" → **"TÜRSAB üyesi A grubu seyahat acente
  güvencesi"** (duyuru şeridi, anlatım son sahnesi, seslendirme metinleri).
- Daha heyecanlı ton: ElevenLabs ayarları `stability 0.65→0.38`, `style 0.0→0.55`,
  similarity 0.80 (speed 1.0 korundu); 7 klip yeniden üretildi (intro 5.2 / passport 4.4 /
  photo 9.2 / upload 12.0 / track 10.7 / extras 12.1 / cta 10.7 sn) ve `voiceMs` güncellendi.
- **Ses varsayılan AÇIK**: `soundOn` başlangıçta `true`; tarayıcı otomatik oynatmayı
  engellerse ses açık kalıyor ve ilk kullanıcı etkileşiminde (pointerdown/keydown/touch/
  wheel/scroll — `{once:true}`) klip başlıyor. Doğrulama: buton "Ses açık" ile açılıyor,
  ilk tıklamadan sonra intro.mp3 çalıyor (currentTime 1.7 / duration 5.1).
- Navbar "Ekstra Hizmetler" menüsündeki tek "eSIM & Sigorta" kaydı **iki ayrı sayfaya**
  bölündü: **Dubai eSIM** (/esim, Smartphone) + **Dubai Seyahat Sigortası**
  (/seyahat-sigortasi, ShieldCheck). Altbilgide de "Dubai Seyahat Sigortası" adı kullanıldı.
  Doğrulama: menüden tıklama /seyahat-sigortasi sayfasını açıyor.

## 2026-06-06 · Profesyonel seslendirme senaryosu (tonlama planlı)
Kullanıcı yeni senaryo + yönetmen notu verdi (ilk %30 sıcak/sakin, orta bilgilendirici,
"uçak bileti gerekmez"de ses yükselsin, "2 iş günü"nde yavaşlasın, son 15 sn satış odaklı).
- `scripts/generate_narration_eleven.py` yeniden yazıldı: artık **sahne bazlı VoiceSettings**
  (stability/style/speed) + metin içine gömülü `<break time="0.3-0.5s" />` duraklamaları.
  intro 0.6/0.20/0.98 · passport 0.55/0.20/1.0 · photo 0.55/0.25/1.0 ·
  upload 0.45/**0.45**/1.0 (avantaj vurgusu) · track **0.65**/0.15/**0.95** (yavaş, güven) ·
  extras 0.45/0.50/1.0 · cta **0.35/0.65/1.02** (enerjik kapanış).
  Ses: İlknur Önal, `eleven_multilingual_v2`, similarity 0.8.
- 7 klip yenilendi: intro 7.7 / passport 5.8 / photo 10.1 / upload 11.9 / track 10.9 /
  extras 13.6 / cta 17.7 sn (toplam ~78 sn). `VisaExplainer` altyazıları senaryo metinleriyle,
  `voiceMs`/`silentMs` yeni sürelerle güncellendi; etiket "Dubai vizenizi **1 dakikada** nasıl
  alacağınızı anlatalım". Son sahne notu: "TÜRSAB üyesi A Grubu seyahat acentesi güvencesi ·
  Dubai sizi bekliyor". Duyuru şeridi metni de "A Grubu ... güvencesi" olarak hizalandı.
- Doğrulama: ilk etkileşimde intro.mp3 (7.7 sn) çalıyor, cta noktasına tıklayınca cta.mp3
  (17.6 sn) çalıyor, altyazılar yeni senaryo metniyle görünüyor.

## 2026-06-06 · Kod inceleme bulguları: TAMAMI FALSE POSITIVE (iteration_75)
Kullanıcının paylaştığı rapordaki 4 "kritik" bulgu doğrulandı ve **kod değişikliği
gerekmedi**; testing_agent ile regresyon doğrulaması yapıldı (backend %100, 65/65 pytest):
- `zami_rpa.py:90` "exec() güvenlik açığı" → satır `await asyncio.create_subprocess_exec(...)`;
  sabit argv ile playwright kurulumu. Projede hiçbir yerde `exec()`/`eval()` yok.
- "insurance_tasks ↔ routes_store döngüsel import" → `insurance_tasks.py:17` yalnızca `db`den
  import ediyor; `routes_store.py:575` importu fonksiyon gövdesinde (lazy).
  POST /api/orders (ins_8d) 200 → lazy import yolu gerçekten çalışıyor.
- "7 tanımsız değişken (F821)" → `ruff check --select F821` 0 hata; server import/başlatma temiz.
- "`is` ile literal karşılaştırma (F632)" → tüm kullanımlar `is None` / `is not None`;
  ruff F632/E711/E712 = 0.
- Not (testing_agent'tan): `zami_rpa` her ~10 dk "bundled chromium unavailable" WARNING
  yazıyor; çalışmayı etkilemiyor (fallback var), sadece log gürültüsü — istenirse log seviyesi
  düşürülebilir.

### Anlatım görselleri profesyonelleştirildi (2026-06-06)
- `extras.jpg`: oyuncak görünümlü çizim yerine **monoline (ince çizgi) kurumsal illüstrasyon**
  (telefon + eSIM sinyalleri, şemsiyeli kalkan, BAE bayrak detayı).
- `photo.jpg`: kullanıcı isteğiyle **erkek + kadın** iki vesikalık kartı, nötr cilt tonu
  (kırmızı yüz sorunu giderildi), izometrik çerçeveler + onay tikleri, üstü çizili gözlük/şapka.
  Eski dosyalar `*.old.jpg` olarak duruyor.

## 2026-06-06 · Eleven v3 sesi, mobil boşluk, log temizliği, eSIM tablosu (iteration_76)
- **Ses (BUG: "bilgisayar konuşması olduğu belli")**: ElevenLabs **`eleven_v3`** modeline
  geçildi (multilingual_v2 yerine; v3 Türkçe destekliyor ve metin içi **audio tag**'leri
  yorumluyor). `scripts/generate_narration_eleven.py` yeniden yazıldı: sahne bazlı etiketler
  `[warm][smiling]`, `[informative]`, `[emphatic]`, `[slowly][reassuring]`, `[excited]`,
  `[confident][premium]` + sahne bazlı stability/style. 7 klip: intro 6.9 / passport 6.6 /
  photo 8.6 / upload 9.7 / track 8.9 / extras 12.6 / cta 16.6 sn; `voiceMs` güncellendi.
  (Not: script artık `requests` ile REST çağırıyor, elevenlabs SDK'sı v3'ü desteklemiyordu.)
- **Mobil boşluk (BUG)**: `VisaExplainer` mobilde dikey yığın — metin `order-1`, illüstrasyon
  `order-2` (176px blok, `object-center`), gradyan yalnız `sm:` üstünde; `min-h` kaldırıldı,
  `sm:absolute` ile masaüstünde eski yan yana düzen korunuyor.
- **Log temizliği**: `zami_rpa.py` "bundled chromium unavailable" → `logger.warning` yerine
  `logger.info`.
- **eSIM sayfası**: yeni `components/EsimCompare.jsx` — `/api/products`'tan 4 eSIM paketini
  çekip **karşılaştırma tablosu** (veri, geçerlilik, hotspot ✓/–, BAE kapsaması, Türkiye
  numarası, kime uygun) + fiyatlar; mobilde yatay kaydırma. `Esim.jsx` adım metinleri
  detaylandırıldı ve **6 adımlık kurulum listesi** (`esim-setup-steps`) eklendi.
- **Ek düzeltme (testing_agent bulgusu)**: `server.py seed_products()` içinde
  `doc.pop("price_usd")` KeyError atıp her açılışta "startup db init failed: price_usd"
  hatası veriyor ve sonraki seed'leri engelliyordu → `doc.pop("price_usd", None)`.
  Artık açılışta "store products seeded (11)" ve hata yok.
- Test: iteration_76 → frontend %100, backend %95 (tek minör bulgu yukarıda düzeltildi).

## 2026-06-06 · Anlatım görselleri mobilde görünür + "Beni hatırla" (iteration_77)
- **BUG "anlatirken resimler gosterilmiyor"**: Kök neden mobil düzendi — illüstrasyon metnin
  ALTINDA (`order-2`, sabit `h-44`, `object-cover`) kaldığı için anlatım oynarken ekranda
  görünmüyor ve kırpılıyordu. Düzeltme (`VisaExplainer.jsx`): görsel katmanı mobilde
  `order-1 aspect-[3/2] w-full` ile **en üste** alındı ve `object-contain` yapıldı
  (kırpma yok); metin katmanı `order-2 p-6 pt-2`. Masaüstü düzeni (`sm:absolute … w-[68%]`,
  `sm:object-cover sm:object-right`) aynı kaldı. `decoding="async"` eklendi.
- **"Beni hatırla" (yeni)**: `AdminLogin.jsx` içine `Checkbox` (data-testid
  `admin-remember-checkbox`) — işaretliyse token **30 gün**, değilse 12 saat; e-posta
  `localStorage.dv_admin_remember_email` ile hatırlanıyor ve sayfa açılışında ön dolduruluyor,
  kutu ön işaretli geliyor. Backend: `models.AdminLogin.remember: bool = False`,
  `routes_admin.create_token(email, remember)`.
- Test: iteration_77 → frontend **%100** (6/6 madde); token süresi curl ile doğrulandı
  (30 gün / 12 saat).
- Bekleyen: Zami bookmarklet "Submit" yakalama (P2, 3. tekrar);
  `insurance_tasks.queue_policy_tasks` ve `emailer.send_email` karmaşıklık refaktörü (P2).

## 2026-06-06 · Zami "Gönder" butonu tespiti + mobil "Dinle" düğmesi
- **Zami submit yakalama (P2, 3. tekrar) çözüldü**: Eski kod yalnızca
  `button[type="submit"],input[type="submit"]` arıyordu; Zami portalındaki type'sız
  `<button onclick>`, `input[type=button][value=SAVE]`, `<a class=btn>` gibi butonları
  kaçırıyordu → `submit_selector` boş kalıyor, robot formu doldurup göndermiyordu.
  - `routes_zami.py`: yeni `SUBMIT_FINDER_JS` (hem `capture.js` hem `bookmarklet.js` içine
    enjekte ediliyor) — metin (insert/submit/save/kaydet/gönder/apply/onayla…) + tür +
    form içi olma puanlaması, cancel/iptal/search/logout gibi kelimeler dışlanıyor,
    görünürlük kontrolü var. Seçici üretimi: `#id` → `tag[name=…]` → `input[value=…]` →
    `tag:has-text("…")`.
  - Yakalama artık `submit_candidates` (ilk 6 aday: selector+metin+puan) de gönderiyor
    (`CaptureIn.submit_candidates`, capture kaydına yazılıyor).
  - `bookmarklet.js`: doldurma sonrası gönder butonu bulunup **turuncu çerçeveyle
    işaretleniyor**, panele **"Formu gönder"** düğmesi eklendi (onay soruyor, tıklama
    başarısızsa `form.submit()` fallback).
  - `zami_rpa.py`: yeni `SUBMIT_FALLBACK_SELECTORS`; artık `if not dry_run:` ile mapping
    seçicisi + 15 yedek seçici sırayla denenerek **her seferinde gönderim tetikleniyor**
    (eskiden mapping boşsa hiç göndermiyordu). Readiness'ta submit artık her zaman "ok".
  - Test: `backend/tests/test_submit_finder.py` — gerçek Chromium'da 6 buton varyantı
    (type=submit / input[type=button] / `<a class=btn>` / type'sız button + Cancel ayıklama /
    `div[role=button]` / hiç buton yok) hepsi doğru; RPA fallback tıklaması doğrulandı.
- **Mobil "Anlatımı dinle" düğmesi**: `VisaExplainer.jsx` — `playing` state (audio
  onPlay/onPause) ve `startNarration()`; illüstrasyonun hemen altında tam genişlikte
  `sm:hidden` büyük düğme (`explainer-listen-button`), anlatım çalarken gizleniyor.
  Doğrulandı: 390px'te düğme görünüyor, dokununca `intro.mp3` çalıyor, düğme kayboluyor.
- **WhatsApp**: altyapı hazır (`whatsapp.py`, `/admin/whatsapp`) ve `manual` modda; Meta
  Cloud API veya Twilio anahtarları kullanıcıdan gelince otomatik gönderim açılacak (bekliyor).

## 2026-06-06 · Seslendirme: tek ses, tek ton, hafif hızlı (kullanıcı notu)
- Kullanıcı yeni senaryo metnini verdi ("Başvurunuzu yapmak için…", "ödemenizi yapmanız
  yeterlidir", "yaptırmanıza da gerek yok", "sizin adınıza biz takip ediyoruz",
  "e-mail adresinize ve WhatsApp ile gönderilir") → hem TTS metinleri hem altyazılar
  (`VisaExplainer.jsx` SCENES.subtitle/note) güncellendi.
- **"tek kişi konuşsun"**: Eleven v3 + sahne bazlı stability/style + duygu etiketleri
  aynı seste farklı kişi hissi veriyordu. Çözüm: model `eleven_multilingual_v2`,
  **tüm sahnelerde tek VOICE_SETTINGS**, tüm `[warm]/[excited]` etiketleri kaldırıldı ve
  klipler arası süreklilik için **request stitching** (`previous_text`, `next_text`,
  `previous_request_ids`) eklendi.
- **"bir tık daha hızlı, doğal, robotik olmasın"**: `speed: 1.07`, `stability: 0.42`
  (monotonluk azalır), `style: 0.32`. Son süreler (voiceMs): intro 6610, passport 5230,
  photo 9300, upload 11160, track 10660, extras 12930, cta 15570 (toplam ~71 sn).
- Ses İlknur Önal (`ELEVENLABS_VOICE_ID=xFsOR54lR471QiCvQ5re`); tek komutla yenilenir:
  `python /app/scripts/generate_narration_eleven.py`.
- Doğrulandı: 3 sahnede klipler yeni sürelerle yükleniyor ve çalıyor, altyazılar senkron.

## Güvenlik denetimi (security_audit_agent, 2026-06-06) — SEC-001/002/003/004 DÜZELTİLDİ
(2026-06-09: SEC-003 dosya erişimi imzalı/süreli jetona geçti, JWT_SECRET yedeği kaldırıldı,
CORS allowlist'e alındı, Zami handoff jetonu 10 kullanımla sınırlandı — bkz. CHANGELOG 2026-06-09)
- SEC-001 **HIGH**: `routes_account.py:206-219` e-posta + soyad ile müşteri hesabına giriş
  → hesap devralma; OTP'ye geçilmeli + rate limit.
- SEC-002 **HIGH**: `routes_zami.py` bookmarklet `box.innerHTML` içine yolcu adı/etiketi
  kaçışsız yazılıyor → Zami portal oturumunda stored XSS; HTML escape + isim karakter kısıtı.
- SEC-003 MEDIUM: `/api/files/{file_id}` kimlik doğrulaması yok; Zami handoff token'ı
  tek kullanımlık değil (45 dk tekrar kullanılabilir).
- SEC-004 MEDIUM: `/photo/check`, `/passport/read` (LLM maliyeti) ve
  `/account/request-code` (e-posta bombardımanı) rate limit yok; OTP düz metin saklanıyor.
- P3: CORS her origin'i yansıtıyor (`server.py:304-310`), e-postalarda kaçışsız kullanıcı
  girdisi, `JWT_SECRET` fallback `dv-dev-secret`, admin login sabit-zaman karşılaştırma yok.

## 2026-06-06 · Anlatım görselleri: Türk pasaportu + yan yana vesikalıklar
- `public/explainer/passport.jpg`: bordo **Türk pasaportu** (altın hilal-yıldız amblemi),
  kimlik sayfası ve telefonla fotoğraflama; `photo.jpg`: iki vesikalık **yan yana, aynı
  hizada** (çapraz/eğik değil) + onay tikleri ve üstü çizili gözlük/şapka ikonları.
  Önceki dosyalar `*.prev.jpg` olarak yedekte. Alt metinler güncellendi.

## 2026-06-06 · E-posta şablonu logo + tablo, anlatım panelinde çakışma düzeltmesi
- **E-posta (`emailer.py`)**: `_wrap` başlığındaki lacivert metin bloğu yerine gerçek
  **logo görseli** (`{PUBLIC_SITE_URL}/brand/logo-horizontal-gold-palm.png`, krem zemin +
  altın 4px şerit) kullanılıyor; `_row` artık **çerçeveli tablo satırı** (etiket hücresi
  krem `#FDF8F0`, kenarlık `#EADFCB`). Tüm şablonlarda lacivert/gri palet logo renklerine
  çevrildi (`#3E2A14` metin, `#8A7355` etiket, `#F7EEDF` sayfa zemini). Altbilgiye
  "TÜRSAB üyesi A Grubu seyahat acentesi" satırı eklendi. 9 şablon render testiyle
  doğrulandı + tarayıcıda görsel kontrol.
- **Anlatım paneli (`VisaExplainer.jsx`)**: Masaüstünde görsel `absolute right-0 w-[68%]`
  olduğu için metin/altyazı görselin üstüne biniyor ve `object-cover` çanta/ayakkabıyı
  kırpıyordu. Panel artık **2 kolonlu grid** (`sm:grid-cols-[54%_46%]`): metin solda,
  görsel sağda kendi kolonunda, `object-contain` ile **tam görünür**; gradyan katman
  kaldırıldı, zoom efekti 1.02'ye indirildi. Doğrulandı: altyazı ile görsel kutuları
  artık kesişmiyor (x: 486+479 < 996).
- Düzeltme (kullanıcı: "resimler daha önceki gibi olsun, ayakkabı ve bavul tam görünsün"):
  görsel yine büyük ve sağda (%52 kolon, `sm:p-5` ile yumuşak çerçeve), `object-contain`
  olduğu için illüstrasyonun tamamı (bavul + ayakkabı) görünüyor; metin kolonu %48,
  çakışma ölçümle 0. Gradyan katman kaldırıldı (kliplerin krem tonları farklı olduğu için
  dikey dikiş izi yapıyordu; artık çerçeveli kart görünümü).

## 2026-06-06 · Anlatım: boşluk azaltma, pasaport yazısı, uçak/otel sahnesi
- Kullanıcı a şıkkını seçti: görsel yine kenardan kenara (%68, `object-cover object-right`,
  gradyanlı) — çerçeveli kart kaldırıldı. Animasyon 961860d ile birebir aynı.
- **Boşluklar ~%50 azaltıldı**: `sm:min-h` 400→320, `sm:p-9`→`sm:p-6`, `sm:gap-6`→`gap-4`,
  mobil `p-6`→`p-5`, altyazı `mt-4 max-w-xl`→`mt-3 max-w-md`, kontroller `mt-5`→`mt-4`.
  Panel yüksekliği 430px → 349-373px.
- **passport.jpg yenilendi**: kapakta okunur şekilde **"TÜRKİYE CUMHURİYETİ"** ve
  **"PASAPORT"** yazıyor (altın, hilal-yıldız amblemiyle).
- **upload.jpg yenilendi**: uçak bileti + otel binası, ikisi de üstü çizili ve yasak
  işaretli, altında **"GEREK YOK"** yazısı; yanda onaylı belge kartı.
- **Vesikalık sahnesinde çakışma bitti**: metin kolonu `sm:w-[50%]` + altyazı `max-w-md`;
  ölçüm: altyazı 682'de bitiyor, portreler 720'de başlıyor.

## 2026-06-06 · Seslendirme telaffuz/tempo + pasaport görseli (son tur)
- **"Dubai" uzun a ile**: TTS metinlerinde `Dubai` → **`Dubaai`** (yalnızca seslendirme
  metni; altyazılarda doğru yazım "Dubai" kalıyor).
- **Tempo**: kullanıcı önce %30 hızlandırma istedi → `speed: 1.2` (toplam 49 sn, fazla
  hızlı bulundu) → ardından %30 yavaşlatma → **`speed: 1.0`** (doğal tempo, toplam ~78 sn).
  voiceMs: 7210 / 6610 / 9770 / 11160 / 11310 / 14060 / 18420. Panel etiketi "kısaca
  anlatalım", mobil düğme "Anlatımı dinle · 1,5 dakika".
- **passport.jpg** son hâli: bordo kapakta **TÜRKİYE CUMHURİYETİ**, altında
  **REPUBLIC OF TÜRKİYE**, hilal-yıldız, **PASAPORT** ve altta **biyometrik çip simgesi**;
  sağda kimlik sayfası + telefon.
- **Kapanış sahnesi kurumsallaştırıldı**: `VisaExplainer.jsx` cta sahnesinde "Başvuruya
  başla" düğmesinin yanında **TÜRSAB güven mührü** (`/brand/tursab.png` + "TÜRSAB üyesi /
  A Grubu seyahat acentesi", `data-testid="explainer-tursab-seal"`) 0.35 sn gecikmeli
  yumuşak giriş animasyonuyla görünüyor. Masaüstü + mobilde doğrulandı.

## 2026-06-06 · Seslendirme: TEK PARÇA kayıt + erkek baritone ses (duraksama fixi)
- **Kök neden**: Anlatım 7 ayrı ElevenLabs isteğiyle üretiliyordu; her klip kendi
  tonlamasını sıfırdan kuruyor, klip başı/sonu sessizlikleri ve sahne geçişleri
  duraksama + robotik his yaratıyordu.
- **Çözüm**: `scripts/generate_narration_eleven.py` yeniden yazıldı — tüm senaryo
  **tek istekte** üretiliyor (`/with-timestamps`), çıktı `public/audio/explainer/full.mp3`
  + `full.json` (karakter zaman damgalarından hesaplanan sahne pencereleri).
  7 ayrı mp3 silindi.
- **Frontend (`VisaExplainer.jsx`)**: tek `<audio src="/audio/explainer/full.mp3">`;
  `full.json` mount'ta çekiliyor, sahne indeksi `onTimeUpdate` ile pencerelere göre
  belirleniyor, altyazı ilerlemesi sahne içi orana göre; noktalara tıklayınca
  `audio.currentTime = scene.start` ile o saniyeye atlıyor; bitince ses kapanıp görsel
  döngü devam ediyor. `audioMs` state'i kaldırıldı.
- **Ses değişti**: kullanıcı erkek + güven veren ton istedi → ElevenLabs kütüphanesine
  **"Mert - Turkish Baritone Man"** (`GkfwuvVxiSskQtPHXcbw`, professional/istanbul)
  eklendi ve varsayılan ses yapıldı. Ayarlar: `stability 0.6`, `style 0.0`
  (dokümana göre style yükseldikçe ses kararsızlaşır), `similarity 0.8`, `speed 1.0`.
- Süre: 73.6 sn. Sahne pencereleri: intro 0-7.66, passport -12.91, photo -22.51,
  upload -33.38, track -43.07, extras -56.56, cta -73.62.
- Doğrulandı: full.mp3 çalıyor, 15. saniyede vesikalık sahnesi, cta noktası 57.7 sn'ye
  atlıyor.
- **Ses denemeleri**: 4 Türk erkek sesi kütüphaneye eklendi ve aynı metinle ~10 sn'lik
  demolar üretildi → `public/audio/demo/{mert,tbm,faruk,goksel}.mp3` +
  `audio/demo/index.html` (dinleme sayfası, noindex). Kullanıcı seçim yapmadı, "en
  güvenilir olanı seç" talimatı gereği **TBM - Confident Narrator**
  (`K03P46eiU2GnWEx7dtcV`) varsayılan yapıldı; full.mp3 bu sesle yenilendi (68.6 sn).
  Sahneler: intro 0-6.41, passport -11.37, photo -20.52, upload -31.02, track -41.20,
  extras -53.20, cta -68.60. Doğrulandı (35. sn → takip sahnesi).
- **Kadın sesler de eklendi**: Selin (kendinden emin), Dilek (profesyonel), Sibel (olgun),
  Aslı (sıcak), Başak (sakin) kütüphaneye eklendi; İlknur/Filiz/Pelin ile birlikte
  8 kadın + 4 erkek = **12 demo** `public/audio/demo/*.mp3` ve dinleme sayfası
  `audio/demo/index.html` (numaralı, "şu an yayında" işaretli). Kullanıcı seçim yapacak;
  seçilen ses `scripts/generate_narration_eleven.py` içindeki VOICE_ID ile tek komutta
  tüm anlatıma uygulanır. Ses ID'leri: tbm K03P46eiU2GnWEx7dtcV, mert GkfwuvVxiSskQtPHXcbw,
  faruk 0j8BpPEUtfp9x9RLrMVB, goksel FrXe0VVv2EHm9zvR8Jra, selin 9nu9B4zyoRSUNfwDafvh,
  dilek ggNaO6NobK7mzVacuMYD, sibel qLdPxFtPuffoxx5gieBJ, asli HZh2tWL1clJO95e2qMt2,
  basak 75LJWFYTuXJDmBjAFvfE, ilknur xFsOR54lR471QiCvQ5re, filiz 151qoe2jIbiWHaD2lbXE,
  pelin FvxJI7vwUDkTkEOO7nd7.
- **8 enerjik kadın ses daha** (kullanıcı: "daha çok kadın sesi, enerjik olsun, robotik
  olmasın"): damla A2XgcJ6lQVEFeIaIUyrc, melek xgYIZvUB5h2eFY3HUFNj,
  tomris bqaNYmxFgK1TN7CL95PZ, fusun cbqdgvVi3C6sgxIWpqIh, nil N0wraTTB0pquzsz3DLG8,
  lisa LYfSi2g3Frvxg50fRl91, aysel 1dZlYtnYGmIIA3kV1FuX, duygu MzfWWOj9g3sIKex1YFMV.
  Bu grup daha canlı ayarla üretildi (stability 0.4, style 0.15) — monotonluk azalır.
  Dinleme sayfasında toplam **20 demo** (13-20 = enerjik kadın grubu).
- **Hero flip başlıklarının altına ilerleme çizgileri** (`HeroHeadline.jsx`): anlatım
  panelindekiyle aynı stil, 5 segment, aktif segment 4,2 sn'de doluyor, tıklanınca o
  başlığa atlıyor (`data-testid="hero-progress"`, `hero-progress-dot-{i}`). Doğrulandı.

## 2026-06-06 · Anlatım paneli 2 kolon + görsel kırpma temizliği + Füsun sesi
- **Yerleşim**: panel `sm:grid-cols-[46%_54%]` — metin solda, görsel sağda kendi
  kolonunda **ortalanmış** (`object-contain object-center`, `sm:p-4`), mutlak konum ve
  gradyan kaldırıldı. Ölçüm: altyazı 655'te bitiyor, görsel 663'te başlıyor → çakışma yok.
  Uçak, uçak bileti, çanta/ayakkabı tamamen görünür.
- **Görsellerin kendi boşlukları kırpıldı**: `explainer/*.jpg` otomatik trim ile içerik
  sınırına göre kesildi (ör. intro 1264x848 → 607x721), orijinaller `*.orig.jpg` olarak
  saklandı. Böylece soldaki/sağdaki ölü boşluk gitti, çizim alanı doldu.
- **Ses seçimi: #16 Füsun Tuncer** (`cbqdgvVi3C6sgxIWpqIh`, enerjik reklam tonu).
  Ayarlar: stability 0.4, style 0.15, similarity 0.85, speed 1.0. full.mp3 72.5 sn;
  sahneler: intro 0-7.02, passport -12.11, photo -21.30, upload -32.12, track -43.26,
  extras -56.18, cta -72.47. Doğrulandı (25. sn → yükleme sahnesi).
- **2 kolon kaldırıldı, tek zemin**: kullanıcı isteğiyle grid kalktı; panel tekrar tek
  parça (`sm:block`), görsel sağda mutlak (`sm:w-[52%] sm:p-5`), metin `sm:w-[48%]`.
  Zemin farkını yaratan şey çizimlerin kendi krem arka planıydı → tüm çizimler
  **şeffaf PNG**'ye çevrildi (kenarlardan flood-fill ile arka plan silindi,
  `explainer/{key}.png`), böylece panelin krem zemini her yerde aynı görünüyor.
  Bileşen artık `.png` kullanıyor; `.jpg` ve `*.orig.jpg` yedek olarak duruyor.

## 2026-06-06 · Anlatım paneli son rötuşlar + Dubai sahnesi
- Panel içindeki "Sadece 2 belgeyle Dubai vizesi" başlığı kaldırıldı (üstte hero başlığı
  zaten var).
- Kapanış sahnesinde sıra değişti: **TÜRSAB mührü solda, "Başvuruya başla" düğmesi
  sağında**, ikisi tek satırda (mühür kompaktlaştırıldı: logo h-6, 9px metin;
  düğme `size="sm"`).
- **Tüm sahnelerde aynı boyut**: metin kolonu `sm:h-[430px]` sabit → panel yüksekliği her
  sahnede 432px, çizim kutusu ~531x346. İçerik üstten hizalı, ilerleme çizgileri+kontroller
  `mt-auto` ile en alta sabitlendi (sahne değişince yapı kaymıyor).
- **extras.png**: telefonun altında "DUBAI eSIM", kalkanın altında "SEYAHAT SAĞLIK
  SİGORTASI" etiketi ve kalkanın sağ üstünde bordo **"30.000 € TEMİNAT"** sticker'ı.
- **intro.png yeniden çizildi**: deve, çöl safari jeep'i, **Museum of the Future** (torus),
  **Burj Khalifa** ve **Burj Al Arab** (deve ile kadının arkasında), tam görünen palmiyeler,
  bayrak direği kadından uzun — ölçekler gerçekçi (kişi en küçük insan ölçeği).
- Tüm çizimler şeffaf PNG (arka plan flood-fill ile silinmiş), jpg'ler yedek.
- **Boşluklar kaldırıldı**: metin kolonu `sm:min-h-[430px] sm:justify-center` — içerik
  dikeyde ortalanıyor, altyazı ile kontroller arasındaki boşluk gitti; panel yüksekliği
  tüm sahnelerde 432px (ölçüldü: intro/photo/cta = 432).
- **Kenar yumuşatma**: tüm `explainer/*.png` kenarlarına %6 alpha feather uygulandı →
  dikdörtgen köşe izi yok, çizimler krem zemine karışıyor. Masaüstünde `sm:overflow-visible`
  ve zoom 1.03 → hiçbir ikon kırpılmıyor.
- **track.png yenilendi** (kullanıcı eski çizimi beğenmedi): kulaklıklı danışman yerine
  onaylı vize gösteren telefon + solda **zarf (e-mail)** ve sağda **WhatsApp** ikon
  madalyonları, kesikli teslim yayları, küçük BAE bayrağı. Metinle birebir uyumlu.
- **Yeni son sahne "specimen"**: `VisaExplainer.jsx` SCENES sonuna eklendi — başlık
  "Onaylanan vizeniz böyle görünür", not "e-Vize örneği · PDF olarak e-mail ve
  WhatsApp'ınıza gelir", `cta: true` (TÜRSAB mührü + Başvuruya başla düğmesi görünür).
  Görsel: `public/ornek-vize.jpg` → yuvarlak köşeli `explainer/specimen.png`.
  Seslendirmeye de yeni cümle eklendi ("İşte, onaylanan Dubaai vizeniz tam olarak böyle
  görünür..."); full.mp3 85.1 sn, specimen penceresi 75.88-85.14.
- **track.png v3**: e-posta ve WhatsApp madalyonları küçültüldü, telefon büyütüldü ve
  ekranında **vize örneği** (portre foto, BAE amblemi, metin satırları, barkod, yeşil onay
  tiki, specimen şeridi) görünüyor.
- track.png son hâli: `track.jpg`'den kod ile yeniden kurgulandı (arka plan silindi,
  telefon 503x825 olduğu gibi, e-posta/WhatsApp madalyonları %55 küçültülerek telefonun
  iki yanına yerleştirildi, kenar feather). Görsel işlem adımları PIL ile yapıldı;
  gerekirse `explainer/track.jpg` kaynağından tekrar üretilebilir.

## 2026-06-06 · Kod kalite raporu düzeltmeleri (backend)
Raporun 3 "kritik" bulgusu **doğrulanınca yanlış alarm çıktı**: `zami_rpa.py:90` `exec()`
değil `asyncio.create_subprocess_exec` (güvenli); pyflakes ile tanımsız değişken YOK;
`is` ile literal karşılaştırması (51 iddia) hiç yok. Gerçek olan ve düzeltilenler:
- **Dairesel bağımlılık çözüldü**: yeni `backend/store_catalog.py` — ürün katalogu
  (ESIM/INSURANCE/TOUR_PRODUCTS, DEFAULT_PRODUCTS, KIND_LABELS, MAX_QTY, `product_list()`)
  routes_store'dan çıkarıldı. `insurance_tasks`, `routes_admin`, `routes_public`, `server`
  artık katalogdan import ediyor; `insurance_tasks` içindeki 2 lazy import ve
  `routes_public` içindeki lazy `MAX_QTY` importu kaldırıldı. routes_store geriye dönük
  uyumluluk için re-export ediyor.
- **routes_public.py**: yinelenen `_parse_iso_date` tanımı (satır 764) silindi.
- **emailer.send_email** 3 yardımcıya bölündü: `_resend_params`, `_send_via_resend`,
  `_record_attempt` (davranış aynı: hata fırlatmaz, her denemeyi email_outbox'a yazar).
- **insurance_tasks.queue_policy_tasks** bölündü: `_build_policy_task`,
  `_notify_policy_pending` (idempotent davranış korundu).
- **Ek sertleştirme** (test ajanının bulgusu): `models.TravelerIn` içine `field_validator`
  eklendi — `birth_date` ve `passport_expiry` ISO tarih değilse 422 ile reddediliyor
  (önce "not-a-date" sessizce geçiyordu).
- `backend_test.py` gibi test dosyalarının karmaşıklığı bilinçli olarak elden geçirilmedi
  (test ajanı üretimi, ürün kodu değil).
- Test: iteration_78 → **17/17 backend regresyon testi PASS**
  (`backend/tests/test_refactor_regression.py`), ayrıca tüm tests/ paketi çalıştırıldı.

## 2026-06-08 · Uygunluk ön kontrolü kaldırıldı + esnek seyahat tarihi + Türkçe e-postalar
Kullanıcı isteği: "gidis ve gelis tarihlerine gore uygun sigorta ve esim leri bir sonraki
asamada gosterelim, Uygunluk ön kontrolü yapmayalim; planlanan seyahat tarihi henuz belli
degil seceneklerin sunalim" + "turkce olsun" (sipariş e-postası ekran görüntüsü).

Kullanıcı seçimleri (ask_human): checkbox + zaman aralığı birlikte; tarih belli değilse
paketler vize süresine göre listelenip seçilebilsin ("başlangıç tarihi siz bildirince
ayarlanır"); sağdaki "Ekstraları ekle" paneli tamamen kaldırılsın; listede sadece en uygun
2-3 paket + "tüm paketleri gör".

Yapılanlar (frontend):
- `components/EligibilityPreCheck.jsx` ve `components/ExtrasQuickAdd.jsx` **silindi**;
  Apply.jsx'ten importlar, `preCheckDone`, `applyPreCheck` kaldırıldı.
- `Apply.jsx` travel state'e `dates_unknown` + `travel_window` eklendi; `TRAVEL_WINDOWS`
  (this_month / 1_3_months / 3_plus_months / undecided) pill seçenekleri Adım 2'de.
  Checkbox işaretlenince tarih alanları gizlenir, aralık seçimi zorunlu olur; pasaport
  6 ay kuralı bugüne göre kontrol edilir (`validateStep`).
- Sigorta/eSIM listeleri kısa listeye indi: `shortlistFor()` → kapsamı yeten en kısa
  süreli max 3 paket (`coverDays = tripDays || visaCoverDays`); `show-all-insurance-button`
  / `show-all-esim-button` ile tüm liste, `hide-all-*` ile geri dönüş.
- Esnek tarihte `FlexibleDatesNote` + kart altı "başlangıç tarihi siz bildirince ayarlanır"
  notu; `extrasSelectable = travelDatesReady || datesFlexible` ile seçim açık.
- Özet adımında tarih yerine "Henüz belli değil · <aralık>" satırı.

Yapılanlar (backend):
- `models.TravelIn`: `arrival_date` / `departure_date` artık opsiyonel (default ""),
  `dates_unknown: bool`, `travel_window: str` eklendi.
- `routes_public._validate_travel_rules`: `dates_unknown` ise tarih kuralları atlanır,
  yaş ve pasaport kontrolleri bugüne göre yapılır; klasik akış aynen korunur.
- `emailer.py` tamamen Türkçe karakterli hâle getirildi: sipariş/başvuru/giriş kodu/taslak
  şablonları, `_payment_method_label` ("card" → "Kredi / Banka Kartı"), tutarlar `money()`
  ile Türkçe formatta (1.288,50 ₺), `_travel_date_rows` (tarih belli değilse aralık yazar).
- E-posta konuları ve WhatsApp şablonları Türkçeleştirildi (routes_store, routes_public,
  routes_admin, routes_payments, routes_account, visa_delivery, insurance_tasks).

Test: iteration_80 → backend 10/10 PASS (`backend/tests/test_iteration_80.py`; esnek tarih
quote/application, tur programı regresyonu, e-posta Türkçe kontrolü). Frontend: Playwright
ile uçtan uca doğrulandı (Adım 1 → 4): kısa liste 2 sigorta + 2 eSIM, "Tüm sigorta
paketlerini gör (4)" çalışıyor, esnek tarih notu ve seçim aktif.

### Kalan / backlog
- P0: Yönetici paneli OTP-only giriş (sadece e-posta + tek kullanımlık kod, aynı cihazda
  1 ay hatırlama) — hâlâ yapılmadı.
- P1: `ImportantNotice.jsx` bileşeni oluşturuldu ama hiçbir sayfaya bağlanmadı.
- P2: `email_outbox` kaydına gönderilen HTML gövdesi eklenmesi (admin panelde önizleme).

## 2026-06-08 (2) · Yönetici OTP girişi + Önemli Uyarı yerleşimi + E-posta önizleme
Kullanıcı seçimleri: şifreli giriş **tamamen kaldırılsın** (sadece OTP); uyarı kutusu
**başvuru (Vize adımı) + Gerekli Belgeler + SSS** sayfalarında görünsün; e-posta önizleme onaylandı.

Yapılanlar (backend):
- `POST /api/admin/login` **kaldırıldı** (404). Yerine:
  - `POST /api/admin/request-code` → 6 haneli kod (sha256+JWT_SECRET ile hashli, `code_plain`
    destek/test icin), 10 dk TTL; bilinmeyen e-postada da aynı jenerik yanıt (adres sızdırmaz);
    60 sn bekleme + saatte 5 talep sınırı (429).
  - `POST /api/admin/verify-code` → `compare_digest` ile doğrulama, 5 hatalı denemede 429,
    başarıda kod silinir ve **30 gün** geçerli JWT (`session_days: 30`) döner.
- `db.admin_login_codes` koleksiyonu; `models.AdminCodeRequest/AdminCodeVerify` (AdminLogin silindi).
- `emailer.admin_code_html` (kod + IP + 30 gün notu); `_record_attempt` artık HTML gövdesini
  `email_outbox`'a saklıyor (max 120 KB).
- `GET /api/admin/emails` → gövde hariç liste + `has_preview`; `GET /api/admin/emails/{id}` →
  tam HTML (yok ise 404).
- Test yardımcısı `backend/admin_test_token.py` (JWT ile jeton üretir; e-posta göndermez).
  `backend_test.py`, `regression_critical_tests.py`, `tests/test_insurance_*.py` bu yardımcıya geçti.

Yapılanlar (frontend):
- `pages/AdminLogin.jsx` iki adımlı OTP arayüzü (e-posta → 6 hane), 60 sn geri sayımlı "yeni kod",
  "e-postayı değiştir", şifre alanı yok. Jeton `localStorage.dv_admin_token` (30 gün).
- `components/AdminLayout.jsx > RequireAdmin`: süresi dolmuş/bozuk jetonu temizleyip girişe atar.
- `pages/AdminEmails.jsx`: satıra tıkla → `email-preview-dialog` (sandbox'lı iframe ile tam HTML),
  gövdesi olmayan eski kayıtlarda "Önizleme yok" notu.
- `components/ImportantNotice.jsx` renkleri `--status-warning` ile düzeltildi ve şu sayfalara
  eklendi: `Apply.jsx` (Vize adımı, compact), `Documents.jsx` (sayfa sonu), `Faq.jsx` (compact).

Test: iteration_81 → frontend 13/13 PASS, backend regresyon iteration_80'de 10/10.
Main agent ayrıca OTP güvenlik yollarını (jenerik yanıt, cooldown 429, yanlış kod, tekrar
kullanım, /admin/login 404, 30 gün exp) ve süresi dolmuş jeton temizliğini doğruladı.

### Kalan / backlog
- P1: `email_outbox` eski kayıtlarında gövde yok (yalnızca bu güncellemeden sonrası önizlenebilir).
- P2: `code_plain` alanı destek/test için saklanıyor; sıkı tehdit modelinde kaldırılabilir.
- P2: Tarihi belli olmayan başvurular için "tarihim belli oldu" hatırlatma e-postası.

## 2026-06-09 · Güvenlik sıkılaştırma + Başvuru formu UX (Adım 1-3) + Fotoğraf zemin denetimi
Ayrıntılı kayıt: `CHANGELOG.md` (2026-06-09), kalan işler: `ROADMAP.md`.

Özet:
- Müşteri girişi **yalnızca e-posta OTP**; `POST /api/account/login-lastname` kaldırıldı (404).
  Kod düz metin saklanmıyor; IP + e-posta bazlı hız sınırları eklendi (`backend/rate_limit.py`).
- Zami bookmarklet'inde HTML kaçışı (`dvoEsc`) → XSS kapatıldı. `/photo/check`, `/passport/read`,
  `/contact` uçlarına IP başına saatlik sınır.
- Başvuru Adım 1: Bireysel / Grup-Aile kartları, "Başvuru Türü" (Yetişkin/Çocuk + çocuk uyarısı),
  "Cep Telefonu (WhatsApp)" maskesi `+90 5XX XXX XX XX`, "Adınız Soyadınız" / "E-mail Adresi".
- Adım 2 Ek hizmetler: Seyahat Sağlık Sigortası + Dubai eSIM anahtarları (en uygun paketi seçer).
- Adım 3 Evraklar: ikon + ZORUNLU/OPSİYONEL etiketli, "Dosya Seç" butonlu kartlar.
- Vesikalık fotoğrafta arka plan artık deterministik ölçülüyor (beyaz/beyaza yakın zorunlu).

### 2026-06-09 (2) · Aile indirimi vitrini + Fotoğraf rehberi
- Başvuru özeti kartında canlı aile indirimi göstergesi (kademeler backend'den dinamik,
  "1 yolcu daha ekleyin → %10" / "%10 aktif · X ₺ tasarruf" + yolcu ekle butonu).
- Fotoğraf uyarısı alan yolcuya 1 doğru + 3 yanlış örnekli rehber
  (`public/photo-guide/*.jpg`, `components/PhotoGuide.jsx`).

---

## 2026-06-10 — Eklenen özellikler (özet; ayrıntı CHANGELOG.md)
- **Ziyaretçi analitiği**: `/admin/ziyaretciler` — ziyaretçinin IP'si, şehri, ülkesi, gezdiği
  sayfa ve ISP'si; ülke/şehir/sayfa top listeleri; 1/7/30/90 gün aralıkları. Takip
  `POST /api/track/visit` + ipwho.is (anahtarsız, `ip_geo` TTL önbellek).
- **Logolu banka hesapları**: 3 banka (İş Bankası, Garanti BBVA, Ziraat), TL+USD IBAN,
  kopyala butonu; `/vize-tipleri` ve ödeme adımı. IBAN'lar yer tutucu (P0).
- **İletişim sayfası**: konu seçimli form, kanal kartları, Google Maps haritası, yol tarifi.
  Adres: Parima Plaza Kat:12 Ofis:146, Zeytinburnu / İstanbul. Tel/WhatsApp +90 532 588 26 30.
- **İştirak notu** (yasal sayfalar + footer + Hakkımızda), şirket adları kalın; adlar
  kullanıcı isteğiyle "XXXX …" yer tutucu.
- **Menüde Vize Rehberi**: 7 rehber navbar dropdown'ında; nav linkleri telefonla aynı hizada.
- **/gelismeler** kapak görselli kartlar; **/seyahat-sigortasi** detaylı bilgi sayfası (satın alma yok).

## 2026-06-10 (2) — Mobil + iletişim güncellemeleri (özet)
- Mobil (iPhone/Samsung) başvuru ve ödeme akışı yatay kaydırma olmadan çalışıyor (iteration_89 %100).
- Telefon alanında `+90 5` sonrası hayalet maske; mobil menüde WhatsApp yeşili tel butonu.
- Dubai ofisi (Marina Plaza, Level 27 Unit 2705 · +971 50 867 26 30) iletişim sayfası, footer ve
  admin panelinde yönetilebilir.
- Mobil menüde tek "Başvuru Takip" girişi; "Hizmetler" ikonu servis çanı.

## 2026-06-10 · Sepet (ayrı satış) + anlatım/örnek vize düzeni + kur kaynağı
Detaylar CHANGELOG.md 2026-06-10 kaydında. Özet:
- **Sepet**: `/sepet` sayfası, navbar sepet ikonu, eSIM/sigorta kartlarında "Sepete ekle",
  %10 sigorta+eSIM indirimi, kart (Stripe) ve havale ödeme, siparişler "Başvurularım →
  Satın aldığım ek hizmetler" altında; vizesi olan müşteri `?basvuru=REF` ile hizmetleri
  başvurusuna bağlayabiliyor (backend `application_reference` doğrulaması).
- **Anlatım paneli**: 2 kolonlu grid (çakışma bitti), illüstrasyonlar kırpıldı/büyütüldü,
  geniş 4 sahne kare kompozisyona yeniden üretildi → tüm sahneler çerçeveyi dolduruyor.
- **Örnek vize**: önizleme sol metin kolonu genişliğinde, tıklayınca tam boy Dialog.
- **Logo + bayrak alanı**: tıklayınca ana sayfa + en üste kaydırma.
- **Fiyat sekmeleri** satırda ortalandı.
- **Kur**: Barchart sunucudan erişilemediği için Yahoo Finance `USDTRY=X` birincil kaynak
  (aynı bankalar arası kotasyon), doviz.com yedek.
- Test: iteration_94 backend %100 + frontend %100 (0 açık bulgu).

## 2026-06-10 (2. tur) · Turlar, hazır paket, sepet hatırlatma
- `/dubai-turlari` sayfası: çöl safarisi + VIP safari, tarih ve otelden alınış saati seçilerek
  sepete eklenir; sepette düzenlenebilir, sipariş detayında görünür.
- Ana sayfa hazır paket kartlarında "Sigorta + eSIM'i sepete ekle" (tek tık, %10 indirim);
  sepette "Bu pakette vize de var → başvurunu başlat" şeridi.
- Terk edilmiş sepet: `cart_snapshots` + 2. ve 24. saatte hatırlatma e-postası
  (`cart_reminders.py`, 15 dk'lık sweep), sipariş verilince kayıt kapanır.
- ⚠️ Resend gönderici domaini (`dubaivizeonline.com`) doğrulanmamış → e-postalar gitmiyor;
  `dubaivizehatti.com` doğrulanmalı (ROADMAP P0).

## 2026-06-11 · Admin WhatsApp AI paneli tamam (bkz. CHANGELOG 2026-06-11)
`/admin/whatsapp` artık 5 sekmeli WhatsApp AI yönetim paneli: **Belge Kuyruğu** (tedarikçi
PDF'lerinin AI eşleşmesi, ata/reddet), **Konuşmalar** (bot aç-kapa + manuel yanıt),
**Bot Ayarları** (Meta Cloud API kimlik bilgileri + webhook), **Simülatör** (mesaj ve belge
testi), **Sonuç Bildirimi** (eski manuel bildirim ekranı korundu).
Dosyalar: `pages/AdminWhatsApp.jsx` + `components/whatsapp/Wa{DocumentQueue,Conversations,
BotSettings,Simulator,ManualNotify}.jsx`. Backend değişmedi (`routes_whatsapp.py`).
Test: iteration_96 frontend %100. Bot hâlâ **simülasyon modunda** — Meta anahtarları
girilince canlıya geçer (ROADMAP P0).

## 2026-06-11 · Anlatım paneli, seslendirme ve e-posta (bkz. CHANGELOG 2026-06-11)
- Ana sayfa anlatımı artık **kapak karesiyle** açılıyor (hareket/ses yok, kullanıcı başlatır),
  bitince kapağa döner. Seslendirme ElevenLabs **eleven_v3** + duygu etiketleriyle üretiliyor;
  cümle araları sessizlik olarak ses dosyasına ekleniyor (pydub/ffmpeg) → toplam 67,4 sn.
  Tek komut: `python /app/scripts/generate_narration_eleven.py`.
- intro çizimi çöl zeminli, palmiyeler kenardan; `scripts/rebuild_explainer_png.py <sahne>`
  ile jpg'den saydam png üretiliyor.
- **Resend e-posta çalışıyor** (tam yetkili anahtar + doğrulanmış `dubaivizehatti.com`),
  ROADMAP P0'dan düşürüldü.
- E-posta şablonları premium künyeli (şirket unvanları, telefon, WhatsApp, e-posta, adresler,
  çalışma saatleri) ve taslak e-postaları başvuran adı + vize tipi gösteriyor.
- Anlatım metinleri ve intro çizimi 2026-06-11'de kullanıcı onayıyla son halini aldı;
  seslendirmeyi güncellemek için `python /app/scripts/generate_narration_eleven.py` yeterli
  (metin bu dosyada, altyazılar `VisaExplainer.jsx` içinde — ikisini birlikte güncelleyin).

## 2026-06-12 · Admin bekleyen iş sayacı + misafir sipariş takibi
- `GET /api/admin/stats` → `wa_pending_documents`, `wa_needs_human` alanları eklendi;
  `AdminLayout` menüde rozet gösteriyor (Mesajlar/WhatsApp), `AdminDashboard` üstünde
  "WhatsApp'ta bekleyen işlem var" bandı.
- Sipariş onay + teslim e-postalarında "Siparişimi takip et" butonu
  (`emailer.order_track_url`, `{SITE}/siparis/{kod}?email=`); `OrderStatus` `?email=` ile
  otomatik sorgulama; sepet altında son sipariş kısayolu (`dv_last_order_ref`).
- Test: manuel uçtan uca (gerçek sipariş + e-posta linki + ekran görüntüleri), pytest
  test_emailer 7/7. Test verileri silindi.

## Kullanıcıdan bekleyen (2026-06-12 itibarıyla)
- **Gerçek IBAN'lar** (havale kartlarında hâlâ "Örnek Bank A.Ş." / TR00… yer tutucu)
  → Admin → Banka Bilgileri.
- **WhatsApp canlı mod**: Meta App bilgileri (phone_number_id, access_token, app_secret,
  verify_token) → Admin → WhatsApp → Bot Ayarları. Şu an simülasyon modunda.
- Şirket unvanı / TÜRSAB belge no / Instagram-Google yorum linkleri.
- Not: yönetici giriş e-postası hâlâ `info@dubaivizeonline.com` (marka artık
  dubaivizehatti.com) — kullanıcı onayı bekliyor.

## 2026-06-12 · Tarih odaklı çapraz satış (Adım 1)
Sihirbaz Adım 1'de gidiş/dönüş tarihi soruluyor; hemen altında seyahat süresine göre
3 öneri kartı çıkıyor (sigorta · eSIM · çöl safarisi), tek tıkla eklenip kaldırılabiliyor.
Safari tarihi gidişin ertesi günü 15:00 olarak ön seçili, kişi sayısı yolcu sayısı kadar.
Tarih doğrulamaları Adım 1'e taşındı; Adım 2 yalnızca vize seçimi + tarih özeti gösteriyor.
Test: Playwright ile masaüstü + mobil uçtan uca doğrulandı (bkz. CHANGELOG 2026-06-12).

## 2026-09-06 · Vize karşılaştırma
`/vize-tipleri` sayfasında ve başvuru Adım 1'deki "Vizeleri karşılaştır" penceresinde
30/60 gün × tek/çok giriş vizeleri tek tabloda karşılaştırılıyor (süre, giriş hakkı, ücret,
işlem süresi, kimlere uygun). Tablodan seçim forma otomatik işleniyor.

## 2026-09-06 · E-posta güvenilirliği + sepette vize
- E-posta logosu artık inline (cid) gömülü; konu satırları "{başvuru no} başvuru nolu
  Dubai vize başvurunuz …" ile başlıyor.
- Hazır paket düğmesi vizeyi de sepete ekliyor; vize sepetteyken ödeme başvuru formunda
  alınıyor (`/basvuru?vize=…&paket=…&sepet=1`), form sepetteki ek hizmetleri devralıyor ve
  başvuru sonrası sepet boşalıyor.
- Vize karşılaştırma tablosunda çocuk ücreti satırı + aile indirimi dipnotu var.
- Doğrulama: iteration_100 test raporu (backend %100, frontend %100).

## 2026-09-06 · Aile Paketi
Ana sayfada "Aile Paketi" (2 yetişkin + 1 çocuk) tek tıkla sepete ekleniyor: 2 yetişkin
vizesi, 1 çocuk vizesi, 3 sigorta, 2 eSIM. Sepet artık birden fazla vize satırı tutuyor,
aile indirimini gösteriyor ve "Vize başvurusunu tamamla" ile forma 3 yolcuyu hazır açıyor.
Doğrulama: iteration_101 (backend %100 / frontend %100).

## 2026-09-06 · Yolcu sayısına göre paket + tam tatil
Aile Paketi kartında yetişkin/çocuk sayısı seçilebiliyor ve "Tam tatil" kutusuyla yolcu
sayısı kadar çöl safarisi ekleniyor; fiyat/içerik `GET /api/bundles/quote` ile anında
güncelleniyor. Kart, sepet ve başvuru formu aynı toplamı gösteriyor (tur tarihi otomatik
öneriliyor). Doğrulama: iteration_102 (%100/%100) + sonrasında UX düzeltmesi.

## 2026-06-06 · WhatsApp reklam videosu (MP4) TAMAMLANDI
Ana sayfa anlatımının video sürümü üretildi ve siteden indirilebilir:
- Dikey (Durum/Story): `/reklam/dubai-vize-hatti-reklam-dikey.mp4` · 1080x1920 · 70,9 sn · 2,6 MB
- Kare (sohbet/akış): `/reklam/dubai-vize-hatti-reklam-kare.mp4` · 1080x1080 · 70,9 sn · 2,1 MB
- İndirme/önizleme sayfası: `/reklam/` (noindex)
- Üretim komutu: `python /app/scripts/render_explainer_video.py [all|dikey|kare]`
  (ffmpeg gerekir; fork sonrası pod'da kurulu olmayabilir → `apt-get install -y ffmpeg`)
- Seslendirme/metin değişirse önce `scripts/generate_narration_eleven.py`, ardından bu script
  çalıştırılmalı (video full.mp3 + full.json'dan beslenir).
Sıradaki açık işler değişmedi: WhatsApp botunu canlıya alma (Meta kimlik bilgileri kullanıcıdan),
gerçek IBAN bilgileri, paylaşılabilir aile paketi linki (P2), İngilizce/global sürüm (P2).


## 2026-06-06 · Güvenlik denetimi turu 2 (deploy edilmiş uygulama) — TAMAMLANDI
Sonuç: **Critical/High bulgu yok** (CONDITIONAL PASS). 3 bulgu + 2 sıkılaştırma düzeltildi,
`testing_agent` iteration_103 ile bağımsız doğrulandı (backend 12/12, frontend %100):
- WhatsApp webhook artık **fail-closed** (imza yoksa/geçersizse 403) + dakikada 120 olay sınırı
- Yönetici OTP kodu düz metin saklanmıyor, e-posta konusunda da geçmiyor
- İşlemsel e-postalarda kullanıcı girdisi HTML olarak kaçırılıyor (`emailer.esc`)
- Takip sorgusunda kod taranabilirliği kapatıldı; WhatsApp bot durum sorgusunda
  telefon VEYA soyad doğrulaması zorunlu
Kalıcı regresyon paketi: `/app/backend/tests/test_security_audit_fixes.py` (12 test).

**ÖNEMLİ / CANLIYA ALMA ŞARTI**: WhatsApp botu canlıya alınırken Admin → WhatsApp → Bot Ayarları
ekranına Meta **App Secret** girilmesi artık zorunludur; girilmezse gelen webhook istekleri
güvenlik gereği reddedilir (panelde amber uyarı gösterilir).

Açık işler (değişmedi): Meta kimlik bilgileriyle WhatsApp canlıya alma (kullanıcı),
gerçek IBAN bilgileri, paylaşılabilir aile paketi linki (P2), İngilizce/global sürüm (P2).
Kabul edilen P3 riskler: `email_outbox` posta günlüğü OTP kodunu HTML gövdede tutar;
`.env` içindeki kullanılmayan `ADMIN_LOGIN_PASSWORD`; CORS alt alan adı regex'i.


## 2026-06-06 · Rakip karşılaştırması + Paket 1 (Güven & Fiyat) TAMAMLANDI
Rakip: dubaivize.com (Birtek Turizm). Analiz ve kullanıcı kararları CHANGELOG'da.
Tamamlanan (testing_agent iteration_104, frontend %100):
- Yeni SEO sayfası **`/dubai-vize-ucreti`** (fiyat tabloları, dahil/dahil değil, faktörler,
  ödeme-güvenlik, iptal-iade, 7 soruluk SSS + FAQPage JSON-LD, çapraz satış)
- `PaymentTrustStrip` (3D Secure + kart amblemleri + havale + kart saklanmaz)
- `ContentByline` (hazırlayan / son güncelleme / resmî kaynak + yasal acente uyarısı)
- Footer'da yasal uyarı bloğu, TÜRSAB/vergi/MERSİS placeholder "0000" değerleri kaldırıldı
- sitemap.xml + robots.txt alan adı dubaivizehatti.com olarak düzeltildi

### Sıradaki (kullanıcı onayı verilen sıra)
- **P0 · E-posta teslimi**: `info@dubaivizehatti.com` kutusu Google Workspace'te YOK
  (550-5.1.1). Kullanıcı ya kutuyu açacak ya da ADMIN_EMAIL değişecek. Ek: panelde
  "teslim edilemedi" uyarısı + Resend teslim durumu yoklama.
- **P1 · Paket 2 (İçerik & SEO)**: `/basvuru-rehberi` (7 adım ekran görüntülü), vize detay
  sayfalarına 58 gün giriş kuralı, kimler başvurabilir/başvuramaz, süre aşımı cezası
  (3.000 $ + günlük 150 $), tipe özel SSS, mobilde sabit fiyat+Başvur çubuğu,
  belge bazlı örnek görseller + vize tipine göre belge filtresi.
- **P1 · Paket 3 (Yabancı uyruklu başvuru)**: TC vatandaşı olmayanlara açılım
  (farklı fiyat kademesi + Türkiye oturum/çalışma kartı belgesi).
- **P1 · WhatsApp canlıya alma**: Meta App Secret ZORUNLU (imza doğrulaması fail-closed).
- **P2**: gerçek IBAN, paylaşılabilir aile paketi linki, iletişim formuna captcha,
  KVKK veri silme talebi akışı, İngilizce/global sürüm.
Reddedilen/parkedilen: SMS bildirimi (WhatsApp yeterli), sigortayı "zorunlu" diye
konumlandırma (yasal risk).


## 2026-06-09 · Fiyat sayfası tekilleştirildi + dinamik WhatsApp vitrini
- `/vize-tipleri` tek fiyat sayfası oldu ("Hizmet Bedelleri"); `/dubai-vize-ucreti`
  buraya 301 mantığıyla yönleniyor (`Navigate replace`), `VisaFees.jsx` silindi.
  Menü/footer/sitemap güncellendi. Ayrıntı: CHANGELOG 2026-06-09.
- Ana sayfa "Önce sorun" bölümündeki telefon maketi artık 4 farklı sohbeti (pasaport
  süresi, ekspres, bilet/otel şartı, vize teslimi) 6.8 sn'de döndürüyor; sohbette
  bilgileri bulanıklaştırılmış gerçekçi Türk pasaportu görseli var.
- Tailwind'e `spacing["4.5"]` eklendi (özel SVG'lerin dev boyutta render olma hatası).
- Açık kalan: admin e-postası `info@dubaivizehatti.com` Google Workspace'te yok →
  kullanıcı kutuyu açmalı veya alternatif adres vermeli (P0, kullanıcı aksiyonu).

## 2026-06-09 · Bu oturum (fork sonrası)
- **WhatsApp telefon maketi tam 4 sohbet** (kullanıcı isteği): 3. sırada eSIM + seyahat
  sigortası, 4. sırada aile/çocuklar. Detay: CHANGELOG 2026-06-09.
- **Pasaport görseli** artık yalnızca kimlik (bio) sayfası, tam görünür ve bilgileri
  bulanık: `frontend/public/chat/passport-bio.jpg`.
- **Kırılgan testler çözüldü**: kök neden test içinden `supervisorctl restart backend`
  çağrılmasıydı (paralel worker 502 alıyordu). Suite artık 271 passed / 3 skipped.
  IP sayacı tüketen 2 test `RUN_RATELIMIT_TESTS=1` ile ayrı çalıştırılır.

### Sıradaki açık işler (2026-06-09)
- **P0** WhatsApp botu canlıya alma: gerçek Meta Cloud API bilgileri Admin → WhatsApp →
  Ayarlar ekranından girilmeli (şu an `manual`/mock mod).
- **P1** Gerçek havale bilgileri (`site_settings.bank_transfer` hâlâ `TR00...` örnek IBAN).
- **P2** Paylaşılabilir aile paketi linki; İngilizce/USD global sürüm (ROADMAP).

## 2026-09-07 · Tamamliyo sigorta CANLI + ekspres sadeleştirme + DUBAI telefonu
Ayrıntılar CHANGELOG.md "2026-09-07 (4)" bölümünde. Özet:
- Tamamliyo Travel API canlı (`api.tamamliyo.com`, partner token .env'de): 4 poliçe (7/15/30/60
  gün), maliyet günlük çekilir, satış = maliyet × 2 (%100 marj). Ödeme bizde (cari tahsilat),
  poliçe API ile kesilir; **otomatik kesim panelden açılıp kapanır, varsayılan KAPALI**.
- Sigorta satın alan her kişi için TC kimlik no + doğum tarihi zorunlu (hem `/basvuru` Adım 4
  hem `/sepet`); sepette sigorta varsa gidiş tarihi de zorunlu (poliçe başlangıcı).
- Ekspres süresi her yerde "12 saat içinde"; "Anında Ekspres Vize" ürünü kaldırıldı; ekspres
  kartı vize özet kartı tasarımında (`AddonCard`); `/vize-tipleri` navbar genişliğinde
  (`.container-wide`).
- Ekstra hizmet önerileri Adım 1'den **Adım 4 (ödeme öncesi)** "Ekstra hizmetler" bloğuna taşındı.
- Telefon +90 533 743 82 24; son 5 hanenin altında D U B A I harfleri (`PhoneDubai`).
- Test: pytest 310 passed / 3 skipped; iteration_115 frontend 10/10.

## 2026-06-13 · Zami RPA sadeleştirmesi + kart genişliği doğrulandı
Ayrıntılar CHANGELOG.md "2026-06-13" bölümünde. Özet:
- `/vize-tipleri` hizmet bedeli kartları ile `/takip` kartları aynı genişlikte (1152 px,
  `.container-page`) — bekleyen doğrulama işi kapandı, kod değişikliği gerekmedi.
- `zami_rpa.fill_application` test edilebilir adımlara bölündü: `_FieldSetter` sınıfı +
  `_fill_precondition_error` / `traveler_selector` / `_fill_mapped_fields` /
  `_run_helper_clicks`. Davranış aynı, 143 → 90 satır, C901 uyarısı düştü.
- Test: yeni `tests/test_iteration_117_zami_fill_steps.py` 32/32; tam suit 351 passed / 3 skipped.

### Sıradaki açık işler (2026-06-13)
- **P0** WhatsApp botu canlıya alma (Meta Cloud API bilgileri kullanıcıdan bekleniyor).
- **P0** İlk sigorta poliçesini elle kesip otomatik kesimi açma.
- **P0** Gerçek IBAN'lar + şirket unvanı + TÜRSAB belge no (kullanıcıdan bekleniyor).
- **P2** Poliçe yenileme akışı, paylaşılabilir aile paketi linki, sepet 3 saat hatırlatması,
  İngilizce/USD global sürüm.

## 2026-09-08 · Tamamliyo canlı test: kod tarafı hazır, ödeme yetkisi bekleniyor
Ayrıntı: CHANGELOG.md "2026-09-08". Özet:
- Canlı API'de fiyat + teklif adımları çalışıyor (gerçek TCKN ile MERNIS geçti).
- 3 kod hatası bulundu ve düzeltildi: eksik `ulkeKodu`, eksik `odeme-onay parameters`,
  sağlayıcı hata mesajının panele ulaşmaması. 13 yeni regresyon testi.
- **P0 ENGEL (Tamamliyo tarafı)**: Partner hesabında ödeme yöntemi kapalı —
  "Bu teklif için açık tahsilat işlemi yapılamaz." Poliçe kesimi bu açılmadan mümkün değil.
  Tamamliyo'dan istenecek: açık tahsilat/cari yetkisi VEYA bakiye yüklemesi (odemeTipi=3)
  VEYA kart ile `odeme-yap` (odemeTipi=2) entegrasyonu.
- Test verisi: sipariş `SV-XFG87WZW`, teklifler 2135824 / 2135825 (ödenmedi, ücret yok).

## 2026-09-08 (2) · Ödeme yöntemi: Tamamliyo cari bakiyesi
- Kullanıcı kararı: cari/açık tahsilat şu an denenmeyecek. Poliçe ödemesi
  `odeme-yap` + `odemeTipi=3` (cari bakiye) ile yapılıyor; kart bilgisi hiçbir yerde
  tutulmuyor. Ayrıntı: CHANGELOG.md "2026-09-08 (2)".
- **P0 kalan tek iş**: Tamamliyo panelinden cari bakiye yüklenmesi. Yüklendiği an
  Admin → Sigorta Poliçeleri → "Poliçeyi kes" ile ilk poliçe kesilip PDF/e-posta/WhatsApp
  akışı doğrulanacak, sonra "Otomatik poliçe kesimi" anahtarı açılacak.
- Test verisi ve kimlik bilgileri veritabanından tamamen silindi (2026-09-08).

## 2026-09-08 (3-4) · Bakiye takibi, otomatik kuyruk ve vize e-postası
Ayrıntı: CHANGELOG.md "2026-09-08 (3)" ve "(4)". Özet:
- **Bakiye takibi**: Tamamliyo bakiye sorgu API'si yok; bakiye panelden girilir, kesilen
  poliçelerin maliyeti düşülür. Kritik seviyede admine e-posta + WhatsApp uyarısı gider.
- **Bakiye bekleyen poliçe kuyruğu**: bakiye yetmezse sipariş `waiting_balance` olur,
  bakiye yüklenince 15 dk içinde (veya yükleme anında) kendiliğinden kesilir.
- **Vize hazır e-postası**: GDRFA resmî sorgulama linki + 5 adımlı yönlendirme eklendi,
  vize PDF'i artık e-postaya ek olarak da gidiyor.
- Kalan P0: Tamamliyo paneline cari bakiye yüklenmesi (kullanıcı tarafında).

## 2026-09-08 (5) · GDRFA yönlendirmesi WhatsApp'ta da
- Vize onay mesajı ve vize belgesi WhatsApp caption'ı artık GDRFA sorgulama linki +
  5 adımlı yönlendirme içeriyor. Metin `content.py`'de tek kaynakta (e-posta + WhatsApp).
- **Düzeltme**: WhatsApp mesaj şablonu veritabanında test metni ("Test template …")
  olarak kalmıştı, varsayılan müşteri metnine geri alındı.

## 2026-09-08 (6) · Tek tık doğrulama sayfası
- GDRFA sayfası ASP.NET ViewState kullandığı için hazır dolu devlet bağlantısı
  üretilemiyor (canlı incelendi). Bunun yerine: dosya numarası vize PDF'inden otomatik
  okunuyor (`visa_file_number.py`, PyMuPDF) ve müşteriye imzalı `/vize-dogrula/{id}`
  sayfası gönderiliyor — File Number / First Name / Date of Birth tek dokunuşla kopyalanır.
- Panelde "GDRFA dosya numarası" alanı var; okunamayan belgelerde admin elle girer.
- Ayrıntı: CHANGELOG.md "2026-09-08 (6)".

## 2026-09-08 · SEO altyapısı (özet — detay CHANGELOG.md)
- Kanonik host tek: `SITE_URL` (`REACT_APP_SITE_URL`, varsayılan https://www.dubaivizehatti.com);
  `setMeta` canonical/OG/twitter + noindex desteği.
- Build sonrası statik ön-render: `frontend/scripts/prerender.js` + `seo-pages.js`
  (30 rota; tekil title/description/JSON-LD + gerçek metin; `build/sitemap.xml` üretimi).
  Build komutu: `craco build && node scripts/prerender.js`.
- JSON-LD: Article (image/publisher.logo/mainEntityOfPage), guide FAQ/Offer korumaları,
  ana sayfada TravelAgency + WebSite.
- SEO dostu başvuru adresleri: `/basvuru/pack-family/visa-30-single` (`applyPath`/`parseApplyPath`).
- Tüm sayfa başlıkları ≤60 karakter (7 vize rehberi seo_title'ı dahil).
- Başvuru formu PDF'i: saydam logo, "Dubai Vizesi Başvuru Detayları" başlığı, başvuru tarihi
  referans bandında, ortalanmış künye + marka/işletmeci cümlesi.

## 2026-09-08 · Kâr koruması (özet — detay CHANGELOG.md)
- `insurance_margin.py`: maliyet satış fiyatına ulaşırsa satış fiyatı otomatik `maliyet × 2`
  yapılır; marj %20 altında yalnız uyarı. Poliçe kesiminde karttan çekilen tutar satışı
  aşarsa uyarı + fiyat düzeltme (soğutma yok).
- Uyarı: yönetici e-postası + WhatsApp + panel bildirimi. Uçlar: `GET/POST
  /admin/insurance/margin[/check]`. Panel: Sigorta Poliçeleri → "Kâr koruması" kartı.
- `GET /admin/insurance/product-check?urun_id=220`: Tamamliyo ürün kodunun satışa açık olup
  olmadığını sorgular (panelde buton). 220 hâlâ kapalı ("Fiyat bulunamadı … 758").

## 2026-06-15 · Basvuru PDF basligi: logo hizalamasi
- Kullanici istegi: "logoyu biraz yukari al, Dubai Vizesi Basvuru Detaylari ile ayni hizada olsun".
- `application_pdf.py _header()`: logo hucresine ayri padding verildi
  (TOPPADDING 0 / BOTTOMPADDING 12) — VALIGN MIDDLE korunurken logo ~3.5pt yukari kaydi,
  "DUBAI" kelime markasi baslik metniyle ayni hizada. Baslik hucresi degismedi.
- Dogrulama: ornek PDF uretildi (`/tmp/test_form.pdf`) ve 200 dpi baslik kirpmasi gorsel
  olarak kontrol edildi; pytest PDF testleri 19/19 PASS.
- Bekleyen: canliya alma (kullanici "Save to Github" / deploy akisini kullanmali),
  gercek IBAN bilgileri, WhatsApp Meta canli anahtarlari, Tamamliyo cari bakiye + urun 220.

## 2026-06-15 (2) · Deployment probe + PDF QR kodu + etiket duzeltmeleri
- **Deployment blocker 1 (/health 404)**: Kubernetes liveness/readiness probu koksuz `GET /health`
  cagiriyor, yalnizca `/api/health` vardi. `server.py` icine `@app.get("/health")`
  (`platform_health`) eklendi. Dogrulama: `curl localhost:8001/health` -> {"status":"ok"}.
- **Deployment blocker 2 (.gitignore)**: `.env`, `.env.*`, `*.env` satirlari .gitignore icinden
  kaldirildi; deploy sirasinda backend/.env ve frontend/.env repoda bulunmali.
- **PDF QR kodu (yeni)**: `application_pdf.py` `_track_band()` — belgenin altinda krem bantta
  19mm QR + "Telefonunuzdan basvuru takibi" metni + takip kodu. QR adresi
  `{PUBLIC_SITE_URL}/takip?kod={reference_code}` (Track.jsx `kod` parametresini okuyor).
  ReportLab dahili `QrCodeWidget` kullanildi (ek bagimlilik yok). QR pyzbar ile okutularak
  dogrulandi; PDF hala tek sayfa.
- **Etiketler (kullanici istegi)**: Ad Soyad -> Adi Soyadi, Dogum t. -> Dogum Tarihi,
  Pasaport no -> Pasaport No, Gecerlilik -> Son Gecerlilik Tarihi, Vize -> Vize Turu.
  Yolcu tablosu kolon genislikleri yeniden dengelendi (6/40/22/24/26/36/26 mm = 180mm).
- pytest: 505 passed, 5 skipped.

## 2026-06-15 (3) · Standart sonuclanma suresi: "36 saatte"
- Kullanici istegi: vize kartlarindaki "ortalama 2 is gunu" ifadesi "36 saatte" olacak.
- `content.py` VISA_TYPES: visa_30_single / visa_60_single / visa_30_child `processing_days`
  -> "36 saatte" (cok girisli 3-5 is gunu, uzatma 2-4 is gunu degismedi). DB `visa_types`
  koleksiyonu `scripts/sync_visa_copy.py` ile senkronlandi (script artik processing_days de yaziyor).
- Ayni ifade tum musteri metinlerinde guncellendi: content.py ADVANTAGES + SSS,
  visa_guides.py (seo_description + SSS), VisaTypes.jsx (2 yer), EasyCompare.jsx,
  AskFirstSection.jsx, HeroBannerSlider.jsx, frontend/scripts/seo-pages.js + prerender.js.
- KALAN CELISKI: `VisaExplainer` takip sahnesi hem ekran metninde hem SESLENDIRMEDE
  "ortalama iki is gunu" diyor. Ses degisirse `scripts/generate_narration_eleven.py`
  yeniden calistirilmali (ElevenLabs kredisi harcar) — kullaniciya soruldu.
- Dogrulama: /api/visa-types 36 saatte donuyor, /vize-tipleri ekran goruntusu,
  pytest 507 passed / 3 skipped.

## 2026-06-15 (4) · Seslendirme 36 saat, garanti rozeti, PDF baslik/etiket
1. **Seslendirme yenilendi**: `scripts/generate_narration_eleven.py` track cumlesi
   "ortalama iki is gunu" -> "otuz alti saat"; tek parca full.mp3 yeniden uretildi
   (65.7 sn, eleven_v3). Sahne pencereleri full.json ile guncel; `VisaExplainer` voiceMs
   degerleri yeni pencerelere gore (7340/5070/8300/9880/9610/12160/13340) ve etiket
   "1,5 dakika" -> "1 dakika". Ekran metni + altyazi da "36 saat" oldu.
   Dogrulama: /tmp/full_align.json icinde "otuz alti saat icinde" gecti, tarayicida
   full.mp3 duration 65.7 okundu.
2. **36 saat garantisi rozeti (yeni)**: `components/GuaranteeBadge.jsx`
   (compact pill + kart varyanti). Hero altinda pill, /vize-tipleri fiyat tablosu altinda
   kart. Kosullar tek kaynakta: content.py SSS ("36 saat garantisi nasil isliyor?") +
   REFUND_TERMS yeni "36 saat garantisi" bolumu (/iade-kosullari).
   Taahhut: sure asilirsa ekspres bedeli iade, ekspres alinmadiysa ucretsiz ekspres sira;
   sure belgeler onaylanip basvuru mercilere iletildigi anda baslar, resmi tatil ve ek
   inceleme talepleri haric.
3. **PDF**: baslik iki satir + ortali ("Dubai Vizesi" / "Basvuru Detaylari", yeni
   `title_head` stili); yolcu tablosu "Son Gecerlilik Tarihi" -> "Gecerlilik Tarihi"
   (kolonlar 6/40/22/26/24/36/26 mm).
- pytest 505 passed / 5 skipped; ana sayfa + /vize-tipleri ekran goruntuleriyle dogrulandi.

## 2026-06-15 (5) · Mobil rotuslar + kart secimi + extras gorseli
1. **extras.png yer degistirildi**: kalkan (seyahat sagligi sigortasi) SOLA, telefon (eSIM)
   SAGA alindi — sahne basligi "Seyahat sigortasi ve Dubai eSIM" ile ayni sira.
   `scripts/swap_extras_sides.py`: gorsel yatay aynalanir, dort metin ogesi (iki etiket,
   rozet yazisi, cip ici "eSIM") genisletilmis maskeyle temizlenip blok halinde duz yazilir.
   Yedek: /tmp/extras.prev.png (orijinal frontend/public/explainer/extras.old.jpg da duruyor).
2. **Anlatim CTA butonu mobilde tam gorunuyor**: `VisaExplainer` cta satiri `flex-wrap`,
   TURSAB muhru `shrink-0` yerine `min-w-0` — buton alt satira sarkiyor, kesilmiyor.
3. **Paket kartlari mobilde ekrana sigiyor**: `HomeBundleStrip` kart genisligi
   `w-[87
## 2026-06-15 (5) · Mobil rotuslar + kart secimi + extras gorseli
1. **extras.png yer degistirildi**: kalkan (seyahat sagligi sigortasi) SOLA, telefon (eSIM)
   SAGA alindi — sahne basligi "Seyahat sigortasi ve Dubai eSIM" ile ayni sira.
   `scripts/swap_extras_sides.py`: gorsel yatay aynalanir, dort metin ogesi (iki etiket,
   rozet yazisi, cip ici "eSIM") genisletilmis maskeyle temizlenip blok halinde duz yazilir.
   Yedek: /tmp/extras.prev.png (extras.old.jpg da duruyor).
2. **Anlatim CTA butonu mobilde tam gorunuyor**: `VisaExplainer` cta satiri `flex-wrap`,
   TURSAB muhru `shrink-0` yerine `min-w-0` — buton alt satira sarkiyor, kesilmiyor.
3. **Paket kartlari mobilde ekrana sigiyor**: `HomeBundleStrip` kart genisligi
   `w-[87%]` -> `w-full` (lg`de grid ayni); kaydirma ipucu duruyor.
4. **Vize karti secimi (kullanici istegi)**: /vize-tipleri sayfasinda "en cok tercih edilen"
   kart kalici vurgulu kaliyordu. `VisaTypeCard` yeni `onHighlight` prop`u aldi (secim
   modundan ayri: yalnizca cerceve vurgular, CTA metni degismez); populer vurgusu artik
   `popularEmphasis = isPopular && !onHighlight`. `PricingTabs` `pickedId` state`i tutuyor;
   baslangicta populer kart vurgulu, tiklanan kart vurguyu aliyor, sekme degisince sifirlanir.
- Dogrulama: 390px viewport`ta CTA butonu tam (x=58 w=148), paket karti 358px genislikte
  (ekrana sigiyor), extras sahnesi ekran goruntusuyle kontrol edildi; /vize-tipleri
  tiklama oncesi/sonrasi computed border renkleri dogrulandi (populer -> notr,
  tiklanan -> primary).

## 2026-06-15 (6) · Guvenlik denetimi (security_audit_agent) — CONDITIONAL PASS
Detay: `memory/security_audit_2026-06-15.md`. Ozet:
- Onceki SEC-001..004 duzeltmeleri dogrulandi (OTP girisi, kacisli bookmarklet, imzali
  dosya jetonlari, hiz sinirlari, Stripe/WhatsApp webhook imzalari) — hepsi yerinde.
- Uygulanan yeni sertlestirmeler: `/api/applications/track` 60/5dk, `POST /api/uploads`
  150/60sn, `POST /api/admin/request-code` 30/saat (IP basina); `re.escape` ile
  routes_account (2 sorgu) ve routes_whatsapp arama (q 80 karaktere kirpilir).
- pytest 505 passed / 5 skipped (hiz sinirlari test paketini bozmuyor).
- ACIK P2 (kullanici karari): `backend/.env` icinde Tamamliyo kurumsal kart no + **CVV**
  ve tek `JWT_SECRET` duruyor; .env deploy icin repoda tutulmak zorunda. Secenekler:
  cari bakiye moduna (odemeTipi=3) gecmek / CVV'yi kaldirmak / anahtar rotasyonu.
- P3 kabul: CORS platform alt alanlarina acik (Bearer token kullanildigi icin etkisi dusuk),
  hiz sinirlari surec ici (cok replikada Redis gerekir).

## 2026-06-15 (7) · PDF logo, 36 saat geri sayimi, iletisim sayfasi, drawer bayraklari
1. **PDF logo buyutuldu**: `application_pdf._header` logo yuksekligi artik `2 * TITLE_LEADING`
   (38pt) ve genislik `ImageReader` ile oranli hesaplaniyor (~48mm). Olculdu: logo 51.5-89.5,
   baslik metni 54.9-88.9 → ust/alt hiza tam. Ozel padding hilesi kaldirildi (iki hucre de
   VALIGN MIDDLE). `TITLE_LEADING = 19` sabiti eklendi.
2. **36 saat geri sayimi (takip sayfasi)**:
   - Backend: `routes_public.build_guarantee_status(doc)` + `GUARANTEE_HOURS = 36`.
     Sure `zami_transferred_at` ya da `reviewing` durumunda baslar; bitis `approved`/`rejected`.
     Durumlar: pending / running / overdue / met / missed / closed (iptal).
     `GET /api/applications/track` yanitina `guarantee` blogu eklendi
     (start_at, deadline_at, finished_at, remaining_seconds, state, hours).
   - Frontend: yeni `components/GuaranteeCountdown.jsx` — saniye saniye isleyen sayac
     (saat:dakika:saniye), ilerleme cubugu, durum metinleri; Track.jsx`te zaman cizelgesinin
     ustunde. Canli dogrulandi (DV-PD753614: 30:44:24 -> saniye ilerliyor).
3. **Iletisim sayfasi yeniden duzenlendi** (kullanicinin gonderdigi referans duzen):
   ust kisimda buyuk **WhatsApp karti** (yesil zemin + yesil pill buton, telefon numarasi),
   altinda "Telefonla arayin / E-posta gonderin / Calisma saatleri" satirlari, sonra form
   (mobilde kanallar once: order-1/order-2; masaustunde form solda). Ofis kartlarina konum
   pini eklendi. Eski `ChannelCard` kaldirildi.
   NOT: grid ogelerine `min-w-0` verilmeden `truncate` yatay tasma yapiyordu — duzeltildi
   (scrollWidth 471 -> 390).
4. **Mobil menu bayraklari**: drawer basliginda `ml-auto` kaldirildi, bayraklar logonun
   yanina alindi ve `pr-12` ile kapatma (X) butonunun altinda kalmasi engellendi.

## 2026-06-15 (8) · Kod incelemesi (code_review_agent) — READY WITH FIXES
Bulgular ve yapilanlar:
- **MEDIUM (duzeltildi)**: `build_guarantee_status`, `reviewing` kaydi ve `zami_transferred_at`
  olmadan panelden dogrudan onaylanan basvurularda `state="pending"` donuyordu; musteri vizesi
  onaylanmisken "geri sayim baslamadi" mesajini goruyordu. Artik sonuc cikmissa (finished ya da
  status approved/rejected) `state="met"` donuyor. `GuaranteeCountdown` de `finished_at` bos
  gelirse alternatif metin gosteriyor.
- **LOW (duzeltildi)**: `routes_account.py` icindeki iki gereksiz fonksiyon-ici `import re`
  kaldirildi (modul seviyesinde zaten var).
- **LOW (kabul)**: hiz sinirlari surec ici; tek replikada gecerli (rate_limit.py docstring'inde
  belirtilmis).
- **Test bosluğu kapatildi**: `tests/test_iteration_127_guarantee_countdown.py` (11 test) —
  pending/running/overdue/met/missed/closed gecisleri, portal aktarimiyla baslama, ret'in de
  sonuc sayilmasi, baslangic kaydi olmayan onay, datetime/ISO girdi.
- pytest: 518 passed / 3 skipped. ESLint ve ruff (yeni kod) temiz.

## 2026-06-15 (9) · Admin → Sosyal Medya yonetimi (yeni ozellik)
Kullanici istegi: "admin panelinden sosyal medya sayfasi yonetme kismi yap, google review ve
instagram hesaplari ac". Instagram kullanici adi: **dubaivizehatti**.

### Backend
- Yeni `social_links.py`: 8 platform katalogu (instagram, google_review, facebook, tiktok,
  youtube, x, linkedin, threads) + `clean_url` (kullanici adi -> tam adres, yalnizca http(s)),
  `normalize_items` (tek kayit/platform, adres yoksa yayindan duser, siralama),
  `resolve_items` (panel icin her platforma bir satir; eski `company_info.instagram` /
  `google_review` degerlerinden geriye uyumlu doldurur), `public_links` (sitede gosterilecekler).
- `models.py`: `SocialLinkIn` + `SocialLinksIn`.
- `routes_admin.py`: `GET /api/admin/social` (katalog + satirlar),
  `PUT /api/admin/social` — **gonderilmeyen platformlar korunur** (merge), kayittan sonra
  `company_info.instagram/google_review` senkronlanir (eski tuketiciler bozulmaz).
- `routes_public.py`: `/api/content/site` yanitina `social_links` eklendi.
- `content.py`: COMPANY instagram -> `instagram.com/dubaivizehatti/`, google_review sorgusu
  "Dubai Vize Hattı yorumlar" oldu.
- `scripts/seed_social_links.py`: DB'ye Instagram + Google yorum baglantisini yazar
  (site_settings koleksiyonu — `db["site_settings"]`, `db.settings` DEGIL).

### Frontend
- Yeni `pages/AdminSocial.jsx` (route `/admin/sosyal-medya`, AdminLayout → Ayarlar → Sosyal Medya):
  her platform icin adres girisi, "Yayında" anahtari (adres yoksa kapali), 3 yerlesim onayi
  (sag alt buton / alt bilgi / iletisim sayfasi), sira, "Bağlantıyı test et" ve yayinda hesap
  sayaci. Tek "Kaydet" ile hepsi yazilir.
- Yeni `components/SocialIcons.jsx`: `SocialIcon` (lucide + Google/TikTok/Threads SVG) ve
  `SOCIAL_ACCENT` (platform renkleri).
- `SocialDock.jsx`, `Footer.jsx`, `pages/Contact.jsx` artik `contact.socialLinks` uzerinden
  dinamik render ediyor (yerlesim bayraklarina gore). `lib/contact.js` `socialLinks` tasiyor.
- `AdminCompany.jsx`: Instagram / Google yorum alanlari kaldirildi, yerine Sosyal Medya
  ekranina yonlendiren not eklendi (degerler silinmiyor).

### Test / dogrulama
- `tests/test_iteration_128_social_links.py` (13 test): kullanici adi cevrimi, javascript:
  adresinin reddi, bos adresin yayindan dusmesi, mukerrer/bilinmeyen platform, siralama,
  panel listesi, public filtreleme, jetonsuz erisim, kaydet + sitede gorunme + merge.
- Panelde canli dogrulandi (8 satir, TikTok kullanici adi girildi -> tam adres, sayac 2->3).
- Site: dock + altbilgi + iletisim sayfasi Instagram/Google baglantilarini gosteriyor.
- pytest: **531 passed / 3 skipped**.
- NOT: `test_iteration_116_refactor` backend hata logunda "NameError" arar; gelistirme
  sirasindaki gecici hot-reload hatasi logda kalirsa log truncate + `supervisorctl restart
  backend` gerekir (schedulers satirlari yeniden yazilsin).

## 2026-06-15 (10) · Google Yorumlari kapatildi + Admin → Instagram Takvimi (12 gonderi)
### Google Yorumlari
- Kullanici istegi ile `google_review` **kapatildi** (`enabled=false`): sitede dock/altbilgi/
  iletisim sayfasinda gorunmuyor, baglanti panelde saklaniyor (tek anahtarla geri acilir).
- `company_info.google_review` legacy alani bu yuzden bos donuyor — `test_iteration_48`
  bu davraniса gore guncellendi (bos = panelden kapatilmis).

### Instagram
- **Hesabi ben acamam / sifre uretemem** (Instagram kaydi kullanicinin telefonu + SMS
  dogrulamasiyla yapilir). Bunun yerine panelde kurulum rehberi + hazir icerik verildi.
- Yeni `backend/instagram_posts.py`: 12 gonderi plani (id, baslik, gorsel, Turkce aciklama,
  hashtag seti, gun/saat kaydirmasi) + `PROFILE` (kullanici adi `dubaivizehatti`, biyografi,
  kategori, 5 adimlik isletme hesabi kurulum rehberi) + `default_schedule(start)`.
  Tarihler 22 gune yayildi (her gonderi farkli gun, 12:00/13:00/18:00/19:00/20:00 saatleri).
- `routes_admin.py`: `GET /api/admin/instagram` (ilk cagirmada site_settings.instagram_calendar
  olarak seed eder), `PUT /api/admin/instagram` (tarih/metin/durum kaydeder; gorsel-baslik-
  hashtag plandan gelir, bilinmeyen id yoksayilir). `models.py`: InstagramPostIn/InstagramPlanIn.
- Yeni `pages/AdminInstagram.jsx` (route `/admin/instagram`, sidebar: Ayarlar → Instagram
  Takvimi): kurulum karti (biyografi kopyala), 12 gonderi karti — gorsel onizleme,
  `datetime-local` tarih, duzenlenebilir metin, hashtagler, "Metni kopyala",
  "Gorseli indir", "Paylasildi" anahtari, "Takvimi kaydet" ve bekleyen sayaci.
- **Gorseller**: 12 kare illustrasyon uretildi (Gemini 3.1 flash image), 4 tanesi yazi hatasi
  /ic cerceve nedeniyle yenilendi. Hamlar `frontend/public/instagram/raw/`.
  `scripts/brand_instagram_posts.py` PIL ile marka cercevesi ekliyor (1080x1350, 4:5):
  lacivert zemin, ust bantta `brand/logo-horizontal-gold.png` + BAE bayragi + "DUBAI",
  alt bantta `dubaivizehatti.com` + yesil WhatsApp pill `+90 538 483 82 24`.
  Cikti: `frontend/public/instagram/post-01..12.jpg`. Yazilar PIL ile basildigi icin
  Turkce karakter hatasi yok (Figtree.ttf).
- Testler: `test_iteration_129_instagram_calendar.py` (9 test: 12 gonderi, gorsellerin
  diskte olmasi, farkli/artan tarihler, metin+hashtag dolulugu, profil, GET/PUT, jetonsuz
  erisim, bilinmeyen id) + `test_iteration_128_social_links.py` merge testi guncellendi.
- pytest: **540 passed / 3 skipped**. Panelde canli dogrulandi (12 kart, kaydet -> bekleyen 12→11).
- Otomatik paylasim (Instagram Graph API) henuz YOK: hesap Isletme hesabina cevrilip bir
  Facebook Sayfasi'na baglandiktan sonra Meta erisim jetonu gelirse eklenecek.


## 2026-06-15 durum notu (fork)
### Bu turda tamamlananlar
1. **Instagram gönderileri profesyonelleştirildi** (kullanıcı isteği: "@dubaivizeal gibi").
   12 görsel gerçek Dubai fotoğrafı + kalın manşet düzeniyle yeniden üretildi
   (`/app/scripts/instagram_pro_posts.py`), metinler kısaltılıp sabit CTA eklendi.
2. **Tamamliyo ödemesi cari bakiyeye** çevrildi ve `.env`'deki kart + CVV verisi silindi
   (`TAMAMLIYO_PAYMENT_TYPE=3`, kart moduna geri dönüş env ile mümkün).
3. **Başvuru PDF'i**: hizmet bedeli tutarları Tutar kolonuyla hizalandı, QR bandı ortalandı
   ve metni güncellendi, footer'daki FZE cümlesi tek satıra alındı.

### Açık işler (öncelik sırası)
- P0 **Instagram hesabı**: hesap henüz açılmadı; kullanıcı kendi açacak (panelde kurulum
  adımları + 12 hazır gönderi bekliyor). Meta jetonu gelirse otomatik paylaşım yazılabilir.
- P0 **WhatsApp botu canlı mod**: Meta Developer App kimlikleri kullanıcı tarafından
  Admin → WhatsApp → Ayarlar ekranından girilecek (şu an MOCK).
- P1 **Gerçek IBAN'lar**: banka havalesi için placeholder IBAN'lar kullanıcıdan bekleniyor.
- P1 **Production deploy**: "Save to Github" + deploy kullanıcı tarafında.
- P2 Poliçe yenileme akışı, paylaşılabilir aile paketi linki, global İngilizce sürüm.

## 2026-06-16 (fork) · Teklif Linkleri (paylasilabilir teklif)
Kullanici bu turda yon vermedi ("best judgment"); backlog'daki P2 maddesi
**"paylasilabilir aile paketi linki"** secildi (kullanici eylemi gerektirmeyen, satis
sureclerine dogrudan katki saglayan is).

**Ne yapildi**: Yonetici Admin -> Musteri Iletisimi -> **Teklif Linkleri**
(`/admin/teklifler`) ekraninda yolcu/vize/ekspres/sigorta/eSIM/tur secip canli tutari
gorerek tek tikla bir teklif linki uretiyor (`/teklif/<token>`, varsayilan 14 gun gecerli).
Link WhatsApp paylasim metniyle hazir geliyor. Musteri linki acinca tutari ve fiyat
dokumunu goruyor; "Basvuruyu tamamla" dedigi anda ayni secimler basvuru formuna doluyor
(`/basvuru?teklif=<token>`) ve basvuru olustugunda teklif "basvuruya donustu" olarak
isaretleniyor (donusum takibi + goruntulenme sayaci).

Detay ve test sonuclari: CHANGELOG.md 2026-06-16.

### Bu turdan sonra bekleyen isler (oncelik sirasi)
- P0 **WhatsApp botu canli mod**: Meta Developer App kimlikleri (phone_number_id,
  access_token, app_secret, verify_token) Admin -> WhatsApp -> Bot Ayarlari'ndan girilecek.
- P0 **Instagram hesabi**: kullanici kendi acacak; panelde 12 hazir gonderi bekliyor.
- P1 **Gercek IBAN'lar**: `/vize-tipleri` ve odeme adiminda hala `TR00 0000 ...` yer tutucu.
- P1 **Production deploy**: "Save to Github" + deploy kullanici tarafinda.
- P2 Police/vize yenileme hatirlatmasi, global Ingilizce surum.
- P2 Teknik borc: `AdminOffers.jsx` (535 satir) ve `Apply.jsx` bilesenlere bolunebilir.

## 2026-06-17 durum notu (fork)
### Bu turda tamamlananlar
1. **Sigorta + eSIM icin detayli aciklamali 3 secenek karti** (basvuru sihirbazi 2. adim ve
   Odeme adimi) — yeni `ExtraOptions` bileseni, seyahat suresine gore rozet ve uygunluk
   cumlesi, eSIM adet secimi. Testing agent ile dogrulandi (iteration_135).
2. **"Degistir" / "Tarihleri duzenle" artik ayni sayfada** aciliyor (vize dropdown +
   tarih alanlari); 1. adima geri donus yok.
3. **Sadelestirme**: "Basvurmadan once okumaniz gerekenler" notu 2x2 kisa metin;
   sigorta/eSIM kartlarindan ozet paragraf kaldirildi.
4. **Iletisim sayfasi**: sol form karti sag kolonla alt hizada; Ofislerimiz'e Dubai karti
   eklendi (`company_info.dubai_address/dubai_phone` varsayilanlarla dolduruldu).
5. **SEO on-render parlamasi**: kod tarafi zaten duzeltilmis; canlidaki build eski oldugu
   icin sorun goruluyor. Inline stil ile ekstra saglamlastirma yapildi.

### Bekleyen isler (oncelik sirasi)
- P0 **Yeniden deploy**: on-render duzeltmesi ve bu turdaki tum degisiklikler icin
  "Save to Github" + deploy kullanici tarafinda.
- P0 **WhatsApp botu canli mod**: Meta Developer App kimlikleri Admin -> WhatsApp'tan.
- P1 **Gercek IBAN'lar**: hala `TR00 0000 ...` yer tutucu.
- P1 **Dubai ofis adresi dogrulama**: varsayilan adres kullanildi; gercek adres farkliysa
  Admin -> Sirket ekranindan guncellenmeli.
- P1 Teklif linkleri donusum raporu; P2 police yenileme, global Ingilizce surum.

## 2026-06-18 (fork) · Fiyat dokumu seffafligi: sigorta indirimi satiri + oran %10
Kullanici sorusu: "Vize 5.190 + Sigorta 450 iken toplam nasil 5.550 oluyor?"
Kok neden: vize ile birlikte alinan police icin uygulanan indirim (o zaman %20) toplamdan
dusuluyordu ama hicbir fiyat dokumunde satir olarak gosterilmiyordu.

Karar ve uygulama (detay: CHANGELOG.md 2026-06-18):
- Indirim orani %20 -> **%10** (content.py `WITH_VISA_INSURANCE_DISCOUNT`).
- Indirim satiri tum yuzeylerde gorunur: Apply ozeti + Adim 4, Track, Admin detay,
  basvuru PDF, makbuz PDF, e-posta ozeti.
- Sigorta kartlarinda rozet + ustu cizili liste fiyati (560 -> 504).
- Track fiyat dokumune magaza (sigorta/eSIM) satirlari eklendi (eksikti).
Durum: DONE · pytest 611 passed / 5 skipped · UI 3 yuzeyde ekran goruntusu ile dogrulandi.

Siradaki bekleyenler (degismedi): gercek IBAN'lar, WhatsApp canli mod (Meta kimlik
bilgileri), teklif linki donusum raporu, teklif geri sayimi, makbuz linki imzali kod,
gercek tur fotograflari, ATV +40 USD ek secenek.

## 2026-06-18 (fork, 2) · Basvuru sihirbazi UX turu
Bu oturumda kullanici geri bildirimleriyle yapilanlar (detay: CHANGELOG.md 2026-06-18 1-12):
- Fiyat seffafligi: gizli sigorta indirimi (%20 -> %10) tum dokumlerde satir olarak
  gorunur; ozet altinda "toplam X TL tasarruf ettiniz" vurgusu.
- Sihirbaz akisi: Adim 1 sadece iletisim + yolcu/pasaport; vize turu ve seyahat tarihleri
  Adim 2'ye tasindi. Stepper tam genislikte ve tiklanabilir (geri serbest, ileri tek adim).
- Form temizligi: "Diger Evraklar" alani, cocuk uyari kutusu ve fotograf uyari kutusu
  kaldirildi; vesikalik aciklamasina "gozluksuz ve sapkasiz" eklendi; WhatsApp bilgilendirme
  anahtari telefon alaninin sagina alindi.
- PDF: sorulmayan alanlar (Sehir/Medeni hal/Meslek) cikarildi, tutar kolonlari saga hizali.
- E-posta disiplini: taslak postasi yalnizca "Kaydet, sonra devam et" ile gider; 2 dakika
  hareketsizlikte "daha sonra devam eder misiniz?" dialogu.
- Gorsel: yuklenen dosyaya "Kaldir", yeni intro illustrasyonu (tam palmiye, saydam zemin),
  yeniden tasarlanan sik tarih secici.
Durum: DONE (her madde Playwright/curl/PDF render ile dogrulandi).

Bekleyen isler: gercek IBAN'lar, WhatsApp canli mod (Meta kimlik bilgileri), teklif linki
donusum raporu, teklif geri sayimi, makbuz linki imzali kod, gercek tur fotograflari,
ATV +40 USD ek secenek. Kullaniciya sorulan acik soru: 72 saatlik "yarim kalan basvuru"
hatirlatma e-postalari kalsin mi?

## 2026-06-18 (fork, 3) · Sayfa genisligi, Dubai ofisi, evrak ornekleri
Kullanici talepleriyle yapilanlar (detay: CHANGELOG.md ayni tarih, 16-21):
- Tarih alanlarinda takvim ikonu artik "gg.aa.yyyy" ile ayni hizada (hata metni ikonu
  asagi itmiyor).
- Tum sayfalar tek paylasilan genislikte: `.container-page` = 1344px (icerik 1296px),
  sol kenar logonun, sag kenar "Basvuru Yap" butonunun uzerinde bitiyor. Navbar 1560px.
- /iletisim'de Dubai (BAE) ofis karti + Google harita yayinda; DB alani bosalirsa
  `fix_placeholder_contact()` varsayilanla doldurur.
- Footer'daki "Vize Rehberi" link blogu kaldirildi (menude duruyor).
- Ana sayfa anlatim kartinda metin ve animasyon ortaya yanastirildi.
- /gerekli-belgeler: solda "Pasaport taramasi nasil olmali?" (1 dogru + 3 yanlis, gercek
  T.C. e-pasaport duzeninde ORNEK/SPECIMEN gorseller, vesikalikla ayni yuz), sagda
  "Vesikalik nasil olmali?" - iki kart esit yukseklikte.
Durum: DONE - testing agent regresyon taramasi %100 (iteration_136.json).

Bekleyen isler (degismedi): gercek IBAN'lar, WhatsApp canli mod (Meta kimlik bilgileri),
teklif linki donusum raporu, teklif geri sayimi, makbuz linki imzali kod, gercek tur
fotograflari, ATV +40 USD ek secenek.
