import React from "react";
import { AlertTriangle, BadgeCheck, Plane, ShieldAlert } from "lucide-react";

const POINTS = [
    {
        icon: BadgeCheck,
        title: "Karar mercii G.D.R.F.A'dır",
        detail:
            "Vize başvurularının değerlendirilmesi ve onayı, Birleşik Arap Emirlikleri Göçmenlik İdaresi (G.D.R.F.A) yetkisindedir. İdare ek belge talep ederse ya da ek kontrol yaparsa sonuçlanma süresi öngörülenden uzun sürebilir.",
    },
    {
        icon: ShieldAlert,
        title: "Turistik vizeyle oturum işlemi yapılamaz",
        detail:
            "Amacınız oturum, çalışma veya öğrenim ise turistik, ticari ya da ziyaret vizesiyle giriş yapıp bu işlemleri başlatamazsınız. Böyle bir girişim vizenin iptaline ve sınır dışı kararına yol açar.",
    },
    {
        icon: Plane,
        title: "Oturum vizesinde işlem havaalanında başlar",
        detail:
            "Oturum, çalışma veya öğrenim vizesiyle gelen kişilerin resmî işlemlerini giriş anında havaalanında başlatması zorunludur. Başlatılmadığı takdirde vize geçersiz sayılır ve aynı yaptırım uygulanır.",
    },
];

export const ImportantNotice = ({ compact = false }) => (
    <section
        className={compact ? "" : "section"}
        aria-labelledby="important-notice-title"
        data-testid="important-notice"
    >
        <div className={compact ? "" : "container-page"}>
            <div className="overflow-hidden rounded-[var(--radius-lg)] border border-[hsl(var(--warning))]/35 bg-[hsl(var(--warning))]/[0.07]">
                <div className="flex items-start gap-3 border-b border-[hsl(var(--warning))]/25 px-5 py-4 sm:px-7">
                    <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[hsl(var(--warning))]/20">
                        <AlertTriangle className="h-4.5 w-4.5 text-[hsl(var(--warning))]" aria-hidden="true" />
                    </span>
                    <div>
                        <h2
                            id="important-notice-title"
                            className="font-heading text-base font-extrabold sm:text-lg"
                            data-testid="important-notice-title"
                        >
                            Başvurmadan önce okumanız gerekenler
                        </h2>
                        <p className="mt-1 text-sm text-muted-foreground">
                            Yanlış vize türü seçimi, girişte geri çevrilmeye kadar giden sonuçlar doğurabilir.
                        </p>
                    </div>
                </div>

                <ul className="divide-y divide-[hsl(var(--warning))]/15">
                    {POINTS.map((point) => (
                        <li
                            key={point.title}
                            className="flex items-start gap-3 px-5 py-4 sm:gap-4 sm:px-7"
                            data-testid={`important-notice-item-${POINTS.indexOf(point)}`}
                        >
                            <point.icon
                                className="mt-0.5 h-4.5 w-4.5 shrink-0 text-[hsl(var(--warning))]"
                                aria-hidden="true"
                            />
                            <div>
                                <p className="text-sm font-bold">{point.title}</p>
                                <p className="mt-1 text-sm leading-6 text-muted-foreground">{point.detail}</p>
                            </div>
                        </li>
                    ))}
                </ul>

                <p className="border-t border-[hsl(var(--warning))]/25 px-5 py-4 text-sm font-semibold sm:px-7">
                    Seyahat amacınızla birebir örtüşen vize türünü seçtiğinizden emin olun; kararsız kaldığınızda
                    başvuruyu göndermeden önce bize yazın, doğru türü birlikte belirleyelim.
                </p>
            </div>
        </div>
    </section>
);
