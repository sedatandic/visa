"""Bellek ici hiz siniri: tek surecte calisan basit kayan pencere sayaci.

Amaci: e-posta/kod bombardimani ve pahali AI cagrilarinin kotuye kullanimini
onlemek. Sayaclar uvicorn surecinde tutulur (birden fazla replikada Redis gerekir).
"""

import os
from collections import deque
from datetime import datetime, timezone
from typing import Optional

import time

from fastapi import HTTPException, Request

_MAX_KEYS = 5000
_hits: dict[str, deque] = {}

# Uygulamanin onunde duran guvenilir proxy sayisi (Cloudflare + platform ingress ...).
# X-Forwarded-For zincirinde SAGDAN bu kadar hop atlanarak gercek istemci bulunur;
# istemcinin basa ekledigi uydurma degerler boylece dikkate alinmaz.
TRUSTED_PROXY_HOPS = max(1, int(os.environ.get("TRUSTED_PROXY_HOPS") or 3))


def client_ip(request: Request) -> str:
    """Sahtelenemez istemci kimligi: XFF zincirinin sagindan guvenilir hop'lar atlanir."""
    chain = [p.strip() for p in (request.headers.get("x-forwarded-for") or "").split(",") if p.strip()]
    if chain:
        return chain[max(0, len(chain) - TRUSTED_PROXY_HOPS)]
    return request.client.host if request.client else "unknown"


def check(key: str, limit: int, window_seconds: int, message: str) -> None:
    """Anahtar icin pencere basina istek sayisini sinirlar, asilirsa 429 atar."""
    now = time.monotonic()
    if len(_hits) > _MAX_KEYS:
        stale = [k for k, q in _hits.items() if not q or now - q[-1] > window_seconds]
        for k in stale:
            _hits.pop(k, None)
    hits = _hits.setdefault(key, deque())
    while hits and now - hits[0] > window_seconds:
        hits.popleft()
    if len(hits) >= limit:
        raise HTTPException(429, message)
    hits.append(now)


def allow(key: str, limit: int, window_seconds: int) -> bool:
    """check() ile ayni sayac; sinir asildiginda 429 yerine False doner.

    Kayit/siparis akisini bozmadan yalnizca bildirim e-postasini atlamak icin.
    """
    try:
        check(key, limit, window_seconds, "rate limited")
    except HTTPException:
        return False
    return True


def as_utc(value) -> Optional[datetime]:
    if not isinstance(value, datetime):
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def code_request_window(
    doc: Optional[dict],
    now: datetime,
    cooldown_seconds: int,
    max_per_hour: int,
) -> tuple[datetime, int]:
    """Tek kullanimlik kod talebi kurallari: bekleme suresi + saatlik ust sinir.

    Geriye yeni pencere baslangicini ve o pencerede kullanilmis talep sayisini doner.
    """
    last_sent = as_utc((doc or {}).get("created_at"))
    if last_sent and (now - last_sent).total_seconds() < cooldown_seconds:
        raise HTTPException(429, "Yeni kod icin lutfen 1 dakika bekleyin.")
    window_start = as_utc((doc or {}).get("window_start")) or now
    count = int((doc or {}).get("request_count") or 0)
    if (now - window_start).total_seconds() >= 3600:
        return now, 0
    if count >= max_per_hour:
        raise HTTPException(429, "Cok fazla kod talebi. Lutfen bir saat sonra tekrar deneyin.")
    return window_start, count
