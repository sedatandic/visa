import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ArrowRight, CalendarDays, Loader2 } from "lucide-react";
import { api } from "../lib/api";
import { COMPANY, formatDate, setJsonLd, setMeta } from "../lib/site";
import { Button } from "../components/ui/button";
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from "../components/ui/breadcrumb";

export default function ArticleDetail() {
    const { slug } = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [notFound, setNotFound] = useState(false);

    useEffect(() => {
        let cancelled = false;
        setLoading(true);
        setNotFound(false);
        api.get(`/articles/${slug}`)
            .then(({ data: res }) => {
                if (cancelled) return;
                setData(res);
                const a = res.article || {};
                setMeta(`${a.title} | VizeAtlas Dubai`, a.excerpt || "", {
                    canonicalPath: `/gelismeler/${a.slug}`,
                    ogType: "article",
                });
                setJsonLd("article", {
                    "@context": "https://schema.org",
                    "@type": "Article",
                    headline: a.title,
                    description: a.excerpt,
                    datePublished: a.date,
                    dateModified: a.updated_at || a.date,
                    inLanguage: "tr-TR",
                    author: { "@type": "Organization", name: `${COMPANY.brand} ${COMPANY.brandSuffix}` },
                    publisher: {
                        "@type": "Organization",
                        name: `${COMPANY.brand} ${COMPANY.brandSuffix}`,
                    },
                    mainEntityOfPage: `${window.location.origin}/gelismeler/${a.slug}`,
                });
            })
            .catch(() => {
                if (!cancelled) setNotFound(true);
            })
            .finally(() => !cancelled && setLoading(false));
        return () => {
            cancelled = true;
            setJsonLd("article", null);
        };
    }, [slug]);

    if (loading) {
        return (
            <div className="container-page flex min-h-[50vh] items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
        );
    }

    if (notFound || !data?.article) {
        return (
            <div className="container-page section text-left" data-testid="article-not-found">
                <h1 className="text-2xl font-bold">Yazı bulunamadı</h1>
                <p className="mt-3 text-sm text-muted-foreground">
                    Aradığınız yazı kaldırılmış veya adresi değişmiş olabilir.
                </p>
                <Button asChild className="mt-6 h-11">
                    <Link to="/gelismeler">Tüm yazılar</Link>
                </Button>
            </div>
        );
    }

    const a = data.article;
    const related = data.related || [];

    return (
        <div data-testid="article-detail-page">
            <section className="border-b border-border bg-card">
                <div className="container-page max-w-3xl py-10 sm:py-14">
                    <Breadcrumb>
                        <BreadcrumbList>
                            <BreadcrumbItem>
                                <BreadcrumbLink asChild>
                                    <Link to="/" data-testid="breadcrumb-home">Ana sayfa</Link>
                                </BreadcrumbLink>
                            </BreadcrumbItem>
                            <BreadcrumbSeparator />
                            <BreadcrumbItem>
                                <BreadcrumbLink asChild>
                                    <Link to="/gelismeler" data-testid="breadcrumb-articles">Dubai'den Gelişmeler</Link>
                                </BreadcrumbLink>
                            </BreadcrumbItem>
                            <BreadcrumbSeparator />
                            <BreadcrumbItem>
                                <BreadcrumbPage className="line-clamp-1">{a.title}</BreadcrumbPage>
                            </BreadcrumbItem>
                        </BreadcrumbList>
                    </Breadcrumb>

                    <p className="mt-6 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-[hsl(var(--brand-red))]">
                        <CalendarDays className="h-3.5 w-3.5" /> {formatDate(a.date)}
                    </p>
                    <h1 className="mt-3 text-3xl font-extrabold leading-tight sm:text-4xl" data-testid="article-title">
                        {a.title}
                    </h1>
                    <p className="mt-4 text-base leading-7 text-muted-foreground">{a.excerpt}</p>
                </div>
            </section>

            <section className="section">
                <div className="container-page max-w-3xl">
                    <div className="space-y-5 text-[15px] leading-8" data-testid="article-body">
                        {(a.body || []).map((p, i) => (
                            <p key={i}>{p}</p>
                        ))}
                    </div>

                    <div className="mt-10 flex flex-col items-start gap-4 rounded-2xl border border-border bg-[hsl(var(--cloud))] p-7 sm:flex-row sm:items-center sm:justify-between">
                        <p className="text-sm font-semibold">
                            Başvurunuzu bugün başlatın; belgelerinizi danışmanlarımız kontrol etsin.
                        </p>
                        <Button asChild className="h-11" data-testid="article-apply-button">
                            <Link to="/basvuru">
                                Başvuru Yap <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                    </div>

                    {related.length > 0 && (
                        <div className="mt-12">
                            <h2 className="text-xl font-bold">Benzer yazılar</h2>
                            <div className="mt-5 grid gap-5 sm:grid-cols-2">
                                {related.map((r) => (
                                    <Link
                                        key={r.slug}
                                        to={`/gelismeler/${r.slug}`}
                                        className="card-surface card-hoverable p-5"
                                        data-testid={`related-article-${r.slug}`}
                                    >
                                        <p className="text-xs font-semibold uppercase tracking-wider text-[hsl(var(--brand-red))]">
                                            {formatDate(r.date)}
                                        </p>
                                        <h3 className="mt-2 font-heading text-base font-bold">{r.title}</h3>
                                        <p className="mt-2 line-clamp-3 text-sm leading-6 text-muted-foreground">
                                            {r.excerpt}
                                        </p>
                                    </Link>
                                ))}
                            </div>
                        </div>
                    )}

                    <Button asChild variant="secondary" className="mt-10 h-11 border border-border">
                        <Link to="/gelismeler">
                            <ArrowLeft className="mr-2 h-4 w-4" /> Tüm yazılar
                        </Link>
                    </Button>
                </div>
            </section>
        </div>
    );
}
