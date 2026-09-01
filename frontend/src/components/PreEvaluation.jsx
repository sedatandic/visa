import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
    ArrowLeft,
    ArrowRight,
    CheckCircle2,
    Gauge,
    Lightbulb,
    Loader2,
    MinusCircle,
    RefreshCcw,
    ShieldCheck,
    Sparkles,
    TriangleAlert,
} from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { api } from "../lib/api";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Progress } from "./ui/progress";
import { Skeleton } from "./ui/skeleton";

const LEVEL_STYLES = {
    high: {
        ring: "text-primary",
        badge: "bg-primary/10 text-primary border-primary/30",
        icon: CheckCircle2,
    },
    medium: {
        ring: "text-primary",
        badge: "bg-primary/10 text-primary border-primary/30",
        icon: ShieldCheck,
    },
    review: {
        ring: "text-[hsl(38_92%_38%)]",
        badge: "bg-[hsl(38_92%_38%/0.12)] text-[hsl(38_92%_32%)] border-[hsl(38_92%_38%/0.3)]",
        icon: TriangleAlert,
    },
    low: {
        ring: "text-[hsl(var(--brand-red))]",
        badge: "bg-[hsl(var(--brand-red)/0.08)] text-[hsl(var(--brand-red))] border-[hsl(var(--brand-red)/0.3)]",
        icon: TriangleAlert,
    },
};

const ScoreDial = ({ score, level }) => {
    const style = LEVEL_STYLES[level] || LEVEL_STYLES.medium;
    const radius = 54;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (Math.max(0, Math.min(100, score)) / 100) * circumference;
    return (
        <div className="relative h-[140px] w-[140px] shrink-0" data-testid="pre-eval-score-dial">
            <svg viewBox="0 0 140 140" className="h-full w-full -rotate-90">
                <circle cx="70" cy="70" r={radius} fill="none" strokeWidth="12" className="stroke-muted" />
                <circle
                    cx="70"
                    cy="70"
                    r={radius}
                    fill="none"
                    strokeWidth="12"
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    className={`${style.ring} stroke-current`}
                    style={{ transition: "stroke-dashoffset 700ms ease-out" }}
                />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold leading-none" data-testid="pre-eval-score-value">
                    {score}
                    <span className="text-lg">%</span>
                </span>
                <span className="mt-1 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                    onay olasılığı
                </span>
            </div>
        </div>
    );
};

export const PreEvaluation = ({ compact = false }) => {
    const [questions, setQuestions] = useState(null);
    const [step, setStep] = useState(0);
    const [answers, setAnswers] = useState({});
    const [result, setResult] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [lead, setLead] = useState({ name: "", email: "", phone: "" });
    const [leadSent, setLeadSent] = useState(false);

    useEffect(() => {
        api
            .get("/pre-evaluation/questions")
            .then(({ data }) => setQuestions(data.questions || []))
            .catch(() => setQuestions([]));
    }, []);

    const total = questions?.length || 0;
    const requiredCount = (questions || []).filter((q) => !q.optional).length || total;
    const current = questions?.[step];
    const progress = useMemo(() => {
        if (result) return 100;
        if (!total) return 0;
        return Math.round((step / total) * 100);
    }, [step, total, result]);

    const submit = async (finalAnswers, contact = null) => {
        setSubmitting(true);
        try {
            const { data } = await api.post("/pre-evaluation", {
                passport_validity: finalAnswers.passport_validity,
                visa_history: finalAnswers.visa_history,
                refusal_history: finalAnswers.refusal_history,
                purpose: finalAnswers.purpose || "",
                name: contact?.name || "",
                email: contact?.email || "",
                phone: contact?.phone || "",
            });
            setResult(data);
            return true;
        } catch (err) {
            toast.error("Değerlendirme yapılamadı. Lütfen tekrar deneyin.");
            return false;
        } finally {
            setSubmitting(false);
        }
    };

    const pick = async (key, value) => {
        const next = { ...answers, [key]: value };
        setAnswers(next);
        if (step + 1 < total) {
            setStep(step + 1);
            return;
        }
        await submit(next);
    };

    const skipOptional = async () => {
        if (step + 1 < total) {
            setStep(step + 1);
            return;
        }
        await submit(answers);
    };

    const reset = () => {
        setAnswers({});
        setResult(null);
        setStep(0);
        setLeadSent(false);
        setLead({ name: "", email: "", phone: "" });
    };

    const sendLead = async (e) => {
        e.preventDefault();
        if (!lead.email.trim() && !lead.phone.trim()) {
            toast.error("E-posta veya telefon bilgisinden en az birini girin.");
            return;
        }
        const ok = await submit(answers, lead);
        if (ok) {
            setLeadSent(true);
            toast.success("Bilgileriniz alındı. Danışmanımız kısa süre içinde dönüş yapacak.");
        }
    };

    if (questions === null) {
        return (
            <div className="rounded-2xl border border-border bg-card p-6" data-testid="pre-eval-loading">
                <Skeleton className="h-5 w-40" />
                <Skeleton className="mt-4 h-12 w-full" />
                <Skeleton className="mt-3 h-12 w-full" />
                <Skeleton className="mt-3 h-12 w-full" />
            </div>
        );
    }

    if (!questions.length) {
        return (
            <div className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground" data-testid="pre-eval-error">
                Ön değerlendirme aracı şu anda kullanılamıyor.{" "}
                <button type="button" className="font-semibold text-primary underline" onClick={() => window.location.reload()}>
                    Yeniden dene
                </button>
            </div>
        );
    }

    const levelStyle = result ? LEVEL_STYLES[result.level] || LEVEL_STYLES.medium : LEVEL_STYLES.medium;
    const LevelIcon = levelStyle.icon;

    return (
        <div
            className="overflow-hidden rounded-2xl border border-border bg-card"
            style={{ boxShadow: "var(--shadow-soft)" }}
            data-testid="pre-eval-widget"
        >
            <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-4 sm:px-6">
                <div className="flex items-center gap-2.5">
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                        <Gauge className="h-4 w-4 text-primary" />
                    </span>
                    <div>
                        <p className="text-sm font-bold leading-tight" data-testid="pre-eval-title">
                            Ücretsiz Ön Değerlendirme
                        </p>
                        <p className="text-xs text-muted-foreground">
                            {result
                                ? "Sonucunuz hazır"
                                : `${requiredCount} kısa soru · yaklaşık 30 saniye`}
                        </p>
                    </div>
                </div>
                {result ? (
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={reset}
                        className="text-xs"
                        data-testid="pre-eval-restart-button"
                    >
                        <RefreshCcw className="mr-1.5 h-3.5 w-3.5" /> Baştan
                    </Button>
                ) : (
                    <span className="text-xs font-semibold text-muted-foreground" data-testid="pre-eval-step-indicator">
                        {step + 1} / {total}
                    </span>
                )}
            </div>

            <Progress value={progress} className="h-1 rounded-none" data-testid="pre-eval-progress" />

            <div className="px-5 py-6 sm:px-6">
                {!result && current && (
                    <motion.div
                        key={current.key}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.2 }}
                        data-testid={`pre-eval-question-${current.key}`}
                    >
                        <h3 className="text-lg font-bold leading-snug sm:text-xl">{current.title}</h3>
                        {current.help && <p className="mt-2 text-sm text-muted-foreground">{current.help}</p>}

                        <div className="mt-5 grid gap-2.5">
                            {current.options.map((opt) => {
                                const selected = answers[current.key] === opt.value;
                                return (
                                    <button
                                        key={opt.value}
                                        type="button"
                                        disabled={submitting}
                                        onClick={() => pick(current.key, opt.value)}
                                        data-testid={`pre-eval-option-${current.key}-${opt.value}`}
                                        className={`group flex items-center justify-between gap-3 rounded-xl border px-4 py-3.5 text-left text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 ${
                                            selected
                                                ? "border-primary bg-primary/10 text-primary"
                                                : "border-border bg-background hover:border-primary/40 hover:bg-primary/[0.04]"
                                        }`}
                                    >
                                        <span>{opt.label}</span>
                                        <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200 group-hover:translate-x-0.5" />
                                    </button>
                                );
                            })}
                        </div>

                        <div className="mt-5 flex items-center justify-between gap-3">
                            <Button
                                variant="ghost"
                                size="sm"
                                disabled={step === 0 || submitting}
                                onClick={() => setStep(Math.max(0, step - 1))}
                                data-testid="pre-eval-back-button"
                            >
                                <ArrowLeft className="mr-1.5 h-3.5 w-3.5" /> Geri
                            </Button>
                            <div className="flex items-center gap-2">
                                {submitting && <Loader2 className="h-4 w-4 animate-spin text-primary" />}
                                {current.optional && (
                                    <Button
                                        variant="secondary"
                                        size="sm"
                                        disabled={submitting}
                                        onClick={skipOptional}
                                        data-testid="pre-eval-skip-button"
                                    >
                                        Atla ve sonucu gör
                                    </Button>
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}

                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.25 }}
                        data-testid="pre-eval-result"
                    >
                        <div className="flex flex-col items-center gap-5 sm:flex-row sm:items-center">
                            <ScoreDial score={result.score} level={result.level} />
                            <div className="min-w-0 flex-1">
                                <span
                                    className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${levelStyle.badge}`}
                                    data-testid="pre-eval-level-badge"
                                >
                                    <LevelIcon className="h-3.5 w-3.5" /> {result.level_title}
                                </span>
                                <p className="mt-3 text-sm leading-6 text-muted-foreground" data-testid="pre-eval-level-note">
                                    {result.level_note}
                                </p>

                                {result.recommended_visa && (
                                    <div
                                        className="mt-4 rounded-xl border border-border bg-background p-3.5"
                                        data-testid="pre-eval-recommended-visa"
                                    >
                                        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                            Size önerilen vize
                                        </p>
                                        <p className="mt-1 text-sm font-bold">{result.recommended_visa.name}</p>
                                        <p className="mt-0.5 text-xs text-muted-foreground">
                                            {result.recommended_visa.processing_days}
                                            {result.recommended_visa.price
                                                ? ` · ${Number(result.recommended_visa.price).toLocaleString("tr-TR")} ₺`
                                                : ""}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>

                        {result.blockers?.length > 0 && (
                            <div
                                className="mt-5 rounded-xl border border-[hsl(var(--brand-red)/0.3)] bg-[hsl(var(--brand-red)/0.06)] p-4"
                                data-testid="pre-eval-blockers"
                            >
                                <p className="flex items-center gap-2 text-sm font-bold text-[hsl(var(--brand-red))]">
                                    <TriangleAlert className="h-4 w-4" /> Önce çözülmesi gerekenler
                                </p>
                                <ul className="mt-2 space-y-1.5">
                                    {result.blockers.map((b) => (
                                        <li key={b} className="text-xs leading-5 text-muted-foreground">
                                            • {b}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {result.factors?.length > 0 && (
                            <div className="mt-5 grid gap-2.5" data-testid="pre-eval-factors">
                                {result.factors.map((f) => (
                                    <div key={f.key} className="flex items-start gap-2.5 rounded-lg border border-border bg-background p-3">
                                        {f.impact === "positive" ? (
                                            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                        ) : f.impact === "negative" ? (
                                            <MinusCircle className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--brand-red))]" />
                                        ) : (
                                            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                                        )}
                                        <div className="min-w-0">
                                            <p className="text-xs font-semibold">{f.label}</p>
                                            <p className="mt-0.5 text-xs leading-5 text-muted-foreground">{f.reason}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        {result.tips?.length > 0 && (
                            <div className="mt-5 rounded-xl border border-border bg-secondary/60 p-4" data-testid="pre-eval-tips">
                                <p className="flex items-center gap-2 text-sm font-bold">
                                    <Lightbulb className="h-4 w-4 text-primary" /> Onay şansınızı artıracak adımlar
                                </p>
                                <ul className="mt-2.5 space-y-2">
                                    {result.tips.map((t) => (
                                        <li key={t} className="flex items-start gap-2 text-xs leading-5 text-muted-foreground">
                                            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                                            {t}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        <div className="mt-6 flex flex-wrap items-center gap-3">
                            <Button asChild className="h-11 px-6" data-testid="pre-eval-apply-button">
                                <Link to="/basvuru">
                                    Başvuruya Başla <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                            <Button asChild variant="secondary" className="h-11 px-5" data-testid="pre-eval-contact-button">
                                <Link to="/iletisim">Danışmanla görüş</Link>
                            </Button>
                        </div>

                        {!leadSent ? (
                            <form onSubmit={sendLead} className="mt-6 rounded-xl border border-dashed border-border p-4" data-testid="pre-eval-lead-form">
                                <p className="text-sm font-semibold">Sonucu size ulaştıralım mı?</p>
                                <p className="mt-1 text-xs text-muted-foreground">
                                    Bilgilerinizi bırakın, danışmanımız dosyanızı ücretsiz kontrol edip dönüş yapsın.
                                </p>
                                <div className="mt-3 grid gap-3 sm:grid-cols-3">
                                    <div>
                                        <Label htmlFor="pre-eval-name" className="text-xs">
                                            Ad Soyad
                                        </Label>
                                        <Input
                                            id="pre-eval-name"
                                            value={lead.name}
                                            onChange={(e) => setLead({ ...lead, name: e.target.value })}
                                            placeholder="Adınız"
                                            className="mt-1.5"
                                            data-testid="pre-eval-lead-name-input"
                                        />
                                    </div>
                                    <div>
                                        <Label htmlFor="pre-eval-email" className="text-xs">
                                            E-posta
                                        </Label>
                                        <Input
                                            id="pre-eval-email"
                                            type="email"
                                            value={lead.email}
                                            onChange={(e) => setLead({ ...lead, email: e.target.value })}
                                            placeholder="ornek@eposta.com"
                                            className="mt-1.5"
                                            data-testid="pre-eval-lead-email-input"
                                        />
                                    </div>
                                    <div>
                                        <Label htmlFor="pre-eval-phone" className="text-xs">
                                            Telefon
                                        </Label>
                                        <Input
                                            id="pre-eval-phone"
                                            value={lead.phone}
                                            onChange={(e) => setLead({ ...lead, phone: e.target.value })}
                                            placeholder="05xx xxx xx xx"
                                            className="mt-1.5"
                                            data-testid="pre-eval-lead-phone-input"
                                        />
                                    </div>
                                </div>
                                <Button
                                    type="submit"
                                    variant="secondary"
                                    className="mt-3.5 h-10"
                                    disabled={submitting}
                                    data-testid="pre-eval-lead-submit-button"
                                >
                                    {submitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                                    Ücretsiz kontrol talep et
                                </Button>
                            </form>
                        ) : (
                            <div
                                className="mt-6 flex items-start gap-2.5 rounded-xl border border-primary/30 bg-primary/[0.06] p-4"
                                data-testid="pre-eval-lead-success"
                            >
                                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                                <p className="text-xs leading-5 text-muted-foreground">
                                    Talebiniz alındı. Danışmanımız en kısa sürede sizinle iletişime geçecek.
                                </p>
                            </div>
                        )}

                        <p className="mt-4 text-[11px] leading-5 text-muted-foreground" data-testid="pre-eval-disclaimer">
                            {result.disclaimer}
                        </p>
                    </motion.div>
                )}
            </div>

            {!compact && !result && (
                <div className="flex items-center gap-2 border-t border-border bg-secondary/50 px-5 py-3 sm:px-6">
                    <Sparkles className="h-3.5 w-3.5 text-primary" />
                    <p className="text-[11px] leading-5 text-muted-foreground">
                        Sonuç bilgilendirme amaçlıdır; kayıt veya ödeme gerektirmez.
                    </p>
                </div>
            )}
        </div>
    );
};

export default PreEvaluation;
