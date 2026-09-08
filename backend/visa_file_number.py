"""Vize PDF'inden GDRFA dosya numarasini okur ve dogrulama baglantisi uretir.

Dubai giris izni belgesinde dosya numarasi `201/2026/1234567` bicimindedir
(emirlik kodu / yil / seri no). GDRFA sorgulama sayfasi bu numarayi bolu isareti
olmadan ister ve ASP.NET ViewState kullandigi icin hazir dolu bir baglantiyla
acilamaz. Bu yuzden numara belge geldigi an otomatik okunur ve musteriye kendi
dogrulama sayfamiz gonderilir: numara, ad ve dogum tarihi tek dokunusla
kopyalanir, musteri PDF icinde numara aramak zorunda kalmaz.
"""

import asyncio
import logging
import re

import pymupdf

import file_access
from db import applications_col, uploads_col
from storage import get_object

logger = logging.getLogger(__name__)

# 201/2026/1234567 - yil 19xx/20xx olmali ki tarih/tutar yanlislikla yakalanmasin
FILE_NUMBER_RE = re.compile(r"\b(\d{3})\s*/\s*((?:19|20)\d{2})\s*/\s*(\d{4,9})\b")

# Etiketli aramada once bu kelimelerin gectigi satirlara bakilir
LABELS = ("file no", "file number", "رقم الملف", "entry permit", "permit no")


def normalize(value: str) -> str:
    """Serbest metinden `201/2026/1234567` bicimini cikarir; bulamazsa bos doner."""
    match = FILE_NUMBER_RE.search(value or "")
    return "/".join(match.groups()) if match else ""


def plain(file_number: str) -> str:
    """GDRFA formuna girilecek hali: sadece rakamlar."""
    return re.sub(r"\D", "", file_number or "")


def extract_all_from_text(text: str) -> list:
    """Belgedeki tum dosya numaralarini gorunum sirasinda, tekrarsiz dondurur."""
    seen, found = set(), []
    for match in FILE_NUMBER_RE.finditer(text or ""):
        number = "/".join(match.groups())
        if number not in seen:
            seen.add(number)
            found.append(number)
    return found


def extract_from_text(text: str) -> str:
    """Once etiketli satirlarda, sonra tum metinde arar."""
    lines = (text or "").splitlines()
    for index, line in enumerate(lines):
        if not any(label in line.lower() for label in LABELS):
            continue
        # Numara etiketle ayni satirda ya da hemen altinda olabilir
        for candidate in (line, *lines[index + 1 : index + 3]):
            found = normalize(candidate)
            if found:
                return found
    return normalize(text)


def _pdf_text(data: bytes) -> str:
    with pymupdf.open(stream=data, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)


async def extract_from_upload(file_id: str) -> list:
    """Vize belgesindeki dosya numaralarini dondurur (okunamazsa bos liste)."""
    if not file_id:
        return []
    record = await uploads_col.find_one({"id": file_id, "is_deleted": False})
    if not record or "pdf" not in (record.get("content_type") or ""):
        return []  # taranmis gorseller icin OCR yok, admin elle girer
    try:
        data, _ = await asyncio.to_thread(get_object, record["storage_path"])
        text = await asyncio.to_thread(_pdf_text, data)
    except Exception as exc:
        logger.warning("vize dosya numarasi okunamadi (%s): %s", file_id, exc)
        return []

    numbers = extract_all_from_text(text)
    labelled = extract_from_text(text)
    if labelled and labelled in numbers:
        numbers = [labelled] + [n for n in numbers if n != labelled]
    if not numbers:
        logger.info("vize belgesinde dosya numarasi bulunamadi (%s)", file_id)
    return numbers


async def annotate(application_id: str, visa_result: dict) -> dict:
    """Dosya numaralarini okuyup basvuruya ve donen visa_result'a yazar."""
    numbers = await extract_from_upload(visa_result.get("file_id", ""))
    if not numbers:
        return visa_result
    await applications_col.update_one(
        {"id": application_id},
        {
            "$set": {
                "visa_result.file_numbers": numbers,
                "visa_result.file_number": numbers[0],
            }
        },
    )
    return {**visa_result, "file_numbers": numbers, "file_number": numbers[0]}


def verify_url(origin: str, application_id: str) -> str:
    """Musteriye gonderilen imzali dogrulama sayfasi baglantisi."""
    if not (origin and application_id):
        return ""
    token = file_access.make_token(application_id, file_access.TTL_EMAIL)
    return f"{origin.rstrip('/')}/vize-dogrula/{application_id}?t={token}"
