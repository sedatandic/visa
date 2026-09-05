"""Hero anlatimi icin ElevenLabs (Turkce, multilingual v2) seslendirmesi uretir.

Kullanim: python /app/scripts/generate_narration_eleven.py
Cikti: /app/frontend/public/audio/explainer/{key}.mp3
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
from elevenlabs import ElevenLabs, VoiceSettings  # noqa: E402

OUT_DIR = Path("/app/frontend/public/audio/explainer")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "XrExE9yKIg1WjnnlVkGX")  # Matilda: sicak, samimi

LINES = {
    "passport": "Dubai vizesi için sadece iki belge yeterli. Birincisi, pasaportunuzun kimlik sayfasının fotoğrafı.",
    "photo": "İkincisi, beyaz fonda çekilmiş bir vesikalık fotoğraf. Gözlüksüz ve şapkasız olması gerekiyor.",
    "upload": "Belgeleri yükleyip ödemenizi yapın. Vizeniz çıkmadan uçak bileti ya da otel rezervasyonu gerekmiyor.",
    "delivered": "Başvurunuzu biz takip ediyoruz. Onaylanan vizeniz, ortalama iki iş gününde e-postanıza geliyor.",
}


def main():
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    settings = VoiceSettings(stability=0.5, similarity_boost=0.85, style=0.2, use_speaker_boost=True, speed=0.95)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, text in LINES.items():
        stream = client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings=settings,
        )
        data = b"".join(stream)
        path = OUT_DIR / f"{name}.mp3"
        path.write_bytes(data)
        print(name, len(data), "bytes ->", path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print("HATA:", exc)
        sys.exit(1)
