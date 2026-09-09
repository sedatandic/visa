# Güvenlik denetimi — 2026-06-15 (deployed app)

## Sonuç: CONDITIONAL PASS
Önceki SEC-001..SEC-004 bulgularının hepsi doğrulandı, düzeltmeler yerinde:
- Müşteri girişi e-posta+soyad yerine OTP (hash'li, hız sınırlı) — `routes_account.py:154-229`
- Zami bookmarklet çıktısı `dvoEsc` ile kaçışlı — `routes_zami.py:1019-1058`
- Dosya bağlantıları HMAC imzalı + süreli, handoff jetonu 10 kullanım — `file_access.py`, `zami.py`
- Stripe (SDK ile) ve WhatsApp (fail-closed) webhook imza doğrulaması çalışıyor
- PDF/e-posta çıktılarında kullanıcı girdisi kaçışlı, ödeme tutarları sunucu tarafında

## Bu turda uygulanan düzeltmeler (2026-06-15)
- `GET /api/applications/track`: IP başına 60 istek / 5 dk (takip kodu tahmini yavaşlatılır)
- `POST /api/uploads` (kimlik doğrulamasız): IP başına 150 istek / 60 sn
  (bir aile başvurusu ~14 dosya; tam test paketi ~100 dosya/90 sn)
- `POST /api/admin/request-code`: IP başına 30 talep / saat (sahte kayıt şişmesi)
- `re.escape`: `routes_account._applications_for_email`, `account_orders`,
  `routes_whatsapp.search_applications` (q ayrıca 80 karaktere kırpılır) — ReDoS/aşırı eşleşme
- pytest: 505 passed / 5 skipped (hız sınırları test paketini bozmuyor)

## Açık kalan / kullanıcı kararı gereken
### SEC-001 (MEDIUM, P2) — kart bilgisi ve ana imza anahtarı .env içinde
- `backend/.env`: TAMAMLIYO_CARD_NUMBER / EXPIRY / **CVV** / NAME / SURNAME
  (`tamamliyo.py:38-43`, `PAYMENT_TYPE_CARD="2"` kurumsal kartla çekim).
  PCI-DSS **CVV'nin saklanmasını yasaklar**. Kod tarafı iyi: kart loglarda maskeli,
  DB'ye yazılmıyor — sorun yalnızca .env'de duruyor olması.
- `JWT_SECRET` tek anahtar: admin JWT + admin OTP hash + müşteri JWT + imzalı dosya
  bağlantıları (`admin_auth.py:16,30,52`, `routes_account.py:41`, `file_access.py:24-33`).
  .env artık deploy için repoda tutulmak zorunda (platform gereği).
- Seçenekler:
  1. Tamamliyo'da **cari bakiye** (odemeTipi=3) moduna geçmek → kart bilgisi hiç saklanmaz
     (bakiye yüklemesi gerekir; kod tarafı daha önce hazırlanmıştı).
  2. Kart modunda kalıp CVV'yi kaldırmak (sağlayıcı CVV'siz çekime izin veriyorsa).
  3. Mevcut durumu kabul etmek + anahtarları (Stripe, Resend, Meta, Tamamliyo, ElevenLabs,
     JWT_SECRET) rotasyona almak.

### P3 (kabul edilebilir, izlenmeli)
- CORS: platform alan adlarının alt alanlarına izin veriyor + allow_credentials
  (`server.py:409-421`). Etkisi sınırlı: kimlik doğrulama Bearer token ile, çerez yok.
  Canlı alan adı sabitlendiğinde tam host listesine daraltılabilir.
- Hız sınırı sayaçları süreç içi (tek replika). Birden fazla replikaya çıkılırsa Redis gerekir.
