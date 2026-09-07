import React from "react";
import { ShieldCheck } from "lucide-react";
import { DateField } from "./DateField";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { cleanTckn, validTckn } from "../lib/tckn";

// Poliçe kesimi için sigortalı kimlik bilgileri (Tamamliyo TC kimlik no + doğum tarihi ister).
export const InsuredIdentityFields = ({
    rows,
    onChange,
    withNameAndBirth = false,
    testIdPrefix = "insured",
}) => (
    <div className="mt-4 space-y-3" data-testid={`${testIdPrefix}-fields`}>
        {rows.map((row) => {
            const digits = cleanTckn(row.tc_kimlik_no);
            const invalid = digits.length > 0 && !validTckn(digits);
            return (
                <div
                    key={row.key}
                    className="rounded-xl border border-border bg-muted/30 p-4"
                    data-testid={`${testIdPrefix}-row-${row.key}`}
                >
                    <p className="flex items-center gap-2 text-sm font-semibold">
                        <ShieldCheck className="h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                        {row.label}
                    </p>
                    <div className={`mt-3 grid gap-3 ${withNameAndBirth ? "sm:grid-cols-3" : "sm:max-w-xs"}`}>
                        {withNameAndBirth && (
                            <div className="space-y-1.5">
                                <Label className="text-xs">Ad soyad</Label>
                                <Input
                                    value={row.full_name || ""}
                                    onChange={(e) => onChange(row.key, { full_name: e.target.value })}
                                    placeholder={row.namePlaceholder || "Ad soyad"}
                                    data-testid={`${testIdPrefix}-name-${row.key}`}
                                />
                            </div>
                        )}
                        <div className="space-y-1.5">
                            <Label className="text-xs">TC kimlik no</Label>
                            <Input
                                inputMode="numeric"
                                maxLength={11}
                                value={digits}
                                onChange={(e) => onChange(row.key, { tc_kimlik_no: cleanTckn(e.target.value) })}
                                placeholder="11 hane"
                                aria-invalid={invalid || undefined}
                                data-testid={`${testIdPrefix}-tckn-${row.key}`}
                            />
                            {invalid && (
                                <p
                                    className="text-xs font-semibold text-destructive"
                                    data-testid={`${testIdPrefix}-tckn-error-${row.key}`}
                                >
                                    Geçerli bir TC kimlik numarası girin.
                                </p>
                            )}
                        </div>
                        {withNameAndBirth && (
                            <div className="space-y-1.5">
                                <Label className="text-xs">Doğum tarihi</Label>
                                <DateField
                                    value={row.birth_date || ""}
                                    onChange={(iso) => onChange(row.key, { birth_date: iso })}
                                    maxDate={new Date()}
                                    fromYear={new Date().getFullYear() - 100}
                                    toYear={new Date().getFullYear()}
                                    data-testid={`${testIdPrefix}-birth-${row.key}`}
                                />
                            </div>
                        )}
                    </div>
                </div>
            );
        })}
    </div>
);
