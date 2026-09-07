"""Musteriye gonderilen baglantilarin kok adresi (origin) cozumlemesi."""

import os
from typing import Optional

from fastapi import Request


def public_base_url() -> str:
    """Ortam degiskeninden kok adres (istek baglami yokken kullanilir)."""
    return (os.environ.get("PUBLIC_BASE_URL") or os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")


def resolve_origin(origin_url: Optional[str], request: Optional[Request]) -> str:
    """Istemciden gelen origin degerini dogrular, gecersizse sunucu adresini kullanir."""
    origin = (origin_url or "").rstrip("/")
    if origin.startswith("http"):
        return origin
    if request is not None:
        return str(request.base_url).rstrip("/")
    return public_base_url()
