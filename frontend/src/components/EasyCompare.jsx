import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Check, X } from "lucide-react";
import { Button } from "./ui/button";

const ROWS = [
    {
        key: "documents",
        label: "İstenen belgeler",
        us: "Pasaport kimlik sayfası + vesikalık fotoğraf",
        them: "Bilet, otel, banka hesap dökümü, dilekçe...",
    },
    {
        key: "ticket",
        label: "Uçak bileti / otel şartı",
        us: "Yok — vizeniz çıktıktan sonra alın",
        them: "Başvurudan önce satın alma isteniyor",
        themNegative: true,
    },
    {
        key: "passport",
        label: "Pasaportunuz nerede kalıyor?",
        us: "Sizde kalıyor, kargoya vermiyorsunuz",
        them: "Ofise teslim veya kargo süreci",
        themNegative: true,
    },
    {
        key: "speed",
        label: "Sonuç süresi",
        us: "Ortalama 2 iş günü · ekspreste 12 saat içinde",
        them: "Belirsiz, evrak eksikliğinde uzuyor",
    },
    {
        key: "price",
        label: "Fiyat",
        us: "Harç + hizmet bedeli dahil, tek seferlik",
        them: "Sonradan eklenen dosya ve komisyon ücretleri",
        themNegative: true,
    },
];

const Cell = ({ text, positive }) => (
    <span className="flex items-start gap-2 text-xs leading-5 sm:text-sm sm:leading-6">
        {positive ? (
            <Check className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--brand-green))] sm:mt-1" aria-hidden="true" />
        ) : (
            <X className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground/70 sm:mt-1" aria-hidden="true" />
        )}
        <span className={positive ? "font-medium text-foreground" : "text-muted-foreground"}>{text}</span>
    </span>
);

export const EasyCompare = () => (
    <section className="section" data-testid="landing-easy-compare">
        <div className="container-page">
            <div className="max-w-2xl">
                <span className="eyebrow">Karşılaştırma</span>
                <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Neden bizde kolay?</h2>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    Bizimle çalışırken yaşadığınız süreci klasik acente yöntemiyle yan yana görün.
                </p>
            </div>

            <div
                className="mt-7 overflow-hidden rounded-[var(--radius-lg)] border border-border bg-card"
                style={{ boxShadow: "var(--shadow-card)" }}
            >
                <div className="hidden grid-cols-[1.05fr_1.3fr_1.3fr] border-b border-border bg-[hsl(var(--cloud))] md:grid">
                    <span className="px-6 py-4 text-xs font-bold uppercase tracking-[0.12em] text-muted-foreground">
                        Süreç
                    </span>
                    <span className="border-l border-border bg-[hsl(var(--brand-green)/0.08)] px-6 py-4 font-heading text-sm font-bold text-[hsl(var(--brand-green))]">
                        Dubai Vize Hattı
                    </span>
                    <span className="border-l border-border px-6 py-4 font-heading text-sm font-bold text-muted-foreground">
                        Klasik acente yöntemi
                    </span>
                </div>

                {ROWS.map((row, i) => (
                    <div
                        key={row.key}
                        className={`grid grid-cols-2 gap-2 px-4 py-3 md:grid-cols-[1.05fr_1.3fr_1.3fr] md:gap-0 md:px-0 md:py-0 ${
                            i ? "border-t border-border" : ""
                        }`}
                        data-testid={`compare-row-${row.key}`}
                    >
                        <span className="col-span-2 font-heading text-sm font-semibold md:col-span-1 md:px-6 md:py-4">
                            {row.label}
                        </span>
                        <div className="rounded-lg bg-[hsl(var(--brand-green)/0.06)] p-3 md:rounded-none md:border-l md:border-border md:px-6 md:py-4">
                            <p className="mb-1 text-[10px] font-bold uppercase tracking-wider text-[hsl(var(--brand-green))] md:hidden">
                                Biz
                            </p>
                            <Cell text={row.us} positive />
                        </div>
                        <div className="rounded-lg border border-border p-3 md:rounded-none md:border-0 md:border-l md:border-border md:px-6 md:py-4">
                            <p className="mb-1 text-[10px] font-bold uppercase tracking-wider text-muted-foreground md:hidden">
                                Klasik acente
                            </p>
                            <Cell text={row.them} positive={false} />
                        </div>
                    </div>
                ))}
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-4">
                <Button asChild size="lg" data-testid="compare-apply-button">
                    <Link to="/basvuru">
                        Hemen başvurun <ArrowRight className="ml-1 h-4 w-4" />
                    </Link>
                </Button>
                <p className="text-xs leading-5 text-muted-foreground">
                    Karşılaştırma, müşterilerimizin başvuru öncesinde bize aktardığı yaygın uygulamaları
                    özetler; her acentenin süreci farklılık gösterebilir.
                </p>
            </div>
        </div>
    </section>
);
