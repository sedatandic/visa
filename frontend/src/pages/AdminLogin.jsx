import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Loader2, Lock, MailCheck, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { setMeta } from "../lib/site";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { BrandMark } from "../components/BrandMark";

const RESEND_SECONDS = 60;

export default function AdminLogin() {
    const navigate = useNavigate();
    const [email, setEmail] = useState(localStorage.getItem("dv_admin_remember_email") || "");
    const [code, setCode] = useState("");
    const [stage, setStage] = useState("email");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [cooldown, setCooldown] = useState(0);
    const codeRef = useRef(null);

    useEffect(() => {
        setMeta("Yönetici Girişi | Dubai Vize Online", "Dubai Vize Online yönetim paneli girişi.");
    }, []);

    useEffect(() => {
        if (cooldown <= 0) return;
        const timer = setTimeout(() => setCooldown((s) => s - 1), 1000);
        return () => clearTimeout(timer);
    }, [cooldown]);

    const requestCode = async (e) => {
        e?.preventDefault();
        setError("");
        setLoading(true);
        try {
            const { data } = await api.post("/admin/request-code", { email: email.trim() });
            localStorage.setItem("dv_admin_remember_email", email.trim().toLowerCase());
            setStage("code");
            setCooldown(RESEND_SECONDS);
            setCode("");
            toast.success(
                data.email_status === "sent"
                    ? "Giriş kodu e-postanıza gönderildi."
                    : "Kod oluşturuldu. E-posta servisi yanıt vermezse tekrar deneyin."
            );
            setTimeout(() => codeRef.current?.focus(), 150);
        } catch (err) {
            setError(apiError(err, "Kod gönderilemedi."));
        } finally {
            setLoading(false);
        }
    };

    const verifyCode = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            const { data } = await api.post("/admin/verify-code", {
                email: email.trim(),
                code: code.trim(),
            });
            localStorage.setItem("dv_admin_token", data.token);
            localStorage.setItem("dv_admin_email", data.user.email);
            toast.success(`Giriş başarılı. Bu bilgisayarda ${data.session_days} gün açık kalacak.`);
            navigate("/admin");
        } catch (err) {
            setError(apiError(err, "Kod doğrulanamadı."));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--navy))] px-4 py-16">
            <div className="w-full max-w-md">
                <div className="mb-8 flex items-center justify-center gap-2.5">
                    <BrandMark light />
                </div>

                {stage === "email" ? (
                    <form onSubmit={requestCode} className="rounded-xl border border-border bg-card p-7" data-testid="admin-login-form">
                        <div className="flex items-center gap-2">
                            <Lock className="h-4.5 w-4.5 text-primary" />
                            <h1 className="font-heading text-xl font-bold">Yönetici girişi</h1>
                        </div>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            Şifre yok. E-posta adresinizi girin, tek kullanımlık giriş kodunuzu gönderelim.
                        </p>

                        <div className="mt-6 space-y-2">
                            <Label htmlFor="a-email">E-posta</Label>
                            <Input
                                id="a-email"
                                type="email"
                                autoComplete="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="info@dubaivizeonline.com"
                                data-testid="admin-email-input"
                            />
                        </div>

                        {error && (
                            <p className="mt-4 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm font-medium text-destructive" data-testid="admin-login-error">
                                {error}
                            </p>
                        )}

                        <Button type="submit" disabled={loading || !email.trim()} className="mt-6 h-12 w-full text-base" data-testid="admin-request-code-button">
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Kod gönderiliyor…
                                </>
                            ) : (
                                "Giriş kodu gönder"
                            )}
                        </Button>

                        <p className="mt-5 flex items-start gap-2 text-xs leading-5 text-muted-foreground">
                            <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                            Kod 10 dakika geçerlidir ve tek kullanımlıktır. Doğruladıktan sonra oturumunuz
                            bu bilgisayarda 30 gün açık kalır.
                        </p>
                    </form>
                ) : (
                    <form onSubmit={verifyCode} className="rounded-xl border border-border bg-card p-7" data-testid="admin-code-form">
                        <div className="flex items-center gap-2">
                            <MailCheck className="h-4.5 w-4.5 text-primary" />
                            <h1 className="font-heading text-xl font-bold">Giriş kodunuzu girin</h1>
                        </div>
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            <strong className="text-foreground">{email}</strong> adresine 6 haneli bir kod
                            gönderdik. Kod 10 dakika geçerlidir.
                        </p>

                        <div className="mt-6 space-y-2">
                            <Label htmlFor="a-code">Tek kullanımlık kod</Label>
                            <Input
                                id="a-code"
                                ref={codeRef}
                                inputMode="numeric"
                                autoComplete="one-time-code"
                                maxLength={6}
                                value={code}
                                onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                                placeholder="123456"
                                className="text-center font-heading text-2xl font-bold tracking-[0.5em]"
                                data-testid="admin-code-input"
                            />
                        </div>

                        {error && (
                            <p className="mt-4 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm font-medium text-destructive" data-testid="admin-login-error">
                                {error}
                            </p>
                        )}

                        <Button type="submit" disabled={loading || code.length !== 6} className="mt-6 h-12 w-full text-base" data-testid="admin-verify-code-button">
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Doğrulanıyor…
                                </>
                            ) : (
                                "Giriş yap"
                            )}
                        </Button>

                        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
                            <button
                                type="button"
                                onClick={() => {
                                    setStage("email");
                                    setError("");
                                }}
                                className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground transition-colors duration-150 hover:text-foreground"
                                data-testid="admin-change-email-button"
                            >
                                <ArrowLeft className="h-3.5 w-3.5" /> E-postayı değiştir
                            </button>
                            <button
                                type="button"
                                onClick={requestCode}
                                disabled={cooldown > 0 || loading}
                                className="text-xs font-semibold text-primary underline underline-offset-4 transition-opacity duration-150 disabled:opacity-50"
                                data-testid="admin-resend-code-button"
                            >
                                {cooldown > 0 ? `Yeni kod (${cooldown} sn)` : "Yeni kod gönder"}
                            </button>
                        </div>
                    </form>
                )}

                <p className="mt-6 text-center text-xs text-white/50">
                    <a href="/" className="transition-colors hover:text-white/80">← Siteye dön</a>
                </p>
            </div>
        </div>
    );
}
