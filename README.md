# Serac 🏔️

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/atacamalabs/ha-serac.svg)](https://github.com/atacamalabs/ha-serac/releases)
[![License](https://img.shields.io/github/license/atacamalabs/ha-serac.svg)](LICENSE)

**Mountain weather and avalanche forecasts for Home Assistant**

Serac is a comprehensive Home Assistant integration providing detailed mountain weather data and avalanche bulletins for the French Alps, Pyrenees, and Corsica. Get accurate forecasts from Météo-France AROME/ARPEGE models and real-time avalanche risk assessments.

---

## Features

### 🌤️ Weather Data
- **Weather entity** with 7-day daily and 48-hour hourly forecasts
- **51 weather sensors** including:
  - Current conditions (temperature, humidity, wind, precipitation, cloud coverage)
  - 3-day detailed forecasts (13 parameters per day)
  - Sunrise/sunset, UV index, sunshine duration
  - Hourly precipitation forecasts

### 🌫️ Air Quality
- **6 air quality sensors** with 5-day forecasts:
  - European Air Quality Index (AQI)
  - PM2.5, PM10, NO₂, O₃, SO₂ levels

### ⚠️ Avalanche Bulletins
- **8 avalanche sensors per massif**:
  - Risk levels (today & tomorrow, 1-5 scale)
  - High/low altitude risk zones
  - Accidental & natural avalanche descriptions
  - Bulletin summaries and dates
- **Multiple massifs support** - select 0-11 massifs from Haute-Savoie/Savoie regions
- **Separate device per massif** for clear organization

### 🎯 Smart Entity Naming
- **User-defined entity prefix** for clean, memorable entity IDs
- Example: `sensor.serac_chamonix_temperature`
- Avalanche sensors include massif: `sensor.serac_chamonix_aravis_avalanche_risk_today`

---

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on **Integrations**
3. Click the **⋮** (three dots) in the top right
4. Select **Custom repositories**
5. Add repository URL: `https://github.com/atacamalabs/ha-serac`
6. Select category: **Integration**
7. Click **Add**
8. Find **Serac** in HACS and click **Download**
9. **Restart Home Assistant**
10. Go to **Settings** → **Devices & Services** → **Add Integration**
11. Search for **Serac** and follow the setup steps

### Manual Installation

1. Download the `custom_components/serac` folder from this repository
2. Copy it to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for **Serac**

---

## Configuration

### Setup Steps

1. **Add Integration**
   - Go to **Settings** → **Devices & Services**
   - Click **+ Add Integration**
   - Search for **Serac**

2. **Location Setup**
   - Enter a name for your location (e.g., "Chamonix Mont-Blanc")
   - Enter GPS coordinates (latitude, longitude)
   - Example: Chamonix (45.9237, 6.8694)

3. **Entity Prefix**
   - Choose a short identifier for your entities
   - Suggested automatically from your location name
   - Used in entity IDs: `sensor.serac_{your_prefix}_temperature`

4. **Avalanche Data (Optional)**
   - Add Météo-France BRA API token (optional)
   - Select massifs for avalanche bulletins (0-11 massifs)
   - Skip if you only want weather data

### Finding GPS Coordinates

- **Google Maps**: Right-click on location → Click coordinates to copy
- **OpenStreetMap**: [openstreetmap.org](https://www.openstreetmap.org/)
- **Your Phone**: Use GPS app to get current coordinates

### Getting BRA API Token (Optional)

For avalanche bulletins, you need a Météo-France BRA API token:

1. Visit [Météo-France API Portal](https://portail-api.meteofrance.fr/)
2. Create an account
3. Subscribe to the **BRA (Bulletin Risque Avalanche)** API
4. Copy your API key
5. Enter it during Serac setup or leave empty to skip avalanche features

---

## Supported Massifs

### Haute-Savoie & Savoie (11 Massifs)

Currently supported massifs for avalanche bulletins:
- **Chablais** • **Aravis** • **Mont-Blanc**
- **Bauges** • **Beaufortain** • **Haute-Tarentaise**
- **Maurienne** • **Vanoise** • **Haute-Maurienne**

*More massifs across the Alps, Pyrenees, and Corsica coming in future updates.*

---

## Usage Examples

### Weather Card

```yaml
type: weather-forecast
entity: weather.serac_chamonix
forecast_type: daily
```

### Sensor Cards

```yaml
type: entities
title: Mountain Conditions
entities:
  - entity: sensor.serac_chamonix_temperature
  - entity: sensor.serac_chamonix_wind_speed_current
  - entity: sensor.serac_chamonix_wind_gust_current
  - entity: sensor.serac_chamonix_european_aqi
  - entity: sensor.serac_chamonix_elevation
```

### Avalanche Risk Card

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

### Automation: High Wind Alert

```yaml
automation:
  - alias: "Mountain High Wind Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.serac_chamonix_wind_gust_max_day0
        above: 60
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ High Wind Warning"
          message: "Wind gusts expected to exceed 60 km/h today in Chamonix!"
```

### Automation: Avalanche Risk Alert

```yaml
automation:
  - alias: "High Avalanche Risk Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.serac_chamonix_aravis_avalanche_risk_today
        above: 3
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Avalanche Warning"
          message: "Avalanche risk level {{ states('sensor.serac_chamonix_aravis_avalanche_risk_today') }} in Aravis today!"
```

---

## Data Sources

- **Weather Forecasts**: [Open-Meteo](https://open-meteo.com/) (Météo-France AROME 2.5km & ARPEGE models)
- **Avalanche Bulletins**: [Météo-France BRA](https://meteofrance.com/meteo-montagne) (Bulletin Risque Avalanche)
- **Air Quality**: Open-Meteo European AQI

All data is provided by **Météo-France**, the French national meteorological service.

---

## Update Frequency

- **Weather Data**: Every 1 hour
- **Air Quality**: Every 1 hour
- **Avalanche Bulletins**: Every 6 hours (published once daily)

---

## Migrating from v0.6.0

**⚠️ Breaking change:** Serac v1.0.0 requires a complete reinstall.

See **[MIGRATION_v1.md](MIGRATION_v1.md)** for detailed migration instructions.

**Quick summary:**
1. Remove old "Better Mountain Weather" integration
2. Remove old HACS repository
3. Restart Home Assistant
4. Add new repository: `https://github.com/atacamalabs/ha-serac`
5. Install Serac and reconfigure
6. Update automations and dashboards with new entity IDs

---

## Troubleshooting

### Integration doesn't appear after installation
- Restart Home Assistant completely (not just reload)
- Check **Settings** → **System** → **Logs** for errors
- Verify the `custom_components/serac` folder exists

### Weather data not updating
- Check your internet connection
- Verify coordinates are correct and within supported regions
- Wait for first update (up to 1 hour)
- Check logs for API errors

### Avalanche sensors not appearing
- Verify you entered a valid BRA API token
- Verify you selected at least one massif
- Avalanche bulletins are seasonal (~December-May)
- Check logs for BRA coordinator errors

### Entity IDs don't match examples
- Entity IDs use your chosen prefix
- Example: If you chose prefix "home", entities will be `sensor.serac_home_temperature`
- Check **Developer Tools** → **States** and filter by "serac"

### "Cannot connect" error during setup
- Verify GPS coordinates format (e.g., 45.9237, not 45° 55' 25")
- Check your internet connection
- Ensure Open-Meteo service is accessible
- Try coordinates of a known location (e.g., Chamonix: 45.9237, 6.8694)

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Feature Requests & Bug Reports
- **Issues**: [GitHub Issues](https://github.com/atacamalabs/ha-serac/issues)
- **Discussions**: [GitHub Discussions](https://github.com/atacamalabs/ha-serac/discussions)

---

## Roadmap

### Planned Features
- [ ] Options flow (change massifs without reinstalling)
- [ ] Support for all 40+ French massifs
- [ ] Custom logo and branding
- [ ] Enhanced error handling and diagnostics
- [ ] Multi-language support (French, German, Italian)
- [ ] Snow depth sensors
- [ ] Hourly avalanche risk evolution

---

## License

[MIT License](LICENSE)

---

## Acknowledgments

- **Météo-France** for providing excellent weather and avalanche data APIs
- **Open-Meteo** for API access to Météo-France models
- Home Assistant community for development support

---

## Disclaimer

This integration provides weather and avalanche information **for informational purposes only**. Always consult official sources and professional mountain guides before making decisions in mountain environments.

**The authors are not responsible for any incidents resulting from use of this data.**

---

## Support

- 🐛 **Bug reports**: [GitHub Issues](https://github.com/atacamalabs/ha-serac/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/atacamalabs/ha-serac/discussions)
- 📧 **Email**: hi@atacamalabs.com

---

**Made with ❤️ for the mountain community**

*Serac: Named after the ice formations found in glaciers and mountain environments.*
