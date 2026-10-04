# Chignecto Storm Change Monitor — User Manual

Website: https://chignecto-resilience-monitor.greysonpmalabanan.chatgpt.site/

## What the website actually shows

The site is a timeline of eight radar snapshots, not a continuous video:

1. August 27, 2019 — before Hurricane Dorian
2. September 8, 2019 — after Hurricane Dorian
3. September 20, 2022 — before Hurricane Fiona
4. September 24, 2022 — after Hurricane Fiona
5. July 17, 2023 — before the July extreme-rainfall event
6. July 21, 2023 — during the onset of the July rainfall
7. September 5, 2023 — before Hurricane Lee
8. September 17, 2023 — after Hurricane Lee

The site contains four measured radar intervals:

- **RCM:** Fiona and July 2023 use matching RCM settings.
- **Sentinel-1:** Dorian and Lee use replacement pairs matched by platform, orbit, mode and polarization.

## Quick start

1. Open the website.
2. Move the bottom slider or press **Play**.
3. Watch the black-and-white radar image change at each date.
4. Read the badge: it states the event, date, sensor, and whether the stop is measured or context only.
5. Stop at any event to inspect coloured change candidates.
6. Adjust **Radar visibility** to reveal the street map underneath.

## Understanding the radar image

- Bright, textured areas return more radar energy and may include buildings, vegetation, or rough ground.
- Dark, smooth areas return less radar energy and may include open water.
- Transparent areas were outside the satellite pass.
- Dark does not automatically mean flooded.

The two images within each event interval use a shared display stretch. The coloured polygons are calculated from calibrated radar values, not from display brightness.

## Understanding the colours

At all four event periods:

- **Orange:** newly crossed the water-like low-return threshold on the second date.
- **Blue:** water-like on both dates; often permanent water.
- **Purple:** water-like only on the first date.
- **Yellow dots:** official historical flood-report locations, not flood boundaries.

For July 2023, orange means newly low-return by the July 21 observation. That image was captured during rainfall onset, not after the full event, so it is an early-event screening result.

## Controls

- **Timeline slider:** choose one of the eight dates.
- **Play:** restart at Dorian and advance through all dates.
- **Actual radar image:** show or hide the current satellite image.
- **Radar visibility:** control image transparency.
- **Change switches:** control persistent, newly appearing and disappearing low-return candidates.
- **Past flood reports:** available throughout the timeline.
- **Largest areas to check:** shows the five largest new candidates for the active measured interval.
- **Search:** find a candidate ID or historical flood record.
- **How to use:** opens the guide; mobile users can select **Open the quick guide**.

## Suggested demonstration

1. Begin at Dorian and compare the matched Sentinel-1 observations.
2. Play through Fiona and explain that it uses Canadian RCM imagery.
3. Continue to July 17 and July 21; note that July 21 was during event onset.
4. Continue to Lee and compare its matched Sentinel-1 pair.
5. Select an orange candidate and explain that it still requires validation.
6. Finish with the product value: one timeline combining RCM and Sentinel-1 evidence.

## Important limitations

- Eight snapshots do not constitute continuous satellite coverage.
- The events occurred in different seasons and weather conditions.
- Dorian and Lee now use matched Sentinel-1 settings, but they are still two-date snapshots rather than continuous observations.
- The July 21 image was acquired during event onset, before the full July 21–22 rainfall concluded.
- The selected Chignecto study area was not the main Halifax-area impact centre.
- Radar-dark areas may also be roads, wet smooth ground, tides, or radar shadow.
- No terrain, permanent-water, or field-validation mask has been applied.
- The tool must not be used alone for insurance, evacuation, property valuation, or engineering decisions.

## Troubleshooting

- **Blank basemap:** check the internet connection.
- **Hidden radar:** turn on **Actual radar image** and increase visibility.
- **Partial coverage:** transparent areas were outside that satellite pass.
- **No orange layer:** confirm that **Appeared after** is enabled and that the current event files loaded successfully.
- **Closed left panel:** select the menu button near the upper-left.
