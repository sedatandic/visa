import React from "react";
import { Link } from "react-router-dom";
import { ShoppingBag } from "lucide-react";
import { useCart } from "../lib/cart";

/** Navbar sepet dugmesi: icindeki urun adedini rozetle gosterir. */
export const CartButton = ({ variant = "desktop" }) => {
    const { count } = useCart();

    if (variant === "mobile") {
        return (
            <Link
                to="/sepet"
                className="flex min-h-[48px] items-center gap-3 rounded-xl px-3 text-sm font-semibold text-foreground hover:bg-muted"
                data-testid="mobile-cart-link"
            >
                <ShoppingBag className="h-4 w-4 text-primary" aria-hidden="true" />
                Sepetim
                {count > 0 && (
                    <span
                        className="ml-auto rounded-full bg-primary px-2 py-0.5 text-xs font-bold text-primary-foreground"
                        data-testid="mobile-cart-count"
                    >
                        {count}
                    </span>
                )}
            </Link>
        );
    }

    return (
        <Link
            to="/sepet"
            aria-label={count ? `Sepetim (${count} ürün)` : "Sepetim"}
            className="relative flex h-14 w-14 items-center justify-center rounded-xl border border-border bg-card text-foreground transition-colors duration-150 hover:border-primary/60 hover:text-primary"
            data-testid="navbar-cart-button"
        >
            <ShoppingBag className="h-5 w-5" aria-hidden="true" />
            {count > 0 && (
                <span
                    className="absolute -right-1.5 -top-1.5 flex h-6 min-w-6 items-center justify-center rounded-full bg-primary px-1.5 text-xs font-bold text-primary-foreground"
                    data-testid="navbar-cart-count"
                >
                    {count}
                </span>
            )}
        </Link>
    );
};
