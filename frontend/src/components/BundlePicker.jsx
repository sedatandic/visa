import React from "react";
import { Check, Package, Sparkles } from "lucide-react";
import { formatMoney } from "../lib/site";

/** Vize suresine gore hazir sigorta + eSIM paketleri. */
export const BundlePicker = ({ bundles, selectedId, onSelect, visaDays }) => {
    if (!bundles?.length) return null;

    return (
        <div className="mt-10" data-testid="apply-bundle-picker">
            <h3 className="flex items-center gap-2 font-heading text-base font-bold">
                <Package className="h-4 w-4 text-primary" aria-hidden="true" />
                {visaDays ? `${visaDays} günlük vizeniz için hazır paketler` : "Hazır seyahat paketleri"}
            </h3>
            <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                Sigorta ve eSIM birlikte; paket indirimi fiyata dahil. Tek tıkla ekleyin,
                istersen aşağıdan tek tek de seçebilirsiniz.
            </p>

            <div className="mt-5 grid gap-4 md:grid-cols-3">
                {bundles.map((b) => {
                    const active = selectedId === b.id;
                    return (
                        <button
                            type="button"
                            key={b.id}
                            onClick={() => onSelect(b)}
                            data-testid={`bundle-option-${b.id}`}
                            className={`flex h-full flex-col rounded-2xl border-2 p-5 text-left transition-colors duration-150 ${
                                active
                                    ? "border-primary bg-primary/[0.05]"
                                    : "border-border bg-card hover:border-primary/40"
                            }`}
                        >
                            <div className="flex items-start justify-between gap-2">
                                <p className="font-heading text-sm font-bold">{b.name}</p>
                                {b.popular && (
                                    <span className="inline-flex items-center gap-1 rounded-full bg-[hsl(var(--cream-tag))] px-2.5 py-1 text-[11px] font-bold text-foreground">
                                        <Sparkles className="h-3 w-3" aria-hidden="true" /> En çok seçilen
                                    </span>
                                )}
                            </div>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">{b.tagline}</p>

                            <ul className="mt-4 space-y-2 text-sm">
                                <li className="flex items-start gap-2">
                                    <Check className="mt-1 h-3.5 w-3.5 shrink-0 text-primary" aria-hidden="true" />
                                    <span>
                                        {b.insurance.name}
                                        <span className="block text-xs text-muted-foreground">
                                            {b.insurance.coverage}
                                        </span>
                                    </span>
                                </li>
                                <li className="flex items-start gap-2">
                                    <Check className="mt-1 h-3.5 w-3.5 shrink-0 text-primary" aria-hidden="true" />
                                    <span>
                                        {b.esim.name}
                                        <span className="block text-xs text-muted-foreground">
                                            {b.esim.data_amount} veri · {b.esim.validity_days} gün
                                        </span>
                                    </span>
                                </li>
                            </ul>

                            <div className="mt-auto pt-5">
                                <p className="text-xs text-muted-foreground line-through">
                                    {formatMoney(b.list_total, b.currency)}
                                </p>
                                <p
                                    className="font-heading text-2xl font-extrabold leading-none text-[hsl(30_62%_38%)]"
                                    data-testid={`bundle-price-${b.id}`}
                                >
                                    {formatMoney(b.price, b.currency)}
                                </p>
                                <p className="mt-1 text-xs font-semibold text-[hsl(var(--brand-green))]">
                                    {formatMoney(b.discount, b.currency)} tasarruf
                                </p>
                                <span
                                    className={`mt-3 inline-flex h-9 w-full items-center justify-center rounded-lg text-sm font-semibold ${
                                        active
                                            ? "bg-primary text-primary-foreground"
                                            : "border border-border text-foreground"
                                    }`}
                                >
                                    {active ? "Pakete eklendi" : "Bu paketi ekle"}
                                </span>
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
};
