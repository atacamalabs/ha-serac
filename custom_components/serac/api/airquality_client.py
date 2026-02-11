"""Open-Meteo Air Quality API client for Serac integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class AirQualityApiError(Exception):
    """Exception raised for Air Quality API errors."""


class AirQualityClient:
    """Client for Open-Meteo Air Quality API."""

    def __init__(self, latitude: float, longitude: float) -> None:
        """Initialize the Air Quality client.

        Args:
            latitude: Location latitude
            longitude: Location longitude
        """
        self.latitude = latitude
        self.longitude = longitude
        self.base_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    async def async_get_air_quality(self) -> dict[str, Any]:
        """Fetch air quality data from Open-Meteo Air Quality API.

        Returns:
            Dictionary with current air quality and daily forecast

        Raises:
            AirQualityApiError: If the API request fails
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": ",".join([
                "european_aqi",
                "pm2_5",
                "pm10",
                "nitrogen_dioxide",
                "ozone",
                "sulphur_dioxide",
            ]),
            "hourly": "european_aqi,pm2_5,pm10",
            "timezone": "auto",
            "forecast_days": 5,  # Get 5 days of hourly data (API limit)
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise AirQualityApiError(
                            f"Air Quality API returned status {response.status}: {error_text}"
                        )

                    data = await response.json()

            # Extract current air quality
            current = data.get("current", {})
            current_aqi = {
                "european_aqi": current.get("european_aqi"),
                "pm2_5": current.get("pm2_5"),
                "pm10": current.get("pm10"),
                "nitrogen_dioxide": current.get("nitrogen_dioxide"),
                "ozone": current.get("ozone"),
                "sulphur_dioxide": current.get("sulphur_dioxide"),
            }

            # Extract and aggregate hourly data into daily maximums
            hourly_data = data.get("hourly", {})
            hourly_times = hourly_data.get("time", [])
            hourly_aqi = hourly_data.get("european_aqi", [])
            hourly_pm25 = hourly_data.get("pm2_5", [])
            hourly_pm10 = hourly_data.get("pm10", [])

            # Aggregate into daily max values
            daily_forecast = self._aggregate_to_daily(
                hourly_times, hourly_aqi, hourly_pm25, hourly_pm10
            )

            return {
                "current": current_aqi,
                "daily_forecast": daily_forecast,
            }

        except aiohttp.ClientError as err:
            raise AirQualityApiError(f"Error communicating with Air Quality API: {err}") from err
        except Exception as err:
            raise AirQualityApiError(f"Unexpected error fetching air quality data: {err}") from err

    def _aggregate_to_daily(
        self,
        hourly_times: list[str],
        hourly_aqi: list[float],
        hourly_pm25: list[float],
        hourly_pm10: list[float],
    ) -> list[dict[str, Any]]:
        """Aggregate hourly data into daily maximums.

        Args:
            hourly_times: List of ISO 8601 datetime strings
            hourly_aqi: List of European AQI values
            hourly_pm25: List of PM2.5 values
            hourly_pm10: List of PM10 values

        Returns:
            List of daily aggregated data (max values per day)
        """
        from datetime import datetime

        if not hourly_times or not hourly_aqi:
            return []

        daily_data = {}

        for i, time_str in enumerate(hourly_times):
            # Parse datetime and extract date
            dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            date_key = dt.date().isoformat()

            # Initialize day if not exists
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "aqi_max": None,
                    "pm25_max": None,
                    "pm10_max": None,
                }

            # Update max values for the day
            if i < len(hourly_aqi) and hourly_aqi[i] is not None:
                current_max = daily_data[date_key]["aqi_max"]
                if current_max is None or hourly_aqi[i] > current_max:
                    daily_data[date_key]["aqi_max"] = hourly_aqi[i]

            if i < len(hourly_pm25) and hourly_pm25[i] is not None:
                current_max = daily_data[date_key]["pm25_max"]
                if current_max is None or hourly_pm25[i] > current_max:
                    daily_data[date_key]["pm25_max"] = hourly_pm25[i]

            if i < len(hourly_pm10) and hourly_pm10[i] is not None:
                current_max = daily_data[date_key]["pm10_max"]
                if current_max is None or hourly_pm10[i] > current_max:
                    daily_data[date_key]["pm10_max"] = hourly_pm10[i]

        # Convert to sorted list (by date)
        return [daily_data[date] for date in sorted(daily_data.keys())]
