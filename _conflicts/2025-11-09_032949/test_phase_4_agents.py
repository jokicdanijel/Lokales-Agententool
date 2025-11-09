"""
Integration tests for Phase 4 Agents (11-15)
Social Media, Influencer, Calendar, HTML, Shop
"""

import json
import urllib.request
from datetime import datetime, timedelta
import sys

# Test configuration
TOKEN = "MEIN_SUPER_TOKEN_123"
SERVICES = {
    "opena11": "http://127.0.0.1:12359",
    "opena12": "http://127.0.0.1:12360",
    "opena13": "http://127.0.0.1:12361",
    "opena14": "http://127.0.0.1:12362",
    "opena15": "http://127.0.0.1:12363",
}

FAILED_TESTS = []
PASSED_TESTS = []


def _post(service: str, path: str, payload: dict = None, expect_error: bool = False) -> dict:
    """POST request helper"""
    url = SERVICES[service] + path
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload or {}).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        if expect_error:
            return {"error": e.code}
        raise
    except Exception as e:
        print(f"❌ Request failed: {e}")
        raise


def _get(service: str, path: str) -> dict:
    """GET request helper"""
    url = SERVICES[service] + path
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    req = urllib.request.Request(url, headers=headers, method="GET")
    
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"❌ Request failed: {e}")
        raise


def _test(name: str, func):
    """Test wrapper"""
    try:
        func()
        PASSED_TESTS.append(name)
        print(f"✅ {name}")
    except AssertionError as e:
        FAILED_TESTS.append((name, str(e)))
        print(f"❌ {name}: {e}")
    except Exception as e:
        FAILED_TESTS.append((name, str(e)))
        print(f"❌ {name}: {e}")


# ============================================================================
# PHASE 4 - AGENT 11 (SOCIAL MEDIA) TESTS
# ============================================================================

def test_opena11_health():
    """Agent 11 health check"""
    resp = _get("opena11", "/health")
    assert resp.get("status") == "healthy", f"Expected healthy, got {resp}"
    assert resp.get("port") == 12359, "Wrong port"


def test_opena11_post_create():
    """Agent 11: Create social post"""
    resp = _post("opena11", "/post/create", {
        "content": "Hello World! 🚀",
        "platform": "twitter"
    })
    assert resp.get("strict") is True
    assert resp.get("published") is True
    assert "post_id" in resp
    assert resp.get("platform") == "twitter"


def test_opena11_post_schedule():
    """Agent 11: Schedule social post"""
    future_time = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
    resp = _post("opena11", "/post/schedule", {
        "content": "Scheduled post 📅",
        "platform": "facebook",
        "scheduled_time": future_time
    })
    assert resp.get("scheduled") is True
    assert "post_id" in resp


def test_opena11_trending():
    """Agent 11: Get trending topics"""
    resp = _get("opena11", "/trending")
    assert resp.get("strict") is True
    assert "trending" in resp
    assert len(resp.get("trending", [])) > 0


def test_opena11_status():
    """Agent 11: Get agent status"""
    resp = _get("opena11", "/status")
    assert resp.get("service") == "opena11_SocialMedia"
    assert resp.get("port") == 12359
    assert resp.get("endpoints") == 6


# ============================================================================
# PHASE 4 - AGENT 12 (INFLUENCER) TESTS
# ============================================================================

def test_opena12_health():
    """Agent 12 health check"""
    resp = _get("opena12", "/health")
    assert resp.get("status") == "healthy"
    assert resp.get("port") == 12360


def test_opena12_list_influencers():
    """Agent 12: List influencers"""
    resp = _get("opena12", "/influencers/list")
    assert resp.get("strict") is True
    assert "influencers" in resp
    assert resp.get("count") >= 0


def test_opena12_campaign_create():
    """Agent 12: Create campaign"""
    resp = _post("opena12", "/campaign/create", {
        "name": "Summer Campaign",
        "influencer_ids": ["INF_TEST001"],
        "budget": 5000.0,
        "duration_days": 30,
        "target_audience": "18-35"
    })
    assert resp.get("strict") is True
    assert resp.get("created") is True
    assert "campaign_id" in resp


def test_opena12_roi_calculate():
    """Agent 12: Calculate ROI"""
    # Create campaign first
    camp_resp = _post("opena12", "/campaign/create", {
        "name": "Test Campaign",
        "influencer_ids": ["INF_TEST001"],
        "budget": 1000.0,
        "duration_days": 10,
        "target_audience": "25-40"
    })
    campaign_id = camp_resp["campaign_id"]
    
    # Calculate ROI
    resp = _post("opena12", "/roi/calculate", {
        "campaign_id": campaign_id
    })
    assert resp.get("strict") is True
    assert "roi" in resp


def test_opena12_status():
    """Agent 12: Get agent status"""
    resp = _get("opena12", "/status")
    assert resp.get("service") == "opena12_Influencer"
    assert resp.get("port") == 12360
    assert resp.get("endpoints") == 6


# ============================================================================
# PHASE 4 - AGENT 13 (CALENDAR) TESTS
# ============================================================================

def test_opena13_health():
    """Agent 13 health check"""
    resp = _get("opena13", "/health")
    assert resp.get("status") == "healthy"
    assert resp.get("port") == 12361


def test_opena13_event_create():
    """Agent 13: Create calendar event"""
    now = datetime.utcnow()
    start = (now + timedelta(hours=1)).isoformat() + "Z"
    end = (now + timedelta(hours=2)).isoformat() + "Z"
    
    resp = _post("opena13", "/event/create", {
        "title": "Team Meeting",
        "description": "Weekly sync",
        "start_time": start,
        "end_time": end,
        "calendar": "default",
        "attendees": ["john@example.com", "jane@example.com"]
    })
    assert resp.get("strict") is True
    assert "event_id" in resp


def test_opena13_event_list():
    """Agent 13: List calendar events"""
    resp = _post("opena13", "/event/list", {
        "calendar": "default"
    })
    assert resp.get("strict") is True
    assert "events" in resp


def test_opena13_availability_check():
    """Agent 13: Check availability"""
    now = datetime.utcnow()
    start = (now + timedelta(days=1)).isoformat() + "Z"
    
    resp = _post("opena13", "/availability/check", {
        "start_time": start,
        "duration_minutes": 60,
        "calendar": "default"
    })
    assert resp.get("strict") is True
    assert "availability" in resp


def test_opena13_status():
    """Agent 13: Get agent status"""
    resp = _get("opena13", "/status")
    assert resp.get("service") == "opena13_Calendar"
    assert resp.get("port") == 12361
    assert resp.get("endpoints") == 6


# ============================================================================
# PHASE 4 - AGENT 14 (HTML) TESTS
# ============================================================================

def test_opena14_health():
    """Agent 14 health check"""
    resp = _get("opena14", "/health")
    assert resp.get("status") == "healthy"
    assert resp.get("port") == 12362


def test_opena14_template_render():
    """Agent 14: Render template"""
    resp = _post("opena14", "/template/render", {
        "template_name": "landing",
        "variables": {
            "title": "My Website",
            "description": "Welcome to my site",
            "date": "2025-11-09"
        }
    })
    assert resp.get("strict") is True
    assert "page_id" in resp
    assert "html" in resp


def test_opena14_page_generate():
    """Agent 14: Generate HTML page"""
    resp = _post("opena14", "/page/generate", {
        "title": "Test Page",
        "content": "This is test content",
        "sections": {
            "introduction": "Welcome",
            "details": "More information here"
        }
    })
    assert resp.get("strict") is True
    assert "page_id" in resp


def test_opena14_export_html():
    """Agent 14: Export HTML"""
    # Generate page first
    gen_resp = _post("opena14", "/page/generate", {
        "title": "Export Test",
        "content": "Test content"
    })
    page_id = gen_resp["page_id"]
    
    # Export
    resp = _post("opena14", "/export/html", {
        "page_id": page_id,
        "format": "html"
    })
    assert resp.get("strict") is True
    assert "export" in resp


def test_opena14_status():
    """Agent 14: Get agent status"""
    resp = _get("opena14", "/status")
    assert resp.get("service") == "opena14_HTML"
    assert resp.get("port") == 12362
    assert resp.get("endpoints") == 6


# ============================================================================
# PHASE 4 - AGENT 15 (SHOP) TESTS
# ============================================================================

def test_opena15_health():
    """Agent 15 health check"""
    resp = _get("opena15", "/health")
    assert resp.get("status") == "healthy"
    assert resp.get("port") == 12363


def test_opena15_product_list():
    """Agent 15: List products"""
    resp = _get("opena15", "/product/list")
    assert resp.get("strict") is True
    assert "products" in resp


def test_opena15_order_create():
    """Agent 15: Create order"""
    # Get products first
    prod_resp = _get("opena15", "/product/list")
    products = prod_resp.get("products", [])
    
    if len(products) > 0:
        product_id = products[0]["id"]
        
        resp = _post("opena15", "/order/create", {
            "customer_name": "John Doe",
            "items": [{"product_id": product_id, "quantity": 2}],
            "shipping_address": "123 Main St, City, State"
        })
        assert resp.get("strict") is True
        assert "order_id" in resp


def test_opena15_inventory_update():
    """Agent 15: Update inventory"""
    # Get products first
    prod_resp = _get("opena15", "/product/list")
    products = prod_resp.get("products", [])
    
    if len(products) > 0:
        product_id = products[0]["id"]
        
        resp = _post("opena15", "/inventory/update", {
            "product_id": product_id,
            "quantity_change": 5,
            "reason": "stock_addition"
        })
        assert resp.get("strict") is True


def test_opena15_pricing_calculate():
    """Agent 15: Calculate pricing"""
    prod_resp = _get("opena15", "/product/list")
    products = prod_resp.get("products", [])
    
    if len(products) > 0:
        product_id = products[0]["id"]
        
        resp = _post("opena15", "/pricing/calculate", {
            "items": [{"product_id": product_id, "quantity": 1}],
            "discount_code": "SAVE10"
        })
        assert resp.get("strict") is True
        assert "pricing" in resp


def test_opena15_status():
    """Agent 15: Get agent status"""
    resp = _get("opena15", "/status")
    assert resp.get("service") == "opena15_Shop"
    assert resp.get("port") == 12363
    assert resp.get("endpoints") == 6


# ============================================================================
# RUN TESTS
# ============================================================================

def main():
    """Run all tests"""
    print("=" * 70)
    print("PHASE 4 AGENT TESTS (11-15)")
    print("=" * 70)
    print()
    
    # Test Agent 11
    print("🧪 Testing Agent 11 (Social Media)...")
    _test("opena11_health", test_opena11_health)
    _test("opena11_post_create", test_opena11_post_create)
    _test("opena11_post_schedule", test_opena11_post_schedule)
    _test("opena11_trending", test_opena11_trending)
    _test("opena11_status", test_opena11_status)
    print()
    
    # Test Agent 12
    print("🧪 Testing Agent 12 (Influencer)...")
    _test("opena12_health", test_opena12_health)
    _test("opena12_list_influencers", test_opena12_list_influencers)
    _test("opena12_campaign_create", test_opena12_campaign_create)
    _test("opena12_roi_calculate", test_opena12_roi_calculate)
    _test("opena12_status", test_opena12_status)
    print()
    
    # Test Agent 13
    print("🧪 Testing Agent 13 (Calendar)...")
    _test("opena13_health", test_opena13_health)
    _test("opena13_event_create", test_opena13_event_create)
    _test("opena13_event_list", test_opena13_event_list)
    _test("opena13_availability_check", test_opena13_availability_check)
    _test("opena13_status", test_opena13_status)
    print()
    
    # Test Agent 14
    print("🧪 Testing Agent 14 (HTML)...")
    _test("opena14_health", test_opena14_health)
    _test("opena14_template_render", test_opena14_template_render)
    _test("opena14_page_generate", test_opena14_page_generate)
    _test("opena14_export_html", test_opena14_export_html)
    _test("opena14_status", test_opena14_status)
    print()
    
    # Test Agent 15
    print("🧪 Testing Agent 15 (Shop)...")
    _test("opena15_health", test_opena15_health)
    _test("opena15_product_list", test_opena15_product_list)
    _test("opena15_order_create", test_opena15_order_create)
    _test("opena15_inventory_update", test_opena15_inventory_update)
    _test("opena15_pricing_calculate", test_opena15_pricing_calculate)
    _test("opena15_status", test_opena15_status)
    print()
    
    # Summary
    print("=" * 70)
    print(f"RESULTS: {len(PASSED_TESTS)} PASSED, {len(FAILED_TESTS)} FAILED")
    print("=" * 70)
    
    if FAILED_TESTS:
        print("\n❌ FAILED TESTS:")
        for test_name, error in FAILED_TESTS:
            print(f"  • {test_name}: {error}")
        sys.exit(1)
    else:
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main()
