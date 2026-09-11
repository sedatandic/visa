# Güvenlik Denetimi · 2026-06-18 (security_audit_agent)

**Sonuç: PASS — kritik/yüksek/orta seviye bulgu YOK.** Güven düzeyi: YÜKSEK
(kod/konfig okuma bazlı; canlı sömürü denemesi politika gereği yapılmadı).

Kapsam: admin + müşteri OTP kimlik doğrulama ve JWT guard'ları, BOLA/IDOR
(applications, orders, account, track, offers, drafts, files), dosya yükleme doğrulaması
(uzantı + boyut + magic byte) ve imzalı `/api/files` erişimi, NoSQL enjeksiyonu
(pydantic + `re.escape`, operator injection yok), Stripe webhook (SDK imza + atomik
idempotency), WhatsApp webhook (fail-closed HMAC + verify_token), dış çağrılar
(fx.py sabit host, Meta media yalnız graph URL), PDF/HTML kaçışı, secret maskeleme
(`wa_cloud`/`whatsapp` ayarlarında token maskeli), frontend (dangerouslySetInnerHTML yok,
REACT_APP içinde secret yok, sourcemap kapalı).

## Önceki bulguların regresyon kontrolü — HEPSİ KAPALI
- SEC-001 müşteri e-posta+soyad girişi → yalnız OTP: KAPALI
- SEC-002 Zami bookmarklet stored XSS (`dvoEsc` kaçışı): KAPALI
- SEC-003 imzalı/süreli dosya jetonu, handoff `used_count`/TTL (`zami.py:787-800`),
  JWT_SECRET fallback'i yok: KAPALI
- SEC-004 hız sınırları + hash'li OTP: KAPALI
- CORS allowlist, güvenlik başlıkları/HSTS, `/docs` kapalı (ENABLE_API_DOCS hariç): KAPALI
- Tüm `/api/admin/*` route'ları `require_admin` bağımlılığına sahip: DOĞRULANDI

## Kalan P3 sıkılaştırma maddeleri (aciliyet yok)
1. **Maliyet/marj sızıntısı** — `store_catalog.py:224-240` public `GET /api/products`
   yanıtında `cost_try`, `routes_store.py:386` sipariş satırlarında `unit_cost` dönüyor.
   Müşteri PII değil ama tedarik maliyeti/kâr marjı müşteriye/rakibe açık.
   Çözüm: müşteriye dönen serializer'lardan `cost_try` / `unit_cost` alanlarını temizle.
2. **Sipariş sorgusunda hız sınırı yok** — `routes_store.py:715-734` (referans kodu ~41 bit
   rastgele + e-posta). Tahmin pratikte imkânsız ama throttle yok.
   Çözüm: `/track` gibi `rate_limit.check` ekle veya imzalı link kullan.
3. **Uzun ömürlü imzalı belge linkleri** — `file_access.py:21` `TTL_EMAIL = 180 gün`.
   Sızan pasaport/vize PDF linki 180 gün geçerli. Çözüm: pasaport/vize/poliçe için TTL kısalt,
   tercihen hesap girişli indirme.
4. **CORS `allow_credentials=True` + subdomain regex** — `server.py:437-449`. Oturum
   localStorage Bearer jetonu olduğu için etki sınırlı; canlı domain netleşince tam host listesi.
5. **Tek `JWT_SECRET`** admin JWT + müşteri JWT + OTP hash + dosya HMAC için kullanılıyor
   (`admin_auth.py:16`, `routes_account.py:42`, `file_access.py:24`). Periyodik rotasyon öneriliyor.
6. **Base URL `Host`/`X-Forwarded-*`'tan** üretiliyor — `routes_zami.py:37-59`; yalnız
   `PUBLIC_BASE_URL` kullanılması tercih edilir.

## Bilinen sınır
Hız sınırı sayaçları süreç içi (tek replika); çoklu replikada Redis'e taşınmalı (ROADMAP P2).
