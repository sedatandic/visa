import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { CalendarDays, FileText, ShieldCheck } from "lucide-react";
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
            "Vize danışmanlık hizmetimizde iptal, iade ve ret durumlarında uygulanan kuralların tamamı.",
        meta: "İade ve İptal Koşulları | Dubai Vize Online",
        metaDesc:
            "Dubai vize başvurularında iptal, iade, ret (RED) ve süre aşımı durumlarında uygulanan koşullar.",
        testId: "refund-terms-page",
        icon: ShieldCheck,
    },
    service: {
        key: "service_terms",
        eyebrow: "Yasal Bilgilendirme",
        title: "Mesafeli Hizmet Sözleşmesi",
        description:
            "Online başvuru sırasında kurulan hizmet sözleşmesinin tarafları, kapsamı ve yükümlülükleri.",
        meta: "Mesafeli Hizmet Sözleşmesi | Dubai Vize Online",
        metaDesc:
            "Dubai Vize Online vize danışmanlık hizmeti mesafeli sözleşme metni: kapsam, yükümlülükler, ödeme ve cayma hakkı.",
        testId: "service-terms-page",
        icon: FileText,
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

            <section className="section">
                <div className="container-page max-w-3xl">
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
            </section>
        </div>
    );
}
