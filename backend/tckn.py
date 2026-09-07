"""TC Kimlik No dogrulamasi (format + kontrol hanesi)."""


def valid_tckn(value: str) -> bool:
    """11 haneli TC kimlik numarasinin kontrol hanelerini dogrular."""
    digits = (value or "").strip()
    if len(digits) != 11 or not digits.isdigit() or digits[0] == "0":
        return False
    nums = [int(c) for c in digits]
    tenth = ((sum(nums[0:9:2]) * 7) - sum(nums[1:8:2])) % 10
    eleventh = sum(nums[:10]) % 10
    return nums[9] == tenth and nums[10] == eleventh


def clean_tckn(value: str) -> str:
    return "".join(c for c in (value or "") if c.isdigit())[:11]
