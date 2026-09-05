import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    ArrowRight,
    BadgeCheck,
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
} from "lucide-react";
import { motion } from "framer-motion";
import { api } from "../lib/api";
import { IMAGES, setMeta } from "../lib/site";
import { useContact, waLink } from "../lib/contact";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { ReviewSpotlight } from "../components/ReviewSpotlight";
import { AuthorityStrip } from "../components/AuthorityStrip";
import { VisaShowcase } from "../components/VisaShowcase";
import { HeroSlider } from "../components/HeroSlider";
import { HeroHeadline } from "../components/HeroHeadline";
import { HomeBundleStrip } from "../components/HomeBundleStrip";
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
    { icon: PlaneTakeoff, title: "Online ve hızlı başvuru", detail: "Tüm süreç web üzerinden, ortalama 5 dakikada tamamlanır." },
    { icon: ShieldCheck, title: "Güvenli belge yükleme", detail: "Pasaportunuzu hiçbir yere teslim etmezsiniz; dijital kopya yeterli." },
    { icon: CreditCard, title: "Kolay ödeme seçenekleri", detail: "Kredi kartı veya banka havalesi ile ödeyin." },
    { icon: Radar, title: "Başvuru durumunu takip etme", detail: "Takip kodunuzla her adımı anlık görün." },
    { icon: HeadphonesIcon, title: "Uzman destek ekibi", detail: "Danışmanınız başvurunuzu gönderilmeden önce kontrol eder." },
];

const PROCESS = [
    { step: "1", title: "Bilgilerinizi girin", detail: "Başvuru formunu doldurun ve seyahat bilgilerinizi paylaşın." },
    { step: "2", title: "Evrakları yükleyin", detail: "Pasaport ve gerekli diğer belgeleri sisteme ekleyin." },
    { step: "3", title: "Ödemenizi tamamlayın", detail: "Güvenli ödeme altyapısı üzerinden işleminizi tamamlayın." },
    { step: "4", title: "Sonucunuzu alın", detail: "Onaylanan vize belgeniz e-posta adresinize gönderilir." },
];

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

    useEffect(() => {
        setMeta(
            "Dubai Vizesi Başvurusu | Online Başvuru ve Fiyatlar | Dubai Vize Online",
            "Dubai (BAE) vize başvurunuzu tamamen online tamamlayın: evraklarınızı yükleyin, ödemenizi yapın, onaylanan vizenizi e-posta ile alın. Net fiyatlar ve başvuru takibi."
        );
        api.get("/content/site").then(({ data }) => setContent(data)).catch(() => {});
    }, []);

    return (
        <div data-testid="home-page">
            {/* HERO */}
            <section className="relative isolate" data-testid="landing-hero">
                <div className="container-page relative pt-0">
                    <motion.div
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.45 }}
                        className="relative overflow-hidden rounded-[var(--radius-xl)] border border-white/60 bg-card/70 px-5 pb-10 pt-6 backdrop-blur-sm sm:px-10 sm:pb-14 sm:pt-8"
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
                            <HeroHeadline />

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

                        <div className="relative mt-10">
                            <HeroSlider />
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
                        <p className="mt-3 text-sm leading-6 text-muted-foreground">
                            Dubai vizesi bizim tek uzmanlık alanımız. Her dosya, yetkili mercilere
                            iletilmeden önce bir danışmanın elinden geçiyor; ret sebebi olabilecek eksikler
                            siz farkına varmadan düzeltiliyor.
                        </p>
                    </div>
                    <div className="mt-9 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                        {ADVANTAGES.map(({ icon: Icon, title, detail }, i) => (
                            <div
                                key={title}
                                className="card-surface card-hoverable p-6"
                                data-testid={`advantage-card-${i + 1}`}
                            >
                                <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10">
                                    <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
                                </span>
                                <h3 className="mt-4 font-heading text-base font-semibold">{title}</h3>
                                <p className="mt-2 text-sm leading-6 text-muted-foreground">{detail}</p>
                            </div>
                        ))}
                        <div className="flex flex-col justify-center rounded-[var(--radius-lg)] border border-border bg-[hsl(var(--cloud))] p-6">
                            <h3 className="font-heading text-base font-semibold">Kimler başvurabilir?</h3>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Umuma mahsus (bordo) pasaport sahibi Türk vatandaşları için Dubai vizesi
                                zorunludur ve başvuru online yapılabilir. Hususi (yeşil), hizmet ve
                                diplomatik pasaport hamilleri yılda 90 güne kadar vizesiz giriş yapar.
                                Başvurular şu an Türkiye doğumlu yolcular için alınmaktadır.
                            </p>
                            <Button asChild variant="secondary" className="mt-4 h-11 border border-border">
                                <Link to="/iletisim" data-testid="eligibility-ask-button">
                                    Durumunuzu sorun
                                </Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>

            {/* BASVURU SURECI */}
            <section
                className="section border-y border-border bg-[hsl(var(--cloud))]"
                data-testid="landing-how-it-works"
            >
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Başvuru Süreci</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">4 adımda Dubai vizesi</h2>
                        <p className="mt-3 text-sm leading-6 text-muted-foreground">
                            Randevu yok, kargo yok, kuyruk yok. Formu açtığınız yerden onaylı vizenizi
                            indirdiğiniz ana kadar her adım aynı ekranda ilerliyor.
                        </p>
                    </div>
                    <div className="mt-9 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                        {PROCESS.map((s) => (
                            <div key={s.step} className="card-surface card-hoverable p-6" data-testid={`process-step-${s.step}`}>
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

            {/* GEREKLI BELGELER */}
            <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="landing-documents">
                <div className="container-page">
                    <div className="max-w-2xl">
                        <span className="eyebrow">Gerekli Belgeler</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Başvuru için gereken belgeler</h2>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Pasaportunuzun kimlik sayfası ve beyaz fonlu bir vesikalık çoğu başvuru için
                            yeterli. Telefonunuzla çektiğiniz fotoğrafı yükleyin; kalan evrakları gerekirse
                            danışmanınız sizden ayrıca ister.
                        </p>
                    </div>
                    <div className="mt-9 grid items-start gap-8 lg:grid-cols-[0.85fr_1.15fr]">
                        <div
                            className="overflow-hidden rounded-2xl border border-border lg:sticky lg:top-28"
                            style={{ boxShadow: "var(--shadow-card)" }}
                        >
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

            {/* BASVURU TAKIBI */}
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
