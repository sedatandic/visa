"""Tum test dosyalari icin tek, kapanmayan event loop.

Motor istemcisi (db.py modul seviyesinde) ilk kullanildigi event loop'a baglanir.
Testler `asyncio.run()` / `new_event_loop()` + `close()` kullandigi icin bir dosya
loop'u kapatinca sonraki dosyalar "Event loop is closed" hatasi aliyordu.
Burada surec basina tek bir loop paylasilir ve kapatma istekleri yok sayilir.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Testler ADMIN_LOGIN_EMAIL / MONGO_URL gibi degerleri env'den okur
load_dotenv(os.path.join(BACKEND_DIR, ".env"))
load_dotenv(os.path.join(BACKEND_DIR, "..", "frontend", ".env"))

_LOOP = asyncio.new_event_loop()
_LOOP._dv_close = _LOOP.close  # gercek kapatma referansi (oturum sonunda kullanilir)
_LOOP.close = lambda: None  # type: ignore[method-assign]
asyncio.set_event_loop(_LOOP)


def _shared_new_event_loop() -> asyncio.AbstractEventLoop:
    asyncio.set_event_loop(_LOOP)
    return _LOOP


def _shared_run(coro, **_kwargs):
    return _LOOP.run_until_complete(coro)


asyncio.new_event_loop = _shared_new_event_loop  # type: ignore[assignment]
asyncio.run = _shared_run  # type: ignore[assignment]


def pytest_sessionfinish(session, exitstatus) -> None:  # noqa: ARG001
    """Oturum sonunda loop'u gercekten kapat."""
    try:
        _LOOP._dv_close()
    except Exception:  # pragma: no cover
        pass
