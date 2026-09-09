import React, { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ArrowRight, Check, Minus, Plus, ShoppingBag } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatMoney, formatUsd } from "../lib/site";
import { CART_MAX_QTY, useCart } from "../lib/cart";
import { FxNote } from "./FxNote";
import { Button } from "./ui/button";
import { Skeleton } from "./ui/skeleton";

const QtyStepper = ({ id, value, onChange }) => (
    <div className="flex items-center gap-2">
        <button
            type="button"
            onClick={() => onChange(Math.max(1, value - 1))}
            aria-label="Adedi azalt"
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card text-foreground transition-colors duration-150 hover:border-primary/60 hover:text-primary"
            data-testid={`plan-qty-minus-${id}`}
        >
            <Minus className="h-3.5 w-3.5" />
        </button>
        <span className="min-w-8 text-center font-heading text-base font-bold" data-testid={`plan-qty-${id}`}>
            {value}
        </span>
        <button
            type="button"
            onClick={() => onChange(Math.min(CART_MAX_QTY, value + 1))}
            aria-label="Adedi artır"
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card text-foreground transition-colors duration-150 hover:border-primary/60 hover:text-primary"
            data-testid={`plan-qty-plus-${id}`}
        >
            <Plus className="h-3.5 w-3.5" />
        </button>
    </div>
);

/**
 * eSIM ve seyahat sigortasi paketleri: karttan adet secip sepete eklenir.
 * Sepetten tek seferde odeme yapilir; ayrica vize basvurusuna da eklenebilir.
 */
export const PlanShowcase = ({ kind }) => {
    const [allProducts, setAllProducts] = useState([]);
    const [bundle, setBundle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [qty, setQty] = useState({});
    const [searchParams] = useSearchParams();
    const cart = useCart();
    const applicationParam = searchParams.get("basvuru") || "";

    useEffect(() => {
        api.get("/products")
            .then(({ data }) => {
                setAllProducts(data.items || []);
                setBundle(data.bundle || null);
            })
            .catch((err) => toast.error(apiError(err, "Paketler yüklenemedi.")))
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        if (applicationParam) cart.linkApplication(applicationParam);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [applicationParam]);

    const products = useMemo(() => allProducts.filter((p) => p.kind === kind), [allProducts, kind]);
    const unit = kind === "esim" ? "paket başı" : "kişi başı";
    const crossLink = kind === "esim" ? "/seyahat-sigortasi" : "/esim";
    const crossLabel = kind === "esim" ? "seyahat sağlık sigortası" : "Dubai eSIM";

    // Secili kart cercevesi: baslangicta en cok tercih edilen, tiklanan karta tasinir
    const [selectedId, setSelectedId] = useState("");
    useEffect(() => {
        if (selectedId || !products.length) return;
        setSelectedId((products.find((p) => p.popular) || products[0]).id);
    }, [products, selectedId]);

    const addToCart = (product) => {
        const quantity = qty[product.id] || 1;
        const res = cart.add(product.id, quantity);
        if (!res.ok) {
            toast.error("Sepete en fazla 6 farklı ürün ekleyebilirsiniz.");
            return;
        }
        toast.success(`${product.name} sepete eklendi (${quantity} adet).`, {
            action: { label: "Sepete git", onClick: () => window.location.assign("/sepet") },
        });
        setQty((q) => ({ ...q, [product.id]: 1 }));
    };

    return (
        <div data-testid={`plans-${kind}`}>
            <div className="flex flex-wrap items-center gap-3">
                <FxNote />
                <span className="text-xs text-muted-foreground">
                    Fiyatlar dolar bazlıdır, tahsilat güncel kurla TL olarak yapılır.
                </span>
            </div>

            {cart.applicationRef && (
                <div
                    className="mt-4 rounded-xl border border-primary/25 bg-primary/[0.06] p-4 text-sm"
                    data-testid={`plans-${kind}-application-note`}
                >
                    Seçtiğiniz hizmetler{" "}
                    <span className="font-heading font-bold">{cart.applicationRef}</span> numaralı vize
                    başvurunuza eklenecek.
                </div>
            )}

            {loading ? (
                <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                    {[0, 1, 2, 3].map((i) => (
                        <Skeleton key={i} className="h-72" />
                    ))}
                </div>
            ) : (
                <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                    {products.map((p) => {
                        const inCart = cart.items.find((i) => i.product_id === p.id);
                        const selected = selectedId === p.id;
                        return (
                            <div
                                key={p.id}
                                onClick={() => setSelectedId(p.id)}
                                className={`flex h-full cursor-pointer flex-col rounded-2xl border-2 bg-card p-5 transition-transform duration-200 hover:-translate-y-1 ${
                                    inCart
                                        ? "border-[hsl(var(--brand-green))]"
                                        : selected
                                          ? "border-primary"
                                          : "border-border hover:border-primary/40"
                                }`}
                                style={{ boxShadow: selected || inCart ? "var(--shadow-soft)" : "var(--shadow-card)" }}
                                data-testid={`plan-card-${p.id}`}
                                data-selected={selected ? "true" : "false"}
                            >
                                {(p.popular || inCart) && (
                                    <span
                                        className={`mb-3 inline-flex w-fit rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-wider ${
                                            inCart
                                                ? "bg-[hsl(var(--brand-green))] text-white"
                                                : "bg-primary text-primary-foreground"
                                        }`}
                                        data-testid={inCart ? `plan-in-cart-${p.id}` : undefined}
                                    >
                                        {inCart ? `Sepette · ${inCart.quantity} adet` : "En çok tercih edilen"}
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

                                    <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                                        <QtyStepper
                                            id={p.id}
                                            value={qty[p.id] || 1}
                                            onChange={(v) => setQty((q) => ({ ...q, [p.id]: v }))}
                                        />
                                        <Button
                                            className="h-11 flex-1"
                                            onClick={() => addToCart(p)}
                                            data-testid={`plan-add-to-cart-${p.id}`}
                                        >
                                            <ShoppingBag className="mr-2 h-4 w-4" /> Sepete ekle
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            <div
                className="mt-8 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-primary/25 bg-primary/[0.05] p-6"
                data-testid={`plans-${kind}-cta`}
            >
                <div className="max-w-2xl">
                    <p className="flex items-center gap-2 font-heading text-base font-bold">
                        <ShoppingBag className="h-4 w-4 text-primary" />
                        {cart.count > 0
                            ? `Sepetinizde ${cart.count} ürün var`
                            : "Paketleri tek başına da satın alabilirsiniz"}
                    </p>
                    <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                        Vizeniz zaten hazır olsa bile bu paketleri ayrı olarak alabilirsiniz; sepetten kart
                        veya havale ile ödeyin, belgeleriniz e-postanıza gelsin. Dilerseniz vize başvurunuzun
                        Ek hizmetler adımında da seçebilirsiniz.{" "}
                        {bundle?.note ||
                            "Seyahat sigortası ile eSIM'i birlikte seçtiğinizde %10 paket indirimi uygulanır."}{" "}
                        <Link to={crossLink} className="font-semibold text-primary hover:underline">
                            {crossLabel} paketlerine de bakın
                        </Link>
                        .
                    </p>
                </div>
                <div className="flex flex-wrap gap-3">
                    <Button asChild className="h-12 px-7 text-base" data-testid={`plans-${kind}-cart-button`}>
                        <Link to="/sepet">
                            Sepete git{cart.count > 0 ? ` (${cart.count})` : ""}{" "}
                            <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                    </Button>
                    <Button
                        asChild
                        variant="secondary"
                        className="h-12 border border-border px-6 text-base"
                        data-testid={`plans-${kind}-apply-button`}
                    >
                        <Link to="/basvuru">Vize başvurusuna başla</Link>
                    </Button>
                </div>
            </div>
        </div>
    );
};
