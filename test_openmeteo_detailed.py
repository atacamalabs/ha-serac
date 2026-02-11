#!/usr/bin/env python3
"""Detailed Open-Meteo API comparison."""

import sys
import requests
from datetime import datetime, timedelta

def analyze_daily_max(hourly_data, days=3):
    """Calculate daily max wind/gust from hourly data."""
    times = hourly_data["time"]
    wind_speeds = hourly_data["wind_speed_10m"]
    wind_gusts = hourly_data["wind_gusts_10m"]

    daily_max = {}

    for i, time_str in enumerate(times):
        dt = datetime.fromisoformat(time_str)
        date = dt.date()

        if date not in daily_max:
            daily_max[date] = {"wind_max": 0, "gust_max": 0}

        wind = wind_speeds[i] if wind_speeds[i] is not None else 0
        gust = wind_gusts[i] if wind_gusts[i] is not None else 0

        daily_max[date]["wind_max"] = max(daily_max[date]["wind_max"], wind)
        daily_max[date]["gust_max"] = max(daily_max[date]["gust_max"], gust)

    return daily_max


def test_source(name: str, url: str, lat: float, lon: float, description: str):
    """Test a specific Open-Meteo source."""

    print("\n" + "=" * 70)
    print(f"{name}")
    print("=" * 70)
    print(description)
    print()

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,wind_speed_10m,wind_gusts_10m",
        "timezone": "Europe/Paris",
        "forecast_days": 7
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Location info
            print(f"📍 Location:")
            print(f"   Requested: {lat:.4f}, {lon:.4f}")
            print(f"   Returned:  {data['latitude']:.4f}, {data['longitude']:.4f}")
            print(f"   Elevation: {data.get('elevation', 'N/A')}m")
            print(f"   Timezone:  {data.get('timezone', 'N/A')}")

            # Calculate daily maximums
            daily_max = analyze_daily_max(data["hourly"])

            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)
            day_after = today + timedelta(days=2)

            print(f"\n📊 Daily Maximum Forecasts:")
            print("-" * 70)

            for i, date in enumerate(sorted(daily_max.keys())[:5]):
                day_data = daily_max[date]

                # Label the day
                if date == today:
                    label = "TODAY"
                elif date == tomorrow:
                    label = "TOMORROW"
                elif date == day_after:
                    label = "DAY AFTER TOMORROW ⭐"
                else:
                    label = f"Day +{i}"

                print(f"{date} ({label:25s})")
                print(f"   Max Wind Speed: {day_data['wind_max']:5.1f} km/h")
                print(f"   Max Wind Gust:  {day_data['gust_max']:5.1f} km/h")
                print()

            return daily_max

        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def main(lat: float, lon: float):
    """Compare different Open-Meteo sources."""

    print("=" * 70)
    print("OPEN-METEO API COMPARISON")
    print("=" * 70)
    print(f"Testing location: {lat}, {lon}")

    sources = [
        {
            "name": "🇫🇷 Météo-France AROME",
            "url": "https://api.open-meteo.com/v1/meteofrance",
            "description": """
Source: Météo-France AROME model
Coverage: France only
Resolution: 1.3km grid
Updates: Every 3 hours (00, 03, 06, 09, 12, 15, 18, 21 UTC)
Forecast: Up to 42 hours
Best for: French locations (especially mountains)
            """.strip()
        },
        {
            "name": "🌍 Open-Meteo Standard (Best Match)",
            "url": "https://api.open-meteo.com/v1/forecast",
            "description": """
Source: Automatically selects best model for location
- In France: Uses Météo-France AROME + ARPEGE
- Blends multiple sources for best accuracy
Resolution: Varies (1-11km depending on location)
Updates: Multiple times per day
Forecast: Up to 16 days
Best for: General use, most accurate automatic selection
            """.strip()
        },
        {
            "name": "🇩🇪 DWD ICON",
            "url": "https://api.open-meteo.com/v1/dwd-icon",
            "description": """
Source: German Weather Service ICON model
Coverage: Global (but optimized for Central Europe)
Resolution: 2km grid (Europe), 13km global
Updates: Every 3 hours
Forecast: Up to 7 days
Best for: Central Europe, alternative to Météo-France
            """.strip()
        }
    ]

    results = {}

    for source in sources:
        results[source["name"]] = test_source(
            source["name"],
            source["url"],
            lat,
            lon,
            source["description"]
        )

    # Summary comparison
    print("\n" + "=" * 70)
    print("📋 SUMMARY - Day After Tomorrow Comparison")
    print("=" * 70)

    day_after = datetime.now().date() + timedelta(days=2)

    for name, data in results.items():
        if data and day_after in data:
            gust = data[day_after]["gust_max"]
            print(f"{name:40s}: {gust:5.1f} km/h")

    print("\n" + "=" * 70)
    print("💡 RECOMMENDATION")
    print("=" * 70)
    print("""
For your French Alps location, I recommend using:

🏆 Open-Meteo Standard (Best Match)
   - Automatically uses Météo-France AROME for France
   - Blends multiple models for best accuracy
   - Longer forecast (16 days vs 2 days)
   - More frequent updates
   - Free, no authentication needed
   - Simple JSON API

This gives you the best of both worlds: Météo-France accuracy
for France + better model selection + longer forecasts.
    """.strip())


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 test_openmeteo_detailed.py <LAT> <LON>")
        sys.exit(1)

    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    main(lat, lon)
