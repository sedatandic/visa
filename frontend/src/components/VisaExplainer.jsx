import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Camera, Captions, CheckCircle2, IdCard, MailCheck, Pause, Play, UploadCloud, Volume2, VolumeX } from "lucide-react";

const SILENT_MS = 5000;
const VOICE_MS = 8500;

const SCENES = [
    {
        key: "passport",
        step: "1",
        icon: IdCard,
        title: "Pasaportunuzun kimlik sayfası",
        note: "Telefonunuzla çektiğiniz net bir fotoğraf yeterli",
        subtitle:
            "Dubai vizesi için sadece iki belge yeterli. Birincisi, pasaportunuzun kimlik sayfasının fotoğrafı.",
        alt: "Telefonla pasaportun kimlik sayfası fotoğraflanıyor",
    },
    {
        key: "photo",
        step: "2",
        icon: Camera,
        title: "Bir vesikalık fotoğraf",
        note: "Beyaz fon, son 6 ay içinde çekilmiş, gözlüksüz",
        subtitle:
            "İkincisi, beyaz fonda çekilmiş bir vesikalık fotoğraf. Gözlüksüz ve şapkasız olması gerekiyor.",
        alt: "Beyaz fonlu biyometrik vesikalık fotoğraf ve pasaport",
    },
    {
        key: "upload",
        step: "3",
        icon: UploadCloud,
        title: "Yükleyin ve ödemeyi yapın",
        note: "Uçak bileti ve otel rezervasyonu şartı yok",
        subtitle:
            "Belgeleri yükleyip ödemenizi yapın. Vizeniz çıkmadan uçak bileti ya da otel rezervasyonu gerekmiyor.",
        alt: "Belgeler bilgisayardan yükleniyor",
    },
    {
        key: "delivered",
        step: "4",
        icon: MailCheck,
        title: "Vizeniz e-postanıza gelir",
        note: "Ortalama 2 iş günü · ekspreste ~8 mesai saati",
        subtitle:
            "Başvurunuzu biz takip ediyoruz. Onaylanan vizeniz ortalama iki iş gününde e-postanıza geliyor.",
        alt: "Onaylı Dubai vizesini telefonunda gösteren gezgin",
    },
];

const Subtitle = ({ text, durationMs, paused, sceneKey }) => {
    const words = text.split(" ");
    const step = Math.max(0.12, durationMs / 1000 / (words.length + 2));
    return (
        <p
            className="mx-auto max-w-2xl rounded-xl bg-black/45 px-4 py-2.5 text-center text-xs font-medium leading-5 text-white backdrop-blur-sm sm:text-sm sm:leading-6"
            data-testid="explainer-subtitle"
        >
            {words.map((word, i) => (
                <motion.span
                    key={`${sceneKey}-${i}`}
                    initial={{ opacity: 0.28 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: paused ? 0 : i * step, duration: 0.25 }}
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
    const [soundOn, setSoundOn] = useState(false);
    const [captions, setCaptions] = useState(true);
    const audioRef = useRef(null);
    const scene = SCENES[index];
    const SceneIcon = scene.icon;
    const sceneMs = soundOn ? VOICE_MS : SILENT_MS;

    // Sessiz modda sahneler 5 sn'de gecer; ses acikken anlatim bitince gecer.
    useEffect(() => {
        if (paused || soundOn) return;
        const timer = setTimeout(() => setIndex((i) => (i + 1) % SCENES.length), SILENT_MS);
        return () => clearTimeout(timer);
    }, [index, paused, soundOn]);

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
        audio.play().catch(() => setSoundOn(false));
    }, [scene.key, soundOn, paused]);

    return (
        <div
            className="relative aspect-[16/10] w-full overflow-hidden rounded-[var(--radius-lg)] border border-border bg-[hsl(var(--charcoal))] sm:aspect-[16/9] lg:aspect-[21/9]"
            style={{ boxShadow: "var(--shadow-float)" }}
            data-testid="visa-explainer"
        >
            {/* GORUNTU KATMANI: Ken Burns yakinlasmasi + capraz gecis */}
            <AnimatePresence initial={false}>
                <motion.img
                    key={scene.key}
                    src={`/explainer/${scene.key}.jpg`}
                    alt={scene.alt}
                    initial={{ opacity: 0, scale: 1.02 }}
                    animate={{ opacity: 1, scale: paused ? 1.04 : 1.12 }}
                    exit={{ opacity: 0 }}
                    transition={{
                        opacity: { duration: 0.8 },
                        scale: { duration: paused ? 0.6 : sceneMs / 1000, ease: "linear" },
                    }}
                    className="absolute inset-0 h-full w-full object-cover"
                    data-testid={`explainer-image-${scene.key}`}
                />
            </AnimatePresence>

            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/45 to-black/25" aria-hidden="true" />

            {/* UST BILGI */}
            <div className="absolute left-5 right-5 top-5 flex flex-wrap items-center justify-between gap-3 sm:left-8 sm:right-8 sm:top-7">
                <div>
                    <span className="inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/12 px-3 py-1 text-[10px] font-bold uppercase tracking-[0.16em] text-white backdrop-blur-md sm:text-[11px]">
                        20 saniyede süreç
                    </span>
                    <p className="mt-3 font-heading text-xl font-extrabold text-white drop-shadow sm:text-3xl">
                        2 belgeyle Dubai vizesi
                    </p>
                </div>
                <span className="hidden items-center gap-2 rounded-full bg-[hsl(var(--brand-green))] px-3.5 py-1.5 text-xs font-bold text-white sm:inline-flex">
                    <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" /> Pasaport + fotoğraf yeterli
                </span>
            </div>

            {/* SAHNE METNI */}
            <div className="absolute bottom-5 left-5 right-5 sm:bottom-7 sm:left-8 sm:right-8">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={scene.key}
                        initial={{ opacity: 0, y: 16 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.4 }}
                        className="flex items-start gap-3"
                    >
                        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/25 bg-white/15 backdrop-blur-md">
                            <SceneIcon className="h-5 w-5 text-white" aria-hidden="true" />
                        </span>
                        <div>
                            <p
                                className="font-heading text-base font-bold text-white sm:text-lg"
                                data-testid="explainer-scene-title"
                            >
                                {scene.step}. {scene.title}
                            </p>
                            <p className="mt-1 text-xs leading-5 text-white/85 sm:text-sm">{scene.note}</p>
                        </div>
                    </motion.div>
                </AnimatePresence>

                {captions && (
                    <div className="mt-4">
                        <Subtitle
                            text={scene.subtitle}
                            durationMs={sceneMs}
                            paused={paused}
                            sceneKey={scene.key}
                        />
                    </div>
                )}

                <div className="mt-5 flex items-center gap-3">
                    <div className="flex flex-1 gap-1.5 sm:max-w-[300px]">
                        {SCENES.map((s, i) => (
                            <button
                                key={s.key}
                                type="button"
                                onClick={() => setIndex(i)}
                                aria-label={`${s.step}. sahne: ${s.title}`}
                                className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/30"
                                data-testid={`explainer-dot-${s.key}`}
                            >
                                <motion.span
                                    key={`${s.key}-${index}-${paused}-${soundOn}`}
                                    initial={{ width: i < index ? "100%" : "0%" }}
                                    animate={{ width: i <= index ? "100%" : "0%" }}
                                    transition={{
                                        duration: i === index && !paused ? sceneMs / 1000 : 0,
                                        ease: "linear",
                                    }}
                                    className="block h-full bg-white"
                                />
                            </button>
                        ))}
                    </div>
                    <button
                        type="button"
                        onClick={() => setSoundOn((s) => !s)}
                        aria-label={soundOn ? "Sesi kapat" : "Sesli anlatımı aç"}
                        className={`flex h-9 items-center gap-1.5 rounded-full border px-3.5 text-xs font-semibold backdrop-blur-md transition-colors duration-200 ${
                            soundOn
                                ? "border-white bg-white text-foreground"
                                : "border-white/30 bg-white/12 text-white hover:bg-white/20"
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
                        title={captions ? "Altyazıyı kapat" : "Altyazıyı aç"}
                        className={`flex h-9 items-center gap-1.5 rounded-full border px-3 text-xs font-bold backdrop-blur-md transition-colors duration-200 ${
                            captions
                                ? "border-white bg-white text-foreground"
                                : "border-white/30 bg-white/12 text-white hover:bg-white/20"
                        }`}
                        data-testid="explainer-captions-button"
                    >
                        <Captions className="h-3.5 w-3.5" /> CC
                    </button>
                    <button
                        type="button"
                        onClick={() => setPaused((p) => !p)}
                        aria-label={paused ? "Anlatımı oynat" : "Anlatımı duraklat"}
                        className="flex h-9 w-9 items-center justify-center rounded-full border border-white/30 bg-white/12 text-white backdrop-blur-md transition-colors duration-200 hover:bg-white/20"
                        data-testid="explainer-toggle-button"
                    >
                        {paused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
                    </button>
                </div>
            </div>

            <audio
                ref={audioRef}
                preload="none"
                onEnded={() => setIndex((i) => (i + 1) % SCENES.length)}
                data-testid="explainer-audio"
            />
        </div>
    );
};
