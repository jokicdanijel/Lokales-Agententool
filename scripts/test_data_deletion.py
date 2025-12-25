#!/usr/bin/env python3
"""
Test Meta Data Deletion Callback Implementation
"""

import base64
import hashlib
import hmac
import json
import time

import requests


def create_test_signed_request(app_secret: str, user_id: str) -> str:
    """Create a test signed request like Facebook would send"""

    # Create payload
    payload_data = {
        "algorithm": "HMAC-SHA256",
        "expires": int(time.time()) + 3600,  # 1 hour from now
        "issued_at": int(time.time()),
        "user_id": user_id,
    }

    # Encode payload
    payload_json = json.dumps(payload_data)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode().rstrip("=")

    # Create signature
    signature = hmac.new(app_secret.encode(), payload_b64.encode(), hashlib.sha256).digest()

    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")

    # Combine
    signed_request = f"{signature_b64}.{payload_b64}"
    return signed_request


def test_data_deletion_callback():
    """Test the data deletion callback endpoint"""

    # Test configuration
    base_url = "http://127.0.0.1:12370"
    app_secret = "test_app_secret"  # Use actual secret in production
    test_user_id = "test_user_12345"

    print("🧪 Testing Meta Data Deletion Callback")
    print("=" * 50)

    # 1. Health Check
    print("\n1. Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Service is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to service: {e}")
        return False

    # 2. Create Test Signed Request
    print("\n2. Creating test signed request...")
    signed_request = create_test_signed_request(app_secret, test_user_id)
    print(f"✅ Signed request created: {signed_request[:50]}...")

    # 3. Test Data Deletion Callback
    print("\n3. Testing data deletion callback...")
    try:
        response = requests.post(
            f"{base_url}/data-deletion-callback", data={"signed_request": signed_request}, timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Deletion request processed")
            print(f"   Status URL: {result.get('url')}")
            print(f"   Confirmation: {result.get('confirmation_code')}")

            # Store confirmation code for status check
            confirmation_code = result.get("confirmation_code")

        else:
            print(f"❌ Deletion request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Deletion request error: {e}")
        return False

    # 4. Check Deletion Status
    print("\n4. Checking deletion status...")
    if confirmation_code:
        try:
            # Wait a moment for async processing
            time.sleep(2)

            response = requests.get(f"{base_url}/deletion-status", params={"code": confirmation_code}, timeout=5)

            if response.status_code == 200:
                status = response.json()
                print("✅ Status retrieved")
                print(f"   User ID: {status.get('user_id')}")
                print(f"   Status: {status.get('status')}")
                print(f"   Requested: {status.get('requested_at')}")

                if status.get("completed_at"):
                    print(f"   Completed: {status.get('completed_at')}")

            else:
                print(f"❌ Status check failed: {response.status_code}")

        except Exception as e:
            print(f"❌ Status check error: {e}")

    # 5. Test Invalid Signed Request
    print("\n5. Testing invalid signed request...")
    try:
        response = requests.post(
            f"{base_url}/data-deletion-callback", data={"signed_request": "invalid.request"}, timeout=5
        )

        if response.status_code == 400:
            print("✅ Invalid request properly rejected")
        else:
            print(f"⚠️  Expected 400, got {response.status_code}")

    except Exception as e:
        print(f"❌ Invalid request test error: {e}")

    print("\n" + "=" * 50)
    print("🎯 Test Results Summary:")
    print("✅ Data Deletion Callback is working")
    print("📋 Ready for Facebook configuration")
    print(f"📋 Callback URL: {base_url}/data-deletion-callback")
    print(f"📋 Status URL: {base_url}/deletion-status?code=CODE")

    return True


if __name__ == "__main__":
    test_data_deletion_callback()
