import React, { useCallback, useEffect, useState } from "react";
import { Bot, Loader2, RefreshCw, Send, UserRound } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../../lib/api";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { Switch } from "../ui/switch";
import { Badge } from "../ui/badge";

const fmt = (v) => (v ? new Date(v).toLocaleString("tr-TR") : "");

const ROLE_STYLE = {
    user: "bg-muted/60 mr-auto",
    assistant: "bg-primary/10 ml-auto",
    agent: "bg-emerald-500/10 ml-auto",
};

const ROLE_LABEL = { user: "Müşteri", assistant: "Bot", agent: "Temsilci" };

export const WaConversations = () => {
    const [items, setItems] = useState([]);
    const [waiting, setWaiting] = useState(0);
    const [active, setActive] = useState(null);
    const [loading, setLoading] = useState(true);
    const [text, setText] = useState("");
    const [sending, setSending] = useState(false);

    const loadList = useCallback(async () => {
        try {
            const { data } = await api.get("/admin/whatsapp/ai/conversations");
            setItems(data.items || []);
            setWaiting(data.waiting || 0);
        } catch (e) {
            toast.error(apiError(e, "Konuşmalar yüklenemedi."));
        } finally {
            setLoading(false);
        }
    }, []);

    const openConversation = async (waId) => {
        try {
            const { data } = await api.get(`/admin/whatsapp/ai/conversations/${waId}`);
            setActive(data);
        } catch (e) {
            toast.error(apiError(e, "Konuşma açılamadı."));
        }
    };

    useEffect(() => {
        loadList();
    }, [loadList]);

    const toggleBot = async (enabled) => {
        try {
            await api.post(`/admin/whatsapp/ai/conversations/${active.wa_id}/bot`, { bot_enabled: enabled });
            setActive((v) => ({ ...v, bot_enabled: enabled, needs_human: !enabled }));
            toast.success(enabled ? "Bot bu sohbette devrede." : "Bot durduruldu, sohbeti siz yönetiyorsunuz.");
            loadList();
        } catch (e) {
            toast.error(apiError(e, "Değiştirilemedi."));
        }
    };

    const sendReply = async () => {
        if (!text.trim()) return;
        setSending(true);
        try {
            await api.post(`/admin/whatsapp/ai/conversations/${active.wa_id}/reply`, { text });
            setText("");
            await openConversation(active.wa_id);
            loadList();
            toast.success("Mesaj gönderildi.");
        } catch (e) {
            toast.error(apiError(e, "Gönderilemedi."));
        } finally {
            setSending(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center py-12">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="grid gap-4 lg:grid-cols-[320px_1fr]" data-testid="wa-conversations-panel">
            <div className="card-surface p-4">
                <div className="flex items-center justify-between">
                    <h2 className="font-heading text-sm font-bold">
                        Konuşmalar
                        {waiting > 0 && (
                            <Badge className="ml-2" variant="destructive" data-testid="wa-waiting-badge">
                                {waiting} bekliyor
                            </Badge>
                        )}
                    </h2>
                    <Button type="button" size="sm" variant="ghost" onClick={loadList} data-testid="wa-conversations-refresh">
                        <RefreshCw className="h-4 w-4" />
                    </Button>
                </div>
                {items.length === 0 ? (
                    <p className="mt-4 text-sm text-muted-foreground" data-testid="wa-conversations-empty">
                        Henüz WhatsApp konuşması yok. Simülatör sekmesinden test mesajı gönderebilirsiniz.
                    </p>
                ) : (
                    <ul className="mt-3 max-h-[560px] space-y-2 overflow-y-auto">
                        {items.map((c) => (
                            <li key={c.id}>
                                <button
                                    type="button"
                                    onClick={() => openConversation(c.wa_id)}
                                    className={`w-full rounded-lg border p-3 text-left text-sm transition-colors ${
                                        active?.wa_id === c.wa_id ? "border-primary bg-primary/5" : "border-border hover:bg-muted/50"
                                    }`}
                                    data-testid={`wa-conversation-item-${c.wa_id}`}
                                >
                                    <span className="flex items-center justify-between gap-2">
                                        <b>{c.profile_name || c.wa_id}</b>
                                        {c.needs_human && (
                                            <Badge variant="destructive" className="text-[10px]">Temsilci</Badge>
                                        )}
                                    </span>
                                    <span className="mt-1 block truncate text-xs text-muted-foreground">{c.last_message || "-"}</span>
                                    <span className="mt-0.5 block text-[11px] text-muted-foreground">
                                        {c.message_count} mesaj · {fmt(c.updated_at)}
                                    </span>
                                </button>
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            <div className="card-surface p-5">
                {!active ? (
                    <p className="text-sm text-muted-foreground" data-testid="wa-conversation-placeholder">
                        Soldan bir konuşma seçin.
                    </p>
                ) : (
                    <div data-testid="wa-conversation-detail">
                        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
                            <div>
                                <p className="font-heading text-base font-bold">{active.profile_name || active.wa_id}</p>
                                <p className="text-xs text-muted-foreground">
                                    +{active.wa_id} · son mesaj {fmt(active.last_inbound_at)}
                                </p>
                            </div>
                            <label className="flex items-center gap-2 text-sm">
                                <Switch
                                    checked={!!active.bot_enabled}
                                    onCheckedChange={(c) => toggleBot(!!c)}
                                    data-testid="wa-conversation-bot-switch"
                                />
                                {active.bot_enabled ? <Bot className="h-4 w-4" /> : <UserRound className="h-4 w-4" />}
                                {active.bot_enabled ? "Bot yanıtlıyor" : "Temsilci modu"}
                            </label>
                        </div>

                        <div className="mt-4 max-h-[420px] space-y-2 overflow-y-auto pr-1" data-testid="wa-conversation-messages">
                            {(active.messages || []).map((m, i) => (
                                <div
                                    key={`${m.at}-${i}`}
                                    className={`max-w-[80%] rounded-xl px-3 py-2 text-sm ${ROLE_STYLE[m.role] || "bg-muted/60"}`}
                                >
                                    <p className="whitespace-pre-wrap">{m.text}</p>
                                    <p className="mt-1 text-[11px] text-muted-foreground">
                                        {ROLE_LABEL[m.role] || m.role} · {fmt(m.at)}
                                    </p>
                                </div>
                            ))}
                        </div>

                        <div className="mt-4 space-y-2 border-t border-border pt-4">
                            <Textarea
                                rows={3}
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                placeholder="Müşteriye yazın (24 saatlik servis penceresi içinde gönderilebilir)"
                                data-testid="wa-conversation-reply-input"
                            />
                            <Button type="button" onClick={sendReply} disabled={sending || !text.trim()} data-testid="wa-conversation-send-button">
                                {sending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
                                Gönder
                            </Button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
