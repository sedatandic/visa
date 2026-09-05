"""Hero anlatimi icin ElevenLabs Turkce seslendirmesi (tek ses, tek ton).

Kullanim: python /app/scripts/generate_narration_eleven.py
Cikti: /app/frontend/public/audio/explainer/{key}.mp3

Kullanici notu: "tek kisi konussun" -> tum sahnelerde AYNI ses ayarlari kullanilir
(sahne bazli stability/style farki, ayni seste farkli kisi hissi yaratiyordu) ve
sahne bazli duygu etiketleri kaldirildi. Klipler arasi sureklilik icin ElevenLabs
request stitching kullanilir: her istek onceki klibin request-id'sini ve komsu
metinleri (previous_text / next_text) alir, boylece ton ve tempo bozulmaz.
"""
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

OUT_DIR = Path("/app/frontend/public/audio/explainer")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "xFsOR54lR471QiCvQ5re")  # Ilknur Onal
MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
API = "https://api.elevenlabs.io/v1/text-to-speech"

# "ortalama iki is gunu" cumlesindeki ton referans alindi: sakin, guven veren.
# Kullanici notu: "bir tik daha hizli, dogal konussun, robotik olmasin" ->
# tempo 1.0 (dogal): 1.2 fazla hizli geldi, kullanici %30 yavaslatma istedi, stability dusuruldu (monoton/robotik his azalir),
# style yukseltildi (dogal tonlama). Tum sahneler bu tek ayarla uretilir.
VOICE_SETTINGS = {
    "stability": 0.42,
    "similarity_boost": 0.85,
    "style": 0.32,
    "use_speaker_boost": True,
    "speed": 1.0,
}

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
        "text": "Dubaai vizenizi Dubaai Vize Online güvencesiyle kolayca alın. "
        "TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle başvurunuzu güvenle tamamlayın. "
        "Hemen başvurun ve Dubaai yolculuğunuzun ilk adımını bugün atın. "
        "Dubaai sizi bekliyor!",
    },
]


def main():
    key = os.environ["ELEVENLABS_API_KEY"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    request_ids: list[str] = []
    for idx, scene in enumerate(SCENES):
        payload = {
            "text": scene["text"],
            "model_id": MODEL_ID,
            "output_format": "mp3_44100_128",
            "voice_settings": VOICE_SETTINGS,
            "previous_text": SCENES[idx - 1]["text"] if idx else None,
            "next_text": SCENES[idx + 1]["text"] if idx + 1 < len(SCENES) else None,
            "previous_request_ids": request_ids[-3:],
        }
        r = requests.post(
            f"{API}/{VOICE_ID}",
            headers={"xi-api-key": key, "Content-Type": "application/json"},
            json={k: v for k, v in payload.items() if v is not None},
            timeout=180,
        )
        r.raise_for_status()
        rid = r.headers.get("request-id") or r.headers.get("x-request-id")
        if rid:
            request_ids.append(rid)
        path = OUT_DIR / f"{scene['key']}.mp3"
        path.write_bytes(r.content)
        print(scene["key"], round(len(r.content) * 8 / 128000, 2), "sn ->", path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print("HATA:", exc)
        sys.exit(1)
