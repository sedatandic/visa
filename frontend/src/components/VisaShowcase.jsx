import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Clock, Repeat, Baby } from "lucide-react";
import { api } from "../lib/api";
import { IMAGES, formatMoney, formatUsd } from "../lib/site";
import { Button } from "./ui/button";
import { Skeleton } from "./ui/skeleton";

// Vitrin kartlarinda gosterilecek vize tipleri ve gorselleri (sabit sira).
const SHOWCASE = [
    { id: "visa_30_single", image: IMAGES.burjAlArabAerial, tag: "En çok tercih edilen" },
    { id: "visa_60_single", image: IMAGES.dubaiNight, tag: "Uzun tatil" },
    { id: "visa_30_multi", image: IMAGES.dubaiHighway, tag: "Çok girişli" },
    { id: "visa_30_child", image: IMAGES.travelFlatlay, tag: "Aile" },
    { id: "visa_transit_48", image: IMAGES.plane, tag: "Aktarma" },
    { id: "visa_extension_30", image: IMAGES.passportDocs, tag: "Uzatma" },
];

const shortTitle = (visa) => {
    const days = visa.duration_days >= 365
        ? `${Math.round(visa.duration_days / 365)} yıl`
        : `${visa.duration_days} gün`;
    if (visa.applicant_type === "child") return `${days} çocuk vizesi`;
    if (visa.id === "visa_extension_30") return `${days} vize uzatma`;
    if (visa.duration_days <= 2) return `${visa.duration_days * 24} saat transit`;
    return `${days} ${visa.entry_type === "multiple" ? "çok girişli" : "tek girişli"}`;
};

const metaIcon = (visa) => {
    if (visa.applicant_type === "child") return Baby;
    if (visa.entry_type === "multiple") return Repeat;
    return Clock;
};

export const VisaShowcase = () => {
    const [visas, setVisas] = useState(null);

    useEffect(() => {
        api.get("/visa-types")
            .then(({ data }) => setVisas(Array.isArray(data) ? data : []))
            .catch(() => setVisas([]));
    }, []);

    const cards = (visas || [])
        .map((visa) => {
            const preset = SHOWCASE.find((s) => s.id === visa.id);
            return preset ? { ...visa, ...preset } : null;
        })
        .filter(Boolean)
        .sort((a, b) => SHOWCASE.findIndex((s) => s.id === a.id) - SHOWCASE.findIndex((s) => s.id === b.id));

    return (
        <section className="section" data-testid="landing-visa-showcase">
            <div className="container-page">
                <div className="panel-float px-5 py-10 sm:px-8 sm:py-12">
                    <div className="flex flex-wrap items-end justify-between gap-4">
                        <div className="max-w-2xl">
                            <span className="eyebrow">Vize tipleri</span>
                            <h2 className="mt-3 font-heading text-2xl font-extrabold sm:text-3xl">
                                En çok tercih edilen Dubai vizeleri
                            </h2>
                            <p className="mt-3 text-sm leading-6 text-muted-foreground sm:text-base">
                                Kartlardan birine dokunun; başvuru formu seçtiğiniz vize türüyle açılır. Fiyatlar ve
                                tüm seçenekler için hizmet bedelleri sayfasına göz atabilirsiniz.
                            </p>
                        </div>
                        <Button asChild variant="outline" data-testid="showcase-all-types-button">
                            <Link to="/vize-tipleri">
                                Tüm vize tipleri <ArrowRight className="ml-1 h-4 w-4" />
                            </Link>
                        </Button>
                    </div>

                    {visas === null ? (
                        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                            {[0, 1, 2, 3, 4, 5].map((i) => (
                                <Skeleton key={i} className="h-[320px] rounded-[var(--radius-lg)]" />
                            ))}
                        </div>
                    ) : cards.length === 0 ? (
                        <div
                            className="mt-8 rounded-[var(--radius-lg)] border border-dashed border-border p-8 text-center"
                            data-testid="showcase-empty-state"
                        >
                            <p className="text-sm text-muted-foreground">
                                Vize tipleri şu anda görüntülenemiyor.
                            </p>
                            <Button asChild variant="outline" className="mt-4">
                                <Link to="/vize-tipleri">Hizmet bedellerine git</Link>
                            </Button>
                        </div>
                    ) : (
                        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                            {cards.map((visa) => {
                                const Icon = metaIcon(visa);
                                return (
                                    <Link
                                        key={visa.id}
                                        to={`/basvuru?vize=${visa.id}`}
                                        className="group block overflow-hidden rounded-[var(--radius-lg)] border border-border bg-card transition-colors duration-200 hover:border-primary/40 focus-visible:outline-none"
                                        data-testid={`showcase-card-${visa.id}`}
                                        aria-label={`${visa.name} ile başvuruya başla`}
                                    >
                                        <span className="relative block overflow-hidden">
                                            <img
                                                src={visa.image}
                                                alt={visa.name}
                                                className="h-[170px] w-full object-cover transition-transform duration-300 group-hover:scale-[1.04]"
                                                loading="lazy"
                                            />
                                            <span className="absolute left-3 top-3 inline-flex items-center gap-1.5 rounded-full bg-white/95 px-3 py-1 text-[10px] font-extrabold uppercase tracking-wider text-[hsl(var(--charcoal))]">
                                                <Icon className="h-3 w-3" aria-hidden="true" />
                                                {visa.tag}
                                            </span>
                                        </span>

                                        <span className="block p-4">
                                            <span className="block font-heading text-lg font-extrabold leading-tight text-foreground">
                                                {shortTitle(visa)}
                                            </span>
                                            <span className="mt-1 block truncate text-xs text-muted-foreground">
                                                {visa.name}
                                            </span>

                                            <span className="mt-3 flex items-end justify-between gap-3 border-t border-border pt-3">
                                                <span>
                                                    <span
                                                        className="tabular block font-heading text-xl font-extrabold leading-none text-foreground"
                                                        data-testid={`showcase-price-${visa.id}`}
                                                    >
                                                        {formatMoney(visa.price, visa.currency)}
                                                    </span>
                                                    <span className="mt-1 block text-[11px] text-muted-foreground">
                                                        kişi başı · {formatUsd(visa.price_usd)}
                                                    </span>
                                                </span>
                                                <span className="inline-flex h-9 shrink-0 items-center gap-1.5 rounded-full bg-primary px-4 text-xs font-bold text-primary-foreground transition-transform duration-200 group-hover:translate-x-0.5">
                                                    Seç
                                                    <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
                                                </span>
                                            </span>
                                        </span>
                                    </Link>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>
        </section>
    );
};
