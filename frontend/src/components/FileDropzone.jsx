import React, { useRef, useState } from "react";
import { AlertCircle, CheckCircle2, FileText, Loader2, UploadCloud } from "lucide-react";
import { api, apiError, fileUrl } from "../lib/api";
import { Button } from "./ui/button";

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
    accept = "image/jpeg,image/png,image/webp,application/pdf",
}) => {
    const inputRef = useRef(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState("");
    const [dragOver, setDragOver] = useState(false);
    const [preview, setPreview] = useState(null);

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
                <p className="text-xs leading-5 text-muted-foreground">{description}</p>
            ) : null}

            {value ? (
                <div
                    className="flex items-center gap-4 rounded-xl border border-[hsl(var(--brand-green)/0.30)] bg-[hsl(var(--brand-green)/0.06)] p-4"
                    data-testid={`${testId}-uploaded`}
                >
                    {isImage && preview ? (
                        <img
                            src={preview}
                            alt={value.original_filename}
                            className="h-16 w-16 rounded-lg border border-border object-cover"
                        />
                    ) : isImage ? (
                        <img
                            src={fileUrl(value.file_id)}
                            alt={value.original_filename}
                            className="h-16 w-16 rounded-lg border border-border object-cover"
                        />
                    ) : (
                        <span className="flex h-16 w-16 items-center justify-center rounded-lg border border-border bg-card">
                            <FileText className="h-6 w-6 text-muted-foreground" />
                        </span>
                    )}
                    <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-1.5 text-sm font-semibold text-[hsl(var(--brand-green))]">
                            <CheckCircle2 className="h-4 w-4" /> Yüklendi
                        </div>
                        <p className="truncate text-xs text-muted-foreground">{value.original_filename}</p>
                        <p className="text-xs text-muted-foreground">
                            {Math.max(1, Math.round((value.size || 0) / 1024))} KB
                        </p>
                    </div>
                    <Button
                        type="button"
                        variant="secondary"
                        className="h-10 shrink-0"
                        onClick={() => inputRef.current?.click()}
                        data-testid={`${testId}-change`}
                    >
                        Değiştir
                    </Button>
                </div>
            ) : (
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
            )}

            <input
                ref={inputRef}
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
        </div>
    );
};
