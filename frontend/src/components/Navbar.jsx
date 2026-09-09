import React, { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import {
    ArrowRight,
    BookOpen,
    ChevronDown,
    ConciergeBell,
    FileCheck2,
    HelpCircle,
    Info,
    Mail,
    Menu,
    Newspaper,
    Palmtree,
    Phone,
    Search,
    ShieldCheck,
    Smartphone,
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
import { Sheet, SheetContent, SheetDescription, SheetTitle, SheetTrigger } from "./ui/sheet";
import { COMPANY } from "../lib/site";
import { api } from "../lib/api";
import { BrandMark } from "./BrandMark";
import { CartButton } from "./CartButton";
import { TrFlag, UaeFlag } from "./FlagIcons";
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
            { to: "/hizmetler", label: "Hizmetler", icon: ConciergeBell },
            { to: "/sss", label: "Sıkça Sorulan Sorular", icon: HelpCircle },
        ],
    },
    {
        label: "Ekstra Hizmetler",
        items: [
            { to: "/esim", label: "Dubai eSIM", icon: Smartphone },
            { to: "/seyahat-sigortasi", label: "Dubai Seyahat Sigortası", icon: ShieldCheck },
            { to: "/dubai-turlari", label: "Dubai Çöl Safarisi", icon: Palmtree },
        ],
    },
    {
        label: "Kurumsal",
        items: [
            { to: "/gelismeler", label: "Dubai'den Haberler", icon: Newspaper },
            { to: "/hakkimizda", label: "Hakkımızda", icon: Info },
            { to: "/iletisim", label: "İletişim", icon: Mail },
        ],
    },
];

const MENU_LINKS = MENU_GROUPS.flatMap((g) => g.items);
const GUIDE_GROUP_LABEL = "Vize Rehberi";
const testId = (to) => `nav-link-${to.replace(/^\//, "").replaceAll("/", "-")}`;

const navLinkClass = ({ isActive }) =>
    `whitespace-nowrap rounded-lg px-2 py-2 text-lg font-semibold transition-colors duration-150 focus-visible:outline-none ${
        isActive
            ? "bg-primary/10 text-primary"
            : "text-foreground/75 hover:bg-muted hover:text-foreground"
    }`;

export const Navbar = () => {
    const contact = useContact();
    const [open, setOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const [guides, setGuides] = useState([]);
    const location = useLocation();

    useEffect(() => setOpen(false), [location.pathname]);

    useEffect(() => {
        api.get("/visa-guides")
            .then(({ data }) => setGuides(data.items || []))
            .catch(() => {});
    }, []);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 8);
        onScroll();
        window.addEventListener("scroll", onScroll);
        return () => window.removeEventListener("scroll", onScroll);
    }, []);

    const guideItems = guides.map((g) => ({ to: g.path, label: g.title, icon: BookOpen }));
    const groups = guideItems.length
        ? [MENU_GROUPS[0], { label: GUIDE_GROUP_LABEL, items: guideItems }, ...MENU_GROUPS.slice(1)]
        : MENU_GROUPS;
    const menuActive =
        MENU_LINKS.some((l) => location.pathname.startsWith(l.to)) ||
        location.pathname.startsWith("/dubai-vizesi");

    // Logo/bayrak alanina tiklandiginda ana sayfaya gider ve sayfa basina kaydirir
    // (zaten ana sayfadaysa route degismedigi icin kaydirmayi burada yapiyoruz).
    const goHomeTop = () => window.scrollTo({ top: 0, behavior: "smooth" });

    return (
        <header
            className={`sticky top-0 z-40 w-full border-b bg-background/85 backdrop-blur-xl transition-shadow duration-200 ${
                scrolled
                    ? "border-border shadow-[0_4px_18px_rgba(11,15,20,0.07)]"
                    : "border-transparent"
            }`}
            data-testid="site-navbar"
        >
            <div className="h-px w-full bg-border" aria-hidden="true" />
            <div className="mx-auto flex h-[84px] w-full max-w-[88rem] items-end justify-between gap-4 px-4 pb-3 sm:h-[96px] sm:px-6 sm:pb-3.5 lg:h-[108px]">
                <Link
                    to="/"
                    onClick={goHomeTop}
                    className="flex shrink-0 items-end gap-2.5 rounded-lg focus-visible:outline-none"
                    data-testid="navbar-logo-link"
                >
                    <BrandMark />
                </Link>

                <Link
                    to="/"
                    onClick={goHomeTop}
                    aria-label="Ana sayfaya dön"
                    className="hidden flex-1 items-end justify-center pb-[1px] min-[360px]:flex lg:pb-[2px]"
                    data-testid="brand-flag-pair"
                >
                    <span className="flex items-center gap-1 lg:gap-2">
                        <TrFlag className="h-4 w-8 min-[380px]:h-5 min-[380px]:w-10 sm:h-6 sm:w-12 lg:h-[46px] lg:w-[92px]" />
                        <ArrowRight className="hidden h-4 w-4 text-primary lg:block" />
                        <UaeFlag className="h-4 w-8 min-[380px]:h-5 min-[380px]:w-10 sm:h-6 sm:w-12 lg:h-[46px] lg:w-[92px]" />
                    </span>
                </Link>

                <nav className="hidden items-center gap-0.5 xl:flex" aria-label="Ana menü">
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
                                className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-lg px-2 py-2 text-lg font-semibold transition-colors duration-150 focus-visible:outline-none ${
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
                            align="center"
                            className="w-auto min-w-[12rem] rounded-xl p-1.5"
                            data-testid="navbar-more-menu"
                        >
                            {groups.map((group, gi) => (
                                <React.Fragment key={group.label}>
                                    {gi > 0 && <DropdownMenuSeparator />}
                                    <DropdownMenuLabel className="text-[11px] font-bold uppercase tracking-[0.12em] text-muted-foreground">
                                        {group.label}
                                    </DropdownMenuLabel>
                                    <div
                                        className={
                                            group.label === GUIDE_GROUP_LABEL
                                                ? "grid grid-cols-2 gap-0.5"
                                                : ""
                                        }
                                    >
                                        {group.items.map(({ to, label, icon: Icon }) => (
                                            <DropdownMenuItem key={to} asChild className="rounded-lg">
                                                <Link
                                                    to={to}
                                                    data-testid={testId(to)}
                                                    className="flex w-full cursor-pointer items-center gap-2.5 py-2 text-sm font-medium"
                                                >
                                                    <Icon className="h-4 w-4 shrink-0 text-primary" aria-hidden="true" />
                                                    {label}
                                                </Link>
                                            </DropdownMenuItem>
                                        ))}
                                    </div>
                                </React.Fragment>
                            ))}
                        </DropdownMenuContent>
                    </DropdownMenu>
                </nav>

                <div className="hidden items-end gap-2.5 md:flex">
                    {contact.phone && (
                    <a
                        href={contact.phoneHref}
                        aria-label={`Telefon: ${contact.phone}`}
                        className="hidden items-center gap-2 whitespace-nowrap rounded-lg px-2 py-2 text-lg font-semibold text-foreground/75 transition-colors duration-150 hover:text-primary 2xl:flex"
                        data-testid="navbar-phone-link"
                    >
                        <Phone className="h-4 w-4 text-[hsl(var(--brand-copper))]" aria-hidden="true" />
                        <span>{contact.phone}</span>
                    </a>
                    )}
                    <CartButton />
                    <Button asChild className="h-14 px-6 text-lg" data-testid="navbar-apply-button">
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
                        <SheetTitle className="sr-only">Menü</SheetTitle>
                        <SheetDescription className="sr-only">
                            Site menüsü: vize bilgileri, rehberler ve iletişim bağlantıları
                        </SheetDescription>
                        <div className="flex h-full flex-col" data-testid="mobile-menu">
                            <div className="flex items-center gap-2.5 border-b border-border py-4 pl-5 pr-12">
                                <BrandMark />
                                <span className="flex shrink-0 items-center gap-1">
                                    <TrFlag className="h-4 w-8" />
                                    <UaeFlag className="h-4 w-8" />
                                </span>
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
                                            data-testid={`mobile-${testId(to)}`}
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
                                    <CartButton variant="mobile" />
                                </div>

                                {groups.map((group) => (
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
                                    aria-label={`Telefon: ${contact.phone}`}
                                    className="flex min-h-[48px] items-center justify-center gap-2 rounded-xl text-sm font-bold text-white transition-opacity duration-150 hover:opacity-90"
                                    style={{ backgroundColor: "#25D366", boxShadow: "var(--shadow-float)" }}
                                    data-testid="mobile-phone-link"
                                >
                                    <Phone className="h-4 w-4" aria-hidden="true" />
                                    <span>{contact.phone}</span>
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
