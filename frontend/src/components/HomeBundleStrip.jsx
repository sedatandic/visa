import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
    ArrowRight,
    Baby,
    Check,
    Minus,
    Plane,
    Plus,
    ShieldCheck,
    ShoppingBag,
    Signal,
    Sparkles,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { applyPath, formatMoney } from "../lib/site";
import { useCart } from "../lib/cart";

const PICKS = ["pack_standard", "pack_family", "pack_long"];

const Stepper = ({ label, value, min, max, onChange, testId }) => (
    <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold">{label}</span>
        <div className="flex items-center gap-1.5">
            <button
                type="button"
                onClick={() => onChange(Math.max(min, value - 1))}
                disabled={value <= min}
                aria-label={`${label} azalt`}
                className="flex h-7 w-7 items-center justify-center rounded-md border border-border bg-card transition-colors duration-150 hover:border-primary/60 hover:text-primary disabled:opacity-40"
                data-testid={`${testId}-minus`}
            >
                <Minus className="h-3 w-3" />
            </button>
            <span className="min-w-5 text-center font-heading text-sm font-bold" data-testid={testId}>
                {value}
            </span>
            <button
                type="button"
                onClick={() => onChange(Math.min(max, value + 1))}
                disabled={value >= max}
                aria-label={`${label} artır`}
                className="flex h-7 w-7 items-center justify-center rounded-md border border-border bg-card transition-colors duration-150 hover:border-primary/60 hover:text-primary disabled:opacity-40"
                data-testid={`${testId}-plus`}
            >
                <Plus className="h-3 w-3" />
            </button>
        </div>
    </div>
);

const BundleCard = ({ bundle, highlighted }) => {
    const cart = useCart();
    const [adults, setAdults] = useState(bundle.family?.adults || 1);
    const [children, setChildren] = useState(bundle.family?.children || 0);
    const [withTour, setWithTour] = useState(false);
    const [quote, setQuote] = useState(null);
    const isFamily = !!bundle.family;

    // Yolcu sayisi / tur secimi degisince fiyati sunucudan yeniden al
    useEffect(() => {
        if (!isFamily) return;
        let alive = true;
        const timer = setTimeout(() => {
            api.get("/bundles/quote", {
                params: { bundle_id: bundle.id, adults, children, tour: withTour },
            })
                .then(({ data }) => alive && setQuote(data.item))
                .catch(() => {});
        }, 180);
        return () => {
            alive = false;
            clearTimeout(timer);
        };
    }, [isFamily, bundle.id, adults, children, withTour]);

    const b = quote || bundle;
    const qty = b.quantities || {};
    const travelers = isFamily ? adults + children : 1;
    const applyHref = applyPath({
        paket: b.id,
        vize: b.visa ? b.visa.id : null,
        query: isFamily ? `yetiskin=${adults}&cocuk=${children}${withTour ? "&tur=1" : ""}` : "",
    });

    const addToCart = () => {
        const visas = [];
        if (b.visa) visas.push({ visa_type_id: b.visa.id, quantity: isFamily ? adults : 1 });
        if (isFamily && children && b.family?.child_visa) {
            visas.push({ visa_type_id: b.family.child_visa.id, quantity: children });
        }
        const items = [
            { product_id: b.insurance?.id, quantity: qty.insurance || 1 },
            { product_id: b.esim?.id, quantity: qty.esim || 1 },
        ];
        if (qty.tour && b.tour) items.push({ product_id: b.tour.id, quantity: qty.tour });
        const res = cart.addMany(items.filter((i) => i.product_id), { bundleId: b.id, visas });
        if (!res.ok) {
            toast.error("Sepete en fazla 6 farklı ürün ekleyebilirsiniz.");
            return;
        }
        const detail = isFamily
            ? `${adults} yetişkin${children ? ` + ${children} çocuk` : ""} vizesi, ${qty.insurance} sigorta, ${qty.esim} eSIM${
                  qty.tour ? `, ${qty.tour} kişilik çöl safarisi` : ""
              }`
            : "vize + sigorta + eSIM";
        toast.success(`${b.name} sepete eklendi: ${detail}.`, {
            action: { label: "Sepete git", onClick: () => window.location.assign("/sepet") },
        });
    };

    return (
        <div
            className={`group flex h-full flex-col rounded-2xl border-2 bg-card p-6 text-left transition-all duration-200 hover:-translate-y-1 ${
                highlighted ? "border-primary" : "border-border hover:border-primary/60"
            }`}
            style={{ boxShadow: highlighted ? "var(--shadow-soft)" : "var(--shadow-card)" }}
            data-testid={`home-bundle-${b.id}`}
        >
            <div className="flex items-start justify-between gap-2">
                <div>
                    <p className="font-heading text-base font-bold">{b.name}</p>
                    <p
                        className="mt-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                        data-testid={`home-bundle-subtitle-${b.id}`}
                    >
                        {isFamily
                            ? `${adults} yetişkin${children ? ` + ${children} çocuk` : ""}${withTour ? " · tam tatil" : ""}`
                            : `${b.visa_days} günlük vize için`}
                    </p>
                </div>
                {isFamily ? (
                    <span className="rounded-full bg-[hsl(var(--cream-tag))] px-2.5 py-1 text-[11px] font-bold">
                        Aile
                    </span>
                ) : (
                    highlighted && (
                        <span className="rounded-full bg-[hsl(var(--cream-tag))] px-2.5 py-1 text-[11px] font-bold">
                            En çok seçilen
                        </span>
                    )
                )}
            </div>

            <p className="mt-3 text-sm leading-6 text-muted-foreground">{b.tagline}</p>

            {isFamily && (
                <div
                    className="mt-4 space-y-2.5 rounded-xl border border-border bg-[hsl(var(--cloud))] p-3.5"
                    data-testid={`home-bundle-config-${b.id}`}
                >
                    <Stepper
                        label="Yetişkin"
                        value={adults}
                        min={1}
                        max={b.family?.max_adults || 6}
                        onChange={setAdults}
                        testId={`home-bundle-adults-${b.id}`}
                    />
                    <Stepper
                        label="Çocuk (0-17)"
                        value={children}
                        min={0}
                        max={b.family?.max_children || 4}
                        onChange={setChildren}
                        testId={`home-bundle-children-${b.id}`}
                    />
                    {b.tour && (
                        <label className="flex cursor-pointer items-start gap-2.5 border-t border-border pt-2.5 text-xs leading-5">
                            <input
                                type="checkbox"
                                checked={withTour}
                                onChange={(e) => setWithTour(e.target.checked)}
                                className="mt-0.5 h-4 w-4 shrink-0 accent-[hsl(var(--primary))]"
                                data-testid={`home-bundle-tour-toggle-${b.id}`}
                            />
                            <span>
                                <strong>Tam tatil:</strong> {travelers} kişilik çöl safarisi ekle
                                <span className="block text-muted-foreground">
                                    {formatMoney(b.tour.price, b.currency)} / kişi · kumul turu, deve gezisi ve
                                    akşam yemeği
                                </span>
                            </span>
                        </label>
                    )}
                </div>
            )}

            <ul className="mt-4 space-y-2.5 text-sm">
                {b.visa && (
                    <li className="flex items-start gap-2.5">
                        <Plane className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                        <span>
                            {b.visa.name}
                            {isFamily && adults > 1 ? ` × ${adults}` : ""}
                            <span className="block text-xs text-muted-foreground">
                                {formatMoney(b.visa.price, b.currency)} / yetişkin
                            </span>
                        </span>
                    </li>
                )}
                {isFamily && children > 0 && b.family?.child_visa && (
                    <li className="flex items-start gap-2.5">
                        <Baby className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                        <span>
                            {b.family.child_visa.name}
                            {children > 1 ? ` × ${children}` : ""}
                            <span className="block text-xs text-muted-foreground">
                                {formatMoney(b.family.child_visa.price, b.currency)} / çocuk
                            </span>
                        </span>
                    </li>
                )}
                <li className="flex items-start gap-2.5">
                    <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                    <span>
                        {b.insurance.name}
                        {qty.insurance > 1 ? ` × ${qty.insurance}` : ""}
                        <span className="block text-xs text-muted-foreground">{b.insurance.coverage}</span>
                    </span>
                </li>
                <li className="flex items-start gap-2.5">
                    <Signal className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                    <span>
                        {b.esim.name}
                        {qty.esim > 1 ? ` × ${qty.esim}` : ""}
                        <span className="block text-xs text-muted-foreground">
                            {b.esim.data_amount} veri · {b.esim.validity_days} gün
                        </span>
                    </span>
                </li>
                {qty.tour > 0 && b.tour && (
                    <li className="flex items-start gap-2.5" data-testid={`home-bundle-tour-line-${b.id}`}>
                        <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                        <span>
                            {b.tour.name} × {qty.tour}
                            <span className="block text-xs text-muted-foreground">
                                {formatMoney(b.tour.total, b.currency)} · otelden alınış
                            </span>
                        </span>
                    </li>
                )}
                <li className="flex items-start gap-2.5">
                    <Check
                        className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--brand-green))]"
                        aria-hidden="true"
                    />
                    <span className="font-semibold text-[hsl(var(--brand-green))]">
                        {formatMoney(b.discount + (b.family?.visa_discount || 0), b.currency)} indirim
                        {b.family?.visa_discount ? " (paket + aile)" : " (paket)"}
                    </span>
                </li>
            </ul>

            <div className="mt-auto pt-5">
                <p className="text-xs text-muted-foreground">Vize dahil toplam</p>
                <p
                    className="tabular font-heading text-3xl font-extrabold leading-none tracking-tight text-[hsl(30_62%_38%)]"
                    data-testid={`home-bundle-price-${b.id}`}
                >
                    {formatMoney(b.total_with_visa ?? b.price, b.currency)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground" data-testid={`home-bundle-price-note-${b.id}`}>
                    {isFamily ? `${b.family?.traveler_count || travelers} kişi` : "kişi başı"} · ekstralar{" "}
                    {formatMoney(b.price, b.currency)}
                </p>
                <div className="mt-4 flex flex-col gap-2.5">
                    <Link
                        to={applyHref}
                        className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-full bg-primary px-6 text-sm font-semibold text-primary-foreground transition-transform duration-150 hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
                        data-testid={`home-bundle-cta-${b.id}`}
                    >
                        Bu paketle başvur <ArrowRight className="h-4 w-4" aria-hidden="true" />
                    </Link>
                    <button
                        type="button"
                        onClick={addToCart}
                        className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-full border-2 border-border px-6 text-sm font-semibold text-foreground transition-colors duration-150 hover:border-primary/60 hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
                        data-testid={`home-bundle-add-to-cart-${b.id}`}
                    >
                        <ShoppingBag className="h-4 w-4" aria-hidden="true" /> Paketi sepete ekle
                    </button>
                    <p className="text-center text-[11px] leading-4 text-muted-foreground">
                        Formda {isFamily ? "yolcular, " : ""}sigorta ve eSIM
                        {qty.tour > 0 ? ", çöl safarisi" : ""} seçili gelir
                    </p>
                </div>
            </div>
        </div>
    );
};

export const HomeBundleStrip = () => {
    const [bundles, setBundles] = useState([]);

    useEffect(() => {
        api.get("/bundles")
            .then(({ data }) => {
                const items = (data.items || []).filter((b) => PICKS.includes(b.id));
                setBundles(items.length ? items : (data.items || []).slice(0, 3));
            })
            .catch(() => setBundles([]));
    }, []);

    if (!bundles.length) return null;
    // Ayni seritte iki "En cok secilen" etiketi cikmasin: yalnizca ilk populer paket isaretlenir.
    const popularId = bundles.find((b) => b.popular)?.id;

    return (
        <section className="section" data-testid="home-bundle-strip">
            <div className="container-page">
                <span className="inline-flex items-center gap-2 rounded-full bg-[hsl(var(--cream-tag))] px-3.5 py-1.5 text-xs font-bold uppercase tracking-wider">
                    <Sparkles className="h-3.5 w-3.5" aria-hidden="true" /> Seyahat paketleri
                </span>
                <h2 className="mt-4 max-w-2xl font-heading text-2xl font-extrabold leading-tight text-[hsl(30_62%_38%)] sm:text-3xl">
                    Vize + sigorta + eSIM, tek başvuruda
                </h2>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground sm:text-base">
                    Sigorta ve internet paketini vizenizle birlikte alın; paket indirimi otomatik
                    uygulanır, poliçe ve QR kod e-postanıza gelir. Seçtiğiniz paket başvuru formunda
                    aynen seçili gelir — istediğinizi tek tıkla değiştirebilirsiniz.
                </p>

                <div className="mt-7 -mx-4 flex snap-x snap-mandatory gap-4 overflow-x-auto px-4 pb-3 lg:mx-0 lg:grid lg:grid-cols-3 lg:gap-5 lg:overflow-visible lg:px-0 lg:pb-0">
                    {bundles.map((b) => (
                        <div key={b.id} className="w-full shrink-0 snap-start lg:w-auto">
                            <BundleCard bundle={b} highlighted={b.id === popularId} />
                        </div>
                    ))}
                </div>
                <p className="mt-2 text-xs text-muted-foreground lg:hidden" data-testid="home-bundle-swipe-hint">
                    Paketleri görmek için yana kaydırın
                </p>
            </div>
        </section>
    );
};
