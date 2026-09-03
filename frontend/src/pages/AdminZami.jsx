import React, { useEffect, useMemo, useState } from "react";
import {
    AlertTriangle,
    CheckCircle2,
    ExternalLink,
    ListChecks,
    Loader2,
    LogIn,
    RefreshCw,
    Save,
    Send,
    Sparkles,
    Trash2,
    Wand2,
} from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { AdminLayout } from "../components/AdminLayout";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Switch } from "../components/ui/switch";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "../components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";

const NONE = "__none__";

const Section = ({ title, description, children, testId }) => (
    <div className="card-surface p-6" data-testid={testId}>
        <h2 className="font-heading text-base font-bold">{title}</h2>
        {description && <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{description}</p>}
        <div className="mt-5">{children}</div>
    </div>
);

export default function AdminZami() {
    const [loading, setLoading] = useState(true);
    const [config, setConfig] = useState(null);
    const [settings, setSettings] = useState({ portal_url: "", username: "", password: "" });
    const [mapping, setMapping] = useState({
        form_url: "",
        submit_selector: "",
        dry_run: true,
        fields: {},
        traveler_fields: {},
        status_url: "",
        status_search_selector: "",
        status_result_selector: "",
        status_keywords: { approved: [], rejected: [], reviewing: [], cancelled: [] },
        auto_check_enabled: false,
        auto_check_hours: 6,
        auto_notify: true,
    });
    const [formHtml, setFormHtml] = useState("");
    const [parsedFields, setParsedFields] = useState([]);
    const [saving, setSaving] = useState(false);
    const [parsing, setParsing] = useState(false);
    const [session, setSession] = useState(null);
    const [rpa, setRpa] = useState({ session_id: null, stage: null, captcha_image: null, screenshot: null, message: "" });
    const [captcha, setCaptcha] = useState("");
    const [otp, setOtp] = useState("");
    const [busy, setBusy] = useState(false);
    const [logs, setLogs] = useState([]);
    const [captured, setCaptured] = useState(null);
    const [suggestions, setSuggestions] = useState(null);
    const [captureToken, setCaptureToken] = useState(null);
    const [readiness, setReadiness] = useState(null);

    const loadReadiness = async () => {
        setBusy(true);
        try {
            const { data } = await api.get("/admin/zami/readiness");
            setReadiness(data);
        } catch (e) {
            toast.error(apiError(e, "Hazırlık kontrolü yapılamadı."));
        } finally {
            setBusy(false);
        }
    };
    const [candidates, setCandidates] = useState([]);
    const [selected, setSelected] = useState({});
    const [bulkResults, setBulkResults] = useState(null);
    const [sweep, setSweep] = useState(null);

    const applyMapping = (m) =>
        setMapping({
            form_url: m.form_url || "",
            submit_selector: m.submit_selector || "",
            dry_run: m.dry_run !== false,
            fields: m.fields || {},
            traveler_fields: m.traveler_fields || {},
            status_url: m.status_url || "",
            status_search_selector: m.status_search_selector || "",
            status_result_selector: m.status_result_selector || "",
            status_keywords: m.status_keywords || { approved: [], rejected: [], reviewing: [], cancelled: [] },
            auto_check_enabled: !!m.auto_check_enabled,
            auto_check_hours: m.auto_check_hours || 6,
            auto_notify: m.auto_notify !== false,
        });

    const load = async () => {
        try {
            const { data } = await api.get("/admin/zami/config");
            setConfig(data);
            setSettings({ portal_url: data.settings.portal_url || "", username: data.settings.username || "", password: "" });
            applyMapping(data.mapping || {});
            setSession(data.session);
            setCaptured(data.captured || null);
            setSuggestions(data.suggestions || null);
            const capturedFields = (data.captured?.form?.fields || []).map((f) => ({
                ...f,
                selector: f.selector || (f.name ? `[name="${f.name}"]` : `#${f.id}`),
            }));
            if (capturedFields.length) setParsedFields(capturedFields);
        } catch (e) {
            toast.error(apiError(e, "Zami ayarları yüklenemedi."));
        } finally {
            setLoading(false);
        }
    };

    const loadLogs = async () => {
        try {
            const { data } = await api.get("/admin/zami/logs");
            setLogs(data.items || []);
        } catch {
            /* sessiz */
        }
    };

    useEffect(() => {
        load();
        loadLogs();
        loadCandidates();
    }, []);

    const selectorOptions = useMemo(
        () =>
            parsedFields.map((f) => ({
                value: f.selector,
                label: `${f.label || f.name} · ${f.selector} (${f.type})`,
            })),
        [parsedFields]
    );

    const saveSettings = async () => {
        setSaving(true);
        try {
            const body = { portal_url: settings.portal_url, username: settings.username };
            if (settings.password) body.password = settings.password;
            const { data } = await api.put("/admin/zami/settings", body);
            setConfig((c) => ({ ...c, settings: data.settings }));
            setSettings((s) => ({ ...s, password: "" }));
            toast.success("Portal ayarları kaydedildi.");
        } catch (e) {
            toast.error(apiError(e, "Kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const saveMapping = async () => {
        setSaving(true);
        try {
            const { data } = await api.put("/admin/zami/mapping", mapping);
            applyMapping(data.mapping || {});
            toast.success("Alan eşlemesi kaydedildi. Hem bookmarklet hem robot bu eşlemeyi kullanır.");
            loadLogs();
        } catch (e) {
            toast.error(apiError(e, "Eşleme kaydedilemedi."));
        } finally {
            setSaving(false);
        }
    };

    const parseHtml = async () => {
        if (formHtml.trim().length < 20) {
            toast.error("Zami başvuru formunun HTML'ini yapıştırın.");
            return;
        }
        setParsing(true);
        try {
            const { data } = await api.post("/admin/zami/parse-form", { html: formHtml });
            setParsedFields(data.fields || []);
            toast.success(`${data.count} form alanı bulundu. Şimdi aşağıdan eşleyin.`);
        } catch (e) {
            toast.error(apiError(e, "Form alanları okunamadı."));
        } finally {
            setParsing(false);
        }
    };

    const setFieldMap = (scope, key, selector) =>
        setMapping((m) => {
            const target = { ...(scope === "global" ? m.fields : m.traveler_fields) };
            if (!selector || selector === NONE) delete target[key];
            else target[key] = selector;
            return scope === "global" ? { ...m, fields: target } : { ...m, traveler_fields: target };
        });

    const loadCandidates = async () => {
        try {
            const { data } = await api.get("/admin/zami/candidates");
            setCandidates(data.items || []);
        } catch (e) {
            toast.error(apiError(e, "Başvurular yüklenemedi."));
        }
    };

    const toggleSelected = (id) =>
        setSelected((s) => {
            const next = { ...s };
            if (next[id]) delete next[id];
            else next[id] = true;
            return next;
        });

    const selectedIds = Object.keys(selected);

    const runBulk = async (dryRun) => {
        if (!selectedIds.length) {
            toast.error("En az bir başvuru seçin.");
            return;
        }
        if (selectedIds.length > 20) {
            toast.error("Tek seferde en fazla 20 başvuru aktarılabilir.");
            return;
        }
        setBusy(true);
        setBulkResults(null);
        try {
            const { data } = await api.post("/admin/zami/bulk-transfer", {
                application_ids: selectedIds,
                dry_run: dryRun,
            });
            setBulkResults(data);
            toast.success(`${data.ok_count}/${data.total} başvuru işlendi.`);
            loadCandidates();
            loadLogs();
        } catch (e) {
            toast.error(apiError(e, "Toplu aktarım başarısız."));
        } finally {
            setBusy(false);
        }
    };

    const runSweep = async () => {
        setBusy(true);
        setSweep(null);
        try {
            const { data } = await api.post("/admin/zami/check-status-all");
            setSweep(data);
            if (data.ok) toast.success(`${data.checked} başvuru kontrol edildi, ${data.changed} durum güncellendi.`);
            else toast.error(data.error || "Kontrol yapılamadı.");
            loadLogs();
        } catch (e) {
            toast.error(apiError(e, "Durum kontrolü başarısız."));
        } finally {
            setBusy(false);
        }
    };

    const setKeywords = (status, text) =>
        setMapping((m) => ({
            ...m,
            status_keywords: {
                ...m.status_keywords,
                [status]: text.split(",").map((w) => w.trim()).filter(Boolean),
            },
        }));

    const getCaptureToken = async () => {
        setBusy(true);
        try {
            const { data } = await api.post("/admin/zami/capture-token");
            setCaptureToken(data);
            toast.success("Yakalama kodu oluşturuldu. Zami sayfasında yakalama yardımcısını çalıştırın.");
        } catch (e) {
            toast.error(apiError(e, "Kod oluşturulamadı."));
        } finally {
            setBusy(false);
        }
    };

    const applySuggestions = async () => {
        setSaving(true);
        try {
            const { data } = await api.post("/admin/zami/apply-suggestions");
            applyMapping(data.mapping || {});
            const g = Object.keys(data.suggestions?.fields || {}).length;
            const t = Object.keys(data.suggestions?.traveler_fields || {}).length;
            toast.success(`${g} genel + ${t} yolcu alanı otomatik eşlendi. Kontrol edip kaydedin.`);
            load();
            loadLogs();
        } catch (e) {
            toast.error(apiError(e, "Öneriler uygulanamadı."));
        } finally {
            setSaving(false);
        }
    };

    const startSession = async () => {
        setBusy(true);
        try {
            const { data } = await api.post("/admin/zami/session/start");
            if (!data.ok) {
                toast.error(data.error || "Oturum başlatılamadı.");
            } else {
                setRpa(data);
                setCaptcha(data.captcha_guess || "");
                setOtp("");
                toast.success(
                    data.captcha_guess
                        ? `Login sayfası açıldı. Captcha yapay zeka ile okundu (${data.captcha_guess}) — kontrol edip giriş yapın.`
                        : "Portal login sayfası açıldı. Captcha'yı girin."
                );
            }
        } catch (e) {
            toast.error(apiError(e, "Oturum başlatılamadı."));
        } finally {
            setBusy(false);
            loadLogs();
        }
    };

    const newCaptcha = async () => {
        if (!rpa.session_id) return;
        setBusy(true);
        try {
            const { data } = await api.post("/admin/zami/session/captcha", { session_id: rpa.session_id });
            if (data.ok) {
                setRpa((r) => ({ ...r, captcha_image: data.captcha_image, captcha_guess: data.captcha_guess }));
                setCaptcha(data.captcha_guess || "");
            } else toast.error(data.error || "Captcha yenilenemedi.");
        } finally {
            setBusy(false);
        }
    };

    const doLogin = async () => {
        if (!rpa.session_id) return;
        setBusy(true);
        try {
            const { data } = await api.post("/admin/zami/session/login", {
                session_id: rpa.session_id,
                captcha,
                otp,
            });
            setRpa((r) => ({ ...r, ...data, session_id: r.session_id }));
            if (data.captcha_guess) setCaptcha(data.captcha_guess);
            if (data.ok && data.stage === "ready") {
                toast.success(data.message || "Giriş başarılı.");
                load();
            } else if (data.ok && data.stage === "otp") {
                toast.info(data.message || "OTP kodu girin.");
            } else {
                toast.error(data.error || "Giriş yapılamadı.");
            }
        } catch (e) {
            toast.error(apiError(e, "Giriş denenemedi."));
        } finally {
            setBusy(false);
            loadLogs();
        }
    };

    const clearSession = async () => {
        setBusy(true);
        try {
            await api.delete("/admin/zami/session");
            setRpa({ session_id: null, stage: null, captcha_image: null, screenshot: null, message: "" });
            toast.success("Kayıtlı portal oturumu silindi.");
            load();
        } finally {
            setBusy(false);
        }
    };

    return (
        <AdminLayout
            title="Zami Tours Aktarımı"
            description="Bizde toplanan başvuruları Zami portalına aktarın. Portal girişinde CAPTCHA + OTP olduğu için giriş adımı insan onayıyla yapılır."
        >
            {loading ? (
                <div className="flex justify-center py-16">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <Tabs defaultValue="mapping" className="space-y-6">
                    <TabsList data-testid="zami-tabs">
                        <TabsTrigger value="mapping" data-testid="zami-tab-mapping">Alan Eşleme</TabsTrigger>
                        <TabsTrigger value="bookmarklet" data-testid="zami-tab-bookmarklet">Tarayıcı Yardımcısı (A)</TabsTrigger>
                        <TabsTrigger value="rpa" data-testid="zami-tab-rpa">Robot Oturumu (B)</TabsTrigger>
                        <TabsTrigger value="bulk" data-testid="zami-tab-bulk">Toplu Aktarım</TabsTrigger>
                        <TabsTrigger value="status" data-testid="zami-tab-status">Durum Takibi</TabsTrigger>
                        <TabsTrigger value="logs" data-testid="zami-tab-logs">Kayıtlar</TabsTrigger>
                    </TabsList>

                    {/* ------------------------------------------------ MAPPING */}
                    <TabsContent value="mapping" className="space-y-6">
                        <Section
                            title="0. Alanları Zami'den otomatik yakala (önerilen)"
                            description="HTML kopyalamaya gerek yok. Aşağıdaki yakalama yardımcısını yer imleri çubuğuna ekleyin, Zami'de ilgili sayfayı açıp çalıştırın; alan adlarını biz okuyup eşleme önerisi çıkarırız."
                            testId="zami-capture-section"
                        >
                            <ol className="space-y-2 text-sm leading-6 text-muted-foreground">
                                <li><strong className="text-foreground">1.</strong> "Yakalama kodu oluştur" butonuna basın.</li>
                                <li><strong className="text-foreground">2.</strong> Aşağıdaki "VizeAtlas → Alanları Yakala" bağlantısını yer imleri çubuğuna sürükleyin.</li>
                                <li><strong className="text-foreground">3.</strong> Zami'de <strong className="text-foreground">yeni başvuru formunu</strong> açıp yer imine tıklayın, kodu yapıştırın, "Tamam" (başvuru formu) seçin.</li>
                                <li><strong className="text-foreground">4.</strong> Aynısını <strong className="text-foreground">başvuru listesi/durum sayfasında</strong> yapın; bu kez "İptal" (durum sayfası) seçin.</li>
                                <li><strong className="text-foreground">5.</strong> Bu ekranı yenileyip "Önerilen eşlemeyi uygula" butonuna basın ve kontrol edip kaydedin.</li>
                            </ol>

                            <div className="mt-4 flex flex-wrap items-center gap-3">
                                <Button type="button" onClick={getCaptureToken} disabled={busy} data-testid="zami-capture-token-button">
                                    {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Wand2 className="mr-2 h-4 w-4" />}
                                    Yakalama kodu oluştur
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="border border-border"
                                    onClick={applySuggestions}
                                    disabled={saving || !(captured?.form?.fields || []).length}
                                    data-testid="zami-apply-suggestions-button"
                                >
                                    <Wand2 className="mr-2 h-4 w-4" /> Önerilen eşlemeyi uygula
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="border border-border"
                                    onClick={loadReadiness}
                                    disabled={busy}
                                    data-testid="zami-readiness-button"
                                >
                                    <ListChecks className="mr-2 h-4 w-4" /> Hazırlık kontrolü
                                </Button>
                                <Button type="button" variant="secondary" className="border border-border" onClick={load} data-testid="zami-capture-refresh">
                                    <RefreshCw className="mr-2 h-4 w-4" /> Yenile
                                </Button>
                            </div>

                            {readiness && (
                                <div className="mt-4 rounded-xl border border-border p-4" data-testid="zami-readiness-box">
                                    <p className="font-heading text-sm font-bold">
                                        {readiness.ready_robot
                                            ? "Hazır: robotla otomatik aktarım yapabilirsiniz."
                                            : readiness.ready_bookmarklet
                                              ? "Hazır: tarayıcı yardımcısı ile aktarım yapabilirsiniz (robot için oturum gerekli)."
                                              : "Eksikler var; aşağıdaki adımları tamamlayın."}
                                    </p>
                                    <ul className="mt-3 space-y-2">
                                        {readiness.checks.map((c) => (
                                            <li key={c.key} className="flex items-start gap-2 text-sm" data-testid={`zami-check-${c.key}`}>
                                                {c.ok ? (
                                                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--brand-green))]" />
                                                ) : (
                                                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--status-warning))]" />
                                                )}
                                                <span>
                                                    <strong className="font-semibold">{c.label}</strong>
                                                    <span className="block text-xs text-muted-foreground">{c.detail}</span>
                                                </span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {captureToken && (
                                <div className="mt-4 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4" data-testid="zami-capture-token-box">
                                    <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                                        Yakalama kodu ({captureToken.expires_in_minutes} dk geçerli)
                                    </p>
                                    <p className="mt-1 break-all font-mono text-sm font-bold" data-testid="zami-capture-token">
                                        {captureToken.token}
                                    </p>
                                    <Button
                                        type="button"
                                        variant="secondary"
                                        className="mt-3 h-9 border border-border"
                                        onClick={() => {
                                            navigator.clipboard?.writeText(captureToken.token);
                                            toast.success("Kod kopyalandı.");
                                        }}
                                        data-testid="zami-capture-token-copy"
                                    >
                                        Kodu kopyala
                                    </Button>
                                </div>
                            )}

                            <div className="mt-4 rounded-xl border border-border p-4">
                                <a
                                    className="font-heading text-sm font-bold text-primary underline"
                                    data-testid="zami-capture-bookmarklet-link"
                                    href={`javascript:(function(){var s=document.createElement('script');s.src='${window.location.origin}/api/zami/capture.js?t='+Date.now();document.body.appendChild(s);})();`}
                                    onClick={(e) => {
                                        e.preventDefault();
                                        toast.info("Bu bağlantıyı tıklamak yerine yer imleri çubuğuna sürükleyin.");
                                    }}
                                >
                                    VizeAtlas → Alanları Yakala (yer imine sürükleyin)
                                </a>
                                <Textarea
                                    readOnly
                                    rows={3}
                                    className="mt-3 font-mono text-xs"
                                    data-testid="zami-capture-bookmarklet-code"
                                    value={`javascript:(function(){var s=document.createElement('script');s.src='${window.location.origin}/api/zami/capture.js?t='+Date.now();document.body.appendChild(s);})();`}
                                />
                            </div>

                            <div className="mt-4 grid gap-3 sm:grid-cols-2" data-testid="zami-capture-status">
                                <div className="rounded-lg border border-border p-3 text-sm">
                                    <p className="font-semibold">Başvuru formu</p>
                                    <p className="mt-1 text-muted-foreground">
                                        {(captured?.form?.fields || []).length
                                            ? `${captured.form.fields.length} alan yakalandı${captured.form.url ? ` · ${captured.form.url}` : ""}`
                                            : "Henüz yakalanmadı"}
                                    </p>
                                </div>
                                <div className="rounded-lg border border-border p-3 text-sm">
                                    <p className="font-semibold">Durum / liste sayfası</p>
                                    <p className="mt-1 text-muted-foreground">
                                        {captured?.status?.url ? captured.status.url : "Henüz yakalanmadı"}
                                    </p>
                                </div>
                            </div>

                            {suggestions && (Object.keys(suggestions.fields || {}).length || Object.keys(suggestions.traveler_fields || {}).length) ? (
                                <p className="mt-3 text-sm text-[hsl(var(--brand-green))]" data-testid="zami-suggestion-summary">
                                    Otomatik eşleşme hazır: {Object.keys(suggestions.fields).length} genel,{" "}
                                    {Object.keys(suggestions.traveler_fields).length} yolcu alanı.
                                </p>
                            ) : null}
                        </Section>

                        <Section
                            title="1. Zami başvuru formunu tanıt"
                            description="Yakalama yardımcısını kullanamıyorsanız: Zami portalında yeni başvuru formunu açın, sağ tıklayıp 'Sayfa kaynağını görüntüle' (Ctrl+U) ile HTML'i kopyalayıp buraya yapıştırın."
                            testId="zami-parse-section"
                        >
                            <div className="grid gap-4 md:grid-cols-2">
                                <div className="space-y-2">
                                    <Label htmlFor="zami-form-url">Başvuru formu adresi (URL)</Label>
                                    <Input
                                        id="zami-form-url"
                                        value={mapping.form_url}
                                        onChange={(e) => setMapping((m) => ({ ...m, form_url: e.target.value }))}
                                        placeholder="https://visa.zamitours.ae/application/new"
                                        data-testid="zami-form-url-input"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="zami-submit">Gönder butonu seçicisi (CSS)</Label>
                                    <Input
                                        id="zami-submit"
                                        value={mapping.submit_selector}
                                        onChange={(e) => setMapping((m) => ({ ...m, submit_selector: e.target.value }))}
                                        placeholder='button[type="submit"]'
                                        data-testid="zami-submit-selector-input"
                                    />
                                </div>
                            </div>
                            <div className="mt-4 space-y-2">
                                <Label htmlFor="zami-html">Form HTML'i</Label>
                                <Textarea
                                    id="zami-html"
                                    rows={6}
                                    value={formHtml}
                                    onChange={(e) => setFormHtml(e.target.value)}
                                    placeholder="<form> ... </form>"
                                    data-testid="zami-html-input"
                                />
                            </div>
                            <div className="mt-4 flex flex-wrap items-center gap-3">
                                <Button type="button" onClick={parseHtml} disabled={parsing} data-testid="zami-parse-button">
                                    {parsing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Wand2 className="mr-2 h-4 w-4" />}
                                    Alanları çıkar
                                </Button>
                                {parsedFields.length > 0 && (
                                    <span className="text-sm text-muted-foreground" data-testid="zami-parsed-count">
                                        {parsedFields.length} alan bulundu
                                    </span>
                                )}
                            </div>
                        </Section>

                        <Section
                            title="2. Alanları eşle"
                            description={'Soldaki bizim alanımızı, sağda Zami formundaki karşılığıyla eşleştirin. Yolcu alanlarında birden fazla yolcu için {i} (0\'dan başlar) veya {n} (1\'den başlar) kullanabilirsiniz. Örnek: input[name="pax[{i}][first_name]"]'}
                            testId="zami-mapping-section"
                        >
                            <div className="grid gap-6 lg:grid-cols-2">
                                <div>
                                    <h3 className="font-heading text-sm font-bold">Başvuru geneli</h3>
                                    <div className="mt-3 space-y-3">
                                        {(config?.global_fields || []).map((f) => (
                                            <div key={f.key} className="grid gap-2 sm:grid-cols-[1fr_1.2fr] sm:items-center">
                                                <span className="text-sm text-muted-foreground">{f.label}</span>
                                                {selectorOptions.length ? (
                                                    <Select
                                                        value={mapping.fields[f.key] || NONE}
                                                        onValueChange={(v) => setFieldMap("global", f.key, v)}
                                                    >
                                                        <SelectTrigger data-testid={`zami-global-select-${f.key}`}>
                                                            <SelectValue placeholder="Eşleşme yok" />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            <SelectItem value={NONE}>Eşleşme yok</SelectItem>
                                                            {selectorOptions.map((o) => (
                                                                <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
                                                            ))}
                                                        </SelectContent>
                                                    </Select>
                                                ) : (
                                                    <Input
                                                        value={mapping.fields[f.key] || ""}
                                                        onChange={(e) => setFieldMap("global", f.key, e.target.value)}
                                                        placeholder='input[name="..."]'
                                                        data-testid={`zami-global-input-${f.key}`}
                                                    />
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div>
                                    <h3 className="font-heading text-sm font-bold">Yolcu bilgileri</h3>
                                    <div className="mt-3 space-y-3">
                                        {(config?.traveler_fields || []).map((f) => (
                                            <div key={f.key} className="grid gap-2 sm:grid-cols-[1fr_1.2fr] sm:items-center">
                                                <span className="text-sm text-muted-foreground">{f.label}</span>
                                                <Input
                                                    value={mapping.traveler_fields[f.key] || ""}
                                                    onChange={(e) => setFieldMap("traveler", f.key, e.target.value)}
                                                    placeholder='input[name="pax[{i}][first_name]"]'
                                                    data-testid={`zami-traveler-input-${f.key}`}
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-border pt-5">
                                <label className="flex items-center gap-3 text-sm">
                                    <Switch
                                        checked={mapping.dry_run}
                                        onCheckedChange={(c) => setMapping((m) => ({ ...m, dry_run: !!c }))}
                                        data-testid="zami-dryrun-switch"
                                    />
                                    Güvenli mod (robot formu doldurur ama göndermez)
                                </label>
                                <Button type="button" onClick={saveMapping} disabled={saving} data-testid="zami-save-mapping-button">
                                    {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                                    Eşlemeyi kaydet
                                </Button>
                            </div>
                        </Section>
                    </TabsContent>

                    {/* -------------------------------------------- BOOKMARKLET */}
                    <TabsContent value="bookmarklet" className="space-y-6">
                        <Section
                            title="Tarayıcı yardımcısı ile tek tık doldurma"
                            description="Şifre hiçbir yere kaydedilmez; Zami'ye kendiniz girersiniz (captcha + OTP). Formu açtıktan sonra yardımcıyı çalıştırıp aktarım kodunu yapıştırmanız yeterli."
                            testId="zami-bookmarklet-section"
                        >
                            <ol className="space-y-3 text-sm leading-6 text-muted-foreground">
                                <li>
                                    <strong className="text-foreground">1.</strong> Aşağıdaki bağlantıyı tarayıcınızın yer imleri
                                    çubuğuna sürükleyin (adı: “VizeAtlas → Zami Doldur”).
                                </li>
                                <li>
                                    <strong className="text-foreground">2.</strong> Zami portalına girin ve yeni başvuru formunu açın.
                                </li>
                                <li>
                                    <strong className="text-foreground">3.</strong> Admin panelinde ilgili başvuruyu açıp
                                    “Zami’ye aktar” butonundan <strong className="text-foreground">aktarım kodunu</strong> alın.
                                </li>
                                <li>
                                    <strong className="text-foreground">4.</strong> Zami formundayken yer imine tıklayın, kodu
                                    yapıştırın; alanlar dolar ve belgelerin indirme bağlantıları listelenir.
                                </li>
                            </ol>

                            <div className="mt-5 rounded-xl border border-border bg-[hsl(var(--cloud))] p-4">
                                <a
                                    className="font-heading text-sm font-bold text-primary underline"
                                    data-testid="zami-bookmarklet-link"
                                    href={`javascript:(function(){var s=document.createElement('script');s.src='${window.location.origin}/api/zami/bookmarklet.js?t='+Date.now();document.body.appendChild(s);})();`}
                                    onClick={(e) => {
                                        e.preventDefault();
                                        toast.info("Bu bağlantıyı tıklamak yerine yer imleri çubuğuna sürükleyin.");
                                    }}
                                >
                                    VizeAtlas → Zami Doldur (yer imine sürükleyin)
                                </a>
                                <p className="mt-3 text-xs leading-5 text-muted-foreground">
                                    Sürükleyemiyorsanız yeni bir yer imi oluşturup adres alanına şunu yapıştırın:
                                </p>
                                <Textarea
                                    readOnly
                                    rows={3}
                                    className="mt-2 font-mono text-xs"
                                    data-testid="zami-bookmarklet-code"
                                    value={`javascript:(function(){var s=document.createElement('script');s.src='${window.location.origin}/api/zami/bookmarklet.js?t='+Date.now();document.body.appendChild(s);})();`}
                                />
                            </div>

                            <div className="mt-5 flex items-start gap-2.5 rounded-xl border border-[hsl(var(--status-warning)/0.35)] bg-[hsl(var(--status-warning)/0.11)] p-4">
                                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--status-warning))]" />
                                <p className="text-sm leading-6 text-[hsl(var(--status-warning))]">
                                    Tarayıcı güvenliği nedeniyle <strong>dosya yükleme alanları</strong> otomatik doldurulamaz.
                                    Belgeler liste halinde gösterilir; indirip Zami formuna elle yüklemeniz gerekir.
                                </p>
                            </div>
                        </Section>
                    </TabsContent>

                    {/* ---------------------------------------------------- RPA */}
                    <TabsContent value="rpa" className="space-y-6">
                        <Section
                            title="Portal bilgileri"
                            description="Robot oturumu için portal kullanıcı adı ve şifresi sunucuda saklanır. Şifrenizi sohbet/e-posta yoluyla paylaşmayın; buradan girin."
                            testId="zami-settings-section"
                        >
                            <div className="grid gap-4 md:grid-cols-3">
                                <div className="space-y-2">
                                    <Label htmlFor="zami-portal">Portal adresi</Label>
                                    <Input
                                        id="zami-portal"
                                        value={settings.portal_url}
                                        onChange={(e) => setSettings((s) => ({ ...s, portal_url: e.target.value }))}
                                        data-testid="zami-portal-url-input"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="zami-user">Kullanıcı (e-posta)</Label>
                                    <Input
                                        id="zami-user"
                                        value={settings.username}
                                        onChange={(e) => setSettings((s) => ({ ...s, username: e.target.value }))}
                                        data-testid="zami-username-input"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="zami-pass">
                                        Şifre {config?.settings?.has_password ? "(kayıtlı · değiştirmek için yazın)" : ""}
                                    </Label>
                                    <Input
                                        id="zami-pass"
                                        type="password"
                                        value={settings.password}
                                        onChange={(e) => setSettings((s) => ({ ...s, password: e.target.value }))}
                                        placeholder="••••••••"
                                        data-testid="zami-password-input"
                                    />
                                </div>
                            </div>
                            <div className="mt-4">
                                <Button type="button" onClick={saveSettings} disabled={saving} data-testid="zami-save-settings-button">
                                    {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                                    Portal ayarlarını kaydet
                                </Button>
                            </div>
                        </Section>

                        <Section
                            title="Robot oturumu (captcha + OTP)"
                            description="Robot login sayfasını açar; captcha görselini ve gerekiyorsa OTP alanını size gösterir. Giriş sonrası oturum saklanır ve başvurular otomatik doldurulabilir."
                            testId="zami-rpa-section"
                        >
                            <div className="flex flex-wrap items-center gap-3">
                                <Button type="button" onClick={startSession} disabled={busy} data-testid="zami-session-start-button">
                                    {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <LogIn className="mr-2 h-4 w-4" />}
                                    Oturum başlat
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="border border-border"
                                    onClick={clearSession}
                                    disabled={busy}
                                    data-testid="zami-session-clear-button"
                                >
                                    <Trash2 className="mr-2 h-4 w-4" /> Kayıtlı oturumu sil
                                </Button>
                                <span className="text-sm text-muted-foreground" data-testid="zami-session-status">
                                    {session?.has_session
                                        ? `Kayıtlı oturum var (${session.saved_at ? new Date(session.saved_at).toLocaleString("tr-TR") : ""})`
                                        : "Kayıtlı oturum yok"}
                                </span>
                            </div>

                            {rpa.session_id && (
                                <div className="mt-6 grid gap-5 lg:grid-cols-[320px_1fr]">
                                    <div className="space-y-4">
                                        {rpa.stage !== "otp" && rpa.captcha_image && (
                                            <div>
                                                <Label>Captcha</Label>
                                                <div className="mt-2 flex items-center gap-3">
                                                    <img
                                                        src={rpa.captcha_image}
                                                        alt="Captcha"
                                                        className="h-12 rounded border border-border bg-white"
                                                        data-testid="zami-captcha-image"
                                                    />
                                                    <Button
                                                        type="button"
                                                        variant="secondary"
                                                        className="h-9 w-9 border border-border p-0"
                                                        onClick={newCaptcha}
                                                        disabled={busy}
                                                        aria-label="Captcha yenile"
                                                        data-testid="zami-captcha-refresh"
                                                    >
                                                        <RefreshCw className="h-4 w-4" />
                                                    </Button>
                                                </div>
                                                <Input
                                                    className="mt-3"
                                                    value={captcha}
                                                    onChange={(e) => setCaptcha(e.target.value)}
                                                    placeholder="3 haneli kod"
                                                    data-testid="zami-captcha-input"
                                                />
                                                {rpa.captcha_guess && (
                                                    <p
                                                        className="mt-2 flex items-center gap-1.5 text-xs font-medium text-primary"
                                                        data-testid="zami-captcha-ai-hint"
                                                    >
                                                        <Sparkles className="h-3.5 w-3.5" />
                                                        Yapay zeka okudu: {rpa.captcha_guess} — yanlışsa düzeltin.
                                                    </p>
                                                )}
                                            </div>
                                        )}
                                        {rpa.stage === "otp" && (
                                            <div>
                                                <Label htmlFor="zami-otp">OTP kodu</Label>
                                                <Input
                                                    id="zami-otp"
                                                    className="mt-2"
                                                    value={otp}
                                                    onChange={(e) => setOtp(e.target.value)}
                                                    placeholder="E-posta/SMS ile gelen kod"
                                                    data-testid="zami-otp-input"
                                                />
                                            </div>
                                        )}
                                        <Button type="button" onClick={doLogin} disabled={busy} data-testid="zami-login-button">
                                            {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <LogIn className="mr-2 h-4 w-4" />}
                                            {rpa.stage === "otp" ? "OTP'yi gönder" : "Giriş yap"}
                                        </Button>
                                        {rpa.message && <p className="text-sm text-muted-foreground">{rpa.message}</p>}
                                        {rpa.error && (
                                            <p className="text-sm font-medium text-destructive" data-testid="zami-rpa-error">
                                                {rpa.error}
                                            </p>
                                        )}
                                    </div>
                                    {rpa.screenshot && (
                                        <div>
                                            <Label>Portal ekranı</Label>
                                            <img
                                                src={rpa.screenshot}
                                                alt="Portal ekran görüntüsü"
                                                className="mt-2 w-full rounded-lg border border-border"
                                                data-testid="zami-rpa-screenshot"
                                            />
                                        </div>
                                    )}
                                </div>
                            )}
                        </Section>
                    </TabsContent>

                    {/* -------------------------------------------- TOPLU AKTARIM */}
                    <TabsContent value="bulk" className="space-y-6">
                        <Section
                            title="Toplu aktarım"
                            description="Seçtiğiniz başvurular sırayla Zami formuna doldurulur. Robot oturumu açık olmalıdır. Güvenli modda form doldurulur ama gönderilmez."
                            testId="zami-bulk-section"
                        >
                            <div className="flex flex-wrap items-center gap-3">
                                <Button
                                    type="button"
                                    onClick={() => runBulk(true)}
                                    disabled={busy || !selectedIds.length}
                                    data-testid="zami-bulk-dry-button"
                                >
                                    {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Send className="mr-2 h-4 w-4" />}
                                    Seçilenleri doldur (göndermeden)
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="border border-border"
                                    onClick={() => runBulk(false)}
                                    disabled={busy || !selectedIds.length}
                                    data-testid="zami-bulk-submit-button"
                                >
                                    Seçilenleri doldur ve gönder
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="border border-border"
                                    onClick={loadCandidates}
                                    data-testid="zami-bulk-refresh"
                                >
                                    <RefreshCw className="mr-2 h-4 w-4" /> Listeyi yenile
                                </Button>
                                <span className="text-sm text-muted-foreground" data-testid="zami-bulk-selected-count">
                                    {selectedIds.length} başvuru seçili
                                </span>
                            </div>

                            <div className="mt-5 overflow-x-auto">
                                <table className="w-full text-sm">
                                    <thead>
                                        <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted-foreground">
                                            <th className="w-10 py-2"> </th>
                                            <th className="py-2">Takip kodu</th>
                                            <th className="py-2">Başvuru sahibi</th>
                                            <th className="py-2">Yolcu</th>
                                            <th className="py-2">Durum</th>
                                            <th className="py-2">Zami no</th>
                                            <th className="py-2">Aktarım</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {candidates.length === 0 ? (
                                            <tr>
                                                <td colSpan={7} className="py-6 text-center text-muted-foreground" data-testid="zami-bulk-empty">
                                                    Aktarılmayı bekleyen başvuru yok.
                                                </td>
                                            </tr>
                                        ) : (
                                            candidates.map((c) => (
                                                <tr key={c.id} className="border-b border-border/60" data-testid={`zami-candidate-${c.reference_code}`}>
                                                    <td className="py-3">
                                                        <input
                                                            type="checkbox"
                                                            className="h-4 w-4 cursor-pointer accent-[hsl(var(--brand-green))]"
                                                            checked={!!selected[c.id]}
                                                            onChange={() => toggleSelected(c.id)}
                                                            aria-label={`${c.reference_code} seç`}
                                                            data-testid={`zami-candidate-check-${c.reference_code}`}
                                                        />
                                                    </td>
                                                    <td className="py-3 font-semibold">{c.reference_code}</td>
                                                    <td className="py-3">
                                                        {c.full_name}
                                                        <span className="block text-xs text-muted-foreground">{c.email}</span>
                                                    </td>
                                                    <td className="py-3">{c.traveler_count}</td>
                                                    <td className="py-3 text-muted-foreground">{c.status}</td>
                                                    <td className="py-3 text-muted-foreground">{c.zami_reference || "-"}</td>
                                                    <td className="py-3 text-xs text-muted-foreground">
                                                        {c.zami_transferred_at ? new Date(c.zami_transferred_at).toLocaleString("tr-TR") : "-"}
                                                    </td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>

                            {bulkResults && (
                                <div className="mt-5 space-y-2" data-testid="zami-bulk-results">
                                    <p className="text-sm font-semibold">
                                        Sonuç: {bulkResults.ok_count}/{bulkResults.total} başarılı
                                    </p>
                                    {bulkResults.results.map((r) => (
                                        <p
                                            key={r.application_id}
                                            className={`text-sm ${r.ok ? "text-muted-foreground" : "text-destructive"}`}
                                        >
                                            {r.reference_code || r.application_id}:{" "}
                                            {r.ok
                                                ? `${r.filled_count} alan${r.submitted ? " · gönderildi" : " · gönderilmedi"}`
                                                : r.error}
                                        </p>
                                    ))}
                                </div>
                            )}
                        </Section>
                    </TabsContent>

                    {/* --------------------------------------------- DURUM TAKIBI */}
                    <TabsContent value="status" className="space-y-6">
                        <Section
                            title="Otomatik durum takibi"
                            description="Robot, Zami'deki başvuru durumunu okur; onay/ret olduğunda başvuru durumunu güncelleyip müşteriye otomatik e-posta gönderir."
                            testId="zami-status-section"
                        >
                            <div className="grid gap-4 md:grid-cols-3">
                                <div className="space-y-2">
                                    <Label htmlFor="zami-status-url">Durum/liste sayfası adresi</Label>
                                    <Input
                                        id="zami-status-url"
                                        value={mapping.status_url}
                                        onChange={(e) => setMapping((m) => ({ ...m, status_url: e.target.value }))}
                                        placeholder="https://visa.zamitours.ae/applications"
                                        data-testid="zami-status-url-input"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="zami-status-search">Arama alanı seçicisi (varsa)</Label>
                                    <Input
                                        id="zami-status-search"
                                        value={mapping.status_search_selector}
                                        onChange={(e) => setMapping((m) => ({ ...m, status_search_selector: e.target.value }))}
                                        placeholder='input[name="search"]'
                                        data-testid="zami-status-search-input"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="zami-status-result">Sonuç satırı seçicisi (opsiyonel)</Label>
                                    <Input
                                        id="zami-status-result"
                                        value={mapping.status_result_selector}
                                        onChange={(e) => setMapping((m) => ({ ...m, status_result_selector: e.target.value }))}
                                        placeholder='tr:has-text("{ref}")'
                                        data-testid="zami-status-result-input"
                                    />
                                </div>
                            </div>

                            <div className="mt-5 grid gap-4 md:grid-cols-2">
                                {["approved", "rejected", "reviewing", "cancelled"].map((st) => (
                                    <div key={st} className="space-y-2">
                                        <Label htmlFor={`kw-${st}`}>
                                            {st === "approved"
                                                ? "Onay kelimeleri"
                                                : st === "rejected"
                                                  ? "Ret kelimeleri"
                                                  : st === "reviewing"
                                                    ? "İnceleme kelimeleri"
                                                    : "İptal kelimeleri"}
                                        </Label>
                                        <Input
                                            id={`kw-${st}`}
                                            value={(mapping.status_keywords?.[st] || []).join(", ")}
                                            onChange={(e) => setKeywords(st, e.target.value)}
                                            placeholder="approved, issued"
                                            data-testid={`zami-keywords-${st}`}
                                        />
                                    </div>
                                ))}
                            </div>

                            <div className="mt-6 flex flex-wrap items-center gap-6 border-t border-border pt-5">
                                <label className="flex items-center gap-3 text-sm">
                                    <Switch
                                        checked={mapping.auto_check_enabled}
                                        onCheckedChange={(c) => setMapping((m) => ({ ...m, auto_check_enabled: !!c }))}
                                        data-testid="zami-autocheck-switch"
                                    />
                                    Otomatik kontrolü aç
                                </label>
                                <div className="flex items-center gap-2 text-sm">
                                    <Label htmlFor="zami-hours" className="text-sm">Her</Label>
                                    <Input
                                        id="zami-hours"
                                        type="number"
                                        min={1}
                                        max={48}
                                        className="w-20"
                                        value={mapping.auto_check_hours}
                                        onChange={(e) => setMapping((m) => ({ ...m, auto_check_hours: Number(e.target.value) }))}
                                        data-testid="zami-autocheck-hours"
                                    />
                                    saatte bir
                                </div>
                                <label className="flex items-center gap-3 text-sm">
                                    <Switch
                                        checked={mapping.auto_notify}
                                        onCheckedChange={(c) => setMapping((m) => ({ ...m, auto_notify: !!c }))}
                                        data-testid="zami-autonotify-switch"
                                    />
                                    Durum değişince müşteriye e-posta gönder
                                </label>
                                <Button type="button" onClick={saveMapping} disabled={saving} data-testid="zami-save-status-button">
                                    {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                                    Kaydet
                                </Button>
                                <Button
                                    type="button"
                                    variant="secondary"
                                    className="border border-border"
                                    onClick={runSweep}
                                    disabled={busy}
                                    data-testid="zami-sweep-button"
                                >
                                    {busy ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                                    Şimdi kontrol et
                                </Button>
                            </div>

                            {sweep && (
                                <div className="mt-5 space-y-2" data-testid="zami-sweep-results">
                                    {sweep.ok ? (
                                        <>
                                            <p className="text-sm font-semibold">
                                                {sweep.checked} başvuru kontrol edildi · {sweep.changed} durum güncellendi
                                            </p>
                                            {(sweep.results || []).map((r, i) => (
                                                <p key={i} className={`text-sm ${r.ok ? "text-muted-foreground" : "text-destructive"}`}>
                                                    {r.reference_code}: {r.ok ? `${r.matched_status || "eşleşme yok"} (${r.raw_text || "-"})` : r.error}
                                                </p>
                                            ))}
                                        </>
                                    ) : (
                                        <p className="text-sm text-destructive">{sweep.error}</p>
                                    )}
                                </div>
                            )}
                        </Section>
                    </TabsContent>

                    {/* --------------------------------------------------- LOGS */}
                    <TabsContent value="logs">
                        <Section title="Aktarım kayıtları" description="Son 100 işlem." testId="zami-logs-section">
                            {logs.length === 0 ? (
                                <p className="text-sm text-muted-foreground" data-testid="zami-logs-empty">
                                    Henüz kayıt yok.
                                </p>
                            ) : (
                                <ul className="space-y-3">
                                    {logs.map((l) => (
                                        <li key={l.id} className="rounded-lg border border-border p-3 text-sm" data-testid={`zami-log-${l.id}`}>
                                            <div className="flex flex-wrap items-center justify-between gap-2">
                                                <span className="font-semibold">{l.event}</span>
                                                <span className="text-xs text-muted-foreground">
                                                    {l.created_at ? new Date(l.created_at).toLocaleString("tr-TR") : ""}
                                                </span>
                                            </div>
                                            <p className="mt-1 text-muted-foreground">
                                                {l.message}
                                                {l.reference_code ? ` · ${l.reference_code}` : ""}
                                            </p>
                                        </li>
                                    ))}
                                </ul>
                            )}
                            <div className="mt-4">
                                <Button type="button" variant="secondary" className="border border-border" onClick={loadLogs} data-testid="zami-logs-refresh">
                                    <RefreshCw className="mr-2 h-4 w-4" /> Yenile
                                </Button>
                            </div>
                        </Section>
                    </TabsContent>
                </Tabs>
            )}

            <p className="mt-6 flex items-center gap-2 text-xs text-muted-foreground">
                <ExternalLink className="h-3.5 w-3.5" />
                Portal: {config?.settings?.portal_url || "https://visa.zamitours.ae"}
                <Send className="ml-4 h-3.5 w-3.5" />
                Aktarım kodu, başvuru detay sayfasındaki “Zami’ye aktar” butonundan alınır.
            </p>
        </AdminLayout>
    );
}
