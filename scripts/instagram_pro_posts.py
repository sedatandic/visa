"""Instagram gonderileri: gercek Dubai fotografi + editorial tipografi (1080x1350).

Girdi : /app/frontend/public/instagram/photos/src-XX.jpg
Cikti : /app/frontend/public/instagram/post-XX.jpg + grid-preview.jpg
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

SRC = Path("/app/frontend/public/instagram/photos")
OUT = Path("/app/frontend/public/instagram")
LOGO = Path("/app/frontend/public/brand/logo-horizontal-gold.png")
ANTON = "/app/scripts/fonts/Anton.ttf"
FIGTREE = "/app/scripts/fonts/Figtree.ttf"

W, H = 1080, 1350
NAVY = (11, 26, 38)
GOLD = (232, 159, 32)
CREAM = (246, 241, 232)
WHITE = (255, 255, 255)
WHATSAPP = (37, 211, 102)

BAR_H = 108
MARGIN = 60
DOMAIN = "dubaivizehatti.com"
PHONE = "+90 538 483 82 24"


def anton(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(ANTON, size)


def figtree(size: int, weight: str = "Bold") -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(FIGTREE, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def cover(path: Path, box: tuple, focus: float = 0.5) -> Image.Image:
    """Fotografi kutuya kirpar (cover), dikey odak noktasi focus (0=ust, 1=alt)."""
    bw, bh = box
    img = Image.open(path).convert("RGB")
    scale = max(bw / img.width, bh / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    top = int((img.height - bh) * focus)
    left = (img.width - bw) // 2
    return img.crop((left, top, left + bw, top + bh))


def scrim(img: Image.Image, stops: list) -> Image.Image:
    """stops: [(y_orani, alpha)] -> lacivert degrade perde."""
    h = img.height
    mask = Image.new("L", (1, h))
    px = mask.load()
    pts = [(int(r * (h - 1)), a) for r, a in stops]
    for i in range(len(pts) - 1):
        (y0, a0), (y1, a1) = pts[i], pts[i + 1]
        for y in range(y0, y1 + 1):
            t = 0 if y1 == y0 else (y - y0) / (y1 - y0)
            px[0, y] = int(a0 + (a1 - a0) * t)
    mask = mask.resize((img.width, h))
    layer = Image.new("RGB", img.size, NAVY)
    return Image.composite(layer, img, mask.point(lambda v: v))


def graded(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Color(img).enhance(0.88)
    return ImageEnhance.Contrast(img).enhance(1.06)


def wrap(draw, text: str, font, max_w: int) -> list:
    lines, line = [], ""
    for word in text.split():
        probe = f"{line} {word}".strip()
        if draw.textlength(probe, font=font) <= max_w or not line:
            line = probe
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit_lines(draw, text: str, max_w: int, max_lines: int, start: int, min_size: int):
    size = start
    while size > min_size:
        font = anton(size)
        lines = wrap(draw, text, font, max_w)
        if len(lines) <= max_lines:
            return font, lines
        size -= 4
    font = anton(min_size)
    return font, wrap(draw, text, font, max_w)


def tracked(draw, xy, text: str, font, fill, tracking: int = 4) -> None:
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def uae_flag(width: int, height: int) -> Image.Image:
    flag = Image.new("RGBA", (width, height), WHITE + (255,))
    d = ImageDraw.Draw(flag)
    bar, third = int(width * 0.3), height / 3
    d.rectangle([bar, 0, width, third], fill=(0, 115, 47))
    d.rectangle([bar, third, width, 2 * third], fill=(255, 255, 255))
    d.rectangle([bar, 2 * third, width, height], fill=(0, 0, 0))
    d.rectangle([0, 0, bar, height], fill=(206, 17, 38))
    mask = Image.new("L", flag.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1, height - 1], 5, fill=255)
    flag.putalpha(mask)
    return flag


def header(canvas: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    logo = Image.open(LOGO).convert("RGBA")
    logo_h = 74
    logo = logo.resize((round(logo.width * logo_h / logo.height), logo_h), Image.LANCZOS)
    canvas.paste(logo, (MARGIN - 8, 46), logo)

    flag = uae_flag(56, 38)
    canvas.paste(flag, (MARGIN - 8 + logo.width + 22, 46 + (logo_h - flag.height) // 2), flag)

    badge_font = figtree(21, "Bold")
    label = "TÜRSAB BELGELİ"
    tw = draw.textlength(label, font=badge_font) + 3 * len(label)
    pw, ph = int(tw) + 44, 46
    px, py = W - MARGIN - pw + 8, 46 + (logo_h - ph) // 2
    draw.rounded_rectangle([px, py, px + pw, py + ph], ph // 2, outline=GOLD, width=2)
    tracked(draw, (px + 22, py + 12), label, badge_font, GOLD, 3)


def footer(draw: ImageDraw.ImageDraw) -> None:
    top = H - BAR_H
    draw.rectangle([0, top, W, H], fill=NAVY)
    draw.rectangle([0, top - 3, W, top], fill=GOLD)

    draw.text((MARGIN, top + 32), DOMAIN, font=figtree(36, "Bold"), fill=GOLD)

    pill_font = figtree(27, "Bold")
    text = f"WhatsApp  {PHONE}"
    pw = int(draw.textlength(text, font=pill_font)) + 52
    ph = 60
    px = W - MARGIN - pw
    py = top + (BAR_H - ph) // 2
    draw.rounded_rectangle([px, py, px + pw, py + ph], ph // 2, fill=WHATSAPP)
    draw.text((px + 26, py + 15), text, font=pill_font, fill=WHITE)


def eyebrow(draw: ImageDraw.ImageDraw, y: int, text: str) -> int:
    draw.rectangle([MARGIN, y + 12, MARGIN + 46, y + 16], fill=GOLD)
    tracked(draw, (MARGIN + 66, y), text, figtree(25, "Bold"), GOLD, 5)
    return y + 46


def check_icon(draw: ImageDraw.ImageDraw, x: int, y: int, size: int = 34) -> None:
    draw.ellipse([x, y, x + size, y + size], fill=GOLD)
    draw.line(
        [(x + size * 0.26, y + size * 0.53), (x + size * 0.44, y + size * 0.71),
         (x + size * 0.76, y + size * 0.32)],
        fill=NAVY, width=4, joint="curve",
    )


def hero(post: dict) -> Image.Image:
    photo = graded(cover(SRC / post["src"], (W, H), post.get("focus", 0.5)))
    canvas = scrim(photo, [(0.0, 165), (0.26, 40), (0.44, 60), (0.70, 232), (1.0, 252)])
    canvas = canvas.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    header(canvas, draw)

    sub_font = figtree(33, "Medium")
    sub_lines = wrap(draw, post["sub"], sub_font, W - 2 * MARGIN - 30)
    head_font, head_lines = fit_lines(draw, post["head"], W - 2 * MARGIN - 20, 3, 104, 62)

    sub_h = len(sub_lines) * 46
    head_h = int(len(head_lines) * head_font.size * 1.0)
    block_bottom = H - BAR_H - 66
    head_top = block_bottom - sub_h - 28 - head_h
    eyebrow_y = head_top - 62

    eyebrow(draw, eyebrow_y, post["eyebrow"])

    y = head_top
    for line in head_lines:
        draw.text((MARGIN, y), line, font=head_font, fill=WHITE)
        y += int(head_font.size * 1.0)

    y += 28
    for line in sub_lines:
        draw.text((MARGIN, y), line, font=sub_font, fill=CREAM)
        y += 46

    footer(draw)
    return canvas


def band(post: dict) -> Image.Image:
    """Yatay fotograflar icin: ustte fotograf, altta lacivert metin bandi."""
    photo_h = 820
    photo = graded(cover(SRC / post["src"], (W, photo_h), post.get("focus", 0.5)))
    photo = scrim(photo, [(0.0, 150), (0.28, 25), (0.82, 30), (1.0, 110)])

    canvas = Image.new("RGB", (W, H), NAVY)
    canvas.paste(photo, (0, 0))
    draw = ImageDraw.Draw(canvas)
    header(canvas, draw)

    y = eyebrow(draw, photo_h + 46, post["eyebrow"])
    head_font, head_lines = fit_lines(draw, post["head"], W - 2 * MARGIN, 2, 76, 50)
    for line in head_lines:
        draw.text((MARGIN, y + 6), line, font=head_font, fill=WHITE)
        y += int(head_font.size * 1.02)

    y += 22
    sub_font = figtree(31, "Medium")
    for line in wrap(draw, post["sub"], sub_font, W - 2 * MARGIN - 20)[:2]:
        draw.text((MARGIN, y), line, font=sub_font, fill=CREAM)
        y += 44

    footer(draw)
    return canvas


def panel(post: dict) -> Image.Image:
    photo_h = 760
    photo = graded(cover(SRC / post["src"], (W, photo_h), post.get("focus", 0.5)))
    photo = scrim(photo, [(0.0, 150), (0.30, 30), (0.80, 40), (1.0, 120)])

    canvas = Image.new("RGB", (W, H), NAVY)
    canvas.paste(photo, (0, 0))
    draw = ImageDraw.Draw(canvas)
    header(canvas, draw)

    numbered = post.get("kind") == "steps"
    y = eyebrow(draw, photo_h + 44, post["eyebrow"])
    head_font, head_lines = fit_lines(draw, post["head"], W - 2 * MARGIN, 2, 72, 48)
    for line in head_lines:
        draw.text((MARGIN, y + 6), line, font=head_font, fill=WHITE)
        y += int(head_font.size * 1.02)

    y += 26
    item_font = figtree(31, "SemiBold")
    num_font = anton(28)
    for i, item in enumerate(post["items"]):
        if numbered:
            draw.rounded_rectangle([MARGIN, y - 2, MARGIN + 40, y + 38], 10, fill=GOLD)
            n = f"{i + 1}"
            draw.text(
                (MARGIN + 20 - draw.textlength(n, font=num_font) / 2, y + 3),
                n, font=num_font, fill=NAVY,
            )
        else:
            check_icon(draw, MARGIN, y + 1)
        draw.text((MARGIN + 60, y + 2), item, font=item_font, fill=CREAM)
        y += 62

    footer(draw)
    return canvas


POSTS = [
    {
        "id": "post-01", "src": "src-01.jpg", "kind": "hero", "focus": 0.45,
        "eyebrow": "DUBAİ VİZESİ",
        "head": "VİZENİZ 36 SAATTE HAZIR",
        "sub": "Sadece pasaport ve fotoğraf yeterli. Otel ya da bilet istemiyoruz.",
    },
    {
        "id": "post-02", "src": "src-02.jpg", "kind": "list", "focus": 0.5,
        "eyebrow": "GEREKLİ BELGELER",
        "head": "TEK İHTİYACIMIZ İKİ BELGE",
        "items": [
            "Pasaportunuzun ana sayfası",
            "Bir vesikalık fotoğraf",
            "3 dakikalık online form",
        ],
    },
    {
        "id": "post-03", "src": "src-03.jpg", "kind": "hero", "focus": 0.4,
        "eyebrow": "YAZILI TAAHHÜT",
        "head": "36 SAAT GARANTİSİ",
        "sub": "Süre aşılırsa ekspres hizmet bedelini iade ediyoruz. Geri sayım ekranınızda.",
    },
    {
        "id": "post-04", "src": "src-04.jpg", "kind": "band", "focus": 0.45,
        "eyebrow": "KOLAY BAŞVURU",
        "head": "OTEL VE BİLET GEREKMEZ",
        "sub": "Planınız netleşmeden başvurun; vizeniz hazır olarak sizi bekler.",
    },
    {
        "id": "post-05", "src": "src-05.jpg", "kind": "list", "focus": 0.62,
        "eyebrow": "AİLE BAŞVURUSU",
        "head": "TÜM AİLE TEK FORMDA",
        "items": [
            "Eş ve çocuklar aynı başvuruda",
            "Aile başvurusuna özel indirim",
            "Herkesin vizesi aynı anda çıkar",
        ],
    },
    {
        "id": "post-06", "src": "src-06.jpg", "kind": "hero", "focus": 0.62,
        "eyebrow": "SEYAHAT SAĞLIK SİGORTASI",
        "head": "DUBAİ'DE SAĞLIK PAHALI",
        "sub": "Poliçenizi vize başvurunuzla birlikte, tek adımda alın.",
    },
    {
        "id": "post-07", "src": "src-07.jpg", "kind": "hero", "focus": 0.4,
        "eyebrow": "DUBAİ eSIM",
        "head": "İNER İNMEZ İNTERNET",
        "sub": "QR kodunuz e-posta ile gelir. Kart değiştirmek, sıra beklemek yok.",
    },
    {
        "id": "post-08", "src": "src-08.jpg", "kind": "list", "focus": 0.45,
        "eyebrow": "CANLI TAKİP",
        "head": "BAŞVURUNUZ NEREDE?",
        "items": [
            "Takip kodunuzla anlık durum",
            "36 saatlik geri sayım ekranda",
            "Her adımda WhatsApp bildirimi",
        ],
    },
    {
        "id": "post-09", "src": "src-09.jpg", "kind": "list", "focus": 0.5,
        "eyebrow": "GÜVENCE",
        "head": "TÜRSAB BELGELİ ACENTE",
        "items": [
            "Yetkili seyahat acentesi",
            "Güvenli ödeme altyapısı",
            "Faturalı ve kayıtlı işlem",
        ],
    },
    {
        "id": "post-10", "src": "src-10.jpg", "kind": "band", "focus": 0.5,
        "eyebrow": "ÇÖL SAFARİSİ",
        "head": "ÇÖLÜ GÖRMEDEN DÖNMEYİN",
        "sub": "Otelden alış, kum tepelerinde sürüş, akşam yemeği ve gösteri dahil.",
    },
    {
        "id": "post-11", "src": "src-11.jpg", "kind": "band", "focus": 0.5,
        "eyebrow": "EN ÇOK SORULAN",
        "head": "\u201cVİZEM REDDEDİLİRSE?\u201d",
        "sub": "İade koşullarımız sitemizde açık yazılı. Gizli ücret yok.",
    },
    {
        "id": "post-12", "src": "src-12.jpg", "kind": "steps", "focus": 0.5,
        "eyebrow": "NASIL ÇALIŞIR",
        "head": "3 ADIMDA DUBAİ VİZESİ",
        "items": [
            "Formu doldur (3 dakika)",
            "Pasaport ve fotoğrafını yükle",
            "Vizeni e-posta ve WhatsApp'tan al",
        ],
    },
]


def main() -> None:
    thumbs = []
    builders = {"hero": hero, "band": band}
    for post in POSTS:
        img = builders.get(post["kind"], panel)(post)
        out = OUT / f"{post['id']}.jpg"
        img.save(out, quality=88, optimize=True, progressive=True)
        thumbs.append(img.resize((270, 338), Image.LANCZOS))
        print("hazir:", out.name, f"{out.stat().st_size // 1024} KB")

    grid = Image.new("RGB", (270 * 3 + 16, 338 * 4 + 24), (240, 240, 240))
    for i, thumb in enumerate(thumbs):
        grid.paste(thumb, ((i % 3) * 274 + 4, (i // 3) * 342 + 4))
    grid.save("/tmp/instagram-grid.jpg", quality=80)
    print("grid: /tmp/instagram-grid.jpg")


main()
