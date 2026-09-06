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
    ShieldCheck,
    ShoppingBag,
    Smartphone,
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
import { AccountLoginCard } from "../components/AccountLoginCard";

export default function MyAccount() {
    const navigate = useNavigate();
    const [token, setToken] = useState(customerAuth.token);
    const [data, setData] = useState(null);
    const [travelers, setTravelers] = useState([]);
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setMeta(
            "Başvurularım | Dubai Vize Hattı",
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
                        <AccountLoginCard onLogin={handleLogin} />
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
                            <div className="mt-10" data-testid="account-orders">
                                <div className="flex flex-wrap items-end justify-between gap-3">
                                    <div>
                                        <h2 className="font-heading text-lg font-bold">
                                            Satın aldığım ek hizmetler
                                        </h2>
                                        <p className="mt-1 text-sm text-muted-foreground">
                                            eSIM ve seyahat sigortası siparişleriniz. Vizeniz hazır olsa bile
                                            sonradan ekleyebilirsiniz.
                                        </p>
                                    </div>
                                    <Button
                                        asChild
                                        variant="secondary"
                                        className="h-10 border border-border"
                                        data-testid="account-open-cart"
                                    >
                                        <Link to="/sepet">
                                            <ShoppingBag className="mr-2 h-4 w-4" /> Sepetim
                                        </Link>
                                    </Button>
                                </div>

                                {orders.length === 0 ? (
                                    <div className="card-surface mt-4 p-6" data-testid="account-orders-empty">
                                        <p className="text-sm leading-6 text-muted-foreground">
                                            Henüz ek hizmet siparişiniz yok. Dubai eSIM ve seyahat sigortası
                                            paketlerini inceleyip sepete ekleyebilirsiniz; ikisini birlikte
                                            aldığınızda %10 indirim uygulanır.
                                        </p>
                                        <div className="mt-4 flex flex-wrap gap-3">
                                            <Button asChild className="h-10" data-testid="account-shop-esim">
                                                <Link to="/esim">
                                                    <Smartphone className="mr-2 h-4 w-4" /> eSIM paketleri
                                                </Link>
                                            </Button>
                                            <Button
                                                asChild
                                                variant="secondary"
                                                className="h-10 border border-border"
                                                data-testid="account-shop-insurance"
                                            >
                                                <Link to="/seyahat-sigortasi">
                                                    <ShieldCheck className="mr-2 h-4 w-4" /> Sigorta paketleri
                                                </Link>
                                            </Button>
                                        </div>
                                    </div>
                                ) : (
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
                                                        {o.application_reference
                                                            ? ` · Başvuru: ${o.application_reference}`
                                                            : ""}
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
                                )}
                            </div>

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
                                                        asChild
                                                        variant="secondary"
                                                        className="h-10 border border-border"
                                                        data-testid={`add-esim-${a.reference_code}`}
                                                    >
                                                        <Link to={`/esim?basvuru=${a.reference_code}`}>
                                                            <Smartphone className="mr-2 h-4 w-4" /> eSIM ekle
                                                        </Link>
                                                    </Button>
                                                    <Button
                                                        asChild
                                                        variant="secondary"
                                                        className="h-10 border border-border"
                                                        data-testid={`add-insurance-${a.reference_code}`}
                                                    >
                                                        <Link to={`/seyahat-sigortasi?basvuru=${a.reference_code}`}>
                                                            <ShieldCheck className="mr-2 h-4 w-4" /> Sigorta ekle
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
