import React, { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { applyTheme, resolveInitialTheme } from "../lib/theme";

export const ThemeToggle = ({ className = "" }) => {
    const [theme, setTheme] = useState(() => resolveInitialTheme());

    useEffect(() => {
        applyTheme(theme);
    }, [theme]);

    const isDark = theme === "dark";

    return (
        <button
            type="button"
            role="switch"
            aria-checked={isDark}
            aria-label={isDark ? "Aydinlik temaya gec" : "Koyu temaya gec"}
            title={isDark ? "Aydınlık tema" : "Koyu tema"}
            onClick={() => setTheme(isDark ? "light" : "dark")}
            data-testid="theme-toggle-button"
            className={`flex h-11 w-11 items-center justify-center rounded-lg border border-border bg-card text-foreground/80 transition-colors duration-150 hover:border-primary/50 hover:text-primary ${className}`}
        >
            {isDark ? <Sun className="h-[18px] w-[18px]" /> : <Moon className="h-[18px] w-[18px]" />}
            <span className="sr-only" data-testid="theme-toggle-state">
                {isDark ? "dark" : "light"}
            </span>
        </button>
    );
};
