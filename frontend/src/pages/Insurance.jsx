import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import {
    AlertTriangle,
    Baby,
    BadgeCheck,
    CalendarClock,
    Globe2,
    HeartPulse,
    Hospital,
    MessageCircle,
    MountainSnow,
    ShieldCheck,
    Users,
} from "lucide-react";
import { setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { PlanShowcase } from "../components/PlanShowcase";
import { Button } from "../components/ui/button";
import { useContact } from "../lib/contact";

const COVERS = [
    {
        icon: Globe2,
        title: "Yedi emirliğin tamamında geçerli",
        detail:
            "Teminat yalnızca Dubai ile sınırlı değildir. Abu Dabi, Şarja veya diğer emirliklere geçtiğinizde de güvenceniz devam eder.",
    },
    {
        icon: ShieldCheck,
        title: "30.000 euroya kadar teminat",
        detail:
            "Acil müdahale, muayene, görüntüleme ve gerektiğinde yatış masrafları poliçe limiti kapsamında karşılanır.",
    },
    {
        icon: HeartPulse,
        title: "Ani ve beklenmedik rahatsızlıklar",
        detail:
            "Seyahatiniz sırasında ortaya çıkan akut sağlık sorunları ve acil durumlar için düzenlenir.",
    },
    {
        icon: CalendarClock,
        title: "7, 15, 30 veya 60 gün",
        detail:
            "Poliçe süresini kalışınıza göre seçersiniz; teminat gidiş tarihinizde başlar ve seçtiğiniz gün sayısı kadar sürer.",
    },
];

const CRITICAL = [
    {
        icon: Baby,
        title: "Çocuklu aileler",
        detail: "Ateş ve mide rahatsızlıkları çocuklarda daha sık görülür; küçük yolcular için poliçe ayrıca değerlendirilir.",
    },
    {
        icon: Users,
        title: "İleri yaştaki yolcular",
        detail: "Aniden gelişen sağlık sorunlarına karşı güvence sağlar, seyahati daha rahat kılar.",
    },
    {
        icon: CalendarClock,
        title: "Uzun konaklamalar",
        detail: "Kalış süresi uzadıkça beklenmedik bir olayla karşılaşma olasılığı da artar.",
    },
    {
        icon: MountainSnow,
        title: "Aktivite ağırlıklı programlar",
        detail: "Çöl safarisi, su sporları ve yüksek irtifa turlarında küçük yaralanma riski daha yüksektir.",
    },
];

const FAQ = [
    {
        q: "Dubai vizesi için sigorta zorunlu mu?",
        a: "Hayır. Turistik vize başvurusunda sigorta şartı aranmaz; tamamen isteğe bağlı bir hizmettir. Poliçe yaptırmamanız başvurunuzun sonucunu etkilemez.",
    },
    {
        q: "Poliçe sadece Dubai'de mi geçerli?",
        a: "Hayır. Teminat Birleşik Arap Emirlikleri genelinde geçerlidir; Abu Dabi, Şarja ve diğer emirlikleri de kapsar.",
    },
    {
        q: "Kronik hastalığım var, poliçe işime yarar mı?",
        a: "Kronik rahatsızlığınıza bağlı masraflar kapsam dışındadır. Buna karşılık seyahatiniz sırasında bu rahatsızlıkla ilgisi olmayan ani bir sağlık sorunu yaşarsanız teminat devreye girer.",
    },
    {
        q: "Sigortayı başvurudan sonra ekleyebilir miyim?",
        a: "Seyahatiniz başlamadan önce eklenebilir. Uçuşunuzdan önce bize yazmanız yeterlidir; yola çıktıktan sonra poliçe düzenlenemez.",
    },
    {
        q: "30 günden uzun kalacağım, ne yapmalıyım?",
        a: "Poliçe süresi 30 gündür ve vize uzatma yaptığınızda kendiliğinden uzamaz. Daha uzun bir kalış planlıyorsanız uygun çözümü belirlemek için önceden bize danışın.",
    },
    {
        q: "Ailemin tamamı için yaptırabilir miyim?",
        a: "Evet. Aynı başvurudaki yolcuların her biri için ayrı poliçe düzenlenir; talebinizi başvuru sırasında belirtmeniz yeterlidir.",
    },
];

export default function Insurance() {
    const contact = useContact();

    useEffect(() => {
        setMeta(
            "Dubai Seyahat Sigortası: Kapsam, Teminat ve Sık Sorulanlar | Dubai Vize Hattı",
            "Dubai seyahat sigortası zorunlu mu, neyi kapsar, kronik hastalıklar dahil mi? BAE genelinde geçerli 30 günlük poliçenin kapsamı, sınırları ve başvuruya nasıl eklendiği.",
            { canonicalPath: "/seyahat-sigortasi" }
        );
    }, []);

    return (
        <div data-testid="insurance-page">
            <PageHeader
                eyebrow="Seyahat Sigortası"
                title="Dubai seyahat sigortası hakkında bilmeniz gerekenler"
                description="Seyahat sağlık sigortası vize başvurusu için zorunlu bir belge değildir; ancak Birleşik Arap Emirlikleri'nde sağlık masraflarının yüksekliği bu poliçeyi düşünmeye değer kılar. Aşağıda kapsamı, sınırlarını ve başvurunuza nasıl eklendiğini bulacaksınız."
            />

            <section className="pb-12 pt-6 sm:pb-16 sm:pt-8" data-testid="insurance-plans">
                <div className="container-page">
                    <PlanShowcase kind="insurance" />
                </div>
            </section>

            <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="insurance-coverage">
                <div className="container-page">
                    <span className="eyebrow">Kapsam</span>
                    <h2 className="mt-3 text-2xl font-bold">Poliçe neyi kapsar?</h2>
                    <p className="mt-2 max-w-3xl text-sm leading-7 text-muted-foreground">
                        Kısaca: poliçe, siz Birleşik Arap Emirlikleri'ndeyken beklenmedik biçimde başlayan bir
                        sağlık sorununu hedefler. Kısa bir tatilde bile ani bir rahatsızlık ciddi bir masraf
                        kalemine dönüşebilir.
                    </p>
                    <div className="mt-7 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                        {COVERS.map(({ icon: Icon, title, detail }) => (
                            <div key={title} className="card-surface p-6">
                                <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                                    <Icon className="h-5 w-5" />
                                </span>
                                <h3 className="mt-4 font-heading text-base font-bold">{title}</h3>
                                <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{detail}</p>
                            </div>
                        ))}
                    </div>

                    <div
                        className="mt-6 flex items-start gap-3 rounded-2xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.08)] p-5 sm:p-6"
                        data-testid="insurance-exclusions"
                    >
                        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--status-warning))]" />
                        <div>
                            <h3 className="font-heading text-base font-bold">Neyi kapsamaz?</h3>
                            <p className="mt-1.5 text-sm leading-7 text-muted-foreground">
                                En önemli ayrım burada: poliçe kronik hastalıkları kapsamaz. Seyahatten önce var
                                olan ve süregelen bir rahatsızlığınız varsa, doğrudan o duruma bağlı masraflar
                                teminat dışındadır. Bu, poliçenin kronik hastalığı olan yolcular için tümüyle
                                işlevsiz olduğu anlamına gelmez; mevcut rahatsızlığınızla ilgisi bulunmayan ani
                                bir sağlık sorununda teminat yine devreye girer.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <section className="section" data-testid="insurance-why">
                <div className="container-page grid gap-8 lg:grid-cols-2">
                    <div>
                        <span className="eyebrow">Zorunlu değilse neden?</span>
                        <h2 className="mt-3 text-2xl font-bold">Küçük bedel, büyük risk farkı</h2>
                        <p className="mt-3 text-sm leading-7 text-muted-foreground">
                            Birleşik Arap Emirlikleri'nde özel hastane masrafları Türkiye'ye kıyasla belirgin
                            biçimde yüksektir. Basit bir acil servis başvurusu bile ciddi bir tutara ulaşabilir;
                            görüntüleme veya bir gecelik yatış söz konusu olduğunda fark daha da açılır.
                        </p>
                        <p className="mt-3 text-sm leading-7 text-muted-foreground">
                            Sigorta bedeli ise vize masrafının yanında küçük bir kalemdir. Riskin büyüklüğü ile
                            maliyetin küçüklüğü arasındaki bu fark, poliçeyi mantıklı kılan asıl nedendir. Güncel
                            tutarı{" "}
                            <Link to="/vize-tipleri" className="font-semibold text-primary hover:underline">
                                hizmet bedelleri sayfamızda
                            </Link>{" "}
                            görebilirsiniz.
                        </p>

                        <div className="mt-6 rounded-2xl border border-border p-5" data-testid="insurance-how-to-add">
                            <h3 className="flex items-center gap-2 font-heading text-base font-bold">
                                <BadgeCheck className="h-5 w-5 text-primary" /> Başvuruya nasıl eklenir?
                            </h3>
                            <ul className="mt-3 space-y-2.5 text-sm leading-6 text-muted-foreground">
                                <li className="flex gap-2">
                                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                                    Ayrı bir süreç yürütmenize gerek yoktur; başvuru adımlarında sigorta
                                    istediğinizi işaretlemeniz ya da danışmanınıza söylemeniz yeterlidir.
                                </li>
                                <li className="flex gap-2">
                                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                                    Sigorta, vize başvurusunda istenen evraklardan biri değildir; gerekli belge
                                    listenize fazladan bir evrak eklemeniz gerekmez.
                                </li>
                                <li className="flex gap-2">
                                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                                    Poliçe dijital olarak düzenlenir ve size iletilir. Belgeyi telefonunuzda
                                    saklamanızı, mümkünse bir çıktısını da yanınızda taşımanızı öneririz.
                                </li>
                                <li className="flex gap-2">
                                    <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                                    Poliçe seyahatiniz başlamadan önce düzenlenmelidir; yola çıktıktan sonra
                                    sigorta yapılamaz.
                                </li>
                            </ul>
                        </div>
                    </div>

                    <div>
                        <span className="eyebrow">Kimler için daha kritik?</span>
                        <h2 className="mt-3 text-2xl font-bold">Her yolcu için faydalı, bazıları için öncelikli</h2>
                        <div className="mt-6 space-y-4">
                            {CRITICAL.map(({ icon: Icon, title, detail }) => (
                                <div key={title} className="flex items-start gap-3.5 rounded-2xl border border-border p-5">
                                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                                        <Icon className="h-5 w-5" />
                                    </span>
                                    <div>
                                        <h3 className="font-heading text-base font-bold">{title}</h3>
                                        <p className="mt-1 text-sm leading-6 text-muted-foreground">{detail}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="insurance-care">
                <div className="container-page grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
                    <div>
                        <span className="eyebrow">Seyahat sırasında</span>
                        <h2 className="mt-3 text-2xl font-bold">Dubai'de sağlık hizmeti almanız gerekirse</h2>
                        <p className="mt-3 text-sm leading-7 text-muted-foreground">
                            Ülkede hem devlet hem özel hastaneler bulunur; turistler çoğunlukla özel hastane ve
                            kliniklere başvurur. Otelinizin resepsiyonu size en yakın sağlık kuruluşunu
                            yönlendirebilir.
                        </p>
                        <ul className="mt-4 space-y-2.5 text-sm leading-6 text-muted-foreground">
                            <li className="flex gap-2">
                                <Hospital className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                Hastaneye giderken poliçe belgenizi ve pasaportunuzu yanınıza alın.
                            </li>
                            <li className="flex gap-2">
                                <Hospital className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                Yapılan işlemlere ait tüm evrakı, reçeteleri ve ödeme belgelerini saklayın;
                                süreç sonrasında bunlar istenebilir.
                            </li>
                            <li className="flex gap-2">
                                <Hospital className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                Durumu en kısa sürede bize de bildirin; yönlendirme konusunda destek olalım.
                            </li>
                        </ul>
                    </div>

                    <div className="card-surface p-6" data-testid="insurance-extension-note">
                        <h3 className="flex items-center gap-2 font-heading text-base font-bold">
                            <CalendarClock className="h-5 w-5 text-primary" /> Vizenizi uzatırsanız
                        </h3>
                        <p className="mt-2 text-sm leading-7 text-muted-foreground">
                            Poliçe 30 gün süreyle düzenlenir. Vize uzatma işlemi yaptırıp ülkede daha uzun
                            kalacaksanız mevcut poliçenizin süresi kendiliğinden uzamaz. Uzatılan dönem için
                            neler yapılabileceğini görüşmek üzere bizimle iletişime geçin.
                        </p>
                        <div className="mt-5 flex flex-wrap gap-3">
                            {contact.whatsappHref && (
                                <Button asChild className="h-11" data-testid="insurance-whatsapp-button">
                                    <a href={contact.whatsappHref} target="_blank" rel="noreferrer">
                                        <MessageCircle className="mr-2 h-4 w-4" /> WhatsApp'tan sorun
                                    </a>
                                </Button>
                            )}
                            <Button asChild variant="secondary" className="h-11 border border-border">
                                <Link to="/iletisim">İletişim sayfası</Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>

            <section className="section" data-testid="insurance-faq">
                <div className="container-page">
                    <span className="eyebrow">Sıkça sorulan sorular</span>
                    <h2 className="mt-3 text-2xl font-bold">Sigorta hakkında merak edilenler</h2>
                    <div className="mt-6 grid gap-4 lg:grid-cols-2">
                        {FAQ.map((f) => (
                            <div key={f.q} className="card-surface p-5">
                                <h3 className="font-heading text-base font-bold">{f.q}</h3>
                                <p className="mt-2 text-sm leading-7 text-muted-foreground">{f.a}</p>
                            </div>
                        ))}
                    </div>

                    <div className="mt-8 flex flex-wrap items-center gap-3 rounded-xl border border-primary/25 bg-primary/5 p-6">
                        <BadgeCheck className="h-5 w-5 text-primary" />
                        <p className="text-sm">
                            Sigortayı vize başvurunuza eklemek için{" "}
                            <Link to="/basvuru" className="font-semibold text-primary hover:underline">
                                başvuru formundaki ek hizmetler adımını
                            </Link>{" "}
                            kullanabilir ya da danışmanımıza yazabilirsiniz. Dubai'de internetsiz kalmamak için{" "}
                            <Link to="/esim" className="font-semibold text-primary hover:underline">
                                eSIM paketlerine
                            </Link>{" "}
                            de göz atın.
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
}
