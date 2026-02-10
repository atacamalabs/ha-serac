"""AROME API client wrapper for meteofrance-api."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from meteofrance_api import MeteoFranceClient

_LOGGER = logging.getLogger(__name__)


class AromeApiError(Exception):
    """Exception raised for AROME API errors."""


class AromeClient:
    """Wrapper for meteofrance-api focused on AROME data."""

    def __init__(
        self,
        latitude: float,
        longitude: float,
    ) -> None:
        """Initialize the AROME client.

        Args:
            latitude: Location latitude
            longitude: Location longitude
        """
        self._client = MeteoFranceClient()
        self._latitude = latitude
        self._longitude = longitude

    async def async_get_current_weather(self) -> dict[str, Any]:
        """Get current weather conditions.

        Returns:
            Dictionary with current weather data
        """
        try:
            # Run blocking call in executor
            forecast = await asyncio.to_thread(
                self._client.get_forecast,
                self._latitude,
                self._longitude,
            )
            current = forecast.current_forecast

            return {
                "condition": self._map_condition(current.get("weather", {}).get("desc")),
                "temperature": current.get("T", {}).get("value"),
                "humidity": current.get("humidity"),
                "pressure": current.get("sea_level"),
                "wind_speed": current.get("wind", {}).get("speed"),
                "wind_bearing": current.get("wind", {}).get("direction"),
                "wind_gust": current.get("wind", {}).get("gust"),
                "cloud_coverage": current.get("clouds"),
                "visibility": None,  # Not provided by meteofrance-api
                "timestamp": current.get("dt"),
            }
        except Exception as err:
            _LOGGER.error("Error getting current weather: %s", err)
            raise AromeApiError(f"Failed to get current weather: {err}") from err

    async def async_get_daily_forecast(self) -> list[dict[str, Any]]:
        """Get daily forecast for 7 days.

        Returns:
            List of daily forecast dictionaries
        """
        try:
            # Run blocking call in executor
            forecast = await asyncio.to_thread(
                self._client.get_forecast,
                self._latitude,
                self._longitude,
            )
            daily_forecasts = []

            for daily in forecast.daily_forecast:
                dt = datetime.fromtimestamp(daily.get("dt", 0), tz=timezone.utc)

                daily_forecasts.append({
                    "datetime": dt.isoformat(),
                    "temperature": daily.get("T", {}).get("max"),
                    "templow": daily.get("T", {}).get("min"),
                    "precipitation": daily.get("precipitation", {}).get("24h", 0),
                    "precipitation_probability": None,  # Not in dict
                    "condition": self._map_condition(daily.get("weather12H", {}).get("desc")),
                    "wind_speed": None,  # Not in daily forecast
                    "wind_gust_speed": None,  # Not in daily forecast
                    "wind_bearing": None,  # Not in daily forecast
                })

            return daily_forecasts
        except Exception as err:
            _LOGGER.error("Error getting daily forecast: %s", err)
            raise AromeApiError(f"Failed to get daily forecast: {err}") from err

    async def async_get_hourly_forecast(self) -> list[dict[str, Any]]:
        """Get hourly forecast for 48 hours.

        Returns:
            List of hourly forecast dictionaries
        """
        try:
            # Run blocking call in executor
            forecast = await asyncio.to_thread(
                self._client.get_forecast,
                self._latitude,
                self._longitude,
            )
            hourly_forecasts = []

            for hourly in forecast.forecast:  # Use forecast, not hourly_forecast
                dt = datetime.fromtimestamp(hourly.get("dt", 0), tz=timezone.utc)

                hourly_forecasts.append({
                    "datetime": dt.isoformat(),
                    "temperature": hourly.get("T", {}).get("value"),
                    "precipitation": hourly.get("rain", {}).get("1h", 0) + hourly.get("snow", {}).get("1h", 0),
                    "precipitation_probability": None,  # Not in dict
                    "condition": self._map_condition(hourly.get("weather", {}).get("desc")),
                    "wind_speed": hourly.get("wind", {}).get("speed"),
                    "wind_gust_speed": hourly.get("wind", {}).get("gust"),
                    "wind_bearing": hourly.get("wind", {}).get("direction"),
                    "cloud_coverage": hourly.get("clouds"),
                })

            return hourly_forecasts
        except Exception as err:
            _LOGGER.error("Error getting hourly forecast: %s", err)
            raise AromeApiError(f"Failed to get hourly forecast: {err}") from err

    async def async_get_additional_data(self) -> dict[str, Any]:
        """Get additional weather data (UV, air quality, sun times, etc.).

        Returns:
            Dictionary with additional weather data
        """
        try:
            # Get forecast for UV and other data
            # Run blocking call in executor
            forecast = await asyncio.to_thread(
                self._client.get_forecast,
                self._latitude,
                self._longitude,
            )
            position = forecast.position

            # Get today's forecast for UV and sun times
            today = forecast.today_forecast if hasattr(forecast, 'today_forecast') else {}

            # Get sunrise/sunset from today's forecast (timezone-aware)
            if today and "sun" in today:
                sunrise = datetime.fromtimestamp(today["sun"].get("rise", 0), tz=timezone.utc)
                sunset = datetime.fromtimestamp(today["sun"].get("set", 0), tz=timezone.utc)
            else:
                # Fallback to simplified calculation (timezone-aware)
                now = datetime.now(tz=timezone.utc)
                sunrise = now.replace(hour=7, minute=0, second=0, microsecond=0)
                sunset = now.replace(hour=19, minute=0, second=0, microsecond=0)

            return {
                "elevation": position.get("alti", 0) if position else 0,
                "uv_index": today.get("uv", 0) if today else 0,
                "air_quality": None,  # Not provided by Météo-France API
                "sunrise": sunrise,
                "sunset": sunset,
            }
        except Exception as err:
            _LOGGER.error("Error getting additional data: %s", err)
            raise AromeApiError(f"Failed to get additional data: {err}") from err

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
            forecast_date = datetime.fromisoformat(forecast["datetime"]).date()
            if forecast_date == today:
                max_wind_speed = max(max_wind_speed, forecast.get("wind_speed", 0))
                max_wind_gust = max(max_wind_gust, forecast.get("wind_gust_speed", 0))

        return {
            "wind_speed_today_max": max_wind_speed,
            "wind_gust_today_max": max_wind_gust,
        }

    @staticmethod
    def _map_condition(description: str | None) -> str:
        """Map Météo-France weather description to Home Assistant condition.

        Args:
            description: Weather description from API

        Returns:
            Home Assistant weather condition
        """
        if not description:
            return "unknown"

        description_lower = description.lower()

        # Map to HA conditions: clear-night, cloudy, fog, hail, lightning,
        # lightning-rainy, partlycloudy, pouring, rainy, snowy, snowy-rainy,
        # sunny, windy, exceptional

        if "ensoleillé" in description_lower or "soleil" in description_lower:
            return "sunny"
        if "nuageux" in description_lower or "couvert" in description_lower:
            return "cloudy"
        if "peu nuageux" in description_lower or "éclaircies" in description_lower:
            return "partlycloudy"
        if "pluie forte" in description_lower or "averse" in description_lower:
            return "pouring"
        if "pluie" in description_lower:
            return "rainy"
        if "neige" in description_lower:
            return "snowy"
        if "orage" in description_lower:
            return "lightning-rainy"
        if "brouillard" in description_lower or "brume" in description_lower:
            return "fog"
        if "grêle" in description_lower:
            return "hail"
        if "venteux" in description_lower or "vent fort" in description_lower:
            return "windy"

        return "partlycloudy"  # Default fallback
