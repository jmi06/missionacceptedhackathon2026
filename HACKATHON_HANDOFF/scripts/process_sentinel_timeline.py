from pathlib import Path
import json
import math
import zipfile

import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject

ROOT = Path(r"C:\Users\Greyson Malabanan\Documents\ChatGPT\Mission Accepted Hackathon")
DOWNLOADS = Path(r"C:\Users\Greyson Malabanan\Downloads")
OUTPUT = ROOT / "chignecto-resilience-demo" / "dist" / "data" / "events"

# One fixed regional grid keeps every Sentinel-1 scene spatially aligned on the map.
WEST, SOUTH, EAST, NORTH = -67.4, 44.3, -60.4, 47.9
PIXEL_DEGREES = 0.003
WIDTH = math.ceil((EAST - WEST) / PIXEL_DEGREES)
HEIGHT = math.ceil((NORTH - SOUTH) / PIXEL_DEGREES)
TRANSFORM = from_origin(WEST, NORTH, PIXEL_DEGREES, PIXEL_DEGREES)

SCENES = [
    {"id": "dorian-before", "zip": "before 3.zip", "pol": "vh", "date": "2019-09-05", "sensor": "Sentinel-1A"},
    {"id": "dorian-after", "zip": "shortlyafter 3.zip", "pol": "hv", "date": "2019-09-08", "sensor": "Sentinel-1B"},
    {"id": "lee-before", "zip": "before 2.zip", "pol": "vh", "date": "2023-09-13", "sensor": "Sentinel-1A"},
    {"id": "lee-after", "zip": "shortlyafter 2.zip", "pol": "hv", "date": "2023-09-17", "sensor": "Sentinel-1A"},
]


def measurement_name(zip_path: Path, polarization: str) -> str:
    with zipfile.ZipFile(zip_path) as archive:
        matches = [
            name for name in archive.namelist()
            if "/measurement/" in name
            and f"-{polarization}-" in name.lower()
            and name.lower().endswith(".tiff")
        ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {polarization.upper()} measurement in {zip_path.name}, found {len(matches)}")
    return matches[0]


def render_scene(scene: dict) -> dict:
    zip_path = DOWNLOADS / scene["zip"]
    inner = measurement_name(zip_path, scene["pol"])
    vsi_path = "/vsizip/" + zip_path.as_posix() + "/" + inner
    destination = np.zeros((HEIGHT, WIDTH), dtype=np.float32)

    with rasterio.open(vsi_path) as source:
        gcps, gcp_crs = source.gcps
        if not gcps or str(gcp_crs) != "EPSG:4326":
            raise RuntimeError(f"Missing EPSG:4326 geolocation points in {scene['zip']}")
        reproject(
            source=rasterio.band(source, 1),
            destination=destination,
            gcps=gcps,
            src_crs=gcp_crs,
            src_nodata=0,
            dst_transform=TRANSFORM,
            dst_crs="EPSG:4326",
            dst_nodata=0,
            resampling=Resampling.average,
            num_threads=2,
            warp_mem_limit=256,
        )

    valid = destination > 0
    if not np.any(valid):
        raise RuntimeError(f"No valid pixels produced for {scene['id']}")

    amplitude_db = np.zeros_like(destination)
    amplitude_db[valid] = 20.0 * np.log10(destination[valid])
    low, high = np.percentile(amplitude_db[valid], [2, 98]).tolist()
    scaled = np.clip((amplitude_db - low) / (high - low), 0, 1)
    scaled = np.power(scaled, 0.85)
    gray = (scaled * 235 + 12).astype(np.uint8)

    rgba = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
    rgba[..., :3] = gray[..., None]
    rgba[..., 3] = np.where(valid, 232, 0).astype(np.uint8)
    output_name = f"{scene['id']}-map.png"
    Image.fromarray(rgba, "RGBA").save(OUTPUT / output_name, optimize=True)

    return {
        **scene,
        "image": f"data/events/{output_name}",
        "bounds_wgs84": [[SOUTH, WEST], [NORTH, EAST]],
        "display_stretch_amplitude_db": [round(low, 4), round(high, 4)],
        "valid_output_pixels": int(valid.sum()),
        "output_dimensions": [WIDTH, HEIGHT],
        "processing": "Raw Sentinel-1 cross-polarized amplitude geolocated from embedded GCPs, averaged to a common regional grid, converted to amplitude dB, and contrast-stretched per scene.",
        "interpretation": "Map-aligned visual context only; brightness and water change are not comparable between the before and after scenes.",
    }


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results = []
    for scene in SCENES:
        print(f"Processing {scene['id']} from {scene['zip']}...")
        results.append(render_scene(scene))
    manifest = {
        "name": "Map-aligned Sentinel-1 storm context",
        "grid": {
            "crs": "EPSG:4326",
            "bounds_wgs84": [[SOUTH, WEST], [NORTH, EAST]],
            "pixel_degrees": PIXEL_DEGREES,
            "dimensions": [WIDTH, HEIGHT],
        },
        "comparison_warning": "Each scene is contrast-stretched independently. Lee and Dorian before/after scenes use different polarizations and viewing directions, so brightness differences must not be interpreted as measured flood change.",
        "scenes": results,
    }
    (OUTPUT / "sentinel-map-imagery.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
