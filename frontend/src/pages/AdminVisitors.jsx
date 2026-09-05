import React, { useCallback, useEffect, useState } from "react";
import { Globe2, Loader2, MapPin, RefreshCw, Users } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";
import { Switch } from "../components/ui/switch";

const RANGES = [
    { days: 1, label: "Bugün" },
    { days: 7, label: "7 gün" },
    { days: 30, label: "30 gün" },
    { days: 90, label: "90 gün" },
];

const StatCard = ({ icon: Icon, label, value, hint, testId }) => (
    <div className="card-surface p-5" data-testid={testId}>
        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
            <Icon className="h-5 w-5 text-primary" />
        </span>
        <p className="mt-3 font-heading text-2xl font-bold">{value}</p>
        <p className="text-sm font-semibold">{label}</p>
        {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
    </div>
);

const TopList = ({ title, rows, testId, emptyText }) => (
    <div className="card-surface p-5" data-testid={testId}>
        <h3 className="font-heading text-base font-bold">{title}</h3>
        {rows.length === 0 ? (
            <p className="mt-3 text-sm text-muted-foreground">{emptyText}</p>
        ) : (
            <ul className="mt-3 space-y-2">
                {rows.map((r) => {
                    const max = rows[0].count || 1;
                    return (
                        <li key={r.label} className="text-sm">
                            <div className="flex items-center justify-between gap-3">
                                <span className="truncate" title={r.label}>{r.label}</span>
                                <span className="shrink-0 font-bold">{r.count}</span>
                            </div>
                            <div className="mt-1 h-1.5 w-full rounded-full bg-muted">
                                <div
                                    className="h-1.5 rounded-full bg-primary"
                                    style={{ width: `${Math.round((r.count / max) * 100)}%` }}
                                />
                            </div>
                        </li>
                    );
                })}
            </ul>
        )}
    </div>
);

const formatTime = (iso) => {
    if (!iso) return "-";
    const d = new Date(iso);
    return d.toLocaleString("tr-TR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
};

export default function AdminVisitors() {
    const [days, setDays] = useState(30);
    const [includeBots, setIncludeBots] = useState(false);
    const [summary, setSummary] = useState(null);
    const [visits, setVisits] = useState([]);
    const [loading, setLoading] = useState(true);

    const load = useCallback(async () => {
        setLoading(true);
        try {
            const [s, v] = await Promise.all([
                api.get(`/admin/visits/summary?days=${days}`),
                api.get(`/admin/visits?limit=100&include_bots=${includeBots}`),
            ]);
            setSummary(s.data);
            setVisits(v.data.items || []);
        } catch (e) {
            toast.error(apiError(e, "Ziyaretçi verileri yüklenemedi."));
        } finally {
            setLoading(false);
        }
    }, [days, includeBots]);

    useEffect(() => {
        load();
    }, [load]);

    return (
        <AdminLayout
            title="Ziyaretçiler"
            description="Siteyi ziyaret eden kişilerin IP adresi, şehri, ülkesi ve gezdiği sayfalar. Konum bilgisi IP üzerinden tahmin edilir; VPN kullanımında şaşabilir."
            actions={
                <Button variant="secondary" className="h-10 border border-border" onClick={load} data-testid="visitors-refresh-button">
                    <RefreshCw className="mr-2 h-4 w-4" /> Yenile
                </Button>
            }
        >
            <div className="flex flex-wrap items-center gap-2" data-testid="visitors-range-tabs">
                {RANGES.map((r) => (
                    <button
                        key={r.days}
                        type="button"
                        onClick={() => setDays(r.days)}
                        data-testid={`visitors-range-${r.days}`}
                        className={`h-10 rounded-full border px-4 text-sm font-semibold transition-colors duration-150 ${
                            days === r.days
                                ? "border-primary bg-primary/10 text-primary"
                                : "border-border bg-card text-muted-foreground hover:text-foreground"
                        }`}
                    >
                        {r.label}
                    </button>
                ))}
                <label className="ml-auto flex items-center gap-2 text-sm font-medium">
                    <Switch checked={includeBots} onCheckedChange={setIncludeBots} data-testid="visitors-bots-switch" />
                    Botları da göster
                </label>
            </div>

            {loading && !summary ? (
                <div className="flex justify-center py-16">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <>
                    <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                        <StatCard
                            icon={Users}
                            label="Toplam görüntüleme"
                            value={summary?.total ?? 0}
                            hint={`Son ${summary?.days ?? days} gün`}
                            testId="visitors-stat-total"
                        />
                        <StatCard
                            icon={Users}
                            label="Tekil ziyaretçi (IP)"
                            value={summary?.unique_visitors ?? 0}
                            hint={`Bugün: ${summary?.unique_today ?? 0}`}
                            testId="visitors-stat-unique"
                        />
                        <StatCard
                            icon={Globe2}
                            label="Bugünkü görüntüleme"
                            value={summary?.total_today ?? 0}
                            hint="Gece yarısından itibaren"
                            testId="visitors-stat-today"
                        />
                        <StatCard
                            icon={MapPin}
                            label="Bot / tarayıcı robotu"
                            value={summary?.bots ?? 0}
                            hint="İstatistiklere dahil edilmez"
                            testId="visitors-stat-bots"
                        />
                    </div>

                    <div className="mt-6 grid gap-4 lg:grid-cols-3">
                        <TopList
                            title="Ülkeler"
                            rows={summary?.countries || []}
                            testId="visitors-top-countries"
                            emptyText="Henüz konum çözümlenmiş ziyaret yok."
                        />
                        <TopList
                            title="Şehirler"
                            rows={summary?.cities || []}
                            testId="visitors-top-cities"
                            emptyText="Henüz şehir bilgisi yok."
                        />
                        <TopList
                            title="En çok gezilen sayfalar"
                            rows={summary?.pages || []}
                            testId="visitors-top-pages"
                            emptyText="Henüz sayfa görüntüleme yok."
                        />
                    </div>

                    <div className="card-surface mt-6 overflow-hidden" data-testid="visitors-table">
                        <div className="flex items-center justify-between gap-3 border-b border-border p-5">
                            <h3 className="font-heading text-base font-bold">Son ziyaretler</h3>
                            <span className="text-xs text-muted-foreground">{visits.length} kayıt</span>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full min-w-[760px] text-sm">
                                <thead className="bg-[hsl(var(--cloud))] text-left text-xs uppercase tracking-wider text-muted-foreground">
                                    <tr>
                                        <th className="px-5 py-3">Zaman</th>
                                        <th className="px-5 py-3">IP adresi</th>
                                        <th className="px-5 py-3">Şehir</th>
                                        <th className="px-5 py-3">Ülke</th>
                                        <th className="px-5 py-3">Sayfa</th>
                                        <th className="px-5 py-3">Operatör / ISP</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {visits.length === 0 ? (
                                        <tr>
                                            <td colSpan={6} className="px-5 py-10 text-center text-muted-foreground">
                                                Henüz ziyaret kaydı yok. Siteyi ziyaret eden ilk kişiden sonra burada listelenir.
                                            </td>
                                        </tr>
                                    ) : (
                                        visits.map((v) => (
                                            <tr key={v.id} className="border-t border-border" data-testid={`visitor-row-${v.id}`}>
                                                <td className="whitespace-nowrap px-5 py-3 text-muted-foreground">{formatTime(v.created_at)}</td>
                                                <td className="font-mono-code whitespace-nowrap px-5 py-3">{v.ip || "-"}</td>
                                                <td className="px-5 py-3">{v.city || "-"}</td>
                                                <td className="whitespace-nowrap px-5 py-3">
                                                    {v.country ? `${v.country}${v.country_code ? ` (${v.country_code})` : ""}` : "-"}
                                                </td>
                                                <td className="max-w-[220px] truncate px-5 py-3 text-muted-foreground" title={v.path}>
                                                    {v.path}
                                                </td>
                                                <td className="max-w-[200px] truncate px-5 py-3 text-muted-foreground" title={v.isp}>
                                                    {v.isp || "-"}
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </AdminLayout>
    );
}
