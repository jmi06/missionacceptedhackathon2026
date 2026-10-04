from __future__ import annotations

import json
import math
import zipfile
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

ROOT = Path(r"C:\Users\Greyson Malabanan\Documents\ChatGPT\Mission Accepted Hackathon")
DOWNLOADS = Path(r"C:\Users\Greyson Malabanan\Downloads")
OUTPUT = ROOT / "data" / "processed" / "july2023"
WEB = ROOT / "chignecto-resilience-demo" / "dist" / "data" / "events"

AOI_WGS84 = (-64.45, 45.84, -63.95, 46.06)
TARGET_CRS = "EPSG:32620"
TARGET_RESOLUTION_M = 50.0
MIN_COMPONENT_PIXELS = 4

SCENES = {
    "before": {
        "zip": DOWNLOADS / "before 4.zip",
        "acquisition_utc": "2023-07-17T21:55:39Z",
        "product_id": "RCM3_OK2430353_PK2653571_1_SC50MA_20230717_215539_VV_VH_GRD",
        "satellite": "RCM-3",
    },
    "during": {
        "zip": DOWNLOADS / "shortlyafter 4.zip",
        "acquisition_utc": "2023-07-21T21:55:17Z",
        "product_id": "RCM1_OK2430353_PK2659153_1_SC50MA_20230721_215517_VV_VH_GRD",
        "satellite": "RCM-1",
    },
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def find_member(archive: zipfile.ZipFile, suffix: str) -> str:
    matches = [name for name in archive.namelist() if name.endswith(suffix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {suffix}, found {len(matches)}")
    return matches[0]


def read_sigma_lut(data: bytes) -> tuple[np.ndarray, np.ndarray, float]:
    root = ET.fromstring(data)
    values = {local_name(el.tag): (el.text or "").strip() for el in root.iter()}
    count = int(values["numberOfValues"])
    positions = int(values["pixelFirstLutValue"]) + np.arange(count, dtype=np.float64) * int(values["stepSize"])
    gains = np.asarray([float(value) for value in values["gains"].split()], dtype=np.float64)
    if len(gains) != count:
        raise ValueError("Sigma LUT gain count does not match declaration")
    return positions, gains, float(values["offset"])


def adjusted_gcps(gcps, row_offset: int, col_offset: int):
    return [GroundControlPoint(row=g.row-row_offset, col=g.col-col_offset, x=g.x, y=g.y, z=g.z, id=g.id, info=g.info) for g in gcps]


def source_window_for_aoi(gcps, width: int, height: int) -> Window:
    west, south, east, north = AOI_WGS84
    xs = [west, east, east, west, (west+east)/2]
    ys = [south, south, north, north, (south+north)/2]
    with GCPTransformer(gcps) as transformer:
        rows, cols = transformer.rowcol(xs, ys)
    margin = 250
    r0, r1 = max(0, min(rows)-margin), min(height, max(rows)+margin)
    c0, c1 = max(0, min(cols)-margin), min(width, max(cols)+margin)
    if r1 <= r0 or c1 <= c0:
        raise RuntimeError("Study area does not overlap RCM scene")
    return Window(c0, r0, c1-c0, r1-r0)


def target_grid():
    left, bottom, right, top = transform_bounds("EPSG:4326", TARGET_CRS, *AOI_WGS84, densify_pts=21)
    width = math.ceil((right-left)/TARGET_RESOLUTION_M)
    height = math.ceil((top-bottom)/TARGET_RESOLUTION_M)
    return from_origin(left, top, TARGET_RESOLUTION_M, TARGET_RESOLUTION_M), width, height, (left,bottom,right,top)


def calibrate(scene: dict, dst_transform, dst_width: int, dst_height: int):
    with zipfile.ZipFile(scene["zip"]) as archive:
        tif_member = find_member(archive, "_VH.tif")
        lut_member = find_member(archive, "lutSigma_VH.xml")
        positions, gains, offset = read_sigma_lut(archive.read(lut_member))

    vsi = "/vsizip/" + scene["zip"].as_posix() + "/" + tif_member
    with rasterio.open(vsi) as source:
        gcps, gcp_crs = source.gcps
        if not gcps or str(gcp_crs) != "EPSG:4326":
            raise RuntimeError("Expected EPSG:4326 GCPs")
        window = source_window_for_aoi(gcps, source.width, source.height)
        row_offset, col_offset = int(window.row_off), int(window.col_off)
        dn = source.read(1, window=window).astype(np.float64)
        columns = np.arange(col_offset, col_offset+dn.shape[1], dtype=np.float64)
        column_gains = np.interp(columns, positions, gains)
        sigma0 = (np.square(dn)+offset) / column_gains[np.newaxis,:]
        sigma0[dn == 0] = np.nan
        destination = np.full((dst_height,dst_width), np.nan, dtype=np.float32)
        reproject(
            source=sigma0.astype(np.float32),
            destination=destination,
            gcps=adjusted_gcps(gcps,row_offset,col_offset),
            src_crs=gcp_crs,
            src_nodata=np.nan,
            dst_transform=dst_transform,
            dst_crs=TARGET_CRS,
            dst_nodata=np.nan,
            resampling=Resampling.average,
            num_threads=2,
        )
    valid = np.isfinite(destination) & (destination > 0)
    db = np.full(destination.shape, np.nan, dtype=np.float32)
    db[valid] = 10*np.log10(destination[valid])
    return db, {"source_member":tif_member,"valid_output_pixels":int(valid.sum()),"lut_offset":offset,"lut_gain_min":float(gains.min()),"lut_gain_max":float(gains.max())}


def otsu(arrays):
    pooled=np.concatenate([a[np.isfinite(a) & (a>=-40) & (a<=0)] for a in arrays])
    hist,edges=np.histogram(pooled,bins=512,range=(-40,0))
    centers=(edges[:-1]+edges[1:])/2
    p=hist.astype(float)/hist.sum(); omega=np.cumsum(p); mean=np.cumsum(p*centers); total=mean[-1]
    denom=omega*(1-omega); between=np.zeros_like(denom); ok=denom>0
    between[ok]=(total*omega[ok]-mean[ok])**2/denom[ok]
    return float(centers[int(np.argmax(between))]), int(pooled.size)


def ring_area(ring):
    x=np.asarray([p[0] for p in ring]); y=np.asarray([p[1] for p in ring])
    return abs(float(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1))))/2


def export_geojson(change, transform, threshold, path):
    labels={1:"persistent_low_backscatter",2:"new_low_backscatter_during_july2023",3:"low_backscatter_no_longer_present"}
    features=[]; counts={v:0 for v in labels.values()}; number=0
    for geometry,value in shapes(change,mask=(change>0)&(change<255),transform=transform,connectivity=8):
        code=int(value); area=ring_area(geometry["coordinates"][0])
        if area < MIN_COMPONENT_PIXELS*TARGET_RESOLUTION_M**2: continue
        geom=transform_geom(TARGET_CRS,"EPSG:4326",geometry,precision=6)
        label=labels[code]; counts[label]+=1; number+=1
        exterior=geom["coordinates"][0]
        lon=(min(p[0] for p in exterior)+max(p[0] for p in exterior))/2
        lat=(min(p[1] for p in exterior)+max(p[1] for p in exterior))/2
        features.append({"type":"Feature","id":f"july2023-{number:04d}","geometry":geom,"properties":{"feature_id":f"july2023-{number:04d}","event_id":"july2023","category":label,"area_ha":round(area/10000,2),"center_lon":round(lon,6),"center_lat":round(lat,6),"threshold_db":round(threshold,3),"polarization":"VH","interpretation":"candidate only; requires validation"}})
    path.write_text(json.dumps({"type":"FeatureCollection","name":"July 2023 RCM low-backscatter change candidates","features":features},separators=(",",":")),encoding="utf-8")
    return counts


def write_raster(path,array,transform,dtype,nodata,tags):
    with rasterio.open(path,"w",driver="GTiff",height=array.shape[0],width=array.shape[1],count=1,dtype=dtype,crs=TARGET_CRS,transform=transform,compress="deflate",tiled=True,blockxsize=256,blockysize=256,nodata=nodata) as dst:
        dst.write(array.astype(dtype),1); dst.update_tags(**tags)


def render_web(data, valid, low, high, path):
    scaled=np.clip(np.nan_to_num((data-low)/(high-low),nan=0),0,1)**0.82
    gray=(scaled*235+12).astype(np.uint8)
    rgba=np.zeros((*data.shape,4),dtype=np.uint8); rgba[...,:3]=gray[...,None]; rgba[...,3]=np.where(valid,235,0).astype(np.uint8)
    Image.fromarray(rgba,"RGBA").save(path,optimize=True)


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True); WEB.mkdir(parents=True,exist_ok=True)
    transform,width,height,bounds_utm=target_grid()
    arrays={}; reports={}
    for name,scene in SCENES.items():
        print(f"Processing {name}...")
        arrays[name],reports[name]=calibrate(scene,transform,width,height)
        write_raster(OUTPUT/f"july2023_{name}_vh_sigma0_db.tif",arrays[name],transform,"float32",np.nan,{"source_product":scene["product_id"],"acquisition_utc":scene["acquisition_utc"],"polarization":"VH","interpretation":"calibrated radar backscatter, not a flood map"})

    threshold,sample_count=otsu(list(arrays.values()))
    common=np.isfinite(arrays["before"]) & np.isfinite(arrays["during"])
    before=sieve((common & (arrays["before"]<=threshold)).astype(np.uint8),size=MIN_COMPONENT_PIXELS,connectivity=8).astype(bool)
    during=sieve((common & (arrays["during"]<=threshold)).astype(np.uint8),size=MIN_COMPONENT_PIXELS,connectivity=8).astype(bool)
    change=np.zeros(before.shape,dtype=np.uint8)
    change[before&during]=1; change[~before&during&common]=2; change[before&~during&common]=3; change[~common]=255
    write_raster(OUTPUT/"july2023_low_backscatter_change.tif",change,transform,"uint8",255,{"threshold_db":str(threshold),"interpretation":"candidate change classes; July 21 image captured during event onset"})
    counts=export_geojson(change,transform,threshold,OUTPUT/"july2023_low_backscatter_change.geojson")

    pooled=np.concatenate([arrays["before"][common],arrays["during"][common]])
    low,high=np.percentile(pooled,[2,98]).tolist()
    render_web(arrays["before"],common,low,high,WEB/"july2023-before-map.png")
    render_web(arrays["during"],common,low,high,WEB/"july2023-during-map.png")
    west,south,east,north=transform_bounds(TARGET_CRS,"EPSG:4326",*bounds_utm,densify_pts=21)

    pixel_ha=TARGET_RESOLUTION_M**2/10000
    summary={
      "event_id":"july2023",
      "event_name":"Nova Scotia July 2023 extreme rainfall",
      "analysis_status":"comparable RCM candidate change; July 21 scene captured during event onset",
      "aoi_wgs84":AOI_WGS84,
      "target_crs":TARGET_CRS,
      "target_resolution_m":TARGET_RESOLUTION_M,
      "polarization":"VH",
      "before":{**{k:str(v) if isinstance(v,Path) else v for k,v in SCENES["before"].items()},**reports["before"]},
      "during":{**{k:str(v) if isinstance(v,Path) else v for k,v in SCENES["during"].items()},**reports["during"]},
      "threshold":{"value_db":threshold,"method":"shared Otsu threshold on pooled before/during VH sigma-nought dB values","pooled_sample_count":sample_count},
      "common_valid_area_ha":round(float(common.sum())*pixel_ha,2),
      "class_areas_ha":{"persistent_low_backscatter":round(float((change==1).sum())*pixel_ha,2),"new_low_backscatter_during_july2023":round(float((change==2).sum())*pixel_ha,2),"low_backscatter_no_longer_present":round(float((change==3).sum())*pixel_ha,2)},
      "exported_polygon_counts":counts,
      "web_imagery":{"bounds_wgs84":[[south,west],[north,east]],"shared_display_stretch_db":[round(low,4),round(high,4)],"images":{"before":"data/events/july2023-before-map.png","during":"data/events/july2023-during-map.png"}},
      "limitations":["The July 21 acquisition occurred during the onset of the extreme-rainfall event, not after the full event.","Low radar backscatter is not unique to open water.","No terrain, permanent-water, or field-validation mask has been applied.","The selected Chignecto study area was not the main Halifax-area impact centre reported by authorities."]
    }
    (OUTPUT/"july2023_analysis_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    (WEB/"july2023-analysis.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    (ROOT/"chignecto-resilience-demo"/"dist"/"data"/"july2023_low_backscatter_change.geojson").write_text((OUTPUT/"july2023_low_backscatter_change.geojson").read_text(encoding="utf-8"),encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    main()
