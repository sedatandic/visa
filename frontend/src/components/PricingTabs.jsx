import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Check, Clock, Star, Users } from "lucide-react";
import { api } from "../lib/api";
import { formatMoney } from "../lib/site";
import { Button } from "./ui/button";
import { VisaTypeCard } from "./VisaTypeCard";
import { Skeleton } from "./ui/skeleton";

/**
 * Category-tabbed pricing block (Tek Girisli / Cok Girisli / Cocuk / Diger)
 * plus the paid add-on cards. Used on the home page and the pricing page.
 */
export const PricingTabs = ({ compactHeading = false }) => {
    const [visaTypes, setVisaTypes] = useState([]);
    const [categories, setCategories] = useState([]);
    const [addons, setAddons] = useState([]);
    const [discountText, setDiscountText] = useState("");
    const [active, setActive] = useState("single");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([api.get("/visa-types"), api.get("/content/site")])
            .then(([v, c]) => {
                setVisaTypes(v.data);
                setCategories(c.data.visa_categories || []);
                setAddons(c.data.addons || []);
                setDiscountText(c.data.family_discount_text || "");
            })
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    const visible = visaTypes.filter((v) => (v.category || "single") === active);

    return (
        <div data-testid="pricing-tabs">
            <div
                className="inline-flex max-w-full flex-wrap gap-1 rounded-2xl border border-border bg-card p-1.5"
                role="tablist"
                style={{ boxShadow: "var(--shadow-card)" }}
            >
                {categories.map((c) => (
                    <button
                        key={c.id}
                        type="button"
                        role="tab"
                        aria-selected={active === c.id}
                        onClick={() => setActive(c.id)}
                        data-testid={`pricing-tab-${c.id}`}
                        className={`min-h-[44px] rounded-xl px-4 text-sm font-bold transition-colors duration-150 focus-visible:outline-none ${
                            active === c.id
                                ? "bg-primary text-primary-foreground"
                                : "text-foreground/75 hover:bg-muted hover:text-foreground"
                        }`}
                    >
                        {c.label}
                    </button>
                ))}
            </div>

            {discountText && (
                <div className="mt-5 flex items-start gap-2.5 rounded-xl border border-primary/25 bg-primary/5 p-4">
                    <Users className="mt-0.5 h-4.5 w-4.5 shrink-0 text-primary" />
                    <p className="text-sm leading-6 text-foreground/85" data-testid="family-discount-text">
                        <strong className="font-semibold">Aile indirimi:</strong> {discountText} Tek formda tüm
                        aileyi ekleyebilirsiniz.
                    </p>
                </div>
            )}

            <div className="mt-7 grid gap-6 md:grid-cols-2 lg:grid-cols-3" data-testid="pricing-grid">
                {loading
                    ? [0, 1, 2].map((i) => (
                          <div key={i} className="card-surface p-6" data-testid={`pricing-skeleton-${i}`}>
                              <Skeleton className="h-5 w-24" />
                              <Skeleton className="mt-4 h-6 w-4/5" />
                              <Skeleton className="mt-2 h-4 w-full" />
                              <Skeleton className="mt-5 h-24 w-full rounded-xl" />
                              <Skeleton className="mt-5 h-4 w-3/4" />
                              <Skeleton className="mt-2.5 h-4 w-2/3" />
                              <Skeleton className="mt-6 h-12 w-full rounded-xl" />
                          </div>
                      ))
                    : visible.map((visa) => <VisaTypeCard key={visa.id} visa={visa} />)}
            </div>

            {!compactHeading && addons.length > 0 && (
                <div className="mt-12">
                    <h3 className="font-heading text-xl font-bold">Ek hizmetler</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Başvuru sırasında dilediğiniz ek hizmeti seçebilirsiniz. Ücretler yolcu başınadır.
                    </p>
                    <div className="mt-6 grid gap-6 md:grid-cols-2">
                        {addons.map((a) => (
                            <div key={a.id} className="card-surface p-6" data-testid={`addon-card-${a.id}`}>
                                <div className="flex items-start justify-between gap-4">
                                    <h4 className="font-heading text-lg font-bold">{a.name}</h4>
                                    <span className="whitespace-nowrap rounded-lg bg-[hsl(var(--sand-surface))] px-3 py-1.5 font-heading text-sm font-bold">
                                        + {formatMoney(a.price, a.currency)}
                                    </span>
                                </div>
                                <p className="mt-2 text-sm leading-6 text-muted-foreground">{a.description}</p>
                                <ul className="mt-4 space-y-2">
                                    {(a.features || []).map((f) => (
                                        <li key={f} className="flex items-start gap-2 text-sm">
                                            <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                            {f}
                                        </li>
                                    ))}
                                </ul>
                                <p className="mt-4 flex items-center gap-1.5 text-xs text-muted-foreground">
                                    <Clock className="h-3.5 w-3.5" /> Başvuru formunun 2. adımında seçilebilir
                                </p>
                            </div>
                        ))}
                    </div>
                    <div className="mt-8 flex flex-col items-start gap-4 rounded-xl border border-border bg-[hsl(var(--cloud))] p-6 sm:flex-row sm:items-center sm:justify-between">
                        <p className="flex items-center gap-2 text-sm font-semibold">
                            <Star className="h-4 w-4 text-[hsl(var(--gold))]" />
                            Hangi vizeyi seçeceğinizden emin değil misiniz? Danışmanımız ücretsiz yönlendirsin.
                        </p>
                        <div className="flex gap-3">
                            <Button asChild variant="secondary" className="h-11 border border-border">
                                <Link to="/iletisim">Bize sorun</Link>
                            </Button>
                            <Button asChild className="h-11">
                                <Link to="/basvuru">Başvuruya başla</Link>
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
