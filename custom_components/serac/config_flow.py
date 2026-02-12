"""Config flow for Serac integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .api.openmeteo_client import OpenMeteoClient, OpenMeteoApiError
from .const import (
    CONF_BRA_TOKEN,
    CONF_ENTITY_PREFIX,
    CONF_LOCATION_NAME,
    CONF_MASSIF_IDS,
    DOMAIN,
    MASSIF_IDS,
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


class SeracConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Serac."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> SeracOptionsFlow:
        """Get the options flow for this handler."""
        return SeracOptionsFlow(config_entry)

    def _validate_prefix(self, prefix: str) -> bool:
        """Validate entity prefix format.

        Args:
            prefix: The prefix to validate

        Returns:
            True if valid, False otherwise
        """
        import re
        # Must be lowercase alphanumeric + underscores, start with letter, 1-20 chars
        return bool(re.match(r'^[a-z][a-z0-9_]{0,19}$', prefix))

    def _suggest_prefix(self, location_name: str) -> str:
        """Suggest a prefix from location name.

        Args:
            location_name: The location name to derive prefix from

        Returns:
            Suggested prefix (lowercase, alphanumeric only)
        """
        import re
        # Take first word, remove special characters, convert to lowercase
        first_word = location_name.split()[0] if location_name else "mountain"
        # Remove accents and special characters
        slug = re.sub(r'[^a-zA-Z0-9]', '', first_word).lower()
        # Ensure it starts with a letter
        if slug and not slug[0].isalpha():
            slug = "m" + slug
        # Limit to 20 characters
        return slug[:20] if slug else "mountain"

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - collect location details."""
        errors: dict[str, str] = {}

        if user_input is not None:
            latitude = user_input[CONF_LATITUDE]
            longitude = user_input[CONF_LONGITUDE]
            location_name = user_input[CONF_LOCATION_NAME].strip()

            # Validate location name is not empty
            if not location_name:
                errors[CONF_LOCATION_NAME] = "required"

            # Validate location and get forecast information
            if not errors:
                try:
                    _LOGGER.debug(
                        "Validating location: lat=%s, lon=%s, name=%s",
                        latitude,
                        longitude,
                        location_name,
                    )

                    # Initialize Open-Meteo client (no authentication needed)
                    client = OpenMeteoClient(latitude=latitude, longitude=longitude)
                    _LOGGER.debug("OpenMeteoClient initialized successfully")

                    # Test coordinates by fetching current weather
                    _LOGGER.debug("Fetching weather for coordinates...")
                    current = await client.async_get_current_weather()
                    _LOGGER.debug("Weather data retrieved successfully")

                    # Store location data
                    self._data[CONF_LATITUDE] = latitude
                    self._data[CONF_LONGITUDE] = longitude
                    self._data[CONF_LOCATION_NAME] = location_name

                    # Proceed to prefix step
                    return await self.async_step_prefix()

                except Exception as err:
                    _LOGGER.error("Error validating location: %s", err, exc_info=True)
                    errors["base"] = "cannot_connect"

        # Show the form with default values from HA configuration
        data_schema = vol.Schema(
            {
                vol.Required(CONF_LOCATION_NAME): str,
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
                "location_name": "Enter a name for this location and its GPS coordinates",
            },
        )

    async def async_step_prefix(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle entity prefix configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            prefix = user_input[CONF_ENTITY_PREFIX].lower().strip()

            # Validate prefix format
            if not self._validate_prefix(prefix):
                errors[CONF_ENTITY_PREFIX] = "invalid_prefix"
            else:
                # Store prefix and proceed to massifs step
                self._data[CONF_ENTITY_PREFIX] = prefix
                return await self.async_step_massifs()

        # Generate suggested prefix from location name
        suggested_prefix = self._suggest_prefix(self._data[CONF_LOCATION_NAME])

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_ENTITY_PREFIX,
                    default=suggested_prefix
                ): str,
            }
        )

        return self.async_show_form(
            step_id="prefix",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "location_name": self._data[CONF_LOCATION_NAME],
                "suggested_prefix": suggested_prefix,
                "example_entity": f"sensor.serac_{suggested_prefix}_temperature",
            },
        )

    async def async_step_massifs(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle massif selection and BRA token."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Store selected massifs (can be empty list)
            selected_massifs = user_input.get(CONF_MASSIF_IDS, [])
            self._data[CONF_MASSIF_IDS] = selected_massifs

            # Store BRA token if provided (optional)
            if user_input.get(CONF_BRA_TOKEN):
                self._data[CONF_BRA_TOKEN] = user_input[CONF_BRA_TOKEN]

            # Create the config entry
            latitude = self._data[CONF_LATITUDE]
            longitude = self._data[CONF_LONGITUDE]

            await self.async_set_unique_id(f"{latitude}_{longitude}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=self._data[CONF_LOCATION_NAME],
                data=self._data,
            )

        # Create massif options for multi-select
        massif_options = {str(num_id): name for num_id, (name, _) in MASSIF_IDS.items()}

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_BRA_TOKEN,
                    description="Météo-France API key for avalanche bulletins (optional)"
                ): str,
                vol.Optional(
                    CONF_MASSIF_IDS,
                    description="Select massifs for avalanche bulletins (requires BRA token)"
                ): cv.multi_select(massif_options),
            }
        )

        return self.async_show_form(
            step_id="massifs",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "massif_info": "Optional: Add Météo-France BRA API token and select massifs for avalanche data. Leave empty to skip avalanche features.",
            },
        )


class SeracOptionsFlow(config_entries.OptionsFlow):
    """Handle Serac options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update config entry with new massifs/token
            new_data = {**self.config_entry.data}

            # Update massif selection
            new_data[CONF_MASSIF_IDS] = user_input.get(CONF_MASSIF_IDS, [])

            # Update BRA token if provided, or remove if empty
            if user_input.get(CONF_BRA_TOKEN):
                new_data[CONF_BRA_TOKEN] = user_input[CONF_BRA_TOKEN].strip()
            elif CONF_BRA_TOKEN in new_data:
                # User cleared token or didn't provide one, remove it
                new_data.pop(CONF_BRA_TOKEN, None)

            # Update config entry
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )

            # Reload the integration to apply changes
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)

            return self.async_create_entry(title="", data={})

        # Get current values
        current_massifs = self.config_entry.data.get(CONF_MASSIF_IDS, [])
        current_token = self.config_entry.data.get(CONF_BRA_TOKEN, "")

        # Create massif options for multi-select
        massif_options = {str(num_id): name for num_id, (name, _) in MASSIF_IDS.items()}

        data_schema = vol.Schema({
            vol.Optional(
                CONF_BRA_TOKEN,
                description={"suggested_value": current_token},
                default=current_token
            ): str,
            vol.Optional(
                CONF_MASSIF_IDS,
                description={"suggested_value": current_massifs},
                default=current_massifs
            ): cv.multi_select(massif_options),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
