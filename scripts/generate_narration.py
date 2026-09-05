"""Hero anlatimi icin Turkce seslendirme dosyalarini bir kez uretir (OpenAI TTS).

Kullanim: python /app/scripts/generate_narration.py
Cikti: /app/frontend/public/audio/explainer/{key}.mp3
Not: ElevenLabs Turk seslendirmecileri ucretsiz planda API'ye kapali oldugu icin
yedek olarak bu script kullaniliyor (bkz. generate_narration_eleven.py).
"""
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
from emergentintegrations.llm.openai import OpenAITextToSpeech  # noqa: E402

OUT_DIR = Path("/app/frontend/public/audio/explainer")

LINES = {
    "intro": "Dubai vizesi almak artık çok kolay. Başvurunuz için sadece iki belge yeterli.",
    "passport": "Birincisi, pasaportunuzun kimlik bilgilerinin bulunduğu sayfa.",
    "photo": "İkincisi ise beyaz fonda çekilmiş güncel bir vesikalık fotoğraf. Fotoğrafın gözlüksüz ve şapkasız olması gerektiğini unutmayın.",
    "upload": "Belgelerinizi yükleyip ödemenizi tamamlamanız yeterli. Üstelik vizeniz onaylanmadan önce uçak bileti satın almanıza veya otel rezervasyonu yaptırmanıza gerek yok.",
    "track": "Başvurunuzun tüm sürecini sizin adınıza biz takip ediyoruz. Onaylanan Dubai vizeniz ortalama iki iş günü içinde e-posta adresinize gönderiliyor.",
    "extras": "Dilerseniz seyahat sigortanızı ve Dubai eSIM'inizi de aynı başvuruya ekleyin. Böylece uçaktan indiğiniz anda internetiniz hazır, sigortanız devrede olur.",
    "cta": "Başvurunuzu TÜRSAB üyesi, A grubu seyahat acentesi güvencesiyle yapın. Hemen başvurun ve Dubai'ye yolculuğunuzun ilk adımını bugün atın.",
}


async def main():
    key = os.environ["EMERGENT_LLM_KEY"]
    tts = OpenAITextToSpeech(api_key=key)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, text in LINES.items():
        audio = await tts.generate_speech(text=text, model="tts-1-hd", voice="shimmer", speed=0.9)
        path = OUT_DIR / f"{name}.mp3"
        path.write_bytes(audio)
        print(name, len(audio), "bytes ->", path)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:  # noqa: BLE001
        print("HATA:", exc)
        sys.exit(1)
