"""Download global GBIF occurrence density (GBIF Maps API v2, EPSG:4326, zoom 0, 8-px square bins ≈ 0.35°)
and decode the two vector tiles into bin centres + record totals -> data/gbif_bins.npz, data/gbif_bins.json.

Note: the Maps API reflects the live GBIF index; it has no DOI. Counts will drift as GBIF grows.
The figure in the talk used the retrieval of 2026-09-26 (data/gbif_bins.json).
"""
import json
import time
from pathlib import Path

import mapbox_vector_tile as mvt
import numpy as np
import requests

URL = "https://api.gbif.org/v2/map/occurrence/density/0/{x}/0.mvt?srs=EPSG:4326&bin=square&squareSize=8"
Path("data").mkdir(exist_ok=True)
lons, lats, tots = [], [], []
for x in (0, 1):
    r = requests.get(URL.format(x=x), timeout=120); r.raise_for_status()
    t = mvt.decode(r.content)
    ext = t["occurrence"]["extent"]
    for f in t["occurrence"]["features"]:
        ring = np.array(f["geometry"]["coordinates"][0], float)
        cx, cy = ring[:, 0].mean(), ring[:, 1].mean()
        lons.append(-180 + x * 180 + cx / ext * 180); lats.append(-90 + cy / ext * 180)
        tots.append(f["properties"]["total"])
lons, lats, tots = map(np.array, (lons, lats, tots))
np.savez("data/gbif_bins.npz", lon=lons, lat=lats, total=tots)
json.dump({"total": int(tots.sum()), "retrieved": time.strftime("%Y-%m-%d"),
           "source": "GBIF Maps API v2 density, EPSG:4326, z0, bin=square&squareSize=8"},
          open("data/gbif_bins.json", "w"))
print("records", int(tots.sum()))
