import { useCallback, useEffect, useState } from "react";

/**
 * Sepet: eSIM / seyahat sigortasi / Dubai turu urunleri tarayicida (localStorage) tutulur.
 * Yalniz urun kimligi + adet (+ tur icin tarih/saat) saklanir; fiyatlar her zaman
 * /api/products'tan gelir.
 */
const KEY = "dv_cart_v1";
const EVENT = "dv-cart-change";

export const CART_MAX_QTY = 10;
export const CART_MAX_LINES = 6;

const EMPTY = { items: [], applicationRef: "", bundleId: "" };

const clampQty = (value) => Math.min(CART_MAX_QTY, Math.max(1, Number(value) || 1));

export const readCart = () => {
    try {
        const raw = JSON.parse(localStorage.getItem(KEY) || "null");
        if (!raw) return EMPTY;
        return {
            items: (Array.isArray(raw.items) ? raw.items : [])
                .filter((i) => i && i.product_id)
                .map((i) => ({
                    product_id: String(i.product_id),
                    quantity: clampQty(i.quantity),
                    scheduled_date: i.scheduled_date || "",
                    scheduled_time: i.scheduled_time || "",
                })),
            applicationRef: raw.applicationRef || "",
            bundleId: raw.bundleId || "",
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

const mergeItem = (items, productId, quantity, extras) => {
    const existing = items.find((i) => i.product_id === productId);
    if (!existing) {
        return [
            ...items,
            {
                product_id: productId,
                quantity: clampQty(quantity),
                scheduled_date: extras.scheduled_date || "",
                scheduled_time: extras.scheduled_time || "",
            },
        ];
    }
    return items.map((i) =>
        i.product_id === productId
            ? {
                  ...i,
                  quantity: Math.min(CART_MAX_QTY, i.quantity + clampQty(quantity)),
                  scheduled_date: extras.scheduled_date || i.scheduled_date,
                  scheduled_time: extras.scheduled_time || i.scheduled_time,
              }
            : i
    );
};

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

    const add = useCallback((productId, quantity = 1, extras = {}) => {
        const current = readCart();
        const isNew = !current.items.some((i) => i.product_id === productId);
        if (isNew && current.items.length >= CART_MAX_LINES) {
            return { ok: false, reason: "max_lines" };
        }
        writeCart({ ...current, items: mergeItem(current.items, productId, quantity, extras) });
        return { ok: true, merged: !isNew };
    }, []);

    /** Hazir paket: birkac urunu tek seferde ekler. */
    const addMany = useCallback((list, options = {}) => {
        const current = readCart();
        let items = current.items;
        for (const entry of list) {
            if (!entry?.product_id) continue;
            const isNew = !items.some((i) => i.product_id === entry.product_id);
            if (isNew && items.length >= CART_MAX_LINES) return { ok: false, reason: "max_lines" };
            items = mergeItem(items, entry.product_id, entry.quantity || 1, entry);
        }
        writeCart({
            ...current,
            items,
            bundleId: options.bundleId ?? current.bundleId,
        });
        return { ok: true };
    }, []);

    const setQty = useCallback((productId, quantity) => {
        const current = readCart();
        const qty = Math.min(CART_MAX_QTY, Math.max(0, Number(quantity) || 0));
        const items = qty
            ? current.items.map((i) => (i.product_id === productId ? { ...i, quantity: qty } : i))
            : current.items.filter((i) => i.product_id !== productId);
        writeCart({ ...current, items });
    }, []);

    /** Tur satirinin tarih/saatini gunceller. */
    const setSchedule = useCallback((productId, patch) => {
        const current = readCart();
        writeCart({
            ...current,
            items: current.items.map((i) => (i.product_id === productId ? { ...i, ...patch } : i)),
        });
    }, []);

    const remove = useCallback((productId) => {
        const current = readCart();
        const items = current.items.filter((i) => i.product_id !== productId);
        writeCart({ ...current, items, bundleId: items.length ? current.bundleId : "" });
    }, []);

    const clear = useCallback(() => writeCart(EMPTY), []);

    const linkApplication = useCallback((reference) => {
        const current = readCart();
        writeCart({ ...current, applicationRef: (reference || "").trim().toUpperCase() });
    }, []);

    const linkBundle = useCallback((bundleId) => {
        const current = readCart();
        writeCart({ ...current, bundleId: bundleId || "" });
    }, []);

    return {
        items: state.items,
        applicationRef: state.applicationRef,
        bundleId: state.bundleId,
        count: cartCount(state),
        add,
        addMany,
        setQty,
        setSchedule,
        remove,
        clear,
        linkApplication,
        linkBundle,
    };
};
