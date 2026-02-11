"""Open-Meteo API client for weather data."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class OpenMeteoApiError(Exception):
    """Exception raised for Open-Meteo API errors."""


class OpenMeteoClient:
    """Client for Open-Meteo API (uses Météo-France models for France)."""

    def __init__(
        self,
        latitude: float,
        longitude: float,
    ) -> None:
        """Initialize the Open-Meteo client.

        Args:
            latitude: Location latitude
            longitude: Location longitude
        """
        self._latitude = latitude
        self._longitude = longitude
        self._base_url = "https://api.open-meteo.com/v1/forecast"

    async def async_get_current_weather(self) -> dict[str, Any]:
        """Get current weather conditions.

        Returns:
            Dictionary with current weather data
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "latitude": self._latitude,
                    "longitude": self._longitude,
                    "current": "temperature_2m,relative_humidity_2m,pressure_msl,"
                    "wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover,"
                    "is_day,precipitation,rain,showers,snowfall",
                    "timezone": "auto",
                }

                async with session.get(
                    self._base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    current = data.get("current", {})

                    return {
                        "condition": self._map_condition(current),
                        "temperature": current.get("temperature_2m"),
                        "humidity": current.get("relative_humidity_2m"),
                        "pressure": current.get("pressure_msl"),
                        "wind_speed": current.get("wind_speed_10m"),
                        "wind_bearing": current.get("wind_direction_10m"),
                        "wind_gust": current.get("wind_gusts_10m"),
                        "cloud_coverage": current.get("cloud_cover"),
                        "is_day": current.get("is_day", 1) == 1,
                        "precipitation": current.get("precipitation"),
                        "rain": current.get("rain"),
                        "showers": current.get("showers"),
                        "snowfall": current.get("snowfall"),
                        "visibility": None,  # Not provided by Open-Meteo
                        "timestamp": current.get("time"),
                    }

        except aiohttp.ClientError as err:
            _LOGGER.error("Network error getting current weather: %s", err)
            raise OpenMeteoApiError(f"Failed to get current weather (network): {err}") from err
        except Exception as err:
            _LOGGER.error("Error getting current weather: %s (type: %s)", err, type(err).__name__)
            raise OpenMeteoApiError(f"Failed to get current weather: {err}") from err

    async def async_get_daily_forecast(self) -> list[dict[str, Any]]:
        """Get daily forecast for 8 days (today + 7 next days).

        Returns:
            List of daily forecast dictionaries
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "latitude": self._latitude,
                    "longitude": self._longitude,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                    "weather_code,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,"
                    "sunrise,sunset,sunshine_duration,daylight_duration,uv_index_max,"
                    "rain_sum,showers_sum,snowfall_sum,precipitation_hours",
                    "timezone": "auto",
                    "forecast_days": 8,
                }

                async with session.get(
                    self._base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    daily = data.get("daily", {})
                    daily_forecasts = []

                    times = daily.get("time", [])
                    for i in range(len(times)):
                        dt = datetime.fromisoformat(times[i])

                        # Parse sunrise/sunset
                        sunrise_str = daily.get("sunrise", [None])[i]
                        sunset_str = daily.get("sunset", [None])[i]
                        sunrise = datetime.fromisoformat(sunrise_str) if sunrise_str else None
                        sunset = datetime.fromisoformat(sunset_str) if sunset_str else None

                        # Ensure timezone awareness for sunrise/sunset
                        if sunrise and sunrise.tzinfo is None:
                            sunrise = sunrise.replace(tzinfo=timezone.utc)
                        if sunset and sunset.tzinfo is None:
                            sunset = sunset.replace(tzinfo=timezone.utc)

                        daily_forecasts.append({
                            "datetime": dt.isoformat(),
                            "temperature": daily["temperature_2m_max"][i],
                            "templow": daily["temperature_2m_min"][i],
                            "precipitation_sum": daily["precipitation_sum"][i],
                            "precipitation": daily["precipitation_sum"][i],  # Keep for backward compatibility
                            "precipitation_probability": None,  # Not in daily
                            "condition": self._map_weather_code(daily.get("weather_code", [None])[i]),
                            "wind_speed": daily.get("wind_speed_10m_max", [None])[i],
                            "wind_gust_speed": daily.get("wind_gusts_10m_max", [None])[i],
                            "wind_bearing": daily.get("wind_direction_10m_dominant", [None])[i],
                            "sunrise": sunrise,
                            "sunset": sunset,
                            "sunshine_duration": daily.get("sunshine_duration", [None])[i],
                            "daylight_duration": daily.get("daylight_duration", [None])[i],
                            "uv_index": daily.get("uv_index_max", [None])[i],
                            "rain_sum": daily.get("rain_sum", [None])[i],
                            "showers_sum": daily.get("showers_sum", [None])[i],
                            "snowfall_sum": daily.get("snowfall_sum", [None])[i],
                            "precipitation_hours": daily.get("precipitation_hours", [None])[i],
                        })

                    return daily_forecasts

        except Exception as err:
            _LOGGER.error("Error getting daily forecast: %s", err)
            raise OpenMeteoApiError(f"Failed to get daily forecast: {err}") from err

    async def async_get_hourly_forecast(self) -> list[dict[str, Any]]:
        """Get hourly forecast for 48 hours (future hours only).

        Returns:
            List of hourly forecast dictionaries
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "latitude": self._latitude,
                    "longitude": self._longitude,
                    "hourly": "temperature_2m,precipitation,weather_code,cloud_cover,"
                    "wind_speed_10m,wind_gusts_10m,wind_direction_10m",
                    "timezone": "auto",
                    "forecast_days": 3,  # 72 hours to ensure we get 48+
                }

                async with session.get(
                    self._base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    hourly = data.get("hourly", {})
                    hourly_forecasts = []

                    times = hourly.get("time", [])

                    # Get current time for comparison
                    # Parse first datetime to get timezone info
                    if not times:
                        return []

                    first_dt = datetime.fromisoformat(times[0])
                    # Use the same timezone as the forecast data
                    if first_dt.tzinfo:
                        now = datetime.now(tz=first_dt.tzinfo)
                    else:
                        now = datetime.now()

                    for i in range(len(times)):
                        dt = datetime.fromisoformat(times[i])

                        # Only include future hours
                        if dt > now:
                            hourly_forecasts.append({
                                "datetime": dt,  # Keep as datetime for processing
                                "temperature": hourly["temperature_2m"][i],
                                "precipitation": hourly["precipitation"][i],
                                "precipitation_probability": None,  # Not in hourly
                                "condition": self._map_weather_code(hourly.get("weather_code", [None])[i]),
                                "wind_speed": hourly["wind_speed_10m"][i],
                                "wind_gust_speed": hourly["wind_gusts_10m"][i],
                                "wind_bearing": hourly["wind_direction_10m"][i],
                                "cloud_coverage": hourly.get("cloud_cover", [None])[i],
                            })

                            # Stop after collecting 48 future hours
                            if len(hourly_forecasts) >= 48:
                                break

                    return hourly_forecasts

        except Exception as err:
            _LOGGER.error("Error getting hourly forecast: %s", err)
            raise OpenMeteoApiError(f"Failed to get hourly forecast: {err}") from err

    async def async_get_hourly_6h(self) -> list[dict[str, Any]]:
        """Get hourly forecast for next 6 hours.

        Returns:
            List of hourly forecast dictionaries for next 6 hours
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "latitude": self._latitude,
                    "longitude": self._longitude,
                    "hourly": "temperature_2m,wind_speed_10m,wind_gusts_10m,cloud_cover,"
                    "snowfall,rain,precipitation",
                    "timezone": "auto",
                    "forecast_days": 1,  # Only need today's data
                }

                async with session.get(
                    self._base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    hourly = data.get("hourly", {})
                    hourly_6h = []

                    times = hourly.get("time", [])

                    # Get current time for comparison
                    if not times:
                        return []

                    first_dt = datetime.fromisoformat(times[0])
                    # Use the same timezone as the forecast data
                    if first_dt.tzinfo:
                        now = datetime.now(tz=first_dt.tzinfo)
                    else:
                        now = datetime.now()

                    hour_count = 0
                    for i in range(len(times)):
                        dt = datetime.fromisoformat(times[i])

                        # Only include future hours
                        if dt > now:
                            hour_count += 1
                            hourly_6h.append({
                                "hour": hour_count,
                                "datetime": dt,
                                "temperature": hourly["temperature_2m"][i],
                                "wind_speed": hourly["wind_speed_10m"][i],
                                "wind_gust": hourly["wind_gusts_10m"][i],
                                "cloud_cover": hourly.get("cloud_cover", [None])[i],
                                "snowfall": hourly.get("snowfall", [None])[i],
                                "rain": hourly.get("rain", [None])[i],
                                "precipitation": hourly.get("precipitation", [None])[i],
                            })

                            # Stop after collecting 6 future hours
                            if hour_count >= 6:
                                break

                    return hourly_6h

        except Exception as err:
            _LOGGER.error("Error getting hourly 6h forecast: %s", err)
            raise OpenMeteoApiError(f"Failed to get hourly 6h forecast: {err}") from err

    async def async_get_additional_data(self) -> dict[str, Any]:
        """Get additional weather data (elevation only).

        Returns:
            Dictionary with elevation data
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "latitude": self._latitude,
                    "longitude": self._longitude,
                    "timezone": "auto",
                }

                async with session.get(
                    self._base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    # Get elevation from response
                    elevation = data.get("elevation", 0)

                    return {
                        "elevation": elevation,
                    }

        except Exception as err:
            _LOGGER.error("Error getting additional data: %s", err)
            raise OpenMeteoApiError(f"Failed to get additional data: {err}") from err

    @staticmethod
    def _map_weather_code(code: int | None) -> str:
        """Map Open-Meteo weather code to Home Assistant condition.

        Args:
            code: WMO weather code

        Returns:
            Home Assistant weather condition
        """
        if code is None:
            return "unknown"

        # WMO Weather interpretation codes
        # https://open-meteo.com/en/docs
        if code == 0:
            return "sunny"
        elif code in (1, 2):
            return "partlycloudy"
        elif code == 3:
            return "cloudy"
        elif code in (45, 48):
            return "fog"
        elif code in (51, 53, 55, 56, 57):
            return "rainy"
        elif code in (61, 63, 65, 66, 67, 80, 81, 82):
            return "pouring"
        elif code in (71, 73, 75, 77, 85, 86):
            return "snowy"
        elif code in (95, 96, 99):
            return "lightning-rainy"
        else:
            return "partlycloudy"

    @staticmethod
    def _map_condition(current: dict) -> str:
        """Map current conditions to HA weather condition.

        Args:
            current: Current weather data

        Returns:
            Home Assistant weather condition
        """
        # Open-Meteo doesn't provide weather code in current, so we use cloud cover
        cloud_cover = current.get("cloud_cover", 50)

        if cloud_cover < 20:
            return "sunny"
        elif cloud_cover < 50:
            return "partlycloudy"
        else:
            return "cloudy"
