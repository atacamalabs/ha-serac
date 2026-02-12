# Serac Integration - Project Status

**Last Updated**: 2026-02-12
**Current Version**: v1.7.1 🎉
**Status**: Vigilance Enhancements & Fixes Complete ✅
**Repository**: https://github.com/atacamalabs/ha-serac
**Roadmap**: See ROADMAP.md for development plan

## 🎯 Quick Overview

Serac (formerly "Better Mountain Weather") is a Home Assistant integration providing:
- **Weather data**: Météo-France AROME/ARPEGE models via Open-Meteo API
- **Air quality**: European AQI and pollutant sensors (5-day forecast)
- **Avalanche bulletins**: Météo-France BRA for French Alps (multiple massifs supported)

**Installation**: HACS custom repository

---

## ✅ Version 1.7.x - Vigilance Enhancements (CURRENT)

### 🎉 What's New in v1.7.1

**v1.7.1 (Latest):**
- 🐛 **Fixed entity ID validation** - Sanitizes special characters (é, à, etc.) from entity prefixes
- 🔧 **Unicode handling** - Proper accent removal using unicodedata normalization
- ✅ **HA 2027.2.0 compatible** - Resolves future deprecation warnings
- 🛡️ **All sensor types** - Fix applied to weather, avalanche, and vigilance sensors

**Technical Details:**
- Added `_sanitize_entity_id_part()` utility function
- Removes diacritics/accents from entity prefixes before entity ID construction
- Display names retain original characters (e.g., "Chamonix Dévoluy")
- Entity IDs now fully compliant: lowercase, numbers, underscores only

### 🎉 What's New in v1.7.0

**v1.7.0:**
- 🌪️ **Individual phenomenon sensors** - 9 new sensors (wind, avalanche, rain/flood, etc.)
- 📝 **Alert summary sensor** - Human-readable active alerts (e.g., "Yellow Alert: Wind, Rain/Flood")
- 🎯 **Easier card integration** - Each phenomenon has its own sensor with level (1-4)
- 🏷️ **Better icons** - Phenomenon-specific icons for each sensor type
- 📊 **12 total vigilance sensors** - 2 overall + 1 summary + 9 phenomena

### 🎉 What's New in v1.6.x Series

### 🎉 What's New in v1.6.0

**v1.6.0 (Latest):**
- 🚨 **Weather Alerts (Vigilance)** - Météo-France department-level weather alerts
- 📍 **GPS to Department mapping** - Automatic French department detection (23 departments)
- 🎯 **Alert sensors** - vigilance_level (1-4) and vigilance_color (green/yellow/orange/red)
- 🌪️ **Phenomena tracking** - Wind, rain/flood, snow/ice, thunderstorms, fog, extreme temps
- 🔑 **Separate token** - Optional vigilance_token field (requires separate API subscription)
- 🌐 **French translations** - Complete UI translations for vigilance features
- 📊 **Rich attributes** - All phenomena levels available in sensor attributes
- 🛡️ **Graceful degradation** - Works only for French coordinates, won't fail otherwise

### 🎉 What's New in v1.5.0

**v1.5.0:**
- 🔄 **Error retry logic** - Exponential backoff for network errors (3 attempts: 1s, 2s, 4s)
- 📊 **Enhanced logging** - Timing metrics, structured logs with context
- 🧪 **Unit tests** - 29 tests covering retry logic, coordinators, config flow
- 🔍 **Test infrastructure** - pytest with asyncio, fixtures for API clients
- 🛡️ **Improved resilience** - Smart retry (network errors yes, auth errors no)
- ⚡ **Better monitoring** - Log timing for API calls and coordinator updates

### 🎉 What's New in v1.4.x Series

**v1.4.2:**
- 🐛 **Fixed diagnostics** - Type checking for timestamp attributes

**v1.4.1:**
- 🐛 **Fixed diagnostics** - Proper attribute existence checks

**v1.4.0:**
- 📚 **Enhanced documentation** - FAQ section with 10 common questions
- 🔧 **Expanded troubleshooting** - 8 detailed troubleshooting sections
- 🇫🇷 **French translation** - Complete UI translation (config flow, options, errors)
- 📝 **CONTRIBUTING.md** - Comprehensive developer guide
- 🔍 **Diagnostics support** - Download integration diagnostics for debugging
- 📸 **Configuration screenshots** - 4 screenshots documenting setup flow

### 🎉 What's New in v1.3.0

**v1.3.0:**
- 🎨 **Custom logo** - Professional serac/mountain icon with weather elements
- 🏔️ **Visual identity** - Logo shows on GitHub README and in repo
- 📦 **Brands PR submitted** - Pending HA brands repository approval for UI display
- 🌟 **README enhancement** - Logo displayed prominently on GitHub
- 📝 **Complete documentation** - Added ROADMAP.md and SESSION_NOTES.md

### 🎉 What's New in v1.2.x Series

**v1.2.6:**
- ✨ **Complete cleanup** - Removes both entities AND devices for removed massifs
- 🔧 **Device registry integration** - Proper device lifecycle management

**v1.2.5:**
- ✨ **Entity cleanup** - Automatically removes entities for removed massifs
- 🧹 **Registry management** - Prevents orphaned entities

**v1.2.4:**
- 🐛 **Fixed TypeError** - OptionsFlow constructor call corrected

**v1.2.3:**
- 🐛 **Fixed AttributeError** - Removed incorrect __init__ override

**v1.2.1:**
- 🐛 **Fixed options flow** - Corrected voluptuous schema syntax

**v1.2.0:**
- ⚙️ **Options Flow** - Change massifs and BRA token without reinstalling
- 🎯 **Dynamic configuration** - Add/remove massifs via UI
- 🔄 **Automatic reload** - Changes apply immediately

### 🎉 What's New in v1.1.0

**v1.1.0:**
- 🗺️ **All 35 French massifs supported** - Expanded from 11 to 35 massifs
- ✅ **Northern Alps** (23 massifs) - All major ranges covered
- ✅ **Pyrenees** (11 massifs) - Complete Pyrenees coverage
- ✅ **Corsica** (1 massif) - Island mountain support
- 📝 **Updated documentation** - All massifs listed in README

### 🎉 What's New in v1.0.0 (Previous Release)

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

## 📦 Current Features (v1.1.0)

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
- **Multiple massifs support** - select 0 to 35 massifs via multi-select
- **Separate device per massif** - clear organization
- **35 massifs supported** - All French Alps (23), Pyrenees (11), Corsica (1)
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

### Supported Massifs (35 Total)

**Northern Alps (16)**: Chablais, Aravis, Mont-Blanc, Bauges, Beaufortain, Haute-Tarentaise, Chartreuse, Belledonne, Maurienne, Vanoise, Haute-Maurienne, Grandes-Rousses, Thabor, Vercors, Oisans, Pelvoux

**Southern Alps (7)**: Queyras, Dévoluy, Champsaur, Embrunais-Parpaillon, Ubaye, Mercantour, Alpes-Azur

**Pyrenees (11)**: Pays-Basque, Aspe-Ossau, Haute-Bigorre, Aure-Louron, Luchonnais, Couserans, Haute-Ariège, Orlu-St-Barthélémy, Capcir-Puymorens, Cerdagne-Canigou, Andorre

**Corsica (1)**: Corse

All massifs use numeric IDs (1-23, 40-50, 70) for the BRA API - see const.py for full mapping.

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

## 🚀 Future Enhancements (Post v1.2.6)

**See ROADMAP.md for detailed development plan**

### ✅ Priority 1: Options Flow (COMPLETE)
- ✅ Change massifs without reinstalling
- ✅ Update BRA token via UI
- ✅ Entity cleanup for removed massifs
- ✅ Device cleanup for removed massifs
- **Status**: Shipped in v1.2.0-v1.2.6

### ✅ Priority 2: Logo & Branding (COMPLETE)
- ✅ Custom logo designed (minimalist pictogram)
- ✅ Logo shows on GitHub README
- ✅ Icon integrated in repo (256×256 and 512×512)
- ⏳ Brands PR submitted (PR #9547) - awaiting approval
- **Status**: Shipped in v1.3.0, HA UI pending brands approval
- **PR**: https://github.com/home-assistant/brands/pull/9547

### ✅ Priority 3: Enhanced Documentation (COMPLETE)
- ✅ FAQ section (10 questions)
- ✅ Expanded troubleshooting (8 sections)
- ✅ French translation (complete UI)
- ✅ CONTRIBUTING.md developer guide
- ✅ Configuration screenshots (4 of 8)
- **Status**: Shipped in v1.4.0
- **Note**: Lovelace dashboard screenshots deferred for later

### ✅ Priority 4: Code Quality & Diagnostics (COMPLETE)
- ✅ Diagnostics support (v1.4.0-1.4.2)
- ✅ Error retry logic with exponential backoff
- ✅ Enhanced logging with timing metrics
- ✅ Unit tests (29 tests: retry, coordinators, config flow)
- ✅ Test infrastructure (pytest + asyncio)
- **Status**: Shipped in v1.5.0

### ✅ Priority 5: Weather Alerts (Vigilance) (COMPLETE)
- ✅ Météo-France Vigilance API integration
- ✅ Department-level weather alerts (23 departments)
- ✅ Color-coded warnings (Green/Yellow/Orange/Red)
- ✅ Phenomena: wind, rain/flood, thunderstorms, snow/ice, fog, extreme temps
- ✅ Separate vigilance_token configuration
- ✅ 2 vigilance sensors (level & color) with rich attributes
- **Status**: Shipped in v1.6.0

### Future Backlog
- Hourly BRA risk evolution
- Snow depth sensors
- Multi-language support (German, Italian)
- Custom Lovelace card

---

## 📚 Version History

- **v1.7.1** (2026-02-12): 🐛 Fixed entity ID validation, unicode character sanitization
- **v1.7.0** (2026-02-12): 🌪️ Individual phenomenon sensors, alert summary sensor (12 vigilance sensors total)
- **v1.6.2** (2026-02-12): 🐛 Fixed Vigilance API data extraction
- **v1.6.1** (2026-02-12): 🔍 Added debug logging for Vigilance API
- **v1.6.0** (2026-02-12): 🚨 Weather Alerts (Vigilance API), department detection, 2 new sensors
- **v1.5.0** (2026-02-12): 🧪 Error retry logic, enhanced logging, 29 unit tests
- **v1.4.2** (2026-02-12): 🐛 Fix diagnostics timestamp type error
- **v1.4.1** (2026-02-12): 🐛 Fix diagnostics attribute check
- **v1.4.0** (2026-02-12): 📚 Enhanced docs, French translation, diagnostics, screenshots
- **v1.3.0** (2026-02-12): 🎨 Custom logo and branding
- **v1.2.6** (2026-02-12): ✨ Device cleanup for removed massifs
- **v1.2.5** (2026-02-12): ✨ Entity cleanup for removed massifs
- **v1.2.4** (2026-02-12): 🐛 Fix TypeError in OptionsFlow constructor
- **v1.2.3** (2026-02-12): 🐛 Fix AttributeError in OptionsFlow
- **v1.2.2** (2026-02-12): 🔧 Improved error logging
- **v1.2.1** (2026-02-12): 🐛 Fix options flow schema syntax
- **v1.2.0** (2026-02-12): ⚙️ Options Flow feature
- **v1.1.0** (2026-02-11): 🗺️ All 35 French massifs supported (Alps, Pyrenees, Corsica)
- **v1.0.1** (2026-02-11): 🐛 Fix translation placeholder error in config flow
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
- No custom logo yet - **Priority 2 for v1.3.0**
- No diagnostics.py yet

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

See **ROADMAP.md** for comprehensive development plan.

**All current priorities complete!** Future enhancements:
- Hourly avalanche risk evolution
- Snow depth sensors (if data becomes available)
- Custom Lovelace card
- Multi-language support (German, Italian)

---

**Status**: Production ready v1.7.1 released 🎉
**Next milestone**: TBD - Feature requests welcome!
