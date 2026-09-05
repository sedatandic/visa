"""Imzali, sureli dosya erisim baglantilari.

/api/files/{id} artik herkese acik degil. Her baglanti JWT_SECRET ile HMAC
imzalanmis, son kullanma tarihi olan bir jeton tasir. Jetonu yalnizca sunucu
uretir: yukleme yanitinda, basvuru/siparis gorunumlerinde (serialize_doc) ve
e-posta baglantilarinda. Yonetici oturum jetonu (Bearer) da gecerli sayilir.
"""

import base64
import hashlib
import hmac
import os
import time

import jwt

# Baglanti gecerlilik sureleri (saniye)
TTL_VIEW = 12 * 3600  # panel / takip sayfasi gorunumleri
TTL_UPLOAD = 7 * 24 * 3600  # yukleme sonrasi onizleme (taslak geri yuklenebilir)
TTL_TRANSFER = 6 * 3600  # Zami aktarimi / RPA indirmeleri
TTL_EMAIL = 180 * 24 * 3600  # e-posta ve WhatsApp indirme baglantilari


def _secret() -> str:
    secret = os.environ.get("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET tanimli degil: imzali dosya baglantisi uretilemez.")
    return secret


def _sign(file_id: str, exp: int) -> str:
    mac = hmac.new(_secret().encode(), f"{file_id}.{exp}".encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode().rstrip("=")


def make_token(file_id: str, ttl: int = TTL_VIEW) -> str:
    exp = int(time.time()) + int(ttl)
    return f"{exp}.{_sign(file_id, exp)}"


def token_valid(file_id: str, token: str) -> bool:
    exp_raw, _, sig = (token or "").partition(".")
    if not sig or not exp_raw.isdigit():
        return False
    exp = int(exp_raw)
    if exp < int(time.time()):
        return False
    return hmac.compare_digest(sig, _sign(file_id, exp))


def admin_token_valid(token: str) -> bool:
    """Yonetici oturum jetonu dosyalara dogrudan erisebilir."""
    if not token:
        return False
    try:
        data = jwt.decode(token, _secret(), algorithms=["HS256"])
    except Exception:
        return False
    return data.get("role") == "admin"


def file_path(file_id: str, ttl: int = TTL_VIEW, download: bool = False) -> str:
    """Site ici kullanim icin imzali gorece yol."""
    if not file_id:
        return ""
    path = f"/api/files/{file_id}?t={make_token(file_id, ttl)}"
    return f"{path}&download=1" if download else path


def file_url(origin: str, file_id: str, ttl: int = TTL_EMAIL, download: bool = False) -> str:
    """E-posta/WhatsApp gibi site disi baglantilar icin tam adres."""
    if not file_id:
        return ""
    return f"{(origin or '').rstrip('/')}{file_path(file_id, ttl, download)}"


_SUFFIX = "_file_id"


def add_file_urls(doc: dict, ttl: int = TTL_VIEW) -> dict:
    """Sozlukteki her dosya kimligi yanina imzali baglanti ekler.

    `serialize_doc` her seviyede cagirdigi icin ozyineleme gerekmez.
    """
    for key, value in list(doc.items()):
        if isinstance(value, str) and value:
            if key == "file_id":
                doc["file_url"] = file_path(value, ttl)
            elif key.endswith(_SUFFIX):
                doc[f"{key[: -len(_SUFFIX)]}_url"] = file_path(value, ttl)
        elif key == "other_file_ids" and isinstance(value, list):
            doc["other_file_urls"] = [file_path(v, ttl) for v in value if isinstance(v, str) and v]
    return doc
