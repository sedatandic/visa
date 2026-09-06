import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Award, Globe2, Users } from "lucide-react";
import { api } from "../lib/api";
import { IMAGES, setMeta } from "../lib/site";
import { TursabBadge } from "../components/TursabBadge";
import { PageHeader } from "../components/SiteLayout";
import { BoldText } from "../components/BoldText";
import { Button } from "../components/ui/button";

const STATS_META = [
    { icon: Users, key: "applications", label: "Tamamlanan başvuru" },
    { icon: Award, key: "recommend", label: "Tavsiye oranı" },
    { icon: Globe2, key: "experience", label: "Sektör deneyimi" },
];

export default function About() {
    const [agency, setAgency] = useState(null);
    const [company, setCompany] = useState(null);
    const [summary, setSummary] = useState(null);
    const [affiliation, setAffiliation] = useState("");

    useEffect(() => {
        api.get("/content/site")
            .then(({ data }) => {
                setAgency(data.agency_info || null);
                setCompany(data.company || null);
                setSummary(data.review_summary || null);
                setAffiliation(data.affiliation || "");
            })
            .catch(() => {});
    }, []);

    useEffect(() => {
        setMeta(
            "Hakkımızda | Dubai Vize Hattı",
            "Dubai Vize Hattı; Birleşik Arap Emirlikleri vize başvurularında uzmanlaşmış bağımsız bir danışmanlık hizmetidir."
        );
    }, []);

    return (
        <div data-testid="about-page">
            <PageHeader
                eyebrow="Hakkımızda"
                title="Dubai vizesi işini biz üstleniyoruz"
                description="Dubai Vize Hattı, Birleşik Arap Emirlikleri vize başvurularına odaklanmış bağımsız bir danışmanlık hizmetidir. Resmî bir devlet kurumu değiliz; başvurunuzu sizin adınıza hazırlar, evraklarınızı tek tek kontrol eder ve yetkili mercilere iletiriz."
            />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page grid items-start gap-12 lg:grid-cols-2">
                    <div>
                        <h2 className="text-2xl font-bold">Neden kurduk?</h2>
                        <div className="mt-4 space-y-4 text-sm leading-7 text-muted-foreground">
                            <p>
                                Vize başvurularında insanları en çok yoran şey belirsizlik: hangi belge
                                gerekiyor, fotoğraf uygun mu, başvuru nerede bekliyor? Bu soruların
                                cevaplarını tek bir ekranda topladık.
                            </p>
                            <p>
                                Her başvuru bir danışmana atanır. Belgeleriniz gönderilmeden önce
                                pasaport geçerliliği, fotoğraf kriterleri ve seyahat tarihleri kontrol
                                edilir. Bir sorun varsa başvuruyu göndermeden sizi bilgilendiririz.
                            </p>
                            <p>
                                Fiyatlarımız baştan nettir. Ödeme sonrası ek ücret talep etmeyiz;
                                başvurunuz olumsuz sonuçlanırsa hizmet bedelimizi iade ederiz.
                            </p>
                        </div>

                        <div className="mt-8 grid gap-4 sm:grid-cols-3">
                            {STATS_META.map(({ icon: Icon, key, label }) => (
                                <div key={key} className="card-surface p-5" data-testid={`about-stat-${key}`}>
                                    <Icon className="h-5 w-5 text-primary" />
                                    <p className="mt-3 font-heading text-2xl font-bold">
                                        {key === "applications"
                                            ? `${Number(summary?.total_applications || 0).toLocaleString("tr-TR")}+`
                                            : key === "recommend"
                                              ? `%${summary?.recommend_rate ?? 0}`
                                              : "7 yıl"}
                                    </p>
                                    <p className="text-xs text-muted-foreground">{label}</p>
                                </div>
                            ))}
                        </div>

                        <Button asChild className="mt-8 h-12 px-7 text-base">
                            <Link to="/basvuru">
                                Başvuru Yap <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                    </div>

                    <div className="space-y-6">
                        <div className="overflow-hidden rounded-2xl border border-border" style={{ boxShadow: "var(--shadow-card)" }}>
                            <img
                                src={IMAGES.dubaiNight}
                                alt="Dubai Şeyh Zayed Yolu gece görünümü"
                                className="h-[280px] w-full object-cover"
                                loading="lazy"
                            />
                        </div>
                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Çalışma ilkelerimiz</h2>
                            <ul className="mt-3 space-y-2.5 text-sm leading-6 text-muted-foreground">
                                <li>• Gerçekçi olmayan söz vermeyiz; onay kararı yetkili mercilere aittir.</li>
                                <li>• Belgelerinizi üçüncü taraflarla paylaşmayız.</li>
                                <li>• Fiyat değişikliklerini başvuru öncesi bildiririz.</li>
                                <li>• Her başvuru için takip kodu ve durum güncellemesi sağlarız.</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </section>

            <section className="section border-t border-border bg-[hsl(var(--cloud))]" data-testid="about-agency-info">
                <div className="container-page grid gap-10 lg:grid-cols-[0.85fr_1.15fr]">
                    <div>
                        <span className="eyebrow">Acente Bilgilerimiz</span>
                        <h2 className="mt-3 text-2xl font-bold">TÜRSAB üyesi seyahat acentesiyiz</h2>
                        <p className="mt-3 text-sm leading-7 text-muted-foreground">
                            {agency?.description ||
                                "Tüm başvurularınız acente güvencesiyle yürütülür; ticari bilgilerimiz aşağıda açıkça yer alır."}
                        </p>
                        {affiliation && (
                            <p className="mt-3 text-sm leading-7 text-muted-foreground" data-testid="about-affiliation-note">
                                <BoldText text={affiliation} />
                            </p>
                        )}
                        <div className="mt-5">
                            <TursabBadge number={company?.tursab_no} type={company?.tursab_type} />
                        </div>
                    </div>

                    <dl className="grid gap-x-8 gap-y-4 sm:grid-cols-2">
                        {(agency?.items || []).map((item) => (
                            <div key={item.label} className="border-b border-border pb-3">
                                <dt className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                                    {item.label}
                                </dt>
                                <dd className="mt-1 text-sm font-semibold" data-testid={`agency-item-${item.label}`}>
                                    {item.value}
                                </dd>
                            </div>
                        ))}
                    </dl>
                </div>
            </section>
        </div>
    );
}
