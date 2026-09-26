"""A result from co-located layers (Beni, WGS84 HEALPix depth 11, ~3.2 km):
did 2024 burning depend on pre-fire biomass (ESA CCI 2023) and rainfall (CHELSA)?
Descriptive association only (one region, one fire year).

Needs: data/S10W070_AGB_2023_v7.tif (beni_biomass_gbif.py) and results/fire_cells.npz (beni_fire.py).
Run in healpix-connector's pixi `test` environment.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

# healpix-connector: pip-install it, or point HEALPIX_CONNECTOR at a checkout (see ../README.md)
if os.environ.get("HEALPIX_CONNECTOR"):
    sys.path.insert(0, str(Path(os.environ["HEALPIX_CONNECTOR"]) / "src"))
from healpix_connector.binning import bin_to_cells  # noqa: E402
from healpix_connector.sources import chelsa  # noqa: E402
from healpix_connector.sources.geotiff import read_window  # noqa: E402
from healpix_connector.sources.gridded import sample_cells_from_grid  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "results"
BBOX = (-67.5, -15.5, -64.5, -12.5)
DEPTH = 11

fire = np.load(OUT / "fire_cells.npz")
cells, burned = fire["cells11"], fire["burned_frac11"]

agb_w = read_window(str(HERE / "data/S10W070_AGB_2023_v7.tif"), BBOX)
st = bin_to_cells(agb_w.values, agb_w.lon, agb_w.lat, DEPTH, agb_w.res_deg)
j = np.searchsorted(st.cell_ids, cells); j[j >= st.cell_ids.size] = 0
ok = (st.cell_ids[j] == cells) & (st.coverage[j] > 0.9)
agb = np.full(cells.size, np.nan); agb[ok] = st.mean[j[ok]]

pr = read_window(chelsa.SOURCE["url_template"].format(n=12), BBOX)
cs = sample_cells_from_grid(pr.values, pr.lon, pr.lat, cells, DEPTH, pr.res_deg)
rain = cs.value

m = np.isfinite(agb) & np.isfinite(burned) & np.isfinite(rain)
edges = [0, 10, 25, 50, 100, 150, 400]
labels = ["<10", "10–25", "25–50", "50–100", "100–150", "≥150"]
by_agb = []
for lo, hi, lab in zip(edges[:-1], edges[1:], labels):
    k = m & (agb >= lo) & (agb < hi)
    by_agb.append({"agb_class": lab, "n_cells": int(k.sum()),
                   "mean_burned_pct": round(100 * float(burned[k].mean()), 1) if k.any() else None,
                   "share_cells_burned_over_25pct": round(100 * float((burned[k] > 0.25).mean()), 1) if k.any() else None})
rt = np.nanpercentile(rain[m], [33.3, 66.7])
by_rain = {}
for name, k in [("drier third", rain < rt[0]), ("middle third", (rain >= rt[0]) & (rain < rt[1])), ("wetter third", rain >= rt[1])]:
    k = k & m
    by_rain[name] = {"n": int(k.sum()), "mean_burned_pct": round(100 * float(burned[k].mean()), 1),
                     "range_mm": [round(float(rain[k].min())), round(float(rain[k].max()))]}
rank = lambda x: np.argsort(np.argsort(x))
out = {"depth": DEPTH, "n_cells": int(m.sum()),
       "spearman_agb_vs_burned": round(float(np.corrcoef(rank(agb[m]), rank(burned[m]))[0, 1]), 3),
       "spearman_rain_vs_burned": round(float(np.corrcoef(rank(rain[m]), rank(burned[m]))[0, 1]), 3),
       "spearman_rain_vs_agb": round(float(np.corrcoef(rank(rain[m]), rank(agb[m]))[0, 1]), 3),
       "by_agb_class": by_agb, "by_rain_tercile": by_rain,
       "rain_support": cs.method,
       "sources": {"agb": "ESA CCI Biomass v7.0 2023 (doi:10.5285/6429d1aafe1e43b9b414e4a5a7f8b903)",
                   "fire": "ESA Fire_cci SYN v1.1 2024 (doi:10.5285/d441079fc77f49fabeb41330612b252f)",
                   "rain": "CHELSA v2.1 bio12 1981-2010 (doi:10.16904/envidat.228)"}}
np.savez(OUT / "fire_result.npz", cells=cells, burned=burned, agb=agb, rain=rain, m=m)
json.dump(out, open(OUT / "fire_result.json", "w"), indent=1)
print(json.dumps(out, indent=1))
