"""BRA (Bulletin de Risque d'Avalanche) API client for Météo-France."""
from __future__ import annotations

import logging
from typing import Any
from xml.etree import ElementTree as ET

import aiohttp

_LOGGER = logging.getLogger(__name__)


class BraApiError(Exception):
    """Exception raised for BRA API errors."""


class BraClient:
    """Client for Météo-France BRA API."""

    def __init__(
        self,
        api_key: str,
        massif_id: str | int,
    ) -> None:
        """Initialize the BRA client.

        Args:
            api_key: Météo-France API key
            massif_id: Massif identifier (numeric: 1=Chablais, 2=Aravis, 3=Mont-Blanc)
        """
        self._api_key = api_key
        self._massif_id = str(massif_id)  # Convert to string for API
        self._api_base_url = "https://public-api.meteofrance.fr/public/DPBRA/v1"

    async def async_get_bulletin(self) -> dict[str, Any]:
        """Get avalanche bulletin for the configured massif.

        Returns:
            Dictionary with parsed bulletin data

        Raises:
            BraApiError: If fetching or parsing fails
        """
        try:
            headers = {
                "apikey": self._api_key,
            }

            url = f"{self._api_base_url}/massif/BRA"
            params = {
                "id-massif": self._massif_id,
                "format": "xml",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise BraApiError(
                            f"Failed to get bulletin: {response.status} - {error_text}"
                        )

                    xml_content = await response.text()

            # Parse XML and extract data
            return self._parse_bulletin_xml(xml_content)

        except aiohttp.ClientError as err:
            raise BraApiError(f"Network error fetching bulletin: {err}") from err
        except ET.ParseError as err:
            raise BraApiError(f"XML parsing error: {err}") from err
        except Exception as err:
            raise BraApiError(f"Unexpected error fetching bulletin: {err}") from err

    def _parse_bulletin_xml(self, xml_content: str) -> dict[str, Any]:
        """Parse BRA XML bulletin into structured data.

        Args:
            xml_content: Raw XML string from API

        Returns:
            Dictionary with bulletin data
        """
        try:
            root = ET.fromstring(xml_content)

            # Extract bulletin metadata
            bulletin_date = root.attrib.get("DATEBULLETIN")
            massif_name = root.attrib.get("MASSIF")

            # Find risk cartridge
            cartouche = root.find(".//CARTOUCHERISQUE")
            if cartouche is None:
                _LOGGER.warning("No CARTOUCHERISQUE found in bulletin")
                return {
                    "bulletin_date": bulletin_date,
                    "massif_name": massif_name,
                    "has_data": False,
                }

            risk_element = cartouche.find("RISQUE")
            if risk_element is None:
                _LOGGER.warning("No risk data found in bulletin")
                return {
                    "bulletin_date": bulletin_date,
                    "massif_name": massif_name,
                    "has_data": False,
                }

            # Extract risk levels
            risk_max = risk_element.attrib.get("RISQUEMAXI")
            risk_max_j2 = risk_element.attrib.get("RISQUEMAXIJ2")
            date_risk_j2 = risk_element.attrib.get("DATE_RISQUE_J2")
            risk_1 = risk_element.attrib.get("RISQUE1")  # High altitude
            risk_2 = risk_element.attrib.get("RISQUE2")  # Low altitude
            altitude_limit = risk_element.attrib.get("ALTITUDE")
            commentaire = risk_element.attrib.get("COMMENTAIRE", "")

            # Extract risk descriptions from CDATA
            accidentel = cartouche.findtext("ACCIDENTEL", default="")
            naturel = cartouche.findtext("NATUREL", default="")
            resume = cartouche.findtext("RESUME", default="")
            risque_j2_text = cartouche.findtext("RisqueJ2", default="")
            commentaire_j2 = cartouche.findtext("CommentaireRisqueJ2", default="")

            # Extract warning/notice
            avis = cartouche.findtext("AVIS", default="")

            # Build result dictionary
            result = {
                "bulletin_date": bulletin_date,
                "massif_name": massif_name,
                "has_data": True,
                # Current risk (J+1)
                "risk_max": int(risk_max) if risk_max else None,
                "risk_high_altitude": int(risk_1) if risk_1 else None,
                "risk_low_altitude": int(risk_2) if risk_2 else None,
                "altitude_limit": int(altitude_limit) if altitude_limit else None,
                "risk_comment": commentaire.strip(),
                # Tomorrow risk (J+2)
                "risk_max_j2": int(risk_max_j2) if risk_max_j2 else None,
                "date_risk_j2": date_risk_j2,
                "risk_j2_text": risque_j2_text.strip(),
                "risk_j2_comment": commentaire_j2.strip(),
                # Risk descriptions
                "accidental_text": accidentel.strip(),
                "natural_text": naturel.strip(),
                "summary": resume.strip(),
                "warning": avis.strip(),
            }

            _LOGGER.debug(
                "Parsed bulletin for massif %s (%s): risk_today=%s, risk_tomorrow=%s, date=%s",
                self._massif_id,
                massif_name,
                risk_max,
                risk_max_j2,
                bulletin_date,
            )

            return result

        except Exception as err:
            _LOGGER.error("Error parsing XML: %s", err)
            raise BraApiError(f"XML parsing failed: {err}") from err
