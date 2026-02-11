"""The Serac integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er

from .api.airquality_client import AirQualityClient
from .api.bra_client import BraApiError, BraClient
from .api.openmeteo_client import OpenMeteoApiError, OpenMeteoClient
from .const import (
    CONF_BRA_TOKEN,
    CONF_LOCATION_NAME,
    CONF_MASSIF_ID,
    CONF_MASSIF_IDS,
    CONF_MASSIF_NAME,
    DOMAIN,
    MASSIF_IDS,
)
from .coordinator import AromeCoordinator, BraCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.WEATHER, Platform.SENSOR]


async def async_migrate_entity_ids(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Migrate entity IDs from old naming pattern to new consistent pattern.

    This removes old unavailable sensors and standardizes entity_ids to use
    the coordinate-based pattern: location_{lat}_{lon}_mountain_weather_*
    """
    entity_registry = er.async_get(hass)
    latitude = entry.data[CONF_LATITUDE]
    longitude = entry.data[CONF_LONGITUDE]

    # Format coordinates for entity_id (rounded to 2 decimals, replace dots with underscores)
    lat_rounded = round(latitude, 2)
    lon_rounded = round(longitude, 2)
    lat_str = str(lat_rounded).replace(".", "_")
    lon_str = str(lon_rounded).replace(".", "_")
    new_entity_id_base = f"location_{lat_str}_{lon_str}_mountain_weather"

    # Old sensors to remove completely (no longer exist in code)
    old_sensors_to_remove = [
        "sensor.station_de_ski_orange_mountain_weather_sunrise",
        "sensor.station_de_ski_orange_mountain_weather_sunset",
        "sensor.station_de_ski_orange_mountain_weather_uv_index",
        "sensor.station_de_ski_orange_mountain_weather_wind_speed_today_max",
        "sensor.station_de_ski_orange_mountain_weather_wind_gust_today_max",
        "sensor.station_de_ski_orange_mountain_weather_wind_tomorrow_max",
        "sensor.station_de_ski_orange_mountain_weather_wind_gust_tomorrow_max",
        "sensor.station_de_ski_orange_mountain_weather_wind_day_2_max",
        "sensor.station_de_ski_orange_mountain_weather_wind_gust_day_2_max",
        # Air quality Day 5 and Day 6 sensors (removed in v0.4.2)
        f"sensor.{new_entity_id_base}_air_quality_index_max_day_5",
        f"sensor.{new_entity_id_base}_air_quality_index_max_day_6",
        f"sensor.{new_entity_id_base}_pm2_5_max_day_5",
        f"sensor.{new_entity_id_base}_pm2_5_max_day_6",
        f"sensor.{new_entity_id_base}_pm10_max_day_5",
        f"sensor.{new_entity_id_base}_pm10_max_day_6",
    ]

    # Remove old unavailable sensors
    for entity_id in old_sensors_to_remove:
        entity_entry = entity_registry.async_get(entity_id)
        if entity_entry and entity_entry.config_entry_id == entry.entry_id:
            _LOGGER.info("Removing old unavailable sensor: %s", entity_id)
            entity_registry.async_remove(entity_id)

    # Also handle full precision coordinate format (from previous migration)
    lat_full = str(latitude)
    lon_full = str(longitude)
    old_full_precision_base = f"location_{lat_full.replace('.', '_')}_{lon_full.replace('.', '_')}_mountain_weather"

    # Migrate entity IDs that still use the old "station_de_ski_orange" pattern
    # or full precision coordinates to the new rounded coordinate-based pattern
    old_to_new_mapping = {
        # Old naming pattern
        "weather.station_de_ski_orange_mountain_weather": f"weather.{new_entity_id_base}",
        "sensor.station_de_ski_orange_mountain_weather_elevation": f"sensor.{new_entity_id_base}_elevation",
        "sensor.station_de_ski_orange_mountain_weather_humidity": f"sensor.{new_entity_id_base}_humidity",
        "sensor.station_de_ski_orange_mountain_weather_wind_speed": f"sensor.{new_entity_id_base}_wind_speed",
        "sensor.station_de_ski_orange_mountain_weather_wind_gust": f"sensor.{new_entity_id_base}_wind_gust",
        "sensor.station_de_ski_orange_mountain_weather_cloud_coverage": f"sensor.{new_entity_id_base}_cloud_coverage",
        # Full precision coordinates (migrate to rounded for consistency)
        f"weather.{old_full_precision_base}": f"weather.{new_entity_id_base}",
        f"sensor.{old_full_precision_base}_elevation": f"sensor.{new_entity_id_base}_elevation",
        f"sensor.{old_full_precision_base}_humidity": f"sensor.{new_entity_id_base}_humidity",
        f"sensor.{old_full_precision_base}_wind_speed": f"sensor.{new_entity_id_base}_wind_speed",
        f"sensor.{old_full_precision_base}_wind_gust": f"sensor.{new_entity_id_base}_wind_gust",
        f"sensor.{old_full_precision_base}_cloud_coverage": f"sensor.{new_entity_id_base}_cloud_coverage",
    }

    for old_entity_id, new_entity_id in old_to_new_mapping.items():
        entity_entry = entity_registry.async_get(old_entity_id)
        if entity_entry and entity_entry.config_entry_id == entry.entry_id:
            # Check if target entity_id already exists
            if entity_registry.async_get(new_entity_id):
                _LOGGER.warning(
                    "Cannot migrate %s to %s: target already exists. Removing old entity.",
                    old_entity_id,
                    new_entity_id,
                )
                entity_registry.async_remove(old_entity_id)
            else:
                _LOGGER.info("Migrating entity ID: %s -> %s", old_entity_id, new_entity_id)
                entity_registry.async_update_entity(
                    entity_entry.entity_id,
                    new_entity_id=new_entity_id,
                )

    # Remove old BRA sensors (v0.6.0 - new format includes massif_id in unique_id)
    # Old format: location_{lat}_{lon}_mountain_weather_avalanche_*
    # New format: location_{lat}_{lon}_mountain_weather_{massif_id}_avalanche_*
    for entity_entry in list(entity_registry.entities.values()):
        if entity_entry.config_entry_id == entry.entry_id:
            # Check if this is an old BRA sensor (has avalanche_ but no massif_id in unique_id)
            if (
                entity_entry.unique_id
                and "avalanche_" in entity_entry.unique_id
                and new_entity_id_base in entity_entry.unique_id
                # Check it's the old format (doesn't have massif_id between base and sensor type)
                and not any(f"_{massif_id}_avalanche_" in entity_entry.unique_id for massif_id in range(1, 100))
            ):
                _LOGGER.info(
                    "Removing old BRA sensor (v0.6.0 migration): %s",
                    entity_entry.entity_id,
                )
                entity_registry.async_remove(entity_entry.entity_id)



async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Serac from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry

    Returns:
        True if setup was successful

    Raises:
        ConfigEntryNotReady: If setup should be retried
    """
    # Extract configuration
    bra_token = entry.data.get(CONF_BRA_TOKEN)
    latitude = entry.data[CONF_LATITUDE]
    longitude = entry.data[CONF_LONGITUDE]
    location_name = entry.data[CONF_LOCATION_NAME]

    # Get massif IDs (new format) or fall back to old single massif
    massif_ids = entry.data.get(CONF_MASSIF_IDS, [])
    if not massif_ids and entry.data.get(CONF_MASSIF_ID):
        # Backward compatibility: convert old single massif to list
        massif_ids = [entry.data[CONF_MASSIF_ID]]

    _LOGGER.debug(
        "Setting up Serac for %s (%.4f, %.4f)",
        location_name,
        latitude,
        longitude,
    )

    # Initialize Open-Meteo client (no authentication required)
    arome_client = OpenMeteoClient(
        latitude=latitude,
        longitude=longitude,
    )

    # Initialize Air Quality client
    airquality_client = AirQualityClient(
        latitude=latitude,
        longitude=longitude,
    )

    # Initialize AROME coordinator
    arome_coordinator = AromeCoordinator(
        hass=hass,
        client=arome_client,
        location_name=location_name,
        airquality_client=airquality_client,
    )

    # Fetch initial weather data
    try:
        await arome_coordinator.async_config_entry_first_refresh()
    except OpenMeteoApiError as err:
        _LOGGER.error("Error communicating with Open-Meteo API: %s", err)
        raise ConfigEntryNotReady(f"Error communicating with Open-Meteo API: {err}") from err
    except Exception as err:
        _LOGGER.error("Unexpected error during AROME setup: %s", err)
        raise ConfigEntryNotReady(f"Unexpected error: {err}") from err

    # Store coordinators in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "arome_coordinator": arome_coordinator,
        "arome_client": arome_client,
        "airquality_client": airquality_client,
    }

    # Initialize BRA coordinators for each selected massif
    bra_coordinators = {}
    if bra_token and massif_ids:
        for massif_id in massif_ids:
            # Convert string ID to int if needed (from multi-select)
            if isinstance(massif_id, str):
                massif_id = int(massif_id)

            # Get massif name from MASSIF_IDS
            massif_name = "Unknown"
            if massif_id in MASSIF_IDS:
                massif_name, _ = MASSIF_IDS[massif_id]

            _LOGGER.debug(
                "Setting up BRA coordinator for massif %s (%s)",
                massif_id,
                massif_name,
            )
            try:
                bra_client = BraClient(
                    api_key=bra_token,
                    massif_id=massif_id,
                )
                bra_coordinator = BraCoordinator(
                    hass=hass,
                    client=bra_client,
                    location_name=location_name,
                    massif_id=massif_id,
                    massif_name=massif_name,
                )
                # Fetch initial BRA data
                await bra_coordinator.async_config_entry_first_refresh()
                bra_coordinators[massif_id] = bra_coordinator
                _LOGGER.info(
                    "Successfully set up BRA coordinator for %s (ID: %s)",
                    massif_name,
                    massif_id,
                )
            except BraApiError as err:
                _LOGGER.warning(
                    "Error setting up BRA coordinator for %s (avalanche data unavailable): %s",
                    massif_name,
                    err,
                )
                # Don't fail setup if BRA is unavailable (might be out of season)
            except Exception as err:
                _LOGGER.warning(
                    "Unexpected error setting up BRA coordinator for %s: %s",
                    massif_name,
                    err,
                )

    # Store BRA coordinators
    if bra_coordinators:
        hass.data[DOMAIN][entry.entry_id]["bra_coordinators"] = bra_coordinators

    # Migrate old entity IDs and remove unavailable sensors
    await async_migrate_entity_ids(hass, entry)

    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info(
        "Successfully set up Serac for %s",
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
    _LOGGER.debug("Unloading Serac")

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
