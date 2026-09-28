"""Slide 9 zoom: GBIF mammal records in a ~27 km window near Trinidad, with their stated uncertainty.

Reads results/mammals.json (step 1, not shipped) and writes results/fh_zoom_records.npz with only
longitude, latitude and coordinateUncertaintyInMeters for the window -- no species, no dataset, no dates.
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
WINDOW = (-65.05, -14.90, -64.80, -14.65)  # lon_min, lat_min, lon_max, lat_max

recs = json.load(open(HERE / "results" / "mammals.json"))
lon = np.array([r["decimalLongitude"] for r in recs], float)
lat = np.array([r["decimalLatitude"] for r in recs], float)
unc = np.array([r.get("coordinateUncertaintyInMeters") or np.nan for r in recs], float)
w = (lon >= WINDOW[0]) & (lon < WINDOW[2]) & (lat >= WINDOW[1]) & (lat < WINDOW[3])
np.savez(HERE / "results" / "fh_zoom_records.npz", lon=lon[w], lat=lat[w], unc=unc[w], window=np.array(WINDOW))
print(f"{w.sum()} records in the zoom window; {np.isfinite(unc[w]).sum()} state an uncertainty")
