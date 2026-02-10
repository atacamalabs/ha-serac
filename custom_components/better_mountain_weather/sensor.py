"""Sensor platform for Better Mountain Weather integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    PERCENTAGE,
    UnitOfLength,
    UnitOfSpeed,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_LOCATION_NAME,
    DOMAIN,
    MANUFACTURER,
    SENSOR_TYPE_AIR_QUALITY,
    SENSOR_TYPE_CLOUD_COVERAGE,
    SENSOR_TYPE_ELEVATION,
    SENSOR_TYPE_HUMIDITY,
    SENSOR_TYPE_SUNRISE,
    SENSOR_TYPE_SUNSET,
    SENSOR_TYPE_UV_INDEX,
    SENSOR_TYPE_WIND_GUST_CURRENT,
    SENSOR_TYPE_WIND_GUST_TODAY_MAX,
    SENSOR_TYPE_WIND_SPEED_CURRENT,
    SENSOR_TYPE_WIND_SPEED_TODAY_MAX,
)
from .coordinator import AromeCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class BetterMountainWeatherSensorDescription(SensorEntityDescription):
    """Class describing Better Mountain Weather sensor entities."""

    value_fn: Callable[[dict[str, Any]], StateType] = None


AROME_SENSORS: tuple[BetterMountainWeatherSensorDescription, ...] = (
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_ELEVATION,
        name="Elevation",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("elevation"),
    ),
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_AIR_QUALITY,
        name="Air Quality",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
        value_fn=lambda data: data.get("air_quality"),
    ),
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_UV_INDEX,
        name="UV Index",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-sunny-alert",
        value_fn=lambda data: data.get("uv_index"),
    ),
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_SUNRISE,
        name="Sunrise",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunset-up",
        value_fn=lambda data: data.get("sunrise"),
    ),
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_SUNSET,
        name="Sunset",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunset-down",
        value_fn=lambda data: data.get("sunset"),
    ),
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_CLOUD_COVERAGE,
        name="Cloud Coverage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cloud-percent",
        value_fn=lambda data: data.get("current", {}).get("cloud_coverage"),
    ),
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_HUMIDITY,
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("current", {}).get("humidity"),
    ),
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_WIND_SPEED_CURRENT,
        name="Wind Speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
        value_fn=lambda data: data.get("current", {}).get("wind_speed"),
    ),
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_WIND_GUST_CURRENT,
        name="Wind Gust",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy-variant",
        value_fn=lambda data: data.get("current", {}).get("wind_gust"),
    ),
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_WIND_SPEED_TODAY_MAX,
        name="Wind Speed Today Max",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
        value_fn=lambda data: data.get("wind_speed_today_max"),
    ),
    BetterMountainWeatherSensorDescription(
        key=SENSOR_TYPE_WIND_GUST_TODAY_MAX,
        name="Wind Gust Today Max",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy-variant",
        value_fn=lambda data: data.get("wind_gust_today_max"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Better Mountain Weather sensors from a config entry."""
    coordinator: AromeCoordinator = hass.data[DOMAIN][entry.entry_id]["arome_coordinator"]
    location_name = entry.data[CONF_LOCATION_NAME]
    latitude = entry.data[CONF_LATITUDE]
    longitude = entry.data[CONF_LONGITUDE]

    # Create AROME sensors
    entities = [
        BetterMountainWeatherSensor(
            coordinator,
            description,
            location_name,
            latitude,
            longitude,
        )
        for description in AROME_SENSORS
    ]

    async_add_entities(entities, True)


class BetterMountainWeatherSensor(CoordinatorEntity[AromeCoordinator], SensorEntity):
    """Sensor entity for Better Mountain Weather integration."""

    entity_description: BetterMountainWeatherSensorDescription
    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: AromeCoordinator,
        description: BetterMountainWeatherSensorDescription,
        location_name: str,
        latitude: float,
        longitude: float,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: Data coordinator
            description: Sensor entity description
            location_name: Name of the location
            latitude: Location latitude
            longitude: Location longitude
        """
        super().__init__(coordinator)
        self.entity_description = description
        self._location_name = location_name
        self._latitude = latitude
        self._longitude = longitude
        self._attr_unique_id = f"{DOMAIN}_{latitude}_{longitude}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._latitude}_{self._longitude}")},
            name=f"{self._location_name} Mountain Weather",
            manufacturer=MANUFACTURER,
            model="AROME Forecast",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        value = self.entity_description.value_fn(self.coordinator.data)

        # Handle datetime objects
        if isinstance(value, datetime):
            return value

        return value

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Sensor is available if coordinator has data
        # Air quality sensor may return None, which is expected
        if self.entity_description.key == SENSOR_TYPE_AIR_QUALITY:
            return self.coordinator.last_update_success
        return self.coordinator.last_update_success and self.native_value is not None
