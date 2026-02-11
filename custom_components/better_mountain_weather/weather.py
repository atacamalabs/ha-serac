"""Weather platform for Better Mountain Weather integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_GUST_SPEED,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_LOCATION_NAME,
    DOMAIN,
    MANUFACTURER,
)
from .coordinator import AromeCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Better Mountain Weather weather entity from a config entry."""
    coordinator: AromeCoordinator = hass.data[DOMAIN][entry.entry_id]["arome_coordinator"]
    location_name = entry.data[CONF_LOCATION_NAME]
    latitude = entry.data[CONF_LATITUDE]
    longitude = entry.data[CONF_LONGITUDE]

    async_add_entities(
        [BetterMountainWeather(coordinator, location_name, latitude, longitude)],
        True,
    )


class BetterMountainWeather(CoordinatorEntity[AromeCoordinator], WeatherEntity):
    """Weather entity for Better Mountain Weather integration."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_native_precipitation_unit = UnitOfLength.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

    def __init__(
        self,
        coordinator: AromeCoordinator,
        location_name: str,
        latitude: float,
        longitude: float,
    ) -> None:
        """Initialize the weather entity.

        Args:
            coordinator: Data coordinator
            location_name: Name of the location
            latitude: Location latitude
            longitude: Location longitude
        """
        super().__init__(coordinator)
        self._location_name = location_name
        self._latitude = latitude
        self._longitude = longitude
        self._attr_unique_id = f"{DOMAIN}_{latitude}_{longitude}_weather"
        self._attr_attribution = ATTRIBUTION

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this weather entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._latitude}_{self._longitude}")},
            name=f"{self._location_name} Mountain Weather",
            manufacturer=MANUFACTURER,
            model="Open-Meteo Forecast",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("current", {}).get("condition")

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("current", {}).get("temperature")

    @property
    def humidity(self) -> int | None:
        """Return the current humidity."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("current", {}).get("humidity")

    @property
    def native_pressure(self) -> float | None:
        """Return the current pressure."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("current", {}).get("pressure")

    @property
    def native_wind_speed(self) -> float | None:
        """Return the current wind speed."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("current", {}).get("wind_speed")

    @property
    def wind_bearing(self) -> int | None:
        """Return the current wind bearing."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("current", {}).get("wind_bearing")

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the current wind gust speed."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("current", {}).get("wind_gust")

    @property
    def cloud_coverage(self) -> int | None:
        """Return the current cloud coverage."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("current", {}).get("cloud_coverage")

    @property
    def native_visibility(self) -> float | None:
        """Return the current visibility."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("current", {}).get("visibility")

    @property
    def uv_index(self) -> float | None:
        """Return the current UV index."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("uv_index")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}

        attrs = {
            "elevation": self.coordinator.data.get("elevation"),
            "latitude": self._latitude,
            "longitude": self._longitude,
            "location_name": self._location_name,
        }

        # Add sunrise/sunset if available
        if sunrise := self.coordinator.data.get("sunrise"):
            attrs["sunrise"] = sunrise.isoformat()
        if sunset := self.coordinator.data.get("sunset"):
            attrs["sunset"] = sunset.isoformat()

        return attrs

    async def async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        if not self.coordinator.data:
            return None

        daily_forecast = self.coordinator.data.get("daily_forecast", [])
        forecasts: list[Forecast] = []

        for forecast_data in daily_forecast:
            forecast = Forecast(
                datetime=forecast_data["datetime"],
                condition=forecast_data.get("condition"),
                native_temperature=forecast_data.get("temperature"),
                native_templow=forecast_data.get("templow"),
                native_precipitation=forecast_data.get("precipitation"),
                precipitation_probability=forecast_data.get("precipitation_probability"),
                native_wind_speed=forecast_data.get("wind_speed"),
                native_wind_gust_speed=forecast_data.get("wind_gust_speed"),
                wind_bearing=forecast_data.get("wind_bearing"),
            )
            forecasts.append(forecast)

        return forecasts

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast."""
        if not self.coordinator.data:
            return None

        hourly_forecast = self.coordinator.data.get("hourly_forecast", [])
        forecasts: list[Forecast] = []

        for forecast_data in hourly_forecast:
            forecast = Forecast(
                datetime=forecast_data["datetime"],
                condition=forecast_data.get("condition"),
                native_temperature=forecast_data.get("temperature"),
                native_precipitation=forecast_data.get("precipitation"),
                precipitation_probability=forecast_data.get("precipitation_probability"),
                native_wind_speed=forecast_data.get("wind_speed"),
                native_wind_gust_speed=forecast_data.get("wind_gust_speed"),
                wind_bearing=forecast_data.get("wind_bearing"),
                cloud_coverage=forecast_data.get("cloud_coverage"),
            )
            forecasts.append(forecast)

        return forecasts
