import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Check, Clock, Zap } from "lucide-react";
import { Button } from "./ui/button";
import { formatMoney, formatUsd } from "../lib/site";

// Ek hizmet karti: vize ozet kartlariyla ayni duzen (serit, fiyat kutusu, ozellikler, CTA)
export const AddonCard = ({
    addon,
    badge = "Öncelikli sıra",
    badgeIcon: BadgeIcon = Zap,
    note = "Başvuru formunun 2. adımında seçilir",
    cta = "Başvuruya başla",
    to = "/basvuru",
}) => (
    <div
        data-testid={`addon-card-${addon.id}`}
        className="group relative flex h-full flex-col overflow-hidden rounded-[var(--radius-lg)] border border-border bg-card transition-[box-shadow,border-color,transform] duration-200 hover:-translate-y-0.5 hover:border-foreground/20 hover:shadow-[var(--shadow-soft)]"
        style={{ boxShadow: "var(--shadow-card)" }}
    >
        <span className="h-1 w-full shrink-0 bg-border" aria-hidden="true" />

        <div className="flex flex-1 flex-col p-6">
            <div className="flex h-6 items-center">
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                    Ek hizmet
                </span>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-1.5">
                <span className="inline-flex items-center gap-1 rounded-full bg-secondary px-2 py-1 text-[11px] font-bold uppercase tracking-wide text-primary">
                    <BadgeIcon className="h-3 w-3" aria-hidden="true" /> {badge}
                </span>
                <span className="inline-flex items-center rounded-md bg-muted px-2 py-1 text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
                    Kişi başı
                </span>
            </div>

            <h3 className="mt-3.5 font-heading text-lg font-extrabold leading-snug text-[hsl(30_62%_38%)]">
                {addon.name}
            </h3>
            <p className="mt-2 min-h-12 text-sm leading-6 text-muted-foreground sm:min-h-[3rem]">
                {addon.description}
            </p>

            <div className="mt-5 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                <div className="flex flex-wrap items-end gap-x-2">
                    <span
                        className="tabular whitespace-nowrap font-heading text-[26px] font-extrabold leading-none tracking-tight text-[hsl(30_62%_38%)] xl:text-[28px]"
                        data-testid={`addon-price-${addon.id}`}
                    >
                        {formatMoney(addon.price, addon.currency)}
                    </span>
                    <span className="whitespace-nowrap pb-0.5 text-xs font-semibold text-muted-foreground">
                        / kişi başı
                    </span>
                </div>
                {addon.price_usd ? (
                    <p className="mt-1.5 font-mono-code text-[11px] text-muted-foreground">
                        {formatUsd(addon.price_usd)} · güncel kurla TL tahsil
                    </p>
                ) : null}
                <p className="mt-2.5 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                    <Clock className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
                    {note}
                </p>
            </div>

            <ul className="mt-5 space-y-2.5">
                {(addon.features || []).map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm">
                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                        <span className="text-foreground/85">{f}</span>
                    </li>
                ))}
            </ul>

            <div className="mt-auto pt-6">
                <Button asChild className="h-12 w-full text-base" data-testid={`addon-apply-${addon.id}`}>
                    <Link to={to}>
                        {cta}
                        <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5" />
                    </Link>
                </Button>
            </div>
        </div>
    </div>
);
