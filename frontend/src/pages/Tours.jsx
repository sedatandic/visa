import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Check, Clock, Minus, Plus, ShoppingBag, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatMoney, formatUsd, setMeta } from "../lib/site";
import { CART_MAX_QTY, useCart } from "../lib/cart";
import { PageHeader } from "../components/SiteLayout";
import { FxNote } from "../components/FxNote";
import { DateField } from "../components/DateField";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Skeleton } from "../components/ui/skeleton";

const todayISO = () => new Date().toISOString().slice(0, 10);

const TourCard = ({ product, onAdd, inCart }) => {
    const [date, setDate] = useState("");
    const [slot, setSlot] = useState((product.time_slots || [])[0] || "");
    const [qty, setQty] = useState(1);

    return (
        <div
            className={`flex h-full flex-col overflow-hidden rounded-2xl border-2 bg-card transition-transform duration-200 hover:-translate-y-1 ${
                inCart ? "border-[hsl(var(--brand-green))]" : product.popular ? "border-primary" : "border-border"
            }`}
            style={{ boxShadow: product.popular ? "var(--shadow-soft)" : "var(--shadow-card)" }}
            data-testid={`tour-card-${product.id}`}
        >
            {product.image_url && (
                <div className="relative aspect-[16/9] w-full overflow-hidden">
                    <img
                        src={product.image_url}
                        alt={product.name}
                        className="absolute inset-0 h-full w-full object-cover"
                        loading="lazy"
                    />
                    {(product.popular || inCart) && (
                        <span
                            className={`absolute left-4 top-4 rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-wider ${
                                inCart
                                    ? "bg-[hsl(var(--brand-green))] text-white"
                                    : "bg-primary text-primary-foreground"
                            }`}
                            data-testid={inCart ? `tour-in-cart-${product.id}` : undefined}
                        >
                            {inCart ? `Sepette · ${inCart.quantity} kişi` : "En çok tercih edilen"}
                        </span>
                    )}
                </div>
            )}

            <div className="flex flex-1 flex-col p-6">
                <h3 className="font-heading text-lg font-bold leading-snug">{product.name}</h3>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{product.summary}</p>

                <ul className="mt-4 space-y-2">
                    {(product.features || []).map((f) => (
                        <li key={f} className="flex items-start gap-2 text-sm leading-6">
                            <Check className="mt-1 h-3.5 w-3.5 shrink-0 text-primary" />
                            {f}
                        </li>
                    ))}
                </ul>

                <div className="mt-6 space-y-4 border-t border-border pt-5">
                    <div className="space-y-2">
                        <Label htmlFor={`tour-date-${product.id}`}>Tur tarihi</Label>
                        <DateField
                            id={`tour-date-${product.id}`}
                            value={date}
                            onChange={setDate}
                            minDate={new Date()}
                            data-testid={`tour-date-input-${product.id}`}
                        />
                    </div>

                    <div>
                        <Label className="mb-2 block">
                            <Clock className="mr-1.5 inline h-3.5 w-3.5 text-primary" />
                            Otelden alınış saati
                        </Label>
                        <div className="flex flex-wrap gap-2">
                            {(product.time_slots || []).map((s) => (
                                <button
                                    key={s}
                                    type="button"
                                    onClick={() => setSlot(s)}
                                    className={`min-h-[40px] rounded-xl border-2 px-3.5 text-sm font-semibold transition-colors duration-150 ${
                                        slot === s
                                            ? "border-primary bg-primary/[0.08] text-foreground"
                                            : "border-border bg-card text-muted-foreground hover:border-primary/50"
                                    }`}
                                    data-testid={`tour-slot-${product.id}-${s.replace(":", "")}`}
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <p className="font-heading text-2xl font-extrabold" data-testid={`tour-price-${product.id}`}>
                            {formatMoney(product.price, product.currency)}
                        </p>
                        <p className="mt-0.5 text-xs text-muted-foreground">
                            {product.price_usd ? `${formatUsd(product.price_usd)} · ` : ""}kişi başı
                        </p>
                    </div>

                    <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="flex items-center gap-2">
                            <button
                                type="button"
                                onClick={() => setQty((q) => Math.max(1, q - 1))}
                                aria-label="Kişi sayısını azalt"
                                className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card transition-colors duration-150 hover:border-primary/60 hover:text-primary"
                                data-testid={`tour-qty-minus-${product.id}`}
                            >
                                <Minus className="h-3.5 w-3.5" />
                            </button>
                            <span
                                className="min-w-8 text-center font-heading text-base font-bold"
                                data-testid={`tour-qty-${product.id}`}
                            >
                                {qty}
                            </span>
                            <button
                                type="button"
                                onClick={() => setQty((q) => Math.min(CART_MAX_QTY, q + 1))}
                                aria-label="Kişi sayısını artır"
                                className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card transition-colors duration-150 hover:border-primary/60 hover:text-primary"
                                data-testid={`tour-qty-plus-${product.id}`}
                            >
                                <Plus className="h-3.5 w-3.5" />
                            </button>
                        </div>
                        <Button
                            className="h-11 flex-1"
                            onClick={() => onAdd(product, { qty, date, slot })}
                            data-testid={`tour-add-to-cart-${product.id}`}
                        >
                            <ShoppingBag className="mr-2 h-4 w-4" /> Sepete ekle
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default function Tours() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const cart = useCart();

    useEffect(() => {
        setMeta(
            "Dubai Turları ve Çöl Safarisi | Dubai Vize Hattı",
            "Türkçe rehberli Dubai çöl safarisi turları: kumul turu, deve gezisi, kum sörfü ve Arap kampında akşam yemeği. Tarih ve saat seçip sepete ekleyin.",
            { canonicalPath: "/dubai-turlari" }
        );
    }, []);

    useEffect(() => {
        api.get("/products", { params: { kind: "tour" } })
            .then(({ data }) => setProducts(data.items || []))
            .catch((err) => toast.error(apiError(err, "Turlar yüklenemedi.")))
            .finally(() => setLoading(false));
    }, []);

    const addTour = (product, { qty, date, slot }) => {
        if (!date || date < todayISO()) {
            toast.error("Tur için geçerli bir tarih seçin.");
            return;
        }
        if ((product.time_slots || []).length && !slot) {
            toast.error("Otelden alınış saatini seçin.");
            return;
        }
        const res = cart.add(product.id, qty, { scheduled_date: date, scheduled_time: slot });
        if (!res.ok) {
            toast.error("Sepete en fazla 6 farklı ürün ekleyebilirsiniz.");
            return;
        }
        toast.success(`${product.name} sepete eklendi (${qty} kişi).`, {
            action: { label: "Sepete git", onClick: () => window.location.assign("/sepet") },
        });
    };

    const cartLines = useMemo(
        () => Object.fromEntries(cart.items.map((i) => [i.product_id, i])),
        [cart.items]
    );

    return (
        <div data-testid="tours-page">
            <PageHeader
                eyebrow="Dubai turları"
                title="Çöl safarisi ve Dubai aktiviteleri"
                description="Türkçe konuşan rehber eşliğinde çöl safarisi turlarını tarih ve saat seçerek sepete ekleyin; rezervasyonunuzu biz yapar, kupon ve buluşma bilgilerini e-postanıza göndeririz."
            />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page">
                    <div className="flex flex-wrap items-center gap-3">
                        <FxNote />
                        <span className="text-xs text-muted-foreground">
                            Fiyatlar kişi başıdır, tahsilat güncel kurla TL olarak yapılır.
                        </span>
                    </div>

                    {loading ? (
                        <div className="mt-6 grid gap-6 lg:grid-cols-2">
                            <Skeleton className="h-[520px]" />
                            <Skeleton className="h-[520px]" />
                        </div>
                    ) : (
                        <div className="mt-6 grid gap-6 lg:grid-cols-2">
                            {products.map((p) => (
                                <TourCard
                                    key={p.id}
                                    product={p}
                                    inCart={cartLines[p.id]}
                                    onAdd={addTour}
                                />
                            ))}
                        </div>
                    )}

                    <div
                        className="mt-8 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-primary/25 bg-primary/[0.05] p-6"
                        data-testid="tours-cta"
                    >
                        <div className="max-w-2xl">
                            <p className="flex items-center gap-2 font-heading text-base font-bold">
                                <Sparkles className="h-4 w-4 text-primary" />
                                {cart.count > 0
                                    ? `Sepetinizde ${cart.count} ürün var`
                                    : "Vizeniz olsun ya da olmasın turları satın alabilirsiniz"}
                            </p>
                            <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                                Tur rezervasyonu ödemeniz onaylandıktan sonra yapılır; buluşma noktası ve
                                rehber iletişimi e-posta ile gelir. Sigorta veya eSIM'i de aynı sepete
                                eklerseniz %10 paket indirimi uygulanır.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-3">
                            <Button asChild className="h-12 px-7 text-base" data-testid="tours-cart-button">
                                <Link to="/sepet">
                                    Sepete git{cart.count > 0 ? ` (${cart.count})` : ""}{" "}
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                            <Button
                                asChild
                                variant="secondary"
                                className="h-12 border border-border px-6 text-base"
                                data-testid="tours-esim-button"
                            >
                                <Link to="/esim">eSIM & sigorta paketleri</Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
