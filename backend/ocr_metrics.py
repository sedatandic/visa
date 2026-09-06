"""Pasaport OCR performans olcumu.

Amac: "tek pasaport fotografiyla form ne kadar hizli doluyor?" sorusunu
olcmek ve hangi alanlarin okunamadigini raporlamak. Her okuma denemesi
sure + alan kapsamiyla `ocr_metrics` koleksiyonuna yazilir; admin panel
ozet raporu bu kayitlardan uretilir.
"""

import logging
from datetime import datetime, timedelta, timezone

from db import db

logger = logging.getLogger(__name__)

metrics_col = db["ocr_metrics"]

# Formda otomatik dolmasi beklenen alanlar (kullaniciya sorulanlar + Zami icin
# gerekli olanlar). Rapor bu liste uzerinden "doluluk orani" hesaplar.
TRACKED_FIELDS = [
    "first_name",
    "last_name",
    "birth_date",
    "gender",
    "passport_no",
    "passport_expiry",
    "nationality",
    "national_id",
    "passport_issue_date",
    "birth_place",
    "passport_issue_place",
]

FIELD_LABELS = {
    "first_name": "Ad",
    "last_name": "Soyad",
    "birth_date": "Doğum Tarihi",
    "gender": "Cinsiyet",
    "passport_no": "Pasaport No",
    "passport_expiry": "Geçerlilik Tarihi",
    "nationality": "Uyruk",
    "national_id": "T.C. Kimlik No",
    "passport_issue_date": "Veriliş Tarihi",
    "birth_place": "Doğum Yeri",
    "passport_issue_place": "Veriliş Yeri",
}

# Kullaniciya sorulan ve OCR ile doldurulmasi kritik olan alanlar
CORE_FIELDS = ["first_name", "last_name", "birth_date", "passport_no", "passport_expiry"]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def field_coverage(data: dict) -> dict:
    """Okunan alanlari filled/missing olarak ayirir."""
    data = data or {}
    filled = [f for f in TRACKED_FIELDS if str(data.get(f) or "").strip()]
    missing = [f for f in TRACKED_FIELDS if f not in filled]
    core_missing = [f for f in CORE_FIELDS if f in missing]
    return {
        "filled": filled,
        "missing": missing,
        "core_missing": core_missing,
        "core_complete": not core_missing,
    }


async def record_attempt(
    *, file_id: str, duration_ms: int, ok: bool, reason: str = "", data: dict | None = None
) -> dict:
    """Bir OCR denemesini kaydeder ve kapsam ozetini dondurur."""
    coverage = field_coverage(data or {})
    doc = {
        "file_id": file_id,
        "at": _now(),
        "duration_ms": int(duration_ms),
        "ok": bool(ok),
        "reason": reason,
        "filled": coverage["filled"],
        "missing": coverage["missing"],
        "core_complete": coverage["core_complete"],
        "confidence": (data or {}).get("confidence"),
    }
    try:
        await metrics_col.insert_one(dict(doc))
    except Exception as exc:  # olcum, ana akisi asla bozmamali
        logger.warning("ocr metric insert failed: %s", exc)
    return coverage


def _percentile(values: list, ratio: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * ratio)))
    return int(ordered[index])


EMPTY_SUMMARY = {
    "total": 0,
    "success_rate": 0,
    "core_complete_rate": 0,
    "avg_ms": 0,
    "p50_ms": 0,
    "p90_ms": 0,
    "fields": [],
    "top_missing": [],
}


def _rate(part: int, whole: int) -> int:
    return round(part * 100 / whole) if whole else 0


def _duration_stats(rows: list) -> dict:
    durations = [r.get("duration_ms") or 0 for r in rows if r.get("duration_ms")]
    return {
        "avg_ms": int(sum(durations) / len(durations)) if durations else 0,
        "p50_ms": _percentile(durations, 0.5),
        "p90_ms": _percentile(durations, 0.9),
    }


def _field_rows(ok_rows: list) -> list:
    """Her alan icin dolum oranini hesaplar."""
    rows = []
    for field in TRACKED_FIELDS:
        hits = len([r for r in ok_rows if field in (r.get("filled") or [])])
        rows.append(
            {
                "key": field,
                "label": FIELD_LABELS.get(field, field),
                "fill_rate": _rate(hits, len(ok_rows)),
                "core": field in CORE_FIELDS,
            }
        )
    return rows


def summarize(rows: list) -> dict:
    """Kayitlardan rapor uretir (saf fonksiyon, test edilebilir)."""
    total = len(rows)
    if not total:
        return dict(EMPTY_SUMMARY)

    ok_rows = [r for r in rows if r.get("ok")]
    core_ok = len([r for r in ok_rows if r.get("core_complete")])
    fields = _field_rows(ok_rows)

    return {
        "total": total,
        "success_rate": _rate(len(ok_rows), total),
        "core_complete_rate": _rate(core_ok, len(ok_rows)),
        **_duration_stats(rows),
        "fields": fields,
        "top_missing": [f for f in sorted(fields, key=lambda x: x["fill_rate"]) if f["fill_rate"] < 100][:5],
    }


async def report(days: int = 30) -> dict:
    """Son `days` gunun OCR performans raporu."""
    since = _now() - timedelta(days=max(1, days))
    rows = await metrics_col.find({"at": {"$gte": since}}).sort("at", -1).limit(500).to_list(500)
    summary = summarize(rows)
    summary["days"] = days
    summary["recent"] = [
        {
            "at": r.get("at").isoformat() if r.get("at") else "",
            "duration_ms": r.get("duration_ms"),
            "ok": r.get("ok"),
            "reason": r.get("reason") or "",
            "missing": [FIELD_LABELS.get(m, m) for m in (r.get("missing") or [])],
        }
        for r in rows[:10]
    ]
    return summary
