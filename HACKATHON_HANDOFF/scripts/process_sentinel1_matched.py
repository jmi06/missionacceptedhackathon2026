from __future__ import annotations

import json
import math
from pathlib import Path
import urllib.request
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
OUTPUT_ROOT = PROJECT / "data" / "processed" / "sentinel1"
WEB_ROOT = PROJECT / "chignecto-resilience-demo" / "dist" / "data"

AOI_WGS84 = (-64.45, 45.84, -63.95, 46.06)
TARGET_CRS = "EPSG:32620"
TARGET_RESOLUTION_M = 50.0
MIN_COMPONENT_PIXELS = 4
AWS_HTTPS = "https://sentinel-s1-l1c.s3.eu-central-1.amazonaws.com/"


EVENTS = {
    "dorian": {
        "label": "Hurricane Dorian",
        "new_class": "new_low_backscatter_after_dorian",
        "before": {
            "acquisition_utc": "2019-08-27T10:30:43Z",
            "product_id": "S1B_IW_GRDH_1SDH_20190827T103043_20190827T103108_017770_021711_9481",
            "base": "GRD/2019/8/27/IW/DH/S1B_IW_GRDH_1SDH_20190827T103043_20190827T103108_017770_021711_9481",
        },
        "after": {
            "acquisition_utc": "2019-09-08T10:30:43Z",
            "product_id": "S1B_IW_GRDH_1SDH_20190908T103043_20190908T103108_017945_021C7C_59C6",
            "base": "GRD/2019/9/8/IW/DH/S1B_IW_GRDH_1SDH_20190908T103043_20190908T103108_017945_021C7C_59C6",
        },
    },
    "lee": {
        "label": "Hurricane Lee",
        "new_class": "new_low_backscatter_after_lee",
        "before": {
            "acquisition_utc": "2023-09-05T10:31:48Z",
            "product_id": "S1A_IW_GRDH_1SDH_20230905T103148_20230905T103213_050191_060A83_BD1E",
            "base": "GRD/2023/9/5/IW/DH/S1A_IW_GRDH_1SDH_20230905T103148_20230905T103213_050191_060A83_BD1E",
        },
        "after": {
            "acquisition_utc": "2023-09-17T10:31:49Z",
            "product_id": "S1A_IW_GRDH_1SDH_20230917T103149_20230917T103214_050366_06106F_D660",
            "base": "GRD/2023/9/17/IW/DH/S1A_IW_GRDH_1SDH_20230917T103149_20230917T103214_050366_06106F_D660",
        },
    },
}


def https_url(base: str, suffix: str) -> str:
    return AWS_HTTPS + base + "/" + suffix


def read_xml(url: str) -> ET.Element:
    request = urllib.request.Request(url, headers={"User-Agent": "Chignecto-Resilience-Monitor/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return ET.fromstring(response.read())


def parse_calibration(url: str) -> tuple[np.ndarray, list[np.ndarray], list[np.ndarray]]:
    root = read_xml(url)
    vectors = [element for element in root.iter() if element.tag.rsplit("}", 1)[-1] == "calibrationVector"]
    lines: list[int] = []
    pixels: list[np.ndarray] = []
    sigma: list[np.ndarray] = []
    for vector in vectors:
        values = {child.tag.rsplit("}", 1)[-1]: (child.text or "").strip() for child in vector}
        lines.append(int(values["line"]))
        pixel_values = np.asarray([float(value) for value in values["pixel"].split()], dtype=np.float64)
        sigma_values = np.asarray([float(value) for value in values["sigmaNought"].split()], dtype=np.float64)
        if pixel_values.size != sigma_values.size:
            raise ValueError("Sentinel-1 calibration vector length mismatch")
        pixels.append(pixel_values)
        sigma.append(sigma_values)
    if not lines:
        raise ValueError("No Sentinel-1 calibration vectors found")
    order = np.argsort(lines)
    return np.asarray(lines, dtype=np.float64)[order], [pixels[i] for i in order], [sigma[i] for i in order]


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
    margin = 300
    row_start = max(0, min(rows) - margin)
    row_stop = min(height, max(rows) + margin)
    col_start = max(0, min(cols) - margin)
    col_stop = min(width, max(cols) + margin)
    if row_stop <= row_start or col_stop <= col_start:
        raise RuntimeError("AOI does not overlap Sentinel-1 scene")
    return Window(col_start, row_start, col_stop - col_start, row_stop - row_start)


def target_grid() -> tuple[rasterio.Affine, int, int, tuple[float, float, float, float]]:
    left, bottom, right, top = transform_bounds("EPSG:4326", TARGET_CRS, *AOI_WGS84, densify_pts=21)
    width = math.ceil((right - left) / TARGET_RESOLUTION_M)
    height = math.ceil((top - bottom) / TARGET_RESOLUTION_M)
    return from_origin(left, top, TARGET_RESOLUTION_M, TARGET_RESOLUTION_M), width, height, (left, bottom, right, top)


def calibration_for_window(
    vector_lines: np.ndarray,
    vector_pixels: list[np.ndarray],
    vector_sigma: list[np.ndarray],
    row_offset: int,
    col_offset: int,
    height: int,
    width: int,
) -> np.ndarray:
    columns = np.arange(col_offset, col_offset + width, dtype=np.float64)
    row_luts = np.vstack([
        np.interp(columns, pixels, sigma).astype(np.float32)
        for pixels, sigma in zip(vector_pixels, vector_sigma)
    ])
    rows = np.arange(row_offset, row_offset + height, dtype=np.float64)
    upper = np.searchsorted(vector_lines, rows, side="right")
    upper = np.clip(upper, 1, len(vector_lines) - 1)
    lower = upper - 1
    denominator = vector_lines[upper] - vector_lines[lower]
    fraction = np.divide(rows - vector_lines[lower], denominator, out=np.zeros_like(rows), where=denominator != 0)
    return row_luts[lower] * (1.0 - fraction[:, None]) + row_luts[upper] * fraction[:, None]


def calibrate_and_warp(scene: dict, dst_transform: rasterio.Affine, dst_width: int, dst_height: int) -> tuple[np.ndarray, dict]:
    measurement_url = https_url(scene["base"], "measurement/iw-hv.tiff")
    calibration_url = https_url(scene["base"], "annotation/calibration/calibration-iw-hv.xml")
    vector_lines, vector_pixels, vector_sigma = parse_calibration(calibration_url)

    with rasterio.Env(GDAL_HTTP_MULTIRANGE="YES", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(measurement_url) as source:
            gcps, gcp_crs = source.gcps
            if not gcps or str(gcp_crs) != "EPSG:4326":
                raise RuntimeError(f"Expected EPSG:4326 GCPs in {scene['product_id']}")
            window = source_window_for_aoi(gcps, source.width, source.height)
            row_offset = int(window.row_off)
            col_offset = int(window.col_off)
            dn = source.read(1, window=window).astype(np.float32)

    calibration = calibration_for_window(
        vector_lines,
        vector_pixels,
        vector_sigma,
        row_offset,
        col_offset,
        dn.shape[0],
        dn.shape[1],
    )
    sigma0 = np.divide(
        np.square(dn, dtype=np.float32),
        np.square(calibration, dtype=np.float32),
        out=np.full(dn.shape, np.nan, dtype=np.float32),
        where=(dn > 0) & (calibration > 0),
    )

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
    return sigma_db, {
        "measurement_url": measurement_url,
        "calibration_url": calibration_url,
        "source_window": {
            "row_offset": row_offset,
            "col_offset": col_offset,
            "height": int(window.height),
            "width": int(window.width),
        },
        "valid_output_pixels": int(np.count_nonzero(valid)),
        "calibration": "sigma0 = DN^2 / sigmaNought_LUT^2; converted to dB with 10*log10(sigma0)",
    }


def pooled_otsu_threshold(arrays: list[np.ndarray]) -> tuple[float, dict]:
    samples = []
    for array in arrays:
        values = array[np.isfinite(array)]
        samples.append(values[(values >= -40.0) & (values <= 0.0)])
    pooled = np.concatenate(samples)
    hist, edges = np.histogram(pooled, bins=512, range=(-40.0, 0.0))
    centers = (edges[:-1] + edges[1:]) / 2.0
    probability = hist.astype(np.float64) / hist.sum()
    omega = np.cumsum(probability)
    mean = np.cumsum(probability * centers)
    denominator = omega * (1.0 - omega)
    between = np.zeros_like(denominator)
    usable = denominator > 0
    between[usable] = np.square(mean[-1] * omega[usable] - mean[usable]) / denominator[usable]
    threshold = float(centers[int(np.argmax(between))])
    return threshold, {
        "method": "shared Otsu threshold on pooled before/after Sentinel-1 HV sigma-nought dB",
        "histogram_range_db": [-40.0, 0.0],
        "histogram_bins": 512,
        "pooled_sample_count": int(pooled.size),
    }


def polygon_area(coordinates: list) -> float:
    def ring_area(ring: list[list[float]]) -> float:
        x = np.asarray([point[0] for point in ring])
        y = np.asarray([point[1] for point in ring])
        return abs(float(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))) / 2.0
    return ring_area(coordinates[0]) - sum(ring_area(ring) for ring in coordinates[1:])


def export_geojson(event_id: str, event: dict, change: np.ndarray, transform: rasterio.Affine, threshold: float, path: Path) -> dict[str, int]:
    categories = {
        1: "persistent_low_backscatter",
        2: event["new_class"],
        3: "low_backscatter_no_longer_present",
    }
    features = []
    counts = {label: 0 for label in categories.values()}
    feature_number = 0
    mask = (change > 0) & (change < 255)
    for geometry, value in shapes(change, mask=mask, transform=transform, connectivity=8):
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
            "id": f"{event_id}-s1-{feature_number:04d}",
            "geometry": geometry_wgs84,
            "properties": {
                "feature_id": f"{event_id}-s1-{feature_number:04d}",
                "event_id": event_id,
                "category": label,
                "area_ha": round(area_m2 / 10_000.0, 2),
                "center_lon": round(center_lon, 6),
                "center_lat": round(center_lat, 6),
                "threshold_db": round(threshold, 3),
                "sensor": "Sentinel-1",
                "polarization": "HV",
                "interpretation": "candidate only; requires validation",
            },
        })
    path.write_text(json.dumps({
        "type": "FeatureCollection",
        "name": f"{event['label']} Sentinel-1 low-backscatter change candidates",
        "features": features,
    }, separators=(",", ":")), encoding="utf-8")
    return counts


def write_raster(path: Path, array: np.ndarray, transform: rasterio.Affine, dtype: str, nodata, tags: dict[str, str]) -> None:
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=array.shape[0],
        width=array.shape[1],
        count=1,
        dtype=dtype,
        crs=TARGET_CRS,
        transform=transform,
        compress="deflate",
        tiled=True,
        blockxsize=256,
        blockysize=256,
        nodata=nodata,
    ) as destination:
        destination.write(array.astype(dtype), 1)
        destination.update_tags(**tags)


def write_map_image(array: np.ndarray, path: Path) -> None:
    valid = np.isfinite(array)
    scaled = np.clip((array + 30.0) / 25.0, 0.0, 1.0)
    scaled = np.power(scaled, 0.85)
    scaled[~valid] = 0.0
    gray = (scaled * 235 + 12).astype(np.uint8)
    rgba = np.zeros((array.shape[0], array.shape[1], 4), dtype=np.uint8)
    rgba[..., :3] = gray[..., None]
    rgba[..., 3] = np.where(valid, 232, 0).astype(np.uint8)
    Image.fromarray(rgba, "RGBA").save(path, optimize=True)


def process_event(event_id: str, event: dict, transform: rasterio.Affine, width: int, height: int, bounds_utm: tuple) -> dict:
    output = OUTPUT_ROOT / event_id
    output.mkdir(parents=True, exist_ok=True)
    arrays: dict[str, np.ndarray] = {}
    reports: dict[str, dict] = {}
    for role in ("before", "after"):
        print(f"Processing {event_id} {role} from public Sentinel-1 COG...")
        arrays[role], reports[role] = calibrate_and_warp(event[role], transform, width, height)
        write_raster(
            output / f"{event_id}_{role}_hv_sigma0_db.tif",
            arrays[role],
            transform,
            "float32",
            np.nan,
            {
                "source_product": event[role]["product_id"],
                "acquisition_utc": event[role]["acquisition_utc"],
                "sensor": "Sentinel-1",
                "polarization": "HV",
                "relative_orbit": "69",
                "orbit_direction": "descending",
                "interpretation": "calibrated radar backscatter, not a flood map",
            },
        )
        write_map_image(arrays[role], WEB_ROOT / "events" / f"{event_id}-{role}-map.png")

    threshold, threshold_report = pooled_otsu_threshold([arrays["before"], arrays["after"]])
    common_valid = np.isfinite(arrays["before"]) & np.isfinite(arrays["after"])
    before_mask = sieve((common_valid & (arrays["before"] <= threshold)).astype(np.uint8), size=MIN_COMPONENT_PIXELS, connectivity=8).astype(bool)
    after_mask = sieve((common_valid & (arrays["after"] <= threshold)).astype(np.uint8), size=MIN_COMPONENT_PIXELS, connectivity=8).astype(bool)
    change = np.zeros(before_mask.shape, dtype=np.uint8)
    change[before_mask & after_mask] = 1
    change[~before_mask & after_mask & common_valid] = 2
    change[before_mask & ~after_mask & common_valid] = 3
    change[~common_valid] = 255

    tags = {
        "method": "shared pooled Otsu threshold on calibrated Sentinel-1 HV sigma-nought dB",
        "threshold_db": str(threshold),
        "minimum_component_pixels": str(MIN_COMPONENT_PIXELS),
        "interpretation": "low-backscatter candidate classes; not validated flood extent",
        "class_1": "persistent low-backscatter",
        "class_2": event["new_class"],
        "class_3": "low-backscatter no longer present",
        "class_255": "no common valid observation",
    }
    write_raster(output / f"{event_id}_low_backscatter_change.tif", change, transform, "uint8", 255, tags)
    geojson_path = output / f"{event_id}_low_backscatter_change.geojson"
    polygon_counts = export_geojson(event_id, event, change, transform, threshold, geojson_path)
    (WEB_ROOT / geojson_path.name).write_bytes(geojson_path.read_bytes())

    pixel_area_ha = TARGET_RESOLUTION_M**2 / 10_000.0
    summary = {
        "event_id": event_id,
        "event": event["label"],
        "analysis_status": "candidate low-backscatter change; validation required",
        "source": "AWS Registry of Open Data Sentinel-1 GRD archive, indexed by Element 84 Earth Search",
        "aoi_wgs84": AOI_WGS84,
        "target_crs": TARGET_CRS,
        "target_resolution_m": TARGET_RESOLUTION_M,
        "target_dimensions": {"width": width, "height": height},
        "target_bounds_utm": bounds_utm,
        "sensor": "Sentinel-1",
        "polarization": "HV",
        "relative_orbit": 69,
        "orbit_direction": "descending",
        "before": {**event["before"], **reports["before"]},
        "after": {**event["after"], **reports["after"]},
        "threshold": {"value_db": threshold, **threshold_report},
        "common_valid_area_ha": round(float(np.count_nonzero(common_valid)) * pixel_area_ha, 2),
        "class_areas_ha": {
            "persistent_low_backscatter": round(float(np.count_nonzero(change == 1)) * pixel_area_ha, 2),
            event["new_class"]: round(float(np.count_nonzero(change == 2)) * pixel_area_ha, 2),
            "low_backscatter_no_longer_present": round(float(np.count_nonzero(change == 3)) * pixel_area_ha, 2),
        },
        "exported_polygon_counts": polygon_counts,
        "limitations": [
            "Low radar backscatter is not unique to open water.",
            "Radar shadow, smooth wet surfaces, roads, tides, and agricultural change may be included.",
            "These dates show conditions at two satellite passes, not continuous or peak-event coverage.",
            "No permanent-water, terrain, tide, or field-validation mask has yet been applied.",
            "The products are calibrated to sigma-nought but are not radiometrically terrain flattened.",
        ],
    }
    summary_path = output / f"{event_id}_sentinel1_analysis_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (WEB_ROOT / "events" / f"{event_id}-sentinel1-analysis.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    WEB_ROOT.mkdir(parents=True, exist_ok=True)
    (WEB_ROOT / "events").mkdir(parents=True, exist_ok=True)
    transform, width, height, bounds_utm = target_grid()
    summaries = {}
    for event_id, event in EVENTS.items():
        summaries[event_id] = process_event(event_id, event, transform, width, height, bounds_utm)
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
