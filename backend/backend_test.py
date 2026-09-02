"""Backend API tests for VizeAtlas Dubai - Passport OCR & Photo Validation"""
import requests
import sys
import time
from pathlib import Path

BASE_URL = "https://visa-application-ae.preview.emergentagent.com/api"

class PhotoValidationTester:
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
    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("=" * 70, "INFO")
        self.log("VizeAtlas Dubai - Backend API Tests (Photo Validation Feature)", "INFO")
        self.log("=" * 70, "INFO")
        
        # Test basic endpoints first
        self.test_basic_endpoints()
        
        # Test passport upload and OCR (regression)
        self.log("\n--- Regression: Passport OCR ---", "INFO")
        if self.test_upload_passport():
            time.sleep(1)
            self.test_passport_ocr()
        
        # Test photo validation feature
        self.log("\n--- New Feature: Photo Validation ---", "INFO")
        
        # Upload test images
        self.test_upload_photo()
        self.test_upload_solid_image()
        self.test_upload_pdf()
        
        time.sleep(1)  # Brief pause before validation tests
        
        # Test photo validation with different scenarios
        if self.photo_file_id:
            self.test_photo_check_valid()
        
        if self.solid_file_id:
            self.test_photo_check_non_portrait()
        
        self.test_photo_check_invalid_file_id()
        
        if self.pdf_file_id:
            self.test_photo_check_pdf()
        
        # Print summary
        self.log("=" * 70, "INFO")
        self.log(f"Tests completed: {self.tests_passed}/{self.tests_run} passed", "INFO")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        self.log(f"Success rate: {success_rate:.1f}%", "INFO")
        self.log("=" * 70, "INFO")
        
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = PhotoValidationTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
