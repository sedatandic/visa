import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Mail, MapPin, Phone, Clock, Instagram, Star } from "lucide-react";
import { api } from "../lib/api";
import { COMPANY } from "../lib/site";
import { TrFlag, UaeFlag } from "./FlagIcons";
import { TursabBadge } from "./TursabBadge";
import { GdrfaBadge } from "./GdrfaBadge";
import { BrandMark } from "./BrandMark";
import { BoldText } from "./BoldText";
import { useContact } from "../lib/contact";

export const Footer = () => {
    const contact = useContact();
    const [agency, setAgency] = useState(null);
    const [agencyItems, setAgencyItems] = useState([]);
    const [affiliation, setAffiliation] = useState("");
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
                setAffiliation(data.affiliation || "");
            })
            .catch(() => {});
    }, []);

    return (
    <footer className="mt-auto bg-[hsl(33_52%_34%)] text-white" data-testid="site-footer">
        <div className="flag-strip" aria-hidden="true" />
        <div className="container-page grid gap-10 py-14 md:grid-cols-4">
            <div className="md:col-span-2">
                <div className="flex items-center gap-2.5">
                    <BrandMark light />
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
                    <li><Link to="/seyahat-sigortasi" className="transition-colors hover:text-primary" data-testid="footer-insurance-link">Dubai Seyahat Sigortası</Link></li>
                    <li><Link to="/gelismeler" className="transition-colors hover:text-primary">Dubai'den Haberler</Link></li>
                    <li><Link to="/sss" className="transition-colors hover:text-primary">Sıkça Sorulan Sorular</Link></li>
                    <li><Link to="/takip" className="transition-colors hover:text-primary">Başvuru Takip</Link></li>
                    <li><Link to="/hakkimizda" className="transition-colors hover:text-primary">Hakkımızda</Link></li>
                    <li><Link to="/kvkk" className="transition-colors hover:text-primary">KVKK Aydınlatma Metni</Link></li>
                    <li><Link to="/gizlilik-politikasi" className="transition-colors hover:text-primary" data-testid="footer-privacy-link">Gizlilik Politikası</Link></li>
                    <li><Link to="/iade-kosullari" className="transition-colors hover:text-primary" data-testid="footer-refund-link">İade ve İptal Koşulları</Link></li>
                    <li><Link to="/hizmet-sozlesmesi" className="transition-colors hover:text-primary" data-testid="footer-service-terms-link">Şartlar ve Hizmet Sözleşmesi</Link></li>
                    <li><Link to="/ticari-ileti-onami" className="transition-colors hover:text-primary" data-testid="footer-marketing-consent-link">Ticari Elektronik İleti Onamı</Link></li>
                </ul>
            </div>

            <div>
                <h3 className="font-heading text-sm font-semibold uppercase tracking-wider text-white/50">
                    İletişim
                </h3>
                <ul className="mt-4 space-y-3 text-sm text-white/80">
                    {contact.phone && (
                        <li className="flex items-start gap-2.5">
                            <Phone className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                            <a href={contact.phoneHref} className="transition-colors hover:text-primary">{contact.phone}</a>
                        </li>
                    )}
                    <li className="flex items-start gap-2.5">
                        <Mail className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                        <a href={`mailto:${contact.email}`} className="transition-colors hover:text-primary">{contact.email}</a>
                    </li>
                    {contact.address && (
                        <li className="flex items-start gap-2.5">
                            <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                            <span>{contact.address}</span>
                        </li>
                    )}
                    {contact.dubaiAddress && (
                        <li className="flex items-start gap-2.5" data-testid="footer-dubai-office">
                            <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                            <span>
                                {contact.dubaiAddress}
                                {contact.dubaiPhone && ` · ${contact.dubaiPhone}`}
                            </span>
                        </li>
                    )}
                    <li className="flex items-start gap-2.5">
                        <Clock className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                        <span>{contact.workingHours}</span>
                    </li>
                </ul>

                <div className="mt-5 flex items-center gap-2.5" data-testid="footer-social-links">
                    {contact.instagram && (
                        <a
                            href={contact.instagram}
                            target="_blank"
                            rel="noreferrer"
                            aria-label="Instagram sayfamız"
                            data-testid="footer-instagram-link"
                            className="flex h-10 w-10 items-center justify-center rounded-full border border-white/15 bg-white/10 text-white transition-colors duration-150 hover:bg-white/20"
                        >
                            <Instagram className="h-5 w-5" />
                        </a>
                    )}
                    {contact.googleReview && (
                        <a
                            href={contact.googleReview}
                            target="_blank"
                            rel="noreferrer"
                            aria-label="Google yorumlarımız"
                            data-testid="footer-google-review-link"
                            className="flex h-10 items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3.5 text-sm font-semibold text-white transition-colors duration-150 hover:bg-white/20"
                        >
                            <Star className="h-4 w-4 fill-[hsl(var(--gold))] text-[hsl(var(--gold))]" />
                            Google Yorumları
                        </a>
                    )}
                </div>
            </div>
        </div>

        {guides.length > 0 && (
            <div className="border-t border-white/10" data-testid="footer-visa-guides">
                <div className="container-page py-7">
                    <h3 className="font-heading text-sm font-semibold uppercase tracking-wider text-white/50">
                        Vize Rehberi
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

        {affiliation && (
            <div className="border-t border-white/10" data-testid="footer-affiliation">
                <div className="container-page py-5 text-xs leading-6 text-white/60">
                    <BoldText text={affiliation} strongClassName="font-bold text-white" />
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
