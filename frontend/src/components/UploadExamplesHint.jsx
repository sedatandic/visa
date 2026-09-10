import React, { useState } from "react";
import { Check, X } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { PHOTO_EXAMPLES, PhotoGuide } from "./PhotoGuide";
import { PASSPORT_EXAMPLES, PassportGuide } from "./PassportGuide";

const CONFIG = {
    passport: { examples: PASSPORT_EXAMPLES, title: "Pasaport taraması örnekleri", Guide: PassportGuide },
    photo: { examples: PHOTO_EXAMPLES, title: "Vesikalık örnekleri", Guide: PhotoGuide },
};

/** Yukleme kutusunun altinda kucuk dogru/yanlis onizlemeleri; tiklaninca buyuk rehber acilir. */
export const UploadExamplesHint = ({ type, testId }) => {
    const [open, setOpen] = useState(false);
    const { examples, title, Guide } = CONFIG[type];

    return (
        <>
            <button
                type="button"
                onClick={() => setOpen(true)}
                className="mt-2 flex w-full items-center gap-2.5 rounded-lg border border-border bg-card px-2.5 py-2 text-left transition-colors hover:border-primary/60"
                data-testid={testId}
            >
                <span className="flex gap-1.5">
                    {examples.map((ex) => (
                        <span
                            key={ex.src}
                            className={`relative block h-12 w-9 shrink-0 overflow-hidden rounded border-2 ${
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
                    <span className="block text-xs font-bold">Doğru / yanlış örnekler</span>
                    <span className="block text-[11px] leading-4 text-muted-foreground">
                        Büyütmek için tıklayın
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
