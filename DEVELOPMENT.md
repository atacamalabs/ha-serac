# Development Guide

## Phase 1 Status: ✅ COMPLETE

Version: **v0.1.0b1** (Beta 1)

### What's Included

#### Core Integration
- ✅ `manifest.json` - Integration metadata with dependencies
- ✅ `const.py` - Constants, massif mappings, sensor types
- ✅ `__init__.py` - Integration setup and platform loading
- ✅ `config_flow.py` - UI configuration with token + GPS validation
- ✅ `coordinator.py` - AROME data coordinator (1h updates)
- ✅ `strings.json` + `translations/en.json` - UI translations

#### AROME Integration
- ✅ `api/arome_client.py` - Wrapper for meteofrance-api
- ✅ `weather.py` - Weather entity with forecasts
- ✅ `sensor.py` - 11 AROME sensors

#### Repository Files
- ✅ `hacs.json` - HACS metadata
- ✅ `README.md` - Comprehensive documentation
- ✅ `LICENSE` - MIT License
- ✅ `.gitignore` - Python/HA ignores
- ✅ `.github/workflows/validate.yml` - CI validation

#### Git Repository
- ✅ Initialized with first commit
- ✅ Tagged as v0.1.0b1
- ✅ Ready for GitHub push

## Next Steps

### 1. Create GitHub Repository

```bash
# On GitHub.com:
# - Create new public repository: ha-better-mountain-weather
# - Don't initialize with README (we already have one)

# Then push your code:
git remote add origin https://github.com/YOUR_USERNAME/ha-better-mountain-weather.git
git branch -M main
git push -u origin main
git push origin v0.1.0b1
```

### 2. Create GitHub Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Select tag: `v0.1.0b1`
4. Mark as "Pre-release" ✓
5. Release title: "v0.1.0b1 - Beta 1: AROME Weather Integration"
6. Description:

```markdown
## 🏔️ First Beta Release - AROME Weather Forecasts

This is the first beta release of A Better Mountain Weather, featuring comprehensive weather forecasts for French mountain regions.

### ✨ Features

**Weather Entity:**
- Current conditions (temperature, humidity, pressure, wind, clouds)
- 7-day daily forecast
- 48-hour hourly forecast
- UV index monitoring

**11 AROME Sensors:**
- Elevation, Air Quality, UV Index
- Sunrise/Sunset times
- Cloud Coverage, Humidity
- Current Wind Speed & Gusts
- Today's Max Wind Speed & Gusts

### 📋 Requirements

- Home Assistant 2024.1.0 or newer
- AROME API token from Météo-France
- BRA API token (for Phase 2)
- HACS (recommended)

### 📦 Installation

1. Add this repository to HACS as a custom repository
2. Install "A Better Mountain Weather"
3. Restart Home Assistant
4. Add integration via Settings → Devices & Services
5. Enter your API tokens and GPS coordinates

### 🧪 Beta Testing

This is a beta release. Please report any issues on GitHub!

**Coming in Phase 2:**
- 8 BRA avalanche risk sensors
- Massif auto-detection with manual override

### 📍 Test Locations

- Chamonix: 45.9237, 6.8694
- Grenoble: 45.1885, 5.7245
- Val d'Isère: 45.4486, 6.9808
```

### 3. Update README with Your GitHub Username

Update the following in `README.md` and `manifest.json`:
- Replace `yourusername` with your actual GitHub username
- Commit and push the changes

```bash
# Find and replace yourusername in files
sed -i '' 's/yourusername/YOUR_ACTUAL_USERNAME/g' README.md
sed -i '' 's/yourusername/YOUR_ACTUAL_USERNAME/g' custom_components/better_mountain_weather/manifest.json

git add README.md custom_components/better_mountain_weather/manifest.json
git commit -m "Update GitHub username in documentation"
git push
```

### 4. Test Installation in Home Assistant

1. Add custom repository in HACS
2. Install the integration
3. Configure with test API tokens
4. Verify all entities appear
5. Check logs for errors

### 5. Share with Beta Testers

Send them:
- Repository URL
- Installation instructions from README
- How to get API tokens
- Recommended test locations

## Phase 2 - BRA Avalanche Integration (Next)

### To Implement

1. **BRA API Client** (`api/bra_client.py`)
   - XML parser using lxml
   - Authentication with BRA token
   - Massif resolution from GPS
   - Bulletin fetching and parsing

2. **BRA Coordinator** (update `coordinator.py`)
   - 6-hour update interval
   - Error handling for missing bulletins
   - Graceful degradation if BRA fails

3. **BRA Sensors** (update `sensor.py`)
   - 8 avalanche risk sensors
   - Risk levels, trends, snowpack quality
   - Altitude limits, snow conditions

4. **Config Flow Enhancement** (update `config_flow.py`)
   - Massif auto-detection display
   - Manual massif override option
   - Dropdown with all 40 massifs

5. **Integration Update** (update `__init__.py`)
   - Initialize BRA coordinator
   - Handle optional BRA data

### Release Process for Phase 2

```bash
# Update version in manifest.json to 0.2.0b1
# Make changes
git add .
git commit -m "Add BRA avalanche risk integration (Phase 2)"
git tag -a v0.2.0b1 -m "Beta 2: BRA avalanche risk sensors"
git push origin main
git push origin v0.2.0b1
# Create GitHub Release (mark as pre-release)
```

## Phase 3 - Polish & Stable Release (Final)

### To Implement

1. **Diagnostics** (`diagnostics.py`)
2. **Error Handling Improvements**
3. **Code Quality** (type hints, docstrings, linting)
4. **Documentation Updates**

### Release as v1.0.0

```bash
# Update version in manifest.json to 1.0.0
git add .
git commit -m "Stable release: v1.0.0"
git tag -a v1.0.0 -m "Stable release: AROME + BRA integration"
git push origin main
git push origin v1.0.0
# Create GitHub Release (NOT pre-release)
```

## Testing Checklist for Phase 1

- [ ] Install via HACS custom repository
- [ ] Config flow accepts both API tokens
- [ ] Config flow validates GPS coordinates
- [ ] Weather entity appears with correct name
- [ ] Weather entity shows current conditions
- [ ] Daily forecast (7 days) is available
- [ ] Hourly forecast (48 hours) is available
- [ ] All 11 AROME sensors appear
- [ ] Sensors update after 1 hour
- [ ] No errors in Home Assistant logs
- [ ] Test with invalid token (should show error)
- [ ] Test with invalid coordinates (should show error)
- [ ] Device info shows correct manufacturer/model

## File Structure Reference

```
/Users/g/claude/abetterweather/
├── .github/workflows/validate.yml
├── .gitignore
├── LICENSE
├── README.md
├── hacs.json
└── custom_components/better_mountain_weather/
    ├── __init__.py
    ├── manifest.json
    ├── const.py
    ├── config_flow.py
    ├── coordinator.py
    ├── weather.py
    ├── sensor.py
    ├── strings.json
    ├── translations/en.json
    └── api/
        ├── __init__.py
        └── arome_client.py
```

## API Token Acquisition

### AROME API Token
1. Go to https://portail-api.meteofrance.fr/
2. Create account / Sign in
3. Subscribe to "AROME" API
4. Generate API key
5. Copy key for configuration

### BRA API Token
1. Same portal: https://portail-api.meteofrance.fr/
2. Subscribe to "BRA" (Bulletin Risque Avalanche) API
3. Generate API key
4. Copy key for configuration

## Known Limitations (Phase 1)

1. **Sunrise/Sunset** - Currently using simplified calculation. Should be improved with proper astronomical library (e.g., astral)
2. **Air Quality** - Not provided by meteofrance-api, sensor will show "None"
3. **BRA Sensors** - Placeholder only, implemented in Phase 2
4. **Language** - Currently only English translations (French could be added)

## Dependencies

From `manifest.json`:
- `meteofrance-api>=1.5.0` - For AROME weather data
- `lxml>=5.0.0` - For BRA XML parsing (Phase 2)

## Useful Commands

```bash
# Validate manifest
python3 -c "import json; json.load(open('custom_components/better_mountain_weather/manifest.json'))"

# Check Python syntax
python3 -m py_compile custom_components/better_mountain_weather/*.py

# View git log
git log --oneline --graph

# View tags
git tag -l -n9

# Create new beta version
git tag -a vX.Y.Zb# -m "Beta message"
```

## Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/)
- [meteofrance-api GitHub](https://github.com/hacf-fr/meteofrance-api)
- [Météo-France API Portal](https://portail-api.meteofrance.fr/)
