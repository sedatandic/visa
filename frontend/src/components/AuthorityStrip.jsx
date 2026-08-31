import React, { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";
import { api } from "../lib/api";
import { GdrfaMark } from "./GdrfaBadge";

const ICP_ITEM = {
    key: "icp",
    title: "ICP",
    subtitle: "Federal Authority for Identity & Citizenship",
    caption: "Federal kimlik ve vatandaşlık otoritesi",
};

/** Temsili ICP amblemi */
const IcpMark = ({ className = "" }) => (
    <svg viewBox="0 0 48 48" className={className} role="img" aria-label="ICP UAE">
        <circle cx="24" cy="24" r="22" fill="#0B2E4F" />
        <circle cx="24" cy="24" r="17.5" fill="none" stroke="#FFFFFF" strokeWidth="1.2" opacity="0.8" />
        <path d="M24 12.5c4.6 2.4 7.6 5.6 9 9.6-1.4 6.3-4.4 10.4-9 13-4.6-2.6-7.6-6.7-9-13 1.4-4 4.4-7.2 9-9.6z" fill="#FFFFFF" />
        <path d="M19.6 24.2l3.1 3.2 5.9-6.6" fill="none" stroke="#0B2E4F" strokeWidth="2.2" strokeLinecap="round" />
    </svg>
);

/** Temsili TÜRSAB amblemi (rozetteki ile ayni dil) */
const TursabMark = ({ className = "" }) => (
    <svg viewBox="0 0 48 48" className={className} role="img" aria-label="TÜRSAB">
        <circle cx="24" cy="24" r="22" fill="#0B6B3A" />
        <circle cx="24" cy="24" r="17.5" fill="none" stroke="#FFFFFF" strokeWidth="1.4" />
        <path
            d="M24 9.5c5.7 4.8 8.6 9.5 8.6 14.5S29.7 33.7 24 38.5c-5.7-4.8-8.6-9.5-8.6-14.5s2.9-9.7 8.6-14.5z"
            fill="none"
            stroke="#FFFFFF"
            strokeWidth="1.3"
        />
        <path d="M6.5 24h35" stroke="#FFFFFF" strokeWidth="1.3" />
        <text
            x="24"
            y="27.8"
            textAnchor="middle"
            fill="#FFFFFF"
            fontSize="8.6"
            fontWeight="700"
            fontFamily="Figtree, sans-serif"
        >
            TÜRSAB
        </text>
    </svg>
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
            key: "gdrfa",
            Mark: GdrfaMark,
            title: "GDRFA Dubai",
            subtitle: "General Directorate of Residency and Foreigners Affairs",
            caption: "Dubai Göçmenlik ve Yabancılar Genel Müdürlüğü",
        },
        {
            key: ICP_ITEM.key,
            Mark: IcpMark,
            title: ICP_ITEM.title,
            subtitle: ICP_ITEM.subtitle,
            caption: ICP_ITEM.caption,
        },
        {
            key: "tursab",
            Mark: TursabMark,
            title: "TÜRSAB Üyesi",
            subtitle: agency?.tursab_type || "A Grubu Seyahat Acentesi",
            caption: agency?.tursab_no ? `Belge No: ${agency.tursab_no}` : "Türkiye Seyahat Acentaları Birliği",
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
                            VizeAtlas Dubai bir seyahat acentesidir; resmî bir devlet kurumu değildir.
                            Amblemler yalnızca ilgili mercileri belirtmek için temsilîdir.
                        </span>
                    </p>
                </div>

                <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {items.map(({ key, Mark, title, subtitle, caption }) => (
                        <li
                            key={key}
                            className="flex items-center gap-4 rounded-xl border border-border bg-card p-4 transition-transform duration-200 hover:-translate-y-0.5"
                            data-testid={`authority-item-${key}`}
                        >
                            <Mark className="h-11 w-11 shrink-0" />
                            <div className="min-w-0 leading-tight">
                                <p className="text-sm font-extrabold text-foreground">{title}</p>
                                <p className="mt-0.5 text-[11px] font-semibold text-muted-foreground">{subtitle}</p>
                                <p className="mt-0.5 text-[11px] text-muted-foreground/80">{caption}</p>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </section>
    );
};
