"""WhatsApp 7/24 yapay zeka asistani (Claude Sonnet 4.6 + Emergent LLM key).

- Sitedeki guncel bilgiyle cevap verir (vize tipleri ve fiyatlar, eSIM/sigorta/tur
  paketleri, kur, SSS, iletisim, linkler).
- `DV-XXXXXX` basvuru kodu yazilirsa basvuru durumunu soyler (numara veya soyad dogrulamasi).
- Cevap veremezse veya musteri isterse temsilciye devreder.
"""

import logging
import os
import re
import uuid
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from db import applications_col, conversations_col, db
from content import COMPANY, FAQ, STATUS_LABELS

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_PROVIDER = "anthropic"
MODEL_NAME = "claude-sonnet-4-6"
MAX_REPLY_CHARS = 900
HISTORY_TURNS = 8
KB_TTL_SECONDS = 600

REFERENCE_RE = re.compile(r"\b(DV[-\s]?[A-Z0-9]{4,10})\b", re.IGNORECASE)
HANDOFF_WORDS = (
    "temsilci",
    "insan",
    "yetkili",
    "musteri hizmetleri",
    "müşteri hizmetleri",
    "canli destek",
    "canlı destek",
    "operator",
    "operatör",
    "sikayet",
    "şikayet",
    "iade",
)

SYSTEM_PROMPT = """Sen {brand} adli Dubai vize danismanlik firmasinin WhatsApp asistanisin.
Gorevin musterilere Turkce, kisa ve net yanit vermek. Musteri Ingilizce yazarsa Ingilizce yanitla.

KURALLAR:
- Yalnizca asagidaki BILGI TABANI'ndaki verilere dayanarak konus. Fiyat, sure, kural
  uydurmak kesinlikle yasak. Bilgi tabaninda olmayan bir sey sorulursa "bunu temsilcimize
  aktariyorum" de.
- Yanitlar en fazla 700 karakter olsun, WhatsApp icin kisa paragraflar ve gerekiyorsa
  madde isaretleri kullan. Emoji kullanma.
- Fiyat verirken bilgi tabanindaki TL fiyati soyle ve "guncel kurla" ifadesini ekle.
- Basvuru, sepet, takip gibi islemler icin bilgi tabanindaki linkleri paylas.
- Kisisel veri isteme; pasaport numarasi, kart bilgisi asla isteme.
- Musteri sikayetci, kizgin veya "temsilciye baglan" diyorsa kisa bir ozur/anlayis cumlesi
  yaz ve temsilciye aktardigini soyle.
- Vize onay suresi ve resmi kararlar konusunda garanti verme.

BILGI TABANI:
{kb}
"""

_kb_cache: dict = {"text": "", "at": None}


def _fmt_try(value) -> str:
    try:
        return f"{float(value):,.0f}".replace(",", ".") + " TL"
    except (TypeError, ValueError):
        return "-"


async def _visa_lines() -> list[str]:
    from fx import apply_fx_to_list
    from db import visa_types_col, serialize_doc
    from content import VISA_TYPES

    docs = await visa_types_col.find({"active": True}).sort("order", 1).to_list(100)
    items = serialize_doc(docs) if docs else VISA_TYPES
    priced = await apply_fx_to_list(items)
    lines = []
    for v in priced:
        lines.append(
            f"- {v.get('name')}: {_fmt_try(v.get('price'))} "
            f"(kalis {v.get('duration_days', '-')} gun, islem {v.get('processing_time', '-')})"
        )
    return lines


async def _product_lines() -> list[str]:
    from store_catalog import product_list

    items = await product_list()
    lines = []
    for p in items:
        unit = "kisi basi" if p["kind"] != "esim" else "paket"
        lines.append(f"- {p['kind_label']} · {p['name']}: {_fmt_try(p['price'])} ({unit})")
    return lines


async def knowledge_base(force: bool = False) -> str:
    """Site bilgilerinden LLM icin ozet bilgi tabani uretir (10 dk onbellek)."""
    now = datetime.now(timezone.utc)
    cached_at = _kb_cache.get("at")
    if not force and cached_at and (now - cached_at).total_seconds() < KB_TTL_SECONDS:
        return _kb_cache["text"]

    from fx import get_fx

    site = (os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")
    fx = await get_fx()
    parts: list[str] = ["VIZE TIPLERI VE FIYATLAR (guncel kurla TL):"]
    parts += await _visa_lines()
    parts.append("")
    parts.append("EK HIZMETLER (sepetten ayri satin alinabilir):")
    parts += await _product_lines()
    parts.append("- Sigorta + eSIM birlikte alinirsa sepette %10 paket indirimi uygulanir.")
    parts.append("")
    parts.append(f"KUR: 1 USD = {fx.get('effective_rate')} TL (kaynak: {fx.get('source')})")
    parts.append("")
    parts.append("LINKLER:")
    parts.append(f"- Basvuru: {site}/basvuru")
    parts.append(f"- Basvuru takibi: {site}/takip")
    parts.append(f"- Vize tipleri ve fiyatlar: {site}/vize-tipleri")
    parts.append(f"- Sepet: {site}/sepet")
    parts.append(f"- eSIM: {site}/esim")
    parts.append(f"- Seyahat sigortasi: {site}/seyahat-sigortasi")
    parts.append(f"- Col safarisi turlari: {site}/dubai-turlari")
    parts.append("")
    parts.append("FIRMA BILGILERI:")
    parts.append(f"- Marka: {COMPANY['brand']} ({COMPANY['legal_name']})")
    parts.append(f"- Dubai ofis: {COMPANY['dubai_company']}, {COMPANY['dubai_address']}")
    parts.append(f"- Telefon: {COMPANY['phone']} · Dubai: {COMPANY['dubai_phone']}")
    parts.append(f"- E-posta: {COMPANY['email']}")
    parts.append(f"- Calisma saatleri: {COMPANY['working_hours']}")
    parts.append("")
    parts.append("SIKCA SORULAN SORULAR:")
    for item in FAQ[:14]:
        parts.append(f"S: {item['q']}\nC: {item['a']}")

    text = "\n".join(parts)
    _kb_cache.update({"text": text, "at": now})
    return text


def wants_human(text: str) -> bool:
    lowered = (text or "").lower()
    return any(word in lowered for word in HANDOFF_WORDS)


async def application_status_text(text: str, wa_id: str) -> str | None:
    """Mesajda basvuru kodu varsa durum ozetini dondurur."""
    match = REFERENCE_RE.search(text or "")
    if not match:
        return None
    code = re.sub(r"[\s-]", "", match.group(1)).upper()
    code = f"DV-{code[2:]}" if code.startswith("DV") else code
    doc = await applications_col.find_one({"reference_code": code})
    if not doc:
        return f"{code} numaralı bir başvuru bulamadım. Kodu kontrol edip tekrar yazabilir misiniz?"

    contact = doc.get("contact") or {}
    from whatsapp import normalize_phone

    app_phone = (normalize_phone(contact.get("phone")) or "").lstrip("+")
    sender = (wa_id or "").lstrip("+")
    surname_ok = False
    travelers = doc.get("travelers") or []
    for t in travelers:
        last_name = (t.get("last_name") or "").strip().lower()
        if last_name and last_name in (text or "").lower():
            surname_ok = True
            break
    if app_phone and sender and app_phone != sender and not surname_ok:
        return (
            f"{code} numaralı başvuruyu buldum ancak güvenlik için doğrulama gerekiyor. "
            "Başvurudaki soyadı da yazar mısınız?"
        )

    status = doc.get("status", "")
    label = STATUS_LABELS.get(status, status)
    site = (os.environ.get("PUBLIC_SITE_URL") or "").rstrip("/")
    lines = [f"{code} numaralı başvurunuzun durumu: {label}."]
    if status == "approved" and (doc.get("visa_result") or {}).get("file_id"):
        lines.append("Vize belgeniz e-posta adresinize gönderildi.")
    if status in ("pending_documents", "documents_missing"):
        lines.append("Eksik belgelerinizi yükledikten sonra işlem devam eder.")
    lines.append(f"Detay: {site}/takip")
    return " ".join(lines)


async def _history_text(conversation: dict) -> str:
    messages = (conversation.get("messages") or [])[-HISTORY_TURNS * 2 :]
    lines = []
    for m in messages:
        who = "Musteri" if m.get("role") == "user" else "Asistan"
        lines.append(f"{who}: {(m.get('text') or '')[:400]}")
    return "\n".join(lines)


async def ask_llm(conversation: dict, text: str) -> str:
    api_key = (os.environ.get("EMERGENT_LLM_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("EMERGENT_LLM_KEY tanimli degil.")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    kb = await knowledge_base()
    system = SYSTEM_PROMPT.format(brand=COMPANY["brand"], kb=kb)
    history = await _history_text(conversation)
    prompt = text if not history else f"Onceki konusma:\n{history}\n\nYeni mesaj:\n{text}"

    chat = LlmChat(
        api_key=api_key,
        session_id=conversation.get("session_id") or f"wa-{uuid.uuid4()}",
        system_message=system,
    ).with_model(MODEL_PROVIDER, MODEL_NAME)
    response = await chat.send_message(UserMessage(text=prompt))
    reply = response if isinstance(response, str) else str(response)
    return reply.strip()[:MAX_REPLY_CHARS]


async def build_reply(conversation: dict, text: str) -> dict:
    """Gelen mesaja yanit uretir. `needs_human` true ise temsilciye devredilir."""
    status_reply = await application_status_text(text, conversation.get("wa_id", ""))
    if status_reply:
        return {"text": status_reply, "needs_human": False, "source": "status"}

    if wants_human(text):
        return {
            "text": (
                "Anladım, sizi hemen bir temsilcimize aktarıyorum. Çalışma saatlerimiz "
                f"{COMPANY['working_hours']}. Bu arada sorunuzu yazabilirsiniz, temsilcimiz "
                "en kısa sürede dönüş yapacak."
            ),
            "needs_human": True,
            "source": "handoff",
        }

    try:
        reply = await ask_llm(conversation, text)
    except Exception as exc:
        logger.error("wa bot llm failed: %s", exc)
        return {
            "text": (
                "Şu anda yanıt üretemedim, sorunuzu temsilcimize aktardım. "
                f"Dilerseniz {COMPANY['phone']} numarasından da ulaşabilirsiniz."
            ),
            "needs_human": True,
            "source": "error",
        }

    if not reply:
        return {
            "text": "Sorunuzu tam anlayamadım, temsilcimize aktarıyorum.",
            "needs_human": True,
            "source": "empty",
        }
    lowered = reply.lower()
    needs_human = "temsilc" in lowered and "aktar" in lowered
    return {"text": reply, "needs_human": needs_human, "source": "llm"}


async def get_conversation(wa_id: str, profile_name: str = "") -> dict:
    now = datetime.now(timezone.utc)
    doc = await conversations_col.find_one({"wa_id": wa_id})
    if doc:
        if profile_name and not doc.get("profile_name"):
            await conversations_col.update_one(
                {"wa_id": wa_id}, {"$set": {"profile_name": profile_name}}
            )
            doc["profile_name"] = profile_name
        return doc
    doc = {
        "id": str(uuid.uuid4()),
        "wa_id": wa_id,
        "session_id": f"wa-{wa_id}-{uuid.uuid4().hex[:8]}",
        "profile_name": profile_name,
        "bot_enabled": True,
        "needs_human": False,
        "messages": [],
        "message_count": 0,
        "created_at": now,
        "updated_at": now,
        "last_inbound_at": now,
    }
    await conversations_col.insert_one(dict(doc))
    return doc


async def append_message(wa_id: str, role: str, text: str, extra: dict | None = None) -> None:
    now = datetime.now(timezone.utc)
    entry = {"role": role, "text": (text or "")[:2000], "at": now, **(extra or {})}
    update: dict = {
        "$push": {"messages": {"$each": [entry], "$slice": -60}},
        "$set": {"updated_at": now},
        "$inc": {"message_count": 1},
    }
    if role == "user":
        update["$set"]["last_inbound_at"] = now
    else:
        update["$set"]["last_outbound_at"] = now
    await conversations_col.update_one({"wa_id": wa_id}, update)


def within_service_window(conversation: dict) -> bool:
    """Musteri son 24 saatte yazdiysa serbest metin gonderilebilir."""
    last = conversation.get("last_inbound_at")
    if not isinstance(last, datetime):
        return False
    if not last.tzinfo:
        last = last.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) - last < timedelta(hours=24)
