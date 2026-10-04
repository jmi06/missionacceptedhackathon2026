# Hurricane Fiona RCM change analysis

## Status

This analysis identifies **low-backscatter change candidates** in two RCM scenes. It is not a validated flood extent, flood forecast, engineering assessment, or property-risk score.

## Source imagery

| Role | RCM product | Acquisition (UTC) | Satellite | Mode | Product | Polarization used |
|---|---|---:|---|---|---|---|
| Before | `RCM3_OK2000431_PK2265822_1_SC50MA_20220920_215531_VV_VH_GRD` | 2022-09-20 21:55:31 | RCM-3 | SC50MA | GRD | VH |
| After | `RCM1_OK2000496_PK2271094_2_SC50MA_20220924_215505_VV_VH_GRD` | 2022-09-24 21:55:05 | RCM-1 | SC50MA | GRD | VH |

Both products were supplied by the project team as complete EODMS downloads. Their embedded metadata reports ascending acquisitions, 20 m pixel sampling, the same SC50MA mode, GRD processing, and VV/VH polarization availability.

Environment and Climate Change Canada reports that Fiona made landfall in eastern Nova Scotia during the early morning of September 24, 2022. Therefore, the second RCM acquisition occurred later that day. It is a post-landfall observation, but it does not represent peak conditions throughout the storm.

## Processing method

1. Extracted the VH raster, `product.xml`, the sigma-nought LUT, incidence-angle metadata, footprint, and preview from each RCM archive.
2. Read the ground-control points embedded in each TIFF.
3. Limited processing to an analyst-defined Chignecto study extent: `[-64.45, 45.84, -63.95, 46.06]` in longitude/latitude.
4. Applied the product-specific sigma-nought LUT using the RCM GRD calibration relationship:

   `sigma0 = (DN² + B) / A`

   Here, `DN` is the stored image value, `B` is the LUT offset, and `A` is the range-dependent gain. Both products contain an offset of zero. The linear sigma-nought power was converted to decibels with `10 log10(sigma0)`.
5. Reprojected both calibrated scenes to the same EPSG:32620 grid at 50 m spacing. Average resampling was applied to linear power before conversion to decibels.
6. Calculated one shared Otsu threshold from the pooled before-and-after VH backscatter distribution between -40 and 0 dB. The resulting threshold was **-20.2734375 dB**.
7. Classified pixels at or below the threshold as low-backscatter candidates.
8. Removed connected regions smaller than four 50 m pixels, equivalent to 1 hectare.
9. Classified the common valid footprint into persistent, newly observed, and no-longer-observed low-backscatter areas.
10. Exported calibrated GeoTIFFs, a classified GeoTIFF, GeoJSON polygons, a preview image, and a machine-readable summary.

## Current results

| Result | Area |
|---|---:|
| Common valid observation area | 82,140.75 ha |
| Persistent low-backscatter | 6,953.75 ha |
| New low-backscatter after Fiona | 412.25 ha |
| Low-backscatter no longer observed | 377.50 ha |

These areas describe the classification output. They must not be reported as confirmed flooded area.

## Reference flood information

The Natural Resources Canada Historical Flood Events GeoPackage was filtered to the study area and records from 1950 onward. It contains 76 location records within the selected extent. These records are points representing places associated with reported historical events. They are contextual evidence and do not provide mapped flood boundaries.

The dataset includes a September 24, 2022 Fiona record at Pointe-du-Chêne, but that point is north of this analysis extent. Therefore, it cannot validate the Chignecto classifications.

## Limitations

- Low SAR backscatter is not unique to open water. Smooth wet surfaces, roads, radar shadow, and other low-return targets may be included.
- A single before-and-after pair cannot establish long-term climate evolution.
- Coastal differences may reflect tide, wind roughness, storm surge, or acquisition geometry.
- The after scene only partially covers the southern edge of the study area. All reported areas use the common valid footprint.
- No digital elevation model, permanent-water mask, field observations, or independent flood-extent polygons have been applied.
- Otsu thresholding is reproducible and data-driven, but its result remains a classification hypothesis that requires validation.

## Authoritative sources

- Canadian Space Agency, *RCM Image Product Format Definition*, Issue 2/8/P, June 4, 2021: https://download-telecharger.services.geo.ca/pub/csa_asc/Space-technology_Technologie-spatiale/radarsat_constellation_mission_plan/RCM-SP-53-0419_Image_Product_Format_Definition_2-8_Public.pdf
- Canadian Space Agency, RCM technical characteristics and product documentation: https://www.asc-csa.gc.ca/eng/satellites/radarsat/technical-features/characteristics.asp
- Natural Resources Canada, radar calibration background: https://natural-resources.canada.ca/maps-tools-publications/satellite-elevation-air-photos/radar-image-properties
- Environment and Climate Change Canada, *Canada's Top 10 Weather Stories of 2022*: https://www.canada.ca/en/environment-climate-change/services/top-ten-weather-stories/2022.html
- Natural Resources Canada, Historical Flood Events dataset: https://open.canada.ca/data/en/dataset/fe83a604-aa5a-4e46-903c-685f8b0cc33c

## Reproduction

The workflow is implemented in:

- `scripts/inspect_rcm.py`
- `scripts/process_fiona_rcm.py`
- `scripts/extract_flood_context.py`

Run the processing script with the project-local Python environment:

```powershell
.\.venv\Scripts\python.exe .\scripts\process_fiona_rcm.py
```
