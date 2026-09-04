import React from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";
import { SocialDock } from "./SocialDock";

export const SiteLayout = ({ children }) => (
    <div className="sky-shell relative flex min-h-screen flex-col">
        <Navbar />
        <main className="relative flex-1">{children}</main>
        <Footer />
        <SocialDock />
    </div>
);

export const PageHeader = ({ eyebrow, title, description, children }) => (
    <section className="relative overflow-hidden">
        <div className="container-page relative pt-0">
            <div className="panel-float px-5 py-10 sm:px-8 sm:py-12">
                {eyebrow && <span className="eyebrow">{eyebrow}</span>}
                <h1 className="mt-4 max-w-3xl text-3xl font-extrabold leading-tight text-[hsl(30_62%_38%)] sm:text-4xl lg:text-[44px]">
                    {title}
                </h1>
                {description && (
                    <p className="mt-4 max-w-4xl text-base leading-7 text-muted-foreground">
                        {description}
                    </p>
                )}
                {children}
            </div>
        </div>
    </section>
);
