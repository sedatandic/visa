import React from "react";
import { BadgeCheck, Quote, Star } from "lucide-react";
import { formatDate } from "../lib/site";

const RED = "text-[hsl(var(--brand-red))]";

const Stars = ({ rating = 5, size = "h-4 w-4" }) => (
    <div className={`flex items-center gap-0.5 ${RED}`} aria-label={`${rating} / 5 puan`}>
        {[0, 1, 2, 3, 4].map((i) => (
            <Star
                key={i}
                className={`${size} ${i < rating ? "fill-current" : "opacity-30"}`}
                aria-hidden="true"
            />
        ))}
    </div>
);

export const ReviewSummary = ({ summary }) => {
    if (!summary) return null;
    return (
        <div
            className="grid gap-6 rounded-2xl border border-[hsl(var(--brand-red)/0.28)] bg-[hsl(var(--brand-red)/0.05)] p-6 sm:p-8 lg:grid-cols-[280px_1fr]"
            data-testid="review-summary"
        >
            <div className="flex flex-col justify-center border-b border-[hsl(var(--brand-red)/0.2)] pb-6 lg:border-b-0 lg:border-r lg:pb-0 lg:pr-8">
                <div className="flex items-end gap-2">
                    <span
                        className={`font-heading text-5xl font-bold leading-none ${RED}`}
                        data-testid="review-average-score"
                    >
                        {Number(summary.average).toLocaleString("tr-TR", { minimumFractionDigits: 1 })}
                    </span>
                    <span className="pb-1 text-sm font-semibold text-muted-foreground">/ 5</span>
                </div>
                <div className="mt-3">
                    <Stars rating={Math.round(summary.average)} size="h-5 w-5" />
                </div>
                <p className="mt-3 text-sm text-muted-foreground" data-testid="review-total-count">
                    {Number(summary.total_reviews).toLocaleString("tr-TR")} doğrulanmış değerlendirme ·{" "}
                    {Number(summary.total_applications).toLocaleString("tr-TR")}+ tamamlanan başvuru
                </p>
            </div>

            <div className="grid gap-5 sm:grid-cols-3">
                {(summary.highlights || []).map((h) => (
                    <div key={h.label} data-testid={`review-highlight-${h.label}`}>
                        <div className="flex items-baseline justify-between gap-2">
                            <span className="text-sm font-medium">{h.label}</span>
                            <span className={`font-heading text-sm font-bold ${RED}`}>%{h.value}</span>
                        </div>
                        <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-[hsl(var(--brand-red)/0.14)]">
                            <div
                                className="h-full rounded-full bg-[hsl(var(--brand-red))]"
                                style={{ width: `${h.value}%` }}
                            />
                        </div>
                    </div>
                ))}
                <p className="text-sm leading-6 text-muted-foreground sm:col-span-3">
                    Değerlendirmeler yalnızca vize sonucu teslim edilen başvuru sahiplerine gönderilen
                    anket üzerinden toplanır; başvuru referans kodu ile eşleştirilmeyen yorumlar
                    yayınlanmaz.
                </p>
            </div>
        </div>
    );
};

export const TestimonialCard = ({ item }) => (
    <figure
        className="flex h-full flex-col rounded-xl border border-border bg-card p-5 transition-shadow duration-200 hover:shadow-[var(--shadow-card)]"
        data-testid={`testimonial-card-${item.name}`}
    >
        <div className="flex items-center justify-between gap-3">
            <Stars rating={item.rating} size="h-3.5 w-3.5" />
            <Quote className="h-5 w-5 text-[hsl(var(--brand-red)/0.35)]" aria-hidden="true" />
        </div>
        <blockquote className="mt-3 flex-1 text-sm leading-6">{item.text}</blockquote>
        <figcaption className="mt-5 flex items-center gap-3 border-t border-border pt-4">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 font-heading text-sm font-bold text-primary">
                {item.initials || item.name?.slice(0, 2)}
            </span>
            <span className="min-w-0">
                <span className="flex items-center gap-1.5 text-sm font-semibold">
                    {item.name}
                    {item.verified && (
                        <BadgeCheck
                            className="h-4 w-4 shrink-0 text-primary"
                            aria-label="Doğrulanmış başvuru sahibi"
                        />
                    )}
                </span>
                <span className="block truncate text-xs text-muted-foreground">
                    {item.city}
                    {item.visa ? ` · ${item.visa}` : ""}
                </span>
                {item.date && (
                    <span className="block text-[11px] text-muted-foreground/80">
                        {formatDate(item.date)}
                    </span>
                )}
            </span>
        </figcaption>
    </figure>
);

/** One cikan (buyuk) yorum karti — ana sayfa yorum bolumunun sol kolonu. */
export const FeaturedTestimonial = ({ item }) => {
    if (!item) return null;
    return (
        <figure
            className="flex h-full flex-col justify-between rounded-2xl border border-[hsl(var(--brand-red)/0.28)] bg-card p-6 sm:p-7"
            style={{ boxShadow: "var(--shadow-soft)" }}
            data-testid="featured-testimonial"
        >
            <div>
                <div className="flex items-start justify-between gap-3">
                    <Stars rating={item.rating} size="h-4.5 w-4.5" />
                    <Quote className="h-8 w-8 text-[hsl(var(--brand-red)/0.2)]" aria-hidden="true" />
                </div>
                <blockquote className="mt-4 font-heading text-lg font-semibold leading-8">
                    “{item.text}”
                </blockquote>
            </div>
            <figcaption className="mt-6 flex items-center gap-3 border-t border-border pt-5">
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-primary/10 font-heading text-sm font-bold text-primary">
                    {item.initials || item.name?.slice(0, 2)}
                </span>
                <span className="min-w-0">
                    <span className="flex items-center gap-1.5 text-sm font-bold">
                        {item.name}
                        {item.verified && (
                            <BadgeCheck className="h-4 w-4 shrink-0 text-primary" aria-label="Doğrulanmış başvuru sahibi" />
                        )}
                    </span>
                    <span className="block truncate text-xs text-muted-foreground">
                        {item.city}
                        {item.visa ? ` · ${item.visa}` : ""}
                    </span>
                    {item.date && (
                        <span className="block text-[11px] text-muted-foreground/80">{formatDate(item.date)}</span>
                    )}
                </span>
            </figcaption>
        </figure>
    );
};
