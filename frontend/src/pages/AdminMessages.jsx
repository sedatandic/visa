import React, { useEffect, useState } from "react";
import { Loader2, Mail, MailOpen } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatDateTime } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";

export default function AdminMessages() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);

    const load = async () => {
        setLoading(true);
        try {
            const { data } = await api.get("/admin/contact-messages");
            setItems(data.items);
        } catch (err) {
            toast.error(apiError(err, "Mesajlar yüklenemedi."));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    const markRead = async (id) => {
        try {
            await api.patch(`/admin/contact-messages/${id}/read`);
            setItems((list) => list.map((m) => (m.id === id ? { ...m, is_read: true } : m)));
        } catch (err) {
            toast.error(apiError(err, "İşlem başarısız."));
        }
    };

    return (
        <AdminLayout title="İletişim mesajları" description="Web sitesindeki iletişim formundan gelen mesajlar.">
            <div data-testid="admin-messages-page">
                {loading ? (
                    <div className="flex justify-center py-16">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                ) : items.length === 0 ? (
                    <div className="card-surface p-10 text-center">
                        <p className="text-sm font-semibold">Henüz mesaj yok</p>
                        <p className="mt-1 text-sm text-muted-foreground">İletişim formundan gelen mesajlar burada listelenir.</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {items.map((m) => (
                            <div key={m.id} className="card-surface p-5" data-testid={`admin-message-${m.id}`}>
                                <div className="flex flex-wrap items-start justify-between gap-3">
                                    <div>
                                        <p className="font-semibold">
                                            {m.name}{" "}
                                            {!m.is_read && (
                                                <span className="ml-2 rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-bold text-primary">Yeni</span>
                                            )}
                                        </p>
                                        <p className="text-xs text-muted-foreground">
                                            {m.email} {m.phone ? `· ${m.phone}` : ""} · {formatDateTime(m.created_at)}
                                        </p>
                                    </div>
                                    {!m.is_read && (
                                        <Button variant="secondary" className="h-9 border border-border" onClick={() => markRead(m.id)}>
                                            <MailOpen className="mr-2 h-4 w-4" /> Okundu işaretle
                                        </Button>
                                    )}
                                </div>
                                {m.subject && <p className="mt-3 text-sm font-semibold">{m.subject}</p>}
                                <p className="mt-1.5 whitespace-pre-wrap text-sm leading-6 text-muted-foreground">{m.message}</p>
                                <a
                                    href={`mailto:${m.email}`}
                                    className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-primary hover:underline"
                                >
                                    <Mail className="h-3.5 w-3.5" /> Yanıtla
                                </a>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </AdminLayout>
    );
}
