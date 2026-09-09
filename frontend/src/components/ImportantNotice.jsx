import React from "react";
import { AlertTriangle, BadgeCheck, Ban, Plane, ShieldAlert } from "lucide-react";

const POINTS = [
    {
        icon: BadgeCheck,
        title: "Karar mercii G.D.R.F.A'dır",
        brief: "Onay yetkisi BAE Göçmenlik İdaresi'ndedir; ek kontrol süreyi uzatabilir.",
        detail:
            "Vize başvurularının değerlendirilmesi ve onayı, Birleşik Arap Emirlikleri Göçmenlik İdaresi (G.D.R.F.A) yetkisindedir. İdare ek belge talep ederse ya da ek kontrol yaparsa sonuçlanma süresi öngörülenden uzun sürebilir.",
    },
    {
        icon: ShieldAlert,
        title: "Turistik vizeyle oturum açılmaz",
        brief: "Oturum, çalışma veya öğrenim için turistik/ticari vize kullanılamaz.",
        detail:
            "Amacınız oturum, çalışma veya öğrenim ise turistik, ticari ya da ziyaret vizesiyle giriş yapıp bu işlemleri başlatamazsınız. Böyle bir girişim vizenin iptaline ve sınır dışı kararına yol açar.",
    },
    {
        icon: Plane,
        title: "Oturum işlemi havaalanında başlar",
        brief: "Oturum/çalışma vizesinde işlem, girişte havaalanında başlatılmalıdır.",
        detail:
            "Oturum, çalışma veya öğrenim vizesiyle gelen kişilerin resmî işlemlerini giriş anında havaalanında başlatması zorunludur. Başlatılmadığı takdirde vize geçersiz sayılır ve aynı yaptırım uygulanır.",
    },
    {
        icon: Ban,
        title: "Sınır dışı girişi kapatır",
        brief: "Sınır dışı edilen kişiler BAE'ye tekrar giriş yapamaz.",
        detail:
            "Sınır dışı işlemi uygulanan kişilerin Birleşik Arap Emirlikleri'ne tekrar girişine izin verilmez. Bu nedenle vize türü seçimi, sonradan telafi edilemeyen tek adımdır.",
    },
];

const NoticeHeader = ({ tight }) => (
    <div className={`flex items-start gap-3 ${tight ? "" : "border-b border-[hsl(var(--status-warning))]/25 px-5 py-4 sm:px-7"}`}>
        <span
            className={`mt-0.5 flex shrink-0 items-center justify-center rounded-full bg-[hsl(var(--status-warning))]/20 ${
                tight ? "h-8 w-8" : "h-9 w-9"
            }`}
        >
            <AlertTriangle
                className={`text-[hsl(var(--status-warning))] ${tight ? "h-4 w-4" : "h-4.5 w-4.5"}`}
                aria-hidden="true"
            />
        </span>
        <div>
            <h2
                id="important-notice-title"
                className={`font-heading font-extrabold ${tight ? "text-base" : "text-base sm:text-lg"}`}
                data-testid="important-notice-title"
            >
                Başvurmadan önce okumanız gerekenler
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
                {tight
                    ? "Yanlış vize türü seçimi girişte geri çevrilmeye yol açabilir."
                    : "Yanlış vize türü seçimi, girişte geri çevrilmeye kadar giden sonuçlar doğurabilir."}
            </p>
        </div>
    </div>
);

// Sihirbaz ve liste sayfalarinda kullanilan sade surum: 2 satir x 2 kolon, kisa metin.
const CompactNotice = () => (
    <section aria-labelledby="important-notice-title" data-testid="important-notice">
        <div className="rounded-[var(--radius-lg)] border border-[hsl(var(--status-warning))]/35 bg-[hsl(var(--status-warning))]/[0.07] p-5">
            <NoticeHeader tight />
            <ul className="mt-4 grid gap-x-6 gap-y-3.5 sm:grid-cols-2">
                {POINTS.map((point, i) => (
                    <li
                        key={point.title}
                        className="flex items-start gap-2.5"
                        data-testid={`important-notice-item-${i}`}
                    >
                        <point.icon
                            className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--status-warning))]"
                            aria-hidden="true"
                        />
                        <div>
                            <p className="text-sm font-bold leading-5">{point.title}</p>
                            <p className="mt-0.5 text-xs leading-5 text-muted-foreground">{point.brief}</p>
                        </div>
                    </li>
                ))}
            </ul>
            <p className="mt-4 border-t border-[hsl(var(--status-warning))]/25 pt-3.5 text-xs font-semibold leading-5">
                Seyahat amacınıza uygun vize türünü seçin; kararsızsanız göndermeden önce bize yazın.
            </p>
        </div>
    </section>
);

const FullNotice = () => (
    <section className="section" aria-labelledby="important-notice-title" data-testid="important-notice">
        <div className="container-page">
            <div className="overflow-hidden rounded-[var(--radius-lg)] border border-[hsl(var(--status-warning))]/35 bg-[hsl(var(--status-warning))]/[0.07]">
                <NoticeHeader />
                <ul className="divide-y divide-[hsl(var(--status-warning))]/15">
                    {POINTS.map((point, i) => (
                        <li
                            key={point.title}
                            className="flex items-start gap-3 px-5 py-4 sm:gap-4 sm:px-7"
                            data-testid={`important-notice-item-${i}`}
                        >
                            <point.icon
                                className="mt-0.5 h-4.5 w-4.5 shrink-0 text-[hsl(var(--status-warning))]"
                                aria-hidden="true"
                            />
                            <div>
                                <p className="text-sm font-bold">{point.title}</p>
                                <p className="mt-1 text-sm leading-6 text-muted-foreground">{point.detail}</p>
                            </div>
                        </li>
                    ))}
                </ul>
                <p className="border-t border-[hsl(var(--status-warning))]/25 px-5 py-4 text-sm font-semibold sm:px-7">
                    Seyahat amacınızla birebir örtüşen vize türünü seçtiğinizden emin olun; kararsız kaldığınızda
                    başvuruyu göndermeden önce bize yazın, doğru türü birlikte belirleyelim.
                </p>
            </div>
        </div>
    </section>
);

export const ImportantNotice = ({ compact = false }) => (compact ? <CompactNotice /> : <FullNotice />);
