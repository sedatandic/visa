"""Anlatim illustrasyonlarinin zemin rengini saydam yapar (tek seferlik yardimci).

Kullanici notu: "animasyonlarda ayrica zemin rengi olmasin" — beyaz/krem zemin
kaldirilir, illustrasyon panelin arka planiyla ayni renkte gorunur.
Yalniz kenardan baglantili zemin bolgesi silinir (flood fill), illustrasyon
icindeki beyaz alanlar (gomlek, pasaport sayfasi, vesikalik fon) korunur.
Orijinaller *.solidbg.png olarak yedeklenir.
"""

import os
import shutil

from PIL import Image, ImageDraw, ImageFilter

BASE = "/app/frontend/public/explainer"
SCENES = ["intro", "passport", "photo", "upload", "extras", "cta", "track"]
MARK = (255, 0, 255)
THRESH = 42


def seeds(width: int, height: int):
    xs = [1, width // 4, width // 2, 3 * width // 4, width - 2]
    ys = [1, height // 4, height // 2, 3 * height // 4, height - 2]
    points = [(x, 1) for x in xs] + [(x, height - 2) for x in xs]
    points += [(1, y) for y in ys] + [(width - 2, y) for y in ys]
    return points


def make_transparent(name: str) -> None:
    path = os.path.join(BASE, f"{name}.png")
    im = Image.open(path)
    if im.mode == "RGBA" and im.getchannel("A").getextrema()[0] < 250:
        print(f"{name}: zemin zaten saydam, atlandi")
        return

    backup = os.path.join(BASE, f"{name}.solidbg.png")
    if not os.path.exists(backup):
        shutil.copy2(path, backup)

    rgb = im.convert("RGB")
    work = rgb.copy()
    for point in seeds(*work.size):
        if sum(abs(a - b) for a, b in zip(work.getpixel(point), MARK)) < 30:
            continue
        ImageDraw.floodfill(work, point, MARK, thresh=THRESH)

    mask = Image.new("L", work.size, 255)
    mask_px = mask.load()
    work_px = work.load()
    removed = 0
    for y in range(work.height):
        for x in range(work.width):
            if work_px[x, y] == MARK:
                mask_px[x, y] = 0
                removed += 1
    mask = mask.filter(ImageFilter.GaussianBlur(0.6))

    out = rgb.convert("RGBA")
    out.putalpha(mask)
    out.save(path, optimize=True)
    print(f"{name}: {removed} piksel zemin saydamlastirildi ({removed / (im.width * im.height):.0%})")


if __name__ == "__main__":
    for scene in SCENES:
        make_transparent(scene)
