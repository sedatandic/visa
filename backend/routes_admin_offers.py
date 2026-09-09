"""Yonetici: paylasilabilir teklif linkleri (`/api/admin/offer-links`).

Teklif mantigi `offer_links.py` icinde; bu dosya yalnizca HTTP katmani.
`routes_admin` zaten cok genis oldugu icin bu alan ayri router'da tutuluyor.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

import offer_links
from admin_auth import require_admin
from db import offer_links_col
from models import OfferLinkIn

logger = logging.getLogger(__name__)
router = APIRouter()

LIST_LIMIT = 60


@router.get("/admin/offer-links")
async def admin_list_offer_links(admin: dict = Depends(require_admin)) -> dict:
    """Son teklif linkleri: durum, goruntulenme ve paylasim baglantilari."""
    docs = await offer_links_col.find().sort("created_at", -1).limit(LIST_LIMIT).to_list(LIST_LIMIT)
    items = [offer_links.admin_view(doc) for doc in docs]
    return {
        "items": items,
        "total": len(items),
        "active": sum(1 for item in items if item["status"] == "active"),
        "used": sum(1 for item in items if item["status"] == "used"),
        "site_url": offer_links.site_url(),
    }


@router.post("/admin/offer-links")
async def admin_create_offer_link(payload: OfferLinkIn, admin: dict = Depends(require_admin)) -> dict:
    doc = await offer_links.create_offer(payload, created_by=admin.get("sub", ""))
    logger.info("offer link created: %s (%s)", doc["token"], doc["title"])
    return offer_links.admin_view(doc)


@router.delete("/admin/offer-links/{offer_id}")
async def admin_disable_offer_link(offer_id: str, admin: dict = Depends(require_admin)) -> dict:
    """Linki kapatir: musteri actiginda 404 doner (kayit gecmiste kalir)."""
    result = await offer_links_col.update_one(
        {"id": offer_id},
        {"$set": {"active": False, "disabled_at": datetime.now(timezone.utc)}},
    )
    if not result.matched_count:
        raise HTTPException(404, "Teklif bulunamadi.")
    return {"ok": True, "id": offer_id, "status": "disabled"}
