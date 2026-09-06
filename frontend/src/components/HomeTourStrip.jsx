import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Clock, MapPin, ShoppingBag, Users } from "lucide-react";
import { api } from "../lib/api";
import { formatMoney } from "../lib/site";
import { useCart } from "../lib/cart";
import { Button } from "./ui/button";

const HIGHLIGHTS = [
    { icon: MapPin, text: "Otelinizden alış ve dönüş dahil" },
    { icon: Users, text: "Türkçe konuşan rehber eşliğinde" },
    { icon: Clock, text: "Yaklaşık 7 saat · öğleden sonra başlar" },
];

/** Ana sayfa çöl safarisi tanıtım şeridi: turları gösterir, sepete yönlendirir. */
export const HomeTourStrip = () => {
    const [tours, setTours] = useState([]);
    const { count } = useCart();

    useEffect(() => {
        api.get("/products", { params: { kind: "tour" } })
            .then(({ data }) => setTours(data.items || []))
            .catch(() => setTours([]));
    }, []);

    if (!tours.length) return null;

    const cheapest = tours.reduce((min, t) => (t.price < min.price ? t : min), tours[0]);

    return (
        <section className="section" data-testid="home-tour-strip">
            <div className="container-page">
                <div
                    className="grid overflow-hidden rounded-[var(--radius-lg)] border border-border bg-card lg:grid-cols-[1.05fr_1fr]"
                    style={{ boxShadow: "var(--shadow-card)" }}
                >
                    <div className="flex flex-col justify-center p-7 sm:p-10">
                        <span className="text-xs font-bold uppercase tracking-[0.18em] text-primary">
                            Dubai turları
                        </span>
                        <h2 className="mt-3 font-heading text-2xl font-extrabold leading-tight sm:text-3xl">
                            Çöl safarisi: kumul turu, deve gezisi ve Arap kampında akşam yemeği
                        </h2>
                        <p className="mt-3 max-w-xl text-sm leading-7 text-muted-foreground md:text-lg">
                            Vizeniz hazır olsun ya da olmasın turu ayrı satın alabilirsiniz. Tarih ve otelden
                            alınış saatini seçin, sepete ekleyin; rezervasyonu biz yapar, kupon ve buluşma
                            bilgilerini e-postanıza göndeririz.
                        </p>

                        <ul className="mt-5 space-y-2.5">
                            {HIGHLIGHTS.map(({ icon: Icon, text }) => (
                                <li key={text} className="flex items-center gap-2.5 text-sm">
                                    <Icon className="h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                    {text}
                                </li>
                            ))}
                        </ul>

                        <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3">
                            <div>
                                <p className="text-xs text-muted-foreground">Kişi başı</p>
                                <p className="font-heading text-2xl font-extrabold" data-testid="home-tour-price">
                                    {formatMoney(cheapest.price, cheapest.currency)}
                                    <span className="ml-1 text-sm font-semibold text-muted-foreground">
                                        ’den başlayan
                                    </span>
                                </p>
                            </div>
                            <div className="flex flex-wrap gap-3">
                                <Button asChild className="h-12 px-7 text-base" data-testid="home-tour-cta">
                                    <Link to="/dubai-turlari">
                                        Tarih seç & sepete ekle <ArrowRight className="ml-2 h-4 w-4" />
                                    </Link>
                                </Button>
                                <Button
                                    asChild
                                    variant="secondary"
                                    className="h-12 border border-border px-6 text-base"
                                    data-testid="home-tour-cart-link"
                                >
                                    <Link to="/sepet">
                                        <ShoppingBag className="mr-2 h-4 w-4" />
                                        Sepetim{count > 0 ? ` (${count})` : ""}
                                    </Link>
                                </Button>
                            </div>
                        </div>
                    </div>

                    <div className="grid gap-1.5 bg-muted/40 p-1.5 lg:gap-2 lg:p-2">
                        {tours.map((t) => (
                            <Link
                                key={t.id}
                                to="/dubai-turlari"
                                className="group relative min-h-[180px] overflow-hidden rounded-xl"
                                data-testid={`home-tour-photo-${t.id}`}
                            >
                                <img
                                    src={t.image_url}
                                    alt={t.name}
                                    className="absolute inset-0 h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                                    loading="lazy"
                                />
                                <span className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-foreground/80 to-transparent p-3 pt-8 text-xs font-bold text-white">
                                    {t.name}
                                </span>
                            </Link>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
};
