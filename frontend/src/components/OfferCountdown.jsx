import React, { useEffect, useState } from "react";
import { Clock } from "lucide-react";

const remaining = (expiresAt) => {
    const end = new Date(expiresAt).getTime();
    if (Number.isNaN(end)) return null;
    return Math.max(0, end - Date.now());
};

const pad = (value) => String(value).padStart(2, "0");

const label = (ms) => {
    const total = Math.floor(ms / 1000);
    const days = Math.floor(total / 86400);
    const hours = Math.floor((total % 86400) / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const seconds = total % 60;
    if (days > 0) return `${days} gün ${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
};

/** Teklif sayfasindaki geri sayim: fiyatin ne kadar sure sabit kalacagini gosterir. */
export const OfferCountdown = ({ expiresAt }) => {
    const [left, setLeft] = useState(() => remaining(expiresAt));

    useEffect(() => {
        setLeft(remaining(expiresAt));
        const timer = setInterval(() => setLeft(remaining(expiresAt)), 1000);
        return () => clearInterval(timer);
    }, [expiresAt]);

    if (left === null) return null;

    if (left === 0) {
        return (
            <span
                className="inline-flex items-center gap-2 rounded-full border border-border bg-muted px-3 py-1.5 text-xs font-semibold text-muted-foreground"
                data-testid="offer-countdown"
            >
                <Clock className="h-3.5 w-3.5" /> Teklif süresi doldu
            </span>
        );
    }

    const urgent = left < 48 * 3600 * 1000;
    return (
        <span
            className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-bold ${
                urgent
                    ? "border-destructive/30 bg-destructive/10 text-destructive"
                    : "border-[hsl(var(--gold))]/45 bg-[hsl(var(--gold))]/[0.12] text-[hsl(var(--brand-copper))]"
            }`}
            data-testid="offer-countdown"
        >
            <Clock className={`h-3.5 w-3.5 ${urgent ? "animate-pulse" : ""}`} />
            <span>
                Bu fiyat <span data-testid="offer-countdown-time">{label(left)}</span> boyunca geçerli
            </span>
        </span>
    );
};
