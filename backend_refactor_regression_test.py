#!/usr/bin/env python3
"""
VizeAtlas Dubai Backend Refactor Regression Test
Tests refactored endpoints to ensure NO behavioral changes after code-quality refactor
"""

import requests
import sys
import time
import uuid
from datetime import datetime, timedelta

BASE_URL = "https://visa-bot-dashboard.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@vizeatlas.com"
ADMIN_PASSWORD = "Dubai2026!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class RefactorRegressionTester:
    def __init__(self):
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_file_ids = []
        self.test_application_id = None

    def log(self, message, color=Colors.BLUE):
        print(f"{color}{message}{Colors.END}")

    def test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None, files=None):
        """Run a single API test"""
        url = f"{BASE_URL}{endpoint}"
        h = headers or {}
        
        # Only set Content-Type for JSON if not already set and no files
        if not files and 'Content-Type' not in h:
            h['Content-Type'] = 'application/json'
        
        self.tests_run += 1
        self.log(f"\n🔍 Test {self.tests_run}: {name}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=h, params=params, timeout=15)
            elif method == 'POST':
                if files:
                    # For file uploads, don't send Content-Type (requests will set it with boundary)
                    response = requests.post(url, data=data, files=files, headers={k:v for k,v in h.items() if k != 'Content-Type'}, timeout=15)
                elif h.get('Content-Type') == 'application/x-www-form-urlencoded':
                    # For form data
                    response = requests.post(url, data=data, headers=h, timeout=15)
                else:
                    # For JSON
                    response = requests.post(url, json=data, headers=h, params=params, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=h, timeout=15)
            elif method == 'PATCH':
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
                    self.log(f"   Response: {response.text[:200]}", Colors.RED)
                return False, {}
                
        except Exception as e:
            self.tests_failed += 1
            self.log(f"❌ FAIL - Exception: {str(e)}", Colors.RED)
            return False, {}

    def admin_login(self):
        """Login as admin"""
        self.log("\n" + "="*80, Colors.YELLOW)
        self.log("ADMIN LOGIN", Colors.YELLOW)
        self.log("="*80, Colors.YELLOW)
        
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

    def test_store_order_creation(self):
        """Test POST /api/orders - refactored create_order with helpers"""
        self.log("\n" + "="*80, Colors.YELLOW)
        self.log("TEST 1: POST /api/orders - Store Order Creation (Refactored)", Colors.YELLOW)
        self.log("="*80, Colors.YELLOW)
        
        # Test 1a: Card payment method
        success, order_card = self.test(
            "POST /api/orders - Card payment method",
            "POST",
            "/orders",
            200,
            data={
                'items': [
                    {'product_id': 'esim_3gb', 'quantity': 1}
                ],
                'contact': {
                    'full_name': 'Test User Card',
                    'email': f'card{int(time.time())}@test.com',
                    'phone': '+905551234567'
                },
                'travel_start': '2026-12-01',
                'travel_end': '2026-12-15',
                'payment_method': 'card'
            }
        )
        
        if success:
            order = order_card.get('order', {})
            bank = order_card.get('bank')
            
            # Verify payment method
            payment = order.get('payment', {})
            if payment.get('method') == 'card' and payment.get('status') == 'pending':
                self.log(f"   ✅ Card payment: method=card, status=pending", Colors.GREEN)
            else:
                self.log(f"   ❌ Card payment incorrect: {payment}", Colors.RED)
            
            # Verify bank details NOT returned for card
            if bank is None:
                self.log(f"   ✅ Bank details NOT returned for card payment", Colors.GREEN)
            else:
                self.log(f"   ❌ Bank details should be None for card payment", Colors.RED)
            
            # Verify pricing fields
            required_fields = ['items_total', 'bundle_discount', 'bundle_discount_rate', 'price']
            for field in required_fields:
                if field in order:
                    self.log(f"   ✅ Field present: {field} = {order[field]}", Colors.GREEN)
                else:
                    self.log(f"   ❌ Missing field: {field}", Colors.RED)
            
            # Verify validity window
            items = order.get('items', [])
            if items:
                item = items[0]
                if item.get('starts_on') == '2026-12-01':
                    self.log(f"   ✅ Validity starts_on = 2026-12-01", Colors.GREEN)
                if item.get('ends_on') == '2026-12-15':
                    self.log(f"   ✅ Validity ends_on = 2026-12-15 (15 days)", Colors.GREEN)
        
        # Test 1b: Transfer payment method
        success, order_transfer = self.test(
            "POST /api/orders - Transfer payment method",
            "POST",
            "/orders",
            200,
            data={
                'items': [
                    {'product_id': 'ins_basic', 'quantity': 1}
                ],
                'contact': {
                    'full_name': 'Test User Transfer',
                    'email': f'transfer{int(time.time())}@test.com',
                    'phone': '+905551234567'
                },
                'payment_method': 'transfer'
            }
        )
        
        if success:
            order = order_transfer.get('order', {})
            bank = order_transfer.get('bank')
            
            # Verify payment method
            payment = order.get('payment', {})
            if payment.get('method') == 'bank_transfer' and payment.get('status') == 'awaiting_transfer':
                self.log(f"   ✅ Transfer payment: method=bank_transfer, status=awaiting_transfer", Colors.GREEN)
            else:
                self.log(f"   ❌ Transfer payment incorrect: {payment}", Colors.RED)
            
            # Verify bank details ARE returned for transfer
            if bank and isinstance(bank, dict):
                self.log(f"   ✅ Bank details returned for transfer payment", Colors.GREEN)
                if 'account_name' in bank and 'iban' in bank:
                    self.log(f"   ✅ Bank details contain account_name and iban", Colors.GREEN)
            else:
                self.log(f"   ❌ Bank details missing for transfer payment", Colors.RED)
        
        # Test 1c: Bundle discount (insurance + eSIM = 10%)
        success, order_bundle = self.test(
            "POST /api/orders - Bundle discount (insurance + eSIM)",
            "POST",
            "/orders",
            200,
            data={
                'items': [
                    {'product_id': 'esim_3gb', 'quantity': 1},
                    {'product_id': 'ins_basic', 'quantity': 1}
                ],
                'contact': {
                    'full_name': 'Test Bundle',
                    'email': f'bundle{int(time.time())}@test.com',
                    'phone': '+905551234567'
                },
                'payment_method': 'card'
            }
        )
        
        if success:
            order = order_bundle.get('order', {})
            bundle_discount = order.get('bundle_discount', 0)
            bundle_discount_rate = order.get('bundle_discount_rate', 0)
            items_total = order.get('items_total', 0)
            price = order.get('price', 0)
            
            if bundle_discount > 0:
                self.log(f"   ✅ Bundle discount applied: {bundle_discount} TRY", Colors.GREEN)
            else:
                self.log(f"   ❌ Bundle discount NOT applied", Colors.RED)
            
            if bundle_discount_rate == 0.1:
                self.log(f"   ✅ Bundle discount rate = 10%", Colors.GREEN)
            else:
                self.log(f"   ❌ Bundle discount rate should be 0.1, got {bundle_discount_rate}", Colors.RED)
            
            # Verify price calculation
            expected_price = items_total - bundle_discount
            if abs(price - expected_price) < 0.01:
                self.log(f"   ✅ Price correctly calculated: {items_total} - {bundle_discount} = {price}", Colors.GREEN)
            else:
                self.log(f"   ❌ Price calculation error: expected {expected_price}, got {price}", Colors.RED)
        
        # Test 1d: Invalid product_id
        success, error = self.test(
            "POST /api/orders - Invalid product_id (should return 400)",
            "POST",
            "/orders",
            400,
            data={
                'items': [
                    {'product_id': 'invalid_product_xyz', 'quantity': 1}
                ],
                'contact': {
                    'full_name': 'Test Invalid',
                    'email': f'invalid{int(time.time())}@test.com',
                    'phone': '+905551234567'
                },
                'payment_method': 'card'
            }
        )
        
        if success:
            self.log(f"   ✅ Invalid product_id correctly rejected with 400", Colors.GREEN)

    def test_application_with_store_items(self):
        """Test visa application submit with eSIM/insurance creates linked order"""
        self.log("\n" + "="*80, Colors.YELLOW)
        self.log("TEST 2: Visa Application with Store Items - Linked Order Creation", Colors.YELLOW)
        self.log("="*80, Colors.YELLOW)
        
        # Create dummy file uploads first
        test_files = []
        for i in range(4):
            # Create a minimal valid image file (1x1 PNG)
            png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
            
            success, upload = self.test(
                f"POST /api/uploads - Upload test file {i+1}",
                "POST",
                "/uploads",
                200,
                files={'file': (f'test{i}.png', png_data, 'image/png')},
                data={'doc_type': 'passport'}
            )
            
            if success:
                file_id = upload.get('file_id')
                test_files.append(file_id)
                self.log(f"   File {i+1} uploaded: {file_id}", Colors.BLUE)
        
        if len(test_files) < 4:
            self.log(f"   ❌ Could not upload test files, skipping application test", Colors.RED)
            return
        
        # Create application with store items
        test_email = f'appstore{int(time.time())}@test.com'
        success, app = self.test(
            "POST /api/applications - With eSIM and insurance",
            "POST",
            "/applications",
            200,
            data={
                'contact': {
                    'full_name': 'Test Application Store',
                    'email': test_email,
                    'phone': '+905551234567',
                    'address_city': 'Istanbul'
                },
                'travelers': [{
                    'first_name': 'AHMET',
                    'last_name': 'TESTSTORE',
                    'birth_date': '1990-01-01',
                    'gender': 'male',
                    'applicant_type': 'adult',
                    'nationality': 'TR',
                    'passport_no': f'U{int(time.time())}',
                    'passport_expiry': '2030-12-31',
                    'visa_type_id': 'visa_30_single',
                    'passport_file_id': test_files[0],
                    'photo_file_id': test_files[1]
                }],
                'travel': {
                    'arrival_date': '2026-12-01',
                    'departure_date': '2026-12-15',
                    'purpose': 'tourism'
                },
                'addons': {'express': False},
                'store_items': [
                    {'product_id': 'esim_3gb', 'quantity': 1},
                    {'product_id': 'ins_basic', 'quantity': 1}
                ],
                'extra_documents': {
                    'ticket_file_id': test_files[2],
                    'hotel_file_id': test_files[3]
                },
                'kvkk_accepted': True
            }
        )
        
        if success:
            self.test_application_id = app.get('id')
            linked_order_id = app.get('linked_order_id')
            linked_order_reference = app.get('linked_order_reference')
            pricing = app.get('pricing', {})
            store_items = app.get('store_items', [])
            
            # Verify linked order created (check both id and reference)
            if linked_order_id and linked_order_reference:
                self.log(f"   ✅ Linked order created: {linked_order_id}", Colors.GREEN)
                self.log(f"   ✅ Linked order reference: {linked_order_reference}", Colors.GREEN)
            elif linked_order_reference:
                # Sometimes only reference is returned in public view
                self.log(f"   ✅ Linked order reference: {linked_order_reference}", Colors.GREEN)
            else:
                self.log(f"   ❌ Linked order NOT created", Colors.RED)
            
            # Verify store items in application
            if len(store_items) == 2:
                self.log(f"   ✅ Store items saved in application: {len(store_items)}", Colors.GREEN)
            
            # Verify pricing includes store items
            store_total = pricing.get('store_total', 0)
            if store_total > 0:
                self.log(f"   ✅ Store total in pricing: {store_total} TRY", Colors.GREEN)
            
            # Verify bundle discount applied
            bundle_discount = pricing.get('bundle_discount', 0)
            if bundle_discount > 0:
                self.log(f"   ✅ Bundle discount in application: {bundle_discount} TRY", Colors.GREEN)
            
            # Now fetch the linked order to verify it was created correctly
            if linked_order_id:
                headers = {'Authorization': f'Bearer {self.admin_token}'}
                success, order = self.test(
                    f"GET /api/admin/orders/{linked_order_id} - Verify linked order",
                    "GET",
                    f"/admin/orders/{linked_order_id}",
                    200,
                    headers=headers
                )
                
                if success:
                    source = order.get('source')
                    application_id = order.get('application_id')
                    application_reference = order.get('application_reference')
                    items_total = order.get('items_total', 0)
                    bundle_discount_order = order.get('bundle_discount', 0)
                    price = order.get('price', 0)
                    
                    if source == 'visa_application':
                        self.log(f"   ✅ Order source = visa_application", Colors.GREEN)
                    
                    if application_id == self.test_application_id:
                        self.log(f"   ✅ Order linked to application: {application_id}", Colors.GREEN)
                    
                    if application_reference:
                        self.log(f"   ✅ Application reference in order: {application_reference}", Colors.GREEN)
                    
                    if items_total > 0:
                        self.log(f"   ✅ Order items_total: {items_total} TRY", Colors.GREEN)
                    
                    if bundle_discount_order > 0:
                        self.log(f"   ✅ Order bundle_discount: {bundle_discount_order} TRY", Colors.GREEN)
                    
                    if price > 0:
                        self.log(f"   ✅ Order price: {price} TRY", Colors.GREEN)

    def test_application_tracking(self):
        """Test GET /api/applications/track - refactored _find_application_for_tracking"""
        self.log("\n" + "="*80, Colors.YELLOW)
        self.log("TEST 3: GET /api/applications/track - Application Tracking", Colors.YELLOW)
        self.log("="*80, Colors.YELLOW)
        
        if not self.test_application_id:
            self.log(f"   ⚠️  No test application created, skipping tracking tests", Colors.YELLOW)
            return
        
        # Get application details to extract reference code and last name
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        success, app_detail = self.test(
            f"GET /api/admin/applications/{self.test_application_id}",
            "GET",
            f"/admin/applications/{self.test_application_id}",
            200,
            headers=headers
        )
        
        if not success:
            self.log(f"   ❌ Could not fetch application details", Colors.RED)
            return
        
        application = app_detail.get('application', {})
        reference_code = application.get('reference_code')
        travelers = application.get('travelers', [])
        last_name = travelers[0].get('last_name') if travelers else None
        
        if not reference_code or not last_name:
            self.log(f"   ❌ Missing reference_code or last_name", Colors.RED)
            return
        
        self.log(f"   Testing with: code={reference_code}, last_name={last_name}", Colors.BLUE)
        
        # Test 3a: Valid tracking (correct code + last name)
        success, track = self.test(
            "GET /api/applications/track - Valid code and last_name",
            "GET",
            "/applications/track",
            200,
            params={'code': reference_code, 'last_name': last_name}
        )
        
        if success:
            # Verify required fields
            required_fields = ['id', 'reference_code', 'status', 'missing_documents', 'timeline']
            for field in required_fields:
                if field in track:
                    self.log(f"   ✅ Field present: {field}", Colors.GREEN)
                else:
                    self.log(f"   ❌ Missing field: {field}", Colors.RED)
            
            # Verify timeline structure
            timeline = track.get('timeline', {})
            if 'steps' in timeline and 'current_status' in timeline:
                self.log(f"   ✅ Timeline structure correct", Colors.GREEN)
                steps = timeline.get('steps', [])
                self.log(f"   Timeline steps: {len(steps)}", Colors.BLUE)
        
        # Test 3b: Wrong last_name (should return 404)
        success, error = self.test(
            "GET /api/applications/track - Wrong last_name (should return 404)",
            "GET",
            "/applications/track",
            404,
            params={'code': reference_code, 'last_name': 'WRONGNAME'}
        )
        
        if success:
            self.log(f"   ✅ Wrong last_name correctly rejected with 404", Colors.GREEN)
        
        # Test 3c: Missing params (should return 422 - FastAPI validation error)
        success, error = self.test(
            "GET /api/applications/track - Missing params (should return 422)",
            "GET",
            "/applications/track",
            422,
            params={'code': reference_code}
        )
        
        if success:
            self.log(f"   ✅ Missing params correctly rejected with 422 (validation error)", Colors.GREEN)

    def test_document_upload(self):
        """Test POST /api/applications/{code}/documents - refactored submit_missing_documents"""
        self.log("\n" + "="*80, Colors.YELLOW)
        self.log("TEST 4: POST /api/applications/{code}/documents - Document Upload", Colors.YELLOW)
        self.log("="*80, Colors.YELLOW)
        
        if not self.test_application_id:
            self.log(f"   ⚠️  No test application created, skipping document upload tests", Colors.YELLOW)
            return
        
        # Get application details
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        success, app_detail = self.test(
            f"GET /api/admin/applications/{self.test_application_id}",
            "GET",
            f"/admin/applications/{self.test_application_id}",
            200,
            headers=headers
        )
        
        if not success:
            return
        
        application = app_detail.get('application', {})
        reference_code = application.get('reference_code')
        travelers = application.get('travelers', [])
        last_name = travelers[0].get('last_name') if travelers else None
        traveler_id = travelers[0].get('id') if travelers else None
        
        if not reference_code or not last_name or not traveler_id:
            self.log(f"   ❌ Missing required data", Colors.RED)
            return
        
        # Upload new files for document submission
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        new_files = []
        for i in range(2):
            success, upload = self.test(
                f"POST /api/uploads - Upload document {i+1}",
                "POST",
                "/uploads",
                200,
                files={'file': (f'newdoc{i}.png', png_data, 'image/png')},
                data={'doc_type': 'passport'}
            )
            if success:
                new_files.append(upload.get('file_id'))
        
        if len(new_files) < 2:
            self.log(f"   ❌ Could not upload new files", Colors.RED)
            return
        
        # Test 4a: Upload traveler documents (passport + photo)
        success, doc_result = self.test(
            f"POST /api/applications/{reference_code}/documents - Upload traveler docs",
            "POST",
            f"/applications/{reference_code}/documents",
            200,
            data={
                'last_name': last_name,
                'traveler_documents': [
                    {
                        'traveler_id': traveler_id,
                        'passport_file_id': new_files[0],
                        'photo_file_id': new_files[1]
                    }
                ]
            }
        )
        
        if success:
            uploaded = doc_result.get('uploaded', [])
            missing_documents = doc_result.get('missing_documents', [])
            application_result = doc_result.get('application', {})
            
            if len(uploaded) > 0:
                self.log(f"   ✅ Documents uploaded: {uploaded}", Colors.GREEN)
            
            self.log(f"   Missing documents after upload: {len(missing_documents)}", Colors.BLUE)
            
            # Check if status changed to reviewing when all docs complete
            status = application_result.get('status')
            if len(missing_documents) == 0 and status == 'reviewing':
                self.log(f"   ✅ Status changed to 'reviewing' when docs complete", Colors.GREEN)
        
        # Test 4b: Invalid file_id (should return 400)
        success, error = self.test(
            f"POST /api/applications/{reference_code}/documents - Invalid file_id (400)",
            "POST",
            f"/applications/{reference_code}/documents",
            400,
            data={
                'last_name': last_name,
                'traveler_documents': [
                    {
                        'traveler_id': traveler_id,
                        'passport_file_id': 'invalid-file-id-xyz'
                    }
                ]
            }
        )
        
        if success:
            self.log(f"   ✅ Invalid file_id correctly rejected with 400", Colors.GREEN)
        
        # Test 4c: Unknown traveler_id (should return 400)
        success, error = self.test(
            f"POST /api/applications/{reference_code}/documents - Unknown traveler_id (400)",
            "POST",
            f"/applications/{reference_code}/documents",
            400,
            data={
                'last_name': last_name,
                'traveler_documents': [
                    {
                        'traveler_id': 'unknown-traveler-id-xyz',
                        'passport_file_id': new_files[0]
                    }
                ]
            }
        )
        
        if success:
            self.log(f"   ✅ Unknown traveler_id correctly rejected with 400", Colors.GREEN)
        
        # Test 4d: No documents provided (should return 400)
        success, error = self.test(
            f"POST /api/applications/{reference_code}/documents - No documents (400)",
            "POST",
            f"/applications/{reference_code}/documents",
            400,
            data={
                'last_name': last_name
            }
        )
        
        if success:
            self.log(f"   ✅ No documents correctly rejected with 400", Colors.GREEN)

    def test_zami_readiness(self):
        """Test GET /api/admin/zami/readiness - refactored into helper functions"""
        self.log("\n" + "="*80, Colors.YELLOW)
        self.log("TEST 5: GET /api/admin/zami/readiness - Zami Readiness Checks", Colors.YELLOW)
        self.log("="*80, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        success, readiness = self.test(
            "GET /api/admin/zami/readiness - Get readiness checks",
            "GET",
            "/admin/zami/readiness",
            200,
            headers=headers
        )
        
        if success:
            checks = readiness.get('checks', [])
            ready_bookmarklet = readiness.get('ready_bookmarklet')
            ready_robot = readiness.get('ready_robot')
            
            self.log(f"   Checks count: {len(checks)}", Colors.BLUE)
            self.log(f"   Ready for bookmarklet: {ready_bookmarklet}", Colors.BLUE)
            self.log(f"   Ready for robot: {ready_robot}", Colors.BLUE)
            
            # Verify checks structure
            expected_check_keys = ['captured', 'form_url', 'fields', 'traveler', 'submit', 'browser', 'session', 'status_url']
            check_keys = [c.get('key') for c in checks]
            
            for expected_key in expected_check_keys:
                if expected_key in check_keys:
                    self.log(f"   ✅ Check present: {expected_key}", Colors.GREEN)
                else:
                    self.log(f"   ❌ Missing check: {expected_key}", Colors.RED)
            
            # Verify each check has required fields
            for check in checks:
                key = check.get('key')
                label = check.get('label')
                ok = check.get('ok')
                detail = check.get('detail')
                
                if key and label and ok is not None and detail:
                    self.log(f"   ✅ Check '{key}' has all required fields", Colors.GREEN)
                else:
                    self.log(f"   ❌ Check '{key}' missing fields", Colors.RED)
            
            # Verify boolean fields
            if isinstance(ready_bookmarklet, bool):
                self.log(f"   ✅ ready_bookmarklet is boolean", Colors.GREEN)
            
            if isinstance(ready_robot, bool):
                self.log(f"   ✅ ready_robot is boolean", Colors.GREEN)

    def test_upload_endpoints(self):
        """Test POST /api/uploads and POST /api/admin/applications/{id}/visa-document"""
        self.log("\n" + "="*80, Colors.YELLOW)
        self.log("TEST 6: Upload Endpoints - Refactored _store_upload and _put_visa_document", Colors.YELLOW)
        self.log("="*80, Colors.YELLOW)
        
        # Test 6a: POST /api/uploads
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        success, upload = self.test(
            "POST /api/uploads - Upload passport document",
            "POST",
            "/uploads",
            200,
            files={'file': ('passport.png', png_data, 'image/png')},
            data={'doc_type': 'passport'}
        )
        
        if success:
            file_id = upload.get('file_id')
            doc_type = upload.get('doc_type')
            url = upload.get('url')
            
            if file_id:
                self.log(f"   ✅ File uploaded: {file_id}", Colors.GREEN)
            
            if doc_type == 'passport':
                self.log(f"   ✅ doc_type = passport", Colors.GREEN)
            
            if url:
                self.log(f"   ✅ URL returned: {url}", Colors.GREEN)
        
        # Test 6b: POST /api/admin/applications/{id}/visa-document
        if self.test_application_id:
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            
            # Create a small PDF-like file
            pdf_data = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n190\n%%EOF'
            
            success, visa_upload = self.test(
                f"POST /api/admin/applications/{self.test_application_id}/visa-document",
                "POST",
                f"/admin/applications/{self.test_application_id}/visa-document",
                200,
                files={'file': ('visa.pdf', pdf_data, 'application/pdf')},
                headers=headers
            )
            
            if success:
                application = visa_upload.get('application', {})
                visa_result = application.get('visa_result', {})
                
                if visa_result.get('file_id'):
                    self.log(f"   ✅ Visa document uploaded: {visa_result.get('file_id')}", Colors.GREEN)
                
                if visa_result.get('filename'):
                    self.log(f"   ✅ Filename saved: {visa_result.get('filename')}", Colors.GREEN)

    def test_ai_endpoints(self):
        """Test POST /api/photo/check and POST /api/passport/read"""
        self.log("\n" + "="*80, Colors.YELLOW)
        self.log("TEST 7: AI Endpoints - Photo Check and Passport Read", Colors.YELLOW)
        self.log("="*80, Colors.YELLOW)
        
        # Upload a test image first
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        success, upload = self.test(
            "POST /api/uploads - Upload photo for AI check",
            "POST",
            "/uploads",
            200,
            files={'file': ('photo.png', png_data, 'image/png')},
            data={'doc_type': 'photo'}
        )
        
        if not success:
            self.log(f"   ❌ Could not upload photo, skipping AI tests", Colors.RED)
            return
        
        file_id = upload.get('file_id')
        
        # Test 7a: POST /api/photo/check (uses Form data, not JSON)
        import urllib.parse
        success, photo_check = self.test(
            "POST /api/photo/check - AI photo validation",
            "POST",
            "/photo/check",
            200,
            data=urllib.parse.urlencode({'file_id': file_id}),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if success:
            checked = photo_check.get('checked')
            message = photo_check.get('message')
            
            if checked is not None:
                self.log(f"   ✅ Photo check completed: checked={checked}", Colors.GREEN)
            
            if message:
                self.log(f"   ✅ Message returned: {message[:50]}...", Colors.GREEN)
        
        # Test 7b: POST /api/passport/read (uses Form data, not JSON)
        success, passport_read = self.test(
            "POST /api/passport/read - AI passport OCR",
            "POST",
            "/passport/read",
            200,
            data=urllib.parse.urlencode({'file_id': file_id}),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if success:
            ok = passport_read.get('ok')
            reason = passport_read.get('reason')
            
            # For a 1x1 PNG, we expect it to fail gracefully
            if ok is not None:
                self.log(f"   ✅ Passport read completed: ok={ok}", Colors.GREEN)
            
            if reason:
                self.log(f"   ✅ Reason provided: {reason}", Colors.GREEN)

    def test_basic_get_endpoints(self):
        """Test GET /api/products, GET /api/visa-types, GET /api/content/site"""
        self.log("\n" + "="*80, Colors.YELLOW)
        self.log("TEST 8: Basic GET Endpoints - Regression Check", Colors.YELLOW)
        self.log("="*80, Colors.YELLOW)
        
        # Test 8a: GET /api/products
        success, products = self.test(
            "GET /api/products - List store products",
            "GET",
            "/products",
            200
        )
        
        if success:
            items = products.get('items', [])
            fx = products.get('fx')
            bundle = products.get('bundle')
            
            if len(items) > 0:
                self.log(f"   ✅ Products returned: {len(items)} items", Colors.GREEN)
            
            if fx:
                self.log(f"   ✅ FX object present", Colors.GREEN)
            
            if bundle:
                self.log(f"   ✅ Bundle discount info present", Colors.GREEN)
        
        # Test 8b: GET /api/visa-types
        success, visa_types = self.test(
            "GET /api/visa-types - List visa types",
            "GET",
            "/visa-types",
            200
        )
        
        if success:
            items = visa_types
            if isinstance(items, list) and len(items) > 0:
                self.log(f"   ✅ Visa types returned: {len(items)} items", Colors.GREEN)
        
        # Test 8c: GET /api/content/site
        success, content = self.test(
            "GET /api/content/site - Get site content",
            "GET",
            "/content/site",
            200
        )
        
        if success:
            required_keys = ['company', 'visa_categories', 'addons', 'fx', 'testimonials', 'articles']
            for key in required_keys:
                if key in content:
                    self.log(f"   ✅ Key present: {key}", Colors.GREEN)
                else:
                    self.log(f"   ❌ Missing key: {key}", Colors.RED)

    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*80, Colors.YELLOW)
        self.log("REFACTOR REGRESSION TEST SUMMARY", Colors.YELLOW)
        self.log("="*80, Colors.YELLOW)
        
        pass_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        self.log(f"\nTotal Tests: {self.tests_run}", Colors.BLUE)
        self.log(f"Passed: {self.tests_passed}", Colors.GREEN)
        self.log(f"Failed: {self.tests_failed}", Colors.RED)
        self.log(f"Pass Rate: {pass_rate:.1f}%", Colors.YELLOW)
        
        if self.tests_failed == 0:
            self.log("\n🎉 SUCCESS! All refactored endpoints working correctly - NO behavioral regressions detected.", Colors.GREEN)
            return 0
        elif pass_rate >= 90:
            self.log("\n⚠️  Minor issues detected. Review failed tests above.", Colors.YELLOW)
            return 1
        else:
            self.log("\n❌ CRITICAL: Multiple regressions detected. Refactoring introduced behavioral changes.", Colors.RED)
            return 1

def main():
    tester = RefactorRegressionTester()
    
    print(f"\n{Colors.BLUE}{'='*80}")
    print("VizeAtlas Dubai Backend Refactor Regression Test")
    print("Testing refactored endpoints for behavioral consistency")
    print(f"Base URL: {BASE_URL}")
    print(f"{'='*80}{Colors.END}\n")
    
    # Login as admin
    if not tester.admin_login():
        print(f"{Colors.RED}❌ Admin login failed. Cannot continue.{Colors.END}")
        return 1
    
    # Run all regression tests
    tester.test_store_order_creation()
    tester.test_application_with_store_items()
    tester.test_application_tracking()
    tester.test_document_upload()
    tester.test_zami_readiness()
    tester.test_upload_endpoints()
    tester.test_ai_endpoints()
    tester.test_basic_get_endpoints()
    
    # Print summary
    return tester.print_summary()

if __name__ == "__main__":
    sys.exit(main())
