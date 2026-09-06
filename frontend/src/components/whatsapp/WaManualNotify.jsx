import React, { useEffect, useState } from "react";
import { Loader2, Save } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../../lib/api";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { Switch } from "../ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select";

const PROVIDERS = [
    { value: "manual", label: "Manuel (anahtar gerekmez · hazır WhatsApp bağlantısı)" },
    { value: "meta", label: "Meta WhatsApp Cloud API" },
    { value: "twilio", label: "Twilio WhatsApp" },
];

export const WaManualNotify = () => {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [s, setS] = useState(null);
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        (async () => {
            try {
                const [cfg, log] = await Promise.all([
                    api.get("/admin/whatsapp/settings"),
                    api.get("/admin/whatsapp/logs"),
                ]);
                setS({ ...cfg.data.settings, meta_access_token: "", twilio_auth_token: "" });
                setLogs(log.data.items || []);
            } catch (e) {
                toast.error(apiError(e, "Ayarlar yüklenemedi."));
            } finally {
                setLoading(false);
            }
        })();
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
            toast.success("WhatsApp bildirim ayarları kaydedildi.");
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const set = (key) => (e) => setS((v) => ({ ...v, [key]: e.target.value }));

    if (loading || !s) {
        return (
            <div className="flex justify-center py-12">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="card-surface p-6" data-testid="whatsapp-settings-form">
                <h2 className="font-heading text-base font-bold">Vize sonucu bildirimi</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                    Vize sonucu (onay/ret) çıktığında müşteriye gönderilen mesaj. Manuel modda hiçbir anahtar gerekmez.
                </p>

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

            <div className="card-surface p-6" data-testid="whatsapp-logs">
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
                                <span className="text-muted-foreground">{l.provider} / {l.result}</span>
                                <span className="block text-xs text-muted-foreground">
                                    {l.created_at ? new Date(l.created_at).toLocaleString("tr-TR") : ""}
                                </span>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};
