import React, { useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Gauge, MessageCircle, ShieldCheck } from "lucide-react";
import { setMeta, COMPANY } from "../lib/site";
import { Button } from "../components/ui/button";
import { PreEvaluation } from "../components/PreEvaluation";

export default function PreEvaluationPage() {
    useEffect(() => {
        setMeta(
            "Ücretsiz Dubai Vize Ön Değerlendirmesi | VizeAtlas Dubai",
            "3 kısa soruyla Dubai (BAE) vizesi onay olasılığınızı ücretsiz öğrenin. Size uygun vize tipi ve onay şansınızı artıracak adımlar anında."
        );
    }, []);

    return (
        <div data-testid="pre-evaluation-page">
            <section className="border-b border-border bg-card">
                <div className="container-page py-12 sm:py-16">
                    <span className="eyebrow">
                        <Gauge className="h-3.5 w-3.5" /> Ücretsiz Ön Değerlendirme
                    </span>
                    <h1 className="mt-4 max-w-3xl text-3xl font-bold leading-tight sm:text-4xl">
                        Dubai vizeniz onaylanır mı? Başvurmadan önce öğrenin
                    </h1>
                    <p className="mt-4 max-w-2xl text-sm leading-7 text-muted-foreground sm:text-base">
                        Pasaport geçerliliğiniz, vize geçmişiniz ve red kaydınıza göre tahmini onay
                        olasılığınızı hesaplıyoruz. Sonuç bilgilendirme amaçlıdır; kayıt veya ödeme
                        gerektirmez.
                    </p>
                </div>
            </section>

            <section className="section">
                <div className="container-page grid items-start gap-10 lg:grid-cols-[1.05fr_0.95fr]">
                    <PreEvaluation />

                    <div className="grid gap-5">
                        <div className="rounded-2xl border border-border bg-card p-5">
                            <p className="flex items-center gap-2 text-sm font-bold">
                                <ShieldCheck className="h-4 w-4 text-primary" /> Değerlendirme nasıl çalışır?
                            </p>
                            <ul className="mt-3 space-y-2.5 text-xs leading-6 text-muted-foreground">
                                <li>
                                    <strong className="text-foreground">Pasaport geçerliliği:</strong> BAE, giriş
                                    tarihinde en az 6 ay geçerli pasaport ister; bu en belirleyici kriterdir.
                                </li>
                                <li>
                                    <strong className="text-foreground">Vize geçmişi:</strong> ABD, İngiltere,
                                    Schengen veya BAE vize kaydı olumlu bir referans oluşturur.
                                </li>
                                <li>
                                    <strong className="text-foreground">Red kaydı:</strong> Önceki redler dosyanın
                                    daha dikkatli hazırlanmasını gerektirir; bu durumda danışmanımız devreye girer.
                                </li>
                            </ul>
                        </div>

                        <div className="rounded-2xl border border-border bg-[hsl(var(--cloud))] p-5">
                            <p className="text-sm font-bold">Sonucunuz düşük mü çıktı?</p>
                            <p className="mt-2 text-xs leading-6 text-muted-foreground">
                                Panik yapmayın. Reddi olan dosyalarda doğru belge seti ve açıklama ile onay
                                alınabiliyor. Danışmanımız dosyanızı ücretsiz inceleyip yol haritası çıkarır.
                            </p>
                            <div className="mt-4 flex flex-wrap gap-2.5">
                                <Button asChild size="sm" data-testid="pre-eval-page-apply-button">
                                    <Link to="/basvuru">
                                        Başvuruya Başla <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                                    </Link>
                                </Button>
                                <Button asChild size="sm" variant="secondary" data-testid="pre-eval-page-whatsapp-button">
                                    <a
                                        href={`https://wa.me/${(COMPANY?.whatsapp || "").replace(/\D/g, "")}`}
                                        target="_blank"
                                        rel="noreferrer"
                                    >
                                        <MessageCircle className="mr-1.5 h-3.5 w-3.5" /> WhatsApp'tan sor
                                    </a>
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
