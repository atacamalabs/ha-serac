"""Data update coordinators for Better Mountain Weather integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api.arome_client import AromeApiError, AromeClient
from .const import AROME_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class AromeCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for AROME weather data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: AromeClient,
        location_name: str,
    ) -> None:
        """Initialize the AROME coordinator.

        Args:
            hass: Home Assistant instance
            client: AROME API client
            location_name: Name of the location for logging
        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{location_name}_arome",
            update_interval=AROME_UPDATE_INTERVAL,
        )
        self.client = client
        self.location_name = location_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from AROME API.

        Returns:
            Dictionary containing all AROME data

        Raises:
            UpdateFailed: If update fails
        """
        try:
            _LOGGER.debug("Updating AROME data for %s", self.location_name)

            # Fetch all data in parallel where possible
            current_weather = await self.client.async_get_current_weather()
            daily_forecast = await self.client.async_get_daily_forecast()
            hourly_forecast = await self.client.async_get_hourly_forecast()
            additional_data = await self.client.async_get_additional_data()

            # Calculate today's max wind from hourly forecast
            today_wind = self.client.get_today_max_wind(hourly_forecast)

            # Combine all data
            data = {
                "current": current_weather,
                "daily_forecast": daily_forecast,
                "hourly_forecast": hourly_forecast,
                "elevation": additional_data.get("elevation", 0),
                "uv_index": additional_data.get("uv_index", 0),
                "air_quality": additional_data.get("air_quality"),
                "sunrise": additional_data.get("sunrise"),
                "sunset": additional_data.get("sunset"),
                "wind_speed_today_max": today_wind.get("wind_speed_today_max", 0),
                "wind_gust_today_max": today_wind.get("wind_gust_today_max", 0),
            }

            _LOGGER.debug(
                "Successfully updated AROME data for %s: %d daily forecasts, %d hourly forecasts",
                self.location_name,
                len(daily_forecast),
                len(hourly_forecast),
            )

            return data

        except AromeApiError as err:
            _LOGGER.error("Error fetching AROME data for %s: %s", self.location_name, err)
            raise UpdateFailed(f"Error fetching AROME data: {err}") from err
        except Exception as err:
            _LOGGER.error(
                "Unexpected error fetching AROME data for %s: %s",
                self.location_name,
                err,
            )
            raise UpdateFailed(f"Unexpected error: {err}") from err


class BraCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for BRA avalanche bulletin updates.

    This will be implemented in Phase 2.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        # client: BraClient,  # Phase 2
        location_name: str,
        massif_id: str,
    ) -> None:
        """Initialize the BRA coordinator.

        Args:
            hass: Home Assistant instance
            location_name: Name of the location for logging
            massif_id: ID of the massif
        """
        from .const import BRA_UPDATE_INTERVAL

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{location_name}_bra",
            update_interval=BRA_UPDATE_INTERVAL,
        )
        # self.client = client  # Phase 2
        self.location_name = location_name
        self.massif_id = massif_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from BRA API.

        This will be implemented in Phase 2.

        Returns:
            Dictionary containing BRA avalanche data

        Raises:
            UpdateFailed: If update fails
        """
        # Phase 2: Implement BRA data fetching
        _LOGGER.debug("BRA coordinator not yet implemented (Phase 2)")
        return {}
