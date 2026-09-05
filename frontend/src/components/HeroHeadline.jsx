import React, { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

const SLOGANS = [
    {
        top: "Sadece 2 belgeyle",
        bottom: "Dubai vizeniz hazır",
        sub: "Başvurunuz için yalnızca pasaportunuzun kimlik sayfası ve vesikalık fotoğrafınız yeterlidir. Belgelerinizi yükledikten sonra sürecin tamamını uzman ekibimiz sizin adınıza yönetir.",
    },
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
        bottom: "gerisini biz yönetelim",
        sub: "Siz sadece belgelerinizi yükleyin, vize sürecinizi biz yönetelim. Uçak bileti veya otel rezervasyonu istemiyoruz; resmî başvuruyu yetkili merciler nezdinde biz yaparız.",
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
                className="mt-6 min-h-[2.2em] font-heading text-4xl font-extrabold sm:text-5xl lg:text-[58px]"
                style={{ perspective: "900px" }}
                data-testid="hero-headline"
            >
                <AnimatePresence mode="wait">
                    <motion.span
                        key={index}
                        initial={{ opacity: 0, rotateX: -75, y: 14 }}
                        animate={{ opacity: 1, rotateX: 0, y: 0 }}
                        exit={{ opacity: 0, rotateX: 70, y: -14 }}
                        transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
                        className="block"
                        style={{ transformOrigin: "center bottom" }}
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

            <div className="mx-auto mt-7 min-h-[4.5em] max-w-2xl sm:min-h-[3.4em]">
                <AnimatePresence mode="wait">
                    <motion.p
                        key={`sub-${index}`}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.4, ease: "easeOut", delay: 0.06 }}
                        className="text-base leading-7 text-muted-foreground sm:text-lg"
                        data-testid={`hero-subtitle-${index}`}
                    >
                        {slogan.sub}
                    </motion.p>
                </AnimatePresence>
            </div>

            {/* Sloganlarin altinda ilerleme cizgileri (anlatim panelindeki gibi) */}
            <div className="mx-auto mt-5 flex max-w-[260px] items-center gap-1.5" data-testid="hero-progress">
                {SLOGANS.map((s, i) => (
                    <button
                        key={s.top}
                        type="button"
                        onClick={() => setIndex(i)}
                        aria-label={`${i + 1}. başlık: ${s.top} ${s.bottom}`}
                        className="h-1.5 flex-1 overflow-hidden rounded-full bg-foreground/15 transition-colors duration-200 hover:bg-foreground/25"
                        data-testid={`hero-progress-dot-${i}`}
                    >
                        <motion.span
                            key={`${i}-${index}`}
                            initial={{ width: i < index ? "100%" : "0%" }}
                            animate={{ width: i <= index ? "100%" : "0%" }}
                            transition={{ duration: i === index ? 4.2 : 0, ease: "linear" }}
                            className="block h-full bg-primary"
                        />
                    </button>
                ))}
            </div>
        </>
    );
};
