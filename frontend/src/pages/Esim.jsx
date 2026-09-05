import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { Cpu, Globe2, QrCode, Wifi, Zap } from "lucide-react";
import { setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { StoreCheckout } from "../components/StoreCheckout";
import { EsimCompare } from "../components/EsimCompare";

const STEPS = [
    {
        icon: QrCode,
        title: "Paketi seçin, ödeyin",
        detail: "Kart veya havale ile ödeme yapın. Siparişiniz anında oluşturulur.",
    },
    {
        icon: Cpu,
        title: "QR kodunuz e-postanıza gelir",
        detail:
            "Ödeme onayından sonra eSIM QR kodunuz e-posta ile iletilir. Telefonunuzda Ayarlar → Hücresel/SIM → eSIM ekle adımını açın.",
    },
    {
        icon: Wifi,
        title: "QR'ı taratın, Dubai'de aktif olur",
        detail:
            "QR kodu taratıp hattı kurun; veri hattı olarak eSIM'i seçin. Uçaktan indiğinizde internetiniz hazır olur.",
    },
];

const SETUP = [
    "Türkiye'de, Wi-Fi bağlantısı varken kuruluma başlayın (QR kodu tek seferlik kullanılır).",
    "Ayarlar → Hücresel/Mobil Veri → eSIM veya Mobil Plan Ekle adımını açın.",
    "E-postanızdaki QR kodu telefonunuzun kamerasıyla okutun; hat telefonunuza eklenir.",
    "Hattı \"Dubai eSIM\" gibi bir etiketle isimlendirin ve şimdilik kapalı bırakın.",
    "Dubai'ye indiğinizde eSIM hattını açın, veri hattı olarak seçin ve dolaşımı (data roaming) etkinleştirin.",
    "Türkiye numaranızın mobil verisini kapatın; aramalar ve WhatsApp Türkiye hattınızda çalışmaya devam eder.",
];

const FAQ = [
    {
        q: "Telefonum eSIM destekliyor mu?",
        a: "iPhone XS ve sonrası, Samsung S20 ve sonrası, Google Pixel 3 ve sonrası modellerin çoğu eSIM destekler. Emin değilseniz sipariş notuna telefon modelinizi yazın, kontrol edip bilgilendiririz.",
    },
    {
        q: "Türkiye numaram açık kalır mı?",
        a: "Evet. eSIM ikinci hat olarak çalışır; Türkiye numaranız açık kalır, WhatsApp ve SMS'leriniz gelmeye devam eder. Yurt dışı veri kullanımını kapatmanız yeterlidir.",
    },
    {
        q: "eSIM ne zaman başlar?",
        a: "Paket, BAE'de şebekeye ilk bağlandığınız anda başlar. Türkiye'de kurulum yapıp Dubai'ye indiğinizde aktif hale gelir.",
    },
    {
        q: "Hotspot (internet paylaşımı) açık mı?",
        a: "3 GB ve üzeri paketlerde hotspot açıktır; dizüstü bilgisayarınızı veya arkadaşınızın telefonunu bağlayabilirsiniz.",
    },
];

export default function Esim() {
    useEffect(() => {
        setMeta(
            "Dubai eSIM Satın Al | Anında Kurulum, QR Kod ile İnternet",
            "Dubai ve BAE için eSIM paketleri: 1 GB'dan sınırsıza kadar seçenekler, QR kod ile 2 dakikada kurulum, Türkiye numaranız açık kalır. Güncel kurla TL ödeme.",
            { canonicalPath: "/esim" }
        );
    }, []);

    return (
        <div data-testid="esim-page">
            <PageHeader
                eyebrow="Dubai eSIM"
                title="Dubai'de ilk dakikadan itibaren internet"
                description="Roaming faturası sürprizi yok. eSIM paketinizi buradan alın, QR kodu taratın; Dubai'ye indiğiniz an bağlanın."
            />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page">
                    <StoreCheckout kind="esim" ctaLabel="eSIM satın al" />
                </div>
            </section>

            <EsimCompare />

            <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="esim-steps">
                <div className="container-page">
                    <span className="eyebrow">Nasıl çalışır?</span>
                    <h2 className="mt-3 text-2xl font-bold">Üç adımda bağlanın</h2>
                    <div className="mt-7 grid gap-5 md:grid-cols-3">
                        {STEPS.map(({ icon: Icon, title, detail }, i) => (
                            <div key={title} className="card-surface p-6">
                                <div className="flex items-center gap-3">
                                    <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                                        <Icon className="h-5 w-5" />
                                    </span>
                                    <span className="font-heading text-sm font-bold text-muted-foreground">
                                        {i + 1}. adım
                                    </span>
                                </div>
                                <h3 className="mt-4 font-heading text-base font-bold">{title}</h3>
                                <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{detail}</p>
                            </div>
                        ))}
                    </div>

                    <div className="mt-8 rounded-[var(--radius-lg)] border border-border bg-card p-6" data-testid="esim-setup-steps">
                        <h3 className="font-heading text-base font-bold">Kurulum adımları (adım adım)</h3>
                        <ol className="mt-4 space-y-3">
                            {SETUP.map((text, i) => (
                                <li key={text} className="flex gap-3 text-sm leading-6 text-muted-foreground">
                                    <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/12 text-xs font-bold text-primary">
                                        {i + 1}
                                    </span>
                                    {text}
                                </li>
                            ))}
                        </ol>
                        <p className="mt-4 text-xs text-muted-foreground">
                            Kurulumda takılırsanız WhatsApp'tan yazın; ekran görüntüsüyle birlikte adım
                            adım yardımcı oluyoruz.
                        </p>
                    </div>
                </div>
            </section>

            <section className="section" data-testid="esim-faq">
                <div className="container-page">
                    <span className="eyebrow">Sıkça sorulan sorular</span>
                    <h2 className="mt-3 text-2xl font-bold">eSIM hakkında merak edilenler</h2>
                    <div className="mt-6 space-y-4">
                        {FAQ.map((f) => (
                            <div key={f.q} className="card-surface p-5">
                                <h3 className="font-heading text-base font-bold">{f.q}</h3>
                                <p className="mt-2 text-sm leading-7 text-muted-foreground">{f.a}</p>
                            </div>
                        ))}
                    </div>

                    <div className="mt-8 flex flex-wrap items-center gap-3 rounded-xl border border-primary/25 bg-primary/5 p-6">
                        <Globe2 className="h-5 w-5 text-primary" />
                        <p className="text-sm">
                            Seyahat sigortanız var mı?{" "}
                            <Link to="/seyahat-sigortasi" className="font-semibold text-primary hover:underline">
                                Seyahat sigortası paketlerine bakın
                            </Link>
                            .
                        </p>
                        <Zap className="ml-auto hidden h-5 w-5 text-[hsl(var(--brand-copper))] sm:block" />
                    </div>
                </div>
            </section>
        </div>
    );
}
