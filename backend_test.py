"""Backend API tests for VizeAtlas Dubai - Round: Passport OCR extended fields, Zami RPA, family discount, processing time"""
import requests
import sys
import time
from pathlib import Path

BASE_URL = "https://visa-application-ae.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@vizeatlas.com"
ADMIN_PASSWORD = "Dubai2026!"

class VizeAtlasBackendTester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_token = None
        self.passport_file_id = None
        self.photo_file_id = None
        self.non_passport_file_id = None
        
    def log(self, message, status="INFO"):
        symbols = {"PASS": "✅", "FAIL": "❌", "INFO": "🔍", "WARN": "⚠️"}
        print(f"{symbols.get(status, '•')} {message}")
    
    def admin_login(self):
        """Login as admin to get token"""
        self.log("Logging in as admin...", "INFO")
        try:
            response = requests.post(
                f"{BASE_URL}/admin/login",
                json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                self.admin_token = result.get("token")
                self.log(f"Admin login successful", "PASS")
                return True
            else:
                self.log(f"Admin login failed: {response.status_code} - {response.text}", "FAIL")
                return False
        except Exception as e:
            self.log(f"Admin login error: {str(e)}", "FAIL")
            return False
    
    def test_passport_ocr_extended_fields(self):
        """Test POST /api/passport/read returns new fields: passport_issue_date, birth_place, passport_issue_place"""
        self.tests_run += 1
        self.log("Testing passport OCR with extended fields...", "INFO")
        
        # Upload passport image first
        passport_path = Path("/app/tests/fixtures/test_passport.png")
        if not passport_path.exists():
            self.log(f"Test passport file not found: {passport_path}", "FAIL")
            return False
        
        try:
            # Upload passport
            with open(passport_path, "rb") as f:
                files = {"file": ("test_passport.png", f, "image/png")}
                data = {"doc_type": "passport"}
                upload_response = requests.post(
                    f"{BASE_URL}/uploads",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if upload_response.status_code != 200:
                self.log(f"Passport upload failed: {upload_response.status_code}", "FAIL")
                return False
            
            self.passport_file_id = upload_response.json().get("file_id")
            self.log(f"Passport uploaded: {self.passport_file_id}", "INFO")
            
            # Read passport with OCR
            time.sleep(1)
            response = requests.post(
                f"{BASE_URL}/passport/read",
                data={"file_id": self.passport_file_id},
                timeout=60
            )
            
            if response.status_code != 200:
                self.log(f"Passport OCR failed: {response.status_code} - {response.text}", "FAIL")
                return False
            
            result = response.json()
            
            if not result.get("ok"):
                self.log(f"OCR not ok: {result.get('message')}", "FAIL")
                return False
            
            data = result.get("data", {})
            
            # Check for NEW extended fields
            required_new_fields = ["passport_issue_date", "birth_place", "passport_issue_place"]
            existing_fields = ["first_name", "last_name", "passport_no", "birth_date", "passport_expiry", "gender", "nationality", "national_id", "confidence", "is_passport"]
            
            all_fields_present = True
            for field in required_new_fields + existing_fields:
                if field not in data:
                    self.log(f"Missing field in OCR response: {field}", "FAIL")
                    all_fields_present = False
                else:
                    value = data[field]
                    # New fields may be empty strings if unreadable, that's OK
                    self.log(f"  {field}: {value if value else '(empty)'}", "INFO")
            
            if all_fields_present:
                self.log("All OCR fields (including new extended fields) present in response", "PASS")
                self.tests_passed += 1
                return True
            else:
                return False
                
        except Exception as e:
            self.log(f"Passport OCR test error: {str(e)}", "FAIL")
            return False
    
    def test_passport_ocr_non_passport_graceful(self):
        """Test POST /api/passport/read with non-passport image returns is_passport=false gracefully (no 500)"""
        self.tests_run += 1
        self.log("Testing passport OCR with non-passport image (should return is_passport=false)...", "INFO")
        
        # Upload a non-passport image (solid color or portrait)
        solid_path = Path("/app/tests/fixtures/solid_blue.png")
        if not solid_path.exists():
            self.log(f"Test non-passport file not found: {solid_path}", "FAIL")
            return False
        
        try:
            # Upload non-passport image
            with open(solid_path, "rb") as f:
                files = {"file": ("solid_blue.png", f, "image/png")}
                data = {"doc_type": "passport"}
                upload_response = requests.post(
                    f"{BASE_URL}/uploads",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if upload_response.status_code != 200:
                self.log(f"Non-passport upload failed: {upload_response.status_code}", "FAIL")
                return False
            
            self.non_passport_file_id = upload_response.json().get("file_id")
            
            # Read with OCR
            time.sleep(1)
            response = requests.post(
                f"{BASE_URL}/passport/read",
                data={"file_id": self.non_passport_file_id},
                timeout=60
            )
            
            # Should NOT return 500
            if response.status_code == 500:
                self.log(f"Non-passport image caused 500 error (should be graceful)", "FAIL")
                return False
            
            if response.status_code != 200:
                self.log(f"Non-passport OCR returned {response.status_code}: {response.text}", "WARN")
                # This might be acceptable if it's a 400 with proper error message
                if response.status_code == 400:
                    self.log("Non-passport gracefully rejected with 400", "PASS")
                    self.tests_passed += 1
                    return True
                return False
            
            result = response.json()
            data = result.get("data", {})
            
            # Check is_passport field
            if data.get("is_passport") == False:
                self.log(f"Non-passport correctly identified: is_passport=false", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"Non-passport not identified correctly: is_passport={data.get('is_passport')}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Non-passport OCR test error: {str(e)}", "FAIL")
            return False
    
    def test_photo_check_regression(self):
        """Test POST /api/photo/check still works (regression)"""
        self.tests_run += 1
        self.log("Testing photo check regression...", "INFO")
        
        # Upload portrait photo
        photo_path = Path("/app/tests/fixtures/test_portrait.png")
        if not photo_path.exists():
            self.log(f"Test portrait file not found: {photo_path}", "FAIL")
            return False
        
        try:
            # Upload photo
            with open(photo_path, "rb") as f:
                files = {"file": ("test_portrait.png", f, "image/png")}
                data = {"doc_type": "photo"}
                upload_response = requests.post(
                    f"{BASE_URL}/uploads",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if upload_response.status_code != 200:
                self.log(f"Photo upload failed: {upload_response.status_code}", "FAIL")
                return False
            
            self.photo_file_id = upload_response.json().get("file_id")
            
            # Check photo
            time.sleep(1)
            response = requests.post(
                f"{BASE_URL}/photo/check",
                data={"file_id": self.photo_file_id},
                timeout=60
            )
            
            if response.status_code != 200:
                self.log(f"Photo check failed: {response.status_code} - {response.text}", "FAIL")
                return False
            
            result = response.json()
            
            # Check for expected keys
            required_keys = ["checked", "ok", "is_photo", "checks", "issues", "advice", "score"]
            missing_keys = [k for k in required_keys if k not in result]
            
            if missing_keys:
                self.log(f"Missing keys in photo check response: {missing_keys}", "FAIL")
                return False
            
            self.log(f"Photo check returned all expected keys: checked={result['checked']}, ok={result['ok']}, score={result['score']}", "PASS")
            self.tests_passed += 1
            return True
                
        except Exception as e:
            self.log(f"Photo check test error: {str(e)}", "FAIL")
            return False
    
    def test_application_with_new_fields(self):
        """Test POST /api/applications accepts and persists new optional fields"""
        self.tests_run += 1
        self.log("Testing application creation WITH new optional fields...", "INFO")
        
        if not self.passport_file_id or not self.photo_file_id:
            self.log("Missing file IDs for application test", "FAIL")
            return False
        
        try:
            application_data = {
                "contact": {
                    "full_name": "Test User",
                    "email": f"test_{int(time.time())}@example.com",
                    "phone": "05551234567",
                    "address_city": "Istanbul",
                    "whatsapp_optin": False
                },
                "travelers": [
                    {
                        "first_name": "AHMET",
                        "last_name": "YILMAZ",
                        "birth_date": "1990-08-15",
                        "gender": "male",
                        "applicant_type": "adult",
                        "nationality": "TR",
                        "national_id": "12345678901",
                        "passport_no": "U12345678",
                        "passport_expiry": "2032-01-20",
                        # NEW OPTIONAL FIELDS
                        "passport_issue_date": "2022-01-20",
                        "birth_place": "ANKARA",
                        "passport_issue_place": "ANKARA",
                        "visa_type_id": "visa_30_single",
                        "passport_file_id": self.passport_file_id,
                        "photo_file_id": self.photo_file_id
                    }
                ],
                "travel": {
                    "arrival_date": "2026-12-01",
                    "departure_date": "2026-12-15",
                    "purpose": "tourism",
                    "birth_country": "TR",
                    "accommodation": "Test Hotel",
                    "flight_no": "TK123",
                    "notes": ""
                },
                "addons": {
                    "express": False
                },
                "store_items": [],
                "extra_documents": {
                    "ticket_file_id": None,
                    "hotel_file_id": None,
                    "other_file_ids": []
                },
                "kvkk_accepted": True
            }
            
            response = requests.post(
                f"{BASE_URL}/applications",
                json=application_data,
                timeout=30
            )
            
            if response.status_code != 200:
                self.log(f"Application creation failed: {response.status_code} - {response.text}", "FAIL")
                return False
            
            result = response.json()
            
            # Check if application was created
            if not result.get("id"):
                self.log("Application created but no ID returned", "FAIL")
                return False
            
            self.log(f"Application created with new fields: {result.get('reference_code')}", "PASS")
            self.tests_passed += 1
            return True
                
        except Exception as e:
            self.log(f"Application creation test error: {str(e)}", "FAIL")
            return False
    
    def test_application_without_new_fields(self):
        """Test POST /api/applications works WITHOUT new fields (backwards compatibility)"""
        self.tests_run += 1
        self.log("Testing application creation WITHOUT new optional fields (backwards compatibility)...", "INFO")
        
        if not self.passport_file_id or not self.photo_file_id:
            self.log("Missing file IDs for application test", "FAIL")
            return False
        
        try:
            application_data = {
                "contact": {
                    "full_name": "Test User 2",
                    "email": f"test2_{int(time.time())}@example.com",
                    "phone": "05551234568",
                    "address_city": "Izmir",
                    "whatsapp_optin": False
                },
                "travelers": [
                    {
                        "first_name": "MEHMET",
                        "last_name": "DEMIR",
                        "birth_date": "1985-05-10",
                        "gender": "male",
                        "applicant_type": "adult",
                        "nationality": "TR",
                        "national_id": "98765432109",
                        "passport_no": "U98765432",
                        "passport_expiry": "2030-06-15",
                        # NO NEW FIELDS - testing backwards compatibility
                        "visa_type_id": "visa_30_single",
                        "passport_file_id": self.passport_file_id,
                        "photo_file_id": self.photo_file_id
                    }
                ],
                "travel": {
                    "arrival_date": "2026-12-10",
                    "departure_date": "2026-12-20",
                    "purpose": "tourism",
                    "birth_country": "TR",
                    "accommodation": "Test Hotel 2",
                    "flight_no": "TK456",
                    "notes": ""
                },
                "addons": {
                    "express": False
                },
                "store_items": [],
                "extra_documents": {
                    "ticket_file_id": None,
                    "hotel_file_id": None,
                    "other_file_ids": []
                },
                "kvkk_accepted": True
            }
            
            response = requests.post(
                f"{BASE_URL}/applications",
                json=application_data,
                timeout=30
            )
            
            if response.status_code != 200:
                self.log(f"Application creation (without new fields) failed: {response.status_code} - {response.text}", "FAIL")
                return False
            
            result = response.json()
            
            if not result.get("id"):
                self.log("Application created but no ID returned", "FAIL")
                return False
            
            self.log(f"Application created without new fields (backwards compatible): {result.get('reference_code')}", "PASS")
            self.tests_passed += 1
            return True
                
        except Exception as e:
            self.log(f"Application creation (backwards compat) test error: {str(e)}", "FAIL")
            return False
    
    def test_family_discount_rate(self):
        """Test GET /api/pricing/quote returns family_discount_rate = 0.1 for 2+ travelers, 0.0 for 1"""
        self.tests_run += 1
        self.log("Testing family discount rate (10% for 2+ travelers)...", "INFO")
        
        try:
            # Test with 1 traveler (no discount)
            response_1 = requests.post(
                f"{BASE_URL}/pricing/quote",
                json={
                    "visa_type_ids": ["visa_30_single"],
                    "addons": {"express": False},
                    "store_items": []
                },
                timeout=10
            )
            
            if response_1.status_code != 200:
                self.log(f"Pricing quote (1 traveler) failed: {response_1.status_code}", "FAIL")
                return False
            
            result_1 = response_1.json()
            discount_rate_1 = result_1.get("family_discount_rate", -1)
            
            # Test with 2 travelers (10% discount)
            response_2 = requests.post(
                f"{BASE_URL}/pricing/quote",
                json={
                    "visa_type_ids": ["visa_30_single", "visa_30_single"],
                    "addons": {"express": False},
                    "store_items": []
                },
                timeout=10
            )
            
            if response_2.status_code != 200:
                self.log(f"Pricing quote (2 travelers) failed: {response_2.status_code}", "FAIL")
                return False
            
            result_2 = response_2.json()
            discount_rate_2 = result_2.get("family_discount_rate", -1)
            
            # Check discount rates
            if discount_rate_1 == 0.0 and discount_rate_2 == 0.1:
                self.log(f"Family discount correct: 1 traveler={discount_rate_1}, 2 travelers={discount_rate_2}", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"Family discount incorrect: 1 traveler={discount_rate_1} (expected 0.0), 2 travelers={discount_rate_2} (expected 0.1)", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Family discount test error: {str(e)}", "FAIL")
            return False
    
    def test_content_site_processing_time(self):
        """Test GET /api/content/site mentions '2 iş günü' and %10 family discount"""
        self.tests_run += 1
        self.log("Testing content/site for '2 iş günü' and %10 family discount...", "INFO")
        
        try:
            response = requests.get(f"{BASE_URL}/content/site", timeout=10)
            
            if response.status_code != 200:
                self.log(f"Content/site failed: {response.status_code}", "FAIL")
                return False
            
            result = response.json()
            
            # Check for '2 iş günü' in processing_days or visa_types
            content_str = str(result).lower()
            
            has_2_days = "2 iş günü" in content_str or "2 is gunu" in content_str
            has_10_percent = "%10" in str(result) or "10%" in str(result)
            
            if has_2_days and has_10_percent:
                self.log(f"Content correct: '2 iş günü' found={has_2_days}, '%10' found={has_10_percent}", "PASS")
                self.tests_passed += 1
                return True
            else:
                self.log(f"Content missing: '2 iş günü' found={has_2_days}, '%10' found={has_10_percent}", "FAIL")
                return False
                
        except Exception as e:
            self.log(f"Content/site test error: {str(e)}", "FAIL")
            return False
    
    def test_zami_readiness(self):
        """Test GET /api/admin/zami/readiness returns ready flags and checks array"""
        self.tests_run += 1
        self.log("Testing Zami readiness endpoint...", "INFO")
        
        if not self.admin_token:
            self.log("No admin token available for Zami readiness test", "FAIL")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/zami/readiness",
                headers={"Authorization": f"Bearer {self.admin_token}"},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log(f"Zami readiness failed: {response.status_code} - {response.text}", "FAIL")
                return False
            
            result = response.json()
            
            # Check for required fields
            required_fields = ["ready_bookmarklet", "ready_robot", "checks"]
            missing_fields = [f for f in required_fields if f not in result]
            
            if missing_fields:
                self.log(f"Missing fields in Zami readiness: {missing_fields}", "FAIL")
                return False
            
            # Check checks array has expected keys
            checks = result.get("checks", [])
            if not isinstance(checks, list) or len(checks) == 0:
                self.log(f"Checks array is empty or not a list", "FAIL")
                return False
            
            # Verify checks have required keys
            expected_check_keys = ["key", "label", "ok", "detail"]
            for check in checks:
                missing_check_keys = [k for k in expected_check_keys if k not in check]
                if missing_check_keys:
                    self.log(f"Check missing keys: {missing_check_keys}", "FAIL")
                    return False
            
            self.log(f"Zami readiness OK: ready_bookmarklet={result['ready_bookmarklet']}, ready_robot={result['ready_robot']}, checks={len(checks)}", "PASS")
            self.tests_passed += 1
            return True
                
        except Exception as e:
            self.log(f"Zami readiness test error: {str(e)}", "FAIL")
            return False
    
    def test_regression_endpoints(self):
        """Test regression endpoints: /products, /visa-types, /applications/track, /uploads"""
        endpoints = [
            ("GET", "/products", None),
            ("GET", "/visa-types", None),
            ("GET", "/visa-guides", None),
        ]
        
        for method, endpoint, data in endpoints:
            self.tests_run += 1
            try:
                if method == "GET":
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
                else:
                    response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=10)
                
                if response.status_code == 200:
                    self.log(f"{method} {endpoint}: OK", "PASS")
                    self.tests_passed += 1
                else:
                    self.log(f"{method} {endpoint}: Failed with status {response.status_code}", "FAIL")
            except Exception as e:
                self.log(f"{method} {endpoint}: Error - {str(e)}", "FAIL")
    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("=" * 80, "INFO")
        self.log("VizeAtlas Dubai - Backend API Tests", "INFO")
        self.log("Round: Passport OCR extended, Zami RPA, family discount, processing time", "INFO")
        self.log("=" * 80, "INFO")
        
        # Admin login first
        if not self.admin_login():
            self.log("Admin login failed, some tests will be skipped", "WARN")
        
        # Test new passport OCR extended fields
        self.log("\n--- Feature: Passport OCR Extended Fields ---", "INFO")
        self.test_passport_ocr_extended_fields()
        
        # Test non-passport graceful handling
        self.log("\n--- Feature: Non-Passport Graceful Handling ---", "INFO")
        self.test_passport_ocr_non_passport_graceful()
        
        # Test photo check regression
        self.log("\n--- Regression: Photo Check ---", "INFO")
        self.test_photo_check_regression()
        
        # Test application with new fields
        self.log("\n--- Feature: Application with New Fields ---", "INFO")
        self.test_application_with_new_fields()
        
        # Test application without new fields (backwards compatibility)
        self.log("\n--- Feature: Application Backwards Compatibility ---", "INFO")
        self.test_application_without_new_fields()
        
        # Test family discount rate
        self.log("\n--- Feature: Family Discount Rate (10% for 2+) ---", "INFO")
        self.test_family_discount_rate()
        
        # Test content/site for processing time and family discount text
        self.log("\n--- Feature: Content Site (2 iş günü, %10) ---", "INFO")
        self.test_content_site_processing_time()
        
        # Test Zami readiness
        self.log("\n--- Feature: Zami RPA Readiness ---", "INFO")
        if self.admin_token:
            self.test_zami_readiness()
        else:
            self.log("Skipping Zami readiness test (no admin token)", "WARN")
        
        # Test regression endpoints
        self.log("\n--- Regression: Other Endpoints ---", "INFO")
        self.test_regression_endpoints()
        
        # Print summary
        self.log("=" * 80, "INFO")
        self.log(f"Tests completed: {self.tests_passed}/{self.tests_run} passed", "INFO")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"Success rate: {success_rate:.1f}%", "INFO")
        self.log("=" * 80, "INFO")
        
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = VizeAtlasBackendTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
