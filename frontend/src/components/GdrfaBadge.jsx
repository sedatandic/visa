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
        <GdrfaMark
            className={`h-9 w-10 shrink-0 ${light ? "rounded-md bg-white px-1 py-0.5" : ""}`}
        />
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

/** GDRFA / Federal Authority resmi amblemi (şahin). */
export const GdrfaMark = ({ className = "" }) => (
    <img
        src="/brand/gdrfa.png"
        alt="Federal Authority for Identity, Citizenship, Customs & Port Security"
        className={`${className} object-contain`}
        loading="lazy"
        decoding="async"
    />
);
