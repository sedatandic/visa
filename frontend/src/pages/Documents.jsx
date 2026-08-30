import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, ArrowRight, Camera, CheckCircle2, FileText } from "lucide-react";
import { api } from "../lib/api";
import { IMAGES, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { Button } from "../components/ui/button";

export default function Documents() {
    const [content, setContent] = useState(null);

    useEffect(() => {
        setMeta(
            "Dubai Vizesi Gerekli Belgeler | VizeAtlas Dubai",
            "Dubai (BAE) vize başvurusu için gereken belgeler: pasaport fotoğrafı, vesikalık fotoğraf kriterleri, dönüş uçak bileti ve otel rezervasyonu."
        );
        api.get("/content/site").then(({ data }) => setContent(data)).catch(() => {});
    }, []);

    return (
        <div data-testid="documents-page">
            <PageHeader
                eyebrow="Gerekli Evraklar"
                title="Başvuru için gereken belgeler"
                description="Dubai vizesi tamamen elektronik düzenlenir. Pasaportunuzu kargoya vermenize gerek yoktur; aşağıdaki belgelerin dijital kopyaları yeterlidir."
            />

            <section className="section">
                <div className="container-page grid gap-12 lg:grid-cols-[1.15fr_0.85fr]">
                    <div>
                        <ul className="space-y-4" data-testid="required-documents-checklist">
                            {(content?.required_documents || []).map((d) => (
                                <li key={d.key} className="card-surface flex items-start gap-4 p-5">
                                    <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                        {d.required ? <CheckCircle2 className="h-5 w-5 text-primary" /> : <FileText className="h-5 w-5 text-primary" />}
                                    </span>
                                    <div>
                                        <div className="flex flex-wrap items-center gap-2">
                                            <h2 className="font-heading text-base font-semibold">{d.title}</h2>
                                            <span
                                                className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${
                                                    d.required
                                                        ? "border-[hsl(var(--brand-red)/0.30)] bg-[hsl(var(--brand-red)/0.08)] text-[hsl(var(--brand-red))]"
                                                        : "border-border bg-muted text-muted-foreground"
                                                }`}
                                            >
                                                {d.required ? "Zorunlu" : "Opsiyonel"}
                                            </span>
                                        </div>
                                        <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{d.detail}</p>
                                    </div>
                                </li>
                            ))}
                        </ul>

                        <div className="mt-8 rounded-xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.09)] p-6">
                            <div className="flex items-center gap-2.5">
                                <AlertTriangle className="h-5 w-5 text-[hsl(var(--status-warning))]" />
                                <h2 className="font-heading text-base font-bold text-[hsl(var(--status-warning))]">
                                    En sık yaşanan ret sebebi: uygun olmayan fotoğraf
                                </h2>
                            </div>
                            <ul className="mt-4 space-y-2.5">
                                {(content?.photo_rules || []).map((r) => (
                                    <li key={r} className="flex items-start gap-2 text-sm leading-6 text-[hsl(var(--status-warning))]">
                                        <Camera className="mt-1 h-3.5 w-3.5 shrink-0" />
                                        {r}
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <Button asChild className="mt-8 h-12 px-7 text-base" data-testid="documents-apply-button">
                            <Link to="/basvuru">
                                Belgeleri yükleyerek başla <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                    </div>

                    <div className="space-y-6">
                        <div className="overflow-hidden rounded-2xl border border-border" style={{ boxShadow: "var(--shadow-card)" }}>
                            <img src={IMAGES.travelFlatlay} alt="Seyahat hazırlığı: harita, defter ve fotoğraf makinesi" className="h-[240px] w-full object-cover" loading="lazy" />
                        </div>
                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Pasaport taraması nasıl olmalı?</h2>
                            <ul className="mt-3 space-y-2.5 text-sm leading-6 text-muted-foreground">
                                <li>• Fotoğrafın bulunduğu sayfanın tamamı görünmeli.</li>
                                <li>• Köşeler kesilmemiş, yazılar okunabilir olmalı.</li>
                                <li>• Parlama ve gölge olmaması için doğal ışıkta çekin.</li>
                                <li>• Pasaport dönüş tarihinden itibaren en az 6 ay geçerli olmalı.</li>
                                <li>• Dosya formatı: JPG, PNG veya PDF (maks. 10 MB).</li>
                            </ul>
                        </div>
                        <div className="rounded-xl border border-border bg-[hsl(var(--cloud))] p-6">
                            <h2 className="font-heading text-base font-bold">Aile başvurusu yapıyorsanız</h2>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Her yolcu için ayrı pasaport ve vesikalık fotoğraf yüklemeniz gerekir. Uçak
                                bileti ve otel rezervasyonu ise tüm başvuru için bir kez yüklenir.
                            </p>
                            <Button asChild variant="secondary" className="mt-4 h-11 border border-border">
                                <Link to="/iletisim">Danışmana sor</Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
