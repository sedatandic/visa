import React, { useEffect, useState } from "react";
import { Loader2, PackageCheck, RefreshCw, Send, Wallet } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { formatDate, formatDateTime, formatMoney } from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { FileDropzone } from "../components/FileDropzone";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";

const STATUS_OPTIONS = [
    { value: "pending", label: "Ödeme bekleniyor" },
    { value: "processing", label: "Hazırlanıyor" },
    { value: "fulfilled", label: "Teslim edildi" },
    { value: "cancelled", label: "İptal" },
];

const PAYMENT_LABEL = {
    pending: "Ödeme bekleniyor",
    awaiting_transfer: "Havale bekleniyor",
    paid: "Ödeme alındı",
    refunded: "İade",
};

const OrderRow = ({ order, onUpdate }) => {
    const [open, setOpen] = useState(false);
    const [esimFile, setEsimFile] = useState(null);
    const [policyFile, setPolicyFile] = useState(null);
    const [message, setMessage] = useState("");
    const [busy, setBusy] = useState(false);

    const patch = async (payload) => {
        setBusy(true);
        try {
            const { data } = await api.patch(`/admin/orders/${order.id}`, payload);
            onUpdate(data);
            toast.success("Sipariş güncellendi.");
        } catch (err) {
            toast.error(apiError(err, "Güncelleme başarısız."));
        } finally {
            setBusy(false);
        }
    };

    const deliver = async () => {
        if (!esimFile && !policyFile) {
            toast.error("En az bir belge yükleyin (eSIM QR veya poliçe).");
            return;
        }
        setBusy(true);
        try {
            const { data } = await api.post(`/admin/orders/${order.id}/deliver`, {
                esim_file_id: esimFile?.file_id || null,
                policy_file_id: policyFile?.file_id || null,
                message: message.trim(),
                origin_url: window.location.origin,
            });
            onUpdate(data.order);
            toast.success(
                data.email?.status === "sent"
                    ? "Belgeler müşteriye e-posta ile gönderildi."
                    : "Belgeler kaydedildi. E-posta servisi yapılandırılmadığı için gönderim atlandı."
            );
        } catch (err) {
            toast.error(apiError(err, "Teslimat başarısız."));
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="card-surface p-5" data-testid={`admin-order-${order.reference_code}`}>
            <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                    <p className="font-heading text-base font-extrabold">{order.reference_code}</p>
                    {order.source === "visa_application" && (
                        <p
                            className="mt-1 inline-flex rounded-full bg-primary/10 px-2 py-0.5 text-[11px] font-semibold text-primary"
                            data-testid={`order-source-visa-${order.reference_code}`}
                        >
                            Vize başvurusu ile alındı{order.application_reference ? ` · ${order.application_reference}` : ""}
                        </p>
                    )}
                    <p className="mt-1 text-sm text-muted-foreground">
                        {order.contact?.full_name} · {order.contact?.email} · {order.contact?.phone}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                        {formatDateTime(order.created_at)} ·{" "}
                        {(order.items || []).map((i) => `${i.name} x${i.quantity}`).join(", ")}
                    </p>
                    {(order.items || []).some((i) => i.starts_on) && (
                        <div className="mt-2 space-y-1" data-testid={`order-item-dates-${order.reference_code}`}>
                            {(order.items || [])
                                .filter((i) => i.starts_on)
                                .map((i) => (
                                    <p key={i.product_id} className="text-xs text-muted-foreground">
                                        <span className="font-semibold text-foreground">{i.name}</span>:{" "}
                                        {formatDate(i.starts_on)}
                                        {i.ends_on ? ` – ${formatDate(i.ends_on)}` : " itibaren"} tarihinde başlatılacak
                                    </p>
                                ))}
                        </div>
                    )}
                    {order.note && (
                        <p className="mt-2 rounded-lg bg-[hsl(var(--cloud))] p-3 text-xs leading-5">
                            Müşteri notu: {order.note}
                        </p>
                    )}
                </div>
                <div className="text-right">
                    <p className="font-heading text-xl font-extrabold">
                        {formatMoney(order.price, order.currency)}
                    </p>
                    {order.bundle_discount > 0 && (
                        <p className="mt-0.5 text-xs font-semibold text-[hsl(var(--brand-green))]" data-testid={`order-bundle-discount-${order.reference_code}`}>
                            Paket indirimi: - {formatMoney(order.bundle_discount, order.currency)}
                        </p>
                    )}
                    <p className="mt-1 text-xs font-semibold text-muted-foreground">
                        {PAYMENT_LABEL[order.payment?.status] || "-"}
                    </p>
                </div>
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-3">
                <div className="w-48">
                    <Select value={order.status} onValueChange={(v) => patch({ status: v })}>
                        <SelectTrigger data-testid={`order-status-select-${order.reference_code}`}>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {STATUS_OPTIONS.map((s) => (
                                <SelectItem key={s.value} value={s.value}>
                                    {s.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
                {order.payment?.status !== "paid" && (
                    <Button
                        variant="secondary"
                        className="h-10 border border-border"
                        onClick={() => patch({ payment_status: "paid" })}
                        disabled={busy}
                        data-testid={`order-mark-paid-${order.reference_code}`}
                    >
                        <Wallet className="mr-2 h-4 w-4" /> Ödemeyi onayla
                    </Button>
                )}
                <Button
                    variant="secondary"
                    className="h-10 border border-border"
                    onClick={() => setOpen((o) => !o)}
                    data-testid={`order-toggle-deliver-${order.reference_code}`}
                >
                    <PackageCheck className="mr-2 h-4 w-4" /> {open ? "Teslimatı kapat" : "Belge gönder"}
                </Button>
                {order.delivery?.sent_at && (
                    <span className="text-xs font-semibold text-[hsl(var(--brand-green))]">
                        Teslim edildi: {formatDateTime(order.delivery.sent_at)}
                    </span>
                )}
            </div>

            {open && (
                <div className="mt-5 rounded-xl border border-border bg-[hsl(var(--cloud))] p-5">
                    <div className="grid gap-5 sm:grid-cols-2">
                        <FileDropzone
                            label="eSIM QR kodu"
                            hint="PNG / JPG"
                            docType="other"
                            value={esimFile}
                            onChange={setEsimFile}
                            testId={`order-esim-upload-${order.reference_code}`}
                        />
                        <FileDropzone
                            label="Sigorta poliçesi"
                            hint="PDF"
                            docType="other"
                            value={policyFile}
                            onChange={setPolicyFile}
                            testId={`order-policy-upload-${order.reference_code}`}
                        />
                    </div>
                    <div className="mt-4 space-y-2">
                        <Label htmlFor={`msg-${order.id}`}>Müşteriye mesaj (opsiyonel)</Label>
                        <Textarea
                            id={`msg-${order.id}`}
                            rows={2}
                            value={message}
                            onChange={(e) => setMessage(e.target.value)}
                            placeholder="Kurulum adımları veya poliçe detayları"
                            data-testid={`order-message-${order.reference_code}`}
                        />
                    </div>
                    <Button
                        onClick={deliver}
                        disabled={busy}
                        className="mt-4 h-11"
                        data-testid={`order-deliver-${order.reference_code}`}
                    >
                        {busy ? (
                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Gönderiliyor…</>
                        ) : (
                            <><Send className="mr-2 h-4 w-4" /> Belgeleri gönder</>
                        )}
                    </Button>
                </div>
            )}
        </div>
    );
};

const ProductCard = ({ product, onUpdate }) => {
    const [price, setPrice] = useState(String(product.price_usd ?? ""));
    const [busy, setBusy] = useState(false);

    const save = async () => {
        setBusy(true);
        try {
            const { data } = await api.patch(`/admin/products/${product.id}`, {
                price_usd: Number(price),
            });
            onUpdate(data);
            toast.success(`${data.name} fiyatı güncellendi.`);
        } catch (err) {
            toast.error(apiError(err, "Fiyat güncellenemedi."));
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="card-surface p-5" data-testid={`admin-product-${product.id}`}>
            <p className="font-heading text-sm font-bold">{product.name}</p>
            <p className="mt-1 text-xs text-muted-foreground">
                {formatMoney(product.price, product.currency)} · {product.kind_label}
            </p>
            <div className="mt-3 flex items-center gap-2">
                <input
                    type="number"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    className="h-10 w-24 rounded-lg border border-border bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
                    data-testid={`product-price-input-${product.id}`}
                />
                <span className="text-sm text-muted-foreground">$</span>
                <Button
                    onClick={save}
                    disabled={busy}
                    className="h-10"
                    data-testid={`product-save-${product.id}`}
                >
                    Kaydet
                </Button>
            </div>
        </div>
    );
};

export default function AdminOrders() {
    const [orders, setOrders] = useState([]);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    const load = () =>
        Promise.all([api.get("/admin/orders"), api.get("/admin/products")])
            .then(([o, p]) => {
                setOrders(o.data.items || []);
                setProducts(p.data.items || []);
            })
            .catch((err) => toast.error(apiError(err, "Siparişler yüklenemedi.")))
            .finally(() => setLoading(false));

    useEffect(() => {
        load();
    }, []);

    const updateOrder = (updated) =>
        setOrders((list) => list.map((o) => (o.id === updated.id ? updated : o)));
    const updateProduct = (updated) =>
        setProducts((list) => list.map((p) => (p.id === updated.id ? updated : p)));

    return (
        <AdminLayout
            title="eSIM & sigorta siparişleri"
            description="Siparişleri takip edin, havale ödemelerini onaylayın, eSIM QR kodu ve poliçe PDF'ini müşteriye gönderin."
        >
            <div data-testid="admin-orders-page">
                {loading ? (
                    <div className="flex justify-center py-16">
                        <Loader2 className="h-6 w-6 animate-spin text-primary" />
                    </div>
                ) : (
                    <>
                        <div className="mb-8">
                            <div className="flex flex-wrap items-center justify-between gap-3">
                                <h2 className="font-heading text-lg font-bold">Paket fiyatları ($)</h2>
                                <Button
                                    variant="secondary"
                                    className="h-10 border border-border"
                                    onClick={load}
                                    data-testid="orders-refresh-button"
                                >
                                    <RefreshCw className="mr-2 h-4 w-4" /> Yenile
                                </Button>
                            </div>
                            <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                                {products.map((p) => (
                                    <ProductCard key={p.id} product={p} onUpdate={updateProduct} />
                                ))}
                            </div>
                        </div>

                        <h2 className="font-heading text-lg font-bold">Siparişler ({orders.length})</h2>
                        {orders.length === 0 ? (
                            <div className="card-surface mt-4 p-8 text-center">
                                <p className="text-sm text-muted-foreground">Henüz sipariş yok.</p>
                            </div>
                        ) : (
                            <div className="mt-4 space-y-4">
                                {orders.map((o) => (
                                    <OrderRow key={o.id} order={o} onUpdate={updateOrder} />
                                ))}
                            </div>
                        )}
                    </>
                )}
            </div>
        </AdminLayout>
    );
}
