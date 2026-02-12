# Serac Integration - Project Status

**Last Updated**: 2026-02-12
**Current Version**: v1.2.6 🎉
**Status**: Options Flow Complete ✅
**Repository**: https://github.com/atacamalabs/ha-serac
**Roadmap**: See ROADMAP.md for development plan

## 🎯 Quick Overview

Serac (formerly "Better Mountain Weather") is a Home Assistant integration providing:
- **Weather data**: Météo-France AROME/ARPEGE models via Open-Meteo API
- **Air quality**: European AQI and pollutant sensors (5-day forecast)
- **Avalanche bulletins**: Météo-France BRA for French Alps (multiple massifs supported)

**Installation**: HACS custom repository

---

## ✅ Version 1.2.6 - Options Flow Complete (CURRENT)

### 🎉 What's New in v1.2.x Series

**v1.2.6 (Latest):**
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

### Priority 2: Logo & Branding 🎨
- Custom logo for integration (QUICK WIN)
- Icon for HACS listing
- Improve visual identity
- **Estimated effort**: 1-2 hours (once logo designed)

### Priority 3: Enhanced Documentation 📚
- Add screenshots to README
- FAQ section
- French translation
- **Estimated effort**: 3-4 hours

### Priority 4: Code Quality & Diagnostics 🔧
- Add diagnostics.py
- Unit tests
- Error retry logic
- **Estimated effort**: 4-6 hours

### Future Backlog
- Hourly BRA risk evolution
- Weather alerts/warnings
- Snow depth sensors
- Multi-language support (German, Italian)
- Custom Lovelace card

---

## 📚 Version History

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

See **ROADMAP.md** for comprehensive development plan (v1.3.0 and beyond).

**Immediate next**: Logo & Branding (Priority 2 - quick win)

---

**Status**: Production ready v1.2.6 released 🎉
**Next milestone**: v1.3.0 (Logo + Enhanced Documentation)
