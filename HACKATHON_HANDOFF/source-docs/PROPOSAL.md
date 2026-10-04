# Chignecto Storm Change Monitor

## One-sentence proposal

We use Canadian RCM radar images, supported by Sentinel-1 satellite images and official flood records, to show how water-like areas can change around major storms and help local decision-makers decide where to inspect first.

## The problem

After a major storm, communities need to understand where water may have spread. Satellite data can help, but the files are technical, difficult to compare, and spread across different sources. This makes it hard for planners, emergency teams, infrastructure owners, and eventually property professionals to turn the data into a quick, understandable picture.

## Our solution

The Chignecto Storm Change Monitor turns storm-related satellite files into a simple map.

A user can:

1. Move through one eight-stop timeline from Dorian in 2019 to Fiona in 2022, the July 2023 rainfall interval, and Lee in 2023.
2. Switch between a real image taken before and after each storm.
3. For images that are technically comparable, see areas that changed to look more like water.
4. View official historical flood reports for context.
5. Mark the largest or most important areas for human review.

The product does **not** claim that every highlighted area flooded. It is an evidence-screening tool that helps people decide where to investigate first.

## What is working in the demo

### Hurricane Fiona — main RCM analysis

The Fiona example is the core of the prototype because the two supplied RCM images have matching settings. We calibrated and aligned them, then used one shared, data-driven cutoff to find low-radar-return areas on each date.

Within the selected Chignecto study area, the prototype found:

- 6,953.75 hectares that looked water-like on both dates;
- 412.25 hectares that became water-like after Fiona;
- 377.50 hectares that looked water-like only before Fiona; and
- 130 separate new areas for possible review.

These numbers describe the satellite classification, not confirmed flood damage.

### Hurricane Lee and Hurricane Dorian — complementary Sentinel-1 analysis

The originally supplied Lee and Dorian pairs had incompatible radar settings. They were replaced with public Sentinel-1 acquisitions matched by platform, descending relative orbit 69, IW GRDH mode and HH/HV polarization.

The Dorian interval identified 1,445.50 hectares of newly low return across 522 candidate polygons. The Lee interval identified 154.25 hectares across 32 candidate polygons. These are screening candidates, not confirmed flood areas; tides, wet ground, agriculture and radar shadow can contribute.

### July 2023 extreme rainfall — second RCM analysis

The supplied July 17 and July 21 RCM images use matching SC50MA, ascending, VV/VH settings and support a second candidate-change calculation. The July 21 image was captured during rainfall onset rather than after the complete event. Within the study area, 330.25 hectares newly crossed the shared low-return threshold, producing 108 candidate polygons for review.

## Datasets used

| Dataset | Role in the product | How it is used |
|---|---|---|
| RCM images for Fiona | Main analytical dataset | Measures where low radar return appeared, remained, or disappeared |
| RCM images for July 2023 | Second analytical interval | Measures early-event candidate change between July 17 and July 21 |
| Sentinel-1 images for Lee | Complementary analytical interval | Measures calibrated HV low-return change using a matched orbit-69 pair |
| Sentinel-1 images for Dorian | Complementary analytical interval | Measures calibrated HV low-return change using a matched orbit-69 pair |
| NRCan Historical Flood Events | Context and evidence | Displays past reported flood locations; these points do not represent flood boundaries |
| OpenStreetMap | Basemap | Gives users familiar roads, place names, and geographic context |
| Future property and infrastructure data | Planned extension | Would show which buildings, roads, rail lines, and properties are near reviewed areas |

Radar satellites are useful for this concept because they can collect images day or night and through cloud cover. That matters during storms, when optical imagery may be blocked by clouds.

## Why this is useful

The prototype shortens the path from a technical satellite file to a practical question: **“Where should we look first?”**

Its immediate users could be municipal planners, emergency managers, infrastructure operators, and environmental analysts. A later version could add assessed property values, listings, insurance-related public information, and critical infrastructure exposure. Those additions should come only after the flood-change method is validated.

## How it addresses the hackathon rubric

### Meaningful problem

The product addresses the difficulty of turning large, technical Earth-observation files into timely and understandable information about storm impacts.

### Strong use of Canadian space data

RCM is the main analytical dataset, not a decorative layer. The Fiona and July 2023 results are calculated from calibrated RCM imagery supplied for the project.

### Innovation

The idea combines satellite change screening, historical flood context, and a simple consumer-style map. It makes specialist data easier for non-specialists to explore.

### Feasibility

The current demo displays authentic map-aligned imagery and produces measured candidate-change layers for all four periods: RCM for Fiona and July 2023, and Sentinel-1 for Dorian and Lee.

### Impact and scalability

The same workflow can be repeated for other storms when suitable image pairs are available. Future versions could add infrastructure and property exposure without changing the core satellite-processing method.

### Clear communication and responsible use

The interface uses plain language and clearly separates measured results from context-only images. It also states that satellite candidates are not confirmed floods.

## Deliverable for tonight

The minimum credible deliverable is:

- a working web map with one chronological Dorian–Fiona–July rainfall–Lee timeline;
- eight real, map-aligned radar observations;
- measured RCM change candidates for Fiona and July 2023;
- measured Sentinel-1 change candidates for Lee and Dorian;
- official historical flood-location context;
- a short method and limitations statement;
- this proposal and a concise pitch.

## Next steps, in order

1. **Test the demo.** Check that all three storms load, the timeline changes the correct date, and the mobile layout remains usable.
2. **Review the biggest Fiona candidates.** Inspect the five largest areas against the radar previews, basemap, permanent water, and local geography.
3. **Add one validation layer.** If time permits, add a permanent-water layer or official flood-extent product. This will help separate rivers and lakes from possible new flooding.
4. **Add important assets.** Use credible public data for roads, rail, dikes, communities, or critical infrastructure. Avoid invented properties or values.
5. **Prepare the pitch.** Lead with the problem, show the Fiona RCM result, then show how matched Sentinel-1 pairs extend the same screening concept to Dorian and Lee.
6. **Package the evidence.** Keep the source ZIP names, product IDs, analysis settings, results, and links together so judges can verify the work.
7. **Validate the Sentinel candidates.** Add permanent-water, terrain, tide and local evidence before presenting any candidate as likely flooding.

## Suggested 45-second pitch

“Storm satellite data can show where water may have spread, but the files are too technical for most local decision-makers to use quickly. Our Chignecto Storm Change Monitor turns matched before-and-after radar images into a simple map. Canadian RCM imagery provides our core Fiona and July analyses, while comparable Sentinel-1 pairs extend the timeline to Dorian and Lee. Orange areas became more water-like in radar observations and are ranked for review alongside official Canadian flood records. The result is not a flood declaration—it is a transparent screening tool that helps communities decide where to inspect first.”

## Credible sources

- Canadian Space Agency, [Access to RCM data](https://www.asc-csa.gc.ca/eng/satellites/radarsat/access-to-data/)
- Canadian Space Agency, [RCM Image Product Format Definition](https://download-telecharger.services.geo.ca/pub/csa_asc/Space-technology_Technologie-spatiale/radarsat_constellation_mission_plan/RCM-SP-53-0419_Image_Product_Format_Definition_2-8_Public.pdf)
- European Space Agency, [Introducing the Sentinel-1 mission](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-1/Introducing_the_Sentinel-1_mission)
- AWS Registry of Open Data, [Sentinel-1 GRD archive](https://registry.opendata.aws/sentinel-1/)
- Element 84, [Earth Search STAC catalogue](https://element84.com/earth-search)
- Natural Resources Canada, [Historical Flood Events dataset](https://open.canada.ca/data/en/dataset/fe83a604-aa5a-4e46-903c-685f8b0cc33c)
- OpenStreetMap, [Copyright and licence](https://www.openstreetmap.org/copyright)

## Important limitations

Radar-dark areas are not automatically floodwater. Calm water often appears dark, but wet smooth ground, roads, radar shadow, tides, vegetation, and different viewing conditions can also change the signal. Historical flood points show reported locations, not the full area that flooded. The prototype should support inspection and discussion, not replace field verification, engineering analysis, insurance decisions, or a formal flood-risk assessment.
