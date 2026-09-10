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

## 2026-06-11 · Anlatım: yükleme cümlesi + intro sahnesine quad/jet ski
- Yükleme sahnesi metni güncellendi (seslendirme + altyazı): "Belgelerinizi yükleyip
  ödemenizi yapmanız yeterlidir. Üstelik Dubai vizeniz onaylanmadan önce uçak bileti ya da
  otel rezervasyonu yaptırmanıza da gerek yoktur." (imla düzeltilerek uygulandı: "ya da",
  "yaptırmanıza da"). full.mp3 yeniden üretildi: 67,8 sn, 7 sahne penceresi güncel.
- intro çizimi: jeepin **tavan sepetinde quad bike (ATV)** ve arkasında **römorkta jet ski**
  eklendi; deve, gezgin, UAE bayrağı, Burj Al Arab + Burj Khalifa, paraşütçü, çöl kumu ve
  kenardan giren palmiyeler korundu (1264x848, gökyüzü saydam).
  Yedekler: `intro.desert.{jpg,png}` (quad/jet ski öncesi), `intro.palmoverlap.{jpg,png}` (ilk hali).
- Doğrulama: mobil 414x900 ve masaüstü 1440x900 ekran görüntüsü — görsel kırpılmıyor
  (taşma 0px), sahne senkronu ve kapak karesi çalışıyor.
- Kullanıcı geri bildirimi: jet ski kaldırıldı, intro sahnesi jet ski öncesi haline döndürüldü
  (`intro.desert.{jpg,png}` → `intro.{jpg,png}`; quad bike jeepin yanında). Jet ski'li sürüm
  `intro.quadjetski.{jpg,png}` olarak saklandı.
- Kullanıcı referans görsel paylaştı → intro sahnesi o referansa göre yeniden üretildi:
  köşelerden giren turkuaz palmiyeler, Burj Al Arab, semerli ve deri çantalı deve, gülümseyen
  bej blazerli gezgin (başparmak yukarı + valiz), direkte büyük BAE bayrağı, Museum of the
  Future halkası (dekoratif hat kıvrımları), Burj Khalifa, paraşütçü, kahverengi jeep, kum
  tepeleri. İkinci turda jeep kadraja tam sığdırıldı (ilk üretimde sağ kenardan kesiliyordu).
  Yedekler: `intro.refclipped.jpg` (jeep kesik ilk deneme), `intro.prevdesert.{jpg,png}`,
  `intro.quadjetski.{jpg,png}`, `intro.palmoverlap.{jpg,png}`.
- intro sahnesi son rötuşlar: jeepin tavan sepetine **quad bike** eklendi, BAE bayrağı Museum
  of the Future halkasına **temas etmeyecek** şekilde yukarı-sola alındı, paraşütçü **tandem
  (2 kişi)** yapıldı ve kanopiye **SKYDIVE DUBAI** yazıldı. Yedek: `intro.refnoquad.jpg`.

## 2026-06-11 · E-postalar premium kimlik + intro sahnesi son hali
- **E-posta şablonları premium hale getirildi** (`backend/emailer.py`):
  - `_wrap`: krem zemin, 16px köşeli beyaz kart, logo altında "TÜRSAB Üyesi A Grubu Seyahat
    Acentesi" harf aralıklı üst başlık, altın ince çizgi, 21px başlık.
  - Yeni `_contact_footer()`: künye artık **şirket unvanları + iletişim** içeriyor —
    Moruya Travel Solutions Turizm Ltd. Şti., BAE iştiraki Moruya Travel Solutions FZE,
    TÜRSAB üyeliği, telefon (tel: linki), WhatsApp (wa.me), e-posta (mailto:),
    www.dubaivizehatti.com, İstanbul + Dubai adresleri, Dubai telefonu, çalışma saatleri,
    telif satırı. Tüm şablonlarda otomatik görünür (giriş kodu, başvuru, ödeme, vize hazır,
    sipariş, sepet hatırlatma...).
  - `_row` yenilendi: çerçeve yerine ince altın alt çizgi, küçük büyük harf etiket, sağa
    hizalı kalın değer; boş değerlerde "-" yazar.
- **Taslak e-postalarına başvuru bilgileri eklendi**: "Sayın <ad>," selamı + Başvuran,
  Vize tipi (`_visa_label` ile `visa_type_id` → katalog kısa adı; seçilmediyse "Seçim
  aşamasında"), 1'den fazla yolcu varsa Yolcular listesi, Devam kodu, Yolcu sayısı
  (`draft_saved_html` ve `draft_reminder_html`).
- Doğrulama: 3 şablon tarayıcıda görsel kontrol (kapak, tablo, künye), tüm şablonlarda künye
  metni assert edildi, Resend ile gerçek gönderim `status=sent`, ilgili pytest paketleri
  (test_emailer, iteration_80, iteration_91) 27 passed.
- **intro sahnesi son hali**: sol ve sağdaki palmiyeler artık **tam görünüyor** (kadraj
  dışına taşmıyor), paraşüt **tandem 2 kişi** ve kanopide okunaklı **SKYDIVE DUBAI**, jeep
  tavanında quad bike, bayrak Museum of the Future halkasına temas etmiyor.
  Ara sürümler yedekte: `intro.floatdune.jpg`, `intro.singlejumper.jpg`, `intro.cutpalms.jpg`,
  `intro.refnoquad.jpg`, `intro.prevdesert.{jpg,png}`, `intro.palmoverlap.{jpg,png}`.
- Kapanış (cta) sahnesinin metni kullanıcı yazımıyla güncellendi (seslendirme + altyazı):
  "Vizenizi Dubai Vize Hattı ile kolayca alın. TÜRSAB üyesi A grubu seyahat acentesi iş
  birliğiyle başvurunuzu baştan sona biz yürütüyoruz. Formu doldurun, gerisini bize bırakın.
  Dubai sizi bekliyor!" · full.mp3 66,7 sn, cta penceresi 53,21-66,74 sn.

## 2026-06-12 · Admin bekleyen iş sayacı + misafir sipariş takibi (P1 x2)
- **Admin bildirim sayacı** (ROADMAP P1): `GET /api/admin/stats` iki yeni alan döndürüyor —
  `wa_pending_documents` (wa_documents `pending_review`/`failed`) ve `wa_needs_human`
  (wa_conversations `needs_human:true`). `AdminLayout` bu uç noktayı açılışta ve 60 sn'de bir
  çekip menüdeki **Mesajlar** (okunmamış mesaj) ve **WhatsApp** (belge + temsilci talebi)
  satırlarına sayı rozeti basıyor (`admin-nav-badge-messages`, `admin-nav-badge-whatsapp`).
  Başvurular sayfasının üstünde ayrıca uyarı bandı (`admin-wa-alert`) + "WhatsApp panelini aç"
  butonu var. Doğrulama: rozet "2", band "1 belge eşleştirme bekliyor · 1 konuşma temsilci
  istiyor" (test verileri sonrasında silindi).
- **Misafir sipariş takibi** (ROADMAP P1): `emailer.order_track_url()` +
  `_order_track_button()` → sipariş onayı ve teslim e-postalarına "Siparişimi takip et"
  butonu eklendi (`{SITE}/siparis/{kod}?email=...`, üyelik gerekmez).
  `OrderStatus.jsx` artık `?email=` parametresini okuyup siparişi otomatik açıyor.
  `Cart.jsx`: sipariş sonrası `dv_last_order_ref` saklanıyor ve sepet sayfasının altında
  `cart-last-order-shortcut` kutusu ("Son siparişiniz DV-… · Siparişimi takip et") görünüyor.
  Doğrulama: gerçek sipariş oluşturulup e-posta gövdesindeki link kontrol edildi
  (`status=sent`, link doğru), `/siparis/{kod}?email=` otomatik sorguladı, sepet kısayolu
  göründü; test siparişi ve e-posta kayıtları temizlendi. pytest test_emailer 7/7.

## 2026-06-12 · Seyahat tarihleri Adım 1'e taşındı + tarihe göre 3 öneri kartı
Kullanıcı isteği: "seyahat tarihleri sor gidiş ve dönüş tarihi, ona göre eSIM, seyahat sağlık
sigortası ve Çöl Safarisi tavsiye et" (seçimler: tarihler Adım 1'e taşınsın · 3 ayrı öneri
kartı · safari kişi sayısı yolcu sayısı kadar).
- **Adım 1 (Bilgiler)**: iletişim bilgilerinin altına `travel-dates-block` eklendi —
  Gidiş/Dönüş tarihi (`input-arrival-date`, `input-departure-date`), "tarihim henüz belli
  değil" kutusu + yaklaşık zaman seçenekleri ve `trip-days-note` ("Seyahatiniz X gün").
  Bu alanlar Adım 2'den kaldırıldı; Adım 2'de artık özet satırı var
  (`visa-step-dates-summary` + `visa-step-edit-dates-button` → Adım 1'e döner).
  Adım 2 başlığı "Vize ve tarihler" → **"Vize seçimi"**.
- **Doğrulama taşındı**: tarih zorunluluğu, dönüş<gidiş kontrolü ve pasaport 6 ay kuralı
  artık Adım 1'de (`validateStep` step 0); kalış süresi–vize uyumu (`stay_length`) vize
  seçimi gerektirdiği için Adım 2'de kaldı.
- **`trip-suggestions` (yeni)**: tarihlere göre 3 kart — Seyahat sağlık sigortası, Dubai eSIM,
  Çöl Safarisi (popüler ürün). Her kartta ürün adı, süre/kapsam bilgisi, kişi başı fiyat ve
  Ekle/Kaldır düğmesi (`suggestion-toggle-{insurance|esim|tour}`). Sigorta ve eSIM `bestFit`
  ile seyahat süresini karşılayan en ucuz paket; safaride tarih **gidişin ertesi günü**
  (dönüşü aşarsa gidiş günü) ve saat **15:00** ön seçili (`suggestedTourDate`,
  `preferredSlot`), kişi sayısı yolcu sayısı kadar. Sigorta+eSIM birlikte seçilince
  `suggestions-bundle-note` %10 paket indirimini duyurur.
- Doğrulama (Playwright): 10 günlük seyahatte ins_15d (560₺) + esim_3gb (740₺) +
  safari 11 Temmuz 15:00 önerildi, üçü eklendiğinde özet 5.190 + 560 + 740 + 2.220 − 352
  = **8.358 ₺**; 6 günlük seyahatte ins_8d/esim_1gb önerildi (mobil 414px'te kartlar dikey
  yığılıyor); tarih boşken Adım 1'den ilerlenemiyor; Adım 2 özeti "10 Temmuz 2026 –
  19 Temmuz 2026 · 10 gün" ve "Tarihleri düzenle" Adım 1'e dönüyor.
- **Öneri kartlarına kapak fotoğrafı (2026-06-12)**: Çöl Safarisi kartında ürünün kendi
  `image_url`'i (Unsplash kumul) kapak olarak gösteriliyor; kartların hizası bozulmasın diye
  sigorta ve eSIM kartlarına da kapak eklendi (`SUGGESTION_COVERS`: pasaport damgaları /
  Burj Khalifa silueti). Görseller `h-32 object-cover`, hover'da hafif zoom;
  metin bloğu `flex-1` ile sarıldı, böylece 3 kartın "Ekle" düğmesi aynı hizada.
  Doğrulama: 1440px'de 3 kart 386px eşit yükseklik, üç görsel de 1200px yüklendi.

## 2026-09-06 · Adım 1'e vize türü dropdown'ı + hero flip düzeni
- **Adım 1'de "Başvurduğunuz vize türü" dropdown'ı** (`primary-visa-block`,
  `primary-visa-select`): seyahat tarihlerinin hemen üstünde. Seçim, aynı kategorideki
  (yetişkin/çocuk) tüm yolculara uygulanır; altında kalış süresi, giriş tipi ve kişi başı
  ücret özeti (`primary-visa-meta`).
- **Vize kartından otomatik seçim güçlendirildi**: `?vize=` parametresi artık yalnızca ilk
  yolcuya değil, aynı kategorideki tüm yolculara uygulanıyor; seçim `preselectedVisa` ref'inde
  tutulduğu için sonradan eklenen yolcular da aynı vizeyle geliyor ve
  "… formda otomatik seçildi" bildirimi gösteriliyor.
  Doğrulama: `/basvuru?vize=visa_60_multi` → dropdown "60 Günlük Çok Girişli · 14.810 ₺",
  dropdown'dan 30 günlüğe geçiş Adım 2'deki yolcu seçimine de yansıdı.
- **Hero flip sırası**: "Dubai vizeniz / 2 iş gününde hazır" ilk slogana alındı (HeroHeadline).
- **Metin**: "gerisini biz yönetelim" → **"gerisini biz halledelim"** (hero sloganı, alt metni
  ve Home'daki vurgulu satır). Doğrulama: sayfada "yönetelim" ifadesi kalmadı.
- Not: DateField'da geçmiş tarih girildiğinde çıkan "seçilebilir aralığın dışında" uyarısı
  doğru çalışıyor (pod tarihi 2026-09-06; test tarihleri buna göre seçilmeli).

## 2026-09-06 · Vize karşılaştırma tablosu
- Yeni bileşen `components/VisaComparison.jsx`: 30/60 gün × tek/çok giriş vizelerini tek
  tabloda karşılaştırıyor. Satırlar: kalış süresi, giriş sayısı, ülke dışına çıkış davranışı,
  kişi başı ücret (TL + ≈USD), işlem süresi, "kimler için uygun?" ve seçim/CTA satırı.
  "En çok tercih edilen" kolonu vurgulu; ilk kolon yatay kaydırmada sabit (sticky),
  mobilde kaydırma ipucu var (`visa-comparison-scroll-hint`).
- **`/vize-tipleri`**: PricingTabs'in altına "30 gün mü 60 gün mü, tek giriş mi çok giriş mi?"
  bölümü eklendi (`visa-comparison-section`); her kolonda "Başvuruya başla" →
  `/basvuru?vize={id}` (form otomatik seçili açılır).
- **Başvuru Adım 1**: vize dropdown'ının yanına "Vizeleri karşılaştır" düğmesi
  (`open-visa-comparison-button`) → tabloyu Dialog içinde açıyor
  (`visa-comparison-dialog`); "Bu vizeyi seç" seçimi dropdown'a ve tüm yetişkin yolculara
  uyguluyor, pencere kapanıyor.
- Doğrulama: masaüstünde 4 kolon, fiyatlar 5.190/9.880/9.880/14.810 ₺ ve çıkış davranışı
  doğru; CTA linki `?vize=visa_60_multi`; Dialog'dan seçim sonrası dropdown "60 Günlük Çok
  Girişli · 14.810 ₺" ve meta "60 gün · Çok girişli"; 414px'te tablo kaydırılabilir.

## 2026-09-06 · E-posta logosu gömüldü, konu satırına başvuru no, sepete vize satırı
- **BUG: e-postada logo görünmüyordu.** Kök neden: logo `<img src>` ile geçici önizleme
  alan adından (`*.preview.emergentagent.com`) çekiliyordu; pod uykuya geçtiğinde/istemci
  proxy'si erişemediğinde kırık görsel çıkıyordu. Çözüm: logo artık **postanın içine
  gömülüyor** — Resend inline attachment (`content_id: dvh-logo`,
  `/app/backend/assets/email-logo.png`, 460px/44KB) ve gövdede `src="cid:dvh-logo"`.
  `email_outbox`'a kaydedilen HTML'de cid yerine genel URL yazılıyor, böylece yönetici
  panelindeki e-posta önizlemesi bozulmuyor.
- **Konu satırları**: yeni yardımcı `emailer.subject_with_ref(ref, tail)` →
  "DV-XXXXXX başvuru nolu Dubai vize başvurunuz alındı". Uygulanan e-postalar: başvuru
  alındı, taslak kaydedildi/yarım kaldı, eksik belge, durum güncellemesi, vize hazır,
  ödeme alındı, havale bilgileri. Referans yoksa "Dubai vize başvurunuz …" olarak düşer.
  (Sipariş e-postaları "Siparişiniz alındı - SV-…" formatında kaldı.)
- **BUG: paket kartındaki düğme vizeyi sepete eklemiyordu.** Kullanıcı (a) seçeneğini seçti.
  `lib/cart.js` artık `visaTypeId` + `visaQty` tutuyor (`setVisa`, `setVisaQty`,
  `removeVisa`, sepet sayacı vizeyi de sayıyor). HomeBundleStrip düğmesi
  **"Paketi sepete ekle"** oldu ve vize + sigorta + eSIM ekliyor.
  `/sepet`: `cart-visa-line` (yolcu sayısı adımlayıcısı + kaldır), özet satırı
  `cart-visa-summary`, "Vize dahil tahmini toplam" `cart-grand-total`. Vize sepette
  olduğunda ödeme formu yerine `cart-visa-checkout-panel` çıkıyor
  ("Vize başvurusunu tamamla" → `/basvuru?vize=…&paket=…&sepet=1`, "Vizeyi çıkar…").
  `Apply.jsx` `?sepet=1` ile sepetteki sigorta/eSIM/tur seçimlerini forma taşıyor ve
  başvuru oluştuğunda sepeti boşaltıyor.
- **Karşılaştırma tablosu**: "Çocuk ücreti (0-17 yaş)" satırı eklendi (30 gün 2.470 ₺,
  60 gün 5.190 ₺, çok girişli kolonlarda "Çocuk vizesi tek girişlidir") + aile indirimi
  dipnotu (`visa-comparison-family-note`).
- Test: testing_agent iteration_100 → backend 100%, frontend 100%, sıfır bulgu.
  Yeni testler: `tests/test_iteration_100_emailer_logo.py`, `tests/test_iteration_100_e2e.py`.

## 2026-09-06 · Aile Paketi (2 yetişkin + 1 çocuk) ve çoklu vize sepeti
- **Yeni paket `pack_family`** (`routes_store.py` BUNDLE_TEMPLATES): 2 yetişkin 30 günlük
  vize + 1 çocuk 30 günlük vize + 3 sigorta (ins_15d) + 2 eSIM (esim_3gb).
  `bundle_list()` artık `quantities` (sigorta/eSIM adedi) ve `family` bloğu
  (adults, children, child_visa, visa_subtotal, visa_discount, traveler_count) döndürüyor;
  ekstralara %10 paket, vizelere %10 aile indirimi uygulanıyor →
  ekstralar 2.844 ₺, vize dahil toplam **14.409 ₺**.
- **Sepet çoklu vize satırını destekliyor**: `lib/cart.js` artık `visas: [{visa_type_id,
  quantity}]` tutuyor (`setVisas`, `setVisaQty(id, qty)`, `removeVisa(id)`), eski
  `visaTypeId/visaQty` biçimi otomatik göç ediyor. Test kimlikleri
  `cart-visa-line-{id}`, `cart-visa-qty-{id}`, `cart-visa-plus/minus/remove-{id}`.
- **Ana sayfa şeridi**: PICKS artık Standart · **Aile** · Uzun Konaklama. Aile kartında
  "2 YETİŞKİN + 1 ÇOCUK" etiketi, "Aile" badge'i, çocuk vizesi satırı, "× 2 / × 3" adet
  gösterimi ve "1.601 ₺ indirim (paket + aile)" var. "Paketi sepete ekle" 8 kalem ekliyor.
- **Sepet özeti**: `cart-family-discount` satırı (`/api/content/site` →
  `family_discount_tiers` ile hesaplanır) eklendi; böylece sepetteki "Vize dahil tahmini
  toplam" ana sayfadaki paket fiyatıyla birebir aynı (14.409 ₺).
- **Başvuru formu**: `/basvuru?vize=…&paket=…&sepet=1&yetiskin=2&cocuk=1` ile açıldığında
  2 yetişkin + 1 çocuk yolcu kartı otomatik oluşuyor, çocuğa çocuk vizesi atanıyor,
  sepetteki sigorta/eSIM adetleri forma taşınıyor.
- Test: testing_agent iteration_101 → backend %100 (6/6 pytest), frontend %100, sıfır bulgu.
  Yeni test: `tests/test_iteration_101_family_bundle.py`.

## 2026-09-06 · Dinamik Aile Paketi + "Tam tatil" çöl safarisi
- **Yeni endpoint `GET /api/bundles/quote`** (`bundle_id`, `adults` 1-6, `children` 0-4,
  `tour`): paketi yolcu sayısına göre yeniden fiyatlandırır. `routes_store._bundle_item()`
  yardımcısına çıkarıldı; `bundle_list()` de aynı yardımcıyı kullanıyor.
  Adet kuralları: sigorta = yolcu sayısı, eSIM = yetişkin sayısı, safari = yolcu sayısı.
  Paket indirimi (%10) **tur dahil** tüm ek hizmetlere uygulanıyor (sipariş fiyatlamasıyla
  birebir aynı), vize bedellerine yolcu sayısına göre %10/%15 aile indirimi.
- **Ana sayfa aile kartı etkileşimli** (`HomeBundleStrip.jsx` yeniden yazıldı: `Stepper` +
  `BundleCard`): Yetişkin/Çocuk adımlayıcıları ve "Tam tatil: N kişilik çöl safarisi ekle"
  kutusu; her değişiklikte fiyat, içerik listesi, indirim satırı ve alt başlık
  (`3 YETİŞKİN + 2 ÇOCUK · TAM TATİL`) 180 ms debounce ile sunucudan güncelleniyor.
  Örnek: 2+1 → 14.409 ₺, 2+1 + safari → 20.403 ₺, 3+2 + safari → 31.941,50 ₺.
- **Sepet ve başvuru formu birebir aynı tutarı gösteriyor**: kart → sepet
  (`cart-grand-total`) → `/basvuru?paket=…&yetiskin=…&cocuk=…&tur=1` özet toplamı
  31.941,50 ₺. Bunun için Apply'da tur seçili olup tarihi boşsa gidişin ertesi günü 15:00
  otomatik atanıyor (aksi halde tarihsiz tur fiyata girmiyordu — iteration_102 UX bulgusu).
- Test: testing_agent iteration_102 → backend %100 (9/9 pytest, sipariş fiyat paritesi
  dahil), frontend %100. Rapor sonrası tek UX bulgusu (kart↔form tutar farkı) giderildi ve
  doğrulandı. Yeni test: `tests/test_iteration_102_family_quote.py`.

## 2026-06-06 · Anlatımın MP4 reklam videosu (WhatsApp)
Kullanıcı isteği: "Ana sayfadaki animasyonu mp4 formatında yap WhatsApp'ta reklam olarak
gönderelim, en sonunda websitesini de göster".
- `scripts/render_explainer_video.py`: PIL ile sahne kareleri üretip ffmpeg ile birleştiriyor.
  Kaynaklar: `public/explainer/{key}.png` (7 sahne), `public/audio/explainer/full.mp3` +
  `full.json` (sahne pencereleri), `scripts/fonts/Figtree.ttf` (variable font, ExtraBold/
  Medium/SemiBold varyasyonları), `public/brand/logo-horizontal-gold-palm.png`.
  Kare düzeni: üstte logo → beyaz kartta illüstrasyon (`object-contain` mantığı, kırpma yok) →
  altın "ADIM X" rozeti → başlık → altyazı kutusu → sahne göstergesi + site adresi.
  Her sahne kendi süresinde (full.json start/end) Ken Burns zoompan + 0.4 sn fade-in.
  Kapanış (4,2 sn): logo + "Dubai vizeniz 2 iş gününde hazır" + www.dubaivizehatti.com
  pili + WhatsApp/telefon + TÜRSAB satırı; içerik saydam katmana çizilip **dikeyde
  ortalanıyor** (ilk denemede alt yarı boştu). Ses `apad` + `afade` ile kapanışa uzatılıyor.
  Geçici klasör (`tempfile.mkdtemp`) her koşuda `shutil.rmtree` ile siliniyor.
- Çıktılar: `public/reklam/dubai-vize-hatti-reklam-dikey.mp4` (1080x1920, 2,6 MB) ve
  `...-kare.mp4` (1080x1080, 2,1 MB) — ikisi de 70,94 sn, h264 + AAC mono 128k,
  `+faststart`. WhatsApp 16 MB sınırının çok altında.
- `public/reklam/index.html` (noindex): iki videoyu önizleyip indirme sayfası
  (telefonda uzun basıp kaydetme talimatı dahil).
- ORTAM NOTU: fork sonrası `ffmpeg` kurulu değildi → `apt-get install -y ffmpeg`
  (Debian 12, ffmpeg 5.1.9) ile kuruldu. Yeni pod/deploy'da script çalışmazsa ilk iş
  ffmpeg kurulumudur.
- Doğrulama: ffprobe (süre/çözünürlük/kodek/ses akışı), volumedetect (mean -15.4 dB,
  max -1.3 dB → ses sessiz değil), 3/25/45/68. saniye kareleri (25. sn = "upload" sahnesi
  20,95-30,85 penceresiyle uyumlu, 68. sn = kapanış karesi), preview URL'den
  `http=200 · video/mp4` ve indirme sayfası ekran görüntüsü.


## 2026-06-06 · Güvenlik denetimi turu 2 (security_audit_agent) — 3 bulgu + 2 sıkılaştırma DÜZELTİLDİ
Kullanıcı isteği: "Run the Security Audit on the deployed app." Denetim sonucu:
**CONDITIONAL PASS** (Critical/High yok). Önceki turda kapatılan maddeler doğrulandı ve hâlâ
kapalı: e-posta+soyad ile müşteri girişi kaldırılmış (yalnız OTP), Zami bookmarklet çıktısı
`dvoEsc` ile kaçışlı, dosya/handoff jetonları nesne bazlı HMAC + süreli (handoff 10 kullanım),
`JWT_SECRET` yedeği yok, admin karşılaştırması sabit zamanlı, fiyatlar her zaman sunucuda
hesaplanıyor, tüm admin route'larında `require_admin` var.

Düzeltilenler:
1. **SEC-001 (MEDIUM) İmzasız WhatsApp webhook kabul ediliyordu** — `wa_cloud.verify_signature`
   `app_secret` boşken `True` dönüyordu; kimliksiz biri sahte mesaj gönderip Claude yanıtları
   üretebiliyor (maliyet istismarı + uydurma sohbet kaydı) ve canlıda sahte tedarikçi belgesi
   akıtabilirdi. Artık **fail-closed**: secret yoksa veya imza geçersizse 403 +
   `wa_events` içine `webhook_rejected` kaydı. `GET /whatsapp/webhook` doğrulama anahtarı
   karşılaştırması `hmac.compare_digest` ile yapılıyor. Ek olarak
   `routes_whatsapp._webhook_rate_ok` (dakikada 120 olay, bellek içi kayan pencere) eklendi.
   Admin panelinde (`WaBotSettings.jsx`) App Secret girilmediğinde amber uyarı kutusu
   (`data-testid="wa-app-secret-warning"`): "imzasız webhook istekleri reddedilir, bot şu an
   gelen mesajları işlemez". `wa_cloud.config()` artık `signature_ready` alanı döndürüyor.
   NOT: Bot canlıya alınırken Meta App Secret'ın girilmesi ARTIK ZORUNLU.
2. **SEC-002 (LOW) Yönetici tek kullanımlık kodu düz metin saklanıyordu** — `code_plain` alanı
   kaldırıldı (her yazımda `$unset`), e-posta konusundan kod çıkarıldı
   ("Yönetici giriş kodunuz"). Kod yalnız `code_hash` olarak saklanıyor; testler kodu
   `email_outbox` HTML gövdesinden okuyor (müşteri OTP'siyle aynı yöntem).
   Mevcut kayıtlardaki `code_plain` alanları DB'den temizlendi.
   `tests/test_iteration_82/83/91` ve `memory/test_credentials.md` bu yönteme güncellendi.
3. **SEC-003 (LOW) İşlemsel e-postalarda HTML/bağlantı enjeksiyonu** — `emailer.esc()`
   (html.escape) eklendi ve kullanıcı girdisinin geçtiği tüm yerlere uygulandı:
   `_contact_name`, `_contact_email`, `_travelers_table`, `admin_notify_html`,
   `contact_admin_html` (ad/e-posta/telefon/konu/mesaj), sipariş şablonları
   (oluşturuldu/admin/teslim), `visa_ready` admin notu, `_draft_name` + `_draft_info_rows`,
   `cart_reminder_html`, ürün satırı adları. `_row()` içine kaçış EKLENMEDİ (tek bir
   `<strong>Toplam</strong>` satırı HTML geçiyor) — kaçış veri kaynağında yapılıyor.
4. **P3 Takip kodu taranabilirliği** — `_find_application_for_tracking` artık "kod yok" ve
   "soyad eşleşmiyor" için aynı 404 mesajını döndürüyor.
5. **P3 WhatsApp bot durum sorgusu** — `wa_bot`: başvuruda telefon kayıtlı değilse doğrulama
   atlanıyordu; artık **telefon eşleşmesi VEYA soyad** şart (`phone_ok or surname_ok`).

Kabul edilen kalanlar (P3): `email_outbox` gönderilen postanın tam HTML'ini (dolayısıyla OTP
kodunu) saklıyor — posta günlüğü olarak bilinçli tercih, test akışları buna dayanıyor;
`.env` içindeki kullanılmayan `ADMIN_LOGIN_PASSWORD` (yalnız `test_iteration_80.py` okuyor);
CORS `allow_credentials` + alt alan adı regex'i (yıldız yok, allowlist dar tutulacak).

Doğrulama: `testing_agent` iteration_103 → backend **12/12**, frontend %100
(`/app/backend/tests/test_security_audit_fixes.py` yeni kalıcı regresyon paketi).
Ayrıca ajan kendi doğrulaması: imzasız/bozuk imzalı webhook 403, doğru verify_token 200 + challenge,
admin OTP akışı uçtan uca (kod yok → hash var, konuda kod yok, gövdedeki kodla giriş 200),
takip 404 mesajları aynı, `pytest tests/test_emailer.py` 7/7.
Bakım: eski `tests/test_bundles.py` ve `test_iteration_101` beklentileri `pack_family`
eklendiğinden güncellendi (güvenlikle ilgisiz, bayat testler).


## 2026-06-06 · Rakip analizi (dubaivize.com) + "Paket 1 – Güven & Fiyat"
Kullanıcı isteği: "https://dubaivize.com/ incele ve bizim sitede olan eksikleri tespit et".
Rakip sitesi (Birtek Turizm, TÜRSAB 6169) tarandı: `/`, `/dubai-vize-ucreti`,
`/vize-tipleri/dubai-vizesi-30-gun-tek-giris`, `/basvuru-rehberi`, `/iletisim`.
Fiyatları bizden yüksek ($130 vs $105) ve 7 belge istiyorlar (uçak bileti + otel + kimlik
ön/arka + pasaport kapağı dahil); bizim "2 belge" avantajımız korunuyor.

Tespit edilen eksikler (kullanıcıya sunuldu): TÜRSAB no "0000", yasal acente uyarısı,
ödeme güven şeridi, içerik künyeleri, `/dubai-vize-ucreti` fiyat sayfası, `/basvuru-rehberi`,
vize detayında 58 gün giriş kuralı + kimler başvuramaz + süre aşımı cezası + mobil sabit CTA,
belge bazlı örnek görseller, yabancı uyruklu başvuru (Türkiye'de oturumlu expat pazarı),
SMS bildirimi, iletişim formunda captcha, KVKK veri silme akışı.

Kullanıcı kararları: **Paket 1** seçildi; sigorta konumlandırması "zorunlu değil ama şiddetle
öneriyoruz" olarak KALACAK (yasal risk almıyoruz); SMS şimdilik YOK (WhatsApp botu yeterli);
TÜRSAB/vergi bilgileri sorusunu atladı → numaralar sitede tamamen gizlendi.

Yapılanlar:
- `content.py` COMPANY: `tursab_no`, `tax_no`, `mersis_no`, `trade_registry_no` varsayılanları
  "0000..." yerine **boş string**. `routes_public._agency_info`: "Vergi Dairesi / No" satırı
  yalnız ikisi de doluysa gösteriliyor (önceden yalnız daire adı kalıyordu).
  `TursabBadge` boş numarada zaten gizleniyor → sitede hiçbir yerde "Belge No: 0000" yok.
- `lib/site.js`: `AGENCY_DISCLAIMER` ("Yetkili özel seyahat acentesiyiz; resmî bir devlet
  kurumu, konsolosluk ya da BAE göç idaresi değiliz..."), `CONTENT_AUTHOR`,
  `CONTENT_UPDATED_AT` (= "Haziran 2026", içerik güncellendikçe elle artırılır),
  `OFFICIAL_SOURCES` (gdrfad.gov.ae, icp.gov.ae).
- Yeni `components/PaymentTrustStrip.jsx`: 3D Secure + Visa/Mastercard/troy amblemleri
  (inline SVG, marka dosyası indirilmedi) + Havale/EFT + "kart bilgileriniz saklanmaz".
  `/dubai-vize-ucreti` ve `/vize-tipleri` sayfalarında.
- Yeni `components/ContentByline.jsx`: hazırlayan + son güncelleme + resmî kaynak linkleri +
  yasal uyarı. `/dubai-vize-ucreti`, `/gerekli-belgeler`, `/sss`, `/vize-tipleri`,
  `/dubai-vizesi/:slug` sayfalarında (E-E-A-T sinyali).
- `Footer.jsx`: yeni `footer-fees-link` ve alt bilgide `footer-disclaimer` bloğu.
- Yeni sayfa **`/dubai-vize-ucreti`** (`pages/VisaFees.jsx`, `Navbar` PRIMARY_LINKS'te
  "Vize Ücretleri"): 4 grup halinde fiyat tabloları (tek/çok giriş, çocuk, uzatma) TRY + ≈USD,
  satır başına "Başvur" → `/basvuru?vize=<id>` (ön seçim çalışıyor), aile indirimi notu,
  ekspres/anında ekspres kartları, sigorta-eSIM-tur çapraz satış "…'den başlayan" fiyatları
  (`/api/products` içinden en ucuzu), ücrete dahil/dahil olmayanlar, ücreti belirleyen
  faktörler, ödeme & güvenlik (fiyat kilidi vurgusu + banka hesapları), iptal-iade özeti,
  7 soruluk SSS + **FAQPage JSON-LD**, içerik künyesi, kapanış CTA.
  Başlangıç fiyatı **yetişkin** vizesinden hesaplanır (çocuk fiyatı yanıltıcı olurdu);
  `popular` rozeti çocuk satırlarında gizlendi.
- `public/sitemap.xml` ve `robots.txt`: alan adı **dubaivizeonline.com → dubaivizehatti.com**
  (eski domain SEO'yu bölüyordu), `/dubai-vize-ucreti`, `/dubai-turlari`, `/basvuru`,
  `/gizlilik-politikasi`, `/ticari-ileti-onami` eklendi; `/hesabim` ve `/sepet` disallow.
- Doğrulama: `testing_agent` iteration_104 → frontend %100, backend spot check %100
  (fiyatlar `/api/visa-types` ile birebir, JSON-LD geçerli, placeholder yok, 390px mobil düzen
  bozulmuyor, konsol hatası yok).

## 2026-06-06 · Başvuru e-postaları neden gelmiyordu (KÖK NEDEN BULUNDU, kullanıcı aksiyonu bekliyor)
Şikayet: "basvurular emaille bana gelmiyor".
Teşhis zinciri: `email_outbox` kayıtları `status=sent` görünüyordu → Resend API
`GET /emails/{id}` ile teslim durumu sorgulandı → `last_event=**suppressed**` →
suppression listesi çekildi: `info@dubaivizehatti.com`, `origin=bounce`, 2026-09-06 16:13 UTC.
Adres listeden silindi, test postası atıldı → **anında `bounced`**;
`bounce.diagnosticCode`: `550-5.1.1 The email account that you tried to reach does not exist`
(gsmtp). DNS kontrolü: MX → SMTP.GOOGLE.com, DKIM `resend._domainkey` var, SPF/DMARC var,
Resend'de domain `verified` → **eksik olan tek şey Google Workspace'te info@ kutusunun kendisi.**
Her bounce sonrası Resend adresi tekrar suppression listesine ekliyor → tüm bildirimler sessiz
kayboluyor. İkincil bulgu: son 24 saatte 76 gönderim "daily email sending quota" hatası
(Resend ücretsiz plan 100/gün) — testler yüzünden dolmuş, gerçek trafikte de risk.
Çözüm kullanıcıda: (a) `info@dubaivizehatti.com` kutusunu Google Workspace'te açmak veya
(b) `ADMIN_EMAIL`'i gerçekten okunan bir adrese çevirmek. Kullanıcı henüz yanıtlamadı.
Öneri (henüz yapılmadı): gönderim sonrası Resend `last_event` yoklayıp Admin → E-postalar
ekranında "teslim edilemedi" uyarısı göstermek.


## 2026-06-09 · Hizmet Bedelleri birleştirme + dönen WhatsApp sohbetleri + blurlu Türk pasaportu
Kullanıcı istekleri (onaylı seçenekler: tek sayfa birleştirme, otomatik dönen sohbetler,
4 senaryo, bordo Türk pasaportu blurlu):
- **Sayfa birleştirme (SEO)**: `pages/VisaFees.jsx` SİLİNDİ; içeriği yeniden yazılarak
  `pages/VisaTypes.jsx` ("Hizmet Bedelleri") altına taşındı — 01 Güncel bedeller
  (PricingTabs + VisaComparison) · 02 Bedelin kapsamı (dahil / dahil olmayan / bedeli
  belirleyen 4 unsur / sepete eklenebilir hizmetler) · 03 Ödeme & güvenlik
  (PaymentTrustStrip, kartla ödeme, havale, tutar kilidi, iade özeti) · 04 Rehberler ·
  05 SSS (7 yeni soru + FAQPage JSON-LD). Metinlerin tamamı yeniden yazıldı (kopya değil).
  `/dubai-vize-ucreti` artık `<Navigate to="/vize-tipleri" replace />`; Navbar'daki
  "Vize Ücretleri" kaydı ve `Receipt` importu kaldırıldı, Footer tek "Hizmet Bedelleri"
  linkine indi (`footer-fees-link`), `public/sitemap.xml`'den eski URL çıkarıldı.
- **WhatsAppPhoneMock: 4 dönen senaryo**: passport (pasaport süresi + aile indirimi,
  blurlu Türk pasaportu fotoğrafı), express (yarın uçuş → anında ekspres), ticket
  (bilet/otel şartı yok + ödeme linki kartı), delivery (vize PDF teslimi + eSIM önerisi).
  6.8 sn'de otomatik geçiş, hover'da durur, açılışta **rastgele** senaryo, altta nokta
  kontrolleri (`wa-chat-dot-{i}`), senaryo etiketi (`wa-chat-label`), sohbet alanı
  `min-h-[452px]` ile zıplama engellendi. Yeni mesaj tipleri: `image`, `doc`, `link`.
- **Görsel**: `public/chat/passport-tr.jpg` — Gemini 3.1 Flash Image ile üretilen bordo
  "TÜRKİYE CUMHURİYETİ / PASAPORT" kapağı + açık kimlik sayfası; isim, numara ve MRZ
  satırları okunamayacak şekilde bulanık.
- **BUG FIX (kullanıcı: "bunu kaldır" + dev WhatsApp ikonu ekran görüntüsü)**: Kök neden
  Tailwind'de `4.5` spacing tanımlı olmaması — lucide ikonları width/height attribute'una
  düştüğü için etkilenmiyordu, ancak `WhatsAppIcon` gibi yalnız viewBox içeren özel SVG'ler
  kapsayıcıyı doldurup 472px'e büyüyordu (`AskFirstSection` not kutusu). Çözüm: ikon
  `h-5 w-5` yapıldı **ve** `tailwind.config.js` → `theme.extend.spacing["4.5"] = 1.125rem`
  eklendi (koddaki ~24 `h-4.5/w-4.5` kullanımı artık gerçekten 18px).
- Doğrulama (self-test, screenshot + DOM ölçümü): sayfadaki en büyük SVG 92px (bayraklar),
  dot-2 → "Bilet & otel şartı", 8 sn sonra otomatik "Vize teslimi", pasaport görseli
  sohbette render ediliyor, `/dubai-vize-ucreti` → `/vize-tipleri` yönleniyor, birleşik
  sayfada 7 bölüm test-id'si mevcut.


### 2026-06-09 · Admin e-posta sorunu ÇÖZÜLDÜ + telefon maketi rötuşu
- **Admin e-postası (P0, birden fazla oturum bekliyordu) çözüldü**: SMTP sondasıyla
  doğrulandı — `smtp.google.com` artık `info@dubaivizehatti.com` için `250 2.1.5 OK`
  dönüyor (uydurma adres hâlâ `550 5.1.1`), yani kullanıcı kutuyu açmış. Tek kalan engel
  Resend'in **suppression** kaydıydı (06.09 20:26'daki hard bounce nedeniyle otomatik
  eklenmişti) — `DELETE https://api.resend.com/suppressions/info@dubaivizehatti.com` ile
  silindi. Doğrulama: doğrudan test postası `last_event: delivered`, ardından gerçek uygulama
  akışı (`POST /api/contact` → `contact_message`) `email_outbox: sent` +
  `Resend last_event: delivered`. Test kaydı DB'den silindi.
  NOT: adres yeniden bounce/spam alırsa Resend tekrar suppress eder; aynı DELETE çağrısı yeterli.
- **Telefon maketi (kullanıcı: "soldan sağa çok geniş, sağa doğru eğik olsun")**:
  `WhatsAppPhoneMock` genişliği 368px → **304px**, çerçeve `border-[9px]` + köşeler 2.4rem,
  gövde `motion.div` ile **6° sağa eğik** (`origin-bottom`), hover'da doğrulup hafif büyüyor
  (rotate 0 + scale 1.015). Nokta kontrolleri ve etiket eğimden bağımsız, üst boşluk `mt-8`.

- **Telefon boyu kısaltıldı (kullanıcı: "yukarıdan aşağıya çok uzun")**: sohbet alanı
  `min-h` 452 → **330px**, pasaport görseli 136 → **100px**, dikey padding `py-2.5`;
  4 senaryonun mesajları 5-6 kısa balona indirildi (uzun cümleler sadeleştirildi).
  Ölçüm: senaryo yükseklikleri 622-690px arası (önce 736+), 304px genişlik + 6° eğim korunuyor.


## 2026-06-09 · Kod inceleme raporu turu (uygulananlar + doğrulanan yanlış pozitifler)
**Uygulananlar**
- `routes_store._bundle_item` (karmaşıklık 33, ~120 satır) **4 yardımcıya bölündü**:
  `_bundle_counts` (yolcu sayıları), `_pick_bundle_visas` (yetişkin/çocuk vize seçimi,
  tek `cheapest` yardımcısı), `_bundle_totals` (ek hizmet + vize tutarları, paket ve aile
  indirimi), `_bundle_family_block` (aile kırılımı). Ana fonksiyon artık yalnız birleştiriyor.
  **Regresyon: çıktı bire bir aynı** — `/api/bundles`, `?visa_days=30`, `?visa_days=60` ve
  3 `/api/bundles/quote` yanıtı refactor öncesi/sonrası JSON olarak karşılaştırıldı (6/6 IDENTICAL);
  ayrıca `pack_family` (2 yetişkin + 2 çocuk + tur) tutarları elle doğrulandı
  (12.600 liste → %10 paket indirimi → 11.340; vize 15.320 → %15 aile indirimi → 24.362 toplam).
- `routes_public`: `/passport/read` ve `/files/{id}` içindeki tekrarlanan upload
  arama + object storage okuma bloğu `_get_upload_record()` ve `_read_upload_bytes()`
  yardımcılarına çıkarıldı (DRY + `read_passport_document` kısaldı). Davranış aynı:
  bogus id → `/passport/read` 404, `/files/{id}` 403 (jeton kontrolü önce) doğrulandı.
- `ruff --select F401 --fix`: 10 kullanılmayan import silindi (9 test dosyası + `wa_bot.py`).
- Tip ipucu kapsamı: `regression_critical_tests.py`, `tests/test_insurance_automation.py`,
  `tests/test_bundles.py`, `tests/test_emailer.py` içindeki **27 test fonksiyonuna `-> None`**
  eklendi (değer döndüren fixture'lara dokunulmadı).
**Yanlış pozitifler (ruff + grep ile doğrulandı, kod değişikliği gerekmedi)**
- "zami_rpa.py:90 exec() güvenlik açığı" → satır `await asyncio.create_subprocess_exec(...)`;
  projede hiçbir yerde `exec(`/`eval(` yok (grep temiz).
- "11 tanımsız değişken" → `ruff --select F821` = 0.
- "141 `is` ile literal karşılaştırma" → `ruff --select F632,E711,E712` = 0; rapordaki tüm
  satırlar `is None` / `is not None` (doğru kullanım).
- `_build_application_doc` (51 satır) → dallanması olmayan düz sözlük eşlemesi; bölmek
  yalnız dolaylılık ekler, risk azaltmaz → değiştirilmedi.
- `routes_admin.py` 33 import / modül bölme → çalışan yönetici uçlarını riske atacağı ve
  kullanıcıya değer katmayacağı için yapılmadı (istenirse ayrı bir tur olarak planlanabilir).
**Test durumu**: `pytest tests -q -n0` → 263 passed, 1 skipped; 4 failed + 1 error
(retention tombstone, tours snapshot, 2 zami session alert, stripe cart) — bunlar
**refactor öncesinde de** başarısız (git stash ile doğrulandı), tek tek çalıştırıldığında
geçiyorlar; kök neden test izolasyonu/paylaşılan event loop (mevcut teknik borç).

### Telefon maketi mobil incelik (kullanıcı: "cep telefonundan kalın gözüküyor")
`WhatsAppPhoneMock` genişliği mobilde **244px**, `sm:` üstünde 300px oldu; 244px'te
başlık taşmasın diye görüntülü/sesli arama ikonları küçük ekranlarda gizlendi
(`hidden sm:block` / `min-[380px]:block`) ve "Mesaj yazın" tek satıra sabitlendi.
390px'te ölçüldü: kart genişliği 244px, düzen bozulmuyor.


## 2026-06-09 · Telefon maketi 4 sohbete indi + pasaport kimlik sayfası görseli
- `WhatsAppPhoneMock.jsx` senaryoları 6 → **4**: (1) WhatsApp'tan başvuru,
  (2) Yeşil/bordo pasaport, (3) **eSIM ve seyahat sigortası** (yeni: eSIM QR, TR numarası
  açık kalır, 30 günlük poliçe 644 ₺, vize+eSIM+sigorta paketinde %10 indirim link kartı),
  (4) Aile ve çocuklar. "Pasaport bende kalıyor", "Süre ve ödeme" ve "Vize teslimi ve takip"
  senaryoları kaldırıldı; kullanılmayan PDF (`doc`) baloncuk tipi ve `FileText` importu silindi.
- **Pasaport görseli**: kullanıcı isteği "sadece kimlik sayfası tam görünsün" →
  Gemini ile Türk pasaportu **kimlik/bio sayfası** üretildi, alan değerleri ve MRZ bandı
  PIL ile yumuşak maskeyle bulanıklaştırıldı → `public/chat/passport-bio.jpg`.
  Baloncuktaki `object-cover h-[100px]` yerine `object-contain w-full` (kırpma yok).

## 2026-06-09 · Kırılgan backend testleri: kök neden bulundu, suite %100 yeşil
- **Kök neden**: `tests/test_iteration_82.py` test ortasında 3 kez
  `sudo supervisorctl restart backend` çağırıyordu. `pytest.ini` `-n 2 --dist loadscope`
  ile çalıştığı için, backend yeniden başlarken **diğer worker'daki tüm istekler 502**
  alıyordu (22 failed). İkinci hata: aynı dosya grubunda `.env` elle parse edilirken
  tırnaklar temizlenmiyordu → `pymongo InvalidURI` (`"mongodb://..."`).
- **Düzeltmeler**:
  - Testlerden supervisor yeniden başlatmaları kaldırıldı.
  - IP başına saatlik bellek içi sayaçları tüketen 2 test (`/account/request-code` 15/sa,
    `/contact` 8/sa) `@shared_limit` ile **varsayılan olarak atlanıyor**; ayrı çalıştırma:
    `RUN_RATELIMIT_TESTS=1 python -m pytest tests/test_iteration_82.py -n 0`.
  - İzole modda oturum sonunda backend bir kez yeniden başlatılıp `/api/products` 200
    olana kadar beklenerek sayaçlar sıfırlanıyor → sonraki suite çalışmaları 429 almıyor.
  - `test_iteration_94_cart.py` artık `os.environ["MONGO_URL"]` kullanıyor (conftest dotenv).
- **Sonuç**: `pytest tests -q` → **271 passed, 3 skipped, 0 failed** (izole grup
  çalıştırıldıktan hemen sonra tekrar çalıştırılıp doğrulandı).

## 2026-09-07 · Kur kaynağı TCMB günlük bülteni (USD döviz satış)
Kullanıcı isteği: "https://www.tcmb.gov.tr/... döviz kurunu buradan günlük çek,
USD döviz satış kuru olacak".
- `fx.py`: **birincil kaynak TCMB** `kurlar/today.xml` → `parse_tcmb_xml()` USD bloğundaki
  **`<ForexSelling>`** (döviz satış) değerini okur (yoksa `BanknoteSelling`),
  `parse_tcmb_date()` bülten tarihini ISO olarak döndürür. Kaynak etiketi
  **"TCMB döviz satış"**. Yedekler sırayla: Yahoo `USDTRY=X`, doviz.com, open.er-api,
  exchangerate.host.
- **Günlük tazeleme**: `expected_bulletin_date()` — bülten iş günü 15:30'da yayınlandığı için
  16:00'dan önce önceki iş gününü, hafta sonunda cumayı döndürür. `_is_stale(state)` artık
  24 saatlik yaşın yanında **bülten tarihini** de kontrol ediyor: kayıtlı bülten beklenenden
  eskiyse (veya kur yedek kaynaktan geldiyse) saatte bir yeniden denenir → yeni bülten
  yayınlandığı gün otomatik yakalanır. Kayıtta yeni `bulletin_date` alanı tutuluyor.
- `GET /api/fx` yanıtına `bulletin_date` eklendi; `components/FxNote.jsx` artık
  "1 $ = 49,40 ₺ · TCMB döviz satış · 07.09.2026 bülteni" yazıyor (manuel kurda eski metin).
- Marj (%2, admin panelinden) aynen korundu: 48,4336 × 1,02 = **49,4023 ₺**
  (eski Yahoo kuruyla 49,38 ₺ idi; vize fiyatları 10 ₺'ye yuvarlandığı için değişmedi).
- Test: `backend/tests/test_fx_tcmb.py` (11 test: parse, bülten takvimi, tazeleme kuralı,
  canlı `/api/fx` yanıtı) + fiyat regresyonu `test_iteration_48`, `test_bundles`,
  `test_insurance_catalog`, `test_iteration_101/102` → 35 passed. Ekran görüntüsüyle
  `/vize-tipleri` kur notu doğrulandı.

## 2026-09-07 (2) · Başvuru formu PDF'i + e-postaya evrak ekleri
Kullanıcı isteği: "Yüklenen evrakları müşteriye e-postayla gönder, sisteme de gönder;
başvuru detaylarını tek sayfalık forma geçir, 'detaylarınızı ekte bulabilirsiniz' diyelim."
- **`backend/application_pdf.py` (yeni)**: reportlab ile **tek sayfalık "Vize Başvuru Formu"**
  (logo + altın çizgi, takip kodu/ödeme durumu/sonuçlanma bandı, iletişim, seyahat bilgileri,
  yolcu tablosu (ad, doğum t., pasaport no, geçerlilik, vize, tutar), hizmet bedeli dökümü,
  yüklenen belgeler, künye). Türkçe glifler için Liberation Sans TTF kaydedilir; yazı tipinde
  ₺ glifi olmadığı için tutarlar "5.190,00 TL" olarak yazılır (`money()` sarmalayıcı).
- **`backend/application_docs.py` (yeni)**: `_targets()` her yolcunun pasaport + vesikalığını,
  uçak bileti/otel/diğer evrakları etiketleyerek toplar; `collect_application_documents()`
  içerikleri object storage'dan okur (**18 MB bütçe**; aşan dosya eke girmez, e-postada
  imzalı indirme bağlantısı olarak listelenir); `application_email_bundle()` ek listesini +
  gövde dökümünü, `application_form_bytes()` indirme için PDF üretir.
- **`emailer.py`**: `send_email(..., attachments=[{filename, content, content_type}])` desteği
  (Resend; inline logo ile birlikte gönderilir), `_attachment_list_html()` → gövdede
  **"Ekteki belgeler"** kutusu, `applicant_received_html` / `admin_notify_html` artık belge
  listesi alıyor. Müşteri metni: "Başvuru detaylarınızı ve yüklediğiniz evrakları bu
  e-postanın ekinde bulabilirsiniz." `email_outbox.meta.attachments` ek adlarını saklıyor.
- **Akış**: `routes_public._send_application_emails()` başvuru oluşunca hem müşteriye hem
  `ADMIN_EMAIL`e (sisteme) aynı PDF + evrakları ekliyor. Ekler hazırlanamazsa e-posta yine
  gidiyor (try/except).
- **İndirme uçları**: `GET /api/applications/form.pdf?code=&last_name=` (takip kodu + soyad
  doğrulaması, yanlışta 404) ve `GET /api/admin/applications/{id}/form.pdf` (`require_admin`,
  jetonsuz 401). UI: `/takip` sonuç kartında `tracking-download-form-button`, yönetici
  başvuru detayında `admin-download-form-button` (blob indirme).
- Test: `tests/test_iteration_112_application_form.py` (9) + testing_agent'ın eklediği
  `tests/test_iteration_112_extras.py` (6) → **15/15 PASS**, iteration_112 raporu
  backend %100 / frontend %100, sıfır bulgu. 3 yolculu (2 yetişkin + 1 çocuk) başvuruda
  6 evrak + bilet + otel ekleniyor; PDF poppler ile tek sayfa doğrulandı. Test verileri silindi.
- Not: reportlab (5.0.1) requirements.txt'e eklendi; PDF önizlemesi için `poppler-utils`
  kuruldu (yalnız geliştirme aracı, üretimde gerekli değil).

### Mesaj temizliği + yönetici giriş yer tutucusu (2026-09-07)
- Kullanıcı isteği: "yönetici panelindeki tüm mesajları silelim" → `contact_messages`
  koleksiyonundaki **27 kayıt silindi** (tamamı regresyon testlerinden kalan TEST/example.com
  kaydıydı; gerçek müşteri mesajı yoktu). `/admin/mesajlar` artık "Henüz mesaj yok" gösteriyor,
  menüdeki okunmamış rozeti sıfırlandı (`/api/admin/stats → unread_messages: 0`).
- Dokunulmayanlar: `email_outbox` (1602 gönderim arşivi), `notifications` (9 poliçe kesim
  hatırlatması — hepsi hâlâ var olan SV- siparişlerine ait), `wa_conversations`/`wa_messages`
  (1 konuşma / 16 mesaj).
- Yan bulgu düzeltildi: `AdminLogin.jsx` e-posta yer tutucusu hâlâ eski markayı
  (`info@dubaivizeonline.com`) gösteriyordu → `info@dubaivizehatti.com`. `routes_admin.py`
  ve `admin_test_token.py` içindeki `ADMIN_LOGIN_EMAIL` yedek değerleri de yeni markaya çevrildi.

### Tam test verisi temizliği (2026-09-07)
Kullanıcı: "tamamen silelim içini · tüm test kayıtlarını sil" → yeni betik
`scripts/wipe_test_data.py` (dry-run varsayılan, `--apply` ile siler). `KEEP_REFS` içindeki
gerçek kayıt zinciri (başvuru + bağlı sipariş + dosyaları + e-postaları + kayıtlı yolcusu)
ve tüm ayar/içerik koleksiyonları korunur.
- Silinen: 193 başvuru, 103 sipariş, 699 dosya kaydı, 1.596 e-posta arşivi,
  15 ödeme kaydı, 9 sigorta görevi, 88 kayıtlı yolcu, 9 bildirim, 1 iletişim mesajı,
  4 taslak, 96 müşteri + 1 yönetici giriş kodu, 28 OCR ölçümü, 131 Zami logu,
  1 WhatsApp konuşması + 16 mesaj + 24 olay + 14 gönderim logu, 695 ziyaret, 11 IP geo.
- Korunan: **DV-BJ930600 (Sedat Andic)** + siparişi SV-4GOGK7CT, 2 dosyası, 17 e-posta kaydı;
  site_settings (12), visa_types (10), store_products (12), articles (5), testimonials (6).
- Doğrulama: `/api/admin/stats` → `total: 1`, bugün 0, okunmamış mesaj 0, WhatsApp sayaçları 0;
  panel ekran görüntüsünde tek başvuru listeleniyor, "Pasaport okuma performansı" ve
  Mesajlar/Ziyaretçiler boş durum metinlerine düştü.
- NOT: Regresyon suite'i (`test_iteration_105`, `test_travel_rules` vb.) çalıştırıldığında yeni
  TEST kayıtları oluşur; panel temiz kalsın diye test sonrası betik tekrar çalıştırılmalı.

## 2026-09-07 (4) · Kod kalitesi raporu: doğrulama + karmaşıklık azaltma
Kullanıcı otomatik bir kod kalitesi raporu iletti. Bulgular tek tek doğrulandı:
- **YANLIŞ POZİTİF · "exec() kritik güvenlik açığı" (`zami_rpa.py:90`)**: satır
  `asyncio.create_subprocess_exec(sys.executable, "-m", "playwright", "install", "chromium")`
  — sabit argv, `shell=True` yok, kullanıcı girdisi yok. Kodda hiçbir `exec()`/`eval()` yok.
- **YANLIŞ POZİTİF · "12 tanımsız değişken"**: `ruff --select F` (F821 dahil) ve
  `pylint E0601/E0602/E0606` sıfır bulgu veriyor.
- **YANLIŞ POZİTİF · "151 yerde `==` yerine `is`"**: raporun işaret ettiği tüm satırlar
  (`zami_rpa.py:150,169,519,583,623`, `zami.py:151,417,793`, `whatsapp.py:119,332,337`)
  `is None` karşılaştırması; `ruff --select F632,E711,E712` temiz. Değişiklik yapılmadı.
- **GEÇERLİ · Karmaşıklık** (davranış korunarak sadeleştirildi):
  - `fx.fetch_live_rate`: yeni `_parse_source()` ile kaynak dağıtımı ayrıldı, guard clause'larla
    iç içe yapı düzleştirildi.
  - `application_pdf._pricing_rows`: `_discount_row()` + `_extras_rows()` olarak bölündü.
  - `zami_rpa.check_status` (22 → <12): `_status_search()`, `_read_status_text()` +
    `ROW_TEXT_JS` sabiti.
  - `zami_rpa.set_value` (20 → <10): `_is_editable`, `_select_option`, `_check_radio_group`,
    `_check_box`, `_fill_text` modül seviyesine çıkarıldı (checkbox kapalıysa "eksik alan"
    sayılmama davranışı korundu).
  - `zami_rpa.fill_application` (49 → 27): `_collect_manual_pending()`,
    `_run_portal_validation()`, `_submit_form()` + `VALIDATION_TEXT_JS`. Kalan 27, doğrusal
    akış (git → doldur → yükle → doğrula → gönder → logla) olduğu için kabul edildi.
- **Yapılmayanlar (bilinçli)**: `emailer.daily_digest_html`/`send_email`,
  `daily_digest._extras_breakdown` ve `backend_test.py` test fonksiyonlarının bölünmesi —
  ruff/mccabe bunları 12'nin altında ölçüyor, çalışan ve testli kodda gereksiz churn.
- Doğrulama: iteration_114 raporu → **302 passed / 3 skipped / 0 failed**, backend %100,
  frontend %100, sıfır bulgu (FX TCMB 49,4023 · fiyatlar değişmedi · Zami uçları 200/422,
  500 yok · panel karşılama kartı ve PDF indirme çalışıyor).

## 2026-09-07 (3) · Panel karşılama kartı (bugünün özeti + hızlı kısayollar)

- **Backend** `daily_digest.today_overview()` (yeni): bugünün (Europe/Istanbul) başvuru/yolcu/
  sipariş sayısı, bugünkü tahsilat (`_revenue`), `_attention()` (eksik belge, havale onayı,
  terk edilmiş sepet) + yeni `policy_tasks` (bekleyen poliçe kesimi), `_upcoming_departures()`
  (7 gün içinde gidişi olan açık başvurular), `pending_total`, `has_activity`, Türkçe
  `day_label` ve saate göre `greeting` (Günaydın/İyi günler/İyi akşamlar).
  Uç nokta: `GET /api/admin/today` (`require_admin`, jetonsuz 401).
- **Frontend** `components/AdminWelcomeCard.jsx` (yeni), `/admin` sayfasının en üstünde:
  tarih + selamlama, tek satır özet ("Bugün henüz yeni başvuru yok · 3 iş sizi bekliyor."),
  4 metrik (bugün gelen, bugünkü yolcu, bugünkü tahsilat, bekleyen iş), tıklanabilir bekleyen
  iş rozetleri (havale onayı → ödeme filtresi, eksik belge → durum filtresi, okunmamış mesaj,
  WhatsApp işlemi, poliçe kesimi; sepet ve uçuş rozetleri bilgi amaçlı) ve 6 hızlı kısayol
  (Ödeme bekleyenler, Eksik belgeliler, WhatsApp, Sigorta poliçeleri, eSIM & Sigorta,
  Ziyaretçiler). Sakin günde metin "Bugün panel sakin…" olur.
  test-id'ler: `admin-welcome-card|greeting|summary`, `admin-welcome-metric-{key}`,
  `admin-welcome-pending-{key}`, `admin-welcome-action-{key}`.
- KPI şeridindeki "Bugün gelen" kartı kaldırıldı (karşılama kartıyla tekrar ediyordu),
  yerine **Toplam başvuru** geldi.
- Doğrulama: `tests/test_iteration_113_admin_today.py` 5/5 PASS (selamlama saatleri, Türkçe
  gün etiketi, yerel gün sınırları, 401, alan/uyum kontrolleri); masaüstü (1600px) ve mobil
  (414px, yatay taşma yok, kart 604px) ekran görüntüleri; "Ödeme bekleyenler" kısayolu ödeme
  filtresini "Ödeme bekliyor"a çeviriyor.

## 2026-09-07 (4) · Tamamliyo seyahat sağlık sigortası CANLI + ekspres/telefon/UI düzenlemeleri

### Tamamliyo entegrasyonu tamamlandı (canlı)
- **Anahtarlar girildi**: `backend/.env` → `TAMAMLIYO_BASE_URL=https://api.tamamliyo.com`,
  `TAMAMLIYO_TOKEN` (partner token, kullanıcı panelinden aldı). Bağlantı doğrulandı:
  4 üründe `fiyat-al` 200 döndü, maliyetler DB'ye yazıldı (ins_7d 244,85 · ins_15d 279,74 ·
  ins_30d 296,63 · ins_60d 367,55 ₺) ve **%100 marj** ile satış fiyatı üretildi
  (490 / 560 / 590 / 740 ₺, 10 TL'ye yuvarlanır). Senkron açılışta + 24 saatte bir.
- `routes_admin.py` lint hatası düzeltildi (`origin_from` → `_resolve_origin(None, request)`).
- **Panelden otomatik kesim anahtarı**: `insurance_provider.auto_issue_on()/set_auto_issue()`
  ayarı `site_settings.insurance_provider.value.auto_issue` içinde tutulur (env yedek),
  yeni uç `POST /api/admin/insurance/auto-issue`. Varsayılan **KAPALI** (ilk poliçe elle kesilir).
- **Admin → Sigorta Poliçeleri** (`AdminInsurance.jsx`): yeni `ProviderPanel`
  (`insurance-provider-panel`) — bağlantı durumu, son senkron, ürün kodu (141), otomatik kesim
  switch'i, "Fiyatları Tamamliyo'dan güncelle" butonu; görev kartlarında sigortalı listesi,
  `provider_error` ve **"Tamamliyo'dan poliçeyi kes ve gönder"** (`insurance-issue-provider-*`,
  teklif → cari ödeme onayı → poliçe → PDF, idempotent). Manuel PDF yükleme yedek olarak kaldı.
- **Sigortalı kimlik bilgileri (poliçe şartı)**: yeni `components/InsuredIdentityFields.jsx`.
  - `/basvuru` Adım 4: sigorta seçilince `insurance-identity-block` açılır, her yolcu için
    TC kimlik no (`insured-tckn-<key>`, pasaport OCR'ından ön dolu) — geçersizse gönderim
    engellenir. Payload artık `tc_kimlik_no` gönderiyor; backend `national_id`'yi de kabul eder.
  - `/sepet` (sigortayı tek başına alma): `cart-insured-block` — kişi başına ad-soyad + TCKN +
    doğum tarihi; sigorta varsa **gidiş tarihi zorunlu** (poliçe başlangıcı) — backend de doğrular.
- Testler: `tests/insured_data.py` (geçerli TCKN üretici) eklendi; eski sabit fiyat/6 ürün
  varsayan 10 test dosyası canlı tarifeye uyumlu hâle getirildi. **310 passed / 3 skipped**.

### Ekspres hizmet sadeleştirildi (kullanıcı isteği)
- "Yaklaşık 8 mesai saati" ibaresi **"12 saat içinde"** oldu (content.py ADDONS/SERVICES/FAQ/
  yorum, visa_guides, routes_public.processing_days, VisaTypes, EasyCompare, AnnouncementTicker,
  HeroBannerSlider, test_iteration_48).
- **"Anında Ekspres Vize" (instant_express) tamamen kaldırıldı**: content.py ADDONS + SERVICES,
  `models.AddonsIn`, `_addon_lines` karşılıklı kapatma mantığı, `Apply.jsx` ek hizmet kartları.
- **Ekspres Vize Hizmeti kartı vize özet kartı tasarımına geçti**: yeni `components/AddonCard.jsx`
  (üst şerit, "Ek hizmet" etiketi, rozetler, fiyat kutusu + ≈50 $, özellik listesi,
  "Başvuruya başla" butonu); `PricingTabs` artık bu kartı vize kartlarıyla aynı ızgarada gösterir.
- **/vize-tipleri genişletildi**: `index.css` → yeni `.container-wide` (`max-w-[88rem]`, navbar ile
  aynı hiza), `PageHeader` `containerClass` prop'u aldı; sayfa içeriği artık logo ↔ "Başvuru Yap"
  hizasında (ölçüm: sol 280px, sağ 1640px @1920).

### Öneriler ödeme adımına taşındı (kullanıcı isteği)
- Adım 1'deki "Tarihlerinize göre önerilerimiz" bloğu kaldırıldı; `components/TripSuggestions.jsx`
  olarak ayrıştırılıp **Adım 4 (Özet ve ödeme)** başına "Ekstra hizmetler" adıyla eklendi.
  Tarih bloğu metinleri de öneri vaadi vermeyecek şekilde güncellendi.

### Telefon numarası + DUBAI harfleri
- Numara **+90 533 743 82 24** (DB `site_settings.company_info.phone` + `content.COMPANY`).
  WhatsApp da geçici test numarası (905331234567) yerine **905337438224** yapıldı (kullanıcı teyidi bekliyor).
- Yeni `components/PhoneDubai.jsx`: son 5 hanenin (3-8-2-2-4) tam altında **D U B A I** harfleri;
  navbar (masaüstü + mobil) ve footer'da kullanılıyor. Erişilebilirlik için bağlantılarda
  `aria-label="Telefon: +90 533 743 82 24"`, harf katmanı `aria-hidden`.
- Doğrulama: iteration_115 → frontend 10/10 madde %100, backend %100 (kapsam içi),
  pytest 310 passed. Not: `/api/contact` testleri tam suite'te IP hız sınırından (429) atabiliyor.

## 2026-09-07 (5) · Ana sayfa "sadece sigorta" vitrini + CTA metni

- **Yeni** `components/HomeInsuranceStrip.jsx` (`home-insurance-strip`), ana sayfada
  `HomeBundleStrip`'in hemen altında: "Sadece sigorta" şeridi. Canlı tarifeden 4 poliçe
  (7/15/30/60 gün · 490/560/590/740 ₺) kart olarak listelenir, her kart tek tıkla sepete ekler
  (`home-insurance-add-<id>`, mobilde 2 kolon, masaüstünde 4), toast'ta "Sepete git" aksiyonu var.
  Teminat maddeleri (7 emirlik · 30.000 €, TC kimlikle e-poliçe PDF, vize şartı yok), CTA'lar
  `home-insurance-cta` (→ /seyahat-sigortasi) ve `home-insurance-cart-link` (sepet adedi ile).
  Görsel: `IMAGES.travelInsurance` (yeni) + fiyat rozeti.
- `/seyahat-sigortasi` sayfasındaki "30 günlük süre" maddesi **"7, 15, 30 veya 60 gün"** oldu.
- `EasyCompare` CTA metni kullanıcı isteğiyle "Pasaportunuzla başlayın" → **"Hemen başvurun"**.
- Kullanıcı kararı: ilk poliçe provası yapılmayacak, **ilk gerçek müşteri siparişinde** elle
  kesilecek; prova başarılı olursa otomatik kesim panelden açılacak (şu an KAPALI).
- Doğrulama: masaüstü (1920) ve mobil (414px, yatay taşma 0) ekran görüntüleri; ins_7d sepete
  eklendi → "Sepetim (1)".

## 2026-09-07 (6) · Poliçe hazır WhatsApp bildirimi

- **Backend** `whatsapp.send_customer_text(phone, text, reason)` (yeni): müşteriye serbest metinli
  WhatsApp mesajı. Sağlayıcı hazır + bildirim açıkken doğrudan gönderir
  (`_send_twilio_text` veya yeni `_send_meta_text` → Meta Cloud API `type: text`, link ön izlemeli);
  aksi halde **manuel mod**: tek dokunuşla gönderilebilen `wa.me` bağlantısı döner.
- `insurance_tasks.issue_policy` artık poliçe e-postasından sonra `_policy_wa_text()` ile
  "poliçeniz hazır + PDF bağlantısı + sipariş kodu" mesajını gönderiyor; sonuç görevin
  `whatsapp` alanına (`status/link/phone/detail/at`) yazılıyor ve yanıtta `whatsapp` olarak dönüyor.
  Hem manuel PDF yükleme hem Tamamliyo API akışı (issue_via_provider → issue_policy) kapsanır.
- **Admin → Sigorta Poliçeleri**: kesilen poliçe kartında yeni blok (`insurance-whatsapp-<task>`);
  API canlı değilse yeşil **"WhatsApp'tan poliçe mesajı gönder"** butonu (`insurance-whatsapp-send-*`)
  hazır mesajı açar, API canlıysa "WhatsApp'tan gönderildi · <numara>" bilgisi görünür.
- Doğrulama (uçtan uca, canlı sağlayıcı tetiklenmeden): sigorta siparişi → ödendi → görev kuyruğu →
  manuel poliçe gönderimi; e-posta `status=sent`, `whatsapp.status=manual`, wa.me bağlantısında
  PDF linki + `SV-…` sipariş kodu doğrulandı; panelde buton görünüyor ve doğru href taşıyor.
- Test verisi temizliği: `scripts/wipe_test_data.py --apply` ile test başvuru/sipariş/poliçe
  kayıtları silindi (yalnız gerçek kayıt DV-BJ930600 + ayarlar kaldı). pytest 310 passed.

## 2026-09-07 (7) · Başvuru formu PDF'i çerçeve içine alındı

- `application_pdf._draw_frame()` (yeni, `onFirstPage`/`onLaterPages`): sayfa kenarından 8 mm
  içeride altın (1.1pt) + 1.6 mm daha içeride ince açık (0.5pt) yuvarlatılmış **çift çerçeve**;
  form artık çerçevenin içinde duruyor.
- Künye (şirket/TÜRSAB/iletişim + "resmî belge değildir" notu) akıştan çıkarılıp çerçevenin
  **alt kenarına sabitlendi**; içerik ile künye arasındaki boşluk artık sayfanın tamamını kullanıyor.
- Üst/alt kenar boşluğu 15 mm'ye çıkarıldı (yan boşluklar 15 mm kaldı: tablo genişlikleri 180 mm).
- Doğrulama: örnek başvuruyla PDF üretildi ve PNG'ye çevrilip görsel kontrol edildi;
  `tests/test_iteration_112_application_form.py` 9/9 PASS.

## 2026-09-07 (8) · Poliçelerim (müşteri arşivi) + e-posta başlığı sadeleşti

- **Backend** `GET /api/account/documents` (yeni, `require_customer`): müşterinin e-postasına ait
  **onaylanan vize PDF'leri** (`visa_result`) + **kesilmiş sigorta poliçeleri`, her biri
  `kind: visa|policy`, başlık, referans (başvuru/sipariş kodu), kişiler, tarih aralığı/dosya adı,
  kesim/gönderim zamanı ve imzalı **PDF indirme yolu** (`file_access.file_path`, 180 gün,
  `download=1`). TC kimlik no yanıtta paylaşılmaz.
- **Frontend** `/hesabim` → yeni **"Belgelerim"** bölümü (`account-documents`,
  `account-document-<id>`, `download-document-<id>`): vize (yeşil `FileCheck2`) ve poliçe
  (altın `ShieldCheck`) kartları, "Vizeyi indir" / "Poliçeyi indir" butonları (`fileUrl()`).
  Belge yoksa bölüm gizli kalır.
- **E-posta başlığı**: logonun altındaki "TÜRSAB ÜYESİ A GRUBU SEYAHAT ACENTESİ" satırı
  kullanıcı isteğiyle kaldırıldı (künyede/alt bilgide bilgi olarak duruyor).
- Doğrulama: uçtan uca (sipariş → ödendi → poliçe kesimi → müşteri girişi) `/account/policies`
  doğru dönüyor; `/hesabim` ekranında bölüm ve indirme bağlantısı çalışıyor (ekran görüntüsü),
  e-posta başlığında TÜRSAB satırı yok, pytest 310 passed. Test kayıtları temizlendi.

## 2026-09-07 (9) · Telefon numarası okunur formatta

- **Yeni** `backend/phone_format.py::format_phone()` ve `frontend/src/lib/phone.js::formatPhone()`:
  `+905551110001`, `905551110001`, `05551110001`, `5551110001` → **`+90 555 111 00 01`**;
  TR dışı/tanınmayan değer olduğu gibi kalır.
- Kullanıldığı yerler: başvuru formu PDF'i (Telefon satırı), e-posta şablonlarındaki müşteri
  telefonu (başvuru bildirimi, iletişim mesajı, sipariş bildirimi), Admin → Başvuru detayı,
  Siparişler, Mesajlar ve Sigorta Poliçeleri ekranları.
- Doğrulama: `format_phone` birim çıktıları kontrol edildi, PDF'te `pdftotext` ile
  "+90 555 111 00 01" göründü, üç admin ekranı hatasız açıldı, pytest 310 passed.

## 2026-09-07 (10) · PDF hizalama düzeltmesi

- Bölüm başlıkları ("BAŞVURU SAHİBİ / İLETİŞİM", "SEYAHAT BİLGİLERİ", …) ile alan etiketleri
  ("Ad Soyad", "Gidiş tarihi") artık **aynı sol hizada** (48,52 pt). Kök neden: tablolar 180 mm
  ile çiziliyordu, kullanılabilir alan ise 175,8 mm (ReportLab frame'i 6 pt sağ/sol padding
  uyguluyor) → tablolar `hAlign=CENTER` ile 6 pt sola kayıyordu.
- Çözüm: `application_pdf._cols()` yardımcısı — 180 mm'lik tasarım genişliği
  `CONTENT_W = A4 genişliği − 2×15 mm − 12 pt`e oranlanıyor; beş tablonun kolon genişlikleri
  bu orana geçirildi (oranlar korundu).
- Doğrulama: `pdftotext -bbox` ile tüm sol kenarlar 48,52 pt; PNG render görsel kontrol;
  `tests/test_iteration_112_application_form.py` 9/9 PASS.

## 2026-09-07 (11) · WhatsApp numarası ayrıldı

- WhatsApp hattı **+90 538 483 82 24** (`905384838224`) olarak güncellendi
  (DB `site_settings.company_info.value.whatsapp` + `content.COMPANY['whatsapp']`).
  Telefon hattı ayrı kaldı: **+90 533 743 82 24**.
- Tüm `wa.me` bağlantıları (SocialDock, ana sayfa, Hizmetler, Sigorta, İletişim, e-postalar,
  poliçe bildirimi) artık yeni WhatsApp numarasına gidiyor.
- `/iletisim` WhatsApp kartı önceden telefon numarasını yazıyordu; artık **WhatsApp numarasını**
  okunur formatta gösteriyor (`formatPhone`).
- Doğrulama: `/api/content/site` → phone `+90 533 743 82 24`, whatsapp `905384838224`;
  sayfadaki tek wa.me hedefi `https://wa.me/905384838224`; kart metinleri ekran görüntüsüyle teyit.

## 2026-09-07 (12) · Belgeyi e-postama tekrar gönder

- **Backend** `POST /api/account/documents/{document_id}/resend` (yeni, `require_customer`):
  `visa-<application_id>` veya `policy-<task_id>` kimliğini çözer, belgenin **giriş yapan
  müşteriye ait olduğunu** e-posta eşleşmesiyle doğrular ve imzalı indirme bağlantısıyla
  e-postayı tekrar gönderir. Vize için `emailer.visa_ready_html`, poliçe için yeni
  `insurance_tasks.policy_email_html()` şablonu kullanılır; hız sınırı **saatte 6 gönderim**
  (`rate_limit.check`), sahip olmayan/bulunamayan belge için 404.
- **Frontend** `/hesabim` → Belgelerim kartlarında **"E-postama tekrar gönder"** butonu
  (`resend-document-<id>`): tıklamada spinner, başarıda "Belge <e-posta> adresine gönderildi"
  bildirimi.
- Doğrulama: vize + poliçe için uç `status=sent` döndü, geçersiz kimlikte 404;
  `/hesabim` ekranında buton tıklandı ve başarı bildirimi göründü (ekran görüntüsü);
  pytest 310 passed, test kayıtları temizlendi.

## 2026-09-07 (13) · Belgeyi WhatsApp'tan gönder

- `/hesabim` → Belgelerim kartlarına **"WhatsApp'tan gönder"** butonu (`whatsapp-document-<id>`,
  WhatsApp yeşili #25D366): tıklamada `https://wa.me/?text=…` paylaşım ekranı açılır; mesajda
  belge adı + referans kodu + imzalı PDF bağlantısı hazır gelir. Müşteri kendi sohbetine,
  eşine/arkadaşına ya da bize tek dokunuşla iletebilir (API canlı olmadan da çalışır).
- Bölüm açıklaması güncellendi: "PDF'i indirebilir, WhatsApp'tan paylaşabilir veya e-postanıza
  tekrar gönderebilirsiniz."
- Admin poliçe kartındaki WhatsApp butonu da aynı yeşile alındı (tema `--brand-green`
  gök mavisi olduğu için WhatsApp rengiyle karışıyordu).
- Doğrulama: paylaşım bağlantısı (metin + PDF adresi) kontrol edildi; masaüstü ve mobil (414px,
  taşma 0) görünüm ekran görüntüleriyle teyit; test kayıtları temizlendi.

## 2026-09-07 (14) · Kod incelemesi bulguları uygulandı

**Yanlış pozitif olarak doğrulanıp değiştirilmeyenler**
- "exec() ile kod enjeksiyonu (`zami_rpa.py:90`)": satır aslında sabit argümanlı
  `asyncio.create_subprocess_exec(sys.executable, "-m", "playwright", "install", "chromium")`.
  Dinamik kod çalıştırma yok, güvenlik açığı değil.
- "156 yerde sabitlerle `is` karşılaştırması": `ruff --select F632` **0** bulgu; incelenen tüm
  satırlar (`zami_rpa 150/169/583`, `whatsapp 119/396/401`, `zami 151/417/793`, `zami_status 204`)
  doğru `is None` / `is not None` tekil nesne kontrolleri.
- "15 tanımsız değişken": `ruff F821` + `pyflakes` temiz; tek gerçek vaka aşağıda düzeltildi.

**Düzeltilenler**
- **Dairesel bağımlılık kırıldı**: yeni `insurance_delivery.py` (police e-posta/WhatsApp gönderimi
  + görev kapatma: `policy_html`, `policy_wa_text`, `_notify_customer`, `_close_task`,
  `issue_policy`). Yön artık tek: `insurance_tasks → insurance_provider → insurance_delivery`.
  Fonksiyon içi karşılıklı importlar kaldırıldı; `routes_admin` ve `routes_account` yeni modülü
  kullanıyor.
- **Gerçek tanımsız değişken hatası**: `server.py` lifespan içinde `insurance_task` yalnız `try`
  bloğunda atanıyordu; sigorta fiyat senkronu başlatılamazsa kapanışta **NameError** oluşuyordu.
  Lifespan tablo tabanlı yazıldı: `_init_startup_state()`, `_background_loops()`,
  `_start_background_loops()` — her döngü tek tek izole, C901 uyarısı da düştü (13 → uyarısız).
- **Karmaşıklık azaltıldı**: `insurance_provider.issue_via_provider` →
  `_ensure_quote` / `_ensure_policy` / `_ensure_policy_pdf` / `_save_provider_error`;
  `emailer.daily_digest_html` → `_digest_intro` / `_digest_apps_block` / `_digest_revenue_block` /
  `_digest_attention_block` / `_digest_admin_button`; `emailer.send_email` → `_sender_identity()`;
  `insurance_tasks._application_insurance_order` → `_insured_from_travelers` +
  `_application_insurance_lines`. `routes_store.py`'daki kullanılmayan yeniden-ihraçlar
  (`ESIM_PRODUCTS`, `INSURANCE_PRODUCTS`, `TOUR_PRODUCTS`) kaldırıldı.
- `GET /api/admin/insurance/provider` artık yalnız **aktif** 4 poliçeyi döndürüyor
  (eski pasif ins_8d/ins_30d_plus satırları panelde görünmüyor) — test ajanının notu.
- Kalan bilinen C901: `zami_rpa.fill_application` (27) ve `_auto_relogin_locked` (11) —
  canlı RPA akışı olduğu için bilinçli olarak dokunulmadı (regresyon riski), incelemede de yoktu.

**Doğrulama**: testing agent iteration_116 → yeni `tests/test_iteration_116_refactor.py` ile
16/16 PASS, kritik/minör bulgu yok; sipariş→ödeme→poliçe kesimi, hesap belgeleri + tekrar gönderim,
sağlayıcı paneli, günlük özet e-postası ve 7 arka plan zamanlayıcısının başlaması doğrulandı
(gerçek Tamamliyo poliçesi tetiklenmedi). Test dosyasındaki sınıflar arası sıra bağımlılığı
`seeded_policy_doc_id` fixture'ı ile giderildi. Tam suit: **324 passed / 5 skipped**.

## 2026-06-13 · Zami RPA form doldurma adımlara bölündü (P1 refactor)

### Kart genişliği doğrulaması (bekleyen iş kapatıldı)
- `/vize-tipleri` "Hizmet bedelleri" kartları ile `/takip` kartları aynı kapta:
  her iki sayfada da `.container-page` → 1152 px genişlik, 384 px sol kenar (1920 px viewport).
  Kod değişikliği gerekmedi; önceki oturumda yapılan `container-wide → container-page`
  değişikliği ekran görüntüsü + `getBoundingClientRect()` ile doğrulandı.

### `zami_rpa.fill_application` sadeleştirmesi
Kod incelemesinde P1 olarak işaretlenen tek büyük fonksiyon (C901 = 27, 143 satır, içinde
64 satırlık `set_value` closure'ı) test edilebilir adımlara bölündü. Davranış birebir aynı.
- **Yeni `_FieldSetter` sınıfı** (`page` + `filled` / `missing` / `skipped_disabled` / `values`):
  - `set(selector, value)` → alan yok = `missing`, kilitli/gizli = `skipped_disabled`,
    tipe göre select / radio / checkbox / metin doldurma (`_apply`).
  - `retry_skipped()` → portal doğrulamasından sonra kilidi açılan alanları tekrar dener.
- **Yeni adım fonksiyonları**: `_fill_precondition_error(mapping)` (form_url / eşleme kontrolü),
  `traveler_selector(template, index)` (`{i}` 0 tabanlı, `{n}` 1 tabanlı),
  `_fill_mapped_fields(setter, mapping, payload)` (sabitler → genel alanlar → yolcular),
  `_run_helper_clicks(page, mapping)` (Arapça çeviri vb. yardımcı butonlar).
- `_run_portal_validation(page, mapping, setter)` artık 5 yerine 3 parametre alıyor
  (set_value + skipped + values yerine tek `setter`).
- `fill_application` 143 → 90 satır, C901 uyarısı düştü. Kalan tek C901:
  `_auto_relogin_locked` (11) — canlı OTP akışı, bilinçli dokunulmadı.

**Doğrulama**: yeni `backend/tests/test_iteration_117_zami_fill_steps.py` → **32/32 PASS**
(Playwright yerine sahte `FakePage` / `FakeLocator` / `FakeRadioGroup`; tarayıcı gerekmez).
Kapsam: ön koşul hataları, selector şablonları, metin/select/radio/checkbox doldurma,
eksik–kilitli–boş değer ayrımı, `retry_skipped`, eşleme sırası, yardımcı tık hataları,
portal doğrulama akışı. `POST /api/admin/zami/bulk-transfer` (dry_run) gerçek tarayıcıyla
çalıştırıldı → beklenen "portal oturumu sona ermiş" yanıtı (canlı Zami oturumu yok).
Tam suit: **351 passed / 3 skipped**.

## 2026-09-08 · Tamamliyo canlı poliçe testi: 3 gerçek hata bulundu ve düzeltildi

Kullanıcının gerçek kimlik bilgisiyle canlı API'de adım adım test yapıldı (TCKN MERNIS'ten
doğrulandı). **Poliçe kesilemedi, ücret oluşmadı** — engel Tamamliyo hesap yetkisinde.

### Canlı test sonuçları
| Adım | Sonuç |
|---|---|
| `urun-kodlari` | ✅ |
| `fiyat-al` | ✅ 7 gün / 1 kişi = 244,85 ₺ |
| `teklif-olustur` | ✅ (düzeltmeden sonra) `teklifId` 2135824 / 2135825 |
| `odeme-onay` (cari tahsilat) | ❌ **"Bu teklif için açık tahsilat işlemi yapılamaz."** |
| `police-olustur` | ⛔ ödeme onaylanmadığı için çalıştırılamadı (HATA_7) |

### Düzeltilen hatalar
1. **`teklif-olustur` → HATA_2 "ulkeKodu gönderilmesi zorunludur"**
   `tamamliyo.create_quote` bu alanı hiç göndermiyordu; ilk gerçek siparişte poliçe kesimi
   hata verecekti. `ULKE_KODU_BAE = 784` (Birleşik Arap Emirlikleri) eklendi — kod
   Tamamliyo'nun kendi `/partner/v1/countries` listesinden doğrulandı.
   `fiyat-al` bu alanı istemiyor ve gönderilse de fiyat değişmiyor (244,85 ₺ = 244,85 ₺),
   bu yüzden fiyat senkronuna dokunulmadı.
2. **`odeme-onay` → HATA_3 "parameters içinde pnrNo/flightNumber/ticketNumber zorunludur"**
   Kod `parameters` içinde sadece `partnerReference` gönderiyordu. Servis 8 bilet alanını
   zorunlu tutuyor. Yeni `insurance_provider._payment_parameters(task)` bunları sipariş
   referansı + poliçe başlangıcından üretiyor (pnrNo/ticketNumber = sipariş referansı,
   ticketType "1", departureLocation "Türkiye", arrivalLocation "Dubai").
3. **Sağlayıcı hata mesajı panele ulaşmıyordu**
   Tamamliyo hataları `data.errorMessage` altında dönüyor; `_error_message` sadece kök
   seviyeye bakıyordu, bu yüzden admin "Tamamliyo servisi beklenmeyen yanıt döndürdü"
   görüyordu. Artık gerçek mesaj görünüyor (ör. "Bu teklif için açık tahsilat işlemi
   yapılamaz.").
4. **Bonus**: `models._iso_date_or_error` hata mesajında "GG.AA.YYYY" diyip sadece ISO
   kabul ediyordu. Artık `01.08.1981`, `01/08/1981` ve `1981-08-01` hepsi kabul edilip
   ISO'ya çevriliyor.

### Kalan engel — Tamamliyo'dan istenmesi gerekenler
`odeme-yap` denemeleri: `odemeTipi=1/2` → kredi kartı zorunlu, `odemeTipi=3` →
"Yetersiz puan bakiyesi", `odeme-onay` → açık tahsilat kapalı. Yani ödeme yöntemi
hesap tarafında açılmadan poliçe kesilemiyor. Seçenekler:
(a) partner token için "açık tahsilat / cari hesap" yetkisi açılması (önerilen),
(b) Tamamliyo bakiyesi yüklenip `odemeTipi=3` kullanılması,
(c) şirket kredi kartıyla `odeme-yap` (`odemeTipi=2`) entegrasyonu.

**Test**: yeni `backend/tests/test_iteration_118_tamamliyo_payment.py` → 13/13 PASS.
Tam suit: **362 passed / 5 skipped**.
Test siparişi: `SV-XFG87WZW` (490 ₺, ödendi işaretli), poliçe görevi `pending` durumda.

### 2026-09-08 (ek) · Müşteri artık Tamamliyo'nun promosyon listesine eklenmiyor
Kullanıcı, Tamamliyo'nun kestiği teklif e-postasının altında
*"Tamamliyo.com'dan haber ve promosyon e-postaları almayı seçtiğiniz için sizinle
iletişime geçtik"* yazdığını gördü. API'de bu aboneliği kapatan bir parametre yok
(dokümanların tamamı tarandı: `mail`, `izin`, `kvkk`, `onay`, `subscribe` alanı yok).

**Çözüm**: `teklif-olustur` çağrısında müşterinin e-posta/telefonu yerine kendi acente
iletişimimiz gönderiliyor (`insurance_provider._provider_contact()` →
`ADMIN_EMAIL` / `COMPANY["phone"]`, boşluklar temizlenir çünkü servis boşluklu `gsmNo`
kabul etmiyor). Böylece Tamamliyo'nun teklif/poliçe ve promosyon e-postaları bize gelir,
müşteriye gitmez. Poliçe müşteriye zaten kendi markalı e-postamız + WhatsApp ile iletiliyor,
bu yüzden müşteri deneyiminde kayıp yok — ayrıca müşteri sağlayıcıyı görüp doğrudan
gitmiyor.

**Doğrulama**: canlı teklif `2135835` — Tamamliyo'ya giden iletişim
`info@dubaivizehatti.com / +905337438224`. Tam suit: **366 passed / 3 skipped**
(3 yeni test `TestProviderContact`).

## 2026-09-08 (2) · Ödeme yöntemi cari tahsilat → Tamamliyo bakiyesi (odemeTipi=3)

Kullanıcı kararı: **"cari ödemeyi denemeyin şu an"** — Tamamliyo'ya açık tahsilat talebi
gönderilmedi. Ödeme, kart bilgisi taşımayan cari bakiye yöntemine çevrildi.

### Değişiklikler
- `tamamliyo.confirm_payment` (POST `odeme-onay`, açık tahsilat) **kaldırıldı**;
  yerine `tamamliyo.pay_with_balance(quote_id)` → POST `odeme-yap`
  `{"odemeTipi": "3", "teklifId": ...}`. `PAYMENT_TYPE_BALANCE = "3"` sabiti eklendi.
- `insurance_provider._payment_parameters` (odeme-onay'ın zorunlu tuttuğu 8 bilet alanı)
  kaldırıldı — `odeme-yap` + `odemeTipi=3` bu alanları istemiyor (canlı doğrulandı:
  parameters ile ve olmadan aynı yanıt).
- `_save_provider_error`: mesajda "bakiye" geçiyorsa panele yapılacak iş de yazılıyor →
  *"Yetersiz puan bakiyesi. Tamamliyo panelinden cari bakiye yükleyip poliçeyi tekrar kesin."*
- `AdminInsurance.jsx`: "Ödeme bizde kalır (cari tahsilat)" metni kaldırıldı; yerine
  "Poliçe bedeli Tamamliyo cari bakiyesinden düşülür, kart bilgisi hiçbir yerde tutulmaz"
  + turuncu bakiye uyarısı (`data-testid="insurance-balance-note"`).

### Canlı doğrulama
`odemeTipi` haritası (canlı deneme): `1`/`2` → kredi kartı zorunlu, **`3` → cari bakiye**,
`odeme-onay` → hesapta kapalı. Teklif `2135835` ile `_ensure_policy` canlı çalıştırıldı →
`HATA_15 "Yetersiz puan bakiyesi."` yani akış doğru, sadece bakiye yüklenmesi bekleniyor.
Kart verisi hiçbir aşamada sisteme girmiyor (test bunu ayrıca doğruluyor).

### Test verisi temizliği (kullanıcı isteği)
`SV-XFG87WZW` kapsamındaki 8 kayıt (sipariş, poliçe görevi, bildirim, 3 e-posta kaydı,
2 ziyaret izi) + kullanıcının onayıyla `DV-BJ930600` vize başvurusu ve kayıtlı yolcu
kaydı silindi. **Veritabanında TCKN `451…` izi kalmadı** (tüm koleksiyonlar tarandı).

**Test**: `test_iteration_118_tamamliyo_payment.py` 17/17 PASS.
Tam suit: **368 passed / 3 skipped**.

## 2026-09-08 (3) · Bakiye takibi + uyarı + bakiye bekleyen poliçe kuyruğu

Tamamliyo **bakiye sorgu API'si sunmuyor** (dokümanlarda yok; `/partner/v1/bakiye`,
`/partner/v1/cari`, `.../bakiye` denendi → 404 / CORS catch-all 405). Bakiye yalnızca
ödeme anında `HATA_15 "Yetersiz puan bakiyesi"` ile anlaşılıyor. Bu yüzden bakiye
kendimiz takip ediliyor.

### Yeni `insurance_balance.py`
- `settings_col` → `insurance_balance`: `loaded_try`, `spent_try`, `topups[]` (son 20),
  `last_alert_at/kind`, `threshold_policies` (varsayılan 3).
- `status()`: kalan bakiye + **kesilebilir poliçe sayısı** (en pahalı aktif poliçe maliyetine
  göre temkinli), `low` / `empty` bayrakları.
- `add_topup(amount, actor)`: panelden girilen yükleme; uyarı kilidini sıfırlar.
- `record_spend(amount)`: her kesilen poliçenin maliyetini düşer
  (`provider_quote_price` varsa o, yoksa katalog maliyeti × kişi).
- `mark_empty()`: Tamamliyo "yetersiz bakiye" derse takip sıfırlanır (gerçek her zaman onda).
- `maybe_alert(waiting)`: admine **e-posta + WhatsApp** uyarısı. `empty` → ACİL,
  `low` → hatırlatma. Aynı tür uyarı 12 saatte bir; `low → empty` yükselmesi anında geçer.
- `parse_try()`: "1.244,85" / "244.85" / sayı formatlarını tolere eder.

### Bakiye bekleyen poliçe kuyruğu (`insurance_provider.py`)
- Poliçe kesimi bakiye hatası verirse görev `status: "waiting_balance"` olur
  (`waiting_since`), bakiye sıfırlanır ve admine uyarı gider (`_park_for_balance`).
- `retry_waiting_tasks()`: takip edilen bakiye > 0 ise bekleyen görevleri sırayla keser;
  ilk hatada durur (bakiye yine bitmiş olabilir).
- `balance_retry_loop()`: 15 dakikada bir çalışır (server.py'de "insurance balance queue").
- Bakiye yüklendiği an `POST /admin/insurance/balance/topup` kuyruğu hemen tetikler.

### API + panel
- `GET /api/admin/insurance/balance` (+ `waiting_tasks`), `POST /api/admin/insurance/balance/topup`.
- `GET /api/admin/insurance-tasks?status=waiting_balance` filtresi eklendi.
- `AdminInsurance.jsx`: "Tamamliyo cari bakiyesi" kartı — kalan bakiye, ≈kesilebilir poliçe,
  poliçe maliyeti, bakiye bekleyen poliçe sayısı, kritik uyarı ve "Bakiye yükledim" alanı
  (`insurance-balance-panel`, `-state`, `-remaining`, `-policies`, `-waiting`, `-warning`,
  `-amount`, `-topup`). Görev rozetine "Bakiye bekliyor" durumu eklendi.

### Canlı doğrulama
Gerçek API ile: görev `waiting_balance`'a düştü, `provider_error` =
*"Yetersiz puan bakiyesi. Tamamliyo panelinden cari bakiye yükleyip poliçeyi tekrar kesin."*,
uyarı e-postası **gönderildi** (`ACİL · Tamamliyo bakiyesi bitti, poliçe kesilemiyor`,
status=sent), panel kartı ve "Bakiye bekliyor" rozeti ekran görüntüsüyle teyit edildi.
Test görevi sonrasında silindi.

**Test**: `test_iteration_119_insurance_balance.py` 30/30 PASS.

## 2026-09-08 (4) · Vize hazır e-postası: GDRFA doğrulama adımları + PDF eki

Kullanıcı isteği: vize çıkınca müşteriye WhatsApp mesajına benzer bir e-posta gitsin —
resmî sorgulama linki + adımlar olsun, vize belgesi de ekte gelsin, **cümleler birebir
aynı olmasın**.

- `emailer.visa_ready_html(app_doc, download_url, message, attached)`:
  - Yeni `_gdrfa_block()`: GDRFA sorgulama kutusu (`GDRFA_STATUS_URL`) + 5 adımlı sıralı
    liste (English dil seçimi → File sekmesi → First Name → File Number'ı `/` olmadan gir →
    sorgula). "Bu adım zorunlu değildir" notu var.
  - Metin yeniden yazıldı; orijinal WhatsApp cümlelerinin hiçbiri geçmiyor (test bunu
    ayrıca doğruluyor: "Linke tıklayın", "Nasıl kontrol edilir?" vb. yasaklı).
  - `attached=True` ise "Vize belgeniz bu e-postanın ekinde…", değilse eski buton metni.
- Yeni `application_docs.visa_pdf_attachment(file_id, reference_code)`: belgeyi object
  storage'dan okur, `vize-dv-xxx.pdf` adıyla ek döndürür; dosya yoksa/okunamazsa/18 MB'ı
  aşarsa boş liste döner (e-posta yine bağlantıyla gider, hiç patlamaz).
- 4 gönderim noktası da eki kullanıyor: `visa_delivery.deliver_visa_document` (Zami'den
  otomatik), `wa_docs` (tedarikçi WhatsApp akışı), `routes_account` (müşteri "tekrar
  gönder"), `routes_admin` (panelden elle gönderim).

**Test**: `test_iteration_120_visa_email.py` 17/17 PASS. Ayrıca gerçek örnek e-posta
`info@dubaivizehatti.com` adresine gönderildi (status=sent).
Tam suit: **413 passed / 5 skipped**.

## 2026-09-08 (5) · GDRFA yönlendirmesi WhatsApp mesajına da eklendi

- **Tek kaynak**: `content.py` içine `GDRFA_STATUS_URL`, `GDRFA_INTRO`, `GDRFA_STEPS`
  eklendi. `emailer` (HTML `<ol>` kutusu) ve `whatsapp` (numaralı düz metin) aynı
  kaynaktan besleniyor — metin ileride tek yerden güncellenebilir.
- **`whatsapp.gdrfa_check_text()`**: WhatsApp'a uygun düz metin (HTML yok, `*kalın*`
  vurgu, numaralı 5 adım, 517 karakter).
- **`whatsapp.visa_ready_wa_text(app_doc, extra)`**: vize belgesi teslim mesajı —
  "…vize belgesi ekte, hayırlı olsun" + GDRFA adımları + kapanış. 659 karakter,
  WhatsApp 1024 karakter caption limitinin altında (test bunu doğruluyor).
- **`wa_docs.deliver_to_customer`**: belge gönderim caption'ı artık bu metni kullanıyor
  (önceden tek satırlık "vize belgesi ekte" metniydi).
- **`whatsapp.notify_result`**: `status == "approved"` ise mesajın sonuna GDRFA
  yönlendirmesi ekleniyor. Ret mesajı temiz kalıyor (test var).
  WhatsApp manuel modda olduğu için bu metin doğrudan `wa.me` bağlantısına giriyor.

### 🐞 Yan bulgu ve düzeltme
Veritabanındaki WhatsApp mesaj şablonu eski bir testten kalmış:
`"Test template {name} {status}"` — gerçek müşteriye *"Test template … Onaylandı"*
gidecekti. Şablon varsayılana geri alındı:
`"Sayın {name}, Dubai vize başvurunuzun sonucu: {status}. Başvuru numaranız: {reference}. Detay: {link}"`

### Canlı doğrulama
`POST /api/admin/whatsapp/send/{id}` (onaylı başvuru, manuel mod) → mesaj GDRFA
adımlarıyla birlikte döndü, `wa.me` bağlantısı hazır. Gönderim yapılmadı (manuel mod).

**Test**: `test_iteration_120_visa_email.py` 25/25 PASS (8'i WhatsApp tarafı).
Tam suit: **421 passed / 5 skipped**.

## 2026-09-08 (6) · Tek tık doğrulama: dosya numarası otomatik okunuyor

### Önce araştırma: GDRFA hazır bağlantı kabul ediyor mu?
Sayfa canlı incelendi: `smart.gdrfad.gov.ae/Public_Th/StatusInquiry_New.aspx`
**OutSystems/ASP.NET WebForms** — `__VIEWSTATE` + `__OSVSTATE` kullanıyor, query string
desteği yok (alan adları `...wtFileNoInp`, `...wtFirstNameInp`, `...wtBirthDateInp`,
ayrıca `wtApplicationNumber_InputOTC` gibi OTC alanları var).
**Sonuç: devlet sayfasına hazır dolu bir GET bağlantısı üretilemiyor.** Sunucudan
sorgulamak (scraping) da hem kırılgan hem uygunsuz olurdu. Bu yüzden en fazla
otomatikleştirilebilir çözüm uygulandı: numara bizde otomatik okunur, müşteriye tek
dokunuşla kopyalanabilen kendi sayfamız gönderilir.

### Yeni `visa_file_number.py`
- `FILE_NUMBER_RE`: `201/2026/1234567` (emirlik/yıl/seri). Yıl `19xx|20xx` zorunlu
  olduğu için tarih/tutar yanlışlıkla yakalanmıyor (`01/2026/12` → boş).
- `extract_from_text()`: önce etiketli satırlarda arar (`File No`, `File Number`,
  `Entry Permit`, `رقم الملف`), etiket bir üst satırdaysa da bulur; sonra tüm metne bakar.
- `extract_all_from_text()`: belgedeki tüm numaralar, görünüm sırasında, tekrarsız
  (çok yolcu tek PDF senaryosu).
- `extract_from_upload()`: object storage'dan PDF'i okur (**PyMuPDF**), hata/görsel/
  bozuk PDF durumunda sessizce boş döner.
- `annotate(application_id, visa_result)`: numaraları `visa_result.file_number` +
  `file_numbers` olarak başvuruya yazar.
- `verify_url(origin, application_id)`: `file_access` HMAC'i ile imzalı, 180 gün
  geçerli `/vize-dogrula/{id}?t=...` bağlantısı.

### Müşteri sayfası `/vize-dogrula/:applicationId`
`VisaVerify.jsx` — her yolcu için **File Number (bölü işareti olmadan)**, **First Name**,
**Date of Birth (GG-AA-YYYY)** kartları; her satırda tek dokunuşla **Kopyala** butonu
(clipboard API + eski tarayıcılar için fallback), "GDRFA sorgulama sayfasını aç" butonu
ve 5 adımlı yönlendirme. Çok yolcu + numara sayısı eşleşmezse numaralar ayrı havuz
kartında listelenir. Süresi geçmiş/yanlış jetonda 403 + anlaşılır hata ekranı.
`GET /api/visa-verify/{application_id}?t=` imzalı jeton ister.

### Mesajlar
- **E-posta**: GDRFA kutusuna "Dosya numaranız: 201/2026/1234567" + **"Doğrulama
  bilgilerimi aç"** butonu eklendi (numara okunamadıysa eski hâli aynen kalıyor).
- **WhatsApp**: bağlantı varsa adımlar mesaja yazılmıyor (sayfada var) → mesaj kısalıyor
  ve 1024 karakter caption limitine rahat sığıyor. Bağlantı yoksa 5 adımlı uzun sürüm.
- Tetiklenen yerler: Zami otomatik teslim, tedarikçi WhatsApp akışı, panelden elle
  gönderim, müşterinin "tekrar gönder"i — hepsi numarayı okuyup bağlantıyı ekliyor.

### Panel
`PATCH /api/admin/applications/{id}/visa-file-number` + Başvuru Detayı'nda
"GDRFA dosya numarası" alanı (`visa-file-number-input`, `-save`). PDF'ten okunamazsa
admin elle girer; biçim doğrulanır (`201/2026/1234567`).

### Canlı doğrulama
Örnek vize PDF'i panelden yüklendi → numara **otomatik okundu** (`201/2026/1234567`),
doğrulama sayfası açıldı, "File Number 20120261234567" kopyalandı (buton "Kopyalandı"
oldu), 5 adım ve GDRFA butonu göründü; geçersiz jeton **403** verdi. WhatsApp onay mesajı
numarayı ve bağlantıyı taşıyor. Örnek e-posta `info@dubaivizehatti.com` adresine gönderildi.
Test vize belgesi sonrasında kaldırıldı.

**Test**: `test_iteration_121_visa_file_number.py` 25/25 PASS.
Tam suit: **448 passed / 3 skipped**.

## 2026-09-08 · SEO denetim düzeltmeleri (dağıtılmış site raporu) + başvuru formu PDF rötuşları

### SEO raporu (Health 83 · 194 hata / 162 uyarı / 89 sayfa) — kök nedenler ve çözümler
1. **60 sayfada tekrarlanan title/description/içerik + 78 sayfada düşük metin/HTML oranı**
   Kök neden (canlıda doğrulandı): CRA SPA olduğu için sunucu her rota için AYNI 3.5 KB'lık
   `index.html` kabuğunu döndürüyor (`curl https://www.dubaivizehatti.com/vize-tipleri` →
   ana sayfa title'ı, canonical yok). Ayrıca hem `www` hem `www'suz` host 200 dönüyor ve
   canonical `window.location.origin` kullandığı için her host kendini işaretliyordu
   (89 taranan sayfa ≈ 44 sayfa × 2 host).
   Çözüm:
   - `src/lib/site.js` → yeni `SITE_URL` sabiti (`REACT_APP_SITE_URL`, varsayılan
     `https://www.dubaivizehatti.com`). canonical + og:url artık HER ZAMAN tek host.
     `setMeta` yeniden yazıldı: og:site_name/og:image, twitter kartları ve
     **noindex desteği** (daha önce `{noindex:true}` seçeneği hiç uygulanmıyordu →
     /sepet, /hesabim indekslenebilir durumdaydı; artık `robots: noindex, nofollow`).
   - **Statik ön-render**: `scripts/prerender.js` + `scripts/seo-pages.js` (yeni).
     `yarn build` artık `craco build && node scripts/prerender.js`. Script build sonrası
     backend API'sinden (`/api/content/site`, `/api/visa-types`, `/api/visa-guides`,
     `/api/articles`, `/api/content/legal`) içeriği çekip **30 rota için** ayrı
     `build/<rota>/index.html` üretiyor: tekil title/description/canonical/OG + JSON-LD +
     gerçek metin gövdesi (`#root` içinde `#seo-prerender`, React mount olunca değişiyor).
     Sonuç: 30 sayfanın tamamında **tekil** title/description, metin/HTML oranı
     **%12.5-46** (önce ~%2), sayfa başına 107-732 kelime. Script idempotent
     (tekrar çalıştırıldığında birikme yok), API'ye ulaşamazsa build'i düşürmüyor.
     `build/sitemap.xml` de bu listeden üretiliyor (lastmod=build günü).
2. **14 sayfada yapısal veri hatası**
   - `ArticleDetail.jsx`: Article şemasına `image` (dizi) ve `publisher.logo` (ImageObject)
     eklendi, `mainEntityOfPage` string → `{"@type":"WebPage","@id":...}`, `author.url`.
   - `VisaGuide.jsx`: FAQ boşsa **FAQPage hiç basılmıyor** (boş `mainEntity` geçersizdi),
     `Offer` yalnız fiyat varsa ve `price` 2 ondalıklı string olarak, breadcrumb ana sayfa
     item'ı `${origin}/`, provider'a `url`.
   - `Home.jsx`: yeni **TravelAgency (@id #organization) + WebSite** şeması (logo, telefon,
     e-posta, adres, sameAs, areaServed) — daha önce hiç kurum şeması yoktu.
3. **/basvuru URL'lerinde çok fazla parametre**: `applyPath()` / `parseApplyPath()` helper'ları
   ve `/basvuru/:seg1/:seg2` rotaları eklendi → `/basvuru/pack-family/visa-30-single`.
   Tüm iç linkler (HomeBundleStrip, VisaShowcase, VisaTypeCard, VisaComparison, Cart,
   VisaGuide) yol tabanlı adrese geçti; eski `?vize=&paket=` adresleri çalışmaya devam ediyor;
   canonical her durumda `/basvuru`.
4. **60 karakterden uzun title'lar**: /seyahat-sigortasi 77→42; ayrıca Home 69→46,
   /vize-tipleri 70→44, /gelismeler 63→52, /basvuru 60→43, /esim, /dubai-turlari, /kvkk,
   2 hukuki sayfa ve **7 vize rehberi** (`backend/visa_guides.py` seo_title'ları 62-67→41-56)
   kısaltıldı. `withBrandTitle()` yazı başlıklarında marka ekini sığmıyorsa düşürüyor.
5. **Minify (80 dosya)**: bu dosyalar `assets.emergent.sh` üzerinden gelen platform
   script'leri — bizim tarafta değiştirilemez. Kendi bundle'ımız CRA/terser ile minify;
   ek olarak `GENERATE_SOURCEMAP=false` eklendi (.map dosyaları artık üretilmiyor).
6. Ek düzeltmeler: `robots.txt` sitemap adresi www'ya alındı + `/siparis/`, `/vize-dogrula/`
   disallow; statik `public/sitemap.xml` www'ya alındı ve **404 veren
   `/dubai-vizesi/transit-vize`** kaydı silindi; rehberi olmayan vize tiplerinde
   ("transit vize", "14 gün") 404'e giden "Detaylı rehberi oku" linki kaldırıldı
   (`PricingTabs` guide slug listesini çekip `VisaTypeCard hasGuide` prop'una geçiriyor).

**Test**: `testing_agent` iteration_117 → frontend **%100**, sorun yok (14 sayfada title
27-53 karakter, duplicate yok, canonical/robots doğru, JSON-LD geçerli, yol tabanlı ve
legacy /basvuru adresleri çalışıyor). Backend pytest **455 passed / 3 skipped**.

**Kullanıcı eylemi gerekiyor**: (a) yeniden **deploy** (ön-render yalnız production build'de),
(b) `dubaivizehatti.com → www.dubaivizehatti.com` **301 yönlendirmesi** alan adı/hosting
tarafında açılmalı (şu an iki host da 200 dönüyor), (c) Search Console'a
`https://www.dubaivizehatti.com/sitemap.xml` yeniden gönderilmeli.

### Başvuru formu PDF'i (kullanıcı ekran görüntüsü üzerine)
`backend/application_pdf.py`:
- Logo krem zeminliydi (`assets/email-logo.png` RGB) → saydam `assets/pdf-logo.png`
  (frontend `logo-horizontal-gold-palm.png` kopyası) kullanılıyor, zemin bloğu kalktı.
- Başlık **"VİZE BAŞVURU FORMU" → "Dubai Vizesi Başvuru Detayları"** (PDF metadata title da).
- Başlık altındaki "Başvuru tarihi … · Dubai / Birleşik Arap Emirlikleri" satırı kaldırıldı;
  **BAŞVURU TARİHİ** referans bandına, **ÖDEME DURUMU'nun soluna** taşındı
  (4 kolon: takip kodu · başvuru tarihi · ödeme durumu · tahmini sonuçlanma).
- Künye **ortalandı** (`foot` stili `TA_CENTER`) ve yeni cümle eklendi: "Dubai Vize Hattı,
  Moruya Travel Solutions Turizm Ltd. Şti. tarafından işletilen bir markadır; tüm hizmetler
  bu şirket üzerinden verilmektedir. Birleşik Arap Emirlikleri'ndeki grup şirketimiz
  Moruya Travel Solutions FZE'dir." Künye 4 satıra çıktığı için `bottomMargin` 15→27 mm
  (form tek sayfada kalıyor, doğrulandı).
- Doğrulama: canlı endpoint `GET /api/admin/applications/{id}/form.pdf` → 200, PDF görsel
  olarak kontrol edildi; `test_iteration_112_application_form.py` dahil 32 PDF testi PASS.

## 2026-09-08 · Güvenlik denetimi (security_audit_agent) ve düzeltmeleri

Denetim sonucu: **kritik/yüksek bulgu yok**; önceki denetimin SEC-001…004 + P3 maddelerinin
tamamı kodda kapalı doğrulandı (OTP + hash'li kod, imzalı/süreli dosya jetonu, kaçışlı
bookmarklet, CORS allowlist, JWT_SECRET fallback'i yok, admin uçları `require_admin`,
ödeme tutarı yalnız sunucudan, WhatsApp webhook imza doğrulaması fail-closed).
Kalan 2 ORTA bulgu ve 6 P3 sertleştirme maddesi düzeltildi:

### SEC-001 (ORTA) — kimliksiz ve sınırsız e-posta gönderimi
Kök neden iki katmanlıydı: (a) `POST /api/drafts` kimlik doğrulaması ve hız sınırı
olmadan istenen adrese posta attırıyordu; (b) **frontend her 5 saniyede otomatik taslak
kaydediyor ve her kayıt posta tetikliyordu** — canlı DB'de tek müşteriye 10 "kaydedildi"
postası gitmiş (`email_outbox`).
- `rate_limit.py`: yeni `allow(key, limit, window)` — sınır aşılınca 429 atmak yerine
  `False` döner (kayıt/sipariş akışı bozulmadan yalnız bildirim atlanır).
- `routes_account.save_draft`: IP başına 120 kayıt/saat (429) + posta yalnızca **ilk
  kayıtta** veya kullanıcının açık isteğinde (`DraftIn.notify`, frontend `notify: !silent`
  gönderiyor), alıcı başına **3 posta/saat**.
- `routes_public.create_application` + `routes_store.create_order`: IP başına 300 oluşturma/saat
  (429) ve müşteri bildirim postası alıcı başına **40/saat** (aşılırsa başvuru/sipariş yine
  oluşur, yalnız müşteri postası atlanır; admin bildirimi gider).
- Eşikler bilinçli olarak geniş: CGNAT/ortak IP arkasındaki gerçek müşteriler ve acente
  personeli engellenmesin (ilk denemede 12/saat seçilmişti, test suit'i ve gerçek kullanım
  senaryosunu kırdığı görülüp yükseltildi).

### SEC-002 (ORTA) — PDF motoruna markup enjeksiyonu
`application_pdf.py`: yeni `_safe()` (xml escape) ile ad/soyad, pasaport no, notlar,
konaklama, ürün adları, belge etiketleri, takip kodu ve süre alanları ReportLab
`Paragraph`'a kaçışlı giriyor. Böylece `<img src=...>`/`<b>` gibi girdiler metin olarak
basılıyor; PDF üretimi bozulmuyor ve sunucu taraflı dış kaynak isteği (SSRF adayı) kalmıyor.

### Sertleştirme (P3)
- `server.py`: güvenlik başlıkları middleware'i (HSTS, `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy`, `Permissions-Policy`).
- `/docs`, `/redoc`, `/openapi.json` artık **kapalı** (yalnız `ENABLE_API_DOCS` env'i
  tanımlıysa açılır) — yönetim API yüzeyi dışarıya listelenmiyor.
- `routes_public._validate_upload`: uzantı/boyut kontrolüne ek **dosya imzası (magic byte)**
  doğrulaması (JPEG/PNG/PDF/WEBP); uzantısı değiştirilmiş dosyalar 400 alıyor.
- `routes_admin.admin_verify_code`: IP başına 20 doğrulama denemesi/saat.
- `backend/.env`: kullanılmayan `ADMIN_LOGIN_PASSWORD` kaldırıldı (giriş OTP ile);
  `tests/test_iteration_80.py` bu env bağımlılığından kurtarıldı.

**Test**: yeni `tests/test_iteration_122_security_hardening.py` (8 test: taslak posta
bastırma + alıcı sınırı, sahte/gerçek JPEG yükleme, güvenlik başlıkları, /docs-/redoc-
/openapi kapalı, PDF markup kaçışı). Tam suit: **461 passed / 3 skipped**.
NOT: tam suit aynı saat içinde arka arkaya çalıştırılırsa `/api/contact` (mevcut, bu
oturumdan önce eklenen) IP sınırı ve paylaşımlı test kutusu (`delivered@resend.dev`)
40/saat posta sınırı nedeniyle 2-3 test 429 alabilir; backend'i yeniden başlatmak sayaçları
sıfırlar.

## 2026-09-08 · Tamamliyo ödemesi: cari bakiye → kurumsal kart (odemeTipi=2)

Tamamliyo'dan gelen bilgi: **"odemeTipi 3 yok bize; `odeme-yap` kullanmanız lazım,
ödeme tipi 2 kullanması gerekiyor."** Partner hesabımızda cari bakiye/puan yöntemi
bulunmuyor. Dokümanda `odemeTipi=2`, `odeme-yap` ucuna kredi kartı alanlarıyla
gönderiliyor (`krediKartiNo`, `krediKartiCvv`, `krediKartiBitisTarihi`, `krediKartiAd`,
`krediKartiSoyad`). Kart bizim **kurumsal kartımız** (müşteri kartı değil).

### Backend
- `tamamliyo.py`: `pay_with_balance()` → **`pay_for_quote()`**; `PAYMENT_TYPE_CARD="2"`,
  kart alanları `CARD_ENV` üzerinden yalnız ortam değişkenlerinden okunuyor
  (`TAMAMLIYO_CARD_NUMBER/EXPIRY/CVV/NAME/SURNAME`), numaradaki boşluklar temizleniyor.
  `card_configured()` + `card_hint()` (maskeli son 4 hane) eklendi; log'a yalnızca
  maskeli bilgi yazılıyor, kart hiçbir yerde saklanmıyor/dönmüyor.
- **Mükerrer çekim koruması**: `_request(..., retry=False)` — ödeme isteği asla
  tekrarlanmaz. Zaman aşımında `ODEME_DURUMU_BILINMIYOR` işaretiyle hata döner
  (integration_expert playbook'undaki "timeout ≠ çekim olmadı" kuralı).
- Yeni **`insurance_payment.py`** (eski `insurance_balance.py` silindi): ödeme engeli
  tespiti (`is_payment_blocked`: kart/limit/bakiye/tanımsız kart), belirsiz çekim tespiti
  (`is_payment_unknown`), operatör uyarısı (e-posta + WhatsApp, 12 saat soğutma) ve
  panel durumu (`method: card`, `card_configured`, `card_hint`).
- `insurance_provider.py`: `WAITING_STATUS` `waiting_balance` → **`waiting_payment`**,
  yeni **`REVIEW_STATUS = "payment_review"`**. Ödeme reddi/kart eksikliği → kuyruk
  (15 dk'da bir otomatik tekrar); yanıt alınamayan çekim → `payment_review` ve
  **otomatik tekrar YOK** (operatör Tamamliyo panelinden kontrol eder).
  Bakiye takibi (`_policy_cost`, `record_spend`, `mark_empty`) kaldırıldı.
- Rotalar: `GET /admin/insurance/balance` + `POST /admin/insurance/balance/topup` kaldırıldı;
  yerine **`GET /admin/insurance/payment`** ve **`POST /admin/insurance/payment/retry`**.
- `server.py`: arka plan döngüsü `insurance balance queue` → `insurance payment queue`
  (`payment_retry_loop`).
- `backend/.env`: 5 kart anahtarı **boş** olarak eklendi (kullanıcı dolduracak).

### Panel (AdminInsurance.jsx)
- "Tamamliyo cari bakiyesi" paneli → **"Poliçe ödemesi · kurumsal kart"**: kart hazır/
  tanımsız durumu (maskeli son 4 hane), ödeme bekleyen poliçe, doğrulama bekleyen çekim,
  son uyarı zamanı, "Bekleyenleri tekrar dene" butonu ve mükerrer çekim uyarısı.
  Bakiye yükleme formu kaldırıldı. Görev etiketleri: "Ödeme bekliyor" /
  "Ödeme doğrulaması bekliyor".

### Test
- `test_iteration_118_tamamliyo_payment.py` güncellendi (21 test): odemeTipi=2 payload'ı,
  kart alanlarının env'den gelmesi, boşluk temizliği, **retry=False**, maskeleme,
  kart eksikken istek gönderilmemesi, zaman aşımında `ODEME_DURUMU_BILINMIYOR`.
- `test_iteration_119_insurance_balance.py` → **`test_iteration_119_insurance_payment.py`**
  (16 test): engel/belirsiz çekim ayrımı, kuyruk durumları, uyarı metinleri + soğutma,
  kart yokken retry'ın atlanması.
- Tam suit **453 passed / 3 skipped**. Canlı uçlar doğrulandı
  (`/admin/insurance/payment` → `card_configured: false`, eski bakiye ucu 404) ve panel
  ekran görüntüsüyle kontrol edildi.

### ⏳ Kullanıcıdan bekleniyor (tek engel)
Kurumsal kart bilgileri `backend/.env` içine girilmeli:
`TAMAMLIYO_CARD_NUMBER`, `TAMAMLIYO_CARD_EXPIRY` (YYYY-MM-DD), `TAMAMLIYO_CARD_CVV`,
`TAMAMLIYO_CARD_NAME`, `TAMAMLIYO_CARD_SURNAME`. Girilene kadar poliçeler
`waiting_payment` kuyruğunda bekler, müşteri siparişi kaybolmaz. Girildikten sonra
gerçek 7 günlük test poliçesi kesilip doğrulanmalı.

### 2026-09-08 (aynı gün, devam) · Kurumsal kart girildi ve bağlantı doğrulandı
- `backend/.env`: kart bilgileri girildi (numara **** 1028, son kullanma 2030-06-01,
  ad SEDAT / soyad ANDİÇ). Numara/CVV hiçbir ekranda, kayıtta veya log'da görünmüyor.
- `krediKartiBitisTarihi` formatı Tamamliyo dokümanına göre **YYYY-AA-01** (06/30 → 2030-06-01).
- Doğrulamalar (ücretsiz, kayıt/çekim oluşturmadan): `GET /admin/insurance/payment` →
  `card_configured: true`, `card_hint: "**** 1028"`; panelde "Kart hazır **** 1028",
  uyarı bandı kayboldu; `POST /admin/insurance/sync-prices` ile Tamamliyo'dan canlı
  maliyetler çekildi (7g 244,85 ₺ → 490 ₺ satış, 15g 279,74 ₺, 30g 296,63 ₺, 60g 367,55 ₺);
  ödeme gövdesi maskeli olarak kontrol edildi (odemeTipi=2, 16 haneli numara, boşluksuz).
- **Gerçek test poliçesi kullanıcı tercihiyle henüz KESİLMEDİ** ("önce bağlantıyı doğrula").
  İlk gerçek kesim yapıldığında kartından ~245 ₺ (7 günlük) çekilecek.

## 2026-09-08 (5) · Sigorta gider raporu + otomatik poliçe kesimi açıldı + ürün kodu env'e taşındı

### Sigorta gider raporu (karttan çekilen tutarlar)
- `insurance_provider._record_charge()`: ödeme başarılı olduğu anda göreve **`charged_try`**
  (Tamamliyo teklif fiyatı) + **`charged_at`** yazılıyor — gider raporunun tek doğruluk kaynağı.
- `insurance_payment.parse_try()` geri geldi ("244,85" / "1.234,56 TL" / 296.63 → float).
- `insurance_tasks.expense_report(months)`: yalnızca gerçekten çekim yapılan görevleri
  (`charged_at` dolu) alır; aylık toplam + adet, bu ay özeti ve son 25 çekimin listesi
  (tarih, sipariş referansı, plan, poliçe no, çekilen tutar, satış tutarı).
  Elle/test kesimleri (mevcut 30 kayıt) gidere girmiyor — tablo sıfırdan başlıyor.
- Yeni uç: **`GET /admin/insurance/expenses?months=12`**.
- Panel: `AdminInsurance.jsx` → yeni **"Sigorta gideri · karttan çekilen"** kartı
  (`insurance-expense-panel`): bu ay toplamı, aylık bar listesi ve çekim tablosu;
  çekim yoksa "Henüz karttan çekim yapılmadı" boş durumu.

### Otomatik poliçe kesimi
- Panelden **açıldı** (`POST /admin/insurance/auto-issue {"enabled": true}` → `auto_issue: true`).
  Artık ödeme onaylanan sigorta siparişlerinde poliçe elle beklemeden kesiliyor, PDF müşteriye
  gidiyor (`insurance_tasks._maybe_auto_issue`).
- `test_iteration_116_refactor.py::test_provider_status` artık `auto_issue`'nun bool olmasını
  doğruluyor (eskiden `False` sabitini bekliyordu).

### Ürün kodu (`urun_id`) artık .env'de
- Kullanıcı Tamamliyo'dan "her sigorta alımında 220 kodunu kullanın" bilgisini iletti.
  **Canlı deneme: 220 fiyat dönmüyor** — `fiyat-al` `urun: yurtdisi-seyahat`, `urun_id: 220`
  ile 1/2 kişi, 7/30/90/365 gün, bugün/yarın başlangıç, string/int id kombinasyonlarının
  **tamamında** `"Fiyat bulunamadı. Lütfen daha sonra tekrar deneyiniz. 758"`.
  Aynı istek 141 (244,82 ₺), 185 (Covid dahil 383,84 ₺), 189 (Covid + vize reddi dahil
  1.483,01 ₺) ile çalışıyor. `urun-kodlari` listesinde de 220 yok → ürün partner hesabımıza
  tanımlı değil; Tamamliyo'nun açması gerekiyor (kullanıcıya iletilecek hata metni verildi).
- `tamamliyo.URUN_ID` artık `TAMAMLIYO_URUN_ID` env'inden okunuyor (varsayılan 141).
  220 açıldığında tek satır .env değişikliği + backend restart yeterli.
- Kullanıcı kararı: **141 ile devam**, 220 açılınca geçilecek.

### İlk gerçek test poliçesi
Kullanıcı isteğiyle **220 açılana kadar ertelendi** (kimlik bilgileri de bu yüzden alınmadı).
Kart hazır (**** 1028), otomatik kesim açık, gider raporu çekimi bekliyor.

**Test**: yeni `tests/test_iteration_123_insurance_expenses.py` (14 test: fiyat ayrıştırma,
çekim kaydı, ödeme adımının çekimi kaydetmesi, tekrarlanan ödemede çift kayıt olmaması,
aylık gruplama, panel alanları, çoklu yolcu cirosu, geçersiz tarihin toplama girmemesi).
Tam suit: **467 passed / 3 skipped**.

## 2026-09-08 (6) · Kâr koruması (otomatik fiyat düzeltme + uyarı) + ürün kodu sorgusu

### Kâr koruması — `backend/insurance_margin.py` (yeni)
Kullanıcı isteği: "Bir poliçenin maliyeti satış fiyatını aşarsa fiyatı otomatik güncelleyip
beni uyar." Tek modülde 3 kontrol noktası:
- `guard_products(reason)`: aktif sigorta ürünlerini tarar. **Zarar** (satış ≤ maliyet) →
  satış fiyatı `maliyet × 2` (10 ₺'ye yuvarlı) olarak güncellenir; **ince marj**
  (%20 altı) → fiyata dokunulmaz, yalnız uyarı. Tetiklendiği yerler: günlük/elle fiyat
  senkronu (`sync_prices` sonunda), panelden fiyat/maliyet elle değiştirildiğinde
  (`PATCH /admin/products/{id}`), panelden "Şimdi kontrol et".
- `check_charge(task)`: poliçe kesiminde karttan çekilen tutar müşteriden alınan tutarı
  aşarsa (asıl zarar senaryosu) olay kaydedilir, kişi başı gerçek maliyetten yeni satış
  fiyatı hesaplanıp ürün güncellenir. Bu uyarıda **soğutma yok** (her zarar bildirilir).
  `insurance_provider._record_charge` içinden çağrılır; uyarı hatası poliçe kesimini bozmaz.
- Uyarı kanalları: yönetici e-postası + WhatsApp + panel bildirimi
  (`notifications.kind=insurance_margin_alert`). Ürün uyarılarında 6 saat soğutma.
  Son 20 olay `site_settings.insurance_margin.events` altında.
- Uçlar: `GET /admin/insurance/margin`, `POST /admin/insurance/margin/check`.
- Panel: `AdminInsurance.jsx` → **"Kâr koruması"** kartı (`insurance-margin-panel`):
  ürün bazlı maliyet/satış/kâr/marj tablosu + durum etiketi (Kârlı / İnce marj / Zarar),
  otomatik düzeltme geçmişi, "Şimdi kontrol et" butonu, son kontrol/uyarı zamanı.

### Tamamliyo ürün kodu sorgusu (220 takibi)
- `insurance_provider.probe_product(urun_id)` + `GET /admin/insurance/product-check?urun_id=`:
  fiyat sorgusu ile kodun partner hesabında satışta olup olmadığını söyler (poliçe kesmez,
  ücret çıkarmaz). Panelde "Ürün kodu satışa açık mı?" alanı (varsayılan 220).
- `tamamliyo._error_message` artık üst seviyedeki `errorMessage/errorCode` alanlarını da
  okuyor → 220 için gerçek hata görünüyor: "Fiyat bulunamadı … 758" (kod hâlâ **kapalı**).
- 141 doğrulandı: "Yurt Dışı Sağlık Destek Paketi", maliyet 244,82 ₺ → satış 490 ₺.

### Doğrulama
- `tests/test_iteration_124_margin_guard.py` (23 test): marj durumları, zararda fiyat
  yükseltme, ince marjda sadece uyarı, soğutma, çoklu yolcuda kişi başı maliyet,
  fiyat gereksizse düşürülmemesi, `_record_charge` entegrasyonu, ürün kodu sorgusu.
- Tam suit: **488 passed / 5 skipped**.
- Canlı e2e: `PATCH /admin/products/ins_7d {"price_try":200}` → fiyat otomatik 490 ₺'ye
  çıktı, olay kaydı oluştu, uyarı e-postası `info@dubaivizehatti.com` adresine
  `status=sent` gitti; panel ekran görüntüsüyle doğrulandı.

## 2026-09-08 (7) · Güven rozetleri + "Güvenlik ve Veri Koruma" sayfası
Kullanıcı isteği: "Web sitesine güvenlikle ilgili bazı sertifikalar koy ya da yazılar
güven sağlamak için." Uydurma sertifika (ISO vb.) kullanılmadı; yalnızca sistemde
gerçekten uygulanan önlemler yazıldı.
- `components/SecurityBadges.jsx` (yeni): 8 rozet — 256-bit SSL/HSTS, 3D Secure + PCI-DSS
  ödeme (kart bilgisi saklanmaz), imzalı/süreli belge bağlantıları, 90 gün sonra imha,
  şifresiz tek kullanımlık kodla giriş, KVKK uyumu, TÜRSAB A Grubu üyeliği, kötüye kullanım
  koruması (hız sınırı + sertleştirilmiş başlıklar). İki varyant: `SecurityBadges` (ızgara
  bölüm, `security-badges`) ve `SecurityMiniStrip` (tek satır, `security-mini-strip`).
- `pages/Security.jsx` + rota **`/guvenlik`**: 6 bölümlük yazılı açıklama (bağlantı, ödeme,
  belge, hesap/oturum, yetki-mevzuat, dolandırıcılığa karşı 4 kontrol), güvenlik açığı
  bildirim kutusu (ADMIN e-postası) ve yasal metin linkleri.
- Yerleşim: ana sayfada `CommitmentsStrip` altına rozet ızgarası; **başvuru sihirbazı Adım 4
  "Ödeme yöntemi"** üstüne, **sepet** özet panelinin ödeme alanına (hem vize hem
  sigorta/eSIM akışı) mini şerit; footer'a "Güvenlik ve Veri Koruma" linki
  (`footer-security-link`).
- SEO: `scripts/seo-pages.js` içine `/guvenlik` kaydı (title/description/h1 + 6 bölüm) →
  ön-render ve sitemap'e otomatik girer (priority 0.5).
- Doğrulama: /guvenlik'te 8 rozet + bildirim kutusu, ana sayfada bölüm, sepet ödeme alanında
  mini şerit ekran görüntüleriyle kontrol edildi; webpack derlemesi temiz.

## 2026-09-08 (8) · Telefon numarası +90 538 483 82 24, "DUBAI" harf gösterimi kaldırıldı
- DB `site_settings.company_info`: `phone` → **+90 538 483 82 24**, `whatsapp` → **905384838224**
  (eski test numarası 905331234567 kalmıştı; sağ alttaki WhatsApp düğmesi bu yüzden yanlış
  numarayı açıyordu). `content.py COMPANY["phone"]` statik yedeği de güncellendi.
- `components/PhoneDubai.jsx` **silindi**; navbar (masaüstü + mobil menü) ve footer artık
  numarayı düz metin gösteriyor (rakamların altındaki D-U-B-A-I harfleri kalktı).
- Doğrulama: `whatsapp-floating-button` href = `https://wa.me/905384838224?text=…`,
  footer `tel:+905384838224`, `phone-dubai` öğesi DOM'da yok; ekran görüntüsüyle kontrol
  edildi. pytest alt kümesi (content/iteration_48/refactor) 89 passed.

## 2026-09-08 (9) · Kod inceleme raporu: 3 gerçek düzeltme + 3 yanlış pozitif doğrulaması

### Uygulanan düzeltmeler
- `zami_rpa.py`: **`_auto_relogin_locked` karmaşıklığı 11 → eşik altı**. Yeni yardımcılar:
  `_relogin_block_reason` (cihaz güveni / bekleyen OTP kontrolü), `_record_auto_login`
  (oturum kaydı + log), `_relogin_attempts` (captcha deneme döngüsü). Davranış aynı.
  Ayrıca 91. satırdaki yorum yeniden yazıldı — yorumun içindeki `"exec("` metni tarayıcıların
  "exec kullanımı" yanlış pozitifini üretiyordu.
- `insurance_tasks.py`: **`expense_report` 62 satır → 20 satır**; `_charge_buckets`
  (aylık toplama) ve `_charge_detail` (tek çekim satırı) ayrıldı. Uç yanıtı bire bir aynı
  (`/admin/insurance/expenses` canlı doğrulandı).
- Test betikleri: `regression_critical_tests.test_zami_mapping_verification` 7 ayrı if
  bloğu yerine tek `checks` listesi + döngü (90 → ~55 satır, karmaşıklık 12 → 4);
  `backend_test.test_brand_name_in_backend` iki yardımcıya bölündü
  (`_check_brand_asset`, `_check_brand_content_site`, karmaşıklık 13 → 3).
- Doğrulama: `ruff --select C901 (max-complexity=10)` → **0 bulgu**; tam pytest
  **490 passed / 3 skipped**.

### Yanlış pozitifler (kod değişikliği gerekmedi, tekrar doğrulandı)
- **"zami_rpa.py:91 exec() güvenlik açığı"**: dosyada `exec()`/`eval()` çağrısı YOK; ilgili
  satır `asyncio.create_subprocess_exec` (sabit argv ile playwright kurulumu) ve tarayıcının
  eşleştiği metin bir YORUM içindeydi. Yorum yeniden yazıldı ki rapor tekrarlanmasın.
- **"18 tanımsız değişken"**: `ruff --select F821` → *All checks passed*.
- **"`is` ile sabit karşılaştırma"**: `ruff --select F632,E711,E712` → 0 bulgu; zami_rpa/zami/
  whatsapp/zami_status/wa_cloud dosyalarında ` is "..."` kalıbı hiç yok (tüm kullanımlar
  `is None` / `is not None`).
- **"routes_admin.py 35 import"**: gerçek sayı **27** import satırı, 1234 satır dosya. Modül
  bölme (P2) risk/fayda dengesi nedeniyle yapılmadı; istenirse `routes_admin_content.py` +
  `routes_admin_reports.py` olarak ayrılabilir (mağaza/sigorta uçları zaten
  `routes_admin_store.py` içinde ayrı).

## 2026-09-08 (10) · Mobilde WhatsApp telefon maketi kısaltıldı
Kullanıcı: "cepten bakınca cep telefonu çok uzun görünüyor."
- `WhatsAppPhoneMock`: sohbet alanı mobilde `h-[498px]` (masaüstünden bile uzundu) →
  **`h-[320px]`**, 420px üstü ekranlarda 380px, `sm:` ve üstünde 452px (masaüstü aynı kaldı).
  Nokta göstergesi boşluğu mobilde `mt-8` → `mt-5`.
- Sonuç: 390px genişlikte maketin toplam yüksekliği ~700px'ten **569px**'e indi (telefon
  gövdesi ~470px); son mesajlar yine `justify-end` ile görünür kalıyor.

## 2026-09-08 (11) · Canlıdaki eski WhatsApp numarası + maket başlığı
- **Kök neden**: önizleme ve canlı ortamların MongoDB'leri ayrı. Numarayı yalnızca önizleme
  veritabanında güncellemiştik; canlıda `company_info.whatsapp = 905331234567` (demo değer)
  kaldığı için sağ alttaki WhatsApp düğmesi hâlâ +90 533 123 45 67 açıyordu.
- Çözüm: `server.fix_placeholder_contact()` açılış göçü — `company_info` içindeki bilinen
  demo numaralar (905331234567 / 905337438224 / 908500000000 ve "+90 533 123 45 67",
  "+90 533 743 82 24", "+90 850 000 00 00") `content.COMPANY` değerleriyle değiştirilir; elle
  girilmiş gerçek numaralara dokunulmaz. `_init_startup_state` içinde çalışır, yani **canlı
  ortam yeni deploy'da kendini düzeltir** (log: "placeholder contact fixed").
  `tests/test_iteration_125_placeholder_contact.py` (11 test).
- `WhatsAppPhoneMock` başlığı: "Dubai Vize Hattı" artık kırpılmıyor (`truncate` kalktı,
  12.5px/13px, satır yüksekliği 15px), "çevrimiçi" ile arasındaki boşluk daraltıldı
  (11px → 10px, leading 13px), avatar mobilde 32px, isim bloğuna `pr-3.5` ile telefon/⋮
  ikonlarından ayrı durması sağlandı. 390px'de ölçüldü: başlık tam görünüyor (97px).
- Maket durum çubuğunda pil yüzdesi ("86" kutusu) yerine **5G** yazısı gösteriliyor.
- Sohbet balonu köşeleri gerçek WhatsApp geometrisine çevrildi: köşe yarıçapı 7px, kuyruk
  tarafındaki üst köşe düz (`rounded-tl-none` / `rounded-tr-none`) ve kuyruk artık üçgen
  clipPath değil, WhatsApp'ın kıvrımlı SVG kuyruğu (gelen solda beyaz, giden sağda #D9FDD3).
- Maket bakış açısı çevrildi (kullanıcı seçimi "a"): artık **bizim WhatsApp Business
  hesabımızdan** görünüyor — kurum cevapları sağda yeşil (mavi tik), müşteri soruları
  solda beyaz (kuyruk sol altta). Başlık müşteri adını gösteriyor (senaryo başına
  Ayşe K. / Mehmet T. / Elif D. / Burak Y.), avatar baş harfli daire
  (`wa-phone-contact`). Yeşil balonda kuyruk/çıkıntı yok, dört köşe yuvarlak.

## 2026-09-08 (12) · Yeni sohbet senaryosu + mobil kısaltma turu 1. tur
- `WhatsAppPhoneMock`: 5. senaryo **"Onay ve PDF teslimi"** (Selin A.) eklendi — durum sorusu,
  "Vizeniz ONAYLANDI" mesajı, **PDF ek balonu** (yeni `doc` tipi: kırmızı dosya ikonu, dosya
  adı + "1 sayfa · 214 KB · PDF"), yazdırma gerekmediği bilgisi ve iyi yolculuk dileği.
- Mobil kısaltma (masaüstü görünüm aynı):
  - `SecurityBadges`: mobilde 2 kolon + kompakt kart (açıklama `sm:` üstünde görünür) →
    **1870px → 786px**.
  - `HomeBundleStrip`: mobilde yatay kaydırmalı (snap) şerit + "yana kaydırın" ipucu,
    `lg:` üstünde eski 3'lü ızgara → **2173px → 1133px**.
  - Ana sayfa toplam mobil yüksekliği **21.987px → 19.863px** (%10 kısaldı).
- Kalan uzun bölümler (390px'de): visa-showcase 1658, easy-compare 1631, ask-first 1513,
  hero 1294, documents 1216, insurance-strip 1199, commitments 1090, visa-specimen 1066,
  tour-strip 1034. Sıradaki turda kullanıcı seçimine göre kısaltılacak.
- Deploy hazırlık kontrolü (deployment_agent): **pass** — gizli anahtar/URL sızıntısı,
  port/CORS, derleme hatası yok. Yayına alma kullanıcının "Deploy" butonuna basmasıyla olur.

## 2026-09-08 (13) · Mobil kısaltma 2. tur (hero, vize türleri, karşılaştırma, belgeler)
Masaüstü görünüm hiçbir bölümde değişmedi (tüm değişiklikler `sm:`/`md:`/`lg:` altında).
- **Hero** (`Home.jsx`): mobilde üst etiket, 3'lü "kolaylık" çipi ve ikinci buton gizlendi;
  tek mesaj (dönen başlık + kapanış cümlesi) + tam genişlik **tek buton** kaldı. `VisaExplainer`
  artık mobilde "Nasıl çalışıyor? 60 saniyede anlatalım" düğmesiyle açılıyor
  (`hero-explainer-toggle`, tek bileşen örneği; `sm:` üstünde her zaman açık).
  **1294px → 494px**.
- **VisaShowcase**: mobilde yatay snap kaydırma (kart genişliği %80), `sm:` üstünde eski
  2/3 kolon ızgara. **1658px → 635px**.
- **EasyCompare**: mobilde satır düzeni "etiket üstte, Biz | Klasik acente yan yana" oldu
  (yazı 12px, etiketler kısaltıldı), `md:` üstünde tablo aynı. **1631px → 1131px**.
- **Gerekli belgeler** (`landing-documents`): mobilde ilk 2 kart görünüyor, "Tüm belgeleri gör (4)"
  düğmesi (`documents-show-all`) kalanları açıyor; `sm:` üstünde hepsi açık. **1216px → 884px**.
- Ana sayfa mobil toplam yükseklik: **19.863px → 17.208px** (ilk ölçüme göre %22 kısaldı).

## 2026-09-09 · Mobil kısaltma 3. tur + sepet hatırlatması 3 saat + hero sloganı
### Mobil kısaltma (masaüstü değişmedi)
- `HomeInsuranceStrip`: mobilde padding 28→20px, plan kartları p-3, avantaj listesi 12px,
  "Sepetim" butonu mobilde gizli (navbar'da sepet var), ana CTA tam genişlik, görsel paneli
  min-h 240→150px. **1199 → 927px**
- `HomeTourStrip`: aynı kompaktlama + tur fotoğrafları mobilde **2 kolon** (min-h 110px).
  **1034 → 658px**
- `CommitmentsStrip`: satır dolguları ve yazı boyları mobilde küçültüldü, taahhüt kartları
  p-4 + 14px başlık. **1090 → 848px**
- Ana sayfa mobil toplam: **17.208 → 16.318px** (bugünün başlangıcı 21.987px, toplam %26 kısaldı).

### Sepet hatırlatması 3 saat
- `cart_reminders.REMINDER_STAGES_HOURS`: `[2, 24]` → **`[3, 24]`**; 1. hatırlatma konusu
  "Sepetinizi tamamlamak ister misiniz?" ve metni daha nazik ("acele etmeniz gerekmiyor").
- Canlı e2e: 4 saat öncesine alınmış test sepeti için süpürme çalıştı → e-posta
  `status=sent`, `stage=1`, `reminders_sent=1` (log: "cart reminder sweep: 1 gonderildi").
  Test kaydı sonrasında silindi. `tests/test_iteration_126_cart_reminder_3h.py` (13 test).
- Not: akış zaten vardı (sepette e-posta girildiğinde `cart_snapshots`'a kayıt); yalnızca
  ilk hatırlatma süresi ve dili değişti.

### Hero sloganı
- `HeroHeadline`: "Dubai vizeniz **2 iş gününde hazır**" → "Dubai vizeniz **36 saatte hazır**".
  Diğer metinlerde ("ortalama 2 iş gününde") değişiklik YAPILMADI — kullanıcı onayı bekliyor:
  VisaTypes SSS, VisaExplainer notu, seo-pages/prerender açıklamaları, visa_guides SEO metni.

### Test hijyeni
- `test_iteration_111_daily_digest`: gün seçimi gerçek "son gönderim" kaydıyla çakışabiliyordu
  (bugün-2 = 07.09 kaydı) → test artık işaretçiyi kendisi sıfırlıyor; kalıcı flaky giderildi.
- Hero slogan güncellemeleri (`HeroHeadline`, 5 slogan döngüsü):
  1. "Dubai vizeniz / **36 saatte hazır**" (eski: 2 iş gününde hazır)
  2. "**Sadece pasaport ve resminizle** / Dubai vizeniz hazır" (eski: Sadece 2 belgeyle)
  3. "**Üstelik uçak bileti ve / otel rezervasyonu da gerekmiyor**" (eski: Bilet ve otel
     şartı yok / sadece pasaport ve fotoğraf — pasaport-fotoğraf ifadesi bu slogandan
     kaldırıldı, alt metin de sadeleştirildi)
  4-5. Aile ve "pasaportunuzu yükleyin" slogancıkları aynı kaldı.
  Beşi de canlı önizlemede tek tek doğrulandı.

## 2026-06-15 (fork · Instagram profesyonelleşme + Tamamliyo cari bakiye + PDF hizalama)

### Instagram gönderileri yeniden tasarlandı (12/12)
- Eski krem zeminli çizgi illüstrasyonlar bırakıldı; artık **gerçek Dubai fotoğrafı +
  sinematik lacivert degrade + Anton kalın manşet** düzeni kullanılıyor (ajans görünümü).
- Yeni betik: `/app/scripts/instagram_pro_posts.py` (3 düzen: `hero`, `band`, `list`/`steps`).
  Kaynak fotoğraflar `/app/frontend/public/instagram/photos/src-XX.jpg`
  (10 stok Unsplash/Pexels + 2 Gemini 3.1 Flash üretimi: belge flat-lay, Dubai'de aile).
- Font: `/app/scripts/fonts/Anton.ttf` (manşet) + Figtree (gövde) — Türkçe glifleri doğrulandı.
- Her görselde: logo + BAE bayrağı, "TÜRSAB BELGELİ" altın çerçeve etiketi, altın eyebrow,
  manşet, tek satır destek metni, altta domain + WhatsApp şeridi. 1080x1350 (4:5).
- `backend/instagram_posts.py`: başlıklar görsellerle eşleştirildi, açıklama metinleri
  kısaltılıp profesyonelleştirildi, her metnin sonuna sabit CTA (WhatsApp + site) eklendi,
  hashtag setleri düzenlendi, görsel yolları `?v=2` ile önbellek kırıldı.
- `site_settings.instagram_calendar` kaydı silinerek yeni metinlerle yeniden tohumlandı.
- NOT: Instagram hesabı halen AÇILMADI (kullanıcı "login yapamıyorum" dedi; hesabı
  kullanıcının kendisi açacak — panelde adım adım kurulum kartı duruyor).

### Tamamliyo ödemesi cari bakiyeye alındı (kullanıcı isteği, P0 güvenlik)
- `tamamliyo.payment_type()` / `balance_mode()`: `TAMAMLIYO_PAYMENT_TYPE` (varsayılan **3 =
  cari bakiye**, `2` = kurumsal kart). `pay_for_quote` cari bakiye modunda kart alanı GÖNDERMEZ.
- `.env`: `TAMAMLIYO_CARD_NUMBER/EXPIRY/CVV/NAME/SURNAME` **boşaltıldı** (kart + CVV verisi
  sunucudan tamamen kaldırıldı), `TAMAMLIYO_PAYMENT_TYPE=3` eklendi.
- `card_configured()` cari bakiye modunda True → bekleyen poliçe kuyruğu kart yüzünden durmaz.
- Uyarı/hata metinleri ve `AdminInsurance.jsx` panel metinleri "cari bakiye" diline çevrildi.
- Bakiye yetersizse davranış: poliçe `waiting_payment` kuyruğunda bekler, 15 dk'da bir tekrar
  denenir, admine e-posta + WhatsApp uyarısı gider (mevcut mekanizma).
- Testler: `tests/test_iteration_130_tamamliyo_balance.py` (11 test) + 118/119 kart modu
  testleri `TAMAMLIYO_PAYMENT_TYPE=2` ile güncellendi. Tüm suite: **551 passed**.

### Başvuru formu PDF düzeltmeleri
- "HİZMET BEDELİ DÖKÜMÜ" tutarları artık yolcu tablosundaki **Tutar kolonuyla tam aynı
  hizada** bitiyor (yeni `amount` sağa dayalı paragraf stili; Paragraph'lar TableStyle ALIGN'ı
  yok saydığı için stil düzeyinde çözüldü).
- QR bandı tamamen **ortalandı** (QR üstte, başlık/metin/takip kodu altında ortalı) ve metin
  güncellendi: "Kodunu kamerayla okutun; başvurunuzun güncel durumu anında açılsın."
- Alt bilgi (footer): "Birleşik Arap Emirlikleri'ndeki grup şirketimiz ... FZE'dir." cümlesi
  artık tek satırda (açık `<br/>` ile bölündü).

### Marka/işletici bildirimi metni güncellendi (2026-06-15)
- `content.affiliation_note()` yeni metin: "Dubai Vize Hattı, **Moruya Travel Solutions Turizm
  Ltd. Şti.**'nin tescilli markası olup, tüm hizmet ve operasyonlar bu şirket tarafından
  yürütülmektedir. Birleşik Arap Emirlikleri'ndeki grup şirketimiz **Moruya Travel Solutions
  FZE**'dir." → site alt bilgisi (Footer), Hakkımızda, KVKK ve Şartlar sayfaları tek kaynaktan
  bu metni okuyor (`/api/content/site`, `/api/content/legal`).
- `application_pdf._footer_paragraph` artık aynı metni `affiliation_note()`'tan alıyor
  (yıldız işaretleri temizlenip cümleler ayrı satırlara bölünüyor) — PDF ve site birebir aynı.
- Not: tekrarlanan tam suite koşularında `/api/contact` 429 (saatlik IP limiti) verip
  contact testlerini düşürebiliyor; backend restart sayaçları sıfırlıyor (ortam artefaktı).

### Yanlış cep telefonu (canlı site) · 2026-06-15
- Kök neden: **canlı (production) veritabanında** `company_info.phone = "+90 532 588 26 30"`
  kalmış. Doğrulama: `curl https://dubaivizehatti.com/api/content/site` → phone 532...,
  whatsapp doğru (905384838224). Önizleme veritabanı doğruydu (+90 538 483 82 24) —
  iki ortamın DB'si ayrı. Frontend'de hardcode numara YOK (`lib/contact.js` fallback boş).
- Düzeltme 1: `server.PLACEHOLDER_CONTACT` listesine eski/test numaraları eklendi
  (`+90 532 588 26 30`, `+905325882630`, `905325882630`) → `fix_placeholder_contact()`
  her açılışta (her ortamda) bu değerleri gerçek numarayla değiştiriyor. Önizlemede
  canlı denendi: numara elle bozuldu → backend restart → otomatik düzeldi.
- Düzeltme 2: `PUT /api/admin/company` artık tüm `value` nesnesini değiştirmiyor;
  alan bazında (`$set: value.<alan>`) birleştiriyor → kısmi kayıt diğer iletişim
  alanlarını silmiyor. (Model `legal_name` zorunlu olduğu için kısmi PUT zaten 422.)
- Testler: `tests/test_iteration_131_company_contact_guard.py` (3) + 125 parametreleri
  genişletildi. Tüm suite: **555 passed / 5 skipped**.
- Kullanıcı aksiyonu: canlıda numara ya bir sonraki deploy'da kendiliğinden düzelir ya da
  hemen Admin → Acente Bilgileri ekranından güncellenebilir.

## 2026-06-16 (fork) · Teklif Linkleri (paylasilabilir teklif · P2 backlog)
Roadmap'teki "paylasilabilir aile paketi linki" maddesi hayata gecirildi: yonetici
WhatsApp'ta konusurken hazir bir teklif olusturuyor, musteri linki acip tutari goruyor ve
tek tikla ayni secimlerle basvuru formuna geciyor.

### Backend
- Yeni `backend/offer_links.py`: 12 karakterlik tahmin edilemez jeton (`secrets.token_urlsafe`),
  gecerlilik (varsayilan 14 gun, en fazla 90), durum makinesi (`active` > `used` > `expired` >
  `disabled`), `wa_number()` TR numara normalizasyonu, hazir WhatsApp paylasim metni,
  `price_offer()` (fiyat basvuru akisiyla ayni: `compute_pricing` + `resolve_store_lines` +
  `addon_prices_try`), `public_view()` (her goruntulemede yeniden fiyatlar; urun pasife
  alinmissa kayitli tutara duser), `mark_used()` donusum takibi.
- `db.py`: `offer_links` koleksiyonu + `token` unique index.
- `models.py`: `OfferTravelerIn`, `OfferLinkIn`; `ApplicationCreate.offer_token`.
- Admin uclari (`routes_admin.py`): `GET/POST /api/admin/offer-links`,
  `DELETE /api/admin/offer-links/{id}` (linki kapatir, kayit gecmiste kalir).
- Musteri ucu (`routes_public.py`): `GET /api/offers/{token}` — IP basina saatte 120 istek
  siniri, goruntulenme sayaci, kapatilmis/suresi dolmus/bilinmeyen jeton icin 404 (ayri metin).
  `POST /api/applications` icinde `offer_links.mark_used()` ile teklif basvuruya baglanir.
- **Gizlilik**: public yanitta yalniz musteri ADI var; telefon/e-posta gonderilmez (link
  sizarsa kisisel veri acilmasin). Basvuru formu da yalniz adi on dolduruyor.

### Frontend
- Yeni `pages/AdminOffers.jsx` + route `/admin/teklifler` (menu: Musteri Iletisimi ->
  "Teklif Linkleri"): yolcu satirlari (yetiskin/cocuk + vize tipi), ekspres anahtari,
  sigorta/eSIM/tur secimi, opsiyonel tarihler, musteriye gorunen not, gecerlilik gunu;
  `POST /api/pricing/quote` ile CANLI tutar; olusturunca link panoya kopyalanir ve
  "WhatsApp'tan gonder" butonu hazir metinle wa.me'yi acar. Liste: durum rozeti, tutar,
  goruntulenme, donusen basvurunun referans kodu, Kopyala / Kapat.
- Yeni `pages/Offer.jsx` + route `/teklif/:token` (noindex): teklif tutari, yolcu ve vize
  satirlari, fiyat dokumu (aile/paket/sigorta indirimleri dahil), gecerlilik etiketi, not,
  "Basvuruyu tamamla" CTA'si, WhatsApp'tan soru sor, TURSAB guven satiri; hata durumunda
  offer-error karti + yeni teklif isteme CTA'si.
- `Apply.jsx`: `?teklif=<token>` okunup yolcu sayisi/vize tipleri, ekspres, sigorta, eSIM,
  tur (tarih/saat) ve tarihler forma yukleniyor; ustte "Size hazirlanan teklif" bandi
  (`apply-offer-banner`) ve gonderimde `offer_token` tasiniyor.
- **Onemli kural**: sihirbaz sigortayi her zaman kisi basi ekliyor; teklif formunda sigorta
  adedi yolcu sayisina esitlendi -> teklif tutari ile basvuru ozeti birebir ayni.

### Test
- `backend/tests/test_iteration_133_offer_links.py` (15 test): jeton/durum/wa numarasi/paylasim
  metni, admin olusturma, tutarin `/pricing/quote` ile ayni olmasi, listeleme, jetonsuz erisim,
  gecersiz vize tipi 400, musteri ucu + goruntulenme sayaci, kapatma/suresi dolma/bilinmeyen
  jeton 404, `mark_used` donusumu. Tum suite: **590 passed / 3 skipped**.
- testing_agent iteration_118: frontend **%100** (9/9 senaryo, defect yok). Dogrulandi: canli
  tutar 5.190 -> 15.364 ₺ akisi, WA href, teklif sayfasi, basvuru on dolumu ve
  `apply-offer-total` = `wizard-stepper-total` = `summary-total-price` esitligi.
- Test sirasinda olusan 13 teklif kaydi DB'den silindi (panel temiz).
- Teknik borc (testing_agent notu): `AdminOffers.jsx` 535 satir; OfferForm/OfferList/
  useLiveQuote olarak bolunebilir (islev etkilenmiyor).

## 2026-06-16 · Kod inceleme raporu: 3 gercek duzeltme + 2 yanlis pozitif (olcumlu)
Kullanicinin paylastigi rapor madde madde **olculdu**; yalniz gercek olanlar duzeltildi.

### Duzeltilenler
1. **Dairesel import (GERCEK, yapisal duzeltme)**: `offer_links` fiyatlama icin
   `routes_public`'i fonksiyon icinde (lazy) import ediyordu; `routes_public` da
   `offer_links`'i import ediyordu -> grafta dongu. Cozum: ortak fiyatlama yardimcilari
   route dosyasindan **`store_catalog.py`**'ye tasindi:
   `parse_iso_date`, `trip_day_count`, `_store_line_validity`, `_store_line`,
   `resolve_store_lines`, `get_visa_type`. `routes_public` bunlari artik katalogdan import
   ediyor (9 `_parse_iso_date` cagrisi `parse_iso_date` olarak guncellendi), `offer_links`
   ise **modul seviyesinde** `store_catalog`/`content`/`fx`/`models` import ediyor.
   Sonuc: tum backend'de **modul seviyesi dongu = 0** (ast ile dogrulandi) ve
   `offer_links -> routes_public` bagi tamamen kalkti. Tekrarlamamasi icin regresyon testi:
   `test_iteration_133_offer_links.py::test_modul_seviyesinde_dairesel_import_yok`.
2. **Rota dosyasi ayrimi (kismi)**: teklif uclari `routes_admin.py`'den cikarilip yeni
   **`routes_admin_offers.py`** (53 satir, 7 import) dosyasina alindi ve `server.py`'de
   ayri router olarak baglandi. `routes_admin.py` import sayisi 39 -> **30**,
   `routes_public.py` 32 -> **30**.
3. **Uzun fonksiyonlar (GERCEK)**:
   - `insurance_margin.guard_products` 54 -> **23 satir** (`_apply_price_guard`,
     `_price_fixed_event`, `_low_margin_event` cikarildi). NOT: ilk denemede yardimciya
     `_raise_price` adi verildi, dosyada ayni isimde baska fonksiyon vardi ve
     `test_iteration_124` 3 testi kirildi -> `_apply_price_guard` olarak yeniden adlandirildi.
   - `insurance_provider.sync_prices` 51 -> **21 satir** (`_sync_product`,
     `_save_sync_state`).
   - `offer_links`: `price_offer` (`_visa_row`/`_visa_rows`), `create_offer`
     (`_customer_fields`/`_tracking_fields`), `public_view` (`_repriced`) olarak bolundu;
     hepsi 34 satirin altinda ve mccabe karmasikligi 1.

### Yanlis pozitifler (olculdu, kod degistirilmedi)
- **"20 tanimsiz degisken"** -> `ruff check --select F821` = **0 hata**; `import server` temiz.
- **"230 hatali esitlik karsilastirmasi (`is` vs `==`)"** -> raporlanan 14 satirin tamami
  `is None` / `is not None` / `is False` (dogru Python deyimi). `ruff --select F632,E711,E712`
  = **0 hata**. (Bu bulgu 3. kez geldi; `visitors.py:67` `is False` bilincli:
  `None` ile `False`'i ayirt ediyor.)
- **"Yuksek karmasiklik"** -> `payment_receipt_pdf._application_items` iddia 11, olculen **5**;
  `_application_summary_rows` iddia 13, olculen **3**; `offer_links` fonksiyonlari **1**.
  (ruff mccabe, esik 10 ile hicbir uyari yok.) Fatura PDF'i kirilma riski nedeniyle
  dokunulmadi.
- `routes_admin.py`/`routes_public.py`'nin domain bazli tam bolunmesi **yapilmadi**
  (yuksek regresyon riski, dusuk kazanc) -> ROADMAP P2 teknik borcunda duruyor.

### Dogrulama
- `pytest`: **589 passed / 3 skipped** (aynı saatte ust uste 3 kez calistirilinca
  `/api/contact` saatlik IP limiti 429 verip 4-6 testi dusuruyor — ortam artefakti;
  backend restart sonrasi ilgili 52 test yeniden PASS).
- Uctan uca: teklif olustur -> `/teklif/<token>` -> `/basvuru?teklif=` akisi cocuk vizeli
  ornekle yeniden dogrulandi (13.312 ₺ teklif = banner = sihirbaz toplami).
- Test verileri temizlendi (25 teklif kaydi silindi).

## 2026-06-16 · Ilk acilista cıplak SEO metni gorunmesi duzeltildi (FOUC)
**Sikayet**: "sayfa acilirken bu cikiyor ilk" — ekran goruntusunde stilsiz, upuzun bir metin
sayfasi (vize fiyatlari + SSS) goruluyordu.

**Kok neden**: `frontend/scripts/prerender.js` (build sonrasi 31 sayfa icin statik SEO HTML
uretir) SEO icerigini `<div id="seo-prerender">` olarak dogrudan `#root` icine yaziyordu.
React paketi (main.*.js, ~1 MB) yuklenip `#root`'u devralana kadar tarayici bu blogu **stilsiz
metin** olarak gosteriyordu; yavas baglantida 1-3 saniye suruyor.

**Cozum** (`scripts/prerender.js`):
- `#seo-prerender` artik ekrandan kaldirilmis (`position:absolute;left:-10000px;1x1`) — metin
  DOM'da kaldigi icin JS calistirmayan bot'lar icerigi okumaya devam eder (SEO kaybi yok).
- Yerine marka acilis ekrani: logo (preload'lu, `fetchpriority=high`), altin renkli ilerleme
  cubugu animasyonu ve "DUBAİ VİZE HATTI YÜKLENİYOR…" satiri. React ilk render'da `#root`
  cocuklarini sildigi icin kendiliginden kayboluyor.
- **JS kapali** ziyaretciler icin `<noscript><style>` ile SEO blogu tekrar okunabilir hale
  gelir (spinner'da kalmaz).
- **Paket hic yuklenemezse** 8 saniye sonra devreye giren inline yedek: splash gizlenir,
  `#boot-style` kaldirilir ve metin 52rem'lik okunur bir kolona acilir. (Ilk denemede
  `!important` kurali inline stili ezdigi icin yedek calismiyordu; `boot-style` elementi
  kaldirilarak duzeltildi.)
- `cleanTemplate()` yeni `<style>`/`<link rel=preload>`/`<noscript>` bloklarini da temizliyor
  (script tekrar kosuldugunda cift enjeksiyon olmasin).

**Dogrulama**: `yarn build` (31 sayfa) + yerel statik sunucuda Playwright ile 3 senaryo:
(1) paket engelli 0.4 sn -> marka ekrani gorunuyor, cıplak metin YOK;
(2) 8 sn sonra -> metin okunabilir kolona aciliyor (832 px);
(3) normal yukleme -> splash ve SEO blogu kalkiyor, site normal render oluyor.
Ayrica yeni build'in JSON-LD telefonu **+90 538 483 82 24** (canlidaki eski build'de
+90 532 588 26 30 kalmisti) -> **bir sonraki deploy structured data telefonunu da duzeltir.**

**NOT**: Duzeltme build zamaninda uretildigi icin canliya ancak **yeni bir deploy** ile iner.

## 2026-06-16 · Adres degisikligi, e-posta kunyesi, konu satiri ve iletisim sayfasi sadelestirme

### 1. Yeni sirket adresi (site + e-posta + PDF)
Eski: "Maltepe Mah., Eski Çırpıcı Yolu Sk. No:8, Parima Plaza Kat:12 Ofis:146, 34010
Zeytinburnu / İstanbul". Yeni: **"Büyükdere Caddesi Nurol Plaza No:255/B02, 34450 Sarıyer /
İstanbul - Türkiye"**.
- `content.py` COMPANY["address"] guncellendi (PDF, e-posta ve yasal metinlerin kaynagi).
- Admin API (`PUT /api/admin/company`) uzerinden **hem preview hem CANLI (prod) veritabani**
  guncellendi. DIKKAT: bu uc gonderilmeyen alanlari bos string ile ezebiliyor; bu yuzden once
  `GET /api/admin/company` ile mevcut kayit okunup tam nesne geri yazildi (telefon/e-posta/
  calisma saatleri korundu). Ayni yontem ileride de kullanilmali.
  (urllib ile cagrida `User-Agent` sart: varsayilan python-urllib UA'sina ingress 403 veriyor.)
- Frontend metinleri: `Contact.jsx` meta aciklamasi ve `CommitmentsStrip.jsx` "İstanbul ·
  Zeytinburnu" -> "İstanbul · Sarıyer".
- Dogrulama: form PDF + fatura PDF metninde yeni adres var/eski adres yok; canli
  `/iletisim` sayfasi ve `/api/content/site` yeni adresi donuyor.
- NOT: canli **yasal sayfalar (KVKK vb.)** ve prod surecinin urettigi PDF/e-posta alt bilgisi
  `content.py` sabitini bellekte tuttugu icin **yeni deploy'a kadar** eski adresi gosterebilir.

### 2. E-posta alt bilgisi artik PDF kunyesiyle birebir ayni
- Yeni tek kaynak: `content.brand_footer_lines()` -> 4 satir (unvan · TÜRSAB üyesi A Grubu ·
  telefon · e-posta · site / adres / marka-isletici notu / BAE grup sirketi).
- `application_pdf._footer_paragraph()` bu fonksiyonu kullaniyor (PDF cikitisi ayni kaldi,
  form/fatura notu en sona ekleniyor).
- `emailer._contact_footer()` yeniden duzenlendi: ust blokta marka + tiklanabilir iletisim
  linkleri + Dubai ofisi/calisma saatleri, en altta cizgiyle ayrilmis kunye blogu ve
  "Bu e-posta ... yanitlayabilirsiniz" notu. Tekrar eden unvan/TÜRSAB satirlari ve ikinci
  Istanbul adresi kaldirildi (adres kunyede 1 kez geciyor).

### 3. Yonetici bildirimi konu satirinda yolcu adi ve alinan hizmetler
- `emailer.admin_subject(doc)`: `Yeni başvuru: DV-PD884784 - Ekrem Sayaner - Vize + eSIM
  (1 yolcu)`. Isim ilk yolcudan (yoksa iletisim adindan), hizmetler `store_items` kind'larindan
  (Sigorta / eSIM / Tur) ve `addons.express` (Ekspres) ile uretilir.
- `routes_public._send_application_emails` artik bu fonksiyonu kullaniyor.

### 4. Iletisim sayfasi sadelestirildi (kullanici talebi)
- Sag kolondaki **"Sosyal medyada takip edin"** karti ve **"Başvurunuz zaten var mı? /
  Başvuru takip sayfası"** karti kaldirildi (`Contact.jsx`); kullanilmayan `SocialIcon`
  import'u temizlendi.

### 5. Kur kaynakli kirilgan test duzeltildi
- `tests/test_iteration_102_family_quote.py`: tur/sigorta/eSIM tutarlari sabit yazildigi icin
  USD kuru degisince (tur 2.220 -> 2.230 TL) 2 test kiriliyordu. Beklenen tutarlar artik
  API'nin donen birim fiyatlarindan hesaplaniyor (indirim orani ve vize tutarlari sabit kaldi).
- Suite: **591 passed / 3 skipped** (tek kalan hata, ust uste calistirmada tetiklenen
  60 sn hesap kodu bekleme siniri; tek basina PASS).

## 2026-06-16 · Footer kunyesi iki satira ayrildi
`Footer.jsx`: marka/isletici notu tek paragraf halinde akiyordu. Metin "Birleşik Arap"
oncesinden bolunup iki ayri `<p>` olarak yaziliyor:
1) "Dubai Vize Hattı, **Moruya Travel Solutions Turizm Ltd. Şti.**'nin tescilli markası olup..."
2) "Birleşik Arap Emirlikleri'ndeki grup şirketimiz **Moruya Travel Solutions FZE**'dir."
Kaynak metin backend'den (content.affiliation_note) tek string geldigi icin bolme goruntuleme
katmaninda yapildi; About sayfasi ve PDF/e-posta kunyesi degistirilmedi (PDF'te zaten
alt alta). Ekran goruntusuyle dogrulandi (2 satir, kalin sirket adlari korunuyor).

## 2026-06-16 · Paket kartlarinda secim cercevesi tiklamayla tasiniyor
`components/PlanShowcase.jsx` (eSIM + seyahat sigortasi sayfalari): altin cerceve artik
"en cok tercih edilen" karta sabit degil. `selectedId` state'i eklendi; baslangicta populer
karta (yoksa ilkine) atanir, kullanici baska bir karta tiklayinca cerceve + yumusak golge o
karta gecer. Populer kart yalnizca "EN ÇOK TERCİH EDİLEN" etiketini korur. Sepette olan urun
yesil cerceveyle isaretlenmeye devam ediyor (oncelik: sepet > secim > notr).
Kart uzerine gelince hafif primary kenarlik ipucu ve `cursor-pointer`, testler icin
`data-selected="true|false"`. Playwright ile dogrulandi: baslangic 3GB secili -> 10GB'a
tiklaninca secim 10GB'a gecti.

## 2026-06-16 · Cep telefonu alani: "5" artik yazili degil, silik maskede
`Apply.jsx`: iletisim adiminda telefon alani `"+90 5"` degeriyle basliyordu, yani "5"
kullanicinin yazdigi gercek bir karakter gibi koyu gorunuyordu. Baslangic degeri ve odak
(onFocus) davranisi `"+90 "` olarak degistirildi; "5XX XXX XX XX" tamami silik maske
katmaninda (`phone-mask-hint`) gosteriliyor. Yazma akisi degismedi: 5384838224 ->
"+90 538 483 82 24". Playwright ile dogrulandi.

## 2026-06-16 · Vize karsilastirma tablosu: genis modal + ortalanmis kolonlar
- `Apply.jsx` karsilastirma modali `max-w-4xl` (896px) -> `max-w-[min(96vw,1360px)]`.
  Artik tablo dikey kaydirma gerektirmiyor ve satirlar sikismiyor.
- `VisaComparison.jsx`: vize kolonlarinin basligi, govde hucreleri ve secim butonlari
  `text-center` ile ortalandi ("Karsilastirma" etiket kolonu solda kaldi); "en cok tercih
  edilen" rozeti de kolonda ortalandi.
- "30/60 günlük tek girişli çocuk vizesi ile başvurulur" alt notu tek satirda: bu satir icin
  `subNoWrap` bayragi eklendi (mono font yerine normal font + `whitespace-nowrap`); diger alt
  notlar (kur bilgisi) mono kaldi.
- Playwright: `/vize-tipleri` tablo 1102px, modal 1360px; her iki cocuk notu **1 satir**;
  hucre hizalamasi `center`.

## 2026-06-17 · Sigorta/eSIM 3 secenek karti, satir ici vize+tarih duzenleme, iletisim sayfasi
### Sigorta ve eSIM icin detayli 3 secenek (kullanici istegi)
- Yeni bilesen `frontend/src/components/ExtraOptions.jsx` (ExtraOptions + OptionCard):
  rozet satiri (min-h ile hizali), urun adi, buyuk vurgu satiri (sigorta: teminat + gun,
  eSIM: veri + gun), "neden bu paket" cumlesi, en fazla 2 fayda maddesi, tarih penceresi,
  kisi/adet basi fiyat, "Bu paketi sec / Secildi - Kaldir" butonu, eSIM'de kart ici adet
  arttir/azalt (stopPropagation ile karti kapatmaz).
- `Apply.jsx`: eski aç/kapa anahtarlari (`extra-toggle-insurance`, `extra-toggle-esim`)
  kaldirildi; yerine 2. adimda (kod: step===1) ve Odeme adiminda (step===3) ayni
  `insuranceBlock` / `esimBlock` render ediliyor.
  Basliklar: "Size uygun seyahat saglik sigortasi onerilerimiz",
  "Seyahatinize en uygun eSIM onerilerimiz". Rozetler: Size en uygun / En cok tercih
  edilen / En ekonomik. Kartlar seyahat suresine gore kisa listeden (3 adet) geliyor.
- Test: `test_reports/iteration_135.json` — tum akislar dogrulandi (tek secim, kaldirma,
  adet, tumunu gor/kapat, %10 paket indirimi, 4 adim regresyon, konsol hatasi yok).

### "Degistir" ve "Tarihleri duzenle" artik satir ici (kullanici istegi)
- 2. adimdaki iki baglanti `setStep(0)` yapmiyor; ayni sayfada acilip kapaniyor
  (`visa-step-visa-editor` = vize turu dropdown + "Vizeleri karsilastir",
  `visa-step-dates-editor` = gidis/donus tarih alanlari + "tarihim belli degil").
- Bunun icin `visaPickerFields` ve `travelDatesEditor` JSX degiskenlerine cikarildi;
  karsilastirma diyalogu artik picker ile birlikte tasiniyor (her iki adimda calisir).

### Onemli bilgi notu sadelestirildi (kullanici istegi)
- `ImportantNotice` compact surumu 2 satir x 2 kolon oldu, her madde icin kisa `brief`
  metni yazildi; uzun `detail` metinleri yalnizca tam surumde (Belgeler sayfasi) kaldi.
- Sigorta/eSIM kartlari da sadelestirildi: ozet paragraf kaldirildi (maddeler yeterli),
  padding ve satir araliklari kisildi; sigorta bolumu ~530px'e indi.

### Iletisim sayfasi
- Sol form karti ile sag kolon (WhatsApp + telefon + e-posta + calisma saatleri) alt
  hizada bitiyor (sag kolon flex-col, satirlar flex-1; textarea 6 -> 5 satir).
- "Ofislerimiz" bolumunde Istanbul'un sagina **Dubai (BAE)** karti geldi: DB'deki
  `company_info.dubai_address` / `dubai_phone` bos oldugu icin gorunmuyordu; content.py
  varsayilanlari ile dolduruldu (Level 27, Unit 2705, Marina Plaza, Dubai Marina /
  +971 50 867 26 30). Farkliysa Admin -> Sirket ekranindan degistirilebilir.

### SEO on-render "ciplak metin" parlamasi (kullanici raporu)
- Kok neden: kod duzeltmesi (09ebf86) canliya alinmadigi icin **yayindaki build eski**.
  `curl https://dubaivizehatti.com/basvuru` -> `boot-splash` / `boot-style` YOK.
- Guncel kod ile alinan build'de dogrulandi: JS paketi bloklanip ilk boyama alindiginda
  ciplak metin degil marka yuklenme ekrani gorunuyor. Ek saglamlastirma: `#seo-prerender`
  div'ine inline `position:absolute;left:-10000px` stili eklendi (style etiketi kaybolsa
  bile metin ekranda gorunmez). **Yapilmasi gereken: yeniden deploy.**
- pytest: 601 passed / 5 skipped; 1 flaky (`test_iteration_82` OTP e2e yarisi) tek
  basina calistirildiginda geciyor.

### 2026-06-17 (devam) · Ana sayfa sigorta gorseli + footer duzeni
- **Turk pasaportu + Dubai binis karti gorseli** (kullanici istegi): "SADECE SIGORTA"
  seridindeki ABD pasaportlu Unsplash fotografi kaldirildi. Gemini 3.1 flash image ile
  uretilip yazi hatalari duzeltilen (TURKIYE CUMHURIYETI / REPUBLIC OF TURKIYE, binis
  karti: ISTANBUL (IST) -> DUBAI (DXB), TK762, GATE A12, SEAT 14C) foto
  `frontend/public/images/turk-pasaport-dubai-binis-karti.jpg` olarak eklendi
  (900x900, 84 KB). `lib/site.js -> IMAGES.travelInsurance` yerel dosyayi gosteriyor.
- **Footer 4. kolon**: yasal/kurumsal baglantilar (Hakkimizda, Guvenlik ve Veri Koruma,
  KVKK, Gizlilik Politikasi, Iade ve Iptal, Sartlar ve Hizmet Sozlesmesi, Ticari
  Elektronik Ileti Onami) "Hizli Baglantilar" listesinden cikarilip **"Kurumsal ve Yasal"**
  basligi altinda Iletisim kolonunun soluna alindi. Grid `md:grid-cols-2 lg:grid-cols-5`.

### 2026-06-17 (devam) · Backend kod kalitesi raporu degerlendirmesi
Rapor iddialari ruff 0.16.5 + pyflakes 3.4 ile dogrulandi:
- "21 undefined variable" -> **DOGRULANMADI**: `ruff --select F821` ve `pyflakes` sifir
  bulgu veriyor. Rapordaki 21 sayisi muhtemelen E741/B904/E731 turu 21 stil bulgusu.
- "234 adet `is` ile sabit karsilastirma" -> **DOGRULANMADI**: `ruff --select F632`
  temiz. Kod tabanindaki tum kullanimlar `is None` / `is True` / `is False` (dogru idiom).
- "Karmasiklik 18/13/11 fonksiyonlar" -> **DOGRULANMADI**: `ruff --select C901`
  (max-complexity 10) tum backend'de temiz; `admin_subject`, `save_draft`,
  `_application_items`, `_application_summary_rows` esigin altinda. Refactor yapilmadi
  (calisan uretim kodunda gereksiz risk).
- "Import sayisi 38/32/30" -> mimari degisiklik onerisi; FastAPI route modulleri icin
  normal. Canli uygulamada 600+ testi riske atacak bolme islemi yapilmadi.

Gercek olan ve duzeltilen bulgular:
- B904 (4): `models.py`, `routes_account.py`, `routes_admin.py`, `routes_payments.py` ->
  `raise ... from exc` (traceback zinciri korunuyor).
- E741 (12): belirsiz `l` degisken adlari -> `row` / `ln` / `line` / `raw`
  (`emailer.py`, `wa_docs.py` + 6 test dosyasi).
- E731: `test_iteration_84.py` lambda atamasi -> `def traveler_tpl(i)`.
- UP012 `admin_auth.py`: gereksiz `encode("utf-8")`; UP031 `test_submit_finder.py`:
  `%` formati -> string birlestirme; W291/E401 kucuk temizlikler.
- `routes_store.py` "kullanilmayan import" bulgusu yanlis: `# noqa: F401` ile bilincli
  re-export (testler bu modulden import ediyor).
Dogrulama: `pytest` 602 passed / 5 skipped; `order_delivered_html` link render kontrolu ok.

### 2026-06-17 (devam) · Anlatim videosunda duraklat ikonu
- `VisaExplainer.jsx`: anlatim basladiktan sonra cizim alaninin tamami tiklanabilir bir
  oynat/duraklat katmani (`explainer-video-toggle-button`). Oynarken ortada %50 opaklikta
  duraklat ikonu (hover/focus'ta tam gorunur), duraklatildiginda tam opak oynat ikonu +
  hafif scrim + "Devam etmek icin dokunun" etiketi. Alttaki kucuk kontrol ile ayni
  `paused` state'i kullanildigi icin ikisi senkron.
- Dogrulama (Playwright): oynat -> katman var, aria-label "Anlatimi duraklat"; tik ->
  `audio.paused === true`, aria-label "Anlatimi devam ettir"; tekrar tik -> ses devam.

### 2026-06-17 (devam) · Anlatim ilerleme cizgisi + sigorta rozeti keskinlestirildi
- **Ilerleme cizgisi**: `VisaExplainer.jsx` cizim alaninin **altinda** ince cizgi + sag
  tarafta "m:ss kaldi" (`explainer-progress`, `explainer-progress-bar`,
  `explainer-remaining-time`). Ses acikken mp3 saatinden (`onLoadedMetadata` +
  `onTimeUpdate`), sessiz modda sahne surelerinden hesaplaniyor; satir sabit 28px
  yukseklikte oldugu icin layout kaymasi yok. Ilk denemede cizgi gorselin ustune
  bindigi icin katman disina, cizimin altina tasindi.
- **Metin guncellemesi (kullanici)**: 2. sahne altyazisi "...yapmaniz yeterli. ...
  gerek yok." olarak kisaltildi (onceki: "yeterlidir / yoktur").
- **"30.000 € TEMINAT" rozeti**: `public/explainer/extras.png` icindeki rozet, onceki
  ayna+metin duzenlemesinden kalan **yari saydam dikdortgen yamayi** ve yumusak
  kenarlari tasiyordu. PIL ile 4x supersampling kullanilarak ayni konumda
  (merkez 125,230 · r=119) yeniden cizildi: keskin daire, altin ic halka (r 99.5-106.5),
  halkaya sigacak sekilde otomatik punto secimi (39pt) ve daire disinda kalan
  yama kalintilarinin temizlenmesi. Yedek: `memory/brand_backup/extras.beforesealfix.png`,
  script: `memory/brand_backup/fix_seal_extras.py`.
- Dogrulama: masaustu + mobil (414px) Playwright ekran goruntuleri; kalan sure
  1:03 -> 0:24 dogru sayiyor, cizgi cizimin altinda, rozet keskin.

### 2026-06-17 (devam) · Seslendirme ile altyazi birebir eslestirildi
- Kullanici bildirimi: "yazilar ve konusmalar ayni degil". Kok neden: altyazi metinleri
  (`VisaExplainer.jsx` SCENES.subtitle) sonradan guncellenmis, ses ise eski
  `scripts/generate_narration_eleven.py` metniyle uretilmisti (upload sahnesinde
  "yeterlidir/yoktur", extras sahnesinde eksik "ve").
- Script metinleri altyazilarla birebir ayni hale getirildi ve dogrulama icin
  JSX <-> script karsilastirmasi yapildi (7/7 sahne AYNI; sadece TTS icin "36" ->
  "otuz alti" yaziliyor, okunusu ayni).
- ElevenLabs (eleven_v3, Fusun Tuncer) ile tek parca ses yeniden uretildi:
  `full.mp3` 68.1 sn (onceki 65.7) + `full.json` sahne pencereleri guncellendi.
  Yedek: /tmp/full.prev.mp3 (kalici saklama gerekirse memory/brand_backup'a alinabilir).
- Bagimsiz dogrulama: OpenAI Whisper (Emergent LLM key) ile yeni ses transkribe edildi;
  cikan metin altyazilarla birebir ayni (STT'nin "TURSAP / Beyaz Fon'da" gibi kucuk
  yazim yorumlari haric).
- Tarayici kontrolu: audio.duration 68.1, sahne atlamasi (upload -> 22.8 sn) ve
  "0:45 kaldi" sayaci dogru.

### 2026-06-17 (devam) · Dubai Col Safarisi icerik guncellemesi + ozet kart genisligi
- **Isimlendirme**: "Col safarisi ve Dubai aktiviteleri" -> **"Dubai Col Safarisi"**
  (Tours.jsx PageHeader + setMeta, seo-pages.js h1/title/description, Navbar ve Footer
  linki "Col Safarisi & Turlar" -> "Dubai Col Safarisi"). Urun adlari da
  "Dubai Col Safarisi · Aksam Turu" / "· VIP Aksam Turu" oldu.
- **"Turkce konusan rehber" ibaresi kaldirildi**: store_catalog.py features,
  HomeTourStrip highlight, Tours.jsx aciklama/meta, seo-pages.js (3 yer).
- **Otelden alinis saati tek saat**: `time_slots` 5 secenek yerine `["15:00"]`.
  Backend `tour_schedule` saati time_slots'a gore dogruladigi icin testler de
  guncellendi (test_iteration_79: 1 slot + "15:00", test_iteration_95: slot listesi
  ve scheduled_time, test_iteration_102: 14:00 -> 15:00).
- **Yeni bilgiler**: "Ortalama 7–8 saat", "7 kisilik 4×4 Land Cruiser" feature ve
  strip highlight olarak eklendi.
- **Tur programi ozeti**: urunlere `itinerary` alani eklendi (8 adim; ATV standart
  turda +40 USD opsiyonel, VIP'te dahil). Tours.jsx kartlarinda "Tur programi (ozet)"
  aciir/kapanir liste (`tour-plan-toggle-<id>`, `tour-plan-<id>`); seo-pages.js
  "Tur programinda neler var?" listesi de bu ozetle guncellendi.
- DB: `store_products` icindeki iki tur dokumani yeni ad/summary/features/itinerary/
  time_slots ile guncellendi (API dogrulandi).
- **Basvuru ozeti karti genisletildi**: Apply.jsx grid `1.4fr_0.6fr` -> `1.25fr_0.75fr`
  (1520px'te 330px -> 402px).
- Dogrulama: pytest 602 passed / 5 skipped; /dubai-turlari ekran goruntusu (H1, tek
  15:00 slotu, 8 adimli program), /basvuru ozet kart genisligi.
- NOT (kullaniciya soruldu): 15:00 alinis + 21:00-22:00 donus ~6-7 saat ediyor ama
  metinde "Ortalama 7–8 saat" yaziyor; kullanici onayina birakildi.

### 2026-06-17 (devam) · Tur suresi tutarliligi + col safarisi foto galerisi
- **Sure duzeltildi**: 15:00 alinis + 21:00-22:00 donus ile uyumlu olacak sekilde tum
  metinler "Ortalama 6–7 saat · otelden alinis 15:00, donus 21:00 – 22:00" oldu
  (store_catalog features x2, HomeTourStrip highlight, Tours.jsx PageHeader + setMeta,
  seo-pages.js description, DB dokumanlari).
- **Foto galerisi**: urunlere `gallery` alani eklendi (4 gercek col safarisi fotografi:
  4×4 kumul safarisi, ATV, deve turu, Bedevi kampi). Tours.jsx TourCard'da ana gorsel
  + 5 kucuk kare (`tour-gallery-<id>`, `tour-gallery-thumb-<id>-<i>`); tiklaninca ana
  gorsel degisiyor, alt kisimda Turkce aciklama gorunuyor (animate-in fade-in).
  Gorseller image_selector_tool ile Unsplash'ten secildi, hepsi HTTP 200.
- Dogrulama: pytest 25 tur testi gecti; /dubai-turlari 1440px ekran goruntusu (galeri
  gecisi, tek 15:00 slotu, guncel sure metni), kirik gorsel yok.

### 2026-06-17 (devam) · Seyahatten kisa sigorta/eSIM paketleri artik teklif edilmiyor
- Kullanici bildirimi: 11 gunluk seyahatte 7 gunluk police/eSIM gosteriliyordu.
- Kok neden: `insuranceProducts` vize suresine gore UST sinir uyguluyordu (30 gunluk
  vizede 7/15/30) ve liste 3 elemana dustugu icin `shortlistFor` erken donup
  seyahat suresini kapsamayan paketi de listeliyordu.
- Cozum (`Apply.jsx`): `coveringOnly()` yardimcisi eklendi -> `validity_days >= coverDays`
  (coverDays = seyahat suresi, yoksa vize suresi). `eligibleInsurance` / `eligibleEsim`
  hem kisa listede hem "Tumunu gor" listesinde kullaniliyor; kapsayan paket yoksa
  guvenlik icin tum liste gosterilir.
- Metinler dinamik: "iki police / uc internet paketi sectik; seyahatinizden kisa sureli
  paketleri listelemiyoruz" (`countWord` yardimcisi).
- `ExtraOptions` grid'i secenek sayisina gore 1/2/3 kolon oluyor (2 seceneginde bosluk
  kalmiyor).
- Dogrulama: 11 gunluk seyahat + 30 gunluk vize -> sigorta 15/30 gun (7 gun yok),
  eSIM 15 gun / 10 GB-30 gun / Sinirsiz-30 gun; hepsinde "11 gunluk seyahatinizin
  tamamini kapsar" notu. Konsol hatasi yok.

### 2026-06-17 (devam) · Uzun seyahatlerde 60 gunluk police secilebilir
- `insuranceProducts` (Apply.jsx): vize suresi ust siniri korunuyor, ancak vize
  suresinden UZUN seyahatlerde seyahati kapsayan uzun policeler (60 gun) listeye
  ekleniyor. Boylece 35 gunluk seyahatte 30 gunluk vizeyle bile 60 gunluk police
  secilebiliyor; kisa seyahatlerde (11 gun) 60 gunluk police yine listelenmiyor.
- `coveringOnly` yedegi iyilestirildi: hicbir paket seyahati kapsamiyorsa (orn. eSIM'de
  en uzun paket 30 gun) tum liste degil yalnizca **en uzun sureli paketler** gosteriliyor.
- Dogrulama (Playwright, 3 senaryo): 60 gun vize + 35 gun -> sigorta [ins_60d],
  eSIM [10GB/30, Sinirsiz/30]; 30 gun vize + 35 gun -> sigorta [ins_60d] (eskiden
  7/15/30 cikiyordu); 30 gun vize + 11 gun -> sigorta [15, 30], eSIM 3 paket (regresyon
  temiz). Konsol hatasi yok.

### 2026-06-17 (devam) · Guvenlik denetimi (security audit) ve duzeltmeler
Denetim sonucu: **CONDITIONAL PASS** - kritik/yuksek bulgu yok. Dogrulananlar: admin
API'leri tek tip auth korumali, OTP kodlari hash'li + deneme limitli, basvuru/siparis/
teklif/taslak/dosya eriimleri sahiplik bazli, pasaport taramalari nesne depolamada
public DEGIL, Stripe ve Meta webhook imzalari dogrulanıyor, frontend bundle'da sizmis
anahtar yok, dangerouslySetInnerHTML kullanimi yok, prerender cikisi HTML-escape'li.

Duzeltilen bulgular:
- **SEC-001 (MEDIUM)** `rate_limit.py:client_ip` X-Forwarded-For zincirinin EN SOLUNU
  aliyordu; istemci basa uydurma IP ekleyerek her istekte yeni kimlik uretip ucretli
  AI uclarindaki (passport OCR, photo check) ve upload'daki limitleri asabiliyordu.
  -> Artik zincirin SAGINDAN `TRUSTED_PROXY_HOPS` (varsayilan 3: istemci, Cloudflare,
  platform ingress) kadar hop atlanarak gercek istemci bulunuyor. Ortam olcumu:
  normalde `client, 104.23.x, 136.110.x`; sahte deger eklenince `fake, client, ...`.
  Canli dogrulama: 45 istek + her birinde farkli sahte XFF -> ilk 40 gecti, 5 istek 429.
- **SEC-001 ek katman**: `usage_quota.py` eklendi - `usage_counters` koleksiyonunda
  atomik gunluk sayac (replikalardan bagimsiz). `passport_ocr` 400/gun, `photo_check`
  800/gun (env: PASSPORT_OCR_DAILY_LIMIT / PHOTO_CHECK_DAILY_LIMIT). Sayac yalnizca
  gercek AI cagrisindan hemen once artiyor; 404/gecersiz istekler kotayi yemiyor.
- **SEC-002 (LOW)** CORS regex'i `*.emergentagent.com` / `*.emergent.host` gibi platform
  genelindeki tum kardes subdomainlere credentialed erisim veriyordu -> regex yalnizca
  kendi alan adlarimiz (dubaivizehatti.com, dubaivizeonline.com) + localhost:3000 olacak
  sekilde daraltildi; preview adresi PUBLIC_SITE_URL uzerinden acikca izinli.
  Dogrulama: www.dubaivizehatti.com -> ACAO donuyor, evil-app.preview.emergentagent.com
  -> ACAO yok.
- Yeni test dosyasi: `tests/test_security_audit_20260617.py` (9 test: XFF sahtecilik
  senaryolari, gunluk kota, CORS wildcard regresyonu). pytest: 611 passed / 5 skipped.

Uygulanmayan (bilincli) oneriler: siparis/makbuz URL'lerindeki e-posta parametresinin
imzali token'a cevrilmesi, e-postadaki imzali dosya linklerinin 180 gunden kisaltilmasi
(musteri deneyimini etkiler), Redis tabanli dagitik limiter, TAMAMLIYO kart bilgilerinin
harici secret manager'a tasinmasi (platformda .env tek secret store).

## 2026-06-18 · "Toplam neden 5.550?" — gizli sigorta indirimi artik dokumde gorunuyor
Kullanici sikayeti: Vize 5.190 + Sigorta 450 = 5.640 beklenirken toplam 5.550 cikiyordu.
Kok neden: `content.py:WITH_VISA_INSURANCE_DISCOUNT` (vize ile birlikte alinan policeye
indirim) toplamdan dusuluyor ama fiyat dokumunde HIC gosterilmiyordu (yalniz Offer.jsx
sayfasinda satiri vardi). Fark = police bedelinin %20'si (90 TL).

Yapilanlar:
- Indirim orani kullanici talebiyle **%20 -> %10** dusuruldu (`content.py`, badge/note
  metinleri + yeni `card_badge` anahtari).
- `/api/products` yanitina `visa_insurance` blogu eklendi (routes_store.py) - frontend
  orani/rozet metnini sabit yazmak yerine backend'den okuyor.
- Indirim satiri artik her yerde: Apply sidebar ozeti (`summary-insurance-discount`),
  Adim 4 fiyat dokumu, Track sayfasi (`tracking-insurance-discount`), Admin basvuru
  detayi, basvuru formu PDF (`application_pdf._pricing_rows`), odeme makbuzu PDF
  (`payment_receipt_pdf._application_summary_rows`), e-posta ozeti (`emailer._pricing_block`).
- Sigorta secim kartlarinda rozet + ustu cizili fiyat: `ExtraOptions.jsx` OptionCard'a
  `discount` prop'u eklendi (560 TL ustu cizili -> 504 TL, "Vize ile birlikte %10 indirim").
- Ek bulgu duzeltildi: Track sayfasindaki fiyat dokumu magaza (sigorta/eSIM) satirlarini
  hic listelemiyordu; store_items + paket indirimi satirlari eklendi.

Dogrulama: `/api/pricing/quote` -> 5190 + 560 - 56 = 5694 (%10). Apply Adim 2 ekran
goruntusu: kart rozeti + 560/504 fiyat, ozet satiri "- 56 TL", toplam 5.694 TL. Track
sayfasi gecici veri ile dogrulandi (sonra geri alindi). PDF/e-posta satirlari python ile
dogrulandi. pytest: 611 passed / 5 skipped.

## 2026-06-18 (2) · Tasarruf vurgusu (savings note)
Apply.jsx'e `SavingsNote` bileseni eklendi: aile + sigorta + seyahat paketi indirimlerinin
toplamini "Bu basvuruda toplam X ₺ tasarruf ettiniz" seklinde yesil satirda gosteriyor.
Konumlar: sidebar Basvuru ozeti (Toplam'in altinda, `summary-total-savings`) ve Adim 4
fiyat dokumu (`breakdown-total-savings`). Indirim yoksa hic gorunmuyor.
Dogrulama: 1 yolcu + 15 gun police -> "Bu basvuruda toplam 56 ₺ tasarruf ettiniz",
toplam 5.694 ₺ (ekran goruntusu ile teyit).

## 2026-06-18 (3) · "Diger Evraklar" yukleme alani kaldirildi
Kullanici istegi: Evraklar adimindaki opsiyonel "Diger Evraklar" (davet mektubu/ogrenci
belgesi) FileDropzone'u kaldirildi. Ucak bileti ve otel rezervasyonu alanlari duruyor.
Backend payload'inda `other_file_ids` alani korundu (artik her zaman bos gonderiliyor),
eski taslak/basvuru kayitlari bozulmuyor.
Dogrulama: Adim 3 ekran goruntusu - "Diger Evraklar" DOM'da yok, ticket/hotel alanlari calisiyor.

## 2026-06-18 (4) · Stepper tam genislik + tiklanabilir adimlar
Apply.jsx STEPPER: adim ogeleri `div` -> `button` oldu, `flex-1` ile satirin tamamini
"Toplam" blogunun soluna kadar dolduruyor (baglanti cizgisi `w-8` -> `flex-1`).
Navigasyon kurali (`goToStep`): geriye serbest; ileri yonde `validateStep()` calisir ve
en fazla tek adim ilerler (Adim 1'den Adim 4'e atlanamaz). Basvuru gonderildikten sonra
(`created`) adimlar kilitli. Hover/focus-visible durumlari + aria-current="step" eklendi.
Dogrulama (Playwright): Adim3 -> Adim1 (geri) OK, Adim1 -> Adim2 (ileri, dogrulama gecti)
OK, Adim2'den Adim4'e tiklama -> yalnizca Adim3'e gitti (atlama engellendi).

## 2026-06-18 (5) · Vize turu + seyahat tarihleri 1. adimdan 2. adima tasindi
Kullanici istegi: "1. adimda kisisel bilgiler ve pasaport olsa yeterli".
- Adim 1'den kaldirilan bloklar: `primary-visa-block` (Basvurdugunuz vize turu) ve
  `travel-dates-block` (Seyahat tarihleriniz). Adim 1 artik: basvuru tipi + iletisim +
  yolcu/pasaport bilgileri.
- Dogrulama tasindi: gidis/donus tarihi, tarih-belirsiz penceresi ve pasaport 6 ay
  gecerlilik kontrolleri `step === 0` -> `step === 1` blogunda.
- Adim 2 (Vize): vize secilmemisse (`visaMissing`) vize secici kendiliginden acik gelir,
  ozet seridi ve "Degistir" butonu gizlenir, baslik "Vizenizi secin" olur; tarih yoksa
  (`datesMissing`) tarih duzenleyici acik gelir, "Tarihleri duzenle" seridi gizlenir.
Dogrulama (Playwright): Adim1'de iki blok da yok; ileri -> Adim2 basligi "Vizenizi secin",
vize secici ve tarih duzenleyici acik; vize/tarih girilmeden ileri tiklamasi adimda tuttu;
vize + tarih girilince Adim3'e gecti.

## 2026-06-18 (6) · Basvuru formu PDF: sorulmayan alanlar kaldirildi
Formda hic sorulmayan alanlar PDF dokumunden cikarildi (`application_pdf.py`):
- Iletisim blogundan "Sehir" (`contact.address_city` hicbir zaman doldurulmuyor, "-" cikiyordu)
- Yolcu blogundan "Medeni hal" ve "Meslek" (formda alan yok; backend varsayilan olarak
  "single"/"Employee" gonderiyor, bu yuzden yanlis bilgi gorunuyordu)
Uyruk ve dogum yeri korundu. Dogrulama: gercek basvuru dokumu ile PDF uretildi, metin
taramasinda Medeni/Meslek/Sehir yok; pytest test_iteration_112_application_form 9 passed.

## 2026-06-18 (7) · WhatsApp bilgilendirme anahtari telefon alaninin yanina tasindi
Iletisim blogunun altindaki genis "WhatsApp ile bilgilendirilmek istiyorum" kutusu
kaldirildi; anahtar artik "Cep Telefonu (WhatsApp)" alaninin hemen altinda kompakt satir
olarak duruyor (`whatsapp-optin-row`, switch testid'i `input-whatsapp-optin` korundu).
Metin kisaltildi: "WhatsApp ile bilgilendir. Sonuc cikinca mesaj gonderelim."
Dogrulama: Playwright ile anahtar unchecked -> checked, ekran goruntusu ile konum teyidi.
