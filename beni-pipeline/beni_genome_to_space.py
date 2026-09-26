"""From genome to space on one grid (Beni lowlands): DNA-sequenced GBIF records, a zoonotic
reservoir host (Calomys callosus, Machupo virus), BIOMASS forest height and CHELSA climate,
all on WGS84 HEALPix depth 9 via healpix-connector.

Needs results/cells.npz (beni_biomass_gbif.py) and results/fh_cells.npz (beni_biomass_fh.py).
Run in healpix-connector's pixi `test` environment.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import requests

# healpix-connector: pip-install it, or point HEALPIX_CONNECTOR at a checkout (see ../README.md)
if os.environ.get("HEALPIX_CONNECTOR"):
    sys.path.insert(0, str(Path(os.environ["HEALPIX_CONNECTOR"]) / "src"))
from healpix_connector.binning import bin_to_cells  # noqa: E402
from healpix_connector.connectors import gbif  # noqa: E402
from healpix_connector.region import Region  # noqa: E402
from healpix_connector.sources import chelsa  # noqa: E402
from healpix_connector.sources.geotiff import read_window  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "results"
BBOX = (-67.5, -15.5, -64.5, -12.5)
DEPTH = 9


def counts_on(cells, recs):
    idx = {int(c): i for i, c in enumerate(cells)}
    n = np.zeros(cells.size, dtype=np.int64)
    for r in gbif.to_cells(recs, DEPTH, footprints=False):
        j = idx.get(r["cell"])
        if j is not None:
            n[j] += 1
    return n


def main():
    c = np.load(OUT / "cells.npz")
    f = np.load(OUT / "fh_cells.npz")
    cells = c["cells"]
    s = requests.Session()
    region = Region.from_bbox(*BBOX)

    seq = gbif.search(region, filters={"isSequenced": "true"}, max_records=2000, session=s)
    host = gbif.match_name("Calomys callosus", session=s)
    hres = gbif.search(region, taxon_key=str(host["taxon_key"]), max_records=3000, session=s)
    seq_n, host_n = counts_on(cells, seq.records), counts_on(cells, hres.records)
    seq_classes = {}
    for r in seq.records:
        k = r.get("class") or r.get("kingdom") or "unknown"
        seq_classes[k] = seq_classes.get(k, 0) + 1
    basis = {}
    for r in seq.records:
        basis[r.get("basisOfRecord")] = basis.get(r.get("basisOfRecord"), 0) + 1

    env = {}
    for n in (1, 12):
        url = chelsa.SOURCE["url_template"].format(n=n)
        w = read_window(url, BBOX)
        st = bin_to_cells(w.values, w.lon, w.lat, DEPTH, w.res_deg)
        j = np.searchsorted(st.cell_ids, cells)
        j[j >= st.cell_ids.size] = 0
        ok = st.cell_ids[j] == cells
        v = np.full(cells.size, np.nan)
        v[ok] = st.mean[j[ok]]
        env[n] = v
        print(f"CHELSA bio{n}: {np.nanmin(v):.1f}..{np.nanmax(v):.1f} {chelsa.BIO[n][1]}", flush=True)

    np.savez(OUT / "g2s_cells.npz", cells=cells, seq_n=seq_n, host_n=host_n, bio1=env[1], bio12=env[12],
             vlon=c["vlon"], vlat=c["vlat"], counts=c["counts"], fh9=f["fh9"], frac9=f["frac9"])
    well = f["frac9"] >= 0.8
    summary = {
        "genome": {"records": len(seq.records), "cells_with_any_pct": round(100 * (seq_n > 0).mean(), 1),
                   "share_of_all_records_pct": round(100 * len(seq.records) / max(1, int(c["counts"].sum())), 2),
                   "basisOfRecord": basis, "provenance": seq.provenance},
        "one_health_host": {"taxon": host, "records": len(hres.records),
                            "cells_with_any_pct": round(100 * (host_n > 0).mean(), 1),
                            "top_cell_share_pct": round(100 * host_n.max() / max(1, host_n.sum()), 1),
                            "provenance": hres.provenance},
        "environment": {"source": chelsa.SOURCE, "bio1_range_degC": [float(np.nanmin(env[1])), float(np.nanmax(env[1]))],
                        "bio12_range_mm": [float(np.nanmin(env[12])), float(np.nanmax(env[12]))]},
        "ecosystem": {"cells_well_observed_by_biomass": int(well.sum()), "of": int(cells.size)},
        "all_four_layers_cells": int(((seq_n > 0) & (host_n > 0) & well & np.isfinite(env[1])).sum()),
    }
    json.dump(summary, open(OUT / "g2s_summary.json", "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in summary.items() if k != "environment"}, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
