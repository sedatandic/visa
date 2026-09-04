import React, { useEffect, useMemo, useState } from "react";
import { ExternalLink, Loader2, RefreshCw, Send, ShieldCheck, TrendingUp } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatDateTime, formatMoney } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { FileDropzone } from "../components/FileDropzone";
import { MonthlyProfitChart } from "../components/MonthlyProfitChart";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";

const TaskRow = ({ task, onIssued }) => {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");
    const [busy, setBusy] = useState(false);

    const issue = async () => {
        if (!file?.file_id) return toast.error("Poliçe PDF'ini yükleyin.");
        setBusy(true);
        try {
            const { data } = await api.post(`/admin/insurance-tasks/${task.id}/issue`, {
                policy_file_id: file.file_id,
                message,
                origin_url: window.location.origin,
            });
            toast.success("Poliçe müşteriye gönderildi.");
            onIssued(data.task);
        } catch (err) {
            toast.error(apiError(err, "Poliçe gönderilemedi."));
        } finally {
            setBusy(false);
        }
    };

    const customer = task.customer || {};

    return (
        <div className="card-surface p-5" data-testid={`insurance-task-${task.id}`}>
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                    <p className="font-heading text-sm font-bold">{task.plan_name}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                        {task.order_reference} · {task.quantity} kişi · {task.validity_days} gün ·{" "}
                        {formatDateTime(task.created_at)}
                    </p>
                </div>
                <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        task.status === "issued"
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-amber-100 text-amber-900"
                    }`}
                    data-testid={`insurance-task-status-${task.id}`}
                >
                    {task.status === "issued" ? "Gönderildi" : "Kesim bekliyor"}
                </span>
            </div>

            <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-3">
                <div>
                    <dt className="text-xs text-muted-foreground">Müşteri</dt>
                    <dd className="font-medium">{customer.full_name || "-"}</dd>
                </div>
                <div>
                    <dt className="text-xs text-muted-foreground">E-posta</dt>
                    <dd className="font-medium">{customer.email || "-"}</dd>
                </div>
                <div>
                    <dt className="text-xs text-muted-foreground">Telefon</dt>
                    <dd className="font-medium">{customer.phone || "-"}</dd>
                </div>
            </dl>

            {task.status !== "issued" && (
                <div className="mt-4 space-y-3">
                    <a
                        href={task.provider_link}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline"
                        data-testid={`insurance-provider-link-${task.id}`}
                    >
                        <ExternalLink className="h-4 w-4" /> {task.provider} üzerinde poliçeyi kes
                    </a>
                    <FileDropzone
                        label="Poliçe PDF"
                        hint="Sağlayıcıdan indirdiğiniz poliçeyi yükleyin, müşteriye otomatik gider."
                        docType="insurance_policy"
                        value={file}
                        onChange={setFile}
                        testId={`insurance-policy-upload-${task.id}`}
                        accept="application/pdf"
                    />
                    <Textarea
                        placeholder="Müşteriye eklenecek not (opsiyonel)"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        data-testid={`insurance-message-${task.id}`}
                    />
                    <Button
                        onClick={issue}
                        disabled={busy}
                        className="h-11"
                        data-testid={`insurance-issue-${task.id}`}
                    >
                        {busy ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                            <Send className="mr-2 h-4 w-4" />
                        )}
                        Poliçeyi müşteriye gönder
                    </Button>
                </div>
            )}
        </div>
    );
};

export default function AdminInsurance() {
    const [tasks, setTasks] = useState([]);
    const [report, setReport] = useState(null);
    const [monthly, setMonthly] = useState(null);
    const [loading, setLoading] = useState(true);

    const load = async () => {
        setLoading(true);
        try {
            const [tasksRes, reportRes, monthlyRes] = await Promise.all([
                api.get("/admin/insurance-tasks"),
                api.get("/admin/insurance-report"),
                api.get("/admin/profit-monthly?months=12"),
            ]);
            setTasks(tasksRes.data.items || []);
            setReport(reportRes.data);
            setMonthly(monthlyRes.data);
        } catch (err) {
            toast.error(apiError(err, "Veriler yüklenemedi."));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    const pending = useMemo(() => tasks.filter((t) => t.status !== "issued"), [tasks]);
    const issued = useMemo(() => tasks.filter((t) => t.status === "issued"), [tasks]);

    const onIssued = (task) =>
        setTasks((prev) => prev.map((t) => (t.id === task.id ? task : t)));

    return (
        <AdminLayout title="Sigorta Poliçeleri">
            <div className="flex items-center justify-between gap-3">
                <p className="text-sm text-muted-foreground">
                    Ödemesi alınan poliçeler otomatik kuyruğa düşer; müşteriye "hazırlanıyor"
                    bilgisi anında gider. PDF'i yüklediğinizde poliçe otomatik e-postalanır.
                </p>
                <Button
                    variant="secondary"
                    onClick={load}
                    className="h-10 border border-border"
                    data-testid="insurance-refresh"
                >
                    <RefreshCw className="mr-2 h-4 w-4" /> Yenile
                </Button>
            </div>

            {monthly && (
                <div className="mt-6">
                    <MonthlyProfitChart data={monthly} />
                </div>
            )}

            {report && (
                <div className="card-surface mt-6 overflow-hidden" data-testid="insurance-profit-panel">
                    <div className="flex items-center gap-2 border-b border-border px-5 py-4">
                        <TrendingUp className="h-4 w-4 text-primary" />
                        <h2 className="font-heading text-sm font-bold">
                            Kâr tablosu · kaynak {report.provider}
                        </h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="bg-muted/50 text-left text-xs uppercase text-muted-foreground">
                                <tr>
                                    <th className="px-5 py-3">Poliçe</th>
                                    <th className="px-3 py-3">Maliyet</th>
                                    <th className="px-3 py-3">Satış</th>
                                    <th className="px-3 py-3">Kâr</th>
                                    <th className="px-3 py-3">Marj</th>
                                    <th className="px-3 py-3">Satılan</th>
                                    <th className="px-3 py-3">Ciro</th>
                                    <th className="px-5 py-3">Toplam kâr</th>
                                </tr>
                            </thead>
                            <tbody>
                                {report.items.map((row) => (
                                    <tr
                                        key={row.id}
                                        className="border-t border-border"
                                        data-testid={`insurance-report-row-${row.id}`}
                                    >
                                        <td className="px-5 py-3 font-medium">{row.name}</td>
                                        <td className="px-3 py-3">{formatMoney(row.cost_try, "TRY")}</td>
                                        <td className="px-3 py-3">{formatMoney(row.price_try, "TRY")}</td>
                                        <td className="px-3 py-3 font-semibold text-emerald-700">
                                            {formatMoney(row.profit_try, "TRY")}
                                        </td>
                                        <td className="px-3 py-3">
                                            {row.margin_pct != null ? `%${row.margin_pct}` : "-"}
                                        </td>
                                        <td className="px-3 py-3">{row.sold_quantity}</td>
                                        <td className="px-3 py-3">{formatMoney(row.revenue_try, "TRY")}</td>
                                        <td className="px-5 py-3 font-semibold">
                                            {formatMoney(row.profit_total_try, "TRY")}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                            <tfoot>
                                <tr className="border-t border-border bg-muted/40 font-semibold">
                                    <td className="px-5 py-3">Toplam</td>
                                    <td className="px-3 py-3">
                                        {formatMoney(report.totals.cost_total_try, "TRY")}
                                    </td>
                                    <td className="px-3 py-3" colSpan={3} />
                                    <td className="px-3 py-3">{report.totals.sold_quantity}</td>
                                    <td className="px-3 py-3">
                                        {formatMoney(report.totals.revenue_try, "TRY")}
                                    </td>
                                    <td className="px-5 py-3" data-testid="insurance-total-profit">
                                        {formatMoney(report.totals.profit_total_try, "TRY")}
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
            )}

            <h2 className="mt-8 flex items-center gap-2 font-heading text-base font-bold">
                <ShieldCheck className="h-4 w-4 text-primary" /> Kesim bekleyen poliçeler (
                {pending.length})
            </h2>
            {loading ? (
                <div className="card-surface mt-4 flex items-center gap-2 p-6 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" /> Yükleniyor…
                </div>
            ) : pending.length === 0 ? (
                <div className="card-surface mt-4 p-6 text-sm text-muted-foreground" data-testid="insurance-empty">
                    Bekleyen poliçe yok. Ödeme alındığında görevler burada otomatik listelenir.
                </div>
            ) : (
                <div className="mt-4 space-y-4">
                    {pending.map((task) => (
                        <TaskRow key={task.id} task={task} onIssued={onIssued} />
                    ))}
                </div>
            )}

            {issued.length > 0 && (
                <>
                    <h2 className="mt-8 font-heading text-base font-bold">
                        Gönderilen poliçeler ({issued.length})
                    </h2>
                    <div className="mt-4 space-y-4">
                        {issued.map((task) => (
                            <TaskRow key={task.id} task={task} onIssued={onIssued} />
                        ))}
                    </div>
                </>
            )}
        </AdminLayout>
    );
}
