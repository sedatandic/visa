import React, { useRef, useState } from "react";
import { AlertCircle, Camera, CheckCircle2, Eye, FileText, Loader2, Trash2, UploadCloud } from "lucide-react";
import { api, apiError, fileUrl } from "../lib/api";
import { Button } from "./ui/button";
import { CameraCapture } from "./CameraCapture";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";

export const FileDropzone = ({
    label,
    hint,
    docType,
    value,
    onChange,
    testId,
    icon: Icon,
    badge,
    description,
    onInputRef,
    capture,
    accept = "image/jpeg,image/png,image/webp,application/pdf",
}) => {
    const inputRef = useRef(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState("");
    const [dragOver, setDragOver] = useState(false);
    const [preview, setPreview] = useState(null);
    const [viewOpen, setViewOpen] = useState(false);
    const [cameraOpen, setCameraOpen] = useState(false);
    const cameraSupported = Boolean(capture && navigator.mediaDevices?.getUserMedia);

    const handleFiles = async (files) => {
        const file = files?.[0];
        if (!file) return;
        setError("");
        if (file.size > 10 * 1024 * 1024) {
            setError("Dosya boyutu en fazla 10 MB olabilir.");
            return;
        }
        const form = new FormData();
        form.append("file", file);
        form.append("doc_type", docType);
        setUploading(true);
        try {
            const { data } = await api.post("/uploads", form, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            if (file.type.startsWith("image/")) {
                setPreview(URL.createObjectURL(file));
            } else {
                setPreview(null);
            }
            onChange(data);
        } catch (err) {
            setError(apiError(err, "Dosya yüklenemedi. Lütfen tekrar deneyin."));
        } finally {
            setUploading(false);
        }
    };

    const removeFile = () => {
        setPreview(null);
        setError("");
        if (inputRef.current) inputRef.current.value = "";
        onChange(null);
    };

    const isImage = value && (value.content_type || "").startsWith("image/");

    return (
        <div className="space-y-2">
            <div className="flex items-baseline justify-between gap-3">
                <span className="flex flex-wrap items-center gap-2 text-sm font-semibold">
                    {label}
                    {badge === "required" && (
                        <span className="rounded-full bg-primary/12 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-primary">
                            Zorunlu
                        </span>
                    )}
                    {badge === "optional" && (
                        <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                            Opsiyonel
                        </span>
                    )}
                </span>
                {hint ? <span className="text-xs text-muted-foreground">{hint}</span> : null}
            </div>
            {description ? (
                <p className="min-h-[3.75rem] text-xs leading-5 text-muted-foreground">{description}</p>
            ) : null}

            {value ? (
                <div
                    className="flex flex-wrap items-center gap-x-4 gap-y-3 rounded-xl border border-[hsl(var(--brand-green)/0.30)] bg-[hsl(var(--brand-green)/0.06)] p-4"
                    data-testid={`${testId}-uploaded`}
                >
                    {isImage && preview ? (
                        <button
                            type="button"
                            onClick={() => setViewOpen(true)}
                            className="group/thumb relative h-16 w-16 shrink-0 overflow-hidden rounded-lg border border-border transition-colors duration-200 hover:border-primary"
                            data-testid={`${testId}-thumb`}
                            aria-label="Yüklenen belgeyi görüntüle"
                        >
                            <img src={preview} alt={value.original_filename} className="h-full w-full object-cover" />
                            <span className="absolute inset-0 flex items-center justify-center bg-foreground/45 opacity-0 transition-opacity duration-200 group-hover/thumb:opacity-100">
                                <Eye className="h-5 w-5 text-white" aria-hidden="true" />
                            </span>
                        </button>
                    ) : isImage ? (
                        <button
                            type="button"
                            onClick={() => setViewOpen(true)}
                            className="group/thumb relative h-16 w-16 shrink-0 overflow-hidden rounded-lg border border-border transition-colors duration-200 hover:border-primary"
                            data-testid={`${testId}-thumb`}
                            aria-label="Yüklenen belgeyi görüntüle"
                        >
                            <img
                                src={fileUrl(value.url)}
                                alt={value.original_filename}
                                className="h-full w-full object-cover"
                            />
                            <span className="absolute inset-0 flex items-center justify-center bg-foreground/45 opacity-0 transition-opacity duration-200 group-hover/thumb:opacity-100">
                                <Eye className="h-5 w-5 text-white" aria-hidden="true" />
                            </span>
                        </button>
                    ) : (
                        <button
                            type="button"
                            onClick={() => setViewOpen(true)}
                            className="flex h-16 w-16 shrink-0 items-center justify-center rounded-lg border border-border bg-card transition-colors duration-200 hover:border-primary hover:text-primary"
                            data-testid={`${testId}-thumb`}
                            aria-label="Yüklenen belgeyi görüntüle"
                        >
                            <FileText className="h-6 w-6 text-muted-foreground" />
                        </button>
                    )}
                    <div className="min-w-[110px] flex-1">
                        <div className="flex items-center gap-1.5 text-sm font-semibold text-[hsl(var(--brand-green))]">
                            <CheckCircle2 className="h-4 w-4" /> Yüklendi
                        </div>
                        <p className="truncate text-xs text-muted-foreground">{value.original_filename}</p>
                        <p className="text-xs text-muted-foreground">
                            {Math.max(1, Math.round((value.size || 0) / 1024))} KB
                        </p>
                    </div>
                    <div className="flex min-w-0 flex-wrap items-center gap-1.5">
                        <Button
                            type="button"
                            variant="secondary"
                            className="h-9 shrink-0 px-2.5 text-xs"
                            onClick={() => setViewOpen(true)}
                            data-testid={`${testId}-view`}
                        >
                            <Eye className="mr-1.5 h-3.5 w-3.5" /> Görüntüle
                        </Button>
                        <Button
                            type="button"
                            variant="secondary"
                            className="h-9 shrink-0 px-2.5 text-xs"
                            onClick={() => inputRef.current?.click()}
                            data-testid={`${testId}-change`}
                        >
                            Değiştir
                        </Button>
                        {cameraSupported && (
                            <Button
                                type="button"
                                variant="secondary"
                                className="h-9 shrink-0 px-2.5 text-xs"
                                onClick={() => setCameraOpen(true)}
                                data-testid={`${testId}-recapture`}
                            >
                                <Camera className="mr-1.5 h-3.5 w-3.5" /> Tekrar çek
                            </Button>
                        )}
                        <Button
                            type="button"
                            variant="ghost"
                            className="h-9 shrink-0 px-2.5 text-xs text-destructive hover:bg-destructive/10 hover:text-destructive"
                            onClick={removeFile}
                            data-testid={`${testId}-remove`}
                        >
                            <Trash2 className="mr-1.5 h-3.5 w-3.5" /> Kaldır
                        </Button>
                    </div>
                </div>
            ) : (
                <div className="flex flex-col gap-2">
                    {cameraSupported && (
                        <Button
                            type="button"
                            className="order-first h-12 w-full text-base sm:order-last sm:h-11 sm:text-sm"
                            onClick={() => setCameraOpen(true)}
                            data-testid={`${testId}-camera-button`}
                        >
                            <Camera className="mr-2 h-5 w-5" /> Kamerayla çek
                        </Button>
                    )}
                    <button
                        type="button"
                        onClick={() => inputRef.current?.click()}
                        onDragOver={(e) => {
                            e.preventDefault();
                            setDragOver(true);
                        }}
                        onDragLeave={() => setDragOver(false)}
                        onDrop={(e) => {
                            e.preventDefault();
                            setDragOver(false);
                            handleFiles(e.dataTransfer.files);
                        }}
                        className={`flex w-full flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-9 text-center transition-colors duration-150 ${
                            dragOver ? "border-primary bg-primary/5" : "border-border bg-card hover:border-primary/50"
                        }`}
                        data-testid={`${testId}-dropzone`}
                    >
                        {uploading ? (
                            <>
                                <Loader2 className="h-7 w-7 animate-spin text-primary" />
                                <span className="text-sm font-semibold">Yükleniyor…</span>
                            </>
                        ) : (
                            <>
                                <span className="flex h-11 w-11 items-center justify-center rounded-full bg-primary/10">
                                    {Icon ? (
                                        <Icon className="h-5 w-5 text-primary" />
                                    ) : (
                                        <UploadCloud className="h-5 w-5 text-primary" />
                                    )}
                                </span>
                                <span className="rounded-full bg-primary/10 px-4 py-1.5 text-sm font-bold text-primary">
                                    Dosya Seç
                                </span>
                                <span className="text-xs text-muted-foreground">
                                    Sürükleyip bırakabilirsiniz · JPG / PNG / PDF · Maks. 10 MB
                                </span>
                            </>
                        )}
                    </button>
                </div>
            )}

            <input
                ref={(el) => {
                    inputRef.current = el;
                    if (onInputRef) onInputRef(el);
                }}
                type="file"
                accept={accept}
                className="hidden"
                data-testid={testId}
                onChange={(e) => handleFiles(e.target.files)}
            />

            {error && (
                <p className="flex items-start gap-1.5 text-xs font-medium text-destructive" data-testid={`${testId}-error`}>
                    <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                    {error}
                </p>
            )}

            {cameraSupported && (
                <CameraCapture
                    mode={capture}
                    open={cameraOpen}
                    onClose={() => setCameraOpen(false)}
                    onCapture={(file) => handleFiles([file])}
                    onPickFile={() => inputRef.current?.click()}
                />
            )}

            {/* Yuklenen belgeyi buyuk onizleme */}
            <Dialog open={viewOpen} onOpenChange={setViewOpen}>
                <DialogContent
                    className="max-h-[92vh] max-w-[min(94vw,880px)] overflow-y-auto"
                    data-testid={`${testId}-preview-dialog`}
                >
                    <DialogHeader>
                        <DialogTitle className="truncate pr-8 text-base">
                            {value?.original_filename || label}
                        </DialogTitle>
                    </DialogHeader>
                    {value && (
                        <div className="mt-2">
                            {isImage ? (
                                <img
                                    src={preview || fileUrl(value.url)}
                                    alt={value.original_filename}
                                    className="mx-auto max-h-[68vh] w-auto rounded-xl border border-border object-contain"
                                    data-testid={`${testId}-preview-image`}
                                />
                            ) : (
                                <iframe
                                    src={fileUrl(value.url)}
                                    title={value.original_filename || "Belge"}
                                    className="h-[68vh] w-full rounded-xl border border-border"
                                    data-testid={`${testId}-preview-frame`}
                                />
                            )}
                            <div className="mt-4 flex flex-wrap gap-2">
                                <Button asChild variant="secondary" className="h-10 border border-border">
                                    <a
                                        href={fileUrl(value.url)}
                                        target="_blank"
                                        rel="noreferrer"
                                        data-testid={`${testId}-preview-newtab`}
                                    >
                                        Yeni sekmede aç
                                    </a>
                                </Button>
                                <Button asChild variant="secondary" className="h-10 border border-border">
                                    <a href={fileUrl(value.url, true)} data-testid={`${testId}-preview-download`}>
                                        İndir
                                    </a>
                                </Button>
                            </div>
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
};
