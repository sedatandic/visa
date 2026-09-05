import React, { useEffect, useRef, useState } from "react";
import { ArrowLeft, Loader2, Mail, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";

export const AccountLoginCard = ({ onLogin, stacked = false, className = "" }) => {
    const [email, setEmail] = useState("");
    const [code, setCode] = useState("");
    const [stage, setStage] = useState("email");
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [cooldown, setCooldown] = useState(0);
    const timerRef = useRef(null);

    useEffect(() => {
        if (cooldown <= 0) return undefined;
        timerRef.current = setTimeout(() => setCooldown((s) => s - 1), 1000);
        return () => clearTimeout(timerRef.current);
    }, [cooldown]);

    const requestCode = async () => {
        if (!email.trim()) return toast.error("E-posta adresinizi girin.");
        setBusy(true);
        setError("");
        try {
            const { data } = await api.post("/account/request-code", { email: email.trim() });
            setStage("code");
            setCooldown(data.cooldown_seconds || 60);
            toast[data.sent ? "success" : "info"](
                data.sent
                    ? `Kod ${email.trim()} adresine gönderildi. ${data.expires_in_minutes} dakika geçerli.`
                    : "Kod gönderilemedi. E-posta adresinizi kontrol edip tekrar deneyin."
            );
        } catch (err) {
            setError(apiError(err, "Kod gönderilemedi."));
        } finally {
            setBusy(false);
        }
    };

    const verifyCode = async () => {
        setBusy(true);
        setError("");
        try {
            const { data } = await api.post("/account/verify-code", {
                email: email.trim(),
                code: code.trim(),
            });
            onLogin(data.token, data.email);
        } catch (err) {
            setError(apiError(err, "Kod doğrulanamadı."));
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className={`card-surface p-6 sm:p-8 ${className}`} data-testid="account-login-card">
            <h2 className="font-heading text-xl font-bold">Başvurularıma giriş</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Şifre yok: e-posta adresinize gönderdiğimiz 6 haneli tek kullanımlık kod ile
                giriş yapın. Başvurularınızı görebilir, yarım kalan başvurunuza devam edebilirsiniz.
            </p>

            {stage === "email" ? (
                <div className={`mt-6 ${stacked ? "grid gap-5" : "grid gap-4"}`} data-testid="account-email-form">
                    <div className="space-y-2">
                        <Label htmlFor="account-email">E-posta adresiniz</Label>
                        <Input
                            id="account-email"
                            type="email"
                            placeholder="ornek@eposta.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && requestCode()}
                            data-testid="account-email-input"
                        />
                        <p className="text-xs text-muted-foreground">
                            Başvuru sırasında kullandığınız e-posta adresini girin.
                        </p>
                    </div>
                    <Button
                        onClick={requestCode}
                        disabled={busy || !email.trim()}
                        className="h-12 w-full px-7 text-base"
                        data-testid="account-request-code-button"
                    >
                        {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Mail className="mr-2 h-4 w-4" />}
                        Giriş kodu gönder
                    </Button>
                </div>
            ) : (
                <div className="mt-6 grid gap-4" data-testid="account-code-form">
                    <div className="flex items-start gap-2 rounded-xl border border-border bg-muted/40 p-3 text-sm">
                        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                        <span>
                            <b className="break-all">{email.trim()}</b> adresine 6 haneli kod gönderdik.
                            Kod 15 dakika geçerli ve tek kullanımlıktır.
                        </span>
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="account-code">6 haneli kod</Label>
                        <Input
                            id="account-code"
                            inputMode="numeric"
                            autoComplete="one-time-code"
                            placeholder="000000"
                            value={code}
                            onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                            onKeyDown={(e) => e.key === "Enter" && code.trim().length === 6 && verifyCode()}
                            className="text-center text-2xl tracking-[0.4em]"
                            data-testid="account-code-input"
                        />
                    </div>
                    <Button
                        onClick={verifyCode}
                        disabled={busy || code.trim().length < 6}
                        className="h-12 w-full text-base"
                        data-testid="account-verify-code-button"
                    >
                        {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Kodu doğrula ve giriş yap
                    </Button>
                    <div className="flex flex-wrap items-center justify-between gap-2">
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                                setStage("email");
                                setCode("");
                                setError("");
                            }}
                            data-testid="account-change-email-button"
                        >
                            <ArrowLeft className="mr-1 h-4 w-4" /> E-postayı değiştir
                        </Button>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={requestCode}
                            disabled={busy || cooldown > 0}
                            data-testid="account-resend-code-button"
                        >
                            {cooldown > 0 ? `Yeni kod (${cooldown} sn)` : "Yeni kod gönder"}
                        </Button>
                    </div>
                </div>
            )}

            {error ? (
                <p className="mt-4 rounded-xl border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive" data-testid="account-login-error">
                    {error}
                </p>
            ) : null}
        </div>
    );
};
