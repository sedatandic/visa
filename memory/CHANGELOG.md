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
