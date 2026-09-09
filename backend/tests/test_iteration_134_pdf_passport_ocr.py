"""Iteration 134: PDF pasaport okuma + okunan bilgilerin alanlari guncellemesi.

Kullanici sikayeti: "pasaportu otomatik okuyup formu doldurmuyor" (PDF yuklenmisti) ve
"adi yanlis gorunuyor" (yeni pasaport okundugu halde eski ad/soyad formda kaliyordu).

Bu dosya backend tarafini dogrular:
- PDF artik reddedilmiyor (eski davranis: reason="pdf"), sayfalar goruntuye cevriliyor,
- sahte ama gecerli bicimli bir pasaport PDF'inden ad/soyad/pasaport no okunuyor,
- ayni belgenin PNG hali ile PDF hali ayni alanlari veriyor,
- ocr_metrics kaydi her denemede yaziliyor.
"""

import io
import os

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
API = f"{BASE_URL}/api"


def _font(size: int, mono: bool = False):
    from PIL import ImageFont

    path = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
        if mono
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    )
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _mock_passport_image():
    """Test icin sahte pasaport kimlik sayfasi (gercek pasaport goruntusu kullanilmaz)."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (1240, 875), (233, 226, 214))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1240, 90], fill=(196, 32, 44))
    d.text((40, 28), "TÜRKİYE CUMHURİYETİ / REPUBLIC OF TÜRKİYE", font=_font(30), fill=(255, 255, 255))
    d.text((40, 110), "PASAPORT / PASSPORT", font=_font(26), fill=(40, 40, 40))
    d.rectangle([40, 170, 330, 560], fill=(205, 198, 186), outline=(120, 120, 120), width=2)
    d.ellipse([120, 240, 250, 380], fill=(170, 160, 148))
    d.rectangle([110, 400, 260, 540], fill=(170, 160, 148))

    rows = [
        ("Type / Tipi", "P"),
        ("Passport No / Pasaport No", "U12345678"),
        ("Surname / Soyadı", "YILMAZ"),
        ("Given names / Adı", "AYSE"),
        ("Nationality / Uyruğu", "T.C. / TUR"),
        ("Date of birth / Doğum tarihi", "01.01.1990"),
        ("Sex / Cinsiyeti", "F / K"),
        ("Place of birth / Doğum yeri", "ISTANBUL"),
        ("Date of issue / Veriliş tarihi", "15.03.2022"),
        ("Date of expiry / Geçerlilik", "15.03.2032"),
        ("Authority / Veren makam", "ISTANBUL VALILIGI"),
    ]
    y = 175
    for label, value in rows:
        d.text((370, y), label, font=_font(15), fill=(105, 105, 105))
        d.text((370, y + 20), value, font=_font(24), fill=(20, 20, 20))
        y += 62
    d.rectangle([0, 700, 1240, 875], fill=(240, 236, 228))
    d.text((45, 745), "P<TURYILMAZ<<AYSE<<<<<<<<<<<<<<<<<<<<<<<<<<<", font=_font(30, True), fill=(20, 20, 20))
    d.text((45, 800), "U123456782TUR9001014F3203155<<<<<<<<<<<<<<02", font=_font(30, True), fill=(20, 20, 20))
    return img


def _mock_bytes(fmt: str) -> bytes:
    buf = io.BytesIO()
    if fmt == "pdf":
        _mock_passport_image().save(buf, "PDF", resolution=170)
    else:
        _mock_passport_image().save(buf, "PNG")
    return buf.getvalue()


def _upload(name: str, data: bytes, mime: str) -> str:
    r = requests.post(
        f"{API}/uploads",
        files={"file": (name, data, mime)},
        data={"doc_type": "passport"},
        timeout=60,
    )
    assert r.status_code == 200, r.text
    return r.json()["file_id"]


def _read(file_id: str) -> dict:
    r = requests.post(f"{API}/passport/read", data={"file_id": file_id}, timeout=120)
    if r.status_code == 429:
        pytest.skip("passport OCR IP limiti doldu")
    assert r.status_code == 200, r.text
    return r.json()


@pytest.fixture(scope="module")
def pdf_result():
    return _read(_upload("pasaport.pdf", _mock_bytes("pdf"), "application/pdf"))


def test_pdf_artik_reddedilmiyor(pdf_result):
    assert pdf_result.get("reason") != "pdf"
    assert "PDF dosyalari otomatik okunamiyor" not in (pdf_result.get("message") or "")


def test_pdf_pasaportu_okunuyor(pdf_result):
    assert pdf_result.get("ok") is True, pdf_result
    data = pdf_result["data"]
    assert data["last_name"].upper().startswith("YILMAZ")
    assert "AYSE" in data["first_name"].upper() or "AYŞE" in data["first_name"].upper()
    assert data["passport_no"].upper() == "U12345678"
    assert data["is_passport"] is True
    assert pdf_result["filled_count"] >= 4


def test_png_ve_pdf_ayni_kisiyi_veriyor(pdf_result):
    png = _read(_upload("pasaport.png", _mock_bytes("png"), "image/png"))
    assert png.get("ok") is True, png
    assert png["data"]["passport_no"] == pdf_result["data"]["passport_no"]
    assert png["data"]["last_name"].upper() == pdf_result["data"]["last_name"].upper()


def test_bozuk_pdf_zarif_hata(pdf_result):
    """Pasaport olmayan/bozuk PDF akisi kirmadan hata donmeli."""
    body = _read(_upload("bos.pdf", b"%PDF-1.4\n%bozuk\n", "application/pdf"))
    assert body.get("ok") is False
    assert body.get("reason") in ("ai_error", "not_readable")


def test_metrics_kaydi_yazildi(pdf_result):
    r = requests.get(f"{API}/health", timeout=30)
    assert r.status_code == 200
    # kapsam raporu admin ucunda; burada en az bir deneme kaydi olustugunu dogruluyoruz
    from pymongo import MongoClient

    mongo_url = db_name = None
    with open("/app/backend/.env") as fh:
        for line in fh:
            if line.startswith("MONGO_URL="):
                mongo_url = line.split("=", 1)[1].strip().strip('"')
            if line.startswith("DB_NAME="):
                db_name = line.split("=", 1)[1].strip().strip('"')
    client = MongoClient(mongo_url)
    try:
        assert client[db_name]["ocr_metrics"].count_documents({}) > 0
    finally:
        client.close()
