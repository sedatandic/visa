"""Telefon numarasi gosterimi: +90 555 111 00 01 duzeni."""


def format_phone(raw: str | None) -> str:
    """TR cep numarasini okunur gruplara ayirir; taninmayan formati oldugu gibi dondurur."""
    text = str(raw or "").strip()
    digits = "".join(c for c in text if c.isdigit())
    if digits.startswith("00"):
        digits = digits[2:]
    if len(digits) == 10 and digits.startswith("5"):
        digits = f"90{digits}"
    elif len(digits) == 11 and digits.startswith("05"):
        digits = f"90{digits[1:]}"
    if len(digits) != 12 or not digits.startswith("90"):
        return text
    body = digits[2:]
    return f"+90 {body[:3]} {body[3:6]} {body[6:8]} {body[8:]}"
