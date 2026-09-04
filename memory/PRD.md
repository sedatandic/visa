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
