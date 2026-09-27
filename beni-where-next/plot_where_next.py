"""Figure: where to observe next (area of applicability), Beni."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection

HERE = Path(__file__).parent.parent / "beni-pipeline"  # derived per-cell results live there
FIG = Path(__file__).parent / "figure"
FIG.mkdir(exist_ok=True)
g = np.load(HERE / "results/g2s_cells.npz")
c = np.load(HERE / "results/cells.npz")
w = np.load(HERE / "results/where_next.npz")
s = json.load(open(HERE / "results/where_next.json"))
polys = [np.column_stack([lo, la]) for lo, la in zip(g["vlon"], g["vlat"])]

plt.rcParams.update({"font.size": 14, "font.family": "DejaVu Sans"})
fig, axes = plt.subplots(1, 2, figsize=(14, 6.6))
for ax, key, samp, lab in [(axes[0], "mammals", c["mammal_counts"], "mammal records"),
                           (axes[1], "dna_sequenced", g["seq_n"], "DNA-sequenced records")]:
    di, thr = w[f"di_{key}"], float(w[f"thr_{key}"])
    ok = np.isfinite(di)
    ax.add_collection(PolyCollection(polys, facecolor="#F1F3F5", edgecolor="#DDE1E5", linewidth=0.2))
    pc = PolyCollection([p for p, k in zip(polys, ok) if k], array=di[ok], cmap="magma_r",
                        clim=(0, np.nanpercentile(di, 99)), edgecolor="none")
    ax.add_collection(pc)
    fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.02, label="dissimilarity to sampled cells")
    out = ok & (di > thr)
    ax.add_collection(PolyCollection([p for p, k in zip(polys, out) if k], facecolor="none",
                                     edgecolor="#00B0AD", linewidth=2.2))
    sm = samp > 0
    cx = g["vlon"].mean(1); cy = g["vlat"].mean(1)
    ax.scatter(cx[sm], cy[sm], s=9, c="#004F8F", label=f"cells with {lab}")
    ax.set_xlim(-67.5, -64.5); ax.set_ylim(-15.5, -12.5); ax.set_aspect(1 / np.cos(np.radians(-14)))
    ax.set_title(f"{lab[0].upper() + lab[1:]}\n{s[key]['outside_aoa_pct']:.1f}% of cells outside the area of applicability",
                 fontsize=14)
    ax.legend(loc="lower right", fontsize=11, frameon=True)
fig.text(0.5, 0.04, "Teal outline: environments no sampled cell resembles — where the next observations teach a model most.",
         ha="center", fontsize=13, color="#004F8F", fontweight="bold")
fig.text(0.01, 0.005, "Predictors: BIOMASS forest height, ESA CCI Biomass, CHELSA bio1 & bio12 on HEALPix WGS84 (~12.7 km). "
         "Dissimilarity index after Meyer & Pebesma 2021 (simplified threshold, unweighted).", fontsize=10, color="#555")
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(FIG / "beni_where_next.png", dpi=110)
print("saved")
