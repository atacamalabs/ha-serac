"""AROME API client wrapper for meteofrance-api."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
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
                "condition": self._map_condition(current.weather_description),
                "temperature": current.temperature,
                "humidity": current.relative_humidity,
                "pressure": current.sea_level_pressure,
                "wind_speed": current.wind_speed,
                "wind_bearing": current.wind_direction,
                "wind_gust": current.wind_gust,
                "cloud_coverage": current.cloud_cover,
                "visibility": None,  # Not provided by meteofrance-api
                "timestamp": current.timestamp,
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
                daily_forecasts.append({
                    "datetime": daily.timestamp.isoformat(),
                    "temperature": daily.temperature_max,
                    "templow": daily.temperature_min,
                    "precipitation": daily.total_precipitation,
                    "precipitation_probability": daily.precipitation_probability,
                    "condition": self._map_condition(daily.weather_description),
                    "wind_speed": daily.wind_speed,
                    "wind_gust_speed": daily.wind_gust,
                    "wind_bearing": daily.wind_direction,
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

            for hourly in forecast.hourly_forecast:
                hourly_forecasts.append({
                    "datetime": hourly.timestamp.isoformat(),
                    "temperature": hourly.temperature,
                    "precipitation": hourly.precipitation,
                    "precipitation_probability": hourly.precipitation_probability,
                    "condition": self._map_condition(hourly.weather_description),
                    "wind_speed": hourly.wind_speed,
                    "wind_gust_speed": hourly.wind_gust,
                    "wind_bearing": hourly.wind_direction,
                    "cloud_coverage": hourly.cloud_cover,
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
            current = forecast.current_forecast
            position = forecast.position

            # Calculate sunrise/sunset (simplified - in production use proper library)
            # For now, using reasonable defaults - this should be improved
            now = datetime.now()
            sunrise = now.replace(hour=7, minute=0, second=0, microsecond=0)
            sunset = now.replace(hour=19, minute=0, second=0, microsecond=0)

            return {
                "elevation": position.get("altitude", 0) if position else 0,
                "uv_index": getattr(current, "uv_index", 0),
                "air_quality": None,  # Not provided by meteofrance-api
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
