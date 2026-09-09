import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Star, Users } from "lucide-react";
import { api } from "../lib/api";
import { formatMoney } from "../lib/site";
import { Button } from "./ui/button";
import { VisaTypeCard } from "./VisaTypeCard";
import { AddonCard } from "./AddonCard";
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
    const [guideSlugs, setGuideSlugs] = useState([]);
    const [active, setActive] = useState("single");
    const [pickedId, setPickedId] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([api.get("/visa-types"), api.get("/content/site"), api.get("/visa-guides")])
            .then(([v, c, g]) => {
                setVisaTypes(v.data);
                setCategories(c.data.visa_categories || []);
                setAddons(c.data.addons || []);
                setDiscountText(c.data.family_discount_text || "");
                setGuideSlugs((g.data.items || []).map((i) => i.slug));
            })
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    const visible = visaTypes.filter((v) => (v.category || "single") === active);
    // Baslangicta "en cok tercih edilen" kart vurgulu gelir; kullanici baska bir karta
    // tiklarsa vurgu o karta gecer.
    const highlightedId = visible.some((v) => v.id === pickedId)
        ? pickedId
        : visible.find((v) => v.popular)?.id;

    return (
        <div data-testid="pricing-tabs">
            <div className="flex justify-center">
                <div
                    className="inline-flex max-w-full flex-wrap justify-center gap-1 rounded-2xl border border-border bg-card p-1.5"
                    role="tablist"
                    style={{ boxShadow: "var(--shadow-card)" }}
                >
                    {categories.map((c) => (
                        <button
                            key={c.id}
                            type="button"
                            role="tab"
                            aria-selected={active === c.id}
                            onClick={() => {
                                setActive(c.id);
                                setPickedId(null);
                            }}
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

            <div
                className={`mt-7 grid gap-6 ${
                    loading || visible.length === 3
                        ? "md:grid-cols-2 lg:grid-cols-3"
                        : visible.length >= 4
                          ? "md:grid-cols-2 xl:grid-cols-4"
                          : visible.length === 2
                            ? "md:grid-cols-2"
                            : "md:grid-cols-1"
                }`}
                data-testid="pricing-grid"
            >
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
                    : visible.map((visa) => (
                          <VisaTypeCard
                              key={visa.id}
                              visa={visa}
                              hasGuide={guideSlugs.includes(visa.slug)}
                              selected={visa.id === highlightedId}
                              onHighlight={(v) => setPickedId(v.id)}
                          />
                      ))}
            </div>

            {!compactHeading && addons.length > 0 && (
                <div className="mt-12">
                    <h3 className="font-heading text-xl font-bold">Ek hizmetler</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Başvuru sırasında dilediğiniz ek hizmeti seçebilirsiniz. Ücretler yolcu başınadır.
                    </p>
                    <div className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {addons.map((a) => (
                            <AddonCard key={a.id} addon={a} />
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
