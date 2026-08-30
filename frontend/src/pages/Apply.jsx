import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
    AlertCircle,
    AlertTriangle,
    ArrowLeft,
    ArrowRight,
    Baby,
    CalendarDays,
    CheckCircle2,
    CreditCard,
    FileText,
    Loader2,
    Landmark,
    Lock,
    Plus,
    ShieldCheck,
    Sparkles,
    Trash2,
    User,
    Users,
} from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { COMPANY, PURPOSES, PURPOSE_LABELS, formatDate, formatMoney, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { FileDropzone } from "../components/FileDropzone";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Progress } from "../components/ui/progress";
import { Checkbox } from "../components/ui/checkbox";
import { Switch } from "../components/ui/switch";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";

const STEPS = [
    { key: "people", label: "Kişisel Bilgiler", icon: Users },
    { key: "visa", label: "Vize Detayları", icon: CalendarDays },
    { key: "docs", label: "Evraklar", icon: FileText },
    { key: "summary", label: "Özet & Ödeme", icon: CreditCard },
];

let travelerSeq = 0;
const newTraveler = (type = "adult") => ({
    key: `t${++travelerSeq}`,
    applicant_type: type,
    first_name: "",
    last_name: "",
    birth_date: "",
    gender: "",
    nationality: "TR",
    national_id: "",
    passport_no: "",
    passport_expiry: "",
    visa_type_id: "",
    passportFile: null,
    photoFile: null,
});

const Field = ({ label, children, error, required, htmlFor }) => (
    <div className="space-y-2">
        <Label htmlFor={htmlFor}>
            {label} {required && <span className="text-destructive">*</span>}
        </Label>
        {children}
        {error && (
            <p className="flex items-start gap-1.5 text-xs font-medium text-destructive">
                <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                {error}
            </p>
        )}
    </div>
);

const SummaryRow = ({ label, value, strong }) => (
    <div className="flex items-start justify-between gap-4 border-b border-border py-2.5 last:border-0">
        <span className={`text-sm ${strong ? "font-semibold" : "text-muted-foreground"}`}>{label}</span>
        <span className={`text-right text-sm ${strong ? "font-bold" : "font-semibold"}`}>{value || "-"}</span>
    </div>
);

export default function Apply() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const [visaTypes, setVisaTypes] = useState([]);
    const [addonMeta, setAddonMeta] = useState([]);
    const [maxTravelers, setMaxTravelers] = useState(10);
    const [step, setStep] = useState(0);
    const [contact, setContact] = useState({ full_name: "", email: "", phone: "", address_city: "" });
    const [travelers, setTravelers] = useState([newTraveler()]);
    const [travel, setTravel] = useState({
        arrival_date: "",
        departure_date: "",
        purpose: "tourism",
        birth_country: "TR",
        accommodation: "",
        flight_no: "",
        notes: "",
    });
    const [addons, setAddons] = useState({ express: false, insurance: false });
    const [extraDocs, setExtraDocs] = useState({ ticket: null, hotel: null, other: null });
    const [kvkk, setKvkk] = useState(false);
    const [errors, setErrors] = useState({});
    const [ocr, setOcr] = useState({});
    const [payMethod, setPayMethod] = useState("card");
    const [transferInfo, setTransferInfo] = useState(null);
    const [quote, setQuote] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [created, setCreated] = useState(null);
    const [paying, setPaying] = useState(false);

    useEffect(() => {
        setMeta(
            "Dubai Vize Başvuru Formu | Aile Başvurusu | VizeAtlas Dubai",
            "Dubai vize başvurunuzu online tamamlayın. Tek formda birden fazla yolcu ekleyin; çocuk vizesi ve aile indirimi otomatik hesaplanır."
        );
    }, []);

    useEffect(() => {
        Promise.all([api.get("/visa-types"), api.get("/content/site")])
            .then(([v, c]) => {
                setVisaTypes(v.data);
                setAddonMeta(c.data.addons || []);
                setMaxTravelers(c.data.max_travelers || 10);
                const wanted = searchParams.get("vize");
                if (wanted && v.data.some((x) => x.id === wanted)) {
                    const found = v.data.find((x) => x.id === wanted);
                    setTravelers((list) =>
                        list.map((t, i) =>
                            i === 0
                                ? { ...t, visa_type_id: wanted, applicant_type: found.applicant_type || "adult" }
                                : t
                        )
                    );
                }
            })
            .catch(() => toast.error("Vize tipleri yüklenemedi."));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // live authoritative price quote
    const selectedVisaIds = travelers.map((t) => t.visa_type_id).filter(Boolean);
    const quoteKey = JSON.stringify([selectedVisaIds, addons]);
    useEffect(() => {
        if (selectedVisaIds.length !== travelers.length || selectedVisaIds.length === 0) {
            setQuote(null);
            return;
        }
        let cancelled = false;
        api.post("/pricing/quote", { visa_type_ids: selectedVisaIds, addons })
            .then(({ data }) => {
                if (!cancelled) setQuote(data);
            })
            .catch(() => {});
        return () => {
            cancelled = true;
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [quoteKey]);

    const visaOptionsFor = (type) =>
        visaTypes.filter((v) =>
            type === "child" ? v.category === "child" : v.category !== "child"
        );

    const updateTraveler = (key, patch) => {
        setTravelers((list) => list.map((t) => (t.key === key ? { ...t, ...patch } : t)));
        setErrors((p) => ({ ...p, [key]: undefined }));
    };

    const addTraveler = (type) => {
        if (travelers.length >= maxTravelers) {
            toast.error(`Tek başvuruda en fazla ${maxTravelers} yolcu ekleyebilirsiniz.`);
            return;
        }
        setTravelers((list) => [...list, newTraveler(type)]);
        toast.success(type === "child" ? "Çocuk yolcu eklendi." : "Yolcu eklendi.");
    };

    const removeTraveler = (key) => {
        if (travelers.length === 1) {
            toast.error("En az bir yolcu bulunmalı.");
            return;
        }
        setTravelers((list) => list.filter((t) => t.key !== key));
    };

    // --- Yapay zeka ile pasaport okuma -------------------------------------
    const readPassportWithAI = async (key, fileInfo) => {
        if (!fileInfo?.file_id) return;
        if ((fileInfo.content_type || "").includes("pdf")) return;
        setOcr((s) => ({ ...s, [key]: { status: "loading" } }));
        try {
            const form = new FormData();
            form.append("file_id", fileInfo.file_id);
            const { data } = await api.post("/passport/read", form, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            if (!data?.ok) {
                setOcr((s) => ({ ...s, [key]: { status: "failed", message: data?.message || "" } }));
                return;
            }
            const d = data.data || {};
            const patch = {};
            const fields = [
                "first_name",
                "last_name",
                "birth_date",
                "gender",
                "passport_no",
                "passport_expiry",
                "national_id",
                "nationality",
            ];
            setTravelers((list) =>
                list.map((t) => {
                    if (t.key !== key) return t;
                    fields.forEach((f) => {
                        const value = d[f];
                        if (!value) return;
                        if (f === "nationality" && t.nationality && t.nationality !== "TR") return;
                        if (!t[f] || t[f] === "TR") patch[f] = value;
                    });
                    return { ...t, ...patch };
                })
            );
            setOcr((s) => ({
                ...s,
                [key]: {
                    status: "done",
                    filled: Object.keys(patch).length,
                    name: `${d.first_name || ""} ${d.last_name || ""}`.trim(),
                    passport_no: d.passport_no || "",
                },
            }));
            if (Object.keys(patch).length) {
                toast.success("Pasaport okundu, bilgiler dolduruldu. Lütfen kontrol edin.");
            }
        } catch (err) {
            setOcr((s) => ({ ...s, [key]: { status: "failed", message: apiError(err, "") } }));
        }
    };

    const setC = (key) => (e) => {
        setContact((f) => ({ ...f, [key]: e.target.value }));
        setErrors((p) => ({ ...p, [key]: undefined }));
    };
    const setT = (key) => (e) => {
        setTravel((f) => ({ ...f, [key]: e.target.value }));
        setErrors((p) => ({ ...p, [key]: undefined }));
    };

    const validateStep = useCallback(() => {
        const e = {};
        if (step === 0) {
            if (contact.full_name.trim().length < 3) e.full_name = "Adınızı ve soyadınızı yazın.";
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(contact.email)) e.email = "Geçerli bir e-posta adresi girin.";
            if (contact.phone.replace(/\D/g, "").length < 10) e.phone = "Telefon numaranızı alan koduyla girin.";
            travelers.forEach((t) => {
                const te = {};
                if (t.first_name.trim().length < 2) te.first_name = "Ad zorunlu (en az 2 karakter).";
                if (t.last_name.trim().length < 2) te.last_name = "Soyad zorunlu (en az 2 karakter).";
                if (!t.birth_date) te.birth_date = "Doğum tarihi zorunlu.";
                if (!t.gender) te.gender = "Cinsiyet seçimi zorunlu.";
                if (t.passport_no.trim().length < 4) te.passport_no = "Pasaport numarası zorunlu.";
                if (!t.passport_expiry) te.passport_expiry = "Pasaport geçerlilik tarihi zorunlu.";
                else if (new Date(t.passport_expiry) < new Date())
                    te.passport_expiry = "Pasaport geçerlilik tarihi geçmiş görünüyor.";
                if (t.birth_date && t.applicant_type === "child") {
                    const age = (Date.now() - new Date(t.birth_date).getTime()) / 31557600000;
                    if (age >= 18) te.birth_date = "Çocuk başvurusu için yolcu 18 yaşından küçük olmalı.";
                }
                if (Object.keys(te).length) e[t.key] = te;
            });
        }
        if (step === 1) {
            travelers.forEach((t) => {
                if (!t.visa_type_id) e[t.key] = { ...(e[t.key] || {}), visa_type_id: "Vize türü seçin." };
            });
            if (travel.birth_country !== "TR")
                e.birth_country = "Üzgünüz, başvuru şu an yalnızca Türkiye doğumlu kişiler için yapılabilmektedir.";
            if (!travel.arrival_date) e.arrival_date = "Gidiş tarihinizi seçin.";
            if (!travel.departure_date) e.departure_date = "Dönüş tarihinizi seçin.";
            if (
                travel.arrival_date &&
                travel.departure_date &&
                new Date(travel.departure_date) < new Date(travel.arrival_date)
            )
                e.departure_date = "Dönüş tarihi gidiş tarihinden önce olamaz.";
        }
        if (step === 2) {
            travelers.forEach((t) => {
                const te = {};
                if (!t.passportFile) te.passport = "Pasaport fotoğrafı zorunlu.";
                if (!t.photoFile) te.photo = "Vesikalık fotoğraf zorunlu.";
                if (Object.keys(te).length) e[t.key] = { ...(e[t.key] || {}), ...te };
            });
        }
        setErrors(e);
        if (Object.keys(e).length) {
            toast.error("Lütfen işaretli alanları kontrol edin.");
            return false;
        }
        return true;
    }, [step, contact, travelers, travel]);

    const next = () => {
        if (!validateStep()) return;
        setStep((s) => Math.min(s + 1, STEPS.length - 1));
        window.scrollTo({ top: 0, behavior: "smooth" });
    };
    const back = () => {
        setStep((s) => Math.max(s - 1, 0));
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    const submitApplication = async () => {
        if (!kvkk) {
            toast.error("Devam etmek için KVKK aydınlatma metnini onaylamanız gerekir.");
            return null;
        }
        setSubmitting(true);
        try {
            const { data } = await api.post("/applications", {
                contact,
                travelers: travelers.map((t) => ({
                    first_name: t.first_name,
                    last_name: t.last_name,
                    birth_date: t.birth_date,
                    gender: t.gender,
                    applicant_type: t.applicant_type,
                    nationality: t.nationality,
                    national_id: t.national_id,
                    passport_no: t.passport_no,
                    passport_expiry: t.passport_expiry,
                    visa_type_id: t.visa_type_id,
                    passport_file_id: t.passportFile.file_id,
                    photo_file_id: t.photoFile.file_id,
                })),
                travel,
                addons,
                extra_documents: {
                    ticket_file_id: extraDocs.ticket?.file_id || null,
                    hotel_file_id: extraDocs.hotel?.file_id || null,
                    other_file_ids: extraDocs.other ? [extraDocs.other.file_id] : [],
                },
                kvkk_accepted: true,
            });
            setCreated(data);
            toast.success(`Başvurunuz oluşturuldu. Takip kodu: ${data.reference_code}`);
            return data;
        } catch (err) {
            toast.error(apiError(err, "Başvuru oluşturulamadı."));
            return null;
        } finally {
            setSubmitting(false);
        }
    };

    const startPayment = async () => {
        let app = created;
        if (!app) {
            app = await submitApplication();
            if (!app) return;
        }
        setPaying(true);
        try {
            const { data } = await api.post("/payments/checkout", {
                application_id: app.id,
                origin_url: window.location.origin,
            });
            sessionStorage.setItem("dv_last_reference", app.reference_code);
            window.location.href = data.checkout_url;
        } catch (err) {
            toast.error(apiError(err, "Ödeme sayfası açılamadı. Lütfen tekrar deneyin."));
            setPaying(false);
        }
    };

    const startBankTransfer = async () => {
        let app = created;
        if (!app) {
            app = await submitApplication();
            if (!app) return;
        }
        setPaying(true);
        try {
            const { data } = await api.post("/payments/bank-transfer", {
                application_id: app.id,
                origin_url: window.location.origin,
            });
            sessionStorage.setItem("dv_last_reference", app.reference_code);
            setTransferInfo(data);
            toast.success("Havale/EFT bilgileri hazır. Ödemenizi yaptıktan sonra dekontu iletin.");
        } catch (err) {
            toast.error(apiError(err, "Havale bilgileri alınamadı."));
        } finally {
            setPaying(false);
        }
    };

    const progress = useMemo(() => ((step + 1) / STEPS.length) * 100, [step]);
    const visaById = (id) => visaTypes.find((v) => v.id === id);

    const urgentTrip = useMemo(() => {
        if (!travel.arrival_date) return false;
        const diff = new Date(travel.arrival_date).getTime() - Date.now();
        return diff > 0 && diff < 1000 * 60 * 60 * 72;
    }, [travel.arrival_date]);

    return (
        <div data-testid="application-wizard">
            <PageHeader
                eyebrow="Başvuru Formu"
                title="Dubai vize başvurunuzu tamamlayın"
                description="Tek formda birden fazla yolcu ekleyebilirsiniz. Çocuk vizesi indirimi ve aile indirimi otomatik hesaplanır."
            />

            <section className="section">
                <div className="container-page">
                    {/* STEPPER */}
                    <div className="card-surface p-5" data-testid="wizard-stepper">
                        <div className="flex items-center justify-between gap-2 overflow-x-auto pb-1">
                            {STEPS.map((s, i) => {
                                const Icon = s.icon;
                                const done = i < step;
                                const active = i === step;
                                return (
                                    <div key={s.key} className="flex min-w-fit items-center gap-2">
                                        <span
                                            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full border text-sm font-bold ${
                                                done
                                                    ? "border-primary bg-primary text-primary-foreground"
                                                    : active
                                                      ? "border-primary bg-primary/10 text-primary"
                                                      : "border-border bg-card text-muted-foreground"
                                            }`}
                                        >
                                            {done ? <CheckCircle2 className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
                                        </span>
                                        <span className={`whitespace-nowrap text-xs font-semibold sm:text-sm ${active ? "text-foreground" : "text-muted-foreground"}`}>
                                            {s.label}
                                        </span>
                                        {i < STEPS.length - 1 && <span className="mx-1 hidden h-px w-8 bg-border lg:block" aria-hidden="true" />}
                                    </div>
                                );
                            })}
                        </div>
                        <Progress value={progress} className="mt-4 h-2" />
                    </div>

                    <div className="mt-8 grid gap-8 lg:grid-cols-[1.4fr_0.6fr]">
                        <motion.div
                            key={step}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.22 }}
                            className="card-surface p-6 sm:p-8"
                        >
                            {/* STEP 0 */}
                            {step === 0 && (
                                <div data-testid="wizard-personal-info-form">
                                    <h2 className="font-heading text-xl font-bold">1. Kişisel bilgiler</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        İlk olarak sizinle iletişim kuracağımız bilgileri, ardondan seyahat edecek
                                        yolcuları ekleyin. Bilgileri pasaportta yazdığı gibi, Türkçe karakter
                                        kullanmadan girin.
                                    </p>

                                    <div className="mt-6 rounded-xl border border-border bg-[hsl(var(--cloud))] p-5">
                                        <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">
                                            İletişim bilgileri
                                        </h3>
                                        <div className="mt-4 grid gap-5 sm:grid-cols-2">
                                            <Field label="Adınız Soyadınız" required htmlFor="c-name" error={errors.full_name}>
                                                <Input id="c-name" value={contact.full_name} onChange={setC("full_name")} placeholder="AHMET YILMAZ" data-testid="input-contact-name" />
                                            </Field>
                                            <Field label="E-Posta Adresi" required htmlFor="c-email" error={errors.email}>
                                                <Input id="c-email" type="email" value={contact.email} onChange={setC("email")} placeholder="ornek@eposta.com" data-testid="input-contact-email" />
                                            </Field>
                                            <Field label="Telefon Numaranız" required htmlFor="c-phone" error={errors.phone}>
                                                <Input id="c-phone" value={contact.phone} onChange={setC("phone")} placeholder="0555 111 22 33" data-testid="input-contact-phone" />
                                            </Field>
                                            <Field label="Yaşadığınız şehir" htmlFor="c-city">
                                                <Input id="c-city" value={contact.address_city} onChange={setC("address_city")} placeholder="İstanbul" data-testid="input-contact-city" />
                                            </Field>
                                        </div>
                                    </div>

                                    <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
                                        <h3 className="font-heading text-base font-bold">
                                            Yolcular <span className="text-muted-foreground">({travelers.length})</span>
                                        </h3>
                                        <div className="flex flex-wrap gap-2">
                                            <Button type="button" variant="secondary" className="h-10 border border-border" onClick={() => addTraveler("adult")} data-testid="add-adult-traveler-button">
                                                <Plus className="mr-1.5 h-4 w-4" /> Yetişkin ekle
                                            </Button>
                                            <Button type="button" variant="secondary" className="h-10 border border-border" onClick={() => addTraveler("child")} data-testid="add-child-traveler-button">
                                                <Baby className="mr-1.5 h-4 w-4" /> Çocuk ekle
                                            </Button>
                                        </div>
                                    </div>

                                    <div className="mt-5 space-y-6">
                                        {travelers.map((t, idx) => {
                                            const te = errors[t.key] || {};
                                            return (
                                                <div key={t.key} className="rounded-xl border border-border p-5" data-testid={`traveler-card-${idx}`}>
                                                    <div className="flex flex-wrap items-center justify-between gap-3">
                                                        <div className="flex items-center gap-2.5">
                                                            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
                                                                {t.applicant_type === "child" ? <Baby className="h-4.5 w-4.5 text-primary" /> : <User className="h-4.5 w-4.5 text-primary" />}
                                                            </span>
                                                            <div>
                                                                <p className="font-heading text-sm font-bold">{idx + 1}. Yolcu</p>
                                                                <p className="text-xs text-muted-foreground">{t.applicant_type === "child" ? "Çocuk (18 yaş altı)" : "Yetişkin"}</p>
                                                            </div>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <div className="flex rounded-lg border border-border bg-card p-0.5">
                                                                {[
                                                                    { v: "adult", l: "Yetişkin" },
                                                                    { v: "child", l: "Çocuk" },
                                                                ].map((opt) => (
                                                                    <button
                                                                        key={opt.v}
                                                                        type="button"
                                                                        onClick={() => updateTraveler(t.key, { applicant_type: opt.v, visa_type_id: "" })}
                                                                        data-testid={`traveler-${idx}-type-${opt.v}`}
                                                                        className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-colors ${
                                                                            t.applicant_type === opt.v ? "bg-primary text-primary-foreground" : "text-muted-foreground"
                                                                        }`}
                                                                    >
                                                                        {opt.l}
                                                                    </button>
                                                                ))}
                                                            </div>
                                                            {travelers.length > 1 && (
                                                                <Button type="button" variant="secondary" className="h-9 border border-border text-destructive" onClick={() => removeTraveler(t.key)} data-testid={`remove-traveler-${idx}`}>
                                                                    <Trash2 className="h-4 w-4" />
                                                                </Button>
                                                            )}
                                                        </div>
                                                    </div>

                                                    <div className="mt-5 rounded-xl border border-dashed border-primary/40 bg-primary/[0.04] p-4" data-testid={`traveler-${idx}-ai-passport-box`}>
                                                        <p className="flex items-center gap-2 text-sm font-bold">
                                                            <Sparkles className="h-4 w-4 text-primary" />
                                                            Pasaportunuzu yükleyin, bilgiler otomatik dolsun
                                                        </p>
                                                        <p className="mt-1 text-xs leading-5 text-muted-foreground">
                                                            Pasaportunuzun kimlik sayfasının fotoğrafını yükleyin; ad, soyad,
                                                            pasaport numarası ve tarihleri yapay zeka okuyup aşağıdaki alanlara
                                                            yazsın. Yüklediğiniz dosya evrak adımında da kullanılır.
                                                        </p>
                                                        <div className="mt-3">
                                                            <FileDropzone
                                                                label="Pasaport kimlik sayfası"
                                                                hint="JPG veya PNG"
                                                                docType="passport"
                                                                value={t.passportFile}
                                                                onChange={(f) => {
                                                                    updateTraveler(t.key, { passportFile: f });
                                                                    readPassportWithAI(t.key, f);
                                                                }}
                                                                testId={`traveler-${idx}-passport-ai-input`}
                                                            />
                                                        </div>
                                                        {ocr[t.key]?.status === "loading" && (
                                                            <p className="mt-2 flex items-center gap-2 text-xs font-medium text-primary" data-testid={`traveler-${idx}-ocr-loading`}>
                                                                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                                                Pasaport yapay zeka ile okunuyor...
                                                            </p>
                                                        )}
                                                        {ocr[t.key]?.status === "done" && (
                                                            <p className="mt-2 text-xs font-semibold text-[hsl(var(--brand-green))]" data-testid={`traveler-${idx}-ocr-success`}>
                                                                Pasaport okundu: {ocr[t.key].name} {ocr[t.key].passport_no ? `· ${ocr[t.key].passport_no}` : ""} — lütfen bilgileri kontrol edin.
                                                            </p>
                                                        )}
                                                        {ocr[t.key]?.status === "failed" && (
                                                            <p className="mt-2 text-xs text-muted-foreground" data-testid={`traveler-${idx}-ocr-failed`}>
                                                                Pasaport otomatik okunamadı; bilgileri elle girebilirsiniz.
                                                            </p>
                                                        )}
                                                    </div>

                                                    <div className="mt-5 grid gap-5 sm:grid-cols-2">
                                                        <Field label="Ad" required error={te.first_name}>
                                                            <Input value={t.first_name} onChange={(e) => updateTraveler(t.key, { first_name: e.target.value })} placeholder="AHMET" data-testid={`traveler-${idx}-first-name`} />
                                                        </Field>
                                                        <Field label="Soyad" required error={te.last_name}>
                                                            <Input value={t.last_name} onChange={(e) => updateTraveler(t.key, { last_name: e.target.value })} placeholder="YILMAZ" data-testid={`traveler-${idx}-last-name`} />
                                                        </Field>
                                                        <Field label="Doğum tarihi" required error={te.birth_date}>
                                                            <Input type="date" value={t.birth_date} onChange={(e) => updateTraveler(t.key, { birth_date: e.target.value })} data-testid={`traveler-${idx}-birth-date`} />
                                                        </Field>
                                                        <Field label="Cinsiyet" required error={te.gender}>
                                                            <Select value={t.gender} onValueChange={(v) => updateTraveler(t.key, { gender: v })}>
                                                                <SelectTrigger data-testid={`traveler-${idx}-gender`}>
                                                                    <SelectValue placeholder="Seçiniz" />
                                                                </SelectTrigger>
                                                                <SelectContent>
                                                                    <SelectItem value="male">Erkek</SelectItem>
                                                                    <SelectItem value="female">Kadın</SelectItem>
                                                                </SelectContent>
                                                            </Select>
                                                        </Field>
                                                        <Field label="Pasaport numarası" required error={te.passport_no}>
                                                            <Input value={t.passport_no} onChange={(e) => updateTraveler(t.key, { passport_no: e.target.value })} placeholder="U12345678" data-testid={`traveler-${idx}-passport-no`} />
                                                        </Field>
                                                        <Field label="Pasaport geçerlilik tarihi" required error={te.passport_expiry}>
                                                            <Input type="date" value={t.passport_expiry} onChange={(e) => updateTraveler(t.key, { passport_expiry: e.target.value })} data-testid={`traveler-${idx}-passport-expiry`} />
                                                        </Field>
                                                        <Field label="T.C. Kimlik No">
                                                            <Input value={t.national_id} onChange={(e) => updateTraveler(t.key, { national_id: e.target.value })} placeholder="11 haneli kimlik numarası" data-testid={`traveler-${idx}-national-id`} />
                                                        </Field>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>

                                    <div className="mt-6 flex items-start gap-2.5 rounded-xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.09)] p-4">
                                        <AlertTriangle className="mt-0.5 h-4.5 w-4.5 shrink-0 text-[hsl(var(--status-warning))]" />
                                        <p className="text-sm leading-6 text-[hsl(var(--status-warning))]">
                                            18 yaşından küçük çocuklar bireysel olarak başvuru yapamaz. Çocukları
                                            mutlaka ebeveyn ile aynı başvuruya ekleyin.
                                        </p>
                                    </div>
                                </div>
                            )}

                            {/* STEP 1 */}
                            {step === 1 && (
                                <div data-testid="wizard-visa-details-form">
                                    <h2 className="font-heading text-xl font-bold">2. Vize ve seyahat bilgileri</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Her yolcu için vize türünü seçin, ardından seyahat tarihlerinizi girin.
                                    </p>

                                    <div className="mt-6 space-y-4">
                                        {travelers.map((t, idx) => {
                                            const te = errors[t.key] || {};
                                            const options = visaOptionsFor(t.applicant_type);
                                            const selected = visaById(t.visa_type_id);
                                            return (
                                                <div key={t.key} className="rounded-xl border border-border p-5" data-testid={`visa-select-card-${idx}`}>
                                                    <div className="flex flex-wrap items-center justify-between gap-2">
                                                        <p className="font-heading text-sm font-bold">
                                                            {t.first_name || `${idx + 1}. Yolcu`} {t.last_name}
                                                            <span className="ml-2 rounded-full bg-muted px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
                                                                {t.applicant_type === "child" ? "Çocuk" : "Yetişkin"}
                                                            </span>
                                                        </p>
                                                        {selected && (
                                                            <span className="font-heading text-base font-bold">{formatMoney(selected.price, selected.currency)}</span>
                                                        )}
                                                    </div>
                                                    <div className="mt-4">
                                                        <Field label="Vize Türü" required error={te.visa_type_id}>
                                                            <Select value={t.visa_type_id} onValueChange={(v) => updateTraveler(t.key, { visa_type_id: v })}>
                                                                <SelectTrigger data-testid={`traveler-${idx}-visa-type`}>
                                                                    <SelectValue placeholder="Seçiniz" />
                                                                </SelectTrigger>
                                                                <SelectContent>
                                                                    {options.map((v) => (
                                                                        <SelectItem key={v.id} value={v.id}>
                                                                            {v.name} – {formatMoney(v.price, v.currency)}
                                                                        </SelectItem>
                                                                    ))}
                                                                </SelectContent>
                                                            </Select>
                                                        </Field>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>

                                    <div className="mt-7 grid gap-5 sm:grid-cols-2">
                                        <Field label="Doğum Ülkesi" required error={errors.birth_country}>
                                            <Select value={travel.birth_country} onValueChange={(v) => { setTravel((f) => ({ ...f, birth_country: v })); setErrors((p) => ({ ...p, birth_country: undefined })); }}>
                                                <SelectTrigger data-testid="select-birth-country">
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="TR">Türkiye</SelectItem>
                                                    <SelectItem value="OTHER">Diğer ülkeler</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </Field>
                                        <Field label="Seyahat amacı">
                                            <Select value={travel.purpose} onValueChange={(v) => setTravel((f) => ({ ...f, purpose: v }))}>
                                                <SelectTrigger data-testid="select-purpose">
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    {PURPOSES.map((p) => (
                                                        <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                        </Field>
                                        <Field label="Giriş (gidiş) tarihi" required error={errors.arrival_date}>
                                            <Input type="date" value={travel.arrival_date} onChange={setT("arrival_date")} data-testid="input-arrival-date" />
                                        </Field>
                                        <Field label="Dönüş tarihi" required error={errors.departure_date}>
                                            <Input type="date" value={travel.departure_date} onChange={setT("departure_date")} data-testid="input-departure-date" />
                                        </Field>
                                        <Field label="Uçuş numarası">
                                            <Input value={travel.flight_no} onChange={setT("flight_no")} placeholder="Örn. TK760" data-testid="input-flight-no" />
                                        </Field>
                                        <Field label="Otel / konaklama">
                                            <Input value={travel.accommodation} onChange={setT("accommodation")} placeholder="Otel adı veya adres" data-testid="input-accommodation" />
                                        </Field>
                                    </div>

                                    <div className="mt-5">
                                        <Field label="Eklemek istediğiniz not">
                                            <Textarea rows={3} value={travel.notes} onChange={setT("notes")} placeholder="Danışmanımızın bilmesi gereken bir durum varsa yazın…" data-testid="input-notes" />
                                        </Field>
                                    </div>

                                    {urgentTrip && (
                                        <div className="mt-6 flex items-start gap-2.5 rounded-xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.11)] p-4" data-testid="urgent-trip-warning">
                                            <AlertTriangle className="mt-0.5 h-4.5 w-4.5 shrink-0 text-[hsl(var(--status-warning))]" />
                                            <p className="text-sm leading-6 text-[hsl(var(--status-warning))]">
                                                <strong>Seyahat tarihinize 72 saatten az kaldı!</strong> Başvurunuzun
                                                zamanında sonuçlanması için ekspres vize hizmetini seçmenizi öneririz.
                                            </p>
                                        </div>
                                    )}

                                    <div className="mt-8">
                                        <h3 className="font-heading text-base font-bold">Ek hizmetler</h3>
                                        <p className="mt-1.5 text-sm text-muted-foreground">Ücretler yolcu başına eklenir.</p>
                                        <div className="mt-4 space-y-4">
                                            {addonMeta.map((a) => (
                                                <label key={a.id} className="flex cursor-pointer items-start gap-4 rounded-xl border border-border bg-card p-5" data-testid={`addon-toggle-row-${a.id}`}>
                                                    <Switch
                                                        checked={!!addons[a.id]}
                                                        onCheckedChange={(c) => setAddons((s) => ({ ...s, [a.id]: !!c }))}
                                                        className="mt-1"
                                                        data-testid={`addon-switch-${a.id}`}
                                                    />
                                                    <div className="flex-1">
                                                        <div className="flex flex-wrap items-center justify-between gap-2">
                                                            <p className="font-heading text-sm font-bold">{a.name}</p>
                                                            <span className="font-heading text-sm font-bold text-primary">
                                                                + {formatMoney(a.price, a.currency)} / kişi
                                                            </span>
                                                        </div>
                                                        <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{a.description}</p>
                                                    </div>
                                                </label>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* STEP 2 */}
                            {step === 2 && (
                                <div data-testid="wizard-document-upload-dropzone">
                                    <h2 className="font-heading text-xl font-bold">3. Evrak yükleme</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Her yolcu için pasaport ve vesikalık fotoğraf zorunludur. Belgeleriniz şifreli
                                        olarak saklanır ve yalnızca başvurunuz için kullanılır.
                                    </p>

                                    <div className="mt-6 space-y-7">
                                        {travelers.map((t, idx) => {
                                            const te = errors[t.key] || {};
                                            return (
                                                <div key={t.key} className="rounded-xl border border-border p-5" data-testid={`docs-card-${idx}`}>
                                                    <p className="font-heading text-sm font-bold">
                                                        {t.first_name || `${idx + 1}. Yolcu`} {t.last_name}
                                                        <span className="ml-2 rounded-full bg-muted px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
                                                            {t.applicant_type === "child" ? "Çocuk" : "Yetişkin"}
                                                        </span>
                                                    </p>
                                                    <div className="mt-5 grid gap-6 md:grid-cols-2">
                                                        <div>
                                                            <FileDropzone
                                                                label="Pasaport Fotoğrafı"
                                                                hint="Zorunlu · Yapay zeka okur"
                                                                docType="passport"
                                                                value={t.passportFile}
                                                                onChange={(f) => {
                                                                    updateTraveler(t.key, { passportFile: f });
                                                                    readPassportWithAI(t.key, f);
                                                                }}
                                                                testId={`traveler-${idx}-passport-upload-input`}
                                                            />
                                                            {ocr[t.key]?.status === "loading" && (
                                                                <p className="mt-2 flex items-center gap-2 text-xs font-medium text-primary" data-testid={`traveler-${idx}-docs-ocr-loading`}>
                                                                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                                                    Pasaport yapay zeka ile okunuyor...
                                                                </p>
                                                            )}
                                                            {ocr[t.key]?.status === "done" && (
                                                                <div className="mt-2 rounded-lg border border-[hsl(var(--brand-green)/0.30)] bg-[hsl(var(--brand-green)/0.07)] p-3" data-testid={`traveler-${idx}-docs-ocr-success`}>
                                                                    <p className="flex items-center gap-2 text-xs font-semibold text-[hsl(var(--brand-green))]">
                                                                        <Sparkles className="h-3.5 w-3.5" />
                                                                        Pasaport okundu: {ocr[t.key].name} {ocr[t.key].passport_no ? `· ${ocr[t.key].passport_no}` : ""}
                                                                    </p>
                                                                    <p className="mt-1 text-xs text-muted-foreground">
                                                                        Boş alanlar otomatik dolduruldu. Lütfen 1. adımdaki bilgileri kontrol edin.
                                                                    </p>
                                                                </div>
                                                            )}
                                                            {ocr[t.key]?.status === "failed" && (
                                                                <p className="mt-2 text-xs text-muted-foreground" data-testid={`traveler-${idx}-docs-ocr-failed`}>
                                                                    Pasaport otomatik okunamadı; bilgileri elle girebilirsiniz.
                                                                </p>
                                                            )}
                                                            {te.passport && (
                                                                <p className="mt-2 flex items-start gap-1.5 text-xs font-medium text-destructive">
                                                                    <AlertCircle className="mt-0.5 h-3.5 w-3.5" /> {te.passport}
                                                                </p>
                                                            )}
                                                        </div>
                                                        <div>
                                                            <FileDropzone
                                                                label="Vesikalık Fotoğraf"
                                                                hint="Zorunlu"
                                                                docType="photo"
                                                                value={t.photoFile}
                                                                onChange={(f) => updateTraveler(t.key, { photoFile: f })}
                                                                testId={`traveler-${idx}-photo-upload-input`}
                                                            />
                                                            {te.photo && (
                                                                <p className="mt-2 flex items-start gap-1.5 text-xs font-medium text-destructive">
                                                                    <AlertCircle className="mt-0.5 h-3.5 w-3.5" /> {te.photo}
                                                                </p>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}

                                        <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-5">
                                            <p className="font-heading text-sm font-bold">Opsiyonel belgeler (tüm başvuru için)</p>
                                            <div className="mt-5 grid gap-6 md:grid-cols-3">
                                                <FileDropzone label="Dönüş Uçak Bileti" hint="Opsiyonel" docType="ticket" value={extraDocs.ticket} onChange={(f) => setExtraDocs((s) => ({ ...s, ticket: f }))} testId="ticket-upload-input" />
                                                <FileDropzone label="Otel Rezervasyonu" hint="Opsiyonel" docType="hotel" value={extraDocs.hotel} onChange={(f) => setExtraDocs((s) => ({ ...s, hotel: f }))} testId="hotel-upload-input" />
                                                <FileDropzone label="Diğer Evrak" hint="Opsiyonel" docType="other" value={extraDocs.other} onChange={(f) => setExtraDocs((s) => ({ ...s, other: f }))} testId="other-upload-input" />
                                            </div>
                                        </div>
                                    </div>

                                    <div className="mt-7 rounded-xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.09)] p-4 text-sm leading-6 text-[hsl(var(--status-warning))]">
                                        Fotoğraflarınız beyaz fonda, son 6 ay içinde çekilmiş, gözlüksüz ve şapkasız
                                        olmalıdır. Uygun olmayan fotoğraf en sık ret sebebidir.
                                    </div>
                                </div>
                            )}

                            {/* STEP 3 */}
                            {step === 3 && (
                                <div data-testid="wizard-summary-section">
                                    <h2 className="font-heading text-xl font-bold">4. Özet ve ödeme</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Bilgilerinizi kontrol edin. "Ödemeye geç" butonuna bastığınızda başvurunuz
                                        oluşturulur ve güvenli ödeme sayfasına yönlendirilirsiniz.
                                    </p>

                                    {created && (
                                        <div className="mt-5 rounded-xl border border-[hsl(var(--brand-green)/0.30)] bg-[hsl(var(--brand-green)/0.08)] p-4" data-testid="application-created-banner">
                                            <p className="text-sm font-semibold text-[hsl(var(--brand-green))]">
                                                Başvurunuz kaydedildi. Takip kodunuz:{" "}
                                                <span className="font-heading tracking-wider" data-testid="created-reference-code">{created.reference_code}</span>
                                            </p>
                                            <p className="mt-1 text-xs text-[hsl(var(--brand-green))]/80">
                                                Ödemeniz tamamlanmadığı sürece başvurunuz işleme alınmaz. Bu kodu saklayın.
                                            </p>
                                        </div>
                                    )}

                                    <div className="mt-6 space-y-6">
                                        <div className="rounded-xl border border-border p-5">
                                            <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">İletişim</h3>
                                            <div className="mt-3">
                                                <SummaryRow label="Ad Soyad" value={contact.full_name} />
                                                <SummaryRow label="E-posta" value={contact.email} />
                                                <SummaryRow label="Telefon" value={contact.phone} />
                                            </div>
                                        </div>

                                        <div className="rounded-xl border border-border p-5">
                                            <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">
                                                Yolcular ({travelers.length})
                                            </h3>
                                            <div className="mt-3 space-y-4">
                                                {travelers.map((t, idx) => {
                                                    const v = visaById(t.visa_type_id);
                                                    return (
                                                        <div key={t.key} className="rounded-lg bg-[hsl(var(--cloud))] p-4" data-testid={`summary-traveler-${idx}`}>
                                                            <div className="flex flex-wrap items-center justify-between gap-2">
                                                                <p className="text-sm font-bold">
                                                                    {t.first_name} {t.last_name}
                                                                    <span className="ml-2 text-xs font-medium text-muted-foreground">
                                                                        {t.applicant_type === "child" ? "Çocuk" : "Yetişkin"}
                                                                    </span>
                                                                </p>
                                                                <span className="font-heading text-sm font-bold">{v ? formatMoney(v.price, v.currency) : "-"}</span>
                                                            </div>
                                                            <p className="mt-1 text-xs text-muted-foreground">
                                                                {v?.name} · Pasaport: {t.passport_no} · Geçerlilik: {formatDate(t.passport_expiry)}
                                                            </p>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>

                                        <div className="rounded-xl border border-border p-5">
                                            <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">Seyahat</h3>
                                            <div className="mt-3">
                                                <SummaryRow label="Gidiş" value={formatDate(travel.arrival_date)} />
                                                <SummaryRow label="Dönüş" value={formatDate(travel.departure_date)} />
                                                <SummaryRow label="Amacı" value={PURPOSE_LABELS[travel.purpose]} />
                                                <SummaryRow label="Konaklama" value={travel.accommodation} />
                                            </div>
                                        </div>

                                        {quote && (
                                            <div className="rounded-xl border border-primary/30 bg-primary/5 p-5" data-testid="summary-price-breakdown">
                                                <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">Fiyat dökümü</h3>
                                                <div className="mt-3">
                                                    <SummaryRow label={`Vize bedelleri (${quote.traveler_count} yolcu)`} value={formatMoney(quote.subtotal, quote.currency)} />
                                                    {quote.family_discount > 0 && (
                                                        <SummaryRow
                                                            label={`Aile indirimi (%${Math.round(quote.family_discount_rate * 100)})`}
                                                            value={`- ${formatMoney(quote.family_discount, quote.currency)}`}
                                                        />
                                                    )}
                                                    {(quote.addons || []).map((a) => (
                                                        <SummaryRow key={a.id} label={`${a.name} x${a.quantity}`} value={formatMoney(a.total, quote.currency)} />
                                                    ))}
                                                    <SummaryRow label="Toplam" value={formatMoney(quote.total, quote.currency)} strong />
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {!created && (
                                        <label className="mt-6 flex cursor-pointer items-start gap-3 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                                            <Checkbox checked={kvkk} onCheckedChange={(v) => setKvkk(!!v)} className="mt-0.5" data-testid="kvkk-checkbox" />
                                            <span className="text-sm leading-6">
                                                KVKK aydınlatma metnini okudum, bilgilerimin ve yüklediğim belgelerin vize
                                                başvurumun hazırlanması amacıyla işlenmesini onaylıyorum.
                                            </span>
                                        </label>
                                    )}

                                    {/* ÖDEME YÖNTEMİ */}
                                    <div className="mt-6" data-testid="payment-method-section">
                                        <h3 className="font-heading text-base font-bold">Ödeme yöntemi</h3>
                                        <div className="mt-3 grid gap-3 sm:grid-cols-2">
                                            {[
                                                {
                                                    id: "card",
                                                    title: "Kredi / Banka Kartı",
                                                    detail: "3D Secure ile güvenli ödeme, anında işleme alınır.",
                                                    icon: CreditCard,
                                                },
                                                {
                                                    id: "transfer",
                                                    title: "Havale / EFT",
                                                    detail: "Banka hesabımıza gönderin, dekont sonrası işleme alınır.",
                                                    icon: Landmark,
                                                },
                                            ].map((m) => (
                                                <button
                                                    key={m.id}
                                                    type="button"
                                                    onClick={() => setPayMethod(m.id)}
                                                    data-testid={`payment-method-${m.id}`}
                                                    className={`flex items-start gap-3 rounded-xl border-2 p-4 text-left transition-colors duration-150 ${
                                                        payMethod === m.id
                                                            ? "border-primary bg-primary/[0.05]"
                                                            : "border-border hover:border-primary/40"
                                                    }`}
                                                >
                                                    <m.icon className={`mt-0.5 h-5 w-5 shrink-0 ${payMethod === m.id ? "text-primary" : "text-muted-foreground"}`} />
                                                    <span>
                                                        <span className="block text-sm font-bold">{m.title}</span>
                                                        <span className="mt-1 block text-xs leading-5 text-muted-foreground">{m.detail}</span>
                                                    </span>
                                                </button>
                                            ))}
                                        </div>

                                        {transferInfo && (
                                            <div className="mt-4 rounded-xl border border-primary/30 bg-primary/[0.05] p-5" data-testid="bank-transfer-details">
                                                <h4 className="font-heading text-sm font-bold">{transferInfo.bank?.title}</h4>
                                                <dl className="mt-3 space-y-2 text-sm">
                                                    <div className="flex justify-between gap-3">
                                                        <dt className="text-muted-foreground">Hesap sahibi</dt>
                                                        <dd className="text-right font-semibold">{transferInfo.bank?.account_name}</dd>
                                                    </div>
                                                    <div className="flex justify-between gap-3">
                                                        <dt className="text-muted-foreground">Banka</dt>
                                                        <dd className="text-right font-semibold">{transferInfo.bank?.bank_name}</dd>
                                                    </div>
                                                    <div className="flex justify-between gap-3">
                                                        <dt className="text-muted-foreground">IBAN</dt>
                                                        <dd className="text-right font-mono-code font-semibold" data-testid="bank-transfer-iban">{transferInfo.bank?.iban}</dd>
                                                    </div>
                                                    <div className="flex justify-between gap-3">
                                                        <dt className="text-muted-foreground">Açıklama</dt>
                                                        <dd className="text-right font-mono-code font-semibold">{transferInfo.reference_code}</dd>
                                                    </div>
                                                    <div className="flex justify-between gap-3 border-t border-border pt-2">
                                                        <dt className="text-muted-foreground">Tutar</dt>
                                                        <dd className="text-right font-bold text-[hsl(var(--brand-red))]">
                                                            {formatMoney(transferInfo.amount, transferInfo.currency)}
                                                        </dd>
                                                    </div>
                                                </dl>
                                                <p className="mt-3 text-xs leading-5 text-muted-foreground">{transferInfo.bank?.note}</p>
                                                <Button asChild variant="secondary" className="mt-4 h-10 border border-border">
                                                    <a href={`https://wa.me/${(COMPANY.whatsapp || "").replace(/\D/g, "")}?text=${encodeURIComponent(`Merhaba, ${transferInfo.reference_code} numaralı başvurumun havale dekontunu göndermek istiyorum.`)}`} target="_blank" rel="noreferrer" data-testid="send-receipt-whatsapp">
                                                        Dekontu WhatsApp'tan gönder
                                                    </a>
                                                </Button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* NAV */}
                            <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-6">
                                <Button type="button" variant="secondary" className="h-11 border border-border" onClick={back} disabled={step === 0} data-testid="wizard-prev-step-button">
                                    <ArrowLeft className="mr-2 h-4 w-4" /> Geri
                                </Button>

                                {step < STEPS.length - 1 ? (
                                    <Button type="button" className="h-11 px-6" onClick={next} data-testid="wizard-next-step-button">
                                        Devam Et <ArrowRight className="ml-2 h-4 w-4" />
                                    </Button>
                                ) : (
                                    <Button type="button" className="h-12 px-7 text-base" onClick={payMethod === "transfer" ? startBankTransfer : startPayment} disabled={submitting || paying} data-testid="wizard-pay-button">
                                        {submitting || paying ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                {submitting ? "Başvuru kaydediliyor…" : payMethod === "transfer" ? "Hazırlanıyor…" : "Ödeme sayfası açılıyor…"}
                                            </>
                                        ) : payMethod === "transfer" ? (
                                            <>
                                                <Landmark className="mr-2 h-4 w-4" /> Havale bilgilerini al
                                            </>
                                        ) : (
                                            <>
                                                <Lock className="mr-2 h-4 w-4" /> Ödemeye geç
                                            </>
                                        )}
                                    </Button>
                                )}
                            </div>
                        </motion.div>

                        {/* SIDEBAR */}
                        <aside className="space-y-5">
                            <div className="card-surface p-5" data-testid="wizard-order-summary">
                                <h3 className="font-heading text-base font-bold">Başvuru özeti</h3>
                                <p className="mt-2 text-sm text-muted-foreground">{travelers.length} yolcu</p>
                                {quote ? (
                                    <div className="mt-4 space-y-2 border-t border-border pt-4 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Vize bedelleri</span>
                                            <span className="font-semibold">{formatMoney(quote.subtotal, quote.currency)}</span>
                                        </div>
                                        {quote.family_discount > 0 && (
                                            <div className="flex justify-between text-[hsl(var(--success))]">
                                                <span>Aile indirimi (%{Math.round(quote.family_discount_rate * 100)})</span>
                                                <span className="font-semibold">- {formatMoney(quote.family_discount, quote.currency)}</span>
                                            </div>
                                        )}
                                        {(quote.addons || []).map((a) => (
                                            <div key={a.id} className="flex justify-between">
                                                <span className="text-muted-foreground">{a.name} x{a.quantity}</span>
                                                <span className="font-semibold">{formatMoney(a.total, quote.currency)}</span>
                                            </div>
                                        ))}
                                        <div className="flex items-end justify-between border-t border-border pt-3">
                                            <span className="text-sm font-semibold">Toplam</span>
                                            <span className="font-heading text-2xl font-bold" data-testid="summary-total-price">
                                                {formatMoney(quote.total, quote.currency)}
                                            </span>
                                        </div>
                                    </div>
                                ) : (
                                    <p className="mt-4 border-t border-border pt-4 text-sm text-muted-foreground">
                                        Fiyat hesabı için her yolcu için vize türü seçin.
                                    </p>
                                )}
                            </div>

                            <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-5">
                                <div className="flex items-center gap-2">
                                    <ShieldCheck className="h-4 w-4 text-primary" />
                                    <h3 className="font-heading text-sm font-bold">Bilgileriniz güvende</h3>
                                </div>
                                <ul className="mt-3 space-y-2 text-xs leading-5 text-muted-foreground">
                                    <li>• Kart bilgileriniz sunucularımıza kaydedilmez.</li>
                                    <li>• Belgeleriniz yalnızca başvurunuz için kullanılır.</li>
                                    <li>• Onaylanan vizeniz PDF olarak e-postanıza gönderilir.</li>
                                </ul>
                            </div>

                            <div className="rounded-xl border border-border bg-card p-5">
                                <h3 className="font-heading text-sm font-bold">Yardıma mı ihtiyacınız var?</h3>
                                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                                    Formu doldururken takılırsanız WhatsApp butonundan yazın; danışmanımız
                                    adım adım yardımcı olsun.
                                </p>
                                <Button type="button" variant="secondary" className="mt-4 h-10 w-full border border-border" onClick={() => navigate("/gerekli-belgeler")}>
                                    Gerekli belgeleri gör
                                </Button>
                            </div>
                        </aside>
                    </div>
                </div>
            </section>
        </div>
    );
}
