import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Check, Info, X } from "lucide-react";
import { api } from "../lib/api";
import { setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { VisaTypeCard } from "../components/VisaTypeCard";
import { Button } from "../components/ui/button";

const INCLUDED = [
    "Başvuru harcı ve hizmet bedeli",
    "Belge ön kontrolü ve düzeltme desteği",
    "Başvuru takibi ve bilgilendirme",
    "Dijital vizenin e-posta ile teslimi",
    "WhatsApp üzerinden danışman desteği",
];

const EXCLUDED = [
    "Uçak bileti ve otel rezervasyonu",
    "Seyahat sağlık sigortası",
    "Biyometrik fotoğraf çekimi",
    "Pasaport yenileme işlemleri",
];

export default function VisaTypes() {
    const [visaTypes, setVisaTypes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setMeta(
            "Dubai Vize Tipleri ve Fiyatları | VizeAtlas Dubai",
            "14, 30 ve 60 günlük tek giriş ve çok giriş Dubai vize tiplerinin güncel fiyatları, kapsamı ve sonuçlanma süreleri."
        );
        api
            .get("/visa-types")
            .then(({ data }) => setVisaTypes(data))
            .catch(() => {})
            .finally(() => setLoading(false));
    }, []);

    return (
        <div data-testid="visa-types-page">
            <PageHeader
                eyebrow="Vize Tipleri & Fiyatlar"
                title="Size uygun Dubai vizesini seçin"
                description="Kalış süreniz ve seyahat sıklığınıza göre aşağıdaki vize tiplerinden birini seçebilirsiniz. Tüm fiyatlar kişi başı ve tek seferliktir."
            />

            <section className="section">
                <div className="container-page">
                    {loading ? (
                        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                            {[0, 1, 2].map((i) => (
                                <div key={i} className="h-[420px] animate-pulse rounded-xl border border-border bg-card" />
                            ))}
                        </div>
                    ) : (
                        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3" data-testid="visa-types-pricing-grid">
                            {visaTypes.map((visa) => (
                                <VisaTypeCard key={visa.id} visa={visa} />
                            ))}
                        </div>
                    )}

                    <div className="mt-14 grid gap-6 md:grid-cols-2">
                        <div className="card-surface p-6">
                            <h2 className="font-heading text-lg font-bold">Fiyata dahil olanlar</h2>
                            <ul className="mt-4 space-y-3">
                                {INCLUDED.map((i) => (
                                    <li key={i} className="flex items-start gap-2.5 text-sm">
                                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--success))]" />
                                        {i}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="card-surface p-6">
                            <h2 className="font-heading text-lg font-bold">Fiyata dahil olmayanlar</h2>
                            <ul className="mt-4 space-y-3">
                                {EXCLUDED.map((i) => (
                                    <li key={i} className="flex items-start gap-2.5 text-sm text-muted-foreground">
                                        <X className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
                                        {i}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    <div className="mt-8 flex items-start gap-3 rounded-xl border border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.1)] p-5">
                        <Info className="mt-0.5 h-5 w-5 shrink-0 text-[#7A4B00]" />
                        <p className="text-sm leading-6 text-[#7A4B00]">
                            Vize ücretleri ve işlem süreleri yetkili merciler tarafından güncellenebilir.
                            Başvurunuzu oluşturmadan önce seçtiğiniz vize tipinin fiyatı özet ekranında
                            tekrar gösterilir.
                        </p>
                    </div>

                    <div className="mt-10 flex flex-col items-start gap-4 rounded-xl border border-border bg-[hsl(var(--cloud))] p-7 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <h2 className="font-heading text-xl font-bold">Hangi vizeyi seçeceğinizden emin değil misiniz?</h2>
                            <p className="mt-1.5 text-sm text-muted-foreground">
                                Seyahat tarihlerinizi yazın, size uygun vizeyi ücretsiz önerelim.
                            </p>
                        </div>
                        <div className="flex flex-wrap gap-3">
                            <Button asChild variant="secondary" className="h-11 border border-border">
                                <Link to="/iletisim">Bize sorun</Link>
                            </Button>
                            <Button asChild className="h-11" data-testid="visa-types-apply-button">
                                <Link to="/basvuru">
                                    Başvuruya başla <ArrowRight className="ml-2 h-4 w-4" />
                                </Link>
                            </Button>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
