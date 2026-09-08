import React, { useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { AlertCircle, ArrowUpRight, Check, Copy, Loader2, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { Button } from "../components/ui/button";

const formatBirthDate = (iso) => {
    if (!iso) return "";
    const [year, month, day] = String(iso).slice(0, 10).split("-");
    return year && month && day ? `${day}-${month}-${year}` : iso;
};

const CopyField = ({ label, value, hint, testId }) => {
    const [copied, setCopied] = useState(false);

    const copy = async () => {
        try {
            await navigator.clipboard.writeText(value);
        } catch {
            const helper = document.createElement("textarea");
            helper.value = value;
            document.body.appendChild(helper);
            helper.select();
            document.execCommand("copy");
            helper.remove();
        }
        setCopied(true);
        toast.success(`${label} kopyalandı`);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!value) return null;
    return (
        <div className="flex items-center justify-between gap-3 border-b border-border/60 py-3 last:border-0">
            <div className="min-w-0">
                <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
                <div className="truncate font-heading text-base font-bold" data-testid={`${testId}-value`}>
                    {value}
                </div>
                {hint && <div className="mt-0.5 text-xs text-muted-foreground">{hint}</div>}
            </div>
            <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={copy}
                className="shrink-0 transition-colors"
                data-testid={`${testId}-copy`}
            >
                {copied ? <Check className="mr-1.5 h-4 w-4" /> : <Copy className="mr-1.5 h-4 w-4" />}
                {copied ? "Kopyalandı" : "Kopyala"}
            </Button>
        </div>
    );
};

const TravelerCard = ({ traveler, index, fallbackNumber }) => {
    const fileNumber = traveler.file_number || fallbackNumber?.formatted || "";
    const plain = traveler.file_number_plain || fallbackNumber?.plain || "";
    return (
        <div className="card-surface border border-border p-5" data-testid={`verify-traveler-${index}`}>
            <div className="font-heading text-sm font-bold">
                {traveler.first_name} {traveler.last_name}
            </div>
            <div className="mt-3">
                <CopyField
                    label="File Number"
                    value={plain}
                    hint={fileNumber ? `Belgedeki hâli: ${fileNumber}` : ""}
                    testId={`verify-file-number-${index}`}
                />
                <CopyField
                    label="First Name"
                    value={traveler.first_name}
                    testId={`verify-first-name-${index}`}
                />
                <CopyField
                    label="Date of Birth"
                    value={formatBirthDate(traveler.birth_date)}
                    hint="GG-AA-YYYY"
                    testId={`verify-birth-date-${index}`}
                />
            </div>
        </div>
    );
};

export default function VisaVerify() {
    const { applicationId } = useParams();
    const [params] = useSearchParams();
    const [data, setData] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const res = await api.get(`/visa-verify/${applicationId}`, {
                    params: { t: params.get("t") || "" },
                });
                setData(res.data);
            } catch (err) {
                setError(apiError(err, "Doğrulama bilgileri açılamadı."));
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [applicationId, params]);

    if (loading) {
        return (
            <div className="flex min-h-[60vh] items-center justify-center" data-testid="verify-loading">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="container-page py-16">
                <div
                    className="card-surface mx-auto max-w-xl border border-destructive/30 p-6 text-center"
                    data-testid="verify-error"
                >
                    <AlertCircle className="mx-auto h-8 w-8 text-destructive" />
                    <p className="mt-3 text-sm">{error}</p>
                </div>
            </div>
        );
    }

    const fallback = data.file_numbers?.[0];
    return (
        <div className="container-page py-10 sm:py-14" data-testid="visa-verify-page">
            <div className="max-w-3xl">
                <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                    <ShieldCheck className="h-3.5 w-3.5" /> {data.reference_code}
                </span>
                <h1 className="mt-4 font-heading text-4xl font-bold sm:text-5xl">
                    Vizenizi resmî kaynaktan doğrulayın
                </h1>
                <p className="mt-4 max-w-2xl text-base text-muted-foreground">
                    Bilgilerinizi sizin için hazırladık. Aşağıdaki değerleri tek dokunuşla kopyalayıp
                    Dubai Göçmenlik İdaresi'nin (GDRFA) sorgulama ekranına yapıştırmanız yeterli —
                    belgenizin içinde numara aramanız gerekmez.
                </p>
            </div>

            <div className="mt-8 grid gap-4 sm:grid-cols-2">
                {(data.travelers || []).map((traveler, index) => (
                    <TravelerCard
                        key={index}
                        traveler={traveler}
                        index={index}
                        fallbackNumber={data.travelers.length === 1 ? fallback : null}
                    />
                ))}
            </div>

            {data.travelers?.length > 1 && data.file_numbers?.length > 0 && !data.travelers[0].file_number && (
                <div className="card-surface mt-4 border border-border p-5" data-testid="verify-number-pool">
                    <div className="font-heading text-sm font-bold">Belgedeki dosya numaraları</div>
                    <div className="mt-3">
                        {data.file_numbers.map((number, index) => (
                            <CopyField
                                key={number.plain}
                                label={`File Number ${index + 1}`}
                                value={number.plain}
                                hint={`Belgedeki hâli: ${number.formatted}`}
                                testId={`verify-pool-number-${index}`}
                            />
                        ))}
                    </div>
                </div>
            )}

            <div className="mt-8 max-w-3xl">
                <a href={data.gdrfa_url} target="_blank" rel="noreferrer" data-testid="verify-gdrfa-link">
                    <Button size="lg" className="h-12">
                        GDRFA sorgulama sayfasını aç
                        <ArrowUpRight className="ml-2 h-4 w-4" />
                    </Button>
                </a>
                <ol className="mt-6 space-y-3 border-l-2 border-primary/20 pl-5">
                    {(data.steps || []).map((step, index) => (
                        <li key={index} className="text-sm leading-6" data-testid={`verify-step-${index}`}>
                            <span className="mr-2 font-heading font-bold text-primary">{index + 1}.</span>
                            {step}
                        </li>
                    ))}
                </ol>
                <p className="mt-6 text-xs leading-5 text-muted-foreground">
                    Bu doğrulama zorunlu değildir; vizeniz onaylanmış olarak tarafımıza ulaştı. Sorgulama
                    sayfası Dubai Göçmenlik İdaresi'ne aittir, biz yalnızca bilgilerinizi hazırlıyoruz.
                </p>
            </div>
        </div>
    );
}
