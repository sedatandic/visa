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

const trLong = new Intl.DateTimeFormat("tr-TR", { day: "2-digit", month: "long", year: "numeric", weekday: "long" });
const longLabel = (date) => trLong.format(date);

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

    const pick = (iso) => {
        setText(isoToDisplay(iso));
        setTouched(true);
        emit(iso);
        setOpen(false);
    };

    const today = new Date();
    const todayBlocked =
        (minDate && today < new Date(minDate.getFullYear(), minDate.getMonth(), minDate.getDate())) ||
        (maxDate && today > new Date(maxDate.getFullYear(), maxDate.getMonth(), maxDate.getDate()));

    return (
        <div className={className}>
            <div className="relative">
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
                className={`pr-12 sm:pr-11 ${showError ? "border-destructive focus-visible:ring-destructive/30" : ""}`}
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
                        className="absolute right-0 top-0 flex h-full w-12 items-center justify-center rounded-r-[var(--radius)] text-muted-foreground transition-colors duration-150 hover:bg-muted hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 sm:right-1 sm:top-1 sm:h-[calc(100%-0.5rem)] sm:w-9 sm:rounded-md"
                    >
                        <CalendarDays className="h-4 w-4" />
                    </button>
                </PopoverTrigger>
                <PopoverContent
                    align="end"
                    sideOffset={8}
                    className="w-auto overflow-hidden rounded-2xl border-border/70 p-0 shadow-[0_28px_60px_-28px_hsl(var(--brand-black)/0.35)]"
                    data-testid={dataTestId ? `${dataTestId}-calendar` : undefined}
                >
                    <Calendar
                        mode="single"
                        locale={tr}
                        weekStartsOn={1}
                        selected={selected || undefined}
                        defaultMonth={selected || minDate || undefined}
                        disabled={disabledMatchers.length ? disabledMatchers : undefined}
                        captionLayout="dropdown-buttons"
                        className="p-3.5"
                        classNames={{
                            // react-day-picker'in gorsel-gizli etiketleri: CSS import edilmedigi
                            // icin ekranda gorunuyordu, sr-only ile gizliyoruz.
                            vhidden: "sr-only",
                            caption_label: "hidden",
                            caption: "relative mb-3 flex items-center justify-center gap-2",
                            caption_dropdowns: "flex items-center gap-2",
                            dropdown:
                                "h-9 cursor-pointer appearance-none rounded-full border border-border/80 bg-[hsl(var(--cloud))] px-3 pr-7 text-sm font-semibold text-foreground outline-none transition-colors duration-200 hover:border-primary/50 hover:text-primary focus-visible:border-primary focus-visible:ring-0",
                            nav: "flex items-center",
                            nav_button:
                                "flex h-8 w-8 items-center justify-center rounded-full border border-border/70 bg-card text-muted-foreground transition-colors duration-200 hover:border-primary/50 hover:bg-primary/10 hover:text-primary disabled:opacity-30",
                            nav_button_previous: "absolute left-0",
                            nav_button_next: "absolute right-0",
                            head_cell:
                                "w-9 text-[10px] font-bold uppercase tracking-[0.08em] text-muted-foreground",
                            row: "mt-1 flex w-full",
                            cell: "relative p-0 text-center",
                            day: "flex h-9 w-9 items-center justify-center rounded-full text-sm font-medium text-foreground transition-colors duration-200 hover:bg-primary/10 hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40",
                            day_selected:
                                "bg-primary font-bold text-primary-foreground shadow-[0_6px_16px_-6px_hsl(var(--brand-black)/0.45)] hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground",
                            day_today: "font-bold text-primary ring-1 ring-inset ring-primary/45",
                            day_outside: "text-muted-foreground/40",
                            day_disabled: "text-muted-foreground/30 hover:bg-transparent hover:text-muted-foreground/30",
                        }}
                        fromYear={fromYear ?? (minDate ? minDate.getFullYear() : currentYear - 90)}
                        toYear={toYear ?? (maxDate ? maxDate.getFullYear() : currentYear + 5)}
                        onSelect={(date) => {
                            if (!date) return;
                            pick(toISODate(date));
                        }}
                    />
                    <div className="flex items-center justify-between gap-3 border-t border-border/70 bg-[hsl(var(--cloud))] px-3.5 py-2.5">
                        <span className="text-xs font-semibold text-muted-foreground" data-testid={dataTestId ? `${dataTestId}-calendar-label` : undefined}>
                            {selected ? longLabel(selected) : "Tarih seçilmedi"}
                        </span>
                        <span className="flex items-center gap-1">
                            <button
                                type="button"
                                onClick={() => pick(toISODate(new Date()))}
                                disabled={todayBlocked}
                                className="rounded-full px-2.5 py-1 text-xs font-bold text-primary transition-colors duration-200 hover:bg-primary/10 disabled:pointer-events-none disabled:opacity-40"
                                data-testid={dataTestId ? `${dataTestId}-calendar-today` : undefined}
                            >
                                Bugün
                            </button>
                            <button
                                type="button"
                                onClick={() => {
                                    setText("");
                                    setTouched(false);
                                    emit("");
                                    setOpen(false);
                                }}
                                className="rounded-full px-2.5 py-1 text-xs font-semibold text-muted-foreground transition-colors duration-200 hover:bg-muted hover:text-foreground"
                                data-testid={dataTestId ? `${dataTestId}-calendar-clear` : undefined}
                            >
                                Temizle
                            </button>
                        </span>
                    </div>
                </PopoverContent>
            </Popover>
            </div>

            {showError && (
                <p className="mt-1.5 text-xs font-medium text-destructive" data-testid={dataTestId ? `${dataTestId}-error` : undefined}>
                    {outOfRange ? "Bu tarih seçilebilir aralığın dışında." : "Geçerli bir tarih girin (gg.aa.yyyy)."}
                </p>
            )}
        </div>
    );
};

export default DateField;
