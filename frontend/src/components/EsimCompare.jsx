import React, { useEffect, useState } from "react";
import { Check, Minus } from "lucide-react";
import { formatMoney } from "../lib/site";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ROWS = [
    { key: "data", label: "Veri" },
    { key: "validity", label: "Geçerlilik" },
    { key: "hotspot", label: "Hotspot (internet paylaşımı)" },
    { key: "coverage", label: "BAE genelinde 4G/5G" },
    { key: "keepNumber", label: "Türkiye numaranız açık kalır" },
    { key: "best", label: "Kimler için uygun?" },
];

const DATA = {
    esim_1gb: { data: "1 GB", validity: "7 gün", hotspot: false, best: "Kısa mola ve aktarmalar" },
    esim_3gb: { data: "3 GB", validity: "15 gün", hotspot: true, best: "Bir haftalık tatil (en çok tercih edilen)" },
    esim_10gb: { data: "10 GB", validity: "30 gün", hotspot: true, best: "Uzun kalış ve iş seyahati" },
    esim_unlimited: { data: "Sınırsız*", validity: "30 gün", hotspot: true, best: "Limit düşünmek istemeyenler" },
};

const Cell = ({ value }) => {
    if (value === true) return <Check className="h-4 w-4 text-[hsl(var(--brand-green))]" aria-hidden="true" />;
    if (value === false) return <Minus className="h-4 w-4 text-muted-foreground/60" aria-hidden="true" />;
    return <span>{value}</span>;
};

export const EsimCompare = () => {
    const [items, setItems] = useState([]);

    useEffect(() => {
        fetch(`${API}/products`)
            .then((r) => r.json())
            .then((d) => setItems((d.items || []).filter((p) => p.kind === "esim" && DATA[p.id])))
            .catch(() => setItems([]));
    }, []);

    if (!items.length) return null;

    return (
        <section className="section border-y border-border" data-testid="esim-compare">
            <div className="container-page">
                <span className="eyebrow">Paket karşılaştırma</span>
                <h2 className="mt-3 text-2xl font-bold">Hangi eSIM paketi size uygun?</h2>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
                    Tüm paketler BAE genelinde geçerlidir, QR kod ile 2 dakikada kurulur ve Türkiye
                    numaranız açık kalır. Aşağıdaki tabloda veri, süre ve hotspot farklarını
                    karşılaştırabilirsiniz.
                </p>

                <div className="mt-7 overflow-x-auto rounded-[var(--radius-lg)] border border-border bg-card">
                    <table className="w-full min-w-[680px] text-sm">
                        <thead>
                            <tr className="border-b border-border bg-[hsl(var(--cloud))] text-left">
                                <th className="px-5 py-4 text-xs font-bold uppercase tracking-[0.12em] text-muted-foreground">
                                    Paket
                                </th>
                                {items.map((p) => (
                                    <th key={p.id} className="px-5 py-4" data-testid={`esim-compare-head-${p.id}`}>
                                        <span className="block font-heading text-sm font-bold">
                                            {p.name.replace("Dubai eSIM · ", "")}
                                        </span>
                                        <span className="mt-1 block text-sm font-semibold text-primary">
                                            {formatMoney(p.price)}
                                        </span>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {ROWS.map((row) => (
                                <tr key={row.key} className="border-b border-border last:border-0">
                                    <th className="px-5 py-4 text-left font-heading text-sm font-semibold">
                                        {row.label}
                                    </th>
                                    {items.map((p) => {
                                        const meta = DATA[p.id];
                                        const value =
                                            row.key === "coverage" || row.key === "keepNumber"
                                                ? true
                                                : meta[row.key];
                                        return (
                                            <td
                                                key={p.id}
                                                className="px-5 py-4 text-muted-foreground"
                                                data-testid={`esim-compare-${row.key}-${p.id}`}
                                            >
                                                <Cell value={value} />
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <p className="mt-4 text-xs text-muted-foreground">
                    * Sınırsız pakette adil kullanım kotası aşıldığında hız düşer, bağlantı kesilmez.
                    Fiyatlar güncel dolar kuruna göre otomatik güncellenir.
                </p>
            </div>
        </section>
    );
};
