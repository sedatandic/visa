import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
    AlertCircle,
    AlertTriangle,
    ArrowLeft,
    ArrowRight,
    Baby,
    CalendarDays,
    Check,
    CheckCircle2,
    CreditCard,
    FileText,
    Info,
    Loader2,
    Pencil,
    Landmark,
    Lock,
    Minus,
    Plus,
    Save,
    ShieldCheck,
    Signal,
    Sparkles,
    ScanLine,
    Star,
    Tag,
    Trash2,
    User,
    Users,
    Wifi,
} from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { api, apiError, customerAuth } from "../lib/api";
import { formatDate, formatMoney, setMeta } from "../lib/site";
import { useContact, waLink } from "../lib/contact";
import { PageHeader } from "../components/SiteLayout";
import { FileDropzone } from "../components/FileDropzone";
import { EligibilityPreCheck } from "../components/EligibilityPreCheck";
import { DateField, fromISODate } from "../components/DateField";
import { FxNote } from "../components/FxNote";
import { BundlePicker } from "../components/BundlePicker";
import { ExtrasQuickAdd } from "../components/ExtrasQuickAdd";
import { ComboSelector } from "../components/ComboSelector";
import { BankTransferInfo } from "../components/BankTransferInfo";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
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
    { key: "people", label: "Bilgiler", icon: Users },
    { key: "visa", label: "Vize", icon: CalendarDays },
    { key: "docs", label: "Evraklar", icon: FileText },
    { key: "summary", label: "Ödeme", icon: CreditCard },
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
    // BAE basvurusunda zorunlu ek bilgiler (pasaportta yer almaz, kullanici girer)
    marital_status: type === "child" ? "single" : "",
    profession: type === "child" ? "Student" : "",
    mother_name: "",
    father_name: "",
    // Pasaport OCR'dan sessizce doldurulan alanlar (kullanıcıya sorulmaz)
    passport_issue_date: "",
    birth_place: "",
    passport_issue_place: "",
    visa_type_id: "",
    passportFile: null,
    photoFile: null,
});

const Field = ({ label, children, error, required, htmlFor }) => (
    <div className="space-y-2" data-invalid={error ? "true" : undefined}>
        <Label htmlFor={htmlFor}>
            {label} {required && <span className="text-destructive">*</span>}
        </Label>
        {children}
        {error && (
            <p className="flex items-start gap-1.5 text-xs font-medium text-destructive" role="alert">
                <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                {error}
            </p>
        )}
    </div>
);

const ERROR_LABELS = {
    full_name: "Adınız Soyadınız",
    email: "E-posta adresi",
    phone: "Telefon numarası",
    first_name: "Ad",
    last_name: "Soyad",
    birth_date: "Doğum Tarihi",
    marital_status: "Medeni Hal",
    profession: "Meslek",
    mother_name: "Anne Adı",
    father_name: "Baba Adı",
    passport_no: "Pasaport numarası",
    passport_expiry: "Pasaport geçerlilik tarihi",
    visa_type_id: "Vize Türü",
    birth_country: "Doğum ülkesi",
    arrival_date: "Gidiş tarihi",
    departure_date: "Dönüş tarihi",
    passport: "Pasaport fotoğrafı",
    photo: "Vesikalık fotoğraf",
    ticket: "Dönüş uçak bileti",
    hotel: "Otel rezervasyonu",
};

/** Hata nesnesinden kullaniciya gosterilecek alan adlarini cikarir. */
const collectErrorLabels = (errorObj, travelers) => {
    const labels = [];
    Object.entries(errorObj || {}).forEach(([key, value]) => {
        if (typeof value === "string") {
            labels.push(ERROR_LABELS[key] || key);
            return;
        }
        const index = travelers.findIndex((t) => t.key === key);
        const prefix = index >= 0 ? `${index + 1}. yolcu: ` : "";
        Object.keys(value || {}).forEach((field) => {
            labels.push(`${prefix}${ERROR_LABELS[field] || field}`);
        });
    });
    return labels;
};

const SummaryRow = ({ label, value, strong }) => (
    <div className="flex items-start justify-between gap-4 border-b border-border py-2.5 last:border-0">
        <span className={`text-sm ${strong ? "font-semibold" : "text-muted-foreground"}`}>{label}</span>
        <span className={`text-right text-sm ${strong ? "font-bold" : "font-semibold"}`}>{value || "-"}</span>
    </div>
);

export default function Apply() {
    const siteContact = useContact();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const [visaTypes, setVisaTypes] = useState([]);
    const [addonMeta, setAddonMeta] = useState([]);
    const [maxTravelers, setMaxTravelers] = useState(10);
    const [step, setStep] = useState(0);
    const [contact, setContact] = useState({ full_name: "", email: "", phone: "", address_city: "", whatsapp_optin: false });
    const [travelers, setTravelers] = useState([newTraveler()]);
    const [openNationalId, setOpenNationalId] = useState({});
    const [fieldsOpen, setFieldsOpen] = useState({});
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
    // Vize basvurusu icinde satilan ek urunler (magaza katalogundan)
    const [storeProducts, setStoreProducts] = useState([]);
    const [bundleInfo, setBundleInfo] = useState(null);
    const [insurancePick, setInsurancePick] = useState(null);
    const [esimQty, setEsimQty] = useState({});
    const [tourQty, setTourQty] = useState({});
    const [tourSchedule, setTourSchedule] = useState({});
    const [extraDocs, setExtraDocs] = useState({ ticket: null, hotel: null, other: null });
    const [kvkk, setKvkk] = useState(false);
    const [errors, setErrors] = useState({});
    const [ocr, setOcr] = useState({});
    const [photoCheck, setPhotoCheck] = useState({});
    const [payMethod, setPayMethod] = useState("card");
    const [transferInfo, setTransferInfo] = useState(null);
    const [bankInfo, setBankInfo] = useState(null);
    const [agencyItems, setAgencyItems] = useState([]);
    const [quote, setQuote] = useState(null);
    const [submitting, setSubmitting] = useState(false);
    const [created, setCreated] = useState(null);
    const [paying, setPaying] = useState(false);
    const [draft, setDraft] = useState({ id: null, code: null });
    const [savingDraft, setSavingDraft] = useState(false);
    const [savedTravelers, setSavedTravelers] = useState([]);
    const [preCheckDone, setPreCheckDone] = useState(false);

    // Giris yapmis musterinin kayitli yolcularini getir (aile profili)
    useEffect(() => {
        if (!customerAuth.token) return;
        api.get("/account/travelers")
            .then(({ data }) => setSavedTravelers(data.items || []))
            .catch(() => {});
    }, []);

    const addSavedTraveler = (saved) => {
        if (travelers.length >= maxTravelers) {
            toast.error(`Tek başvuruda en fazla ${maxTravelers} yolcu ekleyebilirsiniz.`);
            return;
        }
        const type = saved.applicant_type === "child" ? "child" : "adult";
        setTravelers((list) => [
            ...list,
            {
                ...newTraveler(type),
                first_name: saved.first_name || "",
                last_name: saved.last_name || "",
                birth_date: saved.birth_date || "",
                gender: saved.gender || "",
                national_id: saved.national_id || "",
                passport_no: saved.passport_no || "",
                passport_expiry: saved.passport_expiry || "",
                marital_status: saved.marital_status || (type === "child" ? "single" : ""),
                profession: saved.profession || (type === "child" ? "Student" : ""),
                mother_name: saved.mother_name || "",
                father_name: saved.father_name || "",
                applicant_type: type,
            },
        ]);
        toast.success(`${saved.first_name} ${saved.last_name} eklendi. Belgelerini yüklemeyi unutmayın.`);
    };

    // --- Taslak kaydet / devam et -----------------------------------------
    const saveDraft = async ({ silent = false } = {}) => {
        if (!contact.email.trim()) {
            if (silent) return;
            setStep(0);
            setErrors((p) => ({ ...p, contact: { ...(p.contact || {}), email: "Kaydetmek için e-posta gerekli." } }));
            toast.error("Başvurunuzu kaydetmek için e-posta adresinizi girin.");
            return;
        }
        if (!silent) setSavingDraft(true);
        try {
            const { data } = await api.post("/drafts", {
                email: contact.email.trim(),
                draft_id: draft.id,
                resume_code: draft.code,
                step,
                traveler_count: travelers.length,
                title: `${travelers.length} yolcu · ${contact.full_name || contact.email}`,
                data: { contact, travelers, travel, addons, extraDocs, step, insurancePick, esimQty, tourQty, tourSchedule },
            });
            setDraft({ id: data.draft_id, code: data.resume_code });
            if (!silent) {
                toast.success(
                    `Başvurunuz kaydedildi. Devam kodunuz: ${data.resume_code}` +
                        (data.email_status === "sent" ? " (e-postanıza da gönderildi)" : "")
                );
            }
        } catch (err) {
            if (!silent) toast.error(apiError(err, "Taslak kaydedilemedi."));
        } finally {
            if (!silent) setSavingDraft(false);
        }
    };

    // Otomatik taslak kaydi: e-posta girildikten sonra kullanici formu yarida
    // birakirsa, "kaldigin yerden devam" linkini e-postayla gonderebilmek icin
    // arka planda sessizce kaydediyoruz (5 sn'de bir, degisiklik oldukca).
    const autoSaveRef = useRef({ signature: "", submitted: false });
    useEffect(() => {
        if (submitting) return;
        const email = (contact.email || "").trim();
        if (!email.includes("@") || step < 1) return;
        const signature = JSON.stringify({ email, step, travelers, travel, addons, contact });
        if (signature === autoSaveRef.current.signature) return;
        const timer = setTimeout(() => {
            autoSaveRef.current.signature = signature;
            saveDraft({ silent: true });
        }, 5000);
        return () => clearTimeout(timer);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [contact, travelers, travel, addons, step, submitting]);

    // taslaktan devam / onceki basvurudan kopyala
    useEffect(() => {
        const draftId = searchParams.get("taslak");
        const resumeCode = searchParams.get("kod");
        const copyId = searchParams.get("kopya");

        const applyDraftData = (d) => {
            if (!d) return;
            if (d.contact) setContact((c) => ({ ...c, ...d.contact }));
            if (Array.isArray(d.travelers) && d.travelers.length) setTravelers(d.travelers);
            if (d.travel) setTravel((t) => ({ ...t, ...d.travel }));
            if (d.addons) setAddons((a) => ({ ...a, ...d.addons }));
            if (d.insurancePick) setInsurancePick(d.insurancePick);
            if (d.esimQty && typeof d.esimQty === "object") setEsimQty(d.esimQty);
            if (d.tourQty && typeof d.tourQty === "object") setTourQty(d.tourQty);
            if (d.tourSchedule && typeof d.tourSchedule === "object") setTourSchedule(d.tourSchedule);
            if (d.extraDocs) setExtraDocs((e) => ({ ...e, ...d.extraDocs }));
            if (typeof d.step === "number") setStep(Math.min(d.step, 3));
        };

        if (draftId && resumeCode) {
            api.get(`/drafts/${draftId}`, { params: { code: resumeCode } })
                .then(({ data }) => {
                    applyDraftData(data.data);
                    setDraft({ id: data.id, code: data.resume_code });
                    toast.success("Kaydedilen başvurunuz yüklendi. Kaldığınız yerden devam edebilirsiniz.");
                })
                .catch(() => toast.error("Taslak bulunamadı veya devam kodu hatalı."));
            return;
        }

        if (copyId) {
            api.get(`/account/applications/${copyId}`)
                .then(({ data }) => {
                    if (data.contact) setContact((c) => ({ ...c, ...data.contact }));
                    if (data.travel) setTravel((t) => ({ ...t, ...data.travel, arrival_date: "", departure_date: "" }));
                    if (Array.isArray(data.travelers)) {
                        setTravelers(
                            data.travelers.map((t) => ({
                                ...newTraveler(t.applicant_type || "adult"),
                                first_name: t.first_name || "",
                                last_name: t.last_name || "",
                                birth_date: t.birth_date || "",
                                gender: t.gender || "",
                                national_id: t.national_id || "",
                                passport_no: t.passport_no || "",
                                passport_expiry: t.passport_expiry || "",
                                marital_status: t.marital_status || "",
                                profession: t.profession || "",
                                mother_name: t.mother_name || "",
                                father_name: t.father_name || "",
                                visa_type_id: t.visa_type_id || "",
                                applicant_type: t.applicant_type || "adult",
                            }))
                        );
                    }
                    toast.success("Önceki başvurunuzun bilgileri forma kopyalandı. Belgeleri yeniden yüklemeniz gerekir.");
                })
                .catch(() => toast.error("Önceki başvuru bilgileri alınamadı. Lütfen tekrar giriş yapın."));
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        setMeta(
            "Dubai Vize Başvuru Formu | Aile Başvurusu | Dubai Vize Online",
            "Dubai vize başvurunuzu online tamamlayın. Tek formda birden fazla yolcu ekleyin; çocuk vizesi ve aile indirimi otomatik hesaplanır."
        );
    }, []);

    useEffect(() => {
        Promise.all([api.get("/visa-types"), api.get("/content/site")])
            .then(([v, c]) => {
                setVisaTypes(v.data);
                setAddonMeta(c.data.addons || []);
                setMaxTravelers(c.data.max_travelers || 10);
                setBankInfo(c.data.bank_transfer || null);
                setAgencyItems((c.data.agency_info || {}).items || []);
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
    const travelerCount = travelers.length;

    // Magaza urunleri (eSIM + seyahat sigortasi) basvuru icinde de satilir
    useEffect(() => {
        api.get("/products")
            .then(({ data }) => {
                setStoreProducts(data.items || []);
                if (data.bundle) setBundleInfo(data.bundle);
            })
            .catch(() => {});
    }, []);

    const esimProducts = useMemo(() => storeProducts.filter((p) => p.kind === "esim"), [storeProducts]);
    const tourProducts = useMemo(() => storeProducts.filter((p) => p.kind === "tour"), [storeProducts]);
    const allInsuranceProducts = useMemo(
        () => storeProducts.filter((p) => p.kind === "insurance"),
        [storeProducts]
    );

    // eSIM / sigorta gecerliligi seyahatin giris tarihinde baslar
    const travelDatesReady = Boolean(travel.arrival_date);
    const tripDays = useMemo(() => {
        if (!travel.arrival_date || !travel.departure_date) return null;
        const start = new Date(travel.arrival_date);
        const end = new Date(travel.departure_date);
        if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || end < start) return null;
        return Math.round((end - start) / 86400000) + 1;
    }, [travel.arrival_date, travel.departure_date]);

    // Poliçe seçenekleri, seçilen vizenin kalış süresini AŞMAYACAK şekilde listelenir
    // (30 günlük vizede 30 gün ve altı, 60 günlük vizede 60 gün ve altı poliçeler).
    const visaCoverDays = useMemo(() => {
        const visaDays = travelers
            .map((t) => Number(visaTypes.find((v) => v.id === t.visa_type_id)?.duration_days || 0))
            .filter(Boolean);
        return visaDays.length ? Math.max(...visaDays) : null;
    }, [travelers, visaTypes]);

    const insuranceProducts = useMemo(() => {        if (!visaCoverDays) return allInsuranceProducts;
        const fitting = allInsuranceProducts.filter(
            (p) => Number(p.validity_days) <= visaCoverDays
        );
        return fitting.length ? fitting : allInsuranceProducts;
    }, [allInsuranceProducts, visaCoverDays]);

    const productWindow = (product) => {
        if (!travel.arrival_date) return null;
        const start = new Date(travel.arrival_date);
        if (Number.isNaN(start.getTime())) return null;
        const days = Number(product.validity_days) || 0;
        const end = days > 0 ? new Date(start.getTime() + (days - 1) * 86400000) : null;
        return {
            startLabel: formatDate(start),
            endLabel: end ? formatDate(end) : null,
            shortOfTrip: Boolean(tripDays && days > 0 && tripDays > days),
            days,
        };
    };

    const DateWindowNote = ({ product, testId }) => {
        const win = productWindow(product);
        if (!win) return null;
        return (
            <div className="mt-2 space-y-1" data-testid={testId}>
                <p className="flex items-start gap-1.5 text-xs font-medium text-muted-foreground">
                    <CalendarDays className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                    <span>
                        {win.startLabel} tarihinde başlar
                        {win.endLabel ? ` · ${win.endLabel} tarihine kadar geçerli` : ""}
                    </span>
                </p>
                {win.shortOfTrip && (
                    <p className="text-xs font-semibold text-[hsl(var(--status-warning))]">
                        Seyahatiniz {tripDays} gün; bu paket {win.days} gün geçerli. Daha uzun süreli bir paket seçmenizi öneririz.
                    </p>
                )}
            </div>
        );
    };

    // Akilli oneri: seyahat suresini karsilayan en uygun (en ekonomik) paket
    const bestFit = (list) => {
        if (!tripDays || !list.length) return null;
        const covering = list.filter((p) => Number(p.validity_days) >= tripDays);
        if (covering.length) {
            return covering.reduce((best, p) => (Number(p.price) < Number(best.price) ? p : best)).id;
        }
        return list.reduce((best, p) =>
            Number(p.validity_days) > Number(best.validity_days) ? p : best
        ).id;
    };

    const recommendedInsuranceId = useMemo(
        () => bestFit(insuranceProducts),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [insuranceProducts, tripDays]
    );
    const recommendedEsimId = useMemo(
        () => bestFit(esimProducts),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [esimProducts, tripDays]
    );

    const bundleActive = Boolean(insurancePick) && Object.values(esimQty).some((q) => q > 0);

    // Vize suresine gore hazir paketler
    const [bundles, setBundles] = useState([]);
    useEffect(() => {
        if (!visaCoverDays) {
            setBundles([]);
            return;
        }
        api.get(`/bundles?visa_days=${visaCoverDays}`)
            .then(({ data }) => setBundles(data.items || []))
            .catch(() => setBundles([]));
    }, [visaCoverDays]);

    const selectedBundleId = useMemo(() => {
        const match = bundles.find(
            (b) => b.insurance.id === insurancePick && Number(esimQty[b.esim.id] || 0) > 0
        );
        return match?.id || null;
    }, [bundles, insurancePick, esimQty]);

    const pickBundle = (bundle) => {
        setInsurancePick(bundle.insurance.id);
        setEsimQty({ [bundle.esim.id]: 1 });
        toast.success(`${bundle.name} eklendi.`);
    };

    // Ana sayfadan paket secilerek gelindiyse (?paket=pack_x) secimleri hazir getir
    const bundleParam = searchParams.get("paket");
    const bundleApplied = useRef(false);
    useEffect(() => {
        if (!bundleParam || bundleApplied.current) return;
        api.get("/bundles")
            .then(({ data }) => {
                const match = (data.items || []).find((b) => b.id === bundleParam);
                if (!match) return;
                bundleApplied.current = true;
                setInsurancePick(match.insurance.id);
                setEsimQty({ [match.esim.id]: 1 });
                if (match.visa?.id) {
                    setTravelers((list) =>
                        list.map((t) =>
                            t.applicant_type === "child" ? t : { ...t, visa_type_id: match.visa.id }
                        )
                    );
                }
                toast.success(`${match.name} seçildi. Vize, sigorta ve eSIM hazır geldi.`);
            })
            .catch(() => {});
    }, [bundleParam]);

    // Süre değişince kapsamı yetmeyen poliçe seçimini düşür
    useEffect(() => {
        if (insurancePick && !insuranceProducts.some((p) => p.id === insurancePick)) {
            setInsurancePick(null);
        }
    }, [insuranceProducts, insurancePick]);

    const applyRecommended = () => {        if (!travelDatesReady) {
            toast.error("Önce giriş (gidiş) tarihinizi seçin.");
            return;
        }
        if (recommendedInsuranceId) setInsurancePick(recommendedInsuranceId);
        if (recommendedEsimId) {
            setEsimQty({ [recommendedEsimId]: Math.min(Math.max(travelerCount, 1), 10) });
        }
        toast.success("Seyahat sürenize en uygun sigorta ve eSIM paketi eklendi. %10 paket indirimi uygulandı.");
    };

    // Kombinasyon secimi: sadece vize / +eSIM / +sigorta / hepsi
    const applyCombo = (option) => {
        if (option.insurance) {
            const pick = recommendedInsuranceId || insuranceProducts[0]?.id;
            if (pick) setInsurancePick(pick);
        } else {
            setInsurancePick(null);
        }
        if (option.esim) {
            const pick = recommendedEsimId || esimProducts[0]?.id;
            if (pick) setEsimQty({ [pick]: Math.min(Math.max(travelerCount, 1), 10) });
        } else {
            setEsimQty({});
        }
        toast.success(`${option.label} seçildi.`);
    };

    const RecommendedBadge = ({ testId }) => (
        <span
            className="inline-flex items-center gap-1 rounded-full bg-[hsl(var(--brand-green)/0.12)] px-2 py-0.5 text-[11px] font-semibold text-[hsl(var(--brand-green))]"
            data-testid={testId}
        >
            <Star className="h-3 w-3 fill-current" aria-hidden="true" /> Sizin için önerilen
        </span>
    );

    const TravelDatesRequiredNote = ({ testId }) => (
        <div
            className="mt-4 flex items-start gap-2.5 rounded-xl border border-dashed border-primary/40 bg-primary/[0.04] p-4"
            data-testid={testId}
        >
            <CalendarDays className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
            <p className="text-sm leading-6 text-muted-foreground">
                Ürünlerin geçerlilik tarihi seyahatinize göre ayarlanır. Devam etmek için yukarıdan
                <strong className="text-foreground"> giriş (gidiş) tarihinizi</strong> seçin.
            </p>
        </div>
    );

    const storeItems = useMemo(() => {
        const items = [];
        if (insurancePick) {
            items.push({ product_id: insurancePick, quantity: Math.min(Math.max(travelerCount, 1), 10) });
        }
        Object.entries(esimQty).forEach(([pid, qty]) => {
            if (qty > 0) items.push({ product_id: pid, quantity: Math.min(qty, 10) });
        });
        Object.entries(tourQty).forEach(([pid, qty]) => {
            if (qty <= 0) return;
            const plan = tourSchedule[pid] || {};
            if (!plan.date) return; // tarih secilmeden fiyat sorgusu/gonderim yapilmaz
            items.push({
                product_id: pid,
                quantity: Math.min(qty, 10),
                scheduled_date: plan.date,
                scheduled_time: plan.time || null,
            });
        });
        return items.slice(0, 8);
    }, [insurancePick, esimQty, tourQty, tourSchedule, travelerCount]);

    const missingTourDate = useMemo(
        () => Object.entries(tourQty).some(([pid, qty]) => qty > 0 && !(tourSchedule[pid] || {}).date),
        [tourQty, tourSchedule]
    );

    const toggleEsim = (product) => {
        if (!travelDatesReady) {
            toast.error("Önce giriş (gidiş) tarihinizi seçin; eSIM paketiniz bu tarihte başlatılır.");
            return;
        }
        setEsimQty((prev) => {
            const next = { ...prev };
            if (next[product.id]) {
                delete next[product.id];
                return next;
            }
            if (Object.keys(next).length >= 5) {
                toast.error("Tek başvuruda en fazla 5 farklı eSIM paketi seçebilirsiniz.");
                return prev;
            }
            next[product.id] = Math.min(Math.max(travelerCount, 1), 10);
            return next;
        });
    };

    const changeEsimQty = (productId, delta) => {
        setEsimQty((prev) => {
            const current = prev[productId] || 0;
            const value = Math.min(10, current + delta);
            if (value <= 0) {
                const { [productId]: _removed, ...rest } = prev;
                return rest;
            }
            return { ...prev, [productId]: value };
        });
    };

    const changeTourQty = (productId, delta) => {
        setTourQty((prev) => {
            const value = Math.min(10, (prev[productId] || 0) + delta);
            if (value <= 0) {
                const { [productId]: _removed, ...rest } = prev;
                return rest;
            }
            return { ...prev, [productId]: value };
        });
    };

    const toggleTour = (product) => {
        setTourQty((prev) => {
            if (prev[product.id]) {
                const { [product.id]: _removed, ...rest } = prev;
                return rest;
            }
            return { ...prev, [product.id]: Math.min(Math.max(travelerCount, 1), 10) };
        });
        setTourSchedule((prev) => {
            if (prev[product.id]) return prev;
            return {
                ...prev,
                [product.id]: {
                    date: travel.arrival_date || "",
                    time: (product.time_slots || [])[0] || "",
                },
            };
        });
    };

    const setTourPlan = (productId, patch) =>
        setTourSchedule((prev) => ({ ...prev, [productId]: { ...(prev[productId] || {}), ...patch } }));

    const quoteKey = JSON.stringify([selectedVisaIds, addons, storeItems, travel.arrival_date, travel.departure_date]);
    useEffect(() => {
        if (selectedVisaIds.length !== travelers.length || selectedVisaIds.length === 0) {
            setQuote(null);
            return;
        }
        let cancelled = false;
        api.post("/pricing/quote", {
            visa_type_ids: selectedVisaIds,
            addons,
            store_items: storeItems,
            arrival_date: travel.arrival_date || null,
            departure_date: travel.departure_date || null,
        })
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

    const visaById = (id) => visaTypes.find((v) => v.id === id);

    // Kalisi karsilayan en kisa (ve en ucuz) vizeyi bulur; mevcut giris tipini korumaya calisir.
    const pickVisaFor = (days, traveler) => {
        const current = visaById(traveler.visa_type_id);
        const fitting = visaOptionsFor(traveler.applicant_type).filter(
            (v) => Number(v.duration_days) >= days && v.auto_suggest !== false
        );
        const sameEntry = fitting.filter((v) => v.entry_type === (current?.entry_type || "single"));
        const pool = (sameEntry.length ? sameEntry : fitting).slice().sort(
            (a, b) => Number(a.duration_days) - Number(b.duration_days) || Number(a.price) - Number(b.price)
        );
        return pool[0] || null;
    };

    const applyPreCheck = ({ arrival_date, departure_date, passport_expiry, visa, express }) => {
        setTravel((t) => ({ ...t, arrival_date, departure_date }));
        setTravelers((list) =>
            list.map((t) => {
                const match = visa
                    ? pickVisaFor(Number(visa.duration_days) || 0, t) || visa
                    : null;
                return {
                    ...t,
                    passport_expiry: t.passport_expiry || passport_expiry,
                    visa_type_id: t.visa_type_id || match?.id || "",
                };
            })
        );
        setPreCheckDone(true);
        setErrors({});
        if (express) setAddons((a) => ({ ...a, express: true }));
        toast.success(
            express
                ? "Bilgiler forma aktarıldı. Ekspres hizmet ve uygun vize seçildi."
                : "Bilgiler forma aktarıldı. Uygun vize önerisi seçili geldi."
        );
    };

    // Secilen vizeler planlanan kalisi kapsamiyorsa onerilecek vize
    const visaUpgrade = useMemo(() => {
        if (!tripDays) return null;
        const short = travelers.filter((t) => {
            const days = Number(visaById(t.visa_type_id)?.duration_days || 0);
            return days > 0 && tripDays > days;
        });
        if (!short.length) return null;
        const suggestion = pickVisaFor(tripDays, short[0]);
        return suggestion ? { suggestion, count: short.length } : { suggestion: null, count: short.length };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [tripDays, travelers, visaTypes]);

    const applyVisaUpgrade = () => {
        setTravelers((list) =>
            list.map((t) => {
                const days = Number(visaById(t.visa_type_id)?.duration_days || 0);
                if (!days || tripDays <= days) return t;
                const next = pickVisaFor(tripDays, t);
                return next ? { ...t, visa_type_id: next.id } : t;
            })
        );
        setErrors((p) => ({ ...p, stay_length: undefined }));
        toast.success("Vize türleri kalış sürenize göre güncellendi.");
    };

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
                // Kullaniciya sorulmayan, sadece Zami aktarimi icin kullanilan alanlar
                "passport_issue_date",
                "birth_place",
                "passport_issue_place",
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

    // Vesikalik fotografi yapay zeka ile denetler. Sonuc sadece uyari amaclidir,
    // kullanici uygun olmayan fotografla da basvuruya devam edebilir.
    const checkPhotoWithAI = async (key, fileInfo) => {
        if (!fileInfo?.file_id) {
            setPhotoCheck((s) => ({ ...s, [key]: undefined }));
            return;
        }
        if ((fileInfo.content_type || "").includes("pdf")) {
            setPhotoCheck((s) => ({
                ...s,
                [key]: { status: "warn", issues: ["Vesikalık fotoğrafı JPG veya PNG olarak yükleyin."], advice: "" },
            }));
            return;
        }
        setPhotoCheck((s) => ({ ...s, [key]: { status: "loading" } }));
        try {
            const form = new FormData();
            form.append("file_id", fileInfo.file_id);
            const { data } = await api.post("/photo/check", form, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            if (!data?.checked) {
                setPhotoCheck((s) => ({ ...s, [key]: { status: "skipped", message: data?.message || "" } }));
                return;
            }
            if (data.ok) {
                setPhotoCheck((s) => ({ ...s, [key]: { status: "ok", score: data.score } }));
                return;
            }
            setPhotoCheck((s) => ({
                ...s,
                [key]: {
                    status: "warn",
                    isPhoto: data.is_photo !== false,
                    issues: Array.isArray(data.issues) ? data.issues : [],
                    advice: data.advice || "",
                },
            }));
        } catch {
            setPhotoCheck((s) => ({ ...s, [key]: { status: "skipped", message: "" } }));
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
            const hasChild = travelers.some((t) => t.applicant_type === "child");
            const hasAdult = travelers.some((t) => t.applicant_type !== "child");
            if (hasChild && !hasAdult)
                e.travelers_adult =
                    "18 yaş altı yolcular en az bir yetişkinle birlikte başvurmalıdır. Lütfen yolcu ekleyin.";
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
            if (travel.arrival_date && travel.departure_date && !e.departure_date) {
                const stayDays =
                    Math.round(
                        (new Date(travel.departure_date) - new Date(travel.arrival_date)) / 86400000
                    ) + 1;
                const tooShort = travelers.filter((t) => {
                    const days = Number(visaTypes.find((v) => v.id === t.visa_type_id)?.duration_days || 0);
                    return days > 0 && stayDays > days;
                });
                if (tooShort.length)
                    e.stay_length = `Planlanan kalış ${stayDays} gün; seçilen vize bu süreyi kapsamıyor. Daha uzun süreli bir vize seçin veya tarihleri güncelleyin.`;

                const expiryLimit = new Date(travel.departure_date);
                expiryLimit.setMonth(expiryLimit.getMonth() + 6);
                const shortPassports = travelers.filter(
                    (t) => t.passport_expiry && new Date(t.passport_expiry) < expiryLimit
                );
                if (shortPassports.length)
                    e.passport_validity = `Pasaport dönüş tarihinden itibaren en az 6 ay geçerli olmalı: ${shortPassports
                        .map((t) => `${t.first_name} ${t.last_name}`.trim())
                        .join(", ")}`;
            }
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
            const labels = collectErrorLabels(e, travelers);
            const blocking = e.travelers_adult || e.stay_length || e.passport_validity;
            toast.error(
                blocking ||
                    (labels.length
                        ? `Eksik veya hatalı alanlar: ${labels.slice(0, 4).join(", ")}${labels.length > 4 ? "…" : ""}`
                        : "Lütfen işaretli alanları kontrol edin.")
            );
            // ilk hatali alana kaydir ve odakla
            setTimeout(() => {
                const el = document.querySelector('[data-invalid="true"]');
                if (el) {
                    el.scrollIntoView({ behavior: "smooth", block: "center" });
                    const focusable = el.querySelector("input, select, textarea, button");
                    if (focusable) setTimeout(() => focusable.focus({ preventScroll: true }), 350);
                }
            }, 50);
            return false;
        }
        return true;
    }, [step, contact, travelers, travel, extraDocs, visaTypes]);

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
        if (missingTourDate) {
            toast.error("Seçtiğiniz tur için tarih belirlemeniz gerekiyor.");
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
                    passport_issue_date: t.passport_issue_date || "",
                    birth_place: t.birth_place || "",
                    passport_issue_place: t.passport_issue_place || "",
                    marital_status: t.marital_status || "single",
                    profession: t.profession || "",
                    mother_name: (t.mother_name || "").trim(),
                    father_name: (t.father_name || "").trim(),
                    visa_type_id: t.visa_type_id,
                    passport_file_id: t.passportFile.file_id,
                    photo_file_id: t.photoFile.file_id,
                })),
                travel,
                addons,
                store_items: storeItems,
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
                description="Tek formda tüm aileniz için başvurun; indirimler otomatik hesaplanır."
            />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page">
                    {/* STEPPER */}
                    <div
                        className="sticky top-[77px] z-30 overflow-hidden rounded-[var(--radius-lg)] border border-border/70 bg-card/95 backdrop-blur-xl"
                        style={{ boxShadow: "var(--shadow-card)" }}
                        data-testid="wizard-stepper"
                    >
                        <div className="flex items-center gap-2 overflow-x-auto px-4 py-3.5 sm:px-5">
                            {STEPS.map((s, i) => {
                                const Icon = s.icon;
                                const done = i < step;
                                const active = i === step;
                                return (
                                    <div
                                        key={s.key}
                                        className="relative flex min-w-fit items-center gap-2 pb-3"
                                        data-testid={`wizard-step-item-${s.key}`}
                                    >
                                        <span
                                            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border text-[13px] font-bold transition-colors duration-200 ${
                                                done
                                                    ? "border-primary bg-primary text-primary-foreground"
                                                    : active
                                                      ? "border-primary bg-primary/10 text-primary"
                                                      : "border-border bg-card text-muted-foreground"
                                            }`}
                                        >
                                            {done ? <CheckCircle2 className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
                                        </span>
                                        <span className="flex flex-col leading-tight">
                                            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                                                Adım {i + 1}
                                            </span>
                                            <span
                                                className={`whitespace-nowrap text-xs font-bold sm:text-sm ${
                                                    active ? "text-foreground" : "text-muted-foreground"
                                                }`}
                                            >
                                                {s.label}
                                            </span>
                                        </span>
                                        {i < STEPS.length - 1 && (
                                            <span
                                                className={`mx-2 hidden h-0.5 w-8 rounded-full lg:block ${
                                                    done ? "bg-primary/50" : "bg-border"
                                                }`}
                                                aria-hidden="true"
                                            />
                                        )}
                                        {/* adim hizasindaki dolum cizgisi */}
                                        <span
                                            className={`absolute bottom-0 left-0 right-0 h-1.5 rounded-full transition-colors duration-300 ${
                                                done
                                                    ? "bg-primary"
                                                    : active
                                                      ? "bg-primary"
                                                      : "bg-border/50"
                                            }`}
                                            aria-hidden="true"
                                            data-testid={`wizard-step-bar-${s.key}`}
                                        />
                                    </div>
                                );
                            })}
                            {quote ? (
                                <span
                                    className="ml-auto hidden shrink-0 items-center gap-2 rounded-xl border border-border bg-[hsl(var(--cloud))] px-3 py-2 xl:flex"
                                    data-testid="wizard-stepper-total"
                                >
                                    <span className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
                                        Toplam
                                    </span>
                                    <span className="font-heading text-sm font-extrabold">
                                        {formatMoney(quote.total, quote.currency)}
                                    </span>
                                </span>
                            ) : null}
                        </div>
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
                                    <h2 className="font-heading text-xl font-bold">Kişisel bilgiler</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Bilgileri pasaportta yazdığı gibi, Türkçe karakter kullanmadan girin.</p>

                                    {!preCheckDone && (
                                        <div className="mt-6">
                                            <EligibilityPreCheck
                                                visaTypes={visaTypes}
                                                expressAddon={addonMeta.find((a) => a.id === "express") || null}
                                                onApply={applyPreCheck}
                                            />
                                        </div>
                                    )}

                                    <div className="mt-6 rounded-xl border border-border bg-[hsl(var(--cloud))] p-5">
                                        <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">
                                            İletişim bilgileri
                                        </h3>
                                        <div className="mt-4 grid gap-5 sm:grid-cols-2">
                                            <Field label="Ad Soyad" required htmlFor="c-name" error={errors.full_name}>
                                                <Input id="c-name" value={contact.full_name} onChange={setC("full_name")} placeholder="AHMET YILMAZ" data-testid="input-contact-name" />
                                            </Field>
                                            <Field label="E-posta" required htmlFor="c-email" error={errors.email}>
                                                <Input id="c-email" type="email" value={contact.email} onChange={setC("email")} placeholder="ornek@eposta.com" data-testid="input-contact-email" />
                                            </Field>
                                            <Field label="Telefon" required htmlFor="c-phone" error={errors.phone}>
                                                <Input id="c-phone" value={contact.phone} onChange={setC("phone")} placeholder="0555 111 22 33" data-testid="input-contact-phone" />
                                            </Field>
                                        </div>
                                        <label className="mt-4 flex cursor-pointer items-start gap-3 rounded-xl border border-border p-4 text-sm transition-colors duration-200 hover:border-primary/50">
                                            <Switch
                                                checked={!!contact.whatsapp_optin}
                                                onCheckedChange={(c) => setContact((s) => ({ ...s, whatsapp_optin: !!c }))}
                                                data-testid="input-whatsapp-optin"
                                            />
                                            <span className="leading-6 text-muted-foreground">
                                                <strong className="text-foreground">WhatsApp ile bilgilendirilmek istiyorum.</strong>{" "}
                                                Vize sonucunuz çıkınca mesaj gönderelim.
                                            </span>
                                        </label>
                                    </div>

                                    <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
                                        <h3 className="font-heading text-base font-bold">
                                            Yolcular <span className="text-muted-foreground">({travelers.length})</span>
                                        </h3>
                                        <div className="flex flex-wrap gap-2">
                                            <Button type="button" variant="secondary" className="h-10 border border-border" onClick={() => addTraveler("adult")} data-testid="add-adult-traveler-button">
                                                <Plus className="mr-1 h-4 w-4" />
                                                <User className="mr-1.5 h-4 w-4" /> Yetişkin ekle
                                            </Button>
                                            <Button type="button" variant="secondary" className="h-10 border border-border" onClick={() => addTraveler("child")} data-testid="add-child-traveler-button">
                                                <Plus className="mr-1 h-4 w-4" />
                                                <Baby className="mr-1.5 h-4 w-4" /> Çocuk ekle
                                            </Button>
                                        </div>
                                    </div>

                                    {savedTravelers.length > 0 && (
                                        <div
                                            className="mt-5 rounded-xl border border-primary/25 bg-primary/5 p-5"
                                            data-testid="saved-travelers-panel"
                                        >
                                            <div className="flex flex-wrap items-center justify-between gap-2">
                                                <p className="font-heading text-sm font-bold">Kayıtlı yolcularım</p>
                                                <span className="text-xs text-muted-foreground">
                                                    Tek tıkla ekleyin, bilgiler otomatik dolar
                                                </span>
                                            </div>
                                            <div className="mt-3 flex flex-wrap gap-2">
                                                {savedTravelers.map((s) => {
                                                    const added = travelers.some(
                                                        (t) =>
                                                            (s.passport_no && t.passport_no === s.passport_no) ||
                                                            (t.first_name === s.first_name && t.last_name === s.last_name)
                                                    );
                                                    return (
                                                        <Button
                                                            key={s.id}
                                                            type="button"
                                                            variant="secondary"
                                                            className="h-10 border border-border"
                                                            onClick={() => addSavedTraveler(s)}
                                                            disabled={added}
                                                            data-testid={`add-saved-traveler-${s.id}`}
                                                        >
                                                            {added ? (
                                                                <CheckCircle2 className="mr-1.5 h-4 w-4 text-[hsl(var(--success))]" />
                                                            ) : (
                                                                <Plus className="mr-1.5 h-4 w-4" />
                                                            )}
                                                            {s.applicant_type === "child" ? (
                                                                <Baby className="mr-1.5 h-4 w-4" />
                                                            ) : (
                                                                <User className="mr-1.5 h-4 w-4" />
                                                            )}
                                                            {s.first_name} {s.last_name}
                                                        </Button>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}

                                    <div className="mt-5 space-y-6">
                                        {travelers.map((t, idx) => {
                                            const te = errors[t.key] || {};
                                            const passportRead = ocr[t.key]?.status === "done";
                                            // Cinsiyet artik formda sorulmuyor; pasaport MRZ'sinden okunur.
                                            const passportComplete =
                                                !!t.first_name && !!t.last_name && !!t.birth_date && !!t.passport_no && !!t.passport_expiry;
                                            // OCR bilgileri eksiksiz doldurduysa alanlari ozet karta cevir;
                                            // hata varsa veya kullanici "Duzenle"ye bastiysa formu geri ac.
                                            const passportSummaryVisible =
                                                passportRead && passportComplete && !fieldsOpen[t.key] && Object.keys(te).length === 0;
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
                                                                        onClick={() =>
                                                                            updateTraveler(t.key, {
                                                                                applicant_type: opt.v,
                                                                                visa_type_id: "",
                                                                                ...(opt.v === "child"
                                                                                    ? { marital_status: "single", profession: "Student" }
                                                                                    : {}),
                                                                            })
                                                                        }
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

                                                    <div className="mt-5 rounded-xl border border-primary/35 bg-primary/[0.05] p-4" data-testid={`traveler-${idx}-ai-passport-box`}>
                                                        <p className="flex items-center gap-2 font-heading text-base font-bold">
                                                            <ScanLine className="h-4.5 w-4.5 text-primary" aria-hidden="true" />
                                                            Pasaportu yükleyin, gerisini biz dolduralım
                                                        </p>
                                                        <p className="mt-1 text-xs leading-5 text-muted-foreground">
                                                            Tek fotoğraf yeter; ad, soyad, tarih ve pasaport no otomatik dolar.</p>
                                                        <div className="mt-3">
                                                            <FileDropzone
                                                                label="Pasaport kimlik sayfası"
                                                                hint=""
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
                                                                Pasaport bilgileri okunuyor...
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

                                                    {passportSummaryVisible ? (
                                                        <div
                                                            className="mt-5 rounded-xl border border-[hsl(var(--brand-green)/0.30)] bg-[hsl(var(--brand-green)/0.06)] p-4"
                                                            data-testid={`traveler-${idx}-passport-summary`}
                                                        >
                                                            <div className="flex flex-wrap items-start justify-between gap-3">
                                                                <p className="flex items-center gap-2 text-sm font-bold text-[hsl(var(--brand-green))]">
                                                                    <CheckCircle2 className="h-4 w-4" /> Pasaporttan okundu
                                                                </p>
                                                                <button
                                                                    type="button"
                                                                    onClick={() => setFieldsOpen((o) => ({ ...o, [t.key]: true }))}
                                                                    className="inline-flex min-h-[36px] items-center gap-1.5 rounded-lg border border-border bg-card px-3 text-xs font-bold text-foreground transition-colors duration-150 hover:bg-muted focus-visible:outline-none"
                                                                    data-testid={`traveler-${idx}-edit-fields`}
                                                                >
                                                                    <Pencil className="h-3.5 w-3.5" /> Düzenle
                                                                </button>
                                                            </div>
                                                            <dl className="mt-3 grid gap-x-6 gap-y-2 sm:grid-cols-2">
                                                                {[
                                                                    ["Ad Soyad", `${t.first_name} ${t.last_name}`],
                                                                    ["Doğum Tarihi", formatDate(t.birth_date)],
                                                                    ["Pasaport No", t.passport_no],
                                                                    ["Geçerlilik Tarihi", formatDate(t.passport_expiry)],
                                                                    ...(t.national_id ? [["T.C. kimlik no", t.national_id]] : []),
                                                                ].map(([label, value]) => (
                                                                    <div key={label} className="flex items-baseline justify-between gap-3 border-b border-border/60 pb-1.5">
                                                                        <dt className="text-xs text-muted-foreground">{label}</dt>
                                                                        <dd className="text-xs font-bold">{value}</dd>
                                                                    </div>
                                                                ))}
                                                            </dl>
                                                            <p className="mt-3 text-[11px] leading-5 text-muted-foreground">
                                                                Bilgiler pasaportunuzdan okundu. Hatalı bir şey görürseniz "Düzenle"ye
                                                                dokunun.
                                                            </p>
                                                        </div>
                                                    ) : (
                                                    <div className="mt-5 grid gap-5 sm:grid-cols-2">
                                                        <Field label="Ad" required error={te.first_name}>
                                                            <Input value={t.first_name} onChange={(e) => updateTraveler(t.key, { first_name: e.target.value })} placeholder="AHMET" data-testid={`traveler-${idx}-first-name`} />
                                                        </Field>
                                                        <Field label="Soyad" required error={te.last_name}>
                                                            <Input value={t.last_name} onChange={(e) => updateTraveler(t.key, { last_name: e.target.value })} placeholder="YILMAZ" data-testid={`traveler-${idx}-last-name`} />
                                                        </Field>
                                                        <Field label="Doğum Tarihi" required error={te.birth_date}>
                                                            <DateField
                                                                value={t.birth_date}
                                                                onChange={(iso) => updateTraveler(t.key, { birth_date: iso })}
                                                                maxDate={new Date()}
                                                                fromYear={new Date().getFullYear() - 100}
                                                                toYear={new Date().getFullYear()}
                                                                invalid={!!te.birth_date}
                                                                data-testid={`traveler-${idx}-birth-date`}
                                                            />
                                                        </Field>
                                                        <Field label="Pasaport No" required error={te.passport_no}>
                                                            <Input value={t.passport_no} onChange={(e) => updateTraveler(t.key, { passport_no: e.target.value })} placeholder="U12345678" data-testid={`traveler-${idx}-passport-no`} />
                                                        </Field>
                                                        <Field label="Geçerlilik Tarihi" required error={te.passport_expiry}>
                                                            <DateField
                                                                value={t.passport_expiry}
                                                                onChange={(iso) => updateTraveler(t.key, { passport_expiry: iso })}
                                                                minDate={new Date()}
                                                                fromYear={new Date().getFullYear()}
                                                                toYear={new Date().getFullYear() + 15}
                                                                invalid={!!te.passport_expiry}
                                                                data-testid={`traveler-${idx}-passport-expiry`}
                                                            />
                                                        </Field>
                                                        {t.national_id || openNationalId[t.key] ? (
                                                            <Field label="T.C. Kimlik No">
                                                                <Input value={t.national_id} onChange={(e) => updateTraveler(t.key, { national_id: e.target.value })} placeholder="11 hane" data-testid={`traveler-${idx}-national-id`} />
                                                            </Field>
                                                        ) : (
                                                            <div className="flex items-end">
                                                                <button
                                                                    type="button"
                                                                    onClick={() => setOpenNationalId((s) => ({ ...s, [t.key]: true }))}
                                                                    className="inline-flex min-h-[44px] items-center gap-1.5 text-sm font-semibold text-primary underline-offset-4 hover:underline focus-visible:outline-none"
                                                                    data-testid={`traveler-${idx}-add-national-id`}
                                                                >
                                                                    <Plus className="h-3.5 w-3.5" /> T.C. kimlik no ekle (isteğe bağlı)
                                                                </button>
                                                            </div>
                                                        )}
                                                    </div>
                                                    )}

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
                                    <h2 className="font-heading text-xl font-bold">Vize ve tarihler</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Vize türünü ve seyahat tarihlerinizi seçin.
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
                                        <Field label="Gidiş Tarihi" required error={errors.arrival_date}>
                                            <DateField
                                                value={travel.arrival_date}
                                                onChange={(iso) => setTravel((t) => ({ ...t, arrival_date: iso }))}
                                                minDate={new Date()}
                                                fromYear={new Date().getFullYear()}
                                                toYear={new Date().getFullYear() + 3}
                                                invalid={!!errors.arrival_date}
                                                data-testid="input-arrival-date"
                                            />
                                        </Field>
                                        <Field label="Dönüş Tarihi" required error={errors.departure_date}>
                                            <DateField
                                                value={travel.departure_date}
                                                onChange={(iso) => setTravel((t) => ({ ...t, departure_date: iso }))}
                                                minDate={fromISODate(travel.arrival_date) || new Date()}
                                                fromYear={new Date().getFullYear()}
                                                toYear={new Date().getFullYear() + 3}
                                                invalid={!!errors.departure_date}
                                                data-testid="input-departure-date"
                                            />
                                        </Field>
                                    </div>

                                    {visaUpgrade && (
                                        <div
                                            className="mt-6 flex flex-col gap-3 rounded-xl border border-primary/30 bg-primary/5 p-4 sm:flex-row sm:items-center sm:justify-between"
                                            data-testid="visa-upgrade-suggestion"
                                        >
                                            <p className="text-sm leading-6">
                                                <strong>Planlanan kalış {tripDays} gün.</strong>{" "}
                                                {visaUpgrade.suggestion
                                                    ? `Bu süre için ${visaUpgrade.suggestion.duration_days} günlük vize gerekiyor (${formatMoney(
                                                          visaUpgrade.suggestion.price,
                                                          visaUpgrade.suggestion.currency
                                                      )} / kişi başı).`
                                                    : "60 günden uzun kalışlarda 60 günlük vize ile giriş yapıp Dubai'deyken uzatma yapılması gerekir; danışmanımız yönlendirir."}
                                            </p>
                                            {visaUpgrade.suggestion && (
                                                <Button
                                                    type="button"
                                                    className="h-10 shrink-0"
                                                    onClick={applyVisaUpgrade}
                                                    data-testid="visa-upgrade-apply-button"
                                                >
                                                    {visaUpgrade.suggestion.duration_days} günlük vizeye geç
                                                </Button>
                                            )}
                                        </div>
                                    )}

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
                                        <p className="mt-1.5 text-sm text-muted-foreground">Yolcu başına eklenir.</p>
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
                                    <h2 className="font-heading text-xl font-bold">Evraklar</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Pasaport ve vesikalık zorunlu. Belgeleriniz şifreli saklanır.</p>

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
                                                                hint="Zorunlu · Bilgiler otomatik dolar"
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
                                                                    Pasaport bilgileri okunuyor...
                                                                </p>
                                                            )}
                                                            {ocr[t.key]?.status === "done" && (
                                                                <div className="mt-2 rounded-lg border border-[hsl(var(--brand-green)/0.30)] bg-[hsl(var(--brand-green)/0.07)] p-3" data-testid={`traveler-${idx}-docs-ocr-success`}>
                                                                    <p className="flex items-center gap-2 text-xs font-semibold text-[hsl(var(--brand-green))]">
                                                                        <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
                                                                        Pasaport okundu: {ocr[t.key].name} {ocr[t.key].passport_no ? `· ${ocr[t.key].passport_no}` : ""}
                                                                    </p>
                                                                    <p className="mt-1 text-xs text-muted-foreground">
                                                                        Boş alanlar dolduruldu, kontrol edin.
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
                                                                hint="Zorunlu · Otomatik kontrol edilir"
                                                                docType="photo"
                                                                value={t.photoFile}
                                                                onChange={(f) => {
                                                                    updateTraveler(t.key, { photoFile: f });
                                                                    checkPhotoWithAI(t.key, f);
                                                                }}
                                                                testId={`traveler-${idx}-photo-upload-input`}
                                                            />
                                                            {photoCheck[t.key]?.status === "loading" && (
                                                                <p
                                                                    className="mt-2 flex items-center gap-2 text-xs font-medium text-primary"
                                                                    data-testid={`traveler-${idx}-photo-check-loading`}
                                                                >
                                                                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                                                                    Fotoğraf kontrol ediliyor...
                                                                </p>
                                                            )}
                                                            {photoCheck[t.key]?.status === "ok" && (
                                                                <p
                                                                    className="mt-2 flex items-center gap-2 text-xs font-semibold text-[hsl(var(--brand-green))]"
                                                                    data-testid={`traveler-${idx}-photo-check-ok`}
                                                                >
                                                                    <CheckCircle2 className="h-3.5 w-3.5" />
                                                                    Fotoğraf vize standartlarına uygun görünüyor.
                                                                </p>
                                                            )}
                                                            {photoCheck[t.key]?.status === "warn" && (
                                                                <div
                                                                    className="mt-2 rounded-lg border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.08)] p-3"
                                                                    data-testid={`traveler-${idx}-photo-check-warning`}
                                                                >
                                                                    <p className="flex items-center gap-2 text-xs font-bold text-foreground">
                                                                        <AlertCircle className="h-3.5 w-3.5 text-[hsl(var(--status-warning))]" />
                                                                        {photoCheck[t.key].isPhoto === false
                                                                            ? "Bu görüntü vesikalık fotoğraf gibi görünmüyor"
                                                                            : "Fotoğrafta düzeltilmesi önerilen noktalar var"}
                                                                    </p>
                                                                    {photoCheck[t.key].issues?.length > 0 && (
                                                                        <ul className="mt-2 space-y-1 pl-1">
                                                                            {photoCheck[t.key].issues.map((issue, i) => (
                                                                                <li key={i} className="text-xs leading-5 text-muted-foreground">
                                                                                    • {issue}
                                                                                </li>
                                                                            ))}
                                                                        </ul>
                                                                    )}
                                                                    {photoCheck[t.key].advice && (
                                                                        <p className="mt-2 text-xs leading-5 text-muted-foreground">
                                                                            {photoCheck[t.key].advice}
                                                                        </p>
                                                                    )}
                                                                    <p className="mt-2 text-xs text-muted-foreground">
                                                                        Yine de bu fotoğrafla devam edebilirsiniz.
                                                                    </p>
                                                                </div>
                                                            )}
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
                                            <p className="font-heading text-sm font-bold">Seyahat belgeleri (opsiyonel)</p>
                                            <p className="mt-1.5 text-xs leading-5 text-muted-foreground">
                                                Bu alanlar zorunlu değil: vizeniz çıkmadan uçak bileti veya otel
                                                rezervasyonu yapmanıza gerek yok. Elinizde varsa yükleyin, yoksa
                                                boş bırakıp devam edin.
                                            </p>
                                            <div className="mt-5 grid gap-6 md:grid-cols-3">
                                                <div>
                                                    <FileDropzone label="Dönüş Uçak Bileti" hint="Opsiyonel" docType="ticket" value={extraDocs.ticket} onChange={(f) => setExtraDocs((s) => ({ ...s, ticket: f }))} testId="ticket-upload-input" />
                                                    {errors.ticket && (
                                                        <p className="mt-2 flex items-start gap-1.5 text-xs font-medium text-destructive" data-testid="ticket-upload-error">
                                                            <AlertCircle className="mt-0.5 h-3.5 w-3.5" /> {errors.ticket}
                                                        </p>
                                                    )}
                                                </div>
                                                <div>
                                                    <FileDropzone label="Otel Rezervasyonu" hint="Opsiyonel" docType="hotel" value={extraDocs.hotel} onChange={(f) => setExtraDocs((s) => ({ ...s, hotel: f }))} testId="hotel-upload-input" />
                                                    {errors.hotel && (
                                                        <p className="mt-2 flex items-start gap-1.5 text-xs font-medium text-destructive" data-testid="hotel-upload-error">
                                                            <AlertCircle className="mt-0.5 h-3.5 w-3.5" /> {errors.hotel}
                                                        </p>
                                                    )}
                                                </div>
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
                                    <h2 className="font-heading text-xl font-bold">Özet ve ödeme</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Bilgilerinizi kontrol edip ödemeye geçin.</p>

                                    {/* NE ALMAK ISTIYORSUNUZ (kombinasyonlar) */}
                                    <ComboSelector
                                        hasInsurance={Boolean(insurancePick)}
                                        hasEsim={Object.values(esimQty).some((q) => q > 0)}
                                        onChange={applyCombo}
                                    />

                                    {/* AKILLI PAKET ONERISI + PAKET INDIRIMI */}
                                    {(insuranceProducts.length > 0 || esimProducts.length > 0) && (
                                        <div
                                            className="mt-10 rounded-xl border border-[hsl(var(--brand-green)/0.35)] bg-[hsl(var(--brand-green)/0.06)] p-5"
                                            data-testid="bundle-promo-box"
                                        >
                                            <div className="flex flex-wrap items-start justify-between gap-4">
                                                <div className="max-w-xl">
                                                    <p className="flex items-center gap-2 font-heading text-sm font-bold">
                                                        <Tag className="h-4 w-4 text-[hsl(var(--brand-green))]" aria-hidden="true" />
                                                        {bundleInfo?.title || "Seyahat paketi indirimi"}
                                                    </p>
                                                    <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                                                        {bundleInfo?.note ||
                                                            "Sigorta ve eSIM'i birlikte alın, %10 indirim otomatik uygulanır."}
                                                    </p>
                                                    {tripDays && (
                                                        <p className="mt-2 text-sm text-muted-foreground" data-testid="bundle-trip-days">
                                                            Seyahatiniz <strong className="text-foreground">{tripDays} gün</strong> — size uygun paketleri işaretledik.
                                                        </p>
                                                    )}
                                                    {quote?.bundle_discount > 0 && (
                                                        <p
                                                            className="mt-2 flex items-center gap-1.5 text-sm font-semibold text-[hsl(var(--brand-green))]"
                                                            data-testid="bundle-discount-applied"
                                                        >
                                                            <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
                                                            Paket indirimi uygulandı: - {formatMoney(quote.bundle_discount, quote.currency)}
                                                        </p>
                                                    )}
                                                </div>
                                                <Button
                                                    type="button"
                                                    variant="secondary"
                                                    className="h-10 border border-border"
                                                    onClick={applyRecommended}
                                                    disabled={!travelDatesReady || bundleActive}
                                                    data-testid="apply-recommended-bundle-button"
                                                >
                                                    <Plus className="mr-2 h-4 w-4" aria-hidden="true" />
                                                    {bundleActive ? "Paket eklendi" : "Önerilenleri ekle"}
                                                </Button>
                                            </div>
                                        </div>
                                    )}

                                    {/* VIZE SURESINE GORE HAZIR PAKETLER */}
                                    <BundlePicker
                                        bundles={bundles}
                                        selectedId={selectedBundleId}
                                        onSelect={pickBundle}
                                        visaDays={visaCoverDays}
                                    />

                                    {/* SEYAHAT SIGORTASI (magaza katalogu) */}
                                    {insuranceProducts.length > 0 && (
                                        <div className="mt-10" data-testid="apply-insurance-section">
                                            <div className="flex items-center gap-2">
                                                <ShieldCheck className="h-5 w-5 text-primary" />
                                                <h3 className="font-heading text-base font-bold">Seyahat sağlık sigortası</h3>
                                            </div>
                                            <p className="mt-1.5 text-sm text-muted-foreground">
                                                Poliçe yolcu başına hesaplanır ve <strong className="text-foreground">gidiş tarihinizde</strong> başlar; PDF olarak e-postanıza gelir.</p>
                                            {!travelDatesReady && <TravelDatesRequiredNote testId="insurance-dates-required" />}
                                            <div className="mt-4 grid gap-4 md:grid-cols-2">
                                                {insuranceProducts.map((p) => {
                                                    const selected = insurancePick === p.id;
                                                    return (
                                                        <button
                                                            type="button"
                                                            key={p.id}
                                                            aria-pressed={selected}
                                                            disabled={!travelDatesReady}
                                                            onClick={() => setInsurancePick(selected ? null : p.id)}
                                                            className={`rounded-xl border p-5 text-left transition-colors duration-200 hover:border-primary/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-60 ${
                                                                selected ? "border-primary bg-primary/5" : "border-border bg-card"
                                                            }`}
                                                            data-testid={`insurance-option-${p.id}`}
                                                        >
                                                            <div className="flex items-start justify-between gap-3">
                                                                <div>
                                                                    <p className="font-heading text-sm font-bold">{p.name}</p>
                                                                    {p.coverage && (
                                                                        <p className="mt-1 text-xs font-semibold text-muted-foreground">{p.coverage}</p>
                                                                    )}
                                                                    {recommendedInsuranceId === p.id && (
                                                                        <div className="mt-2">
                                                                            <RecommendedBadge testId={`insurance-recommended-${p.id}`} />
                                                                        </div>
                                                                    )}
                                                                </div>
                                                                {selected ? (
                                                                    <CheckCircle2 className="h-5 w-5 shrink-0 text-primary" />
                                                                ) : (
                                                                    <span className="mt-0.5 h-5 w-5 shrink-0 rounded-full border border-border" aria-hidden="true" />
                                                                )}
                                                            </div>
                                                            <p className="mt-2 text-sm leading-6 text-muted-foreground">{p.summary}</p>
                                                            <DateWindowNote product={p} testId={`insurance-dates-${p.id}`} />
                                                            <p className="mt-3 font-heading text-sm font-bold text-primary">
                                                                + {formatMoney(p.price, p.currency)} / kişi
                                                            </p>
                                                        </button>
                                                    );
                                                })}
                                            </div>
                                            {insurancePick && (
                                                <p className="mt-3 text-sm text-muted-foreground" data-testid="insurance-selected-note">
                                                    {travelerCount} yolcu için poliçe eklendi
                                                    {travel.arrival_date ? ` · ${formatDate(travel.arrival_date)} tarihinde başlar` : ""}.
                                                    Toplam sepetinizde otomatik hesaplanır.
                                                </p>
                                            )}
                                        </div>
                                    )}

                                    {/* DUBAI eSIM (magaza katalogu) */}
                                    {esimProducts.length > 0 && (
                                        <div className="mt-10" data-testid="apply-esim-section">
                                            <div className="flex items-center gap-2">
                                                <Wifi className="h-5 w-5 text-primary" />
                                                <h3 className="font-heading text-base font-bold">Dubai eSIM (internet paketi)</h3>
                                            </div>
                                            <p className="mt-1.5 text-sm text-muted-foreground">
                                                Paketiniz <strong className="text-foreground">gidiş tarihinizde</strong> başlar; QR kodunuz e-postanıza gelir.</p>
                                            {!travelDatesReady && <TravelDatesRequiredNote testId="esim-dates-required" />}
                                            <div className="mt-4 space-y-4">
                                                {esimProducts.map((p) => {
                                                    const qty = esimQty[p.id] || 0;
                                                    const selected = qty > 0;
                                                    return (
                                                        <div
                                                            key={p.id}
                                                            className={`rounded-xl border p-5 transition-colors duration-200 ${
                                                                selected ? "border-primary bg-primary/5" : "border-border bg-card"
                                                            }`}
                                                            data-testid={`esim-option-${p.id}`}
                                                        >
                                                            <div className="flex flex-wrap items-start gap-4">
                                                                <Switch
                                                                    checked={selected}
                                                                    disabled={!travelDatesReady}
                                                                    onCheckedChange={() => toggleEsim(p)}
                                                                    className="mt-1"
                                                                    data-testid={`esim-switch-${p.id}`}
                                                                />
                                                                <div className="min-w-[200px] flex-1">
                                                                    <div className="flex flex-wrap items-center gap-2">
                                                                        <p className="font-heading text-sm font-bold">{p.name}</p>
                                                                        {p.popular && (
                                                                            <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary">
                                                                                En çok tercih edilen
                                                                            </span>
                                                                        )}
                                                                        {recommendedEsimId === p.id && (
                                                                            <RecommendedBadge testId={`esim-recommended-${p.id}`} />
                                                                        )}
                                                                    </div>
                                                                    <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{p.summary}</p>
                                                                    <DateWindowNote product={p} testId={`esim-dates-${p.id}`} />
                                                                    <p className="mt-2 flex items-center gap-1.5 text-sm font-semibold text-primary">
                                                                        <Signal className="h-4 w-4" aria-hidden="true" />
                                                                        + {formatMoney(p.price, p.currency)} / adet
                                                                    </p>
                                                                </div>
                                                                {selected && (
                                                                    <div className="flex items-center gap-2" data-testid={`esim-qty-${p.id}`}>
                                                                        <Button
                                                                            type="button"
                                                                            variant="outline"
                                                                            size="icon"
                                                                            onClick={() => changeEsimQty(p.id, -1)}
                                                                            disabled={qty <= 1}
                                                                            aria-label="Adet azalt"
                                                                            data-testid={`esim-qty-minus-${p.id}`}
                                                                        >
                                                                            <Minus className="h-4 w-4" />
                                                                        </Button>
                                                                        <span className="w-9 text-center font-heading text-sm font-bold" data-testid={`esim-qty-value-${p.id}`}>
                                                                            {qty}
                                                                        </span>
                                                                        <Button
                                                                            type="button"
                                                                            variant="outline"
                                                                            size="icon"
                                                                            onClick={() => changeEsimQty(p.id, 1)}
                                                                            disabled={qty >= 10}
                                                                            aria-label="Adet arttır"
                                                                            data-testid={`esim-qty-plus-${p.id}`}
                                                                        >
                                                                            <Plus className="h-4 w-4" />
                                                                        </Button>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}

                                    {/* DUBAI AKTIVITELERI (col safarisi) */}
                                    {tourProducts.length > 0 && (
                                        <div className="mt-10" data-testid="apply-tour-section">
                                            <div className="flex items-center gap-2">
                                                <Sparkles className="h-5 w-5 text-primary" />
                                                <h3 className="font-heading text-base font-bold">Dubai'de yapacaklarınız</h3>
                                            </div>
                                            <p className="mt-1.5 text-sm text-muted-foreground">
                                                Yerinizi şimdiden ayırtın: tur tarihinizi ve otelden alış saatinizi
                                                buradan seçin, rezervasyonunuz bu bilgilerle oluşturulur.
                                            </p>
                                            <div className="mt-4 space-y-4">
                                                {tourProducts.map((p) => {
                                                    const qty = tourQty[p.id] || 0;
                                                    const selected = qty > 0;
                                                    return (
                                                        <div
                                                            key={p.id}
                                                            className={`rounded-xl border p-5 transition-colors duration-200 ${
                                                                selected ? "border-primary bg-primary/5" : "border-border bg-card"
                                                            }`}
                                                            data-testid={`tour-option-${p.id}`}
                                                        >
                                                            {p.image_url && (
                                                                <div className="mb-4 overflow-hidden rounded-lg">
                                                                    <img
                                                                        src={p.image_url}
                                                                        alt={p.name}
                                                                        loading="lazy"
                                                                        className="h-40 w-full object-cover transition-transform duration-500 hover:scale-105 sm:h-48"
                                                                        data-testid={`tour-image-${p.id}`}
                                                                    />
                                                                </div>
                                                            )}
                                                            <div className="flex flex-wrap items-start gap-4">
                                                                <Switch
                                                                    checked={selected}
                                                                    onCheckedChange={() => toggleTour(p)}
                                                                    className="mt-1"
                                                                    data-testid={`tour-switch-${p.id}`}
                                                                />
                                                                <div className="min-w-[200px] flex-1">
                                                                    <p className="font-heading text-sm font-bold">{p.name}</p>
                                                                    <p className="mt-1.5 text-sm leading-6 text-muted-foreground">
                                                                        {p.summary}
                                                                    </p>
                                                                    <ul className="mt-2 space-y-1">
                                                                        {(p.features || []).slice(0, 3).map((f) => (
                                                                            <li key={f} className="flex items-start gap-2 text-xs leading-5 text-muted-foreground">
                                                                                <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                                                                                {f}
                                                                            </li>
                                                                        ))}
                                                                    </ul>
                                                                    <p className="mt-2 text-sm font-semibold text-primary">
                                                                        + {formatMoney(p.price, p.currency)} / kişi
                                                                    </p>
                                                                </div>
                                                                {selected && (
                                                                    <div className="flex items-center gap-2" data-testid={`tour-qty-${p.id}`}>
                                                                        <Button
                                                                            type="button"
                                                                            variant="outline"
                                                                            size="icon"
                                                                            onClick={() => changeTourQty(p.id, -1)}
                                                                            disabled={qty <= 1}
                                                                            aria-label="Kişi sayısını azalt"
                                                                            data-testid={`tour-qty-minus-${p.id}`}
                                                                        >
                                                                            <Minus className="h-4 w-4" />
                                                                        </Button>
                                                                        <span
                                                                            className="w-9 text-center font-heading text-sm font-bold"
                                                                            data-testid={`tour-qty-value-${p.id}`}
                                                                        >
                                                                            {qty}
                                                                        </span>
                                                                        <Button
                                                                            type="button"
                                                                            variant="outline"
                                                                            size="icon"
                                                                            onClick={() => changeTourQty(p.id, 1)}
                                                                            disabled={qty >= 10}
                                                                            aria-label="Kişi sayısını arttır"
                                                                            data-testid={`tour-qty-plus-${p.id}`}
                                                                        >
                                                                            <Plus className="h-4 w-4" />
                                                                        </Button>
                                                                    </div>
                                                                )}
                                                            </div>

                                                            {selected && (
                                                                <div
                                                                    className="mt-5 grid gap-4 border-t border-border/70 pt-4 sm:grid-cols-2"
                                                                    data-testid={`tour-schedule-${p.id}`}
                                                                >
                                                                    <div className="space-y-2">
                                                                        <Label htmlFor={`tour-date-${p.id}`}>Tur tarihi</Label>
                                                                        <DateField
                                                                            id={`tour-date-${p.id}`}
                                                                            value={(tourSchedule[p.id] || {}).date || ""}
                                                                            onChange={(iso) => setTourPlan(p.id, { date: iso })}
                                                                            minDate={fromISODate(travel.arrival_date) || new Date()}
                                                                            maxDate={fromISODate(travel.departure_date) || undefined}
                                                                            fromYear={new Date().getFullYear()}
                                                                            toYear={new Date().getFullYear() + 2}
                                                                            data-testid={`tour-date-input-${p.id}`}
                                                                        />
                                                                        {!(tourSchedule[p.id] || {}).date && (
                                                                            <p
                                                                                className="text-xs font-medium text-destructive"
                                                                                data-testid={`tour-date-error-${p.id}`}
                                                                            >
                                                                                Devam etmek için tur tarihini seçin.
                                                                            </p>
                                                                        )}
                                                                    </div>
                                                                    <div className="space-y-2">
                                                                        <Label>Otelden alış saati</Label>
                                                                        <div className="flex flex-wrap gap-2">
                                                                            {(p.time_slots || []).map((slot) => {
                                                                                const active = (tourSchedule[p.id] || {}).time === slot;
                                                                                return (
                                                                                    <button
                                                                                        key={slot}
                                                                                        type="button"
                                                                                        onClick={() => setTourPlan(p.id, { time: slot })}
                                                                                        className={`rounded-full border px-3.5 py-1.5 text-xs font-semibold transition-colors duration-200 ${
                                                                                            active
                                                                                                ? "border-primary bg-primary text-primary-foreground"
                                                                                                : "border-border bg-background hover:border-primary/60"
                                                                                        }`}
                                                                                        data-testid={`tour-time-${p.id}-${slot.replace(":", "")}`}
                                                                                    >
                                                                                        {slot}
                                                                                    </button>
                                                                                );
                                                                            })}
                                                                        </div>
                                                                        <p className="text-xs text-muted-foreground">
                                                                            Tur yaklaşık 7 saat sürer; dönüş gece 21:30–22:00 civarındadır.
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}

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
                                                    {(quote.store_items || []).map((s) => (
                                                        <SummaryRow
                                                            key={s.product_id}
                                                            label={`${s.name} x${s.quantity}${
                                                                s.scheduled_date
                                                                    ? ` · ${formatDate(s.scheduled_date)}${s.scheduled_time ? ` ${s.scheduled_time}` : ""}`
                                                                    : s.starts_on
                                                                    ? ` · ${formatDate(s.starts_on)}${s.ends_on ? ` – ${formatDate(s.ends_on)}` : ""}`
                                                                    : ""
                                                            }`}
                                                            value={formatMoney(s.total, quote.currency)}
                                                        />
                                                    ))}
                                                    {quote.bundle_discount > 0 && (
                                                        <SummaryRow
                                                            label={`${quote.bundle_discount_title || "Seyahat paketi indirimi"} (%${Math.round((quote.bundle_discount_rate || 0) * 100)})`}
                                                            value={`- ${formatMoney(quote.bundle_discount, quote.currency)}`}
                                                        />
                                                    )}
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

                                        {payMethod === "transfer" && !transferInfo && (
                                            <BankTransferInfo
                                                bank={bankInfo}
                                                agencyItems={agencyItems}
                                                amount={quote ? formatMoney(quote.total, quote.currency) : ""}
                                            />
                                        )}

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
                                                        <dd className="text-right font-bold text-[hsl(var(--brand-copper))]">
                                                            {formatMoney(transferInfo.amount, transferInfo.currency)}
                                                        </dd>
                                                    </div>
                                                </dl>
                                                <p className="mt-3 text-xs leading-5 text-muted-foreground">{transferInfo.bank?.note}</p>
                                                <Button asChild variant="secondary" className="mt-4 h-10 border border-border">
                                                    <a href={waLink(siteContact, `Merhaba, ${transferInfo.reference_code} numaralı başvurumun havale dekontunu göndermek istiyorum.`)} target="_blank" rel="noreferrer" data-testid="send-receipt-whatsapp">
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

                                <div className="flex flex-wrap items-center gap-3">
                                    <Button
                                        type="button"
                                        variant="secondary"
                                        className="h-11 border border-border"
                                        onClick={saveDraft}
                                        disabled={savingDraft}
                                        data-testid="wizard-save-draft-button"
                                    >
                                        {savingDraft ? (
                                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Kaydediliyor…</>
                                        ) : (
                                            <><Save className="mr-2 h-4 w-4" /> Kaydet, sonra devam et</>
                                        )}
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
                            </div>
                        </motion.div>

                        {/* SIDEBAR */}
                        <aside className="space-y-5 lg:sticky lg:top-[172px] lg:self-start">
                            <div className="card-surface p-5" data-testid="wizard-order-summary">
                                <div className="flex items-center justify-between gap-3">
                                    <h3 className="font-heading text-base font-bold">Başvuru özeti</h3>
                                    <span className="rounded-md bg-[hsl(var(--sand-surface))] px-2 py-1 text-[11px] font-bold text-primary">
                                        {travelers.length} yolcu
                                    </span>
                                </div>
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
                                        {(quote.store_items || []).map((s) => (
                                            <div key={s.product_id} className="flex justify-between gap-3" data-testid={`summary-store-line-${s.product_id}`}>
                                                <span className="text-muted-foreground">
                                                    {s.name} x{s.quantity}
                                                    {s.scheduled_date ? (
                                                        <span className="block text-xs" data-testid={`summary-store-schedule-${s.product_id}`}>
                                                            {formatDate(s.scheduled_date)}
                                                            {s.scheduled_time ? ` · ${s.scheduled_time}` : ""}
                                                        </span>
                                                    ) : (
                                                        s.starts_on && (
                                                            <span className="block text-xs">
                                                                {formatDate(s.starts_on)}
                                                                {s.ends_on ? ` – ${formatDate(s.ends_on)}` : " itibaren"}
                                                            </span>
                                                        )
                                                    )}
                                                </span>
                                                <span className="font-semibold">{formatMoney(s.total, quote.currency)}</span>
                                            </div>
                                        ))}
                                        {quote.bundle_discount > 0 && (
                                            <div className="flex justify-between text-[hsl(var(--brand-green))]" data-testid="summary-bundle-discount">
                                                <span>Paket indirimi (%{Math.round((quote.bundle_discount_rate || 0) * 100)})</span>
                                                <span className="font-semibold">- {formatMoney(quote.bundle_discount, quote.currency)}</span>
                                            </div>
                                        )}
                                        <div className="flex items-end justify-between border-t border-border pt-3">
                                            <span className="text-sm font-semibold">Toplam</span>
                                            <span className="font-heading text-2xl font-bold" data-testid="summary-total-price">
                                                {formatMoney(quote.total, quote.currency)}
                                            </span>
                                        </div>
                                        <div className="pt-1">
                                            <FxNote variant="inline" />
                                        </div>
                                    </div>
                                ) : (
                                    <p className="mt-4 border-t border-border pt-4 text-sm text-muted-foreground">
                                        Fiyat için vize türü seçin.
                                    </p>
                                )}
                            </div>

                            <ExtrasQuickAdd
                                insuranceProducts={insuranceProducts}
                                esimProducts={esimProducts}
                                insurancePick={insurancePick}
                                onPickInsurance={setInsurancePick}
                                esimQty={esimQty}
                                onChangeEsimQty={changeEsimQty}
                            />

                            <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-5">
                                <div className="flex items-center gap-2">
                                    <ShieldCheck className="h-4 w-4 text-primary" />
                                    <h3 className="font-heading text-sm font-bold">Bilgileriniz güvende</h3>
                                </div>
                                <ul className="mt-3 space-y-2 text-xs leading-5 text-muted-foreground">
                                    <li>• Kart bilgileri bizde saklanmaz.</li>
                                    <li>• Belgeler yalnızca başvurunuzda kullanılır.</li>
                                    <li>• Vizeniz PDF olarak e-postanıza gelir.</li>
                                </ul>
                            </div>

                            <div className="rounded-xl border border-border bg-card p-5">
                                <h3 className="font-heading text-sm font-bold">Yardıma mı ihtiyacınız var?</h3>
                                <p className="mt-2 text-xs leading-5 text-muted-foreground">
                                    Takılırsanız WhatsApp'tan yazın, hemen yardımcı olalım.</p>
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
