import React, { useEffect, useMemo, useRef, useState } from "react";
import { CalendarDays } from "lucide-react";
import { tr } from "date-fns/locale";
import { Calendar } from "./ui/calendar";
import { Input } from "./ui/input";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";

/* ------------------------------------------------------------------ utils */

const pad = (n) => String(n).padStart(2, "0");

/** Date -> "YYYY-MM-DD" (yerel saat dilimine gore, UTC kaymasi olmadan). */
export const toISODate = (date) =>
    date ? `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` : "";

/** "YYYY-MM-DD" -> Date | null */
export const fromISODate = (iso) => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec((iso || "").slice(0, 10));
    if (!m) return null;
    const [, y, mo, d] = m.map(Number);
    const date = new Date(y, mo - 1, d);
    // 31.02 gibi gecersiz tarihleri ele
    if (date.getFullYear() !== y || date.getMonth() !== mo - 1 || date.getDate() !== d) return null;
    return date;
};

/** "YYYY-MM-DD" -> "GG.AA.YYYY" */
const isoToDisplay = (iso) => {
    const d = fromISODate(iso);
    return d ? `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()}` : "";
};

/**
 * Kullanici girdisini normalize eder.
 * Kabul edilenler: "31.12.2026", "31/12/2026", "31122026", "2026-12-31" (ISO yapistirma
 * ve otomatik test doldurmasi icin).
 * Doner: { display, iso, complete }
 */
const normalizeInput = (raw) => {
    const value = (raw || "").trim();

    // ISO olarak yapistirilmis / programatik doldurulmus deger
    const isoMatch = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(value);
    if (isoMatch) {
        const iso = `${isoMatch[1]}-${pad(isoMatch[2])}-${pad(isoMatch[3])}`;
        return { display: isoToDisplay(iso) || value, iso: fromISODate(iso) ? iso : "", complete: true };
    }

    const digits = value.replace(/\D/g, "").slice(0, 8);
    let display = digits;
    if (digits.length > 4) display = `${digits.slice(0, 2)}.${digits.slice(2, 4)}.${digits.slice(4)}`;
    else if (digits.length > 2) display = `${digits.slice(0, 2)}.${digits.slice(2)}`;

    if (digits.length < 8) return { display, iso: "", complete: false };

    const day = Number(digits.slice(0, 2));
    const month = Number(digits.slice(2, 4));
    const year = Number(digits.slice(4, 8));
    const iso = `${year}-${pad(month)}-${pad(day)}`;
    return { display, iso: fromISODate(iso) ? iso : "", complete: true };
};

/* -------------------------------------------------------------- component */

/**
 * Turkce tarih alani: gg.aa.yyyy formatinda yazilabilir + takvimden secilebilir.
 *
 * Deger sozlesmesi degismedi: `value` ve `onChange` her zaman "YYYY-MM-DD"
 * (veya bos string) kullanir; boylece mevcut form state'i ve API sozlesmesi
 * aynen korunur.
 */
export const DateField = ({
    value = "",
    onChange,
    id,
    disabled = false,
    minDate = null,
    maxDate = null,
    fromYear,
    toYear,
    className = "",
    invalid = false,
    "data-testid": dataTestId,
    ...rest
}) => {
    const [open, setOpen] = useState(false);
    const [text, setText] = useState(() => isoToDisplay(value));
    const [touched, setTouched] = useState(false);
    const lastEmitted = useRef(value);

    // Dis kaynakli deger degisimlerini (OCR autofill, taslak yukleme, reset) yansit
    useEffect(() => {
        if (value !== lastEmitted.current) {
            setText(isoToDisplay(value));
            lastEmitted.current = value;
            if (!value) setTouched(false);
        }
    }, [value]);

    const selected = useMemo(() => fromISODate(value), [value]);

    const emit = (iso) => {
        lastEmitted.current = iso;
        onChange?.(iso);
    };

    const handleText = (e) => {
        const { display, iso, complete } = normalizeInput(e.target.value);
        setText(display);
        if (complete) {
            emit(iso);
        } else if (value) {
            emit("");
        }
    };

    const outOfRange =
        selected &&
        ((minDate && selected < new Date(minDate.getFullYear(), minDate.getMonth(), minDate.getDate())) ||
            (maxDate && selected > new Date(maxDate.getFullYear(), maxDate.getMonth(), maxDate.getDate())));

    const showError = invalid || (touched && text.length > 0 && !value) || outOfRange;

    const currentYear = new Date().getFullYear();
    const disabledMatchers = [];
    if (minDate) disabledMatchers.push({ before: minDate });
    if (maxDate) disabledMatchers.push({ after: maxDate });

    return (
        <div className={`relative ${className}`}>
            <Input
                id={id}
                type="text"
                inputMode="numeric"
                autoComplete="off"
                value={text}
                onChange={handleText}
                onBlur={() => setTouched(true)}
                disabled={disabled}
                placeholder="gg.aa.yyyy"
                aria-invalid={showError ? true : undefined}
                className={`pr-11 ${showError ? "border-destructive focus-visible:ring-destructive/30" : ""}`}
                data-testid={dataTestId}
                {...rest}
            />

            <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                    <button
                        type="button"
                        disabled={disabled}
                        aria-label="Takvimden tarih seç"
                        data-testid={dataTestId ? `${dataTestId}-calendar-button` : undefined}
                        className="absolute right-1 top-1 flex h-[calc(100%-0.5rem)] w-9 items-center justify-center rounded-md text-muted-foreground transition-colors duration-150 hover:bg-muted hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
                    >
                        <CalendarDays className="h-4 w-4" />
                    </button>
                </PopoverTrigger>
                <PopoverContent align="end" className="w-auto p-0" data-testid={dataTestId ? `${dataTestId}-calendar` : undefined}>
                    <Calendar
                        mode="single"
                        locale={tr}
                        weekStartsOn={1}
                        selected={selected || undefined}
                        defaultMonth={selected || minDate || undefined}
                        disabled={disabledMatchers.length ? disabledMatchers : undefined}
                        captionLayout="dropdown-buttons"
                        classNames={{
                            // react-day-picker'in gorsel-gizli etiketleri: CSS import edilmedigi
                            // icin ekranda gorunuyordu, sr-only ile gizliyoruz.
                            vhidden: "sr-only",
                            caption_label: "hidden",
                            caption: "relative flex items-center justify-center gap-2 pt-1",
                            caption_dropdowns: "flex items-center gap-2",
                            dropdown:
                                "h-9 cursor-pointer rounded-lg border border-border bg-card px-2 text-sm font-semibold text-foreground transition-colors duration-150 hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                            day_today: "bg-muted font-bold text-foreground",
                        }}
                        fromYear={fromYear ?? (minDate ? minDate.getFullYear() : currentYear - 90)}
                        toYear={toYear ?? (maxDate ? maxDate.getFullYear() : currentYear + 5)}
                        onSelect={(date) => {
                            if (!date) return;
                            const iso = toISODate(date);
                            setText(isoToDisplay(iso));
                            setTouched(true);
                            emit(iso);
                            setOpen(false);
                        }}
                    />
                </PopoverContent>
            </Popover>

            {showError && (
                <p className="mt-1.5 text-xs font-medium text-destructive" data-testid={dataTestId ? `${dataTestId}-error` : undefined}>
                    {outOfRange ? "Bu tarih seçilebilir aralığın dışında." : "Geçerli bir tarih girin (gg.aa.yyyy)."}
                </p>
            )}
        </div>
    );
};

export default DateField;
