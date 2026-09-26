"""GBIF record density per biodiversity hotspot (records per km2), from GBIF Maps API square bins,
with hotspot areas from equal-area depth-8 HEALPix centres (WGS84). Also land-average density."""
import json

import numpy as np
import shapefile
import shapely
from shapely.geometry import shape
from shapely.ops import unary_union

b = np.load("data/gbif_bins.npz"); d = np.load("data/cells_d4.npz")
cell8_km2 = 4 * np.pi * 6371.0**2 / d["klon"].size
r = shapefile.Reader("external/hotspots_2016_1.shp")
hs = {}
for sh, rec in zip(r.shapes(), r.records()):
    if rec[1] == "hotspot area":
        g = shape(sh.__geo_interface__)
        hs[rec[0]] = unary_union([hs[rec[0]], g]) if rec[0] in hs else g
land = unary_union([shape(f["geometry"]) for f in json.load(open("external/ne_50m_land.geojson"))["features"]])
shapely.prepare(land)
kx, ky = d["klon"].astype(float), d["klat"].astype(float)
bx, by = b["lon"], b["lat"]
on_land_bin = shapely.contains_xy(land, bx, by)
land_area = shapely.contains_xy(land, kx, ky).sum() * cell8_km2
rows = []
for name, g in hs.items():
    shapely.prepare(g)
    area = shapely.contains_xy(g, kx, ky).sum() * cell8_km2
    rec = b["total"][shapely.contains_xy(g, bx, by)].sum()
    if area > 0:
        rows.append({"hotspot": name, "area_km2": round(float(area)), "records": int(rec), "per_km2": float(rec / area)})
rows.sort(key=lambda x: -x["per_km2"])
out = {"land_average_per_km2": float(b["total"][on_land_bin].sum() / land_area), "hotspots": rows}
json.dump(out, open("data/per_hotspot.json", "w"), indent=1)
print("land average %.2f /km2" % out["land_average_per_km2"])
for x in rows:
    print(f"{x['per_km2']:8.2f}  {x['hotspot']}")
