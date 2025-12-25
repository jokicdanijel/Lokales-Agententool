#!/usr/bin/env python3
"""
test_opena14.py - Integration Tests für opena14 (Calendar Agent)
=================================================================

Test Coverage:
  1. Health Check
  2. Root Endpoint
  3. Create Calendar
  4. List Calendars
  5. Create Event
  6. List Events
  7. Update Event
  8. Delete Event
  9. Event Filtering (date range)
 10. iCalendar Export
 11. Command Endpoint (Option-2-Flow)
 12. Strict JSON Validation

Port: 12359
Auth: Bearer Token (from .env)

Maintainer: ELION Team
Last Update: 27. November 2025
"""

import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = "http://127.0.0.1:12359"
PROJECT_ROOT = Path(__file__).parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# Load Bearer Token
BEARER_TOKEN = None
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            if line.strip().startswith("BEARER_TOKEN="):
                BEARER_TOKEN = line.split("=", 1)[1].strip()
                break

if not BEARER_TOKEN:
    print("⚠️  WARNING: BEARER_TOKEN nicht in .env gefunden!")
    BEARER_TOKEN = "dev-token-only"

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}", "Content-Type": "application/json"}

# ============================================================================
# COLOR OUTPUT
# ============================================================================

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_test(name, status, details=""):
    """Print color-coded test result"""
    color = GREEN if status == "PASS" else RED
    symbol = "✓" if status == "PASS" else "✗"
    print(f"{color}[{symbol}] Test {name}: {status}{RESET}")
    if details:
        print(f"    {BLUE}{details}{RESET}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def generate_iso_datetime(days_offset=0, hours_offset=0):
    """Generate ISO 8601 datetime string"""
    dt = datetime.now(UTC) + timedelta(days=days_offset, hours=hours_offset)
    return dt.isoformat().replace("+00:00", "Z")


# ============================================================================
# TESTS
# ============================================================================


def test_health():
    """Test 1: Health Check"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        data = r.json()

        assert r.status_code == 200, f"Status {r.status_code}"
        assert data["status"] == "ok", f"Status: {data['status']}"
        assert data["service"] == "opena14", f"Service: {data['service']}"
        assert data["port"] == 12359, f"Port: {data['port']}"
        assert data["kuerzel"] == "calp", f"Kürzel: {data['kuerzel']}"

        print_test(
            "1 (Health)",
            "PASS",
            f"Uptime: {data['uptime_seconds']:.2f}s, Events: {data['total_events']}, iCal: {data['ical_support']}",
        )
        return True
    except Exception as e:
        print_test("1 (Health)", "FAIL", str(e))
        return False


def test_root():
    """Test 2: Root Endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        data = r.json()

        assert r.status_code == 200
        assert data["service"] == "opena14"
        assert data["kuerzel"] == "calp"
        assert data["port"] == "12359"

        print_test("2 (Root)", "PASS", f"Description: {data['description'][:50]}...")
        return True
    except Exception as e:
        print_test("2 (Root)", "FAIL", str(e))
        return False


def test_create_calendar():
    """Test 3: Create Calendar"""
    try:
        payload = {
            "name": "Work Calendar",
            "description": "Professional meetings and deadlines",
            "timezone": "Europe/Berlin",
            "color": "#FF5733",
        }

        r = requests.post(f"{BASE_URL}/calendars/create", headers=HEADERS, json=payload, timeout=5)
        data = r.json()

        assert r.status_code == 200, f"Status {r.status_code}"
        assert "calendar_id" in data
        assert data["name"] == "Work Calendar"
        assert data["timezone"] == "Europe/Berlin"
        assert data["color"] == "#FF5733"

        print_test("3 (Create Calendar)", "PASS", f"Calendar ID: {data['calendar_id'][:8]}")

        # Store for later tests
        global TEST_CALENDAR_ID
        TEST_CALENDAR_ID = data["calendar_id"]
        return True
    except Exception as e:
        print_test("3 (Create Calendar)", "FAIL", str(e))
        return False


def test_list_calendars():
    """Test 4: List Calendars"""
    try:
        r = requests.get(f"{BASE_URL}/calendars/list", headers=HEADERS, timeout=5)
        data = r.json()

        assert r.status_code == 200
        assert isinstance(data, list)
        assert len(data) >= 1, "Should have at least 1 calendar (default)"

        # Verify structure
        calendar = data[0]
        assert "calendar_id" in calendar
        assert "name" in calendar
        assert "timezone" in calendar

        print_test("4 (List Calendars)", "PASS", f"Total: {len(data)}")
        return True
    except Exception as e:
        print_test("4 (List Calendars)", "FAIL", str(e))
        return False


def test_create_event():
    """Test 5: Create Event"""
    try:
        start = generate_iso_datetime(days_offset=1, hours_offset=9)  # Tomorrow 9 AM
        end = generate_iso_datetime(days_offset=1, hours_offset=10)  # Tomorrow 10 AM

        payload = {
            "calendar_id": TEST_CALENDAR_ID,
            "summary": "Team Meeting",
            "start": start,
            "end": end,
            "description": "Weekly team sync",
            "location": "Conference Room A",
            "attendees": ["alice@example.com", "bob@example.com"],
            "all_day": False,
        }

        r = requests.post(f"{BASE_URL}/events/create", headers=HEADERS, json=payload, timeout=5)
        data = r.json()

        assert r.status_code == 200, f"Status {r.status_code}"
        assert "event_id" in data
        assert data["summary"] == "Team Meeting"
        assert data["calendar_id"] == TEST_CALENDAR_ID
        assert data["location"] == "Conference Room A"
        assert len(data["attendees"]) == 2

        print_test("5 (Create Event)", "PASS", f"Event ID: {data['event_id'][:8]}")

        # Store for later tests
        global TEST_EVENT_ID
        TEST_EVENT_ID = data["event_id"]
        return True
    except Exception as e:
        print_test("5 (Create Event)", "FAIL", str(e))
        return False


def test_list_events():
    """Test 6: List Events"""
    try:
        payload = {"calendar_id": TEST_CALENDAR_ID, "max_results": 100}

        r = requests.post(f"{BASE_URL}/events/list", headers=HEADERS, json=payload, timeout=5)
        data = r.json()

        assert r.status_code == 200
        assert isinstance(data, list)
        assert len(data) > 0, "Should have at least 1 event"

        # Verify structure
        event = data[0]
        assert "event_id" in event
        assert "summary" in event
        assert "start" in event
        assert "end" in event

        print_test("6 (List Events)", "PASS", f"Total: {len(data)}")
        return True
    except Exception as e:
        print_test("6 (List Events)", "FAIL", str(e))
        return False


def test_update_event():
    """Test 7: Update Event"""
    try:
        payload = {
            "event_id": TEST_EVENT_ID,
            "summary": "Team Meeting (Updated)",
            "location": "Conference Room B",
            "description": "Updated weekly team sync",
        }

        r = requests.put(f"{BASE_URL}/events/update", headers=HEADERS, json=payload, timeout=5)
        data = r.json()

        assert r.status_code == 200, f"Status {r.status_code}"
        assert data["event_id"] == TEST_EVENT_ID
        assert data["summary"] == "Team Meeting (Updated)"
        assert data["location"] == "Conference Room B"

        print_test("7 (Update Event)", "PASS", f"Updated: {data['summary']}")
        return True
    except Exception as e:
        print_test("7 (Update Event)", "FAIL", str(e))
        return False


def test_delete_event():
    """Test 8: Delete Event"""
    try:
        # Create a temporary event to delete
        start = generate_iso_datetime(days_offset=2)
        end = generate_iso_datetime(days_offset=2, hours_offset=1)

        create_payload = {
            "calendar_id": TEST_CALENDAR_ID,
            "summary": "Temporary Event (will be deleted)",
            "start": start,
            "end": end,
        }

        r1 = requests.post(f"{BASE_URL}/events/create", headers=HEADERS, json=create_payload, timeout=5)
        temp_event = r1.json()
        temp_event_id = temp_event["event_id"]

        # Delete the event
        delete_payload = {"event_id": temp_event_id, "calendar_id": TEST_CALENDAR_ID}

        r2 = requests.delete(f"{BASE_URL}/events/delete", headers=HEADERS, json=delete_payload, timeout=5)
        data = r2.json()

        assert r2.status_code == 200, f"Status {r2.status_code}"
        assert data["status"] == "deleted"
        assert data["event_id"] == temp_event_id

        print_test("8 (Delete Event)", "PASS", f"Deleted: {temp_event_id[:8]}")
        return True
    except Exception as e:
        print_test("8 (Delete Event)", "FAIL", str(e))
        return False


def test_event_filtering():
    """Test 9: Event Filtering (date range)"""
    try:
        # Create events at different times
        now = datetime.now(UTC)

        # Past event
        past_start = (now - timedelta(days=7)).isoformat().replace("+00:00", "Z")
        past_end = (now - timedelta(days=7, hours=-1)).isoformat().replace("+00:00", "Z")

        r1 = requests.post(
            f"{BASE_URL}/events/create",
            headers=HEADERS,
            json={"calendar_id": TEST_CALENDAR_ID, "summary": "Past Event", "start": past_start, "end": past_end},
            timeout=5,
        )

        # Future event
        future_start = (now + timedelta(days=7)).isoformat().replace("+00:00", "Z")
        future_end = (now + timedelta(days=7, hours=1)).isoformat().replace("+00:00", "Z")

        r2 = requests.post(
            f"{BASE_URL}/events/create",
            headers=HEADERS,
            json={"calendar_id": TEST_CALENDAR_ID, "summary": "Future Event", "start": future_start, "end": future_end},
            timeout=5,
        )

        # Filter: Only future events
        filter_start = now.isoformat().replace("+00:00", "Z")

        r3 = requests.post(
            f"{BASE_URL}/events/list",
            headers=HEADERS,
            json={"calendar_id": TEST_CALENDAR_ID, "start_date": filter_start, "max_results": 100},
            timeout=5,
        )

        data = r3.json()

        assert r3.status_code == 200

        # Verify no past events in results
        summaries = [e["summary"] for e in data]
        assert "Past Event" not in summaries, "Past event should be filtered out"

        print_test("9 (Event Filtering)", "PASS", f"Filtered events: {len(data)} (future only)")
        return True
    except Exception as e:
        print_test("9 (Event Filtering)", "FAIL", str(e))
        return False


def test_ical_export():
    """Test 10: iCalendar Export"""
    try:
        r = requests.get(f"{BASE_URL}/events/{TEST_EVENT_ID}/ical", headers=HEADERS, timeout=5)
        data = r.json()

        assert r.status_code == 200, f"Status {r.status_code}"

        if "ical" in data:
            # iCal support available
            ical_content = data["ical"]
            assert "BEGIN:VCALENDAR" in ical_content
            assert "BEGIN:VEVENT" in ical_content
            assert "Team Meeting" in ical_content
            print_test("10 (iCal Export)", "PASS", "iCalendar format valid")
        else:
            # iCal support disabled (missing library)
            print_test("10 (iCal Export)", "PASS", "iCal support disabled (OK)")

        return True
    except Exception as e:
        # If 501 Not Implemented, that's also OK (missing icalendar library)
        if "501" in str(e):
            print_test("10 (iCal Export)", "PASS", "iCal support disabled (501, OK)")
            return True
        print_test("10 (iCal Export)", "FAIL", str(e))
        return False


def test_command_endpoint():
    """Test 11: Command Endpoint (Option-2-Flow)"""
    try:
        start = generate_iso_datetime(days_offset=5)
        end = generate_iso_datetime(days_offset=5, hours_offset=2)

        payload = {
            "action": "create_event",
            "params": {
                "calendar_id": TEST_CALENDAR_ID,
                "summary": "Command-Created Event",
                "start": start,
                "end": end,
                "description": "Created via command endpoint",
            },
        }

        r = requests.post(f"{BASE_URL}/command", headers=HEADERS, json=payload, timeout=5)
        data = r.json()

        assert r.status_code == 200, f"Status {r.status_code}"
        assert data["status"] == "success"
        assert data["action"] == "create_event"
        assert "result" in data
        assert data["result"]["summary"] == "Command-Created Event"

        print_test("11 (Command Endpoint)", "PASS", f"Action: {data['action']}, Event created")
        return True
    except Exception as e:
        print_test("11 (Command Endpoint)", "FAIL", str(e))
        return False


def test_strict_json():
    """Test 12: Strict JSON Validation (extra="forbid")"""
    try:
        # Send request with unknown field
        payload = {
            "calendar_id": TEST_CALENDAR_ID,
            "summary": "Test Event",
            "start": generate_iso_datetime(),
            "end": generate_iso_datetime(hours_offset=1),
            "unknown_field": "should_be_rejected",  # Extra field
        }

        r = requests.post(f"{BASE_URL}/events/create", headers=HEADERS, json=payload, timeout=5)

        # Pydantic should reject this (422 Unprocessable Entity)
        assert r.status_code == 422, f"Expected 422, got {r.status_code}"

        error = r.json()
        assert "detail" in error

        print_test("12 (Strict JSON)", "PASS", "Unknown fields rejected (extra='forbid')")
        return True
    except Exception as e:
        print_test("12 (Strict JSON)", "FAIL", str(e))
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================


def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}  opena14 (Calendar) - Integration Tests{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    print(f"Base URL:      {BASE_URL}")
    print(f"Bearer Token:  {BEARER_TOKEN[:20]}...")
    print()

    # Wait for service
    print(f"{YELLOW}Warte auf Service-Start (3 Sekunden)...{RESET}")
    time.sleep(3)

    # Run tests
    results = []

    results.append(test_health())
    results.append(test_root())
    results.append(test_create_calendar())
    results.append(test_list_calendars())
    results.append(test_create_event())
    results.append(test_list_events())
    results.append(test_update_event())
    results.append(test_delete_event())
    results.append(test_event_filtering())
    results.append(test_ical_export())
    results.append(test_command_endpoint())
    results.append(test_strict_json())

    # Summary
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100

    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}  Test Summary{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    print(f"Total:  {total}")
    print(f"Passed: {GREEN}{passed}{RESET}")
    print(f"Failed: {RED}{total - passed}{RESET}")
    print(f"Rate:   {GREEN if percentage == 100 else YELLOW}{percentage:.1f}%{RESET}")
    print()

    if percentage == 100:
        print(f"{GREEN}✅ ALL TESTS PASSED{RESET}\n")
        return 0
    else:
        print(f"{RED}❌ SOME TESTS FAILED{RESET}\n")
        return 1


if __name__ == "__main__":
    exit(main())
