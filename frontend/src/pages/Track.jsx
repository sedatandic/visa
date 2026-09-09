import React, { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { AlertTriangle, ArrowRight, CheckCircle2, Clock, CreditCard, Download, FileCheck2, FileDown, Loader2, Search, UploadCloud, XCircle } from "lucide-react";
import { toast } from "sonner";
import { api, apiError, fileUrl, customerAuth, API } from "../lib/api";
import { STATUS_META, formatDate, formatDateTime, formatMoney, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { PaymentBadge, StatusBadge } from "../components/StatusBadge";
import { FileDropzone } from "../components/FileDropzone";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { AccountLoginCard } from "../components/AccountLoginCard";
import { GuaranteeCountdown } from "../components/GuaranteeCountdown";

const StepIcon = ({ state, isResult, resultStatus }) => {
    if (isResult && state === "done") {
        return resultStatus === "approved" ? (
            <CheckCircle2 className="h-5 w-5 text-[hsl(var(--brand-green))]" />
        ) : (
            <XCircle className="h-5 w-5 text-destructive" />
        );
    }
    if (state === "done") return <CheckCircle2 className="h-5 w-5 text-[hsl(var(--brand-green))]" />;
    if (state === "current") return <Clock className="h-5 w-5 text-primary" />;
    return <span className="block h-2.5 w-2.5 rounded-full bg-border" />;
};

const CustomerTimeline = ({ timeline }) => {
    if (!timeline?.steps?.length) return null;
    const total = timeline.steps.length;
    const doneCount = timeline.steps.filter((s) => s.state === "done").length;
    const percent = Math.round((doneCount / total) * 100);
    return (
        <div className="card-surface p-6" data-testid="tracking-customer-timeline">
            <div className="flex flex-wrap items-center justify-between gap-3">
                <h2 className="font-heading text-lg font-bold">Başvurunuz nerede?</h2>
                <span className="text-sm font-semibold text-muted-foreground" data-testid="timeline-progress-label">
                    {doneCount}/{total} adım tamamlandı
                </span>
            </div>
            <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-[hsl(var(--cloud))]">
                <div
                    className="h-full rounded-full bg-[hsl(var(--brand-green))] transition-transform duration-300"
                    style={{ width: `${percent}%` }}
                    data-testid="timeline-progress-bar"
                />
            </div>

            <ol className="mt-6 space-y-1">
                {timeline.steps.map((step, i) => {
                    const isResult = step.key === "result";
                    const active = step.state === "current";
                    return (
                        <li key={step.key} className="flex gap-4" data-testid={`timeline-step-${step.key}`}>
                            <div className="flex flex-col items-center pt-1">
                                <span
                                    className={`flex h-9 w-9 items-center justify-center rounded-full border ${
                                        step.state === "done"
                                            ? "border-[hsl(var(--brand-green)/0.35)] bg-[hsl(var(--brand-green)/0.08)]"
                                            : active
                                              ? "border-primary bg-primary/10 ring-4 ring-primary/10"
                                              : "border-border bg-card"
                                    }`}
                                >
                                    <StepIcon state={step.state} isResult={isResult} resultStatus={timeline.current_status} />
                                </span>
                                {i < total - 1 && (
                                    <span
                                        className={`mt-1.5 w-0.5 flex-1 rounded-full ${
                                            step.state === "done"
                                                ? "bg-[hsl(var(--brand-green)/0.45)]"
                                                : "bg-border"
                                        }`}
                                    />
                                )}
                            </div>
                            <div
                                className={`mb-4 flex-1 rounded-xl border p-4 transition-colors duration-200 ${
                                    active
                                        ? "border-primary/40 bg-primary/[0.06]"
                                        : step.state === "done"
                                          ? "border-border/70 bg-card"
                                          : "border-transparent"
                                }`}
                            >
                                <div className="flex flex-wrap items-center gap-2">
                                    <p
                                        className={`font-heading text-sm font-bold ${
                                            step.state === "pending" ? "text-muted-foreground" : ""
                                        }`}
                                    >
                                        {isResult && step.state === "done"
                                            ? timeline.current_status === "approved"
                                                ? "Vizeniz onaylandı"
                                                : STATUS_META[timeline.current_status]?.label || step.title
                                            : step.title}
                                    </p>
                                    {active && (
                                        <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary">
                                            Şu an burada
                                        </span>
                                    )}
                                </div>
                                <p className="mt-1 text-sm leading-6 text-muted-foreground">{step.description}</p>
                                {step.at && (
                                    <p className="mt-1 text-xs text-muted-foreground" data-testid={`timeline-step-date-${step.key}`}>
                                        {formatDateTime(step.at)}
                                    </p>
                                )}
                            </div>
                        </li>
                    );
                })}
            </ol>

            {timeline.last_portal_check && (
                <p className="mt-2 text-xs text-muted-foreground" data-testid="timeline-last-check">
                    Başvurunuz göçmenlik idaresi portalında en son {formatDateTime(timeline.last_portal_check)} tarihinde
                    kontrol edildi. Durum değiştiğinde size e-posta ile bilgi veriyoruz.
                </p>
            )}
        </div>
    );
};

export default function Track() {    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [code, setCode] = useState(searchParams.get("kod") || "");
    const [lastName, setLastName] = useState(searchParams.get("soyad") || "");
    const [loading, setLoading] = useState(false);
    const [paying, setPaying] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const [docSlots, setDocSlots] = useState({});
    const [submittingDocs, setSubmittingDocs] = useState(false);

    const submitDocuments = async () => {
        const body = { last_name: lastName.trim(), traveler_documents: [] };
        const perTraveler = {};
        Object.entries(docSlots).forEach(([slot, file]) => {
            if (!file?.file_id) return;
            const [key, travelerId] = slot.split(":");
            if (travelerId) {
                perTraveler[travelerId] = { ...(perTraveler[travelerId] || {}), traveler_id: travelerId };
                perTraveler[travelerId][`${key}_file_id`] = file.file_id;
            } else {
                body[`${key}_file_id`] = file.file_id;
            }
        });
        body.traveler_documents = Object.values(perTraveler);
        setSubmittingDocs(true);
        try {
            const { data } = await api.post(`/applications/${result.reference_code}/documents`, body);
            setResult(data.application);
            setDocSlots({});
            toast.success(
                (data.missing_documents || []).length === 0
                    ? "Tüm belgeleriniz alındı. Başvurunuz incelemeye alındı."
                    : "Belgeleriniz alındı. Kalan belgeleri de yükleyebilirsiniz."
            );
        } catch (err) {
            toast.error(apiError(err, "Belgeler gönderilemedi."));
        } finally {
            setSubmittingDocs(false);
        }
    };

    useEffect(() => {
        setMeta(
            "Başvuru Takip | Dubai Vize Hattı",
            "Takip kodunuz ve soyadınızla Dubai vize başvurunuzun durumunu sorgulayın, onaylanan vizenizi indirin."
        );
    }, []);

    const search = async (e) => {
        e?.preventDefault();
        if (!code.trim() || !lastName.trim()) {
            setError("Takip kodu ve soyad alanı zorunludur.");
            return;
        }
        setError("");
        setLoading(true);
        setResult(null);
        try {
            const { data } = await api.get("/applications/track", {
                params: { code: code.trim(), last_name: lastName.trim() },
            });
            setResult(data);
        } catch (err) {
            setError(apiError(err, "Başvuru bulunamadı."));
        } finally {
            setLoading(false);
        }
    };

    const payNow = async () => {
        setPaying(true);
        try {
            const { data } = await api.post("/payments/checkout", {
                application_id: result.id,
                origin_url: window.location.origin,
            });
            window.location.href = data.checkout_url;
        } catch (err) {
            toast.error(apiError(err, "Ödeme sayfası açılamadı."));
            setPaying(false);
        }
    };

    const pricing = result?.pricing;
    const visaFile = result?.visa_result;

    return (
        <div data-testid="track-page">
            <PageHeader
                eyebrow="Başvuru Takip"
                title="Başvurunuzun durumunu sorgulayın"
                description="Takip kodunuz ve yolculardan birinin soyadı ile başvurunuzun güncel durumunu görüntüleyebilir, onaylanan vizenizi indirebilirsiniz."
            />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page">
                  <div className="grid items-stretch gap-6 lg:grid-cols-2">
                   <div className="flex flex-col gap-6">
                    <form onSubmit={search} className="card-surface p-6 sm:p-8" data-testid="tracking-lookup-form">
                        <h2 className="font-heading text-xl font-bold">Takip kodu ile sorgula</h2>
                        <div className="mt-6 grid gap-5 sm:grid-cols-2">
                            <div className="space-y-2">
                                <Label htmlFor="t-code">Takip kodu *</Label>
                                <Input id="t-code" value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} placeholder="DV-AB123456" data-testid="tracking-code-input" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="t-last">Soyad *</Label>
                                <Input id="t-last" value={lastName} onChange={(e) => setLastName(e.target.value)} placeholder="YILMAZ" data-testid="tracking-lastname-input" />
                            </div>
                        </div>
                        <Button type="submit" disabled={loading} className="mt-6 h-12 w-full px-7 text-base sm:w-auto" data-testid="tracking-submit-button">
                            {loading ? (
                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sorgulanıyor…</>
                            ) : (
                                <><Search className="mr-2 h-4 w-4" /> Başvurumu sorgula</>
                            )}
                        </Button>
                        {error && (
                            <p className="mt-4 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-sm font-medium text-destructive" data-testid="tracking-error-message">
                                {error}
                            </p>
                        )}
                    </form>

                    {!result && (
                        <div className="card-surface p-6 sm:p-7" data-testid="tracking-help-card">
                            <h2 className="font-heading text-base font-bold">Takip kodunuz nerede?</h2>
                            <ul className="mt-4 space-y-3.5">
                                {[
                                    "Başvurunuzu tamamladığınızda ekranda gösterilen DV- ile başlayan koddur.",
                                    "\"Başvurunuz alındı\" e-postasının konu satırında ve içeriğinde yer alır.",
                                    "Soyad alanına, başvurudaki yolculardan herhangi birinin soyadını yazabilirsiniz.",
                                ].map((t) => (
                                    <li key={t} className="flex items-start gap-2.5 text-sm leading-6 text-muted-foreground">
                                        <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                                        {t}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                  </div>

                   {!result && (
                       <AccountLoginCard
                           stacked
                           className="h-full"
                           onLogin={(newToken, email) => {
                               customerAuth.save(newToken, email);
                               navigate("/hesabim");
                           }}
                       />
                   )}
                  </div>

                    {result && (
                        <div className="mt-8 space-y-6" data-testid="tracking-result">
                            <div className="card-surface p-6">
                                <div className="flex flex-wrap items-start justify-between gap-4">
                                    <div>
                                        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Takip kodu</p>
                                        <p className="font-heading text-2xl font-bold tracking-wider">{result.reference_code}</p>
                                        <p className="mt-1 text-sm text-muted-foreground">
                                            {result.contact?.full_name} · {(result.travelers || []).length} yolcu
                                        </p>
                                    </div>
                                    <div className="flex flex-col items-start gap-2 sm:items-end">
                                        <StatusBadge status={result.status} />
                                        <PaymentBadge status={result.payment?.status} />
                                        <Button
                                            asChild
                                            variant="secondary"
                                            className="mt-1 h-10 border border-border"
                                            data-testid="tracking-download-form-button"
                                        >
                                            <a
                                                href={`${API}/applications/form.pdf?code=${encodeURIComponent(result.reference_code)}&last_name=${encodeURIComponent(lastName)}`}
                                                target="_blank"
                                                rel="noreferrer"
                                            >
                                                <FileDown className="mr-2 h-4 w-4" /> Başvuru formu (PDF)
                                            </a>
                                        </Button>
                                        {result.payment?.status === "paid" && (
                                            <Button
                                                asChild
                                                variant="secondary"
                                                className="h-10 border border-border"
                                                data-testid="tracking-download-receipt-button"
                                            >
                                                <a
                                                    href={`${API}/applications/receipt.pdf?code=${encodeURIComponent(result.reference_code)}&last_name=${encodeURIComponent(lastName)}`}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                >
                                                    <FileDown className="mr-2 h-4 w-4" /> Ödeme özeti (PDF)
                                                </a>
                                            </Button>
                                        )}
                                    </div>
                                </div>

                                <div className="mt-6 grid gap-4 border-t border-border pt-5 sm:grid-cols-2">
                                    <div>
                                        <p className="text-xs text-muted-foreground">Başvuru tarihi</p>
                                        <p className="text-sm font-semibold">{formatDateTime(result.created_at)}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-muted-foreground">Tahmini sonuçlanma</p>
                                        <p className="text-sm font-semibold">{result.processing_days || "-"}</p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-muted-foreground">Seyahat tarihleri</p>
                                        <p className="text-sm font-semibold">
                                            {formatDate(result.travel?.arrival_date)} – {formatDate(result.travel?.departure_date)}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-muted-foreground">Toplam tutar</p>
                                        <p className="text-sm font-semibold">{formatMoney(result.price, result.currency)}</p>
                                    </div>
                                </div>

                                {visaFile?.file_url && (
                                    <div className="mt-6 flex flex-col gap-3 rounded-xl border border-[hsl(var(--brand-green)/0.30)] bg-[hsl(var(--brand-green)/0.08)] p-5 sm:flex-row sm:items-center sm:justify-between" data-testid="visa-download-box">
                                        <div className="flex items-start gap-2.5">
                                            <FileCheck2 className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--brand-green))]" />
                                            <div>
                                                <p className="text-sm font-semibold text-[hsl(var(--brand-green))]">Vizeniz hazır!</p>
                                                <p className="text-xs text-[hsl(var(--brand-green))]/80">{visaFile.filename}</p>
                                            </div>
                                        </div>
                                        <Button asChild className="h-11 shrink-0" data-testid="tracking-download-visa-button">
                                            <a href={fileUrl(visaFile.file_url, true)} target="_blank" rel="noreferrer">
                                                <Download className="mr-2 h-4 w-4" /> Vizeyi indir
                                            </a>
                                        </Button>
                                    </div>
                                )}

                                {result.payment?.status !== "paid" && (
                                    <div className="mt-6 flex flex-col gap-3 rounded-xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.09)] p-5 sm:flex-row sm:items-center sm:justify-between">
                                        <p className="text-sm font-medium text-[hsl(var(--status-warning))]">
                                            Ödemeniz tamamlanmadı. Başvurunuz ödeme alındıktan sonra işleme alınır.
                                        </p>
                                        <Button onClick={payNow} disabled={paying} className="h-11 shrink-0" data-testid="tracking-pay-button">
                                            {paying ? (
                                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Açılıyor…</>
                                            ) : (
                                                <><CreditCard className="mr-2 h-4 w-4" /> Ödemeyi tamamla</>
                                            )}
                                        </Button>
                                    </div>
                                )}
                            </div>

                            {(result.missing_documents || []).length > 0 && (
                                <div
                                    className="rounded-xl border border-[hsl(var(--status-warning)/0.4)] bg-[hsl(var(--status-warning)/0.07)] p-6"
                                    data-testid="tracking-missing-documents"
                                >
                                    <div className="flex items-start gap-2.5">
                                        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--status-warning))]" />
                                        <div>
                                            <h2 className="font-heading text-lg font-bold text-[hsl(var(--status-warning))]">
                                                Eksik belgeler var
                                            </h2>
                                            <p className="mt-1 text-sm leading-6 text-[hsl(var(--status-warning))]">
                                                Başvurunuzu yetkili mercilere iletebilmemiz için aşağıdaki belgeleri
                                                yüklemeniz gerekiyor. Yükledikten sonra başvurunuz otomatik olarak
                                                incelemeye alınır.
                                            </p>
                                        </div>
                                    </div>

                                    <div className="mt-6 grid gap-6 sm:grid-cols-2">
                                        {(result.missing_documents || []).map((m) => {
                                            const slot = m.scope === "traveler" ? `${m.key}:${m.traveler_id}` : m.key;
                                            return (
                                                <div key={slot} className="rounded-xl border border-border bg-card p-4">
                                                    <FileDropzone
                                                        label={m.label}
                                                        hint={m.traveler_name || "Başvuru geneli"}
                                                        docType={m.key}
                                                        value={docSlots[slot] || null}
                                                        onChange={(f) => setDocSlots((s) => ({ ...s, [slot]: f }))}
                                                        testId={`missing-doc-${slot}`}
                                                    />
                                                </div>
                                            );
                                        })}
                                    </div>

                                    <Button
                                        onClick={submitDocuments}
                                        disabled={submittingDocs || Object.keys(docSlots).length === 0}
                                        className="mt-6 h-11"
                                        data-testid="submit-missing-documents-button"
                                    >
                                        {submittingDocs ? (
                                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Gönderiliyor…</>
                                        ) : (
                                            <><UploadCloud className="mr-2 h-4 w-4" /> Belgeleri gönder</>
                                        )}
                                    </Button>
                                </div>
                            )}

                            {result.missing_documents && result.missing_documents.length === 0 && (
                                <div
                                    className="flex items-start gap-2.5 rounded-xl border border-[hsl(var(--brand-green)/0.3)] bg-[hsl(var(--brand-green)/0.07)] p-5"
                                    data-testid="tracking-documents-complete"
                                >
                                    <FileCheck2 className="mt-0.5 h-5 w-5 shrink-0 text-[hsl(var(--brand-green))]" />
                                    <p className="text-sm font-medium text-[hsl(var(--brand-green))]">
                                        Tüm belgeleriniz tamam. Başvurunuz danışmanlarımız tarafından takip ediliyor.
                                    </p>
                                </div>
                            )}

                            <div className="card-surface p-6" data-testid="tracking-travelers">
                                <h2 className="font-heading text-lg font-bold">Yolcular</h2>
                                <div className="mt-4 space-y-3">
                                    {(result.travelers || []).map((t, i) => (
                                        <div key={t.id || i} className="flex flex-wrap items-center justify-between gap-2 rounded-lg bg-[hsl(var(--cloud))] p-4">
                                            <div>
                                                <p className="text-sm font-bold">
                                                    {t.first_name} {t.last_name}
                                                    <span className="ml-2 text-xs font-medium text-muted-foreground">
                                                        {t.applicant_type === "child" ? "Çocuk" : "Yetişkin"}
                                                    </span>
                                                </p>
                                                <p className="text-xs text-muted-foreground">{t.visa_type_name} · Pasaport: {t.passport_no}</p>
                                            </div>
                                            <span className="font-heading text-sm font-bold">{formatMoney(t.price, t.currency)}</span>
                                        </div>
                                    ))}
                                </div>

                                {pricing && (
                                    <div className="mt-5 space-y-2 border-t border-border pt-4 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Vize bedelleri</span>
                                            <span className="font-semibold">{formatMoney(pricing.subtotal, pricing.currency)}</span>
                                        </div>
                                        {pricing.family_discount > 0 && (
                                            <div className="flex justify-between text-[hsl(var(--success))]">
                                                <span>Aile indirimi (%{Math.round(pricing.family_discount_rate * 100)})</span>
                                                <span className="font-semibold">- {formatMoney(pricing.family_discount, pricing.currency)}</span>
                                            </div>
                                        )}
                                        {(pricing.addons || []).map((a) => (
                                            <div key={a.id} className="flex justify-between">
                                                <span className="text-muted-foreground">{a.name} x{a.quantity}</span>
                                                <span className="font-semibold">{formatMoney(a.total, pricing.currency)}</span>
                                            </div>
                                        ))}
                                        <div className="flex items-end justify-between border-t border-border pt-2">
                                            <span className="font-semibold">Toplam</span>
                                            <span className="font-heading text-xl font-bold">{formatMoney(pricing.total, pricing.currency)}</span>
                                        </div>
                                    </div>
                                )}
                            </div>

                            <GuaranteeCountdown guarantee={result.guarantee} />
                            <CustomerTimeline timeline={result.timeline} />
                            <div className="card-surface p-6" data-testid="tracking-status-timeline">
                                <h2 className="font-heading text-lg font-bold">Başvuru geçmişi</h2>
                                <ol className="mt-5 space-y-5">
                                    {(result.status_history || []).map((h, i) => (
                                        <li key={i} className="flex gap-4">
                                            <div className="flex flex-col items-center">
                                                <span className="mt-1 h-2.5 w-2.5 rounded-full bg-primary" />
                                                {i < (result.status_history || []).length - 1 && <span className="mt-1 w-px flex-1 bg-border" />}
                                            </div>
                                            <div className="pb-1">
                                                <p className="text-sm font-semibold">{STATUS_META[h.status]?.label || h.status}</p>
                                                <p className="text-xs text-muted-foreground">{formatDateTime(h.at)}</p>
                                                {h.note && <p className="mt-1 text-sm text-muted-foreground">{h.note}</p>}
                                            </div>
                                        </li>
                                    ))}
                                </ol>
                            </div>
                        </div>
                    )}

                    <p className="mt-8 text-center text-sm text-muted-foreground">
                        Takip kodunuzu bulamıyor musunuz?{" "}
                        <Link to="/iletisim" className="font-semibold text-primary hover:underline">Bize ulaşın</Link>
                    </p>
                </div>
            </section>
        </div>
    );
}
