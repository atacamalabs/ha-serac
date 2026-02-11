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
        daily_forecast = self.coordinator.data.get("daily_forecast", [])
        if daily_forecast and len(daily_forecast) > 0:
            return daily_forecast[0].get("uv_index")
        return None

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

        # Add sunrise/sunset from today's forecast
        daily_forecast = self.coordinator.data.get("daily_forecast", [])
        if daily_forecast and len(daily_forecast) > 0:
            if sunrise := daily_forecast[0].get("sunrise"):
                attrs["sunrise"] = sunrise.isoformat()
            if sunset := daily_forecast[0].get("sunset"):
                attrs["sunset"] = sunset.isoformat()

        # Add hourly forecast for next 6 hours
        hourly_6h = self.coordinator.data.get("hourly_6h", [])
        for i, hour_data in enumerate(hourly_6h, start=1):
            prefix = f"hour_{i}"
            attrs[f"{prefix}_datetime"] = hour_data.get("datetime").isoformat() if hour_data.get("datetime") else None

            # Add values with units
            temp = hour_data.get("temperature")
            attrs[f"{prefix}_temperature"] = f"{temp}°C" if temp is not None else None

            wind = hour_data.get("wind_speed")
            attrs[f"{prefix}_wind_speed"] = f"{wind}km/h" if wind is not None else None

            gust = hour_data.get("wind_gust")
            attrs[f"{prefix}_wind_gust"] = f"{gust}km/h" if gust is not None else None

            cloud = hour_data.get("cloud_cover")
            attrs[f"{prefix}_cloud_cover"] = f"{cloud}%" if cloud is not None else None

            snow = hour_data.get("snowfall")
            attrs[f"{prefix}_snowfall"] = f"{snow}cm" if snow is not None else None

            rain = hour_data.get("rain")
            attrs[f"{prefix}_rain"] = f"{rain}mm" if rain is not None else None

            precip = hour_data.get("precipitation")
            attrs[f"{prefix}_precipitation"] = f"{precip}mm" if precip is not None else None

        # Add extended daily forecast (days 3-7)
        for day_idx in range(3, min(8, len(daily_forecast))):  # Days 3-7
            day_data = daily_forecast[day_idx]
            prefix = f"day_{day_idx}"

            attrs[f"{prefix}_datetime"] = day_data.get("datetime")

            # Wind with units
            wind_speed = day_data.get("wind_speed")
            attrs[f"{prefix}_wind_speed_max"] = f"{wind_speed}km/h" if wind_speed is not None else None

            wind_gust = day_data.get("wind_gust_speed")
            attrs[f"{prefix}_wind_gust_max"] = f"{wind_gust}km/h" if wind_gust is not None else None

            wind_dir = day_data.get("wind_bearing")
            attrs[f"{prefix}_wind_direction"] = f"{wind_dir}°" if wind_dir is not None else None

            # Sun times
            attrs[f"{prefix}_sunrise"] = day_data.get("sunrise").isoformat() if day_data.get("sunrise") else None
            attrs[f"{prefix}_sunset"] = day_data.get("sunset").isoformat() if day_data.get("sunset") else None

            # Duration (convert seconds to hours)
            sunshine = day_data.get("sunshine_duration")
            attrs[f"{prefix}_sunshine_duration"] = f"{sunshine / 3600:.1f}h" if sunshine is not None else None

            daylight = day_data.get("daylight_duration")
            attrs[f"{prefix}_daylight_duration"] = f"{daylight / 3600:.1f}h" if daylight is not None else None

            # UV index (no unit)
            attrs[f"{prefix}_uv_index"] = day_data.get("uv_index")

            # Precipitation with units
            rain_sum = day_data.get("rain_sum")
            attrs[f"{prefix}_rain_sum"] = f"{rain_sum}mm" if rain_sum is not None else None

            showers = day_data.get("showers_sum")
            attrs[f"{prefix}_showers_sum"] = f"{showers}mm" if showers is not None else None

            snow_sum = day_data.get("snowfall_sum")
            attrs[f"{prefix}_snowfall_sum"] = f"{snow_sum}cm" if snow_sum is not None else None

            precip_sum = day_data.get("precipitation_sum")
            attrs[f"{prefix}_precipitation_sum"] = f"{precip_sum}mm" if precip_sum is not None else None

            precip_hours = day_data.get("precipitation_hours")
            attrs[f"{prefix}_precipitation_hours"] = f"{precip_hours}h" if precip_hours is not None else None

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
