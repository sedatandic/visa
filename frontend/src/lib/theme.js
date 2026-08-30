const STORAGE_KEY = "vizeatlas-theme";

export function getStoredTheme() {
    try {
        return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
        return null;
    }
}

export function resolveInitialTheme() {
    const stored = getStoredTheme();
    if (stored === "dark" || stored === "light") return stored;
    if (typeof window !== "undefined" && window.matchMedia) {
        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    return "light";
}

export function applyTheme(theme) {
    const root = document.documentElement;
    root.classList.toggle("dark", theme === "dark");
    root.style.colorScheme = theme;
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "dark" ? "#0D1115" : "#0B6B3A");
    try {
        localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
        /* storage kapali olabilir */
    }
}
