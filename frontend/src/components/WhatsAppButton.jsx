import React from "react";
import { useContact, waLink } from "../lib/contact";

export const WhatsAppButton = () => {
    const contact = useContact();
    if (!contact.whatsapp) return null;
    return (
    <a
        href={waLink(contact, "Merhaba, Dubai vizesi hakkında bilgi almak istiyorum.")}
        target="_blank"
        rel="noreferrer"
        aria-label="WhatsApp ile yazın"
        data-testid="whatsapp-floating-button"
        className="fixed bottom-4 right-4 z-50 flex h-12 items-center gap-2 rounded-full bg-[hsl(var(--primary))] px-3.5 text-primary-foreground shadow-[var(--shadow-float)] transition-transform duration-150 hover:-translate-y-0.5 hover:bg-[hsl(var(--teal-hover))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 sm:bottom-5 sm:right-5 sm:h-14 sm:px-4"
        style={{ boxShadow: "var(--shadow-float)" }}
    >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M17.47 14.38c-.3-.15-1.75-.86-2.02-.96-.27-.1-.47-.15-.67.15-.2.3-.77.96-.95 1.16-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.9-.8-1.5-1.79-1.67-2.09-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.6-.92-2.19-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.01-1.04 2.46 0 1.45 1.06 2.85 1.21 3.05.15.2 2.09 3.19 5.06 4.47.71.3 1.26.48 1.69.62.71.22 1.36.19 1.87.12.57-.09 1.75-.71 2-1.41.25-.7.25-1.29.17-1.41-.07-.12-.27-.2-.57-.35zM12.02 2C6.5 2 2.02 6.48 2.02 12c0 1.77.46 3.42 1.27 4.86L2 22l5.28-1.26A9.94 9.94 0 0 0 12.02 22c5.52 0 10-4.48 10-10s-4.48-10-10-10zm0 18.2c-1.6 0-3.09-.46-4.34-1.26l-.31-.19-3.13.75.76-3.05-.2-.32A8.14 8.14 0 0 1 3.82 12c0-4.52 3.68-8.2 8.2-8.2s8.2 3.68 8.2 8.2-3.68 8.2-8.2 8.2z" />
        </svg>
        <span className="hidden text-sm font-semibold sm:inline">WhatsApp</span>
    </a>
    );
};
