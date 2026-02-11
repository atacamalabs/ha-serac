"""Sensor platform for Serac integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any
from zoneinfo import ZoneInfo

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
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    ATTRIBUTION,
    CONF_ENTITY_PREFIX,
    CONF_LOCATION_NAME,
    CONF_MASSIF_NAME,
    DOMAIN,
    MANUFACTURER,
    SENSOR_TYPE_AVALANCHE_ACCIDENTAL,
    SENSOR_TYPE_AVALANCHE_BULLETIN_DATE,
    SENSOR_TYPE_AVALANCHE_NATURAL,
    SENSOR_TYPE_AVALANCHE_RISK_HIGH_ALT,
    SENSOR_TYPE_AVALANCHE_RISK_LOW_ALT,
    SENSOR_TYPE_AVALANCHE_RISK_TODAY,
    SENSOR_TYPE_AVALANCHE_RISK_TOMORROW,
    SENSOR_TYPE_AVALANCHE_SUMMARY,
    SENSOR_TYPE_CLOUD_COVERAGE,
    SENSOR_TYPE_ELEVATION,
    SENSOR_TYPE_EUROPEAN_AQI,
    SENSOR_TYPE_HUMIDITY,
    SENSOR_TYPE_NITROGEN_DIOXIDE,
    SENSOR_TYPE_OZONE,
    SENSOR_TYPE_PM10,
    SENSOR_TYPE_PM2_5,
    SENSOR_TYPE_SULPHUR_DIOXIDE,
    SENSOR_TYPE_TEMPERATURE_CURRENT,
    SENSOR_TYPE_WIND_SPEED_CURRENT,
    SENSOR_TYPE_WIND_DIRECTION_CURRENT,
    SENSOR_TYPE_WIND_GUST_CURRENT,
    SENSOR_TYPE_IS_DAY,
    SENSOR_TYPE_PRECIPITATION_CURRENT,
    SENSOR_TYPE_RAIN_CURRENT,
    SENSOR_TYPE_SHOWERS_CURRENT,
    SENSOR_TYPE_SNOWFALL_CURRENT,
)
from .coordinator import AromeCoordinator, BraCoordinator

_LOGGER = logging.getLogger(__name__)


def _parse_bra_datetime(date_str: str | None) -> datetime | None:
    """Parse BRA datetime string as Europe/Paris time and convert to UTC.

    BRA dates are in format '2026-02-11 16:00:00' without timezone.
    The API is French (Météo-France), so times are in Europe/Paris timezone.
    We convert to UTC for Home Assistant storage.
    """
    if not date_str:
        return None
    try:
        # Parse the datetime string
        dt = datetime.fromisoformat(date_str)
        # Add Europe/Paris timezone (this is the source timezone)
        dt_paris = dt.replace(tzinfo=ZoneInfo("Europe/Paris"))
        # Convert to UTC for storage
        return dt_paris.astimezone(dt_util.UTC)
    except (ValueError, AttributeError) as err:
        _LOGGER.warning("Failed to parse BRA datetime '%s': %s", date_str, err)
        return None


@dataclass
class SeracSensorDescription(SensorEntityDescription):
    """Class describing Serac sensor entities."""

    value_fn: Callable[[dict[str, Any]], StateType] = None
    extra_attributes_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


# Static sensors (not dependent on weather updates)
STATIC_SENSORS: tuple[SeracSensorDescription, ...] = (
    SeracSensorDescription(
        key=SENSOR_TYPE_ELEVATION,
        name="Elevation",
        native_unit_of_measurement=UnitOfLength.METERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("elevation"),
    ),
)

# Current weather sensors
CURRENT_SENSORS: tuple[SeracSensorDescription, ...] = (
    SeracSensorDescription(
        key=SENSOR_TYPE_TEMPERATURE_CURRENT,
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("current", {}).get("temperature"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_HUMIDITY,
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("current", {}).get("humidity"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_IS_DAY,
        name="Is Day",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:weather-sunny",
        value_fn=lambda data: "day" if data.get("current", {}).get("is_day") else "night",
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_WIND_SPEED_CURRENT,
        name="Wind Speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy",
        value_fn=lambda data: data.get("current", {}).get("wind_speed"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_WIND_DIRECTION_CURRENT,
        name="Wind Direction",
        native_unit_of_measurement="°",
        icon="mdi:compass",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("current", {}).get("wind_bearing"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_WIND_GUST_CURRENT,
        name="Wind Gust",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-windy-variant",
        value_fn=lambda data: data.get("current", {}).get("wind_gust"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_PRECIPITATION_CURRENT,
        name="Precipitation",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-pouring",
        value_fn=lambda data: data.get("current", {}).get("precipitation"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_RAIN_CURRENT,
        name="Rain",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-rainy",
        value_fn=lambda data: data.get("current", {}).get("rain"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_SHOWERS_CURRENT,
        name="Showers",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-partly-rainy",
        value_fn=lambda data: data.get("current", {}).get("showers"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_SNOWFALL_CURRENT,
        name="Snowfall",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:weather-snowy",
        value_fn=lambda data: data.get("current", {}).get("snowfall"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_CLOUD_COVERAGE,
        name="Cloud Coverage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:cloud-percent",
        value_fn=lambda data: data.get("current", {}).get("cloud_coverage"),
    ),
)

# Current air quality sensors
AIR_QUALITY_CURRENT_SENSORS: tuple[SeracSensorDescription, ...] = (
    SeracSensorDescription(
        key=SENSOR_TYPE_EUROPEAN_AQI,
        name="Air Quality Index",
        native_unit_of_measurement="EAQI",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:air-filter",
        value_fn=lambda data: data.get("air_quality", {}).get("current", {}).get("european_aqi"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_PM2_5,
        name="Particulate Matter 2.5",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("air_quality", {}).get("current", {}).get("pm2_5"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_PM10,
        name="Particulate Matter 10",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.PM10,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("air_quality", {}).get("current", {}).get("pm10"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_NITROGEN_DIOXIDE,
        name="Nitrogen Dioxide",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.NITROGEN_DIOXIDE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:molecule",
        value_fn=lambda data: data.get("air_quality", {}).get("current", {}).get("nitrogen_dioxide"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_OZONE,
        name="Ozone",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.OZONE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:molecule",
        value_fn=lambda data: data.get("air_quality", {}).get("current", {}).get("ozone"),
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_SULPHUR_DIOXIDE,
        name="Sulphur Dioxide",
        native_unit_of_measurement="µg/m³",
        device_class=SensorDeviceClass.SULPHUR_DIOXIDE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:molecule",
        value_fn=lambda data: data.get("air_quality", {}).get("current", {}).get("sulphur_dioxide"),
    ),
)


def _create_daily_aqi_sensors() -> tuple[SeracSensorDescription, ...]:
    """Create daily air quality sensors for days 0-4 (5 days)."""
    sensors = []
    day_names = ["Today", "Tomorrow", "Day 2", "Day 3", "Day 4"]

    for day_idx in range(5):
        day_name = day_names[day_idx]

        # European AQI Max
        sensors.append(SeracSensorDescription(
            key=f"european_aqi_max_day{day_idx}",
            name=f"Air Quality Index Max {day_name}",
            native_unit_of_measurement="EAQI",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:air-filter",
            value_fn=lambda data, idx=day_idx: data.get("air_quality", {}).get("daily_forecast", [])[idx].get("aqi_max") if len(data.get("air_quality", {}).get("daily_forecast", [])) > idx else None,
        ))

        # PM2.5 Max
        sensors.append(SeracSensorDescription(
            key=f"pm2_5_max_day{day_idx}",
            name=f"PM2.5 Max {day_name}",
            native_unit_of_measurement="µg/m³",
            device_class=SensorDeviceClass.PM25,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda data, idx=day_idx: data.get("air_quality", {}).get("daily_forecast", [])[idx].get("pm25_max") if len(data.get("air_quality", {}).get("daily_forecast", [])) > idx else None,
        ))

        # PM10 Max
        sensors.append(SeracSensorDescription(
            key=f"pm10_max_day{day_idx}",
            name=f"PM10 Max {day_name}",
            native_unit_of_measurement="µg/m³",
            device_class=SensorDeviceClass.PM10,
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda data, idx=day_idx: data.get("air_quality", {}).get("daily_forecast", [])[idx].get("pm10_max") if len(data.get("air_quality", {}).get("daily_forecast", [])) > idx else None,
        ))

    return tuple(sensors)


DAILY_AQI_SENSORS = _create_daily_aqi_sensors()


def _create_daily_sensors() -> tuple[SeracSensorDescription, ...]:
    """Create daily sensors for days 0, 1, 2."""
    sensors = []
    day_names = ["Today", "Tomorrow", "Day 2"]

    for day_idx in range(3):
        day_name = day_names[day_idx]

        # Wind Speed Max
        sensors.append(SeracSensorDescription(
            key=f"wind_speed_max_day{day_idx}",
            name=f"Wind Speed Max {day_name}",
            native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:weather-windy",
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("wind_speed") if len(data.get("daily_forecast", [])) > idx else None,
        ))

        # Wind Gust Max
        sensors.append(SeracSensorDescription(
            key=f"wind_gust_max_day{day_idx}",
            name=f"Wind Gust Max {day_name}",
            native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
            device_class=SensorDeviceClass.WIND_SPEED,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:weather-windy-variant",
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("wind_gust_speed") if len(data.get("daily_forecast", [])) > idx else None,
        ))

        # Wind Direction
        sensors.append(SeracSensorDescription(
            key=f"wind_direction_day{day_idx}",
            name=f"Wind Direction {day_name}",
            native_unit_of_measurement="°",
            icon="mdi:compass",
            state_class=SensorStateClass.MEASUREMENT,
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("wind_bearing") if len(data.get("daily_forecast", [])) > idx else None,
        ))

        # Sunrise
        sensors.append(SeracSensorDescription(
            key=f"sunrise_day{day_idx}",
            name=f"Sunrise {day_name}",
            device_class=SensorDeviceClass.TIMESTAMP,
            icon="mdi:weather-sunset-up",
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("sunrise") if len(data.get("daily_forecast", [])) > idx else None,
        ))

        # Sunset
        sensors.append(SeracSensorDescription(
            key=f"sunset_day{day_idx}",
            name=f"Sunset {day_name}",
            device_class=SensorDeviceClass.TIMESTAMP,
            icon="mdi:weather-sunset-down",
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("sunset") if len(data.get("daily_forecast", [])) > idx else None,
        ))

        # Sunshine Duration
        sensors.append(SeracSensorDescription(
            key=f"sunshine_duration_day{day_idx}",
            name=f"Sunshine Duration {day_name}",
            native_unit_of_measurement=UnitOfTime.HOURS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:weather-sunny",
            value_fn=lambda data, idx=day_idx: (data.get("daily_forecast", [])[idx].get("sunshine_duration") / 3600) if len(data.get("daily_forecast", [])) > idx and data.get("daily_forecast", [])[idx].get("sunshine_duration") is not None else None,
        ))

        # Daylight Duration
        sensors.append(SeracSensorDescription(
            key=f"daylight_duration_day{day_idx}",
            name=f"Daylight Duration {day_name}",
            native_unit_of_measurement=UnitOfTime.HOURS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:weather-sunset",
            value_fn=lambda data, idx=day_idx: (data.get("daily_forecast", [])[idx].get("daylight_duration") / 3600) if len(data.get("daily_forecast", [])) > idx and data.get("daily_forecast", [])[idx].get("daylight_duration") is not None else None,
        ))

        # UV Index
        sensors.append(SeracSensorDescription(
            key=f"uv_index_day{day_idx}",
            name=f"UV Index {day_name}",
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:weather-sunny-alert",
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("uv_index") if len(data.get("daily_forecast", [])) > idx else None,
        ))

        # Rain Sum
        sensors.append(SeracSensorDescription(
            key=f"rain_sum_day{day_idx}",
            name=f"Rain Sum {day_name}",
            native_unit_of_measurement=UnitOfLength.MILLIMETERS,
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class=SensorStateClass.TOTAL,
            icon="mdi:weather-rainy",
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("rain_sum") if len(data.get("daily_forecast", [])) > idx else None,
        ))

        # Showers Sum
        sensors.append(SeracSensorDescription(
            key=f"showers_sum_day{day_idx}",
            name=f"Showers Sum {day_name}",
            native_unit_of_measurement=UnitOfLength.MILLIMETERS,
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class=SensorStateClass.TOTAL,
            icon="mdi:weather-partly-rainy",
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("showers_sum") if len(data.get("daily_forecast", [])) > idx else None,
        ))

        # Snowfall Sum
        sensors.append(SeracSensorDescription(
            key=f"snowfall_sum_day{day_idx}",
            name=f"Snowfall Sum {day_name}",
            native_unit_of_measurement=UnitOfLength.CENTIMETERS,
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class=SensorStateClass.TOTAL,
            icon="mdi:weather-snowy",
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("snowfall_sum") if len(data.get("daily_forecast", [])) > idx else None,
        ))

        # Precipitation Sum
        sensors.append(SeracSensorDescription(
            key=f"precipitation_sum_day{day_idx}",
            name=f"Precipitation Sum {day_name}",
            native_unit_of_measurement=UnitOfLength.MILLIMETERS,
            device_class=SensorDeviceClass.PRECIPITATION,
            state_class=SensorStateClass.TOTAL,
            icon="mdi:weather-pouring",
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("precipitation_sum") if len(data.get("daily_forecast", [])) > idx else None,
        ))

        # Precipitation Hours
        sensors.append(SeracSensorDescription(
            key=f"precipitation_hours_day{day_idx}",
            name=f"Precipitation Hours {day_name}",
            native_unit_of_measurement=UnitOfTime.HOURS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:clock-outline",
            value_fn=lambda data, idx=day_idx: data.get("daily_forecast", [])[idx].get("precipitation_hours") if len(data.get("daily_forecast", [])) > idx else None,
        ))

    return tuple(sensors)


DAILY_SENSORS = _create_daily_sensors()


# BRA (Avalanche Bulletin) Sensors
BRA_SENSORS: tuple[SeracSensorDescription, ...] = (
    SeracSensorDescription(
        key=SENSOR_TYPE_AVALANCHE_RISK_TODAY,
        name="Avalanche Risk Today",
        icon="mdi:alert-octagon",
        value_fn=lambda data: data.get("risk_max"),
        extra_attributes_fn=lambda data: {
            "risk_comment": data.get("risk_comment"),
            "warning": data.get("warning"),
        } if data.get("has_data") else {},
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_AVALANCHE_RISK_TOMORROW,
        name="Avalanche Risk Tomorrow",
        icon="mdi:alert-octagon-outline",
        value_fn=lambda data: data.get("risk_max_j2"),
        extra_attributes_fn=lambda data: {
            "date": data.get("date_risk_j2"),
            "risk_text": data.get("risk_j2_text"),
            "comment": data.get("risk_j2_comment"),
        } if data.get("has_data") else {},
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_AVALANCHE_ACCIDENTAL,
        name="Avalanche Accidental Risk",
        icon="mdi:skiing",
        value_fn=lambda data: data.get("accidental_text") if data.get("has_data") else None,
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_AVALANCHE_NATURAL,
        name="Avalanche Natural Risk",
        icon="mdi:landslide",
        value_fn=lambda data: data.get("natural_text") if data.get("has_data") else None,
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_AVALANCHE_SUMMARY,
        name="Avalanche Risk Summary",
        icon="mdi:text-box-multiple",
        value_fn=lambda data: data.get("summary") if data.get("has_data") else None,
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_AVALANCHE_BULLETIN_DATE,
        name="Avalanche Bulletin Date",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:calendar-clock",
        value_fn=lambda data: _parse_bra_datetime(data.get("bulletin_date")) if data.get("has_data") else None,
        extra_attributes_fn=lambda data: {
            "massif": data.get("massif_name"),
        } if data.get("has_data") else {},
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_AVALANCHE_RISK_HIGH_ALT,
        name="Avalanche Risk High Altitude",
        icon="mdi:image-filter-hdr",
        value_fn=lambda data: data.get("risk_high_altitude") if data.get("has_data") else None,
        extra_attributes_fn=lambda data: {
            "altitude_limit": data.get("altitude_limit"),
        } if data.get("has_data") and data.get("altitude_limit") else {},
    ),
    SeracSensorDescription(
        key=SENSOR_TYPE_AVALANCHE_RISK_LOW_ALT,
        name="Avalanche Risk Low Altitude",
        icon="mdi:terrain",
        value_fn=lambda data: data.get("risk_low_altitude") if data.get("has_data") else None,
        extra_attributes_fn=lambda data: {
            "altitude_limit": data.get("altitude_limit"),
        } if data.get("has_data") and data.get("altitude_limit") else {},
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Serac sensors from a config entry."""
    coordinator: AromeCoordinator = hass.data[DOMAIN][entry.entry_id]["arome_coordinator"]
    location_name = entry.data[CONF_LOCATION_NAME]
    entity_prefix = entry.data[CONF_ENTITY_PREFIX]
    latitude = entry.data[CONF_LATITUDE]
    longitude = entry.data[CONF_LONGITUDE]

    # Create all sensors
    entities = []

    # Add static sensors (elevation)
    for description in STATIC_SENSORS:
        entities.append(SeracSensor(
            coordinator, description, location_name, entity_prefix, latitude, longitude
        ))

    # Add current weather sensors
    for description in CURRENT_SENSORS:
        entities.append(SeracSensor(
            coordinator, description, location_name, entity_prefix, latitude, longitude
        ))

    # Add daily sensors
    for description in DAILY_SENSORS:
        entities.append(SeracSensor(
            coordinator, description, location_name, entity_prefix, latitude, longitude
        ))

    # Add current air quality sensors
    for description in AIR_QUALITY_CURRENT_SENSORS:
        entities.append(SeracSensor(
            coordinator, description, location_name, entity_prefix, latitude, longitude
        ))

    # Add daily air quality sensors
    for description in DAILY_AQI_SENSORS:
        entities.append(SeracSensor(
            coordinator, description, location_name, entity_prefix, latitude, longitude
        ))

    # Add BRA (avalanche) sensors for each massif
    bra_coordinators = hass.data[DOMAIN][entry.entry_id].get("bra_coordinators", {})
    for massif_id, bra_coordinator in bra_coordinators.items():
        massif_name = bra_coordinator.massif_name
        for description in BRA_SENSORS:
            entities.append(BraSensor(
                bra_coordinator, description, location_name, entity_prefix, latitude, longitude, massif_id, massif_name
            ))

    async_add_entities(entities, True)


class SeracSensor(CoordinatorEntity[AromeCoordinator], SensorEntity):
    """Sensor entity for Serac integration."""

    entity_description: SeracSensorDescription
    _attr_has_entity_name = False
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: AromeCoordinator,
        description: SeracSensorDescription,
        location_name: str,
        entity_prefix: str,
        latitude: float,
        longitude: float,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: Data coordinator
            description: Sensor entity description
            location_name: Name of the location
            entity_prefix: Prefix for entity ID
            latitude: Location latitude
            longitude: Location longitude
        """
        super().__init__(coordinator)
        self.entity_description = description
        self._location_name = location_name
        self._entity_prefix = entity_prefix
        self._latitude = latitude
        self._longitude = longitude

        # Set entity_id using new pattern: sensor.serac_{prefix}_{sensor_type}
        self.entity_id = f"sensor.serac_{entity_prefix}_{description.key}"

        # Unique ID uses coordinates for uniqueness
        self._attr_unique_id = f"serac_{latitude}_{longitude}_{description.key}"
        self._attr_name = description.name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"serac_{self._latitude}_{self._longitude}")},
            name=f"{self._location_name} (Serac)",
            manufacturer=MANUFACTURER,
            model="Mountain Weather Station",
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
        # Sensor is available if coordinator has data and value is not None
        return self.coordinator.last_update_success and self.native_value is not None


class BraSensor(CoordinatorEntity[BraCoordinator], SensorEntity):
    """Sensor entity for BRA avalanche bulletins."""

    entity_description: SeracSensorDescription
    _attr_has_entity_name = False
    _attr_attribution = "Data from Météo-France BRA"

    def __init__(
        self,
        coordinator: BraCoordinator,
        description: SeracSensorDescription,
        location_name: str,
        entity_prefix: str,
        latitude: float,
        longitude: float,
        massif_id: int,
        massif_name: str,
    ) -> None:
        """Initialize the BRA sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._location_name = location_name
        self._entity_prefix = entity_prefix
        self._latitude = latitude
        self._longitude = longitude
        self._massif_id = massif_id
        self._massif_name = massif_name

        # Create massif slug for entity_id (lowercase, replace spaces/hyphens with underscores)
        massif_slug = massif_name.lower().replace(" ", "_").replace("-", "_")

        # Set entity_id using new pattern: sensor.serac_{prefix}_{massif}_{sensor_type}
        self.entity_id = f"sensor.serac_{entity_prefix}_{massif_slug}_{description.key}"

        # Unique ID uses coordinates and massif_id for uniqueness
        self._attr_unique_id = f"serac_{latitude}_{longitude}_{massif_id}_{description.key}"

        # Name includes massif
        self._attr_name = f"{description.name} - {massif_name}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"serac_{self._latitude}_{self._longitude}_massif_{self._massif_id}")},
            name=f"{self._location_name} - {self._massif_name} (Serac)",
            manufacturer=MANUFACTURER,
            model="BRA Avalanche Bulletin",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if not self.coordinator.data or not self.coordinator.data.get("has_data"):
            return {}

        # Get base attributes from description
        if hasattr(self.entity_description, "extra_attributes_fn") and self.entity_description.extra_attributes_fn is not None:
            attrs = self.entity_description.extra_attributes_fn(self.coordinator.data)
            if attrs:
                return attrs

        return {}

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        # Check if data is available
        if not self.coordinator.data.get("has_data"):
            return None

        value = self.entity_description.value_fn(self.coordinator.data)

        # Handle datetime objects
        if isinstance(value, datetime):
            return value

        return value

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # BRA sensor is available if coordinator succeeded and has data
        if not self.coordinator.last_update_success:
            return False

        # If data exists but has_data is False (out of season), mark unavailable
        if self.coordinator.data and not self.coordinator.data.get("has_data"):
            return False

        return True
