import React, { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";
import { api, apiError } from "../lib/api";
import { AdminLayout } from "../components/AdminLayout";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { WaBotSettings } from "../components/whatsapp/WaBotSettings";
import { WaConversations } from "../components/whatsapp/WaConversations";
import { WaDocumentQueue } from "../components/whatsapp/WaDocumentQueue";
import { WaManualNotify } from "../components/whatsapp/WaManualNotify";
import { WaSimulator } from "../components/whatsapp/WaSimulator";

export default function AdminWhatsApp() {
    const [config, setConfig] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        (async () => {
            try {
                const { data } = await api.get("/admin/whatsapp/ai/config");
                setConfig(data);
            } catch (e) {
                toast.error(apiError(e, "WhatsApp yapılandırması yüklenemedi."));
            } finally {
                setLoading(false);
            }
        })();
    }, []);

    const live = config?.mode === "live";

    return (
        <AdminLayout
            title="WhatsApp AI Botu"
            description="7/24 müşteri yanıtları, tedarikçi belgelerinin otomatik eşleştirilmesi ve vize sonucu bildirimleri."
            actions={
                config ? (
                    <Badge variant={live ? "default" : "secondary"} data-testid="wa-mode-badge">
                        {live ? "Canlı mod" : "Simülasyon modu"}
                    </Badge>
                ) : null
            }
        >
            {loading ? (
                <div className="flex justify-center py-16">
                    <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
            ) : (
                <>
                    {!live && (
                        <div className="mb-5 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900" data-testid="wa-simulate-warning">
                            Meta Cloud API kimlik bilgileri girilmediği için bot <b>simülasyon modunda</b> çalışıyor:
                            mesajlar gerçekten gönderilmez, yalnız kaydedilir. Canlıya almak için
                            <b> Bot Ayarları</b> sekmesinden Phone Number ID ve Access Token girin.
                        </div>
                    )}

                    <Tabs defaultValue="documents" className="space-y-5">
                        <TabsList data-testid="wa-tabs">
                            <TabsTrigger value="documents" data-testid="wa-tab-documents">Belge Kuyruğu</TabsTrigger>
                            <TabsTrigger value="conversations" data-testid="wa-tab-conversations">Konuşmalar</TabsTrigger>
                            <TabsTrigger value="settings" data-testid="wa-tab-settings">Bot Ayarları</TabsTrigger>
                            <TabsTrigger value="simulator" data-testid="wa-tab-simulator">Simülatör</TabsTrigger>
                            <TabsTrigger value="notify" data-testid="wa-tab-notify">Sonuç Bildirimi</TabsTrigger>
                        </TabsList>

                        <TabsContent value="documents">
                            <WaDocumentQueue />
                        </TabsContent>
                        <TabsContent value="conversations">
                            <WaConversations />
                        </TabsContent>
                        <TabsContent value="settings">
                            <WaBotSettings config={config} onSaved={setConfig} />
                        </TabsContent>
                        <TabsContent value="simulator">
                            <WaSimulator />
                        </TabsContent>
                        <TabsContent value="notify">
                            <WaManualNotify />
                        </TabsContent>
                    </Tabs>
                </>
            )}
        </AdminLayout>
    );
}
