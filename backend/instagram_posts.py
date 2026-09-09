"""Instagram takvimi: 12 hazir gonderi (gorsel + metin + hashtag + tarih onerisi).

Gonderiler `instagram_posts` koleksiyonunda tutulur; ilk okumada bu plandan olusturulur.
Yayin elle yapiliyor (panelde "gorseli indir" + "metni kopyala").
"""
from datetime import datetime, time, timedelta, timezone

HASHTAG_SETS = {
    "vize": (
        "#dubaivize #dubaivizesi #dubaivizehatti #dubai #birlesikarapemirlikleri "
        "#vizebasvurusu #vizeislemleri #seyahatacentesi #dubaitatil #seyahat"
    ),
    "aile": (
        "#dubaivize #dubaivizesi #dubaivizehatti #ailetatili #cocuklutatil "
        "#dubaiileaile #seyahatplani #vizebasvurusu #dubai"
    ),
    "ekstra": (
        "#dubaivizehatti #dubai #dubaiesim #seyahatsigortasi #colsafarisi "
        "#dubaiturlari #dubaivizesi #seyahatipuclari #tatilplani"
    ),
}

CTA = "📲 WhatsApp: +90 538 483 82 24\n🔗 dubaivizehatti.com"

# gun: ilk yayin gununden itibaren kaydirma, saat: yerel yayin saati
POSTS = [
    {
        "id": "ig-01",
        "title": "Vizeniz 36 saatte hazır",
        "image": "/instagram/post-01.jpg?v=2",
        "day": 0,
        "hour": 19,
        "caption": (
            "Dubai vizeniz 36 saatte hazır. 🇦🇪\n\n"
            "Pasaportunuzun ana sayfası ve bir vesikalık fotoğraf yeterli. "
            "Belgelerinizi kontrol edip resmî mercilere biz iletiyoruz; "
            "otel rezervasyonu veya uçak bileti istemiyoruz.\n\n"
            "Onaylanan vizeniz e-posta ve WhatsApp ile elinizde.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["vize"],
    },
    {
        "id": "ig-02",
        "title": "Gerekli belgeler",
        "image": "/instagram/post-02.jpg?v=2",
        "day": 2,
        "hour": 12,
        "caption": (
            "Dubai vizesi için istediğimiz tek şey iki belge. 📄\n\n"
            "• Pasaportunuzun ana sayfası\n"
            "• Bir vesikalık fotoğraf\n\n"
            "Formu 3 dakikada dolduruyor, belgeleri telefonunuzdan yüklüyorsunuz. "
            "Eksik ya da hatalı belgeyi başvuru gitmeden biz yakalıyoruz.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["vize"],
    },
    {
        "id": "ig-03",
        "title": "36 saat garantisi",
        "image": "/instagram/post-03.jpg?v=2",
        "day": 4,
        "hour": 20,
        "caption": (
            "36 saat garantisi: yazılı taahhüt. ⏱️\n\n"
            "Belgeleriniz eksiksizse başvurunuz 36 saat içinde sonuçlanır. "
            "Süre aşılırsa ödediğiniz ekspres hizmet bedelini iade ediyoruz; "
            "ekspres almadıysanız başvurunuzu ücretsiz ekspres sıraya alıyoruz.\n\n"
            "Geri sayım, başvurunuz resmî mercilere iletildiği anda başlar ve "
            "takip sayfanızda canlı görünür.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["vize"],
    },
    {
        "id": "ig-04",
        "title": "Otel ve bilet gerekmez",
        "image": "/instagram/post-04.jpg?v=2",
        "day": 6,
        "hour": 13,
        "caption": (
            "Vize için otel rezervasyonu ya da uçak bileti istemiyoruz. ✈️\n\n"
            "Planınız netleşmeden başvurabilirsiniz. Vizeniz onaylandıktan sonra "
            "biletinizi ve otelinizi dilediğiniz gibi ayarlarsınız.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["vize"],
    },
    {
        "id": "ig-05",
        "title": "Aile başvurusu",
        "image": "/instagram/post-05.jpg?v=2",
        "day": 8,
        "hour": 19,
        "caption": (
            "Tüm aile tek formda. 👨‍👩‍👧‍👦\n\n"
            "Eşinizi ve çocuklarınızı aynı başvuruya ekliyor, belgeleri tek seferde "
            "yüklüyorsunuz. Aile başvurularında indirim uygulanıyor ve herkesin vizesi "
            "aynı anda çıkıyor.\n\n"
            "Çocuklar için de aynı iki belge yeterli: pasaport ve fotoğraf.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["aile"],
    },
    {
        "id": "ig-06",
        "title": "Seyahat sağlık sigortası",
        "image": "/instagram/post-06.jpg?v=2",
        "day": 10,
        "hour": 12,
        "caption": (
            "Dubai'de sağlık masrafları yüksek. 🛡️\n\n"
            "Seyahat sağlık sigortanızı vize başvurunuzla birlikte, tek adımda "
            "ekleyebilirsiniz. Poliçeniz e-posta ile anında elinize geçer.\n\n"
            "Teminatlar ve fiyatlar sitemizde açık yazılı.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["ekstra"],
    },
    {
        "id": "ig-07",
        "title": "Dubai eSIM",
        "image": "/instagram/post-07.jpg?v=2",
        "day": 12,
        "hour": 18,
        "caption": (
            "İner inmez internetiniz hazır. 📱\n\n"
            "Dubai eSIM'inizi vizenizle birlikte alın; havalimanında sıra beklemeden, "
            "kart değiştirmeden bağlanın. QR kodunuz e-posta ile geliyor.\n\n"
            "Roaming faturası sürprizi yok.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["ekstra"],
    },
    {
        "id": "ig-08",
        "title": "Canlı başvuru takibi",
        "image": "/instagram/post-08.jpg?v=2",
        "day": 14,
        "hour": 13,
        "caption": (
            "Başvurunuz nerede? Merak etmenize gerek yok. 🔎\n\n"
            "Takip kodunuzla sitemizden başvurunuzun güncel durumunu ve 36 saatlik "
            "geri sayımı canlı görebilirsiniz. Her adımda e-posta ve WhatsApp "
            "bildirimi gönderiyoruz.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["vize"],
    },
    {
        "id": "ig-09",
        "title": "TÜRSAB belgeli acente",
        "image": "/instagram/post-09.jpg?v=2",
        "day": 16,
        "hour": 19,
        "caption": (
            "Kiminle çalıştığınız önemli. 🏅\n\n"
            "TÜRSAB belgeli, yetkili seyahat acentesiyiz. Ödemeniz güvenli altyapıdan "
            "geçer, faturanız düzenlenir, tüm iletişim kayıt altındadır.\n\n"
            "Belge ve şirket bilgilerimiz sitemizde açıkça yayında.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["vize"],
    },
    {
        "id": "ig-10",
        "title": "Çöl safarisi turu",
        "image": "/instagram/post-10.jpg?v=2",
        "day": 18,
        "hour": 20,
        "caption": (
            "Dubai'ye gidip çölü görmemek olmaz. 🏜️\n\n"
            "Çöl safarisi turunu vize başvurunuzla birlikte ekleyebilirsiniz: "
            "otelden alış, kum tepelerinde sürüş, akşam yemeği ve gösteri dahil.\n\n"
            "Kontenjan sınırlı; tarihinizi önceden ayırtın.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["ekstra"],
    },
    {
        "id": "ig-11",
        "title": "Ret durumunda ne olur?",
        "image": "/instagram/post-11.jpg?v=2",
        "day": 20,
        "hour": 12,
        "caption": (
            "\"Vizem reddedilirse ne olacak?\" 🤔\n\n"
            "En çok sorulan soru bu. Cevabımız net: iade koşullarımız sitemizde açıkça "
            "yazılı. Başvurunuz resmî mercilere iletilmeden iptal ederseniz hizmet "
            "bedelini iade ediyoruz; ret durumunda nedenini ve varsa yeniden başvuru "
            "yolunu birlikte değerlendiriyoruz.\n\n"
            "Sürpriz masraf, gizli ücret yok.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["vize"],
    },
    {
        "id": "ig-12",
        "title": "3 adımda vize",
        "image": "/instagram/post-12.jpg?v=2",
        "day": 22,
        "hour": 19,
        "caption": (
            "3 adımda Dubai vizesi. ✅\n\n"
            "1️⃣ Formu doldur (3 dakika)\n"
            "2️⃣ Pasaport ve fotoğrafını yükle\n"
            "3️⃣ Vizeni e-posta ve WhatsApp'tan al\n\n"
            "Gerisini biz hallediyoruz: kontrol, resmî başvuru, takip ve teslim.\n\n" + CTA
        ),
        "hashtags": HASHTAG_SETS["vize"],
    },
]

PROFILE = {
    "username": "dubaivizehatti",
    "display_name": "Dubai Vize Hattı",
    "bio": (
        "🇦🇪 Dubai vizeniz 36 saatte hazır\n"
        "📄 Sadece pasaport + fotoğraf\n"
        "🏅 TÜRSAB belgeli acente\n"
        "👇 Başvuru ve fiyatlar"
    ),
    "category": "Seyahat Acentesi",
    "steps": [
        "Instagram uygulamasında Ayarlar → Hesap → Profesyonel hesaba geç adımını izleyin, "
        "kategori olarak \"Seyahat Acentesi\" seçin ve İşletme hesabını onaylayın.",
        "Kullanıcı adını dubaivizehatti yapın, profil fotoğrafı olarak logonuzu yükleyin.",
        "Biyografiye aşağıdaki metni ve web sitesi alanına dubaivizehatti.com adresini girin.",
        "İletişim seçeneklerine WhatsApp numaranızı ve info@dubaivizehatti.com adresini ekleyin.",
        "İlk 9 gönderiyi sırasıyla paylaşın; profil ızgarası tek bir bütün gibi görünür.",
        "Otomatik paylaşım istiyorsanız hesabı bir Facebook Sayfası'na bağlayın; "
        "Meta erişim jetonunu bize iletince gönderileri sistem kendisi yayınlar.",
    ],
}


def default_schedule(start: datetime) -> list:
    """Plandaki gun/saat degerlerini gercek tarihlere cevirir."""
    rows = []
    for post in POSTS:
        day = (start + timedelta(days=post["day"])).date()
        rows.append(
            {
                **{k: v for k, v in post.items() if k not in ("day", "hour")},
                "scheduled_at": datetime.combine(
                    day, time(hour=post["hour"]), tzinfo=timezone.utc
                ).isoformat(),
                "status": "planned",
            }
        )
    return rows
