# CHANGELOG

> 2026-06-08 ve öncesi tüm geçmiş `PRD.md` içinde. Bu dosya 2026-06-09'dan itibaren tutulur.

## 2026-06-09 · Güvenlik sıkılaştırma + Başvuru formu UX + Fotoğraf zemin denetimi

### Güvenlik (kullanıcı onayı olmadan, güvenlik denetimi bulguları)
- **SEC-001 (HIGH) kapatıldı**: müşteri hesabı girişi artık yalnızca e-posta OTP.
  `POST /api/account/login-lastname` (e-posta + soyad) tamamen kaldırıldı → 404.
  `login_codes.code_plain` artık **saklanmıyor** (yalnız `code_hash`).
- **Yeni** `backend/rate_limit.py`: bellek içi kayan pencere sayacı (`check`, `client_ip`,
  `code_request_window`). `routes_admin._check_code_rate_limit` de bu yardımcıyı kullanıyor (DRY).
  - `/api/account/request-code`: e-posta başına 60 sn bekleme + saatte 5, IP başına saatte 15
  - `/api/account/verify-code`: IP başına saatte 30 deneme
  - `/api/photo/check`, `/api/passport/read`: IP başına saatte 40 (AI maliyet koruması)
  - `/api/contact`: IP başına saatte 8
- **SEC-002 (HIGH) kapatıldı**: `routes_zami.py` bookmarklet'inde `dvoEsc()` HTML kaçışı;
  belge etiketleri, referans kodu ve portal buton metni artık kaçışlanıyor (XSS).
- `GET /api/admin/login-codes` artık kodu göstermiyor (`requested_at` döner).
- Test dosyalarındaki kaldırılmış şifreli giriş fixture'ları `admin_test_token.admin_token()`
  ile değiştirildi (`test_iteration_48/79`, `test_refactor_regression`, `test_zami_otp_fix`);
  `ADMIN_LOGIN_PASSWORD` bağımlılığı ve hardcode şifre kaldırıldı. Serial pytest: 16 → 8 hata.

### Başvuru formu (kullanıcı istekleri)
- **Adım 1 başında** "Bireysel / Grup-Aile" kart seçimi (`application-type-individual|group`).
  Grup seçilince ikinci yetişkin yolcu otomatik eklenir + bilgilendirme kutusu
  (`group-application-note`); Bireysel'e dönünce yalnız ilk yolcu kalır.
- Telefonun yanında **"Başvuru Türü"** (`select-applicant-type`): Yetişkin (varsayılan) / Çocuk.
  Çocuk seçilirse `child-application-notice` uyarısı: 18 yaş altı tek başına başvuru yapamaz.
- Telefon alanı: etiket **"Cep Telefonu (WhatsApp)"** + WhatsApp ikonu
  (`components/WhatsAppIcon.jsx`, SocialDock ile paylaşılıyor), maske **`+90 5XX XXX XX XX`**,
  açılışta `+90 5`, yapıştırılan `0090/90/0` önekleri temizlenir; doğrulama 10 hane + 5 ile başlar.
  Alt not: "Başvurunuzla ilgili dönüş bu numaraya WhatsApp üzerinden yapılacaktır."
- Etiketler: "Ad Soyad" → **"Adınız Soyadınız"**, "E-posta" → **"E-mail Adresi"**.
- **Adım 2 Ek hizmetler**: `extra-switch-insurance` ve `extra-switch-esim` anahtarları.
  Açılınca en uygun (tarihe göre önerilen) paket otomatik seçilir, Özet adımında değiştirilebilir.
  Tarih seçilmemişken sigorta anahtarı uyarı verir + `extra-insurance-dates-hint` ipucu gösterilir.
- **Adım 3 Evraklar**: `FileDropzone` artık `icon` / `badge` ("required"|"optional") /
  `description` proplarını destekliyor; kartlarda ZORUNLU/OPSİYONEL etiketi, ikon ve
  "Dosya Seç" CTA'sı var. Seyahat evrakları 2 kolon: Uçak Bileti, Otel Rezervasyonu,
  Diğer Evraklar (tam genişlik).

### Vesikalık fotoğraf arka plan denetimi
- `passport_ai.background_report()`: kenar piksellerinden (üst bant + üst %65 yan bantlar)
  beyaza yakınlık oranı, ortalama parlaklık ve desen (std) ölçülür.
  Eşikler: beyaz oranı ≥ 0.55, ortalama parlaklık ≥ 185, std ≤ 42.
- `passport_ai.apply_background_report()`: ölçüm uygun değilse sonuç uyarıya çevrilir
  (`failed` içine `background_ok`, Türkçe açıklama, skor ≤ 0.45); ölçüm beyaz zemini
  doğrularsa LLM'in yanlış arka plan itirazı düşürülür (iteration_83 bulgusu).
- `/api/photo/check`: AI çağrısı başarısız olsa bile arka plan kontrolü çalışır
  (`reason: "background_only"`). Mesaj: "Arka plan beyaz degil. Vize icin duz beyaz zeminde
  cekilmis vesikalik gerekir."
- Doğrulama: koyu/kalabalık konferans fotoğrafı → `ok=false`, `background.ok=false`
  (white_ratio 0.24, lum 95.7); beyaz zeminli vesikalık → `background.ok=true`.

### Testler
- `test_reports/iteration_82.json`: güvenlik + eski dropdown/telefon → **tamamı PASS**.
- `test_reports/iteration_83.json`: fotoğraf zemin analizi, Adım 1 UI, regresyonlar → 6/7 PASS;
  bulunan tek hata (beyaz zeminde `background_ok` hâlâ `failed` içindeydi) düzeltildi ve
  ana ajan tarafından yeniden doğrulandı.
- Ana ajan doğrulaması (Playwright): Bireysel/Grup akışı, telefon maskesi, çocuk uyarısı,
  Adım 2 sigorta/eSIM anahtarları (491 ₺ / 450 ₺), Adım 3 evrak kartları (4 ZORUNLU/6 OPSİYONEL).
- `backend/tests/manual_account_otp_check.py`: müşteri OTP akışının uçtan uca betiği.
- Bilinen eski test hataları (bu turla ilgisiz, katalog verisi değişti): `test_visa_categories`,
  `test_tour_safari`, `test_iteration_48::TestVisaPrices`, `test_zami_otp_fix::test_visa_types`.
  Not: pytest **sıralı** çalıştırılmalı (`-n 0`), paralel koşu OTP hız sınırlarına takılır.

## 2026-06-09 (2) · Aile indirimi vitrini + Fotoğraf rehberi

### Aile indirimi vitrini (`components/FamilyDiscountMeter.jsx`)
- Başvuru özeti kartının en üstünde canlı gösterge: kademeler `/api/content/site` içindeki
  `family_discount_tiers` alanından dinamik okunur (şu an tek kademe: 2+ yolcu → %10).
- 1 yolcuda: "1 yolcu daha ekleyin, tüm vize bedellerinde %10 aile indirimi açılır" + ilerleme
  çubuğu + "Yolcu ekle ve indirimi aç" butonu (`family-discount-add-traveler`).
- Kademe sağlandığında: "%10 aktif" etiketi, "2 yolcu ile %10 indirim uygulanıyor · X ₺ tasarruf"
  (tasarruf tutarı `quote.family_discount`'tan gelir), kademe listesi yeşile döner.
- test-id'ler: `family-discount-meter`, `family-discount-active-badge|active-text`,
  `family-discount-progress-text`, `family-discount-tiers`, `family-discount-tier-{min}`.
- Not: `content.py > FAMILY_DISCOUNT_TIERS` içine yeni kademe eklenirse vitrin otomatik gösterir.

### Fotoğraf rehberi (`components/PhotoGuide.jsx`)
- Uyarı çıkan yolcunun altında "Doğru fotoğraf nasıl olmalı? Örneklere bak" bağlantısı
  (`traveler-{i}-photo-guide-toggle`) → 1 doğru + 3 yanlış örnek yan yana
  (`traveler-{i}-photo-guide`). Rehber, yolcu kartının tam genişliğinde açılır.
- Görseller Gemini ile üretilip 3:4 kırpılarak `frontend/public/photo-guide/` altına konuldu:
  `ok.jpg` (düz beyaz zemin), `bad-background.jpg` (kalabalık koyu ortam),
  `bad-sunglasses.jpg` (gözlük + şapka + sert gölge), `bad-selfie.jpg` (selfie açısı, bulanık).
- Doğrulama: koyu zeminli fotoğraf yüklendi → uyarı çıktı → rehber açıldı (Playwright).

## 2026-06-09 (3) · Kademeli aile indirimi, bilgi amaçlı paket sayfaları, ana sayfa kısaltma

### Kademeli aile indirimi
- `content.py`: `FAMILY_DISCOUNT_TIERS = [(2, 0.10), (4, 0.15)]`; `family_discount_rate()` artık
  **en yüksek uyan kademeyi** döndürüyor (önceden ilk eşleşeni dönüyordu → 4+ kişide %10 kalıyordu).
- Doğrulama (`/api/pricing/quote`): 1 kişi %0, 2-3 kişi %10, 4-5 kişi %15.
- Metinler güncellendi: `FAMILY_DISCOUNT_TEXT`, SSS cevabı, HeroBannerSlider, HeroHeadline.
- Özet kartındaki `FamilyDiscountMeter` kademeleri backend'den okuduğu için iki kademeyi
  otomatik listeler ("2+ yolcu %10", "4+ yolcu %15").

### Fotoğraf rehberi Gerekli Belgeler sayfasında
- `Documents.jsx` fotoğraf kuralları listesinin altına `PhotoGuide` eklendi
  (`documents-photo-guide`).

### eSIM ve Seyahat Sigortası sayfaları artık bilgi amaçlı
- Yeni `components/PlanShowcase.jsx`: paketleri (ad, özet, teminat listesi, fiyat, "en çok
  tercih edilen" etiketi) sadece listeler; adet seçici, sepet ve ödeme formu YOK.
- `components/StoreCheckout.jsx` **silindi** (artık referans yok). Satın alma yalnızca vize
  başvurusu akışından yapılır; sayfa altındaki CTA `/basvuru`'ya yönlendirir.
- Sayfa metinleri ve SEO başlıkları "Satın Al" yerine "Paketleri" olacak şekilde güncellendi;
  eSIM adım metni "Başvuruda paketi seçin" oldu.

### Ana sayfa uzunluğu (kullanıcı şikayeti: çok uzun)
- `body.scrollHeight` **8282px → 6767px** (1920x900'de 9.2 → 7.5 ekran).
- Kaldırılan/kısaltılan: "4 adımda Dubai vizesi" bölümü tamamen kaldırıldı (hero anlatımı +
  karşılaştırma tablosu ile tekrar ediyordu); Gerekli Belgeler bölümü 4 kolon kompakt kartlara
  indi (büyük görsel kaldırıldı); Avantajlar kartları tek satır ikon+metin düzenine geçti;
  karşılaştırma tablosu 8 satırdan 5 satıra indi ve satır yükseklikleri azaldı;
  `.section` dolgusu `py-10 sm:py-14` → `py-8 sm:py-12`; hero başlık/alt metin boşlukları azaldı.

### Yasal sayfalar hizalaması
- `LegalTerms.jsx` ve `Kvkk.jsx`: içerik `container-page max-w-3xl` (ortalanmış) yerine
  sol hizalı `max-w-3xl px-5 sm:px-8` sarmalayıcıya alındı → metinler üstteki başlık
  kartıyla aynı sol hizada başlıyor.

### Test — iteration_84 (2026-06-09)
Tüm senaryolar PASS, kritik/minor hata yok (`test_reports/iteration_84.json`,
`backend/tests/test_iteration_84.py` 12 test). Doğrulananlar: kademeli aile indirimi (1..5 yolcu),
`family_discount_tiers` içeriği, 4 rehber görselinin 200 dönmesi, 4 yolculuk başvuruda %15 indirim,
ana sayfa 6739px ve tüm bölümlerin/linklerin sağlam olması, /esim & /seyahat-sigortasi'nda satın
alma UI'ının bulunmaması, yasal sayfalarda h1 ile gövde sol hizasının birebir eşleşmesi (441px),
FamilyDiscountMeter'ın 2 yolcuda %10 / 5 yolcuda %15 göstermesi.

## 2026-06-10 — Ziyaretçi analitiği, banka hesapları, iletişim & içerik güncellemeleri

### Ziyaretçi takibi (yeni)
- `backend/visitors.py`: `client_ip()` (X-Forwarded-For / cf-connecting-ip zinciri, özel IP filtresi),
  `lookup_geo()` → ipwho.is (anahtarsız) + `ip_geo` koleksiyonunda 30 günlük TTL önbellek,
  `record_visit()` → `visits` koleksiyonu, `visit_summary()` (günlük seri, ülke/şehir/sayfa/referrer top listeleri).
- `POST /api/track/visit` (BackgroundTasks ile bloklamaz, bot UA'ları atlar) — `SiteLayout.jsx`
  her rota değişiminde çağırır, `/admin/*` hariç.
- `GET /api/admin/visits`, `GET /api/admin/visits/summary` (require_admin).
- Yeni sayfa `/admin/ziyaretciler` (`AdminVisitors.jsx`): 4 özet kartı, ülke/şehir/sayfa top listeleri,
  son 100 ziyaret tablosu (zaman, IP, şehir, ülke, sayfa, ISP), 1/7/30/90 gün sekmeleri, bot filtresi.

### Banka hesapları (logolu, katlanabilir)
- `content.py > BANK_TRANSFER` artık `banks[]` (İş Bankası, Garanti BBVA, Ziraat — her biri TRY+USD IBAN)
  ve `notes[]` içeriyor; logolar `frontend/public/brand/banks/*.png` (Wikimedia Commons).
- `components/BankAccounts.jsx`: accordion kart + IBAN kopyalama; `/vize-tipleri` sayfasına ve
  ödeme adımındaki `BankTransferInfo`'ya eklendi.
- `AdminBankTransfer.jsx`: banka/hesap/uyarı satırı ekleme-silme editörü (kaydetme `banks`'ı korur).
  `BankTransferIn` legacy `bank_name`/`iban` alanları opsiyonel yapıldı.

### İletişim sayfası
- `Contact.jsx` yenilendi: konu seçimli form, kanal kartları (telefon, WhatsApp, e-posta, saatler),
  başvuru takip CTA'sı, Google Maps gömülü harita + "Yol tarifi al".
- Şirket bilgileri güncellendi (DB `company_info` + `content.py` varsayılanları):
  telefon/WhatsApp **+90 532 588 26 30**, adres **Maltepe Mah. Eski Çırpıcı Yolu Sok. No:8
  Parima Plaza Kat:12 Ofis:146, 34010 Zeytinburnu / İstanbul**, e-posta info@dubaivizeonline.com.

### İçerik / UI
- İştirak notu: `affiliation_note()` (content.py) → `/content/site` ve `/content/legal`;
  `BoldText.jsx` ile şirket adları **kalın**; yasal sayfalar, footer ve Hakkımızda'da gösteriliyor.
  Adlar bilinçli olarak "XXXX Travel Solutions Turizm Ltd. Şti." / "XXXX Travel Solutions FZE" yer tutucu.
- Yasal sayfalar: kart kenarları üstteki başlık kartıyla aynı hizada, bölümler 2 kolon (lg+).
- Menü: "Bilgi & Hizmetler" içine dinamik **VİZE REHBERİ** grubu (7 rehber, 2 kolon);
  footer başlığı "Vize Rehberi" tekil yapıldı. Nav linkleri + telefon aynı hizaya (y=84) getirildi.
- `/gelismeler`: kapak görselli 3'lü kart ızgarası (5 yazıya Unsplash kapak eklendi, `cover_image`
  admin panelinden düzenlenebilir), detay sayfasında kapak görseli.
- `/seyahat-sigortasi`: kapsam kartları, "Neyi kapsamaz?" (kronik hastalık) uyarısı, kimler için kritik,
  başvuruya nasıl eklenir, Dubai'de sağlık hizmeti adımları, uzatma notu, 6 SSS. Satın alma yok.
- `ImportantNotice.jsx`: 4. madde eklendi (sınır dışı → yeniden girişin kapanması).
- Yolcu ekle butonlarındaki ikon-metin boşluğu düzeltildi.

### Test — iteration_86 (2026-06-10)
`test_reports/iteration_86.json`: backend 11/11, frontend tüm akışlar PASS, kritik/minor hata yok.

## 2026-06-10 — Kod incelemesi düzeltmeleri
- **Döngüsel import kırıldı**: `routes_store.py` artık `apply_fx_to_list`'i `routes_public`
  üzerinden değil doğrudan `fx.py`'den (modül seviyesinde) alıyor. `/api/bundles` doğrulandı
  (5 paket, TL fiyatlar geliyor).
- **`os.system` kaldırıldı**: `tests/test_iteration_82.py` (3 yer) →
  `subprocess.run([...], check=False, capture_output=True)`.
- **Lint temizliği**: ruff `F401/F541/F841` (49 bulgu) otomatik düzeltildi + kalan 1 kullanılmayan
  değişken elle kaldırıldı. `ruff check . --select F,E9` artık temiz.
- **`backend_test.py` karmaşıklığı**: `test_zami_mapping_data_preservation` (220 satır) 7 yardımcı
  metoda bölündü (`_zami_restore_mapping`, `_zami_get_mapping`, `_zami_put_mapping`,
  `_zami_check_expected`, `_zami_partial_update_preserves`, `_zami_empty_constants_clears`,
  `_zami_empty_selector_accepted`, `_zami_verify_restore`); `run_all_tests` (125 satır)
  `_run_section` + `_run_public_sections`/`_run_admin_sections`/`_run_gender_sections`/`_print_summary`
  şeklinde ayrıldı; `test_tracking_lastname_validation` (103 satır) payload builder + vaka döngüsüne
  indirildi. En uzun metot artık 82 satır.
- **Yanlış pozitifler (kod değişikliği yapılmadı, doğrulandı)**:
  - `zami_rpa.py:90` "exec()" bulgusu → aslında `asyncio.create_subprocess_exec(...)` argüman
    listesiyle çağrılıyor; shell yok, kod enjeksiyonu riski yok.
  - "`is` ile literal karşılaştırma" → `ruff --select F632` **0 bulgu**; eşleşmeler docstring/log
    metinlerindeki "is" kelimesi.
  - "6 tanımsız değişken" → `ruff --select F821` ve `pyflakes` **0 bulgu**.

## 2026-06-10 (2) — Mobil deneyim, telefon maskesi ve Dubai ofisi

### Mobil uyumluluk (iPhone + Samsung)
- Header mobilde kısaldı (`h-[84px] sm:h-[96px] lg:h-[108px]`); başvuru sihirbazının sabit adım
  çubuğu artık header'ın tam altında (`top-[86px] sm:top-[98px] lg:top-[110px]`) — önceden 33px
  header'ın arkasında kalıyordu.
- Sihirbaz butonları mobilde tam genişlik ve alt alta, birincil CTA en üstte
  (`flex flex-col-reverse ... sm:flex-row`).
- Yüzen sosyal buton grubu mobilde yalnız WhatsApp gösteriyor (Google/Instagram `hidden sm:flex`) —
  içeriğin üzerini kapatma sorunu giderildi.
- `SelectTrigger` mobilde 16px (iOS'ta otomatik zoom olmuyor); mobil menüye erişilebilir
  `SheetTitle` + `SheetDescription` (sr-only) eklendi.
- Bayrak çifti 360px'ten itibaren görünür (`min-[360px]:flex`, kademeli boyut), yatay taşma yok.
- Doğrulama: iteration_89 (mobil uçtan uca başvuru + ödeme, %100 PASS) ve iteration_90.

### Telefon alanı hayalet maske
- `/basvuru` iletişim telefonunda `+90 5` sonrası kalan `XX XXX XX XX` deseni soluk “ghost”
  olarak görünüyor, yazdıkça karakter karakter kayboluyor, silindiğinde geri geliyor
  (`PHONE_MASK`, `data-testid="phone-mask-hint"`, pointer-events yok).
- Mobil menüdeki telefon butonu WhatsApp tarzı dolu yeşil (#25D366, 48px) hâle getirildi.

### Dubai ofisi ve içerik
- `COMPANY.dubai_address` / `dubai_phone`: Level 27, Unit 2705, Marina Plaza, Dubai Marina —
  Tel +971 50 867 26 30. `/iletisim`'de İstanbul + Dubai ofis kartları (adres, telefon, harita,
  yol tarifi), footer'da Dubai satırı, Admin → Acente Bilgileri'nde yeni alanlar.
- Menüde "Hizmetler" ikonu tamirat anahtarı yerine `ConciergeBell`; mobil menüden ayrı
  "Başvurularım" girişi kaldırıldı (tarayıcıdaki gibi tek "Başvuru Takip" sayfası).
- Havale kartlarındaki hesap sahibi adı "VizeAtlas…" → "Dubai Vize Online Turizm ve Danışmanlık A.Ş.".
- Sihirbazın havale onay ekranı artık tek eski IBAN yerine 3 bankalı kopyalanabilir akordiyonu
  gösteriyor; başvuru gönderiminde çift tıklama kilidi (`submitLock`) eklendi.

## 2026-06-09 · İmzalı dosya erişimi (SEC-003 kapatıldı) + vesikalık engelleme kuralı

### Güvenlik: `/api/files/{id}` artık açık değil
- Yeni `backend/file_access.py`: JWT_SECRET ile **HMAC-SHA256 imzalı, süreli** dosya jetonu
  (`?t=<exp>.<imza>`). Fonksiyonlar: `make_token`, `token_valid`, `admin_token_valid`,
  `file_path` (site içi görece yol), `file_url` (e-posta için tam adres),
  `add_file_urls` (bir sözlükteki her `*_file_id` yanına imzalı `*_url` ekler).
  TTL: görünüm 12 saat · yükleme önizlemesi 7 gün · Zami aktarımı 6 saat · e-posta 180 gün.
- `routes_public.get_file`: geçerli `?t=` jetonu **veya** yönetici Bearer jetonu yoksa **403**.
- `db._serialize_mapping` (serialize_doc): dosya kimliklerinin yanına imzalı bağlantı ekler →
  yönetici paneli, `/takip`, `/hesabim` ve sipariş sayfaları tek noktadan imzalı URL alıyor
  (erişim, belgeyi görebilme yetkisini takip eder).
- E-posta/WhatsApp bağlantıları imzalandı: `routes_admin` send-visa · WhatsApp metni ·
  `admin_deliver_order` (eSIM/poliçe), `insurance_tasks.issue_policy`, `visa_delivery`,
  `zami.build_payload` (RPA/bookmarklet indirmeleri).
- Frontend: `lib/api.js → fileUrl(signedPath, download)` artık dosya kimliği değil imzalı yol
  alıyor; `FileDropzone` (önizleme), `AdminApplicationDetail.DocumentViewer({url})`,
  `Track.jsx` (`visa_result.file_url`), `OrderStatus.jsx` (`delivery.esim_url/policy_url`).
- Ek sıkılaştırmalar: `JWT_SECRET` için `dv-dev-secret` yedeği kaldırıldı (routes_admin,
  routes_account, admin_test_token); CORS artık her origin'i yansıtmıyor
  (env `CORS_ORIGINS`/`PUBLIC_SITE_URL` + `dubaivizeonline.com|emergentagent.com|emergent.host`
  regex'i; kötü origin'e `access-control-allow-origin` verilmiyor — NOT: platform ingress'i
  dışarıda hâlâ `*` ekliyor, uygulama Bearer jetonu kullandığı için etki yok);
  Zami handoff jetonu artık en fazla 10 kez kullanılabiliyor (`HANDOFF_MAX_USES`).
- Doğrulama: curl (jetonsuz 403 · imzalı 200 · kurcalanmış 403 · çapraz dosya 403 ·
  admin Bearer 200) + iteration_91 (backend 10/10, yönetici panelinde belge küçük resimleri
  imzalı URL ile yükleniyor, `/takip` sorgulaması çalışıyor).

### Vesikalık uygun olmadan başvuru devam etmiyor (kullanıcı isteği)
- `Apply.jsx validateStep` (step 2/Evraklar): fotoğraf kontrolü `warn` dönerse
  `e.photo_quality` ile ileri geçiş **engellenir**; kontrol sürüyorsa/hiç yapılmadıysa
  (taslak geri yükleme) bekletilir ve kontrol otomatik başlatılır. `skipped` (AI kotası/servis
  yok) durumunda engelleme uygulanmaz.
- Kırmızı bant `data-testid="photo-quality-block-warning"` (adım başında) + toast; uyarı
  kutusundaki "Yine de bu fotoğrafla devam edebilirsiniz" metni
  "Bu fotoğrafla başvuruya devam edilemez…" olarak değişti.
- Doğrulama (Playwright, gerçek AI çağrısı): manzara görseli → uyarı + `photo-quality-block-warning`
  + adım 3'te kalındı; üretilmiş uygun vesikalık → `traveler-0-photo-check-ok` ve adım 4'e geçiş.
  Endpoint kontrolü: manzara `ok:false, score 0.08` · portre `ok:true, score 0.95`.

## 2026-06-09 · Kod incelemesi turu 3 — 3 bulgu yanlış alarm, karmaşıklık düşürüldü

### Doğrulanan yanlış pozitifler (kod değişikliği gerekmedi)
- `zami_rpa.py:90` "exec() güvenlik açığı" → satır `await asyncio.create_subprocess_exec(
  sys.executable, "-m", "playwright", "install", "chromium")`; sabit argv, kullanıcı girdisi yok.
  Projede `exec(`/`eval(` hiç yok (tarama 0 sonuç). **3. kez** aynı yanlış alarm.
- "7 yerde tanımsız değişken" → `ruff --select F821` = 0 hata.
- "85 yerde `is` ile literal karşılaştırma" → `ruff --select F632,E711,E712` = 0 hata;
  raporun verdiği 13 satırın tamamı `is None` / `is not None` / `is False` (doğru kullanım).

### Uygulanan gerçek düzeltmeler
- **Karmaşıklık** (radon): `passport_ai.apply_background_report` 21→4,
  `passport_ai.background_report` 16→3 (`_load_rgb_thumb`, `_edge_samples`, `_luminance_stats`,
  `_accept_background`, `_reject_background`, `_without_background_issues`);
  `ocr_metrics.summarize` 18→6 (`EMPTY_SUMMARY`, `_field_rows`, `_duration_stats`, `_rate`);
  `insurance_tasks.profit_report` 15→3 (`_sold_insurance_totals`, `_profit_row`).
  Davranış birebir korundu; `/api/admin/insurance-report`, `/api/admin/ocr-report`,
  `/api/admin/profit-monthly` 200.
- **Ortak yardımcılar ayrıldı** (raporun "shared utilities to a common module" maddesi):
  yeni `backend/admin_auth.py` → `JWT_SECRET`, `SESSION_DAYS`, `create_token`, `require_admin`,
  `hash_code`. `routes_admin` ve `routes_zami` buradan alıyor (routes_zami artık routes_admin'e
  bağımlı değil); routes_admin import sayısı 27→25 ve jwt/sha256/HTTPBearer importları düştü.
  `routes_admin.py`'yi konu bazlı modüllere bölme (P2) YAPILMADI: tamamen kozmetik, panelin
  tüm uç noktalarını taşıdığı için regresyon riski faydasından büyük.
- **Bayat test beklentileri güncellendi** (katalog değişmişti): 7 aktif vize (8 değil),
  12 ürün (11 değil), 2 tur ürünü, `visa_transit_48` beklentileri kaldırıldı (ürün pasif),
  tur saatinde geçersiz değer artık ilk slota düşmüyor 400 dönüyor, `/api/content/legal`
  yanıtındaki `affiliation` alanı tolere ediliyor.
  Sonuç: **pytest 161 geçti / 0 hata** (tur başında 12 hata vardı). Not: müşteri OTP testleri
  arka arkaya çalıştırılınca IP saatlik kod limitine (429) takılıyor — beklenen davranış,
  backend yeniden başlatılınca geçiyor.
- Doğrulama: yönetici OTP akışı (request-code → verify-code → korumalı uç noktalar 200,
  jetonsuz/bozuk jeton 401, kod tek kullanımlık), Zami yönetici uç noktaları 401/200,
  imzalı dosya erişimi (jetonsuz 403 · admin Bearer 200), `/admin` panosu 125 başvuruyu
  listeliyor (ekran görüntüsü).

## 2026-06-09 · Marka değişikliği: "Dubai Vize Online" → "Dubai Vize Hattı"

Kullanıcı sesli anlatım için 5 aday isim arasından "Dubai Vize Hattı"nı seçti
(karşılaştırma kayıtları `scripts/generate_brand_samples.py` ile üretildi) ve
markanın sitenin tamamına taşınmasını istedi.

### Yapılanlar
- **Metinler**: 48 dosyada 80 geçiş "Dubai Vize Hattı" olarak güncellendi
  (frontend sayfaları + bileşenler, `index.html` başlık/meta, backend `content.py`,
  `emailer.py BRAND`, `routes_admin`, `routes_zami`, `insurance_tasks`, `otp_reminders`,
  `server.py`, testler). `lib/site.js → COMPANY.brandSuffix = "Hattı"`.
- **Veritabanı**: `site_settings` içindeki `bank_transfer.account_name` ve
  `company_info.legal_name` güncellendi (ikisi de hâlâ PLACEHOLDER unvan).
  `email_outbox` geçmiş kayıtları bilinçli olarak değiştirilmedi (arşiv).
- **Logo**: `scripts/rebrand_logo.py` (yeni) — orijinal PNG'nin illüstrasyonu ve altın
  DUBAI yazısı piksel piksel korunur; yalnızca alt satır silinip **Philosopher Bold**
  (Optima benzeri, Türkçe "ı" doğru) ile yeniden yazılır. Ölçüler dosyadan otomatik
  okunur (metin bbox, cap yüksekliği, taban çizgisi, renk); harf aralığı üst satırla
  aynı yerde bitecek şekilde ayarlanır. Kullanıcı "ince" (stroke 0) sürümü seçti.
  Güncellenen 3 dosya: `logo-horizontal-gold-palm.png` (menü + e-posta başlığı),
  `logo-horizontal.png`, `logo-horizontal-gold.png`. Eskiler `memory/brand_backup/`.
  Amblem/favicon/ikonlarda marka yazısı yok, dokunulmadı.
- **Anlatım sesi**: son sahne metni değişti → tek parça mp3 yeniden üretildi
  (85.1 sn → **78.1 sn**), `full.json` sahne pencereleri ve `VisaExplainer.SCENES`
  içindeki `voiceMs` değerleri yeni zaman damgalarıyla eşitlendi. Yeni kapanış:
  "Vizenizi Dubai Vize Hattı ile kolayca alın…" (başlık: "Dubai Vize Hattı ile
  güvenle başvurun").
- **Hero metni 3 satır → 2 satır** (kullanıcı isteği): `HeroHeadline.jsx` 1. ve 5.
  slogan açıklamaları kısaltıldı; 5 sloganın tamamı masaüstünde tam **2 satır**
  (Playwright ile satır sayısı ölçülerek doğrulandı: 144-154 karakter).

### Doğrulama
- iteration_92 (frontend, %100): 18 açık rota gezildi, eski marka **0 kez** görünüyor,
  logo yükleniyor (naturalWidth 929, alt "Dubai Vize Hattı"), masaüstü + mobil temiz,
  anlatım sesi/JSON 200 ve 78.083 sn, footer + 5 yasal sayfa güncel, kritik akışlar
  (başvuru 1. adım, /admin/giris, ana sayfa CTA'ları) çalışıyor.
- pytest 161 geçti (yalnızca saatlik OTP limitine takılan 2 test 429 veriyor).

### Kullanıcı tarafında kalan işler (bilinçli olarak yapılmadı)
- **Alan adı değişmedi**: site ve e-posta hâlâ `dubaivizeonline.com`. `dubaivizehatti.com`
  boş görünüyor; alınırsa Resend doğrulaması + `SENDER_EMAIL`/`PUBLIC_SITE_URL`/sitemap
  güncellenmeli.
- **Instagram (`/dubaivizeonline/`) ve Google yorum bağlantısı** eski profil adlarını
  gösteriyor; profil adları değişmeden bunlara dokunulmadı (`site_settings.company_info`).
- **Unvan placeholder'ları**: `company_info.legal_name = "Dubai Vize Hattı Ltd."` ve
  footer'daki "XXXX Travel Solutions Turizm Ltd. Şti. / FZE" gerçek unvanla değiştirilmeli.
- Kullanılmayan `logo-full.webp` ve `logo-lockup.png` (sosyal medya kare sürüm) hâlâ eski
  yazıyı taşıyor; dikey yerleşim otomatik ölçüme uymadığı için elle işlenmeli.

## 2026-06-09 · Test verisi temizliği + sosyal medya logosu + vesikalık yardımcısı

### 1) Test verisi temizliği (`scripts/cleanup_test_data.py`, dry-run varsayılan)
- Ölçüt: iletişim e-postası `example.com` / `resend.dev` / `@test.` ya da ad-soyad "TEST"
  ile başlayan başvuru/sipariş. Bağlı kayıtlar da zincirleme silinir.
- Silinen: 136 başvuru, 138 sipariş, 337 dosya (212 bağlı + 125 sahipsiz), 580 e-posta
  arşivi, 19 iletişim mesajı, 18 bildirim, 18 sigorta işi, 45 kayıtlı yolcu, 171 OTP kodu,
  9 taslak, 1 ödeme kaydı, 2 OCR metriği.
- Korunan: gerçek kayıt **DV-BJ930600 (Sedat Andic)** ve ilişkili sipariş + dosyaları.
  Panel artık 1 başvuru gösteriyor (yönetici API ile doğrulandı).
- Dokunulmayan: `visits` (224 ziyaretçi kaydı; çoğu Google Cloud IP'li test trafiği ama
  gerçek ziyaret de olabileceği için kullanıcı onayı bekliyor), eski `poc_*` koleksiyonları.

### 2) Sosyal medya kare logosu (`scripts/make_social_logo.py`)
- 1080x1080, orijinal illüstrasyon (deve + altın palmiye + silüet + dalga) ve altın DUBAI
  yazısı yatay logodan piksel piksel kırpılır; alt satır Philosopher Bold ile yazılır.
- Üretilen dosyalar: `/brand/social-square.png` (şeffaf), `-light.png` (krem zemin),
  `-dark.png` (lacivert zemin, krem yazı). Profil resmi daire kırpımı test edildi, taşma yok.
- Bu dosyalar sitede kullanılmıyor; Instagram/WhatsApp profiline elle yüklenmek için.

### 3) Vesikalık reddedildiğinde yardımcı (`components/PhotoRetryHelper.jsx`)
- Eski uyarı kutusu yerine: **"Sizin kareniz" ↔ "Olması gereken"** yan yana karşılaştırma
  (kullanıcının imzalı URL'li fotoğrafı + `/photo-guide/ok.jpg`), yapay zekânın bulduğu
  sorun listesi, **"Doğru kare 5 adımda"** çekim rehberi, tek dokunuşla
  **"Yeni fotoğraf yükle"** düğmesi ve varsayılan açık gelen doğru/yanlış örnek galerisi.
- `FileDropzone` yeni `onInputRef` prop'u ile gizli dosya girdisini dışarıya veriyor;
  yardımcıdaki düğme doğrudan dosya seçiciyi açıyor. `photoGuideKeys` state'i kaldırıldı.
- Doğrulama (Playwright, gerçek Gemini çağrısı): manzara görseli yüklendi → yardımcı açıldı,
  karşılaştırma görselleri ve 4 örnek yüklendi (naturalWidth > 0), 5 adımlı rehber göründü,
  "Yeni fotoğraf yükle" dosya seçiciyi açtı ve yeni dosya yüklendiğinde kontrol yeniden koştu.
  data-testid'ler: `traveler-{i}-photo-check-warning`, `...-mine`, `...-example`,
  `...-retry-button`, `...-guide-toggle`, `...-guide`.

## 2026-06-09 · Anlatımdan "vize örneği" çıkarıldı + gerçek şirket unvanları

### Anlatım (VisaExplainer)
- Son bölüm (`specimen` sahnesi: "Onaylanan vizeniz böyle görünür") anlatımdan kaldırıldı.
  Ses tek parça yeniden üretildi: **73.3 sn / 7 sahne** (önce 78.1 sn / 8 sahne);
  `full.json` pencereleri ve `SCENES[].voiceMs` yeni zaman damgalarıyla eşitlendi.
  Anlatım artık CTA sahnesinde bitiyor (doğrulandı: `explainer-dot-*` 7 nokta,
  specimen yok).

### Yeni bölüm: e-Vize örneği (`components/VisaSpecimen.jsx`)
- **/gerekli-belgeler** sayfasına taşındı: "Onaylanan vizeniz böyle görünür" başlığı,
  büyütmeli (Dialog) belge önizlemesi, 4 maddelik bilgi listesi (PDF olarak e-posta +
  WhatsApp'a gelir, pasaporta etiket yapıştırılmaz, havalimanında telefondan gösterilir,
  takip koduyla yeniden indirilebilir) ve "Başvuruya başla" düğmesi.
- Görsel web için optimize edildi: `explainer/specimen.png` (892 KB) →
  `/samples/evisa-specimen.jpg` (1200x1696, 185 KB, progressive).
- data-testid: `visa-specimen-section`, `visa-specimen-open-button`,
  `visa-specimen-full-image`, `visa-specimen-apply-button`.

### Gerçek şirket unvanları (kullanıcıdan geldi)
- Türkiye: **Moruya Travel Solutions Turizm Ltd. Şti.** · Dubai: **Moruya Travel Solutions FZE**
- `content.py COMPANY`: `legal_name`, `parent_company` (TR) ve `dubai_company` (FZE)
  gerçek unvanlarla güncellendi; `XXXX ...` yer tutucuları tamamen kalktı (kod + DB'de 0).
- `affiliation_note` metni yeniden yazıldı: artık alan adı değil marka üzerinden konuşuyor —
  "Dubai Vize Hattı, **Moruya Travel Solutions Turizm Ltd. Şti.** tarafından işletilen bir
  markadır; … BAE'deki grup şirketimiz **Moruya Travel Solutions FZE**'dir."
- DB: `site_settings.company_info.legal_name/parent_company/dubai_company` ve
  `bank_transfer.account_name` (havale alıcı adı) TR unvanına çevrildi.
- `AdminCompany.jsx` alan örnekleri gerçek unvanlarla güncellendi.
- Doğrulama: `/api/content/site` yanıtı + footer ("Ticaret Unvanı: Moruya Travel Solutions
  Turizm Ltd. Şti.") tarayıcıda kontrol edildi.

### Hâlâ eksik olan tek bilgi
Vergi dairesi / vergi no / MERSİS / ticaret sicil no alanları `company_info` içinde boş
(varsayılan `content.py` değerleri: "Beşiktaş Vergi Dairesi", "0000000000"). Yönetici →
Şirket ekranından girilmeli; yasal metinlerde bu bilgiler gösteriliyor.

## 2026-06-10 · Sepet (eSIM/sigorta ayrı satış), anlatım düzeni, kur kaynağı
Kullanıcı istekleri: "i cant choose other summary cards, same for insurance make kind of
sepet to see users what services they bought — maybe someone bought visa later wanted to add
insurance or esim" + anlatım panelinde yazı/resim çakışması + örnek vize çok büyük + logo
alanına tıklayınca ana sayfa + fiyat sekmelerinin ortalanması + Barchart kur kaynağı.

### 1) Sepet sistemi (yeni)
- `frontend/src/lib/cart.js` (yeni): localStorage tabanlı sepet (`dv_cart_v1`), `useCart()`
  hook'u (add/setQty/remove/clear/linkApplication), `dv-cart-change` event'i ile tüm
  bileşenler senkron. Yalnız `product_id` + `quantity` saklanır; fiyat her zaman
  `/api/products`'tan gelir (bayat fiyat riski yok). Limitler: 10 adet/kalem, 6 kalem.
- `components/PlanShowcase.jsx`: eSIM ve sigorta kartları artık **seçilebilir** —
  adet arttır/azalt + "Sepete ekle" (`plan-add-to-cart-{id}`, `plan-qty-plus/minus-{id}`),
  sepette olan kartta yeşil "Sepette · N adet" rozeti. Alt CTA "bilgi amaçlıdır" yerine
  "Sepete git (n)" + "Vize başvurusuna başla". `?basvuru=REF` parametresi sepete başvuru
  kodunu bağlar ve bilgi notu gösterir.
- `components/CartButton.jsx` (yeni): navbar'da sepet ikonu + adet rozeti
  (`navbar-cart-button`, `navbar-cart-count`), mobil menüde "Sepetim" satırı.
- `pages/Cart.jsx` (yeni, `/sepet`): kalemler (adet +/-, sil, satır toplamı), ara toplam,
  **%10 paket indirimi** (sigorta + eSIM birlikteyse), ödenecek tutar; ad/e-posta/telefon,
  opsiyonel gidiş-dönüş tarihi, opsiyonel **vize başvuru kodu**, not; ödeme yöntemi
  kart (Stripe) / havale. Kart → `POST /orders/{id}/checkout` → Stripe; havale →
  `/siparis/{SV-...}` (banka bilgileri orada). Başarıda sepet boşalır. Boş sepet durumu
  eSIM/sigorta linkleriyle.
- `pages/MyAccount.jsx`: "eSIM & sigorta siparişlerim" → **"Satın aldığım ek hizmetler"**
  (boş durumda mağaza butonları + "Sepetim"), sipariş satırında bağlı başvuru kodu;
  her başvuru kartında **"eSIM ekle"** ve **"Sigorta ekle"** düğmeleri
  (`/esim?basvuru=REF`, `/seyahat-sigortasi?basvuru=REF`).
- Backend `routes_store.py`: `OrderCreateIn.application_reference` + `_linked_application()`
  — kod bulunamazsa 400, e-posta uyuşmazsa 400, doğruysa siparişe `application_id` +
  `application_reference` yazılır; bağımsız siparişlerde `source: "store"`.
- Test: iteration_94 backend %100 (6/6 pytest, `backend/tests/test_iteration_94_cart.py`) +
  frontend %100 (sepete ekleme, sayfalar arası kalıcılık, %10 indirim matematiği,
  havale ve kart ödeme akışı, form doğrulama, `?basvuru=` derin linki).

### 2) Anlatım paneli (VisaExplainer) — çakışma + boyut
- Yerleşim `sm:absolute` katmandan **2 kolonlu grid**'e geçti (`sm:grid-cols-[46%_54%]`,
  metin solda, görsel sağda) → yazılar artık resmin üstüne binmiyor (ölçüm: altyazı sağ
  kenarı 874 < görsel sol kenarı 918). Panel yüksekliği 470→**420px**, görsel dolgusu
  `p-1.5 sm:p-2`, metin genişlikleri 420/400px.
- Görseller ~%25-35 büyütüldü: `scripts/trim_explainer_images.py` (yeni) tüm
  illüstrasyonların çevresindeki boş zemini kırpıyor (track 1180→909 px genişlik).
- Kullanıcı "en sondaki animasyon boyutları iyi, diğerlerini de öyle yap" dedi → geniş
  (1.75-1.8 oranlı) 4 illüstrasyon **kare kompozisyona** yeniden üretildi (Gemini 3.1 Flash
  Image, referans olarak eski görseller verilerek stil/metin korundu): intro, passport
  (TÜRKİYE CUMHURİYETİ / REPUBLIC OF TÜRKİYE / PASAPORT yazıları korunuyor), photo, upload
  (GEREK YOK yazısı korunuyor). Eski geniş sürümler `*.wide.png`, kırpma öncesi
  `*.pretrim.png` olarak yedekte. Artık 7 sahnenin tamamı çerçeveyi dikeyde dolduruyor
  (vgap 0) — üst/alt boşluk kalmadı.

### 3) Örnek vize (VisaSpecimen)
Önizleme soldaki metin kolonuyla aynı genişlikte (`max-w-md`, 448px; grid `lg:grid-cols-2`),
üzerinde "Büyütmek için tıklayın" etiketi; tıklayınca Dialog `max-w-5xl` / `max-h-[80vh]`
ile tam boy açılıyor.

### 4) Logo/bayrak alanı → ana sayfa + en üst
`Navbar`: logo linki ve **bayrak çifti** artık `Link to="/"`; `goHomeTop()` ile aynı
sayfadayken de yumuşak şekilde en üste kaydırıyor (doğrulandı: y=3319 → y=131 → y=1).

### 5) Fiyat sekmeleri ortalandı
`PricingTabs`: sekme şeridi `flex justify-center` içine alındı — "Tek Girişli Vize /
Çok Girişli Vize / Çocuk Vizesi" satırda ortada (1920px'te merkez tam 960).

### 6) USD/TRY kur kaynağı (Barchart engelliyor)
Kullanıcı barchart.com/forex/quotes/^USDTRY istedi; **sunucudan erişilemiyor**
(Cloudflare bot koruması: HTTP 202, boş gövde, çerez yok — Playwright/Chromium de bu podda
kurulu değil). Aynı bankalar arası kotasyonu veren **Yahoo Finance `USDTRY=X`** birincil
kaynak yapıldı (`fx.py` YAHOO_URL + `parse_yahoo_json`), doviz.com / open.er-api /
exchangerate.host yedekte. Kur notu kaynağı "forex (USD/TRY)" olarak gösteriyor
(48,41 × %2 marj = 49,38 ₺; eski doviz.com serbest piyasa satışı 49,46 ₺ idi).

## 2026-06-10 (2. tur) · Turlar sepette, hazır paket sepete ekleme, sepet hatırlatma
Kullanıcı onayı: tur sayfası + sepette tarih/saat (a), paket kartına "Sepete ekle" (a),
hatırlatma 2 saat + 24 saat (b).

### Çöl safarisi sepette
- `pages/Tours.jsx` (yeni, `/dubai-turlari`): safari + VIP safari kartları, kart üzerinde
  tarih (DateField) + otelden alınış saati (14:00-16:00 slotları) + kişi sayısı +
  "Sepete ekle". Tarih/saat seçilmezse Türkçe hata toast'ı. Navbar "Bilgi & Hizmetler →
  Çöl Safarisi & Turlar" ve footer linki eklendi.
- `lib/cart.js`: satırlar artık `scheduled_date` / `scheduled_time` taşıyor; `setSchedule()`
  ile sepette düzenlenebiliyor, `addMany()` ile çoklu ekleme, `linkBundle()` ile paket bağı.
- `pages/Cart.jsx`: tur satırında düzenlenebilir tarih/saat bloğu (`TourSchedule`), eksikse
  uyarı + ödeme engeli; sipariş yükünde tarih/saat gönderiliyor.
- `pages/OrderStatus.jsx`: sipariş detayında tur tarihi + alınış saati gösteriliyor
  (test raporu iteration_95 MEDIUM bulgusu düzeltildi), sayfa metni ve butonlara tur eklendi.
- VIP safari görseli yanlıştı (yeşil kayalık manzara) → çöl kampı görseliyle değiştirildi
  (`store_catalog.py` + DB).

### Hazır paket → sepete ekleme
- `HomeBundleStrip.jsx`: kart artık iki aksiyonlu — "Bu paketle başvur" (mevcut akış) ve
  **"Sigorta + eSIM'i sepete ekle"** (tek tık, %10 indirim). Sepete `bundleId` yazılır.
- `Cart.jsx`: paket sepetteyse "Bu pakette vize de var → Vize başvurusunu başlat" şeridi
  (`/basvuru?paket=<id>`), çünkü vize ücreti başvuru formunda tahsil ediliyor.

### Terk edilmiş sepet hatırlatması (2 saat + 24 saat)
- `POST /api/cart/snapshot` (yeni): e-posta + kalemler + paket kimliği; e-posta başına tek
  kayıt (`cart_snapshots`), fiyat ve %10 indirim sunucuda hesaplanıyor. Boş kalemle
  gönderilirse kayıt pasife alınır. Sipariş oluşunca `create_order` kaydı kapatıyor
  (`closed_reason: "ordered"`).
- `cart_reminders.py` (yeni): `due_stage()` 2. saatte 1., 24. saatte 2. hatırlatmayı
  tetikler; `run_cart_reminder_sweep()` 15 dakikada bir çalışır (server.py lifespan),
  siparişi olan kaydı atlar. `emailer.cart_reminder_html()` Türkçe e-posta şablonu.
- `Cart.jsx`: geçerli e-posta yazıldıktan 1,5 sn sonra sepet sunucuya kaydediliyor.

### Anlatım illüstrasyonları (kullanıcı istekleri)
- Zeminler saydam (`scripts/transparent_explainer_bg.py`), panel rengiyle birleşiyor;
  yükseklik 386px, sol/sağ boşluklar eşitlendi (`sm:grid-cols-[46%_54%]`, `sm:pr-8`).
- intro sahnesi yeniden üretildi: tek quad bike (jeep'e temas etmiyor), **Skydive Dubai**
  paraşütü (kanopide "SKYDIVE DUBAI" yazısı), palmiyeler tam görünüyor, dolgu zemin/blok yok.
- passport sahnesi: "PASAPORT" altında "PASSPORT", gerçekçi biyometrik kimlik sayfası
  (örnek ad AYŞE YILMAZ, MRZ satırları, hologram portre).
- upload sahnesi: yazılar Türkçe ("UÇAK BİLETİ", "OTEL REZERVASYONU", "GEREK YOK"),
  öğeler ayrı bölgelerde, iç içe geçme yok.

### Test
- iteration_95: backend 8/8 pytest (tur kataloğu, tur tarih/saat doğrulaması,
  `/cart/snapshot` upsert + pasife alma, hatırlatma sweep'i), frontend akışları geçti;
  tek MEDIUM bulgu (sipariş detayında tur tarihi görünmüyor) düzeltildi ve doğrulandı.

### ⚠️ Üretim uyarısı: Resend gönderici domaini doğrulanmamış
`SENDER_EMAIL=info@dubaivizeonline.com` (eski marka) Resend'de doğrulanmadığı için
**tüm e-postalar hata alıyor** (`email_outbox.status = "error"`: "The dubaivizeonline.com
domain is not verified"). Yeni marka domaini `dubaivizehatti.com` resend.com/domains
üzerinde doğrulanıp `SENDER_EMAIL` güncellenmeli; aksi halde giriş kodu, sipariş ve
sepet hatırlatma e-postaları müşteriye ulaşmıyor.

## 2026-06-11 · Admin WhatsApp AI paneli (iteration_96, frontend %100)
Eski "manuel bildirim" ekranı yerine `/admin/whatsapp` 5 sekmeli WhatsApp AI paneli oldu.
- `pages/AdminWhatsApp.jsx` yeniden yazıldı: mod rozeti (`wa-mode-badge`: Canlı / Simülasyon),
  simülasyon uyarı bandı (`wa-simulate-warning`) ve Shadcn Tabs (`wa-tabs`).
- `components/whatsapp/WaDocumentQueue.jsx`: tedarikçi belgeleri kuyruğu — durum filtreleri
  (onay bekleyen / iletilen / okunamayan / tümü), belgeden AI'nin okuduğu alanlar, eşleşme
  güven yüzdesi + sebep etiketleri, başvuru arama (`/ai/applications`) ile **ata** ve **reddet**.
- `components/whatsapp/WaConversations.jsx`: konuşma listesi (temsilci bekleyen rozeti),
  mesaj baloncukları (müşteri/bot/temsilci), sohbet bazlı bot aç-kapa, manuel yanıt
  (24 saatlik servis penceresi hatası Türkçe gösterilir).
- `components/whatsapp/WaBotSettings.jsx`: webhook adresi + kopyala, bot/otomatik teslim
  anahtarları, Meta Cloud API alanları (phone_number_id, waba_id, access_token, app_secret,
  verify_token, graph_version, tedarikçi grup/numaralar, şablon adı/dili), grup oluştur +
  davet linki (simülasyon modunda Türkçe hata verir, çökmez).
- `components/whatsapp/WaSimulator.jsx`: müşteri mesajı simülasyonu (botun gerçek LLM yanıtı)
  + tedarikçi PDF yükleyip eşleştirme testi.
- `components/whatsapp/WaManualNotify.jsx`: eski vize sonucu bildirim ayarları + son
  bildirimler logu korundu (5. sekme).
- Test: iteration_96 → istenen tüm akışlar geçti. "Toast iki kez çıkıyor" bulgusu
  doğrulandı ve **yanlış pozitif** (tek `<Toaster/>`, ölçümde 1 toast).
- Simülasyon test verileri temizlendi (`wa_conversations`, `wa_documents`, `wa_messages`,
  `wa_events` → 0) ve `graph_version` v25.0'a geri alındı.

## 2026-06-11 · BUG: anlatımda telefonun sol alt köşesi kırpık (iteration_97, %100)
Kullanıcı mobil ekran görüntüsü paylaştı: ADIM 3 (track) sahnesinde telefonun sol alt köşesi
kesik görünüyordu.
- **Kök neden**: CSS/kırpma değil, **görsel dosyasının kendisi** bozuktu. `track.png`in saydam
  zemini üretilirken zemin ayıklama telefonun sol kenar çizgisinden içeri sızmış ve alt sol
  köşeyi silmişti (kaynak `track.jpg` sağlamdı). `object-contain` olduğu için CSS kırpması yoktu.
- **Düzeltme**: `scripts/rebuild_explainer_png.py` (yeni) — sağlam `track.jpg`ten düşük eşikli
  (thresh 20) flood fill ile zemin saydamlaştırıldı, kenarlar 6px payla kırpıldı.
  Yeni dosya 1251x839, zemin %49 saydam; bozuk sürüm `track.cutcorner.png` olarak yedekte.
  JSX/CSS değişmedi.
- Diğer 6 sahne kontrast kontak sayfasıyla denetlendi; benzer aşınma yok.
- Test: iteration_97 → mobil (414x900) + masaüstü (1920x800): telefon tam görünüyor
  (taşma < 1px), 7 sahnenin görseli yükleniyor, ses/CC/duraklat/CTA/TÜRSAB mührü çalışıyor.

## 2026-06-11 · Anlatım kapağı + Resend anahtarı + hero CTA (iteration_98, %100)
- **Anlatım kapağı** (`VisaExplainer.jsx`): yeni `started` state. Sayfa açılışında sahne
  döngüsü, Ken Burns ve ses TAMAMEN durur; illüstrasyonun üzerinde kapak katmanı
  (`explainer-cover`) + yuvarlak oynat düğmesi (`explainer-cover-play-button`) ve
  "Anlatımı başlat · 1,5 dakika" etiketi görünür. Kaydırma/tıklama artık sesi başlatmıyor
  (eski "ilk etkileşimde çal" dinleyicisi kaldırıldı); anlatım bitince kapak karesine dönülür
  (`onEnded` → started/soundOn false, index 0). Mobil "Anlatımı dinle" düğmesi yalnız anlatım
  başladıktan sonra ve duraklamışken görünür.
- **Resend**: kullanıcı tam yetkili anahtar verdi → `backend/.env RESEND_API_KEY` güncellendi.
  Resend'de doğrulanmış alan adı `dubaivizehatti.com` (SENDER_EMAIL zaten o). Gerçek gönderim
  testi: `status=sent` + provider_id; `/api/account/request-code` akışı da `sent`.
- Hero ana butonu: "Başvuruya Başla" → **"Hemen Başvuruya Başla"** (`Home.jsx`).
- Test: iteration_98 backend %100 + frontend %100 (masaüstü ve 414x900 mobil).

## 2026-06-11 · Seslendirme v3 + duraklamalar + intro çizimi (iteration_99, %100)
Kullanıcı notları doğrultusunda anlatım baştan üretildi (`scripts/generate_narration_eleven.py`):
- **Model `eleven_v3`** + cümle başı duygu etiketleri: `[warm]`, `[energetic]`, `[excited]`,
  `[confident]`, `[reassuring]`, `[informative]`, `[emphatic]` → yeni cümleye enerjik giriş,
  cümle sonuna doğru tempo düşüşü. "Dubai sizi bekliyor!" `[excited]`.
- **"Dubaai" yazımı kaldırıldı** (artık düz "Dubai" okunuyor).
- **Gerçek duraklamalar**: v3 `<break>` etiketlerini 0,1-0,2 sn'ye sıkıştırdığı için sessizlik
  artık ses dosyasına sonradan ekleniyor (pydub + ffmpeg): cümle araları **0,35 sn**,
  "İlk olarak" cümlesinden önce **0,70 sn**. Zaman damgaları eklenen sessizliğe göre kaydırılır
  (`insert_pauses` + `shifted`), böylece altyazı/sahne senkronu bozulmaz.
  full.mp3 67,4 sn (ham 62,5 + 4,9 sn duraklama).
- **Metin değişiklikleri**: "Fotoğrafınızın gözlüksüz ve şapkasız olması **gerekmektedir**.";
  takip sahnesi tek cümle: "Başvurunuzun tüm aşamalarını sizin adınıza biz takip ediyor ve
  onaylanan Dubai vizenizi ortalama iki iş günü içinde e-mail adresinize ve WhatsApp ile
  gönderiyoruz." (hem seslendirme hem altyazı).
- **intro çizimi yenilendi**: palmiyeler artık yalnız sol/sağ kenardan giriyor (devenin ve
  jeepin üstünden çıkmıyor), deve + gezgin + jeep **çöl kumu zemininde** duruyor; gökyüzü
  saydam (1264x848). Eski dosyalar `intro.palmoverlap.{jpg,png}` olarak yedekte.
  NOT: Gemini ile "sadece palmiyeyi taşı" düzenlemesi denendi ama görseli baştan çizip
  Arapça benzeri yazı ekledi → kullanılmadı, sahne aynı öğelerle sıfırdan üretildi.
- Test: iteration_99 frontend %100 (7 sahne senkronu 4/9/16/25/35/46/60 sn, yeni altyazılar,
  intro görseli kırpılmıyor, kapak davranışı ve tüm kontroller).
