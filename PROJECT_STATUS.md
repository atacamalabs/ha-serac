# Better Mountain Weather Integration - Project Status

**Last Updated**: 2026-02-11
**Current Version**: v0.6.0
**Status**: Phase 2 Complete ✅, Ready for Phase 3
**Snapshot Branch**: `snapshot-v0.6.0` (stable fallback)

## 🎯 Quick Start for Next Session

1. **Read this file first** - Complete project overview
2. **Check NEXT_STEPS.md** - Immediate action items
3. **Review recent commits**: `git log --oneline -10`
4. **Test status**: All features working, user has tested v0.6.0 ✅

## 📦 Project Overview

Home Assistant custom integration providing:
- **Weather data**: Météo-France AROME/ARPEGE models via Open-Meteo API
- **Air quality**: European AQI and pollutant sensors (5-day forecast)
- **Avalanche bulletins**: Météo-France BRA for French Alps (multiple massifs supported)

**Repository**: https://github.com/atacamalabs/ha-better-mountain-weather
**Installation**: HACS custom repository

## ✅ Phase 1: Core Weather Integration (COMPLETE)

### Features
- Open-Meteo API integration (AROME & ARPEGE models)
- Weather entity with 7-day forecast
- **51 sensors total**:
  - 1 static sensor (elevation)
  - 11 current weather sensors
  - 39 daily sensors (3 days × 13 parameters)
- Air quality sensors (AQI, PM2.5, PM10, NO2, O3, SO2) - 5-day forecast
- Hourly precipitation forecasts (6-hour and 48-hour)
- Parallel API calls for performance
- ~158 weather entity attributes with units

## ✅ Phase 2: BRA Avalanche Integration (COMPLETE)

### Features
- **8 avalanche sensors per massif**:
  - Risk Today/Tomorrow (1-5 scale)
  - Risk High/Low Altitude
  - Accidental/Natural avalanche descriptions (text)
  - Summary (text)
  - Bulletin Date (Europe/Paris timezone)
- **Custom location naming** - user-provided instead of coordinates
- **Multiple massifs support** - select 0 to 11 massifs via multi-select
- **Separate device per massif** - clear organization
- **11 massifs supported** (Haute-Savoie and Savoie regions)
- Graceful out-of-season handling
- 6-hour update intervals

### Technical Implementation
```
Files Modified:
- api/bra_client.py: BRA API with OAuth2/API key auth, Europe/Paris timezone
- coordinator.py: Multiple BraCoordinators (one per massif)
- sensor.py: BraSensor with massif-specific devices
- config_flow.py: Custom location name + massif multi-select
- __init__.py: Multiple coordinator management + entity migration
- const.py: MASSIF_IDS mapping, CONF_MASSIF_IDS constant
```

## 🏗️ Current Architecture

### Config Data Structure
```python
{
    "latitude": 46.03,
    "longitude": 6.31,
    "location_name": "Station de Ski Orange",  # User-provided (required)
    "bra_token": "...",                         # Optional
    "massif_ids": [1, 2, 3],                    # List (can be empty)
}
```

### Coordinators
- **AromeCoordinator**: Weather + air quality (1-hour updates)
- **BraCoordinator**: One per massif (6-hour updates)
  - Stored in: `hass.data[DOMAIN][entry_id]["bra_coordinators"][massif_id]`

### Devices Structure
1. **Main weather device**: `"{location_name} Mountain Weather"`
   - Contains: All weather sensors, air quality sensors
   - Example: "Station de Ski Orange Mountain Weather"

2. **BRA devices** (one per massif): `"{location_name} - {massif_name}"`
   - Contains: 8 avalanche sensors
   - Example: "Station de Ski Orange - Aravis"

### Entity ID Patterns
- Weather: `sensor.location_46_03_6_31_mountain_weather_temperature`
- AQI: `sensor.location_46_03_6_31_mountain_weather_air_quality_index_max_day_0`
- BRA: `sensor.location_46_03_6_31_mountain_weather_1_avalanche_risk_today`
  - Note: Includes `massif_id` (e.g., `_1_` for Chablais)

### Sensor Naming
- Weather sensors: Standard names ("Temperature", "Wind Speed")
- BRA sensors: Include massif name ("Avalanche Risk Today - Aravis")

## 🔌 API Details

### Open-Meteo API
- **Endpoint**: https://api.open-meteo.com/v1/forecast
- **Auth**: None required
- **Models**: AROME (2.5km) + ARPEGE (fallback)
- **Update**: Hourly
- **Data**: Current, daily/hourly forecasts, air quality

### BRA API
- **Endpoint**: https://public-api.meteofrance.fr/public/DPBRA/v1
- **Auth**: API key in header (`apikey: {token}`)
- **Format**: XML bulletins
- **Update**: Every 6 hours
- **Timezone**: Europe/Paris (converted to UTC internally)
- **Season**: Winter only (~December-May)

## 🗺️ Massif Configuration

### Supported Massifs (Numeric IDs)
```python
MASSIF_IDS = {
    1: ("Chablais", "CHABLAIS"),
    2: ("Aravis", "ARAVIS"),
    3: ("Mont-Blanc", "MONT-BLANC"),
    4: ("Bauges", "BAUGES"),
    5: ("Beaufortain", "BEAUFORTAIN"),
    6: ("Haute-Tarentaise", "HAUTE-TARENTAISE"),
    9: ("Maurienne", "MAURIENNE"),
    10: ("Vanoise", "VANOISE"),
    11: ("Haute-Maurienne", "HAUTE-MAURIENNE"),
}
```

**Expansion potential**: 40+ massifs across Alps, Pyrenees, Corsica

## 📝 File Structure

```
custom_components/better_mountain_weather/
├── __init__.py              # Setup, multiple coordinators, entity migration
├── config_flow.py           # UI: location name + massif multi-select
├── const.py                 # Constants, MASSIF_IDS mapping
├── coordinator.py           # AromeCoordinator, BraCoordinator
├── sensor.py                # 51 weather sensors + BraSensor class
├── weather.py               # Weather entity with ~158 attributes
├── manifest.json            # Integration metadata (version: 0.6.0)
├── strings.json             # UI strings
└── api/
    ├── openmeteo_client.py  # Open-Meteo API client
    ├── airquality_client.py # Air quality API client
    └── bra_client.py        # BRA API client (Europe/Paris timezone)
```

## 🚧 Phase 3: Polish & Enhancement (NEXT)

### Priority 1: Integration Rename 🔴
- **Current**: `better_mountain_weather`
- **Target**: TBD by user
- **Impact**: BREAKING CHANGE
  - All entity IDs will change
  - Users must reinstall integration
  - Automations/dashboards need updates
- **Plan Needed**: Migration strategy, user communication, documentation

### Priority 2: Branding 🟡
- Add custom logo/icon
- Update integration branding
- Improve visual identity

### Priority 3: Fine-tuning 🟢
- **Performance**: Monitor API response times, optimize calls
- **Reliability**: Better error handling, retry logic
- **UX**: Options flow (change massifs without reinstalling)
- **Documentation**: User guides, migration docs, troubleshooting

### Nice-to-Have Features
- Support all 40+ French massifs
- Hourly BRA risk evolution
- Avalanche bulletin PDF links
- Snow depth sensors
- Multi-language support
- Options flow for massif configuration

## 🐛 Known Issues & Resolutions

### All Resolved ✅
- ✅ Timezone handling (Europe/Paris → UTC)
- ✅ Extra attributes None check
- ✅ Multiple massifs support
- ✅ Custom location naming
- ✅ Entity migration for structure changes

### Current Limitations
- BRA data only available in winter season
- Limited to 11 massifs (expandable to 40+)
- No options flow (must re-add integration to change massifs)
- Integration name is generic

## 🔧 Development Patterns

### Important Conventions
- **Timezone**: Parse BRA times as Europe/Paris, convert to UTC for storage
- **Multiple coordinators**: Store in dict keyed by massif_id
- **Entity migration**: Add cleanup logic when structure changes
- **Parallel API**: Use `asyncio.gather()` for performance
- **Error handling**: Log warnings for BRA failures, don't fail setup

### Testing Checklist
```bash
# Test scenarios
- [ ] 0 massifs (weather only)
- [ ] 1 massif
- [ ] Multiple massifs (3+)
- [ ] Out-of-season BRA behavior
- [ ] Timezone correctness
- [ ] Entity migration from v0.5.x

# Commands
tail -f /config/home-assistant.log | grep better_mountain_weather
# Developer Tools → Services → homeassistant.reload_config_entry
```

## 📚 Version History

- **v0.6.0** (2026-02-11): Custom location names, multiple massifs, separate devices
- **v0.5.4** (2026-02-11): Fix BRA timezone (Europe/Paris)
- **v0.5.3** (2026-02-11): Explicit UTC timezone for bulletin_date
- **v0.5.2** (2026-02-11): Fix extra_attributes_fn None check
- **v0.5.1** (2026-02-11): Add extra_attributes_fn field
- **v0.5.0** (2026-02-11): BRA avalanche integration (Phase 2)
- **v0.4.5**: Parallel API calls, performance improvements
- **v0.3.x**: Core weather integration (Phase 1)

## 🎯 Next Session Action Items

See **NEXT_STEPS.md** for detailed task list.

### Immediate Priorities
1. **Plan integration rename** (breaking change strategy)
2. **Design/add logo** (branding)
3. **Options flow** (change massifs without reinstall)
4. **Documentation** (README, migration guide, troubleshooting)

### Before Making Changes
- Create task list for tracking
- Test locally if possible
- Document breaking changes
- Update version in manifest.json
- Create snapshot branch for major changes

## 📞 Support & Credits

**Developer**: Atacama Labs
**AI Assistant**: Claude (Anthropic)
**Data Sources**:
- Weather: Open-Meteo (Météo-France AROME/ARPEGE)
- Avalanche: Météo-France BRA
- Air Quality: Open-Meteo

**GitHub**: https://github.com/atacamalabs/ha-better-mountain-weather
**Issues**: https://github.com/atacamalabs/ha-better-mountain-weather/issues

---

**Note**: This integration is in active development. Phase 2 complete, Phase 3 planning in progress.
