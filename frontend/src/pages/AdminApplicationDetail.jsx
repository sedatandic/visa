import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
    AlertTriangle,
    ArrowLeft,
    Baby,
    Banknote,
    BellRing,
    Download,
    ExternalLink,
    FileCheck2,
    Loader2,
    Mail,
    MessageCircle,
    Save,
    Send,
    Trash2,
    UploadCloud,
    User,
} from "lucide-react";
import { toast } from "sonner";
import { api, apiError, fileUrl, API } from "../lib/api";
import {
    STATUS_META,
    STATUS_OPTIONS,
    PURPOSE_LABELS,
    formatDate,
    formatDateTime,
    formatMoney,
    setMeta,
} from "../lib/site";
import { AdminLayout } from "../components/AdminLayout";
import { PaymentBadge, StatusBadge } from "../components/StatusBadge";
import { Button } from "../components/ui/button";
import { Textarea } from "../components/ui/textarea";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "../components/ui/dialog";

const MARITAL_TR = {
    single: "Bekar",
    married: "Evli",
    divorced: "Boşanmış",
    widowed: "Eşi vefat etmiş",
};


const Row = ({ label, value }) => (
    <div className="flex items-start justify-between gap-4 border-b border-border py-2.5 last:border-0">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="text-right text-sm font-semibold">{value || "-"}</span>
    </div>
);

const DocumentViewer = ({ fileId, title }) => {
    if (!fileId) {
        return (
            <div className="rounded-xl border border-dashed border-border p-5 text-center text-xs text-muted-foreground">
                {title}: yüklenmemiş
            </div>
        );
    }
    const url = fileUrl(fileId);
    return (
        <div className="rounded-xl border border-border bg-card p-3">
            <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-semibold">{title}</p>
                <a href={url} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-[11px] font-semibold text-primary hover:underline" data-testid={`open-document-${title}`}>
                    Aç <ExternalLink className="h-3 w-3" />
                </a>
            </div>
            <Dialog>
                <DialogTrigger asChild>
                    <button type="button" className="mt-2 block w-full overflow-hidden rounded-lg border border-border">
                        <img src={url} alt={title} className="h-32 w-full bg-muted object-contain" data-testid={`document-thumbnail-${title}`} />
                    </button>
                </DialogTrigger>
                <DialogContent className="max-w-3xl bg-card">
                    <DialogHeader>
                        <DialogTitle>{title}</DialogTitle>
                    </DialogHeader>
                    <img src={url} alt={title} className="max-h-[70vh] w-full object-contain" />
                    <a href={`${url}?download=1`} className="mt-2 inline-flex items-center gap-2 text-sm font-semibold text-primary hover:underline">
                        <Download className="h-4 w-4" /> İndir
                    </a>
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default function AdminApplicationDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const fileRef = useRef(null);
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [sending, setSending] = useState(false);
    const [whatsapping, setWhatsapping] = useState(false);
    const [markingPaid, setMarkingPaid] = useState(false);
    const [status, setStatus] = useState("");
    const [note, setNote] = useState("");
    const [visaMessage, setVisaMessage] = useState("");
    const [missingDocs, setMissingDocs] = useState(null);
    const [remindering, setRemindering] = useState(false);
    const [zamiBusy, setZamiBusy] = useState(false);
    const [zamiHandoff, setZamiHandoff] = useState(null);
    const [zamiResult, setZamiResult] = useState(null);
    const [zamiRef, setZamiRef] = useState("");
    const [waBusy, setWaBusy] = useState(false);
    const [waResult, setWaResult] = useState(null);

    const loadMissing = useCallback(async () => {
        try {
            const { data: res } = await api.get(`/admin/applications/${id}/missing-documents`);
            setMissingDocs(res);
        } catch {
            setMissingDocs({ missing: [], reminder_count: 0, last_sent_at: null });
        }
    }, [id]);

    useEffect(() => {
        loadMissing();
    }, [loadMissing]);

    const sendReminder = async () => {
        setRemindering(true);
        try {
            const { data: res } = await api.post(`/admin/applications/${id}/send-document-reminder`, {
                origin_url: window.location.origin,
            });
            if (res.application) {
                setData((d) => ({ ...d, application: res.application }));
                setStatus(res.application.status);
            }
            await loadMissing();
            const emailStatus = res.result?.email?.status || res.result?.status;
            toast.success(
                emailStatus === "sent"
                    ? "Hatırlatma e-postası müşteriye gönderildi."
                    : "Hatırlatma kaydedildi. E-posta servisi yapılandırılmadığı için gönderim atlandı."
            );
        } catch (err) {
            toast.error(apiError(err, "Hatırlatma gönderilemedi."));
        } finally {
            setRemindering(false);
        }
    };

    useEffect(() => {
        setMeta("Başvuru Detayı | Dubai Vize Online", "Başvuru detayı, belge görüntüleyici ve vize teslimi.");
    }, []);

    const load = useCallback(async () => {
        setLoading(true);
        try {
            const { data: res } = await api.get(`/admin/applications/${id}`);
            setData(res);
            setStatus(res.application.status);
            setNote(res.application.admin_notes || "");
            setZamiRef(res.application.zami_reference || "");
        } catch (err) {
            if (err?.response?.status === 401) {
                localStorage.removeItem("dv_admin_token");
                navigate("/admin/giris");
                return;
            }
            toast.error(apiError(err, "Başvuru yüklenemedi."));
        } finally {
            setLoading(false);
        }
    }, [id, navigate]);

    useEffect(() => {
        load();
    }, [load]);

    const saveTravelerGender = async (index, gender) => {
        try {
            const { data: res } = await api.patch(`/admin/applications/${id}/traveler`, { index, gender });
            setData((d) => ({ ...d, application: res.application }));
            toast.success("Cinsiyet kaydedildi. Zami aktarımı yapılabilir.");
        } catch (err) {
            toast.error(apiError(err, "Cinsiyet kaydedilemedi."));
        }
    };

    const save = async () => {
        setSaving(true);
        try {
            const { data: res } = await api.patch(`/admin/applications/${id}`, { status, note, notify: true });
            setData((d) => ({ ...d, application: res.application }));
            if (res.email_notification === "sent") toast.success("Durum güncellendi ve başvuru sahibine e-posta gönderildi.");
            else if (res.email_notification === "skipped") toast.success("Durum güncellendi. (E-posta servisi yapılandırılmadığı için bildirim gönderilmedi.)");
            else toast.success("Durum güncellendi.");
        } catch (err) {
            toast.error(apiError(err, "Güncelleme başarısız."));
        } finally {
            setSaving(false);
        }
    };

    const uploadVisa = async (files) => {
        const file = files?.[0];
        if (!file) return;
        const form = new FormData();
        form.append("file", file);
        setUploading(true);
        try {
            const { data: res } = await api.post(`/admin/applications/${id}/visa-document`, form, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setData((d) => ({ ...d, application: res.application }));
            toast.success("Vize belgesi yüklendi. Şimdi müşteriye gönderebilirsiniz.");
        } catch (err) {
            toast.error(apiError(err, "Vize belgesi yüklenemedi."));
        } finally {
            setUploading(false);
        }
    };

    const removeVisa = async () => {
        try {
            const { data: res } = await api.delete(`/admin/applications/${id}/visa-document`);
            setData((d) => ({ ...d, application: res.application }));
            toast.success("Vize belgesi kaldırıldı.");
        } catch (err) {
            toast.error(apiError(err, "İşlem başarısız."));
        }
    };

    const markPaid = async () => {
        setMarkingPaid(true);
        try {
            const { data: res } = await api.post(`/admin/applications/${id}/mark-paid`);
            if (res.application) {
                setData((d) => ({ ...d, application: res.application }));
                setStatus(res.application.status);
            }
            toast.success("Ödeme onaylandı, başvuru incelemeye alındı.");
        } catch (err) {
            toast.error(apiError(err, "Ödeme onaylanamadı."));
        } finally {
            setMarkingPaid(false);
        }
    };

    const sendWhatsApp = async (template) => {
        setWhatsapping(true);
        try {
            const { data: res } = await api.post(`/admin/applications/${id}/whatsapp`, {
                template,
                origin_url: window.location.origin,
            });
            window.open(res.url, "_blank", "noopener,noreferrer");
            toast.success("WhatsApp mesajı hazırlandı, pencerede gönder tuşuna basın.");
        } catch (err) {
            toast.error(apiError(err, "WhatsApp mesajı hazırlanamadı."));
        } finally {
            setWhatsapping(false);
        }
    };

    const sendVisa = async () => {
        setSending(true);
        try {
            const { data: res } = await api.post(`/admin/applications/${id}/send-visa`, {
                origin_url: window.location.origin,
                message: visaMessage,
                set_approved: true,
            });
            setData((d) => ({ ...d, application: res.application }));
            setStatus(res.application.status);
            if (res.email_notification === "sent") {
                toast.success("Vize belgesi müşteriye e-posta ile gönderildi ve başvuru onaylandı.");
            } else if (res.email_notification === "skipped") {
                toast.success(
                    "Başvuru onaylandı ve belge takip sayfasından indirilebilir hale geldi. E-posta servisi yapılandırılmadığı için bildirim gönderilemedi."
                );
            } else {
                toast.error("E-posta gönderilirken bir hata oluştu, ancak belge takip sayfasına eklendi.");
            }
        } catch (err) {
            toast.error(apiError(err, "Gönderim başarısız."));
        } finally {
            setSending(false);
        }
    };

    if (loading) {
        return (
            <AdminLayout>
                <div className="flex items-center justify-center py-20">
                    <Loader2 className="h-7 w-7 animate-spin text-primary" />
                </div>
            </AdminLayout>
        );
    }

    if (!data) {
        return (
            <AdminLayout title="Başvuru bulunamadı">
                <Button variant="secondary" className="h-11 border border-border" onClick={() => navigate("/admin")}>
                    <ArrowLeft className="mr-2 h-4 w-4" /> Listeye dön
                </Button>
            </AdminLayout>
        );
    }

    const a = data.application;
    const travelers = a.travelers || [];
    const pricing = a.pricing;

    const sendWhatsAppResult = async (status) => {
        setWaBusy(true);
        setWaResult(null);
        try {
            const { data: res } = await api.post(`/admin/whatsapp/send/${a.id}`, { status, force: true });
            setWaResult(res);
            if (res.status === "sent") toast.success("WhatsApp mesajı gönderildi.");
            else if (res.status === "manual") toast.info("Hazır WhatsApp bağlantısı oluşturuldu, aşağıdan açıp gönderin.");
            else toast.error(res.reason || res.detail || "Gönderilemedi.");
        } catch (e) {
            toast.error(apiError(e, "WhatsApp bildirimi başarısız."));
        } finally {
            setWaBusy(false);
        }
    };

    const saveZamiRef = async () => {
        setZamiBusy(true);
        try {
            await api.put(`/admin/zami/reference/${a.id}`, { zami_reference: zamiRef });
            toast.success("Zami başvuru numarası kaydedildi.");
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setZamiBusy(false);
        }
    };

    const checkZamiStatus = async () => {
        setZamiBusy(true);
        setZamiResult(null);
        try {
            const { data: res } = await api.post(`/admin/zami/check-status/${a.id}`, { notify: true });
            setZamiResult(res);
            if (!res.ok) {
                toast.error(res.error || "Durum okunamadı.");
            } else if (res.status_changed) {
                toast.success(`Durum güncellendi: ${res.new_status}. Müşteriye bilgi e-postası gönderildi.`);
                load();
            } else {
                toast.info(
                    res.matched_status
                        ? `Portal durumu: ${res.matched_status} (değişiklik yok).`
                        : "Portalda eşleşen durum bulunamadı."
                );
            }
        } catch (e) {
            toast.error(apiError(e, "Durum kontrolü başarısız."));
        } finally {
            setZamiBusy(false);
        }
    };

    const createZamiHandoff = async () => {
        setZamiBusy(true);
        try {
            const { data: res } = await api.post(`/admin/zami/handoff/${a.id}`);
            setZamiHandoff(res);
            toast.success("Aktarım kodu oluşturuldu. Zami formunda tarayıcı yardımcısına yapıştırın.");
        } catch (e) {
            toast.error(apiError(e, "Aktarım kodu oluşturulamadı."));
        } finally {
            setZamiBusy(false);
        }
    };

    const runZamiTransfer = async (dryRun) => {
        setZamiBusy(true);
        setZamiResult(null);
        try {
            const { data: res } = await api.post(`/admin/zami/transfer/${a.id}`, { dry_run: dryRun });
            setZamiResult(res);
            if (res.ok) {
                toast.success(
                    res.submitted
                        ? `Form dolduruldu ve gönderildi (${res.filled_count} alan).`
                        : `Form dolduruldu, gönderilmedi (${res.filled_count} alan).`
                );
            } else {
                toast.error(res.error || "Aktarım yapılamadı.");
            }
        } catch (e) {
            toast.error(apiError(e, "Aktarım yapılamadı."));
        } finally {
            setZamiBusy(false);
        }
    };

    const extra = a.extra_documents || {};
    const visa = a.visa_result;

    return (
        <AdminLayout>
            <div data-testid="admin-application-detail">
                <Button variant="secondary" className="h-10 border border-border" onClick={() => navigate("/admin")} data-testid="admin-back-to-list">
                    <ArrowLeft className="mr-2 h-4 w-4" /> Başvurular
                </Button>

                <div className="mt-5 flex flex-wrap items-start justify-between gap-4">
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Takip kodu</p>
                        <h1 className="font-heading text-3xl font-bold tracking-wider">{a.reference_code}</h1>
                        <p className="mt-1 text-sm text-muted-foreground">
                            {a.contact?.full_name} · {travelers.length} yolcu · {formatMoney(a.price, a.currency)}
                        </p>
                    </div>
                    <div className="flex flex-col items-start gap-2 sm:items-end">
                        <StatusBadge status={a.status} />
                        <PaymentBadge status={a.payment?.status} />
                    </div>
                </div>

                <div className="mt-7 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
                    <div className="space-y-6">
                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">İletişim</h2>
                            <div className="mt-3">
                                <Row label="Ad Soyad" value={a.contact?.full_name} />
                                <Row label="E-posta" value={a.contact?.email} />
                                <Row label="Telefon" value={a.contact?.phone} />
                                <Row label="Şehir" value={a.contact?.address_city} />
                            </div>
                            <div className="mt-4 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4" data-testid="admin-consents">
                                <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">Onay kayıtları</p>
                                <div className="mt-2 grid gap-1 text-xs sm:grid-cols-2">
                                    {[
                                        ["KVKK aydınlatma", a.kvkk_accepted],
                                        ["İade + Gizlilik", a.consents?.refund_privacy_accepted],
                                        ["Şartlar / sözleşme", a.consents?.service_terms_accepted],
                                        ["WhatsApp bildirimi", a.whatsapp_optin],
                                        ["Ticari ileti (pazarlama)", a.consents?.marketing_email_optin],
                                        ["Reklam eşleştirmesi", a.consents?.ad_personalization_optin],
                                    ].map(([label, given]) => (
                                        <p key={label} className={given ? "text-foreground" : "text-muted-foreground"}>
                                            {given ? "✓" : "—"} {label}
                                        </p>
                                    ))}
                                </div>
                                {a.consents?.accepted_at ? (
                                    <p className="mt-2 text-[11px] text-muted-foreground">
                                        Onay zamanı: {formatDate(a.consents.accepted_at)}
                                    </p>
                                ) : null}
                            </div>
                        </div>

                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Yolcular ({travelers.length})</h2>
                            <div className="mt-4 space-y-5">
                                {travelers.map((t, i) => (
                                    <div key={t.id || i} className="rounded-xl border border-border p-4" data-testid={`admin-traveler-${i}`}>
                                        <div className="flex flex-wrap items-center justify-between gap-2">
                                            <div className="flex items-center gap-2.5">
                                                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                                                    {t.applicant_type === "child" ? <Baby className="h-4 w-4 text-primary" /> : <User className="h-4 w-4 text-primary" />}
                                                </span>
                                                <div>
                                                    <p className="text-sm font-bold">{t.first_name} {t.last_name}</p>
                                                    <p className="text-xs text-muted-foreground">{t.applicant_type === "child" ? "Çocuk" : "Yetişkin"} · {t.visa_type_name}</p>
                                                </div>
                                            </div>
                                            <span className="font-heading text-sm font-bold">{formatMoney(t.price, t.currency)}</span>
                                        </div>
                                        <div className="mt-3 grid gap-x-6 gap-y-1 text-xs text-muted-foreground sm:grid-cols-2">
                                            <p>Doğum: <strong className="text-foreground">{formatDate(t.birth_date)}</strong></p>
                                            {t.gender === "male" || t.gender === "female" ? (
                                                <p>Cinsiyet: <strong className="text-foreground">{t.gender === "female" ? "Kadın" : "Erkek"}</strong></p>
                                            ) : (
                                                <div
                                                    className="flex items-center gap-2 sm:col-span-2"
                                                    data-testid={`traveler-${i}-gender-missing`}
                                                >
                                                    <span className="font-medium text-[hsl(var(--status-warning))]">
                                                        Cinsiyet okunamadı — Zami aktarımı için seçin:
                                                    </span>
                                                    <Select
                                                        value=""
                                                        onValueChange={(v) => saveTravelerGender(i, v)}
                                                    >
                                                        <SelectTrigger
                                                            className="h-8 w-32"
                                                            data-testid={`traveler-${i}-gender-select`}
                                                        >
                                                            <SelectValue placeholder="Seçiniz" />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            <SelectItem value="male">Erkek</SelectItem>
                                                            <SelectItem value="female">Kadın</SelectItem>
                                                        </SelectContent>
                                                    </Select>
                                                </div>
                                            )}
                                            <p>Pasaport: <strong className="text-foreground">{t.passport_no}</strong></p>
                                            <p>Geçerlilik: <strong className="text-foreground">{formatDate(t.passport_expiry)}</strong></p>
                                            {t.national_id ? <p>T.C. No: <strong className="text-foreground">{t.national_id}</strong></p> : null}
                                            {t.marital_status ? <p>Medeni hal: <strong className="text-foreground">{MARITAL_TR[t.marital_status] || t.marital_status}</strong></p> : null}
                                            {t.profession ? <p>Meslek: <strong className="text-foreground">{t.profession}</strong></p> : null}
                                            {t.mother_name ? <p>Anne adı: <strong className="text-foreground">{t.mother_name}</strong></p> : null}
                                            {t.father_name ? <p>Baba adı: <strong className="text-foreground">{t.father_name}</strong></p> : null}
                                        </div>
                                        <div className="mt-4 grid gap-3 sm:grid-cols-2">
                                            <DocumentViewer fileId={t.documents?.passport_file_id || t.passport_file_id} title={`Pasaport ${i + 1}`} />
                                            <DocumentViewer fileId={t.documents?.photo_file_id || t.photo_file_id} title={`Vesikalık ${i + 1}`} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Seyahat bilgileri</h2>
                            <div className="mt-3">
                                <Row label="Gidiş" value={formatDate(a.travel?.arrival_date)} />
                                <Row label="Dönüş" value={formatDate(a.travel?.departure_date)} />
                                <Row label="Amacı" value={PURPOSE_LABELS[a.travel?.purpose] || a.travel?.purpose} />
                                <Row label="Doğum ülkesi" value={a.travel?.birth_country === "TR" ? "Türkiye" : a.travel?.birth_country} />
                                <Row label="Konaklama" value={a.travel?.accommodation} />
                                <Row label="Uçuş no" value={a.travel?.flight_no} />
                                <Row label="Not" value={a.travel?.notes} />
                            </div>
                            {(extra.ticket_file_id || extra.hotel_file_id || (extra.other_file_ids || []).length > 0) && (
                                <div className="mt-5 border-t border-border pt-4">
                                    <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Ek belgeler</p>
                                    <div className="mt-3 grid gap-3 sm:grid-cols-3">
                                        {extra.ticket_file_id && <DocumentViewer fileId={extra.ticket_file_id} title="Uçak Bileti" />}
                                        {extra.hotel_file_id && <DocumentViewer fileId={extra.hotel_file_id} title="Otel Rezervasyonu" />}
                                        {(extra.other_file_ids || []).map((fid, i) => (
                                            <DocumentViewer key={fid} fileId={fid} title={`Diğer ${i + 1}`} />
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Fiyat dökümü</h2>
                            {pricing ? (
                                <div className="mt-3">
                                    <Row label={`Vize bedelleri (${pricing.traveler_count} yolcu)`} value={formatMoney(pricing.subtotal, pricing.currency)} />
                                    {pricing.family_discount > 0 && (
                                        <Row label={`Aile indirimi (%${Math.round(pricing.family_discount_rate * 100)})`} value={`- ${formatMoney(pricing.family_discount, pricing.currency)}`} />
                                    )}
                                    {(pricing.addons || []).map((ad) => (
                                        <Row key={ad.id} label={`${ad.name} x${ad.quantity}`} value={formatMoney(ad.total, pricing.currency)} />
                                    ))}
                                    {(pricing.store_items || []).map((s) => (
                                        <Row
                                            key={s.product_id}
                                            label={`${s.name} x${s.quantity}${s.kind_label ? ` · ${s.kind_label}` : ""}${
                                                s.scheduled_date
                                                    ? ` · ${formatDate(s.scheduled_date)}${s.scheduled_time ? ` ${s.scheduled_time}` : ""}`
                                                    : s.starts_on
                                                    ? ` · ${formatDate(s.starts_on)}${s.ends_on ? ` – ${formatDate(s.ends_on)}` : ""}`
                                                    : ""
                                            }`}
                                            value={formatMoney(s.total, pricing.currency)}
                                        />
                                    ))}
                                    {a.linked_order_reference && (
                                        <Row label="Bağlı sipariş (teslimat)" value={a.linked_order_reference} />
                                    )}
                                    {pricing.bundle_discount > 0 && (
                                        <Row
                                            label={`${pricing.bundle_discount_title || "Seyahat paketi indirimi"} (%${Math.round((pricing.bundle_discount_rate || 0) * 100)})`}
                                            value={`- ${formatMoney(pricing.bundle_discount, pricing.currency)}`}
                                        />
                                    )}
                                    <Row label="Toplam" value={formatMoney(pricing.total, pricing.currency)} />
                                </div>
                            ) : (
                                <p className="mt-3 text-sm text-muted-foreground">Fiyat dökümü yok.</p>
                            )}
                        </div>

                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Ödeme hareketleri</h2>
                            {(data.transactions || []).length === 0 ? (
                                <p className="mt-3 text-sm text-muted-foreground">Henüz ödeme denemesi yok.</p>
                            ) : (
                                <div className="mt-3 space-y-3">
                                    {data.transactions.map((t) => (
                                        <div key={t.session_id} className="rounded-lg border border-border p-3 text-sm">
                                            <div className="flex items-center justify-between gap-3">
                                                <span className="font-semibold">{formatMoney(t.amount, (t.currency || "try").toUpperCase())}</span>
                                                <PaymentBadge status={t.payment_status} />
                                            </div>
                                            <p className="mt-1 break-all text-xs text-muted-foreground">{t.session_id}</p>
                                            <p className="text-xs text-muted-foreground">{formatDateTime(t.created_at)}</p>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {a.payment?.status !== "paid" && (
                                <div className="mt-4 rounded-lg border border-dashed border-border p-4">
                                    <p className="text-sm font-semibold">
                                        {a.payment?.method === "bank_transfer"
                                            ? "Müşteri havale/EFT ile ödemeyi seçti"
                                            : "Ödeme henüz alınmadı"}
                                    </p>
                                    <p className="mt-1 text-xs leading-5 text-muted-foreground">
                                        Havale/EFT tutarı hesabınıza geçtiyse ödemeyi onaylayın; müşteriye
                                        bilgilendirme e-postası gider ve başvuru incelemeye alınır.
                                    </p>
                                    <Button
                                        onClick={markPaid}
                                        disabled={markingPaid}
                                        className="mt-3 h-10"
                                        data-testid="mark-paid-button"
                                    >
                                        {markingPaid ? (
                                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> İşleniyor…</>
                                        ) : (
                                            <><Banknote className="mr-2 h-4 w-4" /> Havale ödemesini onayla</>
                                        )}
                                    </Button>
                                </div>
                            )}
                        </div>

                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Durum geçmişi</h2>
                            <ol className="mt-4 space-y-4">
                                {(a.status_history || []).map((h, i) => (
                                    <li key={i} className="flex gap-3">
                                        <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
                                        <div>
                                            <p className="text-sm font-semibold">{STATUS_META[h.status]?.label || h.status}</p>
                                            <p className="text-xs text-muted-foreground">{formatDateTime(h.at)}</p>
                                            {h.note && <p className="mt-0.5 text-sm text-muted-foreground">{h.note}</p>}
                                        </div>
                                    </li>
                                ))}
                            </ol>
                        </div>
                    </div>

                    <div className="space-y-6">
                        {/* MISSING DOCUMENTS */}
                        <div className="card-surface p-6" data-testid="admin-missing-documents-panel">
                            <div className="flex items-center gap-2">
                                <AlertTriangle className="h-4.5 w-4.5 text-[hsl(var(--status-warning))]" />
                                <h2 className="font-heading text-base font-bold">Eksik belgeler</h2>
                            </div>
                            {missingDocs === null ? (
                                <p className="mt-3 text-sm text-muted-foreground">Kontrol ediliyor…</p>
                            ) : missingDocs.missing.length === 0 ? (
                                <p className="mt-3 text-sm text-muted-foreground" data-testid="admin-no-missing-documents">
                                    Bu başvuruda eksik belge yok.
                                </p>
                            ) : (
                                <>
                                    <ul className="mt-3 space-y-2">
                                        {missingDocs.missing.map((m) => (
                                            <li
                                                key={`${m.key}-${m.traveler_id || "app"}`}
                                                className="flex items-start gap-2 text-sm"
                                                data-testid={`admin-missing-doc-${m.key}`}
                                            >
                                                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[hsl(var(--status-warning))]" />
                                                <span>
                                                    {m.label}
                                                    {m.traveler_name ? (
                                                        <span className="text-muted-foreground"> — {m.traveler_name}</span>
                                                    ) : null}
                                                </span>
                                            </li>
                                        ))}
                                    </ul>
                                    <p className="mt-3 text-xs leading-5 text-muted-foreground">
                                        Gönderilen hatırlatma: {missingDocs.reminder_count} / 3
                                        {missingDocs.last_sent_at
                                            ? ` · Son: ${formatDateTime(missingDocs.last_sent_at)}`
                                            : ""}
                                    </p>
                                    <Button
                                        onClick={sendReminder}
                                        disabled={remindering}
                                        className="mt-4 h-10 w-full"
                                        data-testid="send-document-reminder-button"
                                    >
                                        {remindering ? (
                                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Gönderiliyor…</>
                                        ) : (
                                            <><BellRing className="mr-2 h-4 w-4" /> Hatırlatma e-postası gönder</>
                                        )}
                                    </Button>
                                </>
                            )}
                        </div>

                        {/* ZAMI TRANSFER */}
                        <div className="card-surface p-6" data-testid="admin-zami-panel">
                            <div className="flex items-center gap-2">
                                <Send className="h-4.5 w-4.5 text-primary" />
                                <h2 className="font-heading text-base font-bold">Zami Tours portalına aktar</h2>
                            </div>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Zami portalında başvuru formunu açın ve tarayıcı yardımcısını çalıştırıp aşağıdaki
                                aktarım kodunu yapıştırın; alanlar otomatik dolar. Alternatif olarak robot oturumu
                                açıksa aktarımı sunucu üzerinden de yapabilirsiniz.
                            </p>
                            <div className="mt-4 flex flex-wrap gap-3">
                                <Button
                                    type="button"
                                    onClick={createZamiHandoff}
                                    disabled={zamiBusy}
                                    data-testid="zami-handoff-button"
                                >
                                    {zamiBusy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
                                    Aktarım kodu oluştur
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="border border-border"
                                    onClick={() => runZamiTransfer(true)}
                                    disabled={zamiBusy}
                                    data-testid="zami-rpa-dry-button"
                                >
                                    Robotla doldur (göndermeden)
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="border border-border"
                                    onClick={() => runZamiTransfer(false)}
                                    disabled={zamiBusy}
                                    data-testid="zami-rpa-submit-button"
                                >
                                    Robotla doldur ve gönder
                                </Button>
                            </div>
                            <div className="mt-5 grid gap-3 border-t border-border pt-5 sm:grid-cols-[1fr_auto] sm:items-end">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium" htmlFor="zami-ref-input">
                                        Zami başvuru numarası (durum takibi için)
                                    </label>
                                    <Input
                                        id="zami-ref-input"
                                        value={zamiRef}
                                        onChange={(e) => setZamiRef(e.target.value)}
                                        placeholder="Portaldaki başvuru no"
                                        data-testid="zami-reference-input"
                                    />
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    <Button
                                        type="button"
                                        variant="secondary"
                                        className="border border-border"
                                        onClick={saveZamiRef}
                                        disabled={zamiBusy}
                                        data-testid="zami-reference-save"
                                    >
                                        Kaydet
                                    </Button>
                                    <Button
                                        type="button"
                                        variant="secondary"
                                        className="border border-border"
                                        onClick={checkZamiStatus}
                                        disabled={zamiBusy}
                                        data-testid="zami-status-check-button"
                                    >
                                        Durumu kontrol et
                                    </Button>
                                </div>
                            </div>
                            {a.zami_status_checked_at && (
                                <p className="mt-3 text-sm text-muted-foreground" data-testid="zami-last-status">
                                    Son kontrol: {formatDateTime(a.zami_status_checked_at)}
                                    {a.zami_status ? ` · portal durumu: ${a.zami_status}` : " · eşleşme yok"}
                                    {a.zami_status_raw ? ` (${a.zami_status_raw.slice(0, 80)})` : ""}
                                </p>
                            )}
                            {zamiHandoff && (
                                <div className="mt-4 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4" data-testid="zami-handoff-box">
                                    <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                        Aktarım kodu ({zamiHandoff.expires_in_minutes} dk geçerli)
                                    </p>
                                    <p className="mt-1 break-all font-mono text-sm font-bold" data-testid="zami-handoff-token">
                                        {zamiHandoff.token}
                                    </p>
                                    <Button
                                        type="button"
                                        variant="secondary"
                                        className="mt-3 h-9 border border-border"
                                        onClick={() => {
                                            navigator.clipboard?.writeText(zamiHandoff.token);
                                            toast.success("Kod kopyalandı.");
                                        }}
                                        data-testid="zami-handoff-copy"
                                    >
                                        Kodu kopyala
                                    </Button>
                                </div>
                            )}
                            {zamiResult && (
                                <div className="mt-4 rounded-xl border border-border p-4" data-testid="zami-rpa-result">
                                    <p className="text-sm">
                                        {zamiResult.ok
                                            ? `${zamiResult.filled_count} alan dolduruldu${zamiResult.submitted ? " ve form gönderildi" : " (gönderilmedi)"}.`
                                            : zamiResult.error}
                                    </p>
                                    {zamiResult.ok && zamiResult.manual_pending?.length > 0 && (
                                        <div
                                            className="mt-3 rounded-lg border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.08)] p-3"
                                            data-testid="zami-manual-pending"
                                        >
                                            <p className="flex items-center gap-1.5 text-xs font-bold">
                                                <AlertTriangle className="h-3.5 w-3.5 text-[hsl(var(--status-warning))]" />
                                                Zami formunda elle doldurulması gereken alanlar
                                            </p>
                                            <ul className="mt-2 flex flex-wrap gap-1.5">
                                                {zamiResult.manual_pending.map((label) => (
                                                    <li
                                                        key={label}
                                                        className="rounded-md bg-background px-2 py-1 text-xs text-muted-foreground"
                                                    >
                                                        {label}
                                                    </li>
                                                ))}
                                            </ul>
                                            <p className="mt-2 text-xs text-muted-foreground">
                                                Bu bilgileri başvuru formunda toplamıyoruz; portalda tamamlayın.
                                            </p>
                                        </div>
                                    )}
                                    {zamiResult.ok && zamiResult.missing?.length > 0 && (
                                        <p className="mt-2 text-xs text-destructive" data-testid="zami-missing-fields">
                                            Eşlemede bulunamayan alanlar: {zamiResult.missing.join(", ")}
                                        </p>
                                    )}
                                    {zamiResult.screenshot && (
                                        <img
                                            src={zamiResult.screenshot}
                                            alt="Zami ekran görüntüsü"
                                            className="mt-3 w-full rounded-lg border border-border"
                                            data-testid="zami-rpa-screenshot-app"
                                        />
                                    )}
                                </div>
                            )}
                        </div>

                        {/* WHATSAPP */}
                        <div className="card-surface p-6" data-testid="admin-whatsapp-panel">
                            <div className="flex items-center gap-2">
                                <MessageCircle className="h-4.5 w-4.5 text-primary" />
                                <h2 className="font-heading text-base font-bold">WhatsApp ile sonucu bildir</h2>
                            </div>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Müşteri WhatsApp onayı: {a.whatsapp_optin ? "verildi" : "verilmedi"}. Manuel modda
                                hazır metinli WhatsApp bağlantısı açılır; API modu açıksa mesaj otomatik gönderilir.
                            </p>
                            <div className="mt-4 flex flex-wrap gap-3">
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="border border-border"
                                    onClick={() => sendWhatsAppResult("approved")}
                                    disabled={waBusy}
                                    data-testid="whatsapp-send-approved"
                                >
                                    {waBusy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <MessageCircle className="mr-2 h-4 w-4" />}
                                    Onay mesajı
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="border border-border"
                                    onClick={() => sendWhatsAppResult("rejected")}
                                    disabled={waBusy}
                                    data-testid="whatsapp-send-rejected"
                                >
                                    Ret mesajı
                                </Button>
                            </div>
                            {waResult && (
                                <div className="mt-4 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4" data-testid="whatsapp-result">
                                    <p className="text-sm text-muted-foreground">{waResult.reason || waResult.detail || "Gönderildi."}</p>
                                    {waResult.message && (
                                        <p className="mt-2 rounded-lg bg-card p-3 text-sm" data-testid="whatsapp-message-preview">
                                            {waResult.message}
                                        </p>
                                    )}
                                    {waResult.link && (
                                        <a
                                            href={waResult.link}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="mt-3 inline-flex font-heading text-sm font-bold text-primary underline"
                                            data-testid="whatsapp-manual-link"
                                        >
                                            WhatsApp'ta aç ve gönder
                                        </a>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* VISA DELIVERY */}
                        <div className="card-surface p-6" data-testid="admin-visa-delivery-panel">
                            <div className="flex items-center gap-2">
                                <FileCheck2 className="h-4.5 w-4.5 text-primary" />
                                <h2 className="font-heading text-base font-bold">Onaylanan vizeyi gönder</h2>
                            </div>
                            <p className="mt-2 text-sm leading-6 text-muted-foreground">
                                Onaylanan vize belgesini (PDF veya görsel) yükleyin, ardından tek tıkla
                                başvuru sahibine e-posta ile gönderin. Belge aynı zamanda takip sayfasından
                                indirilebilir hale gelir.
                            </p>

                            <input
                                ref={fileRef}
                                type="file"
                                accept="application/pdf,image/jpeg,image/png"
                                className="hidden"
                                data-testid="visa-document-file-input"
                                onChange={(e) => uploadVisa(e.target.files)}
                            />

                            {visa?.file_id ? (
                                <div className="mt-5 rounded-xl border border-[hsl(var(--brand-green)/0.30)] bg-[hsl(var(--brand-green)/0.07)] p-4" data-testid="visa-document-uploaded">
                                    <p className="text-sm font-semibold text-[hsl(var(--brand-green))]">{visa.filename}</p>
                                    <p className="mt-0.5 text-xs text-[hsl(var(--brand-green))]/80">
                                        Yüklendi: {formatDateTime(visa.uploaded_at)}
                                        {visa.sent_at ? ` · Gönderildi: ${formatDateTime(visa.sent_at)}` : " · Henüz gönderilmedi"}
                                    </p>
                                    {visa.send_status && (
                                        <p className="mt-1 text-xs font-semibold text-[hsl(var(--brand-green))]">
                                            E-posta durumu: {visa.send_status === "sent" ? "Gönderildi" : visa.send_status === "skipped" ? "Atlandı (anahtar yok)" : "Hata"}
                                        </p>
                                    )}
                                    <div className="mt-4 flex flex-wrap gap-2">
                                        <Button asChild variant="secondary" className="h-10 border border-border">
                                            <a href={`${API}/files/${visa.file_id}`} target="_blank" rel="noreferrer">
                                                <ExternalLink className="mr-2 h-4 w-4" /> Önizle
                                            </a>
                                        </Button>
                                        <Button variant="secondary" className="h-10 border border-border" onClick={() => fileRef.current?.click()} disabled={uploading} data-testid="visa-document-replace-button">
                                            <UploadCloud className="mr-2 h-4 w-4" /> Değiştir
                                        </Button>
                                        <Button variant="secondary" className="h-10 border border-border text-destructive" onClick={removeVisa} data-testid="visa-document-delete-button">
                                            <Trash2 className="mr-2 h-4 w-4" /> Kaldır
                                        </Button>
                                    </div>

                                    <div className="mt-5 space-y-3">
                                        <Label htmlFor="visa-message">Müşteriye not (opsiyonel)</Label>
                                        <Textarea
                                            id="visa-message"
                                            rows={3}
                                            value={visaMessage}
                                            onChange={(e) => setVisaMessage(e.target.value)}
                                            placeholder="Örn. Vizeniz 30 gün geçerlidir, giriş tarihinden itibaren işlemeye başlar."
                                            data-testid="visa-message-input"
                                        />
                                        <Button onClick={sendVisa} disabled={sending} className="h-11 w-full" data-testid="send-visa-button">
                                            {sending ? (
                                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Gönderiliyor…</>
                                            ) : (
                                                <><Send className="mr-2 h-4 w-4" /> {visa.sent_at ? "Tekrar gönder" : "Müşteriye gönder ve onayla"}</>
                                            )}
                                        </Button>
                                        <Button
                                            variant="secondary"
                                            onClick={() => sendWhatsApp("visa_ready")}
                                            disabled={whatsapping}
                                            className="h-11 w-full border border-[hsl(var(--brand-green)/0.4)] bg-[hsl(var(--brand-green)/0.08)] text-[hsl(var(--brand-green))] hover:bg-[hsl(var(--brand-green)/0.14)]"
                                            data-testid="send-visa-whatsapp-button"
                                        >
                                            {whatsapping ? (
                                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Hazırlanıyor…</>
                                            ) : (
                                                <><MessageCircle className="mr-2 h-4 w-4" /> WhatsApp ile bildir</>
                                            )}
                                        </Button>
                                        <p className="flex items-start gap-1.5 text-xs leading-5 text-muted-foreground">
                                            <Mail className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                                            Gönderim ile başvuru durumu otomatik olarak "Onaylandı" olur.
                                        </p>
                                    </div>
                                </div>
                            ) : (
                                <button
                                    type="button"
                                    onClick={() => fileRef.current?.click()}
                                    className="mt-5 flex w-full flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border bg-card px-4 py-8 text-center transition-colors hover:border-primary/50"
                                    data-testid="visa-document-dropzone"
                                >
                                    {uploading ? (
                                        <>
                                            <Loader2 className="h-7 w-7 animate-spin text-primary" />
                                            <span className="text-sm font-semibold">Yükleniyor…</span>
                                        </>
                                    ) : (
                                        <>
                                            <span className="flex h-11 w-11 items-center justify-center rounded-full bg-primary/10">
                                                <UploadCloud className="h-5 w-5 text-primary" />
                                            </span>
                                            <span className="text-sm font-semibold">Vize belgesini yükleyin</span>
                                            <span className="text-xs text-muted-foreground">PDF / JPG / PNG · Maks. 15 MB</span>
                                        </>
                                    )}
                                </button>
                            )}
                        </div>

                        {/* STATUS */}
                        <div className="card-surface p-6">
                            <h2 className="font-heading text-base font-bold">Durumu güncelle</h2>
                            <div className="mt-4 space-y-4">
                                <div className="space-y-2">
                                    <Label>Yeni durum</Label>
                                    <Select value={status} onValueChange={setStatus}>
                                        <SelectTrigger data-testid="admin-status-update-select">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {STATUS_OPTIONS.map((s) => (
                                                <SelectItem key={s} value={s}>{STATUS_META[s]?.label || s}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="admin-note">Danışman notu (e-postada gönderilir)</Label>
                                    <Textarea id="admin-note" rows={4} value={note} onChange={(e) => setNote(e.target.value)} placeholder="Örn. Fotoğrafınız yeniden yüklenmeli." data-testid="admin-note-input" />
                                </div>
                                <Button onClick={save} disabled={saving} className="h-11 w-full" data-testid="admin-save-status-button">
                                    {saving ? (
                                        <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Kaydediliyor…</>
                                    ) : (
                                        <><Save className="mr-2 h-4 w-4" /> Kaydet</>
                                    )}
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </AdminLayout>
    );
}
