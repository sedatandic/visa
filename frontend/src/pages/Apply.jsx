import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
    AlertCircle,
    AlertTriangle,
    ArrowLeft,
    ArrowRight,
    Baby,
    BadgeCheck,
    BookUser,
    Building2,
    CalendarDays,
    Camera,
    Check,
    CheckCircle2,
    CreditCard,
    FileText,
    FileCheck2,
    FileUp,
    Info,
    Loader2,
    Pencil,
    Landmark,
    Lock,
    Minus,
    Plane,
    Plus,
    Save,
    Scale,
    ShieldCheck,
    Sparkles,
    ScanLine,
    Tag,
    Trash2,
    User,
    Users,
    Wifi,
} from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { api, apiError, customerAuth } from "../lib/api";
import { formatDate, formatMoney, parseApplyPath, setMeta } from "../lib/site";
import { useContact, waLink } from "../lib/contact";
import { PageHeader } from "../components/SiteLayout";
import { FileDropzone } from "../components/FileDropzone";
import { DateField, fromISODate } from "../components/DateField";
import { FxNote } from "../components/FxNote";
import { BundlePicker } from "../components/BundlePicker";
import { ComboSelector } from "../components/ComboSelector";
import { TripSuggestions } from "../components/TripSuggestions";
import { ExtraOptions } from "../components/ExtraOptions";
import { ImportantNotice } from "../components/ImportantNotice";
import { FamilyDiscountMeter } from "../components/FamilyDiscountMeter";
import { PhotoRetryHelper } from "../components/PhotoRetryHelper";
import { WhatsAppIcon } from "../components/WhatsAppIcon";
import { useCart } from "../lib/cart";
import { BankTransferInfo } from "../components/BankTransferInfo";
import { SecurityMiniStrip } from "../components/SecurityBadges";
import { BankAccounts } from "../components/BankAccounts";
import { VisaComparison } from "../components/VisaComparison";
import { InsuredIdentityFields } from "../components/InsuredIdentityFields";
import { cleanTckn, validTckn } from "../lib/tckn";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "../components/ui/dialog";
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

// Tarihi netlesmemis basvurular icin yaklasik seyahat zamani secenekleri
const TRAVEL_WINDOWS = [
    { id: "this_month", label: "Bu ay içinde" },
    { id: "1_3_months", label: "1-3 ay içinde" },
    { id: "3_plus_months", label: "3 aydan sonra" },
    { id: "undecided", label: "Henüz karar vermedim" },
];

// Oneri kartlari icin kapak gorselleri (urunde image_url yoksa kullanilir)
const SUGGESTION_COVERS = {
    insurance:
        "https://images.unsplash.com/photo-1581553673739-c4906b5d0de8?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
    esim: "https://images.unsplash.com/photo-1651467606797-e1c660cf3fda?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200",
};

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

// Cep telefonu maskesi: her zaman +90 ile baslar, "+90 532 588 26 30" duzeninde gosterilir.
const formatPhoneTR = (value) => {
    let digits = (value || "").replace(/\D/g, "");
    if (digits.startsWith("0090")) digits = digits.slice(4);
    if (digits.startsWith("90")) digits = digits.slice(2);
    if (digits.startsWith("0")) digits = digits.slice(1);
    digits = digits.slice(0, 10);
    const groups = [digits.slice(0, 3), digits.slice(3, 6), digits.slice(6, 8), digits.slice(8, 10)].filter(
        Boolean
    );
    return groups.length ? `+90 ${groups.join(" ")}` : "+90 ";
};

const PHONE_MASK = "+90 5XX XXX XX XX";

const NUMBER_WORDS = ["", "bir", "iki", "üç", "dört", "beş", "altı"];
const countWord = (n) => NUMBER_WORDS[n] || String(n);

const Field = ({ label, children, error, required, htmlFor }) => (    <div className="space-y-2" data-invalid={error ? "true" : undefined}>
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
    phone: "Cep telefonu numarası",
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
    travel_window: "Yaklaşık seyahat zamanı",
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

// Tum indirimlerin toplami: aile + sigorta + seyahat paketi
const savingsTotal = (q) =>
    Number(q?.family_discount || 0) +
    Number(q?.visa_insurance_discount || 0) +
    Number(q?.bundle_discount || 0);

// Ozetin altinda kazanci vurgulayan seffaf satir
const SavingsNote = ({ quote, testId }) => {
    const saved = savingsTotal(quote);
    if (saved <= 0) return null;
    return (
        <div
            className="mt-3 flex items-center gap-2 rounded-xl border border-[hsl(var(--brand-green)/0.35)] bg-[hsl(var(--brand-green)/0.08)] px-3 py-2.5"
            data-testid={testId}
        >
            <Sparkles className="h-4 w-4 shrink-0 text-[hsl(var(--brand-green))]" aria-hidden="true" />
            <p className="text-xs font-semibold leading-5 text-[hsl(var(--brand-green))]">
                Bu başvuruda toplam {formatMoney(saved, quote.currency)} tasarruf ettiniz
            </p>
        </div>
    );
};

export default function Apply() {
    const siteContact = useContact();
    const [searchParams] = useSearchParams();
    const { seg1, seg2 } = useParams();
    const pathIds = useMemo(() => parseApplyPath(seg1, seg2), [seg1, seg2]);
    const navigate = useNavigate();

    const [visaTypes, setVisaTypes] = useState([]);
    const [addonMeta, setAddonMeta] = useState([]);
    const [familyTiers, setFamilyTiers] = useState([]);
    const photoInputs = useRef({});
    // Vize kartindan gelen secim (?vize=): yeni eklenen yolculara da uygulanir
    const preselectedVisa = useRef("");
    const [maxTravelers, setMaxTravelers] = useState(10);
    const [step, setStep] = useState(0);
    const [compareOpen, setCompareOpen] = useState(false);
    const [visaEditOpen, setVisaEditOpen] = useState(false);
    const [datesEditOpen, setDatesEditOpen] = useState(false);
    const cart = useCart();

    const [contact, setContact] = useState({ full_name: "", email: "", phone: "+90 ", address_city: "", whatsapp_optin: false });
    const [travelers, setTravelers] = useState([newTraveler()]);
    const [openNationalId, setOpenNationalId] = useState({});
    const [fieldsOpen, setFieldsOpen] = useState({});
    const [travel, setTravel] = useState({
        arrival_date: "",
        departure_date: "",
        dates_unknown: false,
        travel_window: "",
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
    // Vize basvurusuyla birlikte alinan policeye uygulanan indirim bilgisi
    const [visaInsuranceInfo, setVisaInsuranceInfo] = useState(null);
    const [insurancePick, setInsurancePick] = useState(null);
    const [esimQty, setEsimQty] = useState({});
    const [tourQty, setTourQty] = useState({});
    const [tourSchedule, setTourSchedule] = useState({});
    const [extraDocs, setExtraDocs] = useState({ ticket: null, hotel: null, other: null });
    const [kvkk, setKvkk] = useState(false);
    const [consents, setConsents] = useState({
        refund_privacy_accepted: false,
        service_terms_accepted: false,
        marketing_email_optin: false,
        ad_personalization_optin: false,
    });
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
    const [showAllInsurance, setShowAllInsurance] = useState(false);
    const [showAllEsim, setShowAllEsim] = useState(false);

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
                notify: !silent,
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
    const submitLock = useRef(false);
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
            "Dubai Vize Başvuru Formu | Dubai Vize Hattı",
            "Dubai vize başvurunuzu online tamamlayın. Tek formda birden fazla yolcu ekleyin; çocuk vizesi ve aile indirimi otomatik hesaplanır.",
            { canonicalPath: "/basvuru" }
        );
    }, []);

    useEffect(() => {
        Promise.all([api.get("/visa-types"), api.get("/content/site")])
            .then(([v, c]) => {
                setVisaTypes(v.data);
                setAddonMeta(c.data.addons || []);
                setFamilyTiers(c.data.family_discount_tiers || []);
                setMaxTravelers(c.data.max_travelers || 10);
                setBankInfo(c.data.bank_transfer || null);
                setAgencyItems((c.data.agency_info || {}).items || []);
                const wanted = pathIds.vize || searchParams.get("vize");
                if (wanted && v.data.some((x) => x.id === wanted)) {
                    const found = v.data.find((x) => x.id === wanted);
                    const childVisa = found.category === "child";
                    preselectedVisa.current = wanted;
                    // Sepetten gelen aile paketi: yolcu listesini de kur (2 yetişkin + 1 çocuk gibi)
                    const adults = Math.min(Math.max(Number(searchParams.get("yetiskin")) || 0, 0), 8);
                    const children = Math.min(Math.max(Number(searchParams.get("cocuk")) || 0, 0), 8);
                    if (!childVisa && adults + children > 1) {
                        const childType = v.data.find(
                            (x) =>
                                x.category === "child" &&
                                Number(x.duration_days) === Number(found.duration_days)
                        );
                        const list = [];
                        for (let i = 0; i < Math.max(adults, 1); i += 1) {
                            list.push({ ...newTraveler("adult"), visa_type_id: wanted });
                        }
                        for (let i = 0; i < children; i += 1) {
                            list.push({
                                ...newTraveler("child"),
                                visa_type_id: childType ? childType.id : "",
                            });
                        }
                        setTravelers(list);
                        toast.success(
                            `${found.name} ve ${children} çocuk vizesi forma eklendi (${list.length} yolcu).`
                        );
                        return;
                    }
                    setTravelers((list) =>
                        list.map((t) => {
                            const isChild = t.applicant_type === "child";
                            if (isChild !== childVisa) return t;
                            return { ...t, visa_type_id: wanted, applicant_type: childVisa ? "child" : "adult" };
                        })
                    );
                    toast.success(`${found.name} formda otomatik seçildi.`);
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
                if (data.visa_insurance) setVisaInsuranceInfo(data.visa_insurance);
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
    const datesFlexible = Boolean(travel.dates_unknown);
    // Tarih belli degilse de ekstralar secilebilir; baslangic tarihi sonra ayarlanir
    const extrasSelectable = travelDatesReady || datesFlexible;
    const travelWindowLabel =
        TRAVEL_WINDOWS.find((w) => w.id === travel.travel_window)?.label || "";
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

    const insuranceProducts = useMemo(() => {
        if (!visaCoverDays) return allInsuranceProducts;
        const withinVisa = allInsuranceProducts.filter(
            (p) => Number(p.validity_days) <= visaCoverDays
        );
        const coversTrip = (list) => list.some((p) => Number(p.validity_days) >= (tripDays || 0));
        if (!tripDays || coversTrip(withinVisa)) {
            return withinVisa.length ? withinVisa : allInsuranceProducts;
        }
        // Seyahat, vize suresinden uzun: kapsayan uzun policeler (orn. 60 gun) de secilebilir
        const longer = allInsuranceProducts.filter((p) => Number(p.validity_days) >= tripDays);
        return longer.length ? [...withinVisa, ...longer] : allInsuranceProducts;
    }, [allInsuranceProducts, visaCoverDays, tripDays]);

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
        if (!win) {
            if (!datesFlexible) return null;
            return (
                <p
                    className="mt-2 flex items-start gap-1.5 text-xs font-medium text-muted-foreground"
                    data-testid={testId}
                >
                    <CalendarDays className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                    <span>
                        {product.validity_days} gün geçerli · başlangıç tarihi siz bildirince ayarlanır
                    </span>
                </p>
            );
        }
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

    // Akilli oneri: seyahat suresini (yoksa vize suresini) karsilayan en uygun paket
    const coverDays = tripDays || visaCoverDays || null;

    const bestFit = (list) => {
        if (!coverDays || !list.length) return null;
        const covering = list.filter((p) => Number(p.validity_days) >= coverDays);
        if (covering.length) {
            return covering.reduce((best, p) => (Number(p.price) < Number(best.price) ? p : best)).id;
        }
        return list.reduce((best, p) =>
            Number(p.validity_days) > Number(best.validity_days) ? p : best
        ).id;
    };

    // Tarihlere gore kisa liste: kapsami yeten en kisa sureli 2-3 paket one cikar
    const shortlistFor = (list) => {
        if (list.length <= 3) return list;
        if (!coverDays) return list.slice(0, 3);
        const covering = list.filter((p) => Number(p.validity_days) >= coverDays);
        const pool = covering.length ? covering : list;
        const tightestDays = Math.min(...pool.map((p) => Number(p.validity_days) || 0));
        const sorted = pool
            .slice()
            .sort(
                (a, b) =>
                    Number(a.validity_days) - Number(b.validity_days) ||
                    Number(a.price) - Number(b.price)
            );
        const tight = sorted.filter((p) => Number(p.validity_days) === tightestDays);
        const rest = sorted.filter((p) => Number(p.validity_days) !== tightestDays);
        return [...tight, ...rest].slice(0, 3);
    };

    // Seyahat suresinden (yoksa vize suresinden) KISA paketler hic teklif edilmez
    const coveringOnly = (list) => {
        if (!coverDays || !list.length) return list;
        const covering = list.filter((p) => Number(p.validity_days) >= coverDays);
        if (covering.length) return covering;
        // Hicbiri kapsamiyorsa yalnizca en uzun sureli paket(ler) gosterilir
        const maxDays = Math.max(...list.map((p) => Number(p.validity_days) || 0));
        return list.filter((p) => Number(p.validity_days) === maxDays);
    };

    const eligibleInsurance = useMemo(
        () => coveringOnly(insuranceProducts),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [insuranceProducts, coverDays]
    );
    const eligibleEsim = useMemo(
        () => coveringOnly(esimProducts),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [esimProducts, coverDays]
    );

    const insuranceShortlist = useMemo(
        () => shortlistFor(eligibleInsurance),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [eligibleInsurance, coverDays]
    );
    const esimShortlist = useMemo(
        () => shortlistFor(eligibleEsim),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [eligibleEsim, coverDays]
    );
    const visibleInsurance = showAllInsurance ? eligibleInsurance : insuranceShortlist;
    const visibleEsim = showAllEsim ? eligibleEsim : esimShortlist;

    const recommendedInsuranceId = useMemo(
        () => bestFit(insuranceProducts),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [insuranceProducts, coverDays]
    );
    const recommendedEsimId = useMemo(
        () => bestFit(esimProducts),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [esimProducts, coverDays]
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

    // Ana sayfadan paket secilerek gelindiyse (/basvuru/pack-x veya ?paket=pack_x) secimleri hazir getir
    const bundleParam = pathIds.paket || searchParams.get("paket");
    const bundleApplied = useRef(false);
    useEffect(() => {
        if (!bundleParam || bundleApplied.current) return;
        const adultsParam = Math.max(1, Number(searchParams.get("yetiskin")) || 1);
        const wantTour = searchParams.get("tur") === "1";
        api.get("/bundles")
            .then(({ data }) => {
                const match = (data.items || []).find((b) => b.id === bundleParam);
                if (!match) return;
                bundleApplied.current = true;
                setInsurancePick(match.insurance.id);
                setEsimQty({ [match.esim.id]: Math.min(Math.max(adultsParam, 1), 10) });
                if (match.visa?.id) {
                    setTravelers((list) =>
                        list.map((t) =>
                            t.applicant_type === "child" ? t : { ...t, visa_type_id: match.visa.id }
                        )
                    );
                }
                // "Tam tatil" secildiyse col safarisini yolcu sayisi kadar ekle
                if (wantTour && match.tour?.id) {
                    const travelers = adultsParam + Math.max(0, Number(searchParams.get("cocuk")) || 0);
                    setTourQty({ [match.tour.id]: Math.min(Math.max(travelers, 1), 10) });
                }
                toast.success(
                    wantTour
                        ? `${match.name} seçildi. Vize, sigorta, eSIM ve çöl safarisi hazır geldi.`
                        : `${match.name} seçildi. Vize, sigorta ve eSIM hazır geldi.`
                );
            })
            .catch(() => {});
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [bundleParam]);

    // Yoneticinin hazirladigi teklif linki (?teklif=<token>): secimler hazir gelir
    const offerToken = searchParams.get("teklif") || "";
    const [offerInfo, setOfferInfo] = useState(null);
    const offerApplied = useRef(false);
    useEffect(() => {
        if (!offerToken || offerApplied.current || !storeProducts.length) return;
        offerApplied.current = true;
        api.get(`/offers/${offerToken}`)
            .then(({ data }) => {
                setOfferInfo(data);
                if (data.customer_name) {
                    setContact((c) => ({ ...c, full_name: c.full_name || data.customer_name }));
                }
                if (Array.isArray(data.travelers) && data.travelers.length) {
                    setTravelers(
                        data.travelers.map((t) => ({
                            ...newTraveler(t.applicant_type === "child" ? "child" : "adult"),
                            visa_type_id: t.visa_type_id || "",
                        }))
                    );
                }
                if (data.arrival_date || data.departure_date) {
                    setTravel((t) => ({
                        ...t,
                        arrival_date: data.arrival_date || t.arrival_date,
                        departure_date: data.departure_date || t.departure_date,
                    }));
                }
                if (data.addons?.express) setAddons((a) => ({ ...a, express: true }));
                const esim = {};
                const tours = {};
                for (const line of data.store_items || []) {
                    const product = storeProducts.find((p) => p.id === line.product_id);
                    if (!product) continue;
                    if (product.kind === "insurance") setInsurancePick(product.id);
                    if (product.kind === "esim") esim[product.id] = line.quantity || 1;
                    if (product.kind === "tour") {
                        tours[product.id] = line.quantity || 1;
                        if (line.scheduled_date) {
                            setTourSchedule((prev) => ({
                                ...prev,
                                [product.id]: { date: line.scheduled_date, time: line.scheduled_time || "" },
                            }));
                        }
                    }
                }
                if (Object.keys(esim).length) setEsimQty(esim);
                if (Object.keys(tours).length) setTourQty(tours);
                toast.success("Size hazırlanan teklif forma yüklendi. Bilgilerinizi tamamlayıp ödemeye geçebilirsiniz.");
            })
            .catch(() =>
                toast.error("Teklif bulunamadı veya süresi doldu. Lütfen danışmanınızla iletişime geçin.")
            );
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [offerToken, storeProducts]);

    // Sepetten gelen basvuru (?sepet=1): sigorta / eSIM / tur secimleri forma tasinir
    const cartImported = useRef(false);    useEffect(() => {
        if (searchParams.get("sepet") !== "1" || cartImported.current || !storeProducts.length) return;
        cartImported.current = true;
        const esim = {};
        const tours = {};
        for (const item of cart.items) {
            const product = storeProducts.find((p) => p.id === item.product_id);
            if (!product) continue;
            if (product.kind === "insurance") setInsurancePick(product.id);
            if (product.kind === "esim") esim[product.id] = item.quantity;
            if (product.kind === "tour") {
                tours[product.id] = item.quantity;
                if (item.scheduled_date) {
                    setTourSchedule((prev) => ({
                        ...prev,
                        [product.id]: { date: item.scheduled_date, time: item.scheduled_time || "" },
                    }));
                }
            }
        }
        if (Object.keys(esim).length) setEsimQty(esim);
        if (Object.keys(tours).length) setTourQty(tours);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [searchParams, storeProducts]);

    // Süre değişince kapsamı yetmeyen poliçe seçimini düşür
    useEffect(() => {
        if (insurancePick && !insuranceProducts.some((p) => p.id === insurancePick)) {
            setInsurancePick(null);
        }
    }, [insuranceProducts, insurancePick]);

    const applyRecommended = () => {
        if (!extrasSelectable) {
            toast.error("Önce gidiş tarihinizi seçin veya \"tarihim henüz belli değil\" seçeneğini işaretleyin.");
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

    // Basvuru tipi: tek yolcu = bireysel, birden fazla yolcu = grup/aile
    const applicationType = travelers.length > 1 ? "group" : "individual";

    const setApplicationType = (type) => {
        if (type === applicationType) return;
        if (type === "group") {
            addTraveler("adult");
            return;
        }
        setTravelers((list) => list.slice(0, 1));
        setErrors({});
        toast.success("Bireysel başvuruya geçildi; yalnızca ilk yolcu kaldı.");
    };

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

    const FlexibleDatesNote = ({ testId }) => (
        <div
            className="mt-4 flex items-start gap-2.5 rounded-xl border border-dashed border-primary/40 bg-primary/[0.04] p-4"
            data-testid={testId}
        >
            <CalendarDays className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
            <p className="text-sm leading-6 text-muted-foreground">
                Seyahat tarihiniz henüz belli değil. Paketi şimdi ekleyebilirsiniz;{" "}
                <strong className="text-foreground">başlangıç tarihi siz bildirince ayarlanır</strong>.
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

    // Sigorta secildiginde police kesimi icin her yolcunun TC kimlik numarasi gerekir.
    const insuredRows = useMemo(
        () =>
            travelers.map((t, idx) => ({
                key: t.key,
                label: `${t.first_name} ${t.last_name}`.trim() || `${idx + 1}. Yolcu`,
                tc_kimlik_no: t.national_id,
            })),
        [travelers]
    );

    const insuredMissing = useMemo(
        () => (insurancePick ? travelers.filter((t) => !validTckn(t.national_id)) : []),
        [insurancePick, travelers]
    );

    const toggleEsim = (product) => {
        if (!extrasSelectable) {
            toast.error("Önce gidiş tarihinizi seçin veya \"tarihim henüz belli değil\" seçeneğini işaretleyin.");
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

    // --- Sigorta / eSIM: seyahat tarihine gore detayli aciklamali 3 secenek ---
    const esimSelected = Object.values(esimQty).some((q) => q > 0);
    const pickInsurance = (product) => {
        if (!extrasSelectable) {
            toast.error('Önce gidiş tarihinizi seçin veya "tarihim henüz belli değil" seçeneğini işaretleyin.');
            return;
        }
        if (insurancePick === product.id) {
            setInsurancePick(null);
            return;
        }
        setInsurancePick(product.id);
        toast.success(`${product.name} eklendi.`);
    };

    // Kartta "neden bu paket" cumlesi: seyahat suresi yoksa vize suresine bakar
    const fitNoteFor = (product) => {
        const days = Number(product.validity_days) || 0;
        if (tripDays) {
            return days >= tripDays
                ? { tone: "ok", text: `${tripDays} günlük seyahatinizin tamamını kapsar` }
                : { tone: "warn", text: `Seyahatiniz ${tripDays} gün · bu paket ${days} günü kapsar` };
        }
        if (visaCoverDays) {
            return { tone: "neutral", text: `${visaCoverDays} günlük vize sürenize uygun` };
        }
        return null;
    };

    const badgesFor = (product, list, recommendedId, recommendedTestId) => {
        const badges = [];
        if (product.id === recommendedId) {
            badges.push({ label: "Size en uygun", tone: "primary", testId: recommendedTestId });
        }
        if (product.popular) {
            badges.push({ label: "En çok tercih edilen", tone: "accent" });
        }
        const cheapest = Math.min(...list.map((p) => Number(p.price) || 0));
        if (badges.length < 2 && Number(product.price) === cheapest) {
            badges.push({ label: "En ekonomik", tone: "neutral" });
        }
        return badges.slice(0, 2);
    };

    const extrasDatesNote = (kind) => {
        if (travelDatesReady) return null;
        return datesFlexible ? (
            <FlexibleDatesNote testId={`${kind}-dates-flexible`} />
        ) : (
            <TravelDatesRequiredNote testId={`${kind}-dates-required`} />
        );
    };

    // Vize ile birlikte alinan policede indirim: kartta ustu cizili fiyat + rozet
    const insuranceDiscountRate = Number(visaInsuranceInfo?.rate || 0);
    const insuranceDiscountFor = (product) => {
        if (!(insuranceDiscountRate > 0)) return null;
        const price = Number(product.price) || 0;
        return {
            label:
                visaInsuranceInfo?.card_badge ||
                `Vize ile birlikte %${Math.round(insuranceDiscountRate * 100)} indirim`,
            finalPrice: Math.round(price * (1 - insuranceDiscountRate) * 100) / 100,
        };
    };

    const insuranceOptions = visibleInsurance.map((p) => ({
        id: p.id,
        product: p,
        badges: badgesFor(p, visibleInsurance, recommendedInsuranceId, `insurance-recommended-${p.id}`),
        discount: insuranceDiscountFor(p),
        fit: fitNoteFor(p),
        highlight: [p.coverage, `${p.validity_days} gün geçerli`].filter(Boolean).join(" · "),
        features: (p.features || []).slice(0, 2),
        dateNote: <DateWindowNote product={p} testId={`insurance-dates-${p.id}`} />,
        selected: insurancePick === p.id,
        onSelect: () => pickInsurance(p),
    }));

    const esimOptions = visibleEsim.map((p) => ({
        id: p.id,
        product: p,
        badges: badgesFor(p, visibleEsim, recommendedEsimId, `esim-recommended-${p.id}`),
        fit: fitNoteFor(p),
        highlight: [p.data_amount, `${p.validity_days} gün`].filter(Boolean).join(" · "),
        features: (p.features || []).slice(0, 2),
        dateNote: <DateWindowNote product={p} testId={`esim-dates-${p.id}`} />,
        selected: Number(esimQty[p.id] || 0) > 0,
        qty: Number(esimQty[p.id] || 0),
        onSelect: () => toggleEsim(p),
        onQtyChange: (delta) => changeEsimQty(p.id, delta),
    }));

    const insuranceBlock = insuranceProducts.length > 0 && (
        <ExtraOptions
            testId="apply-insurance-section"
            optionTestIdPrefix="insurance-option"
            icon={ShieldCheck}
            title="Size uygun seyahat sağlık sigortası önerilerimiz"
            subtitle={`${
                tripDays ? `${tripDays} günlük seyahatiniz` : "Vize süreniz"
            } için ${countWord(insuranceOptions.length)} poliçe seçtik; seyahatinizden kısa süreli paketleri listelemiyoruz. Poliçe yolcu başına hesaplanır, gidiş tarihinizde başlar ve PDF olarak e-postanıza gelir.`}
            note={extrasDatesNote("insurance")}
            options={insuranceOptions}
            disabled={!extrasSelectable}
            unitLabel="kişi"
            footer={
                <>
                    {eligibleInsurance.length > visibleInsurance.length && (
                        <button
                            type="button"
                            onClick={() => setShowAllInsurance(true)}
                            className="mt-4 text-sm font-semibold text-primary underline decoration-primary/40 underline-offset-4 transition-colors duration-200 hover:decoration-primary"
                            data-testid="show-all-insurance-button"
                        >
                            Tüm sigorta paketlerini gör ({eligibleInsurance.length})
                        </button>
                    )}
                    {showAllInsurance && eligibleInsurance.length > insuranceShortlist.length && (
                        <button
                            type="button"
                            onClick={() => setShowAllInsurance(false)}
                            className="mt-4 text-sm font-semibold text-muted-foreground underline underline-offset-4 transition-colors duration-200 hover:text-primary"
                            data-testid="hide-all-insurance-button"
                        >
                            Sadece önerilenleri göster
                        </button>
                    )}
                    {insurancePick ? (
                        <p className="mt-3 text-sm text-muted-foreground" data-testid="insurance-selected-note">
                            {travelerCount} yolcu için poliçe eklendi
                            {travel.arrival_date
                                ? ` · ${formatDate(travel.arrival_date)} tarihinde başlar`
                                : datesFlexible
                                  ? " · başlangıç tarihi siz bildirince ayarlanır"
                                  : ""}
                            . Toplam sepetinizde otomatik hesaplanır.
                        </p>
                    ) : (
                        <p className="mt-3 text-xs text-muted-foreground" data-testid="insurance-optional-note">
                            Sigorta zorunlu değildir. Seçtiğiniz paketi tekrar tıklayarak kaldırabilirsiniz.
                        </p>
                    )}
                </>
            }
        />
    );

    const esimBlock = esimProducts.length > 0 && (
        <ExtraOptions
            testId="apply-esim-section"
            optionTestIdPrefix="esim-option"
            icon={Wifi}
            title="Seyahatinize en uygun eSIM önerilerimiz"
            subtitle={`${
                tripDays ? `${tripDays} günlük seyahatiniz` : "Seyahat planınız"
            } için ${countWord(esimOptions.length)} internet paketi seçtik; seyahatinizden kısa süreli paketleri listelemiyoruz. QR kodunuz e-postanıza gelir, Türkiye numaranız açık kalır.`}
            note={extrasDatesNote("esim")}
            options={esimOptions}
            disabled={!extrasSelectable}
            unitLabel="adet"
            footer={
                <>
                    {eligibleEsim.length > visibleEsim.length && (
                        <button
                            type="button"
                            onClick={() => setShowAllEsim(true)}
                            className="mt-4 text-sm font-semibold text-primary underline decoration-primary/40 underline-offset-4 transition-colors duration-200 hover:decoration-primary"
                            data-testid="show-all-esim-button"
                        >
                            Tüm eSIM paketlerini gör ({eligibleEsim.length})
                        </button>
                    )}
                    {showAllEsim && eligibleEsim.length > esimShortlist.length && (
                        <button
                            type="button"
                            onClick={() => setShowAllEsim(false)}
                            className="mt-4 text-sm font-semibold text-muted-foreground underline underline-offset-4 transition-colors duration-200 hover:text-primary"
                            data-testid="hide-all-esim-button"
                        >
                            Sadece önerilenleri göster
                        </button>
                    )}
                    {esimSelected ? (
                        <p className="mt-3 text-sm text-muted-foreground" data-testid="esim-selected-note">
                            eSIM paketiniz{" "}
                            {travel.arrival_date
                                ? `${formatDate(travel.arrival_date)} tarihinde başlar`
                                : "gidiş tarihinizde başlar"}
                            . Adeti yolcu sayınıza göre ayarlayabilirsiniz.
                        </p>
                    ) : (
                        <p className="mt-3 text-xs text-muted-foreground" data-testid="esim-optional-note">
                            eSIM zorunlu değildir. Seçtiğiniz paketi tekrar tıklayarak kaldırabilirsiniz.
                        </p>
                    )}
                </>
            }
        />
    );

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
                    date: suggestedTourDate || travel.arrival_date || "",
                    time: (product.time_slots || [])[0] || "",
                },
            };
        });
    };

    const setTourPlan = (productId, patch) =>
        setTourSchedule((prev) => ({ ...prev, [productId]: { ...(prev[productId] || {}), ...patch } }));

    // Tur icin onerilen tarih: gidisin ertesi gunu (donusu asarsa gidis gunu)
    const suggestedTourDate = useMemo(() => {
        if (!travel.arrival_date) return "";
        const start = new Date(`${travel.arrival_date}T00:00:00Z`);
        if (Number.isNaN(start.getTime())) return "";
        const nextDay = new Date(start.getTime() + 86400000);
        const end = travel.departure_date ? new Date(`${travel.departure_date}T00:00:00Z`) : null;
        const target = end && nextDay > end ? start : nextDay;
        return target.toISOString().slice(0, 10);
    }, [travel.arrival_date, travel.departure_date]);

    const preferredSlot = (product) => {
        const slots = product.time_slots || [];
        return slots.includes("15:00") ? "15:00" : slots[0] || "";
    };

    const toggleSuggestedTour = (product) => {
        if (tourQty[product.id]) {
            setTourQty((prev) => {
                const { [product.id]: _removed, ...rest } = prev;
                return rest;
            });
            return;
        }
        setTourQty((prev) => ({ ...prev, [product.id]: Math.min(Math.max(travelerCount, 1), 10) }));
        setTourPlan(product.id, {
            date: suggestedTourDate || travel.arrival_date || "",
            time: preferredSlot(product),
        });
        toast.success("Çöl safarisi eklendi. Tarih ve saati Özet adımında değiştirebilirsiniz.");
    };

    // Tur secili ama tarih bos ise gidis tarihine gore otomatik doldur (ozet fiyatta gorunsun)
    useEffect(() => {
        if (!suggestedTourDate) return;
        const missing = Object.keys(tourQty).filter(
            (id) => Number(tourQty[id]) > 0 && !(tourSchedule[id] || {}).date
        );
        if (!missing.length) return;
        setTourSchedule((prev) => {
            const next = { ...prev };
            for (const id of missing) {
                const product = tourProducts.find((p) => p.id === id);
                next[id] = { date: suggestedTourDate, time: product ? preferredSlot(product) : "" };
            }
            return next;
        });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [suggestedTourDate, tourQty, tourSchedule, tourProducts]);

    // Gidis-donus tarihine gore 3 oneri: sigorta, eSIM, col safarisi
    const tripSuggestions = useMemo(() => {
        const list = [];
        const insurance = allInsuranceProducts.find((p) => p.id === recommendedInsuranceId);
        if (insurance) {
            list.push({
                key: "insurance",
                icon: ShieldCheck,
                label: "Seyahat sağlık sigortası",
                product: insurance,
                meta: `${insurance.validity_days} gün geçerli${
                    tripDays ? ` · ${tripDays} günlük seyahatinizi kapsar` : ""
                }`,
                unit: "kişi",
                image: insurance.image_url || SUGGESTION_COVERS.insurance,
                selected: insurancePick === insurance.id,
                onToggle: () => {
                    if (insurancePick === insurance.id) {
                        setInsurancePick(null);
                        return;
                    }
                    setInsurancePick(insurance.id);
                    toast.success("Seyahat sağlık sigortası eklendi.");
                },
            });
        }
        const esim = esimProducts.find((p) => p.id === recommendedEsimId);
        if (esim) {
            list.push({
                key: "esim",
                icon: Wifi,
                label: "Dubai eSIM",
                product: esim,
                meta: `${esim.validity_days} gün internet · varışta anında aktif`,
                unit: "kişi",
                image: esim.image_url || SUGGESTION_COVERS.esim,
                selected: Number(esimQty[esim.id] || 0) > 0,
                onToggle: () => {
                    if (esimQty[esim.id]) {
                        setEsimQty((prev) => {
                            const { [esim.id]: _removed, ...rest } = prev;
                            return rest;
                        });
                        return;
                    }
                    setEsimQty({ [esim.id]: Math.min(Math.max(travelerCount, 1), 10) });
                    toast.success("Dubai eSIM eklendi.");
                },
            });
        }
        const tour = tourProducts.find((p) => p.popular) || tourProducts[0];
        if (tour) {
            const plan = tourSchedule[tour.id] || {};
            const selected = Number(tourQty[tour.id] || 0) > 0;
            list.push({
                key: "tour",
                icon: Sparkles,
                label: "Çöl safarisi",
                product: tour,
                meta:
                    selected && plan.date
                        ? `${formatDate(plan.date)} · ${plan.time || preferredSlot(tour)} otelden alınış`
                        : suggestedTourDate
                          ? `Önerilen tarih: ${formatDate(suggestedTourDate)} · ${preferredSlot(tour)} otelden alınış`
                          : "Kumul turu, deve gezisi ve akşam yemeği",
                unit: "kişi",
                selected,
                image: tour.image_url || "",
                onToggle: () => toggleSuggestedTour(tour),
            });
        }
        return list;
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [
        allInsuranceProducts,
        esimProducts,
        tourProducts,
        recommendedInsuranceId,
        recommendedEsimId,
        insurancePick,
        esimQty,
        tourQty,
        tourSchedule,
        suggestedTourDate,
        tripDays,
        travelerCount,
    ]);

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

    // Yolcunun yasi 18'in altindaysa cocuk vizesi gerekir; kullaniciya ayrica sorulmaz.
    const applicantTypeFor = (birthDate, referenceDate) => {
        if (!birthDate) return null;
        const birth = new Date(birthDate);
        if (Number.isNaN(birth.getTime())) return null;
        const ref = referenceDate ? new Date(referenceDate) : new Date();
        if (Number.isNaN(ref.getTime())) return null;
        return (ref - birth) / (365.25 * 86400000) < 18 ? "child" : "adult";
    };

    // Yetiskin <-> cocuk gecisinde ayni sure/giris tipindeki vizeye esler.
    const matchingVisaFor = (currentId, type) => {
        const options = visaOptionsFor(type);
        const current = visaById(currentId);
        if (!current) return options.find((v) => v.popular)?.id || options[0]?.id || "";
        const same = options.find(
            (v) =>
                Number(v.duration_days) === Number(current.duration_days) &&
                v.entry_type === current.entry_type
        );
        return (same || options[0])?.id || "";
    };

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

    // Iletisim bolumundeki basvuru turu: ilk yolcunun yetiskin/cocuk secimini yonetir.
    const primaryApplicantType = travelers[0]?.applicant_type === "child" ? "child" : "adult";
    const hasChildApplicant = travelers.some((t) => t.applicant_type === "child");

    // Adim 1'deki "basvurulan vize turu" dropdown'i: ayni kategorideki tum yolculara uygulanir
    const primaryVisaId = travelers[0]?.visa_type_id || "";
    const primaryVisaOptions = visaOptionsFor(primaryApplicantType);
    const primaryVisa = visaById(primaryVisaId);

    const setPrimaryVisa = (id) => {        const chosen = visaById(id);
        if (!chosen) return;
        const childVisa = chosen.category === "child";
        preselectedVisa.current = id;
        setTravelers((list) =>
            list.map((t) => ((t.applicant_type === "child") === childVisa ? { ...t, visa_type_id: id } : t))
        );
        setErrors((p) => ({ ...p, stay_length: undefined }));
    };

    // Bireysel basvuruda yolcunun adi iletisim adiyla ayni olabilir; iki kez yazdirmayiz.
    // Ama pasaporttan okunan ad her zaman esastir (iletisim kisisi baskasi olabilir).
    useEffect(() => {
        const name = contact.full_name.trim();
        if (travelers.length !== 1 || name.split(/\s+/).length < 2) return;
        const parts = name.split(/\s+/);
        const last = parts.pop();
        const first = parts.join(" ");
        setTravelers((list) => {
            const t = list[0];
            if (!t || t.first_name || t.last_name) return list;
            if (ocr[t.key]?.status === "done") return list;
            return [{ ...t, first_name: first, last_name: last }];
        });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [contact.full_name, travelers.length]);

    // Dogum tarihi girildiginde/okundugunda yetiskin-cocuk ayrimi kendiliginden guncellenir.
    useEffect(() => {
        if (!visaTypes.length) return;
        setTravelers((list) => {
            let changed = false;
            const next = list.map((t) => {
                const type = applicantTypeFor(t.birth_date, travel.arrival_date);
                if (!type || type === t.applicant_type) return t;
                changed = true;
                return { ...t, applicant_type: type, visa_type_id: matchingVisaFor(t.visa_type_id, type) };
            });
            return changed ? next : list;
        });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [travelers, travel.arrival_date, visaTypes]);

    const toggleDatesUnknown = (checked) => {        const on = !!checked;
        setTravel((t) => ({
            ...t,
            dates_unknown: on,
            arrival_date: on ? "" : t.arrival_date,
            departure_date: on ? "" : t.departure_date,
            travel_window: on ? t.travel_window : "",
        }));
        setErrors((p) => ({
            ...p,
            arrival_date: undefined,
            departure_date: undefined,
            travel_window: undefined,
            stay_length: undefined,
        }));
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
        setTravelers((list) => {
            const fresh = newTraveler(type);
            const preset = visaTypes.find((v) => v.id === preselectedVisa.current);
            if (preset && (preset.category === "child") === (type === "child")) {
                fresh.visa_type_id = preset.id;
            }
            return [...list, fresh];
        });
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
                    const identityChanged =
                        !!d.passport_no &&
                        !!t.passport_no &&
                        String(d.passport_no).trim() !== String(t.passport_no).trim();
                    // Baska bir pasaport yuklendiyse eski kisiden kalan, bu okumada
                    // gelmeyen alanlar temizlenir (iki kisinin bilgisi karismasin)
                    const base = { ...t };
                    if (identityChanged) {
                        ["national_id", "birth_place", "passport_issue_date", "passport_issue_place"].forEach(
                            (f) => {
                                base[f] = "";
                            }
                        );
                    }
                    fields.forEach((f) => {
                        const value = d[f];
                        if (!value) return;
                        // Pasaport belgesi esas kaynaktir: dolu alanlar da guncellenir,
                        // aksi halde eski yolcunun adi yeni pasaportla karisiyor
                        if (String(base[f] || "").trim() !== String(value).trim()) patch[f] = value;
                    });
                    return { ...base, ...patch };
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
                toast.success("Pasaport okundu, bilgiler pasaporttaki haliyle güncellendi. Lütfen kontrol edin.");
            }
        } catch (err) {
            setOcr((s) => ({ ...s, [key]: { status: "failed", message: apiError(err, "") } }));
        }
    };

    // Vesikalik fotografi yapay zeka ile denetler. Kontrol "uygun degil" derse
    // basvuru bir sonraki adima gecemez; kullanici yeni fotograf yuklemelidir.
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
            const phoneDigits = contact.phone.replace(/\D/g, "").replace(/^90/, "");
            if (phoneDigits.length !== 10 || !phoneDigits.startsWith("5"))
                e.phone = "Cep telefonunuzu +90 5XX XXX XX XX biçiminde girin.";
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
            if (travel.dates_unknown) {
                if (!travel.travel_window)
                    e.travel_window = "Yaklaşık olarak ne zaman gitmeyi planladığınızı seçin.";
                const limit = new Date();
                limit.setMonth(limit.getMonth() + 6);
                const shortPassports = travelers.filter(
                    (t) => t.passport_expiry && new Date(t.passport_expiry) < limit
                );
                if (shortPassports.length)
                    e.passport_validity = `Pasaport bugünden itibaren en az 6 ay geçerli olmalı: ${shortPassports
                        .map((t) => `${t.first_name} ${t.last_name}`.trim())
                        .join(", ")}`;
            } else {
                if (!travel.arrival_date) e.arrival_date = "Gidiş tarihinizi seçin.";
                if (!travel.departure_date) e.departure_date = "Dönüş tarihinizi seçin.";
                if (
                    travel.arrival_date &&
                    travel.departure_date &&
                    new Date(travel.departure_date) < new Date(travel.arrival_date)
                )
                    e.departure_date = "Dönüş tarihi gidiş tarihinden önce olamaz.";
                if (travel.arrival_date && travel.departure_date && !e.departure_date) {
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
            if (!travel.dates_unknown && travel.arrival_date && travel.departure_date) {
                const stayDays =
                    Math.round(
                        (new Date(travel.departure_date) - new Date(travel.arrival_date)) / 86400000
                    ) + 1;
                const tooShort = travelers.filter((t) => {
                    const days = Number(
                        visaTypes.find((v) => v.id === t.visa_type_id)?.duration_days || 0
                    );
                    return days > 0 && stayDays > days;
                });
                if (tooShort.length)
                    e.stay_length = `Planlanan kalış ${stayDays} gün; seçilen vize bu süreyi kapsamıyor. Daha uzun süreli bir vize seçin veya tarihleri güncelleyin.`;
            }
        }
        if (step === 2) {
            const photoPending = [];
            const photoRejected = [];
            travelers.forEach((t) => {
                const te = {};
                if (!t.passportFile) te.passport = "Pasaport fotoğrafı zorunlu.";
                if (!t.photoFile) te.photo = "Vesikalık fotoğraf zorunlu.";
                const check = photoCheck[t.key];
                const name = `${t.first_name} ${t.last_name}`.trim() || `${travelers.indexOf(t) + 1}. Yolcu`;
                if (t.photoFile && (!check || check.status === "loading")) {
                    photoPending.push(name);
                    if (!check) checkPhotoWithAI(t.key, t.photoFile);
                } else if (check?.status === "warn") {
                    photoRejected.push(name);
                    te.photo = "Fotoğraf vize standartlarına uygun değil. Lütfen yeni bir vesikalık yükleyin.";
                }
                if (Object.keys(te).length) e[t.key] = { ...(e[t.key] || {}), ...te };
            });
            if (photoRejected.length)
                e.photo_quality = `Vesikalık fotoğraf vize standartlarına uygun olmadan devam edemezsiniz (${photoRejected.join(", ")}). Lütfen uygun bir fotoğraf yükleyin.`;
            else if (photoPending.length)
                e.photo_quality = `Vesikalık fotoğraf kontrolü sürüyor (${photoPending.join(", ")}). Lütfen birkaç saniye bekleyin.`;
        }
        setErrors(e);
        if (Object.keys(e).length) {
            const labels = collectErrorLabels(e, travelers);
            const blocking = e.travelers_adult || e.stay_length || e.passport_validity || e.photo_quality;
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
    }, [step, contact, travelers, travel, extraDocs, visaTypes, photoCheck]);

    const next = () => {
        if (!validateStep()) return;
        setStep((s) => Math.min(s + 1, STEPS.length - 1));
        window.scrollTo({ top: 0, behavior: "smooth" });
    };
    const back = () => {
        setStep((s) => Math.max(s - 1, 0));
        window.scrollTo({ top: 0, behavior: "smooth" });
    };
    // Stepper'dan adim degistirme: geriye serbest, ileriye tek adim + dogrulama
    const goToStep = (target) => {
        if (target === step) return;
        if (target < step) {
            setStep(target);
            window.scrollTo({ top: 0, behavior: "smooth" });
            return;
        }
        if (!validateStep()) return;
        setStep(Math.min(target, step + 1));
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    const setConsent = (key, value) => setConsents((s) => ({ ...s, [key]: value }));

    const submitApplication = async () => {
        if (submitLock.current) return null;
        if (!kvkk) {
            toast.error("Devam etmek için KVKK aydınlatma metnini onaylamanız gerekir.");
            return null;
        }
        if (!consents.refund_privacy_accepted) {
            toast.error("İade ve İptal Koşulları ile Gizlilik Politikası'nı onaylamanız gerekir.");
            return null;
        }
        if (!consents.service_terms_accepted) {
            toast.error("Şartlar ve Mesafeli Hizmet Sözleşmesi'ni onaylamanız gerekir.");
            return null;
        }
        if (missingTourDate) {
            toast.error("Seçtiğiniz tur için tarih belirlemeniz gerekiyor.");
            return null;
        }
        if (insuredMissing.length) {
            toast.error(
                `Seyahat sağlık sigortası için geçerli TC kimlik numarası gerekiyor: ${insuredMissing
                    .map((t, idx) => `${t.first_name} ${t.last_name}`.trim() || `${idx + 1}. Yolcu`)
                    .join(", ")}`
            );
            document
                .querySelector('[data-testid="insurance-identity-block"]')
                ?.scrollIntoView({ behavior: "smooth", block: "center" });
            return null;
        }
        submitLock.current = true;
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
                    tc_kimlik_no: cleanTckn(t.national_id),
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
                consents,
                offer_token: offerToken,
            });
            setCreated(data);
            if (searchParams.get("sepet") === "1") cart.clear();
            toast.success(`Başvurunuz oluşturuldu. Takip kodu: ${data.reference_code}`);
            return data;
        } catch (err) {
            toast.error(apiError(err, "Başvuru oluşturulamadı."));
            return null;
        } finally {
            submitLock.current = false;
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


    // Vize secimi ve tarih duzenleme alanlari: 1. adimda ve 2. adimda satir ici kullanilir
    const visaPickerFields = (
        <>
        <div className="mt-4 flex flex-wrap items-end gap-3 sm:max-w-xl">
            <div className="min-w-[240px] flex-1">
                <Field label="Vize Türü" required>
                    <Select value={primaryVisaId} onValueChange={setPrimaryVisa}>
                        <SelectTrigger data-testid="primary-visa-select">
                            <SelectValue placeholder="Vize türü seçin" />
                        </SelectTrigger>
                        <SelectContent>
                            {primaryVisaOptions.map((v) => (
                                <SelectItem
                                    key={v.id}
                                    value={v.id}
                                    data-testid={`primary-visa-option-${v.id}`}
                                >
                                    {v.name} · {formatMoney(v.price, v.currency)}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </Field>
            </div>
            <Button
                type="button"
                variant="secondary"
                className="h-11 border border-border"
                onClick={() => setCompareOpen(true)}
                data-testid="open-visa-comparison-button"
            >
                <Scale className="mr-2 h-4 w-4" /> Vizeleri karşılaştır
            </Button>
        </div>
        <Dialog open={compareOpen} onOpenChange={setCompareOpen}>
            <DialogContent
                className="max-h-[88vh] max-w-[min(96vw,1360px)] overflow-y-auto"
                data-testid="visa-comparison-dialog"
            >
                <DialogHeader>
                    <DialogTitle>Vize türlerini karşılaştırın</DialogTitle>
                    <DialogDescription>
                        Süre, giriş hakkı, ücret ve kimlere uygun olduğunu görün; uygun
                        olanı seçtiğinizde form otomatik güncellenir.
                    </DialogDescription>
                </DialogHeader>
                <VisaComparison
                    visas={visaTypes}
                    selectedId={primaryVisaId}
                    onSelect={(v) => {
                        setPrimaryVisa(v.id);
                        setCompareOpen(false);
                        toast.success(`${v.name} seçildi.`);
                    }}
                />
            </DialogContent>
        </Dialog>
        </>
    );

    // 2. adim: vize/tarih secilmemisse duzenleyiciler kendiliginden acik gelir
    const visaMissing = !primaryVisaId;
    const datesMissing = !datesFlexible && (!travel.arrival_date || !travel.departure_date);

    const travelDatesEditor = (
        <div
            className="mt-6 rounded-xl border border-border bg-[hsl(var(--cloud))] p-5"
            data-testid="travel-dates-block"
        >
            <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">
                Seyahat tarihleriniz
            </h3>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Gidiş ve dönüş tarihinizi girin; vize süresi ve fiyat bu tarihlere göre
                hesaplanır.
            </p>
            {!datesFlexible && (
                <div className="mt-4 grid gap-5 sm:grid-cols-2">
                    <Field label="Gidiş Tarihi" required error={errors.arrival_date}>
                        <DateField
                            value={travel.arrival_date}
                            onChange={(iso) => {
                                setTravel((t) => ({ ...t, arrival_date: iso }));
                                setErrors((p) => ({ ...p, arrival_date: undefined }));
                            }}
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
                            onChange={(iso) => {
                                setTravel((t) => ({ ...t, departure_date: iso }));
                                setErrors((p) => ({ ...p, departure_date: undefined }));
                            }}
                            minDate={fromISODate(travel.arrival_date) || new Date()}
                            fromYear={new Date().getFullYear()}
                            toYear={new Date().getFullYear() + 3}
                            invalid={!!errors.departure_date}
                            data-testid="input-departure-date"
                        />
                    </Field>
                </div>
            )}

            <label
                className="mt-5 flex cursor-pointer items-start gap-3 rounded-xl border border-border bg-card p-4 text-sm transition-colors duration-200 hover:border-primary/50"
                data-testid="dates-unknown-row"
            >
                <Checkbox
                    checked={datesFlexible}
                    onCheckedChange={toggleDatesUnknown}
                    className="mt-0.5"
                    data-testid="dates-unknown-checkbox"
                />
                <span className="leading-6 text-muted-foreground">
                    <strong className="text-foreground">
                        Seyahat tarihim henüz belli değil.
                    </strong>{" "}
                    Başvurunuza şimdi başlayın; sigorta ve eSIM'in başlangıç tarihini siz
                    bildirdiğinizde biz ayarlarız.
                </span>
            </label>

            {datesFlexible && (
                <div
                    className="mt-4 rounded-xl border border-primary/25 bg-primary/[0.04] p-5"
                    data-invalid={errors.travel_window ? "true" : undefined}
                    data-testid="travel-window-options"
                >
                    <p className="font-heading text-sm font-bold">
                        Yaklaşık olarak ne zaman gitmeyi planlıyorsunuz?
                    </p>
                    <p className="mt-1 text-xs leading-5 text-muted-foreground">
                        Bu bilgi vize başlangıcını ve paket sürelerini planlamamıza yardımcı olur.
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                        {TRAVEL_WINDOWS.map((w) => {
                            const active = travel.travel_window === w.id;
                            return (
                                <button
                                    key={w.id}
                                    type="button"
                                    onClick={() => {
                                        setTravel((t) => ({ ...t, travel_window: w.id }));
                                        setErrors((p) => ({ ...p, travel_window: undefined }));
                                    }}
                                    className={`rounded-full border px-4 py-2 text-xs font-semibold transition-colors duration-200 ${
                                        active
                                            ? "border-primary bg-primary text-primary-foreground"
                                            : "border-border bg-background hover:border-primary/60"
                                    }`}
                                    data-testid={`travel-window-${w.id}`}
                                >
                                    {w.label}
                                </button>
                            );
                        })}
                    </div>
                    {errors.travel_window && (
                        <p
                            className="mt-3 flex items-start gap-1.5 text-xs font-medium text-destructive"
                            role="alert"
                        >
                            <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                            {errors.travel_window}
                        </p>
                    )}
                </div>
            )}

            {tripDays && (
                <p
                    className="mt-4 flex items-start gap-2 text-sm leading-6 text-muted-foreground"
                    data-testid="trip-days-note"
                >
                    <CalendarDays className="mt-0.5 h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                    <span>
                        Seyahatiniz <strong className="text-foreground">{tripDays} gün</strong>{" "}
                        sürüyor. Vize süresini bu plana göre öneriyoruz.
                    </span>
                </p>
            )}
        </div>
    );

    return (
        <div data-testid="application-wizard">
            <PageHeader
                eyebrow="Başvuru Formu"
                title="Dubai vize başvurunuzu tamamlayın"
                description="Tek formda tüm aileniz için başvurun; indirimler otomatik hesaplanır."
            />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page">
                    {offerInfo && (
                        <div
                            className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-[var(--radius-lg)] border border-primary/30 bg-primary/5 px-5 py-4"
                            data-testid="apply-offer-banner"
                        >
                            <div className="min-w-0">
                                <p className="text-xs font-bold uppercase tracking-wide text-primary">
                                    Size hazırlanan teklif
                                </p>
                                <p className="font-heading text-base font-bold">{offerInfo.title}</p>
                                <p className="mt-0.5 text-xs text-muted-foreground">
                                    Vize, sigorta ve eSIM seçimleriniz forma yüklendi; bilgilerinizi tamamlamanız yeterli.
                                </p>
                            </div>
                            <span className="font-heading text-lg font-extrabold" data-testid="apply-offer-total">
                                {formatMoney(offerInfo.total, offerInfo.currency)}
                            </span>
                        </div>
                    )}
                    {/* STEPPER */}
                    <div
                        className="sticky top-[86px] z-30 overflow-hidden rounded-[var(--radius-lg)] border border-border/70 bg-card/95 backdrop-blur-xl sm:top-[98px] lg:top-[110px]"
                        style={{ boxShadow: "var(--shadow-card)" }}
                        data-testid="wizard-stepper"
                    >
                        <div className="flex items-stretch gap-1.5 overflow-x-auto px-4 py-3.5 sm:gap-2 sm:px-5">
                            {STEPS.map((s, i) => {
                                const Icon = s.icon;
                                const done = i < step;
                                const active = i === step;
                                const locked = Boolean(created);
                                return (
                                    <button
                                        type="button"
                                        key={s.key}
                                        onClick={() => !locked && goToStep(i)}
                                        disabled={locked}
                                        aria-current={active ? "step" : undefined}
                                        title={locked ? "Başvurunuz gönderildi" : `Adım ${i + 1}: ${s.label}`}
                                        className={`relative flex min-w-fit flex-1 items-center gap-2 rounded-lg px-1.5 pb-3 pt-1 text-left transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                                            locked ? "cursor-default" : "cursor-pointer hover:bg-primary/[0.05]"
                                        }`}
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
                                                className={`mx-2 hidden h-0.5 flex-1 rounded-full lg:block ${
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
                                    </button>
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

                    <div className="mt-8 grid gap-8 lg:grid-cols-[1.25fr_0.75fr]">
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

                                    <div className="mt-6 grid gap-4 sm:grid-cols-2" data-testid="application-type-picker">
                                        {[
                                            {
                                                id: "individual",
                                                title: "Bireysel",
                                                note: "Yalnızca kendi adınıza başvuruyorsunuz.",
                                            },
                                            {
                                                id: "group",
                                                title: "Grup / Aile",
                                                note: "Birden fazla yolcu, tek başvuru ve tek ödeme.",
                                            },
                                        ].map((opt) => (
                                            <button
                                                key={opt.id}
                                                type="button"
                                                aria-pressed={applicationType === opt.id}
                                                onClick={() => setApplicationType(opt.id)}
                                                className={`rounded-xl border p-5 text-left transition-colors duration-200 hover:border-primary/60 ${
                                                    applicationType === opt.id
                                                        ? "border-primary bg-primary/[0.06]"
                                                        : "border-border bg-card"
                                                }`}
                                                data-testid={`application-type-${opt.id}`}
                                            >
                                                <p className="flex items-center gap-2 font-heading text-base font-bold">
                                                    {opt.id === "group" ? (
                                                        <Users className="h-4.5 w-4.5 text-primary" />
                                                    ) : (
                                                        <User className="h-4.5 w-4.5 text-primary" />
                                                    )}
                                                    {opt.title}
                                                </p>
                                                <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{opt.note}</p>
                                            </button>
                                        ))}
                                    </div>
                                    {applicationType === "group" && (
                                        <div
                                            className="mt-4 rounded-xl border border-primary/30 bg-primary/[0.05] p-4 text-sm leading-6 text-muted-foreground"
                                            data-testid="group-application-note"
                                        >
                                            Bildirimlerin tamamı aşağıdaki telefon ve e-posta adresine gider, ödeme tek
                                            seferde alınır ve seyahat tarihleri grubun tümü için geçerlidir.{" "}
                                            <strong className="text-foreground">
                                                Listedeki ilk yolcu grup sorumlusu olarak kaydedilir.
                                            </strong>{" "}
                                            Aile indirimi yolcu sayısına göre otomatik hesaplanır.
                                        </div>
                                    )}

                                    <div className="mt-6 rounded-xl border border-border bg-[hsl(var(--cloud))] p-5">
                                        <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-muted-foreground">
                                            İletişim bilgileri
                                        </h3>
                                        <div className="mt-4 grid gap-5 sm:grid-cols-2">
                                            <Field label="Adınız Soyadınız" required htmlFor="c-name" error={errors.full_name}>
                                                <Input id="c-name" value={contact.full_name} onChange={setC("full_name")} placeholder="AHMET YILMAZ" data-testid="input-contact-name" />
                                            </Field>
                                            <Field label="E-mail Adresi" required htmlFor="c-email" error={errors.email}>
                                                <Input id="c-email" type="email" value={contact.email} onChange={setC("email")} placeholder="ornek@eposta.com" data-testid="input-contact-email" />
                                            </Field>
                                            <Field
                                                label={
                                                    <span className="inline-flex items-center gap-1.5">
                                                        Cep Telefonu
                                                        <WhatsAppIcon className="h-4 w-4 text-[#25D366]" />
                                                        <span className="text-[#128C4B]">(WhatsApp)</span>
                                                    </span>
                                                }
                                                required
                                                htmlFor="c-phone"
                                                error={errors.phone}
                                            >
                                                <div className="relative">
                                                    <Input
                                                        id="c-phone"
                                                        type="tel"
                                                        inputMode="numeric"
                                                        autoComplete="tel"
                                                        value={contact.phone}
                                                        onChange={(ev) =>
                                                            setContact((s) => ({ ...s, phone: formatPhoneTR(ev.target.value) }))
                                                        }
                                                        onFocus={() =>
                                                            setContact((s) =>
                                                                s.phone.replace(/\D/g, "").length > 2 ? s : { ...s, phone: "+90 " }
                                                            )
                                                        }
                                                        maxLength={17}
                                                        data-testid="input-contact-phone"
                                                    />
                                                    <span
                                                        aria-hidden="true"
                                                        className="pointer-events-none absolute inset-0 flex items-center px-4 text-base md:text-sm"
                                                        data-testid="phone-mask-hint"
                                                    >
                                                        <span className="invisible whitespace-pre">{contact.phone}</span>
                                                        <span className="whitespace-pre text-muted-foreground/45">
                                                            {PHONE_MASK.slice(contact.phone.length)}
                                                        </span>
                                                    </span>
                                                </div>
                                                <p className="mt-1.5 text-xs text-muted-foreground">
                                                    Başvurunuzla ilgili dönüş bu numaraya WhatsApp üzerinden yapılacaktır.
                                                </p>
                                                <label
                                                    className="mt-2 flex cursor-pointer items-center gap-2.5 rounded-lg border border-border bg-card px-3 py-2 text-xs leading-5 transition-colors duration-200 hover:border-[#25D366]/60"
                                                    data-testid="whatsapp-optin-row"
                                                >
                                                    <Switch
                                                        checked={!!contact.whatsapp_optin}
                                                        onCheckedChange={(c) => setContact((s) => ({ ...s, whatsapp_optin: !!c }))}
                                                        data-testid="input-whatsapp-optin"
                                                    />
                                                    <span className="text-muted-foreground">
                                                        <strong className="text-foreground">WhatsApp ile bilgilendir.</strong>{" "}
                                                        Sonuç çıkınca mesaj gönderelim.
                                                    </span>
                                                </label>
                                            </Field>
                                            {hasChildApplicant && (
                                                <div
                                                    className="flex items-center gap-2 rounded-xl border border-primary/25 bg-primary/[0.05] px-4 py-3 text-sm font-semibold text-foreground/85 sm:col-span-2"
                                                    data-testid="applicant-type-auto-note"
                                                >
                                                    <BadgeCheck className="h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                                    Doğum tarihine göre çocuk vizesi seçildi (18 yaş altı).
                                                </div>
                                            )}
                                        </div>
                                        {hasChildApplicant && (
                                            <div
                                                className="mt-4 flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/[0.06] p-4"
                                                data-testid="child-application-notice"
                                            >
                                                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-destructive/15">
                                                    <AlertCircle className="h-4 w-4 text-destructive" />
                                                </span>
                                                <div>
                                                    <p className="font-heading text-sm font-bold text-destructive">
                                                        Çocuk başvurusunda dikkat edilmesi gerekenler
                                                    </p>
                                                    <p className="mt-1 text-sm leading-6 text-muted-foreground">
                                                        18 yaşını doldurmamış yolcular kendi adına tek başına başvuru
                                                        gönderemez. Çocuğunuzun vizesi için aynı formda önce ebeveyn
                                                        bilgilerini tamamlayın, ardından çocuğu yolcu olarak ekleyip
                                                        başvurunuzu aile başvurusu şeklinde iletin.
                                                    </p>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* SEYAHAT TARIHLERI ve VIZE TURU 2. adimda secilir */}

                                    <div className="mt-8 flex flex-wrap items-center justify-between gap-3">
                                        <h3 className="font-heading text-base font-bold">
                                            Yolcular <span className="text-muted-foreground">({travelers.length})</span>
                                        </h3>
                                        <div className="flex flex-wrap gap-2">
                                            <Button type="button" variant="secondary" className="h-10 gap-1.5 border border-border" onClick={() => addTraveler("adult")} data-testid="add-adult-traveler-button">
                                                <Plus className="h-4 w-4" />
                                                <User className="h-4 w-4" />
                                                <span>Yetişkin ekle</span>
                                            </Button>
                                            <Button type="button" variant="secondary" className="h-10 gap-1.5 border border-border" onClick={() => addTraveler("child")} data-testid="add-child-traveler-button">
                                                <Plus className="h-4 w-4" />
                                                <Baby className="h-4 w-4" />
                                                <span>Çocuk ekle</span>
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
                                            const hasFieldErrors = Object.keys(te).length > 0;
                                            const passportRead = ocr[t.key]?.status === "done";
                                            const ocrAttempted = !!ocr[t.key] && ocr[t.key].status !== "loading";
                                            // Cinsiyet artik formda sorulmuyor; pasaport MRZ'sinden okunur.
                                            const passportComplete =
                                                !!t.first_name && !!t.last_name && !!t.birth_date && !!t.passport_no && !!t.passport_expiry;
                                            // OCR bilgileri eksiksiz doldurduysa alanlari ozet karta cevir;
                                            // hata varsa veya kullanici "Duzenle"ye bastiysa formu geri ac.
                                            const passportSummaryVisible =
                                                passportRead && passportComplete && !fieldsOpen[t.key] && !hasFieldErrors;
                                            // Pasaport daha yuklenmediyse bes alani bastan gostermeyiz; yukleme
                                            // kutusu yeter. Elle girmek isteyen tek dokunusla alanlari acar.
                                            const manualFieldsVisible =
                                                !passportSummaryVisible &&
                                                (fieldsOpen[t.key] || hasFieldErrors || ocrAttempted || passportComplete);
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
                                                            <div
                                                                className="mt-3 rounded-xl border border-[hsl(var(--brand-green)/0.35)] bg-[hsl(var(--brand-green)/0.07)] p-3.5"
                                                                data-testid={`traveler-${idx}-ocr-success`}
                                                            >
                                                                <p className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-wide text-[hsl(var(--brand-green))]">
                                                                    <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
                                                                    Pasaport okundu
                                                                </p>
                                                                <p className="mt-1.5 font-heading text-sm font-bold text-foreground">
                                                                    {ocr[t.key].name}
                                                                    {ocr[t.key].passport_no && (
                                                                        <span className="ml-2 font-mono-code text-xs font-semibold text-muted-foreground">
                                                                            {ocr[t.key].passport_no}
                                                                        </span>
                                                                    )}
                                                                </p>
                                                                <p className="mt-1 text-xs leading-5 text-muted-foreground">
                                                                    Aşağıdaki alanlar pasaporttaki bilgilerle güncellendi;
                                                                    lütfen kontrol edip gerekirse düzeltin.
                                                                </p>
                                                            </div>
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
                                                    ) : manualFieldsVisible ? (
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
                                                    ) : (
                                                        <button
                                                            type="button"
                                                            onClick={() => setFieldsOpen((o) => ({ ...o, [t.key]: true }))}
                                                            className="mt-4 inline-flex min-h-[44px] items-center gap-1.5 text-sm font-semibold text-primary underline-offset-4 hover:underline focus-visible:outline-none"
                                                            data-testid={`traveler-${idx}-manual-entry-button`}
                                                        >
                                                            <Pencil className="h-3.5 w-3.5" /> Pasaportum yanımda değil, bilgileri elle gireyim
                                                        </button>
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
                                    <h2 className="font-heading text-xl font-bold">
                                        {travelers.length > 1
                                            ? "Vize seçimi"
                                            : visaMissing
                                              ? "Vizenizi seçin"
                                              : "Vizenizi onaylayın"}
                                    </h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        {travelers.length > 1
                                            ? "Yolcularınız için vize türünü ve seyahat tarihlerinizi seçin."
                                            : "Vize türünüzü ve seyahat tarihlerinizi seçin, istersen yanına ek hizmet ekleyin."}
                                    </p>

                                    <div className="mt-6">
                                        <ImportantNotice compact />
                                    </div>


                                    {travelers.length > 1 ? (
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
                                    ) : visaMissing ? null : (
                                        <div
                                            className="mt-6 flex flex-wrap items-center gap-x-3 gap-y-1.5 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4 text-sm"
                                            data-testid="visa-step-selected-summary"
                                        >
                                            <FileCheck2 className="h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                            <span className="text-muted-foreground">Seçtiğiniz vize:</span>
                                            <strong data-testid="visa-step-selected-value">
                                                {primaryVisa ? primaryVisa.name : "Seçilmedi"}
                                            </strong>
                                            {primaryVisa && (
                                                <span className="font-heading font-bold">
                                                    {formatMoney(primaryVisa.price, primaryVisa.currency)}
                                                </span>
                                            )}
                                            {!visaMissing && (
                                                <button
                                                    type="button"
                                                    onClick={() => setVisaEditOpen((o) => !o)}
                                                    className="ml-auto text-xs font-semibold text-primary hover:underline"
                                                    data-testid="visa-step-change-visa-button"
                                                >
                                                    {visaEditOpen ? "Kapat" : "Değiştir"}
                                                </button>
                                            )}
                                        </div>
                                    )}

                                    {travelers.length <= 1 && (visaEditOpen || visaMissing) && (
                                        <div
                                            className="mt-3 rounded-xl border border-primary/25 bg-primary/[0.04] p-5"
                                            data-testid="visa-step-visa-editor"
                                        >
                                            <p className="font-heading text-sm font-bold">
                                                {visaMissing ? "Vize türünüzü seçin" : "Vize türünü değiştirin"}
                                            </p>
                                            <p className="mt-1 text-xs leading-5 text-muted-foreground">
                                                Listeden seçin ya da vizeleri karşılaştırın; fiyat ve öneriler anında
                                                güncellenir.
                                            </p>
                                            {visaPickerFields}
                                        </div>
                                    )}

                                    {!datesMissing && (
                                        <div
                                            className="mt-5 flex flex-wrap items-center gap-2 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4 text-sm"
                                            data-testid="visa-step-dates-summary"
                                        >
                                            <CalendarDays className="h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                            <span className="text-muted-foreground">Seyahat tarihleriniz:</span>
                                            <strong data-testid="visa-step-dates-value">
                                                {datesFlexible
                                                    ? travelWindowLabel || "Henüz belli değil"
                                                    : travel.arrival_date && travel.departure_date
                                                      ? `${formatDate(travel.arrival_date)} – ${formatDate(travel.departure_date)}${
                                                            tripDays ? ` · ${tripDays} gün` : ""
                                                        }`
                                                      : "Seçilmedi"}
                                            </strong>
                                            <button
                                                type="button"
                                                onClick={() => setDatesEditOpen((o) => !o)}
                                                className="ml-auto text-xs font-semibold text-primary hover:underline"
                                                data-testid="visa-step-edit-dates-button"
                                            >
                                                {datesEditOpen ? "Kapat" : "Tarihleri düzenle"}
                                            </button>
                                        </div>
                                    )}

                                    {(datesEditOpen || datesMissing) && (
                                        <div className="mt-1" data-testid="visa-step-dates-editor">
                                            {travelDatesEditor}
                                        </div>
                                    )}

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

                                    {insuranceBlock}
                                    {esimBlock}

                                </div>
                            )}

                            {/* STEP 2 */}
                            {step === 2 && (
                                <div data-testid="wizard-document-upload-dropzone">
                                    <h2 className="font-heading text-xl font-bold">Evraklar</h2>
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Pasaport ve vesikalık zorunlu. Belgeleriniz şifreli saklanır.</p>

                                    {errors.photo_quality && (
                                        <div
                                            className="mt-4 flex items-start gap-2 rounded-xl border border-destructive/40 bg-destructive/10 p-4"
                                            data-testid="photo-quality-block-warning"
                                        >
                                            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
                                            <p className="text-sm font-semibold leading-6 text-destructive">
                                                {errors.photo_quality}
                                            </p>
                                        </div>
                                    )}

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
                                                                hint="Bilgiler otomatik dolar"
                                                                badge="required"
                                                                icon={BookUser}
                                                                description="Pasaportunuzun kimlik bilgilerinin olduğu sayfası net şekilde yükleyin."
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
                                                                        Alanlar pasaporttaki bilgilerle güncellendi, kontrol edin.
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
                                                                hint="Otomatik kontrol edilir"
                                                                badge="required"
                                                                icon={Camera}
                                                                description="Beyaz veya beyaza yakın düz zeminde, son 6 ay içinde çekilmiş biyometrik fotoğraf."
                                                                docType="photo"
                                                                value={t.photoFile}
                                                                onInputRef={(el) => {
                                                                    photoInputs.current[t.key] = el;
                                                                }}
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
                                                                <PhotoRetryHelper
                                                                    testId={`traveler-${idx}-photo-check-warning`}
                                                                    result={photoCheck[t.key]}
                                                                    photoUrl={t.photoFile?.url}
                                                                    onRetry={() => photoInputs.current[t.key]?.click()}
                                                                />
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
                                            <p className="flex items-center gap-2 font-heading text-sm font-bold">
                                                <FileUp className="h-4 w-4 text-primary" />
                                                Seyahat evrakları
                                            </p>
                                            <p className="mt-1.5 text-xs leading-5 text-muted-foreground">
                                                Bu alanlar zorunlu değil: vizeniz çıkmadan uçak bileti veya otel
                                                rezervasyonu yapmanıza gerek yok. Elinizde varsa yükleyin, yoksa
                                                boş bırakıp devam edin.
                                            </p>
                                            <div className="mt-5 grid gap-6 md:grid-cols-2">
                                                <div>
                                                    <FileDropzone label="Uçak Bileti" hint="Varsa" badge="optional" icon={Plane} description="Dönüş biletiniz varsa ekleyin; zorunlu değildir." docType="ticket" value={extraDocs.ticket} onChange={(f) => setExtraDocs((s) => ({ ...s, ticket: f }))} testId="ticket-upload-input" />
                                                    {errors.ticket && (
                                                        <p className="mt-2 flex items-start gap-1.5 text-xs font-medium text-destructive" data-testid="ticket-upload-error">
                                                            <AlertCircle className="mt-0.5 h-3.5 w-3.5" /> {errors.ticket}
                                                        </p>
                                                    )}
                                                </div>
                                                <div>
                                                    <FileDropzone label="Otel Rezervasyonu" hint="Varsa" badge="optional" icon={Building2} description="Konaklama rezervasyonunuz varsa yükleyebilirsiniz." docType="hotel" value={extraDocs.hotel} onChange={(f) => setExtraDocs((s) => ({ ...s, hotel: f }))} testId="hotel-upload-input" />
                                                    {errors.hotel && (
                                                        <p className="mt-2 flex items-start gap-1.5 text-xs font-medium text-destructive" data-testid="hotel-upload-error">
                                                            <AlertCircle className="mt-0.5 h-3.5 w-3.5" /> {errors.hotel}
                                                        </p>
                                                    )}
                                                </div>
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

                                    {/* EKSTRA HIZMET ONERILERI: sigorta + eSIM + col safarisi */}
                                    {extrasSelectable && tripSuggestions.length > 0 && (
                                        <TripSuggestions
                                            suggestions={tripSuggestions}
                                            tripDays={tripDays}
                                            bundleActive={bundleActive}
                                        />
                                    )}

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
                                                    {!tripDays && datesFlexible && (
                                                        <p className="mt-2 text-sm text-muted-foreground" data-testid="bundle-flexible-note">
                                                            Tarihiniz henüz belli değil — <strong className="text-foreground">vize sürenize</strong> uygun paketleri listeledik.
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
                                                    disabled={!extrasSelectable || bundleActive}
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
                                    {insuranceBlock}
                                    {insurancePick && (
                                        <div className="mt-5" data-testid="insurance-identity-block">
                                            <p className="font-heading text-sm font-bold">
                                                Poliçe için kimlik bilgileri
                                            </p>
                                            <p className="mt-1 text-sm leading-6 text-muted-foreground">
                                                Sigorta şirketi poliçeyi TC kimlik numarasıyla düzenler.
                                                Pasaportunuzda yazıyorsa alan otomatik doldurulur; boşsa
                                                lütfen yazın.
                                            </p>
                                            <InsuredIdentityFields
                                                rows={insuredRows}
                                                onChange={(key, patch) =>
                                                    updateTraveler(key, { national_id: patch.tc_kimlik_no })
                                                }
                                                testIdPrefix="insured"
                                            />
                                        </div>
                                    )}

                                    {/* DUBAI eSIM (magaza katalogu) */}
                                    {esimBlock}

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
                                                <SummaryRow label="Cep Telefonu (WhatsApp)" value={contact.phone} />
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
                                                {travel.dates_unknown ? (
                                                    <SummaryRow
                                                        label="Seyahat tarihi"
                                                        value={`Henüz belli değil${travelWindowLabel ? ` · ${travelWindowLabel}` : ""}`}
                                                    />
                                                ) : (
                                                    <>
                                                        <SummaryRow label="Gidiş" value={formatDate(travel.arrival_date)} />
                                                        <SummaryRow label="Dönüş" value={formatDate(travel.departure_date)} />
                                                    </>
                                                )}
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
                                                    {quote.visa_insurance_discount > 0 && (
                                                        <SummaryRow
                                                            label={`${quote.visa_insurance_discount_title || "Sigorta dahil vize indirimi"} (%${Math.round((quote.visa_insurance_discount_rate || 0) * 100)})`}
                                                            value={`- ${formatMoney(quote.visa_insurance_discount, quote.currency)}`}
                                                        />
                                                    )}
                                                    {quote.bundle_discount > 0 && (
                                                        <SummaryRow
                                                            label={`${quote.bundle_discount_title || "Seyahat paketi indirimi"} (%${Math.round((quote.bundle_discount_rate || 0) * 100)})`}
                                                            value={`- ${formatMoney(quote.bundle_discount, quote.currency)}`}
                                                        />
                                                    )}
                                                    <SummaryRow label="Toplam" value={formatMoney(quote.total, quote.currency)} strong />
                                                    <SavingsNote quote={quote} testId="breakdown-total-savings" />
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {!created && (
                                        <div className="mt-6 space-y-3" data-testid="consent-block">
                                            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                                                <Checkbox checked={kvkk} onCheckedChange={(v) => setKvkk(!!v)} className="mt-0.5" data-testid="kvkk-checkbox" />
                                                <span className="text-sm leading-6">
                                                    <Link to="/kvkk" target="_blank" className="font-semibold text-primary hover:underline">
                                                        KVKK aydınlatma metnini
                                                    </Link>{" "}
                                                    okudum, bilgilerimin ve yüklediğim belgelerin vize başvurumun
                                                    hazırlanması amacıyla işlenmesini onaylıyorum.
                                                </span>
                                            </label>
                                            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                                                <Checkbox
                                                    checked={consents.refund_privacy_accepted}
                                                    onCheckedChange={(v) => setConsent("refund_privacy_accepted", !!v)}
                                                    className="mt-0.5"
                                                    data-testid="consent-refund-privacy-checkbox"
                                                />
                                                <span className="text-sm leading-6">
                                                    <Link to="/iade-kosullari" target="_blank" className="font-semibold text-primary hover:underline">
                                                        İade ve İptal Koşulları
                                                    </Link>{" "}
                                                    ile{" "}
                                                    <Link to="/gizlilik-politikasi" target="_blank" className="font-semibold text-primary hover:underline">
                                                        Gizlilik Politikası
                                                    </Link>
                                                    'nı okudum, kabul ediyorum.
                                                </span>
                                            </label>
                                            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                                                <Checkbox
                                                    checked={consents.service_terms_accepted}
                                                    onCheckedChange={(v) => setConsent("service_terms_accepted", !!v)}
                                                    className="mt-0.5"
                                                    data-testid="consent-service-terms-checkbox"
                                                />
                                                <span className="text-sm leading-6">
                                                    <Link to="/hizmet-sozlesmesi" target="_blank" className="font-semibold text-primary hover:underline">
                                                        Şartlar ve Mesafeli Hizmet Sözleşmesi
                                                    </Link>
                                                    'ni okudum, kabul ediyorum. Vize kararının resmî makamlara ait
                                                    olduğunu ve başvuru sisteme girildikten sonra harç iadesi
                                                    yapılmadığını biliyorum.
                                                </span>
                                            </label>
                                            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-dashed border-border p-4">
                                                <Checkbox
                                                    checked={consents.marketing_email_optin}
                                                    onCheckedChange={(v) => setConsent("marketing_email_optin", !!v)}
                                                    className="mt-0.5"
                                                    data-testid="consent-marketing-checkbox"
                                                />
                                                <span className="text-sm leading-6">
                                                    Kampanya ve fırsat bildirimleri almak istiyorum.{" "}
                                                    <Link to="/ticari-ileti-onami" target="_blank" className="font-semibold text-primary hover:underline">
                                                        Ticari Elektronik İleti Onam Formu
                                                    </Link>{" "}
                                                    <span className="text-muted-foreground">(isteğe bağlı)</span>
                                                </span>
                                            </label>
                                            <label className="flex cursor-pointer items-start gap-3 rounded-xl border border-dashed border-border p-4">
                                                <Checkbox
                                                    checked={consents.ad_personalization_optin}
                                                    onCheckedChange={(v) => setConsent("ad_personalization_optin", !!v)}
                                                    className="mt-0.5"
                                                    data-testid="consent-ads-checkbox"
                                                />
                                                <span className="text-sm leading-6">
                                                    Bana uygun Dubai fırsatlarını sosyal medyada görmek istiyorum.
                                                    <span className="mt-1 block text-xs leading-5 text-muted-foreground">
                                                        İletişim bilgim Instagram, Facebook ve Google'a şifrelenmiş
                                                        (hash) olarak iletilir; açık hâlde paylaşılmaz veya satılmaz.
                                                        İşaretlemeseniz de başvurunuz aynı şekilde tamamlanır.
                                                    </span>
                                                </span>
                                            </label>
                                        </div>
                                    )}

                                    {/* ÖDEME YÖNTEMİ */}
                                    <div className="mt-6" data-testid="payment-method-section">
                                        <h3 className="font-heading text-base font-bold">Ödeme yöntemi</h3>
                                        <SecurityMiniStrip className="mt-3" />
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
                                                    {!(transferInfo.bank?.banks || []).length && (
                                                        <>
                                                            <div className="flex justify-between gap-3">
                                                                <dt className="text-muted-foreground">Banka</dt>
                                                                <dd className="text-right font-semibold">{transferInfo.bank?.bank_name}</dd>
                                                            </div>
                                                            <div className="flex justify-between gap-3">
                                                                <dt className="text-muted-foreground">IBAN</dt>
                                                                <dd className="text-right font-mono-code font-semibold" data-testid="bank-transfer-iban">{transferInfo.bank?.iban}</dd>
                                                            </div>
                                                        </>
                                                    )}
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
                                                {(transferInfo.bank?.banks || []).length > 0 && (
                                                    <div className="mt-4">
                                                        <BankAccounts bank={transferInfo.bank} />
                                                    </div>
                                                )}
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
                            <div className="mt-8 flex flex-col-reverse gap-3 border-t border-border pt-6 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
                                <Button type="button" variant="secondary" className="h-11 w-full border border-border sm:w-auto" onClick={back} disabled={step === 0} data-testid="wizard-prev-step-button">
                                    <ArrowLeft className="mr-2 h-4 w-4" /> Geri
                                </Button>

                                <div className="flex flex-col-reverse gap-3 sm:flex-row sm:flex-wrap sm:items-center">
                                    <Button
                                        type="button"
                                        variant="secondary"
                                        className="h-11 w-full border border-border sm:w-auto"
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
                                        <Button type="button" className="h-12 w-full text-base sm:h-11 sm:w-auto sm:px-6 sm:text-sm" onClick={next} data-testid="wizard-next-step-button">
                                            Devam Et <ArrowRight className="ml-2 h-4 w-4" />
                                        </Button>
                                    ) : (
                                        <Button type="button" className="h-12 w-full px-7 text-base sm:w-auto" onClick={payMethod === "transfer" ? startBankTransfer : startPayment} disabled={submitting || paying} data-testid="wizard-pay-button">
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
                                <div className="mt-4">
                                    <FamilyDiscountMeter
                                        tiers={familyTiers}
                                        travelerCount={travelers.length}
                                        discountAmount={quote?.family_discount || 0}
                                        currency={quote?.currency || "TRY"}
                                        canAddTraveler={travelers.length < maxTravelers}
                                        onAddTraveler={() => addTraveler("adult")}
                                    />
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
                                        {quote.visa_insurance_discount > 0 && (
                                            <div
                                                className="flex justify-between text-[hsl(var(--brand-green))]"
                                                data-testid="summary-insurance-discount"
                                            >
                                                <span>
                                                    {quote.visa_insurance_discount_title || "Sigorta dahil vize indirimi"} (%
                                                    {Math.round((quote.visa_insurance_discount_rate || 0) * 100)})
                                                </span>
                                                <span className="font-semibold">
                                                    - {formatMoney(quote.visa_insurance_discount, quote.currency)}
                                                </span>
                                            </div>
                                        )}
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
                                            <SavingsNote quote={quote} testId="summary-total-savings" />
                                            <FxNote variant="inline" />
                                        </div>
                                    </div>
                                ) : (
                                    <p className="mt-4 border-t border-border pt-4 text-sm text-muted-foreground">
                                        Fiyat için vize türü seçin.
                                    </p>
                                )}
                            </div>

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
