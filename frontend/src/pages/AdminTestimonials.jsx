import React, { useEffect, useState } from "react";
import { Loader2, Pencil, Plus, Save, Star, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
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

const emptyItem = {
    name: "",
    initials: "",
    city: "",
    visa: "",
    date: new Date().toISOString().slice(0, 10),
    text: "",
    rating: 5,
    verified: true,
    published: true,
    order: 0,
};

export default function AdminTestimonials() {
    const [items, setItems] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [open, setOpen] = useState(false);
    const [editing, setEditing] = useState(null);
    const [form, setForm] = useState(emptyItem);

    const load = () => {
        setLoading(true);
        api.get("/admin/testimonials")
            .then(({ data }) => {
                setItems(data.items || []);
                setSummary(
                    data.review_summary && Object.keys(data.review_summary).length
                        ? data.review_summary
                        : { average: 4.9, total_reviews: 0, total_applications: 0, recommend_rate: 95, highlights: [] }
                );
            })
            .catch((e) => toast.error(apiError(e, "Yorumlar yüklenemedi.")))
            .finally(() => setLoading(false));
    };

    useEffect(load, []);

    const openNew = () => {
        setEditing(null);
        setForm(emptyItem);
        setOpen(true);
    };

    const openEdit = (item) => {
        setEditing(item);
        setForm({ ...emptyItem, ...item });
        setOpen(true);
    };

    const save = async () => {
        if (!form.name.trim() || form.text.trim().length < 10) {
            toast.error("İsim ve en az 10 karakterlik yorum metni gerekli.");
            return;
        }
        setSaving(true);
        try {
            const payload = {
                ...form,
                rating: Number(form.rating) || 5,
                order: Number(form.order) || 0,
            };
            if (editing) {
                await api.put(`/admin/testimonials/${editing.id}`, payload);
                toast.success("Yorum güncellendi.");
            } else {
                await api.post("/admin/testimonials", payload);
                toast.success("Yorum eklendi.");
            }
            setOpen(false);
            load();
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const remove = async (item) => {
        if (!window.confirm(`"${item.name}" yorumu silinsin mi?`)) return;
        try {
            await api.delete(`/admin/testimonials/${item.id}`);
            toast.success("Yorum silindi.");
            load();
        } catch (e) {
            toast.error(apiError(e, "Silinemedi."));
        }
    };

    const saveSummary = async () => {
        setSaving(true);
        try {
            await api.put("/admin/review-summary", {
                average: Number(summary.average) || 0,
                total_reviews: Number(summary.total_reviews) || 0,
                total_applications: Number(summary.total_applications) || 0,
                recommend_rate: Number(summary.recommend_rate) || 0,
                highlights: (summary.highlights || []).map((h) => ({
                    label: h.label,
                    value: Number(h.value) || 0,
                })),
            });
            toast.success("Puan özeti güncellendi.");
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const setH = (idx, key, value) =>
        setSummary((s) => ({
            ...s,
            highlights: (s.highlights || []).map((h, i) => (i === idx ? { ...h, [key]: value } : h)),
        }));

    return (
        <AdminLayout
            title="Müşteri Yorumları"
            description="Ana sayfada görünen yorumları ve puan özetini buradan yönetin."
        >
            {summary && (
                <div className="card-surface p-6" data-testid="admin-review-summary-card">
                    <h2 className="font-heading text-lg font-bold">Puan özeti</h2>
                    <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                        <div>
                            <Label>Ortalama puan (0-5)</Label>
                            <Input
                                type="number" step="0.1" min="0" max="5"
                                value={summary.average}
                                onChange={(e) => setSummary((s) => ({ ...s, average: e.target.value }))}
                                data-testid="summary-average-input"
                            />
                        </div>
                        <div>
                            <Label>Değerlendirme sayısı</Label>
                            <Input
                                type="number" min="0"
                                value={summary.total_reviews}
                                onChange={(e) => setSummary((s) => ({ ...s, total_reviews: e.target.value }))}
                                data-testid="summary-reviews-input"
                            />
                        </div>
                        <div>
                            <Label>Tamamlanan başvuru</Label>
                            <Input
                                type="number" min="0"
                                value={summary.total_applications}
                                onChange={(e) => setSummary((s) => ({ ...s, total_applications: e.target.value }))}
                                data-testid="summary-applications-input"
                            />
                        </div>
                        <div>
                            <Label>Tavsiye oranı (%)</Label>
                            <Input
                                type="number" min="0" max="100"
                                value={summary.recommend_rate}
                                onChange={(e) => setSummary((s) => ({ ...s, recommend_rate: e.target.value }))}
                                data-testid="summary-recommend-input"
                            />
                        </div>
                    </div>

                    <div className="mt-5 grid gap-4 sm:grid-cols-3">
                        {(summary.highlights || []).map((h, i) => (
                            <div key={i} className="rounded-xl border border-border p-4">
                                <Label>Başlık</Label>
                                <Input
                                    value={h.label}
                                    onChange={(e) => setH(i, "label", e.target.value)}
                                    data-testid={`summary-highlight-label-${i}`}
                                />
                                <Label className="mt-3 block">Değer (%)</Label>
                                <Input
                                    type="number" min="0" max="100"
                                    value={h.value}
                                    onChange={(e) => setH(i, "value", e.target.value)}
                                    data-testid={`summary-highlight-value-${i}`}
                                />
                            </div>
                        ))}
                    </div>

                    <div className="mt-5 flex flex-wrap gap-3">
                        <Button onClick={saveSummary} disabled={saving} className="h-11" data-testid="save-review-summary-button">
                            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                            Puan özetini kaydet
                        </Button>
                        <Button
                            variant="secondary"
                            className="h-11 border border-border"
                            onClick={() =>
                                setSummary((s) => ({
                                    ...s,
                                    highlights: [...(s.highlights || []), { label: "Yeni başlık", value: 90 }],
                                }))
                            }
                            data-testid="add-highlight-button"
                        >
                            <Plus className="mr-2 h-4 w-4" /> Metrik ekle
                        </Button>
                    </div>
                </div>
            )}

            <div className="mt-8 flex items-center justify-between gap-4">
                <h2 className="font-heading text-lg font-bold">Yorumlar ({items.length})</h2>
                <Button onClick={openNew} className="h-11" data-testid="add-testimonial-button">
                    <Plus className="mr-2 h-4 w-4" /> Yorum ekle
                </Button>
            </div>

            {loading ? (
                <div className="mt-6 flex justify-center py-10">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <div className="mt-5 grid gap-5 md:grid-cols-2 lg:grid-cols-3" data-testid="admin-testimonials-list">
                    {items.map((t) => (
                        <div key={t.id} className="card-surface flex flex-col p-5" data-testid={`admin-testimonial-${t.id}`}>
                            <div className="flex items-center gap-1 text-[hsl(var(--brand-red))]">
                                {Array.from({ length: t.rating || 5 }).map((_, i) => (
                                    <Star key={i} className="h-3.5 w-3.5 fill-current" />
                                ))}
                                {!t.published && (
                                    <span className="ml-2 rounded-full bg-muted px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
                                        Gizli
                                    </span>
                                )}
                            </div>
                            <p className="mt-3 flex-1 text-sm leading-6">{t.text}</p>
                            <p className="mt-4 text-sm font-semibold">{t.name}</p>
                            <p className="text-xs text-muted-foreground">
                                {t.city} {t.visa ? `· ${t.visa}` : ""}
                            </p>
                            <div className="mt-4 flex gap-2">
                                <Button variant="secondary" className="h-9 flex-1 border border-border" onClick={() => openEdit(t)} data-testid={`edit-testimonial-${t.id}`}>
                                    <Pencil className="mr-2 h-3.5 w-3.5" /> Düzenle
                                </Button>
                                <Button variant="destructive" className="h-9" onClick={() => remove(t)} data-testid={`delete-testimonial-${t.id}`}>
                                    <Trash2 className="h-3.5 w-3.5" />
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
                    <DialogHeader>
                        <DialogTitle>{editing ? "Yorumu düzenle" : "Yeni yorum"}</DialogTitle>
                    </DialogHeader>
                    <div className="grid gap-4">
                        <div className="grid gap-4 sm:grid-cols-2">
                            <div>
                                <Label>İsim *</Label>
                                <Input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} placeholder="Elif K." data-testid="testimonial-name-input" />
                            </div>
                            <div>
                                <Label>Şehir</Label>
                                <Input value={form.city} onChange={(e) => setForm((f) => ({ ...f, city: e.target.value }))} placeholder="İstanbul" data-testid="testimonial-city-input" />
                            </div>
                            <div>
                                <Label>Vize / hizmet</Label>
                                <Input value={form.visa} onChange={(e) => setForm((f) => ({ ...f, visa: e.target.value }))} placeholder="30 Gün Tek Giriş" data-testid="testimonial-visa-input" />
                            </div>
                            <div>
                                <Label>Tarih</Label>
                                <DateField value={(form.date || "").slice(0, 10)} onChange={(iso) => setForm((f) => ({ ...f, date: iso }))} data-testid="testimonial-date-input" />
                            </div>
                            <div>
                                <Label>Puan (1-5)</Label>
                                <Input type="number" min="1" max="5" value={form.rating} onChange={(e) => setForm((f) => ({ ...f, rating: e.target.value }))} data-testid="testimonial-rating-input" />
                            </div>
                            <div>
                                <Label>Sıra</Label>
                                <Input type="number" value={form.order} onChange={(e) => setForm((f) => ({ ...f, order: e.target.value }))} data-testid="testimonial-order-input" />
                            </div>
                        </div>
                        <div>
                            <Label>Yorum metni *</Label>
                            <Textarea rows={4} value={form.text} onChange={(e) => setForm((f) => ({ ...f, text: e.target.value }))} data-testid="testimonial-text-input" />
                        </div>
                        <div className="flex flex-wrap gap-6">
                            <label className="flex items-center gap-2 text-sm font-medium">
                                <Switch checked={!!form.published} onCheckedChange={(v) => setForm((f) => ({ ...f, published: v }))} data-testid="testimonial-published-switch" />
                                Sitede yayınla
                            </label>
                            <label className="flex items-center gap-2 text-sm font-medium">
                                <Switch checked={!!form.verified} onCheckedChange={(v) => setForm((f) => ({ ...f, verified: v }))} data-testid="testimonial-verified-switch" />
                                Doğrulanmış rozeti
                            </label>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button variant="secondary" className="h-11 border border-border" onClick={() => setOpen(false)}>
                            Vazgeç
                        </Button>
                        <Button onClick={save} disabled={saving} className="h-11" data-testid="save-testimonial-button">
                            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                            Kaydet
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </AdminLayout>
    );
}
