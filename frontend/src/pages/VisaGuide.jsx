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
                            className="h-fit rounded-2xl border-2 border-[hsl(var(--brand-red))] bg-card p-6"
                            style={{ boxShadow: "var(--shadow-soft)" }}
                            data-testid="visa-guide-summary"
                        >
                            <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                                Hizmet bedeli
                            </p>
                            <p
                                className="mt-1.5 font-heading text-4xl font-extrabold tracking-tight text-[hsl(var(--brand-red))]"
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
            <section className="section" data-testid="visa-guide-fit">
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
                                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--brand-red))]" />
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
                            Belgelerinizi telefonunuzla fotoğraflayıp yükleyebilirsiniz. Yüklediğiniz her
                            evrak başvuru gönderilmeden önce danışmanlarımız tarafından kontrol edilir.
                        </p>
                    </div>
                    <div className="mt-7 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                        {(guide.documents || []).map((d) => (
                            <div key={d.key} className="card-surface p-5" data-testid={`guide-doc-${d.key}`}>
                                <div className="flex items-center justify-between gap-3">
                                    <FileText className="h-5 w-5 text-primary" />
                                    <span
                                        className={`rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${
                                            d.required
                                                ? "border-[hsl(var(--brand-red)/0.3)] bg-[hsl(var(--brand-red)/0.08)] text-[hsl(var(--brand-red))]"
                                                : "border-border bg-muted text-muted-foreground"
                                        }`}
                                    >
                                        {d.required ? "Zorunlu" : "Opsiyonel"}
                                    </span>
                                </div>
                                <h3 className="mt-3 font-heading text-base font-bold">{d.title}</h3>
                                <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{d.detail}</p>
                            </div>
                        ))}
                    </div>

                    <div className="mt-8 rounded-xl border border-border bg-card p-6">
                        <h3 className="font-heading text-base font-bold">Vesikalık fotoğraf kuralları</h3>
                        <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                            {(guide.photo_rules || []).map((r) => (
                                <li key={r} className="flex items-start gap-2 text-sm leading-6">
                                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" /> {r}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </section>

            {/* PROCESS */}
            <section className="section" data-testid="visa-guide-process">
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Başvuru Süreci</span>
                        <h2 className="mt-3 text-2xl font-bold">Adım adım nasıl ilerliyor?</h2>
                    </div>
                    <ol className="mt-7 grid gap-5 md:grid-cols-2 lg:grid-cols-4">
                        {(guide.process_steps || []).map((s) => (
                            <li key={s.step} className="card-surface p-5" data-testid={`guide-step-${s.step}`}>
                                <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 font-heading text-base font-extrabold text-primary">
                                    {s.step}
                                </span>
                                <h3 className="mt-3 font-heading text-base font-bold">{s.title}</h3>
                                <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{s.detail}</p>
                            </li>
                        ))}
                    </ol>

                    {(guide.tips || []).length > 0 && (
                        <div className="mt-9 rounded-xl border border-primary/25 bg-primary/5 p-6" data-testid="visa-guide-tips">
                            <h3 className="font-heading text-base font-bold">Danışman notları</h3>
                            <ul className="mt-3 space-y-2.5">
                                {guide.tips.map((t) => (
                                    <li key={t} className="flex items-start gap-2.5 text-sm leading-6">
                                        <BadgeCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                        <span>{t}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            </section>

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
                                    <p className="text-xs font-bold uppercase tracking-wider text-[hsl(var(--brand-red))]">
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
