import React from "react";
import { ShieldCheck } from "lucide-react";
import { UaeFlag } from "./FlagIcons";

/**
 * Gercek bir BAE e-vizesinin (giris izni) ornek gorunumu.
 * Tum kisisel bilgiler bulaniklastirilmis, uzerine "ORNEKTIR" filigrani eklenmistir.
 */
export const SampleVisa = ({ className = "" }) => (
    <figure
        className={`relative overflow-hidden rounded-2xl border border-border bg-card ${className}`}
        style={{ boxShadow: "var(--shadow-soft)" }}
        data-testid="sample-visa-document"
    >
        <div className="flag-strip" aria-hidden="true" />

        <div className="flex items-center justify-between gap-3 border-b border-border px-5 py-4">
            <div className="flex items-center gap-3">
                <UaeFlag className="h-7 w-11" />
                <div>
                    <p className="font-heading text-[13px] font-extrabold leading-tight">
                        UNITED ARAB EMIRATES
                    </p>
                    <p className="text-[11px] leading-tight text-muted-foreground">
                        Entry Permit / Giriş İzni — eVisa
                    </p>
                </div>
            </div>
            <span className="rounded-full bg-[hsl(var(--brand-copper)/0.10)] px-3 py-1 text-[10px] font-extrabold uppercase tracking-wider text-[hsl(var(--brand-copper))]">
                Örnektir
            </span>
        </div>

        <div className="bg-muted/40 p-4">
            <img
                src="/ornek-vize.jpg"
                alt="Örnek Birleşik Arap Emirlikleri e-vizesi; kişisel bilgiler bulanıklaştırılmıştır"
                className="mx-auto w-full max-w-[520px] rounded-lg border border-border bg-white"
                loading="lazy"
                data-testid="sample-visa-image"
            />
        </div>

        <figcaption className="flex items-start gap-2 border-t border-border bg-muted/50 px-5 py-3">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
            <p className="text-xs leading-5 text-muted-foreground">
                Onaylanan vizeniz bu düzende, PDF olarak e-postanıza ve başvuru takip sayfanıza
                yüklenir. Yukarıdaki belge tanıtım amaçlıdır; kişisel bilgiler gizlenmiştir.
            </p>
        </figcaption>
    </figure>
);
