"""Hero anlatimi icin ElevenLabs Eleven v3 Turkce seslendirmesi.

Kullanim: python /app/scripts/generate_narration_eleven.py
Cikti: /app/frontend/public/audio/explainer/{key}.mp3

Eleven v3 metin ici ses etiketlerini (audio tags) destekler; kullanicinin verdigi
yonetmen notlari bu etiketlerle uygulanir:
  - Ilk %30: [warm][smiling] sicak ve sakin
  - Orta: [informative] bilgilendirici
  - "ucak bileti gerekmez": [emphasis] ses hafif yukselir
  - "2 is gunu": [slowly][reassuring] yavaslar, guven verir
  - Kapanis: [excited][confident] satis odakli, enerjik
"""
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

OUT_DIR = Path("/app/frontend/public/audio/explainer")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "xFsOR54lR471QiCvQ5re")  # Ilknur Onal
MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_v3")
API = "https://api.elevenlabs.io/v1/text-to-speech"

SCENES = [
    {
        "key": "intro",
        "text": "[warm][smiling] Dubai vizesi almak artık çok kolay... "
        "Başvurunuzu tamamlamak için yalnızca iki belgeye ihtiyacınız var.",
        "settings": {"stability": 0.5, "style": 0.25},
    },
    {
        "key": "passport",
        "text": "[informative] İlk olarak, pasaportunuzun kimlik bilgilerinin yer aldığı sayfanın fotoğrafını yükleyin.",
        "settings": {"stability": 0.5, "style": 0.2},
    },
    {
        "key": "photo",
        "text": "[informative] Ardından beyaz fonda çekilmiş güncel bir vesikalık fotoğraf ekleyin. "
        "[gently emphasising] Fotoğrafın gözlüksüz ve şapkasız olması gerektiğini lütfen unutmayın.",
        "settings": {"stability": 0.5, "style": 0.25},
    },
    {
        "key": "upload",
        "text": "[reassuring] Belgelerinizi yükleyip ödemenizi tamamlamanız yeterli. "
        "[emphatic] Üstelik vizeniz onaylanmadan önce uçak bileti satın almanıza ya da otel rezervasyonu yaptırmanıza gerek yok.",
        "settings": {"stability": 0.45, "style": 0.4},
    },
    {
        "key": "track",
        "text": "[confident] Başvurunuzun tüm aşamalarını sizin adınıza takip ediyoruz. "
        "[slowly][reassuring] Onaylanan Dubai vizeniz... ortalama iki iş günü içinde e-posta adresinize gönderilir.",
        "settings": {"stability": 0.6, "style": 0.15},
    },
    {
        "key": "extras",
        "text": "[friendly] Dilerseniz seyahat sigortanızı ve Dubai eSIM'inizi de başvurunuza ekleyebilirsiniz. "
        "[excited] Böylece Dubai'ye vardığınız anda internet bağlantınız hazır olur "
        "ve seyahat sigortanız anında devreye girer.",
        "settings": {"stability": 0.45, "style": 0.45},
    },
    {
        "key": "cta",
        "text": "[confident][premium] Dubai vizenizi... Dubai Vize Online güvencesiyle kolayca alın. "
        "TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle başvurunuzu güvenle tamamlayın. "
        "[excited] Hemen başvurun ve Dubai yolculuğunuzun ilk adımını bugün atın. "
        "[smiling] Dubai sizi bekliyor!",
        "settings": {"stability": 0.4, "style": 0.6},
    },
]


def main():
    key = os.environ["ELEVENLABS_API_KEY"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for scene in SCENES:
        payload = {
            "text": scene["text"],
            "model_id": MODEL_ID,
            "output_format": "mp3_44100_128",
            "voice_settings": {
                "similarity_boost": 0.8,
                "use_speaker_boost": True,
                **scene["settings"],
            },
        }
        r = requests.post(
            f"{API}/{VOICE_ID}",
            headers={"xi-api-key": key, "Content-Type": "application/json"},
            json=payload,
            timeout=180,
        )
        r.raise_for_status()
        path = OUT_DIR / f"{scene['key']}.mp3"
        path.write_bytes(r.content)
        print(scene["key"], round(len(r.content) / 16000, 1), "sn ->", path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print("HATA:", exc)
        sys.exit(1)
