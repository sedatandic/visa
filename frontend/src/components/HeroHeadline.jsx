import React, { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

const SLOGANS = [
    { top: "Dubai vizeniz", bottom: "2 günde hazır" },
    { top: "Tüm aileniz", bottom: "tek formda, tek başvuruda" },
    { top: "Pasaportunuzu yükleyin", bottom: "gerisini biz hallederiz" },
];

export const HeroHeadline = () => {
    const [index, setIndex] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => setIndex((i) => (i + 1) % SLOGANS.length), 4200);
        return () => clearInterval(timer);
    }, []);

    const slogan = SLOGANS[index];

    return (
        <h1
            className="mt-6 min-h-[2.6em] font-heading text-4xl font-extrabold sm:text-5xl lg:text-[58px]"
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
    );
};
