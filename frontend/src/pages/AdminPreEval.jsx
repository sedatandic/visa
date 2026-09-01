import React, { useEffect, useState } from "react";
import { Gauge, Loader2, Mail, Phone, Users } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatDateTime } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";

const ANSWER_LABELS = {
    passport_validity: {
        "6_plus": "Pasaport 6+ ay geçerli",
        under_6: "Pasaport 6 aydan az",
        expired: "Pasaport süresi dolmuş",
    },
    visa_history: {
        recent: "Son 5 yılda vize aldı",
        old: "5 yıldan önce vize aldı",
        none: "İlk vize başvurusu",
    },
    refusal_history: {
        none: "Red kaydı yok",
        other_country: "Başka ülkeden red",
        uae: "BAE reddi var",
    },
    purpose: {
        tourism: "Turizm",
        family: "Aile ziyareti",
        business: "İş / ticaret",
        long_stay: "Uzun kalış",
        transit: "Transit",
    },
};

const LEVEL_BADGE = {
    high: "bg-primary/10 text-primary",
    medium: "bg-primary/10 text-primary",
    review: "bg-[hsl(38_92%_38%/0.14)] text-[hsl(38_92%_30%)]",
    low: "bg-[hsl(var(--brand-red)/0.10)] text-[hsl(var(--brand-red))]",
};

const LEVEL_LABEL = {
    high: "Yüksek",
    medium: "İyi",
    review: "İnceleme",
    low: "Riskli",
};

export default function AdminPreEval() {
    const [data, setData] = useState({ items: [], total: 0, leads: 0, average_score: 0 });
    const [loading, setLoading] = useState(true);
    const [onlyLeads, setOnlyLeads] = useState(false);

    const load = async (leadsOnly) => {
        setLoading(true);
        try {
            const { data: res } = await api.get("/admin/pre-evaluations", {
                params: { only_leads: leadsOnly },
            });
            setData(res);
        } catch (err) {
            toast.error(apiError(err, "Ön değerlendirmeler yüklenemedi."));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load(onlyLeads);
    }, [onlyLeads]);

    const stats = [
        { label: "Toplam değerlendirme", value: data.total, icon: Gauge },
        { label: "İletişim bırakan", value: data.leads, icon: Users },
        { label: "Ortalama skor", value: `${data.average_score || 0}%`, icon: Gauge },
    ];

    return (
        <AdminLayout
            title="Ön değerlendirmeler"
            description="Ana sayfadaki ücretsiz ön değerlendirme sihirbazından gelen sonuçlar ve potansiyel müşteriler."
        >
            <div data-testid="admin-pre-eval-page">
                <div className="grid gap-4 sm:grid-cols-3">
                    {stats.map(({ label, value, icon: Icon }) => (
                        <div key={label} className="card-surface p-5" data-testid={`admin-pre-eval-stat-${label}`}>
                            <div className="flex items-center gap-2.5">
                                <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                                    <Icon className="h-4 w-4 text-primary" />
                                </span>
                                <div>
                                    <p className="text-xs text-muted-foreground">{label}</p>
                                    <p className="text-lg font-bold">{value}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-6 flex flex-wrap items-center gap-2.5">
                    <Button
                        size="sm"
                        variant={onlyLeads ? "secondary" : "default"}
                        onClick={() => setOnlyLeads(false)}
                        data-testid="admin-pre-eval-filter-all"
                    >
                        Tümü
                    </Button>
                    <Button
                        size="sm"
                        variant={onlyLeads ? "default" : "secondary"}
                        onClick={() => setOnlyLeads(true)}
                        data-testid="admin-pre-eval-filter-leads"
                    >
                        Sadece iletişim bırakanlar
                    </Button>
                    <Button size="sm" variant="ghost" onClick={() => load(onlyLeads)} data-testid="admin-pre-eval-refresh">
                        Yenile
                    </Button>
                </div>

                {loading ? (
                    <div className="flex justify-center py-16">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                ) : data.items.length === 0 ? (
                    <div className="card-surface mt-6 p-10 text-center" data-testid="admin-pre-eval-empty">
                        <p className="text-sm font-semibold">Henüz kayıt yok</p>
                        <p className="mt-1 text-sm text-muted-foreground">
                            Ana sayfadaki ön değerlendirme sihirbazı kullanıldıkça sonuçlar burada listelenir.
                        </p>
                    </div>
                ) : (
                    <div className="mt-6 space-y-3">
                        {data.items.map((item) => (
                            <div key={item.id} className="card-surface p-5" data-testid={`admin-pre-eval-item-${item.id}`}>
                                <div className="flex flex-wrap items-start justify-between gap-4">
                                    <div className="min-w-0">
                                        <div className="flex flex-wrap items-center gap-2">
                                            <span className="text-sm font-bold">
                                                {item.name || "İsimsiz ziyaretçi"}
                                            </span>
                                            <span
                                                className={`rounded-full px-2 py-0.5 text-[11px] font-bold ${
                                                    LEVEL_BADGE[item.level] || LEVEL_BADGE.medium
                                                }`}
                                            >
                                                {item.score}% · {LEVEL_LABEL[item.level] || item.level}
                                            </span>
                                        </div>
                                        <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted-foreground">
                                            {item.email && (
                                                <a className="inline-flex items-center gap-1.5 hover:text-primary" href={`mailto:${item.email}`}>
                                                    <Mail className="h-3.5 w-3.5" /> {item.email}
                                                </a>
                                            )}
                                            {item.phone && (
                                                <a className="inline-flex items-center gap-1.5 hover:text-primary" href={`tel:${item.phone}`}>
                                                    <Phone className="h-3.5 w-3.5" /> {item.phone}
                                                </a>
                                            )}
                                            {!item.email && !item.phone && <span>İletişim bilgisi bırakılmadı</span>}
                                        </div>
                                        <div className="mt-3 flex flex-wrap gap-1.5">
                                            {Object.entries(item.answers || {}).map(([k, v]) =>
                                                v && ANSWER_LABELS[k]?.[v] ? (
                                                    <span
                                                        key={k}
                                                        className="rounded-md border border-border bg-background px-2 py-1 text-[11px] text-muted-foreground"
                                                    >
                                                        {ANSWER_LABELS[k][v]}
                                                    </span>
                                                ) : null
                                            )}
                                        </div>
                                    </div>
                                    <div className="text-right text-xs text-muted-foreground">
                                        <p>{formatDateTime(item.created_at)}</p>
                                        <p className="mt-1">{item.recommended_visa_type_id}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </AdminLayout>
    );
}
