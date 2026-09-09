"""Static Turkish content + seed data for the Dubai visa site.
Prices are sample values in TRY and can be edited from the admin panel.
"""

# category: single | multiple | child | other
VISA_TYPES = [
    {
        "id": "visa_30_single",
        "slug": "30-gun-tek-giris",
        "name": "30 Günlük Tek Girişli Dubai Vizesi",
        "short_name": "30 Gün Tek Giriş",
        "category": "single",
        "duration_days": 30,
        "entry_type": "single",
        "entry_label": "Tek Giriş",
        "applicant_type": "adult",
        "price": 5190.0,
        "price_usd": 105.0,
        "currency": "TRY",
        "processing_days": "36 saatte",
        "popular": True,
        "order": 1,
        "description": "Dubai seyahatiniz 1-30 gün arasıysa ve tek seferlik gidiş-dönüş yapacaksanız bu vize uygundur.",
        "features": [
            "30 gün kalış hakkı",
            "Tek giriş",
            "Online başvuru",
            "Uzman danışman desteği",
            "Dijital vize teslimi",
        ],
    },
    {
        "id": "visa_60_single",
        "slug": "60-gun-tek-giris",
        "name": "60 Günlük Tek Girişli Dubai Vizesi",
        "short_name": "60 Gün Tek Giriş",
        "category": "single",
        "duration_days": 60,
        "entry_type": "single",
        "entry_label": "Tek Giriş",
        "applicant_type": "adult",
        "price": 9880.0,
        "price_usd": 200.0,
        "currency": "TRY",
        "processing_days": "36 saatte",
        "popular": False,
        "order": 2,
        "description": "Dubai seyahatiniz 1-60 gün arasıysa ve tek seferlik gidiş-dönüş yapacaksanız bu vize uygundur.",
        "features": [
            "60 gün kalış hakkı",
            "Tek giriş",
            "Online başvuru",
            "Uzman danışman desteği",
            "Dijital vize teslimi",
        ],
    },
    {
        "id": "visa_30_multi",
        "slug": "30-gun-cok-giris",
        "name": "30 Günlük Çok Girişli Dubai Vizesi",
        "short_name": "30 Gün Çok Giriş",
        "category": "multiple",
        "duration_days": 30,
        "entry_type": "multiple",
        "entry_label": "Çok Giriş",
        "applicant_type": "adult",
        "price": 9880.0,
        "price_usd": 200.0,
        "currency": "TRY",
        "processing_days": "3-5 iş günü",
        "popular": True,
        "order": 3,
        "description": "30 gün içinde Umman, Katar gibi ülkelere geçip Dubai'ye tekrar dönecekseniz bu vize uygundur.",
        "features": [
            "30 gün kalış hakkı",
            "Sınırsız giriş-çıkış",
            "Online başvuru",
            "Uzman danışman desteği",
            "Dijital vize teslimi",
        ],
    },
    {
        "id": "visa_60_multi",
        "slug": "60-gun-cok-giris",
        "name": "60 Günlük Çok Girişli Dubai Vizesi",
        "short_name": "60 Gün Çok Giriş",
        "category": "multiple",
        "duration_days": 60,
        "entry_type": "multiple",
        "entry_label": "Çok Giriş",
        "applicant_type": "adult",
        "price": 14820.0,
        "price_usd": 300.0,
        "currency": "TRY",
        "processing_days": "3-5 iş günü",
        "popular": False,
        "order": 4,
        "description": "Dubai'ye 60 gün içinde birden fazla giriş yapacaksanız bu vize uygundur.",
        "features": [
            "60 gün kalış hakkı",
            "Sınırsız giriş-çıkış",
            "Online başvuru",
            "Uzman danışman desteği",
            "Dijital vize teslimi",
        ],
    },
    {
        "id": "visa_30_child",
        "slug": "30-gun-cocuk-vizesi",
        "name": "30 Günlük Tek Girişli Çocuk Vizesi",
        "short_name": "30 Gün Çocuk",
        "category": "child",
        "duration_days": 30,
        "entry_type": "single",
        "entry_label": "Tek Giriş",
        "applicant_type": "child",
        "price": 2470.0,
        "price_usd": 50.0,
        "currency": "TRY",
        "processing_days": "36 saatte",
        "popular": True,
        "order": 5,
        "description": "Çocuğunuzun seyahati 1-30 gün arasıysa ve ailesiyle tek seferlik gidiş-dönüş yapacaksa bu indirimli vize uygundur.",
        "features": [
            "30 gün kalış hakkı",
            "Tek giriş · 18 yaş altı indirimli",
            "Online başvuru",
            "Uzman danışman desteği",
            "Dijital vize teslimi",
        ],
    },
    {
        "id": "visa_60_child",
        "slug": "60-gun-cocuk-vizesi",
        "name": "60 Günlük Tek Girişli Çocuk Vizesi",
        "short_name": "60 Gün Çocuk",
        "category": "child",
        "duration_days": 60,
        "entry_type": "single",
        "entry_label": "Tek Giriş",
        "applicant_type": "child",
        "price": 5190.0,
        "price_usd": 105.0,
        "currency": "TRY",
        "processing_days": "3-5 iş günü",
        "popular": False,
        "order": 6,
        "description": "Çocuğunuzun seyahati 1-60 gün arasıysa ve ailesiyle tek seferlik gidiş-dönüş yapacaksa bu indirimli vize uygundur.",
        "features": [
            "60 gün kalış hakkı",
            "Tek giriş · 18 yaş altı indirimli",
            "Online başvuru",
            "Uzman danışman desteği",
            "Dijital vize teslimi",
        ],
    },
    {
        "id": "visa_extension_30",
        "slug": "30-gun-vize-uzatma",
        "name": "30 Günlük Vize Uzatma",
        "short_name": "Vize Uzatma",
        "category": "single",
        "duration_days": 30,
        "entry_type": "single",
        "entry_label": "Uzatma",
        "applicant_type": "adult",
        "price": 14820.0,
        "price_usd": 300.0,
        "currency": "TRY",
        "processing_days": "2-4 iş günü",
        "popular": False,
        "order": 7,
        "auto_suggest": False,
        "description": "Dubai'deyken ülkeden çıkış yapmadan 30 gün daha kalmak istiyorsanız bu hizmet uygundur.",
        "features": [
            "30 gün ek kalış hakkı",
            "Ülkeden çıkmadan uzatma · en fazla 2 kez",
            "Online başvuru",
            "Uzman danışman desteği",
            "Dijital vize teslimi",
        ],
    },
]

VISA_CATEGORIES = [
    {"id": "single", "label": "Tek Girişli Vize"},
    {"id": "multiple", "label": "Çok Girişli Vize"},
    {"id": "child", "label": "Çocuk Vizesi"},
]

# Optional paid add-ons, priced per traveller
ADDONS = {
    "express": {
        'id': 'express',
        'name': 'Ekspres Vize Hizmeti',
        'price': 2470.0,
        'price_usd': 50.0,
        'currency': 'TRY',
        'per_person': True,
        'description': 'Acil seyahatler için öncelikli işlem. Başvurunuz sıraya girmeden işleme alınır, sonuç 12 saat içinde çıkar.',
        'features': ['12 saat içinde sonuç', 'Öncelikli işlem sırası', 'Anlık bilgilendirme'],
    },
}

# Geriye uyumluluk: eski basvurularda saklanan ek hizmet adlari
LEGACY_ADDONS = {
    "insurance": {
        'id': 'insurance',
        'name': 'Seyahat Sağlık Sigortası · Temel',
        'price': 349.0,
        'price_usd': 20.0,
        'currency': 'TRY',
        'per_person': True,
        'description': "BAE'de sağlık masrafları yüksektir. Seyahat sürenizi kapsayan sağlık sigortasını başvurunuza ekleyin.",
        'features': ['Seyahat süresi boyunca geçerli', 'Acil sağlık masrafları', 'Dijital poliçe'],
    },
    "insurance_plus": {
        'id': 'insurance_plus',
        'name': 'Seyahat Sigortası · Geniş Kapsam',
        'price': 689.0,
        'price_usd': 39.0,
        'currency': 'TRY',
        'per_person': True,
        'description': 'Uzun kalışlar için 100.000 € teminatlı poliçe; bagaj kaybı ve seyahat iptali risklerini de kapsar.',
        'features': ['100.000 € teminat', '60 güne kadar', 'Bagaj ve iptal teminatı'],
    },
    "esim": {
        'id': 'esim',
        'name': 'Dubai eSIM · 3 GB / 15 gün',
        'price': 265.0,
        'price_usd': 15.0,
        'currency': 'TRY',
        'per_person': True,
        'description': "Dubai'ye indiğiniz anda internetiniz hazır olsun. QR kod ile 2 dakikada kurulur, hattınız açık kalır.",
        'features': ['3 GB veri / 15 gün', 'QR kod ile anında kurulum', 'Hotspot açık'],
    },
}

# (minimum traveller count, discount rate on visa subtotal)
# Aile basvurusu: 2-3 kisi %10, 4 kisi ve uzeri %15 (en yuksek uyan kademe uygulanir)
FAMILY_DISCOUNT_TIERS = [(2, 0.10), (4, 0.15)]

FAMILY_DISCOUNT_TEXT = (
    "Aile başvurularında 2-3 kişi için %10, 4 kişi ve üzeri için %15 aile indirimi "
    "otomatik uygulanır."
)

MAX_TRAVELERS = 10

REQUIRED_DOCUMENTS = [
    {
        "key": "passport",
        "title": "Pasaport Fotoğrafı",
        "detail": "Dönüş tarihinizden itibaren en az 6 ay geçerliliği bulunan pasaportunuzun kimlik bilgileri sayfasının net fotoğrafı veya taraması.",
        "required": True,
    },
    {
        "key": "photo",
        "title": "Vesikalık Fotoğraf",
        "detail": "Düz beyaz arka fonda çekilmiş, yüzün tamamı görünen net bir vesikalık veya biyometrik fotoğraf.",
        "required": True,
    },
    {
        "key": "ticket",
        "title": "Dönüş Uçak Bileti",
        "detail": "Zorunlu değildir. Vizeniz onaylanmadan bilet almanıza gerek yok; varsa rezervasyon/opsiyon belgesini yükleyebilirsiniz, yoksa boş bırakın.",
        "required": False,
    },
    {
        "key": "hotel",
        "title": "Otel Rezervasyonu",
        "detail": "Zorunlu değildir. Otelinizi vizeniz çıktıktan sonra rahatça seçebilirsiniz; elinizde rezervasyon varsa yüklemek başvurunuzu güçlendirir.",
        "required": False,
    },
]

PHOTO_RULES = [
    "Beyaz veya açık gri fon kullanın.",
    "Yüzünüz kadrajın ortasında ve tamamen görünür olmalı.",
    "Gözlük, şapka, güneş gözlüğü kullanılmamalı.",
    "Fotoğraf son 6 ay içinde çekilmiş olmalı.",
    "Bulanık veya filtreli fotoğraflar kabul edilmez.",
]

PROCESS_STEPS = [
    {"step": 1, "title": "Vize tipini seçin", "detail": "Kalış süreniz, giriş sayınız ve yaşınıza göre uygun vizeyi seçin. Fiyatlar net ve tek seferliktir."},
    {"step": 2, "title": "Yolcuları ekleyin", "detail": "Tek formda tüm aileyi ekleyin. Çocuklar için indirimli vize ve aile indirimi otomatik hesaplanır."},
    {"step": 3, "title": "Belgeleri yükleyip ödeyin", "detail": "Pasaport ve vesikalık fotoğraflarını yükleyin, güvenli altyapı üzerinden ödemenizi tamamlayın."},
    {"step": 4, "title": "Vizeniz e-postanıza gelsin", "detail": "Başvurunuzu biz takip ediyoruz. Onaylanan vizeniz PDF olarak e-postanıza ve takip sayfanıza yüklenir."},
]

WHY_US = [
    {"title": "Şeffaf fiyat", "detail": "Gizli masraf yok. Dosya açma veya danışmanlık adı altında ek kalem çıkarmayız."},
    {"title": "Evrak kontrolü bizde", "detail": "Yüklediğiniz her belgeyi başvuru öncesi kontrol ediyoruz. Eksik varsa sizi arıyoruz."},
    {"title": "Hızlı sonuç", "detail": "Standart başvurular 36 saat, ekspres başvurular 12 saat içinde sonuçlanır."},
    {"title": "Gerçek insan desteği", "detail": "WhatsApp ve telefonla ulaşabileceğiniz Türkçe danışman ekibi."},
]

SERVICES = [
    {"key": "visa", "title": "Dubai Vizesi", "detail": "Vize başvurunuzu eksiksiz ve hatasız tamamlamanız için baştan sona uzman desteği."},
    {"key": "family", "title": "Aile Başvurusu", "detail": "Tek formda tüm aileyi ekleyin; aile ve çocuk indirimleri otomatik hesaplansın."},
    {"key": "documents", "title": "Evrak Kontrolü", "detail": "Pasaport, vesikalık ve ek belgeleriniz başvuru gönderilmeden önce ücretsiz kontrol edilir."},
    {"key": "express", "title": "Ekspres Vize", "detail": "Acil seyahatlerde başvurunuz öncelikli sıraya alınır, sonuç 12 saat içinde gelir."},
    {"key": "extension", "title": "Vize Uzatma", "detail": "Ülkeden çıkmadan kalış sürenizi uzatma işlemlerinizi sizin adınıza yürütüyoruz."},
    {"key": "support", "title": "Başvuru Takibi ve Destek", "detail": "Takip kodunuzla süreci anlık izleyin; danışmanınız her aşamada ulaşılabilir olsun."},
]

TOURS = []

PARTNERS = [
    {"name": "Emirates", "logo": "/brand/partners/emirates.png"},
    {"name": "flydubai", "logo": "/brand/partners/flydubai.png"},
    {"name": "Turkish Airlines", "logo": "/brand/partners/turkish-airlines.png"},
    {"name": "Pegasus", "logo": "/brand/partners/pegasus.png"},
    {"name": "AJet", "logo": "/brand/partners/ajet.png"},
    {"name": "SunExpress", "logo": "/brand/partners/sunexpress.png"},
]

TESTIMONIALS = [
    {
        "name": "Elif K.",
        "initials": "EK",
        "city": "İstanbul",
        "visa": "30 Gün Tek Giriş",
        "date": "2026-07-18",
        "verified": True,
        "text": "Formu 5 dakikada doldurdum, 3 gün sonra vizem e-postama geldi. Eksik belgemi telefonla arayıp söylediler, çok ilgililer.",
        "rating": 5,
    },
    {
        "name": "Mert A.",
        "initials": "MA",
        "city": "İzmir",
        "visa": "60 Gün Çok Giriş",
        "date": "2026-07-02",
        "verified": True,
        "text": "İş seyahati için çok giriş vizesi aldım. Fiyat baştan netti, sürpriz masraf çıkmadı. Takip kodu ile süreci görmek çok rahat.",
        "rating": 5,
    },
    {
        "name": "Zeynep D.",
        "initials": "ZD",
        "city": "Ankara",
        "visa": "Aile Başvurusu · 4 kişi",
        "date": "2026-06-21",
        "verified": True,
        "text": "Eşim ve iki çocuğumuzla tek formdan başvurduk. Çocuk vizesi indirimi ve aile indirimi otomatik hesaplandı, ayrı ayrı uğraşmadık.",
        "rating": 5,
    },
    {
        "name": "Burak Ş.",
        "initials": "BŞ",
        "city": "Bursa",
        "visa": "Ekspres · 30 Gün",
        "date": "2026-06-09",
        "verified": True,
        "text": "Uçuşuma 2 gün kalmıştı, ekspres hizmeti aldım. Vizem 12 saat içinde elimdeydi. Gece yarısı yazdığım mesaja bile dönüş yaptılar.",
        "rating": 5,
    },
    {
        "name": "Selin T.",
        "initials": "ST",
        "city": "Antalya",
        "visa": "30 Gün Tek Giriş",
        "date": "2026-05-27",
        "verified": True,
        "text": "Vesikalık fotoğrafım kriterlere uymuyormuş, başvuru gönderilmeden önce uyardılar. Reddedilseydi ücreti yakacaktım.",
        "rating": 5,
    },
    {
        "name": "Hakan Y.",
        "initials": "HY",
        "city": "Kocaeli",
        "visa": "Aile Başvurusu · 3 kişi",
        "date": "2026-05-11",
        "verified": True,
        "text": "Annemi ve babamı da ekledim, hepsinin pasaportunu tek ekrandan yükledim. Onay PDF'leri aynı gün e-postama düştü.",
        "rating": 4,
    },
]

REVIEW_SUMMARY = {
    "average": 4.9,
    "total_reviews": 1284,
    "total_applications": 5678,
    "recommend_rate": 98,
    "highlights": [
        {"label": "Zamanında sonuç", "value": 99},
        {"label": "Danışman iletişimi", "value": 97},
        {"label": "Fiyat şeffaflığı", "value": 96},
    ],
}

FAQ = [
    {
        "q": "Dubai vize başvurusu nasıl yapılır?",
        "a": "Başvurunuzu tamamen online olarak sitemizden iletebilirsiniz. Vize tipini seçiyor, yolcu bilgilerini giriyor, pasaport ve vesikalık fotoğrafınızı yüklüyor ve ödemenizi yapıyorsunuz. Başvurunuz tarafımızca kontrol edilip yetkili mercilere iletilir.",
    },
    {
        "q": "Dubai vizesi için gerekli evraklar nelerdir?",
        "a": "Pasaportunuzun kimlik bilgileri sayfasının fotoğrafı, beyaz fonda bir vesikalık fotoğraf zorunludur. Dönüş uçak bileti ve otel rezervasyonu opsiyoneldir ancak yüklenmesi başvurunuzu güçlendirir.",
    },
    {
        "q": "Vize almadan uçak bileti ve otel rezervasyonu yapmam gerekiyor mu?",
        "a": "Hayır. Başvurunuz için sadece pasaportunuzun kimlik sayfası ve bir vesikalık fotoğraf yeterlidir. Uçak biletinizi ve otel rezervasyonunuzu vizeniz onaylandıktan sonra almanız hem bütçenizi hem de plan değişikliği riskini korur. Elinizde rezervasyon varsa yüklemek başvurunuzu güçlendirir, ancak zorunlu değildir.",
    },
    {
        "q": "Ailemle birlikte tek başvuru yapabilir miyim?",
        "a": "Evet. Başvuru formunda 'Yolcu ekle' butonuyla eşinizi ve çocuklarınızı aynı başvuruya ekleyebilirsiniz. 18 yaş altı yolcular için indirimli çocuk vizesi, 2-3 kişilik başvurularda %10, 4 kişi ve üzeri başvurularda %15 aile indirimi otomatik uygulanır.",
    },
    {
        "q": "Vize işlemi ne kadar sürüyor?",
        "a": "Belgeleriniz eksiksiz olduğunda standart başvurular 36 saat içinde sonuçlanır. Ekspres vize hizmetiyle sonuç 12 saat içinde çıkar.",
    },
    {
        "q": "36 saat garantisi nasıl işliyor?",
        "a": "Belgeleriniz eksiksizse başvurunuzun 36 saat içinde sonuçlanacağını taahhüt ediyoruz. Süre aşılırsa ödediğiniz ekspres hizmet bedelini iade ediyoruz; ekspres hizmet almadıysanız başvurunuzu ücretsiz olarak ekspres sıraya alıyoruz. Süre, belgeleriniz onaylanıp başvurunuz resmî mercilere iletildiği anda başlar; resmî tatiller ile mercilerin ek belge veya inceleme talepleri süreye dahil değildir.",
    },
    {
        "q": "Pasaportumu göndermem gerekiyor mu?",
        "a": "Hayır. BAE vizesi elektronik olarak düzenlenir ve pasaportunuza işlenmez. Onaylanan vizeniz PDF olarak tarafınıza iletilir; sınır kapısında bu belgeyi göstermeniz yeterlidir.",
    },
    {
        "q": "Pasaportumun ne kadar geçerli olması gerekiyor?",
        "a": "Pasaportunuzun dönüş tarihinizden itibaren en az 6 ay geçerli olması gerekir. Bu, başvurunun tek teknik şartıdır.",
    },
    {
        "q": "Yeşil pasaport için vize gerekiyor mu?",
        "a": "Hususi (yeşil), hizmet (gri) ve diplomatik pasaport hamilleri BAE'ye yılda 90 güne kadar vizesiz giriş yapabilir. Umuma mahsus bordo pasaport sahipleri için vize zorunludur.",
    },
    {
        "q": "Dubai vizesiyle diğer emirliklere gidebilir miyim?",
        "a": "Evet. Aldığınız vize bir Birleşik Arap Emirlikleri vizesidir; Abu Dabi ve Şarja dahil yedi emirliğin tamamında geçerlidir.",
    },
    {
        "q": "Ödeme nasıl yapılıyor, güvenli mi?",
        "a": "Ödemeler uluslararası ödeme altyapısı üzerinden 3D Secure destekli alınır. Kart bilgileriniz sunucularımıza kaydedilmez.",
    },
    {
        "q": "Vizem onaylanmazsa ne olur?",
        "a": "Resmî harcın dışında kalan hizmet bedelimizi iade ediyoruz. Ret gerekçesini sizinle paylaşıp yeniden başvuru için yol haritası sunuyoruz.",
    },
    {
        "q": "18 yaş altı çocuklar tek başına vize alabilir mi?",
        "a": "Hayır. 18 yaş altındaki yolcular anne veya babasıyla birlikte başvuru yapmalı ve seyahat etmelidir. Tek başına yapılan başvurularda ret riski çok yüksektir.",
    },
    {
        "q": "Anne ile çocuğun soyadı farklı; hangi ek belgeler gerekiyor?",
        "a": "Soyadı uyuşmayan çocuk yolcular için pasaport ve vesikalık dışında; velinin önlü arkalı kimlik fotoğrafı ve e-Devlet'ten alacağınız doğum belgesi (Formül A) gerekir. Boşanma durumunda velayet belgesi de istenebilir.",
    },
    {
        "q": "Ödemeyi havale/EFT ile yapabilir miyim?",
        "a": "Evet. Ödeme adımında 'Havale / EFT' seçeneğini işaretleyin; başvuru referans kodunuzla birlikte banka bilgilerimiz ekranda ve e-postanızda yer alır. Ödemeniz hesabımıza geçtiğinde başvurunuz işleme alınır.",
    },
    {
        "q": "Vize süremi aşarsam ne olur?",
        "a": "Vize süreniz dolmadan ülkeden çıkmanız veya yurt içi uzatma yaptırmanız gerekir. Süre aşımında BAE makamları günlük ceza uygular; kaçak kalış tespit edilirse tarafınıza kaçış raporu (Escape Report) düzenlenir ve doğan tüm masraflar faturalandırılır.",
    },
    {
        "q": "Başvurum reddedilirse ücret iadesi yapılıyor mu?",
        "a": "Resmî makamlara ödenen harç iade edilmez; iade koşullarımızın tamamını 'İade ve İptal Koşulları' sayfamızda bulabilirsiniz. Ret gerekçesi ortadan kalktığında yeniden başvuru yapılabilir (aktif vize, başka acenteden devam eden başvuru veya geçmiş deport kaydı gibi).",
    },
    {
        "q": "Form doldurmak istemiyorum, WhatsApp'tan başvurabilir miyim?",
        "a": "Evet. Pasaportunuzun kimlik sayfası ile bir vesikalık fotoğrafınızı WhatsApp hattımıza veya e-posta adresimize gönderin; başvurunuzu sizin adınıza biz oluşturup ödeme bağlantısını iletelim.",
    },
    {
        "q": "Başvurumu nasıl takip ederim?",
        "a": "Başvurunuz oluştuğunda size bir takip kodu veriyoruz. 'Başvuru Takip' sayfasından takip kodunuz ve soyadınızla durumu anında görebilir, onaylanan vizenizi indirebilirsiniz.",
    },
]

ARTICLES = [
    {        "slug": "dubai-vizesi-hangi-emirliklerde-gecerli",
        "title": "Dubai Vizesi Abu Dabi ve Şarja'da Geçerli mi?",
        "date": "2026-08-25",
        "cover_image": "https://images.unsplash.com/photo-1688671525781-d9447cf1abd2?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
        "excerpt": "Dubai vizesi aslında bir Birleşik Arap Emirlikleri vizesidir. Aldığınız vize yalnızca Dubai'de değil, yedi emirliğin tamamında geçerlidir.",
        "body": [
            "Aldığınız belge resmî olarak bir Birleşik Arap Emirlikleri vizesidir. Bu nedenle Dubai'nin yanı sıra Abu Dabi, Şarja, Acman, Umm el-Kayveyn, Re's el-Hayma ve Fuceyre'de de geçerlidir.",
            "Emirlikler arasında pasaport kontrolü yoktur. Dubai'ye giriş yapıp Abu Dabi'den ülkeyi terk edebilir, araçla emirlikler arasında serbestçe dolaşabilirsiniz.",
            "Dikkat edilmesi gereken tek nokta kalış süresidir: 30 veya 60 günlük süre ülkeye giriş yaptığınız gün başlar ve takvim günü olarak işler.",
        ],
    },
    {
        "slug": "dubai-vize-pasaport-suresi",
        "title": "Dubai Vizesi İçin Pasaport Süresi: 6 Ay Kuralı",
        "date": "2026-08-20",
        "excerpt": "Başvurularda en sık takılan nokta pasaport süresidir. Kural net: pasaportunuz dönüş tarihinizden itibaren en az 6 ay geçerli olmalı.",
        "body": [
            "Pasaportunuzun geçerlilik süresi, planladığınız dönüş tarihinden itibaren en az 6 ay olmalıdır. 6 aydan az kalan pasaportlarla yapılan başvurular doğrudan reddedilir.",
            "Süresi yaklaşan pasaportları yenilemek genellikle birkaç iş günü sürüyor. Vize başvurusundan önce pasaport yenilemenizi tamamlamanızı öneriyoruz.",
            "Başvuru formunda pasaport geçerlilik tarihini girdiğinizde sistem sizi otomatik olarak uyarır.",
        ],
    },
    {
        "slug": "dubai-seyahat-sigortasi",
        "title": "Dubai Seyahat Sağlık Sigortası: Kapsam ve Şartlar",
        "date": "2026-08-14",
        "excerpt": "Dubai seyahati için sigorta zorunlu değil. Ancak BAE'de sağlık masrafları yüksek olduğu için kesinlikle öneriyoruz.",
        "body": [
            "Turistik vize başvurusunda seyahat sağlık sigortası zorunlu tutulmuyor. Buna rağmen BAE'de özel hastane ücretleri Avrupa seviyesinin üzerinde olabiliyor.",
            "Başvuru formundaki 'Seyahat Sağlık Sigortası' seçeneğini işaretleyerek poliçenizi başvurunuzla birlikte oluşturabilirsiniz.",
            "Poliçe, seyahat tarihlerinizi kapsayacak şekilde düzenlenir ve dijital olarak e-postanıza iletilir.",
        ],
    },
    {
        "slug": "dubai-vize-uzatma",
        "title": "Dubai Vize Uzatma: Ülkeden Çıkmadan 30 Gün",
        "date": "2026-08-08",
        "excerpt": "Dubai'de kalış süreniz yetmiyorsa ülkeden çıkmanıza gerek yok. Vizenizi 30 gün uzatabilirsiniz.",
        "body": [
            "Vize uzatma işlemi ülke içinden, çıkış yapmadan tamamlanır. Uzatma süresi 30 gündür ve en fazla 2 kez yapılabilir.",
            "Uzatma başvurusunun, mevcut vizenizin bitim tarihinden en az 3 gün önce yapılması gerekir. Aksi halde ceza uygulanabilir.",
            "Uzatma başvurusu için 'Diğer Hizmetler' sekmesinden 30 Günlük Vize Uzatma hizmetini seçebilirsiniz.",
        ],
    },
    {
        "slug": "dubai-vize-reddi",
        "title": "Dubai Vize Reddini Önleme Rehberi",
        "date": "2026-07-29",
        "excerpt": "Ret kararlarının büyük bölümü önlenebilir hatalardan kaynaklanıyor. En sık rastladığımız 5 sebep.",
        "body": [
            "1. Uygun olmayan vesikalık fotoğraf: filtreli, karanlık veya renkli fonda çekilmiş fotoğraflar en sık ret sebebidir.",
            "2. Okunamayan pasaport taraması: köşeleri kesik, parlamalı veya bulanık görüntüler işlemi geciktirir.",
            "3. Seyahat amacıyla uyuşmayan vize tipi: oturum, çalışma veya eğitim amaçlı seyahatlerde turistik vize kullanılamaz.",
            "4. Ad-soyad yazım hataları: bilgilerinizi pasaportta yazdığı gibi, Türkçe karakter kullanmadan girin.",
            "5. Yetersiz pasaport süresi: 6 ay kuralını mutlaka kontrol edin.",
        ],
    },
]

IMPORTANT_NOTICE = [
    "Vize kararı yalnızca Birleşik Arap Emirlikleri Göçmenlik İdaresi'nin (GDRFA) yetkisindedir. Biz başvurunuzu hazırlar, kontrol eder ve resmî sisteme iletiriz; onay veya ret kararını idare verir. İdare ek belge talep ederse ya da ilave inceleme yaparsa belirtilen işlem süresi uzayabilir.",
    "Seçtiğiniz vize türü seyahat amacınızla örtüşmelidir. Amacınız oturum, çalışma veya eğitim ise; turistik, ticari ya da ziyaret vizesiyle ülkeye giriş yapıp resmî oturum işlemlerinizi başlatamazsınız.",
    "Turistik/ticari/ziyaret vizesiyle giriş yapıp oturum işlemi başlatma girişimi, vizenin anında iptaline ve sınır dışı edilmenize yol açar.",
    "Oturum, çalışma veya eğitim vizesiyle gelen yolcuların resmî işlemleri havalimanında, giriş anında başlatması zorunludur. Bu yapılmadığında vize geçersiz sayılır ve aynı yaptırım uygulanır.",
    "Sınır dışı işlemi uygulanan kişilerin Birleşik Arap Emirlikleri'ne yeniden girişi kapatılır. Bu nedenle başvurudan önce vize türünüzün seyahat amacınıza uygun olduğundan emin olun; tereddüt ederseniz başvuruyu göndermeden danışmanımıza yazın.",
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
    "brand": "Dubai Vize Hattı",
    "legal_name": "Moruya Travel Solutions Turizm Ltd. Şti.",
    "parent_company": "Moruya Travel Solutions Turizm Ltd. Şti.",
    "dubai_company": "Moruya Travel Solutions FZE",
    "phone": "+90 538 483 82 24",
    "whatsapp": "905384838224",
    "email": "info@dubaivizehatti.com",
    "instagram": "https://www.instagram.com/dubaivizehatti/",
    "google_review": "https://www.google.com/search?q=Dubai+Vize+Hatt%C4%B1+yorumlar",
    "address": "Büyükdere Caddesi Nurol Plaza No:255/B02, 34450 Sarıyer / İstanbul - Türkiye",
    "dubai_address": "Level 27, Unit 2705, Marina Plaza, Dubai Marina, Dubai - United Arab Emirates",
    "dubai_phone": "+971 50 867 26 30",
    "working_hours": "Hafta içi 09:00 - 19:00, Cumartesi 10:00 - 16:00",
    # Yasal kunye alanlari: gercek degerler admin -> Acente ekranindan girilir.
    # Bos birakilan satirlar sitede hic gosterilmez; ornek/sifir deger yaziLMAZ.
    "tursab_no": "",
    "tursab_type": "A Grubu Seyahat Acentesi",
    "tax_office": "Beşiktaş Vergi Dairesi",
    "tax_no": "",
    "mersis_no": "",
    "trade_registry_no": "",
    "founded_year": "2019",
}

AGENCY_INFO = {
    "title": "Acente Bilgilerimiz",
    "description": "Dubai Vize Hattı, TÜRSAB üyesi bir seyahat acentesidir. Tüm başvurularınız acente güvencesiyle yürütülür.",
    "items": [
        {"label": "Ticaret Unvanı", "value": COMPANY["legal_name"]},
        {"label": "TÜRSAB Belge No", "value": COMPANY["tursab_no"]},
        {"label": "Acente Türü", "value": COMPANY["tursab_type"]},
        {"label": "Vergi Dairesi / No", "value": f"{COMPANY['tax_office']} / {COMPANY['tax_no']}"},
        {"label": "MERSİS No", "value": COMPANY["mersis_no"]},
        {"label": "Ticaret Sicil No", "value": COMPANY["trade_registry_no"]},
        {"label": "Adres", "value": COMPANY["address"]},
        {"label": "Kuruluş", "value": COMPANY["founded_year"]},
    ],
}


def affiliation_note(company: dict | None = None) -> str:
    """Isletici sirket ve BAE grup sirketi bilgisi; adlar **kalin** isaretlenir."""
    c = company or COMPANY
    parent = c.get("parent_company") or COMPANY["parent_company"]
    dubai = c.get("dubai_company") or COMPANY["dubai_company"]
    return (
        f"Dubai Vize Hattı, **{parent}**'nin tescilli markası olup, tüm hizmet ve "
        f"operasyonlar bu şirket tarafından yürütülmektedir. Birleşik Arap "
        f"Emirlikleri'ndeki grup şirketimiz **{dubai}**'dir."
    )


def brand_footer_lines(company: dict | None = None, site_label: str = "www.dubaivizehatti.com") -> list:
    """PDF ve e-postalarin en altinda kullanilan kunye satirlari (tek kaynak).

    1) unvan · acente turu · telefon · e-posta · site
    2) Istanbul ofis adresi
    3) marka/isletici bilgisi
    4) BAE grup sirketi
    """
    c = {**COMPANY, **(company or {})}
    note = affiliation_note(c).replace("**", "")
    first, _, second = note.partition("Birleşik Arap")
    return [
        f"{c['legal_name']} · TÜRSAB Üyesi {c['tursab_type']} · {c['phone']} · {c['email']} · {site_label}",
        c["address"],
        first.strip(),
        f"Birleşik Arap{second}".strip(),
    ]


def family_discount_rate(traveler_count: int) -> float:
    """Yolcu sayisina uyan en yuksek aile indirimi oranini dondurur."""
    rates = [rate for minimum, rate in FAMILY_DISCOUNT_TIERS if traveler_count >= minimum]
    return max(rates) if rates else 0.0


# Sigorta + eSIM birlikte alindiginda ek urun toplamina uygulanan indirim
BUNDLE_DISCOUNT = {
    "rate": 0.10,
    "title": "Seyahat paketi indirimi",
    "badge": "Sigorta + eSIM = %10 indirim",
    "note": "Sigorta ve eSIM'i birlikte alın, %10 indirim otomatik uygulanır.",
    "kinds": ["insurance", "esim"],
}


# Sigortayi vize basvurusuyla birlikte alan musteriye poliçe bedelinde indirim
# (tek basina magazadan alimda gecerli degil - amac vize + sigorta paketini cazip kilmak)
WITH_VISA_INSURANCE_DISCOUNT = {
    "rate": 0.10,
    "title": "Sigorta dahil vize indirimi",
    "badge": "Vize + sigorta = poliçede %10 indirim",
    "card_badge": "Vize ile birlikte %10 indirim",
    "note": "Sigortayı vize başvurunuzla birlikte alın, poliçe bedelinde %10 indirim uygulanır.",
}


def visa_insurance_discount_amount(store_lines) -> float:
    """Vize basvurusuyla birlikte alinan sigorta satirlarina indirim uygular."""
    total = sum(
        float(line.get("total") or 0)
        for line in (store_lines or [])
        if (line.get("kind") or "") == "insurance"
    )
    if total <= 0:
        return 0.0
    return round(total * float(WITH_VISA_INSURANCE_DISCOUNT["rate"]), 2)


def bundle_discount_amount(store_lines) -> float:
    """Sigorta + eSIM birlikte secildiyse ek urun toplamina indirim uygular."""
    lines = list(store_lines or [])
    kinds = {(line.get("kind") or "") for line in lines}
    if not set(BUNDLE_DISCOUNT["kinds"]).issubset(kinds):
        return 0.0
    total = sum(float(line.get("total") or 0) for line in lines)
    return round(total * float(BUNDLE_DISCOUNT["rate"]), 2)


def _addon_lines(addons: dict, count: int, addon_prices: dict | None) -> tuple[list, float]:
    """Secili ek hizmetleri fatura satirlarina cevirir; (satirlar, toplam) doner."""
    lines = []
    for key, meta in ADDONS.items():
        if not addons.get(key):
            continue
        unit_price = float((addon_prices or {}).get(key, meta["price"]))
        quantity = count if meta["per_person"] else 1
        lines.append(
            {
                "id": key,
                "name": meta["name"],
                "unit_price": unit_price,
                "quantity": quantity,
                "total": round(unit_price * quantity, 2),
            }
        )
    return lines, round(sum(line["total"] for line in lines), 2) if lines else 0.0


def compute_pricing(
    visa_prices,
    addons: dict,
    currency: str = "TRY",
    addon_prices: dict | None = None,
    store_lines: list | None = None,
) -> dict:
    """Server-side authoritative pricing. visa_prices = list of float per traveller."""
    count = len(visa_prices)
    subtotal = round(sum(float(p) for p in visa_prices), 2)
    rate = family_discount_rate(count)
    discount = round(subtotal * rate, 2)
    addon_lines, addons_total = _addon_lines(addons, count, addon_prices)
    store_lines = list(store_lines or [])
    store_total = round(sum(float(line.get("total") or 0) for line in store_lines), 2)
    bundle_discount = bundle_discount_amount(store_lines)
    insurance_discount = visa_insurance_discount_amount(store_lines)
    total = round(
        subtotal - discount + addons_total + store_total - bundle_discount - insurance_discount, 2
    )
    return {
        "traveler_count": count,
        "subtotal": subtotal,
        "family_discount_rate": rate,
        "family_discount": discount,
        "addons": addon_lines,
        "addons_total": addons_total,
        "store_items": store_lines,
        "store_total": store_total,
        "visa_insurance_discount": insurance_discount,
        "visa_insurance_discount_rate": (
            float(WITH_VISA_INSURANCE_DISCOUNT["rate"]) if insurance_discount else 0.0
        ),
        "visa_insurance_discount_title": WITH_VISA_INSURANCE_DISCOUNT["title"],
        "bundle_discount": bundle_discount,
        "bundle_discount_rate": float(BUNDLE_DISCOUNT["rate"]) if bundle_discount else 0.0,
        "bundle_discount_title": BUNDLE_DISCOUNT["title"],
        "total": total,
        "currency": currency,
    }


# --------------------------------------------------------------- Odeme / hukuk

# Vize onaylandiginda musteriye gonderilen resmi dogrulama yonlendirmesi.
# Ayni metin e-posta (emailer) ve WhatsApp (whatsapp/wa_docs) kanallarinda kullanilir.
GDRFA_STATUS_URL = "https://smart.gdrfad.gov.ae/Public_Th/StatusInquiry_New.aspx"

GDRFA_INTRO = (
    "Dubai Göçmenlik İdaresi'nin (GDRFA) sorgulama sayfasından vizenizin durumunu "
    "kendiniz de görebilirsiniz. Bu adım zorunlu değildir; vizeniz onaylanmış olarak "
    "tarafımıza ulaştı."
)

GDRFA_STEPS = (
    "Bağlantıyı açın ve sayfanın üst kısmındaki dil seçeneğinden English'i seçin.",
    "Sorgulama türü olarak “File” sekmesini işaretleyin.",
    "“First Name” alanına adınızı, pasaportunuzdaki İngilizce yazımıyla girin.",
    "“File Number” alanına vize belgenizdeki dosya numarasını, bölü işareti (/) "
    "kullanmadan yazın.",
    "Kalan alanları tamamlayıp sorgulayın; vizenizin güncel durumu ekranda görünür.",
)

# Dosya numarasi otomatik okunabildiginde musteriye kendi hazir sayfamiz gonderilir:
# numara, ad ve dogum tarihi tek dokunusla kopyalanir, form aranmaz.
GDRFA_HELPER_INTRO = (
    "Dosya numaranızı sizin için hazırladık; aşağıdaki sayfadan tek dokunuşla "
    "kopyalayıp sorgulama ekranına yapıştırabilirsiniz."
)

PROMO = {
    "title": "Aile başvurularında %10 indirim",
    "detail": "Tek formda birden fazla yolcu eklediğinizde aile indirimi otomatik uygulanır; çocuk vizelerinde ayrıca indirimli fiyat geçerlidir.",
}

BANK_TRANSFER = {
    "enabled": True,
    "title": "Havale / EFT ile ödeme",
    "account_name": "Dubai Vize Hattı Turizm ve Danışmanlık A.Ş.",
    "bank_name": "Türkiye İş Bankası A.Ş.",
    "iban": "TR00 0000 0000 0000 0000 0000 00",
    "currency": "TRY",
    "note": "Açıklama kısmına mutlaka başvuru referans kodunuzu yazın. Ödemeniz hesabımıza geçtiğinde başvurunuz işleme alınır ve size e-posta ile bilgi veririz.",
    "notes": [
        'Açıklamaya "Dubai Vizesi" ve başvuru referans kodunuz yazılmalıdır.',
        'TL olarak yapılacak ödemelerde bankanın güncel "USD banka satış kuru" baz alınır.',
    ],
    "banks": [
        {
            "id": "isbank",
            "name": "Türkiye İş Bankası A.Ş.",
            "logo": "/brand/banks/isbank.png",
            "accounts": [
                {"currency": "TRY", "iban": "TR00 0000 0000 0000 0000 0000 00"},
                {"currency": "USD", "iban": "TR00 0000 0000 0000 0000 0000 01"},
            ],
        },
        {
            "id": "garanti",
            "name": "Garanti BBVA",
            "logo": "/brand/banks/garanti.png",
            "accounts": [
                {"currency": "TRY", "iban": "TR00 0000 0000 0000 0000 0000 02"},
                {"currency": "USD", "iban": "TR00 0000 0000 0000 0000 0000 03"},
            ],
        },
        {
            "id": "ziraat",
            "name": "T.C. Ziraat Bankası A.Ş.",
            "logo": "/brand/banks/ziraat.png",
            "accounts": [
                {"currency": "TRY", "iban": "TR00 0000 0000 0000 0000 0000 04"},
                {"currency": "USD", "iban": "TR00 0000 0000 0000 0000 0000 05"},
            ],
        },
    ],
    "steps": [
        "Başvurunuzu tamamlayın ve referans kodunuzu not alın.",
        "Toplam tutarı aşağıdaki hesaba havale/EFT ile gönderin.",
        "Açıklamaya referans kodunuzu yazın.",
        "Dekontu WhatsApp veya e-posta ile iletin; başvurunuz işleme alınsın.",
    ],
}

REFUND_TERMS = {
    "updated_at": "2026-06-09",
    "intro": "Aşağıdaki koşullar, Dubai Vize Hattı üzerinden alınan vize danışmanlığı ile tur, aktivite ve transfer hizmetleri için geçerlidir. Başvurunuzu veya rezervasyonunuzu tamamladığınızda bu koşulları kabul etmiş sayılırsınız.",
    "sections": [
        {
            "title": "Başvuru öncesi iptal",
            "items": [
                "Başvurunuz henüz resmî makamlara iletilmediyse, ödemenizin tamamı 5 iş günü içinde iade edilir.",
                "İptal talebinizi e-posta veya WhatsApp üzerinden referans kodunuzla iletmeniz yeterlidir.",
            ],
        },
        {
            "title": "36 saat garantisi",
            "items": [
                "Belgeleri eksiksiz olan standart başvurular 36 saat içinde sonuçlanır; süre, belgeler onaylanıp başvuru resmî mercilere iletildiği anda başlar.",
                "Süre aşılırsa ödediğiniz ekspres hizmet bedeli iade edilir; ekspres hizmet almadıysanız başvurunuz ücretsiz olarak ekspres sıraya alınır.",
                "Resmî tatiller ile mercilerin ek belge veya inceleme talepleri süreye dahil değildir; iade, talebe gerek olmadan 5 iş günü içinde ödeme yönteminize yapılır.",
            ],
        },
        {
            "title": "Başvuru iletildikten sonra",
            "items": [
                "Başvurunuz BAE makamlarına iletildikten sonra resmî harç iadesi mümkün değildir.",
                "Hizmet bedelimizin iadesi, işlem aşamasına göre değerlendirilir ve tarafınıza yazılı olarak bildirilir.",
            ],
        },
        {
            "title": "Ret (RED) durumu",
            "items": [
                "Vize başvurunuzun reddedilmesi hâlinde resmî makamlara ödenen harç iade edilmez.",
                "Ret gerekçesi ortadan kalktığında (aktif vize, başka sağlayıcıda açık başvuru, geçmiş deport kaydı vb.) yeniden başvuru yapılabilir.",
                "Yeniden başvuruda hizmet bedelimizde indirim uygulanır.",
            ],
        },
        {
            "title": "Eksik veya hatalı bilgi",
            "items": [
                "Yolcu tarafından hatalı iletilen ad, soyad, pasaport numarası gibi bilgilerden doğan retlerde iade yapılmaz.",
                "Bu nedenle başvuru öncesi tüm bilgileri kontrol etmenizi ve pasaportunuzla birebir aynı olmasını sağlamanızı rica ederiz.",
            ],
        },
        {
            "title": "Süre aşımı ve kaçış raporu (Escape Report)",
            "items": [
                "Vize süresi dolduktan sonra ülkede kalmaya devam eden yolcular için BAE makamları günlük ceza uygular.",
                "Kaçak kalış tespit edilirse kaçış raporu (Escape Report) düzenlenir ve doğan tüm masraflar yolcuya faturalandırılır.",
                "Turistik vize başvurusu yapan tüm misafirler bu şartı kabul etmiş sayılır.",
            ],
        },
        {
            "title": "İade süreci",
            "items": [
                "Onaylanan iadeler, ödemenin yapıldığı yönteme (kredi kartı veya banka hesabı) iade edilir.",
                "Kredi kartı iadelerinin hesabınıza yansıması bankanıza bağlı olarak 5-14 gün sürebilir.",
            ],
        },
        {
            "title": "Tur, aktivite ve transfer rezervasyonları",
            "items": [
                "Aktivite, tur ve transfer hizmetleri Dubai'deki yerel operatör firmalar tarafından sağlanır; biz rezervasyonu iletir ve belgenizi (voucher) düzenleriz.",
                "Rezervasyon oluşturulup voucher düzenlendikten sonra hizmet başlamış sayılır ve nakit iade yapılmaz.",
                "Tarihi ve saati belirli etkinlik biletlerinde, katılım saatine 24 saatten az kalan rezervasyonlarda, yolcunun buluşma noktasında hazır olmadığı (no-show) veya geç kaldığı durumlarda ücret iadesi mümkün değildir.",
                "Yolcunun yanlış tarih, yanlış isim veya hatalı kişi sayısı seçmesinden kaynaklanan iptallerde iade yapılmaz; uygunsa operatörden tarih değişikliği talep edilir.",
                "Transferli aktivitelerde araç, belirtilen saatte buluşma noktasında en fazla 5 dakika bekler; trafik, taksi gecikmesi veya adres karışıklığı geçerli mazeret sayılmaz.",
            ],
        },
        {
            "title": "Hava koşulları ve mücbir sebep",
            "items": [
                "Açık havada yapılan aktivitelerde (çöl safarisi, deniz sporları, yat turu vb.) operatör güvenlik gerekçesiyle programı erteleyebilir veya iptal edebilir.",
                "Bu durumda öncelikli çözüm yeni tarih ya da eşdeğer bir alternatif; nakit iade taahhüdümüz bulunmaz.",
                "Doğal afet, salgın, savaş, resmî yasak ve kısıtlamalar, liman/çöl güvenlik kapatmaları ile operatör kaynaklı teknik arızalar mücbir sebep sayılır.",
            ],
        },
        {
            "title": "Ödeme itirazı (chargeback)",
            "items": [
                "Ödeme onayınız, 3D Secure kaydınız, IP bilgisi, onay saatiniz ve gönderilen belgeler işlem kanıtı olarak saklanır.",
                "Hizmet usulüne uygun sunulduğu hâlde yapılan haksız ödeme itirazlarında bu kayıtlar bankaya sunulur ve doğan masraflar talep edilir.",
            ],
        },
    ],
}

SERVICE_TERMS = {
    "updated_at": "2026-06-09",
    "intro": "Bu mesafeli hizmet sözleşmesi, Dubai Vize Hattı (Hizmet Sağlayıcı) ile online başvuru yapan misafir (Alıcı) arasında elektronik ortamda kurulur.",
    "sections": [
        {
            "title": "1. Sözleşmenin konusu",
            "items": [
                "Sözleşmenin konusu, Alıcı'nın Birleşik Arap Emirlikleri giriş vizesi başvurusunun Hizmet Sağlayıcı tarafından hazırlanması, kontrol edilmesi ve yetkili makamlara iletilmesidir.",
                "Hizmet Sağlayıcı bir danışmanlık hizmeti sunar; vizenin onaylanması yetkisi münhasıran BAE makamlarına aittir.",
            ],
        },
        {
            "title": "2. Alıcı'nın yükümlülükleri",
            "items": [
                "Alıcı, başvuru bilgilerinin pasaportuyla birebir aynı ve doğru olduğunu beyan eder.",
                "Alıcı, yüklediği belgelerin kendisine ait, güncel ve gerçek olduğunu kabul eder.",
                "Alıcı, vize süresine uymakla ve süre bitiminden önce ülkeden çıkış yapmakla yükümlüdür.",
            ],
        },
        {
            "title": "3. Hizmet Sağlayıcı'nın yükümlülükleri",
            "items": [
                "Başvuru evraklarını kontrol eder, eksik veya hatalı belgeleri Alıcı'ya bildirir.",
                "Başvuru sonucunu e-posta ve başvuru takip sayfası üzerinden Alıcı ile paylaşır.",
                "Alıcı'nın kişisel verilerini KVKK kapsamında işler ve üçüncü kişilerle yalnızca başvuru amacıyla paylaşır.",
            ],
        },
        {
            "title": "4. Ödeme",
            "items": [
                "Ödemeler kredi/banka kartı ile 3D Secure altyapısı üzerinden veya havale/EFT yoluyla yapılır.",
                "Havale/EFT ödemelerinde başvuru, tutar hesaba geçtikten sonra işleme alınır.",
            ],
        },
        {
            "title": "5. Cayma hakkı ve iade",
            "items": [
                "Başvuru resmî makamlara iletilmeden önce iptal ve iade talebinde bulunulabilir.",
                "Başvurunun iletilmesinden sonra resmî harç iadesi yapılamaz; ayrıntılar İade ve İptal Koşulları sayfasında yer alır.",
            ],
        },
        {
            "title": "6. Süre aşımı",
            "items": [
                "Vize süresini aşan kalışlarda doğacak ceza, kaçış raporu (Escape Report) ve tüm masraflar Alıcı'ya aittir.",
            ],
        },
        {
            "title": "7. Aracılık statüsü ve tur/aktivite hizmetleri",
            "items": [
                "Vize dışındaki tur, aktivite, etkinlik bileti ve transfer hizmetlerinde Hizmet Sağlayıcı aracı konumundadır; hizmeti fiilen Dubai'deki yetkili yerel operatörler yürütür.",
                "Programın uygulanması, araç ve ekipman güvenliği ile saha organizasyonu ilgili operatörün sorumluluğundadır.",
                "Operatör, hava ve güvenlik koşullarına bağlı olarak program akışında değişiklik yapabilir.",
            ],
        },
        {
            "title": "8. Riskli aktivitelerde katılım beyanı",
            "items": [
                "Çöl safarisi, ATV/buggy, jet ski, yamaç paraşütü, su sporları gibi hareketli aktiviteler yapısı gereği risk barındırır; Alıcı bu riskleri bilerek katılır.",
                "Sarsıntı, ıslanma, hafif sıyrık ve benzeri olağan durumlar iade gerekçesi oluşturmaz.",
                "Alıcı, kendisinin ve birlikte katılan yolcuların sağlık durumunun aktiviteye uygun olduğunu beyan eder; hamilelik, kalp, bel ve boyun rahatsızlıklarında katılım kararı ve sonuçları Alıcı'ya aittir.",
            ],
        },
        {
            "title": "9. Transfer ve ulaşım",
            "items": [
                "Havalimanı ve şehir içi transferler anlaşmalı taşıyıcılar tarafından sağlanır.",
                "Alıcı'nın hatalı uçuş bilgisi, yanlış terminal veya eksik iletişim numarası bildirmesinden doğan aksaklıklar Alıcı'nın sorumluluğundadır.",
                "Araçta unutulan eşyalar için sorumluluk taşıyıcı firmaya aittir; bulunması hâlinde teslimi koordine ederiz.",
            ],
        },
        {
            "title": "10. Cayma hakkı istisnası",
            "items": [
                "Mesafeli Sözleşmeler Yönetmeliği uyarınca, belirli tarih ve saatte sunulan eğlence/etkinlik hizmetlerinde ve Alıcı'nın onayıyla ifasına hemen başlanan hizmetlerde cayma hakkı kullanılamaz.",
                "Vize başvurusu resmî sisteme girildiği anda hizmetin ifasına başlanmış kabul edilir.",
            ],
        },
        {
            "title": "11. Sorumluluğun sınırı",
            "items": [
                "Hizmet Sağlayıcı'nın toplam sorumluluğu, her hâlükârda ilgili hizmet için ödenen bedeli aşmaz.",
                "Uçuş kaçırma, otel kaybı, bağlantılı rezervasyon iptali gibi dolaylı zararlar bu sözleşme kapsamı dışındadır.",
            ],
        },
        {
            "title": "12. Kişisel veriler ve ticari ileti",
            "items": [
                "Kişisel veriler 6698 sayılı Kanun kapsamında, Gizlilik Politikası'nda açıklanan amaçlarla işlenir.",
                "Kampanya ve fırsat bildirimleri yalnızca Alıcı'nın ayrıca verdiği onayla gönderilir; onay her zaman geri alınabilir.",
            ],
        },
        {
            "title": "13. Uyuşmazlık",
            "items": [
                "Taraflar arasındaki uyuşmazlıklarda İstanbul Mahkemeleri ve İcra Daireleri yetkilidir.",
                "Alıcı, tüketici sıfatıyla yerleşim yerindeki tüketici hakem heyetlerine de başvurabilir.",
            ],
        },
    ],
}

# Gizlilik Politikasi (veri sorumlusu aydinlatmasi ile birlikte)
PRIVACY_POLICY = {
    "updated_at": "2026-06-09",
    "intro": (
        "Bu politika, Dubai Vize Hattı markası altında hizmet veren "
        f"{COMPANY['legal_name']} tarafından, web sitemizi ziyaret eden ve hizmetlerimizden "
        "yararlanan kişilerin kişisel verilerinin hangi amaçlarla işlendiğini, kimlerle "
        "paylaşıldığını ve haklarınızı nasıl kullanabileceğinizi açıklar."
    ),
    "sections": [
        {
            "title": "1. Amaç ve kapsam",
            "items": [
                "Şirketimiz, 6698 sayılı Kişisel Verilerin Korunması Kanunu kapsamında veri sorumlusudur ve kişisel verileri hukuka uygun, ölçülü ve yalnızca belirtilen amaçlarla işler.",
                "Politika; web sitemizi ziyaret edenler, başvuru sahipleri, yolcular, müşteri temsilcileri, tedarikçiler ve çalışan adaylarını kapsar.",
                "Sitemizden bağlantı verilen üçüncü taraf platformların veri uygulamalarından sorumlu değiliz; ilgili platformların kendi politikalarını incelemenizi öneririz.",
            ],
        },
        {
            "title": "2. Veri sorumlusunun kimliği",
            "items": [
                f"Ticaret unvanı: {COMPANY['legal_name']}",
                f"Adres: {COMPANY['address']}",
                f"E-posta: {COMPANY['email']} · Telefon: {COMPANY['phone']}",
                "Kişisel verilerinize ilişkin tüm talepleriniz için yukarıdaki iletişim kanallarını kullanabilirsiniz.",
            ],
        },
        {
            "title": "3. İşlenen veri kategorileri",
            "items": [
                "Kimlik verileri: ad, soyad, doğum tarihi, uyruk, pasaport bilgileri, vesikalık fotoğraf.",
                "İletişim verileri: cep telefonu, e-posta adresi, şehir bilgisi.",
                "Başvuru ve işlem verileri: seyahat tarihleri, vize türü, yüklenen belgeler, başvuru durumu, yazışma kayıtları.",
                "Finansal veriler: ödeme yöntemi, işlem tutarı ve referansı (kart bilgileri tarafımızda saklanmaz, ödeme kuruluşunda tutulur).",
                "Teknik veriler: IP adresi, tarayıcı ve cihaz bilgisi, çerez kayıtları, oturum ve giriş kodu kayıtları.",
            ],
        },
        {
            "title": "4. İşleme amaçları ve hukuki sebepler",
            "items": [
                "Vize başvurusunun hazırlanması, kontrolü ve yetkili makamlara iletilmesi — sözleşmenin kurulması ve ifası.",
                "Sigorta, eSIM, tur ve transfer gibi ek hizmetlerin sağlanması — sözleşmenin ifası.",
                "Fatura, muhasebe ve saklama yükümlülükleri — kanunlarda öngörülen yükümlülüğün yerine getirilmesi.",
                "Hesabınıza tek kullanımlık kod ile güvenli giriş, kötüye kullanım ve dolandırıcılık önleme — meşru menfaat.",
                "Kampanya, fırsat ve tanıtım bildirimleri ile reklam eşleştirmesi — yalnızca açık rızanız.",
            ],
        },
        {
            "title": "5. Kişisel verilerin aktarılması",
            "items": [
                "Vize başvurusunun sonuçlanabilmesi için Birleşik Arap Emirlikleri göçmenlik makamları ve yetkili yerel acente/işlem ortaklarına aktarım yapılır.",
                "Ek hizmetlerde ilgili sigorta şirketi, eSIM sağlayıcısı, tur veya transfer operatörüne yalnızca hizmetin gerektirdiği veriler iletilir.",
                "Ödeme kuruluşları, bankalar, e-posta ve bulut altyapı sağlayıcıları, muhasebe ve hukuk danışmanları ile mevzuat gereği yetkili kamu kurumlarına aktarım yapılabilir.",
                "Her aktarımda gizlilik taahhüdü, veri işleme sözleşmesi ve uygun teknik tedbirler aranır.",
            ],
        },
        {
            "title": "6. Yurt dışına aktarım",
            "items": [
                "Vize işlemlerinin doğası gereği başvuru verileri Birleşik Arap Emirlikleri'ndeki yetkili makam ve işlem ortaklarına aktarılır.",
                "E-posta gönderimi, bulut depolama, mesajlaşma ve yapay zekâ destekli belge kontrolü gibi hizmetlerde yurt dışında yerleşik sağlayıcılardan yararlanılır.",
                "Bu aktarımlar Kanun'un 9. maddesindeki şartlara uygun olarak, gerekli taahhüt ve sözleşmeler kurularak gerçekleştirilir.",
            ],
        },
        {
            "title": "7. Saklama süresi",
            "items": [
                "Başvuru ve işlem kayıtları, mali mevzuat ve olası uyuşmazlık süreleri dikkate alınarak 10 yıl boyunca saklanır.",
                "Pasaport ve fotoğraf gibi belgeler başvuru tamamlandıktan sonra yalnızca yasal saklama süresi kadar tutulur, süre sonunda silinir veya anonim hâle getirilir.",
                "Pazarlama izniniz, geri almanıza kadar; geri aldığınızda izin kaydı ispat amacıyla sınırlı süre saklanır.",
            ],
        },
        {
            "title": "8. Veri güvenliği",
            "items": [
                "Aktarım güvenliği için TLS/SSL şifreleme, erişim yetkilendirmesi ve kayıt tutma uygulanır.",
                "Yönetim paneline erişim tek kullanımlık kod ile yapılır; parola saklanmaz.",
                "Belgeler erişimi sınırlı depolama alanında tutulur, personel gizlilik taahhüdü ile çalışır.",
            ],
        },
        {
            "title": "9. Haklarınız",
            "items": [
                "Kişisel verinizin işlenip işlenmediğini öğrenme, işlenmişse buna ilişkin bilgi talep etme.",
                "İşleme amacını ve verilerin amaca uygun kullanılıp kullanılmadığını öğrenme; yurt içinde/yurt dışında aktarıldığı üçüncü kişileri bilme.",
                "Eksik veya yanlış işlenen verilerin düzeltilmesini, koşulları oluştuğunda silinmesini veya yok edilmesini isteme ve bu işlemlerin aktarım yapılan taraflara bildirilmesini talep etme.",
                "Otomatik sistemlerle yapılan analiz sonucu aleyhinize çıkan sonuca itiraz etme ve hukuka aykırı işleme nedeniyle doğan zararın giderilmesini isteme.",
                "Talepleriniz, kimliğinizi doğrulayan bilgilerle e-posta veya yazılı başvuru yoluyla iletildiğinde en geç 30 gün içinde yanıtlanır.",
            ],
        },
        {
            "title": "10. Çerezler ve güncelleme",
            "items": [
                "Sitemizde oturumun sürdürülmesi, tercihlerin hatırlanması ve trafik ölçümü için çerez kullanılır; tarayıcı ayarlarınızdan yönetebilirsiniz.",
                "Bu politika, hizmetlerimiz veya mevzuat değiştiğinde güncellenir; yürürlük tarihi sayfanın başında belirtilir.",
            ],
        },
    ],
}

# Ticari elektronik ileti (izinli pazarlama) onam metni
MARKETING_CONSENT = {
    "updated_at": "2026-06-09",
    "intro": (
        "Kampanya, indirim ve seyahat fırsatlarımızı size iletebilmemiz için verdiğiniz "
        "onayın kapsamı aşağıda açıklanmıştır. Onay vermek tamamen isteğinize bağlıdır; "
        "başvurunuz onay vermeseniz de aynı şekilde tamamlanır."
    ),
    "sections": [
        {
            "title": "1. Onayın kapsamı",
            "items": [
                f"Onay verdiğinizde {COMPANY['legal_name']} tarafından tarafınıza kampanya, indirim, yeni hizmet ve seyahat fırsatlarına ilişkin bilgilendirmeler gönderilebilir.",
                "İletiler; e-posta, SMS, WhatsApp, telefon ve site üzerinden bildirim kanallarıyla gönderilebilir.",
                "Vize başvurunuzla ilgili durum bildirimleri, ödeme ve belge yazışmaları ticari ileti değildir; bunlar hizmetin ifası için onaydan bağımsız olarak gönderilir.",
            ],
        },
        {
            "title": "2. İşlenen bilgiler",
            "items": [
                "Adınız, e-posta adresiniz, cep telefonu numaranız ve hangi hizmetlerle ilgilendiğinize dair tercih bilgileriniz.",
                "İzin kaydınızın tarihi, saati, kanalı ve IP adresi; mevzuat gereği ispat amacıyla saklanır.",
            ],
        },
        {
            "title": "3. Reklam eşleştirmesi (ayrı onay)",
            "items": [
                "Ayrıca onay verirseniz, size uygun içerikleri sosyal medya ve arama ağlarında gösterebilmek için iletişim bilgileriniz şifrelenmiş (hash) biçimde reklam platformlarına iletilir.",
                "Bu yöntemle bilgileriniz açık hâlde paylaşılmaz, satılmaz ve yalnızca hedef kitle eşleştirmesi ile ölçümleme için kullanılır.",
                "Onay vermemeniz hizmet alımınızı hiçbir şekilde etkilemez.",
            ],
        },
        {
            "title": "4. Onayı geri almak",
            "items": [
                "Her e-postanın altındaki bağlantıdan, SMS'e RED yanıtı vererek veya bize yazarak onayınızı dilediğiniz zaman geri alabilirsiniz.",
                "Onay geri alındığında pazarlama iletileri durdurulur; talebiniz en kısa sürede, en geç üç iş günü içinde uygulanır.",
                f"Talepleriniz için: {COMPANY['email']}",
            ],
        },
        {
            "title": "5. Mevzuat",
            "items": [
                "Bu onam metni 6563 sayılı Elektronik Ticaretin Düzenlenmesi Hakkında Kanun, Ticari İletişim ve Ticari Elektronik İletiler Hakkında Yönetmelik ile 6698 sayılı Kişisel Verilerin Korunması Kanunu hükümleri dikkate alınarak hazırlanmıştır.",
                "Onay kayıtları İleti Yönetim Sistemi (İYS) mevzuatına uygun şekilde yönetilir.",
            ],
        },
    ],
}
