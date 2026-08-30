import React from "react";
import { Link } from "react-router-dom";
import { Check, Clock, Star } from "lucide-react";
import { Button } from "./ui/button";
import { formatMoney } from "../lib/site";

export const VisaTypeCard = ({ visa, onSelect, selected = false, compact = false }) => {
    const isPopular = !!visa.popular;
    return (
        <div
            data-testid={`visa-card-${visa.id}`}
            className={`relative flex h-full flex-col rounded-xl border bg-card p-6 transition-shadow duration-200 ${
                selected
                    ? "border-primary ring-2 ring-primary"
                    : isPopular
                      ? "border-primary/40 ring-1 ring-primary/30"
                      : "border-border"
            }`}
            style={{ boxShadow: isPopular || selected ? "var(--shadow-soft)" : "var(--shadow-card)" }}
        >
            {isPopular && (
                <span className="absolute -top-3 left-6 inline-flex items-center gap-1 rounded-full bg-primary px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-primary-foreground">
                    <Star className="h-3 w-3" /> En çok tercih edilen
                </span>
            )}

            <div className="flex items-start justify-between gap-3">
                <div>
                    <h3 className="font-heading text-xl font-bold">{visa.name}</h3>
                    <p className="mt-1 text-sm text-muted-foreground">{visa.entry_label}</p>
                </div>
                <span className="rounded-lg bg-[hsl(var(--sand-surface))] px-3 py-1.5 text-center">
                    <span className="block font-heading text-lg font-bold leading-none">{visa.duration_days}</span>
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">gün</span>
                </span>
            </div>

            <div className="mt-5 flex items-end gap-2">
                <span className="font-heading text-3xl font-bold tracking-tight" data-testid={`visa-price-${visa.id}`}>
                    {formatMoney(visa.price, visa.currency)}
                </span>
                <span className="pb-1 text-xs text-muted-foreground">/ kişi</span>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">Tüm masraflar dahil · Tek seferlik ödeme</p>

            <div className="mt-4 flex items-center gap-2 rounded-lg bg-[hsl(var(--cloud))] px-3 py-2 text-xs font-medium text-foreground/80">
                <Clock className="h-3.5 w-3.5 text-primary" />
                Sonuçlanma: {visa.processing_days}
            </div>

            {!compact && (
                <>
                    <p className="mt-4 text-sm leading-6 text-muted-foreground">{visa.description}</p>
                    <ul className="mt-4 space-y-2.5">
                        {(visa.features || []).map((f) => (
                            <li key={f} className="flex items-start gap-2 text-sm">
                                <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                <span>{f}</span>
                            </li>
                        ))}
                    </ul>
                </>
            )}

            <div className="mt-6 pt-2">
                {onSelect ? (
                    <Button
                        type="button"
                        onClick={() => onSelect(visa)}
                        variant={selected ? "default" : "secondary"}
                        className="h-11 w-full"
                        data-testid={`select-visa-${visa.id}`}
                    >
                        {selected ? "Seçildi" : "Bu vizeyi seç"}
                    </Button>
                ) : (
                    <Button asChild className="h-11 w-full" data-testid={`apply-visa-${visa.id}`}>
                        <Link to={`/basvuru?vize=${visa.id}`}>Başvuruya başla</Link>
                    </Button>
                )}
            </div>
        </div>
    );
};
