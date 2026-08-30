import React from "react";
import { STATUS_META } from "../lib/site";

export const StatusBadge = ({ status, testId = "application-status-badge" }) => {
    const meta = STATUS_META[status] || {
        label: status || "-",
        className: "bg-muted text-foreground border-border",
    };
    return (
        <span
            data-testid={testId}
            className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${meta.className}`}
        >
            {meta.label}
        </span>
    );
};

export const PaymentBadge = ({ status, testId = "payment-status-badge" }) => {
    const paid = status === "paid";
    return (
        <span
            data-testid={testId}
            className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${
                paid
                    ? "border-[hsl(var(--brand-green)/0.30)] bg-[hsl(var(--brand-green)/0.13)] text-[hsl(var(--brand-green))]"
                    : "border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.15)] text-[hsl(var(--status-warning))]"
            }`}
        >
            {paid ? "Ödendi" : "Ödeme Bekliyor"}
        </span>
    );
};
