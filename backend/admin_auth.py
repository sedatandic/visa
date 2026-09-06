"""Yonetici oturumu: jeton uretimi, dogrulama ve kod ozeti (tek kaynak).

`routes_admin` ve `routes_zami` bu modulden alir; `file_access` da ayni
JWT_SECRET ile imzalanmis dosya baglantilarini dogrular.
"""

import os
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Optional

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGO = "HS256"
SESSION_DAYS = 30

security = HTTPBearer(auto_error=False)


def create_token(email: str) -> str:
    """Yonetici oturum jetonu: ayni cihazda 30 gun gecerli."""
    payload = {
        "sub": email,
        "role": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


async def require_admin(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    if not creds or not creds.credentials:
        raise HTTPException(401, "Yetkisiz erisim. Lutfen giris yapin.")
    data: dict = {}
    try:
        data = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(401, "Oturum suresi doldu. Lutfen tekrar giris yapin.") from exc
    except Exception as exc:
        raise HTTPException(401, "Gecersiz oturum.") from exc
    if data.get("role") != "admin":
        raise HTTPException(403, "Bu islem icin yetkiniz yok.")
    return data


def hash_code(code: str) -> str:
    """Tek kullanimlik giris kodunun DB'de saklanan ozeti."""
    return sha256(f"{JWT_SECRET}:{code}".encode("utf-8")).hexdigest()
