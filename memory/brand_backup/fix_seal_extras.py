"""extras.png icindeki '30.000 € TEMINAT' rozetini keskin kenarli olarak yeniden cizer."""
import math
from PIL import Image, ImageDraw, ImageFont

SRC = "/app/frontend/public/explainer/extras.png"
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

CX, CY, R = 125, 230, 119
S = 4  # supersampling
MAROON = (122, 42, 61, 255)
MAROON_DARK = (104, 34, 50, 255)
GOLD = (223, 176, 130, 255)
CREAM = (250, 243, 231, 255)
ANGLE = 9  # metin egimi

im = Image.open("/tmp/extras_orig_backup.png").convert("RGBA")

size = (2 * R + 1) * S
badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
d = ImageDraw.Draw(badge)
d.ellipse((0, 0, size - 1, size - 1), fill=MAROON)
# ic halka: koyu cizgi + altin bant + koyu cizgi
for r0, r1, col in ((97.5, 99.5, MAROON_DARK), (99.5, 106.5, GOLD), (106.5, 108.5, MAROON_DARK)):
    d.ellipse(
        (
            (R - r1) * S,
            (R - r1) * S,
            (R + r1) * S,
            (R + r1) * S,
        ),
        outline=col,
        width=int(round((r1 - r0) * S)),
    )

# metin: iki satir, hafif egimli
text_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
td = ImageDraw.Draw(text_layer)
lines = ["30.000 €", "TEMİNAT"]
R_IN = 92  # altin halkanin ic yaricapi (guvenlik payi dahil)


def layout(pt):
    """Verilen punto icin satir kutularini dondurur; halkaya sigmazsa None."""
    fonts = [ImageFont.truetype(FONT, pt * S), ImageFont.truetype(FONT, pt * S)]
    boxes = [td.textbbox((0, 0), t, font=f) for t, f in zip(lines, fonts)]
    hs = [b[3] - b[1] for b in boxes]
    gap = int(6 * S)
    total = sum(hs) + gap
    top = -total / 2
    for (b, h) in zip(boxes, hs):
        y_far = max(abs(top), abs(top + h))
        if y_far >= R_IN * S:
            return None
        allowed = 2 * math.sqrt((R_IN * S) ** 2 - y_far**2)
        if (b[2] - b[0]) > allowed:
            return None
        top += h + gap
    return fonts, boxes, hs, gap, total


chosen = None
for pt in range(46, 20, -1):
    chosen = layout(pt)
    if chosen:
        print("punto:", pt)
        break
fonts, boxes, heights, gap, total_h = chosen
y = size / 2 - total_h / 2
for text, font, h, box in zip(lines, fonts, heights, boxes):
    x = size / 2 - (box[2] - box[0]) / 2 - box[0]
    td.text((x, y - box[1]), text, font=font, fill=CREAM)
    y += h + gap
text_layer = text_layer.rotate(ANGLE, resample=Image.BICUBIC, center=(size / 2, size / 2))
badge.alpha_composite(text_layer)

badge = badge.resize((2 * R + 1, 2 * R + 1), Image.LANCZOS)
im.alpha_composite(badge, dest=(CX - R, CY - R))

# rozet disinda kalan yari saydam dikdortgen kalintisini temizle
px = im.load()
cleared = 0
for y in range(CY - R - 20, CY + R + 21):
    for x in range(max(0, CX - R - 20), CX + R + 21):
        dist = math.hypot(x - CX, y - CY)
        if dist <= R + 0.5 or dist > R + 30:
            continue
        r, g, b, a = px[x, y]
        if a > 20 and r < 210 and g < 110 and b < 130:
            px[x, y] = (244, 237, 218, 0)
            cleared += 1

im.save(SRC)
print("temizlenen piksel:", cleared)
