"""GBIF records per HEALPix cell since the 2024 fire season (from 2024-10-01), Beni."""
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import requests

# healpix-connector: pip-install it, or point HEALPIX_CONNECTOR at a checkout (see ../README.md)
if os.environ.get("HEALPIX_CONNECTOR"):
    sys.path.insert(0, str(Path(os.environ["HEALPIX_CONNECTOR"]) / "src"))
from healpix_connector.connectors import gbif  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "results"
SINCE = "2024-10-01,2026-09-30"


def wkt(lon4, lat4):
    pts = [f"{x:.6f} {y:.6f}" for x, y in zip(lon4, lat4)]
    return "POLYGON((" + ",".join(pts + [pts[0]]) + "))"


c = np.load(OUT / "cells.npz")
f = np.load(OUT / "fire_cells.npz")
s = requests.Session()
post = np.zeros(c["cells"].size, dtype=np.int64)
for i in range(post.size):
    p = {"geometry": wkt(c["vlon"][i], c["vlat"][i]), "hasCoordinate": "true", "eventDate": SINCE,
         "checklistKey": gbif.COL_XR, "limit": 0}
    post[i] = int(gbif._get(s, f"{gbif.API}/occurrence/search", p)["count"])
    time.sleep(0.15)
    if i % 150 == 0:
        print(i, flush=True)
bf = f["burned_frac9"]
heavy = bf > 0.25
out = {"since": SINCE, "records_since": int(post.sum()),
       "cells_with_any_record_since_pct": round(100 * float((post > 0).mean()), 1),
       "heavily_burned_cells": int(heavy.sum()),
       "heavily_burned_without_record_since": int((heavy & (post == 0)).sum()),
       "heavily_burned_without_record_since_pct": round(100 * float((heavy & (post == 0)).sum() / max(1, heavy.sum())), 1),
       "heavily_burned_with_records_before_but_none_since": int((heavy & (post == 0) & (c["counts"] > 0)).sum())}
np.save(OUT / "post_fire_counts.npy", post)
json.dump(out, open(OUT / "postfire_summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
