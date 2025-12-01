#!/usr/bin/env python3
"""
Test Suite for opena19 - Stocks & Crypto Agent
Port: 12364

Tests:
1. Health check
2. Root endpoint
3. Get stock prices (AAPL, TSLA)
4. Get crypto prices (bitcoin, ethereum)
5. Add portfolio position (stock)
6. Add portfolio position (crypto)
7. Get portfolio overview
8. Create price alert (stock above threshold)
9. Create price alert (crypto below threshold)
10. List active alerts
11. Delete alert
12. Command endpoint (get_prices)
13. Command endpoint (add_position)
14. Command endpoint (get_portfolio)
15. Strict JSON validation (unknown fields rejected)
"""

import sys
import json
import time
import requests
from typing import Dict, Any

# ========== CONFIG ==========
BASE_URL = "http://127.0.0.1:12364"
BEARER_TOKEN = "c899b90d-faf8-485b-afa4-078357cf5313"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# ========== TEST STATE ==========
created_alert_ids = []

# ========== HELPERS ==========
def test_request(method: str, endpoint: str, data: Dict[str, Any] = None, params: Dict[str, Any] = None, expect_auth: bool = True) -> requests.Response:
    """Make HTTP request"""
    url = f"{BASE_URL}{endpoint}"
    headers = HEADERS if expect_auth else {}
    
    if method == "GET":
        return requests.get(url, headers=headers, params=params, timeout=10)
    elif method == "POST":
        return requests.post(url, headers=headers, json=data, timeout=10)
    elif method == "DELETE":
        return requests.delete(url, headers=headers, timeout=10)
    else:
        raise ValueError(f"Unsupported method: {method}")

def print_test(test_num: int, test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    
    print(f"{color}[{status}]{reset} Test {test_num} ({test_name}): {'PASS' if passed else 'FAIL'}{' - ' + details if details else ''}")
    
    return passed

# ========== TESTS ==========
def test_01_health():
    """Test 1: Health check"""
    try:
        response = test_request("GET", "/health", expect_auth=False)
        
        if response.status_code != 200:
            return print_test(1, "Health", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if data.get("status") != "ok" or data.get("service") != "opena19":
            return print_test(1, "Health", False, f"Invalid response: {data}")
        
        uptime = data.get("uptime_seconds", 0)
        positions = data.get("total_positions", 0)
        alerts = data.get("total_alerts", 0)
        
        return print_test(1, "Health", True, f"Uptime: {uptime:.2f}s, Positions: {positions}, Alerts: {alerts}")
    
    except Exception as e:
        return print_test(1, "Health", False, str(e))

def test_02_root():
    """Test 2: Root endpoint"""
    try:
        response = test_request("GET", "/", expect_auth=False)
        
        if response.status_code != 200:
            return print_test(2, "Root", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if data.get("agent") != "opena19":
            return print_test(2, "Root", False, f"Invalid agent: {data.get('agent')}")
        
        return print_test(2, "Root", True)
    
    except Exception as e:
        return print_test(2, "Root", False, str(e))

def test_03_get_stock_prices():
    """Test 3: Get stock prices (AAPL, TSLA)"""
    try:
        # Note: Demo API key may return mock data
        response = test_request("GET", "/prices", params={"symbols": "AAPL,TSLA", "market": "stock"})
        
        if response.status_code != 200:
            return print_test(3, "Get Stock Prices", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if "prices" not in data or "market" not in data:
            return print_test(3, "Get Stock Prices", False, f"Missing fields: {data}")
        
        if data["market"] != "stock":
            return print_test(3, "Get Stock Prices", False, f"Invalid market: {data['market']}")
        
        prices = data["prices"]
        
        # Check for AAPL and TSLA keys
        if "AAPL" not in prices or "TSLA" not in prices:
            return print_test(3, "Get Stock Prices", False, f"Missing symbols: {prices.keys()}")
        
        return print_test(3, "Get Stock Prices", True, f"AAPL: ${prices.get('AAPL')}, TSLA: ${prices.get('TSLA')}")
    
    except Exception as e:
        return print_test(3, "Get Stock Prices", False, str(e))

def test_04_get_crypto_prices():
    """Test 4: Get crypto prices (bitcoin, ethereum)"""
    try:
        response = test_request("GET", "/prices", params={"symbols": "bitcoin,ethereum", "market": "crypto"})
        
        if response.status_code != 200:
            return print_test(4, "Get Crypto Prices", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if data["market"] != "crypto":
            return print_test(4, "Get Crypto Prices", False, f"Invalid market: {data['market']}")
        
        prices = data["prices"]
        
        if "bitcoin" not in prices or "ethereum" not in prices:
            return print_test(4, "Get Crypto Prices", False, f"Missing symbols: {prices.keys()}")
        
        return print_test(4, "Get Crypto Prices", True, f"BTC: ${prices.get('bitcoin')}, ETH: ${prices.get('ethereum')}")
    
    except Exception as e:
        return print_test(4, "Get Crypto Prices", False, str(e))

def test_05_add_portfolio_stock():
    """Test 5: Add portfolio position (stock)"""
    try:
        payload = {
            "symbol": "AAPL",
            "market": "stock",
            "quantity": 10.0,
            "avg_price": 150.0
        }
        
        response = test_request("POST", "/portfolio", data=payload)
        
        if response.status_code != 200:
            return print_test(5, "Add Portfolio Stock", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if not data.get("success"):
            return print_test(5, "Add Portfolio Stock", False, f"Success=False: {data}")
        
        position = data.get("position", {})
        
        if position.get("symbol") != "AAPL" or position.get("quantity") != 10.0:
            return print_test(5, "Add Portfolio Stock", False, f"Invalid position: {position}")
        
        return print_test(5, "Add Portfolio Stock", True, f"Symbol: {position['symbol']}, Qty: {position['quantity']}, Avg: ${position['avg_price']}")
    
    except Exception as e:
        return print_test(5, "Add Portfolio Stock", False, str(e))

def test_06_add_portfolio_crypto():
    """Test 6: Add portfolio position (crypto)"""
    try:
        payload = {
            "symbol": "bitcoin",
            "market": "crypto",
            "quantity": 0.5,
            "avg_price": 40000.0
        }
        
        response = test_request("POST", "/portfolio", data=payload)
        
        if response.status_code != 200:
            return print_test(6, "Add Portfolio Crypto", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if not data.get("success"):
            return print_test(6, "Add Portfolio Crypto", False, f"Success=False")
        
        position = data.get("position", {})
        
        if position.get("symbol") != "bitcoin":
            return print_test(6, "Add Portfolio Crypto", False, f"Invalid symbol: {position.get('symbol')}")
        
        return print_test(6, "Add Portfolio Crypto", True, f"Symbol: {position['symbol']}, Qty: {position['quantity']}")
    
    except Exception as e:
        return print_test(6, "Add Portfolio Crypto", False, str(e))

def test_07_get_portfolio():
    """Test 7: Get portfolio overview"""
    try:
        response = test_request("GET", "/portfolio")
        
        if response.status_code != 200:
            return print_test(7, "Get Portfolio", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if "positions" not in data or "total_value" not in data:
            return print_test(7, "Get Portfolio", False, f"Missing fields: {data.keys()}")
        
        positions = data["positions"]
        total_value = data["total_value"]
        total_pnl = data["total_pnl"]
        
        return print_test(7, "Get Portfolio", True, f"Positions: {len(positions)}, Value: ${total_value:.2f}, PnL: ${total_pnl:.2f}")
    
    except Exception as e:
        return print_test(7, "Get Portfolio", False, str(e))

def test_08_create_alert_stock():
    """Test 8: Create price alert (stock above threshold)"""
    try:
        payload = {
            "symbol": "AAPL",
            "market": "stock",
            "condition": "above",
            "threshold": 200.0,
            "notification": "Email"
        }
        
        response = test_request("POST", "/alerts", data=payload)
        
        if response.status_code != 200:
            return print_test(8, "Create Alert Stock", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if not data.get("success"):
            return print_test(8, "Create Alert Stock", False, f"Success=False")
        
        alert = data.get("alert", {})
        alert_id = alert.get("id")
        
        if not alert_id:
            return print_test(8, "Create Alert Stock", False, "No alert ID returned")
        
        created_alert_ids.append(alert_id)
        
        return print_test(8, "Create Alert Stock", True, f"Alert ID: {alert_id}, Threshold: ${alert['threshold']}")
    
    except Exception as e:
        return print_test(8, "Create Alert Stock", False, str(e))

def test_09_create_alert_crypto():
    """Test 9: Create price alert (crypto below threshold)"""
    try:
        payload = {
            "symbol": "bitcoin",
            "market": "crypto",
            "condition": "below",
            "threshold": 30000.0,
            "notification": "SMS"
        }
        
        response = test_request("POST", "/alerts", data=payload)
        
        if response.status_code != 200:
            return print_test(9, "Create Alert Crypto", False, f"Status {response.status_code}")
        
        data = response.json()
        alert = data.get("alert", {})
        alert_id = alert.get("id")
        
        created_alert_ids.append(alert_id)
        
        return print_test(9, "Create Alert Crypto", True, f"Alert ID: {alert_id}, Condition: {alert['condition']}")
    
    except Exception as e:
        return print_test(9, "Create Alert Crypto", False, str(e))

def test_10_list_alerts():
    """Test 10: List active alerts"""
    try:
        response = test_request("GET", "/alerts", params={"active_only": True})
        
        if response.status_code != 200:
            return print_test(10, "List Alerts", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if "total" not in data or "alerts" not in data:
            return print_test(10, "List Alerts", False, f"Missing fields: {data.keys()}")
        
        total = data["total"]
        alerts = data["alerts"]
        
        return print_test(10, "List Alerts", True, f"Total: {total}, Active: {len(alerts)}")
    
    except Exception as e:
        return print_test(10, "List Alerts", False, str(e))

def test_11_delete_alert():
    """Test 11: Delete alert"""
    try:
        if not created_alert_ids:
            return print_test(11, "Delete Alert", False, "No alerts to delete")
        
        alert_id = created_alert_ids[0]
        
        response = test_request("DELETE", f"/alerts/{alert_id}")
        
        if response.status_code != 200:
            return print_test(11, "Delete Alert", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if not data.get("success"):
            return print_test(11, "Delete Alert", False, f"Success=False")
        
        return print_test(11, "Delete Alert", True, f"Deleted: {alert_id}")
    
    except Exception as e:
        return print_test(11, "Delete Alert", False, str(e))

def test_12_command_get_prices():
    """Test 12: Command endpoint (get_prices)"""
    try:
        payload = {
            "action": "get_prices",
            "params": {
                "symbols": ["AAPL", "MSFT"],
                "market": "stock"
            }
        }
        
        response = test_request("POST", "/command", data=payload)
        
        if response.status_code != 200:
            return print_test(12, "Command get_prices", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if not data.get("success") or data.get("action") != "get_prices":
            return print_test(12, "Command get_prices", False, f"Invalid response: {data}")
        
        result = data.get("result", {})
        prices = result.get("prices", {})
        
        return print_test(12, "Command get_prices", True, f"Prices: {list(prices.keys())}")
    
    except Exception as e:
        return print_test(12, "Command get_prices", False, str(e))

def test_13_command_add_position():
    """Test 13: Command endpoint (add_position)"""
    try:
        payload = {
            "action": "add_position",
            "params": {
                "symbol": "TSLA",
                "market": "stock",
                "quantity": 5.0,
                "avg_price": 250.0
            }
        }
        
        response = test_request("POST", "/command", data=payload)
        
        if response.status_code != 200:
            return print_test(13, "Command add_position", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if not data.get("success"):
            return print_test(13, "Command add_position", False, f"Success=False")
        
        result = data.get("result", {})
        position = result.get("position", {})
        
        return print_test(13, "Command add_position", True, f"Symbol: {position.get('symbol')}, Qty: {position.get('quantity')}")
    
    except Exception as e:
        return print_test(13, "Command add_position", False, str(e))

def test_14_command_get_portfolio():
    """Test 14: Command endpoint (get_portfolio)"""
    try:
        payload = {
            "action": "get_portfolio",
            "params": {}
        }
        
        response = test_request("POST", "/command", data=payload)
        
        if response.status_code != 200:
            return print_test(14, "Command get_portfolio", False, f"Status {response.status_code}")
        
        data = response.json()
        
        if not data.get("success"):
            return print_test(14, "Command get_portfolio", False, f"Success=False")
        
        result = data.get("result", {})
        positions = result.get("positions", [])
        
        return print_test(14, "Command get_portfolio", True, f"Positions: {len(positions)}")
    
    except Exception as e:
        return print_test(14, "Command get_portfolio", False, str(e))

def test_15_strict_json():
    """Test 15: Strict JSON validation (unknown fields rejected)"""
    try:
        payload = {
            "symbol": "AAPL",
            "market": "stock",
            "quantity": 1.0,
            "avg_price": 100.0,
            "unknown_field": "should_fail"  # Extra field
        }
        
        response = test_request("POST", "/portfolio", data=payload)
        
        # Should return 422 (Validation Error)
        if response.status_code == 422:
            return print_test(15, "Strict JSON", True, "Unknown fields rejected (422)")
        
        return print_test(15, "Strict JSON", False, f"Expected 422, got {response.status_code}")
    
    except Exception as e:
        return print_test(15, "Strict JSON", False, str(e))

# ========== MAIN ==========
def main():
    print("=" * 60)
    print("  Test Suite: opena19 (Stocks & Crypto Agent)")
    print("  Port: 12364")
    print("=" * 60)
    print()
    
    # Wait for service
    print("Waiting for service to be ready...")
    time.sleep(2)
    
    results = []
    
    # Run tests
    results.append(test_01_health())
    results.append(test_02_root())
    results.append(test_03_get_stock_prices())
    results.append(test_04_get_crypto_prices())
    results.append(test_05_add_portfolio_stock())
    results.append(test_06_add_portfolio_crypto())
    results.append(test_07_get_portfolio())
    results.append(test_08_create_alert_stock())
    results.append(test_09_create_alert_crypto())
    results.append(test_10_list_alerts())
    results.append(test_11_delete_alert())
    results.append(test_12_command_get_prices())
    results.append(test_13_command_add_position())
    results.append(test_14_command_get_portfolio())
    results.append(test_15_strict_json())
    
    # Summary
    print()
    print("=" * 60)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"Total: {total}, Passed: {passed}, Failed: {failed}, Rate: {pass_rate:.1f}%")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ {failed} TEST(S) FAILED")
    
    print("=" * 60)
    
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
