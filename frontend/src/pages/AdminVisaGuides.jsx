import React, { useCallback, useEffect, useState } from "react";
import { ExternalLink, Loader2, Plus, RotateCcw, Save, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";

const LIST_FIELDS = [
    { key: "intro", label: "Giriş paragrafları", hint: "Her satır bir paragraf olur." },
    { key: "who_for", label: "Bu vize kimler için uygun?", hint: "Her satır bir madde." },
    { key: "highlights", label: "Öne çıkan avantajlar", hint: "Her satır bir madde." },
    { key: "tips", label: "Danışman notları", hint: "Her satır bir madde." },
];

const toText = (list) => (Array.isArray(list) ? list.join("\n") : "");
const toList = (text) =>
    (text || "")
        .split("\n")
        .map((l) => l.trim())
        .filter(Boolean);

const emptyForm = {
    h1: "",
    seo_title: "",
    seo_description: "",
    intro: "",
    who_for: "",
    highlights: "",
    tips: "",
    faqs: [],
};

export default function AdminVisaGuides() {
    const [items, setItems] = useState([]);
    const [slug, setSlug] = useState("");
    const [form, setForm] = useState(emptyForm);
    const [hasOverride, setHasOverride] = useState(false);
    const [loading, setLoading] = useState(true);
    const [loadingGuide, setLoadingGuide] = useState(false);
    const [saving, setSaving] = useState(false);
    const [resetting, setResetting] = useState(false);

    useEffect(() => {
        api.get("/admin/visa-guides")
            .then(({ data }) => {
                setItems(data.items || []);
                if ((data.items || []).length) setSlug(data.items[0].slug);
            })
            .catch((err) => toast.error(apiError(err, "Rehber listesi yüklenemedi.")))
            .finally(() => setLoading(false));
    }, []);

    const fillForm = (guide, override) => {
        setForm({
            h1: guide.h1 || "",
            seo_title: guide.seo_title || "",
            seo_description: guide.seo_description || "",
            intro: toText(guide.intro),
            who_for: toText(guide.who_for),
            highlights: toText(guide.highlights),
            tips: toText(guide.tips),
            // ortak SSS'ler backend tarafinda eklenir; burada sadece sayfaya ozel olanlar duzenlenir
            faqs: (override?.faqs || guide.faqs || []).slice(0, 12).map((f) => ({ q: f.q, a: f.a })),
        });
    };

    const loadGuide = useCallback(async (targetSlug) => {
        if (!targetSlug) return;
        setLoadingGuide(true);
        try {
            const { data } = await api.get(`/admin/visa-guides/${targetSlug}`);
            const base = data.effective || {};
            const override = data.override || {};
            const merged = { ...base, ...override };
            // sayfaya ozel SSS'ler: varsayilan icerikteki sayfa SSS sayisi kadar
            const pageFaqCount = (data.defaults?.faqs || []).length - 4; // 4 ortak SSS
            const faqs = override.faqs || (data.defaults?.faqs || []).slice(0, Math.max(pageFaqCount, 0));
            fillForm({ ...merged, faqs }, { faqs });
            setHasOverride(!!data.has_override);
        } catch (err) {
            toast.error(apiError(err, "Rehber yüklenemedi."));
        } finally {
            setLoadingGuide(false);
        }
    }, []);

    useEffect(() => {
        loadGuide(slug);
    }, [slug, loadGuide]);

    const setField = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

    const setFaq = (index, key, value) =>
        setForm((f) => ({
            ...f,
            faqs: f.faqs.map((item, i) => (i === index ? { ...item, [key]: value } : item)),
        }));

    const addFaq = () => setForm((f) => ({ ...f, faqs: [...f.faqs, { q: "", a: "" }] }));
    const removeFaq = (index) =>
        setForm((f) => ({ ...f, faqs: f.faqs.filter((_, i) => i !== index) }));

    const save = async () => {
        setSaving(true);
        try {
            const payload = {
                h1: form.h1,
                seo_title: form.seo_title,
                seo_description: form.seo_description,
                intro: toList(form.intro),
                who_for: toList(form.who_for),
                highlights: toList(form.highlights),
                tips: toList(form.tips),
                faqs: form.faqs.filter((f) => f.q.trim() && f.a.trim()),
            };
            const { data } = await api.put(`/admin/visa-guides/${slug}`, payload);
            setHasOverride(!!data.has_override);
            setItems((list) => list.map((i) => (i.slug === slug ? { ...i, has_override: true } : i)));
            toast.success("Rehber içeriği kaydedildi. Site anında güncellendi.");
        } catch (err) {
            toast.error(apiError(err, "Rehber kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const resetGuide = async () => {
        setResetting(true);
        try {
            await api.delete(`/admin/visa-guides/${slug}`);
            setItems((list) => list.map((i) => (i.slug === slug ? { ...i, has_override: false } : i)));
            await loadGuide(slug);
            toast.success("Rehber varsayılan içeriğe döndürüldü.");
        } catch (err) {
            toast.error(apiError(err, "Sıfırlama başarısız."));
        } finally {
            setResetting(false);
        }
    };

    const current = items.find((i) => i.slug === slug);

    return (
        <AdminLayout
            title="Vize rehberleri"
            description="Her vize tipinin rehber sayfasındaki metinleri, SEO başlıklarını ve sıkça sorulan soruları buradan düzenleyin. Değişiklikler siteye anında yansır."
        >
            <div data-testid="admin-visa-guides-page">
                {loading ? (
                    <div className="flex justify-center py-16">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                ) : (
                    <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
                        {/* GUIDE LIST */}
                        <aside className="card-surface h-fit p-5">
                            <Label className="text-xs uppercase tracking-wider text-muted-foreground">
                                Rehber seçin
                            </Label>
                            <div className="mt-3 lg:hidden">
                                <Select value={slug} onValueChange={setSlug}>
                                    <SelectTrigger data-testid="guide-select-mobile">
                                        <SelectValue placeholder="Rehber" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {items.map((i) => (
                                            <SelectItem key={i.slug} value={i.slug}>
                                                {i.title}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <ul className="mt-3 hidden space-y-1.5 lg:block">
                                {items.map((i) => (
                                    <li key={i.slug}>
                                        <button
                                            type="button"
                                            onClick={() => setSlug(i.slug)}
                                            className={`w-full rounded-lg border px-3 py-2.5 text-left text-sm font-semibold transition-colors duration-150 ${
                                                slug === i.slug
                                                    ? "border-primary bg-primary/10 text-primary"
                                                    : "border-border bg-card hover:border-primary/40"
                                            }`}
                                            data-testid={`guide-tab-${i.slug}`}
                                        >
                                            {i.title}
                                            {i.has_override && (
                                                <span className="mt-1 block text-[11px] font-medium text-muted-foreground">
                                                    Özel içerik kayıtlı
                                                </span>
                                            )}
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </aside>

                        {/* EDITOR */}
                        <div className="card-surface p-6">
                            {loadingGuide ? (
                                <div className="flex justify-center py-16">
                                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                                </div>
                            ) : (
                                <>
                                    <div className="flex flex-wrap items-start justify-between gap-3">
                                        <div>
                                            <h2 className="font-heading text-lg font-bold">{current?.title || "Rehber"}</h2>
                                            <p className="text-sm text-muted-foreground">
                                                {hasOverride ? "Özel içerik kullanılıyor" : "Varsayılan içerik kullanılıyor"}
                                            </p>
                                        </div>
                                        {current?.path && (
                                            <Button asChild variant="secondary" className="h-10 border border-border">
                                                <a
                                                    href={current.path}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                    data-testid="guide-preview-link"
                                                >
                                                    <ExternalLink className="mr-2 h-4 w-4" /> Sayfayı gör
                                                </a>
                                            </Button>
                                        )}
                                    </div>

                                    <div className="mt-6 space-y-5">
                                        <div className="space-y-2">
                                            <Label htmlFor="guide-h1">Sayfa başlığı (H1)</Label>
                                            <Input
                                                id="guide-h1"
                                                value={form.h1}
                                                onChange={setField("h1")}
                                                data-testid="guide-h1-input"
                                            />
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="guide-seo-title">SEO başlığı (title)</Label>
                                            <Input
                                                id="guide-seo-title"
                                                value={form.seo_title}
                                                onChange={setField("seo_title")}
                                                data-testid="guide-seo-title-input"
                                            />
                                            <p className="text-xs text-muted-foreground">
                                                Önerilen uzunluk: 55-65 karakter ({form.seo_title.length})
                                            </p>
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor="guide-seo-desc">SEO açıklaması (description)</Label>
                                            <Textarea
                                                id="guide-seo-desc"
                                                rows={3}
                                                value={form.seo_description}
                                                onChange={setField("seo_description")}
                                                data-testid="guide-seo-description-input"
                                            />
                                            <p className="text-xs text-muted-foreground">
                                                Önerilen uzunluk: 140-160 karakter ({form.seo_description.length})
                                            </p>
                                        </div>

                                        {LIST_FIELDS.map(({ key, label, hint }) => (
                                            <div key={key} className="space-y-2">
                                                <Label htmlFor={`guide-${key}`}>{label}</Label>
                                                <Textarea
                                                    id={`guide-${key}`}
                                                    rows={key === "intro" ? 7 : 5}
                                                    value={form[key]}
                                                    onChange={setField(key)}
                                                    data-testid={`guide-${key}-input`}
                                                />
                                                <p className="text-xs text-muted-foreground">{hint}</p>
                                            </div>
                                        ))}

                                        <div className="rounded-xl border border-border p-5">
                                            <div className="flex flex-wrap items-center justify-between gap-3">
                                                <div>
                                                    <h3 className="font-heading text-base font-bold">
                                                        Sıkça sorulan sorular
                                                    </h3>
                                                    <p className="mt-1 text-xs leading-5 text-muted-foreground">
                                                        Bu sayfaya özel sorular. Tüm rehberlerde görünen 4 ortak soru
                                                        otomatik olarak eklenir.
                                                    </p>
                                                </div>
                                                <Button
                                                    type="button"
                                                    variant="secondary"
                                                    className="h-10 border border-border"
                                                    onClick={addFaq}
                                                    data-testid="guide-add-faq-button"
                                                >
                                                    <Plus className="mr-2 h-4 w-4" /> Soru ekle
                                                </Button>
                                            </div>

                                            <div className="mt-5 space-y-5">
                                                {form.faqs.length === 0 && (
                                                    <p className="text-sm text-muted-foreground">
                                                        Henüz sayfaya özel soru yok.
                                                    </p>
                                                )}
                                                {form.faqs.map((f, i) => (
                                                    <div
                                                        key={i}
                                                        className="rounded-lg border border-border bg-[hsl(var(--cloud))] p-4"
                                                        data-testid={`guide-faq-row-${i}`}
                                                    >
                                                        <div className="flex items-start gap-3">
                                                            <div className="flex-1 space-y-3">
                                                                <Input
                                                                    value={f.q}
                                                                    onChange={(e) => setFaq(i, "q", e.target.value)}
                                                                    placeholder="Soru"
                                                                    data-testid={`guide-faq-q-${i}`}
                                                                />
                                                                <Textarea
                                                                    rows={3}
                                                                    value={f.a}
                                                                    onChange={(e) => setFaq(i, "a", e.target.value)}
                                                                    placeholder="Cevap"
                                                                    data-testid={`guide-faq-a-${i}`}
                                                                />
                                                            </div>
                                                            <Button
                                                                type="button"
                                                                variant="secondary"
                                                                className="h-10 shrink-0 border border-border text-destructive"
                                                                onClick={() => removeFaq(i)}
                                                                data-testid={`guide-faq-remove-${i}`}
                                                                aria-label="Soruyu sil"
                                                            >
                                                                <Trash2 className="h-4 w-4" />
                                                            </Button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>

                                    <div className="mt-7 flex flex-wrap gap-3">
                                        <Button
                                            onClick={save}
                                            disabled={saving}
                                            className="h-11"
                                            data-testid="guide-save-button"
                                        >
                                            {saving ? (
                                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Kaydediliyor…</>
                                            ) : (
                                                <><Save className="mr-2 h-4 w-4" /> Kaydet</>
                                            )}
                                        </Button>
                                        <Button
                                            variant="secondary"
                                            className="h-11 border border-border"
                                            onClick={resetGuide}
                                            disabled={resetting || !hasOverride}
                                            data-testid="guide-reset-button"
                                        >
                                            {resetting ? (
                                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sıfırlanıyor…</>
                                            ) : (
                                                <><RotateCcw className="mr-2 h-4 w-4" /> Varsayılana dön</>
                                            )}
                                        </Button>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </AdminLayout>
    );
}
