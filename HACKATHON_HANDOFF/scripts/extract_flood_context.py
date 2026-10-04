from __future__ import annotations

import json
from pathlib import Path

import fiona
from rasterio.warp import transform_bounds, transform_geom


PROJECT = Path(r"C:\Users\Greyson Malabanan\Documents\ChatGPT\Mission Accepted Hackathon")
SOURCE = PROJECT / "data" / "reference" / "historical_flood_event_en.gpkg"
OUTPUT = PROJECT / "data" / "processed" / "fiona" / "historical_flood_context.geojson"
LAYER = "historical_flood_location_0"
CONTEXT_BBOX_WGS84 = (-64.45, 45.84, -63.95, 46.06)
MIN_YEAR = 1950


with fiona.open(SOURCE, layer=LAYER) as source:
    source_crs = source.crs_wkt or source.crs
    query_bbox = transform_bounds("EPSG:4326", source_crs, *CONTEXT_BBOX_WGS84, densify_pts=21)
    features = []
    records = []
    seen = set()
    for feature in source.filter(bbox=query_bbox):
        geometry = transform_geom(source_crs, "EPSG:4326", feature["geometry"], precision=6)
        properties = dict(feature["properties"])
        if not properties.get("year") or properties["year"] < MIN_YEAR:
            continue
        identity = (properties.get("event_id"), properties.get("locality"), tuple(geometry.get("coordinates", [])))
        if identity in seen:
            continue
        seen.add(identity)
        features.append({"type": "Feature", "geometry": geometry, "properties": properties})
        records.append({
            "year": properties.get("year"),
            "start_date": properties.get("start_date"),
            "locality": properties.get("locality"),
            "province": properties.get("province_territory"),
            "cause": properties.get("flood_cause"),
            "comment": properties.get("comment"),
            "source": properties.get("source_1_description"),
            "link": properties.get("link_1"),
            "coordinates": geometry.get("coordinates"),
        })

collection = {
    "type": "FeatureCollection",
    "name": "Historical Flood Events context near Chignecto Isthmus",
    "source_file": SOURCE.name,
    "note": f"Event location points from {MIN_YEAR} onward are contextual records, not mapped flood extents.",
    "features": features,
}
OUTPUT.write_text(json.dumps(collection, indent=2, default=str), encoding="utf-8")
year_counts = {}
for record in records:
    year_counts[str(record["year"])] = year_counts.get(str(record["year"]), 0) + 1
print(json.dumps({
    "record_count": len(records),
    "year_counts": year_counts,
    "latest_records": sorted(records, key=lambda item: item["year"] or 0, reverse=True)[:10],
}, indent=2, default=str))
