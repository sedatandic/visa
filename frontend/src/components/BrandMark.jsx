import React from "react";
import { COMPANY } from "../lib/site";

const BRAND_NAME = `${COMPANY.brand} ${COMPANY.brandSuffix}`.trim();

/** Marka işareti: yatay logo kilidi (amblem + DUBAI Vize Hattı). */
export const BrandMark = ({ light = false, compact = false }) => (
    <span className="flex items-center" data-testid="brand-mark">
        <img
            src="/brand/logo-horizontal-gold-palm.png"
            alt={BRAND_NAME}
            className={
                light
                    ? "h-16 w-auto shrink-0 rounded-lg bg-white/95 object-contain px-2 py-1 shadow-sm sm:h-20"
                    : compact
                      ? "h-7 w-auto shrink-0 object-contain min-[390px]:h-8 min-[430px]:h-9"
                      : "h-11 w-auto shrink-0 object-contain min-[420px]:h-14 sm:h-16 lg:h-20"
            }
            width="929"
            height="260"
            loading="eager"
            decoding="async"
        />
    </span>
);
