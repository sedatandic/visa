import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { Mail } from "lucide-react";
import { setMeta } from "../lib/site";
import { useContact } from "../lib/contact";
import { PageHeader } from "../components/SiteLayout";
import { SecurityBadges } from "../components/SecurityBadges";

const SECTIONS = [
    {
        h2: "Bağlantı ve site güvenliği",
        paras: [
            "Sitenin tamamı ve başvuru formu 256-bit SSL/TLS ile şifrelenir. Tarayıcınız HSTS başlığı sayesinde adresi elle yazsanız bile şifresiz bağlantı kurmaz. Sunucu yanıtlarında içerik türü zorlaması, çerçeveleme (clickjacking) koruması, referans politikası ve kamera/mikrofon/konum izinlerini kapatan başlıklar tanımlıdır.",
            "Yönetim arayüzünün API şeması dışarıya kapatılmıştır; başvuru, iletişim ve kod gönderimi uçlarında IP ve e-posta bazlı hız sınırları vardır. Böylece otomatik bot denemeleri ve kötüye kullanım engellenir.",
        ],
    },
    {
        h2: "Ödeme güvenliği",
        paras: [
            "Kart ödemeleri PCI-DSS sertifikalı uluslararası ödeme kuruluşunun güvenli sayfasında alınır. Kart numarası, son kullanma tarihi ve CVV bilgileriniz hiçbir aşamada sunucularımıza ulaşmaz veya kaydedilmez; bize yalnızca işlemin sonucunu gösteren referans bilgisi iletilir.",
            "Son onay bankanızın 3D Secure ekranında verilir. Havale/EFT tercih edenler için hesap bilgileri yalnızca kendi sitemiz üzerinden gösterilir; IBAN'ımızı e-posta veya WhatsApp'ta değiştiğini bildiren mesajlara güvenmeyin, ödeme öncesi bize doğrulatın.",
        ],
    },
    {
        h2: "Belgelerinizin güvenliği",
        paras: [
            "Pasaport taramanız ve biyometrik fotoğrafınız erişimi kısıtlı depolama alanında tutulur. Dosyalar herkese açık bir adreste yer almaz; yalnızca imzalı ve süresi dolan (panel görünümlerinde 12 saat, e-posta bağlantılarında sınırlı süreli) bağlantılarla açılabilir.",
            "Saklama süresi 90 gündür. Süre dolduğunda belgelerin içeriği geri getirilemeyecek şekilde otomatik olarak silinir; kayıtta yalnızca başvurunun izlenebilirliği için gereken bilgi kalır.",
        ],
    },
    {
        h2: "Hesap ve oturum güvenliği",
        paras: [
            "Ne müşteri hesabında ne yönetim panelinde şifre kullanılmaz. Giriş, e-postanıza gönderilen 6 haneli tek kullanımlık kodla yapılır; kod kısa süre geçerlidir, tek kullanımlıktır ve hatalı denemelerde kilitlenir. Şifre tutulmadığı için sızdırılabilecek bir şifre de yoktur.",
            "Kodlar veritabanında düz metin olarak saklanmaz. Oturumlar imzalı jetonla yürür ve süresi dolduğunda kendiliğinden kapanır.",
        ],
    },
    {
        h2: "Yetki, mevzuat ve şeffaflık",
        paras: [
            "Hizmet, TÜRSAB üyesi A Grubu seyahat acentesi olarak sunulur. Vize kararı Dubai göçmenlik makamlarına (GDRFA) aittir; biz başvuru hazırlığı, resmî kanala iletim ve süreç takibi hizmeti veririz.",
            "Kişisel verileriniz KVKK kapsamında işlenir; hangi verinin neden işlendiği, kimlerle paylaşıldığı ve haklarınızı nasıl kullanacağınız aydınlatma metninde ve gizlilik politikasında yazılıdır.",
        ],
    },
    {
        h2: "Dolandırıcılığa karşı 4 kontrol",
        paras: [
            "1) Ödeme yalnızca dubaivizehatti.com adresi üzerinden veya bize ait banka hesabına yapılır. 2) Adres çubuğunda kilit simgesi ve alan adının doğru yazıldığını kontrol edin. 3) Kurumumuz sizden şifre, kart CVV'si veya SMS kodu istemez. 4) Şüpheli bir mesaj alırsanız işlem yapmadan önce iletişim sayfamızdaki numaradan bize doğrulatın.",
        ],
    },
];

export default function Security() {
    const contact = useContact();

    useEffect(() => {
        setMeta(
            "Güvenlik ve Veri Koruma | Dubai Vize Hattı",
            "256-bit SSL, 3D Secure ödeme, imzalı belge bağlantıları, 90 gün sonra imha ve KVKK uyumu: bilgilerinizin nasıl korunduğunu adım adım açıklıyoruz."
        );
    }, []);

    return (
        <div data-testid="security-page">
            <PageHeader
                eyebrow="Güvenlik"
                title="Güvenlik ve veri koruma"
                description="Pasaport bilgilerinizi ve ödemenizi emanet ediyorsunuz. Karşılığında uyguladığımız teknik önlemlerin tamamı burada, açık dille yazılı."
            />

            <SecurityBadges withHeading={false} className="!border-t-0" />

            <section className="pb-14 pt-8 sm:pb-20 sm:pt-10">
                <div className="container-page">
                    <div className="max-w-4xl space-y-8 text-sm leading-7 text-muted-foreground">
                        {SECTIONS.map((section) => (
                            <div key={section.h2} data-testid={`security-section-${section.h2.slice(0, 12)}`}>
                                <h2 className="font-heading text-lg font-bold text-foreground">{section.h2}</h2>
                                {section.paras.map((para) => (
                                    <p key={para.slice(0, 40)} className="mt-2">
                                        {para}
                                    </p>
                                ))}
                            </div>
                        ))}

                        <div className="card-surface p-6" data-testid="security-report-box">
                            <h2 className="font-heading text-base font-bold text-foreground">
                                Güvenlik açığı bildirimi
                            </h2>
                            <p className="mt-2">
                                Sitede bir güvenlik açığı fark ettiyseniz lütfen kötüye kullanmadan bize
                                bildirin. Bildirimleri en kısa sürede inceleyip düzeltiyoruz.
                            </p>
                            {contact?.email && (
                                <a
                                    href={`mailto:${contact.email}?subject=Guvenlik%20bildirimi`}
                                    className="mt-3 inline-flex items-center gap-2 font-semibold text-primary underline-offset-4 hover:underline"
                                    data-testid="security-report-email"
                                >
                                    <Mail className="h-4 w-4" aria-hidden="true" />
                                    {contact.email}
                                </a>
                            )}
                        </div>

                        <p className="text-sm">
                            Ayrıntılı yasal metinler:{" "}
                            <Link to="/kvkk" className="font-semibold text-primary underline-offset-4 hover:underline">
                                KVKK aydınlatma metni
                            </Link>
                            {" · "}
                            <Link
                                to="/gizlilik-politikasi"
                                className="font-semibold text-primary underline-offset-4 hover:underline"
                            >
                                gizlilik politikası
                            </Link>
                            {" · "}
                            <Link
                                to="/hizmet-sozlesmesi"
                                className="font-semibold text-primary underline-offset-4 hover:underline"
                            >
                                hizmet sözleşmesi
                            </Link>
                            .
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
}
