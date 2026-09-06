"""Sosyal medya icin kare marka gorseli (Instagram / WhatsApp profil).

Parcalar orijinal varliklardan alinir: amblem `emblem-512.png`, altin "DUBAI"
yazisi yatay logodan kirpilir, alt satir Philosopher Bold ile yazilir. Cikti
1080x1080; profil resmi daire kirpildigi icin kenarlarda bol bosluk birakilir.

Kullanim: python /app/scripts/make_social_logo.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BRAND = Path("/app/frontend/public/brand")
FONT = Path("/tmp/fonts/Philosopher.ttf")
SIZE = 1080
SS = 4
TEXT = "Vize Hattı"
COPPER = (141, 90, 34)
CREAM = (247, 241, 230)
NAVY = (16, 32, 44)


def trim(img: Image.Image) -> Image.Image:
    box = img.getbbox()
    return img.crop(box) if box else img


def illustration() -> Image.Image:
    """Yatay logodaki illustrasyon (deve + altin palmiye + silüet + dalga)."""
    src = Image.open(BRAND / "logo-horizontal-gold-palm.png").convert("RGBA")
    return trim(src.crop((0, 0, 492, src.height)))


def dubai_wordmark() -> Image.Image:
    """Yatay logodaki altin DUBAI yazisini kirpar (piksel piksel orijinal)."""
    src = Image.open(BRAND / "logo-horizontal-gold-palm.png").convert("RGBA")
    return trim(src.crop((500, 95, src.width, 195)))


def render_text(width: int, color: tuple) -> Image.Image:
    """Verilen genislige oturan "Vize Hattı" satiri."""
    font_size = 120 * SS
    font = ImageFont.truetype(str(FONT), font_size)
    natural = sum(font.getlength(ch) for ch in TEXT)
    tracking = (width * SS - natural) / (len(TEXT) - 1)
    layer = Image.new("RGBA", (width * SS + 40 * SS, font_size * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x = 0
    for ch in TEXT:
        draw.text((x, font_size // 3), ch, font=font, fill=(*color, 255))
        x += font.getlength(ch) + tracking
    line = trim(layer)
    return line.resize((round(line.width / SS), round(line.height / SS)), Image.LANCZOS)


def build(bg, text_color: tuple, out_name: str) -> None:
    canvas = Image.new("RGBA", (SIZE, SIZE), bg if bg else (0, 0, 0, 0))

    emblem = illustration()
    word = dubai_wordmark()

    block_w = 660  # DUBAI ve alt satirin genisligi
    word = word.resize((block_w, round(word.height * block_w / word.width)), Image.LANCZOS)
    sub = render_text(block_w, text_color)

    emblem_w = 600
    emblem = emblem.resize((emblem_w, round(emblem.height * emblem_w / emblem.width)), Image.LANCZOS)

    gap_1, gap_2 = 34, 24
    total_h = emblem.height + gap_1 + word.height + gap_2 + sub.height
    y = (SIZE - total_h) // 2

    canvas.alpha_composite(emblem, ((SIZE - emblem.width) // 2, y))
    y += emblem.height + gap_1
    canvas.alpha_composite(word, ((SIZE - word.width) // 2, y))
    y += word.height + gap_2
    canvas.alpha_composite(sub, ((SIZE - sub.width) // 2, y))

    canvas.save(BRAND / out_name)
    print(BRAND / out_name, canvas.size)


if __name__ == "__main__":
    build(None, COPPER, "social-square.png")
    build((*CREAM, 255), COPPER, "social-square-light.png")
    build((*NAVY, 255), CREAM, "social-square-dark.png")
