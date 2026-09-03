import React from "react";
import {
    Anchor,
    BedDouble,
    Building2,
    CarFront,
    Compass,
    Landmark,
    MapPinned,
    PlaneTakeoff,
    Activity,
    Ticket,
    Waves,
    Wind,
} from "lucide-react";

const SERVICE_ICONS = {
    visa: PlaneTakeoff,
    tour: MapPinned,
    hotel: BedDouble,
    transfer: CarFront,
    citytour: Building2,
    activity: Activity,
};

const TOUR_ICONS = {
    helicopter: Wind,
    safari: Compass,
    yacht: Anchor,
    jetski: Waves,
    tickets: Ticket,
    city: Landmark,
};

export const IconTile = ({ icon: Icon, tone = "teal" }) => {
    const tones = {
        teal: "bg-primary/10 text-primary",
        sand: "bg-[hsl(var(--sand-surface))] text-[hsl(var(--navy))]",
        gold: "bg-[hsl(var(--brand-copper)/0.10)] text-[hsl(var(--brand-copper))]",
    };
    return (
        <span className={`flex h-12 w-12 items-center justify-center rounded-xl ${tones[tone]}`}>
            <Icon className="h-6 w-6" />
        </span>
    );
};

export const ServiceCard = ({ item }) => {
    const Icon = SERVICE_ICONS[item.key] || Compass;
    return (
        <div className="card-surface card-hoverable p-6" data-testid={`service-card-${item.key}`}>
            <IconTile icon={Icon} tone="teal" />
            <h3 className="mt-4 font-heading text-base font-semibold">{item.title}</h3>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.detail}</p>
        </div>
    );
};

export const TourCard = ({ item }) => {
    const Icon = TOUR_ICONS[item.key] || Compass;
    return (
        <div
            className="group relative overflow-hidden rounded-xl border border-border bg-card p-6 transition-shadow duration-200"
            style={{ boxShadow: "var(--shadow-card)" }}
            data-testid={`tour-card-${item.key}`}
        >
            <span
                className="absolute -right-8 -top-8 h-28 w-28 rounded-full bg-primary/5 transition-transform duration-300 group-hover:scale-110"
                aria-hidden="true"
            />
            <IconTile icon={Icon} tone="sand" />
            <h3 className="relative mt-4 font-heading text-base font-semibold">{item.title}</h3>
            <p className="relative mt-2 text-sm leading-6 text-muted-foreground">{item.detail}</p>
        </div>
    );
};
