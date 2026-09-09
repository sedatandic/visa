"""Instagram gonderilerine marka cercevesi ekler (logo, BAE bayragi, alan adi, WhatsApp).

Girdi : /app/frontend/public/instagram/raw/post-XX.jpg  (ham illustrasyon, 1024x1024)
Cikti : /app/frontend/public/instagram/post-XX.jpg      (1080x1350, 4:5 Instagram)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAW_DIR = Path("/app/frontend/public/instagram/raw")
OUT_DIR = Path("/app/frontend/public/instagram")
LOGO = Path("/app/frontend/public/brand/logo-horizontal-gold.png")
FONT = "/app/scripts/fonts/Figtree.ttf"

W, H = 1080, 1350
NAVY = (16, 32, 44)
GOLD = (232, 159, 32)
CREAM = (251, 246, 236)
WHATSAPP = (37, 211, 102)
ART = 1000
ART_TOP = 196

DOMAIN = "dubaivizehatti.com"
PHONE = "+90 538 483 82 24"


def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(FONT, size)
    if bold:
        try:
            f.set_variation_by_name("Bold")
        except Exception:
            pass
    return f


def rounded(img: Image.Image, radius: int) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1], radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def uae_flag(width: int, height: int) -> Image.Image:
    """Birlesik Arap Emirlikleri bayragi (kirmizi dikey + yesil/beyaz/siyah yatay)."""
    flag = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    d = ImageDraw.Draw(flag)
    bar = int(width * 0.3)
    third = height / 3
    d.rectangle([bar, 0, width, third], fill=(0, 115, 47))
    d.rectangle([bar, third, width, 2 * third], fill=(255, 255, 255))
    d.rectangle([bar, 2 * third, width, height], fill=(0, 0, 0))
    d.rectangle([0, 0, bar, height], fill=(206, 17, 38))
    return rounded(flag, 6)


def build(raw_path: Path, out_path: Path) -> None:
    canvas = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(canvas)

    # --- ust bant: logo + bayrak/DUBAI
    logo = Image.open(LOGO).convert("RGBA")
    logo_h = 104
    logo = logo.resize((int(logo.width * logo_h / logo.height), logo_h), Image.LANCZOS)
    canvas.paste(logo, (44, 52), logo)

    flag = uae_flag(78, 54)
    canvas.paste(flag, (W - 44 - flag.width, 56), flag)
    label = font(30)
    text = "DUBAI"
    tw = draw.textlength(text, font=label)
    draw.text((W - 44 - flag.width - 16 - tw, 68), text, font=label, fill=CREAM)

    # --- orta: illustrasyon
    art = Image.open(raw_path).convert("RGB").resize((ART, ART), Image.LANCZOS)
    canvas.paste(rounded(art, 34), ((W - ART) // 2, ART_TOP), rounded(art, 34))

    # --- alt bant: alan adi + WhatsApp
    base_y = ART_TOP + ART + 30
    domain_font = font(40)
    draw.text((46, base_y + 24), DOMAIN, font=domain_font, fill=GOLD)

    pill_font = font(34)
    pill_text = f"WhatsApp  {PHONE}"
    pw = draw.textlength(pill_text, font=pill_font)
    pill_w, pill_h = int(pw) + 56, 74
    pill_x = W - 46 - pill_w
    draw.rounded_rectangle(
        [pill_x, base_y + 8, pill_x + pill_w, base_y + 8 + pill_h], pill_h // 2, fill=WHATSAPP
    )
    draw.text((pill_x + 28, base_y + 28), pill_text, font=pill_font, fill=(255, 255, 255))

    canvas.save(out_path, quality=92, optimize=True)


def main() -> None:
    for raw in sorted(RAW_DIR.glob("post-*.jpg")):
        out = OUT_DIR / raw.name
        build(raw, out)
        print("hazir:", out.name)


main()
