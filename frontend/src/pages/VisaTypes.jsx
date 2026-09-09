import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
    AlertTriangle,
    ArrowRight,
    BadgeCheck,
    CalendarClock,
    Check,
    CreditCard,
    Receipt,
    Users,
    X,
    Zap,
} from "lucide-react";
import { api } from "../lib/api";
import { formatMoney, setJsonLd, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { PricingTabs } from "../components/PricingTabs";
import { VisaGuideLinks } from "../components/VisaGuideLinks";
import { VisaComparison } from "../components/VisaComparison";
import { BankAccounts } from "../components/BankAccounts";
import { ImportantNotice } from "../components/ImportantNotice";
import { FxNote } from "../components/FxNote";
import { GuaranteeBadge } from "../components/GuaranteeBadge";
import { PaymentTrustStrip } from "../components/PaymentTrustStrip";
import { ContentByline } from "../components/ContentByline";
import { Button } from "../components/ui/button";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "../components/ui/accordion";

const INCLUDED = [
    {
        title: "Resmî harç tek tutarın içinde",
        text: "BAE göç idaresinin (GDRFA / ICP) tahsil ettiği harcı ayrıca ödemezsiniz; ekranda gördüğünüz tutar harcı da kapsar.",
    },
    {
        title: "Dosyanızın kurulması",
        text: "Bilgileriniz resmî sisteme istenen formatta işlenir, eksik alanlar tamamlanır ve başvuru idareye tarafımızdan iletilir.",
    },
    {
        title: "Gönderim öncesi belge denetimi",
        text: "Pasaport sayfanız ve vesikalığınız kabul kriterlerine göre denetlenir; kusurlu belge başvuruya hiç girmeden düzeltilir.",
    },
    {
        title: "Süreç bildirimleri ve dijital teslim",
        text: "Her durum değişikliğinde bilgilendirilirsiniz; onaylanan vize PDF olarak e-posta ve WhatsApp ile elinize geçer.",
    },
];

const EXCLUDED = [
    "Uçak bileti, otel ve transfer giderleri (vize başvurusunda istenmez)",
    "Seyahat sağlık sigortası poliçesi — isteğe bağlı ek hizmet",
    "Ekspres vize hizmeti — yalnız siz işaretlerseniz",
    "Vesikalık çekimi, pasaport yenileme, noter ve tercüme masrafları",
    "İdarenin sonradan isteyebileceği ilave belgelerin temin masrafı",
];

const FACTORS = [
    {
        icon: CalendarClock,
        title: "Kalış ve giriş hakkı",
        text: "Bedel iki tercihe göre değişir: 30 mu 60 gün, tek mi çok giriş. Umman veya Katar'a çıkıp döneceksiniz çok girişli seçenek gerekir.",
    },
    {
        icon: Users,
        title: "Yolcu profili",
        text: "Çocuk yolcular daha düşük harçla işlenir. Aynı formdaki üçüncü yolcudan sonra aile indirimi tutara kendiliğinden yansır.",
    },
    {
        icon: Zap,
        title: "Sıra önceliği",
        text: "Standart sırada 36 saat. Uçuşu yakın olanlar için ekspres kademesi vardır; sonuç 12 saat içinde çıkar.",
    },
    {
        icon: Receipt,
        title: "Dolar kuru",
        text: "Harç dolar cinsindendir. TL karşılığı, başvurunuzu oluşturduğunuz andaki satış kuruyla hesaplanır ve o tutar kilitlenir.",
    },
];

const FEE_FAQ = [
    {
        q: "Hizmet bedeli ile resmî harç arasındaki fark nedir?",
        a: "Resmî harç, BAE göç idaresine ödenen ve tutarını devletin belirlediği kalemdir. Hizmet bedeli ise dosyanızın kurulması, belge denetimi, resmî sisteme işlenmesi ve sonuç takibi karşılığıdır. Sayfadaki fiyat ikisinin toplamıdır; ödeme ekranında dökümünü görürsünüz.",
    },
    {
        q: "Gördüğüm tutarın üstüne başka bir kalem ekleniyor mu?",
        a: "Eklenmiyor. Komisyon, dosya masrafı ya da 'işlem ücreti' adı altında sürpriz bir kalem çıkmaz. Tutarı yalnız siz değiştirirsiniz: ekspres vize hizmeti, sigorta, eSIM veya tur eklerseniz sepet o kadar artar.",
    },
    {
        q: "Aile indirimi kaç kişiden başlıyor, nasıl uygulanıyor?",
        a: "Aynı başvuruya eklediğiniz üçüncü yolcudan itibaren indirim devreye girer ve özet ekranındaki toplamdan otomatik düşer. Ayrı ayrı başvuru yaparsanız indirim oluşmaz; eşinizi ve çocuklarınızı tek forma ekleyin.",
    },
    {
        q: "Ekspres vize hizmetini seçmek zorunda mıyım?",
        a: "Hayır. Standart sıra ücretsizdir ve 36 saat içinde sonuçlanır. Ekspres vize hizmeti yalnız uçuşu yakın olanlar için vardır, kişi başı ücretlendirilir ve işaretlemediğiniz sürece sepete girmez.",
    },
    {
        q: "Havale ile ödeyeceğim, arada kur değişirse ne olur?",
        a: "Başvuru oluştuğu anda TL tutarınız kilitlenir. Ödemeyi ertesi gün yapsanız ve dolar yükselse bile bankaya yatıracağınız tutar aynı kalır; fark size yansıtılmaz.",
    },
    {
        q: "Vize onaylanmazsa ödediğim tutarın ne kadarı geri gelir?",
        a: "Başvuru idareye iletilmeden önce iptal ederseniz harç dışındaki kısım iade edilir. Dosya resmî sisteme işlendikten sonra hizmet tamamlanmış sayılır ve harç, sonuç ne olursa olsun geri alınamaz. Ret oranını düşürmek için belgeleri gönderim öncesi denetliyoruz.",
    },
    {
        q: "Kart bilgilerim nerede saklanıyor?",
        a: "Hiçbir yerde. Kart verisi tarayıcınızdan doğrudan PCI-DSS sertifikalı ödeme altyapısına gider, son onayı bankanızın 3D Secure ekranında verirsiniz. Bizim sunucularımıza kart numarası ulaşmaz.",
    },
];

const usdLabel = (value) => (value ? `≈ ${Math.round(value)} $` : "");

export default function VisaTypes() {
    const [bank, setBank] = useState(null);
    const [visaTypes, setVisaTypes] = useState([]);
    const [products, setProducts] = useState([]);

    useEffect(() => {
        setMeta(
            "Dubai Vize Fiyatları 2026 | Dubai Vize Hattı",
            "Dubai (BAE) vize hizmet bedelleri 2026: 30/60 gün tek ve çok girişli vize, çocuk vizesi, uzatma ve ekspres fiyatları. Bedele dahil olanlar, ödeme ve iade koşulları net."
        );
        api.get("/content/site")
            .then(({ data }) => setBank(data.bank_transfer || null))
            .catch(() => {});
        api.get("/visa-types")
            .then(({ data }) => setVisaTypes(data || []))
            .catch(() => {});
        api.get("/products")
            .then(({ data }) => setProducts(data?.items || data || []))
            .catch(() => {});
    }, []);

    useEffect(() => {
        setJsonLd("visa-fees-faq", {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: FEE_FAQ.map((item) => ({
                "@type": "Question",
                name: item.q,
                acceptedAnswer: { "@type": "Answer", text: item.a },
            })),
        });
        return () => setJsonLd("visa-fees-faq", null);
    }, []);

    // Baslangic tutari yetiskin vizeleri uzerinden gosterilir (cocuk fiyati yaniltici olur).
    const cheapest = useMemo(
        () =>
            visaTypes
                .filter((v) => v.category !== "child" && !String(v.id || "").includes("extension"))
                .reduce((min, v) => (min && min.price <= v.price ? min : v), null),
        [visaTypes]
    );

    const extraStart = useMemo(() => {
        const min = (prefix) => {
            const list = products.filter((p) => String(p.id || "").startsWith(prefix));
            if (!list.length) return null;
            return list.reduce((a, b) => (a.price <= b.price ? a : b));
        };
        return { insurance: min("ins_"), esim: min("esim_"), tour: min("tour_") };
    }, [products]);

    return (
        <div data-testid="visa-types-page">
            <PageHeader
                eyebrow="Hizmet Bedelleri"
                title="Dubai vize hizmet bedelleri"
                description="Kalış süreniz, giriş sayınız ve yolcuların yaşına göre bedel değişir. Aşağıdaki tutarlar kişi başıdır, tek seferliktir ve resmî harcı da içerir."
            >
                <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3 text-sm font-semibold">
                    {[
                        "Harç ve hizmet bedeli tek tutarda",
                        "Komisyon, KDV veya dosya masrafı yok",
                        "Tutar başvuru anında kilitlenir",
                    ].map((chip) => (
                        <span key={chip} className="inline-flex items-center gap-2 text-foreground/85">
                            <BadgeCheck className="h-5 w-5 text-[hsl(var(--brand-green))]" />
                            {chip}
                        </span>
                    ))}
                </div>
                {cheapest && (
                    <p className="mt-5 text-sm text-muted-foreground" data-testid="fees-starting-price">
                        Yetişkin vizeleri{" "}
                        <strong className="text-lg font-extrabold text-foreground">
                            {formatMoney(cheapest.price, cheapest.currency)}
                        </strong>{" "}
                        <span className="text-xs">({usdLabel(cheapest.price_usd)}) kişi başı tutardan başlar</span>
                    </p>
                )}
            </PageHeader>

            {/* 01 - GUNCEL BEDELLER */}
            <section className="pb-14 pt-6 sm:pb-16 sm:pt-8">
                <div className="container-page">
                    <span className="eyebrow">01 · Güncel bedeller</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Vize tipine göre kişi başı bedel</h2>
                    <div className="mb-6 mt-5 flex flex-wrap items-center gap-3">
                        <FxNote />
                        <span className="text-xs text-muted-foreground">
                            Harçlar dolar bazlıdır, tahsilat güncel kurla TL olarak yapılır.
                        </span>
                    </div>
                    <PricingTabs />

                    <GuaranteeBadge className="mt-8" />

                    {visaTypes.length > 1 && (
                        <div className="mt-14" data-testid="visa-comparison-section">
                            <span className="eyebrow">Karar Verin</span>
                            <h2 className="mt-3 text-2xl font-bold">30 gün mü 60 gün mü, tek giriş mi çok giriş mi?</h2>
                            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
                                Dört vizenin süresini, giriş hakkını, bedelini ve kimlere uygun olduğunu tek tabloda
                                karşılaştırın. Tablodaki butondan seçtiğiniz vize başvuru formunda otomatik seçili gelir.
                            </p>
                            <div className="mt-6">
                                <VisaComparison visas={visaTypes} />
                            </div>
                        </div>
                    )}
                </div>
            </section>

            {/* 02 - BEDELIN KAPSAMI */}
            <section className="border-t border-border bg-[hsl(var(--cloud))] py-14 sm:py-16">
                <div className="container-page">
                    <span className="eyebrow">02 · Bedelin kapsamı</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Ödediğiniz tutar karşılığında ne alıyorsunuz?</h2>
                    <div className="mt-7 grid gap-5 sm:grid-cols-2" data-testid="fees-included">
                        {INCLUDED.map((i) => (
                            <div key={i.title} className="rounded-2xl border border-border bg-card p-6">
                                <div className="flex items-center gap-2.5">
                                    <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[hsl(var(--brand-green)/0.12)]">
                                        <Check className="h-4 w-4 text-[hsl(var(--brand-green))]" />
                                    </span>
                                    <h3 className="font-heading text-base font-bold">{i.title}</h3>
                                </div>
                                <p className="mt-3 text-sm leading-6 text-muted-foreground">{i.text}</p>
                            </div>
                        ))}
                    </div>

                    <div className="mt-8 grid gap-6 lg:grid-cols-2">
                        <div className="rounded-2xl border border-border bg-card p-6" data-testid="fees-excluded">
                            <h3 className="font-heading text-base font-bold">Bedele dahil olmayanlar</h3>
                            <ul className="mt-4 space-y-2.5">
                                {EXCLUDED.map((e) => (
                                    <li key={e} className="flex items-start gap-2.5 text-sm leading-6 text-muted-foreground">
                                        <X className="mt-1 h-3.5 w-3.5 shrink-0 text-[hsl(var(--brand-red))]" />
                                        {e}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="rounded-2xl border border-border bg-card p-6" data-testid="fees-factors">
                            <h3 className="font-heading text-base font-bold">Bedeli belirleyen dört unsur</h3>
                            <div className="mt-4 space-y-4">
                                {FACTORS.map(({ icon: Icon, title, text }) => (
                                    <div key={title} className="flex items-start gap-3">
                                        <Icon className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                                        <div>
                                            <span className="block text-sm font-semibold text-foreground">{title}</span>
                                            <span className="mt-0.5 block text-sm leading-6 text-muted-foreground">{text}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {(extraStart.insurance || extraStart.esim || extraStart.tour) && (
                        <div className="mt-8 rounded-2xl border border-border bg-card p-6" data-testid="fees-extras-block">
                            <h3 className="font-heading text-base font-bold">Sepete ekleyebileceğiniz seyahat hizmetleri</h3>
                            <div className="mt-4 grid gap-4 sm:grid-cols-3">
                                {[
                                    { item: extraStart.insurance, label: "Seyahat sağlık sigortası", to: "/seyahat-sigortasi" },
                                    { item: extraStart.esim, label: "Dubai eSIM (internet)", to: "/esim" },
                                    { item: extraStart.tour, label: "Çöl safarisi turu", to: "/dubai-turlari" },
                                ]
                                    .filter((x) => x.item)
                                    .map(({ item, label, to }) => (
                                        <Link
                                            key={to}
                                            to={to}
                                            className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-4 transition-colors hover:border-primary/40"
                                            data-testid={`fees-extra-${to.replace("/", "")}`}
                                        >
                                            <span className="block text-sm font-semibold text-foreground">{label}</span>
                                            <span className="mt-1 block text-xs text-muted-foreground">
                                                {formatMoney(item.price, item.currency)}'den başlayan fiyatlarla
                                            </span>
                                        </Link>
                                    ))}
                            </div>
                            <p className="mt-4 text-xs leading-5 text-muted-foreground">
                                Bu hizmetler vize bedeline dahil değildir; yalnız sepetinize eklerseniz ücretlendirilir.
                            </p>
                        </div>
                    )}
                </div>
            </section>

            {/* 03 - ODEME & GUVENLIK */}
            <section className="py-14 sm:py-16">
                <div className="container-page">
                    <span className="eyebrow">03 · Ödeme & güvenlik</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Ödemeniz nasıl korunuyor?</h2>
                    <PaymentTrustStrip className="mt-6" />

                    <div className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_1fr]" data-testid="fees-payment-block">
                        <div className="card-surface p-6">
                            <div className="flex items-center gap-2.5">
                                <CreditCard className="h-5 w-5 text-primary" />
                                <h3 className="font-heading text-base font-bold">Kartla ödeme</h3>
                            </div>
                            <ul className="mt-4 space-y-2.5 text-sm leading-6 text-muted-foreground">
                                <li>• Ödemeden önce vize, ek hizmet ve indirim satırlarını ayrı ayrı görürsünüz.</li>
                                <li>• Son onay bankanızın 3D Secure ekranında sizde kalır.</li>
                                <li>• Kart numarası sunucularımıza hiç ulaşmaz, tarafımızda saklanmaz.</li>
                                <li>• Ödeme düştüğü an dosyanız incelemeye alınır, bildirim size gelir.</li>
                            </ul>
                            <div className="mt-5 rounded-xl border border-primary/25 bg-primary/5 p-4">
                                <p className="text-sm leading-6 text-foreground/85">
                                    <strong className="font-semibold">Tutar kilidi:</strong> Başvurunuz oluştuğunda TL
                                    tutarınız o anki kurla sabitlenir. Havaleyi bir gün sonra yapsanız bile ödeyeceğiniz
                                    tutar değişmez.
                                </p>
                            </div>
                        </div>

                        <div data-testid="visa-types-bank-section">
                            <h3 className="font-heading text-base font-bold">Havale / EFT ile ödeme</h3>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Kart kullanmak istemiyorsanız kurumsal hesaplarımıza havale/EFT yapabilirsiniz. Açıklama
                                alanına başvuru numaranızı yazmanız yeterli; ödeme görüldüğünde dosyanız işleme alınır.
                            </p>
                            <div className="mt-4">
                                <BankAccounts
                                    bank={bank}
                                    footNote="Resmî harç, başvurunuz idareye iletildikten sonra iade edilmez; hizmet bedelimizin iadesi İade Politikası'na tabidir."
                                />
                            </div>
                        </div>
                    </div>

                    <div className="mt-8 rounded-2xl border border-border bg-card p-6" data-testid="fees-refund-summary">
                        <h3 className="font-heading text-base font-bold">İptal ve iade politikası özeti</h3>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Dosyanız idareye iletilmeden önce iptal talebi gelirse, resmî harç dışındaki tutar iade
                            edilir. Başvuru resmî sisteme işlendikten sonra hizmet tamamlanmış sayıldığı için harç
                            iadesi yapılamaz; ret hâlinde de harç geri alınamaz. Bu yüzden belgelerinizi gönderim
                            öncesi denetleyip riski en aza indiriyoruz.
                        </p>
                        <Button asChild variant="secondary" className="mt-4 h-11 border border-border">
                            <Link to="/iade-kosullari" data-testid="fees-refund-link">
                                İade ve iptal koşullarının tamamı
                            </Link>
                        </Button>
                    </div>

                    <div className="mt-8 flex items-start gap-3 rounded-xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.09)] p-5">
                        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--status-warning))]" />
                        <p className="text-sm leading-6 text-[hsl(var(--status-warning))]">
                            Harçlar ve işlem süreleri yetkili merciler tarafından güncellenebilir. Başvurunuzu
                            oluşturmadan önce seçtiğiniz vizelerin bedelleri özet ekranında yeniden gösterilir.
                        </p>
                    </div>
                </div>
            </section>

            {/* 04 - REHBERLER + SSS */}
            <section className="border-t border-border bg-[hsl(var(--cloud))] py-14 sm:py-16">
                <div className="container-page">
                    <div data-testid="visa-guides-index">
                        <span className="eyebrow">04 · Vize rehberi</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Her vize tipi için detaylı rehber</h2>
                        <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
                            Hangi vizenin size uygun olduğundan emin değilseniz, ilgili rehberde şartları, gerekli
                            belgeleri ve sıkça sorulan soruları bulabilirsiniz.
                        </p>
                        <div className="mt-6">
                            <VisaGuideLinks />
                        </div>
                    </div>

                    <div className="mt-14">
                        <span className="eyebrow">05 · Sık sorulan sorular</span>
                        <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Bedeller ve ödeme hakkında sorulanlar</h2>
                        <Accordion type="single" collapsible className="mt-6 w-full" data-testid="fees-faq-accordion">
                            {FEE_FAQ.map((item, i) => (
                                <AccordionItem key={i} value={`fee-faq-${i}`}>
                                    <AccordionTrigger className="text-left text-sm font-semibold sm:text-base">
                                        {item.q}
                                    </AccordionTrigger>
                                    <AccordionContent className="text-sm leading-7 text-muted-foreground">
                                        {item.a}
                                    </AccordionContent>
                                </AccordionItem>
                            ))}
                        </Accordion>
                    </div>

                    <div className="mt-10">
                        <ImportantNotice compact />
                    </div>
                    <ContentByline className="mt-6" />
                </div>
            </section>

            {/* CTA */}
            <section className="border-t border-border bg-[hsl(var(--navy))]">
                <div className="container-page flex flex-col items-start gap-5 py-12 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <h2 className="font-heading text-2xl font-bold text-white">
                            Aileniz için tek başvuru yeterli
                        </h2>
                        <p className="mt-2 max-w-xl text-sm leading-6 text-white/70">
                            Eşinizi ve çocuklarınızı aynı forma ekleyin; indirim ve toplam tutar özet ekranında
                            anında hesaplanır.
                        </p>
                    </div>
                    <div className="flex flex-wrap gap-3">
                        <Button asChild variant="secondary" className="h-12 border border-white/20 bg-white/10 px-6 text-white hover:bg-white/20">
                            <Link to="/gerekli-belgeler">Gerekli belgeler</Link>
                        </Button>
                        <Button asChild className="h-12 px-7 text-base" data-testid="visa-types-apply-button">
                            <Link to="/basvuru">
                                Başvuruya başla <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                    </div>
                </div>
            </section>
        </div>
    );
}
