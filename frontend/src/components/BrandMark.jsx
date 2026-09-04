import React from "react";
import { COMPANY } from "../lib/site";

const BRAND_NAME = `${COMPANY.brand} ${COMPANY.brandSuffix}`.trim();

/**
 * Marka işareti: logodan kesilmiş ikon (deve + skyline) + logo tipografisini
 * yansıtan yazı (bakır serif "DUBAI" + petrol teal "Vize Online").
 * Koyu zeminlerde (`light`) yazı beyaza döner.
 */
export const BrandMark = ({ light = false }) => (
    <span className="flex items-center gap-2.5" data-testid="brand-mark">
        <img
            src="/brand/emblem-512.png"
            alt=""
            aria-hidden="true"
            className={
                light
                    ? "h-10 w-auto shrink-0 rounded-lg bg-white/95 object-contain px-1.5 py-1 shadow-sm"
                    : "h-10 w-auto shrink-0 object-contain"
            }
            width="1060"
            height="555"
            loading="eager"
            decoding="async"
        />
        <span className="flex flex-col leading-none">
            <span
                className={`font-heading text-[20px] font-bold uppercase leading-none tracking-[0.11em] ${
                    light ? "text-white" : "text-[hsl(var(--brand-copper))]"
                }`}
            >
                {COMPANY.brand.replace(" Vize", "")}
            </span>
            <span
                className={`font-heading text-[13.5px] font-bold leading-tight tracking-[0.01em] ${
                    light ? "text-white/80" : "text-primary"
                }`}
            >
                Vize {COMPANY.brandSuffix}
            </span>
        </span>
        <span className="sr-only">{BRAND_NAME}</span>
    </span>
);
