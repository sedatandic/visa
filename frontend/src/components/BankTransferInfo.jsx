import React from "react";
import { Building2, Landmark } from "lucide-react";

const Row = ({ label, value, mono, testId }) =>
    value ? (
        <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border/70 py-2 last:border-0">
            <dt className="text-xs uppercase tracking-wide text-muted-foreground">{label}</dt>
            <dd
                className={`text-right text-sm font-semibold ${mono ? "font-mono-code" : ""}`}
                data-testid={testId}
            >
                {value}
            </dd>
        </div>
    ) : null;

/** Havale/EFT secildiginde gosterilen sirket + banka bilgileri. */
export const BankTransferInfo = ({ bank, agencyItems = [], amount, amountLabel = "Ödenecek tutar" }) => {
    if (!bank) return null;

    return (
        <div
            className="mt-4 rounded-xl border border-primary/30 bg-primary/[0.05] p-5"
            data-testid="bank-transfer-info"
        >
            <h4 className="flex items-center gap-2 font-heading text-sm font-bold">
                <Landmark className="h-4 w-4 text-primary" aria-hidden="true" />
                {bank.title || "Havale / EFT ile ödeme"}
            </h4>

            <dl className="mt-3">
                <Row label="Alıcı / Şirket" value={bank.account_name} testId="bank-account-name" />
                <Row label="Banka" value={bank.bank_name} testId="bank-name" />
                <Row label="IBAN" value={bank.iban} mono testId="bank-iban" />
                {amount ? <Row label={amountLabel} value={amount} testId="bank-amount" /> : null}
            </dl>

            {agencyItems.length > 0 && (
                <div className="mt-4 rounded-lg border border-border bg-card p-4" data-testid="bank-agency-info">
                    <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wide text-muted-foreground">
                        <Building2 className="h-3.5 w-3.5 text-primary" aria-hidden="true" /> Şirket bilgileri
                    </p>
                    <dl className="mt-2">
                        {agencyItems.map((item) => (
                            <Row
                                key={item.label}
                                label={item.label}
                                value={item.value}
                                testId={`agency-row-${item.label}`}
                            />
                        ))}
                    </dl>
                </div>
            )}

            {bank.note && (
                <p className="mt-3 text-xs leading-5 text-muted-foreground">{bank.note}</p>
            )}
        </div>
    );
};
