import React, { useEffect } from "react";
import { setMeta } from "../lib/site";
import { PageHeader } from "../components/SiteLayout";

export default function Kvkk() {
    useEffect(() => {
        setMeta(
            "KVKK ve Gizlilik Politikası | Dubai Vize Online",
            "Kişisel verilerinizin işlenmesi, saklanması ve korunmasına ilişkin aydınlatma metni ve gizlilik politikası."
        );
    }, []);

    return (
        <div data-testid="kvkk-page">
            <PageHeader
                eyebrow="Yasal"
                title="KVKK Aydınlatma Metni ve Gizlilik Politikası"
                description="Başvuru sırasında paylaştığınız bilgilerin nasıl kullanıldığını şeffaf biçimde açıklıyoruz."
            />
            <section className="section">
                <div className="container-page max-w-3xl space-y-8 text-sm leading-7 text-muted-foreground">
                    <div>
                        <h2 className="font-heading text-lg font-bold text-foreground">1. Hangi verileri topluyoruz?</h2>
                        <p className="mt-2">
                            Adınız, soyadınız, doğum tarihiniz, pasaport bilgileriniz, iletişim bilgileriniz,
                            seyahat tarihleri ve yüklediğiniz belgeler (pasaport taraması ve biyometrik
                            fotoğraf). Bu veriler yalnızca vize başvurunuzun hazırlanması ve takibi için
                            kullanılır.
                        </p>
                    </div>
                    <div>
                        <h2 className="font-heading text-lg font-bold text-foreground">2. Verilerinizi kimlerle paylaşıyoruz?</h2>
                        <p className="mt-2">
                            Başvurunuzun işleme alınabilmesi için yetkili merciler ve başvuru aracılık
                            platformlarıyla paylaşılır. Reklam veya pazarlama amacıyla üçüncü taraflara
                            veri satmayız.
                        </p>
                    </div>
                    <div>
                        <h2 className="font-heading text-lg font-bold text-foreground">3. Ödeme bilgileri</h2>
                        <p className="mt-2">
                            Kart bilgileriniz sunucularımıza hiçbir şekilde kaydedilmez. Ödeme işlemi
                            uluslararası ödeme kuruluşunun güvenli sayfasında gerçekleşir; tarafımıza
                            yalnızca işlem sonucunu gösteren referans bilgisi iletilir.
                        </p>
                    </div>
                    <div>
                        <h2 className="font-heading text-lg font-bold text-foreground">4. Saklama süresi</h2>
                        <p className="mt-2">
                            Başvuru kayıtları yasal yükümlülüklerimiz süresince saklanır, ardından
                            silinir veya anonim hale getirilir.
                        </p>
                    </div>
                    <div>
                        <h2 className="font-heading text-lg font-bold text-foreground">5. Haklarınız</h2>
                        <p className="mt-2">
                            KVKK kapsamında verilerinize erişme, düzeltme, silme ve işlenmesine itiraz
                            etme hakkına sahipsiniz. Taleplerinizi iletişim sayfamızdaki e-posta adresine
                            iletebilirsiniz.
                        </p>
                    </div>
                    <div>
                        <h2 className="font-heading text-lg font-bold text-foreground">6. İade koşulları</h2>
                        <p className="mt-2">
                            Başvurunuz yetkili merciler tarafından reddedilirse, resmî harcın dışında kalan
                            hizmet bedelimiz iade edilir. Başvuru gönderilmeden önce yapılan iptal
                            taleplerinde ödeme tamamen iade edilir.
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
}
