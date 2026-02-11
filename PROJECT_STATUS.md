# Serac Integration - Project Status

**Last Updated**: 2026-02-11
**Current Version**: v1.0.0 🎉
**Status**: v1.0.0 Release Complete ✅
**Repository**: https://github.com/atacamalabs/ha-serac

## 🎯 Quick Overview

Serac (formerly "Better Mountain Weather") is a Home Assistant integration providing:
- **Weather data**: Météo-France AROME/ARPEGE models via Open-Meteo API
- **Air quality**: European AQI and pollutant sensors (5-day forecast)
- **Avalanche bulletins**: Météo-France BRA for French Alps (multiple massifs supported)

**Installation**: HACS custom repository

---

## ✅ Version 1.0.0 - Complete Rebrand (RELEASED)

### 🎉 What's New in v1.0.0

**Major Changes:**
- 🏔️ **Rebranded to "Serac"** - New name, new identity
- 🆔 **Smart Entity Naming** - User-defined prefixes for clean entity IDs
- 📦 **Repository Renamed** - `ha-serac` (GitHub auto-redirects from old URL)
- 🎨 **Improved UX** - 3-step config flow with entity prefix selection

**Breaking Changes:**
- ⚠️ All entity IDs changed (old coordinate-based → new prefix-based)
- ⚠️ Domain changed: `better_mountain_weather` → `serac`
- ⚠️ Users must reinstall (see MIGRATION_v1.md)

### Entity Naming Pattern

**User chooses prefix during setup:**
- Weather: `sensor.serac_{prefix}_temperature`
- Avalanche: `sensor.serac_{prefix}_{massif}_avalanche_risk_today`
- Weather entity: `weather.serac_{prefix}`

**Example with prefix "chamonix":**
```
sensor.serac_chamonix_temperature
sensor.serac_chamonix_aravis_avalanche_risk_today
weather.serac_chamonix
```

---

## 📦 Current Features (v1.0.0)

### Phase 1 & 2: Complete ✅

**Weather Integration:**
- Open-Meteo API (AROME & ARPEGE models)
- Weather entity with 7-day forecast
- **51 sensors total**:
  - 1 static sensor (elevation)
  - 11 current weather sensors
  - 39 daily sensors (3 days × 13 parameters)
- Air quality sensors (AQI, PM2.5, PM10, NO₂, O₃, SO₂) - 5-day forecast
- Hourly precipitation forecasts
- Parallel API calls for performance
- ~158 weather entity attributes with units

**BRA Avalanche Integration:**
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

### Phase 3: Complete ✅

**Polish & Rebrand:**
- ✅ Integration renamed to "Serac"
- ✅ Repository renamed to `ha-serac`
- ✅ Entity prefix system implemented
- ✅ Improved entity naming (human-readable)
- ✅ Updated documentation (README, migration guide)
- ✅ Version bumped to 1.0.0

---

## 🏗️ Architecture

### Config Data Structure
```python
{
    "latitude": 46.03,
    "longitude": 6.31,
    "location_name": "Chamonix Mont-Blanc",      # User-provided (required)
    "entity_prefix": "chamonix",                 # User-provided (required)
    "bra_token": "...",                          # Optional
    "massif_ids": [1, 2, 3],                     # List (can be empty)
}
```

### Coordinators
- **AromeCoordinator**: Weather + air quality (1-hour updates)
- **BraCoordinator**: One per massif (6-hour updates)
  - Stored in: `hass.data[DOMAIN][entry_id]["bra_coordinators"][massif_id]`

### Devices Structure
1. **Main weather device**: `"{location_name} (Serac)"`
   - Contains: All weather sensors, air quality sensors
   - Example: "Chamonix Mont-Blanc (Serac)"

2. **BRA devices** (one per massif): `"{location_name} - {massif_name} (Serac)"`
   - Contains: 8 avalanche sensors
   - Example: "Chamonix Mont-Blanc - Aravis (Serac)"

### Entity ID Patterns
- Weather entity: `weather.serac_{prefix}`
- Weather sensors: `sensor.serac_{prefix}_{sensor_type}`
- Avalanche sensors: `sensor.serac_{prefix}_{massif}_{sensor_type}`

### Unique IDs (internal)
- Weather: `serac_{lat}_{lon}_weather`
- Sensors: `serac_{lat}_{lon}_{sensor_type}`
- BRA sensors: `serac_{lat}_{lon}_{massif_id}_{sensor_type}`

---

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

---

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

---

## 📝 File Structure

```
custom_components/serac/
├── __init__.py              # Setup, multiple coordinators, entity migration
├── config_flow.py           # 3-step UI: location → prefix → massifs
├── const.py                 # Constants, MASSIF_IDS mapping, CONF_ENTITY_PREFIX
├── coordinator.py           # AromeCoordinator, BraCoordinator
├── sensor.py                # 51 weather sensors + BraSensor class
├── weather.py               # Weather entity with ~158 attributes
├── manifest.json            # Integration metadata (version: 1.0.0)
├── strings.json             # UI strings
└── api/
    ├── openmeteo_client.py  # Open-Meteo API client
    ├── airquality_client.py # Air quality API client
    └── bra_client.py        # BRA API client (Europe/Paris timezone)
```

---

## 🚀 Future Enhancements (Post v1.0.0)

### Priority 1: Options Flow 🟡
- Change massifs without reinstalling
- Update entity prefix (optional)
- Modify BRA token
- **Estimated effort**: 2-3 hours

### Priority 2: Logo & Branding 🟢
- Custom logo for integration
- Icon for HACS listing
- Improve visual identity
- **Estimated effort**: 1-2 hours (once logo designed)

### Priority 3: Expand Massif Support 🟢
- Add remaining French Alps massifs (12 more)
- Add Pyrenees massifs (16 total)
- Add Corsica massif (1)
- **Total potential**: 40+ massifs

### Nice-to-Have Features
- Hourly BRA risk evolution
- Avalanche bulletin PDF links
- Snow depth sensors
- Multi-language support (French, German, Italian)
- Enhanced diagnostics support
- Custom update intervals

---

## 📚 Version History

- **v1.0.0** (2026-02-11): 🎉 Complete rebrand to "Serac", smart entity naming, breaking changes
- **v0.6.0** (2026-02-11): Custom location names, multiple massifs, separate devices
- **v0.5.4** (2026-02-11): Fix BRA timezone (Europe/Paris)
- **v0.5.0** (2026-02-11): BRA avalanche integration (Phase 2)
- **v0.4.5**: Parallel API calls, performance improvements
- **v0.3.x**: Core weather integration (Phase 1)

---

## 🐛 Known Issues & Limitations

### Current Limitations
- BRA data only available in winter season (~December-May)
- Limited to 11 massifs (expandable to 40+)
- No options flow yet (must re-add integration to change massifs)

### All Previous Issues Resolved ✅
- ✅ Timezone handling (Europe/Paris → UTC)
- ✅ Extra attributes None check
- ✅ Multiple massifs support
- ✅ Custom location naming
- ✅ Entity migration for structure changes
- ✅ Entity naming clarity

---

## 🔧 Development Patterns

### Important Conventions
- **Timezone**: Parse BRA times as Europe/Paris, convert to UTC for storage
- **Multiple coordinators**: Store in dict keyed by massif_id
- **Entity migration**: Add cleanup logic when structure changes
- **Parallel API**: Use `asyncio.gather()` for performance
- **Error handling**: Log warnings for BRA failures, don't fail setup
- **Entity IDs**: Set explicitly using `entity_id` property
- **Unique IDs**: Use coordinates for uniqueness, not entity IDs

### Testing Checklist
```bash
# Test scenarios
- [x] 0 massifs (weather only)
- [x] 1 massif
- [x] Multiple massifs (3+)
- [x] Out-of-season BRA behavior
- [x] Timezone correctness
- [x] Entity prefix validation
- [x] Suggested prefix generation

# Commands
tail -f /config/home-assistant.log | grep serac
# Developer Tools → Services → homeassistant.reload_config_entry
```

---

## 📞 Support & Credits

**Developer**: Atacama Labs
**Repository**: https://github.com/atacamalabs/ha-serac
**Issues**: https://github.com/atacamalabs/ha-serac/issues
**Email**: hi@atacamalabs.com

**Data Sources**:
- Weather: Open-Meteo (Météo-France AROME/ARPEGE)
- Avalanche: Météo-France BRA
- Air Quality: Open-Meteo

---

## 🎯 Next Steps

See **NEXT_STEPS.md** for post-v1.0.0 roadmap.

---

**Status**: Production ready v1.0.0 released 🎉
