import os
import re
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv("/app/backend/.env")
API = open("/app/frontend/.env").read().split("REACT_APP_BACKEND_URL=")[1].split("\n")[0].strip()
db = MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
email = "delivered@resend.dev"
db.login_codes.delete_many({"email": email})

r = requests.post(f"{API}/api/account/request-code", json={"email": email}, timeout=30)
print("request-code:", r.status_code, r.json())
doc = db.email_outbox.find_one({"to": email, "kind": "login_code"}, sort=[("created_at", -1)])
m = re.search(r">\s*(\d{6})\s*<", (doc or {}).get("html", "") or "")
code = m.group(1) if m else None
print("code from outbox:", code)

bad = requests.post(f"{API}/api/account/verify-code", json={"email": email, "code": "000000"}, timeout=30)
print("wrong code (expect 400):", bad.status_code, bad.json())
ok = requests.post(f"{API}/api/account/verify-code", json={"email": email, "code": code}, timeout=30)
print("correct code:", ok.status_code, list(ok.json().keys()) if ok.ok else ok.json())
token = ok.json().get("token") if ok.ok else None
if token:
    me = requests.get(f"{API}/api/account/me", headers={"Authorization": f"Bearer {token}"}, timeout=30)
    print("/account/me:", me.status_code, list(me.json().keys()))
    reuse = requests.post(f"{API}/api/account/verify-code", json={"email": email, "code": code}, timeout=30)
    print("code reuse (expect 400):", reuse.status_code, reuse.json())
print("code_plain in db:", bool((db.login_codes.find_one({"email": email}) or {}).get("code_plain")))
