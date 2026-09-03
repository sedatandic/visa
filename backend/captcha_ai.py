"""Zami portalindaki 3 haneli sayisal captcha'yi Emergent LLM vision ile okur.

Amac: admin panelde robot oturumu acarken captcha'yi otomatik doldurmak.
Basarisiz olursa sessizce bos string doner; kullanici elle yazabilir.
"""
import base64
import logging
import os
import uuid

logger = logging.getLogger(__name__)

MODEL_PROVIDER = "openai"
MODEL_NAME = "gpt-5.4"

SYSTEM_PROMPT = (
    "Sen bir captcha okuyucusun. Sana verilen kucuk goruntude 3 haneli bir sayi var. "
    "Sadece o sayiyi dondur; aciklama, bosluk veya noktalama ekleme."
)
USER_PROMPT = "Bu captcha goruntusundeki 3 haneli sayiyi sadece rakam olarak dondur."


def _upscale(data: bytes) -> bytes:
    """Kucuk captcha gorselini buyutup kontrastini artirir (OCR dogrulugu icin)."""
    try:
        import io

        from PIL import Image, ImageOps

        img = Image.open(io.BytesIO(data)).convert("L")
        img = ImageOps.autocontrast(img)
        img = img.resize((img.width * 5, img.height * 5), Image.LANCZOS)
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        return buf.getvalue()
    except Exception as exc:  # pragma: no cover
        logger.warning("captcha upscale failed: %s", exc)
        return data


async def read_captcha(data: bytes) -> str:
    """Captcha goruntusundeki rakamlari dondurur; okunamazsa bos string."""
    api_key = (os.environ.get("EMERGENT_LLM_KEY") or "").strip()
    if not api_key or not data:
        return ""
    try:
        from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage

        prepared = _upscale(data)
        chat = LlmChat(
            api_key=api_key,
            session_id=f"captcha-{uuid.uuid4()}",
            system_message=SYSTEM_PROMPT,
        ).with_model(MODEL_PROVIDER, MODEL_NAME)
        response = await chat.send_message(
            UserMessage(
                text=USER_PROMPT,
                file_contents=[
                    ImageContent(image_base64=base64.b64encode(prepared).decode("ascii"))
                ],
            )
        )
        text = response if isinstance(response, str) else str(response)
        digits = "".join(ch for ch in text if ch.isdigit())
        return digits[:6]
    except Exception as exc:  # pragma: no cover - AI cagrisi best-effort
        logger.warning("captcha ai read failed: %s", exc)
        return ""
