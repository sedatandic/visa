import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
    ArrowRight,
    BadgeCheck,
    CalendarDays,
    Check,
    Clock,
    FileText,
    HelpCircle,
    Loader2,
    LogIn,
    Users,
} from "lucide-react";
import { api } from "../lib/api";
import { COMPANY, formatMoney, formatUsd, setJsonLd, setMeta } from "../lib/site";
import { FxNote } from "../components/FxNote";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "../components/ui/accordion";
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from "../components/ui/breadcrumb";

const brandName = `${COMPANY.brand} ${COMPANY.brandSuffix}`;

function buildJsonLd(guide, path) {
    const origin = window.location.origin;
    const visa = guide.visa || {};
    return [
        {
            id: "guide-service",
            data: {
                "@context": "https://schema.org",
                "@type": "Service",
                name: guide.h1,
                serviceType: "Vize danışmanlığı",
                description: guide.seo_description,
                inLanguage: "tr-TR",
                areaServed: { "@type": "Country", name: "Türkiye" },
                provider: { "@type": "TravelAgency", name: brandName, telephone: COMPANY.phone },
                url: `${origin}${path}`,
                offers: {
                    "@type": "Offer",
                    price: visa.price,
                    priceCurrency: visa.currency || "TRY",
                    availability: "https://schema.org/InStock",
                    url: `${origin}/basvuru?vize=${visa.id}`,
                },
            },
        },
        {
            id: "guide-faq",
            data: {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                mainEntity: (guide.faqs || []).map((f) => ({
                    "@type": "Question",
                    name: f.q,
                    acceptedAnswer: { "@type": "Answer", text: f.a },
                })),
            },
        },
        {
            id: "guide-breadcrumb",
            data: {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                itemListElement: [
                    { "@type": "ListItem", position: 1, name: "Ana sayfa", item: origin },
                    { "@type": "ListItem", position: 2, name: "Vize Tipleri", item: `${origin}/vize-tipleri` },
                    { "@type": "ListItem", position: 3, name: guide.h1, item: `${origin}${path}` },
                ],
            },
        },
    ];
}

const GuideSkeleton = () => (
    <div className="container-page section space-y-6" data-testid="visa-guide-loading">
        <Skeleton className="h-4 w-64" />
        <Skeleton className="h-10 w-3/4" />
        <Skeleton className="h-24 w-full" />
        <div className="grid gap-5 sm:grid-cols-3">
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
        </div>
    </div>
);

export default function VisaGuide() {
    const { slug } = useParams();
    const [guide, setGuide] = useState(null);
    const [loading, setLoading] = useState(true);
    const [notFound, setNotFound] = useState(false);

    useEffect(() => {
        let cancelled = false;
        setLoading(true);
        setNotFound(false);
        window.scrollTo(0, 0);
        api.get(`/visa-guides/${slug}`)
            .then(({ data }) => {
                if (cancelled) return;
                setGuide(data);
                const path = `/dubai-vizesi/${data.slug}`;
                setMeta(data.seo_title, data.seo_description, {
                    canonicalPath: path,
                    ogType: "article",
                });
                buildJsonLd(data, path).forEach(({ id, data: payload }) => setJsonLd(id, payload));
            })
            .catch(() => {
                if (!cancelled) setNotFound(true);
            })
            .finally(() => !cancelled && setLoading(false));
        return () => {
            cancelled = true;
            ["guide-service", "guide-faq", "guide-breadcrumb"].forEach((id) => setJsonLd(id, null));
        };
    }, [slug]);

    if (loading) return <GuideSkeleton />;

    if (notFound || !guide) {
        return (
            <div className="container-page section" data-testid="visa-guide-not-found">
                <h1 className="text-2xl font-bold">Vize rehberi bulunamadı</h1>
                <p className="mt-3 text-sm text-muted-foreground">
                    Aradığınız rehber kaldırılmış veya adresi değişmiş olabilir.
                </p>
                <Button asChild className="mt-6 h-11">
                    <Link to="/vize-tipleri">Tüm vize tipleri</Link>
                </Button>
            </div>
        );
    }

    const visa = guide.visa || {};
    const applyHref = `/basvuru?vize=${visa.id}`;
    const facts = [
        { icon: CalendarDays, label: "Kalış süresi", value: `${visa.duration_days} gün` },
        { icon: LogIn, label: "Giriş tipi", value: visa.entry_label },
        { icon: Clock, label: "Sonuçlanma", value: visa.processing_days },
        {
            icon: Users,
            label: "Başvuran",
            value: visa.applicant_type === "child" ? "18 yaş altı" : "Yetişkin",
        },
    ];

    return (
        <div data-testid="visa-guide-page">
            {/* HERO */}
            <section className="border-b border-border bg-card">
                <div className="container-page py-10 sm:py-14">
                    <Breadcrumb>
                        <BreadcrumbList>
                            <BreadcrumbItem>
                                <BreadcrumbLink asChild>
                                    <Link to="/" data-testid="guide-breadcrumb-home">Ana sayfa</Link>
                                </BreadcrumbLink>
                            </BreadcrumbItem>
                            <BreadcrumbSeparator />
                            <BreadcrumbItem>
                                <BreadcrumbLink asChild>
                                    <Link to="/vize-tipleri" data-testid="guide-breadcrumb-visa-types">
                                        Vize Tipleri
                                    </Link>
                                </BreadcrumbLink>
                            </BreadcrumbItem>
                            <BreadcrumbSeparator />
                            <BreadcrumbItem>
                                <BreadcrumbPage className="line-clamp-1">{guide.h1}</BreadcrumbPage>
                            </BreadcrumbItem>
                        </BreadcrumbList>
                    </Breadcrumb>

                    <div className="mt-7 grid gap-10 lg:grid-cols-[1.5fr_1fr]">
                        <div>
                            <span className="eyebrow">Vize Rehberi</span>
                            <h1
                                className="mt-3 text-3xl font-extrabold leading-tight sm:text-4xl"
                                data-testid="visa-guide-title"
                            >
                                {guide.h1}
                            </h1>
                            <div className="mt-5 space-y-4 text-[15px] leading-8 text-foreground/85">
                                {(guide.intro || []).map((p, i) => (
                                    <p key={i}>{p}</p>
                                ))}
                            </div>
                        </div>

                        {/* PRICE / CTA BOX */}
                        <aside
                            className="h-fit rounded-2xl border-2 border-[hsl(var(--brand-copper))] bg-card p-6"
                            style={{ boxShadow: "var(--shadow-soft)" }}
                            data-testid="visa-guide-summary"
                        >
                            <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                                Hizmet bedeli
                            </p>
                            <p
                                className="mt-1.5 font-heading text-4xl font-extrabold tracking-tight text-[hsl(var(--brand-copper))]"
                                data-testid="visa-guide-price"
                            >
                                {formatMoney(visa.price, visa.currency)}
                                <span className="ml-2 align-middle text-sm font-semibold text-muted-foreground">
                                    / kişi başı
                                </span>
                            </p>
                            {visa.price_usd ? (
                                <p className="mt-1.5 text-xs text-muted-foreground" data-testid="visa-guide-price-usd">
                                    {formatUsd(visa.price_usd)} — ödeme, işlem günündeki güncel kurla TL olarak alınır
                                </p>
                            ) : null}
                            <div className="mt-3">
                                <FxNote variant="inline" />
                            </div>
                            <dl className="mt-5 space-y-3 border-t border-border pt-5">
                                {facts.map(({ icon: Icon, label, value }) => (
                                    <div key={label} className="flex items-start justify-between gap-3 text-sm">
                                        <dt className="flex items-center gap-2 text-muted-foreground">
                                            <Icon className="h-4 w-4 text-primary" /> {label}
                                        </dt>
                                        <dd className="text-right font-semibold">{value}</dd>
                                    </div>
                                ))}
                            </dl>
                            <Button asChild className="mt-6 h-12 w-full text-base" data-testid="visa-guide-apply-button">
                                <Link to={applyHref}>
                                    Bu vize ile başvuru yap <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                            <p className="mt-3 text-center text-xs text-muted-foreground">
                                Vize türü formda otomatik seçili gelir.
                            </p>
                        </aside>
                    </div>
                </div>
            </section>

            {/* WHO FOR + HIGHLIGHTS */}
            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8" data-testid="visa-guide-fit">
                <div className="container-page grid gap-6 md:grid-cols-2">
                    <div className="card-surface p-6">
                        <h2 className="font-heading text-lg font-bold">Bu vize kimler için uygun?</h2>
                        <ul className="mt-4 space-y-3">
                            {(guide.who_for || []).map((w) => (
                                <li key={w} className="flex items-start gap-2.5 text-sm leading-6">
                                    <BadgeCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                    <span>{w}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className="card-surface p-6">
                        <h2 className="font-heading text-lg font-bold">Öne çıkan avantajlar</h2>
                        <ul className="mt-4 space-y-3">
                            {(guide.highlights || []).map((h) => (
                                <li key={h} className="flex items-start gap-2.5 text-sm leading-6">
                                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--brand-copper))]" />
                                    <span>{h}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </section>

            {/* DOCUMENTS */}
            <section
                className="section border-y border-border bg-[hsl(var(--cloud))]"
                data-testid="visa-guide-documents"
            >
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Gerekli Belgeler</span>
                        <h2 className="mt-3 text-2xl font-bold">Bu başvuru için gereken belgeler</h2>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Belgelerinizi telefonunuzla fotoğraflayıp yükleyebilirsiniz. Ayrıntılı liste ve
                            fotoğraf kuralları Gerekli Belgeler sayfasındadır.
                        </p>
                    </div>
                    <div className="mt-7 grid gap-4 sm:grid-cols-2">
                        {(guide.documents || []).map((d) => (
                            <div
                                key={d.key}
                                className="flex items-start gap-3 rounded-xl border border-border bg-card p-4"
                                data-testid={`guide-doc-${d.key}`}
                            >
                                <FileText className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                <div className="min-w-0">
                                    <p className="text-sm font-semibold">
                                        {d.title}
                                        <span
                                            className={`ml-2 align-middle text-[11px] font-bold ${
                                                d.required
                                                    ? "text-[hsl(var(--brand-copper))]"
                                                    : "text-muted-foreground"
                                            }`}
                                        >
                                            {d.required ? "Zorunlu" : "Opsiyonel"}
                                        </span>
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>

                    <Button asChild variant="secondary" className="mt-7 h-11 border border-border">
                        <Link to="/gerekli-belgeler" data-testid="guide-documents-link">
                            Belge detayları ve fotoğraf kuralları <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                    </Button>
                </div>
            </section>

            {/* CONSULTANT NOTES */}
            {(guide.tips || []).length > 0 && (
                <section className="section" data-testid="visa-guide-tips">
                    <div className="container-page">
                        <div className="max-w-3xl rounded-xl border border-primary/25 bg-primary/5 p-6">
                            <h2 className="font-heading text-lg font-bold">Danışman notları</h2>
                            <ul className="mt-3 space-y-2.5">
                                {guide.tips.map((t) => (
                                    <li key={t} className="flex items-start gap-2.5 text-sm leading-6">
                                        <BadgeCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                        <span>{t}</span>
                                    </li>
                                ))}
                            </ul>
                            <p className="mt-5 text-sm text-muted-foreground">
                                Başvuru 4 adımda tamamlanır: bilgiler → belgeler → ödeme → sonuç.{" "}
                                <Link to="/" className="font-semibold text-primary underline-offset-4 hover:underline" data-testid="guide-process-link">
                                    Süreci ana sayfada görün
                                </Link>
                                .
                            </p>
                        </div>
                    </div>
                </section>
            )}

            {/* FAQ */}
            <section
                className="section border-y border-border bg-[hsl(var(--cloud))]"
                data-testid="visa-guide-faq"
            >
                <div className="container-page max-w-3xl">
                    <span className="eyebrow">Sıkça Sorulan Sorular</span>
                    <h2 className="mt-3 text-2xl font-bold">{visa.short_name} hakkında merak edilenler</h2>
                    <Accordion type="single" collapsible className="mt-6">
                        {(guide.faqs || []).map((f, i) => (
                            <AccordionItem key={f.q} value={`faq-${i}`} data-testid={`guide-faq-item-${i}`}>
                                <AccordionTrigger className="text-left text-sm font-semibold">
                                    <span className="flex items-start gap-2.5">
                                        <HelpCircle className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                        {f.q}
                                    </span>
                                </AccordionTrigger>
                                <AccordionContent className="text-sm leading-7 text-muted-foreground">
                                    {f.a}
                                </AccordionContent>
                            </AccordionItem>
                        ))}
                    </Accordion>
                    <p className="mt-6 text-sm text-muted-foreground">
                        Genel sorular (ödeme, pasaport geçerliliği, iade koşulları){" "}
                        <Link to="/sss" className="font-semibold text-primary underline-offset-4 hover:underline" data-testid="guide-faq-all-link">
                            Sıkça Sorulan Sorular
                        </Link>{" "}
                        sayfasında.
                    </p>
                </div>
            </section>

            {/* RELATED GUIDES */}
            {(guide.related || []).length > 0 && (
                <section className="section" data-testid="visa-guide-related">
                    <div className="container-page">
                        <h2 className="text-2xl font-bold">Diğer vize rehberleri</h2>
                        <p className="mt-2 text-sm text-muted-foreground">
                            Kalış sürenize ve giriş sayınıza göre alternatif vize tiplerini karşılaştırın.
                        </p>
                        <div className="mt-6 grid gap-5 md:grid-cols-3">
                            {guide.related.map((r) => (
                                <Link
                                    key={r.slug}
                                    to={r.path}
                                    className="card-surface card-hoverable p-5"
                                    data-testid={`related-guide-${r.slug}`}
                                >
                                    <p className="text-xs font-bold uppercase tracking-wider text-[hsl(var(--brand-copper))]">
                                        {r.entry_label} · {r.duration_days} gün
                                    </p>
                                    <h3 className="mt-2 font-heading text-base font-bold">{r.title}</h3>
                                    <p className="mt-2 line-clamp-3 text-sm leading-6 text-muted-foreground">
                                        {r.summary}
                                    </p>
                                    <p className="mt-3 font-heading text-lg font-extrabold">
                                        {formatMoney(r.price, r.currency)}
                                    </p>
                                </Link>
                            ))}
                        </div>
                    </div>
                </section>
            )}

            {/* CLOSING CTA */}
            <section className="border-t border-border bg-[hsl(var(--navy))]">
                <div className="container-page flex flex-col items-start gap-5 py-12 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <h2 className="font-heading text-2xl font-bold text-white">
                            {visa.short_name} başvurunuzu şimdi başlatın
                        </h2>
                        <p className="mt-2 max-w-xl text-sm leading-6 text-white/70">
                            Formu ortalama 5 dakikada doldurun; pasaportunuzu yüklediğinizde bilgiler otomatik
                            okunur. Ödeme öncesi tüm bilgileri özet ekranında kontrol edebilirsiniz.
                        </p>
                    </div>
                    <Button asChild className="h-12 shrink-0 px-7 text-base" data-testid="visa-guide-cta-bottom">
                        <Link to={applyHref}>
                            Başvuru Yap <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                    </Button>
                </div>
            </section>
        </div>
    );
}
