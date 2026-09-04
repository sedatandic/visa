import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, Lock, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { setMeta } from "../lib/site";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { BrandMark } from "../components/BrandMark";

export default function AdminLogin() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        setMeta("Yönetici Girişi | Dubai Vize Online", "Dubai Vize Online yönetim paneli girişi.");
    }, []);

    const submit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            const { data } = await api.post("/admin/login", { email, password });
            localStorage.setItem("dv_admin_token", data.token);
            localStorage.setItem("dv_admin_email", data.user.email);
            toast.success("Giriş başarılı.");
            navigate("/admin");
        } catch (err) {
            setError(apiError(err, "Giriş yapılamadı."));
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
                <form onSubmit={submit} className="rounded-xl border border-border bg-card p-7" data-testid="admin-login-form">
                    <div className="flex items-center gap-2">
                        <Lock className="h-4.5 w-4.5 text-primary" />
                        <h1 className="font-heading text-xl font-bold">Yönetici girişi</h1>
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">
                        Başvuruları görüntülemek için yönetici hesabınızla giriş yapın.
                    </p>

                    <div className="mt-6 space-y-5">
                        <div className="space-y-2">
                            <Label htmlFor="a-email">E-posta</Label>
                            <Input
                                id="a-email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="info@dubaivizeonline.com"
                                data-testid="admin-email-input"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="a-pass">Şifre</Label>
                            <Input
                                id="a-pass"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                data-testid="admin-password-input"
                            />
                        </div>
                    </div>

                    {error && (
                        <p className="mt-4 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm font-medium text-destructive" data-testid="admin-login-error">
                            {error}
                        </p>
                    )}

                    <Button type="submit" disabled={loading} className="mt-6 h-12 w-full text-base" data-testid="admin-login-button">
                        {loading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Giriş yapılıyor…
                            </>
                        ) : (
                            "Giriş yap"
                        )}
                    </Button>

                    <p className="mt-5 flex items-start gap-2 text-xs leading-5 text-muted-foreground">
                        <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                        Oturumunuz 12 saat sonra otomatik olarak sona erer. Başvuru sahiplerinin
                        belgeleri yalnızca yönetici oturumuyla görüntülenebilir.
                    </p>
                </form>

                <p className="mt-6 text-center text-xs text-white/50">
                    <a href="/" className="transition-colors hover:text-white/80">← Siteye dön</a>
                </p>
            </div>
        </div>
    );
}
