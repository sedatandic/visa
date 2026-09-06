import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Baby, Check, Plane, ShieldCheck, ShoppingBag, Signal, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { formatMoney } from "../lib/site";
import { useCart } from "../lib/cart";

const PICKS = ["pack_standard", "pack_family", "pack_long"];

export const HomeBundleStrip = () => {
    const [bundles, setBundles] = useState([]);
    const cart = useCart();

    /** Hazir paketi (vizeler + sigorta + eSIM) tek tikla sepete ekler. */
    const addBundleToCart = (bundle) => {
        const visas = [];
        if (bundle.visa) {
            visas.push({ visa_type_id: bundle.visa.id, quantity: bundle.family?.adults || 1 });
        }
        if (bundle.family?.child_visa && bundle.family.children) {
            visas.push({ visa_type_id: bundle.family.child_visa.id, quantity: bundle.family.children });
        }
        const res = cart.addMany(
            [
                { product_id: bundle.insurance?.id, quantity: bundle.quantities?.insurance || 1 },
                { product_id: bundle.esim?.id, quantity: bundle.quantities?.esim || 1 },
            ].filter((i) => i.product_id),
            { bundleId: bundle.id, visas }
        );
        if (!res.ok) {
            toast.error("Sepete en fazla 6 farklı ürün ekleyebilirsiniz.");
            return;
        }
        const detail = bundle.family
            ? `${bundle.family.adults} yetişkin + ${bundle.family.children} çocuk vizesi, ${bundle.quantities.insurance} sigorta, ${bundle.quantities.esim} eSIM`
            : "vize + sigorta + eSIM";
        toast.success(`${bundle.name} sepete eklendi: ${detail}.`, {
            action: { label: "Sepete git", onClick: () => window.location.assign("/sepet") },
        });
    };

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
        <section className="section" data-testid="home-bundle-strip">
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

                <div className="mt-7 grid gap-5 lg:grid-cols-3">
                    {bundles.map((b) => (
                        <div
                            key={b.id}
                            className={`group flex h-full flex-col rounded-2xl border-2 bg-card p-6 text-left transition-all duration-200 hover:-translate-y-1 ${
                                b.id === popularId ? "border-primary" : "border-border hover:border-primary/60"
                            }`}
                            style={{ boxShadow: b.id === popularId ? "var(--shadow-soft)" : "var(--shadow-card)" }}
                            data-testid={`home-bundle-${b.id}`}
                        >
                            <div className="flex items-start justify-between gap-2">
                                <div>
                                    <p className="font-heading text-base font-bold">{b.name}</p>
                                    <p className="mt-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                        {b.family
                                            ? `${b.family.adults} yetişkin + ${b.family.children} çocuk`
                                            : `${b.visa_days} günlük vize için`}
                                    </p>
                                </div>
                                {b.family ? (
                                    <span className="rounded-full bg-[hsl(var(--cream-tag))] px-2.5 py-1 text-[11px] font-bold">
                                        Aile
                                    </span>
                                ) : (
                                    b.id === popularId && (
                                        <span className="rounded-full bg-[hsl(var(--cream-tag))] px-2.5 py-1 text-[11px] font-bold">
                                            En çok seçilen
                                        </span>
                                    )
                                )}
                            </div>

                            <p className="mt-3 text-sm leading-6 text-muted-foreground">{b.tagline}</p>

                            <ul className="mt-4 space-y-2.5 text-sm">
                                {b.visa && (
                                    <li className="flex items-start gap-2.5">
                                        <Plane className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                        <span>
                                            {b.visa.name}
                                            {b.family?.adults > 1 ? ` × ${b.family.adults}` : ""}
                                            <span className="block text-xs text-muted-foreground">
                                                {formatMoney(b.visa.price, b.currency)} / yetişkin
                                            </span>
                                        </span>
                                    </li>
                                )}
                                {b.family?.child_visa && (
                                    <li className="flex items-start gap-2.5">
                                        <Baby className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                        <span>
                                            {b.family.child_visa.name}
                                            {b.family.children > 1 ? ` × ${b.family.children}` : ""}
                                            <span className="block text-xs text-muted-foreground">
                                                {formatMoney(b.family.child_visa.price, b.currency)} / çocuk
                                            </span>
                                        </span>
                                    </li>
                                )}
                                <li className="flex items-start gap-2.5">
                                    <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                    <span>
                                        {b.insurance.name}
                                        {b.quantities?.insurance > 1 ? ` × ${b.quantities.insurance}` : ""}
                                        <span className="block text-xs text-muted-foreground">
                                            {b.insurance.coverage}
                                        </span>
                                    </span>
                                </li>
                                <li className="flex items-start gap-2.5">
                                    <Signal className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                    <span>
                                        {b.esim.name}
                                        {b.quantities?.esim > 1 ? ` × ${b.quantities.esim}` : ""}
                                        <span className="block text-xs text-muted-foreground">
                                            {b.esim.data_amount} veri · {b.esim.validity_days} gün
                                        </span>
                                    </span>
                                </li>
                                <li className="flex items-start gap-2.5">
                                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--brand-green))]" aria-hidden="true" />
                                    <span className="font-semibold text-[hsl(var(--brand-green))]">
                                        {formatMoney(b.discount + (b.family?.visa_discount || 0), b.currency)} indirim
                                        {b.family?.visa_discount ? " (paket + aile)" : " (paket)"}
                                    </span>
                                </li>
                            </ul>

                            <div className="mt-auto pt-5">
                                <p className="text-xs text-muted-foreground">Vize dahil toplam</p>
                                <p
                                    className="tabular font-heading text-3xl font-extrabold leading-none tracking-tight text-[hsl(30_62%_38%)]"
                                    data-testid={`home-bundle-price-${b.id}`}
                                >
                                    {formatMoney(b.total_with_visa ?? b.price, b.currency)}
                                </p>
                                <p className="mt-1 text-xs text-muted-foreground">
                                    {b.family ? `${b.family.traveler_count} kişi` : "kişi başı"} · ekstralar{" "}
                                    {formatMoney(b.price, b.currency)}
                                </p>
                                <div className="mt-4 flex flex-col gap-2.5">
                                    <Link
                                        to={`/basvuru?paket=${b.id}`}
                                        className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-full bg-primary px-6 text-sm font-semibold text-primary-foreground transition-transform duration-150 hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
                                        data-testid={`home-bundle-cta-${b.id}`}
                                    >
                                        Bu paketle başvur <ArrowRight className="h-4 w-4" aria-hidden="true" />
                                    </Link>
                                    <button
                                        type="button"
                                        onClick={() => addBundleToCart(b)}
                                        className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-full border-2 border-border px-6 text-sm font-semibold text-foreground transition-colors duration-150 hover:border-primary/60 hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
                                        data-testid={`home-bundle-add-to-cart-${b.id}`}
                                    >
                                        <ShoppingBag className="h-4 w-4" aria-hidden="true" /> Paketi sepete ekle
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};
