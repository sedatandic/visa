# Güvenlik denetimi · 16.06.2026 (canlı + önizleme)

Kapsam: canlı `https://dubaivizehatti.com` (+ önizleme), FastAPI backend + React frontend,
salt-okunur inceleme + düşük hacimli güvenli istekler.

## Sonuç: PASS — kritik/yüksek/orta seviye işlevsel açık bulunmadı

Dışarıdan başka bir müşterinin verisine erişme, hesap devralma, yönetici girişini atlatma,
fiyat oynatma veya ödeme/WhatsApp webhook'u taklit etme yolu bulunamadı. Önceki denetimin
(15.06.2026) tüm bulguları hâlâ kapalı.

## Son değişikliklerin doğrulanması
1. **Tamamliyo cari bakiye** — ONAYLANDI. `TAMAMLIYO_PAYMENT_TYPE=3`, `.env` içindeki tüm
   kart/CVV alanları boş; kart alanları yalnızca tip "2" iken gönderiliyor; `card_hint()`
   yalnızca son 4 haneyi maskeleyerek döner. Veritabanı, log ve API yanıtlarında kart/CVV yok.
2. **`PUT /api/admin/company` alan bazlı `$set` birleştirme** — GÜVENLİ. Anahtarlar
   `CompanyInfoIn` model alanlarıyla sınırlı; noktalı anahtar (dotted-key) enjeksiyonu yok;
   yalnızca yönetici yazabiliyor.
3. **`fix_placeholder_contact()`** — GÜVENLİ. Yalnızca bilinen sabit placeholder değerlerini
   koddaki sabitlerle değiştiriyor, kullanıcı girdisi kullanmıyor.
4. **PDF alt bilgi + QR bandı** — GÜVENLİ. `affiliation_note()` sabit metinlerden üretiliyor,
   kullanıcı verisi `_safe()` ile XML-escape ediliyor, QR adresi env + sunucu üretimi takip
   kodundan geliyor (markup enjeksiyonu / open redirect yok).
5. **Instagram takvimi (`/api/admin/instagram`)** — GÜVENLİ. Yalnızca yönetici yazıyor,
   metinler React tarafından otomatik kaçışlı basılıyor (HTML sink yok).

## Yeniden doğrulanan eski bulgular (hâlâ kapalı)
- Müşteri OTP girişi: kodlar yalnızca hash'li, hız sınırlı.
- Zami bookmarklet `dvoEsc` kaçışı.
- Dosya bağlantıları: imzalı + süreli, sınırlı kullanımlı devir jetonları.
- Stripe ve WhatsApp webhook imza doğrulamaları (imzasız istek → 403).
- Tutarların sunucu tarafında yeniden hesaplanması.
- Canlıda `/api/docs`, `/api/redoc`, `/api/openapi.json` kapalı; güvenlik başlıkları + HSTS var;
  `/api/admin/login` ve `/api/account/login-lastname` 404.

## Sertleştirme (P3) ve durum
| # | Bulgu | Durum |
|---|-------|-------|
| 1 | Yönetici başvuru aramasında `$regex` kaçışsızdı (ReDoS riski) — `routes_admin.py:257` | **DÜZELTİLDİ** (16.06.2026): `re.escape(...)[:80]` uygulandı (hesap/WhatsApp aramalarıyla aynı desen) |
| 2 | CORS, platform alt alan adlarına `allow_credentials=True` ile açık — `server.py:416` | Açık: oturum `localStorage` Bearer jetonu olduğu için etkisi yok; alan adı netleştiğinde daraltılacak |
| 3 | Hız sınırı sayaçları süreç içi (`rate_limit.py:16`) | Açık: tek replika ile sorun yok; ölçeklenirse paylaşımlı depo (Redis) gerekir |
| 4 | Tek `JWT_SECRET` tüm jeton/HMAC amaçları için | Açık (platform gereği): periyodik rotasyon önerilir |
| 5 | E-posta dosya bağlantıları 180 gün geçerli (`file_access.py:21`) | Açık: hassas belgeler için süre kısaltılabilir |

## Kapsam dışı / test edilemeyen
- Yönetici panelinin oturumlu UI akışları ve gerçek ödeme/poliçe kesimi (güvenlik gereği
  tetiklenmedi).
- Hız sınırları kod düzeyinde doğrulandı, yük testi yapılmadı.
