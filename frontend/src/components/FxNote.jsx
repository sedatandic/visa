import React, { useEffect, useState } from "react";
import { RefreshCcw } from "lucide-react";
import { api } from "../lib/api";

const isToday = (iso) => {
    if (!iso) return false;
    const d = new Date(iso);
    const now = new Date();
    return (
        d.getDate() === now.getDate() &&
        d.getMonth() === now.getMonth() &&
        d.getFullYear() === now.getFullYear()
    );
};

const freshnessLabel = (iso) => {
    if (!iso) return "kur bilgisi alınıyor";
    if (isToday(iso)) return "kur bugün güncellendi";
    const hours = Math.round((Date.now() - new Date(iso).getTime()) / 3600000);
    if (hours < 48) return "kur dün güncellendi";
    return `kur ${Math.round(hours / 24)} gün önce güncellendi`;
};

/**
 * Kur seffafligi notu: musteriye fiyatin hangi kurla hesaplandigini gosterir.
 * variant="inline" -> tek satir metin, variant="badge" -> cerceveli rozet
 */
export const FxNote = ({ variant = "badge", className = "" }) => {
    const [fx, setFx] = useState(null);

    useEffect(() => {
        let cancelled = false;
        api.get("/fx")
            .then(({ data }) => {
                if (!cancelled) setFx(data);
            })
            .catch(() => {});
        return () => {
            cancelled = true;
        };
    }, []);

    if (!fx) return null;

    const rate = Number(fx.effective_rate).toLocaleString("tr-TR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
    const text = `1 $ = ${rate} ₺ · ${freshnessLabel(fx.fetched_at)}`;

    if (variant === "inline") {
        return (
            <span className={`text-xs text-muted-foreground ${className}`} data-testid="fx-note-inline">
                {text}
            </span>
        );
    }

    return (
        <span
            className={`inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-xs font-medium text-muted-foreground ${className}`}
            title={`Fiyatlar dolar bazlıdır ve güncel kurla TL'ye çevrilir. Son güncelleme: ${
                fx.fetched_at ? new Date(fx.fetched_at).toLocaleString("tr-TR") : "-"
            }`}
            data-testid="fx-note-badge"
        >
            <RefreshCcw className="h-3.5 w-3.5 text-primary" />
            {text}
        </span>
    );
};
