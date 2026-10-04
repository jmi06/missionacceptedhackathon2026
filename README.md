# Chignecto Resilience Monitor

An interactive hackathon prototype that combines Canadian RADARSAT Constellation Mission imagery, complementary Sentinel-1 observations, Natural Resources Canada historical flood records, and OpenStreetMap context for the Chignecto Isthmus.

## Live demo

https://chignecto-resilience-monitor.greysonpmalabanan.chatgpt.site/

The interface presents eight radar snapshots across four storm periods:

- Hurricane Dorian, 2019
- Hurricane Fiona, 2022
- July 2023 extreme rainfall
- Hurricane Lee, 2023

Orange polygons are candidate areas that became low-return on the second observation. They are **not confirmed flood boundaries**.

## Repository guide

- `HACKATHON_HANDOFF/website/` — deployable static website snapshot
- `scripts/` — RCM, Sentinel-1, and historical-event processing scripts
- `data/processed/` — calibrated rasters, classified change layers, and summaries
- `data/reference/` — NRCan Historical Flood Events reference dataset
- `HACKATHON_HANDOFF/` — presenter guide, complete data/API inventory, QA report, and demonstration backup
- `PROPOSAL.md` — project proposal and evidence framing
- `TIMELINE_METHOD.md` — technical method and measured results
- `WEBSITE_MANUAL.md` — user instructions

## Processing pipeline

```text
satellite metadata
    → radiometric calibration
    → common EPSG:32620 grid at 50 m
    → shared event-pair threshold
    → low-backscatter change classes
    → removal of regions smaller than 1 ha
    → GeoJSON and web imagery
    → Leaflet timeline over OpenStreetMap
```

## Technology

- Python, NumPy, Rasterio, Fiona, and Pillow for geospatial processing
- Leaflet for the interactive browser map
- OpenStreetMap for the basemap
- Static HTML, CSS, JavaScript, GeoJSON, JSON, and PNG assets
- OpenAI Sites for the deployed prototype

GeoPandas and SciPy are not required by the current processing scripts.

## Data policy

The original satellite ZIP archives and extracted raw TIFFs are intentionally excluded because they are too large for GitHub. Exact archive paths, sizes, product IDs, sources, usage decisions, and SHA-256 hashes are documented in `HACKATHON_HANDOFF/DATA_AND_API_INVENTORY.md`.

This prototype is a screening and communication tool. It must not be used by itself for evacuation, engineering, insurance, property valuation, or underwriting decisions.
