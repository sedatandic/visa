import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, FileCheck2, Mail, Maximize2, MessageCircle, ShieldCheck } from "lucide-react";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";

const FACTS = [
    { icon: Mail, text: "Onaylanan vizeniz PDF olarak e-postanıza ve WhatsApp'ınıza gelir." },
    { icon: FileCheck2, text: "Pasaportunuza etiket yapıştırılmaz; Dubai vizesi tamamen elektroniktir." },
    { icon: ShieldCheck, text: "Havalimanı kontrolünde bu belgeyi telefonunuzdan göstermeniz yeterli." },
    { icon: MessageCircle, text: "Belge kaybolursa takip kodunuzla tekrar indirebilir, bize yazabilirsiniz." },
];

/** Onaylanan e-vizenin ornek gorseli: buyutmeli onizleme + kisa bilgi listesi. */
export const VisaSpecimen = ({ compact = false }) => (
    <section className="border-t border-border bg-[hsl(var(--cloud))] py-14 sm:py-20" data-testid="visa-specimen-section">
        <div className="container-page grid items-start gap-10 lg:grid-cols-[0.9fr_1.1fr]">
            <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-[hsl(var(--brand-copper))]">
                    e-Vize örneği
                </p>
                <h2 className="mt-3 font-heading text-2xl font-bold sm:text-3xl">
                    Onaylanan vizeniz böyle görünür
                </h2>
                <p className="mt-3 max-w-md text-sm leading-7 text-muted-foreground sm:text-base">
                    Başvurunuz sonuçlandığında elinize geçecek belgenin birebir örneği. Kişisel
                    bilgiler gizlenmiş, üzerine "ÖRNEKTİR" ibaresi eklenmiştir.
                </p>

                <ul className="mt-6 space-y-3">
                    {FACTS.map(({ icon: Icon, text }) => (
                        <li key={text} className="flex items-start gap-3 text-sm leading-6 text-muted-foreground">
                            <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                <Icon className="h-3.5 w-3.5 text-primary" />
                            </span>
                            {text}
                        </li>
                    ))}
                </ul>

                {!compact && (
                    <Button asChild className="mt-8 h-12 px-7 text-base" data-testid="visa-specimen-apply-button">
                        <Link to="/basvuru">
                            Başvuruya başla <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>
                    </Button>
                )}
            </div>

            <Dialog>
                <DialogTrigger asChild>
                    <button
                        type="button"
                        className="group relative block w-full overflow-hidden rounded-2xl border border-border bg-white transition-transform duration-300 hover:-translate-y-1"
                        style={{ boxShadow: "var(--shadow-card)" }}
                        data-testid="visa-specimen-open-button"
                    >
                        <img
                            src="/samples/evisa-specimen.jpg"
                            alt="Örnek Dubai e-vize belgesi (ÖRNEKTİR ibareli)"
                            className="w-full object-contain"
                            loading="lazy"
                        />
                        <span className="absolute bottom-3 right-3 flex items-center gap-1.5 rounded-full bg-foreground/85 px-3 py-1.5 text-[11px] font-bold text-white backdrop-blur-sm transition-opacity duration-200 group-hover:opacity-100 sm:opacity-90">
                            <Maximize2 className="h-3 w-3" /> Büyüt
                        </span>
                    </button>
                </DialogTrigger>
                <DialogContent className="max-w-3xl bg-card">
                    <DialogHeader>
                        <DialogTitle>Örnek Dubai e-Vizesi</DialogTitle>
                    </DialogHeader>
                    <img
                        src="/samples/evisa-specimen.jpg"
                        alt="Örnek Dubai e-vize belgesi tam görünüm"
                        className="max-h-[75vh] w-full object-contain"
                        data-testid="visa-specimen-full-image"
                    />
                </DialogContent>
            </Dialog>
        </div>
    </section>
);
