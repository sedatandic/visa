import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Check, Clock, Star } from "lucide-react";
import { Button } from "./ui/button";
import { formatMoney, formatUsd } from "../lib/site";

export const VisaTypeCard = ({ visa, onSelect, selected = false, compact = false }) => {
    const isPopular = !!visa.popular;

    // Kart yalnizca secim modunda (basvuru formu) tiklanabilir; bilgilendirme
    // sayfalarinda kullanicinin istemeden forma yonlendirilmesini engellemek icin
    // yalnizca "Basvuruya basla" butonu yonlendirir.
    const clickable = !!onSelect;

    return (
        <div
            data-testid={`visa-card-${visa.id}`}
            role={clickable ? "button" : undefined}
            tabIndex={clickable ? 0 : undefined}
            aria-label={clickable ? `${visa.name} vizesini seç` : undefined}
            onClick={clickable ? (e) => {
                if (e.target.closest("a,button")) return;
                onSelect(visa);
            } : undefined}
            onKeyDown={clickable ? (e) => {
                if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    if (e.target.closest("a,button")) return;
                    onSelect(visa);
                }
            } : undefined}
            className={`group relative flex h-full flex-col overflow-hidden rounded-[var(--radius-lg)] border bg-card transition-[box-shadow,border-color,transform] duration-200 hover:-translate-y-0.5 hover:shadow-[var(--shadow-soft)] focus-visible:outline-none ${
                clickable ? "cursor-pointer" : ""
            } ${
                selected
                    ? "border-primary ring-2 ring-primary/25"
                    : isPopular
                      ? "border-foreground/25 ring-1 ring-foreground/10"
                      : "border-border hover:border-foreground/20"
            }`}
            style={{ boxShadow: isPopular || selected ? "var(--shadow-soft)" : "var(--shadow-card)" }}
        >
            <span
                className={`h-1 w-full shrink-0 ${
                    selected
                        ? "bg-primary"
                        : isPopular
                          ? "bg-primary"
                          : "bg-border"
                }`}
                aria-hidden="true"
            />

            <div className="flex flex-1 flex-col p-6">
                <div className="flex h-6 items-center">
                    {isPopular ? (
                        <span className="inline-flex items-center gap-1 whitespace-nowrap rounded-full bg-[hsl(var(--cream-tag)/0.35)] px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-wider text-foreground">
                            <Star className="h-3 w-3 fill-current" aria-hidden="true" /> En çok tercih edilen
                        </span>
                    ) : (
                        <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                            {visa.applicant_type === "child" ? "Çocuk vizesi" : "Dubai vizesi"}
                        </span>
                    )}
                </div>

                <div className="mt-3 flex flex-wrap items-center gap-1.5">
                    <span className="inline-flex items-center rounded-full bg-secondary px-2 py-1 text-[11px] font-bold uppercase tracking-wide text-primary">
                        {visa.duration_days} gün
                    </span>
                    {visa.entry_label && (
                        <span className="inline-flex items-center rounded-md bg-muted px-2 py-1 text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
                            {visa.entry_label}
                        </span>
                    )}
                </div>

                <h3 className="mt-3.5 font-heading text-lg font-extrabold leading-snug">{visa.name}</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {compact ? visa.entry_label : visa.description}
                </p>

                <div className="mt-5 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                    <div className="flex items-end gap-2">
                        <span
                            className="tabular font-heading text-[32px] font-extrabold leading-none tracking-tight text-foreground"
                            data-testid={`visa-price-${visa.id}`}
                        >
                            {formatMoney(visa.price, visa.currency)}
                        </span>
                        <span className="pb-0.5 text-xs font-semibold text-muted-foreground">/ kişi başı</span>
                    </div>
                    {visa.price_usd ? (
                        <p
                            className="mt-1.5 font-mono-code text-[11px] text-muted-foreground"
                            data-testid={`visa-price-usd-${visa.id}`}
                        >
                            {formatUsd(visa.price_usd)} · güncel kurla TL tahsil
                        </p>
                    ) : null}
                    <p className="mt-2.5 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                        <Clock className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
                        {visa.processing_days}
                    </p>
                </div>

                {!compact && (
                    <ul className="mt-5 space-y-2.5">
                        {(visa.features || []).map((f) => (
                            <li key={f} className="flex items-start gap-2 text-sm">
                                <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                <span className="text-foreground/85">{f}</span>
                            </li>
                        ))}
                    </ul>
                )}

                <div className="mt-auto pt-6">
                    {onSelect ? (
                        <Button
                            type="button"
                            onClick={() => onSelect(visa)}
                            variant={selected ? "default" : "secondary"}
                            className={`h-12 w-full text-base ${selected ? "" : "border border-border"}`}
                            data-testid={`select-visa-${visa.id}`}
                        >
                            {selected ? "Seçildi" : "Bu vizeyi seç"}
                        </Button>
                    ) : (
                        <>
                            <Button asChild className="h-12 w-full text-base" data-testid={`apply-visa-${visa.id}`}>
                                <Link to={`/basvuru?vize=${visa.id}`}>
                                    Başvuruya başla
                                    <ArrowRight className="ml-2 h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5" />
                                </Link>
                            </Button>
                            {visa.slug && (
                                <Link
                                    to={`/dubai-vizesi/${visa.slug}`}
                                    className="relative z-[2] mt-3 inline-flex w-full items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-sm font-semibold text-primary underline-offset-4 transition-colors duration-150 hover:text-foreground hover:underline focus-visible:outline-none"
                                    data-testid={`guide-link-${visa.id}`}
                                >
                                    Detaylı rehberi oku <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
                                </Link>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};
