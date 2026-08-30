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
                    ? "border-[rgba(22,163,74,0.35)] bg-[rgba(22,163,74,0.16)] text-[#14532D]"
                    : "border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.18)] text-[#7A4B00]"
            }`}
        >
            {paid ? "Ödendi" : "Ödeme Bekliyor"}
        </span>
    );
};
