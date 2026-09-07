import React from "react";

const LETTERS = ["D", "U", "B", "A", "I"];

// Numaranin son 5 hanesi tus takiminda DUBAI harflerine denk gelir (3-8-2-2-4);
// harfler rakamlarin tam altinda hizali gosterilir.
export const PhoneDubai = ({ phone, className = "", letterClassName = "text-primary" }) => {
    const text = String(phone || "");
    const tail = [];
    let digits = 0;
    let i = text.length - 1;
    for (; i >= 0 && digits < 5; i -= 1) {
        if (/\d/.test(text[i])) digits += 1;
        tail.unshift(text[i]);
    }
    if (digits < 5) return <span className={className}>{text}</span>;

    let letterIndex = 0;
    return (
        <span className={`inline-flex items-end ${className}`} data-testid="phone-dubai" aria-hidden="true">
            <span className="leading-none">{text.slice(0, i + 1)}</span>
            {tail.map((char, index) => {
                const isDigit = /\d/.test(char);
                const letter = isDigit ? LETTERS[letterIndex++] : "";
                return (
                    <span key={`${char}-${index}`} className="inline-flex flex-col items-center leading-none">
                        <span>{char === " " ? "\u00a0" : char}</span>
                        <span className={`mt-0.5 text-[9px] font-extrabold leading-none tracking-tight ${letterClassName}`}>
                            {letter || "\u00a0"}
                        </span>
                    </span>
                );
            })}
        </span>
    );
};
