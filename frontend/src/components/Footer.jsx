import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Mail, MapPin, Phone, Clock } from "lucide-react";
import { api } from "../lib/api";
import { COMPANY } from "../lib/site";
import { TrFlag, UaeFlag } from "./FlagIcons";
import { TursabBadge } from "./TursabBadge";
import { GdrfaBadge } from "./GdrfaBadge";

export const Footer = () => {
    const [agency, setAgency] = useState(null);
    const [agencyItems, setAgencyItems] = useState([]);
    const [guides, setGuides] = useState([]);

    useEffect(() => {
        api.get("/visa-guides")
            .then(({ data }) => setGuides(data.items || []))
            .catch(() => {});
    }, []);

    useEffect(() => {
        api.get("/content/site")
            .then(({ data }) => {
                setAgency(data.company || null);
                setAgencyItems(data.agency_info?.items || []);
            })
            .catch(() => {});
    }, []);

    return (
    <footer className="mt-auto bg-[hsl(var(--navy))] text-white" data-testid="site-footer">
        <div className="flag-strip" aria-hidden="true" />
        <div className="container-page grid gap-10 py-14 md:grid-cols-4">
            <div className="md:col-span-2">
                <div className="flex items-center gap-2.5">
                    <span className="relative flex h-9 w-9 items-center justify-center overflow-hidden rounded-md bg-primary">
                        <span className="absolute left-0 top-0 h-full w-1.5 bg-[hsl(var(--brand-red))]" />
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round">
                            <path d="M4 21V11a8 8 0 0 1 16 0v10" />
                            <path d="M8.5 13.5 11 16l4.5-5" />
                        </svg>
                    </span>
                    <span className="font-heading text-lg font-bold">
                        {COMPANY.brand}
                        <span className="text-primary">.</span>{" "}
                        <span className="text-white/60 text-sm font-semibold uppercase tracking-widest">
                            {COMPANY.brandSuffix}
                        </span>
                    </span>
                </div>
                <p className="mt-4 max-w-md text-sm leading-6 text-white/70">
                    Dubai ve Birleşik Arap Emirlikleri vize başvurularınızı baştan sona takip eden
                    TÜRSAB üyesi seyahat acentesiyiz. Resmî bir devlet kurumu değiliz; başvurunuzu
                    sizin adınıza hazırlar ve yetkili mercilere iletiriz.
                </p>
                <div className="mt-5 flex flex-wrap items-center gap-3">
                    <TursabBadge number={agency?.tursab_no} type={agency?.tursab_type} light />
                    <GdrfaBadge light />
                </div>
                <div className="mt-5 flex items-center gap-3">
                    <TrFlag className="h-5 w-8" />
                    <span className="text-xs font-semibold text-white/60">Türkiye → Birleşik Arap Emirlikleri</span>
                    <UaeFlag className="h-5 w-8" />
                </div>
            </div>

            <div>
                <h3 className="font-heading text-sm font-semibold uppercase tracking-wider text-white/50">
                    Hızlı Bağlantılar
                </h3>
                <ul className="mt-4 space-y-2.5 text-sm text-white/80">
                    <li><Link to="/vize-tipleri" className="transition-colors hover:text-primary">Hizmet Bedelleri</Link></li>
                    <li><Link to="/gerekli-belgeler" className="transition-colors hover:text-primary">Gerekli Belgeler</Link></li>
                    <li><Link to="/hizmetler" className="transition-colors hover:text-primary">Hizmetlerimiz</Link></li>
                    <li><Link to="/esim" className="transition-colors hover:text-primary" data-testid="footer-esim-link">Dubai eSIM</Link></li>
                    <li><Link to="/seyahat-sigortasi" className="transition-colors hover:text-primary" data-testid="footer-insurance-link">Seyahat Sigortası</Link></li>
                    <li><Link to="/gelismeler" className="transition-colors hover:text-primary">Dubai'den Gelişmeler</Link></li>
                    <li><Link to="/sss" className="transition-colors hover:text-primary">Sıkça Sorulan Sorular</Link></li>
                    <li><Link to="/takip" className="transition-colors hover:text-primary">Başvuru Takip</Link></li>
                    <li><Link to="/hakkimizda" className="transition-colors hover:text-primary">Hakkımızda</Link></li>
                    <li><Link to="/kvkk" className="transition-colors hover:text-primary">KVKK & Gizlilik</Link></li>
                    <li><Link to="/iade-kosullari" className="transition-colors hover:text-primary" data-testid="footer-refund-link">İade ve İptal Koşulları</Link></li>
                    <li><Link to="/hizmet-sozlesmesi" className="transition-colors hover:text-primary" data-testid="footer-service-terms-link">Mesafeli Hizmet Sözleşmesi</Link></li>
                </ul>
            </div>

            <div>
                <h3 className="font-heading text-sm font-semibold uppercase tracking-wider text-white/50">
                    İletişim
                </h3>
                <ul className="mt-4 space-y-3 text-sm text-white/80">
                    <li className="flex items-start gap-2.5">
                        <Phone className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                        <a href={COMPANY.phoneHref} className="transition-colors hover:text-primary">{COMPANY.phone}</a>
                    </li>
                    <li className="flex items-start gap-2.5">
                        <Mail className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                        <a href={`mailto:${COMPANY.email}`} className="transition-colors hover:text-primary">{COMPANY.email}</a>
                    </li>
                    <li className="flex items-start gap-2.5">
                        <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                        <span>{COMPANY.address}</span>
                    </li>
                    <li className="flex items-start gap-2.5">
                        <Clock className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                        <span>{COMPANY.workingHours}</span>
                    </li>
                </ul>
            </div>
        </div>

        {guides.length > 0 && (
            <div className="border-t border-white/10" data-testid="footer-visa-guides">
                <div className="container-page py-7">
                    <h3 className="font-heading text-sm font-semibold uppercase tracking-wider text-white/50">
                        Vize Rehberleri
                    </h3>
                    <ul className="mt-4 grid gap-x-8 gap-y-2.5 text-sm text-white/80 sm:grid-cols-2 lg:grid-cols-3">
                        {guides.map((g) => (
                            <li key={g.slug}>
                                <Link
                                    to={g.path}
                                    className="transition-colors hover:text-primary"
                                    data-testid={`footer-guide-link-${g.slug}`}
                                >
                                    {g.title}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        )}

        {agencyItems.length > 0 && (            <div className="border-t border-white/10" data-testid="footer-agency-info">
                <div className="container-page py-7">
                    <h3 className="font-heading text-sm font-semibold uppercase tracking-wider text-white/50">
                        Acente Bilgileri
                    </h3>
                    <dl className="mt-4 grid gap-x-8 gap-y-3 sm:grid-cols-2 lg:grid-cols-4">
                        {agencyItems.map((item) => (
                            <div key={item.label} className="text-xs leading-5">
                                <dt className="text-white/45">{item.label}</dt>
                                <dd className="font-semibold text-white/85">{item.value}</dd>
                            </div>
                        ))}
                    </dl>
                </div>
            </div>
        )}

        <div className="border-t border-white/10">
            <div className="container-page flex flex-col gap-2 py-5 text-xs text-white/50 sm:flex-row sm:items-center sm:justify-between">
                <span>© {new Date().getFullYear()} {COMPANY.brand} {COMPANY.brandSuffix}. Tüm hakları saklıdır.</span>
                <Link to="/admin/giris" className="transition-colors hover:text-white/80" data-testid="footer-admin-link">
                    Yönetici Girişi
                </Link>
            </div>
        </div>
    </footer>
    );
};
