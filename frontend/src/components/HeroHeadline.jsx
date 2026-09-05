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
        sub: "Siz sadece belgelerinizi yükleyin, vize sürecinizi biz yöneteceğiz. Uçak bileti veya otel rezervasyonu istemiyoruz; resmî başvuruyu yetkili merciler nezdinde biz yaparız.",
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
        </>
    );
};
