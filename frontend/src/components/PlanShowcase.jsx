import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Check, Info } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatMoney, formatUsd } from "../lib/site";
import { FxNote } from "./FxNote";
import { Button } from "./ui/button";
import { Skeleton } from "./ui/skeleton";

/**
 * eSIM ve seyahat sigortasi paketlerini yalnizca bilgi amacli listeler.
 * Bu sayfalardan satin alma yapilmaz; paketler vize basvurusu sirasinda eklenir.
 */
export const PlanShowcase = ({ kind }) => {
    const [allProducts, setAllProducts] = useState([]);
    const [bundle, setBundle] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get("/products")
            .then(({ data }) => {
                setAllProducts(data.items || []);
                setBundle(data.bundle || null);
            })
            .catch((err) => toast.error(apiError(err, "Paketler yüklenemedi.")))
            .finally(() => setLoading(false));
    }, []);

    const products = useMemo(() => allProducts.filter((p) => p.kind === kind), [allProducts, kind]);
    const unit = kind === "esim" ? "paket başı" : "kişi başı";
    const crossLink = kind === "esim" ? "/seyahat-sigortasi" : "/esim";
    const crossLabel = kind === "esim" ? "seyahat sağlık sigortası" : "Dubai eSIM";

    return (
        <div data-testid={`plans-${kind}`}>
            <div className="flex flex-wrap items-center gap-3">
                <FxNote />
                <span className="text-xs text-muted-foreground">
                    Fiyatlar dolar bazlıdır, tahsilat güncel kurla TL olarak yapılır.
                </span>
            </div>

            {loading ? (
                <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                    {[0, 1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-56" />
                    ))}
                </div>
            ) : (
                <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                    {products.map((p) => (
                        <div
                            key={p.id}
                            className={`flex h-full flex-col rounded-2xl border-2 bg-card p-5 ${
                                p.popular ? "border-primary" : "border-border"
                            }`}
                            style={{ boxShadow: p.popular ? "var(--shadow-soft)" : "var(--shadow-card)" }}
                            data-testid={`plan-card-${p.id}`}
                        >
                            {p.popular && (
                                <span className="mb-3 inline-flex w-fit rounded-full bg-primary px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-primary-foreground">
                                    En çok tercih edilen
                                </span>
                            )}
                            <h3 className="font-heading text-base font-bold leading-snug">{p.name}</h3>
                            <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{p.summary}</p>

                            <ul className="mt-3.5 space-y-1.5">
                                {(p.features || []).map((f) => (
                                    <li key={f} className="flex items-start gap-2 text-xs leading-5">
                                        <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                                        {f}
                                    </li>
                                ))}
                            </ul>

                            <div className="mt-auto pt-4">
                                <p className="font-heading text-xl font-extrabold" data-testid={`plan-price-${p.id}`}>
                                    {formatMoney(p.price, p.currency)}
                                </p>
                                <p className="mt-0.5 text-xs text-muted-foreground">
                                    {p.price_usd ? `${formatUsd(p.price_usd)} · ` : ""}
                                    {unit}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <div
                className="mt-8 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-primary/25 bg-primary/[0.05] p-6"
                data-testid={`plans-${kind}-cta`}
            >
                <div className="max-w-2xl">
                    <p className="flex items-center gap-2 font-heading text-base font-bold">
                        <Info className="h-4 w-4 text-primary" />
                        Bu sayfa bilgi amaçlıdır
                    </p>
                    <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                        Paketler ayrı olarak satılmaz. Vize başvurunuzun Ek hizmetler ve Özet adımlarında
                        istediğiniz paketi seçebilir, ödemesini vize bedeliyle birlikte tek seferde
                        yapabilirsiniz.{" "}
                        {bundle?.note ||
                            "Seyahat sigortası ile eSIM'i birlikte seçtiğinizde %10 paket indirimi uygulanır."}{" "}
                        <Link to={crossLink} className="font-semibold text-primary hover:underline">
                            {crossLabel} paketlerine de bakın
                        </Link>
                        .
                    </p>
                </div>
                <Button asChild className="h-12 px-7 text-base" data-testid={`plans-${kind}-apply-button`}>
                    <Link to="/basvuru">
                        Vize başvurusuna başla <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                </Button>
            </div>
        </div>
    );
};
