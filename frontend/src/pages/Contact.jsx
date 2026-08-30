import React, { useEffect, useState } from "react";
import { Clock, Loader2, Mail, MapPin, Phone, Send } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { COMPANY, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";

const EMPTY = { name: "", email: "", phone: "", subject: "", message: "" };

export default function Contact() {
    const [form, setForm] = useState(EMPTY);
    const [sending, setSending] = useState(false);
    const [sent, setSent] = useState(false);

    useEffect(() => {
        setMeta(
            "İletişim | VizeAtlas Dubai",
            "Dubai vize başvurunuzla ilgili sorularınız için bize telefon, e-posta veya WhatsApp üzerinden ulaşabilirsiniz."
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

    return (
        <div data-testid="contact-page">
            <PageHeader
                eyebrow="İletişim"
                title="Size nasıl yardımcı olabiliriz?"
                description="Başvuru öncesi veya sonrası tüm sorularınız için bize yazın. Genellikle aynı gün içinde dönüş yapıyoruz."
            />

            <section className="section">
                <div className="container-page grid gap-10 lg:grid-cols-[1.1fr_0.9fr]">
                    <form onSubmit={submit} className="card-surface p-6 sm:p-8" data-testid="contact-form">
                        <h2 className="font-heading text-xl font-bold">Mesaj gönderin</h2>
                        <div className="mt-6 grid gap-5 sm:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="c-name">Ad Soyad *</Label>
                                <Input id="c-name" value={form.name} onChange={set("name")} placeholder="Adınız ve soyadınız" data-testid="contact-name-input" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="c-email">E-posta *</Label>
                                <Input id="c-email" type="email" value={form.email} onChange={set("email")} placeholder="ornek@eposta.com" data-testid="contact-email-input" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="c-phone">Telefon</Label>
                                <Input id="c-phone" value={form.phone} onChange={set("phone")} placeholder="05xx xxx xx xx" data-testid="contact-phone-input" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="c-subject">Konu</Label>
                                <Input id="c-subject" value={form.subject} onChange={set("subject")} placeholder="Örn. 30 gün vize hakkında" data-testid="contact-subject-input" />
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
                            <p className="mt-4 rounded-lg border border-[rgba(22,163,74,0.35)] bg-[rgba(22,163,74,0.1)] p-3 text-sm font-medium text-[#14532D]" data-testid="contact-success-message">
                                Mesajınız alındı. En kısa sürede size dönüş yapacağız.
                            </p>
                        )}
                    </form>

                    <div className="space-y-6">
                        <div className="card-surface p-6">
                            <h2 className="font-heading text-lg font-bold">Doğrudan ulaşın</h2>
                            <ul className="mt-5 space-y-4 text-sm">
                                <li className="flex items-start gap-3">
                                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                        <Phone className="h-4 w-4 text-primary" />
                                    </span>
                                    <div>
                                        <p className="font-semibold">Telefon</p>
                                        <a href={COMPANY.phoneHref} className="text-muted-foreground transition-colors hover:text-primary">
                                            {COMPANY.phone}
                                        </a>
                                    </div>
                                </li>
                                <li className="flex items-start gap-3">
                                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                        <Mail className="h-4 w-4 text-primary" />
                                    </span>
                                    <div>
                                        <p className="font-semibold">E-posta</p>
                                        <a href={`mailto:${COMPANY.email}`} className="text-muted-foreground transition-colors hover:text-primary">
                                            {COMPANY.email}
                                        </a>
                                    </div>
                                </li>
                                <li className="flex items-start gap-3">
                                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                        <MapPin className="h-4 w-4 text-primary" />
                                    </span>
                                    <div>
                                        <p className="font-semibold">Adres</p>
                                        <p className="text-muted-foreground">{COMPANY.address}</p>
                                    </div>
                                </li>
                                <li className="flex items-start gap-3">
                                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                        <Clock className="h-4 w-4 text-primary" />
                                    </span>
                                    <div>
                                        <p className="font-semibold">Çalışma saatleri</p>
                                        <p className="text-muted-foreground">{COMPANY.workingHours}</p>
                                    </div>
                                </li>
                            </ul>
                        </div>

                        <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-6">
                            <h2 className="font-heading text-base font-bold">Başvurunuz zaten var mı?</h2>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Takip kodunuz ve soyadınızla başvurunuzun durumunu anında
                                görüntüleyebilirsiniz. Bunun için bizi aramaniza gerek yok.
                            </p>
                            <Button asChild variant="secondary" className="mt-4 h-11 border border-border">
                                <a href="/takip">Başvuru takip sayfası</a>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
