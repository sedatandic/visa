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
import re
import shutil
import tempfile
import uuid
from datetime import datetime, timedelta, timezone

from db import settings_col
from captcha_ai import read_captcha
from zami import (
    MANUAL_FIELDS,
    SESSION_KEY,
    get_mapping,
    log_event,
    match_status,
    raw_credentials,
)

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


_install_tried = False


async def _install_chromium() -> bool:
    """Tarayici indirilmemisse bir kez indirmeyi dener (yeni sunucu/deploy icin)."""
    global _install_tried
    if _install_tried:
        return False
    _install_tried = True
    import asyncio
    import sys

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "playwright", "install", "chromium",
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
        )
        await asyncio.wait_for(proc.wait(), timeout=300)
        return proc.returncode == 0
    except Exception as exc:
        logger.warning("playwright install failed: %s", exc)
        return False


async def _launch_browser(pw):
    """Once paketle gelen tarayiciyi, olmazsa sistem Chromium'unu kullanir."""
    args = ["--no-sandbox", "--disable-dev-shm-usage"]
    try:
        return await pw.chromium.launch(headless=True, args=args)
    except Exception as exc:
        executable = _chrome_executable()
        if not executable:
            if await _install_chromium():
                return await pw.chromium.launch(headless=True, args=args)
            raise
        logger.info("bundled chromium unavailable (%s); using %s", exc, executable)
        return await pw.chromium.launch(headless=True, args=args, executable_path=executable)

_sessions: dict = {}
SESSION_IDLE_LIMIT = 1800  # 30 dk (OTP girisi icin makul sure)
AUTO_RELOGIN_TRIES = 3  # captcha yanlis okunursa tekrar dene
OTP_TRUST_DAYS = 30  # portal trusted-device guveni ~1 ay

# Portal ayni hesap icin es zamanli girisleri tolere etmiyor: ikinci giris
# ilkini dusurup "IP Address changed" hatasi veriyor. Bu yuzden tum giris
# akislari tek kilit uzerinden seri hale getirilir.
_login_lock = asyncio.Lock()


def interactive_login_active() -> bool:
    """Admin panelden baslatilmis ve henuz tamamlanmamis giris var mi?"""
    return any(entry.get("stage") in ("captcha", "otp") for entry in _sessions.values())

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


async def _captcha_bytes(page) -> bytes | None:
    """Captcha gorselinin ham PNG baytlarini dondurur."""
    try:
        el = page.locator(CAPTCHA_IMG).first
        await el.wait_for(timeout=8000)
        return await el.screenshot()
    except Exception as exc:
        logger.warning("captcha capture failed: %s", exc)
        return None


async def _captcha_payload(page) -> tuple[str | None, str]:
    """(data_url, ai_tahmini) dondurur; AI okumasi best-effort'tur."""
    data = await _captcha_bytes(page)
    if not data:
        return None, ""
    data_url = "data:image/png;base64," + base64.b64encode(data).decode()
    guess = await read_captcha(data)
    return data_url, guess


async def _captcha_b64(page) -> str | None:
    data = await _captcha_bytes(page)
    if not data:
        return None
    return "data:image/png;base64," + base64.b64encode(data).decode()


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
    captcha_image, captcha_guess = await _captcha_payload(page)
    return {
        "ok": True,
        "session_id": session_id,
        "stage": "captcha",
        "captcha_image": captcha_image,
        "captcha_guess": captcha_guess,
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
    captcha_image, captcha_guess = await _captcha_payload(page)
    return {"ok": True, "captcha_image": captcha_image, "captcha_guess": captcha_guess}


async def _find_otp_input(page):
    for sel in OTP_SELECTORS:
        try:
            loc = page.locator(sel).first
            if await loc.count() > 0 and await loc.is_visible():
                return loc
        except Exception:
            continue
    return None


OTP_SUBMIT_SELECTORS = [
    'button:has-text("VALIDATE OTP")',
    'button:has-text("Validate OTP")',
    'button:has-text("Validate")',
    'button:has-text("Verify")',
    'button[type="submit"]',
    'input[type="submit"]',
]
TRUSTED_DEVICE_SELECTORS = ['input[name="si"][value="2"]', 'input[name="si"][value="3"]']


async def _try_click_visible(group, count: int) -> bool:
    """Locator grubundaki gorunur ilk ogeye tiklar."""
    for i in range(count):
        item = group.nth(i)
        try:
            if not await item.is_visible():
                continue
            await item.click(timeout=8000)
            return True
        except Exception:
            continue
    return False


async def _click_first(page, selectors: list[str]) -> bool:
    """Verilen seciciler icinden gorunur ilkine tiklar; tiklanirsa True."""
    for sel in selectors:
        try:
            group = page.locator(sel)
            if await _try_click_visible(group, min(await group.count(), 20)):
                return True
        except Exception:
            continue
    return False


SUBMIT_FALLBACK_SELECTORS = (
    'button[type="submit"]',
    'input[type="submit"]',
    'button:has-text("Insert")',
    'button:has-text("Submit")',
    'button:has-text("Save")',
    'button:has-text("Apply")',
    'button:has-text("Send")',
    'button:has-text("Kaydet")',
    'button:has-text("Gönder")',
    'input[value*="insert" i]',
    'input[value*="submit" i]',
    'input[value*="save" i]',
    'input[value*="apply" i]',
    'a:has-text("Insert")',
    'form button:not([type="button"]):not([type="reset"])',
)


async def _mark_trusted_device(page) -> None:
    """Varsa 'Trusted Device' secenegini isaretler; sonraki girislerde OTP azalir.

    Radyo girisi ozel tasarim nedeniyle gizli olabilir; sirayla normal check,
    zorlamali check ve son olarak JS ile isaretleme denenir.
    """
    for sel in TRUSTED_DEVICE_SELECTORS:
        try:
            loc = page.locator(sel).first
            if await loc.count() == 0:
                continue
            if await _check_locator(loc):
                return
            if await _check_via_js(page, sel):
                return
        except Exception:
            continue


async def _check_locator(loc) -> bool:
    """Radyoyu normal, sonra zorlamali sekilde isaretlemeyi dener."""
    for force in (False, True):
        try:
            await loc.check(timeout=4000, force=force)
            if await loc.is_checked():
                return True
        except Exception:
            continue
    return False


async def _check_via_js(page, selector: str) -> bool:
    """Gizli radyoyu DOM uzerinden isaretler ve change olayini tetikler."""
    try:
        return bool(
            await page.eval_on_selector(
                selector,
                "el => { el.checked = true; el.dispatchEvent(new Event('change', {bubbles:true})); return el.checked; }",
            )
        )
    except Exception:
        return False


async def _submit_otp(page, otp: str) -> dict | None:
    """OTP kodunu yazar ve dogrulama butonuna basar. Hata varsa dict dondurur."""
    otp_input = await _find_otp_input(page)
    if not otp_input:
        return {"ok": False, "error": "OTP alanı bulunamadı.", "screenshot": await _shot(page)}
    await otp_input.fill((otp or "").strip())
    await _mark_trusted_device(page)
    if not await _click_first(page, OTP_SUBMIT_SELECTORS):
        await page.keyboard.press("Enter")
    return None


async def _login_credentials_step(page, creds: dict, captcha: str) -> None:
    """Kullanici adi/sifre/captcha alanlarini doldurup formu gonderir.

    Zami login sayfasinda cihaz tipi radyolari (`si`) bulunur ve varsayilan
    "No Change" secenegi cihazi "public/shared" kabul ederek her giriste OTP
    ister. Bu yuzden gonderim oncesi "Trusted Device" isaretlenir; boylece
    portal cihazi hatirlar ve OTP ihtiyaci aylik seviyeye iner.
    """
    await page.fill('input[name="un"]', creds["username"])
    await page.fill('input[name="pw"]', creds["password"])
    if captcha:
        await page.fill('input[name="captcha"]', (captcha or "").strip())
    await _mark_trusted_device(page)
    await page.click('button[type="submit"]')


OTP_COOLDOWN_HINT = "OTP request emailed"


async def _login_error_text(page) -> str:
    """Portalin login sayfasindaki uyariyi Turkce mesaja cevirir."""
    try:
        body = (await page.inner_text("body"))[:4000]
    except Exception:
        body = ""
    if OTP_COOLDOWN_HINT in body:
        minutes = re.search(r"try again after `?(\d+)`? *minutes", body)
        wait = minutes.group(1) if minutes else "15"
        return (
            f"Portal kısa süre önce OTP kodu gönderdi ve yeni kod için {wait} dakika "
            "beklemeyi şart koşuyor. E-postanıza gelen son kodu girin veya süre "
            "dolduktan sonra tekrar deneyin."
        )
    if "Invalid Captcha" in body or "captcha" in body.lower() and "invalid" in body.lower():
        return "Captcha hatalı okundu. Captchayı yenileyip tekrar deneyin."
    return "Giriş yapılamadı (captcha, şifre veya OTP hatası olabilir). Captcha yenilenip tekrar denenebilir."


async def _run_login_attempt(page, entry: dict, creds: dict, captcha: str, otp: str) -> dict | None:
    """Asamaya gore OTP veya kimlik adimini calistirir; hata olursa dict doner."""
    try:
        if entry.get("stage") == "otp":
            failure = await _submit_otp(page, otp)
            if failure:
                return failure
        else:
            await _login_credentials_step(page, creds, captcha)
        await page.wait_for_load_state("domcontentloaded", timeout=45000)
        await asyncio.sleep(2.0)
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Giriş denemesi başarısız: {exc}",
            "screenshot": await _shot(page),
        }
    return None


async def _persist_session(entry: dict, *, via_otp: bool = False) -> None:
    """Basarili girisin cerezlerini (storage_state) DB'ye saklar.

    `via_otp=True` (insan OTP girdi) durumunda ayni cerezler `device_state`
    olarak da saklanir: portal bu cihazi "trusted device" kabul ettigi icin
    sonraki otomatik girisler OTP istemeden yapilabilir. Boylece OTP
    ihtiyaci aylik seviyeye iner.
    """
    state = await entry["context"].storage_state()
    now = _now().isoformat()
    payload = {
        "key": SESSION_KEY,
        "value": {
            "storage_state": state,
            "saved_at": now,
            "expired": False,
            "otp_required": False,
            "last_alive_at": now,
        },
    }
    if via_otp:
        payload["value"]["device_state"] = state
        payload["value"]["last_otp_at"] = now
    else:
        existing = await settings_col.find_one({"key": SESSION_KEY})
        old = (existing or {}).get("value") or {}
        if old.get("device_state"):
            payload["value"]["device_state"] = old["device_state"]
        if old.get("last_otp_at"):
            payload["value"]["last_otp_at"] = old["last_otp_at"]
    await settings_col.update_one({"key": SESSION_KEY}, {"$set": payload}, upsert=True)


async def submit_login(session_id: str, captcha: str, otp: str = "", actor: str = "") -> dict:
    entry = _sessions.get(session_id)
    if not entry:
        return {"ok": False, "error": "Oturum bulunamadı veya zaman aşımına uğradı. Yeniden başlatın."}
    page = entry["page"]
    entry["touched"] = _now()

    used_otp = entry.get("stage") == "otp"
    failure = await _run_login_attempt(page, entry, await raw_credentials(), captcha, otp)
    if failure:
        return failure

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
        captcha_image, captcha_guess = await _captcha_payload(page)
        return {
            "ok": False,
            "stage": "captcha",
            "error": await _login_error_text(page),
            "captcha_image": captcha_image,
            "captcha_guess": captcha_guess,
            "screenshot": await _shot(page),
        }

    await _persist_session(entry, via_otp=used_otp)
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
        "expired": bool(value.get("expired")),
        "last_alive_at": value.get("last_alive_at"),
        "trusted_device": bool(value.get("device_state")),
        "otp_required": bool(value.get("otp_required")),
        "last_otp_at": value.get("last_otp_at"),
        "last_auto_login_at": value.get("last_auto_login_at"),
        "auto_login_count": int(value.get("auto_login_count") or 0),
        "next_otp_due": _next_otp_due(value.get("last_otp_at")),
        "otp_reminder_kind": value.get("otp_reminder_kind"),
        "otp_reminder_sent_at": value.get("otp_reminder_sent_at"),
        "otp_reminder_wa_link": value.get("otp_reminder_wa_link"),
    }


def _next_otp_due(last_otp_at: str | None) -> str | None:
    """Trusted-device guveni ~30 gun surdugu icin bir sonraki OTP tarihi."""
    if not last_otp_at:
        return None
    try:
        base = datetime.fromisoformat(last_otp_at)
    except Exception:
        return None
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    return (base + timedelta(days=OTP_TRUST_DAYS)).isoformat()


async def _mark_otp_required(reason: str) -> None:
    await settings_col.update_one(
        {"key": SESSION_KEY},
        {
            "$set": {
                "value.expired": True,
                "value.otp_required": True,
                "value.otp_required_reason": reason,
                "value.otp_required_at": _now().isoformat(),
            }
        },
    )


async def _auto_login_attempt(page, creds: dict) -> str:
    """Tek bir OTP'siz giris denemesi. Sonuc: ok | otp | retry."""
    await page.goto(
        creds["portal_url"].rstrip("/") + LOGIN_PATH,
        wait_until="domcontentloaded",
        timeout=45000,
    )
    await asyncio.sleep(1.0)
    if await page.locator('input[name="pw"]').count() == 0:
        # login formu yok: zaten oturum acik
        return "ok"

    data = await _captcha_bytes(page)
    guess = await read_captcha(data) if data else ""
    if not guess:
        return "retry"
    await _login_credentials_step(page, creds, guess)
    await page.wait_for_load_state("domcontentloaded", timeout=45000)
    await asyncio.sleep(2.0)

    still_login = await page.locator('input[name="pw"]').count() > 0
    if not still_login and await _find_otp_input(page) is not None:
        return "otp"
    if still_login:
        return "retry"
    return "ok"


def _trust_only_state(device_state: dict) -> dict:
    """Cihaz guveni cerezlerini alir, oturum (session) cerezlerini atar.

    Kaydedilen `device_state` hem kalici "trusted device" cerezini hem de o anki
    oturum cerezini icerir. Bayat oturum cerezi ile giris denemek portalin OTP
    istemesine yol aciyordu; bu yuzden yalnizca son kullanma tarihi olan
    (kalici) cerezlerle temiz bir oturum aciyoruz.
    """
    cookies = [c for c in (device_state.get("cookies") or []) if (c.get("expires") or -1) > 0]
    return {"cookies": cookies, "origins": device_state.get("origins") or []}


async def auto_relogin(actor: str = "auto", force: bool = False) -> dict:
    """Oturum dustugunde OTP olmadan yeniden giris dener.

    Kayitli `device_state` (portalin "trusted device" cerezi) ile acilan
    tarayicida kullanici adi + sifre girilir, captcha AI ile okunur. Portal
    yine de OTP istiyorsa admin bilgilendirilir ve `otp_required` isaretlenir.

    Onemli: `otp_required` isaretliyken veya hic cihaz guveni yokken
    portala tekrar giris denenmez; sifre gonderimi portalin her seferinde
    OTP e-postasi atmasina yol acar. Admin panelden OTP ile giris yapinca
    isaret temizlenir. `force=True` sadece adminin elle tetiklemesi icindir.
    """
    if interactive_login_active():
        # Admin panelden manuel giris suruyor: es zamanli giris onu dusurur.
        return {"ok": False, "reason": "interactive_login_in_progress"}
    if _login_lock.locked():
        return {"ok": False, "reason": "login_in_progress"}

    async with _login_lock:
        return await _auto_relogin_locked(actor, force=force)


async def _auto_relogin_locked(actor: str, force: bool = False) -> dict:
    """auto_relogin'in kilit altinda calisan govdesi."""
    creds = await raw_credentials()
    if not creds.get("username") or not creds.get("password"):
        return {"ok": False, "reason": "no_credentials"}

    doc = await settings_col.find_one({"key": SESSION_KEY})
    value = (doc or {}).get("value") or {}
    device_state = value.get("device_state")

    if not force:
        if not device_state:
            # Cihaz guveni hic kaydedilmemis: her deneme OTP e-postasi tetikler.
            await _mark_otp_required("no_trusted_device")
            return {"ok": False, "reason": "no_trusted_device"}
        if value.get("otp_required"):
            # Admin OTP ile giris yapana kadar portala dokunmuyoruz.
            return {"ok": False, "reason": "otp_required_pending"}

    try:
        if device_state:
            pw, browser, context, page = await _launch_with_state(_trust_only_state(device_state))
        else:
            pw, browser, context, page = await _launch()
    except Exception as exc:
        logger.warning("auto relogin launch failed: %s", exc)
        return {"ok": False, "reason": "browser", "error": str(exc)}

    entry = {"pw": pw, "browser": browser, "context": context}
    try:
        for attempt in range(AUTO_RELOGIN_TRIES):
            try:
                outcome = await _auto_login_attempt(page, creds)
            except Exception as exc:
                logger.warning("auto relogin attempt %s failed: %s", attempt + 1, exc)
                outcome = "retry"
            if outcome == "ok":
                await _persist_session({"context": context}, via_otp=False)
                await settings_col.update_one(
                    {"key": SESSION_KEY},
                    {
                        "$set": {"value.last_auto_login_at": _now().isoformat()},
                        "$inc": {"value.auto_login_count": 1},
                    },
                )
                await log_event(
                    None, None, "rpa_auto_login",
                    "Oturum otomatik yenilendi (OTP gerekmedi)", actor=actor,
                )
                return {"ok": True, "attempts": attempt + 1}
            if outcome == "otp":
                await _mark_otp_required("portal_otp")
                await log_event(
                    None, None, "rpa_otp_required",
                    "Otomatik giriste portal OTP istedi - manuel giris gerekiyor", actor=actor,
                )
                return {"ok": False, "reason": "otp_required"}
            await asyncio.sleep(2.0)
        return {"ok": False, "reason": "captcha_failed"}
    finally:
        await _close(entry)


async def start_session_to_otp(actor: str = "") -> dict:
    """Girisi OTP ekranina kadar otomatik ilerletir.

    Portalin OTP kodu yalnizca birkac dakika gecerli oldugu icin adminin
    captcha adimiyla ugrasmasi zaman kaybi yaratiyor. Bu fonksiyon oturumu
    baslatir, captcha'yi AI ile okuyup sifreyi gonderir ve dogrudan OTP
    asamasini dondurur; admin yalnizca kodu girer.
    """
    async with _login_lock:
        started = await start_session(actor=actor)
        if not started.get("ok"):
            return started
        session_id = started["session_id"]
        last = started
        for _ in range(AUTO_RELOGIN_TRIES):
            entry = _sessions.get(session_id)
            if not entry:
                return {"ok": False, "error": "Oturum düştü, tekrar deneyin."}
            guess = (last.get("captcha_guess") or "").strip()
            if not guess:
                last = await refresh_captcha(session_id)
                continue
            out = await submit_login(session_id, guess, "", actor=actor)
            if out.get("stage") in ("otp", "ready") or out.get("ok"):
                out["session_id"] = session_id
                return out
            last = out
        return {
            "ok": False,
            "session_id": session_id,
            "stage": "captcha",
            "error": "Captcha otomatik okunamadı. Aşağıdaki görselden kodu elle girin.",
            "captcha_image": last.get("captcha_image"),
            "captcha_guess": last.get("captcha_guess"),
        }


async def keepalive_session() -> dict:
    """Portal oturumunu canli tutar.

    Zami oturumu ~15-20 dk hareketsizlikte dusuyor. Bu fonksiyon kayitli
    oturumla portal ana sayfasini acar; oturum ayaktaysa cerezleri tazeleyip
    yeniden kaydeder, dusmusse `expired` isaretler (admin uyarilir).
    """
    if interactive_login_active():
        return {"ok": True, "reason": "interactive_login_in_progress"}

    doc = await settings_col.find_one({"key": SESSION_KEY})
    value = (doc or {}).get("value") or {}
    state = value.get("storage_state")
    if not state:
        return {"ok": False, "reason": "no_session"}

    creds = await raw_credentials()
    try:
        pw, browser, context, page = await _launch_with_state(state)
    except Exception as exc:
        logger.warning("zami keepalive launch failed: %s", exc)
        return {"ok": False, "reason": "browser", "error": str(exc)}

    try:
        await page.goto(creds["portal_url"], wait_until="domcontentloaded", timeout=45000)
        await asyncio.sleep(1.5)
        logged_out = await page.locator('input[name="pw"]').count() > 0
        if logged_out:
            await settings_col.update_one(
                {"key": SESSION_KEY},
                {"$set": {"value.expired": True, "value.expired_at": _now().isoformat()}},
            )
            return {"ok": False, "reason": "expired"}
        fresh_state = await context.storage_state()
        await settings_col.update_one(
            {"key": SESSION_KEY},
            {
                "$set": {
                    "value.storage_state": fresh_state,
                    "value.last_alive_at": _now().isoformat(),
                    "value.expired": False,
                }
            },
        )
        return {"ok": True, "url": page.url}
    except Exception as exc:
        logger.warning("zami keepalive failed: %s", exc)
        return {"ok": False, "reason": "error", "error": str(exc)}
    finally:
        await _close({"pw": pw, "browser": browser, "context": context})


async def _active_state() -> dict | None:
    """Kayitli oturum cerezlerini dondurur.

    Oturum `expired` isaretliyse once OTP'siz otomatik giris denenir; boylece
    aktarim/durum sorgusu admin mudahalesi olmadan devam eder.
    """
    doc = await settings_col.find_one({"key": SESSION_KEY})
    value = (doc or {}).get("value") or {}
    if value.get("storage_state") and not value.get("expired"):
        return value["storage_state"]
    if value.get("storage_state") or value.get("device_state"):
        out = await auto_relogin()
        if out.get("ok"):
            doc = await settings_col.find_one({"key": SESSION_KEY})
            return ((doc or {}).get("value") or {}).get("storage_state")
    return value.get("storage_state")


async def clear_session() -> dict:
    await settings_col.delete_one({"key": SESSION_KEY})
    for sid, entry in list(_sessions.items()):
        await _close(entry)
        _sessions.pop(sid, None)
    return {"ok": True}


ROW_TEXT_JS = """(ref) => {
    const needle = String(ref).toLowerCase();
    const rows = Array.from(document.querySelectorAll('tr,li,div'));
    const hit = rows.find(el => el.offsetParent
        && (el.innerText || '').toLowerCase().includes(needle)
        && (el.innerText || '').length < 400
        && !el.querySelector('table'));
    return hit ? (hit.innerText || '').replace(/\\s+/g, ' ').trim() : '';
}"""


async def _status_search(page, mapping: dict, ref) -> None:
    """Durum sayfasindaki arama alanina referansi yazip sorgular."""
    if not mapping.get("status_search_selector"):
        return
    try:
        await page.locator(mapping["status_search_selector"]).first.fill(str(ref))
        submit = mapping.get("status_submit_selector")
        if not (submit and await _click_first(page, [submit])):
            await page.keyboard.press("Enter")
        await page.wait_for_load_state("domcontentloaded", timeout=30000)
        await asyncio.sleep(2.0)
    except Exception:
        pass


async def _read_status_text(page, mapping: dict, ref) -> str:
    """Durum metnini sirasiyla eslenen secici, tablo satiri ve sayfa govdesinden okur."""
    if mapping.get("status_result_selector"):
        selector = (
            mapping["status_result_selector"].replace("{ref}", str(ref)).replace("{reference}", str(ref))
        )
        try:
            loc = page.locator(selector).first
            if await loc.count() > 0:
                text = (await loc.inner_text()).strip()
                if text:
                    return text
        except Exception:
            pass
    try:
        text = await page.evaluate(ROW_TEXT_JS, str(ref))
        if text:
            return text
    except Exception:
        pass
    body = await page.inner_text("body")
    for line in body.splitlines():
        if str(ref).lower() in line.lower():
            return line.strip()
    return ""


async def check_status(app_doc: dict) -> dict:
    """Zami portalinda basvurunun guncel durumunu okur.

    Arama icin oncelikle `zami_reference` (portaldaki basvuru no), yoksa
    bizim takip kodumuz ve ilk yolcunun pasaport numarasi denenir.
    """
    mapping = await get_mapping()
    if not mapping.get("status_url"):
        return {"ok": False, "error": "Durum sayfası adresi (status_url) tanımlı değil. Zami ekranından girin."}

    state = await _active_state()
    if not state:
        return {"ok": False, "error": "Kayıtlı portal oturumu yok. Önce RPA oturumu açın (captcha + OTP)."}

    travelers = app_doc.get("travelers") or []
    passport_no = travelers[0].get("passport_no") if travelers else None
    if (mapping.get("status_search_field") or "passport") == "passport":
        # Zami arama sayfasinda en guvenilir anahtar pasaport numarasi
        candidates = [passport_no, app_doc.get("zami_reference"), app_doc.get("reference_code")]
    else:
        candidates = [app_doc.get("zami_reference"), app_doc.get("reference_code"), passport_no]
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
            await _status_search(page, mapping, ref)
            raw_text = await _read_status_text(page, mapping, ref)
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


AUTOCOMPLETE_JS = """
async ({selector, wanted}) => {
    const $ = window.jQuery || window.$;
    const el = document.querySelector(selector);
    if (!el) return {ok: false, reason: 'element yok'};
    el.focus();
    el.value = wanted;
    if ($) {
        try { $(el).autocomplete('search', wanted); } catch (e) { /* widget degil */ }
    }
    el.dispatchEvent(new Event('input', {bubbles: true}));
    await new Promise(r => setTimeout(r, 1600));
    const menus = Array.from(document.querySelectorAll('.ui-autocomplete')).filter(m => !!m.offsetParent);
    const items = menus.flatMap(m => Array.from(m.querySelectorAll('li'))).filter(li => (li.innerText || '').trim());
    const norm = s => (s || '').trim().toLowerCase();
    const target = items.find(li => norm(li.innerText) === norm(wanted))
                || items.find(li => norm(li.innerText).startsWith(norm(wanted)))
                || items[0];
    if (target) {
        (target.querySelector('a') || target).click();
        await new Promise(r => setTimeout(r, 600));
    }
    return {ok: !!(el.value || '').trim(), value: (el.value || '').trim(), picked: target ? (target.innerText || '').trim() : null};
}
"""


async def _upload_documents(page, app_doc: dict, mapping: dict) -> dict:
    """Yolcunun pasaport/vesikalik belgelerini portaldaki gorsel alanlarina yukler."""
    from db import uploads_col
    from storage import get_object

    result = {"uploaded": [], "failed": []}
    targets = mapping.get("upload_targets") or []
    if not targets:
        return result
    traveler = (app_doc.get("travelers") or [{}])[0] or {}
    docs = traveler.get("documents") or {}
    temp_dir = tempfile.mkdtemp(prefix="zami-docs-")
    try:
        for target in targets:
            file_id = docs.get(f"{target['doc']}_file_id") or traveler.get(f"{target['doc']}_file_id")
            if not file_id:
                continue
            record = await uploads_col.find_one({"id": file_id, "is_deleted": False})
            if not record:
                result["failed"].append(target["doc"])
                continue
            try:
                data, content_type = get_object(record["storage_path"])
                ext = ".pdf" if "pdf" in (content_type or "") else ".jpg"
                local_path = os.path.join(temp_dir, f"{target['doc']}{ext}")
                with open(local_path, "wb") as fh:
                    fh.write(data)
                async with page.expect_file_chooser(timeout=15000) as fc_info:
                    await page.locator(target["selector"]).first.click(timeout=10000)
                chooser = await fc_info.value
                await chooser.set_files(local_path)
                await asyncio.sleep(3.0)
                result["uploaded"].append(target["doc"])
            except Exception as exc:
                logger.warning("zami upload failed (%s): %s", target["doc"], exc)
                result["failed"].append(target["doc"])
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
    return result


VALIDATION_TEXT_JS = """() => Array.from(document.querySelectorAll('div,span,p,li'))
    .filter(el => el.offsetParent && /msg|error|alert|warn|invalid|required/i.test((el.className || '') + ' ' + (el.id || '')))
    .map(el => (el.innerText || '').trim())
    .filter(t => t && t.length < 240)
    .slice(0, 8).join(' | ')"""


async def _collect_manual_pending(page) -> list:
    """Portalda zorunlu olup bizim doldurmadigimiz alanlari raporlar."""
    pending = []
    for item in MANUAL_FIELDS:
        try:
            loc = page.locator(item["selector"]).first
            if await loc.count() == 0:
                continue
            if not ((await loc.input_value()) or "").strip():
                pending.append(item["label"])
        except Exception:
            continue
    return pending


async def _run_portal_validation(page, mapping: dict, set_value, skipped: list, values: dict) -> tuple:
    """Portal dogrulamasini tetikler, kilidi acilan alanlari tekrar dener; (mesaj, ekran) doner."""
    if not mapping.get("validate_selector"):
        return "", ""
    try:
        if not await _click_first(page, [mapping["validate_selector"]]):
            return "", ""
        await asyncio.sleep(2.5)
        retry = [s for s in skipped if s in values]
        if retry:
            skipped.clear()
            for selector in retry:
                await set_value(selector, values[selector])
            await _click_first(page, [mapping["validate_selector"]])
            await asyncio.sleep(2.0)
        return await page.evaluate(VALIDATION_TEXT_JS), await _shot(page)
    except Exception as exc:
        logger.warning("zami validate click failed: %s", exc)
        return "", ""


async def _submit_form(page, mapping: dict) -> dict:
    """Gonder butonuna basar ve portalin verdigi basvuru numarasini yakalar."""
    candidates = [s for s in [mapping.get("submit_selector") or "", *SUBMIT_FALLBACK_SELECTORS] if s]
    if not await _click_first(page, candidates):
        raise RuntimeError("Gönder/Kaydet butonu görünür durumda bulunamadı.")
    await page.wait_for_load_state("domcontentloaded", timeout=45000)
    await asyncio.sleep(2.5)
    reference = ""
    try:
        # Portalin verdigi basvuru numarasi ("Visa Application VS-66059 inserted.")
        match = re.search(r"\b(VS-?\d{3,})", await page.inner_text("body"))
        if match:
            reference = match.group(1).replace("VS", "VS-").replace("--", "-")
    except Exception:
        pass
    return {"reference": reference, "screenshot": await _shot(page)}


async def _is_editable(loc) -> bool:
    """Alan portal tarafindan kilitli/gizli degil mi? (kontrol hata verirse doldurmayi dener)"""
    try:
        return not await loc.is_disabled() and await loc.is_visible()
    except Exception:
        return True


async def _select_option(loc, value: str) -> bool:
    """Select alaninda once etiketi, olmazsa degeri secer."""
    try:
        await loc.select_option(label=value)
        return True
    except Exception:
        try:
            await loc.select_option(value=value)
            return True
        except Exception:
            return False


async def _check_radio_group(page, selector: str, value: str) -> bool:
    """Ayni isimli radiolar icinde degeri/etiketi eslesen secenegi isaretler."""
    target = str(value).strip().lower()
    try:
        group = page.locator(selector)
        for index in range(await group.count()):
            item = group.nth(index)
            raw_val = ((await item.evaluate("el => el.value || ''")) or "").strip()
            label_txt = (
                await item.evaluate(
                    "el => (el.closest('label')?.innerText || el.parentElement?.innerText || '')"
                )
            ) or ""
            if target in (raw_val.lower(), label_txt.strip().lower()) or (
                target and target in label_txt.lower()
            ):
                await item.check(timeout=8000)
                return True
        return False
    except Exception:
        return False


async def _check_box(loc, value: str) -> bool:
    if str(value).strip().lower() not in {"1", "true", "yes", "evet", "on"}:
        return False
    await loc.check(timeout=8000)
    return True


async def _fill_text(page, loc, selector: str, value: str) -> bool:
    """Metin alanini doldurur; jQuery UI autocomplete alanlarinda oneriden secer."""
    class_name = ((await loc.evaluate("el => el.className || ''")) or "").lower()
    if "ui-autocomplete-input" in class_name:
        result = await page.evaluate(AUTOCOMPLETE_JS, {"selector": selector, "wanted": str(value)})
        return bool((result or {}).get("ok"))
    try:
        await loc.fill(str(value), timeout=8000)
    except Exception:
        return False
    try:
        await loc.dispatch_event("input")
    except Exception:
        pass
    return True


async def fill_application(app_doc: dict, payload: dict, dry_run: bool = True, actor: str = "") -> dict:
    """Saklanan oturumla Zami basvuru formunu doldurur (ve dry_run kapaliysa gonderir)."""
    mapping = await get_mapping()
    if not mapping.get("form_url"):
        return {"ok": False, "error": "Zami başvuru formu adresi (form_url) tanımlı değil. Alan eşleme ekranından girin."}
    if not mapping.get("fields") and not mapping.get("traveler_fields"):
        return {"ok": False, "error": "Alan eşlemesi boş. Önce Zami form alanlarını eşleyin."}

    state = await _active_state()
    if not state:
        return {"ok": False, "error": "Kayıtlı portal oturumu yok. Önce RPA oturumu açın (captcha + OTP)."}

    try:
        pw, browser, context, page = await _launch_with_state(state)
    except Exception as exc:
        logger.error("browser launch failed: %s", exc)
        return {"ok": False, "error": BROWSER_MISSING_MSG}
    filled, missing = [], []
    skipped_disabled: list[str] = []
    values_by_selector: dict[str, str] = {}
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
            """Eslenen alani tipine gore doldurur; sonucu filled/missing listelerine yazar."""
            if value in (None, ""):
                return False
            values_by_selector[selector] = str(value)
            loc = page.locator(selector).first
            if await loc.count() == 0:
                missing.append(selector)
                return False
            if not await _is_editable(loc):
                # Portal bu alani kendisi yonetiyor ya da alan o an gizli - beklemeden atla
                skipped_disabled.append(selector)
                return False

            tag = (await loc.evaluate("el => el.tagName.toLowerCase()")) or ""
            input_type = ((await loc.evaluate("el => el.type || ''")) or "").lower()
            if tag == "select":
                ok = await _select_option(loc, value)
            elif input_type == "radio":
                ok = await _check_radio_group(page, selector, value)
            elif input_type == "checkbox":
                ok = await _check_box(loc, value)
            else:
                ok = await _fill_text(page, loc, selector, value)

            if not ok:
                if input_type != "checkbox":  # kapatilmis checkbox eksik alan sayilmaz
                    missing.append(selector)
                return False
            filled.append(selector)
            return True

        # Sabit degerler (mapping.constants): portalda her basvuruda ayni girilen alanlar
        for selector, const_value in (mapping.get("constants") or {}).items():
            await set_value(selector, const_value)

        for our_key, selector in (mapping.get("fields") or {}).items():
            await set_value(selector, payload["globals"].get(our_key, ""))

        for idx, traveler in enumerate(payload.get("travelers") or []):
            for our_key, selector_tpl in (mapping.get("traveler_fields") or {}).items():
                selector = selector_tpl.replace("{i}", str(idx)).replace("{n}", str(idx + 1))
                await set_value(selector, traveler.get(our_key, ""))

        screenshot = await _shot(page)
        manual_pending = await _collect_manual_pending(page)

        # Belgeleri portaldaki gorsel alanlarina yukle (pasaport + vesikalik)
        upload_result = await _upload_documents(page, app_doc, mapping)
        if upload_result["uploaded"]:
            await asyncio.sleep(2.0)

        # Portal yardimci butonlari (Arapca cevirisi vb.)
        for helper in mapping.get("helper_selectors") or []:
            try:
                if await _click_first(page, [helper]):
                    await asyncio.sleep(2.0)
            except Exception as exc:
                logger.warning("zami helper click failed (%s): %s", helper, exc)

        # Portalin kendi dogrulamasini calistir: eksik zorunlu alanlari acar.
        # Ardindan ilk gecişte kilitli olan alanlar tekrar denenir.
        validation_text, validation_shot = await _run_portal_validation(
            page, mapping, set_value, skipped_disabled, values_by_selector
        )
        if validation_shot:
            screenshot = validation_shot

        submitted = False
        zami_reference = ""
        if not dry_run:
            try:
                result = await _submit_form(page, mapping)
                submitted = True
                zami_reference = result["reference"]
                screenshot = result["screenshot"]
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
            "skipped_disabled": skipped_disabled,
            "manual_pending": manual_pending,
            "uploads": upload_result,
            "zami_reference": zami_reference,
            "validation_text": (validation_text or "")[:600],
            "current_url": page.url,
            "screenshot": screenshot,
        }
    except Exception as exc:
        logger.error("zami rpa fill failed: %s", exc)
        return {"ok": False, "error": f"Aktarım sırasında hata: {exc}"}
    finally:
        await _close({"pw": pw, "browser": browser, "context": context})
