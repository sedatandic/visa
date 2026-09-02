"""Backend API tests for VizeAtlas Dubai - Passport OCR feature"""
import requests
import sys
import time
from pathlib import Path

BASE_URL = "https://visa-application-ae.preview.emergentagent.com/api"

class PassportOCRTester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.file_id = None
        
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
    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("=" * 60, "INFO")
        self.log("VizeAtlas Dubai - Backend API Tests (Passport OCR)", "INFO")
        self.log("=" * 60, "INFO")
        
        # Test basic endpoints first
        self.test_basic_endpoints()
        
        # Test passport upload and OCR
        if self.test_upload_passport():
            time.sleep(1)  # Brief pause before OCR
            self.test_passport_ocr()
        
        # Print summary
        self.log("=" * 60, "INFO")
        self.log(f"Tests completed: {self.tests_passed}/{self.tests_run} passed", "INFO")
        self.log("=" * 60, "INFO")
        
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = PassportOCRTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
