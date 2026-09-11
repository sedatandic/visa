"""Iteration 146: panelden girilen fiyatlar yeniden baslatmada korunur.

Hata (2026-06-18): `seed_products()` katalogdaki `price_try` / `cost_try` degerlerini her
sunucu acilisinda `$set` ile yaziyordu; boylece panelden girilen satis fiyati ve
saglayicidan gelen gercek maliyet sabit katalog degerine geri donuyordu. Tamamliyo fiyat
senkronu kaldirildigi icin fiyatlar artik tamamen panelden yonetiliyor, bu yuzden para
alanlari yalnizca ILK olusturmada yazilmali.
"""

import asyncio
import os
import sys

import pytest

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import server  # noqa: E402

MONEY_FIELDS = {"price_try", "cost_try", "price_usd"}


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture
def seeded(monkeypatch):
    calls = []

    class FakeProducts:
        async def update_one(self, query, update, upsert=False):
            calls.append({"id": query["id"], "update": update, "upsert": upsert})

    monkeypatch.setattr(server, "products_col", FakeProducts())
    run(server.seed_products())
    return calls


class TestSeedProducts:
    def test_money_fields_are_insert_only(self, seeded):
        for call in seeded:
            set_fields = set(call["update"]["$set"])
            assert not (set_fields & MONEY_FIELDS), f"{call['id']}: {set_fields & MONEY_FIELDS}"
            insert_fields = set(call["update"]["$setOnInsert"])
            assert MONEY_FIELDS <= insert_fields, call["id"]

    def test_catalog_copy_is_still_updated(self, seeded):
        """Isim/ozet gibi metinler katalogdan guncellenmeye devam eder."""
        insurance = [c for c in seeded if c["id"].startswith("ins_")]
        assert insurance, "sigorta urunleri seed edilmeli"
        for call in insurance:
            assert "name" in call["update"]["$set"]
            assert call["update"]["$set"]["provider"] == "sigortambudur"
            assert call["upsert"] is True

    def test_all_catalog_products_are_seeded(self, seeded):
        from store_catalog import DEFAULT_PRODUCTS

        assert len(seeded) == len(DEFAULT_PRODUCTS)
