import React, { useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { RotateCcw, XCircle } from "lucide-react";
import { setMeta } from "../lib/site";
import { Button } from "../components/ui/button";

export default function PaymentCancel() {
    const [searchParams] = useSearchParams();
    const ref = searchParams.get("ref") || sessionStorage.getItem("dv_last_reference") || "";

    useEffect(() => {
        setMeta("Ödeme İptal Edildi | Dubai Vize Hattı", "Ödeme işleminiz tamamlanmadı. Başvurunuz kayıtlı kalmaya devam eder.");
    }, []);

    return (
        <section className="section" data-testid="payment-cancel-page">
            <div className="container-page max-w-2xl">
                <div className="card-surface p-8 text-center sm:p-10">
                    <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-[hsl(var(--status-warning)/0.15)]">
                        <XCircle className="h-9 w-9 text-[hsl(var(--status-warning))]" />
                    </span>
                    <h1 className="mt-6 text-2xl font-bold sm:text-3xl">Ödeme tamamlanmadı</h1>
                    <p className="mt-3 text-sm leading-6 text-muted-foreground">
                        Ödeme işlemini iptal ettiniz. Endişelenmeyin: başvurunuz ve yüklediğiniz belgeler
                        sistemimizde kayıtlı kaldı. Dilediğiniz zaman takip kodunuzla ödemeyi
                        tamamlayabilirsiniz.
                    </p>

                    {ref && (
                        <div className="mt-7 rounded-xl border border-border bg-[hsl(var(--sand-surface))] p-5">
                            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Takip kodunuz</p>
                            <p className="mt-1 font-heading text-2xl font-bold tracking-[0.15em]" data-testid="cancel-reference-code">
                                {ref}
                            </p>
                        </div>
                    )}

                    <div className="mt-7 flex flex-wrap justify-center gap-3">
                        <Button asChild className="h-11" data-testid="cancel-retry-button">
                            <Link to={ref ? `/takip?kod=${ref}` : "/takip"}>
                                <RotateCcw className="mr-2 h-4 w-4" /> Ödemeyi tekrar dene
                            </Link>
                        </Button>
                        <Button asChild variant="secondary" className="h-11 border border-border">
                            <Link to="/iletisim">Destek ile iletişime geç</Link>
                        </Button>
                    </div>
                </div>
            </div>
        </section>
    );
}
