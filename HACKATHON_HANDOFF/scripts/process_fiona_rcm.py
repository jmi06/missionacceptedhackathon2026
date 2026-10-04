from __future__ import annotations

import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
import rasterio
from rasterio.control import GroundControlPoint
from rasterio.features import shapes, sieve
from rasterio.transform import GCPTransformer, from_origin
from rasterio.warp import Resampling, reproject, transform_bounds, transform_geom
from rasterio.windows import Window


PROJECT = Path(r"C:\Users\Greyson Malabanan\Documents\ChatGPT\Mission Accepted Hackathon")
RAW = PROJECT / "data" / "rcm-fiona"
OUTPUT = PROJECT / "data" / "processed" / "fiona"

# Analyst-defined study extent covering the Sackville-Amherst/Tantramar portion
# of the Chignecto Isthmus. It is clipped again by valid overlap in both scenes.
AOI_WGS84 = (-64.45, 45.84, -63.95, 46.06)
TARGET_CRS = "EPSG:32620"
TARGET_RESOLUTION_M = 50.0
MIN_COMPONENT_PIXELS = 4  # 1 hectare at 50 m output resolution

SCENES = {
    "before": {
        "folder": RAW / "before",
        "acquisition_utc": "2022-09-20T21:55:31Z",
        "product_id": "RCM3_OK2000431_PK2265822_1_SC50MA_20220920_215531_VV_VH_GRD",
    },
    "after": {
        "folder": RAW / "after",
        "acquisition_utc": "2022-09-24T21:55:05Z",
        "product_id": "RCM1_OK2000496_PK2271094_2_SC50MA_20220924_215505_VV_VH_GRD",
    },
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def read_sigma_lut(path: Path) -> tuple[np.ndarray, np.ndarray, float]:
    root = ET.parse(path).getroot()
    values = {local_name(el.tag): (el.text or "").strip() for el in root.iter()}
    first = int(values["pixelFirstLutValue"])
    step = int(values["stepSize"])
    count = int(values["numberOfValues"])
    offset = float(values["offset"])
    gains = np.asarray([float(value) for value in values["gains"].split()], dtype=np.float64)
    if len(gains) != count:
        raise ValueError(f"LUT declared {count} gains but contains {len(gains)}")
    positions = first + np.arange(count, dtype=np.float64) * step
    return positions, gains, offset


def adjusted_gcps(gcps: list[GroundControlPoint], row_offset: int, col_offset: int) -> list[GroundControlPoint]:
    return [
        GroundControlPoint(
            row=gcp.row - row_offset,
            col=gcp.col - col_offset,
            x=gcp.x,
            y=gcp.y,
            z=gcp.z,
            id=gcp.id,
            info=gcp.info,
        )
        for gcp in gcps
    ]


def source_window_for_aoi(gcps: list[GroundControlPoint], width: int, height: int) -> Window:
    west, south, east, north = AOI_WGS84
    xs = [west, east, east, west, (west + east) / 2]
    ys = [south, south, north, north, (south + north) / 2]
    with GCPTransformer(gcps) as transformer:
        rows, cols = transformer.rowcol(xs, ys)
    margin = 250
    row_start = max(0, min(rows) - margin)
    row_stop = min(height, max(rows) + margin)
    col_start = max(0, min(cols) - margin)
    col_stop = min(width, max(cols) + margin)
    if row_stop <= row_start or col_stop <= col_start:
        raise RuntimeError("AOI does not overlap the source scene")
    return Window(col_start, row_start, col_stop - col_start, row_stop - row_start)


def target_grid() -> tuple[rasterio.Affine, int, int, tuple[float, float, float, float]]:
    left, bottom, right, top = transform_bounds("EPSG:4326", TARGET_CRS, *AOI_WGS84, densify_pts=21)
    width = math.ceil((right - left) / TARGET_RESOLUTION_M)
    height = math.ceil((top - bottom) / TARGET_RESOLUTION_M)
    transform = from_origin(left, top, TARGET_RESOLUTION_M, TARGET_RESOLUTION_M)
    return transform, width, height, (left, bottom, right, top)


def calibrate_and_warp(scene: dict, dst_transform: rasterio.Affine, dst_width: int, dst_height: int) -> tuple[np.ndarray, dict]:
    folder = scene["folder"]
    tif_path = next(folder.glob("*_VH.tif"))
    positions, gains, offset = read_sigma_lut(folder / "lutSigma_VH.xml")

    with rasterio.open(tif_path) as source:
        gcps, gcp_crs = source.gcps
        if not gcps or str(gcp_crs) != "EPSG:4326":
            raise RuntimeError(f"Expected EPSG:4326 GCP geolocation in {tif_path.name}")
        window = source_window_for_aoi(gcps, source.width, source.height)
        row_offset = int(window.row_off)
        col_offset = int(window.col_off)
        dn = source.read(1, window=window).astype(np.float64)

        source_columns = np.arange(col_offset, col_offset + dn.shape[1], dtype=np.float64)
        column_gains = np.interp(source_columns, positions, gains)

        # RCM GRD calibration, Product Format Definition section 7.5:
        # calibrated sigma-nought power = (DN^2 + LUT offset) / LUT gain.
        sigma0 = (np.square(dn) + offset) / column_gains[np.newaxis, :]
        sigma0[dn == 0] = np.nan
        sigma0 = sigma0.astype(np.float32)

        destination = np.full((dst_height, dst_width), np.nan, dtype=np.float32)
        reproject(
            source=sigma0,
            destination=destination,
            gcps=adjusted_gcps(gcps, row_offset, col_offset),
            src_crs=gcp_crs,
            src_nodata=np.nan,
            dst_transform=dst_transform,
            dst_crs=TARGET_CRS,
            dst_nodata=np.nan,
            resampling=Resampling.average,
            num_threads=2,
        )

    valid = np.isfinite(destination) & (destination > 0)
    sigma_db = np.full(destination.shape, np.nan, dtype=np.float32)
    sigma_db[valid] = 10.0 * np.log10(destination[valid])
    metadata = {
        "source_file": str(tif_path),
        "source_window": {
            "row_offset": row_offset,
            "col_offset": col_offset,
            "height": int(window.height),
            "width": int(window.width),
        },
        "valid_output_pixels": int(np.count_nonzero(valid)),
        "calibration": "sigma0 = (DN^2 + B) / A; converted to dB with 10*log10(sigma0)",
        "lut_offset": offset,
        "lut_gain_min": float(gains.min()),
        "lut_gain_max": float(gains.max()),
    }
    return sigma_db, metadata


def pooled_otsu_threshold(arrays: list[np.ndarray]) -> tuple[float, dict]:
    samples = []
    for array in arrays:
        values = array[np.isfinite(array)]
        # Use the physically plausible backscatter range for the histogram while
        # retaining all finite pixels for final classification.
        values = values[(values >= -40.0) & (values <= 0.0)]
        samples.append(values)
    pooled = np.concatenate(samples)
    hist, edges = np.histogram(pooled, bins=512, range=(-40.0, 0.0))
    centers = (edges[:-1] + edges[1:]) / 2.0
    probability = hist.astype(np.float64) / hist.sum()
    omega = np.cumsum(probability)
    mean = np.cumsum(probability * centers)
    total_mean = mean[-1]
    denominator = omega * (1.0 - omega)
    between = np.zeros_like(denominator)
    usable = denominator > 0
    between[usable] = np.square(total_mean * omega[usable] - mean[usable]) / denominator[usable]
    index = int(np.argmax(between))
    threshold = float(centers[index])
    return threshold, {
        "method": "shared Otsu threshold on pooled before/after VH sigma-nought dB values",
        "histogram_range_db": [-40.0, 0.0],
        "histogram_bins": 512,
        "pooled_sample_count": int(pooled.size),
    }


def write_raster(path: Path, array: np.ndarray, transform: rasterio.Affine, dtype: str, nodata, tags: dict[str, str]) -> None:
    profile = {
        "driver": "GTiff",
        "height": array.shape[0],
        "width": array.shape[1],
        "count": 1,
        "dtype": dtype,
        "crs": TARGET_CRS,
        "transform": transform,
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
        "nodata": nodata,
    }
    with rasterio.open(path, "w", **profile) as destination:
        destination.write(array.astype(dtype), 1)
        destination.update_tags(**tags)


def polygon_area(coordinates: list) -> float:
    def ring_area(ring: list[list[float]]) -> float:
        x = np.asarray([point[0] for point in ring])
        y = np.asarray([point[1] for point in ring])
        return abs(float(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))) / 2.0
    return ring_area(coordinates[0]) - sum(ring_area(ring) for ring in coordinates[1:])


def export_change_geojson(change: np.ndarray, transform: rasterio.Affine, threshold: float, path: Path) -> dict[str, int]:
    categories = {
        1: "persistent_low_backscatter",
        2: "new_low_backscatter_after_fiona",
        3: "low_backscatter_no_longer_present",
    }
    features = []
    counts = {label: 0 for label in categories.values()}
    change_mask = (change > 0) & (change < 255)
    feature_number = 0
    for geometry, value in shapes(change, mask=change_mask, transform=transform, connectivity=8):
        code = int(value)
        area_m2 = polygon_area(geometry["coordinates"])
        if area_m2 < MIN_COMPONENT_PIXELS * TARGET_RESOLUTION_M**2:
            continue
        geometry_wgs84 = transform_geom(TARGET_CRS, "EPSG:4326", geometry, precision=6)
        label = categories[code]
        counts[label] += 1
        feature_number += 1
        exterior = geometry_wgs84["coordinates"][0]
        center_lon = (min(point[0] for point in exterior) + max(point[0] for point in exterior)) / 2.0
        center_lat = (min(point[1] for point in exterior) + max(point[1] for point in exterior)) / 2.0
        features.append({
            "type": "Feature",
            "id": f"fiona-{feature_number:04d}",
            "geometry": geometry_wgs84,
            "properties": {
                "feature_id": f"fiona-{feature_number:04d}",
                "category": label,
                "area_ha": round(area_m2 / 10_000.0, 2),
                "center_lon": round(center_lon, 6),
                "center_lat": round(center_lat, 6),
                "threshold_db": round(threshold, 3),
                "polarization": "VH",
                "interpretation": "candidate only; requires validation",
            },
        })
    collection = {
        "type": "FeatureCollection",
        "name": "Hurricane Fiona RCM low-backscatter change candidates",
        "features": features,
    }
    path.write_text(json.dumps(collection, separators=(",", ":")), encoding="utf-8")
    return counts


def write_preview(after_db: np.ndarray, change: np.ndarray, path: Path) -> None:
    gray = np.clip((after_db + 30.0) / 25.0, 0.0, 1.0)
    gray[~np.isfinite(gray)] = 0.0
    base = (gray * 210 + 25).astype(np.uint8)
    rgb = np.dstack([base, base, base]).astype(np.float32)
    colors = {
        1: np.array([41, 149, 190], dtype=np.float32),
        2: np.array([231, 104, 70], dtype=np.float32),
        3: np.array([132, 92, 182], dtype=np.float32),
    }
    alpha = {1: 0.55, 2: 0.80, 3: 0.65}
    for code, color in colors.items():
        mask = change == code
        rgb[mask] = rgb[mask] * (1.0 - alpha[code]) + color * alpha[code]
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), mode="RGB").save(path)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    transform, width, height, bounds_utm = target_grid()
    arrays: dict[str, np.ndarray] = {}
    scene_reports: dict[str, dict] = {}
    for name, scene in SCENES.items():
        arrays[name], scene_reports[name] = calibrate_and_warp(scene, transform, width, height)
        write_raster(
            OUTPUT / f"fiona_{name}_vh_sigma0_db.tif",
            arrays[name], transform, "float32", np.nan,
            {
                "source_product": scene["product_id"],
                "acquisition_utc": scene["acquisition_utc"],
                "polarization": "VH",
                "calibration": "RCM sigma-nought LUT; dB",
                "interpretation": "calibrated radar backscatter, not a flood map",
            },
        )

    threshold, threshold_report = pooled_otsu_threshold([arrays["before"], arrays["after"]])
    common_valid = np.isfinite(arrays["before"]) & np.isfinite(arrays["after"])
    before_mask = common_valid & (arrays["before"] <= threshold)
    after_mask = common_valid & (arrays["after"] <= threshold)

    before_mask = sieve(before_mask.astype(np.uint8), size=MIN_COMPONENT_PIXELS, connectivity=8).astype(bool)
    after_mask = sieve(after_mask.astype(np.uint8), size=MIN_COMPONENT_PIXELS, connectivity=8).astype(bool)

    change = np.zeros(before_mask.shape, dtype=np.uint8)
    change[before_mask & after_mask] = 1
    change[~before_mask & after_mask & common_valid] = 2
    change[before_mask & ~after_mask & common_valid] = 3
    change[~common_valid] = 255

    tags = {
        "method": "shared pooled Otsu threshold on calibrated RCM VH sigma-nought dB",
        "threshold_db": str(threshold),
        "minimum_component_pixels": str(MIN_COMPONENT_PIXELS),
        "interpretation": "low-backscatter candidate classes; not validated flood extent",
        "class_0": "neither date low-backscatter",
        "class_1": "persistent low-backscatter",
        "class_2": "new low-backscatter after Fiona",
        "class_3": "low-backscatter no longer present",
        "class_255": "no common valid observation",
    }
    write_raster(OUTPUT / "fiona_low_backscatter_change.tif", change, transform, "uint8", 255, tags)
    polygon_counts = export_change_geojson(change, transform, threshold, OUTPUT / "fiona_low_backscatter_change.geojson")
    write_preview(arrays["after"], change, OUTPUT / "fiona_change_preview.png")

    pixel_area_ha = TARGET_RESOLUTION_M**2 / 10_000.0
    summary = {
        "analysis_status": "candidate low-backscatter change; validation required",
        "aoi_wgs84": AOI_WGS84,
        "target_crs": TARGET_CRS,
        "target_resolution_m": TARGET_RESOLUTION_M,
        "target_dimensions": {"width": width, "height": height},
        "target_bounds_utm": bounds_utm,
        "polarization": "VH",
        "before": {**SCENES["before"], **scene_reports["before"]},
        "after": {**SCENES["after"], **scene_reports["after"]},
        "threshold": {"value_db": threshold, **threshold_report},
        "common_valid_area_ha": round(float(np.count_nonzero(common_valid)) * pixel_area_ha, 2),
        "class_areas_ha": {
            "persistent_low_backscatter": round(float(np.count_nonzero(change == 1)) * pixel_area_ha, 2),
            "new_low_backscatter_after_fiona": round(float(np.count_nonzero(change == 2)) * pixel_area_ha, 2),
            "low_backscatter_no_longer_present": round(float(np.count_nonzero(change == 3)) * pixel_area_ha, 2),
        },
        "exported_polygon_counts": polygon_counts,
        "limitations": [
            "Low radar backscatter is not unique to open water.",
            "Radar shadow, smooth wet surfaces, roads, and other low-return targets may be included.",
            "Tidal state and acquisition timing may contribute to coastal differences.",
            "The after scene was acquired on September 24, 2022 and does not represent peak conditions throughout the storm.",
            "No terrain mask, permanent-water mask, or field validation has yet been applied.",
        ],
    }
    # Remove Path values before serializing.
    for scene in ("before", "after"):
        summary[scene]["folder"] = str(summary[scene]["folder"])
    (OUTPUT / "fiona_analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
