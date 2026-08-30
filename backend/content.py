"""Static Turkish content + seed data for the Dubai visa site.
Prices are sample values in TRY and can be edited later by the owner.
"""

VISA_TYPES = [
    {
        "id": "visa_14_single",
        "slug": "14-gun-tek-giris",
        "name": "14 Gün Tek Giriş",
        "short_name": "14 Gün",
        "duration_days": 14,
        "entry_type": "single",
        "entry_label": "Tek Giriş",
        "price": 1499.0,
        "currency": "TRY",
        "processing_days": "3-5 iş günü",
        "popular": False,
        "order": 1,
        "description": "Kısa süreli tatil ve iş seyahatleri için en ekonomik seçenek.",
        "features": [
            "14 gün kalış hakkı",
            "Tek giriş",
            "3-5 iş günü içinde sonuç",
            "Evrak kontrolü bize ait",
            "E-posta ile dijital vize teslimi",
        ],
    },
    {
        "id": "visa_30_single",
        "slug": "30-gun-tek-giris",
        "name": "30 Gün Tek Giriş",
        "short_name": "30 Gün",
        "duration_days": 30,
        "entry_type": "single",
        "entry_label": "Tek Giriş",
        "price": 1999.0,
        "currency": "TRY",
        "processing_days": "3-5 iş günü",
        "popular": True,
        "order": 2,
        "description": "En çok tercih edilen vize. Tatil planları için ideal süre.",
        "features": [
            "30 gün kalış hakkı",
            "Tek giriş",
            "3-5 iş günü içinde sonuç",
            "Ücretsiz ön evrak kontrolü",
            "WhatsApp destek hattı",
            "E-posta ile dijital vize teslimi",
        ],
    },
    {
        "id": "visa_30_multi",
        "slug": "30-gun-cok-giris",
        "name": "30 Gün Çok Giriş",
        "short_name": "30 Gün Çok Giriş",
        "duration_days": 30,
        "entry_type": "multiple",
        "entry_label": "Çok Giriş",
        "price": 3499.0,
        "currency": "TRY",
        "processing_days": "4-6 iş günü",
        "popular": False,
        "order": 3,
        "description": "Bölgede birden fazla ülke gezecek yolcular için esnek çözüm.",
        "features": [
            "30 gün kalış hakkı",
            "Sınırsız giriş-çıkış",
            "4-6 iş günü içinde sonuç",
            "Ücretsiz ön evrak kontrolü",
            "Öncelikli başvuru takibi",
        ],
    },
    {
        "id": "visa_60_single",
        "slug": "60-gun-tek-giris",
        "name": "60 Gün Tek Giriş",
        "short_name": "60 Gün",
        "duration_days": 60,
        "entry_type": "single",
        "entry_label": "Tek Giriş",
        "price": 3999.0,
        "currency": "TRY",
        "processing_days": "4-6 iş günü",
        "popular": False,
        "order": 4,
        "description": "Uzun süreli iş görüşmeleri ve aile ziyaretleri için.",
        "features": [
            "60 gün kalış hakkı",
            "Tek giriş",
            "4-6 iş günü içinde sonuç",
            "Ücretsiz ön evrak kontrolü",
            "Öncelikli başvuru takibi",
        ],
    },
    {
        "id": "visa_60_multi",
        "slug": "60-gun-cok-giris",
        "name": "60 Gün Çok Giriş",
        "short_name": "60 Gün Çok Giriş",
        "duration_days": 60,
        "entry_type": "multiple",
        "entry_label": "Çok Giriş",
        "price": 5499.0,
        "currency": "TRY",
        "processing_days": "5-7 iş günü",
        "popular": False,
        "order": 5,
        "description": "Sık seyahat eden iş insanları için en kapsamlı paket.",
        "features": [
            "60 gün kalış hakkı",
            "Sınırsız giriş-çıkış",
            "5-7 iş günü içinde sonuç",
            "Ücretsiz ön evrak kontrolü",
            "Özel danışman ataması",
            "Öncelikli başvuru takibi",
        ],
    },
]

REQUIRED_DOCUMENTS = [
    {
        "title": "Pasaport ana sayfası",
        "detail": "Fotoğrafınızın bulunduğu sayfanın renkli taraması veya net telefon fotoğrafı. Pasaportunuz giriş tarihinden itibaren en az 6 ay geçerli olmalıdır.",
        "required": True,
    },
    {
        "title": "Biyometrik fotoğraf (vesikalık)",
        "detail": "Son 6 ay içinde çekilmiş, beyaz fonda, gözlüksüz ve şapkasız, yüzün tamamı görünen renkli fotoğraf.",
        "required": True,
    },
    {
        "title": "Uçuş rezervasyonu",
        "detail": "Gidiş-dönüş uçuş bilgileriniz. Henüz bilet almadıysanız tahmini tarihleri forma yazmanız yeterlidir.",
        "required": False,
    },
    {
        "title": "Otel / konaklama bilgisi",
        "detail": "Otel rezervasyonu veya Dubai'de kalacağınız adres bilgisi.",
        "required": False,
    },
]

PHOTO_RULES = [
    "Beyaz veya açık gri fon kullanın.",
    "Yüzünüz kadrajın ortasında ve tamamen görünür olmalı.",
    "Gözlük, şapka, güneş gözlüğü kullanılmamalı.",
    "Fotoğraf son 6 ay içinde çekilmiş olmalı.",
    "Bulanık, filtreli veya selfie fotoğraflar kabul edilmez.",
]

PROCESS_STEPS = [
    {
        "step": 1,
        "title": "Vize tipini seçin",
        "detail": "Kalış sürenize ve seyahat planınıza uygun vize tipini seçin. Fiyatlar net ve tek seferliktir.",
    },
    {
        "step": 2,
        "title": "Formu doldurun",
        "detail": "Kimlik, pasaport ve seyahat bilgilerinizi 5 dakikada tamamlayın. Karmaşık evrak yok.",
    },
    {
        "step": 3,
        "title": "Belgeleri yükleyin ve ödeyin",
        "detail": "Pasaport ve vesikalık fotoğrafınızı yükleyin, güvenli altyapı üzerinden ödemenizi yapın.",
    },
    {
        "step": 4,
        "title": "Vizeniz e-postanıza gelsin",
        "detail": "Başvurunuzu biz takip ediyoruz. Onaylanan vizeniz dijital olarak e-postanıza iletilir.",
    },
]

WHY_US = [
    {
        "title": "Şeffaf fiyat",
        "detail": "Gizli masraf yok. Ödediğiniz tutar başvuru ve hizmet bedelinin tamamını kapsar.",
    },
    {
        "title": "Evrak kontrolü bizde",
        "detail": "Yüklediğiniz her belgeyi başvuru öncesi kontrol ediyoruz. Eksik varsa sizi arıyoruz.",
    },
    {
        "title": "Hızlı sonuç",
        "detail": "Başvuruların büyük bölümü 3-5 iş günü içinde sonuçlanır. Süreci panelden takip edin.",
    },
    {
        "title": "Gerçek insan desteği",
        "detail": "WhatsApp ve telefonla ulaşabileceğiniz Türkçe danışman ekibi.",
    },
]

FAQ = [
    {
        "q": "Dubai (BAE) vizesi için Türk vatandaşlarının vize alması gerekiyor mu?",
        "a": "Türkiye Cumhuriyeti pasaportu sahipleri turistik amaçlı kısa seyahatlerde belirli koşullarda vizesiz giriş yapabilmektedir; ancak kalış süresi, seyahat amacı ve pasaport tipine göre önceden vize alınması gerekebilir. Uygulamalar değişebildiği için başvurunuzu almadan önce sizin durumunuzu ücretsiz olarak kontrol ediyoruz.",
    },
    {
        "q": "Vize işlemi ne kadar sürüyor?",
        "a": "Belgeleriniz eksiksiz olduğunda başvurular genellikle 3-5 iş günü içinde sonuçlanır. Yoğun dönemlerde bu süre 7 iş gününe kadar uzayabilir.",
    },
    {
        "q": "Pasaportumu göndermem gerekiyor mu?",
        "a": "Hayır. Dubai vizesi elektronik (e-vize) olarak düzenlenir. Pasaportunuzun sadece fotoğraflı sayfasının taramasını yüklemeniz yeterlidir.",
    },
    {
        "q": "Pasaportumun ne kadar geçerli olması gerekiyor?",
        "a": "Pasaportunuzun, Birleşik Arap Emirlikleri'ne giriş tarihinden itibaren en az 6 ay geçerli olması gerekir.",
    },
    {
        "q": "Ödeme nasıl yapılıyor, güvenli mi?",
        "a": "Ödemeler uluslararası ödeme altyapısı üzerinden 3D Secure destekli olarak alınır. Kart bilgileriniz bizim sunucularımıza hiçbir şekilde kaydedilmez.",
    },
    {
        "q": "Vizem onaylanmazsa ne olur?",
        "a": "Konsolosluk harcı dışındaki hizmet bedelimizi iade ediyoruz. Ret gerekçesini sizinle paylaşıp yeniden başvuru için yol haritası sunuyoruz.",
    },
    {
        "q": "18 yaş altı çocuklar için başvuru yapılabilir mi?",
        "a": "Evet. Çocuklar için ayrı başvuru oluşturulması ve ebeveyn bilgilerinin belirtilmesi gerekir. Detay için bizimle iletişime geçin.",
    },
    {
        "q": "Başvurumu nasıl takip ederim?",
        "a": "Başvurunuz tamamlandığında size bir takip kodu veriyoruz. 'Başvuru Takip' sayfasından takip kodunuz ve soyadınızla durumu anında görebilirsiniz.",
    },
]

TESTIMONIALS = [
    {
        "name": "Elif K.",
        "city": "İstanbul",
        "text": "Formu 5 dakikada doldurdum, 4 gün sonra vizem e-postama geldi. Eksik belgemi telefonla arayıp söylediler, çok ilgililer.",
        "rating": 5,
    },
    {
        "name": "Mert A.",
        "city": "İzmir",
        "text": "İş seyahati için çok giriş vizesi aldım. Fiyat baştan netti, sürpriz masraf çıkmadı. Takip kodu ile süreci görmek çok rahat.",
        "rating": 5,
    },
    {
        "name": "Zeynep D.",
        "city": "Ankara",
        "text": "Vesikalık fotoğrafım uygun değildi, hemen bilgilendirip nasıl olması gerektiğini anlattılar. Süreç sorunsuz ilerledi.",
        "rating": 5,
    },
    {
        "name": "Burak Ş.",
        "city": "Bursa",
        "text": "Ailemle 4 kişi başvurduk, hepsi aynı gün onaylandı. Destek ekibi WhatsApp'tan hızlı dönüş yapıyor.",
        "rating": 5,
    },
]

STATUS_LABELS = {
    "submitted": "Başvuru Alındı",
    "payment_pending": "Ödeme Bekleniyor",
    "documents_pending": "Belge Bekleniyor",
    "reviewing": "İnceleniyor",
    "approved": "Onaylandı",
    "rejected": "Reddedildi",
    "cancelled": "İptal Edildi",
}

COMPANY = {
    "brand": "VizeAtlas Dubai",
    "phone": "+90 850 000 00 00",
    "whatsapp": "908500000000",
    "email": "destek@vizeatlas.com",
    "address": "Levent, İstanbul / Türkiye",
    "working_hours": "Hafta içi 09:00 - 19:00, Cumartesi 10:00 - 16:00",
}
