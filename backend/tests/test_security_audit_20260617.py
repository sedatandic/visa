"""Guvenlik denetimi duzeltmeleri: sahte X-Forwarded-For ve gunluk AI kotasi."""

import asyncio
import os

import pytest
from fastapi import HTTPException

import rate_limit
import usage_quota


class DummyClient:
    def __init__(self, host):
        self.host = host


class DummyRequest:
    def __init__(self, xff=None, peer="10.0.0.1"):
        self.headers = {"x-forwarded-for": xff} if xff else {}
        self.client = DummyClient(peer)


class TestClientIpSpoofing:
    def test_real_client_used_when_no_spoof(self):
        # zincir: istemci, cloudflare, ingress
        req = DummyRequest("34.7.135.173,104.23.168.48,136.110.146.181")
        assert rate_limit.client_ip(req) == "34.7.135.173"

    def test_prepended_fake_hops_are_ignored(self):
        req = DummyRequest("1.2.3.4,34.7.135.173,172.71.98.2,136.110.146.181")
        assert rate_limit.client_ip(req) == "34.7.135.173"

    def test_many_fake_hops_still_resolve_real_client(self):
        req = DummyRequest("a,b,c,d,34.7.135.173,104.23.168.48,136.110.146.181")
        assert rate_limit.client_ip(req) == "34.7.135.173"

    def test_falls_back_to_peer_without_header(self):
        assert rate_limit.client_ip(DummyRequest(peer="10.9.9.9")) == "10.9.9.9"

    def test_rate_limit_not_bypassed_by_rotating_fake_prefix(self):
        base = "203.0.113.7,104.23.1.1,136.110.146.181"
        keys = {
            rate_limit.client_ip(DummyRequest(f"{fake},{base}")) for fake in ("9.9.9.9", "8.8.8.8", "7.7.7.7")
        }
        assert keys == {"203.0.113.7"}, "sahte onek her istekte yeni kimlik uretmemeli"


class TestDailyQuota:
    def test_limit_from_env(self, monkeypatch):
        monkeypatch.setenv("PASSPORT_OCR_DAILY_LIMIT", "12")
        assert usage_quota.daily_limit("passport_ocr") == 12
        monkeypatch.delenv("PASSPORT_OCR_DAILY_LIMIT")
        assert usage_quota.daily_limit("passport_ocr") == usage_quota.DEFAULT_LIMITS["passport_ocr"]

    def test_quota_blocks_after_limit(self, monkeypatch):
        counters = {}

        class FakeCollection:
            async def find_one_and_update(self, flt, update, upsert=False, return_document=None):
                key = flt["_id"]
                counters[key] = counters.get(key, 0) + update["$inc"]["count"]
                return {"_id": key, "count": counters[key]}

        monkeypatch.setattr(usage_quota, "db", type("FakeDb", (), {"usage_counters": FakeCollection()})())
        monkeypatch.setenv("PASSPORT_OCR_DAILY_LIMIT", "2")
        asyncio.run(usage_quota.consume_daily("passport_ocr", "limit"))
        asyncio.run(usage_quota.consume_daily("passport_ocr", "limit"))
        with pytest.raises(HTTPException) as exc:
            asyncio.run(usage_quota.consume_daily("passport_ocr", "limit"))
        assert exc.value.status_code == 429

    def test_zero_limit_disables_quota(self, monkeypatch):
        monkeypatch.setenv("PHOTO_CHECK_DAILY_LIMIT", "0")
        asyncio.run(usage_quota.consume_daily("photo_check", "limit"))  # sayaca dokunmaz


class TestCorsRegex:
    def test_platform_wildcard_removed(self):
        source = open(os.path.join(os.path.dirname(__file__), "..", "server.py"), encoding="utf-8").read()
        assert "emergentagent\\.com" not in source, "platform genelinde wildcard CORS olmamali"
        assert "emergent\\.host" not in source
