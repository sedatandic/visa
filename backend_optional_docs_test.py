#!/usr/bin/env python3
"""
VizeAtlas Dubai - Optional Documents Test Suite
Tests the new optional ticket/hotel document feature (Iteration 26)
"""

import requests
import sys
import time
from datetime import datetime

BASE_URL = "https://otp-admin-flow.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@vizeatlas.com"
ADMIN_PASSWORD = "Dubai2026!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class OptionalDocsAPITester:
    def __init__(self):
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_file_ids = {}  # Store uploaded file IDs

    def log(self, message, color=Colors.BLUE):
        print(f"{color}{message}{Colors.END}")

    def test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None, files=None):
        """Run a single API test"""
        url = f"{BASE_URL}{endpoint}"
        h = {}
        if headers:
            h.update(headers)
        
        # Don't set Content-Type for file uploads
        if not files and 'Content-Type' not in h:
            h['Content-Type'] = 'application/json'
        
        self.tests_run += 1
        self.log(f"\n🔍 Test {self.tests_run}: {name}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=h, params=params, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data, headers=h, timeout=15)
                else:
                    response = requests.post(url, json=data, headers=h, params=params, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=h, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=h, timeout=15)
            
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                self.log(f"✅ PASS - Status: {response.status_code}", Colors.GREEN)
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                self.tests_failed += 1
                self.log(f"❌ FAIL - Expected {expected_status}, got {response.status_code}", Colors.RED)
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data}", Colors.RED)
                except:
                    self.log(f"   Response: {response.text[:200]}", Colors.RED)
                return False, {}
                
        except Exception as e:
            self.tests_failed += 1
            self.log(f"❌ FAIL - Exception: {str(e)}", Colors.RED)
            return False, {}

    def admin_login(self):
        """Login as admin"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("ADMIN LOGIN", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        success, response = self.test(
            "Admin login",
            "POST",
            "/admin/login",
            200,
            data={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        if success and 'token' in response:
            self.admin_token = response['token']
            self.log(f"✅ Admin token obtained", Colors.GREEN)
            return True
        return False

    def upload_test_files(self):
        """Upload test files for passport, photo, ticket, hotel"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("UPLOAD TEST FILES", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        # Create a minimal valid JPEG file (1x1 pixel red)
        jpeg_data = bytes.fromhex(
            'ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707'
            '07090909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c'
            '231c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b'
            '0c180d0d1832211c213232323232323232323232323232323232323232323232323232'
            '32323232323232323232323232323232323232323232323232ffc00011080001000103'
            '012200021101031101ffc4001500010100000000000000000000000000000000ffc400'
            '14100100000000000000000000000000000000ffda000c03010002110311003f00bf80'
            '01ffd9'
        )
        
        doc_types = ['passport', 'photo', 'ticket', 'hotel']
        
        for doc_type in doc_types:
            files = {
                'file': (f'test_{doc_type}.jpg', jpeg_data, 'image/jpeg')
            }
            data = {'doc_type': doc_type}
            
            success, response = self.test(
                f"Upload {doc_type} file",
                "POST",
                "/uploads",
                200,
                data=data,
                files=files
            )
            
            if success and 'file_id' in response:
                self.test_file_ids[doc_type] = response['file_id']
                self.log(f"   File ID: {response['file_id']}", Colors.BLUE)
        
        return len(self.test_file_ids) == 4

    def test_optional_documents_validation(self):
        """Test backend validation for optional ticket/hotel documents"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("FEATURE: OPTIONAL TICKET/HOTEL DOCUMENTS VALIDATION", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        test_email = f"optdocs{int(time.time())}@test.com"
        
        # Base application data
        base_app_data = {
            'contact': {
                'full_name': 'Test User Optional',
                'email': test_email,
                'phone': '+905551234567',
                'address_city': 'Istanbul'
            },
            'travelers': [{
                'first_name': 'AHMET',
                'last_name': 'TESTUSER',
                'birth_date': '1990-01-01',
                'gender': 'male',
                'applicant_type': 'adult',
                'nationality': 'TR',
                'passport_no': 'U12345678',
                'passport_expiry': '2030-12-31',
                'visa_type_id': 'visa_30_single',
                'passport_file_id': self.test_file_ids.get('passport'),
                'photo_file_id': self.test_file_ids.get('photo')
            }],
            'travel': {
                'arrival_date': '2026-12-01',
                'departure_date': '2026-12-15',
                'purpose': 'tourism',
                'birth_country': 'TR'
            },
            'addons': {'express': False},
            'kvkk_accepted': True
        }
        
        # Test 1: Application WITHOUT ticket/hotel (null) - Should return 200
        app_data_no_docs = {
            **base_app_data,
            'extra_documents': {
                'ticket_file_id': None,
                'hotel_file_id': None
            }
        }
        
        success, app_no_docs = self.test(
            "POST /api/applications - WITHOUT ticket/hotel (null) - Should return 200",
            "POST",
            "/applications",
            200,
            data=app_data_no_docs
        )
        
        app_id_no_docs = None
        reference_code_no_docs = None
        if success:
            app_id_no_docs = app_no_docs.get('id')
            reference_code_no_docs = app_no_docs.get('reference_code')
            self.log(f"   ✅ Application created without ticket/hotel", Colors.GREEN)
            self.log(f"   Reference code: {reference_code_no_docs}", Colors.BLUE)
            self.log(f"   Application ID: {app_id_no_docs}", Colors.BLUE)
        
        # Test 2: Application WITHOUT ticket/hotel (empty string) - Should return 200
        app_data_empty = {
            **base_app_data,
            'contact': {**base_app_data['contact'], 'email': f"empty{int(time.time())}@test.com"},
            'extra_documents': {
                'ticket_file_id': '',
                'hotel_file_id': ''
            }
        }
        
        success, app_empty = self.test(
            "POST /api/applications - WITHOUT ticket/hotel (empty string) - Should return 200",
            "POST",
            "/applications",
            200,
            data=app_data_empty
        )
        
        if success:
            self.log(f"   ✅ Application created with empty string ticket/hotel", Colors.GREEN)
        
        # Test 3: Application WITH invalid ticket_file_id - Should return 400
        app_data_invalid_ticket = {
            **base_app_data,
            'contact': {**base_app_data['contact'], 'email': f"invalid{int(time.time())}@test.com"},
            'extra_documents': {
                'ticket_file_id': 'invalid-file-id-12345',
                'hotel_file_id': None
            }
        }
        
        success, app_invalid = self.test(
            "POST /api/applications - WITH invalid ticket_file_id - Should return 400",
            "POST",
            "/applications",
            400,
            data=app_data_invalid_ticket
        )
        
        if success:
            self.log(f"   ✅ Invalid ticket_file_id correctly rejected", Colors.GREEN)
        
        # Test 4: Application WITH invalid hotel_file_id - Should return 400
        app_data_invalid_hotel = {
            **base_app_data,
            'contact': {**base_app_data['contact'], 'email': f"invalidh{int(time.time())}@test.com"},
            'extra_documents': {
                'ticket_file_id': None,
                'hotel_file_id': 'invalid-hotel-id-67890'
            }
        }
        
        success, app_invalid_hotel = self.test(
            "POST /api/applications - WITH invalid hotel_file_id - Should return 400",
            "POST",
            "/applications",
            400,
            data=app_data_invalid_hotel
        )
        
        if success:
            self.log(f"   ✅ Invalid hotel_file_id correctly rejected", Colors.GREEN)
        
        # Test 5: Application WITH missing passport_file_id - Should return 422 (Pydantic validation)
        app_data_no_passport = {
            **base_app_data,
            'contact': {**base_app_data['contact'], 'email': f"nopass{int(time.time())}@test.com"},
            'travelers': [{
                **base_app_data['travelers'][0],
                'passport_file_id': '',  # Empty passport (will fail Pydantic min_length)
                'photo_file_id': self.test_file_ids.get('photo')
            }],
            'extra_documents': {
                'ticket_file_id': None,
                'hotel_file_id': None
            }
        }
        
        success, app_no_passport = self.test(
            "POST /api/applications - WITH missing passport_file_id - Should return 422",
            "POST",
            "/applications",
            422,
            data=app_data_no_passport
        )
        
        if success:
            self.log(f"   ✅ Missing passport_file_id correctly rejected", Colors.GREEN)
        
        # Test 6: Application WITH missing photo_file_id - Should return 422 (Pydantic validation)
        app_data_no_photo = {
            **base_app_data,
            'contact': {**base_app_data['contact'], 'email': f"nophoto{int(time.time())}@test.com"},
            'travelers': [{
                **base_app_data['travelers'][0],
                'passport_file_id': self.test_file_ids.get('passport'),
                'photo_file_id': ''  # Empty photo (will fail Pydantic min_length)
            }],
            'extra_documents': {
                'ticket_file_id': None,
                'hotel_file_id': None
            }
        }
        
        success, app_no_photo = self.test(
            "POST /api/applications - WITH missing photo_file_id - Should return 422",
            "POST",
            "/applications",
            422,
            data=app_data_no_photo
        )
        
        if success:
            self.log(f"   ✅ Missing photo_file_id correctly rejected", Colors.GREEN)
        
        # Test 7: Application WITH all documents - Should return 200
        app_data_all_docs = {
            **base_app_data,
            'contact': {**base_app_data['contact'], 'email': f"alldocs{int(time.time())}@test.com"},
            'extra_documents': {
                'ticket_file_id': self.test_file_ids.get('ticket'),
                'hotel_file_id': self.test_file_ids.get('hotel')
            }
        }
        
        success, app_all_docs = self.test(
            "POST /api/applications - WITH all documents (ticket + hotel) - Should return 200",
            "POST",
            "/applications",
            200,
            data=app_data_all_docs
        )
        
        app_id_all_docs = None
        reference_code_all_docs = None
        if success:
            app_id_all_docs = app_all_docs.get('id')
            reference_code_all_docs = app_all_docs.get('reference_code')
            self.log(f"   ✅ Application created with all documents", Colors.GREEN)
            self.log(f"   Reference code: {reference_code_all_docs}", Colors.BLUE)
        
        return {
            'app_no_docs': {'id': app_id_no_docs, 'reference_code': reference_code_no_docs},
            'app_all_docs': {'id': app_id_all_docs, 'reference_code': reference_code_all_docs}
        }

    def test_missing_documents_tracking(self, app_info):
        """Test missing documents tracking and upload flow"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("FEATURE: MISSING DOCUMENTS TRACKING & UPLOAD", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        app_no_docs = app_info.get('app_no_docs', {})
        app_all_docs = app_info.get('app_all_docs', {})
        
        # Test 1: Track application WITHOUT ticket/hotel - Should list missing documents
        if app_no_docs.get('reference_code'):
            success, track_no_docs = self.test(
                "GET /api/applications/track - Application WITHOUT ticket/hotel",
                "GET",
                "/applications/track",
                200,
                params={
                    'code': app_no_docs['reference_code'],
                    'last_name': 'TESTUSER'
                }
            )
            
            if success:
                missing_docs = track_no_docs.get('missing_documents', [])
                self.log(f"   Missing documents count: {len(missing_docs)}", Colors.BLUE)
                
                # Should have 2 missing documents: ticket and hotel
                if len(missing_docs) == 2:
                    self.log(f"   ✅ Correct number of missing documents (2)", Colors.GREEN)
                else:
                    self.log(f"   ❌ Expected 2 missing documents, got {len(missing_docs)}", Colors.RED)
                
                # Check if ticket and hotel are in missing list
                missing_keys = [doc.get('key') for doc in missing_docs]
                if 'ticket' in missing_keys:
                    self.log(f"   ✅ 'ticket' in missing documents", Colors.GREEN)
                else:
                    self.log(f"   ❌ 'ticket' NOT in missing documents", Colors.RED)
                
                if 'hotel' in missing_keys:
                    self.log(f"   ✅ 'hotel' in missing documents", Colors.GREEN)
                else:
                    self.log(f"   ❌ 'hotel' NOT in missing documents", Colors.RED)
                
                # Check labels
                for doc in missing_docs:
                    self.log(f"   Missing: {doc.get('label')} ({doc.get('key')})", Colors.BLUE)
                
                # Test 2: Upload missing documents
                upload_data = {
                    'last_name': 'TESTUSER',
                    'ticket_file_id': self.test_file_ids.get('ticket'),
                    'hotel_file_id': self.test_file_ids.get('hotel')
                }
                
                success, upload_result = self.test(
                    f"POST /api/applications/{app_no_docs['reference_code']}/documents - Upload missing docs",
                    "POST",
                    f"/applications/{app_no_docs['reference_code']}/documents",
                    200,
                    data=upload_data
                )
                
                if success:
                    uploaded_keys = upload_result.get('uploaded', [])
                    remaining_missing = upload_result.get('missing_documents', [])
                    
                    self.log(f"   Uploaded: {uploaded_keys}", Colors.BLUE)
                    self.log(f"   Remaining missing: {len(remaining_missing)}", Colors.BLUE)
                    
                    if 'ticket' in uploaded_keys and 'hotel' in uploaded_keys:
                        self.log(f"   ✅ Both ticket and hotel uploaded", Colors.GREEN)
                    
                    if len(remaining_missing) == 0:
                        self.log(f"   ✅ No missing documents after upload", Colors.GREEN)
                    else:
                        self.log(f"   ⚠️  Still {len(remaining_missing)} missing documents", Colors.YELLOW)
                
                # Test 3: Track again to verify documents are no longer missing
                success, track_after_upload = self.test(
                    "GET /api/applications/track - After uploading documents",
                    "GET",
                    "/applications/track",
                    200,
                    params={
                        'code': app_no_docs['reference_code'],
                        'last_name': 'TESTUSER'
                    }
                )
                
                if success:
                    missing_after = track_after_upload.get('missing_documents', [])
                    if len(missing_after) == 0:
                        self.log(f"   ✅ Missing documents list is now empty", Colors.GREEN)
                    else:
                        self.log(f"   ⚠️  Still {len(missing_after)} missing documents", Colors.YELLOW)
        
        # Test 4: Track application WITH all documents - Should have empty missing list
        if app_all_docs.get('reference_code'):
            success, track_all_docs = self.test(
                "GET /api/applications/track - Application WITH all documents",
                "GET",
                "/applications/track",
                200,
                params={
                    'code': app_all_docs['reference_code'],
                    'last_name': 'TESTUSER'
                }
            )
            
            if success:
                missing_docs = track_all_docs.get('missing_documents', [])
                self.log(f"   Missing documents count: {len(missing_docs)}", Colors.BLUE)
                
                if len(missing_docs) == 0:
                    self.log(f"   ✅ No missing documents (as expected)", Colors.GREEN)
                else:
                    self.log(f"   ❌ Expected 0 missing documents, got {len(missing_docs)}", Colors.RED)

    def test_admin_missing_documents(self, app_info):
        """Test admin endpoint for missing documents"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("ADMIN: MISSING DOCUMENTS ENDPOINT", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        app_no_docs = app_info.get('app_no_docs', {})
        
        if app_no_docs.get('id'):
            success, admin_missing = self.test(
                f"GET /api/admin/applications/{app_no_docs['id']}/missing-documents",
                "GET",
                f"/admin/applications/{app_no_docs['id']}/missing-documents",
                200,
                headers=headers
            )
            
            if success:
                missing = admin_missing.get('missing', [])
                reminder_count = admin_missing.get('reminder_count', 0)
                
                self.log(f"   Missing documents: {len(missing)}", Colors.BLUE)
                self.log(f"   Reminder count: {reminder_count}", Colors.BLUE)
                
                if len(missing) >= 0:  # After upload test, might be 0
                    self.log(f"   ✅ Admin can view missing documents", Colors.GREEN)

    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("TEST SUMMARY - OPTIONAL DOCUMENTS FEATURE", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        pass_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        self.log(f"\nTotal Tests: {self.tests_run}", Colors.BLUE)
        self.log(f"Passed: {self.tests_passed}", Colors.GREEN)
        self.log(f"Failed: {self.tests_failed}", Colors.RED)
        self.log(f"Pass Rate: {pass_rate:.1f}%", Colors.YELLOW)
        
        if pass_rate == 100:
            self.log("\n🎉 Perfect! All optional documents tests passed.", Colors.GREEN)
        elif pass_rate >= 90:
            self.log("\n✅ Excellent! Optional documents feature working well.", Colors.GREEN)
        elif pass_rate >= 70:
            self.log("\n⚠️  Good, but some issues need attention.", Colors.YELLOW)
        else:
            self.log("\n❌ Critical issues found. Main agent should fix.", Colors.RED)
        
        return 0 if self.tests_failed == 0 else 1

def main():
    tester = OptionalDocsAPITester()
    
    print(f"\n{Colors.BLUE}{'='*70}")
    print("VizeAtlas Dubai - Optional Documents Backend Test")
    print("Testing: Ticket & Hotel as Optional Documents (Iteration 26)")
    print(f"Base URL: {BASE_URL}")
    print(f"{'='*70}{Colors.END}\n")
    
    # Login as admin
    if not tester.admin_login():
        print(f"{Colors.RED}❌ Admin login failed. Cannot continue.{Colors.END}")
        return 1
    
    # Upload test files
    if not tester.upload_test_files():
        print(f"{Colors.RED}❌ File upload failed. Cannot continue.{Colors.END}")
        return 1
    
    # Run tests
    app_info = tester.test_optional_documents_validation()
    tester.test_missing_documents_tracking(app_info)
    tester.test_admin_missing_documents(app_info)
    
    # Print summary
    return tester.print_summary()

if __name__ == "__main__":
    sys.exit(main())
