from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import zipfile


PROJECT = Path(r"C:\Users\Greyson Malabanan\Documents\ChatGPT\Mission Accepted Hackathon")
DOWNLOADS = Path(r"C:\Users\Greyson Malabanan\Downloads")
OUTPUT = PROJECT / "chignecto-resilience-demo" / "dist" / "data" / "events"
OUTPUT.mkdir(parents=True, exist_ok=True)

EVENTS = [
    {
        "id": "fiona",
        "name": "Hurricane Fiona",
        "analysis_status": "RCM change analysis",
        "plain_summary": "The two RCM images are technically comparable, so the map can calculate low-radar-return changes between them.",
        "comparison_note": "Same RCM mode, product type, pass direction and VV/VH polarization.",
        "scenes": [
            {
                "role": "before", "zip": DOWNLOADS / "before 1.zip", "date": "2022-09-20", "time_utc": "21:55:31",
                "sensor": "RCM-3", "polarization": "VV/VH", "mode": "SC50MA GRD",
                "product_id": "RCM3_OK2000431_PK2265822_1_SC50MA_20220920_215531_VV_VH_GRD",
            },
            {
                "role": "after", "zip": DOWNLOADS / "shortlyafter 1.zip", "date": "2022-09-24", "time_utc": "21:55:05",
                "sensor": "RCM-1", "polarization": "VV/VH", "mode": "SC50MA GRD",
                "product_id": "RCM1_OK2000496_PK2271094_2_SC50MA_20220924_215505_VV_VH_GRD",
            },
        ],
    },
    {
        "id": "lee",
        "name": "Hurricane Lee",
        "analysis_status": "Sentinel-1 context",
        "plain_summary": "These scenes show the area around Lee, but they cannot support the same numeric change calculation because the radar settings differ.",
        "comparison_note": "Before is VV/VH and after is HH/HV; acquisition direction also differs. Displayed as context only.",
        "scenes": [
            {
                "role": "before", "zip": DOWNLOADS / "before 2.zip", "date": "2023-09-13", "time_utc": "22:11:46",
                "sensor": "Sentinel-1A", "polarization": "VV/VH", "mode": "IW GRDH",
                "product_id": "S1A_IW_GRDH_1SDV_20230913T221146_20230913T221211_050315_060EC9_C8FA",
            },
            {
                "role": "after", "zip": DOWNLOADS / "shortlyafter 2.zip", "date": "2023-09-17", "time_utc": "10:31:49",
                "sensor": "Sentinel-1A", "polarization": "HH/HV", "mode": "IW GRDH",
                "product_id": "S1A_IW_GRDH_1SDH_20230917T103149_20230917T103214_050366_06106F_D660",
            },
        ],
    },
    {
        "id": "dorian",
        "name": "Hurricane Dorian",
        "analysis_status": "Sentinel-1 context",
        "plain_summary": "These scenes show the area around Dorian, but their radar settings differ, so they are not treated as a measured flood-change layer.",
        "comparison_note": "Before is Sentinel-1A VV/VH and after is Sentinel-1B HH/HV. Displayed as context only.",
        "scenes": [
            {
                "role": "before", "zip": DOWNLOADS / "before 3.zip", "date": "2019-09-05", "time_utc": "22:02:59",
                "sensor": "Sentinel-1A", "polarization": "VV/VH", "mode": "IW GRDH",
                "product_id": "S1A_IW_GRDH_1SDV_20190905T220259_20190905T220324_028892_034669_C3D0",
            },
            {
                "role": "after", "zip": DOWNLOADS / "shortlyafter 3.zip", "date": "2019-09-08", "time_utc": "10:30:43",
                "sensor": "Sentinel-1B", "polarization": "HH/HV", "mode": "IW GRDH",
                "product_id": "S1B_IW_GRDH_1SDH_20190908T103043_20190908T103108_017945_021C7C_59C6",
            },
        ],
    },
]


def read_text(archive: zipfile.ZipFile, entry_name: str) -> str:
    return archive.read(entry_name).decode("utf-8", errors="replace")


def find_entry(archive: zipfile.ZipFile, patterns: list[str]) -> str:
    names = archive.namelist()
    for pattern in patterns:
        regex = re.compile(pattern, re.IGNORECASE)
        for name in names:
            if regex.search(name):
                return name
    raise FileNotFoundError(f"No ZIP entry matched: {patterns}")


def kml_polygon(kml: str) -> list[list[float]]:
    blocks = re.findall(r"<coordinates>(.*?)</coordinates>", kml, flags=re.IGNORECASE | re.DOTALL)
    candidates = []
    for block in blocks:
        coords = []
        for item in block.replace("\n", " ").split():
            parts = item.split(",")
            if len(parts) >= 2:
                try:
                    coords.append([float(parts[0]), float(parts[1])])
                except ValueError:
                    pass
        if len(coords) >= 4:
            candidates.append(coords)
    if not candidates:
        raise ValueError("No polygon coordinate block found in KML")
    coords = max(candidates, key=len)
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords


footprints = []
for event in EVENTS:
    for scene in event["scenes"]:
        with zipfile.ZipFile(scene["zip"]) as archive:
            preview_entry = find_entry(archive, [r"/preview/quick-look\.png$", r"/preview/productOverview\.png$"])
            kml_entry = find_entry(archive, [r"/preview/map-overlay\.kml$", r"/preview/mapOverlay\.kml$"])
            image_name = f"{event['id']}-{scene['role']}.png"
            (OUTPUT / image_name).write_bytes(archive.read(preview_entry))
            scene["preview"] = f"data/events/{image_name}"
            coordinates = kml_polygon(read_text(archive, kml_entry))
            scene["footprint_id"] = f"{event['id']}-{scene['role']}"
            footprints.append({
                "type": "Feature",
                "id": scene["footprint_id"],
                "geometry": {"type": "Polygon", "coordinates": [coordinates]},
                "properties": {
                    "event_id": event["id"],
                    "event_name": event["name"],
                    "role": scene["role"],
                    "date": scene["date"],
                    "sensor": scene["sensor"],
                    "polarization": scene["polarization"],
                    "product_id": scene["product_id"],
                },
            })
        scene["zip"] = scene["zip"].name

(OUTPUT / "events.json").write_text(json.dumps({"events": EVENTS}, indent=2), encoding="utf-8")
(OUTPUT / "event_footprints.geojson").write_text(json.dumps({
    "type": "FeatureCollection",
    "name": "User-provided RCM and Sentinel-1 scene footprints",
    "features": footprints,
}, separators=(",", ":")), encoding="utf-8")

print(json.dumps({
    "events": len(EVENTS),
    "scenes": len(footprints),
    "output": str(OUTPUT),
    "files": sorted(path.name for path in OUTPUT.iterdir()),
}, indent=2))
