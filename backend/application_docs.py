"""Basvuru e-postalarina eklenecek belgeleri toplar (form PDF + yuklenen evraklar)."""

import asyncio
import logging
import os
import re
import unicodedata

import file_access
from application_pdf import build_application_pdf
from db import uploads_col
from storage import get_object

logger = logging.getLogger(__name__)

# Resend toplam 40 MB kabul ediyor; guvenli tarafta kalip fazlasini baglanti olarak veriyoruz.
MAX_TOTAL_BYTES = 18 * 1024 * 1024
SITE_URL = (os.environ.get("PUBLIC_SITE_URL") or "").strip().strip('"').rstrip("/")

_TR_MAP = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
_ALLOWED_EXT = {"jpg", "jpeg", "png", "webp", "pdf"}


def _slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", (text or "").translate(_TR_MAP))
    ascii_text = ascii_text.encode("ascii", "ignore").decode()
    slug = re.sub(r"[^A-Za-z0-9]+", "-", ascii_text).strip("-").lower()
    return re.sub(r"-{2,}", "-", slug) or "belge"


def _traveler_targets(travelers: list) -> list[tuple[str, str]]:
    """Her yolcunun pasaport ve vesikalik dosyalari."""
    out: list[tuple[str, str]] = []
    for index, traveler in enumerate(travelers or [], start=1):
        docs = traveler.get("documents") or {}
        name = f"{traveler.get('first_name', '')} {traveler.get('last_name', '')}".strip()
        name = name or f"{index}. yolcu"
        for label, key in (("pasaport", "passport_file_id"), ("vesikalık fotoğraf", "photo_file_id")):
            if docs.get(key):
                out.append((f"{name} - {label}", docs[key]))
    return out


def _extra_targets(extra: dict) -> list[tuple[str, str]]:
    """Seyahat evraklari: bilet, otel ve diger dosyalar."""
    out: list[tuple[str, str]] = []
    for label, key in (("Uçak bileti", "ticket_file_id"), ("Otel rezervasyonu", "hotel_file_id")):
        if extra.get(key):
            out.append((label, extra[key]))
    for index, file_id in enumerate(extra.get("other_file_ids") or [], start=1):
        if file_id:
            out.append((f"Diğer evrak {index}", file_id))
    return out


def _targets(app_doc: dict) -> list[tuple[str, str]]:
    """(etiket, file_id) listesi: yolcu pasaport/vesikalik + seyahat evraklari."""
    return _traveler_targets(app_doc.get("travelers") or []) + _extra_targets(
        app_doc.get("extra_documents") or {}
    )


def _extension(record: dict) -> str:
    ext = (record.get("original_filename") or "").rsplit(".", 1)[-1].lower()
    if ext in _ALLOWED_EXT:
        return ext
    return "pdf" if record.get("content_type") == "application/pdf" else "jpg"


async def collect_application_documents(app_doc: dict, with_data: bool = True) -> list[dict]:
    """Yuklenen evraklari (istege gore icerikleriyle) toplar; okunamayan dosyayi atlar."""
    items: list[dict] = []
    used = 0
    for index, (label, file_id) in enumerate(_targets(app_doc), start=1):
        record = await uploads_col.find_one({"id": file_id, "is_deleted": False})
        if not record:
            continue
        item = {
            "label": label,
            "file_id": file_id,
            "filename": f"{index:02d}-{_slug(label)}.{_extension(record)}",
            "content_type": record.get("content_type") or "application/octet-stream",
            "size": int(record.get("size") or 0),
            "data": None,
            "url": file_access.file_url(SITE_URL, file_id, file_access.TTL_EMAIL, download=True),
        }
        if with_data and used + item["size"] <= MAX_TOTAL_BYTES:
            try:
                data, _content_type = await asyncio.to_thread(get_object, record["storage_path"])
                item["data"] = data
                used += len(data)
            except Exception as exc:  # pragma: no cover - object storage hatasi
                logger.warning("belge eki okunamadi (%s): %s", file_id, exc)
        items.append(item)
    return items


def document_listing(items: list[dict]) -> list[dict]:
    """E-posta govdesi ve PDF icin icerik tasimayan ozet liste."""
    return [
        {
            "label": item["label"],
            "filename": item["filename"],
            "attached": bool(item.get("data")),
            "url": item["url"],
        }
        for item in items
    ]


def form_filename(app_doc: dict) -> str:
    return f"Basvuru-Formu-{app_doc.get('reference_code', 'DV')}.pdf"


async def application_form_bytes(app_doc: dict) -> bytes:
    """Panelden/takip sayfasindan indirilen tek sayfalik form."""
    items = await collect_application_documents(app_doc, with_data=False)
    listing = [{**item, "attached": True} for item in document_listing(items)]
    return build_application_pdf(app_doc, listing)


async def application_email_bundle(app_doc: dict) -> dict:
    """E-posta ekleri (form PDF + evraklar) ve govdede gosterilecek belge dokumu."""
    documents = await collect_application_documents(app_doc)
    listing = document_listing(documents)
    attachments: list[dict] = []
    name = ""
    try:
        pdf = build_application_pdf(app_doc, listing)
        name = form_filename(app_doc)
        attachments.append({"filename": name, "content": pdf, "content_type": "application/pdf"})
    except Exception as exc:  # pragma: no cover - PDF uretimi
        logger.error("basvuru formu PDF uretilemedi: %s", exc)
    for item in documents:
        if item["data"]:
            attachments.append(
                {
                    "filename": item["filename"],
                    "content": item["data"],
                    "content_type": item["content_type"],
                }
            )
    return {"attachments": attachments, "documents": listing, "form_filename": name}
