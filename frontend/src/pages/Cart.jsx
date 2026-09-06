import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    Clock,
    CreditCard,
    Landmark,
    Loader2,
    Minus,
    PackageSearch,
    PiggyBank,
    Plane,
    Plus,
    PlusCircle,
    ShieldCheck,
    ShoppingBag,
    Smartphone,
    Trash2,
} from "lucide-react";
import { toast } from "sonner";
import { api, apiError, customerAuth } from "../lib/api";
import { formatMoney, setMeta } from "../lib/site";
import { CART_MAX_QTY, useCart } from "../lib/cart";
import { PageHeader } from "../components/SiteLayout";
import { FxNote } from "../components/FxNote";
import { DateField } from "../components/DateField";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Skeleton } from "../components/ui/skeleton";

const BUNDLE_RATE = 0.1;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

const TourSchedule = ({ line, onChange }) => (
    <div className="mt-3 w-full rounded-xl border border-border bg-muted/40 p-3.5">
        <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end">
            <div className="space-y-1.5">
                <Label htmlFor={`cart-tour-date-${line.product_id}`} className="text-xs">
                    Tur tarihi
                </Label>
                <DateField
                    id={`cart-tour-date-${line.product_id}`}
                    value={line.scheduled_date || ""}
                    onChange={(v) => onChange({ scheduled_date: v })}
                    minDate={new Date()}
                    data-testid={`cart-tour-date-${line.product_id}`}
                />
            </div>
            <div className="space-y-1.5">
                <Label className="text-xs">
                    <Clock className="mr-1 inline h-3 w-3 text-primary" /> Alınış saati
                </Label>
                <div className="flex flex-wrap gap-1.5">
                    {(line.product.time_slots || []).map((s) => (
                        <button
                            key={s}
                            type="button"
                            onClick={() => onChange({ scheduled_time: s })}
                            className={`min-h-[38px] rounded-lg border-2 px-3 text-xs font-bold transition-colors duration-150 ${
                                line.scheduled_time === s
                                    ? "border-primary bg-primary/[0.08] text-foreground"
                                    : "border-border bg-card text-muted-foreground hover:border-primary/50"
                            }`}
                            data-testid={`cart-tour-slot-${line.product_id}-${s.replace(":", "")}`}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>
        </div>
        {(!line.scheduled_date || !line.scheduled_time) && (
            <p
                className="mt-2 text-xs font-semibold text-destructive"
                data-testid={`cart-tour-warning-${line.product_id}`}
            >
                Bu tur için tarih ve saat seçmelisiniz.
            </p>
        )}
    </div>
);

// Misafir musteri kisayolu: son siparis kodu tarayicida saklanir, hesap gerekmez.
const LastOrderShortcut = () => {
    const reference = localStorage.getItem("dv_last_order_ref");
    const mail = localStorage.getItem("dv_last_order_email") || "";
    if (!reference) return null;
    return (
        <div
            className="mx-auto mt-6 flex max-w-2xl flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-muted/40 p-4"
            data-testid="cart-last-order-shortcut"
        >
            <p className="text-sm leading-6">
                Son siparişiniz{" "}
                <span className="font-heading font-bold" data-testid="cart-last-order-ref">
                    {reference}
                </span>{" "}
                — durumunu üyelik olmadan görebilirsiniz.
            </p>
            <Button
                asChild
                variant="secondary"
                className="h-10 border border-border"
                data-testid="cart-track-order-button"
            >
                <Link to={`/siparis/${reference}${mail ? `?email=${encodeURIComponent(mail)}` : ""}`}>
                    <PackageSearch className="mr-2 h-4 w-4" /> Siparişimi takip et
                </Link>
            </Button>
        </div>
    );
};

export default function Cart() {    const navigate = useNavigate();
    const cart = useCart();
    const [products, setProducts] = useState([]);
    const [visaTypes, setVisaTypes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [method, setMethod] = useState("card");
    const snapshotSig = useRef("");
    const [form, setForm] = useState({
        full_name: "",
        email: customerAuth.email || localStorage.getItem("dv_last_order_email") || "",
        phone: "",
        travel_start: "",
        travel_end: "",
        note: "",
        application_reference: "",
    });

    useEffect(() => {
        setMeta(
            "Sepetim | Dubai Vize Hattı",
            "Seçtiğiniz Dubai eSIM, seyahat sigortası ve tur paketlerini sepetinizde görüntüleyin, kart veya havale ile ödeyin.",
            { canonicalPath: "/sepet", noindex: true }
        );
    }, []);

    useEffect(() => {
        api.get("/products")
            .then(({ data }) => setProducts(data.items || []))
            .catch((err) => toast.error(apiError(err, "Ürünler yüklenemedi.")))
            .finally(() => setLoading(false));
        api.get("/visa-types")
            .then(({ data }) => setVisaTypes(data || []))
            .catch(() => {});
    }, []);

    useEffect(() => {
        if (cart.applicationRef) {
            setForm((f) => (f.application_reference ? f : { ...f, application_reference: cart.applicationRef }));
        }
    }, [cart.applicationRef]);

    const lines = useMemo(
        () =>
            cart.items
                .map((item) => {
                    const product = products.find((p) => p.id === item.product_id);
                    if (!product) return null;
                    return { ...item, product, total: Number(product.price) * item.quantity };
                })
                .filter(Boolean),
        [cart.items, products]
    );

    // Sepetteki vize satiri: odemesi basvuru formunda alinir
    const visaLine = useMemo(() => {
        if (!cart.visaTypeId) return null;
        const visa = visaTypes.find((v) => v.id === cart.visaTypeId);
        if (!visa) return null;
        const qty = Math.max(1, Number(cart.visaQty) || 1);
        return { visa, qty, total: Number(visa.price) * qty };
    }, [cart.visaTypeId, cart.visaQty, visaTypes]);

    const applyHref = visaLine
        ? `/basvuru?vize=${visaLine.visa.id}${cart.bundleId ? `&paket=${cart.bundleId}` : ""}&sepet=1`
        : "";

    const itemsTotal = lines.reduce((sum, l) => sum + l.total, 0);
    const kinds = new Set(lines.map((l) => l.product.kind));
    const bundleDiscount =
        kinds.has("esim") && kinds.has("insurance") ? Math.round(itemsTotal * BUNDLE_RATE * 100) / 100 : 0;
    const total = itemsTotal - bundleDiscount;
    const grandTotal = total + (visaLine?.total || 0);
    const missingSchedule = lines.filter(
        (l) => l.product.needs_schedule && (!l.scheduled_date || !l.scheduled_time)
    );

    // Tasarruf sayaci: eksik olan urun eklenirse kazanilacak %10 indirimi canli gosterir.
    const savingsOffer = useMemo(() => {
        if (!lines.length || bundleDiscount > 0) return null;
        const missingKind = !kinds.has("insurance") ? "insurance" : !kinds.has("esim") ? "esim" : null;
        if (!missingKind) return null;
        const candidates = products.filter((p) => p.kind === missingKind);
        if (!candidates.length) return null;
        const product =
            candidates.find((p) => p.popular) ||
            candidates.reduce((min, p) => (p.price < min.price ? p : min), candidates[0]);
        const amount = Math.round((itemsTotal + Number(product.price)) * BUNDLE_RATE);
        return {
            product,
            amount,
            label: missingKind === "insurance" ? "Seyahat sigortası" : "Dubai eSIM",
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [lines, products, itemsTotal, bundleDiscount]);

    // Sepeti sunucuya kaydet: e-posta bilindiginde 2 ve 24 saat sonra hatirlatma gonderilir.
    useEffect(() => {
        const email = form.email.trim().toLowerCase();
        if (!EMAIL_RE.test(email) || !lines.length) return undefined;
        const payload = {
            email,
            full_name: form.full_name.trim() || null,
            items: lines.map((l) => ({ product_id: l.product_id, quantity: l.quantity })),
            bundle_id: cart.bundleId || null,
        };
        const sig = JSON.stringify(payload);
        if (sig === snapshotSig.current) return undefined;
        const timer = setTimeout(() => {
            snapshotSig.current = sig;
            api.post("/cart/snapshot", payload).catch(() => {});
        }, 1500);
        return () => clearTimeout(timer);
    }, [form.email, form.full_name, lines, cart.bundleId]);

    const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e?.target ? e.target.value : e }));

    const submit = useCallback(async () => {
        if (!lines.length) return;
        const name = form.full_name.trim();
        const email = form.email.trim();
        const phone = form.phone.trim();
        if (name.length < 3) return toast.error("Ad soyad girin.");
        if (!EMAIL_RE.test(email)) return toast.error("Geçerli bir e-posta girin.");
        if (phone.replace(/\D/g, "").length < 10) return toast.error("Geçerli bir telefon numarası girin.");
        if (missingSchedule.length) {
            return toast.error(`${missingSchedule[0].product.name} için tarih ve saat seçin.`);
        }

        setSubmitting(true);
        try {
            const { data } = await api.post("/orders", {
                items: lines.map((l) => ({
                    product_id: l.product_id,
                    quantity: l.quantity,
                    scheduled_date: l.scheduled_date || null,
                    scheduled_time: l.scheduled_time || null,
                })),
                contact: { full_name: name, email, phone },
                travel_start: form.travel_start || null,
                travel_end: form.travel_end || null,
                note: form.note.trim() || null,
                application_reference: form.application_reference.trim().toUpperCase() || null,
                payment_method: method === "card" ? "card" : "transfer",
            });
            const order = data.order;
            localStorage.setItem("dv_last_order_email", email);
            localStorage.setItem("dv_last_order_ref", order.reference_code);
            cart.clear();

            if (method === "card") {
                const { data: checkout } = await api.post(`/orders/${order.id}/checkout`, {
                    origin_url: window.location.origin,
                });
                window.location.href = checkout.checkout_url;
                return;
            }
            toast.success("Siparişiniz alındı. Havale bilgileri e-postanıza gönderildi.");
            navigate(`/siparis/${order.reference_code}`);
        } catch (err) {
            toast.error(apiError(err, "Sipariş oluşturulamadı."));
        } finally {
            setSubmitting(false);
        }
    }, [lines, form, method, cart, navigate, missingSchedule]);

    const empty = !loading && lines.length === 0 && !visaLine;

    return (
        <div data-testid="cart-page">
            <PageHeader
                eyebrow="Sepetim"
                title="Seçtiğiniz ek hizmetler"
                description="Dubai eSIM, seyahat sigortası ve tur paketlerinizi burada görüp tek seferde ödeyebilirsiniz. Vize başvurunuz olsun ya da olmasın bu hizmetleri ayrı olarak alabilirsiniz."
            />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page">
                    {loading ? (
                        <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
                            <Skeleton className="h-64" />
                            <Skeleton className="h-64" />
                        </div>
                    ) : empty ? (
                        <div className="card-surface mx-auto max-w-xl p-8 text-center" data-testid="cart-empty">
                            <ShoppingBag className="mx-auto h-9 w-9 text-muted-foreground" />
                            <h2 className="mt-4 font-heading text-lg font-bold">Sepetiniz boş</h2>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Dubai eSIM, seyahat sigortası ve çöl safarisi paketlerini inceleyip sepetinize
                                ekleyebilirsiniz. Sigorta ile eSIM'i birlikte aldığınızda %10 paket indirimi
                                uygulanır.
                            </p>
                            <div className="mt-6 flex flex-wrap justify-center gap-3">
                                <Button asChild className="h-11" data-testid="cart-empty-esim-button">
                                    <Link to="/esim">
                                        <Smartphone className="mr-2 h-4 w-4" /> eSIM paketleri
                                    </Link>
                                </Button>
                                <Button
                                    asChild
                                    variant="secondary"
                                    className="h-11 border border-border"
                                    data-testid="cart-empty-insurance-button"
                                >
                                    <Link to="/seyahat-sigortasi">
                                        <ShieldCheck className="mr-2 h-4 w-4" /> Sigorta paketleri
                                    </Link>
                                </Button>
                                <Button
                                    asChild
                                    variant="secondary"
                                    className="h-11 border border-border"
                                    data-testid="cart-empty-tours-button"
                                >
                                    <Link to="/dubai-turlari">Çöl safarisi</Link>
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="grid gap-6 lg:grid-cols-[1.35fr_1fr] lg:items-start">
                            {/* SEPET KALEMLERI */}
                            <div className="card-surface p-6" data-testid="cart-items">
                                <div className="flex flex-wrap items-center justify-between gap-3">
                                    <h2 className="font-heading text-lg font-bold">
                                        Sepetinizdeki hizmetler ({cart.count})
                                    </h2>
                                    <FxNote />
                                </div>

                                {visaLine && (
                                    <div
                                        className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-primary/25 bg-primary/[0.06] p-4"
                                        data-testid="cart-bundle-strip"
                                    >
                                        <p className="text-sm leading-6">
                                            <span className="font-heading font-bold">
                                                Sepetinizde vize var.
                                            </span>{" "}
                                            Vize için pasaport ve fotoğraf bilgileriniz gerekiyor; başvuru formunda
                                            vize, sigorta ve eSIM'i tek seferde ödeyeceksiniz.
                                        </p>
                                        <Button asChild className="h-10" data-testid="cart-bundle-apply-button">
                                            <Link to={applyHref}>
                                                <Plane className="mr-2 h-4 w-4" /> Vize başvurusunu tamamla
                                            </Link>
                                        </Button>
                                    </div>
                                )}

                                {visaLine && (
                                    <div
                                        className="mt-5 border-b border-border pb-4"
                                        data-testid="cart-visa-line"
                                    >
                                        <div className="flex flex-wrap items-center justify-between gap-4">
                                            <div className="min-w-[200px] flex-1">
                                                <p className="flex items-center gap-2 font-heading text-base font-bold">
                                                    <Plane className="h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                                    {visaLine.visa.name}
                                                </p>
                                                <p className="mt-1 text-xs text-muted-foreground">
                                                    Vize ·{" "}
                                                    {formatMoney(visaLine.visa.price, visaLine.visa.currency)} / kişi ·
                                                    başvuru formunda tahsil edilir
                                                </p>
                                            </div>

                                            <div className="flex items-center gap-2">
                                                <button
                                                    type="button"
                                                    onClick={() => cart.setVisaQty(visaLine.qty - 1)}
                                                    aria-label="Yolcu sayısını azalt"
                                                    className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card transition-colors duration-150 hover:border-primary/60 hover:text-primary"
                                                    data-testid="cart-visa-minus"
                                                >
                                                    <Minus className="h-3.5 w-3.5" />
                                                </button>
                                                <span
                                                    className="min-w-8 text-center font-heading text-base font-bold"
                                                    data-testid="cart-visa-qty"
                                                >
                                                    {visaLine.qty}
                                                </span>
                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        cart.setVisaQty(Math.min(CART_MAX_QTY, visaLine.qty + 1))
                                                    }
                                                    aria-label="Yolcu sayısını artır"
                                                    className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card transition-colors duration-150 hover:border-primary/60 hover:text-primary"
                                                    data-testid="cart-visa-plus"
                                                >
                                                    <Plus className="h-3.5 w-3.5" />
                                                </button>
                                            </div>

                                            <div className="flex items-center gap-3">
                                                <span
                                                    className="font-heading text-base font-extrabold"
                                                    data-testid="cart-visa-total"
                                                >
                                                    {formatMoney(visaLine.total, visaLine.visa.currency)}
                                                </span>
                                                <button
                                                    type="button"
                                                    onClick={() => {
                                                        cart.removeVisa();
                                                        toast.success("Vize sepetten çıkarıldı.");
                                                    }}
                                                    aria-label="Vizeyi sepetten çıkar"
                                                    className="rounded-lg border border-border p-2 text-destructive transition-colors duration-150 hover:bg-destructive/10"
                                                    data-testid="cart-visa-remove"
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div className="mt-5 divide-y divide-border">
                                    {lines.map((l) => (
                                        <div key={l.product_id} className="py-4" data-testid={`cart-line-${l.product_id}`}>
                                            <div className="flex flex-wrap items-center justify-between gap-4">
                                                <div className="min-w-[200px] flex-1">
                                                    <p className="font-heading text-base font-bold">{l.product.name}</p>
                                                    <p className="mt-1 text-xs text-muted-foreground">
                                                        {l.product.kind_label} ·{" "}
                                                        {formatMoney(l.product.price, l.product.currency)} /{" "}
                                                        {l.product.kind === "esim" ? "paket" : "kişi"}
                                                    </p>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <button
                                                        type="button"
                                                        onClick={() => cart.setQty(l.product_id, l.quantity - 1)}
                                                        aria-label="Adedi azalt"
                                                        className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card transition-colors duration-150 hover:border-primary/60 hover:text-primary"
                                                        data-testid={`cart-minus-${l.product_id}`}
                                                    >
                                                        <Minus className="h-3.5 w-3.5" />
                                                    </button>
                                                    <span
                                                        className="min-w-8 text-center font-heading text-base font-bold"
                                                        data-testid={`cart-qty-${l.product_id}`}
                                                    >
                                                        {l.quantity}
                                                    </span>
                                                    <button
                                                        type="button"
                                                        onClick={() =>
                                                            cart.setQty(
                                                                l.product_id,
                                                                Math.min(CART_MAX_QTY, l.quantity + 1)
                                                            )
                                                        }
                                                        aria-label="Adedi artır"
                                                        className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-card transition-colors duration-150 hover:border-primary/60 hover:text-primary"
                                                        data-testid={`cart-plus-${l.product_id}`}
                                                    >
                                                        <Plus className="h-3.5 w-3.5" />
                                                    </button>
                                                </div>

                                                <div className="flex items-center gap-3">
                                                    <span
                                                        className="font-heading text-base font-extrabold"
                                                        data-testid={`cart-line-total-${l.product_id}`}
                                                    >
                                                        {formatMoney(l.total, l.product.currency)}
                                                    </span>
                                                    <button
                                                        type="button"
                                                        onClick={() => cart.remove(l.product_id)}
                                                        aria-label="Sepetten çıkar"
                                                        className="rounded-lg border border-border p-2 text-destructive transition-colors duration-150 hover:bg-destructive/10"
                                                        data-testid={`cart-remove-${l.product_id}`}
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                    </button>
                                                </div>
                                            </div>

                                            {l.product.needs_schedule && (
                                                <TourSchedule
                                                    line={l}
                                                    onChange={(patch) => cart.setSchedule(l.product_id, patch)}
                                                />
                                            )}
                                        </div>
                                    ))}
                                </div>

                                <div className="mt-4 flex flex-wrap gap-3 border-t border-border pt-5">
                                    <Button asChild variant="secondary" className="h-10 border border-border">
                                        <Link to="/esim">eSIM ekle</Link>
                                    </Button>
                                    <Button asChild variant="secondary" className="h-10 border border-border">
                                        <Link to="/seyahat-sigortasi">Sigorta ekle</Link>
                                    </Button>
                                    <Button asChild variant="secondary" className="h-10 border border-border">
                                        <Link to="/dubai-turlari">Tur ekle</Link>
                                    </Button>
                                    <Button
                                        variant="secondary"
                                        className="ml-auto h-10 border border-border text-destructive"
                                        onClick={() => cart.clear()}
                                        data-testid="cart-clear-button"
                                    >
                                        Sepeti boşalt
                                    </Button>
                                </div>
                            </div>

                            {/* OZET + ODEME */}
                            <div className="card-surface p-6" data-testid="cart-summary">
                                <h2 className="font-heading text-lg font-bold">Sipariş özeti</h2>

                                <div className="mt-4 space-y-2.5 border-b border-border pb-4 text-sm">
                                    <div className="flex items-center justify-between">
                                        <span className="text-muted-foreground">Ara toplam</span>
                                        <span className="font-semibold" data-testid="cart-items-total">
                                            {formatMoney(itemsTotal)}
                                        </span>
                                    </div>
                                    {visaLine && (
                                        <div
                                            className="flex items-start justify-between gap-3"
                                            data-testid="cart-visa-summary"
                                        >
                                            <span className="text-muted-foreground">
                                                Vize ({visaLine.qty} kişi) · başvuru formunda tahsil edilir
                                            </span>
                                            <span className="font-semibold" data-testid="cart-visa-summary-total">
                                                {formatMoney(visaLine.total, visaLine.visa.currency)}
                                            </span>
                                        </div>
                                    )}
                                    {bundleDiscount > 0 && (
                                        <div
                                            className="flex items-center justify-between text-[hsl(var(--brand-green))]"
                                            data-testid="cart-bundle-discount"
                                        >
                                            <span>Paket indirimi (%10)</span>
                                            <span className="font-semibold">- {formatMoney(bundleDiscount)}</span>
                                        </div>
                                    )}
                                    {bundleDiscount > 0 && (
                                        <p
                                            className="rounded-lg bg-[hsl(var(--brand-green))]/10 px-3 py-2 text-xs font-bold leading-5 text-[hsl(var(--brand-green))]"
                                            data-testid="cart-savings-earned"
                                        >
                                            Tebrikler! Paket indirimiyle {formatMoney(bundleDiscount)} kazandınız.
                                        </p>
                                    )}
                                    {bundleDiscount === 0 && savingsOffer && (
                                        <div
                                            className="rounded-xl border border-[hsl(var(--brand-green))]/35 bg-[hsl(var(--brand-green))]/[0.07] p-3.5"
                                            data-testid="cart-savings-offer"
                                        >
                                            <p className="flex items-start gap-2 text-xs font-bold leading-5 text-[hsl(var(--brand-green))]">
                                                <PiggyBank className="mt-0.5 h-4 w-4 shrink-0" />
                                                <span data-testid="cart-savings-amount">
                                                    {savingsOffer.label} ekleyin, {formatMoney(savingsOffer.amount)}{" "}
                                                    kazanın
                                                </span>
                                            </p>
                                            <p className="mt-1.5 text-xs leading-5 text-muted-foreground">
                                                {savingsOffer.product.name} ·{" "}
                                                {formatMoney(savingsOffer.product.price, savingsOffer.product.currency)}{" "}
                                                — sigorta ve eSIM birlikte alındığında sepetin tamamına %10 indirim
                                                uygulanır.
                                            </p>
                                            <Button
                                                className="mt-3 h-10 w-full"
                                                onClick={() => {
                                                    cart.add(savingsOffer.product.id, 1);
                                                    toast.success(
                                                        `${savingsOffer.product.name} sepete eklendi · %10 paket indirimi uygulandı.`
                                                    );
                                                }}
                                                data-testid="cart-savings-add-button"
                                            >
                                                <PlusCircle className="mr-2 h-4 w-4" /> {savingsOffer.label} ekle ve
                                                kazan
                                            </Button>
                                        </div>
                                    )}
                                    {bundleDiscount === 0 && !savingsOffer && (
                                        <p className="text-xs leading-5 text-muted-foreground">
                                            İpucu: sigorta ve eSIM'i birlikte alırsanız %10 paket indirimi
                                            otomatik uygulanır.
                                        </p>
                                    )}
                                </div>

                                <div className="flex items-center justify-between py-4">
                                    <span className="font-semibold">
                                        {visaLine ? "Sepette ödenecek (sigorta + eSIM)" : "Ödenecek tutar"}
                                    </span>
                                    <span className="font-heading text-2xl font-extrabold" data-testid="cart-total">
                                        {formatMoney(total)}
                                    </span>
                                </div>

                                {visaLine && (
                                    <div
                                        className="flex items-center justify-between border-t border-border py-4"
                                        data-testid="cart-grand-total-row"
                                    >
                                        <span className="font-semibold">Vize dahil tahmini toplam</span>
                                        <span
                                            className="font-heading text-2xl font-extrabold text-[hsl(30_62%_38%)]"
                                            data-testid="cart-grand-total"
                                        >
                                            {formatMoney(grandTotal)}
                                        </span>
                                    </div>
                                )}

                                {visaLine ? (
                                    <div
                                        className="space-y-3 border-t border-border pt-5"
                                        data-testid="cart-visa-checkout-panel"
                                    >
                                        <p className="text-sm leading-6">
                                            Sepetinizde vize olduğu için ödeme başvuru formunda alınır: pasaport ve
                                            fotoğrafınızı yükleyip vize, sigorta ve eSIM'i tek seferde ödeyeceksiniz.
                                        </p>
                                        <Button
                                            className="h-12 w-full text-base"
                                            onClick={() => navigate(applyHref)}
                                            data-testid="cart-visa-apply-button"
                                        >
                                            <Plane className="mr-2 h-4 w-4" /> Vize başvurusunu tamamla
                                        </Button>
                                        <Button
                                            variant="secondary"
                                            className="h-10 w-full border border-border"
                                            onClick={() => {
                                                cart.removeVisa();
                                                toast.success(
                                                    "Vize çıkarıldı. Sigorta ve eSIM'i buradan ödeyebilirsiniz."
                                                );
                                            }}
                                            data-testid="cart-visa-remove-button"
                                        >
                                            Vizeyi çıkar, sadece sigorta + eSIM öde
                                        </Button>
                                        <p className="text-xs leading-5 text-muted-foreground">
                                            Başvurunuzu tamamladığınızda sepetiniz otomatik boşalır; poliçeniz ve eSIM
                                            QR kodunuz e-postanıza gelir.
                                        </p>
                                    </div>
                                ) : (
                                <div className="space-y-4 border-t border-border pt-5">
                                    <div className="space-y-2">
                                        <Label htmlFor="cart-name">Ad soyad</Label>
                                        <Input
                                            id="cart-name"
                                            value={form.full_name}
                                            onChange={set("full_name")}
                                            placeholder="Adınız ve soyadınız"
                                            data-testid="cart-name-input"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="cart-email">E-posta</Label>
                                        <Input
                                            id="cart-email"
                                            type="email"
                                            value={form.email}
                                            onChange={set("email")}
                                            placeholder="ornek@eposta.com"
                                            data-testid="cart-email-input"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label htmlFor="cart-phone">Telefon</Label>
                                        <Input
                                            id="cart-phone"
                                            value={form.phone}
                                            onChange={set("phone")}
                                            placeholder="+90 5XX XXX XX XX"
                                            data-testid="cart-phone-input"
                                        />
                                    </div>

                                    <div className="grid gap-3 sm:grid-cols-2">
                                        <div className="space-y-2">
                                            <Label htmlFor="cart-start">Gidiş tarihi (opsiyonel)</Label>
                                            <DateField
                                                id="cart-start"
                                                value={form.travel_start}
                                                onChange={(v) => setForm((f) => ({ ...f, travel_start: v }))}
                                                data-testid="cart-start-input"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="cart-end">Dönüş tarihi (opsiyonel)</Label>
                                            <DateField
                                                id="cart-end"
                                                value={form.travel_end}
                                                onChange={(v) => setForm((f) => ({ ...f, travel_end: v }))}
                                                data-testid="cart-end-input"
                                            />
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="cart-application">Vize başvuru kodunuz (varsa)</Label>
                                        <Input
                                            id="cart-application"
                                            value={form.application_reference}
                                            onChange={(e) =>
                                                setForm((f) => ({
                                                    ...f,
                                                    application_reference: e.target.value.toUpperCase(),
                                                }))
                                            }
                                            placeholder="DV-XXXXXX"
                                            data-testid="cart-application-input"
                                        />
                                        <p className="text-xs leading-5 text-muted-foreground">
                                            Daha önce vize başvurusu yaptıysanız kodunuzu yazın; hizmetleri o
                                            başvurunuza bağlarız.
                                        </p>
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="cart-note">Not (opsiyonel)</Label>
                                        <Textarea
                                            id="cart-note"
                                            rows={3}
                                            value={form.note}
                                            onChange={set("note")}
                                            placeholder="Telefon modeli, poliçe için özel durum, otel adı vb."
                                            data-testid="cart-note-input"
                                        />
                                    </div>

                                    <div>
                                        <Label className="mb-2 block">Ödeme yöntemi</Label>
                                        <div className="grid gap-3 sm:grid-cols-2">
                                            {[
                                                { id: "card", label: "Kredi / banka kartı", icon: CreditCard },
                                                { id: "transfer", label: "Havale / EFT", icon: Landmark },
                                            ].map(({ id, label, icon: Icon }) => (
                                                <button
                                                    key={id}
                                                    type="button"
                                                    onClick={() => setMethod(id)}
                                                    className={`flex min-h-[52px] items-center gap-2.5 rounded-xl border-2 px-4 text-sm font-semibold transition-colors duration-150 ${
                                                        method === id
                                                            ? "border-primary bg-primary/[0.07] text-foreground"
                                                            : "border-border bg-card text-muted-foreground hover:border-primary/50"
                                                    }`}
                                                    data-testid={`cart-payment-${id}`}
                                                >
                                                    <Icon className="h-4 w-4 text-primary" />
                                                    {label}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <Button
                                        className="h-12 w-full text-base"
                                        onClick={submit}
                                        disabled={submitting}
                                        data-testid="cart-checkout-button"
                                    >
                                        {submitting ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sipariş
                                                oluşturuluyor…
                                            </>
                                        ) : method === "card" ? (
                                            <>
                                                <CreditCard className="mr-2 h-4 w-4" /> Kartla öde{" "}
                                                {formatMoney(total)}
                                            </>
                                        ) : (
                                            <>
                                                <Landmark className="mr-2 h-4 w-4" /> Havale bilgilerini al
                                            </>
                                        )}
                                    </Button>
                                    <p className="text-xs leading-5 text-muted-foreground">
                                        Ödemeniz onaylandığında eSIM QR kodunuz, poliçeniz ve tur kuponunuz
                                        e-posta adresinize gönderilir. Siparişinizi{" "}
                                        <Link to="/hesabim" className="font-semibold text-primary hover:underline">
                                            Başvurularım
                                        </Link>{" "}
                                        sayfasından da takip edebilirsiniz.
                                    </p>
                                </div>
                                )}
                            </div>
                        </div>
                    )}
                    <LastOrderShortcut />
                </div>
            </section>
        </div>
    );
}
