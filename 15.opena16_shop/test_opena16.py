#!/usr/bin/env python3
"""
Integration Tests für opena16 - Shop Management Agent
Port: 12361
Kürzel: shopp

Tests:
1. Health Check
2. Root Endpoint
3. Create Product
4. List Products
5. Update Product
6. Create Category
7. List Categories
8. Update Inventory
9. List Inventory
10. Create Order
11. List Orders
12. Command Endpoint (create_product)
13. Delete Product
14. Strict JSON validation
"""

import sys
import json
import time
import requests
from pathlib import Path

# Config
BASE_URL = "http://127.0.0.1:12361"
BEARER_TOKEN = "c899b90d-faf8-485b-afa4-078357cf5313"
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# Test-Statistiken
total_tests = 14
passed_tests = 0
failed_tests = 0

# Test data (for cleanup)
created_product_ids = []
created_order_ids = []

def log_test(test_num: int, test_name: str, passed: bool, details: str = ""):
    """Test-Ergebnis loggen"""
    global passed_tests, failed_tests
    
    status = "✓" if passed else "✗"
    color = "\033[0;32m" if passed else "\033[0;31m"
    reset = "\033[0m"
    
    if passed:
        passed_tests += 1
    else:
        failed_tests += 1
    
    print(f"{color}[{status}] Test {test_num} ({test_name}): {'PASS' if passed else 'FAIL'}{reset}{f' - {details}' if details else ''}")

def test_1_health():
    """Test 1: Health Check"""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if resp.status_code != 200:
            log_test(1, "Health", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        required_keys = ["status", "service", "kuerzel", "port", "uptime_seconds", "total_products", "total_orders"]
        missing = [k for k in required_keys if k not in data]
        
        if missing:
            log_test(1, "Health", False, f"Missing keys: {missing}")
            return
        
        if data["status"] != "ok":
            log_test(1, "Health", False, f"Status not ok: {data['status']}")
            return
        
        if data["kuerzel"] != "shopp":
            log_test(1, "Health", False, f"Wrong kürzel: {data['kuerzel']}")
            return
        
        uptime = data["uptime_seconds"]
        products = data["total_products"]
        orders = data["total_orders"]
        
        log_test(1, "Health", True, f"Uptime: {uptime:.2f}s, Products: {products}, Orders: {orders}")
    
    except Exception as e:
        log_test(1, "Health", False, str(e))

def test_2_root():
    """Test 2: Root Endpoint"""
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        
        if resp.status_code != 200:
            log_test(2, "Root", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        if "service" not in data or "kuerzel" not in data:
            log_test(2, "Root", False, "Missing service/kuerzel")
            return
        
        log_test(2, "Root", True)
    
    except Exception as e:
        log_test(2, "Root", False, str(e))

def test_3_create_product():
    """Test 3: Create Product"""
    global created_product_ids
    
    try:
        payload = {
            "title": "Test Product",
            "description": "Integration test product",
            "sku": "TEST-001",
            "price": 29.99,
            "currency": "EUR",
            "status": "active",
            "tags": ["test", "integration"]
        }
        
        resp = requests.post(f"{BASE_URL}/products/create", headers=HEADERS, json=payload, timeout=5)
        
        if resp.status_code != 200:
            log_test(3, "Create Product", False, f"Status {resp.status_code}: {resp.text}")
            return
        
        data = resp.json()
        
        if "product_id" not in data:
            log_test(3, "Create Product", False, "Missing product_id")
            return
        
        created_product_ids.append(data["product_id"])
        
        if data["sku"] != "TEST-001":
            log_test(3, "Create Product", False, f"Wrong SKU: {data['sku']}")
            return
        
        if data["price"] != 29.99:
            log_test(3, "Create Product", False, f"Wrong price: {data['price']}")
            return
        
        log_test(3, "Create Product", True, f"Product ID: {data['product_id']}, SKU: {data['sku']}")
    
    except Exception as e:
        log_test(3, "Create Product", False, str(e))

def test_4_list_products():
    """Test 4: List Products"""
    try:
        payload = {
            "max_results": 50
        }
        
        resp = requests.post(f"{BASE_URL}/products/list", headers=HEADERS, json=payload, timeout=5)
        
        if resp.status_code != 200:
            log_test(4, "List Products", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        if not isinstance(data, list):
            log_test(4, "List Products", False, "Response not a list")
            return
        
        # Should have at least the product we created
        if len(data) == 0:
            log_test(4, "List Products", False, "No products found")
            return
        
        log_test(4, "List Products", True, f"Total: {len(data)}")
    
    except Exception as e:
        log_test(4, "List Products", False, str(e))

def test_5_update_product():
    """Test 5: Update Product"""
    global created_product_ids
    
    if not created_product_ids:
        log_test(5, "Update Product", False, "No product to update")
        return
    
    try:
        payload = {
            "product_id": created_product_ids[0],
            "title": "Test Product (Updated)",
            "price": 39.99,
            "tags": ["test", "updated"]
        }
        
        resp = requests.put(f"{BASE_URL}/products/update", headers=HEADERS, json=payload, timeout=5)
        
        if resp.status_code != 200:
            log_test(5, "Update Product", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        if data["title"] != "Test Product (Updated)":
            log_test(5, "Update Product", False, f"Title not updated: {data['title']}")
            return
        
        if data["price"] != 39.99:
            log_test(5, "Update Product", False, f"Price not updated: {data['price']}")
            return
        
        log_test(5, "Update Product", True, f"Updated: {data['title']}, Price: {data['price']}")
    
    except Exception as e:
        log_test(5, "Update Product", False, str(e))

def test_6_create_category():
    """Test 6: Create Category"""
    try:
        payload = {
            "name": "Test Category",
            "description": "Integration test category"
        }
        
        resp = requests.post(f"{BASE_URL}/categories/create", headers=HEADERS, json=payload, timeout=5)
        
        if resp.status_code != 200:
            log_test(6, "Create Category", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        if "category_id" not in data:
            log_test(6, "Create Category", False, "Missing category_id")
            return
        
        if data["name"] != "Test Category":
            log_test(6, "Create Category", False, f"Wrong name: {data['name']}")
            return
        
        log_test(6, "Create Category", True, f"Category ID: {data['category_id']}")
    
    except Exception as e:
        log_test(6, "Create Category", False, str(e))

def test_7_list_categories():
    """Test 7: List Categories"""
    try:
        resp = requests.get(f"{BASE_URL}/categories/list", headers=HEADERS, timeout=5)
        
        if resp.status_code != 200:
            log_test(7, "List Categories", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        if not isinstance(data, list):
            log_test(7, "List Categories", False, "Response not a list")
            return
        
        log_test(7, "List Categories", True, f"Total: {len(data)}")
    
    except Exception as e:
        log_test(7, "List Categories", False, str(e))

def test_8_update_inventory():
    """Test 8: Update Inventory"""
    try:
        payload = {
            "sku": "TEST-001",
            "quantity": 100,
            "warehouse": "main"
        }
        
        resp = requests.post(f"{BASE_URL}/inventory/update", headers=HEADERS, json=payload, timeout=5)
        
        if resp.status_code != 200:
            log_test(8, "Update Inventory", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        if not data.get("success"):
            log_test(8, "Update Inventory", False, "Update failed")
            return
        
        if data["quantity"] != 100:
            log_test(8, "Update Inventory", False, f"Wrong quantity: {data['quantity']}")
            return
        
        log_test(8, "Update Inventory", True, f"SKU: {data['sku']}, Qty: {data['quantity']}")
    
    except Exception as e:
        log_test(8, "Update Inventory", False, str(e))

def test_9_list_inventory():
    """Test 9: List Inventory"""
    try:
        resp = requests.get(f"{BASE_URL}/inventory/list", headers=HEADERS, timeout=5)
        
        if resp.status_code != 200:
            log_test(9, "List Inventory", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        if not isinstance(data, list):
            log_test(9, "List Inventory", False, "Response not a list")
            return
        
        # Should have at least TEST-001
        test_entry = next((i for i in data if i["sku"] == "TEST-001"), None)
        if not test_entry:
            log_test(9, "List Inventory", False, "TEST-001 not found")
            return
        
        log_test(9, "List Inventory", True, f"Total: {len(data)}, TEST-001 qty: {test_entry['quantity']}")
    
    except Exception as e:
        log_test(9, "List Inventory", False, str(e))

def test_10_create_order():
    """Test 10: Create Order"""
    global created_order_ids
    
    try:
        payload = {
            "customer_name": "Test Customer",
            "customer_email": "test@example.com",
            "items": [
                {"sku": "TEST-001", "quantity": 2}
            ],
            "currency": "EUR",
            "shipping_address": "Test Street 123, 12345 Test City"
        }
        
        resp = requests.post(f"{BASE_URL}/orders/create", headers=HEADERS, json=payload, timeout=5)
        
        if resp.status_code != 200:
            log_test(10, "Create Order", False, f"Status {resp.status_code}: {resp.text}")
            return
        
        data = resp.json()
        
        if "order_id" not in data:
            log_test(10, "Create Order", False, "Missing order_id")
            return
        
        created_order_ids.append(data["order_id"])
        
        # Total should be 2 * 39.99 = 79.98
        expected_total = 79.98
        if abs(data["total"] - expected_total) > 0.01:
            log_test(10, "Create Order", False, f"Wrong total: {data['total']} (expected {expected_total})")
            return
        
        log_test(10, "Create Order", True, f"Order ID: {data['order_id']}, Total: {data['total']} EUR")
    
    except Exception as e:
        log_test(10, "Create Order", False, str(e))

def test_11_list_orders():
    """Test 11: List Orders"""
    try:
        payload = {
            "max_results": 50
        }
        
        resp = requests.post(f"{BASE_URL}/orders/list", headers=HEADERS, json=payload, timeout=5)
        
        if resp.status_code != 200:
            log_test(11, "List Orders", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        if not isinstance(data, list):
            log_test(11, "List Orders", False, "Response not a list")
            return
        
        # Should have at least the order we created
        if len(data) == 0:
            log_test(11, "List Orders", False, "No orders found")
            return
        
        log_test(11, "List Orders", True, f"Total: {len(data)}")
    
    except Exception as e:
        log_test(11, "List Orders", False, str(e))

def test_12_command_endpoint():
    """Test 12: Command Endpoint (create_product)"""
    global created_product_ids
    
    try:
        payload = {
            "action": "create_product",
            "params": {
                "title": "Command Test Product",
                "sku": "CMD-TEST-001",
                "price": 19.99,
                "currency": "EUR",
                "status": "active"
            }
        }
        
        resp = requests.post(f"{BASE_URL}/command", headers=HEADERS, json=payload, timeout=5)
        
        if resp.status_code != 200:
            log_test(12, "Command Endpoint", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        if data.get("action") != "create_product":
            log_test(12, "Command Endpoint", False, f"Wrong action: {data.get('action')}")
            return
        
        if not data.get("success"):
            log_test(12, "Command Endpoint", False, "Command failed")
            return
        
        result = data.get("result", {})
        if "product_id" not in result:
            log_test(12, "Command Endpoint", False, "Missing product_id")
            return
        
        created_product_ids.append(result["product_id"])
        
        log_test(12, "Command Endpoint", True, f"Action: {data['action']}, Product: {result['sku']}")
    
    except Exception as e:
        log_test(12, "Command Endpoint", False, str(e))

def test_13_delete_product():
    """Test 13: Delete Product"""
    global created_product_ids
    
    if len(created_product_ids) < 2:
        log_test(13, "Delete Product", False, "Not enough products to delete")
        return
    
    try:
        # Delete the second created product (from command endpoint)
        product_id = created_product_ids[1]
        
        resp = requests.delete(
            f"{BASE_URL}/products/delete",
            headers=HEADERS,
            params={"product_id": product_id},
            timeout=5
        )
        
        if resp.status_code != 200:
            log_test(13, "Delete Product", False, f"Status {resp.status_code}")
            return
        
        data = resp.json()
        
        if not data.get("success"):
            log_test(13, "Delete Product", False, "Delete failed")
            return
        
        # Verify product is gone
        list_payload = {"max_results": 500}
        list_resp = requests.post(f"{BASE_URL}/products/list", headers=HEADERS, json=list_payload, timeout=5)
        products = list_resp.json()
        
        if any(p["product_id"] == product_id for p in products):
            log_test(13, "Delete Product", False, "Product still exists")
            return
        
        log_test(13, "Delete Product", True, f"Deleted: {product_id}")
    
    except Exception as e:
        log_test(13, "Delete Product", False, str(e))

def test_14_strict_json():
    """Test 14: Strict JSON validation"""
    try:
        # Send request with unknown field
        payload = {
            "title": "Test",
            "sku": "TEST-STRICT",
            "price": 10.0,
            "unknown_field": "should_be_rejected"
        }
        
        resp = requests.post(f"{BASE_URL}/products/create", headers=HEADERS, json=payload, timeout=5)
        
        # Should return 422 (Validation Error)
        if resp.status_code == 422:
            log_test(14, "Strict JSON", True, "Unknown fields rejected (422)")
            return
        
        # If 200, check if field was silently ignored (bad)
        if resp.status_code == 200:
            log_test(14, "Strict JSON", False, "Unknown field accepted (should reject)")
            return
        
        log_test(14, "Strict JSON", False, f"Unexpected status: {resp.status_code}")
    
    except Exception as e:
        log_test(14, "Strict JSON", False, str(e))

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def main():
    print("=" * 70)
    print("  opena16 - Shop Management Agent Integration Tests")
    print("  Port: 12361")
    print("=" * 70)
    print("")
    
    # Wait for service to be ready
    print("Warte auf Service-Initialisierung...")
    time.sleep(2)
    
    # Run all tests
    test_1_health()
    test_2_root()
    test_3_create_product()
    test_4_list_products()
    test_5_update_product()
    test_6_create_category()
    test_7_list_categories()
    test_8_update_inventory()
    test_9_list_inventory()
    test_10_create_order()
    test_11_list_orders()
    test_12_command_endpoint()
    test_13_delete_product()
    test_14_strict_json()
    
    # Summary
    print("")
    print("=" * 70)
    print(f"Total: {total_tests}, Passed: {passed_tests}, Failed: {failed_tests}, Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if failed_tests == 0:
        print("\033[0;32m✅ ALL TESTS PASSED\033[0m")
        sys.exit(0)
    else:
        print(f"\033[0;31m❌ {failed_tests} TEST(S) FAILED\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
