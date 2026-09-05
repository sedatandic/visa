import React from "react";

// **...** ile isaretli bolumleri kalin gosterir (yasal metinlerde sirket adlari icin).
export const BoldText = ({ text, className = "", strongClassName = "font-bold text-foreground" }) => {
    if (!text) return null;
    return (
        <span className={className}>
            {String(text)
                .split(/(\*\*[^*]+\*\*)/g)
                .filter(Boolean)
                .map((part, i) =>
                    part.startsWith("**") && part.endsWith("**") ? (
                        <strong key={i} className={strongClassName}>
                            {part.slice(2, -2)}
                        </strong>
                    ) : (
                        <React.Fragment key={i}>{part}</React.Fragment>
                    )
                )}
        </span>
    );
};
