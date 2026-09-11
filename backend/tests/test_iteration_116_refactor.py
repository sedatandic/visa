"""Iteration 116 refactor regression: insurance_delivery split, lifespan rewrite,
emailer/_sender_identity, digest sections, account documents.

Uses delivered@resend.dev (Resend rejects example.com). Valid TCKN 10000000146.
"""

import os
import sys
import time
from datetime import date, timedelta

import pytest
import requests


def _base_url() -> str:
    url = os.environ.get("REACT_APP_BACKEND_URL")
    if url:
        return url.rstrip("/")
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                return line.split("=", 1)[1].strip().rstrip("/")
    raise RuntimeError("no url")


BASE = _base_url()
API = f"{BASE}/api"
CUST_EMAIL = "delivered@resend.dev"
VALID_TCKN = "10000000146"


@pytest.fixture(scope="session")
def sess():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def admin_headers():
    sys.path.insert(0, "/app/backend")
    from admin_test_token import admin_token
    return {"Authorization": f"Bearer {admin_token()}"}


@pytest.fixture(scope="session")
def customer_token():
    sys.path.insert(0, "/app/backend")
    from routes_account import _create_session_token
    return _create_session_token(CUST_EMAIL)


def _insured_line(name="TEST_Sigortali Kisi"):
    return {
        "full_name": name,
        "tc_kimlik_no": VALID_TCKN,
        "birth_date": "1990-01-15",
    }


def _order_payload(with_insured=True, with_travel_start=True):
    travel_start = (date.today() + timedelta(days=10)).isoformat()
    travel_end = (date.today() + timedelta(days=17)).isoformat()
    p = {
        "items": [{"product_id": "ins_15d", "quantity": 1}],
        "contact": {
            "full_name": "TEST_Iter116 Customer",
            "email": CUST_EMAIL,
            "phone": "+905555550116",
        },
        "payment_method": "transfer",
        "note": "TEST_ iter116",
    }
    if with_travel_start:
        p["travel_start"] = travel_start
        p["travel_end"] = travel_end
    if with_insured:
        p["insured"] = [_insured_line()]
    return p


# ------------------------------------------------------- health + startup
class TestHealthLifespan:
    def test_health_ok(self, sess):
        r = sess.get(f"{API}/health", timeout=10)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_backend_log_no_nameerror(self):
        # Look for NameError/traceback in recent backend errors
        import glob
        for path in glob.glob("/var/log/supervisor/backend.err.log*"):
            try:
                with open(path, "rb") as f:
                    f.seek(0, 2)
                    size = f.tell()
                    f.seek(max(0, size - 200_000))
                    tail = f.read().decode("utf-8", errors="ignore")
            except OSError:
                continue
            assert "NameError" not in tail, f"NameError in {path}"

    def test_all_7_schedulers_started(self):
        # Check most recent backend log for 7 scheduler start lines
        import glob
        log = ""
        for path in sorted(glob.glob("/var/log/supervisor/backend.out.log*")) + sorted(
            glob.glob("/var/log/supervisor/backend.err.log*")
        ):
            try:
                with open(path, "rb") as f:
                    f.seek(0, 2)
                    size = f.tell()
                    f.seek(max(0, size - 300_000))
                    log += f.read().decode("utf-8", errors="ignore")
            except OSError:
                pass
        expected = [
            "document reminder scheduler started",
            "zami status + session keepalive scheduler started",
            "zami otp reminder scheduler started",
            "cart reminder scheduler started",
            "document retention scheduler started",
            "daily digest scheduler started",
            "insurance price sync scheduler started",
        ]
        missing = [m for m in expected if m not in log]
        assert not missing, f"missing scheduler lines: {missing}"


# ------------------------------------------------------- order flow
class TestInsuranceOrderFlow:
    def test_missing_insured_400(self, sess):
        r = sess.post(f"{API}/orders", json=_order_payload(with_insured=False), timeout=15)
        assert r.status_code == 400
        assert "TC" in r.text or "kimlik" in r.text.lower()

    def test_missing_travel_start_400(self, sess):
        r = sess.post(
            f"{API}/orders", json=_order_payload(with_travel_start=False), timeout=15
        )
        assert r.status_code == 400
        assert "gidiş" in r.text.lower() or "gidis" in r.text.lower() or "tarih" in r.text.lower()

    def test_valid_order_200(self, sess):
        r = sess.post(f"{API}/orders", json=_order_payload(), timeout=20)
        assert r.status_code == 200, r.text
        ref = r.json()["order"]["reference_code"]
        assert ref.startswith("SV-")
        pytest.iter116_order_ref = ref
        pytest.iter116_order_id = r.json()["order"]["id"]


# ------------------------------------------------------- manual issue
class TestManualIssuePolicy:
    def test_mark_paid_and_queue_task(self, sess, admin_headers):
        order_id = getattr(pytest, "iter116_order_id", None)
        if not order_id:
            pytest.skip("no order")
        r = sess.patch(
            f"{API}/admin/orders/{order_id}",
            json={"payment_status": "paid"},
            headers=admin_headers,
            timeout=15,
        )
        assert r.status_code == 200, r.text
        # Poll for task
        task_id = None
        for _ in range(10):
            time.sleep(0.6)
            tr = sess.get(f"{API}/admin/insurance-tasks", headers=admin_headers, timeout=15)
            assert tr.status_code == 200
            for t in tr.json()["items"]:
                if t.get("order_id") == order_id:
                    task_id = t["id"]
                    assert t["status"] == "pending"
                    break
            if task_id:
                break
        assert task_id, "insurance task did not appear after payment_status=paid"
        pytest.iter116_task_id = task_id

    def test_manual_issue_endpoint(self, sess, admin_headers):
        task_id = getattr(pytest, "iter116_task_id", None)
        if not task_id:
            pytest.skip("no task")
        r = sess.post(
            f"{API}/admin/insurance-tasks/{task_id}/issue",
            json={
                "policy_file_id": "test-policy-file",
                "origin_url": BASE,
                "message": "TEST_ regression manual issue",
            },
            headers=admin_headers,
            timeout=25,
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("ok") is True
        assert body["task"]["status"] == "issued"
        assert body["email"]["status"] in {"sent", "error", "skipped"}
        wa = body.get("whatsapp") or {}
        assert wa.get("status") == "manual"
        link = wa.get("link") or ""
        assert "wa.me" in link
        # link should contain order code SV- and PDF url
        assert "SV-" in link or "SV-" in wa.get("detail", "") or "SV-" in str(body["task"].get("order_reference", ""))
        assert "test-policy-file" in link or "test-policy-file" in body["task"].get("policy_file_id", "")


# ------------------------------------------------------- customer docs
@pytest.fixture(scope="class")
def seeded_policy_doc_id():
    """Kendi kendine yeten kesilmis police kaydi (siniflar arasi sira bagimliligini kaldirir)."""
    import uuid
    from datetime import datetime, timezone

    from dotenv import load_dotenv
    from pymongo import MongoClient

    load_dotenv("/app/backend/.env")
    client = MongoClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    db.insurance_tasks.insert_one(
        {
            "id": task_id,
            "order_reference": "SV-TESTI116",
            "status": "issued",
            "plan_name": "Seyahat Sağlık Sigortası · 7 Gün",
            "validity_days": 7,
            "quantity": 1,
            "starts_on": "2026-12-01",
            "ends_on": "2026-12-08",
            "customer": {"full_name": "TEST Iter116", "email": CUST_EMAIL, "phone": "+905551112233"},
            "insured": [
                {"full_name": "TEST ITER116", "tc_kimlik_no": VALID_TCKN, "birth_date": "1990-06-15"}
            ],
            "policy_file_id": "policy-test-file",
            "issued_at": now,
            "created_at": now,
        }
    )
    yield f"policy-{task_id}"
    db.insurance_tasks.delete_one({"id": task_id})
    client.close()


class TestAccountDocuments:
    def test_list_documents(self, sess, customer_token, seeded_policy_doc_id):
        h = {"Authorization": f"Bearer {customer_token}"}
        r = sess.get(f"{API}/account/documents", headers=h, timeout=15)
        assert r.status_code == 200, r.text
        items = r.json()["items"]
        policies = [it for it in items if it.get("kind") == "policy"]
        assert policies, "no policies found for delivered@resend.dev"
        assert any("/api/files/" in (p.get("download_url") or "") for p in policies)
        assert any(p["id"] == seeded_policy_doc_id for p in policies)

    def test_resend_document(self, sess, customer_token, seeded_policy_doc_id):
        h = {"Authorization": f"Bearer {customer_token}"}
        r = sess.post(
            f"{API}/account/documents/{seeded_policy_doc_id}/resend", headers=h, json={}, timeout=25
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("status") in {"sent", "error", "skipped"}

    def test_resend_invalid_404(self, sess, customer_token):
        h = {"Authorization": f"Bearer {customer_token}"}
        r = sess.post(
            f"{API}/account/documents/policy-does-not-exist/resend",
            headers=h,
            json={},
            timeout=15,
        )
        assert r.status_code == 404


# ------------------------------------------------------- provider panel (READ ONLY)
class TestProviderPanel:
    def test_provider_status(self, sess, admin_headers):
        r = sess.get(f"{API}/admin/insurance/provider", headers=admin_headers, timeout=15)
        assert r.status_code == 200, r.text
        body = r.json()
        # 2026-06-18: Tamamliyo iptal, aktif saglayici ayara bagli (sigortambudur / manual)
        assert body.get("provider") in {"sigortambudur", "tamamliyo", "manual"}
        assert isinstance(body.get("api_enabled"), bool)
        assert isinstance(body.get("price_sync"), bool)
        assert body.get("provider_label")
        assert isinstance(body.get("auto_issue"), bool)
        rows = body.get("products") or body.get("rows") or body.get("items") or []
        active_rows = [r for r in rows if r.get("active")]
        assert len(active_rows) == 4, f"expected 4 active products, got {len(active_rows)}"

    def test_sync_prices(self, sess, admin_headers):
        """Fiyat senkronu yalnizca Tamamliyo API'si acikken calisir; aksi halde atlanir."""
        r = sess.post(
            f"{API}/admin/insurance/sync-prices", headers=admin_headers, timeout=30
        )
        assert r.status_code == 200, r.text
        body = r.json()
        if body.get("skipped"):
            assert body.get("reason") == "provider_disabled"
            return
        rows = body.get("rows") or body.get("items") or body.get("products") or []
        assert len(rows) == 4
        errors = body.get("errors") or []
        assert errors == [] or errors == 0
        for row in rows:
            cost = row.get("cost") or row.get("cost_try")
            price = row.get("price") or row.get("price_try")
            assert cost and price
            expected = round(cost * 2 / 10) * 10
            assert price == expected, f"{row.get('product_id')}: price {price} != round(cost*2/10)*10 = {expected}"


# ------------------------------------------------------- daily digest
class TestDailyDigest:
    def test_digest_preview_and_html(self, sess, admin_headers):
        r = sess.get(f"{API}/admin/daily-digest/preview", headers=admin_headers, timeout=20)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "applications" in data or "revenue" in data or "month" in data
        # Render HTML directly via emailer.daily_digest_html to ensure all sections present
        sys.path.insert(0, "/app/backend")
        from emailer import daily_digest_html
        html = daily_digest_html(data)
        for heading in [
            "Dün gelen başvurular",
            "Tahsilat",
            "Ekstra satışlar",
            "Dikkat gerektirenler",
            "Ay başından bugüne",
        ]:
            assert heading in html, f"missing digest heading: {heading}"

    def test_admin_today(self, sess, admin_headers):
        r = sess.get(f"{API}/admin/today", headers=admin_headers, timeout=15)
        assert r.status_code == 200


# ------------------------------------------------------- sender identity
class TestSenderIdentity:
    def test_sender_identity_extracted(self):
        sys.path.insert(0, "/app/backend")
        from emailer import _sender_identity
        api_key, sender, reply_to = _sender_identity()
        # api_key may be None in tests; sender + reply_to must be strings
        assert isinstance(sender, str) and sender
        assert isinstance(reply_to, str)
