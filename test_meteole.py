#!/usr/bin/env python3
"""Test meteole library for AROME data access."""

import sys
from meteole import AromeForecast
import datetime as dt
import json

def test_meteole(application_id: str, lat: float, lon: float):
    """Test meteole library with user's coordinates."""

    print("=" * 70)
    print("Testing meteole Library")
    print("=" * 70)
    print(f"\nCoordinates: {lat}, {lon}")
    print(f"Application ID: {application_id[:20]}...")

    try:
        # Initialize AROME client
        print("\nInitializing AromeForecast client...")
        arome = AromeForecast(application_id=application_id)
        print("✅ Client initialized successfully!")

        # Get current forecast run time (use latest available)
        now = dt.datetime.utcnow()
        # AROME runs every 3 hours (00, 03, 06, 09, 12, 15, 18, 21 UTC)
        run_hour = (now.hour // 3) * 3
        run_time = now.replace(hour=run_hour, minute=0, second=0, microsecond=0)
        run_str = run_time.strftime("%Y-%m-%dT%H.%M.%SZ")

        print(f"\nUsing forecast run: {run_str}")

        # Try to get wind data at 10m height for next hour
        print("\n" + "-" * 70)
        print("Test 1: Wind Speed at 10m height")
        print("-" * 70)

        try:
            wind_data = arome.get_coverage(
                indicator="U_COMPONENT_OF_WIND__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
                run=run_str,
                forecast_horizons=[dt.timedelta(hours=1)],
                heights=[10],
                lat=(lat, lat),  # Single point
                long=(lon, lon)
            )

            print("✅ Got wind U-component data!")
            print(f"Data shape: {wind_data.shape}")
            print(f"Columns: {wind_data.columns.tolist()}")
            print("\nFirst few rows:")
            print(wind_data.head())

        except Exception as e:
            print(f"❌ Error getting wind data: {e}")

        # Try to get temperature
        print("\n" + "-" * 70)
        print("Test 2: Temperature at 2m height")
        print("-" * 70)

        try:
            temp_data = arome.get_coverage(
                indicator="TEMPERATURE__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
                run=run_str,
                forecast_horizons=[dt.timedelta(hours=1), dt.timedelta(hours=2)],
                heights=[2],
                lat=(lat, lat),
                long=(lon, lon)
            )

            print("✅ Got temperature data!")
            print(f"Data shape: {temp_data.shape}")
            print("\nData:")
            print(temp_data)

        except Exception as e:
            print(f"❌ Error getting temperature: {e}")

        # Try to get wind gust
        print("\n" + "-" * 70)
        print("Test 3: Wind Gust at 10m height")
        print("-" * 70)

        try:
            gust_data = arome.get_coverage(
                indicator="V_COMPONENT_OF_WIND_GUST__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND",
                run=run_str,
                forecast_horizons=[dt.timedelta(hours=1)],
                heights=[10],
                lat=(lat, lat),
                long=(lon, lon)
            )

            print("✅ Got wind gust data!")
            print(f"Data shape: {gust_data.shape}")
            print("\nData:")
            print(gust_data)

        except Exception as e:
            print(f"❌ Error getting wind gust: {e}")

        # Get list of available indicators
        print("\n" + "-" * 70)
        print("Available indicators:")
        print("-" * 70)

        try:
            capabilities = arome.get_capabilities()
            print(f"Found {len(capabilities)} indicators")

            # Look for wind-related indicators
            wind_indicators = [c for c in capabilities if 'WIND' in c or 'GUST' in c]
            print("\nWind-related indicators:")
            for ind in wind_indicators[:10]:
                print(f"  - {ind}")

        except Exception as e:
            print(f"Error getting capabilities: {e}")

    except Exception as e:
        print(f"\n❌ Error initializing meteole: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 test_meteole.py <APPLICATION_ID> <LAT> <LON>")
        print("\nExample:")
        print("  python3 test_meteole.py '5c0aba66-1d59...' 46.03 6.31")
        sys.exit(1)

    app_id = sys.argv[1]
    lat = float(sys.argv[2])
    lon = float(sys.argv[3])

    test_meteole(app_id, lat, lon)
