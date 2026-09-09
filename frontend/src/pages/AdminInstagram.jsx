import React, { useEffect, useMemo, useState } from "react";
import { Check, Copy, Download, Instagram, Loader2, Save } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { Switch } from "../components/ui/switch";
import { Label } from "../components/ui/label";

const toLocalInput = (iso) => {
    if (!iso) return "";
    const d = new Date(iso);
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

const dayLabel = (iso) =>
    new Date(iso).toLocaleDateString("tr-TR", {
        day: "numeric",
        month: "long",
        weekday: "long",
    });

const copy = async (text, message) => {
    try {
        await navigator.clipboard.writeText(text);
        toast.success(message);
    } catch {
        toast.error("Kopyalanamadı, metni elle seçebilirsiniz.");
    }
};

const ProfileCard = ({ profile }) => (
    <div className="card-surface p-6" data-testid="instagram-profile-card">
        <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10">
                <Instagram className="h-5 w-5 text-primary" />
            </span>
            <div>
                <h2 className="font-heading text-lg font-bold">Hesap kurulumu</h2>
                <p className="text-xs text-muted-foreground">
                    Hesabı siz açıyorsunuz; şifre yalnızca sizde kalır.
                </p>
            </div>
        </div>

        <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                <p className="text-xs text-muted-foreground">Kullanıcı adı</p>
                <p className="mt-1 font-heading text-base font-bold" data-testid="instagram-username">
                    @{profile.username}
                </p>
                <p className="mt-3 text-xs text-muted-foreground">Kategori</p>
                <p className="mt-1 text-sm font-semibold">{profile.category}</p>
            </div>
            <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                <p className="text-xs text-muted-foreground">Biyografi</p>
                <pre className="mt-1 whitespace-pre-wrap font-sans text-sm leading-6">{profile.bio}</pre>
                <Button
                    variant="secondary"
                    className="mt-3 h-9 border border-border"
                    onClick={() => copy(profile.bio, "Biyografi kopyalandı.")}
                    data-testid="copy-bio-button"
                >
                    <Copy className="mr-2 h-3.5 w-3.5" /> Biyografiyi kopyala
                </Button>
            </div>
        </div>

        <ol className="mt-4 space-y-2 text-sm leading-6 text-muted-foreground">
            {(profile.steps || []).map((step, i) => (
                <li key={i} className="flex gap-2.5">
                    <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[11px] font-bold text-primary">
                        {i + 1}
                    </span>
                    {step}
                </li>
            ))}
        </ol>
    </div>
);

const PostCard = ({ post, onChange }) => {
    const fullText = `${post.caption}\n\n${post.hashtags}`;
    return (
        <div
            className={`card-surface overflow-hidden ${post.status === "posted" ? "opacity-70" : ""}`}
            data-testid={`instagram-post-${post.id}`}
        >
            <div className="grid gap-5 p-5 sm:grid-cols-[180px_1fr]">
                <a href={post.image} target="_blank" rel="noreferrer" className="block">
                    <img
                        src={post.image}
                        alt={post.title}
                        loading="lazy"
                        className="w-full rounded-xl border border-border"
                        data-testid={`instagram-image-${post.id}`}
                    />
                </a>

                <div className="min-w-0">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                            <p className="eyebrow" data-testid={`instagram-day-${post.id}`}>
                                {dayLabel(post.scheduled_at)}
                            </p>
                            <h3 className="mt-1 font-heading text-base font-bold">{post.title}</h3>
                        </div>
                        <div className="flex items-center gap-2.5">
                            <Label htmlFor={`posted-${post.id}`} className="text-xs">
                                Paylaşıldı
                            </Label>
                            <Switch
                                id={`posted-${post.id}`}
                                checked={post.status === "posted"}
                                onCheckedChange={(v) => onChange({ status: v ? "posted" : "planned" })}
                                data-testid={`instagram-posted-${post.id}`}
                            />
                        </div>
                    </div>

                    <Input
                        type="datetime-local"
                        value={toLocalInput(post.scheduled_at)}
                        onChange={(e) =>
                            onChange({ scheduled_at: new Date(e.target.value).toISOString() })
                        }
                        className="mt-3 sm:max-w-[240px]"
                        data-testid={`instagram-date-${post.id}`}
                    />

                    <Textarea
                        value={post.caption}
                        rows={6}
                        onChange={(e) => onChange({ caption: e.target.value })}
                        className="mt-3"
                        data-testid={`instagram-caption-${post.id}`}
                    />
                    <p className="mt-2 break-words text-xs leading-5 text-muted-foreground">
                        {post.hashtags}
                    </p>

                    <div className="mt-3 flex flex-wrap gap-2.5">
                        <Button
                            variant="secondary"
                            className="h-10 border border-border"
                            onClick={() => copy(fullText, "Açıklama ve hashtagler kopyalandı.")}
                            data-testid={`instagram-copy-${post.id}`}
                        >
                            <Copy className="mr-2 h-4 w-4" /> Metni kopyala
                        </Button>
                        <Button asChild variant="secondary" className="h-10 border border-border">
                            <a
                                href={post.image}
                                download={`${post.id}.jpg`}
                                data-testid={`instagram-download-${post.id}`}
                            >
                                <Download className="mr-2 h-4 w-4" /> Görseli indir
                            </a>
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default function AdminInstagram() {
    const [profile, setProfile] = useState(null);
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        api.get("/admin/instagram")
            .then(({ data }) => {
                setProfile(data.profile);
                setPosts(data.posts || []);
            })
            .catch((e) => toast.error(apiError(e, "Instagram takvimi yüklenemedi.")))
            .finally(() => setLoading(false));
    }, []);

    const update = (id, patch) =>
        setPosts((prev) => prev.map((p) => (p.id === id ? { ...p, ...patch } : p)));

    const save = async () => {
        setSaving(true);
        try {
            const { data } = await api.put("/admin/instagram", {
                items: posts.map(({ id, scheduled_at, caption, status }) => ({
                    id,
                    scheduled_at,
                    caption,
                    status,
                })),
            });
            setPosts(data.posts || []);
            toast.success("Takvim kaydedildi.");
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const pending = useMemo(() => posts.filter((p) => p.status !== "posted").length, [posts]);

    return (
        <AdminLayout
            title="Instagram Takvimi"
            description="12 hazır gönderi: görseli indirin, metni kopyalayın, Instagram'da paylaşın. Paylaştığınızı işaretleyin."
        >
            {loading ? (
                <div className="flex justify-center py-16">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <div className="max-w-5xl space-y-5" data-testid="admin-instagram-page">
                    <ProfileCard profile={profile || {}} />

                    <div className="card-surface flex flex-wrap items-center justify-between gap-4 p-5">
                        <p className="text-sm font-semibold" data-testid="instagram-pending-count">
                            {pending === 0 ? (
                                <span className="flex items-center gap-2 text-[hsl(var(--brand-green))]">
                                    <Check className="h-4 w-4" /> Tüm gönderiler paylaşıldı
                                </span>
                            ) : (
                                `${pending} gönderi paylaşılmayı bekliyor`
                            )}
                        </p>
                        <Button onClick={save} disabled={saving} className="h-11" data-testid="save-instagram-button">
                            {saving ? (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            ) : (
                                <Save className="mr-2 h-4 w-4" />
                            )}
                            Takvimi kaydet
                        </Button>
                    </div>

                    {posts.map((post) => (
                        <PostCard key={post.id} post={post} onChange={(patch) => update(post.id, patch)} />
                    ))}
                </div>
            )}
        </AdminLayout>
    );
}
