"""Zami Tours aktarim API'leri (admin + bookmarklet)."""

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

import zami
import zami_rpa
from db import applications_col, serialize_doc, zami_logs_col
from routes_admin import require_admin

logger = logging.getLogger(__name__)
router = APIRouter()


def _base_url(request: Request) -> str:
    """Public taban URL. Ingress arkasinda http/internal host gelebilecegi icin
    once PUBLIC_BASE_URL, sonra Origin, sonra x-forwarded basliklari kullanilir."""
    configured = os.environ.get("PUBLIC_BASE_URL")
    if configured:
        return configured.rstrip("/")
    origin = request.headers.get("origin") or ""
    if origin.startswith("http") and "zamitours" not in origin:
        return origin.rstrip("/")
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or ""
    if host:
        proto = (request.headers.get("x-forwarded-proto") or "").split(",")[0].strip()
        if not proto:
            proto = "http" if host.startswith("localhost") or host.startswith("127.") else "https"
        return f"{proto}://{host}"
    return str(request.base_url).rstrip("/")


class MappingIn(BaseModel):
    form_url: Optional[str] = ""
    submit_selector: Optional[str] = ""
    dry_run: bool = True
    fields: dict = Field(default_factory=dict)
    traveler_fields: dict = Field(default_factory=dict)
    status_url: Optional[str] = ""
    status_search_selector: Optional[str] = ""
    status_result_selector: Optional[str] = ""
    status_keywords: dict = Field(default_factory=dict)
    auto_check_enabled: bool = False
    auto_check_hours: int = 6
    auto_notify: bool = True


class ParseHtmlIn(BaseModel):
    html: str = Field(..., min_length=10, max_length=800000)


class SettingsIn(BaseModel):
    portal_url: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class LoginIn(BaseModel):
    session_id: str
    captcha: Optional[str] = ""
    otp: Optional[str] = ""


class TransferIn(BaseModel):
    dry_run: bool = True


class BulkTransferIn(BaseModel):
    application_ids: list[str] = Field(..., min_length=1, max_length=20)
    dry_run: bool = True


class ZamiReferenceIn(BaseModel):
    zami_reference: str = Field("", max_length=80)


class StatusCheckIn(BaseModel):
    notify: bool = True


# ------------------------------------------------------------ admin: ayarlar
@router.get("/admin/zami/config")
async def zami_config(admin: dict = Depends(require_admin)) -> dict:
    captured = await zami.get_capture()
    return {
        "settings": await zami.get_settings(),
        "mapping": await zami.get_mapping(),
        "session": await zami_rpa.session_status(),
        "global_fields": [{"key": k, "label": v} for k, v in zami.GLOBAL_FIELDS],
        "traveler_fields": [{"key": k, "label": v} for k, v in zami.TRAVELER_FIELDS],
        "captured": {
            "form": {
                "url": ((captured.get("form") or {}).get("url") or ""),
                "fields": ((captured.get("form") or {}).get("fields") or []),
                "captured_at": captured.get("form_captured_at"),
            },
            "status": {
                "url": ((captured.get("status") or {}).get("url") or ""),
                "fields": ((captured.get("status") or {}).get("fields") or []),
                "sample_text": ((captured.get("status") or {}).get("sample_text") or "")[:400],
                "captured_at": captured.get("status_captured_at"),
            },
        },
        "suggestions": zami.suggest_mapping(captured),
    }


@router.put("/admin/zami/settings")
async def zami_save_settings(payload: SettingsIn, admin: dict = Depends(require_admin)) -> dict:
    return {"settings": await zami.save_settings(payload.model_dump(exclude_none=True))}


@router.put("/admin/zami/mapping")
async def zami_save_mapping(payload: MappingIn, admin: dict = Depends(require_admin)) -> dict:
    mapping = await zami.save_mapping(payload.model_dump())
    await zami.log_event(None, None, "mapping_saved", "Alan eslemesi guncellendi", actor=admin.get("sub", ""))
    return {"mapping": mapping}


@router.post("/admin/zami/parse-form")
async def zami_parse_form(payload: ParseHtmlIn, admin: dict = Depends(require_admin)) -> dict:
    fields = zami.parse_form_fields(payload.html)
    if not fields:
        raise HTTPException(400, "HTML icinde doldurulabilir form alani bulunamadi.")
    return {"fields": fields, "count": len(fields)}


# ------------------------------------------------- admin: bookmarklet handoff
@router.post("/admin/zami/handoff/{application_id}")
async def zami_handoff(application_id: str, request: Request, admin: dict = Depends(require_admin)):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    base = _base_url(request)
    data = await zami.create_handoff(app_doc, admin.get("sub", ""), base)
    data["bookmarklet_url"] = f"{base}/api/zami/bookmarklet.js"
    return data


@router.get("/admin/zami/payload/{application_id}")
async def zami_payload(application_id: str, request: Request, admin: dict = Depends(require_admin)):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    return zami.build_payload(app_doc, _base_url(request))


@router.get("/admin/zami/logs")
async def zami_log_list(application_id: Optional[str] = None, admin: dict = Depends(require_admin)) -> dict:
    query = {"application_id": application_id} if application_id else {}
    docs = await zami_logs_col.find(query).sort("created_at", -1).limit(100).to_list(100)
    return {"items": serialize_doc(docs)}


class CaptureIn(BaseModel):
    page_type: str = Field("form", max_length=20)
    url: Optional[str] = ""
    fields: list = Field(default_factory=list)
    submit_selector: Optional[str] = ""
    search_selector: Optional[str] = ""
    row_selector: Optional[str] = ""
    sample_text: Optional[str] = ""


@router.post("/admin/zami/capture-token")
async def zami_capture_token(request: Request, admin: dict = Depends(require_admin)):
    return await zami.create_capture_token(admin.get("sub", ""), _base_url(request))


@router.post("/admin/zami/apply-suggestions")
async def zami_apply_suggestions(admin: dict = Depends(require_admin)) -> dict:
    """Yakalanan alanlardan uretilen onerileri mevcut eslemeye uygular."""
    captured = await zami.get_capture()
    suggestions = zami.suggest_mapping(captured)
    mapping = await zami.get_mapping()
    merged = dict(mapping)
    merged["fields"] = {**(mapping.get("fields") or {}), **suggestions["fields"]}
    merged["traveler_fields"] = {**(mapping.get("traveler_fields") or {}), **suggestions["traveler_fields"]}
    for key in ("form_url", "submit_selector", "status_url", "status_search_selector", "status_result_selector"):
        if suggestions.get(key) and not mapping.get(key):
            merged[key] = suggestions[key]
    saved = await zami.save_mapping(merged)
    await zami.log_event(
        None,
        None,
        "suggestions_applied",
        f"{len(suggestions['fields'])} genel + {len(suggestions['traveler_fields'])} yolcu alanı otomatik eşlendi",
        actor=admin.get("sub", ""),
    )
    return {"mapping": saved, "suggestions": suggestions}


@router.post("/zami/capture/{token}")
async def zami_capture(token: str, payload: CaptureIn) -> dict:
    """Zami sayfasindan gonderilen alan bilgilerini kaydeder (token korumali)."""
    doc = await zami.consume_handoff(token)
    if not doc or doc.get("kind") != "capture":
        raise HTTPException(404, "Yakalama kodu gecersiz veya suresi dolmus.")
    data = {
        "url": (payload.url or "")[:400],
        "fields": (payload.fields or [])[:200],
        "submit_selector": (payload.submit_selector or "")[:200],
        "search_selector": (payload.search_selector or "")[:200],
        "row_selector": (payload.row_selector or "")[:200],
        "sample_text": (payload.sample_text or "")[:1000],
    }
    captured = await zami.save_capture(payload.page_type, data)
    suggestions = zami.suggest_mapping(captured)
    await zami.log_event(
        None,
        None,
        "form_captured",
        f"{payload.page_type} sayfasından {len(data['fields'])} alan yakalandı",
        actor=doc.get("created_by", ""),
    )
    return {
        "ok": True,
        "captured_fields": len(data["fields"]),
        "suggested_global": len(suggestions["fields"]),
        "suggested_traveler": len(suggestions["traveler_fields"]),
    }


@router.get("/zami/capture.js")
async def zami_capture_script(request: Request):
    from fastapi.responses import Response

    script = CAPTURE_JS.replace("__BASE__", _base_url(request))
    return Response(content=script, media_type="application/javascript; charset=utf-8")


CAPTURE_JS = r"""
(function () {
  var BASE = (function () {
    try {
      var src = document.currentScript && document.currentScript.src;
      if (src) return new URL(src).origin;
    } catch (e) {}
    return "__BASE__";
  })();
  var token = window.__VIZEATLAS_CAPTURE_TOKEN__ || window.prompt("VizeAtlas yakalama kodunu yapıştırın:");
  if (!token) return;
  var pageType =
    window.__VIZEATLAS_PAGE_TYPE__ ||
    (window.confirm("Bu sayfa YENİ BAŞVURU FORMU mu?\n\nTamam = Başvuru formu\nİptal = Başvuru listesi / durum sayfası")
      ? "form"
      : "status");

  function label(el) {
    var txt = "";
    if (el.id) {
      var lab = document.querySelector('label[for="' + el.id + '"]');
      if (lab) txt = lab.innerText;
    }
    if (!txt) {
      var p = el.closest("label");
      if (p) txt = p.innerText;
    }
    if (!txt) {
      var cell = el.closest("td");
      if (cell && cell.previousElementSibling) txt = cell.previousElementSibling.innerText;
    }
    if (!txt) txt = el.placeholder || el.getAttribute("aria-label") || el.name || el.id || "";
    return String(txt).replace(/\s+/g, " ").trim().slice(0, 120);
  }

  var skip = { hidden: 1, submit: 1, button: 1, reset: 1, image: 1 };
  var fields = [];
  document.querySelectorAll("input,select,textarea").forEach(function (el) {
    var type = (el.type || (el.tagName.toLowerCase() === "select" ? "select" : "text")).toLowerCase();
    if (skip[type]) return;
    if (!el.name && !el.id) return;
    fields.push({
      tag: el.tagName.toLowerCase(),
      type: type,
      name: el.name || "",
      id: el.id || "",
      selector: el.name ? '[name="' + el.name + '"]' : "#" + el.id,
      label: label(el),
      placeholder: el.placeholder || "",
    });
  });

  var submitEl = document.querySelector('button[type="submit"],input[type="submit"]');
  var body = {
    page_type: pageType,
    url: location.href,
    fields: fields,
    submit_selector: submitEl
      ? submitEl.id
        ? "#" + submitEl.id
        : submitEl.name
          ? '[name="' + submitEl.name + '"]'
          : 'button[type="submit"]'
      : "",
    search_selector: (function () {
      var el = document.querySelector(
        'input[type="search"],input[name*="search" i],input[placeholder*="search" i],input[name*="ref" i]'
      );
      return el ? (el.name ? '[name="' + el.name + '"]' : "#" + el.id) : "";
    })(),
    row_selector: document.querySelector("table tbody tr") ? 'tr:has-text("{ref}")' : "",
    sample_text: (document.body.innerText || "").slice(0, 900),
  };

  var box = document.createElement("div");
  box.style.cssText =
    "position:fixed;z-index:2147483647;right:16px;bottom:16px;max-width:340px;font:13px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;" +
    "background:#0B1F33;color:#fff;padding:14px 16px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.35)";
  box.innerHTML = "<b>VizeAtlas</b><br>" + fields.length + " alan bulundu, gönderiliyor…";
  document.body.appendChild(box);

  fetch(BASE + "/api/zami/capture/" + encodeURIComponent(token), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
    .then(function (r) {
      if (!r.ok) throw new Error("Kod geçersiz veya süresi dolmuş");
      return r.json();
    })
    .then(function (res) {
      box.innerHTML =
        "<b>VizeAtlas</b><br>" +
        res.captured_fields +
        " alan kaydedildi.<br>Otomatik eşleşme: " +
        res.suggested_global +
        " genel, " +
        res.suggested_traveler +
        " yolcu alanı.<br><span style='opacity:.8;font-size:12px'>Admin panelindeki Alan Eşleme ekranını yenileyin.</span>";
      setTimeout(function () {
        box.remove();
      }, 12000);
    })
    .catch(function (err) {
      box.innerHTML = "<b>VizeAtlas</b><br>Hata: " + err.message;
    });
})();
"""


CRITICAL_TRAVELER_FIELDS = ("first_name", "last_name", "passport_no", "birth_date")
BIRTH_DATE_KEYS = {"birth_date", "birth_date_dmy", "birth_date_mdy", "birth_date_dmy_dash"}
NAME_KEYS = {"first_name", "last_name", "full_name"}


def _capture_check(captured: dict) -> dict:
    fields = (captured.get("form") or {}).get("fields") or []
    return {
        "key": "captured",
        "label": "Zami form alanları yakalandı",
        "ok": bool(fields),
        "detail": f"{len(fields)} alan" if fields else "Yakalama yardımcısını Zami formunda çalıştırın",
    }


def _mapping_checks(mapping: dict) -> list[dict]:
    """Alan eşlemesi ile ilgili kontroller (form adresi, genel alanlar, gönder butonu)."""
    fields = mapping.get("fields") or {}
    return [
        {
            "key": "form_url",
            "label": "Başvuru formu adresi tanımlı",
            "ok": bool(mapping.get("form_url")),
            "detail": mapping.get("form_url") or "Alan Eşleme ekranından girin",
        },
        {
            "key": "fields",
            "label": "Genel alan eşlemesi",
            "ok": len(fields) >= 3,
            "detail": f"{len(fields)} alan eşlendi",
        },
        {
            "key": "submit",
            "label": "Gönder butonu seçicisi (otomatik gönderim için)",
            "ok": bool(mapping.get("submit_selector")),
            "detail": mapping.get("submit_selector") or "Boşsa robot formu doldurur ama göndermez",
        },
        {
            "key": "status_url",
            "label": "Durum takibi sayfası (opsiyonel)",
            "ok": bool(mapping.get("status_url")),
            "detail": mapping.get("status_url") or "Otomatik durum takibi için gerekli",
        },
    ]


def _traveler_check(mapping: dict) -> dict:
    """Yolcu alanlarinin (ad, pasaport, dogum tarihi) eşlenip eşlenmediğini kontrol eder."""
    traveler_keys = set((mapping.get("traveler_fields") or {}).keys())
    has_name = bool(traveler_keys & NAME_KEYS)
    has_passport = "passport_no" in traveler_keys
    has_birth = bool(traveler_keys & BIRTH_DATE_KEYS)
    missing_critical = []
    if not has_name:
        missing_critical.append("ad/soyad")
    if not has_passport:
        missing_critical.append("pasaport no")
    if not has_birth:
        missing_critical.append("doğum tarihi")
    detail = f"{len(traveler_keys)} alan eşlendi"
    if missing_critical:
        detail += f" · eksik: {', '.join(missing_critical)}"
    return {
        "key": "traveler",
        "label": "Yolcu alanları (ad, pasaport, doğum tarihi)",
        "ok": has_name and has_passport and has_birth,
        "detail": detail,
    }


def _browser_check() -> dict:
    ready = zami_rpa._chrome_executable() is not None or bool(os.environ.get("PLAYWRIGHT_BROWSERS_PATH"))
    return {
        "key": "browser",
        "label": "Sunucu tarayıcı motoru",
        "ok": ready,
        "detail": "Hazır" if ready else "Robot modu kullanılamaz; tarayıcı yardımcısını kullanın",
    }


def _session_check(session: dict) -> dict:
    expired = bool(session.get("expired"))
    detail = session.get("last_alive_at") or session.get("saved_at") or "Robot Oturumu sekmesinden giriş yapın"
    if expired:
        detail = "Oturum düştü · Robot Oturumu sekmesinden yeniden giriş yapın"
    return {
        "key": "session",
        "label": "Portal oturumu (captcha + OTP ile açılmış)",
        "ok": bool(session.get("has_session")) and not expired,
        "detail": detail,
    }


@router.get("/admin/zami/readiness")
async def zami_readiness(admin: dict = Depends(require_admin)) -> dict:
    """Ilk gercek aktarim oncesi hazirlik kontrolu."""
    mapping = await zami.get_mapping()
    session = await zami_rpa.session_status()
    captured = await zami.get_capture()

    checks = [
        _capture_check(captured),
        *_mapping_checks(mapping),
        _traveler_check(mapping),
        _browser_check(),
        _session_check(session),
    ]
    by_key = {c["key"]: c["ok"] for c in checks}
    ready_bookmarklet = all(by_key.get(key) for key in ("form_url", "fields", "traveler"))
    ready_robot = ready_bookmarklet and all(by_key.get(key) for key in ("browser", "session"))
    return {
        "checks": checks,
        "ready_bookmarklet": ready_bookmarklet,
        "ready_robot": ready_robot,
    }


# ------------------------------------------------------------ WhatsApp bildirimi
class WhatsAppSettingsIn(BaseModel):
    enabled: Optional[bool] = None
    provider: Optional[str] = None
    template_text: Optional[str] = None
    only_optin: Optional[bool] = None
    meta_phone_number_id: Optional[str] = None
    meta_access_token: Optional[str] = None
    meta_template_name: Optional[str] = None
    meta_template_language: Optional[str] = None
    meta_api_version: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_from: Optional[str] = None
    twilio_content_sid: Optional[str] = None


class WhatsAppSendIn(BaseModel):
    status: Optional[str] = None
    force: bool = True


@router.get("/admin/whatsapp/settings")
async def whatsapp_get_settings(admin: dict = Depends(require_admin)) -> dict:
    import whatsapp

    return {"settings": await whatsapp.get_settings()}


@router.put("/admin/whatsapp/settings")
async def whatsapp_save_settings(payload: WhatsAppSettingsIn, admin: dict = Depends(require_admin)) -> dict:
    import whatsapp

    return {"settings": await whatsapp.save_settings(payload.model_dump(exclude_none=True))}


@router.post("/admin/whatsapp/send/{application_id}")
async def whatsapp_send(application_id: str, payload: WhatsAppSendIn, request: Request, admin: dict = Depends(require_admin)):
    import whatsapp

    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    status = payload.status or app_doc.get("status") or "approved"
    return await whatsapp.notify_result(app_doc, status, _base_url(request), force=payload.force)


@router.get("/admin/whatsapp/logs")
async def whatsapp_logs(application_id: Optional[str] = None, admin: dict = Depends(require_admin)) -> dict:
    import whatsapp

    query = {"application_id": application_id} if application_id else {}
    docs = await whatsapp.logs_col.find(query).sort("created_at", -1).limit(50).to_list(50)
    return {"items": serialize_doc(docs)}


# ------------------------------------------------- toplu aktarim & durum takibi
@router.get("/admin/zami/candidates")
async def zami_candidates(admin: dict = Depends(require_admin)) -> dict:
    """Zami'ye aktarilmaya uygun basvurular (odemesi alinmis / inceleme asamasinda)."""
    query = {"status": {"$in": ["submitted", "payment_pending", "documents_pending", "reviewing"]}}
    docs = await applications_col.find(query).sort("created_at", -1).limit(100).to_list(100)
    items = []
    for d in docs:
        items.append(
            {
                "id": d.get("id"),
                "reference_code": d.get("reference_code"),
                "full_name": (d.get("contact") or {}).get("full_name", ""),
                "email": (d.get("contact") or {}).get("email", ""),
                "traveler_count": len(d.get("travelers") or []),
                "status": d.get("status"),
                "payment_status": (d.get("payment") or {}).get("status"),
                "created_at": d.get("created_at").isoformat() if d.get("created_at") else None,
                "zami_reference": d.get("zami_reference") or "",
                "zami_status": d.get("zami_status") or "",
                "zami_transferred_at": d.get("zami_transferred_at").isoformat()
                if isinstance(d.get("zami_transferred_at"), object) and d.get("zami_transferred_at")
                else None,
            }
        )
    return {"items": items}


@router.post("/admin/zami/bulk-transfer")
async def zami_bulk_transfer(payload: BulkTransferIn, request: Request, admin: dict = Depends(require_admin)) -> dict:
    """Secilen basvurulari sirayla Zami formuna doldurur (dry_run kapaliysa gonderir)."""
    base = _base_url(request)
    results = []
    for app_id in payload.application_ids:
        app_doc = await applications_col.find_one({"id": app_id})
        if not app_doc:
            results.append({"application_id": app_id, "ok": False, "error": "Başvuru bulunamadı."})
            continue
        data = zami.build_payload(app_doc, base)
        res = await zami_rpa.fill_application(
            app_doc, data, dry_run=bool(payload.dry_run), actor=admin.get("sub", "")
        )
        res.pop("screenshot", None)
        if res.get("ok"):
            await applications_col.update_one(
                {"id": app_id},
                {"$set": {"zami_transferred_at": datetime.now(timezone.utc), "zami_submitted": bool(res.get("submitted"))}},
            )
        results.append(
            {
                "application_id": app_id,
                "reference_code": app_doc.get("reference_code"),
                "ok": res.get("ok", False),
                "submitted": res.get("submitted", False),
                "filled_count": res.get("filled_count", 0),
                "missing": res.get("missing", [])[:10],
                "error": res.get("error"),
            }
        )
        if not res.get("ok") and "oturum" in (res.get("error") or "").lower():
            break  # oturum yoksa devam etmenin anlami yok
        await asyncio.sleep(1.0)
    ok_count = sum(1 for r in results if r["ok"])
    await zami.log_event(
        None,
        None,
        "bulk_transfer",
        f"{ok_count}/{len(results)} başvuru aktarıldı (dry_run={payload.dry_run})",
        actor=admin.get("sub", ""),
    )
    return {"results": results, "ok_count": ok_count, "total": len(results)}


@router.put("/admin/zami/reference/{application_id}")
async def zami_set_reference(application_id: str, payload: ZamiReferenceIn, admin: dict = Depends(require_admin)) -> dict:
    res = await applications_col.update_one(
        {"id": application_id},
        {"$set": {"zami_reference": payload.zami_reference.strip(), "updated_at": datetime.now(timezone.utc)}},
    )
    if not res.matched_count:
        raise HTTPException(404, "Basvuru bulunamadi.")
    return {"ok": True, "zami_reference": payload.zami_reference.strip()}


@router.post("/admin/zami/check-status/{application_id}")
async def zami_check_status(application_id: str, payload: StatusCheckIn, admin: dict = Depends(require_admin)):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    result = await zami_rpa.check_status(app_doc)
    if result.get("ok"):
        applied = await apply_status_result(app_doc, result, notify=payload.notify, actor=admin.get("sub", ""))
        result.update(applied)
    return result


@router.post("/admin/zami/check-status-all")
async def zami_check_status_all(admin: dict = Depends(require_admin)):
    from zami_status import sweep_statuses

    return await sweep_statuses(actor=admin.get("sub", ""), force=True)


async def apply_status_result(app_doc: dict, result: dict, notify: bool = True, actor: str = "") -> dict:
    """Portaldan okunan durumu basvuruya isler ve gerekiyorsa musteriyi bilgilendirir."""
    from zami_status import apply_status

    return await apply_status(app_doc, result, notify=notify, actor=actor)


# ------------------------------------------------------------- admin: RPA (B)
@router.post("/admin/zami/session/start")
async def zami_session_start(admin: dict = Depends(require_admin)):
    return await zami_rpa.start_session(actor=admin.get("sub", ""))


@router.post("/admin/zami/session/captcha")
async def zami_session_captcha(payload: LoginIn, admin: dict = Depends(require_admin)):
    return await zami_rpa.refresh_captcha(payload.session_id)


@router.post("/admin/zami/session/login")
async def zami_session_login(payload: LoginIn, admin: dict = Depends(require_admin)):
    return await zami_rpa.submit_login(
        payload.session_id, payload.captcha or "", payload.otp or "", actor=admin.get("sub", "")
    )


@router.delete("/admin/zami/session")
async def zami_session_clear(admin: dict = Depends(require_admin)):
    return await zami_rpa.clear_session()


@router.post("/admin/zami/transfer/{application_id}")
async def zami_transfer(application_id: str, payload: TransferIn, request: Request, admin: dict = Depends(require_admin)):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    data = zami.build_payload(app_doc, _base_url(request))
    result = await zami_rpa.fill_application(
        app_doc, data, dry_run=bool(payload.dry_run), actor=admin.get("sub", "")
    )
    # Portal basvuru numarasi dondurduyse basvuruya isle
    reference = (result or {}).get("zami_reference") or ""
    if reference:
        await applications_col.update_one(
            {"id": application_id},
            {
                "$set": {
                    "zami_reference": reference,
                    "zami_status": "submitted",
                    "zami_submitted_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        await zami.log_event(
            application_id,
            app_doc.get("reference_code"),
            "rpa_submitted",
            f"Zami basvurusu olusturuldu: {reference}",
            actor=admin.get("sub", ""),
        )
    return result


# ------------------------------------- public (token korumali) bookmarklet API
@router.get("/zami/handoff/{token}")
async def zami_handoff_payload(token: str, request: Request):
    doc = await zami.consume_handoff(token)
    if not doc:
        raise HTTPException(404, "Aktarim kodu gecersiz veya suresi dolmus.")
    app_doc = await applications_col.find_one({"id": doc["application_id"]})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    payload = zami.build_payload(app_doc, doc.get("base_url") or _base_url(request))
    payload["mapping"] = await zami.get_mapping()
    return payload


@router.post("/admin/applications/{application_id}/visa-document/auto-fetch")
async def admin_auto_fetch_visa(
    application_id: str, request: Request, admin: dict = Depends(require_admin)
) -> dict:
    """Onaylanan vize belgesini Zami'den indirip musteriye e-postayla iletir."""
    from visa_delivery import deliver_visa_document

    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    if not app_doc.get("zami_reference"):
        raise HTTPException(400, "Basvurunun Zami numarasi (VS-xxxxx) kayitli degil.")
    result = await deliver_visa_document(app_doc, _base_url(request))
    await zami.log_event(
        application_id,
        app_doc.get("reference_code"),
        "visa_autofetch",
        "Vize belgesi otomatik indirme denemesi: "
        + ("basarili" if result.get("ok") else str(result.get("reason"))),
        actor=admin.get("sub", ""),
    )
    return result


@router.get("/zami/bookmarklet.js")
async def zami_bookmarklet(request: Request):
    """Zami form sayfasinda calistirilan otomatik doldurma scripti."""
    from fastapi.responses import Response

    base = _base_url(request)
    script = BOOKMARKLET_JS.replace("__BASE__", base)
    return Response(content=script, media_type="application/javascript; charset=utf-8")


BOOKMARKLET_JS = r"""
(function () {
  var BASE = (function () {
    try {
      var src = document.currentScript && document.currentScript.src;
      if (src) return new URL(src).origin;
    } catch (e) {}
    return "__BASE__";
  })();
  var token = window.__VIZEATLAS_TOKEN__ || window.prompt("VizeAtlas aktarım kodunu yapıştırın:");
  if (!token) return;
  var box = document.createElement("div");
  box.style.cssText =
    "position:fixed;z-index:2147483647;right:16px;bottom:16px;max-width:340px;font:13px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;" +
    "background:#0B1F33;color:#fff;padding:14px 16px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.35)";
  box.innerHTML = "<b>VizeAtlas</b><br>Veriler alınıyor…";
  document.body.appendChild(box);

  function setVal(el, value) {
    if (!el) return false;
    var tag = el.tagName.toLowerCase();
    if (tag === "select") {
      var matched = false;
      for (var i = 0; i < el.options.length; i++) {
        var o = el.options[i];
        if (
          String(o.value).toLowerCase() === String(value).toLowerCase() ||
          o.text.trim().toLowerCase() === String(value).toLowerCase()
        ) {
          el.selectedIndex = i;
          matched = true;
          break;
        }
      }
      if (!matched) return false;
    } else if (el.type === "file") {
      return false;
    } else {
      el.focus();
      el.value = value;
    }
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    el.style.outline = "2px solid #1E9E62";
    return true;
  }

  fetch(BASE + "/api/zami/handoff/" + encodeURIComponent(token))
    .then(function (r) {
      if (!r.ok) throw new Error("Kod geçersiz veya süresi dolmuş");
      return r.json();
    })
    .then(function (data) {
      var mapping = data.mapping || { fields: {}, traveler_fields: {} };
      var ok = 0,
        miss = [];
      Object.keys(mapping.fields || {}).forEach(function (key) {
        var sel = mapping.fields[key];
        var el = document.querySelector(sel);
        if (setVal(el, data.globals[key] || "")) ok++;
        else miss.push(sel);
      });
      (data.travelers || []).forEach(function (traveler, idx) {
        Object.keys(mapping.traveler_fields || {}).forEach(function (key) {
          var sel = String(mapping.traveler_fields[key])
            .replace(/\{i\}/g, String(idx))
            .replace(/\{n\}/g, String(idx + 1));
          var el = document.querySelector(sel);
          if (setVal(el, traveler[key] || "")) ok++;
          else miss.push(sel);
        });
      });
      var docsHtml = (data.documents || [])
        .map(function (d) {
          return (
            '<li style="margin:4px 0"><a target="_blank" style="color:#7CD5A6" href="' +
            d.url +
            '">' +
            d.label +
            "</a></li>"
          );
        })
        .join("");
      box.innerHTML =
        "<b>VizeAtlas · " +
        (data.reference_code || "") +
        "</b><br>" +
        ok +
        " alan dolduruldu" +
        (miss.length ? ", " + miss.length + " alan bulunamadı" : "") +
        '<div style="margin-top:8px;font-size:12px;opacity:.85">Belgeler (indirip yükleyin):</div><ul style="margin:4px 0 0;padding-left:18px">' +
        docsHtml +
        "</ul>" +
        '<div style="margin-top:10px;text-align:right"><button style="background:#1E9E62;color:#fff;border:0;border-radius:8px;padding:6px 10px;cursor:pointer">Kapat</button></div>';
      box.querySelector("button").onclick = function () {
        box.remove();
      };
    })
    .catch(function (err) {
      box.innerHTML = "<b>VizeAtlas</b><br>Hata: " + err.message;
    });
})();
"""
