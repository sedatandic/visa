import React, { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, Loader2, XCircle } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatDateTime } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";

const STATUS_UI = {
    sent: { label: "Gönderildi", icon: CheckCircle2, className: "text-[#14532D]" },
    skipped: { label: "Atlandı", icon: AlertTriangle, className: "text-[#7A4B00]" },
    error: { label: "Hata", icon: XCircle, className: "text-destructive" },
};

export default function AdminEmails() {
    const [items, setItems] = useState([]);
    const [configured, setConfigured] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get("/admin/emails")
            .then(({ data }) => {
                setItems(data.items);
                setConfigured(data.email_configured);
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
                    <div className="mb-6 flex items-start gap-3 rounded-xl border border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.1)] p-5" data-testid="email-not-configured-warning">
                        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[#7A4B00]" />
                        <div className="text-sm leading-6 text-[#7A4B00]">
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
                                </tr>
                            </thead>
                            <tbody>
                                {items.map((m) => {
                                    const ui = STATUS_UI[m.status] || STATUS_UI.error;
                                    const Icon = ui.icon;
                                    return (
                                        <tr key={m.id} className="border-t border-border">
                                            <td className="px-5 py-3.5">{m.to}</td>
                                            <td className="px-5 py-3.5 text-muted-foreground">{m.subject}</td>
                                            <td className="px-5 py-3.5 text-xs text-muted-foreground">{m.kind}</td>
                                            <td className="px-5 py-3.5">
                                                <span className={`inline-flex items-center gap-1.5 font-semibold ${ui.className}`}>
                                                    <Icon className="h-3.5 w-3.5" /> {ui.label}
                                                </span>
                                            </td>
                                            <td className="px-5 py-3.5 text-xs text-muted-foreground">{formatDateTime(m.created_at)}</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </AdminLayout>
    );
}
