"""Ana sayfadaki vize anlatimini WhatsApp reklamina uygun MP4'e cevirir.

Kaynaklar:
  - Sahne gorselleri: /app/frontend/public/explainer/{key}.png
  - Anlatim sesi + sahne zamanlari: /app/frontend/public/audio/explainer/full.mp3 + full.json
  - Sahne metinleri: bu dosyadaki SCENE_TEXT (VisaExplainer.jsx ile ayni)

Cikti:
  /app/frontend/public/reklam/dubai-vize-hatti-reklam-dikey.mp4  (1080x1920)
  /app/frontend/public/reklam/dubai-vize-hatti-reklam-kare.mp4   (1080x1080)

Kullanim: python /app/scripts/render_explainer_video.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

PUBLIC = "/app/frontend/public"
EXPLAINER = os.path.join(PUBLIC, "explainer")
AUDIO = os.path.join(PUBLIC, "audio", "explainer")
OUT_DIR = os.path.join(PUBLIC, "reklam")
FONT_PATH = "/app/scripts/fonts/Figtree.ttf"

BG = (250, 244, 234)
CARD = (255, 255, 255)
GOLD = (176, 106, 41)
INK = (62, 42, 20)
MUTED = (138, 115, 85)
LINE = (234, 223, 203)
SKY = (46, 155, 230)

SITE = "www.dubaivizehatti.com"
PHONE = "+90 532 588 26 30"

SCENE_TEXT = {
    "intro": {
        "step": "Adım 1",
        "title": "Dubai vizesi almak artık çok kolay",
        "subtitle": "Dubai vizesi almak artık çok kolay. Başvurunuzu yapmak için yalnızca iki belgeye ihtiyacınız var.",
    },
    "passport": {
        "step": "1. belge",
        "title": "Pasaportunuzun kimlik sayfası",
        "subtitle": "İlk olarak, pasaportunuzun kimlik bilgilerinin yer aldığı sayfanın fotoğrafını yükleyin.",
    },
    "photo": {
        "step": "2. belge",
        "title": "Güncel bir vesikalık fotoğraf",
        "subtitle": "Ardından beyaz fonda çekilmiş güncel bir vesikalık fotoğraf ekleyin. Gözlüksüz ve şapkasız olmalı.",
    },
    "upload": {
        "step": "Adım 2",
        "title": "Yükleyin ve ödemeyi tamamlayın",
        "subtitle": "Belgelerinizi yükleyip ödemenizi yapmanız yeterli. Uçak bileti ya da otel rezervasyonu istemiyoruz.",
    },
    "track": {
        "step": "Adım 3",
        "title": "Süreci sizin adınıza biz takip ediyoruz",
        "subtitle": "Tüm aşamaları biz takip ediyoruz; onaylanan vizenizi ortalama iki iş gününde e-posta ve WhatsApp ile gönderiyoruz.",
    },
    "extras": {
        "step": "Ekstra",
        "title": "Seyahat sigortası ve Dubai eSIM",
        "subtitle": "Seyahat sigortanızı ve Dubai eSIM'inizi de ekleyebilirsiniz; Dubai'ye indiğiniz an internet ve teminat hazır.",
    },
    "cta": {
        "step": "Son adım",
        "title": "Dubai Vize Hattı ile güvenle başvurun",
        "subtitle": "TÜRSAB üyesi A grubu seyahat acentesi iş birliğiyle başvurunuzu baştan sona biz yürütüyoruz. Dubai sizi bekliyor!",
    },
}


def font(size: int, weight: str = "Regular") -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:  # varyasyon desteklenmezse duz agirlik
        pass
    return f


def wrap(draw, text: str, fnt, max_width: int) -> list:
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_block(draw, text, fnt, box, fill, line_gap=12, center=False, max_lines=None):
    """Metni kutuya sigacak sekilde yazar, kullanilan yuksekligi dondurur."""
    x, y, width = box
    lines = wrap(draw, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    height = fnt.size + line_gap
    for i, line in enumerate(lines):
        lx = x + (width - draw.textlength(line, font=fnt)) / 2 if center else x
        draw.text((lx, y + i * height), line, font=fnt, fill=fill)
    return len(lines) * height


def rounded(draw, box, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def paste_fit(canvas, image_path, box):
    """Gorseli oranini koruyarak kutuya sigdirip ortalar."""
    x0, y0, x1, y1 = box
    img = Image.open(image_path).convert("RGBA")
    scale = min((x1 - x0) / img.width, (y1 - y0) / img.height)
    size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
    img = img.resize(size, Image.LANCZOS)
    canvas.paste(img, (x0 + (x1 - x0 - size[0]) // 2, y0 + (y1 - y0 - size[1]) // 2), img)


def scene_frame(key: str, index: int, total: int, size: tuple) -> Image.Image:
    w, h = size
    vertical = h > w
    canvas = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(canvas)
    meta = SCENE_TEXT[key]
    pad = int(w * 0.06)

    # ust logo
    logo_w = int(w * (0.38 if vertical else 0.3))
    logo = Image.open(os.path.join(PUBLIC, "brand", "logo-horizontal-gold-palm.png")).convert("RGBA")
    logo = logo.resize((logo_w, int(logo.height * logo_w / logo.width)), Image.LANCZOS)
    logo_y = int(h * (0.035 if vertical else 0.03))
    canvas.paste(logo, ((w - logo_w) // 2, logo_y), logo)

    top = logo_y + logo.height + int(h * (0.03 if vertical else 0.02))
    art_h = int(h * (0.42 if vertical else 0.40))
    rounded(draw, (pad, top, w - pad, top + art_h), 44, CARD, LINE, 3)
    paste_fit(canvas, os.path.join(EXPLAINER, f"{key}.png"), (pad + 24, top + 24, w - pad - 24, top + art_h - 24))

    y = top + art_h + int(h * (0.035 if vertical else 0.025))

    # adim etiketi
    badge_font = font(int(w * 0.028), "ExtraBold")
    label = meta["step"].upper()
    bw = draw.textlength(label, font=badge_font) + 44
    bh = badge_font.size + 26
    rounded(draw, ((w - bw) / 2, y, (w + bw) / 2, y + bh), bh / 2, GOLD, None, 0)
    draw.text(((w - draw.textlength(label, font=badge_font)) / 2, y + 12), label, font=badge_font, fill=CARD)
    y += bh + int(h * 0.022)

    # baslik
    y += draw_block(
        draw,
        meta["title"],
        font(int(w * (0.058 if vertical else 0.05)), "ExtraBold"),
        (pad, y, w - 2 * pad),
        GOLD,
        line_gap=14,
        center=True,
        max_lines=2,
    )
    y += int(h * 0.012)

    # altyazi kutusu
    sub_font = font(int(w * (0.034 if vertical else 0.03)), "Medium")
    lines = wrap(draw, meta["subtitle"], sub_font, w - 2 * pad - 56)
    box_h = len(lines) * (sub_font.size + 14) + 52
    rounded(draw, (pad, y, w - pad, y + box_h), 30, CARD, LINE, 2)
    draw_block(
        draw,
        meta["subtitle"],
        sub_font,
        (pad + 28, y + 26, w - 2 * pad - 56),
        INK,
        line_gap=14,
        center=True,
    )

    # sahne gostergesi
    dot_y = h - int(h * (0.055 if vertical else 0.06))
    dot_w, gap = int(w * 0.055), int(w * 0.012)
    total_w = total * dot_w + (total - 1) * gap
    x = (w - total_w) / 2
    for i in range(total):
        color = GOLD if i <= index else LINE
        rounded(draw, (x, dot_y, x + dot_w, dot_y + 8), 4, color, None, 0)
        x += dot_w + gap

    foot = font(int(w * 0.026), "SemiBold")
    draw.text(
        ((w - draw.textlength(SITE, font=foot)) / 2, dot_y + 24),
        SITE,
        font=foot,
        fill=MUTED,
    )
    return canvas


def outro_frame(size: tuple) -> Image.Image:
    w, h = size
    vertical = h > w
    canvas = Image.new("RGB", size, BG)
    # Icerik once seffaf katmana cizilir, sonra dikeyde ortalanir.
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    pad = int(w * 0.08)

    logo_w = int(w * (0.62 if vertical else 0.5))
    logo = Image.open(os.path.join(PUBLIC, "brand", "logo-horizontal-gold-palm.png")).convert("RGBA")
    logo = logo.resize((logo_w, int(logo.height * logo_w / logo.width)), Image.LANCZOS)
    y = 0
    layer.paste(logo, ((w - logo_w) // 2, y), logo)
    y += logo.height + int(h * (0.05 if vertical else 0.04))

    y += draw_block(
        draw,
        "Dubai vizeniz 2 iş gününde hazır",
        font(int(w * (0.062 if vertical else 0.052)), "ExtraBold"),
        (pad, y, w - 2 * pad),
        INK,
        line_gap=14,
        center=True,
    )
    y += int(h * 0.02)
    y += draw_block(
        draw,
        "Formu doldurun, gerisini biz halledelim.",
        font(int(w * (0.036 if vertical else 0.03)), "Medium"),
        (pad, y, w - 2 * pad),
        MUTED,
        line_gap=12,
        center=True,
    )

    y += int(h * (0.05 if vertical else 0.04))
    site_font = font(int(w * (0.056 if vertical else 0.046)), "ExtraBold")
    bw = draw.textlength(SITE, font=site_font) + 72
    bh = site_font.size + 46
    rounded(draw, ((w - bw) / 2, y, (w + bw) / 2, y + bh), bh / 2, GOLD, None, 0)
    draw.text(((w - draw.textlength(SITE, font=site_font)) / 2, y + 22), SITE, font=site_font, fill=CARD)
    y += bh + int(h * 0.035)

    info_font = font(int(w * (0.036 if vertical else 0.03)), "SemiBold")
    for line in (f"WhatsApp / Telefon: {PHONE}", "TÜRSAB üyesi A Grubu seyahat acentesi iş birliğiyle"):
        draw.text(((w - draw.textlength(line, font=info_font)) / 2, y), line, font=info_font, fill=INK)
        y += info_font.size + 18

    content = layer.crop((0, 0, w, y))
    canvas.paste(content, (0, max(0, (h - y) // 2)), content)
    return canvas


def run(cmd: list) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr[-2500:])
        raise SystemExit(f"ffmpeg hatası: {' '.join(cmd[:6])}...")


def build(size: tuple, out_path: str, outro_sec: float = 4.2) -> None:
    w, h = size
    timeline = json.load(open(os.path.join(AUDIO, "full.json")))
    scenes = timeline["scenes"]
    work = tempfile.mkdtemp(prefix="reklam_")
    clips = []

    for i, scene in enumerate(scenes):
        frame_path = os.path.join(work, f"frame_{i}.png")
        scene_frame(scene["key"], i, len(scenes), size).save(frame_path)
        duration = round(float(scene["end"]) - float(scene["start"]), 3)
        clip = os.path.join(work, f"clip_{i}.mp4")
        run(
            [
                "ffmpeg", "-y", "-loop", "1", "-i", frame_path, "-t", f"{duration}",
                "-vf",
                (
                    "zoompan=z='min(zoom+0.00035,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                    f":d=1:s={w}x{h}:fps=30,fade=t=in:st=0:d=0.4,format=yuv420p"
                ),
                "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-r", "30", clip,
            ]
        )
        clips.append(clip)

    outro_path = os.path.join(work, "frame_outro.png")
    outro_frame(size).save(outro_path)
    outro_clip = os.path.join(work, "clip_outro.mp4")
    run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", outro_path, "-t", f"{outro_sec}",
            "-vf",
            (
                "zoompan=z='min(zoom+0.0003,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d=1:s={w}x{h}:fps=30,fade=t=in:st=0:d=0.5,fade=t=out:st={outro_sec - 0.6}:d=0.6,format=yuv420p"
            ),
            "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-r", "30", outro_clip,
        ]
    )
    clips.append(outro_clip)

    list_file = os.path.join(work, "clips.txt")
    with open(list_file, "w") as fh:
        for clip in clips:
            fh.write(f"file '{clip}'\n")

    silent = os.path.join(work, "video.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", silent])

    total = round(float(timeline["duration"]) + outro_sec, 3)
    audio = os.path.join(work, "audio.m4a")
    run(
        [
            "ffmpeg", "-y", "-i", os.path.join(AUDIO, "full.mp3"),
            "-af", f"apad=pad_dur={outro_sec + 1},afade=t=out:st={total - 1.6}:d=1.4",
            "-t", f"{total}", "-c:a", "aac", "-b:a", "128k", audio,
        ]
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    run(
        [
            "ffmpeg", "-y", "-i", silent, "-i", audio,
            "-c:v", "libx264", "-preset", "medium", "-crf", "25",
            "-maxrate", "2200k", "-bufsize", "4400k",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest", out_path,
        ]
    )
    shutil.rmtree(work, ignore_errors=True)
    mb = os.path.getsize(out_path) / 1_048_576
    print(f"{out_path} · {total:.1f} sn · {mb:.1f} MB")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "dikey"):
        build((1080, 1920), os.path.join(OUT_DIR, "dubai-vize-hatti-reklam-dikey.mp4"))
    if which in ("all", "kare"):
        build((1080, 1080), os.path.join(OUT_DIR, "dubai-vize-hatti-reklam-kare.mp4"))
