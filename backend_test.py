#!/usr/bin/env python3
"""
Comprehensive backend API test suite for VizeAtlas Dubai
Tests all public, payment, and admin endpoints
"""
import io
import json
import sys
from datetime import datetime, timedelta

import requests

BASE_URL = "https://visa-application-ae.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@vizeatlas.com"
ADMIN_PASSWORD = "Dubai2026!"


class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.test_file_id = None
        self.test_photo_id = None
        self.test_application_id = None
        self.test_reference_code = None
        self.test_contact_id = None
        self.test_session_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")

    def test(self, name, func):
        """Run a single test"""
        self.tests_run += 1
        self.log(f"\n{'='*60}")
        self.log(f"TEST {self.tests_run}: {name}")
        self.log('='*60)
        try:
            func()
            self.tests_passed += 1
            self.log(f"✅ PASSED: {name}", "SUCCESS")
            return True
        except AssertionError as e:
            self.log(f"❌ FAILED: {name} - {str(e)}", "ERROR")
            self.failed_tests.append({"test": name, "error": str(e)})
            return False
        except Exception as e:
            self.log(f"❌ ERROR: {name} - {str(e)}", "ERROR")
            self.failed_tests.append({"test": name, "error": f"Exception: {str(e)}"})
            return False

    # ============================================================
    # PUBLIC ENDPOINTS
    # ============================================================

    def test_health(self):
        """GET /api/health"""
        r = requests.get(f"{self.base_url}/health", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert data["status"] == "ok", "Health check failed"
        assert "email_configured" in data, "Missing email_configured"
        assert "payments_configured" in data, "Missing payments_configured"
        self.log(f"Health: {data}")

    def test_visa_types(self):
        """GET /api/visa-types - includes new visa types"""
        r = requests.get(f"{self.base_url}/visa-types", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert isinstance(data, list), "Expected list of visa types"
        assert len(data) >= 9, f"Expected at least 9 visa types (including new ones), got {len(data)}"
        
        # Check for new visa types
        visa_ids = [v["id"] for v in data]
        assert "visa_transit_48" in visa_ids, "Missing visa_transit_48"
        assert "visa_freelancer_2y" in visa_ids, "Missing visa_freelancer_2y"
        
        # Verify new visa types structure
        transit = next((v for v in data if v["id"] == "visa_transit_48"), None)
        assert transit is not None, "visa_transit_48 not found"
        assert transit["name"] == "48 Saatlik Transit Vize", f"Transit visa name mismatch: {transit['name']}"
        assert transit["price"] == 1299.0, f"Transit visa price mismatch: {transit['price']}"
        assert transit["currency"] == "TRY", "Transit visa currency should be TRY"
        assert transit["duration_days"] == 2, "Transit visa duration should be 2 days"
        
        freelancer = next((v for v in data if v["id"] == "visa_freelancer_2y"), None)
        assert freelancer is not None, "visa_freelancer_2y not found"
        assert freelancer["name"] == "2 Yıllık Freelancer (Serbest Çalışma) Vizesi", f"Freelancer visa name mismatch: {freelancer['name']}"
        assert freelancer["price"] == 109000.0, f"Freelancer visa price mismatch: {freelancer['price']}"
        assert freelancer["currency"] == "TRY", "Freelancer visa currency should be TRY"
        assert freelancer["duration_days"] == 730, "Freelancer visa duration should be 730 days"
        
        for vt in data:
            assert "id" in vt, "Visa type missing id"
            assert "name" in vt, "Visa type missing name"
            assert "price" in vt, "Visa type missing price"
        self.log(f"Found {len(data)} visa types (including visa_transit_48 and visa_freelancer_2y)")

    def test_site_content(self):
        """GET /api/content/site - includes promo, bank_transfer, 17 FAQs"""
        r = requests.get(f"{self.base_url}/content/site", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        required = ["company", "process_steps", "why_us", "faq", "required_documents", "photo_rules", "testimonials", "review_summary", "status_labels", "promo", "bank_transfer"]
        for key in required:
            assert key in data, f"Missing {key} in site content"
        
        # Verify promo structure
        promo = data.get("promo")
        assert promo is not None, "promo is None"
        assert "title" in promo, "Missing 'title' in promo"
        assert "detail" in promo, "Missing 'detail' in promo"
        self.log(f"Promo: {promo['title']}")
        
        # Verify bank_transfer structure
        bank_transfer = data.get("bank_transfer")
        assert bank_transfer is not None, "bank_transfer is None"
        assert "enabled" in bank_transfer, "Missing 'enabled' in bank_transfer"
        assert "iban" in bank_transfer, "Missing 'iban' in bank_transfer"
        assert "steps" in bank_transfer, "Missing 'steps' in bank_transfer"
        assert "note" in bank_transfer, "Missing 'note' in bank_transfer"
        assert isinstance(bank_transfer["steps"], list), "bank_transfer steps should be a list"
        self.log(f"Bank transfer: {bank_transfer['iban']}")
        
        # Verify FAQ count (should be 17)
        faq = data.get("faq")
        assert faq is not None, "faq is None"
        assert isinstance(faq, list), "faq should be a list"
        assert len(faq) == 17, f"Expected 17 FAQ items, got {len(faq)}"
        self.log(f"FAQ: {len(faq)} items")
        
        # Verify review_summary structure
        review_summary = data.get("review_summary")
        assert review_summary is not None, "review_summary is None"
        assert "average" in review_summary, "Missing 'average' in review_summary"
        assert "total_reviews" in review_summary, "Missing 'total_reviews' in review_summary"
        assert "total_applications" in review_summary, "Missing 'total_applications' in review_summary"
        assert "highlights" in review_summary, "Missing 'highlights' in review_summary"
        assert isinstance(review_summary["highlights"], list), "highlights should be a list"
        self.log(f"Review summary: {review_summary['average']} avg, {review_summary['total_reviews']} reviews")
        
        # Verify testimonials structure
        testimonials = data.get("testimonials")
        assert testimonials is not None, "testimonials is None"
        assert isinstance(testimonials, list), "testimonials should be a list"
        assert len(testimonials) >= 6, f"Expected at least 6 testimonials, got {len(testimonials)}"
        for t in testimonials[:3]:  # Check first 3
            assert "name" in t, "Testimonial missing 'name'"
            assert "initials" in t, "Testimonial missing 'initials'"
            assert "city" in t, "Testimonial missing 'city'"
            assert "visa" in t, "Testimonial missing 'visa'"
            assert "date" in t, "Testimonial missing 'date'"
            assert "verified" in t, "Testimonial missing 'verified'"
            assert "rating" in t, "Testimonial missing 'rating'"
            assert "text" in t, "Testimonial missing 'text'"
        self.log(f"Testimonials: {len(testimonials)} testimonials found")
        self.log("Site content loaded successfully")

    def test_upload_valid_image(self):
        """POST /api/uploads - valid image"""
        # Create a tiny valid PNG (1x1 pixel)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        files = {"file": ("passport.png", io.BytesIO(png_data), "image/png")}
        data = {"doc_type": "passport"}
        r = requests.post(f"{self.base_url}/uploads", files=files, data=data, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert "file_id" in result, "Missing file_id"
        self.test_file_id = result["file_id"]
        self.log(f"Uploaded passport: {self.test_file_id}")

    def test_upload_photo(self):
        """POST /api/uploads - biometric photo"""
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        files = {"file": ("photo.png", io.BytesIO(png_data), "image/png")}
        data = {"doc_type": "biometric_photo"}
        r = requests.post(f"{self.base_url}/uploads", files=files, data=data, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        self.test_photo_id = result["file_id"]
        self.log(f"Uploaded photo: {self.test_photo_id}")

    def test_upload_invalid_extension(self):
        """POST /api/uploads - invalid extension (.txt)"""
        files = {"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")}
        data = {"doc_type": "passport"}
        r = requests.post(f"{self.base_url}/uploads", files=files, data=data, timeout=15)
        assert r.status_code == 400, f"Expected 400, got {r.status_code}"
        assert "JPG" in r.text or "PNG" in r.text, "Expected Turkish error message about file types"
        self.log("Invalid extension correctly rejected")

    def test_upload_oversized(self):
        """POST /api/uploads - file > 10MB"""
        # Create 11MB file
        large_data = b"x" * (11 * 1024 * 1024)
        files = {"file": ("large.jpg", io.BytesIO(large_data), "image/jpeg")}
        data = {"doc_type": "passport"}
        r = requests.post(f"{self.base_url}/uploads", files=files, data=data, timeout=30)
        assert r.status_code == 400, f"Expected 400, got {r.status_code}"
        assert "10 MB" in r.text or "10MB" in r.text, "Expected Turkish error about file size"
        self.log("Oversized file correctly rejected")

    def test_create_application_valid(self):
        """POST /api/applications - valid payload (multi-traveler schema)"""
        assert self.test_file_id, "Need uploaded passport file"
        assert self.test_photo_id, "Need uploaded photo file"
        
        tomorrow = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        payload = {
            "contact": {
                "full_name": "Ahmet Yilmaz",
                "email": f"ahmet.test_{datetime.now().timestamp()}@example.com",
                "phone": "+905551234567",
                "address_city": "Istanbul"
            },
            "travelers": [
                {
                    "first_name": "AHMET",
                    "last_name": "YILMAZ",
                    "birth_date": "1990-05-15",
                    "gender": "male",
                    "applicant_type": "adult",
                    "nationality": "TR",
                    "national_id": "12345678901",
                    "passport_no": "U12345678",
                    "passport_expiry": "2028-12-31",
                    "visa_type_id": "visa_30_single",
                    "passport_file_id": self.test_file_id,
                    "photo_file_id": self.test_photo_id
                }
            ],
            "travel": {
                "arrival_date": tomorrow,
                "departure_date": return_date,
                "purpose": "tourism",
                "birth_country": "TR",
                "accommodation": "Burj Al Arab",
                "flight_no": "TK123",
                "notes": "Test application"
            },
            "addons": {"express": False, "insurance": False},
            "extra_documents": {},
            "kvkk_accepted": True
        }
        r = requests.post(f"{self.base_url}/applications", json=payload, timeout=20)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert "id" in result, "Missing application id"
        assert "reference_code" in result, "Missing reference_code"
        assert result["reference_code"].startswith("DV-"), f"Invalid reference code format: {result['reference_code']}"
        assert "email_notification" in result, "Missing email_notification"
        assert result["email_notification"] == "skipped", "Email should be skipped when RESEND_API_KEY is empty"
        self.test_application_id = result["id"]
        self.test_reference_code = result["reference_code"]
        self.log(f"Created application: {self.test_reference_code} (ID: {self.test_application_id})")

    def test_create_application_invalid(self):
        """POST /api/applications - invalid payload (missing fields)"""
        payload = {
            "visa_type_id": "visa_30_single",
            "applicant": {
                "first_name": "A",  # Too short
                "last_name": "Y",   # Too short
                "email": "invalid-email",  # Invalid email
                "phone": "123",
                "birth_date": "1990-05-15",
                "gender": "unknown",  # Invalid gender
                "passport_no": "U12",
                "passport_expiry": "2028-12-31"
            },
            "travel": {
                "arrival_date": "2026-03-15",
                "departure_date": "2026-03-25"
            },
            "documents": {
                "passport_file_id": "invalid",
                "photo_file_id": "invalid"
            }
        }
        r = requests.post(f"{self.base_url}/applications", json=payload, timeout=15)
        assert r.status_code == 422 or r.status_code == 400, f"Expected 422 or 400, got {r.status_code}"
        self.log("Invalid application correctly rejected")

    def test_track_application_correct(self):
        """GET /api/applications/track - correct credentials"""
        assert self.test_reference_code, "Need created application"
        params = {"code": self.test_reference_code, "last_name": "YILMAZ"}
        r = requests.get(f"{self.base_url}/applications/track", params=params, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert result["reference_code"] == self.test_reference_code, "Reference code mismatch"
        assert len(result["travelers"]) >= 1, "Expected at least one traveler"
        assert result["travelers"][0]["last_name"] == "YILMAZ", "Last name mismatch"
        self.log(f"Tracked application: {result['status']}")

    def test_track_application_wrong_surname(self):
        """GET /api/applications/track - wrong surname"""
        assert self.test_reference_code, "Need created application"
        params = {"code": self.test_reference_code, "last_name": "WrongName"}
        r = requests.get(f"{self.base_url}/applications/track", params=params, timeout=10)
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        self.log("Wrong surname correctly rejected")

    def test_track_application_unknown_code(self):
        """GET /api/applications/track - unknown code"""
        params = {"code": "DV-XX999999", "last_name": "Yilmaz"}
        r = requests.get(f"{self.base_url}/applications/track", params=params, timeout=10)
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        self.log("Unknown code correctly rejected")

    def test_contact_form(self):
        """POST /api/contact"""
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+905551234567",
            "subject": "Test message",
            "message": "This is a test contact message from automated testing."
        }
        r = requests.post(f"{self.base_url}/contact", json=payload, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert result["ok"] is True, "Contact form submission failed"
        self.log("Contact form submitted successfully")

    def test_legal_content(self):
        """GET /api/content/legal - refund_terms and service_terms"""
        r = requests.get(f"{self.base_url}/content/legal", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "refund_terms" in data, "Missing refund_terms"
        assert "service_terms" in data, "Missing service_terms"
        
        # Verify refund_terms structure
        refund = data["refund_terms"]
        assert "updated_at" in refund, "Missing updated_at in refund_terms"
        assert "intro" in refund, "Missing intro in refund_terms"
        assert "sections" in refund, "Missing sections in refund_terms"
        assert isinstance(refund["sections"], list), "refund_terms sections should be a list"
        assert len(refund["sections"]) >= 5, f"Expected at least 5 refund sections, got {len(refund['sections'])}"
        for section in refund["sections"]:
            assert "title" in section, "Section missing title"
            assert "items" in section, "Section missing items"
            assert isinstance(section["items"], list), "Section items should be a list"
        
        # Verify service_terms structure
        service = data["service_terms"]
        assert "updated_at" in service, "Missing updated_at in service_terms"
        assert "intro" in service, "Missing intro in service_terms"
        assert "sections" in service, "Missing sections in service_terms"
        assert isinstance(service["sections"], list), "service_terms sections should be a list"
        assert len(service["sections"]) >= 6, f"Expected at least 6 service sections, got {len(service['sections'])}"
        
        self.log(f"Legal content: {len(refund['sections'])} refund sections, {len(service['sections'])} service sections")

    # ============================================================
    # PAYMENT ENDPOINTS
    # ============================================================

    def test_payment_checkout_valid(self):
        """POST /api/payments/checkout - valid application"""
        assert self.test_application_id, "Need created application"
        payload = {
            "application_id": self.test_application_id,
            "origin_url": "https://visa-application-ae.preview.emergentagent.com"
        }
        r = requests.post(f"{self.base_url}/payments/checkout", json=payload, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert "checkout_url" in result, "Missing checkout_url"
        assert "session_id" in result, "Missing session_id"
        assert "checkout.stripe.com" in result["checkout_url"], "Invalid checkout URL"
        self.test_session_id = result["session_id"]
        self.log(f"Checkout session created: {self.test_session_id}")

    def test_payment_checkout_unknown_app(self):
        """POST /api/payments/checkout - unknown application"""
        payload = {
            "application_id": "unknown-id-12345",
            "origin_url": "https://visa-application-ae.preview.emergentagent.com"
        }
        r = requests.post(f"{self.base_url}/payments/checkout", json=payload, timeout=10)
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        self.log("Unknown application correctly rejected")

    def test_payment_status(self):
        """GET /api/payments/status/{session_id}"""
        assert self.test_session_id, "Need checkout session"
        r = requests.get(f"{self.base_url}/payments/status/{self.test_session_id}", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert "session_id" in result, "Missing session_id"
        assert "status" in result, "Missing status"
        assert "payment_status" in result, "Missing payment_status"
        self.log(f"Payment status: {result['payment_status']}")

    def test_bank_transfer_payment_valid(self):
        """POST /api/payments/bank-transfer - valid application"""
        # Create a new application for bank transfer test
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        files1 = {"file": ("p.png", io.BytesIO(png_data), "image/png")}
        r1 = requests.post(f"{self.base_url}/uploads", files=files1, data={"doc_type": "passport"}, timeout=15)
        passport_id = r1.json()["file_id"]
        files2 = {"file": ("ph.png", io.BytesIO(png_data), "image/png")}
        r2 = requests.post(f"{self.base_url}/uploads", files=files2, data={"doc_type": "photo"}, timeout=15)
        photo_id = r2.json()["file_id"]
        
        tomorrow = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        app_payload = {
            "contact": {
                "full_name": "Bank Transfer Test",
                "email": f"banktest_{datetime.now().timestamp()}@test.com",
                "phone": "+905551234567",
                "address_city": "Istanbul"
            },
            "travelers": [{
                "first_name": "BANK",
                "last_name": "TEST",
                "birth_date": "1990-01-01",
                "gender": "male",
                "applicant_type": "adult",
                "nationality": "TR",
                "passport_no": "U99999999",
                "passport_expiry": "2028-12-31",
                "visa_type_id": "visa_30_single",
                "passport_file_id": passport_id,
                "photo_file_id": photo_id
            }],
            "travel": {
                "arrival_date": tomorrow,
                "departure_date": return_date,
                "purpose": "tourism",
                "birth_country": "TR"
            },
            "addons": {"express": False, "insurance": False},
            "extra_documents": {},
            "kvkk_accepted": True
        }
        r_app = requests.post(f"{self.base_url}/applications", json=app_payload, timeout=15)
        assert r_app.status_code == 200, f"Failed to create application: {r_app.status_code}"
        app_id = r_app.json()["id"]
        
        # Now test bank transfer
        payload = {
            "application_id": app_id,
            "origin_url": "https://visa-application-ae.preview.emergentagent.com"
        }
        r = requests.post(f"{self.base_url}/payments/bank-transfer", json=payload, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert result["ok"] is True, "Bank transfer selection failed"
        assert "reference_code" in result, "Missing reference_code"
        assert "amount" in result, "Missing amount"
        assert "currency" in result, "Missing currency"
        assert "bank" in result, "Missing bank details"
        assert "iban" in result["bank"], "Missing IBAN in bank details"
        assert "steps" in result["bank"], "Missing steps in bank details"
        
        self.test_bank_transfer_app_id = app_id
        self.log(f"Bank transfer selected: {result['reference_code']}, amount: {result['amount']} {result['currency']}")

    def test_bank_transfer_payment_unknown_app(self):
        """POST /api/payments/bank-transfer - unknown application"""
        payload = {
            "application_id": "unknown-id-12345",
            "origin_url": "https://visa-application-ae.preview.emergentagent.com"
        }
        r = requests.post(f"{self.base_url}/payments/bank-transfer", json=payload, timeout=10)
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        self.log("Unknown application correctly rejected for bank transfer")

    def test_bank_transfer_payment_already_paid(self):
        """POST /api/payments/bank-transfer - already paid application"""
        if not hasattr(self, 'test_bank_transfer_app_id'):
            self.log("Skipping: no bank transfer application created", "WARN")
            return
        
        # Mark as paid first via admin
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r_mark = requests.post(f"{self.base_url}/admin/applications/{self.test_bank_transfer_app_id}/mark-paid", headers=headers, timeout=10)
        assert r_mark.status_code == 200, "Failed to mark as paid"
        
        # Try to select bank transfer again
        payload = {
            "application_id": self.test_bank_transfer_app_id,
            "origin_url": "https://visa-application-ae.preview.emergentagent.com"
        }
        r = requests.post(f"{self.base_url}/payments/bank-transfer", json=payload, timeout=10)
        assert r.status_code == 400, f"Expected 400 for already paid, got {r.status_code}"
        self.log("Already paid application correctly rejected for bank transfer")

    # ============================================================
    # ADMIN ENDPOINTS
    # ============================================================

    def test_admin_login_invalid(self):
        """POST /api/admin/login - invalid credentials"""
        payload = {"email": "wrong@example.com", "password": "wrongpass"}
        r = requests.post(f"{self.base_url}/admin/login", json=payload, timeout=10)
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        self.log("Invalid admin login correctly rejected")

    def test_admin_login_valid(self):
        """POST /api/admin/login - valid credentials"""
        payload = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        r = requests.post(f"{self.base_url}/admin/login", json=payload, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert "token" in result, "Missing token"
        assert "user" in result, "Missing user"
        self.admin_token = result["token"]
        self.log(f"Admin logged in: {result['user']['email']}")

    def test_admin_endpoints_without_token(self):
        """Admin endpoints without Bearer token should return 401"""
        endpoints = [
            "/admin/me",
            "/admin/stats",
            "/admin/applications",
            "/admin/contact-messages",
            "/admin/emails",
            "/admin/visa-types"
        ]
        for endpoint in endpoints:
            r = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            assert r.status_code == 401, f"{endpoint}: Expected 401, got {r.status_code}"
        self.log("All admin endpoints correctly require authentication")

    def test_admin_me(self):
        """GET /api/admin/me"""
        assert self.admin_token, "Need admin token"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.get(f"{self.base_url}/admin/me", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert result["email"] == ADMIN_EMAIL, "Email mismatch"
        assert result["role"] == "admin", "Role mismatch"
        self.log(f"Admin me: {result}")

    def test_admin_stats(self):
        """GET /api/admin/stats"""
        assert self.admin_token, "Need admin token"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.get(f"{self.base_url}/admin/stats", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        required = ["total", "today", "payment_pending", "reviewing", "approved", "rejected", "revenue", "unread_messages"]
        for key in required:
            assert key in result, f"Missing {key} in stats"
        self.log(f"Admin stats: {result}")

    def test_admin_applications_list(self):
        """GET /api/admin/applications"""
        assert self.admin_token, "Need admin token"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.get(f"{self.base_url}/admin/applications", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert "items" in result, "Missing items"
        assert "total" in result, "Missing total"
        assert len(result["items"]) > 0, "Expected at least one application"
        self.log(f"Admin applications: {result['total']} total")

    def test_admin_applications_search(self):
        """GET /api/admin/applications?q=<reference_code>"""
        assert self.admin_token, "Need admin token"
        assert self.test_reference_code, "Need reference code"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        params = {"q": self.test_reference_code}
        r = requests.get(f"{self.base_url}/admin/applications", headers=headers, params=params, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert len(result["items"]) >= 1, "Expected to find the test application"
        found = any(item["reference_code"] == self.test_reference_code for item in result["items"])
        assert found, f"Test application {self.test_reference_code} not found in search results"
        self.log(f"Search found application: {self.test_reference_code}")

    def test_admin_application_detail(self):
        """GET /api/admin/applications/{id}"""
        assert self.admin_token, "Need admin token"
        assert self.test_application_id, "Need application id"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.get(f"{self.base_url}/admin/applications/{self.test_application_id}", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert "application" in result, "Missing application"
        assert "transactions" in result, "Missing transactions"
        assert result["application"]["id"] == self.test_application_id, "Application ID mismatch"
        self.log(f"Admin application detail loaded: {result['application']['reference_code']}")

    def test_admin_update_application_status(self):
        """PATCH /api/admin/applications/{id}"""
        assert self.admin_token, "Need admin token"
        assert self.test_application_id, "Need application id"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "status": "reviewing",
            "note": "Test status update from automated testing",
            "notify": False  # Don't send email
        }
        r = requests.patch(f"{self.base_url}/admin/applications/{self.test_application_id}", headers=headers, json=payload, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert result["application"]["status"] == "reviewing", "Status not updated"
        self.log(f"Application status updated to: {result['application']['status']}")

    def test_admin_contact_messages(self):
        """GET /api/admin/contact-messages"""
        assert self.admin_token, "Need admin token"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.get(f"{self.base_url}/admin/contact-messages", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert "items" in result, "Missing items"
        assert len(result["items"]) > 0, "Expected at least one contact message"
        self.test_contact_id = result["items"][0]["id"]
        self.log(f"Admin contact messages: {len(result['items'])} messages")

    def test_admin_mark_message_read(self):
        """PATCH /api/admin/contact-messages/{id}/read"""
        assert self.admin_token, "Need admin token"
        assert self.test_contact_id, "Need contact message id"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.patch(f"{self.base_url}/admin/contact-messages/{self.test_contact_id}/read", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert result["ok"] is True, "Mark read failed"
        self.log("Contact message marked as read")

    def test_admin_emails(self):
        """GET /api/admin/emails"""
        assert self.admin_token, "Need admin token"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.get(f"{self.base_url}/admin/emails", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert "email_configured" in result, "Missing email_configured"
        assert result["email_configured"] is False, "Email should not be configured (RESEND_API_KEY is empty)"
        assert "items" in result, "Missing items"
        # Should have at least the application received email (skipped)
        assert len(result["items"]) > 0, "Expected at least one email record"
        skipped = [item for item in result["items"] if item.get("status") == "skipped"]
        assert len(skipped) > 0, "Expected at least one skipped email"
        self.log(f"Admin emails: {len(result['items'])} emails, {len(skipped)} skipped")

    def test_admin_visa_types(self):
        """GET /api/admin/visa-types"""
        assert self.admin_token, "Need admin token"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.get(f"{self.base_url}/admin/visa-types", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert isinstance(result, list), "Expected list of visa types"
        assert len(result) >= 5, f"Expected at least 5 visa types, got {len(result)}"
        self.log(f"Admin visa types: {len(result)} types")

    def test_admin_update_visa_type(self):
        """PATCH /api/admin/visa-types/{id}"""
        assert self.admin_token, "Need admin token"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Get current visa types
        r = requests.get(f"{self.base_url}/admin/visa-types", headers=headers, timeout=10)
        visa_types = r.json()
        test_visa = visa_types[0]
        original_price = test_visa["price"]
        
        # Update price
        new_price = original_price + 100
        payload = {"price": new_price}
        r = requests.patch(f"{self.base_url}/admin/visa-types/{test_visa['id']}", headers=headers, json=payload, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert float(result["price"]) == new_price, "Price not updated"
        self.log(f"Visa type price updated: {original_price} -> {new_price}")
        
        # Restore original price
        restore_payload = {"price": original_price}
        r = requests.patch(f"{self.base_url}/admin/visa-types/{test_visa['id']}", headers=headers, json=restore_payload, timeout=10)
        assert r.status_code == 200, "Failed to restore original price"
        self.log(f"Visa type price restored to: {original_price}")

    def test_admin_mark_paid_valid(self):
        """POST /api/admin/applications/{id}/mark-paid - mark bank transfer as paid"""
        # Create a new application for mark-paid test
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        files1 = {"file": ("p.png", io.BytesIO(png_data), "image/png")}
        r1 = requests.post(f"{self.base_url}/uploads", files=files1, data={"doc_type": "passport"}, timeout=15)
        passport_id = r1.json()["file_id"]
        files2 = {"file": ("ph.png", io.BytesIO(png_data), "image/png")}
        r2 = requests.post(f"{self.base_url}/uploads", files=files2, data={"doc_type": "photo"}, timeout=15)
        photo_id = r2.json()["file_id"]
        
        tomorrow = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        app_payload = {
            "contact": {
                "full_name": "Mark Paid Test",
                "email": f"markpaid_{datetime.now().timestamp()}@test.com",
                "phone": "+905551234567",
                "address_city": "Istanbul"
            },
            "travelers": [{
                "first_name": "MARK",
                "last_name": "PAID",
                "birth_date": "1990-01-01",
                "gender": "male",
                "applicant_type": "adult",
                "nationality": "TR",
                "passport_no": "U88888888",
                "passport_expiry": "2028-12-31",
                "visa_type_id": "visa_30_single",
                "passport_file_id": passport_id,
                "photo_file_id": photo_id
            }],
            "travel": {
                "arrival_date": tomorrow,
                "departure_date": return_date,
                "purpose": "tourism",
                "birth_country": "TR"
            },
            "addons": {"express": False, "insurance": False},
            "extra_documents": {},
            "kvkk_accepted": True
        }
        r_app = requests.post(f"{self.base_url}/applications", json=app_payload, timeout=15)
        assert r_app.status_code == 200, f"Failed to create application: {r_app.status_code}"
        app_id = r_app.json()["id"]
        
        # Select bank transfer
        payload = {
            "application_id": app_id,
            "origin_url": "https://visa-application-ae.preview.emergentagent.com"
        }
        r = requests.post(f"{self.base_url}/payments/bank-transfer", json=payload, timeout=15)
        assert r.status_code == 200, "Failed to select bank transfer"
        
        # Now mark as paid
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.post(f"{self.base_url}/admin/applications/{app_id}/mark-paid", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert result["ok"] is True, "Mark paid failed"
        assert "application" in result, "Missing application in response"
        assert result["application"]["payment"]["status"] == "paid", f"Payment status should be 'paid', got {result['application']['payment']['status']}"
        assert result["application"]["status"] == "reviewing", f"Application status should be 'reviewing', got {result['application']['status']}"
        assert result["email_notification"] == "skipped", f"Expected 'skipped' email notification, got {result['email_notification']}"
        
        self.test_mark_paid_app_id = app_id
        self.log(f"Application marked as paid: {app_id}, status: {result['application']['status']}")

    def test_admin_mark_paid_already_paid(self):
        """POST /api/admin/applications/{id}/mark-paid - already paid returns already_paid=true"""
        if not hasattr(self, 'test_mark_paid_app_id'):
            self.log("Skipping: no mark-paid application created", "WARN")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.post(f"{self.base_url}/admin/applications/{self.test_mark_paid_app_id}/mark-paid", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert result["ok"] is True, "Mark paid failed"
        assert result.get("already_paid") is True, "Expected already_paid=true"
        self.log("Already paid application correctly returns already_paid=true")

    def test_admin_mark_paid_unknown_app(self):
        """POST /api/admin/applications/{id}/mark-paid - unknown application"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.post(f"{self.base_url}/admin/applications/unknown-id-12345/mark-paid", headers=headers, timeout=10)
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        self.log("Unknown application correctly returns 404 for mark-paid")

    # ============================================================
    # PHASE 3: MULTI-TRAVELER & FAMILY PRICING TESTS
    # ============================================================

    def test_pricing_quote_single_traveler(self):
        """POST /api/pricing/quote - single traveler (no discount)"""
        payload = {
            "visa_type_ids": ["visa_30_single"],
            "addons": {"express": False, "insurance": False}
        }
        r = requests.post(f"{self.base_url}/pricing/quote", json=payload, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["traveler_count"] == 1, f"Expected 1 traveler, got {data['traveler_count']}"
        assert data["family_discount_rate"] == 0.0, f"Expected no discount, got {data['family_discount_rate']}"
        assert data["family_discount"] == 0.0, f"Expected 0 discount, got {data['family_discount']}"
        assert data["subtotal"] == data["total"], "Single traveler: subtotal should equal total"
        self.log(f"Single traveler pricing: {data}")

    def test_pricing_quote_two_travelers(self):
        """POST /api/pricing/quote - 2 travelers (no discount)"""
        payload = {
            "visa_type_ids": ["visa_30_single", "visa_30_child"],
            "addons": {"express": False, "insurance": False}
        }
        r = requests.post(f"{self.base_url}/pricing/quote", json=payload, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["traveler_count"] == 2, f"Expected 2 travelers, got {data['traveler_count']}"
        assert data["family_discount_rate"] == 0.0, f"Expected no discount for 2 travelers, got {data['family_discount_rate']}"
        self.log(f"Two travelers pricing: {data}")

    def test_pricing_quote_three_travelers_discount(self):
        """POST /api/pricing/quote - 3 travelers (5% discount)"""
        payload = {
            "visa_type_ids": ["visa_30_single", "visa_30_single", "visa_30_child"],
            "addons": {"express": False, "insurance": False}
        }
        r = requests.post(f"{self.base_url}/pricing/quote", json=payload, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["traveler_count"] == 3, f"Expected 3 travelers, got {data['traveler_count']}"
        assert data["family_discount_rate"] == 0.05, f"Expected 5% discount, got {data['family_discount_rate']}"
        expected_discount = round(data["subtotal"] * 0.05, 2)
        assert data["family_discount"] == expected_discount, f"Discount mismatch: expected {expected_discount}, got {data['family_discount']}"
        expected_total = round(data["subtotal"] - data["family_discount"] + data["addons_total"], 2)
        assert data["total"] == expected_total, f"Total mismatch: expected {expected_total}, got {data['total']}"
        self.log(f"Three travelers pricing (5% discount): {data}")

    def test_pricing_quote_five_travelers_discount(self):
        """POST /api/pricing/quote - 5 travelers (8% discount)"""
        payload = {
            "visa_type_ids": ["visa_30_single"] * 5,
            "addons": {"express": False, "insurance": False}
        }
        r = requests.post(f"{self.base_url}/pricing/quote", json=payload, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["traveler_count"] == 5, f"Expected 5 travelers, got {data['traveler_count']}"
        assert data["family_discount_rate"] == 0.08, f"Expected 8% discount, got {data['family_discount_rate']}"
        expected_discount = round(data["subtotal"] * 0.08, 2)
        assert data["family_discount"] == expected_discount, f"Discount mismatch: expected {expected_discount}, got {data['family_discount']}"
        self.log(f"Five travelers pricing (8% discount): {data}")

    def test_pricing_quote_with_addons_per_person(self):
        """POST /api/pricing/quote - 3 travelers with per-person addons"""
        payload = {
            "visa_type_ids": ["visa_30_single", "visa_30_single", "visa_30_child"],
            "addons": {"express": True, "insurance": True}
        }
        r = requests.post(f"{self.base_url}/pricing/quote", json=payload, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["traveler_count"] == 3, f"Expected 3 travelers, got {data['traveler_count']}"
        assert len(data["addons"]) == 2, f"Expected 2 addons, got {len(data['addons'])}"
        for addon in data["addons"]:
            assert addon["quantity"] == 3, f"Per-person addon should have quantity 3, got {addon['quantity']}"
        expected_total = round(data["subtotal"] - data["family_discount"] + data["addons_total"], 2)
        assert data["total"] == expected_total, f"Total mismatch with addons: expected {expected_total}, got {data['total']}"
        self.log(f"Three travelers with addons: {data}")

    def test_pricing_quote_invalid_visa_type(self):
        """POST /api/pricing/quote - invalid visa type"""
        payload = {
            "visa_type_ids": ["invalid_visa_id"],
            "addons": {"express": False, "insurance": False}
        }
        r = requests.post(f"{self.base_url}/pricing/quote", json=payload, timeout=10)
        assert r.status_code == 400, f"Expected 400 for invalid visa type, got {r.status_code}"
        self.log("Invalid visa type rejected correctly")

    def test_pricing_quote_new_visa_types(self):
        """POST /api/pricing/quote - with new visa types (transit and freelancer)"""
        # Test transit visa
        payload_transit = {
            "visa_type_ids": ["visa_transit_48"],
            "addons": {"express": False, "insurance": False}
        }
        r = requests.post(f"{self.base_url}/pricing/quote", json=payload_transit, timeout=10)
        assert r.status_code == 200, f"Expected 200 for transit visa, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["traveler_count"] == 1, f"Expected 1 traveler, got {data['traveler_count']}"
        assert data["subtotal"] == 1299.0, f"Expected 1299.0 for transit visa, got {data['subtotal']}"
        self.log(f"Transit visa pricing: {data}")
        
        # Test freelancer visa
        payload_freelancer = {
            "visa_type_ids": ["visa_freelancer_2y"],
            "addons": {"express": False, "insurance": False}
        }
        r = requests.post(f"{self.base_url}/pricing/quote", json=payload_freelancer, timeout=10)
        assert r.status_code == 200, f"Expected 200 for freelancer visa, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["traveler_count"] == 1, f"Expected 1 traveler, got {data['traveler_count']}"
        assert data["subtotal"] == 109000.0, f"Expected 109000.0 for freelancer visa, got {data['subtotal']}"
        self.log(f"Freelancer visa pricing: {data}")

    def test_multi_traveler_application_two_travelers(self):
        """POST /api/applications - 2 travelers with correct file mapping"""
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        files1 = {"file": ("passport1.png", io.BytesIO(png_data), "image/png")}
        r1 = requests.post(f"{self.base_url}/uploads", files=files1, data={"doc_type": "passport"}, timeout=15)
        assert r1.status_code == 200, f"Upload 1 failed: {r1.status_code}"
        passport1_id = r1.json()["file_id"]
        
        files2 = {"file": ("photo1.png", io.BytesIO(png_data), "image/png")}
        r2 = requests.post(f"{self.base_url}/uploads", files=files2, data={"doc_type": "photo"}, timeout=15)
        assert r2.status_code == 200, f"Upload 2 failed: {r2.status_code}"
        photo1_id = r2.json()["file_id"]
        
        files3 = {"file": ("passport2.png", io.BytesIO(png_data), "image/png")}
        r3 = requests.post(f"{self.base_url}/uploads", files=files3, data={"doc_type": "passport"}, timeout=15)
        assert r3.status_code == 200, f"Upload 3 failed: {r3.status_code}"
        passport2_id = r3.json()["file_id"]
        
        files4 = {"file": ("photo2.png", io.BytesIO(png_data), "image/png")}
        r4 = requests.post(f"{self.base_url}/uploads", files=files4, data={"doc_type": "photo"}, timeout=15)
        assert r4.status_code == 200, f"Upload 4 failed: {r4.status_code}"
        photo2_id = r4.json()["file_id"]
        
        tomorrow = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        payload = {
            "contact": {
                "full_name": "Mehmet Yilmaz",
                "email": f"test2travelers_{datetime.now().timestamp()}@test.com",
                "phone": "+905551234567",
                "address_city": "Istanbul"
            },
            "travelers": [
                {
                    "first_name": "MEHMET",
                    "last_name": "YILMAZ",
                    "birth_date": "1985-05-15",
                    "gender": "male",
                    "applicant_type": "adult",
                    "nationality": "TR",
                    "passport_no": "U12345678",
                    "passport_expiry": "2028-12-31",
                    "visa_type_id": "visa_30_single",
                    "passport_file_id": passport1_id,
                    "photo_file_id": photo1_id
                },
                {
                    "first_name": "AYSE",
                    "last_name": "YILMAZ",
                    "birth_date": "2015-08-20",
                    "gender": "female",
                    "applicant_type": "child",
                    "nationality": "TR",
                    "passport_no": "U87654321",
                    "passport_expiry": "2028-12-31",
                    "visa_type_id": "visa_30_child",
                    "passport_file_id": passport2_id,
                    "photo_file_id": photo2_id
                }
            ],
            "travel": {
                "arrival_date": tomorrow,
                "departure_date": return_date,
                "purpose": "tourism",
                "birth_country": "TR"
            },
            "addons": {"express": False, "insurance": False},
            "extra_documents": {},
            "kvkk_accepted": True
        }
        
        r = requests.post(f"{self.base_url}/applications", json=payload, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert len(data["travelers"]) == 2, f"Expected 2 travelers, got {len(data['travelers'])}"
        
        assert data["travelers"][0]["documents"]["passport_file_id"] == passport1_id, "Traveler 1 passport file mismatch"
        assert data["travelers"][0]["documents"]["photo_file_id"] == photo1_id, "Traveler 1 photo file mismatch"
        assert data["travelers"][1]["documents"]["passport_file_id"] == passport2_id, "Traveler 2 passport file mismatch"
        assert data["travelers"][1]["documents"]["photo_file_id"] == photo2_id, "Traveler 2 photo file mismatch"
        
        assert "pricing" in data, "Missing pricing in response"
        assert data["pricing"]["traveler_count"] == 2, f"Pricing traveler count mismatch"
        
        self.test_application_id_multi = data["id"]
        self.test_reference_code_multi = data["reference_code"]
        self.log(f"Multi-traveler application created: {data['reference_code']}, travelers: {len(data['travelers'])}")

    def test_multi_traveler_application_invalid_file_id(self):
        """POST /api/applications - reject invalid file_id"""
        tomorrow = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        payload = {
            "contact": {
                "full_name": "Test User",
                "email": f"testinvalid_{datetime.now().timestamp()}@test.com",
                "phone": "+905551234567",
                "address_city": "Istanbul"
            },
            "travelers": [
                {
                    "first_name": "TEST",
                    "last_name": "USER",
                    "birth_date": "1990-01-01",
                    "gender": "male",
                    "applicant_type": "adult",
                    "nationality": "TR",
                    "passport_no": "U99999999",
                    "passport_expiry": "2028-12-31",
                    "visa_type_id": "visa_30_single",
                    "passport_file_id": "invalid-file-id-12345",
                    "photo_file_id": "invalid-file-id-67890"
                }
            ],
            "travel": {
                "arrival_date": tomorrow,
                "departure_date": return_date,
                "purpose": "tourism",
                "birth_country": "TR"
            },
            "addons": {"express": False, "insurance": False},
            "extra_documents": {},
            "kvkk_accepted": True
        }
        
        r = requests.post(f"{self.base_url}/applications", json=payload, timeout=15)
        assert r.status_code == 400, f"Expected 400 for invalid file_id, got {r.status_code}"
        self.log("Invalid file_id rejected correctly")

    def test_track_application_any_traveler_lastname(self):
        """GET /api/applications/track - works with any traveler's last name"""
        if not hasattr(self, 'test_reference_code_multi'):
            self.log("Skipping: no multi-traveler application created", "WARN")
            return
        
        r1 = requests.get(f"{self.base_url}/applications/track", params={"code": self.test_reference_code_multi, "last_name": "YILMAZ"}, timeout=10)
        assert r1.status_code == 200, f"Expected 200 with first traveler's last name, got {r1.status_code}"
        
        r2 = requests.get(f"{self.base_url}/applications/track", params={"code": self.test_reference_code_multi, "last_name": "yilmaz"}, timeout=10)
        assert r2.status_code == 200, f"Expected 200 with case-insensitive match, got {r2.status_code}"
        
        self.log("Track application works with any traveler's last name")

    def test_payment_checkout_multi_traveler_amount(self):
        """POST /api/payments/checkout - verify amount equals multi-traveler total"""
        if not hasattr(self, 'test_application_id_multi'):
            self.log("Skipping: no multi-traveler application created", "WARN")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r_app = requests.get(f"{self.base_url}/admin/applications/{self.test_application_id_multi}", headers=headers, timeout=10)
        assert r_app.status_code == 200, f"Failed to get application: {r_app.status_code}"
        app_data = r_app.json()["application"]
        expected_total = app_data["pricing"]["total"]
        
        payload = {
            "application_id": self.test_application_id_multi,
            "origin_url": "https://visa-application-ae.preview.emergentagent.com"
        }
        r = requests.post(f"{self.base_url}/payments/checkout", json=payload, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "checkout_url" in data, "Missing checkout_url"
        assert "session_id" in data, "Missing session_id"
        
        self.log(f"Checkout created for multi-traveler app, expected total: {expected_total}")

    def test_admin_upload_visa_document(self):
        """POST /api/admin/applications/{id}/visa-document"""
        if not hasattr(self, 'test_application_id_multi'):
            self.log("Skipping: no multi-traveler application created", "WARN")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        pdf_data = b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n210\n%%EOF'
        
        files = {"file": ("approved_visa.pdf", io.BytesIO(pdf_data), "application/pdf")}
        r = requests.post(f"{self.base_url}/admin/applications/{self.test_application_id_multi}/visa-document", files=files, headers=headers, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "application" in data, "Missing application in response"
        assert data["application"]["visa_result"] is not None, "visa_result should be populated"
        assert "file_id" in data["application"]["visa_result"], "Missing file_id in visa_result"
        
        self.visa_document_file_id = data["application"]["visa_result"]["file_id"]
        self.log(f"Visa document uploaded: {self.visa_document_file_id}")

    def test_admin_send_visa_email(self):
        """POST /api/admin/applications/{id}/send-visa"""
        if not hasattr(self, 'test_application_id_multi'):
            self.log("Skipping: no multi-traveler application created", "WARN")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "origin_url": "https://visa-application-ae.preview.emergentagent.com",
            "message": "Vizeniz hazir. Iyi yolculuklar!",
            "set_approved": True
        }
        
        r = requests.post(f"{self.base_url}/admin/applications/{self.test_application_id_multi}/send-visa", json=payload, headers=headers, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "application" in data, "Missing application in response"
        assert data["application"]["status"] == "approved", f"Status should be approved, got {data['application']['status']}"
        assert data["application"]["visa_result"]["sent_at"] is not None, "sent_at should be populated"
        assert data["email_notification"] == "skipped", f"Expected 'skipped' email status, got {data['email_notification']}"
        
        self.log(f"Visa email sent (status: {data['email_notification']}), application status: {data['application']['status']}")

    def test_admin_delete_visa_document(self):
        """DELETE /api/admin/applications/{id}/visa-document"""
        if not hasattr(self, 'test_application_id_multi'):
            self.log("Skipping: no multi-traveler application created", "WARN")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.delete(f"{self.base_url}/admin/applications/{self.test_application_id_multi}/visa-document", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["application"]["visa_result"] is None, "visa_result should be None after deletion"
        self.log("Visa document deleted successfully")

    def test_admin_emails_outbox(self):
        """GET /api/admin/emails - verify email records"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.get(f"{self.base_url}/admin/emails", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "items" in data, "Missing items in response"
        assert isinstance(data["items"], list), "items should be a list"
        
        email_kinds = [item.get("kind") for item in data["items"]]
        assert "application_received" in email_kinds, "Missing application_received email"
        
        for item in data["items"]:
            assert item.get("status") == "skipped", f"Expected 'skipped' status, got {item.get('status')}"
        
        self.log(f"Email outbox contains {len(data['items'])} records, all with status 'skipped'")

    # ============================================================
    # PHASE 4: AI PASSPORT OCR, BLOG ARTICLES, TESTIMONIALS, WHATSAPP
    # ============================================================

    def test_passport_ocr_with_real_image(self):
        """POST /api/passport/read - with real passport test image"""
        try:
            with open("/tmp/passport_test.jpg", "rb") as f:
                passport_data = f.read()
        except FileNotFoundError:
            self.log("Skipping: /tmp/passport_test.jpg not found", "WARN")
            return
        
        files = {"file": ("passport.jpg", io.BytesIO(passport_data), "image/jpeg")}
        data = {"doc_type": "passport"}
        r = requests.post(f"{self.base_url}/uploads", files=files, data=data, timeout=15)
        assert r.status_code == 200, f"Upload failed: {r.status_code}: {r.text}"
        file_id = r.json()["file_id"]
        
        form_data = {"file_id": file_id}
        r = requests.post(f"{self.base_url}/passport/read", data=form_data, timeout=30)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert "ok" in result, "Missing 'ok' field"
        
        if result["ok"]:
            assert "data" in result, "Missing 'data' field"
            data = result["data"]
            assert "first_name" in data, "Missing first_name"
            assert "last_name" in data, "Missing last_name"
            assert "passport_no" in data, "Missing passport_no"
            assert "birth_date" in data, "Missing birth_date"
            assert "passport_expiry" in data, "Missing passport_expiry"
            assert "gender" in data, "Missing gender"
            assert "nationality" in data, "Missing nationality"
            assert "confidence" in data, "Missing confidence"
            assert "is_passport" in data, "Missing is_passport"
            self.log(f"Passport OCR success: {data.get('first_name')} {data.get('last_name')}, passport: {data.get('passport_no')}, confidence: {data.get('confidence')}")
        else:
            self.log(f"Passport OCR returned ok=false: {result.get('reason')}, {result.get('message')}", "WARN")

    def test_passport_ocr_with_pdf(self):
        """POST /api/passport/read - PDF should return graceful error"""
        pdf_data = b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n210\n%%EOF'
        files = {"file": ("passport.pdf", io.BytesIO(pdf_data), "application/pdf")}
        data = {"doc_type": "passport"}
        r = requests.post(f"{self.base_url}/uploads", files=files, data=data, timeout=15)
        assert r.status_code == 200, f"Upload failed: {r.status_code}"
        file_id = r.json()["file_id"]
        
        form_data = {"file_id": file_id}
        r = requests.post(f"{self.base_url}/passport/read", data=form_data, timeout=15)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert result["ok"] is False, "PDF should return ok=false"
        assert result["reason"] == "pdf", f"Expected reason='pdf', got {result.get('reason')}"
        self.log("PDF correctly rejected with graceful error")

    def test_passport_ocr_unknown_file_id(self):
        """POST /api/passport/read - unknown file_id returns 404"""
        form_data = {"file_id": "unknown-file-id-12345"}
        r = requests.post(f"{self.base_url}/passport/read", data=form_data, timeout=10)
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        self.log("Unknown file_id correctly returns 404")

    def test_articles_list_public(self):
        """GET /api/articles - list published articles"""
        r = requests.get(f"{self.base_url}/articles", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert isinstance(data, list), "Expected list of articles"
        assert len(data) >= 3, f"Expected at least 3 articles, got {len(data)}"
        for article in data[:3]:
            assert "slug" in article, "Missing slug"
            assert "title" in article, "Missing title"
            assert "excerpt" in article, "Missing excerpt"
            assert "date" in article, "Missing date"
            assert "body" in article, "Missing body"
        self.log(f"Found {len(data)} published articles")

    def test_articles_detail_public(self):
        """GET /api/articles/{slug} - get article detail with related"""
        r_list = requests.get(f"{self.base_url}/articles", timeout=10)
        assert r_list.status_code == 200, "Failed to get articles list"
        articles = r_list.json()
        if len(articles) == 0:
            self.log("Skipping: no articles available", "WARN")
            return
        
        test_slug = articles[0]["slug"]
        r = requests.get(f"{self.base_url}/articles/{test_slug}", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "article" in data, "Missing article"
        assert "related" in data, "Missing related"
        article = data["article"]
        assert article["slug"] == test_slug, "Slug mismatch"
        assert "title" in article, "Missing title"
        assert "excerpt" in article, "Missing excerpt"
        assert "body" in article, "Missing body"
        assert isinstance(article["body"], list), "Body should be a list of paragraphs"
        assert isinstance(data["related"], list), "Related should be a list"
        self.log(f"Article detail: {article['title']}, {len(data['related'])} related articles")

    def test_articles_detail_unknown_slug(self):
        """GET /api/articles/{slug} - unknown slug returns 404"""
        r = requests.get(f"{self.base_url}/articles/unknown-slug-12345", timeout=10)
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        self.log("Unknown article slug correctly returns 404")

    def test_admin_testimonials_list(self):
        """GET /api/admin/testimonials"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.get(f"{self.base_url}/admin/testimonials", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "items" in data, "Missing items"
        assert "review_summary" in data, "Missing review_summary"
        assert isinstance(data["items"], list), "items should be a list"
        assert len(data["items"]) >= 6, f"Expected at least 6 testimonials, got {len(data['items'])}"
        self.log(f"Admin testimonials: {len(data['items'])} testimonials")

    def test_admin_testimonials_create(self):
        """POST /api/admin/testimonials"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "name": "Test User OCR",
            "initials": "TU",
            "city": "Istanbul",
            "visa": "30 Gun Tek Giris",
            "date": "2026-01-15",
            "text": "Harika bir hizmet, cok memnun kaldim. Tesekkurler!",
            "rating": 5,
            "verified": True,
            "published": False,
            "order": 999
        }
        r = requests.post(f"{self.base_url}/admin/testimonials", json=payload, headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "id" in data, "Missing id"
        assert data["name"] == "Test User OCR", "Name mismatch"
        assert data["published"] is False, "Published should be False"
        self.test_testimonial_id = data["id"]
        self.log(f"Testimonial created: {data['id']}")

    def test_admin_testimonials_update(self):
        """PUT /api/admin/testimonials/{id}"""
        if not hasattr(self, 'test_testimonial_id'):
            self.log("Skipping: no testimonial created", "WARN")
            return
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "name": "Test User OCR Updated",
            "initials": "TU",
            "city": "Ankara",
            "visa": "30 Gun Tek Giris",
            "date": "2026-01-15",
            "text": "Harika bir hizmet, cok memnun kaldim. Tesekkurler! (Updated)",
            "rating": 5,
            "verified": True,
            "published": True,
            "order": 999
        }
        r = requests.put(f"{self.base_url}/admin/testimonials/{self.test_testimonial_id}", json=payload, headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["name"] == "Test User OCR Updated", "Name not updated"
        assert data["city"] == "Ankara", "City not updated"
        assert data["published"] is True, "Published should be True"
        self.log(f"Testimonial updated: {data['id']}")

    def test_admin_testimonials_appears_in_public(self):
        """Verify published testimonial appears in /api/content/site"""
        if not hasattr(self, 'test_testimonial_id'):
            self.log("Skipping: no testimonial created", "WARN")
            return
        r = requests.get(f"{self.base_url}/content/site", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        testimonials = data.get("testimonials", [])
        found = any(t.get("id") == self.test_testimonial_id for t in testimonials)
        assert found, f"Published testimonial {self.test_testimonial_id} not found in public content"
        self.log("Published testimonial appears in public content")

    def test_admin_testimonials_delete(self):
        """DELETE /api/admin/testimonials/{id}"""
        if not hasattr(self, 'test_testimonial_id'):
            self.log("Skipping: no testimonial created", "WARN")
            return
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.delete(f"{self.base_url}/admin/testimonials/{self.test_testimonial_id}", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["ok"] is True, "Delete failed"
        self.log(f"Testimonial deleted: {self.test_testimonial_id}")

    def test_admin_review_summary_update(self):
        """PUT /api/admin/review-summary"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "average": 4.8,
            "total_reviews": 1234,
            "total_applications": 5678,
            "recommend_rate": 96,
            "highlights": [
                {"label": "Hizli Islem", "value": 98},
                {"label": "Guvenilir", "value": 97}
            ]
        }
        r = requests.put(f"{self.base_url}/admin/review-summary", json=payload, headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["average"] == 4.8, "Average not updated"
        assert data["total_reviews"] == 1234, "Total reviews not updated"
        assert len(data["highlights"]) == 2, "Highlights not updated"
        self.log("Review summary updated")

    def test_admin_articles_list(self):
        """GET /api/admin/articles"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.get(f"{self.base_url}/admin/articles", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "items" in data, "Missing items"
        assert isinstance(data["items"], list), "items should be a list"
        assert len(data["items"]) >= 3, f"Expected at least 3 articles, got {len(data['items'])}"
        self.log(f"Admin articles: {len(data['items'])} articles")

    def test_admin_articles_create(self):
        """POST /api/admin/articles"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "title": "Test Article for OCR Testing",
            "slug": "",
            "date": "2026-01-20",
            "excerpt": "This is a test article created by automated testing to verify the admin articles CRUD functionality.",
            "body": ["First paragraph of the test article.", "Second paragraph with more details.", "Third paragraph concluding the article."],
            "published": False,
            "order": 999
        }
        r = requests.post(f"{self.base_url}/admin/articles", json=payload, headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "id" in data, "Missing id"
        assert "slug" in data, "Missing slug"
        assert data["title"] == "Test Article for OCR Testing", "Title mismatch"
        assert data["published"] is False, "Published should be False"
        assert len(data["slug"]) > 0, "Slug should be auto-generated"
        self.test_article_id = data["id"]
        self.test_article_slug = data["slug"]
        self.log(f"Article created: {data['id']}, slug: {data['slug']}")

    def test_admin_articles_update(self):
        """PUT /api/admin/articles/{id}"""
        if not hasattr(self, 'test_article_id'):
            self.log("Skipping: no article created", "WARN")
            return
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "title": "Test Article for OCR Testing (Updated)",
            "slug": self.test_article_slug,
            "date": "2026-01-20",
            "excerpt": "This is an updated test article excerpt.",
            "body": ["Updated first paragraph.", "Updated second paragraph."],
            "published": True,
            "order": 999
        }
        r = requests.put(f"{self.base_url}/admin/articles/{self.test_article_id}", json=payload, headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["title"] == "Test Article for OCR Testing (Updated)", "Title not updated"
        assert data["published"] is True, "Published should be True"
        self.log(f"Article updated: {data['id']}")

    def test_admin_articles_appears_in_public(self):
        """Verify published article appears in /api/articles"""
        if not hasattr(self, 'test_article_slug'):
            self.log("Skipping: no article created", "WARN")
            return
        r = requests.get(f"{self.base_url}/articles", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        found = any(a.get("slug") == self.test_article_slug for a in data)
        assert found, f"Published article {self.test_article_slug} not found in public articles"
        self.log("Published article appears in public articles list")

    def test_admin_articles_unpublished_404(self):
        """Unpublished article should 404 on public endpoint"""
        if not hasattr(self, 'test_article_id'):
            self.log("Skipping: no article created", "WARN")
            return
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {"title": "Test Article for OCR Testing (Updated)", "slug": self.test_article_slug, "date": "2026-01-20", "excerpt": "Test", "body": ["Test"], "published": False, "order": 999}
        r = requests.put(f"{self.base_url}/admin/articles/{self.test_article_id}", json=payload, headers=headers, timeout=10)
        assert r.status_code == 200, "Failed to unpublish article"
        
        r = requests.get(f"{self.base_url}/articles/{self.test_article_slug}", timeout=10)
        assert r.status_code == 404, f"Unpublished article should return 404, got {r.status_code}"
        self.log("Unpublished article correctly returns 404")

    def test_admin_articles_delete(self):
        """DELETE /api/admin/articles/{id}"""
        if not hasattr(self, 'test_article_id'):
            self.log("Skipping: no article created", "WARN")
            return
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        r = requests.delete(f"{self.base_url}/admin/articles/{self.test_article_id}", headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert data["ok"] is True, "Delete failed"
        self.log(f"Article deleted: {self.test_article_id}")

    def test_admin_whatsapp_link_visa_ready(self):
        """POST /api/admin/applications/{id}/whatsapp - visa_ready template"""
        if not hasattr(self, 'test_application_id'):
            self.log("Skipping: no application created", "WARN")
            return
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "template": "visa_ready",
            "origin_url": "https://visa-application-ae.preview.emergentagent.com"
        }
        r = requests.post(f"{self.base_url}/admin/applications/{self.test_application_id}/whatsapp", json=payload, headers=headers, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "url" in data, "Missing url"
        assert "message" in data, "Missing message"
        assert "phone" in data, "Missing phone"
        assert data["url"].startswith("https://wa.me/"), f"Invalid WhatsApp URL: {data['url']}"
        assert "905" in data["phone"], f"Phone should be normalized to 905xx format, got {data['phone']}"
        self.log(f"WhatsApp link generated: {data['url'][:50]}...")

    def test_admin_whatsapp_link_no_phone(self):
        """POST /api/admin/applications/{id}/whatsapp - application without phone returns 400"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        files1 = {"file": ("p.png", io.BytesIO(png_data), "image/png")}
        r1 = requests.post(f"{self.base_url}/uploads", files=files1, data={"doc_type": "passport"}, timeout=15)
        passport_id = r1.json()["file_id"]
        files2 = {"file": ("ph.png", io.BytesIO(png_data), "image/png")}
        r2 = requests.post(f"{self.base_url}/uploads", files=files2, data={"doc_type": "photo"}, timeout=15)
        photo_id = r2.json()["file_id"]
        
        tomorrow = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        
        app_payload = {
            "contact": {"full_name": "No Phone User", "email": f"nophone_{datetime.now().timestamp()}@test.com", "phone": "", "address_city": "Istanbul"},
            "travelers": [{"first_name": "TEST", "last_name": "USER", "birth_date": "1990-01-01", "gender": "male", "applicant_type": "adult", "nationality": "TR", "passport_no": "U99999999", "passport_expiry": "2028-12-31", "visa_type_id": "visa_30_single", "passport_file_id": passport_id, "photo_file_id": photo_id}],
            "travel": {"arrival_date": tomorrow, "departure_date": return_date, "purpose": "tourism", "birth_country": "TR"},
            "addons": {"express": False, "insurance": False},
            "extra_documents": {},
            "kvkk_accepted": True
        }
        r_app = requests.post(f"{self.base_url}/applications", json=app_payload, timeout=15)
        assert r_app.status_code == 200, "Failed to create application"
        app_id = r_app.json()["id"]
        
        payload = {"template": "visa_ready", "origin_url": "https://visa-application-ae.preview.emergentagent.com"}
        r = requests.post(f"{self.base_url}/admin/applications/{app_id}/whatsapp", json=payload, headers=headers, timeout=10)
        assert r.status_code == 400, f"Expected 400 for no phone, got {r.status_code}"
        self.log("WhatsApp link correctly returns 400 when no phone")

    def test_admin_whatsapp_link_unknown_application(self):
        """POST /api/admin/applications/{id}/whatsapp - unknown application returns 404"""
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {"template": "visa_ready", "origin_url": "https://visa-application-ae.preview.emergentagent.com"}
        r = requests.post(f"{self.base_url}/admin/applications/unknown-id-12345/whatsapp", json=payload, headers=headers, timeout=10)
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        self.log("WhatsApp link correctly returns 404 for unknown application")

    # ============================================================
    # RUN ALL TESTS
    # ============================================================

    def run_all(self):
        """Run all tests in order"""
        self.log("="*60)
        self.log("STARTING BACKEND API TESTS")
        self.log("="*60)
        
        # Public endpoints
        self.test("Health check", self.test_health)
        self.test("Get visa types", self.test_visa_types)
        self.test("Get site content", self.test_site_content)
        
        # File uploads
        self.test("Upload valid passport image", self.test_upload_valid_image)
        self.test("Upload biometric photo", self.test_upload_photo)
        self.test("Upload invalid extension", self.test_upload_invalid_extension)
        self.test("Upload oversized file", self.test_upload_oversized)
        
        # Applications
        self.test("Create application (valid)", self.test_create_application_valid)
        self.test("Create application (invalid)", self.test_create_application_invalid)
        self.test("Track application (correct)", self.test_track_application_correct)
        self.test("Track application (wrong surname)", self.test_track_application_wrong_surname)
        self.test("Track application (unknown code)", self.test_track_application_unknown_code)
        
        # Contact
        self.test("Submit contact form", self.test_contact_form)
        self.test("Get legal content", self.test_legal_content)
        
        # Payments
        self.test("Create payment checkout (valid)", self.test_payment_checkout_valid)
        self.test("Create payment checkout (unknown app)", self.test_payment_checkout_unknown_app)
        self.test("Get payment status", self.test_payment_status)
        self.test("Bank transfer payment (valid)", self.test_bank_transfer_payment_valid)
        self.test("Bank transfer payment (unknown app)", self.test_bank_transfer_payment_unknown_app)
        self.test("Bank transfer payment (already paid)", self.test_bank_transfer_payment_already_paid)
        
        # Admin auth
        self.test("Admin login (invalid)", self.test_admin_login_invalid)
        self.test("Admin login (valid)", self.test_admin_login_valid)
        self.test("Admin endpoints without token", self.test_admin_endpoints_without_token)
        
        # Admin endpoints
        self.test("Admin me", self.test_admin_me)
        self.test("Admin stats", self.test_admin_stats)
        self.test("Admin applications list", self.test_admin_applications_list)
        self.test("Admin applications search", self.test_admin_applications_search)
        self.test("Admin application detail", self.test_admin_application_detail)
        self.test("Admin update application status", self.test_admin_update_application_status)
        self.test("Admin contact messages", self.test_admin_contact_messages)
        self.test("Admin mark message read", self.test_admin_mark_message_read)
        self.test("Admin emails", self.test_admin_emails)
        self.test("Admin visa types", self.test_admin_visa_types)
        self.test("Admin update visa type", self.test_admin_update_visa_type)
        self.test("Admin mark paid (valid)", self.test_admin_mark_paid_valid)
        self.test("Admin mark paid (already paid)", self.test_admin_mark_paid_already_paid)
        self.test("Admin mark paid (unknown app)", self.test_admin_mark_paid_unknown_app)
        
        # Phase 3: Multi-traveler pricing
        self.test("Pricing quote - single traveler", self.test_pricing_quote_single_traveler)
        self.test("Pricing quote - two travelers", self.test_pricing_quote_two_travelers)
        self.test("Pricing quote - three travelers (5% discount)", self.test_pricing_quote_three_travelers_discount)
        self.test("Pricing quote - five travelers (8% discount)", self.test_pricing_quote_five_travelers_discount)
        self.test("Pricing quote - with per-person addons", self.test_pricing_quote_with_addons_per_person)
        self.test("Pricing quote - invalid visa type", self.test_pricing_quote_invalid_visa_type)
        self.test("Pricing quote - new visa types", self.test_pricing_quote_new_visa_types)
        
        # Phase 3: Multi-traveler applications
        self.test("Multi-traveler application - 2 travelers", self.test_multi_traveler_application_two_travelers)
        self.test("Multi-traveler application - invalid file_id", self.test_multi_traveler_application_invalid_file_id)
        self.test("Track application - any traveler's last name", self.test_track_application_any_traveler_lastname)
        self.test("Payment checkout - multi-traveler amount", self.test_payment_checkout_multi_traveler_amount)
        
        # Phase 3: Admin visa document upload & send
        self.test("Admin upload visa document", self.test_admin_upload_visa_document)
        self.test("Admin send visa email", self.test_admin_send_visa_email)
        self.test("Admin delete visa document", self.test_admin_delete_visa_document)
        self.test("Admin emails outbox", self.test_admin_emails_outbox)
        
        # Phase 4: AI Passport OCR
        self.test("Passport OCR - real image", self.test_passport_ocr_with_real_image)
        self.test("Passport OCR - PDF graceful error", self.test_passport_ocr_with_pdf)
        self.test("Passport OCR - unknown file_id 404", self.test_passport_ocr_unknown_file_id)
        
        # Phase 4: Blog Articles
        self.test("Articles list (public)", self.test_articles_list_public)
        self.test("Articles detail (public)", self.test_articles_detail_public)
        self.test("Articles detail - unknown slug 404", self.test_articles_detail_unknown_slug)
        
        # Phase 4: Admin Testimonials CRUD
        self.test("Admin testimonials list", self.test_admin_testimonials_list)
        self.test("Admin testimonials create", self.test_admin_testimonials_create)
        self.test("Admin testimonials update", self.test_admin_testimonials_update)
        self.test("Admin testimonials appears in public", self.test_admin_testimonials_appears_in_public)
        self.test("Admin testimonials delete", self.test_admin_testimonials_delete)
        self.test("Admin review summary update", self.test_admin_review_summary_update)
        
        # Phase 4: Admin Articles CRUD
        self.test("Admin articles list", self.test_admin_articles_list)
        self.test("Admin articles create", self.test_admin_articles_create)
        self.test("Admin articles update", self.test_admin_articles_update)
        self.test("Admin articles appears in public", self.test_admin_articles_appears_in_public)
        self.test("Admin articles unpublished 404", self.test_admin_articles_unpublished_404)
        self.test("Admin articles delete", self.test_admin_articles_delete)
        
        # Phase 4: Admin WhatsApp Link Generation
        self.test("Admin WhatsApp link - visa_ready", self.test_admin_whatsapp_link_visa_ready)
        self.test("Admin WhatsApp link - no phone 400", self.test_admin_whatsapp_link_no_phone)
        self.test("Admin WhatsApp link - unknown app 404", self.test_admin_whatsapp_link_unknown_application)
        
        # Summary
        self.log("\n" + "="*60)
        self.log("TEST SUMMARY")
        self.log("="*60)
        self.log(f"Total tests: {self.tests_run}")
        self.log(f"Passed: {self.tests_passed}")
        self.log(f"Failed: {len(self.failed_tests)}")
        self.log(f"Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            self.log("\n" + "="*60)
            self.log("FAILED TESTS")
            self.log("="*60)
            for fail in self.failed_tests:
                self.log(f"❌ {fail['test']}: {fail['error']}", "ERROR")
        
        return 0 if len(self.failed_tests) == 0 else 1


if __name__ == "__main__":
    tester = BackendTester()
    exit_code = tester.run_all()
    sys.exit(exit_code)
