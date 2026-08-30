import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Award, Globe2, Users } from "lucide-react";
import { IMAGES, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { Button } from "../components/ui/button";

const STATS = [
    { icon: Users, value: "4.500+", label: "Tamamlanan başvuru" },
    { icon: Award, value: "%98", label: "Onay oranı" },
    { icon: Globe2, value: "7 yıl", label: "Sektör deneyimi" },
];

export default function About() {
    useEffect(() => {
        setMeta(
            "Hakkımızda | VizeAtlas Dubai",
            "VizeAtlas Dubai; Birleşik Arap Emirlikleri vize başvurularında uzmanlaşmış bağımsız bir danışmanlık hizmetidir."
        );
    }, []);

    return (
        <div data-testid="about-page">
            <PageHeader
                eyebrow="Hakkımızda"
                title="Vize sürecini insanlar için basitleştiriyoruz"
                description="VizeAtlas Dubai, Birleşik Arap Emirlikleri vize başvurularında uzmanlaşmış bağımsız bir danışmanlık hizmetidir. Resmî bir devlet kurumu değiliz; başvurunuzu sizin adınıza hazırlar, kontrol eder ve yetkili mercilere iletiriz."
            />

            <section className="section">
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
                            {STATS.map(({ icon: Icon, value, label }) => (
                                <div key={label} className="card-surface p-5">
                                    <Icon className="h-5 w-5 text-primary" />
                                    <p className="mt-3 font-heading text-2xl font-bold">{value}</p>
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
        </div>
    );
}
