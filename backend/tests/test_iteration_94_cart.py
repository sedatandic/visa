"""Iteration 94: Shopping cart (sepet), FX, products, checkout tests."""
import os
import pytest
import requests

BASE = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE:
    # fall back to frontend .env parse
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE = line.split("=", 1)[1].strip().rstrip("/")

TEST_EMAIL = "delivered@resend.dev"
CREATED_ORDER_IDS = []


@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    # Cleanup created orders
    import asyncio
    from motor.motor_asyncio import AsyncIOMotorClient
    # conftest.py .env'i dotenv ile yukler (tirnaklar temizlenmis olarak)
    async def do():
        c = AsyncIOMotorClient(os.environ["MONGO_URL"])
        db = c[os.environ["DB_NAME"]]
        r = await db.store_orders.delete_many({
            "contact.email": TEST_EMAIL,
            "source": "store",
        })
        print(f"Cleanup: deleted {r.deleted_count} test orders")
    asyncio.get_event_loop().run_until_complete(do())


# -------------- FX + Products ---------------
def test_fx(s):
    r = s.get(f"{BASE}/api/fx")
    assert r.status_code == 200, r.text
    d = r.json()
    assert "effective_rate" in d
    assert d["effective_rate"] > 0
    assert "source" in d
    assert "fetched_at" in d
    print(f"FX: rate={d['effective_rate']} source={d.get('source')}")


def test_products(s):
    r = s.get(f"{BASE}/api/products")
    assert r.status_code == 200
    d = r.json()
    items = d["items"]
    ids = {i["id"] for i in items}
    for pid in ["esim_3gb", "ins_15d", "esim_1gb", "esim_unlimited"]:
        assert pid in ids, f"missing {pid}"
    for i in items:
        assert i["currency"] == "TRY"
        assert i["price"] > 0


# -------------- Orders ---------------
def _order_payload(items, ref=None, method="transfer", email=TEST_EMAIL):
    return {
        "items": items,
        "contact": {"full_name": "Test Cart User", "email": email, "phone": "+90 555 111 22 33"},
        "payment_method": method,
        "application_reference": ref,
    }


def test_order_with_bundle_discount(s):
    payload = _order_payload([
        {"product_id": "esim_3gb", "quantity": 2},
        {"product_id": "ins_15d", "quantity": 1},
    ])
    r = s.post(f"{BASE}/api/orders", json=payload)
    assert r.status_code == 200, r.text
    order = r.json()["order"]
    CREATED_ORDER_IDS.append(order["id"])
    assert order["source"] == "store"
    assert order["reference_code"].startswith("SV-")
    it = order["items_total"]
    disc = order["bundle_discount"]
    price = order["price"]
    assert disc == pytest.approx(round(it * 0.10, 2), abs=0.02), f"discount {disc} vs {it*0.1}"
    assert price == pytest.approx(round(it - disc, 2), abs=0.02)
    print(f"Bundle order: items_total={it} discount={disc} price={price} ref={order['reference_code']}")


def test_order_single_kind_no_discount(s):
    payload = _order_payload([{"product_id": "esim_3gb", "quantity": 2}])
    r = s.post(f"{BASE}/api/orders", json=payload)
    assert r.status_code == 200, r.text
    order = r.json()["order"]
    CREATED_ORDER_IDS.append(order["id"])
    assert order["bundle_discount"] == 0
    assert order["price"] == order["items_total"]


def test_order_invalid_app_reference(s):
    payload = _order_payload([{"product_id": "esim_3gb", "quantity": 1}], ref="DV-YOK123")
    r = s.post(f"{BASE}/api/orders", json=payload)
    assert r.status_code == 400
    msg = r.json().get("detail", "")
    assert "bulunamad" in msg.lower() or "bulun" in msg.lower(), f"got: {msg}"


def test_order_checkout_stripe(s):
    payload = _order_payload([{"product_id": "esim_3gb", "quantity": 1}], method="card")
    r = s.post(f"{BASE}/api/orders", json=payload)
    assert r.status_code == 200
    order = r.json()["order"]
    CREATED_ORDER_IDS.append(order["id"])
    rc = s.post(f"{BASE}/api/orders/{order['id']}/checkout", json={"origin_url": BASE})
    assert rc.status_code == 200, rc.text
    data = rc.json()
    url = data.get("checkout_url") or data.get("url")
    assert url and "stripe.com" in url, f"got: {data}"
    print(f"Stripe checkout URL: {url[:80]}...")
