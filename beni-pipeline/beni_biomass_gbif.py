"""ESA CCI Biomass x GBIF on WGS84 HEALPix, Beni lowlands (Bolivia), via healpix-connector.

Run inside healpix-connector's pixi `test` environment:
    <repo>/.pixi/envs/test/bin/python beni_biomass_gbif.py

Outputs (next to this script): results/cells.npz, results/summary.json, results/mammals.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests

# healpix-connector: pip-install it, or point HEALPIX_CONNECTOR at a checkout (see ../README.md)
if os.environ.get("HEALPIX_CONNECTOR"):
    sys.path.insert(0, str(Path(os.environ["HEALPIX_CONNECTOR"]) / "src"))

from healpix_connector import __version__ as HC_VERSION  # noqa: E402
from healpix_connector.binning import bin_to_cells  # noqa: E402
from healpix_connector.connectors import gbif  # noqa: E402
from healpix_connector.conventions import ELLIPSOID, cell_size_m  # noqa: E402
from healpix_connector.region import Region  # noqa: E402
from healpix_connector.sources.geotiff import read_window  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "results"
OUT.mkdir(exist_ok=True)

BBOX = (-67.5, -15.5, -64.5, -12.5)  # lon_min, lat_min, lon_max, lat_max: Beni lowlands
DEPTH = 9  # ~12.7 km equal-area cells on WGS84
AGB_TIF = HERE / "data/S10W070_AGB_2023_v7.tif"
SD_TIF = HERE / "data/S10W070_AGB_SD_2023_v7.tif"
CCI_CITATION = ("Santoro, M.; Cartus, O. (2026): ESA Biomass Climate Change Initiative (Biomass_cci): "
                "Global datasets of forest above-ground biomass for the years 2005-2012 and 2015-2024, "
                "v7.0. NERC EDS CEDA. doi:10.5285/6429d1aafe1e43b9b414e4a5a7f8b903")


def cell_polygons(cells: np.ndarray, depth: int):
    from healpix_geo import nested
    lon, lat = nested.vertices(cells.astype(np.uint64), np.uint8(depth), ellipsoid=ELLIPSOID)
    lon = np.where(lon > 180, lon - 360, lon)
    return lon, lat


def wkt(lon4, lat4) -> str:
    pts = [f"{x:.6f} {y:.6f}" for x, y in zip(lon4, lat4)]
    return "POLYGON((" + ",".join(pts + [pts[0]]) + "))"


def main():
    t0 = time.time()
    # 1. CCI Biomass -> WGS84 HEALPix cells (area-weighted mean + within-cell spread)
    agb = read_window(str(AGB_TIF), BBOX)
    sd = read_window(str(SD_TIF), BBOX)
    s_agb = bin_to_cells(agb.values, agb.lon, agb.lat, DEPTH, agb.res_deg)
    s_sd = bin_to_cells(sd.values, sd.lon, sd.lat, DEPTH, sd.res_deg)
    assert np.array_equal(s_agb.cell_ids, s_sd.cell_ids)
    keep = s_agb.coverage > 0.95  # cells fully inside the window
    cells = s_agb.cell_ids[keep]
    print(f"{cells.size} cells at depth {DEPTH} (~{cell_size_m(DEPTH)/1000:.1f} km), "
          f"{time.time()-t0:.0f}s", flush=True)
    vlon, vlat = cell_polygons(cells, DEPTH)

    # 2. Sampling effort: GBIF record counts per cell (all taxa), exact cell polygons
    session = requests.Session()
    counts = np.zeros(cells.size, dtype=np.int64)
    for i in range(cells.size):
        params = {"geometry": wkt(vlon[i], vlat[i]), "hasCoordinate": "true",
                  "checklistKey": gbif.COL_XR, "limit": 0}
        counts[i] = int(gbif._get(session, f"{gbif.API}/occurrence/search", params)["count"])
        time.sleep(0.15)
        if i % 100 == 0:
            print(f"  counts {i}/{cells.size}", flush=True)
    counts_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # 3. Mammals via the connector, with positional-uncertainty footprints
    mam = gbif.match_name("Mammalia")
    region = Region.from_bbox(*BBOX)
    res = gbif.search(region, taxon_key=str(mam["taxon_key"]), max_records=9000, session=session)
    recs = gbif.to_cells(res.records, DEPTH, footprints=True)
    cell_index = {int(c): i for i, c in enumerate(cells)}
    mam_counts = np.zeros(cells.size, dtype=np.int64)
    for r in recs:
        j = cell_index.get(r["cell"])
        if j is not None:
            mam_counts[j] += 1
    unc_known = np.array([r["footprint_known"] for r in recs])
    fp_n = np.array([len(r["footprint_cells"]) for r in recs])
    unc = np.array([r["coordinateUncertaintyInMeters"] or np.nan for r in recs], dtype=float)

    np.savez(OUT / "cells.npz", cells=cells, depth=DEPTH,
             agb_mean=s_agb.mean[keep], agb_within_std=s_agb.std[keep],
             agb_sd_mean=s_sd.mean[keep], counts=counts, mammal_counts=mam_counts,
             vlon=vlon, vlat=vlat)
    json.dump([{k: r[k] for k in ("gbifID", "datasetKey", "eventDate", "decimalLongitude",
                                  "decimalLatitude", "coordinateUncertaintyInMeters",
                                  "basisOfRecord", "taxon_name", "cell", "footprint_known")}
               | {"footprint_n": len(r["footprint_cells"])} for r in recs],
              open(OUT / "mammals.json", "w"))

    # 4. Summary statistics (descriptive only)
    a = s_agb.mean[keep]
    sampled = counts > 0
    top = np.sort(counts)[::-1]
    n_top5 = max(1, int(round(0.05 * cells.size)))
    rank = lambda x: np.argsort(np.argsort(x))
    rho = float(np.corrcoef(rank(a), rank(counts))[0, 1])
    rw_med = float(np.median(np.repeat(a, np.minimum(counts, 10**6)))) if counts.sum() else None
    summary = {
        "region": {"name": "Beni lowlands, Bolivia", "bbox_lonlat": BBOX},
        "grid": {"dggs": "HEALPix NESTED", "ellipsoid": ELLIPSOID, "depth": DEPTH,
                 "cell_width_km": round(cell_size_m(DEPTH) / 1000, 2), "n_cells": int(cells.size)},
        "biomass": {"source": "ESA CCI Biomass v7.0, AGB 2023, 100 m", "citation": CCI_CITATION,
                    "units": "Mg/ha", "cell_mean_median": float(np.median(a)),
                    "cell_mean_p10_p90": [float(np.percentile(a, 10)), float(np.percentile(a, 90))],
                    "median_within_cell_std": float(np.median(s_agb.std[keep])),
                    "median_product_sd": float(np.median(s_sd.mean[keep])),
                    "median_rel_sd": float(np.median(s_sd.mean[keep] / np.maximum(a, 1e-9)))},
        "gbif_all_taxa": {"total_records_in_cells": int(counts.sum()),
                          "cells_with_records_pct": round(100 * sampled.mean(), 1),
                          "cells_without_records": int((~sampled).sum()),
                          "top5pct_cells_share_of_records_pct":
                              round(100 * top[:n_top5].sum() / max(1, counts.sum()), 1),
                          "median_agb_all_cells": float(np.median(a)),
                          "median_agb_sampled_cells": float(np.median(a[sampled])) if sampled.any() else None,
                          "median_agb_unsampled_cells": float(np.median(a[~sampled])) if (~sampled).any() else None,
                          "record_weighted_median_agb": rw_med,
                          "spearman_agb_vs_count": round(rho, 3),
                          "checklist_key": gbif.COL_XR, "retrieved_at": counts_at,
                          "method": "occurrence/search count per exact WGS84 HEALPix cell polygon"},
        "gbif_mammals": {"taxon": mam, "provenance": res.provenance, "n_records": len(recs),
                         "cells_with_mammal_records_pct": round(100 * (mam_counts > 0).mean(), 1),
                         "uncertainty_stated_pct": round(100 * unc_known.mean(), 1) if recs else None,
                         "median_uncertainty_m": float(np.nanmedian(unc)) if np.isfinite(unc).any() else None,
                         "records_spanning_more_than_one_cell_pct":
                             round(100 * (fp_n > 1).mean(), 1) if recs else None},
        "software": {"healpix-connector": HC_VERSION},
        "runtime_s": round(time.time() - t0),
    }
    json.dump(summary, open(OUT / "summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
