import React, { useEffect, useState } from "react";
import { Check, PhoneCall, TriangleAlert } from "lucide-react";
import { api } from "../lib/api";
import { Button } from "./ui/button";

const digits = (value) => String(value || "").replace(/\D/g, "");

const waNumber = (phone) => {
    const d = digits(phone);
    if (!d) return "";
    if (d.startsWith("90")) return d;
    return d.startsWith("0") ? `90${d.slice(1)}` : `90${d}`;
};

const sinceText = (iso) => {
    const minutes = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
    if (minutes < 1) return "az önce";
    if (minutes < 60) return `${minutes} dk önce`;
    const hours = Math.round(minutes / 60);
    return hours < 24 ? `${hours} sa önce` : `${Math.round(hours / 24)} gün önce`;
};

/** Pasaportu okunamayan musteriler: ekip hemen arayabilsin diye panelde kirmizi kart. */
export const DocAlertsCard = () => {
    const [items, setItems] = useState([]);

    const load = async () => {
        try {
            const { data } = await api.get("/admin/alerts", {
                params: { kind: "passport_unreadable", unread: true },
            });
            setItems(data.items || []);
        } catch {
            setItems([]);
        }
    };

    useEffect(() => {
        load();
        const timer = setInterval(load, 60000);
        return () => clearInterval(timer);
    }, []);

    const markRead = async (id) => {
        setItems((list) => list.filter((a) => a.id !== id));
        try {
            await api.post(`/admin/alerts/${id}/read`);
        } catch {
            load();
        }
    };

    if (!items.length) return null;

    return (
        <section
            className="mt-5 rounded-xl border border-destructive/40 bg-destructive/[0.05] p-5"
            data-testid="admin-doc-alerts"
        >
            <div className="flex items-center gap-2">
                <TriangleAlert className="h-4 w-4 text-destructive" aria-hidden="true" />
                <h2 className="font-heading text-base font-bold text-destructive">
                    Pasaport okunamadı · hemen arayın ({items.length})
                </h2>
            </div>
            <p className="mt-1 text-xs leading-5 text-muted-foreground">
                Bu müşteriler pasaportunu yükledi ama otomatik okuma başarısız oldu. Form doldurmayı
                bırakmadan önce telefonla yardım edin.
            </p>
            <ul className="mt-4 space-y-3">
                {items.map((alert) => (
                    <li
                        key={alert.id}
                        className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-card p-3"
                        data-testid={`doc-alert-${alert.id}`}
                    >
                        <div className="min-w-0">
                            <p className="text-sm font-bold">
                                {alert.contact?.name || "İsim girilmemiş"}
                                <span className="ml-2 text-xs font-semibold text-muted-foreground">
                                    {sinceText(alert.created_at)}
                                </span>
                            </p>
                            <p className="text-xs leading-5 text-muted-foreground">
                                {alert.contact?.phone || "telefon yok"} · {alert.contact?.email || "e-posta yok"} ·{" "}
                                {alert.reason_label}
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {alert.contact?.phone && (
                                <>
                                    <Button
                                        asChild
                                        className="h-10"
                                        data-testid={`doc-alert-call-${alert.id}`}
                                    >
                                        <a href={`tel:${digits(alert.contact.phone)}`}>
                                            <PhoneCall className="mr-2 h-4 w-4" /> Ara
                                        </a>
                                    </Button>
                                    <Button
                                        asChild
                                        variant="secondary"
                                        className="h-10 border border-border"
                                        data-testid={`doc-alert-wa-${alert.id}`}
                                    >
                                        <a
                                            href={`https://wa.me/${waNumber(alert.contact.phone)}?text=${encodeURIComponent(
                                                "Merhaba, Dubai Vize Hattı'ndan ulaşıyoruz. Pasaport fotoğrafınız okunamadı, yardımcı olabilir miyiz?"
                                            )}`}
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            WhatsApp
                                        </a>
                                    </Button>
                                </>
                            )}
                            <Button
                                variant="secondary"
                                className="h-10 border border-border"
                                onClick={() => markRead(alert.id)}
                                data-testid={`doc-alert-done-${alert.id}`}
                            >
                                <Check className="mr-2 h-4 w-4" /> İlgilendim
                            </Button>
                        </div>
                    </li>
                ))}
            </ul>
        </section>
    );
};
