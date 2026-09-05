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
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "FvxJI7vwUDkTkEOO7nd7")  # Pelin Yildiz: Turk seslendirmeci, sicak ve samimi

LINES = {
    "intro": "Dubai vizesi almak artık çok kolay. Başvurunuz için sadece iki belge yeterli.",
    "passport": "Birincisi, pasaportunuzun kimlik bilgilerinin bulunduğu sayfa.",
    "photo": "İkincisi ise beyaz fonda çekilmiş güncel bir vesikalık fotoğraf. Fotoğrafın gözlüksüz ve şapkasız olması gerektiğini unutmayın.",
    "upload": "Belgelerinizi yükleyip ödemenizi tamamlamanız yeterli. Üstelik vizeniz onaylanmadan önce uçak bileti satın almanıza veya otel rezervasyonu yaptırmanıza gerek yok.",
    "track": "Başvurunuzun tüm sürecini sizin adınıza biz takip ediyoruz. Onaylanan Dubai vizeniz ortalama iki iş günü içinde e-posta adresinize gönderiliyor.",
    "extras": "Dilerseniz seyahat sigortanızı ve Dubai eSIM'inizi de aynı başvuruya ekleyin. Böylece uçaktan indiğiniz anda internetiniz hazır, sigortanız devrede olur.",
    "cta": "Vizenizi Dubai Vize Online güvencesiyle alın. TÜRSAB üyesi A grubu seyahat acentesiyiz. Hemen başvurun ve Dubai'ye yolculuğunuzun ilk adımını bugün atın.",
}


def main():
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    settings = VoiceSettings(stability=0.5, similarity_boost=0.85, style=0.2, use_speaker_boost=True, speed=0.92)
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
