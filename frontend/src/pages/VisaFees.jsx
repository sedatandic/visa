import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
    ArrowRight,
    BadgeCheck,
    CalendarClock,
    Check,
    CreditCard,
    Gauge,
    Receipt,
    Users,
    X,
    Zap,
} from "lucide-react";
import { api } from "../lib/api";
import { formatMoney, setJsonLd, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { FxNote } from "../components/FxNote";
import { BankAccounts } from "../components/BankAccounts";
import { PaymentTrustStrip } from "../components/PaymentTrustStrip";
import { ContentByline } from "../components/ContentByline";
import { ImportantNotice } from "../components/ImportantNotice";
import { Button } from "../components/ui/button";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "../components/ui/accordion";

const INCLUDED = [
    {
        title: "Resmî vize harcı",
        text: "BAE göç idaresinin (GDRFA / ICP) talep ettiği resmî harç gösterilen tutara dahildir.",
    },
    {
        title: "Acente hizmet bedeli",
        text: "Başvurunun hazırlanması, resmî sisteme işlenmesi ve sonuç takibi; ayrıca komisyon alınmaz.",
    },
    {
        title: "Belge ön kontrolü",
        text: "Pasaport ve fotoğrafınız gönderim öncesi uzman ekibimizce kontrol edilir, hatalı belge ret riskini artırmadan düzeltilir.",
    },
    {
        title: "Takip ve teslim",
        text: "Her durum değişikliğinde e-posta bildirimi, takip paneli ve onaylanan vizenin PDF olarak teslimi.",
    },
];

const EXCLUDED = [
    "Uçak bileti, otel ve konaklama masrafları",
    "Seyahat sağlık sigortası poliçesi (zorunlu değil, ek hizmet olarak eklenebilir)",
    "Ekspres / anında ekspres işlem ücreti (yalnız seçerseniz)",
    "Biyometrik fotoğraf çekimi ve pasaport yenileme işlemleri",
    "Resmî makamların sonradan talep edebileceği ek belge masrafları",
];

const FACTORS = [
    {
        icon: CalendarClock,
        title: "Kalış süresi ve giriş hakkı",
        text: "30 veya 60 gün, tek ya da çok girişli vizeler farklı harçlara tabidir. Çok girişli vize, aynı vizeyle Umman/Katar geçişi yapacaklar için gerekir.",
    },
    {
        icon: Users,
        title: "Yolcu sayısı ve yaş",
        text: "Çocuk vizeleri daha düşük harçla düzenlenir. Aynı formda 3 ve üzeri yolcu için aile indirimi otomatik uygulanır.",
    },
    {
        icon: Zap,
        title: "İşlem hızı",
        text: "Standart başvurular ortalama 2 iş gününde sonuçlanır. Ekspres ve anında ekspres kademeleri kişi başı ek ücretlidir.",
    },
    {
        icon: Receipt,
        title: "Güncel dolar kuru",
        text: "Harçlar dolar bazlıdır; TL tutarı başvuru anındaki kurla hesaplanır ve başvurunuz oluştuğunda sabitlenir.",
    },
];

const FEE_FAQ = [
    {
        q: "Dubai vizesi 2026'da ne kadar?",
        a: "Dubai turistik vize ücreti seçtiğiniz vize tipine göre değişir: 30 gün tek girişli vize en uygun seçenektir, 60 gün çok girişli vize en kapsamlı olanıdır. Çocuk vizeleri daha düşük harçla düzenlenir. Yukarıdaki tabloda tüm tipler için güncel TL ve dolar tutarlarını görebilirsiniz.",
    },
    {
        q: "Fiyata komisyon, KDV veya dosya masrafı ekleniyor mu?",
        a: "Hayır. Gösterilen tutar resmî vize harcını ve acente hizmet bedelimizi kapsar. Üzerine komisyon, KDV, dosya veya hizmet bedeli eklenmez; ödeme ekranında toplam tutarı kalem kalem görürsünüz.",
    },
    {
        q: "Ekspres işlem ne kadar, ne kazandırır?",
        a: "Ekspres seçenek başvurunuzu öncelikli sıraya alır ve sonuç yaklaşık 8 mesai saatinde çıkar. Uçuşu aynı gün olan yolcular için anında ekspres kademesi vardır. İkisi de kişi başı ücretlendirilir ve yalnız seçtiğinizde eklenir.",
    },
    {
        q: "Seyahat sağlık sigortası ücrete dahil mi, zorunlu mu?",
        a: "Sigorta vize ücretine dahil değildir ve BAE turistik vizesi için zorunlu tutulmaz. Ancak BAE'de sağlık masrafları çok yüksek olduğu için şiddetle öneriyoruz; başvuru sırasında dilerseniz poliçeyi de sepetinize ekleyebilirsiniz.",
    },
    {
        q: "Nasıl ödeme yapabilirim?",
        a: "Kredi/banka kartıyla 3D Secure korumalı ekranda ya da havale/EFT ile ödeyebilirsiniz. Kart bilgileriniz tarafımızda saklanmaz; ödeme PCI-DSS sertifikalı altyapı üzerinden işlenir.",
    },
    {
        q: "Fiyat sonradan değişir mi?",
        a: "Başvurunuzu oluşturduğunuzda TL tutarınız o anki kurla sabitlenir. Havale ile ödeyecek olsanız bile, arada kur değişse dahi ödeyeceğiniz tutar aynı kalır.",
    },
    {
        q: "Başvurum reddedilirse ücret iade edilir mi?",
        a: "Başvuru resmî makamlara iletildikten sonra hizmet ifa edilmiş sayıldığı için resmî harç iade edilemez. Belgelerinizi ön kontrolden geçirerek ret riskini en aza indiririz. Ayrıntılar için İade ve İptal Koşulları sayfamıza bakabilirsiniz.",
    },
];

const CATEGORY_LABELS = {
    single: "Tek girişli vizeler",
    multiple: "Çok girişli vizeler",
    child: "Çocuk vizeleri",
    extension: "Vize uzatma",
};

const usdLabel = (value) => (value ? `≈ ${Math.round(value)} $` : "");

export default function VisaFees() {
    const [visaTypes, setVisaTypes] = useState([]);
    const [addons, setAddons] = useState([]);
    const [bank, setBank] = useState(null);
    const [discountText, setDiscountText] = useState("");
    const [products, setProducts] = useState([]);

    useEffect(() => {
        setMeta(
            "Dubai Vize Ücreti 2026 — Güncel Fiyatlar ve Ödeme | Dubai Vize Hattı",
            "Dubai (BAE) vize ücretleri 2026: 30/60 günlük tek ve çok girişli vize, çocuk vizesi ve ekspres işlem fiyatları. Ücrete dahil olanlar, ödeme ve iade koşulları net."
        );
        api.get("/visa-types").then(({ data }) => setVisaTypes(data || [])).catch(() => {});
        api.get("/content/site")
            .then(({ data }) => {
                setAddons(data.addons || []);
                setBank(data.bank_transfer || null);
                setDiscountText(data.family_discount_text || "");
            })
            .catch(() => {});
        api.get("/products").then(({ data }) => setProducts(data?.items || data || [])).catch(() => {});
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

    const grouped = useMemo(() => {
        const groups = { single: [], multiple: [], child: [], extension: [] };
        visaTypes.forEach((v) => {
            if (String(v.id || "").includes("extension")) return groups.extension.push(v);
            const key = v.category === "multiple" || v.category === "child" ? v.category : "single";
            return groups[key].push(v);
        });
        return groups;
    }, [visaTypes]);

    // Baslangic fiyati yetiskin vizeleri uzerinden gosterilir (cocuk fiyati yaniltici olur).
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
        <div data-testid="visa-fees-page">
            <PageHeader
                eyebrow="Ücretler & Ödeme"
                title="Dubai vize ücretleri 2026"
                description="Ödeyeceğiniz tutarı en baştan, kalem kalem görün. Resmî harç ve hizmet bedelimiz tek fiyatta; komisyon, KDV veya dosya masrafı eklenmez."
            >
                <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-3 text-sm font-semibold">
                    {[
                        "Tek net fiyat — gizli ücret yok",
                        "Komisyon ve KDV eklenmez",
                        "Fiyat başvuru anında sabitlenir",
                    ].map((chip) => (
                        <span key={chip} className="inline-flex items-center gap-2 text-foreground/85">
                            <BadgeCheck className="h-4.5 w-4.5 text-[hsl(var(--brand-green))]" />
                            {chip}
                        </span>
                    ))}
                </div>
                {cheapest && (
                    <p className="mt-5 text-sm text-muted-foreground">
                        Yetişkin vizeleri{" "}
                        <strong className="text-lg font-extrabold text-foreground">
                            {formatMoney(cheapest.price, cheapest.currency)}
                        </strong>{" "}
                        <span className="text-xs">({usdLabel(cheapest.price_usd)}) kişi başı tutardan başlar</span>
                    </p>
                )}
            </PageHeader>

            {/* 01 - GUNCEL UCRETLER */}
            <section className="pb-14 pt-8 sm:pb-16">
                <div className="container-page">
                    <span className="eyebrow">01 · Güncel ücretler</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Vize tipine göre ücretler</h2>
                    <div className="mt-5 flex flex-wrap items-center gap-3">
                        <FxNote />
                        <span className="text-xs text-muted-foreground">
                            Harçlar dolar bazlıdır, tahsilat güncel kurla TL olarak yapılır.
                        </span>
                    </div>

                    <div className="mt-7 space-y-8">
                        {Object.entries(CATEGORY_LABELS).map(([key, label]) =>
                            grouped[key]?.length ? (
                                <div key={key} data-testid={`fee-group-${key}`}>
                                    <h3 className="font-heading text-base font-bold text-foreground/90">{label}</h3>
                                    <div className="mt-3 overflow-hidden rounded-2xl border border-border bg-card" style={{ boxShadow: "var(--shadow-card)" }}>
                                        <table className="w-full text-left text-sm">
                                            <thead className="bg-[hsl(var(--cloud))] text-xs uppercase tracking-wider text-muted-foreground">
                                                <tr>
                                                    <th className="px-5 py-3 font-semibold">Vize tipi</th>
                                                    <th className="hidden px-5 py-3 font-semibold sm:table-cell">Kalış</th>
                                                    <th className="hidden px-5 py-3 font-semibold md:table-cell">İşlem süresi</th>
                                                    <th className="px-5 py-3 text-right font-semibold">Kişi başı ücret</th>
                                                    <th className="px-5 py-3" />
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {grouped[key].map((v) => (
                                                    <tr
                                                        key={v.id}
                                                        className="border-t border-border/70 transition-colors hover:bg-[hsl(var(--cloud))]"
                                                        data-testid={`fee-row-${v.id}`}
                                                    >
                                                        <td className="px-5 py-4">
                                                            <span className="font-bold text-foreground">{v.short_name || v.name}</span>
                                                            <span className="mt-0.5 block text-xs text-muted-foreground">
                                                                {v.entry_label}
                                                                {v.popular && v.category !== "child" ? " · en çok tercih edilen" : ""}
                                                            </span>
                                                        </td>
                                                        <td className="hidden px-5 py-4 text-muted-foreground sm:table-cell">
                                                            {v.duration_days} gün
                                                        </td>
                                                        <td className="hidden px-5 py-4 text-muted-foreground md:table-cell">
                                                            {v.processing_days}
                                                        </td>
                                                        <td className="px-5 py-4 text-right">
                                                            <span className="block text-base font-extrabold text-foreground">
                                                                {formatMoney(v.price, v.currency)}
                                                            </span>
                                                            <span className="block text-xs text-muted-foreground">
                                                                {usdLabel(v.price_usd)}
                                                            </span>
                                                        </td>
                                                        <td className="px-5 py-4 text-right">
                                                            <Button asChild variant="secondary" className="h-9 border border-border">
                                                                <Link to={`/basvuru?vize=${v.id}`} data-testid={`fee-apply-${v.id}`}>
                                                                    Başvur
                                                                </Link>
                                                            </Button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            ) : null
                        )}
                    </div>

                    {discountText && (
                        <div className="mt-6 flex items-start gap-2.5 rounded-xl border border-primary/25 bg-primary/5 p-4">
                            <Users className="mt-0.5 h-4.5 w-4.5 shrink-0 text-primary" />
                            <p className="text-sm leading-6 text-foreground/85" data-testid="fee-family-discount">
                                <strong className="font-semibold">Aile indirimi:</strong> {discountText} Tek formda tüm
                                aileyi ekleyin, indirim toplamda otomatik düşülür.
                            </p>
                        </div>
                    )}

                    {addons.length > 0 && (
                        <div className="mt-10" data-testid="fee-express-block">
                            <h3 className="font-heading text-base font-bold text-foreground/90">
                                İşlem hızı (isteğe bağlı)
                            </h3>
                            <div className="mt-3 grid gap-4 sm:grid-cols-2">
                                {addons.map((a) => (
                                    <div key={a.id} className="card-surface p-6" data-testid={`fee-addon-${a.id}`}>
                                        <div className="flex items-start justify-between gap-4">
                                            <div className="flex items-center gap-2.5">
                                                <Gauge className="h-5 w-5 text-primary" />
                                                <h4 className="font-heading text-base font-bold">{a.name}</h4>
                                            </div>
                                            <span className="shrink-0 text-right">
                                                <span className="block text-base font-extrabold">
                                                    +{formatMoney(a.price, a.currency)}
                                                </span>
                                                <span className="block text-xs text-muted-foreground">kişi başı</span>
                                            </span>
                                        </div>
                                        <p className="mt-3 text-sm leading-6 text-muted-foreground">{a.description}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {(extraStart.insurance || extraStart.esim || extraStart.tour) && (
                        <div className="mt-8 rounded-2xl border border-border bg-[hsl(var(--cloud))] p-6" data-testid="fee-extras-block">
                            <h3 className="font-heading text-base font-bold">Seyahatinize ekleyebilecekleriniz</h3>
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
                                            className="rounded-xl border border-border bg-card p-4 transition-colors hover:border-primary/40"
                                            data-testid={`fee-extra-${to.replace("/", "")}`}
                                        >
                                            <span className="block text-sm font-semibold text-foreground">{label}</span>
                                            <span className="mt-1 block text-xs text-muted-foreground">
                                                {formatMoney(item.price, item.currency)}'den başlayan fiyatlarla
                                            </span>
                                        </Link>
                                    ))}
                            </div>
                            <p className="mt-4 text-xs leading-5 text-muted-foreground">
                                Bu hizmetler vize ücretine dahil değildir; yalnız sepetinize eklerseniz ücretlendirilir.
                            </p>
                        </div>
                    )}
                </div>
            </section>

            {/* 02 - UCRETE DAHIL */}
            <section className="border-t border-border bg-[hsl(var(--cloud))] py-14 sm:py-16">
                <div className="container-page">
                    <span className="eyebrow">02 · Ücrete dahil</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Ödediğiniz tutar neleri kapsıyor?</h2>
                    <div className="mt-7 grid gap-5 sm:grid-cols-2">
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
                        <div className="rounded-2xl border border-border bg-card p-6" data-testid="fee-excluded">
                            <h3 className="font-heading text-base font-bold">Ücrete dahil olmayanlar</h3>
                            <ul className="mt-4 space-y-2.5">
                                {EXCLUDED.map((e) => (
                                    <li key={e} className="flex items-start gap-2.5 text-sm leading-6 text-muted-foreground">
                                        <X className="mt-1 h-3.5 w-3.5 shrink-0 text-[hsl(var(--brand-red))]" />
                                        {e}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="rounded-2xl border border-border bg-card p-6" data-testid="fee-factors">
                            <h3 className="font-heading text-base font-bold">Ücreti belirleyen faktörler</h3>
                            <div className="mt-4 space-y-4">
                                {FACTORS.map(({ icon: Icon, title, text }) => (
                                    <div key={title} className="flex items-start gap-3">
                                        <Icon className="mt-0.5 h-4.5 w-4.5 shrink-0 text-primary" />
                                        <div>
                                            <span className="block text-sm font-semibold text-foreground">{title}</span>
                                            <span className="mt-0.5 block text-sm leading-6 text-muted-foreground">{text}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 03 - ODEME & GUVENLIK */}
            <section className="py-14 sm:py-16">
                <div className="container-page">
                    <span className="eyebrow">03 · Ödeme & güvenlik</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Ödemeniz nasıl korunuyor?</h2>
                    <PaymentTrustStrip className="mt-6" />

                    <div className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_1fr]">
                        <div className="card-surface p-6">
                            <div className="flex items-center gap-2.5">
                                <CreditCard className="h-5 w-5 text-primary" />
                                <h3 className="font-heading text-base font-bold">Kartla ödeme</h3>
                            </div>
                            <ul className="mt-4 space-y-2.5 text-sm leading-6 text-muted-foreground">
                                <li>• Toplam tutarı ve dökümünü ödeme öncesi kalem kalem görürsünüz.</li>
                                <li>• Son onay bankanızın 3D Secure ekranında verilir.</li>
                                <li>• Kart numaranız sunucularımıza ulaşmaz, tarafımızda saklanmaz.</li>
                                <li>• Ödeme alındığı anda başvurunuz incelemeye geçer.</li>
                            </ul>
                            <div className="mt-5 rounded-xl border border-primary/25 bg-primary/5 p-4">
                                <p className="text-sm leading-6 text-foreground/85">
                                    <strong className="font-semibold">Fiyat kilidi:</strong> Başvurunuz oluştuğunda TL
                                    tutarınız o anki kurla sabitlenir. Havaleyi bir gün sonra yapsanız bile ödeyeceğiniz
                                    tutar değişmez.
                                </p>
                            </div>
                        </div>

                        <div>
                            <h3 className="font-heading text-base font-bold">Havale / EFT ile ödeme</h3>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Kart kullanmak istemiyorsanız havale/EFT ile de ödeyebilirsiniz. Açıklama alanına
                                başvuru numaranızı yazmanız yeterli; ödemeniz görüldüğünde başvurunuz işleme alınır.
                            </p>
                            <div className="mt-4">
                                <BankAccounts bank={bank} />
                            </div>
                        </div>
                    </div>

                    <div className="mt-8 rounded-2xl border border-border bg-card p-6" data-testid="fee-refund-summary">
                        <h3 className="font-heading text-base font-bold">İptal ve iade politikası</h3>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Başvurunuz resmî makamlara iletilmeden önce iptal talebinde bulunursanız, resmî harç
                            dışındaki tutar iade edilir. Başvuru resmî sisteme işlendikten sonra hizmet ifa edilmiş
                            sayıldığı için harç iadesi yapılamaz; ret durumunda da resmî harç geri alınamaz. Bu nedenle
                            belgelerinizi gönderim öncesi ön kontrolden geçiriyoruz.
                        </p>
                        <Button asChild variant="secondary" className="mt-4 h-11 border border-border">
                            <Link to="/iade-kosullari" data-testid="fee-refund-link">
                                İade ve iptal koşullarının tamamı
                            </Link>
                        </Button>
                    </div>
                </div>
            </section>

            {/* 04 - SSS */}
            <section className="border-t border-border bg-[hsl(var(--cloud))] py-14 sm:py-16">
                <div className="container-page">
                    <span className="eyebrow">04 · Sık sorulan sorular</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Ücretler hakkında sık sorulanlar</h2>
                    <Accordion type="single" collapsible className="mt-6 w-full" data-testid="fee-faq-accordion">
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
                            Toplam tutarınızı görmek 2 dakika sürer
                        </h2>
                        <p className="mt-2 max-w-xl text-sm leading-6 text-white/70">
                            Vize tipinizi ve yolcularınızı seçin; ödeme öncesi tüm kalemleri özet ekranında görün.
                        </p>
                    </div>
                    <div className="flex flex-wrap gap-3">
                        <Button asChild variant="secondary" className="h-12 border border-white/20 bg-white/10 px-6 text-white hover:bg-white/20">
                            <Link to="/gerekli-belgeler">Gerekli belgeler</Link>
                        </Button>
                        <Button asChild className="h-12 px-7 text-base" data-testid="fee-cta-apply">
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
