import React from "react";

/** Birleşik Arap Emirlikleri bayrağı */
export const UaeFlag = ({ className = "h-5 w-8", title = "Birleşik Arap Emirlikleri bayrağı" }) => (
    <svg
        viewBox="0 0 60 30"
        role="img"
        aria-label={title}
        className={`shrink-0 rounded-[3px] ring-1 ring-black/10 ${className}`}
        data-testid="uae-flag-icon"
    >
        <title>{title}</title>
        <rect width="60" height="10" y="0" fill="#00732F" />
        <rect width="60" height="10" y="10" fill="#FFFFFF" />
        <rect width="60" height="10" y="20" fill="#000000" />
        <rect width="15" height="30" fill="#C8102E" />
    </svg>
);

/** Türkiye bayrağı */
export const TrFlag = ({ className = "h-5 w-8", title = "Türkiye bayrağı" }) => (
    <svg
        viewBox="0 0 60 40"
        role="img"
        aria-label={title}
        className={`shrink-0 rounded-[3px] ring-1 ring-black/10 ${className}`}
        data-testid="tr-flag-icon"
    >
        <title>{title}</title>
        <rect width="60" height="40" fill="#E30A17" />
        <circle cx="23" cy="20" r="9" fill="#fff" />
        <circle cx="26" cy="20" r="7.2" fill="#E30A17" />
        <path
            fill="#fff"
            d="M34.4 20l6.4-2.1-3.9 5.4v-6.6l3.9 5.4z"
        />
    </svg>
);

export const RouteFlags = ({ className = "" }) => (
    <span className={`inline-flex items-center gap-2 ${className}`} data-testid="route-flags">
        <TrFlag className="h-4 w-6" />
        <span className="text-xs font-semibold text-muted-foreground">Türkiye → BAE</span>
        <UaeFlag className="h-4 w-6" />
    </span>
);
