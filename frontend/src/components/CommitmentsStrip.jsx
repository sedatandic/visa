import React from "react";
import { Clock3, Languages, MapPin, Tag, Trash2, Zap } from "lucide-react";
import { useContact } from "../lib/contact";

const HIGHLIGHTS = [
    {
        icon: Trash2,
        title: "Belgelerinizin içeriği 90 gün sonra imha ediliyor",
        text: "Pasaport görselleriniz şifreli saklanır; saklama süresi dolduğunda içerik geri getirilemeyecek şekilde silinir.",
    },
    {
        icon: Zap,
        title: "Ekspres öncelik · aynı gün",
        text: "Seyahatine az kalanlar için öncelikli işlem sırası; anında ekspreste sonuç aynı gün çıkar.",
    },
    {
        icon: Tag,
        title: "Fiyat başvuru anında sabitlenir",
        text: "TL tutarınız başvuruyu oluşturduğunuz anki kurla kilitlenir; kur oynasa bile değişmez.",
    },
];

/** "Sozumuzun karsiligi": somut taahhutler tek bakista. */
export const CommitmentsStrip = () => {
    const contact = useContact();
    const rows = [
        { icon: MapPin, label: "Ofis", value: contact?.address ? "İstanbul · Zeytinburnu" : "İstanbul" },
        { icon: Tag, label: "Başvuru takibi", value: "Her başvuruya referans kodu" },
        { icon: Trash2, label: "Belge saklama", value: "90 gün, sonra içerik imha edilir" },
        { icon: Clock3, label: "Çalışma saatleri", value: contact?.workingHours || "Hafta içi 09:00 - 19:00" },
        { icon: Languages, label: "Destek dili", value: "Türkçe · İngilizce" },
    ];

    return (
        <section className="section" data-testid="landing-commitments">
            <div className="container-page grid gap-10 lg:grid-cols-[0.85fr_1fr] lg:items-start">
                <div>
                    <span className="eyebrow">Sözümüzün karşılığı</span>
                    <h2 className="mt-3 text-2xl font-bold sm:text-3xl">Neyi taahhüt ediyorsak yazılı</h2>
                    <p className="mt-3 text-sm leading-6 text-muted-foreground">
                        Vize sürecinde en çok merak edilen konular: belgelerimize ne oluyor, süreç ne kadar
                        sürüyor, kime ulaşacağım. Hepsinin cevabı burada.
                    </p>
                    <dl className="mt-7 divide-y divide-border rounded-2xl border border-border bg-card">
                        {rows.map(({ icon: Icon, label, value }) => (
                            <div
                                key={label}
                                className="flex flex-wrap items-center justify-between gap-2 px-5 py-4"
                                data-testid={`commitment-row-${label.toLowerCase().replace(/\s+/g, "-")}`}
                            >
                                <dt className="inline-flex items-center gap-2 text-sm text-muted-foreground">
                                    <Icon className="h-4 w-4 text-primary" aria-hidden="true" />
                                    {label}
                                </dt>
                                <dd className="text-sm font-semibold text-foreground">{value}</dd>
                            </div>
                        ))}
                    </dl>
                </div>

                <div className="grid gap-4">
                    {HIGHLIGHTS.map(({ icon: Icon, title, text }) => (
                        <div
                            key={title}
                            className="card-surface flex items-start gap-4 p-6"
                            data-testid="commitment-highlight"
                        >
                            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/10">
                                <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
                            </span>
                            <div className="min-w-0">
                                <h3 className="font-heading text-base font-bold">{title}</h3>
                                <p className="mt-1.5 text-sm leading-6 text-muted-foreground">{text}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};
