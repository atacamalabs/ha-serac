"""Météo-France Vigilance API client for weather alerts."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from ..const import DEPARTMENT_BOUNDARIES, VIGILANCE_COLOR_CODES, VIGILANCE_PHENOMENA

_LOGGER = logging.getLogger(__name__)


class VigilanceApiError(Exception):
    """Exception raised for Vigilance API errors."""


class VigilanceClient:
    """Client for Météo-France Vigilance API."""

    def __init__(
        self, api_token: str, latitude: float, longitude: float
    ) -> None:
        """Initialize the Vigilance client.

        Args:
            api_token: Météo-France Vigilance API token
            latitude: Location latitude
            longitude: Location longitude
        """
        self._api_token = api_token
        self._latitude = latitude
        self._longitude = longitude
        self._base_url = "https://public-api.meteofrance.fr/public/DPVigilance/v1"
        self._department = self._get_department_code(latitude, longitude)

    def _get_department_code(self, lat: float, lon: float) -> str | None:
        """Get French department code from GPS coordinates.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Two-digit department code (e.g., "74" for Haute-Savoie) or None if not found
        """
        # Check all department boundaries
        for dept_code, dept_info in DEPARTMENT_BOUNDARIES.items():
            bounds = dept_info["bounds"]
            min_lat, max_lat, min_lon, max_lon = bounds

            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                _LOGGER.debug(
                    "Coordinates (%.4f, %.4f) matched department %s (%s)",
                    lat,
                    lon,
                    dept_code,
                    dept_info["name"],
                )
                return dept_code

        # No match found
        _LOGGER.warning(
            "No French department found for coordinates (%.4f, %.4f). "
            "Vigilance alerts are only available for locations in France.",
            lat,
            lon,
        )
        return None

    async def async_get_current_vigilance(self) -> dict[str, Any]:
        """Get current vigilance alerts for the department.

        Returns:
            Dictionary with vigilance data:
            {
                "has_data": bool,
                "department": str,
                "department_name": str,
                "overall_level": int (1-4),
                "overall_color": str ("green", "yellow", "orange", "red"),
                "phenomena": {
                    "wind": {"level": int, "color": str},
                    "rain_flood": {"level": int, "color": str},
                    ...
                },
                "update_time": str (ISO format),
            }
        """
        # Check if coordinates are in France
        if not self._department:
            return {
                "has_data": False,
                "error": "not_in_france",
                "message": "Vigilance alerts only available for French locations",
            }

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"apikey": self._api_token}
                url = f"{self._base_url}/cartevigilance/encours"

                _LOGGER.debug(
                    "Fetching vigilance data for department %s from %s",
                    self._department,
                    url,
                )

                async with session.get(
                    url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    _LOGGER.debug(
                        "Vigilance API response received for department %s",
                        self._department,
                    )

                    # Extract data for our department
                    department_data = self._extract_department_data(data)

                    if not department_data:
                        _LOGGER.warning(
                            "No vigilance data found for department %s in API response",
                            self._department,
                        )
                        return {
                            "has_data": False,
                            "department": self._department,
                            "error": "no_data",
                        }

                    result = {
                        "has_data": True,
                        "department": self._department,
                        "department_name": DEPARTMENT_BOUNDARIES.get(
                            self._department, {}
                        ).get("name", "Unknown"),
                        "overall_level": department_data.get("overall_level", 1),
                        "overall_color": VIGILANCE_COLOR_CODES.get(
                            department_data.get("overall_level", 1), "green"
                        ),
                        "phenomena": department_data.get("phenomena", {}),
                        "update_time": data.get("update_time"),
                    }

                    _LOGGER.info(
                        "Vigilance data for %s (%s): level %d (%s), %d phenomena",
                        self._department,
                        result["department_name"],
                        result["overall_level"],
                        result["overall_color"],
                        len(result["phenomena"]),
                    )

                    return result

        except aiohttp.ClientResponseError as err:
            if err.status == 404:
                _LOGGER.warning(
                    "No vigilance data available for department %s (404 Not Found)",
                    self._department,
                )
                return {
                    "has_data": False,
                    "department": self._department,
                    "error": "not_found",
                }
            elif err.status in (401, 403):
                _LOGGER.error(
                    "Authentication failed for Vigilance API (status %d). "
                    "Check that your Vigilance API token is valid.",
                    err.status,
                )
                raise VigilanceApiError(
                    f"Authentication error: {err.status}"
                ) from err
            else:
                _LOGGER.error(
                    "HTTP error %d getting vigilance data: %s",
                    err.status,
                    err,
                    exc_info=True,
                )
                raise VigilanceApiError(f"HTTP error: {err}") from err

        except aiohttp.ClientError as err:
            _LOGGER.error(
                "Network error getting vigilance data: %s", err, exc_info=True
            )
            raise VigilanceApiError(f"Network error: {err}") from err

        except Exception as err:
            _LOGGER.error(
                "Unexpected error getting vigilance data: %s", err, exc_info=True
            )
            raise VigilanceApiError(f"Failed to get vigilance: {err}") from err

    def _extract_department_data(self, data: dict) -> dict | None:
        """Extract vigilance data for specific department from API response.

        Args:
            data: Full API response from Vigilance API

        Returns:
            Department-specific vigilance data or None if not found
        """
        # Real API structure (based on actual response):
        # {
        #   "product": {
        #     "periods": [
        #       {
        #         "echeance": "J",
        #         "timelaps": {
        #           "domain_ids": [
        #             {
        #               "domain_id": "74",
        #               "max_color_id": 3,
        #               "phenomenon_items": [
        #                 {
        #                   "phenomenon_id": "8",
        #                   "phenomenon_max_color_id": 3,
        #                   ...
        #                 }
        #               ]
        #             }
        #           ]
        #         }
        #       }
        #     ]
        #   }
        # }

        try:
            # Navigate to department data
            product = data.get("product", {})
            periods = product.get("periods", [])

            if not periods:
                _LOGGER.debug("No periods data in vigilance response")
                return None

            # Get current period (first one, usually "J" for today)
            current_period = periods[0]
            timelaps = current_period.get("timelaps", {})
            domain_ids = timelaps.get("domain_ids", [])

            if not domain_ids:
                _LOGGER.debug("No domain_ids in current period")
                return None

            # Find our department in the domain_ids list
            dept_data = None
            for domain in domain_ids:
                if domain.get("domain_id") == self._department:
                    dept_data = domain
                    break

            if not dept_data:
                _LOGGER.debug(
                    "Department %s not found in domain_ids. Available domains: %s",
                    self._department,
                    [d.get("domain_id") for d in domain_ids[:10]],  # Show first 10
                )
                return None

            # Extract overall level (max_color_id: 1=green, 2=yellow, 3=orange, 4=red)
            overall_level = dept_data.get("max_color_id", 1)

            # Extract individual phenomena
            phenomena = {}
            phenomenon_items = dept_data.get("phenomenon_items", [])

            for phenom_item in phenomenon_items:
                # Get phenomenon ID as string, then convert to int
                phenom_id_str = phenom_item.get("phenomenon_id")
                if not phenom_id_str:
                    continue

                phenom_id_int = int(phenom_id_str)
                phenom_name = VIGILANCE_PHENOMENA.get(phenom_id_int)

                if phenom_name:
                    # Use phenomenon_max_color_id as the alert level
                    phenom_level = phenom_item.get("phenomenon_max_color_id", 1)
                    phenomena[phenom_name] = {
                        "level": phenom_level,
                        "color": VIGILANCE_COLOR_CODES.get(phenom_level, "green"),
                    }

            _LOGGER.debug(
                "Extracted vigilance for dept %s: level=%d, phenomena=%s",
                self._department,
                overall_level,
                list(phenomena.keys()),
            )

            return {
                "overall_level": overall_level,
                "phenomena": phenomena,
            }

        except (KeyError, ValueError, TypeError) as err:
            _LOGGER.error(
                "Error parsing vigilance data for department %s: %s",
                self._department,
                err,
                exc_info=True,
            )
            return None
