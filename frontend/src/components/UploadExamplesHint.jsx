import React, { useState } from "react";
import { Check, X } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { PHOTO_EXAMPLES, PhotoGuide } from "./PhotoGuide";
import { PASSPORT_EXAMPLES, PassportGuide } from "./PassportGuide";

const CONFIG = {
    passport: {
        examples: PASSPORT_EXAMPLES,
        title: "Pasaport taraması örnekleri",
        Guide: PassportGuide,
        warningTitle: "Pasaport okunamadı",
    },
    photo: {
        examples: PHOTO_EXAMPLES,
        title: "Vesikalık örnekleri",
        Guide: PhotoGuide,
        warningTitle: "Fotoğraf uygun bulunmadı",
    },
};

/** Yalnizca belge okunamadiginda uyari olarak cikar; tiklaninca buyuk rehber acilir. */
export const UploadExamplesHint = ({ type, testId, warning = false, warningTitle: titleOverride }) => {
    const [open, setOpen] = useState(false);
    const { examples, title, Guide } = CONFIG[type];
    const warningTitle = titleOverride || CONFIG[type].warningTitle;

    return (
        <>
            <button
                type="button"
                onClick={() => setOpen(true)}
                className={`mt-2 flex w-full items-center gap-3 rounded-lg border px-2.5 py-2.5 text-left transition-colors sm:gap-2.5 sm:py-2 ${
                    warning
                        ? "border-amber-400/70 bg-amber-50 hover:border-amber-500"
                        : "border-border bg-card hover:border-primary/60"
                }`}
                data-testid={testId}
            >
                <span className="grid grid-cols-2 gap-1.5 sm:flex">
                    {examples.map((ex) => (
                        <span
                            key={ex.src}
                            className={`relative block h-16 w-12 shrink-0 overflow-hidden rounded border-2 sm:h-12 sm:w-9 ${
                                ex.good ? "border-[hsl(var(--brand-green))]" : "border-destructive/60"
                            }`}
                        >
                            <img src={ex.src} alt={ex.note} loading="lazy" className="h-full w-full object-cover" />
                            <span
                                className={`absolute right-0 top-0 flex h-3.5 w-3.5 items-center justify-center rounded-bl text-white ${
                                    ex.good ? "bg-[hsl(var(--brand-green))]" : "bg-destructive"
                                }`}
                            >
                                {ex.good ? <Check className="h-2.5 w-2.5" /> : <X className="h-2.5 w-2.5" />}
                            </span>
                        </span>
                    ))}
                </span>
                <span className="min-w-0 flex-1">
                    <span
                        className={`block text-sm font-bold sm:text-xs ${warning ? "text-amber-900" : ""}`}
                    >
                        {warning ? warningTitle : "Doğru / yanlış örnekler"}
                    </span>
                    <span className="block text-xs leading-4 text-muted-foreground sm:text-[11px]">
                        {warning ? "Doğru / yanlış örnekleri inceleyin" : "Büyütmek için dokunun"}
                    </span>
                </span>
            </button>

            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent className="max-w-3xl" data-testid={`${testId}-dialog`}>
                    <DialogHeader>
                        <DialogTitle>{title}</DialogTitle>
                    </DialogHeader>
                    <Guide testId={`${testId}-dialog-guide`} />
                </DialogContent>
            </Dialog>
        </>
    );
};
