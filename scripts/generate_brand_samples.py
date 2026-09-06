"""Marka adi karsilastirmasi: kapanis cumlesinin iki alternatifle seslendirmesi.

Kullanim: python /app/scripts/generate_brand_samples.py
Cikti: /app/frontend/public/audio/samples/{vizecim,vizehatti}.mp3
Ses ve ayarlar anlatim kaydiyla ayni (Fusun Tuncer, eleven_multilingual_v2).
"""
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

OUT_DIR = Path("/app/frontend/public/audio/samples")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "cbqdgvVi3C6sgxIWpqIh")
MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
API = "https://api.elevenlabs.io/v1/text-to-speech"
VOICE_SETTINGS = {
    "stability": 0.4,
    "similarity_boost": 0.85,
    "style": 0.15,
    "use_speaker_boost": True,
    "speed": 1.0,
}

TAIL = (
    "TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle başvurunuzu bugün tamamlayın. "
    "Dubaai sizi bekliyor!"
)
SAMPLES = {
    "vizecim": f"Vizenizi Dubaai Vizecim ile kolayca alın. {TAIL}",
    "vizehatti": f"Vizenizi Dubaai Vize Hattı ile kolayca alın. {TAIL}",
    "online": f"Dubaai vizenizi Dubaai Vize Online güvencesiyle kolayca alın. {TAIL}",
}


def main() -> None:
    key = os.environ["ELEVENLABS_API_KEY"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, text in SAMPLES.items():
        res = requests.post(
            f"{API}/{VOICE_ID}",
            headers={"xi-api-key": key, "Content-Type": "application/json"},
            json={
                "text": text,
                "model_id": MODEL_ID,
                "output_format": "mp3_44100_128",
                "voice_settings": VOICE_SETTINGS,
            },
            timeout=180,
        )
        res.raise_for_status()
        path = OUT_DIR / f"{name}.mp3"
        path.write_bytes(res.content)
        print(f"{path} {len(res.content) * 8 / 128000:.1f} sn")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print("HATA:", exc)
        sys.exit(1)
