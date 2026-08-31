import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { BadgeCheck, FileText, HeartPulse, Plane } from "lucide-react";
import { setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { StoreCheckout } from "../components/StoreCheckout";

const REASONS = [
    {
        icon: HeartPulse,
        title: "BAE'de sağlık masrafları yüksek",
        detail: "Basit bir acil servis başvurusu bile yüzlerce dolar tutabilir. Poliçe, acil sağlık masraflarınızı karşılar.",
    },
    {
        icon: FileText,
        title: "Vize başvurusuna uygun",
        detail: "Poliçeniz PDF olarak e-postanıza gelir; vize dosyanıza ek belge olarak koyabilirsiniz.",
    },
    {
        icon: Plane,
        title: "Bagaj ve iptal riskleri",
        detail: "Geniş kapsam paketi bagaj kaybı/gecikmesi ve seyahat iptali durumlarını da kapsar.",
    },
];

const FAQ = [
    {
        q: "Poliçe ne zaman elime geçer?",
        a: "Ödemeniz onaylandıktan sonra poliçeniz hazırlanır ve PDF olarak e-posta ile gönderilir. Kart ödemelerinde genellikle aynı gün, havalede ödeme onayından sonra iletilir.",
    },
    {
        q: "Kimler sigortalanabilir?",
        a: "Paketler kişi başıdır. Sipariş notuna sigortalanacak kişilerin ad-soyad ve doğum tarihlerini yazmanız yeterlidir; 65 yaş üstü için ek prim gerekebilir, sizi bilgilendiririz.",
    },
    {
        q: "Vize başvurumda sigorta zorunlu mu?",
        a: "Turistik Dubai vizesinde sigorta zorunlu belge değildir; ancak yüksek sağlık masrafları nedeniyle şiddetle önerilir ve dosyanızı güçlendirir.",
    },
    {
        q: "Poliçemi iptal edebilir miyim?",
        a: "Seyahat başlangıç tarihinden önce yazılı talebinizle iptal işlemi yapılabilir. Koşullar için İade ve İptal Koşulları sayfamıza bakabilirsiniz.",
    },
];

export default function Insurance() {
    useEffect(() => {
        setMeta(
            "Dubai Seyahat Sigortası Satın Al | 30.000 € ve 100.000 € Teminat",
            "Dubai ve BAE seyahatleri için seyahat sağlık sigortası: 30.000 € temel ve 100.000 € geniş kapsam paketleri, bagaj ve iptal teminatı, poliçe PDF olarak e-postanıza.",
            { canonicalPath: "/seyahat-sigortasi" }
        );
    }, []);

    return (
        <div data-testid="insurance-page">
            <PageHeader
                eyebrow="Seyahat Sigortası"
                title="Dubai seyahatiniz için sağlık güvencesi"
                description="Acil sağlık masrafları, bagaj ve iptal riskleri için poliçenizi buradan alın. Poliçeniz PDF olarak e-postanıza gelir."
            />

            <section className="section">
                <div className="container-page">
                    <StoreCheckout kind="insurance" ctaLabel="Poliçe satın al" />
                </div>
            </section>

            <section
                className="section border-y border-border bg-[hsl(var(--cloud))]"
                data-testid="insurance-reasons"
            >
                <div className="container-page">
                    <span className="eyebrow">Neden gerekli?</span>
                    <h2 className="mt-3 text-2xl font-bold">Sigorta neden önemli?</h2>
                    <div className="mt-7 grid gap-5 md:grid-cols-3">
                        {REASONS.map(({ icon: Icon, title, detail }) => (
                            <div key={title} className="card-surface p-6">
                                <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                                    <Icon className="h-5 w-5" />
                                </span>
                                <h3 className="mt-4 font-heading text-base font-bold">{title}</h3>
                                <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{detail}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <section className="section" data-testid="insurance-faq">
                <div className="container-page max-w-3xl">
                    <span className="eyebrow">Sıkça sorulan sorular</span>
                    <h2 className="mt-3 text-2xl font-bold">Sigorta hakkında merak edilenler</h2>
                    <div className="mt-6 space-y-4">
                        {FAQ.map((f) => (
                            <div key={f.q} className="card-surface p-5">
                                <h3 className="font-heading text-base font-bold">{f.q}</h3>
                                <p className="mt-2 text-sm leading-7 text-muted-foreground">{f.a}</p>
                            </div>
                        ))}
                    </div>

                    <div className="mt-8 flex flex-wrap items-center gap-3 rounded-xl border border-primary/25 bg-primary/5 p-6">
                        <BadgeCheck className="h-5 w-5 text-primary" />
                        <p className="text-sm">
                            Dubai'de internetsiz kalmayın:{" "}
                            <Link to="/esim" className="font-semibold text-primary hover:underline">
                                eSIM paketlerine göz atın
                            </Link>
                            .
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
}
