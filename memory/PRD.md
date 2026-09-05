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

## Güvenlik denetimi (security_audit_agent, 2026-06-06) — HENÜZ DÜZELTİLMEDİ
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
