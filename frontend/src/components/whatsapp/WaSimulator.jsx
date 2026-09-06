import React, { useState } from "react";
import { FlaskConical, Loader2, Upload } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../../lib/api";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";

export const WaSimulator = () => {
    const [waId, setWaId] = useState("905000000000");
    const [name, setName] = useState("Test Müşteri");
    const [text, setText] = useState("Merhaba, 30 günlük Dubai vizesi ne kadar?");
    const [reply, setReply] = useState(null);
    const [busy, setBusy] = useState("");
    const [file, setFile] = useState(null);
    const [docResult, setDocResult] = useState(null);

    const sendMessage = async () => {
        setBusy("msg");
        setReply(null);
        try {
            const { data } = await api.post("/admin/whatsapp/ai/simulate/message", {
                wa_id: waId,
                text,
                profile_name: name,
            });
            setReply(data.reply);
            toast.success("Bot yanıtı üretildi.");
        } catch (e) {
            toast.error(apiError(e, "Simülasyon başarısız."));
        } finally {
            setBusy("");
        }
    };

    const sendDocument = async () => {
        if (!file) return toast.error("Önce bir PDF veya görsel seçin.");
        setBusy("doc");
        setDocResult(null);
        try {
            const fd = new FormData();
            fd.append("file", file);
            fd.append("from_wa_id", waId);
            const { data } = await api.post("/admin/whatsapp/ai/simulate/document", fd);
            setDocResult(data);
            toast.success(
                data.status === "delivered" ? "Belge eşleşti ve müşteriye iletildi." : "Belge kuyruğa alındı."
            );
        } catch (e) {
            toast.error(apiError(e, "Belge işlenemedi."));
        } finally {
            setBusy("");
        }
    };

    return (
        <div className="grid gap-4 lg:grid-cols-2" data-testid="wa-simulator-panel">
            <div className="card-surface p-6">
                <div className="flex items-center gap-2">
                    <FlaskConical className="h-4 w-4 text-primary" />
                    <h2 className="font-heading text-base font-bold">Müşteri mesajı simülasyonu</h2>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">
                    Meta onayı beklerken botun cevaplarını test edin. Gerçek WhatsApp mesajı gönderilmez.
                </p>
                <div className="mt-4 space-y-3">
                    <div className="space-y-2">
                        <Label htmlFor="sim-wa-id">Numara (ülke koduyla)</Label>
                        <Input id="sim-wa-id" value={waId} onChange={(e) => setWaId(e.target.value)} data-testid="wa-sim-waid-input" />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="sim-name">Profil adı</Label>
                        <Input id="sim-name" value={name} onChange={(e) => setName(e.target.value)} data-testid="wa-sim-name-input" />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="sim-text">Mesaj</Label>
                        <Textarea id="sim-text" rows={3} value={text} onChange={(e) => setText(e.target.value)} data-testid="wa-sim-text-input" />
                    </div>
                    <Button type="button" onClick={sendMessage} disabled={!!busy} data-testid="wa-sim-send-button">
                        {busy === "msg" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                        Botu çalıştır
                    </Button>
                </div>
                {reply && (
                    <div className="mt-4 rounded-lg border border-border bg-muted/40 p-3 text-sm" data-testid="wa-sim-reply">
                        <p className="text-xs font-semibold uppercase text-muted-foreground">
                            Bot yanıtı ({reply.source || reply.role})
                        </p>
                        <p className="mt-1 whitespace-pre-wrap">{reply.text}</p>
                    </div>
                )}
            </div>

            <div className="card-surface p-6">
                <div className="flex items-center gap-2">
                    <Upload className="h-4 w-4 text-primary" />
                    <h2 className="font-heading text-base font-bold">Tedarikçi belgesi simülasyonu</h2>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">
                    Bir vize PDF'i yükleyin; yapay zeka belgeyi okur, başvuruyla eşleştirir ve güven yüksekse
                    müşteriye e-posta + WhatsApp ile iletir.
                </p>
                <div className="mt-4 space-y-3">
                    <Input
                        type="file"
                        accept="application/pdf,image/*"
                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                        data-testid="wa-sim-file-input"
                    />
                    <Button type="button" onClick={sendDocument} disabled={!!busy} data-testid="wa-sim-upload-button">
                        {busy === "doc" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                        Belgeyi işle
                    </Button>
                </div>
                {docResult && (
                    <div className="mt-4 rounded-lg border border-border bg-muted/40 p-3 text-sm" data-testid="wa-sim-doc-result">
                        <p>
                            Durum: <b>{docResult.status || (docResult.ok ? "işlendi" : "başarısız")}</b>
                        </p>
                        <p className="text-xs text-muted-foreground">
                            Eşleşme: {docResult.match?.reference_code || "yok"} · güven %
                            {Math.round((docResult.match?.confidence || 0) * 100)} · {docResult.match?.reason || docResult.reason || "-"}
                        </p>
                        {docResult.delivery && (
                            <p className="text-xs text-muted-foreground">
                                E-posta: {docResult.delivery.email_status} · WhatsApp: {docResult.delivery.whatsapp_status}
                            </p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};
