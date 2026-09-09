import React, { useEffect, useMemo, useState } from "react";
import { AlertTriangle, ExternalLink, Loader2, MessageCircle, Receipt, RefreshCw, Search, Send, ShieldAlert, ShieldCheck, TrendingUp, Wallet } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatDateTime, formatMoney } from "../lib/site";
import { formatPhone } from "../lib/phone";
import { AdminLayout } from "../components/AdminLayout";
import { FileDropzone } from "../components/FileDropzone";
import { MonthlyProfitChart } from "../components/MonthlyProfitChart";
import { Button } from "../components/ui/button";
import { Switch } from "../components/ui/switch";
import { Textarea } from "../components/ui/textarea";

const TaskRow = ({ task, onIssued, providerReady }) => {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");
    const [busy, setBusy] = useState(false);
    const [apiBusy, setApiBusy] = useState(false);

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

    const issueViaProvider = async () => {
        setApiBusy(true);
        try {
            const { data } = await api.post(`/admin/insurance-tasks/${task.id}/issue-provider`);
            toast.success("Poliçe Tamamliyo üzerinden kesildi ve müşteriye gönderildi.");
            onIssued(data.task);
        } catch (err) {
            toast.error(apiError(err, "Poliçe kesilemedi."));
        } finally {
            setApiBusy(false);
        }
    };

    const customer = task.customer || {};
    const insured = task.insured || [];

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
                            : task.status === "waiting_payment" || task.status === "payment_review"
                              ? "bg-destructive/10 text-destructive"
                              : "bg-amber-100 text-amber-900"
                    }`}
                    data-testid={`insurance-task-status-${task.id}`}
                >
                    {task.status === "issued"
                        ? "Gönderildi"
                        : task.status === "waiting_payment"
                          ? "Ödeme bekliyor"
                          : task.status === "payment_review"
                            ? "Ödeme doğrulaması bekliyor"
                            : "Kesim bekliyor"}
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
                    <dd className="font-medium">{formatPhone(customer.phone) || "-"}</dd>
                </div>
            </dl>

            {insured.length > 0 && (
                <div className="mt-3 rounded-xl border border-border bg-muted/40 p-3" data-testid={`insurance-insured-${task.id}`}>
                    <p className="text-xs font-semibold text-muted-foreground">Sigortalılar</p>
                    <ul className="mt-1.5 space-y-1 text-sm">
                        {insured.map((person, i) => (
                            <li key={`${task.id}-ins-${i}`} className="font-medium">
                                {person.full_name || "-"} · {person.tc_kimlik_no || "TC yok"} ·{" "}
                                {person.birth_date || "-"}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {task.provider_error && (
                <p
                    className="mt-3 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-xs font-semibold text-destructive"
                    data-testid={`insurance-provider-error-${task.id}`}
                >
                    Tamamliyo hatası: {task.provider_error}
                </p>
            )}

            {task.status === "issued" && task.whatsapp?.link && (
                <div
                    className="mt-4 rounded-xl border border-[hsl(var(--brand-green))]/30 bg-[hsl(var(--brand-green))]/[0.07] p-4"
                    data-testid={`insurance-whatsapp-${task.id}`}
                >
                    <p className="text-sm font-semibold">
                        {task.whatsapp.status === "sent"
                            ? "WhatsApp'tan gönderildi"
                            : "WhatsApp mesajı hazır"}
                    </p>
                    <p className="mt-1 text-xs leading-5 text-muted-foreground">
                        {task.whatsapp.status === "sent"
                            ? `Poliçe bağlantısı ${task.whatsapp.phone} numarasına iletildi.`
                            : `WhatsApp API canlı olmadığı için mesaj otomatik gitmedi. Butona dokunun, poliçe bağlantılı mesaj ${task.whatsapp.phone} için hazır açılır.`}
                    </p>
                    {task.whatsapp.status !== "sent" && (
                        <Button
                            asChild
                            className="mt-3 h-11 text-white hover:opacity-90"
                            style={{ backgroundColor: "#25D366" }}
                            data-testid={`insurance-whatsapp-send-${task.id}`}
                        >
                            <a href={task.whatsapp.link} target="_blank" rel="noreferrer">
                                <MessageCircle className="mr-2 h-4 w-4" /> WhatsApp'tan poliçe mesajı gönder
                            </a>
                        </Button>
                    )}
                </div>
            )}

            {task.status !== "issued" && (
                <div className="mt-4 space-y-3">
                    {providerReady && (
                        <div className="rounded-xl border border-primary/30 bg-primary/[0.05] p-4">
                            <p className="text-sm font-semibold">Tamamliyo API ile otomatik kes</p>
                            <p className="mt-1 text-xs leading-5 text-muted-foreground">
                                Teklif → cari ödeme onayı → poliçe → PDF adımları tek tıkla çalışır; poliçe
                                müşteriye e-postalanır. Yarıda kalan adımlar tekrar denendiğinde kaldığı yerden
                                devam eder.
                            </p>
                            <Button
                                onClick={issueViaProvider}
                                disabled={apiBusy}
                                className="mt-3 h-11"
                                data-testid={`insurance-issue-provider-${task.id}`}
                            >
                                {apiBusy ? (
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                ) : (
                                    <ShieldCheck className="mr-2 h-4 w-4" />
                                )}
                                Tamamliyo'dan poliçeyi kes ve gönder
                            </Button>
                        </div>
                    )}
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

const ProviderPanel = ({ status, onChange }) => {
    const [syncing, setSyncing] = useState(false);
    const [toggling, setToggling] = useState(false);
    const [probeId, setProbeId] = useState("220");
    const [probing, setProbing] = useState(false);
    const [probe, setProbe] = useState(null);

    const checkProduct = async () => {
        setProbing(true);
        try {
            const { data } = await api.get(`/admin/insurance/product-check?urun_id=${Number(probeId)}`);
            setProbe(data);
            if (data.available)
                toast.success(`${data.urun_id} kodu satışta: maliyet ${data.cost_try} ₺.`);
            else toast.warning(`${data.urun_id} kodu henüz açık değil.`);
        } catch (err) {
            toast.error(apiError(err, "Ürün kodu sorgulanamadı."));
        } finally {
            setProbing(false);
        }
    };

    const sync = async () => {
        setSyncing(true);
        try {
            const { data } = await api.post("/admin/insurance/sync-prices");
            const failed = (data.errors || []).length;
            toast[failed ? "warning" : "success"](
                `${(data.rows || []).length} poliçe fiyatı güncellendi${failed ? `, ${failed} hata` : ""}.`
            );
            onChange();
        } catch (err) {
            toast.error(apiError(err, "Fiyatlar güncellenemedi."));
        } finally {
            setSyncing(false);
        }
    };

    const toggleAuto = async (enabled) => {
        setToggling(true);
        try {
            await api.post("/admin/insurance/auto-issue", { enabled });
            toast.success(
                enabled
                    ? "Otomatik poliçe kesimi açıldı: ödeme alındığında poliçe kendiliğinden kesilir."
                    : "Otomatik poliçe kesimi kapatıldı: poliçeleri panelden keseceksiniz."
            );
            onChange();
        } catch (err) {
            toast.error(apiError(err, "Ayar kaydedilemedi."));
        } finally {
            setToggling(false);
        }
    };

    return (
        <div className="card-surface mt-6 p-5" data-testid="insurance-provider-panel">
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                    <h2 className="flex items-center gap-2 font-heading text-sm font-bold">
                        <ShieldCheck className="h-4 w-4 text-primary" /> Tamamliyo bağlantısı
                    </h2>
                    <p className="mt-1 text-xs leading-5 text-muted-foreground">
                        Maliyetler günlük çekilir, satış fiyatı %{Math.round((status.markup - 1) * 100)} kâr
                        marjıyla hesaplanır. Poliçe bedeli her kesimde Tamamliyo partner cari
                        bakiyenizden düşülür (odemeTipi=3); sunucuda kart veya CVV bilgisi tutulmaz.
                    </p>
                    <p className="mt-1 text-xs leading-5 text-amber-700" data-testid="insurance-payment-note">
                        Cari bakiye yetmezse poliçe kesilemez; sipariş kuyruğa alınır ve bakiye
                        yüklenince kendiliğinden kesilip müşteriye gönderilir.
                    </p>
                </div>
                <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        status.configured ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-900"
                    }`}
                    data-testid="insurance-provider-state"
                >
                    {status.configured ? "Bağlı" : "API bilgisi yok"}
                </span>
            </div>

            <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
                <div>
                    <dt className="text-xs text-muted-foreground">Son fiyat senkronu</dt>
                    <dd className="font-medium" data-testid="insurance-last-sync">
                        {status.last_sync_at ? formatDateTime(status.last_sync_at) : "Henüz yapılmadı"}
                    </dd>
                </div>
                <div>
                    <dt className="text-xs text-muted-foreground">Ürün kodu</dt>
                    <dd className="font-medium">{status.urun_id}</dd>
                </div>
                <div>
                    <dt className="text-xs text-muted-foreground">Otomatik poliçe kesimi</dt>
                    <dd className="mt-1 flex items-center gap-2">
                        <Switch
                            checked={!!status.auto_issue}
                            disabled={toggling || !status.configured}
                            onCheckedChange={toggleAuto}
                            data-testid="insurance-auto-issue-switch"
                        />
                        <span className="text-xs font-semibold">
                            {status.auto_issue ? "Açık" : "Kapalı (elle kesilir)"}
                        </span>
                    </dd>
                </div>
            </dl>

            {(status.last_errors || []).length > 0 && (
                <p
                    className="mt-3 rounded-lg border border-destructive/30 bg-destructive/5 p-3 text-xs font-semibold text-destructive"
                    data-testid="insurance-provider-errors"
                >
                    Son senkron hataları: {status.last_errors.map((e) => `${e.product_id}: ${e.error}`).join(" · ")}
                </p>
            )}

            <Button
                onClick={sync}
                disabled={syncing || !status.configured}
                className="mt-4 h-10"
                data-testid="insurance-sync-prices"
            >
                {syncing ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                    <RefreshCw className="mr-2 h-4 w-4" />
                )}
                Fiyatları Tamamliyo'dan güncelle
            </Button>

            <div className="mt-4 rounded-xl border border-border bg-muted/30 p-3">
                <p className="text-xs font-semibold">Ürün kodu satışa açık mı?</p>
                <p className="mt-1 text-xs leading-5 text-muted-foreground">
                    Tamamliyo'ya fiyat sorgusu gönderir; poliçe kesmez, ücret çıkarmaz. Kod açıldığında
                    sunucudaki <code>TAMAMLIYO_URUN_ID</code> değeri güncellenip fiyatlar senkronlanır.
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-2">
                    <input
                        type="number"
                        value={probeId}
                        onChange={(e) => setProbeId(e.target.value)}
                        className="h-10 w-28 rounded-lg border border-border bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                        data-testid="insurance-product-check-input"
                    />
                    <Button
                        variant="secondary"
                        onClick={checkProduct}
                        disabled={probing || !status.configured}
                        className="h-10 border border-border"
                        data-testid="insurance-product-check"
                    >
                        {probing ? (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                            <Search className="mr-2 h-4 w-4" />
                        )}
                        Kodu sorgula
                    </Button>
                </div>
                {probe && (
                    <p
                        className={`mt-2 text-xs font-semibold ${
                            probe.available ? "text-emerald-700" : "text-amber-700"
                        }`}
                        data-testid="insurance-product-check-result"
                    >
                        {probe.available
                            ? `${probe.urun_id} · ${probe.product_name || "ürün"} satışta: maliyet ${
                                  probe.cost_try
                              } ₺, önerilen satış ${probe.price_try} ₺.`
                            : `${probe.urun_id} kodu kullanılamıyor: ${probe.error}`}
                    </p>
                )}
            </div>
        </div>
    );
};

const MARGIN_STATES = {
    ok: { label: "Kârlı", cls: "bg-emerald-100 text-emerald-800" },
    low: { label: "İnce marj", cls: "bg-amber-100 text-amber-900" },
    loss: { label: "Zarar", cls: "bg-destructive/10 text-destructive" },
    unknown: { label: "Maliyet yok", cls: "bg-muted text-muted-foreground" },
};

const EVENT_LABELS = {
    price_fixed: "Fiyat otomatik yükseltildi",
    low_margin: "Marj eşiğin altına düştü",
    charge_loss: "Çekim satış tutarını aştı",
};

const MarginPanel = ({ data, onChange }) => {
    const [busy, setBusy] = useState(false);
    const items = data.items || [];
    const events = data.events || [];
    const risky = items.filter((row) => row.state === "loss" || row.state === "low");

    const check = async () => {
        setBusy(true);
        try {
            const { data: res } = await api.post("/admin/insurance/margin/check");
            const fixed = res.result?.fixed?.length || 0;
            const low = res.result?.low_margin?.length || 0;
            if (fixed) toast.warning(`${fixed} poliçenin satış fiyatı otomatik yükseltildi.`);
            else if (low) toast.warning(`${low} poliçede marj %${data.low_margin_pct} altında.`);
            else toast.success("Tüm poliçeler kârlı, düzeltme gerekmedi.");
            onChange();
        } catch (err) {
            toast.error(apiError(err, "Kâr kontrolü yapılamadı."));
        } finally {
            setBusy(false);
        }
    };

    return (
        <div
            className={`card-surface mt-6 border p-5 ${
                risky.length ? "border-amber-300 bg-amber-50/60" : "border-border"
            }`}
            data-testid="insurance-margin-panel"
        >
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                    <h2 className="flex items-center gap-2 font-heading text-sm font-bold">
                        <ShieldAlert className="h-4 w-4 text-primary" /> Kâr koruması
                    </h2>
                    <p className="mt-1 max-w-2xl text-xs leading-5 text-muted-foreground">
                        Bir poliçenin maliyeti satış fiyatına ulaşırsa satış fiyatı otomatik olarak
                        maliyet × {data.markup} (10 ₺'ye yuvarlı) yapılır ve size e-posta + WhatsApp
                        uyarısı gider. Marj %{data.low_margin_pct} altına düşerse fiyata dokunulmaz,
                        yalnızca uyarılırsınız. Kesim anında karttan çekilen tutar müşteriden alınan
                        tutarı aşarsa da uyarı gelir.
                    </p>
                </div>
                <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        risky.length ? "bg-amber-100 text-amber-900" : "bg-emerald-100 text-emerald-800"
                    }`}
                    data-testid="insurance-margin-state"
                >
                    {risky.length ? `${risky.length} poliçe riskli` : "Tüm poliçeler kârlı"}
                </span>
            </div>

            <div className="mt-4 overflow-x-auto">
                <table className="w-full text-sm">
                    <thead className="text-left text-xs uppercase text-muted-foreground">
                        <tr>
                            <th className="py-2 pr-3">Poliçe</th>
                            <th className="py-2 pr-3">Maliyet</th>
                            <th className="py-2 pr-3">Satış</th>
                            <th className="py-2 pr-3">Kâr</th>
                            <th className="py-2 pr-3">Marj</th>
                            <th className="py-2">Durum</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border" data-testid="insurance-margin-rows">
                        {items.map((row) => {
                            const tone = MARGIN_STATES[row.state] || MARGIN_STATES.unknown;
                            return (
                                <tr key={row.id} data-testid={`insurance-margin-row-${row.id}`}>
                                    <td className="py-2 pr-3 font-medium">{row.name}</td>
                                    <td className="py-2 pr-3">{formatMoney(row.cost_try, "TRY")}</td>
                                    <td className="py-2 pr-3">{formatMoney(row.price_try, "TRY")}</td>
                                    <td
                                        className={`py-2 pr-3 font-semibold ${
                                            row.profit_try > 0 ? "text-emerald-700" : "text-destructive"
                                        }`}
                                    >
                                        {formatMoney(row.profit_try, "TRY")}
                                    </td>
                                    <td className="py-2 pr-3">
                                        {row.margin_pct != null ? `%${row.margin_pct}` : "-"}
                                    </td>
                                    <td className="py-2">
                                        <span className={`rounded-full px-2 py-1 text-xs font-semibold ${tone.cls}`}>
                                            {tone.label}
                                        </span>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {events.length > 0 ? (
                <ul className="mt-4 space-y-2" data-testid="insurance-margin-events">
                    {events.slice(0, 6).map((event, index) => (
                        <li
                            key={`${event.product_id}-${event.at}-${index}`}
                            className="flex flex-wrap items-center gap-2 rounded-lg border border-border bg-background px-3 py-2 text-xs"
                        >
                            <AlertTriangle className="h-3.5 w-3.5 text-amber-600" />
                            <span className="font-semibold">{EVENT_LABELS[event.kind] || event.kind}</span>
                            <span className="text-muted-foreground">
                                {event.name}
                                {event.new_price_try && event.new_price_try !== event.old_price_try
                                    ? ` · ${formatMoney(event.old_price_try, "TRY")} → ${formatMoney(
                                          event.new_price_try,
                                          "TRY"
                                      )}`
                                    : ""}
                                {event.kind === "charge_loss"
                                    ? ` · çekilen ${formatMoney(event.charged_try, "TRY")} / satış ${formatMoney(
                                          event.revenue_try,
                                          "TRY"
                                      )}`
                                    : ""}
                            </span>
                            <span className="ml-auto text-muted-foreground">{formatDateTime(event.at)}</span>
                        </li>
                    ))}
                </ul>
            ) : (
                <p className="mt-4 text-sm text-muted-foreground" data-testid="insurance-margin-empty">
                    Henüz otomatik fiyat düzeltmesi veya kâr uyarısı olmadı.
                </p>
            )}

            <div className="mt-4 flex flex-wrap items-center gap-3">
                <Button onClick={check} disabled={busy} className="h-10" data-testid="insurance-margin-check">
                    {busy ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                        <ShieldAlert className="mr-2 h-4 w-4" />
                    )}
                    Şimdi kontrol et
                </Button>
                <p className="text-xs text-muted-foreground" data-testid="insurance-margin-last-check">
                    Son kontrol: {data.last_check_at ? formatDateTime(data.last_check_at) : "henüz yapılmadı"}
                    {data.last_alert_at ? ` · son uyarı: ${formatDateTime(data.last_alert_at)}` : ""}
                </p>
            </div>
        </div>
    );
};

const ExpensePanel = ({ data }) => {
    const months = (data.items || []).filter((row) => row.count > 0);
    const max = Math.max(1, ...months.map((row) => row.charged_try));
    const totals = data.totals || {};

    return (
        <div className="card-surface mt-6 p-5" data-testid="insurance-expense-panel">
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                    <h2 className="flex items-center gap-2 font-heading text-sm font-bold">
                        <Receipt className="h-4 w-4 text-primary" /> Sigorta gideri · ödenen poliçeler
                    </h2>
                    <p className="mt-1 max-w-2xl text-xs leading-5 text-muted-foreground">
                        Tamamliyo'ya ödenen poliçe bedelleri (cari bakiyeden düşülen). Yalnızca gerçekten
                        çekim yapılan poliçeler listelenir; elle/test kesimleri gidere girmez.
                    </p>
                </div>
                <div className="text-right">
                    <p className="text-xs text-muted-foreground">Bu ay</p>
                    <p
                        className="font-heading text-lg font-bold text-primary"
                        data-testid="insurance-expense-this-month"
                    >
                        {formatMoney(totals.this_month_try || 0, "TRY")}
                    </p>
                    <p className="text-xs text-muted-foreground">
                        {totals.this_month_count || 0} poliçe · toplam{" "}
                        {formatMoney(totals.charged_try || 0, "TRY")}
                    </p>
                </div>
            </div>

            {months.length === 0 ? (
                <p className="mt-4 text-sm text-muted-foreground" data-testid="insurance-expense-empty">
                    Henüz karttan çekim yapılmadı. İlk poliçe kesildiğinde tutar burada görünecek.
                </p>
            ) : (
                <>
                    <ul className="mt-4 space-y-2" data-testid="insurance-expense-months">
                        {months.map((row) => (
                            <li key={row.month} className="flex items-center gap-3 text-sm">
                                <span className="w-14 shrink-0 text-xs text-muted-foreground">
                                    {row.label}
                                </span>
                                <span className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                                    <span
                                        className="block h-full rounded-full bg-primary transition-all"
                                        style={{ width: `${Math.max(4, (row.charged_try / max) * 100)}%` }}
                                    />
                                </span>
                                <span className="w-16 shrink-0 text-right text-xs text-muted-foreground">
                                    {row.count} poliçe
                                </span>
                                <span className="w-28 shrink-0 text-right font-medium">
                                    {formatMoney(row.charged_try, "TRY")}
                                </span>
                            </li>
                        ))}
                    </ul>

                    <div className="mt-5 overflow-x-auto">
                        <table className="w-full min-w-[720px] text-left text-sm">
                            <thead className="text-xs uppercase text-muted-foreground">
                                <tr>
                                    <th className="pb-2 font-medium">Tarih</th>
                                    <th className="pb-2 font-medium">Sipariş</th>
                                    <th className="pb-2 font-medium">Plan</th>
                                    <th className="pb-2 font-medium">Poliçe no</th>
                                    <th className="pb-2 text-right font-medium">Çekilen</th>
                                    <th className="pb-2 text-right font-medium">Satış</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border" data-testid="insurance-expense-rows">
                                {(data.recent || []).map((row) => (
                                    <tr key={row.task_id} data-testid={`insurance-expense-row-${row.task_id}`}>
                                        <td className="py-2 text-xs text-muted-foreground">
                                            {formatDateTime(row.charged_at)}
                                        </td>
                                        <td className="py-2 font-medium">{row.order_reference || "-"}</td>
                                        <td className="py-2 text-xs">
                                            {row.plan_name || "-"}
                                            {row.quantity > 1 ? ` × ${row.quantity}` : ""}
                                        </td>
                                        <td className="py-2 text-xs">{row.policy_no || row.quote_id || "-"}</td>
                                        <td className="py-2 text-right font-medium">
                                            {formatMoney(row.charged_try, "TRY")}
                                        </td>
                                        <td className="py-2 text-right text-muted-foreground">
                                            {formatMoney(row.revenue_try, "TRY")}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}
        </div>
    );
};

const PaymentPanel = ({ state, onChange }) => {
    const [busy, setBusy] = useState(false);

    const retry = async () => {
        setBusy(true);
        try {
            const { data } = await api.post("/admin/insurance/payment/retry");
            const issued = data.retry?.issued || 0;
            toast.success(
                issued
                    ? `Bekleyen ${issued} poliçe kesildi ve müşterilere gönderildi.`
                    : "Kesilebilecek bekleyen poliçe bulunamadı."
            );
            onChange();
        } catch (err) {
            toast.error(apiError(err, "Tekrar deneme başarısız."));
        } finally {
            setBusy(false);
        }
    };

    const waiting = state.waiting_tasks || 0;
    const review = state.review_tasks || 0;
    const balance = state.method === "balance";
    const blocked = !state.card_configured;
    const tone = blocked || review
        ? "border-destructive/40 bg-destructive/[0.06]"
        : waiting
          ? "border-amber-400/50 bg-amber-50"
          : "border-border";

    return (
        <div className={`card-surface mt-6 border p-5 ${tone}`} data-testid="insurance-payment-panel">
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                    <h2 className="flex items-center gap-2 font-heading text-sm font-bold">
                        <Wallet className="h-4 w-4 text-primary" /> Poliçe ödemesi ·{" "}
                        {balance ? "cari bakiye" : "kurumsal kart"}
                    </h2>
                    <p className="mt-1 max-w-2xl text-xs leading-5 text-muted-foreground">
                        {balance
                            ? "Tamamliyo poliçe bedeli her kesimde partner cari bakiyenizden düşülür (odemeTipi=3). Sunucuda kart veya CVV bilgisi tutulmaz; bakiye yetersizse poliçeler kuyrukta bekler ve size uyarı gider."
                            : "Tamamliyo poliçe bedeli her kesimde kurumsal karttan çekilir (odemeTipi=2). Kart bilgileri yalnızca sunucudaki ortam değişkenlerinde tutulur; panelde, veritabanında ve kayıtlarda görünmez."}
                    </p>
                </div>
                <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        blocked
                            ? "bg-destructive/10 text-destructive"
                            : "bg-emerald-100 text-emerald-800"
                    }`}
                    data-testid="insurance-payment-state"
                >
                    {balance
                        ? "Cari bakiye"
                        : blocked
                          ? "Kart tanımlı değil"
                          : `Kart hazır ${state.card_hint || ""}`}
                </span>
            </div>

            <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-3">
                <div>
                    <dt className="text-xs text-muted-foreground">Ödeme bekleyen poliçe</dt>
                    <dd
                        className="font-heading text-lg font-bold"
                        data-testid="insurance-payment-waiting"
                    >
                        {waiting}
                    </dd>
                </div>
                <div>
                    <dt className="text-xs text-muted-foreground">Doğrulama bekleyen çekim</dt>
                    <dd
                        className="font-heading text-lg font-bold"
                        data-testid="insurance-payment-review"
                    >
                        {review}
                    </dd>
                </div>
                <div>
                    <dt className="text-xs text-muted-foreground">Son uyarı</dt>
                    <dd className="font-medium" data-testid="insurance-payment-last-alert">
                        {state.last_alert_at ? formatDateTime(state.last_alert_at) : "Yok"}
                    </dd>
                </div>
            </dl>

            {blocked && (
                <p
                    className="mt-3 rounded-lg border border-destructive/40 bg-destructive/[0.06] p-3 text-xs font-semibold text-destructive"
                    data-testid="insurance-payment-warning"
                >
                    Kart bilgileri sunucuda tanımlı değil: poliçe kesimi durur ve siparişler kuyrukta
                    bekler. TAMAMLIYO_CARD_NUMBER, TAMAMLIYO_CARD_EXPIRY, TAMAMLIYO_CARD_CVV,
                    TAMAMLIYO_CARD_NAME, TAMAMLIYO_CARD_SURNAME değerleri girilmeli.
                </p>
            )}

            {review > 0 && (
                <p
                    className="mt-3 rounded-lg border border-amber-400/50 bg-amber-50 p-3 text-xs font-semibold text-amber-900"
                    data-testid="insurance-payment-review-warning"
                >
                    {review} poliçede ödeme yanıtı alınamadı; çekim yapılmış olabilir. Mükerrer çekimi
                    önlemek için otomatik tekrar denenmiyor — Tamamliyo panelinden ödeme durumunu
                    kontrol edip poliçeyi elle kesin.
                </p>
            )}

            <div className="mt-4 flex flex-wrap items-center gap-3">
                <Button
                    onClick={retry}
                    disabled={busy || !waiting}
                    className="h-10"
                    data-testid="insurance-payment-retry"
                >
                    {busy ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                        <RefreshCw className="mr-2 h-4 w-4" />
                    )}
                    Bekleyenleri tekrar dene
                </Button>
                <p className="text-xs text-muted-foreground">
                    Ödeme sorunu çözülünce kuyruk 15 dakikada bir kendiliğinden de denenir.
                </p>
            </div>
        </div>
    );
};

export default function AdminInsurance() {
    const [tasks, setTasks] = useState([]);
    const [report, setReport] = useState(null);
    const [monthly, setMonthly] = useState(null);
    const [provider, setProvider] = useState(null);
    const [payment, setPayment] = useState(null);
    const [expenses, setExpenses] = useState(null);
    const [margin, setMargin] = useState(null);
    const [loading, setLoading] = useState(true);

    const load = async () => {
        setLoading(true);
        try {
            const [tasksRes, reportRes, monthlyRes, providerRes, paymentRes, expenseRes, marginRes] =
                await Promise.all([
                    api.get("/admin/insurance-tasks"),
                    api.get("/admin/insurance-report"),
                    api.get("/admin/profit-monthly?months=12"),
                    api.get("/admin/insurance/provider"),
                    api.get("/admin/insurance/payment"),
                    api.get("/admin/insurance/expenses?months=12"),
                    api.get("/admin/insurance/margin"),
                ]);
            setTasks(tasksRes.data.items || []);
            setReport(reportRes.data);
            setMonthly(monthlyRes.data);
            setProvider(providerRes.data);
            setPayment(paymentRes.data);
            setExpenses(expenseRes.data);
            setMargin(marginRes.data);
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

            {provider && <ProviderPanel status={provider} onChange={load} />}
            {payment && <PaymentPanel state={payment} onChange={load} />}
            {margin && <MarginPanel data={margin} onChange={load} />}
            {expenses && <ExpensePanel data={expenses} />}

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
                        <TaskRow
                            key={task.id}
                            task={task}
                            onIssued={onIssued}
                            providerReady={!!provider?.configured}
                        />
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
