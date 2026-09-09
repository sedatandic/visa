export const IMAGES = {
    heroSkyline:
        "https://images.unsplash.com/photo-1580674684081-7617fbf3d745?auto=format&fit=crop&w=1400&q=75",
    dubaiHighway:
        "https://images.unsplash.com/photo-1656994865204-9646ebddd2cb?auto=format&fit=crop&w=1100&q=75",
    burjAlArabAerial:
        "https://images.unsplash.com/photo-1518684079-3c830dcef090?auto=format&fit=crop&w=900&q=75",
    burjAlArabBeach:
        "https://images.unsplash.com/photo-1546412414-e1885259563a?auto=format&fit=crop&w=900&q=75",
    dubaiNight:
        "https://images.unsplash.com/photo-1526495124232-a04e1849168c?auto=format&fit=crop&w=900&q=75",
    office:
        "https://images.unsplash.com/photo-1704655295066-681e61ecca6b?auto=format&fit=crop&w=1100&q=75",
    passportDocs:
        "https://images.unsplash.com/photo-1491317079341-38313806b657?auto=format&fit=crop&w=1000&q=75",
    travelFlatlay:
        "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1000&q=75",
    plane:
        "https://images.unsplash.com/photo-1540339832862-474599807836?auto=format&fit=crop&w=900&q=75",
    travelInsurance: "/images/turk-pasaport-dubai-binis-karti.jpg",
};

export const STATUS_META = {
    submitted: { label: "Başvuru Alındı", className: "bg-[hsl(var(--status-info)/0.12)] text-[hsl(var(--status-info))] border-[hsl(var(--status-info)/0.30)]" },
    payment_pending: { label: "Ödeme Bekleniyor", className: "bg-[hsl(var(--status-warning)/0.15)] text-[hsl(var(--status-warning))] border-[hsl(var(--status-warning)/0.35)]" },
    documents_pending: { label: "Belge Bekleniyor", className: "bg-[hsl(var(--status-warning)/0.15)] text-[hsl(var(--status-warning))] border-[hsl(var(--status-warning)/0.35)]" },
    reviewing: { label: "İnceleniyor", className: "bg-[hsl(var(--status-info)/0.14)] text-[hsl(var(--status-info))] border-[hsl(var(--status-info)/0.35)]" },
    approved: { label: "Onaylandı", className: "bg-[hsl(var(--brand-green)/0.13)] text-[hsl(var(--brand-green))] border-[hsl(var(--brand-green)/0.35)]" },
    rejected: { label: "Reddedildi", className: "bg-[hsl(var(--brand-red)/0.11)] text-[hsl(var(--brand-red))] border-[hsl(var(--brand-red)/0.30)]" },
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

/** Yasal konum uyarisi: her icerik sayfasinda ve alt bilgide gosterilir. */
export const AGENCY_DISCLAIMER =
    "Yetkili özel seyahat acentesiyiz; resmî bir devlet kurumu, konsolosluk ya da BAE göç idaresi değiliz. " +
    "Başvurunuzu sizin adınıza hazırlayıp yetkili mercilere iletiriz.";

/** Icerik kunyesi bilgileri (E-E-A-T sinyalleri). */
export const CONTENT_AUTHOR = "Dubai Vize Hattı Vize Ekibi";
export const CONTENT_UPDATED_AT = "Haziran 2026";
export const OFFICIAL_SOURCES = [
    { label: "gdrfad.gov.ae", href: "https://gdrfad.gov.ae/" },
    { label: "icp.gov.ae", href: "https://icp.gov.ae/" },
];

export const COMPANY = {
    brand: "Dubai Vize",
    brandSuffix: "Hattı",
    phone: "+90 850 000 00 00",
    phoneHref: "tel:+908500000000",
    whatsapp: "908500000000",
    email: "info@dubaivizehatti.com",
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

/** USD baz fiyat gosterimi: "≈ 110 $" */
export function formatUsd(amount, { approx = true } = {}) {
    if (amount === null || amount === undefined || amount === "") return "-";
    const value = Number(amount);
    const formatted = value.toLocaleString("tr-TR", {
        minimumFractionDigits: value % 1 === 0 ? 0 : 2,
        maximumFractionDigits: 2,
    });
    return `${approx ? "≈ " : ""}${formatted} $`;
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

/** Kanonik alan adi: www/www'suz kopyalarin ayni sayfa sayilmasi icin sabit tutulur. */
export const SITE_URL = (process.env.REACT_APP_SITE_URL || "https://www.dubaivizehatti.com").replace(/\/+$/, "");

const BRAND_TITLE = "Dubai Vize Hattı";

/** Title 60 karakteri gecmesin: marka eki sigmiyorsa dusurulur. */
export function withBrandTitle(title) {
    const full = `${title} | ${BRAND_TITLE}`;
    if (full.length <= 60) return full;
    if (title.length <= 60) return title;
    const cut = title.slice(0, 59);
    const space = cut.lastIndexOf(" ");
    return `${cut.slice(0, space > 30 ? space : 59)}…`;
}

const upsertMeta = (attr, key, content) => {
    let tag = document.querySelector(`meta[${attr}="${key}"]`);
    if (!tag) {
        tag = document.createElement("meta");
        tag.setAttribute(attr, key);
        document.head.appendChild(tag);
    }
    tag.setAttribute("content", content);
};

export function setMeta(title, description, options = {}) {
    document.title = title;
    upsertMeta("name", "description", description);

    const path = options.canonicalPath || window.location.pathname;
    const url = `${SITE_URL}${path === "/" ? "/" : path.replace(/\/+$/, "")}`;
    let link = document.querySelector('link[rel="canonical"]');
    if (!link) {
        link = document.createElement("link");
        link.setAttribute("rel", "canonical");
        document.head.appendChild(link);
    }
    link.setAttribute("href", url);

    upsertMeta("name", "robots", options.noindex ? "noindex, nofollow" : "index, follow");

    const image = options.image || `${SITE_URL}/brand/logo-horizontal-gold-palm.png`;
    upsertMeta("property", "og:site_name", BRAND_TITLE);
    upsertMeta("property", "og:title", title);
    upsertMeta("property", "og:description", description);
    upsertMeta("property", "og:type", options.ogType || "website");
    upsertMeta("property", "og:url", url);
    upsertMeta("property", "og:locale", "tr_TR");
    upsertMeta("property", "og:image", image);
    upsertMeta("name", "twitter:card", "summary_large_image");
    upsertMeta("name", "twitter:title", title);
    upsertMeta("name", "twitter:description", description);
    upsertMeta("name", "twitter:image", image);
}

/** SEO dostu basvuru adresi: /basvuru/pack-family/visa-30-single */
export function applyPath({ paket, vize, query } = {}) {
    const seg = (id) => String(id).replace(/_/g, "-");
    const segments = [paket && seg(paket), vize && seg(vize)].filter(Boolean);
    const qs = query ? `?${query}` : "";
    return `/basvuru${segments.length ? `/${segments.join("/")}` : ""}${qs}`;
}

/** /basvuru/<paket>/<vize> yol parcalarini id'lere cevirir. */
export function parseApplyPath(...segments) {
    const out = { paket: null, vize: null };
    segments.filter(Boolean).forEach((segment) => {
        const id = String(segment).replace(/-/g, "_");
        if (id.startsWith("pack")) out.paket = id;
        else if (id.startsWith("visa")) out.vize = id;
    });
    return out;
}

/** Sayfaya JSON-LD yapisal veri ekler (varsa gunceller). */
export function setJsonLd(id, data) {
    const elementId = `jsonld-${id}`;
    let script = document.getElementById(elementId);
    if (!data) {
        if (script) script.remove();
        return;
    }
    if (!script) {
        script = document.createElement("script");
        script.type = "application/ld+json";
        script.id = elementId;
        document.head.appendChild(script);
    }
    script.textContent = JSON.stringify(data);
}
