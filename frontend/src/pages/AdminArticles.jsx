import React, { useEffect, useState } from "react";
import { ExternalLink, Loader2, Pencil, Plus, Save, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatDate } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { DateField } from "../components/DateField";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Switch } from "../components/ui/switch";
import {
    Dialog,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "../components/ui/dialog";

const emptyArticle = {
    title: "",
    slug: "",
    date: new Date().toISOString().slice(0, 10),
    excerpt: "",
    bodyText: "",
    published: true,
    order: 0,
};

export default function AdminArticles() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [open, setOpen] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState(emptyArticle);

    const load = () => {
        setLoading(true);
        api.get("/admin/articles")
            .then(({ data }) => setItems(data.items || []))
            .catch((e) => toast.error(apiError(e, "Yazılar yüklenemedi.")))
            .finally(() => setLoading(false));
    };

    useEffect(load, []);

    const openNew = () => {
        setEditing(null);
        setForm(emptyArticle);
        setOpen(true);
    };

    const openEdit = (a) => {
        setEditing(a);
        setForm({
            title: a.title || "",
            slug: a.slug || "",
            date: (a.date || "").slice(0, 10),
            excerpt: a.excerpt || "",
            bodyText: (a.body || []).join("\n\n"),
            published: a.published !== false,
            order: a.order || 0,
        });
        setOpen(true);
    };

    const save = async () => {
        if (form.title.trim().length < 5 || form.excerpt.trim().length < 20) {
            toast.error("Başlık en az 5, özet en az 20 karakter olmalı.");
            return;
        }
        setSaving(true);
        try {
            const payload = {
                title: form.title,
                slug: form.slug,
                date: form.date,
                excerpt: form.excerpt,
                body: form.bodyText.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean),
                published: form.published,
                order: Number(form.order) || 0,
            };
            if (editing) {
                await api.put(`/admin/articles/${editing.id}`, payload);
                toast.success("Yazı güncellendi.");
            } else {
                await api.post("/admin/articles", payload);
                toast.success("Yazı yayınlandı.");
            }
            setOpen(false);
            load();
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const remove = async (a) => {
        if (!window.confirm(`"${a.title}" yazısı silinsin mi?`)) return;
        try {
            await api.delete(`/admin/articles/${a.id}`);
            toast.success("Yazı silindi.");
            load();
        } catch (e) {
            toast.error(apiError(e, "Silinemedi."));
        }
    };

    return (
        <AdminLayout
            title="Blog Yazıları"
            description="Arama motorları için ayrı sayfada yayınlanan rehber yazılarını yönetin."
        >
            <div className="flex items-center justify-between gap-4">
                <h2 className="font-heading text-lg font-bold">Yazılar ({items.length})</h2>
                <Button onClick={openNew} className="h-11" data-testid="add-article-button">
                    <Plus className="mr-2 h-4 w-4" /> Yeni yazı
                </Button>
            </div>

            {loading ? (
                <div className="mt-6 flex justify-center py-10">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <div className="mt-5 space-y-4" data-testid="admin-articles-list">
                    {items.map((a) => (
                        <div key={a.id} className="card-surface flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between" data-testid={`admin-article-${a.id}`}>
                            <div className="min-w-0">
                                <p className="text-xs font-bold uppercase tracking-wider text-[hsl(var(--brand-copper))]">
                                    {formatDate(a.date)} {a.published === false ? "· TASLAK" : ""}
                                </p>
                                <h3 className="mt-1 font-heading text-base font-bold">{a.title}</h3>
                                <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{a.excerpt}</p>
                                <p className="mt-1 font-mono-code text-xs text-muted-foreground">/gelismeler/{a.slug}</p>
                            </div>
                            <div className="flex shrink-0 gap-2">
                                <Button asChild variant="secondary" className="h-9 border border-border">
                                    <a href={`/gelismeler/${a.slug}`} target="_blank" rel="noreferrer" data-testid={`view-article-${a.id}`}>
                                        <ExternalLink className="h-3.5 w-3.5" />
                                    </a>
                                </Button>
                                <Button variant="secondary" className="h-9 border border-border" onClick={() => openEdit(a)} data-testid={`edit-article-${a.id}`}>
                                    <Pencil className="mr-2 h-3.5 w-3.5" /> Düzenle
                                </Button>
                                <Button variant="destructive" className="h-9" onClick={() => remove(a)} data-testid={`delete-article-${a.id}`}>
                                    <Trash2 className="h-3.5 w-3.5" />
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
                    <DialogHeader>
                        <DialogTitle>{editing ? "Yazıyı düzenle" : "Yeni yazı"}</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4">
                        <div>
                            <Label>Başlık *</Label>
                            <Input value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} data-testid="article-title-input" />
                        </div>
                        <div className="grid gap-4 sm:grid-cols-2">
                            <div>
                                <Label>URL adresi (boş bırakılırsa başlıktan oluşur)</Label>
                                <Input value={form.slug} onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))} placeholder="dubai-vize-rehberi" data-testid="article-slug-input" />
                            </div>
                            <div>
                                <Label>Yayın tarihi</Label>
                                <DateField value={form.date} onChange={(iso) => setForm((f) => ({ ...f, date: iso }))} data-testid="article-date-input" />
                            </div>
                        </div>
                        <div>
                            <Label>Özet (arama sonuçlarında görünür) *</Label>
                            <Textarea rows={2} value={form.excerpt} onChange={(e) => setForm((f) => ({ ...f, excerpt: e.target.value }))} data-testid="article-excerpt-input" />
                        </div>
                        <div>
                            <Label>Yazı metni (paragrafları boş satırla ayırın)</Label>
                            <Textarea rows={10} value={form.bodyText} onChange={(e) => setForm((f) => ({ ...f, bodyText: e.target.value }))} data-testid="article-body-input" />
                        </div>
                        <label className="flex items-center gap-2 text-sm font-medium">
                            <Switch checked={!!form.published} onCheckedChange={(v) => setForm((f) => ({ ...f, published: v }))} data-testid="article-published-switch" />
                            Sitede yayınla
                        </label>
                    </div>
                    <DialogFooter>
                        <Button variant="secondary" className="h-11 border border-border" onClick={() => setOpen(false)}>
                            Vazgeç
                        </Button>
                        <Button onClick={save} disabled={saving} className="h-11" data-testid="save-article-button">
                            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                            Kaydet
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </AdminLayout>
    );
}
