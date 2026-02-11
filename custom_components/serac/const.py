"""Constants for the Serac integration."""
from datetime import timedelta
from typing import Final

# Integration domain
DOMAIN: Final = "serac"

# Platforms
PLATFORMS: Final = ["weather", "sensor"]

# Configuration keys
CONF_AROME_TOKEN: Final = "arome_token"
CONF_BRA_TOKEN: Final = "bra_token"
CONF_LOCATION_NAME: Final = "location_name"
CONF_ENTITY_PREFIX: Final = "entity_prefix"
CONF_MASSIF_ID: Final = "massif_id"
CONF_MASSIF_NAME: Final = "massif_name"
CONF_MASSIF_IDS: Final = "massif_ids"

# Update intervals
AROME_UPDATE_INTERVAL: Final = timedelta(hours=1)
BRA_UPDATE_INTERVAL: Final = timedelta(hours=6)

# API Configuration
API_TIMEOUT: Final = 30

# Default values
DEFAULT_NAME: Final = "Serac"

# Attribution
ATTRIBUTION: Final = "Data from Open-Meteo (Météo-France AROME & ARPEGE models)"
MANUFACTURER: Final = "Météo-France"

# French Alps and Pyrenees Massifs - Numeric IDs for BRA API
# Format: numeric_id -> (Name, Text ID)
MASSIF_IDS: Final = {
    # Northern Alps (Haute-Savoie & Savoie)
    1: ("Chablais", "CHABLAIS"),
    2: ("Aravis", "ARAVIS"),
    3: ("Mont-Blanc", "MONT-BLANC"),
    4: ("Bauges", "BAUGES"),
    5: ("Beaufortain", "BEAUFORTAIN"),
    6: ("Haute-Tarentaise", "HAUTE-TARENTAISE"),
    7: ("Chartreuse", "CHARTREUSE"),
    8: ("Belledonne", "BELLEDONNE"),
    9: ("Maurienne", "MAURIENNE"),
    10: ("Vanoise", "VANOISE"),
    11: ("Haute-Maurienne", "HAUTE-MAURIENNE"),
    12: ("Grandes-Rousses", "GRANDES-ROUSSES"),
    13: ("Thabor", "THABOR"),
    14: ("Vercors", "VERCORS"),
    15: ("Oisans", "OISANS"),
    16: ("Pelvoux", "PELVOUX"),
    # Southern Alps
    17: ("Queyras", "QUEYRAS"),
    18: ("Dévoluy", "DEVOLUY"),
    19: ("Champsaur", "CHAMPSAUR"),
    20: ("Embrunais-Parpaillon", "EMBRUNAIS-PARPAILLON"),
    21: ("Ubaye", "UBAYE"),
    22: ("Mercantour", "MERCANTOUR"),
    23: ("Alpes-Azur", "ALPES-AZUR"),
    # Pyrenees
    40: ("Pays-Basque", "PAYS-BASQUE"),
    41: ("Aspe-Ossau", "ASPE-OSSAU"),
    42: ("Haute-Bigorre", "HAUTE-BIGORRE"),
    43: ("Aure-Louron", "AURE-LOURON"),
    44: ("Luchonnais", "LUCHONNAIS"),
    45: ("Couserans", "COUSERANS"),
    46: ("Haute-Ariège", "HAUTE-ARIEGE"),
    47: ("Orlu-St-Barthélémy", "ORLU-ST-BARTHELEMY"),
    48: ("Capcir-Puymorens", "CAPCIR-PUYMORENS"),
    49: ("Cerdagne-Canigou", "CERDAGNE-CANIGOU"),
    50: ("Andorre", "ANDORRE"),
    # Corsica
    70: ("Corse", "CORSE"),
}

# French Alps and Pyrenees Massifs - For distance calculation
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

# Static sensors
SENSOR_TYPE_ELEVATION: Final = "elevation"

# Current weather sensors
SENSOR_TYPE_TEMPERATURE_CURRENT: Final = "temperature_current"
SENSOR_TYPE_HUMIDITY: Final = "humidity"
SENSOR_TYPE_WIND_SPEED_CURRENT: Final = "wind_speed_current"
SENSOR_TYPE_WIND_DIRECTION_CURRENT: Final = "wind_direction_current"
SENSOR_TYPE_WIND_GUST_CURRENT: Final = "wind_gust_current"
SENSOR_TYPE_IS_DAY: Final = "is_day"
SENSOR_TYPE_PRECIPITATION_CURRENT: Final = "precipitation_current"
SENSOR_TYPE_RAIN_CURRENT: Final = "rain_current"
SENSOR_TYPE_SHOWERS_CURRENT: Final = "showers_current"
SENSOR_TYPE_SNOWFALL_CURRENT: Final = "snowfall_current"
SENSOR_TYPE_CLOUD_COVERAGE: Final = "cloud_coverage"

# Air quality sensors
SENSOR_TYPE_EUROPEAN_AQI: Final = "european_aqi"
SENSOR_TYPE_PM2_5: Final = "pm2_5"
SENSOR_TYPE_PM10: Final = "pm10"
SENSOR_TYPE_NITROGEN_DIOXIDE: Final = "nitrogen_dioxide"
SENSOR_TYPE_OZONE: Final = "ozone"
SENSOR_TYPE_SULPHUR_DIOXIDE: Final = "sulphur_dioxide"

# Daily sensors - Day 0 (Today)
SENSOR_TYPE_WIND_SPEED_MAX_DAY0: Final = "wind_speed_max_day0"
SENSOR_TYPE_WIND_GUST_MAX_DAY0: Final = "wind_gust_max_day0"
SENSOR_TYPE_WIND_DIRECTION_DAY0: Final = "wind_direction_day0"
SENSOR_TYPE_SUNRISE_DAY0: Final = "sunrise_day0"
SENSOR_TYPE_SUNSET_DAY0: Final = "sunset_day0"
SENSOR_TYPE_SUNSHINE_DURATION_DAY0: Final = "sunshine_duration_day0"
SENSOR_TYPE_DAYLIGHT_DURATION_DAY0: Final = "daylight_duration_day0"
SENSOR_TYPE_UV_INDEX_DAY0: Final = "uv_index_day0"
SENSOR_TYPE_RAIN_SUM_DAY0: Final = "rain_sum_day0"
SENSOR_TYPE_SHOWERS_SUM_DAY0: Final = "showers_sum_day0"
SENSOR_TYPE_SNOWFALL_SUM_DAY0: Final = "snowfall_sum_day0"
SENSOR_TYPE_PRECIPITATION_SUM_DAY0: Final = "precipitation_sum_day0"
SENSOR_TYPE_PRECIPITATION_HOURS_DAY0: Final = "precipitation_hours_day0"

# Daily sensors - Day 1 (Tomorrow)
SENSOR_TYPE_WIND_SPEED_MAX_DAY1: Final = "wind_speed_max_day1"
SENSOR_TYPE_WIND_GUST_MAX_DAY1: Final = "wind_gust_max_day1"
SENSOR_TYPE_WIND_DIRECTION_DAY1: Final = "wind_direction_day1"
SENSOR_TYPE_SUNRISE_DAY1: Final = "sunrise_day1"
SENSOR_TYPE_SUNSET_DAY1: Final = "sunset_day1"
SENSOR_TYPE_SUNSHINE_DURATION_DAY1: Final = "sunshine_duration_day1"
SENSOR_TYPE_DAYLIGHT_DURATION_DAY1: Final = "daylight_duration_day1"
SENSOR_TYPE_UV_INDEX_DAY1: Final = "uv_index_day1"
SENSOR_TYPE_RAIN_SUM_DAY1: Final = "rain_sum_day1"
SENSOR_TYPE_SHOWERS_SUM_DAY1: Final = "showers_sum_day1"
SENSOR_TYPE_SNOWFALL_SUM_DAY1: Final = "snowfall_sum_day1"
SENSOR_TYPE_PRECIPITATION_SUM_DAY1: Final = "precipitation_sum_day1"
SENSOR_TYPE_PRECIPITATION_HOURS_DAY1: Final = "precipitation_hours_day1"

# Daily sensors - Day 2
SENSOR_TYPE_WIND_SPEED_MAX_DAY2: Final = "wind_speed_max_day2"
SENSOR_TYPE_WIND_GUST_MAX_DAY2: Final = "wind_gust_max_day2"
SENSOR_TYPE_WIND_DIRECTION_DAY2: Final = "wind_direction_day2"
SENSOR_TYPE_SUNRISE_DAY2: Final = "sunrise_day2"
SENSOR_TYPE_SUNSET_DAY2: Final = "sunset_day2"
SENSOR_TYPE_SUNSHINE_DURATION_DAY2: Final = "sunshine_duration_day2"
SENSOR_TYPE_DAYLIGHT_DURATION_DAY2: Final = "daylight_duration_day2"
SENSOR_TYPE_UV_INDEX_DAY2: Final = "uv_index_day2"
SENSOR_TYPE_RAIN_SUM_DAY2: Final = "rain_sum_day2"
SENSOR_TYPE_SHOWERS_SUM_DAY2: Final = "showers_sum_day2"
SENSOR_TYPE_SNOWFALL_SUM_DAY2: Final = "snowfall_sum_day2"
SENSOR_TYPE_PRECIPITATION_SUM_DAY2: Final = "precipitation_sum_day2"
SENSOR_TYPE_PRECIPITATION_HOURS_DAY2: Final = "precipitation_hours_day2"

# Sensor types for BRA (Avalanche Bulletins)
SENSOR_TYPE_AVALANCHE_RISK_TODAY: Final = "avalanche_risk_today"
SENSOR_TYPE_AVALANCHE_RISK_TOMORROW: Final = "avalanche_risk_tomorrow"
SENSOR_TYPE_AVALANCHE_ACCIDENTAL: Final = "avalanche_accidental"
SENSOR_TYPE_AVALANCHE_NATURAL: Final = "avalanche_natural"
SENSOR_TYPE_AVALANCHE_SUMMARY: Final = "avalanche_summary"
SENSOR_TYPE_AVALANCHE_BULLETIN_DATE: Final = "avalanche_bulletin_date"
SENSOR_TYPE_AVALANCHE_RISK_HIGH_ALT: Final = "avalanche_risk_high_altitude"
SENSOR_TYPE_AVALANCHE_RISK_LOW_ALT: Final = "avalanche_risk_low_altitude"
