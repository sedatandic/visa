"""Backend API tests for VizeAtlas Dubai - New Mandatory Fields (marital_status, profession, mother_name, father_name)"""
import requests
import sys
import time
from pathlib import Path

BASE_URL = "https://visa-application-ae.preview.emergentagent.com/api"

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
            if result.get("is_photo") == False and result.get("ok") == False:
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
            if result.get("checked") == False and result.get("reason") == "pdf":
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
            response = requests.post(
                f"{BASE_URL}/admin/login",
                json={"email": "admin@vizeatlas.com", "password": "Dubai2026!"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                token = result.get("token")
                if token:
                    self.log(f"Admin login successful, token obtained", "PASS")
                    self.tests_passed += 1
                    return True, token
                else:
                    self.log("Admin login response missing token", "FAIL")
                    return False, None
            else:
                self.log(f"Admin login failed with status {response.status_code}: {response.text}", "FAIL")
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
    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("=" * 70, "INFO")
        self.log("VizeAtlas Dubai - Backend API Tests (New Mandatory Fields)", "INFO")
        self.log("=" * 70, "INFO")
        
        # Test basic endpoints first (regression)
        self.log("\n--- Regression: Basic Endpoints ---", "INFO")
        self.test_basic_endpoints()
        
        # Test passport upload and OCR (regression)
        self.log("\n--- Regression: Passport OCR ---", "INFO")
        if self.test_upload_passport():
            time.sleep(1)
            self.test_passport_ocr()
        
        # Upload photo for application tests
        self.log("\n--- Setup: Upload Photo ---", "INFO")
        self.test_upload_photo()
        
        time.sleep(1)
        
        # Test new mandatory fields
        self.log("\n--- New Feature: Mandatory Fields (marital_status, profession, mother_name, father_name) ---", "INFO")
        
        # Test application creation with new fields
        success, app_id = self.test_application_with_new_fields()
        
        # Test validation
        self.test_invalid_marital_status()
        
        # Test backward compatibility
        self.test_backward_compatibility()
        
        # Test admin endpoints
        self.log("\n--- Admin Endpoints ---", "INFO")
        admin_success, admin_token = self.test_admin_login()
        
        if admin_success and app_id:
            self.test_admin_application_detail(app_id, admin_token)
        
        if admin_success:
            self.test_zami_mapping(admin_token)
        
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
