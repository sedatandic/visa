"""Iteration 58: Otomatik police kesim kuyrugu + kar paneli + validity filtre.

Kapsam:
- GET /api/products?kind=insurance -> 6 police (ins_8d..ins_60d_plus) + cost_try
- GET /api/admin/insurance-report -> item/totals kar tablosu
- PATCH /api/admin/products/{id} -> price_try + cost_try guncelleme
- POST /api/orders + PATCH /api/admin/orders/{id} paid -> insurance-tasks pending olusur
- Idempotent: ikinci paid ikinci task olusturmaz
- POST /api/uploads + POST /api/admin/insurance-tasks/{id}/issue -> status issued
- email_outbox insurance_pending / insurance_policy_sent kayitlari
- Yalniz eSIM siparis -> HIC insurance task olusmamali
"""

import io
import os
import time
import uuid

import pytest
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", ".env"))

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")

ADMIN_EMAIL = os.environ["ADMIN_LOGIN_EMAIL"]
ADMIN_PASS = os.environ["ADMIN_LOGIN_PASSWORD"]

EXPECTED_INSURANCE = {
    "ins_8d": {"days": 8, "price": 491},
    "ins_15d": {"days": 15, "price": 560},
    "ins_30d": {"days": 30, "price": 644},
    "ins_30d_plus": {"days": 30, "price": 2754},
    "ins_60d": {"days": 60, "price": 735},
    "ins_60d_plus": {"days": 60, "price": 3989},
}


@pytest.fixture(scope="module")
def api():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_token(api):
    r = api.post(f"{BASE_URL}/api/admin/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
    if r.status_code != 200:
        pytest.skip(f"admin login failed: {r.status_code} {r.text}")
    return r.json()["token"]


@pytest.fixture(scope="module")
def admin(api, admin_token):
    api2 = requests.Session()
    api2.headers.update({"Content-Type": "application/json", "Authorization": f"Bearer {admin_token}"})
    return api2


# 1) katalog
def test_insurance_products(api):
    r = api.get(f"{BASE_URL}/api/products?kind=insurance")
    assert r.status_code == 200
    items = {p["id"]: p for p in r.json()["items"]}
    for pid, want in EXPECTED_INSURANCE.items():
        assert pid in items, f"missing {pid}"
        p = items[pid]
        assert p.get("validity_days") == want["days"], f"{pid} days"
        assert abs(float(p.get("price_try") or p.get("price") or 0) - want["price"]) <= 1, f"{pid} price"
        assert p.get("cost_try") is not None and float(p["cost_try"]) > 0, f"{pid} cost missing"


# 2) kar raporu
def test_insurance_report(admin):
    r = admin.get(f"{BASE_URL}/api/admin/insurance-report")
    assert r.status_code == 200, r.text
    body = r.json()
    ids = {row["id"] for row in body["items"]}
    for pid in EXPECTED_INSURANCE:
        assert pid in ids
    for row in body["items"]:
        assert row["cost_try"] > 0
        assert row["price_try"] > 0
        assert row["profit_try"] == round(row["price_try"] - row["cost_try"], 2)
        # ~%100 marj
        assert row["margin_pct"] is not None and 90 <= row["margin_pct"] <= 110
    totals = body["totals"]
    assert set(totals.keys()) >= {"sold_quantity", "revenue_try", "cost_total_try", "profit_total_try"}


# 3) urun fiyat/maliyet update -> report yeniden hesapliyor
def test_update_product_recomputes_margin(admin):
    # snapshot orig
    r = admin.get(f"{BASE_URL}/api/admin/insurance-report")
    row0 = next(x for x in r.json()["items"] if x["id"] == "ins_30d")
    orig_price, orig_cost = row0["price_try"], row0["cost_try"]

    # yeni degerler: price=800, cost=400 -> margin=100
    up = admin.patch(f"{BASE_URL}/api/admin/products/ins_30d", json={"price_try": 800, "cost_try": 400})
    assert up.status_code == 200, up.text
    r2 = admin.get(f"{BASE_URL}/api/admin/insurance-report")
    row1 = next(x for x in r2.json()["items"] if x["id"] == "ins_30d")
    assert row1["price_try"] == 800
    assert row1["cost_try"] == 400
    assert row1["margin_pct"] == 100

    # geri al
    admin.patch(
        f"{BASE_URL}/api/admin/products/ins_30d",
        json={"price_try": orig_price or 644, "cost_try": orig_cost or 322.22},
    )


# 4-5) siparis olustur, paid yap, task olusur; ikinci paid idempotent
@pytest.fixture(scope="module")
def paid_order(api, admin):
    payload = {
        "items": [{"product_id": "ins_30d", "quantity": 2}],
        "contact": {
            "full_name": "TEST Insurance Auto",
            "email": f"test.ins.{uuid.uuid4().hex[:6]}@example.com",
            "phone": "+905551112233",
        },
        "travel_start": "2026-03-01",
        "travel_end": "2026-03-08",
        "payment_method": "card",
    }
    r = api.post(f"{BASE_URL}/api/orders", json=payload)
    assert r.status_code == 200, r.text
    order = r.json()["order"]
    # paid
    up = admin.patch(f"{BASE_URL}/api/admin/orders/{order['id']}", json={"payment_status": "paid"})
    assert up.status_code == 200, up.text
    time.sleep(0.5)
    return order


def test_task_created_on_paid(admin, paid_order):
    r = admin.get(f"{BASE_URL}/api/admin/insurance-tasks?status=pending")
    assert r.status_code == 200
    tasks = [t for t in r.json()["items"] if t.get("order_id") == paid_order["id"]]
    assert len(tasks) == 1, f"expected 1 task, got {len(tasks)}"
    t = tasks[0]
    assert t["status"] == "pending"
    assert t["plan_name"]
    assert t["validity_days"] == 30
    assert t["quantity"] == 2
    assert "seyahatpolicesi.com" in (t.get("provider_link") or "")
    assert t["customer"]["email"] == paid_order["contact"]["email"]
    assert t["customer"]["full_name"] == "TEST Insurance Auto"
    assert t["customer"]["phone"]


def test_paid_idempotent(admin, paid_order):
    # ikinci paid ikinci task olusturmamali
    admin.patch(f"{BASE_URL}/api/admin/orders/{paid_order['id']}", json={"payment_status": "paid"})
    time.sleep(0.3)
    r = admin.get(f"{BASE_URL}/api/admin/insurance-tasks?status=pending")
    tasks = [t for t in r.json()["items"] if t.get("order_id") == paid_order["id"]]
    assert len(tasks) == 1


# 6) pending mail + notification
def test_pending_email_and_notification(admin, paid_order):
    # email_outbox
    r = admin.get(f"{BASE_URL}/api/admin/emails?limit=100")
    assert r.status_code == 200
    items = r.json()["items"]
    match = [
        e for e in items if e.get("kind") == "insurance_pending"
        and (e.get("meta") or {}).get("order_id") == paid_order["id"]
    ]
    assert match, "insurance_pending email kaydi bulunamadi"


# 7) issue policy -> status issued, insurance_policy_sent email kaydi
def test_issue_policy(api, admin, paid_order):
    r = admin.get(f"{BASE_URL}/api/admin/insurance-tasks?status=pending")
    tasks = [t for t in r.json()["items"] if t.get("order_id") == paid_order["id"]]
    task = tasks[0]

    # upload minik pdf
    pdf_bytes = b"%PDF-1.4\n%TEST\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
    up_headers = {"Authorization": admin.headers["Authorization"]}
    up = requests.post(
        f"{BASE_URL}/api/uploads",
        files={"file": ("policy.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        data={"doc_type": "insurance_policy"},
        headers=up_headers,
    )
    assert up.status_code in (200, 201), f"upload failed: {up.status_code} {up.text}"
    file_id = up.json().get("file_id") or up.json().get("id")
    assert file_id, up.json()

    issue = admin.post(
        f"{BASE_URL}/api/admin/insurance-tasks/{task['id']}/issue",
        json={"policy_file_id": file_id, "origin_url": BASE_URL, "message": "TEST issue"},
    )
    assert issue.status_code == 200, issue.text
    body = issue.json()
    assert body["ok"] is True
    assert body["task"]["status"] == "issued"
    assert body["task"]["policy_file_id"] == file_id

    # email_outbox insurance_policy_sent kaydi
    time.sleep(0.3)
    r2 = admin.get(f"{BASE_URL}/api/admin/emails?limit=100")
    match = [
        e for e in r2.json()["items"] if e.get("kind") == "insurance_policy_sent"
        and (e.get("meta") or {}).get("task_id") == task["id"]
    ]
    assert match, "insurance_policy_sent email kaydi bulunamadi"


# 8) yalniz eSIM siparis -> hic task olusmamali
def test_esim_only_no_task(api, admin):
    payload = {
        "items": [{"product_id": "esim_3gb", "quantity": 1}],
        "contact": {
            "full_name": "TEST eSIM Only",
            "email": f"test.esim.{uuid.uuid4().hex[:6]}@example.com",
            "phone": "+905551112244",
        },
        "payment_method": "card",
    }
    r = api.post(f"{BASE_URL}/api/orders", json=payload)
    assert r.status_code == 200, r.text
    order = r.json()["order"]
    admin.patch(f"{BASE_URL}/api/admin/orders/{order['id']}", json={"payment_status": "paid"})
    time.sleep(0.3)
    r2 = admin.get(f"{BASE_URL}/api/admin/insurance-tasks")
    tasks = [t for t in r2.json()["items"] if t.get("order_id") == order["id"]]
    assert tasks == [], f"eSIM-only order should not create tasks: {tasks}"
