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
                      ? "h-[43px] w-auto shrink-0 object-contain min-[390px]:h-12 min-[430px]:h-[53px]"
                      : "h-11 w-auto shrink-0 object-contain min-[420px]:h-14 min-[560px]:h-[67px] sm:h-[77px] lg:h-24 xl:h-[88px] min-[1400px]:h-24"
            }
            width="929"
            height="260"
            loading="eager"
            decoding="async"
        />
    </span>
);
