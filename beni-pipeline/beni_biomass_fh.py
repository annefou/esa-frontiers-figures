"""BIOMASS L2A forest height x GBIF x ESA CCI Biomass on WGS84 HEALPix (Beni), via healpix-connector.

Needs: biomass_fh/ (get_biomass_fh.py) and results/cells.npz, results/mammals.json (beni_biomass_gbif.py).
Run in healpix-connector's pixi `test` environment.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from pathlib import Path

import numpy as np

# healpix-connector: pip-install it, or point HEALPIX_CONNECTOR at a checkout (see ../README.md)
if os.environ.get("HEALPIX_CONNECTOR"):
    sys.path.insert(0, str(Path(os.environ["HEALPIX_CONNECTOR"]) / "src"))
from healpix_connector.binning import bin_to_cells  # noqa: E402
from healpix_connector.conventions import ELLIPSOID, cell_size_m  # noqa: E402
from healpix_connector.sources.geotiff import read_window  # noqa: E402

HERE = Path(__file__).parent
FH_DIR = HERE / "biomass_fh"
OUT = HERE / "results"
BBOX = (-67.5, -15.5, -64.5, -12.5)
FINE, COARSE = 12, 9
QUALITY_MIN_MEDIAN = 1.0
SHIFT = np.uint64(2 * (FINE - COARSE))


def clipped_bbox(path):
    """BBOX intersected with the file's bounds.

    Works around healpix-connector read_window placing pixels wrongly when the
    requested window extends beyond the file (it clips the data but derives the
    coordinates from the unclipped window)."""
    import rasterio
    with rasterio.open(path) as src:
        b = src.bounds
    return (max(BBOX[0], b.left), max(BBOX[1], b.bottom), min(BBOX[2], b.right), min(BBOX[3], b.top))


def combine(stats_list):
    """Pixel-count-weighted mean over repeat acquisitions, per cell; also count acquisitions."""
    ids = np.unique(np.concatenate([s.cell_ids for s in stats_list]))
    wsum = np.zeros(ids.size); vsum = np.zeros(ids.size); n_acq = np.zeros(ids.size, int)
    for s in stats_list:
        full = s.coverage > 0.9  # only cells the swath covers fully
        j = np.searchsorted(ids, s.cell_ids[full])
        w = s.pixel_count[full].astype(float)
        wsum[j] += w; vsum[j] += w * s.mean[full]; n_acq[j] += 1
    ok = wsum > 0
    return ids[ok], vsum[ok] / wsum[ok], n_acq[ok]


def main():
    fh_stats, q_stats, dates, excluded = [], [], [], []
    for f in sorted(glob.glob(str(FH_DIR / "*_i_fh.tiff"))):
        # Guardrail: read the product's own quality layer and drop failed acquisitions.
        # Observed: two 2026-07-25 products have quality ~0 (others 2-15), no height of
        # ambiguity in their annotation, and forest heights 20-26 m above overlapping dates.
        import rasterio
        with rasterio.open(f.replace("_i_fh.tiff", "_i_quality.tiff")) as src:
            qa = src.read(1)
        qmed = float(np.median(qa[qa != -9999.0]))
        if qmed < QUALITY_MIN_MEDIAN:
            excluded.append({"product": Path(f).name, "median_quality": round(qmed, 2)})
            continue
        w = read_window(f, clipped_bbox(f))
        w.values[w.values == -9999.0] = np.nan
        fh_stats.append(bin_to_cells(w.values, w.lon, w.lat, FINE, w.res_deg))
        qf = f.replace("_i_fh.tiff", "_i_quality.tiff")
        q = read_window(qf, clipped_bbox(qf))
        q.values[q.values == -9999.0] = np.nan
        q_stats.append(bin_to_cells(q.values, q.lon, q.lat, FINE, q.res_deg))
        dates.append(Path(f).name[15:23])
    fine_ids, fh, n_acq = combine(fh_stats)
    qids, qual, _ = combine(q_stats)
    assert np.array_equal(fine_ids, qids)
    print(f"{fine_ids.size} depth-{FINE} cells with BIOMASS forest height", flush=True)

    # Parent join to depth 9 (NESTED: parent = cell >> 2*(fine-coarse))
    c = np.load(OUT / "cells.npz")
    coarse_cells = c["cells"]
    parent = fine_ids >> SHIFT
    idx = np.searchsorted(coarse_cells, parent)
    idx[idx >= coarse_cells.size] = 0
    inside = coarse_cells[idx] == parent
    n_children = 4 ** (FINE - COARSE)
    fh9 = np.full(coarse_cells.size, np.nan); frac9 = np.zeros(coarse_cells.size)
    s = np.bincount(idx[inside], weights=fh[inside], minlength=coarse_cells.size)
    k = np.bincount(idx[inside], minlength=coarse_cells.size)
    fh9[k > 0] = s[k > 0] / k[k > 0]
    frac9 = k / n_children
    well = frac9 >= 0.8  # coarse cells at least 80 % observed by BIOMASS

    counts, agb = c["counts"], c["agb_mean"]
    rank = lambda x: np.argsort(np.argsort(x))
    rho_fh_agb = float(np.corrcoef(rank(fh9[well]), rank(agb[well]))[0, 1])
    rho_fh_cnt = float(np.corrcoef(rank(fh9[well]), rank(counts[well]))[0, 1])
    tall = fh9 >= 15
    area_tall = float((tall & well).sum() / well.sum())
    rec_tall = float(counts[tall & well].sum() / counts[well].sum())

    # Mammal records on the fine grid
    mam = json.load(open(OUT / "mammals.json"))
    from healpix_geo import nested
    mlon = np.array([m["decimalLongitude"] for m in mam]); mlat = np.array([m["decimalLatitude"] for m in mam])
    mcell = nested.lonlat_to_healpix(mlon, mlat, np.uint8(FINE), ellipsoid=ELLIPSOID)
    j = np.searchsorted(fine_ids, mcell); j[j >= fine_ids.size] = 0
    m_obs = fine_ids[j] == mcell
    fine_with_mam = np.unique(mcell[m_obs]).size

    vlon, vlat = nested.vertices(fine_ids, np.uint8(FINE), ellipsoid=ELLIPSOID)
    vlon = np.where(vlon > 180, vlon - 360, vlon)
    np.savez(OUT / "fh_cells.npz", fine_ids=fine_ids, fh=fh, qual=qual, n_acq=n_acq, vlon=vlon, vlat=vlat,
             fh9=fh9, frac9=frac9, mlon=mlon[m_obs], mlat=mlat[m_obs])
    summary = {
        "biomass_fh": {"product": "BIOMASS L2A FP_FH__L2A forest height [m], BPS-Biomass L2a processor 4.4.4, 200 m",
                       "n_products_used": len(fh_stats), "excluded_by_quality_rule": excluded,
                       "quality_rule": f"drop product if median quality < {QUALITY_MIN_MEDIAN}", "acquisition_dates": sorted(set(dates)),
                       "source": "ESA MAAP, collection BiomassLevel2a",
                       "fine_depth": FINE, "fine_cell_km": round(cell_size_m(FINE) / 1000, 2),
                       "n_fine_cells": int(fine_ids.size),
                       "fh_median_m": float(np.median(fh)), "fh_p90_m": float(np.percentile(fh, 90)),
                       "median_acquisitions_per_cell": float(np.median(n_acq)),
                       "quality_median": float(np.median(qual))},
        "join_depth9": {"coarse_cells_well_observed": int(well.sum()), "of": int(coarse_cells.size),
                        "spearman_fh_vs_cci_agb": round(rho_fh_agb, 3),
                        "spearman_fh_vs_gbif_count": round(rho_fh_cnt, 3),
                        "area_share_fh_ge_15m": round(area_tall, 3),
                        "record_share_fh_ge_15m": round(rec_tall, 3)},
        "mammals_on_fine_grid": {"records_in_observed_cells": int(m_obs.sum()), "of": len(mam),
                                 "fine_cells_with_mammal_records": int(fine_with_mam),
                                 "fine_cells_with_mammal_records_pct": round(100 * fine_with_mam / fine_ids.size, 2)},
    }
    json.dump(summary, open(OUT / "fh_summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
