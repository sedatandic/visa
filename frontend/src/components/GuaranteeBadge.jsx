import React from "react";
import { ShieldCheck, Clock } from "lucide-react";

const TITLE = "36 saat garantisi";
const SHORT = "Aşarsak ekspres ücreti bizden";
const LINE =
    "Belgeleriniz eksiksizse başvurunuz 36 saat içinde sonuçlanır. Bu süre aşılırsa ödediğiniz ekspres hizmet bedelini iade ediyoruz; ekspres almadıysanız başvurunuzu ücretsiz olarak ekspres sıraya alıyoruz.";
const TERMS =
    "Süre, belgeleriniz onaylanıp başvurunuz resmî mercilere iletildiği anda başlar. Resmî tatiller ile mercilerin ek belge veya inceleme talepleri süreye dahil değildir.";

export const GuaranteeBadge = ({ compact = false, className = "" }) => {
    if (compact) {
        return (
            <span
                className={`inline-flex items-center gap-2 rounded-full border border-[hsl(var(--brand-green)/0.4)] bg-[hsl(var(--brand-green)/0.1)] px-3.5 py-1.5 text-xs font-bold text-[hsl(var(--brand-green))] ${className}`}
                data-testid="guarantee-badge-compact"
                title={LINE}
            >
                <ShieldCheck className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                {TITLE}
                <span className="hidden font-semibold opacity-80 sm:inline">· {SHORT}</span>
            </span>
        );
    }

    return (
        <div
            className={`rounded-2xl border border-[hsl(var(--brand-green)/0.35)] bg-[hsl(var(--brand-green)/0.07)] p-5 sm:p-6 ${className}`}
            data-testid="guarantee-badge-card"
        >
            <div className="flex items-start gap-3.5">
                <span className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[hsl(var(--brand-green)/0.14)] text-[hsl(var(--brand-green))]">
                    <ShieldCheck className="h-5 w-5" aria-hidden="true" />
                </span>
                <div>
                    <h3
                        className="flex flex-wrap items-center gap-2 text-base font-bold text-foreground"
                        data-testid="guarantee-badge-title"
                    >
                        {TITLE}
                        <span className="inline-flex items-center gap-1 rounded-full bg-card px-2 py-0.5 text-[11px] font-bold uppercase tracking-wider text-[hsl(var(--brand-green))]">
                            <Clock className="h-3 w-3" aria-hidden="true" />
                            {SHORT}
                        </span>
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-foreground/80" data-testid="guarantee-badge-line">
                        {LINE}
                    </p>
                    <p className="mt-2 text-xs leading-5 text-muted-foreground" data-testid="guarantee-badge-terms">
                        {TERMS}
                    </p>
                </div>
            </div>
        </div>
    );
};
