// Telefon gosterimi: +90 555 111 00 01
export const formatPhone = (raw) => {
    const text = String(raw || "").trim();
    let digits = text.replace(/\D/g, "");
    if (digits.startsWith("00")) digits = digits.slice(2);
    if (digits.length === 10 && digits.startsWith("5")) digits = `90${digits}`;
    else if (digits.length === 11 && digits.startsWith("05")) digits = `90${digits.slice(1)}`;
    if (digits.length !== 12 || !digits.startsWith("90")) return text;
    const body = digits.slice(2);
    return `+90 ${body.slice(0, 3)} ${body.slice(3, 6)} ${body.slice(6, 8)} ${body.slice(8)}`;
};
