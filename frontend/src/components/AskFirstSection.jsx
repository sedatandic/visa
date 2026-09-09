import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, CreditCard, FileUp, ShieldCheck } from "lucide-react";
import { Button } from "./ui/button";
import { WhatsAppIcon } from "./WhatsAppIcon";
import { WhatsAppPhoneMock } from "./WhatsAppPhoneMock";
import { useContact, waLink } from "../lib/contact";

const STEPS = [
    {
        icon: FileUp,
        title: "Belgeleri gönderin",
        text: "Pasaportunuzun kimlik sayfası ve bir vesikalık. Pasaportu yükleyin, formu biz doldururuz.",
        badge: "2 dakika",
    },
    {
        icon: CreditCard,
        title: "Ödemeyi yapın",
        text: "Kartla 3D Secure ekranında ya da havale/EFT ile. Başvurunuz ödeme sonrası işleme alınır.",
        badge: "Aynı gün",
    },
    {
        icon: ShieldCheck,
        title: "Vizenizi alın",
        text: "Onaylanan vize PDF olarak e-postanıza gelir. Yazdırmanıza gerek yok, telefonda göstermeniz yeterli.",
        badge: "36 saatte sonuç",
    },
];

/** "Once sorun, formu sonra dusunuruz": WhatsApp sohbet onizlemesi + sureli 3 adim. */
export const AskFirstSection = () => {
    const contact = useContact();
    const href = waLink(contact, "Merhaba, Dubai vizesi hakkında bilgi almak istiyorum.");
    return (
        <section className="section border-y border-border bg-[hsl(var(--cloud))]" data-testid="landing-ask-first">
            <div className="container-page grid gap-12 lg:grid-cols-[0.95fr_1fr] lg:items-start">
                <div>
                    <span className="eyebrow">Önce sorun</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">
                        Formu sonra düşünürüz. İlk adım bir soru.
                    </h2>
                    <p className="mt-3 text-sm leading-6 text-muted-foreground">
                        Pasaport süresi, aile indirimi, vizeyle ne zaman giriş yapılacağı… Aklınıza takılanı
                        WhatsApp'tan yazın. Sıra numarası ve otomatik yanıt yok; cevabı veren kişi işi yapan kişi.
                    </p>

                    <div className="mt-6 flex flex-wrap gap-3">
                        {href && (
                            <Button asChild size="lg" data-testid="ask-first-whatsapp-button">
                                <a href={href} target="_blank" rel="noreferrer">
                                    <WhatsAppIcon className="mr-2 h-4 w-4" /> WhatsApp'tan sor
                                </a>
                            </Button>
                        )}
                        <Button asChild size="lg" variant="outline" data-testid="ask-first-apply-button">
                            <Link to="/basvuru">
                                Başvuruya başla <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                    </div>

                    <div className="mt-9 space-y-5" data-testid="ask-first-steps">
                        {STEPS.map(({ icon: Icon, title, text, badge }, i) => (
                            <div key={title} className="flex items-start gap-4">
                                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-border bg-card">
                                    <Icon className="h-4.5 w-4.5 text-primary" aria-hidden="true" />
                                </span>
                                <div className="min-w-0">
                                    <div className="flex flex-wrap items-center gap-2">
                                        <span className="text-[11px] font-bold tracking-wider text-muted-foreground">
                                            0{i + 1}
                                        </span>
                                        <h3 className="font-heading text-sm font-bold">{title}</h3>
                                        <span className="rounded-full border border-primary/25 bg-primary/[0.06] px-2 py-0.5 text-[11px] font-semibold text-primary">
                                            {badge}
                                        </span>
                                    </div>
                                    <p className="mt-1 text-sm leading-6 text-muted-foreground">{text}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div
                        className="mt-8 flex items-start gap-3 rounded-2xl border border-[hsl(var(--brand-green)/0.3)] bg-[hsl(var(--brand-green)/0.06)] p-5"
                        data-testid="ask-first-note"
                    >
                        <WhatsAppIcon className="mt-0.5 h-5 w-5 shrink-0" />
                        <p className="text-sm leading-6 text-foreground/85">
                            <strong className="font-semibold">Form doldurmak zorunda değilsiniz.</strong> Pasaport
                            ve vesikalık fotoğrafınızı WhatsApp'tan gönderin; başvurunuzu biz oluşturup onay
                            linkini size gönderelim.
                        </p>
                    </div>
                </div>

                <div data-testid="ask-first-chat">
                    <WhatsAppPhoneMock href={href} />
                </div>
            </div>
        </section>
    );
};
