import React, { useCallback, useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import {
    CheckCircle2,
    Clock,
    Download,
    Landmark,
    Loader2,
    Copy,
    PackageCheck,
    Search,
} from "lucide-react";
import { toast } from "sonner";
import { api, apiError, API } from "../lib/api";
import { formatDate, formatDateTime, formatMoney, setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

const STATUS_TEXT = {
    pending: { label: "Ödeme bekleniyor", tone: "warning", icon: Clock },
    processing: { label: "Hazırlanıyor", tone: "info", icon: Loader2 },
    fulfilled: { label: "Teslim edildi", tone: "success", icon: PackageCheck },
    cancelled: { label: "İptal edildi", tone: "error", icon: Clock },
};

const PAYMENT_TEXT = {
    pending: "Ödeme bekleniyor",
    awaiting_transfer: "Havale bekleniyor",
    paid: "Ödeme alındı",
    refunded: "İade edildi",
};

export default function OrderStatus() {
    const { reference } = useParams();
    const [searchParams] = useSearchParams();
    const [email, setEmail] = useState(localStorage.getItem("dv_last_order_email") || "");
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        setMeta(`Sipariş ${reference} | Dubai Vize Online`, "eSIM ve seyahat sigortası sipariş durumunuz.", {
            canonicalPath: `/siparis/${reference}`,
            noindex: true,
        });
    }, [reference]);

    const load = useCallback(
        async (mail) => {
            if (!mail) return;
            setLoading(true);
            setError("");
            try {
                const { data: res } = await api.get(`/orders/${reference}`, { params: { email: mail } });
                setData(res);
                localStorage.setItem("dv_last_order_email", mail);
            } catch (err) {
                setError(apiError(err, "Sipariş bulunamadı."));
                setData(null);
            } finally {
                setLoading(false);
            }
        },
        [reference]
    );

    useEffect(() => {
        const saved = localStorage.getItem("dv_last_order_email");
        if (saved) load(saved);
    }, [load]);

    useEffect(() => {
        if (searchParams.get("session_id")) {
            toast.success("Ödemeniz alındı. Belgeleriniz hazırlandığında e-postanıza gönderilecek.");
        }
        if (searchParams.get("iptal")) {
            toast.info("Ödeme tamamlanmadı. Havale ile de ödeyebilirsiniz.");
        }
    }, [searchParams]);

    const order = data?.order;
    const bank = data?.bank;
    const status = STATUS_TEXT[order?.status] || STATUS_TEXT.pending;
    const StatusIcon = status.icon;

    const copy = (value, label) => {
        navigator.clipboard?.writeText(value);
        toast.success(`${label} kopyalandı.`);
    };

    return (
        <div data-testid="order-status-page">
            <PageHeader
                eyebrow="Sipariş Takibi"
                title={`Sipariş ${reference}`}
                description="eSIM ve seyahat sigortası siparişinizin durumunu buradan görebilirsiniz."
            />

            <section className="section">
                <div className="container-page max-w-3xl">
                    {!order && (
                        <div className="card-surface p-6" data-testid="order-email-form">
                            <div className="space-y-2">
                                <Label htmlFor="order-email">Siparişteki e-posta adresiniz</Label>
                                <Input
                                    id="order-email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    data-testid="order-email-input"
                                />
                            </div>
                            {error && (
                                <p className="mt-3 text-sm font-medium text-destructive" data-testid="order-error">
                                    {error}
                                </p>
                            )}
                            <Button
                                onClick={() => load(email.trim())}
                                disabled={loading || !email.trim()}
                                className="mt-5 h-11"
                                data-testid="order-lookup-button"
                            >
                                {loading ? (
                                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sorgulanıyor…</>
                                ) : (
                                    <><Search className="mr-2 h-4 w-4" /> Siparişi görüntüle</>
                                )}
                            </Button>
                        </div>
                    )}

                    {order && (
                        <div className="space-y-6" data-testid="order-detail">
                            <div className="card-surface p-6">
                                <div className="flex flex-wrap items-center justify-between gap-3">
                                    <div className="flex items-center gap-2.5">
                                        <StatusIcon className="h-5 w-5 text-primary" />
                                        <span
                                            className="font-heading text-lg font-bold"
                                            data-testid="order-status-label"
                                        >
                                            {status.label}
                                        </span>
                                    </div>
                                    <span className="text-sm text-muted-foreground" data-testid="order-payment-label">
                                        {PAYMENT_TEXT[order.payment?.status] || "Ödeme bekleniyor"}
                                    </span>
                                </div>
                                <p className="mt-3 text-sm text-muted-foreground">
                                    Oluşturulma: {formatDateTime(order.created_at)}
                                </p>

                                <ul className="mt-5 space-y-2.5 border-t border-border pt-5">
                                    {(order.items || []).map((i) => (
                                        <li
                                            key={i.product_id}
                                            className="flex items-start justify-between gap-3 text-sm"
                                            data-testid={`order-item-${i.product_id}`}
                                        >
                                            <span className="text-muted-foreground">
                                                {i.name} <span className="font-semibold text-foreground">x{i.quantity}</span>
                                                {i.starts_on && (
                                                    <span className="block text-xs">
                                                        {formatDate(i.starts_on)}
                                                        {i.ends_on ? ` – ${formatDate(i.ends_on)}` : " itibaren"} geçerli
                                                    </span>
                                                )}
                                            </span>
                                            <span className="font-semibold">{formatMoney(i.total, order.currency)}</span>
                                        </li>
                                    ))}
                                </ul>
                                <div className="mt-4 border-t border-border pt-4">
                                    {order.bundle_discount > 0 && (
                                        <div className="mb-3 flex items-center justify-between text-sm text-[hsl(var(--brand-green))]" data-testid="order-bundle-discount">
                                            <span>Paket indirimi (%{Math.round((order.bundle_discount_rate || 0) * 100)})</span>
                                            <span className="font-semibold">- {formatMoney(order.bundle_discount, order.currency)}</span>
                                        </div>
                                    )}
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm font-semibold">Toplam</span>
                                        <span className="font-heading text-2xl font-extrabold" data-testid="order-total">
                                            {formatMoney(order.price, order.currency)}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {bank && order.payment?.status !== "paid" && (
                                <div className="card-surface p-6" data-testid="order-bank-details">
                                    <div className="flex items-center gap-2.5">
                                        <Landmark className="h-5 w-5 text-primary" />
                                        <h2 className="font-heading text-lg font-bold">Havale / EFT bilgileri</h2>
                                    </div>
                                    <dl className="mt-4 space-y-3 text-sm">
                                        {[
                                            ["Banka", bank.bank_name],
                                            ["Hesap sahibi", bank.account_name],
                                            ["IBAN", bank.iban],
                                            ["Açıklama", order.reference_code],
                                        ].map(([label, value]) => (
                                            <div key={label} className="flex items-start justify-between gap-3">
                                                <dt className="text-muted-foreground">{label}</dt>
                                                <dd className="flex items-center gap-2 text-right font-semibold">
                                                    {value}
                                                    <button
                                                        type="button"
                                                        onClick={() => copy(value, label)}
                                                        className="rounded p-1 text-muted-foreground transition-colors hover:text-primary"
                                                        aria-label={`${label} kopyala`}
                                                    >
                                                        <Copy className="h-3.5 w-3.5" />
                                                    </button>
                                                </dd>
                                            </div>
                                        ))}
                                    </dl>
                                    <p className="mt-4 text-xs leading-5 text-muted-foreground">
                                        Açıklama alanına sipariş kodunuzu yazmayı unutmayın. Ödemeniz onaylanınca
                                        belgeleriniz e-postanıza gönderilir.
                                    </p>
                                </div>
                            )}

                            {order.delivery?.sent_at && (
                                <div
                                    className="rounded-xl border border-[hsl(var(--brand-green)/0.3)] bg-[hsl(var(--brand-green)/0.07)] p-6"
                                    data-testid="order-delivery"
                                >
                                    <div className="flex items-center gap-2.5">
                                        <CheckCircle2 className="h-5 w-5 text-[hsl(var(--brand-green))]" />
                                        <h2 className="font-heading text-lg font-bold text-[hsl(var(--brand-green))]">
                                            Belgeleriniz hazır
                                        </h2>
                                    </div>
                                    {order.delivery.message && (
                                        <p className="mt-3 text-sm leading-6">{order.delivery.message}</p>
                                    )}
                                    <div className="mt-4 flex flex-wrap gap-3">
                                        {order.delivery.esim_file_id && (
                                            <Button asChild className="h-11" data-testid="download-esim-button">
                                                <a
                                                    href={`${API}/files/${order.delivery.esim_file_id}?download=1`}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                >
                                                    <Download className="mr-2 h-4 w-4" /> eSIM QR kodunu indir
                                                </a>
                                            </Button>
                                        )}
                                        {order.delivery.policy_file_id && (
                                            <Button asChild className="h-11" data-testid="download-policy-button">
                                                <a
                                                    href={`${API}/files/${order.delivery.policy_file_id}?download=1`}
                                                    target="_blank"
                                                    rel="noreferrer"
                                                >
                                                    <Download className="mr-2 h-4 w-4" /> Poliçeyi indir
                                                </a>
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            )}

                            <div className="flex flex-wrap gap-3">
                                <Button asChild variant="secondary" className="h-11 border border-border">
                                    <Link to="/esim">Yeni eSIM siparişi</Link>
                                </Button>
                                <Button asChild variant="secondary" className="h-11 border border-border">
                                    <Link to="/seyahat-sigortasi">Sigorta paketleri</Link>
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </section>
        </div>
    );
}
