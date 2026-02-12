# Snow Depth Sensor Research for Serac
**Date**: 2026-02-12
**Version**: Research for v2.0
**Status**: Feasibility Analysis

## Executive Summary

Snow depth sensors would provide valuable information for mountain weather monitoring. This document explores available data sources, API capabilities, technical feasibility, and implementation recommendations.

---

## 🎯 Research Goals

1. Identify available snow depth data sources
2. Assess API compatibility with existing architecture
3. Evaluate data quality and update frequency
4. Determine implementation complexity
5. Recommend approach for v2.0

---

## 📊 Data Source Analysis

### 1. Open-Meteo API (Primary Source)

#### Current Integration
Serac currently uses: `https://api.open-meteo.com/v1/forecast`
- ✅ Already integrated
- ✅ Free for non-commercial use
- ✅ No authentication required
- ✅ Reliable uptime

#### Snow Depth Availability

**Parameter**: `snow_depth`
- **Unit**: Meters
- **Type**: Hourly instant value
- **Description**: "Snow depth on the ground"
- **Access**: `&hourly=snow_depth`

**Related Parameters**:
- `snowfall`: Hourly snowfall amount (cm) - ✅ **Already integrated in Serac**
- `snowfall_sum`: Daily total snowfall (cm) - ✅ **Already integrated in Serac**

**Sources**:
- [Open-Meteo Documentation](https://open-meteo.com/en/docs)
- [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
- [ECMWF API Documentation](https://open-meteo.com/en/docs/ecmwf-api)

#### Model Coverage

**Availability by Model**:
- ✅ **ECMWF**: Snow depth (water equivalent) available
- ❌ **IFS**: Excludes snow depth
- ❌ **IFA Assimilation**: Omits snow depth
- ✅ **General Forecast API**: `snow_depth` parameter supported

**Important Note**:
> "Snowfall amount is not provided by ECMWF directly, instead it is approximated based on total precipitation and temperature."

This suggests snow depth may also be model-derived rather than observation-based.

---

### 2. Météo-France Public APIs

#### AROME/ARPEGE Models (via Open-Meteo)

**Currently Used**: `Météo-France AROME` (1.5km resolution for France)

**Available Parameters**:
- ✅ `snowfall`: Hourly snowfall (cm)
- ✅ `snowfall_sum`: Daily snowfall sum (cm)
- ❌ `snow_depth`: **NOT AVAILABLE**

**Source**: [Météo-France API Documentation](https://open-meteo.com/en/docs/meteofrance-api)

#### Météo-France Direct APIs

**Public Data Portal**: [Données Publiques Météo-France](https://donneespubliques.meteofrance.fr/)

**Mountain Weather Service**: [METEO MONTAGNE](http://meteofrance.com/meteo-montagne)
- Provides snow depth at ski resorts
- Real observation station data
- Manual/semi-automated measurements

**Observation Network**:
- **~276 stations** in French Alps and Pyrenees
- **Coverage**: Uneven distribution, sparse above 2500m
- **Data**: Ground-based observations assimilated into SAFRAN-SURFEX/ISBA-Crocus-MEPRA (S2M) reanalysis
- **Limitation**: Low number of long-term high-elevation sites

**Sources**:
- [France Montagnes Snow Forecast](https://en.france-montagnes.com/live/snow-levels/snow-forecast)
- [Current Snow Conditions](https://www.connexionfrance.com/news/what-snow-conditions-look-like-for-skiers-across-french-alps-and-pyrenees/768153)

#### API Access Status

**Météo-France REST API**:
- Documentation: [meteofrance-api](https://meteofrance-api.readthedocs.io/en/stable/reference.html)
- Provides: Weather forecast, rain forecast, alert bulletins
- Snow Depth: **Not documented in public API**

**Conclusion**: Météo-France observation station snow depth data is **not publicly available via API** for programmatic access.

---

## 🔬 Technical Feasibility

### Implementation Options

#### **Option A: Open-Meteo `snow_depth` Parameter** ⭐ RECOMMENDED

**Approach**: Add `snow_depth` to existing Open-Meteo API calls

**Pros**:
- ✅ Minimal code changes (add parameter to existing API call)
- ✅ No new authentication required
- ✅ Same update interval as existing weather data (1 hour)
- ✅ Consistent with current architecture
- ✅ Free and unlimited
- ✅ Same reliability as current data source

**Cons**:
- ⚠️ Model-derived data (not direct observations)
- ⚠️ Accuracy depends on weather model
- ⚠️ May not reflect local microclimates
- ⚠️ Limited validation against ground truth

**Technical Implementation**:
```python
# In openmeteo_client.py
params = {
    "hourly": "...,snow_depth",  # Add to existing parameters
    "daily": "...,snow_depth_max,snow_depth_mean"  # If available
}

# New sensor in sensor.py
SENSOR_TYPE_SNOW_DEPTH_CURRENT = "snow_depth_current"

SeracSensorDescription(
    key=SENSOR_TYPE_SNOW_DEPTH_CURRENT,
    name="Snow Depth",
    native_unit_of_measurement=UnitOfLength.METERS,
    device_class=SensorDeviceClass.DISTANCE,
    state_class=SensorStateClass.MEASUREMENT,
    icon="mdi:snowflake",
    value_fn=lambda data: data.get("current", {}).get("snow_depth"),
)
```

**Effort**: 🟢 Low (2-4 hours)
- Add parameter to API calls
- Create sensor descriptions
- Add translations
- Test with real data

---

#### **Option B: Météo-France Station Data**

**Approach**: Integrate Météo-France observation station network

**Pros**:
- ✅ Real ground-based observations
- ✅ More accurate for specific locations
- ✅ Validated measurements

**Cons**:
- ❌ No public API available
- ❌ Station coverage is sparse (especially >2500m)
- ❌ Uneven distribution across Alps/Pyrenees
- ❌ Requires scraping or unofficial access
- ❌ Would violate data terms of service
- ❌ Maintenance burden

**Effort**: 🔴 High (20+ hours) + Legal/TOS concerns

**Status**: ❌ **NOT RECOMMENDED** - No official public API

---

#### **Option C: Hybrid Approach**

**Approach**: Use Open-Meteo for general coverage + station data where available

**Pros**:
- ✅ Best of both worlds
- ✅ Fall back to model data when stations unavailable

**Cons**:
- ❌ Complexity in data fusion
- ❌ Still requires station API access (see Option B)
- ❌ Inconsistent data quality across locations

**Effort**: 🟠 Medium-High (10-15 hours)

**Status**: ⚠️ **DEFERRED** - Wait for official Météo-France API

---

## 📈 Data Quality Assessment

### Open-Meteo Snow Depth

**Strengths**:
- Global coverage
- Consistent methodology
- Regular updates (hourly)
- Long forecast horizon (7-16 days)
- Historical data available

**Limitations**:
- Model-derived (not direct measurement)
- Accuracy varies by location and conditions
- May not capture:
  - Avalanche effects
  - Wind redistribution
  - Local microclimates
  - Rapid melt events

**Use Cases**:
- ✅ General snow cover awareness
- ✅ Trend monitoring (accumulation/melt)
- ✅ Forecasting future snow depth
- ✅ Historical comparisons
- ⚠️ Precise measurements for specific spots

**Current Snow Conditions (Feb 2026)**:
Per Météo-France observations:
- Northern Alps: 20-50cm above 1,500m, >1m above 2,000m
- Southern Alps: 10-80cm in high valleys, 150-200cm at 2,500m

This provides baseline for validating model accuracy.

---

## 🎯 Recommendation

### **RECOMMENDED: Option A - Open-Meteo `snow_depth`**

**Rationale**:
1. **Low effort**: Leverages existing API integration
2. **Immediate availability**: No waiting for new data sources
3. **Consistent UX**: Same reliability as other Serac sensors
4. **Good coverage**: Works for all locations, not just French Alps
5. **Future-proof**: Can be enhanced with station data if API becomes available

### Implementation Plan for v2.0

**Phase 1: Basic Integration** (v2.0)
- [ ] Add `snow_depth` parameter to OpenMeteoClient
- [ ] Create current snow depth sensor
- [ ] Add hourly snow depth forecast (6h)
- [ ] Add daily max/mean snow depth (7 days)
- [ ] Add translations (EN, FR, DE, IT, ES)
- [ ] Update documentation

**Phase 2: Enhanced Features** (v2.1+)
- [ ] Snow depth change rate sensor (cm/hour)
- [ ] Snow melt detection (negative change)
- [ ] Automation blueprint: "Snow accumulation alert"
- [ ] Historical snow depth tracking
- [ ] Snow depth statistics (season high/low)

**Phase 3: Station Integration** (v3.0 - if API available)
- [ ] Investigate Météo-France official API for stations
- [ ] Hybrid model: prefer station data, fall back to model
- [ ] Station data quality indicators
- [ ] User preference: model vs station data

---

## 📝 Sensor Specifications

### Proposed Sensors (v2.0)

#### Current Sensors
1. **Snow Depth Current**
   - Entity ID: `sensor.serac_{prefix}_snow_depth`
   - Unit: cm (or m)
   - Update: Hourly
   - Icon: `mdi:snowflake`
   - Device Class: `distance`

#### Forecast Sensors
2. **Snow Depth Max Today**
   - Entity ID: `sensor.serac_{prefix}_snow_depth_max_day0`
   - Unit: cm
   - Forecast: Daily

3. **Snow Depth Change 24h**
   - Entity ID: `sensor.serac_{prefix}_snow_depth_change_24h`
   - Unit: cm
   - Calculation: Current - 24h ago
   - Icon: `mdi:chart-line` or `mdi:trending-up`/`down`

#### Future Sensors (v2.1+)
4. **Snow Accumulation Rate**
   - Entity ID: `sensor.serac_{prefix}_snow_accumulation_rate`
   - Unit: cm/hour
   - Calculation: Running average over 6 hours

5. **Snow Melt Detected**
   - Entity ID: `binary_sensor.serac_{prefix}_snow_melting`
   - Type: Binary sensor
   - Condition: Negative depth change + temp > 0°C

---

## 🧪 Validation Strategy

### Testing Plan

1. **API Validation**
   - Test `snow_depth` parameter with Open-Meteo API
   - Verify data format and units
   - Check update frequency
   - Validate historical data availability

2. **Accuracy Testing**
   - Compare model values vs Météo-France observations
   - Test multiple locations (various elevations)
   - Monitor over winter season
   - Document typical error margins

3. **Edge Cases**
   - Zero snow conditions (summer)
   - Heavy snowfall events
   - Rapid melt scenarios
   - High altitude vs valley differences

---

## 🔄 Migration Path

### From v1.x to v2.0

**Backward Compatibility**:
- ✅ Existing sensors remain unchanged
- ✅ New sensors are additive
- ✅ No breaking changes to entity IDs
- ✅ Opt-in feature (automatic if data available)

**User Communication**:
- Document that snow depth is model-derived
- Set expectations for accuracy
- Provide comparison with local observations
- Offer feedback channel for accuracy reports

---

## 💰 Cost Analysis

### Option A (Recommended)

**Development**: 2-4 hours
**Testing**: 1-2 hours
**Documentation**: 1 hour
**Total**: ~5-7 hours

**Ongoing Costs**:
- $0 (free API)
- No additional infrastructure
- Minimal maintenance

### Option B (Station Data)

**Development**: 20+ hours
**Legal Review**: Unknown
**Ongoing Costs**:
- Potential API fees
- Web scraping infrastructure
- Maintenance burden
- TOS compliance risk

---

## 🔗 References

### Documentation
- [Open-Meteo Main API](https://open-meteo.com/en/docs)
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
- [Open-Meteo ECMWF API](https://open-meteo.com/en/docs/ecmwf-api)
- [Météo-France API via Open-Meteo](https://open-meteo.com/en/docs/meteofrance-api)
- [Météo-France Public Data](https://donneespubliques.meteofrance.fr/)
- [Météo-France API Python Client](https://meteofrance-api.readthedocs.io/en/stable/reference.html)

### Research
- [GitHub: Open-Meteo Issue #272 - Historical snow_depth variable](https://github.com/open-meteo/open-meteo/issues/272)
- [Trends in annual snow melt-out day over French Alps](https://tc.copernicus.org/articles/19/2407/2025/)
- [France Montagnes Snow Forecast](https://en.france-montagnes.com/live/snow-levels/snow-forecast)
- [Current Snow Conditions - French Alps](https://www.connexionfrance.com/news/what-snow-conditions-look-like-for-skiers-across-french-alps-and-pyrenees/768153)
- [J2Ski Snow Forecasts France](https://www.j2ski.com/snow_forecast/France/)

---

## ✅ Next Steps

1. **Immediate**: Test Open-Meteo API with `snow_depth` parameter
2. **Short-term**: Implement basic snow depth sensor (v2.0)
3. **Medium-term**: Add advanced snow sensors and automations (v2.1)
4. **Long-term**: Monitor Météo-France API for station data availability (v3.0)

---

## 📌 Conclusion

**Snow depth sensors are FEASIBLE and RECOMMENDED for Serac v2.0**

Using Open-Meteo's `snow_depth` parameter provides:
- ✅ Quick implementation
- ✅ Reliable data source
- ✅ Good user value
- ✅ Foundation for future enhancements

**Recommendation**: Proceed with Option A for v2.0 release.

---

*Research completed: 2026-02-12*
*Next review: After v2.0 implementation and winter season validation*
