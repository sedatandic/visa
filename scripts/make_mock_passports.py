#!/usr/bin/env python3
"""Test icin sahte pasaport kimlik sayfalari uretir (gercek belge kullanilmaz).

Cikti: /app/test_assets/passport_a.png|pdf (AYSE YILMAZ) ve
       /app/test_assets/passport_b.png|pdf (EKREM SAYANER)
Kullanim: python /app/scripts/make_mock_passports.py
"""
import pathlib

from PIL import Image, ImageDraw, ImageFont

OUT = pathlib.Path("/app/test_assets")
OUT.mkdir(parents=True, exist_ok=True)

PEOPLE = {
    "a": {
        "surname": "YILMAZ",
        "given": "AYSE",
        "passport_no": "U12345678",
        "birth": "01.01.1990",
        "sex": "F / K",
        "expiry": "15.03.2032",
        "issue": "15.03.2022",
        "birth_place": "ISTANBUL",
        "mrz1": "P<TURYILMAZ<<AYSE<<<<<<<<<<<<<<<<<<<<<<<<<<<",
        "mrz2": "U123456782TUR9001014F3203155<<<<<<<<<<<<<<02",
    },
    "b": {
        "surname": "SAYANER",
        "given": "EKREM",
        "passport_no": "U22581619",
        "birth": "24.08.1995",
        "sex": "M / E",
        "expiry": "07.11.2029",
        "issue": "07.11.2019",
        "birth_place": "ANKARA",
        "mrz1": "P<TURSAYANER<<EKREM<<<<<<<<<<<<<<<<<<<<<<<<<",
        "mrz2": "U225816193TUR9508243M2911075<<<<<<<<<<<<<<04",
    },
}


def font(size: int, mono: bool = False):
    path = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
        if mono
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    )
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def build(p: dict) -> Image.Image:
    img = Image.new("RGB", (1240, 875), (233, 226, 214))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1240, 90], fill=(196, 32, 44))
    d.text((40, 28), "TÜRKİYE CUMHURİYETİ / REPUBLIC OF TÜRKİYE", font=font(30), fill=(255, 255, 255))
    d.text((40, 110), "PASAPORT / PASSPORT", font=font(26), fill=(40, 40, 40))
    d.rectangle([40, 170, 330, 560], fill=(205, 198, 186), outline=(120, 120, 120), width=2)
    d.ellipse([120, 240, 250, 380], fill=(170, 160, 148))
    d.rectangle([110, 400, 260, 540], fill=(170, 160, 148))

    rows = [
        ("Type / Tipi", "P"),
        ("Passport No / Pasaport No", p["passport_no"]),
        ("Surname / Soyadı", p["surname"]),
        ("Given names / Adı", p["given"]),
        ("Nationality / Uyruğu", "T.C. / TUR"),
        ("Date of birth / Doğum tarihi", p["birth"]),
        ("Sex / Cinsiyeti", p["sex"]),
        ("Place of birth / Doğum yeri", p["birth_place"]),
        ("Date of issue / Veriliş tarihi", p["issue"]),
        ("Date of expiry / Geçerlilik", p["expiry"]),
        ("Authority / Veren makam", "IL EMNIYET MUDURLUGU"),
    ]
    y = 175
    for label, value in rows:
        d.text((370, y), label, font=font(15), fill=(105, 105, 105))
        d.text((370, y + 20), value, font=font(24), fill=(20, 20, 20))
        y += 62

    d.rectangle([0, 700, 1240, 875], fill=(240, 236, 228))
    d.text((45, 745), p["mrz1"], font=font(30, True), fill=(20, 20, 20))
    d.text((45, 800), p["mrz2"], font=font(30, True), fill=(20, 20, 20))
    return img


for key, person in PEOPLE.items():
    image = build(person)
    image.save(OUT / f"passport_{key}.png")
    image.save(OUT / f"passport_{key}.pdf", "PDF", resolution=170)
    print(f"yazildi: passport_{key}.png / passport_{key}.pdf ({person['given']} {person['surname']})")
