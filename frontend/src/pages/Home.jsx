import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    ArrowRight,
    BadgeCheck,
    CheckCircle2,
    CreditCard,
    FileCheck2,
    FileText,
    HeadphonesIcon,
    IdCard,
    Image as ImageIcon,
    MessageCircle,
    PlaneTakeoff,
    CalendarClock,
    Search,
    ShieldCheck,
    Radar,
    X,
} from "lucide-react";
import { motion } from "framer-motion";
import { api } from "../lib/api";
import { IMAGES, setJsonLd, setMeta, SITE_URL } from "../lib/site";
import { useContact, waLink } from "../lib/contact";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { ReviewSpotlight } from "../components/ReviewSpotlight";
import { AuthorityStrip } from "../components/AuthorityStrip";
import { SecurityBadges } from "../components/SecurityBadges";
import { VisaShowcase } from "../components/VisaShowcase";
import { VisaExplainer } from "../components/VisaExplainer";
import { VisaSpecimen } from "../components/VisaSpecimen";
import { HeroHeadline } from "../components/HeroHeadline";
import { HomeBundleStrip } from "../components/HomeBundleStrip";
import { HomeInsuranceStrip } from "../components/HomeInsuranceStrip";
import { HomeTourStrip } from "../components/HomeTourStrip";
import { EasyCompare } from "../components/EasyCompare";
import { AskFirstSection } from "../components/AskFirstSection";
import { CommitmentsStrip } from "../components/CommitmentsStrip";
import { FxNote } from "../components/FxNote";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "../components/ui/accordion";

const DOC_ICONS = {
    passport: IdCard,
    photo: ImageIcon,
    ticket: PlaneTakeoff,
    hotel: CalendarClock,
    other: FileText,
};

const ADVANTAGES = [
    { icon: FileText, title: "Sadece pasaport ve fotoğraf", detail: "Vizenizi yalnızca pasaportunuz ve bir vesikalık fotoğrafla alıyoruz; başka evrak istemiyoruz." },
    { icon: PlaneTakeoff, title: "Bilet ve otel şartı yok", detail: "Vizeniz çıkmadan uçak bileti veya otel rezervasyonu yapmanıza gerek kalmıyor." },
    { icon: ShieldCheck, title: "Güvenli belge yükleme", detail: "Pasaportunuzu hiçbir yere teslim etmezsiniz; dijital kopya yeterli." },
    { icon: CreditCard, title: "Kolay ödeme seçenekleri", detail: "Kredi kartı veya banka havalesi ile ödeyin." },
    { icon: Radar, title: "Başvuru durumunu takip etme", detail: "Takip kodunuzla her adımı anlık görün." },
    { icon: HeadphonesIcon, title: "Uzman destek ekibi", detail: "Danışmanınız başvurunuzu gönderilmeden önce kontrol eder." },
];

const PROCESS_UNUSED_REMOVED = true;

const TrackingBox = () => {
    const navigate = useNavigate();
    const [code, setCode] = useState("");

    const submit = (e) => {
        e.preventDefault();
        const value = code.trim();
        navigate(value ? `/takip?kod=${encodeURIComponent(value)}` : "/takip");
    };

    return (
        <form onSubmit={submit} className="mt-6 flex flex-col gap-3 sm:flex-row" data-testid="home-tracking-form">
            <Input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Başvuru takip kodunuz (örn. DV-2026-1234)"
                className="h-12 sm:max-w-sm"
                aria-label="Başvuru takip kodu"
                data-testid="home-tracking-input"
            />
            <Button type="submit" className="h-12 px-6" data-testid="home-tracking-submit">
                <Search className="mr-2 h-4 w-4" /> Durumu sorgula
            </Button>
        </form>
    );
};

export default function Home() {
    const contact = useContact();
    const [content, setContent] = useState(null);
    const [explainerOpen, setExplainerOpen] = useState(false);
    const [docsOpen, setDocsOpen] = useState(false);

    useEffect(() => {
        setMeta(
            "Dubai Vizesi Online Başvuru | Dubai Vize Hattı",
            "Dubai (BAE) vizenizi online alın: pasaport ve fotoğrafınızı yükleyin, ödemenizi yapın, onaylı vizeniz e-postanıza gelsin. Net fiyatlar, başvuru takibi."
        );
        api.get("/content/site").then(({ data }) => setContent(data)).catch(() => {});
    }, []);

    useEffect(() => {
        const company = content?.company || {};
        setJsonLd("organization", {
            "@context": "https://schema.org",
            "@type": "TravelAgency",
            "@id": `${SITE_URL}/#organization`,
            name: "Dubai Vize Hattı",
            ...(company.legal_name ? { legalName: company.legal_name } : {}),
            url: SITE_URL,
            logo: { "@type": "ImageObject", url: `${SITE_URL}/brand/logo-horizontal-gold-palm.png` },
            image: `${SITE_URL}/brand/logo-horizontal-gold-palm.png`,
            ...(company.phone ? { telephone: company.phone } : {}),
            ...(company.email ? { email: company.email } : {}),
            ...(company.address
                ? { address: { "@type": "PostalAddress", streetAddress: company.address, addressCountry: "TR" } }
                : {}),
            areaServed: { "@type": "Country", name: "Türkiye" },
            ...(company.instagram ? { sameAs: [company.instagram] } : {}),
        });
        setJsonLd("website", {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "@id": `${SITE_URL}/#website`,
            name: "Dubai Vize Hattı",
            url: SITE_URL,
            inLanguage: "tr-TR",
            publisher: { "@id": `${SITE_URL}/#organization` },
        });
        return () => {
            setJsonLd("organization", null);
            setJsonLd("website", null);
        };
    }, [content]);

    return (
        <div data-testid="home-page">
            {/* HERO */}
            <section className="relative isolate" data-testid="landing-hero">
                <div className="container-page relative pt-0">
                    <motion.div
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.45 }}
                        className="relative overflow-hidden rounded-[var(--radius-xl)] border border-white/60 bg-card/70 px-5 pb-8 pt-5 backdrop-blur-sm sm:px-10 sm:pb-10 sm:pt-6"
                        style={{ boxShadow: "var(--shadow-float)" }}
                    >
                        <div className="hero-glow absolute inset-0" aria-hidden="true" />

                        <div className="relative mx-auto max-w-3xl text-center">
                            <span
                                className="hidden items-center gap-2 rounded-full border border-border/70 bg-card px-3.5 py-1.5 text-[11px] font-bold uppercase tracking-[0.14em] text-foreground/70 sm:inline-flex"
                                data-testid="hero-eyebrow"
                            >
                                <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
                                Birleşik Arap Emirlikleri Vize Danışmanlığı
                            </span>
                            <HeroHeadline />

                            <ul
                                className="mt-6 hidden flex-wrap items-center justify-center gap-2.5 sm:flex"
                                data-testid="hero-simplicity-strip"
                            >
                                {[
                                    "Evrak kontrolü",
                                    "Resmî başvuru işlemleri",
                                    "Süreç takibi ve bilgilendirme",
                                ].map((text) => (
                                    <li
                                        key={text}
                                        className="inline-flex items-center gap-2 rounded-full border border-[hsl(var(--brand-green)/0.35)] bg-[hsl(var(--brand-green)/0.08)] px-3.5 py-1.5 text-xs font-semibold text-[hsl(var(--brand-green))]"
                                    >
                                        <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
                                        {text}
                                    </li>
                                ))}
                            </ul>

                            <p
                                className="mt-4 text-sm font-semibold text-primary sm:mt-5"
                                data-testid="hero-closing-line"
                            >
                                Siz sadece belgelerinizi yükleyin, vize sürecinizi biz halledelim.
                            </p>

                            <div className="mt-6 flex flex-wrap items-center justify-center gap-3 sm:mt-8">
                                <Button asChild size="lg" className="w-full sm:w-auto" data-testid="hero-apply-now-button">
                                    <Link to="/basvuru">
                                        Hemen Başvuruya Başla <ArrowRight className="ml-1 h-4 w-4" />
                                    </Link>
                                </Button>
                                <Button
                                    asChild
                                    size="lg"
                                    variant="outline"
                                    className="hidden sm:inline-flex"
                                    data-testid="hero-pricing-button"
                                >
                                    <Link to="/vize-tipleri">Hizmet Bedellerini Gör</Link>
                                </Button>
                            </div>
                        </div>

                        <div className="relative mt-6 sm:mt-8">
                            <button
                                type="button"
                                onClick={() => setExplainerOpen((open) => !open)}
                                className="flex w-full items-center justify-center gap-2 rounded-full border border-border bg-card px-4 py-2.5 text-xs font-semibold text-foreground/80 transition-colors hover:border-primary/50 hover:text-primary sm:hidden"
                                data-testid="hero-explainer-toggle"
                            >
                                {explainerOpen ? "Anlatımı kapat" : "Nasıl çalışıyor? 60 saniyede anlatalım"}
                                <ArrowRight
                                    className={`h-3.5 w-3.5 transition-transform ${explainerOpen ? "-rotate-90" : "rotate-90"}`}
                                    aria-hidden="true"
                                />
                            </button>
                            <div className={explainerOpen ? "mt-4" : "hidden sm:block"}>
                                <VisaExplainer />
                            </div>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* AUTHORITIES */}
            <AuthorityStrip />

            {/* NEDEN BIZI TERCIH ETMELISINIZ */}
            <section className="section" data-testid="landing-advantages">
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Avantajlar</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Neden bizi tercih etmelisiniz?</h2>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Dubai vizesi tek uzmanlık alanımız; her dosya yetkili mercilere iletilmeden önce
                            bir danışmanın elinden geçiyor.
                        </p>
                    </div>
                    <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                        {ADVANTAGES.map(({ icon: Icon, title, detail }, i) => (
                            <div
                                key={title}
                                className="card-surface card-hoverable flex items-start gap-3 p-4"
                                data-testid={`advantage-card-${i + 1}`}
                            >
                                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                    <Icon className="h-4 w-4 text-primary" aria-hidden="true" />
                                </span>
                                <div>
                                    <h3 className="font-heading text-sm font-bold">{title}</h3>
                                    <p className="mt-1 text-xs leading-5 text-muted-foreground">{detail}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <EasyCompare />

            <AskFirstSection />

            {/* DUBAI VIZE TURLERI (fiyatli kartlar) */}
            <VisaShowcase />

            <section className="pb-4" data-testid="landing-price-note">
                <div className="container-page flex flex-wrap items-center gap-3">
                    <FxNote />
                    <span className="text-xs text-muted-foreground">
                        Fiyatlar dolar bazlıdır, tahsilat güncel kurla TL olarak yapılır. Başvuru harcı ve hizmet
                        bedelimizin tamamı fiyata dahildir.
                    </span>
                </div>
            </section>

            {/* SEYAHAT PAKETLERI */}
            <HomeBundleStrip />

            {/* SADECE SIGORTA (vizeden bagimsiz satis) */}
            <HomeInsuranceStrip />

            {/* COL SAFARISI TANITIM SERIDI */}
            <HomeTourStrip />

            {/* GEREKLI BELGELER */}
            <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="landing-documents">
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Gerekli Belgeler</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Başvuru için gereken belgeler</h2>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Pasaportunuzun kimlik sayfası ve beyaz fonlu bir vesikalık yeterli. Uçak bileti ve
                            otel rezervasyonu zorunlu değildir.
                        </p>
                        <div className="mt-5 flex flex-wrap gap-2.5" data-testid="documents-not-required-chips">
                            {["Uçak bileti gerekmiyor", "Otel rezervasyonu gerekmiyor", "Banka dökümü gerekmiyor"].map(
                                (chip) => (
                                    <span
                                        key={chip}
                                        className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-xs font-semibold text-muted-foreground"
                                    >
                                        <X className="h-3.5 w-3.5 text-[hsl(var(--brand-red))]" aria-hidden="true" />
                                        {chip}
                                    </span>
                                )
                            )}
                        </div>
                        <p className="mt-3 text-xs leading-5 text-muted-foreground">
                            Vize çıkmadan bilet almanızı önermiyoruz: önce vizeniz onaylansın, planı sonra yapın.
                        </p>
                    </div>
                    <div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        {(content?.required_documents || []).map((d, i) => {
                            const Icon = DOC_ICONS[d.key] || FileText;
                            return (
                                <div
                                    key={d.key}
                                    className={`card-surface card-hoverable p-5 ${
                                        !docsOpen && i >= 2 ? "hidden sm:block" : ""
                                    }`}
                                    data-testid={`doc-card-${d.key}`}
                                >
                                    <div className="flex items-start justify-between gap-3">
                                        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                                            <Icon className="h-4.5 w-4.5 text-primary" />
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
                                    <h3 className="mt-3 font-heading text-sm font-bold">{d.title}</h3>
                                    <p className="mt-1.5 text-xs leading-5 text-muted-foreground">{d.detail}</p>
                                </div>
                            );
                        })}
                    </div>
                    {(content?.required_documents || []).length > 2 && !docsOpen && (
                        <button
                            type="button"
                            onClick={() => setDocsOpen(true)}
                            className="mt-4 inline-flex h-11 w-full items-center justify-center gap-2 rounded-full border border-border bg-card px-5 text-sm font-semibold transition-colors hover:border-primary/50 hover:text-primary sm:hidden"
                            data-testid="documents-show-all"
                        >
                            Tüm belgeleri gör ({(content?.required_documents || []).length})
                            <ArrowRight className="h-4 w-4 rotate-90" aria-hidden="true" />
                        </button>
                    )}
                    <Button asChild variant="secondary" className="mt-6 h-11 border border-border">
                        <Link to="/gerekli-belgeler">
                            Belge detayları ve fotoğraf kuralları <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                    </Button>
                </div>
            </section>

            {/* BASVURU TAKIBI */}
            <VisaSpecimen compact />

            <CommitmentsStrip />

            <SecurityBadges />

            <section className="section" data-testid="landing-tracking">
                <div className="container-page grid items-center gap-10 lg:grid-cols-[1fr_0.9fr]">
                    <div>
                        <span className="eyebrow">Başvuru Takibi</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Başvurunuz nerede?</h2>
                        <p className="mt-3 text-sm leading-7 text-muted-foreground">
                            Takip kodunuzu girin; başvurunuzun belge kontrolü, resmî başvuru veya sonuç
                            adımlarından hangisinde olduğunu tarih ve saatiyle görün. Her durum değişikliği
                            ayrıca e-posta ile de bildirilir.
                        </p>
                        <TrackingBox />
                        <Link
                            to="/hesabim"
                            className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-primary underline-offset-4 hover:underline"
                            data-testid="home-my-applications-link"
                        >
                            Başvurularım sayfasına giriş yap <ArrowRight className="h-3.5 w-3.5" />
                        </Link>
                    </div>
                    <div className="rounded-2xl border border-border bg-card p-7" style={{ boxShadow: "var(--shadow-card)" }}>
                        <h3 className="font-heading text-base font-bold">Takip sayfasında neler görürsünüz?</h3>
                        <ul className="mt-4 space-y-3 text-sm">
                            {[
                                "Belge kontrolü, resmî başvuru ve sonuç adımları",
                                "Eksik belge varsa bildirim ve yeniden yükleme",
                                "Ödeme durumu ve fatura bilgisi",
                                "Onaylanan vize belgenizi indirme bağlantısı",
                            ].map((t) => (
                                <li key={t} className="flex items-start gap-2.5">
                                    <BadgeCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                    <span>{t}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </section>

            {/* MUSTERI YORUMLARI */}
            <ReviewSpotlight summary={content?.review_summary} testimonials={content?.testimonials} />

            {/* SSS */}
            <section className="section">
                <div className="container-page grid gap-10 lg:grid-cols-[0.8fr_1.2fr]">
                    <div>
                        <span className="eyebrow">Sıkça sorulan sorular</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Sıkça sorulan sorular</h2>
                        <p className="mt-3 text-sm leading-6 text-muted-foreground">
                            Pasaport geçerliliği, 18 yaş altı başvurusu, kalış süresinin aşılması, ödeme ve
                            iade koşulları — danışmanlarımıza en çok sorulan başlıklar burada.
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

            {/* CTA BAND */}
            <section className="border-t border-border bg-[hsl(var(--navy))]">
                <div className="container-page flex flex-col items-start justify-between gap-6 py-12 sm:flex-row sm:items-center">
                    <div>
                        <h2 className="text-2xl font-bold text-white sm:text-3xl">Başvurunuzu şimdi başlatın</h2>
                        <p className="mt-2 max-w-xl text-sm leading-6 text-white/70">
                            Ön kontrolde tarihlerinizi girin, hangi vizenin gerektiğini anında söyleyelim.
                            Form doldurmak istemiyorsanız pasaport ve fotoğrafınızı WhatsApp'tan gönderin,
                            başvurunuzu biz oluşturalım.
                        </p>
                    </div>
                    <div className="flex shrink-0 flex-wrap gap-3">
                        <Button asChild className="h-12 px-7 text-base" data-testid="cta-band-apply-button">
                            <Link to="/basvuru">
                                Başvuru Yap <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                        {contact.whatsapp && (
                            <Button asChild variant="secondary" className="h-12 border border-border px-6 text-base" data-testid="cta-band-whatsapp-button">
                                <a
                                    href={waLink(contact, "Merhaba, Dubai vizesi için başvuru yapmak istiyorum.")}
                                    target="_blank"
                                    rel="noreferrer"
                                >
                                    <MessageCircle className="mr-2 h-5 w-5" /> WhatsApp
                                </a>
                            </Button>
                        )}
                    </div>
                </div>
            </section>
        </div>
    );
}
