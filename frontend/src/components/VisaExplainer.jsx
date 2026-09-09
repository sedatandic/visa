import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
    ArrowRight,
    BadgeCheck,
    Camera,
    Captions,
    Headphones,
    IdCard,
    Pause,
    Play,
    Plane,
    UploadCloud,
    Volume2,
    VolumeX,
    Wifi,
} from "lucide-react";
import { Button } from "./ui/button";

const SCENES = [
    {
        key: "intro",
        step: "Adım 1",
        icon: BadgeCheck,
        title: "Dubai vizesi almak artık çok kolay",
        note: "Başvurunuz için sadece iki belge yeterli",
        subtitle: "Dubai vizesi almak artık çok kolay. Başvurunuzu yapmak için yalnızca iki belgeye ihtiyacınız var.",
        alt: "Bavuluyla gülümseyen gezgin çizimi",
        silentMs: 6000,
        voiceMs: 7340,
    },
    {
        key: "passport",
        step: "1. belge",
        icon: IdCard,
        title: "Pasaportunuzun kimlik sayfası",
        note: "Kimlik bilgilerinizin bulunduğu sayfanın fotoğrafı",
        subtitle: "İlk olarak, pasaportunuzun kimlik bilgilerinin yer aldığı sayfanın fotoğrafını yükleyin.",
        alt: "Türk pasaportu, kimlik sayfası ve telefonla fotoğraflama çizimi",
        silentMs: 5000,
        voiceMs: 5070,
    },
    {
        key: "photo",
        step: "2. belge",
        icon: Camera,
        title: "Güncel bir vesikalık fotoğraf",
        note: "Beyaz fon, gözlüksüz ve şapkasız",
        subtitle:
            "Ardından beyaz fonda çekilmiş güncel bir vesikalık fotoğraf ekleyin. Fotoğrafınızın gözlüksüz ve şapkasız olması gerekmektedir.",
        alt: "Yan yana iki vesikalık fotoğraf ve üstü çizili gözlük şapka çizimi",
        silentMs: 8500,
        voiceMs: 8300,
    },
    {
        key: "upload",
        step: "Adım 2",
        icon: UploadCloud,
        title: "Yükleyin ve ödemeyi tamamlayın",
        note: "Uçak bileti veya otel rezervasyonu gerekmiyor",
        subtitle:
            "Belgelerinizi yükleyip ödemenizi yapmanız yeterlidir. Üstelik Dubai vizeniz onaylanmadan önce uçak bileti ya da otel rezervasyonu yaptırmanıza da gerek yoktur.",
        alt: "Belgelerin bulut simgesine yüklendiği çizim",
        silentMs: 10000,
        voiceMs: 9880,
    },
    {
        key: "track",
        step: "Adım 3",
        icon: Headphones,
        title: "Süreci sizin adınıza biz takip ediyoruz",
        note: "Onaylanan vizeniz 36 saatte e-mail ve WhatsApp'ınızda",
        subtitle:
            "Başvurunuzun tüm aşamalarını sizin adınıza biz takip ediyor ve onaylanan Dubai vizenizi 36 saat içinde e-mail adresinize ve WhatsApp ile gönderiyoruz.",
        alt: "Kulaklıklı danışman ve onay listesi çizimi",
        silentMs: 9000,
        voiceMs: 9610,
    },
    {
        key: "extras",
        step: "Ekstra",
        icon: Wifi,
        title: "Seyahat sigortası ve Dubai eSIM",
        note: "Aynı başvuruya ekleyin, iniş anında internet ve teminat hazır",
        subtitle:
            "Dilerseniz seyahat sigortanızı ve Dubai eSIM'inizi de başvurunuza ekleyebilirsiniz. Böylece Dubai'ye vardığınız anda internet bağlantınız hazır olur ve seyahat sigortanız anında devreye girer.",
        alt: "eSIM ve seyahat sigortası simgeleri çizimi",
        silentMs: 11000,
        voiceMs: 12160,
    },
    {
        key: "cta",
        step: "Son adım",
        icon: Plane,
        title: "Dubai Vize Hattı ile güvenle başvurun",
        note: "TÜRSAB üyesi A Grubu seyahat acentesi güvencesi · Dubai sizi bekliyor",
        subtitle:
            "Vizenizi Dubai Vize Hattı ile kolayca alın. TÜRSAB üyesi A grubu seyahat acentesi iş birliğiyle başvurunuzu baştan sona biz yürütüyoruz. Formu doldurun, gerisini bize bırakın. Dubai sizi bekliyor!",
        alt: "Dubai silüetine doğru havalanan uçak ve BAE bayrağı çizimi",
        silentMs: 12000,
        voiceMs: 13340,
        cta: true,
    },
];

const Subtitle = ({ text, durationMs, paused, sceneKey, progress }) => {
    const words = text.split(" ");
    const step = Math.max(0.1, durationMs / 1000 / (words.length + 2));
    const spoken = progress === null ? -1 : Math.round(progress * words.length);
    return (
        <p
            className="rounded-xl bg-white/85 px-4 py-2.5 text-xs font-medium leading-5 text-foreground shadow-sm backdrop-blur-sm sm:text-sm sm:leading-6"
            data-testid="explainer-subtitle"
        >
            {words.map((word, i) => (
                <motion.span
                    key={`${sceneKey}-${i}`}
                    initial={{ opacity: 0.3 }}
                    animate={{ opacity: progress === null ? 1 : i < spoken ? 1 : 0.35 }}
                    transition={
                        progress === null ? { delay: paused ? 0 : i * step, duration: 0.25 } : { duration: 0.18 }
                    }
                    className="mr-1 inline-block"
                >
                    {word}
                </motion.span>
            ))}
        </p>
    );
};

export const VisaExplainer = () => {
    const [index, setIndex] = useState(0);
    const [paused, setPaused] = useState(false);
    // Sayfa acilisinda anlatim durur: kapak karesi gorunur, kullanici baslatir.
    const [started, setStarted] = useState(false);
    const [soundOn, setSoundOn] = useState(false);
    const [captions, setCaptions] = useState(true);
    const [audioProgress, setAudioProgress] = useState(0);
    const [timeline, setTimeline] = useState(null);
    const [playing, setPlaying] = useState(false);
    const audioRef = useRef(null);
    const scene = SCENES[index];
    const SceneIcon = scene.icon;
    // Anlatim TEK parca mp3: sahne pencereleri full.json'dan gelir (klip gecisi yok,
    // duraksama olmaz). Ses acikken zamanlama bu pencerelerden hesaplanir.
    const window_ = timeline?.[index];
    const sceneMs = soundOn
        ? window_
            ? Math.round((window_.end - window_.start) * 1000)
            : scene.voiceMs
        : scene.silentMs;

    useEffect(() => {
        fetch("/audio/explainer/full.json")
            .then((r) => r.json())
            .then((d) => setTimeline(d.scenes))
            .catch(() => {});
    }, []);

    useEffect(() => {
        if (!started || paused || soundOn) return;
        const timer = setTimeout(() => setIndex((i) => (i + 1) % SCENES.length), scene.silentMs);
        return () => clearTimeout(timer);
    }, [index, started, paused, soundOn, scene.silentMs]);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;
        if (!started || !soundOn || paused) {
            audio.pause();
            return;
        }
        audio.play().catch(() => {});
    }, [started, soundOn, paused]);

    // Sahneye atlar; ses acikken tek parca kaydin ilgili saniyesine konumlanir.
    const goToScene = (i) => {
        setIndex(i);
        const audio = audioRef.current;
        if (audio && timeline?.[i]) audio.currentTime = timeline[i].start;
    };

    // Kapaktaki tek dokunusla anlatimi bastan baslatir (autoplay engelini asar).
    const startNarration = () => {
        const audio = audioRef.current;
        setStarted(true);
        setSoundOn(true);
        setPaused(false);
        setIndex(0);
        if (!audio) return;
        audio.currentTime = 0;
        audio.play().catch(() => {});
    };

    return (
        <div
            className="relative flex flex-col overflow-hidden rounded-[var(--radius-lg)] border border-border bg-[hsl(var(--panel-2))] sm:grid sm:grid-cols-[46%_54%] sm:items-center"
            style={{ boxShadow: "var(--shadow-card)" }}
            data-testid="visa-explainer"
        >
            {/* CIZIM KATMANI */}
            <div className="relative order-1 aspect-[3/2] w-full overflow-hidden sm:order-2 sm:aspect-auto sm:h-[386px] sm:w-full">
                <AnimatePresence initial={false}>
                    <motion.img
                        key={scene.key}
                        src={`/explainer/${scene.key}.png`}
                        alt={scene.alt}
                        decoding="async"
                        initial={{ opacity: 0, scale: 1.0, x: 30 }}
                        animate={{ opacity: 1, scale: paused || !started ? 1.0 : 1.03, x: 0 }}
                        exit={{ opacity: 0, x: -24 }}
                        transition={{
                            opacity: { duration: 0.6 },
                            x: { duration: 0.7, ease: "easeOut" },
                            scale: { duration: paused ? 0.4 : sceneMs / 1000, ease: "linear" },
                        }}
                        className="absolute inset-0 h-full w-full object-contain object-center p-1.5 sm:p-2 sm:pr-8"
                        data-testid={`explainer-image-${scene.key}`}
                    />
                </AnimatePresence>

                {/* KAPAK KARESI: sayfa acilisinda hareket ve ses yok */}
                {!started && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.4 }}
                        className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 bg-[hsl(var(--panel-2))]/35 backdrop-blur-[1px]"
                        data-testid="explainer-cover"
                    >
                        <button
                            type="button"
                            onClick={startNarration}
                            aria-label="Anlatımı başlat"
                            className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-xl transition-transform duration-200 hover:scale-105 active:scale-95"
                            data-testid="explainer-cover-play-button"
                        >
                            <Play className="ml-0.5 h-6 w-6 fill-current" aria-hidden="true" />
                        </button>
                        <span className="rounded-full bg-white/90 px-3.5 py-1.5 text-[11px] font-bold text-foreground shadow-sm">
                            Anlatımı başlat · 1 dakika
                        </span>
                    </motion.div>
                )}
            </div>

            {/* METIN KATMANI */}
            <div className="relative order-2 flex flex-col gap-3 p-5 pt-2 sm:order-1 sm:min-h-[420px] sm:justify-center sm:gap-4 sm:p-6">
                {started && !playing && (
                    <button
                        type="button"
                        onClick={startNarration}
                        className="-mt-1 flex w-full items-center justify-center gap-2.5 rounded-full bg-primary px-5 py-4 text-sm font-bold text-primary-foreground shadow-lg transition-transform duration-200 active:scale-[0.97] sm:hidden"
                        data-testid="explainer-listen-button"
                    >
                        <Headphones className="h-4.5 w-4.5" aria-hidden="true" />
                        Anlatımı dinle · 1 dakika
                    </button>
                )}
                <div className="max-w-md">
                    <span className="inline-flex items-center gap-2 rounded-full border border-primary/25 bg-white/80 px-3.5 py-1.5 text-[10px] font-bold uppercase tracking-[0.12em] text-primary sm:text-[11px]">
                        Dubai vizenizi nasıl alacağınızı kısaca anlatalım
                    </span>
                </div>

                <div className="max-w-[420px]">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={scene.key}
                            initial={{ opacity: 0, y: 18 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -12 }}
                            transition={{ duration: 0.4 }}
                        >
                            <div className="flex items-start gap-3">
                                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/12 text-primary">
                                    <SceneIcon className="h-5 w-5" aria-hidden="true" />
                                </span>
                                <div>
                                    <span className="text-[10px] font-bold uppercase tracking-[0.14em] text-primary">
                                        {scene.step}
                                    </span>
                                    <p
                                        className="font-heading text-base font-bold leading-snug sm:text-lg"
                                        data-testid="explainer-scene-title"
                                    >
                                        {scene.title}
                                    </p>
                                    <p className="mt-1 text-xs leading-5 text-muted-foreground sm:text-sm">
                                        {scene.note}
                                    </p>
                                </div>
                            </div>

                            {scene.cta && (
                                <div className="mt-4 flex flex-wrap items-center gap-2.5">
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        transition={{ delay: 0.35, duration: 0.4 }}
                                        className="flex min-w-0 items-center gap-2 rounded-xl border border-primary/25 bg-white/90 px-2.5 py-1.5 shadow-sm"
                                        data-testid="explainer-tursab-seal"
                                    >
                                        <img
                                            src="/brand/tursab.png"
                                            alt="TÜRSAB - Türkiye Seyahat Acentaları Birliği"
                                            className="h-6 w-auto object-contain"
                                            decoding="async"
                                        />
                                        <span className="border-l border-border pl-2 text-[9px] font-bold uppercase leading-3 tracking-[0.04em] text-foreground">
                                            TÜRSAB üyesi
                                            <span className="mt-0.5 block text-[9px] font-semibold normal-case tracking-normal text-muted-foreground">
                                                A Grubu seyahat acentesi
                                            </span>
                                        </span>
                                    </motion.div>
                                    <Button asChild size="sm" className="shrink-0" data-testid="explainer-cta-button">
                                        <Link to="/basvuru">
                                            Başvuruya başla <ArrowRight className="ml-1 h-4 w-4" />
                                        </Link>
                                    </Button>
                                </div>
                            )}
                        </motion.div>
                    </AnimatePresence>

                    {captions && (
                        <div className="mt-3 max-w-[420px]">
                            <Subtitle
                                text={scene.subtitle}
                                durationMs={sceneMs}
                                paused={paused || !started}
                                sceneKey={scene.key}
                                progress={soundOn ? audioProgress : null}
                            />
                        </div>
                    )}

                    <div className="mt-4 flex flex-wrap items-center gap-2.5">
                        <div className="flex min-w-[140px] flex-1 gap-1.5 sm:max-w-[240px]">
                            {SCENES.map((s, i) => (
                                <button
                                    key={s.key}
                                    type="button"
                                    onClick={() => goToScene(i)}
                                    aria-label={`${s.step}: ${s.title}`}
                                    className="h-1.5 flex-1 overflow-hidden rounded-full bg-foreground/15"
                                    data-testid={`explainer-dot-${s.key}`}
                                >
                                    <motion.span
                                        key={`${s.key}-${index}-${paused}-${soundOn}-${sceneMs}`}
                                        initial={{ width: i < index ? "100%" : "0%" }}
                                        animate={{ width: i <= index ? "100%" : "0%" }}
                                        transition={{
                                            duration: i === index && started && !paused ? sceneMs / 1000 : 0,
                                            ease: "linear",
                                        }}
                                        className="block h-full bg-primary"
                                    />
                                </button>
                            ))}
                        </div>
                        <button
                            type="button"
                            onClick={() => setSoundOn((s) => !s)}
                            aria-label={soundOn ? "Sesi kapat" : "Sesli anlatımı aç"}
                            className={`flex h-9 items-center gap-1.5 rounded-full border px-3.5 text-xs font-semibold transition-colors duration-200 ${
                                soundOn
                                    ? "border-primary bg-primary text-primary-foreground"
                                    : "border-border bg-white/85 text-foreground hover:border-primary/60"
                            }`}
                            data-testid="explainer-sound-button"
                        >
                            {soundOn ? <Volume2 className="h-3.5 w-3.5" /> : <VolumeX className="h-3.5 w-3.5" />}
                            {soundOn ? "Ses açık" : "Sesli anlat"}
                        </button>
                        <button
                            type="button"
                            onClick={() => setCaptions((c) => !c)}
                            aria-label={captions ? "Altyazıyı kapat" : "Altyazıyı aç"}
                            className={`flex h-9 items-center gap-1.5 rounded-full border px-3 text-xs font-bold transition-colors duration-200 ${
                                captions
                                    ? "border-primary bg-primary text-primary-foreground"
                                    : "border-border bg-white/85 text-foreground hover:border-primary/60"
                            }`}
                            data-testid="explainer-captions-button"
                        >
                            <Captions className="h-3.5 w-3.5" /> CC
                        </button>
                        <button
                            type="button"
                            onClick={() => setPaused((p) => !p)}
                            aria-label={paused ? "Anlatımı oynat" : "Anlatımı duraklat"}
                            className="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-white/85 text-foreground transition-colors duration-200 hover:border-primary/60"
                            data-testid="explainer-toggle-button"
                        >
                            {paused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
                        </button>
                    </div>
                </div>
            </div>

            <audio
                ref={audioRef}
                src="/audio/explainer/full.mp3"
                preload="auto"
                onTimeUpdate={(e) => {
                    const t = e.currentTarget.currentTime;
                    if (!timeline) return;
                    const i = timeline.findIndex((w) => t >= w.start && t < w.end);
                    if (i >= 0 && i !== index) setIndex(i);
                    const w = timeline[i >= 0 ? i : index];
                    if (w) setAudioProgress(Math.min(1, Math.max(0, (t - w.start) / (w.end - w.start))));
                }}
                onPlay={() => setPlaying(true)}
                onPause={() => setPlaying(false)}
                onEnded={() => {
                    // Anlatim bir kez calisir: bitince kapak karesine donulur.
                    setSoundOn(false);
                    setStarted(false);
                    setIndex(0);
                }}
                data-testid="explainer-audio"
            />
        </div>
    );
};
