import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
    ArrowRight,
    Banknote,
    CalendarDays,
    FileText,
    Inbox,
    MessageCircle,
    PlaneTakeoff,
    ShieldCheck,
    ShoppingCart,
    Users,
} from "lucide-react";
import { api } from "../lib/api";
import { formatMoney } from "../lib/site";
import { Button } from "./ui/button";

const Metric = ({ id, label, value, icon: Icon }) => (
    <div
        className="flex items-center gap-3 rounded-xl border border-border/70 bg-card/70 px-4 py-3"
        data-testid={`admin-welcome-metric-${id}`}
    >
        <Icon className="h-4 w-4 shrink-0 text-primary" />
        <div>
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{label}</p>
            <p className="font-heading text-lg font-bold leading-tight">{value}</p>
        </div>
    </div>
);

const Chip = ({ id, label, count, icon: Icon, onClick }) => {
    if (!count) return null;
    const classes =
        "flex items-center gap-2 rounded-full border border-primary/30 bg-primary/[0.07] px-3.5 py-1.5 text-sm font-medium";
    const content = (
        <>
            <Icon className="h-4 w-4 text-primary" />
            {label}
            <span className="rounded-full bg-primary px-1.5 text-xs font-bold text-primary-foreground">{count}</span>
        </>
    );
    return onClick ? (
        <button
            type="button"
            onClick={onClick}
            className={`${classes} transition-colors hover:bg-primary/[0.14]`}
            data-testid={`admin-welcome-pending-${id}`}
        >
            {content}
        </button>
    ) : (
        <span className={classes} data-testid={`admin-welcome-pending-${id}`}>{content}</span>
    );
};

/** Panel açılış kartı: bugünün özeti + bekleyen işler + hızlı kısayollar. */
export const AdminWelcomeCard = ({ stats, onShowPaymentPending, onShowDocumentsPending }) => {
    const navigate = useNavigate();
    const [data, setData] = useState(null);

    useEffect(() => {
        let cancelled = false;
        api.get("/admin/today")
            .then(({ data: res }) => !cancelled && setData(res))
            .catch(() => {});
        return () => {
            cancelled = true;
        };
    }, []);

    if (!data) return null;

    const attention = data.attention || {};
    const waCount = (stats?.wa_pending_documents || 0) + (stats?.wa_needs_human || 0);
    const openWork = data.pending_total + (stats?.unread_messages || 0) + waCount;
    const quiet = !data.has_activity && openWork === 0;

    const summary = quiet
        ? "Bugün panel sakin. Bekleyen iş yok, yeni başvuru bekleniyor."
        : [
              data.applications_today
                  ? `Bugün ${data.applications_today} yeni başvuru geldi`
                  : "Bugün henüz yeni başvuru yok",
              data.orders_today ? `${data.orders_today} ek hizmet siparişi alındı` : "",
              openWork ? `${openWork} iş sizi bekliyor` : "",
          ]
              .filter(Boolean)
              .join(" · ") + ".";

    const actions = [
        { id: "payment", label: "Ödeme bekleyenler", onClick: onShowPaymentPending },
        { id: "documents", label: "Eksik belgeliler", onClick: onShowDocumentsPending },
        { id: "whatsapp", label: "WhatsApp paneli", onClick: () => navigate("/admin/whatsapp") },
        { id: "insurance", label: "Sigorta poliçeleri", onClick: () => navigate("/admin/sigorta") },
        { id: "orders", label: "eSIM & Sigorta", onClick: () => navigate("/admin/siparisler") },
        { id: "visitors", label: "Ziyaretçiler", onClick: () => navigate("/admin/ziyaretciler") },
    ];

    return (
        <div
            className="card-surface relative overflow-hidden p-6 sm:p-7"
            data-testid="admin-welcome-card"
        >
            <div className="pointer-events-none absolute -right-16 -top-20 h-56 w-56 rounded-full bg-primary/[0.07]" />
            <div className="relative">
                <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    <CalendarDays className="h-3.5 w-3.5 text-primary" /> {data.day_label}
                </p>
                <h2 className="mt-2 font-heading text-2xl font-bold" data-testid="admin-welcome-greeting">
                    {data.greeting}, {quiet ? "her şey yolunda" : "işe koyulalım"}
                </h2>
                <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground" data-testid="admin-welcome-summary">
                    {summary}
                </p>

                <div className="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
                    <Metric id="applications" label="Bugün gelen" value={data.applications_today} icon={FileText} />
                    <Metric id="travelers" label="Bugünkü yolcu" value={data.travelers_today} icon={Users} />
                    <Metric
                        id="revenue"
                        label="Bugünkü tahsilat"
                        value={formatMoney(data.revenue_today?.total || 0)}
                        icon={Banknote}
                    />
                    <Metric id="pending" label="Bekleyen iş" value={openWork} icon={Inbox} />
                </div>

                {openWork > 0 && (
                    <div className="mt-5 flex flex-wrap gap-2" data-testid="admin-welcome-pending-list">
                        <Chip
                            id="transfer"
                            label="Havale onayı"
                            count={attention.awaiting_transfer?.count}
                            icon={Banknote}
                            onClick={onShowPaymentPending}
                        />
                        <Chip
                            id="documents"
                            label="Eksik belge"
                            count={attention.missing_documents?.count}
                            icon={FileText}
                            onClick={onShowDocumentsPending}
                        />
                        <Chip
                            id="messages"
                            label="Okunmamış mesaj"
                            count={stats?.unread_messages}
                            icon={MessageCircle}
                            onClick={() => navigate("/admin/mesajlar")}
                        />
                        <Chip
                            id="whatsapp"
                            label="WhatsApp işlemi"
                            count={waCount}
                            icon={MessageCircle}
                            onClick={() => navigate("/admin/whatsapp")}
                        />
                        <Chip
                            id="policies"
                            label="Poliçe kesimi"
                            count={attention.policy_tasks?.count}
                            icon={ShieldCheck}
                            onClick={() => navigate("/admin/sigorta")}
                        />
                        <Chip
                            id="carts"
                            label="Terk edilmiş sepet"
                            count={attention.abandoned_carts?.count}
                            icon={ShoppingCart}
                        />
                        <Chip
                            id="departures"
                            label="7 gün içinde uçuş"
                            count={data.upcoming_departures?.count}
                            icon={PlaneTakeoff}
                        />
                    </div>
                )}

                <div className="mt-6 flex flex-wrap gap-2 border-t border-border pt-5" data-testid="admin-welcome-actions">
                    {actions.map(({ id, label, onClick }) => (
                        <Button
                            key={id}
                            variant="secondary"
                            className="h-10 min-w-[46%] flex-1 border border-border sm:min-w-0 sm:flex-none"
                            onClick={onClick}
                            data-testid={`admin-welcome-action-${id}`}
                        >
                            {label} <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                        </Button>
                    ))}
                </div>
            </div>
        </div>
    );
};
