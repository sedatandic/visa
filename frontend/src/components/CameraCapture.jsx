import React, { useCallback, useEffect, useRef, useState } from "react";
import { Camera, Check, Images, RotateCcw, X } from "lucide-react";
import { Button } from "./ui/button";

// ID-3 pasaport kimlik sayfasi orani (125 x 88 mm)
const FRAME_RATIO = 125 / 88;
const MAX_WIDTH = 2000;

const MODES = {
    passport: {
        title: "Pasaport kimlik sayfası",
        hint: "Pasaportu yatay tutun, dört köşesi de çerçeveye girsin",
        facing: "environment",
        fileName: "pasaport.jpg",
    },
    photo: {
        title: "Vesikalık fotoğraf",
        hint: "Yüzünüzü çerçeveye ortalayın, arka plan düz ve açık renk olsun",
        facing: "user",
        fileName: "vesikalik.jpg",
    },
};

export const CameraCapture = ({ mode = "passport", open, onClose, onCapture, onPickFile }) => {
    const config = MODES[mode] || MODES.passport;
    const videoRef = useRef(null);
    const frameRef = useRef(null);
    const streamRef = useRef(null);
    const [error, setError] = useState("");
    const [ready, setReady] = useState(false);
    const [shot, setShot] = useState(null);

    const stop = useCallback(() => {
        streamRef.current?.getTracks().forEach((track) => track.stop());
        streamRef.current = null;
        setReady(false);
    }, []);

    useEffect(() => {
        if (!open) {
            stop();
            return undefined;
        }
        let cancelled = false;
        setError("");
        setShot(null);
        (async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        facingMode: { ideal: config.facing },
                        width: { ideal: 1920 },
                        height: { ideal: 1080 },
                    },
                    audio: false,
                });
                if (cancelled) {
                    stream.getTracks().forEach((track) => track.stop());
                    return;
                }
                streamRef.current = stream;
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                    await videoRef.current.play().catch(() => {});
                }
                setReady(true);
            } catch (err) {
                if (cancelled) return;
                setError(
                    err?.name === "NotAllowedError"
                        ? "Kamera izni verilmedi. Tarayıcı ayarlarından izin verebilir ya da galeriden seçebilirsiniz."
                        : "Kameraya ulaşılamadı. Galeriden fotoğraf seçebilirsiniz."
                );
            }
        })();
        return () => {
            cancelled = true;
            stop();
        };
    }, [open, config.facing, stop]);

    const takeShot = () => {
        const video = videoRef.current;
        const frame = frameRef.current;
        if (!video || !frame || !video.videoWidth) return;

        const vw = video.videoWidth;
        const vh = video.videoHeight;
        const view = video.getBoundingClientRect();
        const box = frame.getBoundingClientRect();
        // video object-cover: kaynak goruntu ekrana tasarak sigar
        const scale = Math.max(view.width / vw, view.height / vh);
        const offsetX = (view.width - vw * scale) / 2;
        const offsetY = (view.height - vh * scale) / 2;
        const sx = Math.max(0, (box.left - view.left - offsetX) / scale);
        const sy = Math.max(0, (box.top - view.top - offsetY) / scale);
        const sw = Math.min(vw - sx, box.width / scale);
        const sh = Math.min(vh - sy, box.height / scale);

        const outW = Math.min(MAX_WIDTH, Math.round(sw));
        const canvas = document.createElement("canvas");
        canvas.width = outW;
        canvas.height = Math.round((sh / sw) * outW);
        const ctx = canvas.getContext("2d");
        if (config.facing === "user") {
            ctx.translate(canvas.width, 0);
            ctx.scale(-1, 1);
        }
        ctx.drawImage(video, sx, sy, sw, sh, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(
            (blob) => {
                if (!blob) return;
                setShot({
                    url: URL.createObjectURL(blob),
                    file: new File([blob], config.fileName, { type: "image/jpeg" }),
                });
            },
            "image/jpeg",
            0.92
        );
    };

    const use = () => {
        if (!shot) return;
        onCapture(shot.file);
        stop();
        onClose();
    };

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-[80] flex flex-col bg-black" data-testid={`camera-capture-${mode}`}>
            <div className="flex items-center justify-between px-4 pb-2 pt-4 text-white">
                <button
                    type="button"
                    onClick={() => {
                        stop();
                        onClose();
                    }}
                    className="flex h-11 w-11 items-center justify-center rounded-full bg-white/15"
                    aria-label="Kamerayı kapat"
                    data-testid="camera-close-button"
                >
                    <X className="h-5 w-5" />
                </button>
                <span className="text-sm font-bold">{config.title}</span>
                <span className="h-11 w-11" />
            </div>

            <div className="relative flex-1 overflow-hidden">
                <video
                    ref={videoRef}
                    playsInline
                    muted
                    autoPlay
                    className={`h-full w-full object-cover ${config.facing === "user" ? "scale-x-[-1]" : ""}`}
                />
                {shot ? (
                    <img
                        src={shot.url}
                        alt="Çekilen kare"
                        className="absolute inset-0 h-full w-full bg-black object-contain"
                        data-testid="camera-shot-preview"
                    />
                ) : (
                    <>
                        <div className="pointer-events-none absolute inset-0 flex items-center justify-center px-5">
                            <div
                                ref={frameRef}
                                className={`relative w-full max-w-[520px] rounded-xl border-2 border-white/90 shadow-[0_0_0_9999px_rgba(0,0,0,0.55)] ${
                                    mode === "photo" ? "aspect-[35/45] max-w-[300px]" : ""
                                }`}
                                style={mode === "passport" ? { aspectRatio: String(FRAME_RATIO) } : undefined}
                            >
                                {mode === "passport" && (
                                    <span className="absolute inset-x-3 bottom-3 h-6 rounded border border-dashed border-white/70" />
                                )}
                            </div>
                        </div>
                        {error ? (
                            <div className="absolute inset-x-4 top-4 rounded-xl bg-white p-4 text-sm font-medium text-foreground" data-testid="camera-error">
                                {error}
                            </div>
                        ) : (
                            <p className="absolute inset-x-6 bottom-4 text-center text-xs font-semibold leading-5 text-white/90">
                                {ready ? config.hint : "Kamera açılıyor…"}
                            </p>
                        )}
                    </>
                )}
            </div>

            <div className="flex items-center justify-between gap-3 bg-black px-5 pb-7 pt-4">
                {shot ? (
                    <>
                        <Button
                            type="button"
                            variant="secondary"
                            className="h-12 flex-1 border border-white/20 bg-white/10 text-white hover:bg-white/20"
                            onClick={() => setShot(null)}
                            data-testid="camera-retake-button"
                        >
                            <RotateCcw className="mr-2 h-4 w-4" /> Tekrar çek
                        </Button>
                        <Button type="button" className="h-12 flex-1" onClick={use} data-testid="camera-use-button">
                            <Check className="mr-2 h-4 w-4" /> Kullan
                        </Button>
                    </>
                ) : (
                    <>
                        <button
                            type="button"
                            onClick={() => {
                                stop();
                                onClose();
                                onPickFile?.();
                            }}
                            className="flex min-h-11 items-center gap-2 text-xs font-semibold text-white/85"
                            data-testid="camera-pick-file-button"
                        >
                            <Images className="h-4 w-4" /> Galeriden seç
                        </button>
                        <button
                            type="button"
                            onClick={takeShot}
                            disabled={!ready}
                            className="flex h-[68px] w-[68px] items-center justify-center rounded-full bg-white text-black transition-transform active:scale-95 disabled:opacity-40"
                            aria-label="Fotoğraf çek"
                            data-testid="camera-shutter-button"
                        >
                            <Camera className="h-7 w-7" />
                        </button>
                        <span className="min-h-11 w-20" />
                    </>
                )}
            </div>
        </div>
    );
};
