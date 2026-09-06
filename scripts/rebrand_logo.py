"""Logo wordmark degisimi: "Vize Online" -> "Vize Hatti".

Orijinal PNG'nin illustrasyonu ve gold DUBAI yazisi korunur; yalnizca ikinci
satir silinip Philosopher Bold ile yeniden yazilir. Olculer orijinalden alinir:
cap yuksekligi 53px, baseline y=252, sol kenar x=506, blok genisligi 393px
(DUBAI ile ayni hizada bitmesi icin harf araligi otomatik ayarlanir).

Kullanim: python /app/scripts/rebrand_logo.py [--stroke 1]
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path("/app/frontend/public/brand/logo-horizontal-gold-palm.png")
FONT = Path("/tmp/fonts/Philosopher.ttf")
TEXT = "Vize Hattı"
COLOR = (141, 90, 34, 255)

# orijinal olculer
LEFT, RIGHT, BASELINE, CAP = 506, 898, 252, 53
ERASE_BOX = (490, 190, 929, 260)
SS = 4  # supersampling


def render_line(stroke: int) -> Image.Image:
    """Metni cap yuksekligi CAP ve genisligi (RIGHT-LEFT) olacak sekilde uretir."""
    size = CAP * SS
    for _ in range(12):  # cap yuksekligini olcerek punto duzelt
        font = ImageFont.truetype(str(FONT), size)
        probe = Image.new("L", (size * 4, size * 3), 0)
        ImageDraw.Draw(probe).text((size, size), "V", font=font, fill=255, stroke_width=stroke * SS)
        box = probe.getbbox()
        cap_now = box[3] - box[1]
        if abs(cap_now - CAP * SS) <= 1:
            break
        size = max(8, int(size * (CAP * SS) / cap_now))
    font = ImageFont.truetype(str(FONT), size)

    # harf araligi: toplam genislik hedefe esitlenir
    widths = [font.getlength(ch) for ch in TEXT]
    target = (RIGHT - LEFT + 1) * SS
    tracking = (target - sum(widths)) / max(1, len(TEXT) - 1)

    layer = Image.new("RGBA", (target + 200 * SS, CAP * SS * 3), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x = 50 * SS
    y = CAP * SS
    for ch, adv in zip(TEXT, widths):
        draw.text((x, y), ch, font=font, fill=COLOR, stroke_width=stroke * SS, stroke_fill=COLOR)
        x += adv + tracking
    return layer.crop(layer.getbbox()).resize(
        (round((layer.getbbox()[2] - layer.getbbox()[0]) / SS), round((layer.getbbox()[3] - layer.getbbox()[1]) / SS)),
        Image.LANCZOS,
    )


def build(stroke: int, out_path: Path) -> Image.Image:
    base = Image.open(SRC).convert("RGBA")
    base.paste((0, 0, 0, 0), ERASE_BOX)  # eski yaziyi sil

    line = render_line(stroke)
    # 'V' harfinin alt kenari baseline'a otursun; 'i' noktasi ustte kalabilir
    v_only = line.crop((0, 0, min(line.width, 90), line.height))
    v_bottom = v_only.getbbox()[3]
    base.alpha_composite(line, (LEFT, BASELINE - v_bottom + 1))
    base.save(out_path)
    return base


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stroke", type=int, default=1)
    ap.add_argument("--out", default="/tmp/logo_hatti.png")
    args = ap.parse_args()
    img = build(args.stroke, Path(args.out))
    print(args.out, img.size)
