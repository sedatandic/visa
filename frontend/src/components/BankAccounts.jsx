import React, { useState } from "react";
import { Check, ChevronDown, Copy, Info, Landmark } from "lucide-react";
import { toast } from "sonner";

const CURRENCY_LABEL = { TRY: "TL", USD: "USD", EUR: "EUR" };

const IbanRow = ({ bankId, account }) => {
    const [copied, setCopied] = useState(false);
    const code = CURRENCY_LABEL[account.currency] || account.currency;

    const copy = async () => {
        try {
            await navigator.clipboard.writeText((account.iban || "").replace(/\s/g, ""));
            setCopied(true);
            toast.success(`${code} IBAN kopyalandı.`);
            setTimeout(() => setCopied(false), 2000);
        } catch {
            toast.error("Kopyalanamadı, IBAN'ı elle seçebilirsiniz.");
        }
    };

    return (
        <div className="flex items-center gap-3 rounded-xl border border-border bg-[hsl(var(--cloud))] p-3">
            <span className="flex h-10 w-14 shrink-0 items-center justify-center rounded-lg bg-primary text-xs font-bold text-primary-foreground">
                {code}
            </span>
            <span
                className="font-mono-code flex-1 text-sm tracking-wide sm:text-base"
                data-testid={`bank-iban-${bankId}-${account.currency}`}
            >
                {account.iban}
            </span>
            <button
                type="button"
                onClick={copy}
                aria-label={`${code} IBAN'ı kopyala`}
                data-testid={`bank-copy-${bankId}-${account.currency}`}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-primary/40 text-primary transition-colors duration-150 hover:bg-primary/10"
            >
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
            </button>
        </div>
    );
};

/** Havale/EFT icin banka hesaplari: logo + katlanabilir IBAN listesi. */
export const BankAccounts = ({ bank, footNote }) => {
    const banks = bank?.banks || [];
    const [openId, setOpenId] = useState(banks[0]?.id || banks[0]?.name || null);
    if (!banks.length) return null;

    return (
        <div className="space-y-4" data-testid="bank-accounts-section">
            {banks.map((b) => {
                const id = b.id || b.name;
                const open = openId === id;
                return (
                    <div key={id} className="card-surface overflow-hidden" data-testid={`bank-card-${id}`}>
                        <button
                            type="button"
                            onClick={() => setOpenId(open ? null : id)}
                            aria-expanded={open}
                            data-testid={`bank-toggle-${id}`}
                            className="flex w-full items-center gap-4 p-5 text-left transition-colors duration-150 hover:bg-[hsl(var(--cloud))]"
                        >
                            <span className="flex h-12 w-20 shrink-0 items-center justify-center rounded-lg border border-border bg-white p-1.5">
                                {b.logo ? (
                                    <img
                                        src={b.logo}
                                        alt={`${b.name} logosu`}
                                        className="max-h-full max-w-full object-contain"
                                        loading="lazy"
                                    />
                                ) : (
                                    <Landmark className="h-5 w-5 text-primary" />
                                )}
                            </span>
                            <span className="flex-1 font-heading text-base font-bold">{b.name}</span>
                            <ChevronDown
                                className={`h-5 w-5 shrink-0 text-primary transition-transform duration-200 ${
                                    open ? "rotate-180" : ""
                                }`}
                            />
                        </button>

                        {open && (
                            <div className="border-t border-border p-5 pt-4" data-testid={`bank-body-${id}`}>
                                {bank.account_name && (
                                    <p className="text-sm">
                                        <span className="font-bold">Hesap sahibi:</span>{" "}
                                        <span className="text-muted-foreground" data-testid={`bank-account-name-${id}`}>
                                            {bank.account_name}
                                        </span>
                                    </p>
                                )}
                                {(bank.notes || []).length > 0 && (
                                    <ul className="mt-3 space-y-1.5">
                                        {bank.notes.map((n, i) => (
                                            <li key={i} className="text-xs leading-5 text-muted-foreground">
                                                * {n}
                                            </li>
                                        ))}
                                    </ul>
                                )}
                                <div className="mt-4 space-y-3">
                                    {(b.accounts || []).map((acc) => (
                                        <IbanRow key={`${acc.currency}-${acc.iban}`} bankId={id} account={acc} />
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                );
            })}

            {footNote && (
                <p
                    className="flex items-center justify-center gap-2 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4 text-center text-sm text-muted-foreground"
                    data-testid="bank-accounts-footnote"
                >
                    <Info className="h-4 w-4 shrink-0 text-primary" />
                    {footNote}
                </p>
            )}
        </div>
    );
};
