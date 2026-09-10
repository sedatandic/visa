import React from "react";
import { Check, X } from "lucide-react";

const EXAMPLES = [
    {
        src: "/passport-guide/ok.jpg",
        good: true,
        title: "Doğru",
        note: "Sayfanın tamamı çerçevede, düz ışık, yazılar net.",
    },
    {
        src: "/passport-guide/bad-crop.jpg",
        good: false,
        title: "Yanlış",
        note: "Köşeler kesilmiş, sayfanın bir kısmı çerçeve dışında.",
    },
    {
        src: "/passport-guide/bad-glare.jpg",
        good: false,
        title: "Yanlış",
        note: "Flaş parlaması bilgileri okunamaz hâle getiriyor.",
    },
    {
        src: "/passport-guide/bad-blur.jpg",
        good: false,
        title: "Yanlış",
        note: "Eğik ve bulanık; parmak alt satırları kapatıyor.",
    },
];

/** Pasaport taramasinda dogru/yanlis ornekleri gosterir. */
export const PassportGuide = ({ testId = "passport-guide" }) => (
    <div className="mt-3 rounded-xl border border-border bg-card p-4" data-testid={testId}>
        <p className="font-heading text-sm font-bold">Pasaport taraması nasıl olmalı?</p>
        <p className="mt-1 text-xs leading-5 text-muted-foreground">
            Kimlik sayfasını telefonla da çekebilirsiniz: pasaportu masaya düz koyun, dört köşe
            çerçevede olsun, flaş kullanmayın.
        </p>
        <div className="mt-3 grid grid-cols-2 gap-3">
            {EXAMPLES.map((ex) => (
                <figure
                    key={ex.src}
                    className="space-y-1.5"
                    data-testid={`${testId}-${ex.good ? "good" : "bad"}`}
                >
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
