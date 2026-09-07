import React from "react";
import { Landmark, Lock, ShieldCheck } from "lucide-react";

const VisaMark = () => (
    <svg viewBox="0 0 48 16" className="h-4 w-12" role="img" aria-label="Visa">
        <text
            x="0"
            y="13"
            fill="#1A1F71"
            fontSize="15"
            fontWeight="800"
            fontStyle="italic"
            fontFamily="Figtree, sans-serif"
            letterSpacing="0.5"
        >
            VISA
        </text>
    </svg>
);

const MastercardMark = () => (
    <svg viewBox="0 0 46 24" className="h-5 w-9" role="img" aria-label="Mastercard">
        <circle cx="17" cy="12" r="10" fill="#EB001B" />
        <circle cx="29" cy="12" r="10" fill="#F79E1B" />
        <path d="M23 4.2a10 10 0 0 0 0 15.6 10 10 0 0 0 0-15.6z" fill="#FF5F00" />
    </svg>
);

const TroyMark = () => (
    <svg viewBox="0 0 52 16" className="h-4 w-12" role="img" aria-label="Troy">
        <text x="0" y="13" fill="#00A3A1" fontSize="14" fontWeight="800" fontFamily="Figtree, sans-serif">
            troy
        </text>
    </svg>
);

/**
 * Odeme guven seridi: 3D Secure, kabul edilen kart aglari ve havale secenegi.
 * Fiyat/sepet/odeme ekranlarinda tereddudu azaltmak icin kullanilir.
 */
export const PaymentTrustStrip = ({ className = "", compact = false }) => (
    <div
        className={`rounded-2xl border border-border bg-card px-5 py-4 ${className}`}
        style={{ boxShadow: "var(--shadow-card)" }}
        data-testid="payment-trust-strip"
    >
        <div className="flex flex-wrap items-center gap-x-7 gap-y-3">
            <span className="inline-flex items-center gap-2 text-sm font-bold text-foreground">
                <ShieldCheck className="h-4.5 w-4.5 text-[hsl(var(--brand-green))]" />
                3D Secure ile güvenli ödeme
            </span>
            <span className="inline-flex items-center gap-3" data-testid="payment-card-marks">
                <VisaMark />
                <MastercardMark />
                <TroyMark />
            </span>
            <span className="inline-flex items-center gap-2 text-sm text-muted-foreground">
                <Landmark className="h-4 w-4 text-primary" />
                Havale / EFT
            </span>
            <span className="inline-flex items-center gap-2 text-sm text-muted-foreground">
                <Lock className="h-4 w-4 text-primary" />
                Kart bilgileriniz tarafımızda saklanmaz
            </span>
        </div>
        {!compact && (
            <p className="mt-3 text-xs leading-5 text-muted-foreground">
                Kart ödemelerinde son onay bankanızın 3D Secure ekranında verilir. Ödeme altyapısı
                PCI-DSS sertifikalı sağlayıcı üzerinden çalışır; kart numaranız sunucularımıza hiç ulaşmaz.
            </p>
        )}
    </div>
);
