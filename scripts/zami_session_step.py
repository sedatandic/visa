"""Backend surecinde canli Zami oturumu acar (oturum backend'de kalir).

Adim 1: python scripts/zami_session_step.py start
        -> captcha AI ile okunur, login denenir, OTP asamasina gecilir.
Adim 2: python scripts/zami_session_step.py otp 123456
        -> kullanicidan gelen OTP kodu ile girisi tamamlar.
"""
import base64
import json
import os
import sys
import urllib.request

BASE = "http://localhost:8001/api"
OUT = "/app/scripts/out"
STATE = "/app/scripts/out/session.json"
ADMIN_EMAIL = "admin@vizeatlas.com"
ADMIN_PASSWORD = "Dubai2026!"


def call(path: str, payload: dict | None = None, token: str = "", method: str = "POST") -> dict:
    data = json.dumps(payload or {}).encode() if payload is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode())


def save_data_url(data_url: str, path: str) -> None:
    if not data_url:
        return
    with open(path, "wb") as fh:
        fh.write(base64.b64decode(data_url.split(",", 1)[-1]))
    print(f"  -> {path}")


def solve_captcha(png_path: str) -> str:
    import asyncio
    import uuid

    sys.path.insert(0, "/app/backend")
    from dotenv import load_dotenv

    load_dotenv("/app/backend/.env")
    from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage

    async def run() -> str:
        with open(png_path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        chat = LlmChat(
            api_key=(os.environ.get("EMERGENT_LLM_KEY") or "").strip(),
            session_id=f"captcha-{uuid.uuid4()}",
            system_message="Sen bir captcha okuyucusun. Sadece goruntudeki sayiyi dondur.",
        ).with_model("openai", "gpt-5.4")
        resp = await chat.send_message(
            UserMessage(
                text="Bu captcha goruntusundeki 3 haneli sayiyi sadece rakam olarak dondur.",
                file_contents=[ImageContent(image_base64=b64)],
            )
        )
        text = resp if isinstance(resp, str) else str(resp)
        return "".join(ch for ch in text if ch.isdigit())

    return asyncio.run(run())


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    token = call("/admin/login", {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})["token"]
    action = sys.argv[1] if len(sys.argv) > 1 else "start"

    if action == "start":
        started = call("/admin/zami/session/start", {}, token)
        if not started.get("ok"):
            print("Oturum baslatilamadi:", started.get("error"))
            return
        session_id = started["session_id"]
        with open(STATE, "w") as fh:
            json.dump({"session_id": session_id}, fh)
        print(f"session_id={session_id} | kullanici: {started.get('username')}")
        guess = started.get("captcha_guess") or ""
        save_data_url(started.get("captcha_image"), f"{OUT}/s_captcha.png")

        for attempt in range(1, 5):
            code = guess or solve_captcha(f"{OUT}/s_captcha.png")
            print(f"Deneme {attempt}: captcha = '{code}'")
            result = call(
                "/admin/zami/session/login", {"session_id": session_id, "captcha": code}, token
            )
            save_data_url(result.get("screenshot"), f"{OUT}/s_login_result.jpg")
            print(f"  stage={result.get('stage')} ok={result.get('ok')} {result.get('error') or ''}")
            if result.get("stage") == "otp":
                print(f"\n>>> OTP BEKLENIYOR. session_id={session_id}")
                print(">>> Kod gelince: python scripts/zami_session_step.py otp <KOD>")
                return
            if result.get("ok") and result.get("stage") == "ready":
                print("\n>>> GIRIS BASARILI:", result.get("current_url"))
                return
            save_data_url(result.get("captcha_image"), f"{OUT}/s_captcha.png")
            guess = result.get("captcha_guess") or ""
        print("\n>>> Giris yapilamadi (4 deneme).")
        return

    if action == "otp":
        otp = sys.argv[2]
        session_id = json.load(open(STATE))["session_id"]
        result = call(
            "/admin/zami/session/login",
            {"session_id": session_id, "captcha": "", "otp": otp},
            token,
        )
        save_data_url(result.get("screenshot"), f"{OUT}/s_otp_result.jpg")
        print(f"stage={result.get('stage')} ok={result.get('ok')} {result.get('error') or ''}")
        print("url:", result.get("current_url"))
        return

    if action == "status":
        print(call("/admin/zami/readiness", None, token, method="GET"))


if __name__ == "__main__":
    main()
