"""The Better Mountain Weather integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api.arome_client import AromeApiError, AromeClient
from .const import (
    CONF_AROME_TOKEN,
    CONF_BRA_TOKEN,
    CONF_LOCATION_NAME,
    CONF_MASSIF_ID,
    DOMAIN,
)
from .coordinator import AromeCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.WEATHER, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Better Mountain Weather from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry

    Returns:
        True if setup was successful

    Raises:
        ConfigEntryNotReady: If setup should be retried
    """
    # Extract configuration
    arome_token = entry.data[CONF_AROME_TOKEN]
    bra_token = entry.data.get(CONF_BRA_TOKEN)
    latitude = entry.data[CONF_LATITUDE]
    longitude = entry.data[CONF_LONGITUDE]
    location_name = entry.data[CONF_LOCATION_NAME]
    massif_id = entry.data.get(CONF_MASSIF_ID)

    _LOGGER.debug(
        "Setting up Better Mountain Weather for %s (%.4f, %.4f)",
        location_name,
        latitude,
        longitude,
    )

    # Initialize HTTP session
    session = async_get_clientsession(hass)

    # Initialize AROME client
    arome_client = AromeClient(
        api_key=arome_token,
        latitude=latitude,
        longitude=longitude,
        session=session,
    )

    # Initialize AROME coordinator
    arome_coordinator = AromeCoordinator(
        hass=hass,
        client=arome_client,
        location_name=location_name,
    )

    # Fetch initial AROME data
    try:
        await arome_coordinator.async_config_entry_first_refresh()
    except AromeApiError as err:
        _LOGGER.error("Error communicating with AROME API: %s", err)
        raise ConfigEntryNotReady(f"Error communicating with AROME API: {err}") from err
    except Exception as err:
        _LOGGER.error("Unexpected error during AROME setup: %s", err)
        raise ConfigEntryNotReady(f"Unexpected error: {err}") from err

    # Store coordinators in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "arome_coordinator": arome_coordinator,
        "arome_client": arome_client,
    }

    # BRA coordinator will be added in Phase 2
    # if bra_token and massif_id:
    #     bra_client = BraClient(...)
    #     bra_coordinator = BraCoordinator(...)
    #     await bra_coordinator.async_config_entry_first_refresh()
    #     hass.data[DOMAIN][entry.entry_id]["bra_coordinator"] = bra_coordinator
    #     hass.data[DOMAIN][entry.entry_id]["bra_client"] = bra_client

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info(
        "Successfully set up Better Mountain Weather for %s",
        location_name,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry

    Returns:
        True if unload was successful
    """
    _LOGGER.debug("Unloading Better Mountain Weather")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Remove data from hass.data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry
    """
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
