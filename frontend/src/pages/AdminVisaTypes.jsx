import React, { useEffect, useState } from "react";
import { Loader2, Save } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatMoney } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Switch } from "../components/ui/switch";

export default function AdminVisaTypes() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [savingId, setSavingId] = useState(null);

    useEffect(() => {
        api.get("/admin/visa-types")
            .then(({ data }) => setItems(data))
            .catch((err) => toast.error(apiError(err, "Vize tipleri yüklenemedi.")))
            .finally(() => setLoading(false));
    }, []);

    const update = (id, patch) =>
        setItems((list) => list.map((v) => (v.id === id ? { ...v, ...patch } : v)));

    const save = async (visa) => {
        setSavingId(visa.id);
        try {
            const { data } = await api.patch(`/admin/visa-types/${visa.id}`, {
                price: Number(visa.price),
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

    return (
        <AdminLayout
            title="Vize tipleri ve fiyatlar"
            description="Fiyatları, işlem sürelerini ve yayın durumunu buradan güncelleyebilirsiniz. Değişiklikler siteye anında yansır."
        >
            <div data-testid="admin-visa-types-page">
                {loading ? (
                    <div className="flex justify-center py-16">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                ) : (
                    <div className="grid gap-5 lg:grid-cols-2">
                        {items.map((v) => (
                            <div key={v.id} className="card-surface p-6" data-testid={`admin-visa-type-${v.id}`}>
                                <div className="flex items-start justify-between gap-4">
                                    <div>
                                        <h2 className="font-heading text-lg font-bold">{v.name}</h2>
                                        <p className="text-sm text-muted-foreground">
                                            {v.entry_label} · {v.duration_days} gün · {formatMoney(v.price, v.currency)}
                                        </p>
                                    </div>
                                </div>

                                <div className="mt-5 grid gap-4 sm:grid-cols-2">
                                    <div className="space-y-2">
                                        <Label htmlFor={`price-${v.id}`}>Fiyat (₺)</Label>
                                        <Input
                                            id={`price-${v.id}`}
                                            type="number"
                                            value={v.price}
                                            onChange={(e) => update(v.id, { price: e.target.value })}
                                            data-testid={`visa-price-input-${v.id}`}
                                        />
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
                )}
            </div>
        </AdminLayout>
    );
}
