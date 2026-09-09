import React, { useEffect, useState } from "react";
import { ShieldCheck, Clock, AlertTriangle, CheckCircle2 } from "lucide-react";
import { formatDateTime } from "../lib/site";

const pad = (n) => String(n).padStart(2, "0");

const split = (totalSeconds) => {
    const s = Math.max(0, totalSeconds);
    return { h: Math.floor(s / 3600), m: Math.floor((s % 3600) / 60), s: s % 60 };
};

const Unit = ({ value, label, testid }) => (
    <div className="flex flex-col items-center">
        <span
            className="font-heading text-2xl font-bold tabular-nums text-foreground sm:text-3xl"
            data-testid={testid}
        >
            {value}
        </span>
        <span className="mt-0.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
            {label}
        </span>
    </div>
);

export const GuaranteeCountdown = ({ guarantee }) => {
    const deadline = guarantee?.deadline_at ? new Date(guarantee.deadline_at).getTime() : null;
    const [now, setNow] = useState(() => Date.now());

    useEffect(() => {
        if (!deadline || !["running", "overdue"].includes(guarantee?.state)) return undefined;
        const id = setInterval(() => setNow(Date.now()), 1000);
        return () => clearInterval(id);
    }, [deadline, guarantee?.state]);

    if (!guarantee) return null;
    const { state, hours = 36 } = guarantee;
    if (state === "closed") return null;

    const remaining = deadline ? Math.round((deadline - now) / 1000) : 0;
    const late = state === "overdue" || (state === "running" && remaining <= 0);
    const { h, m, s } = split(late ? -remaining : remaining);

    const tone = {
        met: "border-[hsl(var(--brand-green)/0.35)] bg-[hsl(var(--brand-green)/0.08)]",
        running: "border-primary/30 bg-primary/[0.06]",
        overdue: "border-destructive/35 bg-destructive/[0.06]",
        missed: "border-destructive/35 bg-destructive/[0.06]",
        pending: "border-border bg-[hsl(var(--cloud))]",
    }[late && state === "running" ? "overdue" : state];

    const Icon = state === "met" ? CheckCircle2 : late || state === "missed" ? AlertTriangle : ShieldCheck;

    return (
        <div className={`rounded-2xl border p-5 sm:p-6 ${tone}`} data-testid="guarantee-countdown">
            <div className="flex flex-wrap items-center justify-between gap-4">
                <div className="flex min-w-0 items-start gap-3">
                    <Icon className="mt-0.5 h-5 w-5 shrink-0 text-primary" aria-hidden="true" />
                    <div className="min-w-0">
                        <p className="font-heading text-base font-bold" data-testid="guarantee-countdown-title">
                            {hours} saat garantisi
                        </p>
                        <p className="mt-1 text-sm leading-6 text-muted-foreground" data-testid="guarantee-countdown-note">
                            {state === "pending" &&
                                "Belgeleriniz onaylanıp başvurunuz resmî mercilere iletildiği anda geri sayım başlar."}
                            {state === "running" && !late &&
                                `Başvurunuz işlemde. Sonucun en geç ${formatDateTime(guarantee.deadline_at)} tarihine kadar çıkmasını taahhüt ediyoruz.`}
                            {late && state !== "missed" &&
                                "Süre aşıldı. Ekspres hizmet bedeliniz iade edilir; ekspres almadıysanız başvurunuz ücretsiz ekspres sıraya alınır."}
                            {state === "met" &&
                                (guarantee.finished_at
                                    ? `Sonucunuz ${formatDateTime(guarantee.finished_at)} tarihinde, ${hours} saat içinde çıktı.`
                                    : `Başvurunuz sonuçlandı; ${hours} saat garantisi kapsamındaydı.`)}
                            {state === "missed" &&
                                "Sonuç taahhüt edilen süreden sonra çıktı. Ekspres hizmet bedeli iadesi için sizinle iletişime geçiyoruz."}
                        </p>
                    </div>
                </div>

                {["running", "overdue"].includes(state) && (
                    <div className="flex items-end gap-3" data-testid="guarantee-countdown-clock">
                        <Unit value={pad(h)} label="saat" testid="guarantee-countdown-hours" />
                        <span className="pb-4 font-heading text-xl text-muted-foreground">:</span>
                        <Unit value={pad(m)} label="dakika" testid="guarantee-countdown-minutes" />
                        <span className="pb-4 font-heading text-xl text-muted-foreground">:</span>
                        <Unit value={pad(s)} label="saniye" testid="guarantee-countdown-seconds" />
                    </div>
                )}
            </div>

            {["running", "overdue"].includes(state) && guarantee.start_at && (
                <div className="mt-4">
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-card">
                        <div
                            className={`h-full rounded-full transition-[width] duration-1000 ${
                                late ? "bg-destructive" : "bg-primary"
                            }`}
                            style={{
                                width: `${Math.min(
                                    100,
                                    Math.max(
                                        2,
                                        Math.round(
                                            ((now - new Date(guarantee.start_at).getTime()) /
                                                (hours * 3600 * 1000)) *
                                                100,
                                        ),
                                    ),
                                )}%`,
                            }}
                            data-testid="guarantee-countdown-bar"
                        />
                    </div>
                    <p className="mt-2 flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" aria-hidden="true" />
                        Süre {formatDateTime(guarantee.start_at)} tarihinde başladı
                        {late ? " · taahhüt edilen süre aşıldı" : ""}
                    </p>
                </div>
            )}
        </div>
    );
};
