import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, CalendarDays } from "lucide-react";
import { api } from "../lib/api";
import { formatDate, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { Button } from "../components/ui/button";

const FALLBACK_COVER =
    "https://images.unsplash.com/photo-1459787915554-b34915863013?crop=entropy&cs=srgb&fm=jpg&q=85&w=1200";

const ArticleCard = ({ article }) => (
    <article
        className="card-surface group flex flex-col overflow-hidden transition-shadow duration-200 hover:shadow-[0_18px_40px_rgba(11,15,20,0.12)]"
        data-testid={`article-${article.slug}`}
    >
        <Link to={`/gelismeler/${article.slug}`} className="block overflow-hidden">
            <img
                src={article.cover_image || FALLBACK_COVER}
                alt={article.title}
                loading="lazy"
                decoding="async"
                className="h-52 w-full object-cover transition-transform duration-500 group-hover:scale-[1.04]"
                data-testid={`article-cover-${article.slug}`}
            />
        </Link>
        <div className="flex flex-1 flex-col p-5">
            <span className="inline-flex w-fit items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-bold text-primary">
                <CalendarDays className="h-3.5 w-3.5" /> {formatDate(article.date)}
            </span>
            <h2 className="mt-3.5 font-heading text-lg font-bold leading-snug">
                <Link to={`/gelismeler/${article.slug}`} className="transition-colors duration-150 hover:text-primary">
                    {article.title}
                </Link>
            </h2>
            <p className="mt-2.5 line-clamp-3 text-sm leading-6 text-muted-foreground">{article.excerpt}</p>
            <Link
                to={`/gelismeler/${article.slug}`}
                className="mt-4 inline-flex items-center gap-2 text-sm font-bold text-primary transition-colors duration-150 hover:text-[hsl(var(--brand-copper))]"
                data-testid={`article-read-more-${article.slug}`}
            >
                Devamını oku
                <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
            </Link>
        </div>
    </article>
);

export default function Articles() {
    const [articles, setArticles] = useState([]);

    useEffect(() => {
        setMeta(
            "Dubai'den Haberler | Vize ve Seyahat Rehberi | Dubai Vize Online",
            "Dubai vize kuralları, pasaport süresi, vize uzatma, seyahat sigortası ve ret sebepleri hakkında güncel rehber yazıları."
        );
        api.get("/articles")
            .then(({ data }) => setArticles(Array.isArray(data) ? data : data.items || []))
            .catch(() => {});
    }, []);

    return (
        <div data-testid="articles-page">
            <PageHeader
                eyebrow="Dubai'den Haberler"
                title="Vize ve seyahat rehberi"
                description="Dubai'den haberler, aktiviteler, restoranlar, oteller ve tüm güncel duyuruları ilk siz öğrenin."
            />

            <section className="pb-14 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page">
                    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3" data-testid="articles-grid">
                        {articles.map((a) => (
                            <ArticleCard key={a.slug} article={a} />
                        ))}
                    </div>

                    <div className="mt-10 flex flex-col items-start gap-4 rounded-2xl border border-border bg-[hsl(var(--cloud))] p-7 sm:flex-row sm:items-center sm:justify-between">
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
