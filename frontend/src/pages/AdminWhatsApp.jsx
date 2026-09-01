import React, { useEffect, useState } from "react";
import { Loader2, MessageCircle, Save } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Switch } from "../components/ui/switch";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";

const PROVIDERS = [
    { value: "manual", label: "Manuel (anahtar gerekmez · hazır WhatsApp bağlantısı)" },
    { value: "meta", label: "Meta WhatsApp Cloud API" },
    { value: "twilio", label: "Twilio WhatsApp" },
];

export default function AdminWhatsApp() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [s, setS] = useState(null);
    const [logs, setLogs] = useState([]);

    const load = async () => {
        try {
            const { data } = await api.get("/admin/whatsapp/settings");
            setS({ ...data.settings, meta_access_token: "", twilio_auth_token: "" });
        } catch (e) {
            toast.error(apiError(e, "Ayarlar yüklenemedi."));
        } finally {
            setLoading(false);
        }
    };

    const loadLogs = async () => {
        try {
            const { data } = await api.get("/admin/whatsapp/logs");
            setLogs(data.items || []);
        } catch {
            /* sessiz */
        }
    };

    useEffect(() => {
        load();
        loadLogs();
    }, []);

    const save = async () => {
        setSaving(true);
        try {
            const body = { ...s };
            if (!body.meta_access_token) delete body.meta_access_token;
            if (!body.twilio_auth_token) delete body.twilio_auth_token;
            delete body.has_meta_token;
            delete body.has_twilio_token;
            const { data } = await api.put("/admin/whatsapp/settings", body);
            setS({ ...data.settings, meta_access_token: "", twilio_auth_token: "" });
            toast.success("WhatsApp ayarları kaydedildi.");
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const set = (key) => (e) => setS((v) => ({ ...v, [key]: e.target.value }));

    return (
        <AdminLayout
            title="WhatsApp Bildirimleri"
            description="Vize sonucu (onay/ret) çıktığında müşteriye WhatsApp mesajı gönderin. Manuel modda hiçbir anahtar gerekmez."
        >
            {loading || !s ? (
                <div className="flex justify-center py-16">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <div className="space-y-6">
                    <div className="card-surface max-w-4xl p-6" data-testid="whatsapp-settings-form">
                        <div className="flex items-center gap-2">
                            <MessageCircle className="h-4.5 w-4.5 text-primary" />
                            <h2 className="font-heading text-base font-bold">Genel</h2>
                        </div>

                        <div className="mt-5 flex flex-wrap items-center gap-6">
                            <label className="flex items-center gap-3 text-sm">
                                <Switch
                                    checked={!!s.enabled}
                                    onCheckedChange={(c) => setS((v) => ({ ...v, enabled: !!c }))}
                                    data-testid="whatsapp-enabled-switch"
                                />
                                Bildirimleri aç
                            </label>
                            <label className="flex items-center gap-3 text-sm">
                                <Switch
                                    checked={!!s.only_optin}
                                    onCheckedChange={(c) => setS((v) => ({ ...v, only_optin: !!c }))}
                                    data-testid="whatsapp-optin-switch"
                                />
                                Sadece onay veren müşterilere otomatik gönder (KVKK)
                            </label>
                        </div>

                        <div className="mt-5 grid gap-4 md:grid-cols-2">
                            <div className="space-y-2">
                                <Label>Sağlayıcı</Label>
                                <Select value={s.provider} onValueChange={(v) => setS((x) => ({ ...x, provider: v }))}>
                                    <SelectTrigger data-testid="whatsapp-provider-select">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {PROVIDERS.map((p) => (
                                            <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="wa-template">Mesaj metni</Label>
                                <Textarea
                                    id="wa-template"
                                    rows={3}
                                    value={s.template_text || ""}
                                    onChange={set("template_text")}
                                    data-testid="whatsapp-template-input"
                                />
                                <p className="text-xs text-muted-foreground">
                                    Kullanılabilir alanlar: {"{name}"} {"{status}"} {"{reference}"} {"{link}"}
                                </p>
                            </div>
                        </div>

                        {s.provider === "meta" && (
                            <div className="mt-6 grid gap-4 md:grid-cols-2" data-testid="whatsapp-meta-fields">
                                <div className="space-y-2">
                                    <Label htmlFor="wa-meta-id">Phone Number ID</Label>
                                    <Input id="wa-meta-id" value={s.meta_phone_number_id || ""} onChange={set("meta_phone_number_id")} data-testid="whatsapp-meta-phone-id" />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="wa-meta-token">
                                        Access Token {s.has_meta_token ? "(kayıtlı · değiştirmek için yazın)" : ""}
                                    </Label>
                                    <Input id="wa-meta-token" type="password" value={s.meta_access_token || ""} onChange={set("meta_access_token")} placeholder="EAAG..." data-testid="whatsapp-meta-token" />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="wa-meta-tpl">Şablon adı</Label>
                                    <Input id="wa-meta-tpl" value={s.meta_template_name || ""} onChange={set("meta_template_name")} data-testid="whatsapp-meta-template" />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="wa-meta-lang">Şablon dili</Label>
                                    <Input id="wa-meta-lang" value={s.meta_template_language || ""} onChange={set("meta_template_language")} data-testid="whatsapp-meta-language" />
                                </div>
                            </div>
                        )}

                        {s.provider === "twilio" && (
                            <div className="mt-6 grid gap-4 md:grid-cols-2" data-testid="whatsapp-twilio-fields">
                                <div className="space-y-2">
                                    <Label htmlFor="wa-tw-sid">Account SID</Label>
                                    <Input id="wa-tw-sid" value={s.twilio_account_sid || ""} onChange={set("twilio_account_sid")} placeholder="AC..." data-testid="whatsapp-twilio-sid" />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="wa-tw-token">
                                        Auth Token {s.has_twilio_token ? "(kayıtlı · değiştirmek için yazın)" : ""}
                                    </Label>
                                    <Input id="wa-tw-token" type="password" value={s.twilio_auth_token || ""} onChange={set("twilio_auth_token")} data-testid="whatsapp-twilio-token" />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="wa-tw-from">Gönderici numara</Label>
                                    <Input id="wa-tw-from" value={s.twilio_whatsapp_from || ""} onChange={set("twilio_whatsapp_from")} placeholder="whatsapp:+14155238886" data-testid="whatsapp-twilio-from" />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="wa-tw-content">Content SID (şablon)</Label>
                                    <Input id="wa-tw-content" value={s.twilio_content_sid || ""} onChange={set("twilio_content_sid")} placeholder="HX..." data-testid="whatsapp-twilio-content" />
                                </div>
                            </div>
                        )}

                        <div className="mt-6">
                            <Button type="button" onClick={save} disabled={saving} data-testid="whatsapp-save-button">
                                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                                Kaydet
                            </Button>
                        </div>
                    </div>

                    <div className="card-surface max-w-4xl p-6" data-testid="whatsapp-logs">
                        <h2 className="font-heading text-base font-bold">Son bildirimler</h2>
                        {logs.length === 0 ? (
                            <p className="mt-3 text-sm text-muted-foreground" data-testid="whatsapp-logs-empty">
                                Henüz WhatsApp bildirimi yok.
                            </p>
                        ) : (
                            <ul className="mt-4 space-y-2">
                                {logs.map((l) => (
                                    <li key={l.id} className="rounded-lg border border-border p-3 text-sm" data-testid={`whatsapp-log-${l.id}`}>
                                        <span className="font-semibold">{l.reference_code || "-"}</span> · {l.status} ·{" "}
                                        <span className="text-muted-foreground">
                                            {l.provider} / {l.result}
                                        </span>
                                        <span className="block text-xs text-muted-foreground">
                                            {l.created_at ? new Date(l.created_at).toLocaleString("tr-TR") : ""}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </div>
            )}
        </AdminLayout>
    );
}
