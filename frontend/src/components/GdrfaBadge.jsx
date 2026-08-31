import React from "react";

/**
 * GDRFA (General Directorate of Residency and Foreigners Affairs - Dubai)
 * referans rozeti (temsili tasarim). Resmi logo musteri tarafindan
 * saglandiginda /public klasorune eklenip bu bilesende kullanilabilir.
 *
 * NOT: Bu rozet, basvurularin iletildigi yetkili mercii belirtmek amaciyla
 * kullanilir. Sirket resmi bir devlet kurumu degildir.
 */
export const GdrfaBadge = ({ light = false, className = "" }) => (
    <div
        className={`inline-flex items-center gap-3 rounded-xl border px-3.5 py-2.5 ${
            light ? "border-white/20 bg-white/5" : "border-border bg-card"
        } ${className}`}
        data-testid="gdrfa-badge"
    >
        <GdrfaMark className="h-9 w-9 shrink-0" />
        <span className="leading-tight">
            <span
                className={`block text-[11px] font-bold uppercase tracking-wider ${
                    light ? "text-white/70" : "text-muted-foreground"
                }`}
            >
                Başvurular şu mercie iletilir
            </span>
            <span
                className={`block text-sm font-extrabold ${light ? "text-white" : "text-foreground"}`}
                data-testid="gdrfa-badge-title"
            >
                GDRFA Dubai
            </span>
            <span className={`block text-[11px] ${light ? "text-white/70" : "text-muted-foreground"}`}>
                General Directorate of Residency &amp; Foreigners Affairs
            </span>
        </span>
    </div>
);

/** Temsili GDRFA amblemi: sahin basi + kalkan silueti, BAE renkleriyle. */
export const GdrfaMark = ({ className = "" }) => (
    <svg
        viewBox="0 0 48 48"
        className={className}
        role="img"
        aria-label="General Directorate of Residency and Foreigners Affairs - Dubai"
    >
        <path
            d="M24 2 43 8v16c0 10.5-7.7 18.9-19 22C12.7 42.9 5 34.5 5 24V8L24 2z"
            fill="#00563F"
        />
        <path
            d="M24 5.6 39.6 10.6v13.4c0 8.8-6.4 15.9-15.6 18.7C14.8 39.9 8.4 32.8 8.4 24V10.6L24 5.6z"
            fill="none"
            stroke="#FFFFFF"
            strokeWidth="1.1"
            opacity="0.85"
        />
        {/* Sahin silueti */}
        <path
            d="M24 11.2c2.9 0 5.1 1.7 6 4.1l3.4-1.1-2.2 3 2.6 1.4-3.2.9c-.4 3.3-2.9 5.6-6.6 5.6s-6.2-2.3-6.6-5.6l-3.2-.9 2.6-1.4-2.2-3 3.4 1.1c.9-2.4 3.1-4.1 6-4.1z"
            fill="#FFFFFF"
        />
        <circle cx="21.4" cy="17.4" r="1.1" fill="#00563F" />
        <circle cx="26.6" cy="17.4" r="1.1" fill="#00563F" />
        {/* BAE bayragi seridi */}
        <rect x="14" y="29.4" width="20" height="2.2" fill="#00843D" />
        <rect x="14" y="31.6" width="20" height="2.2" fill="#FFFFFF" />
        <rect x="14" y="33.8" width="20" height="2.2" fill="#111111" />
        <rect x="14" y="29.4" width="4.4" height="6.6" fill="#C8102E" />
    </svg>
);
