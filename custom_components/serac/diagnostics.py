"""Diagnostics support for Serac."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .const import CONF_BRA_TOKEN, DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry.

    This exports coordinator status and configuration data to help with debugging.
    Sensitive data (BRA API token) is redacted.

    Args:
        hass: Home Assistant instance
        entry: Config entry for this integration

    Returns:
        Dictionary containing diagnostic information
    """
    data = hass.data[DOMAIN].get(entry.entry_id, {})

    # Redact sensitive data from config
    config_data = {**entry.data}
    if CONF_BRA_TOKEN in config_data:
        token = config_data[CONF_BRA_TOKEN]
        # Show only first 4 and last 4 characters
        if token and len(token) > 8:
            config_data[CONF_BRA_TOKEN] = f"{token[:4]}...{token[-4:]}"
        else:
            config_data[CONF_BRA_TOKEN] = "***REDACTED***"

    # Build diagnostics data
    diagnostics_data: dict[str, Any] = {
        "integration_version": entry.version or "unknown",
        "entry_id": entry.entry_id,
        "config_entry": config_data,
        "coordinators": {},
        "statistics": {},
    }

    # AROME coordinator status
    arome_coordinator = data.get("arome_coordinator")
    if arome_coordinator:
        # Get last update time from data timestamp if available
        last_update = None
        if hasattr(arome_coordinator, "last_update_success_time"):
            last_update = arome_coordinator.last_update_success_time
        elif arome_coordinator.data and "timestamp" in arome_coordinator.data:
            last_update = arome_coordinator.data.get("timestamp")

        # Convert to ISO format string if it's a datetime object
        last_update_str = None
        if last_update:
            if isinstance(last_update, str):
                last_update_str = last_update
            elif hasattr(last_update, "isoformat"):
                last_update_str = last_update.isoformat()

        diagnostics_data["coordinators"]["arome"] = {
            "last_update_success": arome_coordinator.last_update_success,
            "last_update_time": last_update_str,
            "update_interval_seconds": (
                arome_coordinator.update_interval.total_seconds()
                if arome_coordinator.update_interval
                else None
            ),
            "has_data": arome_coordinator.data is not None,
            "data_keys": list(arome_coordinator.data.keys()) if arome_coordinator.data else [],
        }

        # Add sample data structure (without actual values)
        if arome_coordinator.data:
            data_structure = {}
            for key, value in arome_coordinator.data.items():
                if isinstance(value, dict):
                    data_structure[key] = f"<dict with {len(value)} keys>"
                elif isinstance(value, list):
                    data_structure[key] = f"<list with {len(value)} items>"
                else:
                    data_structure[key] = type(value).__name__
            diagnostics_data["coordinators"]["arome"]["data_structure"] = data_structure

    # BRA coordinators status
    bra_coordinators = data.get("bra_coordinators", {})
    if bra_coordinators:
        diagnostics_data["coordinators"]["bra"] = {}
        for massif_id, coordinator in bra_coordinators.items():
            # Get last update time from data if available
            last_update = None
            if hasattr(coordinator, "last_update_success_time"):
                last_update = coordinator.last_update_success_time
            elif coordinator.data and "bulletin_date" in coordinator.data:
                last_update = coordinator.data.get("bulletin_date")

            # Convert to ISO format string if it's a datetime object
            last_update_str = None
            if last_update:
                if isinstance(last_update, str):
                    last_update_str = last_update
                elif hasattr(last_update, "isoformat"):
                    last_update_str = last_update.isoformat()

            diagnostics_data["coordinators"]["bra"][str(massif_id)] = {
                "massif_name": coordinator.massif_name,
                "last_update_success": coordinator.last_update_success,
                "last_update_time": last_update_str,
                "update_interval_seconds": (
                    coordinator.update_interval.total_seconds()
                    if coordinator.update_interval
                    else None
                ),
                "has_data": coordinator.data is not None and coordinator.data.get("has_data", False),
                "data_keys": list(coordinator.data.keys()) if coordinator.data else [],
            }

    # Entity statistics
    entity_registry = er.async_get(hass)
    entities = [
        entity
        for entity in entity_registry.entities.values()
        if entity.config_entry_id == entry.entry_id
    ]

    diagnostics_data["statistics"]["total_entities"] = len(entities)
    diagnostics_data["statistics"]["entity_breakdown"] = {
        "weather": sum(1 for e in entities if e.domain == "weather"),
        "sensor": sum(1 for e in entities if e.domain == "sensor"),
    }

    # Count sensor types
    sensor_types = {}
    avalanche_sensors = 0
    weather_sensors = 0
    for entity in entities:
        if entity.domain == "sensor":
            if "avalanche" in entity.entity_id:
                avalanche_sensors += 1
            else:
                weather_sensors += 1

    diagnostics_data["statistics"]["sensor_breakdown"] = {
        "weather_sensors": weather_sensors,
        "avalanche_sensors": avalanche_sensors,
    }

    # Device statistics
    device_registry = dr.async_get(hass)
    devices = [
        device
        for device in device_registry.devices.values()
        if entry.entry_id in device.config_entries
    ]

    diagnostics_data["statistics"]["total_devices"] = len(devices)
    diagnostics_data["statistics"]["device_names"] = [
        device.name for device in devices
    ]

    # Count massif devices
    massif_devices = sum(1 for d in devices if "massif" in str(d.identifiers))
    diagnostics_data["statistics"]["device_breakdown"] = {
        "main_weather_device": 1 if len(devices) > 0 else 0,
        "massif_devices": massif_devices,
    }

    return diagnostics_data
