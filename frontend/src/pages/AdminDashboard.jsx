import React, { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    Banknote,
    ChevronLeft,
    ChevronRight,
    Clock,
    FileText,
    Loader2,
    Search,
    ThumbsUp,
} from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { OcrReportCard } from "../components/OcrReportCard";
import { STATUS_OPTIONS, STATUS_META, formatDateTime, formatMoney, setMeta } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { PaymentBadge, StatusBadge } from "../components/StatusBadge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";

const KPI = [
    { key: "today", label: "Bugün gelen", icon: FileText },
    { key: "payment_pending", label: "Ödeme bekleyen", icon: Clock },
    { key: "reviewing", label: "İnceleniyor", icon: Loader2 },
    { key: "approved", label: "Onaylanan", icon: ThumbsUp },
];

export default function AdminDashboard() {
    const navigate = useNavigate();
    const [stats, setStats] = useState(null);
    const [items, setItems] = useState([]);
    const [total, setTotal] = useState(0);
    const [pages, setPages] = useState(1);
    const [page, setPage] = useState(1);
    const [status, setStatus] = useState("all");
    const [paymentStatus, setPaymentStatus] = useState("all");
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setMeta("Yönetim Paneli | Dubai Vize Hattı", "Başvuru yönetim paneli.");
    }, []);

    const handleAuthError = (err) => {
        if (err?.response?.status === 401) {
            localStorage.removeItem("dv_admin_token");
            navigate("/admin/giris");
            return true;
        }
        return false;
    };

    const load = useCallback(async () => {
        setLoading(true);
        try {
            const [statsRes, listRes] = await Promise.all([
                api.get("/admin/stats"),
                api.get("/admin/applications", {
                    params: { status, payment_status: paymentStatus, q: query || undefined, page, limit: 20 },
                }),
            ]);
            setStats(statsRes.data);
            setItems(listRes.data.items);
            setTotal(listRes.data.total);
            setPages(listRes.data.pages);
        } catch (err) {
            if (!handleAuthError(err)) toast.error(apiError(err, "Veriler yüklenemedi."));
        } finally {
            setLoading(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [status, paymentStatus, query, page]);

    useEffect(() => {
        load();
    }, [load]);

    return (
        <AdminLayout title="Başvurular" description="Tüm vize başvurularını filtreleyin, detaylarını görüntüleyin ve durumlarını güncelleyin.">
            <div data-testid="admin-dashboard">
                {/* KPI */}
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
                    {KPI.map(({ key, label, icon: Icon }) => (
                        <div key={key} className="card-surface p-5" data-testid={`admin-kpi-${key}`}>
                            <div className="flex items-center justify-between">
                                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</span>
                                <Icon className="h-4 w-4 text-primary" />
                            </div>
                            <p className="mt-3 font-heading text-3xl font-bold">{stats?.[key] ?? "-"}</p>
                        </div>
                    ))}
                    <div className="card-surface p-5" data-testid="admin-kpi-revenue">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Tahsil edilen</span>
                            <Banknote className="h-4 w-4 text-primary" />
                        </div>
                        <p className="mt-3 font-heading text-2xl font-bold">
                            {stats ? formatMoney(stats.revenue) : "-"}
                        </p>
                    </div>
                </div>

                {/* BEKLEYEN WHATSAPP ISLERI */}
                {stats && (stats.wa_pending_documents > 0 || stats.wa_needs_human > 0) && (
                    <div
                        className="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-primary/30 bg-primary/[0.06] p-4"
                        data-testid="admin-wa-alert"
                    >
                        <p className="text-sm leading-6">
                            <span className="font-heading font-bold">WhatsApp'ta bekleyen işlem var:</span>{" "}
                            {stats.wa_pending_documents > 0 && (
                                <span data-testid="admin-wa-alert-documents">
                                    {stats.wa_pending_documents} belge eşleştirme bekliyor
                                </span>
                            )}
                            {stats.wa_pending_documents > 0 && stats.wa_needs_human > 0 && " · "}
                            {stats.wa_needs_human > 0 && (
                                <span data-testid="admin-wa-alert-handoffs">
                                    {stats.wa_needs_human} konuşma temsilci istiyor
                                </span>
                            )}
                        </p>
                        <Button
                            className="h-10"
                            onClick={() => navigate("/admin/whatsapp")}
                            data-testid="admin-wa-alert-button"
                        >
                            WhatsApp panelini aç
                        </Button>
                    </div>
                )}

                {/* OCR PERFORMANS RAPORU */}
                <OcrReportCard />

                {/* FILTERS */}
                <div className="card-surface mt-7 flex flex-col gap-4 p-5 lg:flex-row lg:items-end">
                    <div className="flex-1">
                        <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Ara</label>
                        <div className="relative mt-2">
                            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                                value={query}
                                onChange={(e) => {
                                    setPage(1);
                                    setQuery(e.target.value);
                                }}
                                placeholder="Takip kodu, ad soyad, e-posta veya pasaport no"
                                className="pl-9"
                                data-testid="admin-applications-search-input"
                            />
                        </div>
                    </div>
                    <div className="w-full lg:w-52">
                        <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Durum</label>
                        <Select
                            value={status}
                            onValueChange={(v) => {
                                setPage(1);
                                setStatus(v);
                            }}
                        >
                            <SelectTrigger className="mt-2" data-testid="admin-status-filter-select">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Tümü</SelectItem>
                                {STATUS_OPTIONS.map((s) => (
                                    <SelectItem key={s} value={s}>{STATUS_META[s]?.label || s}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="w-full lg:w-48">
                        <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Ödeme</label>
                        <Select
                            value={paymentStatus}
                            onValueChange={(v) => {
                                setPage(1);
                                setPaymentStatus(v);
                            }}
                        >
                            <SelectTrigger className="mt-2" data-testid="admin-payment-filter-select">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">Tümü</SelectItem>
                                <SelectItem value="paid">Ödendi</SelectItem>
                                <SelectItem value="pending">Ödeme bekliyor</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>

                {/* TABLE */}
                <div className="card-surface mt-6 overflow-hidden">
                    <div className="flex items-center justify-between border-b border-border px-5 py-4">
                        <p className="text-sm font-semibold">{total} başvuru</p>
                        {loading && <Loader2 className="h-4 w-4 animate-spin text-primary" />}
                    </div>

                    {items.length === 0 && !loading ? (
                        <div className="p-10 text-center" data-testid="admin-empty-state">
                            <p className="text-sm font-semibold">Kayıt bulunamadı</p>
                            <p className="mt-1 text-sm text-muted-foreground">Filtreleri değiştirerek tekrar deneyin.</p>
                        </div>
                    ) : (
                        <>
                            {/* desktop table */}
                            <div className="hidden overflow-x-auto md:block">
                                <table className="w-full text-left text-sm" data-testid="admin-applications-table">
                                    <thead className="bg-[hsl(var(--cloud))] text-xs uppercase tracking-wider text-muted-foreground">
                                        <tr>
                                            <th className="px-5 py-3 font-semibold">Takip Kodu</th>
                                            <th className="px-5 py-3 font-semibold">Başvuru Sahibi</th>
                                            <th className="px-5 py-3 font-semibold">Vize</th>
                                            <th className="px-5 py-3 font-semibold">Tutar</th>
                                            <th className="px-5 py-3 font-semibold">Durum</th>
                                            <th className="px-5 py-3 font-semibold">Ödeme</th>
                                            <th className="px-5 py-3 font-semibold">Tarih</th>
                                            <th className="px-5 py-3 font-semibold" />
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {items.map((a) => (
                                            <tr key={a.id} className="border-t border-border transition-colors hover:bg-muted/50">
                                                <td className="px-5 py-3.5 font-heading font-semibold">{a.reference_code}</td>
                                                <td className="px-5 py-3.5">
                                                    <p className="font-medium">{a.contact?.full_name || `${a.applicant?.first_name || ""} ${a.applicant?.last_name || ""}`}</p>
                                                    <p className="text-xs text-muted-foreground">{a.contact?.email || a.applicant?.email}</p>
                                                </td>
                                                <td className="px-5 py-3.5 text-muted-foreground">
                                                    {a.visa_type_name}
                                                    <span className="ml-1.5 rounded-full bg-muted px-1.5 py-0.5 text-[11px] font-semibold">
                                                        {(a.travelers || []).length || 1} yolcu
                                                    </span>
                                                </td>
                                                <td className="px-5 py-3.5 font-medium">{formatMoney(a.price, a.currency)}</td>
                                                <td className="px-5 py-3.5"><StatusBadge status={a.status} /></td>
                                                <td className="px-5 py-3.5"><PaymentBadge status={a.payment?.status} /></td>
                                                <td className="px-5 py-3.5 text-xs text-muted-foreground">{formatDateTime(a.created_at)}</td>
                                                <td className="px-5 py-3.5 text-right">
                                                    <Button
                                                        variant="secondary"
                                                        className="h-9 border border-border"
                                                        onClick={() => navigate(`/admin/basvuru/${a.id}`)}
                                                        data-testid={`admin-view-application-${a.reference_code}`}
                                                    >
                                                        Detay
                                                    </Button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            {/* mobile cards */}
                            <div className="divide-y divide-border md:hidden">
                                {items.map((a) => (
                                    <div key={a.id} className="p-5">
                                        <div className="flex items-start justify-between gap-3">
                                            <div>
                                                <p className="font-heading font-bold">{a.reference_code}</p>
                                                <p className="text-sm">{a.contact?.full_name || `${a.applicant?.first_name || ""} ${a.applicant?.last_name || ""}`}</p>
                                                <p className="text-xs text-muted-foreground">{a.visa_type_name} · {(a.travelers || []).length || 1} yolcu</p>
                                            </div>
                                            <span className="font-medium">{formatMoney(a.price, a.currency)}</span>
                                        </div>
                                        <div className="mt-3 flex flex-wrap gap-2">
                                            <StatusBadge status={a.status} />
                                            <PaymentBadge status={a.payment?.status} />
                                        </div>
                                        <Button
                                            variant="secondary"
                                            className="mt-4 h-10 w-full border border-border"
                                            onClick={() => navigate(`/admin/basvuru/${a.id}`)}
                                        >
                                            Detay
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}

                    {pages > 1 && (
                        <div className="flex items-center justify-between border-t border-border px-5 py-4">
                            <Button
                                variant="secondary"
                                className="h-10 border border-border"
                                disabled={page <= 1}
                                onClick={() => setPage((p) => p - 1)}
                                data-testid="admin-prev-page"
                            >
                                <ChevronLeft className="mr-1 h-4 w-4" /> Önceki
                            </Button>
                            <span className="text-sm text-muted-foreground">Sayfa {page} / {pages}</span>
                            <Button
                                variant="secondary"
                                className="h-10 border border-border"
                                disabled={page >= pages}
                                onClick={() => setPage((p) => p + 1)}
                                data-testid="admin-next-page"
                            >
                                Sonraki <ChevronRight className="ml-1 h-4 w-4" />
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </AdminLayout>
    );
}
