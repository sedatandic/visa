import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Star } from "lucide-react";
import { Button } from "./ui/button";
import { applyPath, formatMoney, formatUsd } from "../lib/site";

// Hangi vize kime uygun: fiyat/sure disindaki karar kriteri
const FIT = {
    visa_30_single: "1–30 gün arası tek seferlik tatil ve ziyaretler",
    visa_60_single: "31–60 gün kalacak uzun tatil ve aile ziyaretleri",
    visa_30_multi: "30 gün içinde Umman, Katar gibi ülkelere çıkıp Dubai'ye dönecekler",
    visa_60_multi: "60 gün boyunca birden fazla giriş yapacak iş seyahatleri",
};

const ROWS = [
    { key: "duration", label: "Kalış süresi", value: (v) => `${v.duration_days} gün` },
    {
        key: "entry",
        label: "Giriş sayısı",
        value: (v) => (v.entry_type === "multiple" ? "Çok giriş" : "Tek giriş"),
    },
    {
        key: "exit",
        label: "Ülke dışına çıkış",
        value: (v) =>
            v.entry_type === "multiple"
                ? "Süre boyunca serbest giriş-çıkış"
                : "Çıkış yaptığınızda vize sona erer",
    },
    {
        key: "price",
        label: "Yetişkin ücreti",
        value: (v) => formatMoney(v.price, v.currency),
        sub: (v) => (v.price_usd ? `${formatUsd(v.price_usd)} · güncel kurla TL tahsil` : ""),
        strong: true,
    },
    {
        key: "child",
        label: "Çocuk ücreti (0-17 yaş)",
        value: (v, ctx) => {
            const child = ctx.childFor(v);
            return child ? formatMoney(child.price, child.currency) : "Çocuk vizesi tek girişlidir";
        },
        subNoWrap: true,
        sub: (v, ctx) => {
            const child = ctx.childFor(v);
            if (!child) return `${v.duration_days} günlük tek girişli çocuk vizesi ile başvurulur`;
            const save = Math.round((1 - Number(child.price) / Number(v.price)) * 100);
            return save > 0 ? `Yetişkin ücretine göre %${save} daha ucuz` : "";
        },
    },
    { key: "processing", label: "İşlem süresi", value: (v) => v.processing_days },
    { key: "fit", label: "Kimler için uygun?", value: (v) => FIT[v.id] || v.description },
];

/**
 * 30/60 gun ve tek/cok giris farkini tek tabloda gosterir.
 * `onSelect` verilirse (basvuru formu) satirdaki buton vizeyi secer,
 * verilmezse ilgili vizeyle basvuru sayfasina yonlendirir.
 */
export const VisaComparison = ({ visas = [], onSelect, selectedId = "" }) => {
    const list = visas
        .filter((v) => v.category !== "child" && v.auto_suggest !== false && v.active !== false)
        .slice()
        .sort((a, b) => Number(a.order || 0) - Number(b.order || 0));

    // Ayni sureye sahip cocuk vizesi (aile farkini gostermek icin)
    const childFor = (v) =>
        visas.find(
            (c) =>
                c.category === "child" &&
                c.active !== false &&
                Number(c.duration_days) === Number(v.duration_days) &&
                (v.entry_type === "multiple" ? false : true)
        ) || null;

    if (list.length < 2) return null;

    const cellTone = (v) => (v.popular ? "bg-primary/[0.04]" : "");

    return (
        <div>
            <p className="mb-2 text-xs font-medium text-muted-foreground sm:hidden" data-testid="visa-comparison-scroll-hint">
                Tabloyu yana kaydırarak diğer vizeleri görebilirsiniz.
            </p>
            <div
                className="overflow-x-auto rounded-[var(--radius-lg)] border border-border bg-card"
                style={{ boxShadow: "var(--shadow-card)" }}
                data-testid="visa-comparison"
            >
            <table className="w-full min-w-[760px] border-collapse text-sm">
                <thead>
                    <tr>
                        <th className="sticky left-0 z-[1] w-[180px] bg-card px-4 py-4 text-left align-bottom text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                            Karşılaştırma
                        </th>
                        {list.map((v) => (
                            <th
                                key={v.id}
                                className={`px-4 py-4 text-center align-bottom ${cellTone(v)} ${
                                    selectedId === v.id ? "bg-primary/[0.08]" : ""
                                }`}
                                data-testid={`visa-comparison-col-${v.id}`}
                            >
                                <span className="flex h-5 items-center justify-center">
                                    {v.popular && (
                                        <span className="inline-flex items-center gap-1 whitespace-nowrap rounded-full bg-[hsl(var(--cream-tag)/0.35)] px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wider text-foreground">
                                            <Star className="h-2.5 w-2.5 fill-current" aria-hidden="true" /> En çok
                                            tercih edilen
                                        </span>
                                    )}
                                </span>
                                <span className="mt-2 block font-heading text-sm font-extrabold leading-snug text-[hsl(30_62%_38%)]">
                                    {v.short_name || v.name}
                                </span>
                                <span className="mt-1 block text-xs font-medium text-muted-foreground">
                                    {v.duration_days} gün · {v.entry_label}
                                </span>
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {ROWS.map((r) => (
                        <tr key={r.key} className="border-t border-border">
                            <th
                                scope="row"
                                className="sticky left-0 z-[1] bg-card px-4 py-3.5 text-left align-top text-[11px] font-bold uppercase tracking-wide text-muted-foreground"
                            >
                                {r.label}
                            </th>
                            {list.map((v) => (
                                <td
                                    key={v.id}
                                    className={`px-4 py-3.5 text-center align-top leading-6 ${cellTone(v)} ${
                                        selectedId === v.id ? "bg-primary/[0.08]" : ""
                                    }`}
                                    data-testid={`visa-comparison-${r.key}-${v.id}`}
                                >
                                    <span
                                        className={
                                            r.strong
                                                ? "font-heading text-base font-extrabold text-[hsl(30_62%_38%)]"
                                                : "text-foreground/90"
                                        }
                                    >
                                        {r.value(v, { childFor })}
                                    </span>
                                    {r.sub && r.sub(v, { childFor }) ? (
                                        <span
                                            className={`mt-1 block text-[11px] text-muted-foreground ${
                                                r.subNoWrap ? "whitespace-nowrap" : "font-mono-code"
                                            }`}
                                        >
                                            {r.sub(v, { childFor })}
                                        </span>
                                    ) : null}
                                </td>
                            ))}
                        </tr>
                    ))}
                    <tr className="border-t border-border">
                        <th
                            scope="row"
                            className="sticky left-0 z-[1] bg-card px-4 py-4 text-left align-top text-[11px] font-bold uppercase tracking-wide text-muted-foreground"
                        >
                            Seçim
                        </th>
                        {list.map((v) => (
                            <td
                                key={v.id}
                                className={`px-4 py-4 text-center align-top ${cellTone(v)} ${
                                    selectedId === v.id ? "bg-primary/[0.08]" : ""
                                }`}
                            >
                                {onSelect ? (
                                    <Button
                                        type="button"
                                        variant={selectedId === v.id ? "default" : "secondary"}
                                        className={`h-10 w-full whitespace-nowrap ${
                                            selectedId === v.id ? "" : "border border-border"
                                        }`}
                                        onClick={() => onSelect(v)}
                                        data-testid={`visa-comparison-select-${v.id}`}
                                    >
                                        {selectedId === v.id ? "Seçildi" : "Bu vizeyi seç"}
                                    </Button>
                                ) : (
                                    <Button
                                        asChild
                                        className="h-10 w-full whitespace-nowrap"
                                        data-testid={`visa-comparison-apply-${v.id}`}
                                    >
                                        <Link to={applyPath({ vize: v.id })}>
                                            Başvuruya başla
                                            <ArrowRight className="ml-1.5 h-3.5 w-3.5" aria-hidden="true" />
                                        </Link>
                                    </Button>
                                )}
                            </td>
                        ))}
                    </tr>
                </tbody>
            </table>
            </div>
            <p
                className="mt-3 text-xs leading-5 text-muted-foreground"
                data-testid="visa-comparison-family-note"
            >
                Aile başvurusu: 2-3 yolcuda %10, 4 ve üzeri yolcuda %15 indirim tüm vize bedellerine
                otomatik uygulanır. Çocuk vizeleri tek girişlidir; çok girişli vize alan ebeveynlerle
                aynı başvuruda ilerleyebilirler.
            </p>
        </div>
    );
};

export default VisaComparison;
