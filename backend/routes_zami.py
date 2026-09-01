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
async def zami_config(admin=Depends(require_admin)):
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


class CaptureIn(BaseModel):
    page_type: str = Field("form", max_length=20)
    url: Optional[str] = ""
    fields: list = Field(default_factory=list)
    submit_selector: Optional[str] = ""
    search_selector: Optional[str] = ""
    row_selector: Optional[str] = ""
    sample_text: Optional[str] = ""


@router.post("/admin/zami/capture-token")
async def zami_capture_token(request: Request, admin=Depends(require_admin)):
    return await zami.create_capture_token(admin.get("sub", ""), _base_url(request))


@router.post("/admin/zami/apply-suggestions")
async def zami_apply_suggestions(admin=Depends(require_admin)):
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
async def zami_capture(token: str, payload: CaptureIn):
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


# ------------------------------------------------- toplu aktarim & durum takibi
@router.get("/admin/zami/candidates")
async def zami_candidates(admin=Depends(require_admin)):
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
async def zami_bulk_transfer(payload: BulkTransferIn, request: Request, admin=Depends(require_admin)):
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
async def zami_set_reference(application_id: str, payload: ZamiReferenceIn, admin=Depends(require_admin)):
    res = await applications_col.update_one(
        {"id": application_id},
        {"$set": {"zami_reference": payload.zami_reference.strip(), "updated_at": datetime.now(timezone.utc)}},
    )
    if not res.matched_count:
        raise HTTPException(404, "Basvuru bulunamadi.")
    return {"ok": True, "zami_reference": payload.zami_reference.strip()}


@router.post("/admin/zami/check-status/{application_id}")
async def zami_check_status(application_id: str, payload: StatusCheckIn, admin=Depends(require_admin)):
    app_doc = await applications_col.find_one({"id": application_id})
    if not app_doc:
        raise HTTPException(404, "Basvuru bulunamadi.")
    result = await zami_rpa.check_status(app_doc)
    if result.get("ok"):
        applied = await apply_status_result(app_doc, result, notify=payload.notify, actor=admin.get("sub", ""))
        result.update(applied)
    return result


@router.post("/admin/zami/check-status-all")
async def zami_check_status_all(admin=Depends(require_admin)):
    from zami_status import sweep_statuses

    return await sweep_statuses(actor=admin.get("sub", ""), force=True)


async def apply_status_result(app_doc: dict, result: dict, notify: bool = True, actor: str = "") -> dict:
    """Portaldan okunan durumu basvuruya isler ve gerekiyorsa musteriyi bilgilendirir."""
    from zami_status import apply_status

    return await apply_status(app_doc, result, notify=notify, actor=actor)


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
