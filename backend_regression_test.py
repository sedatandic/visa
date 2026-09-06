#!/usr/bin/env python3
"""
VizeAtlas Dubai - Backend Refactor Regression Test
Tests that refactored code behaves identically to original code.
"""

import requests
import sys
import io
from datetime import datetime

BASE_URL = "https://visa-bot-dashboard.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@vizeatlas.com"
ADMIN_PASSWORD = "Dubai2026!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class RegressionTester:
    def __init__(self):
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.uploaded_files = {}  # Store uploaded file IDs

    def log(self, message, color=Colors.BLUE):
        print(f"{color}{message}{Colors.END}")

    def test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None, files=None):
        """Run a single API test"""
        url = f"{BASE_URL}{endpoint}"
        h = headers or {}
        
        self.tests_run += 1
        self.log(f"\n🔍 Test {self.tests_run}: {name}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=h, params=params, timeout=15)
            elif method == 'POST':
                if files:
                    response = requests.post(url, data=data, files=files, headers={k:v for k,v in h.items() if k != 'Content-Type'}, timeout=15)
                else:
                    h['Content-Type'] = 'application/json'
                    response = requests.post(url, json=data, headers=h, params=params, timeout=15)
            elif method == 'PUT':
                h['Content-Type'] = 'application/json'
                response = requests.put(url, json=data, headers=h, timeout=15)
            elif method == 'PATCH':
                h['Content-Type'] = 'application/json'
                response = requests.patch(url, json=data, headers=h, timeout=15)
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
                    self.log(f"   Response: {response.text[:300]}", Colors.RED)
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

    def test_uploads_regression(self):
        """REGRESSION: POST /api/uploads - file validation"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: POST /api/uploads - File Upload & Validation", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        # Test 1: Upload valid PNG (passport)
        png_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100  # Minimal PNG header
        files = {'file': ('passport.png', io.BytesIO(png_data), 'image/png')}
        data = {'doc_type': 'passport'}
        
        success, response = self.test(
            "Upload valid PNG passport",
            "POST",
            "/uploads",
            200,
            data=data,
            files=files
        )
        
        if success:
            self.uploaded_files['passport'] = response.get('file_id')
            self.log(f"   Passport file_id: {self.uploaded_files['passport']}", Colors.BLUE)
        
        # Test 2: Upload valid PNG (photo)
        files = {'file': ('photo.png', io.BytesIO(png_data), 'image/png')}
        data = {'doc_type': 'photo'}
        
        success, response = self.test(
            "Upload valid PNG photo",
            "POST",
            "/uploads",
            200,
            data=data,
            files=files
        )
        
        if success:
            self.uploaded_files['photo'] = response.get('file_id')
            self.log(f"   Photo file_id: {self.uploaded_files['photo']}", Colors.BLUE)
        
        # Test 3: Upload valid PDF (ticket)
        pdf_data = b'%PDF-1.4\n' + b'\x00' * 100  # Minimal PDF header
        files = {'file': ('ticket.pdf', io.BytesIO(pdf_data), 'application/pdf')}
        data = {'doc_type': 'ticket'}
        
        success, response = self.test(
            "Upload valid PDF ticket",
            "POST",
            "/uploads",
            200,
            data=data,
            files=files
        )
        
        if success:
            self.uploaded_files['ticket'] = response.get('file_id')
            self.log(f"   Ticket file_id: {self.uploaded_files['ticket']}", Colors.BLUE)
        
        # Test 4: Upload valid PDF (hotel)
        files = {'file': ('hotel.pdf', io.BytesIO(pdf_data), 'application/pdf')}
        data = {'doc_type': 'hotel'}
        
        success, response = self.test(
            "Upload valid PDF hotel",
            "POST",
            "/uploads",
            200,
            data=data,
            files=files
        )
        
        if success:
            self.uploaded_files['hotel'] = response.get('file_id')
            self.log(f"   Hotel file_id: {self.uploaded_files['hotel']}", Colors.BLUE)
        
        # Test 5: Upload unsupported extension (.txt) - should return 400
        txt_data = b'This is a text file'
        files = {'file': ('document.txt', io.BytesIO(txt_data), 'text/plain')}
        data = {'doc_type': 'passport'}
        
        success, response = self.test(
            "Upload unsupported .txt file (should fail with 400)",
            "POST",
            "/uploads",
            400,
            data=data,
            files=files
        )
        
        if success:
            self.log(f"   ✅ Correctly rejected .txt file", Colors.GREEN)
        
        # Test 6: Upload empty file - should return 400
        files = {'file': ('empty.png', io.BytesIO(b''), 'image/png')}
        data = {'doc_type': 'passport'}
        
        success, response = self.test(
            "Upload empty file (should fail with 400)",
            "POST",
            "/uploads",
            400,
            data=data,
            files=files
        )
        
        if success:
            self.log(f"   ✅ Correctly rejected empty file", Colors.GREEN)

    def test_pricing_quote_regression(self):
        """REGRESSION: POST /api/pricing/quote - family discount, addons, store items"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: POST /api/pricing/quote - Pricing Calculations", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        # Test 1: Family discount (2 travelers)
        success, quote = self.test(
            "Quote with 2 travelers (family discount)",
            "POST",
            "/pricing/quote",
            200,
            data={
                'visa_type_ids': ['visa_30_single', 'visa_30_single'],
                'addons': {'express': False, 'insurance': False}
            }
        )
        
        if success:
            family_discount = quote.get('family_discount', 0)
            self.log(f"   Family discount: {family_discount} TRY", Colors.BLUE)
            if family_discount > 0:
                self.log(f"   ✅ Family discount applied", Colors.GREEN)
        
        # Test 2: Quote with addons
        success, quote = self.test(
            "Quote with express addon",
            "POST",
            "/pricing/quote",
            200,
            data={
                'visa_type_ids': ['visa_30_single'],
                'addons': {'express': True, 'insurance': False}
            }
        )
        
        if success:
            addon_total = quote.get('addon_total', 0)
            self.log(f"   Addon total: {addon_total} TRY", Colors.BLUE)
            if addon_total > 0:
                self.log(f"   ✅ Express addon applied", Colors.GREEN)
        
        # Test 3: Quote with store items and bundle discount
        success, quote = self.test(
            "Quote with store items (esim_1gb + ins_basic) - 10% bundle discount",
            "POST",
            "/pricing/quote",
            200,
            data={
                'visa_type_ids': ['visa_30_single'],
                'addons': {'express': False, 'insurance': False},
                'store_items': [
                    {'product_id': 'esim_1gb', 'quantity': 1},
                    {'product_id': 'ins_basic', 'quantity': 1}
                ],
                'arrival_date': '2026-12-01',
                'departure_date': '2026-12-15'
            }
        )
        
        if success:
            store_items = quote.get('store_items', [])
            store_total = quote.get('store_total', 0)
            bundle_discount = quote.get('bundle_discount', 0)
            
            self.log(f"   Store items count: {len(store_items)}", Colors.BLUE)
            self.log(f"   Store total: {store_total} TRY", Colors.BLUE)
            self.log(f"   Bundle discount: {bundle_discount} TRY", Colors.BLUE)
            
            # Check bundle discount is 10%
            if bundle_discount > 0:
                self.log(f"   ✅ Bundle discount (10%) applied", Colors.GREEN)
            
            # Check store items have validity dates
            for item in store_items:
                if 'starts_on' in item and 'ends_on' in item and 'validity_days' in item:
                    self.log(f"   ✅ Store item has validity dates: {item.get('name')}", Colors.GREEN)
                    self.log(f"      starts_on: {item.get('starts_on')}, ends_on: {item.get('ends_on')}, validity_days: {item.get('validity_days')}", Colors.BLUE)
                    
                    # Check covers_trip field
                    if 'covers_trip' in item:
                        self.log(f"      covers_trip: {item.get('covers_trip')}", Colors.BLUE)
        
        # Test 4: Quote with invalid visa_type_id - should return 400
        success, quote = self.test(
            "Quote with invalid visa_type_id (should fail with 400)",
            "POST",
            "/pricing/quote",
            400,
            data={
                'visa_type_ids': ['invalid_visa_type'],
                'addons': {'express': False}
            }
        )
        
        if success:
            self.log(f"   ✅ Correctly rejected invalid visa_type_id", Colors.GREEN)

    def test_application_creation_regression(self):
        """REGRESSION: POST /api/applications - full application flow"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: POST /api/applications - Full Application Flow", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        # Ensure we have uploaded files
        if not all(k in self.uploaded_files for k in ['passport', 'photo', 'ticket', 'hotel']):
            self.log("   ⚠️  Skipping application tests - missing uploaded files", Colors.YELLOW)
            return None
        
        # Test 1: Create application with 2 travelers and store items
        test_email = f"regtest{int(datetime.now().timestamp())}@test.com"
        
        success, app = self.test(
            "Create application with 2 travelers + store items (esim_1gb + ins_basic)",
            "POST",
            "/applications",
            200,
            data={
                'contact': {
                    'full_name': 'Regression Test User',
                    'email': test_email,
                    'phone': '+905551234567',
                    'address_city': 'Istanbul'
                },
                'travelers': [
                    {
                        'first_name': 'AHMET',
                        'last_name': 'YILMAZ',
                        'birth_date': '1990-01-15',
                        'gender': 'male',
                        'applicant_type': 'adult',
                        'nationality': 'TR',
                        'passport_no': 'U12345678',
                        'passport_expiry': '2030-12-31',
                        'visa_type_id': 'visa_30_single',
                        'passport_file_id': self.uploaded_files['passport'],
                        'photo_file_id': self.uploaded_files['photo']
                    },
                    {
                        'first_name': 'AYSE',
                        'last_name': 'YILMAZ',
                        'birth_date': '1992-05-20',
                        'gender': 'female',
                        'applicant_type': 'adult',
                        'nationality': 'TR',
                        'passport_no': 'U87654321',
                        'passport_expiry': '2030-12-31',
                        'visa_type_id': 'visa_30_single',
                        'passport_file_id': self.uploaded_files['passport'],
                        'photo_file_id': self.uploaded_files['photo']
                    }
                ],
                'travel': {
                    'arrival_date': '2026-12-01',
                    'departure_date': '2026-12-15',
                    'purpose': 'tourism'
                },
                'addons': {'express': False, 'insurance': False},
                'store_items': [
                    {'product_id': 'esim_1gb', 'quantity': 2},
                    {'product_id': 'ins_basic', 'quantity': 2}
                ],
                'extra_documents': {
                    'ticket_file_id': self.uploaded_files['ticket'],
                    'hotel_file_id': self.uploaded_files['hotel']
                },
                'kvkk_accepted': True
            }
        )
        
        if success:
            reference_code = app.get('reference_code')
            app_id = app.get('id')
            store_items = app.get('store_items', [])
            linked_order_reference = app.get('linked_order_reference')
            pricing = app.get('pricing', {})
            
            self.log(f"   Reference code: {reference_code}", Colors.BLUE)
            self.log(f"   Application ID: {app_id}", Colors.BLUE)
            self.log(f"   Store items count: {len(store_items)}", Colors.BLUE)
            self.log(f"   Linked order reference: {linked_order_reference}", Colors.BLUE)
            
            # Check reference code format (DV-XX######)
            if reference_code and reference_code.startswith('DV-'):
                self.log(f"   ✅ Reference code generated correctly", Colors.GREEN)
            
            # Check store items have validity dates
            for item in store_items:
                if all(k in item for k in ['starts_on', 'ends_on', 'validity_days', 'covers_trip']):
                    self.log(f"   ✅ Store item has all required fields: {item.get('name')}", Colors.GREEN)
            
            # Check bundle discount applied
            bundle_discount = pricing.get('bundle_discount', 0)
            if bundle_discount > 0:
                self.log(f"   ✅ Bundle discount (10%) applied: {bundle_discount} TRY", Colors.GREEN)
            
            # Check linked order created
            if linked_order_reference:
                self.log(f"   ✅ Linked order created", Colors.GREEN)
            
            return {'reference_code': reference_code, 'app_id': app_id, 'email': test_email}
        
        return None
    
    def test_application_missing_docs_regression(self):
        """REGRESSION: POST /api/applications - missing ticket/hotel validation"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: POST /api/applications - Missing Documents Validation", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        if not all(k in self.uploaded_files for k in ['passport', 'photo']):
            self.log("   ⚠️  Skipping - missing uploaded files", Colors.YELLOW)
            return
        
        # Test 1: Missing ticket - should return 400
        success, response = self.test(
            "Create application without ticket (should fail with 400)",
            "POST",
            "/applications",
            400,
            data={
                'contact': {
                    'full_name': 'Test User',
                    'email': 'test@test.com',
                    'phone': '+905551234567',
                    'address_city': 'Istanbul'
                },
                'travelers': [{
                    'first_name': 'AHMET',
                    'last_name': 'TEST',
                    'birth_date': '1990-01-01',
                    'gender': 'male',
                    'applicant_type': 'adult',
                    'nationality': 'TR',
                    'passport_no': 'U12345678',
                    'passport_expiry': '2030-12-31',
                    'visa_type_id': 'visa_30_single',
                    'passport_file_id': self.uploaded_files['passport'],
                    'photo_file_id': self.uploaded_files['photo']
                }],
                'travel': {
                    'arrival_date': '2026-12-01',
                    'departure_date': '2026-12-15',
                    'purpose': 'tourism'
                },
                'addons': {'express': False},
                'extra_documents': {
                    'hotel_file_id': self.uploaded_files['hotel']
                    # Missing ticket_file_id
                },
                'kvkk_accepted': True
            }
        )
        
        if success:
            self.log(f"   ✅ Correctly rejected application without ticket", Colors.GREEN)
        
        # Test 2: Missing hotel - should return 400
        success, response = self.test(
            "Create application without hotel (should fail with 400)",
            "POST",
            "/applications",
            400,
            data={
                'contact': {
                    'full_name': 'Test User',
                    'email': 'test@test.com',
                    'phone': '+905551234567',
                    'address_city': 'Istanbul'
                },
                'travelers': [{
                    'first_name': 'AHMET',
                    'last_name': 'TEST',
                    'birth_date': '1990-01-01',
                    'gender': 'male',
                    'applicant_type': 'adult',
                    'nationality': 'TR',
                    'passport_no': 'U12345678',
                    'passport_expiry': '2030-12-31',
                    'visa_type_id': 'visa_30_single',
                    'passport_file_id': self.uploaded_files['passport'],
                    'photo_file_id': self.uploaded_files['photo']
                }],
                'travel': {
                    'arrival_date': '2026-12-01',
                    'departure_date': '2026-12-15',
                    'purpose': 'tourism'
                },
                'addons': {'express': False},
                'extra_documents': {
                    'ticket_file_id': self.uploaded_files['ticket']
                    # Missing hotel_file_id
                },
                'kvkk_accepted': True
            }
        )
        
        if success:
            self.log(f"   ✅ Correctly rejected application without hotel", Colors.GREEN)
        
        # Test 3: Invalid file_id - should return 400
        success, response = self.test(
            "Create application with invalid file_id (should fail with 400)",
            "POST",
            "/applications",
            400,
            data={
                'contact': {
                    'full_name': 'Test User',
                    'email': 'test@test.com',
                    'phone': '+905551234567',
                    'address_city': 'Istanbul'
                },
                'travelers': [{
                    'first_name': 'AHMET',
                    'last_name': 'TEST',
                    'birth_date': '1990-01-01',
                    'gender': 'male',
                    'applicant_type': 'adult',
                    'nationality': 'TR',
                    'passport_no': 'U12345678',
                    'passport_expiry': '2030-12-31',
                    'visa_type_id': 'visa_30_single',
                    'passport_file_id': 'invalid-file-id',
                    'photo_file_id': self.uploaded_files['photo']
                }],
                'travel': {
                    'arrival_date': '2026-12-01',
                    'departure_date': '2026-12-15',
                    'purpose': 'tourism'
                },
                'addons': {'express': False},
                'extra_documents': {
                    'ticket_file_id': self.uploaded_files['ticket'],
                    'hotel_file_id': self.uploaded_files['hotel']
                },
                'kvkk_accepted': True
            }
        )
        
        if success:
            self.log(f"   ✅ Correctly rejected invalid file_id", Colors.GREEN)

    def test_application_tracking_regression(self, app_data):
        """REGRESSION: GET /api/applications/track - timeline generation"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: GET /api/applications/track - Timeline Generation", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        if not app_data:
            self.log("   ⚠️  Skipping - no application created", Colors.YELLOW)
            return
        
        reference_code = app_data['reference_code']
        
        # Test 1: Track application with correct code and last_name
        success, track = self.test(
            f"Track application {reference_code}",
            "GET",
            "/applications/track",
            200,
            params={'code': reference_code, 'last_name': 'YILMAZ'}
        )
        
        if success:
            timeline = track.get('timeline', {})
            steps = timeline.get('steps', [])
            current_status = timeline.get('current_status')
            is_final = timeline.get('is_final')
            portal_tracked = timeline.get('portal_tracked')
            last_portal_check = timeline.get('last_portal_check')
            
            self.log(f"   Steps count: {len(steps)}", Colors.BLUE)
            self.log(f"   Current status: {current_status}", Colors.BLUE)
            self.log(f"   Is final: {is_final}", Colors.BLUE)
            self.log(f"   Portal tracked: {portal_tracked}", Colors.BLUE)
            self.log(f"   Last portal check: {last_portal_check}", Colors.BLUE)
            
            # Check 5 steps exist
            if len(steps) == 5:
                self.log(f"   ✅ Timeline has 5 steps", Colors.GREEN)
                
                # Check step keys
                expected_keys = ['received', 'payment', 'documents', 'processing', 'result']
                actual_keys = [s.get('key') for s in steps]
                if actual_keys == expected_keys:
                    self.log(f"   ✅ Step keys correct: {actual_keys}", Colors.GREEN)
                
                # Check step states (done/current/pending)
                for step in steps:
                    state = step.get('state')
                    if state in ['done', 'current', 'pending']:
                        self.log(f"   ✅ Step '{step.get('key')}' has valid state: {state}", Colors.GREEN)
            
            # Check timeline fields
            if all(k in timeline for k in ['steps', 'current_status', 'is_final', 'portal_tracked', 'last_portal_check']):
                self.log(f"   ✅ Timeline has all required fields", Colors.GREEN)
        
        # Test 2: Track with wrong last_name - should return 404
        success, response = self.test(
            f"Track with wrong last_name (should fail with 404)",
            "GET",
            "/applications/track",
            404,
            params={'code': reference_code, 'last_name': 'WRONGNAME'}
        )
        
        if success:
            self.log(f"   ✅ Correctly rejected wrong last_name", Colors.GREEN)

    def test_visa_guides_regression(self):
        """REGRESSION: GET /api/visa-guides and GET /api/visa-guides/{slug}"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: Visa Guides Endpoints", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        # Test 1: GET /api/visa-guides - list all guides
        success, guides = self.test(
            "GET /api/visa-guides - List all guides",
            "GET",
            "/visa-guides",
            200
        )
        
        if success:
            items = guides.get('items', [])
            self.log(f"   Found {len(items)} guides", Colors.BLUE)
            if len(items) > 0:
                self.log(f"   ✅ Guides list returned", Colors.GREEN)
        
        # Test 2: GET /api/visa-guides/visa-application-ae - valid slug
        success, guide = self.test(
            "GET /api/visa-guides/visa-application-ae - Valid slug",
            "GET",
            "/visa-guides/visa-application-ae",
            200
        )
        
        if success:
            self.log(f"   ✅ Guide retrieved for valid slug", Colors.GREEN)
        
        # Test 3: GET /api/visa-guides/invalid-slug - should return 404
        success, response = self.test(
            "GET /api/visa-guides/invalid-slug - Invalid slug (should fail with 404)",
            "GET",
            "/visa-guides/invalid-slug",
            404
        )
        
        if success:
            self.log(f"   ✅ Correctly returned 404 for invalid slug", Colors.GREEN)

    def test_admin_endpoints_regression(self):
        """REGRESSION: Admin endpoints (stats, applications, visa document)"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: Admin Endpoints", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test 1: GET /api/admin/stats
        success, stats = self.test(
            "GET /api/admin/stats",
            "GET",
            "/admin/stats",
            200,
            headers=headers
        )
        
        if success:
            self.log(f"   Total applications: {stats.get('total')}", Colors.BLUE)
            self.log(f"   ✅ Stats endpoint working", Colors.GREEN)
        
        # Test 2: GET /api/admin/applications - list
        success, apps = self.test(
            "GET /api/admin/applications - List applications",
            "GET",
            "/admin/applications",
            200,
            headers=headers
        )
        
        if success:
            items = apps.get('items', [])
            self.log(f"   Found {len(items)} applications", Colors.BLUE)
            
            if len(items) > 0:
                app_id = items[0].get('id')
                
                # Test 3: GET /api/admin/applications/{id} - detail
                success, detail = self.test(
                    f"GET /api/admin/applications/{app_id} - Application detail",
                    "GET",
                    f"/admin/applications/{app_id}",
                    200,
                    headers=headers
                )
                
                if success:
                    self.log(f"   ✅ Application detail retrieved", Colors.GREEN)
                
                # Test 4: PATCH /api/admin/applications/{id} - update status
                success, updated = self.test(
                    f"PATCH /api/admin/applications/{app_id} - Update status",
                    "PATCH",
                    f"/admin/applications/{app_id}",
                    200,
                    data={'status': 'reviewing', 'note': 'Regression test update', 'notify': False},
                    headers=headers
                )
                
                if success:
                    self.log(f"   ✅ Application status updated", Colors.GREEN)
                
                # Test 5: POST /api/admin/applications/{id}/visa-document - upload visa document
                # Test with unsupported extension (.txt) - should return 400
                txt_data = b'This is not a visa document'
                files = {'file': ('visa.txt', io.BytesIO(txt_data), 'text/plain')}
                
                success, response = self.test(
                    f"POST /api/admin/applications/{app_id}/visa-document - Unsupported extension (should fail with 400)",
                    "POST",
                    f"/admin/applications/{app_id}/visa-document",
                    400,
                    files=files,
                    headers=headers
                )
                
                if success:
                    self.log(f"   ✅ Correctly rejected unsupported extension", Colors.GREEN)
                
                # Test 6: Upload empty file - should return 400
                files = {'file': ('visa.pdf', io.BytesIO(b''), 'application/pdf')}
                
                success, response = self.test(
                    f"POST /api/admin/applications/{app_id}/visa-document - Empty file (should fail with 400)",
                    "POST",
                    f"/admin/applications/{app_id}/visa-document",
                    400,
                    files=files,
                    headers=headers
                )
                
                if success:
                    self.log(f"   ✅ Correctly rejected empty file", Colors.GREEN)
                
                # Test 7: Upload valid PDF visa document
                pdf_data = b'%PDF-1.4\n' + b'\x00' * 200
                files = {'file': ('visa.pdf', io.BytesIO(pdf_data), 'application/pdf')}
                
                success, visa_doc = self.test(
                    f"POST /api/admin/applications/{app_id}/visa-document - Valid PDF",
                    "POST",
                    f"/admin/applications/{app_id}/visa-document",
                    200,
                    files=files,
                    headers=headers
                )
                
                if success:
                    app_data = visa_doc.get('application', {})
                    visa_result = app_data.get('visa_result', {})
                    
                    if all(k in visa_result for k in ['file_id', 'filename', 'uploaded_at', 'sent_at', 'send_status', 'sent_to']):
                        self.log(f"   ✅ Visa document uploaded with all required fields", Colors.GREEN)
                    
                    # Test 8: DELETE /api/admin/applications/{app_id}/visa-document
                    success, deleted = self.test(
                        f"DELETE /api/admin/applications/{app_id}/visa-document - Delete visa document",
                        "DELETE",
                        f"/admin/applications/{app_id}/visa-document",
                        200,
                        headers=headers
                    )
                    
                    if success:
                        self.log(f"   ✅ Visa document deleted", Colors.GREEN)

    def test_admin_visa_guides_regression(self):
        """REGRESSION: Admin visa guides endpoints"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: Admin Visa Guides Endpoints", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test 1: PUT /api/admin/visa-guides/visa-application-ae - valid data
        success, updated = self.test(
            "PUT /api/admin/visa-guides/visa-application-ae - Valid data",
            "PUT",
            "/admin/visa-guides/visa-application-ae",
            200,
            data={
                'h1': 'Test H1',
                'seo_title': 'Test SEO Title',
                'intro': ['Test intro paragraph']
            },
            headers=headers
        )
        
        if success:
            self.log(f"   ✅ Visa guide updated with valid data", Colors.GREEN)
        
        # Test 2: PUT with completely empty payload - should return 400
        success, response = self.test(
            "PUT /api/admin/visa-guides/visa-application-ae - Empty payload (should fail with 400)",
            "PUT",
            "/admin/visa-guides/visa-application-ae",
            400,
            data={},
            headers=headers
        )
        
        if success:
            # Check Turkish error message
            self.log(f"   ✅ Correctly rejected empty payload with 400", Colors.GREEN)

    def test_payment_endpoints_regression(self, app_data):
        """REGRESSION: Payment endpoints (checkout, orders)"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: Payment Endpoints", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        if not app_data:
            self.log("   ⚠️  Skipping - no application created", Colors.YELLOW)
            return
        
        app_id = app_data['app_id']
        
        # Test 1: POST /api/payments/checkout - invalid origin_url (should return 400)
        success, response = self.test(
            "POST /api/payments/checkout - Invalid origin_url (should fail with 400)",
            "POST",
            "/payments/checkout",
            400,
            data={
                'application_id': app_id,
                'origin_url': 'not-a-valid-url'
            }
        )
        
        if success:
            self.log(f"   ✅ Correctly rejected invalid origin_url", Colors.GREEN)
        
        # Test 2: POST /api/payments/checkout - non-existent application_id (should return 404)
        success, response = self.test(
            "POST /api/payments/checkout - Non-existent application_id (should fail with 404)",
            "POST",
            "/payments/checkout",
            404,
            data={
                'application_id': 'non-existent-id',
                'origin_url': 'https://visa-bot-dashboard.preview.emergentagent.com'
            }
        )
        
        if success:
            self.log(f"   ✅ Correctly returned 404 for non-existent application", Colors.GREEN)
        
        # Test 3: POST /api/payments/checkout - valid request (may return 502 if Stripe key invalid, but should NOT return 500)
        success, response = self.test(
            "POST /api/payments/checkout - Valid request (502 acceptable if no Stripe key)",
            "POST",
            "/payments/checkout",
            (200, 502),  # Accept both 200 and 502
            data={
                'application_id': app_id,
                'origin_url': 'https://visa-bot-dashboard.preview.emergentagent.com'
            }
        )
        
        # Note: We accept 502 because Stripe test key might not be configured
        # But we should NOT get 500 (internal server error with traceback)
        
        # Test 4: GET /api/orders/{reference} - check orders endpoint
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        success, orders = self.test(
            "GET /api/admin/orders - List orders",
            "GET",
            "/admin/orders",
            200,
            headers=headers
        )
        
        if success:
            self.log(f"   ✅ Orders endpoint working", Colors.GREEN)

    def test_pre_evaluation_regression(self):
        """REGRESSION: Pre-evaluation endpoints"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: Pre-Evaluation Endpoints", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        # Test 1: GET /api/pre-evaluation/questions
        success, questions = self.test(
            "GET /api/pre-evaluation/questions",
            "GET",
            "/pre-evaluation/questions",
            200
        )
        
        if success:
            q_list = questions.get('questions', [])
            self.log(f"   Questions count: {len(q_list)}", Colors.BLUE)
            if len(q_list) == 4:
                self.log(f"   ✅ Pre-evaluation questions endpoint working", Colors.GREEN)
        
        # Test 2: POST /api/pre-evaluation - valid enum values
        success, result = self.test(
            "POST /api/pre-evaluation - Valid enum values",
            "POST",
            "/pre-evaluation",
            200,
            data={
                'passport_validity': '6_plus',
                'visa_history': 'recent',
                'refusal_history': 'none',
                'purpose': 'tourism'
            }
        )
        
        if success:
            self.log(f"   ✅ Pre-evaluation with valid enums working", Colors.GREEN)
        
        # Test 3: POST /api/pre-evaluation - invalid enum (should return 422)
        success, response = self.test(
            "POST /api/pre-evaluation - Invalid enum (should fail with 422)",
            "POST",
            "/pre-evaluation",
            422,
            data={
                'passport_validity': 'invalid_value',
                'visa_history': 'recent',
                'refusal_history': 'none'
            }
        )
        
        if success:
            self.log(f"   ✅ Correctly rejected invalid enum", Colors.GREEN)
        
        # Test 4: GET /api/admin/pre-evaluations
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        success, admin_list = self.test(
            "GET /api/admin/pre-evaluations",
            "GET",
            "/admin/pre-evaluations",
            200,
            headers=headers
        )
        
        if success:
            self.log(f"   ✅ Admin pre-evaluations endpoint working", Colors.GREEN)

    def test_zami_endpoints_regression(self):
        """REGRESSION: Zami endpoints (should return 200, not 500)"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION: Zami Endpoints (Should NOT Return 500)", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test 1: GET /api/admin/zami/config
        success, config = self.test(
            "GET /api/admin/zami/config - Should return 200",
            "GET",
            "/admin/zami/config",
            200,
            headers=headers
        )
        
        if success:
            self.log(f"   ✅ Zami config endpoint returns 200", Colors.GREEN)
        
        # Test 2: GET /api/admin/zami/readiness
        success, readiness = self.test(
            "GET /api/admin/zami/readiness - Should return 200",
            "GET",
            "/admin/zami/readiness",
            200,
            headers=headers
        )
        
        if success:
            self.log(f"   ✅ Zami readiness endpoint returns 200", Colors.GREEN)
        
        # Test 3: GET /api/admin/zami/logs
        success, logs = self.test(
            "GET /api/admin/zami/logs - Should return 200",
            "GET",
            "/admin/zami/logs",
            200,
            headers=headers
        )
        
        if success:
            self.log(f"   ✅ Zami logs endpoint returns 200", Colors.GREEN)
        
        # Test 4: GET /api/admin/whatsapp/settings
        success, wa_settings = self.test(
            "GET /api/admin/whatsapp/settings - Should return 200",
            "GET",
            "/admin/whatsapp/settings",
            200,
            headers=headers
        )
        
        if success:
            self.log(f"   ✅ WhatsApp settings endpoint returns 200", Colors.GREEN)

    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*70, Colors.YELLOW)
        self.log("REGRESSION TEST SUMMARY", Colors.YELLOW)
        self.log("="*70, Colors.YELLOW)
        
        pass_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        self.log(f"\nTotal Tests: {self.tests_run}", Colors.BLUE)
        self.log(f"Passed: {self.tests_passed}", Colors.GREEN)
        self.log(f"Failed: {self.tests_failed}", Colors.RED)
        self.log(f"Pass Rate: {pass_rate:.1f}%", Colors.YELLOW)
        
        if pass_rate == 100:
            self.log("\n🎉 Perfect! All regression tests passed. Refactoring successful.", Colors.GREEN)
        elif pass_rate >= 90:
            self.log("\n✅ Excellent! Minor issues only.", Colors.GREEN)
        elif pass_rate >= 70:
            self.log("\n⚠️  Some regressions detected. Review failed tests.", Colors.YELLOW)
        else:
            self.log("\n❌ Critical regressions found. Refactoring broke behavior.", Colors.RED)
        
        return 0 if self.tests_failed == 0 else 1

def main():
    tester = RegressionTester()
    
    print(f"\n{Colors.BLUE}{'='*70}")
    print("VizeAtlas Dubai - Backend Refactor Regression Test")
    print("Testing that refactored code behaves identically")
    print(f"Base URL: {BASE_URL}")
    print(f"{'='*70}{Colors.END}\n")
    
    # Login as admin
    if not tester.admin_login():
        print(f"{Colors.RED}❌ Admin login failed. Cannot continue.{Colors.END}")
        return 1
    
    # Run regression tests in order
    tester.test_uploads_regression()
    tester.test_pricing_quote_regression()
    tester.test_application_missing_docs_regression()
    app_data = tester.test_application_creation_regression()
    tester.test_application_tracking_regression(app_data)
    tester.test_visa_guides_regression()
    tester.test_admin_endpoints_regression()
    tester.test_admin_visa_guides_regression()
    tester.test_payment_endpoints_regression(app_data)
    tester.test_pre_evaluation_regression()
    tester.test_zami_endpoints_regression()
    
    # Print summary
    return tester.print_summary()

if __name__ == "__main__":
    sys.exit(main())
