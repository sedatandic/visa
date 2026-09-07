"""Emergent Object Storage wrapper (proven in scripts/test_core.py)."""
import logging
import os

import requests

logger = logging.getLogger(__name__)

STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
APP_NAME = "dubaivize"

_storage_key = None

MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "pdf": "application/pdf",
}


def init_storage(force: bool = False):
    global _storage_key
    if _storage_key and not force:
        return _storage_key
    key = os.environ.get("EMERGENT_LLM_KEY")
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": key}, timeout=30)
    resp.raise_for_status()
    _storage_key = resp.json()["storage_key"]
    return _storage_key


def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data,
        timeout=120,
    )
    if resp.status_code == 404:
        key = init_storage(force=True)
        resp = requests.put(
            f"{STORAGE_URL}/objects/{path}",
            headers={"X-Storage-Key": key, "Content-Type": content_type},
            data=data,
            timeout=120,
        )
    resp.raise_for_status()
    return resp.json()


def get_object(path: str):
    key = init_storage()
    resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    if resp.status_code == 404:
        key = init_storage(force=True)
        resp = requests.get(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")


def delete_object(path: str) -> str:
    """Nesne icerigini yok eder ve ne yapildigini dondurur.

    Emergent Object Storage DELETE'i desteklemiyor (405; yalniz PUT/GET/HEAD).
    Bu yuzden silme denemesi basarisiz olursa nesneyi 0 baytlik veriyle uzerine
    yazarak icerigi imha ederiz ("wiped"). Kayit tarafindaki tombstone islemi
    cagirana aittir.
    """
    key = init_storage()
    try:
        resp = requests.delete(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
        if resp.status_code == 404:
            return "missing"
        if resp.status_code == 403:
            key = init_storage(force=True)
            resp = requests.delete(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key}, timeout=60)
        if resp.ok:
            return "deleted"
    except requests.RequestException as exc:
        logger.warning("storage delete istegi basarisiz (%s): %s", path, exc)

    put_object(path, b"", "application/octet-stream")
    return "wiped"
