"""extras.png: kalkan (sigorta) sola, telefon (eSIM) saga alinir.

Gorsel yatay aynalanir; aynalama yazilari da ters cevirdigi icin dort metin ogesi
(iki etiket, rozet yazisi, SIM cip yazisi) blok halinde duz sekilde geri yazilir.
Aynalanmis metin once genisletilmis maske ile zemine dondurulur (hayalet kalmasin).
"""
from PIL import Image, ImageFilter, ImageOps

SRC = "/app/frontend/public/explainer/extras.png"

img = Image.open(SRC).convert("RGBA")
W, H = img.size
out = ImageOps.mirror(img)


def dark(p):
    r, g, b, a = p
    return a > 30 and r < 205 and g < 195 and b < 185


def badge_text(p):
    r, g, b, a = p
    return a > 30 and r > 160 and g > 120


def chip_text(p):
    r, g, b, a = p
    return a > 30 and r < 225 and g < 215


ELEMENTS = [
    ((40, 718, 372, 782), dark, (0, 0, 0, 0)),  # "DUBAI eSIM"
    ((578, 666, 1068, 806), dark, (0, 0, 0, 0)),  # "SEYAHAT SAGLIK SIGORTASI"
    ((878, 168, 1074, 297), badge_text, (122, 42, 62, 255)),  # rozet yazisi
    ((133, 388, 257, 462), chip_text, (243, 231, 215, 255)),  # cip icindeki "eSIM"
]


def mask_of(crop: Image.Image, pred) -> Image.Image:
    px = crop.load()
    w, h = crop.size
    mask = Image.new("L", (w, h), 0)
    mpx = mask.load()
    for y in range(h):
        for x in range(w):
            if pred(px[x, y]):
                mpx[x, y] = 255
    return mask


for (x0, y0, x1, y1), pred, bg in ELEMENTS:
    crop = img.crop((x0, y0, x1, y1))
    keep = mask_of(crop, pred)
    clear = ImageOps.mirror(keep).filter(ImageFilter.MaxFilter(9))
    box = (W - x1, y0)
    out.paste(Image.new("RGBA", crop.size, bg), box, clear)
    out.paste(crop, box, keep)
    print(f"{(x0, y0, x1, y1)} -> x={box[0]}")

out.save(SRC)
print("saved", SRC)
