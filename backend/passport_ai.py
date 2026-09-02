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
  "mrz": "okunabildiyse MRZ satirlari, yoksa bos string",
  "confidence": 0.0 ile 1.0 arasinda okuma guveni,
  "is_passport": true veya false (goruntu bir pasaport sayfasi degilse false)
}

Kurallar:
- Tarihleri mutlaka YYYY-MM-DD formatinda ver. MRZ'deki YYMMDD formatini dogru yuzyila cevir
  (dogum tarihi icin gelecek tarih olamaz, gecerlilik tarihi icin genelde 20xx).
- Cinsiyet MRZ'de M ise "male", F ise "female".
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


def normalize_result(raw: dict) -> dict:
    gender = (raw.get("gender") or "").strip().lower()
    if gender in {"m", "male", "erkek"}:
        gender = "male"
    elif gender in {"f", "female", "kadin", "kadın"}:
        gender = "female"
    else:
        gender = ""

    national_id = re.sub(r"\D", "", str(raw.get("national_id") or ""))
    if len(national_id) != 11:
        national_id = ""

    try:
        confidence = float(raw.get("confidence") or 0)
    except (TypeError, ValueError):
        confidence = 0.0

    return {
        "first_name": _clean_name(raw.get("first_name")),
        "last_name": _clean_name(raw.get("last_name")),
        "passport_no": re.sub(r"[^A-Za-z0-9]", "", str(raw.get("passport_no") or "")).upper(),
        "birth_date": _normalize_date(raw.get("birth_date")),
        "passport_expiry": _normalize_date(raw.get("passport_expiry")),
        "gender": gender,
        "nationality": (str(raw.get("nationality") or "").strip().upper()[:3] or "TR"),
        "national_id": national_id,
        "confidence": max(0.0, min(1.0, confidence)),
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


def normalize_photo_result(raw: dict) -> dict:
    """LLM cikisini guvenli, tahmin edilebilir bir sozluge cevirir."""
    def _flag(key: str) -> bool:
        return bool(raw.get(key, True))

    is_photo = bool(raw.get("is_photo", True))
    checks = {key: _flag(key) for key in PHOTO_CRITERIA}

    issues: list[str] = []
    for item in raw.get("issues") or []:
        text = str(item).strip()
        if text:
            issues.append(text[:180])
    if not issues:
        issues = [PHOTO_ISSUE_LABELS[key] for key, ok in checks.items() if not ok]

    try:
        score = float(raw.get("score") or 0)
    except (TypeError, ValueError):
        score = 0.0
    score = max(0.0, min(1.0, score))

    failed = [key for key, ok in checks.items() if not ok]
    ok = is_photo and not failed

    advice = str(raw.get("advice") or "").strip()[:220]
    if not ok and not advice:
        advice = "Duz beyaz bir duvar onunde, net ve yuzunuz tam gorunecek sekilde yeni bir fotograf cekin."

    return {
        "ok": ok,
        "is_photo": is_photo,
        "checks": checks,
        "failed": failed,
        "issues": issues[:6],
        "advice": advice,
        "score": score,
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


async def read_passport(data: bytes, content_type: str) -> dict:
    """Pasaport goruntusunu LLM ile okur. Basarisiz olursa hata firlatir."""
    api_key = (os.environ.get("EMERGENT_LLM_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("EMERGENT_LLM_KEY tanimli degil.")

    from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage

    image_b64, _mime = _prepare_image(data, content_type)

    chat = LlmChat(
        api_key=api_key,
        session_id=f"passport-{uuid.uuid4()}",
        system_message=SYSTEM_PROMPT,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)

    response = await chat.send_message(
        UserMessage(text=USER_PROMPT, file_contents=[ImageContent(image_base64=image_b64)])
    )
    text = response if isinstance(response, str) else str(response)
    parsed = _extract_json(text)
    if not parsed:
        raise ValueError("Pasaport bilgileri okunamadi.")
    return normalize_result(parsed)
