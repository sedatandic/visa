"""Zami Tours aktarim API'leri (admin + bookmarklet)."""

import logging
import os
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


# ------------------------------------------------------------ admin: ayarlar
@router.get("/admin/zami/config")
async def zami_config(admin=Depends(require_admin)):
    return {
        "settings": await zami.get_settings(),
        "mapping": await zami.get_mapping(),
        "session": await zami_rpa.session_status(),
        "global_fields": [{"key": k, "label": v} for k, v in zami.GLOBAL_FIELDS],
        "traveler_fields": [{"key": k, "label": v} for k, v in zami.TRAVELER_FIELDS],
    }


@router.put("/admin/zami/settings")
async def zami_save_settings(payload: SettingsIn, admin=Depends(require_admin)):
    return {"settings": await zami.save_settings(payload.model_dump(exclude_none=True))}


@router.put("/admin/zami/mapping")
async def zami_save_mapping(payload: MappingIn, admin=Depends(require_admin)):
    mapping = await zami.save_mapping(payload.model_dump())
    await zami.log_event(None, None, "mapping_saved", "Alan eslemesi guncellendi", actor=admin.get("sub", ""))
    return {"mapping": mapping}


@router.post("/admin/zami/parse-form")
async def zami_parse_form(payload: ParseHtmlIn, admin=Depends(require_admin)):
    fields = zami.parse_form_fields(payload.html)
    if not fields:
        raise HTTPException(400, "HTML icinde doldurulabilir form alani bulunamadi.")
    return {"fields": fields, "count": len(fields)}


# ------------------------------------------------- admin: bookmarklet handoff
@router.post("/admin/zami/handoff/{application_id}")
async def zami_handoff(application_id: str, request: Request, admin=Depends(require_admin)):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    base = _base_url(request)
    data = await zami.create_handoff(app_doc, admin.get("sub", ""), base)
    data["bookmarklet_url"] = f"{base}/api/zami/bookmarklet.js"
    return data


@router.get("/admin/zami/payload/{application_id}")
async def zami_payload(application_id: str, request: Request, admin=Depends(require_admin)):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    return zami.build_payload(app_doc, _base_url(request))


@router.get("/admin/zami/logs")
async def zami_log_list(application_id: Optional[str] = None, admin=Depends(require_admin)):
    query = {"application_id": application_id} if application_id else {}
    docs = await zami_logs_col.find(query).sort("created_at", -1).limit(100).to_list(100)
    return {"items": serialize_doc(docs)}


# ------------------------------------------------------------- admin: RPA (B)
@router.post("/admin/zami/session/start")
async def zami_session_start(admin=Depends(require_admin)):
    return await zami_rpa.start_session(actor=admin.get("sub", ""))


@router.post("/admin/zami/session/captcha")
async def zami_session_captcha(payload: LoginIn, admin=Depends(require_admin)):
    return await zami_rpa.refresh_captcha(payload.session_id)


@router.post("/admin/zami/session/login")
async def zami_session_login(payload: LoginIn, admin=Depends(require_admin)):
    return await zami_rpa.submit_login(
        payload.session_id, payload.captcha or "", payload.otp or "", actor=admin.get("sub", "")
    )


@router.delete("/admin/zami/session")
async def zami_session_clear(admin=Depends(require_admin)):
    return await zami_rpa.clear_session()


@router.post("/admin/zami/transfer/{application_id}")
async def zami_transfer(application_id: str, payload: TransferIn, request: Request, admin=Depends(require_admin)):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    data = zami.build_payload(app_doc, _base_url(request))
    return await zami_rpa.fill_application(
        app_doc, data, dry_run=bool(payload.dry_run), actor=admin.get("sub", "")
    )


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
