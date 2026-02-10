"""Config flow for Better Mountain Weather integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from meteofrance_api import MeteoFranceClient
from meteofrance_api.helpers import get_warning_text_status_from_indice_color
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_LOCATION_NAME,
    CONF_MASSIF_ID,
    CONF_MASSIF_NAME,
    DOMAIN,
    MASSIFS,
)

_LOGGER = logging.getLogger(__name__)


def _find_nearest_massif(latitude: float, longitude: float) -> tuple[str, str]:
    """Find the nearest massif to the given coordinates.

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Tuple of (massif_id, massif_name)
    """
    from math import radians, cos, sin, asin, sqrt

    def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points."""
        # Convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r

    min_distance = float("inf")
    nearest_massif_id = None
    nearest_massif_name = None

    for massif_id, (massif_name, massif_lat, massif_lon) in MASSIFS.items():
        distance = haversine(latitude, longitude, massif_lat, massif_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_massif_id = massif_id
            nearest_massif_name = massif_name

    return nearest_massif_id, nearest_massif_name


class BetterMountainWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Better Mountain Weather."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - collect GPS coordinates."""
        errors: dict[str, str] = {}

        if user_input is not None:
            latitude = user_input[CONF_LATITUDE]
            longitude = user_input[CONF_LONGITUDE]

            # Validate location and get forecast information
            try:
                _LOGGER.debug(
                    "Validating location: lat=%s, lon=%s",
                    latitude,
                    longitude,
                )

                # Initialize client without authentication (free API)
                client = MeteoFranceClient()
                _LOGGER.debug("MeteoFranceClient initialized successfully")

                # Test coordinates by fetching forecast
                _LOGGER.debug("Fetching forecast for coordinates...")
                forecast = await asyncio.to_thread(
                    client.get_forecast,
                    latitude,
                    longitude,
                )
                _LOGGER.debug("Forecast retrieved successfully")

                # Get location name from forecast or use coordinates
                if hasattr(forecast, 'position') and forecast.position:
                    location_name = forecast.position.get('name', f"Location {latitude:.2f}, {longitude:.2f}")
                else:
                    location_name = f"Location {latitude:.2f}, {longitude:.2f}"

                # Store location data
                self._data[CONF_LATITUDE] = latitude
                self._data[CONF_LONGITUDE] = longitude
                self._data[CONF_LOCATION_NAME] = location_name

                # Find nearest massif for Phase 2
                massif_id, massif_name = _find_nearest_massif(latitude, longitude)
                self._data[CONF_MASSIF_ID] = massif_id
                self._data[CONF_MASSIF_NAME] = massif_name

                # Create the config entry
                await self.async_set_unique_id(
                    f"{latitude}_{longitude}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=location_name,
                    data=self._data,
                )

            except Exception as err:
                _LOGGER.error("Error validating location: %s", err, exc_info=True)
                errors["base"] = "cannot_connect"

        # Show the form with default values from HA configuration
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_LATITUDE,
                    default=self.hass.config.latitude
                ): cv.latitude,
                vol.Required(
                    CONF_LONGITUDE,
                    default=self.hass.config.longitude
                ): cv.longitude,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "location_info": "Enter GPS coordinates for your mountain location",
            },
        )
