"""Backend validation rule tests for /api/applications (iteration 65)."""
import os
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://whatsapp-ai-test.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


def _contact():
    return {
        "full_name": "TEST Kullanici",
        "email": "test_rules@example.com",
        "phone": "+905551112233",
        "address_city": "Istanbul",
        "whatsapp_optin": False,
    }


def _traveler(**overrides):
    base = {
        "first_name": "Ali",
        "last_name": "Yilmaz",
        "birth_date": "1990-05-10",
        "gender": "male",
        "applicant_type": "adult",
        "nationality": "TR",
        "passport_no": "U12345678",
        "passport_expiry": "2030-12-31",
        "marital_status": "single",
        "profession": "Employee",
        "mother_name": "Ayse",
        "father_name": "Mehmet",
        "visa_type_id": "visa_30_single",
        "passport_file_id": "fake-passport-file-id",
        "photo_file_id": "fake-photo-file-id",
    }
    base.update(overrides)
    return base


def _travel(arrival="2026-12-01", departure="2026-12-10"):
    return {
        "arrival_date": arrival,
        "departure_date": departure,
        "purpose": "tourism",
        "birth_country": "TR",
        "accommodation": "Hotel X",
        "flight_no": "TK123",
    }


def _payload(travelers, travel):
    return {
        "contact": _contact(),
        "travelers": travelers,
        "travel": travel,
        "addons": {"express": False, "insurance": False, "insurance_plus": False, "esim": False},
        "store_items": [],
        "extra_documents": {"ticket_file_id": None, "hotel_file_id": None, "other_file_ids": []},
        "kvkk_accepted": True,
    }


def _post(payload):
    return requests.post(f"{API}/applications", json=payload, timeout=15)


# Rule 1: Passport must be valid 6 months (180 days) past return
class TestPassport6MonthRule:
    def test_expiry_less_than_6_months_after_return_rejected(self):
        # departure 2026-12-10, expiry 2027-01-01 => ~22 days < 180
        t = _traveler(passport_expiry="2027-01-01")
        r = _post(_payload([t], _travel()))
        assert r.status_code == 400, r.text
        assert "6 ay" in r.text.lower() or "6 ay gecerli" in r.text

    def test_expiry_well_beyond_6_months_passes_rule(self):
        # This will pass rule but fail on uploads (400) - message must NOT be about 6 ay
        t = _traveler(passport_expiry="2030-12-31")
        r = _post(_payload([t], _travel()))
        # Uploads don't exist -> expect 400 upload error, not 6-month
        assert r.status_code == 400
        assert "6 ay" not in r.text.lower()


# Rule 2: Minor alone rejected
class TestMinorAlone:
    def test_single_child_alone_rejected(self):
        t = _traveler(
            first_name="Kucuk",
            birth_date="2015-05-10",
            applicant_type="child",
            visa_type_id="visa_30_child",
        )
        r = _post(_payload([t], _travel()))
        assert r.status_code == 400, r.text
        assert "yetiskin" in r.text.lower()

    def test_child_with_adult_passes_rule(self):
        adult = _traveler()
        child = _traveler(
            first_name="Kucuk",
            last_name="Yilmaz",
            birth_date="2015-05-10",
            applicant_type="child",
            visa_type_id="visa_30_child",
            passport_no="C11111111",
        )
        r = _post(_payload([adult, child], _travel()))
        assert r.status_code == 400
        assert "yetiskin" not in r.text.lower()


# Rule 3: Child visa restricted to <18
class TestChildVisaAge:
    def test_adult_with_child_visa_rejected(self):
        t = _traveler(applicant_type="child", visa_type_id="visa_30_child", birth_date="1990-05-10")
        r = _post(_payload([t], _travel()))
        assert r.status_code == 400, r.text
        assert "cocuk vizesi" in r.text.lower() or "18 yas" in r.text.lower()


# Rule 4: Stay must fit visa duration
class TestStayVsVisaDuration:
    def test_30day_visa_with_46_day_stay_rejected(self):
        t = _traveler(visa_type_id="visa_30_single")
        r = _post(_payload([t], _travel("2026-12-01", "2027-01-15")))  # 46 days
        assert r.status_code == 400, r.text
        assert "kalis" in r.text.lower() or "vize" in r.text.lower()

    def test_transit48_with_5_day_stay_rejected(self):
        t = _traveler(visa_type_id="visa_transit_48")
        r = _post(_payload([t], _travel("2026-12-01", "2026-12-05")))
        assert r.status_code == 400, r.text
        assert "kalis" in r.text.lower()

    def test_9_day_stay_on_30_day_visa_passes_rule(self):
        t = _traveler(visa_type_id="visa_30_single")
        r = _post(_payload([t], _travel("2026-12-01", "2026-12-09")))
        assert r.status_code == 400
        # Not the stay/duration error
        assert "planlanan kalis" not in r.text.lower()


# Rule 5: Past arrival rejected
class TestPastArrival:
    def test_past_arrival_rejected(self):
        t = _traveler()
        r = _post(_payload([t], _travel("2020-01-01", "2020-01-05")))
        assert r.status_code == 400, r.text
        assert "bugunden once" in r.text.lower() or "gidis tarihi" in r.text.lower()
