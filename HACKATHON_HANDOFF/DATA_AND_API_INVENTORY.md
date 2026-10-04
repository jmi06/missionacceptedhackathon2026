# Data and API Inventory

## Final datasets used in the displayed analysis

| Event/context | Data source | Dates used | Final role |
|---|---|---|---|
| Hurricane Dorian | Sentinel-1B GRD, public AWS archive | 2019-08-27 and 2019-09-08 | Matched before/after low-backscatter analysis |
| Hurricane Fiona | RADARSAT Constellation Mission GRD supplied by the team | 2022-09-20 and 2022-09-24 | Matched before/after low-backscatter analysis |
| July 2023 rainfall | RADARSAT Constellation Mission GRD supplied by the team | 2023-07-17 and 2023-07-21 | Matched before/onset low-backscatter analysis |
| Hurricane Lee | Sentinel-1A GRD, public AWS archive | 2023-09-05 and 2023-09-17 | Matched before/after low-backscatter analysis |
| Historical context | Natural Resources Canada Historical Flood Events | Dataset snapshot supplied by the team | Reference points near the study area |
| Basemap | OpenStreetMap standard tiles | Live | Roads, towns and geographic context |

## Exact Sentinel-1 products

### Dorian

- Before: `S1B_IW_GRDH_1SDH_20190827T103043_20190827T103108_017770_021711_9481`
- After: `S1B_IW_GRDH_1SDH_20190908T103043_20190908T103108_017945_021C7C_59C6`
- Settings: Sentinel-1B, descending relative orbit 69, IW GRDH, HH/HV; HV analyzed.

### Lee

- Before: `S1A_IW_GRDH_1SDH_20230905T103148_20230905T103213_050191_060A83_BD1E`
- After: `S1A_IW_GRDH_1SDH_20230917T103149_20230917T103214_050366_06106F_D660`
- Settings: Sentinel-1A, descending relative orbit 69, IW GRDH, HH/HV; HV analyzed.

The exact public measurement and calibration URLs are retained in `data/web/events/dorian-sentinel1-analysis.json` and `data/web/events/lee-sentinel1-analysis.json`.

## Exact RCM products

### Fiona

- Before: `RCM3_OK2000431_PK2265822_1_SC50MA_20220920_215531_VV_VH_GRD`
- After: `RCM1_OK2000496_PK2271094_2_SC50MA_20220924_215505_VV_VH_GRD`

### July 2023 rainfall

See `data/processed/july2023/july2023_analysis_summary.json` for the product metadata extracted from `before 4.zip` and `shortlyafter 4.zip`.

## Supplied raw archives

The raw archives remain in `C:\Users\Greyson Malabanan\Downloads`. They are not copied into this handoff because they total roughly 12.5 GB. Hashes allow anyone to confirm that an archive has not changed.

| Archive | Size (bytes) | SHA-256 | Final use |
|---|---:|---|---|
| `before 1.zip` | 1,383,007,246 | `DE31209475EA63C27DA1EF5185CA490694556B02E4FFFE20A762692A1CBA7BD1` | Used: Fiona before RCM |
| `shortlyafter 1.zip` | 1,381,911,193 | `D95C77AF89B4ED293C1F6C3203D956066EFA0718E55C709056383A9B905C3478` | Used: Fiona after RCM |
| `before 2.zip` | 1,736,000,515 | `33FD33930219B844800FFBBCD5E5A9329DEA51168988EE887B9ED64B3127FCC6` | Supplied Lee scene; not used in final paired calculation because acquisition settings did not match |
| `shortlyafter 2.zip` | 1,702,065,373 | `5B6E7ABEB79CB26B6F21945DE5CF86598241528514A3CF5510A70A02C410EDEF` | Supplied Lee reference; final analysis streamed a matched public Sentinel-1 pair |
| `before 3.zip` | 1,734,042,797 | `948575481A3603C8CB5E07CE03C10AD6264646BA11F4A5FDE7A2E546D962F7EB` | Supplied Dorian scene; not used in final paired calculation because acquisition settings did not match |
| `shortlyafter 3.zip` | 1,701,711,050 | `778A188A9F9C4DD0FE46CB09CD271A304B68E710864410C867DD04F89A59983C` | Supplied Dorian reference; final analysis streamed a matched public Sentinel-1 pair |
| `before 4.zip` | 1,395,993,457 | `AD7F5670B4E421BA8A9A68EE3DA3FEBE6868BD2DEA6022D9F24F2AA9A2CC2E95` | Used: July 2023 before RCM |
| `shortlyafter 4.zip` | 1,383,144,993 | `D02494E68D5AA7DD16AE0723289206C7DE3C4A7BAEACA7D657EE8C73A1DC75C5` | Used: July 2023 onset RCM |
| `historical_flood_event_en.gpkg.zip` | 1,998,787 | `1C8D4A630DCE461F105FC68D15D1AEBF1B69BB9F672D1F7470C98E0A243399AC` | Used: official historical flood context |

## APIs and online services

No API keys, passwords or tokens are stored in this package.

| Service | Endpoint/source | How it was used |
|---|---|---|
| Element 84 Earth Search STAC | `https://earth-search.aws.element84.com/v1` | Search and inspect public Sentinel-1 scene metadata |
| AWS Sentinel-1 GRD archive | `https://sentinel-s1-l1c.s3.eu-central-1.amazonaws.com/` | Stream Sentinel-1 measurement TIFFs and calibration XML |
| Copernicus Data Space Browser | `https://browser.dataspace.copernicus.eu/` | Visual discovery and cross-checking of Copernicus observations |
| OpenStreetMap tiles | `https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png` | Live street-map basemap in Leaflet |
| Leaflet 1.9.4 | `https://unpkg.com/leaflet@1.9.4/` | Browser mapping library loaded by the static site |
| NRCan Open Government dataset | `https://open.canada.ca/data/en/dataset/fe83a604-aa5a-4e46-903c-685f8b0cc33c` | Official historical flood-event locations |
| Canadian Space Agency RCM documentation | `https://www.asc-csa.gc.ca/eng/satellites/radarsat/access-to-data/` | Product-access and interpretation documentation |

## Included reproducibility files

- `scripts/process_fiona_rcm.py` — Fiona RCM calibration and classification.
- `scripts/process_july2023_rcm.py` — July 2023 RCM calibration and classification.
- `scripts/process_sentinel1_matched.py` — matched Dorian and Lee Sentinel-1 processing.
- `scripts/extract_flood_context.py` — historical-event extraction.
- `scripts/inspect_flood_reference.py` and `scripts/inspect_rcm.py` — metadata inspection.
- `data/processed/` — all final calculated outputs.
- `data/web/` — web manifests, imagery and interactive layers.

## Data that is illustrative or not yet present

The prototype does not currently contain licensed property listings, parcel assessments, insurance premiums or claim records. Those remain a proposed complementary feature. Do not present the interface as making a property valuation or underwriting decision.
