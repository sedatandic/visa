import React, { useEffect, useMemo, useState } from "react";
import {
    Copy,
    Link2,
    Loader2,
    Plus,
    Trash2,
    XCircle,
} from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatDateTime, formatMoney } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { OfferReport } from "../components/OfferReport";
import { WhatsAppIcon } from "../components/WhatsAppIcon";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";
import { Textarea } from "../components/ui/textarea";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";

const STATUS_BADGE = {
    active: { label: "Aktif", className: "bg-emerald-50 text-emerald-700 border-emerald-200" },
    used: { label: "Başvuruya dönüştü", className: "bg-primary/10 text-primary border-primary/20" },
    expired: { label: "Süresi doldu", className: "bg-amber-50 text-amber-700 border-amber-200" },
    disabled: { label: "Kapatıldı", className: "bg-muted text-muted-foreground border-border" },
};

const FILTERS = [
    { key: "", label: "Tümü" },
    { key: "not_opened", label: "Açılmadı" },
    { key: "opened", label: "Açıldı" },
    { key: "used", label: "Dönüştü" },
    { key: "expired", label: "Süresi doldu" },
];

const copyText = (value, message) => {
    navigator.clipboard
        ?.writeText(value)
        .then(() => toast.success(message))
        .catch(() => toast.error("Kopyalanamadı. Bağlantıyı elle seçip kopyalayın."));
};

const OfferRow = ({ offer, onDisable }) => {
    const badge = STATUS_BADGE[offer.status] || STATUS_BADGE.active;
    return (
        <div className="rounded-2xl border border-border bg-card p-4 sm:p-5" data-testid={`offer-item-${offer.token}`}>
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                    <p className="font-heading text-base font-bold">{offer.title}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                        {offer.customer_name || "İsim girilmedi"}
                        {offer.customer_phone ? ` · ${offer.customer_phone}` : ""} ·{" "}
                        {formatDateTime(offer.created_at)}
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`rounded-full border px-2.5 py-1 text-[11px] font-bold ${badge.className}`}>
                        {badge.label}
                    </span>
                    <span className="font-heading text-base font-extrabold">
                        {formatMoney(offer.total, offer.currency)}
                    </span>
                </div>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-2">
                <Input readOnly value={offer.url} className="h-10 min-w-[220px] flex-1 text-xs" />
                <Button
                    variant="secondary"
                    className="h-10 border border-border"
                    onClick={() => copyText(offer.url, "Teklif bağlantısı kopyalandı.")}
                    data-testid={`offer-copy-${offer.token}`}
                >
                    <Copy className="mr-2 h-4 w-4" /> Kopyala
                </Button>
                <Button asChild className="h-10" data-testid={`offer-whatsapp-${offer.token}`}>
                    <a href={offer.whatsapp_url} target="_blank" rel="noreferrer">
                        <WhatsAppIcon className="mr-2 h-4 w-4" /> WhatsApp'tan gönder
                    </a>
                </Button>
                {offer.status !== "disabled" && (
                    <Button
                        variant="ghost"
                        className="h-10 text-muted-foreground"
                        onClick={() => onDisable(offer)}
                        data-testid={`offer-disable-${offer.token}`}
                    >
                        <XCircle className="mr-2 h-4 w-4" /> Kapat
                    </Button>
                )}
            </div>

            <p className="mt-2 text-xs text-muted-foreground" data-testid={`offer-activity-${offer.token}`}>
                {offer.travelers?.length || 0} yolcu ·{" "}
                {offer.opened
                    ? `${offer.views} görüntülenme · son açılış ${formatDateTime(offer.last_viewed_at)}`
                    : "Henüz açılmadı"}
                {offer.reference_code ? ` · Başvuru: ${offer.reference_code}` : ""}
                {offer.used_at ? ` (${formatDateTime(offer.used_at)})` : ""}
            </p>
        </div>
    );
};

export default function AdminOffers() {
    const [visaTypes, setVisaTypes] = useState([]);
    const [products, setProducts] = useState([]);
    const [items, setItems] = useState([]);
    const [report, setReport] = useState(null);
    const [filter, setFilter] = useState("");
    const [loading, setLoading] = useState(true);
    const [creating, setCreating] = useState(false);

    const [form, setForm] = useState({
        customer_name: "",
        customer_phone: "",
        title: "",
        note: "",
        valid_days: 14,
        arrival_date: "",
        departure_date: "",
    });
    const [rows, setRows] = useState([{ applicant_type: "adult", visa_type_id: "" }]);
    const [express, setExpress] = useState(false);
    const [insuranceId, setInsuranceId] = useState("");
    const [esimId, setEsimId] = useState("");
    const [esimQty, setEsimQty] = useState(1);
    const [tourId, setTourId] = useState("");
    const [tourDate, setTourDate] = useState("");
    const [tourTime, setTourTime] = useState("");
    const [quote, setQuote] = useState(null);
    const [quoteError, setQuoteError] = useState("");

    const setField = (key, value) => setForm((f) => ({ ...f, [key]: value }));

    const loadOffers = (status = "") =>
        api
            .get("/admin/offer-links", { params: status ? { status } : {} })
            .then(({ data }) => {
                setItems(data.items || []);
                setReport(data.report || null);
            })
            .catch((e) => toast.error(apiError(e, "Teklifler yüklenemedi.")));

    useEffect(() => {
        loadOffers(filter);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [filter]);

    useEffect(() => {
        Promise.all([api.get("/visa-types"), api.get("/products")])
            .then(([v, p]) => {
                setVisaTypes(v.data || []);
                setProducts(p.data.items || []);
                const first = (v.data || []).find((x) => x.popular && x.applicant_type !== "child");
                if (first) setRows([{ applicant_type: "adult", visa_type_id: first.id }]);
            })
            .catch((e) => toast.error(apiError(e, "Katalog yüklenemedi.")))
            .finally(() => setLoading(false));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const byKind = (kind) => products.filter((p) => p.kind === kind);
    const tourProduct = products.find((p) => p.id === tourId);

    const storeItems = useMemo(() => {
        const list = [];
        // Sihirbaz sigortayi her zaman kisi basi ekliyor: teklif tutari birebir aynı olsun
        if (insuranceId) list.push({ product_id: insuranceId, quantity: Math.max(1, rows.length) });
        if (esimId) list.push({ product_id: esimId, quantity: Math.max(1, Number(esimQty) || 1) });
        if (tourId) {
            list.push({
                product_id: tourId,
                quantity: Math.max(1, rows.length),
                scheduled_date: tourDate || null,
                scheduled_time: tourTime || null,
            });
        }
        return list;
    }, [insuranceId, esimId, esimQty, tourId, tourDate, tourTime, rows.length]);

    const ready = rows.length > 0 && rows.every((r) => r.visa_type_id);

    useEffect(() => {
        if (!ready) {
            setQuote(null);
            return;
        }
        const timer = setTimeout(() => {
            api.post("/pricing/quote", {
                visa_type_ids: rows.map((r) => r.visa_type_id),
                addons: { express },
                store_items: storeItems,
                arrival_date: form.arrival_date || null,
                departure_date: form.departure_date || null,
            })
                .then(({ data }) => {
                    setQuote(data);
                    setQuoteError("");
                })
                .catch((e) => {
                    setQuote(null);
                    setQuoteError(apiError(e, "Fiyat hesaplanamadı."));
                });
        }, 350);
        return () => clearTimeout(timer);
    }, [rows, express, storeItems, form.arrival_date, form.departure_date, ready]);

    const addRow = () => {
        if (rows.length >= 10) {
            toast.error("Bir teklife en fazla 10 yolcu ekleyebilirsiniz.");
            return;
        }
        setRows((list) => [...list, { ...list[list.length - 1] }]);
    };

    const updateRow = (index, patch) =>
        setRows((list) => list.map((r, i) => (i === index ? { ...r, ...patch } : r)));

    const create = async () => {
        if (!ready) {
            toast.error("Her yolcu için vize tipi seçin.");
            return;
        }
        setCreating(true);
        try {
            const { data } = await api.post("/admin/offer-links", {
                ...form,
                valid_days: Math.max(1, Math.min(90, Number(form.valid_days) || 14)),
                travelers: rows,
                addons: { express },
                store_items: storeItems,
            });
            setItems((list) => [data, ...list]);
            loadOffers(filter);
            copyText(data.url, "Teklif oluşturuldu ve bağlantı kopyalandı.");
        } catch (e) {
            toast.error(apiError(e, "Teklif oluşturulamadı."));
        } finally {
            setCreating(false);
        }
    };

    const disable = async (offer) => {
        try {
            await api.delete(`/admin/offer-links/${offer.id}`);
            setItems((list) => list.map((o) => (o.id === offer.id ? { ...o, status: "disabled" } : o)));
            toast.success("Teklif kapatıldı; bağlantı artık açılmıyor.");
        } catch (e) {
            toast.error(apiError(e, "Teklif kapatılamadı."));
        }
    };

    return (
        <AdminLayout
            title="Teklif Linkleri"
            description="Müşteriyle WhatsApp'ta konuşurken hazır bir teklif oluşturun. Müşteri linki açıp tutarı görür; 'Başvuruyu tamamla' dediğinde vize, sigorta ve eSIM seçimleri forma hazır gelir."
        >
            {loading ? (
                <div className="flex justify-center py-16">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <div className="max-w-6xl space-y-6" data-testid="admin-offers-page">
                    <OfferReport report={report} />
                    <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
                    <div className="card-surface p-5 sm:p-6">
                        <h2 className="font-heading text-lg font-bold">Yeni teklif</h2>

                        <div className="mt-4 grid gap-3 sm:grid-cols-2">
                            <div>
                                <Label className="text-xs">Müşteri adı</Label>
                                <Input
                                    value={form.customer_name}
                                    onChange={(e) => setField("customer_name", e.target.value)}
                                    placeholder="Ayşe Yılmaz"
                                    data-testid="offer-customer-name"
                                />
                            </div>
                            <div>
                                <Label className="text-xs">WhatsApp numarası</Label>
                                <Input
                                    value={form.customer_phone}
                                    onChange={(e) => setField("customer_phone", e.target.value)}
                                    placeholder="+90 5xx xxx xx xx"
                                    data-testid="offer-customer-phone"
                                />
                            </div>
                            <div className="sm:col-span-2">
                                <Label className="text-xs">Teklif başlığı (boş bırakırsanız otomatik yazılır)</Label>
                                <Input
                                    value={form.title}
                                    onChange={(e) => setField("title", e.target.value)}
                                    placeholder="Yılmaz ailesi · 30 gün tek giriş"
                                    data-testid="offer-title"
                                />
                            </div>
                            <div>
                                <Label className="text-xs">Gidiş tarihi (opsiyonel)</Label>
                                <Input
                                    type="date"
                                    value={form.arrival_date}
                                    onChange={(e) => setField("arrival_date", e.target.value)}
                                    data-testid="offer-arrival-date"
                                />
                            </div>
                            <div>
                                <Label className="text-xs">Dönüş tarihi (opsiyonel)</Label>
                                <Input
                                    type="date"
                                    value={form.departure_date}
                                    onChange={(e) => setField("departure_date", e.target.value)}
                                    data-testid="offer-departure-date"
                                />
                            </div>
                        </div>

                        <div className="mt-6">
                            <div className="flex items-center justify-between">
                                <h3 className="text-sm font-bold">Yolcular</h3>
                                <Button
                                    variant="secondary"
                                    className="h-9 border border-border"
                                    onClick={addRow}
                                    data-testid="offer-add-traveler"
                                >
                                    <Plus className="mr-1.5 h-4 w-4" /> Yolcu ekle
                                </Button>
                            </div>
                            <div className="mt-2 space-y-2">
                                {rows.map((row, index) => (
                                    <div key={index} className="flex items-center gap-2" data-testid={`offer-traveler-row-${index}`}>
                                        <Select
                                            value={row.applicant_type}
                                            onValueChange={(v) => updateRow(index, { applicant_type: v })}
                                        >
                                            <SelectTrigger className="w-[120px]" data-testid={`offer-traveler-type-${index}`}>
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="adult">Yetişkin</SelectItem>
                                                <SelectItem value="child">Çocuk</SelectItem>
                                            </SelectContent>
                                        </Select>
                                        <Select
                                            value={row.visa_type_id}
                                            onValueChange={(v) => updateRow(index, { visa_type_id: v })}
                                        >
                                            <SelectTrigger className="flex-1" data-testid={`offer-traveler-visa-${index}`}>
                                                <SelectValue placeholder="Vize tipi seçin" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {visaTypes.map((v) => (
                                                    <SelectItem key={v.id} value={v.id}>
                                                        {v.short_name || v.name} · {formatMoney(v.price, v.currency)}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                        {rows.length > 1 && (
                                            <Button
                                                variant="ghost"
                                                className="h-10 w-10 shrink-0 p-0 text-muted-foreground"
                                                onClick={() => setRows((list) => list.filter((_, i) => i !== index))}
                                                data-testid={`offer-remove-traveler-${index}`}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="mt-6 space-y-3">
                            <h3 className="text-sm font-bold">Ek hizmetler</h3>
                            <label className="flex items-center justify-between rounded-xl border border-border px-4 py-3">
                                <span className="text-sm font-semibold">Ekspres vize hizmeti (kişi başı)</span>
                                <Switch checked={express} onCheckedChange={setExpress} data-testid="offer-express" />
                            </label>

                            <div>
                                <Label className="text-xs">Seyahat sigortası (kişi başına eklenir)</Label>
                                <Select value={insuranceId || "none"} onValueChange={(v) => setInsuranceId(v === "none" ? "" : v)}>
                                    <SelectTrigger data-testid="offer-insurance-select">
                                        <SelectValue placeholder="Eklemeyin" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="none">Eklemeyin</SelectItem>
                                        {byKind("insurance").map((p) => (
                                            <SelectItem key={p.id} value={p.id}>
                                                {p.name} · {formatMoney(p.price, "TRY")}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="flex gap-2">
                                <div className="flex-1">
                                    <Label className="text-xs">Dubai eSIM</Label>
                                    <Select value={esimId || "none"} onValueChange={(v) => setEsimId(v === "none" ? "" : v)}>
                                        <SelectTrigger data-testid="offer-esim-select">
                                            <SelectValue placeholder="Eklemeyin" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="none">Eklemeyin</SelectItem>
                                            {byKind("esim").map((p) => (
                                                <SelectItem key={p.id} value={p.id}>
                                                    {p.name} · {formatMoney(p.price, "TRY")}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="w-20">
                                    <Label className="text-xs">Adet</Label>
                                    <Input
                                        type="number"
                                        min={1}
                                        max={10}
                                        value={esimQty}
                                        onChange={(e) => setEsimQty(e.target.value)}
                                        data-testid="offer-esim-qty"
                                    />
                                </div>
                            </div>

                            <div>
                                <Label className="text-xs">Dubai turu</Label>
                                <Select value={tourId || "none"} onValueChange={(v) => setTourId(v === "none" ? "" : v)}>
                                    <SelectTrigger data-testid="offer-tour-select">
                                        <SelectValue placeholder="Eklemeyin" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="none">Eklemeyin</SelectItem>
                                        {byKind("tour").map((p) => (
                                            <SelectItem key={p.id} value={p.id}>
                                                {p.name} · {formatMoney(p.price, "TRY")}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            {tourProduct?.needs_schedule && (
                                <div className="flex gap-2">
                                    <div className="flex-1">
                                        <Label className="text-xs">Tur tarihi (zorunlu)</Label>
                                        <Input
                                            type="date"
                                            value={tourDate}
                                            onChange={(e) => setTourDate(e.target.value)}
                                            data-testid="offer-tour-date"
                                        />
                                    </div>
                                    <div className="flex-1">
                                        <Label className="text-xs">Saat</Label>
                                        <Select value={tourTime || "none"} onValueChange={(v) => setTourTime(v === "none" ? "" : v)}>
                                            <SelectTrigger data-testid="offer-tour-time">
                                                <SelectValue placeholder="Saat seçin" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {(tourProduct.time_slots || []).map((slot) => (
                                                    <SelectItem key={slot} value={slot}>
                                                        {slot}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="mt-6 grid gap-3 sm:grid-cols-[1fr_120px]">
                            <div>
                                <Label className="text-xs">Müşteriye görünecek not (opsiyonel)</Label>
                                <Textarea
                                    rows={3}
                                    value={form.note}
                                    onChange={(e) => setField("note", e.target.value)}
                                    placeholder="Görüştüğümüz gibi 2 yetişkin + 1 çocuk için hazırladım. Ödeme sonrası 36 saatte sonuçlanır."
                                    data-testid="offer-note-input"
                                />
                            </div>
                            <div>
                                <Label className="text-xs">Geçerlilik (gün)</Label>
                                <Input
                                    type="number"
                                    min={1}
                                    max={90}
                                    value={form.valid_days}
                                    onChange={(e) => setField("valid_days", e.target.value)}
                                    data-testid="offer-valid-days"
                                />
                            </div>
                        </div>

                        <div className="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border bg-[hsl(var(--cloud))] p-4">
                            <div>
                                <p className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
                                    Teklif tutarı
                                </p>
                                <p className="font-heading text-2xl font-extrabold" data-testid="offer-quote-total">
                                    {quote ? formatMoney(quote.total, quote.currency) : "—"}
                                </p>
                                {quoteError && !quote && (
                                    <p className="mt-1 text-xs text-destructive" data-testid="offer-quote-error">
                                        {quoteError}
                                    </p>
                                )}
                            </div>
                            <Button
                                className="h-12"
                                onClick={create}
                                disabled={creating || !quote}
                                data-testid="offer-create-button"
                            >
                                {creating ? (
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                ) : (
                                    <Link2 className="mr-2 h-4 w-4" />
                                )}
                                Teklif linki oluştur
                            </Button>
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center justify-between">
                            <h2 className="font-heading text-lg font-bold">Gönderilen teklifler</h2>
                            <span className="text-xs text-muted-foreground" data-testid="offer-list-count">
                                {items.length} kayıt
                            </span>
                        </div>
                        <div className="mt-3 flex flex-wrap gap-2" data-testid="offer-filters">
                            {FILTERS.map((f) => (
                                <button
                                    key={f.key || "all"}
                                    type="button"
                                    onClick={() => setFilter(f.key)}
                                    data-testid={`offer-filter-${f.key || "all"}`}
                                    className={`rounded-full border px-3 py-1.5 text-xs font-bold transition-colors duration-150 ${
                                        filter === f.key
                                            ? "border-primary bg-primary/10 text-primary"
                                            : "border-border text-muted-foreground hover:bg-muted"
                                    }`}
                                >
                                    {f.label}
                                </button>
                            ))}
                        </div>
                        <div className="mt-3 space-y-3">
                            {items.length === 0 && (
                                <p className="card-surface p-5 text-sm text-muted-foreground" data-testid="offer-empty">
                                    {filter
                                        ? "Bu filtreye uyan teklif yok."
                                        : "Henüz teklif oluşturmadınız. Soldaki formu doldurup linki WhatsApp'tan gönderin."}
                                </p>
                            )}
                            {items.map((offer) => (
                                <OfferRow key={offer.id} offer={offer} onDisable={disable} />
                            ))}
                        </div>
                    </div>
                    </div>
                </div>
            )}
        </AdminLayout>
    );
}
