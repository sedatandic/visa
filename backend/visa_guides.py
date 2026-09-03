"""SEO odakli vize rehberi icerikleri.

Her vize tipi icin arama motorlarindan organik trafik cekmeyi hedefleyen,
Turkce, uzun-form rehber icerigi. Icerikler `visa_types` koleksiyonundaki
`guide` alani ile admin panelinden ezilebilir (override).
"""

from content import PHOTO_RULES, PROCESS_STEPS, REQUIRED_DOCUMENTS, VISA_TYPES

BASE_PATH = "/dubai-vizesi"

# Tum rehberlerde tekrar eden ortak SSS'ler
COMMON_FAQ = [
    {
        "q": "Dubai vizesi başvurusu için pasaportumun ne kadar geçerli olması gerekir?",
        "a": "Pasaportunuzun Dubai'den dönüş tarihinizden itibaren en az 6 ay geçerli olması gerekir. Süresi kısa olan pasaportlarla yapılan başvurular reddedilebilir; bu nedenle başvurudan önce pasaport geçerlilik tarihinizi mutlaka kontrol edin.",
    },
    {
        "q": "Vize başvurumu ne kadar önce yapmalıyım?",
        "a": "Standart başvurularda sonuç ortalama 2 iş gününde çıktığı için seyahatinizden en az 7-10 gün önce başvurmanızı öneririz. Uçuşa 48 saatten az kaldıysa ekspres hizmet ile başvurunuzu önceliklendirebiliriz.",
    },
    {
        "q": "Ödemeyi nasıl yapabilirim?",
        "a": "Kredi/banka kartı ile güvenli ödeme altyapısı üzerinden ya da havale/EFT ile ödeyebilirsiniz. Havale seçeneğinde banka bilgileri ve açıklamaya yazacağınız referans numarası başvuru sonunda ekranda ve e-postanızda yer alır.",
    },
    {
        "q": "Başvurum reddedilirse ücret iade edilir mi?",
        "a": "Resmî başvuru harcı yetkili merciler tarafından tahsil edildiğinden red durumunda harç iadesi yapılmaz. Hizmet bedelimize ilişkin koşulları İade ve İptal Koşulları sayfamızda ayrıntılı olarak bulabilirsiniz.",
    },
]

GUIDES = {
    "30-gun-tek-giris": {
        "h1": "30 Günlük Tek Girişli Dubai Vizesi",
        "seo_title": "30 Günlük Dubai Vizesi 2026 | Fiyat, Şartlar ve Online Başvuru",
        "seo_description": "30 günlük tek girişli Dubai vizesi nasıl alınır? 2026 fiyatı, gerekli belgeler, başvuru süresi ve onay şartları. Tek formda aile başvurusu, ortalama 2 iş gününde sonuç.",
        "keywords": ["30 günlük dubai vizesi", "dubai vizesi fiyat", "dubai turistik vize", "dubai vize başvurusu"],
        "intro": [
            "30 günlük tek girişli Dubai vizesi, Birleşik Arap Emirlikleri'ne turistik ya da kısa iş amaçlı seyahat edenlerin en çok tercih ettiği vize tipidir. Vize, ülkeye ilk giriş yaptığınız günden itibaren 30 gün kalış hakkı verir ve tek giriş için geçerlidir; ülkeden çıktığınızda vizeniz kullanılmış sayılır.",
            "Türkiye pasaportu sahipleri için Dubai vizesi süreci tamamen dijitaldir: konsolosluğa gitmenize, randevu almanıza veya parmak izi vermenize gerek yoktur. Pasaportunuzun kimlik sayfası ile vesikalık fotoğrafınızı yüklemeniz, başvurunuzu tamamlamanız için yeterlidir.",
            "Başvurunuzu bizim üzerinden yaptığınızda evraklarınız gönderim öncesi kontrol edilir, eksik veya hatalı belge nedeniyle oluşabilecek red riski en aza indirilir. Onaylanan vizeniz PDF olarak e-postanıza ve başvuru takip sayfanıza yüklenir.",
        ],
        "who_for": [
            "Dubai, Abu Dhabi veya diğer emirliklere 1-30 gün arası tatil planlayanlar",
            "Kısa süreli fuar, toplantı ve iş görüşmesi için gidecek profesyoneller",
            "Aynı seyahatte tek gidiş-dönüş yapacak, ülke dışına çıkıp tekrar girmeyecek yolcular",
            "Eşi ve çocuklarıyla tek formda aile başvurusu yapmak isteyenler",
        ],
        "highlights": [
            "Ülkeye girişten itibaren 30 gün kesintisiz kalış hakkı",
            "Konsolosluk randevusu ve pasaport teslimi gerekmez",
            "Aile başvurusunda %10 indirim, çocuk vizelerinde ayrıca indirimli fiyat",
            "Ekspres hizmet ile genellikle 24 saat içinde sonuç",
        ],
        "tips": [
            "Vize süresi ülkeye giriş tarihinizden itibaren işler; vizenin kullanım penceresini danışmanınıza teyit ettirin.",
            "30 günü aşan planlarınız varsa doğrudan 60 günlük vizeye başvurmak, sonradan uzatma yapmaktan daha ekonomiktir.",
            "Pasaportunuzun fotoğrafını çekerken parlama ve gölge olmamasına dikkat edin; okunmayan bilgiler işlemi geciktirir.",
        ],
        "faqs": [
            {
                "q": "30 günlük Dubai vizesi ile ülkeden çıkıp tekrar girebilir miyim?",
                "a": "Hayır. Bu vize tek girişlidir; Birleşik Arap Emirlikleri'nden çıktığınızda vizeniz geçerliliğini yitirir. Umman, Katar gibi komşu ülkelere geçip Dubai'ye dönmeyi planlıyorsanız çok girişli vize seçmelisiniz.",
            },
            {
                "q": "30 günlük Dubai vizesi kaç günde çıkar?",
                "a": "Standart başvurularda sonuç ortalama 2 iş günü içinde çıkar. Yoğun dönemlerde bu süre 5 iş gününe kadar uzayabilir; acil seyahatlerde ekspres hizmetle genellikle 24 saat içinde sonuç alınır.",
            },
            {
                "q": "Vize süresini Dubai'de uzatabilir miyim?",
                "a": "Evet. Ülkeden çıkış yapmadan 30 gün ek süre alabileceğiniz vize uzatma hizmeti bulunmaktadır ve uzatma en fazla iki kez yapılabilir. Uzatma başvurusunu vizenizin son gününden önce başlatmanız gerekir.",
            },
            {
                "q": "Otel ve uçak bileti rezervasyonu zorunlu mu?",
                "a": "Zorunlu değildir, ancak dönüş bileti ve konaklama belgesi başvurunuzu güçlendirir. Henüz rezervasyon yapmadıysanız tahmini tarihleri yazmanız yeterlidir.",
            },
        ],
    },
    "60-gun-tek-giris": {
        "h1": "60 Günlük Tek Girişli Dubai Vizesi",
        "seo_title": "60 Günlük Dubai Vizesi | Uzun Süreli Kalış İçin Fiyat ve Şartlar",
        "seo_description": "60 günlük tek girişli Dubai vizesi ile iki aya kadar kalın. 2026 fiyatı, gerekli belgeler, başvuru süresi ve 30 günlük vize ile karşılaştırma.",
        "keywords": ["60 günlük dubai vizesi", "dubai uzun süreli vize", "dubai 2 aylık vize"],
        "intro": [
            "60 günlük tek girişli Dubai vizesi, Birleşik Arap Emirlikleri'nde iki aya kadar kalmak isteyen yolcular için tasarlanmıştır. Uzun tatil planlayanlar, kış aylarını sıcak iklimde geçirmek isteyenler ve uzun soluklu iş projeleri için gidecek profesyoneller bu vizeyi tercih eder.",
            "Vize tek giriş hakkı verir; ülkeden çıkış yaptığınızda vize kullanılmış sayılır. Kalış süreniz ülkeye ilk giriş yaptığınız günden itibaren sayılmaya başlar.",
            "30 günlük vizeyi alıp sonradan uzatmak yerine doğrudan 60 günlük vize almak, hem maliyet hem de süreç yönetimi açısından çoğu durumda daha avantajlıdır.",
        ],
        "who_for": [
            "Dubai'de 30 günden uzun, 60 güne kadar kalacak yolcular",
            "Uzun süreli proje, eğitim veya iş görüşmeleri için gidecek profesyoneller",
            "Kış aylarını Körfez bölgesinde geçirmek isteyen emekli ve serbest çalışanlar",
            "Aile ziyareti nedeniyle uzun süre kalacak misafirler",
        ],
        "highlights": [
            "Girişten itibaren 60 gün kalış hakkı",
            "Uzatma ihtiyacını büyük ölçüde ortadan kaldırır",
            "Öncelikli başvuru takibi ve evrak kontrolü",
            "Tek formda aile başvurusu ve otomatik indirim",
        ],
        "tips": [
            "60 günlük vizede de kalış süresi aşımı günlük para cezasına tabidir; dönüş tarihinizi vize bitiminden önce planlayın.",
            "İki ayı aşan planlar için freelancer/oturum vizesi seçenekleri daha uygun olabilir.",
            "Uzun kalışlarda seyahat sağlık sigortası eklemenizi öneririz; BAE'de sağlık masrafları yüksektir.",
        ],
        "faqs": [
            {
                "q": "60 günlük Dubai vizesi ile 30 günlük vize arasındaki fark nedir?",
                "a": "Tek fark kalış süresidir. Her ikisi de tek girişlidir ve aynı belgelerle başvurulur. 60 günlük vize, iki aya kadar kesintisiz kalış imkânı sunar.",
            },
            {
                "q": "60 günlük vizeyi de uzatabilir miyim?",
                "a": "Uzatma imkânı vize tipine ve başvuru anındaki resmî uygulamaya bağlıdır. Uzun kalış planlarınızı başvuru öncesinde danışmanınıza bildirin; en uygun seçeneği birlikte belirleyelim.",
            },
            {
                "q": "60 günlük vize başvurusunda ek belge isteniyor mu?",
                "a": "Standart olarak pasaport ve vesikalık fotoğraf yeterlidir. Bazı durumlarda konaklama belgesi veya banka hesap dökümü talep edilebilir; bu durumda danışmanınız sizi bilgilendirir.",
            },
        ],
    },
    "30-gun-cok-giris": {
        "h1": "30 Günlük Çok Girişli Dubai Vizesi",
        "seo_title": "30 Günlük Çok Girişli Dubai Vizesi | Multiple Vize Fiyat ve Şartlar",
        "seo_description": "30 günlük çok girişli (multiple) Dubai vizesi ile ülkeye birden fazla kez giriş yapın. Fiyat, gerekli belgeler, kimler için uygun ve online başvuru.",
        "keywords": ["çok girişli dubai vizesi", "multiple dubai vize", "dubai multi vize"],
        "intro": [
            "30 günlük çok girişli Dubai vizesi, geçerlilik süresi boyunca Birleşik Arap Emirlikleri'ne birden fazla kez giriş yapmanıza imkân tanır. Bölgedeki komşu ülkelere geçip Dubai'ye dönmeyi planlayan iş insanları ve çoklu güzergâh planlayan gezginler için idealdir.",
            "Tek girişli vizede ülkeden çıktığınızda vize kullanılmış sayılırken, çok girişli vizede geçerlilik süresi içinde çıkış-giriş yapmaya devam edebilirsiniz. Bu esneklik, sık seyahat edenler için önemli bir zaman ve maliyet avantajı sağlar.",
        ],
        "who_for": [
            "Umman, Katar, Suudi Arabistan gibi komşu ülkelerle Dubai arasında gidiş-dönüş yapacaklar",
            "Bölgede birden fazla toplantı ve fuar programı olan iş insanları",
            "Dubai'yi transfer üssü olarak kullanan çoklu güzergâhlı gezginler",
            "Kısa aralıklarla iki kez Dubai'ye gitmesi gereken yolcular",
        ],
        "highlights": [
            "Geçerlilik süresi içinde birden fazla giriş hakkı",
            "Her seyahat için yeni vize başvurusu yapma zorunluluğu yok",
            "İş seyahatlerinde esnek planlama imkânı",
            "Evrak kontrolü ve öncelikli takip dahil",
        ],
        "tips": [
            "Çok girişli vizede her girişte tanınan kalış süresi ile vizenin toplam geçerlilik süresi farklıdır; ikisini de danışmanınıza teyit ettirin.",
            "Komşu ülke geçişlerinde o ülkenin vize kurallarını da kontrol etmeyi unutmayın.",
        ],
        "faqs": [
            {
                "q": "Çok girişli Dubai vizesi ile kaç kez giriş yapabilirim?",
                "a": "Vizenin geçerlilik süresi içinde, her girişte tanınan kalış süresini aşmamak kaydıyla birden fazla kez giriş yapabilirsiniz.",
            },
            {
                "q": "Çok girişli vize neden daha pahalı?",
                "a": "Resmî başvuru harcı çok girişli vizelerde daha yüksektir. Buna karşılık her seyahat için yeni vize almanız gerekmediğinden, iki veya daha fazla giriş planınız varsa toplam maliyet genellikle daha avantajlı olur.",
            },
            {
                "q": "Tek girişli vizem varken çok girişliye geçebilir miyim?",
                "a": "Mevcut vizenin türü sonradan değiştirilemez. Yeni bir çok girişli vize başvurusu yapılması gerekir; bu konuda danışmanlarımız yol gösterir.",
            },
        ],
    },
    "60-gun-cok-giris": {
        "h1": "60 Günlük Çok Girişli Dubai Vizesi",
        "seo_title": "60 Günlük Çok Girişli Dubai Vizesi | En Esnek Vize Seçeneği",
        "seo_description": "60 günlük çok girişli Dubai vizesi: iki aya kadar kalış ve birden fazla giriş hakkı. Fiyat, şartlar, gerekli belgeler ve hızlı online başvuru.",
        "keywords": ["60 günlük çok girişli dubai vizesi", "dubai multiple vize 60 gün"],
        "intro": [
            "60 günlük çok girişli Dubai vizesi, hem uzun kalış hem de çoklu giriş esnekliği arayan yolcular için en kapsamlı turistik vize seçeneğidir. Bölgeye düzenli seyahat eden iş insanları ve uzun soluklu programlar planlayan gezginler için tasarlanmıştır.",
            "Vize, geçerlilik süresi boyunca ülkeye birden fazla kez giriş yapmanıza olanak tanır ve her girişte tanınan kalış süresi boyunca kalabilirsiniz. Böylece Körfez bölgesindeki farklı ülkeleri kapsayan güzergâhları rahatça planlayabilirsiniz.",
        ],
        "who_for": [
            "Bölgede iki ay boyunca yoğun program yürütecek profesyoneller",
            "Dubai merkezli çalışıp komşu ülkelere düzenli geçiş yapanlar",
            "Uzun tatilini birkaç ülkeye bölerek planlayan gezginler",
        ],
        "highlights": [
            "60 gün kalış + çoklu giriş esnekliği",
            "En kapsamlı turistik vize seçeneği",
            "Öncelikli başvuru takibi",
            "Aile başvurusunda otomatik indirim",
        ],
        "tips": [
            "Bu vize tipinde başvuru öncesi evrak kontrolü daha da önemlidir; eksik belge süreci uzatır.",
            "Sık giriş-çıkış yapacaksanız pasaportunuzda yeterli boş sayfa bulunduğundan emin olun.",
        ],
        "faqs": [
            {
                "q": "60 günlük çok girişli vize kimler için mantıklı?",
                "a": "İki ay içinde Birleşik Arap Emirlikleri'ne en az iki kez giriş yapacak olanlar için hem zaman hem maliyet açısından en avantajlı seçenektir.",
            },
            {
                "q": "Her girişte 60 gün kalabilir miyim?",
                "a": "Hayır. 60 gün, vizenin sağladığı toplam kalış hakkıdır. Her girişte tanınan süre resmî uygulamaya bağlıdır; başvuru öncesinde danışmanınız net bilgi verir.",
            },
        ],
    },
    "30-gun-cocuk-vizesi": {
        "h1": "30 Günlük Çocuk Vizesi (Dubai)",
        "seo_title": "Dubai Çocuk Vizesi 30 Gün | 18 Yaş Altı İndirimli Vize Başvurusu",
        "seo_description": "18 yaş altı çocuklar için 30 günlük indirimli Dubai vizesi. Gerekli belgeler, veli izni, aile başvurusu indirimi ve online başvuru adımları.",
        "keywords": ["dubai çocuk vizesi", "18 yaş altı dubai vizesi", "bebek dubai vizesi"],
        "intro": [
            "Dubai çocuk vizesi, 18 yaşından küçük yolcuların aileleriyle birlikte Birleşik Arap Emirlikleri'ne seyahat etmesi için düzenlenen indirimli vize tipidir. Bebekler dahil her yaştaki çocuk için ayrı vize alınması zorunludur; çocuklar ebeveyn vizesine dahil edilemez.",
            "Başvuruyu ebeveyn başvurusuyla birlikte tek formda yapabilirsiniz. Bu sayede aile indirimi ve çocuk vizesine özel indirimli fiyat otomatik olarak hesaplanır, tüm ailenin evrakları aynı dosyada birlikte kontrol edilir.",
            "Çocuğun pasaportunun kendi adına düzenlenmiş olması gerekir. Ebeveynlerden biri seyahate katılmıyorsa noter onaylı veli izin belgesi talep edilebilir.",
        ],
        "who_for": [
            "18 yaşından küçük tüm yolcular (bebekler dahil)",
            "Ailesiyle birlikte 1-30 gün Dubai'de kalacak çocuklar",
            "Okul tatilinde aile seyahati planlayan ebeveynler",
        ],
        "highlights": [
            "18 yaş altı için indirimli hizmet bedeli",
            "Ebeveyn başvurusuyla aynı formda gönderim",
            "Aile indirimi ile toplam maliyette ek avantaj",
            "Çocuk pasaportu ve fotoğraf kurallarında danışman desteği",
        ],
        "tips": [
            "Çocuğun vesikalık fotoğrafı beyaz fonda, yüzü tam görünecek şekilde ve oyuncak/emzik olmadan çekilmelidir.",
            "Boşanmış ebeveynlerde velayet belgesi ve diğer ebeveynin izni istenebilir; bu belgeleri önceden hazırlayın.",
            "Çocuğun pasaport geçerliliği de dönüş tarihinden itibaren en az 6 ay olmalıdır.",
        ],
        "faqs": [
            {
                "q": "Bebekler için de Dubai vizesi almak zorunlu mu?",
                "a": "Evet. Yaş sınırı olmaksızın kendi pasaportu bulunan her yolcu için ayrı vize alınması gerekir; bebekler de dahildir.",
            },
            {
                "q": "Çocuk vizesinde veli izin belgesi isteniyor mu?",
                "a": "Çocuk her iki ebeveyniyle seyahat ediyorsa genelde istenmez. Tek ebeveynle veya refakatçiyle seyahatlerde noter onaylı izin belgesi talep edilebilir.",
            },
            {
                "q": "Çocuk vizesi ebeveyn vizesinden neden daha ucuz?",
                "a": "18 yaş altı yolcular için resmî harç ve hizmet bedeli daha düşük belirlenmiştir. Aile başvurusunda ayrıca kademeli aile indirimi de uygulanır.",
            },
        ],
    },
    "60-gun-cocuk-vizesi": {
        "h1": "60 Günlük Çocuk Vizesi (Dubai)",
        "seo_title": "Dubai Çocuk Vizesi 60 Gün | Uzun Aile Tatili İçin İndirimli Vize",
        "seo_description": "18 yaş altı çocuklar için 60 günlük indirimli Dubai vizesi. Uzun aile tatillerinde gerekli belgeler, veli izni ve tek formda aile başvurusu.",
        "keywords": ["60 günlük çocuk vizesi", "dubai aile vizesi", "çocuk dubai vize fiyat"],
        "intro": [
            "60 günlük çocuk vizesi, uzun süreli aile tatillerinde 18 yaş altı yolcuların iki aya kadar Birleşik Arap Emirlikleri'nde kalmasını sağlar. Özellikle uzun okul tatillerinde ve aile ziyaretlerinde tercih edilir.",
            "Tek formda tüm ailenin başvurusunu birlikte yaparak hem aile indiriminden hem de çocuk vizesine özel indirimli fiyattan yararlanabilirsiniz. Evraklarınız gönderim öncesi tek tek kontrol edilir.",
        ],
        "who_for": [
            "Ailesiyle 30 günden uzun kalacak 18 yaş altı yolcular",
            "Uzun yaz veya kış tatilinde Dubai'de kalacak aileler",
            "BAE'de yaşayan yakınlarını uzun süre ziyaret edecek çocuklar",
        ],
        "highlights": [
            "60 gün kalış hakkı, indirimli çocuk fiyatı",
            "Ebeveyn başvurusuyla birlikte tek dosya",
            "Aile indirimi ile toplam maliyette avantaj",
        ],
        "tips": [
            "Uzun kalışlarda çocuklar için seyahat sağlık sigortası eklemenizi önemle öneririz.",
            "Okul döneminde uzun kalış planlıyorsanız okuldan izin/belge süreçlerini de önceden planlayın.",
        ],
        "faqs": [
            {
                "q": "60 günlük çocuk vizesi kaç günde sonuçlanır?",
                "a": "Bu vize tipinde sonuç genellikle 3-5 iş günü içinde çıkar. Acil durumlarda ekspres hizmet ile süreç hızlandırılabilir.",
            },
            {
                "q": "Çocuğumun pasaportu yok, ailemin pasaportuna ekleyebilir miyim?",
                "a": "Hayır. Vize başvurusu için çocuğun kendi adına düzenlenmiş geçerli bir pasaportu bulunmalıdır.",
            },
        ],
    },
    "30-gun-vize-uzatma": {
        "h1": "Dubai Vize Uzatma (30 Gün)",
        "seo_title": "Dubai Vize Uzatma 2026 | Ülkeden Çıkmadan 30 Gün Ek Süre",
        "seo_description": "Dubai'de vize uzatma nasıl yapılır? Ülkeden çıkmadan 30 gün ek süre, uzatma şartları, ceza riskleri, işlem süresi ve online uzatma başvurusu.",
        "keywords": ["dubai vize uzatma", "dubai vize süresi uzatma", "dubai kalış süresi aşımı"],
        "intro": [
            "Dubai vize uzatma hizmeti, Birleşik Arap Emirlikleri'nde bulunduğunuz sırada ülkeden çıkış yapmanıza gerek kalmadan kalış sürenizi 30 gün daha uzatmanızı sağlar. İşiniz uzadığında ya da tatilinizi uzatmaya karar verdiğinizde en pratik çözümdür.",
            "Uzatma başvurusunun mevcut vizenizin süresi dolmadan yapılması gerekir. Süre aşımı durumunda günlük para cezası uygulanır ve ilerideki başvurularınız olumsuz etkilenebilir; bu nedenle son güne bırakmayın.",
            "Uzatma en fazla iki kez yapılabilir. Daha uzun süre kalmayı planlıyorsanız oturum/freelancer vizesi gibi alternatifleri değerlendirmenizi öneririz.",
        ],
        "who_for": [
            "Dubai'de bulunan ve kalış süresini uzatmak isteyen yolcular",
            "İş programı beklenenden uzun süren profesyoneller",
            "Ülkeden çıkış-giriş yapmak (visa run) istemeyen misafirler",
        ],
        "highlights": [
            "Ülkeden çıkmadan 30 gün ek kalış",
            "En fazla 2 kez uygulanabilir",
            "2-4 iş günü içinde sonuç",
            "Süre aşımı cezası riskine karşı danışman takibi",
        ],
        "tips": [
            "Uzatma başvurusunu vize bitiminden en az 5 gün önce başlatın; işlem süresi 2-4 iş günüdür.",
            "Süre aşımı halinde günlük ceza tahakkuk eder ve havalimanında ödeme yapılmadan çıkış yapılamaz.",
            "Uzatma başvurusu için mevcut vizenizin ve pasaportunuzun net görüntüsü gerekir.",
        ],
        "faqs": [
            {
                "q": "Dubai vizemi kaç kez uzatabilirim?",
                "a": "Uzatma en fazla iki kez yapılabilir; her uzatma 30 gün ek süre sağlar. Sonrasında ülkeden çıkış yapmanız gerekir.",
            },
            {
                "q": "Vizem bitti, uzatma yapabilir miyim?",
                "a": "Süresi dolmuş vizede uzatma yapılamaz; bu durumda günlük ceza işlemeye başlar. En kısa sürede bizimle iletişime geçin, çıkış ve ceza sürecinde yol gösterelim.",
            },
            {
                "q": "Uzatma sırasında ülkeden çıkmam gerekir mi?",
                "a": "Hayır. Uzatmanın en büyük avantajı ülkeden çıkış yapmadan ek süre kazanmanızdır.",
            },
        ],
    },
    "transit-vize": {
        "h1": "48 Saatlik Dubai Transit Vizesi",
        "seo_title": "Dubai Transit Vizesi 48 Saat | Aktarmada Şehre Çıkış İzni",
        "seo_description": "Dubai transit vizesi ile aktarma sırasında 48 saat şehre çıkın. Kimler için uygun, gerekli belgeler, fiyat ve 1-2 iş gününde sonuç.",
        "keywords": ["dubai transit vize", "48 saat transit vize", "dubai aktarma vize"],
        "intro": [
            "Dubai transit vizesi, Birleşik Arap Emirlikleri üzerinden başka bir ülkeye aktarma yapan yolcuların 48 saat boyunca havalimanı dışına çıkmasına izin veren kısa süreli vize tipidir. Uzun bekleme süresi olan aktarmalı uçuşlarda şehri gezmek için idealdir.",
            "Transit vize yalnızca aktarma amaçlı seyahatlerde kullanılır. Doğrudan Dubai'yi hedefleyen tatil planları için 30 veya 60 günlük turistik vize seçenekleri uygundur.",
        ],
        "who_for": [
            "BAE üzerinden üçüncü bir ülkeye aktarmalı uçuşu olan yolcular",
            "Aktarma süresi 8 saatten uzun olup şehre çıkmak isteyenler",
            "Kısa bir Dubai molası planlayan gezginler",
        ],
        "highlights": [
            "48 saate kadar şehre çıkış izni",
            "1-2 iş günü içinde hızlı sonuç",
            "Turistik vizeye göre daha ekonomik",
        ],
        "tips": [
            "Devam eden uçuşunuzun bileti (onward ticket) başvurunun temel dayanağıdır; hazır bulundurun.",
            "48 saati aşan aktarmalarda transit vize yetersiz kalır; turistik vize almanız gerekir.",
        ],
        "faqs": [
            {
                "q": "Transit vize ile havalimanından çıkabilir miyim?",
                "a": "Evet. Transit vizenin amacı, aktarma sırasında 48 saate kadar şehre çıkmanıza izin vermektir.",
            },
            {
                "q": "Transit vize için hangi belgeler gerekir?",
                "a": "Pasaport kimlik sayfası, vesikalık fotoğraf ve devam eden uçuşunuzu gösteren bilet/rezervasyon belgesi gerekir.",
            },
            {
                "q": "Aktarmam 48 saatten uzun, ne yapmalıyım?",
                "a": "Bu durumda transit vize uygun olmaz; 30 günlük turistik vizeye başvurmanız gerekir.",
            },
        ],
    },
    "2-yillik-freelancer-vizesi": {
        "h1": "2 Yıllık Dubai Freelancer (Serbest Çalışma) Vizesi",
        "seo_title": "Dubai Freelancer Vizesi 2 Yıl | Emirates ID ve Oturum İzni Süreci",
        "seo_description": "2 yıllık Dubai freelancer (serbest çalışma) vizesi: Emirates ID, sınırsız giriş-çıkış, banka hesabı açma, gerekli belgeler, süreç ve maliyet.",
        "keywords": ["dubai freelancer vizesi", "dubai oturum izni", "emirates id", "dubai serbest çalışma vizesi"],
        "intro": [
            "2 yıllık Dubai freelancer vizesi, Birleşik Arap Emirlikleri'nde serbest çalışmak, oturum kartı (Emirates ID) almak ve iki yıl boyunca sınırsız giriş-çıkış yapmak isteyenler için tasarlanmış bir oturum çözümüdür. Uzaktan çalışan yazılımcılar, danışmanlar, tasarımcılar ve içerik üreticileri arasında hızla yaygınlaşmaktadır.",
            "Süreç, turistik vizeden farklı olarak birden çok aşamadan oluşur: freelancer izninin (permit) alınması, giriş izni, medikal kontrol, Emirates ID biyometrisi ve son olarak oturum izninin pasaporta işlenmesi. Bu nedenle işlem süresi 15-25 iş günü arasındadır ve bazı adımlar için BAE'de fiziksel olarak bulunmanız gerekir.",
            "Oturum izni sahibi olmak, BAE'de banka hesabı açma, uzun dönem kira sözleşmesi yapma ve yerel hizmetlere erişim gibi önemli avantajlar sağlar. Süreç boyunca tüm adımlarda danışmanınız yanınızda olur.",
        ],
        "who_for": [
            "Uzaktan çalışan yazılımcı, tasarımcı, danışman ve içerik üreticileri",
            "BAE'de banka hesabı açmak ve uzun dönem yerleşmek isteyenler",
            "İki yıl boyunca serbest giriş-çıkış esnekliği arayan profesyoneller",
            "Kendi işini BAE üzerinden yürütmek isteyen girişimciler",
        ],
        "highlights": [
            "2 yıl geçerli oturum izni",
            "Emirates ID (oturum kartı)",
            "Sınırsız giriş-çıkış hakkı",
            "Banka hesabı açma ve uzun dönem kira imkânı",
            "Tüm aşamalarda danışman desteği",
        ],
        "tips": [
            "Medikal test ve Emirates ID biyometrisi için BAE'de bulunmanız gereken bir dönem olacaktır; seyahat planınızı buna göre yapın.",
            "Diploma, portföy ve gelir belgeleri gibi ek evraklar talep edilebilir; süreci başlatmadan önce bunları hazırlayın.",
            "Oturum izni vergi danışmanlığı gerektirebilir; Türkiye'deki mükellefiyet durumunuzu ayrıca değerlendirin.",
        ],
        "faqs": [
            {
                "q": "Freelancer vizesi ile BAE'de çalışabilir miyim?",
                "a": "Evet. Freelancer izni, izin kapsamında belirtilen faaliyet alanında serbest çalışmanıza olanak tanır. Bir şirkete bağlı tam zamanlı çalışma için işveren sponsorluğunda çalışma vizesi gerekir.",
            },
            {
                "q": "Süreç ne kadar sürer ve BAE'de bulunmam gerekir mi?",
                "a": "Toplam süreç 15-25 iş günü arasındadır. Medikal kontrol ve Emirates ID biyometrisi aşamaları için BAE'de fiziksel olarak bulunmanız gerekir.",
            },
            {
                "q": "Ailemi de yanımda getirebilir miyim?",
                "a": "Oturum izni sahipleri belirli gelir ve konaklama koşullarını karşıladığında aile üyelerine sponsor olabilir. Bu süreç ayrı bir başvuru olarak yürütülür; danışmanınız detayları paylaşır.",
            },
            {
                "q": "Emirates ID nedir?",
                "a": "Emirates ID, BAE'de oturum izni sahiplerine verilen resmî kimlik kartıdır. Banka işlemleri, sağlık hizmetleri ve resmî başvurularda kullanılır.",
            },
        ],
    },
}


def _visa_by_slug(slug: str):
    return next((v for v in VISA_TYPES if v.get("slug") == slug), None)


def guide_index() -> list:
    """Rehber sayfalari listesi (linkleme ve sitemap icin)."""
    items = []
    for visa in sorted(VISA_TYPES, key=lambda v: v.get("order", 99)):
        guide = GUIDES.get(visa.get("slug"))
        if not guide:
            continue
        items.append(
            {
                "slug": visa["slug"],
                "path": f"{BASE_PATH}/{visa['slug']}",
                "visa_type_id": visa["id"],
                "title": guide["h1"],
                "name": visa["name"],
                "short_name": visa.get("short_name", visa["name"]),
                "category": visa.get("category"),
                "duration_days": visa.get("duration_days"),
                "entry_label": visa.get("entry_label"),
                "applicant_type": visa.get("applicant_type"),
                "processing_days": visa.get("processing_days"),
                "price": visa.get("price"),
                "price_usd": visa.get("price_usd"),
                "currency": visa.get("currency", "TRY"),
                "popular": visa.get("popular", False),
                "summary": visa.get("description", ""),
                "seo_description": guide["seo_description"],
            }
        )
    return items


def _related(slug: str, limit: int = 3) -> list:
    current = _visa_by_slug(slug)
    if not current:
        return []
    others = [i for i in guide_index() if i["slug"] != slug]
    same_cat = [i for i in others if i["category"] == current.get("category")]
    rest = [i for i in others if i["category"] != current.get("category")]
    ordered = same_cat + sorted(rest, key=lambda i: 0 if i["popular"] else 1)
    return ordered[:limit]


def _documents_for(visa: dict) -> list:
    docs = [dict(d) for d in REQUIRED_DOCUMENTS]
    slug = visa.get("slug")
    if visa.get("applicant_type") == "child":
        docs.append(
            {
                "key": "consent",
                "title": "Veli İzin Belgesi (gerekirse)",
                "detail": "Çocuk tek ebeveynle veya refakatçiyle seyahat ediyorsa noter onaylı veli izin belgesi talep edilebilir.",
                "required": False,
            }
        )
    if slug == "transit-vize":
        docs.append(
            {
                "key": "onward",
                "title": "Devam Eden Uçuş Bileti",
                "detail": "Aktarma sonrası üçüncü ülkeye devam eden uçuşunuzun bileti veya rezervasyon belgesi.",
                "required": True,
            }
        )
    if slug == "30-gun-vize-uzatma":
        docs.append(
            {
                "key": "current_visa",
                "title": "Mevcut Vize Belgesi",
                "detail": "Halen geçerli olan Dubai vizenizin PDF'i veya net görüntüsü.",
                "required": True,
            }
        )
    if slug == "2-yillik-freelancer-vizesi":
        docs.extend(
            [
                {
                    "key": "cv",
                    "title": "CV / Portföy",
                    "detail": "Serbest çalışma faaliyet alanınızı gösteren özgeçmiş veya portföy.",
                    "required": True,
                },
                {
                    "key": "diploma",
                    "title": "Diploma / Sertifika",
                    "detail": "Faaliyet alanınıza ilişkin diploma veya mesleki sertifika (talep edilirse).",
                    "required": False,
                },
            ]
        )
    return docs


def build_guide(slug: str, visa_override: dict | None = None, guide_override: dict | None = None):
    """Rehber sayfasi payload'i uretir. DB'deki degerler statik icerigi ezer."""
    base_visa = _visa_by_slug(slug)
    if not base_visa:
        return None
    guide = GUIDES.get(slug)
    if not guide:
        return None

    visa = {**base_visa, **(visa_override or {})}
    visa.pop("_id", None)
    content = {**guide, **(guide_override or {})}

    faqs = list(content.get("faqs") or []) + COMMON_FAQ

    return {
        "slug": slug,
        "path": f"{BASE_PATH}/{slug}",
        "visa": visa,
        "h1": content["h1"],
        "seo_title": content["seo_title"],
        "seo_description": content["seo_description"],
        "keywords": content.get("keywords", []),
        "intro": content.get("intro", []),
        "who_for": content.get("who_for", []),
        "highlights": content.get("highlights", []),
        "tips": content.get("tips", []),
        "faqs": faqs,
        "documents": _documents_for(visa),
        "photo_rules": PHOTO_RULES,
        "process_steps": PROCESS_STEPS,
        "related": _related(slug),
    }
