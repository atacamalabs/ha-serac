# A Better Mountain Weather

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A comprehensive Home Assistant integration providing detailed mountain weather data for the French Alps, Pyrenees, and Corsica. This integration combines two Météo-France APIs to deliver accurate forecasts and avalanche risk information.

## Features

### Phase 1 (Current) - AROME Weather Integration

**Weather Entity:**
- Current conditions (temperature, humidity, pressure, wind, cloud coverage)
- 7-day daily forecast with temperature, precipitation, and wind
- 48-hour hourly forecast with detailed conditions
- UV index monitoring

**11 AROME Sensors:**
1. **Elevation** - Location altitude in meters
2. **Air Quality** - AQI value (when available)
3. **UV Index** - UV index (0-11)
4. **Sunrise** - Daily sunrise time
5. **Sunset** - Daily sunset time
6. **Cloud Coverage** - Current cloud cover percentage
7. **Humidity** - Current humidity percentage
8. **Wind Speed (Current)** - Current wind speed
9. **Wind Gust (Current)** - Current wind gusts
10. **Wind Speed Today Max** - Maximum wind speed forecast for today
11. **Wind Gust Today Max** - Maximum wind gusts forecast for today

### Phase 2 (Coming Soon) - BRA Avalanche Data

8 additional sensors providing avalanche risk assessment:
- Avalanche risk level (1-5 European scale)
- Risk trend (stable/increasing/decreasing)
- Snowpack quality description
- Recent snowfall measurements
- Altitude risk limits
- Wind transport risk
- Wet snow risk
- Accidental trigger risk

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/atacamalabs/ha-better-mountain-weather`
6. Select category: "Integration"
7. Click "Add"
8. Find "A Better Mountain Weather" in HACS and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/better_mountain_weather` folder
2. Copy it to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

### Prerequisites

You need two API tokens from Météo-France:

1. **AROME API Token**: For weather forecasts
   - Visit: [Météo-France API Portal](https://portail-api.meteofrance.fr/)
   - Create an account and subscribe to the AROME API
   - Copy your API key

2. **BRA API Token**: For avalanche bulletins
   - Visit: [Météo-France API Portal](https://portail-api.meteofrance.fr/)
   - Subscribe to the BRA (Bulletin Risque Avalanche) API
   - Copy your API key

### Setup Steps

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "A Better Mountain Weather"
4. Enter your AROME API token
5. Enter your BRA API token
6. Enter GPS coordinates for your mountain location
   - Example: Chamonix (45.9237, 6.8694)
   - Example: Grenoble (45.1885, 5.7245)
7. The integration will automatically detect the nearest massif for avalanche data

### Finding GPS Coordinates

You can find GPS coordinates for your location using:
- Google Maps (right-click on location → coordinates)
- [OpenStreetMap](https://www.openstreetmap.org/)
- Your smartphone's GPS

## Supported Regions

### French Alps (23 Massifs)
Chablais, Aravis, Mont-Blanc, Bauges, Beaufortain, Haute-Tarentaise, Chartreuse, Belledonne, Maurienne, Vanoise, Haute-Maurienne, Vercors, Oisans, Grandes-Rousses, Thabor, Pelvoux, Queyras, Dévoluy, Champsaur, Embrunais-Parpaillon, Ubaye, Mercantour, Alpes-Azur

### Pyrenees (16 Massifs)
Pays-Basque, Aspe-Ossau, Haute-Bigorre, Aure-Louron, Luchonnais, Couserans, Haute-Ariège, Orlu-St-Barthélémy, Capcir-Puymorens, Cerdagne-Canigou, Andorre, and more

### Corsica (1 Massif)
Corse

## Usage Examples

### Lovelace Card Example

```yaml
type: weather-forecast
entity: weather.better_mountain_weather_chamonix_mont_blanc
forecast_type: daily
```

### Sensor Card Example

```yaml
type: entities
entities:
  - entity: sensor.better_mountain_weather_chamonix_mont_blanc_elevation
  - entity: sensor.better_mountain_weather_chamonix_mont_blanc_uv_index
  - entity: sensor.better_mountain_weather_chamonix_mont_blanc_wind_speed_current
  - entity: sensor.better_mountain_weather_chamonix_mont_blanc_wind_gust_current
```

### Automation Example

```yaml
automation:
  - alias: "Alert on high wind"
    trigger:
      - platform: numeric_state
        entity_id: sensor.better_mountain_weather_chamonix_mont_blanc_wind_gust_today_max
        above: 50
    action:
      - service: notify.mobile_app
        data:
          message: "High wind warning: gusts expected to exceed 50 km/h today!"
```

## Data Sources

- **Weather Forecasts**: Météo-France AROME model (high-resolution forecasts for France)
- **Avalanche Bulletins**: Météo-France BRA (Bulletin Risque Avalanche)

All data is provided by Météo-France, the French national meteorological service.

## Update Frequency

- **AROME Weather Data**: Updated every hour
- **BRA Avalanche Data**: Updated every 6 hours (bulletins published once daily)

## Beta Testing

This integration is currently in beta. We welcome feedback and bug reports!

### Enabling Beta Releases

1. In HACS, go to the integration settings
2. Enable "Show beta versions"
3. You'll receive updates for all beta releases

### Current Version

**v0.1.0b1** - Phase 1: AROME weather integration

### Upcoming Releases

- **v0.2.0b1** - Phase 2: BRA avalanche risk sensors
- **v1.0.0** - Stable release with full feature set

## Troubleshooting

### Integration doesn't appear after installation
- Restart Home Assistant completely (not just reload)
- Check logs for any errors: Settings → System → Logs

### "Invalid API token" error
- Verify your API tokens are correct
- Ensure your API subscription is active on the Météo-France portal
- Check that you haven't exceeded your API quota

### "Cannot connect" error
- Verify your GPS coordinates are correct
- Check your internet connection
- Ensure Météo-France API services are operational

### No data in sensors
- Wait for the first data update (up to 1 hour for AROME)
- Check the coordinator update status in logs
- Verify your location is within supported regions (France)

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/atacamalabs/ha-better-mountain-weather/issues)
- **Discussions**: [GitHub Discussions](https://github.com/atacamalabs/ha-better-mountain-weather/discussions)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Météo-France for providing excellent weather and avalanche data APIs
- [meteofrance-api](https://github.com/hacf-fr/meteofrance-api) library by @hacf-fr
- Home Assistant community for development support

## Disclaimer

This integration provides weather and avalanche information for informational purposes only. Always consult official sources and professional guides before making decisions in mountain environments. The authors are not responsible for any incidents resulting from use of this data.

---

**Made with ❤️ for the mountain community**
