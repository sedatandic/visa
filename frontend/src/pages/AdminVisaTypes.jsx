import React, { useEffect, useState } from "react";
import { Loader2, RefreshCw, Save } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatMoney, formatUsd } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";

const FxCard = ({ fx, onChange }) => {
    const [margin, setMargin] = useState("");
    const [manual, setManual] = useState("");
    const [busy, setBusy] = useState(false);

    useEffect(() => {
        if (!fx) return;
        setMargin(String(fx.margin_pct ?? ""));
        setManual(fx.manual_rate ? String(fx.manual_rate) : "");
    }, [fx]);

    const refresh = async () => {
        setBusy(true);
        try {
            const { data } = await api.get("/admin/fx", { params: { refresh: true } });
            onChange(data);
            toast.success(`Canlı kur güncellendi: 1 $ = ${data.base_rate} ₺`);
        } catch (err) {
            toast.error(apiError(err, "Kur güncellenemedi."));
        } finally {
            setBusy(false);
        }
    };

    const save = async () => {
        setBusy(true);
        try {
            const { data } = await api.put("/admin/fx", {
                margin_pct: margin === "" ? undefined : Number(margin),
                manual_rate: manual === "" ? null : Number(manual),
            });
            onChange(data);
            toast.success("Kur ayarları kaydedildi. Fiyatlar anında güncellendi.");
        } catch (err) {
            toast.error(apiError(err, "Kur ayarları kaydedilemedi."));
        } finally {
            setBusy(false);
        }
    };

    if (!fx) return null;

    return (
        <div className="card-surface mb-6 p-6" data-testid="admin-fx-card">
            <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                    <h2 className="font-heading text-lg font-bold">Döviz kuru (USD/TRY)</h2>
                    <p className="mt-1 max-w-xl text-sm leading-6 text-muted-foreground">
                        Tüm fiyatlar dolar bazlıdır ve müşteriye TL olarak gösterilir. Kur her 24 saatte
                        bir otomatik güncellenir; dilerseniz kur payı ekleyebilir veya sabit kur
                        girebilirsiniz.
                    </p>
                </div>
                <Button
                    variant="secondary"
                    className="h-10 border border-border"
                    onClick={refresh}
                    disabled={busy}
                    data-testid="fx-refresh-button"
                >
                    <RefreshCw className={`mr-2 h-4 w-4 ${busy ? "animate-spin" : ""}`} /> Canlı kuru çek
                </Button>
            </div>

            <dl className="mt-5 grid gap-4 sm:grid-cols-3">
                <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                    <dt className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Piyasa kuru
                    </dt>
                    <dd className="mt-1 font-heading text-xl font-extrabold" data-testid="fx-base-rate">
                        {fx.base_rate} ₺
                    </dd>
                    <dd className="mt-1 text-xs text-muted-foreground">Kaynak: {fx.source || "-"}</dd>
                </div>
                <div className="rounded-xl border border-primary/30 bg-primary/5 p-4">
                    <dt className="text-xs font-bold uppercase tracking-wider text-primary">
                        Kullanılan kur
                    </dt>
                    <dd className="mt-1 font-heading text-xl font-extrabold text-primary" data-testid="fx-effective-rate">
                        {fx.effective_rate} ₺
                    </dd>
                    <dd className="mt-1 text-xs text-muted-foreground">
                        {fx.mode === "manual" ? "Sabit kur (manuel)" : `Canlı kur + %${fx.margin_pct} pay`}
                    </dd>
                </div>
                <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                    <dt className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                        Son güncelleme
                    </dt>
                    <dd className="mt-1 text-sm font-semibold" data-testid="fx-fetched-at">
                        {fx.fetched_at ? new Date(fx.fetched_at).toLocaleString("tr-TR") : "-"}
                    </dd>
                    <dd className="mt-1 text-xs text-muted-foreground">
                        Örnek: 110 $ = {formatMoney(Math.round((110 * fx.effective_rate) / 10) * 10, "TRY")}
                    </dd>
                </div>
            </dl>

            <div className="mt-5 grid gap-4 sm:grid-cols-3">
                <div className="space-y-2">
                    <Label htmlFor="fx-margin">Kur payı (%)</Label>
                    <Input
                        id="fx-margin"
                        type="number"
                        step="0.1"
                        value={margin}
                        onChange={(e) => setMargin(e.target.value)}
                        data-testid="fx-margin-input"
                    />
                </div>
                <div className="space-y-2">
                    <Label htmlFor="fx-manual">Sabit kur (boş = canlı kur)</Label>
                    <Input
                        id="fx-manual"
                        type="number"
                        step="0.01"
                        placeholder="örn. 42.50"
                        value={manual}
                        onChange={(e) => setManual(e.target.value)}
                        data-testid="fx-manual-input"
                    />
                </div>
                <div className="flex items-end">
                    <Button onClick={save} disabled={busy} className="h-11 w-full" data-testid="fx-save-button">
                        <Save className="mr-2 h-4 w-4" /> Kur ayarlarını kaydet
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default function AdminVisaTypes() {
    const [items, setItems] = useState([]);
    const [fx, setFx] = useState(null);
    const [loading, setLoading] = useState(true);
    const [savingId, setSavingId] = useState(null);

    const load = () =>
        Promise.all([api.get("/admin/visa-types"), api.get("/admin/fx")])
            .then(([visas, fxRes]) => {
                setItems(visas.data);
                setFx(fxRes.data);
            })
            .catch((err) => toast.error(apiError(err, "Vize tipleri yüklenemedi.")))
            .finally(() => setLoading(false));

    useEffect(() => {
        load();
    }, []);

    const update = (id, patch) =>
        setItems((list) => list.map((v) => (v.id === id ? { ...v, ...patch } : v)));

    const onFxChange = (data) => {
        setFx(data);
        api.get("/admin/visa-types").then(({ data: visas }) => setItems(visas));
    };

    const save = async (visa) => {
        setSavingId(visa.id);
        try {
            const { data } = await api.patch(`/admin/visa-types/${visa.id}`, {
                price_usd: Number(visa.price_usd),
                processing_days: visa.processing_days,
                active: !!visa.active,
                popular: !!visa.popular,
            });
            update(visa.id, data);
            toast.success(`${data.name} güncellendi.`);
        } catch (err) {
            toast.error(apiError(err, "Güncelleme başarısız."));
        } finally {
            setSavingId(null);
        }
    };

    const previewTry = (usd) =>
        fx && usd ? Math.round((Number(usd) * fx.effective_rate) / 10) * 10 : null;

    return (
        <AdminLayout
            title="Vize tipleri ve fiyatlar"
            description="Fiyatlar dolar bazlı tutulur, müşteriye güncel kurla TL olarak gösterilir. İşlem süresi ve yayın durumunu da buradan yönetebilirsiniz."
        >
            <div data-testid="admin-visa-types-page">
                {loading ? (
                    <div className="flex justify-center py-16">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                ) : (
                    <>
                        <FxCard fx={fx} onChange={onFxChange} />

                        <div className="grid gap-5 lg:grid-cols-2">
                            {items.map((v) => (
                                <div key={v.id} className="card-surface p-6" data-testid={`admin-visa-type-${v.id}`}>
                                    <div className="flex items-start justify-between gap-4">
                                        <div>
                                            <h2 className="font-heading text-lg font-bold">{v.name}</h2>
                                            <p className="text-sm text-muted-foreground">
                                                {v.entry_label} · {v.duration_days} gün ·{" "}
                                                <span data-testid={`admin-visa-price-${v.id}`}>
                                                    {formatMoney(v.price, v.currency)}
                                                </span>{" "}
                                                <span className="text-xs">({formatUsd(v.price_usd)})</span>
                                            </p>
                                        </div>
                                    </div>

                                    <div className="mt-5 grid gap-4 sm:grid-cols-2">
                                        <div className="space-y-2">
                                            <Label htmlFor={`price-usd-${v.id}`}>Fiyat ($)</Label>
                                            <Input
                                                id={`price-usd-${v.id}`}
                                                type="number"
                                                value={v.price_usd ?? ""}
                                                onChange={(e) => update(v.id, { price_usd: e.target.value })}
                                                data-testid={`visa-price-usd-input-${v.id}`}
                                            />
                                            <p className="text-xs text-muted-foreground">
                                                Güncel kurla: {formatMoney(previewTry(v.price_usd), "TRY")}
                                            </p>
                                        </div>
                                        <div className="space-y-2">
                                            <Label htmlFor={`days-${v.id}`}>Sonuçlanma süresi</Label>
                                            <Input
                                                id={`days-${v.id}`}
                                                value={v.processing_days || ""}
                                                onChange={(e) => update(v.id, { processing_days: e.target.value })}
                                                data-testid={`visa-days-input-${v.id}`}
                                            />
                                        </div>
                                    </div>

                                    <div className="mt-5 flex flex-wrap items-center gap-6">
                                        <label className="flex cursor-pointer items-center gap-2.5 text-sm font-medium">
                                            <Switch
                                                checked={!!v.active}
                                                onCheckedChange={(c) => update(v.id, { active: c })}
                                                data-testid={`visa-active-switch-${v.id}`}
                                            />
                                            Sitede yayında
                                        </label>
                                        <label className="flex cursor-pointer items-center gap-2.5 text-sm font-medium">
                                            <Switch
                                                checked={!!v.popular}
                                                onCheckedChange={(c) => update(v.id, { popular: c })}
                                                data-testid={`visa-popular-switch-${v.id}`}
                                            />
                                            "En çok tercih edilen" etiketi
                                        </label>
                                    </div>

                                    <Button
                                        className="mt-6 h-11 w-full"
                                        onClick={() => save(v)}
                                        disabled={savingId === v.id}
                                        data-testid={`visa-save-button-${v.id}`}
                                    >
                                        {savingId === v.id ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Kaydediliyor…
                                            </>
                                        ) : (
                                            <>
                                                <Save className="mr-2 h-4 w-4" /> Kaydet
                                            </>
                                        )}
                                    </Button>
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </div>
        </AdminLayout>
    );
}
