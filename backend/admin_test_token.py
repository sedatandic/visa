"""Testler icin yonetici jetonu.

Yonetici girisi artik yalnizca e-posta + tek kullanimlik kod ile yapilir. Test
betiklerinin her calismada gercek e-posta gondermemesi icin jeton, JWT_SECRET
ile dogrudan uretilir (pod icinden .env erisimi ile).
"""

import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def admin_token(hours: int = 12) -> str:
    email = (os.environ.get("ADMIN_LOGIN_EMAIL") or "info@dubaivizehatti.com").strip().lower()
    payload = {
        "sub": email,
        "role": "admin",
        "exp": datetime.now(timezone.utc) + timedelta(hours=hours),
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")


if __name__ == "__main__":
    print(admin_token())
