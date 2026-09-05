import React, { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

const SLOGANS = [
    {
        top: "Bilet ve otel şartı yok",
        bottom: "sadece pasaport ve fotoğraf",
        sub: "Vizeniz çıkmadan uçak bileti ve otel rezervasyonu yapmanıza gerek yok. Pasaportunuzun kimlik sayfası ve bir vesikalık fotoğrafla başvurunuzu tamamlıyoruz.",
    },
    {
        top: "Dubai vizeniz",
        bottom: "2 iş gününde hazır",
        sub: "Dubai seyahatiniz için vize başvurunuzu tamamen online tamamlayın. Evraklarınızı yükleyin, başvurunuzu gönderin ve sonucunuzu e-posta ile alın.",
    },
    {
        top: "Tüm aileniz",
        bottom: "tek formda, tek başvuruda",
        sub: "Eşinizi ve çocuklarınızı aynı forma ekleyin. 2 kişiden itibaren %10 aile indirimi otomatik uygulanır, çocuk vizeleri indirimli fiyatlanır.",
    },
    {
        top: "Pasaportunuzu yükleyin",
        bottom: "gerisini biz halledelim",
        sub: "Pasaportunuzun fotoğrafını ve vesikalığınızı yükleyin; uçak bileti veya otel rezervasyonu istemiyoruz. Resmî başvuruyu yetkili merciler nezdinde biz yaparız.",
    },
];

export const HeroHeadline = () => {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => setIndex((i) => (i + 1) % SLOGANS.length), 4200);
        return () => clearInterval(timer);
    }, []);

    const slogan = SLOGANS[index];

    return (
        <>
            <h1
                className="mt-6 min-h-[2.2em] overflow-hidden font-heading text-4xl font-extrabold sm:text-5xl lg:text-[58px]"
                data-testid="hero-headline"
            >
                <AnimatePresence mode="wait">
                    <motion.span
                        key={index}
                        initial={{ opacity: 0, x: 120 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -120 }}
                        transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}
                        className="block"
                        data-testid={`hero-slogan-${index}`}
                    >
                        <span className="display-italic" style={{ color: "hsl(38 82% 46%)" }}>
                            {slogan.top}
                        </span>
                        <br />
                        <span style={{ color: "hsl(30 62% 38%)" }}>{slogan.bottom}</span>
                    </motion.span>
                </AnimatePresence>
            </h1>

            <div className="mx-auto mt-7 min-h-[4.5em] max-w-2xl overflow-hidden sm:min-h-[3.4em]">
                <AnimatePresence mode="wait">
                    <motion.p
                        key={`sub-${index}`}
                        initial={{ opacity: 0, x: 90 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -90 }}
                        transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1], delay: 0.08 }}
                        className="text-base leading-7 text-muted-foreground sm:text-lg"
                        data-testid={`hero-subtitle-${index}`}
                    >
                        {slogan.sub}
                    </motion.p>
                </AnimatePresence>
            </div>
        </>
    );
};
