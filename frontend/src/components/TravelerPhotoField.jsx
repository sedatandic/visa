import React from "react";
import { AlertCircle, AlertTriangle, Camera, CheckCircle2, Loader2 } from "lucide-react";
import { FileDropzone } from "./FileDropzone";
import { PhotoRetryHelper } from "./PhotoRetryHelper";

/** Vesikalik yukleme + AI kalite kontrolu ve pasaportla yuz eslesme durumlari. */
export const TravelerPhotoField = ({
    idx,
    value,
    check,
    match,
    error,
    onChange,
    onInputRef,
    onRetry,
    description = "Beyaz veya beyaza yakın düz zeminde, son 6 ay içinde çekilmiş biyometrik fotoğraf. Gözlüksüz ve şapkasız olmalıdır.",
}) => (
    <div>
        <FileDropzone
            label="Vesikalık Fotoğraf"
            hint="Otomatik kontrol edilir"
            badge="required"
            icon={Camera}
            description={description}
            docType="photo"
            value={value}
            onInputRef={onInputRef}
            onChange={onChange}
            testId={`traveler-${idx}-photo-upload-input`}
        />
        {check?.status === "loading" && (
            <p
                className="mt-2 flex items-center gap-2 text-xs font-medium text-primary"
                data-testid={`traveler-${idx}-photo-check-loading`}
            >
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Fotoğraf kontrol ediliyor...
            </p>
        )}
        {check?.status === "ok" && (
            <p
                className="mt-2 flex items-center gap-2 text-xs font-semibold text-[hsl(var(--brand-green))]"
                data-testid={`traveler-${idx}-photo-check-ok`}
            >
                <CheckCircle2 className="h-3.5 w-3.5" />
                Fotoğraf vize standartlarına uygun görünüyor.
            </p>
        )}
        {check?.status === "warn" && (
            <PhotoRetryHelper
                testId={`traveler-${idx}-photo-check-warning`}
                result={check}
                photoUrl={value?.url}
                onRetry={onRetry}
            />
        )}
        {match?.status === "loading" && (
            <p
                className="mt-2 flex items-center gap-2 text-xs font-medium text-primary"
                data-testid={`traveler-${idx}-face-match-loading`}
            >
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Pasaporttaki fotoğrafla karşılaştırılıyor...
            </p>
        )}
        {match?.status === "ok" && (
            <p
                className="mt-2 flex items-center gap-2 text-xs font-semibold text-[hsl(var(--brand-green))]"
                data-testid={`traveler-${idx}-face-match-ok`}
            >
                <CheckCircle2 className="h-3.5 w-3.5" />
                Vesikalık, pasaporttaki kişiyle uyumlu görünüyor.
            </p>
        )}
        {match?.status === "mismatch" && (
            <div
                className="mt-2 flex items-start gap-2 rounded-lg border border-[hsl(var(--status-warning)/0.4)] bg-[hsl(var(--status-warning)/0.1)] p-3"
                data-testid={`traveler-${idx}-face-match-warning`}
            >
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--status-warning))]" />
                <div className="text-xs leading-5">
                    <p className="font-semibold text-[hsl(var(--status-warning))]">
                        Pasaporttaki fotoğraf ile vesikalık eşleşmiyor gibi görünüyor.
                    </p>
                    <p className="mt-0.5 text-muted-foreground">
                        {match.note || "Doğru kişinin vesikalık fotoğrafını yüklediğinizden emin olun."}
                    </p>
                </div>
            </div>
        )}
        {error && (
            <p className="mt-2 flex items-start gap-1.5 text-xs font-medium text-destructive">
                <AlertCircle className="mt-0.5 h-3.5 w-3.5" /> {error}
            </p>
        )}
    </div>
);
