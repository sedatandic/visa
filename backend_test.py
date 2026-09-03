#!/usr/bin/env python3
"""
VizeAtlas Dubai - Backend API Testing
Tests draft functionality, Zami endpoints, passport/photo regression, and pricing.
"""
import requests
import sys
import json
from datetime import datetime

# Get backend URL from frontend .env
try:
    with open("/app/frontend/.env", "r") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip()
                break
except Exception:
    BASE_URL = "https://visa-application-ae.preview.emergentagent.com"

API_BASE = f"{BASE_URL}/api"

class TestRunner:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.admin_token = None
        self.test_draft_id = None
        self.test_resume_code = None
        self.results = []

    def test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test"""
        url = f"{API_BASE}/{endpoint}"
        req_headers = {'Content-Type': 'application/json'}
        if headers:
            req_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=req_headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=req_headers, params=params, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=req_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=req_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    result_data = response.json() if response.text else {}
                except:
                    result_data = {}
                self.results.append({
                    "test": name,
                    "status": "passed",
                    "http_status": response.status_code,
                    "data": result_data
                })
                return True, result_data
            else:
                self.tests_failed += 1
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.results.append({
                    "test": name,
                    "status": "failed",
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })
                return False, {}

        except Exception as e:
            self.tests_failed += 1
            print(f"❌ Failed - Error: {str(e)}")
            self.results.append({
                "test": name,
                "status": "error",
                "error": str(e)
            })
            return False, {}

    def admin_login(self):
        """Login as admin"""
        print("\n🔐 Admin Login...")
        success, data = self.test(
            "Admin Login",
            "POST",
            "admin/login",
            200,
            data={"email": "admin@vizeatlas.com", "password": "Dubai2026!"}
        )
        if success and 'token' in data:
            self.admin_token = data['token']
            print(f"✅ Admin token obtained")
            return True
        print("❌ Admin login failed")
        return False

    def test_drafts(self):
        """Test draft creation, retrieval, and update"""
        print("\n\n📝 TESTING DRAFT FUNCTIONALITY")
        print("=" * 60)
        
        # Test 1: Create a draft
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@test.com"
        draft_data = {
            "email": test_email,
            "data": {
                "contact": {"full_name": "Test User", "email": test_email, "phone": "05551234567"},
                "travelers": [{"first_name": "John", "last_name": "Doe"}],
                "step": 1
            },
            "title": "Test Draft",
            "step": 1,
            "traveler_count": 1
        }
        
        success, response = self.test(
            "Create Draft",
            "POST",
            "drafts",
            200,
            data=draft_data
        )
        
        if success:
            self.test_draft_id = response.get('draft_id')
            self.test_resume_code = response.get('resume_code')
            resume_url = response.get('resume_url')
            email_status = response.get('email_status')
            
            print(f"   Draft ID: {self.test_draft_id}")
            print(f"   Resume Code: {self.test_resume_code}")
            print(f"   Resume URL: {resume_url}")
            print(f"   Email Status: {email_status}")
            
            # Verify resume_url contains correct query params
            if resume_url and f"taslak={self.test_draft_id}" in resume_url and f"kod={self.test_resume_code}" in resume_url:
                print(f"   ✅ Resume URL format correct")
            else:
                print(f"   ❌ Resume URL format incorrect")
        
        # Test 2: Retrieve draft with correct code
        if self.test_draft_id and self.test_resume_code:
            success, response = self.test(
                "Get Draft with Correct Code",
                "GET",
                f"drafts/{self.test_draft_id}",
                200,
                params={"code": self.test_resume_code}
            )
            
            if success:
                if response.get('id') == self.test_draft_id:
                    print(f"   ✅ Draft data retrieved correctly")
                if response.get('data', {}).get('contact', {}).get('email') == test_email:
                    print(f"   ✅ Draft data matches")
        
        # Test 3: Retrieve draft with wrong code (should fail)
        if self.test_draft_id:
            success, response = self.test(
                "Get Draft with Wrong Code (should fail)",
                "GET",
                f"drafts/{self.test_draft_id}",
                404,
                params={"code": "WRONGCODE"}
            )
        
        # Test 4: Update existing draft
        if self.test_draft_id and self.test_resume_code:
            updated_data = {
                "email": test_email,
                "draft_id": self.test_draft_id,
                "resume_code": self.test_resume_code,
                "data": {
                    "contact": {"full_name": "Updated User", "email": test_email, "phone": "05551234567"},
                    "travelers": [{"first_name": "Jane", "last_name": "Smith"}],
                    "step": 2
                },
                "title": "Updated Draft",
                "step": 2,
                "traveler_count": 1
            }
            
            success, response = self.test(
                "Update Existing Draft",
                "POST",
                "drafts",
                200,
                data=updated_data
            )
            
            if success:
                # Should return same draft_id
                if response.get('draft_id') == self.test_draft_id:
                    print(f"   ✅ Draft updated (same ID returned)")
                else:
                    print(f"   ❌ New draft created instead of updating (ID changed)")

    def test_zami_admin_endpoints(self):
        """Test Zami admin endpoints"""
        print("\n\n🔧 TESTING ZAMI ADMIN ENDPOINTS")
        print("=" * 60)
        
        if not self.admin_token:
            print("❌ Skipping - No admin token")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test readiness endpoint
        success, response = self.test(
            "Zami Readiness Check",
            "GET",
            "admin/zami/readiness",
            200,
            headers=headers
        )
        
        if success:
            ready_bookmarklet = response.get('ready_bookmarklet')
            ready_robot = response.get('ready_robot')
            print(f"   Ready Bookmarklet: {ready_bookmarklet}")
            print(f"   Ready Robot: {ready_robot}")
            
            if ready_bookmarklet:
                print(f"   ✅ Bookmarklet ready")
            if ready_robot:
                print(f"   ✅ Robot ready")
        
        # Test mapping endpoint
        success, response = self.test(
            "Zami Mapping",
            "GET",
            "admin/zami/mapping",
            200,
            headers=headers
        )
        
        if success:
            mapping = response
            required_keys = ['constants', 'validate_selector', 'helper_selectors', 
                           'upload_targets', 'status_search_field', 'status_submit_selector',
                           'auto_check_enabled', 'auto_check_hours']
            
            for key in required_keys:
                if key in mapping:
                    print(f"   ✅ {key}: {mapping[key]}")
                else:
                    print(f"   ❌ Missing key: {key}")
            
            # Verify auto_check settings
            if mapping.get('auto_check_enabled') == True:
                print(f"   ✅ Auto-check enabled")
            if mapping.get('auto_check_hours') == 6:
                print(f"   ✅ Auto-check hours set to 6")

    def test_passport_read_regression(self):
        """Test passport read returns new fields"""
        print("\n\n📄 TESTING PASSPORT READ REGRESSION")
        print("=" * 60)
        
        # Note: This test requires an actual file upload, which we can't do in this test
        # We'll just verify the endpoint exists and returns proper error for missing file
        success, response = self.test(
            "Passport Read Endpoint (no file)",
            "POST",
            "passport/read",
            400,  # Should fail without file
            data={}
        )
        print("   ℹ️  Endpoint exists (full test requires file upload)")

    def test_photo_check_regression(self):
        """Test photo check endpoint"""
        print("\n\n📸 TESTING PHOTO CHECK REGRESSION")
        print("=" * 60)
        
        # Similar to passport, just verify endpoint exists
        success, response = self.test(
            "Photo Check Endpoint (no file)",
            "POST",
            "photo/check",
            400,  # Should fail without file
            data={}
        )
        print("   ℹ️  Endpoint exists (full test requires file upload)")

    def test_pricing_family_discount(self):
        """Test pricing quote with family discount"""
        print("\n\n💰 TESTING PRICING FAMILY DISCOUNT")
        print("=" * 60)
        
        # Get visa types first
        success, visa_response = self.test(
            "Get Visa Types",
            "GET",
            "visa-types",
            200
        )
        
        if not success or not visa_response:
            print("❌ Cannot test pricing without visa types")
            return
        
        # Find adult visa types
        adult_visas = [v for v in visa_response if v.get('category') != 'child']
        if len(adult_visas) < 1:
            print("❌ No adult visa types found")
            return
        
        visa_id = adult_visas[0]['id']
        
        # Test with 2 travelers (should get family discount)
        success, response = self.test(
            "Pricing Quote - 2 Travelers (Family Discount)",
            "POST",
            "pricing/quote",
            200,
            data={
                "visa_type_ids": [visa_id, visa_id],
                "addons": {"express": False, "insurance": False},
                "store_items": []
            }
        )
        
        if success:
            family_discount_rate = response.get('family_discount_rate')
            family_discount = response.get('family_discount')
            
            print(f"   Family Discount Rate: {family_discount_rate}")
            print(f"   Family Discount Amount: {family_discount}")
            
            if family_discount_rate == 0.1:
                print(f"   ✅ Family discount rate is 0.1 (10%)")
            else:
                print(f"   ❌ Family discount rate is {family_discount_rate}, expected 0.1")

    def test_mongodb_zami_record(self):
        """Verify MongoDB has the Zami submission record"""
        print("\n\n🗄️  TESTING MONGODB ZAMI RECORD")
        print("=" * 60)
        
        if not self.admin_token:
            print("❌ Skipping - No admin token")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Search for application DV-CV681445
        success, response = self.test(
            "Search Application DV-CV681445",
            "GET",
            "admin/applications",
            200,
            headers=headers,
            params={"search": "DV-CV681445"}
        )
        
        if success:
            items = response.get('items', [])
            if items:
                app = items[0]
                zami_reference = app.get('zami_reference')
                zami_status = app.get('zami_status')
                
                print(f"   Reference Code: {app.get('reference_code')}")
                print(f"   Zami Reference: {zami_reference}")
                print(f"   Zami Status: {zami_status}")
                
                if zami_reference == 'VS-66059':
                    print(f"   ✅ Zami reference is VS-66059")
                else:
                    print(f"   ❌ Zami reference is {zami_reference}, expected VS-66059")
                
                if zami_status == 'submitted':
                    print(f"   ✅ Zami status is 'submitted'")
                else:
                    print(f"   ❌ Zami status is {zami_status}, expected 'submitted'")
            else:
                print(f"   ❌ Application DV-CV681445 not found")

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("VizeAtlas Dubai - Backend API Testing")
        print(f"Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Admin login
        if not self.admin_login():
            print("\n❌ Cannot proceed without admin access")
            return 1
        
        # Run all test suites
        self.test_drafts()
        self.test_zami_admin_endpoints()
        self.test_passport_read_regression()
        self.test_photo_check_regression()
        self.test_pricing_family_discount()
        self.test_mongodb_zami_record()
        
        # Print summary
        print("\n\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print("=" * 60)
        
        return 0 if self.tests_failed == 0 else 1

def main():
    runner = TestRunner()
    return runner.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
