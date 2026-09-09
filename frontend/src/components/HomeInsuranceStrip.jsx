import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, FileCheck2, Globe2, Plus, ShieldCheck, ShoppingBag } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";
import { formatMoney, IMAGES } from "../lib/site";
import { useCart } from "../lib/cart";
import { Button } from "./ui/button";

const HIGHLIGHTS = [
    { icon: Globe2, text: "Yedi emirliğin tamamında geçerli · 30.000 € teminat" },
    { icon: FileCheck2, text: "TC kimlik bilgisiyle düzenlenir, e-poliçe PDF olarak gelir" },
    { icon: ShieldCheck, text: "Vize başvurusu şart değil, tek başına satın alınır" },
];

/** Ana sayfa: vize almadan da alınabilen seyahat sağlık sigortası şeridi. */
export const HomeInsuranceStrip = () => {
    const [plans, setPlans] = useState([]);
    const cart = useCart();

    useEffect(() => {
        api.get("/products", { params: { kind: "insurance" } })
            .then(({ data }) => setPlans(data.items || []))
            .catch(() => setPlans([]));
    }, []);

    if (!plans.length) return null;

    const sorted = [...plans].sort((a, b) => (a.validity_days || 0) - (b.validity_days || 0));
    const cheapest = sorted[0];

    const addPlan = (plan) => {
        const res = cart.add(plan.id, 1);
        if (!res.ok) return toast.error("Sepete en fazla 6 farklı ürün ekleyebilirsiniz.");
        toast.success(`${plan.validity_days} günlük poliçe sepete eklendi.`, {
            description: "Sepette sigortalının adı, TC kimlik no ve doğum tarihini gireceksiniz.",
            action: { label: "Sepete git", onClick: () => window.location.assign("/sepet") },
        });
    };

    return (
        <section className="section" data-testid="home-insurance-strip">
            <div className="container-page">
                <div
                    className="grid overflow-hidden rounded-[var(--radius-lg)] border border-border bg-card lg:grid-cols-[1.1fr_0.8fr]"
                    style={{ boxShadow: "var(--shadow-card)" }}
                >
                    <div className="flex flex-col justify-center p-5 sm:p-10">
                        <span className="text-xs font-bold uppercase tracking-[0.18em] text-primary">
                            Sadece sigorta
                        </span>
                        <h2 className="mt-3 font-heading text-2xl font-extrabold leading-tight sm:text-3xl">
                            Seyahat sağlık sigortasını vizeden bağımsız, tek başına alın
                        </h2>
                        <p className="mt-3 max-w-xl text-sm leading-6 text-muted-foreground sm:leading-7 md:text-lg">
                            Vizesi hazır olan ya da başka bir ülkeye gidenler de poliçe alabilir. Süreyi seçin,
                            sigortalı bilgilerini girin; poliçeniz ödeme sonrası PDF olarak e-postanıza düşer.
                        </p>

                        <div
                            className="mt-5 grid grid-cols-2 gap-2 sm:mt-6 sm:gap-2.5 lg:grid-cols-4"
                            data-testid="home-insurance-plans"
                        >
                            {sorted.map((plan) => (
                                <button
                                    key={plan.id}
                                    type="button"
                                    onClick={() => addPlan(plan)}
                                    className="group rounded-xl border border-border bg-[hsl(var(--cloud))] p-3 text-left transition-[border-color,transform,background-color] duration-200 hover:-translate-y-0.5 hover:border-primary/60 hover:bg-card sm:p-3.5"
                                    data-testid={`home-insurance-add-${plan.id}`}
                                >
                                    <span className="text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
                                        {plan.validity_days} gün
                                    </span>
                                    <span className="mt-1.5 block font-heading text-lg font-extrabold leading-none">
                                        {formatMoney(plan.price, plan.currency)}
                                    </span>
                                    <span className="mt-1 block text-[11px] text-muted-foreground">kişi başı</span>
                                    <span className="mt-2 inline-flex items-center gap-1 text-xs font-bold text-primary">
                                        <Plus className="h-3.5 w-3.5" aria-hidden="true" /> Sepete ekle
                                    </span>
                                </button>
                            ))}
                        </div>

                        <ul className="mt-5 space-y-1.5 sm:mt-6 sm:space-y-2.5">
                            {HIGHLIGHTS.map(({ icon: Icon, text }) => (
                                <li key={text} className="flex items-start gap-2.5 text-xs sm:text-sm">
                                    <Icon className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                    {text}
                                </li>
                            ))}
                        </ul>

                        <div className="mt-5 flex flex-wrap items-center gap-3 sm:mt-7">
                            <Button
                                asChild
                                className="h-12 w-full px-7 text-base sm:w-auto"
                                data-testid="home-insurance-cta"
                            >
                                <Link to="/seyahat-sigortasi">
                                    Teminatları gör & poliçe seç <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                            <Button
                                asChild
                                variant="secondary"
                                className="hidden h-12 border border-border px-6 text-base sm:inline-flex"
                                data-testid="home-insurance-cart-link"
                            >
                                <Link to="/sepet">
                                    <ShoppingBag className="mr-2 h-4 w-4" />
                                    Sepetim{cart.count > 0 ? ` (${cart.count})` : ""}
                                </Link>
                            </Button>
                        </div>
                    </div>

                    <div className="relative min-h-[150px] sm:min-h-[240px]">
                        <img
                            src={IMAGES.travelInsurance}
                            alt="Türk pasaportu ve İstanbul - Dubai biniş kartı"
                            className="absolute inset-0 h-full w-full object-cover object-center"
                            loading="lazy"
                            decoding="async"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-foreground/75 via-foreground/15 to-transparent" />
                        <div className="absolute inset-x-0 bottom-0 p-6">
                            <p className="font-heading text-2xl font-extrabold text-white">
                                {formatMoney(cheapest.price, cheapest.currency)}
                                <span className="ml-1.5 text-sm font-semibold text-white/80">’den başlayan</span>
                            </p>
                            <p className="mt-1 text-xs font-semibold text-white/85">
                                {cheapest.validity_days} günlük poliçe · kişi başı
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};
