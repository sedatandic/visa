import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, MessageCircle } from "lucide-react";
import { api } from "../lib/api";
import { COMPANY, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { ServiceCard } from "../components/IconCards";
import { Button } from "../components/ui/button";

export default function Services() {
    const [content, setContent] = useState(null);

    useEffect(() => {
        setMeta(
            "Vize Hizmetlerimiz | VizeAtlas Dubai",
            "Dubai vize başvurusu, aile başvurusu, evrak kontrolü, ekspres vize, vize uzatma ve başvuru takibi hizmetleri."
        );
        api.get("/content/site").then(({ data }) => setContent(data)).catch(() => {});
    }, []);

    return (
        <div data-testid="services-page">
            <PageHeader
                eyebrow="Hizmetlerimiz"
                title="Tek işimiz vize; baştan sona yanınızdayız"
                description="Başvuru hazırlığından evrak kontrolüne, ekspres işlemden vize uzatmaya kadar tüm süreç uzman danışmanlarımız tarafından yürütülür."
            />

            <section className="section">
                <div className="container-page">
                    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                        {(content?.services || []).map((s) => (
                            <ServiceCard key={s.key} item={s} />
                        ))}
                    </div>

                    <div className="mt-12 flex flex-col items-start gap-4 rounded-xl border border-border bg-[hsl(var(--cloud))] p-7 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <h2 className="font-heading text-xl font-bold">Hangi vize size uygun, birlikte belirleyelim</h2>
                            <p className="mt-1.5 text-sm text-muted-foreground">
                                Seyahat tarihiniz ve kalış sürenize göre en uygun vize tipini ücretsiz
                                değerlendirelim. WhatsApp'tan yazın, danışmanınız hemen dönüş yapsın.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-3">
                            <Button asChild variant="secondary" className="h-11 border border-border">
                                <a href={`https://wa.me/${COMPANY.whatsapp}`} target="_blank" rel="noreferrer" data-testid="services-whatsapp-button">
                                    <MessageCircle className="mr-2 h-4 w-4" /> WhatsApp
                                </a>
                            </Button>
                            <Button asChild className="h-11">
                                <Link to="/basvuru" data-testid="services-apply-button">
                                    Vize başvurusu <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
