import React from "react";
import { Check, Plus, Star } from "lucide-react";
import { Button } from "./ui/button";
import { formatMoney } from "../lib/site";

// Odeme adiminda sunulan ekstra hizmet onerileri (sigorta + eSIM + col safarisi).
export const TripSuggestions = ({ suggestions, tripDays, bundleActive }) => (
    <div className="mt-10" data-testid="trip-suggestions">
        <div className="flex items-center gap-2">
            <Star className="h-4.5 w-4.5 text-primary" aria-hidden="true" />
            <h3 className="font-heading text-base font-bold">Ekstra hizmetler</h3>
        </div>
        <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
            {tripDays
                ? `${tripDays} günlük Dubai seyahatiniz için seçtik.`
                : "Seyahat planınıza göre seçtik."}{" "}
            Ödemeden önce dilediğinizi ekleyin; istediğinizi tek tıkla kaldırabilirsiniz.
        </p>
        <div className="mt-4 grid gap-4 sm:grid-cols-3">
            {suggestions.map((s) => {
                const Icon = s.icon;
                return (
                    <div
                        key={s.key}
                        className={`flex flex-col rounded-xl border p-5 transition-colors duration-200 ${
                            s.selected
                                ? "border-primary bg-primary/[0.06]"
                                : "border-border bg-card hover:border-primary/50"
                        }`}
                        data-testid={`suggestion-card-${s.key}`}
                    >
                        {s.image && (
                            <div className="-mx-5 -mt-5 mb-4 overflow-hidden rounded-t-xl">
                                <img
                                    src={s.image}
                                    alt={s.product.name}
                                    loading="lazy"
                                    decoding="async"
                                    className="h-32 w-full object-cover transition-transform duration-500 hover:scale-105"
                                    data-testid={`suggestion-image-${s.key}`}
                                />
                            </div>
                        )}
                        <div className="flex items-center gap-2">
                            <Icon className="h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                            <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                                {s.label}
                            </span>
                        </div>
                        <p className="mt-2.5 font-heading text-sm font-bold">{s.product.name}</p>
                        <div className="flex-1">
                            <p
                                className="mt-1.5 text-xs leading-5 text-muted-foreground"
                                data-testid={`suggestion-meta-${s.key}`}
                            >
                                {s.meta}
                            </p>
                            <p
                                className="mt-3 font-heading text-base font-extrabold text-primary"
                                data-testid={`suggestion-price-${s.key}`}
                            >
                                {formatMoney(s.product.price, s.product.currency)}
                                <span className="ml-1 text-xs font-semibold text-muted-foreground">
                                    / {s.unit}
                                </span>
                            </p>
                        </div>
                        <Button
                            type="button"
                            variant={s.selected ? "secondary" : "default"}
                            className={`mt-4 h-10 w-full ${s.selected ? "border border-primary/40" : ""}`}
                            onClick={s.onToggle}
                            data-testid={`suggestion-toggle-${s.key}`}
                        >
                            {s.selected ? (
                                <>
                                    <Check className="mr-1.5 h-4 w-4" /> Eklendi · Kaldır
                                </>
                            ) : (
                                <>
                                    <Plus className="mr-1.5 h-4 w-4" /> Ekle
                                </>
                            )}
                        </Button>
                    </div>
                );
            })}
        </div>
        {bundleActive && (
            <p
                className="mt-3 rounded-lg bg-[hsl(var(--brand-green))]/10 px-3.5 py-2.5 text-xs font-bold leading-5 text-[hsl(var(--brand-green))]"
                data-testid="suggestions-bundle-note"
            >
                Sigorta + eSIM birlikte seçildi: %10 paket indirimi toplama otomatik uygulanır.
            </p>
        )}
    </div>
);
