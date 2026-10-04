# Final QA Report

Audit date: 2026-10-04 (America/Halifax)

## Deployment

- Site project: `appgprj_6ac1625f88f481918991355063c83741`
- Production deployment: `appgdep_6ac25ac1f4548191ac77fe350f4fd895`
- Version: 8
- Deployment result: **succeeded**
- Site status: **active**
- Production URL: https://chignecto-resilience-monitor.greysonpmalabanan.chatgpt.site/
- Access at audit time: custom/owner-only. Change sharing before judging if judges must open the URL on their own devices.

## Automated checks passed

- `app-rcm.js` passed Node JavaScript syntax validation.
- All 14 JSON and GeoJSON files in the deployed data directory parsed successfully.
- All eight timeline radar images exist.
- All four event change layers exist.
- The historical flood-context layer exists.
- Dorian GeoJSON: 779 total classified features.
- Fiona GeoJSON: 228 total classified features.
- July 2023 GeoJSON: 222 total classified features.
- Lee GeoJSON: 623 total classified features.
- Local HTTP preview returned status 200 for the home page, four representative scene URLs, event manifests and all four change layers.
- The remote Sites service reconfirmed the production deployment as succeeded with no failure message.

## Visual/browser note

The in-app browser-control runtime could not be attached during this final audit because its trusted Windows Node process exited under the local access-control sandbox. This is an audit-tool limitation, not a reported website error. Route, asset, syntax, JSON and deployment checks all passed, and the production screenshot exists in the Sites service.

## Known limitations to disclose

- The timeline contains snapshots, not continuous coverage.
- Candidate polygons are not confirmed flood extents.
- The July 21, 2023 observation is during event onset, not after the complete rainfall event.
- No terrain, permanent-water, tide, radar-shadow or field-validation mask is applied.
- OpenStreetMap and Leaflet are live external dependencies; an internet connection is needed for the normal basemap and library loading.
- The site is currently owner-only. The owner can present while signed in, but independent judge access requires an explicit sharing change.

## Presenter preflight

1. Sign in and open the production URL.
2. Confirm the basemap appears.
3. Move the timeline through all eight stops.
4. Toggle all three change classes and historical flood reports.
5. Test the radar-opacity slider.
6. Keep this package and the local website snapshot as a backup.
7. Do not claim that orange polygons are verified floods or that the sequence is continuous.
