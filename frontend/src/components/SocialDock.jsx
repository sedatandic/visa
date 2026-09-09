import React from "react";
import { Star } from "lucide-react";
import { useContact, waLink } from "../lib/contact";
import { WhatsAppIcon } from "./WhatsAppIcon";
import { SOCIAL_ACCENT, SocialIcon } from "./SocialIcons";

const ACTION_CLASS =
    "flex h-12 w-12 items-center justify-center rounded-full border border-border bg-card text-foreground transition-transform duration-150 hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 sm:h-13 sm:w-13";

/** Sag altta sabit sosyal iletisim rafi: panelde "sag alt buton" secili hesaplar + WhatsApp. */
export const SocialDock = () => {
    const contact = useContact();
    const links = (contact.socialLinks || []).filter((l) => l.in_dock);

    return (
        <div
            className="fixed bottom-4 right-4 z-50 flex flex-col items-end gap-2.5 sm:bottom-5 sm:right-5"
            data-testid="social-dock"
        >
            {links.map((link) => (
                <a
                    key={link.platform}
                    href={link.url}
                    target="_blank"
                    rel="noreferrer"
                    aria-label={`${link.label} sayfamız`}
                    title={link.label}
                    data-testid={`social-dock-${link.platform}`}
                    className={`hidden sm:flex ${ACTION_CLASS}`}
                    style={{ boxShadow: "var(--shadow-card)", ...(SOCIAL_ACCENT[link.platform] || {}) }}
                >
                    <span className="relative flex items-center justify-center">
                        <SocialIcon platform={link.platform} className="h-6 w-6" />
                        {link.platform === "google_review" && (
                            <Star
                                className="absolute -right-2 -top-2 h-3.5 w-3.5 fill-[hsl(var(--gold))] text-[hsl(var(--gold))]"
                                aria-hidden="true"
                            />
                        )}
                    </span>
                </a>
            ))}

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
