import React from "react";
import { Eye, Link2, MousePointerClick, Wallet } from "lucide-react";
import { formatMoney } from "../lib/site";

const Tile = ({ icon: Icon, label, value, note, testId, tone }) => (
    <div className="rounded-2xl border border-border bg-card p-4" data-testid={testId}>
        <p className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wide text-muted-foreground">
            <Icon className="h-3.5 w-3.5" aria-hidden="true" /> {label}
        </p>
        <p
            className={`mt-1.5 font-heading text-2xl font-extrabold ${
                tone === "primary" ? "text-primary" : ""
            }`}
        >
            {value}
        </p>
        {note && <p className="mt-0.5 text-xs text-muted-foreground">{note}</p>}
    </div>
);

/** Admin → Teklif Linkleri sayfasindaki donusum raporu serit. */
export const OfferReport = ({ report }) => {
    if (!report || !report.total) return null;
    const currency = report.currency || "TRY";
    const avgOpen = report.avg_open_hours;
    const openNote =
        avgOpen == null
            ? `${report.views} görüntülenme`
            : `${report.views} görüntülenme · ortalama ${
                  avgOpen < 1 ? `${Math.max(1, Math.round(avgOpen * 60))} dakikada` : `${avgOpen} saatte`
              } açılıyor`;

    return (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4" data-testid="offer-report">
            <Tile
                icon={Link2}
                label="Gönderilen teklif"
                value={report.total}
                note={`${formatMoney(report.offered_value, currency)} toplam teklif tutarı`}
                testId="offer-report-total"
            />
            <Tile
                icon={Eye}
                label="Açılan"
                value={`${report.opened} · %${report.open_rate}`}
                note={openNote}
                testId="offer-report-opened"
            />
            <Tile
                icon={MousePointerClick}
                label="Başvuruya dönen"
                value={`${report.converted} · %${report.conversion_rate}`}
                note={`Açılan tekliflerin %${report.converted_of_opened}'i`}
                testId="offer-report-converted"
                tone="primary"
            />
            <Tile
                icon={Wallet}
                label="Dönüşen tutar"
                value={formatMoney(report.converted_value, currency)}
                note={`${report.not_opened} teklif hiç açılmadı`}
                testId="offer-report-value"
            />
        </div>
    );
};
