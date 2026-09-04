import React, { useState } from "react";
import { KeyRound, Loader2, Mail, UserCheck } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";

export const AccountLoginCard = ({ onLogin, stacked = false, className = "" }) => {
    const [email, setEmail] = useState("");
    const [lastName, setLastName] = useState("");
    const [code, setCode] = useState("");
    const [codeSent, setCodeSent] = useState(false);
    const [busy, setBusy] = useState(false);

    const requestCode = async () => {
        if (!email.trim()) return toast.error("E-posta adresinizi girin.");
        setBusy(true);
        try {
            const { data } = await api.post("/account/request-code", { email: email.trim() });
            setCodeSent(true);
            toast[data.sent ? "success" : "info"](
                data.sent
                    ? `Kod ${email} adresine gönderildi. ${data.expires_in_minutes} dakika geçerli.`
                    : "E-posta servisi henüz yapılandırılmadığı için kod gönderilemedi. E-posta + soyad ile giriş yapabilirsiniz."
            );
        } catch (err) {
            toast.error(apiError(err, "Kod gönderilemedi."));
        } finally {
            setBusy(false);
        }
    };

    const verifyCode = async () => {
        setBusy(true);
        try {
            const { data } = await api.post("/account/verify-code", {
                email: email.trim(),
                code: code.trim(),
            });
            onLogin(data.token, data.email);
        } catch (err) {
            toast.error(apiError(err, "Kod doğrulanamadı."));
        } finally {
            setBusy(false);
        }
    };

    const loginLastName = async () => {
        setBusy(true);
        try {
            const { data } = await api.post("/account/login-lastname", {
                email: email.trim(),
                last_name: lastName.trim(),
            });
            onLogin(data.token, data.email);
        } catch (err) {
            toast.error(apiError(err, "Giriş başarısız."));
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className={`card-surface p-6 sm:p-8 ${className}`} data-testid="account-login-card">
            <h2 className="font-heading text-xl font-bold">Başvurularıma giriş</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Başvurularınızı görmek, yarım kalan başvurunuza devam etmek ve eski bilgilerinizle
                yeni başvuru açmak için e-posta adresinizle giriş yapın.
            </p>

            <Tabs defaultValue="lastname" className="mt-6">
                <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="lastname" data-testid="account-tab-lastname">
                        <UserCheck className="mr-2 h-4 w-4" /> E-posta + soyad
                    </TabsTrigger>
                    <TabsTrigger value="code" data-testid="account-tab-code">
                        <KeyRound className="mr-2 h-4 w-4" /> E-posta kodu
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="lastname" className="mt-5 space-y-4">
                    <div className={stacked ? "grid gap-5" : "grid gap-4 sm:grid-cols-2"}>
                        <div className="space-y-2">
                            <Label htmlFor="account-email">E-posta adresiniz</Label>
                            <Input
                                id="account-email"
                                type="email"
                                placeholder="ornek@eposta.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                data-testid="account-email-input"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="account-lastname">Soyadınız</Label>
                            <Input
                                id="account-lastname"
                                placeholder="Başvurudaki soyadınız"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                data-testid="account-lastname-input"
                            />
                        </div>
                    </div>
                    <Button
                        onClick={loginLastName}
                        disabled={busy || !email.trim() || !lastName.trim()}
                        className="h-12 w-full px-7 text-base"
                        data-testid="account-lastname-login-button"
                    >
                        {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Giriş yap
                    </Button>
                </TabsContent>

                <TabsContent value="code" className="mt-5 space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="account-email-code">E-posta adresiniz</Label>
                        <Input
                            id="account-email-code"
                            type="email"
                            placeholder="ornek@eposta.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            data-testid="account-email-code-input"
                        />
                    </div>
                    <Button
                        variant="secondary"
                        onClick={requestCode}
                        disabled={busy || !email.trim()}
                        className="h-11 w-full border border-border"
                        data-testid="account-request-code-button"
                    >
                        <Mail className="mr-2 h-4 w-4" /> {codeSent ? "Kodu yeniden gönder" : "Giriş kodu gönder"}
                    </Button>
                    <div className="space-y-2">
                        <Label htmlFor="account-code">6 haneli kod</Label>
                        <Input
                            id="account-code"
                            inputMode="numeric"
                            placeholder="000000"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                            data-testid="account-code-input"
                        />
                    </div>
                    <Button
                        onClick={verifyCode}
                        disabled={busy || code.trim().length < 6}
                        className="h-12 w-full text-base"
                        data-testid="account-verify-code-button"
                    >
                        {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Kodu doğrula
                    </Button>
                </TabsContent>
            </Tabs>
        </div>
    );
};
