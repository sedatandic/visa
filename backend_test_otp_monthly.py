#!/usr/bin/env python3
"""
VizeAtlas Dubai - OTP Once-a-Month Feature Testing
Tests the new trusted-device cookie persistence and automatic OTP-less re-login functionality.
"""
import requests
import sys
import json

# Get backend URL from frontend .env
try:
    with open("/app/frontend/.env", "r") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip()
                break
except Exception:
    BASE_URL = "https://whatsapp-bot-test-2.preview.emergentagent.com"

API_BASE = f"{BASE_URL}/api"

class OTPMonthlyTester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.admin_token = None
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
                print(f"   Response: {response.text[:300]}")
                self.results.append({
                    "test": name,
                    "status": "failed",
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:300]
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

    def test_new_session_fields(self):
        """Test that session object contains new OTP-monthly fields"""
        print("\n\n📊 TESTING NEW SESSION FIELDS")
        print("=" * 60)
        
        if not self.admin_token:
            print("❌ Skipping - No admin token")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test GET /api/admin/zami/config (which includes session data)
        success, response = self.test(
            "GET /admin/zami/config - Check Session Fields",
            "GET",
            "admin/zami/config",
            200,
            headers=headers
        )
        
        if success:
            session = response.get('session', {})
            
            # Check for new fields
            new_fields = {
                'trusted_device': bool,
                'otp_required': bool,
                'last_otp_at': (str, type(None)),
                'last_auto_login_at': (str, type(None)),
                'auto_login_count': int,
                'next_otp_due': (str, type(None))
            }
            
            print(f"\n   Session object keys: {list(session.keys())}")
            
            all_present = True
            for field, expected_type in new_fields.items():
                if field in session:
                    value = session[field]
                    if isinstance(expected_type, tuple):
                        type_ok = type(value) in expected_type
                    else:
                        type_ok = isinstance(value, expected_type)
                    
                    if type_ok:
                        print(f"   ✅ {field}: {value} (type: {type(value).__name__})")
                    else:
                        print(f"   ❌ {field}: {value} (wrong type, expected {expected_type})")
                        all_present = False
                else:
                    print(f"   ❌ {field}: MISSING")
                    all_present = False
            
            if all_present:
                print(f"\n   ✅ All new session fields present with correct types")
            else:
                print(f"\n   ❌ Some session fields missing or have wrong types")
            
            # Display current session status
            print(f"\n   Current Session Status:")
            print(f"   - Has Session: {session.get('has_session')}")
            print(f"   - Expired: {session.get('expired')}")
            print(f"   - Trusted Device: {session.get('trusted_device')}")
            print(f"   - OTP Required: {session.get('otp_required')}")
            print(f"   - Last OTP At: {session.get('last_otp_at')}")
            print(f"   - Last Auto Login At: {session.get('last_auto_login_at')}")
            print(f"   - Auto Login Count: {session.get('auto_login_count')}")
            print(f"   - Next OTP Due: {session.get('next_otp_due')}")

    def test_auto_renew_endpoint(self):
        """Test POST /api/admin/zami/session/auto-renew endpoint"""
        print("\n\n🔄 TESTING AUTO-RENEW ENDPOINT")
        print("=" * 60)
        
        # Test 1: Without authentication (should fail with 401/403)
        print("\n   Test 1: Auto-renew without authentication")
        success, response = self.test(
            "POST /admin/zami/session/auto-renew (No Auth - Should Fail)",
            "POST",
            "admin/zami/session/auto-renew",
            401,  # Expecting 401 Unauthorized
            data={}
        )
        
        if success:
            print(f"   ✅ Correctly rejected unauthenticated request")
        
        # Test 2: With authentication (should return JSON with ok/reason)
        if not self.admin_token:
            print("❌ Skipping authenticated test - No admin token")
            return
        
        print("\n   Test 2: Auto-renew with authentication")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # NOTE: Per instructions, we should only call this AT MOST ONCE
        # because each attempt sends a real OTP email
        success, response = self.test(
            "POST /admin/zami/session/auto-renew (With Auth)",
            "POST",
            "admin/zami/session/auto-renew",
            200,
            data={},
            headers=headers
        )
        
        if success:
            print(f"\n   Response structure:")
            print(f"   - Keys: {list(response.keys())}")
            
            # Check for expected response structure
            has_ok = 'ok' in response
            has_reason = 'reason' in response
            
            if has_ok:
                print(f"   ✅ 'ok' field present: {response.get('ok')}")
            else:
                print(f"   ❌ 'ok' field missing")
            
            if response.get('ok') == False and has_reason:
                print(f"   ✅ 'reason' field present: {response.get('reason')}")
                
                # Per instructions: reason='otp_required' is ACCEPTABLE (not a bug)
                if response.get('reason') == 'otp_required':
                    print(f"   ℹ️  Portal requires OTP (expected behavior - portal session expired)")
                elif response.get('reason') == 'no_credentials':
                    print(f"   ℹ️  No credentials configured (expected if not set up)")
                elif response.get('reason') == 'browser':
                    print(f"   ℹ️  Browser launch failed (expected in some environments)")
                elif response.get('reason') == 'captcha_failed':
                    print(f"   ℹ️  Captcha reading failed (expected - AI may not always succeed)")
            elif response.get('ok') == True:
                print(f"   ✅ Auto-login succeeded without OTP")
                if 'attempts' in response:
                    print(f"   - Attempts: {response.get('attempts')}")
            
            print(f"\n   Full response: {json.dumps(response, indent=2)}")

    def test_existing_zami_endpoints(self):
        """Test that existing Zami endpoints still work (regression)"""
        print("\n\n🔧 TESTING EXISTING ZAMI ENDPOINTS (REGRESSION)")
        print("=" * 60)
        
        if not self.admin_token:
            print("❌ Skipping - No admin token")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test 1: GET /api/admin/zami/readiness
        success, response = self.test(
            "GET /admin/zami/readiness",
            "GET",
            "admin/zami/readiness",
            200,
            headers=headers
        )
        
        if success:
            ready_bookmarklet = response.get('ready_bookmarklet')
            ready_robot = response.get('ready_robot')
            checks = response.get('checks', [])
            
            print(f"   Ready Bookmarklet: {ready_bookmarklet}")
            print(f"   Ready Robot: {ready_robot}")
            print(f"   Checks count: {len(checks)}")
            
            # Verify session check includes new fields
            session_check = next((c for c in checks if c.get('key') == 'session'), None)
            if session_check:
                print(f"   ✅ Session check present in readiness")
                print(f"      - Label: {session_check.get('label')}")
                print(f"      - OK: {session_check.get('ok')}")
                print(f"      - Detail: {session_check.get('detail')}")
        
        # Test 2: GET /api/admin/zami/config
        success, response = self.test(
            "GET /admin/zami/config",
            "GET",
            "admin/zami/config",
            200,
            headers=headers
        )
        
        if success:
            has_settings = 'settings' in response
            has_mapping = 'mapping' in response
            has_session = 'session' in response
            
            print(f"   Has settings: {has_settings}")
            print(f"   Has mapping: {has_mapping}")
            print(f"   Has session: {has_session}")
            
            if has_session:
                print(f"   ✅ Session object present in config response")
        
        # Test 3: GET /api/admin/zami/candidates
        success, response = self.test(
            "GET /admin/zami/candidates",
            "GET",
            "admin/zami/candidates",
            200,
            headers=headers
        )
        
        if success:
            items = response.get('items', [])
            print(f"   Candidates count: {len(items)}")
        
        # Test 4: POST /api/admin/zami/session/start (do NOT complete login)
        # Per instructions: "do NOT complete a real login"
        # We'll just verify the endpoint exists and returns expected structure
        print("\n   Note: Skipping POST /admin/zami/session/start to avoid triggering real OTP")
        print("   (Per instructions: do NOT complete a real login)")

    def test_public_endpoints_regression(self):
        """Test public endpoints still work (regression)"""
        print("\n\n🌐 TESTING PUBLIC ENDPOINTS (REGRESSION)")
        print("=" * 60)
        
        # Test /api/health
        success, response = self.test(
            "GET /health",
            "GET",
            "health",
            200
        )
        
        if success:
            print(f"   Status: {response.get('status')}")
        
        # Test /api/visa-types
        success, response = self.test(
            "GET /visa-types",
            "GET",
            "visa-types",
            200
        )
        
        if success:
            print(f"   Visa types count: {len(response) if isinstance(response, list) else 'N/A'}")
        
        # Test /api/content/site
        success, response = self.test(
            "GET /content/site",
            "GET",
            "content/site",
            200
        )
        
        if success:
            print(f"   Site content keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")
        
        # Test /api/fx
        success, response = self.test(
            "GET /fx",
            "GET",
            "fx",
            200
        )
        
        if success:
            print(f"   FX data present: {bool(response)}")
        
        # Test POST /api/applications (basic validation - should fail without proper data)
        success, response = self.test(
            "POST /applications (Invalid Data - Should Fail)",
            "POST",
            "applications",
            422,  # Expecting validation error
            data={}
        )
        
        if success:
            print(f"   ✅ Correctly validates application data")

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("VizeAtlas Dubai - OTP Once-a-Month Feature Testing")
        print(f"Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Admin login
        if not self.admin_login():
            print("\n❌ Cannot proceed without admin access")
            return 1
        
        # Run test suites
        self.test_new_session_fields()
        self.test_auto_renew_endpoint()
        self.test_existing_zami_endpoints()
        self.test_public_endpoints_regression()
        
        # Print summary
        print("\n\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print("=" * 60)
        
        # Important notes
        print("\n📝 IMPORTANT NOTES:")
        print("=" * 60)
        print("1. Playwright chromium warning in logs is EXPECTED (not a bug)")
        print("2. Zami portal session is currently expired (otp_required=true)")
        print("3. RPA endpoints returning 'oturum' errors is EXPECTED behavior")
        print("4. Auto-renew returning reason='otp_required' is ACCEPTABLE (not a bug)")
        print("5. Did NOT call DELETE /api/admin/zami/session (per instructions)")
        print("6. Called auto-renew only ONCE (per instructions)")
        print("=" * 60)
        
        return 0 if self.tests_failed == 0 else 1

def main():
    tester = OTPMonthlyTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
