"""Onay (consent) alanlarinin basvuru ile kaydedildigini dogrular."""
import io
import os

import requests
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv("/app/backend/.env")
BASE = open("/app/frontend/.env").read().split("REACT_APP_BACKEND_URL=")[1].split("\n")[0].strip()
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000a49444154789c6300010000050001"
    "0d0a2db40000000049454e44ae426082"
)

s = requests.Session()


def upload():
    r = s.post(
        f"{BASE}/api/uploads",
        files={"file": ("t.png", io.BytesIO(PNG), "image/png")},
        data={"doc_type": "passport"},
        timeout=60,
    )
    return r.json()["file_id"]


visa = next(v for v in s.get(f"{BASE}/api/visa-types", timeout=15).json() if v["id"] == "visa_30_single")
fid_a, fid_b = upload(), upload()
payload = {
    "contact": {
        "full_name": "TEST_consent Kullanici",
        "email": "delivered@resend.dev",
        "phone": "+90 532 588 26 30",
        "address_city": "Istanbul",
        "whatsapp_optin": True,
    },
    "travelers": [
        {
            "first_name": "AHMET",
            "last_name": "TEST",
            "birth_date": "1990-05-15",
            "gender": "male",
            "applicant_type": "adult",
            "nationality": "TR",
            "passport_no": "U99887766",
            "passport_expiry": "2032-12-31",
            "visa_type_id": visa["id"],
            "passport_file_id": fid_a,
            "photo_file_id": fid_b,
        }
    ],
    "travel": {
        "arrival_date": "",
        "departure_date": "",
        "dates_unknown": True,
        "travel_window": "1-3ay",
        "purpose": "tourism",
        "birth_country": "TR",
    },
    "addons": {},
    "extra_documents": {},
    "kvkk_accepted": True,
    "consents": {
        "refund_privacy_accepted": True,
        "service_terms_accepted": True,
        "marketing_email_optin": True,
        "ad_personalization_optin": False,
    },
}
r = s.post(f"{BASE}/api/applications", json=payload, timeout=60)
print("create application:", r.status_code, r.json().get("reference_code"))
ref = r.json()["reference_code"]

db = MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
doc = db.visa_applications.find_one({"reference_code": ref})
print("stored consents:", doc.get("consents"))
assert doc["consents"]["refund_privacy_accepted"] is True
assert doc["consents"]["marketing_email_optin"] is True
assert doc["consents"]["ad_personalization_optin"] is False
assert doc["consents"].get("accepted_at")
print("OK")

legal = s.get(f"{BASE}/api/content/legal", timeout=15).json()
print("legal docs:", list(legal.keys()))
assert set(legal) == {"refund_terms", "service_terms", "privacy_policy", "marketing_consent"}
