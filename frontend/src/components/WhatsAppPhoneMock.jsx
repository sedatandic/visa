import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Camera, ChevronLeft, Link2, Mic, MoreVertical, Phone, Plus, Smile, Video } from "lucide-react";

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
        id: "apply",
        label: "WhatsApp'tan başvuru",
        clock: "09:41",
        messages: [
            { from: "out", time: "09:40", text: "Form doldurmak istemiyorum, buradan başvurabilir miyim?" },
            { from: "in", time: "09:40", text: "Elbette. Pasaportunuzun kimlik sayfası ve bir vesikalık yeterli." },
            { from: "out", time: "09:41", text: "Pasaportum 7 ay sonra doluyor, sorun olur mu?" },
            { from: "in", time: "09:41", text: "Olmaz. Dönüş tarihinizden itibaren 6 ay geçerlilik tek teknik şart." },
            { from: "out", time: "09:42", image: "/chat/passport-bio.jpg", text: "Pasaport kimlik sayfam" },
            { from: "in", time: "09:42", text: "Net geldi, başvurunuzu ben oluşturuyorum." },
            { from: "in", time: "09:43", text: "Ödeme linkiniz ve takip kodunuz birazdan burada olacak." },
            { from: "out", time: "09:43", text: "Çok kolay oldu, teşekkürler" },
        ],
    },
    {
        id: "green",
        label: "Yeşil pasaport",
        clock: "11:05",
        messages: [
            { from: "out", time: "11:03", text: "Yeşil pasaportum var, Dubai için vize almam gerekiyor mu?" },
            { from: "in", time: "11:03", text: "Hususi (yeşil) pasaportla yılda 90 güne kadar vizesiz giriş yapabilirsiniz." },
            { from: "out", time: "11:04", text: "Eşimin bordo pasaportu var, o ne yapacak?" },
            { from: "in", time: "11:04", text: "Umuma mahsus bordo pasaportta vize zorunlu; eşiniz için başvuru açalım." },
            { from: "out", time: "11:04", text: "30 gün yeter bize" },
            { from: "in", time: "11:05", text: "30 gün tek girişli vize uygun. Pasaport sayfası ve vesikalık yeterli." },
            { from: "out", time: "11:05", text: "Hemen gönderiyorum" },
            { from: "in", time: "11:06", text: "Bekliyorum; dosyayı bugün resmî sisteme iletiyoruz." },
        ],
    },
    {
        id: "extras",
        label: "eSIM ve seyahat sigortası",
        clock: "16:34",
        messages: [
            { from: "out", time: "16:31", text: "Dubai'de internet için hat mı almam gerekiyor?" },
            { from: "in", time: "16:31", text: "Gerek yok. Dubai eSIM'imizde QR kodu okutuyorsunuz, iner inmez internetiniz açık." },
            { from: "in", time: "16:32", text: "Türkiye numaranız da açık kalır; WhatsApp aynı numaradan çalışmaya devam eder." },
            { from: "out", time: "16:32", text: "Seyahat sigortası da zorunlu mu?" },
            { from: "in", time: "16:33", text: "BAE vizesi için zorunlu değil ama sağlık masrafları için öneriyoruz; 30 günlük poliçe 644 ₺." },
            { from: "out", time: "16:33", text: "İkisini birlikte alabilir miyim?" },
            {
                from: "in",
                time: "16:34",
                link: { title: "Vize + eSIM + Sigorta paketi", sub: "%10 paket indirimi · tek ödeme", url: "dubaivizehatti.com/paketler" },
                text: "Evet, vizeyle birlikte alırsanız ikisinde %10 paket indirimi uygulanır.",
            },
            { from: "out", time: "16:35", text: "Paketi seçtim, ödemeye geçiyorum" },
        ],
    },
    {
        id: "family",
        label: "Aile ve çocuklar",
        clock: "15:48",
        messages: [
            { from: "out", time: "15:45", text: "Eşim ve 2 çocukla gideceğiz, tek başvuru olur mu?" },
            { from: "in", time: "15:45", text: "Olur. Dört yolcuyu aynı başvuruya ekliyoruz, %15 aile indirimi düşüyor." },
            { from: "in", time: "15:46", text: "18 yaş altı yolcular indirimli çocuk vizesiyle işlenir." },
            { from: "out", time: "15:46", text: "Küçük kızımın soyadı benden farklı, ek belge ister mi?" },
            { from: "in", time: "15:47", text: "Evet: velinin önlü arkalı kimlik fotoğrafı ve e-Devlet'ten Formül A doğum belgesi." },
            { from: "out", time: "15:47", text: "Çocuklar tek başına başvurabilir mi?" },
            { from: "in", time: "15:48", text: "Hayır, 18 yaş altı mutlaka anne veya babayla başvurup seyahat etmeli." },
            { from: "out", time: "15:48", text: "Anlaşıldı, belgeleri topluyorum" },
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
                        className="mb-1.5 block w-full rounded-md border border-black/5 bg-white object-contain"
                        loading="lazy"
                        data-testid="wa-bubble-passport-image"
                    />
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
            className="relative mx-auto w-full max-w-[244px] sm:max-w-[300px]"
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
                        <Video className="hidden h-5 w-5 shrink-0 text-white/85 sm:block" aria-hidden="true" />
                        <Phone className="hidden h-4 w-4 shrink-0 text-white/85 min-[380px]:block" aria-hidden="true" />
                        <MoreVertical className="h-4 w-4 shrink-0 text-white/85" aria-hidden="true" />
                    </div>

                    {/* sohbet alani */}
                    <div
                        className="flex h-[498px] flex-col justify-end overflow-hidden px-3 py-2.5 sm:h-[452px]"
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
                            <span className="flex-1 truncate whitespace-nowrap text-[12px] text-[#8696A0]">Mesaj yazın</span>
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
