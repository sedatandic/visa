import React from "react";
import { COMPANY } from "../lib/site";

const BRAND_NAME = `${COMPANY.brand} ${COMPANY.brandSuffix}`.trim();

/** Marka işareti: orijinal yatay logo kilidi (amblem + DUBAI Vize Online). */
export const BrandMark = ({ light = false }) => (
    <span className="flex items-center" data-testid="brand-mark">
        <img
            src="/brand/logo-horizontal.png"
            alt={BRAND_NAME}
            className={
                light
                    ? "h-16 w-auto shrink-0 rounded-lg bg-white/95 object-contain px-2 py-1 shadow-sm sm:h-20"
                    : "h-16 w-auto shrink-0 object-contain sm:h-20"
            }
            width="929"
            height="260"
            loading="eager"
            decoding="async"
        />
    </span>
);
