#!/usr/bin/env python3
"""Test Open-Meteo API for comparison with Météo-France data."""

import sys
import requests
import json
from datetime import datetime

def test_openmeteo(lat: float, lon: float):
    """Test Open-Meteo API with user's coordinates."""

    print("=" * 70)
    print("Testing Open-Meteo API (with Météo-France AROME)")
    print("=" * 70)
    print(f"\nCoordinates: {lat}, {lon}")

    # Open-Meteo Météo-France API endpoint
    base_url = "https://api.open-meteo.com/v1/meteofrance"

    # Test 1: Current + Hourly forecast
    print("\n" + "-" * 70)
    print("Test 1: Hourly Forecast with Wind Data")
    print("-" * 70)

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,wind_gusts_10m,wind_direction_10m",
        "hourly": "temperature_2m,wind_speed_10m,wind_gusts_10m,wind_direction_10m,cloud_cover,precipitation",
        "timezone": "Europe/Paris",
        "forecast_days": 3
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print("✅ SUCCESS!\n")

            # Current conditions
            if "current" in data:
                current = data["current"]
                print("Current Conditions:")
                print(f"  Temperature: {current.get('temperature_2m')}°C")
                print(f"  Wind Speed: {current.get('wind_speed_10m')} km/h")
                print(f"  Wind Gusts: {current.get('wind_gusts_10m')} km/h")
                print(f"  Direction: {current.get('wind_direction_10m')}°")

            # Location returned
            if "latitude" in data and "longitude" in data:
                print(f"\nLocation used by API:")
                print(f"  Requested: {lat}, {lon}")
                print(f"  Returned:  {data['latitude']}, {data['longitude']}")
                print(f"  Elevation: {data.get('elevation', 'N/A')}m")

            # Hourly forecast
            if "hourly" in data:
                hourly = data["hourly"]
                print(f"\nHourly Forecast (first 24 hours):")
                print("-" * 50)

                max_wind = 0
                max_gust = 0

                for i in range(min(24, len(hourly["time"]))):
                    time = hourly["time"][i]
                    temp = hourly["temperature_2m"][i]
                    wind = hourly["wind_speed_10m"][i]
                    gust = hourly["wind_gusts_10m"][i]

                    if wind and wind > max_wind:
                        max_wind = wind
                    if gust and gust > max_gust:
                        max_gust = gust

                    if i < 5:  # Show first 5 hours
                        print(f"{time}: {temp}°C, Wind: {wind} km/h, Gust: {gust} km/h")

                print(f"\n24h Maximum Wind Speed: {max_wind} km/h")
                print(f"24h Maximum Wind Gust: {max_gust} km/h")
        else:
            print(f"❌ Error: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Compare with standard Open-Meteo (not Météo-France specific)
    print("\n" + "-" * 70)
    print("Test 2: Standard Open-Meteo API (for comparison)")
    print("-" * 70)

    std_url = "https://api.open-meteo.com/v1/forecast"

    try:
        response = requests.get(std_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if "current" in data:
                current = data["current"]
                print(f"Wind Speed: {current.get('wind_speed_10m')} km/h")
                print(f"Wind Gusts: {current.get('wind_gusts_10m')} km/h")

            if "hourly" in data:
                hourly = data["hourly"]
                max_gust = max([g for g in hourly["wind_gusts_10m"][:24] if g is not None], default=0)
                print(f"24h Max Gust: {max_gust} km/h")

    except Exception as e:
        print(f"Error: {e}")

    # Test 3: DWD ICON model (high resolution)
    print("\n" + "-" * 70)
    print("Test 3: DWD ICON Model (2km resolution)")
    print("-" * 70)

    icon_url = "https://api.open-meteo.com/v1/dwd-icon"

    try:
        response = requests.get(icon_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if "current" in data:
                current = data["current"]
                print(f"Wind Speed: {current.get('wind_speed_10m')} km/h")
                print(f"Wind Gusts: {current.get('wind_gusts_10m')} km/h")

            if "hourly" in data:
                hourly = data["hourly"]
                max_gust = max([g for g in hourly["wind_gusts_10m"][:24] if g is not None], default=0)
                print(f"24h Max Gust: {max_gust} km/h")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 test_openmeteo.py <LAT> <LON>")
        print("\nExample:")
        print("  python3 test_openmeteo.py 46.03 6.31")
        sys.exit(1)

    lat = float(sys.argv[1])
    lon = float(sys.argv[2])

    test_openmeteo(lat, lon)
