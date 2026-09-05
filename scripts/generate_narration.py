"""Hero anlatimi icin Turkce seslendirme dosyalarini bir kez uretir.

Kullanim: python /app/scripts/generate_narration.py
Cikti: /app/frontend/public/audio/explainer/{key}.mp3
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
    "passport": "Dubai vizesi icin sadece iki belge yeterli. Birincisi, pasaportunuzun kimlik sayfasinin fotografi. Telefonunuzla cektiginiz net bir kare yeterli.",
    "photo": "Ikincisi, beyaz fonda cekilmis bir vesikalik fotograf. Son alti ay icinde cekilmis, gozluksuz ve sapkasiz olmasi gerekiyor.",
    "upload": "Belgeleri yukleyip odemenizi yapin. Vizeniz cikmadan ucak bileti almaniza ya da otel rezervasyonu yapmaniza gerek yok.",
    "delivered": "Basvurunuzu biz takip ediyoruz. Onaylanan vizeniz ortalama iki is gununde, ekspres hizmette yaklasik sekiz mesai saatinde e-postaniza geliyor.",
}


async def main():
    key = os.environ["EMERGENT_LLM_KEY"]
    tts = OpenAITextToSpeech(api_key=key)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, text in LINES.items():
        audio = await tts.generate_speech(text=text, model="tts-1-hd", voice="coral", speed=1.0)
        path = OUT_DIR / f"{name}.mp3"
        path.write_bytes(audio)
        print(name, len(audio), "bytes ->", path)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:  # noqa: BLE001
        print("HATA:", exc)
        sys.exit(1)
