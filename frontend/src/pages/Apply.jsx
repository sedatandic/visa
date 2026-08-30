import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
    AlertCircle,
    ArrowLeft,
    ArrowRight,
    CalendarDays,
    CheckCircle2,
    CreditCard,
    FileText,
    Loader2,
    Lock,
    ShieldCheck,
    User,
} from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatDate, formatMoney, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { VisaTypeCard } from "../components/VisaTypeCard";
import { FileDropzone } from "../components/FileDropzone";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Progress } from "../components/ui/progress";
import { Checkbox } from "../components/ui/checkbox";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";

const STEPS = [
    { key: "visa", label: "Vize Seçimi", icon: ShieldCheck },
    { key: "personal", label: "Kişisel Bilgiler", icon: User },
    { key: "travel", label: "Seyahat Bilgileri", icon: CalendarDays },
    { key: "documents", label: "Belgeler", icon: FileText },
    { key: "summary", label: "Özet & Ödeme", icon: CreditCard },
];

const emptyApplicant = {
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    birth_date: "",
    gender: "",
    nationality: "TR",
    national_id: "",
    passport_no: "",
    passport_expiry: "",
    address_city: "",
};

const emptyTravel = {
    arrival_date: "",
    departure_date: "",
    purpose: "tourism",
    accommodation: "",
    flight_no: "",
    notes: "",
};

const PURPOSES = [
    { value: "tourism", label: "Turistik gezi" },
    { value: "business", label: "İş seyahati" },
    { value: "family", label: "Aile / arkadaş ziyareti" },
    { value: "transit", label: "Transit geçiş" },
    { value: "other", label: "Diğer" },
];

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

const SummaryRow = ({ label, value }) => (
    <div className="flex items-start justify-between gap-4 border-b border-border py-2.5 last:border-0">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-right text-sm font-semibold">{value || "-"}</span>
    </div>
);

export default function Apply() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const [visaTypes, setVisaTypes] = useState([]);
    const [selectedVisa, setSelectedVisa] = useState(null);
    const [step, setStep] = useState(0);
    const [applicant, setApplicant] = useState(emptyApplicant);
    const [travel, setTravel] = useState(emptyTravel);
    const [passportFile, setPassportFile] = useState(null);
    const [photoFile, setPhotoFile] = useState(null);
    const [kvkk, setKvkk] = useState(false);
    const [errors, setErrors] = useState({});
    const [submitting, setSubmitting] = useState(false);
    const [created, setCreated] = useState(null);
    const [paying, setPaying] = useState(false);

    useEffect(() => {
        setMeta(
            "Dubai Vize Başvuru Formu | VizeAtlas Dubai",
            "Dubai vize başvurunuzu 5 dakikada online tamamlayın: kişisel bilgiler, seyahat detayları, belge yükleme ve güvenli ödeme."
        );
    }, []);

    useEffect(() => {
        api.get("/visa-types")
            .then(({ data }) => {
                setVisaTypes(data);
                const wanted = searchParams.get("vize");
                if (wanted) {
                    const found = data.find((v) => v.id === wanted);
                    if (found) {
                        setSelectedVisa(found);
                        setStep(1);
                    }
                }
            })
            .catch(() => toast.error("Vize tipleri yüklenemedi."));
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const setA = (key) => (e) => {
        setApplicant((f) => ({ ...f, [key]: e.target.value }));
        setErrors((p) => ({ ...p, [key]: undefined }));
    };
    const setT = (key) => (e) => {
        setTravel((f) => ({ ...f, [key]: e.target.value }));
        setErrors((p) => ({ ...p, [key]: undefined }));
    };

    const validateStep = useCallback(() => {
        const e = {};
        if (step === 0 && !selectedVisa) {
            toast.error("Lütfen bir vize tipi seçin.");
            return false;
        }
        if (step === 1) {
            if (applicant.first_name.trim().length < 2) e.first_name = "Adınızı yazın (en az 2 karakter).";
            if (applicant.last_name.trim().length < 2) e.last_name = "Soyadınızı yazın (en az 2 karakter).";
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(applicant.email)) e.email = "Geçerli bir e-posta adresi girin.";
            if (applicant.phone.replace(/\D/g, "").length < 10) e.phone = "Telefon numaranızı alan koduyla girin.";
            if (!applicant.birth_date) e.birth_date = "Doğum tarihinizi seçin.";
            if (!applicant.gender) e.gender = "Cinsiyet seçimi zorunludur.";
            if (applicant.passport_no.trim().length < 4) e.passport_no = "Pasaport numaranızı girin.";
            if (!applicant.passport_expiry) e.passport_expiry = "Pasaport geçerlilik tarihini seçin.";
            else if (new Date(applicant.passport_expiry) < new Date())
                e.passport_expiry = "Pasaportunuzun geçerlilik tarihi geçmiş görünüyor.";
        }
        if (step === 2) {
            if (!travel.arrival_date) e.arrival_date = "Gidiş tarihinizi seçin.";
            if (!travel.departure_date) e.departure_date = "Dönüş tarihinizi seçin.";
            if (
                travel.arrival_date &&
                travel.departure_date &&
                new Date(travel.departure_date) < new Date(travel.arrival_date)
            )
                e.departure_date = "Dönüş tarihi gidiş tarihinden önce olamaz.";
        }
        if (step === 3) {
            if (!passportFile) e.passport = "Pasaport taraması yüklemeniz gerekiyor.";
            if (!photoFile) e.photo = "Biyometrik fotoğraf yüklemeniz gerekiyor.";
        }
        setErrors(e);
        if (Object.keys(e).length) {
            toast.error("Lütfen işaretli alanları kontrol edin.");
            return false;
        }
        return true;
    }, [step, selectedVisa, applicant, travel, passportFile, photoFile]);

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
                visa_type_id: selectedVisa.id,
                applicant,
                travel,
                documents: {
                    passport_file_id: passportFile.file_id,
                    photo_file_id: photoFile.file_id,
                    extra_file_ids: [],
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

    const progress = useMemo(() => ((step + 1) / STEPS.length) * 100, [step]);

    return (
        <div data-testid="application-wizard">
            <PageHeader
                eyebrow="Başvuru Formu"
                title="Dubai vize başvurunuzu tamamlayın"
                description="Bilgileriniz yalnızca vize başvurunuz için kullanılır. Ödeme adımından önce tüm bilgilerinizi özet ekranında kontrol edebilirsiniz."
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
                                            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full border text-sm font-bold transition-colors duration-150 ${
                                                done
                                                    ? "border-primary bg-primary text-primary-foreground"
                                                    : active
                                                      ? "border-primary bg-primary/10 text-primary"
                                                      : "border-border bg-card text-muted-foreground"
                                            }`}
                                        >
                                            {done ? <CheckCircle2 className="h-4.5 w-4.5" /> : <Icon className="h-4 w-4" />}
                                        </span>
                                        <span
                                            className={`whitespace-nowrap text-xs font-semibold sm:text-sm ${
                                                active ? "text-foreground" : "text-muted-foreground"
                                            }`}
                                        >
                                            {s.label}
                                        </span>
                                        {i < STEPS.length - 1 && (
                                            <span className="mx-1 hidden h-px w-6 bg-border lg:block" aria-hidden="true" />
                                        )}
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
                            {/* STEP 0: VISA */}
                            {step === 0 && (
                                <div>
                                    <h2 className="font-heading text-xl font-bold">1. Vize tipini seçin</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Kalış sürenize uygun vizeyi seçin. Daha sonra bu adıma geri dönebilirsiniz.
                                    </p>
                                    <div className="mt-6 grid gap-5 md:grid-cols-2">
                                        {visaTypes.map((v) => (
                                            <VisaTypeCard
                                                key={v.id}
                                                visa={v}
                                                compact
                                                selected={selectedVisa?.id === v.id}
                                                onSelect={(visa) => setSelectedVisa(visa)}
                                            />
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* STEP 1: PERSONAL */}
                            {step === 1 && (
                                <div data-testid="wizard-personal-info-form">
                                    <h2 className="font-heading text-xl font-bold">2. Kişisel bilgiler</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Bilgilerinizi pasaportunuzda yazdığı gibi, Türkçe karakter kullanmadan girin.
                                    </p>
                                    <div className="mt-6 grid gap-5 sm:grid-cols-2">
                                        <Field label="Ad" required htmlFor="first_name" error={errors.first_name}>
                                            <Input id="first_name" value={applicant.first_name} onChange={setA("first_name")} placeholder="AHMET" data-testid="input-first-name" />
                                        </Field>
                                        <Field label="Soyad" required htmlFor="last_name" error={errors.last_name}>
                                            <Input id="last_name" value={applicant.last_name} onChange={setA("last_name")} placeholder="YILMAZ" data-testid="input-last-name" />
                                        </Field>
                                        <Field label="E-posta" required htmlFor="email" error={errors.email}>
                                            <Input id="email" type="email" value={applicant.email} onChange={setA("email")} placeholder="ornek@eposta.com" data-testid="input-email" />
                                        </Field>
                                        <Field label="Telefon" required htmlFor="phone" error={errors.phone}>
                                            <Input id="phone" value={applicant.phone} onChange={setA("phone")} placeholder="0555 111 22 33" data-testid="input-phone" />
                                        </Field>
                                        <Field label="Doğum tarihi" required htmlFor="birth_date" error={errors.birth_date}>
                                            <Input id="birth_date" type="date" value={applicant.birth_date} onChange={setA("birth_date")} data-testid="input-birth-date" />
                                        </Field>
                                        <Field label="Cinsiyet" required error={errors.gender}>
                                            <Select
                                                value={applicant.gender}
                                                onValueChange={(v) => {
                                                    setApplicant((f) => ({ ...f, gender: v }));
                                                    setErrors((p) => ({ ...p, gender: undefined }));
                                                }}
                                            >
                                                <SelectTrigger data-testid="select-gender">
                                                    <SelectValue placeholder="Seçiniz" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="male">Erkek</SelectItem>
                                                    <SelectItem value="female">Kadın</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </Field>
                                        <Field label="T.C. Kimlik No" htmlFor="national_id">
                                            <Input id="national_id" value={applicant.national_id} onChange={setA("national_id")} placeholder="11 haneli kimlik numarası" data-testid="input-national-id" />
                                        </Field>
                                        <Field label="Yaşadığınız şehir" htmlFor="address_city">
                                            <Input id="address_city" value={applicant.address_city} onChange={setA("address_city")} placeholder="İstanbul" data-testid="input-city" />
                                        </Field>
                                        <Field label="Pasaport numarası" required htmlFor="passport_no" error={errors.passport_no}>
                                            <Input id="passport_no" value={applicant.passport_no} onChange={setA("passport_no")} placeholder="U12345678" data-testid="input-passport-no" />
                                        </Field>
                                        <Field label="Pasaport geçerlilik tarihi" required htmlFor="passport_expiry" error={errors.passport_expiry}>
                                            <Input id="passport_expiry" type="date" value={applicant.passport_expiry} onChange={setA("passport_expiry")} data-testid="input-passport-expiry" />
                                        </Field>
                                    </div>
                                </div>
                            )}

                            {/* STEP 2: TRAVEL */}
                            {step === 2 && (
                                <div data-testid="wizard-travel-form">
                                    <h2 className="font-heading text-xl font-bold">3. Seyahat bilgileri</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Kesin bileti almadıysanız tahmini tarihleri girebilirsiniz.
                                    </p>
                                    <div className="mt-6 grid gap-5 sm:grid-cols-2">
                                        <Field label="Dubai'ye gidiş tarihi" required htmlFor="arrival_date" error={errors.arrival_date}>
                                            <Input id="arrival_date" type="date" value={travel.arrival_date} onChange={setT("arrival_date")} data-testid="input-arrival-date" />
                                        </Field>
                                        <Field label="Dönüş tarihi" required htmlFor="departure_date" error={errors.departure_date}>
                                            <Input id="departure_date" type="date" value={travel.departure_date} onChange={setT("departure_date")} data-testid="input-departure-date" />
                                        </Field>
                                        <Field label="Seyahat amacı">
                                            <Select value={travel.purpose} onValueChange={(v) => setTravel((f) => ({ ...f, purpose: v }))}>
                                                <SelectTrigger data-testid="select-purpose">
                                                    <SelectValue placeholder="Seçiniz" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    {PURPOSES.map((p) => (
                                                        <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                        </Field>
                                        <Field label="Uçuş numarası" htmlFor="flight_no">
                                            <Input id="flight_no" value={travel.flight_no} onChange={setT("flight_no")} placeholder="Örn. TK760" data-testid="input-flight-no" />
                                        </Field>
                                    </div>
                                    <div className="mt-5 space-y-5">
                                        <Field label="Otel / konaklama adresi" htmlFor="accommodation">
                                            <Input id="accommodation" value={travel.accommodation} onChange={setT("accommodation")} placeholder="Otel adı veya kalacağınız adres" data-testid="input-accommodation" />
                                        </Field>
                                        <Field label="Eklemek istediğiniz not" htmlFor="notes">
                                            <Textarea id="notes" rows={4} value={travel.notes} onChange={setT("notes")} placeholder="Danışmanımızın bilmesi gereken bir durum varsa yazın…" data-testid="input-notes" />
                                        </Field>
                                    </div>
                                </div>
                            )}

                            {/* STEP 3: DOCUMENTS */}
                            {step === 3 && (
                                <div data-testid="wizard-document-upload-dropzone">
                                    <h2 className="font-heading text-xl font-bold">4. Belgeleri yükleyin</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Belgeleriniz şifreli olarak saklanır ve yalnızca başvurunuz için kullanılır.
                                    </p>
                                    <div className="mt-6 space-y-7">
                                        <div>
                                            <FileDropzone
                                                label="Pasaport ana sayfası (fotoğraflı sayfa)"
                                                hint="Zorunlu"
                                                docType="passport"
                                                value={passportFile}
                                                onChange={(f) => {
                                                    setPassportFile(f);
                                                    setErrors((p) => ({ ...p, passport: undefined }));
                                                }}
                                                testId="passport-upload-input"
                                            />
                                            {errors.passport && (
                                                <p className="mt-2 flex items-start gap-1.5 text-xs font-medium text-destructive">
                                                    <AlertCircle className="mt-0.5 h-3.5 w-3.5" /> {errors.passport}
                                                </p>
                                            )}
                                        </div>
                                        <div>
                                            <FileDropzone
                                                label="Biyometrik fotoğraf (vesikalık)"
                                                hint="Zorunlu"
                                                docType="photo"
                                                value={photoFile}
                                                onChange={(f) => {
                                                    setPhotoFile(f);
                                                    setErrors((p) => ({ ...p, photo: undefined }));
                                                }}
                                                testId="biometric-photo-upload-input"
                                            />
                                            {errors.photo && (
                                                <p className="mt-2 flex items-start gap-1.5 text-xs font-medium text-destructive">
                                                    <AlertCircle className="mt-0.5 h-3.5 w-3.5" /> {errors.photo}
                                                </p>
                                            )}
                                        </div>
                                    </div>
                                    <div className="mt-7 rounded-xl border border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.1)] p-4 text-sm leading-6 text-[#7A4B00]">
                                        Fotoğrafınız beyaz fonda, son 6 ay içinde çekilmiş, gözlüksüz ve şapkasız
                                        olmalıdır. Uygun olmayan fotoğraf en sık ret sebebidir.
                                    </div>
                                </div>
                            )}

                            {/* STEP 4: SUMMARY */}
                            {step === 4 && (
                                <div data-testid="wizard-summary-section">
                                    <h2 className="font-heading text-xl font-bold">5. Özet ve ödeme</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Bilgilerinizi kontrol edin. "Ödemeye geç" butonuna bastığınızda başvurunuz
                                        oluşturulur ve güvenli ödeme sayfasına yönlendirilirsiniz.
                                    </p>

                                    {created && (
                                        <div className="mt-5 rounded-xl border border-[rgba(22,163,74,0.35)] bg-[rgba(22,163,74,0.08)] p-4" data-testid="application-created-banner">
                                            <p className="text-sm font-semibold text-[#14532D]">
                                                Başvurunuz kaydedildi. Takip kodunuz:{" "}
                                                <span className="font-heading tracking-wider" data-testid="created-reference-code">
                                                    {created.reference_code}
                                                </span>
                                            </p>
                                            <p className="mt-1 text-xs text-[#14532D]/80">
                                                Ödemeniz tamamlanmadığı sürece başvurunuz işleme alınmaz. Bu kodu saklayın.
                                            </p>
                                        </div>
                                    )}

                                    <div className="mt-6 space-y-6">
                                        <div className="rounded-xl border border-border p-5">
                                            <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">Vize</h3>
                                            <div className="mt-3">
                                                <SummaryRow label="Vize tipi" value={selectedVisa?.name} />
                                                <SummaryRow label="Giriş hakkı" value={selectedVisa?.entry_label} />
                                                <SummaryRow label="Sonuçlanma süresi" value={selectedVisa?.processing_days} />
                                                <SummaryRow label="Tutar" value={selectedVisa ? formatMoney(selectedVisa.price, selectedVisa.currency) : "-"} />
                                            </div>
                                        </div>
                                        <div className="rounded-xl border border-border p-5">
                                            <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">Başvuru sahibi</h3>
                                            <div className="mt-3">
                                                <SummaryRow label="Ad Soyad" value={`${applicant.first_name} ${applicant.last_name}`} />
                                                <SummaryRow label="E-posta" value={applicant.email} />
                                                <SummaryRow label="Telefon" value={applicant.phone} />
                                                <SummaryRow label="Doğum tarihi" value={formatDate(applicant.birth_date)} />
                                                <SummaryRow label="Pasaport No" value={applicant.passport_no} />
                                                <SummaryRow label="Pasaport geçerlilik" value={formatDate(applicant.passport_expiry)} />
                                            </div>
                                        </div>
                                        <div className="rounded-xl border border-border p-5">
                                            <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">Seyahat</h3>
                                            <div className="mt-3">
                                                <SummaryRow label="Gidiş" value={formatDate(travel.arrival_date)} />
                                                <SummaryRow label="Dönüş" value={formatDate(travel.departure_date)} />
                                                <SummaryRow label="Amacı" value={PURPOSES.find((p) => p.value === travel.purpose)?.label} />
                                                <SummaryRow label="Konaklama" value={travel.accommodation} />
                                            </div>
                                        </div>
                                        <div className="rounded-xl border border-border p-5">
                                            <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">Belgeler</h3>
                                            <div className="mt-3">
                                                <SummaryRow label="Pasaport taraması" value={passportFile?.original_filename} />
                                                <SummaryRow label="Biyometrik fotoğraf" value={photoFile?.original_filename} />
                                            </div>
                                        </div>
                                    </div>

                                    {!created && (
                                        <label className="mt-6 flex cursor-pointer items-start gap-3 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                                            <Checkbox
                                                checked={kvkk}
                                                onCheckedChange={(v) => setKvkk(!!v)}
                                                className="mt-0.5"
                                                data-testid="kvkk-checkbox"
                                            />
                                            <span className="text-sm leading-6">
                                                KVKK aydınlatma metnini okudum, bilgilerimin vize başvurumun
                                                hazırlanması amacıyla işlenmesini onaylıyorum.
                                            </span>
                                        </label>
                                    )}
                                </div>
                            )}

                            {/* NAV BUTTONS */}
                            <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-6">
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="h-11 border border-border"
                                    onClick={back}
                                    disabled={step === 0}
                                    data-testid="wizard-prev-step-button"
                                >
                                    <ArrowLeft className="mr-2 h-4 w-4" /> Geri
                                </Button>

                                {step < STEPS.length - 1 ? (
                                    <Button type="button" className="h-11 px-6" onClick={next} data-testid="wizard-next-step-button">
                                        Devam et <ArrowRight className="ml-2 h-4 w-4" />
                                    </Button>
                                ) : (
                                    <Button
                                        type="button"
                                        className="h-12 px-7 text-base"
                                        onClick={startPayment}
                                        disabled={submitting || paying}
                                        data-testid="wizard-pay-button"
                                    >
                                        {submitting || paying ? (
                                            <>
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                {submitting ? "Başvuru kaydediliyor…" : "Ödeme sayfası açılıyor…"}
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
                                {selectedVisa ? (
                                    <>
                                        <p className="mt-3 text-sm font-semibold">{selectedVisa.name}</p>
                                        <p className="text-xs text-muted-foreground">{selectedVisa.entry_label} · {selectedVisa.processing_days}</p>
                                        <div className="mt-4 flex items-end justify-between border-t border-border pt-4">
                                            <span className="text-sm text-muted-foreground">Toplam</span>
                                            <span className="font-heading text-2xl font-bold" data-testid="summary-total-price">
                                                {formatMoney(selectedVisa.price, selectedVisa.currency)}
                                            </span>
                                        </div>
                                    </>
                                ) : (
                                    <p className="mt-3 text-sm text-muted-foreground">Henüz vize tipi seçilmedi.</p>
                                )}
                            </div>

                            <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-5">
                                <div className="flex items-center gap-2">
                                    <ShieldCheck className="h-4.5 w-4.5 text-primary" />
                                    <h3 className="font-heading text-sm font-bold">Bilgileriniz güvende</h3>
                                </div>
                                <ul className="mt-3 space-y-2 text-xs leading-5 text-muted-foreground">
                                    <li>• Kart bilgileriniz sunucularımıza kaydedilmez.</li>
                                    <li>• Belgeleriniz yalnızca başvurunuz için kullanılır.</li>
                                    <li>• Ödeme sonrası takip kodunuz e-postanıza gönderilir.</li>
                                </ul>
                            </div>

                            <div className="rounded-xl border border-border bg-card p-5">
                                <h3 className="font-heading text-sm font-bold">Yardıma mı ihtiyacınız var?</h3>
                                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                                    Formu doldururken takılırsanız WhatsApp butonundan yazın; danışmanımız
                                    adım adım yardımcı olsun.
                                </p>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="mt-4 h-10 w-full border border-border"
                                    onClick={() => navigate("/gerekli-belgeler")}
                                >
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
