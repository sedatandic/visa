import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, BadgeCheck, Quote, Star } from "lucide-react";
import { Button } from "./ui/button";

const RED = "text-[hsl(var(--gold))]";

const Stars = ({ rating = 5, size = "h-4 w-4" }) => (
    <div className={`flex items-center gap-0.5 ${RED}`} aria-label={`${rating} / 5 puan`}>
        {[0, 1, 2, 3, 4].map((i) => (
            <Star key={i} className={`${size} ${i < rating ? "fill-current" : "opacity-30"}`} aria-hidden="true" />
        ))}
    </div>
);

/**
 * Ana sayfada ust bolumde gosterilen kompakt sosyal kanit vitrini:
 * ortalama puan + dogrulanmis yorum sayisi + otomatik donen kisa yorumlar.
 */
export const ReviewSpotlight = ({ summary, testimonials = [] }) => {
    const items = useMemo(() => (testimonials || []).slice(0, 5), [testimonials]);
    const [index, setIndex] = useState(0);
    const [paused, setPaused] = useState(false);

    useEffect(() => {
        if (paused || items.length < 2) return undefined;
        const id = setInterval(() => setIndex((i) => (i + 1) % items.length), 6000);
        return () => clearInterval(id);
    }, [paused, items.length]);

    if (!summary && !items.length) return null;
    const active = items[index] || null;
    const average = summary ? Number(summary.average) : null;

    return (
        <section className="border-b border-border bg-[hsl(var(--cloud))]" data-testid="review-spotlight">
            <div className="container-page grid items-center gap-8 py-10 lg:grid-cols-[0.9fr_1.1fr] lg:py-12">
                <div>
                    <span className="eyebrow">
                        <BadgeCheck className="h-3.5 w-3.5" aria-hidden="true" /> Doğrulanmış Müşteri Yorumları
                    </span>

                    {average !== null && (
                        <div className="mt-4 flex items-end gap-3">
                            <span
                                className={`font-heading text-5xl font-extrabold leading-none ${RED}`}
                                data-testid="spotlight-average-score"
                            >
                                {average.toLocaleString("tr-TR", { minimumFractionDigits: 1 })}
                            </span>
                            <div className="pb-1">
                                <Stars rating={Math.round(average)} size="h-5 w-5" />
                                <p className="mt-1.5 text-xs font-medium text-muted-foreground" data-testid="spotlight-review-count">
                                    {Number(summary.total_reviews).toLocaleString("tr-TR")} değerlendirme ·{" "}
                                    {Number(summary.total_applications).toLocaleString("tr-TR")}+ başvuru
                                </p>
                            </div>
                        </div>
                    )}

                    <p className="mt-5 max-w-md text-sm leading-6 text-muted-foreground">
                        Yorumlar yalnızca vizesi teslim edilen başvuru sahiplerine gönderilen ankete
                        verilen yanıtlardan alınır; referans kodu doğrulanmayan yorum yayınlanmaz.
                    </p>

                    <div className="mt-6 flex flex-wrap items-center gap-3">
                        <Button asChild className="h-11 px-5" data-testid="spotlight-apply-button">
                            <Link to="/basvuru">
                                Başvuruya Başla <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                        <a
                            href="#landing-testimonials"
                            className="inline-flex min-h-[44px] items-center gap-1.5 px-1 text-sm font-bold text-primary underline-offset-4 hover:underline"
                            data-testid="spotlight-all-reviews-link"
                        >
                            Tüm yorumları oku <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
                        </a>
                    </div>
                </div>

                {active && (
                    <div
                        className="relative"
                        onMouseEnter={() => setPaused(true)}
                        onMouseLeave={() => setPaused(false)}
                    >
                        <div
                            className="relative min-h-[232px] overflow-hidden rounded-2xl border border-border bg-card p-6 sm:p-7"
                            style={{ boxShadow: "var(--shadow-soft)" }}
                            aria-live="polite"
                        >
                            <Quote
                                className="absolute right-5 top-5 h-8 w-8 text-[hsl(var(--brand-copper)/0.18)]"
                                aria-hidden="true"
                            />
                            <AnimatePresence mode="wait">
                                <motion.figure
                                    key={active.name + index}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -8 }}
                                    transition={{ duration: 0.22 }}
                                    data-testid="spotlight-quote"
                                >
                                    <Stars rating={active.rating} size="h-4 w-4" />
                                    <blockquote className="mt-4 max-w-xl font-heading text-lg font-semibold leading-8 sm:text-xl">
                                        “{active.text}”
                                    </blockquote>
                                    <figcaption className="mt-5 flex items-center gap-3">
                                        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-primary/10 font-heading text-sm font-bold text-primary">
                                            {active.initials || active.name?.slice(0, 2)}
                                        </span>
                                        <span className="min-w-0">
                                            <span className="flex items-center gap-1.5 text-sm font-bold">
                                                {active.name}
                                                {active.verified && (
                                                    <BadgeCheck
                                                        className="h-4 w-4 shrink-0 text-primary"
                                                        aria-label="Doğrulanmış başvuru sahibi"
                                                    />
                                                )}
                                            </span>
                                            <span className="block truncate text-xs text-muted-foreground">
                                                {active.city}
                                                {active.visa ? ` · ${active.visa}` : ""}
                                            </span>
                                        </span>
                                    </figcaption>
                                </motion.figure>
                            </AnimatePresence>
                        </div>

                        {items.length > 1 && (
                            <div className="mt-4 flex items-center gap-2" role="tablist" aria-label="Yorumlar">
                                {items.map((t, i) => (
                                    <button
                                        key={t.name}
                                        type="button"
                                        role="tab"
                                        aria-selected={i === index}
                                        aria-label={`${i + 1}. yorumu göster`}
                                        onClick={() => setIndex(i)}
                                        data-testid={`spotlight-dot-${i}`}
                                        className={`h-2.5 rounded-full transition-[width,background-color] duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                                            i === index
                                                ? "w-7 bg-primary"
                                                : "w-2.5 bg-border hover:bg-muted-foreground/40"
                                        }`}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </section>
    );
};
