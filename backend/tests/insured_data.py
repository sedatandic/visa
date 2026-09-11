"""Sigorta iceren siparis testleri icin sigortali verisi.

POST /api/orders artik sigorta satiri varsa her sigortali icin ad-soyad, gecerli
TC kimlik no ve dogum tarihi istiyor (saglayici police sarti).
"""


def make_tckn(seed: int) -> str:
    """Kontrol haneleri gecerli, tekrarlanabilir test TC kimlik numarasi uretir."""
    base = f"{100000000 + (seed * 7919) % 800000000:09d}"
    nums = [int(c) for c in base]
    tenth = ((sum(nums[0::2]) * 7) - sum(nums[1::2])) % 10
    eleventh = (sum(nums) + tenth) % 10
    return f"{base}{tenth}{eleventh}"


def insured_people(count: int = 1) -> list:
    return [
        {
            "full_name": f"TEST Sigortali {i + 1}",
            "tc_kimlik_no": make_tckn(i + 1),
            "birth_date": "1990-06-15",
        }
        for i in range(count)
    ]
