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
- **Marka logosu güncellendi**: yüklenen logo `public/brand/emblem-512.png` +
  `logo-lockup.png` olarak işlendi (arka plan şeffaflaştırıldı), `BrandMark` bu amblemi kullanıyor
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
