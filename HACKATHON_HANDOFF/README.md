# Chignecto Resilience Monitor — Hackathon Handoff

This folder is the presenter and evidence package for the deployed prototype:

https://chignecto-resilience-monitor.greysonpmalabanan.chatgpt.site/

## Start here

1. Read `PRESENTER_GUIDE.md` for the live-demo sequence and speaking notes.
2. Read `DEVELOPMENT_STEPS.md` for the plain-language build story.
3. Read `DATA_AND_API_INVENTORY.md` for every data source, product ID, API, local archive and usage decision.
4. Read `QA_REPORT.md` for the final validation results and known limitations.
5. Open `website/index.html` through a local web server if an offline demonstration is needed.

## Folder contents

- `data/processed/` — calibrated rasters, classified change rasters, GeoJSON layers and analysis summaries used by the product.
- `data/reference/` — the Natural Resources Canada historical flood-events GeoPackage.
- `data/web/` — the exact web-ready imagery, manifests and layers used by the deployed interface.
- `scripts/` — the processing and extraction code used to create the evidence layers.
- `website/` — a snapshot of the deployable static website.
- `source-docs/` — proposal, method notes and end-user manual.

## Important interpretation

The map shows eight satellite snapshots grouped into four before/second-date comparisons. It does **not** show uninterrupted flood movement. Orange, blue and purple shapes are radar low-backscatter change candidates, not verified flood boundaries. Property or insurance decisions require terrain, permanent-water, tide and field validation that are outside this prototype.

## Raw archive policy

The supplied ZIP archives total roughly 12.5 GB, so they are not duplicated here. Their exact paths, byte sizes and SHA-256 hashes are recorded in `DATA_AND_API_INVENTORY.md`. The complete processed evidence needed to inspect the prototype is included in this folder.
