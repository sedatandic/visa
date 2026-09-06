import { useCallback, useEffect, useState } from "react";

/**
 * Sepet: eSIM / seyahat sigortasi urunleri tarayicida (localStorage) tutulur.
 * Yalniz urun kimligi + adet saklanir; fiyatlar her zaman /api/products'tan gelir.
 */
const KEY = "dv_cart_v1";
const EVENT = "dv-cart-change";

export const CART_MAX_QTY = 10;
export const CART_MAX_LINES = 6;

const EMPTY = { items: [], applicationRef: "" };

export const readCart = () => {
    try {
        const raw = JSON.parse(localStorage.getItem(KEY) || "null");
        if (!raw) return EMPTY;
        return {
            items: (Array.isArray(raw.items) ? raw.items : [])
                .filter((i) => i && i.product_id)
                .map((i) => ({
                    product_id: String(i.product_id),
                    quantity: Math.min(CART_MAX_QTY, Math.max(1, Number(i.quantity) || 1)),
                })),
            applicationRef: raw.applicationRef || "",
        };
    } catch {
        return EMPTY;
    }
};

const writeCart = (state) => {
    localStorage.setItem(KEY, JSON.stringify(state));
    window.dispatchEvent(new Event(EVENT));
};

export const cartCount = (state) =>
    (state.items || []).reduce((sum, i) => sum + Number(i.quantity || 0), 0);

export const useCart = () => {
    const [state, setState] = useState(readCart);

    useEffect(() => {
        const sync = () => setState(readCart());
        window.addEventListener(EVENT, sync);
        window.addEventListener("storage", sync);
        return () => {
            window.removeEventListener(EVENT, sync);
            window.removeEventListener("storage", sync);
        };
    }, []);

    const add = useCallback((productId, quantity = 1) => {
        const current = readCart();
        const existing = current.items.find((i) => i.product_id === productId);
        if (!existing && current.items.length >= CART_MAX_LINES) {
            return { ok: false, reason: "max_lines" };
        }
        const items = existing
            ? current.items.map((i) =>
                  i.product_id === productId
                      ? { ...i, quantity: Math.min(CART_MAX_QTY, i.quantity + quantity) }
                      : i
              )
            : [...current.items, { product_id: productId, quantity: Math.min(CART_MAX_QTY, quantity) }];
        writeCart({ ...current, items });
        return { ok: true, merged: Boolean(existing) };
    }, []);

    const setQty = useCallback((productId, quantity) => {
        const current = readCart();
        const qty = Math.min(CART_MAX_QTY, Math.max(0, Number(quantity) || 0));
        const items = qty
            ? current.items.map((i) => (i.product_id === productId ? { ...i, quantity: qty } : i))
            : current.items.filter((i) => i.product_id !== productId);
        writeCart({ ...current, items });
    }, []);

    const remove = useCallback((productId) => {
        const current = readCart();
        writeCart({ ...current, items: current.items.filter((i) => i.product_id !== productId) });
    }, []);

    const clear = useCallback(() => writeCart(EMPTY), []);

    const linkApplication = useCallback((reference) => {
        const current = readCart();
        writeCart({ ...current, applicationRef: (reference || "").trim().toUpperCase() });
    }, []);

    return {
        items: state.items,
        applicationRef: state.applicationRef,
        count: cartCount(state),
        add,
        setQty,
        remove,
        clear,
        linkApplication,
    };
};
