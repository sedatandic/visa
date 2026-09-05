import React, { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, Eye, Loader2, XCircle } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatDateTime } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "../components/ui/dialog";

const STATUS_UI = {
    sent: { label: "Gönderildi", icon: CheckCircle2, className: "text-[hsl(var(--brand-green))]" },
    skipped: { label: "Atlandı", icon: AlertTriangle, className: "text-[hsl(var(--status-warning))]" },
    error: { label: "Hata", icon: XCircle, className: "text-destructive" },
};

export default function AdminEmails() {
    const [items, setItems] = useState([]);
    const [configured, setConfigured] = useState(false);
    const [sender, setSender] = useState("");
    const [sandbox, setSandbox] = useState(false);
    const [loading, setLoading] = useState(true);
    const [preview, setPreview] = useState(null);
    const [previewLoading, setPreviewLoading] = useState(false);

    const openPreview = async (item) => {
        setPreview({ ...item, html: "" });
        if (!item.has_preview) return;
        setPreviewLoading(true);
        try {
            const { data } = await api.get(`/admin/emails/${item.id}`);
            setPreview(data);
        } catch (err) {
            toast.error(apiError(err, "E-posta önizlemesi alınamadı."));
        } finally {
            setPreviewLoading(false);
        }
    };

    useEffect(() => {
        api.get("/admin/emails")
            .then(({ data }) => {
                setItems(data.items);
                setConfigured(data.email_configured);
                setSender(data.sender_email || "");
                setSandbox(!!data.sandbox_sender);
            })
            .catch((err) => toast.error(apiError(err, "E-posta kayıtları yüklenemedi.")))
            .finally(() => setLoading(false));
    }, []);

    return (
        <AdminLayout
            title="E-posta bildirimleri"
            description="Sistemin göndermeye çalıştığı tüm bildirimler ve sonuçları."
        >
            <div data-testid="admin-emails-page">
                {!configured && (
                    <div className="mb-6 flex items-start gap-3 rounded-xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.09)] p-5" data-testid="email-not-configured-warning">
                        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--status-warning))]" />
                        <div className="text-sm leading-6 text-[hsl(var(--status-warning))]">
                            <p className="font-semibold">E-posta servisi henüz bağlanmadı</p>
                            <p className="mt-1">
                                Bildirimler gönderilmiyor, yalnızca kaydediliyor. Resend hesabınızdan
                                alacağınız API anahtarını (<code>RESEND_API_KEY</code>) sistemimize eklemesi
                                için bize ilettiğinizde tüm geçmiş ve yeni bildirimler otomatik olarak
                                gönderilmeye başlar.
                            </p>
                        </div>
                    </div>
                )}

                {configured && sandbox && (
                    <div
                        className="mb-6 flex items-start gap-3 rounded-xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.09)] p-5"
                        data-testid="email-sandbox-warning"
                    >
                        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--status-warning))]" />
                        <div className="text-sm leading-6 text-[hsl(var(--status-warning))]">
                            <p className="font-semibold">
                                E-posta servisi bağlı, ancak hâlâ test göndericisi kullanılıyor
                            </p>
                            <p className="mt-1">
                                Gönderici adresi <code>{sender}</code>. Resend'in test göndericisi yalnızca
                                hesap sahibinin adresine mail atabilir; müşterilere gönderim{" "}
                                <strong>başarısız olur</strong>. Çözüm: Resend panelinde{" "}
                                <code>resend.com/domains</code> adresinden kendi alan adınızı doğrulayın,
                                ardından gönderici adresinin (<code>SENDER_EMAIL</code>) örneğin{" "}
                                <code>noreply@alanadiniz.com</code> olarak güncellenmesini isteyin.
                            </p>
                        </div>
                    </div>
                )}

                {configured && !sandbox && !!sender && (
                    <div
                        className="mb-6 flex items-start gap-3 rounded-xl border border-border bg-muted/40 p-5"
                        data-testid="email-sender-info"
                    >
                        <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                        <div className="text-sm leading-6">
                            <p className="font-semibold">E-posta servisi aktif</p>
                            <p className="mt-1 text-muted-foreground">
                                Bildirimler <code>{sender}</code> adresinden gönderiliyor.
                            </p>
                        </div>
                    </div>
                )}

                {loading ? (
                    <div className="flex justify-center py-16">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                ) : items.length === 0 ? (
                    <div className="card-surface p-10 text-center">
                        <p className="text-sm font-semibold">Henüz bildirim yok</p>
                    </div>
                ) : (
                    <div className="card-surface overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-[hsl(var(--cloud))] text-xs uppercase tracking-wider text-muted-foreground">
                                <tr>
                                    <th className="px-5 py-3 font-semibold">Alıcı</th>
                                    <th className="px-5 py-3 font-semibold">Konu</th>
                                    <th className="px-5 py-3 font-semibold">Tür</th>
                                    <th className="px-5 py-3 font-semibold">Durum</th>
                                    <th className="px-5 py-3 font-semibold">Tarih</th>
                                    <th className="px-5 py-3 font-semibold">Önizleme</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items.map((m) => {
                                    const ui = STATUS_UI[m.status] || STATUS_UI.error;
                                    const Icon = ui.icon;
                                    return (
                                        <tr
                                            key={m.id}
                                            className="cursor-pointer border-t border-border transition-colors duration-150 hover:bg-muted/50"
                                            onClick={() => openPreview(m)}
                                            data-testid={`email-row-${m.id}`}
                                        >
                                            <td className="px-5 py-3.5">{m.to}</td>
                                            <td className="px-5 py-3.5 text-muted-foreground">{m.subject}</td>
                                            <td className="px-5 py-3.5 text-xs text-muted-foreground">{m.kind}</td>
                                            <td className="px-5 py-3.5">
                                                <span className={`inline-flex items-center gap-1.5 font-semibold ${ui.className}`}>
                                                    <Icon className="h-3.5 w-3.5" /> {ui.label}
                                                </span>
                                            </td>
                                            <td className="px-5 py-3.5 text-xs text-muted-foreground">{formatDateTime(m.created_at)}</td>
                                            <td className="px-5 py-3.5">
                                                <span
                                                    className={`inline-flex items-center gap-1.5 text-xs font-semibold ${
                                                        m.has_preview ? "text-primary" : "text-muted-foreground"
                                                    }`}
                                                >
                                                    <Eye className="h-3.5 w-3.5" />
                                                    {m.has_preview ? "Görüntüle" : "Önizleme yok"}
                                                </span>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}

                <Dialog open={!!preview} onOpenChange={(open) => !open && setPreview(null)}>
                    <DialogContent className="max-w-3xl" data-testid="email-preview-dialog">
                        <DialogHeader>
                            <DialogTitle className="text-left text-base">
                                {preview?.subject || "E-posta önizlemesi"}
                            </DialogTitle>
                            <DialogDescription className="text-left text-xs">
                                {preview?.to} · {preview?.kind} ·{" "}
                                {preview?.created_at ? formatDateTime(preview.created_at) : ""}
                            </DialogDescription>
                        </DialogHeader>
                        {previewLoading ? (
                            <div className="flex justify-center py-16">
                                <Loader2 className="h-6 w-6 animate-spin text-primary" />
                            </div>
                        ) : preview?.html ? (
                            <iframe
                                title="E-posta önizlemesi"
                                srcDoc={preview.html}
                                sandbox=""
                                className="h-[65vh] w-full rounded-lg border border-border bg-white"
                                data-testid="email-preview-frame"
                            />
                        ) : (
                            <p className="rounded-lg border border-dashed border-border p-6 text-sm text-muted-foreground" data-testid="email-preview-empty">
                                Bu kayıt için önizleme yok. E-posta gövdesi yalnızca bu güncellemeden sonra
                                gönderilen bildirimler için saklanıyor.
                            </p>
                        )}
                    </DialogContent>
                </Dialog>
            </div>
        </AdminLayout>
    );
}
