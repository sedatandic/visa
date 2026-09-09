import React, { useEffect, useState } from "react";
import { ExternalLink, Loader2, Save, Share2 } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { AdminLayout } from "../components/AdminLayout";
import { SocialIcon } from "../components/SocialIcons";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";
import { Checkbox } from "../components/ui/checkbox";

const PLACEMENTS = [
    { key: "in_dock", label: "Sağ alt buton" },
    { key: "in_footer", label: "Alt bilgi" },
    { key: "in_contact", label: "İletişim sayfası" },
];

const SocialRow = ({ platform, item, onChange }) => (
    <div
        className="rounded-2xl border border-border bg-card p-4 sm:p-5"
        data-testid={`social-row-${platform.id}`}
    >
        <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <SocialIcon platform={platform.id} />
                </span>
                <div>
                    <p className="font-heading text-base font-bold">{platform.label}</p>
                    <p className="text-xs text-muted-foreground">
                        {item.url ? (item.enabled ? "Yayında" : "Kapalı") : "Bağlantı girilmedi"}
                    </p>
                </div>
            </div>
            <div className="flex items-center gap-2.5">
                <Label htmlFor={`social-enabled-${platform.id}`} className="text-xs">
                    Yayında
                </Label>
                <Switch
                    id={`social-enabled-${platform.id}`}
                    checked={!!item.enabled}
                    disabled={!item.url}
                    onCheckedChange={(v) => onChange({ enabled: !!v })}
                    data-testid={`social-enabled-${platform.id}`}
                />
            </div>
        </div>

        <div className="mt-4 flex flex-col gap-2 sm:flex-row sm:items-center">
            <Input
                value={item.url || ""}
                placeholder={platform.placeholder}
                onChange={(e) => onChange({ url: e.target.value })}
                data-testid={`social-url-${platform.id}`}
            />
            <Button
                asChild={!!item.url}
                variant="secondary"
                disabled={!item.url}
                className="h-11 shrink-0 border border-border"
                data-testid={`social-test-${platform.id}`}
            >
                {item.url ? (
                    <a href={item.url} target="_blank" rel="noreferrer">
                        <ExternalLink className="mr-2 h-4 w-4" /> Bağlantıyı test et
                    </a>
                ) : (
                    <span>
                        <ExternalLink className="mr-2 h-4 w-4" /> Bağlantıyı test et
                    </span>
                )}
            </Button>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-3">
            {PLACEMENTS.map((p) => (
                <label
                    key={p.key}
                    className="flex cursor-pointer items-center gap-2 text-sm text-muted-foreground"
                >
                    <Checkbox
                        checked={!!item[p.key]}
                        onCheckedChange={(v) => onChange({ [p.key]: !!v })}
                        data-testid={`social-${p.key}-${platform.id}`}
                    />
                    {p.label}
                </label>
            ))}
            <span className="ml-auto flex items-center gap-2 text-sm text-muted-foreground">
                Sıra
                <Input
                    type="number"
                    min={0}
                    max={99}
                    value={item.order ?? 0}
                    onChange={(e) => onChange({ order: Number(e.target.value) })}
                    className="h-9 w-16"
                    data-testid={`social-order-${platform.id}`}
                />
            </span>
        </div>
    </div>
);

export default function AdminSocial() {
    const [platforms, setPlatforms] = useState([]);
    const [items, setItems] = useState({});
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    const apply = ({ platforms: list, items: rows }) => {
        setPlatforms(list || []);
        setItems(Object.fromEntries((rows || []).map((r) => [r.platform, r])));
    };

    useEffect(() => {
        api.get("/admin/social")
            .then(({ data }) => apply(data))
            .catch((e) => toast.error(apiError(e, "Sosyal medya hesapları yüklenemedi.")))
            .finally(() => setLoading(false));
    }, []);

    const update = (platform, patch) =>
        setItems((prev) => {
            const next = { ...prev[platform], ...patch };
            if (patch.url !== undefined && !patch.url.trim()) next.enabled = false;
            if (patch.url !== undefined && patch.url.trim() && prev[platform]?.url === "") {
                next.enabled = true;
            }
            return { ...prev, [platform]: next };
        });

    const save = async () => {
        setSaving(true);
        try {
            const { data } = await api.put("/admin/social", {
                items: platforms.map((p) => ({ platform: p.id, ...items[p.id] })),
            });
            apply(data);
            toast.success("Sosyal medya hesapları güncellendi.");
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const liveCount = Object.values(items).filter((i) => i.enabled && i.url).length;

    return (
        <AdminLayout
            title="Sosyal Medya"
            description="Hesaplarınızın sitede nerede görüneceğini buradan yönetin. Bağlantı girilmeyen platform sitede hiç gösterilmez."
        >
            {loading ? (
                <div className="flex justify-center py-16">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <div className="max-w-4xl" data-testid="admin-social-page">
                    <div className="card-surface flex flex-wrap items-center justify-between gap-4 p-5">
                        <div className="flex items-center gap-3">
                            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                                <Share2 className="h-5 w-5 text-primary" />
                            </span>
                            <div>
                                <h2 className="font-heading text-lg font-bold">Hesaplar</h2>
                                <p className="text-xs text-muted-foreground" data-testid="social-live-count">
                                    {liveCount} hesap sitede yayında
                                </p>
                            </div>
                        </div>
                        <Button onClick={save} disabled={saving} className="h-11" data-testid="save-social-button">
                            {saving ? (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            ) : (
                                <Save className="mr-2 h-4 w-4" />
                            )}
                            Kaydet
                        </Button>
                    </div>

                    <div className="mt-5 space-y-4">
                        {platforms.map((p) => (
                            <SocialRow
                                key={p.id}
                                platform={p}
                                item={items[p.id] || {}}
                                onChange={(patch) => update(p.id, patch)}
                            />
                        ))}
                    </div>

                    <p className="mt-5 text-xs leading-6 text-muted-foreground">
                        Kullanıcı adı yazmanız yeterli; tam adresi otomatik tamamlıyoruz
                        (örn. Instagram için <strong>dubaivizehatti</strong>). Google Yorumları
                        için İşletme Profili'nizdeki "Yorum isteyin" bağlantısını
                        (<strong>g.page/r/...</strong>) yapıştırın.
                    </p>
                </div>
            )}
        </AdminLayout>
    );
}
