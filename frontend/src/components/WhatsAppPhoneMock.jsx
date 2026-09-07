import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Camera, ChevronLeft, FileText, Link2, Mic, MoreVertical, Phone, Plus, Smile, Video } from "lucide-react";

const ROTATE_MS = 6800;

const TICK = (
    <svg viewBox="0 0 18 12" className="ml-1 inline-block h-3 w-4 align-middle" aria-hidden="true">
        <path
            d="M1.2 6.6 3.9 9.3 9.6 3.6"
            fill="none"
            stroke="#53BDEB"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
        />
        <path
            d="M7.4 6.6 10.1 9.3 15.8 3.6"
            fill="none"
            stroke="#53BDEB"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
        />
    </svg>
);

const SCENARIOS = [
    {
        id: "passport",
        label: "Pasaport süresi",
        clock: "09:41",
        messages: [
            { from: "out", time: "09:41", text: "Pasaportum 7 ay sonra doluyor, vize alabilir miyim?" },
            { from: "in", time: "09:41", text: "Alabilirsiniz. Dönüşünüzden itibaren 6 ay geçerlilik yeterli." },
            { from: "out", time: "09:42", image: "/chat/passport-tr.jpg", text: "Pasaport sayfam" },
            { from: "in", time: "09:42", text: "Net geldi, formu ben doldururum. Kaç kişisiniz?" },
            { from: "out", time: "09:43", text: "2 yetişkin 1 çocuk" },
            { from: "in", time: "09:43", text: "3 yolcudan itibaren aile indirimi otomatik düşüyor." },
        ],
    },
    {
        id: "express",
        label: "Yarın uçuşum var",
        clock: "22:07",
        messages: [
            { from: "out", time: "22:06", text: "Yarın 21:00 uçuşum var, vize yetişir mi?" },
            { from: "in", time: "22:06", text: "Anında ekspres ile aynı gün içinde sonuçlanıyor, rahat yetişir." },
            { from: "out", time: "22:07", text: "Ne göndermem gerekiyor?" },
            { from: "in", time: "22:07", text: "Pasaport kimlik sayfası ve bir vesikalık. Başvuruyu ben açıyorum." },
            { from: "out", time: "22:08", text: "Harika, başlıyoruz" },
        ],
    },
    {
        id: "ticket",
        label: "Bilet & otel şartı",
        clock: "14:12",
        messages: [
            { from: "out", time: "14:11", text: "Vize için uçak bileti ve otel istiyorlar mı?" },
            { from: "in", time: "14:11", text: "İstemiyorlar. Pasaport sayfanız ve vesikalığınız yeterli." },
            { from: "out", time: "14:12", text: "Bileti vize çıkınca alsam olur mu?" },
            {
                from: "in",
                time: "14:13",
                link: { title: "Ödeme linkiniz hazır", sub: "30 gün tek giriş · 2 yolcu", url: "dubaivizehatti.com/odeme" },
                text: "Olur. Fiyatı kilitledim, linkten devam edin.",
            },
            { from: "out", time: "14:15", text: "Ödemeyi yaptım, teşekkürler" },
        ],
    },
    {
        id: "delivery",
        label: "Vize teslimi",
        clock: "11:18",
        messages: [
            { from: "out", time: "11:17", text: "DV-8421 başvurumun vizesi çıktı mı?" },
            { from: "in", time: "11:18", text: "Onaylandı! PDF'i gönderiyorum, telefondan göstermeniz yeterli." },
            {
                from: "in",
                time: "11:18",
                doc: { name: "Vize_Onay_DV-8421.pdf", size: "212 KB · 1 sayfa" },
                text: "Yazdırmanıza gerek yok.",
            },
            { from: "in", time: "11:20", text: "İsterseniz eSIM ve sigortayı da ekleyeyim, ikisi sepette indirimli." },
            { from: "out", time: "11:21", text: "eSIM'i ekleyelim" },
        ],
    },
];

const Bubble = ({ m, i }) => {
    const out = m.from === "out";
    return (
        <motion.div
            initial={{ opacity: 0, y: 12, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.3, delay: Math.min(i * 0.11, 0.7), ease: [0.22, 1, 0.36, 1] }}
            className={`flex ${out ? "justify-end" : "justify-start"}`}
            data-testid={`wa-bubble-${i}`}
        >
            <div
                className={`relative max-w-[85%] rounded-lg px-2.5 py-1.5 text-[13px] leading-[18px] text-[#111B21] shadow-[0_1px_0.5px_rgba(11,20,26,0.13)] ${
                    out ? "bg-[#D9FDD3]" : "bg-white"
                }`}
            >
                <span
                    className={`absolute top-0 h-3 w-3 ${out ? "-right-1.5" : "-left-1.5"}`}
                    style={{
                        background: out ? "#D9FDD3" : "#FFFFFF",
                        clipPath: out ? "polygon(0 0, 100% 0, 0 100%)" : "polygon(0 0, 100% 0, 100% 100%)",
                    }}
                    aria-hidden="true"
                />
                {m.image && (
                    <img
                        src={m.image}
                        alt="Sohbette paylaşılan pasaport kimlik sayfası (bilgiler bulanıklaştırıldı)"
                        className="mb-1.5 h-[100px] w-full rounded-md object-cover object-center"
                        loading="lazy"
                        data-testid="wa-bubble-passport-image"
                    />
                )}
                {m.doc && (
                    <span className="mb-1.5 flex items-center gap-2.5 rounded-md bg-black/[0.045] px-2 py-2">
                        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#E11B22]/10">
                            <FileText className="h-5 w-5 text-[#E11B22]" aria-hidden="true" />
                        </span>
                        <span className="min-w-0">
                            <span className="block truncate text-[12px] font-semibold">{m.doc.name}</span>
                            <span className="block text-[11px] text-[#667781]">{m.doc.size}</span>
                        </span>
                    </span>
                )}
                {m.link && (
                    <span className="mb-1.5 block rounded-md bg-black/[0.045] px-2.5 py-2">
                        <span className="flex items-center gap-1.5 text-[11px] font-semibold text-[#027EB5]">
                            <Link2 className="h-3.5 w-3.5" aria-hidden="true" />
                            {m.link.url}
                        </span>
                        <span className="mt-1 block text-[12px] font-semibold">{m.link.title}</span>
                        <span className="block text-[11px] text-[#667781]">{m.link.sub}</span>
                    </span>
                )}
                {m.text}
                <span className="ml-2 inline-block whitespace-nowrap align-bottom text-[10px] text-[#667781]">
                    {m.time}
                    {out && TICK}
                </span>
            </div>
        </motion.div>
    );
};

/** Telefon icinde donen 4 gercekci WhatsApp sohbeti. */
export const WhatsAppPhoneMock = ({ href }) => {
    const [index, setIndex] = useState(() => Math.floor(Math.random() * SCENARIOS.length));
    const paused = useRef(false);

    useEffect(() => {
        const timer = setInterval(() => {
            if (!paused.current) setIndex((i) => (i + 1) % SCENARIOS.length);
        }, ROTATE_MS);
        return () => clearInterval(timer);
    }, []);

    const scenario = SCENARIOS[index];

    return (
        <div
            className="relative mx-auto w-full max-w-[304px]"
            data-testid="wa-phone-mock"
            onMouseEnter={() => {
                paused.current = true;
            }}
            onMouseLeave={() => {
                paused.current = false;
            }}
        >
            <div
                className="pointer-events-none absolute -inset-6 -z-10 rounded-[3rem] opacity-70 blur-2xl"
                style={{ background: "radial-gradient(60% 50% at 50% 30%, hsl(var(--gold)/0.28), transparent 70%)" }}
                aria-hidden="true"
            />
            <motion.div
                initial={{ rotate: 6 }}
                whileHover={{ rotate: 0, scale: 1.015 }}
                transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                className="origin-bottom rounded-[2.4rem] border-[9px] border-[#0B1B2B] bg-[#0B1B2B] shadow-[0_34px_70px_-26px_rgba(11,27,43,0.7)]"
            >
                <div className="overflow-hidden rounded-[1.85rem] bg-[#EFEAE2]">
                    {/* durum cubugu */}
                    <div className="flex items-center justify-between bg-[#075E54] px-5 pb-1 pt-2 text-[10px] font-semibold text-white/90">
                        <span data-testid="wa-phone-clock">{scenario.clock}</span>
                        <span className="flex items-center gap-1">
                            <span className="flex items-end gap-[2px]" aria-hidden="true">
                                <i className="block h-1 w-[3px] rounded-sm bg-white/80" />
                                <i className="block h-1.5 w-[3px] rounded-sm bg-white/80" />
                                <i className="block h-2 w-[3px] rounded-sm bg-white/80" />
                                <i className="block h-2.5 w-[3px] rounded-sm bg-white/40" />
                            </span>
                            <span className="ml-1 rounded-sm border border-white/60 px-1 text-[8px] leading-3">86</span>
                        </span>
                    </div>

                    {/* sohbet basligi */}
                    <div className="flex items-center gap-2.5 bg-[#075E54] px-3 pb-2.5 pt-1">
                        <ChevronLeft className="h-5 w-5 shrink-0 text-white/90" aria-hidden="true" />
                        <img
                            src="/brand/emblem-512.png"
                            alt=""
                            className="h-9 w-9 shrink-0 rounded-full bg-white object-contain p-0.5"
                        />
                        <div className="min-w-0 flex-1">
                            <p className="truncate text-[13px] font-semibold text-white">Dubai Vize Hattı</p>
                            <p className="text-[11px] text-white/70">çevrimiçi</p>
                        </div>
                        <Video className="h-5 w-5 shrink-0 text-white/85" aria-hidden="true" />
                        <Phone className="h-4 w-4 shrink-0 text-white/85" aria-hidden="true" />
                        <MoreVertical className="h-4 w-4 shrink-0 text-white/85" aria-hidden="true" />
                    </div>

                    {/* sohbet alani */}
                    <div
                        className="min-h-[330px] px-3 py-2.5"
                        style={{
                            backgroundColor: "#EFEAE2",
                            backgroundImage:
                                "radial-gradient(circle at 20% 15%, rgba(0,0,0,0.035) 0 2px, transparent 3px), radial-gradient(circle at 70% 55%, rgba(0,0,0,0.03) 0 2px, transparent 3px), radial-gradient(circle at 45% 85%, rgba(0,0,0,0.03) 0 2px, transparent 3px)",
                            backgroundSize: "120px 120px",
                        }}
                    >
                        <div className="mb-2 flex justify-center">
                            <span className="rounded-md bg-[#FFF5C4] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide text-[#54656F] shadow-sm">
                                Bugün
                            </span>
                        </div>
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={scenario.id}
                                initial={{ opacity: 0, x: 18 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -18 }}
                                transition={{ duration: 0.28, ease: "easeOut" }}
                                className="space-y-2"
                                data-testid={`wa-chat-${scenario.id}`}
                            >
                                {scenario.messages.map((m, i) => (
                                    <Bubble key={i} m={m} i={i} />
                                ))}
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* mesaj yazma alani */}
                    <div className="flex items-center gap-2 bg-[#F0F2F5] px-2.5 py-2">
                        <div className="flex flex-1 items-center gap-2 rounded-full bg-white px-3 py-2">
                            <Smile className="h-5 w-5 shrink-0 text-[#8696A0]" aria-hidden="true" />
                            <span className="flex-1 text-[12px] text-[#8696A0]">Mesaj yazın</span>
                            <Plus className="h-4 w-4 shrink-0 text-[#8696A0]" aria-hidden="true" />
                            <Camera className="h-4 w-4 shrink-0 text-[#8696A0]" aria-hidden="true" />
                        </div>
                        <a
                            href={href || undefined}
                            target="_blank"
                            rel="noreferrer"
                            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#00A884] transition-transform hover:scale-105"
                            aria-label="WhatsApp'tan yazın"
                            data-testid="wa-phone-mic-button"
                        >
                            <Mic className="h-5 w-5 text-white" aria-hidden="true" />
                        </a>
                    </div>
                </div>
            </motion.div>

            <div className="mt-8 flex items-center justify-center gap-2" data-testid="wa-chat-dots">
                {SCENARIOS.map((s, i) => (
                    <button
                        key={s.id}
                        type="button"
                        onClick={() => setIndex(i)}
                        aria-label={`${s.label} sohbetini göster`}
                        aria-current={i === index}
                        data-testid={`wa-chat-dot-${i}`}
                        className={`h-2.5 rounded-full transition-all duration-300 ${
                            i === index ? "w-7 bg-primary" : "w-2.5 bg-foreground/20 hover:bg-foreground/40"
                        }`}
                    />
                ))}
            </div>
            <p className="mt-3 text-center text-xs leading-5 text-muted-foreground">
                <strong className="font-semibold text-foreground/80" data-testid="wa-chat-label">
                    {scenario.label}
                </strong>{" "}
                · Gerçek görüşmelerden uyarlandı; isim, numara ve pasaport bilgileri gizlendi.
            </p>
        </div>
    );
};
