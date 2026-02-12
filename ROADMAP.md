# Serac Development Roadmap - Post v1.1.0

## Context

Serac v1.1.0 has been successfully released with:
- Complete rebrand from "Better Mountain Weather" to "Serac"
- Smart entity naming with user-defined prefixes
- All 35 French massifs supported (Alps, Pyrenees, Corsica)
- 3-step config flow (location → prefix → massifs)
- Comprehensive documentation and migration guide

The user has asked for a development plan covering what should be built next and how to approach implementation.

**Current Limitation**: Users cannot change their massif selection or BRA token without completely removing and re-adding the integration. This is the biggest pain point preventing iteration and experimentation.

---

## Development Priorities

### Priority 1: Options Flow ⚙️ (HIGHEST VALUE)

**Why This Matters:**
- **Biggest user pain point**: Users must reinstall to change massifs or add/remove BRA token
- **Enables experimentation**: Users can try different massif combinations without losing their setup
- **Professional UX**: Matches standard Home Assistant integration patterns
- **No breaking changes**: Can be added as enhancement to existing installs

**User Value**: ⭐⭐⭐⭐⭐ (Critical improvement)
**Effort**: 🔨🔨🔨 (2-3 hours)
**Dependencies**: None (can start immediately)

#### What Needs to Be Done

1. **Add OptionsFlowHandler class** to config_flow.py
2. **Implement massif modification** - Allow users to select/deselect massifs
3. **Implement BRA token update** - Allow adding/removing/changing BRA token
4. **Handle coordinator lifecycle** - Create new BRA coordinators, remove old ones
5. **Update platforms** - Reload sensor platform to reflect changes

#### Implementation Approach

**File: `custom_components/serac/config_flow.py`**

Add OptionsFlowHandler class:
```python
@staticmethod
@callback
def async_get_options_flow(config_entry):
    """Get the options flow for this handler."""
    return SeracOptionsFlow(config_entry)

class SeracOptionsFlow(config_entries.OptionsFlow):
    """Handle Serac options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Update config entry with new massifs/token
            new_data = {**self.config_entry.data}
            new_data[CONF_MASSIF_IDS] = user_input.get(CONF_MASSIF_IDS, [])

            # Update BRA token if provided, or remove if empty
            if user_input.get(CONF_BRA_TOKEN):
                new_data[CONF_BRA_TOKEN] = user_input[CONF_BRA_TOKEN]
            elif CONF_BRA_TOKEN in new_data and not user_input.get(CONF_BRA_TOKEN):
                # User cleared token, remove it
                new_data.pop(CONF_BRA_TOKEN, None)

            # Update config entry
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )

            # Reload the integration to apply changes
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)

            return self.async_create_entry(title="", data={})

        # Get current values
        current_massifs = self.config_entry.data.get(CONF_MASSIF_IDS, [])
        current_token = self.config_entry.data.get(CONF_BRA_TOKEN, "")

        # Create massif options
        massif_options = {str(num_id): name for num_id, (name, _) in MASSIF_IDS.items()}

        data_schema = vol.Schema({
            vol.Optional(
                CONF_BRA_TOKEN,
                description="Météo-France BRA API token",
                default=current_token
            ): str,
            vol.Optional(
                CONF_MASSIF_IDS,
                description="Select massifs for avalanche bulletins",
                default=current_massifs
            ): cv.multi_select(massif_options),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            description_placeholders={
                "info": "Change your massif selection or BRA token. The integration will reload automatically."
            },
        )
```

**File: `custom_components/serac/__init__.py`**

The existing `async_reload_entry` function will handle the reload:
```python
async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
```

This already exists and will:
1. Unload all platforms (weather, sensors)
2. Remove coordinators from hass.data
3. Re-run setup with new config data
4. Create new BRA coordinators for selected massifs
5. Set up platforms with new sensors

**No entity ID changes** - Weather entities keep same entity_id (based on prefix), avalanche sensors are added/removed based on massif selection.

#### Testing Plan

1. **Install fresh Serac instance** with 2 massifs (e.g., Aravis, Mont-Blanc)
2. **Verify entities created** - Check Developer Tools → States for avalanche sensors
3. **Open Options** - Settings → Devices & Services → Serac → Configure
4. **Add a massif** (e.g., add Chablais)
5. **Verify new sensors appear** - Check for `sensor.serac_{prefix}_chablais_avalanche_risk_today`
6. **Remove a massif** (e.g., remove Mont-Blanc)
7. **Verify sensors removed** - Check Mont-Blanc sensors are gone
8. **Change BRA token** - Update to different token
9. **Verify reload** - Check logs for successful reload
10. **Remove BRA token entirely** - Clear token field
11. **Verify all avalanche sensors removed** - Only weather sensors remain

#### Strings to Add

**File: `custom_components/serac/strings.json`**
```json
{
  "options": {
    "step": {
      "init": {
        "title": "Serac Configuration",
        "description": "Change your massif selection or BRA API token. The integration will reload automatically.",
        "data": {
          "bra_token": "Météo-France BRA API Token",
          "massif_ids": "Massifs for Avalanche Bulletins"
        }
      }
    }
  }
}
```

#### Estimated Effort
- Implementation: 1.5 hours
- Testing: 1 hour
- **Total: 2-3 hours**

---

### Priority 2: Logo & Branding 🎨 (QUICK WIN)

**Why This Matters:**
- **Visual identity**: Makes Serac recognizable in HACS and Devices & Services
- **Professional appearance**: Shows polish and care
- **Branding consistency**: Reinforces "Serac" name with ice/mountain imagery
- **Quick impact**: Minimal code, maximum visual improvement

**User Value**: ⭐⭐⭐ (Nice improvement)
**Effort**: 🔨 (1-2 hours, mostly design)
**Dependencies**: Need logo design/sourcing

#### What Needs to Be Done

1. **Design or source logo** - Mountain/serac/ice themed, 256×256px PNG
2. **Add icon.png** to integration folder
3. **Update manifest.json** (if HA version supports it)
4. **Add logo to README.md** header
5. **Update HACS repository metadata**

#### Implementation Approach

**Logo Requirements:**
- **Format**: PNG with transparency
- **Size**: 256×256 pixels (Home Assistant standard)
- **Theme**: Mountain/ice/serac formation
- **Colors**: Blue/white palette (ice/snow/sky)
- **Style**: Clean, modern, recognizable at small sizes

**Logo Options:**
1. **Commission designer** - Fiverr, Upwork (~$20-50, 1-3 days)
2. **Use AI generation** - DALL-E, Midjourney (immediate, free/cheap)
3. **Find royalty-free** - Noun Project, Flaticon (immediate, free/attribution)

**Files to Create/Modify:**

1. **`custom_components/serac/icon.png`** - Add 256×256 logo
2. **`custom_components/serac/manifest.json`** - No changes needed (icon.png auto-detected)
3. **`README.md`** - Add logo to header:
   ```markdown
   <p align="center">
     <img src="https://raw.githubusercontent.com/atacamalabs/ha-serac/main/custom_components/serac/icon.png" width="200" alt="Serac Logo">
   </p>

   # Serac 🏔️
   ```

4. **`hacs.json`** - Verify logo shows in HACS (auto-detected from icon.png)

#### Testing Plan

1. Add icon.png to `custom_components/serac/`
2. Restart Home Assistant
3. Navigate to **Settings → Devices & Services**
4. Verify Serac shows custom icon (not generic puzzle piece)
5. Check HACS → Integrations → Serac for logo display
6. View README on GitHub to verify logo appears

#### Estimated Effort
- Logo design/sourcing: Variable (30 min - 3 days)
- Implementation: 15 minutes
- Testing: 15 minutes
- **Total: 1-2 hours** (assuming logo is ready)

---

### Priority 3: Enhanced Documentation 📚 (USER EXPERIENCE)

**Why This Matters:**
- **Reduces support burden**: Clear docs = fewer issues opened
- **Improves onboarding**: New users can self-serve
- **Builds trust**: Professional documentation signals quality
- **SEO benefits**: Better discoverability via searches

**User Value**: ⭐⭐⭐⭐ (Significant improvement)
**Effort**: 🔨🔨🔨 (3-4 hours)
**Dependencies**: Need screenshots from live HA instance

#### What Needs to Be Done

1. **Add screenshots** to README
   - Config flow steps (3 screenshots)
   - Weather card example
   - Sensor cards (weather + avalanche)
   - Devices & Services page showing Serac
2. **Create FAQ section** in README
3. **Expand troubleshooting guide** with common issues
4. **Add French translation** (translations/fr.json)
5. **Create CONTRIBUTING.md** for developers

#### Implementation Approach

**Screenshots to Capture:**

1. **Config Step 1** - Location input (shows coordinates, location name)
2. **Config Step 2** - Entity prefix selection (shows suggestion, validation)
3. **Config Step 3** - Massif selection (shows multi-select with all 35 massifs)
4. **Weather Card** - Lovelace weather-forecast card showing Serac data
5. **Sensor Card** - Entity list showing temperature, wind, AQI sensors
6. **Avalanche Card** - Entity list showing avalanche risk sensors for a massif
7. **Devices Page** - Settings → Devices & Services showing Serac integration

**Store screenshots in:** `docs/screenshots/` folder, reference in README

**FAQ Section (Add to README.md):**
```markdown
## Frequently Asked Questions

### Can I change my massif selection after setup?
Yes! Go to Settings → Devices & Services → Serac → Configure to add/remove massifs without reinstalling.

### Why aren't avalanche sensors appearing?
1. Verify you entered a valid BRA API token
2. Check you selected at least one massif
3. Avalanche bulletins are seasonal (~December-May) - check logs for "out of season" messages
4. Verify the BRA API is accessible from your network

### How do I get multiple locations?
Add the Serac integration multiple times with different coordinates. Use unique entity prefixes (e.g., "chamonix", "zermatt") to keep sensors organized.

### Can I use this outside France?
Weather data works worldwide (Open-Meteo). Avalanche bulletins only work for French massifs (Météo-France BRA API limitation).

### What's the difference between risk_today and risk_high_altitude?
- **risk_today/tomorrow**: Overall risk level (1-5 scale)
- **risk_high_altitude/low_altitude**: Risk at different elevation zones (text descriptions)
```

**Troubleshooting Expansion:**
```markdown
### Common Issues

#### "Cannot connect" error during setup
- **Cause**: Invalid coordinates format or network issue
- **Solution**:
  - Use decimal format (e.g., 45.9237, not 45° 55' 25")
  - Verify internet connection
  - Try known coordinates (Chamonix: 45.9237, 6.8694)

#### Weather data stops updating
- **Cause**: Open-Meteo API outage or rate limiting
- **Solution**:
  - Check Home Assistant logs: `tail -f /config/home-assistant.log | grep serac`
  - Wait 1 hour for next update attempt
  - Reload integration: Settings → Devices & Services → Serac → ⋮ → Reload

#### Avalanche sensors showing "Unknown"
- **Cause**: Out of season (May-November), invalid token, or massif with no bulletin
- **Solution**:
  - Check logs for "out of season" or API error messages
  - Verify BRA token is valid at https://portail-api.meteofrance.fr/
  - Try different massif (some publish earlier/later in season)
```

**French Translation (translations/fr.json):**
```json
{
  "config": {
    "step": {
      "user": {
        "title": "Localisation",
        "description": "Entrez le nom de votre emplacement et ses coordonnées GPS",
        "data": {
          "location_name": "Nom de l'emplacement",
          "latitude": "Latitude",
          "longitude": "Longitude"
        }
      },
      "prefix": {
        "title": "Préfixe des entités",
        "description": "Choisissez un identifiant court pour vos entités. Suggestion : {suggested_prefix}\n\nExemple : {example_entity}",
        "data": {
          "entity_prefix": "Préfixe des entités"
        }
      },
      "massifs": {
        "title": "Bulletins d'avalanche",
        "description": "Optionnel : Ajoutez votre clé API BRA Météo-France et sélectionnez les massifs. Laissez vide pour utiliser uniquement la météo.",
        "data": {
          "bra_token": "Clé API Météo-France BRA",
          "massif_ids": "Massifs pour bulletins d'avalanche"
        }
      }
    },
    "error": {
      "cannot_connect": "Échec de connexion : vérifiez vos coordonnées",
      "invalid_prefix": "Préfixe invalide. Doit commencer par une lettre et contenir uniquement des lettres minuscules, chiffres et underscores (1-20 caractères)."
    }
  }
}
```

#### Testing Plan

1. Take screenshots on test HA instance
2. Add screenshots to `docs/screenshots/` folder
3. Update README with image links
4. Add FAQ and troubleshooting sections
5. Create translations/fr.json
6. View README on GitHub to verify formatting
7. Test a real user scenario: new user follows docs from scratch

#### Estimated Effort
- Screenshots: 30 minutes
- FAQ writing: 1 hour
- Troubleshooting expansion: 1 hour
- French translation: 30 minutes
- CONTRIBUTING.md: 30 minutes
- **Total: 3-4 hours**

---

### Priority 4: Code Quality & Diagnostics 🔧 (MAINTAINABILITY)

**Why This Matters:**
- **Easier debugging**: Users can share diagnostic data with issues
- **Better error messages**: Clearer guidance when things go wrong
- **Improved reliability**: Retry logic prevents transient failures
- **Developer confidence**: Tests catch regressions

**User Value**: ⭐⭐⭐ (Behind-the-scenes improvement)
**Effort**: 🔨🔨🔨🔨 (4-6 hours)
**Dependencies**: None

#### What Needs to Be Done

1. **Add diagnostics.py** - Export config and coordinator status
2. **Improve error handling** - Retry logic, rate limit detection
3. **Add unit tests** - Test coordinator, sensor, config flow
4. **Add integration tests** - Test full setup flow
5. **Improve logging** - More context in error messages

#### Implementation Approach

**File: `custom_components/serac/diagnostics.py`** (NEW)
```python
"""Diagnostics support for Serac."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_BRA_TOKEN

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]

    # Redact sensitive data
    config_data = {**entry.data}
    if CONF_BRA_TOKEN in config_data:
        config_data[CONF_BRA_TOKEN] = "***REDACTED***"

    diagnostics_data = {
        "config_entry": config_data,
        "coordinators": {
            "arome": {
                "last_update_success": data["arome_coordinator"].last_update_success,
                "last_update": data["arome_coordinator"].last_update_success_time,
                "update_interval": str(data["arome_coordinator"].update_interval),
            }
        },
    }

    # Add BRA coordinator status
    if "bra_coordinators" in data:
        diagnostics_data["coordinators"]["bra"] = {}
        for massif_id, coordinator in data["bra_coordinators"].items():
            diagnostics_data["coordinators"]["bra"][str(massif_id)] = {
                "massif_name": coordinator.massif_name,
                "last_update_success": coordinator.last_update_success,
                "last_update": coordinator.last_update_success_time,
                "has_data": coordinator.data.get("has_data", False) if coordinator.data else False,
            }

    return diagnostics_data
```

**Enhanced Error Handling (coordinator.py):**
```python
# Add retry logic with exponential backoff
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import asyncio

async def _async_update_data_with_retry(self) -> dict[str, Any]:
    """Fetch data with retry logic."""
    max_retries = 3
    retry_delay = 1  # seconds

    for attempt in range(max_retries):
        try:
            return await self._async_update_data()
        except UpdateFailed as err:
            if attempt < max_retries - 1:
                _LOGGER.warning(
                    "Update failed (attempt %d/%d), retrying in %ds: %s",
                    attempt + 1,
                    max_retries,
                    retry_delay,
                    err,
                )
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise
```

**Unit Tests (tests/test_coordinator.py):** (NEW)
```python
"""Test Serac coordinators."""
import pytest
from unittest.mock import AsyncMock, patch

from custom_components.serac.coordinator import AromeCoordinator, BraCoordinator

async def test_arome_coordinator_success(hass):
    """Test AromeCoordinator successful update."""
    mock_client = AsyncMock()
    mock_client.async_get_current_weather.return_value = {"temperature": 20}
    mock_client.async_get_daily_forecast.return_value = [{"date": "2026-02-11"}]

    coordinator = AromeCoordinator(hass, mock_client, "Test Location")
    await coordinator.async_refresh()

    assert coordinator.data["current"]["temperature"] == 20
    assert len(coordinator.data["daily_forecast"]) == 1
```

#### Testing Plan

1. **Add diagnostics.py** and verify in Settings → Devices → Serac → Download Diagnostics
2. **Add retry logic** and test with simulated API failures
3. **Write unit tests** for coordinators, sensors, config flow
4. **Run tests** with `pytest tests/`
5. **Add GitHub Actions workflow** to run tests on PR

#### Estimated Effort
- Diagnostics: 1 hour
- Error handling improvements: 2 hours
- Unit tests: 2-3 hours
- Integration tests: 1 hour
- **Total: 4-6 hours**

---

## Implementation Order Recommendation

### Phase 1 (Immediate - Week 1)
1. **Options Flow** (2-3 hours) - Highest user value, unblocks iteration
2. **Logo & Branding** (1-2 hours) - Quick win, improves visibility

**Expected outcome**: Users can modify configuration, Serac has visual identity

### Phase 2 (Short-term - Week 2-3)
3. **Enhanced Documentation** (3-4 hours) - Reduces support burden
4. **Diagnostics** (1 hour) - Easier issue debugging

**Expected outcome**: Better onboarding, easier troubleshooting

### Phase 3 (Medium-term - Month 1-2)
5. **Code Quality** (3-5 hours) - Tests, error handling, logging
6. **Advanced Features** (variable) - Based on user feedback

**Expected outcome**: More robust, maintainable codebase

---

## Nice-to-Have Features (Future Backlog)

### Advanced Data Features
- **Hourly avalanche risk evolution** - Show risk changes throughout the day
- **Snow depth sensors** - If API data becomes available
- **Weather alerts/warnings** - Météo-France vigilance data
- **Historical data tracking** - Track conditions over time

### UX Enhancements
- **Custom update intervals** - Let users choose refresh rate
- **Location suggestions** - Auto-suggest based on nearby massifs
- **Dashboard card** - Custom Lovelace card for avalanche risk

### Multi-language Support
- **German UI** - For Swiss/Austrian Alps users
- **Italian UI** - For Italian Alps users
- **Spanish UI** - For Pyrenees users

---

## Success Metrics

### v1.2.0 Goals (Options Flow + Logo)
- [ ] Users can change massifs without reinstalling
- [ ] BRA token can be added/removed via UI
- [ ] Serac has custom logo in HA and HACS
- [ ] No breaking changes
- [ ] Zero GitHub issues about "can't change massifs"

### v1.3.0 Goals (Documentation + Diagnostics)
- [ ] README has screenshots for all config steps
- [ ] FAQ section answers top 5 user questions
- [ ] French translation available
- [ ] Diagnostics data includes coordinator status
- [ ] Average issue resolution time < 24 hours

### v2.0.0 Goals (Code Quality + Advanced Features)
- [ ] Unit test coverage > 70%
- [ ] Integration tests for all platforms
- [ ] Error retry logic in place
- [ ] Enhanced logging for debugging
- [ ] At least 2 advanced features shipped

---

## Critical Files Reference

### For Options Flow
- `custom_components/serac/config_flow.py` - Add OptionsFlowHandler
- `custom_components/serac/__init__.py` - Reload logic (already exists)
- `custom_components/serac/strings.json` - Add options strings

### For Logo & Branding
- `custom_components/serac/icon.png` - New 256×256 logo
- `README.md` - Add logo to header
- `hacs.json` - Verify metadata

### For Documentation
- `README.md` - Add screenshots, FAQ, troubleshooting
- `docs/screenshots/` - New folder for images
- `custom_components/serac/translations/fr.json` - New French translation
- `CONTRIBUTING.md` - New developer guide

### For Diagnostics & Quality
- `custom_components/serac/diagnostics.py` - New diagnostics support
- `custom_components/serac/coordinator.py` - Enhanced error handling
- `tests/test_coordinator.py` - New unit tests
- `tests/test_config_flow.py` - New config flow tests
- `.github/workflows/test.yml` - New CI workflow

---

## Risk Assessment

### Low Risk
- ✅ Options Flow - Uses existing reload pattern, no entity ID changes
- ✅ Logo - Static asset, no code impact
- ✅ Documentation - External to code

### Medium Risk
- ⚠️ Diagnostics - New file, must redact sensitive data
- ⚠️ Error handling - Could mask real issues if not careful

### High Risk
- ❌ Breaking entity ID changes - AVOID (unless v2.0.0 major release)
- ❌ Domain changes - AVOID (just did this in v1.0.0)

---

## Next Actions

1. **Approve this roadmap** - Review and confirm priorities
2. **Start with Options Flow** - Implement OptionsFlowHandler
3. **Commission/source logo** - Find designer or AI-generate
4. **Take screenshots** - Set up test instance for documentation
5. **Create GitHub milestones** - Track progress for v1.2.0, v1.3.0

---

**Recommended First Task**: Implement Options Flow (Priority 1)
**Estimated Time to v1.2.0 Release**: 1-2 weeks (Options Flow + Logo + Testing)
