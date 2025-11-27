#!/usr/bin/env python3
"""
Integration Tests für opena18 - CRM Agent
Port: 12363

Test-Coverage:
1. Health Check
2. Root Endpoint
3. Contact erstellen
4. Contact aktualisieren
5. Contact auflisten
6. Contact löschen
7. Organization erstellen
8. Organization aktualisieren
9. Deal erstellen (mit Contact-Link)
10. Deal aktualisieren (Stage-Change)
11. Activity erstellen (Contact + Deal)
12. Activity auflisten
13. Globale Suche
14. Command Endpoint (create_contact)
15. Strict JSON Validation
"""

import requests
import json
import time
from typing import Dict, Any, List

BASE_URL = "http://127.0.0.1:12363"
BEARER_TOKEN = "c899b90d-faf8-485b-afa4-078357cf5313"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# Track für Cleanup
created_contact_ids: List[str] = []
created_organization_ids: List[str] = []
created_deal_ids: List[str] = []


def test_health() -> None:
    """Test 1: Health Check"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "opena18"
    assert data["port"] == 12363
    assert data["kuerzel"] == "crmp"
    assert "uptime_seconds" in data
    assert "total_contacts" in data
    assert "total_organizations" in data
    assert "total_deals" in data
    assert "total_activities" in data
    
    print(f"[✓] Test 1 (Health): PASS - Uptime: {data['uptime_seconds']:.2f}s, Contacts: {data['total_contacts']}, Orgs: {data['total_organizations']}, Deals: {data['total_deals']}")


def test_root() -> None:
    """Test 2: Root Endpoint"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["service"] == "opena18"
    assert data["kuerzel"] == "crmp"
    assert "endpoints" in data
    
    print(f"[✓] Test 2 (Root): PASS")


def test_create_contact() -> Dict[str, Any]:
    """Test 3: Contact erstellen"""
    payload = {
        "first_name": "Max",
        "last_name": "Mustermann",
        "email": "max.mustermann@example.com",
        "phone": "+49 123 456789",
        "position": "CEO",
        "tags": ["vip", "decision-maker"]
    }
    
    response = requests.post(f"{BASE_URL}/contacts", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Create contact failed: {response.text}"
    
    data = response.json()
    assert "contact_id" in data
    assert data["first_name"] == "Max"
    assert data["last_name"] == "Mustermann"
    assert data["email"] == "max.mustermann@example.com"
    assert data["position"] == "CEO"
    assert "vip" in data["tags"]
    
    contact_id = data["contact_id"]
    created_contact_ids.append(contact_id)
    
    print(f"[✓] Test 3 (Create Contact): PASS - Contact ID: {contact_id}, Email: {data['email']}")
    return data


def test_update_contact(contact_id: str) -> None:
    """Test 4: Contact aktualisieren"""
    payload = {
        "position": "Managing Director",
        "phone": "+49 987 654321"
    }
    
    response = requests.put(f"{BASE_URL}/contacts/{contact_id}", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Update contact failed: {response.text}"
    
    data = response.json()
    assert data["contact_id"] == contact_id
    assert data["position"] == "Managing Director"
    assert data["phone"] == "+49 987 654321"
    
    print(f"[✓] Test 4 (Update Contact): PASS - Position: {data['position']}, Phone: {data['phone']}")


def test_list_contacts() -> None:
    """Test 5: Contacts auflisten"""
    response = requests.get(f"{BASE_URL}/contacts", headers=HEADERS)
    assert response.status_code == 200, f"List contacts failed: {response.text}"
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Search-Test
    response_search = requests.get(f"{BASE_URL}/contacts?search=Max", headers=HEADERS)
    search_data = response_search.json()
    assert len(search_data) > 0
    assert any(c["first_name"] == "Max" for c in search_data)
    
    print(f"[✓] Test 5 (List Contacts): PASS - Total: {len(data)}, Search 'Max': {len(search_data)}")


def test_delete_contact() -> None:
    """Test 6: Contact löschen"""
    # Erstelle temporären Contact
    payload = {
        "first_name": "Delete",
        "last_name": "Test",
        "email": "delete.test@example.com"
    }
    
    create_response = requests.post(f"{BASE_URL}/contacts", headers=HEADERS, json=payload)
    contact_id = create_response.json()["contact_id"]
    
    # Lösche Contact
    delete_response = requests.delete(f"{BASE_URL}/contacts/{contact_id}", headers=HEADERS)
    assert delete_response.status_code == 200, f"Delete contact failed: {delete_response.text}"
    
    delete_data = delete_response.json()
    assert delete_data["status"] == "deleted"
    assert delete_data["contact_id"] == contact_id
    
    # Verifiziere Löschung
    list_response = requests.get(f"{BASE_URL}/contacts", headers=HEADERS)
    contacts = list_response.json()
    assert not any(c["contact_id"] == contact_id for c in contacts)
    
    print(f"[✓] Test 6 (Delete Contact): PASS - Deleted: {contact_id}")


def test_create_organization() -> Dict[str, Any]:
    """Test 7: Organization erstellen"""
    payload = {
        "name": "ACME Corp",
        "industry": "Technology",
        "size": "large",
        "website": "https://acme.example.com",
        "tags": ["tech", "b2b"]
    }
    
    response = requests.post(f"{BASE_URL}/organizations", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Create organization failed: {response.text}"
    
    data = response.json()
    assert "organization_id" in data
    assert data["name"] == "ACME Corp"
    assert data["industry"] == "Technology"
    assert data["size"] == "large"
    
    organization_id = data["organization_id"]
    created_organization_ids.append(organization_id)
    
    print(f"[✓] Test 7 (Create Organization): PASS - Org ID: {organization_id}, Name: {data['name']}")
    return data


def test_update_organization(organization_id: str) -> None:
    """Test 8: Organization aktualisieren"""
    payload = {
        "size": "enterprise",
        "website": "https://www.acme.example.com"
    }
    
    response = requests.put(f"{BASE_URL}/organizations/{organization_id}", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Update organization failed: {response.text}"
    
    data = response.json()
    assert data["organization_id"] == organization_id
    assert data["size"] == "enterprise"
    assert data["website"] == "https://www.acme.example.com"
    
    print(f"[✓] Test 8 (Update Organization): PASS - Size: {data['size']}, Website: {data['website']}")


def test_create_deal(contact_id: str, organization_id: str) -> Dict[str, Any]:
    """Test 9: Deal erstellen (mit Contact + Organization)"""
    payload = {
        "title": "Enterprise License Deal",
        "value": 50000.00,
        "currency": "EUR",
        "stage": "proposal",
        "contact_id": contact_id,
        "organization_id": organization_id,
        "probability": 60,
        "tags": ["enterprise", "license"]
    }
    
    response = requests.post(f"{BASE_URL}/deals", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Create deal failed: {response.text}"
    
    data = response.json()
    assert "deal_id" in data
    assert data["title"] == "Enterprise License Deal"
    assert data["value"] == 50000.00
    assert data["stage"] == "proposal"
    assert data["contact_id"] == contact_id
    assert data["organization_id"] == organization_id
    
    deal_id = data["deal_id"]
    created_deal_ids.append(deal_id)
    
    print(f"[✓] Test 9 (Create Deal): PASS - Deal ID: {deal_id}, Value: {data['value']} {data['currency']}, Stage: {data['stage']}")
    return data


def test_update_deal(deal_id: str) -> None:
    """Test 10: Deal aktualisieren (Stage-Change)"""
    payload = {
        "stage": "negotiation",
        "probability": 75
    }
    
    response = requests.put(f"{BASE_URL}/deals/{deal_id}", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Update deal failed: {response.text}"
    
    data = response.json()
    assert data["deal_id"] == deal_id
    assert data["stage"] == "negotiation"
    assert data["probability"] == 75
    
    print(f"[✓] Test 10 (Update Deal): PASS - New Stage: {data['stage']}, Probability: {data['probability']}%")


def test_create_activity(contact_id: str, deal_id: str) -> None:
    """Test 11: Activity erstellen (Contact + Deal)"""
    payload = {
        "activity_type": "call",
        "subject": "Follow-up call regarding proposal",
        "description": "Discussed pricing and timeline",
        "contact_id": contact_id,
        "deal_id": deal_id,
        "duration_minutes": 30
    }
    
    response = requests.post(f"{BASE_URL}/activities", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Create activity failed: {response.text}"
    
    data = response.json()
    assert "activity_id" in data
    assert data["activity_type"] == "call"
    assert data["subject"] == "Follow-up call regarding proposal"
    assert data["contact_id"] == contact_id
    assert data["deal_id"] == deal_id
    assert data["duration_minutes"] == 30
    
    print(f"[✓] Test 11 (Create Activity): PASS - Activity ID: {data['activity_id']}, Type: {data['activity_type']}, Duration: {data['duration_minutes']}min")


def test_list_activities(contact_id: str) -> None:
    """Test 12: Activities auflisten (für Contact)"""
    response = requests.get(f"{BASE_URL}/activities?contact_id={contact_id}", headers=HEADERS)
    assert response.status_code == 200, f"List activities failed: {response.text}"
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(a["contact_id"] == contact_id for a in data)
    
    print(f"[✓] Test 12 (List Activities): PASS - Total for contact {contact_id}: {len(data)}")


def test_search() -> None:
    """Test 13: Globale Suche"""
    payload = {
        "query": "Max",
        "entity_types": ["contacts", "organizations", "deals"],
        "max_results": 50
    }
    
    response = requests.post(f"{BASE_URL}/search", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Search failed: {response.text}"
    
    data = response.json()
    assert "contacts" in data
    assert "organizations" in data
    assert "deals" in data
    
    # Sollte mindestens 1 Contact finden
    assert len(data["contacts"]) > 0
    
    print(f"[✓] Test 13 (Search): PASS - Contacts: {len(data['contacts'])}, Orgs: {len(data['organizations'])}, Deals: {len(data['deals'])}")


def test_command_endpoint() -> None:
    """Test 14: Command Endpoint (create_contact via Option-2-Flow)"""
    payload = {
        "action": "create_contact",
        "params": {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "position": "CTO"
        }
    }
    
    response = requests.post(f"{BASE_URL}/command", headers=HEADERS, json=payload)
    assert response.status_code == 200, f"Command failed: {response.text}"
    
    data = response.json()
    assert data["status"] == "success"
    assert data["action"] == "create_contact"
    assert "result" in data
    assert data["result"]["email"] == "jane.doe@example.com"
    
    contact_id = data["result"]["contact_id"]
    created_contact_ids.append(contact_id)
    
    print(f"[✓] Test 14 (Command Endpoint): PASS - Action: {data['action']}, Contact: {data['result']['first_name']} {data['result']['last_name']}")


def test_strict_json() -> None:
    """Test 15: Strict JSON Validation (extra fields rejected)"""
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "unknown_field": "should_fail"  # Extra field
    }
    
    response = requests.post(f"{BASE_URL}/contacts", headers=HEADERS, json=payload)
    assert response.status_code == 422, f"Expected 422 for unknown field, got {response.status_code}"
    
    print(f"[✓] Test 15 (Strict JSON): PASS - Unknown fields rejected (422)")


def run_all_tests():
    """Führe alle Tests aus"""
    print("=" * 60)
    print("opena18 - CRM Agent - Integration Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Create Contact", test_create_contact),
        ("List Contacts", test_list_contacts),
        ("Delete Contact", test_delete_contact),
        ("Create Organization", test_create_organization),
        ("Search", test_search),
        ("Command Endpoint", test_command_endpoint),
        ("Strict JSON", test_strict_json),
    ]
    
    # Entity-abhängige Tests
    contact_data = None
    organization_data = None
    deal_data = None
    
    passed = 0
    failed = 0
    
    try:
        for test_name, test_func in tests:
            try:
                if test_func == test_create_contact:
                    contact_data = test_func()
                elif test_func == test_create_organization:
                    organization_data = test_func()
                else:
                    test_func()
                passed += 1
            except AssertionError as e:
                print(f"[✗] Test '{test_name}': FAIL - {e}")
                failed += 1
            except Exception as e:
                print(f"[✗] Test '{test_name}': ERROR - {e}")
                failed += 1
        
        # Entity-abhängige Tests (nach Create)
        if contact_data and organization_data:
            contact_id = contact_data["contact_id"]
            organization_id = organization_data["organization_id"]
            
            dependent_tests = [
                ("Update Contact", lambda: test_update_contact(contact_id)),
                ("Update Organization", lambda: test_update_organization(organization_id)),
                ("Create Deal", lambda: test_create_deal(contact_id, organization_id)),
            ]
            
            for test_name, test_func in dependent_tests:
                try:
                    if test_func.__name__ == "<lambda>" and "Create Deal" in test_name:
                        deal_data = test_func()
                    else:
                        test_func()
                    passed += 1
                except AssertionError as e:
                    print(f"[✗] Test '{test_name}': FAIL - {e}")
                    failed += 1
                except Exception as e:
                    print(f"[✗] Test '{test_name}': ERROR - {e}")
                    failed += 1
        
        # Deal-abhängige Tests
        if deal_data:
            deal_id = deal_data["deal_id"]
            
            deal_tests = [
                ("Update Deal", lambda: test_update_deal(deal_id)),
                ("Create Activity", lambda: test_create_activity(contact_data["contact_id"], deal_id)),
                ("List Activities", lambda: test_list_activities(contact_data["contact_id"])),
            ]
            
            for test_name, test_func in deal_tests:
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
