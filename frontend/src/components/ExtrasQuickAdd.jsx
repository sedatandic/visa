import React, { useState } from "react";
import { ChevronDown, Minus, Plus, ShieldCheck, Signal } from "lucide-react";
import { formatMoney } from "../lib/site";
import { Button } from "./ui/button";

/** Sihirbazin her adiminda gorunen hizli sigorta / eSIM ekleme paneli. */
export const ExtrasQuickAdd = ({
    insuranceProducts = [],
    esimProducts = [],
    insurancePick,
    onPickInsurance,
    esimQty = {},
    onChangeEsimQty,
}) => {
    const [open, setOpen] = useState(true);
    if (!insuranceProducts.length && !esimProducts.length) return null;

    return (
        <div className="card-surface p-5" data-testid="extras-quick-add">
            <button
                type="button"
                onClick={() => setOpen((v) => !v)}
                className="flex w-full items-center justify-between gap-3 text-left"
                data-testid="extras-quick-add-toggle"
            >
                <h3 className="font-heading text-base font-bold">Ekstraları ekle</h3>
                <ChevronDown
                    className={`h-4 w-4 text-muted-foreground transition-transform duration-200 ${
                        open ? "rotate-180" : ""
                    }`}
                    aria-hidden="true"
                />
            </button>
            <p className="mt-1.5 text-xs leading-5 text-muted-foreground">
                Sigorta + eSIM birlikte alındığında %10 paket indirimi otomatik uygulanır.
            </p>

            {open && (
                <div className="mt-4 space-y-5 border-t border-border pt-4">
                    {insuranceProducts.length > 0 && (
                        <div>
                            <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                                <ShieldCheck className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
                                Seyahat sigortası
                            </p>
                            <div className="mt-3 space-y-2">
                                {insuranceProducts.map((p) => {
                                    const on = insurancePick === p.id;
                                    return (
                                        <button
                                            type="button"
                                            key={p.id}
                                            onClick={() => onPickInsurance(on ? null : p.id)}
                                            data-testid={`quick-insurance-${p.id}`}
                                            className={`flex w-full items-center justify-between gap-2 rounded-lg border px-3 py-2 text-left text-xs transition-colors duration-150 ${
                                                on
                                                    ? "border-primary bg-primary/[0.06]"
                                                    : "border-border hover:border-primary/40"
                                            }`}
                                        >
                                            <span className="font-medium leading-4">
                                                {p.validity_days} gün ·{" "}
                                                {p.name.includes("Geniş") ? "Geniş kapsam" : "Temel"}
                                            </span>
                                            <span className="whitespace-nowrap font-heading font-bold text-[hsl(30_62%_38%)]">
                                                {formatMoney(p.price, p.currency)}
                                            </span>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {esimProducts.length > 0 && (
                        <div>
                            <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-muted-foreground">
                                <Signal className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
                                eSIM internet
                            </p>
                            <div className="mt-3 space-y-2">
                                {esimProducts.map((p) => {
                                    const qty = Number(esimQty[p.id] || 0);
                                    return (
                                        <div
                                            key={p.id}
                                            className={`flex items-center justify-between gap-2 rounded-lg border px-3 py-2 text-xs ${
                                                qty > 0 ? "border-primary bg-primary/[0.06]" : "border-border"
                                            }`}
                                            data-testid={`quick-esim-${p.id}`}
                                        >
                                            <span className="font-medium leading-4">
                                                {p.data_amount} · {p.validity_days} gün
                                                <span className="block font-heading font-bold text-[hsl(30_62%_38%)]">
                                                    {formatMoney(p.price, p.currency)}
                                                </span>
                                            </span>
                                            <span className="flex items-center gap-1">
                                                <Button
                                                    type="button"
                                                    variant="outline"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={() => onChangeEsimQty(p.id, -1)}
                                                    disabled={qty <= 0}
                                                    aria-label="Adet azalt"
                                                    data-testid={`quick-esim-minus-${p.id}`}
                                                >
                                                    <Minus className="h-3 w-3" />
                                                </Button>
                                                <span
                                                    className="w-5 text-center font-heading text-xs font-bold"
                                                    data-testid={`quick-esim-qty-${p.id}`}
                                                >
                                                    {qty}
                                                </span>
                                                <Button
                                                    type="button"
                                                    variant="outline"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={() => onChangeEsimQty(p.id, 1)}
                                                    disabled={qty >= 10}
                                                    aria-label="Adet arttır"
                                                    data-testid={`quick-esim-plus-${p.id}`}
                                                >
                                                    <Plus className="h-3 w-3" />
                                                </Button>
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
