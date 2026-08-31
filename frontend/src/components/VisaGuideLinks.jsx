import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, BookOpen } from "lucide-react";
import { api } from "../lib/api";
import { formatMoney } from "../lib/site";
import { Skeleton } from "./ui/skeleton";

/**
 * Vize rehberi (SEO landing) sayfalarina ic link blogu.
 * /vize-tipleri ve ana sayfada kullanilir.
 */
export const VisaGuideLinks = ({ limit }) => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get("/visa-guides")
            .then(({ data }) => setItems(data.items || []))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" data-testid="visa-guide-links-loading">
                {[0, 1, 2].map((i) => (
                    <Skeleton key={i} className="h-28" />
                ))}
            </div>
        );
    }

    if (items.length === 0) return null;
    const visible = limit ? items.slice(0, limit) : items;

    return (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" data-testid="visa-guide-links">
            {visible.map((g) => (
                <Link
                    key={g.slug}
                    to={g.path}
                    className="group flex h-full flex-col rounded-xl border border-border bg-card p-5 transition-transform duration-200 hover:-translate-y-0.5 hover:border-primary/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                    data-testid={`visa-guide-link-${g.slug}`}
                >
                    <span className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-[hsl(var(--brand-red))]">
                        <BookOpen className="h-3.5 w-3.5" /> {g.entry_label} · {g.duration_days} gün
                    </span>
                    <h3 className="mt-2.5 font-heading text-base font-bold leading-snug">{g.title}</h3>
                    <p className="mt-2 line-clamp-2 text-sm leading-6 text-muted-foreground">{g.summary}</p>
                    <span className="mt-4 flex items-center justify-between gap-3 border-t border-border pt-3">
                        <span className="font-heading text-base font-extrabold">
                            {formatMoney(g.price, g.currency)}
                        </span>
                        <span className="inline-flex items-center gap-1 text-sm font-semibold text-primary">
                            Rehberi oku
                            <ArrowRight className="h-3.5 w-3.5 transition-transform duration-200 group-hover:translate-x-0.5" />
                        </span>
                    </span>
                </Link>
            ))}
        </div>
    );
};
