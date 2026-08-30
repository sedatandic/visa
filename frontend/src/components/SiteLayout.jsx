import React from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";
import { WhatsAppButton } from "./WhatsAppButton";

export const SiteLayout = ({ children }) => (
    <div className="flex min-h-screen flex-col bg-background">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
        <WhatsAppButton />
    </div>
);

export const PageHeader = ({ eyebrow, title, description, children }) => (
    <section className="relative overflow-hidden border-b border-border bg-card">
        <div className="hero-glow absolute inset-0" aria-hidden="true" />
        <div className="container-page relative py-12 sm:py-16">
            {eyebrow && <span className="eyebrow">{eyebrow}</span>}
            <h1 className="mt-4 max-w-3xl text-3xl font-bold leading-tight sm:text-4xl lg:text-[42px]">
                {title}
            </h1>
            {description && (
                <p className="mt-4 max-w-2xl text-base leading-7 text-muted-foreground">{description}</p>
            )}
            {children}
        </div>
    </section>
);
