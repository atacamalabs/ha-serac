"""Constants for the Better Mountain Weather integration."""
from datetime import timedelta
from typing import Final

# Integration domain
DOMAIN: Final = "better_mountain_weather"

# Platforms
PLATFORMS: Final = ["weather", "sensor"]

# Configuration keys
CONF_AROME_TOKEN: Final = "arome_token"
CONF_BRA_TOKEN: Final = "bra_token"
CONF_LOCATION_NAME: Final = "location_name"
CONF_MASSIF_ID: Final = "massif_id"
CONF_MASSIF_NAME: Final = "massif_name"

# Update intervals
AROME_UPDATE_INTERVAL: Final = timedelta(hours=1)
BRA_UPDATE_INTERVAL: Final = timedelta(hours=6)

# API Configuration
API_TIMEOUT: Final = 30

# Default values
DEFAULT_NAME: Final = "Better Mountain Weather"

# Attribution
ATTRIBUTION: Final = "Data provided by Météo-France"
MANUFACTURER: Final = "Météo-France"

# French Alps and Pyrenees Massifs
# Format: ID -> (Name, Approximate center latitude, center longitude)
MASSIFS: Final = {
    # Alps (23 massifs)
    "CHABLAIS": ("Chablais", 46.3, 6.7),
    "ARAVIS": ("Aravis", 45.9, 6.5),
    "MONT-BLANC": ("Mont-Blanc", 45.9, 6.9),
    "BAUGES": ("Bauges", 45.7, 6.2),
    "BEAUFORTAIN": ("Beaufortain", 45.7, 6.6),
    "HAUTE-TARENTAISE": ("Haute-Tarentaise", 45.5, 6.9),
    "CHARTREUSE": ("Chartreuse", 45.4, 5.8),
    "BELLEDONNE": ("Belledonne", 45.3, 6.0),
    "MAURIENNE": ("Maurienne", 45.2, 6.6),
    "VANOISE": ("Vanoise", 45.4, 6.8),
    "HAUTE-MAURIENNE": ("Haute-Maurienne", 45.2, 6.9),
    "VERCORS": ("Vercors", 45.0, 5.5),
    "OISANS": ("Oisans", 45.0, 6.3),
    "GRANDES-ROUSSES": ("Grandes-Rousses", 45.1, 6.1),
    "THABOR": ("Thabor", 45.1, 6.5),
    "PELVOUX": ("Pelvoux", 44.9, 6.4),
    "QUEYRAS": ("Queyras", 44.7, 6.8),
    "DEVOLUY": ("Dévoluy", 44.7, 5.9),
    "CHAMPSAUR": ("Champsaur", 44.7, 6.2),
    "EMBRUNAIS-PARPAILLON": ("Embrunais-Parpaillon", 44.5, 6.5),
    "UBAYE": ("Ubaye", 44.4, 6.7),
    "MERCANTOUR": ("Mercantour", 44.1, 7.4),
    "ALPES-AZUR": ("Alpes-Azur", 43.9, 7.2),

    # Pyrenees (16 massifs)
    "PAYS-BASQUE": ("Pays-Basque", 43.0, -1.0),
    "ASPE-OSSAU": ("Aspe-Ossau", 42.9, -0.4),
    "HAUTE-BIGORRE": ("Haute-Bigorre", 42.8, 0.1),
    "AURE-LOURON": ("Aure-Louron", 42.8, 0.4),
    "LUCHONNAIS": ("Luchonnais", 42.8, 0.6),
    "COUSERANS": ("Couserans", 42.8, 1.0),
    "HAUTE-ARIEGE": ("Haute-Ariège", 42.6, 1.5),
    "ORLU-ST-BARTHELEMY": ("Orlu-St-Barthélémy", 42.6, 1.9),
    "CAPCIR-PUYMORENS": ("Capcir-Puymorens", 42.5, 2.0),
    "CERDAGNE-CANIGOU": ("Cerdagne-Canigou", 42.5, 2.3),
    "ANDORRE": ("Andorre", 42.6, 1.6),
    "MONTAGNE-BASQUE": ("Montagne-Basque", 43.0, -1.2),
    "BEARN": ("Béarn", 42.9, -0.5),
    "BIGORRE": ("Bigorre", 42.9, 0.0),
    "COMMINGES": ("Comminges", 42.8, 0.7),
    "ARIEGE": ("Ariège", 42.7, 1.3),

    # Corsica (1 massif)
    "CORSE": ("Corse", 42.2, 9.0),
}

# Sensor types for AROME
SENSOR_TYPE_ELEVATION: Final = "elevation"
SENSOR_TYPE_AIR_QUALITY: Final = "air_quality"
SENSOR_TYPE_UV_INDEX: Final = "uv_index"
SENSOR_TYPE_SUNRISE: Final = "sunrise"
SENSOR_TYPE_SUNSET: Final = "sunset"
SENSOR_TYPE_CLOUD_COVERAGE: Final = "cloud_coverage"
SENSOR_TYPE_HUMIDITY: Final = "humidity"
SENSOR_TYPE_WIND_SPEED_CURRENT: Final = "wind_speed_current"
SENSOR_TYPE_WIND_GUST_CURRENT: Final = "wind_gust_current"
SENSOR_TYPE_WIND_SPEED_TODAY_MAX: Final = "wind_speed_today_max"
SENSOR_TYPE_WIND_GUST_TODAY_MAX: Final = "wind_gust_today_max"

# Sensor types for BRA (Phase 2)
SENSOR_TYPE_AVALANCHE_RISK: Final = "avalanche_risk"
SENSOR_TYPE_RISK_TREND: Final = "risk_trend"
SENSOR_TYPE_SNOWPACK_QUALITY: Final = "snowpack_quality"
SENSOR_TYPE_RECENT_SNOW: Final = "recent_snow"
SENSOR_TYPE_RISK_ALTITUDE_HIGH: Final = "risk_altitude_high"
SENSOR_TYPE_RISK_ALTITUDE_LOW: Final = "risk_altitude_low"
SENSOR_TYPE_WIND_TRANSPORT_RISK: Final = "wind_transport_risk"
SENSOR_TYPE_WET_SNOW_RISK: Final = "wet_snow_risk"
