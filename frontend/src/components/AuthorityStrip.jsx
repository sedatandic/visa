import React, { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";
import { api } from "../lib/api";
import { GdrfaMark } from "./GdrfaBadge";

/** TÜRSAB resmi logosu */
const TursabMark = ({ className = "" }) => (
    <img
        src="/brand/tursab.png"
        alt="TÜRSAB - Türkiye Seyahat Acentaları Birliği"
        className={`${className} object-contain`}
        loading="lazy"
        decoding="async"
    />
);

/**
 * Ana sayfa guven seridi: basvurularin iletildigi yetkili merciler ve
 * acentenin uyelik bilgisi. Temsili amblemler kullanilir.
 */
export const AuthorityStrip = () => {
    const [agency, setAgency] = useState(null);

    useEffect(() => {
        api.get("/content/site")
            .then(({ data }) => setAgency(data.company || null))
            .catch(() => {});
    }, []);

    const items = [
        {
            key: "tursab",
            Mark: TursabMark,
            title: "TÜRSAB Üyesi",
            subtitle: agency?.tursab_type || "A Grubu Seyahat Acentesi",
            caption: agency?.tursab_no ? `Belge No: ${agency.tursab_no}` : "Türkiye Seyahat Acentaları Birliği",
        },
        {
            key: "gdrfa",
            Mark: GdrfaMark,
            title: "GDRFA Dubai",
            subtitle: "General Directorate of Residency and Foreigners Affairs",
            caption: "Dubai Göçmenlik ve Yabancılar Genel Müdürlüğü",
        },
    ];

    return (
        <section
            className="border-b border-border bg-[hsl(var(--cloud))] py-9"
            data-testid="landing-authorities"
            aria-labelledby="authorities-heading"
        >
            <div className="container-page">
                <div className="flex flex-col gap-1.5 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <span className="eyebrow">Yetkili Merciler</span>
                        <h2 id="authorities-heading" className="mt-2 text-lg font-bold sm:text-xl">
                            Başvurularınız resmî kanallar üzerinden iletilir
                        </h2>
                    </div>
                    <p className="flex items-start gap-2 text-xs leading-5 text-muted-foreground sm:max-w-sm">
                        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                        <span>
                            Dubai Vize Hattı bir seyahat acentesidir; resmî bir devlet kurumu değildir.
                            Amblemler yalnızca ilgili mercileri belirtmek için temsilîdir.
                        </span>
                    </p>
                </div>

                <ul className="mt-6 grid gap-4 sm:grid-cols-2">
                    {items.map(({ key, Mark, title, subtitle, caption }) => (
                        <li
                            key={key}
                            className="flex flex-col items-center gap-4 rounded-xl border border-border bg-card p-6 text-center transition-transform duration-200 hover:-translate-y-0.5 sm:flex-row sm:justify-center sm:gap-6 sm:text-left"
                            data-testid={`authority-item-${key}`}
                        >
                            <Mark className="h-24 w-36 shrink-0" />
                            <div className="min-w-0 leading-snug">
                                <p className="text-lg font-extrabold text-foreground">{title}</p>
                                <p className="mt-1 text-sm font-semibold text-muted-foreground">{subtitle}</p>
                                <p className="mt-1 text-sm text-muted-foreground/80">{caption}</p>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </section>
    );
};
