import React from "react";
import { Check, CheckCircle2, Minus, Plus } from "lucide-react";

import { Button } from "./ui/button";
import { formatMoney } from "../lib/site";

const BADGE_TONES = {
    primary: "bg-[hsl(var(--brand-green)/0.12)] text-[hsl(var(--brand-green))]",
    accent: "bg-primary/10 text-primary",
    neutral: "bg-muted text-muted-foreground",
};

const FIT_TONES = {
    ok: "text-[hsl(var(--brand-green))]",
    warn: "text-[hsl(var(--status-warning))]",
    neutral: "text-muted-foreground",
};

const OptionCard = ({ option, disabled, unitLabel, testId }) => {
    const {
        product,
        badges = [],
        discount,
        fit,
        highlight,
        features = [],
        dateNote,
        selected,
        qty,
        onSelect,
        onQtyChange,
    } = option;
    return (
        <div
            role="button"
            tabIndex={disabled ? -1 : 0}
            aria-pressed={selected}
            aria-disabled={disabled}
            onClick={() => !disabled && onSelect()}
            onKeyDown={(e) => {
                if (disabled || (e.key !== "Enter" && e.key !== " ")) return;
                e.preventDefault();
                onSelect();
            }}
            className={`flex flex-col rounded-2xl border p-4 text-left transition-[transform,border-color,box-shadow,background-color] duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                selected
                    ? "border-primary bg-primary/[0.06] shadow-[0_14px_34px_-22px_hsl(var(--primary)/0.6)]"
                    : "border-border bg-card hover:-translate-y-0.5 hover:border-primary/50"
            } ${disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}
            data-testid={testId}
        >
            <div className="mb-3 flex min-h-[22px] flex-wrap gap-1.5">
                {discount && (
                    <span
                        className="rounded-full bg-[hsl(var(--brand-green)/0.12)] px-2 py-0.5 text-[11px] font-semibold text-[hsl(var(--brand-green))]"
                        data-testid={`${testId}-discount-badge`}
                    >
                        {discount.label}
                    </span>
                )}
                {badges.map((b) => (
                    <span
                        key={b.label}
                        className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                            BADGE_TONES[b.tone] || BADGE_TONES.neutral
                        }`}
                        data-testid={b.testId}
                    >
                        {b.label}
                    </span>
                ))}
            </div>
            <div className="flex items-start justify-between gap-3">
                <div>
                    <p className="font-heading text-sm font-bold leading-5">{product.name}</p>
                    {highlight && (
                        <p className="mt-1 text-xs font-bold uppercase tracking-wide text-primary">
                            {highlight}
                        </p>
                    )}
                </div>
                {selected ? (
                    <CheckCircle2 className="h-5 w-5 shrink-0 text-primary" aria-hidden="true" />
                ) : (
                    <span
                        className="mt-0.5 h-5 w-5 shrink-0 rounded-full border border-border"
                        aria-hidden="true"
                    />
                )}
            </div>
            {fit && (
                <p
                    className={`mt-2.5 text-xs font-semibold leading-5 ${FIT_TONES[fit.tone] || FIT_TONES.neutral}`}
                    data-testid={`${testId}-fit`}
                >
                    {fit.text}
                </p>
            )}
            {features.length === 0 && product.summary && (
                <p className="mt-1.5 text-xs leading-5 text-muted-foreground">{product.summary}</p>
            )}
            {features.length > 0 && (
                <ul className="mt-2.5 space-y-1" data-testid={`${testId}-features`}>
                    {features.map((f) => (
                        <li key={f} className="flex items-start gap-2 text-xs leading-5 text-muted-foreground">
                            <Check
                                className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[hsl(var(--brand-green))]"
                                aria-hidden="true"
                            />
                            <span>{f}</span>
                        </li>
                    ))}
                </ul>
            )}
            <div className="flex-1" />
            {dateNote}
            {discount ? (
                <div className="mt-3">
                    <p className="font-heading text-base font-extrabold text-primary">
                        <span
                            className="mr-2 text-sm font-semibold text-muted-foreground line-through"
                            data-testid={`${testId}-list-price`}
                        >
                            {formatMoney(product.price, product.currency)}
                        </span>
                        <span data-testid={`${testId}-final-price`}>
                            {formatMoney(discount.finalPrice, product.currency)}
                        </span>
                        <span className="ml-1 text-xs font-semibold text-muted-foreground">/ {unitLabel}</span>
                    </p>
                    <p
                        className="mt-1 text-[11px] font-semibold text-[hsl(var(--brand-green))]"
                        data-testid={`${testId}-discount-note`}
                    >
                        Vize başvurunuzla birlikte alındığı için indirimli
                    </p>
                </div>
            ) : (
                <p className="mt-3 font-heading text-base font-extrabold text-primary">
                    {formatMoney(product.price, product.currency)}
                    <span className="ml-1 text-xs font-semibold text-muted-foreground">/ {unitLabel}</span>
                </p>
            )}
            {selected && onQtyChange && (
                <div
                    className="mt-3 flex items-center justify-between gap-2"
                    onClick={(e) => e.stopPropagation()}
                    data-testid={`${testId}-qty`}
                >
                    <div className="flex items-center gap-2">
                        <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            onClick={() => onQtyChange(-1)}
                            disabled={qty <= 1}
                            aria-label="Adet azalt"
                            data-testid={`${testId}-qty-minus`}
                        >
                            <Minus className="h-4 w-4" />
                        </Button>
                        <span
                            className="w-9 text-center font-heading text-sm font-bold"
                            data-testid={`${testId}-qty-value`}
                        >
                            {qty}
                        </span>
                        <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            onClick={() => onQtyChange(1)}
                            disabled={qty >= 10}
                            aria-label="Adet arttır"
                            data-testid={`${testId}-qty-plus`}
                        >
                            <Plus className="h-4 w-4" />
                        </Button>
                    </div>
                    <span className="text-xs font-semibold text-muted-foreground">adet</span>
                </div>
            )}
            <Button
                type="button"
                variant={selected ? "secondary" : "default"}
                className={`mt-3 h-10 w-full ${selected ? "border border-primary/40" : ""}`}
                disabled={disabled}
                onClick={(e) => {
                    e.stopPropagation();
                    onSelect();
                }}
                data-testid={`${testId}-button`}
            >
                {selected ? (
                    <>
                        <Check className="mr-1.5 h-4 w-4" /> Seçildi · Kaldır
                    </>
                ) : (
                    <>
                        <Plus className="mr-1.5 h-4 w-4" /> Bu paketi seç
                    </>
                )}
            </Button>
        </div>
    );
};

// Basvuru sihirbazinda sigorta / eSIM icin detayli aciklamali secenek kartlari.
export const ExtraOptions = ({
    title,
    subtitle,
    icon: Icon,
    options,
    disabled,
    unitLabel,
    note,
    footer,
    testId,
    optionTestIdPrefix,
}) => (
    <div className="mt-10" data-testid={testId}>
        <div className="flex items-center gap-2">
            {Icon && <Icon className="h-5 w-5 shrink-0 text-primary" aria-hidden="true" />}
            <h3 className="font-heading text-base font-bold">{title}</h3>
        </div>
        {subtitle && <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{subtitle}</p>}
        {note}
        <div
            className={`mt-4 grid gap-4 ${
                options.length === 1 ? "md:grid-cols-1" : options.length === 2 ? "md:grid-cols-2" : "md:grid-cols-3"
            }`}
        >
            {options.map((o) => (
                <OptionCard
                    key={o.id}
                    option={o}
                    disabled={disabled}
                    unitLabel={unitLabel}
                    testId={`${optionTestIdPrefix}-${o.id}`}
                />
            ))}
        </div>
        {footer}
    </div>
);
