import React, { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { Menu, Phone, X } from "lucide-react";
import { Button } from "./ui/button";
import { COMPANY } from "../lib/site";
import { BrandMark } from "./BrandMark";

const LINKS = [
    { to: "/vize-tipleri", label: "Vize Tipleri & Fiyatlar" },
    { to: "/gerekli-belgeler", label: "Gerekli Belgeler" },
    { to: "/sss", label: "S.S.S." },
    { to: "/takip", label: "Başvuru Takip" },
    { to: "/iletisim", label: "İletişim" },
];

export const Navbar = () => {
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

    return (
        <header
            className={`sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur transition-shadow duration-200 ${
                scrolled ? "border-border shadow-[0_4px_18px_rgba(11,31,51,0.06)]" : "border-transparent"
            }`}
            data-testid="site-navbar"
        >
            <div className="container-page flex h-[72px] items-center justify-between gap-4">
                <Link to="/" className="flex items-center gap-2.5" data-testid="navbar-logo-link">
                    <BrandMark />
                </Link>

                <nav className="hidden items-center gap-1 lg:flex">
                    {LINKS.map((l) => (
                        <NavLink
                            key={l.to}
                            to={l.to}
                            data-testid={`nav-link-${l.to.replace("/", "")}`}
                            className={({ isActive }) =>
                                `rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-150 ${
                                    isActive
                                        ? "bg-primary/10 text-primary"
                                        : "text-foreground/80 hover:bg-muted hover:text-foreground"
                                }`
                            }
                        >
                            {l.label}
                        </NavLink>
                    ))}
                </nav>

                <div className="hidden items-center gap-3 lg:flex">
                    <a
                        href={COMPANY.phoneHref}
                        className="flex items-center gap-2 text-sm font-semibold text-foreground/80 transition-colors hover:text-primary"
                        data-testid="navbar-phone-link"
                    >
                        <Phone className="h-4 w-4" />
                        {COMPANY.phone}
                    </a>
                    <Button asChild className="h-11 px-5" data-testid="navbar-apply-button">
                        <Link to="/basvuru">Başvuru Yap</Link>
                    </Button>
                </div>

                <button
                    type="button"
                    onClick={() => setOpen((v) => !v)}
                    className="flex h-11 w-11 items-center justify-center rounded-lg border border-border bg-card text-foreground lg:hidden"
                    aria-label="Menüyü aç/kapat"
                    data-testid="mobile-menu-toggle"
                >
                    {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </button>
            </div>

            {open && (
                <div className="border-t border-border bg-card lg:hidden" data-testid="mobile-menu">
                    <div className="container-page flex flex-col gap-1 py-4">
                        {LINKS.map((l) => (
                            <NavLink
                                key={l.to}
                                to={l.to}
                                className={({ isActive }) =>
                                    `rounded-lg px-3 py-3 text-sm font-medium ${
                                        isActive ? "bg-primary/10 text-primary" : "text-foreground"
                                    }`
                                }
                            >
                                {l.label}
                            </NavLink>
                        ))}
                        <Button asChild className="mt-2 h-12" data-testid="mobile-apply-button">
                            <Link to="/basvuru">Başvuru Yap</Link>
                        </Button>
                    </div>
                </div>
            )}
        </header>
    );
};
