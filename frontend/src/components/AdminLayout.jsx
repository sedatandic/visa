import React, { useEffect, useState } from "react";
import { Link, NavLink, Navigate, useLocation, useNavigate } from "react-router-dom";
import {
    BookOpen,
    Building2,
    FileText,
    Landmark,
    Globe2,
    LayoutDashboard,
    LogOut,
    Mail,
    MessageCircle,
    MessageSquare,
    Package,
    PanelLeft,
    Send,
    ShieldCheck,
    Star,
    Tag,
} from "lucide-react";
import { Button } from "./ui/button";
import { Sheet, SheetContent, SheetTrigger } from "./ui/sheet";
import { BrandMark } from "./BrandMark";
import { api } from "../lib/api";

const NAV_GROUPS = [
    {
        label: "Operasyon",
        items: [
            { to: "/admin", label: "Başvurular", icon: LayoutDashboard, end: true },
            { to: "/admin/siparisler", label: "eSIM & Sigorta", icon: Package },
            { to: "/admin/sigorta", label: "Sigorta Poliçeleri", icon: ShieldCheck },
            { to: "/admin/zami", label: "Zami Aktarımı", icon: Send },
        ],
    },
    {
        label: "Müşteri İletişimi",
        items: [
            { to: "/admin/mesajlar", label: "Mesajlar", icon: MessageSquare, badge: "messages" },
            { to: "/admin/e-postalar", label: "E-postalar", icon: Mail },
            { to: "/admin/whatsapp", label: "WhatsApp", icon: MessageCircle, badge: "whatsapp" },
        ],
    },
    {
        label: "İçerik",
        items: [
            { to: "/admin/vize-tipleri", label: "Vize Tipleri", icon: Tag },
            { to: "/admin/vize-rehberleri", label: "Vize Rehberleri", icon: BookOpen },
            { to: "/admin/yazilar", label: "Blog Yazıları", icon: FileText },
            { to: "/admin/yorumlar", label: "Yorumlar", icon: Star },
        ],
    },
    {
        label: "Ayarlar",
        items: [
            { to: "/admin/ziyaretciler", label: "Ziyaretçiler", icon: Globe2 },
            { to: "/admin/banka", label: "Banka Bilgileri", icon: Landmark },
            { to: "/admin/acente", label: "Acente Bilgileri", icon: Building2 },
        ],
    },
];

const navTestId = (to) => `admin-nav-${to.split("/").pop()}`;

const itemClass = ({ isActive }) =>
    `flex min-h-[44px] items-center gap-2.5 rounded-xl px-3 text-sm font-semibold transition-colors duration-150 focus-visible:outline-none ${
        isActive
            ? "bg-primary/10 text-primary"
            : "text-muted-foreground hover:bg-muted hover:text-foreground"
    }`;

export const RequireAdmin = ({ children }) => {
    const token = localStorage.getItem("dv_admin_token");
    if (!token) return <Navigate to="/admin/giris" replace />;
    // Suresi dolmus jetonu temizle: kisa sureli "girisli" ekran gorunmesin
    try {
        const { exp } = JSON.parse(atob(token.split(".")[1]));
        if (exp && exp * 1000 < Date.now()) {
            localStorage.removeItem("dv_admin_token");
            return <Navigate to="/admin/giris" replace />;
        }
    } catch {
        localStorage.removeItem("dv_admin_token");
        return <Navigate to="/admin/giris" replace />;
    }
    return children;
};

const NavList = ({ badges = {} }) => (
    <nav className="space-y-5" aria-label="Yönetim menüsü">
        {NAV_GROUPS.map((group) => (
            <div key={group.label}>
                <p className="px-3 text-[11px] font-bold uppercase tracking-[0.14em] text-muted-foreground/80">
                    {group.label}
                </p>
                <div className="mt-1.5 space-y-0.5">
                    {group.items.map(({ to, label, icon: Icon, end, badge }) => {
                        const count = badge ? badges[badge] || 0 : 0;
                        return (
                            <NavLink key={to} to={to} end={end} data-testid={navTestId(to)} className={itemClass}>
                                <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
                                <span className="flex-1 truncate">{label}</span>
                                {count > 0 && (
                                    <span
                                        className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-primary px-1.5 text-[11px] font-bold text-primary-foreground"
                                        data-testid={`admin-nav-badge-${badge}`}
                                        title={`${count} bekleyen`}
                                    >
                                        {count > 99 ? "99+" : count}
                                    </span>
                                )}
                            </NavLink>
                        );
                    })}
                </div>
            </div>
        ))}
    </nav>
);

export const AdminLayout = ({ children, title, description, actions = null }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [menuOpen, setMenuOpen] = useState(false);
    const [badges, setBadges] = useState({});
    const email = localStorage.getItem("dv_admin_email") || "";

    useEffect(() => setMenuOpen(false), [location.pathname]);

    // Bekleyen mesaj / WhatsApp belgesi sayaci: her sayfada ve 60 sn'de bir tazelenir.
    useEffect(() => {
        let alive = true;
        const load = () =>
            api
                .get("/admin/stats")
                .then(({ data }) => {
                    if (!alive) return;
                    setBadges({
                        messages: data.unread_messages || 0,
                        whatsapp: (data.wa_pending_documents || 0) + (data.wa_needs_human || 0),
                    });
                })
                .catch(() => {});
        load();
        const timer = setInterval(load, 60000);
        return () => {
            alive = false;
            clearInterval(timer);
        };
    }, []);

    const logout = () => {
        localStorage.removeItem("dv_admin_token");
        localStorage.removeItem("dv_admin_email");
        navigate("/admin/giris");
    };

    return (
        <div className="min-h-screen bg-[hsl(var(--cloud))]" data-testid="admin-layout">
            <div className="flex">
                <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-border bg-card lg:flex">
                    <div className="flex h-[68px] items-center border-b border-border px-5">
                        <Link to="/admin" className="flex items-center gap-2.5">
                            <BrandMark />
                        </Link>
                    </div>
                    <div className="flex-1 overflow-y-auto px-3 py-5">
                        <NavList badges={badges} />
                    </div>
                    <div className="border-t border-border p-3">
                        <p className="truncate px-3 pb-2 text-xs text-muted-foreground" title={email}>
                            {email}
                        </p>
                        <Button
                            variant="secondary"
                            className="h-10 w-full border border-border"
                            onClick={logout}
                            data-testid="admin-logout-button"
                        >
                            <LogOut className="mr-2 h-4 w-4" /> Çıkış
                        </Button>
                    </div>
                </aside>

                <div className="min-w-0 flex-1">
                    <header className="sticky top-0 z-30 border-b border-border bg-card/95 backdrop-blur-xl">
                        <div className="flex h-[68px] items-center gap-3 px-4 sm:px-6">
                            <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
                                <SheetTrigger asChild>
                                    <button
                                        type="button"
                                        className="flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-card transition-colors duration-150 hover:bg-muted focus-visible:outline-none lg:hidden"
                                        aria-label="Yönetim menüsünü aç"
                                        data-testid="admin-menu-toggle"
                                    >
                                        <PanelLeft className="h-5 w-5" />
                                    </button>
                                </SheetTrigger>
                                <SheetContent side="left" className="w-[86vw] max-w-xs overflow-y-auto p-0">
                                    <div className="flex h-[68px] items-center border-b border-border px-5">
                                        <BrandMark />
                                    </div>
                                    <div className="px-3 py-5">
                                        <NavList badges={badges} />
                                    </div>
                                    <div className="border-t border-border p-3">
                                        <Button
                                            variant="secondary"
                                            className="h-10 w-full border border-border"
                                            onClick={logout}
                                            data-testid="admin-mobile-logout-button"
                                        >
                                            <LogOut className="mr-2 h-4 w-4" /> Çıkış
                                        </Button>
                                    </div>
                                </SheetContent>
                            </Sheet>

                            <div className="min-w-0 flex-1">
                                {title && (
                                    <h1 className="truncate text-base font-bold sm:text-lg" data-testid="admin-page-title">
                                        {title}
                                    </h1>
                                )}
                            </div>

                            <div className="flex shrink-0 items-center gap-2">
                                {actions}
                                <Button asChild variant="ghost" className="hidden h-10 sm:inline-flex">
                                    <Link to="/" target="_blank" rel="noreferrer" data-testid="admin-view-site-link">
                                        Siteyi gör
                                    </Link>
                                </Button>
                            </div>
                        </div>
                    </header>

                    <main className="px-4 py-7 sm:px-6 lg:px-8">
                        {description && (
                            <p className="mb-6 max-w-3xl text-sm leading-6 text-muted-foreground">{description}</p>
                        )}
                        {children}
                    </main>
                </div>
            </div>
        </div>
    );
};
