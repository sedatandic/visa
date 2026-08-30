import React, { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Download, ExternalLink, Loader2, Save } from "lucide-react";
import { toast } from "sonner";
import { api, apiError, fileUrl } from "../lib/api";
import {
    STATUS_META,
    STATUS_OPTIONS,
    PURPOSE_LABELS,
    formatDate,
    formatDateTime,
    formatMoney,
    setMeta,
} from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { PaymentBadge, StatusBadge } from "../components/StatusBadge";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "../components/ui/dialog";

const Row = ({ label, value }) => (
    <div className="flex items-start justify-between gap-4 border-b border-border py-2.5 last:border-0">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-right text-sm font-semibold">{value || "-"}</span>
    </div>
);

const DocumentViewer = ({ fileId, title }) => {
    if (!fileId) {
        return (
            <div className="rounded-xl border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
                {title}: yüklenmemiş
            </div>
        );
    }
    const url = fileUrl(fileId);
    return (
        <div className="rounded-xl border border-border bg-card p-4">
            <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold">{title}</p>
                <a
                    href={url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 text-xs font-semibold text-primary hover:underline"
                    data-testid={`open-document-${title}`}
                >
                    Yeni sekmede aç <ExternalLink className="h-3 w-3" />
                </a>
            </div>
            <Dialog>
                <DialogTrigger asChild>
                    <button type="button" className="mt-3 block w-full overflow-hidden rounded-lg border border-border">
                        <img
                            src={url}
                            alt={title}
                            className="h-48 w-full bg-muted object-contain"
                            data-testid={`document-thumbnail-${title}`}
                        />
                    </button>
                </DialogTrigger>
                <DialogContent className="max-w-3xl bg-card">
                    <DialogHeader>
                        <DialogTitle>{title}</DialogTitle>
                    </DialogHeader>
                    <img src={url} alt={title} className="max-h-[70vh] w-full object-contain" />
                    <a
                        href={url}
                        download
                        className="mt-2 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline"
                    >
                        <Download className="h-4 w-4" /> İndir
                    </a>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default function AdminApplicationDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [status, setStatus] = useState("");
    const [note, setNote] = useState("");

    useEffect(() => {
        setMeta("Başvuru Detayı | VizeAtlas Dubai", "Başvuru detayı ve belge görüntüleyici.");
    }, []);

    const load = useCallback(async () => {
        setLoading(true);
        try {
            const { data: res } = await api.get(`/admin/applications/${id}`);
            setData(res);
            setStatus(res.application.status);
            setNote(res.application.admin_notes || "");
        } catch (err) {
            if (err?.response?.status === 401) {
                localStorage.removeItem("dv_admin_token");
                navigate("/admin/giris");
                return;
            }
            toast.error(apiError(err, "Başvuru yüklenemedi."));
        } finally {
            setLoading(false);
        }
    }, [id, navigate]);

    useEffect(() => {
        load();
    }, [load]);

    const save = async () => {
        setSaving(true);
        try {
            const { data: res } = await api.patch(`/admin/applications/${id}`, {
                status,
                note,
                notify: true,
            });
            setData((d) => ({ ...d, application: res.application }));
            if (res.email_notification === "sent") {
                toast.success("Durum güncellendi ve başvuru sahibine e-posta gönderildi.");
            } else if (res.email_notification === "skipped") {
                toast.success("Durum güncellendi. (E-posta servisi yapılandırılmadığı için bildirim gönderilmedi.)");
            } else {
                toast.success("Durum güncellendi.");
            }
        } catch (err) {
            toast.error(apiError(err, "Güncelleme başarısız."));
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <AdminLayout>
                <div className="flex items-center justify-center py-20">
                    <Loader2 className="h-7 w-7 animate-spin text-primary" />
                </div>
            </AdminLayout>
        );
    }

    if (!data) {
        return (
            <AdminLayout title="Başvuru bulunamadı">
                <Button variant="secondary" className="h-11 border border-border" onClick={() => navigate("/admin")}>
                    <ArrowLeft className="mr-2 h-4 w-4" /> Listeye dön
                </Button>
            </AdminLayout>
        );
    }

    const a = data.application;

    return (
        <AdminLayout>
            <div data-testid="admin-application-detail">
                <Button variant="secondary" className="h-10 border border-border" onClick={() => navigate("/admin")} data-testid="admin-back-to-list">
                    <ArrowLeft className="mr-2 h-4 w-4" /> Başvurular
                </Button>

                <div className="mt-5 flex flex-wrap items-start justify-between gap-4">
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Takip kodu</p>
                        <h1 className="font-heading text-3xl font-bold tracking-wider">{a.reference_code}</h1>
                        <p className="mt-1 text-sm text-muted-foreground">
                            {a.applicant?.first_name} {a.applicant?.last_name} · {a.visa_type_name} · {formatMoney(a.price, a.currency)}
                        </p>
                    </div>
                    <div className="flex flex-col items-start gap-2 sm:items-end">
                        <StatusBadge status={a.status} />
                        <PaymentBadge status={a.payment?.status} />
                    </div>
                </div>

                <div className="mt-7 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                    <div className="space-y-6">
                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Başvuru sahibi</h2>
                            <div className="mt-3">
                                <Row label="Ad Soyad" value={`${a.applicant?.first_name} ${a.applicant?.last_name}`} />
                                <Row label="E-posta" value={a.applicant?.email} />
                                <Row label="Telefon" value={a.applicant?.phone} />
                                <Row label="Doğum tarihi" value={formatDate(a.applicant?.birth_date)} />
                                <Row label="Cinsiyet" value={a.applicant?.gender === "female" ? "Kadın" : "Erkek"} />
                                <Row label="T.C. Kimlik No" value={a.applicant?.national_id} />
                                <Row label="Şehir" value={a.applicant?.address_city} />
                                <Row label="Pasaport No" value={a.applicant?.passport_no} />
                                <Row label="Pasaport geçerlilik" value={formatDate(a.applicant?.passport_expiry)} />
                            </div>
                        </div>

                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Seyahat bilgileri</h2>
                            <div className="mt-3">
                                <Row label="Gidiş" value={formatDate(a.travel?.arrival_date)} />
                                <Row label="Dönüş" value={formatDate(a.travel?.departure_date)} />
                                <Row label="Amacı" value={PURPOSE_LABELS[a.travel?.purpose] || a.travel?.purpose} />
                                <Row label="Konaklama" value={a.travel?.accommodation} />
                                <Row label="Uçuş no" value={a.travel?.flight_no} />
                                <Row label="Not" value={a.travel?.notes} />
                            </div>
                        </div>

                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Ödeme hareketleri</h2>
                            {(data.transactions || []).length === 0 ? (
                                <p className="mt-3 text-sm text-muted-foreground">Henüz ödeme denemesi yok.</p>
                            ) : (
                                <div className="mt-3 space-y-3">
                                    {data.transactions.map((t) => (
                                        <div key={t.session_id} className="rounded-lg border border-border p-3 text-sm">
                                            <div className="flex items-center justify-between gap-3">
                                                <span className="font-semibold">{formatMoney(t.amount, (t.currency || "try").toUpperCase())}</span>
                                                <PaymentBadge status={t.payment_status} />
                                            </div>
                                            <p className="mt-1 break-all text-xs text-muted-foreground">{t.session_id}</p>
                                            <p className="text-xs text-muted-foreground">{formatDateTime(t.created_at)}</p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Durum geçmişi</h2>
                            <ol className="mt-4 space-y-4">
                                {(a.status_history || []).map((h, i) => (
                                    <li key={i} className="flex gap-3">
                                        <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
                                        <div>
                                            <p className="text-sm font-semibold">{STATUS_META[h.status]?.label || h.status}</p>
                                            <p className="text-xs text-muted-foreground">{formatDateTime(h.at)}</p>
                                            {h.note && <p className="mt-0.5 text-sm text-muted-foreground">{h.note}</p>}
                                        </div>
                                    </li>
                                ))}
                            </ol>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Durumu güncelle</h2>
                            <div className="mt-4 space-y-4">
                                <div className="space-y-2">
                                    <Label>Yeni durum</Label>
                                    <Select value={status} onValueChange={setStatus}>
                                        <SelectTrigger data-testid="admin-status-update-select">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {STATUS_OPTIONS.map((s) => (
                                                <SelectItem key={s} value={s}>{STATUS_META[s]?.label || s}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="admin-note">Danışman notu (başvuru sahibine e-postada gönderilir)</Label>
                                    <Textarea
                                        id="admin-note"
                                        rows={4}
                                        value={note}
                                        onChange={(e) => setNote(e.target.value)}
                                        placeholder="Örn. Fotoğrafınız yeniden yüklenmeli."
                                        data-testid="admin-note-input"
                                    />
                                </div>
                                <Button onClick={save} disabled={saving} className="h-11 w-full" data-testid="admin-save-status-button">
                                    {saving ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Kaydediliyor…
                                        </>
                                    ) : (
                                        <>
                                            <Save className="mr-2 h-4 w-4" /> Kaydet
                                        </>
                                    )}
                                </Button>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <h2 className="font-heading text-base font-bold">Yüklenen belgeler</h2>
                            <DocumentViewer fileId={a.documents?.passport_file_id} title="Pasaport" />
                            <DocumentViewer fileId={a.documents?.photo_file_id} title="Biyometrik Fotoğraf" />
                        </div>
                    </div>
                </div>
            </div>
        </AdminLayout>
    );
}
