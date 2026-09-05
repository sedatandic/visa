"""Backend API tests for Dubai Vize Online - REGRESSION TESTING for Code Quality Refactoring"""
import requests
import sys
import time
from pathlib import Path

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", ".env"))

ADMIN_LOGIN_EMAIL = os.environ["ADMIN_LOGIN_EMAIL"]
from admin_test_token import admin_token as _admin_token
BASE_URL = os.environ["REACT_APP_BACKEND_URL"].rstrip("/") + "/api"

class MandatoryFieldsTester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.file_id = None
        self.photo_file_id = None
        self.solid_file_id = None
        self.pdf_file_id = None
        
    def log(self, message, status="INFO"):
        symbols = {"PASS": "✅", "FAIL": "❌", "INFO": "🔍", "WARN": "⚠️"}
        print(f"{symbols.get(status, '•')} {message}")
    
    def test_upload_passport(self):
        """Test uploading passport image"""
        self.tests_run += 1
        self.log("Testing passport upload...", "INFO")
        
        passport_path = Path("/app/tests/fixtures/test_passport.png")
        if not passport_path.exists():
            self.log(f"Test passport file not found: {passport_path}", "FAIL")
            return False
        
        try:
            with open(passport_path, "rb") as f:
                files = {"file": ("test_passport.png", f, "image/png")}
                data = {"doc_type": "passport"}
                response = requests.post(
                    f"{BASE_URL}/uploads",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                self.file_id = result.get("file_id")
                self.log(f"Passport uploaded successfully. File ID: {self.file_id}", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"Upload failed with status {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Upload error: {str(e)}", "FAIL")
            return False
    
    def test_passport_ocr(self):
        """Test passport OCR reading"""
        self.tests_run += 1
        self.log("Testing passport OCR (may take 10-30 seconds)...", "INFO")
        
        if not self.file_id:
            self.log("No file_id available for OCR test", "FAIL")
            return False
        
        try:
            response = requests.post(
                f"{BASE_URL}/passport/read",
                data={"file_id": self.file_id},
                timeout=60
            )
            
            if response.status_code != 200:
                self.log(f"OCR request failed with status {response.status_code}: {response.text}", "FAIL")
                return False
            
            result = response.json()
            
            if not result.get("ok"):
                self.log(f"OCR failed: {result.get('message', 'Unknown error')}", "FAIL")
                return False
            
            data = result.get("data", {})
            
            # Verify expected values from test_passport.png
            expected = {
                "first_name": "AHMET",
                "last_name": "YILMAZ",
                "passport_no": "U12345678",
                "birth_date": "1990-08-15",
                "passport_expiry": "2032-01-20",
                "gender": "male",
                "national_id": "12345678901"
            }
            
            all_correct = True
            for key, expected_value in expected.items():
                actual_value = data.get(key)
                if actual_value != expected_value:
                    self.log(f"OCR mismatch for {key}: expected '{expected_value}', got '{actual_value}'", "WARN")
                    all_correct = False
                else:
                    self.log(f"OCR correct for {key}: {actual_value}", "PASS")
            
            if all_correct:
                self.log("All OCR fields match expected values", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log("Some OCR fields don't match expected values", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"OCR error: {str(e)}", "FAIL")
            return False
    
    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        endpoints = [
            "/visa-types",
            "/content/site",
            "/products"
        ]
        
        for endpoint in endpoints:
            self.tests_run += 1
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                if response.status_code == 200:
                    self.log(f"GET {endpoint}: OK", "PASS")
                    self.tests_passed += 1
                else:
                    self.log(f"GET {endpoint}: Failed with status {response.status_code}", "FAIL")
            except Exception as e:
                self.log(f"GET {endpoint}: Error - {str(e)}", "FAIL")
    
    def test_upload_photo(self):
        """Test uploading portrait photo"""
        self.tests_run += 1
        self.log("Testing portrait photo upload...", "INFO")
        
        photo_path = Path("/app/tests/fixtures/test_portrait.png")
        if not photo_path.exists():
            self.log(f"Test photo file not found: {photo_path}", "FAIL")
            return False
        
        try:
            with open(photo_path, "rb") as f:
                files = {"file": ("test_portrait.png", f, "image/png")}
                data = {"doc_type": "photo"}
                response = requests.post(
                    f"{BASE_URL}/uploads",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                self.photo_file_id = result.get("file_id")
                self.log(f"Photo uploaded successfully. File ID: {self.photo_file_id}", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"Photo upload failed with status {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Photo upload error: {str(e)}", "FAIL")
            return False
    
    def test_upload_solid_image(self):
        """Test uploading non-portrait image (solid color)"""
        self.tests_run += 1
        self.log("Testing solid color image upload...", "INFO")
        
        solid_path = Path("/app/tests/fixtures/solid_blue.png")
        if not solid_path.exists():
            self.log(f"Test solid image not found: {solid_path}", "FAIL")
            return False
        
        try:
            with open(solid_path, "rb") as f:
                files = {"file": ("solid_blue.png", f, "image/png")}
                data = {"doc_type": "photo"}
                response = requests.post(
                    f"{BASE_URL}/uploads",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                self.solid_file_id = result.get("file_id")
                self.log(f"Solid image uploaded successfully. File ID: {self.solid_file_id}", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"Solid image upload failed with status {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Solid image upload error: {str(e)}", "FAIL")
            return False
    
    def test_upload_pdf(self):
        """Test uploading PDF document"""
        self.tests_run += 1
        self.log("Testing PDF upload...", "INFO")
        
        pdf_path = Path("/app/tests/fixtures/test_document.pdf")
        if not pdf_path.exists():
            self.log(f"Test PDF not found: {pdf_path}", "FAIL")
            return False
        
        try:
            with open(pdf_path, "rb") as f:
                files = {"file": ("test_document.pdf", f, "application/pdf")}
                data = {"doc_type": "photo"}
                response = requests.post(
                    f"{BASE_URL}/uploads",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                self.pdf_file_id = result.get("file_id")
                self.log(f"PDF uploaded successfully. File ID: {self.pdf_file_id}", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"PDF upload failed with status {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"PDF upload error: {str(e)}", "FAIL")
            return False
    
    def test_photo_check_valid(self):
        """Test photo validation with portrait image"""
        self.tests_run += 1
        self.log("Testing photo validation with portrait (may take 10-30 seconds)...", "INFO")
        
        if not self.photo_file_id:
            self.log("No photo file_id available for validation test", "FAIL")
            return False
        
        try:
            response = requests.post(
                f"{BASE_URL}/photo/check",
                data={"file_id": self.photo_file_id},
                timeout=60
            )
            
            if response.status_code != 200:
                self.log(f"Photo check failed with status {response.status_code}: {response.text}", "FAIL")
                return False
            
            result = response.json()
            
            # Verify expected keys
            required_keys = ["checked", "ok", "is_photo", "checks", "failed", "issues", "advice", "score"]
            missing_keys = [k for k in required_keys if k not in result]
            
            if missing_keys:
                self.log(f"Missing keys in response: {missing_keys}", "FAIL")
                return False
            
            if not result.get("checked"):
                self.log(f"Photo was not checked: {result.get('message', 'Unknown reason')}", "FAIL")
                return False
            
            self.log(f"Photo check completed: ok={result['ok']}, is_photo={result['is_photo']}, score={result['score']}", "PASS")
            self.log(f"Failed checks: {result['failed']}", "INFO")
            self.log(f"Issues: {result['issues']}", "INFO")
            
            self.tests_passed += 1
            return True
                
        except Exception as e:
            self.log(f"Photo check error: {str(e)}", "FAIL")
            return False
    
    def test_photo_check_non_portrait(self):
        """Test photo validation with non-portrait image (solid color)"""
        self.tests_run += 1
        self.log("Testing photo validation with non-portrait image...", "INFO")
        
        if not self.solid_file_id:
            self.log("No solid image file_id available for validation test", "FAIL")
            return False
        
        try:
            response = requests.post(
                f"{BASE_URL}/photo/check",
                data={"file_id": self.solid_file_id},
                timeout=60
            )
            
            if response.status_code != 200:
                self.log(f"Photo check failed with status {response.status_code}: {response.text}", "FAIL")
                return False
            
            result = response.json()
            
            if not result.get("checked"):
                self.log(f"Photo was not checked: {result.get('message', 'Unknown reason')}", "FAIL")
                return False
            
            # For non-portrait, we expect is_photo=false and ok=false
            if not result.get("is_photo") and not result.get("ok"):
                self.log(f"Non-portrait correctly detected: is_photo={result['is_photo']}, ok={result['ok']}", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"Non-portrait not detected correctly: is_photo={result.get('is_photo')}, ok={result.get('ok')}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Photo check error: {str(e)}", "FAIL")
            return False
    
    def test_photo_check_invalid_file_id(self):
        """Test photo validation with invalid file_id (should return 404)"""
        self.tests_run += 1
        self.log("Testing photo validation with invalid file_id...", "INFO")
        
        try:
            response = requests.post(
                f"{BASE_URL}/photo/check",
                data={"file_id": "invalid-file-id-12345"},
                timeout=10
            )
            
            if response.status_code == 404:
                self.log(f"Invalid file_id correctly returned 404", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"Expected 404, got {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Photo check error: {str(e)}", "FAIL")
            return False
    
    def test_photo_check_pdf(self):
        """Test photo validation with PDF (should return checked=false, reason='pdf')"""
        self.tests_run += 1
        self.log("Testing photo validation with PDF...", "INFO")
        
        if not self.pdf_file_id:
            self.log("No PDF file_id available for validation test", "FAIL")
            return False
        
        try:
            response = requests.post(
                f"{BASE_URL}/photo/check",
                data={"file_id": self.pdf_file_id},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Photo check failed with status {response.status_code}: {response.text}", "FAIL")
                return False
            
            result = response.json()
            
            # For PDF, we expect checked=false and reason='pdf'
            if not result.get("checked") and result.get("reason") == "pdf":
                self.log(f"PDF correctly handled: checked={result['checked']}, reason={result['reason']}", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"PDF not handled correctly: checked={result.get('checked')}, reason={result.get('reason')}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Photo check error: {str(e)}", "FAIL")
            return False
    
    def test_application_with_new_fields(self):
        """Test creating application with new mandatory fields"""
        self.tests_run += 1
        self.log("Testing application creation with marital_status, profession, mother_name, father_name...", "INFO")
        
        if not self.file_id or not self.photo_file_id:
            self.log("Missing file IDs for application test", "FAIL")
            return False, None
        
        try:
            payload = {
                "contact": {
                    "full_name": "AHMET YILMAZ",
                    "email": f"test_{int(time.time())}@test.com",
                    "phone": "05551234567",
                    "address_city": "Istanbul",
                    "whatsapp_optin": False
                },
                "travelers": [{
                    "first_name": "AHMET",
                    "last_name": "YILMAZ",
                    "birth_date": "1990-08-15",
                    "gender": "male",
                    "applicant_type": "adult",
                    "nationality": "TR",
                    "national_id": "12345678901",
                    "passport_no": "U12345678",
                    "passport_expiry": "2032-01-20",
                    "marital_status": "married",
                    "profession": "Engineer",
                    "mother_name": "AYSE YILMAZ",
                    "father_name": "MEHMET YILMAZ",
                    "visa_type_id": "visa_30_single",
                    "passport_file_id": self.file_id,
                    "photo_file_id": self.photo_file_id
                }],
                "travel": {
                    "arrival_date": "2026-03-15",
                    "departure_date": "2026-03-25",
                    "purpose": "tourism",
                    "birth_country": "TR"
                },
                "addons": {
                    "express": False,
                    "insurance": False
                },
                "store_items": [],
                "extra_documents": {},
                "kvkk_accepted": True
            }
            
            response = requests.post(
                f"{BASE_URL}/applications",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                app_id = result.get("id")
                ref_code = result.get("reference_code")
                self.log(f"Application created successfully. ID: {app_id}, Ref: {ref_code}", "PASS")
                
                # Verify new fields in response
                traveler = result.get("travelers", [{}])[0]
                if (traveler.get("marital_status") == "married" and 
                    traveler.get("profession") == "Engineer" and
                    traveler.get("mother_name") == "AYSE YILMAZ" and
                    traveler.get("father_name") == "MEHMET YILMAZ"):
                    self.log("New fields correctly saved in application", "PASS")
                    self.tests_passed += 1
                    return True, app_id
                else:
                    self.log(f"New fields not saved correctly: {traveler}", "FAIL")
                    return False, app_id
            else:
                self.log(f"Application creation failed with status {response.status_code}: {response.text}", "FAIL")
                return False, None
                
        except Exception as e:
            self.log(f"Application creation error: {str(e)}", "FAIL")
            return False, None
    
    def test_invalid_marital_status(self):
        """Test that invalid marital_status returns 422"""
        self.tests_run += 1
        self.log("Testing invalid marital_status validation...", "INFO")
        
        if not self.file_id or not self.photo_file_id:
            self.log("Missing file IDs for validation test", "FAIL")
            return False
        
        try:
            payload = {
                "contact": {
                    "full_name": "TEST USER",
                    "email": f"test_{int(time.time())}@test.com",
                    "phone": "05551234567"
                },
                "travelers": [{
                    "first_name": "TEST",
                    "last_name": "USER",
                    "birth_date": "1990-01-01",
                    "gender": "male",
                    "applicant_type": "adult",
                    "passport_no": "T12345678",
                    "passport_expiry": "2030-01-01",
                    "marital_status": "foo",  # Invalid value
                    "profession": "Engineer",
                    "mother_name": "MOTHER",
                    "father_name": "FATHER",
                    "visa_type_id": "visa_30_single",
                    "passport_file_id": self.file_id,
                    "photo_file_id": self.photo_file_id
                }],
                "travel": {
                    "arrival_date": "2026-03-15",
                    "departure_date": "2026-03-25",
                    "birth_country": "TR"
                },
                "addons": {},
                "extra_documents": {},
                "kvkk_accepted": True
            }
            
            response = requests.post(
                f"{BASE_URL}/applications",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 422:
                self.log(f"Invalid marital_status correctly returned 422", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"Expected 422, got {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Validation test error: {str(e)}", "FAIL")
            return False
    
    def test_backward_compatibility(self):
        """Test that application works without new fields (defaults applied)"""
        self.tests_run += 1
        self.log("Testing backward compatibility (fields not sent, defaults applied)...", "INFO")
        
        if not self.file_id or not self.photo_file_id:
            self.log("Missing file IDs for backward compatibility test", "FAIL")
            return False
        
        try:
            payload = {
                "contact": {
                    "full_name": "LEGACY USER",
                    "email": f"legacy_{int(time.time())}@test.com",
                    "phone": "05551234567"
                },
                "travelers": [{
                    "first_name": "LEGACY",
                    "last_name": "USER",
                    "birth_date": "1990-01-01",
                    "gender": "female",
                    "applicant_type": "adult",
                    "passport_no": "L12345678",
                    "passport_expiry": "2030-01-01",
                    # NOT sending marital_status, profession, mother_name, father_name
                    "visa_type_id": "visa_30_single",
                    "passport_file_id": self.file_id,
                    "photo_file_id": self.photo_file_id
                }],
                "travel": {
                    "arrival_date": "2026-03-15",
                    "departure_date": "2026-03-25",
                    "birth_country": "TR"
                },
                "addons": {},
                "extra_documents": {},
                "kvkk_accepted": True
            }
            
            response = requests.post(
                f"{BASE_URL}/applications",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                traveler = result.get("travelers", [{}])[0]
                
                # Check defaults: marital_status='single', others empty
                if (traveler.get("marital_status") == "single" and
                    traveler.get("profession") == "" and
                    traveler.get("mother_name") == "" and
                    traveler.get("father_name") == ""):
                    self.log("Backward compatibility OK: defaults applied (marital_status='single', others empty)", "PASS")
                    self.tests_passed += 1
                    return True
                else:
                    self.log(f"Defaults not applied correctly: {traveler}", "FAIL")
                    return False
            else:
                self.log(f"Backward compatibility test failed with status {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Backward compatibility test error: {str(e)}", "FAIL")
            return False
    
    def test_admin_login(self):
        """Test admin login and get token"""
        self.tests_run += 1
        self.log("Testing admin login...", "INFO")
        
        try:
            token = _admin_token()
            probe = requests.get(
                f"{BASE_URL}/admin/stats",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if probe.status_code == 200:
                self.log("Admin token accepted (OTP-only login, token signed locally)", "PASS")
                self.tests_passed += 1
                return True, token
            self.log(f"Admin token rejected with status {probe.status_code}: {probe.text}", "FAIL")
            return False, None
                
        except Exception as e:
            self.log(f"Admin login error: {str(e)}", "FAIL")
            return False, None
    
    def test_admin_application_detail(self, app_id, admin_token):
        """Test admin application detail endpoint shows new fields"""
        self.tests_run += 1
        self.log(f"Testing admin application detail for app {app_id}...", "INFO")
        
        if not admin_token:
            self.log("No admin token available", "FAIL")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/applications/{app_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                app = result.get("application", {})
                traveler = app.get("travelers", [{}])[0]
                
                # Check if new fields are present
                if (traveler.get("marital_status") and
                    traveler.get("profession") and
                    traveler.get("mother_name") and
                    traveler.get("father_name")):
                    self.log(f"Admin detail shows new fields: marital={traveler['marital_status']}, profession={traveler['profession']}", "PASS")
                    self.tests_passed += 1
                    return True
                else:
                    self.log(f"Admin detail missing new fields: {traveler}", "FAIL")
                    return False
            else:
                self.log(f"Admin detail failed with status {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Admin detail error: {str(e)}", "FAIL")
            return False
    
    def test_zami_mapping(self, admin_token):
        """Test Zami mapping includes new traveler fields"""
        self.tests_run += 1
        self.log("Testing Zami mapping for new traveler fields...", "INFO")
        
        if not admin_token:
            self.log("No admin token available", "FAIL")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/zami/config",
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                traveler_fields_list = result.get("traveler_fields", [])
                
                # Check if new fields are in the list
                field_keys = [f["key"] for f in traveler_fields_list]
                
                required_fields = ["marital_status", "marital_status_label", "profession", "mother_name", "father_name"]
                missing = [f for f in required_fields if f not in field_keys]
                
                if not missing:
                    self.log(f"Zami mapping includes all new traveler fields", "PASS")
                    self.tests_passed += 1
                    return True
                else:
                    self.log(f"Zami mapping missing fields: {missing}", "FAIL")
                    return False
            else:
                self.log(f"Zami config failed with status {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Zami mapping test error: {str(e)}", "FAIL")
            return False
    
    def test_whatsapp_settings(self, admin_token):
        """REGRESSION: Test WhatsApp settings GET returns all fields"""
        self.tests_run += 1
        self.log("Testing WhatsApp settings GET (all fields)...", "INFO")
        
        if not admin_token:
            self.log("No admin token available", "FAIL")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/whatsapp/settings",
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"WhatsApp settings GET failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            settings = result.get("settings", {})
            
            # Check all required fields
            required_fields = [
                "enabled", "provider", "template_text", "only_optin",
                "meta_phone_number_id", "meta_template_name", "meta_template_language", "meta_api_version",
                "twilio_whatsapp_from", "twilio_content_sid", "twilio_account_sid",
                "has_meta_token", "has_twilio_token"
            ]
            
            missing = [f for f in required_fields if f not in settings]
            
            if missing:
                self.log(f"WhatsApp settings missing fields: {missing}", "FAIL")
                return False
            
            self.log(f"WhatsApp settings has all required fields", "PASS")
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"WhatsApp settings test error: {str(e)}", "FAIL")
            return False
    
    def test_whatsapp_settings_update(self, admin_token):
        """REGRESSION: Test WhatsApp settings PUT updates and persists"""
        self.tests_run += 1
        self.log("Testing WhatsApp settings PUT (update & persist)...", "INFO")
        
        if not admin_token:
            self.log("No admin token available", "FAIL")
            return False
        
        try:
            # Update settings
            update_payload = {
                "provider": "manual",
                "template_text": "Test template {name} {status}",
                "only_optin": True
            }
            
            response = requests.put(
                f"{BASE_URL}/admin/whatsapp/settings",
                headers={"Authorization": f"Bearer {admin_token}"},
                json=update_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"WhatsApp settings PUT failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            settings = result.get("settings", {})
            
            # Verify updates
            if (settings.get("provider") == "manual" and
                "Test template" in settings.get("template_text", "") and
                settings.get("only_optin")):
                self.log(f"WhatsApp settings updated successfully", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"WhatsApp settings not updated correctly", "FAIL")
                return False
            
        except Exception as e:
            self.log(f"WhatsApp settings update error: {str(e)}", "FAIL")
            return False
    
    def test_content_site_structure(self):
        """REGRESSION: Test GET /api/content/site returns all keys"""
        self.tests_run += 1
        self.log("Testing GET /api/content/site structure...", "INFO")
        
        try:
            response = requests.get(f"{BASE_URL}/content/site", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Content site GET failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            
            # Check all required keys
            required_keys = [
                "company", "agency_info", "bank_transfer", "testimonials",
                "review_summary", "articles", "addons", "fx", "family_discount_tiers",
                "promo", "status_labels", "visa_categories", "process_steps"
            ]
            
            missing = [k for k in required_keys if k not in result]
            
            if missing:
                self.log(f"Content site missing keys: {missing}", "FAIL")
                return False
            
            # Check agency_info.items is populated
            agency_items = result.get("agency_info", {}).get("items", [])
            if not agency_items:
                self.log(f"agency_info.items is empty", "FAIL")
                return False
            
            self.log(f"Content site has all required keys and agency_info.items populated", "PASS")
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Content site test error: {str(e)}", "FAIL")
            return False
    
    def test_pricing_quote_combinations(self):
        """REGRESSION: Test POST /api/pricing/quote with different combinations"""
        self.tests_run += 1
        self.log("Testing pricing quote with various combinations...", "INFO")
        
        try:
            # Test case (a): single traveler, no discount
            payload_a = {
                "visa_type_ids": ["visa_30_single"],
                "addons": {"express": False},
                "store_items": [],
                "arrival_date": "2026-03-15",
                "departure_date": "2026-03-25"
            }
            
            response_a = requests.post(f"{BASE_URL}/pricing/quote", json=payload_a, timeout=10)
            
            if response_a.status_code != 200:
                self.log(f"Pricing quote (single traveler) failed: {response_a.status_code}", "FAIL")
                return False
            
            result_a = response_a.json()
            
            if result_a.get("family_discount") != 0:
                self.log(f"Single traveler should have 0 family discount, got {result_a.get('family_discount')}", "FAIL")
                return False
            
            # Test case (b): 2+ travelers, 10% family discount
            payload_b = {
                "visa_type_ids": ["visa_30_single", "visa_30_single"],
                "addons": {"express": False},
                "store_items": [],
                "arrival_date": "2026-03-15",
                "departure_date": "2026-03-25"
            }
            
            response_b = requests.post(f"{BASE_URL}/pricing/quote", json=payload_b, timeout=10)
            
            if response_b.status_code != 200:
                self.log(f"Pricing quote (2 travelers) failed: {response_b.status_code}", "FAIL")
                return False
            
            result_b = response_b.json()
            
            if result_b.get("family_discount_rate") != 0.10:
                self.log(f"2 travelers should have 10% family discount, got {result_b.get('family_discount_rate')}", "FAIL")
                return False
            
            self.log(f"Pricing quote combinations working correctly", "PASS")
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Pricing quote test error: {str(e)}", "FAIL")
            return False
    
    def test_db_serialization_no_objectid(self):
        """REGRESSION: Test that no ObjectId leaks in responses (_id field)"""
        self.tests_run += 1
        self.log("Testing DB serialization (no ObjectId/_id in responses)...", "INFO")
        
        try:
            # Test multiple endpoints for ObjectId leakage
            endpoints = [
                "/content/site",
                "/visa-types",
                "/articles"
            ]
            
            for endpoint in endpoints:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                
                if response.status_code != 200:
                    continue
                
                result = response.json()
                result_str = str(result)
                
                # Check for _id field (should not be present)
                if '"_id"' in result_str or "'_id'" in result_str:
                    self.log(f"ObjectId/_id found in {endpoint} response", "FAIL")
                    return False
            
            self.log(f"No ObjectId/_id leakage in responses", "PASS")
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"DB serialization test error: {str(e)}", "FAIL")
            return False
    
    def test_tracking_lastname_validation(self):
        """REGRESSION: Test tracking with correct/wrong/empty last name"""
        self.tests_run += 1
        self.log("Testing tracking last name validation...", "INFO")
        
        # First create an application to track
        if not self.file_id or not self.photo_file_id:
            self.log("Missing file IDs for tracking test", "FAIL")
            return False
        
        try:
            # Create application
            payload = {
                "contact": {
                    "full_name": "TRACKING TEST USER",
                    "email": f"track_{int(time.time())}@test.com",
                    "phone": "05551234567"
                },
                "travelers": [{
                    "first_name": "TRACKING",
                    "last_name": "TESTUSER",
                    "birth_date": "1990-01-01",
                    "gender": "male",
                    "applicant_type": "adult",
                    "passport_no": "T99999999",
                    "passport_expiry": "2030-01-01",
                    "marital_status": "single",
                    "profession": "Engineer",
                    "mother_name": "MOTHER",
                    "father_name": "FATHER",
                    "visa_type_id": "visa_30_single",
                    "passport_file_id": self.file_id,
                    "photo_file_id": self.photo_file_id
                }],
                "travel": {
                    "arrival_date": "2026-03-15",
                    "departure_date": "2026-03-25",
                    "birth_country": "TR"
                },
                "addons": {},
                "extra_documents": {},
                "kvkk_accepted": True
            }
            
            response = requests.post(f"{BASE_URL}/applications", json=payload, timeout=30)
            
            if response.status_code != 200:
                self.log(f"Application creation failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            ref_code = result.get("reference_code")
            
            # Test (a): Correct last name -> 200
            response_correct = requests.get(
                f"{BASE_URL}/applications/track",
                params={"code": ref_code, "last_name": "TESTUSER"},
                timeout=10
            )
            
            if response_correct.status_code != 200:
                self.log(f"Tracking with correct last name failed: {response_correct.status_code}", "FAIL")
                return False
            
            # Test (b): Wrong last name -> 404
            response_wrong = requests.get(
                f"{BASE_URL}/applications/track",
                params={"code": ref_code, "last_name": "WRONGNAME"},
                timeout=10
            )
            
            if response_wrong.status_code != 404:
                self.log(f"Tracking with wrong last name should return 404, got {response_wrong.status_code}", "FAIL")
                return False
            
            # Test (c): Empty last name -> 400
            response_empty = requests.get(
                f"{BASE_URL}/applications/track",
                params={"code": ref_code, "last_name": ""},
                timeout=10
            )
            
            if response_empty.status_code != 400:
                self.log(f"Tracking with empty last name should return 400, got {response_empty.status_code}", "FAIL")
                return False
            
            # Test (d): Last name from contact.full_name (last word) should also work
            response_contact = requests.get(
                f"{BASE_URL}/applications/track",
                params={"code": ref_code, "last_name": "USER"},
                timeout=10
            )
            
            if response_contact.status_code != 200:
                self.log(f"Tracking with contact last name failed: {response_contact.status_code}", "FAIL")
                return False
            
            self.log(f"Tracking last name validation working correctly", "PASS")
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Tracking validation test error: {str(e)}", "FAIL")
            return False
    
    def test_zami_config_structure(self, admin_token):
        """REGRESSION: Test GET /api/admin/zami/config structure"""
        self.tests_run += 1
        self.log("Testing Zami config structure...", "INFO")
        
        if not admin_token:
            self.log("No admin token available", "FAIL")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/zami/config",
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Zami config GET failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            
            # Check required keys
            required_keys = [
                "settings", "mapping", "session", "global_fields", "traveler_fields",
                "captured", "suggestions"
            ]
            
            missing = [k for k in required_keys if k not in result]
            
            if missing:
                self.log(f"Zami config missing keys: {missing}", "FAIL")
                return False
            
            # Check captured structure
            captured = result.get("captured", {})
            if "form" not in captured or "status" not in captured:
                self.log(f"Zami config captured missing form/status", "FAIL")
                return False
            
            # Check form structure
            form = captured.get("form", {})
            if not all(k in form for k in ["url", "fields", "captured_at"]):
                self.log(f"Zami config captured.form missing keys", "FAIL")
                return False
            
            # Check status structure
            status = captured.get("status", {})
            if not all(k in status for k in ["url", "fields", "sample_text", "captured_at"]):
                self.log(f"Zami config captured.status missing keys", "FAIL")
                return False
            
            self.log(f"Zami config structure correct", "PASS")
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Zami config test error: {str(e)}", "FAIL")
            return False
    
    def test_zami_candidates_structure(self, admin_token):
        """REGRESSION: Test GET /api/admin/zami/candidates structure"""
        self.tests_run += 1
        self.log("Testing Zami candidates structure...", "INFO")
        
        if not admin_token:
            self.log("No admin token available", "FAIL")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/zami/candidates",
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Zami candidates GET failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            items = result.get("items", [])
            
            # Check structure of each item
            if items:
                item = items[0]
                required_fields = [
                    "id", "reference_code", "full_name", "email", "traveler_count",
                    "status", "payment_status", "created_at", "zami_reference",
                    "zami_status", "zami_transferred_at"
                ]
                
                missing = [f for f in required_fields if f not in item]
                
                if missing:
                    self.log(f"Zami candidate item missing fields: {missing}", "FAIL")
                    return False
            
            self.log(f"Zami candidates structure correct", "PASS")
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Zami candidates test error: {str(e)}", "FAIL")
            return False
    
    def test_zami_readiness(self, admin_token):
        """REGRESSION: Test GET /api/admin/zami/readiness"""
        self.tests_run += 1
        self.log("Testing Zami readiness endpoint...", "INFO")
        
        if not admin_token:
            self.log("No admin token available", "FAIL")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/zami/readiness",
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Zami readiness GET failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            
            # Check required keys
            if not all(k in result for k in ["checks", "ready_bookmarklet", "ready_robot"]):
                self.log(f"Zami readiness missing keys", "FAIL")
                return False
            
            self.log(f"Zami readiness endpoint working", "PASS")
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Zami readiness test error: {str(e)}", "FAIL")
            return False
    
    def test_zami_bookmarklet_js(self):
        """REGRESSION: Test GET /api/zami/bookmarklet.js returns 200 with correct BASE URL"""
        self.tests_run += 1
        self.log("Testing Zami bookmarklet.js...", "INFO")
        
        try:
            response = requests.get(f"{BASE_URL}/zami/bookmarklet.js", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Zami bookmarklet.js GET failed: {response.status_code}", "FAIL")
                return False
            
            content = response.text
            
            # Check if BASE URL is present (should be replaced from __BASE__)
            if "__BASE__" in content:
                self.log(f"Zami bookmarklet.js still contains __BASE__ placeholder", "FAIL")
                return False
            
            # Check if it contains expected JavaScript (marka adı: Dubai Vize Online)
            if "Dubai Vize Online" not in content or "function" not in content:
                self.log(f"Zami bookmarklet.js content seems invalid", "FAIL")
                return False
            
            self.log(f"Zami bookmarklet.js working correctly", "PASS")
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Zami bookmarklet.js test error: {str(e)}", "FAIL")
            return False
    
    def test_zami_capture_js(self):
        """REGRESSION: Test GET /api/zami/capture.js returns 200 with correct BASE URL"""
        self.tests_run += 1
        self.log("Testing Zami capture.js...", "INFO")
        
        try:
            response = requests.get(f"{BASE_URL}/zami/capture.js", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Zami capture.js GET failed: {response.status_code}", "FAIL")
                return False
            
            content = response.text
            
            # Check if BASE URL is present (should be replaced from __BASE__)
            if "__BASE__" in content:
                self.log(f"Zami capture.js still contains __BASE__ placeholder", "FAIL")
                return False
            
            # Check if it contains expected JavaScript
            if "function" not in content:
                self.log(f"Zami capture.js content seems invalid", "FAIL")
                return False
            
            self.log(f"Zami capture.js working correctly", "PASS")
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Zami capture.js test error: {str(e)}", "FAIL")
            return False
    
    def test_zami_mapping_data_preservation(self, admin_token):
        """CRITICAL BUG FIX: Test that Zami mapping preserves fields not sent in PUT request"""
        self.tests_run += 1
        self.log("Testing Zami mapping data preservation (CRITICAL BUG FIX)...", "INFO")
        
        if not admin_token:
            self.log("No admin token available", "FAIL")
            return False
        
        try:
            # First, restore original mapping using zami_save_mapping.py
            import subprocess
            result = subprocess.run(
                ["python", "/app/scripts/zami_save_mapping.py"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.log(f"Failed to restore original mapping: {result.stderr}", "FAIL")
                return False
            
            time.sleep(1)
            
            # Get current mapping to verify restoration
            response = requests.get(
                f"{BASE_URL}/admin/zami/config",
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Failed to get Zami config: {response.status_code}", "FAIL")
                return False
            
            config = response.json()
            original_mapping = config.get("mapping", {})
            
            # Verify original mapping has expected fields
            expected_constants_count = 7
            expected_upload_targets_count = 2
            expected_validate_selector = 'button:has-text("CHECK")'
            expected_status_submit_selector = 'button:has-text("SEARCH")'
            expected_status_search_field = "passport"
            expected_helper_selectors_count = 1
            
            constants = original_mapping.get("constants", {})
            upload_targets = original_mapping.get("upload_targets", [])
            validate_selector = original_mapping.get("validate_selector", "")
            
            if len(constants) != expected_constants_count:
                self.log(f"Original mapping constants count mismatch: expected {expected_constants_count}, got {len(constants)}", "FAIL")
                return False
            
            if len(upload_targets) != expected_upload_targets_count:
                self.log(f"Original mapping upload_targets count mismatch: expected {expected_upload_targets_count}, got {len(upload_targets)}", "FAIL")
                return False
            
            if validate_selector != expected_validate_selector:
                self.log(f"Original mapping validate_selector mismatch: expected '{expected_validate_selector}', got '{validate_selector}'", "FAIL")
                return False
            
            self.log(f"Original mapping verified: constants={len(constants)}, upload_targets={len(upload_targets)}, validate_selector='{validate_selector}'", "PASS")
            
            # Test (a): PUT with ONLY form_url+fields+traveler_fields+status_url (NOT sending constants, upload_targets, etc.)
            # These fields should be PRESERVED from original mapping
            partial_update = {
                "form_url": "https://visa.zamitours.ae/?_=203&s=smrtch.edit",
                "fields": {
                    "travel.arrival_date_dmy_dash": '[name="ad"]',
                    "reference_code": '[name="dr_rf"]'
                },
                "traveler_fields": {
                    "first_name": '[name="fn"]',
                    "last_name": '[name="ln"]'
                },
                "status_url": "https://visa.zamitours.ae/?_=203&s=vs.search"
            }
            
            response = requests.put(
                f"{BASE_URL}/admin/zami/mapping",
                headers={"Authorization": f"Bearer {admin_token}"},
                json=partial_update,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Partial mapping update failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            updated_mapping = result.get("mapping", {})
            
            # Verify that constants, upload_targets, validate_selector, etc. are PRESERVED
            updated_constants = updated_mapping.get("constants", {})
            updated_upload_targets = updated_mapping.get("upload_targets", [])
            updated_validate_selector = updated_mapping.get("validate_selector", "")
            updated_status_submit_selector = updated_mapping.get("status_submit_selector", "")
            updated_status_search_field = updated_mapping.get("status_search_field", "")
            updated_helper_selectors = updated_mapping.get("helper_selectors", [])
            
            if len(updated_constants) != expected_constants_count:
                self.log(f"FAIL: constants NOT preserved after partial update: expected {expected_constants_count}, got {len(updated_constants)}", "FAIL")
                return False
            
            if len(updated_upload_targets) != expected_upload_targets_count:
                self.log(f"FAIL: upload_targets NOT preserved after partial update: expected {expected_upload_targets_count}, got {len(updated_upload_targets)}", "FAIL")
                return False
            
            if updated_validate_selector != expected_validate_selector:
                self.log(f"FAIL: validate_selector NOT preserved after partial update: expected '{expected_validate_selector}', got '{updated_validate_selector}'", "FAIL")
                return False
            
            if updated_status_submit_selector != expected_status_submit_selector:
                self.log(f"FAIL: status_submit_selector NOT preserved after partial update: expected '{expected_status_submit_selector}', got '{updated_status_submit_selector}'", "FAIL")
                return False
            
            if updated_status_search_field != expected_status_search_field:
                self.log(f"FAIL: status_search_field NOT preserved after partial update: expected '{expected_status_search_field}', got '{updated_status_search_field}'", "FAIL")
                return False
            
            if len(updated_helper_selectors) != expected_helper_selectors_count:
                self.log(f"FAIL: helper_selectors NOT preserved after partial update: expected {expected_helper_selectors_count}, got {len(updated_helper_selectors)}", "FAIL")
                return False
            
            self.log(f"PASS: All fields preserved after partial update: constants={len(updated_constants)}, upload_targets={len(updated_upload_targets)}, validate_selector='{updated_validate_selector}'", "PASS")
            
            # Test (b): Explicitly sending constants:{} should CLEAR it (intentional delete)
            clear_constants_update = {
                "form_url": "https://visa.zamitours.ae/?_=203&s=smrtch.edit",
                "constants": {}
            }
            
            response = requests.put(
                f"{BASE_URL}/admin/zami/mapping",
                headers={"Authorization": f"Bearer {admin_token}"},
                json=clear_constants_update,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Clear constants update failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            cleared_mapping = result.get("mapping", {})
            cleared_constants = cleared_mapping.get("constants", {})
            
            if len(cleared_constants) != 0:
                self.log(f"FAIL: constants NOT cleared when explicitly sent as empty: got {len(cleared_constants)}", "FAIL")
                return False
            
            self.log(f"PASS: constants cleared when explicitly sent as empty", "PASS")
            
            # Test (c): Sending validate_selector:'' (empty string) should ACCEPT it (not revert to default)
            empty_validate_update = {
                "form_url": "https://visa.zamitours.ae/?_=203&s=smrtch.edit",
                "validate_selector": ""
            }
            
            response = requests.put(
                f"{BASE_URL}/admin/zami/mapping",
                headers={"Authorization": f"Bearer {admin_token}"},
                json=empty_validate_update,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Empty validate_selector update failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            empty_validate_mapping = result.get("mapping", {})
            empty_validate_selector = empty_validate_mapping.get("validate_selector", "NOT_FOUND")
            
            if empty_validate_selector != "":
                self.log(f"FAIL: validate_selector NOT accepted as empty string: got '{empty_validate_selector}'", "FAIL")
                return False
            
            self.log(f"PASS: validate_selector accepted as empty string", "PASS")
            
            # Restore original mapping
            result = subprocess.run(
                ["python", "/app/scripts/zami_save_mapping.py"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.log(f"Failed to restore original mapping after tests: {result.stderr}", "WARN")
            else:
                self.log(f"Original mapping restored successfully", "PASS")
            
            time.sleep(1)
            
            # Verify restoration
            response = requests.get(
                f"{BASE_URL}/admin/zami/config",
                headers={"Authorization": f"Bearer {admin_token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                config = response.json()
                restored_mapping = config.get("mapping", {})
                restored_constants = restored_mapping.get("constants", {})
                restored_validate_selector = restored_mapping.get("validate_selector", "")
                
                if len(restored_constants) == expected_constants_count and restored_validate_selector == expected_validate_selector:
                    self.log(f"Restoration verified: constants={len(restored_constants)}, validate_selector='{restored_validate_selector}'", "PASS")
                else:
                    self.log(f"Restoration verification failed: constants={len(restored_constants)}, validate_selector='{restored_validate_selector}'", "WARN")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Zami mapping preservation test error: {str(e)}", "FAIL")
            return False
    
    def test_brand_name_in_backend(self):
        """Test that brand name is 'Dubai Vize Online' not 'VizeAtlas' in backend texts"""
        self.tests_run += 1
        self.log("Testing brand name in backend texts...", "INFO")
        
        try:
            # Test bookmarklet.js
            response = requests.get(f"{BASE_URL}/zami/bookmarklet.js", timeout=10)
            if response.status_code == 200:
                content = response.text
                if "VizeAtlas" in content and "Dubai Vize Online" not in content:
                    self.log(f"FAIL: bookmarklet.js still contains 'VizeAtlas' instead of 'Dubai Vize Online'", "FAIL")
                    return False
                elif "Dubai Vize Online" in content:
                    self.log(f"PASS: bookmarklet.js contains 'Dubai Vize Online'", "PASS")
                else:
                    self.log(f"WARN: bookmarklet.js doesn't contain brand name", "WARN")
            
            # Test capture.js
            response = requests.get(f"{BASE_URL}/zami/capture.js", timeout=10)
            if response.status_code == 200:
                content = response.text
                if "VizeAtlas" in content and "Dubai Vize Online" not in content:
                    self.log(f"FAIL: capture.js still contains 'VizeAtlas' instead of 'Dubai Vize Online'", "FAIL")
                    return False
                elif "Dubai Vize Online" in content:
                    self.log(f"PASS: capture.js contains 'Dubai Vize Online'", "PASS")
                else:
                    self.log(f"WARN: capture.js doesn't contain brand name", "WARN")
            
            # Test content/site
            response = requests.get(f"{BASE_URL}/content/site", timeout=10)
            if response.status_code == 200:
                result = response.json()
                company = result.get("company", {})
                brand = company.get("brand", "")
                brand_suffix = company.get("brandSuffix", "")
                
                if "VizeAtlas" in brand:
                    self.log(f"FAIL: content/site company.brand still contains 'VizeAtlas': '{brand}'", "FAIL")
                    return False
                elif "Dubai Vize" in brand:
                    self.log(f"PASS: content/site company.brand is '{brand} {brand_suffix}'", "PASS")
                else:
                    self.log(f"WARN: content/site company.brand is '{brand}'", "WARN")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            self.log(f"Brand name test error: {str(e)}", "FAIL")
            return False
    
    def test_application_without_gender(self):
        """Test creating application WITHOUT gender field (new behavior)"""
        self.tests_run += 1
        self.log("Testing application creation WITHOUT gender (gender optional)...", "INFO")
        
        if not self.file_id or not self.photo_file_id:
            self.log("Missing file IDs for application test", "FAIL")
            return False, None
        
        try:
            payload = {
                "contact": {
                    "full_name": "NO GENDER TEST",
                    "email": f"nogender_{int(time.time())}@test.com",
                    "phone": "05551234567",
                    "address_city": "Istanbul",
                    "whatsapp_optin": False
                },
                "travelers": [{
                    "first_name": "NOGENDER",
                    "last_name": "TEST",
                    "birth_date": "1990-08-15",
                    # NOT sending gender field at all
                    "applicant_type": "adult",
                    "nationality": "TR",
                    "national_id": "12345678901",
                    "passport_no": "U99999999",
                    "passport_expiry": "2032-01-20",
                    "marital_status": "married",
                    "profession": "Engineer",
                    "mother_name": "AYSE TEST",
                    "father_name": "MEHMET TEST",
                    "visa_type_id": "visa_30_single",
                    "passport_file_id": self.file_id,
                    "photo_file_id": self.photo_file_id
                }],
                "travel": {
                    "arrival_date": "2026-03-15",
                    "departure_date": "2026-03-25",
                    "purpose": "tourism",
                    "birth_country": "TR"
                },
                "addons": {
                    "express": False,
                    "insurance": False
                },
                "store_items": [],
                "extra_documents": {},
                "kvkk_accepted": True
            }
            
            response = requests.post(
                f"{BASE_URL}/applications",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                app_id = result.get("id")
                ref_code = result.get("reference_code")
                self.log(f"Application WITHOUT gender created successfully. ID: {app_id}, Ref: {ref_code}", "PASS")
                
                # Verify gender is empty or not present
                traveler = result.get("travelers", [{}])[0]
                gender = traveler.get("gender", "")
                if gender == "" or gender is None:
                    self.log("Gender field correctly empty/omitted in response", "PASS")
                    self.tests_passed += 1
                    return True, app_id
                else:
                    self.log(f"Gender field should be empty, got: {gender}", "FAIL")
                    return False, app_id
            else:
                self.log(f"Application creation WITHOUT gender failed with status {response.status_code}: {response.text}", "FAIL")
                return False, None
                
        except Exception as e:
            self.log(f"Application creation error: {str(e)}", "FAIL")
            return False, None
    
    def test_application_with_empty_gender(self):
        """Test creating application with gender='' (empty string)"""
        self.tests_run += 1
        self.log("Testing application creation with gender='' (empty string)...", "INFO")
        
        if not self.file_id or not self.photo_file_id:
            self.log("Missing file IDs for application test", "FAIL")
            return False, None
        
        try:
            payload = {
                "contact": {
                    "full_name": "EMPTY GENDER TEST",
                    "email": f"emptygender_{int(time.time())}@test.com",
                    "phone": "05551234567"
                },
                "travelers": [{
                    "first_name": "EMPTY",
                    "last_name": "GENDER",
                    "birth_date": "1990-08-15",
                    "gender": "",  # Explicitly empty string
                    "applicant_type": "adult",
                    "passport_no": "U88888888",
                    "passport_expiry": "2032-01-20",
                    "marital_status": "single",
                    "profession": "Engineer",
                    "mother_name": "MOTHER",
                    "father_name": "FATHER",
                    "visa_type_id": "visa_30_single",
                    "passport_file_id": self.file_id,
                    "photo_file_id": self.photo_file_id
                }],
                "travel": {
                    "arrival_date": "2026-03-15",
                    "departure_date": "2026-03-25",
                    "birth_country": "TR"
                },
                "addons": {},
                "extra_documents": {},
                "kvkk_accepted": True
            }
            
            response = requests.post(
                f"{BASE_URL}/applications",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                app_id = result.get("id")
                self.log(f"Application with gender='' created successfully. ID: {app_id}", "PASS")
                self.tests_passed += 1
                return True, app_id
            else:
                self.log(f"Application with gender='' failed with status {response.status_code}: {response.text}", "FAIL")
                return False, None
                
        except Exception as e:
            self.log(f"Application creation error: {str(e)}", "FAIL")
            return False, None
    
    def test_admin_update_traveler_gender(self, app_id, admin_token):
        """Test admin endpoint to update traveler gender"""
        self.tests_run += 1
        self.log(f"Testing admin update traveler gender for app {app_id}...", "INFO")
        
        if not admin_token or not app_id:
            self.log("No admin token or app_id available", "FAIL")
            return False
        
        try:
            # Update gender to 'male'
            response = requests.patch(
                f"{BASE_URL}/admin/applications/{app_id}/traveler",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"index": 0, "gender": "male"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                app = result.get("application", {})
                traveler = app.get("travelers", [{}])[0]
                
                if traveler.get("gender") == "male":
                    self.log(f"Admin successfully updated traveler gender to 'male'", "PASS")
                    self.tests_passed += 1
                    return True
                else:
                    self.log(f"Gender not updated correctly: {traveler.get('gender')}", "FAIL")
                    return False
            else:
                self.log(f"Admin update traveler gender failed with status {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Admin update traveler gender error: {str(e)}", "FAIL")
            return False
    
    def test_zami_transfer_blocks_missing_gender(self, app_id, admin_token):
        """Test that Zami transfer blocks when gender is missing (dry_run=false)"""
        self.tests_run += 1
        self.log(f"Testing Zami transfer blocks missing gender for app {app_id}...", "INFO")
        
        if not admin_token or not app_id:
            self.log("No admin token or app_id available", "FAIL")
            return False
        
        try:
            # Try transfer with dry_run=false (should block)
            response = requests.post(
                f"{BASE_URL}/admin/zami/transfer/{app_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"dry_run": False},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Should return ok=false with error about missing gender
                if not result.get("ok"):
                    error = result.get("error", "").lower()
                    if "cinsiyet" in error or "gender" in error:
                        self.log(f"Zami transfer correctly blocked with error: {result.get('error')}", "PASS")
                        self.tests_passed += 1
                        return True
                    else:
                        self.log(f"Zami transfer blocked but wrong error: {result.get('error')}", "FAIL")
                        return False
                else:
                    self.log(f"Zami transfer should have been blocked but succeeded", "FAIL")
                    return False
            else:
                self.log(f"Zami transfer request failed with status {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Zami transfer test error: {str(e)}", "FAIL")
            return False
    
    def test_zami_transfer_allows_dry_run_missing_gender(self, app_id, admin_token):
        """Test that Zami transfer allows dry_run even with missing gender"""
        self.tests_run += 1
        self.log(f"Testing Zami transfer allows dry_run with missing gender for app {app_id}...", "INFO")
        
        if not admin_token or not app_id:
            self.log("No admin token or app_id available", "FAIL")
            return False
        
        try:
            # Try transfer with dry_run=true (should allow)
            response = requests.post(
                f"{BASE_URL}/admin/zami/transfer/{app_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"dry_run": True},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Dry run might fail for other reasons (no session, etc.) but should not block on gender
                error = result.get("error", "").lower()
                if "cinsiyet" in error or "gender" in error:
                    self.log(f"Dry run should not block on gender, but got: {result.get('error')}", "FAIL")
                    return False
                else:
                    self.log(f"Dry run allowed with missing gender (ok={result.get('ok')})", "PASS")
                    self.tests_passed += 1
                    return True
            else:
                self.log(f"Zami dry run request failed with status {response.status_code}: {response.text}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Zami dry run test error: {str(e)}", "FAIL")
            return False

    def run_all_tests(self):
        """Run all backend tests"""
        self.log("=" * 70, "INFO")
        self.log("Dubai Vize Online - REGRESSION TESTING (Code Quality Refactoring)", "INFO")
        self.log("=" * 70, "INFO")
        
        # Test basic endpoints first (regression)
        self.log("\n--- REGRESSION: Basic Endpoints ---", "INFO")
        self.test_basic_endpoints()
        
        # Test content/site structure
        self.log("\n--- REGRESSION: Content Site Structure (routes_public.py) ---", "INFO")
        self.test_content_site_structure()
        
        # Test DB serialization (no ObjectId)
        self.log("\n--- REGRESSION: DB Serialization (db.py) ---", "INFO")
        self.test_db_serialization_no_objectid()
        
        # Test passport upload and OCR (passport_ai.py regression)
        self.log("\n--- REGRESSION: Passport AI (passport_ai.py) ---", "INFO")
        if self.test_upload_passport():
            time.sleep(1)
            self.test_passport_ocr()
        
        # Upload photo for application tests
        self.log("\n--- Setup: Upload Photo ---", "INFO")
        self.test_upload_photo()
        
        # Upload solid image and PDF for photo check tests
        self.log("\n--- Setup: Upload Solid Image & PDF ---", "INFO")
        self.test_upload_solid_image()
        self.test_upload_pdf()
        
        time.sleep(1)
        
        # Test photo check (passport_ai.py regression)
        self.log("\n--- REGRESSION: Photo Check (passport_ai.py) ---", "INFO")
        self.test_photo_check_valid()
        self.test_photo_check_non_portrait()
        self.test_photo_check_invalid_file_id()
        self.test_photo_check_pdf()
        
        # Test pricing quote (content.py regression)
        self.log("\n--- REGRESSION: Pricing Computation (content.py) ---", "INFO")
        self.test_pricing_quote_combinations()
        
        # Test new mandatory fields (previous iteration feature)
        self.log("\n--- REGRESSION: Mandatory Fields (Previous Iteration) ---", "INFO")
        
        # Test application creation with new fields
        success, app_id = self.test_application_with_new_fields()
        
        # Test validation
        self.test_invalid_marital_status()
        
        # Test backward compatibility
        self.test_backward_compatibility()
        
        # Test tracking with last name validation (routes_public.py regression)
        self.log("\n--- REGRESSION: Tracking Last Name Validation (routes_public.py) ---", "INFO")
        self.test_tracking_lastname_validation()
        
        # Test admin endpoints
        self.log("\n--- REGRESSION: Admin Endpoints ---", "INFO")
        admin_success, admin_token = self.test_admin_login()
        
        if admin_success and app_id:
            self.test_admin_application_detail(app_id, admin_token)
        
        # Test WhatsApp settings (whatsapp.py regression)
        if admin_success:
            self.log("\n--- REGRESSION: WhatsApp Settings (whatsapp.py) ---", "INFO")
            self.test_whatsapp_settings(admin_token)
            self.test_whatsapp_settings_update(admin_token)
        
        # Test Zami endpoints (routes_zami.py regression)
        if admin_success:
            self.log("\n--- REGRESSION: Zami Endpoints (routes_zami.py) ---", "INFO")
            self.test_zami_mapping(admin_token)
            self.test_zami_config_structure(admin_token)
            self.test_zami_candidates_structure(admin_token)
            self.test_zami_readiness(admin_token)
        
        # Test Zami public endpoints
        self.log("\n--- REGRESSION: Zami Public Endpoints (routes_zami.py) ---", "INFO")
        self.test_zami_bookmarklet_js()
        self.test_zami_capture_js()
        
        # Test CRITICAL BUG FIX: Zami mapping data preservation
        if admin_success:
            self.log("\n--- CRITICAL BUG FIX: Zami Mapping Data Preservation ---", "INFO")
            self.test_zami_mapping_data_preservation(admin_token)
        
        # Test brand name changes
        self.log("\n--- BRAND NAME CHANGES: Backend Texts ---", "INFO")
        self.test_brand_name_in_backend()
        
        # Test NEW FEATURE: Gender field optional (current iteration)
        self.log("\n--- NEW FEATURE: Gender Field Optional (Current Iteration) ---", "INFO")
        
        # Test application without gender
        success_no_gender, app_id_no_gender = self.test_application_without_gender()
        
        # Test application with empty gender
        success_empty_gender, app_id_empty_gender = self.test_application_with_empty_gender()
        
        # Test admin update traveler gender
        if admin_success and app_id_no_gender:
            self.test_admin_update_traveler_gender(app_id_no_gender, admin_token)
        
        # Test Zami transfer blocks missing gender (non-dry-run)
        if admin_success and app_id_empty_gender:
            self.test_zami_transfer_blocks_missing_gender(app_id_empty_gender, admin_token)
            
        # Test Zami transfer allows dry-run with missing gender
        if admin_success and app_id_empty_gender:
            self.test_zami_transfer_allows_dry_run_missing_gender(app_id_empty_gender, admin_token)
        
        # Print summary
        self.log("=" * 70, "INFO")
        self.log(f"Tests completed: {self.tests_passed}/{self.tests_run} passed", "INFO")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"Success rate: {success_rate:.1f}%", "INFO")
        self.log("=" * 70, "INFO")
        
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = MandatoryFieldsTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
