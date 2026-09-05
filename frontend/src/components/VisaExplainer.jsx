import React, { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { BadgeCheck, Camera, CheckCircle2, IdCard, Mail, Pause, Play, UploadCloud } from "lucide-react";

const SCENE_MS = 5000;

const SCENES = [
    {
        key: "passport",
        step: "1",
        title: "Pasaportunuzun kimlik sayfası",
        note: "Telefonunuzla çektiğiniz fotoğraf yeterli",
    },
    {
        key: "photo",
        step: "2",
        title: "Bir vesikalık fotoğraf",
        note: "Beyaz fon, son 6 ay içinde çekilmiş",
    },
    {
        key: "upload",
        step: "3",
        title: "Yükleyin ve ödemeyi yapın",
        note: "Uçak bileti ve otel rezervasyonu şartı yok",
    },
    {
        key: "delivered",
        step: "4",
        title: "Vizeniz e-postanıza gelir",
        note: "Ortalama 2 iş günü · ekspreste ~8 mesai saati",
    },
];

const fade = {
    initial: { opacity: 0, y: 14, scale: 0.97 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, y: -12, scale: 0.98 },
};

const DocCard = ({ icon: Icon, label, lines }) => (
    <motion.div
        initial={{ rotate: -4, y: 18, opacity: 0 }}
        animate={{ rotate: -2, y: 0, opacity: 1 }}
        transition={{ type: "spring", stiffness: 120, damping: 14 }}
        className="relative w-56 rounded-xl border border-border bg-card p-4 sm:w-64"
        style={{ boxShadow: "var(--shadow-soft)" }}
    >
        <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
            </span>
            <span className="font-heading text-sm font-bold">{label}</span>
        </div>
        <div className="mt-3 space-y-1.5">
            {lines.map((w, i) => (
                <motion.span
                    key={i}
                    initial={{ width: 0 }}
                    animate={{ width: w }}
                    transition={{ delay: 0.25 + i * 0.15, duration: 0.5 }}
                    className="block h-2 rounded-full bg-muted"
                />
            ))}
        </div>
        <motion.span
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 1.1, type: "spring", stiffness: 240, damping: 12 }}
            className="absolute -right-3 -top-3 flex h-9 w-9 items-center justify-center rounded-full bg-[hsl(var(--brand-green))] text-white"
        >
            <CheckCircle2 className="h-5 w-5" aria-hidden="true" />
        </motion.span>
    </motion.div>
);

const SceneVisual = ({ sceneKey }) => {
    if (sceneKey === "passport") {
        return <DocCard icon={IdCard} label="Pasaport · kimlik sayfası" lines={["85%", "60%", "70%"]} />;
    }
    if (sceneKey === "photo") {
        return <DocCard icon={Camera} label="Vesikalık fotoğraf" lines={["70%", "45%"]} />;
    }
    if (sceneKey === "upload") {
        return (
            <div className="w-64 rounded-xl border border-border bg-card p-5 sm:w-72" style={{ boxShadow: "var(--shadow-soft)" }}>
                <div className="flex items-center gap-2.5">
                    <UploadCloud className="h-5 w-5 text-primary" aria-hidden="true" />
                    <span className="font-heading text-sm font-bold">2 belge yükleniyor</span>
                </div>
                <div className="mt-4 h-2.5 overflow-hidden rounded-full bg-muted">
                    <motion.span
                        initial={{ width: "8%" }}
                        animate={{ width: "100%" }}
                        transition={{ duration: 3.2, ease: "easeInOut" }}
                        className="block h-full rounded-full bg-[hsl(var(--brand-green))]"
                    />
                </div>
                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 3.3 }}
                    className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-[hsl(var(--brand-green))]"
                >
                    <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" /> Ödeme alındı, başvuru bize geçti
                </motion.p>
            </div>
        );
    }
    return (
        <div className="relative flex w-64 flex-col items-center sm:w-72">
            <motion.div
                initial={{ y: 40, opacity: 0, rotate: 6 }}
                animate={{ y: 0, opacity: 1, rotate: 0 }}
                transition={{ type: "spring", stiffness: 110, damping: 13 }}
                className="w-full rounded-xl border border-[hsl(var(--brand-green)/0.4)] bg-[hsl(var(--brand-green)/0.08)] p-5"
                style={{ boxShadow: "var(--shadow-soft)" }}
            >
                <div className="flex items-center gap-2.5">
                    <BadgeCheck className="h-5 w-5 text-[hsl(var(--brand-green))]" aria-hidden="true" />
                    <span className="font-heading text-sm font-bold text-[hsl(var(--brand-green))]">
                        Dubai vizeniz onaylandı
                    </span>
                </div>
                <p className="mt-2 text-xs font-semibold text-[hsl(var(--brand-green))]/80">
                    vize-onayi.pdf · e-posta ile teslim
                </p>
            </motion.div>
            <motion.span
                initial={{ scale: 0.6, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="mt-4 flex items-center gap-2 rounded-full border border-border bg-card px-3.5 py-1.5 text-xs font-semibold"
            >
                <Mail className="h-3.5 w-3.5 text-primary" aria-hidden="true" /> E-postanıza ve takip sayfanıza yüklendi
            </motion.span>
        </div>
    );
};

export const VisaExplainer = () => {
    const [index, setIndex] = useState(0);
    const [paused, setPaused] = useState(false);
    const scene = SCENES[index];

    useEffect(() => {
        if (paused) return;
        const timer = setTimeout(() => setIndex((i) => (i + 1) % SCENES.length), SCENE_MS);
        return () => clearTimeout(timer);
    }, [index, paused]);

    return (
        <div
            className="relative overflow-hidden rounded-[var(--radius-lg)] border border-border bg-[hsl(var(--cloud))] px-6 py-8 sm:px-10 sm:py-10"
            style={{ boxShadow: "var(--shadow-card)" }}
            data-testid="visa-explainer"
        >
            <div className="flex flex-col items-center gap-8 md:flex-row md:items-center md:justify-between md:gap-12">
                <div className="max-w-md text-center md:text-left">
                    <span className="inline-flex items-center gap-2 rounded-full border border-[hsl(var(--brand-green)/0.35)] bg-[hsl(var(--brand-green)/0.09)] px-3 py-1 text-[11px] font-bold uppercase tracking-[0.14em] text-[hsl(var(--brand-green))]">
                        20 saniyede süreç
                    </span>
                    <h2 className="mt-4 font-heading text-2xl font-extrabold sm:text-3xl">
                        2 belgeyle Dubai vizesi
                    </h2>
                    <AnimatePresence mode="wait">
                        <motion.div key={scene.key} {...fade} transition={{ duration: 0.35 }} className="mt-4">
                            <p className="font-heading text-base font-bold text-primary" data-testid="explainer-scene-title">
                                {scene.step}. {scene.title}
                            </p>
                            <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{scene.note}</p>
                        </motion.div>
                    </AnimatePresence>

                    <div className="mt-6 flex items-center justify-center gap-3 md:justify-start">
                        <div className="flex flex-1 gap-1.5 md:max-w-[240px]">
                            {SCENES.map((s, i) => (
                                <button
                                    key={s.key}
                                    type="button"
                                    onClick={() => setIndex(i)}
                                    aria-label={`${s.step}. sahne: ${s.title}`}
                                    className="h-1.5 flex-1 overflow-hidden rounded-full bg-border"
                                    data-testid={`explainer-dot-${s.key}`}
                                >
                                    <motion.span
                                        key={`${s.key}-${index}-${paused}`}
                                        initial={{ width: i === index ? "0%" : i < index ? "100%" : "0%" }}
                                        animate={{ width: i <= index ? "100%" : "0%" }}
                                        transition={{ duration: i === index && !paused ? SCENE_MS / 1000 : 0, ease: "linear" }}
                                        className="block h-full bg-primary"
                                    />
                                </button>
                            ))}
                        </div>
                        <button
                            type="button"
                            onClick={() => setPaused((p) => !p)}
                            aria-label={paused ? "Anlatımı oynat" : "Anlatımı duraklat"}
                            className="flex h-8 w-8 items-center justify-center rounded-full border border-border bg-card text-foreground/70 transition-colors duration-200 hover:text-primary"
                            data-testid="explainer-toggle-button"
                        >
                            {paused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
                        </button>
                    </div>
                </div>

                <div className="flex min-h-[220px] w-full items-center justify-center md:w-auto md:min-w-[320px]">
                    <AnimatePresence mode="wait">
                        <motion.div key={scene.key} {...fade} transition={{ duration: 0.4 }}>
                            <SceneVisual sceneKey={scene.key} />
                        </motion.div>
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
};
