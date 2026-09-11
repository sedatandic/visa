import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, BadgePercent, ShieldCheck } from "lucide-react";
import { api } from "../lib/api";
import { formatMoney } from "../lib/site";
import { Button } from "./ui/button";

/**
 * "Vize + sigorta birlikte al, poliçede indirim" capraz satis kampanyasi.
 * Oran ve metinler sunucudan gelir (`/products` -> visa_insurance), sabit yazi yok.
 *
 * variant="band"   ana sayfa / sigorta sayfasi icin genis serit
 * variant="card"   sepette sigorta varken gosterilen kucuk kart
 * variant="badge"  hizmet bedelleri sayfasindaki satir rozeti
 */
export const InsuranceCampaign = ({ variant = "band", className = "" }) => {
    const [info, setInfo] = useState(null);
    const [cheapest, setCheapest] = useState(null);

    useEffect(() => {
        api.get("/products", { params: { kind: "insurance" } })
            .then(({ data }) => {
                setInfo(data.visa_insurance || null);
                const plans = [...(data.items || [])].sort(
                    (a, b) => (a.validity_days || 0) - (b.validity_days || 0)
                );
                setCheapest(plans[0] || null);
            })
            .catch(() => setInfo(null));
    }, []);

    const rate = Number(info?.rate || 0);
    if (!info || rate <= 0) return null;

    const pct = Math.round(rate * 100);
    const listPrice = Number(cheapest?.price || 0);
    const newPrice = listPrice > 0 ? Math.round(listPrice * (1 - rate)) : 0;

    const priceLine = listPrice > 0 && (
        <span className="inline-flex flex-wrap items-baseline gap-2" data-testid="insurance-campaign-price">
            <span className="text-sm text-muted-foreground line-through">
                {formatMoney(listPrice, cheapest.currency)}
            </span>
            <span className="font-heading text-xl font-extrabold text-[hsl(var(--brand-copper))]">
                {formatMoney(newPrice, cheapest.currency)}
            </span>
            <span className="text-xs font-semibold text-muted-foreground">
                {cheapest.validity_days} günlük poliçe · kişi başı
            </span>
        </span>
    );

    if (variant === "badge") {
        return (
            <span
                className="inline-flex items-center gap-1.5 rounded-full bg-[hsl(var(--gold))]/18 px-2.5 py-1 text-[11px] font-bold text-[hsl(var(--brand-copper))]"
                data-testid="insurance-campaign-badge"
            >
                <BadgePercent className="h-3.5 w-3.5" aria-hidden="true" />
                {info.card_badge || `Vize ile birlikte %${pct} indirim`}
            </span>
        );
    }

    if (variant === "card") {
        return (
            <div
                className={`rounded-xl border border-[hsl(var(--gold))]/45 bg-[hsl(var(--gold))]/[0.07] p-4 ${className}`}
                data-testid="insurance-campaign-card"
            >
                <p className="flex items-start gap-2 font-heading text-sm font-bold">
                    <BadgePercent className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--brand-copper))]" aria-hidden="true" />
                    {info.cross_sell_title || `Vizenizi de bizden alın, poliçede %${pct} indirim`}
                </p>
                <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                    {info.cross_sell_note}
                </p>
                <Button
                    asChild
                    variant="secondary"
                    className="mt-3 h-11 border border-border text-sm"
                    data-testid="insurance-campaign-card-cta"
                >
                    <Link to={info.cta_href || "/basvuru"}>
                        {info.cta_label || "Vize başvurusuna başla"}
                        <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                </Button>
            </div>
        );
    }

    return (
        <section className={`section pt-0 ${className}`} data-testid="insurance-campaign-band">
            <div className="container-page">
                <div
                    className="relative overflow-hidden rounded-[var(--radius-lg)] border border-[hsl(var(--gold))]/45 bg-[hsl(var(--gold))]/[0.08] p-5 sm:p-8"
                    style={{ boxShadow: "var(--shadow-card)" }}
                >
                    <div
                        className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full bg-[hsl(var(--gold))]/20 blur-2xl"
                        aria-hidden="true"
                    />
                    <div className="relative flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                        <div className="max-w-2xl">
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-[hsl(var(--brand-copper))] px-3 py-1 text-[11px] font-bold uppercase tracking-[0.14em] text-white">
                                <BadgePercent className="h-3.5 w-3.5" aria-hidden="true" /> Kampanya
                            </span>
                            <h2 className="mt-3 font-heading text-2xl font-extrabold leading-tight sm:text-3xl">
                                {info.campaign_title || `Vize + sigorta birlikte: poliçede %${pct} indirim`}
                            </h2>
                            <p className="mt-2.5 text-sm leading-6 text-muted-foreground sm:text-base sm:leading-7">
                                {info.campaign_note || info.note}
                            </p>
                            {priceLine && <p className="mt-3">{priceLine}</p>}
                        </div>

                        <div className="flex shrink-0 flex-col gap-2.5 sm:flex-row lg:flex-col">
                            <Button asChild className="h-12 px-7 text-base" data-testid="insurance-campaign-cta">
                                <Link to={info.cta_href || "/basvuru"}>
                                    {info.cta_label || "Vize başvurusuna başla"}
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                            <Button
                                asChild
                                variant="secondary"
                                className="h-12 border border-border px-6 text-base"
                                data-testid="insurance-campaign-detail"
                            >
                                <Link to="/seyahat-sigortasi">
                                    <ShieldCheck className="mr-2 h-4 w-4" /> Teminatları gör
                                </Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
