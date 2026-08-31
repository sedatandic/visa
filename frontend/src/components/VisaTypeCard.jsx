import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Check, Clock } from "lucide-react";
import { Button } from "./ui/button";
import { formatMoney } from "../lib/site";

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
            className={`relative flex h-full flex-col rounded-2xl border-2 bg-card p-6 pt-8 text-center transition-shadow duration-200 hover:shadow-[var(--shadow-soft)] focus-visible:outline-none ${
                clickable ? "cursor-pointer" : ""
            } ${
                selected
                    ? "border-primary"
                    : isPopular
                      ? "border-[hsl(var(--brand-red))]"
                      : "border-border hover:border-primary/50"
            }`}
            style={{ boxShadow: isPopular || selected ? "var(--shadow-soft)" : "var(--shadow-card)" }}
        >

            {isPopular && (
                <span className="absolute -top-3.5 left-1/2 z-[2] inline-flex -translate-x-1/2 items-center gap-1 whitespace-nowrap rounded-full bg-[hsl(var(--brand-red))] px-4 py-1.5 text-[11px] font-extrabold uppercase tracking-wider text-white">
                    En çok tercih edilen
                </span>
            )}

            <h3 className="font-heading text-xl font-extrabold leading-tight">{visa.name}</h3>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                {compact ? visa.entry_label : visa.description}
            </p>

            <div className="mt-5 flex items-end justify-center gap-2">
                <span
                    className="font-heading text-4xl font-extrabold tracking-tight text-[hsl(var(--brand-red))]"
                    data-testid={`visa-price-${visa.id}`}
                >
                    {formatMoney(visa.price, visa.currency)}
                </span>
                <span className="pb-1.5 text-sm text-muted-foreground">/ kişi başı</span>
            </div>

            <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs font-medium text-muted-foreground">
                <span className="inline-flex items-center gap-1.5 rounded-full bg-muted px-3 py-1">
                    {visa.duration_days} gün
                </span>
                <span className="inline-flex items-center gap-1.5 rounded-full bg-muted px-3 py-1">
                    <Clock className="h-3.5 w-3.5 text-primary" /> {visa.processing_days}
                </span>
            </div>

            {!compact && (
                <ul className="mt-6 space-y-2.5 text-left">
                    {(visa.features || []).map((f) => (
                        <li key={f} className="flex items-start gap-2 text-sm">
                            <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                            <span>{f}</span>
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
                        className="h-12 w-full text-base"
                        data-testid={`select-visa-${visa.id}`}
                    >
                        {selected ? "Seçildi" : "Bu vizeyi seç"}
                    </Button>
                ) : (
                    <>
                        <Button asChild className="h-12 w-full text-base" data-testid={`apply-visa-${visa.id}`}>
                            <Link to={`/basvuru?vize=${visa.id}`}>Başvuruya başla</Link>
                        </Button>
                        {visa.slug && (
                            <Link
                                to={`/dubai-vizesi/${visa.slug}`}
                                className="relative z-[2] mt-3 inline-flex w-full items-center justify-center gap-1.5 rounded-lg px-2 py-1.5 text-sm font-semibold text-primary underline-offset-4 transition-colors duration-150 hover:text-[hsl(var(--brand-red))] hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                                data-testid={`guide-link-${visa.id}`}
                            >
                                Detaylı rehberi oku <ArrowRight className="h-3.5 w-3.5" />
                            </Link>
                        )}
                    </>
                )}
            </div>
        </div>
    );
};
