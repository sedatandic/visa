import React from "react";
import { Link } from "react-router-dom";
import { Compass } from "lucide-react";
import { Button } from "../components/ui/button";

export default function NotFound() {
    return (
        <section className="section" data-testid="not-found-page">
            <div className="container-page max-w-xl text-center">
                <span className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                    <Compass className="h-8 w-8 text-primary" />
                </span>
                <h1 className="mt-6 text-3xl font-bold">Sayfa bulunamadı</h1>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                    Aradığınız sayfa taşınmış veya kaldırılmış olabilir. Ana sayfadan devam edebilir
                    ya da doğrudan başvuru formuna geçebilirsiniz.
                </p>
                <div className="mt-7 flex flex-wrap justify-center gap-3">
                    <Button asChild className="h-11">
                        <Link to="/">Ana sayfa</Link>
                    </Button>
                    <Button asChild variant="secondary" className="h-11 border border-border">
                        <Link to="/basvuru">Başvuru yap</Link>
                    </Button>
                </div>
            </div>
        </section>
    );
}
