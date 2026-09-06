"""Logo wordmark degisimi: "Vize Online" -> "Vize Hatti" (otomatik olcum).

Illustrasyon ve gold DUBAI yazisi orijinal dosyadan korunur; yalnizca alt satir
silinip Philosopher Bold ile yeniden yazilir. Olculer her dosyadan otomatik
okunur: metin blogunun sol/sag kenari, ilk harfin ('V') cap yuksekligi ve taban
cizgisi, metin rengi. Harf araligi ust satirla ayni yerde bitecek sekilde ayarlanir.

Kullanim:
  python /app/scripts/rebrand_logo.py --src <png> --out <png> [--stroke 0] [--dry-run]
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT = Path("/tmp/fonts/Philosopher.ttf")
TEXT = "Vize Hattı"
SS = 4  # supersampling


def _runs(profile, min_gap=1):
    runs, start, in_run = [], 0, False
    gap = 0
    for i, v in enumerate(profile):
        if v > 0:
            if not in_run:
                start, in_run = i, True
            gap = 0
        elif in_run:
            gap += 1
            if gap > min_gap:
                runs.append((start, i - gap))
                in_run = False
    if in_run:
        runs.append((start, len(profile) - 1))
    return runs


def measure(img: Image.Image) -> dict:
    """Alt satir metnini bulur: bbox, taban cizgisi, cap yuksekligi, renk.

    Iki asama: (1) illustrasyondan geniş bir bosluk ile ayrilan metin kolonlari,
    (2) o kolonlarda satir bantlari -> en alt bant = "Vize Online" satiri.
    """
    a = np.array(img)
    mask = a[..., 3] > 30

    col_blocks = _runs(mask.sum(axis=0), min_gap=15)
    text_cols = col_blocks[-1]  # yatay logolarda metin en sagdaki blok
    strip = mask[:, text_cols[0] : text_cols[1] + 1]

    row_bands = _runs(strip.sum(axis=1), min_gap=2)
    if len(row_bands) < 2:
        raise SystemExit(f"iki metin satiri bulunamadi: {row_bands}")
    band = row_bands[-1]

    sub = strip[band[0] : band[1] + 1]
    glyph_blocks = _runs(sub.sum(axis=0), min_gap=1)
    left = text_cols[0] + glyph_blocks[0][0]
    right = text_cols[0] + glyph_blocks[-1][1]

    first = glyph_blocks[0]
    glyph = sub[:, first[0] : first[1] + 1]
    rows = np.where(glyph.sum(axis=1) > 0)[0]
    cap = int(rows.max() - rows.min() + 1)
    baseline = int(band[0] + rows.max())

    region = mask[band[0] : band[1] + 1, left : right + 1]
    colors = a[band[0] : band[1] + 1, left : right + 1, :3][region]
    color = tuple(int(v) for v in colors.mean(axis=0).round())
    return {
        "left": int(left),
        "right": int(right),
        "top": int(band[0]),
        "bottom": int(band[1]),
        "cap": cap,
        "baseline": baseline,
        "color": color,
        "size": img.size,
    }


def render_line(m: dict, stroke: int) -> Image.Image:
    cap, target = m["cap"], (m["right"] - m["left"] + 1) * SS
    size = cap * SS
    for _ in range(12):
        font = ImageFont.truetype(str(FONT), size)
        probe = Image.new("L", (size * 4, size * 3), 0)
        ImageDraw.Draw(probe).text((size, size), "V", font=font, fill=255, stroke_width=stroke * SS)
        box = probe.getbbox()
        if abs((box[3] - box[1]) - cap * SS) <= 1:
            break
        size = max(8, int(size * (cap * SS) / (box[3] - box[1])))
    font = ImageFont.truetype(str(FONT), size)

    widths = [font.getlength(ch) for ch in TEXT]
    tracking = (target - sum(widths)) / max(1, len(TEXT) - 1)
    fill = (*m["color"], 255)

    layer = Image.new("RGBA", (target + 200 * SS, cap * SS * 3), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = 50 * SS, cap * SS
    for ch, adv in zip(TEXT, widths):
        draw.text((x, y), ch, font=font, fill=fill, stroke_width=stroke * SS, stroke_fill=fill)
        x += adv + tracking
    box = layer.getbbox()
    line = layer.crop(box)
    return line.resize((round(line.width / SS), round(line.height / SS)), Image.LANCZOS)


def build(src: Path, out: Path, stroke: int) -> None:
    base = Image.open(src).convert("RGBA")
    m = measure(base)
    print(f"{src.name}: {m}")

    pad = max(2, m["cap"] // 12)
    base.paste((0, 0, 0, 0), (m["left"] - pad, m["top"] - pad, min(base.width, m["right"] + pad + 1), min(base.height, m["bottom"] + pad + 1)))

    line = render_line(m, stroke)
    v_slice = line.crop((0, 0, min(line.width, int(m["cap"] * 1.4)), line.height))
    v_bottom = v_slice.getbbox()[3]
    base.alpha_composite(line, (m["left"], m["baseline"] - v_bottom + 1))
    base.save(out)
    print(f"  -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stroke", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.dry_run:
        print(measure(Image.open(args.src).convert("RGBA")))
    else:
        build(Path(args.src), Path(args.out), args.stroke)
