import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
    AlertTriangle,
    ArrowRight,
    BadgeCheck,
    Banknote,
    CalendarClock,
    Clock,
    FileCheck2,
    FileText,
    HeadphonesIcon,
    IdCard,
    Image as ImageIcon,
    Instagram,
    MessageCircle,
    Percent,
    PlaneTakeoff,
    Quote,
    ShieldCheck,
    Star,
    Users,
} from "lucide-react";
import { motion } from "framer-motion";
import { api } from "../lib/api";
import { IMAGES, setMeta } from "../lib/site";
import { useContact, waLink } from "../lib/contact";
import { Button } from "../components/ui/button";
import { PricingTabs } from "../components/PricingTabs";
import { ServiceCard } from "../components/IconCards";
import { FeaturedTestimonial, ReviewSummary, TestimonialCard } from "../components/Testimonials";
import { ReviewSpotlight } from "../components/ReviewSpotlight";
import { SampleVisa } from "../components/SampleVisa";
import { RouteFlags } from "../components/FlagIcons";
import { AuthorityStrip } from "../components/AuthorityStrip";
import { VisaShowcase } from "../components/VisaShowcase";
import { VisaGuideLinks } from "../components/VisaGuideLinks";
import { FxNote } from "../components/FxNote";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "../components/ui/accordion";

const WHY_ICONS = [Banknote, FileCheck2, Clock, HeadphonesIcon];
const DOC_ICONS = {
    passport: IdCard,
    photo: ImageIcon,
    ticket: PlaneTakeoff,
    hotel: CalendarClock,
    other: FileText,
};

export default function Home() {
    const contact = useContact();
    const [content, setContent] = useState(null);

    useEffect(() => {
        setMeta(
            "Dubai Vizesi | Online Başvuru, Fiyatlar ve Aile Başvurusu | Dubai Vize Online",
            "Dubai (BAE) vizesi için online başvuru: net fiyatlar, tek formda aile başvurusu, çocuk vizesi indirimi, ekspres hizmet ve ortalama 2 iş gününde sonuç."
        );
        api.get("/content/site").then(({ data }) => setContent(data)).catch(() => {});
    }, []);

    return (
        <div data-testid="home-page">
            {/* HERO — gökyüzü zemin + yüzen açık panel */}
            <section className="relative isolate" data-testid="landing-hero">
                <div className="container-page relative pt-10 sm:pt-14">
                    <motion.div
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.45 }}
                        className="relative overflow-hidden rounded-[var(--radius-xl)] border border-white/60 bg-card/70 px-5 pb-10 pt-12 backdrop-blur-sm sm:px-10 sm:pb-14 sm:pt-16"
                        style={{ boxShadow: "var(--shadow-float)" }}
                    >
                        <div className="hero-glow absolute inset-0" aria-hidden="true" />

                        <div className="relative mx-auto max-w-3xl text-center">
                            <span
                                className="inline-flex items-center gap-2 rounded-full border border-border/70 bg-card px-3.5 py-1.5 text-[11px] font-bold uppercase tracking-[0.14em] text-foreground/70"
                                data-testid="hero-eyebrow"
                            >
                                <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
                                Birleşik Arap Emirlikleri Vize Danışmanlığı
                            </span>
                            <h1 className="mt-6 font-heading text-4xl font-extrabold sm:text-5xl lg:text-[58px]">
                                <span className="display-italic">Dubai vizeniz</span>
                                <br />
                                2 iş gününde hazır
                            </h1>
                            <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-muted-foreground sm:text-lg">
                                Tek formda tüm aileniz için başvuru yapın. Pasaportunuzu yükleyin, bilgileriniz
                                otomatik dolsun; belgeleri danışmanlarımız kontrol etsin. Onaylanan vizeniz PDF
                                olarak e-postanıza gelsin.
                            </p>

                            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                                <Button asChild size="lg" data-testid="hero-apply-now-button">
                                    <Link to="/basvuru">
                                        Başvuruya Başla <ArrowRight className="ml-1 h-4 w-4" />
                                    </Link>
                                </Button>
                                <Button asChild size="lg" variant="outline" data-testid="hero-pricing-button">
                                    <Link to="/vize-tipleri">Hizmet Bedellerini Gör</Link>
                                </Button>
                            </div>
                        </div>

                        <div className="relative mt-10 overflow-hidden rounded-[var(--radius-lg)] border border-white/60">
                            <img
                                src={IMAGES.heroSkyline}
                                alt="Dubai silueti ve Burj Khalifa gün batımında"
                                className="h-[220px] w-full object-cover object-center sm:h-[300px]"
                                loading="eager"
                            />
                        </div>

                        {content?.promo && (
                            <div
                                className="panel-cream relative mt-8 flex items-start gap-3 p-5"
                                data-testid="hero-promo-banner"
                            >
                                <Percent className="mt-0.5 h-5 w-5 shrink-0 text-foreground/70" aria-hidden="true" />
                                <div>
                                    <p className="text-sm font-bold">{content.promo.title}</p>
                                    <p className="mt-1 text-xs leading-5 text-muted-foreground">
                                        {content.promo.detail}
                                    </p>
                                </div>
                            </div>
                        )}

                        <div
                            className="relative mt-8 grid gap-4 rounded-[var(--radius-lg)] border border-border/70 bg-card p-4 sm:grid-cols-3 sm:divide-x sm:divide-border/70"
                            data-testid="hero-trust-strip"
                        >
                            {[
                                { icon: Users, title: "Aile başvurusu", detail: "Tek formda çoklu yolcu" },
                                { icon: BadgeCheck, title: "Evrak kontrolü", detail: "Başvuru öncesi ücretsiz" },
                                { icon: Clock, title: "Ortalama 2 gün", detail: "Ekspreste 24 saat" },
                            ].map(({ icon: Icon, title, detail }) => (
                                <div
                                    key={title}
                                    className="flex min-w-0 items-center gap-2.5 sm:px-3.5 sm:first:pl-0 sm:last:pr-0"
                                >
                                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                                        <Icon className="h-4 w-4" aria-hidden="true" />
                                    </span>
                                    <div className="min-w-0">
                                        <p className="truncate text-[13px] font-bold leading-tight">{title}</p>
                                        <p className="mt-0.5 text-[11px] leading-4 text-muted-foreground">{detail}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* SAYISAL VITRIN SERIDI */}
                        <div
                            className="relative mt-8 grid grid-cols-2 gap-4 border-t border-border/70 pt-6 sm:divide-x sm:divide-border/70 lg:grid-cols-4"
                            data-testid="hero-stats-bar"
                        >
                            {[
                                { value: "4.500+", label: "Tamamlanan başvuru" },
                                { value: "%98", label: "Onay oranı" },
                                { value: "2 gün", label: "Ortalama sonuç süresi" },
                                { value: "7+ yıl", label: "Acente deneyimi" },
                            ].map(({ value, label }) => (
                                <div key={label} className="px-2 sm:px-6">
                                    <p className="tabular font-heading text-2xl font-extrabold sm:text-3xl">{value}</p>
                                    <p className="mt-1 text-xs font-medium text-muted-foreground sm:text-sm">{label}</p>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                </div>

                {/* MARQUEE RIBBON */}
                <div className="mt-8" data-testid="hero-marquee">
                    <div className="container-page">
                        <div className="panel-dark py-3.5">
                            <div className="marquee">
                                <div className="marquee-track">
                                    {[0, 1].map((dup) => (
                                        <div
                                            key={dup}
                                            className="flex shrink-0 items-center gap-8 pr-8"
                                            aria-hidden={dup === 1}
                                        >
                                            {[
                                                "Turistik Vize",
                                                "Aile Başvurusu",
                                                "Ekspres Vize",
                                                "Vize Uzatma",
                                                "Transit Vize",
                                                "Freelancer Vize",
                                                "Evrak Kontrolü",
                                                "Başvuru Takibi",
                                            ].map((t) => (
                                                <span
                                                    key={t}
                                                    className="flex items-center gap-8 whitespace-nowrap text-sm font-bold uppercase tracking-wider text-white/85"
                                                >
                                                    {t}
                                                    <span className="h-1.5 w-1.5 rounded-full bg-[hsl(var(--cream-tag))]" />
                                                </span>
                                            ))}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* AUTHORITIES / TRUST STRIP */}
            <AuthorityStrip />

            {/* VIZE TIPI VITRINI — tek dokunuşla seçim */}
            <VisaShowcase />

            {/* MUSTERI YORUMU VITRINI (ust bolum) */}
            <ReviewSpotlight summary={content?.review_summary} testimonials={content?.testimonials} />

            {/* PRICING TABS */}
            <section className="section" data-testid="landing-pricing">
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Hizmet Bedelleri</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Dubai vize hizmet bedelleri</h2>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Fiyatlarımız başvuru harcı ve hizmet bedelimizin tamamını kapsar; dosya açma veya
                            danışmanlık adı altında ek kalem çıkarmıyoruz. Yalnızca üçüncü taraf danışmanlık
                            hizmeti veriyoruz; resmî bir devlet kurumu değiliz.
                        </p>
                    </div>
                    <div className="mt-5 flex flex-wrap items-center gap-3">
                        <FxNote />
                        <span className="text-xs text-muted-foreground">
                            Fiyatlar dolar bazlıdır, tahsilat güncel kurla TL olarak yapılır.
                        </span>
                    </div>
                    <div className="mt-8">
                        <PricingTabs />
                    </div>

                    <div className="mt-12" data-testid="home-visa-guides">
                        <h3 className="font-heading text-xl font-bold">Vize tipine göre detaylı rehberler</h3>
                        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
                            Şartlar, gerekli belgeler, süreç ve sıkça sorulan sorular; her vize tipi için
                            ayrı ayrı anlatıldı.
                        </p>
                        <div className="mt-6">
                            <VisaGuideLinks limit={6} />
                        </div>
                    </div>

                    {/* IMPORTANT NOTICE */}
                    <div className="mt-12 rounded-xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.09)] p-6" data-testid="important-notice">
                        <div className="flex items-center gap-2.5">
                            <AlertTriangle className="h-5 w-5 text-[hsl(var(--status-warning))]" />
                            <h3 className="font-heading text-base font-bold text-[hsl(var(--status-warning))]">Önemli Uyarı</h3>
                        </div>
                        <ul className="mt-3 space-y-2.5">
                            {(content?.important_notice || []).map((n) => (
                                <li key={n} className="text-sm leading-6 text-[hsl(var(--status-warning))]">• {n}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            </section>

            {/* REQUIRED DOCUMENTS */}
            <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="landing-documents">
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Gerekli Evraklar</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Başvuru için gereken belgeler</h2>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Pasaportunuzu hiçbir yere teslim etmiyorsunuz. Aşağıdaki belgelerin dijital
                            kopyalarını yüklemeniz yeterli.
                        </p>
                    </div>
                    <div className="mt-9 grid items-start gap-8 lg:grid-cols-[0.85fr_1.15fr]">
                        <div className="overflow-hidden rounded-2xl border border-border lg:sticky lg:top-28" style={{ boxShadow: "var(--shadow-card)" }}>
                            <img
                                src={IMAGES.passportDocs}
                                alt="Pasaport ve seyahat belgeleri"
                                className="h-[280px] w-full object-cover"
                                loading="lazy"
                            />
                        </div>
                        <div className="grid gap-5 sm:grid-cols-2">
                        {(content?.required_documents || []).map((d) => {
                            const Icon = DOC_ICONS[d.key] || FileText;
                            return (
                                <div key={d.key} className="card-surface card-hoverable p-6" data-testid={`doc-card-${d.key}`}>
                                    <div className="flex items-start justify-between gap-3">
                                        <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10">
                                            <Icon className="h-5 w-5 text-primary" />
                                        </span>
                                        <span
                                            className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${
                                                d.required
                                                    ? "border-[hsl(var(--brand-copper)/0.30)] bg-[hsl(var(--brand-copper)/0.08)] text-[hsl(var(--brand-copper))]"
                                                    : "border-border bg-muted text-muted-foreground"
                                            }`}
                                        >
                                            {d.required ? "Zorunlu" : "Opsiyonel"}
                                        </span>
                                    </div>
                                    <h3 className="mt-4 font-heading text-base font-semibold">{d.title}</h3>
                                    <p className="mt-2 text-sm leading-6 text-muted-foreground">{d.detail}</p>
                                </div>
                            );
                        })}
                        </div>
                    </div>
                    <Button asChild variant="secondary" className="mt-8 h-11 border border-border">
                        <Link to="/gerekli-belgeler">
                            Belge detayları ve fotoğraf kuralları <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                    </Button>
                </div>
            </section>

            {/* HOW IT WORKS */}
            <section className="section" data-testid="landing-how-it-works">
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Nasıl Çalışır</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">4 adımda Dubai vizesi</h2>
                    </div>
                    <div className="mt-9 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
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

            {/* SAMPLE VISA */}
            <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="landing-sample-visa">
                <div className="container-page grid items-center gap-10 lg:grid-cols-[1fr_1.05fr]">
                    <div>
                        <span className="eyebrow">Onaylanan Vize</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Vizeniz böyle görünür</h2>
                        <p className="mt-3 text-sm leading-7 text-muted-foreground">
                            BAE vizesi elektroniktir; pasaportunuza yapıştırılmaz. Başvurunuz onaylandığında
                            giriş izni belgeniz PDF olarak e-postanıza gelir. Belgeyi telefonunuzdan veya
                            çıktı alarak pasaport kontrolünde gösterirsiniz.
                        </p>
                        <ul className="mt-5 space-y-2.5 text-sm">
                            {[
                                "Tüm emirliklerde geçerli tek belge",
                                "Kare kod ile sınırda hızlı doğrulama",
                                "Kaybolursa takip sayfanızdan tekrar indirebilirsiniz",
                            ].map((t) => (
                                <li key={t} className="flex items-start gap-2">
                                    <BadgeCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                    <span>{t}</span>
                                </li>
                            ))}
                        </ul>
                        <RouteFlags className="mt-6" />
                    </div>
                    <SampleVisa />
                </div>
            </section>

            {/* WHATSAPP ALTERNATIVE */}
            <section className="section" data-testid="landing-whatsapp-apply">
                <div className="container-page">
                    <div className="grid items-center gap-8 rounded-2xl border border-border bg-card p-7 sm:p-10 lg:grid-cols-[1.2fr_0.8fr]">
                        <div>
                            <span className="eyebrow">Alternatif Başvuru</span>
                            <h2 className="mt-3 text-2xl font-bold sm:text-3xl">
                                Form doldurmak istemiyorsanız WhatsApp'tan başvurun
                            </h2>
                            <p className="mt-3 text-sm leading-7 text-muted-foreground">
                                Pasaportunuzun kimlik sayfası ile bir vesikalık fotoğrafınızı WhatsApp
                                hattımıza gönderin; başvurunuzu sizin adınıza biz oluşturalım, ödeme
                                bağlantısını ve takip kodunuzu size iletelim.
                            </p>
                            <ul className="mt-5 grid gap-2.5 sm:grid-cols-2">
                                {[
                                    "Pasaport + 1 vesikalık yeterli",
                                    "Danışman evrakları kontrol eder",
                                    "Kart veya havale ile ödeme",
                                    "Takip kodu WhatsApp'tan gelir",
                                ].map((t) => (
                                    <li key={t} className="flex items-start gap-2 text-sm">
                                        <BadgeCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                        <span>{t}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="flex flex-col gap-3">
                            {contact.whatsapp && (
                                <Button asChild className="h-12 text-base" data-testid="whatsapp-apply-button">
                                    <a
                                        href={waLink(contact, "Merhaba, Dubai vizesi için başvuru yapmak istiyorum. Pasaport ve fotoğrafımı gönderiyorum.")}
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        <MessageCircle className="mr-2 h-5 w-5" /> WhatsApp'tan başvur
                                    </a>
                                </Button>
                            )}
                            <Button asChild variant="secondary" className="h-12 border border-border text-base">
                                <a href={`mailto:${contact.email}?subject=${encodeURIComponent("Dubai vize başvurusu")}`} data-testid="email-apply-button">
                                    E-posta ile gönder
                                </a>
                            </Button>
                            <p className="text-xs leading-5 text-muted-foreground">
                                Çalışma saatleri: {contact.workingHours}
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* SERVICES */}
            <section className="section border-y border-border bg-[hsl(var(--sand-surface))]" data-testid="landing-services">
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Hizmetlerimiz</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Sadece vize, baştan sona uzman desteğiyle</h2>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Tek işimiz vize: başvuru hazırlığı, evrak kontrolü, ekspres işlem, aile başvurusu ve
                            uzatma süreçlerinizi biz yürütüyoruz.
                        </p>
                    </div>
                    <div className="mt-9 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                        {(content?.services || []).map((s) => (
                            <ServiceCard key={s.key} item={s} />
                        ))}
                    </div>
                </div>
            </section>

            {/* WHY US */}
            <section className="section border-y border-border bg-[hsl(var(--cloud))]">
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
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Başvurunuzu bir danışman takip eder</h2>
                        <p className="mt-3 text-sm leading-7 text-muted-foreground">
                            Otomatik bir form doldurma servisi değiliz. Her başvuruda pasaport geçerliliği,
                            fotoğraf kriterleri ve seyahat tarihleri tek tek kontrol edilir. Eksik veya riskli
                            bir durum varsa başvuruyu göndermeden önce sizi bilgilendiririz.
                        </p>
                        <div className="mt-6 overflow-hidden rounded-2xl border border-border" style={{ boxShadow: "var(--shadow-card)" }}>
                            <img src={IMAGES.office} alt="Dubai Vize Online danışmanlık ofisi" className="h-[220px] w-full object-cover" loading="lazy" />
                        </div>
                    </div>
                </div>
            </section>

            {/* TESTIMONIALS */}
            <section
                id="landing-testimonials"
                className="section scroll-mt-24 border-y border-border bg-[hsl(var(--cloud))]"
                data-testid="landing-testimonials"
            >
                <div className="container-page">
                    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
                        <div className="max-w-2xl">
                            <span className="eyebrow">Müşteri Deneyimleri</span>
                            <h2 className="mt-3 text-2xl font-bold sm:text-3xl">
                                Başvuru sahiplerimiz ne diyor?
                            </h2>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Aşağıdaki yorumlar, vizesi teslim edilen başvuru sahiplerine gönderilen
                                değerlendirme anketinden alınmıştır.
                            </p>
                        </div>
                        <Button asChild variant="secondary" className="h-11 border border-border">
                            <Link to="/basvuru">Siz de başvurun</Link>
                        </Button>
                    </div>

                    <div className="mt-8">
                        <ReviewSummary summary={content?.review_summary} />
                    </div>

                    {(content?.testimonials || []).length > 0 && (
                        <div className="mt-8 grid gap-6 lg:grid-cols-3" data-testid="testimonial-grid">
                            <div className="lg:col-span-1">
                                <FeaturedTestimonial item={content.testimonials[0]} />
                            </div>
                            <div className="grid gap-6 sm:grid-cols-2 lg:col-span-2">
                                {content.testimonials.slice(1).map((t) => (
                                    <TestimonialCard key={t.name} item={t} />
                                ))}
                            </div>
                        </div>
                    )}

                    {/* SOCIAL BAND */}
                    <div className="mt-12 flex flex-col items-start gap-5 rounded-2xl border border-border bg-[hsl(var(--navy))] p-7 sm:flex-row sm:items-center sm:justify-between">
                        <div className="flex items-start gap-4">
                            <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-white/10">
                                <Instagram className="h-6 w-6 text-white" />
                            </span>
                            <div>
                                <h3 className="font-heading text-lg font-bold text-white">Dubai'yi bizimle takip edin</h3>
                                <p className="mt-1 text-sm text-white/70">
                                    Güncel haberler, gezilecek yerler ve vize duyuruları için sosyal medya
                                    hesabımıza göz atın.
                                </p>
                            </div>
                        </div>
                        <Button asChild variant="secondary" className="h-11 border border-border">
                            <Link to="/gelismeler">Dubai'den Gelişmeler</Link>
                        </Button>
                    </div>

                    {/* PARTNERS */}
                    <div className="mt-12">
                        <h3 className="font-heading text-base font-bold">Güvenilir partnerlerimiz</h3>
                        <p className="mt-1.5 text-sm text-muted-foreground">
                            Seyahatiniz için sektörün önde gelen havayolu ve hizmet sağlayıcılarıyla çalışıyoruz.
                        </p>
                        <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
                            {(content?.partners || []).map((p) => (
                                <div
                                    key={p}
                                    className="flex h-16 items-center justify-center rounded-lg border border-border bg-card px-3 text-center font-heading text-sm font-semibold text-muted-foreground"
                                >
                                    {p}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* ARTICLES */}
            <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="landing-articles">
                <div className="container-page">
                    <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
                        <div className="max-w-2xl">
                            <span className="eyebrow">Dubai'den Gelişmeler</span>
                            <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Vize ve seyahat rehberi</h2>
                        </div>
                        <Button asChild variant="secondary" className="h-11 border border-border">
                            <Link to="/gelismeler">Tüm yazılar</Link>
                        </Button>
                    </div>
                    <div className="mt-9 grid gap-6 md:grid-cols-3">
                        {(content?.articles || []).slice(0, 3).map((a) => (
                            <Link
                                key={a.slug}
                                to={`/gelismeler/${a.slug}`}
                                className="card-surface card-hoverable flex flex-col p-6"
                                data-testid={`article-card-${a.slug}`}
                            >
                                <span className="text-xs font-semibold uppercase tracking-wider text-primary">
                                    {new Date(a.date).toLocaleDateString("tr-TR", { day: "2-digit", month: "long", year: "numeric" })}
                                </span>
                                <h3 className="mt-2 font-heading text-base font-semibold">{a.title}</h3>
                                <p className="mt-2 flex-1 text-sm leading-6 text-muted-foreground">{a.excerpt}</p>
                                <span className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-primary">
                                    Devamını oku <ArrowRight className="h-3.5 w-3.5" />
                                </span>
                            </Link>
                        ))}
                    </div>
                </div>
            </section>

            {/* FAQ */}
            <section className="section">
                <div className="container-page grid gap-10 lg:grid-cols-[0.8fr_1.2fr]">
                    <div>
                        <span className="eyebrow">S.S.S.</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Sıkça sorulan sorular</h2>
                        <p className="mt-3 text-sm leading-6 text-muted-foreground">
                            Başvuru öncesi en çok sorulan soruları derledik.
                        </p>
                        <Button asChild variant="secondary" className="mt-5 h-11 border border-border" data-testid="faq-see-all-button">
                            <Link to="/sss">Tüm soruları gör</Link>
                        </Button>
                    </div>
                    <Accordion type="single" collapsible className="w-full" data-testid="faq-accordion">
                        {(content?.faq || []).slice(0, 5).map((item, i) => (
                            <AccordionItem key={i} value={`item-${i}`}>
                                <AccordionTrigger className="text-left text-sm font-semibold">{item.q}</AccordionTrigger>
                                <AccordionContent className="text-sm leading-6 text-muted-foreground">{item.a}</AccordionContent>
                            </AccordionItem>
                        ))}
                    </Accordion>
                </div>
            </section>

            {/* SEO LONG TEXT */}
            <section className="section border-t border-border bg-card" data-testid="landing-seo-text">
                <div className="container-page max-w-3xl">
                    <span className="eyebrow">Rehber</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Dubai vizesi nasıl alınır?</h2>
                    <p className="mt-2 text-sm text-muted-foreground">Başvurudan sonuca kadar bilmeniz gerekenler</p>
                    <div className="mt-6 space-y-4 text-sm leading-7 text-muted-foreground">
                        <p>
                            Dubai vizesi aslında bir <strong className="text-foreground">Birleşik Arap Emirlikleri
                            vizesidir</strong>. Aldığınız vize yalnızca Dubai'de değil, Abu Dabi ve Şarja dahil
                            yedi emirliğin tamamında geçerlidir. Emirlikler arasında sınır kontrolü yoktur;
                            Dubai'den girip Abu Dabi'den çıkabilirsiniz.
                        </p>
                        <p>
                            Umuma mahsus <strong className="text-foreground">bordo pasaport</strong> sahibi Türk
                            vatandaşları için vize gereklidir. Hususi (yeşil), hizmet (gri) ve diplomatik
                            pasaport hamilleri ise yılda 90 güne kadar vizesiz giriş yapabilir.
                        </p>
                        <p>Vize türünüzü üç şey belirler:</p>
                        <ul className="space-y-2 pl-1">
                            <li>
                                <strong className="text-foreground">Kalış süreniz</strong> — 30 gün veya 60 gün.
                                Süre ülkeye giriş yaptığınız gün başlar ve takvim günü olarak işler.
                            </li>
                            <li>
                                <strong className="text-foreground">Giriş sayınız</strong> — Gidip dönecekseniz tek
                                girişli yeterlidir. Umman veya Katar gibi ülkelere geçip Dubai'ye dönecekseniz
                                çok girişli gerekir.
                            </li>
                            <li>
                                <strong className="text-foreground">Yaş</strong> — 18 yaş altı çocuklar,
                                aileleriyle birlikte seyahat etmeleri koşuluyla indirimli çocuk vizesinden
                                yararlanır.
                            </li>
                        </ul>
                        <p>
                            Başvuru tamamen online yapılır. Pasaportunuzu fiziksel olarak hiçbir yere teslim
                            etmezsiniz; fotoğrafın bulunduğu sayfanın net bir taraması yeterlidir.
                            Pasaportunuzun <strong className="text-foreground">dönüş tarihinizden itibaren en az
                            6 ay geçerli</strong> olması tek teknik şarttır.
                        </p>
                        <p>
                            Belgeleriniz tamamlandıktan sonra başvurunuz yetkili mercilere iletilir. Standart
                            başvurular ortalama 2 iş günü içinde sonuçlanır. Uçuşuna az kalan yolcular için
                            ekspres başvuru vardır; sonuç genellikle 24 saat içinde çıkar. Vizeniz
                            onaylandığında PDF olarak e-postanıza ve takip sayfanıza iletilir.
                        </p>
                        <p>
                            Aile başvurularında tek form doldurmanız yeterli: eşinizi ve çocuklarınızı aynı
                            başvuruya ekleyin, çocuk vizesi indirimi ve aile indirimi otomatik hesaplanır.
                        </p>
                    </div>
                </div>
            </section>

            {/* CTA BAND */}
            <section className="border-t border-border bg-[hsl(var(--navy))]">
                <div className="container-page flex flex-col items-start justify-between gap-6 py-12 sm:flex-row sm:items-center">
                    <div>
                        <h2 className="text-2xl font-bold text-white sm:text-3xl">Başvurunuzu şimdi başlatın</h2>
                        <p className="mt-2 max-w-xl text-sm leading-6 text-white/70">
                            Ortalama tamamlanma süresi 5 dakika. Ödeme adımına geçmeden önce tüm bilgilerinizi
                            özet ekranında kontrol edebilirsiniz.
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
