"""Iteration 95 - Safari Sepette + Cart Snapshot + Reminder logic.

Tests:
- /api/products?kind=tour returns 2 tours with schedule metadata
- /api/orders tour validation (missing date, invalid slot, happy path with preserved fields)
- /api/cart/snapshot upsert / deactivate / order-closes
- cart_reminders.due_stage() + run_cart_reminder_sweep() semantics
"""
import asyncio
import os
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
import requests
from motor.motor_asyncio import AsyncIOMotorClient

BASE = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE = line.split("=", 1)[1].strip().rstrip("/")

# read Mongo env
with open("/app/backend/.env") as f:
    ENV = {}
    for l in f:
        l = l.strip()
        if "=" in l and not l.startswith("#"):
            k, v = l.split("=", 1)
            ENV[k] = v.strip().strip('"')

TEST_EMAIL = f"delivered+it95_{uuid.uuid4().hex[:6]}@resend.dev"
CREATED_ORDER_REFS: list[str] = []


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _db():
    c = AsyncIOMotorClient(ENV["MONGO_URL"])
    return c, c[ENV["DB_NAME"]]


@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield

    async def do():
        c, db = _db()
        r1 = await db.store_orders.delete_many(
            {"contact.email": {"$regex": "^delivered\\+it95_"}, "source": "store"}
        )
        r2 = await db.cart_snapshots.delete_many(
            {"email": {"$regex": "^delivered\\+it95_"}}
        )
        print(f"Cleanup: orders={r1.deleted_count} snapshots={r2.deleted_count}")
        c.close()

    _run(do())


# ---------- /api/products?kind=tour ----------
def test_products_tour_kind(s):
    r = s.get(f"{BASE}/api/products?kind=tour")
    assert r.status_code == 200, r.text
    items = r.json()["items"]
    ids = {i["id"] for i in items}
    assert {"tour_desert_safari", "tour_desert_safari_vip"}.issubset(ids)
    for it in items:
        if it["id"].startswith("tour_"):
            assert it.get("needs_schedule") is True
            assert it.get("time_slots") == ["14:00", "14:30", "15:00", "15:30", "16:00"]
            assert it["currency"] == "TRY"
            assert it["price"] > 0
            assert it.get("image_url", "").startswith("http")


# ---------- Tour order validation ----------
def _tour_payload(items, email=None):
    return {
        "items": items,
        "contact": {
            "full_name": "Iter95 Tester",
            "email": email or TEST_EMAIL,
            "phone": "+90 555 000 11 22",
        },
        "payment_method": "transfer",
    }


def test_tour_order_missing_date(s):
    r = s.post(
        f"{BASE}/api/orders",
        json=_tour_payload([{"product_id": "tour_desert_safari", "quantity": 1}]),
    )
    assert r.status_code == 400
    msg = r.json().get("detail", "")
    assert "tur tarihi" in msg.lower(), msg


def test_tour_order_invalid_slot(s):
    r = s.post(
        f"{BASE}/api/orders",
        json=_tour_payload(
            [
                {
                    "product_id": "tour_desert_safari",
                    "quantity": 1,
                    "scheduled_date": (date.today() + timedelta(days=20)).isoformat(),
                    "scheduled_time": "09:00",
                }
            ]
        ),
    )
    assert r.status_code == 400
    msg = r.json().get("detail", "").lower()
    assert "saat" in msg, msg


def test_tour_order_happy_path(s):
    future = (date.today() + timedelta(days=25)).isoformat()
    r = s.post(
        f"{BASE}/api/orders",
        json=_tour_payload(
            [
                {
                    "product_id": "tour_desert_safari",
                    "quantity": 2,
                    "scheduled_date": future,
                    "scheduled_time": "14:30",
                }
            ]
        ),
    )
    assert r.status_code == 200, r.text
    order = r.json()["order"]
    CREATED_ORDER_REFS.append(order["reference_code"])
    line = order["items"][0]
    assert line["scheduled_date"] == future
    assert line["scheduled_time"] == "14:30"
    assert line["kind"] == "tour"


# ---------- /api/cart/snapshot ----------
def test_snapshot_upsert_and_bundle_discount(s):
    r = s.post(
        f"{BASE}/api/cart/snapshot",
        json={
            "email": TEST_EMAIL,
            "full_name": "Snap Tester",
            "items": [
                {"product_id": "esim_3gb", "quantity": 1},
                {"product_id": "ins_15d", "quantity": 1},
            ],
        },
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["saved"] is True
    assert d.get("price", 0) > 0

    async def check():
        c, db = _db()
        snap = await db.cart_snapshots.find_one({"email": TEST_EMAIL.lower()})
        c.close()
        return snap

    snap = _run(check())
    assert snap is not None
    assert snap["active"] is True
    assert snap["reminders_sent"] == 0
    it = snap["items_total"]
    bd = snap["bundle_discount"]
    assert bd == pytest.approx(round(it * 0.10, 2), abs=0.02)
    assert snap["price"] == pytest.approx(round(it - bd, 2), abs=0.02)


def test_snapshot_empty_deactivates(s):
    email = f"delivered+it95_empty_{uuid.uuid4().hex[:6]}@resend.dev"
    # first create with items
    s.post(
        f"{BASE}/api/cart/snapshot",
        json={"email": email, "items": [{"product_id": "esim_3gb", "quantity": 1}]},
    )
    # then empty
    r = s.post(f"{BASE}/api/cart/snapshot", json={"email": email, "items": []})
    assert r.status_code == 200
    d = r.json()
    assert d["saved"] is False
    assert d["active"] is False

    async def check():
        c, db = _db()
        snap = await db.cart_snapshots.find_one({"email": email.lower()})
        c.close()
        return snap

    snap = _run(check())
    assert snap["active"] is False


def test_order_deactivates_snapshot(s):
    email = f"delivered+it95_ord_{uuid.uuid4().hex[:6]}@resend.dev"
    # snapshot first
    s.post(
        f"{BASE}/api/cart/snapshot",
        json={"email": email, "items": [{"product_id": "esim_3gb", "quantity": 1}]},
    )
    # place order with same email
    r = s.post(
        f"{BASE}/api/orders",
        json=_tour_payload(
            [{"product_id": "esim_3gb", "quantity": 1}], email=email
        ),
    )
    assert r.status_code == 200, r.text

    async def check():
        c, db = _db()
        snap = await db.cart_snapshots.find_one({"email": email.lower()})
        c.close()
        return snap

    snap = _run(check())
    assert snap is not None
    assert snap["active"] is False
    assert snap.get("closed_reason") == "ordered"


# ---------- cart_reminders module ----------
def test_due_stage_and_sweep():
    import sys

    sys.path.insert(0, "/app/backend")
    from cart_reminders import due_stage, run_cart_reminder_sweep

    now = datetime.now(timezone.utc)

    # not active
    assert due_stage({"active": False, "items": [{}], "updated_at": now - timedelta(hours=5)}, now) is None
    # active but too fresh
    assert due_stage({"active": True, "items": [{}], "updated_at": now - timedelta(minutes=30), "reminders_sent": 0}, now) is None
    # >2h, 0 sent -> stage 1
    assert due_stage({"active": True, "items": [{}], "updated_at": now - timedelta(hours=3), "reminders_sent": 0}, now) == 1
    # >24h, 1 sent -> stage 2
    assert due_stage({"active": True, "items": [{}], "updated_at": now - timedelta(hours=25), "reminders_sent": 1}, now) == 2
    # 2 already sent -> None
    assert due_stage({"active": True, "items": [{}], "updated_at": now - timedelta(hours=48), "reminders_sent": 2}, now) is None

    # sweep with a seeded snapshot
    email = f"delivered+it95_sweep_{uuid.uuid4().hex[:6]}@resend.dev"

    async def seed_and_sweep():
        c, db = _db()
        stale = datetime.now(timezone.utc) - timedelta(hours=3)
        await db.cart_snapshots.update_one(
            {"email": email},
            {
                "$set": {
                    "email": email,
                    "items": [{"product_id": "esim_3gb", "quantity": 1, "name": "test", "unit_price": 100, "total": 100}],
                    "items_total": 100,
                    "bundle_discount": 0,
                    "price": 100,
                    "currency": "TRY",
                    "active": True,
                    "updated_at": stale,
                    "created_at": stale,
                    "reminders_sent": 0,
                }
            },
            upsert=True,
        )
        result = await run_cart_reminder_sweep("https://example.com")
        snap = await db.cart_snapshots.find_one({"email": email})
        # cleanup
        await db.cart_snapshots.delete_one({"email": email})
        await db.email_outbox.delete_many({"meta.email": email})
        c.close()
        return result, snap

    result, snap = _run(seed_and_sweep())
    print(f"Sweep result: {result}")
    # Either sent (real send attempted) or skipped due to error - but reminders_sent counter must be incremented on send path.
    # Since send_email always inserts an outbox row (even if delivery errors), incrementing should happen.
    assert result["sent"] + result["skipped"] >= 1
    if result["sent"] >= 1:
        assert snap["reminders_sent"] == 1
