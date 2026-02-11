"""Data update coordinators for Serac integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api.airquality_client import AirQualityApiError, AirQualityClient
from .api.bra_client import BraApiError, BraClient
from .api.openmeteo_client import OpenMeteoApiError, OpenMeteoClient
from .const import AROME_UPDATE_INTERVAL, BRA_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class AromeCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for weather data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: OpenMeteoClient,
        location_name: str,
        airquality_client: AirQualityClient | None = None,
    ) -> None:
        """Initialize the weather coordinator.

        Args:
            hass: Home Assistant instance
            client: Open-Meteo API client
            location_name: Name of the location for logging
            airquality_client: Optional Air Quality API client
        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{location_name}_arome",
            update_interval=AROME_UPDATE_INTERVAL,
        )
        self.client = client
        self.airquality_client = airquality_client
        self.location_name = location_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Open-Meteo API.

        Returns:
            Dictionary containing all weather data

        Raises:
            UpdateFailed: If update fails
        """
        try:
            import asyncio

            _LOGGER.debug("Updating weather data for %s", self.location_name)

            # Fetch all data in parallel for better performance
            tasks = [
                self.client.async_get_current_weather(),
                self.client.async_get_daily_forecast(),
                self.client.async_get_hourly_forecast(),
                self.client.async_get_hourly_6h(),
                self.client.async_get_additional_data(),
            ]

            # Add air quality task if client is available
            if self.airquality_client:
                tasks.append(self.airquality_client.async_get_air_quality())

            # Execute all API calls in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Unpack results
            current_weather = results[0] if not isinstance(results[0], Exception) else {}
            daily_forecast = results[1] if not isinstance(results[1], Exception) else []
            hourly_forecast = results[2] if not isinstance(results[2], Exception) else []
            hourly_6h = results[3] if not isinstance(results[3], Exception) else []
            additional_data = results[4] if not isinstance(results[4], Exception) else {}

            # Handle air quality data
            air_quality_data = {}
            if self.airquality_client and len(results) > 5:
                if isinstance(results[5], Exception):
                    _LOGGER.warning("Error fetching air quality data for %s: %s", self.location_name, results[5])
                else:
                    air_quality_data = results[5]
                    _LOGGER.debug("Successfully fetched air quality data for %s", self.location_name)

            # Check for critical errors
            if isinstance(results[0], Exception):
                raise UpdateFailed(f"Failed to get current weather: {results[0]}") from results[0]
            if isinstance(results[1], Exception):
                raise UpdateFailed(f"Failed to get daily forecast: {results[1]}") from results[1]

            # Combine all data
            data = {
                "current": current_weather,
                "daily_forecast": daily_forecast,
                "hourly_forecast": hourly_forecast,
                "hourly_6h": hourly_6h,
                "elevation": additional_data.get("elevation", 0),
                "air_quality": air_quality_data,
            }

            _LOGGER.debug(
                "Successfully updated weather data for %s: %d daily forecasts, %d hourly forecasts, %d hourly 6h",
                self.location_name,
                len(daily_forecast),
                len(hourly_forecast),
                len(hourly_6h),
            )

            return data

        except OpenMeteoApiError as err:
            _LOGGER.error("Error fetching weather data for %s: %s", self.location_name, err)
            raise UpdateFailed(f"Error fetching weather data: {err}") from err
        except Exception as err:
            _LOGGER.error(
                "Unexpected error fetching weather data for %s: %s",
                self.location_name,
                err,
            )
            raise UpdateFailed(f"Unexpected error: {err}") from err


class BraCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for BRA avalanche bulletin updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: BraClient,
        location_name: str,
        massif_id: int,
        massif_name: str,
    ) -> None:
        """Initialize the BRA coordinator.

        Args:
            hass: Home Assistant instance
            client: BRA API client
            location_name: Name of the location for logging
            massif_id: Numeric ID of the massif
            massif_name: Name of the massif
        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{location_name}_bra",
            update_interval=BRA_UPDATE_INTERVAL,
        )
        self.client = client
        self.location_name = location_name
        self.massif_id = massif_id
        self.massif_name = massif_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from BRA API.

        Returns:
            Dictionary containing BRA avalanche data

        Raises:
            UpdateFailed: If update fails
        """
        try:
            _LOGGER.debug(
                "Updating BRA data for %s (massif %s - %s)",
                self.location_name,
                self.massif_id,
                self.massif_name,
            )

            # Fetch bulletin data
            bulletin_data = await self.client.async_get_bulletin()

            if not bulletin_data.get("has_data"):
                _LOGGER.warning(
                    "No BRA data available for massif %s - may be out of season",
                    self.massif_id,
                )
                return {"has_data": False}

            _LOGGER.debug(
                "Successfully updated BRA data for %s: risk_today=%s, risk_tomorrow=%s",
                self.location_name,
                bulletin_data.get("risk_max"),
                bulletin_data.get("risk_max_j2"),
            )

            return bulletin_data

        except BraApiError as err:
            _LOGGER.error("Error fetching BRA data for %s: %s", self.location_name, err)
            raise UpdateFailed(f"Error fetching BRA data: {err}") from err
        except Exception as err:
            _LOGGER.error(
                "Unexpected error fetching BRA data for %s: %s",
                self.location_name,
                err,
            )
            raise UpdateFailed(f"Unexpected error: {err}") from err
