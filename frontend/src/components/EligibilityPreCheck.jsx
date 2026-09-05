import React, { useMemo, useState } from "react";
import { AlertTriangle, CalendarClock, CheckCircle2, ShieldCheck } from "lucide-react";
import { DateField, fromISODate } from "./DateField";
import { Button } from "./ui/button";
import { Label } from "./ui/label";
import { Switch } from "./ui/switch";
import { formatDate, formatMoney } from "../lib/site";

const MIN_PASSPORT_MONTHS = 6;

const addMonths = (date, months) => {
    const next = new Date(date);
    next.setMonth(next.getMonth() + months);
    return next;
};

/**
 * Basvurunun en basinda calisan uygunluk on kontrolu: tarihler + pasaport gecerliligi.
 * Uygunsa onerilen vizeyi bildirir ve bilgileri forma tasir.
 */
export const EligibilityPreCheck = ({ visaTypes = [], expressAddon = null, onApply }) => {
    const [arrival, setArrival] = useState("");
    const [departure, setDeparture] = useState("");
    const [expiry, setExpiry] = useState("");
    const [express, setExpress] = useState(true);

    const result = useMemo(() => {
        const start = fromISODate(arrival);
        const end = fromISODate(departure);
        const passport = fromISODate(expiry);
        if (!start || !end || !passport) return null;
        if (end < start) return { status: "error", title: "Dönüş tarihi gidiş tarihinden önce olamaz." };

        const stayDays = Math.round((end - start) / 86400000) + 1;
        const required = addMonths(end, MIN_PASSPORT_MONTHS);
        if (passport < required) {
            return {
                status: "error",
                title: "Pasaportunuz bu seyahat için yeterli değil.",
                detail: `Pasaportun dönüş tarihinden itibaren en az ${MIN_PASSPORT_MONTHS} ay geçerli olması gerekir. Bu tarihler için en az ${formatDate(
                    required
                )} tarihine kadar geçerli bir pasaport gerekiyor.`,
            };
        }

        const adultSingle = visaTypes
            .filter(
                (v) =>
                    v.applicant_type !== "child" &&
                    (v.category || "single") === "single" &&
                    v.auto_suggest !== false &&
                    Number(v.duration_days) >= stayDays
            )
            .sort((a, b) => Number(a.duration_days) - Number(b.duration_days));
        const visa = adultSingle[0] || null;

        if (!visa) {
            return {
                status: "warning",
                title: `Planlanan kalış ${stayDays} gün.`,
                detail:
                    "60 günden uzun kalışlarda 60 günlük vize ile giriş yapıp Dubai'deyken yurt içi uzatma yapılması gerekir. Danışmanımız süreci sizin için planlar.",
                stayDays,
            };
        }

        return {
            status: "ok",
            title: "Başvurunuz için uygun görünüyor.",
            detail: `Planlanan kalış ${stayDays} gün. Bu süre için önerilen vize: ${visa.name} · ${formatMoney(
                visa.price,
                visa.currency
            )} (kişi başı).`,
            stayDays,
            visa,
            hoursToDeparture: Math.round((start - new Date()) / 3600000),
        };
    }, [arrival, departure, expiry, visaTypes]);

    return (
        <div
            className="rounded-xl border border-primary/25 bg-primary/5 p-5"
            data-testid="eligibility-precheck"
        >
            <div className="flex items-start gap-2.5">
                <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-primary" aria-hidden="true" />
                <div>
                    <h3 className="font-heading text-sm font-bold">Uygunluk ön kontrolü</h3>
                    <p className="mt-1 text-xs leading-5 text-muted-foreground">
                        Tarihlerinizi ve pasaport geçerliliğinizi girin; forma başlamadan uygun olup
                        olmadığınızı ve hangi vizenin gerektiğini söyleyelim.
                    </p>
                </div>
            </div>

            <div className="mt-4 grid gap-4 sm:grid-cols-3">
                <div className="space-y-2">
                    <Label>Gidiş tarihi</Label>
                    <DateField
                        value={arrival}
                        onChange={setArrival}
                        minDate={new Date()}
                        fromYear={new Date().getFullYear()}
                        toYear={new Date().getFullYear() + 3}
                        data-testid="precheck-arrival-date"
                    />
                </div>
                <div className="space-y-2">
                    <Label>Dönüş tarihi</Label>
                    <DateField
                        value={departure}
                        onChange={setDeparture}
                        minDate={fromISODate(arrival) || new Date()}
                        fromYear={new Date().getFullYear()}
                        toYear={new Date().getFullYear() + 3}
                        data-testid="precheck-departure-date"
                    />
                </div>
                <div className="space-y-2">
                    <Label>Pasaport geçerlilik tarihi</Label>
                    <DateField
                        value={expiry}
                        onChange={setExpiry}
                        minDate={new Date()}
                        fromYear={new Date().getFullYear()}
                        toYear={new Date().getFullYear() + 15}
                        data-testid="precheck-passport-expiry"
                    />
                </div>
            </div>

            {result && (
                <div
                    className={`mt-4 flex items-start gap-2.5 rounded-xl border p-4 ${
                        result.status === "ok"
                            ? "border-[hsl(var(--brand-green)/0.35)] bg-[hsl(var(--brand-green)/0.08)]"
                            : "border-[hsl(var(--status-warning)/0.4)] bg-[hsl(var(--status-warning)/0.1)]"
                    }`}
                    data-testid={`precheck-result-${result.status}`}
                    role="status"
                >
                    {result.status === "ok" ? (
                        <CheckCircle2 className="mt-0.5 h-4.5 w-4.5 shrink-0 text-[hsl(var(--brand-green))]" />
                    ) : (
                        <AlertTriangle className="mt-0.5 h-4.5 w-4.5 shrink-0 text-[hsl(var(--status-warning))]" />
                    )}
                    <div className="min-w-0">
                        <p className="text-sm font-bold">{result.title}</p>
                        {result.detail && (
                            <p className="mt-1 text-sm leading-6 text-muted-foreground">{result.detail}</p>
                        )}
                        {result.status === "ok" && (
                            <>
                                {result.hoursToDeparture <= 72 && (
                                    <label
                                        className="mt-3 flex cursor-pointer items-start gap-3 rounded-xl border border-[hsl(var(--status-warning)/0.4)] bg-[hsl(var(--status-warning)/0.1)] p-4 text-sm"
                                        data-testid="precheck-express-suggestion"
                                    >
                                        <Switch
                                            checked={express}
                                            onCheckedChange={(c) => setExpress(!!c)}
                                            data-testid="precheck-express-switch"
                                        />
                                        <span className="leading-6">
                                            <strong className="block">
                                                Uçuşunuza {Math.max(result.hoursToDeparture, 0)} saat kaldı —
                                                ekspres hizmeti öneriyoruz.
                                            </strong>
                                            Standart başvuru ortalama 2 iş günü sürer; ekspres hizmetle sonuç
                                            yaklaşık 8 mesai saatinde çıkar
                                            {expressAddon
                                                ? ` (kişi başı ${formatMoney(expressAddon.price, expressAddon.currency)})`
                                                : ""}
                                            . Devam ettiğinizde ekspres hizmet otomatik seçilir.
                                        </span>
                                    </label>
                                )}
                                <Button
                                    type="button"
                                    className="mt-3 h-10"
                                    onClick={() =>
                                        onApply({
                                            arrival_date: arrival,
                                            departure_date: departure,
                                            passport_expiry: expiry,
                                            visa: result.visa,
                                            express: result.hoursToDeparture <= 72 && express,
                                        })
                                    }
                                    data-testid="precheck-continue-button"
                                >
                                    <CalendarClock className="mr-2 h-4 w-4" /> Bu bilgilerle devam et
                                </Button>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};
