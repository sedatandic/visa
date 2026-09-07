import React, { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

const SLIDES = [
    {
        src: "https://images.unsplash.com/photo-1580674684081-7617fbf3d745?auto=format&fit=crop&w=2000&q=80",
        alt: "Burj Khalifa ve Downtown Dubai silüeti",
        title: "Dubai vizeniz 2 iş gününde",
        text: "Başvurudan sonuca kadar süreci biz yürütüyoruz",
    },
    {
        src: "https://images.unsplash.com/photo-1546412414-e1885259563a?auto=format&fit=crop&w=2000&q=80",
        alt: "Burj Al Arab ve Jumeirah sahili",
        title: "Sadece pasaport ve fotoğraf",
        text: "Uçak bileti ve otel rezervasyonu şartı yok",
    },
    {
        src: "https://images.unsplash.com/photo-1524234599372-a5bd0194758d?auto=format&fit=crop&w=2000&q=80",
        alt: "Dubai Marina gökdelenleri",
        title: "Ekspres vize hizmeti",
        text: "Acil seyahatlerde 12 saat içinde sonuç",
    },
    {
        src: "https://images.unsplash.com/photo-1489516408517-0c0a15662682?auto=format&fit=crop&w=2000&q=80",
        alt: "Palm Jumeirah kuş bakışı",
        title: "Tüm aileniz tek başvuruda",
        text: "2-3 kişide %10, 4+ kişide %15 aile indirimi",
    },
    {
        src: "https://images.unsplash.com/photo-1582882198551-c0d7f863c5dd?auto=format&fit=crop&w=2000&q=80",
        alt: "Jumeirah sahilinde tekne",
        title: "eSIM, sigorta ve turlar",
        text: "Seyahat ekstralarınızı aynı sepette ekleyin",
    },
];

export const HeroBannerSlider = () => {
    const [index, setIndex] = useState(0);
    const [paused, setPaused] = useState(false);

    useEffect(() => {
        if (paused) return undefined;
        const timer = setInterval(() => setIndex((i) => (i + 1) % SLIDES.length), 5000);
        return () => clearInterval(timer);
    }, [paused]);

    const go = (dir) => setIndex((i) => (i + dir + SLIDES.length) % SLIDES.length);

    return (
        <div
            className="group relative w-full overflow-hidden bg-[hsl(var(--muted))]"
            onMouseEnter={() => setPaused(true)}
            onMouseLeave={() => setPaused(false)}
            data-testid="hero-banner-slider"
        >
            <div
                className="flex h-[220px] transition-transform duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] sm:h-[320px] lg:h-[400px]"
                style={{ transform: `translateX(-${index * 100}%)` }}
            >
                {SLIDES.map((s, i) => (
                    <div key={s.src} className="relative h-full w-full shrink-0" data-testid={`hero-banner-${i}`}>
                        <img
                            src={s.src}
                            alt={s.alt}
                            loading={i === 0 ? "eager" : "lazy"}
                            decoding="async"
                            className="absolute inset-0 h-full w-full object-cover object-center"
                        />
                        <div
                            className="absolute inset-0 bg-gradient-to-r from-black/70 via-black/35 to-transparent"
                            aria-hidden="true"
                        />
                        <div className="container-page relative flex h-full flex-col justify-center">
                            <p className="max-w-lg font-heading text-2xl font-extrabold text-white drop-shadow sm:text-4xl">
                                {s.title}
                            </p>
                            <p className="mt-2 max-w-md text-xs text-white/85 sm:text-base">{s.text}</p>
                        </div>
                    </div>
                ))}
            </div>

            <button
                type="button"
                onClick={() => go(-1)}
                aria-label="Önceki banner"
                className="absolute left-3 top-1/2 -translate-y-1/2 rounded-full bg-white/85 p-2 text-foreground opacity-70 transition-opacity duration-300 hover:bg-white sm:opacity-0 group-hover:sm:opacity-100"
                data-testid="hero-banner-prev"
            >
                <ChevronLeft className="h-4 w-4" />
            </button>
            <button
                type="button"
                onClick={() => go(1)}
                aria-label="Sonraki banner"
                className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full bg-white/85 p-2 text-foreground opacity-70 transition-opacity duration-300 hover:bg-white sm:opacity-0 group-hover:sm:opacity-100"
                data-testid="hero-banner-next"
            >
                <ChevronRight className="h-4 w-4" />
            </button>

            <div className="absolute bottom-4 left-1/2 flex -translate-x-1/2 items-center gap-1.5">
                {SLIDES.map((s, i) => (
                    <button
                        key={s.src}
                        type="button"
                        onClick={() => setIndex(i)}
                        aria-label={`${i + 1}. banner`}
                        className="h-2 rounded-full bg-white/55 transition-all duration-300 hover:bg-white"
                        style={i === index ? { width: 28, backgroundColor: "hsl(var(--gold))" } : { width: 8 }}
                        data-testid={`hero-banner-dot-${i}`}
                    />
                ))}
            </div>
        </div>
    );
};
