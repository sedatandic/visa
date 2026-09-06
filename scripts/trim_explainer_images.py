"""Anlatim illustrasyonlarindaki bos kenarlari kirpar (tek seferlik yardimci).

Her PNG'de illustrasyonun cevresindeki duz zemin (veya saydam alan) kaldirilir,
6px nefes payi birakilir. Boylece tum sahneler cerceveyi ayni oranda doldurur
(kullanici notu: "en sondaki animasyon boyutlari iyi, digerlerini de oyle yap").
Orijinaller *.pretrim.png olarak yedeklenir.
"""

import os
import shutil

from PIL import Image, ImageChops

SCENES = ["intro", "passport", "photo", "upload", "track", "extras", "cta"]
BASE = "/app/frontend/public/explainer"
PAD = 6
TOLERANCE = 12


def content_box(im: Image.Image):
    if im.mode == "RGBA":
        alpha = im.getchannel("A")
        if alpha.getextrema()[0] < 250:
            return alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
    rgb = im.convert("RGB")
    bg = rgb.getpixel((1, 1))
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, bg)).convert("L")
    return diff.point(lambda v: 255 if v > TOLERANCE else 0).getbbox()


def trim(name: str) -> None:
    path = os.path.join(BASE, f"{name}.png")
    backup = os.path.join(BASE, f"{name}.pretrim.png")
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
    im = Image.open(backup)
    box = content_box(im)
    if not box:
        print(f"{name}: icerik bulunamadi, atlandi")
        return
    left = max(0, box[0] - PAD)
    top = max(0, box[1] - PAD)
    right = min(im.width, box[2] + PAD)
    bottom = min(im.height, box[3] + PAD)
    out = im.crop((left, top, right, bottom))
    out.save(path, optimize=True)
    print(f"{name}: {im.size} -> {out.size}")


if __name__ == "__main__":
    for scene in SCENES:
        trim(scene)
