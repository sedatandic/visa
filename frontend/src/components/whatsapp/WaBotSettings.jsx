import React, { useEffect, useState } from "react";
import { Copy, Link2, Loader2, Save, Users } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../../lib/api";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Switch } from "../ui/switch";

const WEBHOOK_URL = `${process.env.REACT_APP_BACKEND_URL}/api/whatsapp/webhook`;

const TEXT_FIELDS = [
    { key: "phone_number_id", label: "Phone Number ID", ph: "123456789012345" },
    { key: "waba_id", label: "WhatsApp Business Account ID", ph: "" },
    { key: "verify_token", label: "Webhook doğrulama anahtarı", ph: "dubai-vize-hatti" },
    { key: "graph_version", label: "Graph API sürümü", ph: "v25.0" },
    { key: "supplier_group_id", label: "Tedarikçi grup kimliği", ph: "grup oluşturunca dolar" },
    { key: "supplier_numbers", label: "Tedarikçi numaraları (virgülle)", ph: "9715xxxxxxxx, 9055xxxxxxxx" },
    { key: "visa_template_name", label: "Vize şablon adı", ph: "vize_hazir" },
    { key: "visa_template_language", label: "Şablon dili", ph: "tr" },
];

export const WaBotSettings = ({ config, onSaved }) => {
    const [form, setForm] = useState(null);
    const [busy, setBusy] = useState("");

    useEffect(() => {
        if (config) setForm({ ...config, access_token: "", app_secret: "" });
    }, [config]);

    if (!form) {
        return (
            <div className="flex justify-center py-12">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
            </div>
        );
    }

    const set = (key) => (e) => setForm((v) => ({ ...v, [key]: e.target.value }));

    const save = async () => {
        setBusy("save");
        try {
            const body = {};
            [...TEXT_FIELDS.map((f) => f.key), "bot_enabled", "auto_deliver"].forEach((k) => {
                body[k] = form[k];
            });
            if (form.access_token) body.access_token = form.access_token;
            if (form.app_secret) body.app_secret = form.app_secret;
            const { data } = await api.put("/admin/whatsapp/ai/config", body);
            toast.success(data.ready ? "Kaydedildi · canlı mod aktif." : "Kaydedildi · simülasyon modunda.");
            onSaved(data);
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setBusy("");
        }
    };

    const createGroup = async () => {
        setBusy("group");
        try {
            const fd = new FormData();
            fd.append("subject", "Dubai Vize Hatti - Tedarikci Belgeleri");
            const { data } = await api.post("/admin/whatsapp/ai/group", fd);
            toast.success(`Grup oluşturuldu: ${data.group_id}`);
            setForm((v) => ({ ...v, supplier_group_id: data.group_id }));
        } catch (e) {
            toast.error(apiError(e, "Grup oluşturulamadı."));
        } finally {
            setBusy("");
        }
    };

    const getInvite = async () => {
        setBusy("invite");
        try {
            const { data } = await api.get("/admin/whatsapp/ai/group/invite");
            await navigator.clipboard.writeText(data.invite_link || "");
            toast.success("Davet bağlantısı kopyalandı.");
        } catch (e) {
            toast.error(apiError(e, "Davet bağlantısı alınamadı."));
        } finally {
            setBusy("");
        }
    };

    return (
        <div className="space-y-6" data-testid="wa-settings-panel">
            <div className="card-surface p-6">
                <h2 className="font-heading text-base font-bold">Webhook</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                    Meta Developer → WhatsApp → Configuration ekranına bu adresi ve doğrulama anahtarını girin.
                </p>
                <div className="mt-4 flex flex-wrap items-center gap-2">
                    <code className="flex-1 break-all rounded-lg border border-border bg-muted/40 px-3 py-2 text-xs" data-testid="wa-webhook-url">
                        {WEBHOOK_URL}
                    </code>
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                            navigator.clipboard.writeText(WEBHOOK_URL);
                            toast.success("Webhook adresi kopyalandı.");
                        }}
                        data-testid="wa-copy-webhook-button"
                    >
                        <Copy className="mr-2 h-4 w-4" /> Kopyala
                    </Button>
                </div>
            </div>

            <div className="card-surface p-6">
                <h2 className="font-heading text-base font-bold">Bot davranışı</h2>
                <div className="mt-4 flex flex-wrap gap-6">
                    <label className="flex items-center gap-3 text-sm">
                        <Switch
                            checked={!!form.bot_enabled}
                            onCheckedChange={(c) => setForm((v) => ({ ...v, bot_enabled: !!c }))}
                            data-testid="wa-bot-enabled-switch"
                        />
                        Yapay zeka botu müşterilere otomatik yanıt versin
                    </label>
                    <label className="flex items-center gap-3 text-sm">
                        <Switch
                            checked={!!form.auto_deliver}
                            onCheckedChange={(c) => setForm((v) => ({ ...v, auto_deliver: !!c }))}
                            data-testid="wa-auto-deliver-switch"
                        />
                        Eşleşme güveni yüksekse belgeyi müşteriye otomatik gönder
                    </label>
                </div>
            </div>

            <div className="card-surface p-6">
                <h2 className="font-heading text-base font-bold">Meta Cloud API kimlik bilgileri</h2>
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                    {TEXT_FIELDS.map((f) => (
                        <div key={f.key} className="space-y-2">
                            <Label htmlFor={`wa-${f.key}`}>{f.label}</Label>
                            <Input
                                id={`wa-${f.key}`}
                                value={form[f.key] || ""}
                                placeholder={f.ph}
                                onChange={set(f.key)}
                                data-testid={`wa-field-${f.key}`}
                            />
                        </div>
                    ))}
                    <div className="space-y-2">
                        <Label htmlFor="wa-access-token">
                            Access Token {form.has_access_token ? "(kayıtlı · değiştirmek için yazın)" : ""}
                        </Label>
                        <Input
                            id="wa-access-token"
                            type="password"
                            value={form.access_token}
                            placeholder="EAAG..."
                            onChange={set("access_token")}
                            data-testid="wa-field-access-token"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="wa-app-secret">
                            App Secret {form.has_app_secret ? "(kayıtlı · değiştirmek için yazın)" : ""}
                        </Label>
                        <Input
                            id="wa-app-secret"
                            type="password"
                            value={form.app_secret}
                            onChange={set("app_secret")}
                            data-testid="wa-field-app-secret"
                        />
                    </div>
                </div>

                <div className="mt-6 flex flex-wrap gap-3">
                    <Button type="button" onClick={save} disabled={!!busy} data-testid="wa-settings-save-button">
                        {busy === "save" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                        Kaydet
                    </Button>
                    <Button type="button" variant="outline" onClick={createGroup} disabled={!!busy} data-testid="wa-create-group-button">
                        {busy === "group" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Users className="mr-2 h-4 w-4" />}
                        Tedarikçi grubu oluştur
                    </Button>
                    <Button type="button" variant="outline" onClick={getInvite} disabled={!!busy} data-testid="wa-group-invite-button">
                        {busy === "invite" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Link2 className="mr-2 h-4 w-4" />}
                        Davet bağlantısını kopyala
                    </Button>
                </div>
                <p className="mt-3 text-xs text-muted-foreground">
                    Grup kurma özelliği Meta tarafında Resmî İşletme Hesabı (mavi tik) gerektirir. Grup açılamıyorsa
                    tedarikçi numaralarını yukarıdaki alana yazmanız yeterlidir; belgeler doğrudan mesajdan da işlenir.
                </p>
            </div>
        </div>
    );
};
