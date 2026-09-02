"""Zami Tours portali icin Playwright tabanli yarim otomatik RPA.

Girişte CAPTCHA + OTP oldugu icin login adiminda insan onayi gerekir:
1) `start_session()` -> tarayici acilir, login sayfasindaki captcha gorseli
   base64 olarak admin panelene dondurulur.
2) `submit_login(session_id, captcha, otp)` -> alanlar doldurulur, gerekiyorsa
   OTP istenir; basarili olursa oturum cerezleri (storage_state) saklanir.
3) `fill_application(...)` -> saklanan oturumla basvuru formu doldurulur;
   `dry_run` acikken gonderim yapilmaz, sadece ekran goruntusu alinir.
"""

import asyncio
import base64
import logging
import os
import uuid
from datetime import datetime, timezone

from db import settings_col
from zami import SESSION_KEY, get_mapping, log_event, match_status, raw_credentials

logger = logging.getLogger(__name__)


def _ensure_browser_path():
    """Playwright tarayici dizinini bulur (ortam degiskeni tanimli degilse)."""
    if os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
        return
    for candidate in ("/pw-browsers", "/ms-playwright", os.path.expanduser("~/.cache/ms-playwright")):
        try:
            if os.path.isdir(candidate) and any(
                name.startswith("chromium") for name in os.listdir(candidate)
            ):
                os.environ["PLAYWRIGHT_BROWSERS_PATH"] = candidate
                logger.info("playwright browsers path set to %s", candidate)
                return
        except Exception:
            continue


_ensure_browser_path()

BROWSER_MISSING_MSG = (
    "Tarayıcı motoru (Chromium) sunucuda bulunamadı. Robot modu kullanılamıyor; "
    "tarayıcı yardımcısı (bookmarklet) ile aktarım yapabilirsiniz."
)


def _chrome_executable() -> str | None:
    """Sistemde hazir bulunan Chromium/Chrome yolunu dondurur (varsa)."""
    import shutil

    candidates = [
        os.environ.get("PLAYWRIGHT_CHROME_EXECUTABLE_PATH"),
        "/usr/local/bin/browser-use-chromium",
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("google-chrome"),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


async def _launch_browser(pw):
    """Once paketle gelen tarayiciyi, olmazsa sistem Chromium'unu kullanir."""
    args = ["--no-sandbox", "--disable-dev-shm-usage"]
    try:
        return await pw.chromium.launch(headless=True, args=args)
    except Exception as exc:
        executable = _chrome_executable()
        if not executable:
            raise
        logger.warning("bundled chromium unavailable (%s); using %s", exc, executable)
        return await pw.chromium.launch(headless=True, args=args, executable_path=executable)

_sessions: dict = {}
SESSION_IDLE_LIMIT = 900  # 15 dk

LOGIN_PATH = "/login"
CAPTCHA_IMG = 'img[alt="Captcha"]'
OTP_SELECTORS = ['input[name="otp"]', 'input[name="OTP"]', 'input[name="code"]', 'input[name="token"]']


def _now():
    return datetime.now(timezone.utc)


async def _launch():
    from playwright.async_api import async_playwright

    _ensure_browser_path()
    pw = await async_playwright().start()
    browser = None
    try:
        browser = await _launch_browser(pw)
    except Exception:
        await pw.stop()
        raise
    if browser is None:  # pragma: no cover - defensive
        await pw.stop()
        raise RuntimeError("Tarayici baslatilamadi.")
    context = await browser.new_context(viewport={"width": 1400, "height": 900}, locale="en-US")
    page = await context.new_page()
    return pw, browser, context, page


async def _launch_with_state(state: dict):
    from playwright.async_api import async_playwright

    _ensure_browser_path()
    pw = await async_playwright().start()
    browser = None
    try:
        browser = await _launch_browser(pw)
    except Exception:
        await pw.stop()
        raise
    if browser is None:  # pragma: no cover - defensive
        await pw.stop()
        raise RuntimeError("Tarayici baslatilamadi.")
    context = await browser.new_context(
        storage_state=state, viewport={"width": 1400, "height": 1000}, locale="en-US"
    )
    page = await context.new_page()
    return pw, browser, context, page


async def _close(entry: dict):
    for key in ("context", "browser"):
        try:
            obj = entry.get(key)
            if obj:
                await obj.close()
        except Exception:
            pass
    try:
        if entry.get("pw"):
            await entry["pw"].stop()
    except Exception:
        pass


async def cleanup_idle():
    for sid, entry in list(_sessions.items()):
        if (_now() - entry["touched"]).total_seconds() > SESSION_IDLE_LIMIT:
            await _close(entry)
            _sessions.pop(sid, None)


async def _shot(page) -> str:
    data = await page.screenshot(type="jpeg", quality=45, full_page=False)
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()


async def _captcha_b64(page) -> str | None:
    try:
        el = page.locator(CAPTCHA_IMG).first
        await el.wait_for(timeout=8000)
        data = await el.screenshot()
        return "data:image/png;base64," + base64.b64encode(data).decode()
    except Exception as exc:
        logger.warning("captcha capture failed: %s", exc)
        return None


async def start_session(actor: str = "") -> dict:
    """Login sayfasini acar, captcha gorselini dondurur."""
    await cleanup_idle()
    creds = await raw_credentials()
    if not creds["username"] or not creds["password"]:
        return {"ok": False, "error": "Portal kullanıcı adı/şifresi kayıtlı değil. Önce Zami ayarlarını kaydedin."}

    pw, browser, context, page = None, None, None, None
    try:
        pw, browser, context, page = await _launch()
    except Exception as exc:
        logger.error("browser launch failed: %s", exc)
        return {"ok": False, "error": BROWSER_MISSING_MSG}
    try:
        await page.goto(creds["portal_url"].rstrip("/") + LOGIN_PATH, wait_until="domcontentloaded", timeout=45000)
    except Exception as exc:
        await _close({"pw": pw, "browser": browser, "context": context})
        return {"ok": False, "error": f"Portala erişilemedi: {exc}"}

    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "pw": pw,
        "browser": browser,
        "context": context,
        "page": page,
        "touched": _now(),
        "stage": "captcha",
    }
    await log_event(None, None, "rpa_session_start", "RPA oturumu baslatildi", actor=actor)
    return {
        "ok": True,
        "session_id": session_id,
        "stage": "captcha",
        "captcha_image": await _captcha_b64(page),
        "screenshot": await _shot(page),
        "username": creds["username"],
    }


async def refresh_captcha(session_id: str) -> dict:
    entry = _sessions.get(session_id)
    if not entry:
        return {"ok": False, "error": "Oturum bulunamadı, yeniden başlatın."}
    page = entry["page"]
    try:
        await page.click(CAPTCHA_IMG, timeout=5000)
        await asyncio.sleep(1.2)
    except Exception:
        await page.reload(wait_until="domcontentloaded")
    entry["touched"] = _now()
    return {"ok": True, "captcha_image": await _captcha_b64(page)}


async def _find_otp_input(page):
    for sel in OTP_SELECTORS:
        try:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                return loc
        except Exception:
            continue
    return None


async def submit_login(session_id: str, captcha: str, otp: str = "", actor: str = "") -> dict:
    entry = _sessions.get(session_id)
    if not entry:
        return {"ok": False, "error": "Oturum bulunamadı veya zaman aşımına uğradı. Yeniden başlatın."}
    page = entry["page"]
    entry["touched"] = _now()
    creds = await raw_credentials()

    try:
        if entry.get("stage") == "otp":
            otp_input = await _find_otp_input(page)
            if not otp_input:
                return {"ok": False, "error": "OTP alanı bulunamadı.", "screenshot": await _shot(page)}
            await otp_input.fill((otp or "").strip())
            await page.keyboard.press("Enter")
        else:
            await page.fill('input[name="un"]', creds["username"])
            await page.fill('input[name="pw"]', creds["password"])
            if captcha:
                await page.fill('input[name="captcha"]', (captcha or "").strip())
            await page.click('button[type="submit"]')
        await page.wait_for_load_state("domcontentloaded", timeout=45000)
        await asyncio.sleep(1.5)
    except Exception as exc:
        return {"ok": False, "error": f"Giriş denemesi başarısız: {exc}", "screenshot": await _shot(page)}

    # hala login sayfasindaysa: OTP mi, hata mi?
    still_login = await page.locator('input[name="pw"]').count() > 0
    otp_input = await _find_otp_input(page)
    if otp_input is not None and not still_login:
        entry["stage"] = "otp"
        await log_event(None, None, "rpa_otp_required", "Portal OTP istedi", actor=actor)
        return {
            "ok": True,
            "stage": "otp",
            "session_id": session_id,
            "message": "Portal OTP kodu istiyor. E-postanıza/telefonunuza gelen kodu girin.",
            "screenshot": await _shot(page),
        }
    if still_login:
        entry["stage"] = "captcha"
        return {
            "ok": False,
            "stage": "captcha",
            "error": "Giriş yapılamadı (captcha, şifre veya OTP hatası olabilir). Captcha yenilenip tekrar denenebilir.",
            "captcha_image": await _captcha_b64(page),
            "screenshot": await _shot(page),
        }

    state = await entry["context"].storage_state()
    await settings_col.update_one(
        {"key": SESSION_KEY},
        {"$set": {"key": SESSION_KEY, "value": {"storage_state": state, "saved_at": _now().isoformat()}}},
        upsert=True,
    )
    entry["stage"] = "ready"
    await log_event(None, None, "rpa_login_ok", "RPA oturumu acildi ve cerezler saklandi", actor=actor)
    return {
        "ok": True,
        "stage": "ready",
        "session_id": session_id,
        "message": "Giriş başarılı. Oturum kaydedildi; başvuruları aktarabilirsiniz.",
        "current_url": page.url,
        "screenshot": await _shot(page),
    }


async def session_status() -> dict:
    doc = await settings_col.find_one({"key": SESSION_KEY})
    value = (doc or {}).get("value") or {}
    return {
        "has_session": bool(value.get("storage_state")),
        "saved_at": value.get("saved_at"),
        "active_browsers": len(_sessions),
    }


async def clear_session() -> dict:
    await settings_col.delete_one({"key": SESSION_KEY})
    for sid, entry in list(_sessions.items()):
        await _close(entry)
        _sessions.pop(sid, None)
    return {"ok": True}


async def check_status(app_doc: dict) -> dict:
    """Zami portalinda basvurunun guncel durumunu okur.

    Arama icin oncelikle `zami_reference` (portaldaki basvuru no), yoksa
    bizim takip kodumuz ve ilk yolcunun pasaport numarasi denenir.
    """
    mapping = await get_mapping()
    if not mapping.get("status_url"):
        return {"ok": False, "error": "Durum sayfası adresi (status_url) tanımlı değil. Zami ekranından girin."}

    doc = await settings_col.find_one({"key": SESSION_KEY})
    state = ((doc or {}).get("value") or {}).get("storage_state")
    if not state:
        return {"ok": False, "error": "Kayıtlı portal oturumu yok. Önce RPA oturumu açın (captcha + OTP)."}

    travelers = app_doc.get("travelers") or []
    candidates = [
        app_doc.get("zami_reference"),
        app_doc.get("reference_code"),
        (travelers[0].get("passport_no") if travelers else None),
    ]
    candidates = [c for c in candidates if c]
    if not candidates:
        return {"ok": False, "error": "Aranacak bir referans bulunamadı."}

    try:
        pw, browser, context, page = await _launch_with_state(state)
    except Exception as exc:
        logger.error("browser launch failed: %s", exc)
        return {"ok": False, "error": BROWSER_MISSING_MSG}
    try:
        await page.goto(mapping["status_url"], wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(1.0)
        if await page.locator('input[name="pw"]').count() > 0:
            return {"ok": False, "error": "Portal oturumu sona ermiş. Yeni RPA oturumu açın.", "screenshot": await _shot(page)}

        raw_text = ""
        used_ref = ""
        for ref in candidates:
            used_ref = ref
            if mapping.get("status_search_selector"):
                try:
                    box = page.locator(mapping["status_search_selector"]).first
                    await box.fill(str(ref))
                    await page.keyboard.press("Enter")
                    await page.wait_for_load_state("domcontentloaded", timeout=30000)
                    await asyncio.sleep(1.5)
                except Exception:
                    pass

            if mapping.get("status_result_selector"):
                selector = (
                    mapping["status_result_selector"].replace("{ref}", str(ref)).replace("{reference}", str(ref))
                )
                try:
                    loc = page.locator(selector).first
                    if await loc.count() > 0:
                        raw_text = (await loc.inner_text()).strip()
                except Exception:
                    raw_text = ""
            if not raw_text:
                body = await page.inner_text("body")
                for line in body.splitlines():
                    if str(ref).lower() in line.lower():
                        raw_text = line.strip()
                        break
            if raw_text:
                break

        matched = match_status(raw_text, mapping.get("status_keywords") or {})
        return {
            "ok": True,
            "reference_used": used_ref,
            "raw_text": raw_text[:400],
            "matched_status": matched,
            "screenshot": await _shot(page),
        }
    except Exception as exc:
        logger.error("zami status check failed: %s", exc)
        return {"ok": False, "error": f"Durum kontrolü sırasında hata: {exc}"}
    finally:
        await _close({"pw": pw, "browser": browser, "context": context})


async def fill_application(app_doc: dict, payload: dict, dry_run: bool = True, actor: str = "") -> dict:
    """Saklanan oturumla Zami basvuru formunu doldurur (ve dry_run kapaliysa gonderir)."""
    mapping = await get_mapping()
    if not mapping.get("form_url"):
        return {"ok": False, "error": "Zami başvuru formu adresi (form_url) tanımlı değil. Alan eşleme ekranından girin."}
    if not mapping.get("fields") and not mapping.get("traveler_fields"):
        return {"ok": False, "error": "Alan eşlemesi boş. Önce Zami form alanlarını eşleyin."}

    doc = await settings_col.find_one({"key": SESSION_KEY})
    state = ((doc or {}).get("value") or {}).get("storage_state")
    if not state:
        return {"ok": False, "error": "Kayıtlı portal oturumu yok. Önce RPA oturumu açın (captcha + OTP)."}

    try:
        pw, browser, context, page = await _launch_with_state(state)
    except Exception as exc:
        logger.error("browser launch failed: %s", exc)
        return {"ok": False, "error": BROWSER_MISSING_MSG}
    filled, missing = [], []
    try:
        await page.goto(mapping["form_url"], wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(1.0)
        if await page.locator('input[name="pw"]').count() > 0:
            return {
                "ok": False,
                "error": "Portal oturumu sona ermiş (login ekranına yönlendirildi). Yeni RPA oturumu açın.",
                "screenshot": await _shot(page),
            }

        async def set_value(selector: str, value: str):
            if value in (None, ""):
                return False
            loc = page.locator(selector).first
            if await loc.count() == 0:
                missing.append(selector)
                return False
            tag = (await loc.evaluate("el => el.tagName.toLowerCase()")) or ""
            if tag == "select":
                try:
                    await loc.select_option(label=value)
                except Exception:
                    try:
                        await loc.select_option(value=value)
                    except Exception:
                        missing.append(selector)
                        return False
            else:
                await loc.fill(str(value))
            filled.append(selector)
            return True

        for our_key, selector in (mapping.get("fields") or {}).items():
            await set_value(selector, payload["globals"].get(our_key, ""))

        for idx, traveler in enumerate(payload.get("travelers") or []):
            for our_key, selector_tpl in (mapping.get("traveler_fields") or {}).items():
                selector = selector_tpl.replace("{i}", str(idx)).replace("{n}", str(idx + 1))
                await set_value(selector, traveler.get(our_key, ""))

        screenshot = await _shot(page)
        submitted = False
        if not dry_run and mapping.get("submit_selector"):
            try:
                await page.click(mapping["submit_selector"], timeout=15000)
                await page.wait_for_load_state("domcontentloaded", timeout=45000)
                await asyncio.sleep(1.5)
                submitted = True
                screenshot = await _shot(page)
            except Exception as exc:
                return {
                    "ok": False,
                    "error": f"Form dolduruldu ancak gönderilemedi: {exc}",
                    "filled": filled,
                    "missing": missing,
                    "screenshot": screenshot,
                }

        await log_event(
            app_doc.get("id"),
            app_doc.get("reference_code"),
            "rpa_submitted" if submitted else "rpa_filled",
            f"{len(filled)} alan dolduruldu" + (" ve form gönderildi" if submitted else " (dry-run, gönderilmedi)"),
            actor=actor,
            extra={"filled": filled, "missing": missing, "url": page.url},
        )
        return {
            "ok": True,
            "submitted": submitted,
            "dry_run": dry_run,
            "filled_count": len(filled),
            "filled": filled,
            "missing": missing,
            "current_url": page.url,
            "screenshot": screenshot,
        }
    except Exception as exc:
        logger.error("zami rpa fill failed: %s", exc)
        return {"ok": False, "error": f"Aktarım sırasında hata: {exc}"}
    finally:
        await _close({"pw": pw, "browser": browser, "context": context})
