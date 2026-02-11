"""Weather platform for Serac integration."""
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
    CONF_ENTITY_PREFIX,
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
    """Set up Serac weather entity from a config entry."""
    coordinator: AromeCoordinator = hass.data[DOMAIN][entry.entry_id]["arome_coordinator"]
    location_name = entry.data[CONF_LOCATION_NAME]
    entity_prefix = entry.data[CONF_ENTITY_PREFIX]
    latitude = entry.data[CONF_LATITUDE]
    longitude = entry.data[CONF_LONGITUDE]

    async_add_entities(
        [SeracWeather(coordinator, location_name, entity_prefix, latitude, longitude)],
        True,
    )


class SeracWeather(CoordinatorEntity[AromeCoordinator], WeatherEntity):
    """Weather entity for Serac integration."""

    _attr_has_entity_name = False
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
        entity_prefix: str,
        latitude: float,
        longitude: float,
    ) -> None:
        """Initialize the weather entity.

        Args:
            coordinator: Data coordinator
            location_name: Name of the location
            entity_prefix: Prefix for entity ID
            latitude: Location latitude
            longitude: Location longitude
        """
        super().__init__(coordinator)
        self._location_name = location_name
        self._entity_prefix = entity_prefix
        self._latitude = latitude
        self._longitude = longitude

        # Set entity_id using new pattern: weather.serac_{prefix}
        self.entity_id = f"weather.serac_{entity_prefix}"

        # Unique ID uses coordinates for uniqueness
        self._attr_unique_id = f"serac_{latitude}_{longitude}_weather"
        self._attr_name = location_name
        self._attr_attribution = ATTRIBUTION

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this weather entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"serac_{self._latitude}_{self._longitude}")},
            name=f"{self._location_name} (Serac)",
            manufacturer=MANUFACTURER,
            model="Mountain Weather Station",
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

        # Base attributes
        elevation = self.coordinator.data.get("elevation")
        attrs = {
            "elevation": f"{elevation}m" if elevation is not None else None,
            "latitude": self._latitude,
            "longitude": self._longitude,
            "location_name": self._location_name,
        }

        # Add current weather data
        current = self.coordinator.data.get("current", {})
        if current:
            temp = current.get("temperature")
            attrs["current_temperature"] = f"{temp}°C" if temp is not None else None

            humidity = current.get("humidity")
            attrs["current_humidity"] = f"{humidity}%" if humidity is not None else None

            attrs["current_is_day"] = "day" if current.get("is_day") else "night"

            wind_speed = current.get("wind_speed")
            attrs["current_wind_speed"] = f"{wind_speed}km/h" if wind_speed is not None else None

            wind_bearing = current.get("wind_bearing")
            attrs["current_wind_direction"] = f"{wind_bearing}°" if wind_bearing is not None else None

            wind_gust = current.get("wind_gust")
            attrs["current_wind_gust"] = f"{wind_gust}km/h" if wind_gust is not None else None

            precip = current.get("precipitation")
            attrs["current_precipitation"] = f"{precip}mm" if precip is not None else None

            rain = current.get("rain")
            attrs["current_rain"] = f"{rain}mm" if rain is not None else None

            showers = current.get("showers")
            attrs["current_showers"] = f"{showers}mm" if showers is not None else None

            snowfall = current.get("snowfall")
            attrs["current_snowfall"] = f"{snowfall}cm" if snowfall is not None else None

            cloud = current.get("cloud_coverage")
            attrs["current_cloud_coverage"] = f"{cloud}%" if cloud is not None else None

        # Add daily data for days 0, 1, 2
        daily_forecast = self.coordinator.data.get("daily_forecast", [])
        day_names = ["today", "tomorrow", "day_2"]

        for day_idx in range(min(3, len(daily_forecast))):
            day_data = daily_forecast[day_idx]
            day_name = day_names[day_idx]

            # Wind
            wind_speed = day_data.get("wind_speed")
            attrs[f"{day_name}_wind_speed_max"] = f"{wind_speed}km/h" if wind_speed is not None else None

            wind_gust = day_data.get("wind_gust_speed")
            attrs[f"{day_name}_wind_gust_max"] = f"{wind_gust}km/h" if wind_gust is not None else None

            wind_bearing = day_data.get("wind_bearing")
            attrs[f"{day_name}_wind_direction"] = f"{wind_bearing}°" if wind_bearing is not None else None

            # Sun times
            if sunrise := day_data.get("sunrise"):
                attrs[f"{day_name}_sunrise"] = sunrise.isoformat()
            if sunset := day_data.get("sunset"):
                attrs[f"{day_name}_sunset"] = sunset.isoformat()

            # Sun duration
            sunshine = day_data.get("sunshine_duration")
            attrs[f"{day_name}_sunshine_duration"] = f"{sunshine / 3600:.1f}h" if sunshine is not None else None

            daylight = day_data.get("daylight_duration")
            attrs[f"{day_name}_daylight_duration"] = f"{daylight / 3600:.1f}h" if daylight is not None else None

            # UV index
            attrs[f"{day_name}_uv_index"] = day_data.get("uv_index")

            # Precipitation
            rain_sum = day_data.get("rain_sum")
            attrs[f"{day_name}_rain_sum"] = f"{rain_sum}mm" if rain_sum is not None else None

            showers = day_data.get("showers_sum")
            attrs[f"{day_name}_showers_sum"] = f"{showers}mm" if showers is not None else None

            snow_sum = day_data.get("snowfall_sum")
            attrs[f"{day_name}_snowfall_sum"] = f"{snow_sum}cm" if snow_sum is not None else None

            precip_sum = day_data.get("precipitation_sum")
            attrs[f"{day_name}_precipitation_sum"] = f"{precip_sum}mm" if precip_sum is not None else None

            precip_hours = day_data.get("precipitation_hours")
            attrs[f"{day_name}_precipitation_hours"] = f"{precip_hours}h" if precip_hours is not None else None

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

        # Add current air quality data
        air_quality = self.coordinator.data.get("air_quality", {})
        current_aqi = air_quality.get("current", {})
        if current_aqi:
            aqi = current_aqi.get("european_aqi")
            attrs["current_european_aqi"] = f"{aqi} EAQI" if aqi is not None else None

            pm25 = current_aqi.get("pm2_5")
            attrs["current_pm2_5"] = f"{pm25}µg/m³" if pm25 is not None else None

            pm10 = current_aqi.get("pm10")
            attrs["current_pm10"] = f"{pm10}µg/m³" if pm10 is not None else None

            no2 = current_aqi.get("nitrogen_dioxide")
            attrs["current_nitrogen_dioxide"] = f"{no2}µg/m³" if no2 is not None else None

            o3 = current_aqi.get("ozone")
            attrs["current_ozone"] = f"{o3}µg/m³" if o3 is not None else None

            so2 = current_aqi.get("sulphur_dioxide")
            attrs["current_sulphur_dioxide"] = f"{so2}µg/m³" if so2 is not None else None

        # Add daily air quality forecast (next 5 days)
        daily_aqi = air_quality.get("daily_forecast", [])
        aqi_day_names = ["today", "tomorrow", "day_2", "day_3", "day_4"]

        for day_idx in range(min(5, len(daily_aqi))):
            day_data = daily_aqi[day_idx]
            day_name = aqi_day_names[day_idx]

            aqi_max = day_data.get("aqi_max")
            attrs[f"{day_name}_aqi_max"] = f"{aqi_max} EAQI" if aqi_max is not None else None

            pm25_max = day_data.get("pm25_max")
            attrs[f"{day_name}_pm25_max"] = f"{pm25_max}µg/m³" if pm25_max is not None else None

            pm10_max = day_data.get("pm10_max")
            attrs[f"{day_name}_pm10_max"] = f"{pm10_max}µg/m³" if pm10_max is not None else None

            attrs[f"{day_name}_aqi_date"] = day_data.get("date")

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
