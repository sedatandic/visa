import React from "react";
import { CheckCircle2, Users } from "lucide-react";
import { formatMoney } from "../lib/site";
import { Button } from "./ui/button";

const DEFAULT_TIERS = [{ min: 2, rate: 0.1 }];

/** Ozet kartinda aile indirimini canli gosterir: kac yolcuda ne kadar indirim var. */
export const FamilyDiscountMeter = ({
    tiers,
    travelerCount,
    pendingCount = 0,
    discountAmount = 0,
    currency = "TRY",
    onAddTraveler,
    canAddTraveler = true,
}) => {
    const sorted = [...(tiers?.length ? tiers : DEFAULT_TIERS)].sort((a, b) => a.min - b.min);
    const active = [...sorted].reverse().find((t) => travelerCount >= t.min) || null;
    const next = sorted.find((t) => travelerCount < t.min) || null;
    const target = next?.min || active?.min || sorted[0].min;
    const progress = Math.min(100, Math.round((travelerCount / target) * 100));
    const pct = (rate) => Math.round((rate || 0) * 100);

    return (
        <div
            className={`rounded-xl border p-4 ${
                active
                    ? "border-[hsl(var(--success)/0.35)] bg-[hsl(var(--success)/0.07)]"
                    : "border-dashed border-primary/40 bg-primary/[0.04]"
            }`}
            data-testid="family-discount-meter"
        >
            <div className="flex items-center justify-between gap-3">
                <p className="flex items-center gap-2 font-heading text-sm font-bold">
                    {active ? (
                        <CheckCircle2 className="h-4 w-4 text-[hsl(var(--success))]" />
                    ) : (
                        <Users className="h-4 w-4 text-primary" />
                    )}
                    Aile indirimi
                </p>
                {active && (
                    <span
                        className="rounded-full bg-[hsl(var(--success)/0.15)] px-2 py-0.5 text-[11px] font-bold text-[hsl(var(--success))]"
                        data-testid="family-discount-active-badge"
                    >
                        %{pct(active.rate)} aktif
                    </span>
                )}
            </div>

            {active ? (
                <p className="mt-2 text-sm leading-6 text-muted-foreground" data-testid="family-discount-active-text">
                    {travelerCount} yolcu ile %{pct(active.rate)} indirim uygulanıyor
                    {discountAmount > 0 ? (
                        <>
                            {" · "}
                            <strong className="text-[hsl(var(--success))]">
                                {formatMoney(discountAmount, currency)} tasarruf
                            </strong>
                        </>
                    ) : null}
                    .
                </p>
            ) : pendingCount > 0 ? (
                <p
                    className="mt-2 text-sm font-semibold leading-6 text-amber-700"
                    data-testid="family-discount-pending-text"
                >
                    {pendingCount} yolcunun pasaport veya vesikalık belgesi eksik. Aile indirimi, en az 2 yolcunun
                    pasaportu ve fotoğrafı yüklendiğinde uygulanır.
                </p>
            ) : (
                <p className="mt-2 text-sm leading-6 text-muted-foreground" data-testid="family-discount-progress-text">
                    <strong className="text-foreground">{Math.max(1, target - travelerCount)} yolcu daha</strong> ekleyin,
                    tüm vize bedellerinde %{pct(next?.rate || sorted[0].rate)} aile indirimi açılır.
                </p>
            )}

            <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-border">
                <div
                    className={`h-full rounded-full transition-all duration-500 ${
                        active ? "bg-[hsl(var(--success))]" : "bg-primary"
                    }`}
                    style={{ width: `${Math.max(8, progress)}%` }}
                />
            </div>

            <ul className="mt-3 space-y-1" data-testid="family-discount-tiers">
                {sorted.map((t) => {
                    const reached = travelerCount >= t.min;
                    return (
                        <li
                            key={t.min}
                            className={`flex items-center justify-between text-xs ${
                                reached ? "font-semibold text-[hsl(var(--success))]" : "text-muted-foreground"
                            }`}
                            data-testid={`family-discount-tier-${t.min}`}
                        >
                            <span>{t.min}+ yolcu</span>
                            <span>%{pct(t.rate)} indirim</span>
                        </li>
                    );
                })}
            </ul>

            {!active && pendingCount === 0 && canAddTraveler && onAddTraveler && (
                <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="mt-3 h-11 w-full sm:h-9"
                    onClick={onAddTraveler}
                    data-testid="family-discount-add-traveler"
                >
                    <Users className="mr-2 h-4 w-4" /> Yolcu ekle ve indirimi aç
                </Button>
            )}
        </div>
    );
};
