"""Belge saklama politikasi: yuklenen dosyalar 90 gun sonra kalici olarak silinir.

Sitede verdigimiz "belgeleriniz 90 gun sonra otomatik silinir" taahhudunun
teknik karsiligi burasi. Gunde bir kez calisir; suresi gecen yuklemeleri hem
nesne depolamadan hem de kayittan temizler.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from db import uploads_col
from storage import delete_object

logger = logging.getLogger(__name__)

RETENTION_DAYS = 90
PURGE_INTERVAL_SECONDS = 24 * 3600


async def purge_expired_uploads() -> dict:
    """Saklama suresi gecen yuklemeleri siler, sayilari dondurur.

    Depo silmeyi reddederse dosya 0 bayta indirilir; her durumda kayit
    tombstone'lanir ki dosya bir daha servis edilemesin.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    purged = 0
    wiped = 0
    failed = 0
    cursor = uploads_col.find(
        {"is_deleted": {"$ne": True}, "created_at": {"$lt": cutoff}},
        {"id": 1, "storage_path": 1},
    )
    async for doc in cursor:
        outcome = "failed"
        try:
            outcome = await asyncio.to_thread(delete_object, doc["storage_path"])
        except Exception as exc:
            failed += 1
            logger.error("retention: %s icerigi imha edilemedi: %s", doc.get("id"), exc)
        if outcome == "wiped":
            wiped += 1
        # Depo temizligi basarisiz olsa da kayit kapatilir: storage_path silinince
        # imzali baglantilar dahil hicbir yol dosyaya erisemez.
        await uploads_col.update_one(
            {"id": doc["id"]},
            {
                "$set": {
                    "is_deleted": True,
                    "purged_at": datetime.now(timezone.utc),
                    "purge_reason": f"retention_{RETENTION_DAYS}d",
                    "purge_outcome": outcome,
                },
                "$unset": {"storage_path": ""},
            },
        )
        purged += 1
    if purged or failed:
        logger.info("retention purge: %s kayit kapatildi (%s uzerine yazildi), %s hata", purged, wiped, failed)
    if failed:
        logger.error("retention purge: %s dosyanin icerigi depodan silinemedi, inceleyin", failed)
    return {"purged": purged, "wiped": wiped, "failed": failed, "cutoff": cutoff.isoformat()}


async def retention_loop() -> None:
    """Gunluk saklama temizligi dongusu."""
    while True:
        try:
            await purge_expired_uploads()
        except Exception as exc:
            logger.error("retention loop hatasi: %s", exc)
        await asyncio.sleep(PURGE_INTERVAL_SECONDS)
