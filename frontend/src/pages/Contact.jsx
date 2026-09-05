import React, { useEffect, useState } from "react";
import { Clock, Loader2, Mail, MapPin, MessageCircle, Navigation, Phone, Send } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";
import { useContact } from "../lib/contact";

const EMPTY = { name: "", email: "", phone: "", subject: "", message: "" };

const TOPICS = [
    "Vize başvurusu",
    "Fiyat bilgisi",
    "Belge kontrolü",
    "Mevcut başvurum",
    "eSIM / seyahat sigortası",
    "Diğer",
];

const ChannelCard = ({ icon: Icon, title, detail, value, href, testId, external }) => (
    <div className="card-surface p-5" data-testid={testId}>
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
            <Icon className="h-5 w-5 text-primary" />
        </span>
        <h3 className="mt-3.5 font-heading text-base font-bold">{title}</h3>
        <p className="mt-1 text-sm leading-6 text-muted-foreground">{detail}</p>
        {href ? (
            <a
                href={href}
                target={external ? "_blank" : undefined}
                rel={external ? "noreferrer" : undefined}
                className="mt-3 inline-block text-sm font-bold text-primary transition-colors duration-150 hover:text-[hsl(var(--brand-copper))]"
            >
                {value}
            </a>
        ) : (
            <p className="mt-3 text-sm font-semibold">{value}</p>
        )}
    </div>
);

export default function Contact() {
    const contact = useContact();
    const [form, setForm] = useState(EMPTY);
    const [sending, setSending] = useState(false);
    const [sent, setSent] = useState(false);

    useEffect(() => {
        setMeta(
            "İletişim | Dubai Vize Online",
            "Dubai vize başvurunuzla ilgili sorularınız için telefon, WhatsApp veya e-posta ile ulaşın. İstanbul Zeytinburnu ofisimizin adresi ve çalışma saatleri."
        );
    }, []);

    const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

    const submit = async (e) => {
        e.preventDefault();
        if (!form.name.trim() || !form.email.trim() || form.message.trim().length < 5) {
            toast.error("Lütfen adınızı, e-posta adresinizi ve mesajınızı doldurun.");
            return;
        }
        setSending(true);
        try {
            const { data } = await api.post("/contact", form);
            toast.success(data.message || "Mesajınız alındı.");
            setForm(EMPTY);
            setSent(true);
        } catch (err) {
            toast.error(apiError(err, "Mesaj gönderilemedi. Lütfen tekrar deneyin."));
        } finally {
            setSending(false);
        }
    };

    const mapQuery = encodeURIComponent(contact.address || "Parima Plaza Zeytinburnu İstanbul");

    return (
        <div data-testid="contact-page">
            <PageHeader
                eyebrow="İletişim"
                title="Hemen bizimle iletişime geçin"
                description="Dubai vizeniz, ek hizmetleriniz ve mevcut başvurunuz için danışman ekibimiz yanınızda. Formu doldurun ya da aşağıdaki kanallardan yazın; ofis saatlerinde aynı gün dönüş yapıyoruz."
            />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page grid gap-8 lg:grid-cols-[1.05fr_0.95fr]">
                    <form onSubmit={submit} className="card-surface p-6 sm:p-8" data-testid="contact-form">
                        <h2 className="font-heading text-xl font-bold">Bize ulaşın</h2>
                        <p className="mt-1.5 text-sm text-muted-foreground">
                            Vize başvurunuz veya ek hizmetleriniz için formu doldurun.
                        </p>
                        <div className="mt-6 grid gap-5 sm:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="c-name">Adınız Soyadınız *</Label>
                                <Input id="c-name" value={form.name} onChange={set("name")} placeholder="Adınız ve soyadınız" data-testid="contact-name-input" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="c-email">E-posta *</Label>
                                <Input id="c-email" type="email" value={form.email} onChange={set("email")} placeholder="ornek@eposta.com" data-testid="contact-email-input" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="c-phone">Telefon</Label>
                                <Input id="c-phone" value={form.phone} onChange={set("phone")} placeholder="+90 5XX XXX XX XX" data-testid="contact-phone-input" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="c-subject">Konu</Label>
                                <Select
                                    value={form.subject}
                                    onValueChange={(v) => setForm((f) => ({ ...f, subject: v }))}
                                >
                                    <SelectTrigger id="c-subject" data-testid="contact-subject-select">
                                        <SelectValue placeholder="Konu seçiniz" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {TOPICS.map((t) => (
                                            <SelectItem key={t} value={t} data-testid={`contact-subject-option-${t}`}>
                                                {t}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                        <div className="mt-5 space-y-2">
                            <Label htmlFor="c-message">Mesajınız *</Label>
                            <Textarea
                                id="c-message"
                                rows={6}
                                value={form.message}
                                onChange={set("message")}
                                placeholder="Sorunuzu veya talebinizi yazın…"
                                data-testid="contact-message-input"
                            />
                        </div>
                        <Button type="submit" disabled={sending} className="mt-6 h-12 w-full px-7 text-base sm:w-auto" data-testid="contact-submit-button">
                            {sending ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Gönderiliyor…
                                </>
                            ) : (
                                <>
                                    <Send className="mr-2 h-4 w-4" /> Mesajı gönder
                                </>
                            )}
                        </Button>
                        {sent && (
                            <p className="mt-4 rounded-lg border border-[hsl(var(--brand-green)/0.30)] bg-[hsl(var(--brand-green)/0.09)] p-3 text-sm font-medium text-[hsl(var(--brand-green))]" data-testid="contact-success-message">
                                Mesajınız alındı. En kısa sürede size dönüş yapacağız.
                            </p>
                        )}
                    </form>

                    <div className="grid gap-5 sm:grid-cols-2">
                        {contact.phone && (
                            <ChannelCard
                                icon={Phone}
                                title="Hemen arayın"
                                detail="Danışmanlarımız ofis saatlerinde telefonda."
                                value={contact.phone}
                                href={contact.phoneHref}
                                testId="contact-channel-phone"
                            />
                        )}
                        {contact.whatsappHref && (
                            <ChannelCard
                                icon={MessageCircle}
                                title="WhatsApp"
                                detail="Belge ve fiyat sorularınız için en hızlı kanal."
                                value={contact.phone || `+${contact.whatsapp}`}
                                href={contact.whatsappHref}
                                testId="contact-channel-whatsapp"
                                external
                            />
                        )}
                        <ChannelCard
                            icon={Mail}
                            title="E-posta gönderin"
                            detail="Sorularınızı yazın, en kısa sürede yanıtlayalım."
                            value={contact.email}
                            href={`mailto:${contact.email}`}
                            testId="contact-channel-email"
                        />
                        <ChannelCard
                            icon={Clock}
                            title="Çalışma saatleri"
                            detail="Ofis saatleri dışında WhatsApp'tan yazabilirsiniz."
                            value={contact.workingHours}
                            testId="contact-channel-hours"
                        />
                        <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-5 sm:col-span-2">
                            <h3 className="font-heading text-base font-bold">Başvurunuz zaten var mı?</h3>
                            <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                                Takip kodunuzla başvurunuzun durumunu anında görüntüleyebilirsiniz;
                                bizi aramanıza gerek yok.
                            </p>
                            <Button asChild variant="secondary" className="mt-4 h-11 border border-border" data-testid="contact-track-button">
                                <a href="/takip">Başvuru takip sayfası</a>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>

            {contact.address && (
                <section className="border-t border-border bg-[hsl(var(--cloud))] py-10 sm:py-14" data-testid="contact-office-section">
                    <div className="container-page">
                        <span className="eyebrow">Konum</span>
                        <div className="mt-3 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                            <div>
                                <h2 className="text-2xl font-bold">Merkez ofisimiz</h2>
                                <p className="mt-2 max-w-xl text-sm leading-7 text-muted-foreground" data-testid="contact-office-address">
                                    {contact.address}
                                </p>
                            </div>
                            <Button asChild className="h-11 shrink-0" data-testid="contact-directions-button">
                                <a
                                    href={`https://www.google.com/maps/dir/?api=1&destination=${mapQuery}`}
                                    target="_blank"
                                    rel="noreferrer"
                                >
                                    <Navigation className="mr-2 h-4 w-4" /> Yol tarifi al
                                </a>
                            </Button>
                        </div>

                        <div className="mt-6 overflow-hidden rounded-2xl border border-border bg-card" style={{ boxShadow: "var(--shadow-card)" }}>
                            <iframe
                                title="Ofis konumu"
                                src={`https://www.google.com/maps?q=${mapQuery}&output=embed&hl=tr`}
                                className="h-[320px] w-full border-0 sm:h-[400px]"
                                loading="lazy"
                                referrerPolicy="no-referrer-when-downgrade"
                                data-testid="contact-map-iframe"
                            />
                        </div>

                        <p className="mt-4 flex items-start gap-2 text-xs leading-6 text-muted-foreground">
                            <MapPin className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                            Ofise gelmeniz zorunlu değildir; tüm başvuru süreci online yürütülür.
                            Yine de belgelerinizi birlikte gözden geçirmek isterseniz randevu alarak
                            bizi ziyaret edebilirsiniz.
                        </p>
                    </div>
                </section>
            )}
        </div>
    );
}
