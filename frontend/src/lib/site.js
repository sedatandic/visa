export const IMAGES = {
    heroSkyline:
        "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=1400&q=75",
    burjAlArabAerial:
        "https://images.unsplash.com/photo-1518684079-3c830dcef090?auto=format&fit=crop&w=900&q=75",
    burjAlArabBeach:
        "https://images.unsplash.com/photo-1546412414-e1885259563a?auto=format&fit=crop&w=900&q=75",
    dubaiNight:
        "https://images.unsplash.com/photo-1526495124232-a04e1849168c?auto=format&fit=crop&w=900&q=75",
    travelFlatlay:
        "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1000&q=75",
    plane:
        "https://images.unsplash.com/photo-1540339832862-474599807836?auto=format&fit=crop&w=900&q=75",
};

export const STATUS_META = {
    submitted: { label: "Başvuru Alındı", className: "bg-[rgba(14,165,164,0.14)] text-[#0B5F5E] border-[rgba(14,165,164,0.3)]" },
    payment_pending: { label: "Ödeme Bekleniyor", className: "bg-[rgba(245,158,11,0.18)] text-[#7A4B00] border-[rgba(245,158,11,0.35)]" },
    documents_pending: { label: "Belge Bekleniyor", className: "bg-[rgba(245,158,11,0.18)] text-[#7A4B00] border-[rgba(245,158,11,0.35)]" },
    reviewing: { label: "İnceleniyor", className: "bg-[rgba(14,165,164,0.16)] text-[#0B5F5E] border-[rgba(14,165,164,0.35)]" },
    approved: { label: "Onaylandı", className: "bg-[rgba(22,163,74,0.16)] text-[#14532D] border-[rgba(22,163,74,0.35)]" },
    rejected: { label: "Reddedildi", className: "bg-[rgba(220,38,38,0.14)] text-[#7F1D1D] border-[rgba(220,38,38,0.3)]" },
    cancelled: { label: "İptal Edildi", className: "bg-muted text-foreground border-border" },
};

export const STATUS_OPTIONS = [
    "submitted",
    "documents_pending",
    "reviewing",
    "approved",
    "rejected",
    "cancelled",
];

export const PURPOSE_LABELS = {
    tourism: "Turistik gezi",
    business: "İş seyahati",
    family: "Aile / arkadaş ziyareti",
    transit: "Transit geçiş",
    other: "Diğer",
};

export const PURPOSES = Object.entries(PURPOSE_LABELS).map(([value, label]) => ({ value, label }));

export const COMPANY = {
    brand: "VizeAtlas",
    brandSuffix: "Dubai",
    phone: "+90 850 000 00 00",
    phoneHref: "tel:+908500000000",
    whatsapp: "908500000000",
    email: "destek@vizeatlas.com",
    address: "Levent, İstanbul / Türkiye",
    workingHours: "Hafta içi 09:00 - 19:00 · Cumartesi 10:00 - 16:00",
};

export function formatMoney(amount, currency = "TRY") {
    if (amount === null || amount === undefined) return "-";
    const value = Number(amount);
    const formatted = value.toLocaleString("tr-TR", {
        minimumFractionDigits: value % 1 === 0 ? 0 : 2,
        maximumFractionDigits: 2,
    });
    const cur = (currency || "TRY").toUpperCase();
    return `${formatted} ${cur === "TRY" ? "₺" : cur}`;
}

export function formatDate(value) {
    if (!value) return "-";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return value;
    return d.toLocaleDateString("tr-TR", { day: "2-digit", month: "long", year: "numeric" });
}

export function formatDateTime(value) {
    if (!value) return "-";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return value;
    return d.toLocaleString("tr-TR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

export function setMeta(title, description) {
    document.title = title;
    let tag = document.querySelector('meta[name="description"]');
    if (!tag) {
        tag = document.createElement("meta");
        tag.setAttribute("name", "description");
        document.head.appendChild(tag);
    }
    tag.setAttribute("content", description);
}
