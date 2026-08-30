import React, { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CreditCard, Download, FileCheck2, Loader2, Search } from "lucide-react";
import { toast } from "sonner";
import { api, apiError, API } from "../lib/api";
import { STATUS_META, formatDate, formatDateTime, formatMoney, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { PaymentBadge, StatusBadge } from "../components/StatusBadge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

export default function Track() {
    const [searchParams] = useSearchParams();
    const [code, setCode] = useState(searchParams.get("kod") || "");
    const [lastName, setLastName] = useState("");
    const [loading, setLoading] = useState(false);
    const [paying, setPaying] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        setMeta(
            "Başvuru Takip | VizeAtlas Dubai",
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

            <section className="section">
                <div className="container-page max-w-3xl">
                    <form onSubmit={search} className="card-surface p-6 sm:p-8" data-testid="tracking-lookup-form">
                        <div className="grid gap-5 sm:grid-cols-2">
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

                                {visaFile?.file_id && (
                                    <div className="mt-6 flex flex-col gap-3 rounded-xl border border-[rgba(22,163,74,0.35)] bg-[rgba(22,163,74,0.08)] p-5 sm:flex-row sm:items-center sm:justify-between" data-testid="visa-download-box">
                                        <div className="flex items-start gap-2.5">
                                            <FileCheck2 className="mt-0.5 h-5 w-5 shrink-0 text-[#14532D]" />
                                            <div>
                                                <p className="text-sm font-semibold text-[#14532D]">Vizeniz hazır!</p>
                                                <p className="text-xs text-[#14532D]/80">{visaFile.filename}</p>
                                            </div>
                                        </div>
                                        <Button asChild className="h-11 shrink-0" data-testid="tracking-download-visa-button">
                                            <a href={`${API}/files/${visaFile.file_id}?download=1`} target="_blank" rel="noreferrer">
                                                <Download className="mr-2 h-4 w-4" /> Vizeyi indir
                                            </a>
                                        </Button>
                                    </div>
                                )}

                                {result.payment?.status !== "paid" && (
                                    <div className="mt-6 flex flex-col gap-3 rounded-xl border border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.1)] p-5 sm:flex-row sm:items-center sm:justify-between">
                                        <p className="text-sm font-medium text-[#7A4B00]">
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
