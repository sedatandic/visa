"""track.png'i saydam zeminli olarak sagam kaynaktan (track.jpg) yeniden uretir.

Sorun: onceki saydam surumde telefonun sol alt kosesi silinmisti (zemin ayiklama
telefonun kenar cizgisinden iceri sizmisti). Bu betik duz krem zemini dusuk esikli
flood fill ile kaldirir, ardindan bos kenarlari kirpar.
"""

import os
import shutil
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

BASE = "/app/frontend/public/explainer"
MARK = (255, 0, 255)
PAD = 6
TOLERANCE = 12


def seeds(width: int, height: int):
    xs = [1, width // 4, width // 2, 3 * width // 4, width - 2]
    ys = [1, height // 4, height // 2, 3 * height // 4, height - 2]
    return (
        [(x, 1) for x in xs]
        + [(x, height - 2) for x in xs]
        + [(1, y) for y in ys]
        + [(width - 2, y) for y in ys]
    )


def rebuild(name: str, thresh: int) -> None:
    source = os.path.join(BASE, f"{name}.jpg")
    target = os.path.join(BASE, f"{name}.png")
    backup = os.path.join(BASE, f"{name}.cutcorner.png")
    if os.path.exists(target) and not os.path.exists(backup):
        shutil.copy2(target, backup)

    rgb = Image.open(source).convert("RGB")
    work = rgb.copy()
    for point in seeds(*work.size):
        if sum(abs(a - b) for a, b in zip(work.getpixel(point), MARK)) < 30:
            continue
        ImageDraw.floodfill(work, point, MARK, thresh=thresh)

    diff = ImageChops.difference(work, Image.new("RGB", work.size, MARK)).convert("L")
    mask = diff.point(lambda v: 0 if v == 0 else 255).filter(ImageFilter.GaussianBlur(0.6))
    removed = sum(1 for v in mask.getdata() if v < 8)

    out = rgb.convert("RGBA")
    out.putalpha(mask)
    box = out.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    out = out.crop(
        (
            max(0, box[0] - PAD),
            max(0, box[1] - PAD),
            min(out.width, box[2] + PAD),
            min(out.height, box[3] + PAD),
        )
    )
    out.save(target, optimize=True)
    print(f"{name}: zemin {removed / (rgb.width * rgb.height):.0%} saydam · {rgb.size} -> {out.size}")


if __name__ == "__main__":
    scene = sys.argv[1] if len(sys.argv) > 1 else "track"
    rebuild(scene, int(sys.argv[2]) if len(sys.argv) > 2 else 20)
