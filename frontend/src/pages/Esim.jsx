import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { Cpu, Globe2, QrCode, Wifi, Zap } from "lucide-react";
import { setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { StoreCheckout } from "../components/StoreCheckout";

const STEPS = [
    {
        icon: QrCode,
        title: "Paketi seçin, ödeyin",
        detail: "Kart veya havale ile ödeme yapın. Siparişiniz anında oluşturulur.",
    },
    {
        icon: Cpu,
        title: "QR kodunuz e-postanıza gelir",
        detail: "Ödeme onayından sonra eSIM QR kodunuz e-posta ile iletilir.",
    },
    {
        icon: Wifi,
        title: "Dubai'ye inince aktif olur",
        detail: "QR kodu taratıp eSIM'i kurun; uçaktan indiğinizde internetiniz hazır.",
    },
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

            <section className="section">
                <div className="container-page">
                    <StoreCheckout kind="esim" ctaLabel="eSIM satın al" />
                </div>
            </section>

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
                </div>
            </section>

            <section className="section" data-testid="esim-faq">
                <div className="container-page max-w-3xl">
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
