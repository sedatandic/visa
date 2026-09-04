#!/usr/bin/env python3
"""
VizeAtlas Dubai Store (eSIM & Insurance) Backend API Test Suite
Tests all store-related endpoints for iteration 14
"""

import requests
import sys
import time
from datetime import datetime

BASE_URL = "https://vize-atlas-hub.preview.emergentagent.com/api"
ADMIN_EMAIL = "admin@vizeatlas.com"
ADMIN_PASSWORD = "Dubai2026!"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class StoreAPITester:
    def __init__(self):
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_order_id = None
        self.test_reference_code = None
        self.test_email = f"test_{int(time.time())}@example.com"
        self.original_prices = {}

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

    def test_products_api(self):
        """Test GET /api/products"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST: PRODUCTS API", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        # Test 1: Get all products
        success, response = self.test(
            "GET /api/products - All products",
            "GET",
            "/products",
            200
        )
        
        if success:
            items = response.get('items', [])
            fx = response.get('fx', {})
            self.log(f"   Products count: {len(items)}", Colors.BLUE)
            self.log(f"   FX rate: {fx.get('effective_rate')}", Colors.BLUE)
            
            if len(items) == 6:
                self.log(f"   ✅ Correct product count (6)", Colors.GREEN)
            else:
                self.log(f"   ⚠️  Expected 6 products, got {len(items)}", Colors.YELLOW)
            
            # Verify product structure
            esim_count = sum(1 for p in items if p.get('kind') == 'esim')
            insurance_count = sum(1 for p in items if p.get('kind') == 'insurance')
            
            self.log(f"   eSIM products: {esim_count}", Colors.BLUE)
            self.log(f"   Insurance products: {insurance_count}", Colors.BLUE)
            
            if esim_count == 4 and insurance_count == 2:
                self.log(f"   ✅ Correct product distribution (4 eSIM + 2 insurance)", Colors.GREEN)
            
            # Verify each product has required fields
            for p in items:
                if all(k in p for k in ['id', 'kind', 'name', 'price_usd', 'price', 'currency', 'features']):
                    self.log(f"   ✅ {p['id']}: {p['name']} - ${p['price_usd']} / {p['price']} {p['currency']}", Colors.GREEN)
                else:
                    self.log(f"   ❌ {p.get('id', 'unknown')}: Missing required fields", Colors.RED)
        
        # Test 2: Filter by kind=esim
        success, response = self.test(
            "GET /api/products?kind=esim - Filter eSIM",
            "GET",
            "/products",
            200,
            params={'kind': 'esim'}
        )
        
        if success:
            items = response.get('items', [])
            if len(items) == 4 and all(p.get('kind') == 'esim' for p in items):
                self.log(f"   ✅ eSIM filter working (4 products)", Colors.GREEN)
        
        # Test 3: Filter by kind=insurance
        success, response = self.test(
            "GET /api/products?kind=insurance - Filter insurance",
            "GET",
            "/products",
            200,
            params={'kind': 'insurance'}
        )
        
        if success:
            items = response.get('items', [])
            if len(items) == 2 and all(p.get('kind') == 'insurance' for p in items):
                self.log(f"   ✅ Insurance filter working (2 products)", Colors.GREEN)
        
        # Test 4: Invalid kind should return 400
        success, response = self.test(
            "GET /api/products?kind=invalid - Invalid kind",
            "GET",
            "/products",
            400,
            params={'kind': 'invalid'}
        )

    def test_create_order_transfer(self):
        """Test POST /api/orders with transfer payment"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST: CREATE ORDER (TRANSFER)", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        success, response = self.test(
            "POST /api/orders - Create order with transfer payment",
            "POST",
            "/orders",
            200,
            data={
                "items": [
                    {"product_id": "esim_3gb", "quantity": 2},
                    {"product_id": "ins_basic", "quantity": 1}
                ],
                "contact": {
                    "full_name": "Test User",
                    "email": self.test_email,
                    "phone": "+905551234567"
                },
                "travel_start": "2026-09-01",
                "travel_end": "2026-09-15",
                "note": "Test order for backend testing",
                "payment_method": "transfer"
            }
        )
        
        if success:
            order = response.get('order', {})
            bank = response.get('bank', {})
            
            self.test_order_id = order.get('id')
            self.test_reference_code = order.get('reference_code')
            
            self.log(f"   Order ID: {self.test_order_id}", Colors.BLUE)
            self.log(f"   Reference: {self.test_reference_code}", Colors.BLUE)
            self.log(f"   Total: {order.get('price')} {order.get('currency')}", Colors.BLUE)
            
            # Verify reference code starts with 'SV-'
            if self.test_reference_code and self.test_reference_code.startswith('SV-'):
                self.log(f"   ✅ Reference code format correct (SV-*)", Colors.GREEN)
            
            # Verify items calculation
            items = order.get('items', [])
            if len(items) == 2:
                self.log(f"   ✅ Correct item count (2)", Colors.GREEN)
                for item in items:
                    expected_total = item['unit_price'] * item['quantity']
                    if abs(item['total'] - expected_total) < 0.01:
                        self.log(f"   ✅ {item['name']}: {item['quantity']} x {item['unit_price']} = {item['total']}", Colors.GREEN)
            
            # Verify bank details returned
            if bank and bank.get('iban'):
                self.log(f"   ✅ Bank details returned", Colors.GREEN)
                self.log(f"   Bank: {bank.get('bank_name')}", Colors.BLUE)
                self.log(f"   IBAN: {bank.get('iban')}", Colors.BLUE)
        
        # Test validation: invalid product_id
        success, response = self.test(
            "POST /api/orders - Invalid product_id",
            "POST",
            "/orders",
            400,
            data={
                "items": [{"product_id": "invalid_product", "quantity": 1}],
                "contact": {
                    "full_name": "Test User",
                    "email": self.test_email,
                    "phone": "+905551234567"
                },
                "payment_method": "transfer"
            }
        )
        
        # Test validation: quantity 0
        success, response = self.test(
            "POST /api/orders - Quantity 0",
            "POST",
            "/orders",
            422,
            data={
                "items": [{"product_id": "esim_1gb", "quantity": 0}],
                "contact": {
                    "full_name": "Test User",
                    "email": self.test_email,
                    "phone": "+905551234567"
                },
                "payment_method": "transfer"
            }
        )
        
        # Test validation: quantity > 10
        success, response = self.test(
            "POST /api/orders - Quantity > 10",
            "POST",
            "/orders",
            422,
            data={
                "items": [{"product_id": "esim_1gb", "quantity": 11}],
                "contact": {
                    "full_name": "Test User",
                    "email": self.test_email,
                    "phone": "+905551234567"
                },
                "payment_method": "transfer"
            }
        )
        
        # Test validation: missing contact fields
        success, response = self.test(
            "POST /api/orders - Missing contact email",
            "POST",
            "/orders",
            422,
            data={
                "items": [{"product_id": "esim_1gb", "quantity": 1}],
                "contact": {
                    "full_name": "Test User",
                    "phone": "+905551234567"
                },
                "payment_method": "transfer"
            }
        )

    def test_create_order_card(self):
        """Test POST /api/orders with card payment and checkout"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST: CREATE ORDER (CARD) & CHECKOUT", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        # Create order with card payment
        success, response = self.test(
            "POST /api/orders - Create order with card payment",
            "POST",
            "/orders",
            200,
            data={
                "items": [{"product_id": "esim_unlimited", "quantity": 1}],
                "contact": {
                    "full_name": "Card Test User",
                    "email": f"card_{self.test_email}",
                    "phone": "+905551234567"
                },
                "payment_method": "card"
            }
        )
        
        if success:
            order = response.get('order', {})
            order_id = order.get('id')
            
            self.log(f"   Order ID: {order_id}", Colors.BLUE)
            self.log(f"   Payment method: {order.get('payment', {}).get('method')}", Colors.BLUE)
            
            # Test checkout session creation
            success, checkout_response = self.test(
                "POST /api/orders/{order_id}/checkout - Create checkout session",
                "POST",
                f"/orders/{order_id}/checkout",
                200,
                data={"origin_url": "https://vize-atlas-hub.preview.emergentagent.com"}
            )
            
            if success:
                checkout_url = checkout_response.get('checkout_url')
                session_id = checkout_response.get('session_id')
                
                if checkout_url and session_id:
                    self.log(f"   ✅ Checkout session created", Colors.GREEN)
                    self.log(f"   Session ID: {session_id}", Colors.BLUE)
                    self.log(f"   ⚠️  DO NOT complete payment (test only)", Colors.YELLOW)
                else:
                    self.log(f"   ❌ Missing checkout_url or session_id", Colors.RED)
            
            # Test: Cannot checkout already paid order
            # First mark as paid
            headers = {'Authorization': f'Bearer {self.admin_token}'}
            success, _ = self.test(
                "PATCH /api/admin/orders/{order_id} - Mark as paid",
                "PATCH",
                f"/admin/orders/{order_id}",
                200,
                data={"payment_status": "paid"},
                headers=headers
            )
            
            if success:
                # Try to checkout again
                success, response = self.test(
                    "POST /api/orders/{order_id}/checkout - Already paid order",
                    "POST",
                    f"/orders/{order_id}/checkout",
                    400,
                    data={"origin_url": "https://vize-atlas-hub.preview.emergentagent.com"}
                )

    def test_get_order(self):
        """Test GET /api/orders/{reference}"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST: GET ORDER BY REFERENCE", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        if not self.test_reference_code:
            self.log("   ⚠️  No test order created, skipping", Colors.YELLOW)
            return
        
        # Test: Get order with correct email
        success, response = self.test(
            f"GET /api/orders/{self.test_reference_code} - Correct email",
            "GET",
            f"/orders/{self.test_reference_code}",
            200,
            params={'email': self.test_email}
        )
        
        if success:
            order = response.get('order', {})
            if order.get('reference_code') == self.test_reference_code:
                self.log(f"   ✅ Order retrieved successfully", Colors.GREEN)
        
        # Test: Get order with wrong email
        success, response = self.test(
            f"GET /api/orders/{self.test_reference_code} - Wrong email",
            "GET",
            f"/orders/{self.test_reference_code}",
            404,
            params={'email': 'wrong@example.com'}
        )
        
        # Test: Non-existent reference
        success, response = self.test(
            "GET /api/orders/INVALID - Non-existent reference",
            "GET",
            "/orders/SV-INVALID123",
            404,
            params={'email': self.test_email}
        )

    def test_admin_orders(self):
        """Test admin order management endpoints"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST: ADMIN ORDER MANAGEMENT", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test: Get all orders
        success, response = self.test(
            "GET /api/admin/orders - List all orders",
            "GET",
            "/admin/orders",
            200,
            headers=headers
        )
        
        if success:
            items = response.get('items', [])
            self.log(f"   Total orders: {len(items)}", Colors.BLUE)
        
        if not self.test_order_id:
            self.log("   ⚠️  No test order created, skipping detail tests", Colors.YELLOW)
            return
        
        # Test: Get order detail
        success, response = self.test(
            f"GET /api/admin/orders/{self.test_order_id} - Order detail",
            "GET",
            f"/admin/orders/{self.test_order_id}",
            200,
            headers=headers
        )
        
        # Test: Update order payment status to paid
        success, response = self.test(
            f"PATCH /api/admin/orders/{self.test_order_id} - Mark as paid",
            "PATCH",
            f"/admin/orders/{self.test_order_id}",
            200,
            data={"payment_status": "paid"},
            headers=headers
        )
        
        if success:
            order = response
            if order.get('payment', {}).get('status') == 'paid':
                self.log(f"   ✅ Payment status updated to paid", Colors.GREEN)
            if order.get('status') == 'processing':
                self.log(f"   ✅ Order status auto-updated to processing", Colors.GREEN)
        
        # Test: Update order status to cancelled
        success, response = self.test(
            f"PATCH /api/admin/orders/{self.test_order_id} - Cancel order",
            "PATCH",
            f"/admin/orders/{self.test_order_id}",
            200,
            data={"status": "cancelled"},
            headers=headers
        )
        
        # Test: Invalid status
        success, response = self.test(
            f"PATCH /api/admin/orders/{self.test_order_id} - Invalid status",
            "PATCH",
            f"/admin/orders/{self.test_order_id}",
            400,
            data={"status": "invalid_status"},
            headers=headers
        )

    def test_admin_deliver_order(self):
        """Test POST /api/admin/orders/{order_id}/deliver"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST: ADMIN ORDER DELIVERY", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Create a new order for delivery test
        success, response = self.test(
            "POST /api/orders - Create order for delivery test",
            "POST",
            "/orders",
            200,
            data={
                "items": [
                    {"product_id": "esim_1gb", "quantity": 1},
                    {"product_id": "ins_plus", "quantity": 1}
                ],
                "contact": {
                    "full_name": "Delivery Test User",
                    "email": f"delivery_{self.test_email}",
                    "phone": "+905551234567"
                },
                "payment_method": "transfer"
            }
        )
        
        if not success:
            self.log("   ⚠️  Could not create test order, skipping delivery tests", Colors.YELLOW)
            return
        
        delivery_order_id = response.get('order', {}).get('id')
        
        # Mark as paid first
        success, _ = self.test(
            f"PATCH /api/admin/orders/{delivery_order_id} - Mark as paid",
            "PATCH",
            f"/admin/orders/{delivery_order_id}",
            200,
            data={"payment_status": "paid"},
            headers=headers
        )
        
        # Test: Deliver without files (should fail)
        success, response = self.test(
            f"POST /api/admin/orders/{delivery_order_id}/deliver - No files",
            "POST",
            f"/admin/orders/{delivery_order_id}/deliver",
            400,
            data={},
            headers=headers
        )
        
        # Upload test files
        # Note: In real scenario, files would be uploaded via POST /api/uploads
        # For this test, we'll use placeholder file IDs
        self.log("   ℹ️  Note: File upload requires POST /api/uploads first", Colors.BLUE)
        self.log("   ℹ️  Skipping actual delivery test (requires file upload)", Colors.BLUE)

    def test_admin_products(self):
        """Test admin product management"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST: ADMIN PRODUCT MANAGEMENT", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        # Test: Get all products (admin)
        success, response = self.test(
            "GET /api/admin/products - List all products",
            "GET",
            "/admin/products",
            200,
            headers=headers
        )
        
        if success:
            items = response.get('items', [])
            self.log(f"   Total products: {len(items)}", Colors.BLUE)
            
            # Store original prices
            for item in items:
                self.original_prices[item['id']] = item['price_usd']
        
        # Test: Update product price
        success, response = self.test(
            "PATCH /api/admin/products/esim_1gb - Update price",
            "PATCH",
            "/admin/products/esim_1gb",
            200,
            data={"price_usd": 10.0},
            headers=headers
        )
        
        if success:
            product = response
            if product.get('price_usd') == 10.0:
                self.log(f"   ✅ Price updated to $10.0", Colors.GREEN)
            # Verify TRY price is calculated with current FX rate
            if product.get('price') and product.get('fx_rate'):
                expected_try = round(10.0 * product['fx_rate'] / 10) * 10
                if abs(product['price'] - expected_try) < 1:
                    self.log(f"   ✅ TRY price calculated correctly: {product['price']}", Colors.GREEN)
        
        # Restore original prices
        self.log("\n   Restoring original prices...", Colors.BLUE)
        for product_id, original_price in self.original_prices.items():
            success, _ = self.test(
                f"PATCH /api/admin/products/{product_id} - Restore price",
                "PATCH",
                f"/admin/products/{product_id}",
                200,
                data={"price_usd": original_price},
                headers=headers
            )

    def test_account_orders(self):
        """Test GET /api/account/orders (customer token required)"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST: CUSTOMER ACCOUNT ORDERS", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        # Test: Without token (should fail)
        success, response = self.test(
            "GET /api/account/orders - No token",
            "GET",
            "/account/orders",
            401
        )
        
        # Test: Login with email + lastname
        success, login_response = self.test(
            "POST /api/account/login-lastname - Customer login",
            "POST",
            "/account/login-lastname",
            200,
            data={
                "email": self.test_email,
                "last_name": "User"
            }
        )
        
        if success:
            customer_token = login_response.get('token')
            if customer_token:
                self.log(f"   ✅ Customer token obtained", Colors.GREEN)
                
                # Test: Get orders with token
                headers = {'Authorization': f'Bearer {customer_token}'}
                success, response = self.test(
                    "GET /api/account/orders - With token",
                    "GET",
                    "/account/orders",
                    200,
                    headers=headers
                )
                
                if success:
                    items = response.get('items', [])
                    self.log(f"   Orders for {self.test_email}: {len(items)}", Colors.BLUE)
                    if len(items) > 0:
                        self.log(f"   ✅ Orders retrieved successfully", Colors.GREEN)

    def test_application_addons(self):
        """Test application flow with addons"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST: APPLICATION WITH ADDONS", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        # Test: Get site content (should include addons)
        success, response = self.test(
            "GET /api/content/site - Check addons",
            "GET",
            "/content/site",
            200
        )
        
        if success:
            addons = response.get('addons', {})
            required_addons = ['express', 'insurance', 'insurance_plus', 'esim']
            
            for addon_id in required_addons:
                if addon_id in addons:
                    addon = addons[addon_id]
                    self.log(f"   ✅ {addon_id}: {addon.get('name')} - ${addon.get('price_usd')}", Colors.GREEN)
                else:
                    self.log(f"   ❌ Missing addon: {addon_id}", Colors.RED)
        
        # Test: Pricing quote with addons
        success, response = self.test(
            "POST /api/pricing/quote - With addons",
            "POST",
            "/pricing/quote",
            200,
            data={
                "travelers": [
                    {"visa_type_id": "visa_30_single"},
                    {"visa_type_id": "visa_30_single"}
                ],
                "addons": {
                    "esim": True,
                    "insurance_plus": True
                }
            }
        )
        
        if success:
            pricing = response.get('pricing', {})
            addon_lines = pricing.get('addons', [])
            
            self.log(f"   Traveler count: {pricing.get('traveler_count')}", Colors.BLUE)
            self.log(f"   Addons total: {pricing.get('addons_total')} {pricing.get('currency')}", Colors.BLUE)
            
            # Verify addons are per person
            esim_addon = next((a for a in addon_lines if a['id'] == 'esim'), None)
            insurance_addon = next((a for a in addon_lines if a['id'] == 'insurance_plus'), None)
            
            if esim_addon and esim_addon['quantity'] == 2:
                self.log(f"   ✅ eSIM addon multiplied by traveler count (2)", Colors.GREEN)
            if insurance_addon and insurance_addon['quantity'] == 2:
                self.log(f"   ✅ Insurance addon multiplied by traveler count (2)", Colors.GREEN)

    def test_regression_apis(self):
        """Test regression: ensure existing APIs still work"""
        self.log("\n" + "="*60, Colors.YELLOW)
        self.log("TEST: REGRESSION - EXISTING APIS", Colors.YELLOW)
        self.log("="*60, Colors.YELLOW)
        
        # Test visa types
        success, response = self.test(
            "GET /api/visa-types - Visa types",
            "GET",
            "/visa-types",
            200
        )
        
        # Test visa guides
        success, response = self.test(
            "GET /api/visa-guides - Visa guides",
            "GET",
            "/visa-guides",
            200
        )
        
        # Test FX
        success, response = self.test(
            "GET /api/fx - Exchange rate",
            "GET",
            "/fx",
            200
        )
        
        if success:
            fx = response
            if 'effective_rate' in fx and 'currency_pair' in fx:
                self.log(f"   ✅ FX API working: {fx.get('effective_rate')} {fx.get('currency_pair')}", Colors.GREEN)
            # Verify sensitive data NOT exposed
            if 'margin_pct' not in fx and 'manual_rate' not in fx:
                self.log(f"   ✅ Sensitive FX data not exposed", Colors.GREEN)

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
            self.log("\n🎉 Excellent! Store APIs are working well.", Colors.GREEN)
        elif pass_rate >= 70:
            self.log("\n⚠️  Good, but some issues need attention.", Colors.YELLOW)
        else:
            self.log("\n❌ Critical issues found. Main agent should fix before frontend testing.", Colors.RED)
        
        return 0 if self.tests_failed == 0 else 1

def main():
    tester = StoreAPITester()
    
    print(f"\n{Colors.BLUE}{'='*60}")
    print("VizeAtlas Dubai Store Backend API Test Suite")
    print(f"Testing eSIM & Insurance Features (Iteration 14)")
    print(f"Base URL: {BASE_URL}")
    print(f"{'='*60}{Colors.END}\n")
    
    # Login as admin
    if not tester.admin_login():
        print(f"{Colors.RED}❌ Admin login failed. Cannot continue.{Colors.END}")
        return 1
    
    # Run all store feature tests
    tester.test_products_api()
    tester.test_create_order_transfer()
    tester.test_create_order_card()
    tester.test_get_order()
    tester.test_admin_orders()
    tester.test_admin_deliver_order()
    tester.test_admin_products()
    tester.test_account_orders()
    tester.test_application_addons()
    tester.test_regression_apis()
    
    # Print summary
    return tester.print_summary()

if __name__ == "__main__":
    sys.exit(main())
