"""Data update coordinators for Serac integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
import time
from typing import Any, Callable, TypeVar

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api.airquality_client import AirQualityApiError, AirQualityClient
from .api.bra_client import BraApiError, BraClient
from .api.openmeteo_client import OpenMeteoApiError, OpenMeteoClient
from .const import AROME_UPDATE_INTERVAL, BRA_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


async def async_retry_with_backoff(
    func: Callable[[], Any],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    retry_on: tuple[type[Exception], ...] = (aiohttp.ClientError, asyncio.TimeoutError),
    context: str = "API call",
) -> T:
    """Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Factor to multiply delay by after each retry
        retry_on: Tuple of exception types to retry on
        context: Description of the operation for logging

    Returns:
        Result of the function call

    Raises:
        Exception: The last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except retry_on as err:
            last_exception = err

            if attempt < max_retries:
                _LOGGER.warning(
                    "%s failed (attempt %d/%d), retrying in %.1fs: %s",
                    context,
                    attempt + 1,
                    max_retries + 1,
                    delay,
                    err,
                )
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                _LOGGER.error(
                    "%s failed after %d attempts: %s",
                    context,
                    max_retries + 1,
                    err,
                )
        except (
            aiohttp.ClientResponseError,
        ) as err:
            # Don't retry on auth errors (401, 403) or not found (404)
            if hasattr(err, "status") and err.status in (401, 403, 404):
                _LOGGER.error("%s failed with auth/not found error (status %d): %s", context, err.status, err)
                raise
            # Retry on other HTTP errors (5xx, etc.)
            last_exception = err
            if attempt < max_retries:
                _LOGGER.warning(
                    "%s failed with HTTP error %d (attempt %d/%d), retrying in %.1fs: %s",
                    context,
                    err.status if hasattr(err, "status") else 0,
                    attempt + 1,
                    max_retries + 1,
                    delay,
                    err,
                )
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                _LOGGER.error(
                    "%s failed after %d attempts with HTTP error: %s",
                    context,
                    max_retries + 1,
                    err,
                )

    # If we get here, all retries failed
    if last_exception:
        raise last_exception
    raise UpdateFailed(f"{context} failed after {max_retries + 1} attempts")


class AromeCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for weather data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: OpenMeteoClient,
        location_name: str,
        airquality_client: AirQualityClient | None = None,
    ) -> None:
        """Initialize the weather coordinator.

        Args:
            hass: Home Assistant instance
            client: Open-Meteo API client
            location_name: Name of the location for logging
            airquality_client: Optional Air Quality API client
        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{location_name}_arome",
            update_interval=AROME_UPDATE_INTERVAL,
        )
        self.client = client
        self.airquality_client = airquality_client
        self.location_name = location_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Open-Meteo API.

        Returns:
            Dictionary containing all weather data

        Raises:
            UpdateFailed: If update fails
        """
        start_time = time.monotonic()
        try:
            _LOGGER.debug(
                "Starting weather data update for %s (lat=%.4f, lon=%.4f)",
                self.location_name,
                self.client._latitude,
                self.client._longitude,
            )

            # Define wrapped API calls with retry logic
            async def fetch_current():
                return await async_retry_with_backoff(
                    self.client.async_get_current_weather,
                    context=f"Fetch current weather for {self.location_name}",
                )

            async def fetch_daily():
                return await async_retry_with_backoff(
                    self.client.async_get_daily_forecast,
                    context=f"Fetch daily forecast for {self.location_name}",
                )

            async def fetch_hourly():
                return await async_retry_with_backoff(
                    self.client.async_get_hourly_forecast,
                    context=f"Fetch hourly forecast for {self.location_name}",
                )

            async def fetch_hourly_6h():
                return await async_retry_with_backoff(
                    self.client.async_get_hourly_6h,
                    context=f"Fetch 6h forecast for {self.location_name}",
                )

            async def fetch_additional():
                return await async_retry_with_backoff(
                    self.client.async_get_additional_data,
                    context=f"Fetch additional data for {self.location_name}",
                )

            # Fetch all data in parallel for better performance
            tasks = [
                fetch_current(),
                fetch_daily(),
                fetch_hourly(),
                fetch_hourly_6h(),
                fetch_additional(),
            ]

            # Add air quality task if client is available
            if self.airquality_client:

                async def fetch_air_quality():
                    return await async_retry_with_backoff(
                        self.airquality_client.async_get_air_quality,
                        context=f"Fetch air quality for {self.location_name}",
                    )

                tasks.append(fetch_air_quality())

            # Execute all API calls in parallel (with retry logic per task)
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Unpack results
            current_weather = results[0] if not isinstance(results[0], Exception) else {}
            daily_forecast = results[1] if not isinstance(results[1], Exception) else []
            hourly_forecast = results[2] if not isinstance(results[2], Exception) else []
            hourly_6h = results[3] if not isinstance(results[3], Exception) else []
            additional_data = results[4] if not isinstance(results[4], Exception) else {}

            # Handle air quality data
            air_quality_data = {}
            if self.airquality_client and len(results) > 5:
                if isinstance(results[5], Exception):
                    _LOGGER.warning("Error fetching air quality data for %s: %s", self.location_name, results[5])
                else:
                    air_quality_data = results[5]
                    _LOGGER.debug("Successfully fetched air quality data for %s", self.location_name)

            # Check for critical errors
            if isinstance(results[0], Exception):
                raise UpdateFailed(f"Failed to get current weather: {results[0]}") from results[0]
            if isinstance(results[1], Exception):
                raise UpdateFailed(f"Failed to get daily forecast: {results[1]}") from results[1]

            # Combine all data
            data = {
                "current": current_weather,
                "daily_forecast": daily_forecast,
                "hourly_forecast": hourly_forecast,
                "hourly_6h": hourly_6h,
                "elevation": additional_data.get("elevation", 0),
                "air_quality": air_quality_data,
            }

            elapsed_time = time.monotonic() - start_time
            _LOGGER.info(
                "Weather update completed for %s in %.2fs: %d daily forecasts, %d hourly forecasts, %s air quality",
                self.location_name,
                elapsed_time,
                len(daily_forecast),
                len(hourly_forecast),
                "available" if air_quality_data else "unavailable",
            )
            _LOGGER.debug(
                "Weather data details for %s: elevation=%dm, 6h forecasts=%d, current_temp=%.1f°C",
                self.location_name,
                additional_data.get("elevation", 0),
                len(hourly_6h),
                current_weather.get("temperature", 0),
            )

            return data

        except OpenMeteoApiError as err:
            elapsed_time = time.monotonic() - start_time
            _LOGGER.error(
                "Failed to fetch weather data for %s after %.2fs (lat=%.4f, lon=%.4f): %s",
                self.location_name,
                elapsed_time,
                self.client._latitude,
                self.client._longitude,
                err,
            )
            raise UpdateFailed(f"Error fetching weather data: {err}") from err
        except Exception as err:
            elapsed_time = time.monotonic() - start_time
            _LOGGER.error(
                "Unexpected error fetching weather data for %s after %.2fs: %s (type: %s)",
                self.location_name,
                elapsed_time,
                err,
                type(err).__name__,
            )
            raise UpdateFailed(f"Unexpected error: {err}") from err


class BraCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for BRA avalanche bulletin updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: BraClient,
        location_name: str,
        massif_id: int,
        massif_name: str,
    ) -> None:
        """Initialize the BRA coordinator.

        Args:
            hass: Home Assistant instance
            client: BRA API client
            location_name: Name of the location for logging
            massif_id: Numeric ID of the massif
            massif_name: Name of the massif
        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{location_name}_bra",
            update_interval=BRA_UPDATE_INTERVAL,
        )
        self.client = client
        self.location_name = location_name
        self.massif_id = massif_id
        self.massif_name = massif_name

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from BRA API.

        Returns:
            Dictionary containing BRA avalanche data

        Raises:
            UpdateFailed: If update fails
        """
        start_time = time.monotonic()
        try:
            _LOGGER.debug(
                "Starting BRA bulletin update for %s - massif %s (%s, ID: %d)",
                self.location_name,
                self.massif_name,
                "French Alps" if self.massif_id <= 23 else "Pyrenees/Corsica",
                self.massif_id,
            )

            # Fetch bulletin data with retry logic
            bulletin_data = await async_retry_with_backoff(
                self.client.async_get_bulletin,
                context=f"Fetch BRA bulletin for {self.massif_name} (massif {self.massif_id})",
            )

            elapsed_time = time.monotonic() - start_time

            if not bulletin_data.get("has_data"):
                _LOGGER.warning(
                    "No BRA bulletin available for %s (massif %s, ID: %d) after %.2fs - likely out of season (bulletins published ~Dec-May)",
                    self.massif_name,
                    self.massif_name,
                    self.massif_id,
                    elapsed_time,
                )
                return {"has_data": False}

            _LOGGER.info(
                "BRA update completed for %s in %.2fs: risk_today=%s, risk_tomorrow=%s, bulletin_date=%s",
                self.massif_name,
                elapsed_time,
                bulletin_data.get("risk_max"),
                bulletin_data.get("risk_max_j2"),
                bulletin_data.get("bulletin_date"),
            )
            _LOGGER.debug(
                "BRA details for %s: altitude_limit=%s, high_risk=%s, low_risk=%s",
                self.massif_name,
                bulletin_data.get("altitude_limit"),
                bulletin_data.get("risk_high_altitude"),
                bulletin_data.get("risk_low_altitude"),
            )

            return bulletin_data

        except BraApiError as err:
            elapsed_time = time.monotonic() - start_time
            _LOGGER.error(
                "Failed to fetch BRA bulletin for %s (massif ID: %d) after %.2fs: %s",
                self.massif_name,
                self.massif_id,
                elapsed_time,
                err,
            )
            raise UpdateFailed(f"Error fetching BRA data: {err}") from err
        except Exception as err:
            elapsed_time = time.monotonic() - start_time
            _LOGGER.error(
                "Unexpected error fetching BRA data for %s (massif ID: %d) after %.2fs: %s (type: %s)",
                self.massif_name,
                self.massif_id,
                elapsed_time,
                err,
                type(err).__name__,
            )
            raise UpdateFailed(f"Unexpected error: {err}") from err
