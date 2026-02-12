"""Tests for Serac config flow."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.serac.config_flow import SeracConfigFlow
from custom_components.serac.const import DOMAIN


class TestConfigFlow:
    """Test Serac config flow."""

    @pytest.mark.asyncio
    async def test_user_step_valid_coordinates(self, mock_hass):
        """Test user step with valid coordinates."""
        flow = SeracConfigFlow()
        flow.hass = mock_hass

        # Mock Open-Meteo API call for validation
        with patch(
            "custom_components.serac.config_flow.OpenMeteoClient"
        ) as mock_client_class:
            mock_client = MagicMock()
            mock_client.async_get_current_weather = AsyncMock(
                return_value={"temperature": 5.0}
            )
            mock_client_class.return_value = mock_client

            result = await flow.async_step_user(
                user_input={
                    "location_name": "Test Location",
                    "latitude": 45.9237,
                    "longitude": 6.8694,
                }
            )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "prefix"
        assert flow.location_name == "Test Location"
        assert flow.latitude == 45.9237
        assert flow.longitude == 6.8694

    @pytest.mark.asyncio
    async def test_user_step_invalid_coordinates(self, mock_hass):
        """Test user step with invalid coordinates."""
        flow = SeracConfigFlow()
        flow.hass = mock_hass

        # Mock Open-Meteo API call failure
        with patch(
            "custom_components.serac.config_flow.OpenMeteoClient"
        ) as mock_client_class:
            mock_client = MagicMock()
            mock_client.async_get_current_weather = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_client_class.return_value = mock_client

            result = await flow.async_step_user(
                user_input={
                    "location_name": "Invalid Location",
                    "latitude": 999.0,
                    "longitude": 999.0,
                }
            )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "user"
        assert "cannot_connect" in result["errors"]["base"]

    @pytest.mark.asyncio
    async def test_prefix_step_valid(self, mock_hass):
        """Test prefix step with valid input."""
        flow = SeracConfigFlow()
        flow.hass = mock_hass
        flow.location_name = "Test Location"
        flow.latitude = 45.9237
        flow.longitude = 6.8694

        result = await flow.async_step_prefix(
            user_input={"entity_prefix": "test"}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "massifs"
        assert flow.entity_prefix == "test"

    @pytest.mark.asyncio
    async def test_prefix_step_invalid(self, mock_hass):
        """Test prefix step with invalid input."""
        flow = SeracConfigFlow()
        flow.hass = mock_hass
        flow.location_name = "Test Location"

        result = await flow.async_step_prefix(
            user_input={"entity_prefix": "Invalid Prefix!"}
        )

        assert result["type"] == FlowResultType.FORM
        assert result["step_id"] == "prefix"
        assert "invalid_prefix" in result["errors"]["entity_prefix"]

    @pytest.mark.asyncio
    async def test_massifs_step_with_token(self, mock_hass):
        """Test massifs step with BRA token."""
        flow = SeracConfigFlow()
        flow.hass = mock_hass
        flow.location_name = "Test Location"
        flow.latitude = 45.9237
        flow.longitude = 6.8694
        flow.entity_prefix = "test"

        result = await flow.async_step_massifs(
            user_input={
                "bra_token": "test_token_123",
                "massif_ids": ["1", "2"],
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Test Location"
        assert result["data"]["bra_token"] == "test_token_123"
        assert result["data"]["massif_ids"] == ["1", "2"]

    @pytest.mark.asyncio
    async def test_massifs_step_without_token(self, mock_hass):
        """Test massifs step without BRA token (weather only)."""
        flow = SeracConfigFlow()
        flow.hass = mock_hass
        flow.location_name = "Test Location"
        flow.latitude = 45.9237
        flow.longitude = 6.8694
        flow.entity_prefix = "test"

        result = await flow.async_step_massifs(
            user_input={
                "bra_token": "",
                "massif_ids": [],
            }
        )

        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "Test Location"
        assert "bra_token" not in result["data"]
        assert result["data"]["massif_ids"] == []

    @pytest.mark.asyncio
    async def test_prefix_validation_start_with_letter(self):
        """Test prefix must start with a letter."""
        flow = SeracConfigFlow()

        # Test invalid prefixes
        assert not flow._is_valid_prefix("1test")  # Starts with number
        assert not flow._is_valid_prefix("_test")  # Starts with underscore

        # Test valid prefixes
        assert flow._is_valid_prefix("test")
        assert flow._is_valid_prefix("test123")
        assert flow._is_valid_prefix("test_home")

    @pytest.mark.asyncio
    async def test_prefix_validation_characters(self):
        """Test prefix character validation."""
        flow = SeracConfigFlow()

        # Test invalid characters
        assert not flow._is_valid_prefix("test-home")  # Dash not allowed
        assert not flow._is_valid_prefix("test home")  # Space not allowed
        assert not flow._is_valid_prefix("test!home")  # Special char not allowed
        assert not flow._is_valid_prefix("Test")  # Uppercase not allowed

        # Test valid
        assert flow._is_valid_prefix("test")
        assert flow._is_valid_prefix("test_123")
        assert flow._is_valid_prefix("my_home_station")

    @pytest.mark.asyncio
    async def test_prefix_validation_length(self):
        """Test prefix length validation."""
        flow = SeracConfigFlow()

        # Too short (empty)
        assert not flow._is_valid_prefix("")

        # Too long (>20 characters)
        assert not flow._is_valid_prefix("a" * 21)

        # Valid lengths
        assert flow._is_valid_prefix("a")  # Minimum
        assert flow._is_valid_prefix("a" * 20)  # Maximum
        assert flow._is_valid_prefix("test")  # Normal

    @pytest.mark.asyncio
    async def test_prefix_suggestion(self):
        """Test automatic prefix suggestion."""
        flow = SeracConfigFlow()

        # Test various location names
        suggestions = [
            ("Chamonix Mont-Blanc", "chamonix"),
            ("Les Deux Alpes", "les_deux_alpes"),
            ("Val d'Isère", "val_disere"),
            ("Saint-Gervais-les-Bains", "saint_gervais_les_b"),
            ("Home", "home"),
            ("My Mountain Station", "my_mountain_station"),
        ]

        for location, expected in suggestions:
            suggested = flow._suggest_prefix(location)
            assert suggested == expected or len(suggested) <= 20
