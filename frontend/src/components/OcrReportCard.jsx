import React, { useEffect, useState } from "react";
import { Gauge, RefreshCw, TriangleAlert } from "lucide-react";
import { api } from "../lib/api";
import { Button } from "./ui/button";
import { Skeleton } from "./ui/skeleton";
import { Progress } from "./ui/progress";

const seconds = (ms) => (ms ? `${(ms / 1000).toFixed(1)} sn` : "-");

/**
 * Pasaport OCR performans karti: "tek pasaport fotografiyla form ne kadar
 * hizli doluyor, hangi alanlar okunamiyor" sorusunu yanitlar.
 */
export const OcrReportCard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    const load = async () => {
        setLoading(true);
        try {
            const res = await api.get("/admin/ocr-report", { params: { days: 30 } });
            setData(res.data);
        } catch {
            setData(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    if (loading) {
        return <Skeleton className="mt-7 h-64 rounded-[var(--radius-lg)]" data-testid="ocr-report-loading" />;
    }

    return (
        <section className="card-surface mt-7 p-5 sm:p-6" data-testid="admin-ocr-report">
            <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2">
                        <Gauge className="h-4 w-4 text-primary" aria-hidden="true" />
                        <h2 className="font-heading text-lg font-bold">Pasaport okuma performansı</h2>
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">
                        Son 30 günde tek pasaport fotoğrafıyla formun ne kadar hızlı dolduğu ve hangi
                        alanların okunamadığı.
                    </p>
                </div>
                <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={load}
                    data-testid="ocr-report-refresh-button"
                >
                    <RefreshCw className="mr-1.5 h-3.5 w-3.5" /> Yenile
                </Button>
            </div>

            {!data || data.total === 0 ? (
                <p className="mt-6 text-sm text-muted-foreground" data-testid="ocr-report-empty">
                    Henüz ölçüm yok. Bir başvuruda pasaport yüklenip "Pasaportla tek adımda doldur"
                    kullanıldığında ölçüm burada görünecek.
                </p>
            ) : (
                <>
                    <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        {[
                            { label: "Ortalama süre", value: seconds(data.avg_ms), testId: "ocr-avg" },
                            { label: "Tipik (medyan)", value: seconds(data.p50_ms), testId: "ocr-p50" },
                            { label: "Okuma başarısı", value: `%${data.success_rate}`, testId: "ocr-success" },
                            {
                                label: "Zorunlu alanlar tam",
                                value: `%${data.core_complete_rate}`,
                                testId: "ocr-core",
                            },
                        ].map(({ label, value, testId }) => (
                            <div key={label} className="rounded-[var(--radius)] border border-border/70 bg-secondary/40 p-4">
                                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                    {label}
                                </p>
                                <p className="tabular mt-2 font-heading text-2xl font-extrabold" data-testid={testId}>
                                    {value}
                                </p>
                            </div>
                        ))}
                    </div>

                    <div className="mt-6 grid gap-6 lg:grid-cols-2">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                Alan doluluk oranı ({data.total} ölçüm)
                            </p>
                            <ul className="mt-3 space-y-2.5" data-testid="ocr-field-rates">
                                {(data.fields || []).map((f) => (
                                    <li key={f.key} className="flex items-center gap-3">
                                        <span className="w-36 shrink-0 truncate text-sm">
                                            {f.label}
                                            {f.core && <span className="ml-1 text-xs text-muted-foreground">(zorunlu)</span>}
                                        </span>
                                        <Progress value={f.fill_rate} className="h-2 flex-1" />
                                        <span className="tabular w-10 shrink-0 text-right text-sm font-semibold">
                                            %{f.fill_rate}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div>
                            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                En sık okunamayan alanlar
                            </p>
                            {(data.top_missing || []).length === 0 ? (
                                <p className="mt-3 text-sm text-muted-foreground">
                                    Tüm alanlar sorunsuz okunuyor.
                                </p>
                            ) : (
                                <ul className="mt-3 space-y-2" data-testid="ocr-top-missing">
                                    {data.top_missing.map((f) => (
                                        <li
                                            key={f.key}
                                            className="flex items-center gap-2 rounded-[var(--radius)] border border-border/70 bg-[hsl(var(--panel-2))] px-3 py-2 text-sm"
                                        >
                                            <TriangleAlert
                                                className="h-3.5 w-3.5 shrink-0 text-[hsl(var(--status-warning))]"
                                                aria-hidden="true"
                                            />
                                            <span className="flex-1">{f.label}</span>
                                            <span className="tabular text-xs font-semibold text-muted-foreground">
                                                %{f.fill_rate} dolu
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                            )}

                            <p className="mt-5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                Son ölçümler
                            </p>
                            <ul className="mt-2 space-y-1.5 text-xs text-muted-foreground" data-testid="ocr-recent">
                                {(data.recent || []).slice(0, 5).map((r, i) => (
                                    <li key={i} className="flex items-center justify-between gap-3">
                                        <span>{r.at ? new Date(r.at).toLocaleString("tr-TR") : "-"}</span>
                                        <span className="tabular">
                                            {seconds(r.duration_ms)} · {r.ok ? "okundu" : r.reason || "okunamadı"}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </>
            )}
        </section>
    );
};
