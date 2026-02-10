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
                    "wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover",
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
                        "visibility": None,  # Not provided by Open-Meteo
                        "timestamp": current.get("time"),
                    }

        except Exception as err:
            _LOGGER.error("Error getting current weather: %s", err)
            raise OpenMeteoApiError(f"Failed to get current weather: {err}") from err

    async def async_get_daily_forecast(self) -> list[dict[str, Any]]:
        """Get daily forecast for 7 days.

        Returns:
            List of daily forecast dictionaries
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "latitude": self._latitude,
                    "longitude": self._longitude,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,"
                    "weather_code,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant",
                    "timezone": "auto",
                    "forecast_days": 7,
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

                        daily_forecasts.append({
                            "datetime": dt.isoformat(),
                            "temperature": daily["temperature_2m_max"][i],
                            "templow": daily["temperature_2m_min"][i],
                            "precipitation": daily["precipitation_sum"][i],
                            "precipitation_probability": None,  # Not in daily
                            "condition": self._map_weather_code(daily.get("weather_code", [None])[i]),
                            "wind_speed": daily.get("wind_speed_10m_max", [None])[i],
                            "wind_gust_speed": daily.get("wind_gusts_10m_max", [None])[i],
                            "wind_bearing": daily.get("wind_direction_10m_dominant", [None])[i],
                        })

                    return daily_forecasts

        except Exception as err:
            _LOGGER.error("Error getting daily forecast: %s", err)
            raise OpenMeteoApiError(f"Failed to get daily forecast: {err}") from err

    async def async_get_hourly_forecast(self) -> list[dict[str, Any]]:
        """Get hourly forecast for 48 hours.

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
                    for i in range(min(48, len(times))):  # Limit to 48 hours
                        dt = datetime.fromisoformat(times[i])

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

                    return hourly_forecasts

        except Exception as err:
            _LOGGER.error("Error getting hourly forecast: %s", err)
            raise OpenMeteoApiError(f"Failed to get hourly forecast: {err}") from err

    async def async_get_additional_data(self) -> dict[str, Any]:
        """Get additional weather data (elevation, UV, sun times).

        Returns:
            Dictionary with additional weather data
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "latitude": self._latitude,
                    "longitude": self._longitude,
                    "daily": "sunrise,sunset,uv_index_max",
                    "timezone": "auto",
                    "forecast_days": 1,
                }

                async with session.get(
                    self._base_url, params=params, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    daily = data.get("daily", {})

                    # Get elevation from response
                    elevation = data.get("elevation", 0)

                    # Get today's sunrise/sunset
                    sunrise_str = daily.get("sunrise", [None])[0]
                    sunset_str = daily.get("sunset", [None])[0]

                    sunrise = datetime.fromisoformat(sunrise_str) if sunrise_str else None
                    sunset = datetime.fromisoformat(sunset_str) if sunset_str else None

                    # Ensure timezone awareness
                    if sunrise and sunrise.tzinfo is None:
                        sunrise = sunrise.replace(tzinfo=timezone.utc)
                    if sunset and sunset.tzinfo is None:
                        sunset = sunset.replace(tzinfo=timezone.utc)

                    # Fallback if not available
                    if not sunrise:
                        now = datetime.now(tz=timezone.utc)
                        sunrise = now.replace(hour=7, minute=0, second=0, microsecond=0)
                    if not sunset:
                        now = datetime.now(tz=timezone.utc)
                        sunset = now.replace(hour=19, minute=0, second=0, microsecond=0)

                    uv_index = daily.get("uv_index_max", [0])[0]

                    return {
                        "elevation": elevation,
                        "uv_index": uv_index,
                        "sunrise": sunrise,
                        "sunset": sunset,
                    }

        except Exception as err:
            _LOGGER.error("Error getting additional data: %s", err)
            raise OpenMeteoApiError(f"Failed to get additional data: {err}") from err

    def get_today_max_wind(self, hourly_forecasts: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate today's maximum wind speed and gust from hourly forecasts.

        Args:
            hourly_forecasts: List of hourly forecast dictionaries

        Returns:
            Dictionary with max wind speed and gust for today
        """
        today = datetime.now().date()
        max_wind_speed = 0
        max_wind_gust = 0

        for forecast in hourly_forecasts:
            forecast_dt = forecast["datetime"]
            if isinstance(forecast_dt, str):
                forecast_dt = datetime.fromisoformat(forecast_dt)

            forecast_date = forecast_dt.date()

            if forecast_date == today:
                wind = forecast.get("wind_speed") or 0
                gust = forecast.get("wind_gust_speed") or 0
                max_wind_speed = max(max_wind_speed, wind)
                max_wind_gust = max(max_wind_gust, gust)

        return {
            "wind_speed_today_max": max_wind_speed,
            "wind_gust_today_max": max_wind_gust,
        }

    def get_wind_forecasts(self, hourly_forecasts: list[dict[str, Any]]) -> dict[str, Any]:
        """Calculate wind forecasts for tomorrow and day 2 from hourly forecasts.

        Args:
            hourly_forecasts: List of hourly forecast dictionaries

        Returns:
            Dictionary with max wind speed and gust for tomorrow and day 2
        """
        now = datetime.now(tz=timezone.utc)
        today = now.date()
        tomorrow = (now + timedelta(days=1)).date()
        day_after = (now + timedelta(days=2)).date()

        # Initialize max values
        tomorrow_wind = 0
        tomorrow_gust = 0
        day2_wind = 0
        day2_gust = 0

        for forecast in hourly_forecasts:
            forecast_dt = forecast["datetime"]
            if isinstance(forecast_dt, str):
                forecast_dt = datetime.fromisoformat(forecast_dt)

            forecast_date = forecast_dt.date()

            wind_speed = forecast.get("wind_speed") or 0
            wind_gust = forecast.get("wind_gust_speed") or 0

            if forecast_date == tomorrow:
                tomorrow_wind = max(tomorrow_wind, wind_speed)
                tomorrow_gust = max(tomorrow_gust, wind_gust)
            elif forecast_date == day_after:
                day2_wind = max(day2_wind, wind_speed)
                day2_gust = max(day2_gust, wind_gust)

        return {
            "wind_forecast_tomorrow_max": tomorrow_wind,
            "gust_forecast_tomorrow_max": tomorrow_gust,
            "wind_forecast_day2_max": day2_wind,
            "gust_forecast_day2_max": day2_gust,
        }

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
