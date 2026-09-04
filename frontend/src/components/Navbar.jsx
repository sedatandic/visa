import React, { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import {
    BookOpen,
    ChevronDown,
    FileCheck2,
    HelpCircle,
    Info,
    Mail,
    Menu,
    Newspaper,
    Phone,
    Search,
    Smartphone,
    UserRound,
    Wrench,
} from "lucide-react";
import { Button } from "./ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "./ui/sheet";
import { COMPANY } from "../lib/site";
import { BrandMark } from "./BrandMark";
import { UaeFlag } from "./FlagIcons";
import { useContact } from "../lib/contact";

/** Ust seviyede gorunen ana linkler (donusum odakli). */
const PRIMARY_LINKS = [
    { to: "/vize-tipleri", label: "Hizmet Bedelleri", icon: FileCheck2 },
    { to: "/takip", label: "Başvuru Takip", icon: Search },
];

/** "Bilgi & Hizmetler" menusu altinda toplanan linkler. */
const MENU_GROUPS = [
    {
        label: "Vize Bilgileri",
        items: [
            { to: "/gerekli-belgeler", label: "Gerekli Belgeler", icon: BookOpen },
            { to: "/hizmetler", label: "Hizmetler", icon: Wrench },
            { to: "/sss", label: "S.S.S.", icon: HelpCircle },
        ],
    },
    {
        label: "Yanınızdaki Ekstralar",
        items: [{ to: "/esim", label: "eSIM & Sigorta", icon: Smartphone }],
    },
    {
        label: "Kurumsal",
        items: [
            { to: "/gelismeler", label: "Gelişmeler", icon: Newspaper },
            { to: "/hakkimizda", label: "Hakkımızda", icon: Info },
            { to: "/iletisim", label: "İletişim", icon: Mail },
        ],
    },
];

const MENU_LINKS = MENU_GROUPS.flatMap((g) => g.items);
const testId = (to) => `nav-link-${to.replace("/", "")}`;

const navLinkClass = ({ isActive }) =>
    `whitespace-nowrap rounded-lg px-3 py-2 text-base font-semibold transition-colors duration-150 focus-visible:outline-none ${
        isActive
            ? "bg-primary/10 text-primary"
            : "text-foreground/75 hover:bg-muted hover:text-foreground"
    }`;

export const Navbar = () => {
    const contact = useContact();
    const [open, setOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const location = useLocation();

    useEffect(() => setOpen(false), [location.pathname]);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 8);
        onScroll();
        window.addEventListener("scroll", onScroll);
        return () => window.removeEventListener("scroll", onScroll);
    }, []);

    const menuActive = MENU_LINKS.some((l) => location.pathname.startsWith(l.to));

    return (
        <header
            className={`sticky top-0 z-40 w-full border-b bg-background/85 backdrop-blur-xl transition-shadow duration-200 ${
                scrolled
                    ? "border-border shadow-[0_4px_18px_rgba(11,15,20,0.07)]"
                    : "border-transparent"
            }`}
            data-testid="site-navbar"
        >
            <div className="flag-strip" aria-hidden="true" />
            <div className="container-page flex h-[92px] items-center justify-between gap-4">
                <Link
                    to="/"
                    className="flex shrink-0 items-center gap-2.5 rounded-lg focus-visible:outline-none"
                    data-testid="navbar-logo-link"
                >
                    <BrandMark />
                    <UaeFlag className="ml-1 hidden h-6 w-10 sm:block" />
                </Link>

                <nav className="hidden items-center gap-1 xl:flex" aria-label="Ana menü">
                    {PRIMARY_LINKS.map((l) => (
                        <NavLink key={l.to} to={l.to} data-testid={testId(l.to)} className={navLinkClass}>
                            {l.label}
                        </NavLink>
                    ))}

                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <button
                                type="button"
                                data-testid="navbar-more-menu-trigger"
                                className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-lg px-3 py-2 text-base font-semibold transition-colors duration-150 focus-visible:outline-none ${
                                    menuActive
                                        ? "bg-primary/10 text-primary"
                                        : "text-foreground/75 hover:bg-muted hover:text-foreground"
                                }`}
                            >
                                Bilgi &amp; Hizmetler
                                <ChevronDown className="h-3.5 w-3.5" aria-hidden="true" />
                            </button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent
                            align="start"
                            className="w-64 rounded-xl p-1.5"
                            data-testid="navbar-more-menu"
                        >
                            {MENU_GROUPS.map((group, gi) => (
                                <React.Fragment key={group.label}>
                                    {gi > 0 && <DropdownMenuSeparator />}
                                    <DropdownMenuLabel className="text-[11px] font-bold uppercase tracking-[0.12em] text-muted-foreground">
                                        {group.label}
                                    </DropdownMenuLabel>
                                    {group.items.map(({ to, label, icon: Icon }) => (
                                        <DropdownMenuItem key={to} asChild className="rounded-lg">
                                            <Link
                                                to={to}
                                                data-testid={testId(to)}
                                                className="flex w-full cursor-pointer items-center gap-2.5 py-2 text-sm font-medium"
                                            >
                                                <Icon className="h-4 w-4 text-primary" aria-hidden="true" />
                                                {label}
                                            </Link>
                                        </DropdownMenuItem>
                                    ))}
                                </React.Fragment>
                            ))}
                        </DropdownMenuContent>
                    </DropdownMenu>

                    <NavLink to="/hesabim" data-testid={testId("/hesabim")} className={navLinkClass}>
                        Başvurularım
                    </NavLink>
                </nav>

                <div className="hidden items-center gap-2.5 md:flex">
                    {contact.phone && (
                    <a
                        href={contact.phoneHref}
                        className="hidden items-center gap-2 whitespace-nowrap rounded-lg px-2 py-2 text-base font-semibold text-foreground/75 transition-colors duration-150 hover:text-primary 2xl:flex"
                        data-testid="navbar-phone-link"
                    >
                        <Phone className="h-4 w-4 text-[hsl(var(--brand-copper))]" aria-hidden="true" />
                        {contact.phone}
                    </a>
                    )}
                    <Button asChild className="h-12 px-6 text-base" data-testid="navbar-apply-button">
                        <Link to="/basvuru">Başvuru Yap</Link>
                    </Button>
                </div>

                <Sheet open={open} onOpenChange={setOpen}>
                    <SheetTrigger asChild>
                        <button
                            type="button"
                            className="flex h-11 w-11 items-center justify-center rounded-lg border border-border bg-card text-foreground transition-colors duration-150 hover:bg-muted focus-visible:outline-none xl:hidden"
                            aria-label="Menüyü aç"
                            data-testid="mobile-menu-toggle"
                        >
                            <Menu className="h-5 w-5" />
                        </button>
                    </SheetTrigger>
                    <SheetContent side="right" className="w-[88vw] max-w-sm overflow-y-auto p-0">
                        <div className="flex h-full flex-col" data-testid="mobile-menu">
                            <div className="flex items-center gap-2.5 border-b border-border px-5 py-4">
                                <BrandMark />
                                <UaeFlag className="h-5 w-8" />
                            </div>

                            <div className="flex-1 px-4 py-4">
                                <p className="px-2 text-[11px] font-bold uppercase tracking-[0.14em] text-muted-foreground">
                                    Başvuru
                                </p>
                                <div className="mt-1.5 flex flex-col gap-0.5">
                                    {PRIMARY_LINKS.map(({ to, label, icon: Icon }) => (
                                        <NavLink
                                            key={to}
                                            to={to}
                                            className={({ isActive }) =>
                                                `flex min-h-[48px] items-center gap-3 rounded-xl px-3 text-sm font-semibold ${
                                                    isActive
                                                        ? "bg-primary/10 text-primary"
                                                        : "text-foreground hover:bg-muted"
                                                }`
                                            }
                                        >
                                            <Icon className="h-4 w-4 text-primary" aria-hidden="true" />
                                            {label}
                                        </NavLink>
                                    ))}
                                    <NavLink
                                        to="/hesabim"
                                        className={({ isActive }) =>
                                            `flex min-h-[48px] items-center gap-3 rounded-xl px-3 text-sm font-semibold ${
                                                isActive
                                                    ? "bg-primary/10 text-primary"
                                                    : "text-foreground hover:bg-muted"
                                            }`
                                        }
                                    >
                                        <UserRound className="h-4 w-4 text-primary" aria-hidden="true" />
                                        Başvurularım
                                    </NavLink>
                                </div>

                                {MENU_GROUPS.map((group) => (
                                    <div key={group.label} className="mt-5">
                                        <p className="px-2 text-[11px] font-bold uppercase tracking-[0.14em] text-muted-foreground">
                                            {group.label}
                                        </p>
                                        <div className="mt-1.5 flex flex-col gap-0.5">
                                            {group.items.map(({ to, label, icon: Icon }) => (
                                                <NavLink
                                                    key={to}
                                                    to={to}
                                                    className={({ isActive }) =>
                                                        `flex min-h-[48px] items-center gap-3 rounded-xl px-3 text-sm font-medium ${
                                                            isActive
                                                                ? "bg-primary/10 text-primary"
                                                                : "text-foreground hover:bg-muted"
                                                        }`
                                                    }
                                                >
                                                    <Icon
                                                        className="h-4 w-4 text-muted-foreground"
                                                        aria-hidden="true"
                                                    />
                                                    {label}
                                                </NavLink>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="sticky bottom-0 space-y-2.5 border-t border-border bg-card px-5 py-4">
                                <Button asChild className="h-12 w-full" data-testid="mobile-apply-button">
                                    <Link to="/basvuru">Başvuru Yap</Link>
                                </Button>
                                {contact.phone && (
                                <a
                                    href={contact.phoneHref}
                                    className="flex min-h-[44px] items-center justify-center gap-2 rounded-xl border border-border text-sm font-semibold text-foreground"
                                    data-testid="mobile-phone-link"
                                >
                                    <Phone className="h-4 w-4 text-[hsl(var(--brand-copper))]" aria-hidden="true" />
                                    {contact.phone}
                                </a>
                                )}
                            </div>
                        </div>
                    </SheetContent>
                </Sheet>
            </div>
        </header>
    );
};
