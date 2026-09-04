import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
    ArrowRight,
    Check,
    CreditCard,
    Landmark,
    Loader2,
    Minus,
    Plus,
    ShieldCheck,
} from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatMoney, formatUsd } from "../lib/site";
import { FxNote } from "./FxNote";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { DateField, fromISODate } from "./DateField";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Skeleton } from "./ui/skeleton";

const emptyContact = { full_name: "", email: "", phone: "" };

const validate = (contact, quantities) => {
    const errors = {};
    if (contact.full_name.trim().length < 3) errors.full_name = "Ad soyad zorunlu.";
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(contact.email.trim())) errors.email = "Geçerli bir e-posta girin.";
    if (contact.phone.trim().length < 7) errors.phone = "Telefon numarası zorunlu.";
    const total = Object.values(quantities).reduce((a, b) => a + b, 0);
    if (total === 0) errors.items = "En az bir paket seçin.";
    return errors;
};

/**
 * eSIM ve seyahat sigortasi icin ortak satin alma akisi.
 * kind: "esim" | "insurance"
 */
export const StoreCheckout = ({ kind, ctaLabel = "Satın al" }) => {
    const [allProducts, setAllProducts] = useState([]);
    const [bundle, setBundle] = useState(null);
    const [loading, setLoading] = useState(true);
    const [quantities, setQuantities] = useState({});
    const [contact, setContact] = useState(emptyContact);
    const [dates, setDates] = useState({ travel_start: "", travel_end: "" });
    const [note, setNote] = useState("");
    const [method, setMethod] = useState("card");
    const [errors, setErrors] = useState({});
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        api.get("/products")
            .then(({ data }) => {
                setAllProducts(data.items || []);
                setBundle(data.bundle || null);
            })
            .catch((err) => toast.error(apiError(err, "Paketler yüklenemedi.")))
            .finally(() => setLoading(false));
    }, [kind]);

    const products = useMemo(() => allProducts.filter((p) => p.kind === kind), [allProducts, kind]);
    const crossProducts = useMemo(() => allProducts.filter((p) => p.kind !== kind), [allProducts, kind]);
    const crossLabel = kind === "esim" ? "Seyahat sağlık sigortası" : "Dubai eSIM (internet paketi)";

    const setQty = (id, delta) =>
        setQuantities((q) => {
            const next = Math.max(0, Math.min(10, (q[id] || 0) + delta));
            const copy = { ...q };
            if (next === 0) delete copy[id];
            else copy[id] = next;
            return copy;
        });

    const lines = useMemo(
        () =>
            allProducts
                .filter((p) => quantities[p.id])
                .map((p) => ({
                    ...p,
                    quantity: quantities[p.id],
                    lineTotal: p.price * quantities[p.id],
                })),
        [allProducts, quantities]
    );
    const itemsTotal = lines.reduce((sum, l) => sum + l.lineTotal, 0);
    const bundleRate = Number(bundle?.rate) || 0.1;
    const bundleActive = useMemo(() => {
        const kinds = new Set(lines.map((l) => l.kind));
        return kinds.has("esim") && kinds.has("insurance");
    }, [lines]);
    const bundleDiscount = bundleActive ? Math.round(itemsTotal * bundleRate * 100) / 100 : 0;
    const total = Math.round((itemsTotal - bundleDiscount) * 100) / 100;

    const submit = async () => {
        const errs = validate(contact, quantities);
        setErrors(errs);
        if (Object.keys(errs).length) {
            toast.error(errs.items || "Lütfen eksik alanları doldurun.");
            return;
        }
        setSubmitting(true);
        try {
            const { data } = await api.post("/orders", {
                items: lines.map((l) => ({ product_id: l.id, quantity: l.quantity })),
                contact: {
                    full_name: contact.full_name.trim(),
                    email: contact.email.trim(),
                    phone: contact.phone.trim(),
                },
                travel_start: dates.travel_start || null,
                travel_end: dates.travel_end || null,
                note: note.trim() || null,
                payment_method: method === "transfer" ? "transfer" : "card",
            });
            const order = data.order;
            localStorage.setItem("dv_last_order_email", contact.email.trim());

            if (method === "transfer") {
                toast.success("Siparişiniz oluşturuldu. Havale bilgileri ekranda.");
                window.location.assign(`/siparis/${order.reference_code}`);
                return;
            }

            const { data: pay } = await api.post(`/orders/${order.id}/checkout`, {
                origin_url: window.location.origin,
            });
            window.location.assign(pay.checkout_url);
        } catch (err) {
            toast.error(apiError(err, "Sipariş oluşturulamadı."));
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="grid gap-8 lg:grid-cols-[1.4fr_1fr]" data-testid={`store-${kind}`}>
            {/* PRODUCTS */}
            <div>
                <div className="flex flex-wrap items-center gap-3">
                    <FxNote />
                    <span className="text-xs text-muted-foreground">
                        Fiyatlar dolar bazlıdır, tahsilat güncel kurla TL olarak yapılır.
                    </span>
                </div>

                {loading ? (
                    <div className="mt-6 grid gap-5 sm:grid-cols-2">
                        {[0, 1, 2, 3].map((i) => (
                            <Skeleton key={i} className="h-52" />
                        ))}
                    </div>
                ) : (
                    <div className="mt-6 grid gap-5 sm:grid-cols-2">
                        {products.map((p) => {
                            const qty = quantities[p.id] || 0;
                            return (
                                <div
                                    key={p.id}
                                    className={`flex h-full flex-col rounded-2xl border-2 bg-card p-6 transition-shadow duration-200 ${
                                        qty
                                            ? "border-primary"
                                            : p.popular
                                              ? "border-foreground/30 ring-1 ring-foreground/10"
                                              : "border-border hover:border-primary/50"
                                    }`}
                                    style={{ boxShadow: qty || p.popular ? "var(--shadow-soft)" : "var(--shadow-card)" }}
                                    data-testid={`product-card-${p.id}`}
                                >
                                    {p.popular && (
                                        <span className="mb-3 inline-flex w-fit rounded-full bg-primary px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-primary-foreground">
                                            En çok tercih edilen
                                        </span>
                                    )}
                                    <h3 className="font-heading text-lg font-bold leading-snug">{p.name}</h3>
                                    <p className="mt-2 text-sm leading-6 text-muted-foreground">{p.summary}</p>

                                    <ul className="mt-4 space-y-2">
                                        {(p.features || []).map((f) => (
                                            <li key={f} className="flex items-start gap-2 text-sm leading-6">
                                                <Check className="mt-1 h-3.5 w-3.5 shrink-0 text-primary" />
                                                {f}
                                            </li>
                                        ))}
                                    </ul>

                                    <div className="mt-auto pt-5">
                                        <p className="font-heading text-2xl font-extrabold" data-testid={`product-price-${p.id}`}>
                                            {formatMoney(p.price, p.currency)}
                                        </p>
                                        <p className="mt-0.5 text-xs text-muted-foreground">
                                            {p.price_usd ? `${formatUsd(p.price_usd)} · ` : ""}
                                            {kind === "esim" ? "paket başı" : "kişi başı"}
                                        </p>

                                        <div className="mt-4 flex items-center gap-3">
                                            <Button
                                                type="button"
                                                variant="secondary"
                                                className="h-10 w-10 border border-border p-0"
                                                onClick={() => setQty(p.id, -1)}
                                                disabled={!qty}
                                                aria-label="Adet azalt"
                                                data-testid={`qty-minus-${p.id}`}
                                            >
                                                <Minus className="h-4 w-4" />
                                            </Button>
                                            <span
                                                className="min-w-8 text-center font-heading text-lg font-bold"
                                                data-testid={`qty-value-${p.id}`}
                                            >
                                                {qty}
                                            </span>
                                            <Button
                                                type="button"
                                                variant="secondary"
                                                className="h-10 w-10 border border-border p-0"
                                                onClick={() => setQty(p.id, 1)}
                                                aria-label="Adet arttır"
                                                data-testid={`qty-plus-${p.id}`}
                                            >
                                                <Plus className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* PAKET FIRSATI: diger kategoriyi de sepete ekle */}
                {!loading && crossProducts.length > 0 && (
                    <div
                        className="mt-8 rounded-2xl border-2 border-[hsl(var(--brand-green)/0.35)] bg-[hsl(var(--brand-green)/0.06)] p-6"
                        data-testid="store-bundle-section"
                    >
                        <div className="flex flex-wrap items-start justify-between gap-3">
                            <div className="max-w-xl">
                                <p className="font-heading text-base font-bold">
                                    {bundle?.title || "Seyahat paketi indirimi"} · {crossLabel}
                                </p>
                                <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                                    {bundle?.note ||
                                        "Seyahat sigortası ve Dubai eSIM'i birlikte alın, sepet toplamınızda %10 indirim otomatik uygulanır."}
                                </p>
                            </div>
                            {bundleActive && (
                                <span
                                    className="inline-flex items-center gap-1.5 rounded-full bg-[hsl(var(--brand-green))] px-3 py-1 text-xs font-bold text-white"
                                    data-testid="store-bundle-active-badge"
                                >
                                    <Check className="h-3.5 w-3.5" /> %{Math.round(bundleRate * 100)} indirim aktif
                                </span>
                            )}
                        </div>
                        <div className="mt-5 grid gap-4 sm:grid-cols-2">
                            {crossProducts.map((p) => {
                                const qty = quantities[p.id] || 0;
                                return (
                                    <div
                                        key={p.id}
                                        className={`rounded-xl border bg-card p-5 ${qty ? "border-primary" : "border-border"}`}
                                        data-testid={`cross-product-card-${p.id}`}
                                    >
                                        <p className="font-heading text-sm font-bold">{p.name}</p>
                                        <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{p.summary}</p>
                                        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                                            <div>
                                                <p className="font-heading text-lg font-bold" data-testid={`cross-product-price-${p.id}`}>
                                                    {formatMoney(p.price, p.currency)}
                                                </p>
                                                <p className="text-xs text-muted-foreground">
                                                    {p.price_usd ? `${formatUsd(p.price_usd)} · ` : ""}
                                                    {p.kind === "esim" ? "paket başı" : "kişi başı"}
                                                </p>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Button
                                                    type="button"
                                                    variant="secondary"
                                                    className="h-9 w-9 border border-border p-0"
                                                    onClick={() => setQty(p.id, -1)}
                                                    disabled={!qty}
                                                    aria-label="Adet azalt"
                                                    data-testid={`cross-qty-minus-${p.id}`}
                                                >
                                                    <Minus className="h-4 w-4" />
                                                </Button>
                                                <span className="min-w-7 text-center font-heading text-base font-bold" data-testid={`cross-qty-value-${p.id}`}>
                                                    {qty}
                                                </span>
                                                <Button
                                                    type="button"
                                                    variant="secondary"
                                                    className="h-9 w-9 border border-border p-0"
                                                    onClick={() => setQty(p.id, 1)}
                                                    aria-label="Adet arttır"
                                                    data-testid={`cross-qty-plus-${p.id}`}
                                                >
                                                    <Plus className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}
            </div>

            {/* CHECKOUT */}
            <aside
                className="h-fit rounded-2xl border-2 border-border bg-card p-6 lg:sticky lg:top-24"
                style={{ boxShadow: "var(--shadow-soft)" }}
                data-testid="store-checkout-panel"
            >
                <h2 className="font-heading text-lg font-bold">Sipariş özeti</h2>

                {lines.length === 0 ? (
                    <p className="mt-3 text-sm text-muted-foreground" data-testid="store-empty-cart">
                        Henüz paket seçilmedi. Soldaki paketlerden adet ekleyerek devam edin.
                    </p>
                ) : (
                    <ul className="mt-4 space-y-2.5">
                        {lines.map((l) => (
                            <li key={l.id} className="flex items-start justify-between gap-3 text-sm">
                                <span className="text-muted-foreground">
                                    {l.name} <span className="font-semibold text-foreground">x{l.quantity}</span>
                                </span>
                                <span className="font-semibold">{formatMoney(l.lineTotal, l.currency)}</span>
                            </li>
                        ))}
                    </ul>
                )}

                <div className="mt-4 border-t border-border pt-4">
                    {bundleDiscount > 0 && (
                        <div className="mb-3 flex items-center justify-between text-sm text-[hsl(var(--brand-green))]" data-testid="store-bundle-discount">
                            <span>Paket indirimi (%{Math.round(bundleRate * 100)})</span>
                            <span className="font-semibold">- {formatMoney(bundleDiscount, "TRY")}</span>
                        </div>
                    )}
                    <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold">Toplam</span>
                        <span className="font-heading text-2xl font-extrabold" data-testid="store-total">
                            {formatMoney(total, "TRY")}
                        </span>
                    </div>
                </div>
                <div className="mt-1">
                    <FxNote variant="inline" />
                </div>

                <div className="mt-6 space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="store-name">Ad soyad</Label>
                        <Input
                            id="store-name"
                            value={contact.full_name}
                            onChange={(e) => setContact((c) => ({ ...c, full_name: e.target.value }))}
                            data-testid="store-name-input"
                        />
                        {errors.full_name && (
                            <p className="text-xs font-medium text-destructive" data-testid="store-name-error">
                                {errors.full_name}
                            </p>
                        )}
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="store-email">E-posta</Label>
                        <Input
                            id="store-email"
                            type="email"
                            value={contact.email}
                            onChange={(e) => setContact((c) => ({ ...c, email: e.target.value }))}
                            data-testid="store-email-input"
                        />
                        {errors.email && (
                            <p className="text-xs font-medium text-destructive" data-testid="store-email-error">
                                {errors.email}
                            </p>
                        )}
                        <p className="text-xs text-muted-foreground">
                            {kind === "esim"
                                ? "eSIM QR kodunuz bu adrese gönderilir."
                                : "Poliçeniz PDF olarak bu adrese gönderilir."}
                        </p>
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="store-phone">Telefon</Label>
                        <Input
                            id="store-phone"
                            value={contact.phone}
                            onChange={(e) => setContact((c) => ({ ...c, phone: e.target.value }))}
                            data-testid="store-phone-input"
                        />
                        {errors.phone && (
                            <p className="text-xs font-medium text-destructive" data-testid="store-phone-error">
                                {errors.phone}
                            </p>
                        )}
                    </div>

                    <div className="grid gap-3 sm:grid-cols-2">
                        <div className="space-y-2">
                            <Label htmlFor="store-start">Gidiş tarihi</Label>
                            <DateField
                                id="store-start"
                                value={dates.travel_start}
                                onChange={(iso) => setDates((d) => ({ ...d, travel_start: iso }))}
                                minDate={new Date()}
                                fromYear={new Date().getFullYear()}
                                toYear={new Date().getFullYear() + 3}
                                data-testid="store-start-input"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="store-end">Dönüş tarihi</Label>
                            <DateField
                                id="store-end"
                                value={dates.travel_end}
                                onChange={(iso) => setDates((d) => ({ ...d, travel_end: iso }))}
                                minDate={fromISODate(dates.travel_start) || new Date()}
                                fromYear={new Date().getFullYear()}
                                toYear={new Date().getFullYear() + 3}
                                data-testid="store-end-input"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="store-note">Not (opsiyonel)</Label>
                        <Textarea
                            id="store-note"
                            rows={2}
                            placeholder={
                                kind === "insurance"
                                    ? "Sigortalanacak kişilerin ad-soyad ve doğum tarihleri"
                                    : "Telefon modeli / eSIM destekli mi?"
                            }
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                            data-testid="store-note-input"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label>Ödeme yöntemi</Label>
                        <div className="grid gap-2 sm:grid-cols-2">
                            <Button
                                type="button"
                                variant={method === "card" ? "default" : "secondary"}
                                className={`h-11 ${method === "card" ? "" : "border border-border"}`}
                                onClick={() => setMethod("card")}
                                data-testid="store-method-card"
                            >
                                <CreditCard className="mr-2 h-4 w-4" /> Kart
                            </Button>
                            <Button
                                type="button"
                                variant={method === "transfer" ? "default" : "secondary"}
                                className={`h-11 ${method === "transfer" ? "" : "border border-border"}`}
                                onClick={() => setMethod("transfer")}
                                data-testid="store-method-transfer"
                            >
                                <Landmark className="mr-2 h-4 w-4" /> Havale
                            </Button>
                        </div>
                    </div>

                    <Button
                        onClick={submit}
                        disabled={submitting || lines.length === 0}
                        className="h-12 w-full text-base"
                        data-testid="store-submit-button"
                    >
                        {submitting ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> İşleniyor…
                            </>
                        ) : (
                            <>
                                {ctaLabel} <ArrowRight className="ml-2 h-4 w-4" />
                            </>
                        )}
                    </Button>

                    <p className="flex items-start gap-2 text-xs leading-5 text-muted-foreground">
                        <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                        Ödeme sonrası siparişinizi{" "}
                        <Link to="/hesabim" className="font-semibold text-primary hover:underline">
                            hesabınızdan
                        </Link>{" "}
                        takip edebilirsiniz.
                    </p>
                </div>
            </aside>
        </div>
    );
};
