import React, { useEffect, useState } from "react";
import { Landmark, Loader2, Plus, Save, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Switch } from "../components/ui/switch";

export default function AdminBankTransfer() {
    const [form, setForm] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        api.get("/admin/bank-transfer")
            .then(({ data }) =>
                setForm({ ...data, steps: data.steps || [], notes: data.notes || [], banks: data.banks || [] })
            )
            .catch((e) => toast.error(apiError(e, "Banka bilgileri yüklenemedi.")))
            .finally(() => setLoading(false));
    }, []);

    const set = (key, value) => setForm((f) => ({ ...f, [key]: value }));

    const save = async () => {
        if (!form.account_name?.trim() || !form.bank_name?.trim() || (form.iban || "").replace(/\s/g, "").length < 16) {
            toast.error("Hesap ünvanı, banka adı ve geçerli bir IBAN girin.");
            return;
        }
        const banks = (form.banks || [])
            .filter((b) => (b.name || "").trim())
            .map((b, i) => ({
                id: b.id || `bank-${i + 1}`,
                name: b.name.trim(),
                logo: (b.logo || "").trim(),
                accounts: (b.accounts || []).filter((a) => (a.iban || "").replace(/\s/g, "").length >= 16),
            }));
        setSaving(true);
        try {
            await api.put("/admin/bank-transfer", {
                enabled: !!form.enabled,
                title: form.title || "Havale / EFT ile ödeme",
                account_name: form.account_name,
                bank_name: form.bank_name,
                iban: form.iban,
                currency: form.currency || "TRY",
                note: form.note || "",
                notes: (form.notes || []).filter((n) => n.trim()),
                banks,
                steps: (form.steps || []).filter((s) => s.trim()),
            });
            toast.success("Banka bilgileri güncellendi. Havale ödemeleri bu bilgilerle gösterilecek.");
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const setBank = (index, key, value) =>
        set("banks", (form.banks || []).map((b, i) => (i === index ? { ...b, [key]: value } : b)));

    const setAccount = (bankIndex, accIndex, key, value) =>
        set(
            "banks",
            (form.banks || []).map((b, i) =>
                i === bankIndex
                    ? {
                          ...b,
                          accounts: (b.accounts || []).map((a, j) => (j === accIndex ? { ...a, [key]: value } : a)),
                      }
                    : b
            )
        );

    return (
        <AdminLayout
            title="Banka Bilgileri"
            description="Havale/EFT ile ödeme yapan müşterilere gösterilecek hesap bilgilerini buradan güncelleyin."
        >
            {loading || !form ? (
                <div className="flex justify-center py-16">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <div className="card-surface max-w-3xl p-6" data-testid="admin-bank-transfer-form">
                    <div className="flex items-center gap-3">
                        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                            <Landmark className="h-5 w-5 text-primary" />
                        </span>
                        <div>
                            <h2 className="font-heading text-lg font-bold">Havale / EFT hesabı</h2>
                            <p className="text-xs text-muted-foreground">
                                Bu bilgiler başvuru ödeme adımında ve müşteriye giden e-postada görünür.
                            </p>
                        </div>
                    </div>

                    <div className="mt-6 grid gap-4 sm:grid-cols-2">
                        <div className="sm:col-span-2">
                            <Label>Hesap ünvanı *</Label>
                            <Input
                                value={form.account_name || ""}
                                onChange={(e) => set("account_name", e.target.value)}
                                placeholder="Örn. Dubai Vize Online Turizm ve Danışmanlık A.Ş."
                                data-testid="bank-account-name-input"
                            />
                        </div>
                        <div>
                            <Label>Banka adı *</Label>
                            <Input
                                value={form.bank_name || ""}
                                onChange={(e) => set("bank_name", e.target.value)}
                                placeholder="Örn. Ziraat Bankası"
                                data-testid="bank-name-input"
                            />
                        </div>
                        <div>
                            <Label>Para birimi</Label>
                            <Input
                                value={form.currency || "TRY"}
                                onChange={(e) => set("currency", e.target.value.toUpperCase())}
                                data-testid="bank-currency-input"
                            />
                        </div>
                        <div className="sm:col-span-2">
                            <Label>IBAN *</Label>
                            <Input
                                value={form.iban || ""}
                                onChange={(e) => set("iban", e.target.value)}
                                placeholder="TR00 0000 0000 0000 0000 0000 00"
                                className="font-mono-code"
                                data-testid="bank-iban-input"
                            />
                        </div>
                        <div className="sm:col-span-2">
                            <Label>Müşteriye not</Label>
                            <Textarea
                                rows={3}
                                value={form.note || ""}
                                onChange={(e) => set("note", e.target.value)}
                                data-testid="bank-note-input"
                            />
                        </div>
                    </div>

                    <div className="mt-6">
                        <Label>Ödeme adımları</Label>
                        <div className="mt-2 space-y-2">
                            {(form.steps || []).map((s, i) => (
                                <div key={i} className="flex gap-2">
                                    <Input
                                        value={s}
                                        onChange={(e) =>
                                            set(
                                                "steps",
                                                form.steps.map((v, j) => (j === i ? e.target.value : v))
                                            )
                                        }
                                        data-testid={`bank-step-input-${i}`}
                                    />
                                    <Button
                                        variant="destructive"
                                        className="h-10 shrink-0"
                                        onClick={() => set("steps", form.steps.filter((_, j) => j !== i))}
                                        data-testid={`bank-step-delete-${i}`}
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                        <Button
                            variant="secondary"
                            className="mt-3 h-10 border border-border"
                            onClick={() => set("steps", [...(form.steps || []), ""])}
                            data-testid="bank-add-step-button"
                        >
                            <Plus className="mr-2 h-4 w-4" /> Adım ekle
                        </Button>
                    </div>

                    <div className="mt-8 border-t border-border pt-6">
                        <div className="flex items-center justify-between gap-3">
                            <div>
                                <h3 className="font-heading text-base font-bold">Yayınlanan banka hesapları</h3>
                                <p className="text-xs text-muted-foreground">
                                    Hizmet bedelleri sayfasında ve ödeme adımında logolu kartlar hâlinde gösterilir.
                                </p>
                            </div>
                            <Button
                                variant="secondary"
                                className="h-10 shrink-0 border border-border"
                                onClick={() =>
                                    set("banks", [
                                        ...(form.banks || []),
                                        { id: "", name: "", logo: "", accounts: [{ currency: "TRY", iban: "" }] },
                                    ])
                                }
                                data-testid="bank-add-bank-button"
                            >
                                <Plus className="mr-2 h-4 w-4" /> Banka ekle
                            </Button>
                        </div>

                        <div className="mt-4 space-y-4">
                            {(form.banks || []).map((b, i) => (
                                <div key={i} className="rounded-xl border border-border p-4" data-testid={`admin-bank-block-${i}`}>
                                    <div className="grid gap-3 sm:grid-cols-[1.2fr_1fr_auto]">
                                        <div>
                                            <Label>Banka adı</Label>
                                            <Input
                                                value={b.name || ""}
                                                onChange={(e) => setBank(i, "name", e.target.value)}
                                                placeholder="Örn. Türkiye İş Bankası A.Ş."
                                                data-testid={`admin-bank-name-input-${i}`}
                                            />
                                        </div>
                                        <div>
                                            <Label>Logo yolu</Label>
                                            <Input
                                                value={b.logo || ""}
                                                onChange={(e) => setBank(i, "logo", e.target.value)}
                                                placeholder="/brand/banks/isbank.png"
                                                data-testid={`admin-bank-logo-input-${i}`}
                                            />
                                        </div>
                                        <div className="flex items-end">
                                            <Button
                                                variant="destructive"
                                                className="h-10"
                                                onClick={() => set("banks", form.banks.filter((_, j) => j !== i))}
                                                data-testid={`admin-bank-delete-${i}`}
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>

                                    <div className="mt-3 space-y-2">
                                        {(b.accounts || []).map((acc, j) => (
                                            <div key={j} className="flex gap-2">
                                                <Input
                                                    value={acc.currency || ""}
                                                    onChange={(e) => setAccount(i, j, "currency", e.target.value.toUpperCase())}
                                                    placeholder="TRY"
                                                    className="w-24 shrink-0"
                                                    data-testid={`admin-bank-currency-input-${i}-${j}`}
                                                />
                                                <Input
                                                    value={acc.iban || ""}
                                                    onChange={(e) => setAccount(i, j, "iban", e.target.value)}
                                                    placeholder="TR00 0000 0000 0000 0000 0000 00"
                                                    className="font-mono-code"
                                                    data-testid={`admin-bank-iban-input-${i}-${j}`}
                                                />
                                                <Button
                                                    variant="destructive"
                                                    className="h-10 shrink-0"
                                                    onClick={() =>
                                                        setBank(i, "accounts", b.accounts.filter((_, k) => k !== j))
                                                    }
                                                    data-testid={`admin-bank-account-delete-${i}-${j}`}
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        ))}
                                        <Button
                                            variant="secondary"
                                            className="h-9 border border-border"
                                            onClick={() =>
                                                setBank(i, "accounts", [...(b.accounts || []), { currency: "USD", iban: "" }])
                                            }
                                            data-testid={`admin-bank-add-account-${i}`}
                                        >
                                            <Plus className="mr-2 h-3.5 w-3.5" /> Hesap ekle
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-5">
                            <Label>Hesap kartlarında görünen uyarı satırları</Label>
                            <div className="mt-2 space-y-2">
                                {(form.notes || []).map((n, i) => (
                                    <div key={i} className="flex gap-2">
                                        <Input
                                            value={n}
                                            onChange={(e) =>
                                                set("notes", form.notes.map((v, j) => (j === i ? e.target.value : v)))
                                            }
                                            data-testid={`bank-note-line-input-${i}`}
                                        />
                                        <Button
                                            variant="destructive"
                                            className="h-10 shrink-0"
                                            onClick={() => set("notes", form.notes.filter((_, j) => j !== i))}
                                            data-testid={`bank-note-line-delete-${i}`}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                ))}
                            </div>
                            <Button
                                variant="secondary"
                                className="mt-3 h-10 border border-border"
                                onClick={() => set("notes", [...(form.notes || []), ""])}
                                data-testid="bank-add-note-line-button"
                            >
                                <Plus className="mr-2 h-4 w-4" /> Uyarı satırı ekle
                            </Button>
                        </div>
                    </div>

                    <label className="mt-6 flex items-center gap-2 text-sm font-medium">
                        <Switch
                            checked={!!form.enabled}
                            onCheckedChange={(v) => set("enabled", v)}
                            data-testid="bank-enabled-switch"
                        />
                        Havale/EFT ödeme seçeneği aktif
                    </label>

                    <Button onClick={save} disabled={saving} className="mt-6 h-11" data-testid="save-bank-transfer-button">
                        {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                        Kaydet
                    </Button>
                </div>
            )}
        </AdminLayout>
    );
}
