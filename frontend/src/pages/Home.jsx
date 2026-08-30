import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
    ArrowRight,
    BadgeCheck,
    Banknote,
    Clock,
    FileCheck2,
    HeadphonesIcon,
    Quote,
    ShieldCheck,
    Sparkles,
    Star,
} from "lucide-react";
import { motion } from "framer-motion";
import { api } from "../lib/api";
import { IMAGES, formatMoney, setMeta } from "../lib/site";
import { Button } from "../components/ui/button";
import { VisaTypeCard } from "../components/VisaTypeCard";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "../components/ui/accordion";

const WHY_ICONS = [Banknote, FileCheck2, Clock, HeadphonesIcon];

export default function Home() {
    const [visaTypes, setVisaTypes] = useState([]);
    const [content, setContent] = useState(null);

    useEffect(() => {
        setMeta(
            "Dubai Vizesi Başvurusu | VizeAtlas Dubai",
            "Dubai (BAE) vizesi için online başvuru: net fiyatlar, 5 dakikada form, belge kontrolü ve 3-5 iş gününde sonuç. Başvurunuzu takip kodu ile izleyin."
        );
        api.get("/visa-types").then(({ data }) => setVisaTypes(data)).catch(() => {});
        api.get("/content/site").then(({ data }) => setContent(data)).catch(() => {});
    }, []);

    const teaser = visaTypes.slice(0, 3);
    const cheapest = visaTypes.length
        ? Math.min(...visaTypes.map((v) => Number(v.price)))
        : null;

    return (
        <div data-testid="home-page">
            {/* HERO */}
            <section className="relative overflow-hidden border-b border-border bg-card" data-testid="landing-hero">
                <div className="hero-glow absolute inset-0" aria-hidden="true" />
                <div className="container-page relative grid items-center gap-12 py-14 lg:grid-cols-[1.05fr_0.95fr] lg:py-20">
                    <motion.div
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.45 }}
                    >
                        <span className="eyebrow">
                            <Sparkles className="h-3.5 w-3.5" /> Birleşik Arap Emirlikleri Vize Danışmanlığı
                        </span>
                        <h1 className="mt-5 text-4xl font-bold leading-[1.08] sm:text-5xl lg:text-[56px]">
                            Dubai vizeniz,
                            <br />
                            <span className="text-primary">karmaşıklık olmadan.</span>
                        </h1>
                        <p className="mt-5 max-w-xl text-base leading-7 text-muted-foreground sm:text-lg">
                            Formu 5 dakikada doldurun, pasaport ve fotoğrafınızı yükleyin. Belgelerinizi
                            danışmanlarımız kontrol eder, başvurunuzu biz takip ederiz. Vizeniz dijital
                            olarak e-postanıza gelir.
                        </p>

                        <div className="mt-8 flex flex-wrap items-center gap-3">
                            <Button asChild className="h-12 px-7 text-base" data-testid="hero-apply-now-button">
                                <Link to="/basvuru">
                                    Başvuru Yap <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                            <Button
                                asChild
                                variant="secondary"
                                className="h-12 border border-border px-7 text-base"
                                data-testid="hero-pricing-button"
                            >
                                <Link to="/vize-tipleri">Fiyatları Gör</Link>
                            </Button>
                        </div>

                        {cheapest !== null && (
                            <p className="mt-4 text-sm text-muted-foreground">
                                Başlangıç fiyatı{" "}
                                <strong className="font-heading text-foreground">{formatMoney(cheapest)}</strong>{" "}
                                · gizli masraf yok
                            </p>
                        )}

                        <div className="mt-9 grid gap-4 sm:grid-cols-3">
                            {[
                                { icon: ShieldCheck, title: "Güvenli ödeme", detail: "3D Secure altyapı" },
                                { icon: BadgeCheck, title: "Evrak kontrolü", detail: "Başvuru öncesi ücretsiz" },
                                { icon: Clock, title: "3-5 iş günü", detail: "Ortalama sonuçlanma" },
                            ].map(({ icon: Icon, title, detail }) => (
                                <div key={title} className="flex items-start gap-2.5">
                                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                        <Icon className="h-4.5 w-4.5 text-primary" />
                                    </span>
                                    <div>
                                        <p className="text-sm font-semibold leading-tight">{title}</p>
                                        <p className="text-xs text-muted-foreground">{detail}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.97 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                        className="relative"
                    >
                        <div className="overflow-hidden rounded-2xl border border-border" style={{ boxShadow: "var(--shadow-float)" }}>
                            <img
                                src={IMAGES.heroSkyline}
                                alt="Dubai silueti ve Burj Khalifa gün batımında"
                                className="h-[300px] w-full object-cover sm:h-[420px]"
                                loading="eager"
                            />
                        </div>
                        <div
                            className="absolute -bottom-6 left-4 right-4 rounded-xl border border-border bg-card p-4 sm:left-8 sm:right-auto sm:w-[300px]"
                            style={{ boxShadow: "var(--shadow-soft)" }}
                        >
                            <div className="flex items-center gap-1 text-[hsl(var(--gold))]">
                                {[0, 1, 2, 3, 4].map((i) => (
                                    <Star key={i} className="h-4 w-4 fill-current" />
                                ))}
                            </div>
                            <p className="mt-2 text-sm font-semibold leading-tight">
                                4.500+ başarılı başvuru
                            </p>
                            <p className="text-xs text-muted-foreground">
                                2019'dan bu yana Türkiye'den başvuran misafirlerimiz
                            </p>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* PRICING TEASER */}
            <section className="section" data-testid="landing-pricing-teaser">
                <div className="container-page">
                    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
                        <div>
                            <span className="eyebrow">Fiyatlar</span>
                            <h2 className="mt-3 text-2xl font-bold sm:text-3xl">
                                Şeffaf ve tek seferlik ödeme
                            </h2>
                            <p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">
                                Aşağıdaki fiyatlar başvuru harcı ve hizmet bedelimizin tamamını kapsar.
                                Başvuru sırasında ek ücret talep edilmez.
                            </p>
                        </div>
                        <Button asChild variant="secondary" className="h-11 border border-border" data-testid="teaser-all-prices-button">
                            <Link to="/vize-tipleri">
                                Tüm vize tiplerini gör <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                    </div>

                    <div className="mt-9 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                        {teaser.map((visa) => (
                            <VisaTypeCard key={visa.id} visa={visa} />
                        ))}
                    </div>
                </div>
            </section>

            {/* HOW IT WORKS */}
            <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="landing-how-it-works">
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Nasıl Çalışır</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">4 adımda Dubai vizesi</h2>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Konsolosluk kuyruğu, kargo, karmaşık evrak yok. Tüm süreç online.
                        </p>
                    </div>
                    <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                        {(content?.process_steps || []).map((s) => (
                            <div key={s.step} className="card-surface card-hoverable p-6">
                                <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary font-heading text-base font-bold text-primary-foreground">
                                    {s.step}
                                </span>
                                <h3 className="mt-4 font-heading text-lg font-semibold">{s.title}</h3>
                                <p className="mt-2 text-sm leading-6 text-muted-foreground">{s.detail}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* WHY US */}
            <section className="section">
                <div className="container-page grid items-center gap-12 lg:grid-cols-2">
                    <div className="order-2 grid gap-5 sm:grid-cols-2 lg:order-1">
                        {(content?.why_us || []).map((w, i) => {
                            const Icon = WHY_ICONS[i % WHY_ICONS.length];
                            return (
                                <div key={w.title} className="card-surface p-5">
                                    <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-[hsl(var(--sand-surface))]">
                                        <Icon className="h-5 w-5 text-[hsl(var(--navy))]" />
                                    </span>
                                    <h3 className="mt-3.5 font-heading text-base font-semibold">{w.title}</h3>
                                    <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{w.detail}</p>
                                </div>
                            );
                        })}
                    </div>
                    <div className="order-1 lg:order-2">
                        <span className="eyebrow">Neden Biz</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">
                            Başvurunuzu bir danışman takip eder
                        </h2>
                        <p className="mt-3 text-sm leading-7 text-muted-foreground">
                            Otomatik bir form doldurma servisi değiliz. Her başvuruda pasaport geçerliliği,
                            fotoğraf kriterleri ve seyahat tarihleri tek tek kontrol edilir. Eksik veya riskli
                            bir durum varsa başvuruyu göndermeden önce sizi bilgilendiririz.
                        </p>
                        <div className="mt-6 overflow-hidden rounded-2xl border border-border" style={{ boxShadow: "var(--shadow-card)" }}>
                            <img
                                src={IMAGES.burjAlArabAerial}
                                alt="Dubai Burj Al Arab ve Jumeirah kıyısı"
                                className="h-[220px] w-full object-cover"
                                loading="lazy"
                            />
                        </div>
                    </div>
                </div>
            </section>

            {/* TESTIMONIALS */}
            <section className="section border-y border-border bg-[hsl(var(--sand-surface))]">
                <div className="container-page">
                    <span className="eyebrow">Yorumlar</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Misafirlerimiz ne diyor?</h2>
                    <div className="mt-9 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                        {(content?.testimonials || []).map((t) => (
                            <div key={t.name} className="flex h-full flex-col rounded-xl border border-border bg-card p-5">
                                <Quote className="h-6 w-6 text-primary/40" />
                                <p className="mt-3 flex-1 text-sm leading-6">{t.text}</p>
                                <div className="mt-4 flex items-center gap-1 text-[hsl(var(--gold))]">
                                    {Array.from({ length: t.rating }).map((_, i) => (
                                        <Star key={i} className="h-3.5 w-3.5 fill-current" />
                                    ))}
                                </div>
                                <p className="mt-2 text-sm font-semibold">{t.name}</p>
                                <p className="text-xs text-muted-foreground">{t.city}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* FAQ TEASER */}
            <section className="section">
                <div className="container-page grid gap-10 lg:grid-cols-[0.8fr_1.2fr]">
                    <div>
                        <span className="eyebrow">S.S.S.</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Merak edilenler</h2>
                        <p className="mt-3 text-sm leading-6 text-muted-foreground">
                            Başvuru öncesi en sık sorulan soruları derledik. Aradanızı bulamadınız mı?
                        </p>
                        <Button asChild variant="secondary" className="mt-5 h-11 border border-border" data-testid="faq-see-all-button">
                            <Link to="/sss">Tüm soruları gör</Link>
                        </Button>
                    </div>
                    <Accordion type="single" collapsible className="w-full" data-testid="faq-accordion">
                        {(content?.faq || []).slice(0, 4).map((item, i) => (
                            <AccordionItem key={i} value={`item-${i}`}>
                                <AccordionTrigger className="text-left text-sm font-semibold">{item.q}</AccordionTrigger>
                                <AccordionContent className="text-sm leading-6 text-muted-foreground">
                                    {item.a}
                                </AccordionContent>
                            </AccordionItem>
                        ))}
                    </Accordion>
                </div>
            </section>

            {/* CTA BAND */}
            <section className="border-t border-border bg-[hsl(var(--navy))]">
                <div className="container-page flex flex-col items-start justify-between gap-6 py-12 sm:flex-row sm:items-center">
                    <div>
                        <h2 className="text-2xl font-bold text-white sm:text-3xl">Başvurunuzu şimdi başlatın</h2>
                        <p className="mt-2 max-w-xl text-sm leading-6 text-white/70">
                            Ortalama tamamlanma süresi 5 dakika. Ödeme adımına geçmeden önce tüm
                            bilgilerinizi özet ekranında kontrol edebilirsiniz.
                        </p>
                    </div>
                    <Button asChild className="h-12 shrink-0 px-7 text-base" data-testid="cta-band-apply-button">
                        <Link to="/basvuru">
                            Başvuru Yap <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                    </Button>
                </div>
            </section>
        </div>
    );
}
