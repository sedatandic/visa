import React from "react";
import { Facebook, Instagram, Linkedin, Twitter, Youtube, Star } from "lucide-react";

const GoogleGlyph = ({ className }) => (
    <svg className={className} viewBox="0 0 48 48" aria-hidden="true">
        <path
            fill="#4285F4"
            d="M45.1 24.5c0-1.6-.1-2.8-.4-4H24v7.6h11.9c-.2 2-1.5 5-4.4 7l6.7 5.2c4-3.7 6.9-9.1 6.9-15.8z"
        />
        <path
            fill="#34A853"
            d="M24 46c5.9 0 10.9-1.9 14.2-5.3l-6.7-5.2c-1.8 1.3-4.3 2.2-7.5 2.2-5.9 0-10.9-3.9-12.7-9.3l-7 5.4C7.7 41.1 15.2 46 24 46z"
        />
        <path
            fill="#FBBC05"
            d="M11.3 28.4c-.5-1.4-.7-2.9-.7-4.4s.3-3 .7-4.4l-7-5.4C3.5 17 2.6 20.4 2.6 24s.9 7 2.7 9.8l6-5.4z"
        />
        <path
            fill="#EA4335"
            d="M24 10.3c4.2 0 7 1.8 8.6 3.3l6.1-6C34.9 4.1 29.9 2 24 2 15.2 2 7.7 6.9 4.3 14.2l7 5.4C13.1 14.2 18.1 10.3 24 10.3z"
        />
    </svg>
);

const TikTokGlyph = ({ className }) => (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M16.6 5.82A4.28 4.28 0 0 1 15.54 3h-3.1v12.4a2.59 2.59 0 1 1-1.84-2.48V9.75a5.72 5.72 0 1 0 4.94 5.66V8.9a7.3 7.3 0 0 0 4.06 1.24V7.05a4.3 4.3 0 0 1-3-1.23z" />
    </svg>
);

const ThreadsGlyph = ({ className }) => (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M12.2 22h-.06c-3.1-.02-5.48-1.05-7.08-3.05C3.63 17.17 2.9 14.7 2.87 12v-.02c.03-2.7.76-5.17 2.19-6.95C6.66 3.03 9.04 2 12.14 2h.06c2.38.02 4.35.63 5.86 1.83 1.42 1.13 2.42 2.74 2.97 4.79l-1.94.53c-.93-3.4-3.28-5.13-6.9-5.15h-.05c-2.5 0-4.36.78-5.55 2.32C5.47 7.75 4.9 9.7 4.87 12c.03 2.3.6 4.25 1.72 5.68 1.19 1.54 3.05 2.32 5.55 2.32h.05c2.25-.02 3.75-.55 5-1.77 1.42-1.4 1.4-3.11 .95-4.15-.27-.62-.75-1.13-1.4-1.52-.16 1.16-.53 2.1-1.1 2.8-.77.94-1.87 1.45-3.27 1.51-1.06.06-2.08-.19-2.87-.71-.94-.62-1.49-1.57-1.55-2.68-.06-1.08.37-2.07 1.2-2.79.8-.68 1.92-1.08 3.25-1.15.98-.05 1.9 0 2.74.13-.11-.68-.34-1.22-.68-1.6-.47-.53-1.2-.8-2.16-.81h-.03c-.78 0-1.83.21-2.5 1.2l-1.65-1.1c.9-1.33 2.37-2.07 4.15-2.07h.04c1.53.01 2.74.5 3.6 1.45.78.87 1.22 2.1 1.31 3.67.06.02.12.05.18.08 1.34.63 2.32 1.58 2.84 2.76.72 1.63.79 4.3-1.38 6.44C17.4 21.28 15.3 22 12.2 22zm.6-9.94c-.24 0-.48 0-.73.02-1.67.09-2.7.86-2.64 1.95.06 1.14 1.32 1.67 2.53 1.6 1.11-.05 2.56-.49 2.8-3.38-.62-.13-1.28-.19-1.96-.19z" />
    </svg>
);

const ICONS = {
    instagram: Instagram,
    google_review: GoogleGlyph,
    facebook: Facebook,
    tiktok: TikTokGlyph,
    youtube: Youtube,
    x: Twitter,
    linkedin: Linkedin,
    threads: ThreadsGlyph,
};

/** Platform kimligine gore sosyal medya ikonu. */
export const SocialIcon = ({ platform, className = "h-5 w-5" }) => {
    const Glyph = ICONS[platform] || Star;
    return <Glyph className={className} />;
};

/** Sitede kullanilan platform bazli renk/arka plan aksanlari. */
export const SOCIAL_ACCENT = {
    instagram: {
        background: "linear-gradient(135deg, #F58529 0%, #DD2A7B 55%, #8134AF 100%)",
        borderColor: "transparent",
        color: "#fff",
    },
    facebook: { backgroundColor: "#1877F2", borderColor: "transparent", color: "#fff" },
    tiktok: { backgroundColor: "#010101", borderColor: "transparent", color: "#fff" },
    youtube: { backgroundColor: "#FF0000", borderColor: "transparent", color: "#fff" },
    x: { backgroundColor: "#111111", borderColor: "transparent", color: "#fff" },
    linkedin: { backgroundColor: "#0A66C2", borderColor: "transparent", color: "#fff" },
    threads: { backgroundColor: "#101010", borderColor: "transparent", color: "#fff" },
};
