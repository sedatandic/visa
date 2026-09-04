import React, { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
    AlertTriangle,
    ArrowRight,
    Baby,
    Copy,
    FileText,
    KeyRound,
    Loader2,
    LogOut,
    Mail,
    RefreshCw,
    Trash2,
    User,
    UserCheck,
} from "lucide-react";
import { toast } from "sonner";
import { api, apiError, customerAuth } from "../lib/api";
import { formatDateTime, formatMoney, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { StatusBadge, PaymentBadge } from "../components/StatusBadge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";

const LoginCard = ({ onLogin }) => {
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
        <div className="card-surface mx-auto max-w-xl p-7" data-testid="account-login-card">
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
                    <div className="grid gap-4 sm:grid-cols-2">
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
                    <p className="text-xs text-muted-foreground">
                        Daha önce başvurusu olan müşteriler bu yöntemle giriş yapabilir.
                    </p>
                    <Button
                        onClick={loginLastName}
                        disabled={busy || !email.trim() || !lastName.trim()}
                        className="h-11 w-full"
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
                        className="h-11 w-full"
                        data-testid="account-verify-code-button"
                    >
                        {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null} Kodu doğrula
                    </Button>
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default function MyAccount() {
    const navigate = useNavigate();
    const [token, setToken] = useState(customerAuth.token);
    const [data, setData] = useState(null);
    const [travelers, setTravelers] = useState([]);
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setMeta(
            "Başvurularım | Dubai Vize Online",
            "Dubai vize başvurularınızı görüntüleyin, yarım kalan başvurunuza devam edin ve eski bilgilerinizle yeni başvuru açın.",
            { canonicalPath: "/hesabim", noindex: true }
        );
    }, []);

    const load = useCallback(async () => {
        if (!customerAuth.token) return;
        setLoading(true);
        try {
            const { data: res } = await api.get("/account/me");
            setData(res);
            api.get("/account/travelers")
                .then(({ data: t }) => setTravelers(t.items || []))
                .catch(() => {});
            api.get("/account/orders")
                .then(({ data: o }) => setOrders(o.items || []))
                .catch(() => {});
        } catch (err) {
            if (err?.response?.status === 401) {
                customerAuth.clear();
                setToken(null);
                toast.info("Oturum süresi doldu. Lütfen tekrar giriş yapın.");
            } else {
                toast.error(apiError(err, "Bilgiler yüklenemedi."));
            }
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (token) load();
    }, [token, load]);

    const handleLogin = (newToken, email) => {
        customerAuth.save(newToken, email);
        setToken(newToken);
        toast.success("Giriş yapıldı.");
    };

    const logout = () => {
        customerAuth.clear();
        setToken(null);
        setData(null);
        setTravelers([]);
        setOrders([]);
        toast.success("Çıkış yapıldı.");
    };

    const deleteTraveler = async (id) => {
        try {
            await api.delete(`/account/travelers/${id}`);
            setTravelers((list) => list.filter((t) => t.id !== id));
            toast.success("Kayıtlı yolcu silindi.");
        } catch (err) {
            toast.error(apiError(err, "Yolcu silinemedi."));
        }
    };

    const deleteDraft = async (id) => {
        try {
            await api.delete(`/account/drafts/${id}`);
            setData((d) => ({ ...d, drafts: d.drafts.filter((x) => x.id !== id) }));
            toast.success("Taslak silindi.");
        } catch (err) {
            toast.error(apiError(err, "Taslak silinemedi."));
        }
    };

    const reapply = (app) => navigate(`/basvuru?kopya=${app.id}&eposta=${encodeURIComponent(data.email)}`);

    return (
        <div>
            <PageHeader
                eyebrow="Hesabım"
                title="Başvurularım"
                description="Geçmiş başvurularınızı takip edin, yarım kalan başvurunuza devam edin veya aynı bilgilerle yeni başvuru açın."
            />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page">
                    {!token ? (
                        <LoginCard onLogin={handleLogin} />
                    ) : loading && !data ? (
                        <div className="flex justify-center py-16">
                            <Loader2 className="h-6 w-6 animate-spin text-primary" />
                        </div>
                    ) : (
                        <div data-testid="account-dashboard">
                            <div className="flex flex-wrap items-center justify-between gap-3">
                                <p className="text-sm text-muted-foreground">
                                    Giriş yapıldı:{" "}
                                    <span className="font-semibold text-foreground" data-testid="account-email-label">
                                        {data?.email}
                                    </span>
                                </p>
                                <div className="flex gap-2">
                                    <Button
                                        variant="secondary"
                                        className="h-10 border border-border"
                                        onClick={load}
                                        data-testid="account-refresh-button"
                                    >
                                        <RefreshCw className="mr-2 h-4 w-4" /> Yenile
                                    </Button>
                                    <Button
                                        variant="secondary"
                                        className="h-10 border border-border"
                                        onClick={logout}
                                        data-testid="account-logout-button"
                                    >
                                        <LogOut className="mr-2 h-4 w-4" /> Çıkış
                                    </Button>
                                </div>
                            </div>

                            {/* DRAFTS */}
                            {(data?.drafts || []).length > 0 && (
                                <div className="mt-8" data-testid="account-drafts">
                                    <h2 className="font-heading text-lg font-bold">Yarım kalan başvurular</h2>
                                    <div className="mt-4 grid gap-4 md:grid-cols-2">
                                        {data.drafts.map((d) => (
                                            <div
                                                key={d.id}
                                                className="card-surface p-5"
                                                data-testid={`account-draft-${d.id}`}
                                            >
                                                <div className="flex items-start justify-between gap-3">
                                                    <div>
                                                        <p className="font-heading text-base font-bold">{d.title}</p>
                                                        <p className="mt-1 text-xs text-muted-foreground">
                                                            {d.traveler_count} yolcu · Son kayıt:{" "}
                                                            {formatDateTime(d.updated_at)}
                                                        </p>
                                                        <p className="mt-1 text-xs text-muted-foreground">
                                                            Devam kodu:{" "}
                                                            <span className="font-mono font-semibold text-foreground">
                                                                {d.resume_code}
                                                            </span>
                                                        </p>
                                                    </div>
                                                    <Button
                                                        variant="secondary"
                                                        className="h-9 shrink-0 border border-border text-destructive"
                                                        onClick={() => deleteDraft(d.id)}
                                                        aria-label="Taslağı sil"
                                                        data-testid={`delete-draft-${d.id}`}
                                                    >
                                                        <Trash2 className="h-4 w-4" />
                                                    </Button>
                                                </div>
                                                <Button
                                                    asChild
                                                    className="mt-4 h-10 w-full"
                                                    data-testid={`resume-draft-${d.id}`}
                                                >
                                                    <Link to={`/basvuru?taslak=${d.id}&kod=${d.resume_code}`}>
                                                        Kaldığım yerden devam et{" "}
                                                        <ArrowRight className="ml-2 h-4 w-4" />
                                                    </Link>
                                                </Button>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* ORDERS (eSIM / sigorta) */}
                            {orders.length > 0 && (
                                <div className="mt-10" data-testid="account-orders">
                                    <h2 className="font-heading text-lg font-bold">eSIM & sigorta siparişlerim</h2>
                                    <div className="mt-4 space-y-3">
                                        {orders.map((o) => (
                                            <div
                                                key={o.id}
                                                className="card-surface flex flex-wrap items-center justify-between gap-4 p-5"
                                                data-testid={`account-order-${o.reference_code}`}
                                            >
                                                <div>
                                                    <p className="font-heading text-base font-extrabold">
                                                        {o.reference_code}
                                                    </p>
                                                    <p className="mt-1 text-sm text-muted-foreground">
                                                        {(o.items || []).map((i) => `${i.name} x${i.quantity}`).join(", ")}
                                                    </p>
                                                    <p className="mt-1 text-xs text-muted-foreground">
                                                        {formatDateTime(o.created_at)} ·{" "}
                                                        {o.status === "fulfilled"
                                                            ? "Teslim edildi"
                                                            : o.payment?.status === "paid"
                                                              ? "Hazırlanıyor"
                                                              : "Ödeme bekleniyor"}
                                                    </p>
                                                </div>
                                                <div className="flex items-center gap-4">
                                                    <span className="font-heading text-lg font-extrabold">
                                                        {formatMoney(o.price, o.currency)}
                                                    </span>
                                                    <Button
                                                        asChild
                                                        variant="secondary"
                                                        className="h-10 border border-border"
                                                        data-testid={`view-order-${o.reference_code}`}
                                                    >
                                                        <Link to={`/siparis/${o.reference_code}`}>Siparişi gör</Link>
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* SAVED TRAVELERS */}
                            <div className="mt-10" data-testid="account-saved-travelers">
                                <div className="flex flex-wrap items-end justify-between gap-3">
                                    <div>
                                        <h2 className="font-heading text-lg font-bold">Kayıtlı yolcularım</h2>
                                        <p className="mt-1 text-sm text-muted-foreground">
                                            Başvurularınızdaki yolcular burada saklanır; yeni başvuruda tek tıkla
                                            eklenir. Belgeler her başvuruda yeniden yüklenmelidir.
                                        </p>
                                    </div>
                                </div>

                                {(travelers || []).length === 0 ? (
                                    <div className="card-surface mt-4 p-6">
                                        <p className="text-sm text-muted-foreground">
                                            Henüz kayıtlı yolcu yok. İlk başvurunuzu tamamladığınızda yolcular
                                            otomatik olarak buraya eklenir.
                                        </p>
                                    </div>
                                ) : (
                                    <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                                        {travelers.map((t) => (
                                            <div
                                                key={t.id}
                                                className="card-surface flex items-start justify-between gap-3 p-5"
                                                data-testid={`saved-traveler-${t.id}`}
                                            >
                                                <div className="min-w-0">
                                                    <p className="flex items-center gap-1.5 font-heading text-base font-bold">
                                                        {t.applicant_type === "child" ? (
                                                            <Baby className="h-4 w-4 text-primary" />
                                                        ) : (
                                                            <User className="h-4 w-4 text-primary" />
                                                        )}
                                                        {t.first_name} {t.last_name}
                                                    </p>
                                                    <p className="mt-1.5 text-xs text-muted-foreground">
                                                        {t.birth_date ? `Doğum: ${t.birth_date}` : "Doğum tarihi yok"}
                                                    </p>
                                                    <p className="text-xs text-muted-foreground">
                                                        {t.passport_no ? `Pasaport: ${t.passport_no}` : "Pasaport bilgisi yok"}
                                                    </p>
                                                </div>
                                                <Button
                                                    variant="secondary"
                                                    className="h-9 shrink-0 border border-border text-destructive"
                                                    onClick={() => deleteTraveler(t.id)}
                                                    aria-label="Kayıtlı yolcuyu sil"
                                                    data-testid={`delete-saved-traveler-${t.id}`}
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* APPLICATIONS */}                            <div className="mt-10" data-testid="account-applications">
                                <h2 className="font-heading text-lg font-bold">Başvurularım</h2>
                                {(data?.applications || []).length === 0 ? (
                                    <div className="card-surface mt-4 p-8 text-center">
                                        <FileText className="mx-auto h-8 w-8 text-muted-foreground" />
                                        <p className="mt-3 text-sm text-muted-foreground">
                                            Bu e-posta ile kayıtlı başvuru bulunmuyor.
                                        </p>
                                        <Button asChild className="mt-5 h-11" data-testid="account-new-application">
                                            <Link to="/basvuru">Yeni başvuru yap</Link>
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="mt-4 space-y-4">
                                        {data.applications.map((a) => (
                                            <div
                                                key={a.id}
                                                className="card-surface p-6"
                                                data-testid={`account-application-${a.reference_code}`}
                                            >
                                                <div className="flex flex-wrap items-start justify-between gap-4">
                                                    <div>
                                                        <div className="flex flex-wrap items-center gap-2.5">
                                                            <span className="font-heading text-base font-extrabold">
                                                                {a.reference_code}
                                                            </span>
                                                            <StatusBadge status={a.status} />
                                                            <PaymentBadge status={a.payment?.status} />
                                                        </div>
                                                        <p className="mt-2 text-sm text-muted-foreground">
                                                            {a.visa_names.join(", ") || "Vize başvurusu"} ·{" "}
                                                            {a.traveler_count} yolcu · {formatDateTime(a.created_at)}
                                                        </p>
                                                        <p className="mt-1 text-sm text-muted-foreground">
                                                            {a.traveler_names.join(", ")}
                                                        </p>
                                                        {(a.missing_documents || []).length > 0 && (
                                                            <p
                                                                className="mt-2 flex items-center gap-1.5 text-sm font-medium text-[hsl(var(--status-warning))]"
                                                                data-testid={`account-missing-${a.reference_code}`}
                                                            >
                                                                <AlertTriangle className="h-4 w-4" />
                                                                {a.missing_documents.length} eksik belge var
                                                            </p>
                                                        )}
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="font-heading text-xl font-extrabold">
                                                            {formatMoney(a.price, a.currency)}
                                                        </p>
                                                    </div>
                                                </div>

                                                <div className="mt-5 flex flex-wrap gap-3">
                                                    <Button
                                                        asChild
                                                        variant="secondary"
                                                        className="h-10 border border-border"
                                                        data-testid={`track-application-${a.reference_code}`}
                                                    >
                                                        <Link
                                                            to={`/takip?kod=${a.reference_code}&soyad=${encodeURIComponent(
                                                                a.last_name || ""
                                                            )}`}
                                                        >
                                                            Başvuruyu takip et
                                                        </Link>
                                                    </Button>
                                                    <Button
                                                        onClick={() => reapply(a)}
                                                        className="h-10"
                                                        data-testid={`reapply-${a.reference_code}`}
                                                    >
                                                        <Copy className="mr-2 h-4 w-4" /> Bu bilgilerle yeni başvuru
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
}
