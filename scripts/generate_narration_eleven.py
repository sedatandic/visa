"""Hero anlatimi: TEK PARCA ElevenLabs seslendirmesi + sahne zaman damgalari.

Kullanim: python /app/scripts/generate_narration_eleven.py
Cikti:
  /app/frontend/public/audio/explainer/full.mp3
  /app/frontend/public/audio/explainer/full.json  ({"scenes": [{key, start, end}], "duration"})

Neden tek parca? Metin 7 ayri istekte uretilince her klip bastan baslayan bir tonlama
kuruyordu; klip gecislerinde duraksama ve "robotik" his olusuyordu. Simdi tum senaryo
tek istekte, kesintisiz prozodiyle uretiliyor; sahne gecisleri karakter bazli zaman
damgalarindan (with-timestamps) hesaplaniyor.

Ayarlar: style=0 (ElevenLabs dokumani: style yukseldikce ses kararsizlasir),
stability=0.5 (dengeli), speed=1.0 (dogal tempo).
"""
import base64
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

OUT_DIR = Path("/app/frontend/public/audio/explainer")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "cbqdgvVi3C6sgxIWpqIh")  # Fusun Tuncer (kadin, enerjik reklam tonu) - kullanici secimi
MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
API = "https://api.elevenlabs.io/v1/text-to-speech"

# Guven veren, kendinden emin ton: yuksek stability (kararli, saglam) + style 0.
# Enerjik reklam tonu (demo #16 ayarlari): stability dusuk = canli tonlama, style 0.15.
VOICE_SETTINGS = {
    "stability": 0.4,
    "similarity_boost": 0.85,
    "style": 0.15,
    "use_speaker_boost": True,
    "speed": 1.0,
}

# "Dubai" uzun a ile okunsun diye seslendirme metninde "Dubaai" yazilir (altyazilar dogru yazimda).
SCENES = [
    {
        "key": "intro",
        "text": "Dubaai vizesi almak artık çok kolay. "
        "Başvurunuzu yapmak için yalnızca iki belgeye ihtiyacınız var.",
    },
    {
        "key": "passport",
        "text": "İlk olarak, pasaportunuzun kimlik bilgilerinin yer aldığı sayfanın fotoğrafını yükleyin.",
    },
    {
        "key": "photo",
        "text": "Ardından beyaz fonda çekilmiş güncel bir vesikalık fotoğraf ekleyin. "
        "Fotoğrafınızın gözlüksüz ve şapkasız olması gerektiğini lütfen unutmayın.",
    },
    {
        "key": "upload",
        "text": "Belgelerinizi yükleyip ödemenizi yapmanız yeterlidir. "
        "Üstelik vizeniz onaylanmadan önce uçak bileti satın almanıza "
        "ya da otel rezervasyonu yaptırmanıza da gerek yok.",
    },
    {
        "key": "track",
        "text": "Başvurunuzun tüm aşamalarını sizin adınıza biz takip ediyoruz. "
        "Onaylanan Dubaai vizeniz ortalama iki iş günü içinde "
        "e-mail adresinize ve WhatsApp ile gönderilir.",
    },
    {
        "key": "extras",
        "text": "Dilerseniz seyahat sigortanızı ve Dubaai eSIM'inizi de başvurunuza ekleyebilirsiniz. "
        "Böylece Dubaai'ye vardığınız anda internet bağlantınız hazır olur "
        "ve seyahat sigortanız anında devreye girer.",
    },
    {
        "key": "cta",
        "text": "Vizenizi Dubaai Vize Hattı ile kolayca alın. "
        "TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle başvurunuzu tamamlayın. "
        "Hemen başvurun ve Dubaai yolculuğunuzun ilk adımını bugün atın. "
        "Dubaai sizi bekliyor!",
    },
]


def scene_windows(alignment: dict, offsets: list[tuple[int, int]], total: float) -> list[dict]:
    """Karakter zaman damgalarindan sahne baslangic/bitis saniyelerini cikarir."""
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]
    windows = []
    for (scene, (begin, finish)) in zip(SCENES, offsets):
        begin = min(begin, len(starts) - 1)
        finish = min(finish, len(ends)) - 1
        windows.append({"key": scene["key"], "start": round(starts[begin], 3), "end": round(ends[finish], 3)})
    for i in range(len(windows) - 1):
        windows[i]["end"] = windows[i + 1]["start"]
    windows[-1]["end"] = round(total, 3)
    return windows


def main() -> None:
    key = os.environ["ELEVENLABS_API_KEY"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    full_text = ""
    offsets = []
    for scene in SCENES:
        begin = len(full_text)
        full_text += scene["text"]
        offsets.append((begin, len(full_text)))
        full_text += " "
    full_text = full_text.strip()

    res = requests.post(
        f"{API}/{VOICE_ID}/with-timestamps",
        headers={"xi-api-key": key, "Content-Type": "application/json"},
        json={
            "text": full_text,
            "model_id": MODEL_ID,
            "output_format": "mp3_44100_128",
            "voice_settings": VOICE_SETTINGS,
        },
        timeout=300,
    )
    res.raise_for_status()
    data = res.json()
    audio = base64.b64decode(data["audio_base64"])
    (OUT_DIR / "full.mp3").write_bytes(audio)

    duration = len(audio) * 8 / 128000
    windows = scene_windows(data["alignment"], offsets, duration)
    (OUT_DIR / "full.json").write_text(
        json.dumps({"duration": round(duration, 3), "scenes": windows}, ensure_ascii=False, indent=1)
    )
    print(f"full.mp3 {duration:.1f} sn")
    for w in windows:
        print(f"  {w['key']:9s} {w['start']:6.2f} -> {w['end']:6.2f}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print("HATA:", exc)
        sys.exit(1)
