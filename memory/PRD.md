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
- **P0 Deployment**: Emergent tarafında manuel güven & güvenlik incelemesi nedeniyle bloke.
  Kodda blocker yok (health check PASS). Kullanıcı support@emergent.sh ile iletişimde.
- **P0 Zami OTP ilk giriş**: Kullanıcı Admin → Zami → Robot Oturumu (B) → "Oturum başlat"
  ile OTP kodunu girip cihaz güvenini kaydetmeli (30 gün OTP'siz çalışır).
- **P1** Şirket bilgileri (telefon, WhatsApp, adres, TURSAB) admin panelden güncellenmeli
- **P1** Stripe canlı anahtarları (domain açıldığında)
- **P2** Gerçek müşteri yorumları admin panelden eklenmeli
- **P2** `onyuz-rehberi.pdf` kapsamı netleşmedi (kullanıcı yanıtı bekleniyor)
