import React, { useState } from "react";
import { AlertCircle, Camera, RefreshCw, X } from "lucide-react";
import { fileUrl } from "../lib/api";
import { Button } from "./ui/button";
import { PhotoGuide } from "./PhotoGuide";

const STEPS = [
    "Beyaz ya da açık renkli düz bir duvarın önüne geçin; arkanızda eşya veya başka kişi olmasın.",
    "Telefonu omuz hizasında, tam karşınızda ve bir kol mesafesinde tutun.",
    "Gündüz ışığında çekin; tepe lambası yüzde gölge bırakır.",
    "Gözlük, şapka, maske olmasın; saç yüzünüzü kapatmasın.",
    "Yüzünüz karenin ortasında, net ve tamamen görünür olsun.",
];

/** Vesikalik reddedildiginde: kendi karesi ile dogru ornegi yan yana gosterir,
 *  cekim adimlarini listeler ve tek dokunusla yeniden yukleme sunar. */
export const PhotoRetryHelper = ({ result, photoUrl, onRetry, testId }) => {
    const [guideOpen, setGuideOpen] = useState(true);

    return (
        <div
            className="mt-2 rounded-xl border border-destructive/35 bg-destructive/[0.06] p-4"
            data-testid={testId}
        >
            <p className="flex items-center gap-2 text-sm font-bold text-foreground">
                <AlertCircle className="h-4 w-4 shrink-0 text-destructive" />
                {result.isPhoto === false
                    ? "Bu görüntü vesikalık fotoğraf gibi görünmüyor"
                    : "Bu vesikalık vize standartlarına uygun değil"}
            </p>
            <p className="mt-1 text-xs font-semibold leading-5 text-destructive">
                Bu fotoğrafla başvuruya devam edilemez. Aşağıdaki örneğe bakıp yeni bir kare çekin.
            </p>

            <div className="mt-3 grid grid-cols-2 gap-3 sm:max-w-sm">
                <figure data-testid={`${testId}-mine`}>
                    <div className="overflow-hidden rounded-lg border-2 border-destructive/60">
                        {photoUrl ? (
                            <img
                                src={fileUrl(photoUrl)}
                                alt="Yüklediğiniz fotoğraf"
                                className="aspect-[3/4] w-full bg-muted object-cover"
                            />
                        ) : (
                            <div className="flex aspect-[3/4] w-full items-center justify-center bg-muted">
                                <Camera className="h-6 w-6 text-muted-foreground" />
                            </div>
                        )}
                    </div>
                    <figcaption className="mt-1 text-[11px] font-bold uppercase tracking-wider text-destructive">
                        Sizin kareniz
                    </figcaption>
                </figure>
                <figure data-testid={`${testId}-example`}>
                    <div className="overflow-hidden rounded-lg border-2 border-[hsl(var(--brand-green))]">
                        <img
                            src="/photo-guide/ok.jpg"
                            alt="Vize standartlarına uygun vesikalık örneği"
                            className="aspect-[3/4] w-full object-cover"
                        />
                    </div>
                    <figcaption className="mt-1 text-[11px] font-bold uppercase tracking-wider text-[hsl(var(--brand-green))]">
                        Olması gereken
                    </figcaption>
                </figure>
            </div>

            {result.issues?.length > 0 && (
                <ul className="mt-3 space-y-1">
                    {result.issues.map((issue, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-xs leading-5 text-muted-foreground">
                            <X className="mt-0.5 h-3 w-3 shrink-0 text-destructive" />
                            {issue}
                        </li>
                    ))}
                </ul>
            )}
            {result.advice ? (
                <p className="mt-2 text-xs leading-5 text-muted-foreground">{result.advice}</p>
            ) : null}

            <div className="mt-3 rounded-lg border border-border bg-card p-3">
                <p className="font-heading text-xs font-bold">Doğru kare 5 adımda</p>
                <ol className="mt-2 space-y-1.5">
                    {STEPS.map((s, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs leading-5 text-muted-foreground">
                            <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-primary/12 text-[10px] font-bold text-primary">
                                {i + 1}
                            </span>
                            {s}
                        </li>
                    ))}
                </ol>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-3">
                <Button
                    type="button"
                    className="h-11"
                    onClick={onRetry}
                    data-testid={`${testId}-retry-button`}
                >
                    <RefreshCw className="mr-2 h-4 w-4" /> Yeni fotoğraf yükle
                </Button>
                <button
                    type="button"
                    onClick={() => setGuideOpen((v) => !v)}
                    className="text-xs font-bold text-primary underline decoration-primary/40 underline-offset-4 transition-colors duration-200 hover:decoration-primary"
                    data-testid={`${testId}-guide-toggle`}
                >
                    {guideOpen ? "Örnekleri gizle" : "Doğru ve yanlış örnekleri göster"}
                </button>
            </div>

            {guideOpen && <PhotoGuide testId={`${testId}-guide`} />}
        </div>
    );
};
