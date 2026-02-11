#!/usr/bin/env python3
"""Test script for direct AROME API access."""

import sys
import requests
import json

def test_direct_arome_api(token: str, lat: float, lon: float):
    """Test direct AROME API with authentication."""

    print("=" * 70)
    print("Testing Direct AROME WCS API")
    print("=" * 70)

    # Base URL for AROME API
    base_url = "https://public-api.meteofrance.fr/public/arome/1.0"

    # Headers with authentication
    headers = {
        "apikey": token,
        "Accept": "application/json"
    }

    print(f"\nTesting with coordinates: {lat}, {lon}")
    print(f"Token: {token[:20]}...")

    # Test 1: Simple forecast endpoint
    print("\n" + "-" * 70)
    print("Test 1: Trying /forecast endpoint")
    print("-" * 70)

    try:
        url = f"{base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.content)} bytes")

        if response.status_code == 200:
            print("✅ SUCCESS!")
            data = response.json()
            print("\nResponse structure:")
            print(json.dumps(data, indent=2)[:1000] + "...")
        else:
            print(f"❌ Error: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    # Test 2: WCS GetCapabilities
    print("\n" + "-" * 70)
    print("Test 2: Trying WCS GetCapabilities")
    print("-" * 70)

    try:
        url = f"{base_url}/wcs/MF-NWP-HIGHRES-AROME-001-FRANCE-WCS"
        params = {
            "service": "WCS",
            "version": "2.0.1",
            "request": "GetCapabilities"
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ WCS endpoint accessible!")
            print(f"Response preview: {response.text[:500]}...")
        else:
            print(f"❌ Error: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Exception: {e}")

    # Test 3: Alternative API structure
    print("\n" + "-" * 70)
    print("Test 3: Trying alternative endpoints")
    print("-" * 70)

    endpoints = [
        "/forecast/grid",
        "/data",
        "/coverage",
    ]

    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            params = {"lat": lat, "lon": lon}
            response = requests.get(url, headers=headers, params=params, timeout=5)
            print(f"{endpoint}: {response.status_code}")
        except Exception as e:
            print(f"{endpoint}: ❌ {str(e)[:50]}")

    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 test_direct_arome_api.py <TOKEN> <LAT> <LON>")
        print("\nExample:")
        print("  python3 test_direct_arome_api.py 'eyJ...' 46.03 6.31")
        sys.exit(1)

    token = sys.argv[1]
    lat = float(sys.argv[2])
    lon = float(sys.argv[3])

    test_direct_arome_api(token, lat, lon)
