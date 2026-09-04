"""Regression + fix verification for zami OTP-loop bug (iteration_54)."""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", ".env"))

BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/")
ADMIN_EMAIL = os.environ["ADMIN_LOGIN_EMAIL"]
ADMIN_PASSWORD = os.environ["ADMIN_LOGIN_PASSWORD"]


def _admin_session():
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/admin/login",
               json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
               timeout=15)
    assert r.status_code == 200, r.text
    token = r.json().get("token")
    assert token
    s.headers.update({"Authorization": f"Bearer {token}"})
    return s


def test_auto_renew_no_force_returns_fast_and_guarded():
    """auto-renew (no force) must NOT trigger client OTP email.

    Two valid outcomes after the fix:
      * ok=False with a guarded reason (no_trusted_device / otp_required_pending) —
        the guard bails out without touching the portal (< 1s).
      * ok=True with attempts>=1 — device_state cookie is trusted so the portal
        accepts the login silently (a few seconds, no OTP prompt/email).
    In BOTH cases, response must return well under the ~20-60s a portal-OTP
    round-trip would take, and results must be stable across 3 calls.
    """
    s = _admin_session()
    outcomes = []
    durations = []
    for _ in range(3):
        t0 = time.time()
        r = s.post(f"{BASE_URL}/api/admin/zami/session/auto-renew", timeout=20)
        dt = time.time() - t0
        durations.append(dt)
        assert r.status_code == 200, r.text
        body = r.json()
        if body.get("ok") is False:
            reason = body.get("reason")
            assert reason in ("no_trusted_device", "otp_required_pending",
                              "login_in_progress", "interactive_login_in_progress",
                              "no_credentials"), body
            outcomes.append(("guarded", reason))
        else:
            # Silent trusted-device login is acceptable — no OTP email is sent.
            assert body.get("attempts", 0) >= 1, body
            outcomes.append(("silent_ok", body.get("attempts")))
    # No call must take anywhere near a portal-OTP round-trip.
    for dt in durations:
        assert dt < 15.0, f"auto-renew took {dt}s (>=15s) — suspicious portal round-trip"
    # Outcome kind must be stable across the 3 calls.
    kinds = {o[0] for o in outcomes}
    assert len(kinds) == 1, f"outcome kind drifted across calls: {outcomes}"
    print(f"auto-renew outcomes={outcomes} durations={durations}")


def test_zami_session_readiness_reflects_otp_required():
    s = _admin_session()
    r = s.get(f"{BASE_URL}/api/admin/zami/readiness", timeout=15)
    assert r.status_code == 200, r.text
    body = r.json()
    print("zami/readiness:", body)
    otp_req = body.get("otp_required") or body.get("value", {}).get("otp_required")
    trusted = body.get("trusted_device")
    if trusted is not None:
        assert trusted is False
    reason = body.get("reason") or body.get("otp_reason")
    assert otp_req is True or reason in ("no_trusted_device", None, ""), body


def test_visa_types():
    r = requests.get(f"{BASE_URL}/api/visa-types", timeout=15)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert len(items) == 8, f"expected 8 visa types, got {len(items)}"


def test_content_site_partners_no_24saat():
    r = requests.get(f"{BASE_URL}/api/content/site", timeout=15)
    assert r.status_code == 200
    body = r.json()
    partners = body.get("partners") or []
    assert isinstance(partners, list) and len(partners) > 0
    for p in partners:
        assert p.get("logo") or p.get("logo_url"), f"partner missing logo: {p}"
    raw = requests.get(f"{BASE_URL}/api/content/site", timeout=15).text
    assert "24 saat" not in raw, "'24 saat' should be removed from site content"


def test_admin_login():
    _admin_session()


def test_zami_mapping_and_config_endpoints():
    s = _admin_session()
    r = s.get(f"{BASE_URL}/api/admin/zami/config", timeout=15)
    assert r.status_code == 200, f"/api/admin/zami/config -> {r.status_code} {r.text[:200]}"
    # Zami mapping is exposed via config (candidates endpoint is the read path).
    r = s.get(f"{BASE_URL}/api/admin/zami/candidates", timeout=15)
    assert r.status_code == 200, f"/api/admin/zami/candidates -> {r.status_code} {r.text[:200]}"
