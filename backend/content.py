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
        "price": 1999.0,
        "currency": "TRY",
        "processing_days": "ortalama 3 iş günü",
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
        "price": 3999.0,
        "currency": "TRY",
        "processing_days": "ortalama 3 iş günü",
        "popular": False,
        "order": 2,
        "description": "Dubai seyahatiniz 1-60 gün arasıysa ve tek seferlik gidiş-dönüş yapacaksanız bu vize uygundur.",
        "features": [
            "60 gün kalış hakkı",
            "Tek giriş",
            "Online başvuru",
            "Uzman danışman desteği",
            "Öncelikli başvuru takibi",
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
        "price": 3499.0,
        "currency": "TRY",
        "processing_days": "3-5 iş günü",
        "popular": True,
        "order": 3,
        "description": "30 gün içinde Umman, Katar gibi ülkelere geçip Dubai'ye tekrar döneceklerin tercihi.",
        "features": [
            "30 gün kalış hakkı",
            "Sınırsız giriş-çıkış",
            "Online başvuru",
            "Uzman danışman desteği",
            "Öncelikli başvuru takibi",
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
        "price": 5499.0,
        "currency": "TRY",
        "processing_days": "3-5 iş günü",
        "popular": False,
        "order": 4,
        "description": "Sık seyahat eden iş insanları için en kapsamlı seçenek.",
        "features": [
            "60 gün kalış hakkı",
            "Sınırsız giriş-çıkış",
            "Online başvuru",
            "Özel danışman ataması",
            "Öncelikli başvuru takibi",
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
        "price": 999.0,
        "currency": "TRY",
        "processing_days": "ortalama 3 iş günü",
        "popular": True,
        "order": 5,
        "description": "18 yaş altı çocukların aileleriyle birlikte 1-30 gün tek girişli seyahati için indirimli vize.",
        "features": [
            "18 yaş altı için indirimli",
            "30 gün kalış hakkı",
            "Ebeveyn başvurusuyla birlikte",
            "Online başvuru",
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
        "price": 1899.0,
        "currency": "TRY",
        "processing_days": "3-5 iş günü",
        "popular": False,
        "order": 6,
        "description": "18 yaş altı çocukların aileleriyle birlikte 1-60 gün tek girişli seyahati için indirimli vize.",
        "features": [
            "18 yaş altı için indirimli",
            "60 gün kalış hakkı",
            "Ebeveyn başvurusuyla birlikte",
            "Online başvuru",
        ],
    },
    {
        "id": "visa_extension_30",
        "slug": "30-gun-vize-uzatma",
        "name": "30 Günlük Vize Uzatma",
        "short_name": "Vize Uzatma",
        "category": "other",
        "duration_days": 30,
        "entry_type": "single",
        "entry_label": "Uzatma",
        "applicant_type": "adult",
        "price": 5299.0,
        "currency": "TRY",
        "processing_days": "2-4 iş günü",
        "popular": False,
        "order": 7,
        "description": "Dubai'deyken ülkeden çıkış yapmadan kalış sürenizi 30 gün uzatın. Uzatma en fazla 2 kez yapılabilir.",
        "features": [
            "Ülkeden çıkmadan 30 gün ek süre",
            "En fazla 2 kez uygulanabilir",
            "Online başvuru",
            "Uzman danışman desteği",
        ],
    },
]

VISA_CATEGORIES = [
    {"id": "single", "label": "Tek Girişli"},
    {"id": "multiple", "label": "Çok Girişli"},
    {"id": "child", "label": "Çocuk Vizesi"},
    {"id": "other", "label": "Diğer Hizmetler"},
]

# Optional paid add-ons, priced per traveller
ADDONS = {
    "express": {
        "id": "express",
        "name": "Ekspres Vize Hizmeti",
        "price": 649.0,
        "currency": "TRY",
        "per_person": True,
        "description": "Acil seyahatler için öncelikli işlem. Başvurunuz sıraya girmeden işleme alınır, sonuç genellikle 24 saat içinde çıkar.",
        "features": ["24 saat içinde sonuç", "Öncelikli işlem sırası", "Anlık bilgilendirme"],
    },
    "insurance": {
        "id": "insurance",
        "name": "Seyahat Sağlık Sigortası",
        "price": 349.0,
        "currency": "TRY",
        "per_person": True,
        "description": "BAE'de sağlık masrafları yüksektir. Seyahat sürenizi kapsayan sağlık sigortasını başvurunuza ekleyin.",
        "features": ["Seyahat süresi boyunca geçerli", "Acil sağlık masrafları", "Dijital poliçe"],
    },
}

# (minimum traveller count, discount rate on visa subtotal)
FAMILY_DISCOUNT_TIERS = [(5, 0.08), (3, 0.05)]

FAMILY_DISCOUNT_TEXT = "3 ve 4 kişilik başvurularda %5, 5 kişi ve üzerinde %8 aile indirimi otomatik uygulanır."

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
        "detail": "Dubai'den dönüş uçuşunuzun ad-soyad içeren rezervasyon belgesi. Henüz bilet almadıysanız tahmini tarihleri yazmanız yeterlidir.",
        "required": False,
    },
    {
        "key": "hotel",
        "title": "Otel Rezervasyonu",
        "detail": "Seyahat sürenizi kapsayacak şekilde otel, Airbnb veya konaklama rezervasyon belgesi.",
        "required": False,
    },
    {
        "key": "other",
        "title": "Diğer Evraklar",
        "detail": "Danışmanınızın talep ettiği ek belgeler (veli izin belgesi, davetiye, banka hesap dökümü vb.).",
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
    {"title": "Hızlı sonuç", "detail": "Standart başvurular ortalama 3 iş günü, ekspres başvurular 24 saat içinde sonuçlanır."},
    {"title": "Gerçek insan desteği", "detail": "WhatsApp ve telefonla ulaşabileceğiniz Türkçe danışman ekibi."},
]

SERVICES = [
    {"key": "visa", "title": "Dubai Vizesi", "detail": "Vize başvurunuzu eksiksiz ve hatasız tamamlamanız için baştan sona uzman desteği."},
    {"key": "tour", "title": "Kişiye Özel Tur Paketleri", "detail": "Kusursuz bir Dubai tatili için tüm programınızı siz gitmeden adım adım planlıyoruz."},
    {"key": "hotel", "title": "Otel Rezervasyonu", "detail": "Anlaşmalı olduğumuz prestijli Dubai otellerinde avantajlı konaklama seçenekleri."},
    {"key": "transfer", "title": "Havalimanı Transferi", "detail": "Özel araç ve Türkçe konuşan ekibimizle Dubai'ye indiğiniz andan itibaren yanınızdayız."},
    {"key": "citytour", "title": "Şehir Turları", "detail": "Size özel planlanan rehberli şehir turlarıyla Dubai'yi doğru başlıklarla keşfedin."},
    {"key": "activity", "title": "Aktiviteler", "detail": "Çöl safariden su sporlarına, helikopter turlarından ikonik yapı biletlerine kadar geniş seçenek."},
]

TOURS = [
    {"key": "helicopter", "title": "Helikopter Turları", "detail": "Dubai silüetini bulutların üzerinden izleyerek ayrıcalıklı bir başlangıç yapın."},
    {"key": "safari", "title": "Çöl Safari Turları", "detail": "Kızıl kumlarda hız ve maceranın birleştiği gerçek bir çöl deneyimi."},
    {"key": "yacht", "title": "Yat Turları", "detail": "Şehir manzarası eşliğinde özel bir yatın konforunda lüks bir dokunuş."},
    {"key": "jetski", "title": "Jetski Turları", "detail": "Denizin üzerinde özgürce hızlanabileceğiniz enerjik bir serüven."},
    {"key": "tickets", "title": "İkonik Yapı Biletleri", "detail": "Şehrin en ünlü noktalarına hızlı ve zahmetsiz giriş."},
    {"key": "city", "title": "Şehir Turları", "detail": "Türkçe rehber ve özel araçlarla şehri bizim deneyimimizle tanıyın."},
]

PARTNERS = [
    "Emirates", "flydubai", "Turkish Airlines", "Pegasus", "Atlasjet Global", "SunExpress",
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
        "text": "Uçuşuma 2 gün kalmıştı, ekspres hizmeti aldım. Vizem 20 saat içinde elimdeydi. Gece yarısı yazdığım mesaja bile dönüş yaptılar.",
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
    "total_applications": 4500,
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
        "q": "Ailemle birlikte tek başvuru yapabilir miyim?",
        "a": "Evet. Başvuru formunda 'Yolcu ekle' butonuyla eşinizi ve çocuklarınızı aynı başvuruya ekleyebilirsiniz. 18 yaş altı yolcular için indirimli çocuk vizesi, 3 kişi ve üzeri başvurularda ise aile indirimi otomatik uygulanır.",
    },
    {
        "q": "Vize işlemi ne kadar sürüyor?",
        "a": "Belgeleriniz eksiksiz olduğunda standart başvurular ortalama 3 iş günü içinde sonuçlanır. Ekspres vize hizmetiyle sonuç genellikle 24 saat içinde çıkar.",
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
        "q": "Başvurumu nasıl takip ederim?",
        "a": "Başvurunuz oluştuğunda size bir takip kodu veriyoruz. 'Başvuru Takip' sayfasından takip kodunuz ve soyadınızla durumu anında görebilir, onaylanan vizenizi indirebilirsiniz.",
    },
]

ARTICLES = [
    {
        "slug": "dubai-vizesi-hangi-emirliklerde-gecerli",
        "title": "Dubai Vizesi Abu Dabi ve Şarja'da Geçerli mi?",
        "date": "2026-08-25",
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
    "Vize onay süreçleri tamamen Birleşik Arap Emirlikleri Göçmenlik Ofisi tarafından yürütülür. Ek evrak talebi gibi durumlarda başvuru süresi değişkenlik gösterebilir.",
    "Seyahat amacınız oturum, çalışma veya eğitim ise turistik/ticari vize ile ülkeye giriş yapıp oturum işlemi başlatamazsınız. Bu girişim vizenin iptaline ve sınır dışı işlemine yol açar.",
    "Lütfen başvuracağınız vize türünü seyahat amacınıza uygun seçtiğinizden emin olun.",
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


def family_discount_rate(traveler_count: int) -> float:
    for minimum, rate in FAMILY_DISCOUNT_TIERS:
        if traveler_count >= minimum:
            return rate
    return 0.0


def compute_pricing(visa_prices, addons: dict, currency: str = "TRY") -> dict:
    """Server-side authoritative pricing. visa_prices = list of float per traveller."""
    count = len(visa_prices)
    subtotal = round(sum(float(p) for p in visa_prices), 2)
    rate = family_discount_rate(count)
    discount = round(subtotal * rate, 2)
    addon_lines = []
    addons_total = 0.0
    for key, meta in ADDONS.items():
        if addons.get(key):
            line_total = round(meta["price"] * (count if meta["per_person"] else 1), 2)
            addon_lines.append(
                {
                    "id": key,
                    "name": meta["name"],
                    "unit_price": meta["price"],
                    "quantity": count if meta["per_person"] else 1,
                    "total": line_total,
                }
            )
            addons_total += line_total
    addons_total = round(addons_total, 2)
    total = round(subtotal - discount + addons_total, 2)
    return {
        "traveler_count": count,
        "subtotal": subtotal,
        "family_discount_rate": rate,
        "family_discount": discount,
        "addons": addon_lines,
        "addons_total": addons_total,
        "total": total,
        "currency": currency,
    }
