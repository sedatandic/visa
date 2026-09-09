"""Hero anlatimi: TEK PARCA ElevenLabs seslendirmesi + sahne zaman damgalari.

Kullanim: python /app/scripts/generate_narration_eleven.py
Cikti:
  /app/frontend/public/audio/explainer/full.mp3
  /app/frontend/public/audio/explainer/full.json  ({"scenes": [{key, start, end}], "duration"})

Neden tek parca? Metin 7 ayri istekte uretilince her klip bastan baslayan bir tonlama
kuruyordu; klip gecislerinde duraksama ve "robotik" his olusuyordu. Simdi tum senaryo
tek istekte, kesintisiz prozodiyle uretiliyor; sahne gecisleri karakter bazli zaman
damgalarindan (with-timestamps) hesaplaniyor.

Kullanici notlari (2026-06-11):
- "Dubai" duz okunur (eskiden uzun a icin "Dubaai" yaziliyordu).
- Yeni cumleye enerjik giris, cumle sonunda tempo dususu -> `eleven_v3` + cumle basi
  duygu etiketleri ([energetic], [confident], [reassuring], [excited]).
- Cumle gecislerinde net duraklama: model break etiketlerini cok kisa okudugu icin
  sessizlik SES DOSYASINA sonradan eklenir (pydub + ffmpeg) ve zaman damgalari kaydirilir.
- "Basvurunuzun tum asamalarini" tek nefeste (icinde noktalama yok).
- "Ilk olarak" cumlesinden once daha uzun bekleme (PAUSE_LONG).
- Kapanis "Dubai sizi bekliyor!" heyecanli ([excited]).
"""
import base64
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from pydub import AudioSegment

load_dotenv("/app/backend/.env")

OUT_DIR = Path("/app/frontend/public/audio/explainer")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "cbqdgvVi3C6sgxIWpqIh")  # Fusun Tuncer (kadin, enerjik reklam tonu)
MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID", "eleven_v3")
API = "https://api.elevenlabs.io/v1/text-to-speech"

# v3 stability ayrik degerler bekler: 0.0 (creative) / 0.5 (natural) / 1.0 (robust).
VOICE_SETTINGS = {"stability": 0.5, "similarity_boost": 0.85, "use_speaker_boost": True}

PAUSE_DEFAULT = 0.35  # cumleler arasi eklenen sessizlik (sn)
PAUSE_LONG = 0.7  # "Ilk olarak" cumlesinden once
LONG_PAUSE_BEFORE = "[excited] İlk olarak"

SCENES = [
    {
        "key": "intro",
        "sentences": [
            "[warm] Dubai vizesi almak artık çok kolay.",
            "[energetic] Başvurunuzu yapmak için yalnızca iki belgeye ihtiyacınız var.",
        ],
    },
    {
        "key": "passport",
        "sentences": [
            "[excited] İlk olarak, pasaportunuzun kimlik bilgilerinin yer aldığı sayfanın fotoğrafını yükleyin.",
        ],
    },
    {
        "key": "photo",
        "sentences": [
            "[energetic] Ardından beyaz fonda çekilmiş güncel bir vesikalık fotoğraf ekleyin.",
            "[informative] Fotoğrafınızın gözlüksüz ve şapkasız olması gerekmektedir.",
        ],
    },
    {
        "key": "upload",
        "sentences": [
            "[energetic] Belgelerinizi yükleyip ödemenizi yapmanız yeterli.",
            "[emphatic] Üstelik Dubai vizeniz onaylanmadan önce uçak bileti ya da otel rezervasyonu yaptırmanıza da gerek yok.",
        ],
    },
    {
        "key": "track",
        "sentences": [
            "[confident] Başvurunuzun tüm aşamalarını sizin adınıza biz takip ediyor ve onaylanan Dubai vizenizi otuz altı saat içinde e-mail adresinize ve WhatsApp ile gönderiyoruz.",
        ],
    },
    {
        "key": "extras",
        "sentences": [
            "[energetic] Dilerseniz seyahat sigortanızı ve Dubai eSIM'inizi de başvurunuza ekleyebilirsiniz.",
            "[informative] Böylece Dubai'ye vardığınız anda internet bağlantınız hazır olur ve seyahat sigortanız anında devreye girer.",
        ],
    },
    {
        "key": "cta",
        "sentences": [
            "[confident] Vizenizi Dubai Vize Hattı ile kolayca alın.",
            "[confident] TÜRSAB üyesi A grubu seyahat acentesi iş birliğiyle başvurunuzu baştan sona biz yürütüyoruz.",
            "[energetic] Formu doldurun, gerisini bize bırakın.",
            "[excited] Dubai sizi bekliyor!",
        ],
    },
]

TAG = re.compile(r"\[[^\]]*\]|<[^>]*>")


def plain(text: str) -> str:
    return TAG.sub("", text)


def compact(text: str) -> str:
    return re.sub(r"\s+", "", plain(text))


def all_sentences() -> list[str]:
    return [s for scene in SCENES for s in scene["sentences"]]


def build_text() -> str:
    return " ".join(all_sentences())


def visible_indices(chars: list[str]) -> list[int]:
    """Etiket ([...] / <...>) icindeki ve bosluk karakterlerini atlar."""
    out = []
    square = angle = 0
    for i, c in enumerate(chars):
        if c == "[":
            square += 1
            continue
        if c == "]":
            square = max(0, square - 1)
            continue
        if c == "<":
            angle += 1
            continue
        if c == ">":
            angle = max(0, angle - 1)
            continue
        if square or angle or c.isspace():
            continue
        out.append(i)
    return out


def sentence_bounds(alignment: dict) -> list[tuple[float, float]]:
    """Her cumlenin (baslangic, bitis) saniyesi."""
    chars = alignment["characters"]
    starts = alignment["character_start_times_seconds"]
    ends = alignment["character_end_times_seconds"]
    visible = visible_indices(chars)
    bounds = []
    cursor = 0
    for sentence in all_sentences():
        span = visible[cursor : cursor + len(compact(sentence))]
        bounds.append((starts[span[0]], ends[span[-1]]))
        cursor += len(span)
    return bounds


def insert_pauses(raw: AudioSegment, bounds: list[tuple[float, float]]) -> tuple[AudioSegment, list[tuple[float, float]]]:
    """Cumle aralarina sessizlik ekler; (yeni ses, kaydirma noktalari) dondurur."""
    sentences = all_sentences()
    out = AudioSegment.empty()
    shifts: list[tuple[float, float]] = []  # (orijinal saniye, eklenen toplam)
    added = 0.0
    cut_ms = 0
    for i, (_, end) in enumerate(bounds[:-1]):
        gap = PAUSE_LONG if sentences[i + 1].startswith(LONG_PAUSE_BEFORE) else PAUSE_DEFAULT
        boundary_ms = int(end * 1000)
        out += raw[cut_ms:boundary_ms] + AudioSegment.silent(duration=int(gap * 1000), frame_rate=raw.frame_rate)
        cut_ms = boundary_ms
        added += gap
        shifts.append((end, added))
    out += raw[cut_ms:]
    return out, shifts


def shifted(value: float, shifts: list[tuple[float, float]]) -> float:
    total = 0.0
    for boundary, cumulative in shifts:
        if value >= boundary:
            total = cumulative
    return round(value + total, 3)


def scene_windows(bounds: list[tuple[float, float]], shifts: list[tuple[float, float]], total: float) -> list[dict]:
    windows = []
    cursor = 0
    for scene in SCENES:
        count = len(scene["sentences"])
        start = bounds[cursor][0]
        end = bounds[cursor + count - 1][1]
        windows.append({"key": scene["key"], "start": shifted(start, shifts), "end": shifted(end, shifts)})
        cursor += count
    for i in range(len(windows) - 1):
        windows[i]["end"] = windows[i + 1]["start"]
    windows[0]["start"] = 0.0
    windows[-1]["end"] = round(total, 3)
    return windows


def main() -> None:
    key = os.environ["ELEVENLABS_API_KEY"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    res = requests.post(
        f"{API}/{VOICE_ID}/with-timestamps",
        headers={"xi-api-key": key, "Content-Type": "application/json"},
        json={
            "text": build_text(),
            "model_id": MODEL_ID,
            "output_format": "mp3_44100_128",
            "voice_settings": VOICE_SETTINGS,
        },
        timeout=300,
    )
    if res.status_code >= 400:
        print("HATA", res.status_code, res.text[:400])
        sys.exit(1)
    data = res.json()
    Path("/tmp/tts_raw.mp3").write_bytes(base64.b64decode(data["audio_base64"]))
    Path("/tmp/full_align.json").write_text(json.dumps(data["alignment"], ensure_ascii=False))

    raw = AudioSegment.from_file("/tmp/tts_raw.mp3", format="mp3")
    bounds = sentence_bounds(data["alignment"])
    audio, shifts = insert_pauses(raw, bounds)
    audio.export(OUT_DIR / "full.mp3", format="mp3", bitrate="128k")

    duration = len(audio) / 1000
    windows = scene_windows(bounds, shifts, duration)
    (OUT_DIR / "full.json").write_text(
        json.dumps({"duration": round(duration, 3), "scenes": windows}, ensure_ascii=False, indent=1)
    )
    print(f"full.mp3 {duration:.1f} sn (ham {len(raw) / 1000:.1f} sn + {shifts[-1][1]:.1f} sn duraklama) · {MODEL_ID}")
    for w in windows:
        print(f"  {w['key']:9s} {w['start']:6.2f} -> {w['end']:6.2f}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print("HATA:", exc)
        sys.exit(1)
