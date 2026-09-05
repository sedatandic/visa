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
