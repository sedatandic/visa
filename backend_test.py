#!/usr/bin/env python3
"""
VizeAtlas Dubai Backend API Test Suite
Tests 4 new features: FX, Document Reminders, Visa Guides, Customer Account
"""

import requests
import sys
import time
from datetime import datetime

BASE_URL = "https://visa-application-ae.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@vizeatlas.com"
ADMIN_PASSWORD = "Dubai2026!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class APITester:
    def __init__(self):
        self.admin_token = None
        self.customer_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_application_id = None
        self.test_reference_code = None
        self.test_draft_id = None
        self.test_resume_code = None
        self.original_fx_settings = None
        self.original_transit_price = None

    def log(self, message, color=Colors.BLUE):
        print(f"{color}{message}{Colors.END}")

    def test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test"""
        url = f"{BASE_URL}{endpoint}"
        h = {'Content-Type': 'application/json'}
        if headers:
            h.update(headers)
        
        self.tests_run += 1
        self.log(f"\n🔍 Test {self.tests_run}: {name}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=h, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=h, params=params, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=h, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=h, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=h, timeout=10)
            
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
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("ADMIN LOGIN", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
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

    def test_fx_apis(self):
        """Test FX (USD/TRY) APIs"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("FEATURE 1: FX (USD/TRY) APIS", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Get current FX settings
        success, fx = self.test(
            "GET /api/admin/fx - Get current FX settings",
            "GET",
            "/admin/fx",
            200,
            headers=headers
        )
        
        if success:
            self.original_fx_settings = fx
            self.log(f"   Base rate: {fx.get('base_rate')} TRY", Colors.BLUE)
            self.log(f"   Effective rate: {fx.get('effective_rate')} TRY", Colors.BLUE)
            self.log(f"   Margin: {fx.get('margin_pct')}%", Colors.BLUE)
            self.log(f"   Mode: {fx.get('mode')}", Colors.BLUE)
            self.log(f"   Source: {fx.get('source')}", Colors.BLUE)
            
            # Check required fields
            required_fields = ['base_rate', 'effective_rate', 'margin_pct', 'mode', 'source']
            for field in required_fields:
                if field not in fx:
                    self.log(f"   ⚠️  Missing field: {field}", Colors.RED)
        
        # Refresh FX rate
        success, fx_refreshed = self.test(
            "GET /api/admin/fx?refresh=true - Fetch live rate",
            "GET",
            "/admin/fx",
            200,
            headers=headers,
            params={'refresh': 'true'}
        )
        
        if success:
            self.log(f"   Refreshed base rate: {fx_refreshed.get('base_rate')} TRY", Colors.BLUE)
        
        # Update margin
        success, fx_margin = self.test(
            "PUT /api/admin/fx - Set margin to 5%",
            "PUT",
            "/admin/fx",
            200,
            data={'margin_pct': 5},
            headers=headers
        )
        
        if success:
            expected_effective = fx_margin.get('base_rate', 0) * 1.05
            actual_effective = fx_margin.get('effective_rate', 0)
            if abs(actual_effective - expected_effective) < 0.1:
                self.log(f"   ✅ Effective rate correctly calculated: {actual_effective} TRY", Colors.GREEN)
            else:
                self.log(f"   ❌ Effective rate mismatch: expected ~{expected_effective}, got {actual_effective}", Colors.RED)
        
        # Set manual rate
        success, fx_manual = self.test(
            "PUT /api/admin/fx - Set manual rate to 40",
            "PUT",
            "/admin/fx",
            200,
            data={'manual_rate': 40},
            headers=headers
        )
        
        if success:
            if fx_manual.get('mode') == 'manual' and fx_manual.get('effective_rate') == 40:
                self.log(f"   ✅ Manual rate mode working correctly", Colors.GREEN)
            else:
                self.log(f"   ❌ Manual rate not applied correctly", Colors.RED)
        
        # Return to live rate
        success, fx_live = self.test(
            "PUT /api/admin/fx - Return to live rate (manual_rate=null)",
            "PUT",
            "/admin/fx",
            200,
            data={'manual_rate': None, 'margin_pct': 2},
            headers=headers
        )
        
        if success and fx_live.get('mode') == 'live':
            self.log(f"   ✅ Returned to live rate mode", Colors.GREEN)
        
        # Check visa types have USD prices
        success, visa_types = self.test(
            "GET /api/visa-types - Check USD prices",
            "GET",
            "/visa-types",
            200
        )
        
        if success:
            visa_30 = next((v for v in visa_types if v.get('id') == 'visa_30_single'), None)
            if visa_30:
                price_usd = visa_30.get('price_usd')
                price_try = visa_30.get('price')
                fx_rate = visa_30.get('fx_rate')
                
                self.log(f"   30-day visa: {price_usd} USD = {price_try} TRY (rate: {fx_rate})", Colors.BLUE)
                
                if price_usd == 110:
                    self.log(f"   ✅ visa_30_single price_usd is 110 USD", Colors.GREEN)
                else:
                    self.log(f"   ❌ visa_30_single price_usd should be 110, got {price_usd}", Colors.RED)
                
                # Check TRY price is calculated correctly (rounded to 10 TRY)
                if price_try and fx_rate:
                    expected_try = int(round((price_usd * fx_rate) / 10)) * 10
                    if abs(price_try - expected_try) < 20:  # Allow small variance
                        self.log(f"   ✅ TRY price correctly calculated and rounded", Colors.GREEN)
                    else:
                        self.log(f"   ⚠️  TRY price: expected ~{expected_try}, got {price_try}", Colors.YELLOW)
        
        # Test pricing quote with FX
        success, quote = self.test(
            "POST /api/pricing/quote - Check FX in quote",
            "POST",
            "/pricing/quote",
            200,
            data={
                'visa_type_ids': ['visa_30_single'],
                'addons': {'express': False, 'insurance': False}
            }
        )
        
        if success:
            if 'fx' in quote:
                self.log(f"   ✅ FX object present in quote", Colors.GREEN)
                self.log(f"   FX effective rate: {quote['fx'].get('effective_rate')} TRY", Colors.BLUE)
            else:
                self.log(f"   ❌ FX object missing in quote", Colors.RED)
        
        # Update visa transit price
        success, transit = self.test(
            "PATCH /api/admin/visa-types/visa_transit_48 - Update price_usd to 80",
            "PATCH",
            "/admin/visa-types/visa_transit_48",
            200,
            data={'price_usd': 80},
            headers=headers
        )
        
        if success:
            self.original_transit_price = 70  # Store original for cleanup
            price_try = transit.get('price')
            fx_rate = transit.get('fx_rate')
            if price_try and fx_rate:
                self.log(f"   ✅ Transit visa updated: 80 USD = {price_try} TRY", Colors.GREEN)
            
            # Restore original price
            self.test(
                "PATCH /api/admin/visa-types/visa_transit_48 - Restore price_usd to 70",
                "PATCH",
                "/admin/visa-types/visa_transit_48",
                200,
                data={'price_usd': 70},
                headers=headers
            )

    def test_document_reminders(self):
        """Test document reminder automation"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("FEATURE 2: DOCUMENT REMINDER AUTOMATION", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Get pending reminders
        success, pending = self.test(
            "GET /api/admin/document-reminders/pending - List applications with missing docs",
            "GET",
            "/admin/document-reminders/pending",
            200,
            headers=headers
        )
        
        if success:
            items = pending.get('items', [])
            due_count = pending.get('due', 0)
            self.log(f"   Found {len(items)} applications with missing documents", Colors.BLUE)
            self.log(f"   {due_count} are due for reminder", Colors.BLUE)
            
            # If we have applications, test reminder on first one
            if items:
                app = items[0]
                app_id = app.get('id')
                self.log(f"   Testing with application: {app.get('reference_code')}", Colors.BLUE)
                
                # Get missing documents for this application
                success, missing = self.test(
                    f"GET /api/admin/applications/{app_id}/missing-documents",
                    "GET",
                    f"/admin/applications/{app_id}/missing-documents",
                    200,
                    headers=headers
                )
                
                if success:
                    missing_docs = missing.get('missing', [])
                    reminder_count = missing.get('reminder_count', 0)
                    self.log(f"   Missing documents: {len(missing_docs)}", Colors.BLUE)
                    self.log(f"   Reminder count: {reminder_count}", Colors.BLUE)
                    
                    # Send reminder
                    success, reminder_result = self.test(
                        f"POST /api/admin/applications/{app_id}/send-document-reminder",
                        "POST",
                        f"/admin/applications/{app_id}/send-document-reminder",
                        200,
                        data={'origin_url': 'https://visa-application-ae.preview.emergentagent.com'},
                        headers=headers
                    )
                    
                    if success:
                        result = reminder_result.get('result', {})
                        email_status = result.get('status')
                        updated_app = reminder_result.get('application', {})
                        
                        self.log(f"   Email status: {email_status}", Colors.BLUE)
                        
                        if email_status == 'skipped':
                            self.log(f"   ✅ Email skipped (RESEND_API_KEY not configured - expected)", Colors.GREEN)
                        elif email_status == 'sent':
                            self.log(f"   ✅ Email sent successfully", Colors.GREEN)
                        
                        # Check if reminder_count increased
                        new_reminder = updated_app.get('document_reminder', {})
                        new_count = new_reminder.get('count', 0)
                        if new_count > reminder_count:
                            self.log(f"   ✅ Reminder count increased: {reminder_count} -> {new_count}", Colors.GREEN)
                        
                        # Check if status changed to documents_pending
                        if updated_app.get('status') == 'documents_pending':
                            self.log(f"   ✅ Status changed to documents_pending", Colors.GREEN)
        
        # Test reminder sweep
        success, sweep = self.test(
            "POST /api/admin/document-reminders/run - Run reminder sweep with force=true",
            "POST",
            "/admin/document-reminders/run",
            200,
            data={'force': True, 'origin_url': 'https://visa-application-ae.preview.emergentagent.com'},
            headers=headers
        )
        
        if success:
            sent = sweep.get('sent', 0)
            skipped = sweep.get('skipped', 0)
            self.log(f"   Sweep results: {sent} sent, {skipped} skipped", Colors.BLUE)
            self.log(f"   ✅ Reminder sweep completed", Colors.GREEN)

    def test_customer_account(self):
        """Test customer account features"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("FEATURE 3: CUSTOMER ACCOUNT", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        test_email = f"test{int(time.time())}@example.com"
        test_lastname = "TESTUSER"
        
        # Request login code
        success, code_response = self.test(
            "POST /api/account/request-code - Request login code",
            "POST",
            "/account/request-code",
            200,
            data={'email': test_email}
        )
        
        if success:
            email_status = code_response.get('email_status')
            self.log(f"   Email status: {email_status}", Colors.BLUE)
            
            if email_status == 'skipped':
                self.log(f"   ✅ Email skipped (RESEND_API_KEY not configured - expected)", Colors.GREEN)
            
            # Get the code from admin endpoint
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            success, codes = self.test(
                f"GET /api/admin/login-codes?email={test_email} - Get login code",
                "GET",
                "/admin/login-codes",
                200,
                headers=headers,
                params={'email': test_email}
            )
            
            if success and codes.get('items'):
                code = codes['items'][0].get('code')
                self.log(f"   Retrieved code: {code}", Colors.BLUE)
                
                # Verify code
                success, verify = self.test(
                    "POST /api/account/verify-code - Verify login code",
                    "POST",
                    "/account/verify-code",
                    200,
                    data={'email': test_email, 'code': code}
                )
                
                if success and 'token' in verify:
                    self.customer_token = verify['token']
                    self.log(f"   ✅ Customer token obtained via code", Colors.GREEN)
                
                # Test wrong code
                success, wrong = self.test(
                    "POST /api/account/verify-code - Test wrong code (should fail)",
                    "POST",
                    "/account/verify-code",
                    400,
                    data={'email': test_email, 'code': '999999'}
                )
                
                if success:
                    self.log(f"   ✅ Wrong code correctly rejected", Colors.GREEN)
        
        # Test lastname login (will fail as no application exists)
        success, lastname_login = self.test(
            "POST /api/account/login-lastname - Login with email+lastname (should fail - no application)",
            "POST",
            "/account/login-lastname",
            404,
            data={'email': test_email, 'last_name': test_lastname}
        )
        
        if success:
            self.log(f"   ✅ Correctly returns 404 when no application exists", Colors.GREEN)
        
        # Test account/me without token
        success, me_no_token = self.test(
            "GET /api/account/me - Without token (should fail)",
            "GET",
            "/account/me",
            401
        )
        
        if success:
            self.log(f"   ✅ Correctly requires authentication", Colors.GREEN)
        
        # Test account/me with token
        if self.customer_token:
            headers = {'Authorization': f'Bearer {self.customer_token}'}
            success, me = self.test(
                "GET /api/account/me - Get account info",
                "GET",
                "/account/me",
                200,
                headers=headers
            )
            
            if success:
                applications = me.get('applications', [])
                drafts = me.get('drafts', [])
                self.log(f"   Applications: {len(applications)}", Colors.BLUE)
                self.log(f"   Drafts: {len(drafts)}", Colors.BLUE)
                self.log(f"   ✅ Account info retrieved", Colors.GREEN)

    def test_drafts(self):
        """Test draft save and resume"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("FEATURE 4: DRAFT SAVE & RESUME", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        test_email = f"draft{int(time.time())}@example.com"
        
        # Save draft
        success, draft = self.test(
            "POST /api/drafts - Save draft",
            "POST",
            "/drafts",
            200,
            data={
                'email': test_email,
                'title': 'Test Draft',
                'step': 1,
                'traveler_count': 2,
                'data': {
                    'contact': {'full_name': 'Test User', 'email': test_email},
                    'travelers': [{'first_name': 'John', 'last_name': 'Doe'}]
                }
            }
        )
        
        if success:
            self.test_draft_id = draft.get('draft_id')
            self.test_resume_code = draft.get('resume_code')
            email_status = draft.get('email_status')
            
            self.log(f"   Draft ID: {self.test_draft_id}", Colors.BLUE)
            self.log(f"   Resume code: {self.test_resume_code}", Colors.BLUE)
            self.log(f"   Email status: {email_status}", Colors.BLUE)
            self.log(f"   ✅ Draft saved", Colors.GREEN)
            
            # Get draft with correct code
            success, get_draft = self.test(
                f"GET /api/drafts/{self.test_draft_id}?code={self.test_resume_code} - Get draft",
                "GET",
                f"/drafts/{self.test_draft_id}",
                200,
                params={'code': self.test_resume_code}
            )
            
            if success:
                self.log(f"   ✅ Draft retrieved with correct code", Colors.GREEN)
            
            # Try with wrong code
            success, wrong_code = self.test(
                f"GET /api/drafts/{self.test_draft_id}?code=WRONGCODE - Get draft with wrong code (should fail)",
                "GET",
                f"/drafts/{self.test_draft_id}",
                404,
                params={'code': 'WRONGCODE'}
            )
            
            if success:
                self.log(f"   ✅ Wrong code correctly rejected", Colors.GREEN)
            
            # Update draft (same draft_id and resume_code)
            success, update_draft = self.test(
                "POST /api/drafts - Update existing draft",
                "POST",
                "/drafts",
                200,
                data={
                    'email': test_email,
                    'draft_id': self.test_draft_id,
                    'resume_code': self.test_resume_code,
                    'title': 'Updated Draft',
                    'step': 2,
                    'traveler_count': 2,
                    'data': {
                        'contact': {'full_name': 'Test User Updated', 'email': test_email},
                        'travelers': [{'first_name': 'Jane', 'last_name': 'Doe'}]
                    }
                }
            )
            
            if success:
                self.log(f"   ✅ Draft updated", Colors.GREEN)

    def test_visa_guides(self):
        """Test visa guide content management"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("FEATURE 5: VISA GUIDE CONTENT MANAGEMENT", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # List guides
        success, guides = self.test(
            "GET /api/admin/visa-guides - List all guides",
            "GET",
            "/admin/visa-guides",
            200,
            headers=headers
        )
        
        if success:
            items = guides.get('items', [])
            self.log(f"   Found {len(items)} visa guides", Colors.BLUE)
            
            if items:
                # Test with first guide
                guide = items[0]
                slug = guide.get('slug')
                has_override = guide.get('has_override')
                
                self.log(f"   Testing with guide: {slug}", Colors.BLUE)
                self.log(f"   Has override: {has_override}", Colors.BLUE)
                
                # Get guide details
                success, detail = self.test(
                    f"GET /api/admin/visa-guides/{slug} - Get guide details",
                    "GET",
                    f"/admin/visa-guides/{slug}",
                    200,
                    headers=headers
                )
                
                if success:
                    effective = detail.get('effective', {})
                    defaults = detail.get('defaults', {})
                    override = detail.get('override', {})
                    
                    self.log(f"   Effective H1: {effective.get('h1', '')[:50]}...", Colors.BLUE)
                    self.log(f"   Has override: {detail.get('has_override')}", Colors.BLUE)
                    self.log(f"   ✅ Guide details retrieved", Colors.GREEN)
                    
                    # Update guide
                    success, updated = self.test(
                        f"PUT /api/admin/visa-guides/{slug} - Update guide",
                        "PUT",
                        f"/admin/visa-guides/{slug}",
                        200,
                        data={
                            'h1': 'Test Updated H1',
                            'seo_title': 'Test SEO Title',
                            'seo_description': 'Test SEO Description',
                            'intro': ['Test intro paragraph'],
                            'faqs': [{'q': 'Test question?', 'a': 'Test answer'}]
                        },
                        headers=headers
                    )
                    
                    if success:
                        self.log(f"   ✅ Guide updated", Colors.GREEN)
                        
                        # Verify public endpoint returns updated content
                        success, public = self.test(
                            f"GET /api/visa-guides/{slug} - Verify public endpoint",
                            "GET",
                            f"/visa-guides/{slug}",
                            200
                        )
                        
                        if success:
                            public_h1 = public.get('h1', '')
                            if public_h1 == 'Test Updated H1':
                                self.log(f"   ✅ Public endpoint returns updated content", Colors.GREEN)
                            else:
                                self.log(f"   ⚠️  Public H1: {public_h1}", Colors.YELLOW)
                        
                        # Reset to default
                        success, reset = self.test(
                            f"DELETE /api/admin/visa-guides/{slug} - Reset to default",
                            "DELETE",
                            f"/admin/visa-guides/{slug}",
                            200,
                            headers=headers
                        )
                        
                        if success:
                            reset_detail = reset.get('effective', {})
                            if reset_detail.get('h1') != 'Test Updated H1':
                                self.log(f"   ✅ Guide reset to default", Colors.GREEN)
                            else:
                                self.log(f"   ⚠️  Guide may not have reset correctly", Colors.YELLOW)

    def print_summary(self):
        """Print test summary"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST SUMMARY", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        pass_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        self.log(f"\nTotal Tests: {self.tests_run}", Colors.BLUE)
        self.log(f"Passed: {self.tests_passed}", Colors.GREEN)
        self.log(f"Failed: {self.tests_failed}", Colors.RED)
        self.log(f"Pass Rate: {pass_rate:.1f}%", Colors.YELLOW)
        
        if pass_rate >= 90:
            self.log("\n🎉 Excellent! Backend APIs are working well.", Colors.GREEN)
        elif pass_rate >= 70:
            self.log("\n⚠️  Good, but some issues need attention.", Colors.YELLOW)
        else:
            self.log("\n❌ Critical issues found. Main agent should fix before frontend testing.", Colors.RED)
        
        return 0 if self.tests_failed == 0 else 1

def main():
    tester = APITester()
    
    print(f"\n{Colors.BLUE}{'='*60}")
    print("VizeAtlas Dubai Backend API Test Suite")
    print(f"Testing 4 New Features")
    print(f"Base URL: {BASE_URL}")
    print(f"{'='*60}{Colors.END}\n")
    
    # Login as admin
    if not tester.admin_login():
        print(f"{Colors.RED}❌ Admin login failed. Cannot continue.{Colors.END}")
        return 1
    
    # Run all feature tests
    tester.test_fx_apis()
    tester.test_document_reminders()
    tester.test_customer_account()
    tester.test_drafts()
    tester.test_visa_guides()
    
    # Print summary
    return tester.print_summary()

if __name__ == "__main__":
    sys.exit(main())
