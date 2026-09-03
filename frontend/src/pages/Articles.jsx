import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, CalendarDays } from "lucide-react";
import { api } from "../lib/api";
import { formatDate, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { Button } from "../components/ui/button";

export default function Articles() {
    const [content, setContent] = useState(null);

    useEffect(() => {
        setMeta(
            "Dubai'den Gelişmeler | Vize ve Seyahat Rehberi | Dubai Vize Online",
            "Dubai vize kuralları, pasaport süresi, vize uzatma, seyahat sigortası ve ret sebepleri hakkında güncel rehber yazıları."
        );
        api.get("/content/site").then(({ data }) => setContent(data)).catch(() => {});
    }, []);

    return (
        <div data-testid="articles-page">
            <PageHeader
                eyebrow="Dubai'den Gelişmeler"
                title="Vize ve seyahat rehberi"
                description="Başvuru öncesi bilmeniz gerekenleri, güncel kuralları ve sık yapılan hataları danışman ekibimiz derledi."
            />

            <section className="section">
                <div className="container-page max-w-3xl space-y-8">
                    {(content?.articles || []).map((a) => (
                        <article key={a.slug} className="card-surface p-6 sm:p-8" data-testid={`article-${a.slug}`}>
                            <p className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-[hsl(var(--brand-copper))]">
                                <CalendarDays className="h-3.5 w-3.5" /> {formatDate(a.date)}
                            </p>
                            <h2 className="mt-3 font-heading text-xl font-bold sm:text-2xl">
                                <Link to={`/gelismeler/${a.slug}`} className="transition-colors hover:text-primary">
                                    {a.title}
                                </Link>
                            </h2>
                            <p className="mt-3 text-sm font-medium leading-6">{a.excerpt}</p>
                            <p className="mt-4 line-clamp-3 text-sm leading-7 text-muted-foreground">
                                {(a.body || [])[0]}
                            </p>
                            <Button asChild variant="secondary" className="mt-5 h-10 border border-border" data-testid={`article-read-more-${a.slug}`}>
                                <Link to={`/gelismeler/${a.slug}`}>
                                    Yazının devamını oku <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                        </article>
                    ))}

                    <div className="flex flex-col items-start gap-4 rounded-xl border border-border bg-[hsl(var(--cloud))] p-7 sm:flex-row sm:items-center sm:justify-between">
                        <p className="text-sm font-semibold">Sorunuz mu var? Danışman ekibimiz yanınızda.</p>
                        <div className="flex gap-3">
                            <Button asChild variant="secondary" className="h-11 border border-border">
                                <Link to="/iletisim">İletişim</Link>
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
