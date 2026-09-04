import React from "react";
import { Check, Plane, ShieldCheck, Signal } from "lucide-react";

const OPTIONS = [
    { id: "visa", label: "Sadece vize", icons: [Plane], insurance: false, esim: false },
    { id: "visa_esim", label: "Vize + eSIM", icons: [Plane, Signal], insurance: false, esim: true },
    {
        id: "visa_ins",
        label: "Vize + sigorta",
        icons: [Plane, ShieldCheck],
        insurance: true,
        esim: false,
    },
    {
        id: "visa_all",
        label: "Vize + eSIM + sigorta",
        icons: [Plane, Signal, ShieldCheck],
        insurance: true,
        esim: true,
        badge: "%10 indirim",
    },
];

/** Musterinin ne almak istedigini tek dokunusla belirledigi kombinasyon secici. */
export const ComboSelector = ({ hasInsurance, hasEsim, onChange }) => {
    const activeId = OPTIONS.find(
        (o) => o.insurance === hasInsurance && o.esim === hasEsim
    )?.id;

    return (
        <div className="mt-8" data-testid="combo-selector">
            <h3 className="font-heading text-base font-bold">Ne almak istiyorsunuz?</h3>
            <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                Seçiminize göre ekstraları hazırlayalım; her zaman aşağıdan değiştirebilirsiniz.
            </p>
            <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {OPTIONS.map((o) => {
                    const on = activeId === o.id;
                    return (
                        <button
                            type="button"
                            key={o.id}
                            onClick={() => onChange(o)}
                            data-testid={`combo-option-${o.id}`}
                            className={`flex h-full flex-col gap-2 rounded-xl border-2 p-4 text-left transition-colors duration-150 ${
                                on
                                    ? "border-primary bg-primary/[0.05]"
                                    : "border-border bg-card hover:border-primary/40"
                            }`}
                        >
                            <span className="flex items-center gap-1.5">
                                {o.icons.map((Icon, i) => (
                                    <Icon key={i} className="h-4 w-4 text-primary" aria-hidden="true" />
                                ))}
                                {on && (
                                    <Check className="ml-auto h-4 w-4 text-primary" aria-hidden="true" />
                                )}
                            </span>
                            <span className="text-sm font-bold leading-snug">{o.label}</span>
                            {o.badge && (
                                <span className="w-fit rounded-full bg-[hsl(var(--cream-tag))] px-2 py-0.5 text-[11px] font-bold">
                                    {o.badge}
                                </span>
                            )}
                        </button>
                    );
                })}
            </div>
        </div>
    );
};
