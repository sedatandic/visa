import React, { useCallback, useEffect, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

const SLIDES = [
    {
        src: "https://images.unsplash.com/photo-1546412414-e1885259563a?auto=format&fit=crop&w=1600&q=80",
        alt: "Burj Al Arab gündüz, turkuaz deniz kenarında",
        caption: "Burj Al Arab · Jumeirah",
    },
    {
        src: "https://images.unsplash.com/photo-1489516408517-0c0a15662682?auto=format&fit=crop&w=1600&q=80",
        alt: "Palm Jumeirah'ın kuş bakışı turkuaz görüntüsü",
        caption: "Palm Jumeirah · Kuş bakışı",
    },
    {
        src: "https://images.unsplash.com/photo-1524234599372-a5bd0194758d?auto=format&fit=crop&w=1600&q=80",
        alt: "Dubai Marina gökdelenleri ve havuz, açık mavi gökyüzü",
        caption: "Dubai Marina · Gündüz",
    },
    {
        src: "https://images.unsplash.com/photo-1582882198551-c0d7f863c5dd?auto=format&fit=crop&w=1600&q=80",
        alt: "Jumeirah sahilinde tekne ve turkuaz deniz",
        caption: "Jumeirah sahili · Turkuaz",
    },
    {
        src: "https://images.unsplash.com/photo-1580674684081-7617fbf3d745?auto=format&fit=crop&w=1600&q=80",
        alt: "Burj Khalifa ve Downtown Dubai, palmiyeler ve mavi gökyüzü",
        caption: "Downtown Dubai · Burj Khalifa",
    },
];

export const HeroSlider = () => {
    const [index, setIndex] = useState(0);
    const [paused, setPaused] = useState(false);

    const go = useCallback((dir) => {
        setIndex((i) => (i + dir + SLIDES.length) % SLIDES.length);
    }, []);

    useEffect(() => {
        if (paused) return undefined;
        const t = setInterval(() => setIndex((i) => (i + 1) % SLIDES.length), 4500);
        return () => clearInterval(t);
    }, [paused]);

    return (
        <div
            className="group relative overflow-hidden rounded-[var(--radius-lg)] border border-white/60 bg-[hsl(var(--muted))]"
            onMouseEnter={() => setPaused(true)}
            onMouseLeave={() => setPaused(false)}
            data-testid="hero-slider"
        >
            <div className="relative h-[240px] sm:h-[340px] lg:h-[420px]">
                {SLIDES.map((s, i) => (
                    <img
                        key={s.src}
                        src={s.src}
                        alt={s.alt}
                        className="absolute inset-0 h-full w-full object-cover object-center transition-opacity duration-1000 ease-out"
                        style={{ opacity: i === index ? 1 : 0 }}
                        loading={i === 0 ? "eager" : "lazy"}
                        decoding="async"
                        data-testid={`hero-slide-${i}`}
                    />
                ))}

                <div
                    className="pointer-events-none absolute inset-x-0 bottom-0 h-1/2"
                    style={{ background: "linear-gradient(180deg, transparent, hsl(215 30% 18% / 0.45))" }}
                    aria-hidden="true"
                />

                <span
                    className="absolute bottom-4 left-4 rounded-full bg-black/25 px-3.5 py-1.5 text-xs font-bold text-white backdrop-blur-sm sm:bottom-5 sm:left-6 sm:text-sm"
                    data-testid="hero-slide-caption"
                >
                    {SLIDES[index].caption}
                </span>

                <button
                    type="button"
                    onClick={() => go(-1)}
                    aria-label="Önceki görsel"
                    data-testid="hero-slider-prev"
                    className="absolute left-3 top-1/2 -translate-y-1/2 rounded-full bg-white/85 p-2 text-foreground opacity-70 shadow-sm transition-opacity duration-300 hover:bg-white sm:opacity-0 group-hover:sm:opacity-100 focus-visible:opacity-100"
                >
                    <ChevronLeft className="h-4.5 w-4.5" />
                </button>
                <button
                    type="button"
                    onClick={() => go(1)}
                    aria-label="Sonraki görsel"
                    data-testid="hero-slider-next"
                    className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full bg-white/85 p-2 text-foreground opacity-70 shadow-sm transition-opacity duration-300 hover:bg-white sm:opacity-0 group-hover:sm:opacity-100 focus-visible:opacity-100"
                >
                    <ChevronRight className="h-4.5 w-4.5" />
                </button>

                <div className="absolute bottom-4 right-4 flex items-center gap-1.5 sm:bottom-5 sm:right-6">
                    {SLIDES.map((s, i) => (
                        <button
                            key={s.src}
                            type="button"
                            onClick={() => setIndex(i)}
                            aria-label={`${i + 1}. görsele git`}
                            data-testid={`hero-slider-dot-${i}`}
                            className="h-2 rounded-full bg-white/60 transition-all duration-300 hover:bg-white"
                            style={
                                i === index
                                    ? { width: 26, backgroundColor: "hsl(var(--gold))" }
                                    : { width: 8 }
                            }
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};
