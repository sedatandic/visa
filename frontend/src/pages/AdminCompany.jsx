import React, { useEffect, useState } from "react";
import { Building2, Loader2, Save } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { AdminLayout } from "../components/AdminLayout";
import { TursabBadge } from "../components/TursabBadge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

const FIELDS = [
    { key: "legal_name", label: "Ticaret ünvanı *", placeholder: "Örn. VizeAtlas Turizm ve Danışmanlık A.Ş.", wide: true },
    { key: "tursab_no", label: "TÜRSAB belge numarası", placeholder: "Örn. 12345" },
    { key: "tursab_type", label: "Acente türü", placeholder: "Örn. A Grubu Seyahat Acentesi" },
    { key: "tax_office", label: "Vergi dairesi", placeholder: "Örn. Beşiktaş" },
    { key: "tax_no", label: "Vergi numarası", placeholder: "Örn. 1234567890" },
    { key: "mersis_no", label: "MERSİS numarası", placeholder: "16 haneli" },
    { key: "trade_registry_no", label: "Ticaret sicil numarası", placeholder: "Örn. 123456-5" },
    { key: "address", label: "Adres", placeholder: "Mahalle, ilçe / il", wide: true },
    { key: "phone", label: "Telefon", placeholder: "+90 ..." },
    { key: "whatsapp", label: "WhatsApp numarası", placeholder: "905xxxxxxxxx" },
    { key: "email", label: "E-posta", placeholder: "destek@..." },
    { key: "working_hours", label: "Çalışma saatleri", placeholder: "Hafta içi 09:00 - 19:00" },
    { key: "founded_year", label: "Kuruluş yılı", placeholder: "2019" },
];

export default function AdminCompany() {
    const [form, setForm] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        api.get("/admin/company")
            .then(({ data }) => setForm(data))
            .catch((e) => toast.error(apiError(e, "Acente bilgileri yüklenemedi.")))
            .finally(() => setLoading(false));
    }, []);

    const set = (key, value) => setForm((f) => ({ ...f, [key]: value }));

    const save = async () => {
        if (!form.legal_name?.trim()) {
            toast.error("Ticaret ünvanı zorunludur.");
            return;
        }
        setSaving(true);
        try {
            const { data } = await api.put("/admin/company", form);
            setForm(data);
            toast.success("Acente bilgileri güncellendi.");
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    return (
        <AdminLayout
            title="Acente Bilgileri"
            description="TÜRSAB belge numarası ve ticari bilgileriniz sitenin alt bilgisinde ve Hakkımızda sayfasında görünür."
        >
            {loading || !form ? (
                <div className="flex justify-center py-16">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <div className="card-surface max-w-4xl p-6" data-testid="admin-company-form">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                        <div className="flex items-center gap-3">
                            <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                                <Building2 className="h-5 w-5 text-primary" />
                            </span>
                            <div>
                                <h2 className="font-heading text-lg font-bold">Şirket ve TÜRSAB bilgileri</h2>
                                <p className="text-xs text-muted-foreground">
                                    Boş bıraktığınız alanlar sitede gösterilmez.
                                </p>
                            </div>
                        </div>
                        <TursabBadge number={form.tursab_no || "—"} type={form.tursab_type || ""} />
                    </div>

                    <div className="mt-6 grid gap-4 sm:grid-cols-2">
                        {FIELDS.map((f) => (
                            <div key={f.key} className={f.wide ? "sm:col-span-2" : ""}>
                                <Label htmlFor={`company-${f.key}`}>{f.label}</Label>
                                <Input
                                    id={`company-${f.key}`}
                                    value={form[f.key] || ""}
                                    placeholder={f.placeholder}
                                    onChange={(e) => set(f.key, e.target.value)}
                                    data-testid={`company-${f.key}-input`}
                                />
                            </div>
                        ))}
                    </div>

                    <Button onClick={save} disabled={saving} className="mt-6 h-11" data-testid="save-company-button">
                        {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                        Kaydet
                    </Button>
                </div>
            )}
        </AdminLayout>
    );
}
