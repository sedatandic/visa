import React from "react";

/**
 * TURSAB uyelik rozeti (temsili). Resmi TURSAB logosu musteri tarafindan
 * saglandiginda /public klasorune eklenip bu bilesende kullanilabilir.
 */
export const TursabBadge = ({ number = "0000", type = "A Grubu Seyahat Acentesi", light = false, className = "" }) => (
    <div
        className={`inline-flex items-center gap-3 rounded-xl border px-3.5 py-2.5 ${
            light ? "border-white/20 bg-white/5" : "border-border bg-card"
        } ${className}`}
        data-testid="tursab-badge"
    >
        <svg viewBox="0 0 48 48" className="h-9 w-9 shrink-0" role="img" aria-label="TÜRSAB">
            <circle cx="24" cy="24" r="23" fill="#0B6B3A" />
            <circle cx="24" cy="24" r="18.5" fill="none" stroke="#FFFFFF" strokeWidth="1.6" />
            <path
                d="M24 9c6 5 9 10 9 15s-3 10-9 15c-6-5-9-10-9-15s3-10 9-15z"
                fill="none"
                stroke="#FFFFFF"
                strokeWidth="1.4"
            />
            <path d="M6 24h36" stroke="#FFFFFF" strokeWidth="1.4" />
            <text
                x="24"
                y="28.5"
                textAnchor="middle"
                fill="#FFFFFF"
                fontSize="9.5"
                fontWeight="700"
                fontFamily="Figtree, sans-serif"
            >
                TÜRSAB
            </text>
        </svg>
        <span className="leading-tight">
            <span className={`block text-[11px] font-bold uppercase tracking-wider ${light ? "text-white/70" : "text-muted-foreground"}`}>
                TÜRSAB Üyesi
            </span>
            <span className={`block text-sm font-extrabold ${light ? "text-white" : "text-foreground"}`} data-testid="tursab-number">
                Belge No: {number}
            </span>
            <span className={`block text-[11px] ${light ? "text-white/70" : "text-muted-foreground"}`}>{type}</span>
        </span>
    </div>
);
