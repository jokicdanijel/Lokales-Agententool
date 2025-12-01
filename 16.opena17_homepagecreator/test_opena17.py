#!/usr/bin/env python3
"""
Integration Tests für opena17 - Homepage Creator Agent
Port: 12362

Test-Coverage:
1. Health Check
2. Root Endpoint
3. Site generieren (STATIC)
4. Site exportieren (ZIP)
5. Site deployen (LOCAL)
6. Site-Struktur abrufen
7. Preview-Zugriff (ohne Auth)
8. Command Endpoint (generate_site)
9. Multi-Page Site generieren
10. Navigation generieren
11. Custom CSS/JS injection
12. Strict JSON Validation
"""

import requests
import json
import time
from typing import Dict, Any, List

BASE_URL = "http://127.0.0.1:12362"
BEARER_TOKEN = "c899b90d-faf8-485b-afa4-078357cf5313"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# Track für Cleanup
created_site_ids: List[str] = []


def test_health() -> None:
    """Test 1: Health Check"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "opena17"
    assert data["port"] == 12362
    assert data["kuerzel"] == "hpcreatep"
    assert "uptime_seconds" in data
    assert "total_sites" in data
    
    print(f"[✓] Test 1 (Health): PASS - Uptime: {data['uptime_seconds']:.2f}s, Sites: {data['total_sites']}")


def test_root() -> None:
    """Test 2: Root Endpoint"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["service"] == "opena17"
    assert data["kuerzel"] == "hpcreatep"
    assert "endpoints" in data
    
    print(f"[✓] Test 2 (Root): PASS")


def test_generate_site() -> Dict[str, Any]:
    """Test 3: Site generieren (STATIC, Single Page)"""
    payload = {
        "generator": "static",
        "template": "default",
        "pages": [
            {
                "slug": "home",
                "title": "Welcome Home",
                "content": "<p>This is the homepage content.</p>",
                "meta_description": "Test homepage",
                "meta_keywords": ["test", "homepage"],
                "is_homepage": True
            }
        ],
        "navigation": [],
        "navigation_type": "top",
        "branding": {
            "site_name": "Test Site",
            "tagline": "A test website",
            "color_primary": "#007bff",
            "color_secondary": "#6c757d"
        }
    }
    
    response = requests.post(f"{BASE_URL}/site/generate", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Generate failed: {response.text}"
    
    data = response.json()
    assert "site_id" in data
    assert data["generator"] == "static"
    assert data["pages_generated"] == 1
    assert "output_path" in data
    assert "preview_url" in data
    
    site_id = data["site_id"]
    created_site_ids.append(site_id)
    
    print(f"[✓] Test 3 (Generate Site): PASS - Site ID: {site_id}, Pages: {data['pages_generated']}")
    return data


def test_export_site(site_id: str) -> None:
    """Test 4: Site exportieren (ZIP)"""
    payload = {
        "site_id": site_id,
        "format": "zip",
        "include_assets": True
    }
    
    response = requests.post(f"{BASE_URL}/site/export", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Export failed: {response.text}"
    
    data = response.json()
    assert data["site_id"] == site_id
    assert data["format"] == "zip"
    assert "file_path" in data
    assert data["file_size_bytes"] > 0
    
    print(f"[✓] Test 4 (Export Site): PASS - Format: {data['format']}, Size: {data['file_size_bytes']} bytes")


def test_deploy_site(site_id: str) -> None:
    """Test 5: Site deployen (LOCAL)"""
    payload = {
        "site_id": site_id,
        "target": "local",
        "target_path": "/tmp/test_sites",
        "invalidate_cache": False
    }
    
    response = requests.post(f"{BASE_URL}/site/deploy", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Deploy failed: {response.text}"
    
    data = response.json()
    assert data["site_id"] == site_id
    assert data["target"] == "local"
    assert data["status"] == "deployed"
    assert "deployment_url" in data
    
    print(f"[✓] Test 5 (Deploy Site): PASS - Target: {data['target']}, URL: {data['deployment_url']}")


def test_get_structure(site_id: str) -> None:
    """Test 6: Site-Struktur abrufen"""
    response = requests.get(f"{BASE_URL}/site/structure/{site_id}", headers=HEADERS)
    assert response.status_code == 200, f"Get structure failed: {response.text}"
    
    data = response.json()
    assert data["site_id"] == site_id
    assert "pages" in data
    assert "routes" in data
    assert "assets" in data
    assert "total_size_bytes" in data
    assert len(data["pages"]) > 0
    
    print(f"[✓] Test 6 (Site Structure): PASS - Pages: {len(data['pages'])}, Routes: {len(data['routes'])}, Size: {data['total_size_bytes']} bytes")


def test_preview_access(site_id: str) -> None:
    """Test 7: Preview-Zugriff (ohne Auth)"""
    # Preview-URL ist ohne Bearer Token zugänglich
    response = requests.get(f"{BASE_URL}/preview/{site_id}/index.html")
    assert response.status_code == 200, f"Preview failed: {response.status_code}"
    
    # Sollte HTML sein
    assert response.headers["content-type"].startswith("text/html") or response.headers["content-type"].startswith("application/octet-stream")
    assert len(response.content) > 0
    
    print(f"[✓] Test 7 (Preview Access): PASS - Content-Length: {len(response.content)} bytes")


def test_command_endpoint() -> None:
    """Test 8: Command Endpoint (generate_site via Option-2-Flow)"""
    payload = {
        "action": "generate_site",
        "params": {
            "generator": "static",
            "template": "default",
            "pages": [
                {
                    "slug": "about",
                    "title": "About Us",
                    "content": "<p>About page content.</p>",
                    "is_homepage": True
                }
            ],
            "branding": {
                "site_name": "Command Test Site",
                "tagline": "Generated via command endpoint"
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/command", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Command failed: {response.text}"
    
    data = response.json()
    assert data["status"] == "success"
    assert data["action"] == "generate_site"
    assert "result" in data
    assert "site_id" in data["result"]
    
    site_id = data["result"]["site_id"]
    created_site_ids.append(site_id)
    
    print(f"[✓] Test 8 (Command Endpoint): PASS - Action: {data['action']}, Site ID: {site_id}")


def test_multi_page_site() -> None:
    """Test 9: Multi-Page Site generieren"""
    payload = {
        "generator": "static",
        "template": "default",
        "pages": [
            {
                "slug": "home",
                "title": "Home",
                "content": "<h2>Welcome</h2><p>Homepage content.</p>",
                "is_homepage": True
            },
            {
                "slug": "about",
                "title": "About",
                "content": "<h2>About Us</h2><p>Company information.</p>",
                "is_homepage": False
            },
            {
                "slug": "contact",
                "title": "Contact",
                "content": "<h2>Contact Us</h2><p>Email: test@example.com</p>",
                "is_homepage": False
            }
        ],
        "branding": {
            "site_name": "Multi-Page Test",
            "tagline": "Testing multiple pages"
        }
    }
    
    response = requests.post(f"{BASE_URL}/site/generate", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Multi-page generate failed: {response.text}"
    
    data = response.json()
    assert data["pages_generated"] == 3
    
    site_id = data["site_id"]
    created_site_ids.append(site_id)
    
    print(f"[✓] Test 9 (Multi-Page Site): PASS - Pages: {data['pages_generated']}")


def test_navigation() -> None:
    """Test 10: Navigation generieren"""
    payload = {
        "generator": "static",
        "template": "default",
        "pages": [
            {
                "slug": "home",
                "title": "Home",
                "content": "<p>Home</p>",
                "is_homepage": True
            },
            {
                "slug": "about",
                "title": "About",
                "content": "<p>About</p>",
                "is_homepage": False
            }
        ],
        "navigation": [
            {
                "label": "Home",
                "slug": "home",
                "children": []
            },
            {
                "label": "About",
                "slug": "about",
                "children": []
            }
        ],
        "navigation_type": "top",
        "branding": {
            "site_name": "Nav Test",
            "tagline": "Testing navigation"
        }
    }
    
    response = requests.post(f"{BASE_URL}/site/generate", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Navigation generate failed: {response.text}"
    
    data = response.json()
    assert data["pages_generated"] == 2
    
    site_id = data["site_id"]
    created_site_ids.append(site_id)
    
    # Preview prüfen (sollte Navigation enthalten)
    preview_response = requests.get(f"{BASE_URL}/preview/{site_id}/index.html")
    assert preview_response.status_code == 200
    html_content = preview_response.text
    assert "Home" in html_content
    assert "About" in html_content
    
    print(f"[✓] Test 10 (Navigation): PASS - Navigation items verified in HTML")


def test_custom_css_js() -> None:
    """Test 11: Custom CSS/JS injection"""
    custom_css = "body { background-color: #f0f0f0; }"
    custom_js = "console.log('Custom JS loaded');"
    
    payload = {
        "generator": "static",
        "template": "default",
        "pages": [
            {
                "slug": "home",
                "title": "Custom Styles",
                "content": "<p>Testing custom styles</p>",
                "is_homepage": True
            }
        ],
        "branding": {
            "site_name": "Custom Test"
        },
        "custom_css": custom_css,
        "custom_js": custom_js
    }
    
    response = requests.post(f"{BASE_URL}/site/generate", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Custom CSS/JS failed: {response.text}"
    
    data = response.json()
    site_id = data["site_id"]
    created_site_ids.append(site_id)
    
    # Preview prüfen
    preview_response = requests.get(f"{BASE_URL}/preview/{site_id}/index.html")
    html_content = preview_response.text
    
    assert custom_css in html_content
    assert custom_js in html_content
    
    print(f"[✓] Test 11 (Custom CSS/JS): PASS - Custom styles injected")


def test_strict_json() -> None:
    """Test 12: Strict JSON Validation (extra fields rejected)"""
    payload = {
        "generator": "static",
        "template": "default",
        "pages": [
            {
                "slug": "test",
                "title": "Test",
                "content": "<p>Test</p>",
                "is_homepage": True,
                "unknown_field": "should_fail"  # Extra field
            }
        ],
        "branding": {
            "site_name": "Test"
        }
    }
    
    response = requests.post(f"{BASE_URL}/site/generate", headers=HEADERS, json=payload)
    assert response.status_code == 422, f"Expected 422 for unknown field, got {response.status_code}"
    
    print(f"[✓] Test 12 (Strict JSON): PASS - Unknown fields rejected (422)")


def run_all_tests():
    """Führe alle Tests aus"""
    print("=" * 60)
    print("opena17 - Homepage Creator Agent - Integration Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Generate Site", test_generate_site),
        ("Command Endpoint", test_command_endpoint),
        ("Multi-Page Site", test_multi_page_site),
        ("Navigation", test_navigation),
        ("Custom CSS/JS", test_custom_css_js),
        ("Strict JSON", test_strict_json),
    ]
    
    # Site-abhängige Tests
    site_data = None
    
    passed = 0
    failed = 0
    
    try:
        for test_name, test_func in tests:
            try:
                if test_func == test_generate_site:
                    site_data = test_func()
                else:
                    test_func()
                passed += 1
            except AssertionError as e:
                print(f"[✗] Test '{test_name}': FAIL - {e}")
                failed += 1
            except Exception as e:
                print(f"[✗] Test '{test_name}': ERROR - {e}")
                failed += 1
        
        # Site-abhängige Tests (nach Generate)
        if site_data:
            site_id = site_data["site_id"]
            
            dependent_tests = [
                ("Export Site", lambda: test_export_site(site_id)),
                ("Deploy Site", lambda: test_deploy_site(site_id)),
                ("Site Structure", lambda: test_get_structure(site_id)),
                ("Preview Access", lambda: test_preview_access(site_id)),
            ]
            
            for test_name, test_func in dependent_tests:
                try:
                    test_func()
                    passed += 1
                except AssertionError as e:
                    print(f"[✗] Test '{test_name}': FAIL - {e}")
                    failed += 1
                except Exception as e:
                    print(f"[✗] Test '{test_name}': ERROR - {e}")
                    failed += 1
        
    finally:
        print()
        print("=" * 60)
        print(f"Total: {passed + failed}, Passed: {passed}, Failed: {failed}, Rate: {passed/(passed+failed)*100:.1f}%")
        print("=" * 60)
        
        if failed == 0:
            print("✅ ALL TESTS PASSED")
            return 0
        else:
            print(f"❌ {failed} TEST(S) FAILED")
            return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    exit(exit_code)
