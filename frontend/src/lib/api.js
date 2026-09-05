import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({ baseURL: API });

api.interceptors.request.use((config) => {
    const url = config.url || "";
    const adminToken = localStorage.getItem("dv_admin_token");
    if (adminToken && url.startsWith("/admin")) {
        config.headers.Authorization = `Bearer ${adminToken}`;
        return config;
    }
    const customerToken = localStorage.getItem("dv_customer_token");
    if (customerToken && url.startsWith("/account")) {
        config.headers.Authorization = `Bearer ${customerToken}`;
    }
    return config;
});

export const customerAuth = {
    get token() {
        return localStorage.getItem("dv_customer_token");
    },
    get email() {
        return localStorage.getItem("dv_customer_email");
    },
    save(token, email) {
        localStorage.setItem("dv_customer_token", token);
        if (email) localStorage.setItem("dv_customer_email", email);
    },
    clear() {
        localStorage.removeItem("dv_customer_token");
        localStorage.removeItem("dv_customer_email");
    },
};

// Backend imzali dosya yollari uretir (/api/files/{id}?t=...). Burada yalniz tam
// adrese cevrilir; imzasiz istekler 403 doner.
export const fileUrl = (signedPath, download = false) => {
    if (!signedPath) return "";
    const url = signedPath.startsWith("http") ? signedPath : `${BACKEND_URL}${signedPath}`;
    if (!download) return url;
    return url.includes("download=1") ? url : `${url}${url.includes("?") ? "&" : "?"}download=1`;
};

export function apiError(err, fallback = "Bir hata oluştu. Lütfen tekrar deneyin.") {
    const detail = err?.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail) && detail.length) {
        const first = detail[0];
        return first?.msg ? `Form hatası: ${first.msg}` : fallback;
    }
    if (err?.message === "Network Error") return "Sunucuya ulaşılamadı. İnternet bağlantınızı kontrol edin.";
    return fallback;
}
