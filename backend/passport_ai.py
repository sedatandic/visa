"""Pasaport goruntusunden yapay zeka ile veri cikarma (Emergent LLM key)."""
import base64
import io
import json
import logging
import os
import re
import uuid
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-5.4"

SYSTEM_PROMPT = (
    "Sen pasaport belgelerini okuyan bir OCR asistanisin. Sana verilen goruntu bir pasaportun "
    "kimlik bilgileri sayfasidir. Goruntudeki MRZ (alt kisimdaki iki satirlik makine okunabilir alan) "
    "ve yazili alanlari kullanarak bilgileri cikar. SADECE gecerli JSON dondur, aciklama yazma."
)

USER_PROMPT = """Bu pasaport goruntusunden asagidaki alanlari cikar ve tam olarak su JSON semasinda dondur:

{
  "first_name": "verilen adlar (buyuk harf, Turkce karakter kullanma)",
  "last_name": "soyad (buyuk harf, Turkce karakter kullanma)",
  "passport_no": "pasaport numarasi",
  "birth_date": "YYYY-MM-DD",
  "passport_expiry": "YYYY-MM-DD",
  "gender": "male veya female",
  "nationality": "ISO 3166-1 alpha-2 ulke kodu, orn. TR",
  "national_id": "varsa T.C. kimlik numarasi, yoksa bos string",
  "passport_issue_date": "pasaportun verilis/duzenlenme tarihi YYYY-MM-DD, okunamazsa bos string",
  "birth_place": "dogum yeri (sehir/il, buyuk harf, Turkce karakter kullanma), okunamazsa bos",
  "passport_issue_place": "pasaportu veren makam/yer (orn. ANKARA), okunamazsa bos string",
  "mrz": "okunabildiyse MRZ satirlari, yoksa bos string",
  "confidence": 0.0 ile 1.0 arasinda okuma guveni,
  "is_passport": true veya false (goruntu bir pasaport sayfasi degilse false)
}

Kurallar:
- Tarihleri mutlaka YYYY-MM-DD formatinda ver. MRZ'deki YYMMDD formatini dogru yuzyila cevir
  (dogum tarihi icin gelecek tarih olamaz, gecerlilik tarihi icin genelde 20xx).
- Cinsiyet MRZ'de M ise "male", F ise "female".
- national_id: Turk pasaportlarinda "T.C. Kimlik No / ID No" alaninda 11 haneli bir numara yazar.
  Bu alan gorunmuyorsa MRZ'nin IKINCI satirindaki kisisel numara bolumunde (gecerlilik tarihinden
  sonra gelen rakam grubu) 11 haneli numarayi ara ve oradan al. Sadece 11 rakamdan olusmali.
- passport_issue_place: "Veren Makam / Veren Kurum / Authority / Issuing Authority" alanindaki
  kurum veya sehir adini yaz (orn. "ISTANBUL VALILIGI" icin ISTANBUL). Yalnizca gercekten
  okunamiyorsa bos birak.
- Emin olmadigin alanlari bos string birak, uydurma.
- Sadece JSON dondur."""


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _prepare_image(data: bytes, content_type: str) -> tuple[str, str]:
    """Buyuk goruntuleri kucultup JPEG'e cevirir; (base64, mime) dondurur."""
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(data))
        if getattr(img, "is_animated", False):
            img.seek(0)
        img = img.convert("RGB")
        max_side = 1600
        if max(img.size) > max_side:
            ratio = max_side / max(img.size)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=88)
        return _b64(buf.getvalue()), "image/jpeg"
    except Exception as exc:  # pragma: no cover
        logger.warning("passport image prepare failed, using raw bytes: %s", exc)
        return _b64(data), content_type or "image/jpeg"


def _is_pdf(data: bytes, content_type: str) -> bool:
    return (content_type or "").lower() == "application/pdf" or data[:4] == b"%PDF"


def _pdf_page_images(data: bytes, max_pages: int = 2) -> list:
    """PDF sayfalarini goruntuye cevirir (pasaport taramalari sik sik PDF gelir)."""
    import pymupdf

    images = []
    with pymupdf.open(stream=data, filetype="pdf") as doc:
        for index, page in enumerate(doc):
            if index >= max_pages:
                break
            images.append(page.get_pixmap(dpi=170).tobytes("png"))
    return images


def _prepare_images(data: bytes, content_type: str) -> list:
    """LLM'e gonderilecek base64 goruntuler. PDF ise ilk sayfalar goruntuye cevrilir."""
    if _is_pdf(data, content_type):
        pages = _pdf_page_images(data)
        if not pages:
            raise ValueError("PDF sayfasi goruntuye cevrilemedi.")
        return [_prepare_image(page, "image/png")[0] for page in pages]
    return [_prepare_image(data, content_type)[0]]


def _extract_json(text: str) -> dict:
    if not text:
        return {}
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", cleaned, re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                return {}
    return {}


def _normalize_date(value: str) -> str:
    if not value or not isinstance(value, str):
        return ""
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def _clean_name(value: str) -> str:
    if not value or not isinstance(value, str):
        return ""
    return re.sub(r"[^A-Za-zÇĞİÖŞÜçğıöşü\s'-]", "", value).strip().upper()


GENDER_ALIASES = {
    "m": "male",
    "male": "male",
    "erkek": "male",
    "f": "female",
    "female": "female",
    "kadin": "female",
    "kadın": "female",
}


def _normalize_gender(value) -> str:
    """Model cikisindaki cinsiyet ifadesini male/female/"" degerine indirger."""
    return GENDER_ALIASES.get((value or "").strip().lower(), "")


def _normalize_national_id(value) -> str:
    """TC kimlik no yalnizca 11 haneli ise kabul edilir."""
    digits = re.sub(r"\D", "", str(value or ""))
    return digits if len(digits) == 11 else ""


def _normalize_code(value) -> str:
    """Pasaport no gibi kodlari harf/rakam disini atarak buyuk harfe cevirir."""
    return re.sub(r"[^A-Za-z0-9]", "", str(value or "")).upper()


def _clamp_unit(value) -> float:
    """Sayisal degeri 0.0-1.0 araligina sikistirir; cevrilemezse 0.0 doner."""
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, number))


def normalize_result(raw: dict) -> dict:
    return {
        "first_name": _clean_name(raw.get("first_name")),
        "last_name": _clean_name(raw.get("last_name")),
        "passport_no": _normalize_code(raw.get("passport_no")),
        "birth_date": _normalize_date(raw.get("birth_date")),
        "passport_expiry": _normalize_date(raw.get("passport_expiry")),
        "passport_issue_date": _normalize_date(raw.get("passport_issue_date")),
        "birth_place": _clean_name(raw.get("birth_place"))[:60],
        "passport_issue_place": _clean_name(raw.get("passport_issue_place"))[:60],
        "gender": _normalize_gender(raw.get("gender")),
        "nationality": (str(raw.get("nationality") or "").strip().upper()[:3] or "TR"),
        "national_id": _normalize_national_id(raw.get("national_id")),
        "confidence": _clamp_unit(raw.get("confidence")),
        "is_passport": bool(raw.get("is_passport", True)),
    }


PHOTO_SYSTEM_PROMPT = (
    "Sen vize basvurulari icin biyometrik vesikalik fotograf denetleyicisisin. Sana verilen goruntuyu "
    "BAE (Dubai) vize fotograf standartlarina gore degerlendir. SADECE gecerli JSON dondur, aciklama yazma."
)

PHOTO_USER_PROMPT = """Bu goruntu bir vize basvurusu icin yuklenen vesikalik fotograf olmali.
Asagidaki kriterleri kontrol et ve tam olarak su JSON semasinda dondur:

{
  "is_photo": true veya false (goruntu bir insan portresi/vesikalik degilse false, orn. pasaport sayfasi, manzara, ekran goruntusu),
  "background_ok": true veya false (arka plan duz ve acik renk mi: beyaz/kirik beyaz/acik gri),
  "single_person": true veya false (goruntude sadece bir kisi var mi),
  "face_clear": true veya false (yuz tam gorunur, one bakiyor, kesilmemis, golgesiz mi),
  "no_obstruction": true veya false (gunes gozlugu, sapka, maske, sac ile kapatma, agir filtre YOK mu),
  "sharp": true veya false (bulanik/titrek degil mi),
  "resolution_ok": true veya false (vize icin yeterli netlik ve cozunurluk var mi),
  "issues": ["tespit edilen problemleri kisa Turkce cumlelerle listele, sorun yoksa bos dizi"],
  "advice": "sorun varsa nasil duzeltilecegine dair tek cumlelik kisa Turkce oneri, yoksa bos string",
  "score": 0.0 ile 1.0 arasinda genel uygunluk puani
}

Kurallar:
- Arka plan desenli, koyu, kalabalik veya disari/ic mekan sahnesi ise background_ok false olsun.
- Fotograf net ve kriterlere uygunsa issues bos dizi ve score 0.85 uzeri olsun.
- Emin olamadigin kriteri true kabul etme, issues'a "emin olunamadi" notu ekle.
- Turkce karakter kullanabilirsin ama sadece JSON dondur."""

PHOTO_ISSUE_LABELS = {
    "background_ok": "Arka plan duz ve acik renk (beyaz/acik gri) olmali.",
    "single_person": "Fotografta sadece basvuru sahibi olmali.",
    "face_clear": "Yuz tam, one bakan ve kesilmemis sekilde gorunmeli.",
    "no_obstruction": "Gozluk, sapka, maske veya filtre olmamali.",
    "sharp": "Fotograf net olmali, bulanik olmamali.",
    "resolution_ok": "Fotografin cozunurlugu vize icin yeterli olmali.",
}

PHOTO_CRITERIA = tuple(PHOTO_ISSUE_LABELS.keys())


def _photo_issues(raw: dict, checks: dict) -> list[str]:
    """Modelin sorun listesini temizler; bos ise basarisiz kriterlerden uretir."""
    issues = [str(item).strip()[:180] for item in (raw.get("issues") or []) if str(item).strip()]
    if issues:
        return issues
    return [PHOTO_ISSUE_LABELS[key] for key, ok in checks.items() if not ok]


def _photo_advice(raw: dict, ok: bool) -> str:
    """Model oneri vermediyse ve fotograf uygun degilse varsayilan oneriyi doner."""
    advice = str(raw.get("advice") or "").strip()[:220]
    if ok or advice:
        return advice
    return "Duz beyaz bir duvar onunde, net ve yuzunuz tam gorunecek sekilde yeni bir fotograf cekin."


def normalize_photo_result(raw: dict) -> dict:
    """LLM cikisini guvenli, tahmin edilebilir bir sozluge cevirir."""
    is_photo = bool(raw.get("is_photo", True))
    checks = {key: bool(raw.get(key, True)) for key in PHOTO_CRITERIA}
    failed = [key for key, ok in checks.items() if not ok]
    ok = is_photo and not failed

    return {
        "ok": ok,
        "is_photo": is_photo,
        "checks": checks,
        "failed": failed,
        "issues": _photo_issues(raw, checks)[:6],
        "advice": _photo_advice(raw, ok),
        "score": _clamp_unit(raw.get("score")),
    }


async def check_photo(data: bytes, content_type: str) -> dict:
    """Vesikalik fotografi LLM ile denetler. Basarisiz olursa hata firlatir."""
    api_key = (os.environ.get("EMERGENT_LLM_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("EMERGENT_LLM_KEY tanimli degil.")

    from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage

    image_b64, _mime = _prepare_image(data, content_type)

    chat = LlmChat(
        api_key=api_key,
        session_id=f"photo-{uuid.uuid4()}",
        system_message=PHOTO_SYSTEM_PROMPT,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)

    response = await chat.send_message(
        UserMessage(text=PHOTO_USER_PROMPT, file_contents=[ImageContent(image_base64=image_b64)])
    )
    text = response if isinstance(response, str) else str(response)
    parsed = _extract_json(text)
    if not parsed:
        raise ValueError("Fotograf kontrol edilemedi.")
    return normalize_photo_result(parsed)


# --------------------------------------------- arka plan (deterministik olcum)
# Vize fotografinda zemin beyaz/kirik beyaz olmali. LLM'e guvenmek yerine kenar
# pikselleri olculur: parlaklik, beyaza yakinlik orani ve desen (std sapma).
BG_NEAR_WHITE_CH = 200
BG_MIN_WHITE_RATIO = 0.55
BG_MIN_MEAN_LUM = 185
BG_MAX_STD = 42


def _load_rgb_thumb(data: bytes):
    """Goruntuyu RGB'ye cevirip 360px'e kuculterek doner; okunamazsa None."""
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as exc:
        logger.warning("background analysis failed: %s", exc)
        return None
    img.thumbnail((360, 360))
    return img


def _edge_samples(img) -> list:
    """Ust bant + sol/sag kenarlardan piksel toplar (alt kisim omuz/kiyafet)."""
    width, height = img.size
    px = img.load()
    band = max(3, int(min(width, height) * 0.09))
    upper_limit = int(height * 0.65)
    samples = [px[x, y] for x in range(0, width, 2) for y in range(0, band)]
    for y in range(0, upper_limit, 2):
        samples.extend(px[x, y] for x in range(0, band))
        samples.extend(px[x, y] for x in range(width - band, width))
    return samples


def _luminance_stats(samples: list) -> tuple[float, float, float]:
    """(ortalama parlaklik, standart sapma, beyaza yakin piksel orani)."""
    lums = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in samples]
    mean_lum = sum(lums) / len(lums)
    std = (sum((v - mean_lum) ** 2 for v in lums) / len(lums)) ** 0.5
    white_ratio = sum(1 for r, g, b in samples if min(r, g, b) >= BG_NEAR_WHITE_CH) / len(samples)
    return mean_lum, std, white_ratio


def background_report(data: bytes) -> dict:
    """Kenar piksellerinden arka planin beyaza yakinligini ve duzlugunu olcer."""
    img = _load_rgb_thumb(data)
    if img is None or min(img.size) < 40:
        return {"checked": False}

    samples = _edge_samples(img)
    if not samples:
        return {"checked": False}

    mean_lum, std, white_ratio = _luminance_stats(samples)
    ok = (
        white_ratio >= BG_MIN_WHITE_RATIO
        and mean_lum >= BG_MIN_MEAN_LUM
        and std <= BG_MAX_STD
    )
    return {
        "checked": True,
        "ok": ok,
        "white_ratio": round(white_ratio, 3),
        "mean_luminance": round(mean_lum, 1),
        "uniformity": round(std, 1),
    }


def _background_issue(report: dict) -> str:
    if report.get("mean_luminance", 255) < BG_MIN_MEAN_LUM:
        return "Arka plan koyu. Vesikaligi beyaz veya kirik beyaz bir duvarin onunde cektirin."
    if report.get("uniformity", 0) > BG_MAX_STD:
        return "Arka planda desen, esya veya baska kisiler var. Duz beyaz bir zemin gerekir."
    return "Arka plan beyaza yakin degil. Duz beyaz veya cok acik gri zemin kullanin."


def _without_background_issues(out: dict) -> list:
    return [i for i in (out.get("issues") or []) if "arka plan" not in i.lower()]


def _accept_background(out: dict) -> dict:
    """Olcum beyaz zemini dogruladiysa LLM'in arka plan itirazi dusurulur."""
    checks = dict(out.get("checks") or {})
    if checks.get("background_ok") is False:
        checks["background_ok"] = True
        out["checks"] = checks
    failed = [k for k in (out.get("failed") or []) if k != "background_ok"]
    out["failed"] = failed
    out["issues"] = _without_background_issues(out)
    out["ok"] = bool(out.get("is_photo", True)) and not failed
    return out


def _reject_background(out: dict, report: dict) -> dict:
    """Olcum zemini uygunsuz buldu: sonucu uyariya cevirir ve skoru kisitlar."""
    checks = dict(out.get("checks") or {})
    checks["background_ok"] = False
    out["checks"] = checks
    out["failed"] = ["background_ok"] + [
        k for k in (out.get("failed") or []) if k != "background_ok"
    ]
    out["issues"] = [_background_issue(report)] + _without_background_issues(out)
    out["ok"] = False
    out["advice"] = (
        out.get("advice")
        or "Beyaz duvar onunde, golgesiz ve yalnizca kendinizin gorundugu yeni bir vesikalik cekin."
    )
    score = out.get("score")
    out["score"] = min(float(score) if isinstance(score, (int, float)) else 0.5, 0.45)
    return out


def apply_background_report(result: dict, report: dict) -> dict:
    """Olculen arka plan uygun degilse sonucu uyariya cevirir (LLM'i ezer)."""
    if not report.get("checked"):
        return result
    out = dict(result)
    out["background"] = report
    return _accept_background(out) if report.get("ok") else _reject_background(out, report)


async def read_passport(data: bytes, content_type: str) -> dict:
    """Pasaport goruntusunu LLM ile okur. Basarisiz olursa hata firlatir."""
    api_key = (os.environ.get("EMERGENT_LLM_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("EMERGENT_LLM_KEY tanimli degil.")

    from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage

    image_b64s = _prepare_images(data, content_type)

    chat = LlmChat(
        api_key=api_key,
        session_id=f"passport-{uuid.uuid4()}",
        system_message=SYSTEM_PROMPT,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)

    response = await chat.send_message(
        UserMessage(
            text=USER_PROMPT,
            file_contents=[ImageContent(image_base64=b64) for b64 in image_b64s],
        )
    )
    text = response if isinstance(response, str) else str(response)
    parsed = _extract_json(text)
    if not parsed:
        raise ValueError("Pasaport bilgileri okunamadi.")
    return normalize_result(parsed)


# ------------------------------------------- pasaport fotografi <-> vesikalik
MATCH_SYSTEM_PROMPT = (
    "Sen vize basvurulari icin belge tutarlilik kontrolu yapan bir asistansin. Sana iki goruntu "
    "verilir: birincisi pasaportun kimlik bilgileri sayfasi (uzerinde kucuk bir vesikalik vardir), "
    "ikincisi basvuruya yuklenen vesikalik fotograf. Ikisinin ayni basvuru sahibine ait gorunup "
    "gorunmedigini degerlendirip SADECE gecerli JSON dondur, aciklama yazma."
)

MATCH_USER_PROMPT = """Birinci goruntu pasaportun kimlik sayfasi, ikinci goruntu basvuruya yuklenen vesikalik fotograf.
Bu iki goruntudeki kisi ayni kisi gibi mi gorunuyor? Tam olarak su JSON semasinda dondur:

{
  "passport_photo_visible": true veya false (pasaport sayfasindaki vesikalik yeterince net gorunuyor mu),
  "same_person": true, false veya null (emin olamiyorsan null),
  "confidence": 0.0 ile 1.0 arasinda,
  "note": "tek cumlelik kisa Turkce aciklama"
}

Kurallar:
- Yalnizca genel gorsel benzerligi (yuz sekli, sac, yas ve cinsiyet izlenimi) karsilastir; kisiyi
  tanimlamaya, isim tahmin etmeye veya biyometrik kimlik dogrulamasi yapmaya calisma.
- Goruntulerden biri pasaport sayfasi degilse ya da vesikalik gorunmuyorsa passport_photo_visible
  false ve same_person null olsun.
- Isik, aci ve yas farkina ragmen belirgin benzerlik varsa true; belirgin farkliliklar varsa false;
  emin olamazsan null dondur.
- Sadece JSON dondur."""

MATCH_BOOLS = {"true": True, "yes": True, "evet": True, "false": False, "no": False, "hayir": False}


def normalize_match_result(raw: dict) -> dict:
    """LLM cikisini {same_person, confidence, note} sozlugune indirger."""
    same = raw.get("same_person")
    if isinstance(same, str):
        same = MATCH_BOOLS.get(same.strip().lower())
    if not isinstance(same, bool):
        same = None
    visible = bool(raw.get("passport_photo_visible", True))
    return {
        "passport_photo_visible": visible,
        "same_person": same if visible else None,
        "confidence": _clamp_unit(raw.get("confidence")),
        "note": str(raw.get("note") or "").strip()[:220],
    }


async def compare_passport_photo(
    passport_data: bytes, passport_type: str, photo_data: bytes, photo_type: str
) -> dict:
    """Pasaport sayfasindaki vesikalik ile yuklenen vesikaligi karsilastirir."""
    api_key = (os.environ.get("EMERGENT_LLM_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("EMERGENT_LLM_KEY tanimli degil.")

    from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage

    passport_b64s = _prepare_images(passport_data, passport_type)[:1]
    photo_b64, _mime = _prepare_image(photo_data, photo_type)

    chat = LlmChat(
        api_key=api_key,
        session_id=f"facematch-{uuid.uuid4()}",
        system_message=MATCH_SYSTEM_PROMPT,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)

    response = await chat.send_message(
        UserMessage(
            text=MATCH_USER_PROMPT,
            file_contents=[
                ImageContent(image_base64=b64) for b64 in [*passport_b64s, photo_b64]
            ],
        )
    )
    text = response if isinstance(response, str) else str(response)
    parsed = _extract_json(text)
    if not parsed:
        raise ValueError("Fotograf karsilastirmasi yapilamadi.")
    return normalize_match_result(parsed)
