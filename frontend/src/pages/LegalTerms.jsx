import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { CalendarDays, FileText, Lock, Mail, ShieldCheck } from "lucide-react";
import { api } from "../lib/api";
import { formatDate, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { Button } from "../components/ui/button";

const CONFIG = {
    refund: {
        key: "refund_terms",
        eyebrow: "Yasal Bilgilendirme",
        title: "İade ve İptal Koşulları",
        description:
            "Vize danışmanlığı, tur/aktivite ve transfer hizmetlerinde iptal, iade ve ret durumlarında uygulanan kuralların tamamı.",
        meta: "İade ve İptal Koşulları | Dubai Vize Online",
        metaDesc:
            "Dubai vize başvuruları, tur ve aktivite rezervasyonlarında iptal, iade, ret (RED), no-show ve mücbir sebep koşulları.",
        testId: "refund-terms-page",
        icon: ShieldCheck,
    },
    service: {
        key: "service_terms",
        eyebrow: "Yasal Bilgilendirme",
        title: "Şartlar ve Mesafeli Hizmet Sözleşmesi",
        description:
            "Online başvuru sırasında kurulan sözleşmenin tarafları, kapsamı, aracılık statüsü ve karşılıklı yükümlülükler.",
        meta: "Şartlar ve Mesafeli Hizmet Sözleşmesi | Dubai Vize Online",
        metaDesc:
            "Dubai Vize Online hizmet sözleşmesi: kapsam, yükümlülükler, ödeme, aracılık statüsü, riskli aktiviteler, cayma hakkı ve uyuşmazlık.",
        testId: "service-terms-page",
        icon: FileText,
    },
    privacy: {
        key: "privacy_policy",
        eyebrow: "Yasal Bilgilendirme",
        title: "Gizlilik Politikası",
        description:
            "Kişisel verilerinizi hangi amaçlarla işlediğimiz, kimlerle paylaştığımız, ne kadar sakladığımız ve haklarınız.",
        meta: "Gizlilik Politikası | Dubai Vize Online",
        metaDesc:
            "Dubai Vize Online gizlilik politikası: işlenen veri kategorileri, hukuki sebepler, yurt içi ve yurt dışı aktarım, saklama süreleri ve KVKK haklarınız.",
        testId: "privacy-policy-page",
        icon: Lock,
    },
    marketing: {
        key: "marketing_consent",
        eyebrow: "Yasal Bilgilendirme",
        title: "Ticari Elektronik İleti Onam Formu",
        description:
            "Kampanya ve fırsat bildirimleri için verdiğiniz onayın kapsamı, işlenen bilgiler ve onayı geri alma yolları.",
        meta: "Ticari Elektronik İleti Onam Formu | Dubai Vize Online",
        metaDesc:
            "Kampanya, indirim ve fırsat bildirimleri için ticari elektronik ileti onayının kapsamı, reklam eşleştirmesi ve izni geri alma adımları.",
        testId: "marketing-consent-page",
        icon: Mail,
    },
};

export default function LegalTerms({ variant = "refund" }) {
    const cfg = CONFIG[variant];
    const [doc, setDoc] = useState(null);

    useEffect(() => {
        setMeta(cfg.meta, cfg.metaDesc);
        api.get("/content/legal")
            .then(({ data }) => setDoc(data[cfg.key]))
            .catch(() => {});
    }, [cfg.key, cfg.meta, cfg.metaDesc]);

    const Icon = cfg.icon;

    return (
        <div data-testid={cfg.testId}>
            <PageHeader eyebrow={cfg.eyebrow} title={cfg.title} description={cfg.description} />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page">
                    <div className="max-w-3xl px-5 sm:px-8">
                    {doc?.updated_at && (
                        <p className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
                            <CalendarDays className="h-3.5 w-3.5" /> Son güncelleme: {formatDate(doc.updated_at)}
                        </p>
                    )}
                    <p className="mt-4 text-sm leading-7 text-muted-foreground">{doc?.intro}</p>

                    <div className="mt-8 space-y-6">
                        {(doc?.sections || []).map((s, i) => (
                            <div key={s.title} className="card-surface p-6" data-testid={`legal-section-${i}`}>
                                <h2 className="flex items-start gap-2.5 font-heading text-lg font-bold">
                                    <Icon className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--brand-copper))]" />
                                    {s.title}
                                </h2>
                                <ul className="mt-3 space-y-2.5">
                                    {(s.items || []).map((item, j) => (
                                        <li key={j} className="flex items-start gap-2 text-sm leading-7">
                                            <span className="mt-2.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                                            <span>{item}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>

                    <div className="mt-10 flex flex-col items-start gap-4 rounded-2xl border border-border bg-[hsl(var(--cloud))] p-7 sm:flex-row sm:items-center sm:justify-between">
                        <p className="text-sm font-semibold">
                            Sorunuz mu var? Danışmanlarımız süreçle ilgili tüm detayları açıklar.
                        </p>
                        <div className="flex gap-3">
                            <Button asChild variant="secondary" className="h-11 border border-border">
                                <Link to="/iletisim">İletişim</Link>
                            </Button>
                            <Button asChild className="h-11">
                                <Link to="/basvuru">Başvuru Yap</Link>
                            </Button>
                        </div>
                    </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
