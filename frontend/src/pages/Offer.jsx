import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
    ArrowRight,
    BadgeCheck,
    CalendarDays,
    Loader2,
    ShieldCheck,
    Sparkles,
    Users,
} from "lucide-react";
import { api, apiError } from "../lib/api";
import { formatDate, formatMoney, setMeta } from "../lib/site";
import { useContact, waLink } from "../lib/contact";
import { OfferCountdown } from "../components/OfferCountdown";
import { PageHeader } from "../components/SiteLayout";
import { Button } from "../components/ui/button";
import { WhatsAppIcon } from "../components/WhatsAppIcon";

const Line = ({ label, value, strong, tone }) => (
    <div className="flex items-start justify-between gap-4 border-b border-border py-3 last:border-0">
        <span className={`text-sm ${strong ? "font-bold" : "text-muted-foreground"}`}>{label}</span>
        <span
            className={`shrink-0 text-right text-sm font-bold ${
                tone === "discount" ? "text-emerald-600" : strong ? "font-heading text-base" : ""
            }`}
        >
            {value}
        </span>
    </div>
);

export default function Offer() {
    const { token } = useParams();
    const siteContact = useContact();
    const [offer, setOffer] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setMeta("Size özel Dubai vize teklifi | Dubai Vize Hattı", "Danışmanınızın hazırladığı Dubai vize teklifi.", {
            canonicalPath: `/teklif/${token}`,
            noindex: true,
        });
        api.get(`/offers/${token}`)
            .then(({ data }) => setOffer(data))
            .catch((err) => setError(apiError(err, "Teklif bulunamadı.")))
            .finally(() => setLoading(false));
    }, [token]);

    const quote = offer?.quote || {};
    const currency = offer?.currency || "TRY";
    const waHref = waLink(siteContact, "Merhaba, hazırladığınız teklif hakkında bilgi almak istiyorum.");

    return (
        <div data-testid="offer-page">
            <PageHeader
                eyebrow="Size özel teklif"
                title={offer?.title || "Dubai vize teklifiniz"}
                description={
                    offer
                        ? `${offer.customer_name ? `${offer.customer_name}, ` : ""}danışmanınızın hazırladığı teklif aşağıda. Onaylıyorsanız başvuru formunda seçimleriniz hazır gelecek.`
                        : "Danışmanınızın hazırladığı Dubai vize teklifi."
                }
            />

            <section className="pb-16 pt-6 sm:pb-20 sm:pt-8">
                <div className="container-page max-w-3xl">
                    {loading && (
                        <div className="flex justify-center py-20">
                            <Loader2 className="h-6 w-6 animate-spin text-primary" />
                        </div>
                    )}

                    {!loading && error && (
                        <div className="card-surface p-6 sm:p-8" data-testid="offer-error">
                            <h2 className="font-heading text-lg font-bold">Teklif görüntülenemedi</h2>
                            <p className="mt-3 text-sm leading-6 text-muted-foreground">{error}</p>
                            <div className="mt-6 flex flex-wrap gap-3">
                                {waHref && (
                                    <Button asChild className="h-12" data-testid="offer-error-whatsapp">
                                        <a href={waHref} target="_blank" rel="noreferrer">
                                            <WhatsAppIcon className="mr-2 h-5 w-5" /> WhatsApp'tan yeni teklif isteyin
                                        </a>
                                    </Button>
                                )}
                                <Button asChild variant="secondary" className="h-12 border border-border">
                                    <Link to="/vize-tipleri">Vize fiyatlarını gör</Link>
                                </Button>
                            </div>
                        </div>
                    )}

                    {!loading && offer && (
                        <div className="space-y-5">
                            <div className="card-surface p-6 sm:p-8">
                                <div className="flex flex-wrap items-center gap-3">
                                    <span className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">
                                        <Sparkles className="h-3.5 w-3.5" /> Danışman teklifi
                                    </span>
                                    {offer.expires_at && (
                                        <>
                                            <OfferCountdown expiresAt={offer.expires_at} />
                                            <span
                                                className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1.5 text-xs font-semibold text-muted-foreground"
                                                data-testid="offer-validity"
                                            >
                                                <CalendarDays className="h-3.5 w-3.5" />
                                                {formatDate(offer.expires_at)} tarihine kadar geçerli
                                            </span>
                                        </>
                                    )}
                                </div>

                                <div className="mt-6 rounded-2xl border border-border bg-[hsl(var(--cloud))] p-5">
                                    <p className="text-xs font-bold uppercase tracking-wide text-muted-foreground">
                                        Teklif tutarı
                                    </p>
                                    <p className="font-heading text-3xl font-extrabold sm:text-4xl" data-testid="offer-total">
                                        {formatMoney(offer.total, currency)}
                                    </p>
                                    <p className="mt-1.5 flex items-center gap-2 text-xs text-muted-foreground">
                                        <Users className="h-3.5 w-3.5" />
                                        {offer.travelers?.length || 0} yolcu · tüm hizmet bedelleri dahil
                                    </p>
                                </div>

                                <div className="mt-6">
                                    <h2 className="font-heading text-base font-bold">Yolcular ve vize tipleri</h2>
                                    <div className="mt-2">
                                        {(offer.travelers || []).map((t, i) => (
                                            <Line
                                                key={`${t.visa_type_id}-${i}`}
                                                label={`${i + 1}. Yolcu · ${t.applicant_type === "child" ? "Çocuk" : "Yetişkin"} — ${t.visa_short_name || t.visa_name}`}
                                                value={formatMoney(t.price, currency)}
                                            />
                                        ))}
                                    </div>
                                </div>

                                <div className="mt-6">
                                    <h2 className="font-heading text-base font-bold">Fiyat dökümü</h2>
                                    <div className="mt-2">
                                        <Line label="Vize bedelleri" value={formatMoney(quote.subtotal, currency)} />
                                        {quote.family_discount > 0 && (
                                            <Line
                                                label={`Aile indirimi (%${Math.round((quote.family_discount_rate || 0) * 100)})`}
                                                value={`- ${formatMoney(quote.family_discount, currency)}`}
                                                tone="discount"
                                            />
                                        )}
                                        {(quote.addons || []).map((a) => (
                                            <Line
                                                key={a.id || a.name}
                                                label={`${a.name}${a.quantity > 1 ? ` × ${a.quantity}` : ""}`}
                                                value={formatMoney(a.total, currency)}
                                            />
                                        ))}
                                        {(offer.store_items || []).map((line) => (
                                            <Line
                                                key={line.product_id}
                                                label={`${line.name}${line.quantity > 1 ? ` × ${line.quantity}` : ""}${
                                                    line.scheduled_date ? ` · ${formatDate(line.scheduled_date)}${line.scheduled_time ? ` ${line.scheduled_time}` : ""}` : ""
                                                }`}
                                                value={formatMoney(line.total, currency)}
                                            />
                                        ))}
                                        {quote.bundle_discount > 0 && (
                                            <Line
                                                label={quote.bundle_discount_title || "Paket indirimi"}
                                                value={`- ${formatMoney(quote.bundle_discount, currency)}`}
                                                tone="discount"
                                            />
                                        )}
                                        {quote.visa_insurance_discount > 0 && (
                                            <Line
                                                label={quote.visa_insurance_discount_title || "Sigorta indirimi"}
                                                value={`- ${formatMoney(quote.visa_insurance_discount, currency)}`}
                                                tone="discount"
                                            />
                                        )}
                                        <Line label="Genel toplam" value={formatMoney(offer.total, currency)} strong />
                                    </div>
                                </div>

                                {offer.note && (
                                    <p
                                        className="mt-6 rounded-2xl border border-border bg-card p-4 text-sm leading-6 text-muted-foreground"
                                        data-testid="offer-note"
                                    >
                                        {offer.note}
                                    </p>
                                )}

                                <div className="mt-7 flex flex-col gap-3 sm:flex-row">
                                    <Button asChild className="h-14 flex-1 text-base" data-testid="offer-apply-button">
                                        <Link to={`/basvuru?teklif=${offer.token}`}>
                                            Başvuruyu tamamla <ArrowRight className="ml-2 h-5 w-5" />
                                        </Link>
                                    </Button>
                                    {waHref && (
                                        <Button asChild variant="secondary" className="h-14 border border-border" data-testid="offer-whatsapp-button">
                                            <a href={waHref} target="_blank" rel="noreferrer">
                                                <WhatsAppIcon className="mr-2 h-5 w-5" /> Soru sor
                                            </a>
                                        </Button>
                                    )}
                                </div>

                                <p className="mt-4 text-xs leading-6 text-muted-foreground">
                                    Başvuru için yalnızca pasaportunuzun kimlik sayfası ve vesikalık fotoğrafınız
                                    yeterlidir. Uçak bileti veya otel rezervasyonu şartı yoktur.
                                </p>
                            </div>

                            <div className="grid gap-3 sm:grid-cols-2">
                                <div className="card-surface flex items-center gap-3 p-4">
                                    <ShieldCheck className="h-5 w-5 shrink-0 text-primary" />
                                    <p className="text-sm font-semibold">TÜRSAB üyesi A Grubu seyahat acentesi güvencesi</p>
                                </div>
                                <div className="card-surface flex items-center gap-3 p-4">
                                    <BadgeCheck className="h-5 w-5 shrink-0 text-primary" />
                                    <p className="text-sm font-semibold">Fiyatlar teklif geçerlilik süresi boyunca sabittir</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
}
