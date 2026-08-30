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
        """GET /api/visa-types"""
        r = requests.get(f"{self.base_url}/visa-types", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert isinstance(data, list), "Expected list of visa types"
        assert len(data) >= 5, f"Expected at least 5 visa types, got {len(data)}"
        for vt in data:
            assert "id" in vt, "Visa type missing id"
            assert "name" in vt, "Visa type missing name"
            assert "price" in vt, "Visa type missing price"
        self.log(f"Found {len(data)} visa types")

    def test_site_content(self):
        """GET /api/content/site"""
        r = requests.get(f"{self.base_url}/content/site", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        required = ["company", "process_steps", "why_us", "faq", "required_documents", "photo_rules", "testimonials", "status_labels"]
        for key in required:
            assert key in data, f"Missing {key} in site content"
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
        """POST /api/applications - valid payload"""
        assert self.test_file_id, "Need uploaded passport file"
        assert self.test_photo_id, "Need uploaded photo file"
        
        payload = {
            "visa_type_id": "visa_30_single",
            "applicant": {
                "first_name": "Ahmet",
                "last_name": "Yilmaz",
                "email": "ahmet.test@example.com",
                "phone": "+905551234567",
                "birth_date": "1990-05-15",
                "gender": "male",
                "nationality": "TR",
                "national_id": "12345678901",
                "passport_no": "U12345678",
                "passport_expiry": "2028-12-31",
                "address_city": "Istanbul"
            },
            "travel": {
                "arrival_date": "2026-03-15",
                "departure_date": "2026-03-25",
                "purpose": "tourism",
                "accommodation": "Burj Al Arab",
                "flight_no": "TK123",
                "notes": "Test application"
            },
            "documents": {
                "passport_file_id": self.test_file_id,
                "photo_file_id": self.test_photo_id,
                "extra_file_ids": []
            },
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
        params = {"code": self.test_reference_code, "last_name": "Yilmaz"}
        r = requests.get(f"{self.base_url}/applications/track", params=params, timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        result = r.json()
        assert result["reference_code"] == self.test_reference_code, "Reference code mismatch"
        assert result["applicant"]["last_name"] == "Yilmaz", "Last name mismatch"
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
        
        # Payments
        self.test("Create payment checkout (valid)", self.test_payment_checkout_valid)
        self.test("Create payment checkout (unknown app)", self.test_payment_checkout_unknown_app)
        self.test("Get payment status", self.test_payment_status)
        
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
