# Migration Guide: v0.6.0 → v1.0.0

## 🚨 Breaking Changes

Serac v1.0.0 is a **complete rebrand** of "Better Mountain Weather" with significant improvements. **All users must migrate** - there is no automatic upgrade path.

### What Changed

#### 1. Repository Renamed
- **Old**: `https://github.com/atacamalabs/ha-better-mountain-weather`
- **New**: `https://github.com/atacamalabs/ha-serac`
- GitHub automatically redirects old URLs, but you should update HACS

#### 2. Integration Renamed
- **Old name**: "A Better Mountain Weather"
- **New name**: "Serac"
- **Old domain**: `better_mountain_weather`
- **New domain**: `serac`

#### 3. All Entity IDs Changed
The entity naming system has been completely redesigned for clarity:

**Old pattern** (coordinate-based):
```
sensor.location_46_03_6_31_mountain_weather_temperature
sensor.location_46_03_6_31_mountain_weather_1_avalanche_risk_today
weather.location_46_03_6_31_mountain_weather
```

**New pattern** (user-defined prefix):
```
sensor.serac_chamonix_temperature
sensor.serac_chamonix_aravis_avalanche_risk_today
weather.serac_chamonix
```

**Benefits:**
- ✅ Clean, human-readable entity IDs
- ✅ User chooses the prefix during setup
- ✅ Avalanche sensors include massif name for clarity
- ✅ No more ugly coordinate strings in entity IDs

---

## Migration Steps

### ⚠️ Before You Begin

**Important:** Take note of your current settings before removing the old integration:

1. **Document your configuration**:
   - Location name
   - GPS coordinates
   - Selected massifs
   - Any automations using the integration

2. **Export automations/dashboards** (optional but recommended):
   - Go to **Settings** → **Automations & Scenes**
   - Export any automations referencing Better Mountain Weather entities
   - Take screenshots of dashboards

---

### Step 1: Remove Old Integration

1. Go to **Settings** → **Devices & Services**
2. Find **"A Better Mountain Weather"** or **"Better Mountain Weather"**
3. Click the **⋮** (three dots) → **Delete**
4. Confirm deletion

### Step 2: Remove Old HACS Repository

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Find **"A Better Mountain Weather"**
4. Click **⋮** (three dots) → **Remove**
5. Confirm removal

### Step 3: Restart Home Assistant

1. Go to **Settings** → **System**
2. Click **Restart** (top right)
3. Confirm restart
4. Wait for Home Assistant to come back online (~1-2 minutes)

### Step 4: Add New HACS Repository

1. Open **HACS** → **Integrations**
2. Click **⋮** (three dots, top right)
3. Select **Custom repositories**
4. Add:
   - **Repository**: `https://github.com/atacamalabs/ha-serac`
   - **Category**: Integration
5. Click **Add**

### Step 5: Install Serac

1. In HACS, find **Serac** in the list
2. Click on it
3. Click **Download**
4. Wait for download to complete
5. **Restart Home Assistant** again

### Step 6: Configure Serac

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"Serac"**
4. Click on it to start setup

**Configuration wizard:**

1. **Location Step**:
   - Enter your location name (e.g., "Chamonix Mont-Blanc")
   - Enter GPS coordinates (same as before)
   - Click **Submit**

2. **Entity Prefix Step** (NEW!):
   - Choose a short identifier (e.g., "chamonix", "home", "alps")
   - The system suggests one based on your location name
   - This will be used in all entity IDs
   - Click **Submit**

3. **Avalanche Data Step** (optional):
   - Enter your BRA API token (if you had one before)
   - Select your massifs (same ones as before)
   - Or skip this step if you only want weather data
   - Click **Submit**

4. **Done!** Serac is now configured

### Step 7: Update Automations

All automations referencing old entity IDs must be updated.

**Example: Wind Alert Automation**

❌ **Old** (v0.6.0):
```yaml
automation:
  - alias: "High Wind Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.location_46_03_6_31_mountain_weather_wind_gust_max_day0
        above: 60
```

✅ **New** (v1.0.0) - assuming prefix "chamonix":
```yaml
automation:
  - alias: "High Wind Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.serac_chamonix_wind_gust_max_day0
        above: 60
```

**How to update:**
1. Go to **Settings** → **Automations & Scenes**
2. Click on each automation using Better Mountain Weather entities
3. Click **Edit in YAML** (top right ⋮ menu)
4. Find and replace old entity IDs with new ones
5. **Save**

**Quick find-replace pattern:**
- Old: `sensor.location_XX_XX_XX_XX_mountain_weather_`
- New: `sensor.serac_{your_prefix}_`

### Step 8: Update Dashboards

All dashboard cards using old entity IDs must be updated.

**How to find affected cards:**
1. Go to any dashboard
2. Click **Edit Dashboard** (top right)
3. Look for cards showing "Entity not available" or "Unknown"
4. Click **⋮** → **Edit** on each card
5. Update entity IDs to new format
6. **Save**

**Finding new entity IDs:**
1. Go to **Developer Tools** → **States**
2. Filter by `serac`
3. Browse all available entities
4. Copy the new entity IDs you need

---

## Entity ID Mapping Examples

Assuming you chose **prefix "chamonix"** during setup:

### Weather Entity
| Old (v0.6.0) | New (v1.0.0) |
|--------------|--------------|
| `weather.location_46_03_6_31_mountain_weather` | `weather.serac_chamonix` |

### Weather Sensors
| Old (v0.6.0) | New (v1.0.0) |
|--------------|--------------|
| `sensor.location_46_03_6_31_mountain_weather_temperature` | `sensor.serac_chamonix_temperature_current` |
| `sensor.location_46_03_6_31_mountain_weather_humidity` | `sensor.serac_chamonix_humidity` |
| `sensor.location_46_03_6_31_mountain_weather_wind_speed_current` | `sensor.serac_chamonix_wind_speed_current` |
| `sensor.location_46_03_6_31_mountain_weather_wind_gust_max_day0` | `sensor.serac_chamonix_wind_gust_max_day0` |
| `sensor.location_46_03_6_31_mountain_weather_european_aqi` | `sensor.serac_chamonix_european_aqi` |

### Avalanche Sensors (Aravis massif example)
| Old (v0.6.0) | New (v1.0.0) |
|--------------|--------------|
| `sensor.location_46_03_6_31_mountain_weather_2_avalanche_risk_today` | `sensor.serac_chamonix_aravis_avalanche_risk_today` |
| `sensor.location_46_03_6_31_mountain_weather_2_avalanche_risk_tomorrow` | `sensor.serac_chamonix_aravis_avalanche_risk_tomorrow` |
| `sensor.location_46_03_6_31_mountain_weather_2_avalanche_accidental` | `sensor.serac_chamonix_aravis_avalanche_accidental` |

**Note:** The massif ID number (e.g., `_2_`) is replaced with the massif name (e.g., `_aravis_`)

---

## Troubleshooting

### "Serac not found" in HACS

**Solution:**
1. Make sure you added the new repository URL: `https://github.com/atacamalabs/ha-serac`
2. Refresh HACS (click **⋮** → **Reload**)
3. Search again for "Serac"

### Old entities still showing in Developer Tools

**Solution:**
1. Go to **Settings** → **Devices & Services** → **Entities**
2. Filter by `location_` or `better_mountain`
3. Select orphaned entities
4. Click **Remove selected**
5. This cleans up the entity registry

### Automations broken after migration

**Solution:**
- Check automation logs for errors
- Verify entity IDs match your chosen prefix
- Use **Developer Tools** → **States** to find correct entity IDs
- Test automations individually after updating

### Can't remember old massif selections

**Solution:**
- If you're unsure which massifs you had selected, you can:
  1. Check your location on a map
  2. Select nearby massifs from the list
  3. You can always remove and re-add the integration to change massifs

### History data disappeared

**Expected behavior:**
- Because entity IDs changed, historical data under old entity IDs won't automatically transfer
- This is a limitation of the breaking change
- New history will accumulate under the new entity IDs
- Old data is still in the database but not linked to new entities

---

## Benefits of Migrating

Despite the migration effort, v1.0.0 brings significant improvements:

### ✅ Better Entity Naming
- Human-readable entity IDs
- Customizable prefix
- Massif names in avalanche sensor IDs
- Easier to remember and type

### ✅ Cleaner Organization
- Separate devices per massif
- Clear device names with "(Serac)" identifier
- Better integration with Home Assistant's device system

### ✅ Improved Branding
- Professional name ("Serac")
- Better documentation
- Clearer purpose and identity

### ✅ Foundation for Future Features
- Options flow (coming soon - change massifs without reinstalling)
- More massifs support
- Enhanced customization options

---

## Need Help?

If you encounter issues during migration:

- **Check logs**: Settings → System → Logs
- **GitHub Issues**: [github.com/atacamalabs/ha-serac/issues](https://github.com/atacamalabs/ha-serac/issues)
- **GitHub Discussions**: [github.com/atacamalabs/ha-serac/discussions](https://github.com/atacamalabs/ha-serac/discussions)
- **Email**: hi@atacamalabs.com

---

## FAQ

### Q: Can I keep both versions installed during migration?
**A:** No. The domain change means you cannot run both simultaneously. Follow the migration steps in order.

### Q: Will my historical weather data be preserved?
**A:** Historical data under old entity IDs remains in the database but won't be accessible through new entities. This is a limitation of the breaking change.

### Q: Do I need to reinstall if I'm a new user?
**A:** No! This guide is only for users upgrading from v0.6.0. New users can simply install Serac v1.0.0 directly.

### Q: Can I choose the same prefix as my old coordinate-based IDs?
**A:** While technically possible, it's not recommended. Choose a meaningful, short prefix like your location name.

### Q: What if I have multiple locations configured?
**A:** Each location is a separate config entry. You'll need to:
1. Remove all old entries
2. Add Serac multiple times (once per location)
3. Choose a different prefix for each location (e.g., "chamonix", "grenoble")

---

**Thank you for migrating to Serac v1.0.0!** 🏔️

*We apologize for the inconvenience of this breaking change, but we believe the improved user experience is worth it.*
