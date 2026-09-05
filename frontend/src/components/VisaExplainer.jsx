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
        subtitle: "Dubai vizesi almak artık çok kolay. Başvurunuzu tamamlamak için yalnızca iki belgeye ihtiyacınız var.",
        alt: "Bavuluyla gülümseyen gezgin çizimi",
        silentMs: 6000,
        voiceMs: 7000,
    },
    {
        key: "passport",
        step: "1. belge",
        icon: IdCard,
        title: "Pasaportunuzun kimlik sayfası",
        note: "Kimlik bilgilerinizin bulunduğu sayfanın fotoğrafı",
        subtitle: "İlk olarak, pasaportunuzun kimlik bilgilerinin yer aldığı sayfanın fotoğrafını yükleyin.",
        alt: "Açık pasaport ve telefonla fotoğraflama çizimi",
        silentMs: 5000,
        voiceMs: 6700,
    },
    {
        key: "photo",
        step: "2. belge",
        icon: Camera,
        title: "Güncel bir vesikalık fotoğraf",
        note: "Beyaz fon, gözlüksüz ve şapkasız",
        subtitle:
            "Ardından beyaz fonda çekilmiş güncel bir vesikalık fotoğraf ekleyin. Fotoğrafın gözlüksüz ve şapkasız olması gerektiğini lütfen unutmayın.",
        alt: "Vesikalık fotoğraf ve üstü çizili gözlük şapka çizimi",
        silentMs: 8500,
        voiceMs: 8600,
    },
    {
        key: "upload",
        step: "Adım 2",
        icon: UploadCloud,
        title: "Yükleyin ve ödemeyi tamamlayın",
        note: "Uçak bileti veya otel rezervasyonu gerekmiyor",
        subtitle:
            "Belgelerinizi yükleyip ödemenizi tamamlamanız yeterli. Üstelik vizeniz onaylanmadan önce uçak bileti satın almanıza ya da otel rezervasyonu yaptırmanıza gerek yok.",
        alt: "Belgelerin bulut simgesine yüklendiği çizim",
        silentMs: 10000,
        voiceMs: 9700,
    },
    {
        key: "track",
        step: "Adım 3",
        icon: Headphones,
        title: "Süreci sizin adınıza biz takip ediyoruz",
        note: "Onaylanan vizeniz ortalama 2 iş gününde e-postanızda",
        subtitle:
            "Başvurunuzun tüm aşamalarını sizin adınıza takip ediyoruz. Onaylanan Dubai vizeniz ortalama iki iş günü içinde e-posta adresinize gönderilir.",
        alt: "Kulaklıklı danışman ve onay listesi çizimi",
        silentMs: 9000,
        voiceMs: 8900,
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
        voiceMs: 12700,
    },
    {
        key: "cta",
        step: "Son adım",
        icon: Plane,
        title: "Dubai Vize Online güvencesiyle başvurun",
        note: "TÜRSAB üyesi A Grubu seyahat acentesi güvencesi · Dubai sizi bekliyor",
        subtitle:
            "Dubai vizenizi Dubai Vize Online güvencesiyle kolayca alın. TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle başvurunuzu güvenle tamamlayın. Hemen başvurun ve Dubai yolculuğunuzun ilk adımını bugün atın. Dubai sizi bekliyor!",
        alt: "Dubai silüetine doğru havalanan uçak ve BAE bayrağı çizimi",
        silentMs: 12000,
        voiceMs: 16700,
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
    const [soundOn, setSoundOn] = useState(true);
    const [captions, setCaptions] = useState(true);
    const [audioProgress, setAudioProgress] = useState(0);
    const [audioMs, setAudioMs] = useState(0);
    const audioRef = useRef(null);
    const scene = SCENES[index];
    const SceneIcon = scene.icon;
    // Ses acikken tum zamanlama gercek klip suresinden gelir: konusma, altyazi,
    // ilerleme cubugu ve gorsel yakinlasma ayni anda biter.
    const sceneMs = soundOn ? audioMs || scene.voiceMs : scene.silentMs;

    useEffect(() => {
        if (paused || soundOn) return;
        const timer = setTimeout(() => setIndex((i) => (i + 1) % SCENES.length), scene.silentMs);
        return () => clearTimeout(timer);
    }, [index, paused, soundOn, scene.silentMs]);

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;
        if (!soundOn) {
            audio.pause();
            return;
        }
        audio.src = `/audio/explainer/${scene.key}.mp3`;
        if (paused) {
            audio.pause();
            return;
        }
        audio.currentTime = 0;
        setAudioProgress(0);
        setAudioMs(0);
        // Tarayici otomatik sesi engellerse ses acik kalir, ilk etkilesimde baslar.
        audio.play().catch(() => {});
    }, [scene.key, soundOn, paused]);

    // Tarayicilar sesli otomatik oynatmayi engeller: ilk kullanici etkilesiminde baslat.
    useEffect(() => {
        const start = () => {
            const audio = audioRef.current;
            if (audio && soundOn && !paused && audio.paused) audio.play().catch(() => {});
        };
        const events = ["pointerdown", "keydown", "touchstart", "wheel", "scroll"];
        events.forEach((e) => window.addEventListener(e, start, { once: true, passive: true }));
        return () => events.forEach((e) => window.removeEventListener(e, start));
    }, [soundOn, paused]);

    return (
        <div
            className="relative flex flex-col overflow-hidden rounded-[var(--radius-lg)] border border-border bg-[hsl(var(--panel-2))] sm:block"
            style={{ boxShadow: "var(--shadow-card)" }}
            data-testid="visa-explainer"
        >
            {/* CIZIM KATMANI */}
            <div className="relative order-2 h-44 w-full sm:absolute sm:inset-y-0 sm:right-0 sm:order-none sm:h-auto sm:w-[68%]">
                <AnimatePresence initial={false}>
                    <motion.img
                        key={scene.key}
                        src={`/explainer/${scene.key}.jpg`}
                        alt={scene.alt}
                        initial={{ opacity: 0, scale: 1.04, x: 30 }}
                        animate={{ opacity: 1, scale: paused ? 1.01 : 1.06, x: 0 }}
                        exit={{ opacity: 0, x: -24 }}
                        transition={{
                            opacity: { duration: 0.6 },
                            x: { duration: 0.7, ease: "easeOut" },
                            scale: { duration: paused ? 0.4 : sceneMs / 1000, ease: "linear" },
                        }}
                        className="absolute inset-0 h-full w-full object-cover object-center sm:object-right"
                        data-testid={`explainer-image-${scene.key}`}
                    />
                </AnimatePresence>
                <div
                    className="absolute inset-0 hidden bg-gradient-to-r from-[hsl(var(--panel-2))] via-[hsl(var(--panel-2)/0.35)] to-transparent sm:block"
                    aria-hidden="true"
                />
            </div>

            {/* METIN KATMANI */}
            <div className="relative order-1 flex flex-col justify-between gap-5 p-6 sm:order-none sm:min-h-[400px] sm:gap-6 sm:p-9">
                <div className="max-w-md">
                    <span className="inline-flex items-center gap-2 rounded-full border border-primary/25 bg-white/80 px-3.5 py-1.5 text-[10px] font-bold uppercase tracking-[0.12em] text-primary sm:text-[11px]">
                        Dubai vizenizi 1 dakikada nasıl alacağınızı anlatalım
                    </span>
                    <p className="mt-3 font-heading text-2xl font-extrabold leading-tight sm:text-3xl">
                        Sadece 2 belgeyle Dubai vizesi
                    </p>
                </div>

                <div className="max-w-lg">
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
                                <Button asChild size="lg" className="mt-4" data-testid="explainer-cta-button">
                                    <Link to="/basvuru">
                                        Başvuruya başla <ArrowRight className="ml-1 h-4 w-4" />
                                    </Link>
                                </Button>
                            )}
                        </motion.div>
                    </AnimatePresence>

                    {captions && (
                        <div className="mt-4 max-w-xl">
                            <Subtitle
                                text={scene.subtitle}
                                durationMs={sceneMs}
                                paused={paused}
                                sceneKey={scene.key}
                                progress={soundOn ? audioProgress : null}
                            />
                        </div>
                    )}

                    <div className="mt-5 flex flex-wrap items-center gap-3">
                        <div className="flex min-w-[140px] flex-1 gap-1.5 sm:max-w-[240px]">
                            {SCENES.map((s, i) => (
                                <button
                                    key={s.key}
                                    type="button"
                                    onClick={() => setIndex(i)}
                                    aria-label={`${s.step}: ${s.title}`}
                                    className="h-1.5 flex-1 overflow-hidden rounded-full bg-foreground/15"
                                    data-testid={`explainer-dot-${s.key}`}
                                >
                                    <motion.span
                                        key={`${s.key}-${index}-${paused}-${soundOn}-${sceneMs}`}
                                        initial={{ width: i < index ? "100%" : "0%" }}
                                        animate={{ width: i <= index ? "100%" : "0%" }}
                                        transition={{
                                            duration: i === index && !paused ? sceneMs / 1000 : 0,
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
                preload="none"
                onLoadedMetadata={(e) => {
                    const d = e.currentTarget.duration;
                    if (d && Number.isFinite(d)) setAudioMs(Math.round(d * 1000));
                }}
                onTimeUpdate={(e) => {
                    const el = e.currentTarget;
                    if (el.duration) setAudioProgress(el.currentTime / el.duration);
                }}
                onEnded={() => {
                    // Sesli anlatim bir kez calisir: son sahnede ses kapanir, gorsel dongu devam eder.
                    if (index === SCENES.length - 1) {
                        setSoundOn(false);
                        return;
                    }
                    setIndex((i) => i + 1);
                }}
                data-testid="explainer-audio"
            />
        </div>
    );
};
