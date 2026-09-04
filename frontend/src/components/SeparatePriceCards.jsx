import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Plane, ShieldCheck, Signal } from "lucide-react";
import { api } from "../lib/api";
import { formatMoney } from "../lib/site";

const TABS = [
    { key: "visa", label: "Vize", icon: Plane, cta: "/vize-tipleri" },
    { key: "insurance", label: "Seyahat Sigortası", icon: ShieldCheck, cta: "/seyahat-sigortasi" },
    { key: "esim", label: "eSIM", icon: Signal, cta: "/esim" },
];

const Card = ({ title, subtitle, meta, price, currency, cta, testId }) => (
    <div
        className="flex h-full flex-col rounded-2xl border border-border bg-card p-5"
        style={{ boxShadow: "var(--shadow-card)" }}
        data-testid={testId}
    >
        <p className="font-heading text-sm font-bold leading-snug">{title}</p>
        {subtitle && <p className="mt-1.5 text-xs leading-5 text-muted-foreground">{subtitle}</p>}
        {meta && (
            <p className="mt-3 inline-flex w-fit rounded-full bg-[hsl(var(--cloud))] px-2.5 py-1 text-[11px] font-semibold text-muted-foreground">
                {meta}
            </p>
        )}
        <div className="mt-auto pt-5">
            <p className="tabular font-heading text-2xl font-extrabold leading-none tracking-tight text-[hsl(30_62%_38%)]">
                {formatMoney(price, currency)}
            </p>
            <Link
                to={cta}
                className="mt-3 inline-flex h-10 w-full items-center justify-center gap-2 rounded-full border border-border text-sm font-semibold transition-colors duration-150 hover:border-primary hover:text-primary"
            >
                Seç <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
            </Link>
        </div>
    </div>
);

export const SeparatePriceCards = () => {
    const [active, setActive] = useState("visa");
    const [visaTypes, setVisaTypes] = useState([]);
    const [products, setProducts] = useState([]);

    useEffect(() => {
        api.get("/visa-types")
            .then(({ data }) => setVisaTypes(data.items || data || []))
            .catch(() => setVisaTypes([]));
        api.get("/products")
            .then(({ data }) => setProducts(data.items || []))
            .catch(() => setProducts([]));
    }, []);

    const cards = useMemo(() => {
        if (active === "visa") {
            return (Array.isArray(visaTypes) ? visaTypes : [])
                .filter((v) => v.applicant_type === "adult")
                .map((v) => ({
                    id: v.id,
                    title: v.name,
                    subtitle: v.summary || v.description,
                    meta: `${v.duration_days} gün · ${v.processing_days || "hızlı işlem"}`,
                    price: v.price,
                    currency: v.currency || "TRY",
                    cta: "/basvuru",
                }));
        }
        return products
            .filter((p) => p.kind === active)
            .map((p) => ({
                id: p.id,
                title: p.name,
                subtitle: p.summary,
                meta:
                    active === "esim"
                        ? `${p.data_amount} veri · ${p.validity_days} gün`
                        : `${p.coverage} · ${p.validity_days} gün`,
                price: p.price,
                currency: p.currency || "TRY",
                cta: active === "esim" ? "/esim" : "/seyahat-sigortasi",
            }));
    }, [active, visaTypes, products]);

    if (!cards.length && !visaTypes.length && !products.length) return null;

    return (
        <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="separate-price-cards">
            <div className="container-page">
                <div className="max-w-2xl">
                    <span className="eyebrow">Tek tek seçim</span>
                    <h2 className="mt-3 font-heading text-2xl font-extrabold leading-tight text-[hsl(30_62%_38%)] sm:text-3xl">
                        Vize, sigorta ve eSIM fiyatları ayrı ayrı
                    </h2>
                    <p className="mt-3 text-sm leading-6 text-muted-foreground sm:text-base">
                        Paket almak zorunda değilsiniz. Yalnızca ihtiyacınız olanı seçin; fiyatlar
                        güncel kurla TL olarak gösterilir.
                    </p>
                </div>

                <div className="mt-7 inline-flex flex-wrap gap-2 rounded-full border border-border bg-card p-1.5">
                    {TABS.map((t) => {
                        const Icon = t.icon;
                        const on = active === t.key;
                        return (
                            <button
                                type="button"
                                key={t.key}
                                onClick={() => setActive(t.key)}
                                data-testid={`price-tab-${t.key}`}
                                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition-colors duration-150 ${
                                    on
                                        ? "bg-primary text-primary-foreground"
                                        : "text-muted-foreground hover:text-foreground"
                                }`}
                            >
                                <Icon className="h-4 w-4" aria-hidden="true" /> {t.label}
                            </button>
                        );
                    })}
                </div>

                <div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {cards.map((c) => (
                        <Card key={c.id} {...c} testId={`price-card-${c.id}`} />
                    ))}
                </div>
            </div>
        </section>
    );
};
