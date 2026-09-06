import React, { useCallback, useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { AlertTriangle, CheckCircle2, Loader2, Mail, Search } from "lucide-react";
import { api } from "../lib/api";
import { formatMoney, setMeta } from "../lib/site";
import { Button } from "../components/ui/button";

const POLL_INTERVAL = 2000;
const MAX_ATTEMPTS = 20;

export default function PaymentSuccess() {
    const [searchParams] = useSearchParams();
    const sessionId = searchParams.get("session_id");
    const [state, setState] = useState("checking"); // checking | paid | pending | error
    const [data, setData] = useState(null);
    const attempts = useRef(0);

    useEffect(() => {
        setMeta("Ödeme Sonucu | Dubai Vize Hattı", "Dubai vize başvurusu ödeme sonucu ve takip kodu bilgileri.");
    }, []);

    const poll = useCallback(async () => {
        if (!sessionId) {
            setState("error");
            return;
        }
        try {
            const { data: res } = await api.get(`/payments/status/${sessionId}`);
            setData(res);
            if (res.payment_status === "paid") {
                setState("paid");
                return;
            }
            if (["expired", "failed"].includes(res.payment_status)) {
                setState("error");
                return;
            }
            attempts.current += 1;
            if (attempts.current >= MAX_ATTEMPTS) {
                setState("pending");
                return;
            }
            setTimeout(poll, POLL_INTERVAL);
        } catch (err) {
            attempts.current += 1;
            if (attempts.current >= 4) {
                setState("error");
                return;
            }
            setTimeout(poll, POLL_INTERVAL);
        }
    }, [sessionId]);

    useEffect(() => {
        poll();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const reference = data?.reference_code || sessionStorage.getItem("dv_last_reference") || "";

    return (
        <section className="section" data-testid="payment-success-page">
            <div className="container-page max-w-2xl">
                <div className="card-surface p-8 text-center sm:p-10">
                    {state === "checking" && (
                        <div data-testid="payment-checking-state">
                            <Loader2 className="mx-auto h-12 w-12 animate-spin text-primary" />
                            <h1 className="mt-6 text-2xl font-bold">Ödemeniz doğrulanıyor…</h1>
                            <p className="mt-3 text-sm leading-6 text-muted-foreground">
                                Bu işlem birkaç saniye sürebilir. Lütfen sayfayı kapatmayın.
                            </p>
                        </div>
                    )}

                    {state === "paid" && (
                        <div data-testid="payment-paid-state">
                            <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-[hsl(var(--brand-green)/0.12)]">
                                <CheckCircle2 className="h-9 w-9 text-[hsl(var(--brand-green))]" />
                            </span>
                            <h1 className="mt-6 text-2xl font-bold sm:text-3xl">Ödemeniz alındı</h1>
                            <p className="mt-3 text-sm leading-6 text-muted-foreground">
                                Başvurunuz işleme alındı ve danışmanımıza atandı. Onay durumu
                                değiştiğinde e-posta ile bilgilendirileceksiniz.
                            </p>

                            <div className="mt-7 rounded-xl border border-border bg-[hsl(var(--sand-surface))] p-5">
                                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Takip kodunuz</p>
                                <p className="mt-1 font-heading text-2xl font-bold tracking-[0.15em]" data-testid="success-reference-code">
                                    {reference || "-"}
                                </p>
                                {data?.amount && (
                                    <p className="mt-2 text-sm text-muted-foreground">
                                        Ödenen tutar: {formatMoney(data.amount, (data.currency || "TRY").toUpperCase())}
                                    </p>
                                )}
                            </div>

                            <div className="mt-7 flex flex-wrap justify-center gap-3">
                                <Button asChild className="h-11" data-testid="success-track-button">
                                    <Link to={`/takip?kod=${reference}`}>
                                        <Search className="mr-2 h-4 w-4" /> Başvurumu takip et
                                    </Link>
                                </Button>
                                <Button asChild variant="secondary" className="h-11 border border-border">
                                    <Link to="/">Ana sayfaya dön</Link>
                                </Button>
                            </div>

                            <p className="mt-6 flex items-center justify-center gap-2 text-xs text-muted-foreground">
                                <Mail className="h-3.5 w-3.5" /> Bilgilendirme e-postası kayıtlı adresinize gönderildi.
                            </p>
                        </div>
                    )}

                    {state === "pending" && (
                        <div data-testid="payment-pending-state">
                            <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-[hsl(var(--status-warning)/0.15)]">
                                <AlertTriangle className="h-9 w-9 text-[hsl(var(--status-warning))]" />
                            </span>
                            <h1 className="mt-6 text-2xl font-bold">Ödeme henüz doğrulanamadı</h1>
                            <p className="mt-3 text-sm leading-6 text-muted-foreground">
                                Bankanızın onayı gecikmiş olabilir. Başvurunuz kaydımızda duruyor;
                                ödeme onaylanır onaylanmaz durumu güncelliyoruz. Takip sayfasından
                                birkaç dakika sonra tekrar kontrol edebilirsiniz.
                            </p>
                            <div className="mt-7 flex flex-wrap justify-center gap-3">
                                <Button asChild className="h-11">
                                    <Link to="/takip">Takip sayfasına git</Link>
                                </Button>
                                <Button asChild variant="secondary" className="h-11 border border-border">
                                    <Link to="/iletisim">Destek ile iletişime geç</Link>
                                </Button>
                            </div>
                        </div>
                    )}

                    {state === "error" && (
                        <div data-testid="payment-error-state">
                            <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
                                <AlertTriangle className="h-9 w-9 text-destructive" />
                            </span>
                            <h1 className="mt-6 text-2xl font-bold">Ödeme sonucu alınamadı</h1>
                            <p className="mt-3 text-sm leading-6 text-muted-foreground">
                                Ödeme tamamlanmamış veya oturum süresi dolmuş olabilir. Başvurunuz
                                silinmedi; takip sayfasından ödemeyi yeniden başlatabilirsiniz.
                            </p>
                            <div className="mt-7 flex flex-wrap justify-center gap-3">
                                <Button asChild className="h-11">
                                    <Link to="/takip">Takip sayfasına git</Link>
                                </Button>
                                <Button asChild variant="secondary" className="h-11 border border-border">
                                    <Link to="/iletisim">Destek ile iletişime geç</Link>
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </section>
    );
}
