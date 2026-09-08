import React from "react";
import { Link } from "react-router-dom";
import { BadgeCheck, CreditCard, FileLock2, KeyRound, Lock, Radar, ShieldCheck, Trash2 } from "lucide-react";

/** Sitede gercekten uygulanan guvenlik onlemleri (uydurma sertifika/rozet yok). */
export const SECURITY_BADGES = [
    {
        key: "ssl",
        icon: Lock,
        title: "256-bit SSL şifreleme",
        text: "Site ve başvuru formundaki tüm trafik TLS ile şifrelenir; tarayıcınız her zaman HTTPS'e yönlendirilir (HSTS).",
    },
    {
        key: "payment",
        icon: CreditCard,
        title: "3D Secure · PCI-DSS ödeme",
        text: "Kart bilgileriniz PCI-DSS sertifikalı ödeme kuruluşunda işlenir, son onay bankanızın 3D Secure ekranında verilir. Kart numaranız sunucularımıza hiç ulaşmaz.",
    },
    {
        key: "documents",
        icon: FileLock2,
        title: "Belgeler imzalı bağlantıyla",
        text: "Pasaport taramanız ve fotoğrafınız yalnızca imzalı, süresi dolan bağlantılarla açılır; herkese açık bir dosya adresi yoktur.",
    },
    {
        key: "retention",
        icon: Trash2,
        title: "90 gün sonra imha",
        text: "Saklama süresi dolan belgelerin içeriği geri getirilemeyecek şekilde otomatik silinir.",
    },
    {
        key: "login",
        icon: KeyRound,
        title: "Şifresiz, tek kullanımlık kodla giriş",
        text: "Hesabınıza ve yönetim paneline giriş e-postaya gelen tek kullanımlık kodla yapılır; şifre tutulmadığı için sızdırılacak şifre de yoktur.",
    },
    {
        key: "kvkk",
        icon: ShieldCheck,
        title: "KVKK uyumlu veri işleme",
        text: "Aydınlatma metni ve gizlilik politikası yayında; verileriniz reklam veya pazarlama amacıyla üçüncü taraflara satılmaz.",
    },
    {
        key: "tursab",
        icon: BadgeCheck,
        title: "TÜRSAB üyesi A Grubu acente",
        text: "İşlemleriniz yasal yetkiye sahip, TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle yürütülür.",
    },
    {
        key: "hardening",
        icon: Radar,
        title: "Kötüye kullanım koruması",
        text: "Form ve kod gönderimlerinde hız sınırı, sertleştirilmiş sunucu başlıkları ve düzenli güvenlik denetimi uygulanır.",
    },
];

/** Ana sayfa / guvenlik sayfasi icin rozet izgarasi. */
export const SecurityBadges = ({ withHeading = true, className = "" }) => (
    <section
        className={`section border-y border-border bg-[hsl(var(--cloud))] ${className}`}
        data-testid="security-badges"
        aria-labelledby="security-badges-heading"
    >
        <div className="container-page">
            {withHeading && (
                <div className="max-w-2xl">
                    <span className="eyebrow">Güvenlik</span>
                    <h2 id="security-badges-heading" className="mt-3 text-2xl font-bold sm:text-3xl">
                        Pasaportunuzu emanet ediyorsunuz; karşılığı bu önlemler
                    </h2>
                    <p className="mt-3 text-sm leading-7 text-muted-foreground">
                        Aşağıdaki maddelerin hepsi sistemimizde aktif olarak uygulanıyor. Nasıl
                        çalıştığının ayrıntısını{" "}
                        <Link
                            to="/guvenlik"
                            className="font-semibold text-primary underline-offset-4 hover:underline"
                            data-testid="security-badges-detail-link"
                        >
                            güvenlik ve veri koruma sayfasında
                        </Link>{" "}
                        okuyabilirsiniz.
                    </p>
                </div>
            )}

            <div className={`grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4 ${withHeading ? "mt-8" : ""}`}>
                {SECURITY_BADGES.map(({ key, icon: Icon, title, text }) => (
                    <div
                        key={key}
                        className="card-surface flex h-full flex-col gap-2 p-4 transition-transform duration-200 hover:-translate-y-0.5 sm:gap-3 sm:p-5"
                        data-testid={`security-badge-${key}`}
                    >
                        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 sm:h-10 sm:w-10">
                            <Icon className="h-4 w-4 text-primary sm:h-5 sm:w-5" aria-hidden="true" />
                        </span>
                        <h3 className="font-heading text-[13px] font-bold leading-[18px] sm:text-sm sm:leading-5">
                            {title}
                        </h3>
                        <p className="hidden text-xs leading-6 text-muted-foreground sm:block">{text}</p>
                    </div>
                ))}
            </div>
        </div>
    </section>
);

/** Sepet/odeme adimlarinda kullanilan tek satirlik guven seridi. */
export const SecurityMiniStrip = ({ className = "" }) => (
    <div
        className={`rounded-xl border border-border bg-muted/30 px-4 py-3 ${className}`}
        data-testid="security-mini-strip"
    >
        <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1.5 font-semibold text-foreground">
                <Lock className="h-3.5 w-3.5 text-[hsl(var(--brand-green))]" aria-hidden="true" />
                256-bit SSL ile şifreli
            </span>
            <span className="inline-flex items-center gap-1.5">
                <CreditCard className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
                3D Secure · kart bilgisi saklanmaz
            </span>
            <span className="inline-flex items-center gap-1.5">
                <Trash2 className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
                Belgeler 90 gün sonra imha
            </span>
            <Link
                to="/guvenlik"
                className="ml-auto font-semibold text-primary underline-offset-4 hover:underline"
                data-testid="security-mini-strip-link"
            >
                Güvenlik detayları
            </Link>
        </div>
    </div>
);
