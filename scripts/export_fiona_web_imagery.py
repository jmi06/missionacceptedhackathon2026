from pathlib import Path
import json

import numpy as np
from PIL import Image
import rasterio
from rasterio.warp import transform_bounds

ROOT = Path(r"C:\Users\Greyson Malabanan\Documents\ChatGPT\Mission Accepted Hackathon")
SOURCE = ROOT / "data" / "processed" / "fiona"
OUTPUT = ROOT / "chignecto-resilience-demo" / "dist" / "data" / "events"


def load(path):
    with rasterio.open(path) as src:
        data = src.read(1).astype(np.float32)
        bounds = transform_bounds(src.crs, "EPSG:4326", *src.bounds, densify_pts=21)
        return data, bounds


def render(data, valid, low, high, output):
    scaled = np.clip(np.nan_to_num((data - low) / (high - low), nan=0.0), 0, 1)
    scaled = np.power(scaled, 0.82)
    gray = (scaled * 235 + 12).astype(np.uint8)
    rgba = np.zeros((*data.shape, 4), dtype=np.uint8)
    rgba[..., 0] = gray
    rgba[..., 1] = gray
    rgba[..., 2] = gray
    rgba[..., 3] = np.where(valid, 235, 0).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(output, optimize=True)


def main():
    before, before_bounds = load(SOURCE / "fiona_before_vh_sigma0_db.tif")
    after, after_bounds = load(SOURCE / "fiona_after_vh_sigma0_db.tif")
    if before.shape != after.shape or any(abs(a - b) > 1e-6 for a, b in zip(before_bounds, after_bounds)):
        raise RuntimeError("Fiona rasters are not on the same aligned grid")

    common = np.isfinite(before) & np.isfinite(after)
    pooled = np.concatenate((before[common], after[common]))
    low, high = np.percentile(pooled, [2, 98]).tolist()

    OUTPUT.mkdir(parents=True, exist_ok=True)
    render(before, common, low, high, OUTPUT / "fiona-before-map.png")
    render(after, common, low, high, OUTPUT / "fiona-after-map.png")

    west, south, east, north = before_bounds
    metadata = {
        "bounds_wgs84": [[south, west], [north, east]],
        "shared_display_stretch_db": [round(low, 4), round(high, 4)],
        "source": "calibrated aligned RCM VH sigma-nought dB rasters",
        "alpha_mask": "common valid observation area on both dates",
        "interpretation": "radar intensity image; not a flood map",
        "images": {
            "before": "data/events/fiona-before-map.png",
            "after": "data/events/fiona-after-map.png"
        }
    }
    (OUTPUT / "fiona-map-imagery.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
