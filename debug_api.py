#!/usr/bin/env python3
"""
Debug script to test API responses and diagnose issues
"""
import requests
import json
import sys

# Server URL - update if needed
SERVER_URL = "http://pi-server:8080"

def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)

def test_endpoint(endpoint, description):
    """Test an endpoint and show the response"""
    url = f"{SERVER_URL}{endpoint}"
    print(f"\n{description}")
    print(f"URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response (pretty-printed):")
                print(json.dumps(data, indent=2))

                # Check structure
                if isinstance(data, dict):
                    print(f"\nTop-level keys: {list(data.keys())}")
                    if "success" in data:
                        print(f"Success: {data['success']}")
                    if "data" in data:
                        data_field = data["data"]
                        print(f"Data type: {type(data_field).__name__}")
                        if isinstance(data_field, dict):
                            print(f"Data keys: {list(data_field.keys())}")
                        elif isinstance(data_field, list):
                            print(f"Data length: {len(data_field)}")
                            if len(data_field) > 0:
                                print(f"First item keys: {list(data_field[0].keys()) if isinstance(data_field[0], dict) else 'N/A'}")
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
                print(f"Raw response: {response.text[:500]}")
        else:
            print(f"Error response: {response.text[:200]}")

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return False

    return True

def main():
    print_section("API Debug Tool")
    print(f"Testing server at: {SERVER_URL}")

    # Test health
    print_section("1. Health Check")
    if not test_endpoint("/health", "Testing server health"):
        print("\n❌ Server is not accessible!")
        sys.exit(1)
    print("✅ Server is responding")

    # Test search
    print_section("2. Search Endpoint")
    test_endpoint("/api/search?q=a", "Testing search with query 'a'")

    # Test artists
    print_section("3. Artists Endpoint")
    test_endpoint("/api/artists", "Testing artists endpoint")

    # Test status
    print_section("4. Status Endpoint")
    test_endpoint("/api/status", "Testing player status")

    print_section("Debug Complete")
    print("\nLook for the response structure above.")
    print("The search endpoint should return:")
    print('  {"success": true, "data": {"songs": [...], "albums": [], "artists": []}}')
    print("\nIf it returns something different, the server may not be updated yet.")

if __name__ == "__main__":
    main()
