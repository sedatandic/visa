import React, { useCallback, useEffect, useState } from "react";
import { CheckCircle2, FileText, Loader2, RefreshCw, Search, XCircle } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../../lib/api";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Badge } from "../ui/badge";

const STATUS_FILTERS = [
    { value: "pending_review", label: "Onay bekleyen" },
    { value: "delivered", label: "İletilen" },
    { value: "failed", label: "Okunamayan" },
    { value: "", label: "Tümü" },
];

const STATUS_LABEL = {
    processing: "İşleniyor",
    pending_review: "Onay bekliyor",
    delivered: "Müşteriye iletildi",
    failed: "Okunamadı",
    rejected: "Reddedildi",
};

const REASON_LABEL = {
    reference_code: "Başvuru kodu eşleşti",
    passport_no: "Pasaport numarası eşleşti",
    full_name: "Yalnızca ad-soyad eşleşti",
    multiple_name_matches: "Aynı isimde birden fazla başvuru var",
    no_match: "Hiçbir başvuruyla eşleşmedi",
    admin_assigned: "Yönetici elle atadı",
};

const fmt = (v) => (v ? new Date(v).toLocaleString("tr-TR") : "-");

const AssignBox = ({ documentId, onDone }) => {
    const [q, setQ] = useState("");
    const [items, setItems] = useState([]);
    const [busy, setBusy] = useState(false);

    const search = async () => {
        setBusy(true);
        try {
            const { data } = await api.get("/admin/whatsapp/ai/applications", { params: { q } });
            setItems(data.items || []);
            if (!(data.items || []).length) toast.info("Başvuru bulunamadı.");
        } catch (e) {
            toast.error(apiError(e, "Arama başarısız."));
        } finally {
            setBusy(false);
        }
    };

    const assign = async (applicationId) => {
        setBusy(true);
        try {
            const { data } = await api.post(`/admin/whatsapp/ai/documents/${documentId}/assign`, {
                application_id: applicationId,
            });
            toast.success(`Belge ${data.reference_code} başvurusuna iletildi.`);
            onDone();
        } catch (e) {
            toast.error(apiError(e, "Gönderilemedi."));
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="mt-4 rounded-lg border border-border bg-muted/30 p-3">
            <div className="flex gap-2">
                <Input
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && search()}
                    placeholder="Kod, ad, soyad, pasaport veya e-posta"
                    data-testid={`wa-doc-search-input-${documentId}`}
                />
                <Button type="button" variant="outline" onClick={search} disabled={busy} data-testid={`wa-doc-search-button-${documentId}`}>
                    {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                </Button>
            </div>
            {items.length > 0 && (
                <ul className="mt-3 space-y-2">
                    {items.map((it) => (
                        <li key={it.id} className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border bg-card p-2 text-sm">
                            <span>
                                <b>{it.reference_code}</b> · {it.name || "-"} · {it.passport_no || "-"}
                                <span className="block text-xs text-muted-foreground">{it.email} · {fmt(it.created_at)}</span>
                            </span>
                            <Button
                                type="button"
                                size="sm"
                                onClick={() => assign(it.id)}
                                disabled={busy}
                                data-testid={`wa-doc-assign-${documentId}-${it.id}`}
                            >
                                Bu başvuruya gönder
                            </Button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export const WaDocumentQueue = () => {
    const [status, setStatus] = useState("pending_review");
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [openId, setOpenId] = useState("");

    const load = useCallback(async () => {
        setLoading(true);
        try {
            const { data } = await api.get("/admin/whatsapp/ai/documents", {
                params: status ? { status } : {},
            });
            setItems(data.items || []);
        } catch (e) {
            toast.error(apiError(e, "Belgeler yüklenemedi."));
        } finally {
            setLoading(false);
        }
    }, [status]);

    useEffect(() => {
        load();
    }, [load]);

    const reject = async (id) => {
        try {
            await api.post(`/admin/whatsapp/ai/documents/${id}/reject`);
            toast.success("Belge reddedildi.");
            load();
        } catch (e) {
            toast.error(apiError(e, "Reddedilemedi."));
        }
    };

    return (
        <div className="space-y-4" data-testid="wa-documents-panel">
            <div className="flex flex-wrap items-center gap-2">
                {STATUS_FILTERS.map((f) => (
                    <Button
                        key={f.value || "all"}
                        type="button"
                        size="sm"
                        variant={status === f.value ? "default" : "outline"}
                        onClick={() => setStatus(f.value)}
                        data-testid={`wa-doc-filter-${f.value || "all"}`}
                    >
                        {f.label}
                    </Button>
                ))}
                <Button type="button" size="sm" variant="ghost" onClick={load} data-testid="wa-doc-refresh-button">
                    <RefreshCw className="mr-2 h-4 w-4" /> Yenile
                </Button>
            </div>

            {loading ? (
                <div className="flex justify-center py-12">
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                </div>
            ) : items.length === 0 ? (
                <p className="card-surface p-6 text-sm text-muted-foreground" data-testid="wa-documents-empty">
                    Bu durumda belge yok. Tedarikçi WhatsApp grubuna bir vize PDF'i düştüğünde burada listelenir.
                </p>
            ) : (
                <ul className="space-y-3">
                    {items.map((d) => {
                        const ex = d.extracted || {};
                        const match = d.match || {};
                        return (
                            <li key={d.id} className="card-surface p-5" data-testid={`wa-doc-${d.id}`}>
                                <div className="flex flex-wrap items-start justify-between gap-3">
                                    <div className="flex items-start gap-3">
                                        <FileText className="mt-0.5 h-5 w-5 text-primary" />
                                        <div>
                                            <p className="font-semibold">{d.filename || "belge.pdf"}</p>
                                            <p className="text-xs text-muted-foreground">
                                                {d.from_wa_id || "-"} · {d.source} · {fmt(d.created_at)}
                                            </p>
                                        </div>
                                    </div>
                                    <Badge variant={d.status === "delivered" ? "default" : "secondary"} data-testid={`wa-doc-status-${d.id}`}>
                                        {STATUS_LABEL[d.status] || d.status}
                                    </Badge>
                                </div>

                                <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                                    <div className="rounded-lg border border-border p-3">
                                        <p className="text-xs font-semibold uppercase text-muted-foreground">Belgeden okunanlar</p>
                                        <p className="mt-1">
                                            {(ex.first_name || "-")} {(ex.last_name || "")} · pasaport: {ex.passport_no || "-"}
                                        </p>
                                        <p className="text-xs text-muted-foreground">
                                            tür: {ex.document_kind || "-"} · no: {ex.document_no || "-"} ·
                                            geçerlilik: {ex.valid_from || "-"} → {ex.valid_to || "-"}
                                        </p>
                                    </div>
                                    <div className="rounded-lg border border-border p-3">
                                        <p className="text-xs font-semibold uppercase text-muted-foreground">Eşleşme</p>
                                        <p className="mt-1" data-testid={`wa-doc-match-${d.id}`}>
                                            {match.reference_code || "Eşleşme yok"} ·{" "}
                                            <span className="font-semibold">%{Math.round((match.confidence || 0) * 100)} güven</span>
                                        </p>
                                        <p className="text-xs text-muted-foreground">
                                            {REASON_LABEL[match.reason] || match.reason || "-"}
                                            {d.error ? ` · hata: ${d.error}` : ""}
                                        </p>
                                    </div>
                                </div>

                                {d.status === "delivered" && d.delivery && (
                                    <p className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
                                        <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                                        E-posta: {d.delivery.email_status} · WhatsApp: {d.delivery.whatsapp_status}
                                    </p>
                                )}

                                {["pending_review", "failed"].includes(d.status) && (
                                    <div className="mt-4 flex flex-wrap gap-2">
                                        <Button
                                            type="button"
                                            size="sm"
                                            onClick={() => setOpenId(openId === d.id ? "" : d.id)}
                                            data-testid={`wa-doc-open-assign-${d.id}`}
                                        >
                                            Başvuruya ata
                                        </Button>
                                        <Button
                                            type="button"
                                            size="sm"
                                            variant="outline"
                                            onClick={() => reject(d.id)}
                                            data-testid={`wa-doc-reject-${d.id}`}
                                        >
                                            <XCircle className="mr-2 h-4 w-4" /> Reddet
                                        </Button>
                                    </div>
                                )}

                                {openId === d.id && <AssignBox documentId={d.id} onDone={load} />}
                            </li>
                        );
                    })}
                </ul>
            )}
        </div>
    );
};
