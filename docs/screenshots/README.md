# Screenshots for Serac Documentation

This folder contains screenshots used in the main README.md documentation.

## Required Screenshots

### 1. **config-step1.png** - Location Setup
- **Where**: Settings → Devices & Services → Add Integration → Serac (Step 1)
- **What to show**:
  - Location Name field with example: "Chamonix Mont-Blanc"
  - Latitude field: 45.9237
  - Longitude field: 6.8694
  - "Next" button
- **Resolution**: 1920×1080 or similar
- **Crop**: Show just the config dialog, not entire screen

### 2. **config-step2.png** - Entity Prefix
- **Where**: Step 2 of config flow
- **What to show**:
  - Entity Prefix field with suggested value: "chamonix"
  - Description text showing example entity ID
  - "Next" button
- **Tip**: Shows the auto-suggestion feature

### 3. **config-step3.png** - Massif Selection
- **Where**: Step 3 of config flow
- **What to show**:
  - BRA Token field (can be filled or empty)
  - Massif multi-select dropdown (expanded showing ~5 massifs)
  - Selected: "Aravis" and "Mont-Blanc" (or similar)
  - "Submit" button
- **Tip**: Shows the multi-select UI

### 4. **devices-services.png** - Integration Added
- **Where**: Settings → Devices & Services
- **What to show**:
  - Serac integration card with logo
  - Shows "Chamonix Mont-Blanc (Serac)" or similar
  - Configure and other action buttons visible
- **Purpose**: Shows successful installation

### 5. **weather-card.png** - Weather Forecast Card
- **Where**: Lovelace dashboard
- **What to show**:
  - Weather-forecast card using `weather.serac_chamonix` entity
  - Current conditions + 7-day forecast
  - Temperature, conditions, humidity visible
- **YAML used**:
  ```yaml
  type: weather-forecast
  entity: weather.serac_chamonix
  forecast_type: daily
  ```

### 6. **weather-sensors.png** - Weather Sensor Card
- **Where**: Lovelace dashboard
- **What to show**:
  - Entities card showing 5-8 weather sensors:
    - Temperature
    - Humidity
    - Wind speed
    - Wind gust
    - European AQI
    - Elevation
- **YAML used**:
  ```yaml
  type: entities
  title: Mountain Conditions - Chamonix
  entities:
    - entity: sensor.serac_chamonix_temperature
    - entity: sensor.serac_chamonix_humidity
    - entity: sensor.serac_chamonix_wind_speed_current
    - entity: sensor.serac_chamonix_wind_gust_current
    - entity: sensor.serac_chamonix_european_aqi
    - entity: sensor.serac_chamonix_elevation
  ```

### 7. **avalanche-sensors.png** - Avalanche Risk Card
- **Where**: Lovelace dashboard
- **What to show**:
  - Entities card showing avalanche sensors for one massif (e.g., Aravis):
    - Risk Today
    - Risk Tomorrow
    - Risk High Altitude
    - Risk Low Altitude
    - Accidental description
- **YAML used**:
  ```yaml
  type: entities
  title: Avalanche Risk - Aravis
  entities:
    - entity: sensor.serac_chamonix_aravis_avalanche_risk_today
    - entity: sensor.serac_chamonix_aravis_avalanche_risk_tomorrow
    - entity: sensor.serac_chamonix_aravis_avalanche_risk_high_altitude
    - entity: sensor.serac_chamonix_aravis_avalanche_risk_low_altitude
    - entity: sensor.serac_chamonix_aravis_avalanche_accidental
  ```

### 8. **options-flow.png** - Options Configuration (OPTIONAL)
- **Where**: Settings → Devices & Services → Serac → Configure
- **What to show**:
  - Options dialog with BRA token field
  - Massif selection showing ability to change selections
- **Purpose**: Shows the options flow feature

## Screenshot Guidelines

### Quality
- **Resolution**: Minimum 1920×1080, can be higher
- **Format**: PNG (for sharp text)
- **Crop**: Remove unnecessary UI elements (HA sidebars are OK)
- **Language**: English preferred (easiest to understand globally)
- **Theme**: Light theme preferred for readability

### What to Avoid
- ❌ Personal information (if any location names are private)
- ❌ Other integration names/data visible
- ❌ Blurry or low-resolution images
- ❌ Dark mode (harder to see in documentation)

### Naming Convention
Use the exact names listed above:
- `config-step1.png`
- `config-step2.png`
- `config-step3.png`
- `devices-services.png`
- `weather-card.png`
- `weather-sensors.png`
- `avalanche-sensors.png`
- `options-flow.png` (optional)

## How to Take Screenshots

### macOS
1. **Cmd+Shift+4** → drag to select area
2. Screenshot saved to Desktop
3. Rename and move to this folder

### Windows
1. **Win+Shift+S** → select area
2. Screenshot copied to clipboard
3. Paste into image editor, save as PNG

### Linux
1. Use **Spectacle**, **Flameshot**, or **gnome-screenshot**
2. Select area and save

## After Taking Screenshots

1. **Save to this folder**: `docs/screenshots/`
2. **Update README.md**: Add image links in the Configuration section
3. **Commit**:
   ```bash
   git add docs/screenshots/
   git commit -m "docs: Add configuration screenshots"
   ```

## Image Optimization (Optional)

To reduce file size without losing quality:

```bash
# Install pngquant (optional)
brew install pngquant  # macOS
sudo apt install pngquant  # Linux

# Optimize PNGs
pngquant --quality=80-95 --ext .png --force *.png
```

---

## Status

**Completed** (4 screenshots):
- ✅ config-step1.png - Location Setup
- ✅ config-step2.png - Entity Prefix
- ✅ config-step3.png - Massif Selection
- ✅ devices-services.png - Integration Added

**Deferred** (4 screenshots):
- Screenshots 5-8 (Lovelace dashboard cards) will be added in a future update
