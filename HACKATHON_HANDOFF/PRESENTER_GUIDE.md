# Presenter Guide

## One-sentence product goal

The Chignecto Resilience Monitor turns comparable radar observations into an easy timeline that helps communities and future property-risk users see where water-like radar conditions appeared, persisted or disappeared around major storm periods.

## Problem statement

Flood evidence is scattered across satellite archives, historical records and technical formats that most residents, planners and property buyers cannot interpret. Satellite passes are occasional, different acquisitions are not always comparable, and a dark radar pixel is not automatically a flood. The product organizes credible, comparable observations into one transparent visual screening tool.

## What the product solves

- It makes Canadian RCM and European Sentinel-1 radar evidence understandable on a familiar street map.
- It compares matched observations and highlights places that newly became low-return, stayed low-return or stopped being low-return.
- It places four event periods on one timeline: Dorian, Fiona, July 2023 rainfall and Lee.
- It adds official historical flood-report locations as context.
- It preserves limitations so the result is a screening and prioritization tool, not an insurance or engineering conclusion.

## Three-minute presentation flow

### 1. Open with the problem — 20 seconds

Say: “The Chignecto Isthmus is a critical, low-lying transportation corridor, but useful flood evidence lives in separate technical archives. People need a simple way to compare what satellites observed around storm events without pretending the satellites provide continuous coverage.”

### 2. State the goal — 15 seconds

Say: “Our goal is to convert comparable radar snapshots into a single, understandable timeline that shows candidate surface-water change and helps prioritize places for closer investigation.”

### 3. Explain the evidence — 30 seconds

Say: “We use Canadian RADARSAT Constellation Mission imagery for Fiona and the July 2023 rainfall, matched Sentinel-1 imagery for Dorian and Lee, Natural Resources Canada historical flood records, and OpenStreetMap for geographic context.”

Emphasize that radar works through cloud and at night, which is valuable during storms. Also say that radar-dark does not necessarily mean flooded.

### 4. Demonstrate the timeline — 75 seconds

1. Begin at **Dorian before** on August 27, 2019.
2. Move to **Dorian after** on September 8. Point to orange candidates and say that they newly crossed the pair’s calibrated low-return threshold.
3. Advance to **Fiona before and after**. Explain that this is the core Canadian RCM example.
4. Advance to **July 17 and July 21, 2023**. State that July 21 is an onset observation, not the event’s final extent.
5. Advance to **Lee before and after**. Explain that a matched Sentinel-1 pair filled the comparison gap left by incompatible supplied scenes.
6. Lower **Radar visibility** briefly to reveal roads and communities.
7. Toggle **Past flood reports** and click a yellow point to distinguish an official historical report from a satellite-derived candidate.

### 5. Explain the colours — 20 seconds

- Orange: newly low-return on the second date.
- Blue: low-return on both dates, often including permanent water.
- Purple: low-return only on the first date.
- Yellow points: historical flood reports, not flood boundaries.

### 6. Present the value and next step — 20 seconds

Say: “This prototype proves that RCM and Sentinel-1 observations can be standardized into one defensible visual workflow. The next product layer would connect validated hazard indicators to parcels, listings and insurance context, with clear uncertainty rather than a binary safe-or-unsafe label.”

## Likely judge questions

### Is orange confirmed flooding?

No. It is a candidate change based on calibrated radar backscatter. Terrain, permanent-water, tide and field checks are still needed.

### Is this a continuous animation?

No. It is a chronological sequence of eight available satellite observations.

### Why mix RCM and Sentinel-1?

Both are C-band synthetic-aperture radar missions. Each before/after calculation is performed only within a matched sensor pair; the interface unifies the results without treating raw values from different sensors as identical.

### Why is the real-estate feature not the main result?

The defensible hackathon deliverable is the satellite evidence workflow. Real-estate and insurance context is the product extension once hazard layers have stronger validation.

### What is innovative?

The prototype combines Canadian sovereign radar data, complementary open Sentinel-1 observations and official flood history in an accessible, uncertainty-aware time interface.

## Language to use

Use “candidate low-backscatter change,” “screening layer,” “satellite observation,” and “requires validation.”

Avoid “proven flood boundary,” “continuous flood evolution,” “property is safe,” or “insurance-ready score.”
