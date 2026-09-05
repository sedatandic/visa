"""Hero anlatimi icin ElevenLabs Turkce seslendirmesi (sahne bazli tonlama).

Kullanim: python /app/scripts/generate_narration_eleven.py
Cikti: /app/frontend/public/audio/explainer/{key}.mp3

Tonlama plani (kullanici senaryosu):
  - Ilk %30: sicak + sakin (yuksek stability, dusuk style)
  - Orta: bilgilendirici + profesyonel
  - "ucak bileti gerekmez" ve ekstralar: ses hafif yukselir (style artar)
  - "2 is gunu": yavaslar, guven verir (stability yukselir, speed duser)
  - Kapanis: satis odakli, enerjik (dusuk stability, yuksek style)
Duraklamalar metne <break time="..."/> ile gomulur.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
from elevenlabs import ElevenLabs, VoiceSettings  # noqa: E402

OUT_DIR = Path("/app/frontend/public/audio/explainer")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "xFsOR54lR471QiCvQ5re")  # Ilknur Onal

SCENES = [
    {
        "key": "intro",
        "text": 'Dubai vizesi almak artık çok kolay... <break time="0.5s" /> '
        "Başvurunuzu tamamlamak için yalnızca iki belgeye ihtiyacınız var.",
        "settings": dict(stability=0.6, style=0.2, speed=0.98),
    },
    {
        "key": "passport",
        "text": "İlk olarak, pasaportunuzun kimlik bilgilerinin yer aldığı sayfanın fotoğrafını yükleyin.",
        "settings": dict(stability=0.55, style=0.2, speed=1.0),
    },
    {
        "key": "photo",
        "text": "Ardından beyaz fonda çekilmiş güncel bir vesikalık fotoğraf ekleyin. "
        '<break time="0.4s" /> Fotoğrafın gözlüksüz ve şapkasız olması gerektiğini lütfen unutmayın.',
        "settings": dict(stability=0.55, style=0.25, speed=1.0),
    },
    {
        "key": "upload",
        "text": "Belgelerinizi yükleyip ödemenizi tamamlamanız yeterli. <break time=\"0.5s\" /> Üstelik... "
        "vizeniz onaylanmadan önce uçak bileti satın almanıza ya da otel rezervasyonu yaptırmanıza gerek yok.",
        "settings": dict(stability=0.45, style=0.45, speed=1.0),
    },
    {
        "key": "track",
        "text": "Başvurunuzun tüm aşamalarını sizin adınıza takip ediyoruz. "
        '<break time="0.4s" /> Onaylanan Dubai vizeniz... ortalama iki iş günü içinde e-posta adresinize gönderilir.',
        "settings": dict(stability=0.65, style=0.15, speed=0.95),
    },
    {
        "key": "extras",
        "text": "Dilerseniz seyahat sigortanızı ve Dubai eSIM'inizi de başvurunuza ekleyebilirsiniz. "
        'Böylece Dubai\'ye vardığınız anda internet bağlantınız hazır olur... <break time="0.3s" /> '
        "ve seyahat sigortanız anında devreye girer.",
        "settings": dict(stability=0.45, style=0.5, speed=1.0),
    },
    {
        "key": "cta",
        "text": 'Dubai vizenizi... <break time="0.3s" /> Dubai Vize Online güvencesiyle kolayca alın. '
        'TÜRSAB üyesi A Grubu seyahat acentesi güvencesiyle... <break time="0.3s" /> başvurunuzu güvenle tamamlayın. '
        'Hemen başvurun... <break time="0.3s" /> ve Dubai yolculuğunuzun ilk adımını bugün atın. Dubai sizi bekliyor!',
        "settings": dict(stability=0.35, style=0.65, speed=1.02),
    },
]


def main():
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for scene in SCENES:
        settings = VoiceSettings(
            similarity_boost=0.8,
            use_speaker_boost=True,
            **scene["settings"],
        )
        stream = client.text_to_speech.convert(
            text=scene["text"],
            voice_id=VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings=settings,
        )
        data = b"".join(stream)
        path = OUT_DIR / f"{scene['key']}.mp3"
        path.write_bytes(data)
        print(scene["key"], round(len(data) / 16000, 1), "sn ->", path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print("HATA:", exc)
        sys.exit(1)
