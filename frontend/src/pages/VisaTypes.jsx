import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, ArrowRight, Check, X } from "lucide-react";
import { setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { PricingTabs } from "../components/PricingTabs";
import { Button } from "../components/ui/button";

const INCLUDED = [
    "Başvuru harcı ve hizmet bedeli",
    "Belge ön kontrolü ve düzeltme desteği",
    "Başvuru takibi ve bilgilendirme",
    "Onaylanan vizenin PDF olarak teslimi",
    "WhatsApp üzerinden danışman desteği",
];

const EXCLUDED = [
    "Uçak bileti ve otel rezervasyonu",
    "Seyahat sağlık sigortası (ek hizmet olarak eklenebilir)",
    "Ekspres işlem ücreti (ek hizmet olarak eklenebilir)",
    "Biyometrik fotoğraf çekimi",
    "Pasaport yenileme işlemleri",
];

export default function VisaTypes() {
    useEffect(() => {
        setMeta(
            "Dubai Vize Hizmet Bedelleri ve Fiyatları | VizeAtlas Dubai",
            "30 ve 60 günlük tek giriş, çok giriş, çocuk vizesi ve vize uzatma hizmet bedelleri; ekspres vize ve seyahat sigortası ek hizmet fiyatları."
        );
    }, []);

    return (
        <div data-testid="visa-types-page">
            <PageHeader
                eyebrow="Vize Tipleri & Hizmet Bedelleri"
                title="Size uygun Dubai vizesini seçin"
                description="Kalış süreniz, giriş sayınız ve yolcuların yaşına göre uygun vizeyi seçebilirsiniz. Tüm fiyatlar kişi başı ve tek seferliktir."
            />

            <section className="section">
                <div className="container-page">
                    <PricingTabs />

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
                        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[#7A4B00]" />
                        <p className="text-sm leading-6 text-[#7A4B00]">
                            Vize ücretleri ve işlem süreleri yetkili merciler tarafından güncellenebilir.
                            Başvurunuzu oluşturmadan önce seçtiğiniz vize tiplerinin fiyatları özet ekranında
                            tekrar gösterilir.
                        </p>
                    </div>

                    <div className="mt-10 flex flex-col items-start gap-4 rounded-xl border border-border bg-[hsl(var(--cloud))] p-7 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <h2 className="font-heading text-xl font-bold">Aileniz için tek başvuru yeterli</h2>
                            <p className="mt-1.5 text-sm text-muted-foreground">
                                Eşinizi ve çocuklarınızı aynı forma ekleyin; indirimler otomatik hesaplanır.
                            </p>
                        </div>
                        <Button asChild className="h-11" data-testid="visa-types-apply-button">
                            <Link to="/basvuru">
                                Başvuruya başla <ArrowRight className="ml-2 h-4 w-4" />
                            </Link>
                        </Button>
                    </div>
                </div>
            </section>
        </div>
    );
}
