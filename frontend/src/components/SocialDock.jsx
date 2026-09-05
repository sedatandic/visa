import React from "react";
import { Instagram, Star } from "lucide-react";
import { useContact, waLink } from "../lib/contact";
import { WhatsAppIcon } from "./WhatsAppIcon";


const GoogleIcon = () => (
    <svg width="22" height="22" viewBox="0 0 48 48" aria-hidden="true">
        <path
            fill="#4285F4"
            d="M45.1 24.5c0-1.6-.1-2.8-.4-4H24v7.6h11.9c-.2 2-1.5 5-4.4 7l6.7 5.2c4-3.7 6.9-9.1 6.9-15.8z"
        />
        <path
            fill="#34A853"
            d="M24 46c5.9 0 10.9-1.9 14.2-5.3l-6.7-5.2c-1.8 1.3-4.3 2.2-7.5 2.2-5.9 0-10.9-3.9-12.7-9.3l-7 5.4C7.7 41.1 15.2 46 24 46z"
        />
        <path fill="#FBBC05" d="M11.3 28.4c-.5-1.4-.7-2.9-.7-4.4s.3-3 .7-4.4l-7-5.4C3.5 17 2.6 20.4 2.6 24s.9 7 2.7 9.8l6-5.4z" />
        <path
            fill="#EA4335"
            d="M24 10.3c4.2 0 7 1.8 8.6 3.3l6.1-6C34.9 4.1 29.9 2 24 2 15.2 2 7.7 6.9 4.3 14.2l7 5.4C13.1 14.2 18.1 10.3 24 10.3z"
        />
    </svg>
);

const ACTION_CLASS =
    "flex h-12 w-12 items-center justify-center rounded-full border border-border bg-card text-foreground transition-transform duration-150 hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 sm:h-13 sm:w-13";

/** Sag altta sabit sosyal iletisim rafi: WhatsApp, Instagram, Google yorumlari. */
export const SocialDock = () => {
    const contact = useContact();

    return (
        <div
            className="fixed bottom-4 right-4 z-50 flex flex-col items-end gap-2.5 sm:bottom-5 sm:right-5"
            data-testid="social-dock"
        >
            {contact.googleReview && (
                <a
                    href={contact.googleReview}
                    target="_blank"
                    rel="noreferrer"
                    aria-label="Google yorumlarımızı okuyun"
                    title="Google yorumları"
                    data-testid="google-review-button"
                    className={`hidden sm:flex ${ACTION_CLASS}`}
                    style={{ boxShadow: "var(--shadow-card)" }}
                >
                    <span className="relative flex items-center justify-center">
                        <GoogleIcon />
                        <Star
                            className="absolute -right-2 -top-2 h-3.5 w-3.5 fill-[hsl(var(--gold))] text-[hsl(var(--gold))]"
                            aria-hidden="true"
                        />
                    </span>
                </a>
            )}

            {contact.instagram && (
                <a
                    href={contact.instagram}
                    target="_blank"
                    rel="noreferrer"
                    aria-label="Instagram sayfamız"
                    title="Instagram"
                    data-testid="instagram-button"
                    className={`hidden sm:flex ${ACTION_CLASS}`}
                    style={{
                        boxShadow: "var(--shadow-card)",
                        background: "linear-gradient(135deg, #F58529 0%, #DD2A7B 55%, #8134AF 100%)",
                        borderColor: "transparent",
                        color: "#fff",
                    }}
                >
                    <Instagram className="h-6 w-6" />
                </a>
            )}

            {contact.whatsapp && (
                <a
                    href={waLink(contact, "Merhaba, Dubai vizesi hakkında bilgi almak istiyorum.")}
                    target="_blank"
                    rel="noreferrer"
                    aria-label="WhatsApp ile yazın"
                    data-testid="whatsapp-floating-button"
                    className="flex h-12 items-center gap-2 rounded-full px-3.5 text-white transition-transform duration-150 hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 sm:h-14 sm:px-4"
                    style={{ backgroundColor: "#25D366", boxShadow: "var(--shadow-float)" }}
                >
                    <WhatsAppIcon />
                    <span className="hidden text-sm font-bold sm:inline">WhatsApp</span>
                </a>
            )}
        </div>
    );
};
