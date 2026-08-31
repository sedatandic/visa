import React from "react";
import { Link, NavLink, Navigate, useNavigate } from "react-router-dom";
import { BookOpen, Building2, FileText, Landmark, LayoutDashboard, LogOut, Mail, MessageSquare, Star, Tag } from "lucide-react";
import { Button } from "./ui/button";
import { BrandMark } from "./BrandMark";

const NAV = [
    { to: "/admin", label: "Başvurular", icon: LayoutDashboard, end: true },
    { to: "/admin/mesajlar", label: "Mesajlar", icon: MessageSquare },
    { to: "/admin/e-postalar", label: "E-postalar", icon: Mail },
    { to: "/admin/vize-tipleri", label: "Vize Tipleri", icon: Tag },
    { to: "/admin/vize-rehberleri", label: "Vize Rehberleri", icon: BookOpen },
    { to: "/admin/yorumlar", label: "Yorumlar", icon: Star },
    { to: "/admin/yazilar", label: "Blog Yazıları", icon: FileText },
    { to: "/admin/banka", label: "Banka Bilgileri", icon: Landmark },
    { to: "/admin/acente", label: "Acente Bilgileri", icon: Building2 },
];

export const RequireAdmin = ({ children }) => {
    const token = localStorage.getItem("dv_admin_token");
    if (!token) return <Navigate to="/admin/giris" replace />;
    return children;
};

export const AdminLayout = ({ children, title, description }) => {
    const navigate = useNavigate();
    const email = localStorage.getItem("dv_admin_email") || "";

    const logout = () => {
        localStorage.removeItem("dv_admin_token");
        localStorage.removeItem("dv_admin_email");
        navigate("/admin/giris");
    };

    return (
        <div className="min-h-screen bg-background">
            <header className="border-b border-border bg-card">
                <div className="container-page flex h-[68px] items-center justify-between gap-4">
                    <Link to="/admin" className="flex items-center gap-2.5">
                        <BrandMark />
                    </Link>
                    <div className="flex items-center gap-3">
                        <span className="hidden text-sm text-muted-foreground sm:inline">{email}</span>
                        <Button variant="secondary" className="h-10 border border-border" onClick={logout} data-testid="admin-logout-button">
                            <LogOut className="mr-2 h-4 w-4" /> Çıkış
                        </Button>
                    </div>
                </div>
                <div className="container-page flex gap-1 overflow-x-auto pb-2">
                    {NAV.map(({ to, label, icon: Icon, end }) => (
                        <NavLink
                            key={to}
                            to={to}
                            end={end}
                            data-testid={`admin-nav-${to.split("/").pop()}`}
                            className={({ isActive }) =>
                                `flex items-center gap-2 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition-colors duration-150 ${
                                    isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-muted"
                                }`
                            }
                        >
                            <Icon className="h-4 w-4" />
                            {label}
                        </NavLink>
                    ))}
                </div>
            </header>

            <main className="container-page py-8">
                {title && (
                    <div className="mb-7">
                        <h1 className="text-2xl font-bold sm:text-3xl">{title}</h1>
                        {description && <p className="mt-2 text-sm text-muted-foreground">{description}</p>}
                    </div>
                )}
                {children}
            </main>
        </div>
    );
};
