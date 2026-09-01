"""Ucretsiz on degerlendirme (pre-evaluation) skorlama motoru.

3 hizli soru ile Dubai/BAE vizesi onay olasiligini tahmin eder ve
kullaniciya somut aksiyon onerileri dondurur.

Skorlama tamamen deterministik ve aciklanabilirdir: her cevap icin
puan etkisi (delta) ve gerekce (reason) uretilir, boylece sonuc
ekraninda "neden bu skor" seffaf sekilde gosterilebilir.
"""

from __future__ import annotations

from typing import Any, Dict, List

BASE_SCORE = 55

# --------------------------------------------------------------- secenekler
PASSPORT_OPTIONS: Dict[str, Dict[str, Any]] = {
    "6_plus": {
        "label": "6 aydan fazla geçerli",
        "delta": 12,
        "reason": "Pasaportunuz 6 aydan fazla geçerli — BAE'nin temel şartını karşılıyor.",
    },
    "under_6": {
        "label": "6 aydan az geçerli",
        "delta": -30,
        "reason": "BAE, giriş tarihinde en az 6 ay geçerli pasaport ister. Yenileme gerekiyor.",
        "blocker": "Başvuru öncesi pasaportunuzu yenilemeniz gerekiyor.",
    },
    "expired": {
        "label": "Süresi dolmuş",
        "delta": -55,
        "reason": "Süresi dolmuş pasaportla başvuru kabul edilmez.",
        "blocker": "Yeni pasaport çıkarmadan başvuru yapılamaz.",
    },
}

HISTORY_OPTIONS: Dict[str, Dict[str, Any]] = {
    "recent": {
        "label": "Evet, son 5 yıl içinde",
        "delta": 14,
        "reason": "Son 5 yıldaki ABD/İngiltere/Schengen/BAE vize geçmişi güçlü bir olumlu sinyaldir.",
    },
    "old": {
        "label": "Evet, 5 yıldan önce",
        "delta": 7,
        "reason": "Geçmiş vize kaydınız var; bu seyahat geçmişiniz açısından olumlu.",
    },
    "none": {
        "label": "Hayır, ilk vize başvurum",
        "delta": -6,
        "reason": "İlk vize başvurusunda destekleyici belgeler (banka, otel, bilet) daha kritik olur.",
    },
}

REFUSAL_OPTIONS: Dict[str, Dict[str, Any]] = {
    "none": {
        "label": "Hayır, hiç red almadım",
        "delta": 10,
        "reason": "Temiz vize geçmişi onay olasılığını belirgin şekilde artırır.",
    },
    "other_country": {
        "label": "Evet, başka bir ülkeden",
        "delta": -12,
        "reason": "Başka ülkeden red kaydı BAE değerlendirmesini doğrudan bağlamaz ama dosyanın güçlü olması gerekir.",
    },
    "uae": {
        "label": "Evet, BAE / Dubai vizesi reddedildi",
        "delta": -26,
        "reason": "Önceki BAE reddi sonrası başvuruda ek belge ve doğru gerekçelendirme şarttır.",
    },
}

# Opsiyonel 4. soru: seyahat amaci (skoru hafifce etkiler, vize onerisini belirler)
PURPOSE_OPTIONS: Dict[str, Dict[str, Any]] = {
    "tourism": {"label": "Turizm / tatil", "delta": 4, "visa": "visa_30_single"},
    "family": {"label": "Aile ziyareti", "delta": 2, "visa": "visa_30_single"},
    "business": {"label": "İş / ticaret", "delta": 3, "visa": "visa_30_multi"},
    "long_stay": {"label": "Uzun süreli kalış (30 günden fazla)", "delta": 0, "visa": "visa_60_single"},
    "transit": {"label": "Transit geçiş", "delta": 2, "visa": "visa_transit_48"},
}

LEVELS = [
    (85, "high", "Yüksek onay olasılığı", "Dosyanız güçlü görünüyor. Hemen başvuruya geçebilirsiniz."),
    (65, "medium", "İyi onay olasılığı", "Dosyanız uygun. Küçük iyileştirmelerle olasılığı daha da yükseltebilirsiniz."),
    (45, "review", "İncelenmesi gereken dosya", "Başvuru yapılabilir ancak danışmanımızın dosyanızı gözden geçirmesi önerilir."),
    (0, "low", "Risk taşıyan dosya", "Başvuru öncesi mutlaka bir danışmanımızla görüşmenizi öneriyoruz."),
]


def _clamp(value: int, low: int = 8, high: int = 96) -> int:
    return max(low, min(high, value))


def _level_for(score: int):
    for threshold, key, title, note in LEVELS:
        if score >= threshold:
            return key, title, note
    return LEVELS[-1][1], LEVELS[-1][2], LEVELS[-1][3]


def question_set() -> List[Dict[str, Any]]:
    """Frontend'in dinamik olarak render edebilecegi soru tanimlari."""

    def opts(source: Dict[str, Dict[str, Any]]):
        return [{"value": k, "label": v["label"]} for k, v in source.items()]

    return [
        {
            "key": "passport_validity",
            "title": "Pasaportunuzun geçerlilik süresi ne kadar?",
            "help": "BAE, giriş tarihinde en az 6 ay geçerli pasaport ister.",
            "options": opts(PASSPORT_OPTIONS),
        },
        {
            "key": "visa_history",
            "title": "Daha önce ABD, İngiltere, Schengen veya BAE vizesi aldınız mı?",
            "help": "Geçmiş vize kayıtları değerlendirmede olumlu etki yapar.",
            "options": opts(HISTORY_OPTIONS),
        },
        {
            "key": "refusal_history",
            "title": "Daha önce herhangi bir ülkeden vize reddi aldınız mı?",
            "help": "Red kaydı varsa dosyayı özel olarak hazırlıyoruz.",
            "options": opts(REFUSAL_OPTIONS),
        },
        {
            "key": "purpose",
            "title": "Seyahat amacınız nedir? (opsiyonel)",
            "help": "Size en uygun vize tipini önermek için kullanılır.",
            "optional": True,
            "options": opts(PURPOSE_OPTIONS),
        },
    ]


def _tips(answers: Dict[str, str], level: str) -> List[str]:
    tips: List[str] = []
    if answers.get("passport_validity") in {"under_6", "expired"}:
        tips.append("Pasaportunuzu yenileyin; BAE giriş tarihinde 6+ ay geçerlilik şartı arıyor.")
    if answers.get("visa_history") == "none":
        tips.append("İlk başvuruda gidiş-dönüş bileti ve otel rezervasyonunu eksiksiz yükleyin.")
    if answers.get("refusal_history") == "uae":
        tips.append("Önceki BAE reddinin gerekçesini bizimle paylaşın; dosyayı buna göre güçlendiriyoruz.")
    if answers.get("refusal_history") == "other_country":
        tips.append("Red geçmişini başvuruda şeffaf belirtin; danışmanımız uygun açıklama metnini hazırlar.")
    if answers.get("purpose") == "long_stay":
        tips.append("30 günden uzun kalışlar için 60 günlük vize tipini seçmelisiniz.")
    if answers.get("purpose") == "business":
        tips.append("İş seyahatlerinde çok girişli vize, tekrar başvuru maliyetinden tasarruf ettirir.")

    tips.append("Vesikalık fotoğrafınız beyaz fon ve son 6 ay içinde çekilmiş olmalı.")
    tips.append("Pasaportunuzun kimlik sayfasını net ve kesilmemiş şekilde yükleyin.")
    if level in {"review", "low"}:
        tips.append("Ücretsiz ön kontrol için WhatsApp üzerinden danışmanımıza yazabilirsiniz.")
    return tips[:5]


def evaluate(answers: Dict[str, str]) -> Dict[str, Any]:
    """Cevaplari skora ve onerilere donusturur."""
    score = BASE_SCORE
    factors: List[Dict[str, Any]] = []
    blockers: List[str] = []

    mapping = [
        ("passport_validity", PASSPORT_OPTIONS),
        ("visa_history", HISTORY_OPTIONS),
        ("refusal_history", REFUSAL_OPTIONS),
        ("purpose", PURPOSE_OPTIONS),
    ]

    for key, source in mapping:
        value = (answers.get(key) or "").strip()
        conf = source.get(value)
        if not conf:
            continue
        delta = int(conf.get("delta", 0))
        score += delta
        if conf.get("reason"):
            factors.append(
                {
                    "key": key,
                    "label": conf["label"],
                    "delta": delta,
                    "impact": "positive" if delta > 0 else ("negative" if delta < 0 else "neutral"),
                    "reason": conf["reason"],
                }
            )
        if conf.get("blocker"):
            blockers.append(conf["blocker"])

    score = _clamp(int(round(score)))
    level, level_title, level_note = _level_for(score)

    purpose = (answers.get("purpose") or "").strip()
    recommended = PURPOSE_OPTIONS.get(purpose, {}).get("visa") or "visa_30_single"

    return {
        "score": score,
        "level": level,
        "level_title": level_title,
        "level_note": level_note,
        "factors": factors,
        "blockers": blockers,
        "tips": _tips(answers, level),
        "recommended_visa_type_id": recommended,
        "can_apply": not blockers,
        "disclaimer": (
            "Bu sonuç bilgilendirme amaçlı bir ön değerlendirmedir. Nihai karar "
            "BAE göçmenlik makamlarına (GDRFA/ICP) aittir."
        ),
    }
