"""Where to observe next (Beni): area of applicability of in-situ records in EO/climate space.

Dissimilarity index (DI) after Meyer & Pebesma 2021 (MEE, doi:10.1111/2041-210X.13650):
standardised predictors, DI = distance to the nearest sampled cell / mean distance between
sampled cells; threshold = 95th percentile of leave-one-out DI among sampled cells
(a simplification of their outlier-removed maximum). Unweighted predictors (no model).
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
d = np.load(HERE / "results/g2s_cells.npz")
c = np.load(HERE / "results/cells.npz")

X = np.column_stack([d["fh9"], c["agb_mean"], d["bio1"], d["bio12"]])
use = (d["frac9"] >= 0.8) & np.all(np.isfinite(X), axis=1)
Z = (X[use] - X[use].mean(0)) / X[use].std(0)


def aoa(sampled):
    T = Z[sampled]
    D_tt = np.sqrt(((T[:, None, :] - T[None, :, :]) ** 2).sum(-1))
    mean_d = D_tt[np.triu_indices(len(T), 1)].mean()
    np.fill_diagonal(D_tt, np.inf)
    thr = np.percentile(D_tt.min(1) / mean_d, 95)
    D = np.sqrt(((Z[:, None, :] - T[None, :, :]) ** 2).sum(-1)).min(1) / mean_d
    return D, thr


out = {"cells_considered": int(use.sum()), "predictors": ["BIOMASS forest height", "CCI AGB", "CHELSA bio1", "CHELSA bio12"]}
DI = {}
for name, v in [("all_taxa", c["counts"]), ("mammals", c["mammal_counts"]), ("dna_sequenced", d["seq_n"])]:
    sampled = v[use] > 0
    D, thr = aoa(sampled)
    DI[name] = D
    out[name] = {"sampled_cells": int(sampled.sum()), "threshold": round(float(thr), 3),
                 "outside_aoa_pct": round(100 * float((D > thr).mean()), 1)}
full = np.full(d["cells"].size, np.nan)
res = {}
for k, D in DI.items():
    a = full.copy(); a[use] = D; res[k] = a
np.savez(HERE / "results/where_next.npz", use=use, **{f"di_{k}": v for k, v in res.items()},
         **{f"thr_{k}": out[k]["threshold"] for k in DI})
json.dump(out, open(HERE / "results/where_next.json", "w"), indent=1)
print(json.dumps(out, indent=1))
