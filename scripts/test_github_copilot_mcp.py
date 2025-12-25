#!/usr/bin/env python3
"""Test GitHub Copilot MCP API integration.

This script tests the connection to the GitHub Copilot MCP API
and verifies that the API key is valid.

Usage:
    python scripts/test_github_copilot_mcp.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import requests
except ImportError:
    print("❌ requests library not installed")
    print("   Install with: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv not installed (optional)")
    print("   Install with: pip install python-dotenv")
    # Continue without dotenv
else:
    # Load environment variables from .env
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        env_example = PROJECT_ROOT / ".env.example"
        if env_example.exists():
            print(f"⚠️  No .env file found, using {env_example}")
            load_dotenv(env_example)


def mask_api_key(key: str) -> str:
    """Mask API key for display."""
    if not key or len(key) < 15:
        return "***"
    return f"{key[:10]}...{key[-4:]}"


def test_api_connection() -> bool:
    """Test connection to GitHub Copilot MCP API.

    Returns:
        bool: True if connection successful, False otherwise
    """
    print("=" * 44)
    print("🧪 GitHub Copilot MCP API Test (Python)")
    print("=" * 44)

    # Get configuration from environment
    api_key = os.getenv("GITHUB_COPILOT_API_KEY")
    endpoint = os.getenv("GITHUB_COPILOT_MCP_ENDPOINT", "https://api.githubcopilot.com/mcp/")

    print(f"Endpoint: {endpoint}")
    print()

    # Validate API key
    if not api_key:
        print("❌ GITHUB_COPILOT_API_KEY not set in .env")
        print()
        print("Please add your GitHub Copilot API key to .env:")
        print("  GITHUB_COPILOT_API_KEY=your-key-here")
        print()
        print("To obtain an API key:")
        print("  1. Visit: https://github.com/settings/tokens")
        print("  2. Generate new token with 'copilot' scope")
        print("  3. Add to .env file")
        return False

    print(f"API Key: {mask_api_key(api_key)}")
    print()

    # Prepare request
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json", "User-Agent": "ELION-MCP-Server/1.0"}

    try:
        print("🔍 Testing API connection...")
        response = requests.get(endpoint, headers=headers, timeout=10)

        print()
        print(f"Response Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ API connection successful")
            print()
            print("Response data:")
            if response.text:
                try:
                    data = response.json()
                    import json

                    print(json.dumps(data, indent=2))
                except Exception:
                    print(response.text[:500])
            else:
                print("  (empty response)")
            print()
            print("Your GitHub Copilot MCP API key is valid and working.")
            return True

        elif response.status_code == 401:
            print("❌ Authentication failed")
            print()
            print("Possible causes:")
            print("  - Invalid API key")
            print("  - Expired token")
            print("  - Missing 'copilot' scope")
            print()
            print("Please regenerate your API key at:")
            print("  https://github.com/settings/tokens")
            return False

        elif response.status_code == 404:
            print("⚠️  Endpoint not found")
            print()
            print("The API endpoint may have changed or is incorrect.")
            print("Please check the GitHub Copilot documentation.")
            return False

        else:
            print(f"⚠️  Received HTTP {response.status_code}")
            print()
            print("Response:")
            print(response.text[:500])
            print()
            print("Unexpected response from API.")
            print("Please check the endpoint and API key.")
            return False

    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        print()
        print("The API did not respond within 10 seconds.")
        print("Please check your internet connection.")
        return False

    except requests.exceptions.ConnectionError as e:
        print("❌ Connection failed")
        print()
        print(f"Error: {e}")
        print()
        print("Could not connect to the API endpoint.")
        print("Please check your internet connection.")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main entry point."""
    try:
        success = test_api_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print("⚠️  Test interrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
