import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({ baseURL: API });

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("dv_admin_token");
    if (token && config.url && config.url.startsWith("/admin")) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const fileUrl = (fileId) => `${API}/files/${fileId}`;

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
