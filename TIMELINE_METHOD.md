# Unified Storm Timeline — Data Method

## Purpose

This note records how the eight-scene timeline was produced without presenting incompatible observations as equivalent measurements.

## Timeline

| Stop | Period | Date | Sensor | Displayed channel | Use |
|---|---|---:|---|---|---|
| 1 | Dorian before | 2019-08-27 | Sentinel-1B | HV | Comparable Sentinel-1 analysis |
| 2 | Dorian after | 2019-09-08 | Sentinel-1B | HV | Comparable Sentinel-1 analysis |
| 3 | Fiona before | 2022-09-20 | RCM-3 | VH | Comparable RCM analysis |
| 4 | Fiona after | 2022-09-24 | RCM-1 | VH | Comparable RCM analysis |
| 5 | July rainfall before | 2023-07-17 | RCM-3 | VH | Comparable RCM analysis |
| 6 | July rainfall onset | 2023-07-21 | RCM-1 | VH | Comparable RCM analysis |
| 7 | Lee before | 2023-09-05 | Sentinel-1A | HV | Comparable Sentinel-1 analysis |
| 8 | Lee after | 2023-09-17 | Sentinel-1A | HV | Comparable Sentinel-1 analysis |

## Comparable RCM processing

The Fiona and July 2023 pairs are SC50MA GRD, ascending, VV/VH acquisitions. VH digital numbers were calibrated to sigma-nought using each product's supplied sigma LUT:

`sigma0 = (DN² + LUT offset) / LUT gain`

The calibrated power was converted to dB, geolocated from embedded ground-control points, and aligned to the same 50 m EPSG:32620 grid over the Chignecto study area.

Each event pair uses one shared Otsu threshold calculated from the pooled before/second-date VH values. Components smaller than four pixels, or one hectare, are removed.

### Fiona result

- Common valid area: 82,140.75 ha
- Persistent low return: 6,953.75 ha
- Newly low return after Fiona: 412.25 ha
- Low return no longer present: 377.50 ha
- New candidate polygons: 130

### July 2023 result

- Common valid area: 98,070.75 ha
- Persistent low return: 8,348.25 ha
- Newly low return by July 21: 330.25 ha
- Low return no longer present: 146.50 ha
- New candidate polygons: 108
- Shared threshold: −20.6640625 dB

The July 21 acquisition occurred at 21:55 UTC during the onset of the extreme rainfall event. It is not a post-event or final-extent image.

## Comparable Sentinel-1 processing

Replacement Sentinel-1 products were selected from the public AWS Sentinel-1 GRD archive using Element 84 Earth Search metadata. Each event pair uses the same platform, descending relative orbit 69, IW GRDH mode and HH/HV polarization.

HV digital numbers were calibrated using each product's supplied sigma-nought LUT:

`sigma0 = DN² / sigmaNought_LUT²`

The calibrated values were converted to dB and aligned to the same 50 m EPSG:32620 grid used for the RCM outputs. Each pair uses one pooled Otsu threshold and one fixed −30 to −5 dB display stretch. Components smaller than one hectare were removed.

### Dorian Sentinel-1 result

- Common valid area: 73,802.75 ha
- Persistent low return: 5,764.25 ha
- Newly low return after Dorian: 1,445.50 ha
- Low return no longer present: 311.25 ha
- New candidate polygons: 522
- Shared threshold: −18.0859375 dB

### Lee Sentinel-1 result

- Common valid area: 73,697.75 ha
- Persistent low return: 5,609.00 ha
- Newly low return after Lee: 154.25 ha
- Low return no longer present: 1,317.75 ha
- New candidate polygons: 32
- Shared threshold: −17.6953125 dB

## Interpretation rule

The timeline shows the sequence of available snapshots. It does not prove continuous environmental evolution between 2019 and 2023. All four event periods now support calculated candidate-change layers, but none is confirmed flood extent. Low radar return can also represent permanent water, wet smooth ground, roads, tides, agricultural change or radar shadow.
