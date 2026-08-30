import React from "react";
import { COMPANY } from "../lib/site";

export const BrandMark = ({ light = false }) => (
    <>
        <span
            className="relative flex h-9 w-9 items-center justify-center overflow-hidden rounded-md bg-primary"
            aria-hidden="true"
        >
            <span className="absolute left-0 top-0 h-full w-1.5 bg-[hsl(var(--brand-red))]" />
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round">
                <path d="M4 21V11a8 8 0 0 1 16 0v10" />
                <path d="M8.5 13.5 11 16l4.5-5" />
            </svg>
        </span>
        <span className="flex flex-col leading-none">
            <span
                className={`font-heading text-[18px] font-bold tracking-tight ${light ? "text-white" : "text-foreground"}`}
            >
                {COMPANY.brand}
                <span className="text-[hsl(var(--brand-red))]">.</span>
            </span>
            <span
                className={`text-[10px] font-semibold uppercase tracking-[0.18em] ${
                    light ? "text-white/60" : "text-muted-foreground"
                }`}
            >
                {COMPANY.brandSuffix} Vize
            </span>
        </span>
    </>
);
