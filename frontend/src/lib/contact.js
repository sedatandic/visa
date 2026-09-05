import { useEffect, useState } from "react";
import { api } from "./api";
import { COMPANY } from "./site";

/**
 * Iletisim bilgileri tek kaynaktan: Admin > Acente Bilgileri (DB).
 * Panelde girilen deger varsa o kullanilir, yoksa statik yedek (COMPANY).
 * Boylece canliya cikista telefon/e-posta/adres kod degisikligi olmadan
 * panelden guncellenebilir.
 */

// Yedek olarak SADECE calisma saatleri ve kurumsal e-posta kullanilir.
// Telefon/WhatsApp/adres icin ornek (placeholder) deger GOSTERILMEZ: yanlis
// numara gostermek yerine alan gizlenir; admin panelden girilince gorunur.
const FALLBACK = {
    phone: "",
    whatsapp: "",
    email: COMPANY.email,
    address: "",
    workingHours: COMPANY.workingHours,
};

let cache = null;
let inflight = null;
const listeners = new Set();

const normalize = (company) => {
    const pick = (key, fallback) => {
        const value = String(company?.[key] ?? "").trim();
        return value || fallback;
    };
    const phone = pick("phone", FALLBACK.phone);
    const dubaiPhone = String(company?.dubai_phone ?? "").trim();
    const whatsapp = pick("whatsapp", FALLBACK.whatsapp).replace(/\D/g, "");
    return {
        phone,
        phoneHref: `tel:${phone.replace(/[^\d+]/g, "")}`,
        dubaiPhone,
        dubaiPhoneHref: dubaiPhone ? `tel:${dubaiPhone.replace(/[^\d+]/g, "")}` : "",
        dubaiAddress: String(company?.dubai_address ?? "").trim(),
        whatsapp,
        whatsappHref: whatsapp ? `https://wa.me/${whatsapp}` : "",
        email: pick("email", FALLBACK.email),
        instagram: String(company?.instagram ?? "").trim(),
        googleReview: String(company?.google_review ?? "").trim(),
        address: pick("address", FALLBACK.address),
        workingHours: pick("working_hours", FALLBACK.workingHours),
    };
};

export const contactFallback = normalize({});

const load = () => {
    if (cache) return Promise.resolve(cache);
    if (!inflight) {
        inflight = api
            .get("/content/site")
            .then(({ data }) => {
                cache = normalize(data?.company);
                return cache;
            })
            .catch(() => {
                cache = contactFallback;
                return cache;
            })
            .finally(() => {
                inflight = null;
                listeners.forEach((fn) => fn(cache));
            });
    }
    return inflight;
};

/** Iletisim bilgilerini dondurur; ilk render'da yedek degerler gelir. */
export const useContact = () => {
    const [contact, setContact] = useState(cache || contactFallback);

    useEffect(() => {
        let alive = true;
        const listener = (next) => {
            if (alive && next) setContact(next);
        };
        listeners.add(listener);
        load().then(listener);
        return () => {
            alive = false;
            listeners.delete(listener);
        };
    }, []);

    return contact;
};

/** WhatsApp mesaj linki uretir. */
export const waLink = (contact, text) =>
    contact?.whatsapp ? `https://wa.me/${contact.whatsapp}?text=${encodeURIComponent(text)}` : "";
