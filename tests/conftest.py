"""Fixtures for Serac tests."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_hass():
    """Mock Home Assistant instance."""
    hass = MagicMock()
    hass.data = {}
    return hass


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "latitude": 45.9237,
        "longitude": 6.8694,
        "location_name": "Test Location",
        "entity_prefix": "test",
        "bra_token": "test_token_12345",
        "massif_ids": [1, 2],
    }
    return entry


@pytest.fixture
def mock_openmeteo_client():
    """Mock Open-Meteo API client."""
    client = MagicMock()
    client._latitude = 45.9237
    client._longitude = 6.8694

    # Mock successful responses
    client.async_get_current_weather = AsyncMock(return_value={
        "temperature": 5.2,
        "humidity": 75,
        "wind_speed": 10.5,
        "condition": "cloudy",
    })

    client.async_get_daily_forecast = AsyncMock(return_value=[
        {
            "datetime": "2026-02-12",
            "temperature": 8.0,
            "templow": 2.0,
            "condition": "sunny",
        }
    ])

    client.async_get_hourly_forecast = AsyncMock(return_value=[
        {
            "datetime": "2026-02-12T12:00:00",
            "temperature": 6.0,
            "precipitation": 0.0,
        }
    ])

    client.async_get_hourly_6h = AsyncMock(return_value=[
        {
            "hour": 1,
            "temperature": 5.5,
        }
    ])

    client.async_get_additional_data = AsyncMock(return_value={
        "elevation": 1035,
    })

    return client


@pytest.fixture
def mock_airquality_client():
    """Mock Air Quality API client."""
    client = MagicMock()

    client.async_get_air_quality = AsyncMock(return_value={
        "european_aqi": 25,
        "pm2_5": 8.5,
        "pm10": 12.0,
    })

    return client


@pytest.fixture
def mock_bra_client():
    """Mock BRA API client."""
    client = MagicMock()

    client.async_get_bulletin = AsyncMock(return_value={
        "has_data": True,
        "bulletin_date": "2026-02-12T16:00:00",
        "massif_name": "Aravis",
        "risk_max": 3,
        "risk_max_j2": 2,
        "risk_high_altitude": "Marqué",
        "risk_low_altitude": "Faible",
        "altitude_limit": "2000",
    })

    return client
