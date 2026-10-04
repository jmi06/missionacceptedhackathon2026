from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

import rasterio


ROOT = Path(r"C:\Users\Greyson Malabanan\Documents\ChatGPT\Mission Accepted Hackathon\data\rcm-fiona")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def interesting_xml_values(path: Path) -> dict[str, list[str]]:
    wanted = (
        "acquisition", "beam", "orbit", "pass", "polar", "producttype",
        "processing", "pixelspacing", "linespacing", "timeordering",
        "geodeticcoordinate", "latitude", "longitude", "numberoflines",
        "numberofsamples", "samplesperline", "satellite", "sensor",
    )
    root = ET.parse(path).getroot()
    values: dict[str, list[str]] = {}
    for element in root.iter():
        name = local_name(element.tag)
        text = (element.text or "").strip()
        if text and any(token in name.lower() for token in wanted):
            values.setdefault(name, [])
            if text not in values[name] and len(values[name]) < 12:
                values[name].append(text)
    return values


def lut_summary(path: Path) -> dict:
    root = ET.parse(path).getroot()
    content = {local_name(el.tag): (el.text or "").strip() for el in root.iter()}
    gains = [float(value) for value in content["gains"].split()]
    return {
        "pixelFirstLutValue": int(content["pixelFirstLutValue"]),
        "stepSize": int(content["stepSize"]),
        "numberOfValues": int(content["numberOfValues"]),
        "offset": float(content["offset"]),
        "gain_count": len(gains),
        "gain_min": min(gains),
        "gain_max": max(gains),
        "gain_first": gains[0],
        "gain_last": gains[-1],
    }


def inspect_scene(folder: Path) -> dict:
    tif = next(folder.glob("*_VH.tif"))
    with rasterio.open(tif) as source:
        gcps, gcp_crs = source.gcps
        raster = {
            "file": str(tif),
            "driver": source.driver,
            "dtype": source.dtypes[0],
            "width": source.width,
            "height": source.height,
            "count": source.count,
            "crs": str(source.crs) if source.crs else None,
            "transform": tuple(source.transform),
            "bounds": tuple(source.bounds),
            "gcp_count": len(gcps),
            "gcp_crs": str(gcp_crs) if gcp_crs else None,
            "rpc_available": source.rpcs is not None,
            "nodata": source.nodata,
            "block_shapes": source.block_shapes,
        }
    return {
        "raster": raster,
        "product_metadata": interesting_xml_values(folder / "product.xml"),
        "sigma_lut": lut_summary(folder / "lutSigma_VH.xml"),
    }


if __name__ == "__main__":
    report = {name: inspect_scene(ROOT / name) for name in ("before", "after")}
    print(json.dumps(report, indent=2))
