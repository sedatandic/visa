from PIL import Image, ImageDraw, ImageFont

img = Image.new("RGB", (1000, 260), (16, 32, 44))
d = ImageDraw.Draw(img)
a = ImageFont.truetype("/app/scripts/fonts/Anton.ttf", 80)
f = ImageFont.truetype("/app/scripts/fonts/Figtree.ttf", 70)
try:
    f.set_variation_by_name("Black")
except Exception:
    f.set_variation_by_name("Bold")
d.text((30, 20), "VİZENİZ 36 SAATTE HAZIR ışğçöü", font=a, fill=(255, 255, 255))
d.text((30, 140), "VİZENİZ 36 SAATTE HAZIR ışğçöü", font=f, fill=(232, 159, 32))
img.save("/tmp/glyphtest.png")
print("ok")
