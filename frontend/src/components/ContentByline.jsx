import React from "react";
import { CalendarDays, PenLine, ShieldAlert } from "lucide-react";
import { AGENCY_DISCLAIMER, CONTENT_AUTHOR, CONTENT_UPDATED_AT, OFFICIAL_SOURCES } from "../lib/site";

/**
 * Icerik kunyesi: hazirlayan, son guncelleme ve resmi kaynaklar.
 * Google'in guvenilirlik (E-E-A-T) sinyalleri ve yasal acente uyarisi icin.
 */
export const ContentByline = ({ updated = CONTENT_UPDATED_AT, author = CONTENT_AUTHOR, className = "" }) => (
    <div
        className={`rounded-xl border border-border bg-[hsl(var(--cloud))] px-5 py-4 ${className}`}
        data-testid="content-byline"
    >
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
                <PenLine className="h-3.5 w-3.5 text-primary" />
                Hazırlayan: <strong className="font-semibold text-foreground">{author}</strong>
            </span>
            <span className="inline-flex items-center gap-1.5" data-testid="content-updated-at">
                <CalendarDays className="h-3.5 w-3.5 text-primary" />
                Son güncelleme: <strong className="font-semibold text-foreground">{updated}</strong>
            </span>
            <span className="inline-flex items-center gap-1.5">
                Resmî kaynaklar:
                {OFFICIAL_SOURCES.map((s) => (
                    <a
                        key={s.href}
                        href={s.href}
                        target="_blank"
                        rel="noreferrer nofollow"
                        className="font-semibold text-primary underline-offset-2 hover:underline"
                    >
                        {s.label}
                    </a>
                ))}
            </span>
        </div>
        <p className="mt-3 flex items-start gap-2 text-xs leading-5 text-muted-foreground">
            <ShieldAlert className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[hsl(var(--gold))]" />
            {AGENCY_DISCLAIMER}
        </p>
    </div>
);
