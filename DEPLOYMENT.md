# Deployment Branch

This branch is ready to deploy as a static website from the repository root.

## Publish directory

Use the repository root: `.`

No build command is required.

## Required entry point

- `index.html`

## Runtime files included

- `app-rcm.js` — active timeline and map application
- `styles.css` — interface styling
- `favicon.svg` — site icon
- `data/events/` — eight radar map images, product metadata, and timeline manifests
- `data/*_low_backscatter_change.geojson` — Dorian, Fiona, July 2023, and Lee candidate-change layers
- `data/historical_flood_context.geojson` — NRCan historical flood-report context

The `data/processed/` and `data/reference/` directories are also retained for reproducibility. The application itself reads the web-ready files directly under `data/`.

## GitHub Pages

In the repository settings:

1. Open **Pages**.
2. Select **Deploy from a branch**.
3. Select `codex/deployment-with-data`.
4. Select the repository root `/`.
5. Save.

## Other static hosts

For Netlify, Cloudflare Pages, or similar static hosting, select this branch, leave the build command empty, and use `.` as the publish directory.

## Data scope

All files required by the live visualization are committed to this branch. Multi-gigabyte source ZIP archives and extracted raw satellite TIFFs are intentionally excluded because browsers do not use them and standard GitHub hosting cannot accept them. Their product IDs, source locations, sizes, and hashes are documented in `HACKATHON_HANDOFF/DATA_AND_API_INVENTORY.md`.
