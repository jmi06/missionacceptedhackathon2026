# How the Prototype Was Developed

This is the build process explained from a presenter’s point of view.

## 1. Define the decision problem

We started with a practical question: how can a non-specialist see where storm-related water conditions may have changed around the Chignecto Isthmus? We deliberately framed the output as a screening tool because a two-date radar comparison cannot prove flood depth, cause or property-level loss.

## 2. Choose the study area

We used one common Chignecto map window, approximately 45.84–46.06° N and 64.45–63.95° W. A common area makes the events easier to compare visually.

## 3. Audit every satellite scene

We read each product’s metadata before processing it: acquisition time, satellite, imaging mode, orbit direction, polarization and product type. This revealed that some supplied Dorian and Lee scenes were not technically comparable as pairs.

## 4. Keep the valid RCM comparisons

The Hurricane Fiona and July 2023 pairs use matching RCM SC50MA GRD, ascending, VV/VH acquisition settings. We analyzed the VH channel because cross-polarized radar is useful for distinguishing surface conditions in this landscape.

## 5. Replace incompatible comparisons with matched Sentinel-1 observations

For Dorian and Lee, we searched public Sentinel-1 metadata and chose pairs with the same platform, descending relative orbit 69, IW GRDH mode and HH/HV polarization. This kept the comparison scientifically more defensible than subtracting mismatched scenes.

## 6. Calibrate the radar measurements

Raw radar pixel values are instrument measurements, not map-ready water values. The scripts use each product’s calibration lookup table to convert digital numbers to sigma-nought backscatter and then to decibels.

## 7. Put every observation on a common grid

Each calibrated image was reprojected to EPSG:32620 at 50-metre resolution over the study area. Within each event, the before and second-date image occupy exactly the same pixels.

## 8. Calculate candidate change

For each event pair, one Otsu threshold was calculated from the pooled valid before and second-date values. Pixels were classified as:

- persistent low return;
- newly low return on the second date; or
- low return present only on the first date.

Connected regions smaller than one hectare were removed to reduce isolated radar speckle.

## 9. Convert the result into web layers

The classification rasters were converted to GeoJSON polygons for interactive display. Fixed-stretch grayscale radar images were exported as georeferenced overlays. Analysis summaries preserve thresholds, dates, product IDs, area totals and limitations.

## 10. Add official context

Natural Resources Canada Historical Flood Events points were clipped to the surrounding region and displayed as yellow reference markers. These are observations at locations, not historical flood polygons.

## 11. Build the interface

The website uses Leaflet, OpenStreetMap tiles and static local data files. A single eight-stop timeline moves through Dorian, Fiona, July 2023 and Lee. Layer switches, opacity, search, candidate lists and explanatory text help users interpret the evidence.

## 12. Validate and publish

We checked JavaScript syntax, parsed every JSON/GeoJSON file, verified all eight timeline images and four change layers, and served every major route locally. The exact packaged site was then published through OpenAI Sites.

## Processing flow

`product metadata → calibration → common 50 m grid → shared threshold → change classes → remove <1 ha regions → GeoJSON and image overlays → Leaflet timeline`

## What a production version still needs

1. Terrain and radar-shadow masking.
2. Permanent-water and tidal-state controls.
3. Independent validation using field reports or authoritative flood extents.
4. More acquisitions per event to reduce dependence on two snapshots.
5. Parcel/licensed listing data and an uncertainty-aware exposure summary.
6. User testing with emergency managers, planners, insurers and home buyers.
