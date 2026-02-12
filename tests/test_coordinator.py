"""Tests for Serac coordinators."""
import asyncio
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from custom_components.serac.coordinator import (
    AromeCoordinator,
    BraCoordinator,
    async_retry_with_backoff,
)
from homeassistant.helpers.update_coordinator import UpdateFailed


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self):
        """Test successful call on first attempt."""
        mock_func = AsyncMock(return_value="success")
        result = await async_retry_with_backoff(mock_func, context="Test call")
        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_success_after_failure(self):
        """Test successful call after one failure."""
        mock_func = AsyncMock(
            side_effect=[aiohttp.ClientError("Network error"), "success"]
        )
        result = await async_retry_with_backoff(
            mock_func, max_retries=2, initial_delay=0.01, context="Test call"
        )
        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_max_attempts_exceeded(self):
        """Test failure after max retries."""
        mock_func = AsyncMock(side_effect=aiohttp.ClientError("Persistent error"))
        with pytest.raises(aiohttp.ClientError):
            await async_retry_with_backoff(
                mock_func, max_retries=2, initial_delay=0.01, context="Test call"
            )
        assert mock_func.call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_no_retry_on_auth_error(self):
        """Test no retry on 401 auth error."""
        error = aiohttp.ClientResponseError(
            request_info=None, history=None, status=401
        )
        mock_func = AsyncMock(side_effect=error)
        with pytest.raises(aiohttp.ClientResponseError):
            await async_retry_with_backoff(
                mock_func, max_retries=2, initial_delay=0.01, context="Test call"
            )
        assert mock_func.call_count == 1  # No retries on auth error

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self):
        """Test retry on 503 server error."""
        error = aiohttp.ClientResponseError(
            request_info=None, history=None, status=503
        )
        mock_func = AsyncMock(side_effect=[error, "success"])
        result = await async_retry_with_backoff(
            mock_func, max_retries=2, initial_delay=0.01, context="Test call"
        )
        assert result == "success"
        assert mock_func.call_count == 2


class TestAromeCoordinator:
    """Test AromeCoordinator."""

    @pytest.mark.asyncio
    async def test_successful_update(
        self, mock_hass, mock_openmeteo_client, mock_airquality_client
    ):
        """Test successful weather data update."""
        coordinator = AromeCoordinator(
            hass=mock_hass,
            client=mock_openmeteo_client,
            location_name="Test Location",
            airquality_client=mock_airquality_client,
        )

        # Mock retry function to bypass delays
        with patch(
            "custom_components.serac.coordinator.async_retry_with_backoff",
            side_effect=lambda func, **kwargs: func(),
        ):
            data = await coordinator._async_update_data()

        assert data is not None
        assert "current" in data
        assert "daily_forecast" in data
        assert "hourly_forecast" in data
        assert "elevation" in data
        assert "air_quality" in data

        # Verify API calls were made
        mock_openmeteo_client.async_get_current_weather.assert_called_once()
        mock_openmeteo_client.async_get_daily_forecast.assert_called_once()
        mock_airquality_client.async_get_air_quality.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_without_air_quality(self, mock_hass, mock_openmeteo_client):
        """Test weather update without air quality client."""
        coordinator = AromeCoordinator(
            hass=mock_hass,
            client=mock_openmeteo_client,
            location_name="Test Location",
            airquality_client=None,
        )

        with patch(
            "custom_components.serac.coordinator.async_retry_with_backoff",
            side_effect=lambda func, **kwargs: func(),
        ):
            data = await coordinator._async_update_data()

        assert data is not None
        assert data["air_quality"] == {}

    @pytest.mark.asyncio
    async def test_update_api_error(self, mock_hass, mock_openmeteo_client):
        """Test update with API error."""
        coordinator = AromeCoordinator(
            hass=mock_hass,
            client=mock_openmeteo_client,
            location_name="Test Location",
        )

        # Simulate API error
        error = aiohttp.ClientError("Network error")
        mock_openmeteo_client.async_get_current_weather = AsyncMock(side_effect=error)

        with pytest.raises(UpdateFailed):
            with patch(
                "custom_components.serac.coordinator.async_retry_with_backoff",
                side_effect=error,
            ):
                await coordinator._async_update_data()


class TestBraCoordinator:
    """Test BraCoordinator."""

    @pytest.mark.asyncio
    async def test_successful_update(self, mock_hass, mock_bra_client):
        """Test successful BRA bulletin update."""
        coordinator = BraCoordinator(
            hass=mock_hass,
            client=mock_bra_client,
            location_name="Test Location",
            massif_id=1,
            massif_name="Chablais",
        )

        with patch(
            "custom_components.serac.coordinator.async_retry_with_backoff",
            side_effect=lambda func, **kwargs: func(),
        ):
            data = await coordinator._async_update_data()

        assert data is not None
        assert data["has_data"] is True
        assert "bulletin_date" in data
        assert "risk_max" in data
        assert data["massif_name"] == "Aravis"

        mock_bra_client.async_get_bulletin.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_no_data(self, mock_hass, mock_bra_client):
        """Test update when bulletin has no data (out of season)."""
        coordinator = BraCoordinator(
            hass=mock_hass,
            client=mock_bra_client,
            location_name="Test Location",
            massif_id=1,
            massif_name="Chablais",
        )

        # Simulate no data available (out of season)
        mock_bra_client.async_get_bulletin = AsyncMock(
            return_value={"has_data": False}
        )

        with patch(
            "custom_components.serac.coordinator.async_retry_with_backoff",
            side_effect=lambda func, **kwargs: func(),
        ):
            data = await coordinator._async_update_data()

        assert data is not None
        assert data["has_data"] is False

    @pytest.mark.asyncio
    async def test_update_api_error(self, mock_hass, mock_bra_client):
        """Test update with API error."""
        coordinator = BraCoordinator(
            hass=mock_hass,
            client=mock_bra_client,
            location_name="Test Location",
            massif_id=1,
            massif_name="Chablais",
        )

        # Simulate API error
        error = aiohttp.ClientError("Network error")
        mock_bra_client.async_get_bulletin = AsyncMock(side_effect=error)

        with pytest.raises(UpdateFailed):
            with patch(
                "custom_components.serac.coordinator.async_retry_with_backoff",
                side_effect=error,
            ):
                await coordinator._async_update_data()
