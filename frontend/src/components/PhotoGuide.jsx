import React from "react";
import { Check, X } from "lucide-react";

export const PHOTO_EXAMPLES = [
    {
        src: "/photo-guide/ok.jpg",
        good: true,
        title: "Doğru",
        note: "Düz beyaz zemin, tam karşıdan, gözlüksüz ve gölgesiz.",
    },
    {
        src: "/photo-guide/bad-background.jpg",
        good: false,
        title: "Yanlış",
        note: "Kalabalık ve koyu arka plan; başka kişiler görünüyor.",
    },
    {
        src: "/photo-guide/bad-sunglasses.jpg",
        good: false,
        title: "Yanlış",
        note: "Güneş gözlüğü, şapka ve yüzde sert gölgeler.",
    },
    {
        src: "/photo-guide/bad-selfie.jpg",
        good: false,
        title: "Yanlış",
        note: "Selfie açısı, bulanık kare ve dağınık ev ortamı.",
    },
];

/** Fotograf uyarisi alan yolcuya dogru/yanlis ornekleri yan yana gosterir. */
export const PhotoGuide = ({ testId = "photo-guide", compact = false }) => (
    <div className="mt-3 rounded-xl border border-border bg-card p-4" data-testid={testId}>
        <p className="font-heading text-sm font-bold">Vesikalık nasıl olmalı?</p>
        <p className="mt-1 text-xs leading-5 text-muted-foreground">
            Aşağıdaki örnekleri karşılaştırın. Telefonla da çekebilirsiniz: beyaz bir duvarın önünde,
            gündüz ışığında, omuz hizasından.
        </p>
        <div className={`mt-3 grid gap-3 ${compact ? "grid-cols-2" : "grid-cols-2 sm:grid-cols-4"}`}>
            {PHOTO_EXAMPLES.map((ex) => (
                <figure key={ex.src} className="space-y-1.5" data-testid={`${testId}-${ex.good ? "good" : "bad"}`}>
                    <div
                        className={`relative overflow-hidden rounded-lg border-2 ${
                            ex.good ? "border-[hsl(var(--success))]" : "border-destructive/60"
                        }`}
                    >
                        <img
                            src={ex.src}
                            alt={ex.note}
                            loading="lazy"
                            className="aspect-[3/4] w-full object-cover"
                        />
                        <span
                            className={`absolute left-1.5 top-1.5 flex h-6 w-6 items-center justify-center rounded-full text-white ${
                                ex.good ? "bg-[hsl(var(--success))]" : "bg-destructive"
                            }`}
                        >
                            {ex.good ? <Check className="h-3.5 w-3.5" /> : <X className="h-3.5 w-3.5" />}
                        </span>
                    </div>
                    <figcaption>
                        <span
                            className={`text-[11px] font-bold uppercase tracking-wider ${
                                ex.good ? "text-[hsl(var(--success))]" : "text-destructive"
                            }`}
                        >
                            {ex.title}
                        </span>
                        <p className="text-[11px] leading-4 text-muted-foreground">{ex.note}</p>
                    </figcaption>
                </figure>
            ))}
        </div>
    </div>
);
