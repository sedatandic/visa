import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Check, Plane, ShieldCheck, Signal, Sparkles } from "lucide-react";
import { api } from "../lib/api";
import { formatMoney } from "../lib/site";

const PICKS = ["pack_standard", "pack_comfort", "pack_long"];

export const HomeBundleStrip = () => {
    const [bundles, setBundles] = useState([]);

    useEffect(() => {
        api.get("/bundles")
            .then(({ data }) => {
                const items = (data.items || []).filter((b) => PICKS.includes(b.id));
                setBundles(items.length ? items : (data.items || []).slice(0, 3));
            })
            .catch(() => setBundles([]));
    }, []);

    if (!bundles.length) return null;
    // Ayni seritte iki "En cok secilen" etiketi cikmasin: yalnizca ilk populer paket isaretlenir.
    const popularId = bundles.find((b) => b.popular)?.id;

    return (
        <section className="py-14 sm:py-20" data-testid="home-bundle-strip">
            <div className="container-page">
                <span className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--cream-tag))] px-3.5 py-1.5 text-xs font-bold uppercase tracking-wider">
                    <Sparkles className="h-3.5 w-3.5" aria-hidden="true" /> Seyahat paketleri
                </span>
                <h2 className="mt-4 max-w-2xl font-heading text-2xl font-extrabold leading-tight text-[hsl(30_62%_38%)] sm:text-3xl">
                    Vize + sigorta + eSIM, tek başvuruda
                </h2>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground sm:text-base">
                    Sigorta ve internet paketini vizenizle birlikte alın; paket indirimi
                    otomatik uygulanır, poliçe ve QR kod e-postanıza gelir.
                </p>

                <div className="mt-8 grid gap-5 lg:grid-cols-3">
                    {bundles.map((b) => (
                        <div
                            key={b.id}
                            className={`flex h-full flex-col rounded-2xl border-2 bg-card p-6 transition-shadow duration-200 ${
                                b.id === popularId ? "border-primary" : "border-border"
                            }`}
                            style={{ boxShadow: b.id === popularId ? "var(--shadow-soft)" : "var(--shadow-card)" }}
                            data-testid={`home-bundle-${b.id}`}
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div>
                                    <p className="font-heading text-base font-bold">{b.name}</p>
                                    <p className="mt-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                        {b.visa_days} günlük vize için
                                    </p>
                                </div>
                                {b.id === popularId && (
                                    <span className="rounded-full bg-[hsl(var(--cream-tag))] px-2.5 py-1 text-[11px] font-bold">
                                        En çok seçilen
                                    </span>
                                )}
                            </div>

                            <p className="mt-3 text-sm leading-6 text-muted-foreground">{b.tagline}</p>

                            <ul className="mt-5 space-y-3 text-sm">
                                {b.visa && (
                                    <li className="flex items-start gap-2.5">
                                        <Plane className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                        <span>
                                            {b.visa.name}
                                            <span className="block text-xs text-muted-foreground">
                                                {formatMoney(b.visa.price, b.currency)}
                                            </span>
                                        </span>
                                    </li>
                                )}
                                <li className="flex items-start gap-2.5">
                                    <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                    <span>
                                        {b.insurance.name}
                                        <span className="block text-xs text-muted-foreground">
                                            {b.insurance.coverage}
                                        </span>
                                    </span>
                                </li>
                                <li className="flex items-start gap-2.5">
                                    <Signal className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                    <span>
                                        {b.esim.name}
                                        <span className="block text-xs text-muted-foreground">
                                            {b.esim.data_amount} veri · {b.esim.validity_days} gün
                                        </span>
                                    </span>
                                </li>
                                <li className="flex items-start gap-2.5">
                                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--brand-green))]" aria-hidden="true" />
                                    <span className="font-semibold text-[hsl(var(--brand-green))]">
                                        {formatMoney(b.discount, b.currency)} paket indirimi
                                    </span>
                                </li>
                            </ul>

                            <div className="mt-auto pt-6">
                                <p className="text-xs text-muted-foreground">Vize dahil toplam</p>
                                <p
                                    className="tabular font-heading text-3xl font-extrabold leading-none tracking-tight text-[hsl(30_62%_38%)]"
                                    data-testid={`home-bundle-price-${b.id}`}
                                >
                                    {formatMoney(b.total_with_visa ?? b.price, b.currency)}
                                </p>
                                <p className="mt-1 text-xs text-muted-foreground">
                                    kişi başı · ekstralar {formatMoney(b.price, b.currency)}
                                </p>
                                <Link
                                    to="/basvuru"
                                    className="mt-4 inline-flex h-11 w-full items-center justify-center gap-2 rounded-full bg-primary px-6 text-sm font-semibold text-primary-foreground transition-transform duration-150 hover:-translate-y-0.5"
                                    data-testid={`home-bundle-cta-${b.id}`}
                                >
                                    Bu paketle başvur <ArrowRight className="h-4 w-4" aria-hidden="true" />
                                </Link>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};
