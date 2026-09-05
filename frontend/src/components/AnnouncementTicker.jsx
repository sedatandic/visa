import React from "react";
import { BadgeCheck, Clock, FileText, PlaneTakeoff, ShieldCheck, Wifi } from "lucide-react";

const ITEMS = [
    { icon: BadgeCheck, text: "TÜRSAB üyesi A grubu seyahat acentesi" },
    { icon: Clock, text: "Ekspres başvuruda ~8 mesai saatinde sonuç" },
    { icon: FileText, text: "Sadece pasaport ve fotoğrafınızla başvurun" },
    { icon: PlaneTakeoff, text: "Uçak bileti ve otel rezervasyonu şartı yok" },
    { icon: Wifi, text: "eSIM ve seyahat sigortası aynı sepette" },
    { icon: ShieldCheck, text: "Pasaportunuz sizde kalır, kargoya vermezsiniz" },
];

const Row = ({ ariaHidden }) => (
    <div className="flex shrink-0 items-center gap-10 pr-10" aria-hidden={ariaHidden || undefined}>
        {ITEMS.map(({ icon: Icon, text }) => (
            <span key={text} className="flex items-center gap-2 whitespace-nowrap text-xs font-semibold">
                <Icon className="h-3.5 w-3.5 shrink-0 opacity-80" aria-hidden="true" />
                {text}
            </span>
        ))}
    </div>
);

export const AnnouncementTicker = () => (
    <div
        className="relative overflow-hidden border-b border-border bg-[hsl(var(--panel-2))] text-[hsl(var(--charcoal))]"
        data-testid="announcement-ticker"
    >
        <div className="ticker-track flex w-max items-center py-2">
            <Row />
            <Row ariaHidden />
        </div>
    </div>
);
