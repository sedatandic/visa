import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { api } from "../lib/api";
import { setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { ImportantNotice } from "../components/ImportantNotice";
import { ContentByline } from "../components/ContentByline";
import { useContact } from "../lib/contact";
import { Button } from "../components/ui/button";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "../components/ui/accordion";

export default function Faq() {
    const contact = useContact();
    const [content, setContent] = useState(null);

    useEffect(() => {
        setMeta(
            "Dubai Vizesi Sıkça Sorulan Sorular | Dubai Vize Hattı",
            "Dubai vizesi hakkında sıkça sorulan sorular: işlem süresi, pasaport geçerliliği, ödeme güvenliği, ret durumunda iade ve başvuru takibi."
        );
        api.get("/content/site").then(({ data }) => setContent(data)).catch(() => {});
    }, []);

    return (
        <div data-testid="faq-page">
            <PageHeader
                eyebrow="Sıkça sorulan sorular"
                title="Sıkça sorulan sorular"
                description="Başvuru öncesi aklınıza gelebilecek soruları tek sayfada topladik. Aradiginizi bulamazsanız bize yazın."
            />
            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page">
                    <Accordion type="single" collapsible className="w-full" data-testid="faq-accordion">
                        {(content?.faq || []).map((item, i) => (
                            <AccordionItem key={i} value={`faq-${i}`}>
                                <AccordionTrigger className="text-left text-sm font-semibold sm:text-base">
                                    {item.q}
                                </AccordionTrigger>
                                <AccordionContent className="text-sm leading-7 text-muted-foreground">
                                    {item.a}
                                </AccordionContent>
                            </AccordionItem>
                        ))}
                    </Accordion>

                    <div className="mt-12">
                        <ImportantNotice compact />
                    </div>
                    <ContentByline className="mt-6" />

                    <div className="mt-12 flex flex-col items-start gap-4 rounded-xl border border-border bg-[hsl(var(--cloud))] p-7 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <h2 className="font-heading text-lg font-bold">Sorunuzun cevabını bulamadınız mı?</h2>
                            <p className="mt-1.5 text-sm text-muted-foreground">
                                Danışman ekibimiz {contact.workingHours} saatleri arasında yanınızda.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-3">
                            <Button asChild variant="secondary" className="h-11 border border-border">
                                <Link to="/iletisim">İletişime geç</Link>
                            </Button>
                            <Button asChild className="h-11">
                                <Link to="/basvuru">
                                    Başvuru Yap <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
