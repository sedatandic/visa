#!/usr/bin/env python3
"""
VizeAtlas Dubai - Zami Refactoring Test (Iteration 2)
Tests the refactored zami.py functions: save_mapping and build_payload
BEHAVIOR MUST NOT CHANGE after refactoring.
"""
import requests
import sys
import json
from datetime import datetime, timedelta

# Get backend URL from frontend .env
try:
    with open("/app/frontend/.env", "r") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip()
                break
except Exception:
    BASE_URL = "https://whatsapp-ai-test.preview.emergentagent.com"

API_BASE = f"{BASE_URL}/api"

class ZamiRefactorTester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.admin_token = None
        self.test_app_id = None
        self.original_mapping = None
        self.results = []

    def test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test"""
        url = f"{API_BASE}/{endpoint}"
        req_headers = {'Content-Type': 'application/json'}
        if headers:
            req_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 {name}...")
        
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
                print(f"✅ PASS - Status: {response.status_code}")
                try:
                    result_data = response.json() if response.text else {}
                except:
                    result_data = {}
                self.results.append({
                    "test": name,
                    "status": "passed",
                    "http_status": response.status_code
                })
                return True, result_data
            else:
                self.tests_failed += 1
                print(f"❌ FAIL - Expected {expected_status}, got {response.status_code}")
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
            print(f"❌ ERROR - {str(e)}")
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

    def test_mapping_persistence(self):
        """CRITICAL - Test GET /api/admin/zami/config mapping structure"""
        print("\n\n" + "="*70)
        print("🔍 CRITICAL TEST 1: Zami Mapping Persistence")
        print("="*70)
        
        if not self.admin_token:
            print("❌ No admin token")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        success, response = self.test(
            "GET /api/admin/zami/config",
            "GET",
            "admin/zami/config",
            200,
            headers=headers
        )
        
        if not success:
            return
        
        mapping = response.get('mapping', {})
        self.original_mapping = mapping  # Save for restoration later
        
        # Verify form_url
        expected_form_url = "https://visa.zamitours.ae/?_=203&s=smrtch.edit"
        actual_form_url = mapping.get('form_url', '')
        if actual_form_url == expected_form_url:
            print(f"✅ form_url correct: {actual_form_url}")
        else:
            print(f"❌ form_url incorrect: {actual_form_url}")
            print(f"   Expected: {expected_form_url}")
        
        # Verify fields (should be 8)
        fields = mapping.get('fields', {})
        if len(fields) == 8:
            print(f"✅ fields count: 8")
        else:
            print(f"❌ fields count: {len(fields)}, expected 8")
        
        # Check specific field mappings
        expected_fields = {
            'travel.arrival_date_dmy_dash': '[name="ad"]',
            'reference_code': '[name="dr_rf"]',
            'travel.notes': '[name="vs_cm"]',
            'zami_visa_type': '[name="dr_tp"]',
            'birth_country_label': '[name="bc_tt"]',
            'contact.phone_intl': '[name="mp"]',
            'zami_group_membership': '[name="gp"]',
            'zami_total_members': '[name="gp_f"]'
        }
        
        for key, expected_selector in expected_fields.items():
            actual_selector = fields.get(key)
            if actual_selector == expected_selector:
                print(f"✅ fields['{key}'] = {expected_selector}")
            else:
                print(f"❌ fields['{key}'] = {actual_selector}, expected {expected_selector}")
        
        # Verify traveler_fields (should be 16)
        traveler_fields = mapping.get('traveler_fields', {})
        if len(traveler_fields) == 16:
            print(f"✅ traveler_fields count: 16")
        else:
            print(f"❌ traveler_fields count: {len(traveler_fields)}, expected 16")
        
        # Check critical traveler fields
        critical_traveler_fields = ['marital_status_label', 'profession', 'mother_name', 'father_name']
        for key in critical_traveler_fields:
            if key in traveler_fields:
                print(f"✅ traveler_fields contains '{key}': {traveler_fields[key]}")
            else:
                print(f"❌ traveler_fields missing '{key}'")
        
        # Verify constants (should be 7, and [name="ms"] should NOT be in constants)
        constants = mapping.get('constants', {})
        if len(constants) == 7:
            print(f"✅ constants count: 7")
        else:
            print(f"❌ constants count: {len(constants)}, expected 7")
        
        if '[name="ms"]' not in constants:
            print(f"✅ [name=\"ms\"] NOT in constants (correct - it's in traveler_fields)")
        else:
            print(f"❌ [name=\"ms\"] found in constants (should be in traveler_fields only)")
        
        # Verify status_url
        expected_status_url = "https://visa.zamitours.ae/?_=203&s=vs.search"
        actual_status_url = mapping.get('status_url', '')
        if actual_status_url == expected_status_url:
            print(f"✅ status_url correct")
        else:
            print(f"❌ status_url: {actual_status_url}")
        
        # Verify status_search_selector
        if mapping.get('status_search_selector') == '[name="pn"]':
            print(f"✅ status_search_selector: [name=\"pn\"]")
        else:
            print(f"❌ status_search_selector: {mapping.get('status_search_selector')}")
        
        # Verify validate_selector
        if mapping.get('validate_selector') == 'button:has-text("CHECK")':
            print(f"✅ validate_selector correct")
        else:
            print(f"❌ validate_selector: {mapping.get('validate_selector')}")
        
        # Verify auto_check settings
        if mapping.get('auto_check_enabled') == True:
            print(f"✅ auto_check_enabled: true")
        else:
            print(f"❌ auto_check_enabled: {mapping.get('auto_check_enabled')}")
        
        if mapping.get('auto_check_hours') == 6:
            print(f"✅ auto_check_hours: 6")
        else:
            print(f"❌ auto_check_hours: {mapping.get('auto_check_hours')}")
        
        if mapping.get('auto_notify') == True:
            print(f"✅ auto_notify: true")
        else:
            print(f"❌ auto_notify: {mapping.get('auto_notify')}")
        
        # Verify upload_targets (should be 2)
        upload_targets = mapping.get('upload_targets', [])
        if len(upload_targets) == 2:
            print(f"✅ upload_targets count: 2")
        else:
            print(f"❌ upload_targets count: {len(upload_targets)}, expected 2")

    def test_mapping_normalization(self):
        """CRITICAL - Test PUT /api/admin/zami/mapping normalization behavior"""
        print("\n\n" + "="*70)
        print("🔍 CRITICAL TEST 2: Mapping Normalization Behavior")
        print("="*70)
        
        if not self.admin_token:
            print("❌ No admin token")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Test (a): Empty values in fields/constants/traveler_fields should be dropped
        print("\n--- Test (a): Empty values should be dropped ---")
        test_mapping = {
            "form_url": "https://test.com",
            "fields": {
                "reference_code": '[name="ref"]',
                "empty_field": "",
                "another_field": '[name="test"]'
            },
            "constants": {
                '[name="valid"]': "value",
                '[name="empty"]': ""
            },
            "traveler_fields": {
                "first_name": '[name="fn"]',
                "empty_traveler": ""
            }
        }
        
        success, response = self.test(
            "PUT /api/admin/zami/mapping (empty values)",
            "PUT",
            "admin/zami/mapping",
            200,
            data=test_mapping,
            headers=headers
        )
        
        if success:
            mapping = response.get('mapping', {})
            fields = mapping.get('fields', {})
            constants = mapping.get('constants', {})
            traveler_fields = mapping.get('traveler_fields', {})
            
            if 'empty_field' not in fields:
                print(f"✅ Empty field dropped from fields")
            else:
                print(f"❌ Empty field NOT dropped: {fields.get('empty_field')}")
            
            if '[name="empty"]' not in constants:
                print(f"✅ Empty constant dropped")
            else:
                print(f"❌ Empty constant NOT dropped")
            
            if 'empty_traveler' not in traveler_fields:
                print(f"✅ Empty traveler_field dropped")
            else:
                print(f"❌ Empty traveler_field NOT dropped")
        
        # Test (b): Empty helper_selectors list should revert to default
        print("\n--- Test (b): Empty helper_selectors -> default ---")
        test_mapping = {
            "form_url": "https://test.com",
            "helper_selectors": []
        }
        
        success, response = self.test(
            "PUT /api/admin/zami/mapping (empty helper_selectors)",
            "PUT",
            "admin/zami/mapping",
            200,
            data=test_mapping,
            headers=headers
        )
        
        if success:
            mapping = response.get('mapping', {})
            helper_selectors = mapping.get('helper_selectors', [])
            if len(helper_selectors) > 0 and 'TRANSLATE TO ARABIC' in str(helper_selectors):
                print(f"✅ Empty helper_selectors reverted to default: {helper_selectors}")
            else:
                print(f"❌ helper_selectors: {helper_selectors}")
        
        # Test (c): Empty upload_targets should revert to default
        print("\n--- Test (c): Empty/invalid upload_targets -> default ---")
        test_mapping = {
            "form_url": "https://test.com",
            "upload_targets": [
                {"doc": "passport"},  # Missing selector
                {"selector": "test"}  # Missing doc
            ]
        }
        
        success, response = self.test(
            "PUT /api/admin/zami/mapping (invalid upload_targets)",
            "PUT",
            "admin/zami/mapping",
            200,
            data=test_mapping,
            headers=headers
        )
        
        if success:
            mapping = response.get('mapping', {})
            upload_targets = mapping.get('upload_targets', [])
            if len(upload_targets) == 2 and any('passport' in str(t) for t in upload_targets):
                print(f"✅ Invalid upload_targets reverted to default (2 items)")
            else:
                print(f"❌ upload_targets: {upload_targets}")
        
        # Test (d): auto_check_hours clamping
        print("\n--- Test (d): auto_check_hours clamping (1-48) ---")
        
        # Test 0 -> 6
        test_mapping = {"form_url": "https://test.com", "auto_check_hours": 0}
        success, response = self.test(
            "PUT /api/admin/zami/mapping (auto_check_hours=0)",
            "PUT",
            "admin/zami/mapping",
            200,
            data=test_mapping,
            headers=headers
        )
        if success:
            hours = response.get('mapping', {}).get('auto_check_hours')
            if hours == 6:
                print(f"✅ auto_check_hours=0 clamped to 6")
            else:
                print(f"❌ auto_check_hours=0 resulted in {hours}, expected 6")
        
        # Test 99 -> 48
        test_mapping = {"form_url": "https://test.com", "auto_check_hours": 99}
        success, response = self.test(
            "PUT /api/admin/zami/mapping (auto_check_hours=99)",
            "PUT",
            "admin/zami/mapping",
            200,
            data=test_mapping,
            headers=headers
        )
        if success:
            hours = response.get('mapping', {}).get('auto_check_hours')
            if hours == 48:
                print(f"✅ auto_check_hours=99 clamped to 48")
            else:
                print(f"❌ auto_check_hours=99 resulted in {hours}, expected 48")
        
        # Test -5 -> 1
        test_mapping = {"form_url": "https://test.com", "auto_check_hours": -5}
        success, response = self.test(
            "PUT /api/admin/zami/mapping (auto_check_hours=-5)",
            "PUT",
            "admin/zami/mapping",
            200,
            data=test_mapping,
            headers=headers
        )
        if success:
            hours = response.get('mapping', {}).get('auto_check_hours')
            if hours == 1:
                print(f"✅ auto_check_hours=-5 clamped to 1")
            else:
                print(f"❌ auto_check_hours=-5 resulted in {hours}, expected 1")
        
        # Test (e): status_keywords empty dict -> default, lowercase
        print("\n--- Test (e): status_keywords normalization ---")
        test_mapping = {
            "form_url": "https://test.com",
            "status_keywords": {}
        }
        
        success, response = self.test(
            "PUT /api/admin/zami/mapping (empty status_keywords)",
            "PUT",
            "admin/zami/mapping",
            200,
            data=test_mapping,
            headers=headers
        )
        
        if success:
            mapping = response.get('mapping', {})
            keywords = mapping.get('status_keywords', {})
            if 'approved' in keywords and 'rejected' in keywords and 'reviewing' in keywords:
                print(f"✅ Empty status_keywords reverted to default")
                # Check lowercase
                all_lowercase = all(
                    all(word.islower() for word in words)
                    for words in keywords.values()
                )
                if all_lowercase:
                    print(f"✅ All keywords are lowercase")
                else:
                    print(f"❌ Some keywords not lowercase")
            else:
                print(f"❌ status_keywords: {keywords}")
        
        # Test (f): form_url/status_url trimming
        print("\n--- Test (f): URL trimming ---")
        test_mapping = {
            "form_url": "  https://test.com/form  ",
            "status_url": "  https://test.com/status  "
        }
        
        success, response = self.test(
            "PUT /api/admin/zami/mapping (URLs with whitespace)",
            "PUT",
            "admin/zami/mapping",
            200,
            data=test_mapping,
            headers=headers
        )
        
        if success:
            mapping = response.get('mapping', {})
            form_url = mapping.get('form_url', '')
            status_url = mapping.get('status_url', '')
            
            if form_url == "https://test.com/form":
                print(f"✅ form_url trimmed correctly")
            else:
                print(f"❌ form_url: '{form_url}'")
            
            if status_url == "https://test.com/status":
                print(f"✅ status_url trimmed correctly")
            else:
                print(f"❌ status_url: '{status_url}'")
        
        # Test (g): validate_selector and status_submit_selector
        print("\n--- Test (g): Selector handling (empty string vs None) ---")
        
        # Empty string should be accepted
        test_mapping = {
            "form_url": "https://test.com",
            "validate_selector": "",
            "status_submit_selector": ""
        }
        
        success, response = self.test(
            "PUT /api/admin/zami/mapping (empty string selectors)",
            "PUT",
            "admin/zami/mapping",
            200,
            data=test_mapping,
            headers=headers
        )
        
        if success:
            mapping = response.get('mapping', {})
            validate_sel = mapping.get('validate_selector')
            submit_sel = mapping.get('status_submit_selector')
            
            if validate_sel == "":
                print(f"✅ validate_selector empty string accepted")
            else:
                print(f"❌ validate_selector: '{validate_sel}' (expected empty string)")
            
            if submit_sel == "":
                print(f"✅ status_submit_selector empty string accepted")
            else:
                print(f"❌ status_submit_selector: '{submit_sel}' (expected empty string)")
        
        # None should revert to default
        test_mapping = {
            "form_url": "https://test.com",
            "validate_selector": None,
            "status_submit_selector": None
        }
        
        success, response = self.test(
            "PUT /api/admin/zami/mapping (None selectors)",
            "PUT",
            "admin/zami/mapping",
            200,
            data=test_mapping,
            headers=headers
        )
        
        if success:
            mapping = response.get('mapping', {})
            validate_sel = mapping.get('validate_selector')
            submit_sel = mapping.get('status_submit_selector')
            
            if validate_sel and 'CHECK' in validate_sel:
                print(f"✅ validate_selector None reverted to default")
            else:
                print(f"❌ validate_selector: '{validate_sel}'")
            
            if submit_sel and 'SEARCH' in submit_sel:
                print(f"✅ status_submit_selector None reverted to default")
            else:
                print(f"❌ status_submit_selector: '{submit_sel}'")

    def restore_original_mapping(self):
        """Restore the original mapping after tests"""
        print("\n\n" + "="*70)
        print("🔄 RESTORING ORIGINAL MAPPING")
        print("="*70)
        
        print("\nRunning: cd /app/scripts && python zami_save_mapping.py")
        import subprocess
        try:
            result = subprocess.run(
                ["python", "/app/scripts/zami_save_mapping.py"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("✅ Original mapping restored successfully")
                print(result.stdout[:500])
            else:
                print(f"❌ Failed to restore mapping: {result.stderr}")
        except Exception as e:
            print(f"❌ Error restoring mapping: {str(e)}")

    def create_test_application(self):
        """Create a test application for payload testing"""
        print("\n\n" + "="*70)
        print("📝 Creating Test Application for Payload Tests")
        print("="*70)
        
        # Get visa types
        success, visa_response = self.test(
            "GET /api/visa-types",
            "GET",
            "visa-types",
            200
        )
        
        if not success:
            return None
        
        adult_visas = [v for v in visa_response if v.get('category') != 'child']
        if not adult_visas:
            print("❌ No adult visa types found")
            return None
        
        visa_id = adult_visas[0]['id']
        
        # Upload files
        import io
        import base64
        jpeg_data = base64.b64decode('/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k=')
        
        try:
            files = {'file': ('passport.jpg', io.BytesIO(jpeg_data), 'image/jpeg')}
            form_data = {'doc_type': 'passport'}
            upload_response = requests.post(f"{API_BASE}/uploads", files=files, data=form_data, timeout=30)
            passport_file_id = upload_response.json().get('file_id')
            
            files = {'file': ('photo.jpg', io.BytesIO(jpeg_data), 'image/jpeg')}
            form_data = {'doc_type': 'photo'}
            upload_response = requests.post(f"{API_BASE}/uploads", files=files, data=form_data, timeout=30)
            photo_file_id = upload_response.json().get('file_id')
            
            print(f"✅ Files uploaded")
        except Exception as e:
            print(f"❌ File upload failed: {str(e)}")
            return None
        
        # Create application with 2 travelers (for family logic test)
        today = datetime.now()
        arrival = (today + timedelta(days=30)).strftime('%Y-%m-%d')
        departure = (today + timedelta(days=37)).strftime('%Y-%m-%d')
        
        app_data = {
            "contact": {
                "full_name": "Test Zami User",
                "email": "test.zami@example.com",
                "phone": "05551234567",
                "address_city": "Istanbul",
                "whatsapp_optin": False
            },
            "travelers": [
                {
                    "first_name": "AHMET",
                    "last_name": "YILMAZ",
                    "birth_date": "1990-01-15",
                    "gender": "male",
                    "applicant_type": "adult",
                    "nationality": "TR",
                    "national_id": "12345678901",
                    "passport_no": "U12345678",
                    "passport_expiry": "2030-12-31",
                    "passport_issue_date": "2020-01-01",
                    "birth_place": "Istanbul",
                    "passport_issue_place": "Istanbul",
                    "marital_status": "married",
                    "profession": "Engineer",
                    "mother_name": "AYSE",
                    "father_name": "MEHMET",
                    "visa_type_id": visa_id,
                    "passport_file_id": passport_file_id,
                    "photo_file_id": photo_file_id
                },
                {
                    "first_name": "FATMA",
                    "last_name": "YILMAZ",
                    "birth_date": "1992-05-20",
                    "gender": "female",
                    "applicant_type": "adult",
                    "nationality": "TR",
                    "national_id": "98765432109",
                    "passport_no": "U98765432",
                    "passport_expiry": "2029-06-30",
                    "passport_issue_date": "2019-06-01",
                    "birth_place": "Ankara",
                    "passport_issue_place": "Ankara",
                    "marital_status": "married",
                    "profession": "Teacher",
                    "mother_name": "ZEYNEP",
                    "father_name": "ALI",
                    "visa_type_id": visa_id,
                    "passport_file_id": passport_file_id,
                    "photo_file_id": photo_file_id
                }
            ],
            "travel": {
                "arrival_date": arrival,
                "departure_date": departure,
                "purpose": "tourism",
                "birth_country": "TR",
                "accommodation": "Grand Hotel Dubai",
                "flight_no": "TK123",
                "notes": "Test application for Zami payload"
            },
            "addons": {"express": False, "insurance": False},
            "store_items": [],
            "extra_documents": {
                "ticket_file_id": None,
                "hotel_file_id": None,
                "other_file_ids": []
            },
            "kvkk_accepted": True
        }
        
        success, response = self.test(
            "POST /api/applications (2 travelers)",
            "POST",
            "applications",
            200,
            data=app_data
        )
        
        if success:
            app_id = response.get('id')
            ref_code = response.get('reference_code')
            print(f"✅ Application created: {ref_code} (ID: {app_id})")
            return app_id
        
        return None

    def test_payload_structure(self, app_id):
        """REGRESSION - Test GET /api/admin/zami/payload/{application_id}"""
        print("\n\n" + "="*70)
        print("🔍 REGRESSION TEST 3: Payload Structure")
        print("="*70)
        
        if not self.admin_token or not app_id:
            print("❌ Missing admin token or app_id")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        success, payload = self.test(
            f"GET /api/admin/zami/payload/{app_id}",
            "GET",
            f"admin/zami/payload/{app_id}",
            200,
            headers=headers
        )
        
        if not success:
            return
        
        # Check top-level keys
        expected_top_keys = ['application_id', 'reference_code', 'globals', 'travelers', 'documents']
        actual_top_keys = list(payload.keys())
        
        if set(actual_top_keys) == set(expected_top_keys):
            print(f"✅ Top-level keys correct: {expected_top_keys}")
        else:
            print(f"❌ Top-level keys: {actual_top_keys}")
            print(f"   Expected: {expected_top_keys}")
        
        # Check globals (should have exactly 24 keys)
        globals_dict = payload.get('globals', {})
        globals_count = len(globals_dict)
        
        if globals_count == 24:
            print(f"✅ globals has exactly 24 keys")
        else:
            print(f"❌ globals has {globals_count} keys, expected 24")
            print(f"   Keys: {list(globals_dict.keys())}")
        
        # Verify specific globals keys
        expected_globals_keys = [
            'reference_code', 'contact.full_name', 'contact.email', 'contact.phone',
            'contact.phone_intl', 'contact.address_city',
            'travel.arrival_date', 'travel.arrival_date_dmy', 'travel.arrival_date_dmy_dash', 'travel.arrival_date_mdy',
            'travel.departure_date', 'travel.departure_date_dmy', 'travel.departure_date_dmy_dash', 'travel.departure_date_mdy',
            'travel.purpose', 'travel.accommodation', 'travel.flight_no', 'travel.notes',
            'visa_type_name', 'zami_visa_type', 'birth_country_label',
            'zami_group_membership', 'zami_total_members', 'traveler_count'
        ]
        
        missing_keys = [k for k in expected_globals_keys if k not in globals_dict]
        if not missing_keys:
            print(f"✅ All expected globals keys present")
        else:
            print(f"❌ Missing globals keys: {missing_keys}")
        
        # Check travelers[0] (should have exactly 34 keys)
        travelers = payload.get('travelers', [])
        if len(travelers) >= 1:
            traveler0 = travelers[0]
            traveler0_count = len(traveler0)
            
            if traveler0_count == 34:
                print(f"✅ travelers[0] has exactly 34 keys")
            else:
                print(f"❌ travelers[0] has {traveler0_count} keys, expected 34")
                print(f"   Keys: {list(traveler0.keys())}")
            
            # Check birth_date formats (4 formats)
            birth_date_keys = ['birth_date', 'birth_date_dmy', 'birth_date_dmy_dash', 'birth_date_mdy']
            birth_date_present = [k for k in birth_date_keys if k in traveler0]
            if len(birth_date_present) == 4:
                print(f"✅ birth_date has 4 formats: {birth_date_present}")
            else:
                print(f"❌ birth_date formats: {birth_date_present}, expected 4")
            
            # Check passport_expiry formats (4 formats)
            passport_expiry_keys = ['passport_expiry', 'passport_expiry_dmy', 'passport_expiry_dmy_dash', 'passport_expiry_mdy']
            passport_expiry_present = [k for k in passport_expiry_keys if k in traveler0]
            if len(passport_expiry_present) == 4:
                print(f"✅ passport_expiry has 4 formats: {passport_expiry_present}")
            else:
                print(f"❌ passport_expiry formats: {passport_expiry_present}, expected 4")
            
            # Check passport_issue_date formats (ONLY 3 formats - NO _mdy)
            passport_issue_keys = ['passport_issue_date', 'passport_issue_date_dmy', 'passport_issue_date_dmy_dash']
            passport_issue_present = [k for k in passport_issue_keys if k in traveler0]
            passport_issue_mdy_present = 'passport_issue_date_mdy' in traveler0
            
            if len(passport_issue_present) == 3 and not passport_issue_mdy_present:
                print(f"✅ passport_issue_date has ONLY 3 formats (no _mdy): {passport_issue_present}")
            else:
                print(f"❌ passport_issue_date issue:")
                print(f"   Present: {passport_issue_present}")
                if passport_issue_mdy_present:
                    print(f"   ERROR: passport_issue_date_mdy should NOT exist")
            
            # Check marital_status_label is English
            marital_status_label = traveler0.get('marital_status_label', '')
            if marital_status_label in ['Single', 'Married', 'Divorced', 'Widowed']:
                print(f"✅ marital_status_label is English: '{marital_status_label}'")
            else:
                print(f"❌ marital_status_label: '{marital_status_label}' (expected English)")
        else:
            print(f"❌ No travelers in payload")
        
        # Check documents list format
        documents = payload.get('documents', [])
        if len(documents) > 0:
            print(f"✅ documents list has {len(documents)} items")
            
            # Check first document format
            doc0 = documents[0]
            if 'label' in doc0 and 'url' in doc0 and 'traveler_index' in doc0:
                print(f"✅ Document format correct: {doc0.get('label')}")
            else:
                print(f"❌ Document format incorrect: {doc0}")
        else:
            print(f"⚠️  No documents in payload")
        
        # Test group/family logic (2 travelers)
        zami_group = globals_dict.get('zami_group_membership', '')
        zami_total = globals_dict.get('zami_total_members', '')
        
        if zami_group == 'Family Main Person':
            print(f"✅ zami_group_membership: 'Family Main Person' (2+ travelers)")
        else:
            print(f"❌ zami_group_membership: '{zami_group}', expected 'Family Main Person'")
        
        if zami_total == '2':
            print(f"✅ zami_total_members: '2' (string)")
        else:
            print(f"❌ zami_total_members: '{zami_total}', expected '2'")

    def test_pricing_regression(self):
        """REGRESSION - Test pricing computation"""
        print("\n\n" + "="*70)
        print("🔍 REGRESSION TEST 4: Pricing Computation")
        print("="*70)
        
        # Get visa types
        success, visa_response = self.test(
            "GET /api/visa-types",
            "GET",
            "visa-types",
            200
        )
        
        if not success:
            return
        
        adult_visas = [v for v in visa_response if v.get('category') != 'child']
        if not adult_visas:
            print("❌ No adult visa types found")
            return
        
        visa_id = adult_visas[0]['id']
        
        # Test 1: 1 traveler -> family_discount=0
        print("\n--- Test 1: 1 traveler (no family discount) ---")
        success, response = self.test(
            "POST /api/pricing/quote (1 traveler)",
            "POST",
            "pricing/quote",
            200,
            data={
                "visa_type_ids": [visa_id],
                "addons": {"express": False, "insurance": False},
                "store_items": []
            }
        )
        
        if success:
            family_discount = response.get('family_discount')
            if family_discount == 0:
                print(f"✅ family_discount = 0 (1 traveler)")
            else:
                print(f"❌ family_discount = {family_discount}, expected 0")
        
        # Test 2: 3 travelers -> family_discount_rate=0.1
        print("\n--- Test 2: 3 travelers (10% family discount) ---")
        success, response = self.test(
            "POST /api/pricing/quote (3 travelers)",
            "POST",
            "pricing/quote",
            200,
            data={
                "visa_type_ids": [visa_id, visa_id, visa_id],
                "addons": {"express": False, "insurance": False},
                "store_items": []
            }
        )
        
        if success:
            family_discount_rate = response.get('family_discount_rate')
            family_discount = response.get('family_discount')
            subtotal = response.get('subtotal')
            
            if family_discount_rate == 0.1:
                print(f"✅ family_discount_rate = 0.1 (10%)")
            else:
                print(f"❌ family_discount_rate = {family_discount_rate}, expected 0.1")
            
            expected_discount = round(subtotal * 0.1, 2)
            if family_discount == expected_discount:
                print(f"✅ family_discount = {family_discount} (subtotal * 0.1)")
            else:
                print(f"❌ family_discount = {family_discount}, expected {expected_discount}")
        
        # Test 3: Express addon per_person=true -> quantity=traveler_count
        print("\n--- Test 3: Express addon (per_person=true) ---")
        success, response = self.test(
            "POST /api/pricing/quote (2 travelers + express)",
            "POST",
            "pricing/quote",
            200,
            data={
                "visa_type_ids": [visa_id, visa_id],
                "addons": {"express": True, "insurance": False},
                "store_items": []
            }
        )
        
        if success:
            addons = response.get('addons', [])
            express_addon = next((a for a in addons if a.get('id') == 'express'), None)
            
            if express_addon:
                quantity = express_addon.get('quantity')
                if quantity == 2:
                    print(f"✅ Express addon quantity = 2 (per_person=true)")
                else:
                    print(f"❌ Express addon quantity = {quantity}, expected 2")
            else:
                print(f"❌ Express addon not found in response")
        
        # Test 4: addons_total type should be FLOAT (0.0 even if no addons)
        print("\n--- Test 4: addons_total type (FLOAT) ---")
        success, response = self.test(
            "POST /api/pricing/quote (no addons)",
            "POST",
            "pricing/quote",
            200,
            data={
                "visa_type_ids": [visa_id],
                "addons": {"express": False, "insurance": False},
                "store_items": []
            }
        )
        
        if success:
            addons_total = response.get('addons_total')
            if isinstance(addons_total, float) and addons_total == 0.0:
                print(f"✅ addons_total = 0.0 (float type)")
            else:
                print(f"❌ addons_total = {addons_total} (type: {type(addons_total).__name__}), expected 0.0 (float)")
        
        # Test 5: Insurance + eSIM -> bundle_discount
        print("\n--- Test 5: Bundle discount (insurance + eSIM) ---")
        
        # First get store products
        success, products_response = self.test(
            "GET /api/products",
            "GET",
            "products",
            200
        )
        
        if success:
            # Handle both list and dict responses
            if isinstance(products_response, dict):
                products = products_response.get('items', [])
            elif isinstance(products_response, list):
                products = products_response
            else:
                products = []
            
            if not products:
                print(f"⚠️  No products found, skipping bundle test")
                return
            
            insurance = next((p for p in products if isinstance(p, dict) and p.get('kind') == 'insurance'), None)
            esim = next((p for p in products if isinstance(p, dict) and p.get('kind') == 'esim'), None)
            
            if insurance and esim:
                store_items = [
                    {
                        "product_id": insurance['id'],
                        "quantity": 1
                    },
                    {
                        "product_id": esim['id'],
                        "quantity": 1
                    }
                ]
                
                success, response = self.test(
                    "POST /api/pricing/quote (insurance + eSIM)",
                    "POST",
                    "pricing/quote",
                    200,
                    data={
                        "visa_type_ids": [visa_id],
                        "addons": {"express": False, "insurance": False},
                        "store_items": store_items
                    }
                )
                
                if success:
                    bundle_discount = response.get('bundle_discount')
                    store_total = response.get('store_total')
                    
                    if bundle_discount > 0:
                        print(f"✅ bundle_discount applied: {bundle_discount}")
                        expected_bundle = round(store_total * 0.1, 2)
                        if bundle_discount == expected_bundle:
                            print(f"✅ bundle_discount = {bundle_discount} (10% of store_total)")
                        else:
                            print(f"⚠️  bundle_discount = {bundle_discount}, expected {expected_bundle}")
                    else:
                        print(f"❌ bundle_discount = {bundle_discount}, expected > 0")
            else:
                print(f"⚠️  Insurance or eSIM product not found, skipping bundle test")

    def test_status_check(self):
        """REGRESSION - Test POST /api/admin/zami/check-status-all"""
        print("\n\n" + "="*70)
        print("🔍 REGRESSION TEST 5: Zami Status Check (Read-Only)")
        print("="*70)
        
        if not self.admin_token:
            print("❌ No admin token")
            return
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        success, response = self.test(
            "POST /api/admin/zami/check-status-all",
            "POST",
            "admin/zami/check-status-all",
            200,
            data={"notify": False},
            headers=headers
        )
        
        if success:
            ok = response.get('ok')
            checked = response.get('checked', 0)
            error = response.get('error')
            
            if ok == True:
                print(f"✅ ok = true")
            else:
                print(f"❌ ok = {ok}, expected true")
            
            if checked >= 0:
                print(f"✅ checked = {checked}")
            else:
                print(f"❌ checked = {checked}")
            
            if error is None:
                print(f"✅ error = None")
            else:
                print(f"⚠️  error = {error}")

    def test_other_endpoints(self):
        """REGRESSION - Test other public/admin endpoints return 200"""
        print("\n\n" + "="*70)
        print("🔍 REGRESSION TEST 6: Other Endpoints")
        print("="*70)
        
        headers = {"Authorization": f"Bearer {self.admin_token}"} if self.admin_token else {}
        
        # Public endpoints
        public_endpoints = [
            ("GET /api/content/site", "GET", "content/site", 200, None),
            ("GET /api/visa-types", "GET", "visa-types", 200, None),
            ("GET /api/visa-guides", "GET", "visa-guides", 200, None),
            ("GET /api/articles", "GET", "articles", 200, None),
            ("GET /api/products", "GET", "products", 200, None),
            ("GET /api/fx", "GET", "fx", 200, None),
        ]
        
        for name, method, endpoint, expected, data in public_endpoints:
            self.test(name, method, endpoint, expected, data=data)
        
        # Admin endpoints
        if self.admin_token:
            admin_endpoints = [
                ("GET /api/admin/applications", "GET", "admin/applications", 200, None),
                ("GET /api/admin/orders", "GET", "admin/orders", 200, None),
                ("GET /api/admin/emails", "GET", "admin/emails", 200, None),
                ("GET /api/admin/whatsapp/settings", "GET", "admin/whatsapp/settings", 200, None),
                ("GET /api/admin/zami/readiness", "GET", "admin/zami/readiness", 200, None),
                ("GET /api/admin/zami/candidates", "GET", "admin/zami/candidates", 200, None),
                ("GET /api/admin/contact-messages", "GET", "admin/contact-messages", 200, None),
            ]
            
            for name, method, endpoint, expected, data in admin_endpoints:
                self.test(name, method, endpoint, expected, data=data, headers=headers)

    def test_application_with_new_fields(self):
        """REGRESSION - Test POST /api/applications with new Zami fields"""
        print("\n\n" + "="*70)
        print("🔍 REGRESSION TEST 7: Application with New Zami Fields")
        print("="*70)
        
        # Get visa types
        success, visa_response = self.test(
            "GET /api/visa-types",
            "GET",
            "visa-types",
            200
        )
        
        if not success:
            return
        
        adult_visas = [v for v in visa_response if v.get('category') != 'child']
        if not adult_visas:
            print("❌ No adult visa types found")
            return
        
        visa_id = adult_visas[0]['id']
        
        # Upload files
        import io
        import base64
        jpeg_data = base64.b64decode('/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k=')
        
        try:
            files = {'file': ('passport.jpg', io.BytesIO(jpeg_data), 'image/jpeg')}
            form_data = {'doc_type': 'passport'}
            upload_response = requests.post(f"{API_BASE}/uploads", files=files, data=form_data, timeout=30)
            passport_file_id = upload_response.json().get('file_id')
            
            files = {'file': ('photo.jpg', io.BytesIO(jpeg_data), 'image/jpeg')}
            form_data = {'doc_type': 'photo'}
            upload_response = requests.post(f"{API_BASE}/uploads", files=files, data=form_data, timeout=30)
            photo_file_id = upload_response.json().get('file_id')
        except Exception as e:
            print(f"❌ File upload failed: {str(e)}")
            return
        
        today = datetime.now()
        arrival = (today + timedelta(days=30)).strftime('%Y-%m-%d')
        departure = (today + timedelta(days=37)).strftime('%Y-%m-%d')
        
        # Test with valid marital_status
        app_data = {
            "contact": {
                "full_name": "Test New Fields",
                "email": "test.newfields@example.com",
                "phone": "05551234567",
                "address_city": "Istanbul",
                "whatsapp_optin": False
            },
            "travelers": [{
                "first_name": "TEST",
                "last_name": "USER",
                "birth_date": "1990-01-01",
                "gender": "male",
                "applicant_type": "adult",
                "nationality": "TR",
                "national_id": "12345678901",
                "passport_no": "U12345678",
                "passport_expiry": "2030-12-31",
                "marital_status": "single",
                "profession": "Software Engineer",
                "mother_name": "ANNE ADI",
                "father_name": "BABA ADI",
                "visa_type_id": visa_id,
                "passport_file_id": passport_file_id,
                "photo_file_id": photo_file_id
            }],
            "travel": {
                "arrival_date": arrival,
                "departure_date": departure,
                "purpose": "tourism",
                "birth_country": "TR",
                "accommodation": "Hotel",
                "flight_no": "TK123",
                "notes": ""
            },
            "addons": {"express": False, "insurance": False},
            "store_items": [],
            "extra_documents": {
                "ticket_file_id": None,
                "hotel_file_id": None,
                "other_file_ids": []
            },
            "kvkk_accepted": True
        }
        
        success, response = self.test(
            "POST /api/applications (with new Zami fields)",
            "POST",
            "applications",
            200,
            data=app_data
        )
        
        if success:
            print(f"✅ Application created with new fields")
        
        # Test with invalid marital_status (should return 422)
        app_data['travelers'][0]['marital_status'] = 'invalid_status'
        
        success, response = self.test(
            "POST /api/applications (invalid marital_status)",
            "POST",
            "applications",
            422,
            data=app_data
        )
        
        if success:
            print(f"✅ Invalid marital_status rejected with 422")

    def run_all_tests(self):
        """Run all Zami refactoring tests"""
        print("\n" + "="*70)
        print("VizeAtlas Dubai - Zami Refactoring Test Suite")
        print("Testing refactored zami.py (save_mapping + build_payload)")
        print(f"Base URL: {BASE_URL}")
        print("="*70)
        
        # Admin login
        if not self.admin_login():
            print("\n❌ Cannot proceed without admin access")
            return 1
        
        # Run tests
        self.test_mapping_persistence()
        self.test_mapping_normalization()
        self.restore_original_mapping()
        
        # Create test application
        app_id = self.create_test_application()
        
        if app_id:
            self.test_payload_structure(app_id)
        
        self.test_pricing_regression()
        self.test_status_check()
        self.test_other_endpoints()
        self.test_application_with_new_fields()
        
        # Print summary
        print("\n\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print("="*70)
        
        return 0 if self.tests_failed == 0 else 1

def main():
    tester = ZamiRefactorTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
